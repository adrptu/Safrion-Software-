/* EX-53 D11. Uma fonte de limites no cenário sintético. Não define metas padrão.
   Leitura/comparação puras: cenário e unidade explícitos; comando só dentro de cenMudar estrito.
   Produtividade pertence ao cultivo, não a este registro. */
const META_CATALOGO = Object.freeze([
  {id:'KPI-PCM-05',nome:'Cumprimento de preventiva',un:'%',min:0,max:100,sentido:'maior',kpi:'KPI-PCM-05'},
  {id:'custo-desvio',nome:'Custo realizado × previsto da execução',un:'%',min:-100,sentido:'menor',kpi:'KPI-CUS-03'},
  {id:'venda-referencia',nome:'Preço de venda × referência',un:'%',min:-100,sentido:'maior',kpi:null},
  {id:'compra-referencia',nome:'Preço de compra × referência',un:'%',min:-100,sentido:'menor',kpi:null}
]);
function metaDef(id){ return META_CATALOGO.find(x=>x.id===id)||null; }
function metaNumero(x){ return typeof x==='number'&&Number.isFinite(x); }
function metaValida(id,x){ const d=metaDef(id);
  if(!d||!x||x.un!==d.un||x.sentido!==d.sentido) return false;
  if(!metaNumero(x.valor)||!metaNumero(x.atencao)) return false;
  if([x.valor,x.atencao].some(n=>(d.min!==undefined&&n<d.min)||(d.max!==undefined&&n>d.max))) return false;
  return x.sentido==='maior'?x.atencao<=x.valor:x.atencao>=x.valor;
}
function metaRegistro(c,id){ if(typeof CONF0!=='undefined'&&c&&c.conf&&c.conf.v!==CONF0.v) return null; const x=c&&c.conf&&c.conf.metas&&c.conf.metas[id]; return x||null; }
function metaDe(c,id){ const x=metaRegistro(c,id); return x&&x.escopo==='organizacao'&&x.ativa!==false&&metaValida(id,x)?Object.assign({},x):null; }
function metaDica(c,id){ const m=metaDe(c,id); return m?'Meta '+m.valor+' '+m.un+' · atenção '+m.atencao+' '+m.un+' · '+m.sentido+' é melhor · v'+m.v+' · '+m.quem+' · '+m.d+' '+m.at+' · organização (meta vigente aplicada também aos períodos passados)':'Meta não configurada'; }
function metaAvaliar(c,id,valor,un,parcial){ const m=metaDe(c,id);
  if(!m) return {cor:'gray',texto:'Meta não configurada'};
  if(parcial||!metaNumero(valor)||un!==m.un) return {cor:'gray',texto:parcial?'Base parcial':(!metaNumero(valor)?'Sem base no período':'Unidade incompatível')};
  const boa=m.sentido==='maior'?valor>=m.valor:valor<=m.valor;
  const perto=m.sentido==='maior'?valor>=m.atencao:valor<=m.atencao;
  return {cor:boa?'green':perto?'yellow':'red',texto:boa?'Meta atendida':perto?'Atenção à meta':'Fora da meta'};
}
/* versão é por indicador e preservada na retirada (evita ABA); chave é do rascunho.
   Revalida o papel ativo no estado da transação. A UI nunca é a proteção do comando. */
function metaGravar(c,id,novo,motivo,versao,chave,ator){
  const d=metaDef(id); if(!d) throw new Error('Indicador não encontrado.');
  const K=confLer(c), quem=confExigeA(K,ator,{modo:'um',papeis:['gestor']},'Configurar meta');
  motivo=String(motivo||'').trim(); if(!motivo) throw new Error('Informe o motivo da definição, mudança ou retirada.');
  if(novo!==null&&!metaValida(id,novo)) throw new Error('Confira valor, unidade e sentido do indicador: o limite de atenção deve ser menor ou igual à meta quando maior é melhor, e maior ou igual quando menor é melhor.');
  const dados=novo===null?null:{valor:novo.valor,atencao:novo.atencao,sentido:d.sentido,un:d.un,escopo:'organizacao',kpi:d.kpi};
  const imp=JSON.stringify(['meta',id,dados,motivo,versao,quem]);
  const repetido=confRepete(K,chave,imp,'Meta'); if(repetido) return repetido;
  const antes=metaRegistro(c,id), v=antes?antes.v:0;
  if(!Number.isInteger(versao)||versao!==v) throw new Error('A meta mudou desde que você abriu. Compare a meta vigente e atualize a versão do rascunho; nada foi gravado.');
  if(novo===null&&(!antes||antes.ativa===false)) throw new Error('A meta já está sem configuração.');
  const alvo=confGarante(c); if(!alvo.metas) alvo.metas={};
  const e=confEv(alvo,chave,imp,{tipo:'meta',alvo:id,quem,t:(novo===null?'Retirada':'Definição')+' da meta · '+d.nome,ef:'Comparações futuras; valores do indicador não mudam.',motivo,antes:antes?Object.assign({},antes):null,depois:dados});
  alvo.metas[id]=Object.assign({},dados||{},{ativa:novo!==null,v:v+1,quem,d:e.d,at:e.at,motivo,recibo:e.id});
  return {msg:(novo===null?'Meta retirada':'Meta salva')+' · '+e.id,recibo:alvo.recibos[chave]};
}
