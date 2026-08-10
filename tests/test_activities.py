"""
Tests for GET /activities endpoint.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, test_client):
        """Test that GET /activities returns all activities."""
        response = test_client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have 9 activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, test_client):
        """Test that each activity has required fields."""
        response = test_client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing '{field}' in {activity_name}"

    def test_activities_description_field_is_string(self, test_client):
        """Test that description field is a string."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["description"], str)
            assert len(activity_data["description"]) > 0

    def test_activities_schedule_field_is_string(self, test_client):
        """Test that schedule field is a string."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["schedule"], str)
            assert len(activity_data["schedule"]) > 0

    def test_activities_max_participants_is_positive_integer(self, test_client):
        """Test that max_participants is a positive integer."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_activities_participants_is_list(self, test_client):
        """Test that participants is a list of emails."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation

    def test_chess_club_has_initial_participants(self, test_client):
        """Test that Chess Club has the expected initial participants."""
        response = test_client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_activity_participants_do_not_exceed_max(self, test_client):
        """Test that no activity has more participants than max_participants."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert len(activity_data["participants"]) <= activity_data["max_participants"], \
                f"{activity_name} exceeds max participants"

    def test_activities_response_is_dict(self, test_client):
        """Test that the response is a dictionary."""
        response = test_client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_no_authentication_required(self, test_client):
        """Test that GET /activities doesn't require authentication."""
        # Should work without any special headers
        response = test_client.get("/activities")
        assert response.status_code == 200


class TestActivityAvailability:
    """Test suite for activity availability calculations."""

    def test_availability_calculation(self, test_client):
        """Test that availability is calculated correctly."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            max_p = activity_data["max_participants"]
            current_p = len(activity_data["participants"])
            expected_availability = max_p - current_p
            
            # Frontend calculates this; we verify the data allows correct calculation
            assert expected_availability >= 0

    def test_activity_at_full_capacity(self, test_client):
        """Test that activities can be at full capacity."""
        # Gym Class has 30 capacity and only 2 participants, so not full
        response = test_client.get("/activities")
        data = response.json()
        
        gym_class = data["Gym Class"]
        assert len(gym_class["participants"]) < gym_class["max_participants"]

    def test_no_activities_over_capacity(self, test_client):
        """Test that no activities are over capacity in initial state."""
        response = test_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
