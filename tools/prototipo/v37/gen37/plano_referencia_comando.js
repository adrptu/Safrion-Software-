/* CONTROLE-02/F2: transação técnica no cenário compartilhado.
 * A composição fornece validarDominio(self,safra,c): {impedimentos:string[]}.
 * Sem esse adaptador e AL-18 não publica. Não substitui validação agronômica.
 */
const PlanoReferenciaComando = (() => {
  'use strict';
  const clone = x => JSON.parse(JSON.stringify(x));
  const contextoIgual = (a,b) => a.fazenda===b.fazenda && a.safra===b.safra;
  function pedidoValido(self,p) {
    if (!p || typeof p.chave!=='string' || !p.chave.trim() || p.chave.length>200) throw new Error('Intenção de publicação ausente ou inválida. Abra novamente a prévia.');
    if (p.esperada!==null && (typeof p.esperada!=='string' || !/^R[1-9]\d*$/.test(p.esperada))) throw new Error('Referência esperada inválida. Confira a prévia.');
    const previa=JSON.parse(PlanoReferencia.bytes(p.previa));
    const s=safById(self,p.safra);
    if (s && (typeof s.v.faz!=='string' || !s.v.faz.trim())) throw new Error('Fazenda da safra ausente. Confira o cadastro antes de publicar. Nada foi alterado.');
    if (!s || self.state.saf!==p.safra || previa.contexto.safra!==p.safra || previa.contexto.fazenda!==s.v.faz) throw new Error('Escolha a fazenda e a safra da prévia. Nada foi alterado.');
    if (s.ro || s.v.estado==='Encerrada') throw new Error('Safra encerrada: versões disponíveis somente para consulta.');
    const por=cenExigeAlc(p.ator,'AL-18','Publicar referência técnica');
    const ator=g2pf(p.ator);
    return {previa,por,key:'PLANO-REF:'+p.chave,imp:JSON.stringify([ator.k,p.safra,p.esperada,previa])};
  }
  function historico(c,contexto) {
    const listas=c.planoReferencias||[];
    if (!Array.isArray(listas)) throw new Error('Histórico técnico inválido. Nada foi alterado.');
    const encontrados=listas.filter(x=>contextoIgual(x.contexto,contexto));
    if (encontrados.length>1) throw new Error('Histórico técnico duplicado. Nada foi alterado.');
    return encontrados[0]||null;
  }
  function recuperar(c,x) {
    const r=cenIdem(c,x.key,x.imp,'CMD-02',()=>{throw new Error('Recibo técnico não encontrado.');});
    const meta=r.recibo&&r.recibo.plano;
    const h=meta&&historico(c,meta.contexto);
    const v=h&&h.versoes.find(v=>v.id===meta.id);
    if (!v) throw new Error('Recibo técnico sem versão recuperável. Nada foi alterado.');
    return {msg:'Referência '+v.id+' já registrada. Nenhuma nova versão foi criada.',repetido:true,nova:meta.nova,versao:clone(v),recibo:clone(r.recibo)};
  }
  function registrar(c,self,p,validarDominio) {
    const x=pedidoValido(self,p);
    if (c.recibos && Object.prototype.hasOwnProperty.call(c.recibos,x.key)) return recuperar(c,x);
    const ctx=PlanoReferencia.validarContexto(self,p.safra,p.ator,x.previa);
    if (typeof validarDominio!=='function') throw new Error('Validação do plano indisponível. Nenhuma referência foi publicada.');
    const dominio=validarDominio(self,p.safra,c);
    if (!dominio || !Array.isArray(dominio.impedimentos) || !dominio.impedimentos.every(x=>typeof x==='string'&&x.trim())) throw new Error('Validação do plano incompleta. Nenhuma referência foi publicada.');
    if (dominio.impedimentos.length) throw new Error('Revise o plano antes de publicar: '+dominio.impedimentos.join(' '));
    const contexto=ctx.atual.contexto, h=historico(c,contexto);
    const preparada=PlanoReferencia.prepararVersao(h?h.versoes:[],ctx.atual,p.esperada,x.por,new Date().toISOString());
    const r=cenIdem(c,x.key,x.imp,'CMD-02',()=>{
      let destino=h;
      if (!destino) { destino={contexto:clone(contexto),versoes:[],orcamentoRevisar:false}; (c.planoReferencias||(c.planoReferencias=[])).push(destino); }
      let versao=clone(preparada.versao);
      if (preparada.nova) {
        versao.sq=(c.rev||0)+1;
        destino.versoes.push(versao);
        if (destino.versoes.length>1) destino.orcamentoRevisar=true;
      }
      return {msg:preparada.nova?'Referência '+versao.id+' registrada. Não aprova orçamento nem autoriza O.S.':'O plano já corresponde à referência '+versao.id+'. Nenhuma nova versão foi criada.',nova:preparada.nova,versao};
    });
    c.recibos[x.key].plano={contexto:clone(contexto),id:r.versao.id,nova:r.nova};
    return {...r,recibo:clone(c.recibos[x.key])};
  }
  function publicar(self,p,validarDominio) {
    try {
      if (typeof CEN_GRAVA_ERRO!=='string' || typeof cenIdem!=='function') throw new Error('Gravação segura indisponível nesta versão. Nenhuma referência foi publicada.');
      // Reenvio já persistido não precisa de outra gravação nem incrementa rev.
      const atual=cenGet(), x=pedidoValido(self,p);
      if (atual.recibos && Object.prototype.hasOwnProperty.call(atual.recibos,x.key)) return recuperar(atual,x);
      return cenMudar(self,c=>registrar(c,self,p,validarDominio),{estrito:true});
    } catch(e) { const erro=String(e.message||e); if(self) self.setState({g2toast:erro}); return {erro}; }
  }
  return Object.freeze({publicar,historico});
})();
