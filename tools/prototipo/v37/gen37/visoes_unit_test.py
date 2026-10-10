# -*- coding: utf-8 -*-
"""VISOES-1 (10/10/2026) · regras do seletor de visões sem navegador: python3 visoes_unit_test.py
1. node visoes_unit.js (U1–U9 e a volta do detalhe V1–V4): precedência, endereço, teclado, preferência, celular;
2. P1–P3: a visão nasce do atributo dominante (visoes.py, fonte única do build e dos testes); negativos; painel de visão não sustentada
   falha o build; uma visão só, sem barra;
3. componente (engine.visoes): toolbar com rótulo, um botão por visão com aria-label "Ver em …", aria-pressed, foco itinerante, ícone
   aria-hidden e nenhum texto visível; "mais" com 4 ou mais; nunca o verde cheio; CSS 32/44 px, ativo tonal com barra de 2 px, contraste;
   licença do Lucide (ISC, com o MIT do Feather);
4. mutantes que têm de ficar vermelhos: precedência invertida, seta que ativa, aria-pressed ausente, Calendário aceito sem data;
5. com o build feito: só a O.S. tem seletor; o botão "Agrupar por talhão" saiu (um caminho só); nenhum arrastar.
VISOES_DIR=<gen37> roda contra outra árvore (ex.: a anterior à F1, para ver o vermelho)."""
import os, re, sys, subprocess, tempfile, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.environ.get('VISOES_DIR') or HERE)
if D != HERE: sys.path[:] = [x for x in sys.path if os.path.abspath(x or '.') != HERE]   # a outra árvore não enxerga os módulos desta
sys.path.insert(0, D)
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if (extra != '' and not cond) else ''), flush=True)
def tenta(f, padrao=None):
    try: return f()
    except Exception as e: return padrao if padrao is not None else e

# 1 · regras puras do g2lib (node)
def node(g2lib):
    env = dict(os.environ, VISOES_G2LIB=g2lib)
    return subprocess.run(['node', os.path.join(HERE, 'visoes_unit.js')], capture_output=True, text=True, env=env)
r = node(os.path.join(D, 'g2lib.js'))
for l in r.stdout.strip().splitlines():
    if l.startswith('FALHOU'): print('   ' + l)
print('   ' + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]))
chk('1 node visoes_unit.js (U1–U9, V1–V4)', r.returncode == 0, r.stdout[-400:] + r.stderr[-300:])

V = tenta(lambda: importlib.import_module('visoes'))
E = tenta(lambda: importlib.import_module('engine'))
temV, temE = not isinstance(V, Exception), not isinstance(E, Exception) and hasattr(E, 'visoes')

# 2 · P1–P3
def p1():
    if not temV: return ['visoes.py ausente']
    f = []
    if V.validas('os') != ['lista', 'agrupada', 'kanban', 'carga']: f.append(('validas', V.validas('os')))
    for k, at in V.REGISTRO['os']['ativas'].items():
        if not all(str(at.get(a) or '').strip() for a in V.EXIGE[k]): f.append(('sem fonte', k))
    for k, m in V.REGISTRO['os']['cortes'].items():
        if not str(m).strip(): f.append(('corte sem motivo', k))
    if 'DEC-2609-09' not in V.REGISTRO['os']['cortes'].get('mapa', ''): f.append('O.S. sem Mapa: DEC-2609-09 mantida')
    if V.ORDEM[0] != 'lista': f.append('Lista não é a primeira')
    return f
f1 = p1(); chk('P1 validas(os) = lista, agrupada, kanban, carga; cada visão com os atributos que EXIGE pede, com fonte; cortes com motivo (Mapa: DEC-2609-09)', not f1, f1)
def p2():
    if not temV: return ['visoes.py ausente']
    s = V.sustenta; f = []
    neg = [('calendario', {}, 'sem data, sem Calendário'), ('timeline', {'inicio': 'x'}, 'sem início E fim, sem Timeline'), ('mapa', {'local': 'texto'}, 'sem geometria, sem Mapa'),
           ('kanban', {'estado': 'x'}, 'sem fluxo, sem Kanban'), ('agrupada', {'categoria': 'x'}, 'sem valor somável, sem Agrupada'), ('arvore', {}, 'sem pai e filho, sem Árvore'),
           ('galeria', {'fotos': 'contagem'}, 'sem foto principal, sem Galeria'), ('carga', {'recurso': 'x'}, 'sem tempo, sem Carga'), ('matriz', {'linha': 'x', 'coluna': 'y'}, 'sem valor, sem Matriz')]
    for k, at, n in neg:
        if s(k, at): f.append(n)
    pos = [('calendario', {'data': 'ini ISO'}), ('timeline', {'inicio': 'a', 'fim': 'b'}), ('agrupada', {'categoria': 'a', 'somavel': 'b'})]
    for k, at in pos:
        if not s(k, at): f.append(('positivo recusado', k))
    if s('visao_inexistente', {}): f.append('visão desconhecida aceita')
    return f
f2 = p2(); chk('P2 negativos: sem data sem Calendário; sem início e fim sem Timeline; sem geometria sem Mapa; sem fluxo sem Kanban; sem somável sem Agrupada; sem pai/filho sem Árvore; sem foto sem Galeria', not f2, f2)
def p2b():
    if not (temV and temE): return 'componente ausente'
    V.REGISTRO['_um'] = {'ativas': {'lista': {}}, 'cortes': {}}
    try: return E.visoes('g_um', '_um', {'lista': '<i>X</i>'}, 'Visão de teste')
    finally: V.REGISTRO.pop('_um', None); E.VISOES_SPEC.pop('g_um', None)
r2b = tenta(p2b); chk('P2b uma visão só: sem barra (devolve só o painel)', r2b == ('', '<i>X</i>'), r2b)
def p3():
    if not (temV and temE): return ['componente ausente']
    f = []; P = {'lista': 'L', 'agrupada': 'lista', 'kanban': 'K', 'carga': 'C'}
    for nome, pn in (('painel de Mapa (não sustentado na O.S.)', dict(P, mapa='M')), ('painel faltando (carga)', {k: v for k, v in P.items() if k != 'carga'}),
                     ('apelido para visão sem painel', dict(P, agrupada='calendario'))):
        try: E.visoes('g_p3', 'os', pn, 'r'); f.append(nome + ': não falhou')
        except ValueError: pass
    V.REGISTRO['_cal'] = {'ativas': {'lista': {}, 'calendario': {'data': ''}}, 'cortes': {}}
    try: V.validas('_cal'); f.append('calendário sem fonte de data: não falhou')
    except ValueError: pass
    finally: V.REGISTRO.pop('_cal', None)
    E.VISOES_SPEC.pop('g_p3', None); return f
f3 = p3(); chk('P3 painel para visão não sustentada, painel faltando ou apelido sem painel e visão sem fonte fazem o build falhar (ValueError)', not f3, f3)

# 3 · componente
def barra_os():
    E.VISOES_SPEC.pop('g_c', None); b, c = E.visoes('g_c', 'os', {'lista': '<i>L</i>', 'agrupada': 'lista', 'kanban': '<i>K</i>', 'carga': '<i>C</i>'}, 'Visão das ordens'); E.VISOES_SPEC.pop('g_c', None); return b, c
def checa_barra(b, val):
    f = []
    if 'role="toolbar"' not in b or 'aria-label="Visão das ordens"' not in b: f.append('toolbar com rótulo')
    if f'data-visoes="{" ".join(val)}"' not in b: f.append('data-visoes')
    bts = re.findall(r'<button type="button" data-visao="([a-z]+)"([^>]*)>(.*?)</button>', b)
    if [x[0] for x in bts] != val: f.append(('botões', [x[0] for x in bts]))
    for k, at, dentro in bts:
        if f'aria-label="Ver em {V.NOME[k]}"' not in at: f.append(('aria-label', k))
        if not re.search(r'aria-pressed="\{\{[^}]+\}\}"', at): f.append(('aria-pressed', k))
        if not re.search(r'tabIndex="\{\{[^}]+\}\}"', at): f.append(('tabIndex itinerante', k))
        if 'title=' in at: f.append(('title', k))
        if not dentro.startswith('<svg') or 'aria-hidden="true"' not in dentro or re.sub(r'<[^>]+>', '', dentro).strip(): f.append(('só ícone aria-hidden, sem texto', k))
    if len(val) > 3 and not re.search(r'data-visao-mais="1" aria-haspopup="menu"', b): f.append('"mais" no estreito')
    if re.search(r'background:\s*#1E7A4C', b, re.I): f.append('verde cheio')
    return f
if temV and temE:
    b, corpo = barra_os(); fb = checa_barra(b, V.validas('os'))
    chk('C0 barra: role=toolbar "Visão das ordens", 4 botões data-visao na ordem fixa, aria-label "Ver em …", aria-pressed e tabIndex do estado, só ícone aria-hidden, sem title, "mais" (4 visões), sem verde cheio', not fb, fb)
    chk('C0b corpo: estado da visão (role=status) e um painel por grupo (Lista e Tabela agrupada no mesmo painel), sem invólucro em volta do painel',
        'role="status" data-visoes-estado="g_c"' in corpo and corpo.count('<i>L</i>') == 1 and corpo.count('{{g_c_vp_') == 3 and '{{g_c_vp_agrupada}}' not in corpo and 'display: contents' not in corpo, corpo[:300])
    css = E.VISOES_CSS
    chk('C0c CSS: 32 px no computador; 44 px e ícone 20 px com ponteiro grosso OU até 640 px; até 640 px só as 3 primeiras e o "mais"; no G2_CSS de toda tela',
        'width:32px;height:32px' in css and '@media (pointer:coarse),(max-width:640px){.g2visoes>button{width:44px;height:44px}.g2visoes>button svg{width:20px;height:20px}}' in css
        and ':not([data-i="0"]):not([data-i="1"]):not([data-i="2"]){display:none}' in css and css in E.G2_CSS, css[:200])
    ativo = css.split('.g2visoes>button[aria-pressed=true]', 1)[-1].split('}', 1)[0]
    chk('C0d ativo tonal: fundo #E4F3E9, ícone #1E6B47, borda e barra interna de 2 px (#1E7A4C), nunca fundo verde cheio', 'background:#E4F3E9' in ativo and 'color:#1E6B47' in ativo and 'inset 0 -2px 0 #1E7A4C' in ativo and 'background:#1E7A4C' not in ativo, ativo)
    def lum(h):
        h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]; c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    def ctr(a, b): la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
    DV = E.DS_VISOES; ci, ca = ctr(DV['inativo'], DV['trilho']), ctr(DV['ativo_icone'], DV['ativo_fundo'])   # os tokens do engine, não uma cópia
    chk(f'C0e contraste do ícone: inativo {ci:.2f}:1 sobre o trilho e ativo {ca:.2f}:1 sobre o tonal (≥ 4,5:1)', ci >= 4.5 and ca >= 4.5, (ci, ca))
    lic = os.path.join(D, 'LICENSES', 'lucide-ISC.txt'); t = open(lic, encoding='utf-8').read() if os.path.exists(lic) else ''
    chk('C0f licença: LICENSES/lucide-ISC.txt com o ISC do Lucide 1.45.0 e o MIT do Feather (Cole Bemis); ícones v_* no engine', 'ISC License' in t and 'lucide-static 1.45.0' in t and 'Cole Bemis' in t and 'Feather' in t
        and all(k in E.ICONS for k in ('v_lista', 'v_agrupada', 'v_kanban', 'v_carga', 'v_mais')), lic)
else:
    for n in ('C0', 'C0b', 'C0c', 'C0d', 'C0e', 'C0f'): chk(n + ' componente do seletor (engine.visoes)', False, 'ausente')

# 4 · mutantes (cada um tem de ficar vermelho)
def mut_js(nome, velho, novo):
    src = open(os.path.join(D, 'g2lib.js'), encoding='utf-8').read()
    if velho not in src: return None
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as fh: fh.write(src.replace(velho, novo, 1)); tmp = fh.name
    try: return node(tmp)
    finally: os.unlink(tmp)
m1 = mut_js('precedência', "if(q!==null&&g2visaoValida(q,validas)) return {k:q,fonte:'url',aviso:false};",
            "if(g2visaoValida(pref,validas)) return {k:pref,fonte:'pref',aviso:false}; if(q!==null&&g2visaoValida(q,validas)) return {k:q,fonte:'url',aviso:false};")
chk('M1 mutante "precedência invertida" (preferência antes da URL) fica vermelho', m1 is not None and m1.returncode != 0 and 'FALHOU U1' in m1.stdout, (m1.stdout[-300:] if m1 else 'sem a regra'))
m2 = mut_js('seta', "if(tecla==='ArrowRight') return {foco:(i+1)%n};", "if(tecla==='ArrowRight') return {foco:(i+1)%n,ativa:true};")
chk('M2 mutante "seta que ativa" fica vermelho', m2 is not None and m2.returncode != 0 and 'FALHOU U7c' in m2.stdout, (m2.stdout[-300:] if m2 else 'sem a regra'))
if temV and temE:
    b, _ = barra_os(); bm = re.sub(r' aria-pressed="\{\{[^}]+\}\}"', '', b)
    chk('M3 mutante "aria-pressed ausente" é acusado pela verificação do componente', bool(checa_barra(bm, V.validas('os'))) and not checa_barra(b, V.validas('os')))
    ant = V.EXIGE['calendario']; V.EXIGE['calendario'] = []
    try: fm = p2()
    finally: V.EXIGE['calendario'] = ant
    chk('M4 mutante "Calendário aceito sem data" fica vermelho em P2', 'sem data, sem Calendário' in fm and not p2(), fm)
else:
    chk('M3 mutante "aria-pressed ausente"', False, 'componente ausente'); chk('M4 mutante "Calendário aceito sem data"', False, 'visoes.py ausente')

# 5 · com o build feito
P = os.path.join(D, 'project')
if os.path.isdir(P):
    pags = {f: open(os.path.join(P, f), encoding='utf-8').read() for f in os.listdir(P) if f.endswith('.dc.html')}
    com = sorted(f for f, s in pags.items() if 'data-visoes=' in s)
    s = pags.get('OS.dc.html', '')
    chk('B1 só a O.S. tem o seletor nesta fatia, com as 4 visões; G2_VISOES vai na página', com == ['OS.dc.html'] and 'data-visoes="lista agrupada kanban carga"' in s and 'const G2_VISOES = {"g_os"' in s, com)
    chk('B2 um caminho só: o botão "Agrupar por talhão" (os_agrgo) e as abas de texto Lista | Kanban | Recursos saíram', 'os_agrgo' not in s and '>Recursos</button>' not in s and '>Kanban</button>' not in s, '')
    chk('B3 nenhum arrastar (Kanban e Carga sem draggable)', 'draggable' not in s)
    # §2.4: toda escrita de URL nas telas com seletor preserva location.search (replaceState só com o pathname apagaria o ?view)
    ruins = [f for f in com if re.search(r"replaceState\([^)]*location\.pathname\s*\)", pags[f])]
    chk('B4 telas com seletor: nenhuma escrita de URL que apague a query (?view)', not ruins, ruins)
else:
    chk('B1–B4 build feito (project/)', False, 'sem project/')
print(f'RESULTADO: {"OK" if all(ok) else "FALHOU"} {sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
