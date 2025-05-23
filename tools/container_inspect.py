from . import get_client

def get_container_inspect(container_name):
    client = get_client()
    container = client.containers.get(container_name)
    return container.attrs  # JSON do inspect
