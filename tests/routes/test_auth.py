from decouple import config
from jose import jwt

from app.utils import schemas


prefix = '/login'


def test_login(client, end_user):
    # test access
    body = {
        "username": end_user['email'], 
        "password": end_user['password']
    }
    resp = client.post(prefix + '/', data=body)

    print(f"test login resp: {resp}")
    print(f"test login resp.json: {resp.json()}")

    token = schemas.Token(**resp.json())
    payload = jwt.decode(token=token.access_token, key=config('SECRET_KEY'),
                         algorithms=config('ALGORITHM'))
    user_id: str = payload.get('user_id')

    assert resp.status_code == 200
    assert resp.json().get('token_type') == 'bearer' 
    assert user_id == end_user['id']


def test_incorrect_login(client, end_user):
        # test access
    body = {
        "username": end_user['email'], 
        "password": end_user['password'] + "wrong" # to set incorrect password
    }
    resp = client.post(prefix + '/', data=body)

    print(f"test incorrect login resp: {resp}")
    print(f"test incorrect login resp.json: {resp.json()}")

    assert resp.status_code == 403
    assert resp.json().get('detail') == 'invalid credentials'
