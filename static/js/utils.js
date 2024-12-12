// Function to animate elements using GSAP
function animateElements() {
    // Hero Section Animation
    gsap.from(".hero-content h1", { opacity: 1, y: 50, duration: 1 });
    gsap.from(".hero-content p", { opacity:1, y: 50, duration: 1.2, delay: 0.3 });
    gsap.from(".hero-content .btn", { opacity: 1, y: 50, duration: 1.4, delay: 0.6 });

    // Events Section Animation
    gsap.from(".event-card", { opacity: 1, y: 50, stagger: 0.2 });

    // Sermons Section Animation
    gsap.from(".sermon-card", { opacity:1, y: 50, stagger: 0.2 });

    // News Section Animation
    gsap.from(".news-card", { opacity:1, y: 50, stagger: 0.2 });

    // Button Hover Effect
    gsap.to(".btn", { scale: 1.1, duration: 0.3, ease: "power1.inOut", paused: true });
}

// Initial animation on page load
animateElements();

// Function to animate elements every 10 seconds
setInterval(function() {
    animateElements();
}, 10000);

// Track if the global timeline was paused
let wasPaused = false;

// Visibility change event handler
document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === "hidden") {
        // Save the paused state of the global timeline
        wasPaused = gsap.globalTimeline.paused();
        // Pause the timeline explicitly if needed
        gsap.globalTimeline.pause();
    } else if (document.visibilityState === "visible") {
        // Restart animations if the timeline was paused
        if (wasPaused) {
            gsap.globalTimeline.resume();
            animateElements(); // Optionally, re-run animations
        }
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


setTimeout(function() {
    var flashes = document.querySelectorAll('.flashes li');
    flashes.forEach(function(flash) {
        flash.style.display = 'none';
    });
}, 5000); // 5000 milliseconds = 5 seconds


document.getElementById('give-via-mpesa-btn').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('mpesaModal').style.display = 'block';
  });
  
  document.getElementById('mpesaPaymentForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const phone = document.getElementById('phone').value;
    const amount = document.getElementById('amount').value;
  
    fetch('/mpesa_payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone: phone, amount: amount }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Payment initiated. Please check your phone to complete the transaction.');
      } else {
        alert('Payment failed. Please try again.');
      }
      document.getElementById('mpesaModal').style.display = 'none';
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred. Please try again.');
      document.getElementById('mpesaModal').style.display = 'none';
    });
  });
  
const cards = document.querySelectorAll('.card');
const slider = document.querySelector('.card-wrapper');
const background = document.getElementById('background');
let currentIndex = 0;

const updateCardPositions = () => {
    cards.forEach((card, index) => {
        card.classList.remove('card-center');
        if (index !== currentIndex) {
            gsap.to(card, { scale: 0.9, duration: 0.5, opacity: 0.8 });
        }
    });
    cards[currentIndex].classList.add('card-center');
    gsap.to(cards[currentIndex], { scale: 1.2, duration: 0.5, opacity: 1 });

    // Background image transition
    gsap.to(background, {
        backgroundImage: `url('${cards[currentIndex].getAttribute('data-background')}')`,
        duration: 0.5,
        ease: "power1.inOut"
    });
};

const nextSlide = () => {
    // Current card slides out
    gsap.to(cards[currentIndex], {
        x: '-100%',
        opacity: 0,
        duration: 0.5,
        onComplete: () => {
            slider.appendChild(cards[currentIndex]); // Move to the back
            gsap.set(cards[currentIndex], { x: '100%' }); // Reset position
        }
    });

    // Update the index
    currentIndex = (currentIndex + 1) % cards.length;

    // Next card slides in
    gsap.fromTo(cards[currentIndex], { x: '100%', opacity: 0 }, { x: '0%', opacity: 1, duration: 0.5 });

    updateCardPositions();
};

const prevSlide = () => {
    // Current card slides out
    gsap.to(cards[currentIndex], {
        x: '100%',
        opacity: 0,
        duration: 0.5,
        onComplete: () => {
            slider.prepend(cards[currentIndex]); // Move to the front
            gsap.set(cards[currentIndex], { x: '-100%' }); // Reset position
        }
    });

    // Update the index
    currentIndex = (currentIndex - 1 + cards.length) % cards.length;

    // Previous card slides in
    gsap.fromTo(cards[currentIndex], { x: '-100%', opacity: 0 }, { x: '0%', opacity: 1, duration: 0.5 });

    updateCardPositions();
};

// Automatic loop every 5 seconds
setInterval(nextSlide, 5000);

document.querySelector('.next-btn').addEventListener('click', nextSlide);
document.querySelector('.prev-btn').addEventListener('click', prevSlide);

updateCardPositions(); // Initialize the first center card
