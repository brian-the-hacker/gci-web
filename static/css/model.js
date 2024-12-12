document.getElementById('contactBtn').addEventListener('click', function() {
    document.getElementById('contactModal').style.display = 'block';
});

document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('contactModal').style.display = 'none';
});

// Close the modal when clicking outside the modal content
window.onclick = function(event) {
    if (event.target == document.getElementById('contactModal')) {
        document.getElementById('contactModal').style.display = 'none';
    }
};



// Mobile menu toggle
const mobileMenu = document.querySelector('.mobile-menu');
const navLinks = document.querySelector('.nav-links');

mobileMenu?.addEventListener('click', () => {
    navLinks?.classList.toggle('active');
});

// Hero slider
const slides = document.querySelectorAll('.slide');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');
let currentSlide = 0;

function showSlide(n) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[n].classList.add('active');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
}

prevBtn?.addEventListener('click', prevSlide);
nextBtn?.addEventListener('click', nextSlide);

// Auto slide
setInterval(nextSlide, 5000);

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            // Close mobile menu if open
            navLinks?.classList.remove('active');
        }
    });
});

// Form submissions
const contactForm = document.getElementById('contact-form');
const newsletterForm = document.getElementById('newsletter-form');
const newsletterMessage = document.getElementById('newsletter-message');

contactForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    form.querySelector('button').disabled = true;
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    alert('Message sent successfully!');
    form.reset();
    form.querySelector('button').disabled = false;
});

newsletterForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    form.querySelector('button').disabled = true;
    
    // Simulate newsletter subscription
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (newsletterMessage) {
        newsletterMessage.textContent = 'Thank you for subscribing!';
        newsletterMessage.style.color = '#4caf50';
    }
    
    form.reset();
    form.querySelector('button').disabled = false;
    
    // Clear success message after 3 seconds
    setTimeout(() => {
        if (newsletterMessage) {
            newsletterMessage.textContent = '';
        }
    }, 3000);
});