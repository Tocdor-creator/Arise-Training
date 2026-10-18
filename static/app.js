/* ARISE — Shadow Training (SPA sem build) */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const app = $('#app');
const today = () => new Date().toLocaleDateString('sv-SE'); // AAAA-MM-DD local

const store = {
  get(k, d = null) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* sem storage */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* sem storage */ } },
};

const state = {
  me: null,
  prefs: Object.assign({ sound: true, voice: true, cadence: true }, store.get('arise_prefs', {})),
};
const savePrefs = () => store.set('arise_prefs', state.prefs);

const GOALS = [
  ['emagrecer', 'Perder gordura', 'Mais repetições, descanso curto, condicionamento em todo treino.'],
  ['massa', 'Ganhar massa muscular', 'Cadência lenta (3-1-1), 8–15 reps, foco em tensão.'],
  ['forca', 'Força & habilidades', 'Progressões mais difíceis, poucas reps, descanso longo.'],
  ['resistencia', 'Resistência / condicionamento', 'Muitas repetições e circuitos rápidos.'],
  ['saude', 'Saúde geral / começar do zero', 'Volume moderado para criar o hábito com segurança.'],
];
const STAT_INFO = {
  STR: 'Força — empurrar, puxar, mergulhos',
  AGI: 'Agilidade — pernas e posterior',
  VIT: 'Vitalidade — núcleo e condicionamento',
  PER: 'Percepção — treinos com cadência',
  INT: 'Inteligência — missões diárias completas',
};
const BODY_PARTS = [
  ['', 'Todos'], ['chest', 'Peito'], ['back', 'Costas'], ['upper arms', 'Braços'], ['shoulders', 'Ombros'],
  ['waist', 'Abdômen'], ['upper legs', 'Coxas'], ['lower legs', 'Panturrilhas'], ['cardio', 'Cardio'],
  ['lower arms', 'Antebraços'], ['neck', 'Pescoço'],
];
const MUSCLES = {
  pectorals: 'peitorais', triceps: 'tríceps', deltoids: 'deltoides', core: 'core', lats: 'dorsais', biceps: 'bíceps',
  glutes: 'glúteos', quads: 'quadríceps', quadriceps: 'quadríceps', hamstrings: 'posteriores de coxa', calves: 'panturrilhas',
  abs: 'abdômen', abdominals: 'abdômen', obliques: 'oblíquos', 'upper back': 'costas superiores', traps: 'trapézio',
  trapezius: 'trapézio', 'hip flexors': 'flexores do quadril', 'erector spinae': 'eretores da espinha',
  'serratus anterior': 'serrátil', forearms: 'antebraços', shoulders: 'ombros', adductors: 'adutores',
  abductors: 'abdutores', 'lower back': 'lombar', rhomboids: 'romboides', 'rear deltoids': 'deltoide posterior',
  'cardiovascular system': 'sistema cardiovascular', chest: 'peito', back: 'costas', 'wrist flexors': 'flexores do punho',
  'rotator cuff': 'manguito rotador', 'latissimus dorsi': 'dorsais', 'levator scapulae': 'elevador da escápula',
  'inner thighs': 'parte interna da coxa', groin: 'virilha', ankles: 'tornozelos', feet: 'pés', hands: 'mãos',
  wrists: 'punhos', 'upper chest': 'peitoral superior', soleus: 'sóleo', 'rear delts': 'deltoide posterior',
};
const tMuscle = (m) => MUSCLES[m?.toLowerCase()] || m;
const gifUrl = (id) => `/gif/${encodeURIComponent(id)}.gif`;
const fmtTime = (s) => { s = Math.max(0, Math.round(s)); const m = Math.floor(s / 60); return m ? `${m}:${String(s % 60).padStart(2, '0')}` : `${s}s`; };
const fmtTarget = (v, type) => (type === 'time' ? fmtTime(v) : `${v} reps`);

/* ================================================================ API */
async function api(path, opts = {}) {
  const init = { method: opts.method || 'GET', headers: {}, credentials: 'same-origin' };
  if (opts.body !== undefined) { init.headers['Content-Type'] = 'application/json'; init.body = JSON.stringify(opts.body); }
  let res;
  try { res = await fetch(path, init); } catch { throw new Error('Sem conexão com o servidor.'); }
  let data = {};
  try { data = await res.json(); } catch { /* vazio */ }
  if (res.status === 401 && !opts.allow401) { state.me = null; go('entrar'); throw new Error(data.error || 'Faça login.'); }
  if (!res.ok) throw new Error(data.error || `Erro ${res.status}`);
  return data;
}

async function refreshMe() {
  state.me = await api('/api/me');
  return state.me;
}

/* ================================================================ UI helpers */
let toastTimer;
function toast(msg, ms = 2600) {
  const t = $('#toast');
  t.textContent = msg; t.classList.remove('hidden');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add('hidden'), ms);
}
function openModal(html, { onClose, dismiss = true } = {}) {
  const m = $('#modal');
  m.innerHTML = html; m.classList.remove('hidden');
  m.onclick = (e) => { if (dismiss && e.target === m) closeModal(); };
  m._onClose = onClose;
  $$('[data-close]', m).forEach((b) => (b.onclick = closeModal));
  return m;
}
function closeModal() {
  const m = $('#modal');
  if (m.classList.contains('hidden')) return;
  m.classList.add('hidden'); m.innerHTML = '';
  const cb = m._onClose; m._onClose = null; if (cb) cb();
}
const modalOpen = () => !$('#modal').classList.contains('hidden');
function waitModalClosed() {
  return new Promise((resolve) => { const m = $('#modal'); const prev = m._onClose; m._onClose = () => { if (prev) prev(); resolve(); }; });
}
function sys(title, body, { cls = '', icon = '!' } = {}) {
  return `<section class="sys ${cls}"><div class="sys-title"><span class="ico">${icon}</span><span class="tag">${title}</span></div>${body}</section>`;
}
const rankBadge = (r, size = '') => `<span class="rank ${size}" data-r="${esc(r)}"><span>${esc(r === 'N' ? 'N' : r === 'M' ? 'M' : r)}</span></span>`;
function confirmBox(title, text, okLabel = 'Confirmar', danger = false) {
  return new Promise((resolve) => {
    let val = false;
    openModal(sys(title, `<p>${text}</p><div class="btn-row"><button class="btn" data-close>Cancelar</button>
      <button class="btn ${danger ? 'danger' : 'primary'}" id="cf-ok">${esc(okLabel)}</button></div>`, { cls: danger ? 'danger' : '' }),
    { onClose: () => resolve(val) });
    $('#cf-ok').onclick = () => { val = true; closeModal(); };
  });
}

/* ================================================================ som / voz */
let audioCtx;
function beep(freq = 880, dur = 0.12, type = 'sine', vol = 0.18) {
  if (!state.prefs.sound) return;
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(vol, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + dur);
    o.connect(g).connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + dur + 0.02);
  } catch { /* sem áudio */ }
}
function chime() { beep(988, 0.12, 'triangle'); setTimeout(() => beep(1319, 0.3, 'triangle'), 110); }
function sysSound() { beep(660, 0.08, 'square', 0.06); setTimeout(() => beep(990, 0.18, 'sine', 0.12), 80); }
function speak(text) {
  if (!state.prefs.voice || !state.prefs.sound || !('speechSynthesis' in window)) return;
  try {
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(String(text)); u.lang = 'pt-BR'; u.rate = 1.15;
    speechSynthesis.speak(u);
  } catch { /* sem voz */ }
}
let wakeLock;
async function keepAwake(on) {
  try {
    if (on && 'wakeLock' in navigator && !wakeLock) wakeLock = await navigator.wakeLock.request('screen');
    if (!on && wakeLock) { await wakeLock.release(); wakeLock = null; }
  } catch { /* contexto inseguro (http) — ignora */ }
}

/* ================================================================ ticker (timers) */
let ticker = null;
function startTicker(fn) {
  stopTicker();
  const h = { alive: true, raf: 0, stop() { h.alive = false; cancelAnimationFrame(h.raf); } };
  const loop = (t) => { if (!h.alive) return; fn(t); if (h.alive) h.raf = requestAnimationFrame(loop); };
  ticker = h; h.raf = requestAnimationFrame(loop);
}
function stopTicker() { if (ticker) ticker.stop(); ticker = null; }
function ring(pct, big, ph = '', sub = '', rest = false) {
  const C = 2 * Math.PI * 100;
  return `<div class="ring-wrap" id="ring"><svg viewBox="0 0 220 220"><circle class="bgc" cx="110" cy="110" r="100"/>
    <circle class="fg ${rest ? 'rest' : ''}" id="ring-fg" cx="110" cy="110" r="100" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - pct)}"/></svg>
    <div class="mid"><div class="big" id="ring-big">${big}</div><div class="ph" id="ring-ph">${ph}</div><div class="sub" id="ring-sub">${sub}</div></div></div>`;
}
function setRing(pct, big, ph, sub) {
  const C = 2 * Math.PI * 100; const fg = $('#ring-fg'); if (!fg) return;
  fg.setAttribute('stroke-dashoffset', C * (1 - Math.max(0, Math.min(1, pct))));
  if (big !== undefined) $('#ring-big').textContent = big;
  if (ph !== undefined) $('#ring-ph').textContent = ph;
  if (sub !== undefined) $('#ring-sub').textContent = sub;
}
function pulseRing() { const r = $('#ring'); if (!r) return; r.classList.remove('beat'); void r.offsetWidth; r.classList.add('beat'); }

/* ================================================================ router */
const PUBLIC = new Set(['entrar', 'despertar']);
const NAV_ROUTES = new Set(['status', 'dungeon', 'missoes', 'habilidades', 'arquivo', 'historico', 'perfil']);
function go(route) { if (location.hash !== '#' + route) location.hash = route; else render(); }
window.addEventListener('hashchange', render);

async function render() {
  stopTicker();
  if (modalOpen()) closeModal();
  const route = (location.hash.slice(1) || 'status').split('?')[0];
  if (!PUBLIC.has(route) && !state.me) {
    try { await refreshMe(); } catch { return; }
  }
  const showNav = NAV_ROUTES.has(route);
  $('#nav').classList.toggle('hidden', !showNav);
  app.classList.toggle('no-nav', !showNav);
  $$('#nav a').forEach((a) => a.classList.toggle('on', a.dataset.r === route || (route === 'historico' || route === 'perfil') && a.dataset.r === 'status'));
  if (route !== 'treino') keepAwake(false);
  const view = VIEWS[route] || VIEWS.status;
  try { await view(); } catch (e) { app.innerHTML = sys('ERRO', `<p>${esc(e.message)}</p><button class="btn block" onclick="location.reload()">Tentar de novo</button>`, { cls: 'danger' }); }
  window.scrollTo(0, 0);
  updateNavBadge();
}
function updateNavBadge() {
  const a = $('#nav a[data-r=missoes] span'); if (!a) return;
  const q = state.me?.quests;
  a.innerHTML = 'Missões' + (q && !q.all_done ? '<span class="badge-dot"></span>' : '');
}

/* ================================================================ LOGIN */
const VIEWS = {};
VIEWS.entrar = async () => {
  app.innerHTML = `<div class="intro"><div class="logo">ARISE</div><div class="logo-sub">SHADOW TRAINING</div>
  ${sys('LOGIN', `<form id="lf"><label class="f"><span>Usuário</span><input type="text" name="username" autocomplete="username" required autocapitalize="off"></label>
    <label class="f"><span>Senha</span><input type="password" name="password" autocomplete="current-password" required></label>
    <button class="btn primary block">Entrar</button></form>
    <p class="center muted small" style="margin-top:16px">Ainda não despertou? <a href="#despertar">Tornar-se um Jogador</a></p>`, { icon: '◉' })}</div>`;
  $('#lf').onsubmit = async (e) => {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    try { await api('/api/login', { method: 'POST', body: f, allow401: true }); state.me = null; go('status'); } catch (err) { toast(err.message); }
  };
};

/* ================================================================ CADASTRO (DESPERTAR) */
const reg = { step: 0, d: { sex: 'M', goal: 'saude', has_bar: false, low_impact: false, a_push: 0, a_squat: 0, a_plank: 0, a_pull: 0 } };
VIEWS.despertar = async () => {
  const d = reg.d;
  const dots = `<div class="steps">${[1, 2, 3, 4].map((i) => `<i class="${i <= reg.step ? 'on' : ''}"></i>`).join('')}</div>`;
  if (reg.step === 0) {
    app.innerHTML = `<div class="intro"><div class="logo">ARISE</div><div class="logo-sub">SHADOW TRAINING</div>
      ${sys('NOTIFICAÇÃO', `<p class="center" id="tw" style="font-size:19px;min-height:84px"></p>
      <div class="btn-row"><button class="btn danger" id="no">Recusar</button><button class="btn primary" id="yes">Aceitar</button></div>
      <p class="center muted small" style="margin-top:16px">Já é um Jogador? <a href="#entrar">Entrar</a></p>`)}</div>`;
    typewriter($('#tw'), 'Você adquiriu as qualificações para se tornar um Jogador. Deseja aceitar?');
    sysSound();
    $('#yes').onclick = () => { reg.step = 1; render(); };
    $('#no').onclick = () => { $('#tw').textContent = 'Recusar não é uma opção. Seu coração vai parar em 0,02 segundos se você não aceitar.'; beep(200, .3, 'sawtooth', .08); };
    return;
  }
  if (reg.step === 1) {
    app.innerHTML = sys('REGISTRO DO JOGADOR', `${dots}
      <label class="f"><span>Nome de caçador</span><input type="text" id="name" value="${esc(d.name || '')}" placeholder="Ex.: Sung Jin-Woo" maxlength="40"></label>
      <label class="f"><span>Usuário (para entrar)</span><input type="text" id="username" value="${esc(d.username || '')}" autocapitalize="off" autocomplete="username"></label>
      <label class="f"><span>Senha</span><input type="password" id="password" value="${esc(d.password || '')}" autocomplete="new-password"></label>
      <div class="btn-row"><a class="btn" href="#entrar">Voltar</a><button class="btn primary" id="next">Próximo</button></div>`, { icon: '1' });
    $('#next').onclick = () => {
      d.name = $('#name').value.trim(); d.username = $('#username').value.trim(); d.password = $('#password').value;
      if (d.username.length < 3) return toast('Usuário precisa de pelo menos 3 caracteres.');
      if (d.password.length < 4) return toast('Senha precisa de pelo menos 4 caracteres.');
      if (!d.name) d.name = d.username;
      reg.step = 2; render();
    };
    return;
  }
  if (reg.step === 2) {
    app.innerHTML = sys('DADOS FÍSICOS', `${dots}
      <div class="grid2"><label class="f"><span>Peso (kg)</span><input type="number" id="weight" inputmode="decimal" step="0.1" value="${esc(d.weight || '')}"></label>
      <label class="f"><span>Altura (cm)</span><input type="number" id="height" inputmode="numeric" value="${esc(d.height || '')}"></label></div>
      <label class="f"><span>Idade</span><input type="number" id="age" inputmode="numeric" value="${esc(d.age || '')}"></label>
      <label class="f"><span>Sexo</span><div class="seg" id="sex">${[['M', 'Masculino'], ['F', 'Feminino'], ['O', 'Outro']].map(([k, l]) => `<button type="button" data-v="${k}" class="${d.sex === k ? 'on' : ''}">${l}</button>`).join('')}</div></label>
      <p class="center" id="bmi-out"></p>
      <div class="btn-row"><button class="btn" id="back">Voltar</button><button class="btn primary" id="next">Próximo</button></div>`, { icon: '2' });
    const upd = () => {
      const w = +$('#weight').value, h = +$('#height').value;
      $('#bmi-out').innerHTML = w && h ? `IMC <b class="num glow-text">${(w / (h / 100) ** 2).toFixed(1)}</b>` : '';
    };
    $$('#weight,#height').forEach((i) => (i.oninput = upd)); upd();
    $$('#sex button').forEach((b) => (b.onclick = () => { d.sex = b.dataset.v; $$('#sex button').forEach((x) => x.classList.toggle('on', x === b)); }));
    $('#back').onclick = () => { reg.step = 1; render(); };
    $('#next').onclick = () => {
      d.weight = +$('#weight').value; d.height = +$('#height').value; d.age = +$('#age').value;
      if (!(d.weight > 25 && d.weight < 350)) return toast('Informe um peso válido.');
      if (!(d.height > 100 && d.height < 250)) return toast('Informe a altura em centímetros (ex.: 175).');
      if (!(d.age >= 10 && d.age <= 100)) return toast('Informe uma idade válida.');
      const bmi = d.weight / (d.height / 100) ** 2;
      if (!d._liTouched) d.low_impact = d.age >= 55 || bmi >= 32;
      reg.step = 3; render();
    };
    return;
  }
  if (reg.step === 3) {
    app.innerHTML = sys('OBJETIVO', `${dots}
      <div class="choice" id="goals">${GOALS.map(([k, n, s]) => `<button type="button" data-v="${k}" class="${d.goal === k ? 'on' : ''}"><b>${n}</b><small>${s}</small></button>`).join('')}</div>
      <h3 style="margin-top:18px">Equipamento & limitações</h3>
      <label class="toggle"><div><b>Tenho barra fixa</b><div class="muted small">Libera barras, muscle-up e front lever.</div></div><input type="checkbox" id="bar" ${d.has_bar ? 'checked' : ''}><span class="sw"></span></label>
      <label class="toggle"><div><b>Baixo impacto (sem saltos)</b><div class="muted small">Recomendado para joelhos sensíveis, 55+ anos ou IMC alto.</div></div><input type="checkbox" id="li" ${d.low_impact || d.pregnant ? 'checked' : ''} ${d.pregnant ? 'disabled' : ''}><span class="sw"></span></label>
      ${d.sex !== 'M' ? pregnancyBlock(d) : ''}
      <div class="btn-row"><button class="btn" id="back">Voltar</button><button class="btn primary" id="next">Próximo</button></div>`, { icon: '3' });
    $$('#goals button').forEach((b) => (b.onclick = () => { d.goal = b.dataset.v; $$('#goals button').forEach((x) => x.classList.toggle('on', x === b)); }));
    $('#bar').onchange = (e) => (d.has_bar = e.target.checked);
    $('#li').onchange = (e) => { d.low_impact = e.target.checked; d._liTouched = true; };
    bindPregnancy(d, () => { $('#li').checked = d.pregnant || d.low_impact; $('#li').disabled = !!d.pregnant; });
    $('#back').onclick = () => { reg.step = 2; render(); };
    $('#next').onclick = () => {
      if (d.sex === 'M') d.pregnant = false;
      if (d.pregnant) {
        if (!(d.preg_week >= 1 && d.preg_week <= 42)) return toast('Informe a semana de gestação (1 a 42).');
        if (!d.preg_clearance) return toast('Confirme que tem liberação médica para se exercitar.');
      }
      reg.step = 4; render();
    };
    return;
  }
  // passo 4 — teste de despertar
  const field = (id, label, hint, extra = '') => `<label class="f"><span>${label}</span><div class="row"><input type="number" inputmode="numeric" id="${id}" value="${d[id] || ''}" placeholder="0">${extra}</div><div class="muted small">${hint}</div></label>`;
  app.innerHTML = d.pregnant ? sys('TESTE DE DESPERTAR', `${dots}
    <p class="muted small">Na gestação o teste é leve: <b>não vá até a falha</b>. Pare quando ficar difícil conversar ou se sentir qualquer desconforto (ou deixe 0).</p>
    ${field('a_push', 'Flexões na parede (confortáveis)', 'Mãos na parede na altura do peito.')}
    ${field('a_squat', 'Agachamentos com apoio (confortáveis)', 'Segurando numa cadeira ou batente.')}
    <div class="btn-row"><button class="btn" id="back">Voltar</button><button class="btn primary" id="go">Despertar</button></div>`, { icon: '4' })
    : sys('TESTE DE DESPERTAR', `${dots}
    <p class="muted small">O Sistema precisa medir seu poder atual para escolher os exercícios certos. Faça cada teste até a falha com boa forma (ou deixe 0 se não souber).</p>
    ${field('a_push', 'Flexões seguidas (máximo)', 'Flexão clássica. Se só consegue com joelhos, divida o número por 2.')}
    ${field('a_squat', 'Agachamentos seguidos (máximo)', 'Agachamento livre, coxa até a paralela.')}
    ${field('a_plank', 'Prancha (segundos)', 'Antebraços no chão, corpo reto.', '<button type="button" class="btn sm" id="plank-t" style="flex:none">⏱ Cronometrar</button>')}
    ${d.has_bar ? field('a_pull', 'Barras fixas (máximo)', 'Pull-up completa, braços esticando embaixo.') : ''}
    <div class="btn-row"><button class="btn" id="back">Voltar</button><button class="btn primary" id="go">Despertar</button></div>`, { icon: '4' });
  const read = () => ['a_push', 'a_squat', 'a_plank', 'a_pull'].forEach((k) => { const el = $('#' + k); if (el) d[k] = Math.max(0, parseInt(el.value, 10) || 0); });
  $('#back').onclick = () => { read(); reg.step = 3; render(); };
  if ($('#plank-t')) $('#plank-t').onclick = () => stopwatchModal('Prancha', (secs) => { $('#a_plank').value = secs; });
  $('#go').onclick = async () => {
    read();
    const body = Object.assign({}, d); delete body._liTouched;
    try {
      $('#go').disabled = true;
      await api('/api/register', { method: 'POST', body, allow401: true });
      reg.step = 0; reg.d = { sex: 'M', goal: 'saude', has_bar: false, low_impact: false };
      await refreshMe();
      awakenFx(`${esc(state.me.status.name)}<br><small style="font-size:16px;letter-spacing:.3em">O JOGADOR DESPERTOU</small>`);
      go('status');
    } catch (err) { toast(err.message); $('#go').disabled = false; }
  };
};

/* ---------------------------------------------------------------- modo gestante */
const PREG_STOP_SIGNS = [
  'Sangramento vaginal ou perda de líquido', 'Contrações regulares e dolorosas', 'Tontura, desmaio ou falta de ar antes do esforço',
  'Dor no peito', 'Dor de cabeça forte', 'Dor ou inchaço na panturrilha', 'Fraqueza muscular afetando o equilíbrio',
  'Diminuição dos movimentos do bebê',
];
function pregSafetyHtml(open = false) {
  return `<details class="preg-safety" ${open ? 'open' : ''}><summary>⚠ Sinais para PARAR na hora e procurar seu médico</summary>
    <ul>${PREG_STOP_SIGNS.map((s) => `<li>${s}</li>`).join('')}</ul>
    <p class="small">Regras do modo gestante: intensidade moderada (<b>teste da fala</b> — você deve conseguir conversar), nada de saltos,
    abdominais tipo crunch ou exercícios deitada de barriga para cima após a 12ª semana. Beba água, evite calor excessivo e não prenda a respiração.
    O app <b>não substitui</b> a orientação do seu obstetra.</p></details>`;
}
function pregnancyBlock(p) {
  return `<label class="toggle"><div><b>🤰 Estou grávida</b><div class="muted small">Troca por exercícios seguros para gestantes, ajustados à semana de gestação.</div></div>
      <input type="checkbox" id="preg" ${p.pregnant ? 'checked' : ''}><span class="sw"></span></label>
    <div id="preg-extra" class="${p.pregnant ? '' : 'hidden'}" style="padding:4px 0 8px">
      <label class="f"><span>Semana de gestação atual</span><input type="number" inputmode="numeric" id="preg-week" min="1" max="42" value="${esc(p.preg_week || '')}" placeholder="Ex.: 16"></label>
      <label class="row" style="gap:10px;align-items:flex-start;cursor:pointer"><input type="checkbox" id="preg-ok" ${p.preg_clearance ? 'checked' : ''} style="width:22px;height:22px;flex:none;margin-top:2px">
        <span class="small">Tenho <b>liberação do meu médico/obstetra</b> para praticar exercícios e não tenho contraindicações (placenta prévia, risco de parto prematuro, sangramento, pré-eclâmpsia etc.).</span></label>
      ${pregSafetyHtml()}
    </div>`;
}
function bindPregnancy(p, onChange = () => {}) {
  const t = $('#preg'); if (!t) return;
  t.onchange = () => { p.pregnant = t.checked; $('#preg-extra').classList.toggle('hidden', !t.checked); onChange(); };
  $('#preg-week').oninput = (e) => (p.preg_week = parseInt(e.target.value, 10) || null);
  $('#preg-ok').onchange = (e) => (p.preg_clearance = e.target.checked);
}

function typewriter(el, text, speed = 32) {
  el.textContent = ''; el.classList.add('typing'); let i = 0;
  const t = setInterval(() => { el.textContent = text.slice(0, ++i); if (i >= text.length) { clearInterval(t); el.classList.remove('typing'); } }, speed);
}
function awakenFx(html) {
  const d = document.createElement('div'); d.className = 'awaken'; d.innerHTML = `<div>${html}</div>`;
  document.body.appendChild(d); chime(); setTimeout(() => d.remove(), 3300);
}
function stopwatchModal(title, done) {
  let start = 0; let running = false;
  openModal(sys(title.toUpperCase(), `${ring(0, '0', 'PRONTO')}<div class="btn-row"><button class="btn" data-close>Cancelar</button><button class="btn primary" id="sw">Iniciar</button></div>`), { onClose: stopTicker });
  $('#sw').onclick = () => {
    if (!running) {
      running = true; start = performance.now(); $('#sw').textContent = 'Parar'; beep(880);
      startTicker(() => { const s = (performance.now() - start) / 1000; setRing((s % 60) / 60, Math.floor(s), 'SEGURANDO'); });
    } else { const s = Math.floor((performance.now() - start) / 1000); stopTicker(); chime(); closeModal(); done(s); }
  };
}

/* ================================================================ STATUS */
VIEWS.status = async () => {
  await refreshMe();
  const { status: s, quests: q, trained_today } = state.me;
  const r = s.rank;
  const pct = Math.round((s.xp / s.xp_next) * 100);
  const questDone = q.quests.filter((x) => x.status === 'done' && !x.penalty).length;
  const questTotal = q.quests.filter((x) => !x.penalty).length;
  const pr = s.profile;
  app.innerHTML = `
  ${pr.pregnant ? `<div class="preg-banner">🤰 <b>Modo gestante</b> · semana ${pr.preg_week} · ${pr.trimester}º trimestre
    ${pr.preg_week > 41 ? '<br><a href="#perfil">O bebê já chegou? Atualize seu perfil.</a>' : ''}</div>` : ''}
  ${q.penalty ? sys('ZONA DE PENALIDADE', `<p class="center">Você não completou a Missão Diária de ontem. Sua sequência foi zerada.<br>Complete a <b>missão de penalidade</b> hoje.</p><a class="btn danger block" href="#missoes">Ver penalidade</a>`, { cls: 'danger', icon: '☠' }) : ''}
  ${sys('STATUS', `
    <div class="player-head">
      <div class="lvl-box"><div class="n">${s.level}</div><div class="l">NÍVEL</div></div>
      <dl class="kv" style="flex:1">
        <dt>Nome</dt><dd>${esc(s.name)}</dd>
        <dt>Classe</dt><dd>${s.level >= 60 ? 'Necromante' : s.level >= 30 ? 'Assassino' : 'Nenhuma'}</dd>
        <dt>Título</dt><dd>${esc(r.title)}</dd>
      </dl>
      <div class="center">${rankBadge(r.code, 'md')}<div class="muted small" style="margin-top:12px">${esc(r.name)}</div></div>
    </div>
    <div class="bar-lbl"><span>EXP</span><b>${s.xp} / ${s.xp_next}</b></div><div class="bar"><i style="width:${pct}%"></i></div>
    <div class="grid2"><div><div class="bar-lbl"><span>HP</span><b>${s.hp}</b></div><div class="bar hp"><i style="width:100%"></i></div></div>
    <div><div class="bar-lbl"><span>MP</span><b>${s.mp}</b></div><div class="bar mp"><i style="width:100%"></i></div></div></div>
    <div class="stats">${['STR', 'AGI', 'VIT', 'PER', 'INT'].map((k) => [k, s.stats[k]]).map(([k, v]) => `<div class="stat" title="${esc(STAT_INFO[k])}"><span class="k">${k}</span><span class="v">${v}<small>${esc(STAT_INFO[k].split(' — ')[0])}</small></span>${s.stat_points > 0 ? `<button class="plus" data-stat="${k}" aria-label="Adicionar ponto em ${k}">+</button>` : ''}</div>`).join('')}</div>
    ${s.stat_points > 0 ? `<p class="center" style="margin:10px 0 0">Pontos disponíveis: <b class="num" style="color:var(--gold)">${s.stat_points}</b></p>` : ''}
    <p class="center muted small" style="margin:10px 0 0">${r.next_code ? `Próximo rank: <b>${r.next_code}</b> no nível ${r.next_level}` : 'Rank máximo alcançado.'}</p>
  `, { icon: '◉' })}
  ${sys('MISSÃO DIÁRIA', `
    <div class="row between"><div><b>Preparação para se tornar forte</b><div class="muted small">${questDone}/${questTotal} concluídas</div></div>
    <div class="streak">🔥 ${s.streak}</div></div>
    ${q.quests.map((x) => `<div class="quest ${x.status} ${x.penalty ? 'penalty' : ''}"><div class="qi">${esc(x.icon || '!')}</div><div class="qn"><b>${esc(x.name)}</b></div><div class="qt">${x.status === 'done' ? '✓' : x.status === 'failed' ? '✗' : fmtTarget(x.target, x.type)}</div></div>`).join('')}
    <a class="btn ${q.all_done ? '' : 'primary'} block" href="#missoes" style="margin-top:10px">${q.all_done ? 'Missão concluída ✓' : 'Ir para as missões'}</a>
  `, { icon: '❖', cls: q.all_done ? 'gold' : '' })}
  ${sys('DUNGEON DE HOJE', `
    <p class="center">${trained_today ? 'Você já limpou uma dungeon hoje. Treinar de novo ainda rende XP.' : 'Um portão se abriu. Entre para treinar e ganhar EXP.'}</p>
    <a class="btn ${trained_today ? '' : 'primary'} block" href="#dungeon">⛩ ${trained_today ? 'Ver dungeon' : 'Entrar na dungeon'}</a>
  `, { icon: '⛩' })}
  <div class="btn-row"><a class="btn sm" href="#historico">Histórico</a><a class="btn sm" href="#perfil">Perfil</a></div>`;
  $$('[data-stat]').forEach((b) => (b.onclick = async () => {
    try { await api('/api/stats/allocate', { method: 'POST', body: { stat: b.dataset.stat } }); beep(1200, .06); render(); } catch (e) { toast(e.message); }
  }));
};

/* ================================================================ DUNGEON (treino do dia) */
VIEWS.dungeon = async () => {
  const run = store.get('arise_run');
  const plan = await api('/api/workout/today');
  const ongoing = run && run.day === today() && !run.finished;
  app.innerHTML = `${ongoing ? sys('DUNGEON EM ANDAMENTO', `<p class="center">Você tem um treino em andamento (exercício ${run.i + 1}/${run.plan.exercises.length}).</p>
      <div class="btn-row"><button class="btn danger" id="discard">Descartar</button><a class="btn primary" href="#treino">Continuar</a></div>`, { cls: 'gold' }) : ''}
  ${plan.pregnancy ? `<div class="preg-banner">🤰 <b>Treino adaptado à gestação</b> · semana ${plan.pregnancy.week} (${plan.pregnancy.trimester}º tri)
    ${pregSafetyHtml()}</div>` : ''}
  ${sys(plan.gate.toUpperCase(), `
    <div class="row between wrap"><span class="chip on">${esc(plan.goal)}</span><span class="chip">~${plan.estimated_min} min</span>
    ${plan.streak_bonus > 1 ? `<span class="chip" style="color:var(--gold);border-color:var(--gold)">Bônus sequência ×${plan.streak_bonus}</span>` : ''}</div>
    ${plan.exercises.map((e, i) => `<div class="ex" data-i="${i}"><div class="gif"><img loading="lazy" src="${gifUrl(e.db)}" alt=""></div>
      <div class="info"><b>${esc(e.name)}</b><div class="meta">${esc(e.chain_name)} · Tier ${e.tier}/${e.tiers}${e.impact ? ' · <span style="color:#ffb454">salto</span>' : ''}</div>
      <div class="rx">${e.sets} × ${fmtTarget(e.target, e.type)}${e.type === 'reps' ? ` · cadência ${e.tempo.slice(0, 3).join('-')}` : ''} · desc. ${e.rest}s</div>
      <div class="mini-bar"><i style="width:${e.mastered ? 100 : ((e.level - 1) / 5) * 100}%"></i></div></div>${rankBadge(e.rank, 'sm')}</div>`).join('')}
    <label class="toggle"><div><b>Modo cadência</b><div class="muted small">Metrônomo guia cada repetição e conta sozinho. +15% EXP e +PER.</div></div><input type="checkbox" id="cad" ${state.prefs.cadence ? 'checked' : ''}><span class="sw"></span></label>
    <button class="btn primary block" id="start" style="margin-top:14px">⚔ Entrar na dungeon</button>
    <p class="muted small center">Barra de progresso = rank do exercício (E→S). Ao dominar (S) você evolui para o próximo tier.</p>
  `, { icon: '⛩' })}`;
  $$('.ex').forEach((el) => (el.onclick = () => exerciseModal(plan.exercises[+el.dataset.i])));
  $('#cad').onchange = (e) => { state.prefs.cadence = e.target.checked; savePrefs(); };
  $('#start').onclick = async () => {
    if (ongoing && !(await confirmBox('NOVA DUNGEON', 'Isso descarta o treino em andamento. Continuar?', 'Descartar e começar', true))) return;
    store.set('arise_run', { day: today(), plan, i: 0, s: 0, logs: plan.exercises.map(() => []), started: Date.now(), cadenceUsed: false, phase: 'ready' });
    beep(440, .1); setTimeout(() => chime(), 120);
    go('treino');
  };
  if (ongoing) $('#discard').onclick = async () => { if (await confirmBox('DESCARTAR', 'Descartar o treino em andamento?', 'Descartar', true)) { store.del('arise_run'); render(); } };
};

async function exerciseModal(e) {
  openModal(`<section class="sys"><button class="icon-btn close" data-close aria-label="Fechar">✕</button>
    <div class="sys-title"><span class="tag">${esc(e.chain_name || 'EXERCÍCIO')}</span></div>
    <div class="row" style="align-items:flex-start"><div style="flex:1"><h2>${esc(e.name)}</h2>
      <div class="muted small">Tier ${e.tier}/${e.tiers}${e.best ? ` · Recorde ${fmtTarget(e.best, e.type || 'reps')}` : ''}</div></div>${e.rank ? rankBadge(e.rank, 'md') : ''}</div>
    <div class="player-gif" style="margin:14px auto"><img src="${gifUrl(e.db)}" alt="Demonstração de ${esc(e.name)}"></div>
    <p>${esc(e.cue || '')}</p>
    ${e.next ? `<p class="small muted">Próxima evolução: <b style="color:var(--text)">${esc(e.next.name)}</b> (domine este exercício · nível ${e.next.req_level}+)</p>` : ''}
    <div id="api-info" class="small muted">Carregando dados da ExerciseDB…</div>
    <div id="modal-actions"></div></section>`);
  try {
    const info = await api(`/api/exercise/${encodeURIComponent(e.db)}`);
    const box = $('#api-info'); if (!box) return;
    box.innerHTML = `<p><b style="color:var(--text)">Músculo-alvo:</b> ${info.target.map(tMuscle).join(', ')}${info.secondary.length ? `<br><b style="color:var(--text)">Secundários:</b> ${info.secondary.map(tMuscle).join(', ')}` : ''}</p>
      <details><summary>Instruções originais (ExerciseDB · inglês)</summary><ol>${info.instructions.map((s) => `<li>${esc(s)}</li>`).join('')}</ol></details>`;
  } catch { const box = $('#api-info'); if (box) box.textContent = ''; }
}

/* ================================================================ TREINO (player) */
function saveRun(run) { store.set('arise_run', run); }
VIEWS.treino = async () => {
  const run = store.get('arise_run');
  if (!run || run.finished) return go('dungeon');
  keepAwake(true);
  renderRun(run);
};

function renderRun(run) {
  stopTicker();
  const ex = run.plan.exercises[run.i];
  const total = run.plan.exercises.length;
  const cad = state.prefs.cadence && ex.type === 'reps';
  const tempoTxt = ex.tempo.slice(0, 3).join('-');
  const dots = `<div class="set-dots">${Array.from({ length: ex.sets }, (_, k) => `<i class="${k < run.s ? 'done' : k === run.s ? 'cur' : ''}"></i>`).join('')}</div>`;
  const header = `<div class="topbar"><button class="icon-btn" id="quit" aria-label="Sair">✕</button>
    <div class="t">EXERCÍCIO ${run.i + 1}/${total} · SÉRIE ${Math.min(run.s + 1, ex.sets)}/${ex.sets}</div>
    <button class="icon-btn ${state.prefs.sound ? 'on' : ''}" id="snd" aria-label="Som">${state.prefs.sound ? '🔊' : '🔇'}</button>
    ${ex.type === 'reps' ? `<button class="icon-btn ${state.prefs.cadence ? 'on' : ''}" id="cdn" aria-label="Cadência">♪</button>` : ''}</div>`;
  const title = `<div class="row" style="margin:6px 0"><div style="flex:1"><h2 style="margin:0">${esc(ex.name)}</h2>
    <div class="muted small">${esc(ex.chain_name)} · Meta ${fmtTarget(ex.target, ex.type)}${ex.type === 'reps' ? ` · <span class="cadence-pill">cadência <b>${tempoTxt}</b></span>` : ''}</div></div>${rankBadge(ex.rank, 'sm')}</div>`;

  if (run.phase === 'rest') return renderRest(run, header);

  app.innerHTML = `${header}${title}<div class="player-gif"><img src="${gifUrl(ex.db)}" alt="Demonstração"></div>${dots}<div id="stage"></div>`;
  $('#quit').onclick = async () => {
    if (await confirmBox('SAIR DA DUNGEON', 'Seu progresso fica salvo. Você pode continuar depois pela aba Dungeon.', 'Sair')) go('dungeon');
  };
  $('#snd').onclick = () => { state.prefs.sound = !state.prefs.sound; savePrefs(); renderRun(run); };
  if ($('#cdn')) $('#cdn').onclick = () => { state.prefs.cadence = !state.prefs.cadence; savePrefs(); if (run.phase === 'active') run.phase = 'ready'; renderRun(run); };
  $('.player-gif').onclick = () => exerciseModal(ex);

  const stage = $('#stage');
  if (run.phase === 'input') return renderInput(run, ex, stage, run.pending ?? ex.target);

  if (run.phase === 'ready') {
    stage.innerHTML = `<p class="center muted small" style="margin:8px 0">${esc(ex.cue)}</p>
      <button class="btn primary block" id="go">${ex.type === 'time' ? '▶ Iniciar cronômetro' : cad ? '▶ Iniciar série com cadência' : '▶ Iniciar série'}</button>
      <button class="btn ghost block small" id="manual">Registrar manualmente</button>`;
    $('#manual').onclick = () => { run.phase = 'input'; run.pending = ex.target; saveRun(run); renderRun(run); };
    $('#go').onclick = () => {
      if (ex.type === 'reps' && !cad) { run.phase = 'input'; run.pending = ex.target; saveRun(run); renderRun(run); return; }
      countdown(stage, () => (ex.type === 'time' ? runTimer(run, ex, stage) : runCadence(run, ex, stage)));
    };
  }
}

function countdown(stage, then) {
  stage.innerHTML = ring(1, '3', 'PREPARE-SE');
  let n = 3; beep(660, .1);
  const t = setInterval(() => {
    n -= 1;
    if (!$('#ring')) return clearInterval(t);
    if (n <= 0) { clearInterval(t); beep(1320, .2); then(); return; }
    setRing(n / 3, String(n)); pulseRing(); beep(660, .1);
  }, 1000);
}

function runCadence(run, ex, stage) {
  const labels = ['DESCE', 'SEGURA', 'SOBE', 'SEGURA'];
  const freqs = [520, 700, 880, 700];
  const phases = ex.tempo.map((d, k) => ({ d: Math.max(0, d), label: labels[k], f: freqs[k] })).filter((p) => p.d > 0);
  const repDur = phases.reduce((a, p) => a + p.d, 0) * 1000;
  stage.innerHTML = `${ring(0, '0', phases[0].label, `meta ${ex.target}`)}
    <button class="btn danger block" id="stop">■ Terminar série</button>`;
  run.cadenceUsed = true; saveRun(run);
  const t0 = performance.now(); let lastPhase = -1; let lastRep = 0;
  startTicker((now) => {
    const el = now - t0; const rep = Math.floor(el / repDur); const inRep = el - rep * repDur;
    let acc = 0; let pi = 0;
    for (; pi < phases.length; pi++) { acc += phases[pi].d * 1000; if (inRep < acc) break; }
    pi = Math.min(pi, phases.length - 1);
    const key = rep * 10 + pi;
    if (key !== lastPhase) { lastPhase = key; beep(phases[pi].f, .09, 'sine', .15); pulseRing(); }
    if (rep !== lastRep) {
      lastRep = rep;
      if (rep === ex.target) { chime(); speak('Meta!'); } else speak(rep);
    }
    setRing(inRep / repDur, String(rep), phases[pi].label, rep >= ex.target ? 'META ✓ — continue se aguentar' : `meta ${ex.target}`);
  });
  $('#stop').onclick = () => {
    const reps = Math.floor((performance.now() - t0) / repDur);
    stopTicker(); run.phase = 'input'; run.pending = reps; saveRun(run); renderRun(run);
  };
}

function runTimer(run, ex, stage) {
  stage.innerHTML = `${ring(0, fmtTime(ex.target), 'EM AÇÃO')}<button class="btn danger block" id="stop">■ Parei antes</button>`;
  const t0 = performance.now(); let lastSec = -1;
  const finish = (secs) => { stopTicker(); run.phase = 'input'; run.pending = secs; saveRun(run); renderRun(run); };
  startTicker((now) => {
    const s = (now - t0) / 1000; const left = ex.target - s;
    const sec = Math.ceil(left);
    if (sec !== lastSec) { lastSec = sec; if (sec <= 3 && sec > 0) beep(880, .08); }
    setRing(s / ex.target, fmtTime(left));
    if (left <= 0) { chime(); speak('Tempo!'); finish(ex.target); }
  });
  $('#stop').onclick = () => finish(Math.floor((performance.now() - t0) / 1000));
}

function renderInput(run, ex, stage, value) {
  const step = ex.type === 'time' ? 5 : 1;
  let v = Math.max(0, value | 0);
  stage.innerHTML = `<p class="center muted small" style="margin:8px 0 2px">${ex.type === 'time' ? 'Segundos mantidos' : 'Repetições feitas'} nesta série</p>
    <div class="stepper"><button id="m">−</button><div class="v" id="v">${v}</div><button id="p">+</button></div>
    <p class="center small" id="hint"></p>
    <button class="btn primary block" id="ok">✓ Confirmar série</button>`;
  const upd = () => { $('#v').textContent = ex.type === 'time' ? fmtTime(v) : v; $('#hint').innerHTML = v >= ex.target ? '<span class="check">Meta atingida ✓</span>' : `<span class="muted">Meta: ${fmtTarget(ex.target, ex.type)}</span>`; };
  upd();
  $('#m').onclick = () => { v = Math.max(0, v - step); upd(); };
  $('#p').onclick = () => { v += step; upd(); };
  $('#ok').onclick = () => {
    run.logs[run.i][run.s] = v; delete run.pending; run.s += 1;
    if (run.s >= ex.sets) {
      if (run.i + 1 >= run.plan.exercises.length) return finishRun(run);
      run.i += 1; run.s = 0;
    }
    run.phase = 'rest'; run.restUntil = Date.now() + ex.rest * 1000; run.restTotal = ex.rest;
    saveRun(run); sysSound(); renderRun(run);
  };
}

function renderRest(run, header) {
  const ex = run.plan.exercises[run.i];
  app.innerHTML = `${header}${sys('DESCANSO', `${ring(1, '', 'RECUPERANDO', '', true)}
    <p class="center muted small">A seguir: <b style="color:var(--text)">${esc(ex.name)}</b> — série ${run.s + 1}/${ex.sets}, meta ${fmtTarget(ex.target, ex.type)}</p>
    ${run.plan.pregnancy ? '<p class="center small" style="color:#ffb3c7">💧 Beba um gole de água. Sentiu algo estranho? Pare o treino — nenhuma missão vale mais que você e o bebê.</p>' : ''}
    <div class="ex" style="cursor:default"><div class="gif"><img src="${gifUrl(ex.db)}" alt=""></div><div class="info"><b>${esc(ex.name)}</b><div class="meta">${esc(ex.cue)}</div></div></div>
    <div class="btn-row"><button class="btn" id="add">+15s</button><button class="btn primary" id="skip">Pular ▶</button></div>`, { icon: '⏸' })}`;
  $('#quit').onclick = async () => { if (await confirmBox('SAIR DA DUNGEON', 'Seu progresso fica salvo.', 'Sair')) go('dungeon'); };
  $('#snd').onclick = () => { state.prefs.sound = !state.prefs.sound; savePrefs(); renderRun(run); };
  if ($('#cdn')) $('#cdn').onclick = () => { state.prefs.cadence = !state.prefs.cadence; savePrefs(); renderRun(run); };
  const end = () => { stopTicker(); run.phase = 'ready'; delete run.restUntil; saveRun(run); renderRun(run); };
  $('#skip').onclick = end;
  $('#add').onclick = () => { run.restUntil += 15000; run.restTotal += 15; saveRun(run); };
  let lastSec = -1;
  startTicker(() => {
    const left = (run.restUntil - Date.now()) / 1000;
    const sec = Math.ceil(left);
    if (sec !== lastSec) { lastSec = sec; if (sec <= 3 && sec > 0) beep(700, .07); }
    setRing(left / run.restTotal, fmtTime(left));
    if (left <= 0) { chime(); end(); }
  });
}

async function finishRun(run) {
  stopTicker();
  run.finished = true; saveRun(run);
  app.innerHTML = sys('PROCESSANDO', '<p class="center typing">O Sistema está calculando suas recompensas</p>');
  const payload = {
    split: run.plan.split, cadence_used: !!run.cadenceUsed, duration_s: Math.round((Date.now() - run.started) / 1000),
    exercises: run.plan.exercises.map((e, k) => ({ key: e.key, sets: run.logs[k].filter((x) => x != null) })),
  };
  try {
    const res = await api('/api/workout/complete', { method: 'POST', body: payload });
    store.del('arise_run');
    store.set('arise_result', res);
    go('resultado');
  } catch (e) {
    run.finished = false; saveRun(run);
    app.innerHTML = sys('ERRO', `<p>${esc(e.message)}</p><button class="btn primary block" id="retry">Tentar enviar de novo</button>`, { cls: 'danger' });
    $('#retry').onclick = () => finishRun(run);
  }
}

/* ================================================================ RESULTADO */
VIEWS.resultado = async () => {
  const res = store.get('arise_result');
  if (!res) return go('status');
  const s = res.status;
  app.innerHTML = `${sys('DUNGEON LIMPA', `
    <div class="center"><div class="muted small">EXP OBTIDA</div><div class="num glow-text" style="font-size:56px" id="xpc">0</div>
    <div class="muted small">base ${res.base_xp} + bônus ${res.session_bonus}${res.multiplier > 1 ? ` · sequência ×${res.multiplier}` : ''}${res.cadence_bonus ? ' · cadência +15%' : ''}</div></div>
    ${res.exercises.map((e) => `<div class="quest ${e.cleared ? 'done' : ''}"><div class="qi">${e.cleared ? '✓' : '·'}</div>
      <div class="qn"><b>${esc(e.name)}</b><div class="muted small">${e.sets.map((x) => (e.type === 'time' ? fmtTime(x) : x)).join(' / ')} · meta ${fmtTarget(e.target, e.type)}</div></div>
      <div class="row">${e.rank_from !== e.rank_to ? `${rankBadge(e.rank_from, 'sm')}<span class="muted">→</span>` : ''}${rankBadge(e.rank_to, 'sm')}</div></div>`).join('')}
    ${Object.keys(res.stat_gain || {}).length ? `<p class="center">Atributos: ${Object.entries(res.stat_gain).map(([k, v]) => `<b class="glow-text">${k} +${v}</b>`).join(' · ')}</p>` : ''}
  `, { icon: '✓', cls: 'gold' })}
  ${res.evolutions.length ? sys('NOVA HABILIDADE', res.evolutions.map((e) => `<div class="ex" style="cursor:default"><div class="gif"><img src="${gifUrl(e.db)}" alt=""></div>
      <div class="info"><div class="meta">${esc(e.chain)} evoluiu</div><b>${esc(e.from)} → ${esc(e.to)}</b></div></div>`).join(''), { icon: '⬆' }) : ''}
  ${res.blocked.length ? sys('EVOLUÇÃO BLOQUEADA', res.blocked.map((b) => `<p class="small">${esc(b.chain)}: <b>${esc(b.to)}</b> requer nível ${b.req_level}. Continue ganhando EXP.</p>`).join(''), { icon: '🔒' }) : ''}
  <div class="bar-lbl"><span>NÍVEL ${s.level}</span><b>${s.xp} / ${s.xp_next}</b></div><div class="bar"><i style="width:${(s.xp / s.xp_next) * 100}%"></i></div>
  <div class="btn-row"><a class="btn" href="#status">Status</a><a class="btn primary" href="#missoes">Missão diária ▶</a></div>`;
  let cur = 0; const target = res.xp; const t0 = performance.now();
  startTicker((now) => { cur = Math.min(target, Math.round(target * Math.min(1, (now - t0) / 1200))); const el = $('#xpc'); if (el) el.textContent = '+' + cur; if (cur >= target) stopTicker(); });
  chime();
  if (res.shown) return;
  res.shown = true; store.set('arise_result', res);
  await celebrate(res.level_ups, res.rank_up, s);
};

async function celebrate(levelUps, rankUp, s) {
  if (!levelUps || !levelUps.length) return;
  const lv = levelUps[levelUps.length - 1];
  openModal(`<section class="sys levelup"><div class="muted small">[ NOTIFICAÇÃO ]</div><div class="big">LEVEL UP!</div>
    <p style="font-size:20px">Nível <b class="num glow-text">${lv}</b></p>
    <p class="muted">+${levelUps.length * 3} pontos de atributo para distribuir no Status.</p>
    <button class="btn primary" data-close>OK</button></section>`);
  sysSound(); setTimeout(chime, 200);
  await waitModalClosed();
  if (rankUp) {
    openModal(`<section class="sys levelup gold"><div class="muted small">[ REAVALIAÇÃO DO SISTEMA ]</div>
      <div style="margin:30px 0">${rankBadge(s.rank.code, 'xl')}</div><div class="big" style="font-size:30px">${esc(s.rank.name)}</div>
      <p>Novo título: <b>${esc(s.rank.title)}</b></p><button class="btn gold" data-close>Levantar-se</button></section>`);
    chime(); setTimeout(chime, 400);
    await waitModalClosed();
  }
}

/* ================================================================ MISSÕES */
VIEWS.missoes = async () => {
  const q = await api('/api/quests/today');
  if (state.me) state.me.quests = q;
  const day = today();
  const counterKey = (k) => `arise_q_${day}_${k}`;
  const penalty = q.quests.filter((x) => x.penalty);
  const main = q.quests.filter((x) => !x.penalty);
  const questRow = (x) => {
    const cnt = store.get(counterKey(x.key), 0);
    let action = '';
    if (x.status === 'pending') {
      action = x.type === 'time'
        ? `<div class="btn-row"><button class="btn sm danger" data-fail="${x.key}">Não consegui</button><button class="btn sm primary" data-timer="${x.key}">▶ Iniciar ${fmtTime(x.target)}</button></div>`
        : `<div class="row" style="margin-top:8px"><button class="btn sm" data-add="${x.key}" data-n="-1">−1</button><div class="num spacer center" style="font-size:22px">${cnt}/${x.target}</div>
            <button class="btn sm" data-add="${x.key}" data-n="1">+1</button><button class="btn sm" data-add="${x.key}" data-n="5">+5</button><button class="btn sm" data-add="${x.key}" data-n="10">+10</button></div>
           <div class="mini-bar"><i style="width:${Math.min(100, (cnt / x.target) * 100)}%"></i></div>
           <div class="btn-row"><button class="btn sm danger" data-fail="${x.key}">Não consegui</button><button class="btn sm primary" data-done="${x.key}" ${cnt >= x.target ? '' : 'disabled'}>Concluir</button></div>`;
    }
    const res = x.status === 'done' ? `<span class="check">✓ +${x.xp} EXP</span>` : x.status === 'failed' ? '<span style="color:var(--danger)">✗ falhou</span>' : `<span class="muted">+${x.xp} EXP</span>`;
    return `<div class="quest ${x.status} ${x.penalty ? 'penalty' : ''}" style="flex-wrap:wrap">
      <div class="qi">${esc(x.icon || '!')}</div><div class="qn"><b>${esc(x.name)}</b><div class="muted small">${esc(x.desc)}</div></div>
      <div class="qt">${fmtTarget(x.target, x.type)}<div class="small center">${res}</div></div>
      ${x.db ? `<button class="btn sm ghost" data-gif="${x.db}" data-name="${esc(x.name)}" style="width:100%;min-height:30px">ver demonstração</button>` : ''}
      <div style="width:100%">${action}</div></div>`;
  };
  app.innerHTML = `
    ${penalty.length && penalty.some((x) => x.status !== 'done') ? sys('PENALIDADE', `<p class="center small">Aviso: você não concluiu a missão diária de ontem. Sobreviva à penalidade.</p>${penalty.map(questRow).join('')}`, { cls: 'danger', icon: '☠' }) : ''}
    ${sys('MISSÃO DIÁRIA', `
      <h2 class="center" style="font-size:15px">Preparação para se tornar forte</h2>
      <p class="center muted small">Faça depois do treino. Cada sucesso aumenta a meta de amanhã — e o EXP que ela rende.</p>
      ${main.map(questRow).join('')}
      <div style="margin-top:12px;border-top:1px solid var(--line-soft);padding-top:10px">
        <div class="row between"><span class="muted small">RECOMPENSAS</span><span class="streak">🔥 ${q.streak} dia(s)</span></div>
        <p class="small" style="margin:6px 0 0">EXP ×${q.reward_mult} · +1 INT · bônus de conclusão · a sequência também multiplica o EXP dos treinos</p>
      </div>
      ${state.me?.status?.profile?.pregnant
        ? '<p class="warn-text" style="color:#ffb3c7">Modo gestante: sem penalidades. Descansar quando o corpo pedir também é treino. 🤰</p>'
        : '<p class="warn-text">AVISO: a não conclusão da Missão Diária resultará em uma penalidade apropriada.</p>'}
    `, { icon: '❖', cls: q.all_done ? 'gold' : '' })}
    ${q.all_done ? sys('MISSÃO CONCLUÍDA', '<p class="center">Recompensas entregues. Descanse, Jogador. Amanhã a missão será mais difícil.</p>', { cls: 'gold', icon: '✓' }) : ''}`;

  $$('[data-gif]').forEach((b) => (b.onclick = () => openModal(sys(esc(b.dataset.name).toUpperCase(), `<div class="player-gif"><img src="${gifUrl(b.dataset.gif)}" alt=""></div><button class="btn block" data-close style="margin-top:12px">Fechar</button>`))));
  $$('[data-add]').forEach((b) => (b.onclick = () => {
    const k = b.dataset.add; const n = Math.max(0, store.get(counterKey(k), 0) + (+b.dataset.n));
    store.set(counterKey(k), n); beep(900 + Math.min(n, 50) * 8, .05); render();
  }));
  $$('[data-done]').forEach((b) => (b.onclick = () => resolveQuest(b.dataset.done, true)));
  $$('[data-fail]').forEach((b) => (b.onclick = async () => {
    if (await confirmBox('DESISTIR', 'Registrar a missão como não concluída? A meta se mantém (e cai após 2 falhas seguidas).', 'Registrar falha', true)) resolveQuest(b.dataset.fail, false);
  }));
  $$('[data-timer]').forEach((b) => (b.onclick = () => questTimer(q.quests.find((x) => x.key === b.dataset.timer))));
};

function questTimer(x) {
  openModal(sys(x.name.toUpperCase(), `<p class="center muted small">${esc(x.desc)}</p>${ring(1, '5', 'PREPARE-SE')}
    <div class="btn-row"><button class="btn danger" id="giveup">Desisti</button></div>`, { icon: x.icon || '!' }), { dismiss: false, onClose: () => { stopTicker(); keepAwake(false); } });
  keepAwake(true);
  let t0 = performance.now(); let prep = true; let lastSec = -1;
  startTicker((now) => {
    const el = (now - t0) / 1000;
    if (prep) {
      const left = 5 - el; const sec = Math.ceil(left);
      if (sec !== lastSec) { lastSec = sec; beep(660, .08); }
      setRing(left / 5, String(Math.max(0, sec)), 'PREPARE-SE');
      if (left <= 0) { prep = false; t0 = now; beep(1320, .25); speak('Vai!'); }
      return;
    }
    const left = x.target - el; const sec = Math.ceil(left);
    if (sec !== lastSec) {
      lastSec = sec;
      if (sec <= 5 && sec > 0) beep(880, .07);
      if (sec > 0 && sec % 30 === 0 && sec !== x.target) speak(`${sec} segundos`);
    }
    setRing(left / x.target, fmtTime(left), 'SEGURE', `meta ${fmtTime(x.target)}`);
    if (left <= 0) { stopTicker(); chime(); speak('Missão concluída'); closeModal(); resolveQuest(x.key, true); }
  });
  $('#giveup').onclick = () => { stopTicker(); closeModal(); resolveQuest(x.key, false); };
}

async function resolveQuest(key, success) {
  try {
    const res = await api(`/api/quests/${key}`, { method: 'POST', body: { success } });
    if (success) {
      sysSound();
      const nxt = res.next_target != null ? `<p class="muted">Meta de amanhã: <b style="color:var(--text)">${key === 'plank' || key === 'wall_sit' ? fmtTime(res.next_target) : res.next_target}</b></p>` : '';
      openModal(sys('MISSÃO CUMPRIDA', `<p class="center" style="font-size:20px">+<b class="num glow-text">${res.xp}</b> EXP</p>${nxt}
        ${res.quest_complete ? `<p class="center">Missão diária completa! Bônus <b class="glow-text">+${res.bonus}</b> EXP · INT +1 · 🔥 ${res.streak}</p>` : ''}
        <button class="btn primary block" data-close>OK</button>`, { cls: 'gold', icon: '✓' }));
      await waitModalClosed();
      if (res.level_ups?.length) await celebrate(res.level_ups, false, res.status);
    } else {
      toast(`Falha registrada. Meta: ${res.next_target}.`);
    }
    state.me = null; render();
  } catch (e) { toast(e.message); }
}

/* ================================================================ HABILIDADES */
VIEWS.habilidades = async () => {
  const tree = await api('/api/skills');
  app.innerHTML = `<h1 class="center glow-text" style="margin-top:8px">HABILIDADES</h1>
    <p class="center muted small">Cada linha é uma árvore de evolução. Domine o exercício atual (rank S) e alcance o nível exigido para desbloquear o próximo.</p>
    <div class="chips" id="tabs">${tree.map((c, i) => `<button data-i="${i}" class="${i === 0 ? 'on' : ''}">${c.icon} ${esc(c.name)}</button>`).join('')}</div>
    <div id="tree"></div>`;
  const show = (i) => {
    const c = tree[i];
    $$('#tabs button').forEach((b) => b.classList.toggle('on', +b.dataset.i === i));
    $('#tree').innerHTML = sys(`${c.name.toUpperCase()} · ${c.stat}`, `<p class="center muted small">Tier ${c.tier} de ${c.tiers}</p>
      ${c.exercises.map((e, k) => `<div class="ex ${e.state}" data-k="${k}"><div class="gif"><img loading="lazy" src="${gifUrl(e.db)}" alt=""></div>
        <div class="info"><div class="meta">TIER ${e.tier}${e.bar ? ' · barra' : ''}${e.impact ? ' · salto' : ''}</div><b>${e.state === 'locked' ? '???' : ''} ${esc(e.name)}</b>
        <div class="rx">${e.state === 'current' ? '▶ ATUAL' : e.state === 'done' ? '✓ Superado' : `🔒 Nível ${e.req_level}+`}${e.best ? ` · recorde ${e.best}` : ''}</div></div>
        ${e.state !== 'locked' ? rankBadge(e.rank, 'sm') : ''}</div>`).join('')}`, { icon: c.icon });
    $$('#tree .ex').forEach((el) => (el.onclick = async () => {
      const e = c.exercises[+el.dataset.k];
      await exerciseModal(e);
      const box = $('#modal-actions');
      if (box && e.state === 'done') {
        box.innerHTML = '<button class="btn block" id="use">Usar esta versão nos próximos treinos</button><p class="muted small center">Útil em dias de dor ou para refinar a técnica.</p>';
        $('#use').onclick = async () => {
          try { await api(`/api/skills/${c.key}/select`, { method: 'POST', body: { key: e.key } }); toast('Exercício atualizado.'); closeModal(); VIEWS.habilidades(); } catch (err) { toast(err.message); }
        };
      }
    }));
  };
  $$('#tabs button').forEach((b) => (b.onclick = () => show(+b.dataset.i)));
  show(0);
};

/* ================================================================ ARQUIVO (ExerciseDB) */
const lib = { part: '', q: '' };
VIEWS.arquivo = async () => {
  app.innerHTML = `<h1 class="center glow-text" style="margin-top:8px">ARQUIVO DO SISTEMA</h1>
    <p class="center muted small">Exercícios de peso corporal da <a href="https://oss.exercisedb.dev" target="_blank" rel="noopener">ExerciseDB</a> (API pública) com GIF.</p>
    <div class="search"><input type="text" id="q" placeholder="Buscar (ex.: push, squat, abs)" value="${esc(lib.q)}"><button class="btn" id="live" title="Buscar na API">API</button></div>
    <div class="chips" id="parts">${BODY_PARTS.map(([k, l]) => `<button data-p="${k}" class="${lib.part === k ? 'on' : ''}">${l}</button>`).join('')}</div>
    <p class="muted small" id="count"></p><div class="lib-grid" id="grid"></div>
    <div class="center" style="margin-top:16px"><button class="btn sm" id="sync">↻ Sincronizar catálogo com a API</button></div>`;
  const load = async () => {
    const d = await api(`/api/library?part=${encodeURIComponent(lib.part)}&q=${encodeURIComponent(lib.q)}`);
    $('#count').textContent = `${d.count} de ${d.total} exercícios${d.count > d.items.length ? ` (mostrando ${d.items.length})` : ''}`;
    drawGrid(d.items);
  };
  const drawGrid = (items) => {
    $('#grid').innerHTML = items.map((e, i) => `<button class="lib-card" data-i="${i}"><div class="gif"><img loading="lazy" src="${gifUrl(e.id)}" alt=""></div><div class="n">${esc(e.name)}</div></button>`).join('') || '<p class="muted">Nada encontrado.</p>';
    $$('#grid .lib-card').forEach((b) => (b.onclick = () => { const e = items[+b.dataset.i]; exerciseModal({ name: e.name, db: e.id, chain_name: (e.bodyParts || []).join(', '), cue: '' }); }));
  };
  let deb;
  $('#q').oninput = (e) => { lib.q = e.target.value; clearTimeout(deb); deb = setTimeout(load, 250); };
  $$('#parts button').forEach((b) => (b.onclick = () => { lib.part = b.dataset.p; $$('#parts button').forEach((x) => x.classList.toggle('on', x === b)); load(); }));
  $('#live').onclick = async () => {
    if ((lib.q || '').length < 2) return toast('Digite algo para buscar na API.');
    $('#count').textContent = 'Consultando ExerciseDB…';
    try { const d = await api(`/api/library/search?q=${encodeURIComponent(lib.q)}`); $('#count').textContent = `${d.items.length} resultado(s) ao vivo (todos os equipamentos)`; drawGrid(d.items); } catch (e) { toast(e.message); }
  };
  $('#sync').onclick = async () => {
    if (!(await confirmBox('SINCRONIZAR', 'Baixar o catálogo atualizado da ExerciseDB? Leva cerca de 1 minuto.', 'Sincronizar'))) return;
    toast('Sincronizando… aguarde.', 60000);
    try { const d = await api('/api/library/sync', { method: 'POST' }); toast(`Catálogo atualizado: ${d.total} exercícios.`); load(); } catch (e) { toast(e.message); }
  };
  await load();
};

/* ================================================================ HISTÓRICO */
VIEWS.historico = async () => {
  const h = await api('/api/history');
  const s = state.me.status;
  const w = h.weights;
  let chart = '<p class="muted small">Atualize seu peso no Perfil para ver a evolução.</p>';
  if (w.length >= 2) {
    const ys = w.map((x) => x.weight); const mn = Math.min(...ys) - 1; const mx = Math.max(...ys) + 1;
    const pts = w.map((x, i) => [10 + (i / (w.length - 1)) * 280, 10 + (1 - (x.weight - mn) / (mx - mn)) * 110]);
    const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ');
    chart = `<svg class="chart" viewBox="0 0 300 140"><path class="a" d="${d} L${pts[pts.length - 1][0]},130 L10,130 Z"/><path class="l" d="${d}"/>
      <text x="10" y="138">${esc(w[0].day.slice(5))} · ${w[0].weight}kg</text><text x="290" y="138" text-anchor="end">${w[w.length - 1].weight}kg</text></svg>`;
  }
  const xs = h.workouts.slice(0, 24).reverse(); const mxp = Math.max(1, ...xs.map((x) => x.xp));
  app.innerHTML = `<h1 class="center glow-text" style="margin-top:8px">REGISTROS</h1>
    ${sys('RESUMO', `<div class="grid2 center"><div><div class="num" style="font-size:28px">${s.sessions}</div><div class="muted small">dungeons</div></div>
      <div><div class="num" style="font-size:28px">${s.total_xp}</div><div class="muted small">EXP total</div></div>
      <div><div class="num streak" style="font-size:28px">${s.streak}</div><div class="muted small">sequência atual</div></div>
      <div><div class="num" style="font-size:28px">${s.best_streak}</div><div class="muted small">melhor sequência</div></div></div>`, { icon: '☷' })}
    ${sys('EXP POR DUNGEON', xs.length ? `<div class="bars-chart">${xs.map((x) => `<i title="${x.day}: ${x.xp} EXP" style="height:${(x.xp / mxp) * 100}%"></i>`).join('')}</div>` : '<p class="muted small">Nenhuma dungeon ainda.</p>', { icon: '▲' })}
    ${sys('PESO', chart, { icon: '⚖' })}
    ${sys('RECORDES DAS MISSÕES', h.missions.map((m) => `<div class="row between hist-item"><span>${esc(m.name)}</span><span class="muted small">meta atual <b style="color:var(--text)">${fmtTarget(m.target, m.type)}</b> · recorde ${m.best ? fmtTarget(m.best, m.type) : '—'} · ${m.completed}×</span></div>`).join(''), { icon: '❖' })}
    ${sys('DUNGEONS RECENTES', h.workouts.map((x) => `<details class="hist-item"><summary><b>${x.day.split('-').reverse().join('/')}</b> · Portão ${x.split === 'A' ? 'Azul' : 'Vermelho'} · <span class="glow-text">+${x.xp} EXP</span>${x.cadence ? ' · ♪' : ''}${x.duration_s ? ` · ${Math.round(x.duration_s / 60)} min` : ''}</summary>
      ${x.exercises.map((e) => `<div class="small" style="padding:4px 0 0 12px">${e.cleared ? '✓' : '·'} ${esc(e.name)} — ${e.sets.map((v) => (e.type === 'time' ? fmtTime(v) : v)).join('/')} (${e.rank_to})</div>`).join('')}</details>`).join('') || '<p class="muted small">Nenhuma dungeon ainda.</p>', { icon: '⛩' })}
    <a class="btn block" href="#status">Voltar</a>`;
};

/* ================================================================ PERFIL */
VIEWS.perfil = async () => {
  await refreshMe();
  const s = state.me.status; const p = s.profile;
  const preg = { pregnant: p.pregnant, preg_week: p.preg_week, preg_clearance: p.pregnant };
  app.innerHTML = sys('PERFIL DO JOGADOR', `
    <p class="center">IMC <b class="num glow-text">${p.bmi ?? '—'}</b> <span class="muted small">(${esc(p.bmi_label)})</span></p>
    <form id="pf">
      <label class="f"><span>Nome de caçador</span><input type="text" name="name" value="${esc(s.name)}" maxlength="40"></label>
      <div class="grid2"><label class="f"><span>Peso (kg)</span><input type="number" step="0.1" inputmode="decimal" name="weight" value="${p.weight ?? ''}"></label>
      <label class="f"><span>Altura (cm)</span><input type="number" inputmode="numeric" name="height" value="${p.height ?? ''}"></label></div>
      <label class="f"><span>Idade</span><input type="number" inputmode="numeric" name="age" value="${p.age ?? ''}"></label>
      <label class="f"><span>Objetivo</span><select name="goal">${GOALS.map(([k, n]) => `<option value="${k}" ${p.goal === k ? 'selected' : ''}>${n}</option>`).join('')}</select></label>
      <label class="toggle"><div><b>Tenho barra fixa</b></div><input type="checkbox" name="has_bar" ${p.has_bar ? 'checked' : ''}><span class="sw"></span></label>
      <label class="toggle"><div><b>Baixo impacto (sem saltos)</b></div><input type="checkbox" name="low_impact" ${p.low_impact ? 'checked' : ''}><span class="sw"></span></label>
      ${p.sex !== 'M' ? pregnancyBlock(preg) : ''}
      <label class="toggle"><div><b>Voz contando repetições</b></div><input type="checkbox" id="voice" ${state.prefs.voice ? 'checked' : ''}><span class="sw"></span></label>
      <label class="f"><span>Nova senha (opcional)</span><input type="password" name="password" autocomplete="new-password"></label>
      <button class="btn primary block">Salvar</button>
    </form>
    <p class="muted small" style="margin-top:16px">📱 <b>Instalar como app:</b> no Chrome do celular, menu ⋮ → <i>Adicionar à tela inicial</i>.</p>
    <div class="btn-row"><a class="btn" href="#status">Voltar</a><button class="btn danger" id="logout">Sair</button></div>`, { icon: '◉' });
  $('#voice').onchange = (e) => { state.prefs.voice = e.target.checked; savePrefs(); };
  bindPregnancy(preg);
  $('#pf').onsubmit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const body = { name: f.get('name'), weight: f.get('weight'), height: f.get('height'), age: f.get('age'), goal: f.get('goal'),
      has_bar: f.get('has_bar') === 'on', low_impact: f.get('low_impact') === 'on' };
    if (p.sex !== 'M') Object.assign(body, { pregnant: !!preg.pregnant, preg_week: preg.preg_week, preg_clearance: !!preg.preg_clearance });
    if (f.get('password')) body.password = f.get('password');
    try { await api('/api/profile', { method: 'PUT', body }); toast('Perfil atualizado. O Sistema recalculou seus treinos.'); state.me = null; render(); } catch (err) { toast(err.message); }
  };
  $('#logout').onclick = async () => { await api('/api/logout', { method: 'POST' }); state.me = null; store.del('arise_run'); go('entrar'); };
};

// GIF indisponível na ExerciseDB -> placeholder no lugar da imagem quebrada
document.addEventListener('error', (e) => {
  const img = e.target;
  if (img.tagName !== 'IMG' || img.dataset.failed) return;
  img.dataset.failed = '1';
  img.src = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#0b1630"/><text x="50" y="56" font-size="12" text-anchor="middle" fill="#7f95b8" font-family="sans-serif">sem GIF</text></svg>');
}, true);

/* ================================================================ boot */
(async function boot() {
  const route = location.hash.slice(1);
  if (!PUBLIC.has(route)) {
    try { state.me = await api('/api/me', { allow401: true }); } catch {
      const seen = store.get('arise_seen');
      store.set('arise_seen', true);
      return go(seen ? 'entrar' : 'despertar');
    }
  }
  store.set('arise_seen', true);
  render();
})();
