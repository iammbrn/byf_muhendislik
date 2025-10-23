// BYF Mühendislik - Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Dashboard specific initialization
    initDashboardCharts();
    initDashboardFilters();
    initRealTimeUpdates();
    initServiceActions();
});

// Initialize Dashboard Charts
function initDashboardCharts() {
    const statsChart = document.getElementById('stats-chart');
    if (statsChart) {
        // Burada chart.js veya başka bir kütüphane kullanılabilir
        console.log('Chart container found, would initialize chart here');
    }
}

// Initialize Dashboard Filters
function initDashboardFilters() {
    const filterForms = document.querySelectorAll('.filter-form');
    
    filterForms.forEach(form => {
        form.addEventListener('change', debounce(function() {
            // AJAX ile filtreleme yapılabilir
            submitFilterForm(form);
        }, 500));
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitFilterForm(form);
        });
    });
}

function submitFilterForm(form) {
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Filtreleniyor...';
    submitBtn.disabled = true;
    
    // Simulate API call - replace with actual AJAX call
    setTimeout(() => {
        window.location.href = `${window.location.pathname}?${params.toString()}`;
    }, 1000);
}

// Real-time Updates for Dashboard
function initRealTimeUpdates() {
    // Only initialize if user is on dashboard page
    if (!document.querySelector('.dashboard-header')) return;
    
    // Check for new notifications every 30 seconds
    setInterval(checkForUpdates, 30000);
}

async function checkForUpdates() {
    try {
        const updates = await BYFAPI.request('/dashboard/updates/');
        
        if (updates.new_services > 0 || updates.new_documents > 0) {
            showUpdateNotification(updates);
        }
    } catch (error) {
        console.error('Failed to check for updates:', error);
    }
}

function showUpdateNotification(updates) {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-bell"></i>
            <div>
                <strong>Yeni Güncellemeler</strong>
                <p>${updates.new_services} yeni hizmet, ${updates.new_documents} yeni doküman</p>
            </div>
            <button class="btn btn-sm btn-primary" onclick="location.reload()">Yenile</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        z-index: 1050;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 10 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 10000);
}

// Service Actions (start, complete, cancel)
function initServiceActions() {
    const serviceActions = document.querySelectorAll('[data-service-action]');
    
    serviceActions.forEach(action => {
        action.addEventListener('click', function() {
            const serviceId = this.dataset.serviceId;
            const actionType = this.dataset.serviceAction;
            
            performServiceAction(serviceId, actionType);
        });
    });
}

async function performServiceAction(serviceId, actionType) {
    if (!confirm('Bu işlemi gerçekleştirmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const result = await BYFAPI.request(`/services/${serviceId}/${actionType}/`, {
            method: 'POST'
        });
        
        showToast('İşlem başarıyla gerçekleştirildi.', 'success');
        
        // Reload the page after a short delay
        setTimeout(() => {
            location.reload();
        }, 1500);
        
    } catch (error) {
        showToast('İşlem sırasında bir hata oluştu.', 'error');
        console.error('Service action failed:', error);
    }
}

// Document Download with Progress
function initDocumentDownloads() {
    const downloadButtons = document.querySelectorAll('[data-document-download]');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const documentId = this.dataset.documentId;
            downloadDocument(documentId, this);
        });
    });
}

async function downloadDocument(documentId, button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;
    
    try {
        const response = await fetch(`/api/documents/${documentId}/download/`);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `document-${documentId}.pdf`; // You might want to get the actual filename from response
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        showToast('Doküman indiriliyor...', 'success');
        
    } catch (error) {
        showToast('İndirme sırasında bir hata oluştu.', 'error');
        console.error('Download failed:', error);
    } finally {
        button.innerHTML = originalHTML;
        button.disabled = false;
    }
}

// Quick Stats Update
function updateQuickStats() {
    const statElements = {
        totalServices: document.querySelector('[data-stat="total-services"]'),
        completedServices: document.querySelector('[data-stat="completed-services"]'),
        pendingRequests: document.querySelector('[data-stat="pending-requests"]')
    };
    
    // Simulate stats update - replace with actual API call
    Object.values(statElements).forEach(stat => {
        if (stat) {
            const current = parseInt(stat.textContent);
            const change = Math.floor(Math.random() * 5) - 2; // Random change between -2 and +2
            const newValue = Math.max(0, current + change);
            
            stat.textContent = newValue;
            stat.parentElement.classList.add('updated');
            
            setTimeout(() => {
                stat.parentElement.classList.remove('updated');
            }, 2000);
        }
    });
}

// Utility function for showing toasts
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-auto-close`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // Initialize toast behavior
    const toasts = document.querySelectorAll('.alert');
    toasts.forEach(t => {
        if (t.classList.contains('alert-auto-close')) {
            setTimeout(() => {
                t.style.opacity = '0';
                t.style.transition = 'opacity 0.5s ease';
                setTimeout(() => t.remove(), 500);
            }, 5000);
        }
    });
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Auto-refresh dashboard data every 2 minutes
setInterval(updateQuickStats, 120000);

// Export functions for global access
window.Dashboard = {
    updateQuickStats,
    performServiceAction,
    downloadDocument,
    showToast
};