import heapq


def dijkstra(graph, start, destination, locations=None, accessible_only=False):
    """
    Find the shortest path between two locations
    using Dijkstra's algorithm.

    If accessible_only is True, locations marked as
    inaccessible will not be used.
    """

    distances = {
        location: float("inf")
        for location in graph
    }

    previous = {
        location: None
        for location in graph
    }

    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:

        current_distance, current_location = heapq.heappop(
            priority_queue
        )

        if current_distance > distances[current_location]:
            continue

        if current_location == destination:
            break

        for neighbour, distance in graph[current_location]:

            # Accessibility check
            if accessible_only and locations:

                neighbour_info = locations.get(neighbour, {})

                if not neighbour_info.get("accessible", True):
                    continue

            new_distance = current_distance + distance

            if new_distance < distances[neighbour]:

                distances[neighbour] = new_distance

                previous[neighbour] = current_location

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    # Reconstruct path
    path = []

    current = destination

    while current is not None:

        path.append(current)

        current = previous[current]

    path.reverse()

    # No route exists
    if not path or path[0] != start:
        return [], float("inf")

    return path, distances[destination]