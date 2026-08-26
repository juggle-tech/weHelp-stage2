/**
 * Sign in / sign up pop-up dialog and login status management
 * - Toggle signin/signup pop-ups and switch between them
 * - Sign in: Store JWT token
 * - Sign up: Create account and show result message
 * - Check login status on page load
 * - Sign out: Clear token and reload page
 */


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
            location.reload();
            document.getElementById("signInStatus").textContent = "登出系統";
            document.getElementById("signinError").textContent = "";
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
            signupPopup.classList.remove("open");
            document.getElementById("signupForm").reset();
            document.getElementById("signupError").textContent = "";
        } else {
            // Show error message
            document.getElementById("signupError").textContent = result.message;
        }
    } catch (err) {
        console.error("Sign up fails:", err);
    }
});


// Check logged-in status
async function checkSignInStatus() {
    const token = localStorage.getItem("token");
    const status = document.getElementById("signInStatus");

    if (!token) {
        status.textContent = "登入/註冊";
        return;
    }

    try {
        let response = await fetch("/api/user/auth", {
            method: "GET",
            headers: { "Authorization": "Bearer " + token }
        });

        let result = await response.json();

        // User has logged in with a token
        if (result.data) {
            status.textContent = "登出系統";
        } else {
            localStorage.removeItem("token");
            status.textContent = "登入/註冊";
        }
    } catch (err) {
        console.error("Sign-in status fails:", err);
    }
}


/* Pop-up dialogs */
// Toggle signin and signup pop-up dialogs
const signinPopup = document.querySelector(".signinPopup");
const signupPopup = document.querySelector(".signupPopup");

document.getElementById("signInStatus").addEventListener("click", function(event) {
    event.preventDefault();
    console.log(localStorage.getItem("token"));
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
    document.getElementById("signinForm").reset();
    document.getElementById("signinError").textContent = "";
});

// Change to Signin pop-up dialog
document.getElementById("signupText").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    signinPopup.classList.add("open");
    document.getElementById("signupForm").reset();
    document.getElementById("signupError").textContent = "";
});

// Close Signin / Signup pop-up dialogs
document.getElementById("signinX").addEventListener("click", function() {
    signinPopup.classList.remove("open");
    document.getElementById("signinForm").reset();
    document.getElementById("signinError").textContent = "";
});

document.getElementById("signupX").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    document.getElementById("signupForm").reset();
    document.getElementById("signupError").textContent = "";
});



document.addEventListener("DOMContentLoaded", checkSignInStatus);