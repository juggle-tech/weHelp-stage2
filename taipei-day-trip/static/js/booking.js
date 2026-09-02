/**
 * Booking details page.
 * - Render booking details or an empty state
 * - Redirect to homepage if the user has not signed in
 * - On page load: verify login status, fetch current user and booking data then render
 */


// Render booking details 
function renderBooking(user_name, booking_data) {

    document.getElementById("username").textContent = user_name;

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

        document.getElementById("bookingEmptyMsg").innerHTML = "";

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

        document.getElementById("bookingEmptyMsg").textContent = "目前沒有任何預定行程";

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


// Reserved trip
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
            headers: { "Authorization": "Bearer " + token }
        });

        let result = await response.json();

        if (result.error) {
            location.href = "/";
            return;
        }

        renderBooking(user.name, result.data);

    } catch (err) {
        console.error("Retrieving booking fails: ", err);
    }
}

document.addEventListener("DOMContentLoaded", initBookingPage);