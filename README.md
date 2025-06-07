# Gmail Unread Email Reader

A Python application that fetches unread emails from Gmail and processes them using Ollama for summarization and categorization.

## Features

- Fetch unread emails from Gmail with configurable date ranges
- Automatic OAuth2 authentication
- Process emails using Ollama to:
  - Generate brief summaries
  - Categorize emails (Work, Personal, Newsletter, etc.)
  - Assign priority levels
  - Extract action items
- Uses Ollama for email analysis (model configurable in `config.py`)
- Handles base64 encoded email bodies

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Cloud Project and enable Gmail API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API for your project
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save them as `credentials.json` in the project directory

3. Install and run Ollama:
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull the model specified in `config.py`:
     ```bash
     ollama pull $(grep OLLAMA_MODEL config.py | cut -d'"' -f2)
     ```
   - Make sure Ollama is running (default: http://localhost:11434)

## Configuration

Edit `config.py` to customize settings:
```python
# Ollama model settings
OLLAMA_MODEL = "gemma3:4b"  # Change this to use a different model

# Email processing settings
DEFAULT_DAYS_TO_FETCH = 1
```

## Usage

```python
from gmail_reader import GmailReader
from email_processor import EmailProcessor

# Initialize the readers
reader = GmailReader()
processor = EmailProcessor()

# Get unread emails from the last day
unread_emails = reader.get_unread_emails(days=1)

# Process the emails
processed_emails = processor.process_emails(unread_emails)
```

## Output Format

Each processed email includes:
- Subject
- Sender
- Date
- Category
- Priority
- Summary
- Action items (if any)

Example output:
```
Subject: Order Shipped - YoYoExpert.com
From: orders@yoyoexpert.com
Date: 2024-03-20 10:30:00
Category: Work
Priority: Medium

Summary: This email is an automated notification from YoYoExpert.com informing the recipient that their order (a JUGEMU '24 - Raw yo-yo) has shipped via USPS Ground Advantage. The email provides tracking information and a list of items included in the order.

Action Items:
- Track the shipment using the provided USPS tracking number: 9400XXXXXX1234567890
- Review the order details to ensure accuracy.
--------------------------------------------------
```

## Note

The first time you run the script, it will open a browser window for OAuth2 authentication. After successful authentication, the credentials will be saved in `token.pickle` for future use.