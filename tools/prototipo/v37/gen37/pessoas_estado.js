/* CD-04 / D11b: fonte compartilhada do cadastro, distinta dos acessos c.conf.pessoas.
   Comando executado somente na transação estrita cenMudar. Sem escrita ao renderizar.
   Compartilhada pelo editor CD-04 e pela dedicação CF-06. */
function pessoasClonar(x) { return JSON.parse(JSON.stringify(x)); }
function pessoasLer(c) {
  const x=c&&c.cadPessoas;
  return x&&x.v===PESSOAS0.v ? x : {v:PESSOAS0.v,rev:0,pessoas:PESSOAS0.pessoas,equipes:PESSOAS0.equipes,versoes:{}};
}
function pessoasCapacidade(c) {
  const x=pessoasLer(c), out=Object.create(null);
  x.pessoas.forEach(p=>{
    const eq=x.equipes.filter(e=>e.v.nome===p.v.equipe);
    const hoje=CONF0.hoje, adm=p.v.adm||'', ate=p.v.ate||'';
    out[p.id]={fonteV:x.v,v:x.versoes[p.id]||1,nome:p.v.nome,sit:p.v.sit,adm,ate,
      disponivel:(!adm||adm<=hoje)&&(!ate||ate>=hoje),
      calendario:eq.length===1?eq[0].v.cal:null};
  });
  return out;
}
function pessoasValidarLista(xs, tipo) {
  if(!Array.isArray(xs)) throw Error('Cadastro de '+tipo+' inválido.');
  const ids=new Set(), nomes=new Set();
  xs.forEach(r=>{
    if(!r||typeof r.id!=='string'||!r.id||['__proto__','constructor','prototype'].includes(r.id)||ids.has(r.id)||!r.v||typeof r.v!=='object'||Array.isArray(r.v)) throw Error('Identificador inválido ou repetido no cadastro.');
    const nome=String(r.v.nome||'').trim().toLocaleLowerCase('pt-BR');
    if(!nome||nomes.has(nome)) throw Error('Nome vazio ou repetido no cadastro.');
    ids.add(r.id);nomes.add(nome);
  });
}
function pessoasGravar(c, pessoas, equipes, revisao, chave, ator) {
  const K=confLer(c),quem=confQuemAge(K,ator,'Salvar pessoas e equipes'),antes=pessoasLer(c);
  pessoasValidarLista(pessoas,'pessoas');pessoasValidarLista(equipes,'equipes');
  const ps=pessoasClonar(pessoas), es=pessoasClonar(equipes);
  const imp=JSON.stringify(['cad-pessoas',ps,es,revisao,quem]);
  const rep=confRepete(K,chave,imp,'Cadastro');if(rep)return rep;
  if(!Number.isInteger(revisao)||revisao!==antes.rev) throw Error('Pessoas ou equipes mudaram em outra tela. Reabra o cadastro e compare o rascunho; nada foi gravado.');
  const nomes=new Set(es.map(e=>e.v.nome));
  if(ps.some(p=>!['Ativa','Inativa'].includes(p.v.sit)||(p.v.sit==='Ativa'&&!nomes.has(p.v.equipe)))) throw Error('Confira a situação e a equipe de cada pessoa.');
  const versoes=Object.assign({},antes.versoes), base=pessoasCapacidade(c);
  const prox={v:PESSOAS0.v,rev:antes.rev+1,pessoas:ps,equipes:es,versoes};
  const atual=pessoasCapacidade({cadPessoas:prox});
  ps.forEach(p=>{
    const b=base[p.id],a=atual[p.id];
    versoes[p.id]=b?b.v+Number(b.sit!==a.sit||b.calendario!==a.calendario||b.adm!==a.adm||b.ate!==a.ate):1;
  });
  // IDs removidos conservam a versão para uma eventual recriação não revalidar partilha antiga.
  antes.pessoas.filter(p=>!atual[p.id]).forEach(p=>{versoes[p.id]=(versoes[p.id]||1)+1;});
  ps.filter(p=>!base[p.id]&&antes.versoes[p.id]).forEach(p=>{versoes[p.id]=antes.versoes[p.id]+1;});
  const alvo=confGarante(c),e=confEv(alvo,chave,imp,{tipo:'cad-pessoas',alvo:'CD-04',quem,t:'Pessoas e equipes atualizadas',ef:'Fonte atual do cadastro e da capacidade informada.'});
  c.cadPessoas=prox;
  return {msg:'Cadastro salvo · '+e.id,recibo:alvo.recibos[chave]};
}
