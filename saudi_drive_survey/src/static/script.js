document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('surveyForm');
    const charCountElement = document.getElementById('char-count');
    const customerSuggestionsTextarea = document.getElementById('customer_suggestions');
    const submitBtn = document.querySelector('.submit-btn');
    const modal = document.getElementById('successModal');
    const closeModal = document.querySelector('.close');

    // Character counters for all textareas
    const textareas = [
        { element: customerSuggestionsTextarea, counter: charCountElement, max: 1000 },
        { element: document.getElementById('additional_features'), counter: document.getElementById('additional-features-count'), max: 500 },
        { element: document.getElementById('additional_problems'), counter: document.getElementById('additional-problems-count'), max: 500 },
        { element: document.getElementById('female_service_suggestions'), counter: document.getElementById('female-suggestions-count'), max: 300 }
    ];

    // Setup character counters
    textareas.forEach(({ element, counter, max }) => {
        if (element && counter) {
            element.addEventListener('input', function() {
                const currentLength = this.value.length;
                const remaining = max - currentLength;
                
                counter.textContent = currentLength;
                
                // Remove existing classes
                counter.classList.remove('warning', 'danger');
                
                // Add appropriate class based on remaining characters
                if (remaining < max * 0.1) { // Less than 10% remaining
                    counter.classList.add('danger');
                } else if (remaining < max * 0.3) { // Less than 30% remaining
                    counter.classList.add('warning');
                }
            });
        }
    });

    // Helper function to get checkbox values
    function getCheckboxValues(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="btn-text">جاري الإرسال...</span> <span class="btn-icon">⏳</span>';
        
        try {
            // Collect form data
            const formData = new FormData(form);
            const data = {};
            
            // Get regular form fields
            for (let [key, value] of formData.entries()) {
                if (!data[key]) {
                    data[key] = value;
                }
            }
            
            // Get checkbox values for multiple choice questions
            data.important_factors = getCheckboxValues('important_factors');
            data.current_problems = getCheckboxValues('current_problems');
            data.preferred_payment = getCheckboxValues('preferred_payment');
            
            // Validate required fields
            if (!data.current_app) {
                throw new Error('يرجى اختيار التطبيق الذي تستخدمه حالياً');
            }
            
            if (!data.usage_frequency) {
                throw new Error('يرجى اختيار تكرار الاستخدام');
            }
            
            if (!data.try_saudi_app) {
                throw new Error('يرجى الإجابة على سؤال تجربة التطبيق السعودي');
            }
            
            if (!data.customer_suggestions || data.customer_suggestions.trim() === '') {
                throw new Error('يرجى كتابة اقتراحاتك وملاحظاتك');
            }
            
            if (data.customer_suggestions.length > 1000) {
                throw new Error('اقتراحاتك يجب أن تكون أقل من 1000 حرف');
            }
            
            // Validate additional text fields lengths
            if (data.additional_features && data.additional_features.length > 500) {
                throw new Error('الميزات الإضافية يجب أن تكون أقل من 500 حرف');
            }
            
            if (data.additional_problems && data.additional_problems.length > 500) {
                throw new Error('المشاكل الإضافية يجب أن تكون أقل من 500 حرف');
            }
            
            if (data.female_service_suggestions && data.female_service_suggestions.length > 300) {
                throw new Error('اقتراحات خدمة الكابتنة يجب أن تكون أقل من 300 حرف');
            }
            
            // Validate Saudi phone number if provided
            if (data.phone && data.phone.trim() !== '') {
                const saudiPhoneRegex = /^(05|5)[0-9]{8}$/;
                const cleanPhone = data.phone.replace(/\s+/g, '');
                if (!saudiPhoneRegex.test(cleanPhone)) {
                    throw new Error('يرجى إدخال رقم جوال سعودي صحيح (مثال: 0551234567)');
                }
                data.phone = cleanPhone;
            }
            
            // Send data to server
            const response = await fetch('/api/survey', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Show success modal
                modal.style.display = 'block';
                
                // Reset form
                form.reset();
                
                // Reset all character counters
                textareas.forEach(({ counter }) => {
                    if (counter) {
                        counter.textContent = '0';
                        counter.classList.remove('warning', 'danger');
                    }
                });
                
                // Add success animation
                document.body.classList.add('success-submitted');
                
                // Track successful submission (optional analytics)
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'survey_submitted', {
                        'event_category': 'engagement',
                        'event_label': 'saudi_drive_survey_v2'
                    });
                }
                
            } else {
                throw new Error(result.error || 'حدث خطأ أثناء إرسال الاستبيان');
            }
            
        } catch (error) {
            // Show error message
            alert('خطأ: ' + error.message);
            console.error('Survey submission error:', error);
            
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-text">إرسال الاستبيان</span> <span class="btn-icon">🚀</span>';
        }
    });

    // Modal close functionality
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Add smooth scrolling for better UX
    function smoothScrollToElement(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }

    // Highlight required fields that are empty
    function highlightEmptyRequiredFields() {
        const requiredFields = form.querySelectorAll('[required]');
        let firstEmptyField = null;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                if (!firstEmptyField) {
                    firstEmptyField = field;
                }
            } else {
                field.classList.remove('error');
            }
        });
        
        if (firstEmptyField) {
            smoothScrollToElement(firstEmptyField);
            firstEmptyField.focus();
        }
        
        return !firstEmptyField;
    }

    // Remove error class when user starts typing
    form.addEventListener('input', function(e) {
        if (e.target.classList.contains('error')) {
            e.target.classList.remove('error');
        }
    });

    // Add interactive feedback for checkboxes
    const checkboxGroups = document.querySelectorAll('.checkbox-group');
    checkboxGroups.forEach(group => {
        const checkboxes = group.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const label = this.closest('.checkbox-label');
                if (this.checked) {
                    label.classList.add('checked');
                } else {
                    label.classList.remove('checked');
                }
            });
        });
    });

    // Add progress indicator (optional)
    function updateProgress() {
        const requiredFields = form.querySelectorAll('[required]');
        const filledFields = Array.from(requiredFields).filter(field => field.value.trim() !== '');
        const progress = (filledFields.length / requiredFields.length) * 100;
        
        // You can add a progress bar here if needed
        console.log(`Form completion: ${Math.round(progress)}%`);
    }

    // Update progress on form changes
    form.addEventListener('input', updateProgress);
    form.addEventListener('change', updateProgress);

    // Initialize character counters
    textareas.forEach(({ element }) => {
        if (element && element.value) {
            element.dispatchEvent(new Event('input'));
        }
    });

    // Add welcome animation
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);

    // Phone number formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, ''); // Remove non-digits
            
            // Format as Saudi phone number
            if (value.length > 0) {
                if (value.startsWith('966')) {
                    value = value.substring(3);
                }
                if (!value.startsWith('05') && !value.startsWith('5')) {
                    if (value.startsWith('5')) {
                        value = '0' + value;
                    }
                }
                if (value.length > 10) {
                    value = value.substring(0, 10);
                }
            }
            
            this.value = value;
        });
    }

    // Auto-expand textareas
    const autoExpandTextareas = document.querySelectorAll('textarea');
    autoExpandTextareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Add typing animation effect
    const textInputs = document.querySelectorAll('input[type="text"], input[type="tel"], textarea');
    textInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});

