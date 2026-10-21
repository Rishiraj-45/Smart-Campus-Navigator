
import pytest

from backend.navigation.campus import CAMPUS_GRAPH
from backend.navigation.campus_map_data import LOCATIONS
from backend.navigation.pathfinder import dijkstra
from backend.navigation.floor_transitions import get_floor_transitions
from backend.navigation.directions import generate_directions


TRANSITIONS = get_floor_transitions()


def test_same_location_returns_zero_distance():
    """A route from a location to itself should have zero distance."""
    location = next(iter(CAMPUS_GRAPH))

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        location,
        location,
        locations=LOCATIONS,
        transitions=TRANSITIONS,
    )

    assert path == [location]
    assert distance == 0


def test_connected_ground_floor_route():
    """A known direct connection should be routable."""
    start = "MAIN HALL / ATRIUM"
    destination = "Placement Cell G28"

    assert start in CAMPUS_GRAPH
    assert destination in CAMPUS_GRAPH

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        start,
        destination,
        locations=LOCATIONS,
        transitions=TRANSITIONS,
    )

    assert path
    assert path[0] == start
    assert path[-1] == destination
    assert distance >= 0


def test_floor_transitions_are_bidirectional():
    """Each configured floor transition should exist in both directions."""
    for (source, target), metadata in TRANSITIONS.items():
        reverse = TRANSITIONS.get((target, source))

        assert reverse is not None
        assert reverse["type"] == metadata["type"]


def test_accessible_mode_excludes_stair_transitions():
    """Accessible mode should not use configured stairs for floor changes."""
    for (source, target), metadata in TRANSITIONS.items():
        if metadata.get("type") != "stairs":
            continue

        path, _ = dijkstra(
            CAMPUS_GRAPH,
            source,
            target,
            locations=LOCATIONS,
            accessible_only=True,
            transitions=TRANSITIONS,
        )

        # A direct stair transition must not be added in accessible mode.
        # Another all-horizontal route may still exist.
        if path:
            assert not any(
                TRANSITIONS.get((a, b), {}).get("type") == "stairs"
                for a, b in zip(path, path[1:])
            )


def test_directions_include_start_and_arrival():
    """Directions should identify the start and destination."""
    start = "MAIN HALL / ATRIUM"
    destination = "Placement Cell G28"

    path, _ = dijkstra(
        CAMPUS_GRAPH,
        start,
        destination,
        locations=LOCATIONS,
        transitions=TRANSITIONS,
    )

    directions = generate_directions(
        path,
        locations=LOCATIONS,
        transitions=TRANSITIONS,
    )

    assert directions
    assert directions[0].startswith("Start at")
    assert any("You have arrived at" in line for line in directions)


def test_unknown_location_returns_no_route():
    """Unknown nodes should return an empty path."""
    path, distance = dijkstra(
        CAMPUS_GRAPH,
        "LOCATION_THAT_DOES_NOT_EXIST",
        "ANOTHER_UNKNOWN_LOCATION",
        locations=LOCATIONS,
        transitions=TRANSITIONS,
    )

    assert path == []
    assert distance == float("inf")


def test_transition_nodes_exist_in_graph():
    """All configured transitions must reference real graph nodes."""
    for source, target in TRANSITIONS:
        assert source in CAMPUS_GRAPH, f"Missing graph node: {source}"
        assert target in CAMPUS_GRAPH, f"Missing graph node: {target}"


def test_transition_endpoints_are_on_different_floors():
    """Configured floor transitions should connect different floors."""
    for (source, target), _metadata in TRANSITIONS.items():
        source_floor = LOCATIONS[source]["floor"]
        target_floor = LOCATIONS[target]["floor"]

        assert source_floor != target_floor, (
            f"{source} and {target} are on the same floor"
        )

def test_accessible_route_distance_matches_graph_edges():
    from backend.navigation.campus import CAMPUS_GRAPH
    from backend.navigation.campus_map_data import LOCATIONS
    from backend.navigation.pathfinder import dijkstra
    from backend.navigation.floor_transitions import get_floor_transitions

    start = "MAIN HALL / ATRIUM"
    destination = "LAB 119"
    transitions = get_floor_transitions()

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        start,
        destination,
        locations=LOCATIONS,
        accessible_only=True,
        transitions=transitions,
    )

    assert path, "An accessible route should be found."
    assert path[0] == start
    assert path[-1] == destination

    # Verify each route step has a corresponding graph edge
    # or a configured floor transition.
    total_horizontal_distance = 0.0

    for source, target in zip(path, path[1:]):
        if (source, target) in transitions:
            continue

        neighbours = dict(CAMPUS_GRAPH[source])
        assert target in neighbours, (
            f"Missing graph edge: {source} -> {target}"
        )
        total_horizontal_distance += float(neighbours[target])

    assert distance == total_horizontal_distance

def test_accessible_route_never_uses_staircase_nodes():
    from backend.navigation.campus import CAMPUS_GRAPH
    from backend.navigation.campus_map_data import LOCATIONS
    from backend.navigation.pathfinder import dijkstra
    from backend.navigation.floor_transitions import get_floor_transitions

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        "MAIN HALL / ATRIUM",
        "LAB 119",
        locations=LOCATIONS,
        accessible_only=True,
        transitions=get_floor_transitions(),
    )

    assert path, "An accessible route should be found."

    staircase_nodes = [
        node
        for node in path
        if LOCATIONS.get(node, {}).get("type") == "staircase"
    ]

    assert not staircase_nodes, (
        f"Accessible route contains staircase nodes: {staircase_nodes}"
    )


def test_accessible_route_cannot_start_at_staircase():
    from backend.navigation.campus import CAMPUS_GRAPH
    from backend.navigation.campus_map_data import LOCATIONS
    from backend.navigation.pathfinder import dijkstra
    from backend.navigation.floor_transitions import get_floor_transitions

    staircase_nodes = [
        node
        for node, info in LOCATIONS.items()
        if info.get("type") == "staircase" and node in CAMPUS_GRAPH
    ]

    assert staircase_nodes, (
        "Test setup error: no staircase nodes were found in the campus data."
    )

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        staircase_nodes[0],
        "LAB 119",
        locations=LOCATIONS,
        accessible_only=True,
        transitions=get_floor_transitions(),
    )

    assert path == [], (
        f"Accessible routing should not start at staircase "
        f"{staircase_nodes[0]!r}."
    )

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_rejects_unknown_start_location():
    response = client.get(
        "/navigation",
        params={
            "start": "UNKNOWN LOCATION",
            "destination": "LAB 119",
        },
    )

    assert response.status_code == 404


def test_api_rejects_unknown_destination():
    response = client.get(
        "/navigation",
        params={
            "start": "MAIN HALL / ATRIUM",
            "destination": "UNKNOWN LOCATION",
        },
    )

    assert response.status_code == 404


def test_api_rejects_same_start_and_destination():
    response = client.get(
        "/navigation",
        params={
            "start": "LAB 119",
            "destination": "LAB 119",
        },
    )

    assert response.status_code == 400


def test_api_returns_valid_accessible_route():
    response = client.get(
        "/navigation",
        params={
            "start": "MAIN HALL / ATRIUM",
            "destination": "LAB 119",
            "accessible": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["start"] == "MAIN HALL / ATRIUM"
    assert data["destination"] == "LAB 119"
    assert data["accessible_route"] is True
    assert data["route"][0] == "MAIN HALL / ATRIUM"
    assert data["route"][-1] == "LAB 119"
    assert data["distance_meters"] >= 0
    assert isinstance(data["directions"], list)

def test_multiple_routes_have_valid_graph_connections():
    from backend.navigation.campus import CAMPUS_GRAPH
    from backend.navigation.campus_map_data import LOCATIONS
    from backend.navigation.pathfinder import dijkstra
    from backend.navigation.floor_transitions import get_floor_transitions

    transitions = get_floor_transitions()

    test_routes = [
        ("MAIN HALL / ATRIUM", "LAB 119", False),
        ("MAIN HALL / ATRIUM", "LAB 119", True),
        ("117", "LAB 119", False),
        ("LAB 119", "MAIN HALL / ATRIUM", True),
    ]

    for start, destination, accessible in test_routes:
        path, distance = dijkstra(
            CAMPUS_GRAPH,
            start,
            destination,
            locations=LOCATIONS,
            accessible_only=accessible,
            transitions=transitions,
        )

        assert path, (
            f"No route found: {start} -> {destination}, "
            f"accessible={accessible}"
        )

        assert path[0] == start
        assert path[-1] == destination

        horizontal_distance = 0.0

        for source, target in zip(path, path[1:]):
            if accessible:
                assert LOCATIONS.get(target, {}).get("type") != "staircase", (
                    f"Accessible route uses staircase node {target!r}: "
                    f"{start} -> {destination}"
                )

            if (source, target) in transitions:
                continue

            neighbours = dict(CAMPUS_GRAPH[source])

            assert target in neighbours, (
                f"Invalid connection {source!r} -> {target!r} "
                f"for route {start!r} -> {destination!r}"
            )

            horizontal_distance += float(neighbours[target])

        assert abs(distance - horizontal_distance) < 1e-9, (
            f"Distance mismatch for {start!r} -> {destination!r}: "
            f"reported {distance}, calculated {horizontal_distance}"
        )
