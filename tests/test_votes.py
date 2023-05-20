def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/", json={"post_id": str(test_posts[0].id), "dir": 1}
    )

    assert res.status_code == 201


def test_double_vote_on_post(authorized_client, test_posts, test_vote):
    res = authorized_client.post(
        "/vote/", json={"post_id": str(test_posts[0].id), "dir": 1}
    )

    assert res.status_code == 409


def test_delete_vote_on_post(authorized_client, test_posts, test_vote):
    res = authorized_client.post(
        "/vote/", json={"post_id": str(test_posts[0].id), "dir": 0}
    )

    assert res.status_code == 201


def test_delete_vote_non_exist(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/", json={"post_id": str(test_posts[0].id), "dir": 0}
    )

    assert res.status_code == 404


def test_vote_on_post_non_exist(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/", json={"post_id": "00000000-0000-0000-0000-000000000000", "dir": 1}
    )

    assert res.status_code == 404


def test_vote_on_post_invalid_uuid(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": "123", "dir": 1})

    assert res.status_code == 422


def test_vote_on_post_unauthorized_user(client, test_posts):
    res = client.post("/vote/", json={"post_id": str(test_posts[0].id), "dir": 1})

    assert res.status_code == 401
