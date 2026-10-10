// DS-SEPARADOR, DS-HOVER, DS-RETORNO e DS-DICA (09/10/2026) · regras puras do g2lib, sem navegador: node ds_unit.js
// 1. texto da dica (explícito > selo do dicionário > title que acrescenta > nome do ícone sem texto > nada; nunca repete o rótulo visível)
// 2. dicionário de estados: as 5 fases do Kanban (AGENTS §4) e os selos de bloqueio têm significado e próximo passo
// 3. contraste AA (WCAG 2.2, 4,5:1) do texto sobre o hover verde, da primária escurecida, do realce e da dica
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'g2lib.js'), 'utf8');
// glossário de teste para a sigla da célula (o texto real vem do engine.GLOSSARIO no build; aqui importa a regra de g2glossCol)
const GL = [['\\bDAP\\b', 'DAP: dias após o plantio.'], ['sc/ha', 'sc/ha: sacas por hectare.'], ['R\\$/ha·mês', 'R$/ha·mês: reais por hectare por mês.'],
  ['R\\$/ha(?![·/])', 'R$/ha: reais por hectare.'], ['\\bCOT\\b', 'COT: custo operacional total.']];
const G = new Function('const G2_GLOSS=' + JSON.stringify(GL) + ';\n' + src + '\nreturn {g2dicaRegra, g2dicaDe, G2_DICAS, g2contem, g2norm, g2glossCol, g2part};')();
let ok = 0, falhas = 0;
const chk = (nome, cond, extra) => { if (cond) { ok++; console.log('OK  ' + nome); } else { falhas++; console.log('FALHOU ' + nome + (extra !== undefined ? ' · ' + JSON.stringify(extra) : '')); } };

// ---------- 1 · regra do texto ----------
const R = G.g2dicaRegra;
chk('1.1 data-dica explícito vence o title', R({dica: 'Falta a aprovação do agrônomo', title: 'Aprovar', vis: 'Aprovar e liberar', aria: '', comando: true}) === 'Falta a aprovação do agrônomo');
chk('1.2 data-dica vazio = sem dica (mesmo com title)', R({dica: '', title: 'Abrir a ordem', vis: 'OS-0430', comando: true}) === '');
chk('1.3 title igual ao rótulo visível não vira dica', R({dica: null, title: 'Mapa', vis: 'Mapa', aria: '', comando: true}) === '');
chk('1.4 title contido no rótulo (sem acento e caixa) não vira dica', R({dica: null, title: 'Planejar safra', vis: 'PLANEJAR SAFRA ›', comando: true}) === '');
chk('1.5 title que acrescenta ao rótulo vira dica', R({dica: null, title: 'Mudar dose ou área antes de liberar (gera a versão seguinte)', vis: 'Ajustar', comando: true}) === 'Mudar dose ou área antes de liberar (gera a versão seguinte)');
chk('1.6 ícone sem texto mostra o nome do comando', R({dica: null, title: '', vis: '×', aria: 'Fechar', comando: true}) === 'Fechar');
chk('1.7 menu recolhido (texto oculto) mostra o nome do grupo', R({dica: null, title: 'Agrícola', vis: '', aria: '', comando: true}) === 'Agrícola');
chk('1.8 texto com nome acessível e rótulo visível: sem dica', R({dica: null, title: '', vis: 'Nova ordem', aria: 'Nova ordem', comando: true}) === '');
chk('1.9 nome acessível sem ser comando (selo, célula) não vira dica', R({dica: null, title: '', vis: '', aria: 'Situação', comando: false}) === '');
chk('1.10 data-dica-de busca o selo no dicionário', R({dica: null, de: 'A liberar', title: '', vis: 'A liberar', comando: false}).indexOf('Aprovar e liberar') >= 0);
chk('1.11 data-dica-de de selo desconhecido: sem dica', R({dica: null, de: 'Em dia', title: '', vis: 'Em dia', comando: false}) === '');

// ---------- 2 · dicionário de estados ----------
const FASES = ['A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas'];   // Kanban: exatamente 5 fases
chk('2.1 as 5 fases do Kanban têm dica com próximo passo (Encerradas: sem próximo passo)', FASES.every(f => G.g2dicaDe(f) && /Próximo passo|Sem próximo passo/.test(G.g2dicaDe(f))), FASES.map(f => G.g2dicaDe(f)));
chk('2.2 A liberar: Aprovar e liberar com dois registros (agrônomo aprova, gestor libera; PEND-OS-01)', /agrônomo aprova/.test(G.g2dicaDe('A liberar')) && /gestor libera/.test(G.g2dicaDe('A liberar')) && /dois registros/.test(G.g2dicaDe('A liberar')));
chk('2.2b A liberar: as exceções da aprovação (irrigação só com água, manutenção, beneficiamento) não são ditas como aprovação do agrônomo', /só com água/.test(G.g2dicaDe('A liberar')) && /manutenção/.test(G.g2dicaDe('A liberar')) && /beneficiamento/.test(G.g2dicaDe('A liberar')) && /responsável próprio/.test(G.g2dicaDe('A liberar')));
chk('2.3 o selo com detalhe ("Falta insumo · Ureia 45%") usa a chave antes de " · "', G.g2dicaDe('Falta insumo · Ureia 45%') === G.G2_DICAS['Falta insumo'] && !!G.g2dicaDe('Falta insumo · Ureia 45%'));
chk('2.4 bloqueios do encerramento nomeiam quem resolve', /almoxarife/.test(G.g2dicaDe('Sobras a receber')) && /reconecta o app/.test(G.g2dicaDe('Aguardando sinal do app')) && /conferência decide/.test(G.g2dicaDe('Apontamento em conferência')));
chk('2.5 nenhuma dica do dicionário repete só o nome do selo', Object.entries(G.G2_DICAS).every(([k, v]) => G.g2norm(v) !== G.g2norm(k) && v.length > k.length + 10));
chk('2.6 texto sem chave conhecida: vazio', G.g2dicaDe('Qualquer coisa') === '' && G.g2dicaDe('') === '' && G.g2dicaDe(null) === '');

chk('2.7 nenhuma dica do dicionário cita caminho de menu (o nome do item muda; revisão DS, achado 6)', Object.values(G.G2_DICAS).every(v => v.indexOf('›') < 0 && !/Produção|Cargas e recebimento/.test(v)), Object.values(G.G2_DICAS).filter(v => v.indexOf('›') >= 0));
chk('2.8 "Carga a pesar" sai do dicionário: o selo só existe com o bloqueio do encerramento e a dica vem de osEncBloq (osSeloDica)', !('Carga a pesar' in G.G2_DICAS) && G.g2dicaDe('Carga a pesar') === '');
const pdv = G.g2part({ k: 'chip', t: 'Sobras a receber', c: 'yellow', de: 1, dv: 'Encerrar bloqueado: sobra em custódia. Próximo passo: Rui (almoxarife) recebe a devolução.' }), pde = G.g2part({ k: 'chip', t: 'Sobras a receber', c: 'yellow', de: 1, dv: '' });
chk('2.9 selo com o texto do bloqueio (dv, osSeloDica) usa esse texto, só visual como o do dicionário; sem ele, o dicionário', pdv.dica.indexOf('Encerrar bloqueado') === 0 && !pdv.hasDica && pde.dica === G.G2_DICAS['Sobras a receber'] && !pde.hasDica, [pdv.dica, pdv.hasDica, pde.dica]);

// ---------- 2b · sigla ou unidade na célula vira dica do cabeçalho (revisão DS, achado 8) ----------
const L = (k, ts) => ts.map((t, i) => ({ id: 'r' + i, s: { [k]: t } }));
const prod = L('p', ['62,4 sc/ha', '58,1 sc/ha', '—', '60,0 sc/ha']);
chk('2b.1 coluna com "62,4 sc/ha" nas células: a dica do cabeçalho explica sc/ha', G.g2glossCol({ id: 'g1' }, { k: 'p' }, prod) === 'sc/ha: sacas por hectare.', G.g2glossCol({ id: 'g1' }, { k: 'p' }, prod));
chk('2b.2 termo solto numa observação (1 de 10 células) não vira dica da coluna', G.g2glossCol({ id: 'g2' }, { k: 'o' }, L('o', ['meta de 60 sc/ha'].concat(Array(9).fill('sem ocorrência')))) === '');
chk('2b.3 código de registro (COT-0031) não é a sigla COT', G.g2glossCol({ id: 'g3' }, { k: 'c' }, L('c', ['COT-0031', 'COT-0032', 'COT-0040'])) === '');
chk('2b.4 sigla na célula ("35 DAP") e partes da célula (selo) contam', G.g2glossCol({ id: 'g4' }, { k: 'd' }, [{ id: 'a', s: { d: '' }, p: { d: [{ k: 'chip', t: '35 DAP' }] } }, { id: 'b', s: { d: '42 DAP' } }]) === 'DAP: dias após o plantio.');
const g5 = G.g2glossCol({ id: 'g5' }, { k: 'x' }, L('x', ['R$/ha·mês', 'R$/ha·mês']));
chk('2b.5 R$/ha·mês usa a entrada própria e não soma a de R$/ha (revisão DS, achado 7)', g5 === 'R$/ha·mês: reais por hectare por mês.', g5);
const rs = L('p', ['10 sc/ha']); const a1 = G.g2glossCol({ id: 'g6' }, { k: 'p' }, rs), a2 = G.g2glossCol({ id: 'g6' }, { k: 'p' }, L('p', ['sem unidade']));
chk('2b.6 linhas novas na grade refazem a conta (o guardado vale só para as mesmas linhas)', a1 === 'sc/ha: sacas por hectare.' && a2 === '', [a1, a2]);
chk('2b.7 grade sem linhas: sem dica', G.g2glossCol({ id: 'g7' }, { k: 'p' }, []) === '');
{ const cs = [...Array(12)].map((_, i) => ({ k: 'c' + i })), tx = 'Aplicação no talhão T7 com pulverizador, dose 0,5 L/ha, observação longa de campo 62,4 sc/ha';
  let pior = 0; for (let it = 0; it < 8; it++) { const rr = [...Array(400)].map((_, i) => ({ id: 'r' + i, s: Object.fromEntries(cs.map(c => [c.k, tx + ' ' + i])) }));
    const t = process.hrtime.bigint(); cs.forEach(c => G.g2glossCol({ id: 'g8' }, c, rr)); const ms = Number(process.hrtime.bigint() - t) / 1e6; if (it > 1) pior = Math.max(pior, ms); }
  chk('2b.8 custo: grade de 400 linhas × 12 colunas, linhas novas a cada desenho (pior caso: o termo em toda célula) abaixo de 25 ms', pior < 25, pior.toFixed(1) + ' ms'); }

// ---------- 3 · contraste AA ----------
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const lum = c => { const l = c.map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]; };
const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const sobre = (base, cor, a) => base.map((v, i) => Math.round(v * (1 - a) + cor[i] * a));   // camada translúcida sobre o fundo
const VERDE = hex('#1E7A4C'), BRANCO = hex('#FFFFFF'), INK = hex('#15201A'), MUTED = hex('#65736A'), ACCS = hex('#E4F3E9'), YELS = hex('#FFF3D6'), YEL = hex('#8A5A00'), RED = hex('#B42318');
const hoverBranco = sobre(BRANCO, VERDE, 0.07), hoverTonal = sobre(ACCS, VERDE, 0.07), hoverAmarelo = sobre(YELS, VERDE, 0.07), ativo = sobre(BRANCO, VERDE, 0.14);
const casos = [
  ['texto (#15201A) sobre o hover verde do branco', INK, hoverBranco], ['texto apagado (#65736A) sobre o hover verde', MUTED, hoverBranco],
  ['ação (#1E7A4C) sobre o hover verde', VERDE, hoverBranco], ['ação sobre o hover do selecionado tonal', hex('#1E6B47'), hoverTonal],
  ['amarelo (#8A5A00) sobre o hover do selo amarelo', YEL, hoverAmarelo], ['texto sobre o pressionado (.14)', INK, ativo],
  ['texto sobre o fundo da linha (#F2F8F4)', INK, hex('#F2F8F4')], ['texto apagado sobre a linha (#F2F8F4)', MUTED, hex('#F2F8F4')],
  ['vermelho sobre o hover destrutivo', RED, sobre(BRANCO, RED, 0.06)],
  ['branco sobre a primária escurecida (brightness .92)', BRANCO, VERDE.map(v => Math.round(v * 0.92))],
  ['texto sobre o realce (#EDF7F0)', INK, hex('#EDF7F0')], ['texto apagado sobre o realce', MUTED, hex('#EDF7F0')], ['ação sobre o realce', VERDE, hex('#EDF7F0')],
  ['branco sobre a dica (#15201A)', BRANCO, INK]];
casos.forEach(([n, a, b]) => chk('3 · ' + n + ' ≥ 4,5:1', cr(a, b) >= 4.5, cr(a, b).toFixed(2)));
chk('3 · o hover do branco é verde (G > R e G > B), não cinza', hoverBranco[1] > hoverBranco[0] && hoverBranco[1] > hoverBranco[2], hoverBranco);

console.log(`RESULTADO: ${falhas ? 'FALHOU' : 'OK'} ${ok}/${ok + falhas}`);
process.exit(falhas ? 1 : 0);
