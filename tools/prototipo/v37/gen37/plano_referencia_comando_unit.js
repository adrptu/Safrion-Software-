// AL18 acordada6151368134; fixture até Claude compor a entrada em g2lib.
G2_ALCADAS.push({id:'AL-18',t:'Publicar referência técnica do plano operacional',papeis:['gestor'],modo:'todos',edita:''});
let n=0,fail=0;const clone=x=>JSON.parse(JSON.stringify(x));
function teste(nome,fn){n++;try{__cota=false;cenReset();fn();console.log('OK '+nome);}catch(e){fail++;console.log('FALHA '+nome+' '+e.stack);}}
const self=()=>({state:{g2:{},saf:'S2627'},setState(x){Object.assign(this.state,x);}});
const pedido=(s,chave='teste',esperada=null)=>({chave,esperada,safra:s.state.saf,ator:'Ana',previa:PlanoReferencia.projetar(s,s.state.saf)});
const valido=()=>({impedimentos:[]});
const pub=(s,p,v=valido)=>PlanoReferenciaComando.publicar(s,p,v);
const hist=()=>cenGet().planoReferencias[0];
const alterar=s=>{const g=GR('g_cult_S2627');s.state.g2[g.id]={rows:clone(g.rows)};cultRows(s,'S2627')[0].v.area+=1;};
const estado=()=>JSON.stringify({store:__ls,mem:CEN_MEM});
teste('R1 grava snapshot e recibo juntos; não altera O.S./estoque/demanda',()=>{
 const s=self(),p=pedido(s),antes=clone(cenGet()),r=pub(s,p);assert.ok(!r.erro,r.erro);assert.equal(r.versao.id,'R1');assert.equal(hist().versoes.length,1);assert.equal(hist().orcamentoRevisar,false);assert.equal(r.versao.sq,cenGet().rev);
 const depois=clone(cenGet());delete depois.planoReferencias;delete depois.recibos;depois.rev=antes.rev;
 // confCarimbar é do gravador compartilhado; o oráculo é o mesmo gravador sem comando.
 cenReset();cenMudar(null,()=>({}));const controle=clone(cenGet());controle.rev=antes.rev;
 assert.deepEqual(depois,controle);assert.equal(r.recibo.plano.id,'R1');
});
teste('duplo envio e recarga recuperam mesmo recibo sem incrementar rev',()=>{
 const s=self(),p=pedido(s),a=pub(s,p);assert.ok(!a.erro,a.erro);const bytes=__ls[CEN_KEY],rev=cenGet().rev;
 CEN_MEM=null;const b=pub(s,p);assert.equal(b.repetido,true);assert.deepEqual(b.recibo,a.recibo);assert.deepEqual(b.versao,a.versao);assert.equal(__ls[CEN_KEY],bytes);assert.equal(cenGet().rev,rev);
});
teste('mesma chave com outro conteúdo recusa sem modificar versão/recibo',()=>{
 const s=self(),p=pedido(s);pub(s,p);alterar(s);const antes=estado(),r=pub(s,pedido(s));assert.match(r.erro,/outro conteúdo/);assert.equal(estado(),antes);
});
teste('R2 preserva R1 e sinaliza orçamento a revisar após recarga',()=>{
 const s=self();pub(s,pedido(s));const r1=clone(hist().versoes[0]);alterar(s);const r=pub(s,pedido(s,'revisao','R1'));assert.ok(!r.erro,r.erro);assert.equal(r.versao.id,'R2');CEN_MEM=null;assert.deepEqual(hist().versoes[0],r1);assert.equal(hist().orcamentoRevisar,true);assert.equal(PlanoReferencia.trilha(hist().versoes).length,2);
});
teste('nova intenção sem mudança preserva a versão e orçamento a revisar',()=>{
 const s=self();pub(s,pedido(s));alterar(s);pub(s,pedido(s,'r2','R1'));const r=pub(s,pedido(s,'sem-mudanca','R2'));assert.ok(!r.erro,r.erro);assert.equal(r.nova,false);assert.equal(hist().versoes.length,2);assert.equal(hist().orcamentoRevisar,true);assert.equal(pub(s,pedido(s,'sem-mudanca','R2')).repetido,true);
});
teste('duas prévias: segunda intenção com referência antiga recusa atomicamente',()=>{
 const a=self(),b=self(),pa=pedido(a,'a'),pb=pedido(b,'b');pub(a,pa);const antes=estado(),r=pub(b,pb);assert.match(r.erro,/outra aba/);assert.equal(estado(),antes);
});
teste('cota cheia não grava histórico/recibo; retry grava uma vez',()=>{
 const s=self(),p=pedido(s);cenMudar(null,()=>({}));const antes=estado();__cota=true;const r=pub(s,p);assert.match(r.erro,/Não foi possível gravar/);assert.equal(estado(),antes);__cota=false;const a=pub(s,p);assert.equal(a.versao.id,'R1');const rev=cenGet().rev;assert.equal(pub(s,p).repetido,true);assert.equal(cenGet().rev,rev);
});
teste('papel revogado antes de confirmar ou recuperar recibo recusa',()=>{
 const s=self(),p=pedido(s);pub(s,p);cenMudar(null,c=>{const k=confGarante(c);k.pessoas.p1.papeis=[];return {};});const antes=estado(),r=pub(s,p);assert.ok(r.erro);assert.equal(estado(),antes);
});
teste('plano alterado após prévia recusa e preserva rascunho',()=>{
 const s=self(),p=pedido(s);alterar(s);const draft=JSON.stringify(s.state.g2),antes=estado(),r=pub(s,p);assert.match(r.erro,/plano mudou/);assert.equal(estado(),antes);assert.equal(JSON.stringify(s.state.g2),draft);
});
teste('safra encerrada e contexto alheio recusam',()=>{
 const s=self(),p=pedido(s);p.previa=clone(p.previa);p.previa.contexto.fazenda='Outra';assert.match(pub(s,p).erro,/fazenda/);
 const g=GR('g_saf');s.state.g2[g.id]={rows:clone(g.rows)};safById(s,'S2627').v.estado='Encerrada';assert.match(pub(s,pedido(s)).erro,/encerrada/);assert.equal(cenGet().planoReferencias,undefined);
});
teste('sem adaptador, validação incompleta ou impedimento não escreve',()=>{
 const s=self(),p=pedido(s);cenGet();const antes=estado();
 for(const fn of [undefined,()=>true,()=>Promise.resolve({impedimentos:[]}),()=>({impedimentos:['Dose pendente.']})]){const r=PlanoReferenciaComando.publicar(s,p,fn);assert.ok(r.erro);assert.equal(estado(),antes);}
});
teste('adaptador reexecutado dentro de cada intenção; erro não deixa efeito parcial',()=>{
 const s=self();let chamadas=0;const r=pub(s,pedido(s),(ss,saf,c)=>{chamadas++;c.sonda='não persiste';throw new Error('Impedimento atualizado');});assert.match(r.erro,/Impedimento/);assert.equal(chamadas,1);assert.equal(cenGet().sonda,undefined);assert.equal(cenGet().planoReferencias,undefined);
});
teste('sem chave ou referência esperada não aceita publicação',()=>{
 const s=self();for(const muda of [{chave:''},{esperada:undefined}])assert.ok(pub(s,{...pedido(s),...muda}).erro);assert.equal(cenGet().planoReferencias,undefined);
});
teste('consulta lê versão gravada pelo comando no contexto selecionado, por cópia',()=>{
 global.document={getElementById:()=>null};global.requestAnimationFrame=()=>{};
 const s=self(),r=pub(s,pedido(s));assert.ok(!r.erro,r.erro);
 const antes=estado();planoRefAbrir(s,null);assert.equal(s.state.prPainel.publicadas[0].id,'R1');
 s.state.prPainel.publicadas[0].por='Outro';assert.equal(estado(),antes);
 const outro=self();outro.state.saf='S27SF';planoRefAbrir(outro,null);assert.deepEqual(outro.state.prPainel.publicadas,[]);
});
console.log(`RESULTADO ${n-fail}/${n} · transação real com adaptador de domínio de teste; UI/agronomia não executadas`);if(fail)process.exitCode=1;
