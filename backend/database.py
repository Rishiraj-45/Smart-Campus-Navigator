
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Allows a Render PostgreSQL URL if you choose PostgreSQL later.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )
    engine = create_engine(DATABASE_URL)
else:
    # Local development, or a persistent disk mounted at /var/data on Render.
    data_dir = Path(os.getenv("DATA_DIR", "."))
    data_dir.mkdir(parents=True, exist_ok=True)
    database_path = data_dir / "campus.db"

    engine = create_engine(
        f"sqlite:///{database_path.resolve().as_posix()}",
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
