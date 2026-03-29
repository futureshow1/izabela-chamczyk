// ===== HAMBURGER MENU =====
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.querySelector('.hamburger');
  const nav = document.querySelector('.main-nav');

  if (hamburger && nav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      nav.classList.toggle('open');
    });

    // Close menu when clicking a link
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        nav.classList.remove('open');
      });
    });
  }

  // ===== SLIDER =====
  const slider = document.querySelector('.slider-track');
  const dots = document.querySelectorAll('.slider-dot');
  const slides = document.querySelectorAll('.slide');

  if (slider && slides.length > 0) {
    let current = 0;
    const total = slides.length;
    let autoPlayInterval;

    function goTo(index) {
      if (index < 0) index = total - 1;
      if (index >= total) index = 0;
      current = index;
      slider.style.transform = `translateX(-${current * 100}%)`;
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === current);
      });
    }

    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        goTo(i);
        resetAutoPlay();
      });
    });

    function startAutoPlay() {
      autoPlayInterval = setInterval(() => goTo(current + 1), 4000);
    }

    function resetAutoPlay() {
      clearInterval(autoPlayInterval);
      startAutoPlay();
    }

    // Pause on hover
    const sliderContainer = document.querySelector('.slider');
    if (sliderContainer) {
      sliderContainer.addEventListener('mouseenter', () => clearInterval(autoPlayInterval));
      sliderContainer.addEventListener('mouseleave', () => startAutoPlay());
    }

    // Touch/swipe support
    let touchStartX = 0;
    let touchEndX = 0;

    if (sliderContainer) {
      sliderContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      sliderContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        const diff = touchStartX - touchEndX;
        if (Math.abs(diff) > 50) {
          if (diff > 0) goTo(current + 1);
          else goTo(current - 1);
          resetAutoPlay();
        }
      }, { passive: true });
    }

    startAutoPlay();
  }
});

// ===== MOBILE PREVIEW =====
function toggleMobilePreview() {
  let overlay = document.querySelector('.mobile-preview-overlay');
  if (overlay) {
    overlay.classList.toggle('active');
    return;
  }

  overlay = document.createElement('div');
  overlay.className = 'mobile-preview-overlay active';
  overlay.innerHTML = `
    <div class="mobile-preview-frame" id="previewFrame">
      <div class="mobile-preview-bar">
        <button class="active" onclick="resizePreview(375, 812, this)">iPhone</button>
        <button onclick="resizePreview(390, 844, this)">iPhone Pro</button>
        <button onclick="resizePreview(768, 1024, this)">iPad</button>
      </div>
      <div class="mobile-preview-close" onclick="closeMobilePreview()">&times;</div>
      <iframe src="${window.location.href}"></iframe>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeMobilePreview();
  });
}

function closeMobilePreview() {
  const overlay = document.querySelector('.mobile-preview-overlay');
  if (overlay) overlay.classList.remove('active');
}

function resizePreview(w, h, btn) {
  const frame = document.getElementById('previewFrame');
  if (frame) {
    frame.style.width = w + 'px';
    frame.style.height = h + 'px';
  }
  document.querySelectorAll('.mobile-preview-bar button').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
}
