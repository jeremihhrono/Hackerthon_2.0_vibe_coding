/**
 * Community Health System - Payments JavaScript
 * Handles payment processing, IntaSend integration, and payment-related UI interactions
 */

// Payment processing state
let paymentState = {
    processing: false,
    currentPayment: null,
    intasendInstance: null
};

// IntaSend configuration
const INTASEND_CONFIG = {
    sandbox: true, // Toggle for production
    currency: 'KES',
    methods: ['mpesa', 'card', 'bank'],
    webhookUrl: '/webhooks/intasend'
};

document.addEventListener('DOMContentLoaded', function() {
    initializePaymentSystem();
});

/**
 * Initialize payment system
 */
function initializePaymentSystem() {
    // Initialize payment form enhancements
    initializePaymentForm();
    
    // Initialize payment method selection
    initializePaymentMethods();
    
    // Initialize M-Pesa specific features
    initializeMpesaFeatures();
    
    // Initialize payment status tracking
    initializePaymentTracking();
    
    // Initialize payment history features
    initializePaymentHistory();
    
    console.log('Payment system initialized');
}

/**
 * Initialize payment form enhancements
 */
function initializePaymentForm() {
    const paymentForm = document.getElementById('paymentForm');
    if (!paymentForm) return;
    
    // Amount input formatting
    const amountInput = paymentForm.querySelector('input[name="amount"]');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            formatAmountInput(this);
            updatePaymentSummary();
        });
        
        amountInput.addEventListener('blur', function() {
            validateAmount(this);
        });
    }
    
    // Phone number validation
    const phoneInput = paymentForm.querySelector('input[name="phone_number"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatMpesaPhoneNumber(this);
            updatePaymentSummary();
        });
        
        phoneInput.addEventListener('blur', function() {
            validateMpesaPhoneNumber(this);
        });
    }
    
    // Payment type change handler
    const paymentTypeSelect = paymentForm.querySelector('select[name="payment_type"]');
    if (paymentTypeSelect) {
        paymentTypeSelect.addEventListener('change', function() {
            updatePaymentTypeDescription(this.value);
            updatePaymentSummary();
        });
    }
    
    // Description input handler
    const descriptionInput = paymentForm.querySelector('textarea[name="description"]');
    if (descriptionInput) {
        descriptionInput.addEventListener('input', function() {
            updatePaymentSummary();
        });
    }
    
    // Form submission handler
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        processPayment();
    });
}

/**
 * Format amount input
 */
function formatAmountInput(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Limit decimal places to 2
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    input.value = value;
}

/**
 * Validate amount
 */
function validateAmount(input) {
    const amount = parseFloat(input.value);
    const minAmount = 1;
    const maxAmount = 1000000; // 1 million KES
    
    if (isNaN(amount) || amount < minAmount) {
        showInputError(input, `Minimum amount is KES ${minAmount}`);
        return false;
    }
    
    if (amount > maxAmount) {
        showInputError(input, `Maximum amount is KES ${maxAmount.toLocaleString()}`);
        return false;
    }
    
    hideInputError(input);
    return true;
}

/**
 * Format M-Pesa phone number
 */
function formatMpesaPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Handle different Kenyan number formats
    if (value.startsWith('254')) {
        value = '+' + value;
    } else if (value.startsWith('0')) {
        value = '+254' + value.substring(1);
    } else if (value.length === 9) {
        value = '+254' + value;
    } else if (value.startsWith('7') && value.length === 9) {
        value = '+254' + value;
    }
    
    input.value = value;
}

/**
 * Validate M-Pesa phone number
 */
function validateMpesaPhoneNumber(input) {
    const phonePattern = /^\+254[17]\d{8}$/;
    const isValid = phonePattern.test(input.value);
    
    if (input.value && !isValid) {
        showInputError(input, 'Please enter a valid Safaricom M-Pesa number (e.g., +254712345678)');
        return false;
    }
    
    hideInputError(input);
    return true;
}

/**
 * Show input error
 */
function showInputError(input, message) {
    hideInputError(input);
    
    input.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    feedback.setAttribute('data-error-for', input.name);
    
    input.parentNode.appendChild(feedback);
}

/**
 * Hide input error
 */
function hideInputError(input) {
    input.classList.remove('is-invalid');
    
    const existingError = input.parentNode.querySelector(`[data-error-for="${input.name}"]`);
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Update payment type description
 */
function updatePaymentTypeDescription(paymentType) {
    const descriptions = {
        'consultation_fee': 'Fee for medical consultation and examination',
        'treatment_fee': 'Fee for medical treatment and procedures',
        'medication_fee': 'Fee for prescribed medications and drugs',
        'screening_fee': 'Fee for health screening and diagnostic tests',
        'chw_allowance': 'Monthly allowance for Community Health Worker',
        'other': 'Other healthcare-related payment'
    };
    
    const descriptionInput = document.querySelector('textarea[name="description"]');
    if (descriptionInput && !descriptionInput.value) {
        descriptionInput.value = descriptions[paymentType] || '';
        descriptionInput.dispatchEvent(new Event('input'));
    }
}

/**
 * Update payment summary
 */
function updatePaymentSummary() {
    const form = document.getElementById('paymentForm');
    if (!form) return;
    
    const amount = form.querySelector('input[name="amount"]')?.value || '0';
    const paymentType = form.querySelector('select[name="payment_type"]')?.selectedOptions[0]?.text || 'Select payment type';
    const description = form.querySelector('textarea[name="description"]')?.value || 'Enter description';
    const phone = form.querySelector('input[name="phone_number"]')?.value || 'Enter phone number';
    
    // Update summary elements
    updateSummaryElement('summaryAmount', formatCurrency(parseFloat(amount) || 0));
    updateSummaryElement('summaryType', paymentType);
    updateSummaryElement('summaryDescription', truncateText(description, 50));
    updateSummaryElement('summaryPhone', phone);
}

/**
 * Update summary element
 */
function updateSummaryElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        const strongElement = element.querySelector('strong').nextSibling;
        if (strongElement) {
            strongElement.textContent = ` ${value}`;
        }
    }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return `KES ${amount.toLocaleString('en-KE', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

/**
 * Truncate text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Initialize payment methods
 */
function initializePaymentMethods() {
    // Add payment method selection if needed
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            selectPaymentMethod(this.dataset.method);
        });
    });
}

/**
 * Select payment method
 */
function selectPaymentMethod(method) {
    // Remove active class from all methods
    document.querySelectorAll('.payment-method').forEach(el => {
        el.classList.remove('active');
    });
    
    // Add active class to selected method
    const selectedMethod = document.querySelector(`[data-method="${method}"]`);
    if (selectedMethod) {
        selectedMethod.classList.add('active');
    }
    
    // Update form based on selected method
    updateFormForPaymentMethod(method);
}

/**
 * Update form for payment method
 */
function updateFormForPaymentMethod(method) {
    const phoneGroup = document.querySelector('.phone-group');
    const cardGroup = document.querySelector('.card-group');
    
    if (method === 'mpesa') {
        if (phoneGroup) phoneGroup.style.display = 'block';
        if (cardGroup) cardGroup.style.display = 'none';
    } else if (method === 'card') {
        if (phoneGroup) phoneGroup.style.display = 'none';
        if (cardGroup) cardGroup.style.display = 'block';
    }
}

/**
 * Initialize M-Pesa specific features
 */
function initializeMpesaFeatures() {
    // Add M-Pesa number suggestions based on patient data
    const phoneInput = document.querySelector('input[name="phone_number"]');
    if (phoneInput) {
        // Pre-fill with patient phone if available
        const patientPhone = phoneInput.getAttribute('data-patient-phone');
        if (patientPhone && !phoneInput.value) {
            phoneInput.value = patientPhone;
        }
    }
    
    // Add M-Pesa instructions
    addMpesaInstructions();
}

/**
 * Add M-Pesa instructions
 */
function addMpesaInstructions() {
    const mpesaInstructions = document.querySelector('.mpesa-instructions');
    if (mpesaInstructions) {
        mpesaInstructions.innerHTML = `
            <div class="alert alert-info">
                <h6><i class="fas fa-mobile-alt me-2"></i>M-Pesa Payment Instructions</h6>
                <ol class="mb-0">
                    <li>Enter your Safaricom M-Pesa number</li>
                    <li>Click "Process Payment" to initiate</li>
                    <li>Check your phone for M-Pesa prompt</li>
                    <li>Enter your M-Pesa PIN to complete payment</li>
                    <li>You'll receive SMS confirmation</li>
                </ol>
            </div>
        `;
    }
}

/**
 * Process payment
 */
function processPayment() {
    if (paymentState.processing) return;
    
    const form = document.getElementById('paymentForm');
    if (!validatePaymentForm(form)) return;
    
    paymentState.processing = true;
    updateProcessingUI(true);
    
    const paymentData = collectPaymentData(form);
    
    // Simulate IntaSend API call
    initiateIntasendPayment(paymentData)
        .then(response => {
            handlePaymentResponse(response);
        })
        .catch(error => {
            handlePaymentError(error);
        })
        .finally(() => {
            paymentState.processing = false;
            updateProcessingUI(false);
        });
}

/**
 * Validate payment form
 */
function validatePaymentForm(form) {
    let isValid = true;
    
    const amountInput = form.querySelector('input[name="amount"]');
    if (!validateAmount(amountInput)) isValid = false;
    
    const phoneInput = form.querySelector('input[name="phone_number"]');
    if (!validateMpesaPhoneNumber(phoneInput)) isValid = false;
    
    const paymentType = form.querySelector('select[name="payment_type"]').value;
    if (!paymentType) {
        showFormError('Please select a payment type');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Collect payment data from form
 */
function collectPaymentData(form) {
    const formData = new FormData(form);
    return {
        amount: parseFloat(formData.get('amount')),
        payment_type: formData.get('payment_type'),
        description: formData.get('description'),
        phone_number: formData.get('phone_number'),
        currency: 'KES',
        method: 'mpesa'
    };
}

/**
 * Update processing UI
 */
function updateProcessingUI(processing) {
    const submitBtn = document.getElementById('processPaymentBtn');
    const form = document.getElementById('paymentForm');
    
    if (processing) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Payment...';
        form.classList.add('processing');
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-credit-card me-2"></i>Process Payment';
        form.classList.remove('processing');
    }
}

/**
 * Initiate IntaSend payment
 */
function initiateIntasendPayment(paymentData) {
    return new Promise((resolve, reject) => {
        // Simulate API delay
        setTimeout(() => {
            // Simulate successful payment initiation
            const mockResponse = {
                success: true,
                checkout_url: `/payments?mock_payment=CHS${Date.now()}`,
                payment_id: `PAY_${Date.now()}`,
                message: 'Payment initiated successfully. Check your phone for M-Pesa prompt.'
            };
            
            // Simulate occasional failures for testing
            if (Math.random() < 0.1) {
                reject(new Error('Payment initiation failed. Please try again.'));
            } else {
                resolve(mockResponse);
            }
        }, 2000);
    });
}

/**
 * Handle payment response
 */
function handlePaymentResponse(response) {
    if (response.success) {
        showPaymentSuccess(response);
        
        // Redirect to payment processing page or show success
        if (response.checkout_url) {
            setTimeout(() => {
                window.location.href = response.checkout_url;
            }, 2000);
        }
    } else {
        handlePaymentError(new Error(response.message || 'Payment failed'));
    }
}

/**
 * Handle payment error
 */
function handlePaymentError(error) {
    console.error('Payment error:', error);
    showPaymentError(error.message || 'Payment processing failed. Please try again.');
}

/**
 * Show payment success
 */
function showPaymentSuccess(response) {
    const alert = createAlert('success', `
        <strong>Payment Initiated Successfully!</strong><br>
        ${response.message}<br>
        <small>Payment ID: ${response.payment_id}</small>
    `);
    
    insertAlert(alert);
}

/**
 * Show payment error
 */
function showPaymentError(message) {
    const alert = createAlert('danger', `
        <strong>Payment Failed!</strong><br>
        ${message}<br>
        <small>Please check your details and try again.</small>
    `);
    
    insertAlert(alert);
}

/**
 * Show form error
 */
function showFormError(message) {
    const alert = createAlert('warning', message);
    insertAlert(alert);
}

/**
 * Create alert element
 */
function createAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    return alert;
}

/**
 * Insert alert at top of form
 */
function insertAlert(alert) {
    const form = document.getElementById('paymentForm');
    const container = form.closest('.card-body');
    container.insertBefore(alert, container.firstChild);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 10000);
}

/**
 * Initialize payment tracking
 */
function initializePaymentTracking() {
    // Check for payment status in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get('status');
    const paymentRef = urlParams.get('payment_ref');
    
    if (paymentStatus) {
        handlePaymentStatusCallback(paymentStatus, paymentRef);
    }
    
    // Start payment status polling if there are pending payments
    startPaymentStatusPolling();
}

/**
 * Handle payment status callback
 */
function handlePaymentStatusCallback(status, paymentRef) {
    const messages = {
        'success': 'Payment completed successfully!',
        'failed': 'Payment was unsuccessful. Please try again.',
        'cancelled': 'Payment was cancelled.',
        'pending': 'Payment is being processed. Please wait...'
    };
    
    const message = messages[status] || 'Unknown payment status';
    const alertType = status === 'success' ? 'success' : status === 'pending' ? 'info' : 'warning';
    
    if (window.CHS) {
        window.CHS.showMessage(message, alertType);
    }
    
    // Clean up URL
    if (paymentRef) {
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
}

/**
 * Start payment status polling
 */
function startPaymentStatusPolling() {
    const pendingPayments = document.querySelectorAll('[data-payment-status="pending"]');
    
    if (pendingPayments.length > 0) {
        const pollInterval = setInterval(() => {
            checkPaymentStatus(pendingPayments)
                .then(hasCompletedPayments => {
                    if (hasCompletedPayments) {
                        // Refresh the page to show updated status
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                        clearInterval(pollInterval);
                    }
                })
                .catch(error => {
                    console.error('Payment status check failed:', error);
                });
        }, 10000); // Check every 10 seconds
        
        // Stop polling after 5 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
        }, 300000);
    }
}

/**
 * Check payment status
 */
function checkPaymentStatus(pendingPayments) {
    return new Promise((resolve) => {
        // In a real implementation, this would make API calls to check status
        // For now, simulate random status updates
        let hasCompleted = false;
        
        pendingPayments.forEach(payment => {
            if (Math.random() < 0.1) { // 10% chance of completion per check
                payment.setAttribute('data-payment-status', 'completed');
                hasCompleted = true;
            }
        });
        
        resolve(hasCompleted);
    });
}

/**
 * Initialize payment history features
 */
function initializePaymentHistory() {
    // Initialize payment filtering
    initializePaymentFiltering();
    
    // Initialize payment export
    initializePaymentExport();
    
    // Initialize payment details modals
    initializePaymentDetailsModals();
}

/**
 * Initialize payment filtering
 */
function initializePaymentFiltering() {
    const filterForm = document.querySelector('.payment-filter-form');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('select, input');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit filter form after short delay
                setTimeout(() => {
                    filterForm.submit();
                }, 500);
            });
        });
    }
}

/**
 * Initialize payment export
 */
function initializePaymentExport() {
    const exportBtn = document.querySelector('.export-payments-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportPaymentData();
        });
    }
}

/**
 * Export payment data
 */
function exportPaymentData() {
    // Collect visible payment data
    const paymentRows = document.querySelectorAll('.payment-table tbody tr');
    const payments = [];
    
    paymentRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            payments.push({
                'Reference': cells[0].textContent.trim(),
                'Amount': cells[1].textContent.trim(),
                'Type': cells[2].textContent.trim(),
                'Patient': cells[3].textContent.trim(),
                'Status': cells[4].textContent.trim(),
                'Date': cells[5].textContent.trim()
            });
        }
    });
    
    if (payments.length > 0 && window.CHS) {
        const filename = `payments_${new Date().toISOString().split('T')[0]}.csv`;
        window.CHS.exportToCSV(payments, filename);
    }
}

/**
 * Initialize payment details modals
 */
function initializePaymentDetailsModals() {
    // This would be implemented based on the actual modal structure
    console.log('Payment details modals initialized');
}

// Quick amount buttons functionality
document.addEventListener('click', function(e) {
    if (e.target.matches('.quick-amount-btn')) {
        const amount = e.target.getAttribute('data-amount');
        const amountInput = document.querySelector('input[name="amount"]');
        if (amountInput) {
            amountInput.value = amount;
            amountInput.dispatchEvent(new Event('input'));
        }
    }
});

// Export payment utilities
window.PaymentUtils = {
    formatCurrency,
    validateAmount,
    validateMpesaPhoneNumber,
    processPayment
};

console.log('Community Health System - Payments JS loaded');
