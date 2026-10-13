// Estado da tela é separado do recibo: rascunho por O.S./dia, inclusive ao fechar o detalhe.
function cdLinha(self, o, ap) {
  const c = cenGet(), k = o.id + ':' + ap.dia, fid = 'cd_' + o.id + '_' + ap.dia;
  const st = self.state, aberto = st.cdAtivo === k;
  const draft = (st.cdRascunhos || {})[k] || {};
  const set = patch => self.setState({cdRascunhos: Object.assign({}, self.state.cdRascunhos || {},
    {[k]: Object.assign({}, (self.state.cdRascunhos || {})[k] || {}, patch)})});
  const foco = suffix => setTimeout(() => {const el=document.getElementById(fid+suffix);if(el)el.focus();}, 0);
  const rec = ap.conferenciaDia, mudou = !!rec && rec.fato !== cdFato(c,o.id,ap.dia);
  const caso=rec&&rec.caso, resolver=!!rec&&rec.estado==='Não conforme';
  const referencia=()=>resolver?cdCasoReferencia(cenGet(),o.id,ap.dia):cdReferencia(cenGet(),o.id,ap.dia);
  const impedimento = cdImpedimento(c,o.id,ap.dia);
  const estado = ap.st===CEN_AP_DESC ? 'Fora do acumulado · histórico preservado' : mudou ? 'Reabrir conferência: dados alterados' : rec ? rec.estado : ap.st==='Conferido' ? 'Conferido · registro anterior sem recibo detalhado' : 'Conferência pendente';
  const recibo = rec ? rec.estado+' por '+rec.por+' · '+rec.at+(rec.motivo?' · '+rec.motivo:'')+(rec.revisaoPosterior?' · '+rec.revisaoPosterior:'') : '';
  const abrir = () => {
    const anterior=(self.state.cdRascunhos||{})[k];
    if (!anterior) set({decisao:'conferir',motivo:'',referencia:referencia(),erro:''});
    self.setState({cdAtivo:k}); foco(resolver?'_mot':'_dec');
  };
  const salvar = () => {
    const d=(self.state.cdRascunhos||{})[k]||{};
    const r=osRun(self,atual=>resolver?cdResolverRelato(atual,o.id,ap.dia,'vincular',d.motivo,d.referencia,g2perfil()):cdConferir(atual,o.id,ap.dia,d.decisao,d.motivo,d.referencia,g2perfil()),{},e=>set({erro:e}));
    if (!r.erro) {const ds=Object.assign({},self.state.cdRascunhos||{});delete ds[k];self.setState({cdRascunhos:ds,cdAtivo:null});foco('_open');}
    else foco('_erro');
  };
  return {cdVisivel:ap.st!=='Previsto',cdAberto:aberto,cdFechado:!aberto,cdId:fid,cdDecId:fid+'_dec',cdMotId:fid+'_mot',cdErrId:fid+'_erro',cdOpenId:fid+'_open',
    cdNormal:!resolver,cdResolver:resolver,cdAcao:resolver?'Vincular evidência e conferir dia':'Registrar conferência',cdAbrirNome:resolver?'Resolver divergência':'Conferir dia',
    cdCaso:caso?'Caso '+caso.id+' · '+caso.estado+' · '+caso.motivo:'Caso sem identificação; requer reavaliação.',
    cdTemCaso:!!caso,cdMotLabel:resolver?'Motivo e evidência do vínculo — obrigatório':'Motivo — obrigatório para divergência',
    cdTitulo:o.id+' · '+o.talhao+' · dia '+ap.dia+' · '+ap.d,
    cdEstado:estado,cdRecibo:recibo+(caso?' · Caso '+caso.id+': '+caso.estado:'' ),cdTemRecibo:!!rec,cdQuem:g2quem('conferente'),cdPode:g2papel(g2perfil(),'conferente')&&!impedimento,
    cdContexto:'Apontado por '+(ap.quem||'responsável não informado')+' · '+(ap.origem||'web')+' · '+(ap.sinc===false?'aguarda envio':'sincronizado'),
    cdComparacao:'Realizado neste dia: '+nf(ap.ha)+' ha'+(ap.h?' · '+nd(ap.h,1)+' h':'')+'. Área autorizada da O.S. inteira: '+nf(o.area)+' ha. Não há meta diária registrada.',
    cdImpedimento:impedimento,cdTemImpedimento:!!impedimento,cdDec:draft.decisao||'conferir',cdMot:draft.motivo||'',cdErro:draft.erro||'',cdTemErro:!!draft.erro,
    cdAbrir:abrir,cdDecSet:e=>set({decisao:e.target.value,erro:''}),cdMotSet:e=>set({motivo:e.target.value,erro:''}),cdSalvar:salvar,
    cdAtualizar:()=>{set({referencia:referencia(),erro:''});foco(resolver?'_mot':'_dec');},
    cdVoltar:()=>{self.setState({cdAtivo:null});foco('_open');}};
}
