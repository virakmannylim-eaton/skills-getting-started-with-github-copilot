from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # make a shallow copy of original state and restore after test
    original = {k: {**v, "participants": v["participants"].copy()} for k, v in activities.items()}
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_dict():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_successful_signup_and_duplicate_error():
    email = "tester1@mergington.edu"
    activity = "Chess Club"

    # ensure email not already in participants
    assert email not in activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # second attempt should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json()["detail"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NotAThing/signup?email=foo@bar.com")
    assert resp.status_code == 404


def test_remove_participant_and_errors():
    activity = "Programming Class"
    email = "unique@mergington.edu"

    # signup first so we can delete
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # delete now
    r2 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 200
    assert email not in activities[activity]["participants"]

    # attempt to delete again yields 404
    r3 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert r3.status_code == 404


def test_remove_from_wrong_activity():
    # activity doesn't exist
    resp = client.delete("/activities/nada/signup?email=someone@mergington.edu")
    assert resp.status_code == 404
