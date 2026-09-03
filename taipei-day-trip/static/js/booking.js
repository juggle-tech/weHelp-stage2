/**
 * Booking details page.
 * - Render booking details or an empty state
 * - Redirect to homepage if the user has not signed in
 * - On page load: verify login status, fetch current user and booking data then render
 * - Delete booking: remove the current booking and reload the page
 */


// Render booking details 
function renderBooking(user, booking_data) {

    document.getElementById("username").textContent = user.name;

    if (booking_data) {  // Display booking page with booking details
        
        // Show booking details
        const attraction_data = booking_data.attraction;
        document.getElementById("bookedAttrImg").src = attraction_data.image;
        document.getElementById("bookedAttrName").textContent = attraction_data.name;
        document.getElementById("bookedAttrAddr").textContent = attraction_data.address;

        document.getElementById("bookedAttrDate").textContent = booking_data.date;
        document.querySelectorAll(".bookedAttrPrice").forEach((span) => {
            span.textContent = booking_data.price;
        });

        document.getElementById("contactName").value = user.name;
        document.getElementById("contactEmail").value = user.email;

        document.getElementById("bookingEmptyMsg").classList.remove("show");

        // Show Booking section
        document.getElementById("bookedAttr").classList.add("show");

        // Show Contact section
        document.getElementById("contactBlock").classList.add("show");

        // Show Payment section
        document.getElementById("paymentBlock").classList.add("show");

        // Show Summary section
        document.getElementById("summaryBlock").classList.add("show");

        // Show hr
        document.querySelectorAll(".bookingHr").forEach((hr) => hr.classList.add("show"));

    } else {  // Display booking page with an empty state

        document.getElementById("bookingEmptyMsg").classList.add("show");

        // Hide Booking section
        document.getElementById("bookedAttr").classList.remove("show");
        
        // Hide Contact section
        document.getElementById("contactBlock").classList.remove("show");

        // Hide Payment section
        document.getElementById("paymentBlock").classList.remove("show");

        // Hide Summary section
        document.getElementById("summaryBlock").classList.remove("show");

        // Hide hr
        document.querySelectorAll(".bookingHr").forEach((hr) => hr.classList.remove("show"));
    }
}


// Enter booking.html
async function initBookingPage() {
    const token = localStorage.getItem("token");

    // No token: Redirect to homepage
    if (!token) {
        location.href = "/";
        return;
    }

    const user = await getCurrentUser(token);

    try {
        let response = await fetch("/api/booking", {
            method: "GET",
            headers: { 
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + token 
            },
        });

        let result = await response.json();

        if (result.error) {
            location.href = "/";
            return;
        }

        renderBooking(user, result.data);

    } catch (err) {
        console.error("Retrieving booking fails: ", err);
    }
}


// Delete booking on click
document.getElementById("deleteBtn").addEventListener("click", async function() {
    const token = localStorage.getItem("token");

    try {
        let response = await fetch("/api/booking", {
            method: "DELETE",
            headers: { 
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + token 
            },
        });

        let result = await response.json();

        if (result.ok) {
            location.reload();
        }

    } catch (err) {
        console.error("Delete booking fails: ", err);
    }
});

document.addEventListener("DOMContentLoaded", initBookingPage);