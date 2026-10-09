# -*- coding: utf-8 -*-
"""B-R8 · parte de navegador do dose_divergente_test.py: app MB-03 (390 px), O.S. (1440 px e 390 px) sobre o mesmo cenário (localStorage).
Caminho normal (turno com dose divergente → recibo, selo, linha do apontamento, aceite), erro/recusa (perfil sem papel, motivo vazio,
encerrar antes da revisão), repetição (mesma revisão de novo não grava) e o encerramento depois da correção registrada.
Capturas em _probe/dose_div_*.png. Uso: python3 dose_divergente_test.py nav   (compile antes: build.py && montar_render.py)"""
import json, os, re, time
from app_lib import App

HERE = os.path.dirname(os.path.abspath(__file__))
OS = 'OS-0430'
SELO = 'Divergência de consumo/dose'


def rodar():
    a = App(['MB-01', 'MB-03', 'OS']); J = a.J; erros = []
    shot = lambda n: a.c.shot(os.path.join(HERE, '_probe', n))
    def web(w=1440):
        a.c.size(w, 1100); a.abrir('OS'); time.sleep(.3)
    def ordem(id_):
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r&&r.click();}})()"); time.sleep(.45)
    def pan():
        if J('(()=>{const bs=[...document.querySelectorAll(\'aside[role=dialog] section[aria-label] > button[aria-expanded="false"]\')]; bs.forEach(b=>b.click()); return bs.length;})()'): time.sleep(.3)
        return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    def btn(t):
        r = J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.45); return r
    def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)}&&b.offsetParent!==null)"))
    def settx(lab, val):
        return J(f"""(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] textarea')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)}); if(!i) return 'NÃO ACHEI';
          Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()""")
    def alerta(): return J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
    def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def linha(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    def aba(n): J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(n)}); b&&b.click();}})()"); time.sleep(.4)
    def cartao(id_): return J(f"(()=>{{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(x=>x.innerText.indexOf({json.dumps(id_)})===0); return k?k.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    def perfil(k):
        J(f"(()=>{{const i=document.querySelector('[aria-label=\"Trocar perfil de demonstração\"]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(k)}); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.4)
    def cmd(js):
        return J("(()=>{const W=window.__cen; const r=W.cenMudar(null,c=>" + js + "); return r.erro||r.msg||'';})()") or ''
    def guard(): erros.extend(a.erros() or [])
    def sem_rolagem(): return J("document.documentElement.scrollWidth<=window.innerWidth+1")
    REV = f"c.ordens['{OS}'].ap.filter(x=>x.rev).map(x=>x.dia+':'+x.rev.dec+':'+x.rev.quem).join(',')"
    try:
        a.c.size(390, 1800); a.abrir('MB-01'); a.clk('Restaurar demonstração'); time.sleep(.3)
        # preparo (como o escritório e o almoxarifado fariam): Ana aprova e libera a OS-0430; Rui entrega os três insumos a Marcos; Marcos confirma
        web()
        p0 = cmd(f"(W.osc_liberar(c,'{OS}',false,'','Ana'), c.reqs[c.ordens['{OS}'].req].itens.forEach(i=>W.cenEntregar(c,c.ordens['{OS}'].req,i.prod,i.solicitado,'Marcos','Rui')), W.cenConfirmarRecebimento(c,c.ordens['{OS}'].req))")
        a.ok(p0.startswith('Recebimento confirmado'), 'preparo: OS-0430 liberada por Ana, insumos entregues e confirmados: ' + p0[:90])
        # 1 · app (390 px): turno de 10 ha com Glifosato 20 L, 2,4-D 0 L e Óleo 0 L (planejado 20 / 10 / 5) → recibo com a divergência
        a.c.size(390, 1800); a.abrir('MB-03'); r = a.clk_sel(f'main button[title="Iniciar turno na {OS}"]'); time.sleep(.2)
        a.setv('#ft_ha', '10'); a.setv('#ft_h', '1'); sug = [J("document.querySelector('#ft_c%d').value" % i) for i in range(3)]
        a.setv('#ft_c0', '20'); a.setv('#ft_c1', '0'); a.setv('#ft_c2', '0'); a.clk('Fechar turno'); t = a.toast() or ''; b = a.body()
        DIVT = '2,4-D 806 planejado 10 L × informado 0 L; Óleo mineral planejado 5 L × informado 0 L'
        a.ok(r == 'ok' and sug == ['20', '10', '5'] and f'{SELO}: {DIVT} · revisão técnica de Ana (agrônoma).' in t,
             f'MB-03: sugestão 20/10/5; informado 20/0/0 fecha o turno e o aviso diz a divergência e quem revisa: {sug} · {t[:220]}')
        i = b.find('Turno fechado ·'); rb = b[i:i + 500]
        a.ok(SELO in rb and f'{DIVT} · revisão técnica de Ana (agrônoma)' in rb and 'S2' not in rb, 'recibo do turno no app: selo e planejado × informado com unidade, sem "S2": ' + rb.replace('\n', ' / ')[:300])
        a.ok(sem_rolagem(), 'app a 390 px sem rolagem horizontal')
        shot('dose_div_1_app_recibo.png'); guard()
        # 2 · O.S. (1440 px): selo na lista e no Kanban; painel com a linha do apontamento e a revisão (perfil Ana, agrônoma)
        web(); ln = linha(OS)
        a.ok(f'{SELO} · 2,4-D 806, Óleo mineral' in ln and 'Ana (agrônoma)' in ln and 'revisar a divergência de dose do dia 1' in ln,
             'lista: selo por produto, quem resolve Ana (agrônoma) e a próxima ação: ' + ln[:260])
        aba('Kanban'); kb = cartao(OS)
        a.ok(f'{SELO} · 2,4-D 806, Óleo mineral' in kb and 'Ana (agrônoma) · revisar a divergência de dose do dia 1' in kb, 'Kanban (5 fases, sem coluna nova): cartão com o selo e a pendência: ' + kb[:240])
        ncol = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] span')].filter(s=>getComputedStyle(s).textTransform==='uppercase').map(s=>s.innerText.trim().toLowerCase()).filter((x,i,l)=>l.indexOf(x)===i).join('|')")
        shot('dose_div_2_kanban.png'); aba('Lista')
        ordem(OS); p = pan()
        a.ok(f'{SELO} · {DIVT}' in p and temb('Aceitar com motivo') and temb('Registrar correção') and 'Pendência com Ana (agrônoma) · revisar a divergência de dose do dia 1' in p,
             'painel: linha do dia 1 com planejado × informado, Aceitar com motivo e Registrar correção (perfil Ana): ' + p[p.find('Dia 1'):][:300])
        shot('dose_div_3_painel.png'); guard()
        # 3 · recusa: perfil Rui (almoxarife) não vê a decisão e o comando direto é recusado; nada muda
        perfil('Rui'); web(); ordem(OS); p = pan()
        rx = cmd(f"W.cenDivRever(c,'{OS}',1,'aceitar','teste','Rui')")
        a.ok(not temb('Aceitar com motivo') and 'Revisão técnica pendente: decisão de Ana (agrônoma) (aceitar com motivo ou registrar a correção).' in p
             and rx == 'Revisar a divergência de consumo/dose do dia 1 da OS-0430: decisão de Ana (agrônoma). Nada foi alterado.' and a.cen(REV) == '',
             f'perfil Rui: sem os botões, a linha diz quem decide; comando direto recusado, nada gravado: {rx}')
        perfil('Ana'); web(); ordem(OS); pan()
        # 4 · erro: aceitar sem motivo → aviso junto ao campo, nada gravado
        btn('Aceitar com motivo'); al = alerta()
        a.ok('Informe o motivo para aceitar a divergência do dia 1 da OS-0430. Nada foi alterado.' in al and a.cen(REV) == '' and SELO in linha(OS),
             'aceitar sem motivo: erro junto ao campo, revisão continua pendente: ' + al[:160])
        # 5 · normal: motivo e Aceitar → selo sai, a linha mostra a revisão com autor; o consumo informado fica (2,4-D sem baixa)
        MOT = 'Calda sem 2,4-D por deriva no vizinho; controle conferido em campo'
        settx('Motivo ou correção decidida · dia 1', MOT); btn('Aceitar com motivo'); t = toast(); p = pan()
        cons = a.cen(f"c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.prod+' '+i.consumido).join(', ')")
        a.ok(f'aceita por Ana (agrônoma): {MOT}' in t and a.cen(REV) == '1:Aceita:Ana (agrônoma)' and SELO not in linha(OS)
             and re.search(r'Revisão técnica: aceita por Ana \(agrônoma\) às \d\d:\d\d · ' + re.escape(MOT), p) and not temb('Aceitar com motivo')
             and cons == 'Glifosato 480 20, 2,4-D 806 0, Óleo mineral 0',
             f'Ana aceita com motivo: selo sai da lista, a linha mostra quem e quando; consumo informado preservado ({cons}): ' + t[:160])
        # 6 · repetição: a mesma revisão de novo não grava; outra decisão no mesmo dia é conflito
        r1 = cmd(f"W.cenDivRever(c,'{OS}',1,'aceitar',{json.dumps(MOT)},'Ana')"); r2 = cmd(f"W.cenDivRever(c,'{OS}',1,'corrigir','Reaplicar','Ana')")
        a.ok('já revisada' in r1 and 'conflito' in r2 and a.cen(REV) == '1:Aceita:Ana (agrônoma)', f'repetição sem efeito; outra decisão é conflito: {r1[:90]} · {r2[:90]}')
        shot('dose_div_4_aceita.png'); guard()
        # 7 · conferência: o resto da área (150 ha) com Óleo abaixo do planejado; sobras devolvidas; enviada para conferência
        f = cmd(f"(W.cenIniciarTurno(c,'{OS}'), W.cenFecharTurno(c,150,8,{{'Glifosato 480':300,'2,4-D 806':150,'Óleo mineral':50}},'',[]))")
        dv = cmd(f"(c.reqs[c.ordens['{OS}'].req].itens.filter(i=>i.custodia>0).forEach(i=>W.cenDevolver(c,c.ordens['{OS}'].req,i.prod,i.custodia,true,'Rui')), W.osc_conferencia(c,'{OS}'))")
        a.ok('Óleo mineral planejado 75 L × informado 50 L' in f and dv == 'OS-0430 enviada para conferência.', f'turno de 150 ha com Óleo 50 L (75 L planejado) e envio para conferência: {f[-120:]} · {dv}')
        web(); ordem(OS); p = pan(); i = p.find('PRÓXIMO PASSO'); pp = p[i:i + 420]
        a.ok(f'{SELO} · Óleo mineral' in p and 'Encerrar bloqueado: divergência de consumo/dose em revisão técnica · dia 2 · Óleo mineral planejado 75 L × informado 50 L.' in pp
             and 'Quem resolve: Ana (agrônoma), na linha do apontamento' in pp and not temb('Conferir e encerrar'),
             'Em conferência: selo e encerramento bloqueado com quem resolve; sem "Conferir e encerrar": ' + pp[:300])
        aba('Kanban'); kb = cartao(OS)
        a.ok(f'{SELO} · Óleo mineral' in kb and 'Ana (agrônoma) · revisar a divergência de dose' in kb and 'Sobras a receber' not in kb, 'Kanban em conferência: selo e pendência com Ana, sem "Sobras a receber": ' + kb[:220])
        shot('dose_div_5_conferencia.png'); aba('Lista'); guard()
        # 8 · 390 px: a revisão cabe e funciona (Registrar correção); depois o encerramento passa
        web(390); ordem(OS); pan()
        settx('Motivo ou correção decidida · dia 2', 'Reaplicar Óleo mineral 0,5 L/ha nos 50 ha do fim do talhão em nova O.S.'); btn('Registrar correção'); t = toast()
        a.ok('Correção registrada por Ana (agrônoma) para o dia 2 da OS-0430' in t and a.cen(REV) == '1:Aceita:Ana (agrônoma),2:Correção decidida:Ana (agrônoma)' and sem_rolagem(),
             '390 px: Registrar correção grava a decisão, sem rolagem horizontal: ' + t[:160])
        shot('dose_div_6_390_correcao.png')
        ok_enc = btn('Conferir e encerrar') and btn('Confirmar encerramento'); et = a.cen(f"c.ordens['{OS}'].etapa")
        a.ok(ok_enc and et == 'Encerradas', f'revisões feitas: Conferir e encerrar → Encerradas ({et})')
        guard()
        a.ok(not erros and ncol == 'a liberar|liberadas|em execução|em conferência|encerradas', f'sem erros JS (O.S., app) e Kanban com as 5 fases, sem coluna nova: {erros} · {ncol}')
        # 9 · revisão DOM achado 6: turno retido como duplicidade (mesma data do apontamento da web) → o recibo do app diz que a revisão só abre
        #     se o turno somar; guardado como duplicidade por Paula, a linha do dia não mostra divergência nem promete revisão
        a.c.size(390, 1800); a.abrir('MB-01'); a.clk('Restaurar demonstração'); time.sleep(.3); web()
        p0 = cmd(f"(W.osc_liberar(c,'{OS}',false,'','Ana'), c.reqs[c.ordens['{OS}'].req].itens.forEach(i=>W.cenEntregar(c,c.ordens['{OS}'].req,i.prod,i.solicitado,'Marcos','Rui')), W.cenConfirmarRecebimento(c,c.ordens['{OS}'].req), W.cenIniciarTurno(c,'{OS}'), c.app.turno=null, W.osc_apontar(c,'{OS}','26/09',10,{{'Glifosato 480':20,'2,4-D 806':10,'Óleo mineral':5}},[],'W-DUP'))")
        a.c.size(390, 1800); a.abrir('MB-03'); r = a.clk_sel(f'main button[title="Iniciar turno na {OS}"]'); time.sleep(.2)
        a.setv('#ft_ha', '10'); a.setv('#ft_h', '1'); a.setv('#ft_c0', '20'); a.setv('#ft_c1', '0'); a.setv('#ft_c2', '5'); a.clk('Fechar turno'); t = a.toast() or ''; b = a.body()
        i = b.find('Turno fechado ·'); rb = b[i:i + 600]
        a.ok(p0.startswith('Apontamento do dia 1') and r == 'ok' and 'em conferência' in t and 'Em conferência · duplicidade' in rb
             and '2,4-D 806 planejado 10 L × informado 0 L · a revisão técnica abre se Paula (conferência) somar o turno' in rb and 'revisão técnica de Ana' not in rb,
             'recibo do turno retido como duplicidade: a divergência fica registrada e a revisão só abre se Paula somar: ' + rb.replace('\n', ' / ')[:320])
        shot('dose_div_7_app_dup.png')
        web(); dd = cmd(f"W.osc_apDecidir(c,'{OS}',2,'anterior',null,'Paula')")   # o comando da O.S. (Paula, conferência)
        web(); ordem(OS); p = pan(); i = p.find('Dia 2'); l2 = p[i:p.find('Acumulado', i)] if i >= 0 else ''
        a.ok(dd.startswith('Dia 2 guardado como duplicidade') and 'Duplicidade · não somado' in l2 and SELO not in l2 and 'A revisão técnica abre quando o apontamento somar' not in l2 and SELO not in linha(OS),
             f'guardado como duplicidade ({dd[:60]}): a linha do dia 2 sem divergência nem promessa de revisão; lista sem selo: ' + l2[:240])
        shot('dose_div_8_dup_guardado.png'); guard()
        # 10 · DOM-REV-20261009-01 (S3): dois dias divergentes na mesma ordem, os dois motivos escritos; Ana confirma o dia 1 pelo teclado →
        #      só o dia 1 grava, o rascunho do dia 2 continua no campo e o foco vai para ele; depois o dia 2 confirma pelo teclado
        def tecla(k, code, vk, text=None):
            d = {'type': 'keyDown', 'key': k, 'code': code, 'windowsVirtualKeyCode': vk}
            if text: d['text'] = text
            a.c.call('Input.dispatchKeyEvent', d); a.c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': k, 'code': code, 'windowsVirtualKeyCode': vk}); time.sleep(.12)
        def escrever(fid, txt):   # foco no campo, digita (insertText) e sai com Tab, como quem usa o teclado
            J(f"document.getElementById({json.dumps(fid)}).focus()"); a.c.call('Input.insertText', {'text': txt}); time.sleep(.15); tecla('Tab', 'Tab', 9)
        def val(fid): return J(f"(()=>{{const e=document.getElementById({json.dumps(fid)}); return e?e.value:null;}})()")
        def ativo(): return J("(()=>{const e=document.activeElement; return e?(e.id||e.innerText||e.tagName).trim():'';})()") or ''
        a.c.size(390, 1800); a.abrir('MB-01'); a.clk('Restaurar demonstração'); time.sleep(.3); web()
        p0 = cmd(f"(W.osc_liberar(c,'{OS}',false,'','Ana'), c.reqs[c.ordens['{OS}'].req].itens.forEach(i=>W.cenEntregar(c,c.ordens['{OS}'].req,i.prod,i.solicitado,'Marcos','Rui')), W.cenConfirmarRecebimento(c,c.ordens['{OS}'].req), W.cenIniciarTurno(c,'{OS}'), c.app.turno=null, "
                 f"W.osc_apontar(c,'{OS}','25/09',10,{{'Glifosato 480':20,'2,4-D 806':0,'Óleo mineral':5}},[],'W-RASC-1'), W.osc_apontar(c,'{OS}','26/09',10,{{'Glifosato 480':20,'2,4-D 806':10,'Óleo mineral':0}},[],'W-RASC-2'))")
        perfil('Ana'); web(); ordem(OS); pan()
        T1 = 'Calda sem 2,4-D no dia 1: deriva no vizinho, controle conferido'; T2 = 'Reaplicar Óleo mineral 0,5 L/ha nos 10 ha do dia 2 em nova O.S.'
        escrever('dv_2', T2); escrever('dv_1', T1); foco1 = ativo()
        tecla('Enter', 'Enter', 13, '\r'); time.sleep(.5); t = toast(); pan(); f2 = ativo(); v2 = val('dv_2')
        a.ok(p0.startswith('Apontamento do dia 2') and foco1 == 'Aceitar com motivo' and f'aceita por Ana (agrônoma): {T1}' in t and a.cen(REV) == '1:Aceita:Ana (agrônoma)'
             and v2 == T2 and val('dv_1') is None and f2 == 'dv_2',
             f'dois dias divergentes: Enter em "Aceitar com motivo" do dia 1 grava só o dia 1; o texto do dia 2 fica ({v2!r}) e o foco vai para ele ({foco1} → {f2}): {p0[:40]} · ' + t[:120])
        tecla('Tab', 'Tab', 9); tecla('Tab', 'Tab', 9); fco = ativo(); tecla('Enter', 'Enter', 13, '\r'); time.sleep(.5); t = toast()
        a.ok(fco == 'Registrar correção' and a.cen(REV) == '1:Aceita:Ana (agrônoma),2:Correção decidida:Ana (agrônoma)' and f'Correção registrada por Ana (agrônoma) para o dia 2 da OS-0430: {T2}' in t,
             f'dia 2 pelo teclado (Tab até "Registrar correção" e Enter) grava o rascunho preservado, só a decisão confirmada: {fco} · ' + t[:160])
        shot('dose_div_9_dois_dias.png'); guard()
        a.c.size(390, 1800); a.abrir('MB-01'); a.clk('Restaurar demonstração')
    finally:
        a.fim()
    return 1 if a.FAIL else 0
