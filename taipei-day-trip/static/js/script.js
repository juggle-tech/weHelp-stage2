// Dropdow Menu for Category
const trigger = document.getElementById("cateSearch");
const menu = document.getElementById("cateMenu");
const menuButtons = menu.querySelectorAll("button");

trigger.addEventListener('click', () => {
    const isOpen = menu.classList.toggle("isOpen");
});

menuButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    trigger.textContent = btn.textContent + "▼";
    menu.classList.remove("isOpen");
  });
});

