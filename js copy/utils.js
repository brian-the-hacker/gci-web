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

    // Button Hover Effect
    gsap.to(".btn", { scale: 1.1, duration: 0.3, ease: "power1.inOut", paused: true });
}

// Initial animation on page load


// Function to animate elements every 10 seconds
setInterval(function() {
    animateElements();
}, 10000);

// Pause animations when tab is not visible
document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === "hidden") {
        gsap.globalTimeline.resume()();
    } else {
        gsap.globalTimeline.resume();
    }
});


// Hover effect for buttons
document.querySelectorAll(".btn").forEach(btn => {
    btn.addEventListener("mouseenter", function() {
        gsap.to(this, { scale: 1.1 });
    });
    btn.addEventListener("mouseleave", function() {
        gsap.to(this, { scale: 1 });
    });
});

const accordionButtons = document.querySelectorAll('.accordion-button');
        
        accordionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const content = button.nextElementSibling;

                button.classList.toggle('active');

                if (button.classList.contains('active')) {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        });


    
        window.onscroll = function() {scrollFunction()};

        function scrollFunction() {
            const backToTopBtn = document.getElementById("backToTopBtn");
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                backToTopBtn.style.display = "block";
            } else {
                backToTopBtn.style.display = "none";
            }
        }
    
        // When the user clicks on the button, scroll to the top of the document
        function topFunction() {
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        }
    
        document.getElementById("backToTopBtn").addEventListener("click", topFunction);