'use strict';

/** Agenda sequencial estimada; não aprova, libera ou altera O.S.
 * Instantes absolutos em ms. O adaptador resolve o fuso da fazenda.
 * parametros.turnos: [[inicio,fim],...], obrigatórios, ordenados e sem sobreposição.
 * Deslocamento consome turno; operação consome turno ∩ janela da O.S.; podem pausar.
 * Durações arredondadas para cima em 1 ms. Sem lavagem, troca de calda ou clima.
 * fim:null indica trabalho incompleto; não projeta término fora da janela.
 */
function frAgenda(sequencia, parametros) {
  const linhas = [];
  const positivo = n => typeof n === 'number' && Number.isFinite(n) && n > 0;
  const instante = n => Number.isSafeInteger(n) && Math.abs(n) <= 8640000000000000;
  const p = parametros || {};
  const premissas = {inicio: p.inicio, velocidadeKmh: p.velocidadeKmh, fonte: p.fonte,
    turnos: Array.isArray(p.turnos) ? p.turnos.map(t=>Array.isArray(t)?t.slice():t) : null,
    incluiTrocaCaldaLavagem: false, incluiPausas: true, esperaIntegraJornada: true};
  const resultado = (status, id, motivo) => ({status, id, motivo, linhas, premissas});
  const sem = (id, motivo) => resultado('sem_conta', id, motivo);
  if (!Array.isArray(sequencia) || !sequencia.length) return sem(null, 'Sequência ausente ou vazia');
  if (!instante(p.inicio)) return sem(null, 'Informe o início da jornada como instante absoluto');
  if (!positivo(p.velocidadeKmh) || typeof p.fonte !== 'string' || !p.fonte.trim()) {
    return sem(null, 'Informe velocidade de deslocamento em km/h e sua fonte');
  }
  if (!Array.isArray(p.turnos) || !p.turnos.length) return sem(null, 'Informe os turnos da jornada');
  let fimAnterior = null;
  for (const t of p.turnos) {
    if (!Array.isArray(t) || t.length !== 2 || !instante(t[0]) || !instante(t[1]) ||
        t[1] <= t[0] || (fimAnterior !== null && t[0] < fimAnterior)) {
      return sem(null, 'Turnos inválidos: use intervalos ordenados, não vazios e sem sobreposição');
    }
    fimAnterior = t[1];
  }
  const ids = new Set();
  for (const o of sequencia) {
    if (!o || typeof o.id !== 'string' || !o.id.trim() || ids.has(o.id)) {
      return sem(o && o.id || null, 'Identificador ausente ou repetido na sequência');
    }
    ids.add(o.id);
  }
  let anterior = p.inicio;
  for (const o of sequencia) {
    if (!positivo(o.areaHa) || !positivo(o.rendimentoHaH)) {
      return sem(o.id, 'Área ou rendimento em ha/h ausente ou inválido');
    }
    if (!instante(o.janelaInicio) || !instante(o.janelaFim) || o.janelaFim <= o.janelaInicio) {
      return sem(o.id, 'Janela de início/fim ausente ou inválida');
    }
    if (typeof o.kmAnterior !== 'number' || !Number.isFinite(o.kmAnterior) || o.kmAnterior < 0) {
      return sem(o.id, 'Distância do trecho anterior ausente ou inválida');
    }
    const operacaoMs = Math.ceil(o.areaHa / o.rendimentoHaH * 3600000);
    const deslocamentoMs = Math.ceil(o.kmAnterior / p.velocidadeKmh * 3600000);
    if (!Number.isSafeInteger(operacaoMs) || operacaoMs <= 0 ||
        !Number.isSafeInteger(deslocamentoMs) || deslocamentoMs < 0 ||
        !instante(anterior + deslocamentoMs + operacaoMs)) {
      return sem(o.id, 'Duração ou horário fora do intervalo calculável');
    }
    let cursor = anterior, pausaMs = 0, esperaMs = 0;
    let viagem = deslocamentoMs, trabalho = operacaoMs;
    let chegada = viagem ? null : cursor, inicio = null, fim = null;
    // A janela agronômica protege a operação; viajar antes dela é permitido no turno.
    for (const t of p.turnos) {
      if (!viagem) break;
      const a = Math.max(cursor, t[0]), b = t[1];
      if (a >= b) continue;
      pausaMs += a - cursor; cursor = a;
      const deslocar = Math.min(viagem, b - cursor);
      viagem -= deslocar; cursor += deslocar;
      if (!viagem) chegada = cursor;
    }
    if (!viagem) {
      // Espera no destino dentro de turno; o restante do tempo parado é pausa.
      const abertura = Math.max(cursor, o.janelaInicio);
      esperaMs = p.turnos.reduce((s,t)=>s+Math.max(0,Math.min(t[1],abertura)-Math.max(t[0],cursor)),0);
      pausaMs += abertura - cursor - esperaMs; cursor = abertura;
      for (const t of p.turnos) {
        const a = Math.max(cursor, t[0]), b = Math.min(t[1], o.janelaFim);
        if (a >= b) continue;
        pausaMs += a - cursor; cursor = a;
        if (inicio === null) inicio = cursor;
        const operar = Math.min(trabalho, b - cursor);
        trabalho -= operar; cursor += operar;
        if (!trabalho) { fim = cursor; break; }
      }
    }
    const cabe = trabalho === 0;
    linhas.push({id:o.id, chegada, inicio, fim, esperaMs, pausaMs, operacaoMs, deslocamentoMs,
      operacaoExecutadaMs:operacaoMs-trabalho, deslocamentoExecutadoMs:deslocamentoMs-viagem,
      janelaFim:o.janelaFim, status:cabe?'cabe':'inviavel'});
    if (!cabe) return resultado('inviavel',o.id,
      viagem ? 'Sem turno para o deslocamento' : p.turnos[p.turnos.length-1][1] < o.janelaFim ? 'Sem turno até o fim da janela' : 'Trabalho não termina na janela da O.S.');
    anterior = fim;
  }
  return resultado('viavel', null, 'Sequência cabe nas premissas temporais informadas');
}

if (typeof module !== 'undefined' && module.exports) module.exports = {frAgenda};
