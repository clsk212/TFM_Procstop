import pytest
from unittest.mock import MagicMock
from app.chatbot import Chatbot
from bson.objectid import ObjectId

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.conversations.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    return db

@pytest.fixture
def mock_openai_client(mocker):
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response"
    mock_response.choices = [mock_choice]
    mock_client_instance.chat.completions.create.return_value = mock_response
    mocker.patch('app.chatbot.OpenAI', return_value=mock_client_instance)
    return mock_client_instance

def test_chatbot_initialization(mock_db, mock_openai_client):
    """
    Test that the Chatbot class initializes correctly.
    """
    api_key = "fake_api_key"
    bot = Chatbot(api_key=api_key, db=mock_db)
    assert bot.client is not None
    assert bot.db is not None
    assert bot.model == "gpt-4o-mini"
    assert bot.language == "ES"
    assert bot.gender == "Other"

def test_start_conver(mock_db, mock_openai_client):
    """
    Test the start_conver method.
    """
    api_key = "fake_api_key"
    bot = Chatbot(api_key=api_key, db=mock_db)
    bot.user_id = ObjectId()
    bot.start_conver()
    mock_db.conversations.insert_one.assert_called_once()
    assert bot.conversation_id is not None

def test_get_response(mock_db, mock_openai_client):
    """
    Test the get_response method.
    """
    api_key = "fake_api_key"
    bot = Chatbot(api_key=api_key, db=mock_db)
    bot.user_id = ObjectId()
    response = bot.get_response("Hello")
    assert response == "Test response"
    mock_openai_client.chat.completions.create.assert_called_once()
