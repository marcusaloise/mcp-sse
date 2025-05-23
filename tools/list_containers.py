from . import get_client

def list_containers(all_containers=False):
    """
    Lista containers disponíveis.
    :param all_containers: Se True, mostra todos (inclusive parados). Se False, só os rodando.
    :return: Lista de dicts com info resumida dos containers.
    """
    client = get_client()
    containers = client.containers.list(all=all_containers)
    result = []
    for c in containers:
        result.append({
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "image": c.image.tags,
            "short_id": c.short_id
        })
    return result
