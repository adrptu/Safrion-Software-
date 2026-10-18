# -*- coding: utf-8 -*-
"""N-1/B-3 (EX-51, PR #113 + composição do Claude): fluxo real no navegador, com o armazenamento real do navegador.
AG-01 emite pela tela (autor, chave e versão) → O.S., DIA, REC/RA, decisão e recibo numa só gravação do cenário → a O.S. libera;
divergência entre O.S. e receituário: a tela diz antes do clique e os comandos recusam (O.S. e portas de grupo); cópia antiga do MIP migra
uma vez ao abrir e não volta depois de restaurar; cópia ilegível não derruba as telas e tem saída; o app de campo (MB-06) grava.
Limites: o grupo com a O.S. do MIP depende do pulverizador alocado pelo PCP; aqui se prova só a recusa da composição antes da alocação
(as portas do grupo com o receituário estão no n1_recipe_test.cjs);
concorrência entre abas fora do escopo (pendente no contrato). Uso: RENDER_DIR=<_render> python3 n1_fluxo_test.py"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.environ.get('RENDER_DIR') or os.path.join(HERE,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:700]))
try:
    for _i in range(4):
        try: c=Chrome(port=free()); break
        except Exception: time.sleep(2)
    J=c.js; c.size(1440,900); U=f'http://127.0.0.1:{p}/'
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));window.addEventListener('unhandledrejection',e=>window.__errs.push(String(e.reason)));"})   # erro de página derruba a tela: o teste vê
    CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
    SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
    def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
    def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.35); return r
    def ir(pg,w=1.4): c.goto(U+pg,wait=w)
    JX=lambda s: J("(()=>{try{return "+s.strip()+"}catch(e){return {__erro:String(e&&e.message||e)}}})()")   # erro do JS volta no resultado (vira FALHA com a causa)
    def ir_hash(pg): ir(pg,1.6); time.sleep(.4)
    def recarrega(pg): ir(pg,1.6); J('location.reload()'); time.sleep(1.8)   # mesma URL com # não recarrega a página: força a leitura nova do cenário
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    aside=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    corpo=lambda: J("document.body.innerText") or ''
    limpa=lambda: J("localStorage.clear(); sessionStorage.clear()")
    ir('Main.dc.html',0.8); limpa()
    # leitura do cenário pela chave que o próprio mip.js expõe (window.__mip.chaves), sem repetir a chave no teste
    CEN="JSON.parse(localStorage.getItem(window.__mip.chaves.cen)||'null')"
    # N1 · emissão pela tela: uma gravação com O.S., DIA, REC/RA, decisão v1 e recibo; autor do perfil; sem tocar a chave antiga
    ir_hash('AG-01.dc.html#VIS-013:decidir'); J("[...document.querySelectorAll('aside input[name=dc_prod]')][0].click()"); time.sleep(.3)
    setv('aside #dc_dose','0,5'); setv('aside input[aria-label="Data da aplicação"]','2026-09-24'); clk('Emitir receituário e gerar O.S.','aside'); t1=T()
    e=JX(f"""(()=>{{ const c={CEN}, m=c&&c.mip||null; const o=c&&Object.values(c.ordens).find(x=>x.osc&&x.osc.novo&&x.osc.novo.mip&&x.osc.novo.mip.vis==='VIS-013');
      const v=m&&m.vis['VIS-013']; const ch=Object.keys((c&&c.recibos)||{{}}).filter(k=>k.indexOf('MIP-EMI-VIS-013-v1-')===0);
      return {{os:o?o.id:null, etapa:o?o.etapa:null, recOs:(m&&o&&m.rec[o.osc.novo.mip.rec]||{{}}).os, ver:v&&v.dec?v.dec.ver:null, por:v&&v.dec?v.dec.por:null,
        chaves:ch, comResultado:ch.length===1&&!!c.recibos[ch[0]].resultado, migrado:!!(m&&m.migradoDe), antiga:localStorage.getItem(window.__mip.chaves.mip)}}; }})()""") or {}
    OS=e.get('os') or 'OS-0440'
    chk('N1 AG-01 emite pela tela: O.S. em A liberar com o REC ligado a ela, decisão v1 com autor, 1 recibo MIP-EMI-VIS-013-v1-… com resultado, MIP no cenário; a chave antiga não é criada',
        e.get('os') and e.get('etapa')=='A liberar' and e.get('recOs')==OS and e.get('ver')==1 and (e.get('por') or '').startswith('Ana') and e.get('comResultado') and e.get('migrado') and e.get('antiga') is None
        and 'emitido' in t1, [e,t1])
    # N2 · repetir a mesma intenção (mesma chave e conteúdo) devolve o recibo, sem O.S. nova
    r2=JX(f"""(()=>{{ const c={CEN}, k=Object.keys(c.recibos).find(x=>x.indexOf('MIP-EMI-VIS-013-v1-')===0), d=c.mip.vis['VIS-013'].dec, n0=Object.keys(c.ordens).length;
      const r=window.__mip.mipEmitir(null,'VIS-013',{{kind:'controlar',prod:d.prod,dose:'0,5',area:String(d.area),data:'2026-09-24',ator:'Ana',chave:k,dver:1}});
      return {{rep:!!r.repetido, os:r.os, erro:r.erro||'', n:Object.keys({CEN}.ordens).length-n0}}; }})()""") or {}
    chk('N2 a mesma chave com o mesmo conteúdo devolve o recibo (repetido, mesma O.S.) e não cria outra', r2.get('rep') and r2.get('os')==OS and r2.get('n')==0 and not r2.get('erro'), r2)
    # N3 · O.S. coerente com o receituário: o painel segue para liberar, sem aviso de receituário
    ir_hash('OS.dc.html#'+OS); a=aside()
    chk('N3 OS.dc.html#'+OS+': em A liberar, sem "Receituário divergente" (o que segura a liberação, se houver, é o Estoque)', 'A liberar' in a and 'Receituário divergente' not in a, a[:400])
    # N4 · divergência gravada por fora (dose 0,5 → 0,6): a tela diz antes do clique e os comandos recusam sem efeito
    JX(f"window.__cen.cenMudar(null,k=>{{ k.ordens['{OS}'].ins[0].dose=0.6; return {{msg:''}}; }})"); recarrega('OS.dc.html#'+OS); a=aside(); lista=corpo()
    q4=JX(f"""(()=>{{ const C=window.__cen, n0=Object.keys(C.cenGet().reqs||{{}}).length;
      const rl=C.cenMudar(null,k=>C.osc_liberar(k,'{OS}',false,'','Ana')), ra=C.cenMudar(null,k=>C.osc_aprovar(k,'{OS}','Ana')); const o=C.cenGet().ordens['{OS}'];
      return {{lib:rl.erro||'', apr:ra.erro||'', etapa:o.etapa, aprov:!!o.aprov, reqs:Object.keys(C.cenGet().reqs||{{}}).length-n0}}; }})()""") or {}
    chk('N4 dose da O.S. diferente do receituário: painel "Liberar e aprovar bloqueados: receituário divergente…" com o caminho para Pragas e doenças; selo na lista; liberar e aprovar recusam; segue em A liberar, sem aprovação nem requisição nova',
        'Liberar e aprovar bloqueados: receituário divergente' in a and 'Pragas e doenças' in a and 'Receituário divergente' in lista
        and 'Receituário divergente' in q4.get('lib','') and 'Receituário divergente' in q4.get('apr','') and q4.get('etapa')=='A liberar' and q4.get('aprov') is False and q4.get('reqs')==0, [a[:500],q4])
    # N5 · grupo no fluxo real: a O.S. recém-emitida pelo MIP não tem pulverizador alocado, e a composição do grupo recusa antes de qualquer gravação.
    #      A recusa do receituário nas portas do grupo (cenGrupoAprovar/cenGrupoLiberar com a fonte real) está no n1_recipe_test.cjs.
    g=JX(f"""(()=>{{ const C=window.__cen, n0=Object.keys(C.cenGet().gruposExec||{{}}).length;
      C.cenMudar(null,k=>{{ const o=JSON.parse(JSON.stringify(k.ordens['{OS}'])), n=o.osc.novo; o.id='OS-0499'; o.talhao='P2'; n.id='OS-0499'; n.talhao='P2'; n.keys=['mip|VIS-N1B|x']; n.mip=Object.assign({{}},n.mip,{{vis:'VIS-N1B'}}); k.ordens['OS-0499']=o; return {{msg:''}}; }});
      const cr=C.cenMudar(null,k=>{{ const pv=C.cenGrupoPrevia(k,['{OS}','OS-0499'],'Ana'); return C.cenGrupoCriar(k,pv,'Ana','N1-G-CRIAR'); }});
      C.cenMudar(null,k=>{{ delete k.ordens['OS-0499']; return {{msg:''}}; }});
      return {{criar:cr.erro||'', grupos:Object.keys(C.cenGet().gruposExec||{{}}).length-n0, etapa:C.cenGet().ordens['{OS}'].etapa}}; }})()""") or {}
    chk('N5 grupo: com a O.S. do MIP ainda sem pulverizador, a composição recusa ("Sem conjunto"), nenhum grupo é gravado e a O.S. segue em A liberar',
        'Sem conjunto' in g.get('criar','') and g.get('grupos')==0 and g.get('etapa')=='A liberar', g)
    # N6 · corrigida a dose (volta ao receituário), a O.S. libera pelo comando real (ou para só no estoque, nunca no receituário)
    JX(f"window.__cen.cenMudar(null,k=>{{ k.ordens['{OS}'].ins[0].dose=0.5; Object.keys(k.gruposExec||{{}}).forEach(id=>{{ if((k.gruposExec[id].ids||[]).includes('{OS}')) delete k.gruposExec[id]; }}); return {{msg:''}}; }})"); recarrega('OS.dc.html#'+OS); a=aside()
    l6=JX(f"(()=>{{ const C=window.__cen; const r=C.cenMudar(null,k=>C.osc_liberar(k,'{OS}',false,'','Ana')); return {{erro:r.erro||'', etapa:C.cenGet().ordens['{OS}'].etapa}}; }})()") or {}
    chk('N6 de volta à dose do receituário: o painel deixa de acusar o receituário e a liberação passa da trava B-3 (para só no Estoque, sem lote do produto na demonstração)',
        'Receituário divergente' not in a and 'Receituário' not in l6.get('erro','') and (l6.get('etapa')=='Liberadas' or 'Estoque' in l6.get('erro','')), [a[:300],l6])
    # N7 · cópia antiga: migra ao abrir uma tela de Pragas e doenças, uma vez, sem alterar a cópia
    ir('AG-01.dc.html'); limpa(); JX("(()=>{ const s=window.__mip.mipGet(); s.rev=41; s.vis['VIS-013'].nota='LEGADO-N1'; localStorage.setItem(window.__mip.chaves.mip,JSON.stringify(s)); return 1; })()")
    leg0=J("localStorage.getItem(window.__mip.chaves.mip)"); ir('AG-01.dc.html')
    m7=JX(f"(()=>{{ const c={CEN}; return c&&c.mip?{{nota:c.mip.vis['VIS-013'].nota, rev:(c.mip.migradoDe||{{}}).rev, marca:localStorage.getItem(window.__mip.chaves.marca)!==null}}:null; }})()")
    chk('N7 abrir o AG-01 com a cópia antiga leva-a ao cenário (migradoDe.rev 41) e marca a migração; a cópia antiga fica igual',
        m7 and m7.get('nota')=='LEGADO-N1' and m7.get('rev')==41 and m7.get('marca') and J("localStorage.getItem(window.__mip.chaves.mip)")==leg0, m7)
    # N8 · Restaurar demonstração em outra tela (cenReset) não traz a cópia antiga de volta
    ir('OS.dc.html'); J("window.__cen.cenReset()"); ir('AG-01.dc.html'); n8=J("window.__mip.mipGet().vis['VIS-013'].nota||''")
    chk('N8 depois de restaurar o cenário (outra tela), o AG-01 mostra a semente, não a cópia antiga', n8!='LEGADO-N1', n8)
    # N9 · cópia antiga ilegível: AG-01, Mapa e app abrem; o AG-01 diz o que houve e oferece restaurar; restaurar resolve e preserva a cópia
    limpa(); J("localStorage.setItem(window.__mip.chaves.mip,'{ilegivel')"); ir('AG-01.dc.html'); b=corpo(); hd=J("(document.querySelector('header')||{innerText:''}).innerText") or ''
    ir('IN-04.dc.html',2.5); mapa_ok=J("window.__errs.length===0&&document.querySelectorAll('svg').length>0"); c.size(390,940); ir('MB-06.dc.html#VIS-017'); app_ok=len(corpo())>50; c.size(1440,900)
    ir('AG-01.dc.html'); r9=clk('Restaurar demonstração'); time.sleep(.6); b2=corpo(); leg=J("localStorage.getItem(window.__mip.chaves.mip)")
    chk('N9 cópia ilegível: AG-01 com "Dados ilegíveis" e "Restaurar demonstração" (lista vazia), Mapa e app abrem; restaurar volta as vistorias e a cópia segue intacta',
        'Dados ilegíveis' in hd and 'nada é gravado até restaurar a demonstração' in b and 'VIS-05' not in b and mapa_ok and app_ok and r9=='ok' and 'VIS-05' in b2 and leg=='{ilegivel',
        [hd[:200],b[b.find('Pragas e doenças'):][:400],mapa_ok,app_ok,r9,('VIS-05' in b2),leg])
    # N10 · app de campo (MB-06) grava a coleta no cenário (antes: tela sem cenario.js recusava)
    limpa(); c.size(390,940); ir('MB-06.dc.html#VIS-017'); setv('#mb_cont','3,5'); r10=clk('Registrar e ir ao ponto 2'); t10=T()
    p10=JX(f"(()=>{{ const c={CEN}; const v=c&&c.mip&&c.mip.vis['VIS-017']; return v?v.pts[0].v:null; }})()"); c.size(1440,900)
    chk('N10 MB-06 registra o ponto 1 da VIS-017 (3,5) no cenário, sem erro de gravação', r10=='ok' and p10==3.5 and 'indisponível' not in t10 and 'Não foi possível gravar' not in t10, [r10,t10,p10])
    limpa()
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print('RESULTADO', f'{len(OK)}/{len(OK)+len(FAIL)}')
sys.exit(1 if FAIL else 0)
