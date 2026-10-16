// ===== Documentos para crédito: o vínculo entre o cadastro da fazenda (CD-01) e o Crédito (GE-08 › Documentos para crédito) =====
// CAD-02 (proprietário, 16/10/2026: "documentos para credito podemos deixar tudo separado em outro lugar"): CAR, matrícula, módulos fiscais
// e contrato de arrendamento saíram do formulário da fazenda e vivem no Crédito. Fonte única do vínculo (revisão do Codex 6220145128, S2):
// - a fazenda é identificada pelo id estável do cadastro (SR, BV, LG ou o id da fazenda criada no CD-01), nunca pelo nome;
// - credMigrar(): migração idempotente do cadastro salvo antes da mudança (talhao-os-cd01-v1 com car, matr, mf, arrend, custo e pend).
//   Copia para o Crédito só o documento que o Crédito ainda não tem (o que já foi editado lá fica) e depois tira os campos do cadastro.
//   Grava primeiro o Crédito e só então o cadastro: se cair no meio, a próxima chamada termina sem duplicar nem sobrescrever;
// - credFazendas() e credDocs(): o Crédito segue o cadastro atual (nome, posse, fim do contrato e fazendas criadas) e guarda só o que
//   foi migrado ou editado nele (safrion-credito-docs-v1, por id do documento).
// - documento automático (id "dc_…": CAR, matrícula e contrato de cada fazenda, e os do seed) tem tipo e fazenda fixos: o formulário os
//   mostra só para leitura e credSalvarDoc recusa a mudança, mesmo chamado direto (revisão do Codex 6221423767, S2). Documento incluído
//   pela pessoa tem id próprio e continua editável. Transferir documento entre fazendas fica fora (decisão de produto);
// - gravar devolve "" ou o motivo; o GE-08 grava no ponto transacional do motor (g2persist): falhou, nada é confirmado e o formulário
//   volta com o rascunho (como no cad_gravacao_falha).
// Usado pelo CD-01, pelo CD-01det (migram antes de ler o cadastro) e pelo GE-08 (migra, monta as linhas e grava as edições).
const CRED_CADKEY = 'talhao-os-cd01-v1', CRED_DKEY = 'safrion-credito-docs-v1';
const CRED_LEG = ['car', 'matr', 'mf', 'arrend', 'custo', 'pend'], CRED_LIXO = ['kml', 'perim', 'ambs', 'aguas'];   // LIXO: textos só de leitura que repetiam as abas
function credLer() { try { const s = JSON.parse(localStorage.getItem(CRED_DKEY) || 'null'); if (s && typeof s === 'object' && s.ed && typeof s.ed === 'object') return s; } catch (e) {} return { v: 1, ed: {} }; }
function credGravar(ds) { try { localStorage.setItem(CRED_DKEY, JSON.stringify(ds)); return ''; }
  catch (e) { return 'o navegador não gravou o documento (' + ((e && e.name && e.name !== 'Error') ? e.name : (e && e.message) || 'erro') + ').'; } }
function credAuto(id) { return /^dc_/.test(String(id || '')); }
const CRED_TIPO = { car: 'CAR', mat: 'Matrícula', arr: 'Contrato de arrendamento' };
// identidade do documento automático: tipo e fazenda (id estável) pelo id; os do seed pelo próprio seed
function credIdent(id, seedDocs) { const m = String(id || '').match(/^dc_(car|mat|arr)_(.+)$/); if (m) return { tipo: CRED_TIPO[m[1]], fid: m[2] };
  const d = (seedDocs || []).find(x => x.id === id); return d ? { tipo: d.tipo, fid: d.fid || '', tit: d.fid ? '' : (d.tit || '') } : null; }
// campos que o formulário antigo do CD-01 tinha, por documento (a mesma regra para migrar e para mostrar o que ainda não migrou)
function credLegPatches(f) { const V = f && f.v; const p = {}; if (!V) return p;
  const put = (id, o) => { const x = {}; Object.keys(o).forEach(k => { if (o[k] !== undefined && o[k] !== null) x[k] = o[k]; }); if (Object.keys(x).length) p[id] = Object.assign(p[id] || { fid: f.id }, x); };
  if ('car' in V || 'mf' in V) put('dc_car_' + f.id, { num: V.car, mf: V.mf });
  if ('matr' in V) put('dc_mat_' + f.id, { num: V.matr });
  if (credArr(V) && ('arrend' in V || 'custo' in V || 'pend' in V)) put('dc_arr_' + f.id, { num: V.arrend, custo: V.custo, pend: V.pend });
  else if (V.pend) put('dc_mat_' + f.id, { pend: V.pend });   // sem contrato, a pendência dos documentos vai para a matrícula
  return p; }
function credCad() { try { const cs = JSON.parse(localStorage.getItem(CRED_CADKEY) || 'null'); return (cs && Array.isArray(cs.faz)) ? cs : null; } catch (e) { return null; } }
function credArr(V) { return !!(V && V.posse && V.posse !== 'Própria'); }
function credMigrar() {
  const cs = credCad(); if (!cs) return false;
  const ks = CRED_LEG.concat(CRED_LIXO); const ds = credLer(); let tem = false;
  cs.faz.forEach(f => { const V = f && f.v; if (!V || !ks.some(k => k in V)) return; tem = true;
    const p = credLegPatches(f); Object.keys(p).forEach(id => { if (!ds.ed[id]) ds.ed[id] = Object.assign(p[id], { mig: 1 }); }); });
  if (!tem) return false;
  if (credGravar(ds)) return false;   // sem gravar o Crédito, o cadastro fica como está: nada se perde (credDocs ainda mostra o valor antigo)
  cs.faz.forEach(f => { if (f && f.v) ks.forEach(k => { delete f.v[k]; }); });
  try { localStorage.setItem(CRED_CADKEY, JSON.stringify(cs)); } catch (e) {}
  return true; }
// fazendas do cadastro atual: as salvas no navegador (na ordem do cadastro) e as do seed que o salvo ainda não tem
function credFazendas(seed) {
  let cs = null; try { cs = JSON.parse(localStorage.getItem(CRED_CADKEY) || 'null'); } catch (e) {}
  const out = []; const add = (id, V) => { if (!id || out.some(x => x.id === id)) return; out.push({ id: id, nome: V.nome || '', posse: V.posse || '', fim: V.fim || '', sit: V.sit || '' }); };
  ((cs && Array.isArray(cs.faz)) ? cs.faz : []).forEach(f => { if (f && f.v) add(f.id, f.v); });
  (seed || []).forEach(f => add(f.id, f)); return out; }
// documentos: CAR e matrícula de cada fazenda ativa e o contrato de quem não tem posse própria; os outros do seed (certidão do CRE-0102);
// os incluídos no Crédito. Valor = padrão < seed < migrado ou editado (ed). O titular de documento de fazenda é o nome atual dela (fid);
// a validade do contrato segue o fim do contrato do cadastro enquanto ninguém a editou no Crédito
function credDocs(fzs, seedDocs) {
  const ed = credLer().ed; const out = []; const visto = {};
  // o que o cadastro ainda guarda do formulário antigo (migração que não gravou): aparece por baixo do que o Crédito gravou
  const leg = {}; const cs = credCad(); ((cs && cs.faz) || []).forEach(f => Object.assign(leg, credLegPatches(f)));
  const base = id => (seedDocs || []).find(d => d.id === id) || {};
  const put = (id, def, segue) => { if (visto[id]) return; visto[id] = 1; const e = ed[id] || {}, l = ed[id] ? {} : (leg[id] || {});
    const v = Object.assign({}, def, base(id), l, e); Object.keys(segue || {}).forEach(k => { if (!(k in e) && !(k in l)) v[k] = segue[k]; }); out.push({ id: id, v: v }); };
  fzs.forEach(f => { if (f.sit === 'Inativa') return;
    put('dc_car_' + f.id, { tipo: 'CAR', fid: f.id, num: '', val: '', exig: '', mf: '', pend: '' });
    put('dc_mat_' + f.id, { tipo: 'Matrícula', fid: f.id, num: '', val: '', exig: '', pend: '' });
    if (credArr(f)) put('dc_arr_' + f.id, { tipo: 'Contrato de arrendamento', fid: f.id, num: '', val: '', exig: '', custo: '', pend: '' }, { val: f.fim || '' }); });
  (seedDocs || []).forEach(d => { if (!/^dc_(car|mat|arr)_/.test(d.id)) put(d.id, {}); });
  Object.keys(ed).forEach(id => put(id, { tipo: 'Outro', num: '', val: '', exig: '', pend: '' }));
  out.forEach(r => { const f = r.v.fid ? fzs.find(x => x.id === r.v.fid) : null; if (f && f.nome) r.v.tit = f.nome; });
  return out; }
// grava a edição de um documento no Crédito, por id; devolve "" ou o motivo (nada gravado).
// Automático: tipo e fazenda vêm da identidade (id), e a mudança deles é recusada. Incluído pela pessoa: fazenda pelo id estável ou parceiro pelo nome
const CRED_FIXO = 'Documento automático da fazenda: o tipo e a fazenda não mudam. Para outro documento, use "Incluir documento".';
function credSalvarDoc(r, fzs, seedDocs) {
  const V = (r && r.v) || {}; const f = (fzs || []).find(x => x.nome === V.tit);
  const o = { tipo: V.tipo || '', num: V.num || '', val: V.val || '', pend: V.pend || '', exig: V.exig || '' };
  if (credAuto(r && r.id)) { const I = credIdent(r.id, seedDocs); if (!I) return 'documento automático desconhecido (' + r.id + ').';
    const fid = f ? f.id : ''; if (o.tipo !== I.tipo || (I.fid ? fid !== I.fid : (V.tit || '') !== (I.tit || ''))) return CRED_FIXO;
    if (I.fid) o.fid = I.fid; else o.tit = I.tit || ''; }
  else if (f) o.fid = f.id; else o.tit = V.tit || '';
  if (o.tipo === 'CAR') o.mf = (V.mf === undefined || V.mf === null) ? '' : V.mf;
  if (o.tipo === 'Contrato de arrendamento') o.custo = (V.custo === undefined || V.custo === null) ? '' : V.custo;
  const ds = credLer(); ds.ed[r.id] = o; return credGravar(ds); }
