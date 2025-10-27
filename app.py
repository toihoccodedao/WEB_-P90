from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import traceback
import os
import json


app = Flask(__name__)

# -----------------------------
# KẾT NỐI GOOGLE SHEETS
# -----------------------------
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Lấy credentials từ biến môi trường thay vì file
creds_json = json.loads(os.environ["GCP_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)

# Lấy JSON credentials từ biến môi trường GOOGLE_CREDS
# creds_json = os.environ.get("GOOGLE_CREDS")

# if creds_json:
#     creds_dict = json.loads(creds_json)
#     credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
# else:
#     raise Exception("⚠️ Environment variable GOOGLE_CREDS is missing!")

# client = gspread.authorize(credentials)

# ID của Google Sheet
SPREADSHEET_ID = '14AWEbPdGMZElO-VBzW9N9MTlf0kZxtBNeBIbkxQsxQo'

# Header cột
HEADERS = [
    'Họ tên', 'Ngày sinh', 'Giới tính', 'Số CCCD', 'Số BHXH', 'Số BHYT',
    'Nơi đăng ký thường trú', 'Nơi ở hiện tại', 'Đối tượng ưu tiên', 'Trình độ phổ thông',
    'Trình độ chuyên môn kỹ thuật', 'Chuyên ngành đào tạo', 'Tình trạng hoạt động kinh tế',
    'Lý do không tham gia HĐKT', 'Vị trí việc làm', 'Nghề nghiệp cụ thể',
    'Tham gia BHXH', 'Loại BHXH', 'Có hợp đồng lao động', 'Loại hợp đồng lao động',
    'Ngày bắt đầu làm việc', 'Nơi làm việc', 'Loại hình DN', 'Địa chỉ nơi làm việc',
    'Tình trạng thất nghiệp', 'Thời gian thất nghiệp'
]

# -----------------------------
# HÀM HỖ TRỢ
# -----------------------------
def ensure_headers(sheet):
    """Đảm bảo rằng dòng đầu tiên của sheet có header."""
    try:
        first_row = sheet.row_values(1)
        if not first_row or all(not c.strip() for c in first_row):
            sheet.insert_row(HEADERS, index=1)
            app.logger.info('✅ Đã chèn tiêu đề cột vào Google Sheet')
    except Exception as e:
        app.logger.warning(f'⚠️ Không thể kiểm tra header: {e}')

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
            safe(data, 'jobStatus'),
            safe(data, 'currentJob'),
            safe(data, 'insurance'),
            insurance_out,
            safe(data, 'contract'),
            contract_type,
            safe(data, 'contractDate'),
            safe(data, 'workplace'),
            safe(data, 'enterpriseType'),
            safe(data, 'workplaceAddress'),
            safe(data, 'unemploymentStatus'),
            safe(data, 'unemploymentDuration'),
        ]

        sheet.append_row(row, value_input_option='USER_ENTERED')
        return jsonify({'success': True})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})
