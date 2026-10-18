'use strict';
const assert = require('node:assert/strict');
const {frAgenda} = require('./frentes_agenda.js');
const H = 3600000, D = Date.UTC(2026, 9, 18);
const p = {inicio: D + 8*H, velocidadeKmh: 20, turnos:[[D,D+96*H]], fonte: 'Hipótese sintética de teste, não regra operacional'};
const os = (id, horas, a=8, b=16, km=0) => ({id, areaHa: horas*10, rendimentoHaH: 10,
  janelaInicio: D+a*H, janelaFim: D+b*H, kmAnterior: km});
let total=0;
function test(nome, fn) { fn(); total++; console.log('OK '+nome); }
test('3 operações de4h em8h: primeira que estoura é C', () => {
  const r=frAgenda([os('A',4),os('B',4),os('C',4)],p);
  assert.equal(r.status,'inviavel'); assert.equal(r.id,'C'); assert.equal(r.linhas[2].fim,null);
});
test('janelas adjacentes sem interseção global são viáveis', () => {
  const r=frAgenda([os('A',2,8,10),os('B',2,10,12)],p);
  assert.equal(r.status,'viavel'); assert.equal(r.linhas[1].inicio,D+10*H);
});
test('janela de1h expira antes da segunda operação', () => {
  const r=frAgenda([os('A',2),os('B',1,8,9),os('C',1)],p);
  assert.equal(r.id,'B'); assert.equal(r.status,'inviavel'); assert.equal(r.linhas.length,2);
});
test('virada de dia preserva data e fim exato', () => {
  const r=frAgenda([os('A',3,23,26)],{...p,inicio:D+23*H});
  assert.equal(r.status,'viavel'); assert.equal(r.linhas[0].fim,D+26*H);
});
test('deslocamento entre O.S. impede janela antes viável', () => {
  const r=frAgenda([os('A',2,8,10),os('B',2,10,12,20)],p);
  assert.equal(r.status,'inviavel'); assert.equal(r.linhas[1].inicio,D+11*H);
});
test('viagem chega antes da janela e espera no destino', () => {
  const r=frAgenda([os('A',2,10,12,20)],p);
  assert.equal(r.status,'viavel'); assert.equal(r.linhas[0].chegada,D+9*H);
  assert.equal(r.linhas[0].esperaMs,H); assert.equal(r.linhas[0].operacaoExecutadaMs,2*H);
  assert.equal(r.linhas[0].fim,D+12*H);
  assert.equal(r.premissas.incluiTrocaCaldaLavagem,false);
  assert.equal(r.premissas.incluiPausas,true);
});
test('dados ausentes e inválidos nunca presumem viabilidade', () => {
  for(const campo of ['areaHa','rendimentoHaH','janelaInicio','janelaFim','kmAnterior']) {
    for(const valor of [undefined,null,'10',NaN,Infinity].concat(campo.startsWith('janela') ? [0.5] : [-1])) {
      assert.equal(frAgenda([{...os('A',1),[campo]:valor}],p).status,'sem_conta',campo+':'+valor);
    }
  }
  for(const campo of ['areaHa','rendimentoHaH']) assert.equal(frAgenda([{...os('A',1),[campo]:0}],p).status,'sem_conta');
  assert.equal(frAgenda([os('A',1,10,9)],p).status,'sem_conta');
  assert.equal(frAgenda([os('A',1,10,10)],p).status,'sem_conta','janela de duração zero');
});
test('parâmetro explícito e fonte obrigatórios, sem padrão', () => {
  for(const q of [null,{}, {...p,velocidadeKmh:0},{...p,fonte:''},{...p,inicio:'08:00'}]) {
    assert.equal(frAgenda([os('A',1)],q).status,'sem_conta');
  }
});
test('sem dado intermediário não calcula sucessor nem oculta prefixo', () => {
  const r=frAgenda([os('A',1),{...os('B',1),rendimentoHaH:null},os('C',1)],p);
  assert.equal(r.status,'sem_conta'); assert.equal(r.id,'B'); assert.deepEqual(r.linhas.map(x=>x.id),['A']);
});
test('entrada vazia e IDs ausentes/duplicados', () => {
  for(const seq of [[],null,[null],[{...os('A',1),id:''}],[os('A',1),os('A',1)]]) {
    assert.equal(frAgenda(seq,p).status,'sem_conta');
  }
});
test('não altera ordem, dados ou parâmetros congelados', () => {
  const seq=Object.freeze([Object.freeze(os('Z',1)),Object.freeze(os('A',1))]);
  const r=frAgenda(seq,Object.freeze({...p})); assert.deepEqual(r.linhas.map(x=>x.id),['Z','A']);
});
test('precisão de1ms conservadora e fronteira inclusiva', () => {
  const o={...os('A',1),areaHa:1,rendimentoHaH:7};
  const dur=Math.ceil(H/7); o.janelaFim=p.inicio+dur;
  assert.equal(frAgenda([o],p).status,'viavel');
  assert.equal(frAgenda([{...o,janelaFim:o.janelaFim-1}],p).status,'inviavel');
});
test('overflow não vira horário viável ou exceção', () => {
  assert.equal(frAgenda([{...os('A',1),rendimentoHaH:Number.MIN_VALUE}],p).status,'sem_conta');
});
test('20h em turnos07–17 termina17h no segundo dia; janela1dia não cabe',()=>{
  const q={...p,inicio:D+7*H,turnos:[[D+7*H,D+17*H],[D+31*H,D+41*H]]};
  const r=frAgenda([os('A',20,7,41)],q), l=r.linhas[0];
  assert.equal(r.status,'viavel'); assert.equal(l.fim,D+41*H);
  assert.equal(l.operacaoMs,20*H); assert.equal(l.operacaoExecutadaMs,20*H);
  assert.equal(l.pausaMs,14*H); assert.equal(l.esperaMs,0);
  const x=frAgenda([os('A',20,7,17)],q);
  assert.equal(x.status,'inviavel'); assert.equal(x.linhas[0].fim,null);
  assert.equal(x.linhas[0].operacaoExecutadaMs,10*H);
});
test('deslocamento interrompido não consome madrugada',()=>{
  const q={...p,inicio:D+16*H,turnos:[[D+7*H,D+17*H],[D+31*H,D+41*H]]};
  const r=frAgenda([os('A',1,7,41,40)],q), l=r.linhas[0];
  assert.equal(r.status,'viavel'); assert.equal(l.chegada,D+32*H);
  assert.equal(l.inicio,D+32*H); assert.equal(l.fim,D+33*H);
  assert.equal(l.deslocamentoMs,2*H); assert.equal(l.pausaMs,14*H);
});
test('turnos obrigatórios, válidos, ordenados e não sobrepostos',()=>{
  for(const turnos of [undefined,null,[],[[]],[[D,D]],[[D+H,D]],[[D,D+2*H],[D+H,D+3*H]],[[D+H,D+2*H],[D,D+H]],[[D,'fim']]])
    assert.equal(frAgenda([os('A',1)],{...p,turnos}).status,'sem_conta');
});
test('espera pela abertura separada da pausa fora do turno',()=>{
  const r=frAgenda([os('A',1,10,17)],{...p,inicio:D+6*H,turnos:[[D+7*H,D+17*H]]});
  assert.equal(r.status,'viavel'); assert.equal(r.linhas[0].esperaMs,3*H);
  assert.equal(r.linhas[0].pausaMs,H); assert.equal(r.linhas[0].inicio,D+10*H);
});
test('fim exato do turno aceito;1ms extra exige outro turno',()=>{
  const q={...p,turnos:[[D+8*H,D+9*H]]};
  assert.equal(frAgenda([os('A',1,8,10)],q).status,'viavel');
  const r=frAgenda([{...os('A',1,8,10),areaHa:10+10/H}],q);
  assert.equal(r.status,'inviavel'); assert.match(r.motivo,/Sem turno/);
});
test('viagem termina na borda; operação inicia somente no próximo turno',()=>{
  const q={...p,inicio:D+16*H,turnos:[[D+7*H,D+17*H],[D+31*H,D+41*H]]};
  const l=frAgenda([os('A',1,7,41,20)],q).linhas[0];
  assert.equal(l.chegada,D+17*H); assert.equal(l.inicio,D+31*H);
  assert.equal(l.pausaMs,14*H); assert.equal(l.fim,D+32*H);
});
test('A1: termina A08h, viaja até09h e opera B10–12h',()=>{
  const q={...p,inicio:D+7*H,turnos:[[D+7*H,D+17*H]]};
  const r=frAgenda([os('A',1,7,17),os('B',2,10,12,20)],q), b=r.linhas[1];
  assert.equal(r.status,'viavel'); assert.equal(b.chegada,D+9*H);
  assert.equal(b.inicio,D+10*H); assert.equal(b.fim,D+12*H); assert.equal(b.esperaMs,H);
});
test('viagem incompleta sem turno tem motivo próprio e não inicia operação',()=>{
  const r=frAgenda([os('A',1,8,20,40)],{...p,turnos:[[D+8*H,D+9*H]]});
  assert.equal(r.status,'inviavel'); assert.equal(r.motivo,'Sem turno para o deslocamento');
  assert.equal(r.linhas[0].chegada,null); assert.equal(r.linhas[0].inicio,null);
  assert.equal(r.linhas[0].fim,null); assert.equal(r.linhas[0].deslocamentoExecutadoMs,H);
});
console.log(total+' cenários passaram');
