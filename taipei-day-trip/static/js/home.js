let nextPage = 0;
let isLoading = false;
let currentCategory = null;
let currentKeyword = null;
let observer;
let sentinel;

async function getAttractions(page=nextPage, append=false) {
    if (isLoading) return;
    isLoading = true;

  try {
    let url = "/api/attractions?page=" + nextPage;

    if (currentCategory) {
        url += "&category=" + encodeURIComponent(currentCategory);
    }
        
    if (currentKeyword) {
        url += "&keyword=" + encodeURIComponent(currentKeyword);
    } 
    
    let response = await fetch(url, {
        method: "GET"
    });

    let result = await response.json();

    if (!result.error) {
        let board = document.getElementById("attrBlocks");

        if (!append) {
            board.innerHTML = "";
        }

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


        // Update nextPage 
        nextPage = result.nextPage;
        if (nextPage === null) {
            observer.unobserve(sentinel);
        } else {
            observer.observe(sentinel);
        }
    
    } else {
      console.error("Error messages:", result.message);
    }

  } catch (err) {
    console.error("Fetching attractions fails:", err);
  } finally {
    isLoading = false;
  }
}


function setupInfiniteScroll() {
  sentinel = document.getElementById("footer");

  observer = new IntersectionObserver((entries) => {
    const entry = entries[0];
    if (entry.isIntersecting && nextPage !== null && !isLoading) {
      getAttractions(nextPage, true);
    }
  }, {
    rootMargin: "200px"
  });

  observer.observe(sentinel);
}

setupInfiniteScroll();
getAttractions(nextPage, false);