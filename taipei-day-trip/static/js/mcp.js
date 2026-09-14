


// Render member center page (MCP)
async function initMCPpage() {
    const token = localStorage.getItem("token");

    // No token: Redirect to homepage
    if (!token) {
        location.href = "/";
        return;
    }

    const user = await getCurrentUser(token);

    document.getElementById("username").textContent = user.name;
}

// Member logout
document.getElementById("logoutBtn").addEventListener("click", function() {
    localStorage.removeItem("token");
    location.href = "/";
});

document.addEventListener("DOMContentLoaded", initMCPpage);