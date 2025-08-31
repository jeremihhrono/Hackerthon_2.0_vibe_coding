/**
 * Community Health System - Main JavaScript File
 * Handles global functionality, UI enhancements, and common interactions
 */

// Global variables
let currentUser = null;
let notifications = [];

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize common UI components
    initializeCommonComponents();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize navigation features
    initializeNavigation();
    
    // Initialize back to top button
    initializeBackToTop();
    
    // Initialize auto-refresh features
    initializeAutoRefresh();
    
    console.log('Community Health System initialized');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize common UI components
 */
function initializeCommonComponents() {
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize modals with custom behavior
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('show.bs.modal', function() {
            // Add loading animation if needed
            var loadingContent = modal.querySelector('.loading-content');
            if (loadingContent) {
                showLoading(loadingContent);
            }
        });
    });
    
    // Initialize alerts auto-dismiss
    var alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.parentNode) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000); // Auto-dismiss after 5 seconds
    });
}

/**
 * Initialize form enhancements
 */
function initializeFormEnhancements() {
    // Phone number formatting
    var phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            formatKenyanPhoneNumber(this);
        });
    });
    
    // Auto-resize textareas
    var textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    });
    
    // Form validation feedback
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                scrollToFirstError(form);
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Currency formatting for amount inputs
    var amountInputs = document.querySelectorAll('input[name="amount"], input[data-currency="true"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            formatCurrency(this);
        });
    });
}

/**
 * Format Kenyan phone numbers
 */
function formatKenyanPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.startsWith('254')) {
        value = '+' + value;
    } else if (value.startsWith('0')) {
        value = '+254' + value.substring(1);
    } else if (value.length === 9) {
        value = '+254' + value;
    }
    
    input.value = value;
    
    // Validate Kenyan phone number format
    var isValid = /^\+254[17]\d{8}$/.test(value);
    if (value && !isValid) {
        input.classList.add('is-invalid');
        showFieldError(input, 'Please enter a valid Kenyan phone number');
    } else {
        input.classList.remove('is-invalid');
        hideFieldError(input);
    }
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

/**
 * Format currency values
 */
function formatCurrency(input) {
    let value = parseFloat(input.value);
    if (!isNaN(value)) {
        input.value = value.toFixed(2);
    }
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
    hideFieldError(field);
    
    var feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    feedback.setAttribute('data-field-error', 'true');
    
    field.parentNode.appendChild(feedback);
}

/**
 * Hide field error message
 */
function hideFieldError(field) {
    var existingError = field.parentNode.querySelector('[data-field-error="true"]');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Scroll to first form error
 */
function scrollToFirstError(form) {
    var firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

/**
 * Initialize navigation features
 */
function initializeNavigation() {
    // Highlight current page in navigation
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href)) {
            link.classList.add('active');
        }
    });
    
    // Mobile menu enhancements
    var navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
}

/**
 * Initialize back to top button
 */
function initializeBackToTop() {
    // Create back to top button
    var backToTopBtn = document.createElement('button');
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTopBtn.setAttribute('title', 'Back to top');
    document.body.appendChild(backToTopBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });
    
    // Scroll to top functionality
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Initialize auto-refresh features
 */
function initializeAutoRefresh() {
    // Auto-refresh notifications badge
    setInterval(function() {
        updateNotificationsBadge();
    }, 60000); // Check every minute
    
    // Auto-save form data to localStorage
    var formInputs = document.querySelectorAll('form input, form textarea, form select');
    formInputs.forEach(function(input) {
        if (input.type !== 'password' && input.type !== 'submit') {
            input.addEventListener('input', function() {
                saveFormData(this);
            });
        }
    });
    
    // Restore form data on page load
    restoreFormData();
}

/**
 * Update notifications badge
 */
function updateNotificationsBadge() {
    // In a real implementation, this would make an API call
    // For now, we'll simulate notification updates
    var notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        // Simulate random notification count (0-5)
        var count = Math.floor(Math.random() * 6);
        if (count > 0) {
            notificationBadge.textContent = count;
            notificationBadge.style.display = 'inline-block';
        } else {
            notificationBadge.style.display = 'none';
        }
    }
}

/**
 * Save form data to localStorage
 */
function saveFormData(input) {
    var formId = input.closest('form')?.id;
    if (formId) {
        var key = formId + '_' + input.name;
        localStorage.setItem(key, input.value);
    }
}

/**
 * Restore form data from localStorage
 */
function restoreFormData() {
    var forms = document.querySelectorAll('form[id]');
    forms.forEach(function(form) {
        var formId = form.id;
        var inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(function(input) {
            if (input.type !== 'password' && input.type !== 'submit') {
                var key = formId + '_' + input.name;
                var savedValue = localStorage.getItem(key);
                if (savedValue) {
                    input.value = savedValue;
                }
            }
        });
    });
}

/**
 * Clear saved form data
 */
function clearFormData(formId) {
    for (var i = localStorage.length - 1; i >= 0; i--) {
        var key = localStorage.key(i);
        if (key && key.startsWith(formId + '_')) {
            localStorage.removeItem(key);
        }
    }
}

/**
 * Show loading overlay
 */
function showLoading(container = document.body) {
    var overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted">Loading...</p>
        </div>
    `;
    container.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading(container = document.body) {
    var overlay = container.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Show success message
 */
function showSuccessMessage(message, container = null) {
    showMessage(message, 'success', container);
}

/**
 * Show error message
 */
function showErrorMessage(message, container = null) {
    showMessage(message, 'danger', container);
}

/**
 * Show warning message
 */
function showWarningMessage(message, container = null) {
    showMessage(message, 'warning', container);
}

/**
 * Show info message
 */
function showInfoMessage(message, container = null) {
    showMessage(message, 'info', container);
}

/**
 * Generic message display function
 */
function showMessage(message, type = 'info', container = null) {
    var targetContainer = container || document.querySelector('.container') || document.body;
    
    var alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the beginning of the container
    targetContainer.insertBefore(alert, targetContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        if (alert.parentNode) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Confirm dialog with custom styling
 */
function confirmAction(message, callback, type = 'danger') {
    var modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-0">
                    <h5 class="modal-title">
                        <i class="fas fa-${type === 'danger' ? 'exclamation-triangle text-danger' : 'question-circle text-primary'} me-2"></i>
                        Confirm Action
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="mb-0">${message}</p>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-${type}" id="confirmBtn">Confirm</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    var bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Handle confirm button click
    modal.querySelector('#confirmBtn').addEventListener('click', function() {
        callback();
        bsModal.hide();
    });
    
    // Clean up modal after hiding
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
}

/**
 * Format date for display
 */
function formatDate(date, format = 'short') {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const options = {
        short: { day: 'numeric', month: 'short', year: 'numeric' },
        long: { day: 'numeric', month: 'long', year: 'numeric' },
        time: { hour: '2-digit', minute: '2-digit' },
        datetime: { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-KE', options[format]).format(date);
}

/**
 * Format currency for Kenyan Shillings
 */
function formatKenyanCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait, immediate) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Check if user is online
 */
function checkOnlineStatus() {
    if (navigator.onLine) {
        document.body.classList.remove('offline');
        showSuccessMessage('Connection restored');
    } else {
        document.body.classList.add('offline');
        showWarningMessage('You are currently offline. Some features may not work.');
    }
}

// Listen for online/offline events
window.addEventListener('online', checkOnlineStatus);
window.addEventListener('offline', checkOnlineStatus);

/**
 * Healthcare-specific utilities
 */

/**
 * Calculate BMI
 */
function calculateBMI(weight, height) {
    if (!weight || !height || height === 0) return null;
    const heightM = height / 100; // Convert cm to meters
    const bmi = weight / (heightM * heightM);
    return Math.round(bmi * 10) / 10; // Round to 1 decimal place
}

/**
 * Get BMI category
 */
function getBMICategory(bmi) {
    if (!bmi) return 'Unknown';
    
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

/**
 * Calculate age from date of birth
 */
function calculateAge(dateOfBirth) {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    return age;
}

/**
 * Validate Kenyan National ID
 */
function validateKenyanNationalId(nationalId) {
    if (!nationalId) return false;
    const cleaned = nationalId.replace(/\D/g, '');
    return cleaned.length === 8;
}

/**
 * Export functionality for healthcare data
 */
function exportToCSV(data, filename) {
    const csv = convertArrayToCSV(data);
    downloadCSV(csv, filename);
}

function convertArrayToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Export functions for use in other scripts
window.CHS = {
    showLoading,
    hideLoading,
    showSuccessMessage,
    showErrorMessage,
    showWarningMessage,
    showInfoMessage,
    confirmAction,
    formatDate,
    formatKenyanCurrency,
    calculateBMI,
    getBMICategory,
    calculateAge,
    validateKenyanNationalId,
    exportToCSV,
    debounce
};

console.log('Community Health System - Main JS loaded');
