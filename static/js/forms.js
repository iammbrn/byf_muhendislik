// BYF Mühendislik - Advanced Form Features
// Requires main.js to be loaded first

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.dynamic-field, [data-add-field], [data-preview], [data-enhanced], .form-wizard, form[data-auto-save]')) {
        initDynamicForms();
        initFileUploads();
        initDatePickers();
        initSelect2();
        initFormWizards();
        initAutoSave();
        initCharacterCounters();
    }
});

// Dynamic Form Fields
function initDynamicForms() {
    // Add/remove form fields dynamically
    const addButtons = document.querySelectorAll('[data-add-field]');
    const removeButtons = document.querySelectorAll('[data-remove-field]');
    
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.dataset.addField;
            const template = document.getElementById(`${target}-template`);
            const container = document.getElementById(`${target}-container`);
            
            if (template && container) {
                const newField = template.content.cloneNode(true);
                container.appendChild(newField);
                updateFieldIndexes(container);
            }
        });
    });
    
    // Event delegation for remove buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-remove-field]')) {
            const button = e.target.closest('[data-remove-field]');
            const field = button.closest('.dynamic-field');
            if (field) {
                field.remove();
                updateFieldIndexes(field.parentElement);
            }
        }
    });
}

function updateFieldIndexes(container) {
    const fields = container.querySelectorAll('.dynamic-field');
    fields.forEach((field, index) => {
        // Update all inputs, labels, and other elements with index
        field.querySelectorAll('[name]').forEach(input => {
            const name = input.getAttribute('name');
            const newName = name.replace(/\[\d+\]/, `[${index}]`);
            input.setAttribute('name', newName);
        });
        
        field.querySelectorAll('[id]').forEach(element => {
            const id = element.getAttribute('id');
            const newId = id.replace(/\d+$/, index);
            element.setAttribute('id', newId);
        });
    });
}

// File Upload with Preview
function initFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const previewContainer = document.getElementById(this.dataset.preview);
            
            if (previewContainer) {
                previewContainer.innerHTML = '';
                
                Array.from(files).forEach(file => {
                    if (file.type.startsWith('image/')) {
                        createImagePreview(file, previewContainer);
                    } else {
                        createFilePreview(file, previewContainer);
                    }
                });
            }
            
            // Update file count
            const fileCount = document.getElementById(`${this.id}-count`);
            if (fileCount) {
                fileCount.textContent = `${files.length} dosya seçildi`;
            }
        });
    });
}

function createImagePreview(file, container) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.innerHTML = `
            <img src="${e.target.result}" alt="${file.name}">
            <div class="file-info">
                <span class="file-name">${file.name}</span>
                <span class="file-size">${BYFUtils.formatFileSize(file.size)}</span>
            </div>
            <button type="button" class="btn btn-sm btn-danger remove-file">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(preview);
        
        // Add remove functionality
        preview.querySelector('.remove-file').addEventListener('click', function() {
            preview.remove();
            updateFileInput();
        });
    };
    reader.readAsDataURL(file);
}

function createFilePreview(file, container) {
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    preview.innerHTML = `
        <div class="file-icon">
            <i class="fas fa-file"></i>
        </div>
        <div class="file-info">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${BYFUtils.formatFileSize(file.size)}</span>
        </div>
        <button type="button" class="btn btn-sm btn-danger remove-file">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(preview);
    
    preview.querySelector('.remove-file').addEventListener('click', function() {
        preview.remove();
        updateFileInput();
    });
}

function updateFileInput() {
    // This would need to be implemented based on specific requirements
    // Could involve creating a new FileList or using FormData
    console.log('Update file input logic here');
}

// Date Pickers
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Add custom date picker if needed
        // You can integrate a library like flatpickr here
        
        // Set min/max dates based on data attributes
        if (input.dataset.minDate) {
            input.min = input.dataset.minDate;
        }
        if (input.dataset.maxDate) {
            input.max = input.dataset.maxDate;
        }
        
        // Add today button if specified
        if (input.dataset.showToday) {
            addTodayButton(input);
        }
    });
}

function addTodayButton(input) {
    const wrapper = input.parentElement;
    const todayBtn = document.createElement('button');
    todayBtn.type = 'button';
    todayBtn.className = 'btn btn-sm btn-outline';
    todayBtn.innerHTML = '<i class="fas fa-calendar-day"></i> Bugün';
    todayBtn.style.marginLeft = '0.5rem';
    
    todayBtn.addEventListener('click', function() {
        const today = new Date().toISOString().split('T')[0];
        input.value = today;
        input.dispatchEvent(new Event('change'));
    });
    
    wrapper.appendChild(todayBtn);
}

// Enhanced Select Elements (Select2-like functionality)
function initSelect2() {
    const enhancedSelects = document.querySelectorAll('select[data-enhanced]');
    
    enhancedSelects.forEach(select => {
        // You can integrate Select2 library here
        // For now, we'll add basic search functionality
        
        if (select.dataset.ajaxUrl) {
            initAjaxSelect(select);
        }
    });
}

function initAjaxSelect(select) {
    let isOpen = false;
    
    select.addEventListener('focus', function() {
        if (!isOpen && this.value === '') {
            loadAjaxOptions(this);
        }
    });
    
    select.addEventListener('click', function() {
        if (!isOpen && this.value === '') {
            loadAjaxOptions(this);
        }
    });
}

async function loadAjaxOptions(select) {
    const url = select.dataset.ajaxUrl;
    const searchTerm = select.dataset.term || '';
    
    try {
        const response = await fetch(`${url}?search=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        
        // Clear existing options except the first one
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Add new options
        data.results.forEach(item => {
            const option = new Option(item.text, item.id, false, false);
            select.add(option);
        });
        
    } catch (error) {
        console.error('Failed to load select options:', error);
    }
}

// Form Wizards
function initFormWizards() {
    const wizards = document.querySelectorAll('.form-wizard');
    
    wizards.forEach(wizard => {
        const steps = wizard.querySelectorAll('.wizard-step');
        const nextButtons = wizard.querySelectorAll('.btn-next');
        const prevButtons = wizard.querySelectorAll('.btn-prev');
        const progress = wizard.querySelector('.wizard-progress');
        
        let currentStep = 0;
        
        // Initialize wizard
        showStep(wizard, currentStep);
        
        // Next button handlers
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                if (validateStep(wizard, currentStep)) {
                    currentStep++;
                    showStep(wizard, currentStep);
                    updateProgress(progress, currentStep, steps.length);
                }
            });
        });
        
        // Previous button handlers
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentStep--;
                showStep(wizard, currentStep);
                updateProgress(progress, currentStep, steps.length);
            });
        });
    });
}

function showStep(wizard, stepIndex) {
    const steps = wizard.querySelectorAll('.wizard-step');
    const nextButtons = wizard.querySelectorAll('.btn-next');
    const prevButtons = wizard.querySelectorAll('.btn-prev');
    const submitButton = wizard.querySelector('.btn-submit');
    
    // Hide all steps
    steps.forEach(step => step.classList.remove('active'));
    
    // Show current step
    steps[stepIndex].classList.add('active');
    
    // Update button states
    const isFirstStep = stepIndex === 0;
    const isLastStep = stepIndex === steps.length - 1;
    
    prevButtons.forEach(btn => btn.disabled = isFirstStep);
    nextButtons.forEach(btn => btn.style.display = isLastStep ? 'none' : 'inline-flex');
    
    if (submitButton) {
        submitButton.style.display = isLastStep ? 'inline-flex' : 'none';
    }
}

function validateStep(wizard, stepIndex) {
    const currentStep = wizard.querySelectorAll('.wizard-step')[stepIndex];
    const inputs = currentStep.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            BYFValidation.showFieldError(input, 'Bu alan zorunludur.');
            isValid = false;
        } else {
            BYFValidation.clearFieldError(input);
        }
    });
    
    return isValid;
}

function updateProgress(progress, currentStep, totalSteps) {
    if (progress) {
        const percentage = ((currentStep + 1) / totalSteps) * 100;
        progress.style.width = `${percentage}%`;
        
        // Update progress text if exists
        const progressText = progress.parentElement.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${currentStep + 1}/${totalSteps}`;
        }
    }
}

// Auto-save functionality for long forms
function initAutoSave() {
    const autoSaveForms = document.querySelectorAll('form[data-auto-save]');
    
    autoSaveForms.forEach(form => {
        let saveTimeout;
        
        form.addEventListener('input', BYFUtils.debounce(function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveForm(form);
            }, 1000);
        }, 500));
    });
}

async function autoSaveForm(form) {
    const formData = new FormData(form);
    const saveUrl = form.dataset.saveUrl;
    
    if (!saveUrl) return;
    
    try {
        const response = await fetch(saveUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': BYFAPI.getCSRFToken()
            }
        });
        
        if (response.ok) {
            showAutoSaveIndicator(form, true);
        } else {
            throw new Error('Auto-save failed');
        }
    } catch (error) {
        showAutoSaveIndicator(form, false);
        console.error('Auto-save failed:', error);
    }
}

function showAutoSaveIndicator(form, success) {
    let indicator = form.querySelector('.auto-save-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        form.appendChild(indicator);
    }
    
    indicator.textContent = success ? '✓ Kaydedildi' : '! Kaydedilemedi';
    indicator.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        padding: 0.5rem 1rem;
        background: ${success ? '#d4edda' : '#f8d7da'};
        color: ${success ? '#155724' : '#721c24'};
        border: 1px solid ${success ? '#c3e6cb' : '#f5c6cb'};
        border-radius: 4px;
        font-size: 0.875rem;
        z-index: 1000;
    `;
    
    setTimeout(() => {
        indicator.style.opacity = '0';
        indicator.style.transition = 'opacity 0.5s ease';
        setTimeout(() => indicator.remove(), 500);
    }, 2000);
}

// Character counters for text inputs
function initCharacterCounters() {
    const textInputs = document.querySelectorAll('input[maxlength], textarea[maxlength]');
    
    textInputs.forEach(input => {
        const maxLength = input.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.cssText = `
            font-size: 0.75rem;
            color: #6c757d;
            text-align: right;
            margin-top: 0.25rem;
        `;
        
        input.parentNode.appendChild(counter);
        
        function updateCounter() {
            const currentLength = input.value.length;
            counter.textContent = `${currentLength}/${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counter.style.color = '#dc3545';
            } else if (currentLength > maxLength * 0.75) {
                counter.style.color = '#ffc107';
            } else {
                counter.style.color = '#6c757d';
            }
        }
        
        input.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });
}

// Export form functions for external use
window.BYFForms = {
    initDynamicForms,
    initFileUploads,
    initDatePickers,
    initSelect2,
    initFormWizards,
    initAutoSave,
    initCharacterCounters,
    updateFieldIndexes,
    validateStep
};