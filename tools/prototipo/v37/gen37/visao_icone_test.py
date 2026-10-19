"""VIS-08 · Visão pelo ícone (proprietário, 18/10/2026: "O modo de visão em mapa em planejar safra tem que ser pelo ícone igual os demais").
Varredura estática das telas do menu (sem navegador): todo seletor de visão (role=group ou toolbar com rótulo "Visão…" ou "Visualização…")
tem só botões de ícone, como o seletor da VISOES-1: cada botão com o svg e sem texto visível (o nome vai no aria-label e na dica).
Fora, com o motivo: grupos com o rótulo "Visão" que não trocam o modo de ver a mesma lista (EXCECOES).
Contraprova: o render da v138 (antes da VIS-08) reprova no Planejar safra, na CD-01 e no Beneficiamento.
Uso: python3 visao_icone_test.py [pasta do render] (padrão: _render)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_render')
MENU = {f for f, b in json.load(open(os.path.join(HERE, 'project', 'canvas.json'), encoding='utf-8'))['boards'].items() if b.get('page') == 'menu'}
# grupos com rótulo "Visão" que não são modo de visão (trocam o conjunto de dados ou o submenu); (página, classe do grupo): motivo
EXCECOES = {
    ('COLH.dc.html', 'pr-vis'): 'Por talhão | Por semana: duas análises diferentes da colheita, não dois modos de ver a mesma lista',
    ('MA.dc.html', 'ma-vis'): 'Sem ordem | Ordens | Ativos | Planos: os subitens do menu da Manutenção (DS-MAN), não modos de ver a mesma lista',
}
GRUPO = re.compile(r'<div([^>]*?)role="(?:group|toolbar)"([^>]*?)aria-label="(Vis(?:ão|ualização)[^"]*)"([^>]*)>(.*?)</div>', re.S)
BOTAO = re.compile(r'<button\b[^>]*>(.*?)</button>', re.S)
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
desvios, vistos = [], 0
for f in sorted(MENU):
    p = os.path.join(R, f)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    for m in GRUPO.finditer(s):
        attrs = m.group(1) + m.group(2) + m.group(4); cls = (re.search(r'class="([^"]*)"', attrs) or [None, ''])[1]
        if any(f == pg and c in cls.split() for pg, c in EXCECOES): continue
        bts = BOTAO.findall(m.group(5))
        if not bts: continue
        vistos += 1
        ruins = [re.sub(r'\s+', ' ', re.sub(r'<svg.*?</svg>', '', b, flags=re.S)).strip() or '(sem svg)' for b in bts
                 if '<svg' not in b or re.sub(r'<[^>]+>', '', re.sub(r'<svg.*?</svg>', '', b, flags=re.S)).strip()]
        if ruins: desvios.append((f, m.group(3), ruins[:4]))
chk(f'VIS-08 seletores de visão só com ícone nas telas do menu ({vistos} seletores em {len(MENU)} telas; exceções com motivo: {len(EXCECOES)})',
    vistos > 0 and not desvios, desvios)
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(0 if OK and not FAIL else 1)
