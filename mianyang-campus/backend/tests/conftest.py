import os
import pytest
from unittest.mock import MagicMock, patch

from app.models.user import UserRole

os.environ.setdefault("TESTING", "1")


@pytest.fixture(autouse=True)
def mock_db_settings():
    """Prevent real database calls in LLM config (handled gracefully by _get_db_settings try/except)"""
    with patch('app.services.llm_service._get_db_settings', return_value={}):
        yield


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Mock OpenAI client to prevent real API calls"""
    with patch('app.services.llm_service._get_client') as mock_get_client:
        client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "测试回复"
        mock_message.tool_calls = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = client
        yield client


@pytest.fixture
def mock_user():
    """Create a mock student user"""
    user = MagicMock()
    user.id = 1
    user.username = "test_student"
    user.name = "测试学生"
    user.role = UserRole.STUDENT
    user.college = "计算机学院"
    user.avatar = None
    user.skills_json = {"skills": [], "interests": []}
    return user


@pytest.fixture
def mock_teacher():
    """Create a mock teacher user"""
    user = MagicMock()
    user.id = 10
    user.username = "test_teacher"
    user.name = "测试教师"
    user.role = UserRole.TEACHER
    user.college = "计算机学院"
    user.avatar = None
    user.skills_json = None
    return user


@pytest.fixture
def mock_profile():
    """Create a mock student profile snapshot"""
    profile = MagicMock()
    profile.academic_score = 50.0
    profile.psychological_risk = 30.0
    profile.engagement_score = 50.0
    profile.growth_score = 50.0
    profile.overall_risk = 20.0
    return profile
