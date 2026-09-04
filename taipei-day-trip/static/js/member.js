/**
 * Sign in / sign up pop-up dialog and login status management
 * - Toggle signin/signup pop-ups and switch between them
 * - Sign in: Store JWT token
 * - Sign up: Create account and show result message
 * - Check login status on page load
 * - Sign out: Clear token and reload page
 * - Fetch current user info with a stored token
 * - Redirect to booking page from the nav bar
 */


// Flag: Ｕser login triggered by the trip booking button
let signinRedirectToBooking = false;

// User sign in
document.getElementById("signinBtn").addEventListener("click", async function() {
    const email = document.getElementById("emailSignin").value.trim();
    const password = document.getElementById("passwordSignin").value.trim();

    if (!email || !password) {
        alert("Email and password can not be empty!");
        return;
    }

    try {
        let response = await fetch("/api/user/auth", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password })
        });
        
        let result = await response.json();

        // Sign in successfully
        if (result.token) {
            // Store token and change status
            localStorage.setItem("token", result.token);
            document.getElementById("signInStatus").textContent = "登出系統";
            document.getElementById("signinError").textContent = "";

            if (signinRedirectToBooking) {
                location.href = "/booking";
            } else {
                location.reload();
            }
        } else {
            // Show error message
            document.getElementById("signinError").textContent = result.message;
        }
    } catch (err) {
        console.error("Sign in fails:", err);
    }
});


// User sign up
document.getElementById("signupBtn").addEventListener("click", async function() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("emailSignup").value.trim();
    const password = document.getElementById("passwordSignup").value.trim();
    const error = document.getElementById("signupError");

    if (!name || !email || !password) {
        alert("No input can be empty!");
        return;
    }

    try {
        let response = await fetch("/api/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, email: email, password: password })
        });
        
        let result = await response.json();

        // Sign in successfully
        if (result.ok) {
            // Close pop-up and reset all values
            document.getElementById("signupForm").reset();
            error.textContent = "會員已成功註冊";
            error.style.color = "#1B5E20";
        } else {
            // Show error message
            document.getElementById("signupError").textContent = result.message;
            error.style.color = "#D32F2F";
        }
    } catch (err) {
        console.error("Sign up fails:", err);
    }
});


// Get current user info
async function getCurrentUser(token) {
    try {
        let response = await fetch("/api/user/auth", {
            method: "GET",
            headers: { 
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + token 
            },
        });

        let result = await response.json();

        if (result.data) {
            return result.data;
        }

        return null;

    } catch (err) {
        console.error("Sign-in status fails:", err);
        return null;
    }
}


// Check logged-in status
async function checkSignInStatus() {
    const token = localStorage.getItem("token");
    const status = document.getElementById("signInStatus");

    if (!token) {
        status.textContent = "登入/註冊";
        return;
    }

    const user = await getCurrentUser(token);

    try {
        // User has logged in with a token
        if (user) {
            status.textContent = "登出系統";
        } else {
            localStorage.removeItem("token");
            status.textContent = "登入/註冊";
        }
    } catch (err) {
        console.error("Sign-in status fails:", err);
    }
}


//  Redirect to booking page after checking sign-in status
document.getElementById("bookingTrip").addEventListener("click", async function(event) {
    const token = localStorage.getItem("token");

    if (!token) {
        signinRedirectToBooking = true;
        signinPopup.classList.add("open");
        return;
    }
    
    location.href = "/booking";
});


/* Pop-up dialogs */
// Toggle signin and signup pop-up dialogs
const signinPopup = document.querySelector(".signinPopup");
const signupPopup = document.querySelector(".signupPopup");
const signinError = document.getElementById("signinError");
const signupError = document.getElementById("signupError");
const signinForm = document.getElementById("signinForm");
const signupForm = document.getElementById("signupForm");

document.getElementById("signInStatus").addEventListener("click", function(event) {
    event.preventDefault();
    
    // Check if the user has token： Text shown on screen is "登出系統"
    if (localStorage.getItem("token")) {
        localStorage.removeItem("token");
        location.reload();
    } else if (!signupPopup.classList.contains("open")) {
        signinPopup.classList.add("open");
    }
});

// Change to Signup pop-up dialog
document.getElementById("signinText").addEventListener("click", function() {
    signinPopup.classList.remove("open");
    signupPopup.classList.add("open");
    signinForm.reset();
    signinError.textContent = "";
    signinRedirectToBooking = false;
});

// Change to Signin pop-up dialog
document.getElementById("signupText").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    signinPopup.classList.add("open");
    signupForm.reset();
    signupError.textContent = "";
    signinRedirectToBooking = false;
});

// Close Signin / Signup pop-up dialogs
document.getElementById("signinX").addEventListener("click", function() {
    signinPopup.classList.remove("open");
    signinForm.reset();
    signinError.textContent = "";
    signinRedirectToBooking = false;
});

document.getElementById("signupX").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    signupForm.reset();
    signupError.textContent = "";
    signinRedirectToBooking = false;
});



document.addEventListener("DOMContentLoaded", checkSignInStatus);