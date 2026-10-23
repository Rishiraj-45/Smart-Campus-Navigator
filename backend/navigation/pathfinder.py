
import heapq
from math import inf


def dijkstra(
    graph,
    start,
    destination,
    locations=None,
    accessible_only=False,
    transitions=None,
):
    """
    Find the minimum-cost route using Dijkstra's algorithm.

    In accessible mode:
    - Locations marked accessible=False cannot be used.
    - Staircase locations cannot be used.
    - Stair transitions cannot be used.
    - Elevator transitions remain available.

    Vertical transition distances are not included in the
    returned distance unless represented by graph edge weights.
    """

    if start not in graph or destination not in graph:
        return [], inf

    locations = locations or {}
    transitions = transitions or {}

    def is_inaccessible(node):
        """Return True if a node cannot be used in accessible mode."""
        info = locations.get(node, {})
        location_type = str(info.get("type", "")).lower()

        return (
            info.get("accessible") is False
            or location_type in {"staircase", "stairs"}
        )

    if accessible_only:
        if is_inaccessible(start) or is_inaccessible(destination):
            return [], inf

    # Copy the graph so the original graph is not modified.
    adjacency = {
        node: list(neighbours)
        for node, neighbours in graph.items()
    }

    # Add explicitly configured floor transitions.
    for (source, target), metadata in transitions.items():
        if source not in adjacency or target not in adjacency:
            continue

        transition_type = str(
            metadata.get("type", "stairs")
        ).lower()

        if accessible_only and transition_type not in {
            "elevator",
            "lift",
        }:
            continue

        if accessible_only and (
            is_inaccessible(source) or is_inaccessible(target)
        ):
            continue

        adjacency[source].append((target, 0.0))

    best = {node: inf for node in adjacency}
    previous = {node: None for node in adjacency}

    best[start] = 0.0
    queue = [(0.0, start)]

    while queue:
        distance, current = heapq.heappop(queue)

        # Ignore outdated queue entries.
        if distance != best[current]:
            continue

        if current == destination:
            break

        for neighbour, edge_distance in adjacency[current]:
            if neighbour not in adjacency:
                continue

            if accessible_only and is_inaccessible(neighbour):
                continue

            new_distance = distance + float(edge_distance)

            if new_distance < best[neighbour]:
                best[neighbour] = new_distance
                previous[neighbour] = current
                heapq.heappush(
                    queue,
                    (new_distance, neighbour),
                )

    if best[destination] == inf:
        return [], inf

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, best[destination]


def count_floor_transitions(path, locations):
    """Count adjacent path locations on different floors."""

    return sum(
        1
        for source, target in zip(path, path[1:])
        if locations.get(source, {}).get("floor") is not None
        and locations.get(target, {}).get("floor") is not None
        and locations[source]["floor"] != locations[target]["floor"]
    )
