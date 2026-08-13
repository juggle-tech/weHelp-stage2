/**
 * Search bar interactions.
 * - Category dropdown: toggle open/close and update category filter
 * - Keyword input: update keyword filter on form submit
 * - MRT list: horizontal scroll via left/right buttons
 * - MRT click: update keyword filter with selected station name
 */


// Toggle dropdown menu for category
const trigger = document.getElementById("cateSearch");
const menu = document.getElementById("cateMenu");

trigger.addEventListener('click', () => {
  const isOpen = menu.classList.toggle("isOpen");
});

// Update category filter
menu.addEventListener('click', (event) => {
  const btn = event.target.closest("button");
  if (!btn) return;

  trigger.textContent = btn.textContent + "▼";
  menu.classList.remove("isOpen");

  if (btn.textContent === "全部分類") {
    currentCategory = null;
  } else {
    currentCategory = btn.textContent;
  }
});


// Update keyword filter on input
const keywordInput = document.getElementById("keyword");
const searchBar = document.getElementById("searchBar");

searchBar.addEventListener('submit', (event) => {
  event.preventDefault();

  let keyword = keywordInput.value.trim();

  if (keyword === "") {
    currentKeyword = null;
  } else {
    currentKeyword = keyword;
  }

  // Reset page and get filtered attractions
  nextPage = 0;
  getAttractions(0, false);
});


// Scroll through MRT list
const mrtMenu = document.getElementById("mrtMenu");
const leftBtn = document.getElementById("leftBtn");
const rightBtn = document.getElementById("rightBtn");

leftBtn.addEventListener("click", () => {
  mrtMenu.scrollBy({ left: -350, behavior: "smooth" });
});

rightBtn.addEventListener("click", () => {
  mrtMenu.scrollBy({ left: 350, behavior: "smooth" });
});


// Update keyword filter on MRT click
mrtMenu.addEventListener('click', (event) => {
  const btn = event.target.closest("button");
  if (!btn) return;

  keywordInput.value = btn.textContent;
  currentKeyword = btn.textContent;
});

