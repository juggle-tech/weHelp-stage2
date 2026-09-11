/**
 * Thankyou page (order confirmation).
 * - Fetch the order details by order number and redirect to homepage on error
 * - Render order details: attraction name, date, price and address
 * - Render payment status: green text for success, red text for not yet paid
 */


// Render Thankyou page
async function initThankyou() {

    const token = localStorage.getItem("token");
    const params = new URLSearchParams(window.location.search);
    const orderNumber = params.get("number");

    // No token: Redirect to homepage
    if (!token) {
        location.href = "/";
        return;
    }


    let response = await fetch("/api/orders/"+ orderNumber, {
        method: "GET",
        headers: {
            "Content-Type": "application/json", 
            "Authorization": "Bearer " + token 
        }
    });

    let result = await response.json();

    if (result.error) {
        location.href = "/";
        return;
    }

    if (result.data) {
        // Render thankyou.html
        document.getElementById("thankyouOrderNum").textContent = result.data.number;
        
        trip = result.data.trip;
        document.getElementById("thankyouAttrName").textContent = trip.attraction.name;
        document.getElementById("thankyouAttrDate").textContent = trip.date;
        document.getElementById("thankyouAttrPrice").textContent = "NT$ " + result.data.price;
        document.getElementById("thankyouAttrAddr").textContent = trip.attraction.address;
        
        paymentStatus = document.getElementById("thankyouPaymentStatus");
        if (result.data.status === 0) {
            paymentStatus.textContent = "已付款成功";
            paymentStatus.style.color = "#166534";
        } else {
            paymentStatus.textContent = "尚未成功付款";
            paymentStatus.style.color = "#9B1C1C";
        }
    }
}

document.addEventListener("DOMContentLoaded", initThankyou);