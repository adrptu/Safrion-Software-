const fs=require('fs'),vm=require('vm'),a=require('node:assert/strict');
const ctx={window:{},MIPD:{prot:{P:{un:'alvos/ponto',crit:'nc',nc:10,chave:'alvo'}},tal:{T:{fase:'demo'}}}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/mip.js','utf8'),ctx);
const vis=(id,extra={})=>({id,tal:'T',prot:'P',data:'2026-01-02',est:'concluida',npts:1,pts:[{n:1,v:0,ok:true}],pend:[],...extra});
const s={vis:{V:vis('V',{dec:{os:'OS-1',pos:'POS'}}),POS:vis('POS',{pos_de:'V',est:'programada',pts:[{n:1,v:null,ok:true}]})},apl:[{tal:'T',chave:'alvo',os:'OS-1',data:'2026-01-03',prod:'demo'}]};
const ordens={'OS-1':{etapa:'A liberar'}};const norm=x=>JSON.parse(JSON.stringify(x));
const before=JSON.stringify(s);let r=ctx.mipRaioxFontes(s,'V',{ordens});
a.equal(r.antes.valorObservado,0);a.equal(r.antes.versao,null);a.equal(r.antes.disponivelEm,null);
a.equal(r.depois.valorObservado,null);a.equal(r.depois.completa,false);a.equal(r.variacao,null);
a.equal(r.aplicacoes[0].estado,'execucao_nao_demonstrada');
ordens['OS-1'].etapa='Concluídas';a.equal(ctx.mipRaioxFontes(s,'V',{ordens}).aplicacoes[0].estado,'execucao_nao_demonstrada');
ordens['OS-1'].etapa='Canceladas';a.equal(ctx.mipRaioxFontes(s,'V',{ordens}).aplicacoes[0].estado,'cancelada_ou_ausente');
a.equal(JSON.stringify(s),before,'diagnóstico não muda as fontes');
s.vis.POS.tal='OUTRO';a.equal(ctx.mipRaioxFontes(s,'V',{ordens}).depois,null);
s.apl[0].tal='OUTRO';a.equal(ctx.mipRaioxFontes(s,'V',{ordens}).aplicacoes.length,0);
a.equal(ctx.mipRaioxFontes(s,'AUSENTE',{ordens}).estado,'fonte_ausente');
s.vis.V.versao=3;s.vis.V.disponivelEm='2026-10-19T15:24:00.000Z';r=ctx.mipRaioxFontes(s,'V',{ordens});
a.equal(r.antes.versao,3);a.equal(r.antes.historico,'indisponivel');a.equal(r.antes.precisao,'dia');a.equal(r.variacao,null);
console.log('PASS: zero/ausência, pós programado, planejamento não comprova execução, cancelamento, isolamento, legado, versão sem histórico e imutabilidade');

for (const bad of [{npts:0,pts:[]},{pts:[{n:1,v:Infinity,ok:true}]},{pts:[{n:1,v:'inválido',ok:true}]}]) {
 const z={vis:{V:vis('V',bad)},apl:[]};
 const f=ctx.mipRaioxFontes(z,'V',null);
 a.equal(f.antes.completa,false,'fonte vazia ou não finita não está completa');
 a.equal(f.antes.valorObservado,null,'valor não finito permanece ausente');
}
console.log('PASS fontes vazias/não finitas');
