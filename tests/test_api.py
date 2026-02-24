"""
Tests for Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    # Reset to initial state
    activities.clear()
    activities.update({
        "Soccer Team": {
            "description": "Join the school soccer team and compete in local leagues",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["charlotte@mergington.edu", "jackson@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Mondays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["henry@mergington.edu", "grace@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data

    def test_get_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)

    def test_get_activities_returns_current_participants(self, client):
        """Test that activities include current participants"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer Team"]
        assert "lucas@mergington.edu" in soccer["participants"]
        assert "mia@mergington.edu" in soccer["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to the activity"""
        client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "test@mergington.edu" in data["Soccer Team"]["participants"]

    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice returns an error"""
        email = "test@mergington.edu"
        
        # First signup
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup (duplicate)
        response2 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response2.status_code == 400
        
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_url_encoded_email(self, client):
        """Test signup with URL-encoded email"""
        response = client.post(
            "/activities/Soccer Team/signup?email=test%40mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Soccer Team/unregister?email=lucas@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "lucas@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from the activity"""
        client.delete("/activities/Soccer Team/unregister?email=lucas@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "lucas@mergington.edu" not in data["Soccer Team"]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregistering a participant who is not signed up"""
        response = client.delete(
            "/activities/Soccer Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        response = client.delete(
            "/activities/Soccer%20Team/unregister?email=lucas@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_url_encoded_email(self, client):
        """Test unregister with URL-encoded email"""
        response = client.delete(
            "/activities/Soccer Team/unregister?email=lucas%40mergington.edu"
        )
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complete user scenarios"""

    def test_complete_signup_and_unregister_flow(self, client):
        """Test a complete flow: signup then unregister"""
        email = "test@mergington.edu"
        activity = "Soccer Team"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple activities"""
        email = "test@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        response2 = client.post(f"/activities/Drama Club/signup?email={email}")
        response3 = client.post(f"/activities/Chess Club/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Verify participant in all activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Team"]["participants"]
        assert email in data["Drama Club"]["participants"]
        assert email in data["Chess Club"]["participants"]

    def test_activity_capacity_tracking(self, client):
        """Test that we can track how many spots are available"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer Team"]
        current_participants = len(soccer["participants"])
        max_participants = soccer["max_participants"]
        spots_left = max_participants - current_participants
        
        assert spots_left > 0
        assert current_participants <= max_participants
