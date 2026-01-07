import uuid

from sqlmodel import select

from backend.src.models.user import User


def test_register_success(client, db):
    resp = client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@example.com"
    assert "id" in data

    user = db.exec(select(User).where(User.email == "user@example.com")).first()
    assert user is not None
    assert user.password_hash != "password123"


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    resp = client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["expires_in"] > 0


def test_login_invalid_password(client):
    client.post("/auth/register", json={"email": "badpass@example.com", "password": "password123"})
    resp = client.post("/auth/login", json={"email": "badpass@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_register_invalid_email(client):
    resp = client.post("/auth/register", json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422


def test_register_short_password(client):
    resp = client.post("/auth/register", json={"email": "short@example.com", "password": "short"})
    assert resp.status_code == 422
