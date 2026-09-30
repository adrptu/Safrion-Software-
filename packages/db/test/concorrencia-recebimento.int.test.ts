import { randomUUID } from 'node:crypto';

import { canonizarRecebimento, type DadosRecebimento } from '@safrion/contracts';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando, type Recibo } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { COMANDO_RECEBER_DOCUMENTO, receberDocumento } from '../src/recebimento.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Concorrência do recebimento (contrato CMD-15 v3.3, §3 e §6; AC-84) em PostgreSQL real: a mesma chave cria um
// documento; chaves diferentes na mesma origem dão um confirmado e as demais DOCUMENTO_JA_RECEBIDO; lotes novos em
// ordens opostas não travam. Nenhuma resposta vira erro 500.
let amb: Ambiente;
let a: Semente;
const fornecedor = randomUUID();

beforeAll(async () => {
  amb = await criarBanco({ maxApp: 12 });
  a = await semear(amb.app, 'C');
  await emOrganizacao(amb.app, a.org, (c) =>
    c.query(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'Fornecedor', '99')",
      [fornecedor, a.org],
    ),
  );
});
afterAll(async () => {
  await amb.encerrar();
});

const linha = (numero: number, codigo: string): DadosRecebimento['linhas'][number] => ({
  numero,
  produto: a.produto,
  lote: { codigo },
  validade: '2027-06-30',
  local: a.local,
  unidade: { tipo: 'medida', unidade: 'L' },
  documento: '1',
  parcelas: { apto: '1', quarentena: '0', bloqueado: '0', recusado: '0' },
});
const documento = (numero: string, lotes: string[]): DadosRecebimento => ({
  emitente: fornecedor,
  tipo: 'nfe',
  serie: '1',
  numero,
  emissao: '2026-09-29',
  recebimento: '2026-09-30',
  fazenda: a.fazenda,
  linhas: lotes.map((l, i) => linha(i + 1, l)),
});

async function receber(chave: string, docId: string, dados: DadosRecebimento): Promise<Recibo | ErroComando> {
  const canonico = canonizarRecebimento(dados);
  try {
    return await executarComando(
      amb.app,
      a.org,
      {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: chave,
        initiatorKind: 'web',
        actorId: a.usuario,
        target: { type: 'receipt_document', id: docId, expectedVersion: 0 },
        data: canonico,
        correlationId: `corr-${chave}`,
      },
      receberDocumento(canonico),
      { esperaChaveMs: 20_000 },
    );
  } catch (erro) {
    // Só erro previsto do envelope é aceitável aqui; qualquer outro (o que viraria 500) derruba o teste.
    if (erro instanceof ErroComando && erro.codigo === 'IDEMPOTENCY_IN_PROGRESS') return erro;
    throw erro;
  }
}

const documentosDaOrigem = (numero: string) =>
  emOrganizacao(amb.app, a.org, async (c) =>
    Number(
      (
        await c.query<{ n: string }>('SELECT count(*)::text n FROM app.receipt_document WHERE number = $1', [
          numero,
        ])
      ).rows[0]?.n,
    ),
  );

describe('recebimento concorrente', () => {
  it('10 envios simultâneos com a mesma chave criam um documento e devolvem o mesmo recibo (AC-84)', async () => {
    const doc = randomUUID();
    const r = await Promise.all(
      Array.from({ length: 10 }, () => receber('mesma-chave', doc, documento('3001', ['C-1']))),
    );
    const recibos = r.filter((x): x is Recibo => !(x instanceof ErroComando));
    expect(recibos.length).toBeGreaterThan(0);
    expect(new Set(recibos.map((x) => x.receiptId)).size).toBe(1);
    expect(recibos.filter((x) => !x.alreadyReceived)).toHaveLength(1);
    expect(recibos.every((x) => x.outcome === 'confirmed')).toBe(true);
    expect(await documentosDaOrigem('3001')).toBe(1);
  });

  it('10 chaves diferentes na mesma origem: 1 confirmado e 9 DOCUMENTO_JA_RECEBIDO', async () => {
    const r = await Promise.all(
      Array.from({ length: 10 }, (_, i) =>
        receber(`origem-${String(i)}`, randomUUID(), documento('3002', ['C-2'])),
      ),
    );
    const recibos = r.filter((x): x is Recibo => !(x instanceof ErroComando));
    expect(recibos).toHaveLength(10);
    expect(recibos.filter((x) => x.outcome === 'confirmed')).toHaveLength(1);
    expect(recibos.filter((x) => x.reasonCode === 'DOCUMENTO_JA_RECEBIDO')).toHaveLength(9);
    expect(await documentosDaOrigem('3002')).toBe(1);
  });

  it('documentos com lotes novos em ordens opostas terminam sem deadlock, em várias rodadas', async () => {
    for (let rodada = 0; rodada < 5; rodada++) {
      const [x, y] = [`X-${String(rodada)}`, `Y-${String(rodada)}`];
      const [ra, rb] = await Promise.all([
        receber(`ab-${String(rodada)}`, randomUUID(), documento(`40${String(rodada)}A`, [x, y])),
        receber(`ba-${String(rodada)}`, randomUUID(), documento(`40${String(rodada)}B`, [y, x])),
      ]);
      expect(ra).toMatchObject({ outcome: 'confirmed' });
      expect(rb).toMatchObject({ outcome: 'confirmed' });
      const versoes = await emOrganizacao(amb.app, a.org, (c) =>
        c.query<{ code: string; version: string }>(
          'SELECT code, version::text FROM app.lot WHERE code = ANY($1) ORDER BY code',
          [[x, y]],
        ),
      );
      expect(versoes.rows).toEqual([
        { code: x, version: '2' },
        { code: y, version: '2' },
      ]);
    }
  });
});
