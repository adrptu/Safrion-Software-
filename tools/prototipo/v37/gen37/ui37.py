# -*- coding: utf-8 -*-
"""Shell v3.7: menu de 13 áreas do cap. 4.1, contexto do cap. 4.2, faixa de continuidade e rodapé de demonstração."""
import json, os
from engine import (INK,MUTED,LINE,BG,SURF,ACC,ACCS,SH,SIDE,SIDE_TX,SIDE_MUTED,DISP,FONT,YEL,YELS,RED,REDS,GRAY,GRAYS,
                    icon,esc,chip,btn,act,chev,engine,extra_html,wid,reg,wget,_reset_screen,FIRST_TBL,CHIP_ON,CHIP_OFF,HL)
import engine as E

V37=os.path.dirname(os.path.abspath(__file__))
CAT=json.load(open(os.path.join(V37,'..','catalogo.json')))
MENU=json.load(open(os.path.join(V37,'..','menu.json')))
MAPA=json.load(open(os.path.join(V37,'..','menu_map.json')))

AREA_ICON={'Início':'Início','Agronomia':'Agronomia','Planejamento':'calendar','Campo':'Campo','Irrigação':'Irrigação',
 'Máquinas e manutenção':'wrench','Colheita e pós-colheita':'Colheita','Suprimentos':'cart','Comercial':'Vendas',
 'Logística':'truck','Gestão e resultados':'trend','Cadastros':'layers','Configurações':'grid'}
PREF_AREA={'IN':'Início','AG':'Agronomia','PL':'Planejamento','CA':'Campo','IR':'Irrigação','MA':'Máquinas e manutenção',
 'CO':'Colheita e pós-colheita','SU':'Suprimentos','VE':'Comercial','LO':'Logística','GE':'Gestão e resultados',
 'CD':'Cadastros','CF':'Configurações','PT':'Portal do parceiro','BO':'Backoffice da plataforma','ON':'Onboarding','MB':'App móvel'}
EXTERNOS={'PT':('Portal do parceiro','tag'),'BO':('Backoffice da plataforma','card'),'ON':('Onboarding','users')}

def ffile(fid): return f'{fid}.dc.html'
def area_of(fid): return PREF_AREA.get(fid[:2])

HEIGHTS37={}
_OVR_P=os.path.join(V37,'heights_override.json')
H_OVR=json.load(open(_OVR_P)) if os.path.exists(_OVR_P) else {}  # alturas medidas pelo qa37 (overflow real)
def _h(fname,H): return H_OVR.get(fname) or HEIGHTS37.get(fname,H)
PRIMHREF={}   # fid -> destino do botão primário
PARENT37={}   # fname -> fname de volta
# botão de voltar com rótulo, ao lado do título (13/10/2026, proprietário: "botão de voltar fácil para todos cadastros"): fname -> (rótulo, destino)
VOLTA37={f'CD-0{i}.dc.html':('Cadastros','CD.dc.html') for i in range(1,9)}   # CD-08 Operações e rendimentos (13/10)

# Menu vigente por decisão do proprietário (25/09/2026): Mapa · Cadastros · Agrícola · Suprimentos.
# 01/10/2026: Consulta Agrofit (antes de Planos), Pragas e doenças (MIP/MID) e Irrigação voltam dentro de Agrícola; Manutenção volta logo abaixo de Agrícola (pedidos do proprietário).
# 02/10/2026: Manutenção ganha "Planos de manutenção" (PM) como 1º item; MA-03 vira "Vencimentos e paradas" (sem dois itens com o mesmo nome).
# 05/10/2026 (pedido "PCM /manutenção também tem telas e menus demais... faça o melhor num só"; PCM simplificado v2, D-01/D-02): o grupo Manutenção
#   passa a 1 item, "Manutenção" → MA.dc.html (link direto), com as visões Sem ordem · Ordens · Ativos · Planos; a posição de 01/10 fica.
# 06/10/2026: grupo Produção logo depois de Agrícola (colheita de ponta a ponta, docs/colheita · D-01): no máximo 3 itens.
# 09/10/2026 (SOLO-01, D-01): Análises de solo (AG-02) em Agrícola, entre Planos agronômicos e Planejar safra (o laudo vira sugestão nas doses do plano).
# 06/10/2026: grupo Comercial logo depois de Produção (comercial e logística, docs/comercial · D-C01): planejamento, execução e controle, no máximo 3 itens.
# Os demais módulos ficam ocultos do menu, preservados no canvas (página "Módulos ocultos").
# v55 (10/10/2026): o Beneficiamento (BEN.dc.html) sai da navegação até a rodada 3 do BEN: os defeitos S2 de saldo e reserva de caixas
#   estão em correção em outra frente e a tela não estreia no artefato. O código fica na branch, sem perda; só deixa de ser alcançável:
#   sem aba irmã em Cargas (CARGA vira tela única), sem link de tela visível (Cargas e Estoque de produto mostram a ordem em texto) e,
#   no canvas, na página "Módulos ocultos". Chave única, lida por ui37, areas/producao.py e build.py: reativar é BEN_PUBLICADO=True.
# 13/10/2026 (proprietário: "coloque beneficiamento dentro de menu produção. Packing house, industria, etc" e "coloque tudo de produção, dentro
#   de Agrícola"): rodada 3 do BEN e os 3 S2 da revisão (A1, A2, A8) corrigidos com teste de regressão (BEN-D33 a BEN-D39): o Beneficiamento
#   volta à navegação como cartão próprio de Agrícola, logo depois de Recebimento; Cargas aponta a ordem do lote em processo (atalho e linha),
#   sem a faixa de telas (seria um 2º caminho para o mesmo cartão).
BEN_PUBLICADO=True
MENU2=[('Mapa','map',[('Mapa','IN-04.dc.html')]),
 ('Cadastros','pasta',[('Cadastros','CD.dc.html')]),   # 13/10/2026 (proprietário): sem submenus; a tela CD mostra os 7 cadastros em cartões e cada um volta por "‹ Cadastros"
 ('Agrícola','leaf',[('Painel','PAGR.dc.html'),('Consulta Agrofit','AG-07.dc.html'),('Planos agronômicos','PA.dc.html'),('Análises de solo','AG-02.dc.html'),('Planejar safra','SAF.dc.html'),('Orçamento e previsões','GE-02.dc.html'),('Ordem de Serviço','OS.dc.html'),('Pragas e doenças (MIP/MID)','AG-01.dc.html'),('Irrigação','IR-01.dc.html'),('Previsão e colheita','COLH.dc.html'),('Recebimento','CARGA.dc.html')]+([('Beneficiamento','BEN.dc.html')] if BEN_PUBLICADO else [])+[('Estoque de produto','PROD.dc.html'),('Custos e fechamento','GE-03.dc.html')]),   # 13/10/2026 (proprietário: "coloque orçamento e custos dentro do menu agrícola"; "coloque o submenu colheita dentro de agrícola"; "coloque tudo de produção, dentro de Agrícola"): o ciclo da lavoura até o produto em estoque
 ('Manutenção','wrench',[('Painel','PMAN.dc.html'),('Pendências sem ordem','MA.dc.html#vis=semordem'),('Ordens de manutenção','MA.dc.html#vis=ordens'),('Ativos e disponibilidade','MA.dc.html#vis=ativos'),('Planos preventivos','MA.dc.html#vis=planos')]),   # 13/10/2026 (pedido do proprietário: subitens de novo, enxutos): um subitem por visão da tela única, sem tela nova
 ('Suprimentos','cart',[('Painel','PSUP.dc.html'),('Compra de insumos','CMP.dc.html'),('Estoque','EST.dc.html'),('Inteligência de compras','IC.dc.html')]),   # INTEL-01 (13/10)
 ('Comercial','Vendas',[('Painel','PCOM.dc.html'),('Contratos e pedidos','VEN.dc.html'),('Expedição e entregas','EXPED.dc.html'),('Inteligência de vendas','IV.dc.html')]),   # INTEL-01 (13/10): inteligência comercial de vendas
 ('Crédito','cash',[('Solicitações e contratos','GE-08.dc.html#vis=contratos'),('Liberações e garantias','GE-08.dc.html#vis=liberacoes'),('Dossiê e consentimento','GE-08.dc.html#vis=dossie')]),   # 14/10/2026 (proprietário: "crie o menu de crédito"; depois "coloque os submenus de crédito como os demais"): a GE-08 (PRD; DEMO-10) abre pela tela de entrada do Crédito, um cartão por visão (como a Manutenção); sem visão no endereço, a GE-08 mostra tudo (links de outras telas)
 ('Configurações','engrenagem',[('Usuários e alçadas','CF-01.dc.html'),('Auditoria','CF-04.dc.html'),('Integrações','CF-03.dc.html'),('Assinatura e cobrança','CF-05.dc.html')])]   # 06/10/2026 (PLAT-01): grupo por último; CONF-01 (CONF-D01/D02): Usuários e alçadas · Auditoria · Integrações · Assinatura e cobrança, cada item entra no passo que entrega a tela
# 13/10/2026 (proprietário: "troque a posição do menu comercial com suprimentos. e manutenção logo abaixo de agrícola"): Agrícola ·
#   Manutenção · Suprimentos · Comercial.
# 13/10/2026 (proprietário: "tire todos submenus de todos os módulos e coloque na tela como fizemos com cadastros e deixe a barra lateral dos
# menus somente recolhido com os ícones e tooltip sem opção de expandir. Mas reduza texto ao mínimo essencial de cada submenu ... sempre com
# opção de voltar rápido e fácil. use sempre ícones mais intuitivos"): cada módulo com mais de uma tela abre a sua tela de entrada (cartões
# com ícone e nome curto, areas/modulos.py); o Mapa abre direto. Cada tela do módulo volta por "‹ Módulo".
# 13/10/2026 (proprietário: "o menu de manutenção está sem os submenus na tela igual os demais"): a Manutenção também abre a sua tela de
# entrada, um cartão por visão da tela única MA (Sem ordem · Ordens · Ativos · Planos); a chave do CURTO37 com #vis= vale para o cartão.
HUB37={'Agrícola':'MOD-AGR.dc.html','Comercial':'MOD-COM.dc.html','Suprimentos':'MOD-SUP.dc.html','Configurações':'MOD-CFG.dc.html','Manutenção':'MOD-MAN.dc.html','Crédito':'MOD-CRE.dc.html'}
# 14/10/2026 (proprietário: "faça um teste nesses sub menus como se fosse um fluxograma com setas de linhas curvas, separando em 3 fases/blocos
#   (input, processamento, output, mas sem escrever isso, apenas para o modo de organizar o fluxo). Assim o usuario entende onde as coisas
#   começam e terminam e a ordem correta do fluxo de processos"): a tela de entrada do módulo com fluxo mostra os cartões em blocos, na ordem
#   do processo, ligados por setas curvas (areas/modulos.py), sem título de bloco. Teste só no Agrícola; os demais módulos seguem em grade.
#   Cada cartão do módulo aparece uma vez (o build confere); um href fora do menu (BEN_PUBLICADO=False) fica de fora.
FLUXO37={'Agrícola':[['AG-07.dc.html','AG-02.dc.html','PA.dc.html','SAF.dc.html','GE-02.dc.html'],   # planejar
                     ['AG-01.dc.html','OS.dc.html','IR-01.dc.html','COLH.dc.html'],                   # executar
                     ['CARGA.dc.html','BEN.dc.html','PROD.dc.html','GE-03.dc.html','PAGR.dc.html']]}  # resultado
CURTO37={'PAGR.dc.html':('Painel','grafico'),'PMAN.dc.html':('Painel','grafico'),'PSUP.dc.html':('Painel','grafico'),'AG-07.dc.html':('Agrofit','livro'),'PA.dc.html':('Planos agronômicos','prancheta'),'AG-02.dc.html':('Análises de solo','frasco'),
 'SAF.dc.html':('Planejar safra','calendar'),'OS.dc.html':('Ordens de serviço','prancheta_ok'),'AG-01.dc.html':('Pragas e doenças','inseto'),'IR-01.dc.html':('Irrigação','drop'),
 'GE-02.dc.html':('Orçamento','cash'),'GE-03.dc.html':('Custos','calc'),
 'COLH.dc.html':('Colheita','Colheita'),'CARGA.dc.html':('Recebimento','scale'),'BEN.dc.html':('Beneficiamento','fabrica'),'PROD.dc.html':('Estoque de produto','armazem'),
 'VEN.dc.html':('Contratos e pedidos','doc'),'EXPED.dc.html':('Expedição','truck'),'PCOM.dc.html':('Painel','grafico'),'IV.dc.html':('Inteligência','trend'),
 'MA.dc.html#vis=semordem':('Sem ordem','clock'),'MA.dc.html#vis=ordens':('Ordens','wrench'),'MA.dc.html#vis=ativos':('Ativos','truck'),'MA.dc.html#vis=planos':('Planos','calendar'),
 'GE-08.dc.html#vis=contratos':('Contratos','doc'),'GE-08.dc.html#vis=liberacoes':('Liberações','cash'),'GE-08.dc.html#vis=dossie':('Dossiê','pasta'),
 'CMP.dc.html':('Compras','cart'),'EST.dc.html':('Estoque','box'),'IC.dc.html':('Inteligência','trend'),
 'CF-01.dc.html':('Usuários e alçadas','users'),'CF-04.dc.html':('Auditoria','historico'),'CF-03.dc.html':('Integrações','tomada'),'CF-05.dc.html':('Assinatura','card')}
# outras pontas do protótipo (antes só no índice, que saiu em 13/10: o artefato abre direto no Mapa)
OUTROS37=('Outros acessos','grid','MOD-OUT.dc.html',[('App de campo','MB-01.dc.html','celular'),('Portal do parceiro','PT-01.dc.html','users'),
                                                    ('Onboarding','ON-01.dc.html','check'),('Backoffice','BO-02.dc.html','escudo')])
VOLTA37.update({_hv.split('#')[0]:(_nv,HUB37[_nv]) for _nv,_iv,_itv in MENU2 if _nv in HUB37 for _lv,_hv in _itv})
INICIO37='IN-04.dc.html'   # o protótipo começa no Mapa (1º item do menu)
MENU_OF={'CA-01det.dc.html':'OS.dc.html','CA-02.dc.html':'OS.dc.html','CA-01x-os0420.dc.html':'OS.dc.html',
 'IR-02.dc.html':'IR-01.dc.html','IR-03.dc.html':'IR-01.dc.html','IR-03det.dc.html':'IR-01.dc.html','IR-04.dc.html':'IR-01.dc.html'}  # detalhes e telas irmãs que pertencem a um item do menu (o BEN é item próprio de Agrícola desde 13/10)
def menu_item(fname):
    f=MENU_OF.get(fname,fname)
    for i,(nome,ic,items) in enumerate(MENU2):
        if HUB37.get(nome)==f: return i,f   # tela de entrada do módulo
    for i,(nome,ic,items) in enumerate(MENU2):
        for lab,h in items:
            h=h.split('#')[0]   # subitem que abre uma visão da mesma tela (Manutenção: MA.dc.html#vis=…) pertence à tela
            if h==f or (f.startswith(h.replace('.dc.html','')) and f!=h and h not in ('IN-04.dc.html',) and f[:len(h)-8]==h[:-8]): return i,h
    return None,None
def oculto(fname):
    return menu_item(fname)[0] is None and fname not in ('Main.dc.html',OUTROS37[2]) and fname not in {h for _,h,_ in OUTROS37[3]}   # pontas de Outros acessos não são ocultas
def subnav_st(cur):
    """estilo do subitem do menu (ativo ou não); a Manutenção usa os dois no navegador para destacar a visão aberta."""
    return ('display: block; margin-left: 30px; padding: 5px 10px; border-radius: 8px; font-size: 12.8px; text-decoration: none; '
            + (f'background: {ACC}; color: #fff; font-weight: 700;' if cur else f'color: {SIDE_MUTED}; font-weight: 500;'))
def navbar(fid,fname=None):
    """Barra lateral sempre recolhida (13/10/2026): um ícone por módulo, com o nome na dica (title → g2dica) e no nome acessível; o módulo
    com mais de uma tela abre a tela de entrada (HUB37). Sem submenus e sem expandir. Por último, "Outros acessos" (app, portal, backoffice)."""
    fname=fname or ffile(fid)
    act_i,_=menu_item(fname)
    def item(nome,ic,h,on):
        st=('display: flex; align-items: center; justify-content: center; gap: 10px; padding: 8px 12px; border-radius: 10px; min-height: 44px; text-decoration: none; '
            + (f'background: {ACC}; color: #fff;' if on else f'color: {SIDE_TX};'))
        return (f'<a href="{h}" title="{esc(nome)}" aria-label="{esc(nome)}"' + (' aria-current="page"' if on else '') + f' style="{st}">'
                f'{icon(ic,20,"#fff" if on else SIDE_TX)}<span class="ml-txt">{esc(nome)}</span></a>')
    out=[item(nome,ic,HUB37.get(nome) or items[0][1].split('#')[0],i==act_i) for i,(nome,ic,items) in enumerate(MENU2)]
    out.append(f'<span aria-hidden="true" style="height: 1px; margin: 6px 8px; background: rgba(255,255,255,.12);"></span>')
    out.append(item(OUTROS37[0],OUTROS37[1],OUTROS37[2],fname==OUTROS37[2]))
    return ''.join(out)

# ---------------- progresso do processo e telas do módulo (UX-ACAO-UNICA-20261003 · DS-31 v2 · DS-33 §74.5.7.1) ----------------
# Pedido do Adrianus (03/10/2026): no Planejar safra, clicar nas etapas, usar as setas e clicar em "Definir rendimentos" mudavam a
# etapa por três caminhos; "com tantas opções o usuário fica perdido". Esta decisão REVOGA as setas ‹ › e a lista de etapas
# navegável de 01/10 (QUALIDADE…/RESPONSIVIDADE): não há os dois padrões. Dois componentes, cada um com uma função:
# 1) indicador de progresso do processo guiado (SAF, CMP, PA, PM): lista ordenada que só informa atual/concluída/pendente/impedida,
#    com a palavra do estado para leitor de tela (cor nunca sozinha); sem clique, sem handler, sem hover de ação e sem parada de Tab.
#    Avanço e retorno ficam na área de ações ao fim do conteúdo (engine.area_acoes + g2acoes). No estreito: "Etapa i de n · Nome";
#    a lista completa abre sob demanda e continua só informando (tocar em qualquer lugar fecha).
# 2) telas irmãs de um módulo de trabalho paralelo (Estoque, Irrigação, Manutenção e módulos ocultos): é navegação (seções/telas,
#    em qualquer ordem), não progresso; rotulada como tal, sem número de etapa e sem setas, com a pendência de cada tela escrita.
#    É o único caminho entre as telas irmãs (as do menu também estão no menu lateral, que é o nível Menu do master-detail).
_ETP_LIM={3:520,4:640,5:740}
def _etp_lim(n): return _ETP_LIM.get(n,520 if n<3 else 900)
def _etp_abre(i,n,nome,secao=False):
    """Rótulo da faixa estreita + caixa que abre a lista completa (só aparece na faixa estreita); o fundo escurecido fecha ao toque.
    Progresso: "Etapa i de n · Nome". Telas do módulo: o nome da tela atual (não é etapa)."""
    if secao:
        t=esc(nome); aria=f'Tela atual: {esc(nome)} · mostrar todas as telas'; dica='Mostrar todas as telas'
    else:
        t=f'Etapa {i} de {n} · {esc(nome)}' if i else f'{n} etapas'; aria=f'{t} · mostrar todas as etapas'; dica='Mostrar todas as etapas'
    return (f'<input type="checkbox" id="etp-c{i}" class="etp-chk" aria-controls="etp-lista" aria-label="{aria}">'
            f'<label for="etp-c{i}" class="etp-atual" title="{dica}"><span style="flex-grow: 1; min-width: 0;">{t}</span><span class="etp-seta" aria-hidden="true">▾</span></label>'
            f'<label for="etp-c{i}" class="etp-fundo" aria-hidden="true"></label>')
def _etp_lista(abre,itens,tag='div',attrs=''):
    return (f'<div style="display: flex; align-items: center; gap: 6px;">{abre}'
            f'<{tag} id="etp-lista" class="etp-itens"{attrs} style="flex-grow: 1; min-width: 0; display: flex; align-items: stretch; gap: 4px; margin: 0; padding: 0; list-style: none;">{itens}</{tag}></div>')
_ETP_CX=f'position: sticky; top: 0; z-index: 30; background: {SURF}; border-bottom: 1px solid {LINE}; box-shadow: 0 6px 12px -10px rgba(21,32,26,.25); padding: 6px 24px;'
def _etp_progresso(n,corpo):
    # sem nav: indicador não é navegação (DS-31 v2); o nome acessível "Etapas do processo" fica na lista ordenada
    return f'<div class="etp etp-ind etp-l{_etp_lim(n)}" style="{_ETP_CX}">{corpo}</div>'
def _etp_telas(label,n,corpo):
    return f'<nav aria-label="{esc(label)}" class="etp etp-sec etp-l{_etp_lim(n)}" style="{_ETP_CX}">{corpo}</nav>'
_SEC_IT=('display: flex; flex-direction: column; justify-content: center; gap: 1px; padding: 6px 10px; border-radius: 10px; text-decoration: none; color: '+INK+'; '
         'font-family: inherit; font-size: 12.5px; line-height: 1.2; border: 0; cursor: pointer; text-align: left; min-width: 0; ')
def secoes_nav(itens,n,i,nome,label):
    """Telas irmãs de um módulo (links ou botões já montados): navegação sem número de etapa e sem setas."""
    return _etp_telas(label,n,_etp_lista(_etp_abre(i,n,nome,secao=True),itens))
def secao_item(t,cur,href=None,fn=None,why='',why_hole=None):
    """Um item da navegação de telas: atual em destaque tonal com traço inferior e aria-current; pendência da tela escrita."""
    st=_SEC_IT+(f'background: {ACCS}; box-shadow: inset 0 -2px 0 {ACC}; font-weight: 800;' if cur else 'background: transparent; font-weight: 600;')
    w=(f'<sc-if value="{{{{{why_hole}_has}}}}" hint-placeholder-val="{{{{false}}}}"><span style="font-size: 11px; font-weight: 700; color: {RED};">{{{{{why_hole}_why}}}}</span></sc-if>' if why_hole
       else (f'<span style="font-size: 11px; font-weight: 700; color: {RED};">{esc(why)}</span>' if why else ''))
    inner=f'<span>{esc(t)}</span>{w}'
    cur_at=' aria-current="page"' if cur else ''
    if fn: return f'<button type="button" onClick="{{{{{fn}}}}}"{cur_at} style="{st}">{inner}</button>'
    return f'<a href="{href or "#"}"{cur_at} style="{st}">{inner}</a>'

# Casca em tela estreita ou baixa (só CSS; em 1280 px ou mais de largura e mais de 560 px de altura nada muda, salvo a linha do
# título quebrar quando não cabe): título e comando principal nunca saem da tela; menu aberto passa por cima do conteúdo;
# conteúdo largo demais rola na horizontal em vez de ser cortado; a lista da tela nunca fica espremida.
_RAIZ='[data-root]>div>header'
# linha de título de bloco + ação: <section> dos módulos e section() do engine (DIV). Só linhas: CD-07 (.cadx-dados) é coluna e
# quebrar uma coluna a joga para o lado, onde a seção corta (revisão do item 3, achado alto)
_TIT=('main[data-scroll] section>div:first-child:not([class]):not([style*="column"])',
      'main[data-scroll] div[style*="border-radius: 16px"]>div:first-child[style*="column"]>div:first-child:not([style*="column"])')
_KPI='main[data-scroll] div[style="display: flex; gap: 14px;"]'   # fileira de indicadores do engine (kpis)
# lista única que estica até o fim da janela (G2_CSS e cadastros): em tela estreita ou baixa fica com a altura natural e a tela rola
_S1='main section:only-of-type'
_ESTICA=(f'{_S1}:has(.g2caixa,.rola)',f'{_S1}:has(.g2caixa,.rola)>div:last-child',
         f'{_S1}>div:last-child>:is(.g2caixa,.rola,div:has(>.g2caixa,>.rola))',f'{_S1}>div:last-child>div>:is(.g2caixa,.rola)',
         f'{_S1} .g2caixa>.g2rola','main .cadx','main .cadx-dados','main .cadx-dados .g2caixa','main .cadx-dados .g2rola',
         'main[data-scroll]>div:last-child')
# RESPONSIVIDADE (QUALIDADE-ARTEFATO-20261003): a casca acompanha largura E altura, sem identificar aparelho. Altura = janela visível
# (dvh: a barra do navegador do celular não corta o pé); áreas seguras (entalhe, barra de gestos) por env(); até 1023 px (celular,
# tablet em pé, zoom de 200 %) o menu aberto passa por cima do conteúdo com fundo que fecha ao toque (Esc também: g2lib), o
# conteúdo fica com a trilha de 68 px e o título quebra linha; com ponteiro grosso (toque) os itens do menu têm 44 px.
# O botão do menu e o menu sobreposto (absolutos) também descontam as áreas seguras: não ficam sob o entalhe nem sobre o logo.
_CSS_RESP=('[data-root]{height:100vh;height:100dvh;padding:env(safe-area-inset-top,0px) env(safe-area-inset-right,0px) env(safe-area-inset-bottom,0px) env(safe-area-inset-left,0px)}'
    '.ml-fundo{display:none}'
    'main[data-scroll]{scroll-padding-block:8px}'   # o foco levado à vista pela rolagem fica com o contorno inteiro (não rente à borda)
    'main[data-scroll]>*{flex-shrink:0!important}'   # cortes visuais (13/10): na coluna flex que rola, o bloco não encolhe para a janela; senão o conteúdo transborda da caixa e a barra de ações (logo depois dela) fica no meio da tela com a lista correndo por baixo
    '@media (max-width: 1023px){'
    '.menu-lat:not(.rec){position:absolute;top:env(safe-area-inset-top,0px);bottom:env(safe-area-inset-bottom,0px);left:env(safe-area-inset-left,0px);z-index:35;box-shadow:12px 0 32px -12px rgba(21,32,26,.45)}'
    '.menu-lat:not(.rec)+.ml-tog+div{margin-left:68px}'
    '.menu-lat:not(.rec)~.ml-fundo{display:block;position:absolute;inset:0;z-index:34;background:rgba(21,32,26,.32);cursor:default}'
    f'{_RAIZ} h1{{white-space:normal!important;flex-shrink:1!important;min-width:0;overflow-wrap:anywhere}}'
    '}'
    '@media (pointer: coarse){.menu-lat a,.menu-lat>button{min-height:44px;box-sizing:border-box;display:flex!important;align-items:center}'
    '.ml-tog{width:32px;height:32px}.menu-lat.rec+.ml-tog{left:calc(52px + env(safe-area-inset-left,0px))}.ml-tog{left:calc(216px + env(safe-area-inset-left,0px))}}')
_CSS_ESTREITA=(f'@media (max-width: 640px){{.mf-tela select{{min-height:44px!important}}.g2-info{{width:44px!important;height:44px!important}}}}'   # NAV-2CB-TOQUE-01 (Codex, 13/10): listas da faixa com alvo de 44 px no celular
    f'{_RAIZ}>div:nth-child(2){{flex-wrap:wrap}}'          # linha do título: o comando principal desce em vez de sair da tela
    f'@media (max-width: 1279px){{{_RAIZ}>div{{flex-wrap:wrap}}}}'    # demais linhas do cabeçalho; em 1440 px igual à base
    f'@media (max-width: 640px){{{_RAIZ}{{padding:10px 14px!important;gap:8px!important}}'
    f'{_RAIZ} h1{{white-space:normal!important;flex-shrink:1!important;min-width:0;font-size:20px!important}}'
    f'{_RAIZ}>div>span{{max-width:100%!important;min-width:0}}'
    f'{_RAIZ}>div:nth-child(2)>span[style*="nowrap"],{_RAIZ}>div:nth-child(2)>span>span[style*="nowrap"]{{white-space:normal!important;max-width:100%;box-sizing:border-box}}'   # situação longa quebra em vez de sair da tela
    f'main[data-scroll]{{padding:12px 14px 18px!important;overflow-x:auto!important}}'
    f'.etp{{padding:6px 10px!important}}'
    + ','.join(_TIT) + '{flex-wrap:wrap}'                              # título do bloco e sua ação: a ação desce em vez de cobrir o título
    + ','.join(f'{s} :is(label,select)' for s in _TIT) + '{min-width:0;max-width:100%}'
    + f'{_KPI}{{flex-wrap:wrap}}{_KPI}>*{{flex-basis:90px}}{_KPI}>*>div:nth-child(2)>span{{display:block;line-height:1.35;margin-top:4px}}'          # dois indicadores por linha; a lista da tela sobe
    '}'
    '@media (max-width: 640px),(max-height: 560px){' + ','.join(_ESTICA) + '{flex:1 0 auto!important}}'
    # tela baixa (celular deitado, zoom de 200 %): cabeçalho, faixa e conteúdo rolam juntos; a faixa de etapas fica presa no alto
    '@media (max-height: 560px){.ml-tog+div{overflow-y:auto;scroll-padding-top:calc(var(--etp-h,0px) + 8px)}main[data-scroll]{flex:1 0 auto!important}}')   # foco não fica sob a faixa presa (altura medida pelo g2lib)
def _etp_css():
    """Regras das duas faixas: base (desktop igual) + modo estreito por container query, um bloco por limite.
    No modo estreito a lista abre como folha presa à base da janela (cabe em qualquer altura), com fundo que fecha ao toque.
    Progresso: a folha só informa (tocar nela ou fora fecha). Telas do módulo: tocar noutra tela leva a ela; na atual, fecha.
    Alvos de toque de 44 px (PRD, ações de campo)."""
    def estreita(p):
        r=[('.etp-itens','display:none!important'),
           ('.etp-chk','display:block;position:absolute;opacity:0;width:1px;height:1px;margin:0;pointer-events:none'),
           ('.etp-atual',f'display:flex;align-items:center;gap:8px;flex-grow:1;min-width:0;min-height:44px;box-sizing:border-box;padding:7px 10px;border-radius:10px;background:{ACCS};box-shadow:inset 0 -2px 0 {ACC};color:{INK};font-size:13px;font-weight:800;line-height:1.25;cursor:pointer'),
           ('.etp-chk:focus-visible',f'outline:none'),('.etp-chk:focus-visible+.etp-atual',f'outline:2px solid {ACC};outline-offset:2px'),   # o anel fica no rótulo visível, não na caixa invisível de 1 px
           ('.etp-chk:checked+.etp-atual .etp-seta','transform:rotate(180deg)'),
           ('.etp-chk:checked~.etp-fundo','display:block;position:fixed;inset:0;z-index:30;background:rgba(21,32,26,.32);cursor:default'),
           ('.etp-chk:checked~.etp-itens',f'display:flex!important;flex-direction:column;position:fixed;left:8px;right:8px;bottom:8px;max-width:560px;margin:0 auto;box-sizing:border-box;gap:2px;padding:6px;background:{SURF};border:1px solid {LINE};border-radius:14px;box-shadow:0 18px 40px -12px rgba(21,32,26,.5);max-height:calc(100% - 16px);overflow-y:auto;z-index:31;pointer-events:none'),
           ('.etp-chk:checked~.etp-itens>*','min-width:0!important;min-height:44px;box-sizing:border-box'),
           ('.etp-chk:checked~.etp-itens>a:not([aria-current]),.etp-chk:checked~.etp-itens>button:not([aria-current=true])','pointer-events:auto')]
        return ''.join(f'{p} {s}{{{d}}}' for s,d in r)
    lims=sorted(set(_ETP_LIM.values())|{520,900})
    return ('.etp{container:etp/inline-size}.etp-chk,.etp-atual,.etp-fundo{display:none}.etp-seta{transition:transform .15s ease}'
            '.etp-itens>*{min-width:min-content!important}'   # nenhuma etapa fica mais estreita que a maior palavra: sem texto por cima da vizinha
            '.etp-ind .etp-itens>li{cursor:default}'          # progresso: inerte (sem cursor de ação, sem hover de ação, sem foco)
            '@media (hover:hover){.etp-sec .etp-itens>:not([aria-current=page]):not([aria-current=true]):hover{background:#F2F8F4!important;text-decoration:underline;text-underline-offset:3px}}'
            + ''.join(f'@container etp (max-width: {L-1}px){{{estreita(f".etp-l{L}")}}}' for L in lims))
def steps_bar(steps,current=None,label=None):
    """Telas irmãs de um módulo de trabalho paralelo, por links (MA-01…05, módulos ocultos): navegação, não progresso.
    Sem número de etapa e sem setas (UX-ACAO-UNICA-20261003); o atual leva aria-current="page"; a pendência da tela fica escrita.
    steps: [dict(t, href, why='', cur=bool, tip)]"""
    n=len(steps)
    c=current if current is not None else next((i for i,s in enumerate(steps,1) if s.get('cur')),0)
    itens=''.join(secao_item(s['t'],i==c,href=s.get('href','#'),why=s.get('why') or '') for i,s in enumerate(steps,1))
    lab=label if label and label not in ('Etapas','Etapas do processo') else 'Telas do módulo'
    return secoes_nav(itens,n,c,steps[c-1]['t'] if c else '',lab)

def continuity(veio,aqui,falta,proxima):
    """Faixa do cap. 4.2: Veio de → Está aqui → Falta → Próxima ação."""
    def cell(lbl,val,strong=False):
        return (f'<span style="display: inline-flex; flex-direction: column; gap: 1px; min-width: 0;">'
                f'<span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{lbl}</span>'
                f'<span style="font-size: 12.5px; font-weight: {700 if strong else 600}; color: {ACC if strong else INK}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{val}</span></span>')
    arrow=f'<span style="color: {MUTED}; flex-shrink: 0;">→</span>'
    return (f'<div style="display: flex; align-items: center; gap: 12px; padding: 8px 14px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px;">'
            + cell('VEIO DE',veio)+arrow+cell('ESTÁ AQUI',f'<b>{aqui}</b>')+arrow+cell('FALTA',falta)+arrow+cell('PRÓXIMA AÇÃO',proxima,strong=True)+'</div>')

def demo_badge():
    return (f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; margin: 4px 0; border-radius: 10px; background: rgba(255,255,255,.06); color: {SIDE_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: .05em;">'
            f'<span style="width: 7px; height: 7px; border-radius: 999px; background: {YEL}; flex-shrink: 0;"></span><span class="ml-txt">DEMONSTRAÇÃO · dados fictícios</span></div>')

def perfil_pill(perfil):
    """avatar do perfil no pé da barra recolhida (13/10/2026): a dica diz o perfil; na equipe da fazenda o toque no avatar abre a lista de
    perfis de demonstração (o seletor fica por cima do avatar, transparente; g2lib.js G2_PERFIS é a fonte única). Portal e backoffice: fixos."""
    ini=perfil[0].upper()
    av=('position: relative; width: 32px; height: 32px; border-radius: 999px; background: {ACC}; color: #fff; font-weight: 700; font-size: 13px; '
        'display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;').replace('{ACC}',ACC)
    pe='display: flex; align-items: center; justify-content: center; padding: 10px 0; border-top: 1px solid rgba(255,255,255,.08);'
    if perfil=='Ana · Gestora':
        return (f'<div style="{pe}"><label title="Perfil de demonstração: {{{{perfil_k}}}} · tocar para trocar" style="{av} cursor: pointer;">{{{{perfil_ini}}}}'
            f'<select aria-label="Trocar perfil de demonstração" value="{{{{perfil_k}}}}" onChange="{{{{perfil_set}}}}" style="position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; font-size: 16px; border: 0;">'
            f'<sc-for list="{{{{perfil_opts}}}}" as="o" hint-placeholder-count="5"><option value="{{{{o.v}}}}" style="color: {INK};">{{{{o.t}}}}</option></sc-for></select></label></div>')
    return f'<div style="{pe}"><span title="{esc(perfil)}" style="{av}">{ini}</span></div>'

# Filtros de fazenda e safra por tela: 'filtro' = seletor que muda os dados da tela; 'contexto' = só leitura (escolhido no próprio processo).
# 13/10/2026 (proprietário: "tire o macro filtro fazenda e safra do topo e coloque nas telas para evitar confusão"): saem da barra do topo e
# ficam na própria tela, numa faixa "Filtros desta tela" acima dos dados que filtram (shell37); as ligações (mf_*) não mudam.
MACRO = {
    'IN-04.dc.html': dict(faz='filtro'),
    'OS.dc.html': dict(faz='filtro', saf='filtro', cult='filtro', tal='filtro'),   # 13/10 (proprietário): Cultura e Talhão no filtro principal da O.S.
    'SAF.dc.html': dict(faz='contexto', saf='contexto'),
    'CMP.dc.html': dict(faz='contexto', saf='contexto'),
    'EST.dc.html': dict(faz='filtro'),
    'COLH.dc.html': dict(faz='filtro', saf='filtro', cult='filtro', tal='filtro'),   # 13/10: Cultura e Talhão onde ajudam (colheita é por cultura e talhão)
    'CARGA.dc.html': dict(faz='filtro', saf='filtro', cult='filtro'),
    'PROD.dc.html': dict(faz='filtro', saf='filtro', cult='filtro'),
}
FAZENDAS = ['Lagoa Grande', 'Santa Rita', 'Boa Vista']
SAFRAS_MF = ['2026/27', 'Safrinha 2027', '2025/26']
# faixa "Filtros" (funil + seletores): o mesmo desenho em toda tela que filtra dados (14/10/2026, proprietário: "em manutenção os filtros não
# estavam seguindo o padrão que definimos"). MF_SEL e MF_LBL são o seletor e o rótulo; faixa_filtros monta a faixa (shell37 e telas com filtros próprios)
MF_SEL = ('font-family: inherit; font-size: 12px; font-weight: 700; padding: 4px 26px 4px 10px; min-height: 32px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer;')   # alvo de toque ≥ 32 px
MF_LBL = 'display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;'
def faixa_filtros(inner, rot='Filtros', fim=''):
    cab = (f'<span class="mf-rot" data-dica="Filtros" style="display: inline-flex; align-items: center; color: {MUTED};">{icon("filtro",18,MUTED)}</span>' if rot == 'Filtros'
           else f'<span class="mf-rot" style="font-size: 11.5px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; color: {MUTED};">{rot}</span>')
    return (f'<div class="mf-tela" role="group" aria-label="{rot}" style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; flex-shrink: 0; '
            f'padding: 8px 14px; min-height: 48px; box-sizing: border-box; border: 1px solid {LINE}; border-radius: 12px; background: {SURF};">'   # 14/10 (proprietário: "trabalhando em… ficou muito estreito"): o mesmo respiro com ou sem ação no fim
            f'{cab}{inner}' + (f'<span style="margin-left: auto;">{fim}</span>' if fim else '') + '</div>')
def _macro_html(fname, ctx, sep=True):
    cfg = MACRO.get(fname)
    sel = MF_SEL
    lab = f'display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: {GRAYS}; font-weight: 700; font-size: 11.5px;'
    if cfg is None:
        return ''
    out = ''
    if cfg.get('faz') == 'filtro':
        out += (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;">Fazenda'
                f'<select aria-label="Filtrar por fazenda" value="{{{{mf_faz}}}}" disabled="{{{{mf_susp}}}}" onChange="{{{{mf_setfaz}}}}" style="' + sel.format(LINE=LINE, SURF=SURF, INK=INK) + '">'
                + ''.join(f'<option value="{f}">{f}</option>' for f in ['Todas'] + FAZENDAS) + '</select></label>')
    elif cfg.get('faz') == 'contexto':
        out += f'<span title="Fazenda da safra aberta" style="{lab}">{esc(ctx[0]) if ctx and ctx[0] else "Fazenda Santa Rita"}</span>'
    if cfg.get('saf') == 'filtro':
        out += (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;">Safra'
                f'<select aria-label="Filtrar por safra" value="{{{{mf_saf}}}}" disabled="{{{{mf_susp}}}}" onChange="{{{{mf_setsaf}}}}" style="' + sel.format(LINE=LINE, SURF=SURF, INK=INK) + '">'
                + ''.join(f'<option value="{f}">{f}</option>' for f in ['Todas'] + SAFRAS_MF) + '</select></label>')
    elif cfg.get('saf') == 'contexto':
        out += (f'<span style="{lab}">{ctx[1] if ctx and len(ctx) > 1 and ctx[1] else ""}</span>'
                f'<button type="button" onClick="{{{{mf_trocar}}}}" title="Voltar à etapa 1 para escolher outra safra" style="border: 0; background: transparent; color: {ACC}; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px;">Trocar safra</button>')
    # Cultura e Talhão (13/10/2026, proprietário: "em ordem de serviço coloque no filtro principal da tela... também cultura e talhão"): as opções
    # vêm da tela (mf_cult_opts, mf_tal_opts: só o que existe no recorte de Fazenda e Safra); o Talhão é o mesmo filtro da coluna Talhão
    for k, rot, al in (('cult', 'Cultura', 'Filtrar por cultura'), ('tal', 'Talhão', 'Filtrar por talhão')):
        if cfg.get(k) == 'filtro':
            out += (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;">{rot}'
                    f'<select aria-label="{al}" value="{{{{mf_{k}}}}}" disabled="{{{{mf_susp}}}}" onChange="{{{{mf_set{k}}}}}" style="' + sel.format(LINE=LINE, SURF=SURF, INK=INK) + '">'
                    f'<sc-for list="{{{{mf_{k}_opts}}}}" as="o" hint-placeholder-count="3"><option value="{{{{o.v}}}}">{{{{o.t}}}}</option></sc-for></select></label>')
    return out + (f'<span style="width: 1px; height: 18px; background: {LINE};"></span>' if sep else '')

# Faixa de cobrança (PLAT-01, R11): só nas telas web da organização (fora de BO, ON e PT; não no próprio CF-05, que já mostra o estado e a
# primária). Amarela em atraso (nada restrito), vermelha inadimplente (ampliar a área suspenso). "Pagar fatura" é link de texto para o CF-05,
# nunca botão verde (não vira 2ª primária). O app de campo (mobile37) nunca mostra cobrança. Texto e cor vêm de assinAvisoVals (assinatura.js).
def faixa_cobranca(fid,fname):
    if fid[:2] in ('BO','ON','PT') or fname.startswith('CF-05'): return ''
    return (f'<sc-if value="{{{{assin_fx}}}}" hint-placeholder-val="{{{{false}}}}"><div role="note" aria-label="Cobrança" class="assin-fx" style="{{{{assin_fx_st}}}}">'
            # celular: só o essencial, com o link na mesma linha do texto (revisão PLAT, achado 12: a faixa ocupava 123 px)
            f'<style>.assin-fx-m{{display:none}}@media (max-width:640px){{.assin-fx-w{{display:none}}.assin-fx-m{{display:inline}}.assin-fx{{display:block!important;padding:6px 10px!important}}.assin-fx>a{{margin-left:6px;white-space:nowrap}}}}</style>'
            f'<span class="assin-fx-w">{{{{assin_fx_t}}}}</span><span class="assin-fx-m">{{{{assin_fx_m}}}}</span><a href="CF-05.dc.html#pagar" style="color: inherit; font-weight: 800; text-decoration: underline; text-underline-offset: 3px;">Pagar fatura ›</a></div></sc-if>')
def shell37(fid,title,body,subtitle='',status=None,primary=None,primary_href=None,crumbs_extra=None,
            ctx=('Fazenda Santa Rita','Safra 2026/27',None),cont=None,chipsrow='',footer=None,
            fname=None,W=1440,H=880,perfil='Ana · Gestora',search=False,steps=None,primary_html=None,mf_fim=''):
    # subtítulo sob o título não aparece mais# 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas"); o parâmetro fica por compatibilidade
    fname=fname or ffile(fid)
    H=_h(fname,H)
    if steps: H=max(900,min(H,1000))  # processos: tela de trabalho com rolagem interna; faixa de etapas sempre visível
    mi,mh=menu_item(fname)
    if mi is not None:
        vs=[l for l,h in MENU2[mi][2] if h.split('#')[0]==mh]   # vários subitens da mesma tela (visões da Manutenção): o caminho diz o grupo, como antes
        m={'area':MENU2[mi][0],'submenu':vs[0] if len(vs)==1 else MENU2[mi][0]}
    else:
        m=MAPA.get(fid) or {'area':area_of(fid) or 'Módulo oculto','submenu':CAT.get(fid,{}).get('titulo',fid)}
    if fname==OUTROS37[2]: m={'area':OUTROS37[0],'submenu':OUTROS37[0]}
    if fname in VOLTA37 and not crumbs_extra: m={'area':m['area'],'submenu':title}   # cadastro aberto pela tela inicial: o caminho diz qual
    crumbs=([m['area']] if m['area']==m['submenu'] and not crumbs_extra else [m['area'],m['submenu']])+(crumbs_extra or [])   # "Cadastros", não "Cadastros › Cadastros"
    back=PARENT37.get(fname) or ffile(fid) if crumbs_extra else (PARENT37.get(fname) or fname)
    _sep=f' <span style="color: {MUTED};">›</span> '
    parts=[]
    for i,c in enumerate(crumbs):
        if i==1 and crumbs_extra: parts.append(f'<a href="{(mh or ffile(fid))}" style="color: {MUTED}; text-decoration: none;">{esc(c)}</a>')
        elif i<len(crumbs)-1: parts.append(f'<span style="color: {MUTED};">{esc(c)}</span>')
        else: parts.append(f'<span>{esc(c)}</span>')
    crumb=_sep.join(parts)
    if crumbs==[title]: crumb=''   # tela de entrada do módulo: o caminho repetiria o título (13/10, mais essencial)
    if oculto(fname):
        ctxp=''.join(f'<span style="font-size: 11.5px; color: {MUTED}; font-weight: 600;">{esc(c)}</span>' for c in tuple(ctx) if c)   # 14/10 (menos é mais): saiu o rótulo "Módulo oculto no menu · preservado"
        ctxp+=f'<span style="width: 1px; height: 18px; background: {LINE};"></span>'
    else:
        ctxp=''   # Fazenda e Safra não ficam mais no topo (13/10/2026): vão para a tela, junto dos dados
        mf=_macro_html(fname,ctx,sep=False)
        if mf:
            _filtra='filtro' in (MACRO.get(fname) or {}).values()   # só contexto (Planejar safra, Compra): a faixa diz onde se trabalha, não "filtros"
            # 14/10/2026 (proprietário: "Em vez de filtros desta tela… coloque Filtros: · teste o símbolo de filtro junto ou sozinho"): testadas as três
            # (texto, funil + texto, só o funil); fica só o funil, com a dica "Filtros" (cada filtro já tem o nome ao lado; no celular sobra largura).
            # O grupo continua com o nome acessível "Filtros". Só contexto (Planejar safra, Compra) segue "Trabalhando em".
            _rot='Filtros' if _filtra else 'Trabalhando em'
            body=faixa_filtros(mf,_rot,mf_fim) + body   # mf_fim: ação da tela que cabe na faixa (Planejar safra: Comparar versões do plano), sem uma linha a mais
        search=False
    st=chip(status[0],status[1]) if status else ''
    srch=(f'<span style="flex-grow: 1;"></span><span style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border: 1px solid {LINE}; border-radius: 999px; background: {SURF}; color: {MUTED}; font-size: 12.5px; min-width: 220px;">'
          f'{icon("lista",13,MUTED)}Buscar ID, talhão, ativo, lote, pessoa…</span>') if search else '<span style="flex-grow: 1;"></span>'
    prim=primary_html or (btn(primary,True,href=primary_href) if primary else '')
    controw=cont if cont else ''
    # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos e os demais soltos pela tela ... somos minimalistas e essencialistas"):
    # a regra que ficava numa faixa no rodapé vira uma dica (ⓘ ao lado do título, com nome acessível; abre no hover, no foco e no toque)
    foot=''
    info=(f'<button type="button" class="g2-info" aria-label="Regras desta tela" data-dica="{esc(footer)}" style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 999px; '
          f'border: 1px solid {LINE}; background: {SURF}; color: {MUTED}; font-family: inherit; font-size: 15px; font-weight: 700; cursor: help; display: inline-flex; align-items: center; justify-content: center;">i</button>') if footer else ''
    voltar=f'<a href="{back}" aria-label="Voltar" style="text-decoration: none; display: inline-flex; align-items: center;">{chev()}</a>' if crumbs_extra else ''
    if not crumbs_extra and fname in VOLTA37:
        _vr,_vh=VOLTA37[fname]
        voltar=(f'<a href="{_vh}" class="volta37" aria-label="Voltar para {esc(_vr)}" style="text-decoration: none; display: inline-flex; align-items: center; gap: 4px; min-height: 36px; padding: 0 14px 0 10px; '
                f'border: 1px solid {LINE}; border-radius: 999px; background: {SURF}; color: {INK}; font-size: 13px; font-weight: 700; flex-shrink: 0;">'
                f'<span aria-hidden="true" style="font-size: 16px; line-height: 1;">‹</span>{esc(_vr)}</a>')
    html=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>
html,body{{height:100%;overflow:hidden}}
.menu-lat{{width:232px;transition:width .18s ease}}.menu-lat.rec{{width:68px}}.menu-lat.rec .ml-txt,.menu-lat.rec .ml-sub{{display:none!important}}
.menu-lat.rec a,.menu-lat.rec button{{justify-content:center}}
.ml-tog{{position:absolute;top:calc(22px + env(safe-area-inset-top,0px));left:calc(219px + env(safe-area-inset-left,0px));z-index:40;width:26px;height:26px;border:1px solid {LINE};border-radius:999px;background:#fff;color:{INK};cursor:pointer;display:inline-flex;align-items:center;justify-content:center;padding:0;box-shadow:0 1px 4px rgba(21,32,26,.22);transition:left .18s ease}}
.menu-lat.rec+.ml-tog{{left:calc(55px + env(safe-area-inset-left,0px))}}@media (hover:hover){{.ml-tog:hover{{background:{ACCS};color:{ACC}}}}}.ml-tog:focus-visible{{outline:2px solid {ACC};outline-offset:2px}}body{{margin:0;font-family:{FONT};color:{INK};background:{BG}}}
a{{color:{ACC}}}@media (hover:hover){{a:hover{{color:#15603a}}}}
{E.G2_CSS}
{_etp_css()}{_CSS_ESTREITA}{_CSS_RESP}
</style>
</helmet>
<div data-root="1" style="position: relative; width: 100%; box-sizing: border-box; display: flex; background: {BG}; font-family: {FONT}; color: {INK}; overflow: clip;">
<nav aria-label="Menu" class="menu-lat {{{{menu_cls}}}}" style="flex-shrink: 0; background: {SIDE}; display: flex; flex-direction: column; padding: 16px 12px 12px; gap: 2px; box-sizing: border-box; overflow-x: clip; overflow-y: auto;">
{navbar(fid,fname)}
<div style="flex-grow: 1;"></div>
{demo_badge()}
{perfil_pill(perfil)}
</nav>
<span class="ml-tog" aria-hidden="true" style="display: none;"></span>
<div style="flex-grow: 1; display: flex; flex-direction: column; min-width: 0; min-height: 0;">
<header style="padding: 14px 32px 14px; background: {SURF}; border-bottom: 1px solid {LINE}; display: flex; flex-direction: column; gap: 10px;">
<div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 500;">{ctxp}<span>{crumb}</span>{srch}</div>
<div style="display: flex; align-items: center; gap: 12px;">
{voltar}<h1 style="margin: 0; font-family: {DISP}; font-size: 23px; font-weight: 700; letter-spacing: -.02em; white-space: nowrap; flex-shrink: 0;">{esc(title)}</h1>{info}
<span style="flex-shrink: 0; max-width: 300px;">{st}</span>
<span style="flex-grow: 1;"></span>
{prim}
</div>

{faixa_cobranca(fid,fname)}
{controw}
{chipsrow}
</header>
{steps or ''}
<main data-scroll="1" style="flex-grow: 1; padding: 18px 32px 22px; overflow-y: auto; overflow-x: hidden; min-height: 0; display: flex; flex-direction: column; gap: 18px; box-sizing: border-box; min-width: 0;">
{body}
</main>
{foot}
</div>
{extra_html()}
{E.G2_TOAST}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
{engine()}
</script>
</body>
</html>
'''
    open(os.path.join(E.P,fname),'w').write(html)
    _reset_screen(fname)  # engine() NÃO limpa o registro; sem isto, widgets/drawers vazam para a tela seguinte
    return fname

def mobile37(fid,title,sub,status,primary,body,fname=None,H=844,back='MB-01.dc.html',primary_href=None,dica=''):
    """Tela móvel MB: cabeçalho simples, CTA grande, badge de demonstração; reseta o registro após gravar."""
    fname=fname or ffile(fid)
    E.HEIGHTS[fname]=_h(fname,H)
    E.MPARENT[fname]=back
    if primary_href: E.PHREF[fname]=primary_href
    E.mobile(fname,title,sub,status,primary,body,dica=dica)   # dica: regras da tela no ⓘ do cabeçalho (14/10/2026)
    _reset_screen(fname)
    return fname

# ---------- vocabulário visual único ----------
_RED_WORDS=('impedid','bloquead','atrasad','conflito','vencid','reprovad','rejeitad','falha')
def selo(texto):
    """Condição (selo) de uma ordem/objeto: vermelho para impedimento/bloqueio/atraso/conflito; amarelo para o resto."""
    if not texto: return '—'
    t=texto.lower()
    return chip(texto,'red' if any(w in t for w in _RED_WORDS) else 'yellow')
ETAPA_COR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'}
def etapa(nome): return chip(nome,ETAPA_COR.get(nome,'gray'))

def farm_map(h=460,camada='Integrado',sel=None):
    """Mapa da fazenda em largura total: talhões (polígonos) e pivôs (círculos) com rótulo grande, cor e legenda pela camada."""
    GEO=[('T1','poly','30,30 290,22 300,205 40,215'),('T2','poly','315,22 560,28 555,200 318,206'),
         ('T4','poly','40,250 300,240 305,430 45,438'),('T3','poly','320,240 555,236 560,430 325,434'),
         ('P1','circ','685,118,88'),('P2','circ','890,118,82'),
         ('T7','poly','590,245 780,240 785,430 595,434'),('C1','poly','800,240 970,236 975,430 805,434')]
    L=LAYERS.get(camada,LAYERS['Integrado'])
    g=[]
    for tid,tp,geo in GEO:
        ck,leg=L['v'].get(tid,('none',''))
        fill,stroke=LCOR[ck]
        hatch=(ck=='cloud')
        wsel=' stroke-width="4"' if sel==tid else ' stroke-width="2"'
        fillattr=f'fill="url(#hatch)"' if hatch else f'fill="{fill}" fill-opacity="{".8" if ck not in ("none",) else "1"}"'
        if tp=='poly':
            pts=[tuple(map(float,p.split(','))) for p in geo.split()]
            cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            g.append(f'<polygon points="{geo}" {fillattr} stroke="{stroke}"{wsel}/>')
        else:
            cx,cy,r=map(float,geo.split(','))
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {fillattr} stroke="{stroke}"{wsel}/>')
            g.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*0.7}" y2="{cy-r*0.7}" stroke="{stroke}" stroke-width="2"/>')
        g.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="Sora, Manrope, sans-serif" font-size="34" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="5" paint-order="stroke">{tid}</text>')
        if leg: g.append(f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-family="Manrope, sans-serif" font-size="12.5" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="3.5" paint-order="stroke">{esc(leg)}</text>')
    svg=(f'<svg viewBox="0 0 1000 460" width="100%" height="{h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa da fazenda Santa Rita, camada {esc(camada)}" style="display: block; background: #DDE5D4; border-radius: 14px;">'
         '<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/><line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern></defs>'
         '<rect x="0" y="0" width="1000" height="460" fill="#DDE5D4"/>'
         '<path d="M0 225 C 250 219, 520 231, 1000 225" stroke="#B9C6AE" stroke-width="10" fill="none"/>'
         + ''.join(g) + '</svg>')
    return svg
def map_legend(camada):
    L=LAYERS.get(camada,LAYERS['Integrado'])
    itens=' · '.join(f'<span style="color:{LCOR[k][1]}; font-weight:700;">■ {esc(t)}</span>' for k,t in L['leg'])
    return f'<div style="font-size: 11.5px; color: {MUTED};"><b style="color:{INK};">{esc(camada)}</b> · {esc(L["fonte"])} · {itens}</div>'
# cores por classe (paleta viva; nuvem hachurada, sem dado neutro)
LCOR={'ok':('#3FBF2A','#1E7A4C'),'good':('#0B7A1E','#0B5A16'),'lime':('#B5E61D','#5F7A0E'),'yellow':('#FFD500','#8A5A00'),
      'orange':('#FF6A00','#9A3F00'),'red':('#E4002B','#9E0A1F'),'gray':('#C9CFCB','#5B6660'),'blue':('#4FA3E0','#1E5F8F'),
      'navy':('#1E5F8F','#123A57'),'none':('#E9EEE6','#8A968E'),'cloud':('#C9CFCB','#6B6B6B'),'purple':('#9B7BD4','#5B3E94')}
LAYERS={
 'Integrado':{'fonte':'O.S. (PCP, 23/09 06:40), satélite 21/09 (nuvem 4%), solo campanha 2026',
   'v':{'T1':('ok','OS-0421 · 190/350 ha'),'T2':('ok','OS-0421 · mesma ordem'),'T4':('red','OS-0420 · impedida'),'T3':('gray','OS-0415 · encerrada'),
        'P1':('yellow','2 ordens · atenção'),'P2':('blue','água por política'),'T7':('none','mamão · sem ordem'),'C1':('none','café · granação')},
   'leg':[('ok','em execução/no prazo'),('yellow','atenção'),('red','impedida'),('blue','água por política'),('gray','encerrada'),('none','sem ordem aberta')]},
 'Satélite':{'fonte':'NDVI Sentinel-2 · cena 21/09 · nuvem 4% (C1 com nuvem) · escala da fazenda',
   'v':{'T1':('gray','pré-plantio · solo exposto'),'T2':('gray','pré-plantio · solo exposto'),'T4':('gray','pré-plantio'),'T3':('gray','colhido'),
        'P1':('good','NDVI 0,84 · vigor alto'),'P2':('ok','NDVI 0,76 · bom'),'T7':('lime','NDVI 0,66 · mancha 1,2 ha'),'C1':('cloud','nuvem · sem leitura')},
   'leg':[('good','> 0,82 vigor alto'),('ok','0,72–0,82 bom'),('lime','0,60–0,72 médio'),('yellow','0,45–0,60 atenção'),('red','< 0,30 falha'),('gray','sem cultura'),('cloud','nuvem (hachurado)')]},
 'Solo':{'fonte':'saturação por bases V% · 0–20 cm · campanha 2026 · laboratório Lab Solo Vale',
   'v':{'T1':('yellow','V 48%'),'T2':('ok','V 55%'),'T4':('red','V 41% · abaixo da meta'),'T3':('good','V 62%'),
        'P1':('ok','V 58%'),'P2':('good','V 60%'),'T7':('good','V 66%'),'C1':('yellow','V 52%')},
   'leg':[('red','< 45%'),('yellow','45–55%'),('ok','55–60%'),('good','≥ 60%')]},
 'MIP/MID':{'fonte':'vistorias de 20–22/09 · contagem × nível de controle da cultura',
   'v':{'T1':('none','sem cultura'),'T2':('none','sem cultura'),'T4':('orange','nematoide · VIS-011'),'T3':('none','colhido'),
        'P1':('red','percevejo 2,1/pano · NC 2'),'P2':('ok','abaixo do nível'),'T7':('yellow','ácaro · atenção'),'C1':('ok','abaixo do nível')},
   'leg':[('red','acima do nível de controle'),('orange','foco em investigação'),('yellow','atenção'),('ok','abaixo do nível'),('none','sem registro')]},
 'O.S./prazos':{'fonte':'O.S. do PCP · hoje 23/09',
   'v':{'T1':('ok','no prazo'),'T2':('ok','no prazo'),'T4':('red','atrasada · ativo bloqueado'),'T3':('gray','encerrada'),
        'P1':('orange','vence hoje'),'P2':('blue','irrigando hoje 18h'),'T7':('none','sem ordem'),'C1':('none','sem ordem')},
   'leg':[('red','atrasada'),('orange','vence hoje'),('yellow','até 3 dias'),('ok','no prazo'),('blue','irrigando'),('gray','encerrada')]},
 'Irrigação':{'fonte':'balanço hídrico 23/09 06:00 · sensores P1/P2 · estação Sede',
   'v':{'T1':('none','sequeiro'),'T2':('none','sequeiro'),'T4':('none','sequeiro'),'T3':('none','sequeiro'),
        'P1':('yellow','déficit 18 mm'),'P2':('blue','lâmina 10,81 mm · 62%'),'T7':('ok','gotejo em dia'),'C1':('none','sequeiro')},
   'leg':[('red','déficit crítico'),('yellow','déficit'),('ok','em dia'),('blue','irrigando'),('none','sequeiro')]},
 'Estádio':{'fonte':'ocupações e fenologia apontadas · variedade por parcela',
   'v':{'T1':('gray','pré-plantio · 58 W e 62 X'),'T2':('gray','pré-plantio · 58 W'),'T4':('gray','pré-plantio'),'T3':('none','colhido 12/09'),
        'P1':('purple','Feijão BRS · R5'),'P2':('ok','Milho · V10'),'T7':('yellow','Mamão · produção'),'C1':('orange','Café · granação')},
   'leg':[('gray','pré-plantio'),('ok','vegetativo'),('purple','reprodutivo'),('yellow','produção contínua'),('orange','enchimento/maturação'),('none','colhido')]},
 'Colheita/produtividade':{'fonte':'romaneios conferidos e previsões publicadas · safra 2026/27',
   'v':{'T1':('none','—'),'T2':('none','—'),'T4':('none','—'),'T3':('good','142 sc/ha · realizado'),
        'P1':('lime','previsto 48 sc/ha'),'P2':('lime','previsto 180 sc/ha'),'T7':('ok','9,6 t A/semana'),'C1':('lime','previsto 38 sc/ha')},
   'leg':[('good','realizado acima da meta'),('ok','realizado na meta'),('lime','previsão'),('red','abaixo da meta'),('none','sem dado')]},
 'Custos':{'fonte':'custo realizado R$/ha × orçado · fechamento parcial 22/09',
   'v':{'T1':('ok','R$ 1.240/ha · no orçado'),'T2':('ok','R$ 1.180/ha'),'T4':('red','R$ 2.050/ha · +18%'),'T3':('ok','R$ 3.960/ha · fechado'),
        'P1':('yellow','R$ 3.900/ha · +6%'),'P2':('ok','R$ 3.400/ha'),'T7':('ok','R$ 21 mil/ha/ano'),'C1':('ok','R$ 9,8 mil/ha')},
   'leg':[('ok','dentro do orçado'),('yellow','até +10%'),('red','acima de +10%')]},
}

def tabs(opts,contents,active=0,label='Visão',chips=False):
    """Abas reais: devolve (barra, painéis). Cada painel só aparece com sua aba ativa (sc-if sobre o estado do seg)."""
    from engine import seg_buttons, SEG_ON, SEG_OFF
    on=off=None
    if chips:
        on=f'font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 5px 11px; border-radius: 999px; border: 1px solid {INK}; background: {INK}; color: #fff; cursor: pointer; white-space: nowrap;'
        off=f'font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 5px 11px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer; white-space: nowrap;'
    s,bs=seg_buttons(opts,active,on=on,off=off)
    # seletor exclusivo de visão da mesma coleção (DS-33 §74.5.7.1 · DS-36 v2): grupo de botões com aria-pressed, não abas de processo
    bar=(f'<div role="group" aria-label="{esc(label)}" style="display: inline-flex; flex-wrap: wrap; gap: {6 if chips else 2}px; '
         + ('' if chips else f'padding: 3px; border-radius: 999px; background: {GRAYS};') + '">' + ''.join(bs) + '</div>')
    panes=''.join(f'<sc-if value="{HL(s+"_v"+str(i))}" hint-placeholder-val="{HL("true") if i==active else HL("false")}">{c}</sc-if>' for i,c in enumerate(contents))
    return bar,panes


def steps_state(names,pre='stp',label='Etapas do processo'):
    """Indicador de progresso do processo guiado (estado da tela; g2steps preenche): lista ordenada com número ou ✓, nome, palavra do
    estado para leitor de tela e motivo do impedimento. Não navega: sem botão, sem handler, sem parada de Tab (DS-31 v2)."""
    n=len(names); items=''
    for i,t in enumerate(names,1):
        h=lambda k,i=i: '{{'+f'{pre}{i}_{k}'+'}}'
        items+=(f'<li aria-current="{h("cur")}" class="etp-it" style="{h("st")}"><span aria-hidden="true" style="{h("bst")}">{h("num")}</span>'
                f'<span style="display: flex; flex-direction: column; min-width: 0;"><span style="{h("tst")}">{esc(t)}<span class="etp-sr"> · {h("sr")}</span></span>'
                f'<sc-if value="{h("hasWhy")}" hint-placeholder-val="{{{{false}}}}"><span style="font-size: 11px; font-weight: 700; color: {RED}; line-height: 1.2;">{h("why")}</span></sc-if></span></li>')
    # etapa atual em texto para a faixa estreita: um bloco por etapa, montado só na atual; ao trocar de etapa a caixa nasce fechada
    abre=''.join(f'<sc-if value="{{{{{pre}{i}_cur === \'step\'}}}}" hint-placeholder-val="{{{{false}}}}">{_etp_abre(i,n,t)}</sc-if>' for i,t in enumerate(names,1))
    return _etp_progresso(n,_etp_lista(abre,items,'ol',f' aria-label="{esc(label)}"'))
def secoes_state(names,pre='stp',label='Seções'):
    """Seções de uma tela de trabalho paralelo (Estoque): navegação entre visões em qualquer ordem (g2secoes preenche).
    Sem número de etapa e sem setas; a seção atual leva aria-current="true"; a pendência de cada uma fica escrita."""
    n=len(names); items=''
    for i,t in enumerate(names,1):
        h=lambda k,i=i: '{{'+f'{pre}{i}_{k}'+'}}'
        items+=(f'<button type="button" onClick="{h("go")}" aria-current="{h("cur")}" style="{h("st")}"><span>{esc(t)}</span>'
                f'<sc-if value="{h("hasWhy")}" hint-placeholder-val="{{{{false}}}}"><span style="font-size: 11px; font-weight: 700; color: {RED};">{h("why")}</span></sc-if></button>')
    abre=''.join(f'<sc-if value="{{{{{pre}{i}_cur === \'true\'}}}}" hint-placeholder-val="{{{{false}}}}">{_etp_abre(i,n,t,secao=True)}</sc-if>' for i,t in enumerate(names,1))
    return _etp_telas(label,n,_etp_lista(abre,items))
