import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, mover, semear, type Ambiente, type Semente } from './ambiente.js';

let amb: Ambiente;
let s: Semente;
beforeAll(async () => {
  amb = await criarBanco();
  s = await semear(amb.app, 'Imutavel');
  await mover(amb.app, s, 'k-i', 0, {
    tipo: 'entrada',
    quantidade: '5',
    unidade: 'L',
    situacao: 'liberado_livre',
  });
});
afterAll(async () => {
  await amb.encerrar();
});

describe('fatos imutáveis (ENG-026; IDEM-17; NFR-04)', () => {
  it('a aplicação não altera nem apaga movimento, auditoria ou registro de intenção concluído', async () => {
    const tentativas: [string, string][] = [
      ['UPDATE app.stock_movement SET base_quantity = 999', '42501'],
      ['DELETE FROM app.stock_movement', '42501'],
      ['UPDATE app.audit_log SET reason = $$outro$$', '42501'],
      ['DELETE FROM app.audit_log', '42501'],
      ['DELETE FROM app.intent_record', '42501'],
      ["UPDATE app.intent_record SET outcome = 'rejected'", 'P0001'],
    ];
    for (const [sql, codigo] of tentativas) {
      await expect(
        emOrganizacao(amb.app, s.org, (c) => c.query(sql)),
        sql,
      ).rejects.toMatchObject({ code: codigo });
    }
  });

  it('nem o dono das tabelas altera fato registrado: o gatilho recusa', async () => {
    for (const sql of [
      'UPDATE app.stock_movement SET base_quantity = 999',
      'DELETE FROM app.audit_log',
      "UPDATE app.intent_record SET reason_code = 'x'",
    ]) {
      await expect(
        emOrganizacao(amb.migrator, s.org, (c) => c.query(sql)),
        sql,
      ).rejects.toMatchObject({
        code: 'P0001',
      });
    }
  });
});
