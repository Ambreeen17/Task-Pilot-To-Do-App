import uuid


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_full_flow_register_login_crud_toggle_search(client):
    email = f"flow-{uuid.uuid4()}@example.com"

    # register
    resp = client.post("/auth/register", json={"email": email, "full_name": "Flow User", "password": "password123"})
    assert resp.status_code == 201

    # login
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # empty list
    resp = client.get("/tasks", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0

    # create
    resp = client.post(
        "/tasks",
        json={"title": "Alpha", "description": "hello", "priority": "High"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    # get
    resp = client.get(f"/tasks/{task_id}", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["title"] == "Alpha"

    # update
    resp = client.put(
        f"/tasks/{task_id}",
        json={"title": "Alpha updated", "description": "hello", "priority": "Low", "completed": False},
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Alpha updated"

    # toggle
    resp = client.patch(f"/tasks/{task_id}/toggle", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["completed"] is True

    # search/filter
    resp = client.get("/tasks?search=Alpha", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/tasks?priority=Low", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/tasks?status=completed", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    # delete
    resp = client.delete(f"/tasks/{task_id}", headers=_auth_header(token))
    assert resp.status_code == 204

    # confirm gone
    resp = client.get(f"/tasks/{task_id}", headers=_auth_header(token))
    assert resp.status_code == 404
