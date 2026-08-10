"""
Tests for POST /activities/{activity_name}/signup endpoint.
"""

import pytest


class TestSignupHappyPath:
    """Test successful signup scenarios."""

    def test_successful_signup(self, test_client, sample_emails, activity_name):
        """Test successful signup adds student to activity."""
        email = sample_emails[0]
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_to_participants_list(self, test_client, sample_emails, activity_name):
        """Test that signup actually adds student to participants list."""
        email = sample_emails[0]
        
        # Get initial state
        initial_response = test_client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        initial_count = len(initial_participants)
        
        # Sign up
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated state
        updated_response = test_client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        assert len(updated_participants) == initial_count + 1
        assert email in updated_participants

    def test_signup_decreases_availability(self, test_client, sample_emails, activity_name):
        """Test that signup decreases available spots."""
        email = sample_emails[0]
        
        # Get initial availability
        initial_response = test_client.get("/activities")
        activity = initial_response.json()[activity_name]
        initial_availability = activity["max_participants"] - len(activity["participants"])
        
        # Sign up
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated availability
        updated_response = test_client.get("/activities")
        activity = updated_response.json()[activity_name]
        updated_availability = activity["max_participants"] - len(activity["participants"])
        
        assert updated_availability == initial_availability - 1

    def test_multiple_students_can_signup(self, test_client, sample_emails):
        """Test that multiple students can sign up for the same activity."""
        activity_name = "Gym Class"  # Has high capacity
        
        # Sign up multiple students
        for email in sample_emails[:3]:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        activities_response = test_client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        
        for email in sample_emails[:3]:
            assert email in participants

    def test_signup_response_format(self, test_client, sample_emails, activity_name):
        """Test that signup response has correct format."""
        email = sample_emails[0]
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestSignupErrorHandling:
    """Test error scenarios for signup."""

    def test_signup_nonexistent_activity(self, test_client, sample_emails):
        """Test signup fails for non-existent activity."""
        email = sample_emails[0]
        
        response = test_client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_student(self, test_client, existing_participant, activity_name):
        """Test that same student cannot signup twice for same activity."""
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_activity_full(self, test_client, sample_emails):
        """Test signup fails when activity is at capacity."""
        # Create a nearly-full activity scenario
        activity_name = "Tennis Club"  # max 12 participants
        
        # Get current participants
        response = test_client.get("/activities")
        current_count = len(response.json()[activity_name]["participants"])
        
        # Fill remaining spots
        emails_to_add = sample_emails[:12]  # Try to add many students
        for i, email in enumerate(emails_to_add):
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            if current_count + i + 1 > 12:
                # Should fail when full
                assert response.status_code == 400
                data = response.json()
                assert "full" in data["detail"].lower()
            else:
                # Should succeed while space available
                assert response.status_code == 200

    def test_signup_error_response_has_detail(self, test_client, sample_emails):
        """Test that error responses include detail message."""
        response = test_client.post(
            "/activities/Fake Activity/signup",
            params={"email": sample_emails[0]}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestSignupValidation:
    """Test input validation for signup."""

    def test_signup_with_various_email_formats(self, test_client, activity_name):
        """Test signup with different email formats."""
        emails = [
            "simple@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
        ]
        
        for email in emails:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400, 404]

    def test_signup_activity_name_with_spaces(self, test_client, sample_emails):
        """Test signup with activity names containing spaces."""
        email = sample_emails[0]
        
        # Activity names have spaces
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Should work with spaces (or fail with 400/404, not 500)
        assert response.status_code != 500

    def test_signup_case_sensitive_activity_name(self, test_client, sample_emails):
        """Test that activity names are case-sensitive."""
        email = sample_emails[0]
        
        # Try lowercase - should fail
        response = test_client.post(
            "/activities/chess club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404

    def test_signup_url_encoding_in_activity_name(self, test_client, sample_emails):
        """Test signup works with URL-encoded activity names."""
        email = sample_emails[0]
        activity_name_encoded = "Programming%20Class"
        
        response = test_client.post(
            f"/activities/{activity_name_encoded}/signup",
            params={"email": email}
        )
        
        # Should successfully decode and either succeed or fail appropriately
        assert response.status_code != 500


class TestSignupIntegration:
    """Integration tests combining multiple signup operations."""

    def test_signup_then_verify_in_get(self, test_client, sample_emails, activity_name):
        """Test that signup data immediately appears in GET /activities."""
        email = sample_emails[0]
        
        # Signup
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify in activities list
        response = test_client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        assert email in participants

    def test_multiple_signups_cumulative(self, test_client, sample_emails):
        """Test that multiple signups properly accumulate."""
        activity_name = "Gym Class"
        
        # Sign up 3 students
        for email in sample_emails[:3]:
            test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Get activities
        response = test_client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # All three should be there
        for email in sample_emails[:3]:
            assert email in participants

    def test_signup_preserves_existing_participants(self, test_client, sample_emails, activity_name):
        """Test that new signup doesn't remove existing participants."""
        email = sample_emails[0]
        
        # Get existing participants before signup
        response = test_client.get("/activities")
        existing = response.json()[activity_name]["participants"].copy()
        
        # Signup new student
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated participants
        response = test_client.get("/activities")
        updated = response.json()[activity_name]["participants"]
        
        # All existing should still be there
        for participant in existing:
            assert participant in updated
        
        # New one should be added
        assert email in updated
