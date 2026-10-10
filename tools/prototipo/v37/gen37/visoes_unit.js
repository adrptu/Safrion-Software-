// VISOES-1 (10/10/2026) · regras puras do seletor de visões no g2lib, sem navegador: node visoes_unit.js
// U1–U9 do desenho (precedência, endereço, teclado, chave da preferência, celular) e a volta do detalhe (revisão Codex 6093255041, item 2).
// VISOES_G2LIB=<arquivo> roda contra outro g2lib (o anterior à F1, para ver o vermelho; ou um mutante).
const fs = require('fs'), path = require('path');
const arq = process.env.VISOES_G2LIB || path.join(__dirname, 'g2lib.js');
const src = fs.readFileSync(arq, 'utf8');
const NOMES = ['g2visaoValida', 'g2visaoInicial', 'g2visaoAviso', 'g2visaoUrl', 'g2visaoTecla', 'g2visaoChave', 'g2visaoPrefLer', 'g2visaoPrefGrava',
  'g2visoesCelular', 'g2voltaValido', 'g2voltaDecide', 'g2voltaUrl'];
const G = new Function('const G2_GLOSS=[];\n' + src + '\nreturn {' + NOMES.map(n => n + ': (typeof ' + n + "==='function'?" + n + ':null)').join(',') + '};')();
let ok = 0, falhas = 0;
const chk = (nome, f, extra) => { let c = false, x; try { c = !!f(); } catch (e) { x = String(e && e.message || e); }
  if (c) { ok++; console.log('OK  ' + nome); } else { falhas++; console.log('FALHOU ' + nome + (x ? ' · erro: ' + x : '') + (extra !== undefined ? ' · ' + JSON.stringify(extra) : '')); } };
const F = (n) => { if (!G[n]) throw new Error(n + ' ausente no g2lib'); return G[n]; };
const OS = ['lista', 'agrupada', 'kanban', 'carga'];   // visoes.validas('os')
const ini = (s, p, v) => F('g2visaoInicial')(s, p, v || OS);

// U1 · URL válida vence a preferência
chk('U1 ?view=agrupada vence a preferência kanban (fonte url, sem aviso)', () => { const r = ini('?view=agrupada', 'kanban'); return r.k === 'agrupada' && r.fonte === 'url' && !r.aviso; });
// U2 · URL fora das válidas cai para a preferência, com aviso que não repete o valor cru
chk('U2 ?view=mapa (fora das válidas da O.S.) abre a preferência kanban, com aviso sem o valor cru', () => { const r = ini('?view=mapa', 'kanban'); const a = F('g2visaoAviso')(r, 'Kanban');
  return r.k === 'kanban' && r.fonte === 'pref' && r.aviso && a.indexOf('Kanban (sua última escolha)') >= 0 && a.indexOf('mapa') < 0; });
chk('U2b ?view=<script> sem preferência abre a Lista e o aviso não traz o valor', () => { const r = ini('?view=%3Cscript%3E', null); const a = F('g2visaoAviso')(r, 'Lista');
  return r.k === 'lista' && r.aviso && a.indexOf('<') < 0 && a.indexOf('script') < 0 && /aberta em Lista\.$/.test(a); });
// U3–U4 · preferência antiga, inválida ou ausente
chk('U3 preferência antiga (calendario, não válida na O.S.) abre a Lista', () => ini('', 'calendario').k === 'lista');
chk('U3b preferência de lixo ("KANBAN") abre a Lista', () => ini('', 'KANBAN').k === 'lista');
chk('U4 sem URL e sem preferência: Lista, sem aviso', () => { const r = ini('', null); return r.k === 'lista' && !r.aviso && r.fonte === 'lista'; });
chk('U4b ?view= vazio: aviso e precedência (preferência kanban)', () => { const r = ini('?view=', 'kanban'); return r.k === 'kanban' && r.aviso; });
chk('U4c sem ?view a preferência vale (kanban)', () => { const r = ini('?theme=dark', 'kanban'); return r.k === 'kanban' && r.fonte === 'pref' && !r.aviso; });
// U5 · lixo é inválido
chk('U5 KANBAN, kanbán, <x>, "kanban " e "kanban1" são inválidos', () => ['KANBAN', 'kanbán', '<x>', 'kanban ', 'kanban1', ''].every(x => !F('g2visaoValida')(x, OS))
  && F('g2visaoValida')('kanban', OS) && !F('g2visaoValida')('mapa', OS));
// U6 · endereço: preserva hash e outros parâmetros; a escolha explícita da Lista mantém ?view=lista (revisão Codex, item 1); ida e volta sem perda
const U = (p, s, h, k) => F('g2visaoUrl')(p, s, h, k);
chk('U6 #OS-0420 fica: /OS.dc.html?view=agrupada#OS-0420', () => U('/OS.dc.html', '', '#OS-0420', 'agrupada') === '/OS.dc.html?view=agrupada#OS-0420');
chk('U6b ?theme=dark e #tal=Santa Rita|T1 ficam', () => U('/OS.dc.html', '?theme=dark', '#tal=Santa Rita|T1', 'agrupada') === '/OS.dc.html?theme=dark&view=agrupada#tal=Santa Rita|T1');
chk('U6c escolher a Lista grava ?view=lista (não tira o parâmetro)', () => U('/OS.dc.html', '?view=kanban', '#OS-0430:ajustar', 'lista') === '/OS.dc.html?view=lista#OS-0430:ajustar');
chk('U6d sem visão (k vazio) tira só o view; os outros parâmetros ficam', () => U('/OS.dc.html', '?theme=dark&view=xyz', '', '') === '/OS.dc.html?theme=dark');
chk('U6e ida e volta: o endereço gravado reabre na mesma visão e preserva theme', () => OS.every(k => { const u = U('/OS.dc.html', '?theme=dark', '#x', k); const q = u.slice(u.indexOf('?'), u.indexOf('#'));
  return ini(q, 'kanban').k === k && new URLSearchParams(q).get('theme') === 'dark' && u.endsWith('#x'); }));
chk('U6f (Codex, item 1) preferência kanban → escolher Lista → F5: abre a Lista', () => { const u = U('/OS.dc.html', '', '', 'lista'); return ini(u.slice(u.indexOf('?')), 'kanban').k === 'lista'; });
// U7 · teclado: seta move o foco e nunca ativa
const T = (i, k, n, m) => F('g2visaoTecla')(i, k, n || 4, m);
chk('U7 → com volta (3 → 0), ← com volta (0 → 3), Home 0 e End 3', () => T(3, 'ArrowRight').foco === 0 && T(1, 'ArrowRight').foco === 2 && T(0, 'ArrowLeft').foco === 3 && T(2, 'Home').foco === 0 && T(1, 'End').foco === 3);
chk('U7b ↑ e ↓ não movem na barra; no "mais", ↓ abre o menu', () => T(1, 'ArrowUp') === null && T(1, 'ArrowDown') === null && T(3, 'ArrowDown', 4, true).abre === true && !('foco' in T(3, 'ArrowDown', 4, true)));
chk('U7c Enter, Espaço e outras teclas devolvem nulo (ativar é do botão); nenhuma seta ativa', () => ['Enter', ' ', 'a', '1', 'Tab', 'Escape'].every(k => T(1, k) === null)
  && ['ArrowRight', 'ArrowLeft', 'Home', 'End'].every(k => { const r = T(1, k); return r && Object.keys(r).join() === 'foco'; }));
// U8 · chave da preferência e armazenamento que lança
const quebrado = { getItem() { throw new Error('bloqueado'); }, setItem() { throw new Error('bloqueado'); } };
chk('U8 chave por perfil × entidade com o prefixo safrion.pref.visao:', () => F('g2visaoChave')('Ana', 'os') === 'safrion.pref.visao:Ana:os' && F('g2visaoChave')('Caio', 'os') !== F('g2visaoChave')('Ana', 'os'));
chk('U8b armazenamento que lança: ler devolve nulo e a entrada abre a Lista, sem erro', () => { const v = F('g2visaoPrefLer')('safrion.pref.visao:U8b:os', quebrado); return v === null && ini('', v).k === 'lista'; });
chk('U8c gravar com armazenamento que lança não quebra e vale na memória da tela', () => { F('g2visaoPrefGrava')('safrion.pref.visao:U8c:os', 'kanban', quebrado); return F('g2visaoPrefLer')('safrion.pref.visao:U8c:os', quebrado) === 'kanban'; });
// U9 · celular
const C = (v, a) => F('g2visoesCelular')(v, a);
chk('U9 até 3 visões: todas na barra, sem "mais"', () => { const r = C(['lista', 'agrupada', 'kanban'], 'lista'); return r.barra.length === 3 && r.mais.length === 0 && !r.maisAtivo; });
chk('U9b 4 visões: 3 na barra + "mais" com a Carga', () => { const r = C(OS, 'lista'); return r.barra.join() === 'lista,agrupada,kanban' && r.mais.join() === 'carga' && !r.maisAtivo; });
chk('U9c ativa dentro do "mais" (carga) marca o "mais"', () => C(OS, 'carga').maisAtivo === true);
chk('U9d uma visão só: nada (sem barra)', () => { const r = C(['lista'], 'lista'); return r.barra.length === 0 && r.mais.length === 0; });
// V · volta do detalhe (revisão Codex 6093255041, item 2): back só com histórico comprovado; senão destino canônico; contexto validado
const ctx = { arq: 'OS.dc.html', ent: 'os', gid: 'g_os', view: 'agrupada', q: 'theme=dark', foco: 'OS-0421', nt: 'ab12cd34', t: 1, dest: 'CA-01det.dc.html' };
const D = (c, a, h) => F('g2voltaDecide')(c, a, h);
chk('V1 mesma aba (marca do detalhe = contexto e história > 1): history.back()', () => D(ctx, 'OS.dc.html', { len: 3, marca: 'ab12cd34' }) === 'back');
chk('V2 nova aba (history.length = 1, sem marca): destino canônico com ?view', () => D(ctx, 'OS.dc.html', { len: 1, marca: undefined }) === 'canonico' && F('g2voltaUrl')(ctx) === 'OS.dc.html?theme=dark&view=agrupada');
chk('V3 referrer sem histórico comprovado (marca de outro contexto): canônico, nunca back', () => D(ctx, 'OS.dc.html', { len: 4, marca: 'zz99' }) === 'canonico');
chk('V4 link para outra lista ou contexto inválido (arquivo, entidade, visão): o link segue como está', () => D(ctx, 'EST.dc.html', { len: 3, marca: 'ab12cd34' }) === 'link'
  && D(Object.assign({}, ctx, { arq: 'javascript:alert(1)' }), 'javascript:alert(1)', { len: 3 }) === 'link' && D(Object.assign({}, ctx, { view: 'KANBAN' }), 'OS.dc.html', { len: 3 }) === 'link'
  && D(Object.assign({}, ctx, { arq: '../x/OS.dc.html' }), '../x/OS.dc.html', { len: 3 }) === 'link' && D(null, 'OS.dc.html', { len: 3 }) === 'link');
console.log(`TOTAL ${ok + falhas} · OK ${ok} · FALHAS ${falhas}`);
process.exit(falhas ? 1 : 0);
