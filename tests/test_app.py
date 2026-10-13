import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_website():
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)


def test_get_activities_returns_dictionary():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) >= 4


def test_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_duplicate_participant_is_rejected():
    # Arrange
    activity = "Chess Club"
    email = "duplicatestudent@mergington.edu"

    # Act
    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    second = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400


def test_unregister_removes_participant():
    # Arrange
    activity = "Chess Club"
    email = "leavingstudent@mergington.edu"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    # Act
    response = client.post(
        "/activities/UnknownActivity/signup", params={"email": "x@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
