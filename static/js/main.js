// جافاسكريبت للنظام

// تأكيد الحذف
function confirmDelete(message = 'هل أنت متأكد من أنك تريد الحذف؟') {
    return confirm(message);
}

// تأكيد الأرشيف
function confirmArchive(message = 'هل أنت متأكد من أنك تريد أرشفة هذه المراسلة؟') {
    return confirm(message);
}

// تحويل التاريخ
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG');
}

// رسائل التنبيه
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.prepend(alertDiv);
        
        // إزالة التنبيه تلقائياً بعد 5 ثوان
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// البحث في الجداول
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cell = cells[j];
                if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            
            if (found) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إضافة تأثيرات للبطاقات
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // تأكيد عند الخروج من الصفحة مع بيانات غير محفوظة
    window.addEventListener('beforeunload', function(e) {
        const forms = document.querySelectorAll('form');
        let hasUnsavedData = false;
        
        forms.forEach(form => {
            if (form.classList.contains('needs-validation')) {
                const inputs = form.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    if (input.value !== input.defaultValue) {
                        hasUnsavedData = true;
                    }
                });
            }
        });
        
        if (hasUnsavedData) {
            e.preventDefault();
            e.returnValue = 'لديك بيانات غير محفوظة. هل تريد المغادرة دون الحفظ؟';
        }
    });
});

// تحميل الملفات المعاينة
function previewFile(input, previewId) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    
    if (file) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-file"></i> ${file.name} (${(file.size / 1024).toFixed(2)} KB)
                </div>
            `;
        }
    }
}