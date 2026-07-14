from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os   

load_dotenv()


DATABASE_URL=os.getenv("DATABASE_set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()



def get_db():
    """
    Production-grade Database Session Generator.
    Guarantees that every API request gets its own isolated database connection
    and safely closes it when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()