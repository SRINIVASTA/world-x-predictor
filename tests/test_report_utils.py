import os
import pytest
from unittest.mock import patch, MagicMock
from src.utils.report_utils import generate_dashboard_pdf, send_bulk_report_emails

# =====================================================================
# 1️⃣ MODULE A TEST: PDF COMPILATION ASSERTS
# =====================================================================
@patch('src.utils.report_utils.HTML')
def test_generate_dashboard_pdf_success(mock_html_cls):
    """Verifies that the PDF generator processes string templates and outputs a target file path."""
    # Arrange
    mock_html_instance = MagicMock()
    mock_html_cls.return_value = mock_html_instance
    
    test_output_path = "test_market_snapshot.pdf"
    test_headlines = [
        {"title": "Global Markets Rise Amid Tech Surge", "date": "Nov 07, 2026"},
        {"title": "Crude Oil Consolidates Below Resistance", "date": "Nov 06, 2026"}
    ]

    # Act
    result_path = generate_dashboard_pdf(
        ticker="AAPL",
        company="Apple Inc.",
        current_p="$180.50",
        predicted_p="$185.20",
        bound_low="$182.00",
        bound_high="$188.00",
        sentiment_lbl="Positive Bullish",
        sentiment_scr=0.45,
        summary_text="Sustained consolidation looking for near-term breakouts.",
        headlines=test_headlines,
        output_path=test_output_path
    )

    # Assert
    assert result_path == test_output_path
    mock_html_cls.assert_called_once()
    mock_html_instance.write_pdf.assert_called_once_with(test_output_path)


# =====================================================================
# 2️⃣ MODULE B TESTS: BULK EMAIL SMTP LOOPS
# =====================================================================
@patch('src.utils.report_utils.smtplib.SMTP')
def test_send_bulk_report_emails_success(mock_smtp_cls):
    """Validates successful secure bulk email dispatch execution paths over fake loops."""
    # Arrange
    mock_server_instance = MagicMock()
    mock_smtp_cls.return_value = mock_server_instance
    
    test_sender = "automation@worldx.com"
    test_pass = "mock_app_password"
    test_recipients = "user1@domain.com, user2@gmail.com, user3@yahoo.com"
    test_subject = "Test Analytics Subject"
    test_body = "Hello, please review the attached document data profile."

    # Act
    total_dispatched = send_bulk_report_emails(
        email_sender=test_sender,
        app_password=test_pass,
        recipient_input=test_recipients,
        subject=test_subject,
        body=test_body,
        attachment_path=None
    )

    # Assert
    assert total_dispatched == 3  # Verified 3 unique clean strings parsed out
    mock_smtp_cls.assert_called_once_with('://gmail.com', 587)
    mock_server_instance.starttls.assert_called_once()
    mock_server_instance.login.assert_called_once_with(test_sender, test_pass)
    
    # Ensure sendmail execution array was invoked individually for each user to prevent header leakage
    assert mock_server_instance.sendmail.call_count == 3
    mock_server_instance.quit.assert_called_once()


def test_send_bulk_report_emails_empty_recipient_exception():
    """Asserts that a descriptive ValueError is thrown if input strings resolve into an empty space array."""
    with pytest.raises(ValueError, match="Please provide at least one valid recipient address destination."):
        send_bulk_report_emails(
            email_sender="sender@test.com",
            app_password="pass",
            recipient_input=" , ,,  ",
            subject="Subj",
            body="Body"
        )
