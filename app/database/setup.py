from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


dbname=config('postgres_database')
user=config('postgres_user')
password=config('postgres_password')

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@localhost/{dbname}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


