from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app=app)

def test_root():
    resp = client.get('/')
    print(resp.json())

    
    assert resp.json().get("message", None) == "Root"
    assert resp.status_code == 200