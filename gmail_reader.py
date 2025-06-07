import os
import pickle
import base64
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailReader:
    def __init__(self, credentials_path: str = 'credentials.json'):
        """
        Initialize the Gmail reader.
        
        Args:
            credentials_path (str): Path to the credentials.json file from Google Cloud Console
        """
        self.credentials_path = credentials_path
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Get Gmail API service instance."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def _decode_base64(self, data: str) -> str:
        """
        Decode base64 encoded string.
        
        Args:
            data (str): Base64 encoded string
            
        Returns:
            str: Decoded string
        """
        if not data:
            return ''
        try:
            # Add padding if needed
            padding = 4 - (len(data) % 4)
            if padding != 4:
                data += '=' * padding
            return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            print(f"Error decoding base64: {e}")
            return ''

    def get_unread_emails(self, days: int = 1) -> List[Dict]:
        """
        Fetch unread emails from the specified number of days ago.
        
        Args:
            days (int): Number of days to look back for unread emails
            
        Returns:
            List[Dict]: List of unread emails with their details
        """
        # Calculate the date range using UTC time
        end_date = datetime.now(UTC) + timedelta(days=1)  # Add one day to include current day
        start_date = end_date - timedelta(days=days+1)
        
        # Format dates for Gmail query
        start_date_str = start_date.strftime('%Y/%m/%d')
        end_date_str = end_date.strftime('%Y/%m/%d')
        
        # Create query for unread emails within date range
        query = f'is:unread after:{start_date_str} before:{end_date_str}'
        
        try:
            # Get list of messages matching the query
            results = self.service.users().messages().list(
                userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full details for each message
            emails = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full').execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get message body
                body = ''
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = part['body'].get('data', '')
                            break
                elif 'body' in msg['payload']:
                    body = msg['payload']['body'].get('data', '')
                
                # Decode the body if it's not empty
                decoded_body = self._decode_base64(body)
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': decoded_body
                })
            
            return emails
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

if __name__ == '__main__':
    # Example usage
    reader = GmailReader()
    # Get unread emails from the last x days
    unread_emails = reader.get_unread_emails(days=1)
    for email in unread_emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Date: {email['date']}")
        print(f"Body: {email['body']}")
        print("-" * 50) 