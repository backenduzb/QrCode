document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.qr-placement');
  if (!container) return;

  const pdfImg = container.querySelector('.qr-placement-pdf');
  const qrImg = container.querySelector('.qr-placement-qr');
  const qrXField = document.getElementById('id_qr_x');
  const qrYField = document.getElementById('id_qr_y');
  const qrSizeField = document.getElementById('id_qr_size');

  if (!pdfImg || !qrImg || !qrXField || !qrYField || !qrSizeField) return;

  let sizeRel = parseFloat(qrSizeField.value);
  if (!Number.isFinite(sizeRel) || sizeRel <= 0) {
    sizeRel = 0.18;
    qrSizeField.value = sizeRel.toString();
  }

  const getImageMetrics = () => {
    const imgRect = pdfImg.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    return {
      left: imgRect.left - containerRect.left,
      top: imgRect.top - containerRect.top,
      width: imgRect.width,
      height: imgRect.height,
    };
  };

  const applySize = () => {
    qrImg.style.width = `${sizeRel * 100}%`;
  };

  const clampPosition = (leftPx, topPx) => {
    const metrics = getImageMetrics();
    const sizePx = sizeRel * metrics.width;

    const minLeft = metrics.left;
    const maxLeft = metrics.left + metrics.width - sizePx;
    const minTop = metrics.top;
    const maxTop = metrics.top + metrics.height - sizePx;

    const clampedLeft = Math.min(Math.max(leftPx, minLeft), maxLeft);
    const clampedTop = Math.min(Math.max(topPx, minTop), maxTop);

    return { left: clampedLeft, top: clampedTop, metrics, sizePx };
  };

  const setHiddenFields = (leftPx, topPx, metrics) => {
    const x = (leftPx - metrics.left) / metrics.width;
    const y = (topPx - metrics.top) / metrics.height;

    qrXField.value = Math.max(0, Math.min(1, x)).toFixed(6);
    qrYField.value = Math.max(0, Math.min(1, y)).toFixed(6);
  };

  const setPositionFromFields = () => {
    const x = parseFloat(qrXField.value);
    const y = parseFloat(qrYField.value);
    const hasPos = Number.isFinite(x) && Number.isFinite(y);

    const metrics = getImageMetrics();
    const sizePx = sizeRel * metrics.width;
    const leftPx = metrics.left + (hasPos ? x : 0.5) * metrics.width - sizePx / 2;
    const topPx = metrics.top + (hasPos ? y : 0.5) * metrics.height - sizePx / 2;

    const clamped = clampPosition(leftPx, topPx);
    qrImg.style.left = `${clamped.left}px`;
    qrImg.style.top = `${clamped.top}px`;

    if (hasPos) {
      container.classList.remove('unset');
    } else {
      container.classList.add('unset');
    }
  };

  const placeAt = (clientX, clientY) => {
    const metrics = getImageMetrics();
    const sizePx = sizeRel * metrics.width;
    const leftPx = clientX - metrics.left - sizePx / 2;
    const topPx = clientY - metrics.top - sizePx / 2;

    const clamped = clampPosition(leftPx, topPx);
    qrImg.style.left = `${clamped.left}px`;
    qrImg.style.top = `${clamped.top}px`;
    setHiddenFields(clamped.left, clamped.top, clamped.metrics);
    container.classList.remove('unset');
  };

  let dragging = false;
  let startX = 0;
  let startY = 0;
  let startLeft = 0;
  let startTop = 0;

  qrImg.addEventListener('mousedown', (e) => {
    e.preventDefault();
    dragging = true;
    startX = e.clientX;
    startY = e.clientY;
    startLeft = parseFloat(qrImg.style.left) || 0;
    startTop = parseFloat(qrImg.style.top) || 0;
    qrImg.style.cursor = 'grabbing';
  });

  qrImg.addEventListener('dragstart', (e) => {
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;
    const clamped = clampPosition(startLeft + deltaX, startTop + deltaY);
    qrImg.style.left = `${clamped.left}px`;
    qrImg.style.top = `${clamped.top}px`;
    setHiddenFields(clamped.left, clamped.top, clamped.metrics);
  });

  document.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    qrImg.style.cursor = 'move';
    container.classList.remove('unset');
  });

  container.addEventListener('click', (e) => {
    if (e.target === qrImg) return;
    const rect = container.getBoundingClientRect();
    placeAt(e.clientX - rect.left, e.clientY - rect.top);
  });

  const syncLayout = () => {
    applySize();
    setPositionFromFields();
  };

  if (pdfImg.complete) {
    syncLayout();
  } else {
    pdfImg.addEventListener('load', syncLayout, { once: true });
  }

  window.addEventListener('resize', syncLayout);
});
