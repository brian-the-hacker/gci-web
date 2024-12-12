// Function to animate elements using GSAP
function animateElements() {
    // Hero Section Animation
    gsap.from(".hero-content h1", { opacity: 0, y: 50, duration: 1 });
    gsap.from(".hero-content p", { opacity: 0, y: 50, duration: 1.2, delay: 0.3 });
    gsap.from(".hero-content .btn", { opacity: 0, y: 50, duration: 1.4, delay: 0.6 });

    // Events Section Animation
    gsap.from(".event-card", { opacity: 0, y: 50, stagger: 0.2 });

    // Sermons Section Animation
    gsap.from(".sermon-card", { opacity: 0, y: 50, stagger: 0.2 });

    // News Section Animation
    gsap.from(".news-card", { opacity: 0, y: 50, stagger: 0.2 });

    // Social Icons Animation
    gsap.from(".social-icons a", { opacity: 0, scale: 0.8, stagger: 0.2, duration: 0.6 });

    // Button Hover Effect
    gsap.to(".btn", { scale: 1.1, duration: 0.3, ease: "power1.inOut", paused: true });
}

// Initial animation on page load
animateElements();

// Function to animate elements every 10 seconds
setInterval(function() {
    animateElements();
}, 10000);

// Hover effect for buttons
document.querySelectorAll(".btn").forEach(btn => {
    btn.addEventListener("mouseenter", function() {
        gsap.to(this, { scale: 1.1 });
    });
    btn.addEventListener("mouseleave", function() {
        gsap.to(this, { scale: 1 });
    });
});

// Hover effect for social icons
document.querySelectorAll(".social-icons a").forEach(icon => {
    icon.addEventListener("mouseenter", function() {
        gsap.to(this, { scale: 1.2 });
    });
    icon.addEventListener("mouseleave", function() {
        gsap.to(this, { scale: 1 });
    });
});
