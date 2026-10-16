// Quantas vezes o efeito plantado "dias quentes e secos" (qs) aparece, direto ou pelo grupo que anda junto (tmax+, dpv+, ur-),
// por variante de controle de época. Uso: node calor.mjs repro.json
import fs from 'node:fs';
const R = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ok = x => /^(qs\+|tmax\+|dpv\+|ur-):/.test(x);
const conta = (runs, alvo) => { let n = 0, any = 0, fm = 0; for (const rr of Object.values(runs)) { const o = rr[alvo]; if (!o || o.frio) continue; n++;
  const e = o.exibidos.filter(ok); if (e.length) any++; if (e.some(x => /:(forte|moderada)/.test(x))) fm++; } return `${any}/${n} exibido (F/M ${fm}/${n})`; };
const semEpoca = Object.assign({ original: R.original }, R.replicas);
for (const alvo of ['acaro', 'mosca', 'cochon']) console.log(`${alvo}: calor/ar seco — sem controle de época ${conta(semEpoca, alvo)} · mês ${conta(R.epoca.mes, alvo)} · tendência suave ${conta(R.epoca.suave, alvo)}`);
