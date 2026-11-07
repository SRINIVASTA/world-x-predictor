import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64

def send_bulk_dashboard_emails(email_sender, app_password, recipient_input, subject, body, attachment_path=None):
    """
    Exclusively handles parsing distinct list endpoints and executing secure delivery loops
    with attached multi-part documentation assets matching your functional pattern requirements.
    """
    # 1. Clean and convert the input string into a proper Python list matching your pattern
    recipient_list = [email.strip() for email in recipient_input.split(",") if email.strip()]

    if not recipient_list:
        raise ValueError("Please enter at least one recipient email address.")

    # 2. Connect securely to Gmail infrastructure
    server = smtplib.SMTP('://gmail.com', 587)
    server.starttls()
    server.login(email_sender, app_password)

    try:
        # 3. Loop through each recipient and send individually
        for receiver in recipient_list:
            # We use MIMEMultipart to support the file attachment correctly
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = receiver
            msg['Subject'] = subject
            
            # Attach the main message text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the snapshot file if provided and exists
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encode_base64(part)
                    part.add_header(
                        "Content-Disposition", 
                        f"attachment; filename={os.path.basename(attachment_path)}"
                    )
                    msg.attach(part)

            server.sendmail(email_sender, receiver, msg.as_string())
            
            # Anti-spam delay matching your original template layout logic
            if len(recipient_list) > 1:
                time.sleep(1)
                
    finally:
        server.quit()
        
    return len(recipient_list)
