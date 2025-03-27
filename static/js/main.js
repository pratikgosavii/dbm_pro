/*
 * Main JavaScript for Lead Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add animation classes to message alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert, index) {
        alert.classList.add('animate__animated', 'animate__fadeInDown');
        alert.style.animationDelay = (index * 0.2) + 's';
    });
    
    // Handle sidebar toggles on mobile
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
    
    // Add fade animations to all page transitions
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        // Check if it's a link (or inside a link) that isn't an external link or specifically excluded
        if (target.tagName === 'A' || target.closest('a')) {
            const link = target.tagName === 'A' ? target : target.closest('a');
            
            // Skip if it's an external link, has a target, or is marked to skip animation
            if (link.getAttribute('href').startsWith('http') || 
                link.getAttribute('target') ||
                link.classList.contains('no-animation') ||
                link.getAttribute('href') === '#' ||
                link.getAttribute('data-bs-toggle')) {
                return;
            }
            
            // Prevent default navigation
            e.preventDefault();
            
            // Animate out
            document.body.classList.add('animate__animated', 'animate__fadeOut', 'animate__faster');
            
            // After animation completes, navigate to the link
            setTimeout(function() {
                window.location.href = link.getAttribute('href');
            }, 400);
        }
    });
    
    // Add chart JS helpers
    if (window.Chart) {
        // Set defaults for all charts
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.scale.ticks.padding = 10;
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.elements.point.radius = 4;
        Chart.defaults.elements.point.hoverRadius = 6;
        Chart.defaults.elements.line.tension = 0.3;
    }
    
    // Add date picker on date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.classList.add('active-date-input');
        });
        input.addEventListener('blur', function() {
            this.classList.remove('active-date-input');
        });
    });
    
    // Add animations to tables on load
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(function(row, index) {
        row.style.animationDelay = (index * 0.05) + 's';
    });
    
    // Handle task status updates with animation
    const statusSelects = document.querySelectorAll('select[id*="status"]');
    statusSelects.forEach(function(select) {
        const originalValue = select.value;
        
        select.addEventListener('change', function() {
            const newValue = this.value;
            const row = this.closest('tr');
            
            if (row) {
                if (newValue === 'done') {
                    row.classList.add('animate__animated', 'animate__fadeOutRight');
                    setTimeout(function() {
                        row.classList.remove('animate__animated', 'animate__fadeOutRight');
                    }, 1000);
                } else if (originalValue === 'done' && newValue !== 'done') {
                    row.classList.add('animate__animated', 'animate__headShake');
                    setTimeout(function() {
                        row.classList.remove('animate__animated', 'animate__headShake');
                    }, 1000);
                }
            }
        });
    });
    
    // Handle form submissions with animations
    const forms = document.querySelectorAll('form:not(.no-animation)');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('animate__animated', 'animate__pulse');
                submitBtn.disabled = true;
                
                // Add spinner to button
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + 
                                     'Processing...';
                                     
                // Re-enable after timeout (in case of form validation error)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                    submitBtn.classList.remove('animate__animated', 'animate__pulse');
                }, 3000);
            }
        });
    });
    
    // Add focus animation for search inputs
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.classList.add('animate__animated', 'animate__pulse');
            this.parentNode.classList.add('focused-search');
        });
        input.addEventListener('blur', function() {
            this.classList.remove('animate__animated', 'animate__pulse');
            this.parentNode.classList.remove('focused-search');
        });
    });
    
    // Handle card interactions
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        // Add subtle hover effect
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });
    
    // Dashboard metric cards counter animation
    const metricValues = document.querySelectorAll('.metric-value');
    metricValues.forEach(function(value) {
        const finalValue = value.textContent;
        
        // Check if it's a number or currency
        if (/^[$€£¥]?\d+([,.]\d+)?$/.test(finalValue.trim())) {
            let startValue = 0;
            const currency = finalValue.match(/^[$€£¥]/);
            const cleanValue = finalValue.replace(/[$€£¥,]/g, '');
            const decimalValue = parseFloat(cleanValue);
            const hasDecimal = finalValue.includes('.') || finalValue.includes(',');
            
            // Animate counter from 0 to final value
            const duration = 1500;
            const frameRate = 30;
            const totalFrames = duration * frameRate / 1000;
            let currentFrame = 0;
            
            const prefix = currency ? currency[0] : '';
            const decimals = hasDecimal ? 2 : 0;
            
            const animate = function() {
                if (currentFrame <= totalFrames) {
                    const progress = currentFrame / totalFrames;
                    // Easing function for smoother animation
                    const easedProgress = 1 - Math.pow(1 - progress, 3);
                    const currentValue = easedProgress * decimalValue;
                    
                    value.textContent = prefix + currentValue.toFixed(decimals);
                    currentFrame++;
                    requestAnimationFrame(animate);
                } else {
                    value.textContent = finalValue; // Ensure final value is exact
                }
            };
            
            // Only animate if the element is visible in viewport
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animate();
                        observer.disconnect();
                    }
                });
            }, { threshold: 0.1 });
            
            observer.observe(value);
        }
    });
    
    // Initialize custom dropdown selects
    const selects = document.querySelectorAll('select.form-control');
    selects.forEach(function(select) {
        // Add focus effect
        select.addEventListener('focus', function() {
            this.parentNode.classList.add('select-focused');
        });
        select.addEventListener('blur', function() {
            this.parentNode.classList.remove('select-focused');
        });
    });
    
    // Conditional form fields visibility
    const conditionalSelects = document.querySelectorAll('[data-toggle-fields]');
    conditionalSelects.forEach(function(select) {
        const updateVisibility = function() {
            const selectedValue = select.value;
            const toggleFields = JSON.parse(select.getAttribute('data-toggle-fields'));
            
            Object.keys(toggleFields).forEach(function(value) {
                const fieldsToToggle = toggleFields[value];
                fieldsToToggle.forEach(function(fieldId) {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        const fieldContainer = field.closest('.mb-3') || field.closest('.form-group');
                        if (fieldContainer) {
                            if (selectedValue === value) {
                                fieldContainer.style.display = 'block';
                                field.classList.add('animate__animated', 'animate__fadeIn');
                            } else {
                                fieldContainer.style.display = 'none';
                            }
                        }
                    }
                });
            });
        };
        
        // Initial update
        updateVisibility();
        
        // Update on change
        select.addEventListener('change', updateVisibility);
    });
    
    // Add animation for unread badges/notifications
    const unreadBadges = document.querySelectorAll('.badge.unread');
    unreadBadges.forEach(function(badge) {
        badge.classList.add('animate__animated', 'animate__pulse', 'animate__infinite');
    });
    
    // Add click-to-copy functionality for shareable items
    const copyableItems = document.querySelectorAll('.copyable');
    copyableItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy') || this.textContent;
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Show tooltip or feedback
                const originalTitle = item.getAttribute('title');
                item.setAttribute('title', 'Copied!');
                
                // If using Bootstrap tooltips
                const tooltip = bootstrap.Tooltip.getInstance(item);
                if (tooltip) {
                    tooltip.hide();
                    tooltip.show();
                }
                
                setTimeout(function() {
                    item.setAttribute('title', originalTitle);
                }, 1000);
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
            });
        });
        
        // Add visual indicator that it's copyable
        item.classList.add('cursor-pointer');
        if (!item.querySelector('.copy-icon')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-copy copy-icon ms-1';
            icon.style.fontSize = '0.8em';
            item.appendChild(icon);
        }
    });
    
    // Add progress bars animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const percentage = bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = percentage;
        }, 100);
    });
    
    // Theme toggle (if implemented)
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            document.body.classList.toggle('dark-theme');
            
            // Save preference
            const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
            localStorage.setItem('theme', currentTheme);
        });
    }
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        } else {
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        }
    }
    
    // Sticky headers in tables with many rows
    const largeTables = document.querySelectorAll('.table-sticky-header');
    largeTables.forEach(function(table) {
        const header = table.querySelector('thead');
        if (header) {
            header.classList.add('sticky-header');
        }
    });
    
    // Add loading indicators for dynamic content
    const dynamicContainers = document.querySelectorAll('[data-dynamic-content]');
    dynamicContainers.forEach(function(container) {
        // Show loading spinner
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading content...</p>
            </div>
        `;
        
        // Fetch content (in real implementation)
        // For now, just simulate loading
        setTimeout(function() {
            container.classList.add('animate__animated', 'animate__fadeIn');
            container.innerHTML = '<div class="p-4 text-center">Content loaded successfully</div>';
        }, 1500);
    });
    
    // Handle "Remember Me" checkbox in login
    const rememberCheckbox = document.getElementById('remember-me');
    if (rememberCheckbox) {
        // Check if we have a saved username
        const savedUsername = localStorage.getItem('rememberedUsername');
        const usernameField = document.getElementById('id_username');
        
        if (savedUsername && usernameField) {
            usernameField.value = savedUsername;
            rememberCheckbox.checked = true;
        }
        
        // Handle saving on form submit
        const loginForm = rememberCheckbox.closest('form');
        if (loginForm) {
            loginForm.addEventListener('submit', function() {
                if (rememberCheckbox.checked && usernameField) {
                    localStorage.setItem('rememberedUsername', usernameField.value);
                } else {
                    localStorage.removeItem('rememberedUsername');
                }
            });
        }
    }
});

/**
 * Format a number as currency
 */
function formatCurrency(amount, currency = '$') {
    return currency + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Format a date string to a more readable format
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Format a datetime string including time
 */
function formatDateTime(dateTimeString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateTimeString).toLocaleString(undefined, options);
}

/**
 * Calculate time ago string (e.g., "2 hours ago")
 */
function timeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const secondsAgo = Math.floor((now - date) / 1000);
    
    if (secondsAgo < 60) return 'Just now';
    if (secondsAgo < 3600) return Math.floor(secondsAgo / 60) + ' minutes ago';
    if (secondsAgo < 86400) return Math.floor(secondsAgo / 3600) + ' hours ago';
    if (secondsAgo < 2592000) return Math.floor(secondsAgo / 86400) + ' days ago';
    if (secondsAgo < 31536000) return Math.floor(secondsAgo / 2592000) + ' months ago';
    
    return Math.floor(secondsAgo / 31536000) + ' years ago';
}

/**
 * Truncate text with ellipsis
 */
function truncateText(text, maxLength = 50) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

/**
 * Confirm deletion with custom dialog
 */
function confirmDelete(event, message = 'Are you sure you want to delete this item?') {
    if (!confirm(message)) {
        event.preventDefault();
        return false;
    }
    return true;
}

/**
 * Parse URL parameters
 */
function getUrlParams() {
    const params = {};
    new URLSearchParams(window.location.search).forEach((value, key) => {
        params[key] = value;
    });
    return params;
}

/**
 * Add form validation highlighting
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            field.classList.add('animate__animated', 'animate__headShake');
            
            // Remove animation after it completes
            setTimeout(() => {
                field.classList.remove('animate__animated', 'animate__headShake');
            }, 1000);
            
            isValid = false;
            
            // Add invalid feedback if not present
            const parent = field.parentNode;
            if (!parent.querySelector('.invalid-feedback')) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'This field is required.';
                parent.appendChild(feedback);
            }
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Toggle password visibility in form
 */
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (passwordInput && icon) {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
        
        // Focus back on input
        passwordInput.focus();
    }
}

/**
 * Create and show a toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + new Date().getTime();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 animate__animated animate__fadeInRight`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    // Clean up after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}
