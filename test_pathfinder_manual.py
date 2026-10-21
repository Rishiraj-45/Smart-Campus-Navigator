
from backend.navigation.pathfinder import dijkstra

graph = {
    "Entrance": [("Corridor", 5), ("Stairs", 2)],
    "Corridor": [("Entrance", 5), ("Lift", 4)],
    "Stairs": [("Entrance", 2), ("Room", 3)],
    "Lift": [("Corridor", 4), ("Room", 6)],
    "Room": [("Stairs", 3), ("Lift", 6)],
}

locations = {
    "Entrance": {"accessible": True},
    "Corridor": {"accessible": True},
    "Stairs": {"accessible": False},
    "Lift": {"accessible": True},
    "Room": {"accessible": True},
}

# Normal route should choose the shortest route via stairs.
path, distance = dijkstra(
    graph, "Entrance", "Room", locations
)
assert path == ["Entrance", "Stairs", "Room"]
assert distance == 5

# Accessible route should avoid stairs and use the lift.
path, distance = dijkstra(
    graph, "Entrance", "Room", locations,
    accessible_only=True
)
assert path == ["Entrance", "Corridor", "Lift", "Room"]
assert distance == 15
assert "Stairs" not in path

# Unknown locations should return no route.
path, distance = dijkstra(
    graph, "Entrance", "Unknown", locations
)
assert path == []
assert distance == float("inf")

print("All pathfinder tests passed!")
