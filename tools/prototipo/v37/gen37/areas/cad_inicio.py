# -*- coding: utf-8 -*-
"""Cadastros · tela inicial (pedido do proprietário, 13/10/2026: "tire os submenus de cadastro e coloque tudo na tela para o usuário
clicar e cair na tela de cadastro de interesse, com componentes visuais organizados e intuitivos. e botão de voltar fácil para todos
cadastros").
- O grupo Cadastros do menu vira um link para esta tela (ui37.MENU2); dentro de qualquer cadastro o menu continua marcando Cadastros.
- Cartões em 4 grupos, cada um com o ícone, o nome, para que serve e o que tem dentro (as abas reais da tela). Um toque abre o cadastro.
- A busca filtra pelos termos de cada cadastro ("talhão", "trator", "fornecedor", "embalagem"…); sem resultado, diz o que buscar.
- Todo cadastro (CD-01 … CD-07) ganha o botão "‹ Cadastros" ao lado do título (ui37.VOLTA37).
Nada é gravado aqui."""
import json
import engine as E
from engine import EXTRAJS, icon, INK, MUTED, LINE, SURF, ACC
from ui37 import shell37, HEIGHTS37

H = lambda s: '{{' + s + '}}'
# (código, nome, ícone, para que serve, o que tem dentro, termos de busca)
GRUPOS = [
    ('Propriedade e produção', [
        ('CD-01', 'Fazendas, áreas e talhões', 'map', 'Onde a fazenda produz: talhões com área e mapa, documentos da fazenda, áreas ambientais e outorgas de água.',
         'Talhões · Fazendas · Ambiental · Água', 'fazenda área talhão parcela gleba mapa geometria matrícula car ambiental reserva app água outorga poço'),
        ('CD-02', 'Culturas, cultivares e operações', 'leaf', 'O que se planta e como: culturas, cultivares e as operações de campo usadas nos planos.',
         'Culturas · Operações', 'cultura cultivar variedade soja milho café mamão feijão ciclo operação atividade rendimento'),
    ]),
    ('Recursos', [
        ('CD-03', 'Máquinas, instalações e setores', 'truck', 'Com o que se trabalha: tratores, implementos, colhedoras, pivôs, bombas, silos e os conjuntos máquina + implemento.',
         'Máquinas · Conjuntos', 'máquina trator implemento colhedora pulverizador plantadeira pivô bomba silo armazém instalação setor conjunto vazão potência'),
        ('CD-04', 'Pessoas e equipes', 'users', 'Quem trabalha: pessoas, equipes, habilidades, habilitações com validade e o calendário de cada uma.',
         'Pessoas · Equipes', 'pessoa equipe operador funcionário colaborador habilidade habilitação nr validade calendário jornada líder'),
    ]),
    ('Suprimentos e comercial', [
        ('CD-05', 'Parceiros e fornecedores', 'cart', 'Com quem a fazenda compra e vende: fornecedores, clientes, transportadoras e prestadores, e o que cada um atende.',
         'Parceiros · Cobertura', 'parceiro fornecedor cliente transportadora prestador cnpj cpf contato email cobertura homologado'),
        ('CD-06', 'Produtos, unidades e locais', 'box', 'O que entra e sai do estoque: insumos e produtos com unidade, embalagem e preço de referência, e os locais de estoque.',
         'Itens · Locais', 'produto insumo defensivo herbicida fungicida fertilizante adubo semente diesel unidade embalagem preço local depósito almoxarifado estoque'),
    ]),
    ('Gestão', [
        ('CD-07', 'Estrutura gerencial', 'grid', 'Como o resultado é lido: centros de custo e de resultado, naturezas de custo e projetos, com vigência.',
         'Dimensões e códigos', 'estrutura gerencial centro custo resultado natureza projeto dimensão código vigência rateio'),
    ]),
]
CARTOES = [dict(id=c, g=g, t=t, p=p, d=d, k=(t + ' ' + p + ' ' + d + ' ' + k).lower(), h=c + '.dc.html', ic=ic)
           for g, cs in GRUPOS for c, t, ic, p, d, k in cs]

CSS = ('<style>'
       '.cdi{display:flex;flex-direction:column;gap:22px}'
       '.cdi [hidden]{display:none!important}'   # o display:flex do cartão venceria o [hidden] padrão e a busca não esconderia nada
       '.cdi-busca{flex:1 1 360px;display:flex;align-items:center;gap:8px;max-width:520px;padding:0 14px;min-height:44px;border:1px solid #E4E9E5;border-radius:999px;background:#FFFFFF}'
       '.cdi-busca input{flex:1;min-width:0;border:0;outline:0;font:inherit;font-size:14px;background:transparent;color:#15201A}'
       '.cdi-busca:focus-within{border-color:#1E7A4C;box-shadow:0 0 0 3px #E4F3E9}'
       '.cdi-grupo{display:flex;flex-direction:column;gap:10px}'
       '.cdi-gt{margin:0;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#65736A;font-weight:800}'
       '.cdi-grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}'
       '.cdi-cartao{display:flex;gap:14px;align-items:flex-start;padding:16px 18px;border:1px solid #E4E9E5;border-radius:16px;background:#FFFFFF;text-decoration:none;color:#15201A;min-height:44px;box-sizing:border-box}'
       '.cdi-cartao:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}'
       '@media (hover:hover){.cdi-cartao:hover{border-color:#1E7A4C;background:#F2F8F4}}'
       '.cdi-ic{flex:0 0 auto;width:40px;height:40px;border-radius:12px;background:#E4F3E9;color:#1E7A4C;display:flex;align-items:center;justify-content:center}'
       '.cdi-tx{display:flex;flex-direction:column;gap:4px;min-width:0}'
       '.cdi-t{font-size:15px;font-weight:800;line-height:1.25}'
       '.cdi-p{font-size:13px;color:#4B5A51;line-height:1.4}'
       '.cdi-d{font-size:12px;color:#65736A;font-weight:700}'
       '.cdi-ir{margin-left:auto;align-self:center;color:#1E7A4C;font-size:18px;font-weight:800}'
       '@media (max-width:600px){.cdi-grade{grid-template-columns:1fr}.cdi-busca{max-width:none}}'
       '</style>')

JS = r'''
const CDI_CARTOES = __CARTOES__;
function cdiNorm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
function EXTRAVALS(self, v) { const q = cdiNorm(self.state.cdi_q || '').trim(); const ws = q ? q.split(/\s+/) : []; let n = 0; const gs = {};
  CDI_CARTOES.forEach(c => { const ok = ws.every(w => cdiNorm(c.k).indexOf(w) >= 0); v['cdi_h_' + c.id] = !ok; if (ok) { n++; gs[c.gi] = 1; } });
  CDI_CARTOES.forEach(c => { v['cdi_hg_' + c.gi] = !gs[c.gi]; });
  v.cdi_vazio = n === 0; v.cdi_q = self.state.cdi_q || ''; v.cdi_n = q ? n + ' de ' + CDI_CARTOES.length + ' cadastros' : CDI_CARTOES.length + ' cadastros';
  v.cdi_set = e => self.setState({ cdi_q: e && e.target ? e.target.value : '' });
  v.cdi_key = e => { if (e && e.key === 'Escape') { e.preventDefault(); self.setState({ cdi_q: '' }); } }; }
'''


def _cartao(c):
    k = c['id'].replace('-', '')
    return (f'<a class="cdi-cartao" role="listitem" href="{c["h"]}" hidden="{H("cdi_h_" + k)}">'
            f'<span class="cdi-ic" aria-hidden="true">{icon(c["ic"], 20, "#1E7A4C")}</span>'
            f'<span class="cdi-tx"><span class="cdi-t">{E.esc(c["t"])}</span><span class="cdi-p">{E.esc(c["p"])}</span>'
            f'<span class="cdi-d">Tem: {E.esc(c["d"])}</span></span><span class="cdi-ir" aria-hidden="true">›</span></a>')


def build():
    fname = 'CD.dc.html'; E._reset_screen(fname)
    grupos = ''.join(f'<section class="cdi-grupo" aria-label="{E.esc(g)}" hidden="{H("cdi_hg_" + str(gi))}"><h2 class="cdi-gt">{E.esc(g)}</h2>'
                     f'<div class="cdi-grade" role="list">' + ''.join(_cartao(c) for c in CARTOES if c['g'] == g) + '</div></section>'
                     for gi, (g, _) in enumerate(GRUPOS))
    corpo = (CSS + '<div class="cdi">'
             + f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><label class="cdi-busca">{icon("lista", 16, MUTED)}'
               f'<input type="search" aria-label="Buscar cadastro" placeholder="Buscar: talhão, trator, fornecedor, embalagem…" value="{H("cdi_q")}" onChange="{H("cdi_set")}" onKeyDown="{H("cdi_key")}"></label>'
               f'<span role="status" style="font-size: 13px; color: {MUTED}; font-weight: 600;">{H("cdi_n")}</span></div>'
             + f'<sc-if value="{H("cdi_vazio")}" hint-placeholder-val="{H("false")}"><p role="status" style="margin: 0; font-size: 14px; color: {INK};">Nenhum cadastro com esse termo. '
               f'Tente o nome do que procura (talhão, trator, pessoa, fornecedor, produto, centro de custo) ou apague a busca.</p></sc-if>'
             + grupos + '</div>')
    EXTRAJS[0] = JS.replace('__CARTOES__', json.dumps([dict(id=c['id'].replace('-', ''), gi=[g for g, _ in GRUPOS].index(c['g']), k=c['k']) for c in CARTOES], ensure_ascii=False))
    HEIGHTS37[fname] = 900
    shell37('CD', 'Cadastros', corpo, fname=fname, status=None, primary_html=None, search=False,
            subtitle='Escolha o cadastro: um toque abre a tela. Em qualquer cadastro, "‹ Cadastros" traz de volta para cá.')
