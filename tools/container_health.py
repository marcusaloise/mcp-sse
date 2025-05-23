from . import get_client

def get_container_health(container_name):
    client = get_client()
    container = client.containers.get(container_name)
    inspect = container.attrs
    # Health status pode não existir se não tiver HEALTHCHECK no Dockerfile
    health = inspect.get('State', {}).get('Health', {})
    return {
        "Status": health.get("Status", "none"),
        "Log": health.get("Log", [])
    }
