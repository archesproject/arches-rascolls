from functools import lru_cache

from arches.app.models.models import Node


@lru_cache(maxsize=None)
def get_node_id(graph_slug, node_alias):
    """Resolve a node UUID from its graph slug and node alias.

    Cached for the process lifetime: node ids only change when a model is
    re-imported, which requires a restart anyway.
    """
    return str(
        Node.objects.only("nodeid")
        .get(graph__slug=graph_slug, alias=node_alias, source_identifier=None)
        .nodeid
    )


@lru_cache(maxsize=None)
def get_nodegroup_id(graph_slug, node_alias):
    """Resolve the nodegroup UUID containing the node with the given alias."""
    return str(
        Node.objects.only("nodegroup_id")
        .get(graph__slug=graph_slug, alias=node_alias, source_identifier=None)
        .nodegroup_id
    )
