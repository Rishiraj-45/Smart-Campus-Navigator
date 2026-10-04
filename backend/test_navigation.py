from navigation.pathfinder import dijkstra
from navigation.campus import CAMPUS_GRAPH


start = "Main Gate"
destination = "CSE Lab"

path, distance = dijkstra(
    CAMPUS_GRAPH,
    start,
    destination
)

print("Starting location:", start)
print("Destination:", destination)
print()
print("Shortest route:")

for location in path:
    print(" →", location)

print()
print("Total distance:", distance, "meters")