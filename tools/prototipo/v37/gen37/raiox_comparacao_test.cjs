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
teste('A1 controle precisa envolver o instante da aplicação', () => {
  for (const d of [2, 3]) assert.equal(executar(mudar('a', 'C1', {evento: dia(d), disponivelEm: dia(d)})).comparacao.controles[0].motivo, 'ordem_controle_invalida');
  const ps = {...p, toleranciaDias: 10};
  for (const d of [1, 2]) assert.equal(executar(mudar('b', 'C1', {evento: dia(d), disponivelEm: dia(d)}), contexto, ps).comparacao.controles[0].motivo, 'ordem_controle_invalida');
});
teste('A2 defensivo para outro alvo interfere no tratado e encerra seguimento', () => {
  const d = fixture(); d.aplicacoes.push(aplicacao('OUTRO', 'T', 5, {alvo: 'A2'})); const r = executar(d);
  assert.equal(r.comparacao.motivo, 'interferencia_no_tratado'); assert.equal(r.seguimento.estado, 'S5a'); assert.equal(r.seguimento.proximaAplicacao.alvo, 'A2');
});
teste('A2 defensivo para outro alvo também exclui controle e respeita resíduo', () => {
  const d = fixture(); d.aplicacoes.push(aplicacao('OUTRO', 'C1', 1, {alvo: 'A2'}));
  assert.equal(executar(d).comparacao.controles[0].motivo, 'interferencia_no_controle');
});
teste('A2 mesmo ID de defensivo revisado para outro alvo substitui versão', () => {
  const d = fixture(); d.aplicacoes.push(aplicacao('M', 'T', 2, {alvo: 'A2', versao: 2, disponivelEm: dia(15)}));
  assert.equal(executar(d).motivo, 'aplicacao_alvo_incompativel');
  assert.equal(executar(d, {...contexto, corte: dia(12)}).comparacao.estado, 'agregacao_pendente');
});
teste('A2 cancelamento em outro alvo substitui aplicação no universo amplo', () => {
  const d = fixture(); d.aplicacoes.push(aplicacao('OUTRO', 'T', 5, {alvo: 'A2'}), aplicacao('OUTRO', 'T', 5, {alvo: 'A2', versao: 2, estado: 'cancelada', disponivelEm: dia(8)}));
  assert.equal(executar(d).comparacao.estado, 'agregacao_pendente'); assert.equal(executar(d).seguimento.estado, 'S3');
});
teste('A2 outros alvos futuros continuam invisíveis e outras fazendas isoladas', () => {
  const d = fixture(), r = executar(d);
  d.aplicacoes.push(aplicacao('OUTRO', 'T', 5, {alvo: 'A2', disponivelEm: dia(21)}));
  assert.deepEqual(executar(d), r);
  for (const k of ['org', 'fazenda', 'cultivo', 'safra']) { d.aplicacoes.push(aplicacao('OUTRO', 'T', 5, {alvo: 'A2', [k]: 'outro'})); assert.deepEqual(executar(d), r); }
});
teste('A2 leitura de outro alvo não entra no seguimento', () => {
  const d = fixture(), r = executar(d); d.leituras.push(leitura('OUTRA', 'T', 15, 100, {alvo: 'A2'})); assert.deepEqual(executar(d), r);
});
const pAgregado = {...p, agregacao: 'mediana_razoes_talhao_v1'};
function exemploPar() {
  const d = fixture(); Object.assign(d.leituras.find(x => x.talhao === 'C1' && x.id === 'a'), {valor: 5});
  for (const x of d.leituras.filter(x => x.talhao === 'C2')) x.valor = 15;
  return d;
}
const perto = (a, b) => assert.ok(Math.abs(a - b) < 1e-12, `${a} != ${b}`);
teste('método explícito calcula contraste com mediana dos fatores, não mediana dos contrastes', () => {
  const r = executar(exemploPar(), contexto, pAgregado).comparacao;
  assert.equal(r.estado, 'disponivel'); assert.equal(r.metodo, pAgregado.agregacao); assert.equal(r.fatorControles, 1.5); perto(r.variacao, 2/3);
  assert.notEqual(r.variacao, 3/5); assert.notEqual(r.variacao, 5/8); assert.equal(r.medianaInterpolada, true);
  assert.deepEqual(r.faixaEntreControles, {minimo: 0.5, maximo: 0.75});
});
teste('n ímpar preserva fator central sem peso implícito pelo nível inicial', () => {
  const d = exemploPar(); d.leituras.push(leitura('a', 'C3', 1, 10), leitura('b', 'C3', 10, 10));
  const r = executar(d, contexto, pAgregado, {...pedido, controles: [...pedido.controles, {talhao: 'C3', antes: 'a', depois: 'b'}]}).comparacao;
  assert.equal(r.variacao, 0.5); assert.equal(r.fatorControles, 1); assert.equal(r.medianaInterpolada, false); assert.notEqual(r.variacao, 4/7);
});
teste('contraprova Gemini ajustada ao pareamento: fatores divergentes mantêm faixa visível', () => {
  const d = exemploPar(); d.leituras.find(x => x.talhao === 'T' && x.id === 'b').valor = 2;
  d.leituras.find(x => x.talhao === 'C1' && x.id === 'b').valor = 25;
  d.leituras.find(x => x.talhao === 'C2' && x.id === 'a').valor = 10;
  d.leituras.find(x => x.talhao === 'C2' && x.id === 'b').valor = 5;
  const r = executar(d, contexto, pAgregado).comparacao;
  assert.equal(r.quantidadeElegivel, 2); assert.equal(r.fatorControles, 2.75); perto(r.variacao, 51/55);
  assert.deepEqual(r.faixaEntreControles, {minimo: 0.6, maximo: 0.96}); assert.notEqual(r.variacao, 0.78);
});
teste('agregado sem mínimo ou denominador válido continua null', () => {
  const d = exemploPar(); d.leituras.find(x => x.talhao === 'C1' && x.id === 'b').valor = 0;
  const r = executar(d, contexto, pAgregado).comparacao; assert.equal(r.estado, 'insuficiente'); assert.equal(r.variacao, null); assert.equal(r.fatorControles, undefined);
  const rep = executar(exemploPar(), contexto, pAgregado, {...pedido, controles: [...pedido.controles, pedido.controles[0]]}).comparacao;
  assert.equal(rep.estado, 'insuficiente'); assert.equal(rep.variacao, null);
});
teste('zero observado e aumento continuam explícitos no agregado', () => {
  const d = exemploPar(); d.leituras.find(x => x.talhao === 'T' && x.id === 'b').valor = 0;
  let r = executar(d, contexto, pAgregado).comparacao; assert.equal(r.variacao, 1); assert.equal(r.zeroObservadoDepois, true);
  d.leituras.find(x => x.talhao === 'T' && x.id === 'b').valor = 30;
  r = executar(d, contexto, pAgregado).comparacao; assert.equal(r.variacao, -1); assert.equal(r.zeroObservadoDepois, false);
});
teste('agregado é invariante à ordem e à escala comum da unidade', () => {
  const d = exemploPar(), r = executar(d, contexto, pAgregado).comparacao;
  d.leituras.reverse(); assert.deepEqual(executar(d, contexto, pAgregado, {...pedido, controles: [...pedido.controles].reverse()}).comparacao, r);
  for (const x of d.leituras) x.valor *= 100;
  const escalado = executar(d, contexto, {...pAgregado, pisoAntes: p.pisoAntes * 100, nc: p.nc * 100}).comparacao;
  assert.equal(escalado.variacao, r.variacao); assert.deepEqual(escalado.faixaEntreControles, r.faixaEntreControles);
});
teste('método não declarado permanece pendente; nome desconhecido falha', () => {
  assert.equal(executar(exemploPar()).comparacao.estado, 'agregacao_pendente');
  assert.equal(executar(exemploPar(), contexto, {...p, agregacao: 'automatico'}).motivo, 'contrato_invalido');
});

teste('A3 residual anterior no tratado bloqueia contraste; fora da janela permanece elegível', () => {
  const instante = '2025-12-31T12:00:00.000Z';
  const d = fixture();
  d.aplicacoes.push(aplicacao('ANT', 'T', 1, {alvo: 'A2', evento: instante, disponivelEm: instante}));
  const ps = {...p, agregacao: 'mediana_razoes_talhao_v1'};
  const r = executar(d, contexto, ps);
  assert.equal(r.comparacao.motivo, 'interferencia_no_tratado');
  assert.equal(r.comparacao.estado, 'indisponivel');
  d.aplicacoes[1].evento = d.aplicacoes[1].disponivelEm = '2025-12-29T12:00:00.000Z';
  assert.equal(executar(d, contexto, ps).comparacao.estado, 'disponivel');
});

teste('precisão insuficiente não comprova ausência de interferência', () => {
  for (const talhao of ['T', 'C1']) {
    const d = fixture(); d.aplicacoes.push(aplicacao('dia', talhao, 1, {alvo:'A2', precisao:'dia', evento:'2025-12-30T00:00:00.000Z', disponivelEm:'2025-12-30T00:00:00.000Z'}));
    const r=executar(d).comparacao;
    assert.equal(talhao==='T' ? r.motivo : r.controles[0].motivo, 'precisao_do_manejo_insuficiente');
  }
});
teste('limite residual inclusivo e um milissegundo fora em ambos os talhões', () => {
  for (const talhao of ['T','C1']) for (const fora of [false,true]) {
    const d=fixture(), t=new Date(Date.parse(dia(1))-2*86400000-(fora?1:0)).toISOString();
    d.aplicacoes.push(aplicacao('borda',talhao,1,{alvo:'A2',evento:t,disponivelEm:t}));
    const r=executar(d).comparacao;
    if(fora) assert.equal(r.quantidadeElegivel,2);
    else assert.equal(talhao==='T'?r.motivo:r.controles[0].motivo,talhao==='T'?'interferencia_no_tratado':'interferencia_no_controle');
  }
});
teste('dias e meses fora do período permanecem elegíveis; sobreposição tem motivo próprio', () => {
 for(const talhao of ['T','C1']) for(const [evento,precisao,toca] of [
 ['2025-12-29','dia',false],['2025-12-22','dia',false],['2025-11-02','dia',false],
 ['2026-01-15','dia',false],['2026-01-11','dia',true],['2025-11','mes',false],
 ['2025-12-30','dia',true],['2025-12','mes',true],['2025-11','desconhecida',true],
 ['2025-11',undefined,true],['2025-11-02T00:00:00.000Z',undefined,true],['2025-12-01T00:00:00.000Z','mes',true],['2025-02-30','dia',true]]) {
  const d=fixture();d.aplicacoes.push(aplicacao('X',talhao,1,{alvo:'A2',evento,precisao}));
  const r=executar(d).comparacao;
  if(toca) assert.equal(talhao==='T'?r.motivo:r.controles[0].motivo,'precisao_do_manejo_insuficiente',evento);
  else assert.equal(r.quantidadeElegivel,2,evento);
 }
});
teste('limites civis explícitos UTC e fim exclusivo; limites inválidos não liberam',()=>{
 for(const talhao of ['T','C1']) for(const [de,ate,toca] of [
 ['2025-12-29T12:00:00.000Z','2025-12-30T12:00:00.000Z',false],
 ['2025-12-30T03:00:00.000Z','2025-12-31T03:00:00.000Z',true],
 ['2025-12-30T03:00:00.000Z','invalido',true],
 ['2026-01-11T03:00:00.000Z','2026-01-12T03:00:00.000Z',false]]) {
  const d=fixture(),evento=de.slice(0,10);d.aplicacoes.push(aplicacao('X',talhao,1,{alvo:'A2',evento,precisao:'dia',de,ate}));
  const r=executar(d).comparacao;
  if(toca)assert.equal(talhao==='T'?r.motivo:r.controles[0].motivo,'precisao_do_manejo_insuficiente');
  else assert.equal(r.quantidadeElegivel,2);
 }
});
teste('borda superior inclusiva e um milissegundo depois em tratado e controle',()=>{
 for(const talhao of ['T','C1'])for(const fora of [false,true]){
  const d=fixture(),evento=new Date(Date.parse(dia(10))+(fora?1:0)).toISOString();
  d.aplicacoes.push(aplicacao('X',talhao,10,{alvo:'A2',evento,disponivelEm:evento}));
  const r=executar(d).comparacao;
  if(fora)assert.equal(r.quantidadeElegivel,2);
  else assert.equal(talhao==='T'?r.motivo:r.controles[0].motivo,talhao==='T'?'interferencia_no_tratado':'interferencia_no_controle');
 }
});
teste('seguimento não atribui retorno quando manejo de dia ou mês pode suceder M',()=>{
 for(const [evento,precisao,bloqueia] of [['2026-01-02','dia',true],['2026-01-03','dia',true],['2026-01','mes',true],['2025-11','mes',false],['2025-11',undefined,true],['2025-11-02T00:00:00.000Z',undefined,true],['2025-12-01T00:00:00.000Z','mes',false]]){
 const d=fixture();d.leituras.push(leitura('c','T',18,11));d.aplicacoes.push(aplicacao('X','T',1,{alvo:'A2',evento,precisao}));
 const r=executar(d).seguimento;
 if(bloqueia)assert.equal(r.motivo,'ordem_ou_confirmacao_da_proxima_aplicacao_pendente');else assert.equal(r.estado,'S1');
 }
});
console.log(passou+'/'+passou+' PASS — dados e parâmetros exclusivamente sintéticos.');
