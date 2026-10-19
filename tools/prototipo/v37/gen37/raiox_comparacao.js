/* RX-1: comparação observacional e seguimento. Contrato e limites em RX-1.md.
 * Sem seleção automática de controles, imputação, persistência ou efeito causal.
 */
'use strict';
const RaioxComparacao = (() => {
  const DIA = 86400000;
  const ESCOPO = ['org', 'fazenda', 'cultivo', 'safra', 'alvo'];
  const ESCOPO_MANEJO = ['org', 'fazenda', 'cultivo', 'safra'];
  const texto = x => typeof x === 'string' && x.trim().length > 0;
  const numero = x => typeof x === 'number' && Number.isFinite(x);
  function instante(x) {
    if (typeof x !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(x)) return NaN;
    const n = Date.parse(x);
    return Number.isFinite(n) && new Date(n).toISOString() === x ? n : NaN;
  }
  const chave = x => JSON.stringify([...ESCOPO.map(k => x[k]), x.talhao, x.id]);
  const chaveAplicacao = x => JSON.stringify([...ESCOPO_MANEJO.map(k => x[k]), x.talhao, x.id]);
  const fonte = x => Object.fromEntries([...ESCOPO, 'talhao', 'id', 'versao', 'evento', 'disponivelEm'].map(k => [k, x[k]]));
  const ordenar = (a, b) => instante(a.evento) - instante(b.evento) || chave(a).localeCompare(chave(b));
  const indisponivel = motivo => ({estado: 'indisponivel', motivo});
  function preparar(dados, contexto, parametros) {
    if (!contexto || !ESCOPO.every(k => texto(contexto[k])) || !Number.isFinite(instante(contexto.corte))) throw Error('Contexto ou corte inválido.');
    if (!Array.isArray(dados?.leituras) || !Array.isArray(dados?.aplicacoes)) throw Error('Fontes ausentes.');
    const corte = instante(contexto.corte);
    function vigentes(registros, manejos = false) {
      const campos = manejos ? ESCOPO_MANEJO : ESCOPO;
      const identidade = manejos ? chaveAplicacao : chave;
      const mapa = new Map(), instantesConhecidos = new Set(), versoesConhecidas = new Set();
      for (const x of registros) {
        if (!x || !campos.every(k => x[k] === contexto[k])) continue;
        const disp = instante(x.disponivelEm);
        if (!Number.isFinite(disp)) throw Error('Disponibilidade inválida no escopo.');
        // A própria existência de uma versão futura não aparece na saída.
        if (disp > corte) continue;
        if (!texto(x.id) || !texto(x.talhao) || !Number.isInteger(x.versao) || x.versao < 1) throw Error('Identidade de fonte inválida.');
        const k = identidade(x), atual = mapa.get(k);
        const kd = JSON.stringify([k, disp]), kv = JSON.stringify([k, x.versao]);
        if (instantesConhecidos.has(kd) || versoesConhecidas.has(kv)) throw Error('Versão ou instante de disponibilidade repetido na fonte.');
        instantesConhecidos.add(kd); versoesConhecidas.add(kv);
        if (!atual || disp > instante(atual.disponivelEm)) mapa.set(k, x);
      }
      // Revisão conhecida inválida ou cancelada substitui a antiga, sem fallback.
      return [...mapa.values()].sort((a, b) => identidade(a).localeCompare(identidade(b)));
    }
    const p = parametros;
    if (!p || !texto(p.id) || !Number.isInteger(p.versao) || p.versao < 1 || p.origem !== 'demonstrativo') throw Error('Este núcleo só aceita parâmetros demonstrativos identificados.');
    if (!Number.isFinite(instante(p.publicadoEm)) || instante(p.publicadoEm) > corte) throw Error('Parâmetros não publicados até o corte.');
    if (p.agregacao !== undefined && p.agregacao !== 'mediana_razoes_talhao_v1') throw Error('Método de agregação desconhecido.');
    if (!texto(p.protocolo) || !texto(p.unidade) || !numero(p.nc) || p.nc <= 0) throw Error('Protocolo, unidade ou NC inválido.');
    for (const k of ['antesMaxDias', 'depoisMinDias', 'depoisMaxDias', 'toleranciaDias', 'residualDias', 'pisoAntes', 'diferencaRelativaAntes']) {
      if (!numero(p[k]) || p[k] < 0) throw Error('Parâmetro inválido: ' + k);
    }
    if (p.depoisMaxDias < p.depoisMinDias || !Number.isInteger(p.minControles) || p.minControles < 1) throw Error('Janela ou mínimo de controles inválido.');
    // Defensivos de outros alvos também podem interferir. A identidade da aplicação
    // não inclui alvo: corrigir o alvo de uma versão não duplica o mesmo manejo.
    return {corte, p, leituras: vigentes(dados.leituras), aplicacoes: vigentes(dados.aplicacoes, true), contexto: {...contexto}};
  }
  function problemaTempo(x, corte) {
    if (!x) return 'fonte_nao_disponivel';
    if (!Number.isFinite(instante(x.evento)) || x.precisao !== 'instante') return 'instante_nao_demonstrado';
    if (instante(x.evento) > corte) return 'evento_apos_corte';
    if (instante(x.evento) > instante(x.disponivelEm)) return 'disponibilidade_anterior_ao_evento';
    return '';
  }
  function problemaLeitura(x, s) {
    return problemaTempo(x, s.corte) || (x.estado !== 'completa' ? 'leitura_incompleta' : '') ||
      (!numero(x.valor) || x.valor < 0 ? 'valor_ausente_ou_invalido' : '') ||
      (x.unidade !== s.p.unidade || x.protocolo !== s.p.protocolo ? 'protocolo_ou_unidade_incompativel' : '') ||
      (!texto(x.avaliador) ? 'avaliador_ausente' : '');
  }
  function buscar(xs, ref) { return ref && xs.find(x => x.id === ref.id && x.talhao === ref.talhao); }
  function interferencia(s, talhao, inicio, fim, exceto) {
    return s.aplicacoes.some(x => {
      if (x.talhao !== talhao || chaveAplicacao(x) === exceto || x.estado === 'cancelada') return false;
      const t = instante(x.evento);
      // Evento conhecido sem ordem ou confirmação suficiente não comprova ausência.
      // Sem instante demonstrado, não há prova de que o manejo ficou fora da
      // janela. Não interpretar a meia-noite de uma data como hora de aplicação.
      if (!Number.isFinite(t) || x.precisao !== 'instante') return true;
      return t >= inicio && t <= fim;
    });
  }
  function comparar(s, pedido, aplicacao) {
    const a = buscar(s.leituras, pedido.antes), b = buscar(s.leituras, pedido.depois);
    let motivo = problemaLeitura(a, s) || problemaLeitura(b, s);
    if (motivo) return indisponivel(motivo);
    if (a.talhao !== aplicacao.talhao || b.talhao !== aplicacao.talhao) return indisponivel('talhao_tratado_incompativel');
    const ta = instante(a.evento), tb = instante(b.evento), t = instante(aplicacao.evento), p = s.p;
    if (!(ta < t && tb > t)) return indisponivel('ordem_antes_aplicacao_depois_invalida');
    if ((t - ta) / DIA > p.antesMaxDias || (tb - t) / DIA < p.depoisMinDias || (tb - t) / DIA > p.depoisMaxDias) return indisponivel('leitura_fora_da_janela');
    if (a.valor === 0) return indisponivel('tratado_zerado_antes');
    if (a.valor < p.pisoAntes) return indisponivel('tratado_abaixo_do_piso');
    if (!texto(a.estadio)) return indisponivel('estadio_ausente');
    if (interferencia(s, a.talhao, ta - p.residualDias * DIA, tb, chaveAplicacao(aplicacao))) return indisponivel('interferencia_no_tratado');
    const candidatos = Array.isArray(pedido.controles) ? pedido.controles : [];
    const repetidos = new Map();
    for (const c of candidatos) repetidos.set(c?.talhao, (repetidos.get(c?.talhao) || 0) + 1);
    const controles = candidatos.map(c => {
      const ca = buscar(s.leituras, {id: c?.antes, talhao: c?.talhao}), cb = buscar(s.leituras, {id: c?.depois, talhao: c?.talhao});
      const out = {talhao: c?.talhao || '', estado: 'excluido'};
      let erro = c?.talhao === a.talhao ? 'mesmo_talhao_do_tratado' : repetidos.get(c?.talhao) > 1 ? 'talhao_repetido' : '';
      erro ||= problemaLeitura(ca, s) || problemaLeitura(cb, s);
      if (!erro) {
        const tca = instante(ca.evento), tcb = instante(cb.evento);
        if (!(tca < t && tcb > t)) erro = 'ordem_controle_invalida';
        else if (Math.abs(tca - ta) / DIA > p.toleranciaDias || Math.abs(tcb - tb) / DIA > p.toleranciaDias) erro = 'controle_fora_da_tolerancia';
        else if (ca.valor === 0) erro = 'controle_zerado_antes';
        else if (cb.valor === 0) erro = 'controle_zerado_depois';
        else if (ca.valor < p.pisoAntes) erro = 'controle_abaixo_do_piso';
        else if (ca.estadio !== a.estadio) erro = 'estadio_incompativel';
        else if (Math.abs(ca.valor - a.valor) / a.valor > p.diferencaRelativaAntes) erro = 'nivel_inicial_incompativel';
        else if (interferencia(s, c.talhao, tca - p.residualDias * DIA, tcb)) erro = 'interferencia_no_controle';
      }
      if (erro) return {...out, motivo: erro};
      const razao = cb.valor / ca.valor, variacao = 1 - (b.valor / a.valor) / razao;
      if (!Number.isFinite(razao) || !Number.isFinite(variacao)) return {...out, motivo: 'resultado_nao_finito'};
      return {...out, estado: 'elegivel', razao, variacao, fontes: [fonte(ca), fonte(cb)], mudouAvaliador: ca.avaliador !== cb.avaliador};
    }).sort((a, b) => a.talhao.localeCompare(b.talhao) || JSON.stringify(a).localeCompare(JSON.stringify(b)));
    const elegiveis = controles.filter(c => c.estado === 'elegivel');
    const resumo = {estado: elegiveis.length < p.minControles ? 'insuficiente' : 'agregacao_pendente',
      motivo: elegiveis.length < p.minControles ? 'controles_elegiveis_insuficientes' : 'metodo_de_agregacao_nao_adotado',
      fontes: [fonte(a), fonte(b)], mudouAvaliador: a.avaliador !== b.avaliador,
      zeroObservadoDepois: b.valor === 0, controles, quantidadeElegivel: elegiveis.length,
      variacao: null};
    if (elegiveis.length < p.minControles || p.agregacao === undefined) return resumo;
    const fatores = elegiveis.map(c => c.razao).sort((a, b) => a - b), meio = Math.floor(fatores.length / 2);
    const interpolada = fatores.length % 2 === 0;
    // Média dos dois centrais sem somar números que possam exceder o limite finito.
    const fator = interpolada ? fatores[meio - 1] + (fatores[meio] - fatores[meio - 1]) / 2 : fatores[meio];
    const variacao = 1 - (b.valor / a.valor) / fator;
    if (!Number.isFinite(variacao)) return {...resumo, estado: 'indisponivel', motivo: 'resultado_nao_finito'};
    const faixa = elegiveis.reduce((v, c) => ({minimo: Math.min(v.minimo, c.variacao), maximo: Math.max(v.maximo, c.variacao)}), {minimo: Infinity, maximo: -Infinity});
    return {...resumo, estado: 'disponivel', motivo: '', variacao, metodo: p.agregacao,
      rotulo: 'Contraste frente ao fator mediano dos controles', fatorTratado: b.valor / a.valor,
      fatorControles: fator, medianaInterpolada: interpolada, faixaEntreControles: faixa,
      avisoMetodo: 'Faixa entre contrastes individuais; não é intervalo de confiança. Não demonstra eficácia causal.'};
  }
  function seguir(s, aplicacao) {
    const t = instante(aplicacao.evento);
    const outras = s.aplicacoes.filter(x => x.talhao === aplicacao.talhao && chaveAplicacao(x) !== chaveAplicacao(aplicacao) && x.estado !== 'cancelada');
    if (outras.some(x => !Number.isFinite(instante(x.evento)) || (instante(x.evento) >= t && instante(x.evento) <= s.corte && (problemaTempo(x, s.corte) || x.estado !== 'confirmada' || instante(x.evento) === t)))) return indisponivel('ordem_ou_confirmacao_da_proxima_aplicacao_pendente');
    const proxima = outras.filter(x => instante(x.evento) > t && instante(x.evento) <= s.corte).sort(ordenar)[0];
    const fim = proxima ? instante(proxima.evento) : s.corte;
    const excluidas = [], validas = []; let incompatibilidade = false;
    for (const x of s.leituras.filter(x => x.talhao === aplicacao.talhao)) {
      const tx = instante(x.evento);
      if (!Number.isFinite(tx)) { excluidas.push({fonte: fonte(x), motivo: 'instante_nao_demonstrado'}); continue; }
      if (tx <= t || tx > fim) continue;
      // Instante igual ao manejo não estabelece a ordem de leitura/execução.
      let motivo = proxima && tx === fim ? 'leitura_no_instante_da_nova_aplicacao' : problemaLeitura(x, s);
      if (motivo === 'protocolo_ou_unidade_incompativel') incompatibilidade = true;
      if (motivo) excluidas.push({fonte: fonte(x), motivo}); else validas.push(x);
    }
    validas.sort(ordenar);
    if (validas.some((x, i) => i && x.evento === validas[i - 1].evento && x.valor !== validas[i - 1].valor)) return indisponivel('leituras_conflitantes_no_mesmo_instante');
    const base = {populacao: 'P-SEG', fontes: validas.map(fonte), excluidas, proximaAplicacao: proxima ? fonte(proxima) : null};
    if (incompatibilidade) return {...base, estado: 'S6', motivo: 'nc_incompativel'};
    if (!validas.length) return {...base, estado: proxima ? 'S5a' : 'S4'};
    if (validas[0].valor >= s.p.nc) return {...base, estado: 'S2', motivo: 'retorno_nao_demonstrado'};
    for (let i = 1; i < validas.length; i++) if (validas[i].valor >= s.p.nc) return {...base, estado: 'S1', intervalo: {depoisDe: validas[i - 1].evento, ate: validas[i].evento, larguraDias: (instante(validas[i].evento) - instante(validas[i - 1].evento)) / DIA}};
    return {...base, estado: proxima ? 'S5b' : 'S3', observadoAte: validas.at(-1).evento};
  }
  function analisar(dados, contexto, parametros, pedido) {
    try {
      const s = preparar(dados, contexto, parametros);
      const a = buscar(s.aplicacoes, pedido?.aplicacao);
      const erro = problemaTempo(a, s.corte) || (a.estado !== 'confirmada' ? 'aplicacao_nao_confirmada' : '');
      if (erro) return indisponivel(erro);
      if (a.alvo !== contexto.alvo) return indisponivel('aplicacao_alvo_incompativel');
      return {estado: 'demonstrativo', contrato: 'RX-1.0', contexto: s.contexto,
        parametros: {...parametros}, aplicacao: fonte(a),
        comparacao: comparar(s, pedido, a), seguimento: seguir(s, a),
        aviso: 'Comparação observacional; não demonstra eficácia causal nem recomenda produto ou dose.'};
    } catch (e) { return {...indisponivel('contrato_invalido'), detalhe: e.message}; }
  }
  return Object.freeze({analisar});
})();
if (typeof module !== 'undefined' && module.exports) module.exports = RaioxComparacao;
