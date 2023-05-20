from fastapi import HTTPException, status
from app import schemas
from .database import client, session
import pytest
from app import oauth2


@pytest.fixture
def test_user(client):
    user_data = {"email": "test1@test.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


def test_root(client):
    res = client.get("/")
    assert res.json().get("message") == "hello"
    assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "test1@test.com", "password": "password123"}
    )
    user = schemas.UserData(**res.json())
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login/",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_response = schemas.Token(**res.json())
    # verify token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    assert (
        oauth2.verify_access_token(
            login_response.access_token, credentials_exception=credentials_exception
        ).user_id
        == test_user["id"]
    )
    assert login_response.token_type == "bearer"
    assert res.status_code == 200
