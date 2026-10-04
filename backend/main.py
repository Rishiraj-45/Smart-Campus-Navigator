from fastapi import FastAPI, HTTPException

from backend.database import SessionLocal
from backend.models import Location

from backend.navigation.campus import CAMPUS_GRAPH
from backend.navigation.pathfinder import dijkstra
from backend.navigation.locations import LOCATIONS
from backend.navigation.directions import generate_directions
from backend.navigation.route_utils import calculate_walking_time


app = FastAPI(
    title="Smart Campus Navigator",
    description="Indoor Navigation and Campus Assistance System",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Smart Campus Navigator API is running!"
    }


@app.get("/locations")
def get_locations():
    """Return all campus locations from the database."""

    db = SessionLocal()

    try:
        locations = db.query(Location).all()

        return {
            "count": len(locations),
            "locations": [
                {
                    "id": location.id,
                    "name": location.name,
                    "type": location.type,
                    "building": location.building,
                    "floor": location.floor,
                    "accessible": location.accessible
                }
                for location in locations
            ]
        }

    finally:
        db.close()

@app.get("/location/{location_name}")
def get_location(location_name: str):
    """Return details of a single campus location."""

    db = SessionLocal()

    try:
        location = db.query(Location).filter(
            Location.name == location_name
        ).first()

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{location_name}' not found."
            )

        return {
            "id": location.id,
            "name": location.name,
            "type": location.type,
            "building": location.building,
            "floor": location.floor,
            "accessible": location.accessible
        }

    finally:
        db.close()

@app.get("/navigation")
def navigate(
    start: str,
    destination: str,
    accessible: bool = False
):
    """Find the shortest route between two campus locations."""

    if start not in CAMPUS_GRAPH:
        raise HTTPException(
            status_code=404,
            detail=f"Starting location '{start}' not found."
        )

    if destination not in CAMPUS_GRAPH:
        raise HTTPException(
            status_code=404,
            detail=f"Destination '{destination}' not found."
        )

    path, distance = dijkstra(
        CAMPUS_GRAPH,
        start,
        destination,
        locations=LOCATIONS,
        accessible_only=accessible
    )

    if not path:
        raise HTTPException(
            status_code=404,
            detail="No route found between these locations."
        )

    walking_time = calculate_walking_time(distance)

    route_directions = generate_directions(path)

    return {
    "start": start,
    "destination": destination,
    "accessible_route": accessible,
    "route": path,
    "distance_meters": distance,
    "walking_time_minutes": walking_time,
    "directions": route_directions
}