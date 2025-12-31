"""
📧 Email Sender Module - وحدة إرسال البريد الإلكتروني
Handles sending reports via Gmail API
"""

import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64

from config import EMAIL_RECIPIENTS

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Initialize Gmail API service and handle token creation"""
    creds = None

    # ✅ Load existing credentials if available
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"⚠️ Error loading credentials: {e}")

    # ✅ If no valid creds, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("❌ credentials.json not found! Please add your Google OAuth file.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def create_message_with_attachment(sender, to, subject, message_text, file_path):
    """Create email message with attachment"""
    message = MIMEMultipart()
    message['to'] = ', '.join(to)
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='txt')
            attachment.add_header('Content-Disposition', 'attachment',
                                  filename=os.path.basename(file_path))
            message.attach(attachment)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_report_via_email(report_path):
    """
    Send the monthly report via email using Gmail API
    Args:
        report_path: Path to the report file
    """
    if not EMAIL_RECIPIENTS:
        print("📧 No email recipients configured in config.py")
        return

    print("\n📤 Preparing to send report via email...")
    print(f"📧 Recipients: {', '.join(EMAIL_RECIPIENTS)}")

    try:
        service = get_gmail_service()

        if not os.path.exists(report_path):
            print(f"❌ Report file not found: {report_path}")
            return

        email_msg = create_message_with_attachment(
            sender="me",
            to=EMAIL_RECIPIENTS,
            subject="Monthly Opportunities Report",
            message_text="Please find attached the monthly opportunities report.",
            file_path=report_path
        )

        service.users().messages().send(userId="me", body=email_msg).execute()
        print("✅ Report sent successfully via email!")

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("⚠️ Report would have been sent to:")
        print(f"   {', '.join(EMAIL_RECIPIENTS)}")


if __name__ == "__main__":
    test_file = "test_report.txt"
    with open(test_file, 'w') as f:
        f.write("Test report content")

    send_report_via_email(test_file)
    os.remove(test_file)
