# -*- coding: utf-8 -*-
"""Telas de entrada dos módulos (13/10/2026, proprietário: "tire todos submenus de todos os módulos e coloque na tela como fizemos com
cadastros ... reduza texto ao mínimo essencial de cada submenu ... sempre com opção de voltar rápido e fácil. use sempre ícones mais
intuitivos para eliminar necessidade de textos longos. Mais minimalista e essencialista").
- Um cartão por tela do módulo, só com o ícone e o nome curto (fonte única: ui37.CURTO37); um toque abre a tela.
- Cada tela do módulo volta por "‹ Módulo" ao lado do título (ui37.VOLTA37).
- A barra lateral fica recolhida, um ícone por módulo com dica (ui37.navbar). Mapa e Manutenção (uma tela com visões) abrem direto.
- "Outros acessos" reúne as pontas que antes só o índice abria (app de campo, portal do parceiro, onboarding e backoffice).
O cartão (cartao) e o seu CSS também servem à tela Cadastros (areas/cad_inicio.py). Nada é gravado aqui."""
import engine as E
from engine import icon
from ui37 import shell37, HEIGHTS37, MENU2, HUB37, CURTO37, OUTROS37

CSS=('<style>.mod-grade{display:grid!important;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;align-content:start}'   # !important: a coluna do main põe display:flex nos filhos diretos
     '.mod-grade [hidden]{display:none!important}'   # o display:flex do cartão venceria o [hidden] padrão (busca da tela Cadastros)
     '.mod-item{display:flex;min-width:0}.mod-item>.mod-cartao{flex:1 1 auto;min-width:0}'   # item da lista no contêiner; o <a> segue link (revisão Codex CAD-INICIO-AX-01)
     '.mod-cartao{display:flex;align-items:center;gap:12px;padding:12px 16px;min-height:64px;box-sizing:border-box;border:1px solid #E4E9E5;border-radius:14px;'
     'background:#FFFFFF;text-decoration:none;color:#15201A;font-size:15px;font-weight:700;line-height:1.25}'
     '.mod-cartao:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}'
     '@media (hover:hover){.mod-cartao:hover{border-color:#1E7A4C;background:#F2F8F4}}'
     '.mod-ic{flex:0 0 auto;width:40px;height:40px;border-radius:12px;background:#E4F3E9;color:#1E7A4C;display:flex;align-items:center;justify-content:center}'
     '@media (max-width:600px){.mod-grade{grid-template-columns:1fr}}</style>')


def cartao(h, nome, ic, extra=''):
    # o papel de item de lista fica no contêiner: o <a href> mantém o papel nativo de link (revisão Codex CAD-INICIO-AX-01: com role="listitem"
    # no <a>, a navegação assistiva por links perdia o destino); extra (ex.: hidden da busca) vai no contêiner
    return (f'<div class="mod-item" role="listitem"{extra}><a class="mod-cartao" href="{h}"><span class="mod-ic" aria-hidden="true">{icon(ic, 22, "#1E7A4C")}</span>'
            f'<span>{E.esc(nome)}</span></a></div>')

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


def _hub(fname, titulo, itens):
    E._reset_screen(fname); HEIGHTS37[fname] = 760
    E.EXTRAJS[0] = JS_VOLTA + 'function EXTRAVALS(self, v) { modVolta(self); }\n'
    shell37(fname.replace('.dc.html', ''), titulo, CSS + grade(itens, titulo), fname=fname, status=None, primary_html=None, search=False)


def itens_do(nome):
    """cartões de um módulo: uma tela por cartão (visões da mesma tela contam uma vez), na ordem do menu."""
    its, vistos = [], set()
    for _, ic, items in [m for m in MENU2 if m[0] == nome]:
        for l, h in items:
            h0 = h.split('#')[0]
            if h0 in vistos: continue
            vistos.add(h0); curto, ic2 = CURTO37[h0]; its.append((h, curto, ic2))
    return its


def build():
    for nome, ic, items in MENU2:
        if nome in HUB37: _hub(HUB37[nome], nome, itens_do(nome))
    _hub(OUTROS37[2], OUTROS37[0], [(h, n, i2) for n, h, i2 in OUTROS37[3]])
