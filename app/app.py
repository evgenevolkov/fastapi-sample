from decouple import config
from datetime import time
from fastapi import FastAPI, Depends
import psycopg2
from sqlalchemy.orm import Session

from .utils import schemas
from .database.setup import engine, get_db
from .database import models
from .utils.logger import get_logger
from .routers import auth, texts, users


timeout = 3
logger = get_logger(__name__)
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


while True:  # infinitely try to connect to database unless succeeded
    logger.debug('Attempting to connect to the DB')
    try:
        conn = psycopg2.connect(f"""
            host={config('POSTGRES_HOST')}
            port={config('POSTGRES_PORT')}
            dbname={config('POSTGRES_DATABASE')}
            user={config('POSTGRES_USER')}
            password={config('POSTGRES_PASSWORD')}
            """
            )
      
        logger.debug('Succesfully connected to DB')
        break
    except Exception as error:
        logger.error("Failed to connect to DB")
        logger.error(f"Error: {error}")
        logger.error(f"Will try to connect in {timeout} sec.")
        time.sleep(timeout)


@app.get('/')
async def root():
    return {"message": "Root"}


@app.get('/debug')
def debug(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)):
    return {"message": "Debug route."}


app.include_router(auth.router)
app.include_router(texts.router)
app.include_router(users.router)