/**
 * Animation utilities for Lead Management System
 */

// Add fade-in animation to elements
function fadeIn(element, duration = 500) {
    element.style.opacity = 0;
    element.style.display = 'block';
    
    let opacity = 0;
    const interval = 10;
    const steps = duration / interval;
    const increment = 1 / steps;
    
    const timer = setInterval(() => {
        opacity += increment;
        element.style.opacity = opacity;
        
        if (opacity >= 1) {
            clearInterval(timer);
        }
    }, interval);
}

// Add fade-out animation to elements
function fadeOut(element, duration = 500) {
    let opacity = 1;
    const interval = 10;
    const steps = duration / interval;
    const decrement = 1 / steps;
    
    const timer = setInterval(() => {
        opacity -= decrement;
        element.style.opacity = opacity;
        
        if (opacity <= 0) {
            element.style.display = 'none';
            clearInterval(timer);
        }
    }, interval);
}

// Add slide-down animation to elements
function slideDown(element, duration = 500) {
    element.style.height = '0';
    element.style.overflow = 'hidden';
    element.style.display = 'block';
    element.style.transition = `height ${duration}ms ease`;
    
    setTimeout(() => {
        element.style.height = element.scrollHeight + 'px';
    }, 10);
    
    setTimeout(() => {
        element.style.height = 'auto';
    }, duration);
}

// Add slide-up animation to elements
function slideUp(element, duration = 500) {
    element.style.height = element.offsetHeight + 'px';
    element.style.overflow = 'hidden';
    element.style.transition = `height ${duration}ms ease`;
    
    setTimeout(() => {
        element.style.height = '0';
    }, 10);
    
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// Add pulse animation to elements
function pulse(element, duration = 500) {
    element.classList.add('animate-pulse');
    
    setTimeout(() => {
        element.classList.remove('animate-pulse');
    }, duration);
}

// Add bounce animation to elements
function bounce(element, duration = 500) {
    element.classList.add('animate-bounce');
    
    setTimeout(() => {
        element.classList.remove('animate-bounce');
    }, duration);
}

// Add page transition animations
function pageTransition() {
    const content = document.querySelector('.content-wrapper');
    content.classList.add('page-transition');
    
    setTimeout(() => {
        content.classList.remove('page-transition');
    }, 300);
}

// Initialize animation observers
function initAnimationObservers() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animationType = entry.target.getAttribute('data-animation') || 'fade-in';
                entry.target.classList.add(animationType);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

// Add smooth scrolling to elements
function smoothScroll(target, duration = 500) {
    const targetElement = document.querySelector(target);
    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        const ease = easeInOutQuad(progress);
        
        window.scrollTo(0, startPosition + distance * ease);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }
    
    requestAnimationFrame(animation);
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements with data-animation attribute
    const animatedElements = document.querySelectorAll('[data-animation]');
    animatedElements.forEach(element => {
        const animationType = element.getAttribute('data-animation');
        element.classList.add(animationType);
    });
    
    // Initialize scroll animations
    initAnimationObservers();
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add animation to alert messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('slide-in');
        
        // Auto dismiss alerts after 5 seconds
        setTimeout(() => {
            fadeOut(alert);
        }, 5000);
    });
    
    // Add animation to modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const modalDialog = modal.querySelector('.modal-dialog');
            modalDialog.classList.add('scale-in');
        });
        
        modal.addEventListener('hide.bs.modal', function() {
            const modalDialog = modal.querySelector('.modal-dialog');
            modalDialog.classList.add('scale-out');
        });
    });
});

// CSS Animation classes
document.head.insertAdjacentHTML('beforeend', `
<style>
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease forwards;
    }
    
    .scale-in {
        animation: scaleIn 0.3s ease forwards;
    }
    
    .scale-out {
        animation: scaleOut 0.3s ease forwards;
    }
    
    .animate-pulse {
        animation: pulse 0.5s ease;
    }
    
    .animate-bounce {
        animation: bounce 0.5s ease;
    }
    
    .page-transition {
        animation: pageTransition 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    @keyframes scaleOut {
        from { transform: scale(1); opacity: 1; }
        to { transform: scale(0.9); opacity: 0; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pageTransition {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
`);
