// SAF-FAZ-2 · testes do autor (Claude) do domínio da safra com várias fazendas, sem navegador: node safra_grupo_unit.js
// Os testes de contrato do revisor ficam em arquivo próprio (safra_grupo_contrato_test.js, autoria Codex). Dados sintéticos (fixtures).
// SG_ARQ=<arquivo> roda contra outra versão do domínio (contraprova).
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(process.env.SG_ARQ || path.join(__dirname, 'safra_grupo.js'), 'utf8');
const NOMES = ['sgMaeDe', 'sgGrupo', 'sgImpedeRemover', 'sgCompor', 'sgLeitura', 'sgEnviar'];
const G = new Function(src + '\nreturn {' + NOMES.map(n => n + ': (typeof ' + n + "==='function'?" + n + ':null)').join(',') + '};')();
const FX = JSON.parse(fs.readFileSync(path.join(__dirname, 'safra_grupo_fixtures.json'), 'utf8'));
let ok = 0, falhas = 0;
const chk = (nome, f, extra) => { let c = false, x, e2; try { c = !!f(); } catch (e) { x = String(e && e.message || e); } try { e2 = extra && extra(); } catch (e) { e2 = String(e.message); }
  if (c) { ok++; console.log('OK  ' + nome); } else { falhas++; console.log('FALHOU ' + nome + (x ? ' · erro: ' + x : '') + (e2 !== undefined ? ' · ' + JSON.stringify(e2).slice(0, 600) : '')); } };
const F = (n) => { if (!G[n]) throw new Error(n + ' ausente'); return G[n]; };
const cp = (o) => JSON.parse(JSON.stringify(o));
const ids = () => { let n = 0; return (tipo, faz) => (tipo === 'mae' ? 'M' : 'n') + (++n) + (faz ? '_' + faz.split(' ')[0] : ''); };
const deps = (m) => (saf) => m[saf] || FX.deps.vazia;
const compor = (safs, ped, op) => F('sgCompor')(safs, ped, Object.assign({ rec: {}, deps: deps({}), novoId: ids() }, op || {}));

// 1 · uma fazenda: igual a hoje (uma linha, sem mãe, rascunho)
const r1 = compor(cp(FX.safs), FX.pedidos.uma_fazenda);
const n1 = r1.safs.filter(s => s.nome === 'Safra 2027/28');
chk('G1 uma fazenda: uma sub-safra, sem mãe, em rascunho; as safras de antes ficam idênticas', () => r1.ok && n1.length === 1 && !('mae' in n1[0]) && n1[0].faz === 'Santa Rita' && n1[0].estado === 'Rascunho'
  && JSON.stringify(r1.safs.slice(0, 4)) === JSON.stringify(FX.safs), () => r1);
// 2 · duas fazendas: uma sub-safra por fazenda, ligadas pela mesma mãe; fazenda repetida conta uma vez
const r2 = compor(cp(FX.safs), FX.pedidos.duas_fazendas);
const n2 = r2.safs.filter(s => s.nome === 'Safra 2027/28');
chk('G2 duas fazendas: duas sub-safras com a mesma mãe, cada uma em rascunho e com a própria fazenda', () => r2.ok && n2.length === 2 && n2[0].mae && n2[0].mae === n2[1].mae
  && n2.map(s => s.faz).join('|') === 'Santa Rita|Lagoa Grande' && n2.every(s => s.estado === 'Rascunho') && r2.recibo.subs.every(x => x.acao === 'criada'), () => r2);
const r2b = compor(cp(FX.safs), FX.pedidos.fazenda_repetida);
chk('G2b fazenda repetida (com espaços) entra uma vez', () => r2b.ok && r2b.safs.filter(s => s.nome === 'Safra 2027/28').length === 2, () => r2b.recibo);
// 3 · idempotência: o mesmo comando repetido não cria nada de novo
const rec = {}, gid = ids();
const a = F('sgCompor')(cp(FX.safs), FX.pedidos.duas_fazendas, { rec, deps: deps({}), novoId: gid });
const b = F('sgCompor')(a.safs, FX.pedidos.duas_fazendas, { rec, deps: deps({}), novoId: gid });
chk('G3 repetir o comando (mesma chave) devolve o mesmo recibo e não duplica sub-safra', () => a.ok && b.ok && b.repetido && b.safs.length === a.safs.length
  && JSON.stringify(b.recibo) === JSON.stringify(a.recibo), () => [a.safs.length, b.safs.length, b.repetido]);
// 4 · validação
const sem = compor(cp(FX.safs), FX.pedidos.sem_fazenda), inv = compor(cp(FX.safs), FX.pedidos.periodo_invertido), sch = compor(cp(FX.safs), Object.assign({}, FX.pedidos.uma_fazenda, { chave: '' }));
chk('G4 sem fazenda, período invertido e comando sem chave são recusados sem mudar nada', () => !sem.ok && sem.erros.fazendas && !inv.ok && inv.erros.fim && !sch.ok && sch.erros.chave
  && sem.safs.length === 4 && inv.safs.length === 4 && sch.safs.length === 4, () => [sem.erros, inv.erros, sch.erros]);
// 5 · editar: acrescentar fazenda a uma safra que já existe preserva o ID, o estado e o resto; a nova não herda estado
const e5 = compor(cp(FX.safs), { chave: 'k5', saf: 'S2627', nome: 'Safra 2026/27', ini: '2026-09-01', fim: '2027-08-31', fazendas: ['Santa Rita', 'Lagoa Grande'] }, { deps: deps(FX.deps) });
const sr = e5.safs.find(s => s.id === 'S2627'), lg = e5.safs.find(s => s.mae && s.id !== 'S2627');
chk('G5 acrescentar Lagoa Grande à Safra 2026/27: S2627 fica com ID e estado; a nova sub-safra nasce em rascunho, ligada pela mesma mãe', () => e5.ok && sr.estado === 'Em planejamento' && sr.mae
  && lg && lg.faz === 'Lagoa Grande' && lg.estado === 'Rascunho' && lg.mae === sr.mae && e5.safs.length === 5
  && e5.safs.findIndex(s => s.id === 'S2627') + 1 === e5.safs.findIndex(s => s.id === lg.id), () => e5);
// 6 · remover fazenda com vínculo é recusado por inteiro, com motivo e destino
const e6 = compor(e5.safs, { chave: 'k6', saf: lg.id, nome: 'Safra 2026/27', ini: '2026-09-01', fim: '2027-08-31', fazendas: ['Lagoa Grande'] }, { deps: deps(FX.deps) });
chk('G6 tirar Santa Rita (9 cultivos, SOL-2026-07, OS-0417 e OS-0420) é recusado; nada muda; cada motivo diz onde resolver', () => !e6.ok && e6.bloqueios.length === 1
  && e6.bloqueios[0].saf === 'S2627' && e6.bloqueios[0].motivos.length === 3 && e6.bloqueios[0].motivos.every(m => m.destino)
  && JSON.stringify(e6.safs) === JSON.stringify(e5.safs), () => e6.bloqueios);
// 7 · remover fazenda vazia é aceito; voltando a uma fazenda, a safra deixa de ter mãe
const e7 = compor(e5.safs, { chave: 'k7', saf: 'S2627', nome: 'Safra 2026/27', ini: '2026-09-01', fim: '2027-08-31', fazendas: ['Santa Rita'] }, { deps: deps(FX.deps) });
const sr7 = e7.safs.find(s => s.id === 'S2627');
chk('G7 tirar a fazenda vazia: a sub-safra sai, S2627 volta a ser safra de uma fazenda (sem mãe), com o mesmo ID e estado', () => e7.ok && e7.safs.length === 4 && !('mae' in sr7)
  && sr7.estado === 'Em planejamento' && e7.recibo.subs.some(x => x.acao === 'removida' && x.faz === 'Lagoa Grande'), () => e7);
// 8 · trocar a fazenda de uma safra vazia: o ID continua (a safra aberta continua a mesma), o estado volta a rascunho
const base8 = compor(cp(FX.safs), FX.pedidos.uma_fazenda).safs; const id8 = base8[4].id;
const e8 = compor(base8.map(s => s.id === id8 ? Object.assign({}, s, { estado: 'Em planejamento' }) : s), { chave: 'k8', saf: id8, nome: 'Safra 2027/28', ini: '2027-09-01', fim: '2028-08-31', fazendas: ['Lagoa Grande'] });
const s8 = e8.safs.find(s => s.id === id8);
chk('G8 trocar Santa Rita por Lagoa Grande numa safra vazia: mesmo ID, fazenda nova, rascunho (sem herdar estado)', () => e8.ok && s8 && s8.faz === 'Lagoa Grande' && s8.estado === 'Rascunho'
  && e8.recibo.subs[0].acao === 'trocada' && e8.recibo.subs[0].de === 'Santa Rita', () => e8);
// 9 · aprovação: plano aprovado impede tirar a fazenda; safra encerrada não se edita
const e9 = compor(e5.safs, { chave: 'k9', saf: 'S2627', nome: 'Safra 2026/27', ini: '2026-09-01', fim: '2027-08-31', fazendas: ['Santa Rita'] }, { deps: (s) => s === lg.id ? FX.deps.aprovada : FX.deps.vazia });
const e9b = compor(cp(FX.safs), { chave: 'k9b', saf: 'S2526', nome: 'Safra 2025/26', ini: '2025-09-01', fim: '2026-08-31', fazendas: ['Santa Rita', 'Lagoa Grande'] });
chk('G9 plano aprovado na fazenda impede tirá-la; safra encerrada recusa edição', () => !e9.ok && /Plano operacional aprovado/.test(e9.bloqueios[0].motivos[0].t) && !e9b.ok && e9b.erros.saf, () => [e9.bloqueios, e9b.erros]);
// 10 · leitura reunida: estados por fazenda, parcial, sem "Aprovado" geral; soma só da mesma unidade; linha guarda fazenda e destino
const g10 = { mae: 'M1', nome: 'Safra 2027/28', subs: [{ id: 'A', faz: 'Santa Rita' }, { id: 'B', faz: 'Lagoa Grande' }] };
const L = F('sgLeitura')(g10, FX.leitura.uma_aprovada_outra_pendente);
const gl = (un) => L.demanda.porInsumo.find(p => p.insumo === 'Glifosato 480' && p.un === un);
chk('G10 uma fazenda aprovada e outra pendente: contagem por estado, parcial, nenhum campo de aprovação geral', () => L.parcial && JSON.stringify(L.planos) === JSON.stringify([{ t: 'Aprovado', n: 1 }, { t: 'Pendente', n: 1 }])
  && !('aprovado' in L) && !('estado' in L) && L.fazendas[0].plano === 'Aprovado' && L.fazendas[1].plano === 'Pendente' && L.sol.enviadas === 1 && L.sol.de === 2, () => L);
chk('G10b área 160 + 75,11 = 235,11 ha; Glifosato em L soma as duas fazendas (470,25 L) e em kg fica à parte (10 kg)', () => L.area.ha === 235.11 && L.area.completa
  && gl('L').qtd === 470.25 && gl('L').fazendas.length === 2 && gl('kg').qtd === 10 && gl('kg').fazendas.join() === 'Lagoa Grande', () => [L.area, L.demanda.porInsumo]);
chk('G10c a mesma demanda em duas fazendas mantém fazenda, talhão, ciclo e destino de entrega por linha', () => L.demanda.linhas.filter(l => l.insumo === 'Glifosato 480' && l.un === 'L').map(l => l.faz + '>' + l.destino + '>' + l.talhao).join('|')
  === 'Santa Rita>Almoxarifado Santa Rita>T1-A|Lagoa Grande>Almoxarifado Lagoa Grande>Pivô 19', () => L.demanda.linhas);
// 11 · falta de dado não vira zero
const L2 = F('sgLeitura')(g10, FX.leitura.area_desconhecida);
chk('G11 área desconhecida numa fazenda: total só do conhecido, marcado incompleto, com a fazenda que falta; demanda sem dado fica incompleta', () => L2.area.ha === 160 && !L2.area.completa
  && L2.area.faltam.join() === 'Lagoa Grande' && L2.demanda.incompleta.join() === 'Lagoa Grande' && L2.parcial, () => [L2.area, L2.demanda]);
// 12 · envio: falha no segundo, repetição só tenta o que falhou; nada duplica
let chamadas = {}, falhaB = true; const um = (saf) => { chamadas[saf] = (chamadas[saf] || 0) + 1; if (saf === 'B' && falhaB) return { ok: false, erro: 'navegador sem armazenamento' }; return { ok: true, recibo: 'SOL-' + saf }; };
const recE = {};
const v1 = F('sgEnviar')(g10, 'env-1', recE, um);
chk('G12 falha no segundo envio: resultado parcial, sem sucesso integral; o primeiro tem recibo', () => !v1.ok && v1.parcial && v1.recibos.length === 1 && v1.recibos[0].saf === 'A' && v1.falhas[0].saf === 'B', () => v1);
falhaB = false; const v2 = F('sgEnviar')(g10, 'env-1', recE, um);
chk('G12b repetir com a mesma chave: só a fazenda que falhou é enviada; a outra reaproveita o recibo', () => v2.ok && !v2.parcial && chamadas.A === 1 && chamadas.B === 2
  && v2.recibos.find(r => r.saf === 'A').repetido && !v2.recibos.find(r => r.saf === 'B').repetido, () => [v2, chamadas]);
const v3 = F('sgEnviar')(g10, 'env-1', recE, um);
chk('G12c repetir de novo depois de tudo enviado não chama o envio', () => v3.ok && chamadas.A === 1 && chamadas.B === 2 && v3.recibos.every(r => r.repetido), () => chamadas);
const v4 = F('sgEnviar')(g10, '', {}, um);
chk('G13 envio sem chave é recusado para todas as fazendas, sem chamar o envio', () => !v4.ok && v4.falhas.length === 2 && chamadas.A === 1, () => v4);
// 14 · grupo e mãe
const g14 = F('sgGrupo')(e5.safs, lg.id), g14b = F('sgGrupo')(cp(FX.safs), 'S27SF');
chk('G14 o grupo de qualquer sub-safra traz as duas fazendas; safra de uma fazenda é um grupo de uma, sem mãe', () => g14.subs.map(s => s.faz).join('|') === 'Santa Rita|Lagoa Grande' && g14.mae === sr.mae
  && g14b.subs.length === 1 && g14b.mae === null && F('sgMaeDe')(e5.safs, sr.mae) === sr.mae, () => [g14, g14b]);
// 15–17 · achados do revisor (Codex 6174603770): data civil, área vazia e quantidade desconhecida
const d15 = compor(cp(FX.safs), Object.assign({}, FX.pedidos.duas_fazendas, { ini: '2027-02-31' }));
chk('G15 31/02 é recusado (data civil), sem criar safra', () => !d15.ok && d15.erros.ini && d15.safs.length === 4, () => d15.erros);
const L15 = F('sgLeitura')(g10, { A: { area_ha: 160, demanda: [] }, B: { area_ha: '', demanda: [] } }), L15z = F('sgLeitura')(g10, { A: { area_ha: 0, demanda: [] }, B: { area_ha: '  ', demanda: [] } });
chk('G16 área vazia é desconhecida (não vira zero): total incompleto com a fazenda que falta; zero informado continua zero', () => L15.fazendas[1].area_ha === null && !L15.area.completa
  && L15.area.faltam.join() === 'Lagoa Grande' && L15z.fazendas[0].area_ha === 0 && L15z.fazendas[1].area_ha === null, () => [L15.area, L15z.fazendas]);
const i17 = cp(FX.leitura.uma_aprovada_outra_pendente); i17.B.demanda[0].qtd = null; i17.A.demanda.push({ insumo: 'Ureia', un: 'kg', qtd: 0, talhao: 'T1-A', destino: 'Almoxarifado Santa Rita' });
const L17 = F('sgLeitura')(g10, i17);
chk('G17 quantidade nula marca a fazenda incompleta e mantém as outras linhas; quantidade zero não marca nem vira linha', () => L17.demanda.incompleta.join() === 'Lagoa Grande'
  && L17.demanda.linhas.some(l => l.faz === 'Lagoa Grande' && l.un === 'kg') && !L17.demanda.linhas.some(l => l.insumo === 'Ureia') && L17.parcial, () => L17.demanda);
console.log(`TOTAL ${ok + falhas} · OK ${ok} · FALHAS ${falhas}`);
process.exit(falhas ? 1 : 0);
