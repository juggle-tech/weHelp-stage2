/**
 * Attraction detail page.
 * - Fetch and render attraction details
 * - Time selection: toggle guide fee
 * - Image slideshow: render images with left/right navigation and indicators
 * - booking: submit booking request with auth token
 */


// Fetch the details of the attraction by its id and render them
// Retrieve Attraction Id from the path
const pathElement = window.location.pathname.split('/');
const attractionId = pathElement[pathElement.length - 1];

async function getAttractionDetail(attractionId) {

    try {
        let response = await fetch("/api/attraction/" + attractionId , {
            method: "GET"
        });

        let result = await response.json();

        if (!result.error) {
            let attrName = document.getElementById("attrName");
            attrName.textContent = result.data.name;

            let attrCate = document.getElementById("attrCate");
            attrCate.textContent = result.data.category + " at " + result.data.mrt;

            let attrDescrip = document.getElementById("attrDescrip");
            attrDescrip.textContent = result.data.description;

            let attrAddr = document.getElementById("attrAddr");
            attrAddr.textContent = result.data.address;
            
            let attrTrans = document.getElementById("attrTrans");
            attrTrans.textContent = result.data.transport;


            initSlideShow(result.data.images);

        } else {
            console.error("Error messages:", result.message);
        }

    } catch (err) {
        console.error("Fetching attraction detail fails:", err);
    }
}


// Change fee as the user selects different travel time
const timeInputs = document.querySelectorAll('input[name="time"]');
const fee = document.getElementById("fee");

timeInputs.forEach((input) => {
  input.addEventListener("change", () => {
    if (input.value === "morning") {
      fee.textContent = "2000";
    } else {
      fee.textContent = "2500";
    }
  });
});


// Image slideshow
let slideImages = [];
let curIndex = 0;
 
const slideImg = document.getElementById("slideShow");
const indicator = document.getElementById("indicator");
const leftBtnSlide = document.getElementById("leftBtnSlide");
const rightBtnSlide = document.getElementById("rightBtnSlide");

// Pre-load images
function preloadImages(urls) {
    urls.forEach((url) => {
        const img = new Image();
        img.src = url;
    });
}

// Initialize slide show
function initSlideShow(images) {

    slideImages = images;
    curIndex = 0;

    preloadImages(slideImages);

    slideImg.style.backgroundImage = "url(" + slideImages[curIndex] + ")";

    indicator.innerHTML = "";
    slideImages.forEach((_, index) => {
        let shadow = document.createElement("div");
        shadow.classList.add("item");

        if (index === curIndex) {
            shadow.classList.add("active");
        }

        shadow.addEventListener("click", () => {
            curIndex = index;
            updateSlide();
        })

        indicator.appendChild(shadow);

    });
}


// Update the slide when a button is clicked or when the page first loads
function updateSlide() {

    slideImg.style.backgroundImage = "url(" + slideImages[curIndex] + ")";

    let shadows = indicator.querySelectorAll(".item");

    // Toggle "active" class on the corresponding indicator
    shadows.forEach((shadow, index) => {
        shadow.classList.toggle("active", index === curIndex);
    });
}


// Events for clicking slide buttons
leftBtnSlide.addEventListener("click", () => {
    
    if (slideImages.length === 0) { return; }

    curIndex= (curIndex - 1 + slideImages.length) % slideImages.length;

    updateSlide();

});
 
rightBtnSlide.addEventListener("click", () => {
    
    if (slideImages.length === 0) { return; }

    curIndex = (curIndex + 1) % slideImages.length;
    
    updateSlide();
});

const dateInput = document.getElementById("date");

dateInput.addEventListener("click", () => {
    dateInput.showPicker();
});


// Add the attraction booking to the cart on click
document.getElementById("bookBtn").addEventListener("click", async function() {
    const date = document.getElementById("date").value.trim();
    const time = document.querySelector('input[name="time"]:checked').value;
    const fee = document.getElementById("fee").textContent.trim();
    const token = localStorage.getItem("token");

    if (!token) {
        signinPopup.classList.add("open");
        signinPopup.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
    }

    try {
        let response = await fetch("/api/booking", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + token 
            },
            body: JSON.stringify({ attr_id: Number(attractionId), booking_date: date, time: time, price: fee })
        })

        let result = await response.json();
        console.log(result);

        if (result.has_booking) {
            alert("You already have a booking. Please cancel it first.");
            return;
        } else if (result) {
            location.href = "/booking";
        }

    } catch (err) {
        console.error("Adding trip to the cart fails: ", err);
    }
});


getAttractionDetail(attractionId);