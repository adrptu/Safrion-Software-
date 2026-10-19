let n=0,f=0;const clone=x=>JSON.parse(JSON.stringify(x));
function t(nome,fn){n++;try{cenReset();fn();console.log('OK '+nome);}catch(e){f++;console.log('FALHA '+nome+' '+e.message);}}
const self=()=>({state:{g2:{},saf:'S2627'},setState(x){Object.assign(this.state,x);}});
const p=(s,ator='Ana')=>({chave:'real-teste',esperada:null,safra:s.state.saf,ator,previa:PlanoReferencia.projetar(s,s.state.saf)});
const publicar=(s,ator)=>PlanoReferenciaComando.publicar(s,p(s,ator),safImpedimentosRef);
const estado=()=>JSON.stringify({mem:CEN_MEM,ls:__ls});
t('adaptador real permite avisos e publica R1 pela alçada real',()=>{const s=self(),d=safImpedimentosRef(s,s.state.saf,cenGet());assert.equal(d.impedimentos.length,0);assert.equal(d.avisos.length,3);const r=publicar(s);assert.ok(!r.erro,r.erro);assert.equal(r.versao.id,'R1');});
t('sobreposição real recusa antes de gravar recibo ou referência',()=>{const s=self(),g=GR('g_cult_S2627');s.state.g2[g.id]={rows:clone(g.rows)};cultRows(s,'S2627')[0].v.area=99999;cenGet();const antes=estado(),r=publicar(s);assert.match(r.erro,/Sobreposição/);assert.equal(estado(),antes);});
t('cultura incompatível real recusa e preserva rascunho',()=>{const s=self(),g=GR('g_cult_S2627');s.state.g2[g.id]={rows:clone(g.rows)};const c=cultRows(s,'S2627')[0];c.v.plano=D2.planos.find(x=>x.cultura!==c.v.cult).id;cenGet();const antes=estado(),draft=JSON.stringify(s.state),r=publicar(s);assert.match(r.erro,/plano de/);assert.equal(estado(),antes);assert.equal(JSON.stringify(s.state.g2),JSON.stringify(JSON.parse(draft).g2));});
t('Rui sem AL18 recusa comando real',()=>{const s=self();cenGet();const antes=estado(),r=publicar(s,'Rui');assert.ok(r.erro);assert.equal(estado(),antes);});
t('AL18 editável para agrônomo conflita com gestor fixo no núcleo (contraprova)',()=>{
 const s=self(),caio=CONF0.pessoas.find(x=>x.k==='Caio').id,ana=CONF0.pessoas.find(x=>x.k==='Ana').id;
 const c1=cenMudar(null,c=>confPapeis(c,caio,['gestor','pcp'],'dar-gestor','Ana'));assert.ok(!c1.erro,c1.erro);
 const c2=cenMudar(null,c=>confPapeis(c,ana,['agronomo'],'tirar-gestor','Caio'));assert.ok(!c2.erro,c2.erro);
 const r=cenMudar(null,c=>confAlcMudar(c,'AL-18',{papel:'agronomo'},'Contraprova sintética','alc-teste','Caio',1));console.log('MUDANCA '+JSON.stringify(r));console.log('AL18 '+JSON.stringify(g2alc('AL-18')));
 assert.equal(g2alc('AL-18').papeis[0],'agronomo');const q=g2perfis().find(x=>x.papeis.agronomo&&!x.papeis.gestor);assert.ok(q);assert.ok(cenExigeAlc(q.k,'AL-18','Teste'));const a=publicar(s,q.k);console.log('PUBLICAR '+JSON.stringify(a));assert.match(a.erro,/gestor/);
});
console.log(`RESULTADO ${n-f}/${n}`);if(f)process.exitCode=1;
