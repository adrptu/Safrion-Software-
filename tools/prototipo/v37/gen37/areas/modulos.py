# -*- coding: utf-8 -*-
"""Telas de entrada dos módulos (13/10/2026, proprietário: "tire todos submenus de todos os módulos e coloque na tela como fizemos com
cadastros ... reduza texto ao mínimo essencial de cada submenu ... sempre com opção de voltar rápido e fácil. use sempre ícones mais
intuitivos para eliminar necessidade de textos longos. Mais minimalista e essencialista").
- Um cartão por tela do módulo, só com o ícone e o nome curto (fonte única: ui37.CURTO37); um toque abre a tela.
- Cada tela do módulo volta por "‹ Módulo" ao lado do título (ui37.VOLTA37).
- A barra lateral fica recolhida, um ícone por módulo com dica (ui37.navbar). O Mapa abre direto; a Manutenção (uma tela com visões)
  tem um cartão por visão (13/10, proprietário: "o menu de manutenção está sem os submenus na tela igual os demais").
- "Outros acessos" reúne as pontas que antes só o índice abria (app de campo, portal do parceiro, onboarding e backoffice).
O cartão (cartao) e o seu CSS também servem à tela Cadastros (areas/cad_inicio.py). Nada é gravado aqui.
- Blocos por macro contexto (14/10/2026, proprietário: primeiro um teste com setas curvas em 3 blocos; depois "Tire as setas, alinhe cada
  submenu no seu macro contexto e coloque titulos em cima dos blocos visuais de cada macro contexto"): o módulo com blocos (ui37.FLUXO37,
  só no Agrícola) mostra um painel por macro contexto (Planejamento, Execução, Resultados), com o título em cima e os cartões alinhados, na
  ordem do processo (uma lista ordenada por bloco: a ordem do DOM e do Tab é a do processo). Computador: blocos lado a lado; até 640 px de
  largura (ou 560 px de altura, celular deitado): uma coluna, blocos empilhados."""
import engine as E
from engine import icon
from ui37 import shell37, HEIGHTS37, MENU2, HUB37, CURTO37, OUTROS37, FLUXO37

CSS=('<style>.mod-grade{display:grid!important;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;align-content:start}'   # !important: a coluna do main põe display:flex nos filhos diretos
     '.mod-grade [hidden]{display:none!important}'   # o display:flex do cartão venceria o [hidden] padrão (busca da tela Cadastros)
     '.mod-item{display:flex;min-width:0}.mod-item>.mod-cartao{flex:1 1 auto;min-width:0}'   # item da lista no contêiner; o <a> segue link (revisão Codex CAD-INICIO-AX-01)
     '.mod-cartao{display:flex;align-items:center;gap:12px;padding:12px 16px;min-height:64px;box-sizing:border-box;border:1px solid #E4E9E5;border-radius:14px;'
     'background:#FFFFFF;text-decoration:none;color:#15201A;font-size:15px;font-weight:700;line-height:1.25}'
     '.mod-cartao:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}'
     '@media (hover:hover){.mod-cartao:hover{border-color:#1E7A4C;background:#F2F8F4}}'
     '.mod-ic{flex:0 0 auto;width:40px;height:40px;border-radius:12px;background:#E4F3E9;color:#1E7A4C;display:flex;align-items:center;justify-content:center}'
     '@media (max-width:600px){.mod-grade{grid-template-columns:1fr}}</style>')


def cartao(h, nome, ic, extra='', tag='div'):
    # o papel de item de lista fica no contêiner: o <a href> mantém o papel nativo de link (revisão Codex CAD-INICIO-AX-01: com role="listitem"
    # no <a>, a navegação assistiva por links perdia o destino); extra (ex.: hidden da busca) vai no contêiner. tag='li': item nativo da
    # lista ordenada do fluxo (sem role redundante)
    papel = '' if tag == 'li' else ' role="listitem"'
    return (f'<{tag} class="mod-item"{papel}{extra}><a class="mod-cartao" href="{h}"><span class="mod-ic" aria-hidden="true">{icon(ic, 22, "#1E7A4C")}</span>'
            f'<span>{E.esc(nome)}</span></a></{tag}>')

# volta ao ponto útil (revisão Codex CAD-INICIO-RETORNO-01): o cartão aberto fica guardado na sessão da aba; na volta por "‹ Módulo" (ou pelo
# Voltar do navegador) a tela de entrada devolve o foco a ele. A tela Cadastros também guarda o termo da busca (areas/cad_inicio.py).
JS_VOLTA = r'''
function modLe(k) { try { return sessionStorage.getItem(k) || ''; } catch (e) { return ''; } }
function modGrava(k, v) { try { if (v) sessionStorage.setItem(k, v); else sessionStorage.removeItem(k); } catch (e) {} }
function modVolta(self) { if (self.__modVolta) return; self.__modVolta = 1; const pg = String(location.pathname).split('/').pop(), k = 'safrion.mod_ult:' + pg;
  document.addEventListener('click', e => { const a = e.target && e.target.closest && e.target.closest('a.mod-cartao'); if (a) modGrava(k, a.getAttribute('href')); }, true);
  const u = modLe(k); if (!u) return; let n = 0;   // espera o cartão existir (condição, até 2 s), em vez de um tempo fixo
  const foca = () => { const a = [...document.querySelectorAll('a.mod-cartao')].find(x => x.getAttribute('href') === u && x.getClientRects().length);
    if (a) { a.focus(); return; } if (++n < 40) setTimeout(foca, 50); }; setTimeout(foca, 0); }
'''


def grade(itens, rotulo):
    return f'<div class="mod-grade" role="list" aria-label="{E.esc(rotulo)}">' + ''.join(cartao(*x) for x in itens) + '</div>'


# ---------- blocos por macro contexto: lado a lado (até 640 px, empilhados), título em cima, cartões alinhados ----------
# Coluna estreita (bloco < 230 px, ex.: 800 px de janela): o cartão põe o ícone sobre o nome, sem estourar "Beneficiamento" (container query).
CSS_FLUXO = ('<style>.mod-grade.mod-fluxo{display:grid!important;grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);'
             'gap:24px;align-items:start;padding:0;border:0}'
             '.mod-sec{display:flex;flex-direction:column;gap:10px;min-width:0}'
             '.mod-bloco-tit{margin:0;padding:0 4px;font-size:15px;font-weight:800;letter-spacing:-.01em;color:#15201A}'
             '.mod-bloco{list-style:none;margin:0;padding:12px;min-width:0;display:flex;flex-direction:column;gap:10px;border:1px solid #E4E9E5;'
             'border-radius:18px;background:#EEF1EE;container-type:inline-size}'
             '.mod-bloco>.mod-item{width:100%;box-sizing:border-box}'
             '@container (max-width:229px){.mod-bloco .mod-cartao{flex-direction:column;align-items:flex-start;gap:8px;padding:10px 12px}'
             '.mod-bloco .mod-cartao>span:last-child{max-width:100%;overflow-wrap:anywhere;hyphens:auto}}'
             '@media (max-width:900px){.mod-grade.mod-fluxo{gap:16px}.mod-bloco{padding:10px}}'
             '@media (max-width:640px),(max-height:560px){.mod-grade.mod-fluxo{grid-auto-flow:row;grid-template-columns:minmax(0,1fr);gap:20px}}</style>')


def fluxo(blocos):
    """um painel por macro contexto, com o título em cima, na ordem do processo; os cartões alinhados dentro do painel (sem setas)."""
    return ('<div class="mod-grade mod-fluxo">'
            + ''.join(f'<section class="mod-sec" aria-labelledby="mod-b{k}"><h2 id="mod-b{k}" class="mod-bloco-tit">{E.esc(tit)}</h2>'
                      '<ol class="mod-bloco" role="list">'   # role="list": a lista sem marcador continua lista no VoiceOver
                      + ''.join(cartao(h, nome, ic, '', tag='li') for (h, nome, ic) in b) + '</ol></section>' for k, (tit, b) in enumerate(blocos))
            + '</div>')


def blocos_do(nome, itens):
    """os cartões do módulo nos blocos de ui37.FLUXO37; confere que cada cartão aparece uma vez (sem perder tela ao mudar o menu)."""
    por = {x[0]: x for x in itens}
    bl = [(t, [por[h] for h in b if h in por]) for t, b in FLUXO37[nome]]
    usados = [x[0] for _, b in bl for x in b]
    assert sorted(usados) == sorted(por) and len(set(usados)) == len(usados), f'FLUXO37[{nome!r}] não cobre os cartões do módulo uma vez cada: {sorted(set(por) ^ set(usados))}'
    return [(t, b) for t, b in bl if b]


def _hub(fname, titulo, itens, blocos=None):
    E._reset_screen(fname); HEIGHTS37[fname] = 760
    E.EXTRAJS[0] = JS_VOLTA + 'function EXTRAVALS(self, v) { modVolta(self); }\n'
    corpo = CSS + (CSS_FLUXO + fluxo(blocos) if blocos else grade(itens, titulo))
    shell37(fname.replace('.dc.html', ''), titulo, corpo, fname=fname, status=None, primary_html=None, search=False)


def itens_do(nome):
    """cartões de um módulo, na ordem do menu: uma tela por cartão; a visão com nome próprio no CURTO37 (MA.dc.html#vis=…) tem o seu."""
    its, vistos = [], set()
    for _, ic, items in [m for m in MENU2 if m[0] == nome]:
        for l, h in items:
            k = h if h in CURTO37 else h.split('#')[0]
            if k in vistos: continue
            vistos.add(k); curto, ic2 = CURTO37[k]; its.append((h, curto, ic2))
    return its


def build():
    for nome, ic, items in MENU2:
        if nome in HUB37: its = itens_do(nome); _hub(HUB37[nome], nome, its, blocos_do(nome, its) if nome in FLUXO37 else None)
    _hub(OUTROS37[2], OUTROS37[0], [(h, n, i2) for n, h, i2 in OUTROS37[3]])
