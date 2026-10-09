# -*- coding: utf-8 -*-
"""CTL-3 · ATOR (O.S., Chrome real, 1440 px): quem age é o perfil de demonstração do menu lateral (não é segurança de acesso).
Liberar a O.S. agrícola grava CMD-42 (aprovada por, papel agrônomo) e CMD-06 (liberada por, papel liberador = gestor, padrão de 05/10):
  - Caio (PCP) não vê "Liberar para execução" nem "Ajustar antes de liberar"; a tela diz quem decide; o comando direto é recusado e nada é gravado;
  - Ana (gestora e agrônoma) libera numa confirmação: os dois registros, cada um com o papel que decidiu.
Duplicidade de apontamento (CMD-09): só quem confere (Paula) vê as três saídas; Rui é recusado no comando; a decisão de Paula grava "Paula (conferência)".
Revisão do CTL-3: trocar o perfil com a confirmação (ou a dispensa) aberta fecha o que foi montado para o perfil anterior; cancelar sem execução
(CMD-46, AL-04) só para o gestor.
Uso (de gen37/, depois de build.py e montar_render.py): python3 os_ator_test.py"""
import sys, os, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
T = Os(); J = T.J
SEL = '[aria-label="Trocar perfil de demonstração"]'
def perfil(k):   # o seletor do menu lateral (o mesmo de qualquer tela da equipe da fazenda)
    J(f"""(()=>{{const i=document.querySelector({json.dumps(SEL)}); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(k)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def cmd(js):   # comando direto no cenário da página (como outro canal chamaria o servidor)
    return J("(()=>{const X=window.__cen; const r=X.cenMudar(null,c=>" + js + "); return r.erro||r.msg||'';})()") or ''
try:
    T.abrir(wait=1.3)
    T.ok(J(f"(document.querySelector({json.dumps(SEL)})||{{value:''}}).value") == 'Ana', 'menu lateral: perfil de demonstração começa em Ana')
    # ---- 1 · Caio (PCP): a liberação é recusada a quem não tem os papéis ----
    perfil('Caio'); tt = T.toast()
    T.ordem('OS-0430'); p = T.pan()
    T.ok('Perfil de demonstração: Caio · PCP (não é segurança de acesso).' in tt and 'Liberar para execução: decisão de Ana (agrônoma e gestora).' in p
         and 'Quem resolve: Ana (agrônoma) aprova esta versão e Ana (gestora) libera; o perfil Caio · PCP não tem esses papéis.' in p
         and not T.temb('Liberar para execução') and not T.temb('Ajustar antes de liberar'),
         'Caio: no lugar de "Liberar para execução" a tela diz quem aprova e quem libera; sem Ajustar antes de liberar', (tt, p[p.find('PRÓXIMO'):][:300]))
    r = cmd("X.osc_liberar(c,'OS-0430',false,'',{k:'Caio'})")
    st = T.cen("[c.ordens['OS-0430'].etapa,((c.ordens['OS-0430'].osc||{}).ev||[]).length,c.lotes['Glifosato 480|G26-14'].reservado,c.ordens['OS-0430'].req||'']")
    T.ok(r == 'Aprovar a v1 da OS-0430 (CMD-42): decisão de Ana (agrônoma). Nada foi alterado.' and st == ['A liberar', 0, 0, ''],
         'Caio no comando direto: recusado com quem decide; nada gravado (A liberar, sem CMD-42/CMD-06, sem reserva, sem requisição)', (r, st))
    r = cmd("X.osc_ajustar(c,'OS-0430',150,{'Glifosato 480':1.8},'',[],[],true,{k:'Caio'})")
    T.ok(r == 'Ajustar a OS-0430 (nova versão): decisão de Ana (agrônoma). Nada foi alterado.' and T.cen("c.ordens['OS-0430'].versao") == 'v1',
         'Caio não ajusta dose e área pelo comando: versão segue v1', r)
    T.shot('os_ator_caio.png'); T.fechar()
    # ---- 2 · Ana (gestora e agrônoma): aprova e libera numa confirmação, com dois registros ----
    perfil('Ana'); T.ordem('OS-0430')
    T.ok(T.temb('Liberar para execução') and T.temb('Ajustar antes de liberar'), 'de volta a Ana: Liberar para execução e Ajustar antes de liberar')
    T.btn('Liberar para execução'); ct = T.pan()
    T.ok('ao confirmar, Ana (agrônoma) aprova esta versão e Ana (gestora) libera' in ct, 'confirmação nomeia quem aprova e quem libera', ct[ct.find('PRÓXIMO'):][:300])
    T.btn('Confirmar liberação'); t = T.toast(); p = T.pan()
    ev = T.cen("((c.ordens['OS-0430'].osc||{}).ev||[]).map(e=>e.cmd+'|'+e.por)") or []
    T.ok(ev == ['CMD-42|Ana (agrônoma)', 'CMD-06|Ana (gestora)'] and t.rstrip().endswith('v1 aprovada por Ana (agrônoma) e liberada por Ana (gestora).')
         and re.search(r'v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 160 ha', p) and re.search(r'v1 liberada por Ana \(gestora\) às \d\d:\d\d · REQ-\d+ reservada no Estoque \(CMD-06\)', p)
         and 'Liberadas' in T.linha('OS-0430'), 'Ana libera: CMD-42 por Ana (agrônoma) e CMD-06 por Ana (gestora), na Origem e no aviso', (ev, t[-160:], p[p.find('ORIGEM'):][:400]))
    T.fechar()
    # ---- 3 · duplicidade (CMD-09): só quem confere decide ----
    T.mudar("osc_apontar(c,'OS-0421','26/09',50); cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,50,8,undefined,'',[]);")
    perfil('Rui'); T.ordem('OS-0421'); p = T.pan()
    T.ok('Quem decide: Paula (conferência).' in p and not T.temb('Outro turno: somar') and not T.temb('Mesmo turno: vale o dia 5'),
         'Rui: a linha retida diz quem decide e não oferece as três saídas', p[p.find('Dia 6'):][:240])
    r = cmd("X.osc_apDecidir(c,'OS-0421',6,'somar',undefined,{k:'Rui'})")
    T.ok(r == 'Decidir a duplicidade do dia 6 da OS-0421: decisão de Paula (conferência). Nada foi alterado.' and T.cen("c.ordens['OS-0421'].realizado") == 240,
         'Rui no comando direto: recusado, nada somado (240 ha)', r)
    T.fechar(); perfil('Paula'); T.ordem('OS-0421'); p = T.pan()
    T.ok(T.temb('Outro turno: somar') and T.temb('Mesmo turno: vale o dia 5'), 'Paula (almoxarife e conferência): as saídas aparecem', p[p.find('Dia 6'):][:200])
    T.btn('Mesmo turno: vale o dia 5'); dec = T.cen("(c.ordens['OS-0421'].ap.find(a=>a.dia===6).dec||{}).quem")
    T.ok(dec == 'Paula (conferência)' and T.cen("c.ordens['OS-0421'].realizado") == 240, 'Paula decide: a decisão grava Paula (conferência); 240 ha', dec)
    T.shot('os_ator_paula.png'); T.fechar(); perfil('Ana')
    # ---- 4 · revisão do CTL-3, achado 1: trocar o perfil fecha a confirmação ou o formulário montado para o perfil anterior; CMD-46 (achado 4) ----
    T.J("window.__cen.cenReset()"); T.abrir(wait=1.2); perfil('Ana')
    T.ordem('OS-0430'); T.btn('Liberar para execução'); c0 = T.pan()
    perfil('Caio'); p = T.pan()
    T.ok('ao confirmar, Ana (agrônoma) aprova esta versão e Ana (gestora) libera' in c0 and 'Liberar OS-0430 (versão' not in p and 'Caio (PCP) aprova' not in p
         and not T.temb('Confirmar liberação') and 'Liberar para execução: decisão de Ana (agrônoma e gestora).' in p and T.cen("c.ordens['OS-0430'].etapa") == 'A liberar',
         'Ana abre a confirmação da OS-0430 e troca para Caio: a confirmação fecha (sem "Caio (PCP) aprova" nem "Confirmar liberação"); fica a pendência; segue A liberar (antes: a tela dizia "Caio (PCP) aprova esta versão e Caio (PCP) libera")',
         [c0[c0.find('Liberar OS-0430'):][:160], p[p.find('PRÓXIMO'):][:300]])
    T.shot('os_ator_troca_caio.png'); T.fechar(); perfil('Ana'); T.ordem('OS-0421'); T.btn('Dispensar saldo'); d0 = T.temb('Confirmar dispensa')
    perfil('Caio'); p = T.pan()
    T.ok(d0 and not T.temb('Confirmar dispensa') and 'Dispensar saldo: decisão de Ana (gestora e agrônoma).' in p and T.cen("c.ordens['OS-0421'].saldo") == 160,
         'dispensa aberta por Ana e perfil trocado para Caio: o formulário fecha e a linha diz quem decide; saldo segue 160 ha', p[-300:])
    T.fechar(); T.ordem('OS-0424'); p = T.pan()
    r = cmd("X.osc_cancelar(c,'OS-0424','teste',['','',''],{k:'Caio'})")
    T.ok(not T.temb('Cancelar sem execução') and 'Cancelar sem execução: decisão de Ana (gestora).' in p and T.cen("c.ordens['OS-0424'].etapa") == 'Liberadas'
         and r == 'Cancelar a OS-0424 sem execução (CMD-46): decisão de Ana (gestora). Nada foi alterado.',
         'Caio: sem "Cancelar sem execução" (CMD-46, AL-04: o gestor); a linha diz quem decide e o comando direto recusa; OS-0424 segue Liberadas', [r, p[-300:]])
    T.fechar(); perfil('Ana')
    er = T.erros(); T.ok(not er, 'sem erro de script', er)
except Exception as ex:
    T.ok(False, 'execução', ex)
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
