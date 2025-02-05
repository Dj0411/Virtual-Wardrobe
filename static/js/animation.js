document.addEventListener("DOMContentLoaded", function() {
    let emailInput = document.getElementById("email");
    let passwordInput = document.getElementById("password");
    let usernameInput = document.getElementById("username"); // For signup page
    let gear1 = document.getElementById("gear1");
    let gear2 = document.getElementById("gear2");
    let gear3 = document.getElementById("gear3"); // For signup page
    let submitBtn = document.getElementById("submit-btn");
    let loginForm = document.querySelector("#login-form");
    let signupForm = document.querySelector("#signup-form"); // For signup page
    let formContainer = document.querySelector(".form-container");
    let bg = document.querySelector("body");

    let emailTyping, passwordTyping, usernameTyping;
    let isSubmitting = false; // Prevents multiple submissions

    function startRotation(inputField, gear, typingVariable) {
        inputField.addEventListener("input", function() {
            clearTimeout(typingVariable);
            gear.classList.add("rotating"); // Start rotation
            typingVariable = setTimeout(() => {
                gear.classList.remove("rotating"); // Stop rotation when typing stops
            }, 500); // Stops 0.5s after user stops typing
        });
    }

    // Apply continuous rotation while typing
    if (emailInput && gear1) startRotation(emailInput, gear1, emailTyping);
    if (passwordInput && gear2) startRotation(passwordInput, gear2, passwordTyping);
    if (usernameInput && gear3) startRotation(usernameInput, gear3, usernameTyping); // Only for signup

    // Enable submit button when all fields are filled
    document.addEventListener("input", function() {
        let isLoginPage = !usernameInput; // If there's no username field, it's login
        if ((isLoginPage && emailInput.value.length > 0 && passwordInput.value.length > 0) ||
            (!isLoginPage && usernameInput.value.length > 0 && emailInput.value.length > 0 && passwordInput.value.length > 0)) {
            submitBtn.classList.add("active");
            submitBtn.removeAttribute("disabled");
        } else {
            submitBtn.classList.remove("active");
            submitBtn.setAttribute("disabled", "true");
        }
    });

    // After-submit animation
    function playExitAnimation() {
        // Step 1: Fade out email input and gear
        emailInput.parentElement.classList.add("fade-out");
        if (gear1) gear1.classList.add("fade-out");

        setTimeout(() => {
            // Step 2: Fade out password input and gear
            passwordInput.parentElement.classList.add("fade-out");
            if (gear2) gear2.classList.add("fade-out");
        }, 400);

        setTimeout(() => {
            // Step 3: Fade out submit button
            submitBtn.classList.add("fade-out");
        }, 800);

        setTimeout(() => {
            // Step 4: Slide out form container
            formContainer.classList.add("slide-out-right");
        }, 1200);

        setTimeout(() => {
            // Step 5: Apply swirl effect to background
            bg.classList.add("swirl-out");
        }, 1600);

        setTimeout(() => {
            // Step 6: Redirect to home page after animation completes
            window.location.href = "/home";
        }, 2500);
    }

    // Handle form submission (Login)
    if (loginForm) {
        loginForm.addEventListener("submit", function(e) {
            e.preventDefault(); // Prevent default form submission

            if (isSubmitting) return; // Prevent multiple submissions
            isSubmitting = true; // Set flag to true
            submitBtn.setAttribute("disabled", "true"); // Disable button

            let formData = new FormData(loginForm);

            fetch("/auth/login", { // Update with actual login API route
                method: "POST",
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    playExitAnimation();
                } else {
                    throw new Error("Invalid login");
                }
            })
            .catch(error => {
                console.error("Login error:", error);
                alert("Invalid email or password. Please try again.");
                isSubmitting = false; // Allow retry
                submitBtn.removeAttribute("disabled");
            });
        });
    }

    // Handle form submission (Signup)
    if (signupForm) {
        signupForm.addEventListener("submit", function(e) {
            e.preventDefault(); // Prevent default form submission

            if (isSubmitting) return; // Prevent multiple submissions
            isSubmitting = true; // Set flag to true
            submitBtn.setAttribute("disabled", "true"); // Disable button

            let formData = new FormData(signupForm);

            fetch("/auth/signup", { // Update with actual signup API route
                method: "POST",
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    playExitAnimation();
                } else {
                    throw new Error("Error during signup");
                }
            })
            .catch(error => {
                console.error("Signup error:", error);
                alert("Error during signup. Please try again.");
                isSubmitting = false; // Allow retry
                submitBtn.removeAttribute("disabled");
            });
        });
    }
});
