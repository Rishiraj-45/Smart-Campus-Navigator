from sqlalchemy import Column, Integer, String, Boolean
from backend.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    type = Column(String, nullable=False)

    building = Column(String, nullable=False)

    floor = Column(Integer, nullable=False)

    accessible = Column(Boolean, default=True)