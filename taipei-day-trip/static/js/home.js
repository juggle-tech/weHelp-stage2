
async function getAttractions() {
  try {
    let response = await fetch("/api/attractions", {
      method: "GET"
    });

    let result = await response.json();

    if (!result.error) {
        let board = document.getElementById("attrBlocks");
        board.innerHTML = "";

        result.data.forEach((attraction) => {
            let attrCard = document.createElement("a");
            attrCard.className = "attrCard";
            attrCard.href = "/attraction/" + attraction.attr_id;
            

            // Attraction image and name
            let attrNameDiv = document.createElement("div");
            attrNameDiv.className = "attrName";
            attrCard.appendChild(attrNameDiv);

            let attrImg = document.createElement("img");
            attrImg.src = attraction.images[0];
            attrImg.alt = attraction.name;
            attrNameDiv.appendChild(attrImg);

            let attrName = document.createElement("p");
            attrName.textContent = attraction.name;
            attrNameDiv.appendChild(attrName);


            // Attraction MRT and Category
            let attrInfo = document.createElement("div");
            attrInfo.className = "attrInfo";
            attrCard.appendChild(attrInfo);

            let attrMRT = document.createElement("span");
            attrMRT.textContent = attraction.mrt;
            attrInfo.appendChild(attrMRT);

            let attrCate= document.createElement("span");
            attrCate.textContent = attraction.category;
            attrInfo.appendChild(attrCate);


            board.appendChild(attrCard);
        });
    
    } else {
      console.error("Error messages:", result.message);
    }

  } catch (err) {
    console.error("Fetching attractions fails:", err);
  }
}

getAttractions();