import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from src.services.llm_orchestrator import analyze_and_summarize_news

def test_analyze_and_summarize_news_empty_input():
    """Asserts fallback configuration structure when clean text matrices are dropped."""
    result = analyze_and_summarize_news("AAPL", "Stocks", [])
    assert isinstance(result, dict)
    assert "summary" in result
    assert result["composite_score"] == 0.0

@patch('src.services.llm_orchestrator.Groq')
def test_analyze_and_summarize_news_success(mock_groq_cls):
    """Validates unified quant model parsing over mock dictionary return items."""
    # Build complete mock SDK interface structure matching the qwen parser engine
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    # Enforce realistic multi-task JSON serialization structure matching model definitions
    mock_message.content = """
    {
      "summary": "Tech sector performance tracks macro momentum targets securely.",
      "composite_score": 0.65,
      "label": "Bullish",
      "breakdown": [
        {"headline": "Tech Surge", "score": 0.65, "impact_weight": 0.8}
      ]
    }
    """
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_groq_cls.return_value = mock_client

    test_headlines = ["Tech Surge"]

    # Inject mock platform secrets parameter layers to bypass application errors
    with patch.dict(st.secrets, {"GROQ_API_KEY": "gsk_mock_production_token"}):
        result = analyze_and_summarize_news("AAPL", "Stocks", test_headlines)

    # Dictionary Analytical Validations
    assert isinstance(result, dict)
    assert result["label"] == "Bullish"
    assert result["composite_score"] == 0.65
    assert "summary" in result
    
    # Track complex downstream execution calls securely
    mock_client.chat.completions.create.assert_called_once()
    called_kwargs = mock_client.chat.completions.create.call_args[1]
    assert called_kwargs["model"] == "qwen/qwen3.8-27b"
    assert called_kwargs["response_format"] == {"type": "json_object"}

@patch('src.services.llm_orchestrator.Groq')
def test_analyze_and_summarize_news_api_failure(mock_groq_cls):
    """Asserts recovery pathways handle connection disruptions gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Quota Exceeded")
    mock_groq_cls.return_value = mock_client

    with patch.dict(st.secrets, {"GROQ_API_KEY": "gsk_mock_token"}):
        result = analyze_and_summarize_news("AAPL", "Stocks", ["Some News"])

    # Fallback Assertion Engine Check
    assert isinstance(result, dict)
    assert "Execution Fallback" in result["label"]
    assert result["composite_score"] == 0.00
