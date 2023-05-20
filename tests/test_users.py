from fastapi import HTTPException, status
from app import schemas
from app import oauth2
import pytest


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


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("wrongemail@email.com", "password123", 403),
        ("test1@test.com", "wrongpassword", 403),
        ("wrong@wrong.com", "wrongpassword", 403),
        (None, "password123", 422),
        ("test1@test.com", None, 422),
        (None, None, 422),
    ],
)
def test_incorrect_login(client, email, password, status_code):
    response_wrong_password = client.post(
        "/login", data={"username": email, "password": password}
    )

    assert response_wrong_password.status_code == status_code
