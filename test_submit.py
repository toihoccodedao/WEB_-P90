"""Test script để kiểm tra việc submit dữ liệu"""

import requests
import json

# Dữ liệu test
test_data = {
    "fullName": "Test User",
    "birthDate": "1990-01-01",
    "gender": "Nam",
    "idNumber": "123456789012",
    "bhxh": "",
    "bhyt": "",
    "address": "Test Address",
    "currentAddress": "",
    "priority": [],
    "ethnicity": "",
    "education": "Tốt nghiệp THPT",
    "specialization": "Chưa qua đào tạo",
    "major": "",
    "employmentStatus": "Người có việc làm",
    "employmentType": "Tự làm",
    "jobStatus": "Làm công ăn lương",
    "currentJob": "Test Job",
    "insurance": "Có",
    "insuranceType": "Bắt buộc",
    "contract": "Có",
    "contractType": "HĐLĐ xác định thời hạn",
    "contractDate": "2024-01-01",
    "workplace": "Doanh nghiệp",
    "enterpriseType": "DN ngoài Nhà nước / DN FDI",
    "workplaceAddress": "Test Workplace",
    "unemploymentStatus": "",
    "unemploymentDuration": ""
}

print("Testing submit to local server...")
print("=" * 50)

try:
    response = requests.post(
        'http://localhost:5000/submit',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("=" * 50)
    
except Exception as e:
    print(f"Error: {e}")

