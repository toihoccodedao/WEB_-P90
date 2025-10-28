# Hướng Dẫn Debug Lỗi Lưu Dữ Liệu

## 🔍 Vấn Đề
Form hiển thị xác nhận thành công nhưng dữ liệu không lưu vào Google Sheets.

## ✅ Đã Sửa
1. **Thêm trường "Loại hình việc làm"** vào data mapping
2. **Thêm logging** để debug dễ hơn
3. **Sửa lỗi xử lý lỗi obstruction** trong exception

## 🔧 Cách Kiểm Tra

### 1. Kiểm tra biến môi trường GOOGLE_CREDS
```powershell
# Kiểm tra xem biến có tồn tại không
echo $env:GOOGLE_CREDS

# Nếu không có, set biến (đọc từ file credentials.json)
$credentialJson = Get-Content -Path "credentials.json" -Raw
$env:GOOGLE_CREDS = $credentialJson
```

### 2. Chạy ứng dụng và xem log
```powershell
cd WEB_-P90
python app.py
```

Khi submit form, log sẽ hiển thị:
- `📝 Received data:` - Dữ liệu nhận được từ form
- `📊 Appending row to sheet...` - Đang lưu vào Google Sheets
- `✅ Data saved successfully!` - Lưu thành công
- Hoặc `❌ Error:` - Có lỗi xảy ra

### 3. Kiểm tra Console của trình duyệt
Mở Developer Tools (F12) → Console tab
- Xem có lỗi JavaScript không
- Xem response từ server

### 4. Kiểm tra Network tab
Mở Developer Tools (F12) → Network tab
- Tìm request `/submit`
- Xem status code (200 = OK, 500 = Server error)
- Xem response body

## 🐛 Các Lỗi Thường Gặp

### Lỗi 1: "Environment variable GOOGLE_CREDS is missing"
**Nguyên nhân:** Chưa set biến môi trường
**Giải pháp:** Set biến như hướng dẫn ở trên

### Lỗi 2: "APIError: 401"
**Nguyên nhân:** Credentials không hợp lệ hoặc hết hạn
**Giải pháp:** Tạo lại credentials.json từ Google Cloud Console

### Lỗi 3: "APIError: 403"
**Nguyên nhân:** Service account không có quyền truy cập Google Sheet
**Giải pháp:** 
1. Mở Google Sheet
2. Click "Share"
3. Thêm email của service account (waż z pliku credentials.json)
4. Cấp quyền "Editor"

### Lỗi 4: "HTTP 500 Internal Server Error"
**Nguyên nhân:** Có lỗi trong code Python
**Giải pháp:** Xem log trong terminal để biết chi tiết lỗi

## 🧪 Test Nhanh
```powershell
# Test kết nối Google Sheets
cd WEB_-P90
python test_gspread.py
```

Nếu test thành công, sẽ hiển thị:
```
Spreadsheet title: [Tên Sheet]
Worksheets:
- Sheet1
```

## 📝 Note
- Đảm bảo file `credentials.json` trong cùng thư mục
- Đảm bảo Google Sheet ID đúng
- Kiểm tra quyền truy TED cập của service account

