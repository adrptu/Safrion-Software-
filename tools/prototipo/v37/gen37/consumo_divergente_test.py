# -*- coding: utf-8 -*-
"""Consumo relatado acima da custódia (RN-018; CONC-07; CONC-13; CMD-50; revisão QUALIDADE-ARTEFATO-20261003-FLUXO, caso 3) · Chrome real, ponta a ponta:
App MB-03 (390 px): a sugestão dose × área não editada acima da custódia não abre conferência (pede quanto foi usado); o valor informado grava o fato
Em conferência sem baixa nem custódia negativa · recibo e cartão do app mostram o caso e quem concilia · Estoque (#req=, painel do registro) mostra
relatado × custódia e, antes do toque, de onde sai cada litro (custódia, reserva da própria requisição) · o painel do lote mostra a exposição ·
SUP (06/10): a forma mudou (etapas → endereço e painel; recusa com motivo digitado; excedente aceito pela gestora); ficam os casos CC-301 e CC-302 ·
O.S. mostra o selo e não encerra com o caso aberto · aceitar regulariza uma vez e não deixa reserva própria acima da necessidade · recusar deixa o relato
sem efeito · sem sinal o caso só aparece depois do envio · recibo de caso resolvido abre com o estado (Aceito/Recusado).
Capturas em _probe/q_consumo_*.png. Uso: python3 consumo_divergente_test.py   (compile antes: build.py ou areas.mobile/processo_estoque)"""
import os, time
from app_lib import App

HERE = os.path.dirname(os.path.abspath(__file__))
a = App(['MB-01', 'MB-02det', 'MB-03', 'MB-05'])
OS, RQ, P = 'OS-0421', 'REQ-035', 'Fungicida A'
IT = f"c.reqs['{RQ}'].itens.find(i=>i.prod==='{P}')"
IT9 = f"c.reqs['REQ-039'].itens.find(i=>i.prod==='{P}')"
LOT = f"c.lotes['{P}|F26-02']"
ALR = "[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' | ')"
shot = lambda n: a.c.shot(os.path.join(HERE, '_probe', n))
def est(h='#sec=requisicoes'):
    a.c.size(1440, 1100); a.c.goto('about:blank', wait=.1); a.c.goto(f'http://127.0.0.1:{a.p}/EST.dc.html{h}', wait=1.2)
    a.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }"); time.sleep(.5)
def abrir_linha(*ts):
    r = a.J("(()=>{const ts=%s; const r=[...document.querySelectorAll('[role=row]')].find(r=>r.offsetParent&&ts.every(t=>r.innerText.indexOf(t)>=0)); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})()" % repr(list(ts)).replace("'", '"')); time.sleep(.5); return r
painel = lambda: a.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
def prim_painel():
    return a.J("(()=>{const x=document.querySelector('aside[role=dialog]'); if(!x) return ''; const b=[...x.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); return b.length?b[b.length-1].innerText.trim():'';})()") or ''
def clk_prim():
    r = a.J("(()=>{const x=document.querySelector('aside[role=dialog]'); const b=[...x.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); if(!b.length) return 'sem primária'; b[b.length-1].click(); return 'ok';})()"); time.sleep(.6); return r
cnt1 = lambda: a.J("(()=>{const b=document.querySelector('nav[aria-label=\"Seções do estoque\"] button'); const s=b&&b.querySelector('.sec-cnt'); return s?s.innerText.trim():'';})()") or ''
def linha(*ts):
    return a.J("(()=>{const ts=%s; const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)); return r?r.innerText.replace(/\\s+/g,' '):'';})()" % repr(list(ts)).replace("'", '"')) or ''
campo = lambda i: a.J("document.querySelector('#ft_c%d').parentElement.innerText" % i).replace('\n', ' / ')
erros = []
def ok(cond, msg, extra=''): a.ok(cond, msg + ('' if cond or extra == '' else ' · ' + str(extra)[:300]))
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    # turno anterior (como o app faria): 128 ha e 64 L de Fungicida A → resta 1 L com Marcos
    a.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,128,8,{{'{P}':64,'Adjuvante espalhante':0}},'');")
    c0 = a.cen(f"[{IT}.custodia,{IT}.consumido,{IT}.entregue,{LOT}.fisico,c.ordens['{OS}'].ap.length]")
    # 0 · CONC-13: 4 ha × 0,5 L/ha = 2 L sugeridos (não editados) com 1 L em custódia → o campo pede quanto foi usado; nada é gravado nem aberto
    a.c.size(390, 1800); a.abrir('MB-03'); a.clk_sel(f'main button[title="Iniciar turno na {OS}"]'); a.setv('#ft_ha', '4'); a.setv('#ft_h', '1')
    w0 = campo(0); a.clk('Fechar turno'); e0 = a.J(ALR)
    s0 = a.cen(f"[!!c.app.turno,(c.confs||[]).length,c.ordens['{OS}'].ap.length,{IT}.custodia]")
    ok(a.J("document.querySelector('#ft_c0').value") == '2' and 'Sugestão acima do que está com você (1 L): informe quanto usou.' in w0
       and 'Informe quanto usou: a sugestão de 2 L passa do que está com você (1 L).' in e0 and s0 == [True, 0, c0[4], 1],
       f'MB-03: sugestão 2 L não editada acima de 1 L → pede o número real, turno aberto, nenhum caso aberto: {s0} · {e0[:90]}')
    shot('q_consumo_0_app_sugestao.png')
    # 1 · App: 2 ha, a sugestão é 1 L (dose 0,5 L/ha); o operador informa o real, 2 L → aviso no campo, sem bloqueio
    a.setv('#ft_ha', '2'); sug = a.J("document.querySelector('#ft_c0').value")
    a.setv('#ft_c0', '2'); av = campo(0)
    ok(sug == '1' and 'Acima do que está com você (1 L): fecha em conferência com Rui (almoxarife).' in av and a.J(ALR) == '',
         f'MB-03: sugestão 1 L (dose × área); o real 2 L informado avisa a conferência, sem erro: {av[-110:]}')
    shot('q_consumo_1_app_aviso.png')
    a.clk('Fechar turno'); b = a.body()
    cs = a.cen(f"(()=>{{const o=c.ordens['{OS}']; const ap=o.ap[o.ap.length-1]; const k=(c.confs||[])[0]||{{}};"
               f" return [{IT}.custodia,{IT}.consumido,o.ap.length,JSON.stringify(ap.cons),JSON.stringify(ap.conf||null),k.id,k.relatado,k.custodia,k.estado,k.resp,o.selos.map(s=>s.t).join(','),!!c.app.turno];}})()")
    ok(cs[0] == c0[0] == 1 and cs[1] == c0[1] and cs[2] == c0[4] + 1 and cs[3] == '{}' and cs[4] == '{"Fungicida A":2}' and not cs[11],
         f'fato gravado: 1 apontamento a mais, relatado 2 L em ap.conf (não trocado pela dose), custódia segue 1 L e consumido sem baixa: {cs[:5]}')
    ok(cs[5] == 'CC-301' and cs[6] == 2 and cs[7] == 1 and cs[8] == 'Em conferência' and cs[9] == 'Rui (almoxarife)' and 'Consumo em conferência' in cs[10] and a.J(ALR) == '',
         f'caso CC-301 Em conferência com relatado × custódia, dono Rui (almoxarife) e selo na O.S.; nenhum erro no app: {cs[5:11]}')
    ok('Turno fechado · OS-0421 · dia 6 · 2 ha em 1 h' in b and 'Consumo em conferência' in b and 'Consumo: nada baixado neste turno' in b
         and 'Em conferência · Fungicida A 2 L relatados, 1 L em custódia · Rui (almoxarife) confere; Ana (gestora) aceita o excedente' in b,
         'recibo do turno no app: selo Consumo em conferência, nada baixado, quem confere e quem aceita o excedente (revisão do CTL-3, achado 7)')
    shot('q_consumo_2_app_recibo.png')
    a.abrir('MB-01'); b = a.body(); i = b.find('OS-0421 ·')
    ok('em conferência · relatado 2 L · com você 1 L' in b[i:i + 600] and 'Devolver sobra' not in b, 'MB-01: cartão da OS-0421 mostra o consumo em conferência e não pede devolução do 1 L')
    erros += a.erros() or []
    # 2 · Estoque: o caso como linha filha da REQ-035 (relatado × custódia, quem decide); o painel mostra de onde sai cada litro antes do toque
    # SUP (06/10): a REQ-035 tem reserva própria (15 L): o litro além da custódia sai da reserva dela, não do livre (antes "(livre)")
    est(); lc = linha(P, 'consumo relatado'); k1 = cnt1()
    ok('CC-301' in lc and 'Aguardando gestora' in lc and k1.endswith('1 aguardando gestora'), f'EST: linha filha da REQ-035 "Aguardando gestora" (CC-301) e contador "{k1}"', lc[:200])
    abrir_linha(P, 'consumo relatado'); pn = painel()
    ok('Fungicida A 2 L relatados, 1 L em custódia' in pn and 'Baixa 2 L na OS-0421: 1 L da custódia de Marcos · 1 L sai do lote F26-02 (reserva da REQ-035).' in pn
       and prim_painel() == 'Aprovar consumo · 1 L além da custódia' and 'Recusar relato CC-301' in pn,
       f'painel do caso: relatado × custódia, de onde sai cada litro antes do toque; Ana vê "Aprovar consumo"; recusar é a alternativa: {pn[:260]}')
    shot('q_consumo_3_est_conferencia.png')
    est('#lote=F26-02'); l4 = painel()
    ok('= 465 L' in l4 and 'Exposição: 1 L em conferência (CC-301)' in l4, f'EST lote F26-02: disponível 465 L (545 − 80 reservados) e a exposição de 1 L em conferência: {l4[:200]}')
    shot('q_consumo_6_est_exposicao.png')
    erros += a.erros() or []
    # 3 · O.S.: selo na lista e encerrar bloqueado pelo caso aberto
    a.abrir('OS'); a.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0421')); r&&r.click();})()"); time.sleep(.5)
    lo = a.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0421')); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    pe = a.J("window.__cen.cenPodeEncerrar(window.__cen.cenGet(),'OS-0421')")
    pa = a.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    ok('Consumo em conferência' in lo and 'Consumo em conferência' in pa and pe.startswith('Consumo em conferência: Fungicida A 2 L relatados, 1 L em custódia. No Estoque: Rui (almoxarife) confere; Ana (gestora) aceita o excedente'),
         f'O.S.: selo na lista e no painel; encerrar bloqueado pelo caso ({pe[:80]})', lo[:200])
    shot('q_consumo_4_os_selo.png')
    erros += a.erros() or []
    # 4 · Estoque aceita: a prévia já está no painel (nada muda até o toque); o toque aplica uma vez; custódia 0, consumido +2, selo some
    # CTL-3 (padrão 2): o 1 L acima da custódia sai do lote; com o perfil Rui o painel diz quem aceita, Recusar continua, e o comando direto é recusado
    est(); a.setv('[aria-label="Trocar perfil de demonstração"]', 'Rui'); abrir_linha(P, 'consumo relatado'); pr = painel(); prr = prim_painel()
    rx = a.J("(()=>{const X=window.__cen; const r=X.cenMudar(null,c=>X.cenConciliar(c,'CC-301',true,undefined,{k:'Rui'})); return r.erro||r.msg;})()")
    ok('aceite de Ana (gestora)' in pr and prr == '' and 'Recusar relato CC-301' in pr and rx == 'Aceitar 1 L acima da custódia (CC-301): decisão de Ana (gestora). Nada foi alterado.'
       and a.cen(f"[{LOT}.fisico,c.confs[0].estado]") == [c0[3], 'Em conferência'], f'perfil Rui: o painel diz quem aceita, sem a primária; comando direto recusado, lote intacto: {rx} · {pr[-200:]}')
    a.setv('[aria-label="Trocar perfil de demonstração"]', 'Ana')
    est(); abrir_linha(P, 'consumo relatado'); cp = a.cen(f"[{LOT}.fisico,c.confs[0].estado,{IT}.custodia]")
    a.clk('Cancelar', 'aside[role=dialog]'); cv = a.cen(f"[{LOT}.fisico,c.confs[0].estado,{IT}.custodia]")
    ok(cp == [c0[3], 'Em conferência', 1] and cv == cp, f'abrir e fechar o painel não muda nada (a prévia não grava): {cp}')
    shot('q_consumo_7_est_previa.png')
    abrir_linha(P, 'consumo relatado'); r = clk_prim(); t = a.toast()
    ca = a.cen(f"[{IT}.custodia,{IT}.consumido,{IT}.entregue,{LOT}.fisico,c.confs[0].estado,c.ordens['{OS}'].selos.map(s=>s.t).join(','),window.__cen.cenPodeEncerrar(c,'{OS}'),{LOT}.reservado]")
    ok(r == 'ok' and 'CC-301 aceito: Fungicida A 2 L baixados na OS-0421 · 1 L regularizado do lote F26-02 (reserva da REQ-035).' in t and ca[0] == 0 and ca[1] == c0[1] + 2 and ca[2] == c0[2] + 1
         and ca[3] == c0[3] - 1 and ca[4] == 'Aceito' and 'Consumo em conferência' not in ca[5] and ca[7] == 79,
         f'aceite: custódia 0, consumido +2, entregue +1, lote −1 L da reserva da REQ-035 (80 → 79; os 65 L da REQ-039 intactos), caso Aceito e selo fora: {ca[:5]} · {ca[7]} · {t[:120]}')
    rr = a.mudar("return window.__cen.cenConciliar(c,'CC-301',true);"); rep = a.cen(f"[{IT}.consumido,{LOT}.fisico]")
    ok(rep == [ca[1], ca[3]] and rr == 'Este consumo não está em conferência.', f'aceitar de novo é recusado e não baixa outra vez: {rep} · {rr}')
    shot('q_consumo_5_est_aceito.png')
    erros += a.erros() or []
    # 5 · fora da requisição (Adjuvante, nada com o operador) e recusa: relato sem efeito, nenhum relato apagado
    # CTL-2 · B: com custódia 0 o app recusa iniciar (regra única da web); o relato fora da requisição continua possível num turno aberto antes
    a.c.size(390, 1800); a.abrir('MB-03'); rx = a.mudar(f"return cenIniciarTurno(c,'{OS}');")
    ok(rx == 'Iniciar bloqueado: REQ-035 sem entrega · Fungicida A 14 L a entregar. Rui (almoxarife) entrega no Estoque; Marcos confirma o recebimento no app.' and a.cen("!c.app.turno"),
       f'custódia 0: o app recusa iniciar com o texto da web e o dono, sem abrir turno: {rx}')
    a.mudar(f"c.app.turno={{os:'{OS}',ini:'10:00',pausas:[],fim:null}}; return 'turno aberto antes';"); a.abrir('MB-03')   # como app_saldo_zero_test.py
    a.setv('#ft_ha', '2'); a.setv('#ft_h', '1'); a.setv('#ft_c0', '0'); a.setv('#ft_c1', '0,5')
    av1 = campo(1); a.clk('Fechar turno')
    k2 = a.cen("(c.confs||[]).map(k=>k.id+' '+k.prod+' '+k.relatado+' '+k.custodia+' '+k.estado+' '+k.motivo)")
    ok('Acima do que está com você (0 L): fecha em conferência' in av1 and len(k2) == 2 and k2[1] == 'CC-302 Adjuvante espalhante 0.5 0 Em conferência Consumo sem material em custódia',
         f'Adjuvante fora da REQ-035: aviso e caso CC-302 (custódia 0), sem recusa no app: {k2}')
    est(); a.setv('[aria-label="Trocar perfil de demonstração"]', 'Rui'); lf = linha('Adjuvante espalhante', 'fora da requisição')
    abrir_linha('Adjuvante espalhante', 'fora da requisição'); pf = painel(); a.clk('Recusar relato CC-302 ›', 'aside[role=dialog]')
    e0 = a.cen("c.movs.length"); clk_prim(); er0 = a.J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
    ok('Informe o motivo' in er0 and a.cen("[c.confs[1].estado,c.movs.length]") == ['Em conferência', e0], f'recusa sem motivo não grava (antes gravava um texto fixo): {er0}')
    a.setv('#fx_g_req_mot', 'registro sem fato físico'); r = clk_prim()
    kr = a.cen("[c.confs[1].estado,c.confs[1].decisao,c.ordens['OS-0421'].selos.map(s=>s.t).join(','),(c.ordens['OS-0421'].ap.slice(-1)[0].conf||{})['Adjuvante espalhante']]")
    ok('CC-302' in lf and 'Adjuvante espalhante 0,5 L relatado, nada em custódia' in pf and r == 'ok' and kr[0] == 'Recusado' and kr[1] == 'registro sem fato físico'
         and 'Consumo em conferência' not in kr[2] and kr[3] == 0.5,
         f'EST: linha própria do relato fora da requisição; o painel diz "nada em custódia"; recusar com o motivo digitado deixa sem efeito e preserva o relatado: {kr}', lf[:160])
    a.setv('[aria-label="Trocar perfil de demonstração"]', 'Ana')
    erros += a.erros() or []
    # 6 · sem sinal: o caso fica no aparelho e só aparece no Estoque e na O.S. depois do envio, uma vez
    a.mudar(f"cenSinal(c,false); c.app.turno={{os:'{OS}',ini:'10:00',pausas:[],fim:null}}; return cenFecharTurno(c,2,1,{{'{P}':3,'Adjuvante espalhante':0}},'');")   # turno aberto antes (CTL-2 · B)
    s0 = a.cen(f"[(c.confs||[]).filter(k=>k.estado==='Em conferência'&&k.sinc).length,c.confs.slice(-1)[0].sinc,c.ordens['{OS}'].selos.map(s=>s.t).join(',')]")
    a.mudar("cenSinal(c,true); return cenSinal(c,true);")
    s1 = a.cen(f"[(c.confs||[]).filter(k=>k.estado==='Em conferência'&&k.sinc).length,c.confs.length,c.ordens['{OS}'].selos.map(s=>s.t).join(',')]")
    ok(s0[0] == 0 and s0[1] is False and 'Consumo em conferência' not in s0[2] and s1[0] == 1 and s1[1] == 3 and 'Consumo em conferência' in s1[2],
         f'sem sinal: caso só no aparelho; ao voltar o sinal (2 envios) aparece uma vez, com selo: {s0} → {s1}')
    erros += a.erros() or []
    # 7 · reserva própria (OS-0424 · REQ-039, entrega parcial de 20 L): 25 L relatados → os 5 L que faltam saem da reserva da própria requisição
    a.mudar(f"window.__cen.cenEntregar(c,'REQ-039','{P}',20,'Marcos','Rui'); window.__cen.cenConfirmarRecebimento(c,'REQ-039'); return window.__cen.cenIniciarTurno(c,'OS-0424');")
    a.abrir('MB-03'); a.setv('#ft_ha', '10'); a.setv('#ft_h', '2'); a.setv('#ft_c0', '25'); a.clk('Fechar turno')
    r0 = a.cen(f"[{LOT}.fisico,{LOT}.reservado,{IT9}.custodia,c.confs.slice(-1)[0].id,c.confs.slice(-1)[0].estado]")
    est('#req=REQ-039'); abrir_linha(P, 'consumo relatado', r0[3]); l9 = painel()
    a.clk('Cancelar', 'aside[role=dialog]'); l9v = a.cen(f"[{LOT}.fisico,{LOT}.reservado,c.confs.slice(-1)[0].estado]")
    abrir_linha(P, 'consumo relatado', r0[3]); r = clk_prim(); t9 = a.toast()
    r1 = a.cen(f"[{LOT}.fisico,{LOT}.reservado,{IT9}.custodia,{IT9}.consumido,{IT9}.entregue,{IT9}.solicitado-{IT9}.consumido-{IT9}.custodia]")
    # SUP (06/10): o F26-02 reserva também os 14 L da REQ-035 (65 → 79 antes da entrega de 20 L à REQ-039): reservado 59 → 54 (antes 45 → 40)
    ok(r0[1:] == [59, 20, 'CC-304', 'Em conferência'] and 'Baixa 25 L na OS-0424: 20 L da custódia de Marcos · 5 L saem do lote F26-02 (reserva da REQ-039).' in l9
         and l9v == [r0[0], 59, 'Em conferência'],
         f'prévia da OS-0424 no painel: 5 L da reserva da própria REQ-039; fechar o painel não muda nada: {r0} · {l9[-160:]}')
    ok('CC-304 aceito: Fungicida A 25 L baixados na OS-0424 · 5 L regularizados do lote F26-02 (reserva da REQ-039).' in t9
         and r1 == [r0[0] - 5, 54, 0, 25, 25, 40],
         f'aceite: físico −5, reserva 59 → 54 (40 L da REQ-039 = saldo a entregar; 14 L da REQ-035), nenhum litro preso além da necessidade: {r1} · {t9[:120]}')
    shot('q_consumo_8_est_reserva_propria.png')
    erros += a.erros() or []
    # 8 · recibo do turno com o caso resolvido abre com o estado (Recusado por …), não com "Em conferência"
    a.c.size(390, 1800); a.mudar("c.app.turno={os:'OS-0424',ini:'10:00',pausas:[],fim:null}; return 'turno aberto antes';"); a.abrir('MB-03')   # custódia 0 após §7 (CTL-2 · B)
    a.setv('#ft_ha', '2'); a.setv('#ft_h', '1'); a.setv('#ft_c0', '3'); a.clk('Fechar turno')
    kid = a.cen("c.confs.slice(-1)[0].id")
    a.J("(()=>{const {cenMudar,cenConciliar}=window.__cen; return cenMudar(null,c=>cenConciliar(c,'%s',false,'registro sem fato físico','Rui'));})()" % kid)   # CTL-3: quem recusa é Rui (sem perfil, nada é gravado)
    a.clk('Com sinal'); time.sleep(.3); b = a.body(); i = b.find('Turno fechado ·'); rb = b[i:i + 400]
    ok('Conferência resolvida' in rb and 'Recusado por Rui (almoxarife) · Fungicida A 3 L relatados, nada em custódia' in rb and 'Em conferência ·' not in rb,
       f'recibo do app com caso resolvido: "{rb[:220]}"')
    shot('q_consumo_9_app_resolvido.png')
    erros += a.erros() or []
    ok(not erros, 'sem erros JS em MB-03, MB-01, EST e O.S. ' + str(erros))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
