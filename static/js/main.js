// BYF Mühendislik - Ana JavaScript Dosyası

document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initFormValidations();
    initStatsCounter();
    initToastMessages();
    initBackToTop();
});

// Navbar Toggle Function
function initNavbar() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar')) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
}

// Form Validation - Basic for simple forms (complex forms use forms.js)
function initFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!BYFValidation.validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

// Stats Counter Animation
function initStatsCounter() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    
    if (counters.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => observer.observe(counter));
    }
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-count'));
    const duration = 2000; // 2 seconds
    const step = target / (duration / 16); // 60fps
    let current = 0;
    
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// Toast Messages
function initToastMessages() {
    const toasts = document.querySelectorAll('.alert');
    
    toasts.forEach(toast => {
        if (toast.classList.contains('alert-auto-close')) {
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.5s ease';
                setTimeout(() => toast.remove(), 500);
            }, 5000);
        }
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: auto;
        `;
        closeBtn.addEventListener('click', () => toast.remove());
        
        toast.style.display = 'flex';
        toast.appendChild(closeBtn);
    });
}

// Back to Top Button
function initBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '↑';
    backToTop.className = 'back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        font-size: 1.2rem;
        display: none;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    `;
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('tr-TR', options);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API Helper Functions
class BYFAPI {
    static async request(endpoint, options = {}) {
        const baseURL = window.location.origin;
        const url = `${baseURL}/api${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    // Auth endpoints
    static async login(credentials) {
        return this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }
    
    static async logout() {
        return this.request('/auth/logout/', {
            method: 'POST'
        });
    }
    
    // Firm endpoints
    static async getFirm() {
        return this.request('/firms/my-firm/');
    }
    
    static async getFirmServices() {
        return this.request('/firms/my-services/');
    }
    
    // Service endpoints
    static async createServiceRequest(data) {
        return this.request('/service-requests/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Validation utilities - shared with forms.js
const BYFValidation = {
    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Bu alan zorunludur.');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
            
            if (field.type === 'email' && field.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(field.value)) {
                    this.showFieldError(field, 'Geçerli bir e-posta adresi girin.');
                    isValid = false;
                }
            }
            
            if (field.type === 'tel' && field.value) {
                const phoneRegex = /^[+]?[0-9\s\-()]{10,}$/;
                if (!phoneRegex.test(field.value)) {
                    this.showFieldError(field, 'Geçerli bir telefon numarası girin.');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    },
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        field.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = 'color: #dc3545; font-size: 0.875rem; margin-top: 0.25rem; display: block;';
        field.parentNode.appendChild(errorDiv);
    },
    
    clearFieldError(field) {
        field.classList.remove('error');
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) existingError.remove();
    }
};

// Export for use in other modules
window.BYFAPI = BYFAPI;
window.BYFValidation = BYFValidation;
window.BYFUtils = {
    debounce,
    formatDate,
    formatFileSize
};