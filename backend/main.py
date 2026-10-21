
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine, SessionLocal
from backend.models import Location

from backend.navigation.campus import CAMPUS_GRAPH
from backend.navigation.campus_map_data import LOCATIONS as MAP_LOCATIONS
from backend.navigation.pathfinder import dijkstra
from backend.navigation.directions import generate_directions
from backend.navigation.route_utils import calculate_walking_time
from backend.navigation.floor_transitions import get_floor_transitions


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Smart Campus Navigator",
    description="Indoor Navigation and Campus Assistance System",
    version="1.1.0",
)


# --------------------------------------------------
# Database Initialization
# --------------------------------------------------


Base.metadata.create_all(bind=engine)

# Populate the database with campus locations from the map.
db = SessionLocal()

try:
    existing_names = {
        name for (name,) in db.query(Location.name).all()
    }

    for node_name, info in MAP_LOCATIONS.items():
        if node_name in existing_names:
            continue

        db.add(
            Location(
                name=node_name,
                type=info.get("type", "location"),
                building=info.get("building", "Academic Block"),
                floor=info.get("floor") or 0,
                accessible=info.get("accessible", False),
            )
        )

    db.commit()

finally:
    db.close()


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Home / Health Check
# --------------------------------------------------

@app.get("/")
def home():
    """Check whether the API is running."""
    return {
        "message": "Smart Campus Navigator API is running!"
    }


# --------------------------------------------------
# Get All Campus Locations
# --------------------------------------------------

@app.get("/locations")
def get_locations():
    """Return all locations from the generated campus map."""

    locations = []

    for node_name, info in MAP_LOCATIONS.items():
        locations.append({
            "id": node_name,
            "name": node_name,
            "type": info.get("type", "location"),
            "building": info.get("building", "Academic Block"),
            "floor": info.get("floor"),
            "accessible": info.get("accessible", False),
        })

    # Ground Floor first, then First Floor.
    locations.sort(
        key=lambda location: (
            location["floor"]
            if location["floor"] is not None
            else 99,
            location["name"].casefold(),
        )
    )

    return {
        "count": len(locations),
        "locations": locations,
    }


# --------------------------------------------------
# Get Details of a Single Location
# --------------------------------------------------

@app.get("/location/{location_name}")
def get_location(location_name: str):
    """Return details of a location stored in the database."""

    db = SessionLocal()

    try:
        location = (
            db.query(Location)
            .filter(Location.name == location_name)
            .first()
        )

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{location_name}' not found in database.",
            )

        return {
            "id": location.id,
            "name": location.name,
            "type": location.type,
            "building": location.building,
            "floor": location.floor,
            "accessible": location.accessible,
        }

    finally:
        db.close()


# --------------------------------------------------
# Campus Navigation
# --------------------------------------------------

@app.get("/navigation")
def navigate(
    start: str,
    destination: str,
    accessible: bool = False,
):
    """Find a route between two campus locations."""

    # Validate starting location.
    if start not in CAMPUS_GRAPH:
        raise HTTPException(
            status_code=404,
            detail=f"Starting location '{start}' not found.",
        )

    # Validate destination.
    if destination not in CAMPUS_GRAPH:
        raise HTTPException(
            status_code=404,
            detail=f"Destination '{destination}' not found.",
        )

    # Start and destination must be different.
    if start == destination:
        raise HTTPException(
            status_code=400,
            detail="Starting location and destination cannot be the same.",
        )

    # Get configured floor transitions.
    transitions = get_floor_transitions()

    # Calculate the shortest route.
    path, horizontal_distance = dijkstra(
        CAMPUS_GRAPH,
        start,
        destination,
        locations=MAP_LOCATIONS,
        accessible_only=accessible,
        transitions=transitions,
    )

    if not path:
        raise HTTPException(
            status_code=404,
            detail=(
                "No route found between these locations. "
                "Check the map connections and accessibility options."
            ),
        )

    # Record staircase and lift transitions in the route.
    vertical_transitions = []

    for source, target in zip(path, path[1:]):
        transition = transitions.get((source, target))

        if transition is None:
            continue

        source_floor = MAP_LOCATIONS.get(source, {}).get("floor")
        target_floor = MAP_LOCATIONS.get(target, {}).get("floor")

        vertical_transitions.append({
            "from": source,
            "to": target,
            "type": transition.get("type", "stairs"),
            "from_floor": source_floor,
            "to_floor": target_floor,
            "vertical_distance_meters": None,
        })

    # Generate written, step-by-step directions.
    route_directions = generate_directions(
        path,
        locations=MAP_LOCATIONS,
        transitions=transitions,
    )

    # Walking-time estimate uses known horizontal distance only.
    walking_time = calculate_walking_time(horizontal_distance)

    return {
        "start": start,
        "destination": destination,
        "accessible_route": accessible,
        "route": path,

        "distance_meters": round(horizontal_distance, 2),
        "horizontal_distance_meters": round(horizontal_distance, 2),

        "vertical_transition_count": len(vertical_transitions),
        "vertical_transitions": vertical_transitions,

        "walking_time_minutes": walking_time,

        "distance_note": (
            "Distance and walking time include known horizontal "
            "segments only. Vertical travel distances and times are "
            "not included because they have not been verified."
        ),

        "directions": route_directions,
    }
