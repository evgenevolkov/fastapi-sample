from datetime import datetime, timedelta, UTC
from decouple import config
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..database import models
from . import schemas
from ..database.setup import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(
        data: dict,
        secret_key: str,
        algorithm: str,
        token_expire_minutes: int):
    
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=token_expire_minutes)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(claims=to_encode, key=secret_key,
                             algorithm=algorithm)

    return {"token": encoded_jwt, 
            "expire_at": expire} 


def verify_access_token(
        token: str,
        credentials_exception,
        secret_key: str,
        algorithm: str) -> schemas.TokenData:
    
    try:
        payload = jwt.decode(token=token, key=secret_key,
                             algorithms=[algorithm])
        user_id: str = payload.get('user_id')
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)) -> schemas.UserCurrent:
    credentials_exception = HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_access_token(token, credentials_exception, 
                                     secret_key=config('SECRET_KEY'),
                                     algorithm=config('ALGORITHM')) 
    user_data = (db.query(models.Users)
                   .filter(models.Users.id==token_data.user_id)
                   .first())
    
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No user with id: {token_data.user_id} found")

    current_user = schemas.UserCurrent(
                        id=token_data.user_id,
                        role=user_data.role)

    return current_user