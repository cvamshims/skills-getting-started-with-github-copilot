import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Soccer Team" in data
    assert "Basketball Club" in data

def test_signup_for_activity():
    activity_name = "Soccer Team"
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify student is in participants
    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]

def test_signup_already_registered():
    activity_name = "Soccer Team"
    email = "alex@mergington.edu" # Already in initial data
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_unregister_from_activity():
    activity_name = "Soccer Team"
    email = "alex@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify student is no longer in participants
    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]

def test_unregister_not_signed_up():
    activity_name = "Soccer Team"
    email = "not_signed_up@example.com"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"

def test_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
