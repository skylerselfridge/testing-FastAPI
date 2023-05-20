from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker
import pytest
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.TEST_DB_NAME}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test1@test.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@test.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "test post 1",
            "content": "test post 1 content",
            "user_id": test_user["id"],
        },
        {
            "title": "test post 2",
            "content": "test post 2 content",
            "user_id": test_user["id"],
        },
        {
            "title": "test post 3",
            "content": "test post 3 content",
            "user_id": test_user["id"],
        },
        {
            "title": "test post 4",
            "content": "test post 4 content",
            "user_id": test_user2["id"],
        },
    ]

    def convert_post_model(post):
        return models.Post(**post)

    session.add_all(list(map(convert_post_model, posts_data)))
    session.commit()
    return session.query(models.Post).all()


@pytest.fixture
def test_vote(test_posts, session, test_user):
    session.add(models.Vote(post_id=test_posts[0].id, user_id=test_user["id"]))
    session.commit()
