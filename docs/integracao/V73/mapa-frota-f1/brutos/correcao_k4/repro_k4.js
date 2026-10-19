// Reprodução K4 (revisão Codex 6270760702): frota.js + frota_ui.js num VM com DOM mínimo e cenário sintético.
// Uso (de gen37/): node ../../../../docs/integracao/V73/mapa-frota-f1/brutos/correcao_k4/repro_k4.js <pasta com frota.js e frota_ui.js> . [K4,K6]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const dir = path.resolve(process.argv[2]), gen = path.resolve(process.argv[3]);
const alo = fs.readFileSync(path.join(gen, 'alocacao.py'), 'utf8');
const alV = alo.slice(alo.indexOf('function alVigente(c){'), alo.indexOf('\nfunction alHh('));

function cenario(caso) {
  const D = '2026-09-26', bl = (os, ini, fim, rs) => rs.map(r => ({r, dia: D, ini, fim, sit: 'firme'}));
  const b2 = caso === 'K6' ? [9, 11] : [9, 11], b1 = caso === 'K6' ? [6, 10] : [6, 9];
  return {ordens: {'OS-0421': {id: 'OS-0421', etapa: 'Em execução', versao: 'v2', prog: {blocos: bl('OS-0421', b1[0], b1[1], ['T03', 'PJ', 'MAR'])}},
    'OS-0424': {id: 'OS-0424', etapa: 'Em execução', versao: 'v1', prog: {blocos: bl('OS-0424', b2[0], b2[1], ['T03', 'PJ', 'MAR'])}}},
    gruposExec: {'GRP-1': {id: 'GRP-1', ids: ['OS-0421', 'OS-0424'], programa: {maquina: 'T03', implemento: 'PJ'}}}};
}
function roda(caso, hash) {
  class El {
    constructor(t) { this.tag = t; this.attrs = {}; this.children = []; this.style = {}; this.isConnected = false; this.innerHTML = ''; this.textContent = ''; this.sub = {}; const cs = new Set();
      this.classList = {toggle: (c, on) => { if (on) cs.add(c); else cs.delete(c); }, contains: c => cs.has(c)}; }
    setAttribute(k, v) { this.attrs[k] = String(v); } getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; }
    appendChild(c) { this.children.push(c); c.isConnected = true; c.parent = this; return c; }
    remove() { if (this.parent) this.parent.children = this.parent.children.filter(x => x !== this); this.isConnected = false; }
    getClientRects() { return this.isConnected ? [1] : []; } getBoundingClientRect() { return {left: 0, top: 0, bottom: 0}; }
    contains() { return false; } querySelector(s) { return this.sub[s] || null; } querySelectorAll() { return []; } focus() { doc.activeElement = this; }
  }
  const cam = new El('div'); cam.isConnected = true;
  const painel = new El('aside'); painel.isConnected = true; ['[data-frota-cab]', '[data-frota-corpo]', '[data-frota-acoes]', '.fr-x'].forEach(s => { painel.sub[s] = new El('div'); });
  const doc = {activeElement: null, hidden: false, addEventListener() {}, createElement: t => new El(t),
    querySelectorAll: s => s === '[data-frota-camada]' ? [cam] : [], querySelector: s => s === '[data-frota-painel]' ? painel : null};
  const timers = [];
  const ctx = {console, document: doc, window: {addEventListener() {}, __frotaRelogio: 1790000000}, location: {hash: hash || ''},
    sessionStorage: {getItem: () => null}, setTimeout: f => { timers.push(f); return timers.length; }, clearTimeout() {}, setInterval: () => 1, clearInterval() {},
    FROTA0: {intervalo_s: 10, limite_s: 60, passada_m: 36, recuo_m: 18, base: [-34.629941, -47.122425], vel_kmh: {'Pulverização': 8, padrao: 6}, paradas: {},
      simula: ['OS-0421', 'OS-0424'], rota_tal: {'OS-0421': 'T2', 'OS-0424': 'T2'}, demo: {}, rend: {}, tanque: {}},
    FR_ICONES: {}, AL0: {aloc: [], nome: {T03: 'Trator 03', PJ: 'Pulverizador PJ-3030 36 m', MAR: 'Marcos · operador'}, tipo: {T03: 'Máquina', PJ: 'Implemento', MAR: 'Pessoa'}},
    CEN_DIA_OP: '2026-09-26', SAF: '2026/27', FAZ: 'Santa Rita', TIDS: () => ['T1', 'T2', 'T1-B'], g2perfil: () => ({k: 'Ana', todos: true}),
    M: {ord: [{id: 'OS-0421', tal: ['T1', 'T2'], tipo: 'Pulverização · Fungicida 1ª aplicação', fase: 'Em execução', selos: [], area: 350, rz: 190, saldo: 160, resp: 'Marcos', saf: '2026/27'},
      {id: 'OS-0424', tal: ['T1-B'], tipo: 'Pulverização · Fungicida A', fase: 'Em execução', selos: [], area: 80, rz: 0, saldo: 80, resp: 'Marcos', saf: '2026/27'}],
      geoc: {T2: ['poly', '100,100 300,100 300,250 100,250']}, tal: {T2: {ha: 100}}, lg: {pivos: [], ids: []}}};
  const c = cenario(caso); ctx.cenGet = () => c;
  vm.createContext(ctx);
  vm.runInContext(alV + '\n' + fs.readFileSync(path.join(dir, 'frota.js'), 'utf8') + '\n' + fs.readFileSync(path.join(dir, 'frota_ui.js'), 'utf8'), ctx);
  // posição na tela: metros da leitura em torno da âncora, 4 m por pixel (o que o SVG faria)
  vm.runInContext('frTelaSvg = x => { const m = frGrausParaMetros(x.geo.lat0, x.geo.lon0, x.at.lat, x.at.lon); return [400 + m.x / 4, 300 - m.y / 4]; };', ctx);
  let v = {};
  const self = {state: {frOn: true, tsel: []}, setState(o) { Object.assign(this.state, o); v = {map_on: true}; ctx.frVals(self, v); }};
  const flush = () => { for (let n = 0; timers.length && n < 200; n++) timers.shift()(); };
  self.setState({}); flush();
  const md = vm.runInContext('FRUI.modelo', ctx);
  const mk = () => cam.children.filter(b => b.getAttribute('data-frota-os')).map(b => ({os: b.getAttribute('data-frota-os'), sel: b.getAttribute('aria-pressed'), aria: b.getAttribute('aria-label'), html: b.innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()}));
  const grp = () => cam.children.filter(b => /fr-grupo/.test(b.className)).map(b => b.textContent);
  const pn = () => ['[data-frota-cab]', '[data-frota-corpo]', '[data-frota-acoes]'].map(s => painel.sub[s].innerHTML).join(' ').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  const ofs = () => (pn().match(/OS-\d{4}/g) || []).filter((x, i, a) => a.indexOf(x) === i);
  const conj = Object.fromEntries(md.it.map(x => [x.cj.os, {maquina: x.cj.maquina, implemento: x.cj.implemento, prog: x.cj.prog, blocos: x.cj.blocos}]));
  const et = Object.fromEntries(md.it.map(x => [x.cj.os, 'Em execução']));
  const out = {caso, hash: hash || '', modelItems: md.it.length, physicalSets: ctx.frMarcadores(conj, et, ctx.frGrupos(c)).length, visiblePositions: md.it.filter(x => x.comPos && x.geo).length,
    conflicts: md.it.map(x => x.conflito.length), botao: v.fr_t, lista: v.fr_lt, marcadores: mk(), grupos: grp(), frSel: self.state.frSel || null};
  // lista
  self.setState({frLista: true, frSel: null}); flush(); out.listaPainel = pn(); out.listaOS = ofs();
  // painel pelo marcador (ou pelo grupo, se não houver marcador solto)
  self.setState({frLista: false, frSel: null}); flush();
  const b = cam.children.find(x => x.getAttribute('data-frota-os')); if (b) { b.onclick(); flush(); out.painelMarcador = pn(); out.painelOS = ofs(); }
  // "Ver no mapa" da OS-0424: frSel = OS-0424; o marcador do conjunto fica selecionado, também depois de redesenhar com o foco nele
  self.setState({frSel: 'OS-0424'}); flush(); const m1 = mk(); const b1 = cam.children.find(x => x.getAttribute('aria-pressed') === 'true');
  if (b1) b1.focus(); ctx.window.__frotaRelogio += 10; vm.runInContext('FRUI.modelo = frModelo(FRUI.self); frDesenha();', ctx); flush();
  const m2 = mk(); out.verNoMapa = {marcadores: m1, depois: m2, mesmoBotao: !!b1 && b1.isConnected && doc.activeElement === b1, painel: pn()};
  return out;
}
const casos = process.argv[4] ? process.argv[4].split(',') : ['K4', 'K6'];
casos.forEach(k => console.log(JSON.stringify(roda(k), null, 1)));
