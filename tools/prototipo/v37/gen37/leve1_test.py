# -*- coding: utf-8 -*-
"""LEVE-1 · travas sem dano viram clique direto, padrão preenchido ou aviso (proprietário 19/10: "Não quero um sistema travado e burocrático,
quero leve e fluido"; AGENTS §4; triagem em docs/integracao/V73/LEVE/INVENTARIO.md). No Chrome headless, como a pessoa faz, dados sintéticos.
  I1  O.S.: Iniciar execução e Enviar para conferência gravam no clique (sem "Confirmar …"), com recibo; toque duplo não faz nada de novo;
      Aprovar, Liberar e Encerrar continuam pedindo confirmação. Mapa (IN-04): Iniciar no painel do talhão também grava no clique.
  I2  App: Fechar turno vem com as horas = agora − início − pausas (editável) e fecha sem digitar as horas; apagado ou sem início, pede.
      Colheita (MB-10): com turno aberto na O.S., as horas da área vêm preenchidas; sem turno, o campo fica vazio.
  I3  O.S. › Nova ordem: início da janela = data do gatilho do plano (c1 · a7 = 14/12/2026) ou hoje se o gatilho já passou; editável.
  I4  Manutenção › Liberar OM: executante (pessoa única habilitada) e tempo do serviço já vêm preenchidos (já era assim na base: sem contraprova).
  I5  Vincular ativo sem execução registrada: "Contar de agora" marcado e a primária ligada.
  I6  Cadastros › Produtos: digitar o preço preenche a data do preço com hoje (23/09/2026).
  I7  Comercial: encerrar com carga programada cancela a carga no mesmo comando (comercial_unit_test C09/RV-A5c cobre o comando).
  I8  Gestão (GE-03) e Campo (CA-02) sem os botões "Prévia · nada foi alterado".
  I9  Motivo opcional: cancelar OM, fechar achado e checklist do app (Não feito) sem motivo; reordenar a fila da Logística; alçada AL-05
      (redução, vale na hora); irrigação: aceitar divergência e fertirrigação sem motivo.
  I10 Cadastros › Fazendas: talhão acima da área da fazenda salva com aviso no recibo.
  I11 Irrigação › Terminar sem a leitura do hidrômetro: Em conferência "Sem leitura", nada creditado no balanço.
Uso (de gen37/): env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B leve1_test.py
       RENDER_DIR=<outro _render> (ou ANTES=<_render da base>) roda contra outro build (contraprova). Sai 1 se algo falhar.
Emulação no Chrome headless; não é aparelho físico."""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('ANTES') or os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, '' if cond else str(info)[:900], flush=True)
class secao:
    def __init__(self, nome): self.nome = nome
    def __enter__(self): print('==', self.nome, flush=True); return self
    def __exit__(self, t, e, tb):
        if t: chk(self.nome + ' · o roteiro não chegou ao fim do trecho', False, repr(e)[:400])
        return True
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def espera(e, s=8):
    f = time.time() + s
    while time.time() < f:
        try:
            if J(e): return True
        except Exception: pass
        time.sleep(.2)
    return False
def ir(pg, w=1440, h=1000, limpa=False, perfil=None, toque=False, espera_s=1.2):
    c.aparelho(w, h, 1, toque)
    if limpa or perfil:
        c.goto(U('Main.dc.html'), .3)
        if limpa: J("localStorage.clear(); sessionStorage.clear(); 1")
        if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)}); 1")
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.15); c.goto(U(pg), espera_s)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def alertas(): return J("[...document.querySelectorAll('[role=alert]')].filter(x=>x.getClientRects().length).map(x=>x.innerText).join(' | ')") or ''
def botoes(root='body'): return J(f"[...document.querySelectorAll({json.dumps(root + ' button')})].filter(b=>b.getClientRects().length).map(b=>{N}(b.innerText))") or []
def clk(t, root='body', w=.5):
    r = J(f"(()=>{{const els=[...document.querySelectorAll({json.dumps(root + ' button,' + root + ' a')})].filter(e=>e.getClientRects().length&&!e.disabled);"
          f" const e=els.find(x=>{N}(x.innerText)==={json.dumps(t)})||els.find(x=>{N}(x.innerText).startsWith({json.dumps(t)})); if(!e) return 'NÃO ACHEI: '+{json.dumps(t)}; e.click(); return 'ok';}})()")
    time.sleep(w); return r
SETV = "((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"
def setv(sel, val): r = J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.3); return r
def val(sel): return J(f"(()=>{{const i=document.querySelector({json.dumps(sel)}); return i?i.value:null;}})()")
def cen(expr): return J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")
def cen_mudar(body): return J(f"(()=>{{const X=window.__cen; const r=X.cenMudar(null,c=>{{{body}}}); window.dispatchEvent(new StorageEvent('storage',{{key:'talhao-os-cenario-v1'}})); return r.erro||r.msg||'';}})()")
def man(expr): return J(f"(()=>{{const m=window.__man.manGet(); return ({expr});}})()")
def man_mudar(body): return J(f"(()=>{{const X=window.__man; const r=X.manMudar(null,m=>{{{body}}}); return r&&(r.erro||r.msg)||'';}})()")
HM = "(m=>{const d=new Date(Date.now()-m*60000); return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);})"
PAN_OS = "aside[role=dialog]"
def pan_os(): return J(f"(()=>{{const a=document.querySelector({json.dumps(PAN_OS)}); return a?{N}(a.innerText):'';}})()") or ''
def abre_os(id_):
    J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.split(/\\s+/).indexOf({json.dumps(id_)})>=0); r&&r.click();}})()"); time.sleep(.5)

try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    # ======================================================================================== I1 · O.S. e Mapa
    with secao('I1 O.S. · Iniciar e Enviar gravam no clique'):
        ir('OS.dc.html', limpa=True); espera("!!(window.__cen&&window.__cen.cenGet)")
        cen_mudar("const X=window.__cen; X.cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); return X.cenConfirmarRecebimento(c,'REQ-039');")
        ir('OS.dc.html#OS-0424'); time.sleep(.4)
        b0 = botoes(PAN_OS); clk('Iniciar execução', PAN_OS); tt = toast(); b1 = botoes(PAN_OS); et = cen("c.ordens['OS-0424'].etapa")
        chk('I1a Iniciar execução grava no clique: OS-0424 Em execução, recibo "OS-0424 em execução: insumos com Marcos", sem bloco "Confirmar início"',
            'Iniciar execução' in b0 and et == 'Em execução' and 'OS-0424 em execução: insumos com Marcos, confirmados no app' in tt and 'Confirmar início' not in b1, [b0, et, tt, b1])
        # I1b toque duplo de verdade: dois cliques no mesmo botão, na mesma tarefa (a 2ª chamada usa a fase de antes do 1º clique). osDireto
        # vive no escopo da página (não é global); a guarda da função é coberta por leve1_unit (U1b/U1c). Oráculo: uma ordem em execução,
        # nenhum erro "não está liberada" no painel nem alerta; o aviso é o recibo ou "já está em Em execução: nada foi feito de novo".
        ir('OS.dc.html', limpa=True); espera("!!(window.__cen&&window.__cen.cenGet)")
        cen_mudar("const X=window.__cen; X.cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); return X.cenConfirmarRecebimento(c,'REQ-039');")
        ir('OS.dc.html#OS-0424'); time.sleep(.4)
        rd = J(f"(()=>{{const e=[...document.querySelectorAll({json.dumps(PAN_OS + ' button')})].find(b=>b.getClientRects().length&&{N}(b.innerText)==='Iniciar execução'); if(!e) return 'NÃO ACHEI'; e.click(); e.click(); return 'ok';}})()")
        time.sleep(.6); td = toast(); pd = pan_os(); ad = alertas(); etd = cen("c.ordens['OS-0424'].etapa")
        chk('I1b toque duplo em "Iniciar execução": uma vez em execução, sem erro ("não está liberada") no painel nem alerta; aviso = recibo ou "nada foi feito de novo"',
            rd == 'ok' and etd == 'Em execução' and 'não está liberada' not in pd and 'não está liberada' not in ad
            and ('OS-0424 em execução: insumos com Marcos' in td or 'já está em Em execução: nada foi feito de novo' in td), [rd, etd, td, ad, pd[:300]])
        cen_mudar("const o=c.ordens['OS-0424']; o.realizado=o.area; o.saldo=0; return {msg:'saldo zero (roteiro do teste)'};"); time.sleep(.5)
        ir('OS.dc.html#OS-0424'); time.sleep(.4)
        b2 = botoes(PAN_OS); clk('Enviar para conferência', PAN_OS); tt = toast(); b3 = botoes(PAN_OS); et = cen("c.ordens['OS-0424'].etapa"); fim = cen("JSON.stringify((c.ordens['OS-0424'].osc||{}).fim||[])")
        chk('I1c Enviar para conferência grava no clique: Em conferência, recibo com quem enviou (CMD-08 gravado), sem "Confirmar envio"',
            'Enviar para conferência' in b2 and et == 'Em conferência' and 'OS-0424 enviada para conferência por' in tt and 'Confirmar envio' not in b3 and 'CMD-08' in (fim or ''), [b2, et, tt, b3, fim])
        # I1d na OS-0508 (Em conferência no cenário-semente e sem impedimento, a mesma do config_test): a OS-0424 do roteiro fica com a
        # sobra do Fungicida em custódia, e aí o painel mostra "Encerrar bloqueado" em vez do botão (trava que fica, AGENTS §4).
        ir('OS.dc.html#OS-0508'); time.sleep(.4); b4a = botoes(PAN_OS); r4 = clk('Conferir e encerrar', PAN_OS); b4 = botoes(PAN_OS); et4 = cen("c.ordens['OS-0508'].etapa")
        chk('I1d Encerrar continua pedindo confirmação ("Confirmar encerramento"; OS-0508 segue Em conferência antes dela)', r4 == 'ok' and 'Confirmar encerramento' in b4 and et4 == 'Em conferência', [r4, b4a, b4, et4])
        ir('OS.dc.html#OS-0430'); time.sleep(.3); clk('Liberar para execução', PAN_OS); b5 = botoes(PAN_OS); et5 = cen("c.ordens['OS-0430'].etapa")
        chk('I1e Liberar continua pedindo confirmação ("Confirmar liberação"; a ordem segue A liberar)', 'Confirmar liberação' in b5 and et5 == 'A liberar', [b5, et5])
    with secao('I1 Mapa · Iniciar grava no clique'):
        ir('OS.dc.html', limpa=True); espera("!!(window.__cen&&window.__cen.cenGet)")
        cen_mudar("const X=window.__cen; X.cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); return X.cenConfirmarRecebimento(c,'REQ-039');")
        tal = cen("c.ordens['OS-0424'].talhao") or ''
        J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'})); 1"); ir('IN-04.dc.html', espera_s=1.6)
        J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Ordens de serviço'); b&&b.click();})()"); time.sleep(.8)
        ids = J("[...document.querySelectorAll('svg [role=button]')].map(x=>x.getAttribute('data-talhao')).filter(Boolean)") or []
        alvo = next((t for t in ids if tal.startswith(t)), None) or next((t for t in ids if t in tal), None)
        J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>x.getAttribute('data-talhao')==={json.dumps(alvo)}); e&&e.dispatchEvent(new MouseEvent('click',{{bubbles:true}}));}})()"); time.sleep(.7)
        J("(()=>{const b=[...document.querySelectorAll('main aside button')].find(b=>b.innerText.trim().startsWith('OS-0424')); b&&b.click();})()"); time.sleep(.5)
        bm = botoes('main aside'); r = clk('Iniciar execução', 'main aside'); tm = toast(); bm2 = botoes('main aside')
        ir('OS.dc.html'); espera("!!(window.__cen&&window.__cen.cenGet)"); etm = cen("c.ordens['OS-0424'].etapa")
        chk(f'I1f Mapa ({alvo}): "Iniciar execução" no painel do talhão grava no clique (OS-0424 Em execução), sem "Confirmar início"',
            r == 'ok' and etm == 'Em execução' and 'Confirmar início' not in bm2 and 'OS-0424 em execução' in tm, [alvo, tal, r, bm, bm2, tm, etm])
    # ======================================================================================== I2 · App: horas do turno
    with secao('I2 App · Fechar turno com horas preenchidas'):
        ir('MB-03.dc.html', 390, 1800, limpa=True, toque=True); espera("!!(window.__cen&&window.__cen.cenGet)")
        clk("Iniciar turno · OS-0421") if 'Iniciar turno · OS-0421' in ' '.join(botoes()) else J("(()=>{const b=document.querySelector('main button[title=\"Iniciar turno na OS-0421\"]'); b&&b.click();})()")
        time.sleep(.6); t0 = cen("c.app.turno&&c.app.turno.os")
        # turno começou há 185 min, com uma pausa de 25 min (há 70 → há 45 min): 160 min = 2,7 h (estável por 2 min)
        J(f"(()=>{{const X=window.__cen; X.cenMudar(null,c=>{{ const t=c.app.turno; t.ini={HM}(185); t.pausas=[{{ini:{HM}(70),fim:{HM}(45)}}]; return {{msg:'ok'}}; }}); }})()")
        ir('MB-03.dc.html', 390, 1800, toque=True); espera("!!document.querySelector('#ft_h')")
        h = val('#ft_h'); dica = J("(()=>{const i=document.querySelector('#ft_h'); return i?i.parentElement.innerText.replace(/\\s+/g,' '):'';})()") or ''
        chk('I2a Fechar turno: horas pré-preenchidas = agora − início − pausas = 2,7 h, com a dica do cálculo', t0 == 'OS-0421' and h == '2,7' and 'Calculado' in dica, [t0, h, dica])
        setv('#ft_h', ''); clk('Fechar turno'); al = alertas() + ' ' + toast()
        chk('I2b campo apagado volta a pedir: "Informe as horas trabalhadas." (nada inventado)', 'Informe as horas trabalhadas.' in al and cen("!!c.app.turno") is True, al)
        ir('MB-03.dc.html', 390, 1800, toque=True); espera("!!document.querySelector('#ft_h')")
        n0 = cen("c.ordens['OS-0421'].ap.filter(a=>a.st!=='Previsto').length")
        setv('#ft_ha', '20'); clk('Fechar turno'); time.sleep(.4)
        ap = cen("(()=>{const a=c.ordens['OS-0421'].ap.filter(a=>a.st!=='Previsto'); return a[a.length-1];})()") or {}
        chk('I2c sem digitar as horas, Fechar turno grava 20 ha em 2,7 h (o apontamento recebe as horas calculadas)', cen("!!c.app.turno") is False and cen("c.ordens['OS-0421'].ap.filter(a=>a.st!=='Previsto').length") == n0 + 1 and abs((ap.get('h') or 0) - 2.7) < 1e-9, [ap, toast()])
        r = J(f"(()=>{{const X=window.__cen; const r1=X.cenMudar(null,c=>X.cenIniciarTurno(c,'OS-0421')); const r=X.cenMudar(null,c=>{{ c.app.turno.ini={HM}(185); c.app.turno.pausas=[{{ini:{HM}(70),fim:{HM}(45)}}]; return X.cenFecharTurno(c,5,undefined,{{'Fungicida A':2.5}}); }}); return [r1.erro||'',r.erro||r.msg||''];}})()") or ['', '']
        chk('I2d o comando (cenFecharTurno) sem horas calcula as do turno: "Turno fechado: 5 ha em 2,7 h"', 'Turno fechado: 5 ha em 2,7 h' in r[1], r)
        r = J("(()=>{const X=window.__cen; X.cenMudar(null,c=>X.cenIniciarTurno(c,'OS-0421')); const r=X.cenMudar(null,c=>{ c.app.turno.ini=''; return X.cenFecharTurno(c,5,undefined,{'Fungicida A':2.5}); }); X.cenMudar(null,c=>{ c.app.turno.ini=''; return {msg:'ok'}; }); return r.erro||r.msg;})()")
        ir('MB-03.dc.html', 390, 1800, toque=True); espera("!!document.querySelector('#ft_h')")
        chk('I2e sem início registrado: o comando recusa ("Informe as horas trabalhadas.") e o campo fica vazio (nada inventado)', 'Informe as horas trabalhadas.' in (r or '') and val('#ft_h') == '', [r, val('#ft_h')])
    with secao('I2 App · colheita (MB-10)'):
        ir('MB-10.dc.html', 390, 1800, limpa=True, toque=True); espera("!!(window.__cen&&window.__cen.cenGet)")
        clk('Apontar área · OS-0505'); time.sleep(.3); h0 = val('#mb_h')
        J(f"(()=>{{const X=window.__cen; X.cenMudar(null,c=>{{ c.app.turno={{os:'OS-0505',ini:{HM}(185),d:'26/09',chave:'TU-T',pausas:[{{ini:{HM}(70),fim:{HM}(45)}}],fim:null}}; return {{msg:'ok'}}; }}); }})()")
        ir('MB-10.dc.html', 390, 1800, toque=True); espera("!!(window.__cen&&window.__cen.cenGet)"); clk('Apontar área · OS-0505'); time.sleep(.3); h1 = val('#mb_h')
        chk('I2f colheita: sem turno, horas vazias (pede); com turno aberto na OS-0505, horas = 2,7 (editáveis)', h0 == '' and h1 == '2,7', [h0, h1])
    # ======================================================================================== I3 · Nova ordem
    with secao('I3 O.S. › Nova ordem: início da janela preenchido'):
        ir('OS.dc.html', limpa=True); espera("!!(window.__cen&&window.__cen.cenGet)"); hoje = cen("c.diaOperacional")   # CEN_DIA_OP = CEN0.diaOperacional (a constante não é global na página)
        r = clk('Criar ordem', 'header'); r = r if r == 'ok' else clk('Nova ordem')
        setv('#nv_saf', 'S2627'); setv('#nv_cult', 'c1'); setv('#nv_atv', 'a7'); j7 = val('#nv_jan'); d7 = J("(()=>{const i=document.querySelector('#nv_jan'); return i?i.parentElement.innerText.replace(/\\s+/g,' '):'';})()") or ''
        setv('#nv_atv', 'a1'); j1 = val('#nv_jan'); d1 = J("(()=>{const i=document.querySelector('#nv_jan'); return i?i.parentElement.innerText.replace(/\\s+/g,' '):'';})()") or ''
        chk('I3a c1 · a7 (DAP +60): início da janela = 2026-12-14 (gatilho do plano); a1 (DAP −20 = 25/09, já passou) = hoje ' + str(hoje),
            j7 == '2026-12-14' and 'gatilho do plano' in d7 and j1 == hoje and 'já passou' in d1, [j7, d7, j1, d1, hoje])
        setv('#nv_jan', '2026-12-20'); setv('#nv_atv', 'a7'); je = val('#nv_jan')
        chk('I3b data escolhida à mão vale ao trocar a atividade (editável, não volta ao padrão)', je == '2026-12-20', je)
        clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
        clk('Criar ordem', 'header'); setv('#nv_saf', 'S2627'); setv('#nv_cult', 'c1'); setv('#nv_atv', 'a7'); clk('Emitir ordem', 'aside[role=dialog]'); tt = toast()
        no = cen("(()=>{const k=Object.keys(c.ordens).filter(k=>c.ordens[k].osc&&c.ordens[k].osc.novo); const o=k.length?c.ordens[k[k.length-1]].osc.novo:null; return o?[o.id,o.jan,o.janela]:null;})()")
        chk('I3c Emitir sem escolher data grava a janela do gatilho ("a partir de 14/12/2026")', bool(no) and no[1] == '2026-12-14' and no[2] == 'a partir de 14/12/2026', [no, tt])
        clk('Criar ordem', 'header'); setv('#nv_saf', 'S2627'); setv('#nv_cult', 'c1'); setv('#nv_atv', 'a6'); setv('#nv_jan', ''); clk('Emitir ordem', 'aside[role=dialog]'); al = alertas()
        chk('I3d campo apagado volta a pedir ("Informe o início da janela.")', 'Informe o início da janela.' in al, al)
    # ======================================================================================== I4 / I5 / I9 · Manutenção
    with secao('I4 Manutenção › Liberar OM com executante e tempo preenchidos'):
        ir('MA.dc.html', 1440, 1000, limpa=True, perfil='Otávio'); espera("!!(window.__man&&window.__man.manGet)")
        man_mudar("return window.__man.manGerarTodas(m,null,'Otávio');"); ir('MA.dc.html#om=OM-0234', perfil='Otávio'); espera("!!document.querySelector('#ma-painel')")
        ex = val('#om-exe'); tp = val('#om-tempo')
        # OM-0234 tem conflito de janela no cenário (OS-0420 em 28/09): a primária é "Mover janela" e o liberar vem como "Liberar mesmo assim";
        # "Liberar serviço" e "Liberar mesmo assim" usam o mesmo desligamento ("Falta: executante" / "Falta: tempo previsto"), que é o que o item prova
        lib = J("(()=>{const b=[...document.querySelectorAll('#ma-painel button')].find(b=>['Liberar serviço','Liberar mesmo assim'].indexOf(b.innerText.trim())>=0); return b?[b.innerText.trim(),!b.disabled&&b.getAttribute('aria-disabled')!=='true']:null;})()")
        chk('I4 (já na base) OM-0234: executante Zé (única pessoa habilitada) e tempo do serviço 5 h já preenchidos; o botão de liberar ligado (sem "Falta: …")', ex == 'Zé' and tp == '5' and bool(lib) and lib[1] is True, [ex, tp, lib])
    with secao('I9 Manutenção · motivo opcional'):
        r = man_mudar("return window.__man.manCancelar(m,'OM-0234','','Otávio','T-LEVE-CANC');"); cc = man("m.oms['OM-0234'].canc||{}") or {}
        chk('I9a cancelar OM sem motivo: cancela, grava quem e quando (motivo vazio) e devolve a reserva', man("m.oms['OM-0234'].etapa") == 'Canceladas' and cc.get('motivo') == '' and 'Otávio' in (cc.get('por') or '') and bool(cc.get('em')), [r, cc])
        ir('MA.dc.html', 1440, 1000, limpa=True, perfil='Otávio'); espera("!!(window.__man&&window.__man.manGet)")
        qid = 'SM-0150'   # colhedora sem OM e sem vencimento devido: "Fechar sem serviço" entre as secundárias (AC-PCM-09)
        ir(f'MA.dc.html#achado={qid}', perfil='Otávio'); espera("!!document.querySelector('#ma-painel')")
        clk('Fechar sem serviço', '#ma-painel'); clk('Fechar sem serviço', '#ma-painel'); time.sleep(.3); q = man(f"m.achados[{json.dumps(qid)}]") or {}
        chk(f'I9b achado {qid}: Fechar sem serviço sem motivo fecha, com quem e quando', q.get('estado') == 'Fechado sem serviço' and 'Otávio' in ((q.get('dec') or {}).get('por') or ''), [qid, q.get('estado'), q.get('dec'), alertas(), toast()])
    with secao('I9 App · checklist fora de OK sem motivo'):
        ir('MB-01.dc.html', 390, 1800, limpa=True, toque=True); clk('Restaurar demonstração')
        J("(()=>{const s=document.querySelector('select[aria-label=\"Usuário do app (demonstração)\"]'); if(!s) return; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,'Zé'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.6)
        ir('MB-09det.dc.html#OM-0233', 390, 1800, toque=True); espera("!!(window.__man&&window.__man.manGet)")
        J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').startsWith('Não feito · Substituir bomba')||b.innerText.trim()==='Não feito'); b&&b.click();})()"); time.sleep(.5)
        r = clk('Registrar Não feito'); time.sleep(.4); t = man("m.oms['OM-0233'].chk[0]") or {}
        chk('I9c app (Zé, OM-0233): "Não feito" sem motivo grava a resposta com quem e quando', t.get('r') == 'Não feito' and 'Zé' in (t.get('por') or ''), [r, t, toast()])
    with secao('I5 Vincular ativo: Contar de agora por padrão'):
        ir('MA.dc.html#vis=ativos&pend=semplano', 1440, 1000, limpa=True, perfil='Otávio'); espera("!!(window.__man&&window.__man.manGet)"); time.sleep(.5)
        J("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='a12'&&r.getClientRects().length); const a=r&&[...r.querySelectorAll('a')].find(a=>/^Vincular ao /.test(a.innerText.trim())); a&&a.click();})()"); time.sleep(.8)
        ag = J("(()=>{const b=[...document.querySelectorAll('#vl-painel button')].find(x=>x.innerText.trim()==='Contar de agora'); return b?b.getAttribute('aria-pressed'):null;})()")
        pr = J("(()=>{const b=[...document.querySelectorAll('#vl-painel button')].find(x=>/^Vincular ao PM-07/.test(x.innerText.trim())); return b?{dis:b.disabled||b.getAttribute('aria-disabled')==='true'}:null;})()")
        chk('I5 Gotejo T7 sem execução registrada: "Contar de agora" marcado e "Vincular ao PM-07" ligado (um toque a menos)', ag == 'true' and pr and not pr['dis'], [ag, pr])
    # ======================================================================================== I6 · Produtos
    with secao('I6 Cadastros › Produtos: data do preço = hoje'):
        ir('CD-06.dc.html', limpa=True); time.sleep(.3); clk('Criar item', 'header'); time.sleep(.3)
        d0 = val("aside[role=dialog] [id$='_pdata']"); setv("aside[role=dialog] [id$='_preco']", '85'); d1 = val("aside[role=dialog] [id$='_pdata']")
        chk('I6 digitar o preço preenche a data do preço com hoje (2026-09-23), editável', d0 == '' and d1 == '2026-09-23', [d0, d1])
    # ======================================================================================== I8 · Prévias sem efeito
    with secao('I8 botões "Prévia · nada foi alterado" saem'):
        ir('GE-03.dc.html', limpa=True); b = ' | '.join(botoes()); tx = J("document.body.innerText") or ''
        chk('I8a GE-03 sem "Conferir reabertura de 08/2026"; "Conciliar diesel do tanque" segue', 'Conferir reabertura de 08/2026' not in b and 'Conciliar diesel do tanque' in b, b[:400])
        ir('CA-02.dc.html'); b = ' | '.join(botoes()); bl = ' | '.join(J("[...document.querySelectorAll('a')].filter(a=>a.getClientRects().length).map(a=>a.innerText.trim())") or [])
        chk('I8b CA-02 sem "Conferir reabertura do saldo"; o atalho "Abrir O.S." segue', 'Conferir reabertura do saldo' not in b and 'Abrir O.S.' in bl, [b[:300], bl[:300]])
    # ======================================================================================== I9 · Logística, Configurações, Irrigação
    with secao('I9 Logística · reordenar a fila sem motivo'):
        ir('LO-02.dc.html', limpa=True)
        J("(()=>{const t=[...document.querySelectorAll('[role=table]')][0]; const r=t&&[...t.querySelectorAll('[role=row]')].find(r=>/^T4\\b/.test(r.innerText.trim())||r.innerText.indexOf('T4')>=0&&r.innerText.indexOf('frota própria')>=0); const cel=r&&r.querySelector('[role=cell]'); cel&&cel.click();})()"); time.sleep(.5)
        sel = J("(()=>{const s=document.querySelector('aside[role=dialog] select'); return s?s.id:'';})()")
        setv(f'#{sel}', '2'); clk('Salvar', 'aside[role=dialog]'); tt = toast(); al = alertas()
        chk('I9d LO-02: reordenar o T4 sem motivo publica a fila nova com autor e horário (sem "Informe motivo")', 'publicada' in tt and 'T4 na posição 2' in tt and 'Informe' not in al, [sel, tt, al])
    with secao('I9 Configurações · AL-05 sem motivo'):
        ir('CF-01.dc.html', limpa=True, perfil='Ana'); time.sleep(.3)
        J("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf('AL-05 · Dispensar')>=0); r&&((r.querySelector('.g2pw')||r).click());})()"); time.sleep(.5)
        setv('#cf1_lim', '15'); b = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar alçada'); return b?!b.disabled&&b.getAttribute('aria-disabled')!=='true':null;})()")
        clk('Salvar alçada', 'aside[role=dialog]'); tt = toast()
        chk('I9e AL-05 20 → 15 % (não amplia poder) sem motivo: "Salvar alçada" ligado e a v2 vale na hora', b is True and 'AL-05 v2 vigente' in tt, [b, tt])
        ir('CF-01.dc.html', perfil='Ana'); time.sleep(.3)
        J("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf('AL-05 · Dispensar')>=0); r&&((r.querySelector('.g2pw')||r).click());})()"); time.sleep(.5)
        setv('#cf1_lim', '25'); d = J("(()=>{const d=document.querySelector('aside[role=dialog]'); return d?d.innerText.replace(/\\s+/g,' '):'';})()") or ''
        chk('I9f ampliar o próprio poder (15 → 25 %) continua pedindo 2º aprovador', 'aguarda 2º aprovador' in d and 'Enviar para confirmação' in ' '.join(botoes('aside[role=dialog]')), d[:400])
    with secao('I9/I11 Irrigação · terminar sem leitura e sem motivo; aceitar divergência e fertirrigação sem motivo'):
        IRR = "JSON.parse(localStorage.getItem('talhao-os-irrigacao-v1')||'null')"
        ir('IR-03det.dc.html#OS-0419', limpa=True, espera_s=1.6); clk('Iniciar irrigação'); time.sleep(.4)
        b0 = J(f"(()=>{{const s={IRR}; return s?JSON.stringify(s.setores.P2.bal.ap):'';}})()")
        clk('Registrar término antecipado'); time.sleep(.3); setv('#tm_cob', '80'); clk('Registrar término antecipado', 'aside[role=dialog]'); time.sleep(.4)
        o = J(f"(()=>{{const s={IRR}; const o=s&&s.ordens['OS-0419']; return o?{{et:o.etapa,conf:o.conf,vol:o.passadas[0].vol,mot:o.passadas[0].motivoTempo}}:null;}})()") or {}
        b1 = J(f"(()=>{{const s={IRR}; return s?JSON.stringify(s.setores.P2.bal.ap):'';}})()"); al = alertas()
        chk('I11 Terminar sem a leitura do hidrômetro (e sem motivo da área e tempo): Em conferência "Sem leitura", volume nulo (não zero), nada creditado no balanço',
            o.get('et') == 'Em conferência' and (o.get('conf') or {}).get('st') == 'Sem leitura' and o.get('vol') is None and b0 == b1, [o, al, toast(), b0 == b1])
        ir('IR-03det.dc.html#OS-0394:conferir', limpa=True, espera_s=1.6); time.sleep(.4)
        bt = ' | '.join(botoes('aside[role=dialog]')); clk('Aceitar divergência', 'aside[role=dialog]'); time.sleep(.4)
        o = J(f"(()=>{{const s={IRR}; const o=s&&s.ordens['OS-0394']; return o?{{et:o.etapa,conf:o.conf}}:null;}})()") or {}
        chk('I9g aceitar a divergência do hidrômetro sem motivo: encerra, hidrômetro prevalece, quem gravado', o.get('et') == 'Encerradas' and (o.get('conf') or {}).get('st') == 'Hidrômetro prevaleceu' and bool((o.get('conf') or {}).get('quem')), [bt, o, alertas()])
        # I9h pela tela: OS-0419 antes de iniciar, "Adicionar produtos" com o motivo em branco (o formulário abre com Ureia 45% e 12 kg/ha)
        ir('IR-03det.dc.html#OS-0419', limpa=True, espera_s=1.6); r1 = clk('Adicionar produtos'); time.sleep(.3); r2 = clk('Criar versão v2'); time.sleep(.4)
        f = J(f"(()=>{{const s={IRR}; const o=s&&s.ordens['OS-0419']; return o?{{v:o.versao,fert:o.fert?{{prod:o.fert.prod,dose:o.fert.dose,mot:o.fert.mot}}:null}}:null;}})()") or {}
        chk('I9h fertirrigação (Adicionar produtos) sem motivo agronômico: cria a v2 (o agrônomo libera na O.S.), motivo vazio gravado',
            r1 == 'ok' and r2 == 'ok' and f.get('v') == 'v2' and bool(f.get('fert')) and (f.get('fert') or {}).get('mot') == '', [r1, r2, f, alertas(), toast()])
    # ======================================================================================== I10 · Fazendas
    with secao('I10 Cadastros › Fazendas: área acima da fazenda vira aviso'):
        ir('CD-01.dc.html', limpa=True); time.sleep(.3)
        # a árvore abre recolhida (DRILL-RECOLHIDO, como no cadf_test): o T4 da Santa Rita aparece depois do "Expandir tudo"
        J("[...document.querySelectorAll('button.g2xtog')].filter(b=>b.getClientRects().length&&/Expandir/.test(b.innerText)).forEach(b=>b.click())"); time.sleep(.4)
        J("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].find(r=>{const c=r.querySelector('[role=cell]'); return c&&c.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()==='T4';}); r&&((r.querySelector('[role=cell] span')||r).click());})()"); time.sleep(.5)
        aberto = J("!!document.querySelector('aside[role=dialog]')") and val("aside[role=dialog] [id$='_faz']") == 'Santa Rita'
        setv("aside[role=dialog] [id$='_decl']", '2000'); clk('Salvar', 'aside[role=dialog]'); time.sleep(.3); tt = toast(); al = alertas(); ainda = J("!!document.querySelector('aside[role=dialog]')")
        chk('I10 talhão T4 com 2.000 ha (acima da Santa Rita): salva e o recibo traz o aviso da soma; nada barrado', aberto and not ainda and 'Aviso:' in tt and 'talhões ativos da' in tt, [aberto, ainda, tt, al])
    err = J("window.__err||''") or ''
    chk('sem erro de JavaScript na última tela', not err, err)
finally:
    try: c.close()
    finally: srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + ' ; '.join(FAIL) if FAIL else ''), flush=True)
sys.exit(1 if FAIL else 0)
