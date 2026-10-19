# Teste real (Chrome) — O.S.: clicar abre a tela da ordem com atividade, insumos e doses e o botão do próximo passo
# 01/10/2026 (decisões do proprietário):
#  - "Ajustar antes de liberar" também tira ("Tirar"/"Desfazer") e inclui produtos (#aj_inc + datalist #aj_prods + "Incluir"),
#    além de dose e área; "Salvar e liberar" segue igual. O teste confere o formulário e a ordem liberada com o ajuste.
# 19/10/2026 · LEVE-1 (leve, proprietário 19/10: "leve e fluido"): Iniciar execução e Enviar para conferência gravam no clique, sem o bloco "Confirmar …"; o oráculo passa a ser o recibo (aviso) e a fase.
#  - ordens só de água (OS-0419, OS-0422, OS-0423) não são O.S. agrícola: saem da página O.S.; as regras da água que este
#    teste conferia no painel da O.S. passam a ser conferidas onde vivem agora (IR-03 Ordens de irrigação e IR-03det = OS-0419).
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js; OK=[]; FAIL=[]
def chk(n,cond,info=''): (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ')+n+(' · '+str(info)[:220] if info!='' else ''))
# 01/10: o painel recolhe o que não faz a ordem andar na fase; o teste abre tudo antes de ler
def pan():
    if J('(()=>{const bs=[...document.querySelectorAll(\'aside[role=dialog] section[aria-label] > button[aria-expanded="false"]\')]; bs.forEach(b=>b.click()); return bs.length;})()'): time.sleep(.3)
    return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def btn(t,root='aside[role=dialog]'):
    r=J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root+' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def abrir(id_):
    J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.4)
def fechar(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
def setin(lab,val):
    J(f"(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)}); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"); time.sleep(.2)
def temb(t): return bool(J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
def fase_lista(id_): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def btnl(lab):   # botão pelo aria-label (Tirar/Desfazer de cada produto no ajuste)
    r=J(f"(()=>{{const b=document.querySelector('aside[role=dialog] button[aria-label={json.dumps(lab)}]'); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
def temlab(lab): return bool(J(f"!!document.querySelector('aside[role=dialog] button[aria-label={json.dumps(lab)}]')"))
def setid(sel,val):
    J(f"(()=>{{const i=document.querySelector({json.dumps(sel)}); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.25)
def alertas(): return J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
def ins(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const t=a.innerText; const i=t.indexOf('INSUMOS E DOSES'); const j=t.indexOf('RECURSOS ALOCADOS'); return i<0?'':t.slice(i,j<0?undefined:j).replace(/\\s+/g,' ');})()") or ''
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
AGUA=['OS-0419','OS-0422','OS-0423']   # 01/10: ordens só de água, fora da página O.S.
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.3)
    chk('sem erro JS', (J("window.__err||''") or '')=='')
    abrir('OS-0430'); t=pan()
    chk('clicar abre a tela da ordem', 'OS-0430' in t and 'PRÓXIMO PASSO' in t.upper())
    chk('atividade: operação, atividade e gatilho', 'Pulverização' in t and 'Dessecação pré-plantio' in t and 'DAP −20' in t, t[:300])
    chk('conjunto e horas previstas', 'Pulverizador PJ-3030' in t and '21,6 ha/h' in t and '7,4 h' in t, t)
    chk('insumos com dose e quantidade da ordem', 'Glifosato 480' in t and '2 L/ha' in t and '320 L' in t and '2,4-D 806' in t and '160 L' in t and 'Óleo mineral' in t and '80 L' in t, t)
    chk('dono e prazo da pendência na lista', 'Ana (agrônoma) · antes de 25/09' in fase_lista('OS-0430'), fase_lista('OS-0430'))
    # O.S. sem revisão (01/10): o agrônomo libera; com produto, pode ajustar dose e área antes
    chk('próximo passo: Liberar para execução e Ajustar antes de liberar, sem revisar/aprovar/rejeitar versão', temb('Liberar para execução') and temb('Ajustar antes de liberar')
        and not any(temb(x) for x in ('Revisar versão','Aprovar versão','Devolver para ajuste','Rejeitar')))
    btn('Ajustar antes de liberar'); setin('Dose de Glifosato 480 (L/ha)','0'); btn('Salvar e liberar'); t=pan()
    chk('ajustar: dose inválida fica junto ao campo e nada é liberado', 'Informe a dose maior que 0 L/ha.' in t and 'A liberar' in fase_lista('OS-0430'), t[-400:])
    # 01/10: o ajuste também tira e inclui produtos
    btnl('Tirar Óleo mineral da ordem'); t=pan()
    # 01/10: a linha tem o atalho "Agrofit ›" entre o nome e o total, então o texto é conferido pela linha do produto
    lin=J("(()=>{const g=document.querySelector('aside[role=dialog] [role=group][aria-label=\"Ajustar antes de liberar\"]'); const l=g&&[...g.querySelectorAll('label')].find(x=>x.innerText.trim()==='Óleo mineral'); const r=l&&l.closest('div'); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    tirou='sai da ordem' in lin and temlab('Manter Óleo mineral na ordem') and not temlab('Tirar Óleo mineral da ordem')
    btnl('Manter Óleo mineral na ordem'); t=pan()
    chk('ajustar: Tirar marca o produto que sai e Desfazer devolve à ordem', tirou and 'sai da ordem' not in t and temlab('Tirar Óleo mineral da ordem')
        and J("!!document.querySelector('aside[role=dialog] input[aria-label=\"Dose de Óleo mineral (L/ha)\"]')"), (tirou, t[t.find('Área da ordem'):][:220]))
    lst=J("(()=>{const i=document.querySelector('#aj_inc'); return i?i.getAttribute('list'):'';})()"); opts=J("[...document.querySelectorAll('#aj_prods option')].map(o=>o.value)") or []
    btn('Incluir'); e1=alertas(); setid('#aj_inc','Produto inexistente'); btn('Incluir'); e2=alertas()
    setid('#aj_inc','Adjuvante espalhante'); btn('Incluir'); t=pan()
    chk('ajustar: incluir produto da lista do cadastro (#aj_inc + #aj_prods), recusando vazio e fora do cadastro', lst=='aj_prods' and 'Adjuvante espalhante' in opts
        and 'Digite o nome do produto' in e1 and 'Produto não encontrado no cadastro' in e2 and 'Adjuvante espalhante incluído' in t
        and J("!!document.querySelector('aside[role=dialog] input[aria-label=\"Dose de Adjuvante espalhante (L/ha)\"]')") and temlab('Tirar Adjuvante espalhante'), (lst, len(opts), e1, e2, t[t.find('Área da ordem'):][:260]))
    btnl('Tirar Óleo mineral da ordem')
    btn('Voltar')
    btn('Liberar para execução'); t=pan()
    chk('liberar pede confirmação com reserva por lote (Voltar descartou o ajuste) e oferece ajustar antes', 'reserva no Estoque, por lote: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L' in t and 'Adjuvante espalhante' not in t and temb('Ajustar antes de liberar'), t[-400:])
    btn('Voltar'); chk('Voltar não muda a fase', fase_lista('OS-0430').find('A liberar')>=0)
    btn('Liberar para execução'); btn('Confirmar liberação'); t=pan(); tt=toast()
    chk('liberada: fase, toast e reserva', 'OS-0430 liberada' in tt and 'Liberadas' in fase_lista('OS-0430') and 'Reservado no Estoque' in t, (tt, fase_lista('OS-0430')))
    ST="window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"
    t=pan(); chk('sem insumo entregue, iniciar fica bloqueado e nomeia a entrega no Estoque', 'Iniciar bloqueado: REQ-041 sem entrega' in t and 'Rui (almoxarife) entrega no Estoque' in t
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"), t[:500])
    # Estoque entrega (outra tela, pelo cenário compartilhado): falta a confirmação no app
    J("(()=>{const X=window.__cen; const rq=X.cenGet().ordens['OS-0430'].req; X.cenMudar(null,c=>{ X.cenEntregar(c,rq,'Glifosato 480',320,'Marcos','Rui'); X.cenEntregar(c,rq,'2,4-D 806',160,'Marcos','Rui'); return X.cenEntregar(c,rq,'Óleo mineral',80,'Marcos','Rui'); }); "+ST+";})()"); time.sleep(.4)
    t=pan(); chk('entregue sem confirmação: iniciar bloqueado até o app confirmar', 'aguardando confirmação no app' in t and 'Marcos confirma o recebimento no app' in t
        and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"), t[:500])
    J("(()=>{const X=window.__cen; const rq=X.cenGet().ordens['OS-0430'].req; X.cenMudar(null,c=>X.cenConfirmarRecebimento(c,rq)); "+ST+";})()"); time.sleep(.4)
    chk('próximo passo agora é Iniciar execução', J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Iniciar execução')"))
    btn('Iniciar execução'); t=pan(); tt=toast()
    chk('Iniciar grava no clique (LEVE-1): o recibo diz que os insumos estão com Marcos, confirmados no app; sem bloco "Confirmar início"', 'OS-0430 em execução: insumos com Marcos, confirmados no app' in tt and not temb('Confirmar início'), (tt, t[-300:]))
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
    btn('Registrar apontamento'); setin('Data do turno','2026-09-27'); setin('Área feita em hectares','100'); btn('Salvar apontamento')   # CTL-2 · A: outro dia (o mesmo dia com outra chave fica em conferência de duplicidade)
    chk('saldo zero muda o botão para Enviar para conferência', J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Enviar para conferência')"))
    btn('Enviar para conferência'); tt=toast()
    chk('em conferência no clique (LEVE-1), com recibo de quem enviou e sem "Confirmar envio"', 'Em conferência' in fase_lista('OS-0430') and 'OS-0430 enviada para conferência por' in tt and not temb('Confirmar envio'), (tt, fase_lista('OS-0430')))
    btn('Conferir e encerrar'); btn('Confirmar encerramento'); t=pan()
    chk('encerrada, sem botão de ação', 'Encerradas' in fase_lista('OS-0430') and 'somente consulta' in t and not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>/Liberar|Ajustar|Iniciar|Registrar|Enviar|Conferir/.test(b.innerText))"))
    fechar()
    abrir('OS-0431'); t=pan()
    chk('falta de máquina: liberação recusa com causa e dono', 'Falta máquina · Trator T1 bloqueado' in t and 'Liberar bloqueado: Trator T1' in t and 'Quem resolve: PCP' in t
        and not temb('Liberar para execução') and temb('Ajustar antes de liberar'), t[:400])
    # 01/10: com a liberação impedida pela máquina, o agrônomo ainda ajusta produtos e doses; o botão só grava a versão (não libera)
    btn('Ajustar antes de liberar'); t2=pan()
    chk('falta de máquina: ajuste grava a versão sem liberar ("Salvar ajuste")', temb('Salvar ajuste') and not temb('Salvar e liberar') and 'a liberação continua impedida' in t2, t2[-300:])
    btn('Voltar')
    chk('plantio com semente e MAP pela dose', '52 kg/ha' in t and '5.304 kg' in t and '250 kg/ha' in t and '25.500 kg' in t, t)
    fechar(); abrir('OS-0417'); t=pan()
    # CTL-1 (Frente F): CA-02 é oculta e fixa; o painel fica com o atalho vivo ao Estoque
    chk('conferência bloqueada por sobras com atalho ao Estoque e sem elo para CA-02 (oculta e fixa)', 'Encerrar bloqueado' in t and J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>a.getAttribute('href')==='EST.dc.html')") and not J("[...document.querySelectorAll('aside[role=dialog] a')].some(a=>(a.getAttribute('href')||'').startsWith('CA-02'))"), t[:300])
    fechar()
    # 01/10: água sem produto não é O.S. agrícola: OS-0419/OS-0422/OS-0423 não abrem mais aqui (regras conferidas na IR-03/IR-03det, abaixo)
    corpo=J("document.body.innerText") or ''
    chk('ordens só de água fora da página O.S.: sem OS-0419, OS-0422 e OS-0423 na lista e no texto', not any(x in ids() or x in corpo for x in AGUA) and 'OS-0418' in ids(), [x for x in AGUA if x in corpo])
    abrir('OS-0421'); btn('Registrar apontamento')
    chk('apontamento sugere o previsto do dia (50 ha)', J("[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==='Área feita em hectares').value")=='50')
    btn('Cancelar'); fechar(); abrir('OS-0425'); t=pan()
    chk('entrega parcial avisa no próximo passo', 'cobre 26,7 dos 38 ha' in t and '11.400 kg' in t)
    fechar()
    J("document.querySelector('[data-visao=kanban]').click()"); time.sleep(.4)   # VISOES-1: pelo seletor (data-visao)
    J("(()=>{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(x=>x.innerText.indexOf('OS-0424')===0); k&&k.click();})()"); time.sleep(.4); t=pan()
    chk('cartão do Kanban abre a mesma tela', 'OS-0424' in t and 'Fungicida A' in t and '0,5 L/ha' in t and '64 L' in t, t[:200])   # G1 do CTL-1: 0,5 L/ha × 128 ha no T1-B (antes 0,8 × 80 no milho do P2)
    c.shot(os.path.join(HERE,'_probe','os_tela.png'))
    # 01/10: ajuste que tira e inclui produto, salvo e liberado — cenário limpo (a OS-0430 acima já foi encerrada)
    fechar(); J("document.querySelector('[data-visao=lista]').click()")
    J("try{localStorage.removeItem('talhao-os-cenario-v1')}catch(e){}"); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.3)
    abrir('OS-0430'); btn('Ajustar antes de liberar'); btnl('Tirar Óleo mineral da ordem'); setid('#aj_inc','Adjuvante espalhante'); btn('Incluir')
    btn('Salvar e liberar'); e=alertas()
    setin('Dose de Adjuvante espalhante (L/ha)','0,2'); btn('Salvar e liberar'); tt=toast(); t=pan()
    chk('Salvar e liberar com produto tirado e incluído: dose do incluído é obrigatória; libera a v2 reservando só o que ficou',
        'Informe a dose maior que 0 L/ha.' in e and 'OS-0430 ajustada para v2 e liberada' in tt and 'Adjuvante espalhante 32 L' in tt and 'Óleo mineral' not in tt
        and 'Liberadas' in fase_lista('OS-0430') and 'tirado Óleo mineral; incluído Adjuvante espalhante 0,2 L/ha' in t, (e, tt))
    i=ins()
    chk('insumos e doses da ordem liberada mostram o ajuste: Adjuvante espalhante 0,2 L/ha · 32 L reservado, sem Óleo mineral', 'Adjuvante espalhante' in i and '0,2 L/ha' in i and '32 L' in i and 'Óleo mineral' not in i, i)
    chk('sem erro JS no fim', (J("window.__err||''") or '')=='')
    # 01/10: regras da água conferidas onde ela vive agora (Irrigação)
    c.goto(f'http://127.0.0.1:{p}/IR-03.dc.html',wait=1.3)
    lin=lambda id_: J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    acao=lambda id_: J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); const a=r&&[...r.querySelectorAll('a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    # 03/10 (Irrigação v43): a linha da ordem abre o detalhe; a ação mora no detalhe (IR-03det#OS-…) e a fertirrigação abre na O.S.
    abre=lambda id_: (J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r&&r.click(); return !!r;}})()"), time.sleep(1.2), J("location.href.split('/').pop()"))[2]
    l22=lin('OS-0422').lower(); l18=lin('OS-0418')
    u22=abre('OS-0422'); t22=(J("document.body.innerText") or '').replace('\n',' ')
    bt22=J("[...document.querySelectorAll('button,a')].map(b=>b.innerText.trim())") or []
    chk('IR-03: OS-0422 só água em A liberar com Janela a definir; a linha abre IR-03det#OS-0422 com Definir janela, sem agrônomo nem Liberar na O.S.', 'água' in l22 and 'a liberar' in l22 and 'janela a definir' in l22
        and 'agrônom' not in l22 and u22=='IR-03det.dc.html#OS-0422' and 'Definir janela' in bt22 and 'Liberar na O.S.' not in bt22 and 'agrônom' not in t22[t22.find('OS-0422 · Irrigação'):][:400], (l22, u22))
    c.goto(f'http://127.0.0.1:{p}/IR-03.dc.html',wait=1.3)
    u18=abre('OS-0418'); t18=(J("document.body.innerText") or '').replace('\n',' ')
    chk('IR-03: fertirrigação OS-0418 abre na página O.S. para o agrônomo (Ajustar antes de liberar), com o mesmo impedimento de Estoque', 'Falta insumo' in l18 and u18=='OS.dc.html#OS-0418'
        and 'O agrônomo confere' in t18 and J("[...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Ajustar antes de liberar')"), (l18, u18))
    c.goto(f'http://127.0.0.1:{p}/IR-03det.dc.html',wait=1.3)
    t=(J("document.body.innerText") or '').replace('\n',' ')
    chk('IR-03det (OS-0419): água sem produtos (nenhuma requisição ou custódia na tela); próxima ação Iniciar irrigação', 'OS-0419' in t and 'REQ-' not in t and 'custódia' not in t.lower()
        and J("[...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Iniciar irrigação')"), t[:200])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
