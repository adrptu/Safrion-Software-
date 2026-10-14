// ===== SAF-FAZ-2 · safra com várias fazendas (proprietário, 14/10/2026: "E se planejar safra puder selecionar mais de 1 fazenda e os
// talhoes de cada fazenda?") · acordo Claude/Codex 6173544970 e ajustes 6173977617 =====
// Modelo: cada fazenda tem a própria sub-safra (a linha de hoje: {id, nome, ini, fim, faz, estado, ro}); a safra de várias fazendas liga as
// sub-safras pelo campo mae. Talhões, ocupação, capacidade, demanda e solicitação de compra continuam por sub-safra, com os cálculos já
// testados; a mãe só reúne a leitura. Danos evitados: recurso ou insumo de uma fazenda cobrir a falta de outra; remover fazenda e deixar
// cultivo, solicitação, O.S., plano ou orçamento órfãos; fazenda nova herdar estado ou aprovação de outra; envio repetido duplicar compra.
// Funções puras sobre dados simples, sem DOM: a tela (safra.js) e os testes de contrato (safra_grupo_contrato_test.js, autoria Codex) chamam.

const SG_ESTADO_NOVA = 'Rascunho';

function sgTxt(x) { return String(x === undefined || x === null ? '' : x).trim(); }
function sgData(x) { return /^\d{4}-\d{2}-\d{2}$/.test(sgTxt(x)); }
// arredonda somas de quantidade sem arrastar erro binário (0,1 + 0,2): 6 casas bastam para kg, L, sc e ha
function sgSoma(a, b) { return Math.round((Number(a) + Number(b)) * 1e6) / 1e6; }

// mãe da safra (id de sub-safra ou da própria mãe); safra de uma fazenda: null
function sgMaeDe(safs, id) { const s = (safs || []).find(x => x.id === id); if (s) return s.mae || null; return (safs || []).some(x => x.mae === id) ? id : null; }
// grupo de uma safra: a mãe e as sub-safras na ordem da lista; safra de uma fazenda: grupo de uma sub, sem mãe
function sgGrupo(safs, id) {
  const mae = sgMaeDe(safs, id);
  const subs = mae ? (safs || []).filter(x => x.mae === mae) : (safs || []).filter(x => x.id === id);
  if (!subs.length) return null;
  return { mae, nome: subs[0].nome, ini: subs[0].ini, fim: subs[0].fim, subs: subs.map(x => Object.assign({}, x)) };
}

// o que impede tirar a fazenda da safra; cada motivo diz onde se resolve (destino)
// dep = {cultivos, sol: {id, estado}|null, os: [ids], plano_aprovado, orcamento_aprovado}
function sgImpedeRemover(sub, dep) {
  const d = dep || {}, m = [];
  if (sub.ro) m.push({ t: 'Safra encerrada: só consulta.', destino: '' });
  if (d.plano_aprovado) m.push({ t: 'Plano operacional aprovado nesta fazenda.', destino: 'Plano operacional da safra' });
  if (d.orcamento_aprovado) m.push({ t: 'Orçamento aprovado nesta fazenda.', destino: 'Orçamento da safra' });
  if (d.sol) m.push({ t: 'Solicitação ' + d.sol.id + ' enviada a Compras' + (d.sol.estado ? ' (' + d.sol.estado + ')' : '') + '.', destino: 'Compra de insumos' });
  if ((d.os || []).length) m.push({ t: (d.os.length === 1 ? 'O.S. ' + d.os[0] + ' vinculada' : d.os.length + ' O.S. vinculadas (' + d.os.join(', ') + ')') + '.', destino: 'Ordens de serviço' });
  if (Number(d.cultivos) > 0) m.push({ t: d.cultivos + (d.cultivos === 1 ? ' cultivo planejado' : ' cultivos planejados') + ' nesta fazenda.', destino: 'Cultivos e planos desta fazenda' });
  return m;
}

// cria ou edita a safra com uma ou mais fazendas, sem tocar nas sub-safras que ficam (IDs, estado, cultivos)
// ped = {chave, nome, ini, fim, fazendas: [...], saf?: id de uma sub-safra (editar)}
// op = {rec: memória de recibos por chave (idempotência), deps: (saf) => dep, novoId: (tipo, faz, i) => id}
// volta {ok, erros?, bloqueios?, safs, mae, recibo, repetido}; recusa é atômica: nada muda quando algo bloqueia
function sgCompor(safs, ped, op) {
  op = op || {}; const rec = op.rec || {}, deps = op.deps || (() => ({})), novoId = op.novoId;
  const lista = (safs || []).map(x => Object.assign({}, x));
  const chave = sgTxt(ped && ped.chave);
  if (!chave) return { ok: false, erros: { chave: 'Comando sem chave de idempotência.' }, safs: lista };
  if (rec[chave]) return Object.assign({}, rec[chave], { safs: lista, repetido: true });
  const nome = sgTxt(ped.nome), ini = sgTxt(ped.ini), fim = sgTxt(ped.fim);
  const faz = []; (ped.fazendas || []).map(sgTxt).filter(Boolean).forEach(f => { if (faz.indexOf(f) < 0) faz.push(f); });
  const erros = {};
  if (!nome) erros.nome = 'Informe o nome da safra.';
  if (!sgData(ini)) erros.ini = 'Informe o início.';
  if (!sgData(fim)) erros.fim = 'Informe o fim.';
  else if (sgData(ini) && fim <= ini) erros.fim = 'O fim precisa ser depois do início.';
  if (!faz.length) erros.fazendas = 'Escolha ao menos uma fazenda.';
  if (Object.keys(erros).length) return { ok: false, erros, safs: lista };
  if (typeof novoId !== 'function') return { ok: false, erros: { chave: 'Sem gerador de identificador.' }, safs: lista };
  const g = ped.saf ? sgGrupo(lista, ped.saf) : null;
  if (ped.saf && !g) return { ok: false, erros: { saf: 'Safra não encontrada.' }, safs: lista };
  if (g && g.subs.some(s => s.ro)) return { ok: false, erros: { saf: 'Safra encerrada: só consulta.' }, safs: lista };
  const atuais = g ? g.subs : [];
  const sai = atuais.filter(s => faz.indexOf(s.faz) < 0), entra = faz.filter(f => !atuais.some(s => s.faz === f));
  const bloqueios = sai.map(s => ({ faz: s.faz, saf: s.id, motivos: sgImpedeRemover(s, deps(s.id)) })).filter(b => b.motivos.length);
  if (bloqueios.length) return { ok: false, bloqueios, safs: lista };
  let mae = g ? g.mae : null; const fica = atuais.length - sai.length + entra.length;
  if (fica > 1 && !mae) mae = novoId('mae', '', 0);
  if (fica <= 1) mae = null;
  const subsR = [];
  // sub-safra vazia que sai empresta o ID à fazenda que entra (a safra aberta continua a mesma), sem herdar estado: volta a rascunho
  const livres = sai.slice();
  atuais.forEach(s => { if (sai.indexOf(s) >= 0) return; subsR.push({ s: Object.assign(s, { nome, ini, fim, mae }), a: 'mantida' }); });
  entra.forEach((f, i) => { const l = livres.shift();
    if (l) { const de = l.faz; subsR.push({ s: Object.assign(l, { nome, ini, fim, faz: f, mae, estado: SG_ESTADO_NOVA }), a: 'trocada', de }); }
    else subsR.push({ s: { id: novoId('sub', f, i), nome, ini, fim, faz: f, mae, estado: SG_ESTADO_NOVA }, a: 'criada' }); });
  subsR.forEach(x => { if (!x.s.mae) delete x.s.mae; });
  // a lista guarda a ordem: as sub-safras do grupo ficam juntas, no lugar da primeira; safra nova vai para o fim
  const idsG = atuais.map(s => s.id); const pos = lista.findIndex(x => idsG.indexOf(x.id) >= 0);
  const resto = lista.filter(x => idsG.indexOf(x.id) < 0); const ordem = faz.map(f => subsR.find(x => x.s.faz === f));
  const novas = ordem.map(x => x.s);
  const out = pos < 0 ? resto.concat(novas) : resto.slice(0, pos).concat(novas, resto.slice(pos));
  const recibo = { chave, mae, nome, subs: ordem.map(x => Object.assign({ faz: x.s.faz, saf: x.s.id, acao: x.a }, x.de ? { de: x.de } : {}))
    .concat(livres.map(s => ({ faz: s.faz, saf: s.id, acao: 'removida' }))) };
  const res = { ok: true, mae, recibo };
  rec[chave] = res;
  return Object.assign({}, res, { safs: out, repetido: false });
}

// leitura reunida: o que cada fazenda tem e a soma só do que se soma. info[saf] = {area_ha: número|null, cultivos, estado,
// plano?: 'Aprovado'|'Pendente'|null, orcamento?: idem, demanda: [{insumo, un, qtd, talhao, ciclo, destino}]|null, sol: {id, estado}|null}
// Sem estado geral herdado: a safra mostra a contagem de estados e diz quando está parcial. Falta de dado não vira zero.
function sgLeitura(grupo, info) {
  const I = info || {}; const fz = grupo.subs.map(s => { const x = I[s.id] || {};
    const area = (x.area_ha === null || x.area_ha === undefined || isNaN(Number(x.area_ha))) ? null : Number(x.area_ha);
    return { faz: s.faz, saf: s.id, area_ha: area, cultivos: Number(x.cultivos) || 0, estado: x.estado || s.estado || SG_ESTADO_NOVA,
      plano: x.plano || null, orcamento: x.orcamento || null, sol: x.sol || null, demanda: Array.isArray(x.demanda) ? x.demanda : null }; });
  const conh = fz.filter(f => f.area_ha !== null);
  const area = { ha: conh.reduce((a, f) => sgSoma(a, f.area_ha), 0), completa: conh.length === fz.length, faltam: fz.filter(f => f.area_ha === null).map(f => f.faz) };
  const cont = (k) => { const m = {}; fz.forEach(f => { const t = f[k] || 'sem registro'; m[t] = (m[t] || 0) + 1; }); return Object.keys(m).map(t => ({ t, n: m[t] })); };
  const estados = cont('estado'), planos = cont('plano'), orcamentos = cont('orcamento');
  const sol = { enviadas: fz.filter(f => f.sol).length, de: fz.length };
  const linhas = [], por = {}, inc = [];
  fz.forEach(f => { if (!f.demanda) { inc.push(f.faz); return; }
    f.demanda.forEach(d => { const q = Number(d.qtd); if (!(q > 0)) return;
      linhas.push({ faz: f.faz, saf: f.saf, talhao: d.talhao || '', ciclo: d.ciclo || '', insumo: d.insumo, un: d.un, qtd: q, destino: d.destino || '' });
      const k = d.insumo + '\u0001' + d.un; const p = por[k] || (por[k] = { insumo: d.insumo, un: d.un, qtd: 0, fazendas: [] });
      p.qtd = sgSoma(p.qtd, q); if (p.fazendas.indexOf(f.faz) < 0) p.fazendas.push(f.faz); }); });
  const parcial = estados.length > 1 || planos.length > 1 || orcamentos.length > 1 || (sol.enviadas > 0 && sol.enviadas < sol.de) || !area.completa || inc.length > 0;
  return { mae: grupo.mae, nome: grupo.nome, fazendas: fz.map(f => { const o = Object.assign({}, f); delete o.demanda; return o; }), area, estados, planos, orcamentos, sol,
    parcial, demanda: { linhas, porInsumo: Object.keys(por).map(k => por[k]), incompleta: inc } };
}

// envio da demanda de todas as fazendas: uma solicitação por sub-safra, pelo comando que já existe (enviarUm). A chave do comando
// lembra o que deu certo: repetir não reenvia o que já foi, e só tenta de novo o que falhou. Falha parcial não vira sucesso.
// enviarUm(saf) => {ok, recibo?, erro?}
function sgEnviar(grupo, chave, rec, enviarUm) {
  rec = rec || {}; const ch = sgTxt(chave);
  if (!ch) return { ok: false, parcial: false, recibos: [], falhas: grupo.subs.map(s => ({ faz: s.faz, saf: s.id, erro: 'Comando sem chave de idempotência.' })) };
  const recibos = [], falhas = [];
  grupo.subs.forEach(s => { const k = ch + '|' + s.id;
    if (rec[k] && rec[k].ok) { recibos.push({ faz: s.faz, saf: s.id, recibo: rec[k].recibo, repetido: true }); return; }
    if (s.ro) { falhas.push({ faz: s.faz, saf: s.id, erro: 'Safra encerrada: não gera solicitações.' }); return; }
    let r; try { r = enviarUm(s.id) || {}; } catch (e) { r = { ok: false, erro: String(e && e.message || e) }; }
    if (r.ok) { rec[k] = { ok: true, recibo: r.recibo }; recibos.push({ faz: s.faz, saf: s.id, recibo: r.recibo, repetido: false }); }
    else falhas.push({ faz: s.faz, saf: s.id, erro: r.erro || 'Falha sem motivo informado.' }); });
  return { ok: !falhas.length, parcial: !!(falhas.length && recibos.length), recibos, falhas };
}
