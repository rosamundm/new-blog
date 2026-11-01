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


/* blog post reading progress bar */

document.addEventListener("DOMContentLoaded", function () {
  const progressBar = document.getElementById("progress-bar");
  if (!progressBar) return;

  function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = progress + "%";
  }

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();
});


/* Tufte-style footnotes */

const SIDENOTE_QUERY = "(min-width: 1200px)";

document.addEventListener("DOMContentLoaded", () => {
  const seen = new Set();
  const refs = [];

  document.querySelectorAll('.post-content a[href^="#footnote-"]').forEach((ref) => {
    const id = ref.getAttribute("href");  // e.g. "#footnote-3"
    refs.push(ref);

    // override so that footnote "[1]" displays "1"
    const sup = ref.querySelector("sup");
    if (sup) sup.textContent = sup.textContent.replace(/^\[(.*)\]$/, "$1");

    if (seen.has(id)) return;  // make sure sidenote doesn't repeat
    const text = document.querySelector(id + " .footnote-text");
    if (!text) return;
    seen.add(id);

    const side = document.createElement("span");
    side.className = "sidenote";

    const num = document.createElement("span");
    num.className = "sidenote-number";
    num.textContent = id.replace("#footnote-", "") + ". ";

    side.append(num);
    side.insertAdjacentHTML("beforeend", text.innerHTML);
    ref.after(side);
  });

  if (!seen.size) return;
  document.body.classList.add("has-sidenotes");

  // make references plain text while sidenotes are visible
  const query = window.matchMedia(SIDENOTE_QUERY);
  const update = () => {
    refs.forEach((ref) => {
      if (query.matches) {
        if (ref.hasAttribute("href")) {
          ref.dataset.href = ref.getAttribute("href");
          ref.removeAttribute("href");  // unlink if large screen
        }
        ref.classList.add("footnote-ref-static");
      } else {
        if (ref.dataset.href) ref.setAttribute("href", ref.dataset.href);
        ref.classList.remove("footnote-ref-static");
      }
    });
  };
  update();
  query.addEventListener("change", update);
});