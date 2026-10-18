/* EX57 F0a/F0b — variantes legadas preservadas; canonica opt-in.
 * Interface: daDataAtividade(atividade, cultivo, {variante, plano}).
 * Cultivo normalizado: {plantio, colheita}, datas ISO civis; dias inteiros.
 * Variantes obrigatórias identificam a cópia original, não uma regra preferida.
 * canonica usa dia civil e ausência explícita, sem fallback no plantio.
 * A primeira Colheita do plano continua sendo a âncora; não reordena eventos.
 * safra mantém aritmética local ao meio-dia; as demais usam dias civis UTC.
 * Sem DOM, estado global de aplicação, recorte de safra ou geração de O.S.
 * DAPA do editor chega como DAP negativo. Entradas inválidas não são normalizadas.
 */
'use strict';
const DA_VARIANTES = Object.freeze(['safra', 'solo', 'ocupacao_js', 'ocupacao_py', 'dados2', 'inicio', 'canonica']);
function daDataAtividade(atividade, cultivo, contexto) {
  const variante = contexto.variante;
  if (!DA_VARIANTES.includes(variante)) throw new Error('Variante de data desconhecida: ' + variante);
  const g = atividade.g || {};
  const resultado = (data, origem) => ({data, origem, variante});
  const mais = (data, dias) => {
    const local = variante === 'safra';
    const d = new Date(String(data).slice(0, 10) + (local ? 'T12:00:00' : 'T12:00:00Z'));
    if (local) d.setDate(d.getDate() + dias);
    else d.setUTCDate(d.getUTCDate() + dias);
    return d.toISOString().slice(0, 10);
  };
  if (variante === 'canonica') {
    if (g.tipo === 'DATA') return resultado(g.data || null, g.data ? 'data_fixa' : 'data_ausente');
    if (!['DAP', 'DAPC', 'DANC'].includes(g.tipo)) return resultado(null, 'gatilho_desconhecido');
    if (g.tipo === 'DAP' && !cultivo.plantio) return resultado(null, 'ancora_ausente');
  }
  if (g.tipo === 'DAP') return resultado(mais(cultivo.plantio, g.dias), 'plantio');
  if (g.tipo === 'DATA' && (variante !== 'inicio' || g.data)) return resultado(g.data, 'data_fixa');
  if (variante === 'inicio' && (!['DAPC', 'DANC'].includes(g.tipo) || !cultivo.colheita))
    return resultado(null, 'sem_ancora');
  let colheita = cultivo.colheita;
  let origem = 'colheita_informada';
  if (!colheita) {
    const ca = ((contexto.plano || {}).atividades || []).find(a => String(a.op).startsWith('Colheita'));
    if (ca && ca.g.tipo === 'DAP' && (variante !== 'canonica' || cultivo.plantio)) {
      colheita = mais(cultivo.plantio, ca.g.dias);
      origem = 'colheita_plano_dap';
    } else if (ca && ca.g.tipo === 'DATA' && variante !== 'dados2' && (variante !== 'canonica' || ca.g.data)) {
      colheita = ca.g.data;
      origem = 'colheita_plano_data';
    } else {
      if (variante === 'canonica') return resultado(null, 'ancora_ausente');
      colheita = cultivo.plantio;
      origem = 'fallback_plantio_legado';
    }
  }
  return resultado(mais(colheita, g.tipo === 'DAPC' ? g.dias : -g.dias), origem);
}
if (typeof module !== 'undefined' && module.exports) module.exports = {daDataAtividade, DA_VARIANTES};
