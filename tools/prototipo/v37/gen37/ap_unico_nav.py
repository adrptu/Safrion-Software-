# -*- coding: utf-8 -*-
"""CTL-2 · Frente A (AP-ÚNICO), parte de navegador do ap_unico_test.py: O.S. (1440 px), app MB-03 (390 px) e Estoque sobre o mesmo cenário.
Uso: python3 ap_unico_test.py nav   (compile antes: build.py && montar_render.py)"""
import json, re, time
from app_lib import App

OS, P = 'OS-0421', 'Fungicida A'
FA = "c.reqs['REQ-035'].itens[0]"
FATO = f"[c.ordens['{OS}'].realizado,{FA}.consumido,{FA}.custodia]"

def rodar():
    a = App(['MB-01', 'MB-03', 'OS', 'EST']); J = a.J; erros = []
    def web():
        a.c.size(1440, 1100); a.abrir('OS'); time.sleep(.3)
    def ordem(id_):
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r&&r.click();}})()"); time.sleep(.45)
    def pan():
        if J('(()=>{const bs=[...document.querySelectorAll(\'aside[role=dialog] section[aria-label] > button[aria-expanded="false"]\')]; bs.forEach(b=>b.click()); return bs.length;})()'): time.sleep(.3)
        return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    def btn(t):
        r = J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.4); return r
    def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
    def temb_ini(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim().startsWith({json.dumps(t)}))"))
    def inp(lab): return J(f"(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)}); return i?i.value:null;}})()")
    def setin(lab, val):
        J(f"""(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)});
          Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
    def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def linha(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    def restaurar():
        a.c.size(390, 1800); a.abrir('MB-01'); a.clk('Restaurar demonstração'); time.sleep(.3)
    def web_apontar(ha, usado=None, data=None):
        web(); ordem(OS); btn('Registrar apontamento')
        if data: setin('Data do turno', data)
        setin('Área feita em hectares', ha)
        if usado is not None: setin(f'Usado de {P} (L)', usado)
        btn('Salvar apontamento'); return toast()
    def app_turno(ha, usado=None):
        a.c.size(390, 1800); a.abrir('MB-03'); a.clk_sel(f'main button[title="Iniciar turno na {OS}"]'); time.sleep(.2)
        a.setv('#ft_ha', ha); a.setv('#ft_h', '8')
        if usado is not None: a.setv('#ft_c0', usado)
        a.clk('Fechar turno'); return a.toast() or ''
    def cmd(js):   # comando direto no cenário da página (window.__cen), como um reenvio do mesmo formulário ou outro canal
        return J("(()=>{const W=window.__cen; const r=W.cenMudar(null,c=>" + js + "); return r.erro||r.msg||'';})()") or ''
    def guard():
        e = a.erros() or []; erros.extend(e)
    try:
        restaurar()
        # 1 · formulário: data operacional, operador herdado, consumo por insumo (Fungicida A sugerido; Adjuvante fora da REQ-035 vazio), sem aviso
        web(); ordem(OS); n0 = 1; btn('Registrar apontamento'); p = pan()
        vals = [inp('Data do turno'), inp(f'Usado de {P} (L)'), inp('Usado de Adjuvante espalhante (L)')]
        a.ok(inp('Data do turno') == '2026-09-26' and 'Turno de Marcos · quem está com os insumos' in p and inp(f'Usado de {P} (L)') == '25'
             and inp('Usado de Adjuvante espalhante (L)') == '' and 'Fora da REQ-035 · nada em custódia' in p and 'Já há' not in p,
             'AP-01/02/04 formulário: 26/09, "Turno de Marcos · quem está com os insumos", usado de Fungicida A 25 L sugerido, adjuvante vazio, sem aviso: ' + str(vals) + ' · ' + p[p.find('Data do turno'):][:200])
        # 2 · usado real 27 L e duplo clique em Salvar: 240 ha, 122 L / 38 L, uma só chave (2 cliques: Registrar + Salvar)
        setin(f'Usado de {P} (L)', '27')
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar apontamento'); b.click(); b.click();})()"); time.sleep(.5)
        f = a.cen(FATO); nw = a.cen(f"c.ordens['{OS}'].ap.filter(x=>/^W-/.test(x.chave||'')).length")
        a.ok(f == [240, 122, 38] and nw == 1, f'AP-03/04 usado 27 L e duplo clique: 240 ha, 122 L / 38 L, um só registro: {f} · {nw}')
        # a chave gravada é a do formulário aberto (não a reserva "-dia5"); reenviar o mesmo conteúdo com ela não soma; outro conteúdo é conflito (ENG-021)
        ch = a.cen(f"c.ordens['{OS}'].ap.find(x=>x.dia===5).chave") or ''
        r1 = cmd(f"W.osc_apontar(c,'{OS}','26/09',50,{{'{P}':27,'Adjuvante espalhante':0}},['Adjuvante espalhante'],{json.dumps(ch)})")
        r2 = cmd(f"W.osc_apontar(c,'{OS}','26/09',50,{{'{P}':30,'Adjuvante espalhante':0}},['Adjuvante espalhante'],{json.dumps(ch)})")
        a.ok(bool(re.match(r'^W-OS-0421-\d{13}$', ch)) and 'já registrado' in r1 and 'com outro conteúdo: conflito' in r2 and a.cen(FATO) == [240, 122, 38],
             f'ENG-021 chave do formulário {ch}: reenvio igual "já registrado", outro consumo = conflito, 240 ha / 122 L: {r1[:70]} · {r2[:90]}')
        mv = a.cen("c.movs.filter(m=>m.tipo==='consumo'&&m.origem==='web').map(m=>m.quem+'|'+m.det)")
        a.ok(mv == ['Marcos|Fungicida A 27'], f'a web grava o movimento de consumo com Marcos (não "web"): {mv}')
        # 3 · turno do app no mesmo dia: retido, recibo diz quem decide; o formulário web passa a avisar
        t = app_turno('50'); card = a.body()
        a.ok('em conferência: já há dia 5, 50 ha pela web em 26/09. Nada foi somado nem baixado; Paula (conferência) decide se é outro turno.' in t
             and 'Em conferência · duplicidade' in card and 'nada baixado: Paula (conferência) decide se é outro turno' in card and a.cen(FATO) == [240, 122, 38],
             'AP-05/06 app retido: recibo "Em conferência · duplicidade", nada baixado (240 ha, 122 L): ' + t[:160])
        guard(); web(); ordem(OS); btn('Registrar apontamento'); p = pan()
        a.ok('Já há dia 5, 50 ha pela web' in p and 'em 26/09. Se for outro turno, salve' in p, 'aviso no formulário antes de salvar (sem clique): ' + p[p.find('Já há'):][:160])
        btn('Cancelar')
        # 4 · painel: selo, pendência com Paula, linha não somada com as três saídas, acumulado 240 (não 290)
        # CTL-3 (ATOR): as três saídas são de quem confere; com o perfil Ana (padrão) a linha só diz quem decide; com o perfil Paula, elas aparecem
        p = pan(); semAna = not temb('Outro turno: somar') and not temb('Mesmo turno: vale o dia 5') and 'Quem decide: Paula (conferência).' in p
        a.ok(semAna, 'CTL-3: perfil Ana não vê as três saídas da duplicidade; a linha diz "Quem decide: Paula (conferência).": ' + p[p.find('Dia 6'):][:220])
        J("(()=>{const i=document.querySelector('[aria-label=\"Trocar perfil de demonstração\"]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'Paula'); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
        p = pan()
        a.ok('Apontamento em conferência' in p and 'Paula (conferência)' in p and 'decidir se o dia 6 é outro turno' in p and 'não somado' in p
             and temb('Mesmo turno: vale o dia 5') and temb('Mesmo turno: vale este') and temb('Outro turno: somar') and '240 / 350' in p and '290 / 350' not in p
             and 'Apontamento em conferência' in linha(OS),
             'AP-06/07 painel: selo na lista e no painel, Paula decide, três saídas, acumulado 240/350: ' + p[p.find('APONTAMENTOS'):][:400])
        # 5 · "Mesmo turno: vale o dia 5" (1 clique): dia 6 guardado, selo sai, 240 ha
        btn('Mesmo turno: vale o dia 5'); p = pan(); s6 = a.cen(f"c.ordens['{OS}'].ap.find(x=>x.dia===6).st")
        a.ok(s6 == 'Duplicidade · não somado' and 'Apontamento em conferência' not in p and a.cen(FATO) == [240, 122, 38] and 'Dia 6 guardado como duplicidade do dia 5' in toast(),
             f'AP-07 "vale o dia 5": dia 6 = {s6}, selo fora, 240 ha / 122 L')
        guard()
        # 6 · "Mesmo turno: vale este": web 50 ha (estimativa 25 L) e app 50 ha com 27 L reais → 240 ha, 122 L; dia 5 estornado e guardado
        restaurar(); web_apontar('50'); app_turno('50', '27'); web(); ordem(OS); pan(); btn('Mesmo turno: vale este'); time.sleep(.2)
        f = a.cen(FATO); m5 = a.cen(f"(()=>{{const k=c.ordens['{OS}'].ap.find(x=>x.dia===5); const m=c.movs.find(x=>x.id===k.mov); return [k.st,m.det,m.obs||'']}})()")
        a.ok(f == [240, 122, 38] and m5[0] == 'Duplicidade · não somado' and m5[1] == '' and m5[2].startswith('Estornado: mesmo turno do dia 6'),
             f'AP-07 "vale este" (DEMO-11): 240 ha, 122 L / 38 L; dia 5 estornado, movimento sem item: {f} · {m5}')
        mid = a.cen(f"c.ordens['{OS}'].ap.find(x=>x.dia===5).mov")
        a.c.size(1440, 1100); a.abrir('EST'); J("document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[5].click()"); time.sleep(.5)
        row = J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(mid)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
        a.ok(bool(mid) and 'Consumo apontado na web' in row and ' Web ' in row + ' ' and P not in row and '25 L' not in row,
             f'EST · movimentos: o consumo estornado do dia 5 ({mid}) é "Consumo apontado na web", origem Web, sem item nem quantidade: {row}')
        guard()
        # 7 · "Outro turno: somar": web 40 ha + app 50 ha → 280 ha, 140 L
        restaurar(); web_apontar('40'); app_turno('50'); web(); ordem(OS); pan(); btn('Outro turno: somar'); f = a.cen(FATO)
        a.ok(f[:2] == [280, 140], f'AP-07 "outro turno: somar": 280 ha, 140 L: {f}')
        guard()
        # 8 · sem sinal: app 50 ha no aparelho, web 50 ha, sinal volta → 240 ha, 120 L; movimento retido sem item
        restaurar(); a.abrir('MB-03'); a.clk('Sem sinal'); app_turno('50'); web_apontar('50'); a.c.size(390, 1800); a.abrir('MB-03'); a.clk('Com sinal'); t = a.toast() or ''
        f = a.cen(FATO); md = a.cen(f"(()=>{{const k=c.ordens['{OS}'].ap.find(x=>x.st==='Duplicidade a conferir'); const m=k&&c.movs.find(x=>x.id===k.mov); return k?[k.dia,m?m.det:null,m?m.obs:null]:null}})()")
        a.ok(f == [240, 120, 40] and md and md[1] == '' and 'Em conferência de duplicidade: OS-0421 dia 5' in t,
             f'AP-06 sem sinal + web: 240 ha, 120 L / 40 L; o turno do app fica retido, baixa desfeita, movimento sem item: {f} · {md} · {t[:120]}')
        guard()
        # 9 · retido até Em conferência: a pendência é de Paula (decidir a duplicidade), não de Rui
        restaurar(); a.mudar("return cenEntregar(c,'REQ-035','Fungicida A',15,'Marcos','Rui');"); web_apontar('50'); app_turno('50'); web_apontar('110', data='2026-09-27')
        web(); ordem(OS); btn('Enviar para conferência'); btn('Confirmar envio'); p = pan(); ln = linha(OS)
        a.ok('Em conferência' in ln and 'Apontamento em conferência' in ln and 'Rui (almoxarife)' not in ln and 'Sobras a receber' not in ln and 'receber a devolução' not in p
             and 'Encerrar bloqueado: Apontamento em conferência de duplicidade: dia 6' in p and 'Quem resolve: Paula (conferência) decide na linha do apontamento' in p,
             'AP-08 Em conferência com retido: selo "Apontamento em conferência" na lista (não "Sobras a receber"/Rui) e o painel bloqueia o encerramento com Paula (dono Paula: unit C1): ' + ln[:200] + ' · ' + p[p.find('PRÓXIMO'):][:200])
        guard()
        # 10 · negativo: dois turnos do app no mesmo dia (mesmo operador) somam: 230 ha
        restaurar(); app_turno('20'); app_turno('20'); f = a.cen(FATO)
        a.ok(f[0] == 230 and a.cen(f"c.ordens['{OS}'].ap.some(x=>x.st==='Duplicidade a conferir')") is False, f'negativo: dois turnos do app somam (230 ha), nada retido: {f}')
        guard()
        # 12 · S2 (revisão 2): "Outro turno: somar" desconta a área no aparelho; com o sinal o realizado não passa da área (310 ≤ 350)
        restaurar(); web_apontar('50', data='2026-09-27'); web_apontar('50', data='2026-09-27')
        a.c.size(390, 1800); a.abrir('MB-03'); a.clk('Sem sinal'); app_turno('70', '35')
        web(); ordem(OS); pan(); btn('Outro turno: somar'); t = toast(); a.c.size(390, 1800); a.abrir('MB-03'); a.clk('Com sinal')
        f = a.cen(f"[c.ordens['{OS}'].realizado,c.ordens['{OS}'].saldo,c.ordens['{OS}'].area,c.ordens['{OS}'].ap.find(x=>x.dia===6).st]")
        a.ok('Somar 50 ha passa do saldo da ordem (40 ha, descontando 70 ha ainda no aparelho)' in t and f == [310, 40, 350, 'Duplicidade a conferir'],
             f'S2 somar com área no aparelho recusado; depois do sinal 310/350 ha, dia 6 segue retido: {f} · {t[:140]}')
        guard()
        # 13 · app: o caso do turno retido fica "Aguarda a decisão da duplicidade" e conta como aberto no cartão (não "Conferência resolvida")
        restaurar(); a.abrir('MB-03'); a.clk('Sem sinal'); app_turno('2', '70')
        cmd("W.cenApontar(c,{os:'OS-0421',d:'26/09',ha:2,origem:'web',chave:'W-nav-13'})"); a.clk('Com sinal'); time.sleep(.3)
        b = a.body(); card = b[b.find('Turno fechado ·'):][:420].replace('\n', ' | ')
        a.ok('Em conferência · duplicidade' in card and 'Consumo em conferência' in card and 'Aguarda a decisão da duplicidade · Fungicida A 70 L relatados' in card and 'Conferência resolvida' not in card,
             'app: turno retido com consumo em conferência fica aberto no cartão: ' + card[:260])
        guard()
        # 14 · S3 (revisão 2): com o dia 5 estornado por "vale este" no dia 6, o dia 7 só oferece "Outro turno: somar"
        restaurar(); web_apontar('50'); a.c.size(390, 1800); a.abrir('MB-03'); a.clk('Sem sinal'); app_turno('25'); app_turno('25'); a.abrir('MB-03'); a.clk('Com sinal')
        web(); ordem(OS); pan(); btn('Mesmo turno: vale este'); p = pan()
        a.ok('O dia 5 já não vale: este só pode ser somado como outro turno' in p and not temb_ini('Mesmo turno') and temb('Outro turno: somar'),
             'dia 7 depois do estorno do dia 5: só "somar", com a causa: ' + p[p.find('Dia 7'):][:200])
        btn('Outro turno: somar'); f = a.cen(FATO)
        a.ok(f == [240, 120, 40], f'dia 7 somado: 25 + 25 ha do app no lugar dos 50 ha da web: 240 ha, 120 L / 40 L: {f}')
        guard()
        # 15 · S3 (revisão 2): estimativa acima da custódia na decisão pede o usado na linha (AP-04); com 8 L informado, soma e baixa 8 L
        restaurar(); web_apontar('50'); web_apontar('40'); web_apontar('60', usado='30', data='2026-09-27')
        web(); ordem(OS); p = pan(); btn('Outro turno: somar'); t = toast(); f0 = a.cen(FATO)
        a.ok('Estimativa 20 L passa da custódia (10 L): informe o usado com Marcos' in p and 'Informe o usado (com Marcos) e decida de novo' in t and f0 == [300, 150, 10],
             f'linha do dia 6 pede o usado; "somar" sem ele é recusado, nada muda: {f0} · {t[:140]}')
        setin(f'Usado de {P} (L)', '8'); btn('Outro turno: somar'); f = a.cen(FATO)
        a.ok(f == [340, 158, 2], f'com 8 L informado: 340 ha, 158 L consumidos, 2 L em custódia: {f}')
        guard()
        # 16 · S2 (revisão 2): consumo do dia 5 já aceito → a linha do retido não oferece "vale este" e diz por quê e por quem
        # CTL-3 (padrão 2): os 5 L acima da custódia saem do lote: aceite da gestora, e a linha nomeia quem aceitou de fato
        restaurar(); web_apontar('50', usado='70'); a.c.size(390, 1800); a.abrir('MB-01'); ac = cmd("W.cenConciliar(c,'CC-301',true,undefined,'Ana')")
        web_apontar('50', usado='27'); web(); ordem(OS); p = pan()
        a.ok('aceito' in ac and '"Vale este" indisponível: consumo já aceito por Ana (gestora) (CC-301).' in p and not temb('Mesmo turno: vale este')
             and temb('Mesmo turno: vale o dia 5') and temb('Outro turno: somar') and a.cen(FATO) == [240, 165, 0],
             f'linha do dia 6 sem "vale este" depois do aceite do CC-301 (240 ha, 165 L): {ac[:60]} · ' + p[p.find('Dia 6'):][:220])
        guard()
        # 11 · sem erros JS
        a.ok(not erros, 'sem erros JS em OS, MB-01, MB-03 e EST: ' + str(erros[:3]))
        restaurar()
    finally:
        a.fim()
    print(f'RESULTADO nav: {a.n - len(a.FAIL)}/{a.n}' + (' · FALHAS: ' + '; '.join(a.FAIL) if a.FAIL else ''))
    return 1 if a.FAIL else 0
