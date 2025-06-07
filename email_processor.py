import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import ollama
from config import OLLAMA_MODEL

@dataclass
class ProcessedEmail:
    id: str
    subject: str
    sender: str
    date: str
    body: str
    summary: str
    category: str
    priority: str
    action_items: List[str]

class EmailProcessor:
    def __init__(self, model_name: str = OLLAMA_MODEL):
        """
        Initialize the email processor with Ollama.
        
        Args:
            model_name (str): Name of the Ollama model to use
        """
        self.model_name = model_name
        
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama to generate a response.
        
        Args:
            prompt (str): The prompt to send to the model
            
        Returns:
            str: The model's response
        """
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""

    def process_email(self, email: Dict) -> ProcessedEmail:
        """
        Process a single email using Ollama to generate summary, category, and other metadata.
        
        Args:
            email (Dict): The email to process
            
        Returns:
            ProcessedEmail: Processed email with additional metadata
        """
        # Create a prompt for the model
        prompt = f"""Please analyze this email and provide the following information in JSON format:
1. A brief summary (2-3 sentences)
2. Category (e.g., Work, Personal, Newsletter, Spam, Important, Urgent, etc.)
3. Priority (High, Medium, Low)
4. List of action items (if any)

Email details:
Subject: {email['subject']}
From: {email['sender']}
Date: {email['date']}
Body: {email['body']}

Please respond in the following JSON format:
{{
    "summary": "brief summary here",
    "category": "category here",
    "priority": "priority level here",
    "action_items": ["action item 1", "action item 2", ...]
}}"""

        # Get response from Ollama
        print(f"Calling Ollama with email: {email['subject']}")
        response = self._call_ollama(prompt)
        
        try:
            # Find the JSON object in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON object found", response, 0)
            
            email = ProcessedEmail(
                id=email['id'],
                subject=email['subject'],
                sender=email['sender'],
                date=email['date'],
                body=email['body'],
                summary=analysis.get('summary', ''),
                category=analysis.get('category', 'Uncategorized'),
                priority=analysis.get('priority', 'Medium'),
                action_items=analysis.get('action_items', [])
            )
            print_processed_email(email)
            return email
        except json.JSONDecodeError as e:
            print(f"Error processing email {email['id']}: {str(e)}")
            return ProcessedEmail(
                id=email['id'],
                subject=email['subject'],
                sender=email['sender'],
                date=email['date'],
                body=email['body'],
                summary="Error processing email",
                category="Error",
                priority="Medium",
                action_items=[]
            )

    def process_emails(self, emails: List[Dict]) -> List[ProcessedEmail]:
        """
        Process a list of emails.
        
        Args:
            emails (List[Dict]): List of emails to process
            
        Returns:
            List[ProcessedEmail]: List of processed emails
        """
        return [self.process_email(email) for email in emails]

def print_processed_email(email: ProcessedEmail):
    """Print a processed email in a readable format."""
    print(f"\nSubject: {email.subject}")
    print(f"From: {email.sender}")
    print(f"Date: {email.date}")
    print(f"Category: {email.category}")
    print(f"Priority: {email.priority}")
    print(f"\nSummary: {email.summary}")
    if email.action_items:
        print("\nAction Items:")
        for item in email.action_items:
            print(f"- {item}")
    print("-" * 50)

if __name__ == "__main__":
    from gmail_reader import GmailReader
    from config import DEFAULT_DAYS_TO_FETCH
    
    # Example usage
    reader = GmailReader()
    processor = EmailProcessor()
    
    # Get unread emails from the last day
    print(f"Getting unread emails from the last {DEFAULT_DAYS_TO_FETCH} days")
    unread_emails = reader.get_unread_emails(days=DEFAULT_DAYS_TO_FETCH)
    
    # Process the emails
    print(f"Processing {len(unread_emails)} emails")
    processed_emails = processor.process_emails(unread_emails)
    
    # # Print the results
    # for email in processed_emails:
    #     print_processed_email(email) 