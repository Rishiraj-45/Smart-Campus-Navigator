from backend.database import SessionLocal
from backend.models import Location


db = SessionLocal()

locations = db.query(Location).all()

print(f"Total locations: {len(locations)}")

for location in locations:
    print(
        f"{location.name} | "
        f"{location.type} | "
        f"{location.building} | "
        f"Floor {location.floor}"
    )

db.close()