from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import traceback
import os, json

app = Flask(__name__)

# --------------------------------------
# KẾT NỐI GOOGLE SHEETS
# --------------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

try:
    # ✅ Lấy credentials từ biến môi trường
    creds_json = json.loads(os.environ["GCP_CREDENTIALS"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(credentials)
    print("✅ Đã kết nối Google Sheets thành công.")
except Exception as e:
    print("❌ Lỗi khi khởi tạo client Google Sheets:", e)
    client = None  # để tránh lỗi name 'client' is not defined

# ID Google Sheet của bạn
SPREADSHEET_ID = "14AWEbPdGMZElO-VBzW9N9MTlf0kZxtBNeBIbkxQsxQo"

HEADERS = [
    'Họ tên', 'Ngày sinh', 'Giới tính', 'Số CCCD', 'Số BHXH', 'Số BHYT',
    'Nơi đăng ký thường trú', 'Nơi ở hiện tại', 'Đối tượng ưu tiên',
    'Trình độ phổ thông', 'Trình độ chuyên môn kỹ thuật', 'Chuyên ngành đào tạo',
    'Tình trạng hoạt động kinh tế', 'Lý do không tham gia HĐKT', 'Vị trí việc làm',
    'Nghề nghiệp cụ thể', 'Tham gia BHXH', 'Loại BHXH', 'Có hợp đồng lao động',
    'Loại hợp đồng lao động', 'Ngày bắt đầu làm việc', 'Nơi làm việc',
    'Loại hình DN', 'Địa chỉ nơi làm việc', 'Tình trạng thất nghiệp',
    'Thời gian thất nghiệp'
]

def ensure_headers(sheet):
    """Đảm bảo hàng đầu tiên là header."""
    try:
        first_row = sheet.row_values(1)
        if not first_row or all(not c.strip() for c in first_row):
            sheet.insert_row(HEADERS, index=1)
            app.logger.info('✅ Đã thêm header vào Google Sheet.')
    except Exception as e:
        app.logger.warning(f'⚠️ Không thể kiểm tra header: {e}')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if client is None:
        return jsonify({'success': False, 'error': 'Google Sheets client chưa được khởi tạo'})

    try:
        data = request.get_json()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        ensure_headers(sheet)

        def safe(k): return data.get(k, '')

        priorities = data.get('priority') or []
        if isinstance(priorities, str):
            priorities = [priorities]
        priority_str = ', '.join(priorities)
        ethnicity = safe('ethnicity')
        if ethnicity:
            if priority_str:
                priority_str = f"{priority_str}; Dân tộc: {ethnicity}"
            else:
                priority_str = f"Dân tộc: {ethnicity}"

        insurance = safe('insurance')
        insurance_out = ''
        if insurance:
            insurance_out = insurance
            ins_type = safe('insuranceType')
            if ins_type:
                insurance_out = f"{insurance_out} ({ins_type})"

        contract = safe('contract')
        contract_type = ''
        if contract == 'Có':
            contract_type = safe('contractType') or 'Có'

        inactive_reason = ''
        if safe('employmentStatus') == 'Không tham gia hoạt động kinh tế':
            inactive_reason = safe('inactiveReason')

        row = [
            safe('fullName'),
            safe('birthDate'),
            safe('gender'),
            safe('idNumber'),
            safe('bhxh'),
            safe('bhyt'),
            safe('address'),
            safe('currentAddress'),
            priority_str,
            safe('education'),
            safe('specialization'),
            safe('major'),
            safe('employmentStatus'),
            inactive_reason,
            safe('jobStatus'),
            safe('currentJob'),
            safe('insurance'),
            insurance_out,
            safe('contract'),
            contract_type,
            safe('contractDate'),
            safe('workplace'),
            safe('enterpriseType'),
            safe('workplaceAddress'),
            safe('unemploymentStatus'),
            safe('unemploymentDuration'),
        ]

        sheet.append_row(row, value_input_option='USER_ENTERED')
        return jsonify({'success': True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

