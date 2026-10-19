// CONTROLE-02 fatia 1 · CMD-09. Decisão diária não refaz os efeitos do apontamento.
function cdAp(c, id, dia) {
  const o = c.ordens[id];
  const aps = o && (o.ap || []).filter(a => a.dia === dia);
  if (!aps || aps.length !== 1) throw new Error('Apontamento não encontrado ou ambíguo. Reabra a ordem.');
  return { o, ap: aps[0] };
}
function cdFato(c, id, dia) {
  const { o, ap } = cdAp(c, id, dia);
  const fato = Object.assign({}, ap);
  delete fato.conferenciaDia; delete fato.conferenciasAnteriores;
  // Conferir não muda o fato executado; permite recuperar o mesmo recibo.
  if (fato.st === 'Conferido') fato.st = 'Provisório';
  return JSON.stringify({ fato,
    consumos: (c.confs || []).filter(x => x.os === id && x.dia === dia) });
}
function cdBaseReferencia(c, id, dia) {
  return JSON.stringify({versao:c.ordens[id].versao, fato:cdFato(c,id,dia)});
}
function cdReferencia(c,id,dia) {
  const ap=cdAp(c,id,dia).ap;
  return JSON.stringify({fato:cdBaseReferencia(c,id,dia),recibos:(ap.conferenciasAnteriores||[]).length+(ap.conferenciaDia?1:0)});
}
function cdCasoReferencia(c,id,dia) {
  const caso=cdAp(c,id,dia).ap.conferenciaDia?.caso;
  return JSON.stringify({apontamento:cdReferencia(c,id,dia),caso:caso?.id,versao:caso?.versao});
}
function cdConteudo(ap) {
  // Conteúdo físico do relato; revisão técnica e recibos não são uma nova execução.
  return JSON.stringify([ap.dia,ap.d,ap.ha,ap.h,ap.parc,ap.cons,ap.inf,ap.origem,ap.chave,ap.quem,ap.obs]);
}
function cdValidarEvidencias(c,id,dia,ap) {
  if ((ap.div || []).length && !ap.rev) throw new Error('A divergência de dose aguarda revisão técnica do agrônomo.');
  if (cenConfAbertas(c, id).some(x => x.dia === dia)) throw new Error('O consumo deste dia aguarda decisão no Estoque.');
}
function cdImpedimento(c, id, dia) {
  const { o, ap } = cdAp(c, id, dia);
  if (!['Em execução', 'Em conferência'].includes(o.etapa)) return 'A ordem não admite conferência diária nesta fase.';
  if (ap.sinc === false) return 'Envie o apontamento do app quando houver sinal.';
  if (ap.st===CEN_AP_DESC && ap.conferenciaDia?.caso?.estado==='Em conferência' && ['estornado','anterior'].includes(ap.dec?.modo)) return '';
  if (!['Provisório', 'Conferido'].includes(ap.st)) return 'Resolva a duplicidade ou aguarde o apontamento executado.';
  return '';
}
function cdPendente(c, id) {
  const o = c.ordens[id];
  if (!o) return '';
  const pendentes = (o.ap || []).filter(a => a.conferenciaDia?.caso?.estado==='Em conferência' || cenApSomado(a) &&
    (!a.conferenciaDia ? a.st === 'Provisório' :
      (a.conferenciaDia.estado === 'Não conforme' || a.conferenciaDia.fato !== cdFato(c, id, a.dia))));
  return pendentes.length ? 'Conferência diária pendente: dia ' + pendentes.map(a => a.dia).join(', ') + '.' : '';
}
function cdConferir(c, id, dia, decisao, motivo, referencia, ator) {
  const quem = cenExigeAlc(ator, 'AL-12', 'Conferir o dia ' + dia + ' da ' + id);
  const { o, ap } = cdAp(c, id, dia);
  if (!['conferir', 'divergencia'].includes(decisao)) throw new Error('Escolha conferir ou registrar divergência.');
  const texto = String(motivo || '').trim();
  const estado = decisao === 'conferir' ? 'Conferido' : 'Não conforme';
  const atual = cdReferencia(c, id, dia);
  const anterior = ap.conferenciaDia;
  if (anterior && anterior.referencia === referencia && anterior.versao===o.versao && anterior.fato===cdFato(c,id,dia) && anterior.estado === estado && anterior.motivo === texto && anterior.por === quem) {
    return { msg: 'Conferência já registrada. Mesmo recibo, sem repetir efeitos.', repetido: true, recibo: anterior };
  }
  if (!referencia || referencia !== atual) throw new Error('O apontamento, o recibo ou a versão mudou. Reabra o dia e confira os dados atuais; o motivo foi preservado.');
  const impedimento = cdImpedimento(c, id, dia);
  if (impedimento) throw new Error(impedimento);
  if (anterior && anterior.estado === 'Não conforme') throw new Error('Resolva o caso do relato antes de conferir o dia. Conferência não substitui a decisão do caso.');
  if (decisao === 'divergencia' && !texto) throw new Error('Informe o motivo da divergência.');
  if (decisao === 'conferir') {
    cdValidarEvidencias(c,id,dia,ap);
  }
  const rp = cenRevisao(ator, ap.quem, 'apontou');
  const recibo = { estado, versao:o.versao, motivo: texto, por: quem, at: new Date().toISOString(), referencia: atual, fato: cdFato(c,id,dia), revisaoPosterior: rp || '' };
  if (decisao === 'divergencia') recibo.caso = {id:'CD-'+id+'-'+dia+'-'+((ap.conferenciasAnteriores||[]).length+1),comando:'CMD-50',estado:'Em conferência',versao:1,
    origem:{os:id,dia,chave:ap.chave||null},conteudo:cdConteudo(ap),motivo:texto,abertoPor:quem,at:recibo.at};
  if (anterior) ap.conferenciasAnteriores = (ap.conferenciasAnteriores || []).concat([anterior]);
  ap.conferenciaDia = recibo;
  ap.st = decisao === 'conferir' ? 'Conferido' : 'Provisório';
  return { msg: 'Dia ' + dia + ': ' + estado.toLowerCase() + ' por ' + quem + '. A fase da O.S. e os efeitos do apontamento permanecem.' + (rp ? ' ' + rp : ''), recibo };
}
// CMD-50, recorte documental: o relato já tem efeito. Vincular a evidência confirma
// o fato existente; não aceita outro turno, não recusa/estorna nem converte quantidades.
// As demais decisões exigem seus comandos físicos vinculados, fora desta fatia.
function cdResolverRelato(c,id,dia,decisao,motivo,referencia,ator) {
  const quem=cenExigeAlc(ator,'AL-12','Resolver o relato do dia '+dia+' da '+id);
  const {ap}=cdAp(c,id,dia), anterior=ap.conferenciaDia, caso=anterior&&anterior.caso;
  const texto=String(motivo||'').trim();
  if(!['vincular','arquivar'].includes(decisao)) throw new Error('Este recorte permite vincular evidência ao fato existente. A correção vinculada ainda não existe no protótipo: o caso fica aberto e a O.S. não encerra.');
  if(!caso) throw new Error('Sem caso identificado: reavalie o relato antes de decidir.');
  const atual=cdBaseReferencia(c,id,dia);
  if(caso.estado!=='Em conferência') {
    if(caso.decisao===decisao&&caso.motivoDecisao===texto&&caso.por===quem&&caso.referencia===referencia&&caso.apontamento===atual)
      return {msg:'Caso já resolvido. Mesmo recibo, sem repetir efeitos.',repetido:true,recibo:anterior};
    throw new Error('Caso já resolvido: outra decisão é conflito, nada gravado.');
  }
  if(!referencia||referencia!==cdCasoReferencia(c,id,dia)) throw new Error('O apontamento, o caso ou a versão mudou. Reveja os dados atuais; o motivo foi preservado.');
  if(!texto) throw new Error(decisao==='arquivar'?'Informe o motivo do arquivamento do caso substituído.':'Informe o motivo e a evidência que vinculam o relato ao fato existente.');
  const impedimento=cdImpedimento(c,id,dia);if(impedimento)throw new Error(impedimento);
  const arquivar=decisao==='arquivar';
  if(arquivar) {
    if(ap.st!==CEN_AP_DESC || !['estornado','anterior'].includes(ap.dec?.modo))throw new Error('Arquivar exige descarte por decisão de duplicidade registrada.');
  } else {
    if(ap.st===CEN_AP_DESC)throw new Error('Relato descartado: arquive o caso com a decisão de duplicidade, sem conferir como execução válida.');
    cdValidarEvidencias(c,id,dia,ap);
  }
  if(!arquivar && caso.conteudo!==cdConteudo(ap))throw new Error('O conteúdo do fato mudou: o vínculo documental não corrige quantidades. A correção vinculada ainda não existe no protótipo: o caso fica aberto e a O.S. não encerra.');
  const rp=cenRevisao(ator,ap.quem,'apontou'), at=new Date().toISOString();
  const resolvido=Object.assign({},caso,{estado:arquivar?'Arquivado':'Vinculado',descarte:arquivar?Object.assign({},ap.dec):null,versao:caso.versao+1,decisao,motivoDecisao:texto,por:quem,atDecisao:at,referencia,apontamento:atual,revisaoPosterior:rp||''});
  const recibo={estado:arquivar?'Arquivado':'Conferido',versao:c.ordens[id].versao,motivo:texto,por:quem,at,referencia:atual,fato:cdFato(c,id,dia),revisaoPosterior:rp||'',caso:resolvido};
  ap.conferenciasAnteriores=(ap.conferenciasAnteriores||[]).concat([anterior]);ap.conferenciaDia=recibo;if(!arquivar)ap.st='Conferido';
  return {msg:arquivar?caso.id+' arquivado: relato descartado por decisão de duplicidade registrada. Histórico e efeitos preservados.':caso.id+' vinculado ao fato do dia '+dia+' e conferido por '+quem+'. Nenhuma nova área, hora ou baixa de consumo.'+(rp?' '+rp:''),recibo};
}
