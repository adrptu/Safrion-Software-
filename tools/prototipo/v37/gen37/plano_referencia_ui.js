/* Consulta de retratos da fatia2. Não publica nem grava no cenário.
 * publicadas é fornecido pelo comando compartilhado quando composto; padrão vazio, sem histórico fictício.
 */
const PR_LABELS = {safra:'Safra', cultivo:'Cultivo', plano:'Plano agronômico', atividade:'Atividade', produto:'Insumo',
  configuracao:'Configuração', recurso:'Recurso', calendario:'Calendário', nome:'Nome', ini:'Início', fim:'Fim',
  talhao:'Talhão', local:'Local', tipo:'Tipo', cult:'Cultura', cultura:'Cultura', var:'Variedade', plantio:'Plantio',
  colheita:'Colheita prevista', ciclo:'Ciclo', origem:'Origem', area:'Área', meta:'Meta', ajustesLocais:'Ajustes locais',
  versao:'Versão', operacao:'Operação', gatilho:'Gatilho', data:'Data', incluida:'Incluída por recomendação',
  horasPlanejadas:'Horas planejadas', configuracoes:'Configurações', grupo:'Grupo', dose:'Dose', quantidade:'Quantidade',
  preco:'Preço de referência', laudo:'Laudo', seq:'Em sequência', rend:'Rendimento', part:'Parte da área', jan:'Janela',
  custo_h:'Custo por hora', diesel:'Diesel', pess:'Pessoas', troca:'Tempo de troca', ativos:'Ativos', recursos:'Recursos',
  pessoas:'Equipe de pessoas', un:'Unidades', jornada:'Jornada', turnos:'Turnos', disp:'Disponibilidade', abs:'Absenteísmo',
  meses:'Meses', diasUteis:'Dias úteis'};
function planoRefTexto(valor) {
  if (valor === null || valor === undefined || valor === '') return 'Não informado';
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não';
  if (typeof valor === 'number') return valor.toLocaleString('pt-BR', {maximumFractionDigits:8});
  if (Array.isArray(valor)) return valor.length ? valor.map(planoRefTexto).join(' · ') : 'Nenhum';
  if (typeof valor === 'object') {
    if (Object.prototype.hasOwnProperty.call(valor,'unidade')) return planoRefTexto(valor.valor) + ' ' + valor.unidade;
    const itens=Object.keys(valor).map(k=>(PR_LABELS[k]||k)+': '+planoRefTexto(valor[k]));
    return itens.length ? itens.join(' · ') : 'Nenhum';
  }
  return String(valor);
}
function planoRefLinhas(atual, anterior, busca, completo) {
  const entidades = new Map([...((anterior||{}).entidades||[]),...atual.entidades].map(e=>[JSON.stringify([e.tipo,e.id]),e]));
  const nome=(e)=> {
    const x=entidades.get(JSON.stringify([e.tipo,e.id])), c=x.campos;
    const cu=entidades.get(JSON.stringify(['cultivo',c.cultivo]));
    if (c.nome || c.local || c.produto) return (cu?cu.campos.local+' · ':'')+(c.nome || c.local || c.produto);
    if (e.tipo==='calendario') return 'Capacidade dos recursos';
    const cultivo=entidades.get(JSON.stringify(['cultivo',c.cultivo]));
    return (cultivo ? cultivo.campos.local+' · ' : '')+(c.atividade||e.id);
  };
  const exibir=(campo,valor)=>{
    if(campo==='ajustesLocais') return Object.keys(valor||{}).length+' ajustes locais; doses e origens nos insumos.';
    if(campo==='gatilho') return gatLabel(valor);
    const tipo={cultivo:'cultivo',plano:'plano'}[campo];
    const e=tipo&&entidades.get(JSON.stringify([tipo,valor]));
    return e?nome(e):planoRefTexto(valor);
  };
  let rows=[];
  if (anterior && !completo) {
    rows=PlanoReferencia.comparar(anterior,atual).map((d,i)=>({id:'d'+i, entidade:(PR_LABELS[d.tipo]||d.tipo)+' · '+nome(d),
      campo:d.campo?(PR_LABELS[d.campo]||d.campo):'Registro', estado:d.estado,
      antes:d.campo?(d.antes.presente?exibir(d.campo,d.antes.valor):'Ausente'):(d.antes?'Registro removido':'Ausente'),
      depois:d.campo?(d.depois.presente?exibir(d.campo,d.depois.valor):'Ausente'):(d.depois?'Registro incluído; consulte o conteúdo completo.':'Ausente'),
      aviso:d.unidadesIncompativeis?'Unidades diferentes; valores não subtraídos.':''}));
  } else {
    atual.entidades.forEach(e=>Object.keys(e.campos).forEach(campo=>rows.push({id:JSON.stringify([e.tipo,e.id,campo]),
      entidade:(PR_LABELS[e.tipo]||e.tipo)+' · '+nome(e), campo:PR_LABELS[campo]||campo, estado:'', antes:'',
      depois:exibir(campo,e.campos[campo]), aviso:''})));
  }
  const q=String(busca||'').toLocaleLowerCase('pt-BR').trim();
  return q ? rows.filter(r=>[r.entidade,r.campo,r.estado,r.antes,r.depois].join(' ').toLocaleLowerCase('pt-BR').includes(q)) : rows;
}
function planoRefAbrir(self, evento, publicadas=[]) {
  const safra=self.state.saf;
  try {
    const atual=PlanoReferencia.projetar(self,safra);
    // Recusa histórico de outra safra, versão sem identificação ou mesmo ID repetido.
    const ids=new Set();
    const historico=publicadas.map(p=>{
      if (!p.id || ids.has(p.id) || !p.em || !p.por) throw new Error('Histórico sem identificação de versão, data ou responsável.');
      ids.add(p.id); PlanoReferencia.comparar(p.retrato,atual);
      return JSON.parse(JSON.stringify(p));
    });
    self.__prFoco=evento&&evento.currentTarget || document.getElementById('pr_abrir');
    self.setState({prPainel:{safra,atual,publicadas:historico,versao:historico.length?historico[0].id:'',busca:'',completo:!historico.length}});
    requestAnimationFrame(()=>{const el=document.getElementById('pr_x'); if(el) el.focus();});
  } catch(e) { self.setState({g2toast:'Não foi possível consultar as versões: '+e.message}); }
}
function planoRefVals(self,v) {
  // Porta de consulta para contraprovas, como __solo/__safSelf; não oferece comandos de gravação.
  window.__planoRef={projetar:()=>PlanoReferencia.projetar(self,self.state.saf),abrir:publicadas=>planoRefAbrir(self,null,publicadas)};
  const p=self.state.prPainel;
  v.pr_has=!!self.state.saf; v.pr_abrir=(e)=>planoRefAbrir(self,e);
  v.pr_open=!!p; v.pr_titulo='Versões do plano';
  v.pr_close=()=>{
    const alvo=self.__prFoco;
    self.setState({prPainel:null});
    requestAnimationFrame(()=>{const el=alvo&&alvo.isConnected?alvo:document.getElementById('pr_abrir'); if(el) el.focus({preventScroll:true});});
  };
  v.pr_key=e=>{
    if(e.key==='Escape'){e.preventDefault();e.stopPropagation();v.pr_close();return;}
    if(e.key!=='Tab') return;
    const root=e.currentTarget;
    const xs=Array.from(root.querySelectorAll('button,input,select,[tabindex="0"]')).filter(x=>!x.disabled&&x.offsetParent!==null);
    const i=xs.indexOf(document.activeElement);
    if(xs.length&&((e.shiftKey&&i<=0)||(!e.shiftKey&&i===xs.length-1))){e.preventDefault();xs[e.shiftKey?xs.length-1:0].focus();}
  };
  if(!p) return;
  const alterar=patch=>self.setState({prPainel:{...self.state.prPainel,...patch}});
  const anterior=p.publicadas.find(x=>x.id===p.versao);
  v.pr_sub=p.atual.contexto.fazenda+' · '+(entidadeSafra=>entidadeSafra?entidadeSafra.campos.nome:p.safra)(p.atual.entidades.find(e=>e.tipo==='safra'));
  v.pr_estado=anterior?(p.historico?'Consultando '+anterior.id:'Comparando '+anterior.id+' com o plano atual'):'Sem referência registrada';
  v.pr_nota=anterior?'Referência técnica de '+anterior.por+' em '+anterior.em+'. Não autoriza orçamento nem execução de O.S.':'Este conteúdo é uma consulta do plano atual, ainda não publicado. Não autoriza orçamento nem execução de O.S.';
  v.pr_temHistorico=!!p.publicadas.length;
  v.pr_versoes=p.publicadas.map((x,i)=>({id:x.id,nome:x.id+(i===0?' · referência original':' · revisão')+' · '+x.em}));
  v.pr_versao=p.versao; v.pr_trocar=e=>alterar({versao:e.target.value});
  v.pr_busca=p.busca; v.pr_buscar=e=>alterar({busca:e.target.value});
  v.pr_completo=p.completo; v.pr_modo=()=>alterar({completo:!p.completo,historico:false});
  v.pr_historico=()=>alterar({completo:true,historico:true});
  v.pr_modoTexto=p.completo?'Mostrar só diferenças':'Consultar conteúdo completo';
  v.pr_comparando=!!anterior&&!p.completo;
  v.pr_valorTitulo=p.historico?'Na versão selecionada':'No plano atual';
  v.pr_linhas=planoRefLinhas(p.historico&&anterior?anterior.retrato:p.atual,anterior&&anterior.retrato,p.busca,p.completo);
  v.pr_vazio=!v.pr_linhas.length;
  v.pr_vazioTexto=p.busca?'Nenhum resultado. Altere a busca para consultar o plano.':'Nenhuma diferença em relação à versão selecionada.';
  v.pr_contagem=v.pr_linhas.length+' registros exibidos';
}
