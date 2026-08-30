const colors = {
  gris: { name: 'Gris carbón', swatch: '#555957', images: ['p3017110/k$a7fc94d4f2ded1052a164521a4041990','p3079490/k$693debf0d906c774018bd9302d6c3697','p3078138/k$3d7d919edccfdfdbeaccd26e5f2f7857','p3078143/k$5dbadf45e4c43d8e731977d113c425c0','p3079458/k$9b4753def1552a0b1af9bc704d2d218b','p3079465/k$264c7db2b67ef8047cfc013d1fbce9e8','p3079380/k$edb263e123c0185f88dd5dddc1662190','p3079366/k$5a3d69598cf16d9a27699c5a8cbc4940','p3087182/k$97eaa3ad1fb3073be96d33dafcd92d09'] },
  naranja: { name: 'Naranja terracota', swatch: '#b85e38', images: ['p3079340/k$c31fb7931f4dcabab29efb334bd83623','p3078103/k$82426d3617c6d9f588de34b1846fce3e','p3078095/k$0f84d9f2ed01406400914da9d43a941f','p3079404/k$f118a9ea26c03716c234c4a62f685c49','p3079524/k$1fce1658af5e1ed1f0366585141241a2','p3079466/k$6afeda576fa1b5a05fb5ba50a424c2db','p3079397/k$d9135570c080b6b413f30c12e82d5a96','p3079322/k$964e915e91efcfd9bca20c06aa7f275a','p3079493/k$e642f751ac43bc7bc3dd2c50bfbd006b'] },
  verde: { name: 'Verde oliva', swatch: '#6b7046', images: ['p3017116/k$84ab719a554796f32ba1758b956d0a78','p3078046/k$c6af87d08ac5019c6aaca9e960471308','p3078141/k$ce7693ff9fcf84e2f6f386e37be5dfa2','p3079552/k$54ba7fd865dcec1c2951e592a85c1fc1','p3079351/k$cae0509b49de51a9079237ca07861198','p3079316/k$f888cdbb59ec0131bc2426188c52a55c','p3079385/k$8b717bba24a09cf899776425d38f888b','p3079442/k$d1904cd1ed42c8de62fe1978aabcfe14','p3079529/k$d05c0e9042ab414420d34bf246816360'] }
};
const imageUrl = path => `https://contents.mediadecathlon.com/${path}/picture.jpg?f=1600x0&format=auto`;
const requestedColor = new URLSearchParams(window.location.search).get('color');
let activeColor = Object.prototype.hasOwnProperty.call(colors, requestedColor) ? requestedColor : 'gris';
let activeImage = 0;
let touchStart = null;

const stageImage = document.querySelector('.zoom-image img');
const storyImage = document.querySelector('.story-image img');
const thumbnails = document.querySelector('.thumbnails');
const colorName = document.querySelector('.color-picker strong');
const colorButtons = [...document.querySelectorAll('.color-options button')];
const whatsappLinks = [...document.querySelectorAll('a[href*="wa.me"]')];

const countdown = document.createElement('section');
countdown.className = 'offer-countdown';
countdown.setAttribute('aria-label', 'Tiempo restante de la oferta');
countdown.innerHTML = `
  <div class="countdown-heading"><span>Oferta por tiempo limitado</span><strong>Termina el 30/09/2026</strong></div>
  <div class="countdown-units">
    <div><strong data-countdown="days">00</strong><span>Días</span></div>
    <b>:</b>
    <div><strong data-countdown="hours">00</strong><span>Horas</span></div>
    <b>:</b>
    <div><strong data-countdown="minutes">00</strong><span>Min</span></div>
    <b>:</b>
    <div><strong data-countdown="seconds">00</strong><span>Seg</span></div>
  </div>`;
document.querySelector('.stock').insertAdjacentElement('afterend', countdown);

const offerEndsAt = new Date('2026-10-01T00:00:00-05:00').getTime();
let countdownTimer;
function updateCountdown() {
  const remaining = Math.max(0, offerEndsAt - Date.now());
  const days = Math.floor(remaining / 86400000);
  const hours = Math.floor((remaining % 86400000) / 3600000);
  const minutes = Math.floor((remaining % 3600000) / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  const values = { days, hours, minutes, seconds };
  Object.entries(values).forEach(([unit, value]) => {
    countdown.querySelector(`[data-countdown="${unit}"]`).textContent = String(value).padStart(2, '0');
  });
  if (remaining === 0) {
    countdown.classList.add('ended');
    countdown.querySelector('.countdown-heading').innerHTML = '<span>Promoción</span><strong>Oferta finalizada</strong>';
    clearInterval(countdownTimer);
  }
}
updateCountdown();
countdownTimer = setInterval(updateCountdown, 1000);

function whatsappUrl() {
  const productUrl = `https://jorgesport.github.io/te-equipamos-arpenaz-27l/?color=${activeColor}#inicio`;
  const message = `Hola Te Equipamos, deseo consultar y comprar la mochila Arpenaz 100 de 27 L en color ${colors[activeColor].name} a S/179.00.\n\nEnlace del producto: ${productUrl}`;
  return `https://wa.me/51920807184?text=${encodeURIComponent(message)}`;
}
function syncWhatsapp() { whatsappLinks.forEach(link => link.href = whatsappUrl()); }
function renderGallery() {
  const selected = colors[activeColor];
  const images = selected.images.map(imageUrl);
  stageImage.src = images[activeImage];
  stageImage.alt = `Mochila Arpenaz 100 ${selected.name}, vista ${activeImage + 1}`;
  storyImage.src = images[1];
  storyImage.alt = `Detalle de la mochila Arpenaz 100 ${selected.name}`;
  colorName.textContent = selected.name;
  document.querySelector('.spec-list p:nth-child(3) strong').textContent = selected.name;
  thumbnails.innerHTML = '';
  images.forEach((src, index) => {
    const button = document.createElement('button');
    button.className = index === activeImage ? 'active' : '';
    button.setAttribute('aria-label', `Ver imagen ${index + 1}`);
    button.innerHTML = `<img src="${src}" alt="" loading="lazy">`;
    button.addEventListener('click', () => { activeImage = index; renderGallery(); });
    thumbnails.appendChild(button);
  });
  colorButtons.forEach((button, index) => button.classList.toggle('active', Object.keys(colors)[index] === activeColor));
  syncWhatsapp();
}
function move(direction) { activeImage = (activeImage + direction + 9) % 9; renderGallery(); updateLightbox(); }

document.querySelector('.gallery-arrow.left').addEventListener('click', () => move(-1));
document.querySelector('.gallery-arrow.right').addEventListener('click', () => move(1));
colorButtons.forEach((button, index) => button.addEventListener('click', () => {
  activeColor = Object.keys(colors)[index];
  activeImage = 0;
  renderGallery();
  history.replaceState(null, '', `?color=${activeColor}#inicio`);
  document.querySelector('.gallery').scrollIntoView({ behavior: 'smooth', block: 'start' });
}));

const nav = document.querySelector('.nav');
const menu = document.querySelector('.menu-button');
menu.addEventListener('click', () => nav.classList.toggle('open'));
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => nav.classList.remove('open')));

const lightbox = document.createElement('div');
lightbox.className = 'lightbox';
lightbox.setAttribute('role', 'dialog');
lightbox.setAttribute('aria-modal', 'true');
lightbox.innerHTML = '<button class="lightbox-close" aria-label="Cerrar">×</button><button class="lightbox-arrow left" aria-label="Imagen anterior">‹</button><img alt="Imagen ampliada"><button class="lightbox-arrow right" aria-label="Imagen siguiente">›</button><p></p>';
function updateLightbox() {
  lightbox.querySelector('img').src = imageUrl(colors[activeColor].images[activeImage]);
  lightbox.querySelector('p').textContent = `${activeImage + 1} / 9 · ${colors[activeColor].name}`;
}
function openLightbox() { updateLightbox(); document.body.appendChild(lightbox); }
function closeLightbox() { lightbox.remove(); }
document.querySelector('.zoom-image').addEventListener('click', openLightbox);
lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
lightbox.querySelector('.lightbox-arrow.left').addEventListener('click', e => { e.stopPropagation(); move(-1); });
lightbox.querySelector('.lightbox-arrow.right').addEventListener('click', e => { e.stopPropagation(); move(1); });
lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });

const stage = document.querySelector('.gallery-stage');
stage.addEventListener('touchstart', e => touchStart = e.touches[0].clientX, { passive: true });
stage.addEventListener('touchend', e => { const distance = e.changedTouches[0].clientX - touchStart; if (Math.abs(distance) > 45) move(distance > 0 ? -1 : 1); }, { passive: true });
renderGallery();
