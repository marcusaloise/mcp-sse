# Servidor MCP de Observabilidade Docker

Um servidor **Model Context Protocol (MCP)** que fornece ferramentas de observabilidade para containers Docker e métricas do sistema host, utilizando **FastMCP** e **Server-Sent Events (SSE)**.

## 📋 Visão Geral

Este projeto implementa um servidor MCP que permite monitorar e inspecionar:

- **Containers Docker**: Status, logs, estatísticas de uso, health checks e informações detalhadas
- **Métricas do Host**: CPU, memória, disco e load average via Node Exporter
- **Integração com IA**: Protocolo MCP permite que assistentes de IA acessem essas informações

## 🔧 Funcionalidades

### Ferramentas Docker
- `DockerPsFrom{CLIENT_NAME}` - Lista containers (rodando ou todos)
- `DockerStatsFrom{CLIENT_NAME}` - Estatísticas de uso de recursos
- `HealthcheckFrom{CLIENT_NAME}` - Status de health checks
- `DockerLogsFrom{CLIENT_NAME}` - Logs dos containers
- `DockerInspectFrom{CLIENT_NAME}` - Informações detalhadas do container

### Métricas do Sistema
- `HostMetricsFrom{CLIENT_NAME}` - Métricas completas do host:
  - **CPU**: Percentual de uso
  - **Memória**: Total, usado, disponível
  - **Disco**: Espaço total, livre, usado
  - **Load Average**: 1min, 5min, 15min

### Utilitários
- `GetClientNameFrom{CLIENT_NAME}` - Retorna o nome do cliente configurado

## 🏗️ Arquitetura

```
mcp_sse.py              # Servidor principal FastMCP
├── tools/              # Módulos de funcionalidades
│   ├── __init__.py     # Cliente Docker base
│   ├── container_stats.py
│   ├── container_health.py
│   ├── container_logs.py
│   ├── container_inspect.py
│   ├── list_containers.py
│   └── host_metrics.py # Cliente Node Exporter
├── docker-compose.n8n.yaml
├── Dockerfile
└── requirements.txt
```

## 🚀 Como Executar

### Opção 1: Docker Compose (Recomendado)

```bash
# Clone o repositório
git clone <seu-repositorio>
cd <diretorio-do-projeto>

# Execute com Docker Compose
docker-compose -f docker-compose.n8n.yaml up -d
```

Isso irá inicializar:
- **n8n** (automação) na porta 5678
- **Redis** para cache/sessões
- **Node Exporter** para métricas do sistema
- **MCP Server** conectado via SSE

### Opção 2: Execução Local

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
export MCP_CLIENT_NAME="Meu-Cliente"
export NODE_EXPORTER_URL="http://localhost:9100/metrics"

# Execute o servidor
python mcp_sse.py
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `MCP_CLIENT_NAME` | Nome do cliente (usado nos nomes das ferramentas) | `"Cliente Padrão"` |
| `NODE_EXPORTER_URL` | URL do Node Exporter para métricas | `"http://node_exporter:9100/metrics"` |

### Docker Compose

O arquivo `docker-compose.n8n.yaml` inclui:

- **N8N**: Plataforma de automação com autenticação básica
  - Usuário: `marcola`
  - Senha: `12345678987456321`
  - Porta: `5678`

- **Node Exporter**: Coletor de métricas do sistema
  - Acesso aos diretórios `/proc`, `/sys` e `/` do host

- **Redis**: Cache e armazenamento de sessões

## 🔌 Integrações

### Model Context Protocol (MCP)

O servidor implementa o protocolo MCP via SSE, permitindo que assistentes de IA:

1. **Descubram** automaticamente as ferramentas disponíveis
2. **Executem** comandos de observabilidade
3. **Recebam** dados estruturados em tempo real

### Node Exporter

Integração com Prometheus Node Exporter para coleta de métricas:

```python
from tools.host_metrics import NodeExporterClient

client = NodeExporterClient("http://node-exporter:9100/metrics")
metrics = client.get_all_metrics()
```

### Docker API

Acesso completo à API Docker via socket Unix:

```python
from tools import get_client

client = get_client()  # docker.from_env()
containers = client.containers.list()
```

## 📊 Exemplos de Uso

### Listando Containers

```python
# Via MCP tool
{
  "tool": "DockerPsFromMeu-Cliente",
  "arguments": {
    "all_containers": true
  }
}
```

### Obtendo Métricas do Host

```python
# Retorna algo como:
{
  "cpu": {"usage_percent": 23.45},
  "memory": {
    "total_bytes": 8589934592,
    "used_bytes": 4294967296,
    "used_percent": 50.0
  },
  "disk": {
    "total_bytes": 107374182400,
    "used_percent": 45.2
  },
  "load": {
    "load_1min": 1.2,
    "load_5min": 1.0,
    "load_15min": 0.8
  }
}
```

## 🔒 Segurança

- **Docker Socket**: Montado com acesso somente leitura quando possível
- **Autenticação N8N**: Configurada com usuário/senha básicos
- **Isolamento**: Containers executam em rede isolada
- **Logs**: Configurados com níveis apropriados

## 📝 Desenvolvimento

### Estrutura de Código

- **FastMCP**: Framework para servidores MCP simples
- **Pydantic**: Validação de dados de entrada
- **Docker SDK**: Integração com Docker API
- **Requests**: Cliente HTTP para Node Exporter

### Adicionando Novas Ferramentas

1. Crie um novo módulo em `tools/`
2. Implemente a função de negócio
3. Registre como `@mcp_server.tool()` em `mcp_sse.py`
4. Defina modelos Pydantic se necessário

### Exemplo:

```python
@mcp_server.tool(name=f"MinhaNovaFerramentaFrom{CLIENT_NAME}")
def minha_ferramenta(parametro: str):
    """Descrição da minha ferramenta"""
    return {"resultado": f"Processado: {parametro}"}
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique os logs: `docker-compose logs mcp_sse`
2. Teste a conectividade: `curl http://localhost:9100/metrics`
3. Valide o Docker socket: `docker ps`

---

**Desenvolvido com ❤️ para observabilidade inteligente via MCP**