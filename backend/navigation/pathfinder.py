
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
    Find the shortest route using known horizontal edge distances.

    In accessible mode:
    - Staircase nodes cannot be used.
    - Stair transitions cannot be used.
    - Elevator transitions remain available.

    Vertical transition distances are unknown and are not included
    in the returned distance.
    """

    if start not in graph or destination not in graph:
        return [], inf

    locations = locations or {}
    transitions = transitions or {}

    if accessible_only:
        # Do not route through staircase nodes in accessible mode.
        for node in (start, destination):
            if locations.get(node, {}).get("type") == "staircase":
                return [], inf

    adjacency = {
        node: list(neighbours)
        for node, neighbours in graph.items()
    }

    # Add explicitly configured floor transitions.
    for (source, target), metadata in transitions.items():
        if source not in adjacency or target not in adjacency:
            continue

        transition_type = metadata.get("type", "stairs")

        if accessible_only and transition_type != "elevator":
            continue

        if accessible_only and (
            locations.get(source, {}).get("type") == "staircase"
            or locations.get(target, {}).get("type") == "staircase"
        ):
            continue

        adjacency[source].append((target, 0.0))

    best = {node: inf for node in adjacency}
    previous = {node: None for node in adjacency}

    best[start] = 0.0
    queue = [(0.0, start)]

    while queue:
        distance, current = heapq.heappop(queue)

        if distance != best[current]:
            continue

        if current == destination:
            break

        for neighbour, edge_distance in adjacency[current]:
            if accessible_only and (
                locations.get(neighbour, {}).get("type") == "staircase"
            ):
                continue

            new_distance = distance + float(edge_distance)

            if new_distance < best[neighbour]:
                best[neighbour] = new_distance
                previous[neighbour] = current
                heapq.heappush(queue, (new_distance, neighbour))

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
