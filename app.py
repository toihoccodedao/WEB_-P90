from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import traceback
import os
import json


app = Flask(__name__)

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# KẾT NỐI GOOGLE SHEETS
# -----------------------------
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Ưu tiên đọc từ file credentials.json (cho local)
# Nếu không có file, đọc từ biến môi trường GOOGLE_CREDS (cho Render)
if os.path.exists('credentials.json'):
    # Chạy local: đọc từ file
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    print('[SUCCESS] Loaded credentials from credentials.json')
else:
    # Chạy trên cloud (Render): đọc từ biến môi trường
    creds_json = os.environ.get("GOOGLE_CREDS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        print('[SUCCESS] Loaded credentials from environment variable')
    else:
        raise Exception("Khong tim thay credentials.json va bien moi truong GOOGLE_CREDS!")

client = gspread.authorize(credentials)
print('[SUCCESS] Google Sheets client authorized')

# ID của Google Sheet
SPREADSHEET_ID = '14AWEbPdGMZElO-VBzW9N9MTlf0kZxtBNeBIbkxQsxQo'

# Header cột
HEADERS = [
    'Họ tên', 'Ngày sinh', 'Giới tính', 'Số CCCD', 'Số BHXH', 'Số BHYT',
    'Nơi đăng ký thường trú', 'Nơi ở hiện tại', 'Đối tượng ưu tiên', 'Trình độ phổ thông',
    'Trình độ chuyên môn kỹ thuật', 'Chuyên ngành đào tạo', 'Tình trạng hoạt động kinh tế',
    'Lý do không tham gia hoạt động kinh tế', 'Vị trí việc làm', 'Nghề nghiệp cụ thể',
    'Tham gia BHXH', 'Loại BHXH', 'Có hợp đồng lao động', 'Loại hợp đồng lao động',
    'Ngày bắt đầu làm việc', 'Nơi làm việc', 'Loại hình DN', 'Địa chỉ nơi làm việc',
    'Tình trạng thất nghiệp', 'Thời gian thất nghiệp'
]

# -----------------------------
# HÀM HỖ TRỢ
# -----------------------------
def ensure_headers(sheet):
    """Cập nhật header trong Google Sheet."""
    try:
        # Cập nhật header row 1
        header_range = sheet.range(1, 1, 1, len(HEADERS))
        for i, cell in enumerate(header_range):
            cell.value = HEADERS[i]
        sheet.update_cells(header_range)
        print(f'[INFO] Updated {len(HEADERS)} headers in Google Sheet')
    except Exception as e:
        print(f'[WARNING] Khong the cap nhat header: {e}')

def safe(data, key):
    return data.get(key, '').strip()

# -----------------------------
# ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        
        # Log dữ liệu nhận được để debug
        print('=' * 50)
        print('[INFO] RECEIVED DATA:')
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print('=' * 50)

        # Mở Google Sheet
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        ensure_headers(sheet)

        # Xử lý đối tượng ưu tiên
        priorities = data.get('priority') or []
        if isinstance(priorities, str):
            priorities = [priorities]
        priority_str = ', '.join(priorities)
        ethnicity = safe(data, 'ethnicity')
        if ethnicity:
            if priority_str:
                priority_str = f"{priority_str}; Dân tộc: {ethnicity}"
            else:
                priority_str = f"Dân tộc: {ethnicity}"

        # Thông tin BHXH
        insurance = safe(data, 'insurance')
        insurance_out = ''
        if insurance:
            insurance_out = insurance
            ins_type = safe(data, 'insuranceType')
            if ins_type:
                insurance_out = f"{insurance_out} ({ins_type})"

        # Loại hợp đồng
        contract = safe(data, 'contract')
        contract_type = ''
        if contract == 'Có':
            contract_type = safe(data, 'contractType') or 'Có'

        # Lý do không tham gia hoạt động kinh tế
        inactive_reason = ''
        if safe(data, 'employmentStatus') == 'Không tham gia hoạt động kinh tế':
            inactive_reason = safe(data, 'inactiveReason')

        # Vị trí việc làm (combine employmentType và jobStatus)
        job_position = safe(data, 'employmentType') or safe(data, 'jobStatus')

        # Dòng dữ liệu theo đúng thứ tự
        row = [
            safe(data, 'fullName'),
            safe(data, 'birthDate'),
            safe(data, 'gender'),
            safe(data, 'idNumber'),
            safe(data, 'bhxh'),
            safe(data, 'bhyt'),
            safe(data, 'address'),
            safe(data, 'currentAddress'),
            priority_str,
            safe(data, 'education'),
            safe(data, 'specialization'),
            safe(data, 'major'),
            safe(data, 'employmentStatus'),
            inactive_reason,
            job_position,  # Vị trí việc làm
            safe(data, 'currentJob'),  # Nghề nghiệp cụ thể
            insurance,  # Tham gia BHXH
            insurance_out,  # Loại BHXH
            contract,  # Có hợp đồng lao động
            contract_type,  # Loại hợp đồng lao động
            safe(data, 'contractDate'),  # Ngày bắt đầu làm việc
            safe(data, 'workplace'),  # Nơi làm việc (cột V)
            safe(data, 'enterpriseType'),  # Loại hình DN (cột W)
            safe(data, 'workplaceAddress'),  # Địa chỉ nơi làm việc (cột X)
            safe(data, 'unemploymentStatus'),  # Tình trạng thất nghiệp (cột Y)
            safe(data, 'unemploymentDuration')  # Thời gian thất nghiệp (cột Z)
        ]

        print('[INFO] NUMBER OF COLUMNS:', len(row))
        print('[INFO] ROW DATA:')
        for i, val in enumerate(row):
            print(f'  Column {i+1}: {val}')
        print('=' * 50)
        
        print('[INFO] Appending row to sheet...')
        sheet.append_row(row, value_input_option='USER_ENTERED')
        print('[SUCCESS] Data saved successfully!')
        return jsonify({'success': True, 'message': 'Dữ liệu đã được lưu thành công!'})

    except Exception as e:
        error_msg = str(e)
        print('=' * 50)
        print('[ERROR]:', error_msg)
        print('=' * 50)
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500


if __name__ == '__main__':
    # Chạy app ở chế độ debug khi chạy local
    app.run(debug=True, host='0.0.0.0', port=5000)
