/**
 * Member Center page (MCP).
 * - Fetch and render the user's MCP token
 * - Regenerate MCP token on button click
 */


const token = localStorage.getItem("token");

// Render member center page (MCP)
async function initMCPpage() {

    // No token: Redirect to homepage
    if (!token) {
        location.href = "/";
        return;
    }

    const user = await getCurrentUser(token);
    document.getElementById("username").textContent = user.name;

    let response = await fetch("/api/token", {
        method: "GET",
        headers: { 
            "Content-Type": "application/json", 
            "Authorization": "Bearer " + token 
        }
    });

    let mcpToken = await response.json();
    document.getElementById("mcpToken").textContent = mcpToken.token;
}


// Generate and update new mcp token
async function updateToken() {
    
    let response = await fetch("/api/token", {
        method: "PUT",
        headers: { 
            "Content-Type": "application/json", 
            "Authorization": "Bearer " + token 
        }
    });

    let result = await response.json();

    if (result.ok) {
        let mcpToken = document.getElementById("mcpToken");
        mcpToken.textContent = result.token;
    }
}


// Handle button click
// Update mcp token
document.getElementById("tokenBtn").addEventListener("click", function() {
    updateToken();
});

// Member logout
document.getElementById("logoutBtn").addEventListener("click", function() {
    localStorage.removeItem("token");
    location.href = "/";
});


document.addEventListener("DOMContentLoaded", initMCPpage);