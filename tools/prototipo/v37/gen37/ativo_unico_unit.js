// ATIVO-UNICO · gravação do CD-03 com a versão lida (Codex 6252809331, S2), sem navegador: as funções reais de areas/cad_culturas.py (CAD_LS_JS)
// e areas/cad_ativos_pessoas.py (c3atvIni, c3grava e auxiliares), duas telas sintéticas e um armazenamento comum. Dados sintéticos.
// Uso: node ativo_unico_unit.js   (ATV_SRC=<outro cad_ativos_pessoas.py> para a contraprova)
const fs = require('node:fs'), vm = require('node:vm'), A = require('node:assert/strict'), path = require('node:path');
const pyCul = fs.readFileSync(path.join(__dirname, 'areas/cad_culturas.py'), 'utf8');
const pyAtv = fs.readFileSync(process.env.ATV_SRC || path.join(__dirname, 'areas/cad_ativos_pessoas.py'), 'utf8');
const LS_JS = /CAD_LS_JS=r'''([\s\S]*?)'''/.exec(pyCul)[1];
function fn(src, nome) { const i = src.indexOf('function ' + nome + '('); if (i < 0) return ''; let d = 0, j = src.indexOf('{', i);
  for (; j < src.length; j++) { if (src[j] === '{') d++; else if (src[j] === '}' && --d === 0) break; } return src.slice(i, j + 1); }
const C3 = ['c3lista', 'c3poe', 'c3atvIni', 'c3junta', 'c3grava'].map(n => fn(pyAtv, n)).join('\n');
let ok = 0, fail = 0;
function test(nome, f) { try { f(); ok++; console.log('OK   ' + nome); } catch (e) { fail++; console.log('FALHA ' + nome + ' :: ' + e.message); } }
const at = (id, nome, extra) => ({ id, v: Object.assign({ nome, classe: 'Trator', modelo: 'M', local: 'Sede', sit: 'Ativo' }, extra || {}) });
function mundo(disco) {
  const c = { console, setTimeout: f => f(), JSON }; vm.createContext(c);
  vm.runInContext(`const store={}; const localStorage={getItem:k=>store[k]===undefined?null:store[k],setItem:(k,v)=>{store[k]=String(v)}};
    function RW(self,g){ return ((self.state.g2||{})[g]||{}).rows||[]; }
    function GR(g){ return {edit:{fields:[{k:'nome'},{k:'classe'},{k:'modelo'},{k:'local'},{k:'sit'}]}}; }
    ${LS_JS}\n${C3}`, c);
  c.run = js => vm.runInContext(js, c);
  if (disco) c.run(`localStorage.setItem(CAD_LS, ${JSON.stringify(JSON.stringify({ ativos: disco }))})`);
  c.tela = (semente) => { const nome = 't' + Math.random().toString(36).slice(2); c.run(`var ${nome}={state:{g2:{g_atv:{rows:${JSON.stringify((semente || []).map(a => Object.assign({ s: {}, p: {} }, a)))}}}},setState(p){Object.assign(this.state,p)}}; c3atvIni(${nome});`); return nome; };
  c.lista = () => (JSON.parse(c.run(`localStorage.getItem(CAD_LS)`) || '{}').ativos || []);
  return c;
}
const nomes = L => L.map(a => a.v.nome).join(',');

test('U1 contraexemplo do Codex: B cria b, a tela antiga A renomeia a; b continua no cadastro (e não fica inativo na Manutenção)', () => {
  const c = mundo([at('a', 'Trator A')]); const A1 = c.tela(), B1 = c.tela();
  c.run(`${B1}.state.g2.g_atv.rows.push({id:'b',v:${JSON.stringify(at('b', 'Trator B').v)},s:{},p:{}})`); A.equal(c.run(`c3grava(${B1})`), '');
  A.equal(nomes(c.lista()), 'Trator A,Trator B');
  c.run(`${A1}.state.g2.g_atv.rows[0].v.nome='Trator A1'`); A.equal(c.run(`c3grava(${A1})`), '');
  A.equal(nomes(c.lista()), 'Trator A1,Trator B'); A.equal(c.run(`${A1}.state.g2.g_atv.rows.map(r=>r.id).join()`), 'a,b', 'a tela A passa a mostrar o b');
});
test('U2 duas edições do mesmo ativo: a segunda é recusada com o motivo; o salvo fica e o rascunho de A continua', () => {
  const c = mundo([at('a', 'Trator A')]); const A1 = c.tela(), B1 = c.tela();
  c.run(`${B1}.state.g2.g_atv.rows[0].v.nome='Trator X'`); A.equal(c.run(`c3grava(${B1})`), '');
  c.run(`${A1}.state.g2.g_atv.rows[0].v.nome='Trator Y'`); const e = c.run(`c3grava(${A1})`);
  A.match(e, /outra tela alterou Trator Y/); A.equal(nomes(c.lista()), 'Trator X'); A.equal(c.run(`${A1}.state.g2.g_atv.rows[0].v.nome`), 'Trator Y');
});
test('U3 campo calculado na tela (capacidade, conjuntos) não conta como mudança: a renomeação da outra tela fica', () => {
  const c = mundo([at('a', 'Trator A'), at('b', 'Trator B')]); const A1 = c.tela(), B1 = c.tela();
  c.run(`${B1}.state.g2.g_atv.rows[1].v.nome='Trator B2'`); A.equal(c.run(`c3grava(${B1})`), '');
  c.run(`${A1}.state.g2.g_atv.rows.forEach(r=>{ r.v.ncj=3; r.v.capn=120; })`); A.equal(c.run(`c3grava(${A1})`), '');
  A.equal(nomes(c.lista()), 'Trator A,Trator B2');
});
test('U4 excluído na outra tela e sem mudança aqui: sai daqui também; excluído aqui e mudado lá: recusa', () => {
  const c = mundo([at('a', 'Trator A'), at('b', 'Trator B')]); const A1 = c.tela(), B1 = c.tela();
  c.run(`${B1}.state.g2.g_atv.rows.splice(1,1)`); A.equal(c.run(`c3grava(${B1})`), ''); A.equal(c.run(`c3grava(${A1})`), '');
  A.equal(nomes(c.lista()), 'Trator A'); A.equal(c.run(`${A1}.state.g2.g_atv.rows.length`), 1);
  const d = mundo([at('a', 'Trator A')]); const A2 = d.tela(), B2 = d.tela();
  d.run(`${B2}.state.g2.g_atv.rows[0].v.sit='Inativo'`); A.equal(d.run(`c3grava(${B2})`), '');
  d.run(`${A2}.state.g2.g_atv.rows.splice(0,1)`); A.match(d.run(`c3grava(${A2})`), /outra tela alterou/); A.equal(d.lista()[0].v.sit, 'Inativo');
});
test('U5 primeira gravação (cadastro vazio, semente): A e B abrem da semente; B renomeia, A cria c; nada se perde', () => {
  const c = mundo(null); const sem = [at('a', 'Trator A')]; const A1 = c.tela(sem), B1 = c.tela(sem);
  c.run(`${B1}.state.g2.g_atv.rows[0].v.nome='Trator A2'`); A.equal(c.run(`c3grava(${B1})`), '');
  c.run(`${A1}.state.g2.g_atv.rows.push({id:'c',v:${JSON.stringify(at('c', 'Trator C').v)},s:{},p:{}})`); A.equal(c.run(`c3grava(${A1})`), '');
  A.equal(nomes(c.lista()), 'Trator A2,Trator C');
});
test('U6 sem outra tela: grava normal e repetir não regrava (mesmo comportamento de antes)', () => {
  const c = mundo([at('a', 'Trator A')]); const A1 = c.tela(); c.run(`${A1}.state.g2.g_atv.rows[0].v.modelo='M2'`);
  A.equal(c.run(`c3grava(${A1})`), ''); A.equal(c.lista()[0].v.modelo, 'M2'); A.equal(c.run(`c3grava(${A1})`), '');
});
console.log(`RESULTADO: ${ok}/${ok + fail} ok`); process.exit(fail ? 1 : 0);
