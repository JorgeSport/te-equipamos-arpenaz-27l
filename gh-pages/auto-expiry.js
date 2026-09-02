(() => {
  const PROMO_END = new Date('2026-09-06T04:59:59Z'); // 05/09/2026 23:59:59, hora de Perú

  function finishPromotion() {
    if (Date.now() <= PROMO_END.getTime()) return;

    const offer = document.querySelector('#oferta');
    if (!offer || offer.dataset.promoFinished === 'true') return;
    offer.dataset.promoFinished = 'true';

    const eyebrow = offer.querySelector('.ey');
    const title = offer.querySelector('h2');
    const lead = offer.querySelector('.lead');
    const priceBox = offer.querySelector('.pricebox');

    if (eyebrow) eyebrow.textContent = 'PROMOCIÓN FINALIZADA';
    if (title) title.innerHTML = 'Esta oferta<br>ha terminado.';
    if (lead) lead.textContent = 'La promoción especial finalizó el 5 de septiembre de 2026.';

    if (priceBox) {
      priceBox.innerHTML = `
        <span class="flag">PROMOCIÓN FINALIZADA</span>
        <div style="font-size:32px;font-weight:900;letter-spacing:-.04em;margin:18px 0 10px">Consulta disponibilidad</div>
        <p style="line-height:1.55;margin-bottom:0">El precio promocional ya no está vigente. Escríbenos por WhatsApp para consultar disponibilidad y precio actual.</p>
      `;
    }
  }

  finishPromotion();
  setInterval(finishPromotion, 30000);
})();
