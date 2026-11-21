
/* ==========================================
   AQUACARE - PREMIUM MAIN JAVASCRIPT
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* --------------------------------------
       1. AUTO-CLOSE SUCCESS AND INFO MESSAGES
    -------------------------------------- */

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        if (
            alert.classList.contains("alert-success") ||
            alert.classList.contains("alert-info")
        ) {

            setTimeout(function () {

                if (!alert.isConnected) return;

                const closeButton =
                    alert.querySelector(".btn-close");

                if (closeButton) {
                    closeButton.click();
                } else {
                    alert.classList.remove("show");
                    alert.remove();
                }

            }, 4000);

        }

    });


    /* --------------------------------------
       2. NAVBAR SCROLL EFFECT
    -------------------------------------- */

    const navbar = document.querySelector(".aquacare-navbar");

    if (navbar) {

        let ticking = false;

        window.addEventListener("scroll", function () {

            if (ticking) return;

            ticking = true;

            window.requestAnimationFrame(function () {

                if (window.scrollY > 30) {
                    navbar.classList.add("navbar-scrolled");
                } else {
                    navbar.classList.remove("navbar-scrolled");
                }

                ticking = false;

            });

        }, { passive: true });

    }


    /* --------------------------------------
       3. CARD HOVER INTERACTION
    -------------------------------------- */

    const interactiveCards = document.querySelectorAll(
        ".aquacare-card, " +
        ".dashboard-stat-card, " +
        ".staff-stat-card, " +
        ".manager-stat-card"
    );

    interactiveCards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {
            card.classList.add("card-active");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("card-active");
        });

    });


    /* --------------------------------------
       4. BUTTON CLICK FEEDBACK
    -------------------------------------- */

    const actionButtons = document.querySelectorAll(
        ".btn-aquacare"
    );

    actionButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            button.classList.add("button-clicked");

            setTimeout(function () {
                button.classList.remove("button-clicked");
            }, 180);

        });

    });


    /* --------------------------------------
       5. CONFIRMATION FOR DELETE ACTIONS
    -------------------------------------- */

    const deleteForms = document.querySelectorAll(
        "form[data-confirm]"
    );

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmationMessage =
                form.dataset.confirm ||
                "Are you sure you want to continue?";

            if (!window.confirm(confirmationMessage)) {
                event.preventDefault();
            }

        });

    });


    /* --------------------------------------
       6. PREVENT MULTIPLE FORM SUBMISSIONS
    -------------------------------------- */

    const protectedForms = document.querySelectorAll(
        "form[data-prevent-double-submit]"
    );

    protectedForms.forEach(function (form) {

        form.addEventListener("submit", function () {

            if (form.dataset.submitted === "true") {
                return;
            }

            form.dataset.submitted = "true";

            const submitButtons = form.querySelectorAll(
                'button[type="submit"], input[type="submit"]'
            );

            submitButtons.forEach(function (button) {
                button.disabled = true;
            });

        });

    });


    /* --------------------------------------
       7. WATERCARE PAGE FADE-IN
    -------------------------------------- */

    const pageContent = document.querySelector(".main-content");

    if (
        pageContent &&
        !window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {

        pageContent.classList.add("page-loaded");

    }


    console.log("AquaCare premium interface initialized.");

});


console.log("AquaCare JavaScript loaded successfully!");







document.addEventListener("DOMContentLoaded", function () {

    console.log("AquaCare JavaScript loaded successfully!");

    // Navbar scroll effect
    const navbar = document.querySelector(".aquacare-navbar");

    if (navbar) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 30) {
                navbar.classList.add("navbar-scrolled");
            } else {
                navbar.classList.remove("navbar-scrolled");
            }
        });
    }

    // Page entrance animation
    const mainContent = document.querySelector(".main-content");

    if (mainContent) {
        mainContent.classList.add("page-loaded");
    }

});
