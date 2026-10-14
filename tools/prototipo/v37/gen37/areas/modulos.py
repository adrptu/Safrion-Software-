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
- Fluxo (14/10/2026, proprietário: "faça um teste nesses sub menus como se fosse um fluxograma com setas de linhas curvas, separando em 3
  fases/blocos ... mas sem escrever isso ... Assim o usuario entende onde as coisas começam e terminam e a ordem correta do fluxo de
  processos"): o módulo com fluxo (ui37.FLUXO37, teste só no Agrícola) mostra um painel por bloco, sem título, com os cartões na ordem do
  processo (uma lista ordenada por bloco: a ordem do DOM e do Tab é a do fluxo). Setas curvas (Bezier cúbica) ligam cada cartão ao seguinte,
  inclusive do último de um bloco ao primeiro do bloco seguinte; são um SVG decorativo (aria-hidden, sem interceptar toques), redesenhado
  pelas posições reais dos cartões (carga, fontes e ResizeObserver). Computador: blocos lado a lado; até 640 px de largura (ou 560 px de
  altura, celular deitado): uma coluna, blocos empilhados. Os cartões alternam de lado dentro do bloco (a seta entre dois vizinhos faz um S);
  o último de um bloco com seguinte fica à direita, para a seta entre blocos não cruzar o cartão de cima, e, no último bloco, o primeiro fica
  à esquerda."""
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


# ---------- fluxo (14/10/2026): blocos lado a lado (até 640 px, empilhados) e setas curvas entre cartões consecutivos ----------
# Painel discreto (GRAYS/LINE do engine), sem título; cartão por cima das setas (z-index); seta verde-acinzentada #6F8C7B (3,2:1 sobre o painel).
# Coluna estreita (bloco < 230 px, ex.: 800 px de janela): o cartão põe o ícone sobre o nome, sem estourar "Beneficiamento" (container query).
# Uma coluna até 640 px de largura ou 560 px de altura (celular em pé ou deitado: o mesmo corte da casca, ui37).
CSS_FLUXO = ('<style>.mod-grade.mod-fluxo{display:grid!important;grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);'
             'gap:28px;align-items:stretch;position:relative;z-index:0;padding:0;border:0}'
             '.mod-setas{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:0}'
             '.mod-bloco{list-style:none;margin:0;padding:14px;min-width:0;display:flex;flex-direction:column;gap:36px;border:1px solid #E4E9E5;'
             'border-radius:18px;background:#EEF1EE;container-type:inline-size;--desl:clamp(12px,9%,40px)}'
             '.mod-bloco>.mod-item{width:calc(100% - var(--desl));box-sizing:border-box}.mod-bloco>.mod-item[data-lado=dir]{align-self:flex-end}'
             '.mod-fluxo .mod-cartao{position:relative;z-index:1}'
             '@container (max-width:229px){.mod-bloco .mod-cartao{flex-direction:column;align-items:flex-start;gap:8px;padding:10px 12px}'
             '.mod-bloco .mod-cartao>span:last-child{max-width:100%;overflow-wrap:anywhere;hyphens:auto}}'
             '@media (max-width:900px){.mod-grade.mod-fluxo{gap:18px}.mod-bloco{padding:10px}}'
             '@media (max-width:640px),(max-height:560px){.mod-grade.mod-fluxo{grid-auto-flow:row;grid-template-columns:minmax(0,1fr);gap:22px}.mod-bloco{padding:12px;gap:32px}}</style>')

# desenho das setas pelas posições reais: abaixo → S vertical (base do cartão ao topo do seguinte); na coluna seguinte → S de lado (borda
# direita à esquerda do seguinte). Uma fila por quadro (requestAnimationFrame); o ResizeObserver vê o contêiner e cada cartão.
JS_FLUXO = r'''
function modFluxo() { if (window.__modFluxo) { window.__modFluxo(); return; } let fila = 0, obs = null, alvo = null;
  const n = x => Math.round(x * 10) / 10, NS = 'http://www.w3.org/2000/svg';
  const desenha = () => { fila = 0; const f = document.querySelector('.mod-fluxo'), svg = f && f.querySelector('svg.mod-setas'); if (!svg) return;
    const cs = [...f.querySelectorAll('a.mod-cartao')].filter(a => a.getClientRects().length);
    if (alvo !== f) { alvo = f; if (obs) obs.disconnect(); if (window.ResizeObserver) { obs = new ResizeObserver(agenda); obs.observe(f); cs.forEach(a => obs.observe(a)); } }
    const o = f.getBoundingClientRect(), e = (o.width / (f.offsetWidth || o.width)) || 1, g = 3;
    const R = a => { const r = a.getBoundingClientRect(), l = (r.left - o.left) / e, t = (r.top - o.top) / e, w = r.width / e, h = r.height / e; return { l, t, r: l + w, b: t + h, x: l + w / 2, y: t + h / 2 }; };
    const ds = [];
    for (let i = 0; i + 1 < cs.length; i++) { const a = R(cs[i]), b = R(cs[i + 1]);
      if (b.t < a.b - 1 && b.l > a.r + 2 * g) { const x0 = a.r + g, x3 = b.l - g, k = x3 - x0;   // coluna seguinte: S de lado
        ds.push(`M${n(x0)} ${n(a.y)}C${n(x0 + k)} ${n(a.y)} ${n(x3 - k)} ${n(b.y)} ${n(x3)} ${n(b.y)}`); }
      else { const y0 = a.b + g, y3 = b.t - g, k = Math.max(6, (y3 - y0) * .75);   // abaixo: S vertical (pontas na vertical, meio inclinado)
        ds.push(`M${n(a.x)} ${n(y0)}C${n(a.x)} ${n(y0 + k)} ${n(b.x)} ${n(y3 - k)} ${n(b.x)} ${n(y3)}`); } }
    const ant = svg.getAttribute('data-ds'), nova = ds.join('|'); if (ant === nova) return; svg.setAttribute('data-ds', nova);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const df = document.createElementNS(NS, 'defs'), mk = document.createElementNS(NS, 'marker'), pt = document.createElementNS(NS, 'path');
    [['id', 'mod-seta-ponta'], ['viewBox', '0 0 10 10'], ['refX', '9'], ['refY', '5'], ['markerWidth', '8'], ['markerHeight', '8'], ['markerUnits', 'userSpaceOnUse'], ['orient', 'auto']].forEach(([k, v]) => mk.setAttribute(k, v));
    pt.setAttribute('d', 'M0 1L10 5L0 9z'); pt.setAttribute('fill', '#6F8C7B'); mk.appendChild(pt); df.appendChild(mk); svg.appendChild(df);
    ds.forEach((d, i) => { const p = document.createElementNS(NS, 'path'); p.setAttribute('class', 'mod-seta'); p.setAttribute('d', d); p.setAttribute('fill', 'none');
      p.setAttribute('stroke', '#6F8C7B'); p.setAttribute('stroke-width', '1.5'); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('marker-end', 'url(#mod-seta-ponta)');
      p.setAttribute('data-de', cs[i].getAttribute('href')); p.setAttribute('data-para', cs[i + 1].getAttribute('href')); svg.appendChild(p); }); };
  const agenda = () => { if (!fila) fila = requestAnimationFrame(desenha); };
  window.__modFluxo = agenda; addEventListener('resize', agenda); addEventListener('load', agenda);
  try { document.fonts && document.fonts.ready && document.fonts.ready.then(agenda); } catch (e) {} agenda(); }
'''


def fluxo(blocos):
    """um painel por bloco (lista ordenada), na ordem do processo. Lado do cartão: alterna dentro do bloco; o último de um bloco com seguinte
    fica à direita (a seta sai pela borda direita) e, no último bloco, o primeiro fica à esquerda (a seta chega pela borda esquerda)."""
    def lado(k, i, m): return (m - 1 - i) % 2 == 0 if k < len(blocos) - 1 else i % 2 == 1
    return ('<div class="mod-grade mod-fluxo"><svg class="mod-setas" aria-hidden="true" focusable="false"></svg>'
            + ''.join('<ol class="mod-bloco" role="list">'   # role="list": a lista sem marcador continua lista no VoiceOver
                      + ''.join(cartao(h, nome, ic, ' data-lado="dir"' if lado(k, i, len(b)) else '', tag='li') for i, (h, nome, ic) in enumerate(b))
                      + '</ol>' for k, b in enumerate(blocos))
            + '</div>')


def blocos_do(nome, itens):
    """os cartões do módulo nos blocos de ui37.FLUXO37; confere que cada cartão aparece uma vez (sem perder tela ao mudar o menu)."""
    por = {x[0]: x for x in itens}
    bl = [[por[h] for h in b if h in por] for b in FLUXO37[nome]]
    usados = [x[0] for b in bl for x in b]
    assert sorted(usados) == sorted(por) and len(set(usados)) == len(usados), f'FLUXO37[{nome!r}] não cobre os cartões do módulo uma vez cada: {sorted(set(por) ^ set(usados))}'
    return [b for b in bl if b]


def _hub(fname, titulo, itens, blocos=None):
    E._reset_screen(fname); HEIGHTS37[fname] = 760
    E.EXTRAJS[0] = JS_VOLTA + (JS_FLUXO if blocos else '') + 'function EXTRAVALS(self, v) { modVolta(self);' + (' modFluxo();' if blocos else '') + ' }\n'
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
