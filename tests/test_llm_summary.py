import pytest
from unittest.mock import patch, MagicMock
from src.services.llm_orchestrator import summarize_news_with_groq

def test_summarize_news_with_groq_empty_input():
    # Act
    result = summarize_news_with_groq([], "mock_api_key_12345")
    # Assert
    assert result == "No headlines provided to summarize."

@patch('src.services.llm_orchestrator.Groq')
def test_summarize_news_with_groq_success(mock_groq_cls):
    # Arrange Mock Client structure mirroring Groq SDK hierarchy
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    mock_message.content = "  Market sentiment points to sustained high-volume consolidation.  "
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_groq_cls.return_value = mock_client

    test_headlines = ["Tesla shares drop 6%", "Nucor executive sells $3.4m stock"]

    # Act
    summary = summarize_news_with_groq(test_headlines, "gsk_valid_key_token")

    # Assert
    assert summary == "Market sentiment points to sustained high-volume consolidation."
    
    # Verify exact delivery arguments to parameters
    mock_client.chat.completions.create.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": "You are a financial analyst helper. Provide clear, objective, bulleted investor summaries based solely on the provided headlines."
            },
            {
                "role": "user", 
                "content": "Summarize the following recent news headlines for investors:\n\n- Tesla shares drop 6%\n- Nucor executive sells $3.4m stock"
            }
        ],
        temperature=0.3,
        max_tokens=512
    )

@patch('src.services.llm_orchestrator.Groq')
def test_summarize_news_with_groq_api_failure(mock_groq_cls):
    # Arrange client execution runtime to blow up (Simulating network outage / expired tokens)
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Unauthorized API Token String Provided")
    mock_groq_cls.return_value = mock_client

    # Act & Assert
    with pytest.raises(RuntimeError, match="AI Synthesis pipeline failed: Unauthorized API Token String Provided"):
        summarize_news_with_groq(["Some news"], "gsk_expired_key")
