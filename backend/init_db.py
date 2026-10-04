from backend.database import engine, Base
from backend.models import Location

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")