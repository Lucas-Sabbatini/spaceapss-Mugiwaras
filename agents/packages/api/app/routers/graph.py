"""Router para endpoints do Knowledge Graph."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from packages.api.app.services.graph_service import GraphService
from packages.api.app.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/graph", tags=["graph"])


class GraphStats(BaseModel):
    """Estatísticas detalhadas do grafo."""
    total_nodes: int
    total_edges: int
    node_types: dict[str, int]
    avg_degree: float
    max_degree: int
    min_degree: int
    most_connected_node: Optional[dict] = None
    top_connected_nodes: list[dict] = Field(default_factory=list, description="Top 10 nós mais conectados")
    degree_distribution: Optional[dict] = Field(None, description="Quartis da distribuição de graus (min, Q1, median, Q3, max)")
    density: float = Field(description="Densidade do grafo (0-1, onde 1 = totalmente conectado)")
    num_components: int = Field(description="Número de componentes conectados")
    largest_component_size: int = Field(description="Tamanho do maior componente conectado")
    avg_clustering: float = Field(description="Coeficiente médio de clustering")
    isolated_nodes: int = Field(description="Quantidade de nós isolados (grau = 0)")
    edge_types: dict[str, int] = Field(default_factory=dict, description="Contagem de arestas entre tipos de nós")


class VisNode(BaseModel):
    """Nó no formato vis.js."""
    id: str
    label: str
    group: str
    title: Optional[str] = None
    value: Optional[int] = None  # Tamanho do nó baseado em grau


class VisEdge(BaseModel):
    """Aresta no formato vis.js."""
    from_: str = Field(..., alias="from")
    to: str
    value: Optional[float] = None  # Peso da aresta
    title: Optional[str] = None

    class Config:
        populate_by_name = True


class GraphResponse(BaseModel):
    """Resposta do endpoint de grafo."""
    nodes: list[VisNode]
    edges: list[VisEdge]
    stats: GraphStats


@router.get("/stats", response_model=GraphStats)
async def get_graph_stats():
    """
    Retorna estatísticas do Knowledge Graph.
    
    Retorna contagens de nós por tipo, total de arestas, e métricas de conectividade.
    """
    try:
        service = GraphService()
        stats = service.get_stats()
        return stats
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Grafo não encontrado. Execute build_knowledge_graph.py primeiro."
        )
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do grafo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=GraphResponse)
async def get_graph(
    node_type: Optional[str] = Query(None, description="Filtrar por tipo de nó (author, institution, organism, mesh_term, journal)"),
    limit: Optional[int] = Query(None, description="Limitar número de nós retornados", ge=1, le=5000),
    experiment_id: Optional[str] = Query(None, description="Filtrar por experiment_id específico"),
    min_degree: Optional[int] = Query(None, description="Nós com grau mínimo (mínimo de conexões)", ge=1),
):
    """
    Retorna o Knowledge Graph no formato vis.js.
    
    ## Parâmetros de Filtro
    - **node_type**: Tipos válidos: `author`, `institution`, `organism`, `mesh_term`, `journal`
    - **limit**: Limita quantos nós retornar (útil para grafos grandes)
    - **experiment_id**: Retorna apenas nós relacionados a um experimento específico
    - **min_degree**: Retorna apenas nós altamente conectados
    
    ## Formato de Resposta
    Retorna dados compatíveis com vis.js Network:
    - `nodes`: Array de nós com id, label, group, etc.
    - `edges`: Array de arestas com from, to, value (peso)
    - `stats`: Estatísticas do grafo filtrado
    
    ## Exemplos
    - `/api/graph` - Grafo completo
    - `/api/graph?limit=500` - Primeiros 500 nós
    - `/api/graph?node_type=author` - Apenas autores
    - `/api/graph?experiment_id=PMC123456` - Nós do experimento específico
    - `/api/graph?min_degree=10` - Nós com pelo menos 10 conexões
    """
    try:
        service = GraphService()
        
        graph_data = service.get_graph_data(
            node_type=node_type,
            limit=limit,
            experiment_id=experiment_id,
            min_degree=min_degree
        )
        
        return graph_data
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Grafo não encontrado. Execute build_knowledge_graph.py primeiro."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao obter dados do grafo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node/{node_id}")
async def get_node_details(node_id: str):
    """
    Retorna detalhes de um nó específico.
    
    Inclui todos os atributos do nó e lista de vizinhos.
    """
    try:
        service = GraphService()
        node_data = service.get_node_details(node_id)
        
        if node_data is None:
            raise HTTPException(status_code=404, detail=f"Nó '{node_id}' não encontrado")
        
        return node_data
        
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Grafo não encontrado. Execute build_knowledge_graph.py primeiro."
        )
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do nó: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/neighbors/{node_id}")
async def get_node_neighbors(
    node_id: str,
    max_depth: int = Query(1, description="Profundidade da vizinhança (1 = vizinhos diretos)", ge=1, le=3)
):
    """
    Retorna subgrafo de vizinhos de um nó.
    
    Útil para explorar conexões locais sem carregar o grafo completo.
    
    - **max_depth=1**: Vizinhos diretos
    - **max_depth=2**: Vizinhos + vizinhos dos vizinhos
    - **max_depth=3**: Até 3 níveis de distância
    """
    try:
        service = GraphService()
        subgraph = service.get_neighbors_subgraph(node_id, max_depth)
        
        return subgraph
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Grafo não encontrado. Execute build_knowledge_graph.py primeiro."
        )
    except Exception as e:
        logger.error(f"Erro ao obter vizinhos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
