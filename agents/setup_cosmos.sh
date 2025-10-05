#!/usr/bin/env bash
set -euo pipefail

SUBSCRIPTION_ID="65ed8716-13ad-4a97-b504-b61fd6be7e29"
echo "=========================================================="
echo "🚀 Cosmos DB via CLI (alinhado com Azure Policy de regiões)"
echo "=========================================================="

# 1) Seleciona assinatura
echo "🧭 Selecionando assinatura..."
az account set --subscription "$SUBSCRIPTION_ID"
echo "✅ Assinatura definida."

# 2) Descobre regiões permitidas pela policy
echo "🔎 Buscando regiões permitidas pela policy..."
mapfile -t ALLOWED < <(az policy assignment list --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --query "[?parameters.listOfAllowedLocations].parameters.listOfAllowedLocations.value[]" -o tsv)

if [ ${#ALLOWED[@]} -eq 0 ]; then
  echo "❌ Não há lista de regiões permitidas detectada. Verifique suas policies."
  exit 1
fi

# Ordena priorizando eastus2 se existir
PREF_ORDER=("eastus2")
ORDERED=()

# Add preferidas primeiro
for p in "${PREF_ORDER[@]}"; do
  for r in "${ALLOWED[@]}"; do
    if [ "$r" = "$p" ]; then ORDERED+=("$r"); fi
  done
done
# Adiciona o resto mantendo ordem original
for r in "${ALLOWED[@]}"; do
  skip=0
  for o in "${ORDERED[@]}"; do [ "$o" = "$r" ] && { skip=1; break; }; done
  [ $skip -eq 0 ] && ORDERED+=("$r")
done

echo "✅ Regiões permitidas: ${ALLOWED[*]}"
echo "✅ Ordem de tentativa: ${ORDERED[*]}"
echo "=========================================================="

# 3) Providers
echo "🔌 Registrando providers (idempotente)..."
for p in Microsoft.DocumentDB Microsoft.Network Microsoft.KeyVault Microsoft.Resources; do
  az provider register --namespace $p --wait >/dev/null
done
echo "✅ Providers ok."
echo "=========================================================="

# 4) Variáveis
RAND=$RANDOM
PREFIX="cosmos${RAND}"
ACCOUNT="${PREFIX}-acct"
DB="${PREFIX}-db"
CONTAINER="${PREFIX}-container"
PARTITION_KEY="/pk"
THROUGHPUT=400
OWNER=$(az account show --query user.name -o tsv)
TAGS="env=dev project=spaceapps owner=${OWNER}"

echo "📦 Config:"
echo "  Account:   $ACCOUNT"
echo "  DB:        $DB"
echo "  Container: $CONTAINER"
echo "  Tags:      $TAGS"
echo "=========================================================="

# 5) Cria RG NA MESMA REGIÃO PERMITIDA (primeira da lista ordenada)
RG_LOCATION="${ORDERED[0]}"
RG="${PREFIX}-rg"
echo "🏗️ Criando Resource Group '$RG' em '$RG_LOCATION'..."
az group create -n "$RG" -l "$RG_LOCATION" --tags $TAGS >/dev/null
echo "✅ RG criado."
echo "=========================================================="

# 6) Função que tenta criar a conta Cosmos em uma região permitida
try_create_cosmos () {
  local region="$1"
  echo "🌌 Tentando Cosmos em '$region' (Free Tier primeiro)..."
  set +e
  az cosmosdb create \
    -g "$RG" -n "$ACCOUNT" \
    --locations regionName="$region" \
    --default-consistency-level Session \
    --enable-free-tier true \
    --public-network-access Enabled \
    --ip-range-filter "" \
    --minimal-tls-version Tls12 \
    --assign-identity \
    --tags $TAGS >/dev/null 2>create_err.log
  local ret=$?
  set -e

  if [ $ret -ne 0 ]; then
    echo "⚠️ Falhou com Free Tier em $region. Tentando SEM Free Tier..."
    set +e
    az cosmosdb create \
      -g "$RG" -n "$ACCOUNT" \
      --locations regionName="$region" \
      --default-consistency-level Session \
      --public-network-access Enabled \
      --ip-range-filter "" \
      --minimal-tls-version Tls12 \
      --assign-identity \
      --tags $TAGS >/dev/null 2>>create_err.log
    ret=$?
    set -e
    if [ $ret -ne 0 ]; then
      echo "❌ Falhou em $region. Últimas linhas do erro:"
      tail -n 12 create_err.log || true
      return 1
    fi
  fi

  echo "✅ Cosmos criado em '$region'."
  echo "$region" > .cosmos_region.ok
  return 0
}

# 7) Itera pelas regiões permitidas
CHOSEN=""
for region in "${ORDERED[@]}"; do
  if try_create_cosmos "$region"; then
    CHOSEN="$region"
    break
  fi
done

if [ -z "$CHOSEN" ]; then
  echo "=========================================================="
  echo "❌ Nenhuma região permitida aceitou a criação do Cosmos."
  echo "   • Verifique se a policy permite CosmosDB (não só a região)."
  echo "   • Veja logs em: create_err.log"
  echo "=========================================================="
  exit 2
fi

# 8) Database e container
echo "🗃️ Criando DB '$DB'..."
az cosmosdb sql database create -g "$RG" -a "$ACCOUNT" -n "$DB" --throughput $THROUGHPUT >/dev/null
echo "✅ DB ok."

echo "📂 Criando container '$CONTAINER'..."
az cosmosdb sql container create \
  -g "$RG" -a "$ACCOUNT" -d "$DB" -n "$CONTAINER" \
  --partition-key-path "$PARTITION_KEY" \
  --idx @- >/dev/null <<'JSON'
{
  "indexingPolicy": {
    "indexingMode": "consistent",
    "automatic": true,
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": "/\"_etag\"/?"}]
  }
}
JSON
echo "✅ Container ok."
echo "=========================================================="

# 9) Keys / connection string (pode ser bloqueado pela policy)
echo "🔑 Buscando keys/connection string (se permitido pela policy)..."
set +e
PRIMARY_KEY=$(az cosmosdb keys list -g "$RG" -n "$ACCOUNT" --type keys --query primaryMasterKey -o tsv 2>/dev/null)
CONN=$(az cosmosdb keys list -g "$RG" -n "$ACCOUNT" --type connection-strings --query "connectionStrings[0].connectionString" -o tsv 2>/dev/null)
set -e

echo "=========================================================="
echo "✅ Cosmos DB PRONTO!"
echo "RG:            $RG  (região do RG: $RG_LOCATION)"
echo "Cosmos:        $ACCOUNT (região: $CHOSEN)"
echo "DB/Container:  $DB / $CONTAINER"
echo "PartitionKey:  $PARTITION_KEY"
echo "Throughput:    $THROUGHPUT RU/s"
echo "Primary Key:   ${PRIMARY_KEY:-<bloqueada por policy>}"
echo "Conn String:   ${CONN:-<bloqueada por policy>}"
echo "=========================================================="
