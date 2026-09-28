/** Fuso civil da operação na F0 (Brasil, horário de Brasília). A organização terá o seu fuso quando houver mais de um. */
export const FUSO_OPERACAO = 'America/Sao_Paulo';

/** Data civil AAAA-MM-DD do instante no fuso: é o "hoje" do saldo e da validade. */
export function dataCivil(instante: Date, fuso: string = FUSO_OPERACAO): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: fuso,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(instante);
}

const DATA = /^(\d{4})-(\d{2})-(\d{2})$/;

/** AAAA-MM-DD para dd/mm/aaaa, sem passar por Date (que mudaria o dia pelo fuso). */
export function formatarData(civil: string): string {
  if (!DATA.test(civil)) throw new Error('Data civil fora do formato AAAA-MM-DD.');
  return `${civil.slice(8, 10)}/${civil.slice(5, 7)}/${civil.slice(0, 4)}`;
}

/** dd/mm/aaaa digitado para AAAA-MM-DD; null se não for uma data do calendário. */
export function dataDoCampo(texto: string): string | null {
  const t = texto.trim();
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(t)) return null;
  const civil = `${t.slice(6, 10)}-${t.slice(3, 5)}-${t.slice(0, 2)}`;
  const d = new Date(`${civil}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().startsWith(civil) ? civil : null;
}

/** Instante ISO para "dd/mm/aaaa hh:mm" no fuso da operação. */
export function formatarInstante(iso: string, fuso: string = FUSO_OPERACAO): string {
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: fuso,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  })
    .format(new Date(iso))
    .replace(', ', ' ');
}
