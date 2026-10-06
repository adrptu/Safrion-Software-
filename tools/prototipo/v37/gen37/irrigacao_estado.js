// ===== Irrigação · estado compartilhado (IR-01..IR-04, IR-03det e camada Irrigação do Mapa) =====
// Um estado gravado no navegador (localStorage 'talhao-os-irrigacao-v1'); sem localStorage vale só para a tela aberta.
// Regras (PRD cap. 63, CAL-09, AGUA-01..08 e decisões do proprietário): água só com água não passa pelo agrônomo e é liberada pela
// prontidão (janela definida, sem conflito físico ou legal); fertirrigação é da O.S. (agrônomo libera, estoque bloqueia).
// Bloqueiam: mesma bomba em janelas sobrepostas, parada do PCM, vazão outorgada excedida e outorga vencida. O resto é aviso.
// Tempo em minutos desde 23/09/2026 00:00. Crédito no balanço = irrigação líquida (bruta medida × eficiência), uma vez por passada.
const IRR_KEY = 'talhao-os-irrigacao-v1';
let IRR_MEM = null, IRR_RAW = null, IRR_OBJ = null;
function irrClone(o) { return JSON.parse(JSON.stringify(o)); }
function irrInicial() { const s = irrClone(IRR0); irrGerar(s); return s; }
function irrGet() {
  let t = null; try { t = localStorage.getItem(IRR_KEY); } catch (e) { t = null; }
  if (t) { let o = (t === IRR_RAW && IRR_OBJ) ? IRR_OBJ : null;
    if (!o) { try { const p = JSON.parse(t); if (p && p.v === IRR0.v) { o = p; o.capt = irrClone(IRR0.capt); } } catch (e) {} }   // outorga: vale sempre a do cadastro (CTL-5)
    if (o && irrOrfa(o)) { irrReset(); o = null; }
    if (o) { IRR_RAW = t; IRR_OBJ = o; return o; } }
  if (IRR_MEM && irrOrfa(IRR_MEM)) IRR_MEM = null;
  if (!IRR_MEM) IRR_MEM = irrInicial(); return IRR_MEM;
}
function irrSave(s) { s.cenVisto = Math.max(s.cenVisto || 0, irrCenRev()); IRR_MEM = s; try { const t = JSON.stringify(s); localStorage.setItem(IRR_KEY, t); IRR_RAW = t; IRR_OBJ = s; } catch (e) {} }
function irrReset() { IRR_MEM = null; IRR_RAW = null; IRR_OBJ = null; try { localStorage.removeItem(IRR_KEY); } catch (e) {} }
// mudança atômica: aplica fn numa cópia, grava e devolve a mensagem; com erro nada é gravado
function irrMudar(self, fn) {
  const s = irrClone(irrGet()); let r;
  try { r = fn(s) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (r.erro) { if (self) self.setState({ g2toast: r.erro }); return r; }
  s.rev = (s.rev || 0) + 1; irrSave(s); if (self) self.setState({ irrrev: s.rev, g2toast: r.msg || '' }); return r;
}
function irrOuvir(self) {
  if (self.__irrOuvindo) return; self.__irrOuvindo = true;
  try { window.addEventListener('storage', (e) => { if (e.key === IRR_KEY || e.key === 'talhao-os-cenario-v1') self.setState({ irrrev: Date.now() }); }); } catch (e) {}
}
// cenário da O.S. (cenario.js): lido uma vez por versão gravada (o texto do localStorage serve de chave do cache)
let IRR_CRAW = null, IRR_COBJ = null;
function irrCen() {
  try { const t = localStorage.getItem('talhao-os-cenario-v1');
    if (t) { if (t === IRR_CRAW && IRR_COBJ) return IRR_COBJ; const o = JSON.parse(t); if (o && typeof CEN0 !== 'undefined' && o.v === CEN0.v) { IRR_CRAW = t; IRR_COBJ = o; return o; } } } catch (e) {}
  try { return (typeof cenGet === 'function') ? cenGet() : null; } catch (e) { return null; }
}
// "Restaurar demonstração" (O.S., Estoque, app) zera o cenário da O.S.: a irrigação volta à semente junto (inclusive as v2)
function irrCenRev() { const c = irrCen(); return c ? (c.rev || 0) : 0; }
function irrOrfa(o) { if (!o) return false; const c = irrCen(); if (!c) return false;
  if (o.cenVisto && irrCenRev() < o.cenVisto) return true;   // o cenário voltou ao início depois da última gravação da irrigação
  if (!o.cenRev) return false; if (irrCenRev() < o.cenRev) return true;
  return Object.values(o.ordens || {}).some(z => z.fert && z.fert.cen && !(c.ordens && c.ordens[z.id])); }

// ---------- formatos ----------
const IRR_D0 = Date.UTC(2026, 8, 23);
// área da v2 (Adicionar produtos): com passada em curso, o que falta dela (2 casas); a área já coberta fica na v1. Mesma conta na prévia.
// área digitada com 2 casas, meio para cima no decimal (20,275 → 20,28; o binário de 20,275 × 100 daria 20,27)
function irr2(n) { const t = String(n); return /e/i.test(t) ? Math.round(n * 100) / 100 : Number(Math.round(Number(t + 'e2')) + 'e-2'); }
function irrAreaV2(x, p) { return p ? Math.round((x.ha - Math.min(x.ha, p.cob || 0)) * 100) / 100 : x.ha; }
// v2 que daria total 0 pela regra única: a liberação recusaria e a ordem ficaria sem saída; diz a causa (mesmo texto na prévia)
function irrV2Zero(o, x, p, dose) { const a = irrAreaV2(x, p); if (!(a > 0)) return irrPassProx(o) ? 'A passada ' + p.n + ' já cobriu o setor: confirme o término dela e adicione os produtos para as próximas passadas.' : 'A passada já cobriu o setor: confirme o término e programe uma nova fertirrigação na O.S.';
  if (p && irrPassProx(o)) return 'A passada ' + p.n + ' está em curso e há outra programada: confirme o término dela e adicione os produtos para as próximas passadas.';   // a v2 cobriria só o saldo desta passada com a água das seguintes (PRE-REV U2)
  return (dose > 0 && !(cenQtd(dose, a) > 0)) ? 'Dose × área dá 0 kg: aumente a dose.' : ''; }
function irrN(n, d, dmin) { return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: (dmin === undefined ? (d || 0) : dmin), maximumFractionDigits: d || 0 }); }
function irrHa(n) { return irrN(n, Math.abs(n % 1) > 1e-9 ? 1 : 0); }
function irrMm(n) { return irrN(n, 2, 1); }      // 10,81 · 4,0 · 13,5 · 6,75 (o mesmo formato em todas as telas)
function irrHm(m) { m = Math.round(m); const d = ((m % 1440) + 1440) % 1440; return String(Math.floor(d / 60)).padStart(2, '0') + ':' + String(d % 60).padStart(2, '0'); }
function irrDiaN(m) { return Math.floor(Math.round(m) / 1440); }
function irrDdmm(k) { const d = new Date(IRR_D0 + k * 86400000); return String(d.getUTCDate()).padStart(2, '0') + '/' + String(d.getUTCMonth() + 1).padStart(2, '0'); }
function irrIso(k) { const d = new Date(IRR_D0 + k * 86400000); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
function irrDeIso(iso) { const a = String(iso || '').split('-').map(Number); if (a.length !== 3 || a.some(isNaN)) return null; return Math.round((Date.UTC(a[0], a[1] - 1, a[2]) - IRR_D0) / 86400000); }
function irrDiaT(m) { const k = irrDiaN(m); return k === 0 ? 'hoje' : (k === 1 ? 'amanhã' : (k === -1 ? 'ontem' : irrDdmm(k))); }
function irrQuando(m) { return irrDiaT(m) + ' ' + irrHm(m); }
function irrJan(a, b) { if (a === null || a === undefined) return 'a definir'; return irrQuando(a) + '–' + (irrDiaN(a) === irrDiaN(b) ? irrHm(b) : irrQuando(b)); }
function irrPct(n) { return (n > 0.05 ? '+' : (n < -0.05 ? '−' : '')) + irrN(Math.abs(n), 1) + ' %'; }
function irrH(min) { return irrN(min / 60, 1) + ' h'; }

// ---------- setor: balanço e necessidade ----------
function irrSonda(s, x) { return x && x.sonda ? s.fontes[x.sonda] : null; }
function irrEst(s, x) { const so = irrSonda(s, x); return !!(so && so.st !== 'Ativa'); }   // sonda suspeita ou sem dado → estimativa por ET
// aplicação: lâmina = volume ÷ área COBERTA (CAL-09); a passagem parcial vale só na faixa coberta
function irrApCob(a) { return (a.cob === null || a.cob === undefined) ? a.ha : a.cob; }
function irrApBr(a) { const c = irrApCob(a); return c > 0 ? a.vol / (10 * c) : 0; }
function irrApNet(a) { return irrApBr(a) * a.ef / 100; }
function irrApParc(a, ha) { return irrApCob(a) < ha - 1e-9; }
// água das fertirrigações apontadas na O.S. (cenário): área realizada × lâmina bruta por ha da ordem; provisória até a O.S. encerrar
function irrApsOS(s, sid) {
  const x = s.setores[sid]; const c = irrCen(); const out = []; if (!c || !c.ordens) return out;
  const add = (id, lamHa, base, q, ef) => { const co = c.ordens[id]; if (!co || !(lamHa > 0)) return; const R = Math.min(x.ha, Math.max(0, (co.realizado || 0) - (base || 0))); if (!(R > 0)) return;
    out.push({ q, os: id, n: 'O.S.', vol: Math.round(lamHa * R * 10), ha: x.ha, ef, cob: R, txt: 'fertirrigação apontada na O.S.', prov: co.etapa !== 'Encerradas', osc: true }); };
  Object.values(s.ordens).forEach(o => { if (o.setor === sid && o.fert && o.fert.cen) add(o.id, o.fert.lamHa, 0, o.fert.q, o.ef || x.efic); });
  Object.keys(s.fert).forEach(k => { const f = s.fert[k]; if (f.setor === sid && !s.ordens[k]) add(k, f.lam, f.base, (f.ini === null || f.ini === undefined) ? s.agora : f.ini, x.efic); });
  return out;
}
// aplicações do setor (gravadas + O.S.), em ordem de tempo; a v1 de uma v2 vira definitiva quando a O.S. encerra
function irrApsSetor(s, sid) {
  const x = s.setores[sid]; if (!x || !x.bal) return []; const c = irrCen();
  return x.bal.ap.map(a => { const o = s.ordens[a.os]; if (a.prov && o && o.fert) { const co = c && c.ordens ? c.ordens[a.os] : null; if (co && co.etapa === 'Encerradas') return Object.assign({}, a, { prov: false }); } return a; })
    .concat(irrApsOS(s, sid)).sort((p, q) => p.q - q.q);
}
// crédito no déficit do pivô: volta/turno completo credita o pivô inteiro; passagem parcial fica na faixa coberta e não baixa o déficit
// do pivô, salvo quando as parciais da MESMA ordem completam a área (v1 + saldo da v2) — aí vale a menor lâmina líquida entre elas.
function irrCreditos(s, sid, ate) {
  // parcial com 0 m³ (avanço pequeno que a telemetria arredonda a 0) ainda conta a área coberta da ordem; a lâmina vem só de quem tem volume (PRE-REV U1)
  const x = s.setores[sid]; const aps = irrApsSetor(s, sid).filter(a => (ate === undefined || a.q < ate) && irrApCob(a) > 0 && (a.vol > 0 || irrApParc(a, x.ha)));
  let gov = 0, ultCheia = -1e9; const grp = {}; let faixa = null;
  aps.forEach(a => { if (!irrApParc(a, x.ha)) { gov += irrApNet(a); ultCheia = Math.max(ultCheia, a.q); return; }
    const g = grp[a.os] || (grp[a.os] = { cob: 0, net: 1e9, q: a.q }); g.cob += irrApCob(a); if (a.vol > 0) g.net = Math.min(g.net, irrApNet(a)); g.q = Math.max(g.q, a.q); });
  Object.keys(grp).forEach(k => { const g = grp[k]; if (g.net < 1e9 && g.cob >= x.ha - 1e-6) { gov += g.net; ultCheia = Math.max(ultCheia, g.q); } });
  // faixa pendente: a parcial mais recente que nenhuma volta completa cobriu depois
  Object.keys(grp).forEach(k => { const g = grp[k]; if (g.net < 1e9 && g.cob < x.ha - 1e-6 && g.q > ultCheia && (!faixa || g.q > faixa.q)) faixa = { os: k, q: g.q, cob: g.cob, net: g.net }; });
  return { gov, faixa, aps };
}
function irrBase(b) { return b.d0 + b.etc - b.pef; }
function irrDef(s, sid) { const x = s.setores[sid]; if (!x || !x.bal) return null; return Math.max(0, irrBase(x.bal) - irrCreditos(s, sid).gov); }
// faixa coberta por passagem parcial (ainda sem o resto da volta): área e déficit dela
function irrFaixaCob(s, sid) { const x = s.setores[sid]; if (!x || !x.bal) return null; const cr = irrCreditos(s, sid); if (!cr.faixa) return null;
  return { os: cr.faixa.os, cob: cr.faixa.cob, d: Math.max(0, irrBase(x.bal) - cr.gov - cr.faixa.net) }; }
function irrLamTxt(vol, cob, ha) { return cob < ha - 1e-9 ? irrMm(vol / (10 * cob)) + ' mm na faixa de ' + irrN(cob, 2, 0) + ' ha' : irrMm(vol / (10 * ha)) + ' mm no setor'; }
function irrCobO(o) { return o.passadas.filter(p => p.st === 'Feita' || p.st === 'Parcial').reduce((q, p) => Math.max(q, p.cob || 0), 0); }
function irrDefTxt(s, sid, pre) { const x = s.setores[sid]; const fx = irrFaixaCob(s, sid); return 'déficit do ' + x.nome + ' ' + (pre || '') + irrN(irrDef(s, sid), 1) + ' mm' + (fx ? ' (faixa de ' + irrN(fx.cob, 2, 1) + ' ha: ' + irrN(fx.d, 1) + ' mm)' : ''); }
function irrDur(x, lam) { return Math.round(lam * x.ha * 10 / (x.vazao * 3.6) * 60); }
function irrNec(s, sid) {
  const x = s.setores[sid]; const d = irrDef(s, sid); if (d === null) return null;
  const br = d / (x.efic / 100); const np = Math.max(1, Math.ceil(br / x.lmax - 1e-9)); const por = br / np;
  return { liq: d, br, np, por, vol: br * x.ha * 10, dur: irrDur(x, por) };
}
// déficit no fim de cada dia (7 dias fechados) com ≈ nos dias estimados
function irrSerie(s, sid) {
  const x = s.setores[sid]; const b = x && x.bal; if (!b) return [];
  const so = irrSonda(s, x); const estDesde = (so && so.st !== 'Ativa' && so.desde !== undefined) ? irrDiaN(so.desde) : 99;
  const out = []; const etcd = b.etc / b.dias; const k0 = irrDiaN(b.ini); let nd = 0, chuva = 0;
  for (let k = -7; k <= -1; k++) {
    if (k < k0) { out.push({ k, t: irrDdmm(k), v: null, est: false }); continue; }
    nd++; if (b.pef && irrDdmm(k) === '20/09') chuva = b.pef;
    const d = b.d0 + etcd * nd - chuva - irrCreditos(s, sid, (k + 1) * 1440).gov;
    out.push({ k, t: irrDdmm(k), v: Math.max(0, d), est: k > estDesde });
  }
  return out;
}

// ---------- ordens ----------
const IRR_FASES = ['A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas'];
// etapa da ordem: a v2 (com produto) segue a etapa da O.S. depois que o agrônomo libera
function irrEt(o) { if (o.fert) { const et = irrFertEtapa(o.id); if (et && et !== 'A liberar') return et; } return o.etapa; }
function irrAberta(o) { return ['Encerradas', 'Canceladas'].indexOf(irrEt(o)) < 0; }
function irrPausaMin(o, n) { return (o.exec.pausas || []).filter(p => p.n === n && p.fim !== undefined && p.fim !== null).reduce((q, p) => q + (p.fim - p.ini), 0); }
function irrPausada(o) { return (o.exec.pausas || []).some(p => p.fim === null || p.fim === undefined); }
function irrFimP(o, p) { if (p.ini === null || p.ini === undefined) return null; if (p.fimReal !== undefined && p.fimReal !== null) return p.fimReal; const i0 = (p.iniReal !== undefined && p.iniReal !== null) ? p.iniReal : p.ini; return i0 + p.dur + irrPausaMin(o, p.n); }
function irrJanO(o) { const ps = o.passadas.filter(p => p.ini !== null && p.ini !== undefined); if (!ps.length) return 'a definir'; if (o.passadas.length === 1) return irrJan(ps[0].ini, irrFimP(o, ps[0])); return o.passadas.map(p => p.ini === null ? 'a definir' : irrJan(p.ini, irrFimP(o, p))).join(' · '); }
function irrIni(o) { const ps = o.passadas.filter(p => p.ini !== null && p.ini !== undefined); return ps.length ? Math.min.apply(null, ps.map(p => p.ini)) : null; }
function irrPassAtual(o) { return o.passadas.find(p => p.st === 'Em execução') || null; }
function irrPassProx(o) { return o.passadas.find(p => p.st === 'Programada') || null; }
function irrOrdensSetor(s, sid) { return Object.values(s.ordens).filter(o => o.setor === sid).sort((a, b) => (irrIni(a) === null ? 1e9 : irrIni(a)) - (irrIni(b) === null ? 1e9 : irrIni(b))); }
function irrFertEtapa(id) { const c = irrCen(); const o = c && c.ordens ? c.ordens[id] : null; return o ? o.etapa : null; }
function irrFertImpedida(id) { const c = irrCen(); const o = c && c.ordens ? c.ordens[id] : null; return !!(o && (o.selos || []).some(x => /^Impedida/.test(x.t || ''))); }
function irrFertResp(id) { const c = irrCen(); const o = c && c.ordens ? c.ordens[id] : null; return o ? (o.resp || '') : ''; }
// o que segura a fertirrigação na O.S. (mesma regra da tela O.S.): bomba impedida ou falta de insumo no Estoque para liberar
function irrFertBloq(id) {
  const c = irrCen(); const co = c && c.ordens ? c.ordens[id] : null; if (!co) return null;
  const imp = (co.selos || []).find(x => /^Impedida/.test(x.t || '')); if (imp) return { t: /bomba/.test(imp.t) ? 'Impedida · bomba parada' : imp.t, dono: 'Manutenção', passo: 'Abrir ' + id, h: 'OS.dc.html#' + id };
  if (co.etapa === 'A liberar' && (co.ins || []).length && typeof cenLote === 'function') {
    for (const z of co.ins) { const l = cenLote(c, z.p); if (!l || cenDisp(l) + 1e-9 < (z.tot || 0)) return { t: 'Falta insumo · ' + z.p, dono: 'Suprimentos', passo: 'Receber o insumo no Estoque', h: 'EST.dc.html' }; } }
  return null;
}
// janelas comprometidas na bomba: ordens Liberadas/Em execução (passadas ainda não feitas); a v2 segura a janela desde a criação
// até a O.S. encerrar (o agrônomo libera sem nova checagem de bomba); fertirrigações da O.S. abertas
function irrComprometidas(s, excl) {
  const out = [];
  Object.values(s.ordens).forEach(o => { if (o.id === excl) return; const et = irrEt(o);
    if (o.fert ? ['A liberar', 'Liberadas', 'Em execução'].indexOf(et) < 0 : ['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) return; const x = s.setores[o.setor];
    o.passadas.forEach(p => { if (p.ini === null || p.ini === undefined || p.st === 'Feita' || p.st === 'Parcial') return; out.push({ os: o.id, n: p.n, bomba: x.bomba, capt: x.capt, ls: x.vazao, ini: p.ini, fim: irrFimP(o, p) }); });
    if (o.fert && o.fert.sw) out.push({ os: o.id, n: 0, bomba: x.bomba, capt: x.capt, ls: x.vazao, ini: o.fert.sw.ini, fim: o.fert.sw.fim, fert: true }); });
  Object.keys(s.fert).forEach(k => { const f = s.fert[k]; if (!f.ini || k === excl) return; const et = irrFertEtapa(k); if (et && ['Encerradas', 'Canceladas', 'Em conferência'].indexOf(et) >= 0) return;
    const x = s.setores[f.setor]; out.push({ os: k, n: 1, bomba: x.bomba, capt: x.capt, ls: x.vazao, ini: f.ini, fim: f.fim, fert: true }); });
  return out;
}
function irrOv(a1, b1, a2, b2) { return a1 < b2 && a2 < b1; }
// ponta de energia (aviso de custo, não bloqueia)
function irrPonta(s, a, b) { const P = s.ponta; let ini = null, fim = null;
  for (let k = irrDiaN(a); k <= irrDiaN(b); k++) { const pa = k * 1440 + P[0], pb = k * 1440 + P[1]; if (irrOv(a, b, pa, pb)) { const x = Math.max(a, pa), y = Math.min(b, pb); if (ini === null) { ini = x; fim = y; } } }
  if (ini === null) return ''; const tot = (fim - ini) >= (P[1] - P[0]); return (tot ? 'Ponta' : 'Ponta parcial') + ' (' + irrN(ini % 1440 / 60, 0) + '–' + irrN((fim % 1440 || 1440) / 60, 0) + ' h)'; }
// ---------- outorga da captação (fonte única: o cadastro, via dados_lagoa_fonte.captacao; CTL-5 · RL-E4) ----------
// volume do dia autorizado (m³) = vazão (L/s) × horas por dia × 3,6: uma conta só para a trava e para as telas
function irrCapDia(cp) { return cp ? cp.ls * cp.h * 3.6 : 0; }
function irrOutC(st) { return { 'Vigente': 'green', 'Vence em 90 dias': 'yellow', 'Em renovação': 'yellow', 'Vencida': 'red' }[st] || 'gray'; }
function irrOutVenc(s, cp) { const a = String((cp && cp.venc) || '').split('-'); if (a.length !== 3) return 'sem vencimento no cadastro';
  return (cp.venc < s.hoje ? 'venceu em ' : 'até ') + a[2] + '/' + a[1] + '/' + a[0]; }
// bloqueios de uma janela: bomba ocupada, parada do PCM, outorga vencida, vazão outorgada (instantânea e do dia)
function irrBloqJanela(s, x, a, b, excl, proprias) {
  const F = s.faz[x.faz]; const out = []; const occ = irrComprometidas(s, excl).concat(proprias || []);
  occ.filter(w => w.bomba === x.bomba && irrOv(a, b, w.ini, w.fim)).forEach(w => out.push({ k: 'bomba', c: 'red', t: 'Conflito · ' + (w.os === excl ? 'passadas sobrepostas' : w.os + ' na ' + x.bnome), h: irrJan(w.ini, w.fim), dono: F.pcp, os: w.os }));
  s.paradas.filter(z => z.bomba === x.bomba && irrOv(a, b, z.ini, z.fim)).forEach(z => out.push({ k: 'parada', c: 'red', t: 'Conflito · ' + z.txt, h: irrHm(z.ini) + '–' + irrHm(z.fim) + (irrDiaN(z.ini) !== irrDiaN(z.fim) ? ' (' + irrDdmm(irrDiaN(z.fim)) + ')' : ''), dono: z.dono || F.pcm, ref: z.ref }));
  const cp = s.capt[x.capt];
  if (cp) {
    if (cp.st === 'Vencida') { out.push({ k: 'outorga', c: 'red', t: 'Outorga vencida · ' + cp.nome, dono: F.gestor }); return out; }   // sem outorga vigente nada se capta: a vazão não entra
    const ws = occ.filter(w => w.capt === x.capt && w.bomba !== x.bomba);
    const pts = [a].concat(ws.filter(w => w.ini > a && w.ini < b).map(w => w.ini)); let mx = 0;
    pts.forEach(t => { const q = x.vazao + ws.filter(w => w.ini <= t && w.fim > t).reduce((q2, w) => q2 + w.ls, 0); if (q > mx) mx = q; });
    if (mx > cp.ls + 1e-9) out.push({ k: 'vazao', c: 'red', t: 'Sem vazão outorgada · ' + irrN(mx) + ' de ' + irrN(cp.ls) + ' L/s', dono: F.gestor });
    else { const lim = irrCapDia(cp); for (let k = irrDiaN(a); k <= irrDiaN(b); k++) { const d0 = k * 1440, d1 = d0 + 1440; let v = 0;
        ws.concat([{ ini: a, fim: b, ls: x.vazao }]).forEach(w => { const o0 = Math.max(d0, w.ini), o1 = Math.min(d1, w.fim); if (o1 > o0) v += w.ls * (o1 - o0) * 0.06; });
        if (v > lim + 1e-6) { out.push({ k: 'vazao', c: 'red', t: 'Sem vazão outorgada · ' + irrN(v) + ' de ' + irrN(lim) + ' m³ em ' + irrDdmm(k), dono: F.gestor }); break; } } }
  }
  return out;
}
// prontidão da ordem: bloqueios (impedem a liberação) e avisos (não impedem)
function irrChecar(s, o, ps) {
  ps = ps || o.passadas; const x = s.setores[o.setor]; const F = s.faz[x.faz]; const bloq = [], av = [];
  const pend = ps.filter(p => p.st === 'Programada' || p.st === 'Em execução');
  if (pend.some(p => p.ini === null || p.ini === undefined)) bloq.push({ k: 'jan', c: 'yellow', t: 'Janela a definir', dono: F.irrig });
  // outorga vencida sem janela: quem resolve é o gestor (com janela, irrBloqJanela já trava por passada)
  { const cp0 = s.capt[x.capt]; if (cp0 && cp0.st === 'Vencida' && pend.some(p => p.ini === null || p.ini === undefined)) bloq.unshift({ k: 'outorga', c: 'red', t: 'Outorga vencida · ' + cp0.nome, dono: F.gestor }); }
  const prop = [];
  pend.forEach(p => { if (p.ini === null || p.ini === undefined) return; const a = p.ini, b = irrFimP(o, p);
    irrBloqJanela(s, x, a, b, o.id, prop).forEach(z => bloq.push(z)); prop.push({ os: o.id, n: p.n, bomba: x.bomba, capt: x.capt, ls: x.vazao, ini: a, fim: b });
    const pt = irrPonta(s, a, b); if (pt) av.push({ k: 'ponta', t: pt }); });
  // intervalo mínimo entre inícios (passadas da ordem e a ordem anterior do setor): só aviso
  const ini = ps.filter(p => p.ini !== null && p.ini !== undefined).map(p => p.ini);
  const ant = irrOrdensSetor(s, o.setor).filter(z => z.id !== o.id && z.etapa !== 'Canceladas').map(z => irrIni(z)).filter(q => q !== null && ini.length && q < ini[0]);
  const todos = ant.slice(-1).concat(ini).sort((p, q) => p - q);
  for (let i = 1; i < todos.length; i++) { const dh = (todos[i] - todos[i - 1]) / 60; if (dh < x.imin - 1e-9) { av.push({ k: 'int', t: 'Intervalo curto · ' + irrN(dh, 1) + ' h (mín. ' + irrN(x.imin) + ' h)' }); break; } }
  if (irrEst(s, x)) av.push({ k: 'est', t: 'Estimativa por ET' });
  const cp = s.capt[x.capt]; if (cp && cp.aviso) av.push({ k: 'renov', t: cp.aviso });   // aviso da outorga vem do cadastro (vence em 90 dias, em renovação)
  // lâmina × necessidade (só aviso): acima do que o setor vai precisar até a última passada, ou setor abaixo do limiar de irrigação
  if (x.bal && !ps.some(p => p.st === 'Feita' || p.st === 'Parcial' || p.st === 'Em execução')) {
    const liq = ps.filter(p => p.st === 'Programada').reduce((q, p) => q + p.lam, 0) * (o.ef || x.efic) / 100; const d = irrDef(s, o.setor);
    const iU = ini.length ? Math.max.apply(null, ini) : null; const need = iU === null ? null : irrNecAte(s, o, iU);
    if (need !== null && liq > need + Math.max(1, 0.1 * liq)) av.push({ k: 'acima', t: 'Lâmina acima da necessidade · ' + irrMm(liq) + ' mm líquidos para ' + irrN(need, 1) + ' mm' });
    else if (x.limiar !== null && x.limiar !== undefined && d < x.limiar - 1e-9) av.push({ k: 'limiar', t: 'Abaixo do limiar · déficit ' + irrN(d, 1) + ' de ' + irrN(x.limiar, 1) + ' mm' });
  }
  const uniq = (l) => l.filter((z, i) => l.findIndex(y => y.t === z.t) === i);
  return { bloq: uniq(bloq), av: uniq(av) };
}
// necessidade do setor no momento t: déficit de hoje − água das ordens abertas que começam antes desta + ETc prevista até t
function irrNecAte(s, o, t) {
  const x = s.setores[o.setor]; const d = irrDef(s, o.setor); if (d === null) return null; const i0 = irrIni(o); let rest = d;
  irrOrdensSetor(s, o.setor).filter(z => z.id !== o.id && irrAberta(z) && irrEt(z) !== 'Em conferência' && irrIni(z) !== null && (i0 === null || irrIni(z) < i0))
    .forEach(z => { rest -= z.passadas.filter(p => p.st === 'Programada' || p.st === 'Em execução').reduce((q, p) => q + p.lam, 0) * (z.ef || x.efic) / 100; });
  return Math.max(0, rest) + x.bal.etc / x.bal.dias * Math.max(0, t - s.agora) / 1440;
}
// passadas em ordem de tempo: cada uma começa depois do fim da anterior (vale para o painel e para salvar)
function irrOrdemErro(o) {
  const ps = o.passadas.slice().sort((a, b) => a.n - b.n);
  for (let k = 1; k < ps.length; k++) { const a = ps[k - 1], b = ps[k]; if (a.ini === null || a.ini === undefined || b.ini === null || b.ini === undefined || b.st !== 'Programada') continue;
    const fa = irrFimP(o, a); if (b.ini < fa) return 'A passada ' + b.n + ' começa antes do fim da passada ' + a.n + ' (' + irrQuando(fa) + ').'; }
  return '';
}
function irrNovoId(s, pre) {
  const c = irrCen(); const tem = (id) => !!s.ordens[id] || !!(c && c.ordens && c.ordens[id]);
  if (pre === 'OS') { let n = s.seq.os; let id; do { n++; id = 'OS-0' + n; } while (tem(id)); s.seq.os = n; return id; }
  const n = ++s.seq[pre]; return { lib: 'LIB-', ex: 'EX-', au: 'AU-' }[pre] + n;
}
function irrTr(o, q, rec, ev, quem) { o.trilha.push({ q, rec, ev, quem }); }
// liberação automática pela prontidão (água sem produto) ou revogação, se a ordem deixou de estar pronta
function irrProntidao(s, o) {
  if (o.fert) return '';
  const ck = irrChecar(s, o); const x = s.setores[o.setor];
  if (o.etapa === 'A liberar' && !ck.bloq.length) {
    o.lib = o.libRes || irrNovoId(s, 'lib'); delete o.libRes; o.etapa = 'Liberadas'; o.libQ = s.agora;
    irrTr(o, s.agora, o.lib, 'Liberada pela prontidão · janela ' + irrJanO(o) + ' · ' + x.bnome + ', energia e outorga conferidas' + (ck.av.length ? ' · avisos: ' + ck.av.map(a => a.t).join(', ') : ''), 'sistema');
    return o.id + ' Liberadas · ' + o.lib + ' · ' + irrMm(o.lam) + ' mm' + (o.passadas.length > 1 ? ' em ' + o.passadas.length + ' passadas' : '') + ' · ' + irrJanO(o) + ' · liberar não liga o equipamento.';
  }
  if (o.etapa === 'Liberadas' && ck.bloq.length) { o.libRes = o.lib; irrTr(o, s.agora, o.lib, 'Liberação revogada · ' + ck.bloq.map(b => b.t).join(', '), 'sistema'); o.lib = null; o.etapa = 'A liberar';
    return o.id + ' voltou a A liberar: ' + ck.bloq.map(b => b.t).join(', ') + '.'; }
  return '';
}

// ---------- janela sugerida: bomba livre, sem parada, fora da ponta, dentro da outorga e do intervalo mínimo ----------
function irrSugerir(s, sid, durs, desde, excl) {
  const x = s.setores[sid]; const out = []; const prop = [];
  // próximo ciclo: depois do fim das passadas já programadas no setor e com o intervalo mínimo desde o último início
  irrOrdensSetor(s, sid).filter(z => z.id !== excl && irrAberta(z) && z.etapa !== 'Em conferência').forEach(z => z.passadas.forEach(p => {
    if (p.ini === null || p.ini === undefined || p.st === 'Feita' || p.st === 'Parcial') return; desde = Math.max(desde, irrFimP(z, p), p.ini + x.imin * 60); }));
  durs.forEach((du, i) => { let t = Math.ceil(Math.max(desde, i ? out[i - 1] + x.imin * 60 : desde) / 15) * 15; let achou = null;
    const semPonta = du <= (1440 - (s.ponta[1] - s.ponta[0]));
    for (let k = 0; k < 4 * 24 * 5 && achou === null; k++) { const a = t + k * 15, b = a + du;
      if (semPonta && irrPonta(s, a, b)) continue; if (irrBloqJanela(s, x, a, b, excl, prop).length) continue; achou = a; }
    out.push(achou); if (achou !== null) prop.push({ os: excl || 'novo', n: i + 1, bomba: x.bomba, capt: x.capt, ls: x.vazao, ini: achou, fim: achou + du }); });
  return out;
}
// opções para resolver o conflito: a primeira janela livre depois da original e a primeira à noite (fora da ponta)
function irrOpcoes(s, id) {
  const o = s.ordens[id]; const ps = o.passadas.filter(p => p.st === 'Programada'); const durs = ps.map(p => p.dur); const ini = ps[0] && ps[0].ini !== null ? ps[0].ini : s.agora;
  const opts = []; const add = (inis, t) => { if (inis.some(q => q === null)) return; const key = inis.join(','); if (opts.some(z => z.key === key)) return;
    opts.push({ key, inis, t: t + ' · ' + inis.map((q, i) => irrJan(q, q + durs[i])).join(' · ') }); };
  add(irrSugerir(s, o.setor, durs, Math.max(ini, s.agora), id), 'Logo depois');
  const noite = irrDiaN(Math.max(ini, s.agora)) * 1440 + s.ponta[1]; add(irrSugerir(s, o.setor, durs, Math.max(noite, s.agora), id), 'À noite');
  return opts;
}

// ---------- geração diária (AGUA-01): tarefa única por setor e ciclo; idempotente ----------
function irrFertAbertaSetor(s, sid) { return Object.keys(s.fert).filter(k => { if (s.fert[k].setor !== sid) return false; const et = irrFertEtapa(k); return !et || ['Encerradas', 'Canceladas'].indexOf(et) < 0; }); }
function irrNova(s, sid, quem) {
  const x = s.setores[sid]; const n = irrNec(s, sid); const F = s.faz[x.faz];
  const id = irrNovoId(s, 'OS'); const au = irrNovoId(s, 'au'); const est = irrEst(s, x);
  const durs = Array.from({ length: n.np }, () => n.dur); const inis = irrSugerir(s, sid, durs, s.agora, id);
  const o = { id, faz: x.faz, setor: sid, tipo: 'água', versao: 'v1', etapa: 'A liberar', lam: Math.round(n.br * 100) / 100, au, ef: x.efic, ex: null,
    orig: { d: Math.round(n.liq * 10) / 10, q: s.agora, t: 'balanço de 23/09' + (est ? ' · estimativa por ET' : '') + (F.demo ? ' · demonstrativo' : '') },
    passadas: inis.map((q, i) => ({ n: i + 1, ini: q, dur: n.dur, lam: Math.round(n.por * 100) / 100, st: 'Programada', cob: null, vol: null })),
    exec: { pausas: [] }, conf: null, fert: null, trilha: [] };
  irrTr(o, s.agora, au, 'Necessidade ' + (quem === 'sistema' ? 'gerada pelo balanço' : 'programada por ' + quem) + ' · déficit ' + irrN(n.liq, 1) + ' mm → ' + irrMm(n.br) + ' mm brutos em ' + n.np + (n.np > 1 ? ' passadas de ' + irrMm(n.por) + ' mm (limite ' + irrMm(x.lmax) + ' mm)' : ' passada') + (inis.every(q => q !== null) ? ' · janela sugerida ' + inis.map((q, i) => irrJan(q, q + durs[i])).join(' · ') : ' · sem janela livre em 5 dias'), quem);
  s.ordens[id] = o; const lib = irrProntidao(s, o);
  return { o, msg: id + ' criada · ' + irrMm(o.lam) + ' mm em ' + n.np + (n.np > 1 ? ' passadas' : ' passada') + ' · ' + (lib || 'A liberar: ' + irrChecar(s, o).bloq.map(b => b.t).join(', ')) };
}
function irrGerar(s) {
  if (s.ger) return 0; let n = 0;
  Object.keys(s.setores).forEach(sid => { const x = s.setores[sid]; if (!x.bal || x.limiar === null || x.limiar === undefined) return;
    const d = irrDef(s, sid); if (d < x.limiar) return;
    if (irrOrdensSetor(s, sid).some(irrAberta) || irrFertAbertaSetor(s, sid).length) return;
    irrNova(s, sid, 'sistema'); n++; });
  s.ger = true; return n;
}

// ---------- comandos ----------
function irrO(s, id) { const o = s.ordens[id]; if (!o) throw new Error('Ordem ' + id + ' não encontrada na irrigação.'); return o; }
function irrProgramar(s, sid) {
  const x = s.setores[sid]; if (!x) throw new Error('Setor não encontrado.'); if (!x.bal) throw new Error(x.nome + ' não irriga agora (' + (x.fase || 'sequeiro') + ').');
  const ab = irrOrdensSetor(s, sid).filter(irrAberta).filter(o => irrEt(o) !== 'Em conferência');
  if (ab.length) return { id: ab[0].id, rec: true, msg: 'Tarefa única ' + ab[0].id + ' recuperada · ' + x.nome + ' · ' + irrEt(ab[0]) + ' · nenhuma ordem duplicada.' };
  const fe = irrFertAbertaSetor(s, sid); const fb = fe.length ? irrFertBloq(fe[0]) : null;
  if (fe.length && !fb) return { id: fe[0], fert: true, rec: true, msg: x.nome + ' já tem a fertirrigação ' + fe[0] + ' aberta: a água vai junto com ela · nenhuma ordem duplicada.' };
  const n = irrNec(s, sid); if (n.liq < 0.05) throw new Error(x.nome + ' sem déficit hoje: nada a programar.');
  const r = irrNova(s, sid, s.faz[x.faz].irrig); if (fb) irrTr(r.o, s.agora, r.o.au, 'Só água: a fertirrigação ' + fe[0] + ' segue parada na O.S. (' + fb.t + ')', s.faz[x.faz].irrig);
  return { id: r.o.id, msg: r.msg + (fb ? ' · só água: ' + fe[0] + ' segue parada (' + fb.t + ').' : '') };
}
// fertirrigação aberta e parada na O.S. (insumo, bomba): a água do setor pode ir sem o produto
function irrFertParadaSetor(s, sid) { const fe = irrFertAbertaSetor(s, sid); if (!fe.length) return null; const fb = irrFertBloq(fe[0]); return fb ? { id: fe[0], b: fb } : null; }
function irrDefinirJanela(s, id, inis) {
  const o = irrO(s, id); if (['A liberar', 'Liberadas'].indexOf(o.etapa) < 0 && !(o.etapa === 'Em execução' && irrPassProx(o))) throw new Error(id + ' já está ' + o.etapa + ': a janela não muda.');
  if (o.fert) throw new Error(id + ' é fertirrigação (v2): a janela é ajustada pelo agrônomo na O.S.');
  let i = 0; const ps = o.passadas.filter(p => p.st === 'Programada');
  ps.forEach(p => { const q = inis[i++]; if (q === null || q === undefined || isNaN(q)) throw new Error('Informe data e hora da passada ' + p.n + '.'); if (q < s.agora) throw new Error('A passada ' + p.n + ' começa antes de agora (' + irrQuando(s.agora) + ').'); p.ini = q; });
  const oe = irrOrdemErro(o); if (oe) throw new Error(oe);
  const ck = irrChecar(s, o);
  irrTr(o, s.agora, o.lib || o.au, 'Janela definida · ' + irrJanO(o), s.faz[o.faz].irrig);
  const lib = irrProntidao(s, o);
  if (o.etapa === 'A liberar') return { msg: 'Janela salva · ' + id + ' segue A liberar: ' + ck.bloq.map(b => b.t + (b.h ? ' ' + b.h : '')).join(', ') + '.' };
  return { msg: lib || ('Janela salva · ' + id + ' ' + irrJanO(o) + '.') };
}
function irrIniciar(s, id) {
  const o = irrO(s, id); if (o.fert) throw new Error(id + ' v2 aguarda a liberação do agrônomo na O.S.');
  if (o.etapa === 'A liberar') throw new Error(id + ' ainda não está pronta: ' + irrChecar(s, o).bloq.map(b => b.t).join(', ') + '.');
  if (irrPassAtual(o)) throw new Error('A passada ' + irrPassAtual(o).n + ' já está em execução.');
  if (irrPausada(o)) throw new Error('Retome a irrigação antes.');
  const p = irrPassProx(o); if (!p || ['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) throw new Error(id + ' está ' + o.etapa + '.');
  if (p.ini === null) throw new Error('Defina a janela da passada ' + p.n + '.');
  p.st = 'Em execução'; p.iniReal = p.ini + 2; p.cob = 0; o.etapa = 'Em execução'; if (!o.ex) o.ex = irrNovoId(s, 'ex'); if (o.exec.ini === undefined) o.exec.ini = p.iniReal;
  irrTr(o, p.iniReal, o.ex, 'Início' + (o.passadas.length > 1 ? ' da passada ' + p.n : '') + ' · telemetria da ' + s.setores[o.setor].bnome + ' ativa', s.faz[o.faz].irrig);
  return { msg: id + ' Em execução · início ' + irrQuando(p.iniReal) + ' (' + o.ex + ') · término previsto ' + irrQuando(irrFimP(o, p)) + '.' };
}
function irrUlt(o) { return o.trilha.reduce((q, t) => Math.max(q, t.q), -1e9); }
function irrPausar(s, id) {
  const o = irrO(s, id); const p = irrPassAtual(o); if (o.etapa !== 'Em execução' || !p) throw new Error('Só pausa uma passada em execução.');
  if (irrPausada(o)) throw new Error('A irrigação já está pausada.');
  const q = irrUlt(o) + 60; o.exec.pausas.push({ n: p.n, ini: q, fim: null }); irrTr(o, q, o.ex, 'Pausa · selo Pausada · etapa preservada', s.faz[o.faz].irrig);
  return { msg: 'Pausada às ' + irrHm(q) + ' · a etapa continua Em execução.' };
}
function irrRetomar(s, id) {
  const o = irrO(s, id); const pz = (o.exec.pausas || []).find(z => z.fim === null || z.fim === undefined); if (!pz) throw new Error('A irrigação não está pausada.');
  pz.fim = pz.ini + 8; irrTr(o, pz.fim, o.ex, 'Retomada', s.faz[o.faz].irrig); const p = irrPassAtual(o);
  return { msg: 'Retomada às ' + irrHm(pz.fim) + ' · término previsto ' + irrQuando(irrFimP(o, p)) + '.' };
}
function irrAvanco(s, id, cob) {
  const o = irrO(s, id); const p = irrPassAtual(o); const x = s.setores[o.setor]; if (!p) throw new Error('Nenhuma passada em execução.');
  cob = irr2(cob);   // 2 casas, antes de validar (PRE-REV Z4/Y4)
  if (!(cob >= 0) || cob > x.ha) throw new Error('Informe a área coberta entre 0 e ' + irrN(x.ha, 2, 0) + ' ha.');
  p.cob = cob; const q = irrUlt(o) + 30; const tr = o.trilha.find(t => t.av === p.n);   // 2 casas (PRE-REV Z4)
  const ev = 'Avanço da passada ' + p.n + ' · ' + irrN(cob, 2, 0) + ' de ' + irrN(x.ha, 2, 0) + ' ha (' + irrN(cob / x.ha * 100, 0) + ' %)';
  if (tr) { tr.ev = ev; tr.q = q; } else { o.trilha.push({ q, rec: o.ex, ev, quem: s.faz[o.faz].irrig, av: p.n }); }   // telemetria e manual do mesmo evento: um registro
  return { msg: ev + ' · mesmo registro da telemetria, sem duplicar.' };
}
function irrTele(s, o, p, cob) { if (o.tele && cob >= s.setores[o.setor].ha - 1e-9 && o.passadas.length === 1) return o.tele; return Math.round(p.lam * cob * 10 * 0.985 / 10) * 10; }
function irrCredito(s, o, p) {
  const x = s.setores[o.setor]; const ap = x.bal.ap; const i = ap.findIndex(a => a.os === o.id && a.n === p.n);
  if (p.vol === null || p.vol === undefined || !(p.cob > 0)) { if (i >= 0) ap.splice(i, 1); return; }
  const e = { q: irrFimP(o, p), os: o.id, n: p.n, vol: p.vol, ha: x.ha, ef: o.ef || x.efic, cob: p.cob, txt: p.st === 'Parcial' ? 'passagem parcial' : (x.tipo === 'gotejo' ? 'turno completo' : 'volta completa'), prov: true };
  if (i >= 0) ap[i] = e; else ap.push(e);   // um crédito por passada: telemetria e registro manual não duplicam
}
function irrTerminar(s, id, cob, vol) {
  const o = irrO(s, id); const p = irrPassAtual(o); const x = s.setores[o.setor];
  if (!p) throw new Error(o.etapa === 'Liberadas' ? 'Nada foi executado ainda: inicie a irrigação.' : 'Nenhuma passada em execução.');
  if (irrPausada(o)) throw new Error('Retome a irrigação antes de confirmar o término.');
  if (o.fert && o.fert.exec) throw new Error('Saldo parado pela v2: aguarde o agrônomo liberar na O.S.');
  cob = irr2(cob);   // 2 casas, antes de validar (PRE-REV Z4/Y4)
  if (!(cob > 0) || cob > x.ha + 1e-9) throw new Error('Área coberta entre 0 e ' + irrN(x.ha, 2, 0) + ' ha.');
  if (vol !== null && vol !== undefined && !(vol >= 0)) throw new Error('Leitura do hidrômetro inválida.');
  const parc = cob < x.ha - 1e-9; p.cob = cob; p.st = parc ? 'Parcial' : 'Feita';   // 2 casas (PRE-REV Z4)
  p.fimReal = p.iniReal + Math.round(p.dur * cob / x.ha) + irrPausaMin(o, p.n); p.vol = (vol === null || vol === undefined || vol === '') ? null : vol;
  irrCredito(s, o, p);
  irrTr(o, p.fimReal, o.ex, 'Término' + (o.passadas.length > 1 ? ' da passada ' + p.n : '') + ' · ' + irrH(p.fimReal - p.iniReal) + ' de bombeamento · ' + (parc ? 'parou antes: ' + irrN(cob, 2, 0) + ' de ' + irrN(x.ha, 2, 0) + ' ha' : (x.tipo === 'gotejo' ? 'turno completo' : 'volta completa') + ' nos ' + irrN(x.ha, 2, 0) + ' ha') + (p.vol === null ? ' · sem leitura do hidrômetro' : ' · hidrômetro ' + irrN(p.vol) + ' m³'), s.faz[o.faz].irrig);
  const prox = irrPassProx(o);
  if (prox) return { msg: 'Passada ' + p.n + ' encerrada · ' + id + ' segue Em execução · próxima passada ' + (prox.ini === null ? 'a definir' : irrQuando(prox.ini)) + '.' };
  o.etapa = 'Em conferência'; o.exec.fim = p.fimReal;
  return { msg: irrConfAuto(s, o) };
}
function irrConfAuto(s, o) {
  const ps = o.passadas.filter(p => p.st === 'Feita' || p.st === 'Parcial'); const x = s.setores[o.setor];
  const med = ps.some(p => p.vol === null || p.vol === undefined) ? null : ps.reduce((q, p) => q + p.vol, 0);
  const est = ps.reduce((q, p) => q + p.lam * p.cob * 10, 0); const q0 = o.exec.fim + 1;
  if (med === null) { o.conf = { med: null, est: Math.round(est), st: 'Sem leitura' };
    irrTr(o, q0, o.ex, 'Em conferência · sem leitura do hidrômetro: nada é creditado no balanço até a leitura', 'sistema');
    return o.id + ' Em conferência · sem leitura do hidrômetro: informe a leitura (o balanço não assume zero nem o previsto).'; }
  const dv = est ? (med - est) / est * 100 : 0; o.conf = { med, est: Math.round(est), dv, st: Math.abs(dv) <= s.tol + 1e-9 ? 'Automática' : 'Divergência' };
  if (o.conf.st === 'Automática') { o.etapa = 'Encerradas'; o.conf.q = q0; x.bal.ap.filter(a => a.os === o.id).forEach(a => { a.prov = false; });
    irrTr(o, q0, o.ex, 'Conferência automática · ' + irrN(med) + ' m³ medidos × ' + irrN(est) + ' m³ estimados (' + irrPct(dv) + ') · encerrada · balanço creditado uma vez', 'sistema');
    return o.id + ' conferida e encerrada · ' + irrN(med) + ' m³ = ' + irrLamTxt(med, irrCobO(o), x.ha) + ' (' + irrPct(dv) + ', tolerância ' + s.tol + ' %) · ' + irrDefTxt(s, o.setor, 'agora ') + '.'; }
  irrTr(o, q0, o.ex, 'Conferência: ' + irrN(med) + ' m³ medidos × ' + irrN(est) + ' m³ estimados (' + irrPct(dv) + ') · acima da tolerância de ' + s.tol + ' %', 'sistema');
  return o.id + ' Em conferência · divergência de ' + irrPct(dv) + ' entre hidrômetro e estimativa: confira a medição.';
}
// conferir medição / informar leitura: o hidrômetro validado prevalece
function irrConferir(s, id, vol) {
  const o = irrO(s, id); if (o.etapa !== 'Em conferência') throw new Error(id + ' não está Em conferência.'); const x = s.setores[o.setor];
  const ps = o.passadas.filter(p => p.st === 'Feita' || p.st === 'Parcial');
  if (vol !== null && vol !== undefined) { if (!(vol > 0)) throw new Error('Informe a leitura do hidrômetro em m³ (ex.: 8.480).');
    const est = ps.map(p => p.lam * p.cob * 10); const te = est.reduce((a, b) => a + b, 0) || 1; ps.forEach((p, i) => { p.vol = Math.round(vol * est[i] / te); irrCredito(s, o, p); }); }
  const med = ps.some(p => p.vol === null || p.vol === undefined) ? null : ps.reduce((q, p) => q + p.vol, 0);
  if (med === null) throw new Error('Sem leitura do hidrômetro: informe o volume medido.');
  const est = ps.reduce((q, p) => q + p.lam * p.cob * 10, 0); const dv = est ? (med - est) / est * 100 : 0;
  o.etapa = 'Encerradas'; o.conf = { med, est: Math.round(est), dv, st: 'Hidrômetro prevaleceu', q: s.agora }; x.bal.ap.filter(a => a.os === o.id).forEach(a => { a.prov = false; });
  irrTr(o, s.agora, o.ex, 'Conferida · hidrômetro validado prevalece: ' + irrN(med) + ' m³ = ' + irrLamTxt(med, irrCobO(o), x.ha) + ' (' + irrPct(dv) + ' da estimativa) · encerrada', s.faz[o.faz].irrig);
  return { msg: id + ' encerrada · hidrômetro prevalece: ' + irrN(med) + ' m³ · balanço usa o medido, sem duplicar · ' + irrDefTxt(s, o.setor) + '.' };
}
function irrLimites(s, sid, v) {
  const x = s.setores[sid]; if (!x) throw new Error('Setor não encontrado.');
  if (!(v.lmax >= 1 && v.lmax <= 40)) throw new Error('Lâmina máxima por passada entre 1 e 40 mm.');
  if (!(v.imin >= 6 && v.imin <= 96)) throw new Error('Intervalo mínimo entre 6 e 96 h.');
  if (!(v.efic >= 50 && v.efic <= 100)) throw new Error('Eficiência entre 50 e 100 %.');
  x.lmax = v.lmax; x.imin = v.imin; x.efic = v.efic; const n = irrNec(s, sid);
  const lib = irrOrdensSetor(s, sid).filter(o => ['Liberadas', 'Em execução'].indexOf(o.etapa) >= 0).map(o => o.id);
  return { msg: 'Limites do ' + x.nome + ' salvos · a próxima programação usa até ' + irrMm(v.lmax) + ' mm por passada' + (n && n.liq > 0.05 ? ' (necessidade de hoje = ' + n.np + (n.np > 1 ? ' passadas' : ' passada') + ')' : '') + (lib.length ? ' · ' + lib.join(', ') + ' não ' + (lib.length > 1 ? 'mudam' : 'muda') : '') + '.' };
}
function irrSondaMarcar(s, fid, st, motivo) {
  const f = s.fontes[fid]; if (!f) throw new Error('Fonte não encontrada.'); if (f.ro) throw new Error(f.nome + ' não entra no balanço.');
  if (st === 'Suspeita') { if (f.st !== 'Ativa') throw new Error(f.nome + ' já está ' + f.st + '.'); f.st = 'Suspeita'; f.motivo = motivo || 'marcada na conferência'; f.desde = s.agora; }
  else { f.st = 'Ativa'; delete f.motivo; delete f.desde; }
  const x = f.setor ? s.setores[f.setor] : null;
  return { msg: f.nome + ' ' + (st === 'Suspeita' ? 'marcada como suspeita · fora do balanço até a inspeção' + (x ? ' · ' + x.nome + ' passa a estimativa por ET em todas as telas' : '') : 'validada · ' + (x ? x.nome + ' volta a usar a medição' : 'volta ao balanço')) + '.' };
}
function irrCalibrar(s, fid, iso) { const f = s.fontes[fid]; if (!f) throw new Error('Fonte não encontrada.'); if (irrDeIso(iso) === null) throw new Error('Informe a data da calibração.'); f.cal = iso; f.calAg = true; return { msg: 'Calibração de ' + f.nome + ' agendada para ' + irrDdmm(irrDeIso(iso)) + ' · troca ou reset exige leituras de fechamento e abertura.' }; }
function irrFonteNova(s, d) { if (!String(d.nome || '').trim()) throw new Error('Informe o nome do sensor.'); const id = 'F-' + (Object.keys(s.fontes).length + 1);
  s.fontes[id] = { faz: d.faz, nome: d.nome.trim(), gr: d.gr, un: d.un, at: null, cal: d.cal || '', cob: d.cob, st: 'Aguardando 1ª leitura', novo: true };
  return { id, msg: 'Sensor cadastrado · aguardando a primeira leitura validada · nada entra no balanço sem origem.' }; }
// Adicionar produtos: v2 da mesma ordem (fertirrigação), liberada pelo agrônomo na O.S.; a área já irrigada fica na v1
function irrReclassificar(s, id, d) {
  const o = irrO(s, id); if (o.fert) throw new Error(id + ' já tem a v2 com o agrônomo.');
  if (['Em conferência', 'Encerradas', 'Canceladas'].indexOf(o.etapa) >= 0) throw new Error('A execução terminou: programe uma nova fertirrigação na O.S.');
  if (!(d.dose > 0) || d.dose > 50) throw new Error('Dose entre 0 e 50 kg/ha.'); if (!String(d.mot || '').trim()) throw new Error('Informe o motivo agronômico.');
  const x = s.setores[o.setor]; const iniciou = o.etapa === 'Em execução'; const p = irrPassAtual(o);
  // antes de partir (ou entre passadas), a janela do saldo precisa estar pronta: bomba, parada do PCM e outorga valem também para a v2
  if (!p) { const ck = irrChecar(s, o); if (ck.bloq.length) throw new Error('Resolva antes de adicionar produtos: ' + ck.bloq.map(b => b.t + (b.h ? ' ' + b.h : '')).join(', ') + '.'); }
  if (irrPausada(o)) { const pz = o.exec.pausas.find(z => z.fim === null || z.fim === undefined); pz.fim = pz.ini + 8; }
  const q = iniciou ? irrUlt(o) + 30 : s.agora; let v1 = 0, area = x.ha, vol = 0, sw = null;
  if (p) {   // a passada em curso para na área já coberta: essa água fica na v1 (crédito só na faixa); o saldo vai para a v2
    v1 = Math.min(x.ha, p.cob || 0); area = irrAreaV2(x, p); const fim0 = irrFimP(o, p);
    p.st = 'Parcial'; p.cob = v1; p.fimReal = q; p.vol = v1 > 0 ? irrTele(s, o, p, v1) : 0; irrCredito(s, o, p);
    vol += area * p.lam * 10; sw = { ini: q, fim: Math.max(q + 15, fim0) }; }
  o.passadas.filter(z => z.st === 'Programada').forEach(z => { vol += x.ha * z.lam * 10; });
  { const m = irrV2Zero(o, x, p, d.dose); if (m) throw new Error(m); }   // nunca seria liberada nem entregue (PRE-REV Y1)
  o.fert = { prod: d.prod, dose: d.dose, mot: d.mot, exec: iniciou, q, area, v1, vol: Math.round(vol), lamHa: area > 0 ? vol / (10 * area) : 0, tot: cenQtd(d.dose, area), sw };   // regra única de quantidade (cenario.js, sempre carregado antes)
  o.versao = 'v2';
  if (!iniciou) { if (o.lib) { o.libRes = o.lib; irrTr(o, q, o.lib, 'Liberação da água revogada: com produto, a liberação é do agrônomo', 'sistema'); } o.lib = null; o.etapa = 'A liberar'; }
  irrTr(o, q, 'RC-' + id.slice(3) + '-2', 'Versão v2 · ' + d.prod + ' ' + irrN(d.dose, 3, 1) + ' kg/ha · ' + d.mot + ' · ' + (iniciou ? (p ? 'passada ' + p.n + ' parada em ' + irrN(v1, 2, 0) + ' de ' + irrN(x.ha, 2, 0) + ' ha (fica na v1); saldo de ' + irrN(area, 2, 0) + ' ha' : 'passadas seguintes') + ' aguardam a liberação' : 'voltou a A liberar') + ' · requisição de ' + irrN(o.fert.tot, 2) + ' kg na liberação', s.faz[o.faz].gestor);
  return { msg: id + ' v2 criada (' + d.prod + ' ' + irrN(d.dose, 3, 1) + ' kg/ha) · para o agrônomo liberar na O.S. · ' + (iniciou ? 'segue Em execução com selo Revisão de saldo pendente' + (p ? ' · ' + irrN(v1, 2, 0) + ' ha já irrigados ficam na v1' : '') : 'voltou a A liberar') + ' · requisição de ' + irrN(o.fert.tot, 2) + ' kg na liberação.' };
}
// Adicionar produtos de uma vez: v2 na irrigação e no cenário da O.S.; se um lado falhar, nada é gravado
function irrReclassTudo(self, id, d) {
  const s = irrClone(irrGet()); let r;
  try { r = irrReclassificar(s, id, d); } catch (e) { r = { erro: String(e.message || e) }; }
  if (!r.erro && typeof cenMudar === 'function') { const rc = cenMudar(null, c => irrReclassCen(c, s, id)); if (rc.erro) r = { erro: rc.erro }; }
  if (r.erro) { if (self) self.setState({ g2toast: r.erro }); return r; }
  s.ordens[id].fert.cen = true; s.cenRev = irrCenRev(); s.rev = (s.rev || 0) + 1; irrSave(s);
  if (self) self.setState({ irrrev: s.rev, g2toast: r.msg || '' }); return r;
}
// a mesma v2 no cenário da O.S. (forma osc.novo): o agrônomo libera em OS.dc.html, com reserva de estoque
function irrReclassCen(c, s, id) {
  const o = s.ordens[id]; const x = s.setores[o.setor]; const f = o.fert; if (!f) throw new Error('Sem v2.');
  if (c.ordens[id]) throw new Error(id + ' já está no cenário da O.S.');
  const ins = [{ g: 'Fertilizantes', p: f.prod, dose: f.dose, un: 'kg', tot: cenQtd(f.dose, f.area), sit: 'Reserva ao liberar' }];
  const no = { id, novo: false, keys: [], tipo: 'Fertirrigação · ' + f.prod + ' (v2 da irrigação)', talhao: o.setor, area: f.area, etapa: 'A liberar', selos: f.exec ? [{ t: 'Revisão de saldo pendente', c: 'yellow' }] : [],
    faz: x.faz === 'LG' ? 'Lagoa Grande' : 'Santa Rita', saf: '2026/27', lam: irrMm(o.lam) + ' mm', obs: f.mot, agua: false, ins, semins: '', bloq: null, aviso: '', dono: 'Ana (agrônoma)', prazo: 'liberar',
    atv: { op: 'Fertirrigação', nome: 'Fertirrigação · ' + f.prod, gat: '', orig: 'Irrigação ' + id + ' v1 → v2', conj: x.bnome, rend: 0 },
    realizado: 0, saldo: f.area, resp: s.faz[x.faz].irrig, versao: 'v2', janela: irrJanO(o), ap: [], nota: '',
    cond: 'Produto na água: o agrônomo confere, ajusta se precisar e libera; a liberação reserva o estoque. Próximo passo: liberar para execução.',
    orig: ['Irrigação ' + id + ' (água) · ' + x.nome, 'Adicionar produtos · ' + f.mot, f.exec ? irrN(f.v1, 2, 0) + ' ha já irrigados ficam na v1' : 'antes do início'], link: 'IR-03det.dc.html#' + id };
  c.ordens[id] = { id, tipo: no.tipo, talhao: no.talhao, area: f.area, etapa: 'A liberar', versao: 'v2', realizado: 0, saldo: f.area, resp: no.resp,
    ins: ins.map(z => ({ p: z.p, dose: z.dose, un: z.un, tot: z.tot, emb: '' })), req: null, selos: no.selos, ap: [], reservado: false, osc: { novo: no } };
  return { msg: '' };
}

// ---------- leitura para as telas ----------
const IRR_COR = { 'A liberar': 'gray', 'Liberadas': 'green', 'Em execução': 'green', 'Em conferência': 'yellow', 'Encerradas': 'gray', 'Canceladas': 'gray' };
function irrEtapa(s, o) { return irrEt(o); }
// selos (condição) da ordem: bloqueios e situação; avisos à parte
function irrSelos(s, o) {
  const out = []; const et = irrEtapa(s, o);
  if (o.fert) { const et2 = irrFertEtapa(o.id);
    if (!et2 || et2 === 'A liberar') { const fb = irrFertBloq(o.id); if (fb) out.push({ t: fb.t, c: 'red', dono: fb.dono });
      out.push({ t: o.fert.exec ? 'Revisão de saldo pendente · v2' : 'Liberação do agrônomo · v2', c: 'yellow' }); }
    return out; }
  if (et === 'A liberar') irrChecar(s, o).bloq.forEach(b => out.push({ t: b.t, c: b.c, h: b.h, dono: b.dono }));
  if (et === 'Em execução') { if (irrPausada(o)) out.push({ t: 'Pausada', c: 'yellow' }); else if (!irrPassAtual(o) && irrPassProx(o)) out.push({ t: 'Entre passadas', c: 'gray' }); }
  if (et === 'Em conferência' && o.conf) { if (o.conf.st === 'Sem leitura') out.push({ t: 'Sem leitura do hidrômetro', c: 'yellow' }); else if (o.conf.st === 'Divergência') out.push({ t: 'Divergência · ' + irrPct(o.conf.dv !== undefined ? o.conf.dv : (o.conf.med - o.conf.est) / o.conf.est * 100), c: 'yellow' }); }
  if (et === 'Encerradas' && o.conf) out.push({ t: o.conf.st === 'Automática' ? 'Encerrada automaticamente' : 'Hidrômetro prevaleceu', c: 'gray', mut: true });
  return out;
}
function irrAvisos(s, o) { return irrAberta(o) && !o.fert ? irrChecar(s, o).av : []; }
// próximo passo da ordem (verbo + destino + dono); rank = urgência (1 maior). A v2 segue os passos da O.S. (mesmo verbo e dono de lá)
function irrProx(s, o) {
  const F = s.faz[o.faz]; const det = 'IR-03det.dc.html#' + o.id; const et = irrEtapa(s, o);
  if (o.fert) { const et2 = irrFertEtapa(o.id); const resp = irrFertResp(o.id) || F.irrig;
    if (!et2 || et2 === 'A liberar') { const fb = irrFertBloq(o.id); if (fb) return { t: fb.passo, h: fb.h, dono: fb.dono, r: 1 };
      return { t: o.fert.exec ? 'Liberar saldo na O.S.' : 'Liberar na O.S.', h: 'OS.dc.html#' + o.id, dono: 'Ana (agrônoma)', r: 3 }; }
    const P = { 'Liberadas': ['Iniciar execução na O.S.', 5], 'Em execução': ['Registrar apontamento na O.S.', 4], 'Em conferência': ['Conferir e encerrar na O.S.', 4] }[et2];
    return P ? { t: P[0], h: 'OS.dc.html#' + o.id, dono: resp, r: P[1] } : null; }
  if (et === 'A liberar') { const b = irrChecar(s, o).bloq; const red = b.find(z => z.c === 'red');
    if (red) { if (red.k === 'outorga' || red.k === 'vazao') return { t: 'Ajustar à outorga', h: det + ':conflito', dono: red.dono, r: 1 }; return { t: 'Resolver conflito', h: det + ':conflito', dono: red.dono, r: 1 }; }
    return { t: 'Definir janela', h: det + ':janela', dono: F.irrig, r: 3 }; }
  if (et === 'Liberadas') return { t: 'Iniciar irrigação', h: det, dono: F.irrig, r: 5 };
  if (et === 'Em execução') { if (irrPausada(o)) return { t: 'Retomar irrigação', h: det, dono: F.irrig, r: 4 }; if (irrPassAtual(o)) return { t: 'Confirmar término', h: det + ':termino', dono: F.irrig, r: 4 };
    return { t: 'Iniciar passada ' + irrPassProx(o).n, h: det, dono: F.irrig, r: 5 }; }
  if (et === 'Em conferência') { if (o.conf && o.conf.st === 'Sem leitura') return { t: 'Informar leitura', h: det + ':conferir', dono: F.irrig, r: 2 }; return { t: 'Conferir medição', h: det + ':conferir', dono: F.irrig, r: 2 }; }
  return null;
}
// ações da IR-03det que valem no estado da ordem (links diretos #OS-xxxx:acao só abrem o painel quando valem)
function irrAcaoVale(s, o, ac) {
  if (!o) return 'Ordem não encontrada.'; const et = irrEtapa(s, o);
  if (ac === 'janela') { if (o.fert) return o.id + ' é fertirrigação (v2): a janela fica com o agrônomo na O.S.';
    if (!(['A liberar', 'Liberadas'].indexOf(o.etapa) >= 0 || (o.etapa === 'Em execução' && irrPassProx(o) && !irrPassAtual(o))) || !o.passadas.some(p => p.st === 'Programada')) return 'Definir janela não vale: ' + o.id + ' está ' + et + '.'; return ''; }
  if (ac === 'conflito') { if (o.fert || o.etapa !== 'A liberar' || !irrChecar(s, o).bloq.some(b => b.c === 'red')) return o.id + ' não tem conflito a resolver (' + et + ').'; return ''; }
  if (ac === 'termino') { if (o.fert || !irrPassAtual(o) || irrPausada(o)) return 'Confirmar término não vale: ' + o.id + ' ' + (irrPausada(o) ? 'está pausada.' : 'não tem passada em execução.'); return ''; }
  if (ac === 'conferir') { if (o.fert || o.etapa !== 'Em conferência') return 'Conferir medição não vale: ' + o.id + ' está ' + et + '.'; return ''; }
  return 'Ação desconhecida.';
}
// quanto a ordem cobre da necessidade do setor (ordens abertas em ordem de início; líquida = bruta × eficiência)
function irrCobre(s, o) {
  const x = s.setores[o.setor]; const d = irrDef(s, o.setor); if (d === null) return null; let rest = d; let res = null; let i = 0;
  irrOrdensSetor(s, o.setor).filter(z => irrAberta(z) && irrEt(z) !== 'Em conferência').forEach(z => {
    const liq = (z.fert ? z.fert.lamHa : z.passadas.filter(p => p.st === 'Programada' || p.st === 'Em execução').reduce((q, p) => q + p.lam, 0)) * (z.ef || x.efic) / 100;   // v2: lâmina por ha do saldo
    if (z.id === o.id) res = { liq, cob: (i === 0 && rest > 0.05) ? Math.min(100, liq / rest * 100) : null, resta: Math.max(0, rest - liq), prox: i > 0 };
    rest = Math.max(0, rest - liq); i++; });
  return res;
}
// situação da ordem no setor (mapa, IR-01): cor da camada, rótulo curto e situação
function irrSitOrdem(s, o, p, et) {
  if (p && p.r === 1) { const sel = irrSelos(s, o); if (o.fert) { const fb = irrFertBloq(o.id) || { t: '' }; return { c: 'red', sit: 'Impedida', l: (/^Falta insumo/.test(fb.t) ? 'falta insumo · ' : 'v2 parada · ') + o.id }; }
    return { c: 'red', sit: 'Impedida', l: sel[0] ? sel[0].t.replace(/^Conflito · /, 'conflito · ') : 'conflito' }; }
  if (o.fert) { const et2 = irrFertEtapa(o.id);
    if (!et2 || et2 === 'A liberar') return { c: 'yellow', sit: 'A liberar', l: (o.fert.exec ? 'saldo a liberar · ' : 'fertirrigação a liberar · ') + o.id };
    if (et2 === 'Em execução') return { c: 'blue', sit: 'Irrigando', l: 'fertirrigando · ' + o.id };
    return { c: 'lime', sit: 'Programada', l: (et2 === 'Liberadas' ? 'fertirrigação liberada · ' : 'fertirrigação em conferência · ') + o.id }; }
  if (et === 'Em conferência') return { c: 'yellow', sit: 'A conferir', l: 'conferir medição · ' + o.id };
  if (et === 'A liberar') return { c: 'yellow', sit: 'A programar', l: 'janela a definir · ' + o.id };
  if (et === 'Em execução') return { c: irrPausada(o) ? 'yellow' : 'blue', sit: 'Irrigando', l: (irrPausada(o) ? 'pausada · ' : 'irrigando · ') + o.id };
  const q = irrIni(o); return { c: 'lime', sit: 'Programada', l: 'programada · ' + (q === null ? o.id : irrQuando((irrPassProx(o) || {}).ini || q)) };
}
// situação do setor (mapa, IR-01 e faixa): c = cor da camada do mapa · l = rótulo · acao = [verbo, destino] · dono = de quem é o passo
function irrSituacao(s, sid) {
  const x = s.setores[sid]; const F = s.faz[x.faz];
  if (!x.bal) return { c: 'gray', l: x.faz === 'LG' ? 'preparo · sem rega' : 'sequeiro', sit: 'Sem irrigação', d: null, est: false, hoje: '', acao: null, dono: '', ords: [] };
  const d = irrDef(s, sid); const est = irrEst(s, x); const n = irrNec(s, sid); const cp = s.capt[x.capt];
  const ords = irrOrdensSetor(s, sid); const ab = ords.filter(irrAberta);
  const fe = Object.keys(s.fert).filter(k => s.fert[k].setor === sid && !s.ordens[k]).map(k => ({ id: k, f: s.fert[k], et: irrFertEtapa(k) })).filter(z => z.et && ['Encerradas', 'Canceladas'].indexOf(z.et) < 0);
  const lim = x.limiar; const precisa = lim !== null && lim !== undefined && d >= lim;
  const aguaAb = ab.some(o => !o.fert);
  const it = [];
  ab.forEach(o => { const p = irrProx(s, o); const et = irrEtapa(s, o); const sel = irrSelos(s, o); const so = irrSitOrdem(s, o, p, et);
    it.push({ r: p ? p.r : 6, c: so.c, l: so.l, sit: so.sit, o, acao: p ? [p.t, p.h] : null, dono: p ? p.dono : '', hoje: o.id + ' · ' + (sel.length ? sel.map(z => z.t).join(' · ') + ' · ' : '') + et + (irrJanO(o) !== 'a definir' ? ' · ' + irrJanO(o) : '') + (p && p.dono ? ' · ' + p.t.toLowerCase() + ': ' + p.dono : '') }); });
  fe.forEach(z => { const fb = irrFertBloq(z.id); const resp = irrFertResp(z.id) || F.irrig; let r, c, l, sit, acao, dono;
    if (fb) { r = 1; c = 'red'; sit = 'Impedida'; l = (/^Falta insumo/.test(fb.t) ? 'falta insumo · ' : 'bomba parada · ') + z.id;
      if (precisa && !aguaAb && !/^Impedida/.test(fb.t)) { acao = ['Programar só água', 'IR-02.dc.html#programar=' + sid]; dono = F.irrig; } else { acao = [fb.passo, fb.h]; dono = fb.dono; } }
    else if (z.et === 'A liberar') { r = 3; c = 'yellow'; l = 'fertirrigação a liberar · ' + z.id; sit = 'A liberar'; acao = ['Liberar fertirrigação', 'OS.dc.html#' + z.id]; dono = 'Ana (agrônoma)'; }
    else { r = 5; c = z.et === 'Em execução' ? 'blue' : 'lime'; sit = z.et === 'Em execução' ? 'Irrigando' : 'Programada'; l = (z.et === 'Em conferência' ? 'fertirrigação em conferência · ' : 'fertirrigação · ') + z.id; acao = ['Abrir ' + z.id, 'OS.dc.html#' + z.id]; dono = resp; }
    it.push({ r, c, l, sit, fert: z.id, acao, dono,
      hoje: z.id + ' · ' + z.f.nome + ' · ' + z.et + (fb ? ' · ' + fb.t + ' · ' + fb.passo.toLowerCase() + ': ' + fb.dono : '') + (fb && acao[0] === 'Programar só água' ? ' · a água pode ir sem o produto' : ' · a fertirrigação leva a água do setor') }); });
  it.sort((a, b) => a.r - b.r);
  const fon = est ? ((irrSonda(s, x) || {}).st === 'Suspeita' ? 'sonda suspeita (' + (irrSonda(s, x).motivo || '') + ') · estimativa por ET' : 'sonda sem dado desde ' + irrQuando(irrSonda(s, x).desde) + ' · estimativa por ET') : (F.demo ? 'balanço demonstrativo · hoje 06:00' : 'estação Santa Rita + sonda · hoje 06:00');
  const aps = irrApsSetor(s, sid); const ultA = aps.slice().sort((a, b) => b.q - a.q)[0]; const fx = irrFaixaCob(s, sid);
  const ult = ultA ? irrDdmm(irrDiaN(ultA.q)) + ' · ' + ultA.os + ' · ' + irrMm(irrApBr(ultA)) + ' mm em ' + (irrApParc(ultA, x.ha) ? irrN(irrApCob(ultA), 2, 1) + ' de ' + irrN(x.ha, 2, 0) + ' ha' : irrN(x.ha, 2, 0) + ' ha') + (ultA.prov ? ' · provisório' : '')
    : (x.bal.repos !== undefined ? irrDdmm(irrDiaN(x.bal.repos)) + ' · reposição completa (há ' + (-irrDiaN(x.bal.repos)) + (irrDiaN(x.bal.repos) === -1 ? ' dia' : ' dias') + ')' : '—');
  const base = { d, est, n, fon, eq: (x.tipo === 'gotejo' ? 'Gotejo' : 'Pivô central') + ' · ' + irrN(x.ha, 2, 0) + ' ha · ' + irrN(x.vazao) + ' L/s · ' + x.bnome + (cp ? ' · ' + cp.nome : ''), ult, ords: ab,
    faixa: fx ? 'faixa de ' + irrN(fx.cob, 2, 1) + ' ha (' + fx.os + '): ' + irrN(fx.d, 1) + ' mm · resto do ' + (x.tipo === 'gotejo' ? 'setor' : 'pivô') + ': ' + irrN(d, 1) + ' mm' : '' };
  if (it.length) { const t = it[0]; const o = (t.o && irrEt(t.o) === 'Em conferência') ? (ab.find(z => irrEt(z) !== 'Em conferência') || null) : t.o; let limt = 'Lâmina programada', lam = '';
    if (o) { lam = irrMm(o.lam) + ' mm' + (o.passadas.length > 1 ? ' em ' + o.passadas.length + ' passadas' : '') + ' · ' + irrJanO(o); const cb = irrCobre(s, o); if (cb && cb.cob !== null) lam += ' · cobre ' + irrN(cb.cob, 0) + ' %' + (cb.resta > 0.05 ? ' · resta ' + irrN(cb.resta, 1) + ' mm' : ''); }
    else if (t.fert) { const f = s.fert[t.fert]; lam = f.lam ? irrMm(f.lam) + ' mm · ' + irrJan(f.ini, f.fim) : (f.ini ? irrJan(f.ini, f.fim) : 'parada'); limt = 'Fertirrigação'; }
    else { limt = 'Necessidade'; lam = n && n.liq > 0.05 ? irrMm(n.br) + ' mm brutos em ' + n.np + (n.np > 1 ? ' passadas' : ' passada') + ' · sem ordem programada' : 'sem lâmina'; }
    return Object.assign(base, { c: t.c, l: t.l, sit: t.sit, hoje: t.hoje, acao: t.acao, dono: t.dono || '', limt, lam, top: t }); }
  const lamN = n && n.liq > 0.05 ? irrMm(n.br) + ' mm brutos em ' + n.np + (n.np > 1 ? ' passadas' : ' passada') : 'sem lâmina';
  if (precisa) return Object.assign(base, { c: 'yellow', l: 'a programar · ' + irrN(d, 1) + ' mm', sit: 'A programar', hoje: 'Déficit de ' + irrN(d, 1) + ' mm passou do limite de ' + irrN(lim, 1) + ' mm: programe a irrigação', acao: ['Programar irrigação', 'IR-02.dc.html#programar=' + sid], dono: F.irrig, limt: 'Necessidade', lam: lamN });
  return Object.assign(base, { c: est ? 'cloud' : 'ok', l: est ? 'sem necessidade · ≈ estimado' : 'sem necessidade hoje', sit: 'Sem necessidade', hoje: 'Déficit de ' + (est ? '≈' : '') + irrN(d, 1) + ' mm abaixo do limite de ' + irrN(lim || 0, 1) + ' mm: sem rega hoje', acao: null, dono: '', limt: 'Irrigar a partir de', lam: irrN(lim || 0, 1) + ' mm de déficit' + (x.fase ? ' (' + x.cult.toLowerCase() + ')' : '') });
}
// contadores da faixa de etapas
function irrContagem(s, fz) {
  const sids = Object.keys(s.setores).filter(k => !fz || s.setores[k].faz === fz); const out = { aprog: 0, conf: 0, jan: 0, confer: 0, sens: 0, sensT: '' };
  sids.forEach(k => { const si = irrSituacao(s, k); if ((si.sit === 'A programar' && !irrOrdensSetor(s, k).some(irrAberta)) || (si.acao && si.acao[0] === 'Programar só água')) out.aprog++; });
  Object.values(s.ordens).filter(o => (!fz || o.faz === fz) && irrAberta(o) && !o.fert).forEach(o => { const p = irrProx(s, o); if (!p) return; if (p.r === 1) out.conf++; else if (p.t === 'Definir janela') out.jan++; else if (p.r === 2) out.confer++; });
  const fs = Object.values(s.fontes).filter(f => (!fz || f.faz === fz) && !f.ro); const su = fs.filter(f => f.st === 'Suspeita').length, sd = fs.filter(f => f.st === 'Sem dado').length;
  out.sens = su + sd; out.sensT = [su ? su + (su > 1 ? ' suspeitas' : ' suspeita') : '', sd ? sd + ' sem dado' : ''].filter(Boolean).join(' · ');
  return out;
}
