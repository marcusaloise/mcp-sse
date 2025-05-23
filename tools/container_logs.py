from . import get_client

def get_container_logs(container_name, tail=100):
    client = get_client()
    container = client.containers.get(container_name)
    logs = container.logs(tail=tail)
    return logs.decode()
