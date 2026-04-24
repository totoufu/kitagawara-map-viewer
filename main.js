/**
 * main.js — 北川原温 時空間マップ
 * Leaflet.js + noUiSlider によるインタラクティブ地図
 */

// ===================== 定数 =====================
const MIN_YEAR = 1979;
const MAX_YEAR = 2022;
const DATA_URL = 'data/projects.json';

// 年代に応じたピン色（古→青 / 新→橙）
function yearToColor(year) {
  const t = (year - MIN_YEAR) / (MAX_YEAR - MIN_YEAR); // 0..1
  // 青 #4a9eff → ゴールド #c8a96e → 橙 #ff6b35
  if (t < 0.5) {
    const u = t * 2;
    return lerpColor('#4a9eff', '#c8a96e', u);
  } else {
    const u = (t - 0.5) * 2;
    return lerpColor('#c8a96e', '#ff6b35', u);
  }
}

function lerpColor(a, b, t) {
  const ah = parseInt(a.slice(1), 16);
  const bh = parseInt(b.slice(1), 16);
  const ar = (ah >> 16) & 0xff, ag = (ah >> 8) & 0xff, ab = ah & 0xff;
  const br = (bh >> 16) & 0xff, bg = (bh >> 8) & 0xff, bb = bh & 0xff;
  const r = Math.round(ar + (br - ar) * t);
  const g = Math.round(ag + (bg - ag) * t);
  const bv = Math.round(ab + (bb - ab) * t);
  return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${bv.toString(16).padStart(2,'0')}`;
}

// ===================== 状態管理 =====================
let allProjects = [];
let markers = {};       // id -> { marker, project }
let trajectoryLines = [];
let currentMode = 'all'; // 'all' | 'range' | 'trace'
let rangeFrom = MIN_YEAR;
let rangeTo = MAX_YEAR;
let traceAnimTimer = null;

// ===================== 地図初期化 =====================
const map = L.map('map', {
  center: [36.5, 137.5],
  zoom: 5,
  zoomControl: true,
  attributionControl: true,
});

// 国土地理院 淡色地図 (日本語表記が正確で建築アーカイブに適したデザイン)
L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
  maxZoom: 18,
}).addTo(map);

// ===================== データ読み込み =====================
async function loadData() {
  const res = await fetch(DATA_URL);
  allProjects = await res.json();
  initMarkers();
  initSlider();
  initTicks();
  applyFilter();
  hideLoading();
}

// ===================== マーカー生成 =====================
function initMarkers() {
  allProjects.forEach(p => {
    if (p.lat == null || p.lng == null) return;

    const color = yearToColor(p.year);
    const iconHtml = `<div class="proj-dot" id="dot-${p.id}" style="background-color:${color};box-shadow:0 0 10px ${color}99;"></div>`;

    const icon = L.divIcon({
      html: iconHtml,
      className: '',
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });

    const marker = L.marker([p.lat, p.lng], { icon })
      .addTo(map)
      .on('click', () => showPopup(p));

    markers[p.id] = { marker, project: p };
  });
}

// ===================== スライダー初期化 =====================
function initSlider() {
  const slider = document.getElementById('year-slider');
  noUiSlider.create(slider, {
    start: [MIN_YEAR, MAX_YEAR],
    connect: true,
    step: 1,
    range: { min: MIN_YEAR, max: MAX_YEAR },
    format: { to: v => Math.round(v), from: v => Number(v) },
  });

  slider.noUiSlider.on('update', (values) => {
    rangeFrom = parseInt(values[0]);
    rangeTo = parseInt(values[1]);
    document.getElementById('year-from').textContent = rangeFrom;
    document.getElementById('year-to').textContent = rangeTo;
    if (currentMode !== 'all') applyFilter();
  });
}

// ===================== ティック生成 =====================
function initTicks() {
  const ticks = document.getElementById('timeline-ticks');
  const years = [];
  for (let y = 1980; y <= 2020; y += 5) years.push(y);
  years.unshift(MIN_YEAR);
  years.push(MAX_YEAR);

  years.forEach(y => {
    const span = document.createElement('span');
    span.className = 'tick-label';
    span.textContent = y;
    ticks.appendChild(span);
  });
}

// ===================== フィルター適用 =====================
function applyFilter() {
  clearTrajectory();
  let count = 0;

  allProjects.forEach(p => {
    const entry = markers[p.id];
    if (!entry) return;
    const visible = (currentMode === 'all') ||
                    (p.year >= rangeFrom && p.year <= rangeTo);
    const el = entry.marker.getElement();
    if (el) {
      el.style.opacity = visible ? '1' : '0';
      el.style.pointerEvents = visible ? 'auto' : 'none';
      el.style.transform = visible ? 'scale(1)' : 'scale(0.3)';
      el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
    }
    if (visible) count++;
  });

  document.getElementById('stat-showing').textContent = count;

  if (currentMode === 'trace') {
    drawTrajectoryAnimated();
  } else if (currentMode === 'range') {
    drawTrajectoryStatic();
  }
}

// ===================== 軌跡描画（静的） =====================
function drawTrajectoryStatic() {
  clearTrajectory();
  const visible = getVisibleSorted();
  if (visible.length < 2) return;

  for (let i = 0; i < visible.length - 1; i++) {
    const a = visible[i], b = visible[i + 1];
    const line = L.polyline(
      curveMidpoints([a.lat, a.lng], [b.lat, b.lng]),
      {
        color: lerpColor('#4a9eff', '#ff6b35',
          (a.year - MIN_YEAR) / (MAX_YEAR - MIN_YEAR)),
        weight: 1.5,
        opacity: 0.55,
        dashArray: '6 4',
        className: 'trajectory-line',
      }
    ).addTo(map);
    trajectoryLines.push(line);
  }
}

// ===================== 軌跡アニメーション =====================
function drawTrajectoryAnimated() {
  clearTrajectory();
  const visible = getVisibleSorted();
  if (visible.length < 2) return;

  let i = 0;
  function drawNext() {
    if (i >= visible.length - 1) return;
    const a = visible[i], b = visible[i + 1];
    const pts = curveMidpoints([a.lat, a.lng], [b.lat, b.lng]);
    const line = L.polyline(pts, {
      color: lerpColor('#4a9eff', '#ff6b35',
        (a.year - MIN_YEAR) / (MAX_YEAR - MIN_YEAR)),
      weight: 2,
      opacity: 0,
      className: 'trajectory-line',
    }).addTo(map);

    // フェードイン
    let op = 0;
    const fade = setInterval(() => {
      op += 0.08;
      line.setStyle({ opacity: Math.min(op, 0.7) });
      if (op >= 0.7) clearInterval(fade);
    }, 30);

    trajectoryLines.push(line);
    i++;
    traceAnimTimer = setTimeout(drawNext, 120);
  }
  drawNext();
}

// ===================== ベジェ近似カーブ =====================
function curveMidpoints(a, b) {
  const midLat = (a[0] + b[0]) / 2;
  const midLng = (a[1] + b[1]) / 2;
  const dx = b[1] - a[1];
  const dy = b[0] - a[0];
  const dist = Math.sqrt(dx * dx + dy * dy);
  const bend = dist * 0.18;
  // 垂直方向にオフセットして曲線っぽくする
  const ctrlLat = midLat - dx * 0.18;
  const ctrlLng = midLng + dy * 0.18;
  // 20点で近似
  const pts = [];
  for (let t = 0; t < 1; t += 0.05) {
    const mt = 1 - t;
    const lat = mt * mt * a[0] + 2 * mt * t * ctrlLat + t * t * b[0];
    const lng = mt * mt * a[1] + 2 * mt * t * ctrlLng + t * t * b[1];
    pts.push([lat, lng]);
  }
  pts.push([b[0], b[1]]); // 確実に終点(t=1)を追加
  return pts;
}

function getVisibleSorted() {
  return allProjects
    .filter(p => {
      if (p.lat == null) return false;
      return (currentMode === 'all') ||
             (p.year >= rangeFrom && p.year <= rangeTo);
    })
    .sort((a, b) => a.year - b.year);
}

function clearTrajectory() {
  if (traceAnimTimer) { clearTimeout(traceAnimTimer); traceAnimTimer = null; }
  trajectoryLines.forEach(l => map.removeLayer(l));
  trajectoryLines = [];
}

// ===================== ポップアップ =====================
function showPopup(p) {
  document.getElementById('popup-year-badge').textContent = p.year;
  document.getElementById('popup-name').textContent = p.name;
  document.getElementById('popup-location').textContent = p.location || '';
  document.getElementById('popup-notes').textContent = p.notes ? `※ ${p.notes}` : '';
  document.getElementById('popup-card').classList.remove('hidden');

  // ハイライト
  Object.values(markers).forEach(({ marker }) => {
    const el = marker.getElement();
    if (el) el.classList.remove('highlighted');
  });
  const dotEl = markers[p.id]?.marker.getElement();
  if (dotEl) dotEl.classList.add('highlighted');
}

document.getElementById('popup-close').addEventListener('click', () => {
  document.getElementById('popup-card').classList.add('hidden');
  Object.values(markers).forEach(({ marker }) => {
    const el = marker.getElement();
    if (el) el.classList.remove('highlighted');
  });
});

// ===================== モードボタン =====================
document.getElementById('btn-all').addEventListener('click', () => setMode('all'));
document.getElementById('btn-range').addEventListener('click', () => setMode('range'));
document.getElementById('btn-trajectory').addEventListener('click', () => setMode('trace'));

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  const btnMap = { all: 'btn-all', range: 'btn-range', trace: 'btn-trajectory' };
  document.getElementById(btnMap[mode]).classList.add('active');
  applyFilter();
}

// ===================== ローディング非表示 =====================
function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  overlay.classList.add('fade-out');
  setTimeout(() => { overlay.style.display = 'none'; }, 700);
}

// ===================== 起動 =====================
loadData().catch(err => {
  console.error('Failed to load projects.json:', err);
  document.getElementById('loading-inner').innerHTML =
    '<p style="color:#ff6b35">データの読み込みに失敗しました</p>';
});
