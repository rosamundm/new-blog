/* hamburger open/close */

const hamburger = document.getElementById("hamburger");
const navbarMenu = document.getElementById("navbar-menu");

hamburger.addEventListener("click", () => {
  hamburger.classList.toggle("active");
  navbarMenu.classList.toggle("active");
});

navbarMenu.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", () => {
    hamburger.classList.remove("active");
    navbarMenu.classList.remove("active");
  });
});


/* detect scroll to hide navbar on mobile view */

let lastScrollTop = 0;
const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
  if (window.innerWidth <= 767) {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    
    if (currentScroll > lastScrollTop) {  // scrolling down
      navbar.style.transform = "translateY(-100%)";
    } else {
      navbar.style.transform = "translateY(0)";
    }
    lastScrollTop = Math.max(0, currentScroll);
  }
});