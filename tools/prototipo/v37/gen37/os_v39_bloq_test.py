# -*- coding: utf-8 -*-
"""O.S. · bloqueios do cenário na lista e no Kanban (verificador v39, itens 2, 4 e 6): liberação sem lote (OS-0418) e encerramento com
sobra em custódia (OS-0430) mostram selo e dono fora do painel; rótulo único "Rui (almoxarife)"; período da coluna Encerradas calculado."""
import sys, os, time, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
from conferencia_diaria_nav_helpers import conferir_dias
T = Os(); J = T.J; OS = 'OS-0430'
VERM = 'rgb(180, 35, 24)'; AMAR = 'rgb(138, 90, 0)'
def card(id_): return J(f"(()=>{{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(k=>k.innerText.trim().startsWith('{id_}')); return k?k.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def tab(t): J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab],button')].find(b=>b.innerText.trim()==='{t}'); b&&b.click();}})()"); time.sleep(.4)
def cor(id_, t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('{id_}')); if(!r) return ''; const s=[...r.querySelectorAll('span')].filter(s=>s.innerText.trim().startsWith({json.dumps(t)})).reverse().sort((a,b)=>a.innerText.length-b.innerText.length)[0]; return s?getComputedStyle(s).color:'';}})()") or ''
def hdr(): return J("(()=>{const s=document.querySelector('header h1').nextElementSibling; return s?s.innerText.trim():'';})()") or ''
try:
    T.abrir(wait=1.3)
    # ---- rótulo único do almoxarife (OS-0417) ----
    l = T.linha('OS-0417'); tab('Kanban'); k = card('OS-0417'); tab('Lista')
    T.ok(T.cel('OS-0417', 'Quem resolve') == 'Rui (almoxarife)' and T.cel('OS-0417', 'Prazo') == '24/09' and 'Rui (almoxarife) · 24/09' in k and 'almoxarifado)' not in l + k, 'OS-0417: lista e Kanban com "Rui (almoxarife)"', (l, k))
    h0 = hdr()
    # ---- liberação bloqueada pelo Estoque (OS-0418 sem lote de Ureia) ----
    T.ordem('OS-0418'); p = T.pan(); T.fechar(); l = T.linha('OS-0418')   # sem etapa de revisão: o Estoque segura desde a abertura
    T.ok('Liberar bloqueado: sem lote de Ureia 45%' in p, 'painel da OS-0418 aponta o bloqueio', p[p.find('PRÓXIMO'):][:200])
    T.ok('Falta insumo · Ureia 45%' in l and cor('OS-0418', 'Falta insumo') == VERM and T.cel('OS-0418', 'Quem resolve') == 'Suprimentos', 'lista da OS-0418: selo vermelho Falta insumo e dono Suprimentos', (l, cor('OS-0418', 'Falta insumo')))
    tab('Kanban'); k = card('OS-0418'); tab('Lista')
    T.ok('Falta insumo · Ureia 45%' in k and 'Suprimentos · ' in k, 'Kanban da OS-0418 com o mesmo selo e dono', k)
    T.ok(h0.endswith('3 impedidas') and hdr().endswith('3 impedidas'), 'cabeçalho conta a OS-0418 como impedida desde a abertura', (h0, hdr()))
    T.ok('Próximo passo: liberar para execução' not in p[p.find('SITUAÇÃO ATUAL'):], 'situação atual não manda liberar o que está bloqueado', p[p.find('SITUAÇÃO ATUAL'):][:220])
    # ---- encerramento bloqueado pela sobra (OS-0430) ----
    T.ordem(OS); T.btn('Liberar para execução'); T.btn('Confirmar liberação'); T.fechar()
    RQ = T.cen(f"c.ordens['{OS}'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): T.mudar(f"return cenEntregar(c,'{RQ}','{prod}',{q},'Marcos','Rui');", avisar=False)
    T.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,160,12,{{'Glifosato 480':300}});")
    T.ordem(OS); T.btn('Enviar para conferência'); T.btn('Confirmar envio'); T.fechar(); l = T.linha(OS)
    T.ok('Sobras a receber' in l and cor(OS, 'Sobras a receber') == AMAR and T.cel(OS, 'Quem resolve') == 'Rui (almoxarife)' and T.cel(OS, 'Próxima ação') == 'receber a devolução', 'lista da OS-0430: Sobras a receber + Rui (almoxarife)', l)
    tab('Kanban'); k = card(OS); tab('Lista')
    T.ok('Sobras a receber' in k and 'Rui (almoxarife) · receber a devolução' in k, 'Kanban da OS-0430 com o mesmo selo e dono', k)
    T.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true,'Rui');"); l = T.linha(OS)
    # B-R8 (09/10): 300 L de Glifosato informados para 160 ha (planejado 320 L) abrem a divergência de dose; depois da sobra, a pendência é
    # a revisão técnica de Ana (agrônoma). Expectativa mudada com motivo: regra nova; aceita a revisão, o dono volta a ser Marcos
    T.ok('Sobras a receber' not in l and 'Divergência de consumo/dose · Glifosato 480' in l and T.cel(OS, 'Quem resolve') == 'Ana (agrônoma)' and T.cel(OS, 'Próxima ação') == 'revisar a divergência de dose',
         'devolução recebida: selo de sobra sai; fica a divergência de dose com Ana (agrônoma)', l)
    T.mudar(f"return cenDivRever(c,'{OS}',1,'aceitar','Bordadura sem aplicação; vistoria sem rebrote','Ana');"); l = T.linha(OS)
    T.ok(T.cel(OS,'Quem resolve')=='Paula (conferência)' and 'Conferência diária pendente' in l,'Após revisão técnica, conferência diária tem dona Paula',l)
    T.ordem(OS);conferir_dias(T.J,OS,[1]);T.fechar();l=T.linha(OS)
    T.ok('Divergência de consumo/dose' not in l and T.cel(OS, 'Quem resolve') == 'Marcos' and T.cel(OS, 'Próxima ação') == 'conferir e encerrar', 'revisão aceita por Ana: selo sai e o dono volta a ser Marcos', l)
    T.ordem(OS); T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); T.fechar()
    # CTL-2 · A (AP-02): o turno do app grava a data operacional (CEN_DIA_OP = 26/09), não o relógio do aparelho → o período fecha em 26/09
    esp = 'período 10–26/09'
    tab('Kanban'); col = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,3).join(' | ')).pop()") or ''
    T.ok(col.endswith(esp) and '3' in col, 'coluna Encerradas com o período das ordens encerradas', (col, esp))
    T.ok(not T.erros(), 'sem erro JS', T.erros())
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
