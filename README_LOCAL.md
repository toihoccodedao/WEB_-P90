# Hướng Dẫn Chạy Local

## 🚀 Cách Chạy Ứng Dụng Local

### Bước 1: Cài đặt dependencies
```powershell
cd WEB_-P90
pip install -r requirements.txt
```

### Bước 2: Đảm bảo có file credentials.json
Đảm bảo file `credentials.json` (Google Service Account credentials) nằm trong thư mục `WEB_-P90`.

### Bước 3: Chạy ứng dụng
```powershell
python app.py
```

Server sẽ chạy tại: **http://localhost:5000**

### Bước 4: Test
1. Mở trình duyệt: http://localhost:5000
2. Điền form và submit
3. Kiểm tra terminal để xem log:
   - `📝 Received data:` - Dữ liệu nhận được
   - `✅ Data saved successfully!` - Lưu thành công
   - `❌ Error:` - Có lỗi (nếu có)

## 🔧 Code đã được cập nhật để:
1. ✅ **Tự động phát hiện môi trường chạy:**
   - Chạy **local**: Đọc từ file `credentials.json`
   - Chạy **Render**: Đọc từ biến môi trường `GOOGLE_CREDS`

2. ✅ **Thêm trường `employmentType`** vào data mapping

3. ✅ **Thêm logging chi tiết** để debug dễ hơn

4. ✅ **Cải thiện xử lý lỗi** với thông báo rõ ràng

## 📝 Lưu Ý

### Để chạy local:
- Không cần set biến môi trường `GOOGLE_CREDS`
- Chỉ cần file `credentials.json` trong thư mục

### Để deploy lên Render:
- Không cần file `credentials.json` (đã có trong .gitignore)
- Cần set biến môi trường `GOOGLE_CREDS` trong Render dashboard

## 🐛 Debug

Nếu gặp lỗi, kiểm tra:
1. File `credentials.json` có tồn tại không
2. Service account có quyền truy cập Google Sheet không
3. Xem log trong terminal để biết chi tiết lỗi

## 📊 Google Sheets
- Sheet ID: `14AWEbPdGMZElO-VBzW9N9MTlf0kZxtBNeBIbkxQsxQo`
- Tự động chèn header nếu sheet trống
- Dữ liệu sẽ được append vào cuối sheet

