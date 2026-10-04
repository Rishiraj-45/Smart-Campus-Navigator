from backend.database import SessionLocal
from backend.models import Location
from backend.navigation.locations import LOCATIONS


def seed_locations():
    db = SessionLocal()

    try:
        for name, info in LOCATIONS.items():

            existing = db.query(Location).filter(
                Location.name == name
            ).first()

            if existing:
                continue

            location = Location(
                name=info["name"],
                type=info["type"],
                building=info["building"],
                floor=info["floor"],
                accessible=info["accessible"]
            )

            db.add(location)

        db.commit()

        print("Sample campus locations added successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_locations()