/* ============================================================
   HAR GHAR SOLAR — MAIN JS
   Features: Loader, Navbar scroll, Active nav, Back-to-top,
   Counter animation, Solar calculator, Ripple buttons,
   Visitor counter, Lightbox, AOS re-init
============================================================ */

// ---- LOADER ----
window.addEventListener('load', function() {
  setTimeout(function() {
    var loader = document.getElementById('loader');
    if (loader) {
      loader.classList.add('hidden');
      setTimeout(function() { loader.style.display = 'none'; }, 500);
    }
  }, 1200);
});

// ---- STICKY NAVBAR + SCROLL CLASS ----
var mainNav = document.getElementById('mainNav');
window.addEventListener('scroll', function() {
  if (mainNav) {
    if (window.scrollY > 80) {
      mainNav.classList.add('scrolled');
    } else {
      mainNav.classList.remove('scrolled');
    }
  }
  // Back to top visibility
  var btn = document.getElementById('backToTop');
  if (btn) {
    if (window.scrollY > 400) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }
});

// ---- BACK TO TOP ----
var backToTopBtn = document.getElementById('backToTop');
if (backToTopBtn) {
  backToTopBtn.addEventListener('click', function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ---- ACTIVE NAV LINK ----
(function() {
  var path = window.location.pathname;
  var links = document.querySelectorAll('.navbar-nav .nav-link');
  links.forEach(function(link) {
    var href = link.getAttribute('href');
    if (href === path || (path === '/' && href === '/') ||
        (path !== '/' && href !== '/' && path.startsWith(href.split('#')[0]) && href.split('#')[0].length > 1)) {
      link.classList.add('active');
    }
  });
  // Hash links
  if (window.location.hash) {
    links.forEach(function(link) {
      if (link.getAttribute('href') === '/' + window.location.hash ||
          link.getAttribute('href') === window.location.hash) {
        link.classList.add('active');
      }
    });
  }
})();

// ---- RIPPLE EFFECT ----
document.addEventListener('click', function(e) {
  var btn = e.target.closest('.quote-btn,.hero-btn,.calc-btn,.lead-form button,.btn-login-admin,.btn-login-vendor');
  if (!btn) return;
  var ripple = document.createElement('span');
  ripple.className = 'ripple';
  var rect = btn.getBoundingClientRect();
  var size = Math.max(rect.width, rect.height);
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
  ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
  btn.appendChild(ripple);
  setTimeout(function() { ripple.remove(); }, 700);
});

// ---- COUNTER ANIMATION ----
function animateCounter(el, target, suffix) {
  suffix = suffix || '';
  var duration = 2000;
  var start = 0;
  var step = target / (duration / 16);
  var isFloat = target % 1 !== 0;
  var timer = setInterval(function() {
    start += step;
    if (start >= target) {
      start = target;
      clearInterval(timer);
    }
    el.textContent = (isFloat ? start.toFixed(1) : Math.floor(start)) + suffix;
  }, 16);
}

function initCounters() {
  var counters = document.querySelectorAll('.counter-num[data-target]');
  counters.forEach(function(el) {
    var target = parseFloat(el.getAttribute('data-target'));
    var suffix = el.getAttribute('data-suffix') || '';
    animateCounter(el, target, suffix);
  });
}

// Intersection Observer for counters
var counterObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      initCounters();
      counterObserver.disconnect();
    }
  });
}, { threshold: 0.3 });
var counterArea = document.querySelector('.counter-area');
if (counterArea) counterObserver.observe(counterArea);

// ---- SOLAR CALCULATOR ----
function calculateSolar() {
  var billEl = document.getElementById('bill');
  if (!billEl) return;
  var bill = parseFloat(billEl.value);
  if (!bill || bill <= 0) {
    billEl.style.borderColor = '#ff4d4d';
    billEl.focus();
    setTimeout(function() { billEl.style.borderColor = ''; }, 2000);
    return;
  }
  var kw = Math.ceil(bill / 1000);
  kw = Math.max(1, kw);
  var monthlySaving = Math.round(bill * 0.85);
  var yearlySaving = monthlySaving * 12;
  var subsidy = kw <= 2 ? 30000 : kw <= 3 ? 60000 : 78000;
  var resultEl = document.getElementById('solarResult');
  if (!resultEl) return;
  resultEl.innerHTML =
    '<div class="result-grid">' +
    '<div class="result-item">' +
    '<span class="result-val">' + kw + ' KW</span>' +
    '<span class="result-lbl">Recommended System</span>' +
    '</div>' +
    '<div class="result-item">' +
    '<span class="result-val">&#8377;' + monthlySaving.toLocaleString('en-IN') + '</span>' +
    '<span class="result-lbl">Monthly Saving</span>' +
    '</div>' +
    '<div class="result-item">' +
    '<span class="result-val">&#8377;' + yearlySaving.toLocaleString('en-IN') + '</span>' +
    '<span class="result-lbl">Yearly Saving</span>' +
    '</div>' +
    '</div>' +
    '<p style="text-align:center;margin-top:16px;font-size:13px;opacity:.75;">Subsidy available up to &#8377;' + subsidy.toLocaleString('en-IN') + ' under PM Surya Ghar Yojana</p>';
  resultEl.classList.add('show');
}
// Allow Enter key on calculator
var calcInput = document.getElementById('bill');
if (calcInput) {
  calcInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') calculateSolar();
  });
}

// ---- PROJECT LIGHTBOX ----
var lightbox = document.getElementById('lightbox');
var lightboxImg = document.getElementById('lightbox-img');
var lightboxClose = document.getElementById('lightbox-close');

document.querySelectorAll('.project-card').forEach(function(card) {
  card.addEventListener('click', function() {
    var img = card.querySelector('img');
    if (img && lightbox && lightboxImg) {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || 'Project Image';
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  });
});
function closeLightbox() {
  if (lightbox) {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  }
}
if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
if (lightbox) {
  lightbox.addEventListener('click', function(e) {
    if (e.target === lightbox) closeLightbox();
  });
}
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeLightbox();
});

// ---- VISITOR COUNTER ----
function loadVisitorCount() {
  var el = document.getElementById('visitorCount');
  if (!el) return;
  fetch('/visitor-count')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var count = data.count || 0;
      el.textContent = count.toLocaleString('en-IN');
    })
    .catch(function() {
      el.textContent = '10,000+';
    });
}
loadVisitorCount();

// ---- ADMIN TABLE SEARCH ----
function searchLead() {
  var input = document.getElementById('leadSearch');
  if (!input) return;
  var val = input.value.toLowerCase();
  document.querySelectorAll('#leadTable tbody tr').forEach(function(row) {
    row.style.display = row.innerText.toLowerCase().includes(val) ? '' : 'none';
  });
}

// ---- SMOOTH SCROLL FOR HASH LINKS ----
document.querySelectorAll('a[href*="#"]').forEach(function(link) {
  link.addEventListener('click', function(e) {
    var href = link.getAttribute('href');
    if (href.startsWith('#') || (href.includes('#') && href.split('#')[0] === window.location.pathname)) {
      var id = href.split('#')[1];
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        var offset = 80;
        var top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    }
  });
});

// ---- FORM VALIDATION FEEDBACK ----
var leadForms = document.querySelectorAll('.lead-form');
leadForms.forEach(function(form) {
  form.addEventListener('submit', function(e) {
    var inputs = form.querySelectorAll('input[required],select[required]');
    var valid = true;
    inputs.forEach(function(input) {
      if (!input.value.trim()) {
        input.style.borderColor = '#ff4d4d';
        valid = false;
        setTimeout(function() { input.style.borderColor = ''; }, 3000);
      }
    });
    if (!valid) { e.preventDefault(); }
  });
});

// ---- CLOSE MOBILE MENU ON LINK CLICK ----
document.querySelectorAll('#navMenu .nav-link').forEach(function(link) {
  link.addEventListener('click', function() {
    var collapse = document.getElementById('navMenu');
    if (collapse && collapse.classList.contains('show')) {
      var toggler = document.querySelector('.custom-toggler');
      if (toggler) toggler.click();
    }
  });
});
