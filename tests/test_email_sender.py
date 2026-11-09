import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from src.utils.email_sender import send_bulk_dashboard_emails

@pytest.fixture
def mock_smtp_setup():
    """Fixture to cleanly mock the smtplib.SMTP_SSL network layer."""
    with patch("src.utils.email_sender.smtplib.SMTP_SSL") as mock_smtp_class:
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server
        yield mock_server, mock_smtp_class


def test_send_bulk_emails_success_no_attachment(mock_smtp_setup):
    """Verifies successful multi-recipient processing without file attachments."""
    mock_server, _ = mock_smtp_setup
    
    # Inputs
    sender = "sender@gmail.com"
    pwd = "secret_app_password"
    recipients = "user1@test.com, user2@test.com , user3@test.com"
    subject = "WORLD-X Daily Briefing"
    body = "Here is your requested trading outlook analytics."
    
    # Execute loop
    count = send_bulk_dashboard_emails(sender, pwd, recipients, subject, body, attachment_path=None)
    
    # Assertions
    assert count == 3
    mock_server.login.assert_called_once_with(sender, pwd)
    assert mock_server.sendmail.call_count == 3
    mock_server.quit.assert_called_once()


def test_send_bulk_emails_with_valid_attachment(mock_smtp_setup):
    """Verifies that the file attachment is read and embedded properly when the path exists."""
    mock_server, _ = mock_smtp_setup
    
    sender = "sender@gmail.com"
    pwd = "app_pass"
    recipients = "single_user@test.com"
    subject = "Forecast PDF Report"
    body = "See attachment."
    fake_path = "/workspace/reports/market_report.pdf"
    fake_file_content = b"%PDF-1.4 simulated pdf vector streams data"
    
    # Mock both file validation and binary I/O operations simultaneously
    with patch("src.utils.email_sender.os.path.exists", return_value=True), \
         patch("src.utils.email_sender.open", mock_open(read_data=fake_file_content)) as mocked_file:
         
        count = send_bulk_dashboard_emails(sender, pwd, recipients, subject, body, attachment_path=fake_path)
        
        # Verify file properties were queried correctly
        assert count == 1
        mocked_file.assert_called_once_with(fake_path, "rb")
        mock_server.sendmail.assert_called_once()
        
        # Verify the target payload was processed
        called_args = mock_server.sendmail.call_args[0]
        assert called_args[0] == sender
        assert called_args[1] == "single_user@test.com"
        assert "Content-Disposition" in called_args[2]
        assert "filename=market_report.pdf" in called_args[2]


def test_send_bulk_emails_empty_recipient_raise_value_error(mock_smtp_setup):
    """Ensures input strings missing valid emails instantly drop out via a ValueError."""
    mock_server, _ = mock_smtp_setup
    
    with pytest.raises(ValueError, match="Please enter at least one recipient email address."):
        send_bulk_dashboard_emails(
            email_sender="sender@gmail.com",
            app_password="pwd",
            recipient_input="   , ,   ",  # Garbage layout string
            subject="Fail Test",
            body="Should fail fast"
        )
        
    # Ensure network pipelines were never provisioned
    mock_server.login.assert_not_called()


@patch("src.utils.email_sender.time.sleep")
def test_send_bulk_emails_anti_spam_delay(mock_sleep, mock_smtp_setup):
    """Verifies anti-spam pacing engine executes only when parsing multiple entries."""
    mock_server, _ = mock_smtp_setup
    
    # Case 1: Multiple recipients triggers sleep
    send_bulk_dashboard_emails("s@g.com", "p", "a@a.com, b@b.com", "Subj", "Body")
    assert mock_sleep.call_count == 1  # 2 recipients means 1 delay between them
    
    mock_sleep.reset_mock()
    
    # Case 2: Single recipient skips sleep cycle completely
    send_bulk_dashboard_emails("s@g.com", "p", "a@a.com", "Subj", "Body")
    mock_sleep.assert_not_called()
