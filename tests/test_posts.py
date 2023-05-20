from uuid import UUID
from app import schemas
import pytest


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    def convert_to_post_schema(post):
        return schemas.PostOut(**post)

    posts = list(map(convert_to_post_schema, res.json()))

    assert len(posts) == len(test_posts) == 4
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")

    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401


def test_get_one_post_invalid_uuid(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{1}")

    assert res.status_code == 400


def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/00000000-0000-0000-0000-000000000000")

    assert res.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())

    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert post.Post.user_id == test_posts[0].user_id
    assert post.Post.time_stamp == test_posts[0].time_stamp
    assert res.status_code == 200


@pytest.mark.parametrize(
    "title,content,published,status_code",
    [
        ("title 1", "content 1", False, 201),
        ("title 2", "content 2", True, 201),
        ("title 3", "content 3", False, 201),
        (None, "content 4", False, 422),
        ("title 4", None, True, 422),
        (None, None, True, 422),
    ],
)
def test_create_post(
    authorized_client, test_user, test_posts, title, content, published, status_code
):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )

    assert res.status_code == status_code

    if status_code == 201:
        post = schemas.Post(**res.json())
        assert published == post.published
        assert title == post.title
        assert content == post.content
        assert UUID(test_user["id"]) == post.user_id == post.owner.id
        assert test_user["email"] == post.owner.email


@pytest.mark.parametrize(
    "title,content,status_code",
    [
        ("title 1", "content 1", 201),
        ("title 2", "content 2", 201),
        ("title 3", "content 3", 201),
        (None, "content 4", 422),
        ("title 4", None, 422),
        (None, None, 422),
    ],
)
def test_create_post_default_published_true(
    authorized_client, test_user, test_posts, title, content, status_code
):
    res = authorized_client.post("/posts/", json={"title": title, "content": content})

    assert res.status_code == status_code

    if status_code == 201:
        post = schemas.Post(**res.json())
        assert True == post.published
        assert title == post.title
        assert content == post.content
        assert UUID(test_user["id"]) == post.user_id == post.owner.id
        assert test_user["email"] == post.owner.email


def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post("/posts/", json={"title": "title", "content": "content"})

    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401


def test_delete_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/00000000-0000-0000-0000-000000000000")

    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[-1].id}")

    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    res = authorized_client.put(
        f"/posts/{test_posts[0].id}",
        json={"title": "updated", "content": "updated", "published": False},
    )

    post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert post.id == test_posts[0].id
    assert post.title == "updated"
    assert post.content == "updated"
    assert post.published == False


def test_update__post_not_exist(authorized_client, test_user, test_posts):
    res = authorized_client.put(
        f"/posts/00000000-0000-0000-0000-000000000000",
        json={"title": "updated", "content": "updated", "published": False},
    )

    assert res.status_code == 404


def test_update_other_user_post(authorized_client, test_posts):
    res = authorized_client.put(
        f"/posts/{test_posts[-1].id}",
        json={"title": "wrong", "content": "wrong", "published": False},
    )

    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(
        f"/posts/{test_posts[0].id}",
        json={"title": "updated", "content": "updated", "published": False},
    )

    assert res.status_code == 401
