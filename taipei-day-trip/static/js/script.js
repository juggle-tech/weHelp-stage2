/**
 * 
 */

// Toggle signin and signup pop-up dialogues
const signinPopup = document.querySelector(".signinPopup");
const signupPopup = document.querySelector(".signupPopup");

document.getElementById("signInStatus").addEventListener("click", function(event) {
    event.preventDefault();
    signinPopup.classList.add("open");
});

// Change to Signup pop-up dialogue
document.getElementById("signinText").addEventListener("click", function() {
    signinPopup.classList.remove("open");
    signupPopup.classList.add("open");
    document.getElementById("signinError").textContent = "";
});

// Change to Signin pop-up dialogue
document.getElementById("signupText").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    signinPopup.classList.add("open");
    document.getElementById("signupError").textContent = "";
});

// Close Signin / Signup pop-up dialogues
document.getElementById("signinX").addEventListener("click", function() {
    signinPopup.classList.remove("open");
    document.getElementById("signinError").textContent = "";
});

document.getElementById("signupX").addEventListener("click", function() {
    signupPopup.classList.remove("open");
    document.getElementById("signupError").textContent = "";
});


// User sign in 
document.getElementById("signinBtn").addEventListener("click", async function() {
    const email = document.getElementById("emailSignin").value.trim();
    const password = document.getElementById("passwordSignin").value.trim();

    if (!email || !password) {
        alert("Email and password can not be empty!");
        return;
    }

    try {
        let response = await fetch(("/api/user/auth"), {
            method: "PUT"
        });
        
        let result = await response.json();

        // Sign in successfully
        if (result.data) {
            // Store token and change status
            localStorage.setItem("token", result.token);
            location.reload();
            document.getElementById("signInStatus").textContent = "登出系統";
            // document.getElementById("signinError").textContent = "";
        } else {
            // Show error message
            document.getElementById("signinError").textContent = "帳號或密碼輸入錯誤";
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
        let response = await fetch(("/api/user"), {
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
            document.getElementById("signupError").textContent = "帳號或密碼輸入錯誤";
        }
    } catch (err) {
        console.error("Sign up fails:", err);
    }
});