import type { Conector, CriarConector } from './conexao.js';

// Nome em constante: o TypeScript não segue um import dinâmico que não é literal, e o contrato usado é só o Conector de
// conexao.ts, que confere em tempo de execução o formato das opções. O Turbopack resolve a constante e leva o pacote ao
// bundle da web. Versão fixa no package.json e no lockfile, dentro da quarentena de 7 dias (1.12.0 é de 02/09/2026).
// Carregado só quando há SAFRION_CLOUDSQL_INSTANCIA (conexao.ts).
const PACOTE = '@google-cloud/cloud-sql-connector';

/** Conector oficial do Cloud SQL, carregado sob demanda; conexao.ts confere o formato das opções que ele devolve. */
export const criarConectorGoogle: CriarConector = async () => {
  const m = (await import(PACOTE)) as { Connector: new () => Conector };
  return new m.Connector();
};
