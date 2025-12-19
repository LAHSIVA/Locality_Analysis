from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "postgresql://localhost/micro_locality_db"

engine = create_engine(DATABASE_URL)  # Creates a connection Factory [Connects Only When it is Needed]

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# DataBase Name : micro_locality_db
# sessionMaker : Each API request gets its own DB session , Prevents Data Corruption
# Base : Parent Class 
# SQLAlchemy  uses base to create table later


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get_db() --> one DB session per request