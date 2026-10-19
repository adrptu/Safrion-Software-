# -*- coding: utf-8 -*-
"""Galeria de conferência visual (skill padrao-safrion, passo 7): uma foto por família de tela × largura (1440 e 390 px), para o agente OLHAR
antes de publicar (teste verde não vê poluição visual nem desalinhamento). Fotos em GALERIA_DIR (padrão: _galeria/).
Famílias obrigatórias (FAMILIAS): lista do motor, agrupada, árvore, cadastro, Atividades do plano (Tabela e Cartões), Planejar safra, Kanban,
formulário (aberto pela primária "Criar…"/"Cadastrar…"), mapa e app de campo. Cobertura conferida (revisão do Codex no #73, 16/10/2026):
página ausente no render, estado que não abre (ex.: formulário) ou foto que não sai REPROVA a rodada completa (saída 1) e o inventário
família × largura diz o que faltou. Com filtro (argumento), roda só as fotos cujo nome contém o filtro e declara COBERTURA PARCIAL: serve para
olhar uma mudança, não substitui a rodada completa. Dados sintéticos; render em RENDER_DIR ou _render.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B galeria.py [filtro | --contraprova]"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OUT = os.environ.get('GALERIA_DIR') or os.path.join(HERE, '_galeria')
# abrir o formulário pela primária do cabeçalho ("Criar ordem", "Cadastrar parceiro"…) e esperar o painel (aside role=dialog)
ABRE_FORM = ("(()=>{const b=[...document.querySelectorAll('header button, main button')].find(b=>b.getClientRects().length&&/^(Criar|Cadastrar)\\b/.test(b.innerText.trim()));"
             " if(!b) return 'sem primária de criar'; b.click(); return 'ok';})()")
TEM_FORM = "!!document.querySelector('aside[role=dialog]')"
# prova de estado (revisão do Codex 6215833046): título exato da tela + componente-chave VISÍVEL da família + condição própria.
# Página trocada, app trocado, Kanban que caiu na tabela ou componente ausente reprovam (modo --contraprova confere isso).
VIS = "(e=>!!e&&e.getClientRects().length>0)"
def prova(titulo, chave, extra='true'):
    return (f"(()=>{{const v={VIS}; const k=[...document.querySelectorAll({chave!r})].filter(v);"
            f" return document.title==={titulo!r} && k.length>0 && ({extra});}})()")
SEM_TABELA = "![...document.querySelectorAll('[role=table][data-g2g]')].some(v)"
# (família, nome da foto, endereço, ação JS ou '', título, componente-chave, condição própria)
FAMILIAS = [
    ('lista do motor', 'os_tabela', 'OS.dc.html', '', 'Ordem de Serviço', '[role=table][data-g2g=g_os] [role=row][data-rid]',
     "!document.querySelector('[aria-label=\"Kanban das ordens\"]')"),
    ('agrupada', 'os_agrupada_talhao', 'OS.dc.html?ag=onde', '', 'Ordem de Serviço', '[data-g2g=g_os] [data-rid^="grp@"]', 'true'),
    ('cartões', 'os_cartoes', 'OS.dc.html?view=cartoes', '', 'Ordem de Serviço', '[data-g2cd=g_os] .g2cd-g:not(.g2cd-hd)', SEM_TABELA),
    ('kanban', 'os_kanban', 'OS.dc.html?view=kanban', '', 'Ordem de Serviço', '[aria-label="Kanban das ordens"] [role=button]',
     SEM_TABELA + " && [...document.querySelectorAll('[data-visao=kanban]')].some(e=>e.getAttribute('aria-pressed')==='true'||e.getAttribute('aria-selected')==='true')"),
    ('formulário', 'os_form_criar', 'OS.dc.html', ABRE_FORM, 'Ordem de Serviço', 'aside[role=dialog] input, aside[role=dialog] select', 'true'),
    ('árvore', 'cd06_produtos_arvore', 'CD-06.dc.html', '', 'Produtos, unidades e locais', '[data-g2g] [role=row] .g2car', 'true'),
    ('cadastro', 'cd05_parceiros', 'CD-05.dc.html', '', 'Parceiros e fornecedores', '[role=table][data-g2g] [role=row][data-rid]', 'true'),
    ('cadastro', 'cd01_fazendas', 'CD-01.dc.html', '', 'Fazendas, áreas e talhões', '[role=table][data-g2g] [role=row][data-rid]', 'true'),
    ('tabela própria', 'pa_tabela', 'PA.dc.html?view=tabela#plano=SOJA-AT', '', 'Planos agronômicos', '.pa-tb .pa-tb-l[data-atv]', 'true'),
    ('cartões próprios', 'pa_cartoes', 'PA.dc.html#plano=SOJA-AT', '', 'Planos agronômicos', '.pa-atividade[data-atv]',
     "![...document.querySelectorAll('.pa-tb')].some(v)"),
    ('etapas', 'saf_etapas', 'SAF.dc.html', '', 'Planejar safra',
     'ol[aria-label="Etapas do processo"] [aria-current=step], [aria-label^="Etapa "][aria-label*="mostrar todas as etapas"]', 'true'),   # faixa compacta abaixo de 800 px
    ('manutenção', 'ma_ordens', 'MA.dc.html?vis=ordens', '', 'Manutenção', '[role=table][data-g2g] [role=row][data-rid]', 'true'),
    ('consulta', 'agrofit', 'AG-07.dc.html', '', 'Consulta Agrofit', '[role=table][data-g2g] [role=row][data-rid]', 'true'),
    ('estoque', 'est', 'EST.dc.html', '', 'Estoque', 'nav[aria-label="Seções do estoque"]',
     "[...document.querySelectorAll('[role=table][data-g2g] [role=row][data-rid]')].some(v)"),
    ('mapa', 'mapa', 'IN-04.dc.html', '', 'Mapa da fazenda', '[role=tablist] [role=tab]', 'true'),
    ('app de campo', 'mb01_inicio', 'MB-01.dc.html', '', 'Hoje no campo', 'select[aria-label="Usuário do app (demonstração)"]',
     "[...document.querySelectorAll('a[href=\"MB-03.dc.html\"]')].some(v)"),
    ('app de campo', 'mb03_turno', 'MB-03.dc.html', '', 'Apontamento do turno', 'h1',
     "[...document.querySelectorAll('h1')].some(e=>v(e)&&e.innerText.trim()==='Apontamento do turno') && !document.querySelector('select[aria-label=\"Usuário do app (demonstração)\"]')"),
]
# contraprova: a prova de cada família no estado de outra (rota trocada, app trocado, Kanban → tabela, cartões → tabela)
TROCA = {'os_tabela': 'os_kanban', 'os_agrupada_talhao': 'os_tabela', 'os_cartoes': 'os_tabela', 'os_kanban': 'os_tabela',
         'os_form_criar': 'os_tabela', 'cd06_produtos_arvore': 'cd05_parceiros', 'cd05_parceiros': 'cd01_fazendas',
         'cd01_fazendas': 'cd05_parceiros', 'pa_tabela': 'pa_cartoes', 'pa_cartoes': 'pa_tabela', 'saf_etapas': 'est', 'ma_ordens': 'agrofit',
         'agrofit': 'ma_ordens', 'est': 'saf_etapas', 'mapa': 'est', 'mb01_inicio': 'mb03_turno', 'mb03_turno': 'mb01_inicio'}
LARGURAS = [(1440, 900, 1, False), (390, 844, 2, True)]

def contraprova(c, J, B):
    """Para cada família, nas duas larguras: (a) a prova no estado da família vizinha (TROCA) tem de dar falso; (b) com o componente-chave
    removido da página, a prova tem de dar falso. Saída 1 se alguma prova aceitar o estado errado."""
    por = {f[1]: f for f in FAMILIAS}; ruins = []; n = 0
    for w, h, esc, toque in LARGURAS:
        c.aparelho(w, h, esc, toque)
        for fam, nome, url, acao, tit, chave, extra in FAMILIAS:
            viz = por[TROCA[nome]]
            for caso in ('troca', 'ausente'):
                f = viz if caso == 'troca' else por[nome]
                c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
                c.goto(B + f[2], 1.6)
                if f[3]: J(f[3]); time.sleep(.6)
                if caso == 'ausente': J(f"document.querySelectorAll({chave!r}).forEach(e=>e.remove())")
                r = J(prova(tit, chave, extra)); n += 1
                print(f'{"FALHA" if r else "ok   "} contraprova {caso:7} {nome:22} {w:>5}' + (f' (estado de {viz[1]})' if caso == 'troca' else ''))
                if r: ruins.append((caso, nome, w))
    print(f'RESULTADO CONTRAPROVA: {n - len(ruins)}/{n} estados errados reprovados' + ('' if not ruins else f' · ACEITOS POR ENGANO: {ruins}'))
    return 1 if ruins else 0

def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ''
    os.makedirs(OUT, exist_ok=True)
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js
    B = f'http://127.0.0.1:{p}/'
    if filtro == '--contraprova':
        rc = contraprova(c, J, B); c.close(); return rc
    inv = []   # (família, nome, largura, situação)
    for w, h, esc, toque in LARGURAS:
        c.aparelho(w, h, esc, toque)
        for fam, nome, url, acao, tit, chave, extra in FAMILIAS:
            if filtro and filtro not in nome: continue
            pagina = url.split('?')[0].split('#')[0]
            if not os.path.exists(os.path.join(R, pagina)):
                inv.append((fam, nome, w, 'FALTA: página ausente no render (' + pagina + ')')); continue
            try:
                c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
                c.goto(B + url, 1.6)
                if acao:
                    r = J(acao); time.sleep(.6)
                    if r != 'ok': inv.append((fam, nome, w, 'FALTA: estado não abriu (' + str(r) + ')')); continue
                if not J(prova(tit, chave, extra)):
                    inv.append((fam, nome, w, 'FALTA: o estado esperado não apareceu (' + tit + ' · ' + chave + ')')); continue
                f = os.path.join(OUT, f'{nome}_{w}.png'); c.shot(f)
                inv.append((fam, nome, w, 'ok ' + f) if os.path.exists(f) and os.path.getsize(f) > 0 else (fam, nome, w, 'FALTA: foto não gravada'))
            except Exception as e:
                inv.append((fam, nome, w, 'FALTA: ' + str(e)[:120]))
    c.close()
    print(f'{"família":18} {"foto":24} {"largura":>7}  situação')
    for fam, nome, w, s in inv: print(f'{fam:18} {nome:24} {w:>7}  {s}')
    faltas = [x for x in inv if x[3].startswith('FALTA')]
    esperadas = len(FAMILIAS) * len(LARGURAS)
    if filtro:
        print(f'RESULTADO: COBERTURA PARCIAL (filtro "{filtro}"): {len(inv) - len(faltas)} fotos, {len(faltas)} faltas; não substitui a rodada completa')
        return 1 if faltas else 0
    ok = not faltas and len(inv) == esperadas
    print(f'RESULTADO: {len(inv) - len(faltas)}/{esperadas} fotos em {OUT}' + ('' if ok else f' · REPROVADO: {len(faltas)} faltas') + ' (olhe cada uma antes de publicar)')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
