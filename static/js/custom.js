/**
 * Custom JavaScript for Lead Management System
 * Includes animations, sidebar toggle, and other UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Constants
    const ANIMATION_DURATION = 300; // milliseconds
    
    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menu-toggle');
    const mainContent = document.querySelector('.main-content');
    const loadingOverlay = document.querySelector('.loading-overlay');
    const logoutButtons = document.querySelectorAll('.logout-btn');
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const dynamicContents = document.querySelectorAll('.dynamic-content');
    const punchInBtn = document.getElementById('punch-in-btn');
    const punchOutBtn = document.getElementById('punch-out-btn');
    
    // Initialize Bootstrap tooltips
    if (tooltipTriggerList.length) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Sidebar Toggle
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('full-width');
            
            // Store sidebar state in sessionStorage
            sessionStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
    
    // Restore sidebar state from sessionStorage
    if (sessionStorage.getItem('sidebarCollapsed') === 'true' && sidebar) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('full-width');
    }
    
    // Mobile Sidebar Toggle
    const handleResize = () => {
        if (window.innerWidth < 992 && sidebar) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('full-width');
        } else if (sessionStorage.getItem('sidebarCollapsed') !== 'true' && sidebar) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('full-width');
        }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize(); // Call once on load
    
    // Handle form submissions with loading overlay
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            // Don't show loading for search forms
            if (!this.querySelector('[type="search"]') && !this.classList.contains('no-loading')) {
                showLoading();
            }
        });
    });
    
    // Handle link clicks with loading overlay
    document.querySelectorAll('a').forEach(link => {
        // Skip links that should not trigger loading
        if (link.classList.contains('no-loading') || 
            link.getAttribute('href') === '#' || 
            link.getAttribute('href') === 'javascript:void(0)' ||
            link.getAttribute('target') === '_blank' ||
            link.getAttribute('role') === 'button' ||
            link.hasAttribute('data-bs-toggle')) {
            return;
        }
        
        link.addEventListener('click', function(e) {
            // Check if the link is not an internal anchor
            if (this.getAttribute('href') && !this.getAttribute('href').startsWith('#')) {
                showLoading();
            }
        });
    });
    
    // Show loading overlay
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.add('show');
            setTimeout(() => {
                // Safety timeout to hide overlay if page doesn't change
                loadingOverlay.classList.remove('show');
            }, 8000);
        }
    }
    
    // Hide loading overlay
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
        }
    }
    
    // Hide loading overlay when page is fully loaded
    window.addEventListener('load', hideLoading);
    
    // Add confirmation dialog to logout button
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    });
    
    // Punch-in button confirmation
    if (punchInBtn) {
        punchInBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to punch in now?')) {
                e.preventDefault();
            } else {
                showLoading();
            }
        });
    }
    
    // Punch-out button confirmation
    if (punchOutBtn) {
        punchOutBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to punch out now?')) {
                e.preventDefault();
            } else {
                showLoading();
            }
        });
    }
    
    // Animation for success messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Add close functionality to alerts
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                const alertElement = this.closest('.alert');
                alertElement.classList.add('animate__fadeOut');
                setTimeout(() => {
                    alertElement.remove();
                }, 500);
            });
        }
        
        // Auto-close success alerts after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.classList.add('animate__fadeOut');
                setTimeout(() => {
                    alert.remove();
                }, 500);
            }, 5000);
        }
    });
    
    // Scroll reveal animation for dynamic content
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    dynamicContents.forEach(content => {
        observer.observe(content);
    });
    
    // Enhance table interactions
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            // Add hover class for better interaction
            row.addEventListener('mouseenter', function() {
                this.classList.add('highlight-row');
            });
            
            row.addEventListener('mouseleave', function() {
                this.classList.remove('highlight-row');
            });
            
            // Apply staggered animation delay for rows
            row.style.animationDelay = `${index * 50}ms`;
        });
    });
    
    // Dynamic date pickers enhancement
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(picker => {
        picker.addEventListener('focus', function() {
            this.classList.add('date-active');
        });
        
        picker.addEventListener('blur', function() {
            this.classList.remove('date-active');
        });
    });
    
    // Enhance dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(dropdown => {
        const items = dropdown.querySelectorAll('.dropdown-item');
        items.forEach((item, index) => {
            item.style.animationDelay = `${index * 50}ms`;
            item.classList.add('animate__animated', 'animate__fadeIn');
        });
    });
    
    // Add active class to current nav item based on URL
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#sidebar .list-group-item');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
    
    // Handle password visibility toggle
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.classList.add('btn', 'btn-outline-secondary', 'password-toggle');
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.top = '50%';
        toggleBtn.style.transform = 'translateY(-50%)';
        toggleBtn.style.zIndex = '10';
        
        // Add toggle functionality
        toggleBtn.addEventListener('click', function() {
            const type = field.getAttribute('type') === 'password' ? 'text' : 'password';
            field.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
        
        // Add toggle button to field container
        if (field.parentNode.style.position !== 'relative') {
            field.parentNode.style.position = 'relative';
        }
        field.parentNode.appendChild(toggleBtn);
    });
});

/**
 * Form validation enhancement
 * Adds custom validation styles and messages
 */
(function() {
    'use strict';
    
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find the first invalid field and focus it
                const invalidField = form.querySelector(':invalid');
                if (invalidField) {
                    invalidField.focus();
                    
                    // Scroll to the invalid field
                    invalidField.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });
})();

/**
 * Custom toast notification system
 * Creates and shows toast notifications
 */
const Toast = {
    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '11';
            document.body.appendChild(toastContainer);
        }
    },
    
    show(message, type = 'info', duration = 5000) {
        this.init();
        const container = document.getElementById('toast-container');
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast show animate__animated animate__fadeInUp bg-dark text-light border border-${type}`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Set appropriate icon based on type
        let icon;
        switch (type) {
            case 'success':
                icon = 'fa-check-circle text-success';
                break;
            case 'danger':
                icon = 'fa-exclamation-circle text-danger';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle text-warning';
                break;
            default:
                icon = 'fa-info-circle text-info';
        }
        
        // Set toast content
        toast.innerHTML = `
            <div class="toast-header bg-dark text-light border-bottom border-${type}">
                <i class="fas ${icon} me-2"></i>
                <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <small>Just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        // Add toast to container
        container.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.classList.remove('animate__fadeInUp');
                toastElement.classList.add('animate__fadeOutDown');
                setTimeout(() => {
                    if (toastElement.parentNode) {
                        toastElement.parentNode.removeChild(toastElement);
                    }
                }, 500);
            }
        }, duration);
        
        // Add close button functionality
        const closeButton = toast.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                const toastElement = document.getElementById(toastId);
                if (toastElement) {
                    toastElement.classList.remove('animate__fadeInUp');
                    toastElement.classList.add('animate__fadeOutDown');
                    setTimeout(() => {
                        if (toastElement.parentNode) {
                            toastElement.parentNode.removeChild(toastElement);
                        }
                    }, 500);
                }
            });
        }
    }
};

/**
 * Handle dark theme consistently
 * Ensures dark theme is applied on all pages
 */
function applyDarkTheme() {
    document.body.classList.add('bg-dark', 'text-light');
    
    // Ensure tables are dark themed
    document.querySelectorAll('table').forEach(table => {
        table.classList.add('table-dark');
    });
    
    // Ensure cards have dark background
    document.querySelectorAll('.card').forEach(card => {
        if (!card.classList.contains('bg-dark')) {
            card.classList.add('bg-dark');
        }
        card.classList.add('text-light');
    });
}

// Apply dark theme when document is ready
document.addEventListener('DOMContentLoaded', applyDarkTheme);
