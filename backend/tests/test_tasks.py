from datetime import datetime, timedelta, timezone


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, email: str = "user@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_create_and_list_tasks_user_scoped(client):
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")

    resp = client.post(
        "/tasks",
        json={"title": "Task A", "description": "desc", "priority": "High"},
        headers=_auth_header(token_a),
    )
    assert resp.status_code == 201

    resp = client.get("/tasks", headers=_auth_header(token_a))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/tasks", headers=_auth_header(token_b))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_update_task(client):
    token = _register_and_login(client, "u@example.com")
    create = client.post("/tasks", json={"title": "t", "priority": "Medium"}, headers=_auth_header(token))
    task_id = create.json()["id"]

    upd = client.put(
        f"/tasks/{task_id}",
        json={"title": "updated", "completed": True, "priority": "Low"},
        headers=_auth_header(token),
    )
    assert upd.status_code == 200
    assert upd.json()["title"] == "updated"
    assert upd.json()["completed"] is True
    assert upd.json()["priority"] == "Low"


def test_toggle_task(client):
    token = _register_and_login(client, "toggle@example.com")
    create = client.post("/tasks", json={"title": "t"}, headers=_auth_header(token))
    task_id = create.json()["id"]

    resp = client.patch(f"/tasks/{task_id}/toggle", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


def test_delete_task(client):
    token = _register_and_login(client, "del@example.com")
    create = client.post("/tasks", json={"title": "t"}, headers=_auth_header(token))
    task_id = create.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers=_auth_header(token))
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}", headers=_auth_header(token))
    assert resp.status_code == 404


def test_search_and_filter(client):
    token = _register_and_login(client, "search@example.com")
    client.post("/tasks", json={"title": "Alpha", "description": "hello", "priority": "High"}, headers=_auth_header(token))
    client.post("/tasks", json={"title": "Beta", "description": "world", "priority": "Low"}, headers=_auth_header(token))

    resp = client.get("/tasks?search=Alpha", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/tasks?priority=Low", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    # mark one completed
    tasks = client.get("/tasks", headers=_auth_header(token)).json()["tasks"]
    beta_id = [t for t in tasks if t["title"] == "Beta"][0]["id"]
    client.patch(f"/tasks/{beta_id}/toggle", headers=_auth_header(token))

    resp = client.get("/tasks?status=completed", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
