"""
FastAPI Application Tests

Comprehensive test suite for the Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern with pytest fixtures for test isolation.
"""

import pytest
import copy
from starlette.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance.
    Resets the activities data before each test to ensure isolation.
    """
    # Arrange: Create a fresh copy of activities for each test
    original_activities = copy.deepcopy(activities)
    
    # Clear existing participants and reset to original state
    activities.clear()
    activities.update(original_activities)
    
    # Yield the TestClient for the test to use
    yield TestClient(app)
    
    # Cleanup: Restore original state after test completes
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200_status(self, client):
        """
        ARRANGE: Prepare TestClient
        ACT: Make GET request to /activities
        ASSERT: Verify response status is 200
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Prepare TestClient
        ACT: Make GET request to /activities
        ASSERT: Verify all 9 activities are returned
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Club" in data
        assert "Science Club" in data
    
    def test_get_activities_contains_required_fields(self, client):
        """
        ARRANGE: Prepare TestClient
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has all required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_existing_participants(self, client):
        """
        ARRANGE: Prepare TestClient with activities that have participants
        ACT: Make GET request to /activities
        ASSERT: Verify participants are included in response
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful_with_valid_activity_and_email(self, client):
        """
        ARRANGE: Prepare TestClient and identify empty activity
        ACT: Sign up a new participant for Basketball Team
        ASSERT: Verify response is 200 and success message returned
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Get initial participant count for Basketball Team
        ACT: Sign up a new participant
        ASSERT: Verify participant is added to activity's participants list
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]
    
    def test_signup_fails_with_nonexistent_activity(self, client):
        """
        ARRANGE: Prepare TestClient with non-existent activity name
        ACT: Attempt to sign up for activity that doesn't exist
        ASSERT: Verify 404 error is returned
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_allows_duplicate_signup(self, client):
        """
        ARRANGE: Sign up a participant once
        ACT: Attempt to sign up same participant again
        ASSERT: Verify participant is added twice (current behavior - no validation)
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        # Note: Current implementation allows duplicate signups
        assert len(activities[activity_name]["participants"]) == initial_count + 1


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_successful(self, client):
        """
        ARRANGE: Identify activity with existing participants
        ACT: Remove a participant from Chess Club
        ASSERT: Verify response is 200 and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_remove_participant_removes_from_activity(self, client):
        """
        ARRANGE: Get initial participant count
        ACT: Remove a participant from Chess Club
        ASSERT: Verify participant is removed from activity's participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_participant_fails_with_nonexistent_activity(self, client):
        """
        ARRANGE: Prepare non-existent activity name
        ACT: Attempt to remove participant from non-existent activity
        ASSERT: Verify 404 error is returned
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_participant_fails_with_nonexistent_participant(self, client):
        """
        ARRANGE: Prepare activity name and email not in participants
        ACT: Attempt to remove participant that doesn't exist in activity
        ASSERT: Verify 404 error is returned with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_participant_updates_availability(self, client):
        """
        ARRANGE: Get initial availability (spots left)
        ACT: Remove a participant
        ASSERT: Verify availability increases after removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        max_participants = activities[activity_name]["max_participants"]
        initial_availability = max_participants - len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        new_availability = max_participants - len(activities[activity_name]["participants"])
        assert new_availability == initial_availability + 1


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Prepare TestClient
        ACT: Make GET request to /
        ASSERT: Verify redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_signup_and_then_remove_workflow(self, client):
        """
        ARRANGE: Prepare activity and new participant email
        ACT: Sign up participant, then remove participant
        ASSERT: Verify participant added then removed correctly
        """
        # Arrange
        activity_name = "Soccer Club"
        email = "test@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        after_signup_count = len(activities[activity_name]["participants"])
        
        # Assert signup
        assert signup_response.status_code == 200
        assert after_signup_count == initial_count + 1
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        final_count = len(activities[activity_name]["participants"])
        
        # Assert remove
        assert remove_response.status_code == 200
        assert final_count == initial_count
    
    def test_multiple_participants_signup(self, client):
        """
        ARRANGE: Prepare activity and multiple participant emails
        ACT: Sign up multiple participants one by one
        ASSERT: Verify all participants are added to activity
        """
        # Arrange
        activity_name = "Art Club"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        final_count = len(activities[activity_name]["participants"])
        assert final_count == initial_count + len(emails)
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestActivityDataConsistency:
    """Tests for data integrity and consistency"""
    
    def test_activities_structure_is_consistent(self, client):
        """
        ARRANGE: Get all activities
        ACT: Verify structure after operations
        ASSERT: Verify all activities maintain consistent structure
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert isinstance(activity_data.get("participants"), list)
            assert isinstance(activity_data.get("max_participants"), int)
            assert activity_data["max_participants"] > 0
    
    def test_participant_capacity_is_not_enforced(self, client):
        """
        ARRANGE: Have activity with limited capacity
        ACT: Sign up more participants than capacity allows
        ASSERT: Verify current implementation allows over-capacity signups
        """
        # Arrange
        activity_name = "Drama Club"
        max_participants = activities[activity_name]["max_participants"]
        
        # Act - Sign up more than max capacity
        for i in range(max_participants + 2):
            email = f"student{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Assert - Current implementation allows over-capacity
        assert len(activities[activity_name]["participants"]) > max_participants
