// EDL-01 · funções puras do "Editar talhões" (safra_lote.js, bloco SL-PURO) no node. Executor: saf_lote_unit_test.py. Dados sintéticos.
(() => {
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 400))); } }
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const CTX = { culturas: ['Soja', 'Milho', 'Feijão', 'Café', 'Mamão Formosa'], ini: '2026-09-01', fim: '2027-08-31',
  planos: [{ id: 'SOJA-AT', nome: 'Soja alta tecnologia', versao: 6, cultura: 'Soja' }, { id: 'SOJA-PD', nome: 'Soja padrão', versao: 3, cultura: 'Soja' }, { id: 'MILHO-SF', nome: 'Milho safrinha', versao: 4, cultura: 'Milho' }],
  cultivares: [['Soja', '58 W', 118], ['Soja', '62 X', 112], ['Milho', 'Híbrido AG 8700', 140]],
  sugere: (cu) => cu === 'Milho' ? { var: 'Híbrido AG 8700', plano: 'MILHO-SF', plantio: '2027-02-20' } : (cu === 'Soja' ? { var: '58 W', plano: 'SOJA-AT', plantio: '2026-10-15' } : {}) };
const LINS = [
  { k: 'c3', tipo: 'tal', rot: 'T2', T: 298, cult: 'Soja', trava: { area: 'A área do talhão inteiro vem do cadastro (CD-01).', cult: 'OS-0421 em execução', var: 'OS-0421 em execução', plano: 'OS-0421 em execução' } },
  { k: 'c5', tipo: 'tal', rot: 'T3', T: 96, cult: 'Soja', trava: { area: 'A área do talhão inteiro vem do cadastro (CD-01).' } },
  { k: 'c1', tipo: 'par', rot: 'T1-A', T: 312, cult: 'Soja', trava: {} },
  { k: 'ro:T7', tipo: 'ro', rot: 'T7', T: 42, motivoRo: 'Perene · só leitura', trava: {} },
  { k: 'novo:P2', tipo: 'novo', rot: 'P2', T: 80, cult: '', trava: { area: 'área livre calculada' } } ];
const V0 = { c3: { area: '298', cult: 'Soja', var: '58 W', plantio: '2026-10-18', meta: '63', plano: 'SOJA-AT' }, c5: { area: '96', cult: 'Soja', var: '62 X', plantio: '2026-10-22', meta: '62', plano: '' },
  c1: { area: '160', cult: 'Soja', var: '58 W', plantio: '2026-10-15', meta: '64', plano: 'SOJA-AT' }, 'novo:P2': { area: '80', cult: '', var: '', plantio: '', meta: '', plano: '' } };

console.log('— slTsv: bloco copiado do Excel/Planilhas');
ok('linhas por \\r\\n, células por tabulação, quebra final ignorada', eq(slTsv('a\tb\r\nc\td\r\n'), [['a', 'b'], ['c', 'd']]), slTsv('a\tb\r\nc\td\r\n'));
ok('\\n e \\r sozinhos também quebram linha', eq(slTsv('1\n2\r3'), [['1'], ['2'], ['3']]));
ok('célula entre aspas com tabulação, quebra e aspas duplicadas', eq(slTsv('"x\ty"\t"a ""b"""\n"l1\nl2"\tz'), [['x\ty', 'a "b"'], ['l1\nl2', 'z']]), slTsv('"x\ty"\t"a ""b"""\n"l1\nl2"\tz'));
ok('célula vazia no meio continua na posição', eq(slTsv('a\t\tc'), [['a', '', 'c']]));
ok('linhas vazias do fim saem', eq(slTsv('a\n\n\t\n'), [['a']]));
ok('espaços nas pontas da célula saem', eq(slTsv(' 64 \t 58 W '), [['64', '58 W']]));

console.log('— slNumTxt: número pt-BR');
ok('"1.234,5" → "1234,5"', slNumTxt('1.234,5') === '1234,5', slNumTxt('1.234,5'));
ok('"12,5" e "12.5" → "12,5"', slNumTxt('12,5') === '12,5' && slNumTxt('12.5') === '12,5');
ok('"64 sc/ha" → "64" (a unidade colada junto sai)', slNumTxt('64 sc/ha') === '64');
ok('negativo, texto e vazio → null', slNumTxt('-3') === null && slNumTxt('abc') === null && slNumTxt('') === null);

console.log('— slData: datas com atalho');
ok('aaaa-mm-dd fica', slData('2026-10-15', CTX) === '2026-10-15');
ok('dd/mm/aaaa → ISO', slData('15/10/2026', CTX) === '2026-10-15');
ok('dd/mm/aa → 20aa', slData('15/10/26', CTX) === '2026-10-15');
ok('dd/mm sem ano: o ano que cai dentro da safra (out → 2026; fev → 2027)', slData('15/10', CTX) === '2026-10-15' && slData('20/02', CTX) === '2027-02-20', [slData('15/10', CTX), slData('20/02', CTX)]);
ok('ddmmaaaa e ddmm (só dígitos)', slData('15102026', CTX) === '2026-10-15' && slData('2002', CTX) === '2027-02-20');
ok('31/02 e 13/13 → null (data que não existe)', slData('31/02/2027', CTX) === null && slData('13/13/2026', CTX) === null);
ok('texto → null; vazio → ""', slData('amanhã', CTX) === null && slData('  ', CTX) === '');

console.log('— slPode: o que cada célula aceita (mesmas regras do painel do cultivo e do Dividir)');
const p = (k, c, t, cu) => slPode(LINS.find(l => l.k === k), c, t, CTX, cu);
ok('O.S. liberada ou em execução prende cultura, variedade e plano, com o motivo', !p('c3', 'cult', 'Milho').ok && /OS-0421/.test(p('c3', 'cult', 'Milho').motivo) && !p('c3', 'var', 'X').ok && !p('c3', 'plano', 'SOJA-PD').ok);
ok('na linha com O.S., plantio e meta seguem editáveis', p('c3', 'plantio', '20/10/2026').ok && p('c3', 'meta', '65').ok);
ok('área do talhão inteiro vem do cadastro (recusa com motivo)', !p('c5', 'area', '90').ok && /cadastro/.test(p('c5', 'area', '90').motivo));
ok('área da parcela: número, mínimo 0,01 ha e no máximo a área do talhão', p('c1', 'area', '150,5').v === '150,5' && !p('c1', 'area', '0').ok && !p('c1', 'area', '400').ok && /312/.test(p('c1', 'area', '400').motivo), p('c1', 'area', '400'));
ok('perene só leitura recusa tudo com o motivo', !p('ro:T7', 'meta', '50').ok && p('ro:T7', 'meta', '50').motivo === 'Perene · só leitura');
ok('cultura pelo nome sem acento nem maiúscula ("feijao" → Feijão); cultura fora do cadastro recusa', p('c5', 'cult', 'feijao').v === 'Feijão' && !p('c5', 'cult', 'Trigo').ok);
ok('plano pelo nome, pelo código e pelo nome com versão', p('c5', 'plano', 'soja padrão').v === 'SOJA-PD' && p('c5', 'plano', 'SOJA-AT').v === 'SOJA-AT' && p('c5', 'plano', 'Soja alta tecnologia v6').v === 'SOJA-AT');
ok('plano de outra cultura recusa (a cultura do rascunho conta)', !p('c5', 'plano', 'Milho safrinha').ok && /plano de Milho não serve para Soja/.test(p('c5', 'plano', 'Milho safrinha').motivo) && p('c5', 'plano', 'Milho safrinha', 'Milho').ok);
ok('"sem plano" limpa o plano', p('c5', 'plano', 'sem plano').ok && p('c5', 'plano', 'sem plano').v === '');
ok('meta inválida recusa; data inválida recusa com o formato', !p('c5', 'meta', 'muito').ok && /dd\/mm\/aaaa/.test(p('c5', 'plantio', '32/10').motivo));

console.log('— slTrocaCult: trocar a cultura arrasta plano e variedade');
const tc = slTrocaCult({ cult: 'Soja', var: '58 W', plano: 'SOJA-AT', plantio: '2026-10-15', meta: '64' }, 'Milho', CTX, LINS[1]);
ok('plano e variedade da cultura anterior saem; vazios recebem a sugestão da safra; plantio e meta ficam', tc.plano === 'MILHO-SF' && tc.var === 'Híbrido AG 8700' && tc.plantio === '2026-10-15' && tc.meta === '64', tc);
const tn = slTrocaCult({ cult: '', var: '', plano: '', plantio: '', meta: '' }, 'Soja', CTX, LINS[4]);
ok('linha livre ganha variedade, plano e o primeiro plantio possível; a meta nunca vem de sugestão', tn.var === '58 W' && tn.plano === 'SOJA-AT' && tn.plantio === '2026-10-15' && tn.meta === '', tn);
const tv = slTrocaCult({ cult: 'Soja', var: 'Minha seleção', plano: '', plantio: '', meta: '' }, 'Milho', CTX, LINS[1]);
ok('variedade digitada fora do cadastro fica (não se apaga o que não se sabe de quem é)', tv.var === 'Minha seleção', tv);

console.log('— slColarBloco: colar a partir da célula focada');
const dados = LINS.filter(l => l.tipo !== 'grp');
const M = slTsv('Milho\tHíbrido AG 8700\t20/02/2027\t180\tMilho safrinha\nSoja\t62 X\t25/10\t60\tSoja padrão\nSoja\t58 W\t01/11/2026\t62\tSOJA-AT\nSoja\t58 W\t01/11/2026\t62\tSOJA-AT\n');
const r = slColarBloco(dados, V0, 0, 'cult', M, CTX);
ok('dimensão 4 × 5', eq(r.dim, [4, 5]), r.dim);
ok('T2 (O.S. em execução): cultura, variedade e plano recusados; plantio e meta colados', r.vals.c3.cult === 'Soja' && r.vals.c3.var === '58 W' && r.vals.c3.plano === 'SOJA-AT' && r.vals.c3.plantio === '2027-02-20' && r.vals.c3.meta === '180', r.vals.c3);
ok('T3 recebe a linha inteira (cultura antes do plano)', eq(r.vals.c5, { area: '96', cult: 'Soja', var: '62 X', plantio: '2026-10-25', meta: '60', plano: 'SOJA-PD' }), r.vals.c5);
ok('T1-A recebe a 3ª linha', r.vals.c1.var === '58 W' && r.vals.c1.plantio === '2026-11-01' && r.vals.c1.meta === '62');
ok('T7 (perene) recusa a 4ª linha inteira', !r.vals['ro:T7'] && r.recusas.filter(x => x.rot === 'T7').length === 5, r.recusas.filter(x => x.rot === 'T7'));
ok('contagem: 4 + 2 + 5 + 5 colados = 12 e 3 + 5 recusados = 8', r.n === 12 && r.recusas.length === 8, [r.n, r.recusas.length]);
ok('o rascunho de partida não muda (nada é salvo antes do Salvar)', V0.c5.cult === 'Soja' && V0.c5.var === '62 X' && V0.c5.plano === '');
const r2 = slColarBloco(dados, V0, 3, 'meta', [['1', '2', '3']], CTX);
ok('além da última coluna e da última linha: recusas com o motivo', r2.recusas.some(x => x.motivo === 'além da última coluna') && slColarBloco(dados, V0, 4, 'meta', [['1'], ['2']], CTX).recusas.some(x => x.motivo === 'além da última linha'), r2.recusas);
const r3 = slColarBloco(dados, V0, 1, 'cult', [['', '64 Z']], CTX);
ok('célula vazia do bloco não apaga o que estava', r3.vals.c5.cult === 'Soja' && r3.vals.c5.var === '64 Z' && r3.n === 1);
ok('texto das recusas cita linha, coluna e motivo', /^8 recusados \(T2 · Cultura: OS-0421/.test(slRecusasTxt(r.recusas)), slRecusasTxt(r.recusas));

console.log('— slAplicarSel: aplicar aos marcados');
const a = slAplicarSel(dados, V0, { c3: true, c5: true, 'novo:P2': true, 'ro:T7': true }, { cult: 'Milho', plano: 'MILHO-SF', meta: '' }, CTX);
ok('só os campos preenchidos da faixa', eq(a.cols, ['cult', 'plano']), a.cols);
ok('T3 e P2 recebem Milho e o plano do milho; T2 (O.S.) e T7 (perene) recusam com o motivo', a.vals.c5.cult === 'Milho' && a.vals.c5.plano === 'MILHO-SF' && a.vals['novo:P2'].cult === 'Milho' && a.vals.c3.cult === 'Soja'
  && a.recusas.filter(x => x.rot === 'T2').length === 2 && a.recusas.filter(x => x.rot === 'T7').length === 2, a.recusas);
ok('linha livre que recebe a cultura ganha o plantio sugerido (primeiro possível)', a.vals['novo:P2'].plantio === '2027-02-20', a.vals['novo:P2']);
const a2 = slAplicarSel(dados, V0, { c5: true }, { plano: 'Milho safrinha' }, CTX);
ok('plano de outra cultura sem trocar a cultura: recusado', a2.n === 0 && /plano de Milho não serve para Soja/.test(a2.recusas[0].motivo), a2.recusas);

console.log('— slPlano exato (revisão do Codex 6229216931, PR #47): sem prefixo, nome repetido é ambíguo, a ordem do catálogo não decide');
{
  const P1 = { id: 'P1', nome: 'Soja', versao: 1, cultura: 'Soja' }, P2 = { id: 'P2', nome: 'Soja precoce', versao: 1, cultura: 'Soja' }, P3 = { id: 'P3', nome: 'Soja', versao: 2, cultura: 'Soja' };
  const M1 = { id: 'M1', nome: 'Milho safrinha', versao: 4, cultura: 'Milho' };
  const perms = (a) => a.length <= 1 ? [a] : a.flatMap((x, i) => perms(a.slice(0, i).concat(a.slice(i + 1))).map(r => [x].concat(r)));
  const L = { k: 'c5', tipo: 'tal', rot: 'T3', T: 96, cult: 'Soja', trava: {} };
  const casos = [['Soja precoce v9', null], ['Soja v99', null], ['Soja', 'ambíguo'], ['P2', 'P2'], ['Soja precoce v1', 'P2'], ['soja PRECOCE', 'P2'], ['Soja v2', 'P3'], ['soja v1', 'P1'],
    ['Soja v2 · 8 atividades', 'P3'], ['Milho safrinha', 'outra'], ['sem plano', '']];
  const res = perms([P1, P2, P3, M1]).map(ps => { const cx = Object.assign({}, CTX, { planos: ps });
    return casos.map(([t]) => { const r = slPode(L, 'plano', t, cx, 'Soja'); return r.ok ? r.v : (/ambíguo/.test(r.motivo) ? 'ambíguo' : (/não serve/.test(r.motivo) ? 'outra' : null)); }); });
  const r0 = res[0];
  ok('"Soja precoce v9" e "Soja v99" recusados (não encontrados; nada por prefixo)', r0[0] === null && r0[1] === null, r0);
  ok('"Soja" com Soja v1 e Soja v2 no catálogo: recusado como ambíguo, com as versões no motivo', r0[2] === 'ambíguo' && /ambíguo: Soja v1, Soja v2; informe com a versão/.test(slPode(L, 'plano', 'Soja', Object.assign({}, CTX, { planos: [P1, P2, P3] }), 'Soja').motivo),
    slPode(L, 'plano', 'Soja', Object.assign({}, CTX, { planos: [P1, P2, P3] }), 'Soja').motivo);
  ok('código exato (P2) e nome com versão exatos (Soja precoce v1, Soja v2, soja v1) aceitos', r0[3] === 'P2' && r0[4] === 'P2' && r0[6] === 'P3' && r0[7] === 'P1', r0);
  ok('nome único sem versão (Soja precoce) aceito; o rótulo da lista ("Soja v2 · 8 atividades") também', r0[5] === 'P2' && r0[8] === 'P3', r0);
  ok('plano de outra cultura continua recusado pela cultura; "sem plano" limpa', r0[9] === 'outra' && r0[10] === '', r0);
  ok('as 24 ordens do catálogo dão a mesma resolução', res.length === 24 && res.every(r => JSON.stringify(r) === JSON.stringify(r0)), res.filter(r => JSON.stringify(r) !== JSON.stringify(r0)).slice(0, 2));
  const cx = Object.assign({}, CTX, { planos: [P1, P2, P3] }); const V = { c5: { area: '96', cult: 'Soja', var: '62 X', plantio: '2026-10-22', meta: '62', plano: 'P1' } };
  const col = slColarBloco([L], V, 0, 'plano', [['Soja']], cx); const apl = slAplicarSel([L], V, { c5: true }, { plano: 'Soja v99' }, cx);
  ok('colar e "Aplicar aos marcados" recusam com o motivo e o rascunho fica (P1)', col.n === 0 && /ambíguo/.test(col.recusas[0].motivo) && col.vals.c5.plano === 'P1' && apl.n === 0 && /não encontrado/.test(apl.recusas[0].motivo) && apl.vals.c5.plano === 'P1', [col.recusas, apl.recusas]);
}
console.log('— revisão do app do Codex (#98, P2): cultivar de outra cultura e erro já corrigido');
{
  const L = { k: 'c5', tipo: 'tal', rot: 'T3', T: 96, cult: 'Soja', trava: {} };
  const pm = slPode(L, 'var', '58 W', CTX, 'Milho');
  ok('cultivar cadastrada de outra cultura é recusada pela regra (vale para célula, colagem e faixa); a da própria cultura e o texto livre passam',
    !pm.ok && /cultivar de Soja, não de Milho/.test(pm.motivo) && slPode(L, 'var', '58 W', CTX, 'Soja').ok && slPode(L, 'var', 'Cultivar própria', CTX, 'Milho').ok, pm);
  const b = slAplicarSel([L], { c5: Object.assign({}, V0.c5) }, { c5: true }, { cult: 'Milho', var: '58 W' }, CTX);
  ok('faixa com Milho e a cultivar de soja (58 W) que sobrou: a linha fica Milho sem a 58 W, e a recusa diz por quê', b.vals.c5.cult === 'Milho' && b.vals.c5.var !== '58 W' && b.recusas.some(x => x.col === 'var' && /cultivar de Soja/.test(x.motivo)), b);
  const cb = slColarBloco([L], { c5: Object.assign({}, V0.c5, { cult: 'Milho', var: '' }) }, 0, 'var', [['62 X']], CTX);
  ok('colar a cultivar de soja (62 X) numa linha de milho: recusado, o rascunho fica', cb.n === 0 && cb.vals.c5.var === '' && /cultivar de Soja/.test((cb.recusas[0] || {}).motivo), cb);
  const SE = typeof slSemErro === 'function' ? slSemErro : null; const E = { c5: { var: 'Informe a variedade', meta: 'Informe a meta' }, c3: { cult: 'x', plano: 'y' } };
  ok('slSemErro: a célula corrigida sai do erro, o resto fica; a cultura leva junto o erro do plano', !!SE && eq(SE(E, [['c5', 'var'], ['c3', 'cult']]), { c5: { meta: 'Informe a meta' } }), SE && SE(E, [['c5', 'var'], ['c3', 'cult']]));
  ok('aplicar e colar devolvem as células feitas (para limpar o erro)', eq(slAplicarSel([L], { c5: Object.assign({}, V0.c5) }, { c5: true }, { meta: '70' }, CTX).feitos, [['c5', 'meta']])
    && eq(slColarBloco([L], { c5: Object.assign({}, V0.c5) }, 0, 'meta', [['70']], CTX).feitos, [['c5', 'meta']]));
}
console.log('— slContar: células alteradas (contador do Salvar)');
ok('sem mudança → 0', slContar(dados, V0, V0) === 0);
ok('mudança de espaço nas pontas não conta', slContar(dados, Object.assign({}, V0, { c5: Object.assign({}, V0.c5, { var: ' 62 X ' }) }), V0) === 0);
ok('colagem acima: 12 células coladas, 7 mudaram de valor (colar o mesmo valor não conta)', slContar(dados, r.vals, V0) === 7, slContar(dados, r.vals, V0));
console.log(nfail ? ('\n' + nfail + ' FALHA(S)') : '\nTODOS OK');
})();
