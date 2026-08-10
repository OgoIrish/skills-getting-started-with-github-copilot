"""
Pytest configuration and shared fixtures for FastAPI testing.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_client():
    """Provide a TestClient for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    # Store original activities
    original = {
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
            "description": "Join our competitive basketball team and compete in tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop your tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["james@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills through competitive debate",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific discoveries",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    
    # Restore original state
    activities.update(original)
    
    yield
    
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(original)


@pytest.fixture
def sample_activity():
    """Provide a sample activity dict for testing."""
    return {
        "description": "Test activity",
        "schedule": "Mondays, 5:00 PM - 6:00 PM",
        "max_participants": 5,
        "participants": ["test1@example.com", "test2@example.com"]
    }


@pytest.fixture
def sample_emails():
    """Provide a list of valid test email addresses."""
    return [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
        "student4@mergington.edu",
        "student5@mergington.edu",
    ]


@pytest.fixture
def existing_participant():
    """Provide an email that's already signed up for an activity."""
    return "michael@mergington.edu"  # Signed up for Chess Club


@pytest.fixture
def activity_name():
    """Provide a valid activity name."""
    return "Chess Club"
