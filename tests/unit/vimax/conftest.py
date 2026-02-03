"""
Pytest fixtures for ViMax tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }


@pytest.fixture
def mock_image_generator():
    """Mock image generator."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "image_path": "/tmp/test_image.png",
        "width": 1024,
        "height": 1024,
    }
    return mock


@pytest.fixture
def mock_video_generator():
    """Mock video generator."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "video_path": "/tmp/test_video.mp4",
        "duration": 5.0,
    }
    return mock


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "name": "John",
        "description": "A young warrior",
        "age": "25",
        "gender": "male",
        "appearance": "Tall with dark hair",
        "personality": "Brave and determined",
    }


@pytest.fixture
def sample_shot_data():
    """Sample shot data for testing."""
    return {
        "shot_id": "shot_001",
        "shot_type": "medium",
        "description": "Hero standing at crossroads",
        "duration_seconds": 5.0,
    }
