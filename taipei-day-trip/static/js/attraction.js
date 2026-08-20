


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
            console.log("In");
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

        } else {
            console.error("Error messages:", result.message);
        }

    } catch (err) {
        console.error("Fetching categories fails:", err);
    }
}



// Change fee as the user selects different travel time
const timeInputs = document.querySelectorAll('input[name="time"]');
const fee = document.getElementById("fee");

timeInputs.forEach((input) => {
  input.addEventListener('change', () => {
    if (input.value === "morning") {
      fee.textContent = " 新台幣 2000 元 ";
    } else {
      fee.textContent = " 新台幣 2500 元 ";
    }
  });
});

getAttractionDetail(attractionId);