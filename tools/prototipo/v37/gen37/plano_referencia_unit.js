// A infraestrutura vem do executor. Os seletores SAF e g2 são reais; não substituímos contas.
let n = 0, falhas = 0;
function teste(nome, fn) {
  n++;
  try { fn(); console.log('OK ' + nome); }
  catch (e) { falhas++; console.log('FALHA ' + nome + ': ' + e.stack); }
}
const PR = PlanoReferencia;
const ctx = {fazenda:'Santa Rita', safra:'S2627'};
const e = (id, campos) => ({tipo:'cultivo', id, campos});
const snap = rows => PR.retrato(ctx, rows);
const clone = x => JSON.parse(JSON.stringify(x));
const S = () => ({state:{g2:{}}, setState(v){ Object.assign(this.state,v); }});
const entidade = (r,t,id) => r.entidades.find(e=>e.tipo===t && (!id || e.id===id));

teste('retrato independente e congelado em todos os níveis', () => {
  const origem = {area:{valor:10,unidade:'ha'}, local:'T1'};
  const r = snap([e('C1',origem)]), antes = PR.bytes(r);
  origem.area.valor=99;
  assert.equal(PR.bytes(r),antes);
  assert.ok(Object.isFrozen(r.entidades[0].campos.area));
  assert.equal(Reflect.set(r.entidades[0].campos.area,'valor',22),false);
  assert.equal(r.entidades[0].campos.area.valor,10);
});
teste('ordem visual de entidades e chaves não produz revisão', () => {
  const a=snap([e('2',{data:'2026-10-01',area:1}),e('1',{area:2})]);
  const b=snap([e('1',{area:2}),e('2',{area:1,data:'2026-10-01'})]);
  assert.equal(PR.bytes(a),PR.bytes(b)); assert.deepEqual(PR.comparar(a,b),[]);
});
teste('incluído, removido e alterado por identidade, sem depender da posição', () => {
  const d=PR.comparar(snap([e('1',{area:10}),e('2',{area:20})]),snap([e('1',{area:11}),e('3',{area:30})]));
  assert.deepEqual(d.map(x=>[x.id,x.estado]),[['1','alterado'],['2','removido'],['3','incluído']]);
});
teste('ausente, null e zero são três estados distintos', () => {
  const d=PR.comparar(snap([e('1',{})]),snap([e('1',{area:0})]))[0];
  assert.deepEqual(d.antes,{presente:false,valor:null}); assert.deepEqual(d.depois,{presente:true,valor:0});
  assert.equal(PR.comparar(snap([e('1',{area:null})]),snap([e('1',{area:0})]))[0].estado,'alterado');
});
teste('unidades incompatíveis explicitadas, sem subtrair kg de L', () => {
  const d=PR.comparar(snap([e('1',{dose:{valor:2,unidade:'kg/ha'}})]),snap([e('1',{dose:{valor:2,unidade:'L/ha'}})]))[0];
  assert.equal(d.unidadesIncompativeis,true); assert.ok(!('delta' in d));
});
teste('isolamento fazenda/safra mesmo com ID de cultivo igual', () => {
  for (const contexto of [{...ctx,safra:'S27SF'},{...ctx,fazenda:'Boa Vista'}]) assert.throws(()=>PR.comparar(snap([e('1',{})]),PR.retrato(contexto,[e('1',{})])),/diferentes/);
});
teste('recusa identidades repetidas, sem sobrescrever silenciosamente', () => {
  assert.throws(()=>snap([e('1',{}),e('1',{area:2})]),/repetida/);
});
teste('número não finito não vira null na serialização', () => {
  for (const area of [NaN,Infinity,-Infinity,undefined]) assert.throws(()=>snap([e('1',{area})]),/não finito/);
});
teste('versão de esquema desconhecida e identidade vazia recusadas', () => {
  assert.throws(()=>PR.bytes({...snap([]),schema:2}),/não suportada/);
  assert.throws(()=>PR.retrato({...ctx,fazenda:''},[]),/identidade/);
});
teste('serializar e recuperar conserva a referência sem recalcular', () => {
  const a=snap([e('1',{preco:{valor:28,unidade:'R$/L'}})]);
  assert.equal(PR.bytes(JSON.parse(PR.bytes(a))),PR.bytes(a));
});

teste('SAF real: projeção copia todos os cultivos e ocorrências', () => {
  const s=S(), r=PR.projetar(s,'S2627');
  assert.equal(r.entidades.filter(x=>x.tipo==='cultivo').length,cultRows(s,'S2627').length);
  assert.equal(r.entidades.filter(x=>x.tipo==='atividade').length,ocorr(s,'S2627').length);
  assert.equal(r.entidades.filter(x=>x.tipo==='produto').length,ocorr(s,'S2627').reduce((n,o)=>n+o.prods.length,0));
  assert.equal(r.contexto.fazenda,'Santa Rita');
});
teste('SAF real: dose, quantidade e preço vêm da ocorrência existente', () => {
  const s=S(), o=ocorr(s,'S2627')[0], p=o.prods[0], r=PR.projetar(s,'S2627');
  const x=entidade(r,'produto',JSON.stringify([o.c.id,o.a.id,p.nome])).campos;
  assert.equal(x.dose.valor,p.dose); assert.equal(x.quantidade.valor,p.q); assert.equal(x.preco.valor,p.preco);
});
teste('SAF real: editar área/data/meta não altera o retrato anterior', () => {
  const s=S(), a=PR.projetar(s,'S2627'), antes=PR.bytes(a), g=GR('g_cult_S2627');
  s.state.g2[g.id]={rows:clone(g.rows)};
  const c=cultRows(s,'S2627')[0]; c.v.area+=1; c.v.plantio='2026-10-21'; c.v.meta=0;
  const d=PR.comparar(a,PR.projetar(s,'S2627'));
  for (const campo of ['area','plantio','meta']) assert.ok(d.some(x=>x.tipo==='cultivo'&&x.id===c.id&&x.campo===campo));
  assert.equal(PR.bytes(a),antes);
});
teste('SAF real: mudança de preço/versão de catálogo não reescreve passado', () => {
  const s=S(), a=PR.projetar(s,'S2627'), antes=PR.bytes(a), pl=planById(cultRows(s,'S2627')[0].v.plano);
  const preco=pl.atividades[0].prods[0].preco, versao=pl.versao;
  try {
    pl.atividades[0].prods[0].preco=preco+1; pl.versao++;
    const d=PR.comparar(a,PR.projetar(s,'S2627'));
    assert.ok(d.some(x=>x.tipo==='produto'&&x.campo==='preco'));
    assert.ok(d.some(x=>x.tipo==='plano'&&x.campo==='versao'));
    assert.equal(PR.bytes(a),antes);
  } finally { pl.atividades[0].prods[0].preco=preco; pl.versao=versao; }
});
teste('SAF real: estoque/reserva/realizado não entram no retrato', () => {
  const s=S(), antes=PR.bytes(PR.projetar(s,'S2627'));
  const c=cenGet(); c.lotes['Glifosato 480|G26-14'].fisico=7; c.lotes['Glifosato 480|G26-14'].reservado=5; cenSave(c);
  const g=GR('g_cult_S2627'); s.state.g2[g.id]={rows:clone(g.rows)}; cultRows(s,'S2627')[0].v.colheita_real='2027-04-01';
  assert.equal(PR.bytes(PR.projetar(s,'S2627')),antes);
});
teste('SAF real: ordem de linhas não gera diferenças', () => {
  const s=S(), a=PR.projetar(s,'S2627'), g=GR('g_cult_S2627');
  s.state.g2[g.id]={rows:clone(g.rows).reverse()};
  assert.deepEqual(PR.comparar(a,PR.projetar(s,'S2627')),[]);
});
teste('SAF real: safra inexistente recusa, encerrada permite somente leitura do retrato', () => {
  assert.throws(()=>PR.projetar(S(),'inexistente'),/não encontrada/);
  const r=PR.projetar(S(),'S2526'); assert.equal(r.contexto.safra,'S2526');
  assert.ok(!('recibo' in r)); assert.ok(!('publicar' in PR));
});
teste('SAF real: retrato não grava cenário ou recibo', () => {
  const antes=JSON.stringify(__ls); PR.projetar(S(),'S2627'); assert.equal(JSON.stringify(__ls),antes);
});
teste('SAF real: ajuste de dose, retirada e inclusão entram pela conta existente', () => {
  const s=S(), a=PR.projetar(s,'S2627'), o=ocorr(s,'S2627')[0];
  s.state.adj=clone(adjOf(s));
  s.state.adj[o.c.id] = {...(s.state.adj[o.c.id]||{}),[o.a.id+'|0']:3,[o.a.id+'|1']:'-',
    [o.a.id+'|+901']:{prod:'Insumo sintético F2',grupo:'Adjuvantes',un:'L',preco:1,dose:0.1}};
  const b=PR.projetar(s,'S2627'), d=PR.comparar(a,b);
  assert.ok(d.some(x=>x.tipo==='produto'&&x.campo==='dose'&&x.depois.valor.valor===3));
  assert.ok(d.some(x=>x.tipo==='produto'&&x.estado==='removido'));
  assert.ok(d.some(x=>x.tipo==='produto'&&x.estado==='incluído'&&x.depois.produto==='Insumo sintético F2'));
  assert.equal(entidade(b,'cultivo',o.c.id).campos.ajustesLocais[o.a.id+'|0'],3);
});
teste('SAF real: parâmetros de recursos e calendário ficam congelados', () => {
  const s=S(), a=PR.projetar(s,'S2627'), antes=PR.bytes(a), r=entidade(a,'recurso');
  const g=['g_recp_maq','g_recp_pes'].map(GR).find(g=>g.rows.some(x=>x.id===r.id));
  s.state.g2[g.id]={rows:clone(g.rows)};
  const v=g2rows(s,g).find(x=>x.id===r.id).v; v.jornada+=1;
  const perda = 'disp' in v ? 'disp' : 'abs'; v[perda]-=1;
  const d=PR.comparar(a,PR.projetar(s,'S2627'));
  assert.ok(d.some(x=>x.tipo==='recurso'&&x.campo==='jornada'));
  assert.ok(d.some(x=>x.tipo==='recurso'&&x.campo===perda));
  assert.deepEqual(entidade(a,'calendario').campos.diasUteis,D2.dias);
  assert.equal(PR.bytes(a),antes);
});
teste('SAF real: quantidade infinita recusa projeção sem gravar', () => {
  const s=S(), g=GR('g_cult_S2627'); s.state.g2[g.id]={rows:clone(g.rows)};
  cultRows(s,'S2627')[0].v.area=Infinity;
  const antes=JSON.stringify(__ls);
  assert.throws(()=>PR.projetar(s,'S2627'),/Quantidade inválida/);
  assert.equal(JSON.stringify(__ls),antes);
});
teste('SAF real: projetar não modifica a demanda calculada', () => {
  const s=S(), antes=JSON.stringify(demanda(s,'S2627'));
  PR.projetar(s,'S2627'); assert.equal(JSON.stringify(demanda(s,'S2627')),antes);
});
const contexto = () => { const s=S(); s.state.saf='S2627'; return s; };
function recusaSemEscrever(s, previa, ator, padrao) {
  const estado=JSON.stringify(s.state), armazenamento=JSON.stringify(__ls);
  assert.throws(()=>PR.validarContexto(s,'S2627',ator,previa),padrao);
  assert.equal(JSON.stringify(s.state),estado);
  assert.equal(JSON.stringify(__ls),armazenamento);
}
teste('contexto: gestora recebe retrato atual congelado sem gravar', () => {
  const s=contexto(), previa=PR.projetar(s,'S2627');
  const antes=JSON.stringify(s.state), armazenamento=JSON.stringify(__ls);
  const r=PR.validarContexto(s,'S2627','Ana',previa);
  assert.equal(r.responsavel,g2ator('Ana','gestor'));
  assert.equal(PR.bytes(r.atual),PR.bytes(previa));
  assert.ok(Object.isFrozen(r)&&Object.isFrozen(r.atual));
  assert.equal(JSON.stringify(s.state),antes);
  assert.equal(JSON.stringify(__ls),armazenamento);
});
teste('contexto: papel vem do cadastro, não do objeto informado', () => {
  const s=contexto(), previa=PR.projetar(s,'S2627');
  G2_PERFIS.filter(p=>!g2papel(p,'gestor')).forEach(p=>recusaSemEscrever(s,previa,p.k,/decisão de/));
  [null,undefined,'inexistente',{k:'Caio',papeis:{gestor:'gestor'}}].forEach(p=>recusaSemEscrever(s,previa,p,/decisão de/));
});
teste('contexto: nova chamada revalida papel após prévia válida', () => {
  const s=contexto(), previa=PR.projetar(s,'S2627');
  PR.validarContexto(s,'S2627','Ana',previa);
  recusaSemEscrever(s,previa,'Caio',/decisão de/);
});
teste('contexto: ambos os marcadores de encerramento impedem publicação', () => {
  ['ro','estado'].forEach(k=>{
    const s=contexto(), previa=PR.projetar(s,'S2627'), g=GR('g_saf');
    s.state.g2[g.id]={rows:clone(g.rows)};
    const r=safById(s,'S2627'); if(k==='ro') r.ro=true; else r.v.estado='Encerrada';
    recusaSemEscrever(s,previa,'Ana',/Safra encerrada/);
  });
});
teste('contexto: seleção diferente e ausência de prévia preservam rascunho', () => {
  const s=contexto(), previa=PR.projetar(s,'S2627');
  s.state.saf='S2526'; recusaSemEscrever(s,previa,'Ana',/Escolha a safra/);
  s.state.saf='S2627'; recusaSemEscrever(s,null,'Ana',/Confira a prévia/);
});
teste('contexto: outra fazenda ou safra não reutiliza prévia', () => {
  const s=contexto();
  ['fazenda','safra'].forEach(k=>{
    const previa=clone(PR.projetar(s,'S2627')); previa.contexto[k]='outro';
    recusaSemEscrever(s,previa,'Ana',/plano mudou/);
  });
});
teste('contexto: área, data e dose alteradas exigem nova prévia sem perder rascunho', () => {
  ['area','data','dose'].forEach(k=>{
    const s=contexto(), previa=PR.projetar(s,'S2627'), g=GR('g_cult_S2627');
    s.state.g2[g.id]={rows:clone(g.rows)};
    const c=cultRows(s,'S2627')[0];
    if(k==='area') c.v.area+=1;
    else if(k==='data') c.v.plantio='2026-11-20';
    else { const o=ocorr(s,'S2627')[0]; s.state.adj=clone(adjOf(s)); s.state.adj[o.c.id]={...(s.state.adj[o.c.id]||{}),[o.a.id+'|0']:3}; }
    recusaSemEscrever(s,previa,'Ana',/plano mudou/);
    PR.validarContexto(s,'S2627','Ana',PR.projetar(s,'S2627'));
  });
});
const preparar=(h,r,esp=null,por='Ana (gestora)',em='2026-10-13T16:30:00.000Z')=>PR.prepararVersao(h,r,esp,por,em);
teste('versão: primeira referência independente e metadados explícitos, sem gravar',()=>{
  const atual=snap([e('C1',{area:{valor:10,unidade:'ha'}})]), h=[], antes=JSON.stringify(__ls);
  const p=preparar(h,atual);assert.equal(p.nova,true);assert.equal(p.versao.id,'R1');
  assert.equal(h.length,0);assert.ok(Object.isFrozen(p.versao.retrato));assert.notEqual(p.versao.retrato,atual);
  assert.equal(JSON.stringify(__ls),antes);
});
teste('versão: R2 conserva R1 após recarga e alteração do plano',()=>{
  const a=snap([e('C1',{area:{valor:10,unidade:'ha'}})]), h=[preparar([],a).versao];
  const original=JSON.stringify(h);const recarga=clone(h);
  const p=preparar(recarga,snap([e('C1',{area:{valor:11,unidade:'ha'}})]),'R1');
  assert.equal(p.versao.id,'R2');assert.equal(p.nova,true);assert.equal(JSON.stringify(h),original);assert.equal(JSON.stringify(recarga),original);
});
teste('versão: conteúdo sem mudança não gera versão redundante',()=>{
  const a=snap([e('C1',{area:10}),e('C2',{area:20})]), h=[preparar([],a).versao];
  const p=preparar(h,snap([e('C2',{area:20}),e('C1',{area:10})]),'R1');
  assert.equal(p.nova,false);assert.deepEqual(p.versao,h[0]);assert.notEqual(p.versao,h[0]);
});
teste('versão: referência concorrente recusa mesmo conteúdo, sem mudar histórico',()=>{
  const a=snap([e('C1',{area:10})]), h=[preparar([],a).versao], antes=JSON.stringify(h);
  for(const esperada of [null,'R0','R2',undefined]) assert.throws(()=>preparar(h,a,esperada),/outra aba/);
  assert.equal(JSON.stringify(h),antes);
});
teste('versão: histórico de outra safra/fazenda, incompleto ou fora de ordem é recusado',()=>{
  const a=snap([e('C1',{area:10})]), r=preparar([],a).versao;
  for(const campo of ['fazenda','safra']){const x=clone(r);x.retrato.contexto[campo]='Outra';assert.throws(()=>preparar([x],a,'R1'),/fazendas ou safras/);}
  for(const h of [[{...r,id:'R2'}],[r,r],[{...r,por:''}],[{...r,em:''}]]) assert.throws(()=>preparar(h,a,'R1'),/Histórico/);
});
teste('versão: publicação nova exige autor e instante válido sem inventá-los',()=>{
  const a=snap([e('C1',{area:10})]);
  assert.throws(()=>preparar([],a,null,''),/Responsável/);
  for(const em of ['', 'ontem', '2026-02-30T16:30:00.000Z']) assert.throws(()=>preparar([],a,null,'Ana',em),/Data/);
});
const reciboTrilha=(r,sq=1)=>({...preparar([],r).versao,sq});
teste('trilha: legado vazio não recebe data, ator ou publicação fictícia',()=>assert.deepEqual(PR.trilha([]),[]));
teste('trilha: recibo completo usa a identidade, autor, instante e ordem registrados',()=>{
  const p=reciboTrilha(snap([e('C1',{area:10})]),7), antes=JSON.stringify(p), estado=JSON.stringify(__ls);
  const [linha]=PR.trilha([p]);
  assert.equal(linha.quem,p.por);assert.equal(linha.d,'2026-10-13');assert.equal(linha.at,'16:30:00');assert.equal(linha.sq,7);
  assert.equal(linha.cmd,'CMD-02');assert.equal(linha.h,'SAF.dc.html#saf=S2627');assert.match(linha.ef,/Não autoriza/);
  assert.equal(JSON.stringify(p),antes);assert.equal(JSON.stringify(__ls),estado);assert.ok(Object.isFrozen(linha));
});
teste('trilha: mesmo R1 em contextos diferentes tem identidade distinta e estável',()=>{
  const a=reciboTrilha(snap([e('C1',{area:10})]));
  const b=reciboTrilha(PR.retrato({fazenda:'Outra',safra:'S2627'},[e('C1',{area:10})]),2);
  const c=reciboTrilha(PR.retrato({fazenda:'Santa Rita',safra:'S2526'},[e('C1',{area:10})]),3);
  const linhas=PR.trilha([a,b,c]);assert.equal(new Set(linhas.map(l=>l.id)).size,3);
  assert.deepEqual(PR.trilha([c,a,b]).map(l=>l.id).sort(),linhas.map(l=>l.id).sort());
  assert.deepEqual(PR.trilha(clone([a,b,c])),linhas);
});
teste('trilha: revisão indica orçamento a revisar sem dar aprovação ou alterar R1',()=>{
  const a=snap([e('C1',{area:10})]), r1=reciboTrilha(a), antes=JSON.stringify(r1);
  const r2={...preparar([r1],snap([e('C1',{area:11})]),'R1').versao,sq:2};
  const ls=PR.trilha([r1,r2]);assert.match(ls[0].oq,/referência/);assert.match(ls[1].oq,/revisão/);assert.match(ls[1].ef,/Orçamento a revisar/);
  assert.equal(JSON.stringify(r1),antes);
});
teste('trilha: recibo duplicado ou sem autor/data/ordem não vira evento',()=>{
  const p=reciboTrilha(snap([e('C1',{area:10})]));
  assert.throws(()=>PR.trilha([p,p]),/repetido/);
  for(const mudanca of [{por:''},{em:''},{em:'2026-02-30T00:00:00.000Z'},{sq:0},{sq:undefined},{sq:1.5},{id:'R0'}])
    assert.throws(()=>PR.trilha([{...p,...mudanca}]),/incompleto/);
});
console.log(`RESULTADO ${n-falhas}/${n} · núcleo/projeção/contexto/preparação/trilha; publicação e UI não executadas`);
if (falhas) process.exitCode=1;
