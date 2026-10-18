'use strict';

/** Agenda sequencial estimada, sem mutação, aprovação ou liberação de O.S.
 * Instantes: milissegundos Unix inteiros; o adaptador resolve data e fuso.
 * sequencia: [{id, areaHa, rendimentoHaH, janelaInicio, janelaFim, kmAnterior}].
 * parametros: {inicio, velocidadeKmh, fonte}. Não há velocidade padrão.
 * kmAnterior inclui o primeiro trecho (zero explícito se já estiver no local).
 * Cada duração é arredondada para cima em 1 ms. Espera pela janela é permitida;
 * operação é contínua, sem divisão em turnos, pausas ou reordenação automática.
 * Não inclui troca de calda nem lavagem. Espera compõe o tempo decorrido da
 * jornada, que não tem limite próprio nesta estimativa (somente as janelas).
 * Viável significa apenas caber nestas premissas temporais, não autorização.
 */
function frAgenda(sequencia, parametros) {
  const linhas = [];
  const positivo = n => typeof n === 'number' && Number.isFinite(n) && n > 0;
  const instante = n => Number.isSafeInteger(n) && Math.abs(n) <= 8640000000000000;
  const p = parametros || {};
  const premissas = {inicio: p.inicio, velocidadeKmh: p.velocidadeKmh, fonte: p.fonte,
    incluiTrocaCaldaLavagem: false, incluiPausas: false, limiteJornadaMs: null,
    esperaIntegraJornada: true};
  const resultado = (status, id, motivo) => ({status, id, motivo, linhas, premissas});
  const sem = (id, motivo) => resultado('sem_conta', id, motivo);
  if (!Array.isArray(sequencia) || !sequencia.length) return sem(null, 'Sequência ausente ou vazia');
  if (!instante(p.inicio)) return sem(null, 'Informe o início da jornada como instante absoluto');
  if (!positivo(p.velocidadeKmh) || typeof p.fonte !== 'string' || !p.fonte.trim()) {
    return sem(null, 'Informe velocidade de deslocamento em km/h e sua fonte');
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
    const chegada = anterior + deslocamentoMs;
    const inicio = Math.max(chegada, o.janelaInicio);
    const fim = inicio + operacaoMs;
    if (!Number.isSafeInteger(operacaoMs) || operacaoMs <= 0 ||
        !Number.isSafeInteger(deslocamentoMs) || !instante(chegada) || !instante(fim)) {
      return sem(o.id, 'Duração ou horário fora do intervalo calculável');
    }
    const cabe = fim <= o.janelaFim;
    linhas.push({id: o.id, inicio, fim, chegada, esperaMs: inicio - chegada,
      operacaoMs, deslocamentoMs, janelaFim: o.janelaFim, status: cabe ? 'cabe' : 'inviavel'});
    if (!cabe) return resultado('inviavel', o.id,
      'Termina ' + new Date(fim).toISOString() + ', janela fecha ' + new Date(o.janelaFim).toISOString());
    anterior = fim;
  }
  return resultado('viavel', null, 'Sequência cabe nas premissas temporais informadas');
}

if (typeof module !== 'undefined' && module.exports) module.exports = {frAgenda};
