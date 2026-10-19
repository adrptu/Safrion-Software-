// ===== MAPA-FROTA F1 · camada "Máquinas" do Mapa (IN-04): marcadores, lista, painel do conjunto e "Ver no mapa" (#frota=OS-…).
// Regras puras em frota.js; fixture da simulação em dados_frota.py (FROTA0). Desenha em contêineres vazios do template ([data-frota-camada],
// [data-frota-painel], [data-frota-leg]), por código próprio e com chave por O.S., para não perder o foco a cada leitura (como os anéis do MUX).
// Só leitura: nada aqui grava no cenário. A posição é simulada e rotulada; a área feita e o saldo vêm da O.S.
const FRUI = {self: null, timer: 0, mk: {}, lg: {}, grp: {}, ultimo: '', modelo: null, origem: null, hashOk: false, aviso: ''};
const FR_VE_POS = ['gestor', 'pcp', 'agronomo', 'pcm'], FR_VE_NOME = ['gestor', 'pcp'];
const FR_SELO = {Trabalhando: ['▶', 'trabalhando'], Deslocando: ['→', 'deslocando'], Parada: ['‖', 'parada'], Desligada: ['⏻', 'desligada'], semSinal: ['◌', 'sem sinal']};
function frEsc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c])); }
function frNum(x, d) { return Number(x || 0).toLocaleString('pt-BR', {minimumFractionDigits: d || 0, maximumFractionDigits: d || 0}); }
// "agora" em segundos: a data operacional do cenário com a hora do navegador; nos testes, window.__frotaRelogio (número ou função)
function frAgora() {
  const r = window.__frotaRelogio; if (typeof r === 'function') return Number(r()); if (typeof r === 'number') return r;
  const d = new Date(), dia = (typeof CEN_DIA_OP !== 'undefined' ? CEN_DIA_OP : d.toISOString().slice(0, 10)).split('-').map(Number);
  return Math.floor(new Date(dia[0], dia[1] - 1, dia[2], d.getHours(), d.getMinutes(), d.getSeconds()).getTime() / 1000);
}
function frHora(t) { const d = new Date(t * 1000); return [d.getHours(), d.getMinutes(), d.getSeconds()].map(x => String(x).padStart(2, '0')).join(':'); }
function frPerfil() { let p = null; try { p = g2perfil(); } catch (e) { p = null; } const pp = (p && p.papeis) || {};
  return {k: p ? p.k : '', pos: !!(p && p.todos) || FR_VE_POS.some(x => pp[x]), nome: !!(p && p.todos) || FR_VE_NOME.some(x => pp[x])}; }
// geometria de cada simulação: rota em metros relativa a uma âncora; desenho SVG (Santa Rita) ou mapa real (Lagoa Grande)
function frGeo(os, tal) {
  const F0 = FROTA0, t = (F0.rota_tal || {})[os] || tal.find(x => (M.geoc || {})[x] || (M.lg.pivos || []).some(p => p.id === x));
  if (!t) return null;
  const pv = (M.lg.pivos || []).find(p => p.id === t);
  if (pv) return {modo: 'lg', t, rota: frRotaCirculo(pv.r_m, F0.passada_m, F0.recuo_m), lat0: pv.lat, lon0: pv.lon};
  const g = (M.geoc || {})[t]; if (!g || g[0] !== 'poly') return null;
  const P = g[1].split(/\s+/).map(q => q.split(',').map(Number)), cx = P.reduce((s, p) => s + p[0], 0) / P.length, cy = P.reduce((s, p) => s + p[1], 0) / P.length;
  let A = 0; P.forEach((p, i) => { const q = P[(i + 1) % P.length]; A += p[0] * q[1] - q[0] * p[1]; }); A = Math.abs(A) / 2;
  const ha = ((M.tal || {})[t] || {}).ha || 0; if (!ha || !A) return null;
  const s = Math.sqrt(ha * 10000 / A);   // metros por unidade do desenho (oráculo G2)
  return {modo: 'svg', t, s, cx, cy, rota: frRotaPoligono(P.map(p => [(p[0] - cx) * s, -(p[1] - cy) * s]), F0.passada_m, F0.recuo_m), lat0: F0.base[0], lon0: F0.base[1]};
}
// modelo: O.S. Em execução da fazenda e safra do mapa, conjunto, leitura, posição e estado (um "agora" só para mapa, lista e painel: M15)
function frModelo(self) {
  const F0 = FROTA0, agora = frAgora(), c = (typeof MAPC !== 'undefined' && MAPC) || cenGet(), pf = frPerfil();
  const ids = TIDS(), ords = (M.ord || []).filter(o => (o.tal || []).some(t => ids.indexOf(t) >= 0) && (!o.saf || o.saf === SAF));
  const A = typeof alVigente === 'function' ? alVigente(c) : [], T = {nome: AL0.nome, tipo: AL0.tipo};
  const cjs = frConjuntos(ords, c, A, CEN_DIA_OP, T, F0), K = frConflitosDe(cjs, c, T), FX = window.__frotaFixture || {};
  const it = cjs.map(cj => {
    const fx = FX[cj.os] || {}, selo = (cj.selos || []).find(x => /^Impedida/.test(x)) || null;
    let geo = null, leit = [], res = {atual: null}, fontes = {};
    const simula = cj.vinculo && (F0.simula || []).indexOf(cj.os) >= 0 && !fx.semFonte;
    if (simula && (geo = frGeo(cj.os, cj.tal))) {
      const fam = cj.fam.familia, P = (F0.paradas || {})[fam] || null;
      leit = frSimular({os: cj.os, rota: geo.rota, vel_kmh: (F0.vel_kmh || {})[fam] || F0.vel_kmh.padrao, t0: F0.t0 != null ? F0.t0 : agora - 3600,
        lat0: geo.lat0, lon0: geo.lon0, paradas: P, corte: fx.corte}, agora, F0);
      res = frProcessar(leit);
      fontes.simulacao = {obs: res.atual ? res.atual.obs : null, limite: F0.limite_s, conectada: fx.conectada !== false, online: fx.online !== false,
        revogada: !!fx.revogada, estado: fx.estado || (res.atual ? res.atual.estado : null)};
    }
    const ava = frAvaliar(fontes, agora, selo), at = res.atual, pos = ava.posicao;
    const comPos = !!(at && pos[0] && pf.pos), idade = at ? agora - at.obs : null;
    return {cj, geo, at, ava, pos, comPos, idade, selo, conflito: K[cj.os] || [], hora: at ? frHora(at.obs) : ''};
  }).sort((a, b) => a.cj.os < b.cj.os ? -1 : 1);
  return {agora, it, pf, n: it.length};
}
function frTal(t) { try { return typeof rotT === 'function' ? rotT(t) : t; } catch (e) { return t; } }
function frTals(cj) { return cj.tal.map(frTal).join(' + '); }
function frNomeConj(cj) { return cj.componentes.length ? cj.componentes.map(x => x.nome).join(' + ') : (cj.fixo ? frTals(cj) + ' (ativo fixo)' : 'Sem conjunto alocado hoje'); }
function frCurto(cj) { const m = cj.componentes.find(x => x.papel !== 'implemento') || cj.componentes[0]; return m ? m.id.replace(/^T(\d)$/, 'T0$1') : cj.os; }
function frEstadoCurto(x) { const e = x.ava.estado; if (/^Trabalhando/.test(e)) return FR_SELO.Trabalhando; if (/^Deslocando/.test(e)) return FR_SELO.Deslocando;
  if (/Parada/.test(e)) return FR_SELO.Parada; if (/Desligada/.test(e)) return FR_SELO.Desligada; return null; }
function frAtual(x) { return x.pos[1] === 'Atual'; }
function frPosTxt(x, pf) {
  if (!pf.pos) return 'Posição restrita ao seu perfil';
  if (x.cj.fixo) return 'Ativo fixo · ver na Irrigação';
  if (!x.cj.vinculo) return 'Sem conjunto alocado hoje';
  if (!x.pos[0]) return x.pos[1] + (x.at ? '' : ' · sem fonte vinculada');
  const f = frFonteNome(x.pos[0]); return (x.pos[1] === 'Atual' ? 'Atual · ' + frIdadeTxt(x.idade) : x.pos[1]) + ' · fonte: ' + f + ' · leitura ' + x.hora;
}
function frEstTxt(x, pf) {
  if (x.cj.fixo) return 'na Irrigação';
  if (!pf.pos && x.ava.estado !== 'Desconhecido') return 'Estado da máquina restrito ao seu perfil';
  return x.ava.estado === 'Desconhecido' ? 'estado desconhecido' : x.ava.estado;
}
function frAria(x, pf) {
  const cj = x.cj, est = frEstTxt(x, pf);
  return [frNomeConj(cj), cj.fam.curto, cj.os, est, pf.pos && x.at ? 'leitura ' + frIdadeTxt(x.idade) : '', pf.pos && x.at ? 'simulação' : '', x.conflito.length ? 'Conflito' : ''].filter(Boolean).join(' · ');
}
// ----- valores do template (chamado no fim do MAPVALS) -----
function frVals(self, v) {
  FRUI.self = self; const st = self.state;
  if (!FRUI.hashOk) { FRUI.hashOk = true; frLeHash(self); }
  const on = !!st.frOn, md = frModelo(self); FRUI.modelo = md;
  // clicar num talhão (ou "Ver talhão") fecha o painel da máquina: o painel do talhão volta a valer
  const tk = (st.tsel || []).join(','); if (FRUI.tsel !== undefined && tk && tk !== FRUI.tsel && (st.frSel || st.frLista)) setTimeout(() => self.setState({frSel: null, frLista: false}), 0); FRUI.tsel = tk;
  v.fr_tem = !!v.map_on; v.fr_on = on ? 'true' : 'false'; v.fr_t = 'Máquinas (' + md.n + ')';
  v.fr_st = 'display:inline-flex;align-items:center;gap:6px;padding:6px 10px;min-height:var(--g2-alvo,0px);min-width:var(--g2-alvo,0px);box-sizing:border-box;border-radius:10px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:700;color:#15201A;box-shadow:0 1px 3px rgba(21,32,26,.18);'
    + (on ? 'border:1px solid #1E7A4C;background:#E4F3E9;' : 'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.fr_tog = () => { const s = self.state, liga = !s.frOn; frOrigem(null);
    self.setState({frOn: liga, frLista: false, frSel: null, g2toast: liga ? 'Máquinas: toque numa máquina para ver a O.S.' : 'Máquinas desligadas.'}); };   // função, filtros, seleção e zoom ficam (M2)
  v.fr_lon = st.frLista ? 'true' : 'false'; v.fr_lt = 'Lista (' + md.n + ')'; v.fr_lst = v.fr_st.replace(on ? 'border:1px solid #1E7A4C;background:#E4F3E9;' : 'border:1px solid #E4E9E5;background:#FFFFFF;', st.frLista ? 'border:1px solid #1E7A4C;background:#E4F3E9;' : 'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.fr_lis = () => { const s = self.state; frOrigem(null); self.setState({frLista: !s.frLista, frSel: null, frGrupo: null});
    if (!s.frLista) setTimeout(() => { const t = document.querySelector('[data-frota-painel] h2'); if (t) t.focus(); }, 60); };
  v.fr_pan = on && !!(st.frSel || st.frLista);
  if (v.fr_pan) v.pan_open = false;
  if (on && !(st.selm || st.medir || st.cvis || st.dw)) { v.modo = 'Máquinas · toque numa máquina para ver a O.S.'; v.has_modo = true; }
  // o recorte termina quando a pessoa mexe na fazenda, safra ou função: a partir daí o 'mapa-ctx' volta a ser gravado
  if (st.frRec) { const sig = [st.mf_faz, st.mf_saf, st.lay].join('|'); if (FRUI.recSig == null) FRUI.recSig = sig;
    else if (sig !== FRUI.recSig) { FRUI.recSig = null; window.__frRec = null; setTimeout(() => self.setState({frRec: null}), 0); } } else FRUI.recSig = null;
  v.fr_rec = !!st.frRec; v.fr_rect = st.frRec ? 'Recorte temporário: ' + st.frRec : '';
  v.fr_sairrec = () => { let s0 = null; try { s0 = JSON.parse(sessionStorage.getItem('mapa-ctx') || 'null'); } catch (e) { s0 = null; }
    window.__frRec = null; self.setState(Object.assign({}, s0 || {}, {frRec: null, frSel: null, g2toast: 'Recorte desfeito: voltou o contexto salvo do mapa.'})); };
  v.fr_volta = st.frRec ? 'OS.dc.html#' + st.frRec : 'OS.dc.html'; v.fr_voltat = st.frRec ? 'Voltar à ' + st.frRec : '';
  v.fr_volt = (e) => { if (document.referrer && /OS\.dc\.html/.test(document.referrer) && history.length > 1) { e && e.preventDefault && e.preventDefault(); history.back(); } };
  clearTimeout(FRUI.dt); FRUI.dt = setTimeout(frDesenha, 0); clearTimeout(FRUI.dt2); FRUI.dt2 = setTimeout(frDesenha, 260);   // depois da transição do zoom do desenho
  if (on && !FRUI.timer) FRUI.timer = setInterval(() => { if (!FRUI.self || !FRUI.self.state.frOn || document.hidden) return; FRUI.modelo = frModelo(FRUI.self); frDesenha(); }, 1000);
  if (!on && FRUI.timer) { clearInterval(FRUI.timer); FRUI.timer = 0; }
}
// #frota=OS-0421: abre na fazenda da O.S., com Máquinas ligada, o conjunto selecionado e o painel aberto; recorte temporário se o contexto salvo esconderia
function frLeHash(self) {
  const m = /(?:^#|&)frota=(OS-\d{3,5})/.exec(location.hash || ''); if (!m) return;
  const os = m[1], o = (M.ord || []).find(x => x.id === os); if (!o) { setTimeout(() => self.setState({g2toast: os + ' não está no mapa.'}), 0); return; }
  const lg = (o.tal || []).some(t => (M.lg.ids || []).indexOf(t) >= 0), faz = lg ? 'Lagoa Grande' : 'Santa Rita';
  let s0 = null; try { s0 = JSON.parse(sessionStorage.getItem('mapa-ctx') || 'null'); } catch (e) { s0 = null; }
  const esconde = !!s0 && ((s0.mf_faz || 'Lagoa Grande') !== faz || (o.saf && (s0.mf_saf || '2026/27') !== o.saf));
  frOrigem({tipo: 'link', os}); if (esconde) window.__frRec = os;   // trava o endereço e o 'mapa-ctx' já na primeira montagem
  setTimeout(() => { self.setState({mf_faz: faz, mf_saf: o.saf || '2026/27', frOn: true, frSel: os, frLista: false, tsel: [], frRec: esconde ? os : null});
    setTimeout(() => { const t = document.querySelector('[data-frota-painel] h2'); if (t) t.focus(); }, 120); }, 30);
}
function frOrigem(o) { FRUI.origem = o; }
function frAbre(os, origem) { const self = FRUI.self; if (!self) return; frOrigem({tipo: origem, os}); self.setState({frSel: os});   // não seleciona o talhão
  setTimeout(() => { const t = document.querySelector('[data-frota-painel] h2'); if (t) t.focus(); }, 60); }
function frFecha() { const self = FRUI.self; if (!self) return; const o = FRUI.origem, s = self.state;
  if (s.frSel && s.frLista) { self.setState({frSel: null}); setTimeout(() => { const b = document.querySelector('[data-frota-painel] [data-frota-linha="' + (o && o.os) + '"] button'); if (b) b.focus(); }, 60); return; }
  self.setState({frSel: null, frLista: false});
  setTimeout(() => { const b = o && o.os && (FRUI.mk[o.os] || (FRUI.lg[o.os] && FRUI.lg[o.os].getElement())); if (b && b.getClientRects().length) b.focus();
    else { const t = document.querySelector('[data-frota-tog]'); if (t) t.focus(); } }, 60);
}
// ----- desenho (marcadores, legenda, lista e painel) -----
function frMarcadorHtml(x) {
  const cj = x.cj, sel = FRUI.self && FRUI.self.state.frSel === cj.os, atual = frAtual(x), e = frEstadoCurto(x);
  const ic = (FR_ICONES || {})[cj.fam.icone] || '', selo = atual || /envio suspenso/.test(x.pos[1]) ? (e || ['?', 'desconhecido']) : FR_SELO.semSinal;
  const seta = atual && x.at && x.at.rumo != null && x.at.vel > 0.5 ? '<span class="fr-seta" style="transform:rotate(' + Math.round(x.at.rumo) + 'deg)" aria-hidden="true"></span>' : '';
  return '<span class="fr-disco' + (atual ? '' : ' fr-vazado') + (sel ? ' fr-sel' : '') + '" aria-hidden="true">' + ic + seta + '</span>'
    + '<span class="fr-rot" aria-hidden="true"><b>' + frEsc(frCurto(cj)) + ' · ' + frEsc(cj.fam.curto) + '</b><span class="fr-selo">' + selo[0] + ' ' + selo[1] + (x.conflito.length ? ' · Conflito' : '') + '</span></span>';
}
function frTelaSvg(x) {   // posição da leitura no desenho da Santa Rita → pixels dentro da camada
  const svg = [...document.querySelectorAll('svg[data-mux-grupo]')].find(s => s.getClientRects().length); if (!svg || !x.geo || !x.at) return null;
  const g = x.geo, m = frGrausParaMetros(g.lat0, g.lon0, x.at.lat, x.at.lon), p = svg.createSVGPoint(); p.x = g.cx + m.x / g.s; p.y = g.cy - m.y / g.s;
  const k = svg.getScreenCTM(); if (!k) return null; const q = p.matrixTransform(k); return [q.x, q.y];
}
function frDesenha() {
  const self = FRUI.self, md = FRUI.modelo; if (!self || !md) return; const st = self.state, on = !!st.frOn;
  const cam = [...document.querySelectorAll('[data-frota-camada]')].find(d => d.getClientRects().length) || null;
  const lgOn = typeof LGI !== 'undefined' && LGI.map && LGI.pronto && FAZ === 'Lagoa Grande';
  const vis = on && md.pf.pos ? md.it.filter(x => x.comPos && x.geo) : [];
  const vivos = new Set();
  // posições na tela (para o agrupamento: menos de 28 px vira "N máquinas"; o marcador com foco e o selecionado nunca entram num grupo)
  const R = cam ? cam.getBoundingClientRect() : null, pts = [];
  vis.forEach(x => { let q = null;
    if (x.geo.modo === 'svg' && R) { const s = frTelaSvg(x); if (s) q = [s[0] - R.left, s[1] - R.top]; }
    else if (x.geo.modo === 'lg' && lgOn) { const p = LGI.map.project([x.at.lon, x.at.lat]); q = [p.x, p.y]; }
    if (q) pts.push([x.cj.os, q[0], q[1], x]); });
  const foco = document.activeElement && document.activeElement.getAttribute && document.activeElement.getAttribute('data-frota-os');
  const [grupos] = frAgrupar(pts.map(p => [p[0], p[1], p[2]]), foco, st.frSel);
  const emGrupo = {}; grupos.filter(g => g.length > 1).forEach(g => g.forEach(id => { emGrupo[id] = g; }));
  pts.forEach(([os, px, py, x]) => {
    if (emGrupo[os]) return; vivos.add(os);
    const html = frMarcadorHtml(x), aria = frAria(x, md.pf);
    if (x.geo.modo === 'svg') {
      let b = FRUI.mk[os]; if (b && !b.isConnected) { delete FRUI.mk[os]; b = null; }
      if (!b && cam) { b = document.createElement('button'); b.type = 'button'; b.className = 'fr-m'; b.setAttribute('data-frota-os', os); b.onclick = () => frAbre(os, 'mapa'); cam.appendChild(b); FRUI.mk[os] = b; }
      if (!b) return; if (b.__h !== html) { b.innerHTML = html; b.__h = html; } if (b.getAttribute('aria-label') !== aria) b.setAttribute('aria-label', aria);
      b.setAttribute('aria-pressed', st.frSel === os ? 'true' : 'false'); b.style.transform = 'translate(' + Math.round(px - 22) + 'px,' + Math.round(py - 22) + 'px)';
    } else if (lgOn && window.maplibregl) {
      let mk = FRUI.lg[os];
      if (!mk) { const b = document.createElement('button'); b.type = 'button'; b.className = 'fr-m fr-m-lg'; b.setAttribute('data-frota-os', os); b.onclick = (e) => { e.stopPropagation(); frAbre(os, 'mapa'); };
        mk = new maplibregl.Marker({element: b, anchor: 'center'}).setLngLat([x.at.lon, x.at.lat]).addTo(LGI.map); FRUI.lg[os] = mk; }
      const b = mk.getElement(); if (b.__h !== html) { b.innerHTML = html; b.__h = html; } if (b.getAttribute('aria-label') !== aria) b.setAttribute('aria-label', aria);
      b.setAttribute('aria-pressed', st.frSel === os ? 'true' : 'false'); mk.setLngLat([x.at.lon, x.at.lat]);
    }
  });
  // grupos: um botão "N máquinas" (44 px) que abre a lista
  const gv = new Set();
  grupos.filter(g => g.length > 1).forEach(g => { const k = g.slice().sort().join(','); gv.add(k); const ps = pts.filter(p => g.indexOf(p[0]) >= 0);
    const cx = ps.reduce((s, p) => s + p[1], 0) / ps.length, cy = ps.reduce((s, p) => s + p[2], 0) / ps.length; let b = FRUI.grp[k];
    if (b && !b.isConnected) { delete FRUI.grp[k]; b = null; }
    if (!b && cam) { b = document.createElement('button'); b.type = 'button'; b.className = 'fr-m fr-grupo'; b.onclick = () => FRUI.self.setState({frLista: true, frSel: null, frGrupo: g.slice()}); cam.appendChild(b); FRUI.grp[k] = b; }
    if (!b) return; b.textContent = g.length + ' máquinas'; b.setAttribute('aria-label', g.length + ' máquinas neste ponto: abrir a lista'); b.style.transform = 'translate(' + Math.round(cx - 22) + 'px,' + Math.round(cy - 22) + 'px)'; });
  Object.keys(FRUI.grp).forEach(k => { if (!gv.has(k)) { FRUI.grp[k].remove(); delete FRUI.grp[k]; } });
  Object.keys(FRUI.mk).forEach(os => { if (!vivos.has(os) || !FRUI.mk[os].isConnected) { FRUI.mk[os].remove(); delete FRUI.mk[os]; } });
  Object.keys(FRUI.lg).forEach(os => { if (!vivos.has(os) || !lgOn) { FRUI.lg[os].remove(); delete FRUI.lg[os]; } });
  frLegenda(on, md); frPainel(on, md);
}
function frLegenda(on, md) {
  document.querySelectorAll('[data-frota-leg]').forEach(el => {
    let h = '';
    if (on) { const fams = [...new Set(md.it.filter(x => x.comPos).map(x => x.cj.fam.icone + '|' + x.cj.fam.curto))];
      h = '<span class="fr-leg"><b>Máquinas</b>' + fams.map(f => { const [ic, t] = f.split('|'); return '<span class="fr-leg-i">' + ((FR_ICONES || {})[ic] || '') + frEsc(t) + '</span>'; }).join('')
        + '<span>▶ trabalhando · → deslocando · ‖ parada · ⏻ desligada · ◌ sem sinal</span>' + (md.pf.pos ? '<span class="fr-leg-sim">Posições simuladas · demonstração</span>' : '') + '</span>'; }
    if (el.__h !== h) { el.innerHTML = h; el.__h = h; } });
}
function frFeito(cj) { return frNum(cj.rz, cj.rz % 1 ? 1 : 0) + ' de ' + frNum(cj.area, cj.area % 1 ? 2 : 0) + ' ha · saldo ' + frNum(cj.saldo, cj.saldo % 1 ? 2 : 0) + ' ha'; }
function frFalta(x) {
  const cj = x.cj, F0 = FROTA0, r = (F0.rend || {})[cj.fam.familia]; let s = frNum(cj.rz, cj.rz % 1 ? 1 : 0) + ' de ' + frNum(cj.area, cj.area % 1 ? 2 : 0) + ' ha apontados · saldo ' + frNum(cj.saldo, cj.saldo % 1 ? 2 : 0) + ' ha';
  if (r && cj.saldo > 0) s += ' · ≈ ' + frNum(cj.saldo / r, 1) + ' h no rendimento de referência (estimativa)'; return s; }
function frCarga(x) {
  const cj = x.cj, F0 = FROTA0, c = (typeof MAPC !== 'undefined' && MAPC) || cenGet(), co = (c.ordens || {})[cj.os] || {};
  if (cj.fam.familia === 'Pulverização' && co.instrucao && co.instrucao.vazao && (F0.tanque || {})[cj.implemento] && cj.saldo > 0) {
    const ha = F0.tanque[cj.implemento] / co.instrucao.vazao, n = Math.ceil(cj.saldo / ha - 1e-9), ult = cj.saldo - ha * (n - 1);
    return 'Preparo previsto (projeção da O.S.): ' + n + ' cargas de ' + frNum(ha, ha % 1 ? 1 : 0) + ' ha, a última com ' + frNum(ult, ult % 1 ? 1 : 0) + ' ha'; }
  if (cj.fam.familia === 'Colheita') { const cg = Object.values(c.producao && c.producao.cargas || {}).filter(g => (g.os === cj.os) || (g.origem || []).some(o => o.os === cj.os)).sort((a, b) => String(a.at || a.d || '') < String(b.at || b.d || '') ? 1 : -1)[0];
    if (cg) return 'Última carga ' + (cg.id || '') + (cg.hora ? ' às ' + cg.hora : ''); }
  return '';
}
function frPainel(on, md) {
  const el = document.querySelector('[data-frota-painel]'); if (!el) return; const st = FRUI.self.state, pf = md.pf;
  const x = st.frSel ? md.it.find(i => i.cj.os === st.frSel) : null;
  let chave, cab, corpo, acoes;
  if (st.frSel) {
    if (!x) { chave = 'saiu|' + st.frSel; const c = (typeof MAPC !== 'undefined' && MAPC) || cenGet(), et = ((c.ordens || {})[st.frSel] || {}).etapa || 'fora do mapa';
      cab = '<h2 tabindex="-1">' + frEsc(st.frSel) + '</h2><div class="fr-sub">Máquinas</div>';
      corpo = '<div role="status" class="fr-aviso">' + frEsc(st.frSel) + ' saiu de Em execução (agora ' + frEsc(et) + ') · dados desta máquina retirados</div>';
      acoes = '<a class="fr-prim" href="OS.dc.html#' + frEsc(st.frSel) + '">Abrir O.S.</a>';
    } else {
      const cj = x.cj; chave = 'cj|' + cj.os + '|' + (st.frLista ? 'l' : '');
      cab = '<h2 tabindex="-1">' + frEsc(frNomeConj(cj)) + '</h2><div class="fr-sub">' + frEsc(cj.fam.curto + ' · ' + cj.os + (cj.versao ? ' · v' + cj.versao : '') + ' · ' + frTals(cj)) + '</div>';
      const kv = [['O.S. e versão', cj.os + (cj.versao ? ' · versão ' + cj.versao : '')], ['Operação', cj.tipo], ['Talhão', frTals(cj)],
        ['Conjunto', frNomeConj(cj) + (cj.vinculo === 'programacao' ? ' · pela programação' + (cj.condicional ? ' (condicional)' : '') : (cj.vinculo === 'fixture' ? ' · conjunto de demonstração' : ''))],
        ['Estado', frEstTxt(x, pf) + (pf.pos && x.at ? ' · ' + x.hora : '')], ['Posição', frPosTxt(x, pf) + (pf.pos && x.at ? ' · precisão não informada' : '')],
        ['Quanto falta', frFalta(x)]];
      if (pf.pos && x.at && frAtual(x)) kv.push(['Velocidade', frNum(x.at.vel, 0) + ' km/h (leitura)']);
      const cg = frCarga(x); if (cg) kv.push(['Carga', cg]);
      kv.push(['Operador', pf.nome ? (cj.pessoas.filter(p => /operador/.test(p.papel)).map(p => p.nome).join(', ') || cj.resp || '—') : 'operador da O.S.']);
      if (x.selo) kv.push(['O.S.', x.selo]);
      corpo = '<dl class="fr-kv">' + kv.map(([k, v]) => '<div><dt>' + frEsc(k) + '</dt><dd>' + frEsc(v) + '</dd></div>').join('') + '</dl>'
        + x.conflito.map(k => '<div class="fr-conf">Conflito · ' + frEsc(k.nome) + ' também na ' + k.com.map(o => '<a href="OS.dc.html#' + o + '">' + o + '</a>').join(', ') + '</div>').join('')
        + (x.ava.aviso && pf.pos ? '<div role="note" class="fr-aviso">' + frEsc(x.ava.aviso) + '</div>' : '')
        + (pf.pos && x.at ? '<div class="fr-nota">Fonte: simulação · posições de demonstração, sem efeito na O.S.</div>' : '');
      acoes = '<a class="fr-prim" href="OS.dc.html#' + frEsc(cj.os) + '">Abrir O.S.</a>' + (x.selo ? '<a class="fr-sec" href="OS.dc.html#' + frEsc(cj.os) + '">Ver impedimento</a>' : '')
        + (cj.fixo ? '<a class="fr-sec" href="IR-01.dc.html#faz=' + encodeURIComponent(FAZ) + '">Ver na Irrigação</a>' : '')
        + (cj.tal.length ? '<button type="button" class="fr-sec" data-frota-tal="' + frEsc(cj.tal.find(t => TIDS().indexOf(t) >= 0) || cj.tal[0]) + '">Ver talhão</button>' : '');
    }
  } else if (st.frLista) {
    chave = 'lista';
    const g = st.frGrupo && st.frGrupo.length ? st.frGrupo : null, its = md.it.filter(i => !g || g.indexOf(i.cj.os) >= 0);
    cab = '<h2 tabindex="-1">Máquinas em execução (' + its.length + ')</h2><div class="fr-sub">' + frEsc(FAZ + ' · ' + SAF) + (g ? ' · ' + g.length + ' no mesmo ponto' : '') + '</div>';
    corpo = '<table class="fr-tab"><thead><tr><th>Conjunto</th><th>Operação</th><th>O.S.</th><th>Talhão</th><th>Estado</th><th>Posição</th><th>Feito/saldo</th></tr></thead><tbody>'
      + its.map(i => '<tr data-frota-linha="' + i.cj.os + '"><td><button type="button" data-frota-abre="' + i.cj.os + '">' + frEsc(frNomeConj(i.cj)) + '</button></td><td>' + frEsc(i.cj.fam.curto) + '</td><td>' + i.cj.os + '</td><td>'
        + frEsc(frTals(i.cj)) + '</td><td>' + frEsc(i.cj.fixo ? (i.selo ? 'O.S. ' + i.selo.toLowerCase() : '—') : (i.selo ? 'O.S. ' + i.selo.toLowerCase() + ' · máquina: ' : '') + frEstTxt(i, pf)) + (i.conflito.length ? ' · Conflito · também na ' + i.conflito.map(k => k.com.join(', ')).join(', ') : '') + '</td><td>'
        + frEsc(frPosTxt(i, pf)) + '</td><td>' + frEsc(frFeito(i.cj)) + '</td></tr>').join('') + '</tbody></table>'
      + (pf.pos ? '<div class="fr-nota">Fonte: simulação · posições de demonstração</div>' : '');
    acoes = '';
  } else { if (el.__k) { el.innerHTML = ''; el.__k = ''; } return; }
  if (el.__k !== chave) { el.__k = chave; el.innerHTML = '<div class="fr-cab"><div class="fr-cab-t" data-frota-cab></div><button type="button" class="fr-x" aria-label="Fechar painel" title="Fechar painel">×</button></div>'
      + '<div class="fr-corpo" data-frota-corpo></div><div class="fr-acoes" data-frota-acoes></div>';
    el.querySelector('.fr-x').onclick = frFecha; el.__c = el.__b = el.__a = null;
    el.onclick = (e) => { const a = e.target.closest('[data-frota-abre]'); if (a) { frOrigem({tipo: 'lista', os: a.getAttribute('data-frota-abre')}); FRUI.self.setState({frSel: a.getAttribute('data-frota-abre')}); setTimeout(() => { const t = document.querySelector('[data-frota-painel] h2'); if (t) t.focus(); }, 60); return; }
      const tr = e.target.closest('tr[data-frota-linha]'); if (tr && !e.target.closest('a,button')) { const b = tr.querySelector('button'); if (b) b.click(); return; }
      const t = e.target.closest('[data-frota-tal]'); if (t) { const id = t.getAttribute('data-frota-tal'); FRUI.self.setState({frSel: null, frLista: false, tsel: [id]}); } }; }
  const set = (sel, k, h) => { if (el[k] === h) return; const d = el.querySelector(sel); if (!d) return; const ativo = d.contains(document.activeElement) ? document.activeElement : null;
    if (k === '__c' && ativo && d.querySelector('tbody')) {   // lista: atualiza as células no lugar (a linha com foco não se perde)
      const tmp = document.createElement('div'); tmp.innerHTML = h; const nv = tmp.querySelectorAll('tbody tr'), at = d.querySelectorAll('tbody tr');
      if (nv.length === at.length) { nv.forEach((tr, i) => { [...tr.children].forEach((td, j) => { if (j && at[i].children[j].textContent !== td.textContent) at[i].children[j].textContent = td.textContent; }); }); el[k] = h; return; } }
    d.innerHTML = h; el[k] = h; };
  set('[data-frota-cab]', '__b', cab); set('[data-frota-corpo]', '__c', corpo); set('[data-frota-acoes]', '__a', acoes);
}
// Esc: fecha o painel ou a lista e devolve o foco à origem (marcador ou linha); antes do Esc do Mapa
document.addEventListener('keydown', (e) => { if (e.key !== 'Escape' || !FRUI.self) return; const t = e.target;
  if (!(t.closest && (t.closest('[data-frota-painel]') || t.closest('[data-frota-os]')))) return;
  const s = FRUI.self.state; if (s.frSel || s.frLista) { e.preventDefault(); e.stopPropagation(); frFecha(); } }, true);
// a camada some ao trocar de fazenda; o MapLibre redesenha os marcadores no próprio movimento
document.addEventListener('visibilitychange', () => { if (!document.hidden && FRUI.self && FRUI.self.state.frOn) { FRUI.modelo = frModelo(FRUI.self); frDesenha(); } });
window.addEventListener('resize', () => { if (FRUI.self && FRUI.self.state.frOn) frDesenha(); });
// gancho só de teste (como o window.__LGI): relógio, redesenho e o cenário da página para os casos M8/M9/M14; a camada não o chama
try { window.__frotaTeste = {agora: frAgora, redesenha: () => { if (FRUI.self) { FRUI.modelo = frModelo(FRUI.self); frDesenha(); } },
  render: () => { if (FRUI.self) FRUI.self.setState({frT: Date.now()}); }, estado: (k, v) => { if (FRUI.self) { const o = {}; o[k] = v; FRUI.self.setState(o); } },
  frota0: () => FROTA0, cenario: (fn) => { const c = cenGet(); if (fn) { fn(c); cenSave(c); } return JSON.parse(JSON.stringify(c)); }}; } catch (e) {}
