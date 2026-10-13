# -*- coding: utf-8 -*-
"""Índice central do protótipo v3.7 — entrada por área, perfis de demonstração e cenários DEMO."""
import json, os
from engine import (icon,esc,chip,tag,btn,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,GRAYS,SH,DISP,FONT,SIDE,SIDE_TX,SIDE_MUTED)
import engine as E
from ui37 import AREA_ICON, MENU, MAPA, ffile, _h

PERFIS=[('Ana','Gestora · safra, compras e aprovações','SAF.dc.html'),
 ('Beto','Agrônomo(a) · planos agronômicos','PA.dc.html'),
 ('Caio','PCP · ordens de serviço','OS.dc.html'),
 ('Marcos','Operador(a) de campo · app móvel','MB-01.dc.html'),
 ('Rui','Almoxarife · estoque e custódia','EST.dc.html'),
 ('Dora','Comercial e logística','VE-01.dc.html'),
 ('Fertisul','Parceiro credenciado (portal)','PT-01.dc.html'),
 ('Plataforma','Backoffice (admin)','BO-02.dc.html')]
CENARIOS=[('Safra','Planejar safra: aplicar plano em lote, ajustar um cultivo e enviar para cotação','SAF.dc.html'),
 ('Compra','Compra de insumos: da SOL-2026-07 às propostas, aprovação e entrega','CMP.dc.html'),
 ('Estoque','Estoque: recebimento com quarentena, entrega por O.S. e devolução','EST.dc.html'),
 ('Planos','Planos agronômicos: gatilho → atividades → produtos e doses','PA.dc.html'),
 ('Mapa','Mapa: trocar camada, filtrar e clicar no talhão','IN-04.dc.html'),
 ('DEMO-13','Uma O.S., sete dias — fechar turno não conclui','CA-01det.dc.html'),
 ('DEMO-14','Dose ajustada só no saldo (60/40)','OS.dc.html#OS-0420'),
 ('DEMO-03','Custódia e devolução parcial (100/70/20/10)','CA-04.dc.html'),
 ('DEMO-15','Água sem agrônomo, liberada pela prontidão','IR-02.dc.html'),
 ('DEMO-16','Água reclassificada em fertirrigação','OS.dc.html#OS-0418'),
 ('DEMO-17','Ativo bloqueado antes do início','PL-05.dc.html'),
 ('DEMO-18','Reserva concorrente do mesmo lote','SU-07.dc.html'),
 ('DEMO-11','Offline reenviado duas vezes','MB-03.dc.html'),
 ('DEMO-19','Processo encerrado, lote não liberado','CO-06.dc.html'),
 ('DEMO-20','Caminhão atrasado e fila explicável','LO-02.dc.html')]

def build():
    fname='Main.dc.html'
    E._reset_screen(fname)
    W,H=1440,_h(fname,1500)
    def card(area,subs,first):
        lis=''.join(f'<a href="{ffile(f)}" style="display: block; font-size: 12.3px; color: {MUTED}; text-decoration: none; padding: 2px 0;">{esc(m["submenu"])}</a>' for f,m in subs[:4])
        mais=f'<span style="font-size: 11.5px; color: {MUTED};">+{len(subs)-4} destinos</span>' if len(subs)>4 else ''
        return (f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px; min-width: 0;">'
                f'<a href="{ffile(first)}" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 10px;"><span style="width: 34px; height: 34px; border-radius: 10px; background: {ACCS}; display: inline-flex; align-items: center; justify-content: center;">{icon(AREA_ICON.get(area,"grid"),18,ACC)}</span>'
                f'<span style="font-size: 15px; font-weight: 800; letter-spacing: -.01em; flex-grow: 1;">{esc(area)}</span><span style="color:{MUTED};">›</span></a>{lis}{mais}</div>')
    from ui37 import MENU2
    cards=[]
    for nome,ic,items in MENU2:
        lis=''.join(f'<a href="{h}" style="display: block; font-size: 12.8px; color: {INK}; text-decoration: none; padding: 3px 0; font-weight: 600;">{esc(l)} ›</a>' for l,h in items) if len(items)>1 else ''
        cards.append(f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px; min-width: 0;">'
                     + (f'<a href="{items[0][1]}" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 10px;">' if len(items)==1 else '<div style="display: flex; align-items: center; gap: 10px;">')
                     + f'<span style="width: 34px; height: 34px; border-radius: 10px; background: {ACCS}; display: inline-flex; align-items: center; justify-content: center;">{icon(ic,18,ACC)}</span>'
                     + f'<span style="font-size: 15px; font-weight: 800; flex-grow: 1;">{esc(nome)}</span>' + (f'<span style="color:{MUTED};">›</span></a>' if len(items)==1 else '</div>') + f'{lis}</div>')
    ocultos=[(a['area'],[f for f,m in MAPA.items() if m['area']==a['area']]) for a in MENU]
    from ui37 import menu_item
    SAIRAM={'CF-02'}   # telas que deixaram de existir (CONF-01, CONF-D01: o bloco Alçadas fica no CF-01): sem atalho no índice
    ocultos=[(n,[f for f in fs if menu_item(ffile(f))[0] is None and f not in SAIRAM]) for n,fs in ocultos if n not in ('Cadastros',)]   # só as telas que continuam fora do menu (01/10)
    oc_html=''.join(f'<a href="{ffile(fs[0])}" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border: 1px solid {LINE}; border-radius: 999px; font-size: 12.3px; color: {INK}; text-decoration: none; background: {SURF};">{esc(n)} <span style="color: {MUTED};">{len(fs)}</span></a>' for n,fs in ocultos if fs)
    EXT=[('App móvel','MB-01',10,''),('Portal do parceiro','PT-01',7,''),('Onboarding','ON-01',1,''),('Backoffice','BO-02',2,'')]
    oc_html+=''.join(f'<a href="{fid}.dc.html" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border: 1px solid {LINE}; border-radius: 999px; font-size: 12.3px; color: {INK}; text-decoration: none; background: {SURF};">{esc(nome)} <span style="color: {MUTED};">{n}</span></a>' for nome,fid,n,ic in EXT)
    NOMENU={h:(nome if len(items)==1 else f'{nome} › {l}') for nome,ic,items in MENU2 for l,h in items}
    NOMENU.update({ffile(fs[0]):f'Módulos ocultos › {n}' for n,fs in ocultos if fs}); NOMENU.update({f'{fid}.dc.html':f'Módulos ocultos › {nome}' for nome,fid,n,ic in EXT})
    grid='<div style="display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px;">'+''.join(cards)+'</div>'
    grid+=(f'<div style="font-size: 13px; font-weight: 800; letter-spacing: .04em; color: {MUTED}; margin-top: 6px;">MÓDULOS OCULTOS DO MENU (PRESERVADOS)</div>'
           f'<div style="font-size: 12.5px; color: {MUTED};">Fora do menu por decisão de 25/09/2026; seguem no protótipo com os mesmos padrões e são alcançados por links dos processos.</div>'
           f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">{oc_html}</div>')

    def _ab(h,st): return f'<div style="{st}">' if h in NOMENU else f'<a href="{h}" style="text-decoration: none; color: inherit; {st}">'
    def _fe(h): return '</div>' if h in NOMENU else '</a>'
    perfis=''.join(_ab(h,f'display: flex; align-items: center; gap: 10px; background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px;')
        + f'<span style="width: 30px; height: 30px; border-radius: 999px; background: {ACC}; color: #fff; font-weight: 800; font-size: 13px; display: inline-flex; align-items: center; justify-content: center;">{n[0]}</span>'
        + f'<span style="display: flex; flex-direction: column; line-height: 1.25;"><b style="font-size: 13px;">{esc(n)}</b><span style="font-size: 11.5px; color: {MUTED};">{esc(d)}</span>'
        + (f'<span style="font-size: 11.5px; color: {MUTED};">começa em: {esc(NOMENU[h])}</span>' if h in NOMENU else '') + '</span>' + _fe(h) for n,d,h in PERFIS)
    cen=''.join(_ab(h,f'display: flex; align-items: center; gap: 10px; background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 9px 12px;')
        + f'{tag(c)}<span style="font-size: 12.6px; flex-grow: 1;">{esc(t)}</span>'
        + (f'<span style="font-size: 11.5px; color: {MUTED}; white-space: nowrap;">no menu: {esc(NOMENU[h])}</span>' if h in NOMENU else f'<span style="color:{MUTED};">›</span>') + _fe(h) for c,t,h in CENARIOS)
    html=f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Do Talhão à O.S. · protótipo v3.7</title><script src="./support.js"></script></head><body><x-dc><helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>body{{margin:0;font-family:{FONT};color:{INK};background:{BG}}}a{{color:{ACC}}}</style></helmet>
<div data-root="1" style="position: relative; width: {W}px; height: {H}px; box-sizing: border-box; background: {BG}; font-family: {FONT}; color: {INK}; overflow: hidden; padding: 34px 40px; display: flex; flex-direction: column; gap: 20px;">
<div style="display: flex; align-items: center; gap: 14px;">
<span style="width: 44px; height: 44px; border-radius: 13px; background: {ACC}; display: inline-flex; align-items: center; justify-content: center;">{icon("Agronomia",24,"#fff")}</span>
<div style="display: flex; flex-direction: column;"><h1 style="margin: 0; font-family: {DISP}; font-size: 26px; font-weight: 700; letter-spacing: -.02em;">Do Talhão à O.S. — protótipo navegável v3.7</h1>
<span style="font-size: 13px; color: {MUTED};">Fonte oficial: PRD v3.7 · 23/09/2026 · etapa: validação do proprietário · dados fictícios (Fazenda Santa Rita, safra 2026/27, hoje = 23/09/2026)</span></div>
<span style="flex-grow: 1;"></span>{chip('DEMONSTRAÇÃO','yellow')}{E.msgbtn('Restaurar dados iniciais','Para voltar ao cenário inicial, recarregue o Canvas: cada tela reabre com os dados de demonstração originais. Nada foi gravado fora do protótipo.')}</div>
<div style="display: grid; grid-template-columns: 1.05fr 1fr; gap: 16px;">
<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 14px 16px;"><div style="font-size: 13px; font-weight: 800; letter-spacing: .04em; color: {MUTED}; margin-bottom: 8px;">ENTRAR COMO (perfil de demonstração)</div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">{perfis}</div>
<div style="font-size: 11.5px; color: {MUTED}; margin-top: 8px;">A troca de perfil demonstra a experiência esperada; não comprova segurança real de acesso.</div>
<div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid {LINE}; display: flex; flex-direction: column; gap: 8px;">
<div style="font-size: 13px; font-weight: 800; letter-spacing: .04em; color: {MUTED};">COMO VALIDAR</div>
<div style="font-size: 13px; line-height: 1.5;"><b>1.</b> Escolha um perfil e abra pelo menu abaixo a tela em que ele começa.</div>
<div style="font-size: 13px; line-height: 1.5;"><b>2.</b> Rode os cenários prontos: cada processo mostra a faixa de etapas no topo; clique nas linhas das tabelas para editar.</div>
<div style="font-size: 13px; line-height: 1.5;"><b>3.</b> Para pedir ajuste, comente no próprio quadro citando o código da tela no título (ex.: <b>IN-04</b>) e o que esperava ver.</div>
</div></div>
<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 14px 16px;"><div style="font-size: 13px; font-weight: 800; letter-spacing: .04em; color: {MUTED}; margin-bottom: 8px;">CENÁRIOS PRONTOS</div><div style="display: flex; flex-direction: column; gap: 6px;">{cen}</div></div>
</div>
<div style="font-size: 13px; font-weight: 800; letter-spacing: .04em; color: {MUTED};">MENU DO SISTEMA</div>
{grid}
<div style="font-size: 12px; color: {MUTED};">Integrações, telemetria, IA, pagamentos, laboratório, satélite e arquivos de máquina usam respostas simuladas identificadas. Estado navegado persiste dentro de cada tela; ao recarregar o Canvas os dados voltam ao cenário inicial.</div>
</div></x-dc><script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
__ENGINE__
</script></body></html>'''
    # sem widgets dinâmicos nesta tela: escreve direto
    E._reset_screen(fname)
    open(os.path.join(E.P,fname),'w').write(html.replace('__ENGINE__',E.engine()))
