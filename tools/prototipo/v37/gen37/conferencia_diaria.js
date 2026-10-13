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
function cdReferencia(c, id, dia) {
  return JSON.stringify({versao:c.ordens[id].versao, fato:cdFato(c,id,dia)});
}
function cdImpedimento(c, id, dia) {
  const { o, ap } = cdAp(c, id, dia);
  if (!['Em execução', 'Em conferência'].includes(o.etapa)) return 'A ordem não admite conferência diária nesta fase.';
  if (ap.sinc === false) return 'Envie o apontamento do app quando houver sinal.';
  if (!['Provisório', 'Conferido'].includes(ap.st)) return 'Resolva a duplicidade ou aguarde o apontamento executado.';
  return '';
}
function cdPendente(c, id) {
  const o = c.ordens[id];
  if (!o) return '';
  const pendentes = (o.ap || []).filter(a => cenApSomado(a) &&
    (!a.conferenciaDia ? a.st === 'Provisório' :
      (a.conferenciaDia.estado === 'Não conforme' || a.conferenciaDia.fato !== cdFato(c, id, a.dia))));
  return pendentes.length ? 'Reveja a conferência diária: dia ' + pendentes.map(a => a.dia).join(', ') + '.' : '';
}
function cdConferir(c, id, dia, decisao, motivo, referencia, ator) {
  const quem = cenExige(ator, 'conferente', 'Conferir o dia ' + dia + ' da ' + id);
  const { o, ap } = cdAp(c, id, dia);
  if (!['conferir', 'divergencia'].includes(decisao)) throw new Error('Escolha conferir ou registrar divergência.');
  const texto = String(motivo || '').trim();
  const estado = decisao === 'conferir' ? 'Conferido' : 'Não conforme';
  const atual = cdReferencia(c, id, dia);
  if (!referencia || referencia !== atual) throw new Error('O apontamento ou a versão mudou. Reabra o dia e confira os dados atuais; o motivo foi preservado.');
  const anterior = ap.conferenciaDia;
  if (anterior && anterior.referencia === atual && anterior.estado === estado && anterior.motivo === texto && anterior.por === quem) {
    return { msg: 'Conferência já registrada. Mesmo recibo, sem repetir efeitos.', repetido: true, recibo: anterior };
  }
  const impedimento = cdImpedimento(c, id, dia);
  if (impedimento) throw new Error(impedimento);
  if ((decisao === 'divergencia' || (anterior && anterior.estado === 'Não conforme')) && !texto) throw new Error('Informe o motivo da divergência ou como ela foi resolvida.');
  if (decisao === 'conferir') {
    if ((ap.div || []).length && !ap.rev) throw new Error('A divergência de dose aguarda revisão técnica do agrônomo.');
    if (cenConfAbertas(c, id).some(x => x.dia === dia)) throw new Error('O consumo deste dia aguarda decisão no Estoque.');
  }
  const rp = cenRevisao(ator, ap.quem, 'apontou');
  const recibo = { estado, motivo: texto, por: quem, at: new Date().toISOString(), referencia: atual, fato: cdFato(c,id,dia), revisaoPosterior: rp || '' };
  if (anterior) ap.conferenciasAnteriores = (ap.conferenciasAnteriores || []).concat([anterior]);
  ap.conferenciaDia = recibo;
  ap.st = decisao === 'conferir' ? 'Conferido' : 'Provisório';
  return { msg: 'Dia ' + dia + ': ' + estado.toLowerCase() + ' por ' + quem + '. A fase da O.S. e os efeitos do apontamento permanecem.' + (rp ? ' ' + rp : ''), recibo };
}
