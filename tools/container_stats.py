from . import get_client  # Importa do __init__.py

def get_container_stats(container_name):
    client = get_client()
    container = client.containers.get(container_name)
    return container.stats(stream=False)
