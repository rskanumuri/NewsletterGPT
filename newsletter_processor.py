import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

load_dotenv()  # Load environment variables
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import base64
from email.mime.text import MIMEText
import openai
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
NEWSLETTER_SENDERS = [
'satish@influencewithoutauthoritycourse.com',
'producttalkdaily@substack.com',
'huryn@substack.com',
'<peteryang+product-track@substack.com',
'noreply@newsletter.skiplevel.co',
'runthebusiness@substack.com',
'hello@tryexponent.com',
'newsletters-noreply@linkedin.com',
'info@strategyn.com',
'teresa@producttalk.org',
'sc@productsthatcount.com',
'mail@digest.sharebird.com',
'lenny@substack.com',
'team@mindtheproduct.com',
'aakashgupta@substack.com',
'productmindset@substack.com',
'cutlefish@substack.com',
'eam@productalliance.com',
'newsletter@techtello.com',
'hello@mail1.reforge.com',
'lg@substack.com',
'annelaure@nesslabs.com',
'team@productcollective.com'
]

def get_gmail_service():
    creds = None
    # If token file exists, try to load credentials from it
    if os.path.exists('credentials.json'):
        try:
            creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
        except Exception:
            # If there's any error loading the token, set creds to None
            creds = None
    
    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # If refresh fails, force new OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new credentials
        with open('credentials.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_newsletter_emails(service, sender_email):
    query = f'from:{sender_email} is:unread'
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])
    return messages

def get_email_content(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body'].get('data', '')
    else:
        data = payload['body'].get('data', '')
    
    if data:
        text = base64.urlsafe_b64decode(data).decode()
        return text
    return ''

def summarize_with_gpt(content):
    # Truncate content to ~4000 chars to stay within limits
    truncated_content = content[:4000] + "..." if len(content) > 4000 else content
    
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following newsletter content in 2-3 concise bullet points."},
            {"role": "user", "content": truncated_content}
        ]
    )
    return completion.choices[0].message.content

def send_summary_email(service, summaries):
    date_str = datetime.now().strftime('%Y-%m-%d')
    email_content = f"Newsletter Summaries for {date_str}\n\n"
    
    for sender, summary in summaries.items():
        email_content += f"\nFrom {sender}:\n{summary}\n"
    
    message = MIMEText(email_content)
    message['to'] = os.getenv('SUMMARY_EMAIL')  # Your verified email
    message['subject'] = f'Newsletter Summaries - {date_str}'
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

def archive_email(service, msg_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={'removeLabelIds': ['UNREAD', 'INBOX']}
    ).execute()

def main():
    print("Starting newsletter processing...")
    
    # Get OpenAI API key from .env
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    print("Setting up Gmail service...")
    # Initialize Gmail service
    service = get_gmail_service()
    print("Gmail service initialized")
    
    summaries = {}
    
    # Process each newsletter
    for sender in NEWSLETTER_SENDERS:
        print(f"Checking emails from: {sender}")
        messages = get_newsletter_emails(service, sender)
        print(f"Found {len(messages)} unread messages")
        
        if messages:
            combined_content = ""
            for message in messages:
                content = get_email_content(service, message['id'])
                combined_content += content + "\n\n"
                archive_email(service, message['id'])
            
            if combined_content:
                summary = summarize_with_gpt(combined_content)
                summaries[sender] = summary
    
    # Send combined summary if we have any summaries
    if summaries:
        send_summary_email(service, summaries)

if __name__ == '__main__':
    main()