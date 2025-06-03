from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional
import os

from tools.container_stats import get_container_stats
from tools.container_health import get_container_health
from tools.container_logs import get_container_logs
from tools.container_inspect import get_container_inspect
from tools.list_containers import list_containers
from tools.host_metrics import NodeExporterClient


NODE_EXPORTER_URL = os.environ.get("NODE_EXPORTER_URL", "http://node_exporter:9100/metrics")
node_exporter_client = NodeExporterClient(NODE_EXPORTER_URL)

CLIENT_NAME = os.environ.get("MCP_CLIENT_NAME", "Cliente Padrão")
mcp_server = FastMCP(name=f"Observabilidade - {CLIENT_NAME}")

# MODELS DE ENTRADA
class ContainerName(BaseModel):
    container_name: str

class ContainerLogsRequest(BaseModel):
    container_name: str
    tail: Optional[int] = 100


# TOOLS

@mcp_server.tool(name=f"Captura_as_Informacoes_do_host_do_{CLIENT_NAME}")
def get_host_metrics():
    """
    Retorna métricas do host coletadas via Node Exporter.
    Retorna um dicionário como:
    {
      "cpu": {"usage_percent": 17.3},
      "memory": {...},
      "disk": {...},
      "load": {...}
    }
    """
    return node_exporter_client.get_all_metrics()


@mcp_server.tool(name=f"Captura_o_nome_do_cliente_{CLIENT_NAME}")
def get_client_name():
    """
    Retorna o nome do cliente.
    """
    return {"client_name": CLIENT_NAME}


@mcp_server.tool(name=f"Captura_a_lista_de_Docker_do_{CLIENT_NAME}")
def api_list_containers(all_containers: bool):
    """
    Lista containers Docker disponíveis.

    Exemplo de entrada:
    {
      "all_containers": true
    }
    """
    return list_containers(all_containers)

@mcp_server.tool(name=f"Captura_Docker_Stats_do_{CLIENT_NAME}")
def api_get_stats(req: ContainerName):
    """
    Obtém stats de uso do container.

    Exemplo de entrada:
    {
      "container_name": "Nome completo do container"
    }
    """
    return get_container_stats(req.container_name)

@mcp_server.tool(name=f"Realiza_Docker_healthcheck_do_{CLIENT_NAME}")
def api_get_health(req: ContainerName):
    """
    Obtém informações de healthcheck do container.

    Exemplo de entrada:
    {
      "container_name": "Nome completo do container"
    }
    """
    return get_container_health(req.container_name)

@mcp_server.tool(name=f"Captura_logs_do_Docker_do_{CLIENT_NAME}")
def api_get_logs(req: ContainerLogsRequest):
    """
    Obtém os últimos logs do container.

    Exemplo de entrada:
    {
      "container_name": "Nome completo do container",
      "tail": 100
    }
    """
    return get_container_logs(req.container_name, req.tail)

@mcp_server.tool(name=f"Realiza_o_inspect_do_Docker_do_{CLIENT_NAME}")
def api_get_inspect(req: ContainerName):
    """
    Retorna o inspect completo do container.

    Exemplo de entrada:
    {
      "container_name": "Nome completo do container"
    }
    """
    return get_container_inspect(req.container_name)

if __name__ == "__main__":
    mcp_server.run(transport="sse")

