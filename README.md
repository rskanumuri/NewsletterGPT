# NewsletterGPT

AI-powered newsletter summarizer that reads your newsletters and sends concise summaries.

## Setup Guide

### Prerequisites
- Python 3.8+
- Gmail account
- OpenAI account or HuggingFace account
- Google Cloud account

### NOTE:
The HuggingFace Serverless Inference API has a free tier, but the OpenAI API does not.

### Step 1: Clone Repository
```bash
git clone https://github.com/sb529/NewsletterGPT.git
cd NewsletterGPT
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
   - Click top bar dropdown → "New Project"
   - Name: "Newsletter Summarizer"
   - Click "Create"

3. Enable Gmail API
   - Search "Gmail API" in top search bar
   - Click "Enable API"

4. Create OAuth Credentials
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Configure consent screen:
     - User Type: External
     - App name: "Newsletter Summarizer"
     - User support email: Your email
     - Developer contact: Your email
   - Add test users:
     - Your Gmail address
   - Create OAuth Client ID:
     - Application type: Desktop app
     - Name: "Newsletter Client"
   - Download JSON
   - Rename to `credentials.json`
   - Move to project folder

### Step 3a: OpenAI Setup
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create account/login
3. Click "API Keys" → "Create new secret key"
4. Copy key

### Step 3b: HuggingFace Setup
1. Visit [HuggingFace](https://huggingface.co)
2. Create account/login
3. Go to Access Tokens
4. Click "Create new token"
5. In User Permissions, select Inference->"Make calls to the serverless inference API"
6. Click "Create"
7. Copy key

### Step 4: Environment Setup
Create `.env` file:
```
TYPE=OPENAI or HUGGINGFACE
OPENAI_API_KEY=your-openai-key
INFERENCE_API_KEY=your-huggingface-key
SUMMARY_EMAIL=your-email@example.com
```

### Step 5: Configure Newsletters
Update `NEWSLETTER_SENDERS` in newsletter_processor.py:
```python
NEWSLETTER_SENDERS = [
    'newsletter1@example.com',
    'newsletter2@example.com'
]
```

### Step 6: Run
```bash
python newsletter_processor.py
```
First run opens browser for Gmail authorization.

## Troubleshooting

### Common Issues
1. "Access Blocked" error
   - Check OAuth consent screen setup
   - Verify you're logged into correct Google account

2. "API Key Invalid" error
   - Check OPENAI_API_KEY in .env
   - Verify key on OpenAI platform

3. No emails processed
   - Verify newsletter sender addresses
   - Check for unread emails


