# -*- coding: utf-8 -*-
"""Área App móvel (módulo OCULTO do menu, preservado) — MB-01 Hoje no campo · MB-02 Minhas ordens · MB-03 Apontamento ·
MB-04 Ocorrência · MB-05 Almoxarifado móvel · MB-06 Vistoria · MB-07 Contagem de frutos · MB-08 Irrigação móvel ·
MB-09 Manutenção e combustível · MB-10 Cargas e entregas. Telas 390 px via mobile37().
Padrão novo (25/09/2026): descrição curta no imperativo sob cada bloco; ações secundárias com ícone + rótulo + title;
sem faixa de etapas (módulo não sequencial). O app não tem tabelas: cada cartão é um registro e abre o seu formulário/detalhe.
Regra da tela móvel: a única ação primária é o botão grande do rodapé; botões dentro do corpo são secundários.
Ações que mudam estado (sincronizar, reconhecer, confirmar, pesar) alteram a própria tela — selo, contador e botão primário.

App de campo ligado ao cenário compartilhado (v3.9, 26/09/2026) — MB-01, MB-02, MB-02det, MB-03, MB-03x-recibo, MB-04 e MB-05:
- EXTRAJS[0] = cenario.js_prefixo() + JS do app (prefixo mb*); cada tela chama cenOuvir(self), lê cenGet() e muda só por cenMudar.
- Operador = c.app.operador (Marcos). Minha fila = ordens dele Liberadas ou Em execução, na ordem da janela (dados.ORDEM).
- Próximo passo por ordem: Fechar turno (turno aberto) › Confirmar recebimento (entregue por Rui) › sem área a fazer (saldo menos os
  hectares no aparelho = 0): Ver envios / Devolver sobra / aguardar encerramento › Retirar no almoxarifado (reservado, nada entregue)
  › Fechar turno · <outra ordem> (turno aberto em outra) › Iniciar turno. O botão do rodapé leva ao passo mais urgente.
- Guardas do app (26/09): mbIniciar recusa ordem sem saldo; mbDescartar solta turno aberto numa ordem sem saldo; o limite de hectares
  do MB-03 desconta os turnos no aparelho; insumo fora da requisição não é pré-calculado nem baixado. Listas com teto (quadro de altura fixa).
- Sem sinal (cenSinal): tudo vai para a fila do aparelho; ao voltar o sinal a fila é enviada uma vez só e o app guarda o recibo
  (mbSinal: c.app.recibos, REC-7742 em diante; REC-7741 = APT-1187, dia 4 da OS-0421, já confirmado).
- Fechar o turno (cenFecharTurno) não encerra a O.S.; erro junto ao campo só para área acima do saldo. Consumo informado acima do que está
  com você não é recusado (RN-018; CONC-07): aviso no campo, o fato fica Em conferência sem baixa; Rui (almoxarife) confere e Ana (gestora) aceita o excedente no Estoque.
  A sugestão dose × área não editada é estimativa (CONC-13): acima do que está com você, o campo pede quanto foi usado (nada abre sozinho).
- Apontamento único (CTL-2 · AP-ÚNICO): o turno grava pelo mesmo comando da web (cenApontar), com a data operacional e a chave do turno;
  o mesmo dia já apontado pela web fica "Em conferência · duplicidade", sem soma nem baixa, até Paula (conferência) decidir.
- MB-05det..MB-10det seguem com dados locais (abaixo) e a regra de irrigação já aplicada (MB-08).

observacoes (dados locais coerentes com dados.py / dados2.py / telas vizinhas):
- OS-0421: equipe Marcos · Pulverizador PJ-3030 + Trator 03 (campo.py); janela da ordem 20–26/09 (processo_os.JANELA).
- OS-0420: 30/100 ha (18 conferidos + 12 provisórios) na v2; saldo de 70 ha na v3 (KCl −12 % só no saldo), ajustada por Ana (agrônoma)
  em 23/09 e já em vigor; o saldo está parado só pelo Trator T1 (OM-0233) — mesmo recorte de campo.py/processo_os.py (não 60/40).
  Fichas do saldo revogadas em 23/09 08:05 pelo ajuste da v3; ciência CI-0931.
- OS-0418 no pacote offline: autorização de água revogada no servidor em 23/09 07:15 (reclassificada para fertirrigação, v2 a liberar por Ana);
  relato local de 07:40 ("pivô 1 ligado 20 min para teste de pressão") fica como relato fora da autorização, aguardando decisão.
- OS-0419 = irrigacao.py: 1 volta a 62 % ≈ 14,5 h · janela hoje 20:00–amanhã 10:31, início 20:02, término amanhã 10:33; andamento
  de 2,1 h ≈ 14,47 % (≈11,6 ha). Recibos AU-3098 · LIB-2287 · EX-5120; conferência 10,6 mm medidos × 10,81 mm estimados nos 80 ha
  (−1,9 %, tolerância 3 %). Bomba B2 166 L/s.
  Próximo ciclo = OS-0422 (13,5 mm em 2 passadas de 6,75 mm · janela a definir), sem aprovação do agrônomo.
- Almoxarife (aba de MB-05) = dados2: REQ-031 (MAP 100/70/20/10 sc, custódia de Paula; sobras vão ao lote M26-05 de suprimentos.py),
  REQ-038 (OS-0418, Ureia 45 % 1.140 kg, aguardando liberação; estoque apto 0 kg), conflito F26-02 rebaseado como em suprimentos.py
  (545 L físicos, 65 L reservados à OS-0424, 480 L livres); o uso da safra e a pendência na SOL-2026-07 vêm de dados2.demanda (CTL-4: com as
  O.S. na demanda, o Fungicida A não tem pendência e o cartão sai do vermelho).
- DEMO-20: Balança/Recebedor usam a carga CG-1207 da colheita.py (OC-0510 · talhão T7 · Carreta 03 · 4.310 − 1.180 = 3.130 kg ·
  ROM-0791 · Packing Sede · chegada a confirmar). Motorista = caminhão T1 da logistica.py (VD-2101 1ª de 3, janela 08:00,
  previsão 09:10 informada às 07:40, posição 4 ao chegar). Carga 07 = PV-034 · CD Horti · 9,6 t · dono Sandra (fiscal) · prazo 10:00.
- DEMO-06: a contagem de frutos vem da previsão T7 · S39 (v S39-02), que abastece o PV-031 (10,0 t classe A) — colheita.py.
"""
import json, os, re
from engine import (chip,tag,esc,icon,prazo,mfield,BTN_ST,EXTRAJS,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAY,GRAYS,SH,DISP)
import engine as E
from ui37 import mobile37, HEIGHTS37, selo, etapa, ETAPA_COR
import dados as D
import dados2 as D2
import dados_irrigacao as _DI   # equipamento do setor (nome e vazão do cadastro e da ficha do pivô)
import cenario
import dados_manutencao as DM   # regras da manutenção sobre o cenário único (PCM S4: MB-01, MB-04, MB-09, MB-09det)

H=lambda s: '{{'+s+'}}'
T=lambda: H('true'); F=lambda: H('false')
def IF(h,body,d=False): return f'<sc-if value="{H(h)}" hint-placeholder-val="{H("true" if d else "false")}">{body}</sc-if>'
def br(x): return str(x).replace('.',',')
def nf(n,d=0): return f'{n:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')

# ---------- dados locais (números que só o app usa; coerentes com dados.py/dados2.py) ----------
O421,O420,O419=D.OS[0],D.OS[1],D.OS[2]
APT=dict(id='APT-1187', os='OS-0421', dia=4, ha=O421['dias'][3], recibo='REC-7741', uuid='c9e2-…-4f1a')
REQ=next(r for r in D2.REQUISICOES if r['id']=='REQ-031')
R38=next(r for r in D2.REQUISICOES if r['id']=='REQ-038')
F02=next(l for l in D2.LOTES if l['lote']=='F26-02')
F02_LIVRE=F02['fisico']-F02['quarentena']-F02['reservado']                            # 480 L

EQ421='Marcos · Pulverizador PJ-3030 + Trator 03'
CALDA=dict(litros='2.000', vazao='120 L/ha', dose='0,5 L/ha de Fungicida A', cobre='16,7 ha', por_tanque='8,3 L')
P,POL=D.PIVO,D.POLITICA_AGUA
AREA_PIVO=80; AREA_COB=round(AREA_PIVO*P['cobertura_pct']/100,1); AREA_RESTO=round(AREA_PIVO-AREA_COB,1)   # ≈11,6 · ≈68,4 ha
IRR=dict(janela='20:00–amanhã 10:31', ini='20:02', fim='amanhã 10:33', fim_d='24/09 10:33', dur='14,5 h', au='AU-3098', lib='LIB-2287', ex='EX-5120', medido='10,6', dif='−1,9%')
VIST=dict(rota='Rota W · P1 (Feijão · R5)', alvo='Percevejo-marrom', metodo='Pano de batida · insetos/pano', contagem='3,2', nc='4,5', total=14)
FRUTO=dict(parcela='T7-B · Mamão Formosa', total=40, verdes=46, inchados=12, maduros=5,
           amostra='40 de 3.600 plantas (1,1%)', peso='1,9 kg médio · 12 frutos')
CG=dict(id='CG-1207', oc='OC-0510', veic='Carreta 03', bruto='4.310 kg', tara='1.180 kg', liq='3.130 kg', rom='ROM-0791',
        origem='talhão T7 · Mamão Formosa', destino='Packing Sede', hora='09:40', acum='9,3 de 12,0 t', saldo='2,7 t')
VIAGEM=dict(veic='caminhão T1', pedido='VD-2101 · 1ª de 3', produto='Milho a granel · 37,00 t', rota='Silo Sede → Cooperativa Central',
            janela='08:00–09:00', prev='09:10 (informada às 07:40)', pos='4ª ao chegar')
C07=dict(id='Carga 07', pedido='PV-034', cliente='CD Horti', produto='Mamão Formosa classe A · 9,6 t', dono='Sandra (fiscal)', prazo='hoje 10:00')

# ---------- helpers locais de apresentação ----------
DOT={'green':ACC,'yellow':YEL,'red':RED,'gray':GRAY,'blue':'#1E88E5'}
def h2(t,desc=''):
    if '{{' not in str(desc): desc=''   # 14/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos titulos e os demais soltos pela tela ... somos minimalistas e essencialistas"): só fica a descrição que mostra estado (buraco dinâmico)
    s=f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: 2px;">{esc(desc)}</div>' if desc else ''
    return f'<div><div style="font-family: {DISP}; font-size: 15px; font-weight: 700; letter-spacing: -.01em;">{esc(t)}</div>{s}</div>'
def h2v(t,desc):
    """h2 com texto do estado (revisão CONF F14: o almoxarife vem do papel, não de nome fixo): argumento que começa por al_ é chave de v."""
    x=lambda a: H(a) if a.startswith('al_') else esc(a)
    d=f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: 2px;">{x(desc)}</div>' if desc.startswith('al_') else ''   # 14/10/2026: sem descrição fixa
    return f'<div><div style="font-family: {DISP}; font-size: 15px; font-weight: 700; letter-spacing: -.01em;">{x(t)}</div>{d}</div>'
CARD_ST=f'background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 13px 15px; display: flex; flex-direction: column; gap: 7px; min-width: 0;'
def card(title,rows,state='gray',desc='',head_right=''):
    if '{{' not in str(desc): desc=''   # 14/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos titulos e os demais soltos pela tela ... somos minimalistas e essencialistas")
    d=f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">{esc(desc)}</div>' if desc else ''
    body=''.join(f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{r}</div>' for r in rows)
    return (f'<div style="{CARD_ST}">'
            f'<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {DOT[state]}; flex-shrink: 0;"></span>'
            f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;">{title}</div>{head_right}</div>{d}{body}</div>')
def kv(label,val): return f'<span style="font-weight: 600; color: {INK};">{esc(label)}:</span> {val}'
def chips(*cs): return '<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">'+''.join(cs)+'</div>'
def btns(*bs): return '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'+''.join(bs)+'</div>'
def note(txt,color=None): return f'<div style="font-size: 12px; color: {color or MUTED}; line-height: 1.5;">{txt}</div>'
def dchip(k): return f'<span style="{H(k+"_st")}"><span style="{H(k+"_dot")}"></span>{H(k+"_t")}</span>'
def hchip(a): return f'<span style="{H(a+"_st")}"><span style="{H(a+"_dot")}"></span>{H(a+"_t")}</span>'
def navcard(lbl,sub,fid,ic):
    return (f'<a href="{fid}.dc.html" title="Abrir {esc(lbl)}" style="text-decoration: none; color: inherit; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 11px 12px; display: flex; gap: 9px; align-items: flex-start;">'
            f'<span style="color: {ACC}; margin-top: 1px;">{icon(ic,16)}</span><span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">'
            f'<span style="font-size: 13px; font-weight: 700;">{esc(lbl)}</span><span style="font-size: 11.5px; color: {MUTED};">{esc(sub)}</span></span></a>')
def grid2(*cells): return '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">'+''.join(cells)+'</div>'
def counter(lbl,val):
    return (f'<div style="flex: 1 1 0; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 10px; text-align: center;">'
            f'<div style="font-family: {DISP}; font-size: 20px; font-weight: 700;">{val}</div><div style="font-size: 11px; font-weight: 700; letter-spacing: .05em; color: {MUTED};">{esc(lbl)}</div></div>')
def counters(*cs): return '<div style="display: flex; gap: 8px;">'+''.join(counter(l,v) for l,v in cs)+'</div>'
def mcont(veio,aqui,falta,proxima):
    """Faixa de continuidade (cap. 4.2) em 2×2 para 390 px — o texto quebra linha em vez de ser cortado."""
    def cell(lbl,val,strong=False):
        return (f'<div style="display: flex; flex-direction: column; gap: 1px; min-width: 0;">'
                f'<span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{lbl}</span>'
                f'<span style="font-size: 12.5px; line-height: 1.3; font-weight: {700 if strong else 600}; color: {ACC if strong else INK};">{val}</span></div>')
    return (f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; padding: 10px 14px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px;">'
            + cell('VEIO DE',veio)+cell('ESTÁ AQUI',f'<b>{aqui}</b>')+cell('FALTA',falta)+cell('PRÓXIMA AÇÃO',proxima,strong=True)+'</div>')
def vstep(steps,hint):
    """Etapas em coluna (a régua horizontal não cabe em 390 px)."""
    rows=''
    for name,st in steps:
        if st=='done':
            dot=f'<span style="width: 20px; height: 20px; border-radius: 999px; background: {ACC}; color: #fff; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 12px; font-weight: 800;">✓</span>'
        elif st=='now':
            dot=f'<span style="width: 20px; height: 20px; border-radius: 999px; border: 2px solid {ACC}; box-sizing: border-box; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;"><span style="width: 8px; height: 8px; border-radius: 999px; background: {ACC};"></span></span>'
        else:
            dot=f'<span style="width: 20px; height: 20px; border-radius: 999px; border: 2px solid {LINE}; box-sizing: border-box; display: inline-block; flex-shrink: 0;"></span>'
        rows+=(f'<div style="display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: {700 if st=="now" else 600}; color: {MUTED if st=="todo" else INK};">{dot}<span>{esc(name)}</span></div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 7px; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 12px 14px;">{rows}'
            + (f'<div style="font-size: 12px; color: {MUTED}; line-height: 1.45; margin-top: 2px;">{esc(hint)}</div>' if hint else '') + '</div>')   # 14/10/2026: a regra vai para a dica ⓘ da tela

# ---------- ações (ícone + rótulo + title) e JS da tela ----------
MS={}
_BST=BTN_ST(False,True)+' display: inline-flex; align-items: center; gap: 6px;'
_NXST=_BST.replace(f'background: {SURF}; color: {INK}; border: 1px solid {LINE};',f'background: {ACCS}; color: {ACC}; border: 1px solid {ACC};')
def _b(label,hole,ic,title):
    return f'<button type="button" onClick="{H(hole)}" title="{esc(title or label)}" style="{_BST}">{icon(ic,14) if ic else ""}{esc(label)}</button>'
def say(label,msg,ic,title=None):
    """ação que responde na própria tela (aviso com o efeito real ou o motivo do bloqueio)."""
    k='m%d'%len(MS); MS[k]=msg; return _b(label,'say_'+k,ic,title)
def fnb(label,fn,ic,title=None):
    """ação com efeito de estado (função no JS da tela)."""
    return _b(label,fn,ic,title)
def lnk(label,href,ic,title=None):
    return (f'<a href="{href}" title="{esc(title or label)}" style="{_BST} text-decoration: none;">{icon(ic,14) if ic else ""}{esc(label)}</a>')
JS_BASE=('const MBC={green:["%s","%s"],yellow:["%s","%s"],red:["%s","%s"],gray:["%s","%s"]};\n' % (ACC,ACCS,YEL,YELS,RED,REDS,GRAY,GRAYS)) + r'''
function mbChs(c){ const k=MBC[c]||MBC.gray; return 'display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; color: '+k[0]+'; background: '+k[1]+'; white-space: nowrap;'; }
function mbDot(c){ const k=MBC[c]||MBC.gray; return 'width: 6px; height: 6px; border-radius: 999px; background: '+k[0]+';'; }
function DCH(v,k,t,c){ v[k+'_t']=t; v[k+'_st']=mbChs(c); v[k+'_dot']=mbDot(c); }
function TOAST(self,t){ self.setState({g2toast:t}); }
function SAY(self,v,M){ Object.keys(M).forEach(k=>{ v['say_'+k]=()=>TOAST(self,M[k]); }); }
'''

# ---------- app de campo × cenário compartilhado (funções mb*: só leem o cenário ou mudam por cenMudar) ----------
def _jk(j):
    m=re.search(r'(\d{1,2})(?:–\d{1,2})?/(\d{2})',j or '')
    return int(m.group(2))*100+int(m.group(1)) if m else 9999
MBJAN={k:dict(j=o.get('janela') or 'a definir',k=_jk(o.get('janela'))) for k,o in D.ORDEM.items()}
MBAPP_JS=('const MBJAN = '+json.dumps(MBJAN,ensure_ascii=False)+';\nconst MB_ETAPA_COR = '+json.dumps(ETAPA_COR,ensure_ascii=False)
          +';\nconst MBTX = {ink:"%s",muted:"%s",surf:"%s",line:"%s",acc:"%s",accs:"%s",yel:"%s",yels:"%s"};\n' % (INK,MUTED,SURF,LINE,ACC,ACCS,YEL,YELS)) + r'''
// Gancho de teste/inspeção: o script da tela roda isolado (new Function); os testes app_* usam a mesma API do cenário por aqui.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenConfirmarRecebimento, cenIniciarTurno, cenFecharTurno, cenOcorrencia, cenSinal, cenPodeEncerrar, cenConciliar, cenApontar }; window.__mb = { mbIniciar, mbDescartar, mbResta }; } catch (e) {}
const MB_SEL_KEY = 'talhao-os-mb-os';   // ordem aberta no detalhe (conveniência do aparelho; o cenário não muda)
function mbSelGet(){ try { return localStorage.getItem(MB_SEL_KEY) || ''; } catch (e) { return ''; } }
function mbSelSet(id){ try { localStorage.setItem(MB_SEL_KEY, id || ''); } catch (e) {} }
function mbNum(s){ if (s === null || s === undefined) return NaN; let t = String(s).trim(); if (!t) return NaN; if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.'); return Number(t); }
function mbIn(n){ return String(Math.round(n * 100) / 100).replace('.', ','); }
function mbK(o){ return (MBJAN[o.id] || { k: 9999 }).k; }
function mbJan(o){ return (MBJAN[o.id] || {}).j || 'a definir'; }
// colheita (D-16): a O.S. de colheita não entra na fila do MB-02/MB-03; a área de colheita no app é só pelo MB-10 (cenApDup não compara app × app do mesmo operador)
function mbMinhas(c){ return Object.values(c.ordens).filter(o => o.resp === c.app.operador && !/^Colheita/.test(String(o.tipo || ''))).sort((a, b) => mbK(a) - mbK(b) || a.id.localeCompare(b.id)); }
function mbFila(c){ return mbMinhas(c).filter(o => o.etapa === 'Liberadas' || o.etapa === 'Em execução'); }
function mbReq(c, o){ return (o && o.req && c.reqs[o.req]) || null; }
function mbProv(o){ return (o.ap || []).filter(a => a.sinc === false).reduce((s, a) => s + (a.ha || 0), 0); }
function mbTurno(c){ const t = c.app.turno; return t && !t.fim ? t : null; }
function mbPausado(t){ const p = t && t.pausas[t.pausas.length - 1]; return !!(p && !p.fim); }
function mbRealTxt(o){ const p = mbProv(o); return 'Realizado ' + cenNum(o.realizado, 1) + ' de ' + cenNum(o.area, 1) + ' ha · saldo ' + cenNum(o.saldo, 1) + ' ha' + (p ? ' · +' + cenNum(p, 1) + ' ha no aparelho, aguardando sinal' : ''); }
function mbTx(c){ return 'font-weight: 700; color: ' + (MBC[c] || MBC.gray)[0] + ';'; }
function mbEmb(i, q){ const m = String(i.emb || '').match(/([\d.]+(?:,\d+)?)\s*(L|kg)\b/); if (!m) return i.emb || ''; const sz = Number(m[1].replace(/\./g, '').replace(',', '.')); return sz > 0 ? Math.ceil(q / sz - 1e-9) + ' × ' + i.emb : i.emb; }
// Área que ainda cabe em turnos: saldo do servidor menos os hectares que já estão no aparelho (aguardando sinal).
function mbResta(o){ return Math.max(0, (o.saldo || 0) - mbProv(o)); }
// consumo relatado em conferência (CONC-07): o item não é sobra a devolver enquanto o almoxarife não concilia
function mbConf(c, os, prod){ return cenConfAbertas(c, os).find(k => !prod || k.prod === prod) || null; }
function mbSobra(c, o){ const r = mbReq(c, o); return r ? r.itens.filter(i => i.custodia > 0.001 && !mbConf(c, o.id, i.prod)) : []; }
function mbSobraTxt(l){ return l.map(i => i.prod + ' ' + cenNum(i.custodia) + ' ' + i.un).join(', '); }
// Iniciar turno só com área a fazer (o cenário não confere o saldo; sem esta guarda o turno abre e não fecha).
function mbIniciar(c, id){ const o = c.ordens[id]; if (o && mbResta(o) <= 0.001) throw new Error('A ' + id + ' não tem área a fazer (saldo 0 ha). Nada a iniciar.'); return cenIniciarTurno(c, id); }
// Turno aberto numa ordem sem saldo (estado antigo ou aberto fora do app): descarta sem apontamento para não prender o operador.
function mbDescartar(c){ cenAppAtivo(c); const t = c.app.turno; if (!t || t.fim) throw new Error('Nenhum turno aberto.'); c.app.turno = null; return { msg: 'Turno da ' + t.os + ' descartado sem apontamento: a ordem não tem saldo.' }; }
// Próximo passo da ordem na fila (verbo + objeto) e o selo de estado que o justifica.
function mbPasso(c, o){
  if (o.etapa !== 'Liberadas' && o.etapa !== 'Em execução') return { k: 'none', t: '', chip: [o.etapa === 'A liberar' ? 'Aguarda liberação no escritório' : 'Fora da fila', 'gray'], cor: 'gray', tt: '' };
  const t = mbTurno(c);
  if (t && t.os === o.id) { const pz = mbPausado(t); return { k: 'fechar', t: 'Fechar turno', chip: [pz ? 'Turno pausado' : 'Turno aberto · desde ' + t.ini, pz ? 'yellow' : 'green'], cor: 'green', href: 'MB-03.dc.html', tt: 'Fechar o turno da ' + o.id + ' com hectares, horas e consumo' }; }
  const r = mbReq(c, o);
  if (r && r.itens.some(i => i.custodia > 0 && !i.confirmado)) return { k: 'confirmar', t: 'Confirmar recebimento', chip: ['Entregue por ' + (cenEntPor(c, r.id) || 'almoxarifado') + ' · ' + r.id, 'yellow'], cor: 'yellow', href: 'MB-05.dc.html#' + o.id, tt: 'Conferir itens, lote e embalagem e confirmar o recebimento da ' + r.id };
  if (mbResta(o) <= 0.001) {
    if (mbProv(o) > 0) return { k: 'enviar', t: 'Ver envios', chip: ['Área feita · aguardando sinal', 'yellow'], cor: 'yellow', href: 'MB-03x-recibo.dc.html', tt: 'Ver os turnos da ' + o.id + ' que estão no aparelho' };
    const sb = mbSobra(c, o);
    if (sb.length) return { k: 'devolver', t: 'Devolver sobra', chip: ['Área feita · sobra com você', 'yellow'], cor: 'yellow', href: 'MB-05.dc.html#' + o.id, tt: 'Levar ' + cenAoAlmox() + ' a sobra da ' + o.id + ': ' + mbSobraTxt(sb) };
    if (mbConf(c, o.id)) return { k: 'none', t: '', chip: ['Consumo em conferência · ' + CEN_CONC_RESP(), 'yellow'], cor: 'yellow', tt: '', feita: true };
    return { k: 'none', t: '', chip: ['Área feita · aguarda encerramento', 'green'], cor: 'green', tt: '', feita: true };
  }
  const f = cenIniFalta(o, r);   // regra única de início (cenario.js): a mesma da web e do comando
  if (f && f.k === 'rever') return { k: 'rever', t: '', chip: ['Insumo esgotado · ' + g2alcQuem('AL-02'), 'red'], cor: 'red', tt: f.t + ' ' + f.q };
  if (f && f.k === 'entregar') return { k: 'retirar', t: 'Retirar no almoxarifado', chip: [(r.itens.some(i => i.entregue > 0) ? 'Entrega parcial' : 'Reservado') + ' · ' + r.id, 'gray'], cor: 'gray', href: 'MB-05.dc.html#' + o.id, tt: 'Ver o que retirar com ' + (cenAlmoxNome() || 'o almoxarife') + ' no almoxarifado para a ' + o.id };
  if (t) return { k: 'outro', t: 'Fechar turno · ' + t.os, chip: ['Outro turno aberto · ' + t.os, 'yellow'], cor: 'yellow', href: 'MB-03.dc.html', tt: 'Fechar o turno aberto da ' + t.os + ' antes de iniciar a ' + o.id };
  return { k: 'iniciar', t: 'Iniciar turno', chip: [o.etapa === 'Em execução' ? 'Pronta para o próximo turno' : 'Pronta para iniciar', 'green'], cor: 'green',
           fn: (self) => cenMudar(self, c => mbIniciar(c, o.id)), tt: 'Iniciar turno na ' + o.id };
}
// Insumos da ordem: a retirar, entregues a confirmar, com o operador (custódia) ou já consumidos.
function mbIns(c, o){ const r = mbReq(c, o); if (!r) return [];
  return r.itens.map(i => { const L = i.prod + ' · lote ' + i.lote + (i.emb ? ' · ' + i.emb : ''); const k = mbConf(c, o.id, i.prod);
    if (k) return { t: L, s: 'em conferência · relatado ' + cenNum(k.relatado) + ' ' + k.un + ' · com você ' + cenNum(i.custodia) + ' ' + i.un, st: mbTx('yellow') };
    if (i.custodia > 0 && !i.confirmado) return { t: L, s: 'entregue ' + cenNum(i.custodia) + ' ' + i.un + ' · a confirmar', st: mbTx('yellow') };
    if (i.custodia > 0) return { t: L, s: 'com você ' + cenNum(i.custodia) + ' ' + i.un, st: mbTx('green') };
    const sal = cenSaldoEntregar(i); if (sal > 0) return { t: L, s: 'retirar ' + cenNum(sal) + ' ' + i.un, st: mbTx('gray') };
    return { t: L, s: 'consumido ' + cenNum(i.consumido) + ' ' + i.un, st: mbTx('gray') }; }); }
function mbCard(self, c, o){ const p = mbPasso(c, o); const ec = MB_ETAPA_COR[o.etapa] || 'gray'; const ins = mbIns(c, o);
  return { id: o.id, tipo: o.tipo, loc: o.talhao + ' · ' + cenNum(o.area, 1) + ' ha · janela ' + mbJan(o), real: mbRealTxt(o),
    e_t: o.etapa, e_st: mbChs(ec), e_dot: mbDot(ec), p_t: p.chip[0], p_st: mbChs(p.chip[1]), p_dot: mbDot(p.chip[1]),
    dot: 'width: 10px; height: 10px; border-radius: 999px; flex-shrink: 0; background: ' + (MBC[p.cor] || MBC.gray)[0] + ';',
    ins: ins, hasIns: ins.length > 0, nx_isA: !!p.href, nx_isB: !!p.fn, nx_t: p.t, nx_href: p.href || 'MB-01.dc.html', nx_tt: p.tt || '',
    nx_fn: () => { mbSelSet(o.id); if (p.fn) p.fn(self); }, sel: () => mbSelSet(o.id), ab_tt: 'Abrir a ' + o.id + ' · instrução, insumos e apontamentos' }; }
// Passo mais urgente de toda a fila (botão do rodapé).
function mbPrim(c, fila){ const t = mbTurno(c); if (t) return { k: 'fechar', o: c.ordens[t.os], lab: 'Fechar turno · ' + t.os, href: 'MB-03.dc.html' };
  for (const k of ['confirmar', 'iniciar', 'retirar', 'devolver']) { const o = fila.find(x => mbPasso(c, x).k === k); if (o) { const p = mbPasso(c, o); return { k, o, lab: p.t + ' · ' + o.id, href: p.href || '' }; } }
  return { k: 'none', o: null, lab: 'Ver minhas ordens' }; }
function mbDesc(c, k){
  if (k.indexOf('MAN|') === 0) { const q = manAppFila(c).find(x => 'MAN|' + x.chave === k); return q ? q.desc : 'Registro da manutenção'; }
  if (k.indexOf('AP|') === 0) { const [, id, dia] = k.split('|'); const o = c.ordens[id]; const a = o && (o.ap || []).find(x => String(x.dia) === dia);
    return 'Apontamento ' + id + ' · dia ' + dia + (a ? ' · ' + cenNum(a.ha, 1) + ' ha' + (a.h ? ' em ' + cenNum(a.h, 1) + ' h' : '') + (a.conf ? ' · consumo em conferência' : '') : ''); }
  const oc = (c.ocorr || []).find(x => x.id === k); if (oc) return 'Ocorrência ' + oc.id + ' · ' + oc.os + ' · ' + oc.tipo;
  const m = (c.movs || []).find(x => x.id === k); if (m) return m.tipo === 'recebimento' ? 'Recebimento confirmado · ' + m.req + ' · ' + m.os : m.tipo + ' · ' + (m.os || '');
  return k; }
// Sinal: usa cenSinal (envia a fila uma vez só) e guarda o recibo do envio; o movimento de consumo segue o apontamento enviado.
function mbSinal(c, on){ const fila = (c.app.fila || []).slice(); const itens = fila.map(k => mbDesc(c, k));
  // manutenção (PCM S4): a fila do aparelho vai uma vez só; OM mudada no escritório vira conflito para o Otávio (nada aplicado em silêncio)
  const mm = (on && manAppFila(c).length) ? (c.app.online = true, manAppSinal(c)) : null; const r = cenSinal(c, on);
  if (mm) { const pt = []; if (mm.n) pt.push(mm.n + (mm.n > 1 ? ' registros da manutenção enviados' : ' registro da manutenção enviado'));
    if (mm.conf.length) pt.push(mm.conf.length + (mm.conf.length > 1 ? ' conflitos a resolver' : ' conflito a resolver') + ' · Otávio (a ordem mudou no escritório; nada foi aplicado em silêncio)');
    if (pt.length) r.msg = pt.join(' · ') + (/^Sinal de volta\. Nada pendente\./.test(r.msg) ? '.' : ' · ' + r.msg); }
  if (on && fila.length) { (c.movs || []).forEach(m => { if (m.origem === 'app' && m.tipo === 'consumo' && m.sinc === false) m.sinc = true; });
    c.app.recibos = c.app.recibos || []; const id = 'REC-' + (7742 + c.app.recibos.length); c.app.recibos.push({ id, at: cenAgora(), n: fila.length, itens });
    r.msg = r.msg.replace(/\.$/, '') + ' · recibo ' + id + ' · cada registro entrou uma vez.'; }
  return r; }
function mbSeg(on, warn){ return 'font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 12px; border-radius: 999px; border: 0; cursor: pointer; white-space: nowrap; '
  + (on ? (warn ? 'background: ' + MBTX.yels + '; color: ' + MBTX.yel + ';' : 'background: ' + MBTX.surf + '; color: ' + MBTX.ink + '; box-shadow: 0 1px 2px rgba(21,32,26,.12);') : 'background: transparent; color: ' + MBTX.muted + ';'); }
function mbPill(on){ return 'font-family: inherit; font-size: 13px; font-weight: 700; padding: 7px 12px; border-radius: 999px; cursor: pointer; white-space: nowrap; border: 1px solid ' + (on ? MBTX.acc : MBTX.line) + '; background: ' + (on ? MBTX.accs : MBTX.surf) + '; color: ' + (on ? MBTX.acc : MBTX.ink) + ';'; }
// Barra de sinal (todas as telas do app ligadas ao cenário): alternador, contador e último recibo.
function mbSig(self, v, c){ const on = cenOnline(c); const n = (c.app.fila || []).length;
  v.sg_on = on; v.sg_off = !on; v.sg_st1 = mbSeg(on, false); v.sg_st0 = mbSeg(!on, true);
  v.sg_t = n ? n + (n > 1 ? ' registros aguardando sinal' : ' registro aguardando sinal') : 'Nada aguardando sinal';
  v.sg_tst = 'font-size: 12.5px; font-weight: 700; color: ' + (n ? MBTX.yel : MBTX.muted) + ';';
  const rc = (c.app.recibos || []).slice(-1)[0]; v.sg_rec = !!rc; v.sg_rect = rc ? 'Último envio ' + rc.at + ' · ' + rc.n + (rc.n > 1 ? ' registros' : ' registro') + ' · recibo ' + rc.id : '';
  v.sg_com = () => { if (cenOnline(cenGet())) return TOAST(self, 'Já está com sinal · nada aguardando envio.'); cenMudar(self, c => mbSinal(c, true)); };
  v.sg_sem = () => { if (!cenOnline(cenGet())) return TOAST(self, 'Já está sem sinal · os registros ficam no aparelho.'); cenMudar(self, c => mbSinal(c, false)); };
}
'''
def sigbar(envios=True):
    """Alternador Com sinal / Sem sinal + contador de registros no aparelho + último recibo (cenSinal).
    envios=False na própria tela de envios (MB-03x-recibo): sem link para si mesma nem a linha do último recibo (a tela lista os recibos)."""
    row2=(f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; color: {MUTED};">'
          + IF('sg_rec',f'<span>{H("sg_rect")}</span>')
          + f'<a href="MB-03x-recibo.dc.html" title="Abrir envios e recibos do aparelho" style="color: {ACC}; font-weight: 700; text-decoration: none;">Ver envios</a></div>') if envios else ''
    return (f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 8px 10px; border-radius: 12px; background: {SURF}; border: 1px solid {LINE};">'
            f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
            f'<span role="group" aria-label="Sinal do aparelho (simulação)" style="display: inline-flex; padding: 2px; border-radius: 999px; background: {GRAYS}; gap: 2px;">'
            f'<button type="button" aria-pressed="{H("sg_on")}" onClick="{H("sg_com")}" title="Simular aparelho com sinal: envia o que está no aparelho" style="{H("sg_st1")}">Com sinal</button>'
            f'<button type="button" aria-pressed="{H("sg_off")}" onClick="{H("sg_sem")}" title="Simular aparelho sem sinal: registros ficam no aparelho" style="{H("sg_st0")}">Sem sinal</button></span>'
            f'<span aria-live="polite" style="{H("sg_tst")}">{H("sg_t")}</span></div>'
            + row2 + '</div>')
def pills(lst,label,count=3,a='o'):
    """Lista curta em pílulas (um toque), com aria-pressed."""
    return (f'<div role="group" aria-label="{esc(label)}" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="{count}">'
            f'<button type="button" aria-pressed="{H(a+".on")}" onClick="{H(a+".fn")}" title="{H(a+".tt")}" style="{H(a+".st")}">{H(a+".t")}</button></sc-for></div>')
def lab(t): return f'<span style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(t)}</span>'
def omcards(lst,a='m',count=1):
    """Cartões das OMs na Minha fila do mecânico: etapa + passo, tarefas e o próximo passo com verbo (PCM S4)."""
    return (f'<sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="{count}"><div style="{CARD_ST}">'
            f'<div style="display: flex; align-items: center; gap: 8px;"><span style="{H(a+".dot")}"></span><div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;"><b>{H(a+".id")}</b> · {H(a+".tit")}</div></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(a+".loc")}</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;"><span style="{H(a+".e_st")}"><span style="{H(a+".e_dot")}"></span>{H(a+".e_t")}</span>'
            f'<span style="{H(a+".p_st")}"><span style="{H(a+".p_dot")}"></span>{H(a+".p_t")}</span></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(a+".real")}</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
            + IF(a+'.isLnk',f'<a href="{H(a+".href")}" onClick="{H(a+".sel")}" title="{H(a+".nx_tt")}" style="{_NXST} text-decoration: none;">{H(a+".nx_t")}</a>')
            + IF(a+'.isIni',f'<button type="button" onClick="{H(a+".ini")}" title="{H(a+".nx_tt")}" style="{_NXST}">{H(a+".nx_t")}</button>')
            + f'<a href="{H(a+".href")}" onClick="{H(a+".sel")}" title="{H(a+".tt")}" style="{_BST} text-decoration: none;">{icon("doc",14)}Abrir ordem</a></div></div></sc-for>')
def qcards(lst,a='q',count=2,abrir=True):
    """Cartões de ordem da fila (sc-for): etapa + passo, realizado/saldo, insumos e o próximo passo com verbo."""
    ab=(f'<a href="MB-02det.dc.html" onClick="{H(a+".sel")}" title="{H(a+".ab_tt")}" style="{_BST} text-decoration: none;">{icon("doc",14)}Abrir ordem</a>' if abrir else '')
    return (f'<sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="{count}"><div style="{CARD_ST}">'
            f'<div style="display: flex; align-items: center; gap: 8px;"><span style="{H(a+".dot")}"></span><div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;"><b>{H(a+".id")}</b> · {H(a+".tipo")}</div></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(a+".loc")}</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;"><span style="{H(a+".e_st")}"><span style="{H(a+".e_dot")}"></span>{H(a+".e_t")}</span>'
            f'<span style="{H(a+".p_st")}"><span style="{H(a+".p_dot")}"></span>{H(a+".p_t")}</span></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(a+".real")}</div>'
            + IF(a+'.hasIns',f'<div style="display: flex; flex-direction: column; gap: 3px; padding: 7px 10px; border-radius: 10px; background: {BG};"><sc-for list="{H(a+".ins")}" as="i" hint-placeholder-count="1">'
                 f'<div style="font-size: 12.5px; line-height: 1.4; color: {INK};">{H("i.t")} <span style="{H("i.st")}">· {H("i.s")}</span></div></sc-for></div>')
            + f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
            + IF(a+'.nx_isA',f'<a href="{H(a+".nx_href")}" onClick="{H(a+".sel")}" title="{H(a+".nx_tt")}" style="{_NXST} text-decoration: none;">{H(a+".nx_t")}</a>')
            + IF(a+'.nx_isB',f'<button type="button" onClick="{H(a+".nx_fn")}" title="{H(a+".nx_tt")}" style="{_NXST}">{H(a+".nx_t")}</button>')
            + ab + '</div></div></sc-for>')
INP=f'font-family: inherit; font-size: 16px; font-weight: 500; color: {INK}; padding: 12px 14px; border: 1px solid {LINE}; border-radius: 14px; background: {SURF}; width: 100%; box-sizing: border-box;'
def ffield(label,fid,val,setfn,err,hint='',big=False,area=False,ph=''):
    """Campo do formulário móvel com dica e erro junto ao campo."""
    st=INP+(f' font-family: {DISP}; font-size: 22px; font-weight: 700;' if big else '')
    el=(f'<textarea id="{fid}" value="{H(val)}" onChange="{H(setfn)}" placeholder="{esc(ph)}" style="{st} min-height: 70px; resize: vertical;"></textarea>' if area
        else f'<input id="{fid}" type="text" inputMode="decimal" value="{H(val)}" onChange="{H(setfn)}" placeholder="{esc(ph)}" style="{st}">')
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="{fid}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>{el}'
            + (f'<span style="font-size: 12px; color: {MUTED};">{hint}</span>' if hint else '')
            + (IF(err+'_has',f'<span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H(err)}</span>') if err else '') + '</div>')

_PRIM_RE=re.compile(r'(<div style="padding: 12px 20px 28px;[^"]*">)<a href="[^"]*" style="([^"]*)">.*?</a>(</div>)',re.S)
def emit(fid,title,sub,status,primary,body,H_=900,fname=None,back='MB-01.dc.html',primary_href=None,js='',dyn_status=False,prim=None,cen=False,dyn_head=None,sem_prim=False,pre_extra='',sub_html=None,dica=''):
    """Gera a tela. dyn_status: selo do cabeçalho vem de v.hdr_* (JS). prim: variantes do botão primário
    [(condição|None,'a'|'b'|'ac',rótulo,href|função|(href,função))] — link navega, botão executa na própria tela, 'ac' = link que também
    executa (ex.: escolher a ordem antes de abrir o detalhe). cen: tela ligada ao cenário compartilhado (cenario.js_prefixo() + JS do app).
    dyn_head: título do <title> quando título e subtítulo do cabeçalho vêm de v.hdr_ttl / v.hdr_sub."""
    pre=((cenario.js_prefixo()+DM.js_regras()+JS_BASE+MBAPP_JS) if cen else JS_BASE)+pre_extra   # pre_extra: ex. a demanda viva (dados2.js_dem_viva) no MB-05
    head=' cenOuvir(self); const c=cenGet(); mbSig(self,v,c);' if cen else ''
    EXTRAJS[0]=pre+'const M='+json.dumps(MS,ensure_ascii=False)+';\nfunction EXTRAVALS(self,v){ const s=self.state; SAY(self,v,M);'+head+'\n'+js+'\n}'
    MS.clear()
    st=('§ST§','yellow') if dyn_status else status
    if dyn_head: title,sub='§TT§','§SB§'
    f=mobile37(fid,title,sub,st,primary,body,fname=fname,H=H_,back=back,primary_href=primary_href,dica=dica)   # dica: regras da tela no ⓘ (14/10/2026)
    if dyn_status or prim or dyn_head or sem_prim:
        path=os.path.join(E.P,f); s=open(path).read()
        if sem_prim: n0=len(s); s=_PRIM_RE.sub('',s,count=1); assert len(s)<n0, 'rodapé não encontrado'
        if dyn_status: s=s.replace(chip('§ST§','yellow'),dchip('hdr'))
        if dyn_head: s=s.replace('<title>§TT§</title>',f'<title>{esc(dyn_head)}</title>').replace('§TT§',H('hdr_ttl')).replace('§SB§',sub_html if sub_html else H('hdr_sub'))
        if prim:
            m=_PRIM_RE.search(s); pst=m.group(2)+' cursor: pointer;'
            out=''
            for cond,kind,lab,tgt in prim:
                if kind=='a': el=f'<a href="{tgt}" style="{pst}">{lab}</a>'
                elif kind=='ac': el=f'<a href="{tgt[0]}" onClick="{H(tgt[1])}" style="{pst}">{lab}</a>'
                else: el=f'<button type="button" onClick="{H(tgt)}" style="{pst}">{lab}</button>'
                out+=IF(cond,el) if cond else el
            s=s[:m.start()]+m.group(1)+out+m.group(3)+s[m.end():]
        open(path,'w').write(s)
    return f

def build():
    E._reset_screen('MB-01.dc.html'); MS.clear()
    sel420=''.join(chip(t,'yellow') for t in (D.ORDEM['OS-0420'].get('selos_extra') or []))   # mesmo selo da O.S., do Mapa e do detalhe

    # ================= MB-01 · Hoje no campo (lista · minha fila) =================
    corpo=(
      sigbar()
      + IF('us_mar',h2('Minha fila','Siga a ordem da janela; o botão diz o próximo passo.')
           + IF('fila_vazia',card('Nada liberado para você',[note('Quando o escritório liberar uma ordem sua, ela aparece aqui com os insumos a retirar.')]))
           + qcards('fila',count=2))
      + IF('us_ze',h2('Minha fila','Ordens de manutenção em que você é o executante, pela janela e depois pela criticidade.')
           + IF('omf_vazia',card('Nenhuma ordem de manutenção para você',[note('Quando o Otávio liberar uma ordem com você de executante, ela aparece aqui.')]))
           + omcards('omf',count=1))
      + h2('Abrir por tipo de trabalho','Escolha o trabalho para abrir o formulário do seu domínio.')
      + grid2(navcard('Minhas ordens','lista e detalhe da O.S.','MB-02','lista'),
              navcard('Apontamento','turno: início, pausa e fechamento','MB-03','check'),
              navcard('Ocorrência','tipo, texto, foto e voz','MB-04','alert'),
              navcard('Almoxarifado','retirar e confirmar','MB-05','box'),
              navcard('Vistoria','rota por pontos','MB-06','leaf'),
              navcard('Contagem de frutos','previsão de colheita','MB-07','grid'),
              navcard('Cargas e entregas','área e cargas da colheita','MB-10','truck'),
              navcard('Máquina','condição, leitura e abastecimento','MB-09','fuel'))   # MB-07 e MB-10 ligados ao estado (colheita, 06/10); PCM S4: MB-09 ligado ao cenário; MB-08 ainda simula (Frente F): fora do app
      + f'<div style="display: flex; justify-content: flex-end;"><button type="button" onClick="{H("restaurar")}" title="Voltar ordens, estoque, manutenção, colheita e app ao início da demonstração" '
        f'style="font-family: inherit; font-size: 12px; font-weight: 600; color: {MUTED}; background: transparent; border: 0; padding: 4px 0; cursor: pointer; text-decoration: underline;">Restaurar demonstração</button></div>')
    js='''const fila=mbFila(c); v.fila=fila.map(o=>mbCard(self,c,o)); v.fila_vazia=!fila.length;
const pend=(c.app.fila||[]).length; const us=mbUsuario(c); mbVerComo(self,v,c); const ze=mbPapelUs(us)!=='operador'; v.us_mar=!ze; v.us_ze=ze;   /* técnico de manutenção (Zé, mecânico; João, eletricista; revisão 09/10, A8): Minha fila com as OMs dele */
v.hdr_ttl='Hoje no campo'; v.hdr_sub=us+' · '+mbPapelUs(us)+' · Santa Rita';
const mv=mbManView(c); const oms=ze?mbOmsDe(mv,us):[]; v.omf=oms.map(o=>mbOmCard(self,c,mv,o)); v.omf_vazia=ze&&!oms.length;
const nq=ze?oms.length:fila.length; DCH(v,'hdr',ze?(nq+(nq===1?' ordem':' ordens')+' · '+(pend?pend+' aguardando sinal':'envios em dia')):(fila.length+(fila.length===1?' ordem':' ordens')+' · '+(pend?pend+' aguardando sinal':'envios em dia')),pend?'yellow':'green');
const o0=oms[0]; const p0=o0?mbOmPasso(mv,o0):null; v.zk_a=ze&&!!p0&&(p0.k==='cont'||p0.k==='apt'); v.zk_b=ze&&!!p0&&p0.k==='ini'; v.zk_none=ze&&!v.zk_a&&!v.zk_b;
v.zk_lab=p0?p0.t+' · '+o0.id:''; v.zk_href=o0?'MB-09det.dc.html#'+o0.id:'MB-09.dc.html'; v.zk_sel=()=>{ if(o0) mbOmSet(o0.id); };
v.zk_go=()=>{ if(o0){ mbOmSet(o0.id); mbManCmd(self,'iniciar',{om:o0.id}); } };
const pk=mbPrim(c,fila); v.pk_isA=!ze&&!!pk.href; v.pk_ini=!ze&&pk.k==='iniciar'; v.pk_none=!ze&&pk.k==='none'; v.pk_lab=pk.lab; v.pk_href=pk.href||'MB-01.dc.html';
v.pk_sel=()=>{ if(pk.o) mbSelSet(pk.o.id); };
v.pk_go=()=>{ if(pk.o){ mbSelSet(pk.o.id); cenMudar(self,c=>mbIniciar(c,pk.o.id)); } };
// cenReset só apaga a chave: grava o cenário inicial para que os outros quadros abertos também voltem ao início (e não regravem o antigo).
v.restaurar=()=>{ cenReset(); cenSave(cenGet()); mbSelSet(''); mbOmSet(''); self.setState({cenrev:Date.now(),ft:{},ft_err:{},g2toast:'Demonstração restaurada: ordens, estoque, manutenção, colheita e app voltaram ao início.'}); };'''
    # 14/10/2026 (proprietário: "tire das telas ver como simulação"): quem usa o app é escolhido no próprio nome do cabeçalho (como o avatar da web)
    us_sel=(f'<span style="display: inline-flex; align-items: center; gap: 4px; flex-wrap: wrap;"><select aria-label="Usuário do app (demonstração)" value="{H("us_k")}" onChange="{H("us_set")}" '
            f'style="font: inherit; color: inherit; border: 0; border-bottom: 1px dashed currentColor; background: transparent; padding: 0 2px; min-height: 32px; cursor: pointer;">'
            f'<sc-for list="{H("us_opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select><span>· Santa Rita</span></span>')
    emit('MB-01','Hoje no campo','Marcos · operador · Santa Rita',None,'Abrir próxima tarefa',corpo,H_=1800,back='IN-01.dc.html',
         js=js,dyn_status=True,cen=True,dyn_head='Hoje no campo',sub_html=us_sel,
         dica='Minha fila segue a ordem da janela; o botão do rodapé leva ao próximo passo. Na manutenção, a fila é das ordens em que você é o executante, pela janela e depois pela criticidade.',
         prim=[('pk_isA','ac',H('pk_lab'),(H('pk_href'),'pk_sel')),('pk_ini','b',H('pk_lab'),'pk_go'),('pk_none','a','Ver minhas ordens','MB-02.dc.html'),
               ('zk_a','ac',H('zk_lab'),(H('zk_href'),'zk_sel')),('zk_b','b',H('zk_lab'),'zk_go'),('zk_none','a','Abrir Máquina','MB-09.dc.html')])

    # ================= MB-02 · Minhas ordens (lista) =================
    corpo=(
      sigbar()
      + h2('Suas ordens · Marcos','Abra a ordem para ver instrução, insumos e apontamentos.')
      + qcards('minhas',count=3)
      + h2('Da equipe · outros responsáveis','Consulte; quem executa é o responsável indicado.')
      + card(f'<b>{O420["id"]}</b> · Plantio · Soja 58 W',[
          kv('Contexto',f'T4 · Santa Rita · resp. {O420["resp"]}')+' · '+kv('Realizado',f'{O420["realizado"]}/{O420["area"]} ha (18 conferidos + 12 provisórios) · saldo {O420["saldo"]} ha parado'),
          chips(etapa('Em execução'),selo(O420['selo']),sel420,tag('v2 no realizado · v3 no saldo')),
          kv('Aviso','Fichas do saldo revogadas pelo ajuste da v3 (KCl −12 % só nos 70 ha, por Ana) · 23/09 08:05'),
          chips(dchip('ack')),
          kv('Impedimento',f'{D.OM["id"]} · Trator T1 bloqueado · substituto {esc(D.OM["substituto"])} a partir de 24/09 06:00'),
          btns(IF('noack',fnb('Reconhecer','ack','check','Registrar ciência da revogação das fichas do saldo')),
               say('Iniciar · bloqueado','Bloqueado: Trator T1 com OM-0233 — saldo de 70 ha parado; aguarde o reparo ou o substituto Trator 02 (a partir de 24/09) confirmado pelo PCP (nada foi iniciado).','alert','Ver por que não pode iniciar'),
               lnk('Registrar ocorrência','MB-04.dc.html','alert','Abrir a captura de ocorrência'))],state='red')
      + card('<b>OS-0418</b> · Fertirrigação · Pivô 1',[
          kv('Contexto',f'P1 · 95 ha · resp. {D.ORDEM["OS-0418"]["resp"]}')+' · '+kv('Motivo','água reclassificada para fertirrigação · v2 a liberar por Ana (agrônoma)'),
          chips(etapa('A liberar'),chip('Revogada no servidor · 23/09 07:15','red')),
          kv('Relato no aparelho','23/09 07:40 · “pivô 1 ligado 20 min para teste de pressão”'),
          chips(chip('Relato fora da autorização atual · aguarda decisão','yellow')),
          btns(say('Iniciar · bloqueado (revogada 07:15)','Bloqueado: a OS-0418 foi revogada no servidor em 23/09 07:15 — o pacote offline não autoriza nova execução. O relato das 07:40 segue para decisão de Ana, sem aprovação retroativa.','alert','Ver por que não pode iniciar'))],state='red')
      + card(f'<b>{O419["id"]}</b> · Irrigação · água',[
          kv('Contexto',f'Pivô 2 · Santa Rita · janela hoje {IRR["janela"]} · resp. {O419["resp"]}'),
          chips(etapa('Liberadas'),tag('necessidade do balanço')),
          ],state='blue')   # MB-08 só simula (Frente F); a regra da água simplificada foi para a dica ⓘ (14/10/2026)
      + btns(say('Ler QR','QR da OS-0421 lido · ordem aberta na versão autorizada v2.','grid','Ler o QR impresso da ordem')))
    js='''const mine=mbMinhas(c).filter(o=>o.etapa!=='Encerradas'); v.minhas=mine.map(o=>mbCard(self,c,o));
const ack=!!s.ack; v.noack=!ack;
DCH(v,'ack',ack?'Ciência registrada · CI-0931 · 10:44':'Ciência pendente do operador',ack?'green':'yellow');
v.ack=()=>{ if(self.state.ack) return; self.setState({ack:true,g2toast:'Ciência registrada (recibo CI-0931) · o saldo de 70 ha segue na v3 e fica parado até o Trator T1 voltar ou o substituto ser confirmado · os 30 ha realizados seguem na v2.'}); };'''
    emit('MB-02','Minhas ordens','',('1 impedida · 1 revogada','red'),
         'Abrir ordem',corpo,H_=2320,back='MB-01.dc.html',js=js,cen=True,sem_prim=True,
         dica='Mesma ordem do escritório. Da equipe: quem executa é o responsável indicado. Irrigação só com água abre em Irrigação, sem materiais e sem requisição. '
              'Fechar o turno não encerra a ordem: encerrar é no escritório, com apontamentos enviados e nada em custódia.')

    # ---- MB-02det · detalhe da ordem escolhida (cenário) ----
    PREP421=f"{CALDA['litros']} L de calda · {CALDA['vazao']} · cobre {CALDA['cobre']} · {CALDA['por_tanque']} de Fungicida A ({CALDA['dose']})"
    corpo=(
      sigbar()
      + mcont('Minhas ordens',H('d_aqui'),H('d_falta'),H('d_prox'))
      + f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Instrução liberada</div></div>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{hchip("d_ps")}</div>'
        f'<sc-for list="{H("d_kv")}" as="k" hint-placeholder-count="4"><div style="font-size: 13px; color: {MUTED}; line-height: 1.45;"><span style="font-weight: 600; color: {INK};">{H("k.l")}:</span> {H("k.t")}</div></sc-for>'
        + IF('d_424',btns(lnk('Abrir ficha do caldeiro','OS-0424-app.dc.html','doc','Abrir o preparo carga a carga da OS-0424 (funciona sem internet)')))
        + '</div>'
      + IF('d_hasins',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {GRAY}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Insumos · {H("d_req")}</div></div>'
        f'<sc-for list="{H("d_ins")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 7px 0; border-top: 1px solid {LINE};">'
        f'<div style="font-size: 13px; font-weight: 700;">{H("i.t")}</div><div style="font-size: 12.5px; color: {MUTED}; line-height: 1.4;">{H("i.s")}</div>'
        f'<div style="font-size: 12.5px; line-height: 1.4;"><span style="{H("i.st")}">{H("i.c")}</span></div></div></sc-for></div>')
      + f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {GRAY}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Apontamentos</div></div>'
        + IF('d_semap',note('Nenhum turno fechado nesta ordem.'))
        + IF('d_apmais',f'<div style="font-size: 12.5px; color: {MUTED}; padding: 5px 0; border-top: 1px solid {LINE};">{H("d_apmais_t")}</div>')
        + f'<sc-for list="{H("d_aps")}" as="a" hint-placeholder-count="2"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 13px; padding: 5px 0; border-top: 1px solid {LINE};">'
        f'<span style="flex-grow: 1; min-width: 0;">{H("a.t")}</span><span style="{H("a.st")}"><span style="{H("a.dot")}"></span>{H("a.c")}</span></div></sc-for></div>'
      + IF('d_hasoc',f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">Ocorrências</div>'
        f'<sc-for list="{H("d_ocs")}" as="o" hint-placeholder-count="1"><div style="font-size: 13px; color: {MUTED}; line-height: 1.45; padding: 5px 0; border-top: 1px solid {LINE}; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;"><b style="color: {INK};">{H("o.t")}</b> · {H("o.s")}</div></sc-for>'
        + IF('d_ocmais',f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 5px; border-top: 1px solid {LINE};">{H("d_ocmais_t")}</div>') + '</div>')
      + btns(lnk('Registrar ocorrência','MB-04.dc.html','alert','Abrir a captura de ocorrência desta ordem'),
             lnk('Ver retirada','MB-05.dc.html','box','Abrir retiradas e custódia no almoxarifado')))
    js=f'''const mine=mbMinhas(c); let id=mbSelGet(); if(!c.ordens[id]||c.ordens[id].resp!==c.app.operador) id=((mbFila(c)[0]||mine[0])||{{}}).id; const o=c.ordens[id];
v.d_none=!o;
if(o){{ const p=mbPasso(c,o); const ec=MB_ETAPA_COR[o.etapa]||'gray'; const r=mbReq(c,o);
v.hdr_ttl=o.id+' · '+o.tipo.split(' · ')[0]; v.hdr_sub=o.tipo+' · '+o.talhao+' · '+cenNum(o.area,1)+' ha';
DCH(v,'hdr',o.etapa,ec); DCH(v,'d_ps',p.chip[0],p.chip[1]);
v.d_aqui=o.id+' · '+o.etapa; v.d_prox=p.t||(p.feita?'Aguardar encerramento':'Voltar às ordens');
const tt=mbTurno(c); const rs=mbResta(o);
v.d_falta=({{fechar:'hectares, horas e consumo do turno',confirmar:'confirmar o recebimento',retirar:'retirar os insumos com '+(cenAlmoxNome()||'o almoxarife'),iniciar:'saldo de '+cenNum(rs,1)+' ha',
  outro:'fechar o turno da '+(tt?tt.os:'')+' · saldo de '+cenNum(rs,1)+' ha',devolver:'devolver a sobra '+cenAoAlmox()+': '+mbSobraTxt(mbSobra(c,o)),
  enviar:cenNum(mbProv(o),1)+' ha no aparelho, aguardando sinal',rever:'decisão de '+g2alcQuem('AL-02')+' sobre a área restante',none:p.feita?'encerramento no escritório':'liberação no escritório'}})[p.k];
const kv=[{{l:'Versão',t:o.versao}},{{l:'Janela',t:mbJan(o)}},{{l:'Local',t:o.talhao+' · '+cenNum(o.area,1)+' ha'}},{{l:'Andamento',t:mbRealTxt(o)}}];
if(o.id==='OS-0421'){{ kv.push({{l:'Equipe/conjunto',t:{json.dumps(EQ421)}}}); kv.push({{l:'Preparo por tanque',t:{json.dumps(PREP421)}}}); }}
v.d_kv=kv; v.d_424=o.id==='OS-0424';
v.d_req=r?r.id:'sem requisição'; v.d_hasins=(o.ins||[]).length>0;
v.d_ins=(o.ins||[]).map(x=>{{ const it=r&&r.itens.find(i=>i.prod===x.p);
  let cst='gray', ct=r?'Peça ao escritório antes de usar':'Reserva ao liberar a ordem';
  const kc=mbConf(c,o.id,x.p); if(kc){{cst='yellow'; ct='Em conferência · '+cenConfTxt(kc,c)+' · '+cenConcQuem(c,[kc]);}}
  else if(it){{ if(it.custodia>0&&!it.confirmado){{cst='yellow'; ct='Entregue '+cenNum(it.custodia)+' '+it.un+' · confirme a retirada';}} else if(it.custodia>0){{cst='green'; ct='Com você '+cenNum(it.custodia)+' '+it.un;}} else if(cenSaldoEntregar(it)>0){{cst='gray'; ct='Retirar '+cenNum(cenSaldoEntregar(it))+' '+it.un+' com '+(cenAlmoxNome()||'o almoxarife');}} else {{cst='gray'; ct='Nada em custódia';}} }}
  return {{t:x.p+' · '+cenNum(x.dose,2)+' '+x.un+'/ha × '+cenNum(o.area,2)+' ha = '+cenNum(x.tot)+' '+x.un,
          s:it?('lote '+it.lote+(it.emb?' · '+it.emb:'')+' · entregue '+cenNum(it.entregue)+' '+it.un+' · consumido '+cenNum(it.consumido)+' '+it.un):(r?'fora da '+r.id+' · nada com você':'sem requisição'),
          c:ct, st:mbTx(cst)}}; }});
const aps=(o.ap||[]); v.d_semap=!aps.length; const apx=Math.max(0,aps.length-4); v.d_apmais=apx>0; v.d_apmais_t=apx?apx+(apx>1?' turnos anteriores':' turno anterior'):'';
v.d_aps=aps.slice(-4).map(a=>{{ const ofl=a.sinc===false; const cc=ofl?'yellow':(a.st==='Conferido'?'green':((a.st==='Previsto'||a.st===CEN_AP_DESC)?'gray':'yellow'));
  return {{t:'Dia '+a.dia+' · '+a.d+' · '+cenNum(a.ha,1)+' ha'+(a.h?' em '+cenNum(a.h,1)+' h':''), c:ofl?'No aparelho · aguardando sinal':a.st, st:mbChs(cc), dot:mbDot(cc)}}; }});
const ocs=(c.ocorr||[]).filter(x=>x.os===o.id); v.d_hasoc=ocs.length>0; const ocx=Math.max(0,ocs.length-2); v.d_ocmais=ocx>0; v.d_ocmais_t=ocx?'+ '+ocx+(ocx>1?' anteriores':' anterior'):'';
v.d_ocs=ocs.slice(-2).reverse().map(x=>({{t:x.id+' · '+x.tipo+' · '+x.at+(x.sinc?'':' · no aparelho'),s:x.texto}}));
v.d_isA=!!p.href; v.d_ini=p.k==='iniciar'; v.d_none=!p.href&&p.k!=='iniciar'; v.d_href=p.href||'MB-02.dc.html'; v.d_lab=p.k==='iniciar'?'Iniciar turno · '+o.id:p.t;
v.d_go=()=>cenMudar(self,c=>mbIniciar(c,o.id));
}}'''
    emit('MB-02','Detalhe da ordem','',None,'Abrir ordem',corpo,H_=1620,fname='MB-02det.dc.html',back='MB-02.dc.html',js=js,dyn_status=True,cen=True,
         dyn_head='Detalhe da ordem',dica='Siga dose, janela e preparo da versão autorizada. Use só o material autorizado; a sobra volta pela devolução.',
         prim=[('d_isA','a',H('d_lab'),H('d_href')),('d_ini','b',H('d_lab'),'d_go'),('d_none','a','Voltar às ordens','MB-02.dc.html')])

    # ================= MB-03 · Apontamento do turno (detalhe/formulário) =================
    turno_on=(
      mcont('Minha fila',H('t_aqui'),H('t_falta'),H('t_prox'))
      + f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;">{H("t_tt")}</div></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("t_loc")}</div>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">{hchip("tst")}<span style="font-size: 12.5px; color: {MUTED};">{H("t_desde")}</span></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("t_real")}</div>'
        + btns(f'<button type="button" onClick="{H("pausar")}" title="{H("pz_tt")}" style="{_BST}">{icon("clock",14)}{H("pz_lab")}</button>',
               lnk('Registrar ocorrência','MB-04.dc.html','alert','Abrir a captura de ocorrência desta ordem'))
        + '</div>'
      + IF('t_zero',note(H('ha_hint'),RED))
      + IF('t_fe',ffield('Hectares feitos neste turno','ft_ha','ft_ha','set_ha','e_ha',hint=H('ha_hint'),big=True,ph='0')
      + ffield('Horas trabalhadas','ft_h','ft_h','set_h','e_h',ph='ex.: 5,5')
      + IF('has_cons',f'<div style="display: flex; flex-direction: column; gap: 10px;">'+h2('Consumo por insumo','Confira: vem calculado por dose × hectares.')
           + f'<sc-for list="{H("cons")}" as="k" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 4px;">'
             f'<label for="{H("k.id")}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("k.l")}</label>'
             f'<input id="{H("k.id")}" type="text" inputMode="decimal" value="{H("k.val")}" onChange="{H("k.set")}" style="{INP}">'
             f'<span style="font-size: 12px; color: {MUTED};">{H("k.hint")}</span>'
             f'<sc-if value="{H("k.has_warn")}" hint-placeholder-val="{H("false")}"><span aria-live="polite" style="font-size: 12px; font-weight: 700; color: {YEL};">{H("k.warn")}</span></sc-if>'
             f'<sc-if value="{H("k.has_err")}" hint-placeholder-val="{H("false")}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("k.err")}</span></sc-if></div></sc-for></div>')
      + ffield('Observação','ft_obs','ft_obs','set_obs','',area=True,ph='Ex.: vento subiu às 10:30; parei a barra 20 min.')
))
    turno_off=(
      IF('has_last',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
         f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Turno fechado · {H("last_t")}</div></div>'
         f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{hchip("lst")}'+IF('last_hasConf',hchip('lcf'))+IF('last_hasDiv',hchip('ldv'))+'</div>'
         f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">Consumo: {H("last_cons")}</div>'
         + IF('last_hasConf',f'<div style="font-size: 13px; color: {INK}; line-height: 1.45;">{H("last_conf")}</div>')
         + IF('last_hasDiv',f'<div style="font-size: 13px; color: {INK}; line-height: 1.45;">{H("last_div")}</div>')
         + f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("last_real")}</div></div>')
      + h2('Nenhum turno aberto','Inicie o turno na ordem em que vai trabalhar.')
      + qcards('lista',a='l',count=2))
    corpo=sigbar()+IF('t_on',turno_on)+IF('t_off',turno_off)
    js='''const t=mbTurno(c); const o=t?c.ordens[t.os]:null; v.t_on=!!t; v.t_off=!t;
const fila=mbFila(c); const prontas=fila.filter(x=>mbPasso(c,x).k==='iniciar');
v.t_ini=!t&&prontas.length>0; v.t_none=!t&&!prontas.length; v.ti_lab=prontas.length?'Iniciar turno · '+prontas[0].id:'';
v.ti_go=()=>{ if(prontas[0]){ mbSelSet(prontas[0].id); cenMudar(self,c=>mbIniciar(c,prontas[0].id)); } };
v.lista=fila.map(x=>mbCard(self,c,x));
const L=s.ft_last; v.has_last=!t&&!!L;
if(L){ const oo=c.ordens[L.os]; const ap=oo&&(oo.ap||[]).find(a=>a.dia===L.dia); const env=ap?ap.sinc!==false:true;
  v.last_t=L.os+' · dia '+L.dia+' · '+cenNum(L.ha,1)+' ha em '+cenNum(L.h,1)+' h'; v.last_cons=L.cons||'nenhum'; v.last_real=oo?mbRealTxt(oo):'';
  const dup=!!ap&&ap.st===CEN_AP_DUP, desc=!!ap&&ap.st===CEN_AP_DESC;   // duplicidade: nada baixado até a decisão de Paula (conferência)
  DCH(v,'lst',dup?'Em conferência · duplicidade':(desc?'Duplicidade · não somado':(env?'Enviado · a ordem continua aberta':'No aparelho · aguardando sinal')),dup?'yellow':(desc?'gray':(env?'green':'yellow')));
  if(dup) v.last_cons='nada baixado: '+CEN_CONF_AP()+' decide se é outro turno'; else if(desc) v.last_cons='nada baixado: guardado como duplicidade';
  const cf=(c.confs||[]).filter(k=>k.os===L.os&&k.dia===L.dia); const ab=cf.some(k=>k.estado==='Em conferência'||k.estado===CEN_CC_AGUARDA); v.last_hasConf=cf.length>0;
  v.last_conf=cf.map(k=>k.estado==='Em conferência'?'Em conferência · '+cenConfTxt(k,c)+' · '+cenConcQuem(c,[k]):(k.estado===CEN_CC_AGUARDA?'Aguarda a decisão da duplicidade · '+cenConfTxt(k,c)+' · '+CEN_CONF_AP():k.estado+' por '+k.por+' · '+cenConfTxt(k))).join(' | ');
  DCH(v,'lcf',ab?'Consumo em conferência':'Conferência resolvida',ab?'yellow':'green'); if(!L.cons&&cf.length&&!dup&&!desc) v.last_cons='nada baixado neste turno';
  /* B-R8: dose diferente da planejada fica como informada e vai para revisão técnica do agrônomo (o operador vê no recibo) */
  const dva=(ap&&(ap.div||[]).length&&!desc)?ap:null; v.last_hasDiv=!!dva;
  /* retido como duplicidade: a revisão só abre se o turno somar (revisão DOM achado 6) */
  v.last_div=dva?(dva.div.map(cenDivTxt).join('; ')+(dva.rev?' · '+dva.rev.dec.toLowerCase()+' por '+dva.rev.quem:(dup?' · a revisão técnica abre se '+CEN_CONF_AP()+' somar o turno':' · revisão técnica de '+g2quem('agronomo')))):'';
  DCH(v,'ldv',dva&&dva.rev?'Dose revisada':CEN_DIV,dva&&dva.rev?'green':(dup?'yellow':'red')); }
DCH(v,'hdr',t?(mbPausado(t)?'turno pausado':'turno aberto'):'sem turno aberto',t?(mbPausado(t)?'yellow':'green'):'gray');
v.t_fe=false; v.t_zero=false;
if(t){ const pz=mbPausado(t);
  v.t_aqui='Turno · '+o.id; v.t_tt=o.id+' · '+o.tipo; v.t_loc=o.talhao+' · '+cenNum(o.area,1)+' ha · '+o.versao;
  v.t_desde='iniciado às '+t.ini+(t.pausas.length?' · '+t.pausas.length+(t.pausas.length>1?' pausas':' pausa'):'');
  DCH(v,'tst',pz?'Turno pausado':'Turno aberto',pz?'yellow':'green'); v.t_real=mbRealTxt(o);
  v.pz_lab=pz?'Retomar turno':'Pausar turno'; v.pz_tt=pz?'Retomar o turno':'Pausar o turno (o tempo parado não conta)';
  v.pausar=()=>cenMudar(self,c=>cenPausar(c));
  const f=s.ft||{}; const er=s.ft_err||{}; const r=mbReq(c,o); const ha=mbNum(f.ha); const pv=mbProv(o); const mx=mbResta(o);
  v.t_fe=mx>0.001; v.t_zero=!v.t_fe; v.descartar=()=>cenMudar(self,c=>mbDescartar(c));
  v.t_falta=v.t_fe?'hectares, horas e consumo':'nada: a ordem não tem saldo'; v.t_prox=v.t_fe?'Fechar turno':'Descartar turno';
  v.ft_ha=f.ha||''; v.ft_h=f.h||''; v.ft_obs=f.obs||'';
  v.ha_hint=!v.t_fe?'Saldo 0 ha: nada a apontar nesta ordem. Descarte o turno.':(pv?'Máximo '+cenNum(mx,1)+' ha: saldo '+cenNum(o.saldo,1)+' ha menos '+cenNum(pv,1)+' ha no aparelho':'Máximo '+cenNum(mx,1)+' ha (saldo da ordem)');
  v.cons=(o.ins||[]).map((x,i)=>{ const it=r&&r.itens.find(y=>y.prod===x.p); const ed=(f.ced||{})[x.p]; const e2=(er.cons||{})[x.p]||'';
    const qv=(ed!==undefined&&String(ed).trim()!=='')?mbNum(ed):(ha>0&&it&&ed===undefined?cenQtdTrecho(x.dose,(o.realizado||0)+pv,ha):NaN); const tem=it?it.custodia:0;
    const warn=(!e2&&qv>tem+1e-9)?(ed===undefined?'Sugestão acima do que está com você ('+cenNum(tem)+' '+x.un+'): informe quanto usou.'
      :'Acima do que está com você ('+cenNum(tem)+' '+x.un+'): fecha em conferência com '+CEN_CONC_RESP()+'.'):'';
    return {id:'ft_c'+i, l:x.p+' ('+x.un+')', val:ed!==undefined?ed:(ha>0&&it?mbIn(cenQtdTrecho(x.dose,(o.realizado||0)+pv,ha)):''), err:e2, has_err:!!e2, warn, has_warn:!!warn,
      hint:it?cenNum(x.dose,2)+' '+x.un+'/ha × hectares · com você '+cenNum(it.custodia)+' '+it.un:(r?'Fora da '+r.id+' · nada com você':'Sem requisição · nada com você'),
      set:(e)=>{ const st=self.state; const ff=Object.assign({},st.ft||{}); ff.ced=Object.assign({},ff.ced||{},{[x.p]:e.target.value}); const ee=Object.assign({},st.ft_err||{}); ee.cons=Object.assign({},ee.cons||{}); delete ee.cons[x.p]; self.setState({ft:ff,ft_err:ee}); } }; });
  v.has_cons=v.cons.length>0;
  const set=(k)=>(e)=>{ const st=self.state; const ff=Object.assign({},st.ft||{},{[k]:e.target.value}); const ee=Object.assign({},st.ft_err||{}); delete ee[k]; self.setState({ft:ff,ft_err:ee}); };
  v.set_ha=set('ha'); v.set_h=set('h'); v.set_obs=set('obs');
  v.e_ha=er.ha||''; v.e_ha_has=!!er.ha; v.e_h=er.h||''; v.e_h_has=!!er.h;
  v.ft_ok=()=>{ const c2=cenGet(); const t2=mbTurno(c2); if(!t2) return TOAST(self,'Nenhum turno aberto.'); const o2=c2.ordens[t2.os]; const st=self.state; const f2=st.ft||{};
    const e={}; const h2=mbNum(f2.ha), hh=mbNum(f2.h); const pv2=mbProv(o2); const mx2=mbResta(o2);
    if(!(h2>0)) e.ha='Informe os hectares feitos (maior que zero).'; else if(h2>mx2+1e-9) e.ha='Máximo '+cenNum(mx2,1)+' ha: é o saldo da ordem'+(pv2?' menos '+cenNum(pv2,1)+' ha no aparelho':'')+'.';
    if(!(hh>0)) e.h='Informe as horas trabalhadas.'; else if(hh>24) e.h='Máximo 24 h por turno.';
    const r2=mbReq(c2,o2); const cons={}; const ec={}; const est=[];
    (o2.ins||[]).forEach(x=>{ const ed=(f2.ced||{})[x.p]; const it=r2&&r2.itens.find(y=>y.prod===x.p);
      // fora da requisição nada está com o operador: sem pré-cálculo e 0 explícito (o cenário completaria com dose × área)
      const vazio=ed===undefined||String(ed).trim()==='';
      const q=!vazio?mbNum(ed):(it?(ed===undefined&&h2>0?cenQtdTrecho(x.dose,(o2.realizado||0)+pv2,h2):NaN):0);   // regra única (SINT-C03)
      if(isNaN(q)||q<0){ if(ed!==undefined) ec[x.p]='Informe o consumo em '+x.un+' (0 se não usou).'; return; }
      // sugestão (dose × área) não editada é estimativa (CONC-13): acima do que está com o operador, ele informa quanto usou
      if(ed===undefined&&it&&q>it.custodia+1e-9){ ec[x.p]='Informe quanto usou: a sugestão de '+cenNum(q)+' '+x.un+' passa do que está com você ('+cenNum(it.custodia)+' '+x.un+').'; return; }
      if(ed===undefined) est.push(x.p);
      cons[x.p]=q; });   // informado acima do que está com o operador: o cenário grava o fato Em conferência (CONC-07), sem baixa
    if(Object.keys(ec).length) e.cons=ec;
    if(Object.keys(e).length){ self.setState({ft_err:e,g2toast:'Corrija os campos destacados; nada foi gravado.'}); return; }
    const dia=(o2.ap||[]).filter(a=>a.st!=='Previsto').length+1; const obs=String(f2.obs||'').trim();
    // o movimento e o apontamento guardam só o que foi baixado (sem linha 0 de insumo fora da requisição); o relatado em conferência fica no caso
    const res=cenMudar(self,c=>{ const rr=cenFecharTurno(c,h2,hh,Object.assign({},cons),obs,est);
      const oo=c.ordens[o2.id]; const ap=(oo.ap||[])[oo.ap.length-1]; if(ap&&ap.cons) Object.keys(ap.cons).forEach(k=>{ if(!(ap.cons[k]>0)) delete ap.cons[k]; });
      const m=ap&&c.movs.find(x=>x.id===ap.mov); if(m&&m.tipo==='consumo'&&m.origem==='app') m.det=Object.keys(ap.cons||{}).map(k=>k+' '+cenNum(ap.cons[k],1)).join(', ');
      return rr; });
    if(res&&!res.erro){ const ap3=(cenGet().ordens[o2.id].ap||[]).find(a=>a.dia===dia)||{}; const cc=ap3.cons||{};
      self.setState({ft:{},ft_err:{},ft_last:{os:o2.id,dia,ha:h2,h:hh,cons:Object.keys(cc).map(k=>k+' '+cenNum(cc[k],1)+' '+((o2.ins.find(x=>x.p===k)||{}).un||'')).join(' · ')}}); }
  };
}'''
    emit('MB-03','Apontamento do turno','',None,
         'Fechar turno',corpo,H_=1530,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
         dica='Inicie o turno na ordem em que vai trabalhar. O consumo vem calculado por dose × hectares: confira. Fechar o turno guarda o dia; a ordem continua aberta até o escritório encerrar.',
         prim=[('t_fe','b','Fechar turno','ft_ok'),('t_zero','b','Descartar turno','descartar'),('t_ini','b',H('ti_lab'),'ti_go'),('t_none','a','Voltar à fila','MB-01.dc.html')])

    # ---- MB-03x-recibo · envios e recibos do aparelho (cenário: fila offline e recibos) ----
    corpo=(
      sigbar(envios=False)
      + mcont('Apontamento do turno','Envios e recibos',H('ct_f'),H('ct_p'))
      + IF('pend',vstep([('Capturado no aparelho','done'),('Aguardando sinal','now'),('Enviado com recibo','todo'),('Conferência no escritório','todo')],''))
      + IF('nopend',vstep([('Capturado no aparelho','done'),('Enviado com recibo','done'),('Conferência no escritório','now')],''))
      + IF('pend',f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">No aparelho · {H("n_t")}</div>'
           f'<sc-for list="{H("itens")}" as="i" hint-placeholder-count="1"><div style="font-size: 13px; padding: 5px 0; border-top: 1px solid {LINE};">{H("i.t")}</div></sc-for>'
           + IF('mais',f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 5px; border-top: 1px solid {LINE};">{H("mais_t")}</div>') + '</div>')
      + f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">Recibos do servidor</div>'
        f'<sc-for list="{H("recs")}" as="r" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0; border-top: 1px solid {LINE};">'
        f'<div style="font-size: 13px; font-weight: 700;">{H("r.t")}</div><sc-for list="{H("r.itens")}" as="x" hint-placeholder-count="1"><div style="font-size: 12.5px; color: {MUTED};">{H("x.t")}</div></sc-for></div></sc-for>'
        f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0; border-top: 1px solid {LINE};"><div style="font-size: 13px; font-weight: 700;">{APT["recibo"]} · 23/09 10:45 · 1 registro</div>'
        f'<div style="font-size: 12.5px; color: {MUTED};">{APT["id"]} · {APT["os"]} · dia {APT["dia"]} · {APT["ha"]} ha · identidade {APT["uuid"]} · confirmado uma vez</div></div></div>'
      )
    js='''const fila=c.app.fila||[]; const n=fila.length; v.pend=n>0; v.nopend=!n;
// Tetos da lista (quadro de altura fixa): 3 registros no aparelho e os 2 últimos recibos com até 2 itens cada; o resto vira contagem.
const mais=(k)=>'+ '+k+(k>1?' outros registros':' outro registro');
v.n_t=n+(n>1?' registros aguardando sinal':' registro aguardando sinal'); v.itens=fila.slice(0,3).map(k=>({t:mbDesc(c,k)})); v.mais=n>3; v.mais_t=n>3?mais(n-3):'';
v.recs=(c.app.recibos||[]).slice(-2).reverse().map(r=>({t:r.id+' · '+r.at+' · '+r.n+(r.n>1?' registros':' registro'),itens:r.itens.slice(0,2).map(x=>({t:x})).concat(r.itens.length>2?[{t:mais(r.itens.length-2)}]:[])}));
v.ct_f=n?v.n_t:'conferência no escritório'; v.ct_p=n?'Reenviar pendentes':'Voltar à fila';
DCH(v,'hdr',n?n+' aguardando sinal':'envios em dia',n?'yellow':'green');
v.reenviar=()=>{ const cc=cenGet(); const nn=(cc.app.fila||[]).length; if(!nn) return TOAST(self,'Nada pendente: reenviar devolve o mesmo recibo, sem duplicar.');
  if(!cenOnline(cc)) return TOAST(self,'Sem sinal: '+nn+(nn>1?' registros seguem':' registro segue')+' no aparelho, sem cópia · envia uma vez quando o sinal voltar.');
  cenMudar(self,c=>mbSinal(c,true)); };'''
    emit('MB-03','Envios e recibos','',None,
         'Voltar à fila',corpo,H_=1300,fname='MB-03x-recibo.dc.html',back='MB-03.dc.html',js=js,dyn_status=True,cen=True,
         dica='Cada registro entra uma vez: reiniciar o app preserva a fila, reenviar sem sinal não cria cópia e reenvios devolvem o mesmo recibo; a conferência decide o realizado. '
              'Conflito com outro aparelho abre reconciliação sem somar em dobro. Pacote revogado ou vencido vira relato para decisão, sem aprovação retroativa.',
         prim=[('pend','b','Reenviar pendentes','reenviar'),('nopend','a','Voltar à fila','MB-01.dc.html')])

    # ================= MB-04 · Ocorrência móvel (detalhe/formulário) =================
    corpo=(
      sigbar()
      + mcont('Minha fila',H('oc_aqui'),H('ct_f'),H('ct_p'))
      + IF('oc_novo',
          f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">Ordem</span>'
          f'<div role="group" aria-label="Ordem da ocorrência" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("oc_ords")}" as="o" hint-placeholder-count="2">'
          f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.fn")}" title="{H("o.tt")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></div></div>'
          f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">Tipo</span>'
          f'<div role="group" aria-label="Tipo da ocorrência" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("oc_tipos")}" as="o" hint-placeholder-count="6">'
          f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.fn")}" title="{H("o.tt")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></div></div>'
          # PCM S4: Equipamento (e Segurança ligada a máquina) pede a máquina e grava um achado na Manutenção, ligado à O.S.
          + IF('oc_maq',f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Máquina")}' + pills('oc_atvs','Máquina da ocorrência',3) + note(H('oc_maqt')) + '</div>')
          + IF('oc_ach',f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Componente")}' + pills('oc_comps','Componente',7) + '</div>'
               f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Pode operar?")}' + pills('oc_sugs','Pode operar?',3) + '</div>')
          + IF('oc_hasRep',f'<div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">{H("oc_repMsg")}'
               + btns(fnb('Somar ao achado aberto','oc_somar','check','Somar esta ocorrência ao achado aberto da mesma máquina e componente'),
                      fnb('Registrar novo','oc_novoAch','alert','Registrar um achado novo mesmo assim')) + '</div>')
          + ffield('Descrição','oc_txt','oc_txt','oc_set','oc_err',area=True,ph='O que aconteceu, onde e o que você fez.')
          + btns(fnb('Ditar (simulado)','voz','users','Transcrever a fala para o texto (simulado)'),
                 f'<button type="button" onClick="{H("foto")}" title="Anexar foto com GPS (simulado)" style="{_BST}">{icon("map",14)}{H("foto_lab")}</button>')
          + note(H('oc_foto_t')))
      + IF('oc_feito',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
           f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">{H("d_t")}</div></div>'
           f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{hchip("dsc")}</div>'
           f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("d_txt")}</div>'
           + btns(fnb('Nova ocorrência','nova','alert','Registrar outra ocorrência')) + '</div>')
      + IF('has_ocs',f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">Ocorrências das suas ordens</div>'
           f'<sc-for list="{H("ocs")}" as="x" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 3px; padding: 6px 0; border-top: 1px solid {LINE};">'
           f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><b style="font-size: 13px;">{H("x.t")}</b><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.c")}</span></div>'
           f'<div style="font-size: 12.5px; color: {MUTED}; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{H("x.s")}</div></div></sc-for>'
           + IF('oc_mais',f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 6px; border-top: 1px solid {LINE};">{H("oc_mais_t")}</div>') + '</div>'))
    js='''const fila=mbFila(c); const t=mbTurno(c); const sel=mbSelGet(); mbVerComo(self,v,c); const us=mbUsuario(c); const mv=mbManView(c);
const osSel=s.oc_os||(t?t.os:(fila.find(o=>o.id===sel)?sel:(fila[0]?fila[0].id:'')));
v.oc_ords=fila.map(o=>({t:o.id+' · '+o.talhao,on:o.id===osSel,st:mbPill(o.id===osSel),fn:()=>self.setState({oc_os:o.id}),tt:'Registrar na '+o.id+' · '+o.tipo}));
const TIPOS=['Equipamento','Clima','Praga ou doença','Falha de aplicação','Segurança','Outro']; const tipo=s.oc_tipo||'Equipamento';
v.oc_tipos=TIPOS.map(x=>({t:x,on:x===tipo,st:mbPill(x===tipo),fn:()=>self.setState({oc_tipo:x,oc_err:''}),tt:'Tipo: '+x}));
// PCM S4: máquina da O.S. (alocação) ou do turno; a que veio do MB-09 (#ativo=) já vem escolhida; Segurança pode ser "Sem máquina" (fica na O.S.)
const hm=(String(location.hash||'').match(/ativo=([\\w-]+)/)||[])[1]; const maq=tipo==='Equipamento'||tipo==='Segurança';
const rsO=osSel?MAN_AL.aloc.filter(x=>x.os===osSel).map(x=>x.r):[]; const ids=Object.keys(MAN_AL.rec).filter(id=>rsO.indexOf(MAN_AL.rec[id])>=0&&mv.ativos[id]);
mbAtvCurtos(c,mv,us).ids.forEach(id=>{ if(ids.indexOf(id)<0) ids.push(id); }); if(hm&&mv.ativos[hm]&&ids.indexOf(hm)<0) ids.unshift(hm);
const aid=s.oc_aid!==undefined?s.oc_aid:((hm&&mv.ativos[hm])?hm:(tipo==='Equipamento'&&ids.length===1?ids[0]:''));
v.oc_maq=maq; v.oc_atvs=(tipo==='Segurança'?[{id:'',t:'Sem máquina'}]:[]).concat(ids.map(id=>({id,t:mv.ativos[id].nome})))
  .map(x=>({t:x.t,on:String(x.id===aid),st:mbPill(x.id===aid),fn:()=>self.setState({oc_aid:x.id,oc_err:''}),tt:x.id?'Máquina: '+x.t:'Segurança sem máquina: fica como ocorrência da O.S.'}));
v.oc_maqt=maq?(aid?'Vai como achado para a Manutenção (Sem ordem)'+(osSel?', ligado à '+osSel:'')+'; o Otávio decide o serviço.':(tipo==='Equipamento'?'Escolha a máquina: a falha vai para a Manutenção.':'Sem máquina: fica como ocorrência da O.S.')):'';
const ach=maq&&!!aid; v.oc_ach=ach; const sg=s.oc_sug||'', cp=s.oc_comp||'';
v.oc_sugs=[['Sim','Apto'],['Com restrição','Restrito'],['Não','Bloqueado']].map(([x,k])=>({t:x,on:String(k===sg),st:mbPill(k===sg),fn:()=>self.setState({oc_sug:k,oc_err:''}),tt:'Pode operar? '+x}));
v.oc_comps=MAN_COMP.map(x=>({t:x,on:String(x===cp),st:mbPill(x===cp),fn:()=>self.setState({oc_comp:x,oc_err:''}),tt:'Componente: '+x}));
v.oc_hasRep=!!s.oc_repId; v.oc_repMsg=s.oc_repMsg||'';
v.oc_txt=s.oc_txt||''; v.oc_set=(e)=>self.setState({oc_txt:e.target.value,oc_err:''}); v.oc_err=s.oc_err||''; v.oc_err_has=!!s.oc_err;
const oo=c.ordens[osSel]; v.foto_lab=s.oc_foto?'Remover foto':'Anexar foto (simulado)'; v.oc_foto_t=s.oc_foto?'1 foto · GPS '+(oo?oo.talhao:'')+' (simulado)':'Sem foto · a foto e a voz são simuladas neste protótipo.';
v.foto=()=>{ const f=!self.state.oc_foto; self.setState({oc_foto:f,g2toast:f?'Foto anexada (simulado) · GPS do aparelho.':'Foto removida.'}); };
v.voz=()=>{ const cur=self.state.oc_txt||''; self.setState({oc_txt:(cur?cur+' ':'')+'Seção 3 da barra falhou; troquei o bico e segui.',oc_err:'',g2toast:'Voz transcrita (simulado) · revise o texto.'}); };
const done=s.oc_done; v.oc_novo=!done; v.oc_feito=!!done;
v.oc_aqui=done?done:'Nova ocorrência'; v.ct_f=done?'nada nesta ocorrência':'tipo e descrição'; v.ct_p=done?'Voltar à fila':'Registrar ocorrência';
const regAch=(rep)=>{ const st=self.state; const txt=String(st.oc_txt||'').trim(); if(!txt){ self.setState({oc_err:'Descreva a falha (ou use Ditar).'}); return; }
  const er=[]; if(!st.oc_comp) er.push('o componente'); if(!st.oc_sug) er.push('se pode operar'); if(er.length){ self.setState({oc_err:'Informe '+er.join(' e ')+'.'}); return; }
  const k=st.oc_k||self.__ock0||(self.__ock0=manChave()); const tp=st.oc_tipo||'Equipamento';
  const d={aid,origem:'Relato',comp:st.oc_comp,sint:txt+(tp==='Segurança'?' (segurança)':''),crit:{Apto:'Baixa',Restrito:'Média',Bloqueado:'Alta'}[st.oc_sug],sug:st.oc_sug,evid:st.oc_foto?'1 foto (simulada)':'',os:osSel||''};
  if(rep) d.rep=rep;
  const r=mbManCmd(self,'achado',{d},null,k);
  if(r.nada&&r.rep){ self.setState({oc_repId:r.rep,oc_repMsg:r.msg}); return; }
  if(!r.erro&&!r.nada){ self.setState({oc_done:'ACH|'+k,oc_achMsg:r.msg,oc_achFila:!!r.fila,oc_txt:'',oc_foto:false,oc_comp:'',oc_sug:'',oc_repId:'',oc_repMsg:'',oc_k:manChave()}); } };
v.oc_somar=()=>regAch('somar'); v.oc_novoAch=()=>regAch('novo');
v.registrar=()=>{ const st=self.state; const txt=String(st.oc_txt||'').trim();
  if(ach) return regAch(''); if(tipo==='Equipamento'){ self.setState({oc_err:'Escolha a máquina: a falha de equipamento vai para a Manutenção.'}); return; }
  if(!osSel) return TOAST(self,'Nenhuma ordem liberada na sua fila.');
  if(!txt){ self.setState({oc_err:'Descreva a ocorrência (ou use Ditar).'}); return; }
  const r=cenMudar(self,c=>cenOcorrencia(c,osSel,st.oc_tipo||'Equipamento',txt+(st.oc_foto?' · 1 foto (simulada)':'')));
  if(r&&!r.erro){ const cc=cenGet(); const oc=cc.ocorr[cc.ocorr.length-1]; self.setState({oc_done:oc.id,oc_txt:'',oc_foto:false}); } };
v.nova=()=>self.setState({oc_done:null,oc_err:'',oc_aid:undefined});
const achDone=!!done&&String(done).indexOf('ACH|')===0; const achNaFila=achDone&&manAppFila(c).some(q=>'ACH|'+q.chave===done);
if(achDone){ const rc=(c.man.recibos||{})[String(done).slice(4)]; v.d_t=(rc&&rc.id?rc.id+' · ':'')+'Achado na Manutenção'; v.d_txt=s.oc_achMsg||'';
  DCH(v,'dsc',achNaFila?'No aparelho · aguardando sinal':(rc?'Na Manutenção · Sem ordem':'Conflito a resolver · Otávio'),achNaFila?'yellow':(rc?'green':'red')); }
else if(done){ const oc=(c.ocorr||[]).find(x=>x.id===done); if(oc){ v.d_t=oc.id+' · '+oc.os+' · '+oc.tipo; v.d_txt=oc.texto; DCH(v,'dsc',oc.sinc?'Registrada na O.S. · '+oc.at:'No aparelho · aguardando sinal',oc.sinc?'green':'yellow'); } }
const mine=new Set(mbMinhas(c).map(o=>o.id)); const ocs=(c.ocorr||[]).filter(x=>mine.has(x.os)&&x.id!==done);
// Teto da lista (quadro de altura fixa): as 2 mais recentes; as demais seguem na O.S. (MB-02det).
v.has_ocs=ocs.length>0; v.oc_mais=ocs.length>2; v.oc_mais_t=ocs.length>2?'+ '+(ocs.length-2)+(ocs.length-2>1?' anteriores':' anterior')+' no detalhe de cada ordem':'';
v.ocs=ocs.slice(-2).reverse().map(x=>({t:x.id+' · '+x.os+' · '+x.tipo,s:x.texto,c:x.sinc?'na O.S. · '+x.at:'aguardando sinal',st:mbChs(x.sinc?'green':'yellow'),dot:mbDot(x.sinc?'green':'yellow')}));
const ocd=done&&(c.ocorr||[]).find(x=>x.id===done); const naf=achDone?achNaFila:!!(ocd&&!ocd.sinc);
DCH(v,'hdr',done?(naf?'no aparelho':(achDone?'enviada à Manutenção':'registrada')):'rascunho',done?(naf?'yellow':'green'):'gray');'''
    emit('MB-04','Registrar ocorrência','',None,
         'Registrar ocorrência',corpo,H_=1420,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
         dica='Funciona sem sinal: a ocorrência fica no aparelho e vai uma vez quando houver sinal. Falha de máquina vai para a Manutenção. Foto e voz são simuladas neste protótipo.',
         prim=[('oc_novo','b','Registrar ocorrência','registrar'),('oc_feito','a','Voltar à fila','MB-01.dc.html')])

    # ================= MB-05 · Almoxarifado móvel (lista · papéis) =================
    tabs=('<div role="tablist" aria-label="Papel" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px; align-self: flex-start;">'
          + ''.join(f'<button type="button" role="tab" onClick="{H("role"+str(i))}" style="{H("rs"+str(i))}">{esc(t)}</button>' for i,t in enumerate(['Minhas retiradas','Almoxarife']))+'</div>')
    operador=(
      sigbar()
      + IF('has_conf',h2v('al_conf_t','Confira itens, lote e embalagem antes de confirmar.')
           + f'<sc-for list="{H("conf")}" as="r" hint-placeholder-count="1"><div style="{CARD_ST}">'
             f'<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {YEL}; flex-shrink: 0;"></span>'
             f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;">{H("r.t")}</div></div>'
             f'<sc-for list="{H("r.itens")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 7px 0; border-top: 1px solid {LINE};">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 14px;"><b>{H("i.p")}</b><b>{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for>'
             + IF('r.btn',btns(f'<button type="button" onClick="{H("r.fn")}" title="{H("r.tt")}" style="{_NXST}">Confirmar recebimento</button>'))
             + '</div></sc-for>')
      + IF('has_cust',h2v('Com você','')
           + f'<div style="{CARD_ST}"><sc-for list="{H("cust")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0;">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px;"><b>{H("i.p")}</b><b style="color: {ACC};">{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for></div>')
      + IF('has_res',h2v('al_res_t','')
           + f'<div style="{CARD_ST}"><sc-for list="{H("res")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0;">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px;"><b>{H("i.p")}</b><b>{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for></div>')
      + IF('nada',card('Nada a retirar',[note('Quando o escritório liberar uma ordem sua com insumos, a reserva aparece aqui.')])))
    almox=(
      card(f'Receber devolução · <b>{REQ["id"]}</b> · {REQ["os"]}',[
          kv('Produto',f'{REQ["item"]} · {REQ["un"]}'),
          kv('Conta',f'entregue {REQ["entregue"]} · consumo {REQ["consumido"]} · devolvido {REQ["dev_recebida"]} · <b>custódia {REQ["custodia"]} sc com Paula</b>'),
          chips(chip(f'{REQ["custodia"]} sc a receber · OS-0417 em conferência','yellow'))],state='yellow')   # MB-05det só simula o DV-0912 (Frente F)
      + card(f'Conferir e entregar · <b>{R38["id"]}</b> · {R38["os"]} fertirrigação',[
          kv('Produto',f'{R38["item"]} · {nf(R38["solicitado"])} kg (12 kg/ha × 95 ha)'),
          chips(chip('Aguardando liberação da O.S.','yellow'),chip('Saldo apto 0 kg','red')),
          btns(say('Conferir e entregar · bloqueado',f'Bloqueado: a {R38["os"]} aguarda a liberação no escritório e a {R38["item"]} não tem saldo apto (0 kg) — nada foi separado.','alert','Ver por que não pode entregar'))],state='yellow')
      # revisão do 853a6a8 (achado 6, S3): lote, uso da safra e pendência de compra AO VIVO, da mesma demanda do Planejar safra e da Compra
      # (dados2.js_dem_viva) — nunca "sem pendência" da semente com a demanda pedindo complemento. Sem pendência não há conflito a registrar
      # (revisão do CTL-4, S4: congelar reservas sem conflito travaria a entrega da OS-0424 à toa).
      + IF('mbfa_conf',card(f'Conflito de reserva · lote {F02["lote"]} · {F02["item"]}',[
          kv('Saldo',H('mbfa_saldo')),
          kv('Conflito','a demanda da safra pede '+H('mbfa_plan')+' de hoje em diante · pendência de compra de '+H('mbfa_pend')+' (complemento no Planejar safra)'+H('mbfa_condc')),
          chips(chip('Conflito · decide o planejamento','red')+IF('mbfa_cond',chip(H('mbfa_condt'),'yellow'))),   # falta firme + qualidade pendente (revisão do 16fb55e, ajuste 1)
          btns(say('Registrar divergência','Divergência registrada com dono (planejamento) e prazo · reservas congeladas até a decisão — nada foi entregue.','alert','Registrar a divergência física do lote'))],state='red'))
      + IF('mbfa_ok',card(f'Reserva da safra · lote {F02["lote"]} · {F02["item"]}',[
          kv('Saldo',H('mbfa_saldo')),
          kv('Safra','uso de hoje em diante '+H('mbfa_plan')+' (O.S. abertas pelo pendente + plano sem O.S.) · '+H('mbfa_okt')),
          chips(IF('mbfa_cond',chip(H('mbfa_condt'),'yellow'))+IF('mbfa_semp',chip('Sem pendência de compra','green')))],state='green')))
    corpo=tabs+IF('r0',operador)+IF('r1',almox)
    js=f'''const r0=(s.role||0)===0; v.r0=r0; v.r1=!r0;
{{ const fa=demViva('Fungicida A')||{{liq:0,cond:0,bruta:0}}; const lf=c.lotes['Fungicida A|F26-02']||{{fisico:0,reservado:0,quarentena:0}};   /* a mesma demanda do Planejar safra e da Compra, viva */
  const n1=(x)=>Number(x||0).toLocaleString('pt-BR',{{minimumFractionDigits:1,maximumFractionDigits:1}})+' L';   /* o mesmo formato do Planejar safra e do SU-03det */
  v.mbfa_conf=fa.liq>0.05; v.mbfa_ok=!v.mbfa_conf; v.mbfa_cond=fa.cond>0.05; v.mbfa_semp=!v.mbfa_cond; v.mbfa_plan=n1(fa.bruta); v.mbfa_pend=n1(fa.liq); v.mbfa_condq=n1(fa.cond); v.mbfa_condt='Qualidade pendente · '+n1(fa.cond);
  v.mbfa_condc=v.mbfa_cond?(' · mais '+n1(fa.cond)+' dependem do laudo da quarentena (fora da compra; o gestor libera ou reprova no Estoque)'):'';
  v.mbfa_okt=v.mbfa_cond?(n1(fa.cond)+' dependem do laudo da quarentena; sem nova compra automática'):'sem pendência de compra: o estoque apto cobre';
  v.mbfa_saldo=cenNum(lf.fisico)+' L físicos · '+cenNum(lf.reservado)+' L reservados'+(lf.quarentena>1e-9?' · '+cenNum(lf.quarentena)+' L em quarentena':'')+' · '+cenNum(cenDisp(lf))+' L livres'; }}
[0,1].forEach(i=>{{ v['role'+i]=()=>self.setState({{role:i}}); v['rs'+i]='font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 14px; border-radius: 999px; border: 0; cursor: pointer; white-space: nowrap; '+(((s.role||0)===i)?'background: {SURF}; color: {INK}; box-shadow: 0 1px 2px rgba(21,32,26,.12);':'background: transparent; color: {MUTED};'); }});
// vindo do passo de uma ordem (MB-01 · MB-05.dc.html#OS-…): essa ordem vem primeiro e o selo a nomeia; sem âncora, a fila de sempre (AÇÃO v3.1)
const foco=(typeof location!=='undefined'&&/^#OS-[0-9]+$/.test(location.hash||''))?location.hash.slice(1):''; const fila0=mbFila(c);
const fila=foco?fila0.filter(o=>o.id===foco).concat(fila0.filter(o=>o.id!==foco)):fila0; const reqs=fila.map(o=>mbReq(c,o)).filter(Boolean);
const pend=reqs.filter(r=>r.itens.some(i=>i.custodia>0&&!i.confirmado));
const lot=(i)=>{{ const l=c.lotes[i.prod+'|'+i.lote]; return 'lote '+i.lote+(l&&l.validade&&l.validade!=='—'?' · val. '+l.validade:'')+(l?' · '+l.local:''); }};
v.conf=pend.map((r,ix)=>({{t:r.id+' · '+r.os+' · '+c.ordens[r.os].tipo,
  itens:r.itens.filter(i=>i.custodia>0&&!i.confirmado).map(i=>({{p:i.prod,q:cenNum(i.custodia)+' '+i.un,l:lot(i)+' · '+mbEmb(i,i.custodia)+(i.quem?' · entregue a '+i.quem:'')}})),
  btn:ix>0,fn:()=>cenMudar(self,c=>cenConfirmarRecebimento(c,r.id)),tt:'Confirmar recebimento da '+r.id}}));
v.has_conf=pend.length>0;
const cust=[]; const res=[];
reqs.forEach(r=>r.itens.forEach(i=>{{ if(i.custodia>0&&i.confirmado) cust.push({{p:i.prod,q:cenNum(i.custodia)+' '+i.un,l:lot(i)+' · '+r.os+' · consumido '+cenNum(i.consumido)+' '+i.un+(mbConf(c,r.os,i.prod)?' · consumo em conferência com '+CEN_CONC_RESP():(mbResta(c.ordens[r.os])<=0.001?' · área feita: devolva a sobra '+cenAoAlmox():''))}});
  else if(!(i.custodia>0)&&cenSaldoEntregar(i)>0) res.push({{p:i.prod,q:cenNum(cenSaldoEntregar(i))+' '+i.un,l:lot(i)+' · '+mbEmb(i,cenSaldoEntregar(i))+' · '+r.id+' · '+r.os}}); }}));
const alx=cenAlmoxNome(); v.al_conf_t='Entregue por '+((pend[0]&&cenEntPor(c,pend[0].id))||alx||'almoxarifado')+' · confirme';
v.al_res_t='Reservado · retire com '+(alx||'o almoxarife');   /* 14/10/2026: as descrições "Use na ordem…" e "Leve a O.S.…" foram para a dica ⓘ */
v.cust=cust; v.has_cust=cust.length>0; v.res=res; v.has_res=res.length>0; v.nada=!pend.length&&!cust.length&&!res.length;
v.p_conf=r0&&pend.length>0; v.p_back=r0&&!pend.length;
v.pc_lab='Confirmar recebimento'+(pend.length>1?' · '+pend[0].id:'');
v.pc_go=()=>{{ if(pend[0]) cenMudar(self,c=>cenConfirmarRecebimento(c,pend[0].id)); }};
if(r0) DCH(v,'hdr',(foco&&c.ordens[foco]?foco+' · ':'')+(pend.length?pend.length+(pend.length>1?' entregas a confirmar':' entrega a confirmar'):(cust.length?'insumos com você':'nada a confirmar')),pend.length?'yellow':'green');
else DCH(v,'hdr','1 devolução hoje','yellow');'''
    emit('MB-05','Almoxarifado móvel','',None,
         'Confirmar recebimento',corpo,H_=1220,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,pre_extra=D2.js_dem_viva('S2627'),
         dica='Confira itens, lote e embalagem antes de confirmar. Confirmar o recebimento põe o material sob sua custódia; o apontamento do turno baixa o consumo. '
              'Use na ordem; a sobra volta pela devolução ao almoxarife. Reservado: leve a O.S.; o almoxarife entrega por lote e embalagem. '
              'Irrigação só com água não aparece no almoxarifado: não cria fila nem documento de movimentação de produtos.',
         prim=[('p_conf','b',H('pc_lab'),'pc_go'),('p_back','a','Voltar à fila','MB-01.dc.html')])

    # ---- MB-05det · tarefa-âncora: receber devolução REQ-031 ----
    corpo=(
      mcont('Almoxarifado · fila',f'Devolução {REQ["id"]} · {REQ["os"]}',H('ct_f'),H('ct_p'))
      + card('Autorização e conta do material',[
          kv('O.S./versão','OS-0417 · v1 · adubação de cobertura P1'),
          kv('Produto',f'{REQ["item"]} · {REQ["un"]}'),
          kv('Solicitado/entregue',f'{REQ["solicitado"]} sc / {REQ["entregue"]} sc'),
          kv('Consumo apontado',f'{REQ["consumido"]} sc'),
          kv('Devolvido recebido',H('dev')),
          kv('Saldo em custódia',H('cus')),
          kv('Responsável pela custódia','Paula (equipe de campo)'),
          chips(dchip('rc'))],state='yellow')
      + btns(say('Registrar divergência','Recebidas 8 de 10 sc: pendência aberta com dono (Paula) e prazo · 2 sc seguem em custódia — nada foi zerado.','alert','Registrar quantidade diferente da esperada')))
    js=f'''const ok=!!s.rc; v.rc=ok; v.norc=!ok;
v.ct_f=ok?'nada nesta devolução':'conferir {REQ["custodia"]} sc e zerar custódia'; v.ct_p=ok?'Voltar ao almoxarifado':'Confirmar recebimento';
v.dev=ok?'{REQ["dev_recebida"]+REQ["custodia"]} sc':'{REQ["dev_recebida"]} sc'; v.cus=ok?'0 sc':'{REQ["custodia"]} sc';
DCH(v,'hdr',ok?'custódia zerada · DV-0912':'custódia {REQ["custodia"]} sc',ok?'green':'yellow');
DCH(v,'rc',ok?'Recebido · recibo DV-0912':'A receber',ok?'green':'yellow');
v.receber=()=>{{ self.setState({{rc:true,g2toast:'Recebidas {REQ["custodia"]} sc · recibo DV-0912 · custódia de Paula zerada · conta {REQ["entregue"]} = {REQ["consumido"]} + {REQ["dev_recebida"]+REQ["custodia"]} fechada · OS-0417 segue para o fechamento da conferência.'}}); }};'''
    emit('MB-05','Receber devolução',f'{REQ["id"]} · sobras da OS-0417',None,
         'Confirmar recebimento de 10 sc',corpo,H_=890,fname='MB-05det.dc.html',back='MB-05.dc.html',primary_href='MB-05.dc.html',js=js,dyn_status=True,
         dica=f'Confira as sacas contra o QR antes de confirmar. Ao confirmar: custódia zera, a conta {REQ["entregue"]} = {REQ["consumido"]} + {REQ["dev_recebida"]+REQ["custodia"]} fecha e a OS-0417 segue para o fechamento da conferência; '
             'sobras íntegras entram no lote M26-05 (sobras) até inspeção. Material preparado não retorna como produto original disponível; só sobra íntegra volta ao estoque.',
         prim=[('norc','b',f'Confirmar recebimento de {REQ["custodia"]} sc','receber'),('rc','a','Voltar ao almoxarifado','MB-05.dc.html')])

    # ================= MB-06 · Vistoria por pontos (coleta no app · estado compartilhado do MIP) =================
    # MB-06.dc.html#VIS-xxx abre a vistoria do estado 'talhao-os-mip-v1' (dados_mip.py + mip.js, a mesma do Mapa e do AG-01); sem hash,
    # a vistoria aberta de Marcos. Alvo, método, unidade, NC e pontos vêm do protocolo; registrar grava o ponto e concluir fecha a coleta
    # (completa ou incompleta). O resultado e a decisão ficam com o agrônomo no AG-01.
    import dados_mip as DM
    inp=(f'font-family: {DISP}; font-size: 22px; font-weight: 700; padding: 10px 12px; border-radius: 12px; border: 1px solid {LINE}; width: 100%; box-sizing: border-box; background: {SURF}; color: {INK};')
    # pontos coletados viram botão enquanto não há decisão: tocar carrega a contagem para corrigir (erro de digitação)
    pts=(f'<div style="display: flex; flex-wrap: wrap; gap: 5px;"><sc-for list="{H("mb_pts")}" as="q" hint-placeholder-count="12">'
         f'<button type="button" onClick="{H("q.go")}" disabled="{H("q.dis")}" title="{H("q.tt")}" aria-label="{H("q.tt")}" style="{H("q.st")}">{H("q.t")}</button></sc-for></div>')
    corpo=(
      mcont(H('mb_veio'),H('mb_aqui'),H('mb_falta'),H('mb_prox'))
      + note(H('mb_proto'))
      + IF('mb_aberta',
          f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="mb_cont" style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("mb_lbl")}</label>'
          f'<input id="mb_cont" type="text" inputMode="decimal" value="{H("mb_v")}" onChange="{H("mb_setv")}" placeholder="0" style="{inp}">'
          + IF('mb_err_has',f'<span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("mb_err")}</span>') + '</div>'
          f'<label style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: {INK};"><input type="checkbox" checked="{H("mb_gpsfora")}" onChange="{H("mb_toggps")}" style="width: 18px; height: 18px; accent-color: {RED}; margin: 0;">GPS fora da tolerância (ponto vai para recoleta)</label>'
          + IF('mb_ed',btns(f'<button type="button" onClick="{H("mb_edx")}" style="{_BST}">Cancelar correção</button>'))
          + '<div style="display: flex; gap: 8px;">'+counter('PONTO',H('mb_pt'))+counter('NC DO ALVO',H('mb_nc'))+counter('PARCIAL',H('mb_par'))+'</div>')
      + IF('mb_done',card('Coleta concluída',[note(H('mb_res'))],state='green'))
      + card(H('mb_ptsT'),[pts],state='gray')
      + IF('mb_podeConc',btns(f'<button type="button" onClick="{H("mb_conc")}" title="Fechar a coleta com os pontos registrados; os que faltam ficam como coleta incompleta" style="{_BST}">{icon("check",14)}{H("mb_concT")}</button>'))
      + IF('mb_temOutras',h2('Outras vistorias abertas')+f'<div style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("mb_outras")}" as="o" hint-placeholder-count="2">'
          f'<a href="{H("o.h")}" title="{H("o.tt")}" style="display: flex; justify-content: space-between; gap: 8px; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 12px; background: {SURF}; color: {INK}; text-decoration: none; font-size: 13px;">'
          f'<b>{H("o.t")}</b><span style="color: {MUTED};">{H("o.s")}</span></a></sc-for></div>'))
    # coleta: ponto da vez = o primeiro sem contagem, depois os de recoleta (mipAlvoPt); vistoria concluída com falta ou recoleta e sem
    # decisão reabre a coleta ("Completar coleta" do AG-01); a contagem é validada pelo protocolo (percentual até 100) e pode ser corrigida.
    js=r"""mipOuvir(self); const sm=mipGet(); let hh=''; try{ hh=decodeURIComponent(location.hash||''); }catch(e){ hh=''; }
if(!self.__mbh){ self.__mbh=1; try{ window.addEventListener('hashchange',()=>self.setState({mbv:'',mberr:'',mbgps:false,mbed:0,mbrev:Date.now()})); }catch(e){} }
const mh=/^#(VIS-\d+)$/.exec(hh); const ab=Object.values(sm.vis).filter(x=>x.est!=='concluida'||mipColetavel(x)).sort((a,b)=>((a.est==='coleta'?0:1)-(b.est==='coleta'?0:1))||(a.data<b.data?-1:1));
const vid=(mh&&sm.vis[mh[1]])?mh[1]:((ab.find(x=>x.resp==='Marcos')||ab[0]||{id:'VIS-014'}).id); const vv=sm.vis[vid];
const p=mipP(vv), t=mipT(vv), R=mipRes(vv,sm), nc=R.nc; const col=mipColetavel(vv); const alvo=col?mipAlvoPt(vv):null; const n=alvo?alvo.n:vv.npts; const done=!col;
const depois=col?(vv.pts.find(x=>x.n!==n&&(x.v===null||x.v===undefined))||vv.pts.find(x=>x.n!==n&&x.rec)):null; const reab=col&&vv.est==='concluida';
const ed=Number(s.mbed||0); const edq=(ed&&!vv.dec)?vv.pts.find(x=>x.n===ed&&x.v!==null&&x.v!==undefined):null; const edit=!!edq;
v.hdr_ttl='Vistoria '+vid; v.hdr_sub=t.rot+' · '+p.alvo.toLowerCase()+' · '+(edit?'corrigir ponto '+ed:(done?'coleta concluída':(reab?'completar coleta · ponto '+n:'ponto '+n+' de '+vv.npts)));
DCH(v,'hdr',done?'coleta concluída':(reab?'coleta incompleta':(vv.est==='programada'?'programada para '+mipBr(vv.data):'em coleta')),done?'gray':(reab?'yellow':'green'));
v.mb_veio='Pragas e doenças · '+vid; v.mb_aqui=t.rot+' · '+(edit?'corrigindo ponto '+ed:(done?(R.falt?'coleta fechada':'rota completa'):'ponto '+n+(alvo&&alvo.rec?' (recoleta)':'')+' de '+vv.npts));
v.mb_falta=R.falt?(R.falt+(R.falt===1?' ponto':' pontos')):(R.rec?(R.rec+' em recoleta'):'nada');
v.mb_prox=edit?'Corrigir ponto '+ed:(done?'Voltar ao início':(depois?'Registrar e ir ao ponto '+depois.n:'Registrar e concluir'));
v.mb_proto=p.alvo+' · '+p.met+' · '+p.un+(nc?' · NC '+mipN(nc)+' ('+t.fase+')':' · critério presença')+' · '+vv.resp;
v.mb_aberta=!done||edit; v.mb_done=done&&!edit; v.mb_ed=edit;
v.mb_lbl=edit?('Corrigir o ponto '+ed+' ('+p.un+')'):('Contagem no ponto '+n+(alvo&&alvo.rec?' · recoleta':'')+' ('+p.un+')'); v.mb_v=s.mbv||''; v.mb_setv=(e)=>self.setState({mbv:e.target.value,mberr:''});
v.mb_err=s.mberr||''; v.mb_err_has=!!s.mberr; v.mb_gpsfora=!!s.mbgps; v.mb_toggps=()=>self.setState({mbgps:!self.state.mbgps});
v.mb_edx=()=>self.setState({mbed:0,mbv:'',mbgps:false,mberr:''});
v.mb_pt=(edit?ed:n)+'/'+vv.npts; v.mb_nc=nc?mipN(nc):'presença'; v.mb_par=R.crit==='presenca'?(R.pres+' c/ sintoma'):(R.media===null?'—':mipN(R.media));
v.mb_res=R.col+' de '+R.tot+' pontos · '+(R.crit==='presenca'?R.pres+' com sintoma':(R.media===null?'—':'média '+mipN(R.media)+' '+p.un))+'. O agrônomo decide no escritório (Pragas e doenças).';
const podeEd=!vv.dec&&!(vv.pend||[]).length; v.mb_ptsT='Pontos da rota'+(podeEd&&R.col?' · toque para corrigir':'');
v.mb_pts=vv.pts.map(q=>{ const nul=q.v===null||q.v===undefined; const k=q.rec?['#EEF1EE','#5B6660']:(nul?['#FFFFFF','#8A968E']:(R.crit==='presenca'?(q.v>0?['#FFE8D6','#9A3F00']:['#E4F3E9','#1E7A4C']):(q.v>=nc?['#FDE8E6','#B42318']:(q.v>=0.8*nc?['#FFF3D6','#8A5A00']:['#E4F3E9','#1E7A4C']))));
  const pode=podeEd&&!nul; const foco=edit?q.n===ed:(q.n===n&&!done);
  return {t:String(q.n).padStart(2,'0')+(nul?'':' · '+mipN(q.v)),tt:'Ponto '+q.n+(nul?': não coletado':': '+mipN(q.v)+' '+p.un+(q.rec?' · recoleta':''))+(pode?' · tocar para corrigir':''),dis:!pode,
    go:()=>{ if(pode) self.setState({mbed:q.n,mbv:String(q.v).replace('.',','),mbgps:!!q.rec,mberr:''}); },
    st:'display:inline-flex;padding:3px 8px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:700;color:'+k[1]+';background:'+k[0]+';border:1px solid '+(nul?'#E4E9E5':k[0])+';'+(pode?'cursor:pointer;':'cursor:default;')+(foco?'box-shadow:0 0 0 2px #1E7A4C;':'')}; });
const reg=(fim)=>{ const cur=self.state; const ec=Number(cur.mbed||0);
  const r=mipMudar(null,s2=>{ if(ec) return mipCorrigir(s2,vid,ec,cur.mbv,!cur.mbgps); const a=mipColetar(s2,vid,cur.mbv,!cur.mbgps); if(fim){ const b=mipConcluir(s2,vid); return {msg:a.msg+' '+b.msg}; } return a; });
  if(r.erro){ self.setState({mberr:r.erro}); return; } self.setState({mbv:'',mbgps:false,mberr:'',mbed:0,g2toast:r.msg,miprev:Date.now()}); setTimeout(()=>{ const el=document.getElementById('mb_cont'); if(el) el.focus(); },60); };
v.mb_mid=!done&&!edit&&!!depois; v.mb_last=!done&&!edit&&!depois; v.mb_nxt='Registrar e ir ao ponto '+(depois?depois.n:''); v.mb_reg=()=>reg(false); v.mb_regfim=()=>reg(true);
v.mb_edt='Corrigir ponto '+ed; v.mb_corr=()=>reg(false);
v.mb_podeConc=!done&&!edit&&R.col>0&&vv.est!=='concluida'; v.mb_concT='Concluir com '+R.col+' de '+vv.npts+' pontos'; v.mb_conc=()=>mipMudar(self,s2=>mipConcluir(s2,vid));
v.mb_outras=ab.filter(x=>x.id!==vid&&x.faz===vv.faz).slice(0,4).map(x=>{ const t2=mipT(x), p2=mipP(x), r2=mipRes(x,sm); return {h:'MB-06.dc.html#'+x.id,t:x.id+' · '+t2.rot+' · '+p2.alvo,s:(x.est==='programada'?mipBr(x.data):r2.col+'/'+r2.tot),tt:'Abrir a vistoria '+x.id}; });
v.mb_temOutras=v.mb_outras.length>0;"""
    global JS_BASE
    _jb=JS_BASE; JS_BASE=DM.js_prefixo()+_jb
    try:
        emit('MB-06','Vistoria por pontos','',None,'Registrar e ir ao ponto',corpo,H_=940,back='MB-01.dc.html',primary_href='MB-06.dc.html',js=js,dyn_status=True,dyn_head='Vistoria por pontos',
             prim=[('mb_ed','b',H('mb_edt'),'mb_corr'),('mb_mid','b',H('mb_nxt'),'mb_reg'),('mb_last','b','Registrar e concluir coleta','mb_regfim'),('mb_done','a','Voltar ao início','MB-01.dc.html')])
    finally:
        JS_BASE=_jb

    # ================= MB-07 · Contagem de frutos (no estado: prContar · colheita P6) =================
    # Talhão por um toque entre os de fruta em produção; +/− por estádio em cada planta (Pintado: colher nesta semana · De vez: próxima ·
    # Verde desenvolvido: em 2 semanas); peso médio da amostra; "Concluir talhão" grava a contagem (CNT-) e NÃO publica: Ana publica
    # em Produção › Previsão e colheita. Sem sinal, a contagem fica no aparelho e entra uma vez ao voltar o sinal.
    est=''.join(
        f'<div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-top: 1px solid {LINE};">'
        f'<div style="flex-grow: 1; min-width: 0;"><div style="font-size: 14px; font-weight: 700;">{lab}</div><div style="font-size: 12px; color: {MUTED};">{dica}</div></div>'
        f'<button type="button" onClick="{H("m7_menos_"+k)}" aria-label="Menos um fruto {lab}" title="Menos um fruto {lab}" style="{_BST} width: 44px; height: 44px; justify-content: center; font-size: 20px;">−</button>'
        f'<span aria-live="polite" style="font-family: {DISP}; font-size: 24px; font-weight: 700; min-width: 40px; text-align: center;">{H("m7_n_"+k)}</span>'
        f'<button type="button" onClick="{H("m7_mais_"+k)}" aria-label="Mais um fruto {lab}" title="Mais um fruto {lab}" style="{_BST} width: 44px; height: 44px; justify-content: center; font-size: 20px;">+</button></div>'
        for k,lab,dica in (('pintado','Pintado','colher nesta semana'),('devez','De vez','colher na próxima semana'),('verde','Verde desenvolvido','colher em 2 semanas')))
    corpo=(
      sigbar()
      + h2('Talhão','Toque no talhão de fruta em produção que vai contar.')
      + f'<div role="group" aria-label="Talhão" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("m7_tals")}" as="x" hint-placeholder-count="4"><button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" title="{H("x.tt")}" style="{H("x.st")}">{H("x.t")}</button></sc-for></div>'
      + IF('m7_ok',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
           f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">{H("m7_okt")}</div></div><div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("m7_oks")}</div></div>')
      + IF('m7_tem',
           f'<div style="{CARD_ST}"><div style="display: flex; align-items: baseline; gap: 8px;"><div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">{H("m7_pl")}</div>'
           f'<span style="font-size: 12.5px; color: {MUTED};">{H("m7_falta")}</span></div>{est}</div>'
           + ffield('Peso médio do fruto da amostra','mb_peso','m7_peso','m7_setpeso','m7_epeso',hint='kg por fruto (pese alguns frutos e divida).',ph='ex.: 1,20')
           + note(H('m7_amostra'))
           + IF('m7_err',f'<div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("m7_errt")}</div>')
           + btns(fnb('Corrigir a última planta','m7_corr','clock','Devolver a última planta registrada para os contadores'),
                  fnb(H('m7_conct'),'m7_conc','check','Gravar a contagem do talhão (não publica a previsão)'))))
    js='''const tals=Object.keys(PRDC.cult).filter(id=>PRDC.cult[id].semanal&&PRDC.cult[id].prod).sort((a,b)=>String(PRDC.cult[a].local).localeCompare(String(PRDC.cult[b].local),'pt-BR',{numeric:true}));
let h=''; try{ h=decodeURIComponent(location.hash||'').slice(1); }catch(e){}
/* chave de quem inicia (R-07): nasce ao escolher o talhão e vale até gravar; nunca da contagem do estado (revisão A-09) */
const m7ch=(id)=>'APP-CNT-'+id+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8);
if(!s.m7&&PRDC.cult[h]&&!self.__m7ch) self.__m7ch=m7ch(h);
const m=s.m7||{cult:(PRDC.cult[h]?h:''),pl:[],cur:{pintado:0,devez:0,verde:0},ch:self.__m7ch||''}; const cid=m.cult; const k=PRDC.cult[cid];
const set=(x)=>self.setState({m7:Object.assign({},m,x),m7err:''});
v.m7_tals=tals.map(id=>({t:PRDC.cult[id].local,on:String(id===cid),st:mbPill(id===cid),tt:'Contar '+PRDC.cult[id].local+' · '+PRDC.cult[id].faz,go:()=>self.setState({m7:{cult:id,pl:[],cur:{pintado:0,devez:0,verde:0},ch:m7ch(id)},m7err:'',m7ok:null})}));
v.m7_tem=!!k; const n=m.pl.length; const ALVO=20;
v.m7_pl=k?k.local+' · planta '+(n+1)+' de '+ALVO:''; v.m7_falta=n>=ALVO?'amostra completa':(ALVO-n)+(ALVO-n===1?' planta a contar':' plantas a contar');
['pintado','devez','verde'].forEach(e=>{ v['m7_n_'+e]=String(m.cur[e]||0);
  v['m7_mais_'+e]=()=>set({cur:Object.assign({},m.cur,{[e]:(m.cur[e]||0)+1})}); v['m7_menos_'+e]=()=>set({cur:Object.assign({},m.cur,{[e]:Math.max(0,(m.cur[e]||0)-1)})}); });
const tot=e=>m.pl.reduce((a,x)=>a+x[e],0);
v.m7_amostra=n?('Amostra: '+n+(n>1?' plantas':' planta')+' · Pintado '+tot('pintado')+' · De vez '+tot('devez')+' · Verde desenvolvido '+tot('verde')):'Nenhuma planta registrada ainda.';
v.m7_peso=s.m7peso||''; v.m7_setpeso=(e)=>self.setState({m7peso:e.target.value,m7err:''}); v.m7_epeso=''; v.m7_epeso_has=false;
v.m7_err=!!s.m7err; v.m7_errt=s.m7err||'';
v.m7_reg=()=>{ if(!k) return; self.setState({m7:Object.assign({},m,{pl:m.pl.concat([m.cur]),cur:{pintado:0,devez:0,verde:0}}),m7err:'',g2toast:'Planta '+(n+1)+' registrada · planta '+(n+2)+' aberta · contadores zerados.'}); };
v.m7_corr=()=>{ if(!n){ TOAST(self,'Nenhuma planta registrada para corrigir.'); return; } const ult=m.pl[n-1]; self.setState({m7:Object.assign({},m,{pl:m.pl.slice(0,-1),cur:ult}),g2toast:'Planta '+n+' de volta aos contadores para corrigir · histórico só grava ao concluir.'}); };
v.m7_conct='Concluir talhão'+(n?' ('+n+(n>1?' plantas)':' planta)'):'');
v.m7_conc=()=>{ if(!n){ self.setState({m7err:'Registre ao menos uma planta antes de concluir.'}); return; }
  const ch=m.ch||m7ch(cid);
  const r=cenMudar(self,c=>prContar(c,{cult:cid,plantas:n,pintado:tot('pintado'),devez:tot('devez'),verde:tot('verde'),peso:s.m7peso||'',quem:c.app.operador,via:'app',chave:ch}));
  if(r.erro){ self.setState({m7err:r.erro}); return; } self.__m7ch=''; self.setState({m7:{cult:'',pl:[],cur:{pintado:0,devez:0,verde:0}},m7peso:'',m7ok:{t:r.cnt.id+' · '+PRDC.cult[cid].local,s:r.msg}}); };
v.m7_ok=!!s.m7ok&&!k; v.m7_okt=s.m7ok?s.m7ok.t:''; v.m7_oks=s.m7ok?s.m7ok.s:'';
v.m7_pr=!!k; v.m7_prt='Registrar e ir à planta '+(n+2); v.m7_sem=!k;
DCH(v,'hdr',k?(k.local+' · planta '+(n+1)):(s.m7ok?'contagem gravada':'escolha o talhão'),k?'green':(s.m7ok?'green':'gray'));'''
    emit('MB-07','Contagem de frutos','',None,
         'Registrar e ir à planta 2',corpo,H_=1180,back='MB-01.dc.html',primary_href='MB-07.dc.html',js=js,dyn_status=True,cen=True,
         dica='Toque no talhão de fruta em produção que vai contar; a contagem é por planta e estádio. A previsão não é publicada a cada planta: '
              'a contagem vira rascunho e Ana (agrônoma) publica em Produção › Previsão e colheita.',
         prim=[('m7_pr','b',H('m7_prt'),'m7_reg'),('m7_sem','a','Voltar a Hoje no campo','MB-01.dc.html')])

    # ================= MB-08 · Irrigação móvel (detalhe · volta em curso) =================
    exec_txt=f'{br(P["lamina_aplicada"])} mm em ≈{br(AREA_COB)} de {AREA_PIVO} ha ({br(P["cobertura_pct"])}% da volta · estimativa por percentímetro)'
    corpo=(
      mcont('Irrigação de hoje','OS-0419 · Pivô 2 · água','confirmar término da volta','Confirmar término')
      + card('Lâmina que a cultura precisa',[
          kv('Origem',f'balanço de 23/09 · déficit 11,2 mm → {br(P["lamina_aplicada"])} mm brutos em 1 passada (máx. {br(POL["lamina_max"])} mm por passada)'),
          chips(chip(f'Liberada sem aprovação · {IRR["au"]}','green'),tag(IRR['lib']))],state='blue')
      + card('Alvo e andamento desta volta',[
          kv('Janela',f'hoje {IRR["janela"]} · 1 volta de {IRR["dur"]} · iniciada {IRR["ini"]} ({IRR["ex"]}) · término previsto {IRR["fim"]}'),
          kv('Percentímetro',f'<b>{P["percent"]}%</b> → lâmina {br(P["lamina_aplicada"])} mm (100% = {br(P["lamina_100"])} mm)'),
          kv('Andamento',f'≈{br(AREA_COB)} de {AREA_PIVO} ha ({br(P["cobertura_pct"])}% da volta) · {br(P["exec_h"])} de {IRR["dur"]} executadas'),
          kv('Medidores',f"{_DI.eq_nome('a11')} · {_DI.eq_vazao_ls('a11')} L/s · pressão 2,8 bar · ponta parcial 20–21 h"),   # nome e vazão do cadastro e da ficha do pivô (A7)
          chips(prazo('irrigando','volta em curso'))],state='green')
      + h2('Ações da volta','Registre pausas e avanço sem encerrar a ordem.')
      + btns(say('Pausar','Pausada · queda de pressão na '+_DI.eq_nome('a11')+' · o tempo parado não conta como lâmina e empurra o término previsto.','clock','Pausar a volta com motivo'),
             say('Retomar','Retomada · pressão normalizada · término previsto recalculado pelo tempo parado.','check','Retomar a volta'),
             say('Registrar avanço',f'Avanço registrado: {br(P["exec_h"])} h · {exec_txt} · balanço hídrico atualizado 1× por aplicação.','drop','Registrar o avanço da volta'))
      + btns(say('Finalizar apontamento do turno','Turno do irrigante finalizado · a ordem segue Em execução — finalizar o turno nunca conclui.','doc','Guardar o turno sem concluir'),
             say('Próximo setor','Sem outro setor liberado hoje · a OS-0422 (13,5 mm em 2 passadas) libera quando a janela for definida.','pivot','Ver o próximo setor liberado'))
      + card('Próximo ciclo',[
          note(f'<b>OS-0422</b> · 13,5 mm em <b>2 passadas de 6,75 mm</b> (máx. {br(POL["lamina_max"])} mm por passada) · janela a definir')],state='gray'))   # 14/10/2026: só o dado; a regra da divisão foi para a dica ⓘ
    emit('MB-08','Irrigação de hoje','',('Em execução · irrigando','green'),
         'Confirmar término da irrigação',corpo,H_=1430,back='MB-01.dc.html',primary_href='MB-08x-recibo.dc.html',
         dica='Água sem produto: sem emissão manual, sem materiais, sem requisição, sem custódia e sem devolução. Confira a lâmina antes de iniciar; registre pausas e avanço sem encerrar a ordem '
              'e confirme o término no fim. Lâmina acima do máximo por passada é dividida pelo sistema em passadas iguais, sem aprovação; a ordem libera quando a janela for definida. '
              'Só a fertirrigação (OS-0418) é liberada pelo agrônomo, com materiais e requisição próprios. Área ou volume insuficientes: registra-se o tempo e a '
              'estimativa fica pendente; a lâmina não é afirmada como medida. Não existe “Encerrar e apontar”.')

    # ---- MB-08x-recibo · término confirmado, conferência automática (estado) ----
    corpo=(
      mcont('Irrigação · OS-0419 · Pivô 2',f'Término confirmado · {IRR["fim_d"]}','próximo ciclo: OS-0422 (13,5 mm em 2 passadas)','Voltar à fila do turno')
      + vstep([(f'Lâmina pelo balanço · {IRR["au"]}','done'),(f'Liberação por prontidão · {IRR["lib"]}','done'),
               (f'Execução · {br(P["lamina_aplicada"])} mm nos {AREA_PIVO} ha (volta completa)','done'),('Conferida e encerrada','done')],'')
      + card('Recibos do evento',[
          kv('Origem da lâmina',f'{IRR["au"]} · balanço de 23/09 · memória de cálculo'),
          kv('Liberação',f'{IRR["lib"]} · prontidão validada às 06:12, antes de iniciar'),
          kv('Execução',f'{IRR["ex"]} · {IRR["ini"]}–{IRR["fim_d"]} · {IRR["dur"]} · {br(P["lamina_aplicada"])} mm nos {AREA_PIVO} ha (volta completa · estimativa por percentímetro)'),
          kv('Conferência',f'{IRR["medido"]} mm medidos × {br(P["lamina_aplicada"])} mm estimados ({IRR["dif"]}, tolerância 3%)'),
          chips(chip('Conferida e encerrada automaticamente','green')),
          note(f'Balanço hídrico: {IRR["medido"]} mm creditados nos {AREA_PIVO} ha do pivô.')],
          state='green'))
    emit('MB-08','Irrigação · recibo do término','',('Encerradas','gray'),
         'Voltar à fila do turno',corpo,H_=1120,fname='MB-08x-recibo.dc.html',back='MB-08.dc.html',primary_href='MB-01.dc.html',
         dica='Mapa, lista, quadro e app leem o mesmo evento. Fatos consistentes levam à conferência e ao encerramento automáticos, com recibos separados; o balanço hídrico é atualizado uma vez por aplicação. '
              'Quando não fecha sozinho: horímetro divergente da lâmina calculada deixa a ordem Em conferência com o motivo exibido; corrigir a calibração do pivô substitui a fórmula anterior.')

    # ================= MB-09 · Máquina (PCM simplificado S4, §3.7) =================
    # Ativo herdado do turno (senão lista curta com busca); condição em texto ("Não opere" quando Bloqueado), leitura com data e OM aberta.
    # Primária "Registrar abastecimento" (com "Salvar e registrar outro"); secundárias "Registrar leitura" e "Reportar falha" (MB-04 com o ativo).
    # Grava pelas mesmas funções da tela MA (manAbastecer, manLeituraAvulsa) com a chave do aparelho; sem sinal, vai para a fila.
    recst=f'display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; border-radius: 12px; font-size: 13px; font-weight: 700; line-height: 1.4;'
    corpo=(
      sigbar()
      + h2('Máquina','Herdada do seu turno; toque noutra ou busque pelo nome.')
      + pills('mq_curtos','Máquinas do turno',2)
      + f'<input id="mq-busca" type="search" aria-label="Buscar máquina" placeholder="Buscar máquina" value="{H("mq_q")}" onChange="{H("mq_setq")}" style="{INP}">'
      + IF('mq_hasSug',pills('mq_sug','Máquinas encontradas',3))
      + IF('mq_sem',card('Escolha a máquina',[note('Toque numa máquina do turno ou busque pelo nome.')]))
      + IF('mq_tem',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="{H("mq_dot")}"></span>'
           f'<div style="font-size: 15px; font-weight: 700; flex-grow: 1; min-width: 0;">{H("mq_nome")}</div></div>'
           f'<div role="status" style="{H("mq_cst")}">{H("mq_cond")}</div>'
           f'<div style="font-size: 13px; color: {MUTED};">{H("mq_leit")}</div>'
           + IF('mq_hasOm',f'<div><a href="{H("mq_omh")}" onClick="{H("mq_omsel")}" title="Abrir a ordem de manutenção aberta desta máquina" style="{_BST} text-decoration: none;">{icon("wrench",14)}{H("mq_omt")}</a></div>')
           + note(H('mq_her')) + '</div>')
      + IF('mq_rec',f'<div role="status" style="{recst} {H("mq_recst")}">✓ {H("mq_rect")}</div>')
      + IF('mq_ab',h2('Registrar abastecimento','Tanque, volume e leitura; a foto do tíquete é a evidência.')
           + f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Tanque · lote")}' + pills('mq_tqs','Tanque e lote',2) + '</div>'
           + ffield('Volume · L','mq-vol','mq_vol','mq_setvol','',big=True,ph='0')
           + IF('mq_hasCont',ffield(H('mq_unl'),'mq-leit','mq_leitv','mq_setleit','',hint=H('mq_ult'),ph='leitura no painel'))
           + btns(f'<button type="button" aria-pressed="{H("mq_cheio")}" onClick="{H("mq_tcheio")}" title="Marque quando completou o tanque: calcula o consumo" style="{H("mq_cheiost")}">{H("mq_cheiot")}</button>',
                  f'<button type="button" onClick="{H("mq_foto")}" title="Anexar a foto do tíquete (simulado)" style="{_BST}">{icon("doc",14)}{H("mq_fotol")}</button>')
           + note(H('mq_fotot'))
           + f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Operador da máquina")}' + pills('mq_ops','Operador da máquina',3) + note(H('mq_opsug')) + '</div>'
           + f'<div style="font-size: 13px; color: {MUTED};">{kv("Data",H("mq_data"))}</div>'
           + btns(fnb('Salvar e registrar outro','mq_outro','fuel','Gravar este lançamento e limpar para o próximo tíquete (fica só a data)')))
      + IF('mq_lt',h2('Registrar leitura','Leitura avulsa do contador, com a data em que foi lida.')
           + ffield(H('mq_unl'),'mq-lt','mq_ltv','mq_setlt','',big=True,hint=H('mq_ult'),ph='leitura no painel')
           + f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Data da leitura")}' + pills('mq_ltdias','Data da leitura',2) + '</div>')
      + IF('mq_tem',btns(IF('mq_isAb',IF('mq_hasCont',fnb('Registrar leitura','mq_modoLt','clock','Registrar só a leitura do contador'))),
                         IF('mq_isLt',fnb('Voltar ao abastecimento','mq_modoAb','fuel','Voltar ao lançamento de abastecimento')),
                         f'<a href="{H("mq_falhah")}" title="Abrir a ocorrência de equipamento com esta máquina" style="{_BST} text-decoration: none;">{icon("alert",14)}Reportar falha</a>'))
      + IF('mq_hasHist',f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">Últimos registros desta máquina</div>'
           f'<sc-for list="{H("mq_hist")}" as="x" hint-placeholder-count="2"><div style="display: flex; flex-direction: column; gap: 3px; padding: 6px 0; border-top: 1px solid {LINE};">'
           f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><b style="font-size: 13px;">{H("x.t")}</b><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.c")}</span></div>'
           f'<div style="font-size: 12.5px; color: {MUTED}; line-height: 1.4;">{H("x.s")}</div></div></sc-for></div>'))
    js='''const mv=mbManView(c); const us=mbUsuario(c); mbVerComo(self,v,c); const cur=mbAtvCurtos(c,mv,us);
const hm=(String(location.hash||'').match(/ativo=([\\w-]+)/)||[])[1];
let aid=s.mq_aid; if(!aid) aid=(hm&&mv.ativos[hm])?hm:(cur.ids[0]||''); if(aid==='-') aid=''; const a=aid?mv.ativos[aid]:null;
v.mq_curtos=cur.ids.map(id=>({t:mv.ativos[id].nome,on:String(id===aid),st:mbPill(id===aid),fn:()=>self.setState({mq_aid:id,mq_rec:null,mq_tq:undefined,mq_opk:undefined}),tt:'Escolher '+mv.ativos[id].nome}));
const q=String(s.mq_q||'').trim().toLowerCase(); v.mq_q=s.mq_q||''; v.mq_setq=(e)=>self.setState({mq_q:e.target.value});
const sug=q?Object.values(mv.ativos).filter(x=>x.nome.toLowerCase().indexOf(q)>=0||String(x.modelo||'').toLowerCase().indexOf(q)>=0).slice(0,5):[];
v.mq_sug=sug.map(x=>({t:x.nome,on:String(x.id===aid),st:mbPill(x.id===aid),fn:()=>self.setState({mq_aid:x.id,mq_q:'',mq_rec:null,mq_tq:undefined,mq_opk:undefined}),tt:'Escolher '+x.nome})); v.mq_hasSug=sug.length>0;
v.mq_tem=!!a; v.mq_sem=!a; v.mq_hasCont=!!(a&&a.un);
const cd=mbCond(a); v.mq_nome=a?manNome(a):''; v.mq_cond=cd.t; v.mq_cst=mbCondSt(cd.c); v.mq_dot='width: 10px; height: 10px; border-radius: 999px; flex-shrink: 0; background: '+(MBC[cd.c]||MBC.gray)[0]+';';
v.mq_leit=a?(a.un?('Leitura '+manLeitTxt(a)+(a.suspeita?' · leitura a confirmar (Otávio)':'')):'Sem contador'):'';
const om=a?Object.values(mv.oms).filter(o=>o.aid===a.id&&manAberta(o)).sort((x,y)=>MAN_FASES.indexOf(y.etapa)-MAN_FASES.indexOf(x.etapa))[0]:null;
v.mq_hasOm=!!om; v.mq_omh=om?'MB-09det.dc.html#'+om.id:'MB-09.dc.html'; v.mq_omt=om?(om.id+' · '+om.etapa+' · abrir ordem'):''; v.mq_omsel=()=>{ if(om) mbOmSet(om.id); };
v.mq_her=a?((cur.ids.indexOf(a.id)>=0&&cur.de)?('Herdada '+cur.de):'Escolhida por você'):'';   /* 14/10/2026: "toque noutra para trocar" foi para a dica ⓘ */ v.mq_falhah=a?'MB-04.dc.html#ativo='+a.id:'MB-04.dc.html';
DCH(v,'hdr',a?(a.cond==='Bloqueado'?'Não opere':(a.cond==='Restrito'?'Com restrição':'Apto')):'escolha a máquina',a?cd.c:'gray');
const modo=(s.mq_modo==='lt'&&a&&a.un)?'lt':'ab'; v.mq_ab=!!a&&modo==='ab'; v.mq_lt=!!a&&modo==='lt'; v.mq_isAb=modo==='ab'; v.mq_isLt=modo==='lt';
v.mq_pab=v.mq_ab; v.mq_plt=v.mq_lt; v.mq_pnone=!a;
v.mq_modoLt=()=>self.setState({mq_modo:'lt',mq_rec:null}); v.mq_modoAb=()=>self.setState({mq_modo:'ab',mq_rec:null});
const tqs=a?manTanques(mv,a.id):[]; const tq=(s.mq_tq&&tqs.indexOf(s.mq_tq)>=0)?s.mq_tq:(tqs.length===1?tqs[0]:'');
v.mq_tqs=tqs.map(x=>({t:x,on:String(x===tq),st:mbPill(x===tq),fn:()=>self.setState({mq_tq:x}),tt:'Tanque e lote: '+x}));
v.mq_vol=s.mq_vol||''; v.mq_setvol=(e)=>self.setState({mq_vol:e.target.value});
v.mq_unl=a&&a.un==='km'?'Odômetro · km':'Horímetro · h'; v.mq_leitv=s.mq_leit||''; v.mq_setleit=(e)=>self.setState({mq_leit:e.target.value}); v.mq_ult=a&&a.leit?('Última: '+manLeitTxt(a)):'';
v.mq_cheio=String(!!s.mq_cheio); v.mq_cheiost=mbPill(!!s.mq_cheio); v.mq_tcheio=()=>self.setState({mq_cheio:!self.state.mq_cheio});
v.mq_fotol=s.mq_foto?'Remover foto':'Anexar foto (simulado)'; v.mq_fotot=s.mq_foto?'1 foto do tíquete (simulada)':'Sem foto · a foto é simulada neste protótipo.'; v.mq_foto=()=>self.setState({mq_foto:!self.state.mq_foto});
/* S4 da revisão (09/10): o operador do abastecimento é quem opera a máquina, não quem lança. Operador do app: ele mesmo; mecânico ou eletricista: o operador
   da alocação de hoje (O.S. › Recursos), corrigível; sem alocação, escolher (nunca o próprio mecânico por padrão) */
const opDef=mbPapelUs(us)==='operador'?us:(a?manOperadorDia(mv,a.id,mv.hoje):''); const op=s.mq_opk!==undefined?s.mq_opk:opDef;
v.mq_ops=MAN_OPS.map(x=>({t:x+(x===us?' (você)':''),on:String(x===op),st:mbPill(x===op),fn:()=>self.setState({mq_opk:x===op?'':x}),tt:'Operador da máquina: '+x}));
v.mq_opsug=op?(op===us?'Você opera esta máquina · corrigível':('Operador '+(op===opDef&&opDef?'da alocação de hoje':'escolhido')+': '+op+' · corrigível')):'Sem alocação hoje: escolha quem opera a máquina.';
v.mq_cheiot='Tanque cheio · calcula '+(a&&a.un==='km'?'km/L':'L/h');
v.mq_op=op; v.mq_data=manBr(mv.hoje)+' (hoje)';
const chave=()=>self.state.mq_k||self.__mqk0||(self.__mqk0=manChave());   /* duplo toque no mesmo instante lê a mesma chave: um lançamento só (AC-PCM-16) */
const salvar=(outro)=>{ if(!a) return TOAST(self,'Escolha a máquina.'); const st=self.state;
  const d={aid:a.id,tq,vol:st.mq_vol,leit:st.mq_leit,op,evid:st.mq_foto?'foto do tíquete (simulada)':'',cheio:!!st.mq_cheio,data:mv.hoje,os:cur.os||''};
  const r=mbManCmd(self,'abastecer',{d},null,chave());
  if(!r.erro&&!r.nada){ const base={mq_vol:'',mq_leit:'',mq_foto:false,mq_cheio:false,mq_k:manChave(),mq_rec:{t:r.msg,fila:!!r.fila}}; self.setState(outro?Object.assign(base,{mq_aid:'-',mq_tq:undefined,mq_opk:undefined}):base); } };
v.mq_reg=()=>salvar(false); v.mq_outro=()=>salvar(true);
v.mq_ltv=s.mq_lt||''; v.mq_setlt=(e)=>self.setState({mq_lt:e.target.value}); const dl=s.mq_ltd||mv.hoje;
v.mq_ltdias=[['Hoje',mv.hoje],['Ontem',manAdd(mv.hoje,-1)]].map(([t,d])=>({t:t+' · '+manBr(d),on:String(d===dl),st:mbPill(d===dl),fn:()=>self.setState({mq_ltd:d}),tt:'Data da leitura: '+manBr(d)}));
v.mq_regLt=()=>{ if(!a) return TOAST(self,'Escolha a máquina.'); const st=self.state; const r=mbManCmd(self,'leitura',{aid:a.id,val:st.mq_lt,data:dl},null,chave());
  if(!r.erro&&!r.nada){ self.setState({mq_lt:'',mq_k:manChave(),mq_rec:{t:r.msg,fila:!!r.fila}}); } };
v.mq_rec=!!s.mq_rec; v.mq_rect=s.mq_rec?s.mq_rec.t:''; v.mq_recst=s.mq_rec&&s.mq_rec.fila?'background: '+MBTX.yels+'; color: '+MBTX.yel+';':'background: '+MBTX.accs+'; color: '+MBTX.acc+';';
const F=a?manAppFila(c).filter(x=>manAppAid(c.man,x)===a.id):[]; const CF=a?manAppConfAbertos(c.man,undefined,a.id):[];
const hist=F.map(x=>({t:x.desc,s:'registrado às '+x.at+' · '+x.por,c:'No aparelho · aguardando sinal',st:mbChs('yellow'),dot:mbDot('yellow')}))
  .concat(CF.map(x=>({t:x.desc,s:x.mot+' · por '+x.por+' às '+x.at,c:'Conflito a resolver · Otávio',st:mbChs('red'),dot:mbDot('red')})))
  .concat(a?(c.man.abast||[]).filter(b=>b.aid===a.id).slice(-2).reverse().map(b=>({t:b.id+' · '+(b.tipo?'Estorno de '+b.ref:manN(b.vol)+' L'),s:manBr(b.data)+' '+(b.hora||'')+(b.leit!==null&&b.leit!==undefined?' · '+manQ(b.leit,b.un):'')+' · '+b.op,
     c:b.qual,st:mbChs(b.qual==='Confirmada'?'green':(b.qual==='Estornado'||b.qual==='Estorno'?'gray':'yellow')),dot:mbDot(b.qual==='Confirmada'?'green':(b.qual==='Estornado'||b.qual==='Estorno'?'gray':'yellow'))})):[]);
v.mq_hist=hist.slice(0,4); v.mq_hasHist=hist.length>0;'''
    emit('MB-09','Máquina','',None,
         'Registrar abastecimento',corpo,H_=1500,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
         dica='Condição, leitura e abastecimento; funciona sem sinal. A máquina vem herdada do seu turno: toque noutra ou busque pelo nome. '
              'Abastecimento: tanque, volume e leitura; a foto do tíquete é a evidência. Leitura avulsa leva a data em que foi lida.',
         prim=[('mq_pab','b','Registrar abastecimento','mq_reg'),('mq_plt','b','Registrar leitura','mq_regLt'),('mq_pnone','a','Voltar à fila','MB-01.dc.html')])

    # ---- MB-09det · Ordem de manutenção: o painel da OM em 390 px, com as mesmas funções (PCM S4) ----
    rowst=f'display: flex; flex-direction: column; gap: 6px; padding: 10px 0; border-top: 1px solid {LINE};'
    tk=(f'<div style="{rowst}"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
        f'<span style="font-size: 12px; font-weight: 800; color: {MUTED}; width: 18px;">{H("t.n")}</span><span style="font-size: 13.5px; font-weight: 600; flex: 1 1 180px; min-width: 0;">{H("t.t")}</span>'
        f'<span style="font-size: 11px; font-weight: 700; color: {MUTED}; border: 1px solid {LINE}; border-radius: 999px; padding: 0 7px;">{H("t.tipo")}</span>'
        + IF('t.nova',f'<span style="{BTN_ST(False,True)} padding: 2px 8px; font-size: 11px; color: {YEL}; background: {YELS}; border: 0;">Tarefa nova</span>') + '</div>'
        + IF('t.hasVal',f'<label style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: {MUTED};">Valor<input aria-label="{H("t.vlab")}" inputMode="decimal" value="{H("t.val")}" onChange="{H("t.setval")}" style="{INP} width: 120px; text-align: right;">{H("t.un")}</label>')
        + IF('t.showOpts',f'<span role="group" aria-label="{H("t.t")}" style="display: flex; gap: 6px; flex-wrap: wrap;"><sc-for list="{H("t.opts")}" as="b" hint-placeholder-count="3">'
             f'<button type="button" aria-pressed="{H("b.on")}" aria-label="{H("b.lab")}" title="{H("b.lab")}" disabled="{H("b.dis")}" onClick="{H("b.go")}" style="{H("b.st")}">{H("b.t")}</button></sc-for></span>')
        + IF('t.hasMot',f'<input aria-label="{H("t.motlab")}" placeholder="Motivo (obrigatório)" value="{H("t.mot")}" onChange="{H("t.setmot")}" style="{INP}">'
             + f'<div><button type="button" onClick="{H("t.motgo")}" title="Gravar a resposta com o motivo" style="{_BST}">{H("t.motgot")}</button></div>')
        + IF('t.ro',f'<span style="{H("t.rst")}"><span style="{H("t.rdot")}"></span>{H("t.r")}</span>')
        + IF('t.hasPor',f'<span style="font-size: 12px; color: {MUTED};">{H("t.por")}</span>')
        + IF('t.hasMotTx',f'<span style="font-size: 12.5px; color: {MUTED};">Motivo: {H("t.motTx")}</span>')
        + IF('t.hasValTx',f'<span style="font-size: 12.5px;">Medido: {H("t.valTx")}</span>')
        + IF('t.hasTents',f'<div style="display: flex; flex-direction: column; gap: 4px;"><sc-for list="{H("t.tents")}" as="x" hint-placeholder-count="1"><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span></sc-for></div>')
        + IF('t.treg',f'<div><button type="button" onClick="{H("t.tgo")}" title="Anexar a foto do teste (simulada) e registrar a tentativa" style="{_NXST}">{icon("doc",14)}{H("t.tgot")}</button></div>')
        + IF('t.hasWhy',f'<span style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("t.why")}</span>') + '</div>')
    corpo=(
      sigbar()
      + f'<div style="{CARD_ST}"><div role="status" style="{H("dp_cst")}">{H("dp_cond")}</div>'
        f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 13px; color: {MUTED};"><span>{H("dp_leit")}</span>'
        f'<a href="{H("dp_ath")}" title="Abrir a máquina desta ordem (condição, leitura e abastecimento)" style="color: {ACC}; font-weight: 700; text-decoration: none;">{H("dp_att")}</a></div>'
        f'<div role="list" aria-label="Fases da ordem" style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-for list="{H("dp_fases")}" as="f" hint-placeholder-count="5">'
        f'<span role="listitem" aria-current="{H("f.cur")}" style="{H("f.st")}">{H("f.t")}</span></sc-for></div>'
        f'<div style="font-size: 12.5px; color: {MUTED};">{H("dp_info")}</div></div>'
      + IF('dp_hasFila',f'<div role="status" style="{recst} background: {YELS}; color: {YEL};">{H("dp_filat")}</div>')
      + IF('dp_hasConf',f'<div role="alert" style="{recst} background: {REDS}; color: {RED};"><sc-for list="{H("dp_confs")}" as="x" hint-placeholder-count="1"><div>{H("x.t")}<div style="font-weight: 600;">{H("x.s")}</div></div></sc-for></div>')
      + IF('dp_hasWhy',f'<div style="{recst} background: {GRAYS}; color: {INK}; font-weight: 600;">{H("dp_why")}</div>')
      + IF('dp_rec',f'<div role="status" style="{recst} {H("dp_recst")}">✓ {H("dp_rect")}</div>')
      + IF('dp_aviso',f'<div role="alert" style="{recst} background: {YELS}; color: {YEL};">{H("dp_avisot")}'
           + btns(fnb('Concluir com esta leitura','dp_forcar','check','Concluir mesmo com a leitura acima do possível'),fnb('Corrigir leitura','dp_corrigir','clock','Voltar e corrigir a leitura')) + '</div>')
      + h2('Tarefas',H('dp_tkn')) + f'<div style="{CARD_ST} padding-top: 4px;"><sc-for list="{H("dp_tks")}" as="t" hint-placeholder-count="4">{tk}</sc-for>'
      + IF('dp_incEd',f'<div style="{rowst}">{lab("Incluir tarefa")}' + pills('dp_inct','Tipo da tarefa',4)
           + f'<input aria-label="Nova tarefa" placeholder="Nova tarefa" value="{H("dp_incx")}" onChange="{H("dp_setincx")}" style="{INP}">'
           + f'<div><button type="button" onClick="{H("dp_inc")}" title="Incluir a tarefa nesta ordem (corretiva ou pendência)" style="{_BST}">Incluir tarefa</button></div></div>')
      + IF('dp_incWhy',note(H('dp_incWhy'))) + '</div>'
      + IF('dp_temPc',h2('Peças','Aplicado: vazio = o planejado.') + f'<div style="{CARD_ST} padding-top: 4px;"><sc-for list="{H("dp_pcs")}" as="p" hint-placeholder-count="2"><div style="{rowst}">'
           f'<div style="display: flex; gap: 8px; flex-wrap: wrap; font-size: 13px;"><b style="font-weight: 600; flex: 1 1 160px;">{H("p.nome")}</b><span>planejado {H("p.q")}</span></div>'
           f'<span style="{H("p.st")}"><span style="{H("p.dot")}"></span>{H("p.s")}</span>'
           + IF('p.ed',f'<label style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: {MUTED};">Aplicado<input aria-label="{H("p.alab")}" inputMode="decimal" placeholder="{H("p.aph")}" value="{H("p.av")}" onChange="{H("p.aset")}" style="{INP} width: 110px; text-align: right;">{H("p.un")}</label>')
           + IF('p.ro',f'<span style="font-size: 12.5px;">Aplicado: {H("p.apl")}</span>') + '</div></sc-for></div>')
      + IF('dp_temRet',h2('Peças retiradas','Nunca voltam ao estoque livre: destino e responsável.') + f'<div style="{CARD_ST} padding-top: 4px;"><sc-for list="{H("dp_rets")}" as="r" hint-placeholder-count="2"><div style="{rowst}">'
           f'<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; font-size: 13px;"><b style="font-weight: 600; flex: 1 1 160px;">{H("r.t")}</b><span style="{H("r.st")}"><span style="{H("r.dot")}"></span>{H("r.d")}</span><span style="color: {MUTED};">{H("r.rs")}</span></div>'
           + IF('r.ed',pills('r.dests','Destino',3,a='d') + f'<input aria-label="{H("r.rlab")}" placeholder="Responsável pelo destino" value="{H("r.rv")}" onChange="{H("r.setr")}" style="{INP}">'
                + f'<div><button type="button" onClick="{H("r.go")}" title="Registrar o destino e o responsável pela peça retirada" style="{_BST}">Registrar destino</button></div>') + '</div></sc-for></div>')
      + IF('dp_conEd',h2('Conclusão','Leitura do contador e horas de oficina.') + f'<div style="{CARD_ST}">'
           + IF('dp_hasCont',ffield(H('dp_unl'),'dp-leit','dp_leitv','dp_setleit','',big=True,hint=H('dp_ult'),ph='leitura no painel'))
           + f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Horas de oficina · h")}<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">'
             f'<button type="button" aria-pressed="{H("dp_prevOn")}" onClick="{H("dp_prev")}" title="Usar o tempo previsto da ordem como horas de oficina" style="{H("dp_prevSt")}">{H("dp_prevt")}</button>'
             f'<input id="dp-horas" aria-label="Horas de oficina" inputMode="decimal" value="{H("dp_horas")}" onChange="{H("dp_sethoras")}" style="{INP} width: 110px; text-align: right;"></div></div></div>')
      + IF('dp_exRo',card('Serviço concluído',[H('dp_exTxt')],state='green'))
      + IF('dp_apt',h2('Aptidão',H('dp_aptSub')) + f'<div style="{CARD_ST}">'
           + IF('dp_aptMot',note(H('dp_aptMotT')))
           + IF('dp_manEd',f'<input aria-label="Motivo para manter" placeholder="Motivo para manter (obrigatório)" value="{H("dp_mant")}" onChange="{H("dp_setmant")}" style="{INP}">'
                + f'<div><button type="button" onClick="{H("dp_man")}" title="Manter a condição do ativo, com o motivo (desfaz o vínculo com esta ordem)" style="{_BST}">{H("dp_manl")}</button></div>') + '</div>'))
    js='''const mv=mbManView(c); const us=mbUsuario(c); mbVerComo(self,v,c);
let id=(String(location.hash||'').match(/OM-\\d+/)||[])[0]; if(!id||!mv.oms[id]) id=mbOmGet(); if(!id||!mv.oms[id]){ const f=mbOmsDe(mv,us); id=f[0]?f[0].id:'OM-0233'; }
const o=mv.oms[id]; const a=mv.ativos[o.aid]; const exe=o.etapa==='Em execução'; const pE=manPode(mv,us,'executar',{o}); const pT=manPode(mv,us,'teste',{o});
const ff=s.dp||{}; const setF=(k,val)=>self.setState({dp:Object.assign({},self.state.dp||{},{[k]:val})});
const fim=(r,limpa)=>{ const f2=Object.assign({},self.state.dp||{}); (limpa||[]).forEach(k=>{ delete f2[k]; }); self.setState({dp:f2,dp_aviso:null,dp_rec:r&&r.msg?{t:r.msg,fila:!!r.fila}:null}); };
const dk=()=>self.state.dp_k||self.__dpk0||(self.__dpk0=manChave());   /* chave do aparelho: o toque repetido no mesmo instante é um efeito só */
const run=(cmd,args,limpa)=>mbManCmd(self,cmd,Object.assign({om:o.id},args||{}),(r)=>{ self.setState({dp_k:manChave()}); fim(r,limpa); },dk());
v.hdr_ttl=o.id+' · '+(a?a.nome:''); v.hdr_sub=(String(o.serv||'').indexOf(o.tipo)===0?o.serv:o.tipo+' · '+o.serv)+(o.executante?' · executante '+o.executante:'');
DCH(v,'hdr',o.etapa+(a&&a.cond==='Bloqueado'&&manAberta(o)?' · ativo bloqueado':''),o.etapa==='Encerradas'?'gray':(a&&a.cond==='Bloqueado'?'red':(MB_ETAPA_COR[o.etapa]==='blue'?'green':(MB_ETAPA_COR[o.etapa]||'gray'))));
const cd=mbCond(a); v.dp_cond=cd.t; v.dp_cst=mbCondSt(cd.c); v.dp_leit=a&&a.un?'Leitura '+manLeitTxt(a):'Sem contador'; v.dp_ath='MB-09.dc.html#ativo='+o.aid; v.dp_att='Abrir '+(a?a.nome:'máquina')+' ›';
const cur=MAN_FASES.indexOf(o.etapa); v.dp_fases=MAN_FASES.map((x,i)=>({t:x,cur:i===cur?'step':'false',st:'font-size: 11.5px; font-weight: '+(i===cur?800:600)+'; padding: 3px 8px; border-radius: 999px; white-space: nowrap; '+(i===cur?'background: '+MBTX.accs+'; color: '+MBTX.acc+';':'color: '+MBTX.muted+';')}));
v.dp_info='Janela '+(o.jan||manBr(o.janIso))+' · criticidade '+(o.crit||'—')+' · retorno '+(o.ret||'—');
const nf=manAppFila(c).filter(x=>x.om===o.id); v.dp_hasFila=nf.length>0; v.dp_filat=nf.length+(nf.length>1?' registros desta ordem no aparelho':' registro desta ordem no aparelho')+' · aguardando sinal (vai uma vez só)';
const cf=manAppConfAbertos(c.man,o.id); v.dp_hasConf=cf.length>0; v.dp_confs=cf.map(x=>({t:'Conflito a resolver · Otávio',s:x.desc+' · por '+x.por+' às '+x.at+' · '+x.mot}));
v.dp_why=o.etapa==='A liberar'?'A liberar: o Otávio (responsável de manutenção) libera a ordem.':((o.etapa==='Liberadas'||exe)&&pE?pE+' · você vê a ordem, sem alterar.':''); v.dp_hasWhy=!!v.dp_why;
v.dp_rec=!!s.dp_rec; v.dp_rect=s.dp_rec?s.dp_rec.t:''; v.dp_recst=s.dp_rec&&s.dp_rec.fila?'background: '+MBTX.yels+'; color: '+MBTX.yel+';':'background: '+MBTX.accs+'; color: '+MBTX.acc+';';
/* tarefas pelo tipo: OK grava num toque; fora de OK pede o motivo; Teste com tentativa e foto (D-36); nada vem marcado */
const nr=o.chk.filter(t=>t.tipo==='Teste'?((t.tent||[]).slice(-1)[0]||{}).r==='Aprovado':!!t.r).length; v.dp_tkn=nr+' de '+o.chk.length+' respondidas';
const pst=(on,ok,dis)=>'font-family: inherit; font-size: 13px; font-weight: 700; padding: 8px 12px; border-radius: 10px; cursor: '+(dis?'not-allowed':'pointer')+'; white-space: nowrap;'+(dis?' opacity: .55;':'')
  +(on?(ok?' border: 1px solid '+MBTX.acc+'; background: '+MBTX.acc+'; color: #fff;':' border: 1px solid '+MBTX.yel+'; background: '+MBTX.yels+'; color: '+MBTX.yel+';'):' border: 1px solid '+MBTX.line+'; background: '+MBTX.surf+'; color: '+MBTX.ink+';');
v.dp_tks=o.chk.map((t,i)=>{ const tp=t.tipo||'Serviço'; const isT=tp==='Teste'; const isM=tp==='Medição'; const why=isT?pT:pE; const ed=exe&&!why;
  const R=MAN_RESP[tp]||MAN_RESP['Serviço']; const ul=(t.tent||[]).slice(-1)[0]; const rr=isT?(ul?ul.r:''):(t.r||''); const pend=ff['tr'+i]||'';
  const mval=ff['mv'+i]!==undefined?ff['mv'+i]:(t.val===undefined||t.val===''?'':String(t.val).replace('.',','));
  const opts=R.map(x=>({t:x,lab:x+' · '+t.t,dis:!ed,on:String(isT||pend?pend===x:t.r===x),st:pst(isT||pend?pend===x:t.r===x,MAN_OK.indexOf(x)>=0,!ed),
    go:()=>{ if(!ed) return; if(isT){ setF('tr'+i,pend===x?'':x); return; }
      if(MAN_OK.indexOf(x)>=0){ const a2=isM?{i,r:x,val:mval}:{i,r:x}; run('resp',a2,['tr'+i]); return; } setF('tr'+i,x); }}));
  const cfr=ff['tr'+i]&&!isT&&MAN_OK.indexOf(ff['tr'+i])<0;
  const so=exe&&(ed||(isT&&!pE));   /* Teste sem a habilidade: botões desabilitados com o motivo */
  return {n:String(i+1),t:t.t,tipo:tp,nova:!!(t.nova&&!t.r),showOpts:so,opts,ro:!so,
    r:rr||'Sem resposta',rst:mbChs(MAN_OK.indexOf(rr)>=0?'green':(rr?(rr==='Reprovado'?'red':'yellow'):'gray')),rdot:mbDot(MAN_OK.indexOf(rr)>=0?'green':(rr?(rr==='Reprovado'?'red':'yellow'):'gray')),
    por:t.por&&!isT?('por '+t.por+(t.em?' às '+t.em:'')):'',hasPor:!!t.por&&!isT,
    hasVal:ed&&isM,val:mval,un:t.un||'',vlab:'Valor · '+t.t+(t.un?' ('+t.un+')':''),setval:(e)=>setF('mv'+i,e.target.value),hasValTx:!ed&&isM&&t.val!==''&&t.val!==undefined,valTx:t.val!==''&&t.val!==undefined?manN(t.val,2)+' '+(t.un||''):'',
    hasMot:ed&&!!cfr,mot:ff['mt'+i]!==undefined?ff['mt'+i]:(t.mot||''),motlab:'Motivo · '+t.t,setmot:(e)=>setF('mt'+i,e.target.value),motgot:'Registrar '+(ff['tr'+i]||'')+' com o motivo',
    motgo:()=>{ const f2=self.state.dp||{}; const mt=String(f2['mt'+i]||'').trim(); if(!mt) return TOAST(self,'Informe o motivo de “'+t.t+'”.'); run('resp',isM?{i,r:f2['tr'+i],mot:mt,val:mval}:{i,r:f2['tr'+i],mot:mt},['tr'+i,'mt'+i]); },
    hasMotTx:!!t.mot&&!cfr,motTx:t.mot||'',
    tents:(t.tent||[]).map((x,j)=>({t:(j+1)+'ª tentativa · '+x.r+' · '+x.evid+' · '+x.por+' · '+x.em,st:mbChs(x.r==='Aprovado'?'green':'red').replace('white-space: nowrap;','white-space: normal; line-height: 1.35; align-items: flex-start;'),dot:mbDot(x.r==='Aprovado'?'green':'red')})),hasTents:isT&&(t.tent||[]).length>0,
    treg:isT&&ed&&!!pend,tgot:'Anexar foto e registrar '+pend,tgo:()=>run('tentativa',{i,r:pend,evid:'foto (simulada)'},['tr'+i]),
    hasWhy:exe&&isT&&!pE&&!!pT,why:'Teste: '+pT}; });
/* incluir tarefa (Corretiva e Pendência, pela matriz) */
const pI=manPode(mv,us,'incluir',{o}); const incP=['Corretiva','Pendência'].indexOf(o.tipo)>=0&&MAN_ABERTAS.indexOf(o.etapa)>=0; v.dp_incEd=incP&&!pI; v.dp_incWhy=incP&&pI&&exe?'Incluir tarefa: '+pI:'';
const it=ff.itipo||'Serviço'; v.dp_inct=MAN_TIPOS.map(x=>({t:x,on:String(x===it),st:mbPill(x===it),fn:()=>setF('itipo',x),tt:'Tipo da tarefa: '+x}));
v.dp_incx=ff.itxt||''; v.dp_setincx=(e)=>setF('itxt',e.target.value); v.dp_inc=()=>{ const f2=self.state.dp||{}; run('incluir',{tipo:f2.itipo||'Serviço',txt:f2.itxt},['itxt']); };
/* peças (aplicado na conclusão) e retiradas (destino e responsável) */
v.dp_pcs=(o.pecas||[]).map((p,i)=>{ const st=p.apl&&o.exec?['Aplicado '+manN(p.apl,1)+' '+p.un,'green']:(p.res?['Reservado '+manN(p.res,1)+' '+p.un,'green']:['Sem reserva','gray']);
  return {nome:p.nome,q:manN(p.qtd,1)+' '+p.un,s:st[0],st:mbChs(st[1]),dot:mbDot(st[1]),ed:exe&&!pE,ro:!(exe&&!pE),av:ff['ap'+i]===undefined?'':ff['ap'+i],aph:'vazio = '+manN(p.qtd,1),alab:'Aplicado · '+p.nome+' ('+p.un+')',un:p.un,
    apl:o.exec?manN(p.apl,1)+' '+p.un:'—',aset:(e)=>setF('ap'+i,e.target.value)}; }); v.dp_temPc=v.dp_pcs.length>0;
const pR=(manPode(mv,us,'executar',{o})&&manPode(mv,us,'ponte'))||'';
v.dp_rets=(o.retiradas||[]).map((r,i)=>{ const ok=!!(r.dest&&r.dest!=='A definir'&&r.resp); const dv=ff['rd'+i]!==undefined?ff['rd'+i]:(r.dest==='A definir'?'':r.dest);
  return {t:r.nome+' · '+manN(r.qtd)+' '+r.un,d:r.dest||'A definir',rs:r.resp||'sem responsável',st:mbChs(ok?'gray':'red'),dot:mbDot(ok?'gray':'red'),ed:!pR&&manAberta(o)&&o.etapa!=='A liberar'&&o.etapa!=='Liberadas',
    dests:['Recondicionar','Garantia','Sucata'].map(x=>({t:x,on:String(x===dv),st:mbPill(x===dv),fn:()=>setF('rd'+i,x),tt:'Destino: '+x})),
    rv:ff['rr'+i]!==undefined?ff['rr'+i]:(r.resp||''),setr:(e)=>setF('rr'+i,e.target.value),rlab:'Responsável · '+r.nome,
    go:()=>{ const f2=self.state.dp||{}; run('retirada',{i,dest:f2['rd'+i]!==undefined?f2['rd'+i]:(r.dest==='A definir'?'':r.dest),resp:f2['rr'+i]!==undefined?f2['rr'+i]:r.resp},['rd'+i,'rr'+i]); }}; }); v.dp_temRet=v.dp_rets.length>0;
/* conclusão: leitura pela função única; horas pelo chip "Previsto" ou digitadas (sem valor implícito, D-18) */
v.dp_conEd=exe&&!pE; v.dp_hasCont=!!(a&&a.un); v.dp_unl=a&&a.un==='km'?'Leitura do odômetro · km':'Leitura do horímetro · h'; v.dp_leitv=ff.leit||''; v.dp_setleit=(e)=>setF('leit',e.target.value);
v.dp_ult=a&&a.leit?('Última: '+manLeitTxt(a)):''; v.dp_horas=ff.horas||''; v.dp_sethoras=(e)=>setF('horas',e.target.value);
const prevOn=!!ff.horas&&manNum(ff.horas)===Number(o.tempo); v.dp_prevt='Previsto ('+manN(o.tempo||0,1)+' h)'; v.dp_prevOn=String(prevOn); v.dp_prevSt=mbPill(prevOn); v.dp_prev=()=>setF('horas',String(o.tempo||0).replace('.',','));
v.dp_exRo=!!o.exec; v.dp_exTxt=o.exec?('Concluída em '+manBr(o.exec.data)+((o.exec.leit!==null&&o.exec.leit!==undefined&&a&&a.un)?' · leitura '+manQ(o.exec.leit,a.un):'')+' · '+manN(o.exec.horas,1)+' h de oficina · por '+o.exec.por):'';
const conc=(forcar)=>{ const f2=self.state.dp||{}; const ap={}; (o.pecas||[]).forEach((p,i)=>{ if(f2['ap'+i]!==undefined) ap[i]=f2['ap'+i]; });
  const r=mbManCmd(self,'concluir',{om:o.id,leit:f2.leit,horas:f2.horas,forcar:!!forcar,apl:ap},(r2)=>{ self.setState({dp_k:manChave()}); fim(r2,['leit','horas'].concat((o.pecas||[]).map((p,i)=>'ap'+i))); },dk());
  if(r.avisoLeit) self.setState({dp_aviso:{t:r.msg}}); };
v.dp_aviso=!!s.dp_aviso; v.dp_avisot=s.dp_aviso?s.dp_aviso.t:''; v.dp_forcar=()=>conc(true);
v.dp_corrigir=()=>{ self.setState({dp_aviso:null}); setTimeout(()=>{ const e=document.getElementById('dp-leit'); if(e){ e.focus(); if(e.select) e.select(); } },0); };
/* aptidão (CMD-19): Declarar apto com teste válido; Manter com motivo; quem decide: Otávio ou o responsável técnico do ativo */
const podeC=manPode(mv,us,'condicao',{aid:o.aid}); const aptM=manAptoMotivo(mv,o); const decide=o.etapa==='Em conferência'&&o.trata&&!o.aptidao;
v.dp_apt=decide; v.dp_aptSub=(a?a.nome:'Ativo')+' '+(a?a.cond.toLowerCase():'')+' · quem decide: Otávio ou '+manRtTxt(a)+' (responsável técnico)';
v.dp_aptMot=decide&&(!!podeC||!!aptM); v.dp_aptMotT=podeC?podeC+'.':(aptM||'');
v.dp_manEd=decide&&!podeC; v.dp_mant=ff.mant||''; v.dp_setmant=(e)=>setF('mant',e.target.value); v.dp_manl='Manter '+(a?a.cond.toLowerCase():'')+' · com motivo';
v.dp_man=()=>{ const f2=self.state.dp||{}; run('manter',{motivo:f2.mant},['mant']); };
v.dp_aptl=manAptoRot(mv,o); v.dp_apto=()=>run('apto',{});   /* A1: com outro motivo aberto, encerra só o desta OM e o ativo segue na condição */
/* primária: o próximo passo com verbo, pela fase; sem permissão, volta à fila (o motivo fica no corpo) */
v.dp_pIni=o.etapa==='Liberadas'&&!pE; v.dp_pCon=exe&&!pE; v.dp_pApt=decide&&!podeC&&!aptM; v.dp_pVolta=!v.dp_pIni&&!v.dp_pCon&&!v.dp_pApt;
v.dp_ini=()=>run('iniciar',{}); v.dp_con=()=>conc(false);'''
    emit('MB-09','Ordem de manutenção','',None,'Concluir serviço',corpo,H_=2000,fname='MB-09det.dc.html',back='MB-01.dc.html',js=js,dyn_status=True,cen=True,dyn_head='Ordem de manutenção',
         dica='Peças: Aplicado vazio = o planejado. Peças retiradas nunca voltam ao estoque livre: destino e responsável. Conclusão: leitura do contador e horas de oficina.',
         prim=[('dp_pIni','b','Iniciar serviço','dp_ini'),('dp_pCon','b','Concluir serviço','dp_con'),('dp_pApt','b',H('dp_aptl'),'dp_apto'),('dp_pVolta','a','Voltar à fila','MB-01.dc.html')])

    # ================= MB-10 · Cargas e entregas (nome e papéis do PRD; aba Colheita no estado · colheita P6, D-16) =================
    # Aba Colheita: um cartão por O.S. de colheita Em execução; "Apontar área" pelo mesmo cenApontar da web (origem app, chave do aparelho)
    # e "Registrar carga" (prCarga: veículo por toque, caixas ou kg estimados opcionais, talhões e %). Pesar e receber ficam na web (CARGA),
    # um lugar só: Balança, Recebedor e MB-10det saíram. Aba Motorista: igual (logística, fora do escopo).
    tabs=('<div role="tablist" aria-label="Papel" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px; align-self: flex-start;">'
          + ''.join(f'<button type="button" role="tab" aria-selected="{H("tab"+str(i)+"_on")}" onClick="{H("tab"+str(i))}" style="{H("ts"+str(i))}">{esc(t)}</button>' for i,t in enumerate(['Colheita','Motorista']))+'</div>')
    form=(f'<div style="{CARD_ST} border-color: {ACC};"><div style="font-size: 14.5px; font-weight: 700;">{H("f_tt")}</div>'
          + IF('fa',ffield('Hectares colhidos neste turno','mb_ha','f_ha','f_setha','f_eha',hint=H('f_hha'),big=True,ph='0')
               + ffield('Horas trabalhadas','mb_h','f_h','f_seth','f_eh',ph='ex.: 8'))
          + IF('fc',f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">Veículo</span>'
               f'<div role="group" aria-label="Veículo" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("f_veics")}" as="x" hint-placeholder-count="3"><button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" title="{H("x.tt")}" style="{H("x.st")}">{H("x.t")}</button></sc-for></div></div>'
               + ffield('Caixas na carga (estimativa)','mb_cx','f_cx','f_setcx','',hint='Opcional: ajuda a balança; não soma na produção.',ph='ex.: 590')
               + ffield('Ou kg estimados','mb_kg','f_kg','f_setkg','',ph='opcional')
               + f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">Fruta de mais de um talhão?</span>'
               f'<div role="group" aria-label="Segundo talhão" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("f_os2")}" as="x" hint-placeholder-count="1"><button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" title="{H("x.tt")}" style="{H("x.st")}">{H("x.t")}</button></sc-for></div></div>'
               + IF('f_mix',ffield('Participação do talhão desta O.S.','mb_pct','f_pct','f_setpct','',hint='O outro talhão fica com o resto (soma 100 %).',ph='ex.: 60')))
          + IF('fd',f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">Carga a descartar</span>'
               f'<div role="group" aria-label="Carga a descartar" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("f_cgs")}" as="x" hint-placeholder-count="1"><button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" title="{H("x.tt")}" style="{H("x.st")}">{H("x.t")}</button></sc-for></div></div>'
               + ffield('Motivo do descarte','mb_mot','f_mot','f_setmot','',hint='Só carga registrada por engano (em dobro ou que não saiu). Nada foi pesado; o registro e o motivo ficam.',area=True,ph='ex.: registrada duas vezes'))
          + IF('f_car',f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 700; color: {RED};">{H("f_cart")}</span>'
               f'<div role="group" aria-label="Colheita na carência" style="display: flex; flex-wrap: wrap; gap: 6px;"><button type="button" aria-pressed="{H("f_conf_on")}" onClick="{H("f_conf_go")}" style="{H("f_conf_st")}">Colheita já feita</button></div></div>')
          + IF('f_err',f'<div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("f_errt")}</div>')
          + btns(fnb('Cancelar','f_cancel','',"Fechar o formulário sem gravar"))+'</div>')
    colheita=(
      sigbar()
      + IF('f_on',form)
      + h2('Colheita em execução','Aponte a área do turno e registre cada carga que sai do talhão; a balança pesa e recebe.')
      + IF('c_vazio',card('Nenhuma O.S. de colheita em execução',[note('Quando o escritório liberar e a equipe iniciar a colheita, ela aparece aqui.')]))
      + f'<sc-for list="{H("ords")}" as="o" hint-placeholder-count="1"><div style="{CARD_ST}">'
        f'<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;"><b>{H("o.id")}</b> · {H("o.tal")}</div></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("o.feito")}</div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("o.cargas")}</div>'
        f'<sc-if value="{H("o.car")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 700; color: {RED}; line-height: 1.4;">{H("o.car_t")}</div></sc-if>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
        f'<sc-if value="{H("o.bA")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("o.ga")}" title="{H("o.ttA")}" style="{_BST}">{icon("check",14)}{H("o.tA")}</button></sc-if>'
        f'<sc-if value="{H("o.bC")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("o.gc")}" title="{H("o.ttC")}" style="{_BST}">{icon("truck",14)}{H("o.tC")}</button></sc-if>'
        f'<sc-if value="{H("o.bD")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("o.gd")}" title="{H("o.ttD")}" style="{_BST}">{H("o.tD")}</button></sc-if></div></div></sc-for>'
      )
    motorista=(
      card(f'Minha viagem · {VIAGEM["veic"]}',[
          kv('Pedido',f'{VIAGEM["pedido"]} · {VIAGEM["produto"]}'),
          kv('Rota',VIAGEM['rota']),
          kv('Janela',f'{VIAGEM["janela"]} (original, congelada para pontualidade)'),
          kv('Previsão',H('prev')),
          kv('Posição',f'saiu da vez após a tolerância de 30 min · entra em {VIAGEM["pos"]} na fila'),
          chips(chip('Atrasado · janela 08:00','red'))],state='red'))
    corpo=(tabs + IF('r0',colheita,d=True) + IF('r1',motorista))
    js=f'''const r=s.tab10||0; v.r0=r===0; v.r1=r===1;
[0,1].forEach(i=>{{ v['tab'+i]=()=>self.setState({{tab10:i,m10:null,m10e:''}}); v['tab'+i+'_on']=String(r===i); v['ts'+i]='font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 14px; border-radius: 999px; border: 0; cursor: pointer; white-space: nowrap; '+(r===i?'background: {SURF}; color: {INK}; box-shadow: 0 1px 2px rgba(21,32,26,.12);':'background: transparent; color: {MUTED};'); }});
v.prev=s.np?'10:20 (informada às 09:55)':'{VIAGEM["prev"]}';
v.prever=()=>{{ self.setState({{np:true,g2toast:'Nova previsão 10:20 enviada à expedição · a janela original 08:00 segue congelada · você entra na fila ao chegar à portaria (simulado · nenhuma mensagem real enviada).'}}); }};
const ords=Object.values(c.ordens).filter(o=>prEhColheita(o)&&o.etapa==='Em execução').sort((a,b)=>a.id.localeCompare(b.id));
const F=s.m10||null; const f=s.f10||{{}}; const hoje=cenDdMm(CEN_DIA_OP);
const abre=(o,k)=>{{ const cc=cenGet(); const n=k==='area'?((cc.app.nap||0)+1):((cc.app.ncg||0)+1); self.setState({{m10:{{os:o.id,k,chave:(k==='area'?'APC-':'APP-CG-')+o.id+'-'+n,n}},f10:{{}},m10e:''}}); }};
v.c_vazio=!ords.length;
v.ords=ords.map((o,i)=>{{ const cg=prCargas(c,g=>(g.origem||[]).some(x=>x.os===o.id)&&(g.st==='A pesar'||g.dcol===CEN_DIA_OP));
  const ap=cg.filter(g=>g.st==='A pesar'); const rc=cg.filter(g=>g.st==='Recebida'); const cb=(typeof carBloqColheita==='function')?carBloqColheita(c,o,'iniciar'):null; const pend=mbProv(o);
  return {{id:o.id,tal:o.talhao,feito:'Feito '+cenNum(o.realizado,2)+' de '+cenNum(o.area,2)+' ha · saldo '+cenNum(o.saldo,2)+' ha'+(pend?' · +'+cenNum(pend,2)+' ha no aparelho':''),
    cargas:(ap.length?ap.length+(ap.length>1?' cargas a pesar: ':' carga a pesar: ')+ap.map(g=>g.id+(g.est_cx?' (~'+g.est_cx+' cx)':'')+(g.sinc===false?' · no aparelho':'')).join(', '):'Nada a pesar')+(rc.length?' · '+rc.length+' recebida(s) hoje':''),
    car:!!cb,car_t:cb?((cb.fim?'Carência até '+carAte(cb.fim):'Carência sem dados')+': não colha agora · '+cb.q):'',
    bA:!F,bC:!F&&i>0,bD:!F&&ap.some(g=>g.via==='app'),tA:'Apontar área · '+o.id,tC:'Registrar carga · '+o.id,tD:'Descartar carga a pesar',ttA:'Apontar hectares e horas do turno na '+o.id,ttC:'Registrar uma carga que saiu do '+o.talhao,ttD:'Descartar carga registrada por engano na '+o.id,
    ga:()=>abre(o,'area'),gc:()=>abre(o,'carga'),gd:()=>abre(o,'desc')}}; }});
v.f_on=!!F; v.fa=!!F&&F.k==='area'; v.fc=!!F&&F.k==='carga'; v.fd=!!F&&F.k==='desc'; v.f_tt=F?((F.k==='area'?'Apontar área · ':(F.k==='carga'?'Registrar carga · ':'Descartar carga a pesar · '))+F.os+' · '+((c.ordens[F.os]||{{}}).talhao||'')):'';
/* carência na O.S. do formulário (revisão A-14): registrar o que já foi colhido nunca é impedido, mas pede confirmação explícita */
const oFc=F&&c.ordens[F.os]; const cbF=(F&&F.k!=='desc'&&oFc&&typeof carBloqColheita==='function')?carBloqColheita(c,oFc,'iniciar'):null;
v.f_car=!!cbF; v.f_cart=cbF?((cbF.fim?'Carência até '+carAte(cbF.fim):'Carência sem dados')+': confirme que é colheita já feita (o lote fica fora da venda até a conferência).'):'';
v.f_conf_on=String(!!f.conf); v.f_conf_st=mbPill(!!f.conf); v.f_conf_go=()=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{conf:!f.conf}}),m10e:''}});
const apF=F&&F.k==='desc'?prAPesar(c,F.os).filter(g=>g.via==='app'):[];
v.f_cgs=apF.map(g=>({{t:g.id+(g.est_cx?' · ~'+g.est_cx+' cx':'')+' · '+cenDdMm(g.dcol),on:String(f.cg===g.id),st:mbPill(f.cg===g.id),tt:'Descartar a '+g.id,go:()=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{cg:g.id}}),m10e:''}})}}));
v.f_mot=f.mot||''; v.f_setmot=(e)=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{mot:e.target.value}}),m10e:''}});
const fs=(k)=>(e)=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{[k]:e.target.value}}),m10e:''}});
v.f_ha=f.ha||''; v.f_h=f.h||''; v.f_cx=f.cx||''; v.f_kg=f.kg||''; v.f_pct=f.pct||''; v.f_setha=fs('ha'); v.f_seth=fs('h'); v.f_setcx=fs('cx'); v.f_setkg=fs('kg'); v.f_setpct=fs('pct');
v.f_eha=''; v.f_eha_has=false; v.f_eh=''; v.f_eh_has=false;
const oF=F&&c.ordens[F.os]; v.f_hha=oF?('Saldo da ordem: '+cenNum(Math.max(0,oF.saldo-mbProv(oF)),2)+' ha · data '+hoje):'';
v.f_veics=['Carreta 01','Carreta 02','Caminhão 03'].map(x=>({{t:x,on:String(f.veic===x),st:mbPill(f.veic===x),tt:'Veículo da carga: '+x,go:()=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{veic:x}}),m10e:''}})}}));
v.f_os2=[{{id:'',t:'Só este talhão'}}].concat(ords.filter(o=>!F||o.id!==F.os).map(o=>({{id:o.id,t:'+ '+o.talhao+' · '+o.id}}))).map(x=>({{t:x.t,on:String((f.os2||'')===x.id),st:mbPill((f.os2||'')===x.id),tt:x.id?'Carga com fruta também do '+x.t.slice(2):'Carga de um talhão só',go:()=>self.setState({{f10:Object.assign({{}},self.state.f10||{{}},{{os2:x.id}}),m10e:''}})}}));
v.f_mix=!!f.os2; v.f_err=!!s.m10e; v.f_errt=s.m10e||'';
v.f_cancel=()=>self.setState({{m10:null,f10:{{}},m10e:''}});
v.grava=()=>{{ if(!F) return; let r;
  if(cbF&&!f.conf){{ self.setState({{m10e:'Carência: toque em "Colheita já feita" para registrar o que já foi colhido.'}}); return; }}
  if(F.k==='desc'){{ if(!f.cg){{ self.setState({{m10e:'Toque na carga a descartar.'}}); return; }} if(!String(f.mot||'').trim()){{ self.setState({{m10e:'Informe o motivo do descarte.'}}); return; }}
    r=cenMudar(null,cc=>prDescartarCarga(cc,f.cg,f.mot,cc.app.operador,'app')); }}
  else if(F.k==='area'){{ const ha=mbNum(f.ha), h=mbNum(f.h); if(!(ha>0)){{ self.setState({{m10e:'Informe os hectares colhidos (maior que 0).'}}); return; }} if(!(h>0)){{ self.setState({{m10e:'Informe as horas trabalhadas.'}}); return; }}
    r=cenMudar(null,cc=>{{ cc.app.nap=Math.max(cc.app.nap||0,F.n); const R=cenApontar(cc,{{os:F.os,d:hoje,ha,h,origem:'app',quem:cc.app.operador,chave:F.chave}});
      return {{msg:R.repetido?'Área já registrada ('+F.os+' · '+cenNum(ha,2)+' ha): nada somado de novo.':('Área apontada: '+cenNum(ha,2)+' ha em '+cenNum(h,1)+' h na '+F.os+(R.ap.sinc?'.':' · salva no aparelho, envia quando houver sinal.')+' A produção só muda com a carga pesada.')}}; }}); }}
  else {{ if(!f.veic){{ self.setState({{m10e:'Toque no veículo da carga.'}}); return; }} const mix=f.os2?[{{os:F.os,pct:mbNum(f.pct),modo:'estimada'}},{{os:f.os2,pct:100-mbNum(f.pct),modo:'estimada'}}]:null;
    if(f.os2&&!(mbNum(f.pct)>0&&mbNum(f.pct)<100)){{ self.setState({{m10e:'Informe a participação do talhão desta O.S. (entre 0 e 100 %).'}}); return; }}
    r=cenMudar(null,cc=>{{ cc.app.ncg=Math.max(cc.app.ncg||0,F.n); return prCarga(cc,{{os:F.os,mix,cx:mbNum(f.cx)||0,kg:mbNum(f.kg)||0,veic:f.veic,via:'app',quem:cc.app.operador,chave:F.chave,dcol:CEN_DIA_OP}}); }}); }}
  if(r.erro){{ self.setState({{m10e:r.erro}}); return; }} self.setState({{m10:null,f10:{{}},m10e:'',cenrev:Date.now(),g2toast:r.msg}}); }};
v.p_grava=!!F&&r===0; v.p_gt=F?(F.k==='area'?'Gravar área':(F.k==='carga'?'Gravar carga':'Descartar carga')):''; v.p_carga=!F&&r===0&&ords.length>0; v.p_ct=ords.length?'Registrar carga · '+ords[0].id:''; v.p_cgo=()=>{{ if(ords[0]) abre(ords[0],'carga'); }};
v.p_volta=!F&&r===0&&!ords.length; v.p_prev=r===1;
const ap=[].concat(...ords.map(o=>prAPesar(c,o.id)));
if(r===1) DCH(v,'hdr','atrasado · prev. '+(s.np?'10:20':'09:10'),'red'); else DCH(v,'hdr',ords.length?(ords.length+(ords.length>1?' colheitas em execução':' colheita em execução')+(ap.length?' · '+ap.length+' a pesar':'')):'nenhuma colheita em execução',ords.length?'green':'gray');'''
    emit('MB-10','Cargas e entregas','',None,
         'Registrar carga',corpo,H_=1180,back='MB-01.dc.html',primary_href='MB-10.dc.html',js=js,dyn_status=True,cen=True,
         dica='Colheita: aponte a área do turno e registre cada carga que sai do talhão; a balança pesa e recebe. Área não gera produção: a produção do talhão nasce só da carga pesada e recebida. '
              'Motorista: informe sua previsão; a chegada só conta na portaria. Aviso do motorista não é check-in; você vê só a sua viagem, sem preços ou custos internos.',
         prim=[('p_grava','b',H('p_gt'),'grava'),('p_carga','b',H('p_ct'),'p_cgo'),('p_volta','a','Voltar a Hoje no campo','MB-01.dc.html'),('p_prev','b','Informar nova previsão','prever')])


# ===================== Carência e destino no app de campo (MAPA-CARENCIA-LMR-20261003) =====================
# A colheita no campo segue o mesmo impedimento do escritório (osc_iniciar): iniciar turno de O.S. de colheita com carência em curso, ou
# sem prazo conhecido, é recusado com motivo e dono, e o cartão mostra o selo. Registrar o que já foi colhido nunca é impedido.
# Bloco só acrescentado: envolve mbIniciar/mbPasso sem mudar as demais ordens. Motor e regras: dados_carencia.py (versão leve do app).
import dados_carencia as _DCAR
MBAPP_JS += _DCAR.js_nucleo(app=True) + r'''
const mbIniciarSemCar = mbIniciar, mbPassoSemCar = mbPasso;
mbIniciar = function (c, id) { const o = c.ordens[id]; const cb = o ? carBloqColheita(c, o, 'iniciar') : null; if (cb) throw new Error(cb.t + ' ' + cb.q); return mbIniciarSemCar(c, id); };
mbPasso = function (c, o) { const p = mbPassoSemCar(c, o); if (p.k !== 'iniciar') return p; const cb = carBloqColheita(c, o, 'iniciar'); if (!cb) return p;
  return { k: 'none', t: '', chip: [cb.fim ? 'Carência até ' + carAte(cb.fim) + ' · colheita impedida' : 'Carência sem dados · colheita impedida', 'red'], cor: 'red', tt: cb.t }; };
try { window.__mb = { mbIniciar, mbDescartar, mbResta }; } catch (e) {}
'''

# ---------- App × Manutenção (PCM simplificado S4, §3.7): Ver como Marcos · Zé (c.app.usuario); Minha fila do Zé com as OMs;
# MB-09 "Máquina" (condição em texto, leitura, OM aberta, abastecimento e leitura); MB-09det = painel da OM em 390 px com as mesmas
# funções (dados_manutencao: manIniciar, manResp, manTentativa, manIncluir, manRetirada, manConcluir, manDeclararApto, manManter);
# MB-04 "Equipamento" (e "Segurança" com máquina) grava um achado de origem Relato ligado à O.S. (manAchRegistrar).
# Sem sinal: o comando leva a chave do aparelho e vai para c.app.manFila (manAppCmd); a fila vai uma vez só (manAppSinal, no mbSinal);
# OM mudada no escritório vira "Conflito a resolver · Otávio" e nunca é aplicada em silêncio.
MBAPP_JS += r'''
const MB_US = [{ k: 'Marcos', p: 'operador' }, { k: 'Zé', p: 'mecânico' }, { k: 'João', p: 'eletricista' }];   // João: OMs de eletricista (NR-10), revisão 09/10 (A8)
function mbUsuario(c){ const u = c && c.app && c.app.usuario; return MB_US.some(x => x.k === u) ? u : 'Marcos'; }
function mbPapelUs(u){ return (MB_US.find(x => x.k === u) || MB_US[0]).p; }
// Ver como (simulação, não é login): troca quem usa o app; o estado da demonstração não muda além de c.app.usuario.
function mbVerComo(self, v, c){ const u = mbUsuario(c);
  v.us_k = u; v.us_opts = MB_US.map(x => ({ v: x.k, t: x.k + ' · ' + x.p }));
  v.us_set = (e) => { const k = e && e.target ? e.target.value : ''; const it = (v.vc_us || [])[MB_US.findIndex(x => x.k === k)]; if (it) it.fn(); };
  v.vc_us = MB_US.map(x => ({ t: x.k + ' · ' + x.p, on: String(x.k === u), st: mbSeg(x.k === u, false), tt: 'Ver o app como ' + x.k + ' (' + x.p + ') · simulação, não é login',
    fn: () => { if (mbUsuario(cenGet()) === x.k) return; cenMudar(self, c2 => { c2.app.usuario = x.k; return { msg: 'Quem usa o app: ' + x.k + ' (' + x.p + ').' }; });
      self.setState({ mq_aid: '', mq_rec: null, mq_opk: undefined, dp: {}, dp_rec: null, dp_aviso: null, oc_aid: undefined }); } })); }
// O que o aparelho mostra: o estado do servidor com a fila feita sem sinal aplicada por cima (mesmas funções).
function mbManView(c){ return manAppProj(c); }
const MB_CRIT = { 'Alta': 0, 'Média': 1, 'Baixa': 2 };
function mbCritK(o){ return o.crit in MB_CRIT ? MB_CRIT[o.crit] : 3; }
// Minha fila do mecânico: OMs em que é o executante (Liberadas, Em execução) e a aptidão a decidir onde é o responsável técnico; pela janela e depois pela criticidade.
function mbOmsDe(m, u){ return Object.values(m.oms).filter(o => (o.executante === u && (o.etapa === 'Liberadas' || o.etapa === 'Em execução'))
    || (o.etapa === 'Em conferência' && o.trata && !o.aptidao && !manPode(m, u, 'condicao', { aid: o.aid }) && (o.executante === u || (m.ativos[o.aid] || {}).rt === u)))
  .sort((a, b) => String(a.janIso || '').localeCompare(String(b.janIso || '')) || (mbCritK(a) - mbCritK(b)) || a.id.localeCompare(b.id)); }
function mbOmPasso(m, o){ const a = m.ativos[o.aid];
  if (o.etapa === 'Liberadas') return { k: 'ini', t: 'Iniciar serviço', chip: ['Pronta para iniciar', 'green'] };
  if (o.etapa === 'Em execução') { const fl = manFaltaConcluir(m, o, 'x', 'x'); const te = fl.some(x => x.indexOf('teste aprovado') === 0);
    return { k: 'cont', t: 'Continuar serviço', chip: [fl.length ? (te ? 'Teste pendente' : 'Falta: ' + fl.length + (fl.length > 1 ? ' respostas' : ' resposta')) : 'Pronta para concluir', fl.length ? 'yellow' : 'green'] }; }
  if (o.etapa === 'Em conferência') return { k: 'apt', t: 'Decidir aptidão', chip: ['Decidir aptidão · ' + (a ? a.nome : ''), 'yellow'] };
  return { k: 'none', t: '', chip: [o.etapa, 'gray'] }; }
const MB_OM_KEY = 'talhao-os-mb-om';   // ordem aberta no MB-09det (conveniência do aparelho; o cenário não muda)
function mbOmGet(){ try { return localStorage.getItem(MB_OM_KEY) || ''; } catch (e) { return ''; } }
function mbOmSet(id){ try { localStorage.setItem(MB_OM_KEY, id || ''); } catch (e) {} }
// Comando da manutenção pelo app: quem age é o Ver como do app; chave do aparelho (a mesma num toque repetido = um efeito só).
function mbManCmd(self, cmd, args, depois, chave){ const u = mbUsuario(cenGet()); const q = { chave: chave || manChave(), cmd, args, por: u };
  const r = manMudar(self, (m, c) => manAppCmd(c, q)); if (!r.erro && !r.nada && depois) depois(r); return r; }
function mbOmCard(self, c, m, o){ const a = m.ativos[o.aid]; const p = mbOmPasso(m, o); const ec = MB_ETAPA_COR[o.etapa] || 'gray';
  const nr = o.chk.filter(t => t.tipo === 'Teste' ? ((t.tent || []).slice(-1)[0] || {}).r === 'Aprovado' : !!t.r).length; const nf = manAppFila(c).filter(q => q.om === o.id).length;
  return { id: o.id, tit: o.tipo + ' · ' + (a ? a.nome : ''), loc: 'Janela ' + (o.jan || manBr(o.janIso)) + ' · criticidade ' + (o.crit || '—') + (o.ret && o.ret !== '—' ? ' · retorno ' + o.ret : ''),
    e_t: o.etapa, e_st: mbChs(ec), e_dot: mbDot(ec), p_t: p.chip[0], p_st: mbChs(p.chip[1]), p_dot: mbDot(p.chip[1]),
    dot: 'width: 10px; height: 10px; border-radius: 999px; flex-shrink: 0; background: ' + (MBC[a && a.cond === 'Bloqueado' ? 'red' : p.chip[1]] || MBC.gray)[0] + ';',
    real: 'Tarefas ' + nr + ' de ' + o.chk.length + (a && a.cond !== 'Apto' ? ' · ' + a.nome + ' ' + a.cond.toLowerCase() : '') + (nf ? ' · ' + nf + ' no aparelho, aguardando sinal' : ''),
    href: 'MB-09det.dc.html#' + o.id, sel: () => mbOmSet(o.id), isIni: p.k === 'ini', isLnk: p.k === 'cont' || p.k === 'apt', nx_t: p.t,
    ini: () => { mbOmSet(o.id); mbManCmd(self, 'iniciar', { om: o.id }); }, tt: 'Abrir ' + o.id + ' · tarefas, peças e conclusão', nx_tt: p.t + ' · ' + o.id }; }
function mbCond(a){ if (!a) return { t: '—', c: 'gray' }; const ci = a.condInfo || {};
  const nm = (ci.mais || []).length;   // A1: outros motivos de bloqueio
  if (a.cond === 'Bloqueado') return { t: 'Não opere · bloqueado' + (ci.motivo ? ' · ' + ci.motivo : '') + (ci.om ? ' · ' + ci.om : '') + (nm ? ' · +' + nm + (nm > 1 ? ' motivos' : ' motivo') : ''), c: 'red' };
  if (a.cond === 'Restrito') return { t: 'Opere com restrição' + (ci.lim ? ' · ' + ci.lim : (ci.motivo ? ' · ' + ci.motivo : '')) + (ci.ate ? ' · até ' + manBr(ci.ate) : ''), c: 'yellow' };
  return { t: 'Apto para operar', c: 'green' }; }
function mbCondSt(k){ const x = MBC[k] || MBC.gray; return 'font-size: 15px; font-weight: 800; line-height: 1.35; padding: 8px 12px; border-radius: 12px; color: ' + x[0] + '; background: ' + x[1] + ';'; }
// Máquinas herdadas: as da O.S. do turno aberto; sem turno, as da O.S. do usuário alocada hoje (O.S. › Recursos); depois as das OMs do mecânico.
function mbAtvCurtos(c, m, u){ const hoje = m.hoje; const t = mbTurno(c); let os = t ? [t.os] : [];
  if (!os.length) { const mine = Object.values(c.ordens).filter(o => o.resp === u && (o.etapa === 'Liberadas' || o.etapa === 'Em execução')).map(o => o.id);
    os = [...new Set(MAN_AL.aloc.filter(x => x.dia === hoje && mine.indexOf(x.os) >= 0).map(x => x.os))]; }
  const rs = MAN_AL.aloc.filter(x => x.dia === hoje && os.indexOf(x.os) >= 0).map(x => x.r);
  const ids = Object.keys(MAN_AL.rec).filter(id => rs.indexOf(MAN_AL.rec[id]) >= 0 && m.ativos[id]);
  ids.sort((x, y) => (m.ativos[x].classe === 'Trator' ? 0 : 1) - (m.ativos[y].classe === 'Trator' ? 0 : 1));
  const oms = mbOmsDe(m, u); oms.forEach(o => { if (ids.indexOf(o.aid) < 0 && m.ativos[o.aid]) ids.push(o.aid); });
  return { ids, os: os[0] || '', de: os.length ? ('do turno da ' + os[0] + ' (alocação de hoje)') : (oms.length ? ('da ' + oms[0].id) : '') }; }
function mbPillD(on, dis){ return mbPill(on) + (dis ? ' opacity: .55; cursor: not-allowed;' : ''); }
try { window.__mbman = { mbUsuario, mbOmsDe, mbAtvCurtos, mbManView, mbCond }; } catch (e) {}
'''
