// Apenas dados sintéticos de teste. Não executar este arquivo como aplicação.
import https from 'node:https';

// ruleid: safrion-tls-verification-disabled
const unsafeAgent = new https.Agent({ rejectUnauthorized: false });
// ok: safrion-tls-verification-disabled
const safeAgent = new https.Agent({ rejectUnauthorized: true });
// ruleid: safrion-tls-verification-disabled
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
// ok: safrion-tls-verification-disabled
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '1';

async function unsafeJson(req, db) {
  const input = await req.json();
  // ruleid: safrion-request-in-sql
  return db.query(`SELECT id FROM lote WHERE nome = '${input.nome}'`);
}

async function safeJson(req, db) {
  const input = await req.json();
  // ok: safrion-request-in-sql
  return db.query('SELECT id FROM lote WHERE nome = $1', [input.nome]);
}

async function unsafeText(req, db) {
  const text = await req.text();
  // ruleid: safrion-request-in-sql
  return db.query(text);
}

function unsafeQuery(req, db) {
  // ruleid: safrion-request-in-sql
  return db.query('SELECT id FROM lote WHERE id = ' + req.query.id);
}

function unsafeParams(req, db) {
  // ruleid: safrion-request-in-sql
  return db.query({ text: 'SELECT id FROM lote WHERE id = ' + req.params.id });
}

function safeConfig(req, db) {
  // ok: safrion-request-in-sql
  return db.query({ text: 'SELECT id FROM lote WHERE id = $1', values: [req.params.id] });
}

function unsafeUrl(url, db) {
  const id = url.searchParams.get('id');
  // ruleid: safrion-request-in-sql
  return db.query('SELECT id FROM lote WHERE id = ' + id);
}

function safeUrl(url, db) {
  const id = url.searchParams.get('id');
  // ok: safrion-request-in-sql
  return db.query('SELECT id FROM lote WHERE id = $1', [id]);
}
