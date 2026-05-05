"""
Comprehensive tests for Mergington High School API using AAA (Arrange-Act-Assert) pattern.

Tests cover all endpoints:
- GET / (redirect)
- GET /activities (list activities)
- POST /activities/{activity_name}/signup (register student)
- POST /activities/{activity_name}/unregister (unregister student)
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to a known state before each test.
    This ensures test isolation and prevents state from leaking between tests.
    """
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 25,
            "participants": ["harper@mergington.edu", "logan@mergington.edu"]
        }
    }

    # Deep copy to reset activities before test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

    yield

    # Clean up after test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    """Create a TestClient for making requests to the app."""
    return TestClient(app)


# ============================================================================
# Tests for GET / (Root Redirect)
# ============================================================================

class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.

        Arrange: Set up test client
        Act: Make GET request to /
        Assert: Verify redirect status and target URL
        """
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


# ============================================================================
# Tests for GET /activities (List Activities)
# ============================================================================

class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.

        Arrange: Define expected activity names
        Act: Make GET request to /activities
        Assert: Verify response contains all activities
        """
        # Arrange
        expected_activity_names = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_activity_names

    def test_get_activities_returns_correct_structure(self, client):
        """
        Test that each activity has the required structure.

        Arrange: Define required fields for an activity
        Act: Make GET request to /activities
        Assert: Verify each activity has description, schedule, max_participants, participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, activity_data in data.items():
            assert set(activity_data.keys()) == required_fields

    def test_get_activities_returns_correct_participant_counts(self, client):
        """
        Test that participant counts are accurate.

        Arrange: Define expected participant counts
        Act: Make GET request to /activities
        Assert: Verify participant counts match expected values
        """
        # Arrange
        expected_counts = {
            "Chess Club": 2,
            "Programming Class": 2,
            "Gym Class": 2,
            "Basketball Team": 1,
            "Soccer Club": 2,
            "Art Club": 1,
            "Drama Club": 2,
            "Debate Club": 1,
            "Science Club": 2
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, expected_count in expected_counts.items():
            assert len(data[activity_name]["participants"]) == expected_count


# ============================================================================
# Tests for POST /activities/{activity_name}/signup (Student Signup)
# ============================================================================

class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_successful(self, client):
        """
        Test successful signup of a new student.

        Arrange: Define a new student email and activity
        Act: Make POST request to signup endpoint
        Assert: Verify 200 response and success message
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_verifies_participant_added(self, client):
        """
        Test that signup actually adds participant to activity.

        Arrange: Track initial participant count
        Act: Make POST request to signup endpoint
        Assert: Verify participant list includes new email
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count + 1
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """
        Test signup attempt for non-existent activity.

        Arrange: Define invalid activity name
        Act: Make POST request with invalid activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_student_already_registered(self, client):
        """
        Test signup attempt for already registered student.

        Arrange: Select existing participant and activity
        Act: Try to signup same student again
        Assert: Verify 400 status and duplicate error message
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_activities_allowed(self, client):
        """
        Test that a student can register for multiple different activities.

        Arrange: Select student and two different activities
        Act: Make POST requests to signup for both activities
        Assert: Verify both signups successful and student in both activities
        """
        # Arrange
        email = "multiactivity@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


# ============================================================================
# Tests for POST /activities/{activity_name}/unregister (Student Unregister)
# ============================================================================

class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_successful(self, client):
        """
        Test successful unregistration of existing participant.

        Arrange: Select existing participant in activity
        Act: Make POST request to unregister endpoint
        Assert: Verify 200 response and success message
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_verifies_participant_removed(self, client):
        """
        Test that unregister actually removes participant from activity.

        Arrange: Track initial participant count
        Act: Make POST request to unregister endpoint
        Assert: Verify participant count decreases and email not in list
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count - 1
        assert email not in activities[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """
        Test unregister attempt for non-existent activity.

        Arrange: Define invalid activity name
        Act: Make POST request with invalid activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self, client):
        """
        Test unregister attempt for non-participant.

        Arrange: Select email not registered for activity
        Act: Make POST request to unregister with non-participant email
        Assert: Verify 400 status and not found error
        """
        # Arrange
        activity = "Chess Club"
        email = "notregistered@mergington.edu"  # Not registered

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_then_can_register_again(self, client):
        """
        Test that unregistered student can register again for same activity.

        Arrange: Select existing participant
        Act: Unregister, then register again
        Assert: Both operations succeed and student is back in activity
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act - Unregister
        response1 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Act - Register again
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity]["participants"]

    def test_unregister_one_does_not_affect_others(self, client):
        """
        Test that unregistering one student doesn't affect other participants.

        Arrange: Identify target and other participants
        Act: Unregister target participant
        Assert: Other participants still in activity, only target removed
        """
        # Arrange
        activity = "Drama Club"
        target_email = "mason@mergington.edu"
        other_email = "charlotte@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": target_email}
        )

        # Assert
        assert response.status_code == 200
        assert target_email not in activities[activity]["participants"]
        assert other_email in activities[activity]["participants"]


# ============================================================================
# Integration Tests (Signup + Unregister Flow)
# ============================================================================

class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister workflows."""

    def test_full_signup_unregister_cycle(self, client):
        """
        Test complete signup and unregister cycle for a student.

        Arrange: Define new student and activity
        Act: Signup, verify, unregister, verify
        Assert: Participant count correct at each step
        """
        # Arrange
        email = "integration@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])

        # Act - Signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert - After signup
        assert response1.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count + 1
        assert email in activities[activity]["participants"]

        # Act - Unregister
        response2 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert - After unregister
        assert response2.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count
        assert email not in activities[activity]["participants"]

    def test_signup_multiple_then_unregister_one(self, client):
        """
        Test signing up multiple times then unregistering from one activity.

        Arrange: New student and multiple activities
        Act: Signup for two activities, unregister from one
        Assert: Student only in remaining activity
        """
        # Arrange
        email = "multi@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Art Club"

        # Act - Signup for both
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        client.post(f"/activities/{activity2}/signup", params={"email": email})

        # Act - Unregister from first
        response = client.post(
            f"/activities/{activity1}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
