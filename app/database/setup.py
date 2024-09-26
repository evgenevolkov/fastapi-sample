from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


dbname = config('POSTGRES_DATABASE')
user = config('POSTGRES_USER')
password = config('POSTGRES_PASSWORD')
host = config('POSTGRES_HOST')
port = config('POSTGRES_PORT')


SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:password123@localhost:5432/fastapi_sample_test"

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


