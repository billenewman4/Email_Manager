// Handle popup content
const popupModal = document.getElementById('popupModal');
if (popupModal) {
    popupModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const section = button.getAttribute('data-section');
        const modalTitle = popupModal.querySelector('.modal-title');

        switch (section) {
            case 'get-started':
            case 'free-trial':
                modalTitle.textContent = 'Start Your Free Trial';
                break;
            default:
                modalTitle.textContent = 'Join NetworkPro';
        }
    });
}

// Form validation and submission
const emailForm = document.getElementById('emailForm');
const emailInput = document.getElementById('email');
const successMessage = document.getElementById('successMessage');

if (emailForm) {
    emailForm.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!emailInput.checkValidity()) {
            emailInput.classList.add('is-invalid');
        } else {
            emailInput.classList.remove('is-invalid');
            submitEmail();
        }
    });
}

function submitEmail() {
    // Validate required fields before submission
    const requiredFields = ['email', 'firstName', 'lastName'];
    let hasError = false;
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            hasError = true;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    if (hasError) {
        return;
    }

    const formData = {
        email: emailInput.value.trim(),
        first_name: document.getElementById('firstName').value.trim(),
        last_name: document.getElementById('lastName').value.trim(),
        company: document.getElementById('company').value.trim(),
        job_title: document.getElementById('jobTitle').value.trim(),
        linkedin_url: document.getElementById('linkedinUrl').value.trim()
    };

    // Show loading state
    const submitButton = emailForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';

    fetch('/submit-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            emailForm.reset();
            emailForm.style.display = 'none';
            successMessage.textContent = 'Thanks for signing up! We will be in touch shortly.';
            successMessage.style.display = 'block';
        } else {
            throw new Error(data.message || 'An error occurred. Please try again.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger mt-3';
        errorMessage.textContent = error.message || 'An error occurred. Please try again.';
        emailForm.appendChild(errorMessage);
        setTimeout(() => errorMessage.remove(), 5000);
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    });
}

// Add animation to elements on scroll
const animateOnScroll = (entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate__animated', 'animate__fadeInUp');
            observer.unobserve(entry.target);
        }
    });
};

const scrollObserver = new IntersectionObserver(animateOnScroll, {
    root: null,
    threshold: 0.1
});

document.querySelectorAll('.card, h2, .btn-lg').forEach(element => {
    scrollObserver.observe(element);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Add hover effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    });
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = 'none';
    });
});

// Reset modal content when it's closed
if (popupModal) {
    popupModal.addEventListener('hidden.bs.modal', function () {
        if (emailForm && successMessage) {
            emailForm.reset();
            emailForm.style.display = 'block';
            successMessage.style.display = 'none';
        }
    });
}

