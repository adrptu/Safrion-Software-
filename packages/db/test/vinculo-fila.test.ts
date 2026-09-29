// Fila de vínculo em HML (R-006, GCP-0017, §3c) sem banco: validação do pedido, conteudo_hash e o laço da fila com um
// cliente e um segredo simulados (ordem, destino da versão, saídas e falhas). O banco real está em
// vinculo-fila.int.test.ts.
import { createHash } from 'node:crypto';
import { EventEmitter } from 'node:events';

import type { ClientBase } from 'pg';
import { describe, expect, it } from 'vitest';

import { hashCanonico } from '../src/canonico.js';
import type { SegredoPedido, VersaoAtiva } from '../src/segredo-pedido.js';
import {
  conteudoHash,
  PEDIDO_INVALIDO,
  processarFila,
  validarPedido,
  type Pedido,
} from '../src/vinculo-fila.js';

const ORG = '22222222-2222-4222-8222-222222222222';
const USUARIO = '33333333-3333-4333-8333-333333333333';
const conceder = {
  pedido_id: '00000000-0000-4000-8000-000000000001',
  acao: 'conceder',
  organizacao: ORG,
  usuario: USUARIO,
  responsavel: 'Operador sintético',
  motivo: 'Teste de contrato da fila',
  codigo: '0123456789',
};
const semCodigo = {
  pedido_id: conceder.pedido_id,
  acao: 'conceder',
  organizacao: ORG,
  usuario: USUARIO,
  responsavel: conceder.responsavel,
  motivo: conceder.motivo,
};
const revogar = { ...semCodigo, pedido_id: '00000000-0000-4000-8000-000000000002', acao: 'revogar' };
const texto = (o: unknown) => JSON.stringify(o);
const sha256 = (t: string) => createHash('sha256').update(t).digest('hex');

describe('validarPedido', () => {
  it('conceder e revogar no formato do contrato, em texto ou em bytes; o código é normalizado', () => {
    expect(validarPedido(texto({ ...conceder, codigo: 'o1234-56789' }))).toEqual(conceder);
    expect(validarPedido(Buffer.from(texto(revogar)))).toEqual(revogar);
    expect(validarPedido(new TextEncoder().encode(texto(conceder)))).toEqual(conceder);
  });

  it('qualquer outra forma é PEDIDO_INVALIDO', () => {
    const casos: [string, string | Uint8Array][] = [
      ['JSON quebrado', '{"pedido_id":'],
      ['não é objeto', '[1]'],
      ['nulo', 'null'],
      ['número', '5'],
      ['chave desconhecida', texto({ ...conceder, extra: 'x' })],
      ['chave faltante', texto(semCodigo)],
      ['chave trocada', texto({ ...revogar, usuario: undefined, outro: USUARIO })],
      ['codigo em revogar', texto({ ...revogar, codigo: '0123456789' })],
      ['acao fora das duas', texto({ ...conceder, acao: 'apagar' })],
      ['acao ausente', texto({ ...revogar, acao: undefined })],
      ['tipo errado', texto({ ...revogar, motivo: 5 })],
      ['pedido_id inválido', texto({ ...conceder, pedido_id: 'invalid-uuid-format' })],
      ['pedido_id em maiúsculas', texto({ ...conceder, pedido_id: 'ABCDEF00-0000-4000-8000-000000000001' })],
      ['organização inválida', texto({ ...revogar, organizacao: 'x' })],
      ['responsável com controle', texto({ ...revogar, responsavel: 'a\nb' })],
      ['motivo vazio', texto({ ...revogar, motivo: '  ' })],
      ['código fora do formato', texto({ ...conceder, codigo: 'ABCDEFGHJU' })],
      ['UTF-8 inválido', Buffer.from([0x7b, 0xff, 0x7d])],
      ['texto acima de 4 KiB', texto({ ...revogar, motivo: 'é'.repeat(2100) })],
      ['bytes acima de 4 KiB', Buffer.alloc(4097, 0x20)],
      // Chaves com vírgula não se passam pelas do contrato.
      [
        'chave com vírgula',
        texto({ acao: 'revogar', 'motivo,organizacao': 'x', pedido_id: '', responsavel: '', usuario: '' }),
      ],
    ];
    for (const [nome, conteudo] of casos) expect(validarPedido(conteudo), nome).toBe(PEDIDO_INVALIDO);
  });

  it('chave repetida é PEDIDO_INVALIDO, mesmo com o último valor válido (revisão: o JSON.parse ficava com ele)', () => {
    const outro = '44444444-4444-4444-8444-444444444444';
    // O texto de revogar, sem o "}" final, recebe as chaves a mais.
    const base = texto(revogar).slice(0, -1);
    const casos: [string, string][] = [
      ['acao', `${base},"acao":"conceder","codigo":"0123456789"}`],
      ['usuario', `${base},"usuario":"${outro}"}`],
      ['pedido_id', `${base},"pedido_id":"00000000-0000-4000-8000-000000000009"}`],
      ['valor não texto antes', `{"usuario":5,${base.slice(1)}}`],
    ];
    for (const [nome, conteudo] of casos) {
      expect(JSON.parse(conteudo), nome).toBeTypeOf('object');
      expect(validarPedido(conteudo), nome).toBe(PEDIDO_INVALIDO);
    }
    // O printf do OPERACAO.md com aspas no motivo: antes, um pedido aceito para outro usuário.
    const motivo = `x","usuario":"${outro}`;
    const printf = `{"pedido_id":"${conceder.pedido_id}","acao":"conceder","organizacao":"${ORG}","usuario":"${USUARIO}","responsavel":"r","motivo":"${motivo}","codigo":"0123456789"}`;
    expect(JSON.parse(printf)).toMatchObject({ usuario: outro, motivo: 'x' });
    expect(validarPedido(printf)).toBe(PEDIDO_INVALIDO);
    // Aspas e barra invertida escapadas dentro de um valor continuam valendo: só a chave escrita conta.
    expect(validarPedido(texto({ ...revogar, motivo: 'a "b" \\ ":"' }))).toMatchObject({
      motivo: 'a "b" \\ ":"',
    });
  });

  it('4 KiB exatos ainda vale; um byte a mais, não', () => {
    // Espaço em volta do responsável não conta nos 120 da validação (como no banco, que apara).
    const com = (n: number) => texto({ ...revogar, responsavel: `${' '.repeat(n)}r` });
    const base = Buffer.byteLength(com(0));
    expect(Buffer.byteLength(com(4096 - base))).toBe(4096);
    expect(validarPedido(com(4096 - base))).toMatchObject({ acao: 'revogar' });
    expect(validarPedido(Buffer.from(com(4096 - base)))).toMatchObject({ acao: 'revogar' });
    expect(validarPedido(com(4097 - base))).toBe(PEDIDO_INVALIDO);
  });
});

describe('conteudoHash', () => {
  it('hashCanonico dos campos fixos, com o SHA-256 do código normalizado e null explícito em revogar', () => {
    const p = validarPedido(texto(conceder)) as Pedido;
    expect(conteudoHash(p)).toBe(
      hashCanonico({
        formato: 'VINCULO-PEDIDO-1',
        pedido_id: conceder.pedido_id,
        acao: 'conceder',
        organizacao: ORG,
        usuario: USUARIO,
        responsavel: conceder.responsavel,
        motivo: conceder.motivo,
        codigo_hash: sha256('0123456789'),
      }),
    );
    const r = validarPedido(texto(revogar)) as Pedido;
    expect(conteudoHash(r)).toBe(
      hashCanonico({
        ...semCodigo,
        pedido_id: revogar.pedido_id,
        acao: 'revogar',
        formato: 'VINCULO-PEDIDO-1',
        codigo_hash: null,
      }),
    );
    // O código digitado de outro jeito é o mesmo pedido; UUID em maiúsculas vindo de fora também.
    expect(conteudoHash(validarPedido(texto({ ...conceder, codigo: '01234 56789' })) as Pedido)).toBe(
      conteudoHash(p),
    );
    expect(conteudoHash({ ...p, organizacao: ORG.toUpperCase() })).toBe(conteudoHash(p));
    expect(conteudoHash({ ...p, motivo: `${p.motivo} ` })).not.toBe(conteudoHash(p));
  });
});

// Cliente simulado: responde pela primeira regra que casa com o texto; registra tudo.
type Regra = (texto: string, valores?: unknown[]) => { rows: unknown[] } | Error | undefined;

class ClienteSimulado extends EventEmitter {
  readonly consultas: string[] = [];
  constructor(private readonly regras: Regra[] = []) {
    super();
  }
  query(texto: string, valores?: unknown[]): Promise<{ rows: unknown[] }> {
    this.consultas.push(texto);
    for (const regra of this.regras) {
      const r = regra(texto, valores);
      if (r instanceof Error) return Promise.reject(r);
      if (r) return Promise.resolve(r);
    }
    if (texto.includes('pg_try_advisory_lock')) return Promise.resolve({ rows: [{ livre: true }] });
    if (texto.includes('processar_pedido_vinculo')) {
      return Promise.resolve({ rows: [{ resultado: 'concedido', revogados: null, repetido: false }] });
    }
    return Promise.resolve({ rows: [] });
  }
}

interface VersaoSimulada {
  estado: string;
  etag: string;
  readonly createTime: string;
  readonly dados: string;
}

/** Segredo simulado em memória; `antes` intercepta cada chamada (pode lançar). */
class SegredoSimulado implements SegredoPedido {
  readonly chamadas: string[] = [];
  antes: (operacao: string, versao?: string) => void = () => undefined;
  constructor(readonly versoes: Map<string, VersaoSimulada>) {}
  listarAtivas(): Promise<VersaoAtiva[]> {
    this.chamadas.push('listar');
    this.antes('listar');
    return Promise.resolve(
      [...this.versoes]
        .filter(([, v]) => v.estado === 'ENABLED')
        .map(([versao, v]) => ({ versao, createTime: v.createTime })),
    );
  }
  private versao(operacao: string, versao: string): VersaoSimulada {
    this.chamadas.push(`${operacao}:${versao}`);
    this.antes(operacao, versao);
    const v = this.versoes.get(versao);
    if (!v) throw new Error('versão inexistente');
    return v;
  }
  obter(versao: string) {
    const v = this.versao('obter', versao);
    return Promise.resolve({ estado: v.estado, etag: v.etag });
  }
  acessar(versao: string) {
    return Promise.resolve(Buffer.from(this.versao('acessar', versao).dados));
  }
  desativar(versao: string, etag: string) {
    const v = this.versao('desativar', versao);
    if (v.etag !== etag)
      return Promise.reject(Object.assign(new Error('etag'), { codigo: 'SEGREDO_HTTP_409' }));
    v.estado = 'DISABLED';
    return Promise.resolve();
  }
  destruir(versao: string, etag: string) {
    const v = this.versao('destruir', versao);
    if (v.etag !== etag)
      return Promise.reject(Object.assign(new Error('etag'), { codigo: 'SEGREDO_HTTP_409' }));
    v.estado = 'DESTROYED';
    return Promise.resolve();
  }
}

const versao = (createTime: string, dados: unknown, etag = `e-${createTime}`): VersaoSimulada => ({
  estado: 'ENABLED',
  etag,
  createTime,
  dados: typeof dados === 'string' ? dados : texto(dados),
});

async function rodar(cliente: ClienteSimulado, segredo: SegredoSimulado) {
  const linhas: string[] = [];
  const saida = await processarFila({
    cliente: cliente as unknown as ClientBase,
    segredo,
    registrar: (l) => linhas.push(l),
  });
  return { saida, linhas: linhas.map((l) => JSON.parse(l) as Record<string, unknown>) };
}

const pedidoComId = (id: string, base: object = revogar) => ({ ...base, pedido_id: id });
const id = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`;

describe('processarFila', () => {
  it('trava ocupada: OCUPADO e saída 1, sem ler o segredo', async () => {
    const cliente = new ClienteSimulado([
      (t) => (t.includes('pg_try_advisory_lock') ? { rows: [{ livre: false }] } : undefined),
    ]);
    const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', conceder)]]));
    expect(await rodar(cliente, segredo)).toEqual({ saida: 1, linhas: [{ resultado: 'OCUPADO' }] });
    expect(segredo.chamadas).toEqual([]);
    expect(cliente.consultas.some((c) => c.includes('pg_advisory_unlock'))).toBe(false);
    expect(cliente.listenerCount('end') + cliente.listenerCount('error')).toBe(0);
  });

  it('ordem por createTime (fração completada) e número da versão, não pela ordem da API; uma transação por pedido', async () => {
    const segredo = new SegredoSimulado(
      new Map([
        ['9', versao('2026-09-28T21:50:00.5Z', pedidoComId(id(4)))],
        ['10', versao('2026-09-28T21:50:00Z', pedidoComId(id(3)))],
        ['2', versao('2026-09-28T21:50:00.000000001Z', pedidoComId(id(5)))],
        ['12', versao('2026-09-28T21:49:59.999999999Z', pedidoComId(id(1)))],
        ['11', versao('2026-09-28T21:50:00Z', pedidoComId(id(2)))],
        ['3', versao('2026-09-28T21:50:00Z', pedidoComId(id(0)))],
        ['5', versao('2026-09-28T21:50:00Z', pedidoComId(id(7)))],
        ['4', versao('2026-09-28T21:50:00Z', pedidoComId(id(6)))],
      ]),
    );
    const valores: unknown[][] = [];
    const cliente = new ClienteSimulado([
      (t, v) => {
        if (t.includes('processar_pedido_vinculo')) valores.push(v ?? []);
        return undefined;
      },
    ]);
    const { saida, linhas } = await rodar(cliente, segredo);
    expect(saida).toBe(0);
    expect(linhas.map((l) => l['versao'])).toEqual(['12', '3', '4', '5', '10', '11', '2', '9']);
    expect(linhas[0]).toEqual({ pedido_id: id(1), versao: '12', resultado: 'concedido', repetido: false });
    expect(valores[0]?.[2]).toBe('12');
    expect(valores[0]?.[9]).toBe('2026-09-28T21:49:59.999999999Z');
    expect(valores[0]?.[4]).toBeNull();
    const transacoes = cliente.consultas.filter((c) => !c.includes('advisory'));
    expect(transacoes.slice(0, 5)).toEqual([
      'BEGIN',
      "SET LOCAL lock_timeout = '5s'",
      "SET LOCAL statement_timeout = '30s'",
      'SELECT resultado, repetido FROM app.processar_pedido_vinculo($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
      'COMMIT',
    ]);
    expect(transacoes).toHaveLength(40);
    expect(cliente.consultas.at(-1)).toContain('pg_advisory_unlock');
    expect([...segredo.versoes.values()].every((v) => v.estado === 'DESTROYED')).toBe(true);
  });

  it('conceder manda o SHA-256 do código normalizado e o conteudo_hash em bytes', async () => {
    const valores: unknown[][] = [];
    const cliente = new ClienteSimulado([
      (t, v) => {
        if (t.includes('processar_pedido_vinculo')) valores.push(v ?? []);
        return undefined;
      },
    ]);
    const segredo = new SegredoSimulado(
      new Map([['1', versao('2026-09-28T21:50:00Z', { ...conceder, codigo: 'o123456789' })]]),
    );
    expect((await rodar(cliente, segredo)).saida).toBe(0);
    const [v] = valores;
    expect((v?.[4] as Buffer).toString('hex')).toBe(sha256('0123456789'));
    expect((v?.[1] as Buffer).toString('hex')).toBe(conteudoHash(conceder as Pedido));
    expect(v?.[3]).toBe('conceder');
  });

  it('inativa, inválida, reutilizada e recusas: destino de cada versão, logs exatos e saída 1', async () => {
    const resultados: Record<string, [string, boolean]> = {
      [id(2)]: ['PEDIDO_ID_REUTILIZADO', false],
      [id(3)]: ['USUARIO_INVALIDO', true],
      [id(4)]: ['mantido', false],
    };
    const cliente = new ClienteSimulado([
      (t, v) => {
        if (!t.includes('processar_pedido_vinculo')) return undefined;
        const [resultado, repetido] = resultados[String(v?.[0])] ?? ['revogado', false];
        return { rows: [{ resultado, revogados: 0, repetido }] };
      },
    ]);
    const inativa = versao('2026-09-28T21:50:00Z', pedidoComId(id(1)));
    const segredo = new SegredoSimulado(
      new Map([
        ['1', inativa],
        ['2', versao('2026-09-28T21:51:00Z', { ...revogar, extra: 'x' })],
        ['3', versao('2026-09-28T21:52:00Z', pedidoComId(id(2)))],
        ['4', versao('2026-09-28T21:53:00Z', pedidoComId(id(3)))],
        ['5', versao('2026-09-28T21:54:00Z', pedidoComId(id(4)))],
      ]),
    );
    // Desativada entre a listagem e a leitura: fica de fora.
    segredo.antes = (op, v) => {
      if (op === 'obter' && v === '1') inativa.estado = 'DISABLED';
    };
    const { saida, linhas } = await rodar(cliente, segredo);
    expect(saida).toBe(1);
    expect(linhas).toEqual([
      { versao: '1', resultado: 'VERSAO_INATIVA' },
      { versao: '2', resultado: 'PEDIDO_INVALIDO' },
      { pedido_id: id(2), versao: '3', resultado: 'PEDIDO_ID_REUTILIZADO', repetido: false },
      { pedido_id: id(3), versao: '4', resultado: 'USUARIO_INVALIDO', repetido: true },
      { pedido_id: id(4), versao: '5', resultado: 'mantido', repetido: false },
    ]);
    expect(segredo.chamadas).not.toContain('acessar:1');
    expect(Object.fromEntries([...segredo.versoes].map(([k, v]) => [k, v.estado]))).toEqual({
      '1': 'DISABLED',
      '2': 'DISABLED',
      '3': 'DISABLED',
      '4': 'DESTROYED',
      '5': 'DESTROYED',
    });
    const tudo = JSON.stringify(linhas);
    expect(tudo).not.toContain('extra');
    expect(tudo).not.toContain(revogar.motivo);
  });

  it('fila vazia: saída 0 sem linhas', async () => {
    expect(await rodar(new ClienteSimulado(), new SegredoSimulado(new Map()))).toEqual({
      saida: 0,
      linhas: [],
    });
  });

  it('falha no banco antes do COMMIT: ROLLBACK, saída 3 só com códigos e a versão fica', async () => {
    const falha = Object.assign(new Error(`timeout em postgresql://u:senha@host/db ${conceder.codigo}`), {
      code: '57014',
    });
    const cliente = new ClienteSimulado([
      (t) => (t.includes('processar_pedido_vinculo') ? falha : undefined),
    ]);
    const segredo = new SegredoSimulado(
      new Map([
        ['1', versao('2026-09-28T21:50:00Z', conceder)],
        ['2', versao('2026-09-28T21:51:00Z', revogar)],
      ]),
    );
    const { saida, linhas } = await rodar(cliente, segredo);
    expect(saida).toBe(3);
    expect(linhas).toEqual([
      { resultado: 'falha', codigo: 'FALHA_INFRAESTRUTURA', erro_tipo: 'Error', codigo_tecnico: '57014' },
    ]);
    expect(cliente.consultas).toContain('ROLLBACK');
    expect(cliente.consultas).not.toContain('COMMIT');
    // A trava fica com a conexão, que o comando encerra.
    expect(cliente.consultas.some((c) => c.includes('pg_advisory_unlock'))).toBe(false);
    expect(segredo.chamadas).not.toContain('obter:2');
    expect(segredo.versoes.get('1')?.estado).toBe('ENABLED');
  });

  it('resultado desconhecido (AMBIENTE_PROIBIDO inclusive) ou linha fora do formato: ROLLBACK e saída 3', async () => {
    for (const linha of [
      { resultado: 'AMBIENTE_PROIBIDO', repetido: false },
      { resultado: 'concedido', repetido: 'nao' },
      undefined,
    ]) {
      const cliente = new ClienteSimulado([
        (t) => (t.includes('processar_pedido_vinculo') ? { rows: linha ? [linha] : [] } : undefined),
        // ROLLBACK que também falha não troca a causa.
        (t) => (t === 'ROLLBACK' ? new Error('conexão caiu') : undefined),
      ]);
      const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', conceder)]]));
      const { saida, linhas } = await rodar(cliente, segredo);
      expect(saida).toBe(3);
      expect(linhas.at(-1)).toMatchObject({ erro_tipo: 'ErroFila', codigo_tecnico: 'RESULTADO_INESPERADO' });
      expect(segredo.versoes.get('1')?.estado).toBe('ENABLED');
    }
  });

  it('COMMIT sem resposta: sem ROLLBACK, saída 3 e a versão fica para a próxima execução repetir', async () => {
    const cliente = new ClienteSimulado([
      (t) => (t === 'COMMIT' ? new Error('Connection terminated') : undefined),
    ]);
    const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', conceder)]]));
    const { saida } = await rodar(cliente, segredo);
    expect(saida).toBe(3);
    expect(cliente.consultas).not.toContain('ROLLBACK');
    expect(segredo.chamadas).not.toContain('destruir:1');
  });

  it('etag recusado ao destruir: saída 3 e o pedido seguinte não é lido', async () => {
    const segredo = new SegredoSimulado(
      new Map([
        ['1', versao('2026-09-28T21:50:00Z', conceder)],
        ['2', versao('2026-09-28T21:51:00Z', revogar)],
      ]),
    );
    segredo.antes = (op, v) => {
      const alvo = segredo.versoes.get('1');
      if (op === 'acessar' && v === '1' && alvo) alvo.etag = 'etag-novo';
    };
    const { saida, linhas } = await rodar(new ClienteSimulado(), segredo);
    expect(saida).toBe(3);
    expect(linhas.at(-1)).toEqual({
      resultado: 'falha',
      codigo: 'FALHA_INFRAESTRUTURA',
      erro_tipo: 'Error',
      codigo_tecnico: 'SEGREDO_HTTP_409',
    });
    expect(segredo.chamadas).not.toContain('obter:2');
  });

  it('conexão que cai entre pedidos: saída 3 antes de ler a versão seguinte, sem consulta na conexão caída', async () => {
    const cliente = new ClienteSimulado();
    const segredo = new SegredoSimulado(
      new Map([
        ['1', versao('2026-09-28T21:50:00Z', pedidoComId(id(1)))],
        ['2', versao('2026-09-28T21:51:00Z', pedidoComId(id(2)))],
      ]),
    );
    segredo.antes = (op) => {
      if (op === 'destruir') cliente.emit('end');
    };
    const { saida, linhas } = await rodar(cliente, segredo);
    expect(saida).toBe(3);
    expect(linhas.at(-1)).toMatchObject({ codigo_tecnico: 'CONEXAO_PERDIDA' });
    expect(segredo.chamadas.filter((c) => c.endsWith(':2'))).toEqual([]);
    expect(cliente.consultas.some((c) => c.includes('pg_advisory_unlock'))).toBe(false);
  });

  it('conexão que cai durante uma chamada à API: para ali, sem a chamada seguinte nem transação (revisão)', async () => {
    // Antes, a iteração seguia sem a trava: acessava, desativava o inválido ou mandava BEGIN na conexão caída.
    const casos: [string, unknown, string[]][] = [
      ['obter', { ...revogar, extra: 'x' }, ['obter:1']],
      ['acessar', { ...revogar, extra: 'x' }, ['obter:1', 'acessar:1']],
      ['obter', revogar, ['obter:1']],
      ['acessar', revogar, ['obter:1', 'acessar:1']],
    ];
    for (const [momento, dados, chamadas] of casos) {
      const cliente = new ClienteSimulado();
      const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', dados)]]));
      segredo.antes = (op) => {
        if (op === momento) cliente.emit('end');
      };
      const { saida, linhas } = await rodar(cliente, segredo);
      expect(saida, momento).toBe(3);
      expect(linhas, momento).toEqual([
        {
          resultado: 'falha',
          codigo: 'FALHA_INFRAESTRUTURA',
          erro_tipo: 'ErroFila',
          codigo_tecnico: 'CONEXAO_PERDIDA',
        },
      ]);
      expect(segredo.chamadas.slice(1), momento).toEqual(chamadas);
      expect(segredo.versoes.get('1')?.estado, momento).toBe('ENABLED');
      expect(cliente.consultas, momento).not.toContain('BEGIN');
    }
  });

  it('conexão que cai logo depois do COMMIT: registra o pedido e não destrói; a versão fica para a repetição', async () => {
    const cliente = new ClienteSimulado([
      (t) => {
        if (t === 'COMMIT') cliente.emit('error', new Error('socket'));
        return undefined;
      },
    ]);
    const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', revogar)]]));
    const { saida, linhas } = await rodar(cliente, segredo);
    expect(saida).toBe(3);
    expect(linhas).toEqual([
      { pedido_id: revogar.pedido_id, versao: '1', resultado: 'concedido', repetido: false },
      {
        resultado: 'falha',
        codigo: 'FALHA_INFRAESTRUTURA',
        erro_tipo: 'ErroFila',
        codigo_tecnico: 'CONEXAO_PERDIDA',
      },
    ]);
    expect(segredo.chamadas).not.toContain('destruir:1');
    expect(segredo.versoes.get('1')?.estado).toBe('ENABLED');
  });

  it('erro da conexão depois do último pedido também dá 3', async () => {
    const cliente = new ClienteSimulado();
    const segredo = new SegredoSimulado(new Map([['1', versao('2026-09-28T21:50:00Z', revogar)]]));
    segredo.antes = (op) => {
      if (op === 'destruir') cliente.emit('error', new Error('socket'));
    };
    expect((await rodar(cliente, segredo)).saida).toBe(3);
  });

  it('falha ao soltar a trava não muda a saída; valor lançado que não é Error sai só com o tipo', async () => {
    const cliente = new ClienteSimulado([
      (t) => (t.includes('pg_advisory_unlock') ? new Error('x') : undefined),
    ]);
    expect((await rodar(cliente, new SegredoSimulado(new Map()))).saida).toBe(0);
    const segredo = new SegredoSimulado(new Map());
    segredo.antes = () => {
      // eslint-disable-next-line @typescript-eslint/only-throw-error -- o caso é justamente um valor que não é Error
      throw 'texto solto com 0123456789';
    };
    const { saida, linhas } = await rodar(new ClienteSimulado(), segredo);
    expect(saida).toBe(3);
    expect(linhas).toEqual([{ resultado: 'falha', codigo: 'FALHA_INFRAESTRUTURA', erro_tipo: 'string' }]);
  });
});
