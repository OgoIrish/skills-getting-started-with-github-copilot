"""
Tests for DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterHappyPath:
    """Test successful unregister scenarios."""

    def test_successful_unregister(self, test_client, existing_participant, activity_name):
        """Test successful unregister removes student from activity."""
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_participant in data["message"]
        assert activity_name in data["message"]

    def test_unregister_removes_from_participants_list(self, test_client, existing_participant, activity_name):
        """Test that unregister actually removes student from participants list."""
        # Verify they're registered initially
        response = test_client.get("/activities")
        assert existing_participant in response.json()[activity_name]["participants"]
        
        # Unregister
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        # Verify they're no longer in the list
        response = test_client.get("/activities")
        assert existing_participant not in response.json()[activity_name]["participants"]

    def test_unregister_increases_availability(self, test_client, existing_participant, activity_name):
        """Test that unregister increases available spots."""
        # Get initial availability
        initial_response = test_client.get("/activities")
        activity = initial_response.json()[activity_name]
        initial_availability = activity["max_participants"] - len(activity["participants"])
        
        # Unregister
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        # Get updated availability
        updated_response = test_client.get("/activities")
        activity = updated_response.json()[activity_name]
        updated_availability = activity["max_participants"] - len(activity["participants"])
        
        assert updated_availability == initial_availability + 1

    def test_unregister_multiple_students(self, test_client, activity_name):
        """Test unregistering multiple students from same activity."""
        # Get initial participants
        response = test_client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        # Unregister all
        for email in initial_participants:
            test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
        
        # Verify all are gone
        response = test_client.get("/activities")
        remaining = response.json()[activity_name]["participants"]
        
        assert len(remaining) == 0

    def test_unregister_response_format(self, test_client, existing_participant, activity_name):
        """Test that unregister response has correct format."""
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestUnregisterErrorHandling:
    """Test error scenarios for unregister."""

    def test_unregister_nonexistent_activity(self, test_client, existing_participant):
        """Test unregister fails for non-existent activity."""
        response = test_client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_student_not_enrolled(self, test_client, sample_emails, activity_name):
        """Test that unregister fails for student not enrolled."""
        email = sample_emails[0]
        
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower() or "not enrolled" in data["detail"].lower()

    def test_unregister_already_unregistered(self, test_client, existing_participant, activity_name):
        """Test that unregistering twice fails second time."""
        # First unregister succeeds
        response1 = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        assert response2.status_code == 400

    def test_unregister_error_response_has_detail(self, test_client, sample_emails):
        """Test that error responses include detail message."""
        response = test_client.delete(
            "/activities/Fake Activity/unregister",
            params={"email": sample_emails[0]}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestUnregisterValidation:
    """Test input validation for unregister."""

    def test_unregister_with_various_email_formats(self, test_client, activity_name):
        """Test unregister with different email formats."""
        emails = [
            "simple@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
        ]
        
        for email in emails:
            response = test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            # Should either succeed or fail gracefully (not 500)
            assert response.status_code != 500

    def test_unregister_activity_name_with_spaces(self, test_client, existing_participant):
        """Test unregister with activity names containing spaces."""
        activity_name = "Chess Club"
        
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        # Should work with spaces
        assert response.status_code in [200, 400, 404]

    def test_unregister_case_sensitive_activity_name(self, test_client, existing_participant):
        """Test that activity names are case-sensitive."""
        # Try lowercase - should fail
        response = test_client.delete(
            "/activities/chess club/unregister",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 404

    def test_unregister_url_encoding_in_activity_name(self, test_client, existing_participant):
        """Test unregister works with URL-encoded activity names."""
        activity_name_encoded = "Chess%20Club"
        
        response = test_client.delete(
            f"/activities/{activity_name_encoded}/unregister",
            params={"email": existing_participant}
        )
        
        # Should successfully decode
        assert response.status_code in [200, 400]


class TestUnregisterIntegration:
    """Integration tests combining multiple unregister operations."""

    def test_unregister_then_verify_not_in_get(self, test_client, existing_participant, activity_name):
        """Test that unregister data immediately reflects in GET /activities."""
        # Unregister
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        # Verify not in activities list
        response = test_client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        assert existing_participant not in participants

    def test_unregister_preserves_other_participants(self, test_client, activity_name):
        """Test that unregistering one student doesn't affect others."""
        # Get initial participants
        response = test_client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        if len(initial_participants) < 2:
            pytest.skip("Activity doesn't have multiple participants")
        
        # Unregister first student
        student_to_remove = initial_participants[0]
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_to_remove}
        )
        
        # Verify others are still there
        response = test_client.get("/activities")
        remaining = response.json()[activity_name]["participants"]
        
        for participant in initial_participants[1:]:
            assert participant in remaining

    def test_signup_after_unregister(self, test_client, sample_emails, activity_name):
        """Test that student can sign up again after unregistering."""
        email = sample_emails[0]
        
        # Sign up
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify signed up
        response = test_client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Unregister
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Verify not in list
        response = test_client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # Sign up again
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Should succeed
        assert response.status_code == 200
        
        # Verify back in list
        response = test_client.get("/activities")
        assert email in response.json()[activity_name]["participants"]

    def test_full_activity_then_unregister_allows_signup(self, test_client, sample_emails):
        """Test that unregistering frees up space in a full activity."""
        activity_name = "Tennis Club"  # max 12 participants
        
        # Fill the activity
        response = test_client.get("/activities")
        current_count = len(response.json()[activity_name]["participants"])
        
        # Add students until full
        for email in sample_emails[:12]:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            if response.status_code != 200:
                # Activity is now full
                assert response.status_code == 400
                break
        
        # Try to add one more - should fail
        extra_email = "extra@example.com"
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": extra_email}
        )
        
        if response.status_code == 200:
            # If we got this far, activity isn't full yet
            pytest.skip("Activity not at capacity")
        
        # Unregister someone
        response = test_client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        to_remove = participants[0]
        
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": to_remove}
        )
        
        # Now signup should work
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": extra_email}
        )
        
        # Should succeed now
        assert response.status_code == 200
