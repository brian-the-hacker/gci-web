// Main JavaScript file
import { initCarousel } from './carousel.js';
import { initNavigation } from './navigation.js';
import { initBackToTop } from './backToTop.js';
import { initContactForm } from './contactForm.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    initNavigation();
    initCarousel();
    initBackToTop();
    initContactForm();

    // Handle smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Handle service worker registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}


// Carousel functionality
export function initCarousel() {
    const carousel = document.querySelector('.carousel');
    if (!carousel) return;

    const items = carousel.querySelector('.carousel-items');
    const prevBtn = carousel.querySelector('.prev-btn');
    const nextBtn = carousel.querySelector('.next-btn');
    const indicators = carousel.querySelector('.carousel-indicators');

    let currentIndex = 0;
    let isTransitioning = false;
    const autoPlayDelay = 5000;
    let autoPlayTimer;

    // Initialize carousel
    function init() {
        // Create indicators
        items.querySelectorAll('.carousel-item').forEach((_, index) => {
            const dot = document.createElement('button');
            dot.classList.add('carousel-indicator');
            dot.setAttribute('aria-label', `Slide ${index + 1}`);
            dot.addEventListener('click', () => goToSlide(index));
            indicators.appendChild(dot);
        });

        updateCarousel();
        startAutoPlay();
    }

    // Navigation functions
    function goToSlide(index) {
        if (isTransitioning || index === currentIndex) return;

        isTransitioning = true;
        items.style.transform = `translateX(-${index * 100}%)`;
        currentIndex = index;
        updateCarousel();

        setTimeout(() => {
            isTransitioning = false;
        }, 500);
    }

    function nextSlide() {
        const nextIndex = (currentIndex + 1) % items.children.length;
        goToSlide(nextIndex);
    }

    function prevSlide() {
        const prevIndex = (currentIndex - 1 + items.children.length) % items.children.length;
        goToSlide(prevIndex);
    }

    // Update carousel state
    function updateCarousel() {
        // Update indicators
        indicators.querySelectorAll('.carousel-indicator').forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });

        // Update ARIA labels
        items.querySelectorAll('.carousel-item').forEach((item, index) => {
            item.setAttribute('aria-hidden', index !== currentIndex);
        });
    }

    // Auto play functions
    function startAutoPlay() {
        stopAutoPlay();
        autoPlayTimer = setInterval(nextSlide, autoPlayDelay);
    }

    function stopAutoPlay() {
        if (autoPlayTimer) {
            clearInterval(autoPlayTimer);
        }
    }

    // Event listeners
    prevBtn.addEventListener('click', () => {
        prevSlide();
        stopAutoPlay();
    });

    nextBtn.addEventListener('click', () => {
        nextSlide();
        stopAutoPlay();
    });

    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);

    // Touch support
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    carousel.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                nextSlide();
            } else {
                prevSlide();
            }
        }
    }

    // Initialize carousel
    init();
}

// Navigation functionality
export function initNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const header = document.querySelector('.header');

    if (!navToggle || !navLinks || !header) return;

    // Toggle mobile menu
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('show');
        navToggle.classList.toggle('active');
        header.classList.toggle('nav-open');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!header.contains(e.target) && navLinks.classList.contains('show')) {
            navLinks.classList.remove('show');
            navToggle.classList.remove('active');
            header.classList.remove('nav-open');
        }
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 768 && navLinks.classList.contains('show')) {
                navLinks.classList.remove('show');
                navToggle.classList.remove('active');
                header.classList.remove('nav-open');
            }
        }, 250);
    });

    // Add scroll behavior
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
    });
}




//step 1: get DOM

let nextDom = document.getElementById('next');
let prevDom = document.getElementById('prev');

let carouselDom = document.querySelector('.carousel');
let SliderDom = carouselDom.querySelector('.carousel .list');
let thumbnailBorderDom = document.querySelector('.carousel .thumbnail');
let thumbnailItemsDom = thumbnailBorderDom.querySelectorAll('.item');
let timeDom = document.querySelector('.carousel .time');

thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
let timeRunning = 3000;
let timeAutoNext = 10000;

nextDom.onclick = function(){
    showSlider('next');    
}

prevDom.onclick = function(){
    showSlider('prev');    
}
let runTimeOut;
let runNextAuto = setTimeout(() => {
    next.click();
}, timeAutoNext)
function showSlider(type){
    let  SliderItemsDom = SliderDom.querySelectorAll('.carousel .list .item');
    let thumbnailItemsDom = document.querySelectorAll('.carousel .thumbnail .item');
    
    if(type === 'next'){
        SliderDom.appendChild(SliderItemsDom[0]);
        thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
        carouselDom.classList.add('next');
    }else{
        SliderDom.prepend(SliderItemsDom[SliderItemsDom.length - 1]);
        thumbnailBorderDom.prepend(thumbnailItemsDom[thumbnailItemsDom.length - 1]);
        carouselDom.classList.add('prev');
    }
    clearTimeout(runTimeOut);
    runTimeOut = setTimeout(() => {
        carouselDom.classList.remove('next');
        carouselDom.classList.remove('prev');
    }, timeRunning);

    clearTimeout(runNextAuto);
    runNextAuto = setTimeout(() => {
        next.click();
    }, timeAutoNext)
}
$(document).ready(function() {
    $('#contact-form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Collect form data
        var formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'), // URL to submit the form data
            type: 'POST',
            data: formData,
            success: function(response) {
                console.log('Form submitted successfully:', response);

                // Assuming the response has a message field
                var message = response.message || 'Message sent successfully! Thank you for contacting Gospel Centers International Machakos..';
                
                // Hide the form
                $('#contact-form').hide();

                // Display success message
                $('.flash-messages').html('<ul class="flashes"><li class="success">' + message + '</li></ul>');
            },
            error: function(xhr, status, error) {
                console.error('Form submission failed:', status, error);

                // Display error message
                $('.flash-messages').html('<ul class="flashes"><li class="error">Failed to send the message. Please try again later.</li></ul>');
            }
        });
    });
});
