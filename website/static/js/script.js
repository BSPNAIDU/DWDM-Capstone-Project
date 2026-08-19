// =======================================
// AgriAI - script.js
// =======================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("AgriAI Loaded Successfully");

    // -----------------------------
    // Animate Cards
    // -----------------------------
    const cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(40px)";

        setTimeout(() => {

            card.style.transition = "0.7s ease";

            card.style.opacity = "1";

            card.style.transform = "translateY(0px)";

        }, index * 200);

    });

    // -----------------------------
    // Button Loading Animation
    // -----------------------------
    const form = document.querySelector("form");

    if (form) {

        form.addEventListener("submit", function () {

            const btn = document.querySelector("button");

            btn.disabled = true;

            btn.innerHTML = "🤖 Predicting...";

        });

    }

    // -----------------------------
    // Input Animation
    // -----------------------------
    const inputs = document.querySelectorAll("input, select");

    inputs.forEach(input => {

        input.addEventListener("focus", function () {

            this.style.transform = "scale(1.03)";

        });

        input.addEventListener("blur", function () {

            this.style.transform = "scale(1)";

        });

    });

    // -----------------------------
    // Floating Background Animation
    // -----------------------------
    const background = document.querySelector(".background");

    if (background) {

        let angle = 0;

        setInterval(() => {

            angle += 1;

            background.style.backgroundPosition =
                `${Math.sin(angle / 20) * 20}px ${Math.cos(angle / 20) * 20}px`;

        }, 60);

    }

    // -----------------------------
    // Prediction Card Pulse
    // -----------------------------
    const prediction = document.querySelector(".prediction");

    if (prediction) {

        setInterval(() => {

            prediction.animate(
                [
                    {
                        transform: "scale(1)"
                    },
                    {
                        transform: "scale(1.02)"
                    },
                    {
                        transform: "scale(1)"
                    }
                ],
                {
                    duration: 2000
                }
            );

        }, 2500);

    }

    // -----------------------------
    // Button Hover Glow
    // -----------------------------
    const buttons = document.querySelectorAll("button");

    buttons.forEach(button => {

        button.addEventListener("mouseenter", () => {

            button.style.boxShadow =
                "0px 0px 25px rgba(46,204,113,0.7)";

        });

        button.addEventListener("mouseleave", () => {

            button.style.boxShadow = "none";

        });

    });

    // -----------------------------
    // Success Message Animation
    // -----------------------------
    const title = document.querySelector("h1");

    if (title) {

        title.animate(
            [
                {
                    opacity: 0
                },
                {
                    opacity: 1
                }
            ],
            {
                duration: 1000
            }
        );

    }

});