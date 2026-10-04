# -*- coding: utf-8 -*-
"""Consumo relatado acima da custódia (RN-018; CONC-07; CONC-13; CMD-50; revisão QUALIDADE-ARTEFATO-20261003-FLUXO, caso 3) · Chrome real, ponta a ponta:
App MB-03 (390 px): a sugestão dose × área não editada acima da custódia não abre conferência (pede quanto foi usado); o valor informado grava o fato
Em conferência sem baixa nem custódia negativa · recibo e cartão do app mostram o caso e quem concilia · Estoque (etapa 3) mostra relatado × custódia;
Aceitar mostra antes de confirmar de onde sai cada litro (custódia, reserva da própria requisição, livre) · etapa 4 mostra a exposição junto ao disponível ·
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
def etapa(i):
    a.c.size(1440, 1100); a.abrir('EST'); a.J("document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[%d].click()" % i); time.sleep(.5)
est3 = lambda: etapa(2)
def linha(*ts):
    return a.J("(()=>{const ts=%s; const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)); return r?r.innerText.replace(/\\s+/g,' '):'';})()" % repr(list(ts)).replace("'", '"')) or ''
def btn_linha(ts, b):
    r = a.J("(()=>{const ts=%s; const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('button')].find(x=>x.innerText.trim()===%s); if(!x) return 'sem botão'; x.click(); return 'ok';})()"
            % (repr(list(ts)).replace("'", '"'), '"' + b + '"')); time.sleep(.5); return r
def prim():   # ação da etapa: botão verde do bloco onde age
    return a.J("(()=>{const b=[...document.querySelectorAll('main section button')].find(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); return b?b.innerText.trim():'';})()") or ''
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
         and 'Em conferência · Fungicida A 2 L relatados, 1 L em custódia · Rui (almoxarife) concilia' in b,
         'recibo do turno no app: selo Consumo em conferência, nada baixado e quem concilia')
    shot('q_consumo_2_app_recibo.png')
    a.abrir('MB-01'); b = a.body(); i = b.find('OS-0421 ·')
    ok('em conferência · relatado 2 L · com você 1 L' in b[i:i + 600] and 'Devolver sobra' not in b, 'MB-01: cartão da OS-0421 mostra o consumo em conferência e não pede devolução do 1 L')
    erros += a.erros() or []
    # 2 · Estoque, etapa 3: o caso com relatado × custódia, dono e decisões; a ação da etapa não oferece devolução fantasma; etapa 4 mostra a exposição
    est3(); k3 = a.J("document.querySelector('main').innerText"); ln = linha(RQ, P)
    ok('Consumo em conferência: OS-0421 · Fungicida A 2 L relatados, 1 L em custódia · Rui (almoxarife) aceita com a origem ou recusa o relato' in k3
         and 'Consumo em conferência' in ln and 'CC-301' in ln and 'Aceitar consumo' in ln and 'Recusar relato' in ln and prim() == 'Receber devolução da REQ-031',
         f'EST etapa 3: resumo e linha da REQ-035 com o caso, Aceitar/Recusar; ação da etapa = "{prim()}"', ln[:200])
    shot('q_consumo_3_est_conferencia.png')
    etapa(3); l4 = linha(P, 'em conferência (CC-301)')
    ok('480 L' in l4 and '1 L em conferência (CC-301)' in l4, f'EST etapa 4: disponível do Fungicida A mostra a exposição de 1 L em conferência: {l4[:160]}')
    shot('q_consumo_6_est_exposicao.png')
    erros += a.erros() or []
    # 3 · O.S.: selo na lista e encerrar bloqueado pelo caso aberto
    a.abrir('OS'); a.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0421')); r&&r.click();})()"); time.sleep(.5)
    lo = a.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith('OS-0421')); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    pe = a.J("window.__cen.cenPodeEncerrar(window.__cen.cenGet(),'OS-0421')")
    pa = a.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    ok('Consumo em conferência' in lo and 'Consumo em conferência' in pa and pe.startswith('Consumo em conferência: Fungicida A 2 L relatados, 1 L em custódia. Rui (almoxarife) concilia'),
         f'O.S.: selo na lista e no painel; encerrar bloqueado pelo caso ({pe[:80]})', lo[:200])
    shot('q_consumo_4_os_selo.png')
    erros += a.erros() or []
    # 4 · Estoque aceita: primeiro a consequência (nada muda), depois Confirmar aplica uma vez; custódia 0, consumido +2, selo some
    est3(); r = btn_linha([RQ, P], 'Aceitar consumo'); lp = linha(RQ, P)
    cp = a.cen(f"[{LOT}.fisico,c.confs[0].estado,{IT}.custodia]")
    ok(r == 'ok' and 'Baixa 2 L na OS-0421: 1 L da custódia de Marcos · 1 L sai do lote F26-02 (livre).' in lp and 'Confirmar aceite' in lp and 'Voltar' in lp
         and cp == [c0[3], 'Em conferência', 1], f'Aceitar mostra antes de confirmar de onde sai cada litro; nada muda até confirmar: {cp} · {lp[-160:]}')
    shot('q_consumo_7_est_previa.png')
    r = btn_linha([RQ, P], 'Confirmar aceite'); t = a.toast()
    ca = a.cen(f"[{IT}.custodia,{IT}.consumido,{IT}.entregue,{LOT}.fisico,c.confs[0].estado,c.ordens['{OS}'].selos.map(s=>s.t).join(','),window.__cen.cenPodeEncerrar(c,'{OS}'),{LOT}.reservado]")
    ok(r == 'ok' and 'CC-301 aceito: Fungicida A 2 L baixados na OS-0421 · 1 L regularizado do lote F26-02.' in t and ca[0] == 0 and ca[1] == c0[1] + 2 and ca[2] == c0[2] + 1
         and ca[3] == c0[3] - 1 and ca[4] == 'Aceito' and 'Consumo em conferência' not in ca[5] and ca[7] == 65,
         f'confirmar: custódia 0, consumido +2, entregue +1, lote −1 L do livre (reserva da REQ-039 intacta), caso Aceito e selo fora: {ca[:5]} · {t[:120]}')
    rr = a.mudar("return window.__cen.cenConciliar(c,'CC-301',true);"); rep = a.cen(f"[{IT}.consumido,{LOT}.fisico]")
    ok(rep == [ca[1], ca[3]] and rr == 'Este consumo não está em conferência.', f'aceitar de novo é recusado e não baixa outra vez: {rep} · {rr}')
    shot('q_consumo_5_est_aceito.png')
    erros += a.erros() or []
    # 5 · fora da requisição (Adjuvante, nada com o operador) e recusa: relato sem efeito, nenhum relato apagado
    a.c.size(390, 1800); a.abrir('MB-03'); a.mudar(f"return cenIniciarTurno(c,'{OS}');"); a.abrir('MB-03')   # custódia 0: o cartão pede retirada; o turno abre direto
    a.setv('#ft_ha', '2'); a.setv('#ft_h', '1'); a.setv('#ft_c0', '0'); a.setv('#ft_c1', '0,5')
    av1 = campo(1); a.clk('Fechar turno')
    k2 = a.cen("(c.confs||[]).map(k=>k.id+' '+k.prod+' '+k.relatado+' '+k.custodia+' '+k.estado+' '+k.motivo)")
    ok('Acima do que está com você (0 L): fecha em conferência' in av1 and len(k2) == 2 and k2[1] == 'CC-302 Adjuvante espalhante 0.5 0 Em conferência Consumo sem material em custódia',
         f'Adjuvante fora da REQ-035: aviso e caso CC-302 (custódia 0), sem recusa no app: {k2}')
    est3(); lf = linha('Adjuvante espalhante', 'fora da requisição'); r = btn_linha(['Adjuvante espalhante', 'fora da requisição'], 'Recusar relato')
    kr = a.cen("[c.confs[1].estado,c.confs[1].decisao,c.ordens['OS-0421'].selos.map(s=>s.t).join(','),(c.ordens['OS-0421'].ap.slice(-1)[0].conf||{})['Adjuvante espalhante']]")
    ok('CC-302' in lf and 'Adjuvante espalhante 0,5 L relatado, nada em custódia' in lf and r == 'ok' and kr[0] == 'Recusado' and kr[1] == 'registro sem fato físico'
         and 'Consumo em conferência' not in kr[2] and kr[3] == 0.5,
         f'EST: linha própria do relato fora da requisição (singular, "nada em custódia"); recusar deixa sem efeito e preserva o relatado: {kr}', lf[:160])
    erros += a.erros() or []
    # 6 · sem sinal: o caso fica no aparelho e só aparece no Estoque e na O.S. depois do envio, uma vez
    a.mudar(f"cenSinal(c,false); cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,2,1,{{'{P}':3,'Adjuvante espalhante':0}},'');")
    s0 = a.cen(f"[(c.confs||[]).filter(k=>k.estado==='Em conferência'&&k.sinc).length,c.confs.slice(-1)[0].sinc,c.ordens['{OS}'].selos.map(s=>s.t).join(',')]")
    a.mudar("cenSinal(c,true); return cenSinal(c,true);")
    s1 = a.cen(f"[(c.confs||[]).filter(k=>k.estado==='Em conferência'&&k.sinc).length,c.confs.length,c.ordens['{OS}'].selos.map(s=>s.t).join(',')]")
    ok(s0[0] == 0 and s0[1] is False and 'Consumo em conferência' not in s0[2] and s1[0] == 1 and s1[1] == 3 and 'Consumo em conferência' in s1[2],
         f'sem sinal: caso só no aparelho; ao voltar o sinal (2 envios) aparece uma vez, com selo: {s0} → {s1}')
    erros += a.erros() or []
    # 7 · reserva própria (OS-0424 · REQ-039, entrega parcial de 20 L): 25 L relatados → os 5 L que faltam saem da reserva da própria requisição
    a.mudar(f"window.__cen.cenEntregar(c,'REQ-039','{P}',20,'Marcos'); window.__cen.cenConfirmarRecebimento(c,'REQ-039'); return window.__cen.cenIniciarTurno(c,'OS-0424');")
    a.abrir('MB-03'); a.setv('#ft_ha', '10'); a.setv('#ft_h', '2'); a.setv('#ft_c0', '25'); a.clk('Fechar turno')
    r0 = a.cen(f"[{LOT}.fisico,{LOT}.reservado,{IT9}.custodia,c.confs.slice(-1)[0].id,c.confs.slice(-1)[0].estado]")
    est3(); r = btn_linha(['REQ-039', P], 'Aceitar consumo'); l9 = linha('REQ-039', P)
    b1 = btn_linha(['REQ-039', P], 'Voltar'); l9v = linha('REQ-039', P)
    r = btn_linha(['REQ-039', P], 'Aceitar consumo'); r = btn_linha(['REQ-039', P], 'Confirmar aceite'); t9 = a.toast()
    r1 = a.cen(f"[{LOT}.fisico,{LOT}.reservado,{IT9}.custodia,{IT9}.consumido,{IT9}.entregue,{IT9}.solicitado-{IT9}.consumido-{IT9}.custodia]")
    ok(r0[1:] == [45, 20, 'CC-304', 'Em conferência'] and 'Baixa 25 L na OS-0424: 20 L da custódia de Marcos · 5 L saem do lote F26-02 (reserva da REQ-039).' in l9
         and b1 == 'ok' and 'Aceitar consumo' in l9v and 'Confirmar aceite' not in l9v,
         f'prévia da OS-0424: 5 L da reserva da própria REQ-039; Voltar desfaz só a prévia: {r0} · {l9[-140:]}')
    ok('CC-304 aceito: Fungicida A 25 L baixados na OS-0424 · 5 L regularizados do lote F26-02 (reserva da REQ-039).' in t9
         and r1 == [r0[0] - 5, 40, 0, 25, 25, 40],
         f'aceite: físico −5, reserva 45 → 40 = saldo a entregar 40 (nenhum litro preso além da necessidade): {r1} · {t9[:120]}')
    shot('q_consumo_8_est_reserva_propria.png')
    erros += a.erros() or []
    # 8 · recibo do turno com o caso resolvido abre com o estado (Recusado por …), não com "Em conferência"
    a.c.size(390, 1800); a.mudar("return window.__cen.cenIniciarTurno(c,'OS-0424');"); a.abrir('MB-03')
    a.setv('#ft_ha', '2'); a.setv('#ft_h', '1'); a.setv('#ft_c0', '3'); a.clk('Fechar turno')
    kid = a.cen("c.confs.slice(-1)[0].id")
    a.J("(()=>{const {cenMudar,cenConciliar}=window.__cen; return cenMudar(null,c=>cenConciliar(c,'%s',false,'registro sem fato físico'));})()" % kid)
    a.clk('Com sinal'); time.sleep(.3); b = a.body(); i = b.find('Turno fechado ·'); rb = b[i:i + 400]
    ok('Conferência resolvida' in rb and 'Recusado por Rui (almoxarife) · Fungicida A 3 L relatados, nada em custódia' in rb and 'Em conferência ·' not in rb,
       f'recibo do app com caso resolvido: "{rb[:220]}"')
    shot('q_consumo_9_app_resolvido.png')
    erros += a.erros() or []
    ok(not erros, 'sem erros JS em MB-03, MB-01, EST e O.S. ' + str(erros))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
