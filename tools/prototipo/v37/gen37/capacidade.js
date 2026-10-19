/* EX-53 D11b / P10: dedicação explícita por pessoa e especialidade.
   Comando só dentro de cenMudar estrito; editor CF-06 e fonte CD-04. */
function capacidadeRegistro(c, id) {
  if (typeof CONF0 !== 'undefined' && c && c.conf && c.conf.v !== CONF0.v) return null;
  const rs=c&&c.conf&&c.conf.capacidadePessoas;
  return rs&&Object.prototype.hasOwnProperty.call(rs,id)?rs[id]:null;
}
function capacidadeDe(c, esp) {
  if(typeof pessoasCapacidade!=='function'||typeof PESSOAS0==='undefined') return null;
  if(typeof CONF0!=='undefined'&&c&&c.conf&&c.conf.v!==CONF0.v) return null;
  return capacidadeSomar(c&&c.conf&&c.conf.capacidadePessoas,pessoasCapacidade(c),esp);
}
function capacidadeGravar(c,id,novo,motivo,versao,pessoaV,chave,ator) {
  const K=confLer(c),quem=confExigeA(K,ator,{modo:'um',papeis:['gestor']},'Configurar capacidade');
  motivo=String(motivo||'').trim();if(!motivo)throw Error('Informe o motivo da dedicação, mudança ou retirada.');
  if(typeof id!=='string'||!id||['__proto__','constructor','prototype'].includes(id))throw Error('Pessoa inválida.');
  if(novo!==null&&(!novo||typeof novo!=='object'||Array.isArray(novo)||!Object.keys(novo).length||Object.keys(novo).some(k=>!CAP_ESPECIALIDADES.includes(k)))) throw Error('Informe a dedicação nas especialidades do cadastro.');
  const dados=novo===null?null:Object.fromEntries(Object.keys(novo).sort().map(k=>[k,novo[k]]));
  const imp=JSON.stringify(['capacidade',id,dados,motivo,versao,pessoaV,quem]);
  const rep=confRepete(K,chave,imp,'Capacidade');if(rep)return rep;
  const antes=capacidadeRegistro(c,id),v=antes?antes.v:0;
  if(!Number.isInteger(versao)||versao!==v)throw Error('A dedicação mudou. Compare o registro vigente antes de salvar.');
  if(novo!==null){
    const ps=pessoasCapacidade(c),p=Object.prototype.hasOwnProperty.call(ps,id)?ps[id]:null;
    if(!p||p.sit!=='Ativa'||p.disponivel===false||p.v!==pessoaV)throw Error('Confira a situação, a vigência do contrato e o calendário da pessoa antes de definir a dedicação.');
    if(!capacidadePartilha(dados,capacidadeJornada(p.calendario)))throw Error('A soma das especialidades deve caber na jornada semanal conhecida da pessoa.');
  }else if(!antes||antes.ativa===false)throw Error('A pessoa já está sem dedicação configurada.');
  const alvo=confGarante(c),e=confEv(alvo,chave,imp,{tipo:'capacidade',alvo:id,quem,t:novo===null?'Dedicação retirada':'Dedicação semanal definida',motivo,antes:antes?JSON.parse(JSON.stringify(antes)):null,depois:dados,ef:'Capacidade disponível para o backlog; não altera a jornada da equipe.'});
  if(!alvo.capacidadePessoas)alvo.capacidadePessoas={};
  alvo.capacidadePessoas[id]={fonteV:PESSOAS0.v,ativa:novo!==null,alocacoes:dados||{},pessoaV,v:v+1,quem,motivo,recibo:e.id,d:e.d,at:e.at};
  return {msg:(novo===null?'Dedicação retirada':'Dedicação salva')+' · '+e.id,recibo:alvo.recibos[chave]};
}
/* Teto nominal somente quando o cadastro contém dias e horários inequívocos.
   Escala cíclica sem data de referência não define as horas de uma semana. */
function capacidadeJornada(calendario) {
  const m = /^seg–(sex|sáb) · (\d{2})–(\d{2})h$/.exec(calendario || '');
  if (!m) return null;
  const inicio = Number(m[2]), fim = Number(m[3]);
  if (inicio < 0 || fim > 24 || fim <= inicio) return null;
  return {hhSemana:(fim - inicio) * (m[1] === 'sex' ? 5 : 6), fonte:calendario};
}
function capacidadePartilha(alocacoes, teto) {
  if (!teto || !Number.isFinite(teto.hhSemana) || teto.hhSemana <= 0) return false;
  if (!alocacoes || typeof alocacoes !== 'object' || Array.isArray(alocacoes)) return false;
  const horas = Object.values(alocacoes);
  if (horas.some(h => typeof h !== 'number' || !Number.isFinite(h) || h <= 0)) return false;
  const soma = horas.reduce((a,b) => a+b,0);
  return Number.isFinite(soma) && soma <= teto.hhSemana;
}
/* Contrato interno da agregação: fonte atual normalizada por id estável, nunca por
   nome/habilitação. A ligação CD-04 fornece calendário da equipe vigente.
   Um registro obsoleto da especialidade suspende o total: não mostra soma parcial
   como capacidade completa. Pessoas inativas/retiradas não compõem a oferta. */
function capacidadeSomar(registros, pessoas, esp) {
  if (!registros || !pessoas || typeof esp !== 'string' || !esp) return null;
  let total = 0, n = 0;
  for (const [id, r] of Object.entries(registros)) {
    if (!r || r.ativa === false) continue;
    const a = r.alocacoes;
    if (!a || !Object.prototype.hasOwnProperty.call(a, esp)) continue;
    if (!Object.prototype.hasOwnProperty.call(pessoas, id)) return null;
    const p = pessoas[id];
    if (!p || p.sit === 'Inativa') continue;
    if ((p.fonteV && r.fonteV !== p.fonteV) || p.sit !== 'Ativa' || p.disponivel===false || !Number.isInteger(p.v) || r.pessoaV !== p.v ||
        !Number.isInteger(r.v) || r.v < 1 || !r.quem || !r.motivo || !r.recibo ||
        !capacidadePartilha(a, capacidadeJornada(p.calendario))) return null;
    total += a[esp]; n++;
  }
  return n && Number.isFinite(total) && total > 0
    ? {hhSemana:total, pessoas:n, fonte:'Dedicação semanal informada por pessoa e especialidade'} : null;
}
