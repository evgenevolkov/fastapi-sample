# from tests.database import session, client
from decouple import config
from fastapi.testclient import TestClient
import pytest
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.database.models import Base
from app.database.setup import get_db 
from app.utils import schemas, oauth2


# # Override db with test database
dbname='fastapi_sample_test'
user=config('POSTGRES_USER')
password=config('POSTGRES_PASSWORD')
host=config('POSTGRES_HOST')
port=config('POSTGRES_PORT')

# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:password123@localhost:5432/fastapi_sample_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@fixture()
def admin(client):
    # create test user
    body = schemas.UserCreate(
        name="test_admin", 
        email="test_admin@test.user.com",
        password="password", 
        role = "admin"
    )
    resp = client.post('users/create', json=body.model_dump())
    
    # store for further use
    new_user = resp.json()
    new_user['password'] = body.password

    print(f"Fixture admin: {new_user}")

    assert resp.status_code == 201
    assert resp.json().get('name') == body.name
    assert resp.json().get('email') == body.email

    return new_user


@fixture()
def end_user(client):
    # create test user
    body = schemas.UserCreate(
        name="test_end_user", 
        email="test_end_user@test.user.com",
        password="password", 
        role = "end_user"
    )
    resp = client.post('users/create', json=body.model_dump())
    
    # store for further use
    new_user = resp.json()
    new_user['password'] = body.password

    print(f"Fixture end user: {new_user}")

    assert resp.status_code == 201
    assert resp.json().get('name') == body.name
    assert resp.json().get('email') == body.email

    return new_user

def get_token(user_id):
    auth_data = oauth2.create_access_token(
                    data={"user_id": user_id},
                    secret_key=config('SECRET_KEY'),
                    algorithm=config('ALGORITHM'),
                    token_expire_minutes=int(config('TOKEN_EXPIRE_MINUTES'))
    )
    return auth_data['token']


@fixture()
def authorised_client_admin(client, admin):
    token = get_token(admin['id'])
    print(f"Fixture admin: {admin}")
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    print(f"client.headers: {client.headers}")
    print(f"Fixture token: {token}")

    return client


@fixture()
def authorised_client_end_user(client, end_user):
    token = get_token(end_user['id'])
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    print(f"Fixture token: {token}")

    return client