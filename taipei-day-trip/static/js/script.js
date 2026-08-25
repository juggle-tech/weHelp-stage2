
// Toggle signin and signup pop-up dialogues



// User sign in 
document.getElementById("signinBtn").addEventListener("click", async function(event) {
    const email = document.getElementById("emailSignin").value.trim();
    const password = document.getElementById("passwordSignin").value.trim();

    if (!email || !password) {
        event.preventDefault();
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
            localStorage.setItem("token", result.token);
            location.reload();

            document.getElementById("signInStatus").textContent = "登出系統";
        } else {
            document.getElementById("signinError").textContent = "帳號或密碼輸入錯誤";
        }
    } catch (err) {
        console.error("Signin fails:", err);
    }
});


// User sign up
document.getElementById("signupBtn").addEventListener("click", async function(event) {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("emailSignup").value.trim();
    const password = document.getElementById("passwordSignup").value.trim();

    if (!name || !email || !password) {
        event.preventDefault();
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
        } else {
            document.getElementById("signupError").textContent = "帳號或密碼輸入錯誤";
        }
    } catch (err) {
        console.error("Signin fails:", err);
    }
});