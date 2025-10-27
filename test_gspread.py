import gspread
from oauth2client.service_account import ServiceAccountCredentials
import traceback

SPREADSHEET_ID = '14AWEbPdGMZElO-VBzW9N9MTlf0kZxtBNeBIbkxQsxQo'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SPREADSHEET_ID)
    print('Spreadsheet title:', sh.title)
    print('Worksheets:')
    for w in sh.worksheets():
        print('-', w.title)
except Exception as e:
    print('ERROR:', str(e))
    traceback.print_exc()
