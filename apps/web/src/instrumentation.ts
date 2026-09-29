/**
 * Subida do servidor. No Next 16, register roda uma vez por instância e termina antes de o servidor atender
 * (https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation; com src/, o arquivo fica em src/).
 * Com SAFRION_CLOUDSQL_INSTANCIA, a conexão por IP privado fica pronta aqui; sem ela, nada acontece.
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { prepararDependencias } = await import('./servidor/ambiente');
    await prepararDependencias();
  }
}
