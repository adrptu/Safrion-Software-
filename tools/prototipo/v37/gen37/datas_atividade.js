/* EX57 F0a — extração, não correção de domínio.
 * Interface: daDataAtividade(atividade, cultivo, {variante, plano}).
 * Cultivo normalizado: {plantio, colheita}, datas ISO civis; dias inteiros.
 * Variantes obrigatórias identificam a cópia original, não uma regra preferida.
 * safra mantém aritmética local ao meio-dia; as demais usam dias civis UTC.
 * Sem DOM, estado global de aplicação, recorte de safra ou geração de O.S.
 * DAPA do editor chega como DAP negativo. Entradas inválidas não são normalizadas.
 */
'use strict';
const DA_VARIANTES = Object.freeze(['safra', 'solo', 'ocupacao_js', 'ocupacao_py', 'dados2', 'inicio']);
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
  if (g.tipo === 'DAP') return resultado(mais(cultivo.plantio, g.dias), 'plantio');
  if (g.tipo === 'DATA' && (variante !== 'inicio' || g.data)) return resultado(g.data, 'data_fixa');
  if (variante === 'inicio' && (!['DAPC', 'DANC'].includes(g.tipo) || !cultivo.colheita))
    return resultado(null, 'sem_ancora');
  let colheita = cultivo.colheita;
  let origem = 'colheita_informada';
  if (!colheita) {
    const ca = (contexto.plano.atividades || []).find(a => String(a.op).startsWith('Colheita'));
    if (ca && ca.g.tipo === 'DAP') {
      colheita = mais(cultivo.plantio, ca.g.dias);
      origem = 'colheita_plano_dap';
    } else if (ca && ca.g.tipo === 'DATA' && variante !== 'dados2') {
      colheita = ca.g.data;
      origem = 'colheita_plano_data';
    } else {
      colheita = cultivo.plantio;
      origem = 'fallback_plantio_legado';
    }
  }
  return resultado(mais(colheita, g.tipo === 'DAPC' ? g.dias : -g.dias), origem);
}
if (typeof module !== 'undefined' && module.exports) module.exports = {daDataAtividade, DA_VARIANTES};
