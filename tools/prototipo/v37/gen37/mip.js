// ===== Pragas e doenças (MIP/MID): estado compartilhado entre Mapa, AG-01, AG-01det, AG-03/AG-04 e app de campo (MB-06) =====
// MIPD (estático: protocolos, talhões, Agrofit) e MIP0 (semente) vêm de dados_mip.py. Um único estado no navegador ('talhao-os-mip-v1');
// a O.S. de controle vai para o cenário das O.S. (cenario.js, cenMudar) no formato osc.novo, sempre em A liberar.
const MIP_KEY = 'talhao-os-mip-v1';
let MIP_MEM = null;
function mipClone(o) { return JSON.parse(JSON.stringify(o)); }
function mipLoad() { try { const t = localStorage.getItem(MIP_KEY); return t ? JSON.parse(t) : null; } catch (e) { return null; } }
function mipSave(s) { MIP_MEM = s; try { localStorage.setItem(MIP_KEY, JSON.stringify(s)); } catch (e) {} }
function mipGet() { const s = mipLoad() || MIP_MEM; if (s && s.v === MIP0.v) return s; MIP_MEM = mipClone(MIP0); return MIP_MEM; }
function mipReset() { MIP_MEM = mipClone(MIP0); try { localStorage.removeItem(MIP_KEY); } catch (e) {} }
// mudança atômica: aplica fn numa cópia; erro não grava nada
function mipMudar(self, fn) {
  const s = mipClone(mipGet()); let r;
  try { r = fn(s) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (r.erro) { if (self) self.setState({ g2toast: r.erro }); return r; }
  s.rev = (s.rev || 0) + 1; mipSave(s); if (self) self.setState({ miprev: s.rev, g2toast: r.msg || '' }); return r;
}
// outras telas (outras abas ou quadros) redesenham quando o MIP ou o cenário das O.S. mudam
function mipOuvir(self) {
  if (self.__mipOuv) return; self.__mipOuv = true;
  try { window.addEventListener('storage', (e) => { if (e.key === MIP_KEY || e.key === 'talhao-os-cenario-v1') self.setState({ miprev: Date.now() }); }); } catch (e) {}
}
// ---------- datas (iso aaaa-mm-dd) e números pt-BR ----------
function mipDt(iso) { const a = String(iso).split('-').map(Number); return new Date(Date.UTC(a[0], a[1] - 1, a[2])); }
function mipIso(d) { return d.toISOString().slice(0, 10); }
function mipAdd(iso, n) { const d = mipDt(iso); d.setUTCDate(d.getUTCDate() + n); return mipIso(d); }
function mipDif(a, b) { return Math.round((mipDt(b) - mipDt(a)) / 86400000); }
function mipBr(iso) { if (!iso || !/^\d{4}-/.test(iso)) return iso || ''; const a = iso.split('-'); return a[2] + '/' + a[1]; }
function mipBrA(iso) { if (!iso || !/^\d{4}-/.test(iso)) return iso || ''; const a = iso.split('-'); return a[2] + '/' + a[1] + '/' + a[0]; }
function mipN(n, d) { return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: d === undefined ? 1 : d }); }
function mipPct(x) { return Math.round(x * 100 + 1e-7); }
function mipAmanha() { return mipAdd(MIPD.hoje, 1); }
// ---------- protocolo, talhão e cores ----------
function mipP(v) { return MIPD.prot[v.prot]; }
function mipT(v) { return MIPD.tal[v.tal]; }
function mipNC(p, t) { if (p.crit !== 'nc') return null; if (p.ncf) { const f = (t && t.fase) || ''; for (const x of p.ncf) if (f.indexOf(x[0]) === 0) return x[1]; } return p.nc; }
function mipPontos(prot, area) { const p = MIPD.prot[prot]; return Math.max(p.pmin, Math.min(p.pmax, Math.ceil(area / p.ap))); }
function mipCult(t) { return (t.cultura || '').toLowerCase(); }
// cor do chip (G2C) e da camada do mapa por situação
const MIP_SIT = {
  programada: ['Programada', 'gray', 'lime'], coleta: ['Em coleta', 'blue', 'yellow'], sinc: ['Sincronizar', 'yellow', 'yellow'],
  incompleta: ['Coleta incompleta', 'yellow', 'yellow'], acima: ['Acima do NC', 'red', 'red'], foco: ['Foco', 'orange', 'orange'],
  perto: ['Perto do NC', 'yellow', 'yellow'], abaixo: ['Abaixo do NC', 'green', 'ok'], controle: ['Em controle', 'blue', 'blue'],
  pos: ['Avaliar controle', 'yellow', 'blue'], avaliacao: ['Leitura pós', 'blue', 'blue'], encerrada: ['Encerrada', 'gray', 'ok'],
  cancelada: ['O.S. cancelada', 'red', 'red'], atrasada: ['Vistoria atrasada', 'yellow', 'gray'] };
// ordem de atenção: decisão pendente do agrônomo > coleta a resolver > controle a liberar ou avaliar > ritmo atrasado > coleta em andamento > programada > em dia
const MIP_ORD = ['acima', 'foco', 'cancelada', 'sinc', 'incompleta', 'perto', 'pos', 'controle', 'atrasada', 'coleta', 'avaliacao', 'programada', 'abaixo', 'encerrada'];
// O.S. cancelada, ou fora do cenário (demonstração das O.S. restaurada): não conta como aplicação nem como controle
function mipOsFora(c, id) { return !!(id && c && c.ordens && (!c.ordens[id] || c.ordens[id].etapa === 'Canceladas')); }
function mipCen() { return (typeof cenGet === 'function') ? cenGet() : null; }
// aplicações que valem para rotação e nº máximo: sem O.S. (histórico) ou com O.S. não cancelada
function mipApl(s, c) { return s.apl.filter(x => !x.os || !mipOsFora(c, x.os)); }
// vistoria seguinte do mesmo talhão × alvo (a aberta primeiro; senão a mais recente posterior)
function mipSeg(s, v) {
  const vs = Object.values(s.vis).filter(x => x.id !== v.id && x.tal === v.tal && x.prot === v.prot && (x.data > v.data || (x.data === v.data && x.id > v.id)));
  return vs.find(x => x.est !== 'concluida' || (x.pend || []).length) || vs.sort((a, b) => (a.data < b.data ? 1 : -1))[0] || null;
}
// próxima vistoria prevista depois desta (decisão registrada manda; senão, o intervalo do protocolo; perto do NC = 3 dias)
function mipPrevista(v) { const R = mipRes(v); return (v.dec && v.dec.prox) || mipAdd(v.data, R.kr === 'perto' ? 3 : mipP(v).inter); }
// ponto a coletar no app: o primeiro sem contagem; depois, os de recoleta (GPS fora da tolerância)
function mipAlvoPt(v) { return v.pts.find(x => x.v === null || x.v === undefined) || v.pts.find(x => x.rec) || null; }
// o app coleta enquanto não houver decisão nem pacote pendente no aparelho; vistoria concluída com falta ou recoleta reabre
function mipColetavel(v) { return !v.dec && !(v.pend || []).length && !!mipAlvoPt(v); }
// contagem válida para o protocolo: número ≥ 0; percentual até 100; presença em plantas inteiras
function mipValor(p, valor, n) {
  const x = Number(String(valor === null || valor === undefined ? '' : valor).replace(',', '.'));
  if (String(valor === null || valor === undefined ? '' : valor).trim() === '' || isNaN(x) || x < 0) throw new Error('Informe a contagem do ponto ' + n + '.');
  if (/%/.test(p.un) && x > 100) throw new Error('Ponto ' + n + ': ' + mipN(x) + ' passa de 100 (' + p.un + ').');
  if (p.crit === 'presenca' && Math.round(x) !== x) throw new Error('Ponto ' + n + ': informe o número de plantas (inteiro).');
  return x;
}
// ---------- resultado da contagem × NC (CAL-12: só pontos válidos; recoleta fica à vista e fora da média) ----------
function mipRes(v, s) {
  const p = mipP(v), t = mipT(v), nc = mipNC(p, t);
  const col = v.pts.filter(x => x.v !== null && x.v !== undefined), val = col.filter(x => x.ok !== false && !x.rec);
  const R = { nc, un: p.un, crit: p.crit, tot: v.npts, col: col.length, val: val.length, rec: col.length - val.length, falt: v.npts - col.length,
    pend: (v.pend || []).length, media: null, pct: null, pres: 0, reb: 0, k: '', kr: '', red: null };
  if (val.length) { R.media = val.reduce((a, x) => a + Number(x.v), 0) / val.length; R.pres = val.filter(x => Number(x.v) > 0).length;
    if (nc) { R.pct = R.media / nc; R.reb = val.filter(x => Number(x.v) >= 2 * nc).length; } }
  // resultado técnico (com o que foi coletado)
  if (p.crit === 'presenca') R.kr = R.val ? (R.pres > 0 ? 'foco' : 'abaixo') : '';
  else if (R.media === null) R.kr = '';
  else if (R.media >= nc) R.kr = 'acima';
  // foco: média abaixo do NC com ≥ 2 pontos de reboleira (≥ 2 × NC); mais reboleiras nunca rebaixam o resultado.
  // Acima de 30 % dos pontos a reboleira é "larga": a decisão sugere controlar o talhão em vez do controle localizado.
  else if (R.reb >= 2) { R.kr = 'foco'; R.larga = R.reb > Math.ceil(0.3 * R.val); }
  else if (R.media >= 0.8 * nc) R.kr = 'perto';
  else R.kr = 'abaixo';
  if (v.est === 'programada') R.k = 'programada';
  else if (R.pend) R.k = 'sinc';
  else if (v.est === 'coleta') R.k = 'coleta';
  else if (R.falt > 0 && !v.parcial) R.k = 'incompleta';
  else R.k = R.kr || 'incompleta';
  // texto da contagem
  if (p.crit === 'presenca') R.txt = R.val ? (R.pres + (R.pres === 1 ? ' ponto' : ' pontos') + ' com sintoma de ' + R.val + ' · critério presença') : '—';
  else R.txt = R.media === null ? '—' : (mipN(R.media) + ' / ' + mipN(nc) + ' ' + p.un + ' · ' + mipPct(R.pct) + ' % do NC');
  R.ctxt = p.crit === 'presenca' ? (R.val ? R.pres + ' de ' + R.val + ' com sintoma' : '—') : (R.media === null ? '—' : mipN(R.media) + ' / ' + mipN(nc));
  R.ptxt = R.col + '/' + R.tot + ' pontos' + (R.rec ? ' · ' + R.rec + ' em recoleta' : '') + (R.pend ? ' · ' + R.pend + ' no aparelho' : '');
  // leitura pós: redução observada = 1 − pós/pré (mesmo método; só com pré > 0)
  if (v.pos_de && s && s.vis[v.pos_de] && R.media !== null) { const pre = mipRes(s.vis[v.pos_de]); if (pre.media > 0) R.red = 1 - R.media / pre.media; }
  return R;
}
// ---------- situação (resultado + decisão + O.S. do cenário) ----------
function mipOsEt(c, id) { const o = c && c.ordens ? c.ordens[id] : null; return o ? o.etapa : ''; }
function mipSit(s, v, c) {
  const R = mipRes(v, s), d = v.dec; let k = R.k, sub = '';
  if (d) {
    if (d.t === 'monitorar') { k = 'encerrada'; sub = 'seguir monitorando' + (d.prox ? ' · próxima ' + mipBr(d.prox) : ''); }
    else if (d.os) { const et = mipOsEt(c, d.os);
      // O.S. cancelada, ou fora do cenário (demonstração das O.S. restaurada): a decisão volta a ficar pendente
      if (mipOsFora(c, d.os)) { k = 'cancelada'; sub = d.os + (et ? '' : ' não encontrada'); }
      else if (et === 'Encerradas') { const pv = d.pos ? s.vis[d.pos] : null;
        if (!pv) { k = 'pos'; sub = d.os + ' encerrada'; }
        else { const rp = mipRes(pv, s); if (pv.est === 'concluida' && !rp.falt) { k = 'encerrada'; sub = rp.red !== null ? 'redução observada ' + Math.round(rp.red * 100) + ' %' : 'leitura pós ' + pv.id; } else { k = 'avaliacao'; sub = pv.id + ' · ' + mipBr(pv.data); } } }
      else { k = 'controle'; sub = d.os + (et ? ' · ' + et : ''); } }
  } else if (k === 'foco') sub = R.crit === 'presenca' ? 'virose · erradicar' : (R.larga ? 'reboleiras em ' + R.reb + ' de ' + R.val + ' pontos' : 'reboleira');
  else if (k === 'perto') sub = mipPct(R.pct) + ' % do NC';
  // ritmo: a última vistoria encerrada do talhão × alvo, sem vistoria seguinte e com a prevista vencida, fica "Vistoria atrasada"
  let seg = null, prev = '';
  if (k === 'encerrada' && v.est === 'concluida') { seg = mipSeg(s, v);
    if (!seg) { prev = mipPrevista(v); if (prev < MIPD.hoje) { k = 'atrasada'; const n = mipDif(prev, MIPD.hoje); sub = 'prevista para ' + mipBr(prev) + ' · ' + n + (n > 1 ? ' dias' : ' dia'); } } }
  const S = MIP_SIT[k] || ['—', 'gray', 'none'];
  return { k, t: S[0], c: S[1], mc: S[2], sub, R, ord: MIP_ORD.indexOf(k), seg, prev };
}
// ---------- ritmo do talhão: próxima vistoria pela última (intervalo do protocolo; perto do NC = 3 dias) ----------
function mipRitmo(s, tal) {
  const vs = Object.values(s.vis).filter(x => x.tal === tal);
  const ab = vs.find(x => x.est !== 'concluida' || (x.pend || []).length);
  const feitas = vs.filter(x => x.est === 'concluida').sort((a, b) => (a.data < b.data ? 1 : -1));
  const ult = feitas[0] || null; if (!ult) return { ult: null, prox: '', atras: 0, aberta: ab ? ab.id : '' };
  // a próxima é a mais cedo entre as vistorias mais recentes de cada alvo (decisão registrada manda; senão, o intervalo do protocolo)
  // por alvo: o alvo com vistoria aberta está em dia; os demais vencem pela prevista da última vistoria deles
  const porAlvo = {}; feitas.forEach(x => { if (!porAlvo[x.prot]) porAlvo[x.prot] = x; });
  let prox = ''; Object.values(porAlvo).forEach(x => { if (mipAberta(s, tal, x.prot)) return; const d = mipPrevista(x); if (!prox || d < prox) prox = d; });
  const atras = (prox && prox < MIPD.hoje) ? mipDif(prox, MIPD.hoje) : 0;
  return { ult, prox, atras, aberta: ab ? ab.id : '' };
}
// ---------- próximo passo (o mesmo no Mapa, no AG-01 e no app) ----------
function mipProx(s, v, c) {
  const S = mipSit(s, v, c), R = S.R, p = mipP(v), t = mipT(v), d = v.dec; const app = 'MB-06.dc.html#' + v.id;
  const P = { t: '', fn: '', h: '', txt: '', sec: null };
  const nxt = v.pts.find(x => x.v === null || x.v === undefined);
  switch (S.k) {
    case 'programada': Object.assign(P, { t: 'Coletar no app', h: app, txt: 'Programada para ' + mipBr(v.data) + ' com ' + v.resp + ' · ' + v.npts + ' pontos · ' + p.met + '.' }); break;
    case 'coleta': Object.assign(P, { t: 'Continuar coleta', h: app, txt: R.col + ' de ' + R.tot + ' pontos coletados' + (nxt ? ' · próximo: ponto ' + nxt.n : '') + (R.media !== null ? ' · parcial ' + R.ctxt + ' ' + p.un : '') + '.' }); break;
    case 'sinc': Object.assign(P, { t: 'Sincronizar agora', fn: 'sinc', txt: R.pend + ' pontos de ' + v.resp + ' estão no aparelho, sem sinal.' }); break;
    case 'incompleta': Object.assign(P, { t: 'Completar coleta', h: app, txt: 'Faltam ' + R.falt + ' de ' + R.tot + ' pontos' + (R.media !== null ? ' · parcial ' + R.txt : '') + ' · o app reabre a coleta no ponto ' + (nxt ? nxt.n : '') + '.',
      sec: R.val ? { t: 'Decidir com ' + R.val + ' de ' + R.tot + ' pontos', fn: 'parcial' } : null }); break;
    case 'acima': Object.assign(P, { t: 'Decidir controle', fn: 'decidir', txt: 'Média ' + R.txt + '. Escolha um produto registrado e emita o receituário: a O.S. nasce em A liberar.' }); break;
    case 'foco': Object.assign(P, { t: 'Confirmar foco', fn: 'decidir', txt: p.id === 'inspecao' ? (R.pres + (R.pres === 1 ? ' ponto' : ' pontos') + ' com sintoma na mancha: registre a causa; se for alvo do protocolo, programe a vistoria dele.')
      : R.crit === 'presenca' ? (R.pres + (R.pres === 1 ? ' ponto' : ' pontos') + ' com sintoma de ' + p.alvo.toLowerCase() + '. ' + (p.sem || '') + '.')
      : ('Média ' + R.txt + ' com ' + R.reb + ' pontos de reboleira (≥ 2 × NC). Controle localizado ou seguir monitorando.') }); break;
    case 'perto': Object.assign(P, { t: 'Seguir monitorando', fn: 'monitorar', txt: 'Média ' + R.txt + '. Revisita em 3 dias.' }); break;
    case 'abaixo': Object.assign(P, { t: 'Seguir monitorando', fn: 'monitorar', txt: (R.crit === 'presenca' ? 'Sem sintoma nos pontos.' : 'Média ' + R.txt + '.') + ' Próxima vistoria no ritmo de ' + p.inter + ' dias; o manejo preventivo do plano continua.' }); break;
    case 'controle': Object.assign(P, { t: 'Abrir ' + d.os, h: 'OS.dc.html#' + d.os, txt: 'Controle em ' + d.os + ' · ' + (mipOsEt(c, d.os) || 'A liberar') + (mipOsEt(c, d.os) === 'A liberar' ? ': Ana libera na O.S.; o estoque é reservado ao liberar.' : '.') }); break;
    case 'pos': Object.assign(P, { t: 'Programar leitura pós', fn: 'pos', txt: d.os + ' encerrada. Leitura pós 7 dias após a aplicação, no mesmo método.' }); break;
    case 'avaliacao': Object.assign(P, { t: 'Abrir ' + d.pos, h: 'AG-01.dc.html#' + d.pos, txt: 'Leitura pós ' + d.pos + ' programada para ' + mipBr(s.vis[d.pos].data) + '.' }); break;
    case 'cancelada': Object.assign(P, { t: 'Decidir controle', fn: 'decidir', txt: d.os + (mipOsEt(c, d.os) ? ' foi cancelada sem execução' : ' não está mais nas O.S.') + ': decida de novo.' }); break;
    case 'atrasada': Object.assign(P, { t: 'Programar vistoria', fn: 'programar', txt: 'Vistoria de ' + p.alvo.toLowerCase() + ' no ' + t.rot + ' prevista para ' + mipBr(S.prev) + ': ' + S.sub.split(' · ').pop() + ' de atraso.' }); break;
    default: { const txt = d ? ('Decisão de ' + mipBr(d.em) + ' por ' + d.por + (d.t === 'monitorar' ? ': seguir monitorando' : '') + '.') : 'Consulta.';
      const red = (S.sub && /redução/.test(S.sub) ? ' Redução observada ' + S.sub.replace('redução observada ', '') + ' (não equivale a eficácia causal).' : '');
      const sg = S.seg;
      if (sg && (sg.est !== 'concluida' || (sg.pend || []).length)) Object.assign(P, { t: 'Abrir ' + sg.id, h: 'AG-01.dc.html#' + sg.id, txt: txt + red + ' Próxima: ' + sg.id + (sg.est === 'programada' ? ' programada para ' + mipBr(sg.data) : ' em coleta') + '.' });
      else if (sg) Object.assign(P, { txt: txt + red + ' Seguida pela ' + sg.id + ' (' + mipBr(sg.data) + ').' });
      else if (S.prev) Object.assign(P, { t: 'Programar vistoria', fn: 'programar', txt: txt + red + ' Próxima vistoria prevista para ' + mipBr(S.prev) + '.' });
      else Object.assign(P, { txt: txt + red }); }
  }
  return Object.assign(P, { S, R });
}
// ---------- programar vistoria (um contador para todas as telas; não duplica talhão × alvo aberto) ----------
function mipProtPadrao(s, tal) {
  const ps = MIPD.prots[tal] || []; if (!ps.length) return '';
  const ult = Object.values(s.vis).filter(x => x.tal === tal && ps.indexOf(x.prot) >= 0).sort((a, b) => (a.data < b.data ? 1 : -1))[0];
  return ult ? ult.prot : ps[0];
}
function mipAberta(s, tal, prot) { return Object.values(s.vis).find(x => x.tal === tal && x.prot === prot && (x.est !== 'concluida' || (x.pend || []).length)) || null; }
function mipNovaVis(s, tal, prot, data, resp, orig, extra) {
  const t = MIPD.tal[tal]; if (!t) throw new Error('Talhão não encontrado.');
  const p = MIPD.prot[prot]; if (!p) throw new Error('Escolha o alvo.');
  if (prot !== 'inspecao' && (MIPD.prots[tal] || []).indexOf(prot) < 0) throw new Error(p.alvo + ' não está no protocolo de ' + (mipCult(t) || 'área sem cultura') + (t.fase ? ' em ' + t.fase : '') + '.');
  if (!data) throw new Error('Informe a data.');
  const ab = mipAberta(s, tal, prot); if (ab) throw new Error(ab.id + ' já está aberta para ' + t.rot + ' × ' + p.alvo.toLowerCase() + '.');
  let n = s.seq.vis; const idOf = (k) => 'VIS-' + String(k).padStart(3, '0'); while (s.vis[idOf(n)]) n++;
  const id = idOf(n); s.seq.vis = n + 1;
  const np = mipPontos(prot, t.area); const pts = []; for (let i = 1; i <= np; i++) pts.push({ n: i, v: null, ok: true, rec: false });
  s.vis[id] = Object.assign({ id, faz: t.faz, tal, prot, data, resp: resp || (MIPD.resp[t.faz] || ['Marcos'])[0], est: 'programada', npts: np, pts, pend: [], dec: null, dia: '', nota: '', orig: orig || 'ag01', parcial: false, pos_de: '' }, extra || {});
  return { id, msg: id + ' programada para ' + t.rot + ' × ' + p.alvo.toLowerCase() + ' · ' + mipBr(data) + ' · ' + s.vis[id].resp + ' · ' + np + ' pontos · aparece no app.' };
}
// ---------- coleta (app) ----------
// registra o ponto da vez (sem contagem; depois os de recoleta). Vistoria concluída com falta ou recoleta e sem decisão reabre a coleta.
function mipColetar(s, vid, valor, gpsOk) {
  const v = s.vis[vid]; if (!v) throw new Error('Vistoria não encontrada.');
  if (v.dec) throw new Error(vid + ' já tem decisão: a coleta está fechada.');
  if ((v.pend || []).length) throw new Error('Sincronize os pontos que estão no aparelho antes de coletar.');
  const pt = mipAlvoPt(v); if (!pt) throw new Error(vid + ' já foi concluída com todos os pontos.');
  const n = mipValor(mipP(v), valor, pt.n); const eraRec = pt.rec, reab = v.est === 'concluida';
  pt.v = n; pt.ok = gpsOk !== false; pt.rec = gpsOk === false;
  if (v.est === 'programada') { v.est = 'coleta'; if (v.data > MIPD.hoje) v.data = MIPD.hoje; }
  if (reab) { v.est = 'coleta'; v.parcial = false; }
  const prox = mipAlvoPt(v); const vez = prox && prox.n !== pt.n ? prox : null;
  return { msg: (reab ? vid + ' reaberta · ' : '') + 'Ponto ' + pt.n + (eraRec && !pt.rec ? ' recoletado' : ' registrado') + (pt.rec ? ' para recoleta (GPS fora da tolerância)' : '')
    + (vez ? ' · ponto ' + vez.n + (vez.rec ? ' (recoleta)' : '') + ' aberto.' : (prox ? ' · ponto ' + prox.n + ' segue em recoleta.' : ' · todos os pontos coletados.')) };
}
// corrige a contagem de um ponto já coletado (erro de digitação), enquanto não houver decisão
function mipCorrigir(s, vid, n, valor, gpsOk) {
  const v = s.vis[vid]; if (!v) throw new Error('Vistoria não encontrada.');
  if (v.dec) throw new Error(vid + ' já tem decisão: a contagem não muda mais.');
  const pt = v.pts.find(x => x.n === Number(n)); if (!pt || pt.v === null || pt.v === undefined) throw new Error('Ponto ' + n + ' ainda não foi coletado.');
  const x = mipValor(mipP(v), valor, pt.n); const de = pt.v;
  pt.v = x; pt.ok = gpsOk !== false; pt.rec = gpsOk === false;
  return { msg: 'Ponto ' + pt.n + ' corrigido: ' + mipN(de) + ' → ' + mipN(x) + (pt.rec ? ' (recoleta)' : '') + '.' };
}
function mipConcluir(s, vid) {
  const v = s.vis[vid]; if (!v) throw new Error('Vistoria não encontrada.'); if (v.est === 'concluida') throw new Error(vid + ' já foi concluída.');
  const R0 = mipRes(v); if (!R0.col) throw new Error('Colete ao menos um ponto antes de concluir.');
  v.est = 'concluida'; v.parcial = false; const R = mipRes(v, s); const S = MIP_SIT[R.k];
  return { msg: vid + ' concluída com ' + R.col + ' de ' + R.tot + ' pontos · ' + (S ? S[0].toLowerCase() : '') + (R.kr && R.k === 'incompleta' ? ' (parcial: ' + MIP_SIT[R.kr][0].toLowerCase() + ')' : '') + '.' };
}
function mipSinc(s, vid) {
  const v = s.vis[vid]; if (!v || !(v.pend || []).length) throw new Error('Nada a sincronizar.');
  const n = v.pend.length; v.pend.forEach(val => { const pt = v.pts.find(x => x.v === null || x.v === undefined); if (pt) pt.v = val; }); v.pend = [];
  const R = mipRes(v, s);
  return { msg: n + ' pontos de ' + v.resp + ' entraram na ' + vid + ' · ' + R.col + ' de ' + R.tot + ' pontos · sem conflito de versão.' };
}
function mipParcial(s, vid) { const v = s.vis[vid]; const R = mipRes(v); if (!R.val) throw new Error('Sem pontos válidos para decidir.'); v.parcial = true;
  return { msg: 'Decisão liberada com ' + R.val + ' de ' + R.tot + ' pontos · fica o alerta de coleta incompleta.' }; }
// ---------- produtos elegíveis e conferência do receituário ----------
function mipElig(v) { const p = mipP(v), t = mipT(v); return (MIPD.agf[t.cultura + '|' + p.chave] || []); }
function mipChecks(s, v, a, c) {
  const p = mipP(v), t = mipT(v); const tr = [], al = [], inf = []; let cond = '', fim = '', lim = '';
  const out = () => ({ tr, al, inf, cond, fim, lim, u: u || null });
  let u = null;
  if (v.parcial) { const R = mipRes(v); al.push('Decisão com ' + R.val + ' de ' + R.tot + ' pontos (coleta incompleta).'); }
  if (a.kind === 'monitorar' || a.kind === 'erradicar') { if (a.kind === 'erradicar') { const ar = Number(String(a.area).replace(',', '.'));
    if (!(ar > 0)) tr.push('Informe a área do foco.'); else if (ar > t.area + 1e-9) tr.push('Área maior que o talhão (' + mipN(t.area, 2) + ' ha).'); } return out(); }
  const L = mipElig(v); u = L.find(x => x.id === a.prod) || null;
  if (!L.length) { tr.push('Sem produto registrado para ' + mipCult(t) + ' × ' + p.alvo.toLowerCase() + ' nesta base.'); return out(); }
  if (!a.prod) { tr.push('Escolha um produto registrado.'); return out(); }
  if (!u) { tr.push('Sem registro para ' + mipCult(t) + ' × ' + p.alvo.toLowerCase() + '.'); return out(); }
  if (u.sit === 'Cancelado') tr.push('Registro cancelado: uso proibido.');
  else if (u.sit === 'Em reavaliação') al.push('Produto em reavaliação na Anvisa.');
  if (!u.conf) al.push('Uso não conferido na bula: confira antes de emitir.');
  const dose = Number(String(a.dose).replace(',', '.')), area = Number(String(a.area).replace(',', '.'));
  const fx = mipN(u.dmin, 3) + (u.dmax !== u.dmin ? '–' + mipN(u.dmax, 3) : '') + ' ' + u.un + '/ha';
  if (!(dose > 0)) tr.push('Informe a dose.'); else if (dose < u.dmin - 1e-9 || dose > u.dmax + 1e-9) tr.push('Dose fora da bula: ' + fx + (u.calda ? ' (calda de 1.000 L/ha)' : '') + '.');
  if (!(area > 0)) tr.push('Informe a área.'); else if (area > t.area + 1e-9) tr.push('Área maior que o talhão (' + mipN(t.area, 2) + ' ha).');
  if (!a.data) tr.push('Informe a data da aplicação.'); else if (a.data < MIPD.hoje) tr.push('Data da aplicação no passado.');
  const hist = mipApl(s, c).filter(x => x.tal === v.tal && (!a.os || x.os !== a.os));   // aplicação de O.S. cancelada não conta
  const nap = hist.filter(x => x.prod === u.id).length; if (u.mx && nap >= u.mx) tr.push('Nº máximo de aplicações no ciclo atingido: ' + nap + ' de ' + u.mx + '.');
  const prev = hist.filter(x => x.chave === p.chave && (!a.data || x.data <= a.data)).sort((x, y) => (x.data < y.data ? -1 : 1)).pop();
  if (prev) { const G = MIPD.grupo[prev.prod] || { gr: [], nome: prev.prod }; const com = G.gr.filter(g => u.gr.indexOf(g) >= 0);
    if (com.length) al.push('Rotação: mesmo grupo ' + com.join(' + ') + ' da última aplicação no ' + t.rot + ' (' + mipBr(prev.data) + ' · ' + G.nome + ').'); }
  const car = u.car || 0;
  if (a.data && car > 0) { fim = mipAdd(a.data, car);
    if (t.colheita === 'contínua') { cond = 'Colheita do ' + t.rot + ' suspensa até ' + mipBr(fim) + ' (carência de ' + car + ' dias).'; al.push(cond); }
    else if (/^\d{4}-/.test(t.colheita || '')) { lim = mipAdd(t.colheita, -car);
      if (fim > t.colheita) tr.push('Carência de ' + car + ' dias passa da colheita prevista (' + mipBr(t.colheita) + '): aplicar até ' + mipBr(lim) + '.');
      else inf.push('Carência de ' + car + ' dias: colheita liberada a partir de ' + mipBr(fim) + ' · prevista ' + mipBr(t.colheita) + ' · aplicar até ' + mipBr(lim) + '.'); } }
  else if (car === 0) inf.push('Carência: ' + (u.cart || 'sem restrição') + '.');
  if (c && c.lotes && dose > 0 && area > 0) { const need = cenQtd(dose, area);   // regra única (PRE-REV Q4)
    const disp = Object.values(c.lotes).filter(l => l.prod === u.nome).reduce((q, l) => q + Math.max(0, (l.fisico || 0) - (l.quarentena || 0) - (l.reservado || 0)), 0);
    if (disp + 1e-9 < need) al.push('Estoque: ' + mipN(disp, 2) + ' de ' + mipN(need, 2) + ' ' + u.un + ' · a liberação na O.S. aguarda a compra.');
    else inf.push('Estoque cobre: ' + mipN(need, 2) + ' ' + u.un + ' (' + mipN(disp, 2) + ' disponíveis).'); }
  return out();
}
// ---------- decisão: receituário + O.S. em A liberar (cenário das O.S.), erradicação e seguir monitorando ----------
function mipOsNova(c, no) {
  if (c.ordens[no.id]) throw new Error(no.id + ' já existe.');
  c.ordens[no.id] = { id: no.id, tipo: no.tipo, talhao: no.talhao, area: no.area, etapa: 'A liberar', versao: 'v1', realizado: 0, saldo: no.area, resp: no.resp,
    ins: (no.ins || []).map(x => ({ p: x.p, dose: x.dose, un: x.un, tot: x.tot, emb: '' })), req: null, selos: no.selos || [], ap: [], reservado: false, osc: { novo: no } };
  return { msg: no.id + ' emitida em A liberar.' };
}
// diagnóstico da decisão: o "A decidir" da vistoria, ou o mesmo DIA quando a O.S. da decisão anterior foi cancelada (mesmo diagnóstico,
// nova decisão); senão um DIA novo. Receituário emitido nunca é reaproveitado: o da O.S. cancelada fica "Cancelado" e nasce outro.
function mipDiaRedecide(s, v, c) { return !!(v.dia && s.dia[v.dia] && v.dec && v.dec.os && mipOsFora(c, v.dec.os)); }
function mipIds(s, v, a, c) {
  const dia = (v.dia && s.dia[v.dia] && (s.dia[v.dia].sit === 'A decidir' || mipDiaRedecide(s, v, c))) ? v.dia : 'DIA-' + String(s.seq.dia).padStart(3, '0');
  const r0 = s.dia[dia] && s.dia[dia].rec && s.rec[s.dia[dia].rec] && s.rec[s.dia[dia].rec].sit === 'Rascunho' ? s.dia[dia].rec : '';
  const ctl = a.kind === 'controlar' || a.kind === 'localizado';
  const old = (v.dec && v.dec.rec && s.rec[v.dec.rec] && s.rec[v.dec.rec].sit === 'Receituário emitido' && mipOsFora(c, v.dec.os)) ? v.dec.rec : '';
  return { dia, old, rec: ctl ? (r0 || 'REC-' + String(s.seq.rec).padStart(3, '0')) : '', ra: ctl ? 'RA-' + String(s.seq.ra).padStart(4, '0') : '' };
}
// receituário cuja O.S. foi cancelada sem execução: fica cancelado, com o substituto (se houver)
function mipRecCancelar(s, id, os, subst) { const r = s.rec[id]; if (!r) return; r.sit = 'Cancelado'; r.motivo = os + ' cancelada sem execução'; r.subst = subst || ''; }
function mipNo(c, s, v, a, ck, ids) {
  const p = mipP(v), t = mipT(v), R = mipRes(v, s); const er = a.kind === 'erradicar'; const u = ck.u;
  const novos = Object.values(c.ordens).filter(o => o.osc && o.osc.novo);
  const key = 'mip|' + v.id + '|' + v.prot; const dup = novos.find(o => (o.osc.novo.keys || []).indexOf(key) >= 0 && o.etapa !== 'Canceladas');
  if (dup) throw new Error('Já existe ' + dup.id + ' para ' + v.id + ' (' + p.alvo.toLowerCase() + ').');
  const id = 'OS-0' + (440 + novos.length);
  const area = Number(String(a.area).replace(',', '.')), dose = er ? 0 : Number(String(a.dose).replace(',', '.'));
  const op = er ? 'Tratos culturais' : 'Pulverização'; const cj = MIPD.conj[er ? 'Tratos culturais' : (t.cultura === 'Mamão' ? 'Pulverização · mamão' : 'Pulverização')];
  const nome = er ? 'Erradicação de plantas · ' + p.alvo.toLowerCase() : 'Controle de ' + p.alvo.toLowerCase() + (a.kind === 'localizado' ? ' · foco' : '');
  const g = u ? (/^Fungicida/.test(u.cls) ? 'Fungicidas' : (/^Herbicida/.test(u.cls) ? 'Herbicidas' : 'Inseticidas')) : '';
  const ins = er ? [] : [{ g, p: u.nome, dose, un: u.un, tot: cenQtd(dose, area), sit: 'Reserva ao liberar' }];
  return { id, novo: true, keys: [key], tipo: (er ? 'Tratos culturais · ' : 'Pulverização · ') + nome, talhao: t.rot, area, etapa: 'A liberar',
    selos: ck.cond ? [{ t: 'Colheita suspensa até ' + mipBr(ck.fim), c: 'yellow' }] : [], faz: t.faz, saf: '2026/27', lam: '', obs: '', agua: false, ins,
    semins: er ? 'Sem insumo: arrancar e destruir as plantas com sintoma (roguing).' : '', bloq: null, aviso: ck.cond || '', dono: 'Ana (agrônoma)', prazo: 'liberar',
    atv: { op, nome, gat: v.id + ' · ' + mipSit(s, v, c).t.toLowerCase(), orig: 'Pragas e doenças' + (ids.ra ? ' · receituário ' + ids.ra : ' · ' + ids.dia), conj: cj.conj, rend: cj.rend },
    realizado: 0, saldo: area, resp: '—', versao: 'v1', janela: 'a partir de ' + mipBr(a.data) + (ck.lim ? ' · aplicar até ' + mipBr(ck.lim) : ''), ap: [], nota: '',
    cond: 'Ana (agrônoma) confere e libera' + (er ? '' : '; liberar reserva o produto no Estoque') + '. Próximo passo: liberar para execução.',
    orig: ['Pragas e doenças · ' + v.id + ' · ' + t.rot + ' · ' + p.alvo + ' · ' + R.txt, ids.dia + (ids.rec ? ' · ' + ids.rec : '') + (ids.ra ? ' · receituário ' + ids.ra + ' (Ana · RT)' : '')], link: '' };
}
// emitir (agrônomo RT): numa só ação grava a O.S. (A liberar) no cenário e DIA + REC/RA + decisão no MIP; nada é liberado aqui
function mipEmitir(self, vid, a) {
  const s = mipGet(); const v = s.vis[vid]; if (!v) return { erro: 'Vistoria não encontrada.' };
  if (v.dec && v.dec.os) { const et = mipOsEt(typeof cenGet === 'function' ? cenGet() : null, v.dec.os); if (et && et !== 'Canceladas') return { erro: vid + ' já tem controle em ' + v.dec.os + '.' }; }
  if (typeof cenMudar !== 'function') return { erro: 'Cenário das O.S. indisponível nesta tela.' };
  const c0 = cenGet(); const ck = mipChecks(s, v, a, c0); if (ck.tr.length) return { erro: ck.tr[0] };
  const ids = mipIds(s, v, a, c0); let osId = '';
  const r1 = cenMudar(null, (c) => { const no = mipNo(c, s, v, a, ck, ids); osId = no.id; return mipOsNova(c, no); });
  if (r1.erro) return { erro: r1.erro };
  const p = mipP(v), u = ck.u, er = a.kind === 'erradicar';
  const r2 = mipMudar(null, (s2) => {
    const v2 = s2.vis[vid]; const hoje = MIPD.hoje;
    if (ids.dia === 'DIA-' + String(s2.seq.dia).padStart(3, '0')) s2.seq.dia++;
    const R = mipRes(v2, s2);
    s2.dia[ids.dia] = Object.assign(s2.dia[ids.dia] || { id: ids.dia, vis: vid, tal: v2.tal, hip: p.alvo + ' · ' + MIP_SIT[R.kr || R.k][0].toLowerCase(), risco: 'alto' },
      { sit: 'Registrada', dec: er ? 'Erradicar plantas' : (a.kind === 'localizado' ? 'Controle localizado' : 'Controlar'), em: hoje, por: 'Ana', rec: ids.rec });
    if (ids.old) mipRecCancelar(s2, ids.old, v2.dec.os, ids.rec);
    if (ids.rec) { if (ids.rec === 'REC-' + String(s2.seq.rec).padStart(3, '0')) s2.seq.rec++; s2.seq.ra++;
      s2.rec[ids.rec] = Object.assign(s2.rec[ids.rec] || { id: ids.rec, dia: ids.dia, vis: vid, tal: v2.tal },
        { sit: 'Receituário emitido', ra: ids.ra, prod: u.id, nome: u.nome, g: u.g, dose: Number(String(a.dose).replace(',', '.')), un: u.un, area: Number(String(a.area).replace(',', '.')), data: a.data, os: osId, cond: ck.cond, em: hoje }); }
    v2.dia = ids.dia;
    v2.dec = { t: a.kind, por: 'Ana', em: hoje, dia: ids.dia, rec: ids.rec, ra: ids.ra, os: osId, prod: u ? u.id : '', dose: u ? Number(String(a.dose).replace(',', '.')) : 0, area: Number(String(a.area).replace(',', '.')), data: a.data, cond: ck.cond, nota: a.nota || '' };
    if (u) s2.apl.push({ tal: v2.tal, data: a.data, prod: u.id, chave: p.chave, os: osId });
    return { msg: er ? (osId + ' de erradicação emitida em A liberar (' + ids.dia + ') · Ana libera na O.S.')
      : ('Receituário ' + ids.ra + ' emitido (' + ids.dia + ' · ' + ids.rec + ') · ' + osId + ' em A liberar · Ana libera na O.S.') };
  });
  if (r2.erro) return r2;
  if (self) self.setState({ miprev: Date.now(), cenrev: Date.now(), g2toast: r2.msg });
  return { msg: r2.msg, os: osId };
}
// seguir monitorando: registra a decisão e programa a próxima (ritmo do protocolo; perto do NC = 3 dias; nunca antes de amanhã)
function mipMonitorar(s, vid, motivo) {
  const v = s.vis[vid]; const R = mipRes(v, s), p = mipP(v); const hoje = MIPD.hoje;
  if ((R.k === 'acima' || R.k === 'foco') && !String(motivo || '').trim()) throw new Error('Informe o motivo para não controlar.');
  let prox = mipAdd(v.data, R.kr === 'perto' ? 3 : p.inter); if (prox <= hoje) prox = mipAdd(hoje, 1);
  let dia = ''; const c = mipCen(); const red = mipDiaRedecide(s, v, c);
  if (red && v.dec.rec && s.rec[v.dec.rec] && s.rec[v.dec.rec].sit === 'Receituário emitido') mipRecCancelar(s, v.dec.rec, v.dec.os, '');
  if (R.k === 'foco' || R.k === 'acima' || red) { dia = (v.dia && s.dia[v.dia] && (s.dia[v.dia].sit === 'A decidir' || red)) ? v.dia : 'DIA-' + String(s.seq.dia++).padStart(3, '0');
    s.dia[dia] = Object.assign(s.dia[dia] || { id: dia, vis: vid, tal: v.tal, hip: p.alvo + ' · ' + MIP_SIT[R.k][0].toLowerCase(), risco: 'médio' }, { sit: 'Registrada', dec: 'Seguir monitorando', em: hoje, por: 'Ana', motivo: motivo || '', rec: '' });
    v.dia = dia; }
  v.dec = { t: 'monitorar', por: 'Ana', em: hoje, prox, dia, nota: motivo || '' };
  let nova = ''; if (!mipAberta(s, v.tal, v.prot)) { nova = mipNovaVis(s, v.tal, v.prot, prox, v.resp, 'monitorar').id; }
  return { msg: 'Seguir monitorando registrado em ' + vid + (nova ? ' · ' + nova + ' programada para ' + mipBr(prox) : ' · já há vistoria aberta') + (R.kr === 'perto' ? ' (perto do NC: revisita em 3 dias)' : '') + '.', nova };
}
// leitura pós: vistoria no mesmo método, 7 dias após a aplicação (nunca antes de amanhã)
function mipPos(s, vid) {
  const v = s.vis[vid]; const d = v.dec; if (!d || !d.os) throw new Error('Sem controle para avaliar.'); if (d.pos) throw new Error('Leitura pós já programada: ' + d.pos + '.');
  let data = mipAdd(d.data || d.em, 7); if (data <= MIPD.hoje) data = mipAdd(MIPD.hoje, 1);
  const ab = mipAberta(s, v.tal, v.prot); let id;
  if (ab) { ab.pos_de = vid; id = ab.id; } else id = mipNovaVis(s, v.tal, v.prot, data, v.resp, 'pos', { pos_de: vid }).id;
  d.pos = id; return { msg: 'Leitura pós ' + id + ' programada para ' + mipBr(s.vis[id].data) + ' (mesmo método da ' + vid + ').' };
}
// histórico do talhão: vistorias e aplicações (grupo de modo de ação), da mais recente para a mais antiga
function mipHist(s, tal, c) {
  const vs = Object.values(s.vis).filter(x => x.tal === tal).map(x => { const S = mipSit(s, x, c); const p = mipP(x);
    return { d: x.data, t: x.id + ' · ' + p.alvo, sub: S.R.txt, ch: S.t, c: S.c, h: 'AG-01.dc.html#' + x.id, tipo: 'vis' }; });
  const ap = s.apl.filter(x => x.tal === tal).map(x => { const G = MIPD.grupo[x.prod] || { nome: x.prod, g: '' };
    const canc = mipOsFora(c, x.os);
    return { d: x.data, t: 'Aplicação · ' + G.nome, sub: (G.g || '') + ' · ' + x.chave + (x.os ? ' · ' + x.os : ''), ch: canc ? 'cancelada' : (x.data > MIPD.hoje ? 'programada' : 'aplicada'), c: canc ? 'red' : 'gray', h: x.os ? 'OS.dc.html#' + x.os : '', tipo: 'apl' }; });
  return vs.concat(ap).sort((a, b) => (a.d < b.d ? 1 : -1));
}
// vistorias do talhão no período (dias) + as abertas e as decisões pendentes, da pior para a melhor
function mipDoTal(s, tal, dias, c) {
  const lim = mipAdd(MIPD.hoje, -(dias || 7));
  return Object.values(s.vis).filter(x => x.tal === tal).map(x => ({ v: x, S: mipSit(s, x, c) }))
    .filter(x => x.v.data >= lim || x.S.k !== 'encerrada')
    .sort((a, b) => (a.S.ord - b.S.ord) || (a.v.data < b.v.data ? 1 : -1));
}
try { window.__mip = { mipGet, mipMudar, mipReset, mipRes, mipSit, mipProx, mipChecks, mipNovaVis, mipEmitir, mipMonitorar, mipColetar, mipCorrigir, mipConcluir }; } catch (e) {}
