document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.qr-placement');
  if (!container) return;

  const pdfImg = container.querySelector('.qr-placement-pdf');
  const qrImg = container.querySelector('.qr-placement-qr');

  const qrXField = document.getElementById('id_qr_x');
  const qrYField = document.getElementById('id_qr_y');
  const qrSizeField = document.getElementById('id_qr_size');

  const scaleInput = container.querySelector('.qr-scale-input');
  const scaleValue = container.querySelector('.qr-scale-value');

  if (!pdfImg || !qrImg || !qrXField || !qrYField || !qrSizeField) return;

  const clamp01 = (v) => Math.max(0, Math.min(1, v));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  let sizeRel = parseFloat(qrSizeField.value);
  if (!Number.isFinite(sizeRel) || sizeRel <= 0) {
    sizeRel = 0.18;
    qrSizeField.value = String(sizeRel);
  }

  const getMetrics = () => {
    const imgRect = pdfImg.getBoundingClientRect();
    const contRect = container.getBoundingClientRect();
    return {
      left: imgRect.left - contRect.left,
      top: imgRect.top - contRect.top,
      width: imgRect.width,
      height: imgRect.height,
    };
  };

  const sizePx = (metrics) => Math.max(1, sizeRel * metrics.width);

  const applySize = () => {
    const m = getMetrics();
    qrImg.style.width = `${sizePx(m)}px`;
    if (scaleValue) scaleValue.textContent = `${Math.round(sizeRel * 100)}%`;
  };

  const setHiddenFromLeftTop = (leftPx, topPx, metrics) => {
    const s = sizePx(metrics);
    const x = (leftPx - metrics.left + s / 2) / metrics.width;
    const y = (topPx - metrics.top + s / 2) / metrics.height;

    qrXField.value = clamp01(x).toFixed(6);
    qrYField.value = clamp01(y).toFixed(6);
  };

  const leftTopFromHidden = (metrics) => {
    const s = sizePx(metrics);
    const x = parseFloat(qrXField.value);
    const y = parseFloat(qrYField.value);
    const hasPos = Number.isFinite(x) && Number.isFinite(y);

    const cx = metrics.left + (hasPos ? clamp01(x) : 0.5) * metrics.width;
    const cy = metrics.top + (hasPos ? clamp01(y) : 0.5) * metrics.height;

    let left = cx - s / 2;
    let top = cy - s / 2;

    left = clamp(left, metrics.left, metrics.left + metrics.width - s);
    top = clamp(top, metrics.top, metrics.top + metrics.height - s);

    return { left, top, hasPos };
  };

  const setQRLeftTop = (left, top) => {
    qrImg.style.left = `${left}px`;
    qrImg.style.top = `${top}px`;
  };

  const syncFromFields = () => {
    const m = getMetrics();
    applySize();
    const { left, top, hasPos } = leftTopFromHidden(m);
    setQRLeftTop(left, top);

    if (hasPos) container.classList.remove('unset');
    else container.classList.add('unset');
  };

  const placeCenterAt = (xInContainer, yInContainer) => {
    const m = getMetrics();
    const s = sizePx(m);

    let left = xInContainer - s / 2;
    let top = yInContainer - s / 2;

    left = clamp(left, m.left, m.left + m.width - s);
    top = clamp(top, m.top, m.top + m.height - s);

    setQRLeftTop(left, top);
    setHiddenFromLeftTop(left, top, m);
    container.classList.remove('unset');
  };

  container.addEventListener('click', (e) => {
    if (e.target === qrImg) return;

    const contRect = container.getBoundingClientRect();
    const x = e.clientX - contRect.left;
    const y = e.clientY - contRect.top;

    const m = getMetrics();
    const insidePdf =
      x >= m.left && x <= m.left + m.width &&
      y >= m.top && y <= m.top + m.height;

    if (!insidePdf) return;

    placeCenterAt(x, y);
  });
  let dragging = false;
  let startPointerX = 0;
  let startPointerY = 0;
  let startLeft = 0;
  let startTop = 0;

  qrImg.addEventListener('pointerdown', (e) => {
    e.preventDefault();
    qrImg.setPointerCapture(e.pointerId);
    dragging = true;

    startPointerX = e.clientX;
    startPointerY = e.clientY;
    startLeft = parseFloat(qrImg.style.left) || 0;
    startTop = parseFloat(qrImg.style.top) || 0;

    qrImg.style.cursor = 'grabbing';
  });

  qrImg.addEventListener('pointermove', (e) => {
    if (!dragging) return;

    const dx = e.clientX - startPointerX;
    const dy = e.clientY - startPointerY;

    const m = getMetrics();
    const s = sizePx(m);

    let left = startLeft + dx;
    let top = startTop + dy;

    left = clamp(left, m.left, m.left + m.width - s);
    top = clamp(top, m.top, m.top + m.height - s);

    setQRLeftTop(left, top);
    setHiddenFromLeftTop(left, top, m);
  });

  qrImg.addEventListener('pointerup', (e) => {
    if (!dragging) return;
    dragging = false;
    try { qrImg.releasePointerCapture(e.pointerId); } catch (_) {}
    qrImg.style.cursor = 'grab';
    container.classList.remove('unset');
  });

  if (scaleInput) {

    scaleInput.value = String(clamp(sizeRel, 0.05, 0.6));
    if (scaleValue) scaleValue.textContent = `${Math.round(sizeRel * 100)}%`;

    scaleInput.addEventListener('input', () => {
      const v = parseFloat(scaleInput.value);
      if (!Number.isFinite(v)) return;

      sizeRel = clamp(v, 0.05, 0.6);
      qrSizeField.value = sizeRel.toFixed(2);

      const m = getMetrics();
      const { left, top, hasPos } = leftTopFromHidden(m);
      applySize();
      setQRLeftTop(left, top);

      if (hasPos) setHiddenFromLeftTop(left, top, m);
    });
  }

  if (pdfImg.complete) syncFromFields();
  else pdfImg.addEventListener('load', syncFromFields, { once: true });

  window.addEventListener('resize', syncFromFields);
});
