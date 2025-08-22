import os
from datetime import datetime

USE_SERVICE_ACCOUNT = True if os.path.exists(os.path.join(os.getcwd(), 'service_account.json')) else False
SHEET_NAME = os.getenv('SHEET_NAME', 'FintechEscalations')
APPS_SCRIPT_WEBHOOK_URL = os.getenv('APPS_SCRIPT_WEBHOOK_URL', '').strip()

if USE_SERVICE_ACCOUNT:
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        first_row = sheet.row_values(1)
        if not first_row or first_row == []:
            sheet.append_row(['Timestamp', 'Name', 'Email', 'Question'])
    except Exception as e:
        print('Failed to initialize gspread:', e)
        USE_SERVICE_ACCOUNT = False

def log_escalation(question, name='Guest', email='N/A'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [timestamp, name, email, question]
    if USE_SERVICE_ACCOUNT:
        try:
            sheet.append_row(row)
            print('Logged escalation to Google Sheet (service account).')
            return True
        except Exception as e:
            print('Failed to append row via service account:', e)
    if APPS_SCRIPT_WEBHOOK_URL:
        try:
            import requests
            resp = requests.post(APPS_SCRIPT_WEBHOOK_URL, json={'timestamp': timestamp, 'name': name, 'email': email, 'question': question}, timeout=10)
            resp.raise_for_status()
            print('Logged escalation via Apps Script webhook.')
            return True
        except Exception as e:
            print('Failed to call Apps Script webhook:', e)
    try:
        with open('escalations.log', 'a', encoding='utf-8') as f:
            f.write('\t'.join(row) + '\n')
        print('Logged escalation to escalations.log locally.')
        return True
    except Exception as e:
        print('Failed to log escalation locally:', e)
        return False