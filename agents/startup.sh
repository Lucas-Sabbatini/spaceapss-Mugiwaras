#!/bin/bash
set -e

python build_knowledge_graph.py

if [ $? -eq 0 ]; then
    echo "Knowledge graph construído com sucesso!"
else
    echo "Erro ao construir knowledge graph"
    exit 1
fi

exec uvicorn packages.api.app.main:app --host 0.0.0.0 --port 8080
