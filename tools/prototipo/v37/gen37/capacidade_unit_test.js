const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const ctx = vm.createContext({});
vm.runInContext(fs.readFileSync(__dirname + '/capacidade.js', 'utf8'), ctx);
const teto = ctx.capacidadeJornada('seg–sex · 07–17h');
assert.equal(teto.hhSemana,50);
assert.equal(ctx.capacidadeJornada('seg–sáb · 06–15h').hhSemana,54);
for (const cal of ['escala 6×2 · 8h','Da equipe','',null,'seg–sex · 17–07h','seg–sex · 07–25h'])
  assert.equal(ctx.capacidadeJornada(cal),null);
assert.equal(ctx.capacidadePartilha({Mecânico:30,Lubrificador:20},teto),true);
assert.equal(ctx.capacidadePartilha({Mecânico:30,Lubrificador:21},teto),false);
assert.equal(ctx.capacidadePartilha({Mecânico:50,Lubrificador:50},teto),false);
assert.equal(ctx.capacidadePartilha({Mecânico:10},null),false);
assert.equal(ctx.capacidadePartilha({Mecânico:30,Lubrificador:20},ctx.capacidadeJornada('seg–sex · 08–16h')),false);
for(const h of [0,-1,'20',NaN,Infinity]) assert.equal(ctx.capacidadePartilha({Mecânico:h},teto),false);
console.log('PASS D11b partilha: teto nominal explícito, ciclo sem âncora indisponível, limite inclusivo, dupla contagem recusada e redução de jornada invalida partilha.');
const ps={p1:{v:1,sit:'Ativa',calendario:'seg–sex · 07–17h'},p2:{v:2,sit:'Ativa',calendario:'seg–sex · 07–17h'}};
const rs={p1:{v:1,pessoaV:1,quem:'Gestor',motivo:'Dedicação',recibo:'CFG-1',alocacoes:{Mecânico:30,Lubrificador:20}},p2:{v:1,pessoaV:2,quem:'Gestor',motivo:'Dedicação',recibo:'CFG-2',alocacoes:{Mecânico:10}}};
assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico').hhSemana,40);
assert.equal(ctx.capacidadeSomar(rs,ps,'Lubrificador').hhSemana,20);
assert.equal(ctx.capacidadeSomar(rs,ps,'Eletricista'),null);
assert.equal(ctx.capacidadeSomar({},ps,'Mecânico'),null);
ps.p1.v=2; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico'),null); // não disfarça 10h parciais como total
ps.p1.v=1; ps.p1.calendario='escala 6×2 · 8h'; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico'),null);
ps.p1.calendario='seg–sex · 07–17h'; ps.p1.sit='Inativa'; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico').hhSemana,10);
ps.p1.sit='Ativa'; rs.p1.alocacoes.Lubrificador=21; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico'),null);
rs.p1.alocacoes.Lubrificador=20; rs.p1.ativa=false; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico').hhSemana,10);
rs.p1.ativa=true; delete ps.p1; assert.equal(ctx.capacidadeSomar(rs,ps,'Mecânico'),null);
console.log('PASS D11b agregação por pessoa: partilha sem duplicação, ausência sem padrão, revisão obsoleta suspende total, calendário incerto, inativação e retirada. Prova unitária, não teste de UI.');
