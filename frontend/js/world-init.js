(function () {
  "use strict";

  const worldEl = document.getElementById("world");
  if (!worldEl || typeof window.mountScrollWorld !== "function") return;

  window.mountScrollWorld(worldEl, {
    brand: null,
    cta: null,
    hint: null,
    crossfade: 0.08,
    atmosphere: false,
    nav: false,
    connectors: [],
    sections: [
      {
        id: "lobby",
        label: "Институт долголетия",
        still: "assets/world/clinic-lobby-desktop.webp",
        clip: "assets/world/clinic-lobby-desktop.mp4",
        stillMobile: "assets/world/clinic-lobby-demo.webp",
        clipMobile: "assets/world/clinic-lobby-demo.mp4",
        accent: "#111111",
        scroll: 2.5,
        linger: 0,
        eyebrow: "BIOTECH & LONGEVITY MEDICINE",
        title: "Объединяя биотехнологии, диагностику и превенцию в *современное здоровье*",
        body: "Клинический институт и центр превентивной медицины. Персональные протоколы управления *здоровьем* и биомаркерами."
      },
      {
        id: "flow",
        label: "Диагностика и протоколы",
        still: "assets/world/clinic-flow-desktop.webp",
        clip: "assets/world/clinic-flow-desktop.mp4",
        stillMobile: "assets/world/clinic-flow-demo.webp",
        clipMobile: "assets/world/clinic-flow-demo.mp4",
        accent: "#111111",
        scroll: 2.5,
        linger: 0,
        eyebrow: "КЛИНИЧЕСКИЙ МАРШРУТ",
        title: "Передовая диагностика и стандарты доказательного *лечения*",
        body: "МРТ экспертного класса Siemens 1.5T, экспресс-панели биомаркеров и персональное ведение профильными врачами.",
        cta: {
          primary: { label: "Записаться на консультацию", href: "#appointment" }
        }
      }
    ]
  });

  // Flow Overlay Transition
  let overlayEl = worldEl.querySelector(".flow-overlay");
  if (!overlayEl) {
    overlayEl = document.createElement("div");
    overlayEl.className = "flow-overlay";
    overlayEl.setAttribute("aria-hidden", "true");

    const heading = document.createElement("h2");
    heading.className = "flow-overlay__heading";
    heading.innerHTML = "От знакомства к <em>диагностике</em>";
    overlayEl.appendChild(heading);

    worldEl.appendChild(overlayEl);
  }

  const reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  function updateOverlay() {
    if (reduceMotionQuery.matches) {
      overlayEl.style.opacity = "0";
      overlayEl.style.visibility = "hidden";
      overlayEl.style.display = "none";
      overlayEl.setAttribute("aria-hidden", "true");
      return;
    }

    const vh = window.innerHeight || 1;
    const y = window.scrollY || 0;
    const dist = Math.abs(y / vh - 2.5);

    let opacity = 0;
    if (dist <= 0.12) {
      opacity = 1;
    } else if (dist >= 0.55) {
      opacity = 0;
    } else {
      opacity = (0.55 - dist) / (0.55 - 0.12);
    }

    if (opacity < 0.001) {
      overlayEl.style.opacity = "0";
      overlayEl.style.visibility = "hidden";
      overlayEl.style.display = "none";
      overlayEl.setAttribute("aria-hidden", "true");
    } else {
      overlayEl.style.display = "flex";
      overlayEl.style.visibility = "visible";
      overlayEl.style.opacity = opacity.toFixed(4);
      overlayEl.setAttribute("aria-hidden", "false");
    }
  }

  let ticking = false;
  function requestOverlayUpdate() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(() => {
        ticking = false;
        updateOverlay();
      });
    }
  }

  window.addEventListener("scroll", requestOverlayUpdate, { passive: true });
  window.addEventListener("resize", requestOverlayUpdate, { passive: true });
  updateOverlay();
})();
