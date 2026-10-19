'use strict';
const assert = require('node:assert/strict');
const {analisar} = require('./raiox_comparacao.js');
const dia = d => `2026-01-${String(d).padStart(2, '0')}T12:00:00.000Z`;
const escopo = {org: 'demo', fazenda: 'F1', cultivo: 'C1', safra: 'S1', alvo: 'A1'};
const contexto = {...escopo, corte: dia(20)};
const p = {id: 'fixture', versao: 1, origem: 'demonstrativo', publicadoEm: dia(1), protocolo: 'P@1', unidade: 'alvos/ponto', nc: 10, antesMaxDias: 3, depoisMinDias: 1, depoisMaxDias: 10, toleranciaDias: 2, residualDias: 2, pisoAntes: 1, diferencaRelativaAntes: 0.5, minControles: 2};
const leitura = (id, talhao, d, valor, extra = {}) => ({...escopo, id, talhao, versao: 1, evento: dia(d), disponivelEm: dia(d), precisao: 'instante', estado: 'completa', valor, protocolo: 'P@1', unidade: p.unidade, estadio: 'V1', avaliador: 'sintetico', ...extra});
const aplicacao = (id, talhao, d, extra = {}) => ({...escopo, id, talhao, versao: 1, evento: dia(d), disponivelEm: dia(d), precisao: 'instante', estado: 'confirmada', ...extra});
function fixture() { return {leituras: [leitura('a', 'T', 1, 10), leitura('b', 'T', 10, 5), leitura('a', 'C1', 1, 10), leitura('b', 'C1', 10, 10), leitura('a', 'C2', 1, 10), leitura('b', 'C2', 10, 20)], aplicacoes: [aplicacao('M', 'T', 2)]}; }
const pedido = {aplicacao: {id: 'M', talhao: 'T'}, antes: {id: 'a', talhao: 'T'}, depois: {id: 'b', talhao: 'T'}, controles: [{talhao: 'C1', antes: 'a', depois: 'b'}, {talhao: 'C2', antes: 'a', depois: 'b'}]};
const executar = (d = fixture(), c = contexto, ps = p, req = pedido) => analisar(d, c, ps, req);
let passou = 0;
function teste(nome, fn) { fn(); passou++; console.log('PASS ' + nome); }
function mudar(id, talhao, delta) { const d = fixture(); Object.assign(d.leituras.find(x => x.id === id && x.talhao === talhao), delta); return d; }
teste('HT por controle sem inventar agregação ou causalidade', () => {
  const r = executar(); assert.equal(r.comparacao.estado, 'agregacao_pendente'); assert.equal(r.comparacao.variacao, null);
  assert.deepEqual(r.comparacao.controles.map(c => c.variacao), [0.5, 0.75]); assert.equal(r.seguimento.estado, 'S3'); assert.equal(r.seguimento.observadoAte, dia(10));
});
teste('controle futuro não fornece comparação até D; contraprova D10/D12', () => {
  const d = fixture(); for (const x of d.leituras.filter(x => x.talhao !== 'T' && x.id === 'b')) { x.evento = dia(12); x.disponivelEm = dia(12); }
  const r = executar(d, {...contexto, corte: dia(10)}); assert.equal(r.comparacao.quantidadeElegivel, 0);
  for (const x of d.leituras.filter(x => x.talhao !== 'T' && x.id === 'b')) x.valor = 30;
  assert.deepEqual(executar(d, {...contexto, corte: dia(10)}), r); assert.equal(executar(d, {...contexto, corte: dia(12)}).comparacao.quantidadeElegivel, 2);
});
teste('versões e identidades futuras invisíveis em todas as saídas', () => {
  const d = fixture(), antes = executar(d);
  d.leituras.push(leitura('b', 'T', 10, 1000, {versao: 2, disponivelEm: dia(21)}), leitura('futuro', 'T', 15, null, {disponivelEm: dia(21)}));
  d.aplicacoes.push(aplicacao('extra', 'T', 12, {disponivelEm: dia(21)})); assert.deepEqual(executar(d), antes);
});
teste('revisão retroativa conhecida substitui; não ressuscita número antigo', () => {
  const d = fixture(); d.leituras.push(leitura('b', 'T', 10, null, {versao: 2, disponivelEm: dia(15)}));
  assert.equal(executar(d).comparacao.motivo, 'valor_ausente_ou_invalido'); assert.equal(executar(d, {...contexto, corte: dia(12)}).comparacao.quantidadeElegivel, 2);
});
teste('isolamento por todos os componentes do contexto', () => {
  for (const k of Object.keys(escopo)) { const d = fixture(); d.leituras.push(leitura('b', 'T', 10, 999, {[k]: 'outro', versao: 3, disponivelEm: dia(19)})); assert.deepEqual(executar(d), executar()); }
});
teste('ausência e parcial nunca equivalem a zero', () => {
  for (const valor of [null, undefined, '', '0', NaN, Infinity, -1]) assert.equal(executar(mudar('b', 'T', {valor})).comparacao.motivo, 'valor_ausente_ou_invalido');
  assert.equal(executar(mudar('b', 'T', {estado: 'parcial'})).comparacao.motivo, 'leitura_incompleta');
});
teste('zero antes é estrutural; zero depois do tratado é observado', () => {
  assert.equal(executar(mudar('a', 'T', {valor: 0})).comparacao.motivo, 'tratado_zerado_antes');
  const r = executar(mudar('b', 'T', {valor: 0})); assert.equal(r.comparacao.zeroObservadoDepois, true); assert.deepEqual(r.comparacao.controles.map(c => c.variacao), [1, 1]);
});
teste('zeros de controle não ganham epsilon', () => {
  assert.equal(executar(mudar('a', 'C1', {valor: 0})).comparacao.controles[0].motivo, 'controle_zerado_antes');
  assert.equal(executar(mudar('b', 'C1', {valor: 0})).comparacao.controles[0].motivo, 'controle_zerado_depois');
});
teste('mesmo piso do tratado e controle; sem suavização', () => {
  assert.equal(executar(mudar('a', 'T', {valor: 0.5})).comparacao.motivo, 'tratado_abaixo_do_piso');
  assert.equal(executar(mudar('a', 'C1', {valor: 0.5})).comparacao.controles[0].motivo, 'controle_abaixo_do_piso');
});
teste('efeito negativo não truncado em zero', () => assert.equal(executar(mudar('b', 'T', {valor: 30})).comparacao.controles[0].variacao, -2));
teste('sem antes não usa Abbott; seguimento permanece independente', () => { const d = fixture(); d.leituras = d.leituras.filter(x => !(x.talhao === 'T' && x.id === 'a')); const r = executar(d); assert.equal(r.comparacao.estado, 'indisponivel'); assert.equal(r.seguimento.estado, 'S3'); });
teste('janelas, estágio, nível inicial e tolerância não têm fallback', () => {
  assert.equal(executar(mudar('a', 'C1', {estadio: 'R1'})).comparacao.controles[0].motivo, 'estadio_incompativel');
  assert.equal(executar(mudar('a', 'C1', {valor: 20})).comparacao.controles[0].motivo, 'nivel_inicial_incompativel');
  assert.equal(executar(mudar('b', 'C1', {evento: dia(13), disponivelEm: dia(13)})).comparacao.controles[0].motivo, 'controle_fora_da_tolerancia');
  assert.equal(executar(mudar('b', 'T', {evento: dia(15), disponivelEm: dia(15)})).comparacao.motivo, 'leitura_fora_da_janela');
});
teste('controle repetido não aumenta n e tratado não vira controle', () => {
  const r = executar(fixture(), contexto, p, {...pedido, controles: [...pedido.controles, pedido.controles[0], {talhao: 'T', antes: 'a', depois: 'b'}]});
  assert.equal(r.comparacao.quantidadeElegivel, 1); assert.equal(r.comparacao.estado, 'insuficiente');
});
teste('campanha sem controle elegível; seguimento continua', () => {
  const d = fixture(); d.aplicacoes.push(aplicacao('M', 'C1', 2), aplicacao('M', 'C2', 2)); const r = executar(d); assert.equal(r.comparacao.quantidadeElegivel, 0); assert.equal(r.seguimento.estado, 'S3');
});
teste('residual no controle exclui', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'C1', 1)); assert.equal(executar(d).comparacao.controles[0].motivo, 'interferencia_no_controle'); });
teste('nova aplicação interfere no par e encerra seguimento sem leitura', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'T', 5)); const r = executar(d); assert.equal(r.comparacao.motivo, 'interferencia_no_tratado'); assert.equal(r.seguimento.estado, 'S5a'); });
teste('nova aplicação após leitura baixa produz S5b', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'T', 12)); const r = executar(d); assert.equal(r.seguimento.estado, 'S5b'); assert.equal(r.seguimento.observadoAte, dia(10)); });
teste('retorno em intervalo entre leituras, não data inventada', () => { const d = fixture(); d.leituras.push(leitura('c', 'T', 18, 11)); const r = executar(d); assert.equal(r.seguimento.estado, 'S1'); assert.deepEqual(r.seguimento.intervalo, {depoisDe: dia(10), ate: dia(18), larguraDias: 8}); });
teste('primeiro pós acima/igual NC não demonstra retorno', () => assert.equal(executar(mudar('b', 'T', {valor: 10})).seguimento.estado, 'S2'));
teste('sem leitura S4; data de corte não vira última leitura', () => { const d = fixture(); d.leituras = d.leituras.filter(x => x.talhao !== 'T' || x.id === 'a'); assert.equal(executar(d).seguimento.estado, 'S4'); });
teste('protocolo incompatível é S6, mesmo havendo leitura compatível', () => { const d = fixture(); d.leituras.push(leitura('c', 'T', 15, 12, {protocolo: 'P@2'})); assert.equal(executar(d).seguimento.estado, 'S6'); });
teste('hora ausente não estabelece antes/depois', () => assert.equal(executar(mudar('a', 'T', {precisao: 'dia'})).comparacao.motivo, 'instante_nao_demonstrado'));
teste('leitura simultânea à próxima aplicação não atribui retorno', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'T', 18)); d.leituras.push(leitura('c', 'T', 18, 20)); assert.equal(executar(d).seguimento.estado, 'S5b'); });
teste('evento conhecido sem confirmação bloqueia ordem, sem falso seguimento', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'T', 15, {estado: 'parcial'})); assert.equal(executar(d).seguimento.motivo, 'ordem_ou_confirmacao_da_proxima_aplicacao_pendente'); });
teste('cancelamento conhecido substitui aplicação; não interfere', () => { const d = fixture(); d.aplicacoes.push(aplicacao('X', 'T', 5), aplicacao('X', 'T', 5, {versao: 2, disponivelEm: dia(8), estado: 'cancelada'})); assert.equal(executar(d).comparacao.quantidadeElegivel, 2); });
teste('duas leituras conflitantes no mesmo instante não escolhem por ID', () => { const d = fixture(); d.leituras.push(leitura('conflito', 'T', 10, 20)); assert.equal(executar(d).seguimento.motivo, 'leituras_conflitantes_no_mesmo_instante'); });
teste('data civil impossível e disponibilidade impossível são rejeitadas', () => {
  assert.equal(executar(fixture(), {...contexto, corte: '2026-02-30T12:00:00.000Z'}).estado, 'indisponivel');
  assert.equal(executar(mudar('b', 'T', {disponivelEm: dia(9)})).comparacao.motivo, 'disponibilidade_anterior_ao_evento');
});
teste('parâmetro futuro, ausente ou apresentado como RT não habilita cálculo', () => {
  for (const delta of [{publicadoEm: dia(21)}, {minControles: 0}, {pisoAntes: NaN}, {origem: 'adotado pelo RT'}]) assert.equal(executar(fixture(), contexto, {...p, ...delta}).motivo, 'contrato_invalido');
});
teste('entrada e ordem preservadas; permutações produzem mesma saída', () => {
  const d = fixture(), antes = structuredClone(d), r = executar(d); assert.deepEqual(d, antes);
  d.leituras.reverse(); d.aplicacoes.reverse(); assert.deepEqual(executar(d, contexto, p, {...pedido, controles: [...pedido.controles].reverse()}), r);
});
teste('proveniência mantém escopo completo e versão efetivamente usada', () => { const d = fixture(); d.leituras.push(leitura('b', 'T', 10, 4, {versao: 2, disponivelEm: dia(15)})); const f = executar(d).comparacao.fontes[1]; assert.equal(f.versao, 2); for (const k of Object.keys(escopo)) assert.equal(f[k], escopo[k]); });
teste('duplicidade antiga é recusada independentemente da ordem de versões', () => {
  const d = fixture(); d.leituras.push(leitura('b', 'T', 10, 4, {versao: 2, disponivelEm: dia(15)}), {...d.leituras[1]});
  const r = executar(d); assert.equal(r.motivo, 'contrato_invalido'); d.leituras.reverse(); assert.deepEqual(executar(d), r);
});
console.log(`${passou}/${passou} PASS — dados e parâmetros exclusivamente sintéticos.`);
