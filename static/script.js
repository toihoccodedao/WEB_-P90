// DOM Elements
const form = document.getElementById('laborForm');
const progressFill = document.getElementById('progressFill');
const successMessage = document.getElementById('successMessage');

// Xử lý hiển thị/ẩn các section dựa trên lựa chọn
document.querySelectorAll('input[name="employmentStatus"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.getElementById('employedSection').style.display = 
            this.value === 'Người có việc làm' ? 'block' : 'none';
        document.getElementById('unemployedSection').style.display = 
            this.value === 'Người thất nghiệp' ? 'block' : 'none';
        document.getElementById('inactiveReason').style.display = 
            this.value === 'Không tham gia hoạt động kinh tế' ? 'block' : 'none';
        
        updateProgress();
    });
});

// Xử lý hiển thị/ẩn loại bảo hiểm
document.querySelectorAll('input[name="insurance"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const insuranceTypeGroup = document.getElementById('insuranceTypeGroup');
        if (insuranceTypeGroup) {
            insuranceTypeGroup.style.display = this.value === 'Có' ? 'block' : 'none';
        }
    });
});

// Xử lý hiển thị/ẩn chi tiết hợp đồng
document.querySelectorAll('input[name="contract"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.getElementById('contractDetails').style.display = 
            this.value === 'Có' ? 'block' : 'none';
    });
});

// Xử lý hiển thị/ẩn loại doanh nghiệp
document.querySelectorAll('input[name="workplace"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const enterpriseTypeGroup = document.getElementById('enterpriseTypeGroup');
        if (enterpriseTypeGroup) {
            enterpriseTypeGroup.style.display = 
                this.value === 'Doanh nghiệp' ? 'block' : 'none';
        }
    });
});

// Tính toán progress bar
function updateProgress() {
    const requiredInputs = form.querySelectorAll('input[required]');
    let filledCount = 0;
    let totalRequired = 0;
    
    const processedGroups = new Set();
    
    requiredInputs.forEach(input => {
        if (input.type === 'radio') {
            const groupName = input.name;
            if (!processedGroups.has(groupName)) {
                processedGroups.add(groupName);
                totalRequired++;
                const isChecked = form.querySelector(`input[name="${groupName}"]:checked`);
                if (isChecked) filledCount++;
            }
        } else {
            totalRequired++;
            if (input.value.trim() !== '') filledCount++;
        }
    });
    
    const progress = totalRequired > 0 ? (filledCount / totalRequired) * 100 : 0;
    progressFill.style.width = progress + '%';
}

// Lắng nghe thay đổi trên tất cả input
form.addEventListener('input', updateProgress);
form.addEventListener('change', updateProgress);

// Xử lý submit form
document.getElementById('laborForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Hiển thị xác nhận trước khi lưu
    const confirmSave = confirm('Bạn chắc chắn muốn lưu thông tin này?');
    if (!confirmSave) {
        return; // Hủy submit nếu user không đồng ý
    }
    
    // Lấy tất cả dữ liệu từ form
    const formData = {
        fullName: document.getElementById('fullName')?.value,
        birthDate: document.getElementById('birthDate')?.value,
        gender: document.querySelector('input[name="gender"]:checked')?.value,
        idNumber: document.getElementById('idNumber')?.value,
        bhxh: document.getElementById('bhxh')?.value,
        bhyt: document.getElementById('bhyt')?.value,
        address: document.getElementById('address')?.value,
        currentAddress: document.getElementById('currentAddress')?.value,
        priority: Array.from(document.querySelectorAll('input[name="priority"]:checked')).map(cb => cb.value),
        ethnicity: document.getElementById('ethnicity')?.value,
        education: document.querySelector('input[name="education"]:checked')?.value,
        specialization: document.querySelector('input[name="specialization"]:checked')?.value,
        major: document.getElementById('major')?.value,
        employmentStatus: document.querySelector('input[name="employmentStatus"]:checked')?.value,
    };

    // Thêm dữ liệu cho người có việc làm
    if (formData.employmentStatus === 'Người có việc làm') {
        formData.employmentType = document.querySelector('input[name="employmentType"]:checked')?.value;
        formData.jobStatus = document.querySelector('input[name="jobStatus"]:checked')?.value;
        formData.currentJob = document.getElementById('currentJob')?.value;
        formData.insurance = document.querySelector('input[name="insurance"]:checked')?.value;
        if (formData.insurance === 'Có') {
            formData.insuranceType = document.querySelector('input[name="insuranceType"]:checked')?.value;
        }
        formData.contract = document.querySelector('input[name="contract"]:checked')?.value;
        if (formData.contract === 'Có') {
            formData.contractType = document.querySelector('input[name="contractType"]:checked')?.value;
            formData.contractDate = document.getElementById('contractDate')?.value;
        }
        formData.workplace = document.querySelector('input[name="workplace"]:checked')?.value;
        if (formData.workplace === 'Doanh nghiệp') {
            formData.enterpriseType = document.querySelector('input[name="enterpriseType"]:checked')?.value;
        }
        formData.workplaceAddress = document.getElementById('workplaceAddress')?.value;
    }

    // Thêm dữ liệu cho người thất nghiệp
    if (formData.employmentStatus === 'Người thất nghiệp') {
        formData.unemploymentStatus = document.querySelector('input[name="unemploymentStatus"]:checked')?.value;
        formData.unemploymentDuration = document.querySelector('input[name="unemploymentDuration"]:checked')?.value;
    }

    // Thêm lý do nếu không tham gia hoạt động kinh tế
    if (formData.employmentStatus === 'Không tham gia hoạt động kinh tế') {
        formData.inactiveReason = document.querySelector('input[name="inactiveReason"]:checked')?.value;
    }

    // Thêm loading state
    form.classList.add('loading');

    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        // Nếu server trả về mã lỗi HTTP
        if (!response.ok) {
            const text = await response.text();
            alert(`Có lỗi xảy ra (HTTP ${response.status}):\n${text}`);
            console.error('HTTP error', response.status, text);
            form.classList.remove('loading');
            return;
        }

        // Cố gắng parse JSON trả về
        let result = null;
        try {
            result = await response.json();
        } catch (parseErr) {
            const text = await response.text();
            alert('Có lỗi xảy ra: server trả về dữ liệu không phải JSON:\n' + text);
            console.error('JSON parse error:', parseErr, 'response text:', text);
            form.classList.remove('loading');
            return;
        }

        form.classList.remove('loading');

        if (result && result.success) {
            // Hiển thị thông báo thành công
            successMessage.classList.add('show');
            
            // Lưu vào localStorage
            localStorage.setItem('laborFormData', JSON.stringify(formData));
            localStorage.setItem('laborFormSubmitTime', new Date().toISOString());
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Reset form sau 2 giây
            setTimeout(() => {
                document.getElementById('laborForm').reset();
                // Ẩn các section
                document.getElementById('employedSection').style.display = 'none';
                document.getElementById('unemployedSection').style.display = 'none';
                document.getElementById('inactiveReason').style.display = 'none';
                document.getElementById('contractDetails').style.display = 'none';
                const insuranceTypeGroup = document.getElementById('insuranceTypeGroup');
                if (insuranceTypeGroup) insuranceTypeGroup.style.display = 'none';
                const enterpriseTypeGroup = document.getElementById('enterpriseTypeGroup');
                if (enterpriseTypeGroup) enterpriseTypeGroup.style.display = 'none';
                
                updateProgress();
            }, 2000);
            
            // Ẩn thông báo sau 5 giây
            setTimeout(() => {
                successMessage.classList.remove('show');
            }, 5000);
            
        } else {
            const errMsg = result && result.error ? result.error : JSON.stringify(result);
            alert('Có lỗi xảy ra: ' + errMsg);
            console.error('Server returned error:', result);
        }
    } catch (err) {
        // Lỗi fetch / network
        form.classList.remove('loading');
        alert('Có lỗi xảy ra khi gửi dữ liệu! Xem console để biết chi tiết.');
        console.error('Fetch error:', err);
    }
});

// Tự động điền dữ liệu từ localStorage nếu có (chỉ khi chưa submit)
window.addEventListener('load', function() {
    const savedDraft = localStorage.getItem('laborFormDraft');
    const lastSubmitTime = localStorage.getItem('laborFormSubmitTime');
    
    if (savedDraft && !lastSubmitTime) {
        try {
            const data = JSON.parse(savedDraft);
            
            // Hỏi người dùng có muốn khôi phục dữ liệu không
            const restore = confirm('Phát hiện dữ liệu đã lưu trước đó. Bạn có muốn khôi phục không?');
            
            if (restore) {
                // Điền dữ liệu vào form
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input) {
                        if (input.type === 'radio') {
                            const radio = form.querySelector(`[name="${key}"][value="${data[key]}"]`);
                            if (radio) {
                                radio.checked = true;
                                radio.dispatchEvent(new Event('change'));
                            }
                        } else if (input.type === 'checkbox') {
                            if (Array.isArray(data[key])) {
                                data[key].forEach(value => {
                                    const checkbox = form.querySelector(`[name="${key}"][value="${value}"]`);
                                    if (checkbox) checkbox.checked = true;
                                });
                            }
                        } else {
                            input.value = data[key] || '';
                        }
                    }
                });
                
                updateProgress();
            }
        } catch (e) {
            console.error('Lỗi khi khôi phục dữ liệu:', e);
        }
    }
    
    // Initial progress calculation
    updateProgress();
});

// Auto-save feature (lưu tự động mỗi 30 giây)
let autoSaveInterval = setInterval(() => {
    const formDataObj = {
        fullName: document.getElementById('fullName')?.value,
        birthDate: document.getElementById('birthDate')?.value,
        gender: document.querySelector('input[name="gender"]:checked')?.value,
        idNumber: document.getElementById('idNumber')?.value,
        bhxh: document.getElementById('bhxh')?.value,
        bhyt: document.getElementById('bhyt')?.value,
        address: document.getElementById('address')?.value,
        currentAddress: document.getElementById('currentAddress')?.value,
        ethnicity: document.getElementById('ethnicity')?.value,
        major: document.getElementById('major')?.value,
    };
    
    // Chỉ lưu nếu có dữ liệu
    const hasData = Object.values(formDataObj).some(val => val && val.trim() !== '');
    if (hasData) {
        localStorage.setItem('laborFormDraft', JSON.stringify(formDataObj));
        console.log('Đã tự động lưu nháp');
    }
}, 30000); // 30 giây

// Clear interval khi rời trang
window.addEventListener('beforeunload', () => {
    clearInterval(autoSaveInterval);
});

// Validation cho số CCCD (12 số)
const idNumberInput = document.getElementById('idNumber');
if (idNumberInput) {
    idNumberInput.addEventListener('input', function(e) {
        // Chỉ cho phép số
        this.value = this.value.replace(/[^0-9]/g, '');
        
        // Giới hạn 12 ký tự
        if (this.value.length > 12) {
            this.value = this.value.slice(0, 12);
        }
    });
}

// Validation cho mã BHXH (10 số)
const bhxhInput = document.getElementById('bhxh');
if (bhxhInput) {
    bhxhInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 10) {
            this.value = this.value.slice(0, 10);
        }
    });
}

// Validation cho mã BHYT (15 ký tự)
const bhytInput = document.getElementById('bhyt');
if (bhytInput) {
    bhytInput.addEventListener('input', function(e) {
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        if (this.value.length > 15) {
            this.value = this.value.slice(0, 15);
        }
    });
}

// Xử lý ngày sinh (không được là tương lai)
const birthDateInput = document.getElementById('birthDate');
if (birthDateInput) {
    // Set max date to today
    const today = new Date().toISOString().split('T')[0];
    birthDateInput.setAttribute('max', today);
    
    birthDateInput.addEventListener('change', function() {
        const selectedDate = new Date(this.value);
        const currentDate = new Date();
        
        if (selectedDate > currentDate) {
            alert('Ngày sinh không thể là ngày trong tương lai!');
            this.value = '';
        }
    });
}

// Format tên (viết hoa chữ cái đầu)
const fullNameInput = document.getElementById('fullName');
if (fullNameInput) {
    fullNameInput.addEventListener('blur', function() {
        const words = this.value.trim().split(' ').filter(w => w);
        const formattedWords = words.map(word => {
            if (word.length > 0) {
                return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            }
            return word;
        });
        this.value = formattedWords.join(' ');
    });
}

console.log('Form đã sẵn sàng! 🎉');