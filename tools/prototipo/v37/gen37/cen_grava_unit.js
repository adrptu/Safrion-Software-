// Gravação do cenário (Codex 6150155986) · node, sem navegador. Executor: cen_grava_test.py. Dados sintéticos.
// Modo estrito: só confirma depois de gravar; cota cheia → erro recuperável e nada muda. Modo padrão: a mudança fica visível nesta aba,
// com aviso, e a cópia antiga gravada não a esconde. Repetir depois de liberar espaço grava.
(() => {
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 400))); } }
const caso = (t, f) => { console.log('\n— ' + t); try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const cheia = (on) => { __cota = on; };
const lido = () => { const t = __ls[CEN_KEY]; return t ? JSON.parse(t) : null; };
const marca = (c, v) => { c.__sonda = v; return { msg: 'Sonda ' + v + ' registrada' }; };

caso('gravação normal: confirma e grava', () => {
  cheia(false); cenReset(); const r = cenMudar(null, c => marca(c, 'a'));
  ok('sem erro e sem aviso', !r.erro && !r.naoGravado && r.msg === 'Sonda a registrada', r);
  ok('gravado e lido de volta', (lido() || {}).__sonda === 'a' && cenGet().__sonda === 'a', [lido() && lido().__sonda, cenGet().__sonda]);
});
caso('modo estrito com a cota cheia: erro recuperável e nada muda (memória, armazenamento e cenGet)', () => {
  cheia(false); cenReset(); cenMudar(null, c => marca(c, 'antes')); const s0 = __ls[CEN_KEY], m0 = JSON.stringify(cenGet()), rev0 = cenGet().rev;
  cheia(true); const r = cenMudar(null, c => marca(c, 'depois'), { estrito: true });
  ok('erro com o motivo e o caminho', r.erro === CEN_GRAVA_ERRO && /libere espaço e repita/.test(r.erro), r);
  ok('armazenamento idêntico', __ls[CEN_KEY] === s0);
  ok('memória e cenGet iguais ao estado anterior (rev ' + rev0 + ')', JSON.stringify(cenGet()) === m0 && cenGet().__sonda === 'antes' && JSON.stringify(CEN_MEM) === m0, cenGet().__sonda);
  cheia(false); const r2 = cenMudar(null, c => marca(c, 'depois'), { estrito: true });
  ok('repetir depois de liberar espaço grava uma vez (rev +1)', !r2.erro && (lido() || {}).__sonda === 'depois' && cenGet().rev === rev0 + 1, [r2, cenGet().rev]);
});
caso('modo padrão com a cota cheia: a mudança vale nesta aba, com aviso, e a cópia antiga não a esconde', () => {
  cheia(false); cenReset(); cenMudar(null, c => marca(c, 'antes'));
  cheia(true); const r = cenMudar(null, c => marca(c, 'depois'));
  ok('mensagem com o aviso e naoGravado', /o navegador não gravou/.test(r.msg || '') && r.naoGravado === true, r);
  ok('cenGet mostra a mudança (não volta à cópia antiga)', cenGet().__sonda === 'depois', cenGet().__sonda);
  ok('a cópia antiga saiu do armazenamento', __ls[CEN_KEY] === undefined);
  cheia(false);
});
caso('erro do comando continua sem gravar, nos dois modos', () => {
  cheia(false); cenReset(); cenMudar(null, c => marca(c, 'x')); const s0 = __ls[CEN_KEY];
  const r1 = cenMudar(null, c => { throw new Error('recusado'); }); const r2 = cenMudar(null, c => { throw new Error('recusado'); }, { estrito: true });
  ok('erro devolvido e armazenamento idêntico', r1.erro === 'recusado' && r2.erro === 'recusado' && __ls[CEN_KEY] === s0);
});
console.log('\nRESULTADO_JS ' + (nfail ? 'FALHA ' + nfail : 'OK'));
})();
