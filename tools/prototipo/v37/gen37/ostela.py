# Teste real (Chrome) — O.S.: clicar abre a tela da ordem com atividade, insumos e doses e o botão do próximo passo
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:220] if info!='' else ''))
def pan(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def btn(t,root='aside[role=dialog]'):
    r=J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root+' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def abrir(id_):
    J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.4)
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def setin(lab,val):
    J(f"(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)}); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"); time.sleep(.2)
def fase_lista(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.3)
    chk('sem erro JS', (J("window.__err||''") or '')=='')
    abrir('OS-0430'); t=pan()
    chk('clicar abre a tela da ordem', 'OS-0430' in t and 'PRÓXIMO PASSO' in t.upper())
    chk('atividade: operação, atividade e gatilho', 'Pulverização' in t and 'Dessecação pré-plantio' in t and 'DAP −20' in t, t[:300])
    chk('conjunto e horas previstas', 'Pulverizador PJ-3030' in t and '21,6 ha/h' in t and '7,4 h' in t, t)
    chk('insumos com dose e quantidade da ordem', 'Glifosato 480' in t and '2 L/ha' in t and '320 L' in t and '2,4-D 806' in t and '160 L' in t and 'Óleo mineral' in t and '80 L' in t, t)
    chk('dono e prazo da pendência na lista', 'Ana (agrônoma) · antes de 25/09' in fase_lista('OS-0430'), fase_lista('OS-0430'))
    chk('botão do próximo passo: Revisar versão', J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Revisar versão')"))
    btn('Revisar versão'); btn('Rejeitar')
    chk('rejeitar exige motivo', 'Informe o motivo.' in pan())
    btn('Aprovar versão'); tt=toast(); t=pan()
    chk('aprovar não libera', 'ainda não foi liberada' in tt and 'A liberar' in fase_lista('OS-0430') and 'Aprovada pelo agrônomo' in fase_lista('OS-0430'), (tt,fase_lista('OS-0430')))
    btn('Liberar para execução'); t=pan()
    chk('liberar pede confirmação com reserva por lote', 'reserva no Estoque, por lote: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L' in t, t[-400:])
    btn('Voltar'); chk('Voltar não muda a fase', fase_lista('OS-0430').find('A liberar')>=0)
    btn('Liberar para execução'); btn('Confirmar liberação'); t=pan(); tt=toast()
    chk('liberada: fase, toast e reserva', 'OS-0430 liberada' in tt and 'Liberadas' in fase_lista('OS-0430') and 'Reservado no Estoque' in t, (tt, fase_lista('OS-0430')))
    ST="window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"
    t=pan(); chk('sem insumo entregue, iniciar fica bloqueado e nomeia a entrega no Estoque', 'Iniciar bloqueado: REQ-041 sem entrega' in t and 'Rui (almoxarife) entrega no Estoque' in t
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"), t[:500])
    # Estoque entrega (outra tela, pelo cenário compartilhado): falta a confirmação no app
    J("(()=>{const X=window.__cen; const rq=X.cenGet().ordens['OS-0430'].req; X.cenMudar(null,c=>{ X.cenEntregar(c,rq,'Glifosato 480',320,'Marcos'); X.cenEntregar(c,rq,'2,4-D 806',160,'Marcos'); return X.cenEntregar(c,rq,'Óleo mineral',80,'Marcos'); }); "+ST+";})()"); time.sleep(.4)
    t=pan(); chk('entregue sem confirmação: iniciar bloqueado até o app confirmar', 'aguardando confirmação no app' in t and 'Marcos confirma o recebimento no app' in t
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"), t[:500])
    J("(()=>{const X=window.__cen; const rq=X.cenGet().ordens['OS-0430'].req; X.cenMudar(null,c=>X.cenConfirmarRecebimento(c,rq)); "+ST+";})()"); time.sleep(.4)
    chk('próximo passo agora é Iniciar execução', J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"))
    btn('Iniciar execução'); t=pan()
    chk('confirmação do início diz que os insumos estão com Marcos, confirmados no app', 'insumos com Marcos, confirmados no app' in t, t[-300:])
    btn('Confirmar início')
    chk('em execução', 'Em execução' in fase_lista('OS-0430'), fase_lista('OS-0430'))
    btn('Registrar apontamento'); t=pan()
    chk('formulário de apontamento com saldo', 'Saldo da ordem: 160 ha' in t)
    setin('Área feita em hectares','200'); btn('Salvar apontamento')
    chk('bloqueia área acima do saldo', 'Máximo 160 ha: é o saldo da ordem.' in pan())
    setin('Área feita em hectares','60')
    btn('Salvar apontamento'); tt=toast(); t=pan()
    chk('apontamento de 60 ha com insumos usados', 'Apontamento do dia 1: 60 ha' in tt and 'Glifosato 480 120 L' in tt and 'continua em execução' in tt, tt)
    chk('ordem continua em execução, saldo 100', 'Em execução' in fase_lista('OS-0430') and '60 / 160 ha' in fase_lista('OS-0430'), fase_lista('OS-0430'))
    chk('coluna Usado atualiza (120 L)', '120 L' in t)
    btn('Registrar apontamento'); setin('Área feita em hectares','100'); btn('Salvar apontamento')
    chk('saldo zero muda o botão para Enviar para conferência', J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Enviar para conferência')"))
    btn('Enviar para conferência'); btn('Confirmar envio')
    chk('em conferência', 'Em conferência' in fase_lista('OS-0430'))
    btn('Conferir e encerrar'); btn('Confirmar encerramento'); t=pan()
    chk('encerrada, sem botão de ação', 'Encerradas' in fase_lista('OS-0430') and 'somente consulta' in t and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>/Aprovar|Iniciar|Registrar|Enviar|Conferir/.test(b.innerText))"))
    fechar()
    abrir('OS-0431'); t=pan()
    chk('aprovada pelo agrônomo com falta de máquina: sem nova revisão, liberação recusa com causa e dono', 'Aprovada pelo agrônomo' in t and 'Falta máquina · Trator T1 bloqueado' in t and 'Liberar bloqueado: Trator T1' in t and 'Quem resolve: PCP' in t
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>['Liberar para execução','Revisar versão'].includes(b.innerText.trim()))"), t[:400])
    chk('plantio com semente e MAP pela dose', '52 kg/ha' in t and '5.304 kg' in t and '250 kg/ha' in t and '25.500 kg' in t, t)
    fechar(); abrir('OS-0417'); t=pan()
    chk('conferência bloqueada por sobras com atalho ao Estoque e à conferência', 'Encerrar bloqueado' in t and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='EST.dc.html')") and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='CA-02.dc.html')"), t[:300])
    fechar(); abrir('OS-0422'); t=pan()
    chk('irrigação só água (26/09): próximo passo Definir janela com João e atalho à Irrigação, sem agrônomo', 'Definir janela' in t and 'João (irrigante)' in t and 'agrônom' not in t
        and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='IR-02.dc.html'&&a.innerText.indexOf('Definir janela')===0)")
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>['Revisar versão','Liberar para execução'].includes(b.innerText.trim()))"), t[:400])
    fechar(); abrir('OS-0421'); btn('Registrar apontamento')
    chk('apontamento sugere o previsto do dia (50 ha)', J("[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==='Área feita em hectares').value")=='50')
    btn('Cancelar'); fechar(); abrir('OS-0419'); t=pan()
    chk('irrigação: água, sem almoxarifado', 'sem almoxarifado' in t and 'Iniciar execução' in t)
    fechar(); abrir('OS-0425'); t=pan()
    chk('entrega parcial avisa no próximo passo', 'cobre 26,7 dos 38 ha' in t and '11.400 kg' in t)
    fechar()
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Kanban'); b&&b.click();})()"); time.sleep(.4)
    J("(()=>{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(x=>x.innerText.indexOf('OS-0424')===0); k&&k.click();})()"); time.sleep(.4); t=pan()
    chk('cartão do Kanban abre a mesma tela', 'OS-0424' in t and 'Fungicida A' in t and '0,8 L/ha' in t and '64 L' in t, t[:200])
    c.shot(os.path.join(HERE,'_probe','os_tela.png'))
    chk('sem erro JS no fim', (J("window.__err||''") or '')=='')
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
