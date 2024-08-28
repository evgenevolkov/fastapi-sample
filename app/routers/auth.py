from decouple import config
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from ..database import models
from ..database.setup import get_db
from ..utils import oauth2, schemas, utils


router = APIRouter(prefix='/login', tags=['Authentication'])

@router.post('/', response_model=schemas.Token, status_code=status.HTTP_200_OK)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(models.Users).filter(
        models.Users.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='invalid credentials')
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status.HTTP_403_FORBIDDEN, 
                            detail='invalid credentials')

    expire = int(config('TOKEN_EXPIRE_MINUTES'))
    auth_data = oauth2.create_access_token(
                    data={"user_id": user.id},
                    secret_key=config('SECRET_KEY'),
                    algorithm=config('ALGORITHM'),
                    token_expire_minutes=expire)

    token_data = schemas.Token(
                    access_token=auth_data["token"],
                    expire_at=auth_data["expire_at"],
                    token_type="bearer")

    return token_data
