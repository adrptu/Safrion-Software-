// ===== MAPA-FROTA F1 (frota.js): regras puras das máquinas no Mapa. Especificação: docs/integracao/V71/MAPA-FROTA.md =====
// Oráculo executável: docs/integracao/V71/mapa-frota/mapa_frota_chk.py (L, P, K, Z). Os casos dele estão em frota_unit.js.
// Só leitura: a posição é relato da fonte, nunca fato de execução. Nada aqui grava no cenário (área, consumo, carga e fase vêm do cenário).

const FR_TOL_FUT = 120;        // s: observada depois de recebida + 120 s = futura (L4)
const FR_VMAX = 60;            // km/h: velocidade implícita acima disso = salto suspeito (L8–L9; fixture da classe)
const FR_PRIO = ['telemetria', 'app', 'simulacao'];   // a simulação do protótipo fica abaixo das fontes reais
const FR_FONTE_NOME = {telemetria: 'telemetria', app: 'app', simulacao: 'simulação', arquivo: 'arquivo'};
const frFonteNome = t => FR_FONTE_NOME[t] || t;

function frDistM(a, b) {       // metros entre duas leituras (aproximação local, como no oráculo)
  const k = Math.cos(Number(a.lat) * Math.PI / 180);
  const dx = (Number(b.lon) - Number(a.lon)) * 111320 * k, dy = (Number(b.lat) - Number(a.lat)) * 110540;
  return Math.sqrt(dx * dx + dy * dy);
}
function frValida(r) {
  const la = Number(r && r.lat), lo = Number(r && r.lon);
  return Number.isFinite(la) && Number.isFinite(lo) && Math.abs(la) <= 90 && Math.abs(lo) <= 180 && !(la === 0 && lo === 0);
}
// L · leituras de uma fonte, na ordem de chegada. Vale o instante observado (obs); rec = recebido. Devolve atual, rastro (por obs), recusadas e suspeita.
function frProcessar(recebidas) {
  let atual = null, susp = null; const rastro = [], vistos = new Set(), recus = [];
  for (const r of (recebidas || [])) {
    if (vistos.has(r.id)) { recus.push([r.id, 'duplicada']); continue; }
    vistos.add(r.id);
    if (!frValida(r)) { recus.push([r.id, 'inválida']); continue; }
    if (r.obs > r.rec + FR_TOL_FUT) { recus.push([r.id, 'futura']); continue; }
    if (atual && r.obs === atual.obs) { recus.push([r.id, 'mesmo instante']); continue; }
    if (atual && r.obs < atual.obs) { rastro.push(Object.assign({}, r, {atrasada: true})); continue; }   // só completa o rastro; o marcador não volta
    if (susp && r.obs === susp.obs) { recus.push([r.id, 'mesmo instante da suspeita']); continue; }    // Δt = 0 não decide (L11)
    if (susp && r.obs > susp.obs) {                                                                    // só Δt > 0 decide a suspeita (L14)
      if (frDistM(susp, r) / (r.obs - susp.obs) * 3.6 <= FR_VMAX) { rastro.push(susp); atual = susp; }
      else recus.push([susp.id, 'salto descartado']);
      susp = null;
    }
    if (atual && frDistM(atual, r) / (r.obs - atual.obs) * 3.6 > FR_VMAX) {
      if (!susp) susp = r; else recus.push([r.id, 'salto anterior à suspeita pendente']);
      continue;
    }
    rastro.push(r); atual = r;
  }
  return {atual, rastro: rastro.slice().sort((a, b) => a.obs - b.obs), recus, susp};
}
function frIdadeTxt(seg) {
  const m = Math.floor(seg / 60);
  if (m === 0) return 'há menos de 1 min';
  return m < 60 ? 'há ' + m + ' min' : 'há ' + Math.floor(m / 60) + ' h ' + String(m % 60).padStart(2, '0') + ' min';
}
// situação da posição pela idade; a fronteira do limite é inclusiva (L6). Nunca diz "parada" por causa da idade.
function frSituacao(res, agora, limite) {
  const a = res && res.atual; if (!a) return ['Posição indisponível', null];
  const idade = agora - a.obs;
  return idade <= limite ? ['Atual', idade] : ['Sem sinal ' + frIdadeTxt(idade), idade];
}
// P · posição e estado operacional da máquina, em saídas separadas. fontes: {tipo: {obs, limite, conectada, online, revogada, estado}}.
// os_selo é o selo da O.S. (eixo 1): nunca vira estado da máquina; leitura que o contradiz gera aviso (P13).
function frAvaliar(fontes, agora, os_selo) {
  const F = fontes || {}, vivas = {}, revog = [];
  Object.keys(F).forEach(t => { if (F[t] && F[t].revogada) revog.push(t); else vivas[t] = F[t]; });
  const conectada = f => f.conectada !== false, online = f => f.online !== false;
  const atuais = FR_PRIO.filter(t => vivas[t] && conectada(vivas[t]) && vivas[t].obs != null && agora - vivas[t].obs <= vivas[t].limite);
  let pos;
  if (atuais.length) pos = [atuais[0], 'Atual'];
  else {
    const ult = Object.keys(vivas).filter(t => vivas[t].obs != null).map(t => [vivas[t].obs, t]).sort((a, b) => a[0] - b[0] || (a[1] < b[1] ? -1 : 1));
    if (!ult.length) pos = [null, 'Posição indisponível' + (revog.length ? ' · compartilhamento encerrado' : '')];
    else {
      const [obs, t] = ult[ult.length - 1], f = vivas[t];
      if (!conectada(f)) pos = [t, 'Sem fonte: ' + frFonteNome(t) + ' desconectada · última ' + frIdadeTxt(agora - obs)];
      else if (online(f) && String(f.estado || '').startsWith('Parada · pausa')) pos = [t, 'Última posição ' + frIdadeTxt(agora - obs) + ' · envio suspenso na pausa'];
      else pos = [t, 'Sem sinal ' + frIdadeTxt(agora - obs)];
    }
  }
  let est = 'Desconhecido';
  for (const t of FR_PRIO) { const f = vivas[t];
    if (f && f.estado && conectada(f)) { est = online(f) ? f.estado + ' (' + frFonteNome(t) + ')' : 'Última informação: ' + f.estado + ' (' + frFonteNome(t) + ') · sem sinal'; break; } }
  const aviso = (os_selo && String(os_selo).startsWith('Impedida') && est.startsWith('Trabalhando')) ? 'Leitura contradiz o impedimento da O.S. · conferir' : null;
  return {posicao: pos, estado: est, aviso};
}
// K · conflito por componente físico entre O.S. Em execução. conjs: {os: {maquina, implemento, prog: grupo|alocacao|troca, blocos: [[ini, fim]]}}.
// grupos: {gid: {ids, maquina, implemento}}. Só some no MESMO conjunto do MESMO grupo, programação do grupo e blocos sem sobreposição.
function frConflitos(conjs, etapa, grupos) {
  const ex = {}, por = {}, G = grupos || {};
  Object.keys(conjs || {}).forEach(o => { if ((etapa || {})[o] === 'Em execução') ex[o] = conjs[o]; });
  Object.keys(ex).forEach(o => [ex[o].maquina, ex[o].implemento].forEach(r => { if (r) (por[r] = por[r] || []).push(o); }));
  const out = {};
  Object.keys(por).forEach(r => { const oss = por[r]; if (oss.length < 2) return;
    const gids = new Set(oss.map(o => Object.keys(G).find(g => (G[g].ids || []).indexOf(o) >= 0) || null));
    let compat = false;
    if (gids.size === 1 && !gids.has(null)) { const g = G[[...gids][0]];
      const mesmo = oss.every(o => ex[o].maquina === g.maquina && ex[o].implemento === g.implemento && ex[o].prog === 'grupo');
      const bl = [].concat(...oss.map(o => ex[o].blocos || [])).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      compat = mesmo && bl.every((b, i) => i === bl.length - 1 || b[1] <= bl[i + 1][0]); }
    if (!compat) out[r] = oss.slice().sort(); });
  return out;
}
// um marcador por conjunto físico distinto (máquina + implemento); dois conjuntos distintos nunca viram um (K7)
function frMarcadores(conjs, etapa) {
  const s = new Map(); Object.keys(conjs || {}).forEach(o => { if ((etapa || {})[o] !== 'Em execução') return; const c = conjs[o];
    const k = (c.maquina || '') + '|' + (c.implemento || ''); if (!s.has(k)) s.set(k, [c.maquina, c.implemento]); });
  return [...s.keys()].sort().map(k => s.get(k));
}
// Z · o que o mapa e a lista mostram. modo: ativo | pausado; congelada/corrente: {fonte, obs}. Pausa congela só a posição EXIBIDA no mapa.
function frExibir(modo, congelada, corrente, agora, osEmExecucao, perfilVe) {
  if (osEmExecucao === false) return {mapa: null, lista: null, aviso: 'A O.S. saiu de Em execução · dados desta máquina retirados · Abrir O.S.'};
  if (perfilVe === false) return {mapa: null, lista: null, aviso: 'Seu acesso à localização foi retirado'};
  const lista = {fonte: corrente.fonte, hora: corrente.obs, idade: agora - corrente.obs, selo: ''};
  if (modo !== 'pausado') return {mapa: Object.assign({}, lista), lista, aviso: null};
  return {mapa: {fonte: congelada.fonte, hora: congelada.obs, idade: agora - congelada.obs, selo: 'pausado'}, lista, aviso: null};
}
// agrupamento na tela: marcadores a menos de lim px viram "N máquinas"; o com foco e o selecionado nunca entram num grupo (Z6)
function frAgrupar(pts, foco, sel, lim) {
  lim = lim || 28; const fora = id => id === foco || id === sel;
  const livres = (pts || []).filter(p => !fora(p[0])), usados = new Set(), grupos = [];
  livres.forEach(p => { if (usados.has(p[0])) return;
    const g = livres.filter(q => !usados.has(q[0]) && (q[1] - p[1]) ** 2 + (q[2] - p[2]) ** 2 < lim * lim);
    g.forEach(q => usados.add(q[0])); grupos.push(g.map(q => q[0])); });
  return [grupos, (pts || []).filter(p => fora(p[0])).map(p => p[0])];
}
// família do ícone pela operação do catálogo (decisão 5), nunca pelo texto livre do tipo
const FR_FAMILIAS = [
  ['Pulverização', /pulveriza|desseca|fungic|herbic|inseticida/i, 'gotas', 'Pulverização'],
  ['Plantio', /plantio|semeadura|transplant|mudas/i, 'broto', 'Plantio'],
  ['Adubação e correção', /aduba|calag|gessag|fosfatag|corretivo/i, 'graos', 'Adubação'],
  ['Preparo de solo', /preparo|canteir|reforma|grade|subsol/i, 'grade', 'Preparo'],
  ['Colheita', /colheita/i, 'Colheita', 'Colheita'],
  ['Transporte', /transport|carreta|graneleir/i, 'truck', 'Transporte'],
  ['Irrigação e fertirrigação', /irriga|fertirriga|lâmina/i, 'Irrigação', 'Irrigação'],
];
function frFamilia(operacao) {
  const t = String(operacao || '');
  const f = FR_FAMILIAS.find(x => x[1].test(t));
  return f ? {familia: f[0], icone: f[2], curto: f[3]} : {familia: 'Outra', icone: 'wrench', curto: t || 'Operação'};
}

// ===== Conjuntos em execução (derivados, nunca gravados). Fonte: alVigente (programação do PCP e do OS-LOTE, só leitura) e, onde não
// há conjunto nela, a fixture de demonstração (F0.demo, rotulada "conjunto de demonstração"). Ativo fixo de irrigação fica só na lista.
// ords: O.S. do mapa ({id, tal, tipo, fase, selos, area, rz, saldo, resp, saf}); c: cenário; dia: data operacional; T: {nome, tipo, classe} dos recursos
function frConjuntos(ords, c, A, dia, T, F0) {
  const G = (c && c.gruposExec) || {}, O = (c && c.ordens) || {}, D = (F0 && F0.demo) || {};
  return (ords || []).filter(o => o.fase === 'Em execução').map(o => {
    const fam = frFamilia(o.tipo), co = O[o.id] || {};
    const base = {os: o.id, versao: co.versao || null, tipo: o.tipo || '', fam, tal: (o.tal || []).slice(), selos: (o.selos || []).map(x => x[0]),
      area: Number(o.area) || 0, rz: Number(o.rz) || 0, saldo: Number(o.saldo) || 0, resp: o.resp || '', componentes: [], pessoas: [], vinculo: null, condicional: false,
      maquina: null, implemento: null, prog: 'alocacao', blocos: [], grupo: null, fixo: false};
    if (fam.familia === 'Irrigação e fertirrigação') return Object.assign(base, {fixo: true});
    let its = (A || []).filter(a => a.os === o.id);
    const doDia = its.filter(a => a.dia === dia);
    if (doDia.length) its = doDia; else if (its.length) { const ult = its.map(a => a.dia).sort().pop(); its = its.filter(a => a.dia === ult); }
    const tipo = r => (T.tipo || {})[r], rs = [...new Set(its.map(a => a.r))];
    const maq = rs.find(r => tipo(r) === 'Máquina'), imp = rs.find(r => tipo(r) === 'Implemento');
    if (maq || imp) {
      const papel = r => tipo(r) === 'Implemento' ? 'implemento' : (/colhedora/i.test((T.nome || {})[r] || '') ? 'colhedora' : 'trator');
      base.componentes = [maq, imp].filter(Boolean).map(r => ({id: r, papel: papel(r), nome: (T.nome || {})[r] || r}));
      base.pessoas = rs.filter(r => tipo(r) === 'Pessoa').map(r => ({id: r, nome: String((T.nome || {})[r] || r).split(' · ')[0], papel: String((T.nome || {})[r] || '').split(' · ')[1] || 'operador'}));
      base.vinculo = 'programacao'; base.condicional = its.some(a => a.sit === 'condicional'); base.maquina = maq || null; base.implemento = imp || null;
      base.blocos = its.filter(a => a.r === (maq || imp)).map(a => [a.ini, a.fim]);
      const gid = Object.keys(G).find(g => (G[g].ids || []).indexOf(o.id) >= 0);
      if (gid) base.grupo = gid;
      base.prog = co.rec && Object.keys(co.rec).length ? 'troca' : (gid && co.prog && Array.isArray(co.prog.blocos) ? 'grupo' : 'alocacao');
    } else if (D[o.id]) {
      const d = D[o.id]; base.componentes = d.componentes.map(x => Object.assign({}, x)); base.vinculo = 'fixture';
      base.maquina = (d.componentes.find(x => x.papel !== 'implemento') || {}).id || null; base.implemento = (d.componentes.find(x => x.papel === 'implemento') || {}).id || null;
    }
    return base;
  });
}
// grupos do OS-LOTE no formato do frConflitos: {gid: {ids, maquina, implemento}}
function frGrupos(c) { const G = (c && c.gruposExec) || {}, out = {};
  Object.keys(G).forEach(g => { const p = G[g].programa || {}; out[g] = {ids: (G[g].ids || []).slice(), maquina: p.maquina || null, implemento: p.implemento || null}; });
  return out; }
// conflitos dos conjuntos (K): componente físico em duas O.S. Em execução; devolve {os: [{ativo, nome, com: [outras O.S.]}]}
function frConflitosDe(cjs, c, T) {
  const cj = {}, et = {}; (cjs || []).filter(x => x.vinculo).forEach(x => { cj[x.os] = {maquina: x.maquina, implemento: x.implemento, prog: x.prog, blocos: x.blocos}; et[x.os] = 'Em execução'; });
  const K = frConflitos(cj, et, frGrupos(c)), out = {};
  Object.keys(K).forEach(r => K[r].forEach(os => (out[os] = out[os] || []).push({ativo: r, nome: (T.nome || {})[r] || r, com: K[r].filter(x => x !== os)})));
  return out;
}
// ===== Percurso sintético (decisão 7): passadas paralelas a cada 36 m, recuo de 18 m nas cabeceiras, em metros relativos a uma âncora.
// Polígono convexo: pontos [[x, y]] em metros (y para o norte). Círculo: raio em metros, centro na âncora.
function frRotaPoligono(pts, passo, recuo) {
  passo = passo || 36; recuo = recuo || 18; const xs = pts.map(p => p[0]), rota = [];
  let k = 0;
  for (let x = Math.min(...xs) + passo / 2; x < Math.max(...xs) - passo / 2; x += passo) {
    const ys = [];
    pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length];
      if (a[0] !== b[0] && Math.min(a[0], b[0]) <= x && x <= Math.max(a[0], b[0])) ys.push(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0])); });
    if (ys.length < 2) continue;
    const lo = Math.min(...ys) + recuo, hi = Math.max(...ys) - recuo; if (hi <= lo) continue;
    if (k++ % 2 === 0) rota.push([x, lo], [x, hi]); else rota.push([x, hi], [x, lo]);
  }
  return rota;
}
function frRotaCirculo(r, passo, recuo) {
  passo = passo || 36; recuo = recuo || 18; const rota = []; let k = 0;
  for (let x = -r + passo / 2; x < r - passo / 2; x += passo) {
    const h = Math.sqrt(r * r - x * x) - recuo; if (h <= 0) continue;
    if (k++ % 2 === 0) rota.push([x, -h], [x, h]); else rota.push([x, h], [x, -h]);
  }
  return rota;
}
// posição a d metros do início da rota (fechada em laço: ao fim, volta pelo começo); rumo em graus (0 = norte, horário)
function frNaRota(rota, d) {
  const seg = []; let L = 0;
  for (let i = 0; i < rota.length; i++) { const a = rota[i], b = rota[(i + 1) % rota.length], l = Math.hypot(b[0] - a[0], b[1] - a[1]); seg.push([a, b, l]); L += l; }
  if (!L) return null;
  let r = ((d % L) + L) % L;
  for (const [a, b, l] of seg) { if (r <= l) { const f = l ? r / l : 0; const dx = b[0] - a[0], dy = b[1] - a[1];
      return {x: a[0] + dx * f, y: a[1] + dy * f, rumo: (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360, L}; } r -= l; }
  return {x: rota[0][0], y: rota[0][1], rumo: 0, L};
}
// metros (x leste, y norte) → graus em torno de uma âncora (lat0, lon0); e o inverso
function frMetrosParaGraus(lat0, lon0, x, y) { return {lat: lat0 + y / 110540, lon: lon0 + x / (111320 * Math.cos(lat0 * Math.PI / 180))}; }
function frGrausParaMetros(lat0, lon0, lat, lon) { return {x: (lon - lon0) * 111320 * Math.cos(lat0 * Math.PI / 180), y: (lat - lat0) * 110540}; }
// leituras simuladas discretas (a cada F0.intervalo_s) até min(agora, corte): {id, obs, rec, lat, lon, vel, rumo, estado}. t0 = início do percurso.
// Colheita com paradas: anda F0.paradas.anda_s e para F0.paradas.para_s ("Parada · carregando"). Nada aqui grava no cenário.
function frSimular(sim, agora, F0, n) {
  const dt = F0.intervalo_s || 10, out = [], ult = Math.floor(Math.min(agora, sim.corte != null ? sim.corte : agora) / dt) * dt;
  if (!sim.rota || sim.rota.length < 2) return out;
  const v = sim.vel_kmh / 3.6, P = sim.paradas;
  const dist = t => { const e = Math.max(0, t - sim.t0); if (!P) return e * v; const ciclo = P.anda_s + P.para_s, k = Math.floor(e / ciclo), r = e - k * ciclo; return (k * P.anda_s + Math.min(r, P.anda_s)) * v; };
  const parado = t => { if (!P) return false; const e = Math.max(0, t - sim.t0), r = e % (P.anda_s + P.para_s); return r >= P.anda_s; };
  for (let k = (n || 6) - 1; k >= 0; k--) {
    const t = ult - k * dt; if (t < sim.t0) continue;
    const p = frNaRota(sim.rota, dist(t)); if (!p) continue;
    const g = frMetrosParaGraus(sim.lat0, sim.lon0, p.x, p.y), pa = parado(t);
    out.push({id: sim.os + '@' + t, obs: t, rec: t + 1, lat: g.lat, lon: g.lon, vel: pa ? 0 : sim.vel_kmh, rumo: pa ? null : p.rumo,
      estado: pa ? 'Parada · carregando' : 'Trabalhando', x: p.x, y: p.y});
  }
  return out;
}
if (typeof module !== 'undefined') module.exports = {frConjuntos, frGrupos, frConflitosDe, frRotaPoligono, frRotaCirculo, frNaRota, frMetrosParaGraus, frGrausParaMetros, frSimular, frDistM, frValida, frProcessar, frIdadeTxt, frSituacao, frAvaliar, frConflitos, frMarcadores, frExibir, frAgrupar, frFamilia, FR_TOL_FUT, FR_VMAX};
