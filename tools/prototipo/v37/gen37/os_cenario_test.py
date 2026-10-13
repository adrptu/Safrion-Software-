# -*- coding: utf-8 -*-
"""O.S. × cenário compartilhado (OS.dc.html no Chrome headless), 15 verificações · jornada da OS-0430.
Pela tela: liberar pelo agrônomo (pode ajustar antes) → requisição nova reserva por lote. Estoque e App simulados por cenMudar + aviso de
mudança (como outro quadro do Canvas): entregas → confirmação no app → turno sem sinal → sinal → turno 2 com sobra. A tela reflete
entregue/consumido/realizado sem recarregar; encerrar fica bloqueado pela sobra até a devolução no Estoque. Depois: bloqueio por sinal
(OS-0417), liberar bloqueado por falta de lote (OS-0418) e por saldo (OS-0430), Restaurar demonstração e Ajustar antes de liberar
(dose e área → v2 com histórico, liberada no mesmo comando).
Uso: python3 os_cenario_test.py   (compile antes: areas.processo_os.build())"""
import sys, os, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
from conferencia_diaria_nav_helpers import conferir_dias

T = Os(); OS = 'OS-0430'
def setin(lab, val):  # campo do painel pelo rótulo acessível (input + change, como a digitação)
    T.J(f"""(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)});
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
try:
    T.abrir()
    # 1 · A liberar sem etapa de revisão: próximo passo Liberar para execução (Ana pode ajustar antes); ajuste inválido não libera
    T.ordem(OS); p = T.pan(); st = T.cen(f"[c.ordens['{OS}'].etapa, 'aprov' in c.ordens['{OS}'], c.v]")
    T.btn('Ajustar antes de liberar'); setin('Área da ordem (ha)', '0'); T.btn('Salvar e liberar'); pa = T.pan(); T.btn('Voltar'); print('  ', st)
    T.ok(st == ['A liberar', False, 2] and T.temb('Liberar para execução') and T.temb('Ajustar antes de liberar') and not T.temb('Revisar versão') and not T.temb('Aprovar versão')
         and 'Aguardando agrônomo' not in p and 'Aprovada pelo agrônomo' not in p and 'APV-' not in p and 'Informe a área maior que 0 ha.' in pa and T.cen(f"c.ordens['{OS}'].etapa") == 'A liberar',
         'A liberar sem revisão: Liberar para execução + Ajustar antes de liberar; área 0 recusada junto ao campo, nada liberado; cenário v2 sem aprov', (st, p[p.find('PRÓXIMO'):][:300], pa[-300:]))
    # 2 · liberar: a requisição nova reserva por lote (Glifosato 320 L, 2,4-D 160 L, Óleo 80 L)
    T.btn('Liberar para execução'); ct = T.pan(); T.btn('Confirmar liberação'); tt = T.toast()
    RQ = T.cen(f"c.ordens['{OS}'].req"); st = T.cen(f"[c.ordens['{OS}'].etapa, c.reqs['{RQ}'].itens.map(i=>i.prod+' '+i.solicitado+' '+i.lote).join(' | '), c.lotes['Glifosato 480|G26-14'].reservado]")
    print('  ', RQ, st, '|', tt)
    T.ok('reserva no Estoque, por lote: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L' in ct and st[0] == 'Liberadas' and st[1].startswith('Glifosato 480 320 G26-14 | 2,4-D 806 160')
         and 'Óleo mineral 80' in st[1] and st[2] == 320 and f'{OS} liberada. {RQ} reservou' in tt and 'Reservado 320 L · lote G26-14' in T.ins() and 'Liberadas' in T.linha(OS),
         f'liberar: {RQ} reserva Glifosato 480 320 L (G26-14), 2,4-D 806 160 L e Óleo mineral 80 L; painel mostra a reserva por lote', (ct[-300:], st, tt))
    # 2b · CTL-1 (Frente F): a confirmação diz que é aprovar e liberar; a Origem ganha CMD-42 (área e doses) e CMD-06 (requisição reservada)
    p = T.pan()
    T.ok('ao confirmar, Ana (agrônoma) aprova esta versão e Ana (gestora) libera' in ct and re.search(r'v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 160 ha · Glifosato 480 2 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha \(CMD-42\)', p)
         and re.search(r'v1 liberada por Ana \(gestora\) às \d\d:\d\d · ' + RQ + r' reservada no Estoque \(CMD-06\)', p) and tt.rstrip().endswith('v1 aprovada por Ana (agrônoma) e liberada por Ana (gestora).'),   # CTL-3: CMD-06 pelo papel liberador (gestor)
         'CTL-1: confirmar = aprovar esta versão e liberar; Origem com CMD-42 e CMD-06 separados', (ct[-300:], p[p.find('ORIGEM'):][:500], tt))
    # 3 · Estoque entrega os 3 itens a Marcos (outra tela): o painel mostra entregue, embalagem e a quem, sem recarregar
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): T.mudar(f"return cenEntregar(c,'{RQ}','{prod}',{q},'Marcos','Rui');", avisar=False)
    T.mudar("return {msg:''};"); i = T.ins(); print('  ', i[:400])
    T.ok('Entregue 320 L (16 × galão 20 L) a Marcos' in i and i.count('Aguardando confirmação no app') >= 3 and 'Entregue · aguardando confirmação no app' in i,
         'entregas do Estoque aparecem sem recarregar: 320 L (16 × galão 20 L) a Marcos, aguardando confirmação no app', i[:400])
    # 4 · App: confirma, inicia turno, fica sem sinal e fecha 60 ha → "Aguardando sinal"; realizado e consumo só mudam no envio (custódia 320 L)
    T.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenIniciarTurno(c,'{OS}'); cenSinal(c,false); return cenFecharTurno(c,60,5);")
    p = T.pan(); a = T.aps(); i = T.ins(); print('  ', a, '|', T.linha(OS))
    T.ok('Em execução' in T.linha(OS) and T.cel(OS, 'Realizado') == '0,00 ha' and T.cel(OS, 'Saldo') == '160,00 ha' and len(a) == 1 and 'Dia 1 · app' in a[0] and 'Aguardando sinal' in a[0] and 'não somado' in a[0]
         and 'Acumulado 0 / 160 ha · saldo 160 ha · 60 ha no aparelho aguardando sinal' in p and 'Confirmado no app' in i and 'Consumido 120 L' not in i and 'Em custódia 320 L' in i and 'consumo no aparelho, aguardando sinal' in i,
         'turno do app sem sinal: Em execução, "Dia 1 · app · Aguardando sinal" fora do acumulado; consumo ainda no aparelho (custódia 320 L)', (a, T.linha(OS), i[:300]))
    # 5 · sinal volta: o realizado passa a 60 ha (uma vez só)
    T.mudar("cenSinal(c,true); return cenSinal(c,true);"); a = T.aps(); i = T.ins(); print('  ', a, '|', T.linha(OS))
    T.ok(T.cel(OS, 'Realizado') == '60,00 ha' and T.cel(OS, 'Saldo') == '100,00 ha' and len(a) == 1 and 'Provisório' in a[0] and '60 / 160 ha' in a[0] and 'Consumido 120 L' in i and 'Em custódia 200 L' in i,
         'sinal de volta: realizado 60 / 160 ha e consumo 120 L (custódia 200 L) juntos, sem duplicar', (a, T.linha(OS), i[:300]))
    # 6 · turno 2 de 100 ha com 180 L de Glifosato (sobra 20 L): saldo zero → próximo passo Enviar para conferência
    T.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,100,8,{{'Glifosato 480':180}});"); i = T.ins()
    T.ok(T.cel(OS, 'Realizado') == '160,00 ha' and T.cel(OS, 'Saldo') == '0,00 ha' and T.temb('Enviar para conferência') and 'Consumido 300 L' in i and 'Em custódia 20 L' in i
         and 'Insumo esgotado' not in T.linha(OS),
         'turno 2 (100 ha, 180 L de Glifosato): 160 / 160 ha, sobra 20 L em custódia, botão Enviar para conferência, sem "Insumo esgotado" (CTL-2 · B, P5)', (T.linha(OS), i[:300]))
    # 7 · em conferência, encerrar fica bloqueado pela sobra, com o atalho para receber a devolução no Estoque
    T.btn('Enviar para conferência'); T.btn('Confirmar envio'); p = T.pan(); print('  ', p[p.find('PRÓXIMO'):][:300])
    T.ok('Em conferência' in T.linha(OS) and 'Encerrar bloqueado: sobra em custódia · Glifosato 480 20 L (1 × galão 20 L) com Marcos.' in p
         and T.link('Receber devolução no Estoque') == 'EST.dc.html' and not T.temb('Conferir e encerrar'),
         'Em conferência: encerrar bloqueado pela sobra de 20 L com Marcos e link "Receber devolução no Estoque" → EST.dc.html', p[:500])
    # 8 · Estoque recebe a devolução (apta): o bloqueio da sobra sai sem recarregar
    # B-R8 (09/10): o turno 2 informou 180 L de Glifosato onde o planejado do trecho era 200 L (2 L/ha × 100 ha); a divergência de dose
    # passa a ser o bloqueio do encerramento até a revisão técnica de Ana (agrônoma) — regra nova, expectativa mudada com motivo
    T.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true,'Rui');"); p = T.pan(); i = T.ins()
    T.ok('sobra em custódia' not in p and 'Encerrar bloqueado: divergência de consumo/dose em revisão técnica · dia 2 · Glifosato 480 planejado 200 L × informado 180 L.' in p
         and not T.temb('Conferir e encerrar') and 'Devolvido 20 L' in i and 'Consumido · sobra devolvida' in i,
         'devolução recebida no Estoque: o bloqueio da sobra some e fica o da divergência de dose (Glifosato 200 L planejado × 180 L informado), trilha com Devolvido 20 L', p[:500])
    # 8b · Ana (agrônoma) aceita a divergência com motivo na linha do apontamento: o bloqueio some e surge Conferir e encerrar
    T.J("""(()=>{const i=[...document.querySelectorAll('aside[role=dialog] textarea')].find(x=>x.getAttribute('aria-label')==='Motivo ou correção decidida · dia 2');
      Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(i,'Bordadura sem aplicação por vento; vistoria sem rebrote');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    T.btn('Aceitar com motivo'); p = T.pan()
    T.ok('Conferência diária pendente' in p and not T.temb('Conferir e encerrar'), 'Após revisão técnica, Paula ainda precisa conferir os dias', p[:500])
    conferir_dias(T.J,OS,[1,2]); p=T.pan()
    T.ok('Encerrar bloqueado' not in p and T.temb('Conferir e encerrar') and 'nada em custódia' in p and 'Revisão técnica: aceita por Ana (agrônoma)' in p,
         'revisão técnica aceita por Ana (agrônoma) com motivo: bloqueio some e surge Conferir e encerrar', p[:500])
    # 9 · conferir e encerrar grava no cenário (regra atual: Em conferência → Encerradas)
    T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); st = T.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].ap.map(a=>a.st).join(',')]"); print('  ', st, T.toast())
    T.ok(st == ['Encerradas', 'Conferido,Conferido'] and 'Encerradas' in T.linha(OS) and 'somente consulta' in T.pan() and f'{OS} encerrada' in T.toast(),
         'encerrar: cenário Encerradas, apontamentos conferidos, painel somente consulta', st)
    T.shot('os_cenario_encerrada.png'); T.fechar()
    # 10 · bloqueio por sinal: OS-0417 com apontamento no aparelho aguardando sinal
    T.mudar("c.ordens['OS-0417'].ap.push({d:'26/09',dia:4,ha:0,st:'Provisório',origem:'app',sinc:false}); return {msg:''};")
    T.ordem('OS-0417'); p = T.pan()
    T.ok('Encerrar bloqueado: há apontamentos no aparelho aguardando sinal.' in p and 'Quem resolve: Paula reconecta o app' in p and not T.temb('Conferir e encerrar'),
         'OS-0417: apontamento aguardando sinal bloqueia o encerramento e diz quem resolve', p[:400])
    T.fechar()
    # 11 · liberar bloqueado pelo Estoque: OS-0418 A liberar, sem lote de Ureia 45% → motivo no próximo passo desde a abertura, sem botão de liberar
    T.ordem('OS-0418'); p = T.pan()
    # 01/10: bloqueada pelo Estoque, a ordem segue sem "Liberar", mas o agrônomo pode ajustar (trocar o produto ou a dose) e liberar no mesmo passo
    T.ok('Liberar bloqueado: sem lote de Ureia 45% no Estoque.' in p and T.link('Ver saldos no Estoque') == 'EST.dc.html' and not T.temb('Liberar para execução')
         and T.temb('Ajustar antes de liberar') and T.cen("c.ordens['OS-0418'].etapa") == 'A liberar',
         'OS-0418 A liberar: liberar bloqueado com o motivo do Estoque (sem lote de Ureia 45%) e atalho aos saldos', p[p.find('PRÓXIMO'):][:300])
    T.fechar()
    # 12 · outra tela restaura a demonstração: a O.S. volta ao início sem recarregar; com o lote G26-14 baixo, liberar mostra o saldo
    T.J("window.__cen.cenReset(); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4); l0 = T.linha(OS)
    T.mudar("c.lotes['Glifosato 480|G26-14'].fisico=100; return {msg:''};"); T.ordem(OS); p = T.pan(); print('  ', l0, '|', p[p.find('PRÓXIMO'):][:260])
    T.ok('A liberar' in l0 and 'Aguardando agrônomo' not in l0 and 'Liberar bloqueado: saldo insuficiente de Glifosato 480: 100 L disponíveis para 320 L.' in p and not T.temb('Liberar para execução'),
         'cenReset em outra tela volta a OS-0430 a A liberar; com 100 L no G26-14, liberar fica bloqueado pelo saldo', (l0, p[:300]))
    T.fechar()
    # 13 · Restaurar demonstração (rodapé, com confirmação): lote e requisições voltam ao início
    T.btn('Restaurar demonstração', 'body'); T.btn('Restaurar', 'body'); tt = T.toast()
    st = T.cen(f"[Object.keys(c.reqs).length, c.ordens['{OS}'].etapa, c.lotes['Glifosato 480|G26-14'].fisico]"); print('  ', st, tt)
    # 01/10: + 5 requisições da Fazenda Lagoa Grande (REQ-021 a REQ-025, dados_lagoa_safra.py) → 11 no cenário inicial
    # 06/10 (BEN-1): + REQ-030 das caixas da OB-0110 (ordem de beneficiamento) → 12
    T.ok(st == [12, 'A liberar', 1200] and 'Demonstração restaurada' in tt and 'A liberar' in T.linha(OS),
         'Restaurar demonstração: 12 requisições (6 da Santa Rita + 5 da Lagoa Grande + REQ-030 do beneficiamento), OS-0430 volta a A liberar, G26-14 com 1.200 L', (st, tt))
    # 14 · Ajustar antes de liberar: área e dose no mesmo passo; Salvar e liberar grava a v2 (histórico na Origem) e libera com a reserva ajustada
    T.ordem(OS); T.btn('Ajustar antes de liberar'); setin('Área da ordem (ha)', '150'); setin('Dose de Glifosato 480 (L/ha)', '1,8'); T.btn('Salvar e liberar')
    tt = T.toast(); p = T.pan(); i = T.ins()
    st = T.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].versao, c.ordens['{OS}'].area, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.prod+' '+i.solicitado).join(' | ')]"); print('  ', st, tt)
    T.ok(st == ['Liberadas', 'v2', 150, 'Glifosato 480 270 | 2,4-D 806 150 | Óleo mineral 75'] and f'{OS} ajustada para v2 e liberada' in tt
         and re.search(r'v2 ajustada por Ana \(agrônoma\) às \d\d:\d\d ao liberar: área 160 → 150 ha; Glifosato 480 2 → 1,8 L/ha', p) is not None and '1,8 L/ha' in i and '270 L' in i and 'Liberadas' in T.linha(OS),
         'Ajustar antes de liberar: 150 ha e Glifosato 1,8 L/ha → v2 com histórico na Origem, liberada com a reserva ajustada (270 L)', (st, tt, p[-400:]))
    # 14b · CTL-1 (Frente F): o CMD-42 aprova a v2 com as doses ajustadas
    T.ok(re.search(r'v2 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 150 ha · Glifosato 480 1,8 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha \(CMD-42\)', p) is not None
         and T.cen(f"((c.ordens['{OS}'].osc||{{}}).ev||[]).map(e=>e.cmd+' '+e.v).join(',')") == 'CMD-42 v2,CMD-06 v2',
         'CTL-1: ajustar e liberar grava CMD-42 e CMD-06 da v2 com as doses ajustadas', p[p.find('ORIGEM'):][:600])
    T.fechar()
    # 14c-14f · CTL-1 (Frente E1): a trava legal única (a mesma do AG-01) no ajuste, no painel e na Nova ordem; alertas na confirmação
    def reset():
        T.J("window.__cen.cenReset(); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    def setid(sel, val):
        T.J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)});
          i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
    reset(); T.ordem(OS); T.btn('Ajustar antes de liberar'); setin('Dose de Glifosato 480 (L/ha)', '7,5'); T.btn('Salvar e liberar'); pa = T.pan()
    st = T.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].versao, c.ordens['{OS}'].req, ((c.ordens['{OS}'].osc||{{}}).ev||[]).length]")
    setin('Dose de Glifosato 480 (L/ha)', '2'); setid('#aj_inc', 'Abamectina 18 EC'); T.btn('Incluir'); setin('Dose de Abamectina 18 EC (L/ha)', '0,5'); T.btn('Salvar e liberar'); pb = T.pan()
    st2 = T.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].versao]")
    T.btn('Tirar Abamectina 18 EC da ordem') or T.J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>(b.getAttribute('aria-label')||'').startsWith('Tirar Abamectina')); b&&b.click();})()"); time.sleep(.3)
    T.btn('Salvar e liberar'); tt = T.toast(); st3 = T.cen(f"c.ordens['{OS}'].etapa")
    T.ok('Glifosato 480 7,5 L/ha em T1 (T1-A): dose fora da bula: 1,5–3 L/ha.' in pa and st == ['A liberar', 'v1', None, 0]
         and 'Abamectina 18 EC 0,5 L/ha em T1 (T1-A): sem registro para soja.' in pb and st2 == ['A liberar', 'v1'] and st3 == 'Liberadas' and f'{OS} liberada' in tt,
         'E1 14c: ajuste com Glifosato 7,5 L/ha e Abamectina em soja recusados junto ao campo (nada gravado: v1, sem REQ, sem CMD-42); dentro da bula, Salvar e liberar passa',
         (pa[-500:], st, pb[-400:], st2, st3, tt))
    T.fechar(); reset()
    T.mudar(f"c.ordens['{OS}'].ins[0].dose=7.5; c.ordens['{OS}'].ins[0].tot=1200; return {{msg:''}};"); T.ordem(OS); p = T.pan()
    T.fechar(); aba = lambda n: (T.J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(n)}); b&&b.click();}})()"), time.sleep(.4))
    aba('Kanban'); kb = T.J("(()=>{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(x=>x.innerText.indexOf('OS-0430')===0); return k?k.innerText:'';})()") or ''
    aba('Lista'); T.ordem(OS)
    T.ok('Fora do registro · Glifosato 480' in T.linha(OS) and 'Fora do registro · Glifosato 480' in kb and 'Liberar bloqueado: Glifosato 480 7,5 L/ha em T1 (T1-A): dose fora da bula: 1,5–3 L/ha.' in p
         and 'Quem resolve: Ana (agrônoma), ajustando produto ou dose antes de liberar.' in p and not T.temb('Liberar para execução') and T.temb('Ajustar antes de liberar'),
         'E1 14d: dose fora da bula no cenário → selo "Fora do registro" na lista e no Kanban; painel "Liberar bloqueado", quem resolve = Ana, sem Liberar', (T.linha(OS), kb, p[p.find('PRÓXIMO'):][:400]))
    T.fechar(); reset()
    NV = 'aside[role=dialog][aria-label="Nova ordem"]'
    def nova(saf, cult, atv):
        T.btn('Nova ordem', root='main'); setv('#nv_saf', saf); setv('#nv_cult', cult); setv('#nv_atv', atv); setv('#nv_jan', '2026-10-05'); T.btn('Emitir ordem', root=NV)
        return (T.J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.getAttribute('aria-label'):'';})()") or '').split(' · ')[0]
    def setv(sel, val):
        T.J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
    oa = nova('S27SF', 'd1', 'm3'); T.btn('Ajustar antes de liberar'); setin('Dose de Atrazina 500 (L/ha)', '4'); T.btn('Salvar e liberar'); pa = T.pan(); T.btn('Voltar'); T.fechar()
    ob = nova('S2627', 'c1', 'a7'); cb = T.pan()   # revisão do CTL-1, achado 1: unidade diferente da bula agora trava (antes só alerta)
    T.ok(oa and 'Atrazina 500' in pa and 'sem registro' not in pa and 'fora da bula' not in pa
         and 'Liberar bloqueado: Inseticida B 0,3 L/ha em T1 (T1-A): dose em L/ha e bula em 0,8–1 kg/ha: unidade diferente da bula' in cb
         and not T.temb('Liberar para execução') and T.temb('Ajustar antes de liberar'),
         'E1 14e: Nova ordem da Safrinha 2027 (milho no T1-A) aceita a Atrazina sem erro junto ao campo; Nova ordem c1·a7 bloqueia a liberação pela unidade do Inseticida B (L/ha × bula em kg/ha) e oferece o ajuste',
         (oa, pa[-300:], ob, cb[cb.find('PRÓXIMO'):][:400]))
    T.fechar()
    # 15 · sem erro de script
    er = T.erros(); T.ok(not er, 'sem erro de script', er)
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
