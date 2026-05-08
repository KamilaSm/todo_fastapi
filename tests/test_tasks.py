from main import app, get_session


def test_create_task(client):
    response = client.post("/task/", json={"title": "Test Task", "description": "Desc"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_get_task(client):
    post_response = client.post("/task/", json={"title": "Test Task", "description": "Desc", "is_done": False})
    task_id = post_response.json()["id"]
    response = client.get(f"/taskes/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_update_task(client):
    post_response = client.post("/task/", json={"title": "Test Task", "description": "Desc", "is_done": False})
    task_id = post_response.json()["id"]
    response = client.patch(f"/taskes/{task_id}", json={"title": "update Task"})
    assert response.status_code == 200
    assert response.json()["title"] == "update Task"

def test_delete_task(client):
    post_response = client.post("/task/", json={"title": "Test Task", "description": "Desc", "is_done": False})
    task_id = post_response.json()["id"]
    response = client.delete(f"/taskes/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

