# -*- coding: utf-8 -*-
"""PCM simplificado · revisão adversarial de 09/10 na tela MA (Chrome, 1440 px): a proteção de regressão de navegador de cada achado
corrigido que tem efeito na tela. As regras estão em ma_regras_test.py (ma_regras_unit.js e ma_os_unit.js) e o app em ma_app_test.py.
- A1 (S1): "Registrar e bloquear" no Trator T1 já bloqueado acrescenta o motivo; a OM-0233 diz que encerra só o motivo dela e o T1 segue bloqueado;
- A2 (S2): repetição mais grave: "Somar ao INSP-104 e bloquear" (quem tem a competência), com o aviso de que a nova é mais grave;
- A6 (S3): "Gerar N" conta e gera só o que a grade Sem ordem mostra (busca);
- A8 (S3): Ver como João (eletricista NR-10) executa a OM-0228 e declara a Bomba do Pivô 2 apta;
- A10 (S3): o comboio mostra o consumo em km/L na célula (coluna "Consumo");
- A11 (S3): o painel da OM confere a versão lida (o.rv): mudou em outra aba → "Mudou desde que você abriu"; o toque seguinte confirma;
- F22/AC-PCM-23 (S4): o painel Vínculo sugere o marco da última OM encerrada do mesmo serviço (antes só conferido no HTML).
Uso (de gen37/, depois de build.py e montar_render.py): python3 ma_revisao_test.py"""
import sys, json, time
from ma_lib import MA

m = MA(1440, 1000); J = m.J
PRIMS_PAN = "[...document.querySelectorAll('#ma-painel button,#ma-painel a')].filter(e=>e.getClientRects().length&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>e.innerText.replace(/\\s+/g,' ').trim())"
def man_js(js): return J(f"(()=>{{ const r=window.__man.manMudar(null,(m)=>{{ {js} }}); return r.erro||''; }})()")
try:
    # ---------- A1 · segundo motivo de bloqueio no Trator T1 ----------
    m.ir('ativo=a01', perfil='Zé', limpa=True); m.sem_erro('MA #ativo=a01')
    m.clk('Registrar achado'); m.clk('Inspeção', '#ma-painel'); m.clk('Rodado e freios', '#ma-painel'); m.setv('#na-sint', 'Freio de serviço sem ação no pedal')
    m.clk('Alta', '#ma-painel'); m.clk('Bloqueado', '#ma-painel'); p1 = J(PRIMS_PAN)
    m.clk('Registrar e bloquear', '#ma-painel'); t = m.toast()
    nm = m.man("(m.ativos.a01.condInfo.mais||[]).length"); aid = m.man("(m.ativos.a01.condInfo.mais||[{}])[0].achado")
    m.ok(p1 == ['Registrar e bloquear'] and nm == 1 and aid == 'INSP-106' and 'segue bloqueado · motivo acrescentado (2 motivos)' in t,
         'A1 · "Registrar e bloquear" no T1 já bloqueado acrescenta o INSP-106 como 2º motivo e diz "segue bloqueado"', [p1, nm, aid, t[:200]])
    m.ir('ativo=a01'); m.bloco('Situação'); b = J("document.querySelector('main').innerText") or ''
    m.ok('2 motivos' in b and 'MOTIVO 2' in b.upper() and 'INSP-106 · sem ordem' in b, 'A1 · o detalhe do T1 lista os 2 motivos, cada um com achado e ordem', b[b.find('Situação'):][:700])
    m.ir('om=OM-0233', perfil='Zé'); m.clk('Aprovado', '#ma-painel'); m.clk('Anexar foto e registrar Aprovado', '#ma-painel'); m.setv('#om-leitura', '4320')
    m.clk('Previsto (6,5 h)', '#ma-painel'); m.clk('Concluir serviço', '#ma-painel'); p2 = J(PRIMS_PAN)
    m.ok(p2 == ['Encerrar o motivo da OM-0233 · Trator T1 segue bloqueado'] and 'outros motivos: INSP-106 · sem ordem' in m.pan(),
         'A1 · em Em conferência a primária da OM-0233 diz que encerra só o motivo dela e o T1 segue bloqueado', [p2, m.pan()[:300]])
    m.clk('Encerrar o motivo da OM-0233 · Trator T1 segue bloqueado', '#ma-painel'); t = m.toast()
    m.ok(m.man("m.ativos.a01.cond") == 'Bloqueado' and 'Falta: INSP-106 · sem ordem' in (t + m.pan()) and m.man("m.oms['OM-0233'].aptidao.dec") == 'motivo',
         'A1 (S1) · o T1 segue Bloqueado pelo freio (Falta: INSP-106 · sem ordem); o app e as O.S. continuam vendo "bloqueado"', [m.man("m.ativos.a01.cond"), t[:200]])
    m.ir('ativo=a01', perfil='Otávio'); pa = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.getClientRects().length); return b?b.innerText.trim():'';})()")
    m.ok(pa == 'Criar ordem corretiva', 'A1 · o motivo sem ordem faz o detalhe do T1 pedir "Criar ordem corretiva"', pa)
    m.sem_erro('A1')
    # ---------- A2 · repetição mais grave: Somar e bloquear ----------
    m.ir('ativo=a02', perfil='Otávio', limpa=True)
    m.clk('Registrar achado'); m.clk('Relato', '#ma-painel'); m.clk('Hidráulico', '#ma-painel'); m.setv('#na-sint', 'Mangueira estourou, óleo no motor')
    m.clk('Alta', '#ma-painel'); m.clk('Bloqueado', '#ma-painel'); p = m.pan(); pr = J(PRIMS_PAN)
    m.ok(pr == ['Somar ao INSP-104 e bloquear'] and 'a nova é mais grave: somar eleva criticidade Média → Alta e sugestão Apto → Bloqueado' in p,
         'A2 · a repetição mais grave avisa e oferece "Somar ao INSP-104 e bloquear" como primária', [pr, p[:300]])
    m.clk('Somar ao INSP-104 e bloquear', '#ma-painel')
    m.ok(m.man("m.ativos.a02.cond") == 'Bloqueado' and m.man("m.achados['INSP-104'].crit") == 'Alta' and m.man("m.achados['INSP-104'].sug") == 'Bloqueado' and m.man("m.ativos.a02.condInfo.achado") == 'INSP-104',
         'A2 (S2) · somar leva a gravidade ao INSP-104 e bloqueia o Trator 02 com ele como motivo', [m.man("m.ativos.a02.cond"), m.man("m.achados['INSP-104'].crit")])
    m.sem_erro('A2')
    # ---------- A6 · "Gerar N" segue a busca da grade ----------
    m.ir('vis=semordem', perfil='Otávio', limpa=True); n0 = m.man("Object.keys(m.oms).length")
    m.setv('main .g2caixa input[type=search]', 'Trator 03'); time.sleep(.4); vis = m.linhas(0)
    hb = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>/^Gerar/.test(b.innerText.trim())); return b?b.innerText.trim():'';})()")
    J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>/^Gerar/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.6)
    novas = m.man("Object.keys(m.oms).length") - n0; nova_a = m.man("Object.values(m.oms).filter(o=>o.etapa==='A liberar'&&o.tipo==='Preventiva'&&!['OM-0234'].includes(o.id)).map(o=>o.aid)")
    m.ok(len(vis) == 1 and hb == 'Gerar 1 ordem preventiva' and novas == 1 and nova_a == ['a03'], 'A6 (S3) · com a busca "Trator 03", a primária é "Gerar 1 ordem preventiva" e gera só a do Trator 03', [vis, hb, novas, nova_a])
    # ---------- A8 · João executa a OM-0228 e declara a Bomba do Pivô 2 apta ----------
    m.ir('om=OM-0228', perfil='João', limpa=True); vc = J("(document.querySelector('select[aria-label=\"Trocar perfil de demonstração\"]')||{}).value")   # 14/10: o perfil é o do avatar (sem a faixa Ver como)
    pr = J(PRIMS_PAN); m.clk('Iniciar serviço', '#ma-painel'); m.bloco('Tarefas'); n = m.responder('Conforme')
    m.setv('#ma-painel input[aria-label^="Valor · Medir pressão"]', '3,4'); m.setv('#om-leitura', '8930'); m.clk('Previsto (3 h)', '#ma-painel'); m.clk('Concluir serviço', '#ma-painel')
    p3 = J(PRIMS_PAN); m.clk(p3[0] if p3 else 'Declarar', '#ma-painel')
    m.ok(vc == 'João' and pr == ['Iniciar serviço'] and n == 3 and m.man("m.oms['OM-0228'].etapa") == 'Em conferência' and (p3 or [''])[0].startswith('Declarar ') and m.man("m.ativos.a11.cond") == 'Apto' and 'João' in (m.man("m.oms['OM-0228'].aptidao.por") or ''),
         'A8 (S3) · Ver como João: inicia a OM-0228, mede conforme, conclui e declara a bomba apta (responsável técnico)', [vc, pr, n, m.man("m.oms['OM-0228'].etapa"), p3, m.man("m.ativos.a11.cond")])
    m.sem_erro('A8')
    # ---------- A10 · comboio em km/L na célula ----------
    m.ir('vis=ativos&modo=abastecimentos', perfil='Otávio', limpa=True)
    e1 = man_js("return window.__man.manAbastecer(m,{aid:'cb01',tq:'Sede · D-118',vol:'200',leit:'48.300',op:'Beto',cheio:true},'Otávio','t-c1');")
    e2 = man_js("return window.__man.manAbastecer(m,{aid:'cb01',tq:'Sede · D-118',vol:'60',leit:'48.500',op:'Beto',cheio:true},'Otávio','t-c2');")
    m.ir('vis=ativos&modo=abastecimentos'); ln = m.linha('AB-1044') or ''; hd = J("[...document.querySelectorAll('main [role=columnheader]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim())") or []
    m.ok(not e1 and not e2 and '3,3 km/L' in ln and 'L/h' not in ln and any(x.upper().startswith('CONSUMO') for x in hd) and not any('L/H' in x.upper() for x in hd), 'A10 (S3) · a linha do comboio mostra "3,3 km/L" (unidade na célula); a coluna é "Consumo"', [e1, e2, ln, hd])
    # ---------- A11 · versão do registro no painel da OM ----------
    m.ir('om=OM-0234', perfil='Otávio', limpa=True)
    e = man_js("const o=m.oms['OM-0234']; o.tempo=6; o.rv=(o.rv||0)+1; return {msg:''};")   # outra aba muda a OM depois que o painel abriu
    m.clk('Liberar mesmo assim', '#ma-painel'); t1 = m.toast(); f1 = m.man("m.oms['OM-0234'].etapa")
    m.clk('Liberar mesmo assim', '#ma-painel'); f2 = m.man("m.oms['OM-0234'].etapa")
    m.ok(not e and 'Mudou desde que você abriu: OM-0234' in t1 and f1 == 'A liberar' and f2 == 'Liberadas',
         'A11 (S3) · mudou em outra aba: o 1º toque é recusado ("Mudou desde que você abriu") e nada grava; o toque seguinte, já com o estado novo, libera', [e, t1[:160], f1, f2])
    m.sem_erro('A11')
    # ---------- F22 / AC-PCM-23 · marco sugerido no painel Vínculo ----------
    m.ir('plano=PM-03', perfil='Otávio', limpa=True)
    e = man_js("delete m.vinc['PM-03|a04']; return {msg:''};"); m.ir('plano=PM-03')
    m.clk('Vincular ativo'); m.setv('#vk_aid', 'a04'); time.sleep(.3); vk = J("(document.querySelector('#vk-painel')||{}).innerText||''") or ''
    dv = J("(document.querySelector('#vk_data')||{}).value||''"); lv = J("(document.querySelector('#vk_leit')||{}).value||''")
    m.ok(not e and 'Marco da OM-0205' in vk and dv == '2026-06-02' and lv == '3300', 'F22 · Vincular o Trator 04 ao PM-03 sugere o marco da OM-0205 (02/06 · 3.300 h), corrigível com motivo', [e, vk[:240], dv, lv])
    m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
