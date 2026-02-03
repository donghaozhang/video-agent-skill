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


@pytest.fixture
def sample_portrait_data():
    """Sample portrait data for testing."""
    return {
        "character_name": "John",
        "front_view": "/path/to/john_front.png",
        "side_view": "/path/to/john_side.png",
        "back_view": "/path/to/john_back.png",
        "three_quarter_view": "/path/to/john_3q.png",
    }


@pytest.fixture
def sample_registry_data():
    """Sample portrait registry data for testing."""
    return {
        "project_id": "test_project",
        "portraits": {
            "John": {
                "character_name": "John",
                "front_view": "/path/to/john_front.png",
                "side_view": "/path/to/john_side.png",
            },
            "Mary": {
                "character_name": "Mary",
                "front_view": "/path/to/mary_front.png",
                "three_quarter_view": "/path/to/mary_3q.png",
            },
        },
    }


@pytest.fixture
def sample_shot_with_characters():
    """Sample shot with characters for reference testing."""
    return {
        "shot_id": "shot_001",
        "shot_type": "close_up",
        "camera_angle": "front",
        "description": "John looks at camera",
        "characters": ["John"],
        "duration_seconds": 5.0,
    }


@pytest.fixture
def mock_reference_generator():
    """Mock reference-based image generator."""
    mock = AsyncMock()
    mock.generate_with_reference.return_value = {
        "image_path": "/tmp/test_ref_image.png",
        "width": 1024,
        "height": 1024,
        "reference_used": True,
        "cost": 0.025,
    }
    return mock
