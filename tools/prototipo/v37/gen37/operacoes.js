// PA-OPER F1 · serviço único das contas por operação (docs/integracao/V71/PA-OPER.md, decisões 2, 3, 5, 8 e 9).
// Plano, O.S., MB-02det e ficha chamam estas funções; nenhuma outra tela repete a fórmula (ENG-011). As cargas ficam no cenPreparoOrdem.
// Valores normativos (bula, curva de ponta) chegam como dado, com origem; o código não traz nenhum padrão.
'use strict';

// Famílias técnicas (tabela "Seções por operação"). A F1 implementa os campos de Pulverização; as demais só organizam.
const OP_FAMILIAS = {
  preparo: 'Preparo do solo', ts: 'Tratamento de sementes', plantio: 'Plantio', mudas: 'Plantio de mudas',
  adubacao: 'Adubação e correção', pulverizacao: 'Pulverização', fertirrigacao: 'Fertirrigação',
  tratos: 'Tratos culturais e poda', colheita: 'Colheita'
};
// Migração das operações de hoje (tabela "Migração das operações de hoje para as famílias").
const OP_MIGRACAO = [
  [/^pulveriza/i, 'pulverizacao'], [/^dessecaç/i, 'pulverizacao'], [/^plantio de mudas/i, 'mudas'], [/^plantio/i, 'plantio'],
  [/^tratamento de sementes/i, 'ts'], [/^aduba|^calagem|^gessagem|^fosfatagem/i, 'adubacao'], [/^fertirriga/i, 'fertirrigacao'],
  [/^poda|^tratos|^desbaste|^desbrota|^roçada|^capina|^sexagem/i, 'tratos'], [/^colheita/i, 'colheita'],
  [/^subsolagem|^gradagem|^escarifica|^terraç|^preparo/i, 'preparo']
];
function opFamilia(nomeOp) {
  const n = String(nomeOp || '').trim();
  for (const [re, f] of OP_MIGRACAO) if (re.test(n)) return f;
  return null;                                   // "Outra operação…" exige escolher a família (decisão 2)
}
// Chave estável da operação no endereço (#plano=…&op=…): sem acento, minúscula, com hífen.
function opChave(nomeOp) {
  return String(nomeOp || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

// Seções na ordem do ciclo: pela primeira atividade (gatilho em DAP) e, no empate, pela fase do CD-08.
function opSecoes(atividades, faseDe) {
  const m = new Map();
  for (const a of atividades) {
    if (!m.has(a.op)) m.set(a.op, {op: a.op, chave: opChave(a.op), familia: opFamilia(a.op), atividades: []});
    m.get(a.op).atividades.push(a);
  }
  const s = [...m.values()];
  for (const x of s) {
    x.atividades.sort((a, b) => a.dap - b.dap || String(a.id).localeCompare(String(b.id)));
    x.inicio = x.atividades[0].dap;
  }
  const f = faseDe || (() => 0);
  return s.sort((a, b) => a.inicio - b.inicio || f(a.op) - f(b.op) || a.op.localeCompare(b.op));
}

// Dois níveis (decisão 3): a atividade herda o parâmetro da operação; o valor próprio é visível e reversível.
function opParam(ativ, params, campo) {
  const proprio = ativ && ativ[campo];
  if (proprio !== undefined && proprio !== null && proprio !== '') return {valor: Number(proprio), origem: 'própria'};
  const op = params && params[campo];
  if (op !== undefined && op !== null && op !== '') return {valor: Number(op), origem: 'da operação'};
  return {valor: null, origem: 'pendente'};
}
// Texto das alterações do rascunho para o parâmetro da operação (P3).
function opAlteracaoParam(secao, params0, params1, campo, rotulo, un) {
  const a = params0 && params0[campo], b = params1 && params1[campo];
  if (String(a ?? '') === String(b ?? '')) return '';
  const herdeiras = secao.atividades.filter(x => x[campo] === undefined || x[campo] === null || x[campo] === '').length;
  const fmt = v => v === undefined || v === null || v === '' ? 'pendente' : opNum(v);
  return `${secao.op} · ${rotulo} ${fmt(a)} → ${fmt(b)} ${un} em ${herdeiras} atividade${herdeiras === 1 ? '' : 's'}`;
}

// Cargas (41.5): o serviço é o cenPreparoOrdem (cenario.js, EX-38), em decimal; este arquivo não repete a conta (ENG-011).
const OP_EPS = 1e-9;

// Vazão por bico (EX-38 R10): alvo = volume × velocidade × espaçamento ÷ 600 (L/min). Sem velocidade ou espaçamento: desconhecido.
function opVazaoAlvo(volumeLHa, velKmh, espM) {
  const v = Number(volumeLHa), s = Number(velKmh), e = Number(espM);
  if (!(v > 0) || !(s > 0) || !(e > 0)) return null;
  return v * s * e / 600;
}
// Vazão disponível: da curva ponta × pressão (outra fonte, dado com origem). Sem curva ou ponto: desconhecido.
function opVazaoDisp(curva, ponta, pressaoBar) {
  if (!curva || !ponta || !(Number(pressaoBar) > 0)) return null;
  const pts = (curva[ponta] || []).filter(p => Number(p.bar) > 0 && Number(p.lmin) > 0);
  const hit = pts.find(p => Math.abs(p.bar - pressaoBar) < OP_EPS);
  return hit ? Number(hit.lmin) : null;
}
function opVazao(volumeLHa, velKmh, espM, curva, ponta, pressaoBar) {
  const alvo = opVazaoAlvo(volumeLHa, velKmh, espM), disp = opVazaoDisp(curva, ponta, pressaoBar);
  return {alvo, disp, difPct: alvo !== null && disp !== null ? (disp - alvo) / alvo * 100 : null};
}

// Dose por 100 L → dose/ha pelo volume efetivo da atividade.
function opDoseHa(prod, volumeLHa) {
  if (prod.base === '100L') return Number(volumeLHa) > 0 ? Number(prod.dose) * Number(volumeLHa) / 100 : null;
  return Number(prod.dose);
}

// Conferência de bula pelo gatilho (P7). Entrada já no dia relativo (t) que o adaptador calcula: DAP, data em dias, ou colheita ± dias.
// bula[produto] = {grupos: [...], usos: {cultura: {alvo: {dmax, un, car, mx, porCalda}}}} (AG-07; demonstração marcada na origem).
// Com alvo: vale o uso daquele cultura × alvo. Sem alvo: só reprova o que todos os usos da cultura reprovariam (o mais permissivo passa).
// Devolve [{nivel: 'impede'|'aviso', ativ, prod, motivo}]. Impede publicar a versão; nunca impede guardar o rascunho.
function opBula(pulverizacoes, bula, ctx) {
  const out = [], cultura = ctx && ctx.cultura;
  // colheitas do plano (perenes colhem várias vezes): a carência vale contra a próxima colheita depois da aplicação
  const colheitas = ((ctx && ctx.colheitasT) || (ctx && ctx.colheitaT !== undefined && ctx.colheitaT !== null ? [ctx.colheitaT] : [])).slice().sort((x, y) => x - y);
  const ordem = [...pulverizacoes].sort((a, b) => a.t - b.t || String(a.id).localeCompare(String(b.id)));
  const usos = {};
  let grupoAnt = null;
  for (const a of ordem) {
    const vol = opParam(a, ctx && ctx.params, 'calda').valor;
    const grupos = [];
    for (const p of a.produtos || []) {
      const nome = p.prod || p.nome, b = bula && bula[nome];
      if (!b || !(b.grupos || []).length) continue;                     // adjuvante e item sem modo de ação: a bula não se aplica aqui
      usos[nome] = (usos[nome] || 0) + 1;
      const daCultura = (b.usos && b.usos[cultura]) || {};
      const alvos = Object.keys(daCultura);
      if (!alvos.length) { out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: sem registro para ${cultura}`}); continue; }
      let cand = alvos.map(k => daCultura[k]);
      if (a.alvo) {
        if (!daCultura[a.alvo]) { out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: sem registro para ${cultura} × ${a.alvo}`}); continue; }
        cand = [daCultura[a.alvo]];
      }
      const lims = cand.map(u => {
        if (!(Number(u.dmax) > 0)) return null;
        if (u.porCalda) return vol !== null ? Number(u.dmax) * vol / 100 : null;
        return String(u.un || '').startsWith(String(p.un || '')) ? Number(u.dmax) : null;
      });
      const dha = Number(p.dose);
      if (lims.every(x => x === null) && cand.some(u => !u.porCalda && Number(u.dmax) > 0 && !String(u.un || '').startsWith(String(p.un || ''))))
        out.push({nivel: 'aviso', ativ: a.id, prod: nome, motivo: `${nome}: unidade da bula (${cand[0].un}) diferente da do plano (${p.un}/ha); dose não conferida`});
      if (lims.every(x => x !== null) && dha > Math.max(...lims) + OP_EPS)
        out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: dose de ${opNum(dha)} ${p.un}/ha acima da bula (${opNum(Math.max(...lims))} ${p.un}/ha)`});
      const fx = cand.filter(u => u.volMin !== undefined || u.volMax !== undefined);   // faixa de volume, só quando a bula a define
      if (vol !== null && fx.length === cand.length && fx.every(u => vol < Number(u.volMin ?? -Infinity) || vol > Number(u.volMax ?? Infinity)))
        out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: volume de ${opNum(vol)} L/ha fora da faixa da bula (${opNum(fx[0].volMin)}–${opNum(fx[0].volMax)} L/ha)`});
      const mxs = cand.map(u => u.mx).filter(x => x !== null && x !== undefined);
      if (mxs.length === cand.length && usos[nome] > Math.max(...mxs))
        out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: ${usos[nome]}ª aplicação no plano; a bula permite ${Math.max(...mxs)}`});
      const cars = cand.map(u => u.car).filter(x => x !== null && x !== undefined);
      const colheita = colheitas.find(x => x >= a.t);
      if (colheita !== undefined && cars.length === cand.length) {
        const sobra = a.t + Math.min(...cars) - colheita;
        if (sobra > 0) out.push({nivel: 'impede', ativ: a.id, prod: nome, motivo: `${nome}: carência termina ${sobra} dia${sobra === 1 ? '' : 's'} depois da colheita prevista`});
      }
      grupos.push(...(b.grupos || []));
    }
    if (grupoAnt && grupos.some(g => grupoAnt.includes(g))) out.push({nivel: 'aviso', ativ: a.id, prod: null, motivo: `mesmo grupo de modo de ação da aplicação anterior (${[...new Set(grupos.filter(g => grupoAnt.includes(g)))].join(', ')})`});
    if (grupos.length) grupoAnt = grupos;
  }
  return out;
}

// O que falta para gerar a O.S. (Pendente). Na F1, só Pulverização tem campos próprios.
function opPendencias(secao, params) {
  if (secao.familia !== 'pulverizacao') return [];
  const out = [];
  for (const a of secao.atividades) {
    if (opParam(a, params, 'calda').valor === null) out.push({ativ: a.id, campo: 'calda', motivo: `${a.nome}: sem volume de calda`});
    if (!a.alvo) out.push({ativ: a.id, campo: 'alvo', motivo: `${a.nome}: sem alvo`});
  }
  return out;
}
// Estado calculado (decisão 5): fala de completude, não de aprovação.
function opEstado(pendencias, conferencias) {
  if (conferencias.some(c => c.nivel === 'impede')) return {cod: 'impedida', marca: '⛔', texto: 'Impedida'};
  if (pendencias.length) return {cod: 'pendente', marca: '•', texto: 'Pendente'};
  if (conferencias.some(c => c.nivel === 'aviso')) return {cod: 'aviso', marca: '⚠', texto: 'Com aviso'};
  return {cod: 'pronta', marca: '✓', texto: 'Pronta'};
}

// Publicação (decisão 9). versoes = [{v, estado: 'publicada'|'em revisão'|'rascunho', por, em, chave}]. Pura: devolve o novo estado.
function opPublicar(plano, ato) {
  const vs = (plano.versoes || []).slice();
  if (ato.chave && vs.some(x => x.chave === ato.chave)) return {plano, repetido: true};          // mesma chave: não cria vN+1
  const pub = vs.filter(x => x.estado === 'publicada').map(x => x.v);
  const vigente = pub.length ? Math.max(...pub) : 0;
  const novo = vigente + 1;
  if (ato.tipo === 'publicar' && !ato.podePublicar) return {plano, erro: 'sem papel para publicar nesta fazenda'};
  if (ato.tipo === 'publicar' && ato.impedimentos && ato.impedimentos.length) return {plano, erro: ato.impedimentos[0].motivo};
  const resto = vs.filter(x => x.estado === 'publicada');
  const reg = {v: novo, por: ato.por, em: ato.em, chave: ato.chave || null};
  if (ato.tipo === 'publicar') resto.push(Object.assign(reg, {estado: 'publicada'}));
  else if (ato.tipo === 'submeter') resto.push(Object.assign(reg, {estado: 'em revisão'}));
  else if (ato.tipo === 'devolver') return {plano: Object.assign({}, plano, {versoes: resto, revisao: null}), devolvida: novo};
  else return {plano, erro: 'ato desconhecido'};
  return {plano: Object.assign({}, plano, {versoes: resto}), v: novo};
}

// K7 · desloca o gatilho de uma atividade n dias no calendário (n > 0 adia; n < 0 antecipa). Puro. A âncora fica a mesma; só antes ↔ depois
// da colheita troca quando o deslocamento cruza a colheita (é o mesmo instante, contado do outro lado). n não inteiro ou zero: nada muda.
function opDeslocar(g, n) {
  n = Number(n);
  if (!g || !Number.isInteger(n) || n === 0) return g;
  if (g.tipo === 'DATA') {
    const d = new Date(String(g.data) + 'T12:00:00Z'); if (isNaN(d.getTime())) return g;
    d.setUTCDate(d.getUTCDate() + n); return Object.assign({}, g, {data: d.toISOString().slice(0, 10)});
  }
  if (g.tipo === 'DAP') return Object.assign({}, g, {dias: Number(g.dias) + n});
  if (g.tipo === 'DANC' || g.tipo === 'DAPC') {
    const r = (g.tipo === 'DANC' ? -Number(g.dias) : Number(g.dias)) + n;   // dias contados da colheita: antes < 0 ≤ depois
    return Object.assign({}, g, r < 0 ? {tipo: 'DANC', dias: -r} : {tipo: 'DAPC', dias: r});
  }
  return g;
}

function opNum(v, casas) {
  if (v === null || v === undefined || v === '' || !isFinite(Number(v))) return '—';
  const c = casas === undefined ? (Number.isInteger(Number(v)) ? 0 : 2) : casas;
  return Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 0, maximumFractionDigits: c});
}

if (typeof module !== 'undefined') module.exports = {OP_FAMILIAS, opFamilia, opChave, opSecoes, opParam, opAlteracaoParam, opVazaoAlvo, opVazaoDisp, opVazao, opDoseHa, opBula, opPendencias, opEstado, opPublicar, opDeslocar, opNum};
