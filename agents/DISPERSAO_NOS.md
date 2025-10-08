# 📏 Como Deixar os Nós do Grafo Mais Dispersos

## 🎯 Mudanças Implementadas

Para deixar os nós mais distantes uns dos outros, foram ajustados os **parâmetros padrão** da função `generate_graph_image()`:

### Antes vs Depois

| Parâmetro | Antes | Depois | Efeito |
|-----------|-------|--------|--------|
| `k` | 0.5 | **1.5** | 🔵 Distância entre nós **3x maior** |
| `iterations` | 100 | **150** | 🔵 Melhor convergência do layout |
| `scale` | N/A | **2.0** | 🔵 Canvas 2x maior (spring/kamada_kawai) |

## 🔧 Como Controlar a Dispersão

### 1. Parâmetro `k` (Mais Importante) 🌟

O parâmetro `k` define a **distância ótima** entre nós no algoritmo spring layout.

```python
# Muito compacto (nós próximos)
k=0.3

# Padrão antigo
k=0.5

# Novo padrão (mais espaçado)
k=1.5

# Bem disperso
k=2.0

# Muito disperso
k=3.0

# Extremamente disperso
k=5.0
```

**Exemplo:**
```python
kg.generate_graph_image(
    output_path="dispersed.png",
    k=3.0  # Nós bem separados
)
```

### 2. Parâmetro `scale` (Automático)

Agora os layouts `spring` e `kamada_kawai` usam automaticamente `scale=2.0`, que **dobra o tamanho** do canvas:

```python
# Spring layout - agora com scale=2.0
pos = nx.spring_layout(graph, k=1.5, iterations=150, scale=2.0)

# Kamada-Kawai layout - agora com scale=2.0
pos = nx.kamada_kawai_layout(graph, scale=2.0)

# Circular layout - agora com scale=2.0
pos = nx.circular_layout(graph, scale=2.0)
```

### 3. Parâmetro `iterations`

Mais iterações = layout mais estável e bem organizado.

```python
# Rápido mas pode não convergir bem
iterations=50

# Padrão antigo
iterations=100

# Novo padrão (melhor qualidade)
iterations=150

# Alta qualidade
iterations=200

# Máxima qualidade (mais lento)
iterations=300
```

### 4. Parâmetro `figsize`

Canvas maior = mais espaço para os nós.

```python
# Pequeno
figsize=(16, 12)

# Padrão
figsize=(24, 18)

# Grande
figsize=(30, 24)

# Muito grande
figsize=(40, 30)

# Enorme (para impressão)
figsize=(60, 45)
```

## 📊 Exemplos Práticos

### Exemplo 1: Dispersão Moderada (Padrão Novo)
```python
kg.generate_graph_image(
    output_path="moderate.png",
    k=1.5,           # Distância moderada
    iterations=150,  # Boa convergência
    figsize=(24, 18) # Tamanho padrão
)
# Os layouts spring/kamada_kawai usam scale=2.0 automaticamente
```

### Exemplo 2: Alta Dispersão
```python
kg.generate_graph_image(
    output_path="high_dispersion.png",
    k=2.5,           # Grande distância
    iterations=200,  # Muitas iterações
    figsize=(30, 24) # Canvas maior
)
```

### Exemplo 3: Máxima Dispersão
```python
kg.generate_graph_image(
    output_path="max_dispersion.png",
    k=4.0,           # Distância máxima
    iterations=250,  # Convergência total
    figsize=(40, 30) # Canvas muito grande
)
```

### Exemplo 4: Comparação Lado a Lado

```python
# Compacto
kg.generate_graph_image(
    output_path="compact.png",
    k=0.5,
    iterations=100,
    title="Compact Layout (k=0.5)"
)

# Disperso
kg.generate_graph_image(
    output_path="dispersed.png",
    k=3.0,
    iterations=200,
    title="Dispersed Layout (k=3.0)"
)
```

## 🎨 Demonstração Visual

Execute o script de teste atualizado para ver 8 exemplos diferentes:

```bash
cd agents
python test_graph_visualization.py
```

Exemplos gerados:
- `example_01_default.png` - Configuração padrão (k=1.5)
- `example_02_kamada_kawai.png` - Layout alternativo
- `example_03_no_labels.png` - Sem labels
- `example_04_high_res.png` - Alta resolução
- `example_05_circular.png` - Layout circular
- `example_06_custom_bg.png` - Fundo customizado
- `example_07_dispersed.png` - **Máxima dispersão (k=3.0)** ⭐
- `example_08_comparison_compact.png` - Comparação compacta (k=0.5)
- `example_08_comparison_dispersed.png` - Comparação dispersa (k=2.0)

## 🔍 Quando Usar Cada Configuração

### Grafos Pequenos (<50 nós)
```python
k=1.0, iterations=150, figsize=(20, 15)
```
Nós ficam organizados sem muito espaço vazio.

### Grafos Médios (50-200 nós)
```python
k=1.5, iterations=150, figsize=(24, 18)  # Padrão
```
Boa dispersão sem exagero.

### Grafos Grandes (200-500 nós)
```python
k=2.0, iterations=200, figsize=(30, 24)
```
Nós bem separados para evitar sobreposição.

### Grafos Muito Grandes (>500 nós)
```python
k=2.5, iterations=200, figsize=(40, 30), show_labels=False
```
Máxima dispersão, sem labels para não poluir.

### Para Apresentações
```python
k=2.0, iterations=200, figsize=(30, 24), layout="kamada_kawai"
```
Layout bonito e organizado.

### Para Análise Detalhada
```python
k=3.0, iterations=250, figsize=(50, 40), dpi=600
```
Máxima separação e alta resolução.

## ⚙️ Parâmetros Completos

```python
kg.generate_graph_image(
    output_path="graph.png",
    
    # Dispersão principal
    k=1.5,              # ⭐ Distância entre nós (0.3 a 5.0)
    iterations=150,     # ⭐ Qualidade do layout (50 a 300)
    figsize=(24, 18),   # ⭐ Tamanho do canvas
    
    # Layout (scale=2.0 é automático para spring/kamada_kawai)
    layout="spring",    # spring, kamada_kawai, circular, random
    
    # Outros parâmetros
    dpi=300,
    node_base_size=300,
    node_size_scale=100,
    edge_width=0.3,
    edge_alpha=0.4,
    font_size=8,
    show_labels=True,
    show_legend=True,
    title="Knowledge Graph",
    background_color="#FFFFFF"
)
```

## 💡 Dicas Finais

1. **Para começar:** Use os valores padrão (k=1.5, iterations=150)
2. **Se nós estão sobrepostos:** Aumente `k` para 2.0, 2.5 ou 3.0
3. **Se ficou muito vazio:** Diminua `k` para 1.0 ou 0.8
4. **Para melhor qualidade:** Aumente `iterations` para 200+
5. **Para grafos grandes:** Combine k alto + figsize grande + show_labels=False
6. **Para comparar:** Gere várias versões com k diferentes

## 🚀 Resultado

Com as mudanças implementadas:

✅ **Padrão agora é k=1.5** (antes era 0.5) - **3x mais disperso**  
✅ **Scale=2.0 automático** nos layouts - **canvas 2x maior**  
✅ **Iterations=150** (antes 100) - **melhor convergência**  
✅ **Facilmente customizável** via parâmetros

Os grafos agora ficam **muito mais legíveis** com nós bem separados! 🎉

---

**Atualizado:** Outubro 2025  
**Projeto:** SpaceAPSS - Mugiwaras
