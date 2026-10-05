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
  com você não é recusado (RN-018; CONC-07): aviso no campo, o fato fica Em conferência sem baixa e Rui (almoxarife) concilia no Estoque.
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
  (545 L físicos, 65 L reservados à OS-0424, 480 L livres; reserva planejada da safra 625,2 L em conflito, pendência 145,2 L).
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
import cenario

H=lambda s: '{{'+s+'}}'
def IF(h,body): return f'<sc-if value="{H(h)}" hint-placeholder-val="{H("false")}">{body}</sc-if>'
def br(x): return str(x).replace('.',',')
def nf(n,d=0): return f'{n:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')

# ---------- dados locais (números que só o app usa; coerentes com dados.py/dados2.py) ----------
O421,O420,O419=D.OS[0],D.OS[1],D.OS[2]
APT=dict(id='APT-1187', os='OS-0421', dia=4, ha=O421['dias'][3], recibo='REC-7741', uuid='c9e2-…-4f1a')
REQ=next(r for r in D2.REQUISICOES if r['id']=='REQ-031')
R38=next(r for r in D2.REQUISICOES if r['id']=='REQ-038')
F02=next(l for l in D2.LOTES if l['lote']=='F26-02')
F02_LIVRE=F02['fisico']-F02['quarentena']-F02['reservado']                            # 480 L
PLAN_FA=625.2; PEND_FA=round(PLAN_FA-F02_LIVRE,1)                                    # reserva planejada da safra · pendência 145,2 L
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
    s=f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: 2px;">{esc(desc)}</div>' if desc else ''
    return f'<div><div style="font-family: {DISP}; font-size: 15px; font-weight: 700; letter-spacing: -.01em;">{esc(t)}</div>{s}</div>'
CARD_ST=f'background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 13px 15px; display: flex; flex-direction: column; gap: 7px; min-width: 0;'
def card(title,rows,state='gray',desc='',head_right=''):
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
            f'<div style="font-size: 12px; color: {MUTED}; line-height: 1.45; margin-top: 2px;">{esc(hint)}</div></div>')

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
function mbMinhas(c){ return Object.values(c.ordens).filter(o => o.resp === c.app.operador).sort((a, b) => mbK(a) - mbK(b) || a.id.localeCompare(b.id)); }
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
function mbDescartar(c){ const t = c.app.turno; if (!t || t.fim) throw new Error('Nenhum turno aberto.'); c.app.turno = null; return { msg: 'Turno da ' + t.os + ' descartado sem apontamento: a ordem não tem saldo.' }; }
// Próximo passo da ordem na fila (verbo + objeto) e o selo de estado que o justifica.
function mbPasso(c, o){
  if (o.etapa !== 'Liberadas' && o.etapa !== 'Em execução') return { k: 'none', t: '', chip: [o.etapa === 'A liberar' ? 'Aguarda liberação no escritório' : 'Fora da fila', 'gray'], cor: 'gray', tt: '' };
  const t = mbTurno(c);
  if (t && t.os === o.id) { const pz = mbPausado(t); return { k: 'fechar', t: 'Fechar turno', chip: [pz ? 'Turno pausado' : 'Turno aberto · desde ' + t.ini, pz ? 'yellow' : 'green'], cor: 'green', href: 'MB-03.dc.html', tt: 'Fechar o turno da ' + o.id + ' com hectares, horas e consumo' }; }
  const r = mbReq(c, o);
  if (r && r.itens.some(i => i.custodia > 0 && !i.confirmado)) return { k: 'confirmar', t: 'Confirmar recebimento', chip: ['Entregue por Rui · ' + r.id, 'yellow'], cor: 'yellow', href: 'MB-05.dc.html#' + o.id, tt: 'Conferir itens, lote e embalagem e confirmar o recebimento da ' + r.id };
  if (mbResta(o) <= 0.001) {
    if (mbProv(o) > 0) return { k: 'enviar', t: 'Ver envios', chip: ['Área feita · aguardando sinal', 'yellow'], cor: 'yellow', href: 'MB-03x-recibo.dc.html', tt: 'Ver os turnos da ' + o.id + ' que estão no aparelho' };
    const sb = mbSobra(c, o);
    if (sb.length) return { k: 'devolver', t: 'Devolver sobra', chip: ['Área feita · sobra com você', 'yellow'], cor: 'yellow', href: 'MB-05.dc.html#' + o.id, tt: 'Levar ao Rui a sobra da ' + o.id + ': ' + mbSobraTxt(sb) };
    if (mbConf(c, o.id)) return { k: 'none', t: '', chip: ['Consumo em conferência · ' + CEN_CONC_RESP, 'yellow'], cor: 'yellow', tt: '', feita: true };
    return { k: 'none', t: '', chip: ['Área feita · aguarda encerramento', 'green'], cor: 'green', tt: '', feita: true };
  }
  const f = cenIniFalta(o, r);   // regra única de início (cenario.js): a mesma da web e do comando
  if (f && f.k === 'rever') return { k: 'rever', t: '', chip: ['Insumo esgotado · Ana (agrônoma)', 'red'], cor: 'red', tt: f.t + ' ' + f.q };
  if (f && f.k === 'entregar') return { k: 'retirar', t: 'Retirar no almoxarifado', chip: [(r.itens.some(i => i.entregue > 0) ? 'Entrega parcial' : 'Reservado') + ' · ' + r.id, 'gray'], cor: 'gray', href: 'MB-05.dc.html#' + o.id, tt: 'Ver o que retirar com Rui no almoxarifado para a ' + o.id };
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
  if (k.indexOf('AP|') === 0) { const [, id, dia] = k.split('|'); const o = c.ordens[id]; const a = o && (o.ap || []).find(x => String(x.dia) === dia);
    return 'Apontamento ' + id + ' · dia ' + dia + (a ? ' · ' + cenNum(a.ha, 1) + ' ha' + (a.h ? ' em ' + cenNum(a.h, 1) + ' h' : '') + (a.conf ? ' · consumo em conferência' : '') : ''); }
  const oc = (c.ocorr || []).find(x => x.id === k); if (oc) return 'Ocorrência ' + oc.id + ' · ' + oc.os + ' · ' + oc.tipo;
  const m = (c.movs || []).find(x => x.id === k); if (m) return m.tipo === 'recebimento' ? 'Recebimento confirmado · ' + m.req + ' · ' + m.os : m.tipo + ' · ' + (m.os || '');
  return k; }
// Sinal: usa cenSinal (envia a fila uma vez só) e guarda o recibo do envio; o movimento de consumo segue o apontamento enviado.
function mbSinal(c, on){ const fila = (c.app.fila || []).slice(); const itens = fila.map(k => mbDesc(c, k)); const r = cenSinal(c, on);
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
def emit(fid,title,sub,status,primary,body,H_=900,fname=None,back='MB-01.dc.html',primary_href=None,js='',dyn_status=False,prim=None,cen=False,dyn_head=None,sem_prim=False):
    """Gera a tela. dyn_status: selo do cabeçalho vem de v.hdr_* (JS). prim: variantes do botão primário
    [(condição|None,'a'|'b'|'ac',rótulo,href|função|(href,função))] — link navega, botão executa na própria tela, 'ac' = link que também
    executa (ex.: escolher a ordem antes de abrir o detalhe). cen: tela ligada ao cenário compartilhado (cenario.js_prefixo() + JS do app).
    dyn_head: título do <title> quando título e subtítulo do cabeçalho vêm de v.hdr_ttl / v.hdr_sub."""
    pre=(cenario.js_prefixo()+JS_BASE+MBAPP_JS) if cen else JS_BASE
    head=' cenOuvir(self); const c=cenGet(); mbSig(self,v,c);' if cen else ''
    EXTRAJS[0]=pre+'const M='+json.dumps(MS,ensure_ascii=False)+';\nfunction EXTRAVALS(self,v){ const s=self.state; SAY(self,v,M);'+head+'\n'+js+'\n}'
    MS.clear()
    st=('§ST§','yellow') if dyn_status else status
    if dyn_head: title,sub='§TT§','§SB§'
    f=mobile37(fid,title,sub,st,primary,body,fname=fname,H=H_,back=back,primary_href=primary_href)
    if dyn_status or prim or dyn_head or sem_prim:
        path=os.path.join(E.P,f); s=open(path).read()
        if sem_prim: n0=len(s); s=_PRIM_RE.sub('',s,count=1); assert len(s)<n0, 'rodapé não encontrado'
        if dyn_status: s=s.replace(chip('§ST§','yellow'),dchip('hdr'))
        if dyn_head: s=s.replace('<title>§TT§</title>',f'<title>{esc(dyn_head)}</title>').replace('§TT§',H('hdr_ttl')).replace('§SB§',H('hdr_sub'))
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
      + h2('Minha fila','Siga a ordem da janela; o botão diz o próximo passo.')
      + IF('fila_vazia',card('Nada liberado para você',[note('Quando o escritório liberar uma ordem sua, ela aparece aqui com os insumos a retirar.')]))
      + qcards('fila',count=2)
      + h2('Abrir por tipo de trabalho','Escolha o trabalho para abrir o formulário do seu domínio.')
      + grid2(navcard('Minhas ordens','lista e detalhe da O.S.','MB-02','lista'),
              navcard('Apontamento','turno: início, pausa e fechamento','MB-03','check'),
              navcard('Ocorrência','tipo, texto, foto e voz','MB-04','alert'),
              navcard('Almoxarifado','retirar e confirmar','MB-05','box'),
              navcard('Vistoria','rota por pontos','MB-06','leaf'),
              '<span></span>')   # MB-07..MB-10 só simulam com dados locais (Frente F): fora do app até ligarem ao estado
      + f'<div style="display: flex; justify-content: flex-end;"><button type="button" onClick="{H("restaurar")}" title="Voltar ordens, estoque e app ao início da demonstração" '
        f'style="font-family: inherit; font-size: 12px; font-weight: 600; color: {MUTED}; background: transparent; border: 0; padding: 4px 0; cursor: pointer; text-decoration: underline;">Restaurar demonstração</button></div>')
    js='''const fila=mbFila(c); v.fila=fila.map(o=>mbCard(self,c,o)); v.fila_vazia=!fila.length;
const pend=(c.app.fila||[]).length;
DCH(v,'hdr',fila.length+(fila.length===1?' ordem':' ordens')+' · '+(pend?pend+' aguardando sinal':'envios em dia'),pend?'yellow':'green');
const pk=mbPrim(c,fila); v.pk_isA=!!pk.href; v.pk_ini=pk.k==='iniciar'; v.pk_none=pk.k==='none'; v.pk_lab=pk.lab; v.pk_href=pk.href||'MB-01.dc.html';
v.pk_sel=()=>{ if(pk.o) mbSelSet(pk.o.id); };
v.pk_go=()=>{ if(pk.o){ mbSelSet(pk.o.id); cenMudar(self,c=>mbIniciar(c,pk.o.id)); } };
// cenReset só apaga a chave: grava o cenário inicial para que os outros quadros abertos também voltem ao início (e não regravem o antigo).
v.restaurar=()=>{ cenReset(); cenSave(cenGet()); mbSelSet(''); self.setState({cenrev:Date.now(),ft:{},ft_err:{},g2toast:'Demonstração restaurada: ordens, estoque e app voltaram ao início.'}); };'''
    emit('MB-01','Hoje no campo','Marcos · operador · Santa Rita',None,'Abrir próxima tarefa',corpo,H_=1740,back='IN-01.dc.html',
         js=js,dyn_status=True,cen=True,
         prim=[('pk_isA','ac',H('pk_lab'),(H('pk_href'),'pk_sel')),('pk_ini','b',H('pk_lab'),'pk_go'),('pk_none','a','Ver minhas ordens','MB-02.dc.html')])

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
          note('Água simplificada: abre em Irrigação, sem materiais e sem requisição.')],state='blue')   # MB-08 só simula (Frente F)
      + btns(say('Ler QR','QR da OS-0421 lido · ordem aberta na versão autorizada v2.','grid','Ler o QR impresso da ordem'))
      + note('Fechar o turno não encerra a ordem. Encerrar é no escritório, com apontamentos enviados e nada em custódia.'))
    js='''const mine=mbMinhas(c).filter(o=>o.etapa!=='Encerradas'); v.minhas=mine.map(o=>mbCard(self,c,o));
const ack=!!s.ack; v.noack=!ack;
DCH(v,'ack',ack?'Ciência registrada · CI-0931 · 10:44':'Ciência pendente do operador',ack?'green':'yellow');
v.ack=()=>{ if(self.state.ack) return; self.setState({ack:true,g2toast:'Ciência registrada (recibo CI-0931) · o saldo de 70 ha segue na v3 e fica parado até o Trator T1 voltar ou o substituto ser confirmado · os 30 ha realizados seguem na v2.'}); };'''
    emit('MB-02','Minhas ordens','suas (Marcos) e da equipe · mesma ordem do escritório',('1 impedida · 1 revogada','red'),
         'Abrir ordem',corpo,H_=2320,back='MB-01.dc.html',js=js,cen=True,sem_prim=True)

    # ---- MB-02det · detalhe da ordem escolhida (cenário) ----
    PREP421=f"{CALDA['litros']} L de calda · {CALDA['vazao']} · cobre {CALDA['cobre']} · {CALDA['por_tanque']} de Fungicida A ({CALDA['dose']})"
    corpo=(
      sigbar()
      + mcont('Minhas ordens',H('d_aqui'),H('d_falta'),H('d_prox'))
      + f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Instrução liberada</div></div>'
        f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">Siga dose, janela e preparo da versão autorizada.</div>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{hchip("d_ps")}</div>'
        f'<sc-for list="{H("d_kv")}" as="k" hint-placeholder-count="4"><div style="font-size: 13px; color: {MUTED}; line-height: 1.45;"><span style="font-weight: 600; color: {INK};">{H("k.l")}:</span> {H("k.t")}</div></sc-for>'
        + IF('d_424',btns(lnk('Abrir ficha do caldeiro','OS-0424-app.dc.html','doc','Abrir o preparo carga a carga da OS-0424 (funciona sem internet)')))
        + '</div>'
      + IF('d_hasins',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {GRAY}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Insumos · {H("d_req")}</div></div>'
        f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">Use só o material autorizado; a sobra volta pela devolução.</div>'
        f'<sc-for list="{H("d_ins")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 7px 0; border-top: 1px solid {LINE};">'
        f'<div style="font-size: 13px; font-weight: 700;">{H("i.t")}</div><div style="font-size: 12.5px; color: {MUTED}; line-height: 1.4;">{H("i.s")}</div>'
        f'<div style="font-size: 12.5px; line-height: 1.4;"><span style="{H("i.st")}">{H("i.c")}</span></div></div></sc-for></div>')
      + f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {GRAY}; flex-shrink: 0;"></span>'
        f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Apontamentos</div></div>'
        f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">Confira o que já foi enviado e o que está só no aparelho.</div>'
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
v.d_falta=({{fechar:'hectares, horas e consumo do turno',confirmar:'confirmar o recebimento',retirar:'retirar os insumos com Rui',iniciar:'saldo de '+cenNum(rs,1)+' ha',
  outro:'fechar o turno da '+(tt?tt.os:'')+' · saldo de '+cenNum(rs,1)+' ha',devolver:'devolver a sobra ao Rui: '+mbSobraTxt(mbSobra(c,o)),
  enviar:cenNum(mbProv(o),1)+' ha no aparelho, aguardando sinal',rever:'decisão de Ana (agrônoma) sobre a área restante',none:p.feita?'encerramento no escritório':'liberação no escritório'}})[p.k];
const kv=[{{l:'Versão',t:o.versao}},{{l:'Janela',t:mbJan(o)}},{{l:'Local',t:o.talhao+' · '+cenNum(o.area,1)+' ha'}},{{l:'Andamento',t:mbRealTxt(o)}}];
if(o.id==='OS-0421'){{ kv.push({{l:'Equipe/conjunto',t:{json.dumps(EQ421)}}}); kv.push({{l:'Preparo por tanque',t:{json.dumps(PREP421)}}}); }}
v.d_kv=kv; v.d_424=o.id==='OS-0424';
v.d_req=r?r.id:'sem requisição'; v.d_hasins=(o.ins||[]).length>0;
v.d_ins=(o.ins||[]).map(x=>{{ const it=r&&r.itens.find(i=>i.prod===x.p);
  let cst='gray', ct=r?'Peça ao escritório antes de usar':'Reserva ao liberar a ordem';
  const kc=mbConf(c,o.id,x.p); if(kc){{cst='yellow'; ct='Em conferência · '+cenConfTxt(kc,c)+' · '+kc.resp+' concilia';}}
  else if(it){{ if(it.custodia>0&&!it.confirmado){{cst='yellow'; ct='Entregue '+cenNum(it.custodia)+' '+it.un+' · confirme a retirada';}} else if(it.custodia>0){{cst='green'; ct='Com você '+cenNum(it.custodia)+' '+it.un;}} else if(cenSaldoEntregar(it)>0){{cst='gray'; ct='Retirar '+cenNum(cenSaldoEntregar(it))+' '+it.un+' com Rui';}} else {{cst='gray'; ct='Nada em custódia';}} }}
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
         dyn_head='Detalhe da ordem',
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
      + note('Fechar o turno guarda o dia; a ordem continua aberta até o escritório encerrar.')))
    turno_off=(
      IF('has_last',f'<div style="{CARD_ST}"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {ACC}; flex-shrink: 0;"></span>'
         f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1;">Turno fechado · {H("last_t")}</div></div>'
         f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{hchip("lst")}'+IF('last_hasConf',hchip('lcf'))+'</div>'
         f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">Consumo: {H("last_cons")}</div>'
         + IF('last_hasConf',f'<div style="font-size: 13px; color: {INK}; line-height: 1.45;">{H("last_conf")}</div>')
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
  if(dup) v.last_cons='nada baixado: '+CEN_CONF_AP+' decide se é outro turno'; else if(desc) v.last_cons='nada baixado: guardado como duplicidade';
  const cf=(c.confs||[]).filter(k=>k.os===L.os&&k.dia===L.dia); const ab=cf.some(k=>k.estado==='Em conferência'||k.estado===CEN_CC_AGUARDA); v.last_hasConf=cf.length>0;
  v.last_conf=cf.map(k=>k.estado==='Em conferência'?'Em conferência · '+cenConfTxt(k,c)+' · '+k.resp+' concilia':(k.estado===CEN_CC_AGUARDA?'Aguarda a decisão da duplicidade · '+cenConfTxt(k,c)+' · '+CEN_CONF_AP:k.estado+' por '+k.por+' · '+cenConfTxt(k))).join(' | ');
  DCH(v,'lcf',ab?'Consumo em conferência':'Conferência resolvida',ab?'yellow':'green'); if(!L.cons&&cf.length&&!dup&&!desc) v.last_cons='nada baixado neste turno'; }
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
      :'Acima do que está com você ('+cenNum(tem)+' '+x.un+'): fecha em conferência com '+CEN_CONC_RESP+'.'):'';
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
    emit('MB-03','Apontamento do turno','iniciar, pausar e fechar · hectares, horas e consumo',None,
         'Fechar turno',corpo,H_=1530,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
         prim=[('t_fe','b','Fechar turno','ft_ok'),('t_zero','b','Descartar turno','descartar'),('t_ini','b',H('ti_lab'),'ti_go'),('t_none','a','Voltar à fila','MB-01.dc.html')])

    # ---- MB-03x-recibo · envios e recibos do aparelho (cenário: fila offline e recibos) ----
    corpo=(
      sigbar(envios=False)
      + mcont('Apontamento do turno','Envios e recibos',H('ct_f'),H('ct_p'))
      + IF('pend',vstep([('Capturado no aparelho','done'),('Aguardando sinal','now'),('Enviado com recibo','todo'),('Conferência no escritório','todo')],
                'Reiniciar o app preserva a fila; ao voltar o sinal cada registro entra uma vez.'))
      + IF('nopend',vstep([('Capturado no aparelho','done'),('Enviado com recibo','done'),('Conferência no escritório','now')],
                'Reenvios devolvem o mesmo recibo; a conferência decide o realizado.'))
      + IF('pend',f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">No aparelho · {H("n_t")}</div>'
           f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">Reenviar sem sinal não cria cópia.</div>'
           f'<sc-for list="{H("itens")}" as="i" hint-placeholder-count="1"><div style="font-size: 13px; padding: 5px 0; border-top: 1px solid {LINE};">{H("i.t")}</div></sc-for>'
           + IF('mais',f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 5px; border-top: 1px solid {LINE};">{H("mais_t")}</div>') + '</div>')
      + f'<div style="{CARD_ST}"><div style="font-size: 14.5px; font-weight: 700;">Recibos do servidor</div>'
        f'<div style="font-size: 12.5px; color: {MUTED}; margin-top: -3px;">Confira o que o servidor confirmou.</div>'
        f'<sc-for list="{H("recs")}" as="r" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0; border-top: 1px solid {LINE};">'
        f'<div style="font-size: 13px; font-weight: 700;">{H("r.t")}</div><sc-for list="{H("r.itens")}" as="x" hint-placeholder-count="1"><div style="font-size: 12.5px; color: {MUTED};">{H("x.t")}</div></sc-for></div></sc-for>'
        f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0; border-top: 1px solid {LINE};"><div style="font-size: 13px; font-weight: 700;">{APT["recibo"]} · 23/09 10:45 · 1 registro</div>'
        f'<div style="font-size: 12.5px; color: {MUTED};">{APT["id"]} · {APT["os"]} · dia {APT["dia"]} · {APT["ha"]} ha · identidade {APT["uuid"]} · confirmado uma vez</div></div></div>'
      + note('Conflito com outro aparelho abre <b>reconciliação</b> sem somar em dobro. Pacote revogado ou vencido vira relato para decisão, sem aprovação retroativa.'))
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
    emit('MB-03','Envios e recibos','fila do aparelho · cada registro entra uma vez',None,
         'Voltar à fila',corpo,H_=1300,fname='MB-03x-recibo.dc.html',back='MB-03.dc.html',js=js,dyn_status=True,cen=True,
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
    js='''const fila=mbFila(c); const t=mbTurno(c); const sel=mbSelGet();
const osSel=s.oc_os||(t?t.os:(fila.find(o=>o.id===sel)?sel:(fila[0]?fila[0].id:'')));
v.oc_ords=fila.map(o=>({t:o.id+' · '+o.talhao,on:o.id===osSel,st:mbPill(o.id===osSel),fn:()=>self.setState({oc_os:o.id}),tt:'Registrar na '+o.id+' · '+o.tipo}));
const TIPOS=['Equipamento','Clima','Praga ou doença','Falha de aplicação','Segurança','Outro']; const tipo=s.oc_tipo||'Equipamento';
v.oc_tipos=TIPOS.map(x=>({t:x,on:x===tipo,st:mbPill(x===tipo),fn:()=>self.setState({oc_tipo:x}),tt:'Tipo: '+x}));
v.oc_txt=s.oc_txt||''; v.oc_set=(e)=>self.setState({oc_txt:e.target.value,oc_err:''}); v.oc_err=s.oc_err||''; v.oc_err_has=!!s.oc_err;
const oo=c.ordens[osSel]; v.foto_lab=s.oc_foto?'Remover foto':'Anexar foto (simulado)'; v.oc_foto_t=s.oc_foto?'1 foto · GPS '+(oo?oo.talhao:'')+' (simulado)':'Sem foto · a foto e a voz são simuladas neste protótipo.';
v.foto=()=>{ const f=!self.state.oc_foto; self.setState({oc_foto:f,g2toast:f?'Foto anexada (simulado) · GPS do aparelho.':'Foto removida.'}); };
v.voz=()=>{ const cur=self.state.oc_txt||''; self.setState({oc_txt:(cur?cur+' ':'')+'Seção 3 da barra falhou; troquei o bico e segui.',oc_err:'',g2toast:'Voz transcrita (simulado) · revise o texto.'}); };
const done=s.oc_done; v.oc_novo=!done; v.oc_feito=!!done;
v.oc_aqui=done?done:'Nova ocorrência'; v.ct_f=done?'nada nesta ocorrência':'tipo e descrição'; v.ct_p=done?'Voltar à fila':'Registrar ocorrência';
v.registrar=()=>{ const st=self.state; const txt=String(st.oc_txt||'').trim(); if(!osSel) return TOAST(self,'Nenhuma ordem liberada na sua fila.');
  if(!txt){ self.setState({oc_err:'Descreva a ocorrência (ou use Ditar).'}); return; }
  const r=cenMudar(self,c=>cenOcorrencia(c,osSel,st.oc_tipo||'Equipamento',txt+(st.oc_foto?' · 1 foto (simulada)':'')));
  if(r&&!r.erro){ const cc=cenGet(); const oc=cc.ocorr[cc.ocorr.length-1]; self.setState({oc_done:oc.id,oc_txt:'',oc_foto:false}); } };
v.nova=()=>self.setState({oc_done:null,oc_err:''});
if(done){ const oc=(c.ocorr||[]).find(x=>x.id===done); if(oc){ v.d_t=oc.id+' · '+oc.os+' · '+oc.tipo; v.d_txt=oc.texto; DCH(v,'dsc',oc.sinc?'Registrada na O.S. · '+oc.at:'No aparelho · aguardando sinal',oc.sinc?'green':'yellow'); } }
const mine=new Set(mbMinhas(c).map(o=>o.id)); const ocs=(c.ocorr||[]).filter(x=>mine.has(x.os)&&x.id!==done);
// Teto da lista (quadro de altura fixa): as 2 mais recentes; as demais seguem na O.S. (MB-02det).
v.has_ocs=ocs.length>0; v.oc_mais=ocs.length>2; v.oc_mais_t=ocs.length>2?'+ '+(ocs.length-2)+(ocs.length-2>1?' anteriores':' anterior')+' no detalhe de cada ordem':'';
v.ocs=ocs.slice(-2).reverse().map(x=>({t:x.id+' · '+x.os+' · '+x.tipo,s:x.texto,c:x.sinc?'na O.S. · '+x.at:'aguardando sinal',st:mbChs(x.sinc?'green':'yellow'),dot:mbDot(x.sinc?'green':'yellow')}));
const ocd=done&&(c.ocorr||[]).find(x=>x.id===done); DCH(v,'hdr',done?(ocd&&!ocd.sinc?'no aparelho':'registrada'):'rascunho',done?(ocd&&!ocd.sinc?'yellow':'green'):'gray');'''
    emit('MB-04','Registrar ocorrência','tipo e texto · foto e voz simuladas · funciona sem sinal',None,
         'Registrar ocorrência',corpo,H_=1180,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
         prim=[('oc_novo','b','Registrar ocorrência','registrar'),('oc_feito','a','Voltar à fila','MB-01.dc.html')])

    # ================= MB-05 · Almoxarifado móvel (lista · papéis) =================
    tabs=('<div role="tablist" aria-label="Papel" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px; align-self: flex-start;">'
          + ''.join(f'<button type="button" role="tab" onClick="{H("role"+str(i))}" style="{H("rs"+str(i))}">{esc(t)}</button>' for i,t in enumerate(['Minhas retiradas','Almoxarife']))+'</div>')
    operador=(
      sigbar()
      + IF('has_conf',h2('Entregue por Rui · confirme','Confira itens, lote e embalagem antes de confirmar.')
           + f'<sc-for list="{H("conf")}" as="r" hint-placeholder-count="1"><div style="{CARD_ST}">'
             f'<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {YEL}; flex-shrink: 0;"></span>'
             f'<div style="font-size: 14.5px; font-weight: 700; flex-grow: 1; min-width: 0;">{H("r.t")}</div></div>'
             f'<sc-for list="{H("r.itens")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 7px 0; border-top: 1px solid {LINE};">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 14px;"><b>{H("i.p")}</b><b>{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for>'
             + IF('r.btn',btns(f'<button type="button" onClick="{H("r.fn")}" title="{H("r.tt")}" style="{_NXST}">Confirmar recebimento</button>'))
             + '</div></sc-for>')
      + IF('has_cust',h2('Com você','Use na ordem; a sobra volta pela devolução ao Rui.')
           + f'<div style="{CARD_ST}"><sc-for list="{H("cust")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0;">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px;"><b>{H("i.p")}</b><b style="color: {ACC};">{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for></div>')
      + IF('has_res',h2('Reservado · retire com Rui','Leve a O.S.; Rui entrega por lote e embalagem.')
           + f'<div style="{CARD_ST}"><sc-for list="{H("res")}" as="i" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 2px; padding: 6px 0;">'
             f'<div style="display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px;"><b>{H("i.p")}</b><b>{H("i.q")}</b></div>'
             f'<div style="font-size: 12.5px; color: {MUTED};">{H("i.l")}</div></div></sc-for></div>')
      + IF('nada',card('Nada a retirar',[note('Quando o escritório liberar uma ordem sua com insumos, a reserva aparece aqui.')]))
      + note('Confirmar o recebimento põe o material sob sua custódia; o apontamento do turno baixa o consumo.'))
    almox=(
      card(f'Receber devolução · <b>{REQ["id"]}</b> · {REQ["os"]}',[
          kv('Produto',f'{REQ["item"]} · {REQ["un"]}'),
          kv('Conta',f'entregue {REQ["entregue"]} · consumo {REQ["consumido"]} · devolvido {REQ["dev_recebida"]} · <b>custódia {REQ["custodia"]} sc com Paula</b>'),
          chips(chip(f'{REQ["custodia"]} sc a receber · OS-0417 em conferência','yellow'))],state='yellow')   # MB-05det só simula o DV-0912 (Frente F)
      + card(f'Conferir e entregar · <b>{R38["id"]}</b> · {R38["os"]} fertirrigação',[
          kv('Produto',f'{R38["item"]} · {nf(R38["solicitado"])} kg (12 kg/ha × 95 ha)'),
          chips(chip('Aguardando liberação da O.S.','yellow'),chip('Saldo apto 0 kg','red')),
          btns(say('Conferir e entregar · bloqueado',f'Bloqueado: a {R38["os"]} aguarda a liberação por Ana (agrônoma) e a {R38["item"]} não tem saldo apto (0 kg) — nada foi separado.','alert','Ver por que não pode entregar'))],state='yellow')
      + card(f'Conflito de reserva · lote {F02["lote"]} · {F02["item"]}',[
          kv('Saldo',f'{nf(F02["fisico"])} L físicos · {F02["reservado"]} L reservados (OS-0424) · <b>{nf(F02_LIVRE)} L livres</b>'),
          kv('Conflito',f'reserva planejada da safra pediu {nf(PLAN_FA,1)} L → nada reservado · pendência de {nf(PEND_FA,1)} L na SOL-2026-07'),
          chips(chip('Conflito · decide o planejamento','red')),
          btns(say('Registrar divergência','Divergência registrada com dono (planejamento) e prazo · reservas congeladas até a decisão — nada foi entregue.','alert','Registrar a divergência física do lote'))],state='red')
      + note(f'<b style="color:{INK};">{O419["id"]} · água</b> não aparece aqui: água só-água não cria fila nem documento de movimentação de produtos.'))
    corpo=tabs+IF('r0',operador)+IF('r1',almox)
    js=f'''const r0=(s.role||0)===0; v.r0=r0; v.r1=!r0;
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
reqs.forEach(r=>r.itens.forEach(i=>{{ if(i.custodia>0&&i.confirmado) cust.push({{p:i.prod,q:cenNum(i.custodia)+' '+i.un,l:lot(i)+' · '+r.os+' · consumido '+cenNum(i.consumido)+' '+i.un+(mbConf(c,r.os,i.prod)?' · consumo em conferência com '+CEN_CONC_RESP:(mbResta(c.ordens[r.os])<=0.001?' · área feita: devolva a sobra ao Rui':''))}});
  else if(!(i.custodia>0)&&cenSaldoEntregar(i)>0) res.push({{p:i.prod,q:cenNum(cenSaldoEntregar(i))+' '+i.un,l:lot(i)+' · '+mbEmb(i,cenSaldoEntregar(i))+' · '+r.id+' · '+r.os}}); }}));
v.cust=cust; v.has_cust=cust.length>0; v.res=res; v.has_res=res.length>0; v.nada=!pend.length&&!cust.length&&!res.length;
v.p_conf=r0&&pend.length>0; v.p_back=r0&&!pend.length;
v.pc_lab='Confirmar recebimento'+(pend.length>1?' · '+pend[0].id:'');
v.pc_go=()=>{{ if(pend[0]) cenMudar(self,c=>cenConfirmarRecebimento(c,pend[0].id)); }};
if(r0) DCH(v,'hdr',(foco&&c.ordens[foco]?foco+' · ':'')+(pend.length?pend.length+(pend.length>1?' entregas a confirmar':' entrega a confirmar'):(cust.length?'insumos com você':'nada a confirmar')),pend.length?'yellow':'green');
else DCH(v,'hdr','1 devolução hoje','yellow');'''
    emit('MB-05','Almoxarifado móvel','retiradas do operador e tarefas do almoxarife · por lote e embalagem',None,
         'Confirmar recebimento',corpo,H_=1220,back='MB-01.dc.html',js=js,dyn_status=True,cen=True,
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
          chips(dchip('rc'))],state='yellow',desc='Confira as sacas contra o QR antes de confirmar.')
      + note(f'Ao confirmar: custódia zera, a conta {REQ["entregue"]} = {REQ["consumido"]} + {REQ["dev_recebida"]+REQ["custodia"]} fecha e a OS-0417 segue para o fechamento da conferência · sobras íntegras entram no lote M26-05 (sobras) até inspeção.')
      + btns(say('Registrar divergência','Recebidas 8 de 10 sc: pendência aberta com dono (Paula) e prazo · 2 sc seguem em custódia — nada foi zerado.','alert','Registrar quantidade diferente da esperada'))
      + note('Material preparado não retorna como produto original disponível; só sobra íntegra volta ao estoque.'))
    js=f'''const ok=!!s.rc; v.rc=ok; v.norc=!ok;
v.ct_f=ok?'nada nesta devolução':'conferir {REQ["custodia"]} sc e zerar custódia'; v.ct_p=ok?'Voltar ao almoxarifado':'Confirmar recebimento';
v.dev=ok?'{REQ["dev_recebida"]+REQ["custodia"]} sc':'{REQ["dev_recebida"]} sc'; v.cus=ok?'0 sc':'{REQ["custodia"]} sc';
DCH(v,'hdr',ok?'custódia zerada · DV-0912':'custódia {REQ["custodia"]} sc',ok?'green':'yellow');
DCH(v,'rc',ok?'Recebido · recibo DV-0912':'A receber',ok?'green':'yellow');
v.receber=()=>{{ self.setState({{rc:true,g2toast:'Recebidas {REQ["custodia"]} sc · recibo DV-0912 · custódia de Paula zerada · conta {REQ["entregue"]} = {REQ["consumido"]} + {REQ["dev_recebida"]+REQ["custodia"]} fechada · OS-0417 segue para o fechamento da conferência.'}}); }};'''
    emit('MB-05','Receber devolução',f'{REQ["id"]} · sobras da OS-0417 · conferência física contra QR',None,
         'Confirmar recebimento de 10 sc',corpo,H_=890,fname='MB-05det.dc.html',back='MB-05.dc.html',primary_href='MB-05.dc.html',js=js,dyn_status=True,
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

    # ================= MB-07 · Contagem de frutos (detalhe/coleta) =================
    pv=D.PREVISAO
    corpo=(
      mcont('Previsão T7 · S39 (v S39-02)',FRUTO['parcela']+' · planta '+H('pl'),H('falta'),'Contar e avançar')
      + note(kv('Ciclo/parcela','safra '+D.SAFRA+' · '+FRUTO['parcela'])+' · '+kv('Método','contagem total por planta')+' · '+kv('Data','23/09'))
      + counters(('VERDES',FRUTO['verdes']),('INCHADOS',FRUTO['inchados']),('MADUROS',FRUTO['maduros']))
      + card('Classe e peso amostral',[
          kv('Amostra de peso',FRUTO['peso']+' · classe A estimada'),
          kv('Amostra de plantas',FRUTO['amostra']),
          note('Amostra e estimativa de população ficam explícitas; a previsão <b>não é publicada</b> a cada planta — só depois da revisão.')],state='gray',
          desc='Confira amostra e peso antes de concluir a parcela.')
      + btns(say('Corrigir contagem','Última contagem da planta substituída (46→44 verdes) · histórico preservado.','clock','Corrigir a última contagem'),
             say('Concluir parcela','Parcela T7-B concluída · 40 plantas · segue para revisão antes de compor a previsão.','check','Fechar a parcela para revisão'),
             say('Próxima parcela','Parcela T7-C aberta · contadores zerados · mesma amostra rastreável.','grid','Abrir a parcela seguinte'))
      + btns(lnk('Enviar para revisão','CO-01.dc.html','leaf','Abrir a previsão de colheita para revisão'))
      + note(f'A revisão compara com a previsão S39, que abastece o {pv["pedido"]} ({br(pv["classeA_t"])} t classe A · rendimento {int(pv["rendA"]*100)}%).'))
    js=f'''const pl=s.pl||18, T={FRUTO["total"]}; v.pl=pl+' de '+T; v.falta=(T-pl)+' plantas'; v.nxt='Registrar e ir à planta '+(pl+1); v.fim=pl>=T; v.nfim=pl<T;
DCH(v,'hdr','planta '+pl+' de '+T,'green');
v.reg=()=>{{ const p=self.state.pl||18; if(p>=T) return; self.setState({{pl:p+1,g2toast:'Planta '+p+' registrada · planta '+(p+1)+' aberta · contadores zerados.'}}); }};
v.fecha=()=>TOAST(self,'Parcela T7-B concluída · '+T+' plantas · segue para revisão antes de compor a previsão.');'''
    emit('MB-07','Contagem de frutos','coleta por planta e parcela · estádios do protocolo',None,
         'Registrar e ir à planta 19',corpo,H_=920,back='MB-01.dc.html',primary_href='MB-07.dc.html',js=js,dyn_status=True,
         prim=[('nfim','b',H('nxt'),'reg'),('fim','b','Concluir parcela','fecha')])

    # ================= MB-08 · Irrigação móvel (detalhe · volta em curso) =================
    exec_txt=f'{br(P["lamina_aplicada"])} mm em ≈{br(AREA_COB)} de {AREA_PIVO} ha ({br(P["cobertura_pct"])}% da volta · estimativa por percentímetro)'
    corpo=(
      mcont('Irrigação de hoje','OS-0419 · Pivô 2 · água','confirmar término da volta','Confirmar término')
      + card('Lâmina que a cultura precisa',[
          kv('Origem',f'balanço de 23/09 · déficit 11,2 mm → {br(P["lamina_aplicada"])} mm brutos em 1 passada (máx. {br(POL["lamina_max"])} mm por passada)'),
          chips(chip(f'Liberada sem aprovação · {IRR["au"]}','green'),tag(IRR['lib'])),
          note('Água sem produto: <b>sem materiais</b>, sem requisição, sem custódia e sem devolução.')],state='blue',
          desc='Confira a lâmina antes de iniciar.')
      + card('Alvo e andamento desta volta',[
          kv('Janela',f'hoje {IRR["janela"]} · 1 volta de {IRR["dur"]} · iniciada {IRR["ini"]} ({IRR["ex"]}) · término previsto {IRR["fim"]}'),
          kv('Percentímetro',f'<b>{P["percent"]}%</b> → lâmina {br(P["lamina_aplicada"])} mm (100% = {br(P["lamina_100"])} mm)'),
          kv('Andamento',f'≈{br(AREA_COB)} de {AREA_PIVO} ha ({br(P["cobertura_pct"])}% da volta) · {br(P["exec_h"])} de {IRR["dur"]} executadas'),
          kv('Medidores','bomba B2 · 166 L/s · pressão 2,8 bar · ponta parcial 20–21 h'),
          chips(prazo('irrigando','volta em curso'))],state='green',desc='Acompanhe a volta e confirme o término no fim.')
      + h2('Ações da volta','Registre pausas e avanço sem encerrar a ordem.')
      + btns(say('Pausar','Pausada · queda de pressão na bomba B2 · o tempo parado não conta como lâmina e empurra o término previsto.','clock','Pausar a volta com motivo'),
             say('Retomar','Retomada · pressão normalizada · término previsto recalculado pelo tempo parado.','check','Retomar a volta'),
             say('Registrar avanço',f'Avanço registrado: {br(P["exec_h"])} h · {exec_txt} · balanço hídrico atualizado 1× por aplicação.','drop','Registrar o avanço da volta'))
      + btns(say('Finalizar apontamento do turno','Turno do irrigante finalizado · a ordem segue Em execução — finalizar o turno nunca conclui.','doc','Guardar o turno sem concluir'),
             say('Próximo setor','Sem outro setor liberado hoje · a OS-0422 (13,5 mm em 2 passadas) libera quando a janela for definida.','pivot','Ver o próximo setor liberado'))
      + card('Próximo ciclo',[
          note(f'<b>13,5 mm (OS-0422)</b> passam do máximo de {br(POL["lamina_max"])} mm por passada: o sistema divide em <b>2 passadas de 6,75 mm</b>. Sem aprovação; libera quando a janela for definida.'),
          note('Só a fertirrigação (OS-0418) é liberada pelo agrônomo, com materiais e requisição próprios.')],state='gray',
          desc='Veja como fica a próxima lâmina.')
      + note('Área/volume insuficientes? Registra-se o tempo e a estimativa fica pendente — a lâmina não é afirmada como medida. Não existe “Encerrar e apontar”.'))
    emit('MB-08','Irrigação de hoje','OS-0419 · Pivô 2 · água · sem emissão manual',('Em execução · irrigando','green'),
         'Confirmar término da irrigação',corpo,H_=1430,back='MB-01.dc.html',primary_href='MB-08x-recibo.dc.html')

    # ---- MB-08x-recibo · término confirmado, conferência automática (estado) ----
    corpo=(
      mcont('Irrigação · OS-0419 · Pivô 2',f'Término confirmado · {IRR["fim_d"]}','próximo ciclo: OS-0422 (13,5 mm em 2 passadas)','Voltar à fila do turno')
      + vstep([(f'Lâmina pelo balanço · {IRR["au"]}','done'),(f'Liberação por prontidão · {IRR["lib"]}','done'),
               (f'Execução · {br(P["lamina_aplicada"])} mm nos {AREA_PIVO} ha (volta completa)','done'),('Conferida e encerrada','done')],
                'Fatos consistentes → conferência e encerramento automáticos, com recibos separados.')
      + card('Recibos do evento',[
          kv('Origem da lâmina',f'{IRR["au"]} · balanço de 23/09 · memória de cálculo'),
          kv('Liberação',f'{IRR["lib"]} · prontidão validada às 06:12, antes de iniciar'),
          kv('Execução',f'{IRR["ex"]} · {IRR["ini"]}–{IRR["fim_d"]} · {IRR["dur"]} · {br(P["lamina_aplicada"])} mm nos {AREA_PIVO} ha (volta completa · estimativa por percentímetro)'),
          kv('Conferência',f'{IRR["medido"]} mm medidos × {br(P["lamina_aplicada"])} mm estimados ({IRR["dif"]}, tolerância 3%)'),
          chips(chip('Conferida e encerrada automaticamente','green')),
          note(f'Balanço hídrico atualizado uma vez por aplicação · {IRR["medido"]} mm creditados nos {AREA_PIVO} ha do pivô.')],
          state='green',desc='Confira os recibos e a área realmente atendida.')
      + card('Quando não fecha sozinho',[
          note('Horímetro divergente da lâmina calculada → a ordem fica <b>Em conferência</b> com o motivo exibido; corrigir a calibração do pivô substitui a fórmula anterior.')],
          state='yellow',desc='Saiba quando a ordem para em conferência.'))
    emit('MB-08','Irrigação · recibo do término','mapa, lista, quadro e app leem o mesmo evento',('Encerradas','gray'),
         'Voltar à fila do turno',corpo,H_=1120,fname='MB-08x-recibo.dc.html',back='MB-08.dc.html',primary_href='MB-01.dc.html')

    # ================= MB-09 · Manutenção e combustível (lista) =================
    om=D.OM
    ABAST=dict(ativo='Trator 02 · MF 7719', litros='180 L', comb='Diesel S10', horim='4.812 h')
    corpo=(
      card(f'<b>{om["id"]}</b> · corretiva · {esc(om["ativo"])}',[
          kv('Causa',esc(om['causa'])),
          chips(etapa('Em execução'),chip('Ativo bloqueado','red')),
          kv('Afeta',f'{om["os_afetada"]} (plantio T4) · substituto: {esc(om["substituto"])} a partir de 24/09 06:00')],state='red')
      + card('Inspeção preventiva · Colhedora CH-01',[
          kv('Checklist','250 h · 18 itens · vence 26/09'),
          chips(etapa('Liberadas')),
          btns(say('Iniciar serviço','Inspeção iniciada · checklist de 18 itens aberto no aparelho.','check','Iniciar a inspeção preventiva'))],state='green')
      + card(f'Abastecimento · {esc(ABAST["ativo"])}',[
          kv('Registro próprio',f'{ABAST["comb"]} · bomba da fazenda · horímetro {ABAST["horim"]}'),
          btns(say('Registrar abastecimento',f'Abastecidos {ABAST["litros"]} de {ABAST["comb"]} · horímetro {ABAST["horim"]} · documento próprio de combustível — não encerra manutenção nem libera o ativo.','fuel','Registrar litros e horímetro')),
          note('Abastecer não leva o ativo à oficina nem o libera.')],state='gray')
      + btns(lnk('Reportar falha','MB-04.dc.html','alert','Abrir a captura de ocorrência'))
      + note('Combustível fica em registro próprio; a liberação técnica respeita a competência do usuário.'))
    emit('MB-09','Manutenção e combustível','serviço, inspeção e abastecimento · campos por contexto',('1 ativo bloqueado','red'),
         'Abrir serviço OM-0233',corpo,H_=900,back='MB-01.dc.html',primary_href='MB-09det.dc.html')

    # ---- MB-09det · serviço-âncora OM-0233 ----
    corpo=(
      mcont('Manutenção · minhas tarefas','OM-0233 · Trator T1',H('ct_f'),H('ct_p'))
      + IF('noc',vstep([('Diagnóstico','done'),('Peças e serviço','now'),('Teste por pessoa autorizada','todo'),('Liberação técnica do ativo','todo')],
                'O ativo segue bloqueado para operação até a liberação técnica.'))
      + IF('conc',vstep([('Diagnóstico','done'),('Peças e serviço','done'),('Teste por pessoa autorizada','now'),('Liberação técnica do ativo','todo')],
                'Serviço em conferência · o bloqueio só cai com teste e liberação técnica.'))
      + card('Serviço e horas',[
          kv('Causa',esc(om['causa'])+' · bomba hidráulica'),
          kv('Horas apontadas','6,5 h (mecânico Zé)'),
          kv('Peças','1 bomba hidráulica JD-RE-241 · 2 retentores'),
          kv('Condição técnica',chip('Bloqueado para operação','red'))],state='red',desc='Registre horas e peças do serviço.')
      + btns(say('Registrar avanço e peças','Peças aplicadas e 2,0 h somadas · requisição de peça conciliada no almoxarifado.','wrench','Somar horas e peças'),
             say('Registrar teste · sem permissão','Seu perfil não tem competência de liberação técnica — peça ao mecânico autorizado para registrar o teste; nada foi registrado.','alert','Ver por que não pode registrar o teste'),
             say('Finalizar apontamento do turno','Turno do mecânico finalizado · o serviço continua Em execução — não conclui o serviço.','clock','Guardar o turno sem concluir'))
      + note('Concluir serviço leva a manutenção para <b>Em conferência</b>, mas não libera o ativo: o bloqueio só cai com teste e liberação técnica. A OS-0420 só volta com a substituição publicada e a reliberação.'))
    js='''const c=!!s.conc; v.conc=c; v.noc=!c; v.ct_f=c?'teste e liberação técnica':'peças + teste autorizado'; v.ct_p=c?'Voltar às tarefas':'Concluir serviço';
DCH(v,'hdr',c?'Em conferência · bloqueado':'Em execução · bloqueado',c?'yellow':'red');
v.concluir=()=>{ self.setState({conc:true,g2toast:'Serviço concluído · OM-0233 em conferência · o Trator T1 segue bloqueado até teste e liberação técnica por pessoa autorizada.'}); };'''
    emit('MB-09','OM-0233 · Trator T1','corretiva · pressão hidráulica baixa · afeta OS-0420',None,
         'Concluir serviço',corpo,H_=1000,fname='MB-09det.dc.html',back='MB-09.dc.html',primary_href='MB-09.dc.html',js=js,dyn_status=True,
         prim=[('noc','b','Concluir serviço','concluir'),('conc','a','Voltar às tarefas','MB-09.dc.html')])

    # ================= MB-10 · Cargas e entregas (lista · papéis) =================
    tabs=('<div role="tablist" aria-label="Papel" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px; align-self: flex-start;">'
          + ''.join(f'<button type="button" role="tab" onClick="{H("role"+str(i))}" style="{H("rs"+str(i))}">{esc(t)}</button>' for i,t in enumerate(['Balança','Motorista','Recebedor']))+'</div>')
    balanca=(
      card(f'<b>{CG["id"]}</b> · {CG["oc"]} · Mamão Formosa',[
          kv('Veículo',f'{CG["veic"]} · chegou {CG["hora"]}')+' · '+kv('Rota',f'{CG["origem"]} → {CG["destino"]}'),
          chips(chip(f'Na balança · {CG["veic"]}','yellow'))],state='yellow')
      + card(f'{C07["id"]} · expedição · {C07["pedido"]}',[
          kv('Carga',f'{C07["cliente"]} · {C07["produto"]}'),
          chips(chip('Impedida · NF pendente','red')),
          kv('Dono',f'{C07["dono"]} · prazo {C07["prazo"]}'),
          note('Fica visível e volta à seleção após resolver; não trava os caminhões aptos.')],state='red')
      + btns(say('Registrar carga e vincular à ordem',f'Carga CG-1208 criada e vinculada à {CG["oc"]} · romaneio ROM-0792 aberto — salvar a carga não conclui a ordem de colheita.','truck','Criar carga ligada à ordem de colheita')))
    motorista=(
      card(f'Minha viagem · {VIAGEM["veic"]}',[
          kv('Pedido',f'{VIAGEM["pedido"]} · {VIAGEM["produto"]}'),
          kv('Rota',VIAGEM['rota']),
          kv('Janela',f'{VIAGEM["janela"]} (original, congelada para pontualidade)'),
          kv('Previsão',H('prev')),
          kv('Posição',f'saiu da vez após a tolerância de 30 min · entra em {VIAGEM["pos"]} na fila'),
          chips(chip('Atrasado · janela 08:00','red'))],state='red',desc='Informe sua previsão; a chegada só conta na portaria.')
      + note('Aviso do motorista não é check-in. Você vê só a sua viagem, sem preços ou custos internos.'))
    recebedor=(
      card(f'<b>{CG["id"]}</b> · chegada no {CG["destino"]}',[
          kv('Origem',f'{CG["oc"]} · {CG["origem"]} · {CG["veic"]}'),
          kv('Pesagem',f'{CG["liq"]} líquidos · romaneio {CG["rom"]}'),
          chips(dchip('rc')),
          btns(say('Registrar divergência','Avaria térmica parcial registrada · amostra AM-3315 · lote segregado até decisão — recusa não recoloca produto em estoque apto.','alert','Registrar recusa ou avaria'))],
          state='green',desc='Confira peso e condição antes de confirmar a chegada.'))
    corpo=(tabs
      + note('Cada papel vê e confirma só a sua parte. Estados logísticos são separados da etapa da O.S.')
      + IF('r0',balanca)+IF('r1',motorista)+IF('r2',recebedor))
    js=f'''const r=s.role||0, rc=!!s.rc; v.r0=r===0; v.r1=r===1; v.r2=r===2; v.r2a=r===2&&!rc; v.r2b=r===2&&rc;
[0,1,2].forEach(i=>{{ v['role'+i]=()=>self.setState({{role:i}}); v['rs'+i]='font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 14px; border-radius: 999px; border: 0; cursor: pointer; white-space: nowrap; '+(r===i?'background: {SURF}; color: {INK}; box-shadow: 0 1px 2px rgba(21,32,26,.12);':'background: transparent; color: {MUTED};'); }});
v.prev=s.np?'10:20 (informada às 09:55)':'{VIAGEM["prev"]}';
if(r===0) DCH(v,'hdr','1 na balança · 1 impedida','yellow'); else if(r===1) DCH(v,'hdr','atrasado · prev. '+(s.np?'10:20':'09:10'),'red'); else DCH(v,'hdr',rc?'chegada confirmada':'1 chegada a confirmar',rc?'green':'yellow');
DCH(v,'rc',rc?'Chegada confirmada · {CG["liq"]}':'Chegada a confirmar',rc?'green':'yellow');
v.prever=()=>{{ self.setState({{np:true,g2toast:'Nova previsão 10:20 enviada à expedição · a janela original 08:00 segue congelada · você entra na fila ao chegar à portaria (simulado · nenhuma mensagem real enviada).'}}); }};
v.chegou=()=>{{ self.setState({{rc:true,g2toast:'Chegada confirmada no {CG["destino"]} · {CG["liq"]} · evento único na colheita e no packing · reenvio offline não duplica.'}}); }};'''
    emit('MB-10','Cargas e entregas','pesagem, romaneio e confirmação de entrega, por papel',None,
         'Abrir pesagem da CG-1207',corpo,H_=780,back='MB-01.dc.html',primary_href='MB-10det.dc.html',js=js,dyn_status=True,
         prim=[('r0','a',f'Abrir pesagem da {CG["id"]}','MB-10det.dc.html'),('r1','b','Informar nova previsão','prever'),
               ('r2a','b',f'Confirmar chegada de {CG["liq"]}','chegou'),('r2b','a','Voltar a Hoje no campo','MB-01.dc.html')])

    # ---- MB-10det · pesagem-âncora CG-1207 ----
    corpo=(
      mcont('Cargas · fila da balança',f'{CG["id"]} · balança',H('ct_f'),H('ct_p'))
      + card('Identificação',[
          kv('Romaneio',CG['rom']+' · mamão Formosa de campo'),
          kv('Ordem de colheita',f'{CG["oc"]} · vínculo obrigatório'),
          kv('Rota',f'{CG["origem"]} → {CG["destino"]}'),
          kv('Veículo',CG['veic']),
          kv('Evidência',f'foto do ticket · 23/09 {CG["hora"]} · sincronização ok')],state='gray',desc='Confira veículo, ordem e rota antes de pesar.')
      + counters(('BRUTO',CG['bruto']),('TARA',CG['tara']),('LÍQUIDO',CG['liq']))
      + chips(dchip('ps'))
      + note(f'Ao confirmar: romaneio {CG["rom"]} emitido com {CG["liq"]} · a {CG["oc"]} soma {CG["acum"]} (saldo {CG["saldo"]}) · não conclui a ordem de colheita nem o recebimento no packing.')
      + btns(say('Registrar divergência','Divergência de 40 kg entre ticket e balança: pendência aberta com dono · a carga não sai até decisão.','alert','Registrar diferença de peso'),
             say('Próxima carga',f'{CG["veic"]} liberada · Carreta 02 volta ao talhão T7 para a próxima carga (saldo {CG["saldo"]}).','truck','Chamar a próxima carga'))
      + note('Confirmar a chegada no destino é tarefa do papel Recebedor; recusa registra motivo, quantidade e destinação proposta.'))
    js=f'''const ok=!!s.ps; v.ps=ok; v.nops=!ok; v.ct_f=ok?'chegada no packing (Recebedor)':'pesar e emitir romaneio'; v.ct_p=ok?'Voltar às cargas':'Confirmar pesagem';
DCH(v,'hdr',ok?'pesada · {CG["rom"]}':'na balança',ok?'green':'yellow');
DCH(v,'ps',ok?'Romaneio {CG["rom"]} emitido · {CG["liq"]}':'Pesagem a confirmar',ok?'green':'yellow');
v.pesar=()=>{{ self.setState({{ps:true,g2toast:'Pesagem confirmada · romaneio {CG["rom"]} emitido com {CG["liq"]} · {CG["oc"]} soma {CG["acum"]} — pesar não conclui a ordem de colheita.'}}); }};'''
    emit('MB-10',f'{CG["id"]} · pesagem',f'papel Balança · romaneio {CG["rom"]} · vínculo à {CG["oc"]}',None,
         f'Confirmar pesagem de {CG["liq"]}',corpo,H_=870,fname='MB-10det.dc.html',back='MB-10.dc.html',primary_href='MB-10.dc.html',js=js,dyn_status=True,
         prim=[('nops','b',f'Confirmar pesagem de {CG["liq"]}','pesar'),('ps','a','Voltar às cargas','MB-10.dc.html')])


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
