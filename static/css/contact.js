// Import AOS
import AOS from 'aos';

// Initialize AOS
AOS.init({
  duration: 800,
  easing: 'ease-in-out',
  once: true
});

// Mobile Menu Functionality
document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      mobileMenuBtn.classList.toggle('active');
    });
  }

  // Contact Form Functionality
  const form = document.getElementById('contactForm');
  const formMessages = document.getElementById('formMessages');

  if (form) {
    // Add floating label functionality
    const formFields = document.querySelectorAll('.form-field input, .form-field textarea');
    formFields.forEach(field => {
      field.addEventListener('focus', () => {
        field.parentElement.classList.add('focused');
      });

      field.addEventListener('blur', () => {
        if (!field.value) {
          field.parentElement.classList.remove('focused');
        }
      });
    });

    // Form submission handling
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      const submitBtn = form.querySelector('.submit-btn');
      const btnText = submitBtn.querySelector('.btn-text');
      const originalBtnText = btnText.textContent;

      try {
        // Show loading state
        btnText.textContent = 'Sending...';
        submitBtn.disabled = true;

        // Simulate form submission (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Show success message
        formMessages.innerHTML = `
          <div class="success-message">
            <i class="fas fa-check-circle"></i>
            Message sent successfully! We'll get back to you soon.
          </div>
        `;

        // Reset form
        form.reset();
        formFields.forEach(field => {
          field.parentElement.classList.remove('focused');
        });

      } catch (error) {
        // Show error message
        formMessages.innerHTML = `
          <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            Oops! Something went wrong. Please try again later.
          </div>
        `;
      } finally {
        // Reset button state
        btnText.textContent = originalBtnText;
        submitBtn.disabled = false;
      }
    });
  }

  // Newsletter Form Functionality
  const newsletterForm = document.getElementById('newsletterForm');

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const emailInput = this.querySelector('input[type="email"]');
      const submitBtn = this.querySelector('button');
      const originalBtnText = submitBtn.textContent;

      try {
        // Show loading state
        submitBtn.textContent = 'Subscribing...';
        submitBtn.disabled = true;

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Show success message
        alert('Thank you for subscribing to our newsletter!');
        
        // Reset form
        emailInput.value = '';

      } catch (error) {
        alert('Failed to subscribe. Please try again later.');
      } finally {
        // Reset button state
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
      }
    });
  }
});