from app.utils import schemas


prefix = '/users'


def test_create(client):

    body = schemas.UserCreate(
        name="test_create_user", 
        email="test_create_user@test.user.com",
        password="password"
    )
    resp = client.post(prefix + '/create', json=body.model_dump())

    print(f"test_created resp: {resp.json()}")
    # validate schema of the output
    new_user = schemas.UserOut(**resp.json())
    assert new_user.name == "test_create_user"
    assert new_user.email == "test_create_user@test.user.com"

    assert resp.status_code == 201 


def test_all_end_user_role(authorised_client_end_user):
    """ End user should not have access to all users"""
    resp = authorised_client_end_user.get(prefix + '/all')

    print(f"test_all_end_user resp: {resp.json()}, status_code: {resp.status_code}")

    assert resp.status_code == 401


def test_all_admin_role(authorised_client_admin):
    """ Admin should have access to all users"""
    resp = authorised_client_admin.get(prefix + '/all')

    print(f"test_all_admin resp: {resp.json()}, status_code: {resp.status_code}")

    assert resp.status_code == 200