import docker

def get_client():
    return docker.from_env()

def get_container_stats(container_name):
    client = get_client()
    container = client.containers.get(container_name)
    return container.stats(stream=False)
