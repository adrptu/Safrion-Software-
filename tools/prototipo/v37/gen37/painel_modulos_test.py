# -*- coding: utf-8 -*-
"""PAINEL-01: oráculos explícitos e UI real isolada. python3 painel_modulos_test.py [--ui].
Dados sintéticos. Sem alterar cenários do usuário. --ui requer build + montar_render.
"""
import os, sys, json, subprocess, tempfile, time
from pathlib import Path
os.environ.setdefault('SAFRION_DADOS','sintetico')
from areas import paineis as P
import cenario
import dados_manutencao as DM
TEST = r'''
const assert=require('node:assert/strict'); let n=0;
function chk(nome,actual,expected){assert.deepEqual(actual,expected,nome);console.log('OK '+nome);n++;}
const c={ordens:{a:{id:'OS-1',etapa:'A liberar'},b:{id:'OS-2',etapa:'Liberadas'},c:{id:'OS-3',etapa:'Em execução'},d:{id:'OS-4',etapa:'Em execução'},e:{id:'OS-5',etapa:'Em conferência'},f:{id:'OS-6',etapa:'Encerradas'},g:{id:'OS-7',etapa:'Canceladas'},ben:{id:'OB-1',fam:'BEN',etapa:'Em execução'}},lotes:{a:{fisico:100,reservado:30,quarentena:20},b:{fisico:10,reservado:10,quarentena:0},c:{fisico:80,reservado:0,quarentena:0},d:{fisico:0,reservado:0,quarentena:0}},reqs:{
 r1:{os:'b',itens:[{solicitado:20,consumido:5,custodia:15}]},
 r2:{os:'c',itens:[{solicitado:20,consumido:5,custodia:10}]},
 r3:{os:'d',itens:[{solicitado:20,consumido:20,custodia:0},{solicitado:1,consumido:0,custodia:0}]},
 r4:{os:'g',itens:[{solicitado:100,consumido:0,custodia:0}]},
 r5:{os:'a',itens:[{solicitado:100,consumido:0,custodia:0}]}}};
const before=JSON.stringify(c);
chk('Agrícola: quatro estados; não conta cancelada, encerrada nem BEN',pnValores(c,'PAGR').vals,[1,1,2,1]);
chk('Suprimentos: lote sobreposto conta nos indicadores pertinentes; requisição por registro, item coberto e cancelada excluídos',pnValores(c,'PSUP').vals,[3,2,1,2]);
chk('Gráfico de estoque: cada lote físico conta uma só vez',pnValores(c,'PSUP').bars,[1,1,1]);
chk('Painéis não alteram cenário',JSON.stringify(c),before);
const m={hoje:'2026-10-13',horiz:7,achados:{},ativos:{a:{id:'a',cond:'Bloqueado',un:'h',leit:null,ritmo:0},b:{id:'b',cond:'Disponível'}},planos:{p:{id:'p',versao:1,estado:'Ativo',servicos:[{id:'s',nome:'Revisão',gat:{d:10},tol:{d:0}}]}},vinc:{'p|a':{marco:{data:'2026-10-01',leit:null}}},oms:{a:{etapa:'A liberar'},b:{etapa:'Liberadas'},c:{etapa:'Em execução'},d:{etapa:'Em conferência'},e:{etapa:'Encerradas'},f:{etapa:'Canceladas'}}};
c.man=m;
chk('Manutenção: serviço vencido sem ordem; quatro abertas, uma executando e um ativo bloqueado',pnValores(c,'PMAN').vals,[1,4,1,1]);
chk('Gráfico manutenção: fases abertas',pnValores(c,'PMAN').bars,[1,1,1,1]);
m.planos.p.estado='Inativo';chk('Plano inativo não cria pendência',pnValores(c,'PMAN').vals[0],0);
m.planos.p.estado='Ativo';m.vinc['p|a'].marco.data='2026-11-01';chk('Próxima revisão fora da janela não cria pendência',pnValores(c,'PMAN').vals[0],0);
for(const k of ['PAGR','PMAN','PSUP'])chk(k+' ausente nunca vira zero',pnValores({},k).vals,[null,null,null,null]);
// MAN-SEMORDEM-01 (revisão Codex 6161081449): a lista Sem ordem depende dos achados; sem a coleção, Sem dados (os outros indicadores seguem)
const sd=cenClone(CEN0), n0=pnValores(sd,'PMAN').vals[0], nv=manSemOrdem(sd.man).n;
chk('Sem ordem com o seed: a mesma conta da visão (manSemOrdem)',[n0===nv,n0>0],[true,true]);
const nAch=Object.values(sd.man.achados).filter(q=>q.estado==='Sem ordem'&&sd.man.ativos[q.aid]).length;
sd.man.achados={};chk('Sem ordem com achados vazios (coleção válida): só os vencimentos',pnValores(sd,'PMAN').vals[0],n0-nAch);
delete sd.man.achados;const va=pnValores(sd,'PMAN').vals;chk('Sem ordem sem a coleção de achados: Sem dados, e os demais indicadores seguem',[va[0],va.slice(1).every(x=>x!==null)],[null,true]);
sd.man.achados={x:{estado:null}};chk('Achado sem estado: Sem dados',pnValores(sd,'PMAN').vals[0],null);
chk('Coleções vazias válidas: zero agrícola',pnValores({ordens:{}},'PAGR').vals,[0,0,0,0]);
chk('Coleções vazias válidas: zero suprimentos',pnValores({ordens:{},lotes:{},reqs:{}},'PSUP').vals,[0,0,0,0]);
c.lotes.a.fisico=null;chk('Saldo físico ausente não produz total parcial',pnValores(c,'PSUP').vals.slice(0,3),[null,null,null]);
c.reqs.r2.itens[0].custodia=null;chk('Custódia ausente não vira demanda falsa',pnValores(c,'PSUP').vals[3],null);
c.ordens.c.etapa=null;chk('Estado ausente impede contagem parcial de O.S.',pnValores(c,'PAGR').vals,[null,null,null,null]);
// PAINEL-02 · agrPainelRef (contrato 6163002343/6163029779; revisão Codex 6163287732: projeção da O.S. e recorte)
const ag=cenClone(CEN0), antes=JSON.stringify(ag), r0=agrPainelRef(ag);
chk('agrPainelRef: não muda o estado (JSON igual antes e depois)',JSON.stringify(ag),antes);
chk('agrPainelRef: seed = OS-0418 e OS-0502 (falta insumo no Estoque), OS-0420 (ativo bloqueado), OS-0431 (falta máquina), OS-0507 (bomba)',r0.os.impedidas.map(x=>[x.id,x.dono]),[['OS-0418','Suprimentos'],['OS-0420','Manutenção'],['OS-0431','PCP'],['OS-0502','Suprimentos'],['OS-0507','Manutenção']]);
chk('agrPainelRef: mesma lista e mesmo motivo que a projeção da tela O.S. (osProjecao + OS_IMP_RE)',r0.os.impedidas.map(x=>[x.id,x.motivo]),
 osProjecao(ag).filter(o=>!/^OB-/.test(o.id)&&!['Encerradas','Canceladas'].includes(o.etapa)).map(o=>[o.id,(o.selos.find(s=>OS_IMP_RE.test(s.t))||{}).t]).filter(x=>x[1]));
chk('agrPainelRef: origem na O.S. e n confere',[r0.os.impedidas[0].origem,r0.os.n.impedidas],['OS.dc.html#OS-0418',5]);
chk('agrPainelRef: cada impedida traz fazenda e safra do registro',r0.os.impedidas.map(x=>[x.id,x.faz,x.saf]),[['OS-0418','Santa Rita','2026/27'],['OS-0420','Santa Rita','2026/27'],['OS-0431','Santa Rita','2026/27'],['OS-0502','Lagoa Grande','2026/27'],['OS-0507','Lagoa Grande','2026/27']]);
chk('agrPainelRef: hoje 23/09 (D2.HOJE_ISO) = nenhuma atrasada, nenhuma sem prazo; custos null; desde null',[r0.os.atrasadas,r0.os.n.atrasadas,r0.os.n.sem_prazo,r0.custos,r0.os.impedidas.every(x=>x.desde===null)],[[],0,0,null,true]);
{ const h0=OSD.hoje; OSD.hoje='2026-09-25'; const ra=agrPainelRef(cenClone(CEN0));
  chk('agrPainelRef: hoje 25/09 → atrasadas = abertas com fim antes de hoje (Em conferência fora)',ra.os.atrasadas.map(x=>[x.id,x.etapa,x.prevista,x.dias]),
   [['OS-0424','Liberadas','2026-09-24',1],['OS-0431','A liberar','2026-09-24',1],['OS-0505','Em execução','2026-09-24',1],['OS-0506','Em execução','2026-09-24',1],['OS-0507','Em execução','2026-09-23',2]]);
  chk('agrPainelRef: atrasadas com recorte Lagoa Grande',agrPainelRef(cenClone(CEN0),{faz:'Lagoa Grande'}).os.atrasadas.map(x=>x.id),
   ra.os.atrasadas.filter(x=>x.faz==='Lagoa Grande').map(x=>x.id));
  const ec=cenClone(CEN0); ec.ordens['OS-0505'].etapa='Em conferência';
  chk('agrPainelRef: enviada para conferência deixa de ser atrasada',agrPainelRef(ec).os.atrasadas.some(x=>x.id==='OS-0505'),false);
  const bz=JSON.parse(JSON.stringify(OSD.ords.find(o=>o.id==='OS-0430'))); bz.id='OS-0601'; delete bz.fim; const ne=cenClone(CEN0); ne.ordens['OS-0601']={id:'OS-0601',etapa:'A liberar',osc:{novo:bz}};
  chk('agrPainelRef: ordem emitida sem fim não é julgada: conta em sem_prazo',[agrPainelRef(ne).os.n.sem_prazo,agrPainelRef(ne).os.atrasadas.some(x=>x.id==='OS-0601')],[1,false]);
  OSD.hoje='23/09/2026'; chk('agrPainelRef: hoje fora do formato ISO = atrasadas Sem dados, impedidas mantidas',[agrPainelRef(cenClone(CEN0)).os.atrasadas,agrPainelRef(cenClone(CEN0)).os.n.impedidas],[null,5]);
  OSD.hoje=h0; }
// S2: máquina apta (CMD-19) tira só o impedimento dela, como na tela O.S.
const ap=cenClone(CEN0); ap.man.ativos.a01.cond='Disponível'; const rA=agrPainelRef(ap);
chk('agrPainelRef: Trator T1 apto → OS-0420 e OS-0431 saem; falta de insumo e bomba ficam',rA.os.impedidas.map(x=>x.id),['OS-0418','OS-0502','OS-0507']);
chk('agrPainelRef: apto = a mesma projeção da tela O.S. (sem selo de impedimento na OS-0420)',osProjecao(ap).find(o=>o.id==='OS-0420').selos.some(s=>OS_IMP_RE.test(s.t)),false);
// S3: recorte por fazenda e safra
chk('agrPainelRef: recorte Lagoa Grande = OS-0502 e OS-0507',agrPainelRef(ag,{faz:'Lagoa Grande'}).os.impedidas.map(x=>x.id),['OS-0502','OS-0507']);
chk('agrPainelRef: recorte Santa Rita = OS-0418, OS-0420 e OS-0431',agrPainelRef(ag,{faz:'Santa Rita'}).os.impedidas.map(x=>x.id),['OS-0418','OS-0420','OS-0431']);
chk('agrPainelRef: recorte safra 2025/26 = nenhuma',agrPainelRef(ag,{saf:'2025/26'}).os.impedidas,[]);
chk('agrPainelRef: recorte Santa Rita · 2026/27 = OS-0418, OS-0420 e OS-0431',agrPainelRef(ag,{faz:'Santa Rita',saf:'2026/27'}).os.impedidas.map(x=>x.id),['OS-0418','OS-0420','OS-0431']);
const sf=cenClone(CEN0); const k0=OSD.ords.find(o=>o.id==='OS-0507'); const fz0=k0.faz; k0.faz='';
chk('agrPainelRef: ordem aberta sem fazenda com recorte pedido = Sem dados',agrPainelRef(sf,{faz:'Lagoa Grande'}).os,null);
chk('agrPainelRef: sem recorte, a mesma ordem conta',agrPainelRef(sf).os.n.impedidas,5); k0.faz=fz0;
const en=cenClone(CEN0); en.ordens['OS-0420'].etapa='Encerradas';chk('agrPainelRef: encerrada sai da lista',agrPainelRef(en).os.impedidas.some(x=>x.id==='OS-0420'),false);
en.ordens['OS-0420'].etapa='Canceladas';chk('agrPainelRef: cancelada sai da lista',agrPainelRef(en).os.impedidas.some(x=>x.id==='OS-0420'),false);
chk('agrPainelRef: ordens ausentes = Sem dados',agrPainelRef({}).os,null);
// revisão Codex 6163849078: o estado decide quais ordens existem; o registro não ressuscita ordem nem transforma vazio em impedida
chk('agrPainelRef: ordens vazias = lista vazia e 0',[agrPainelRef({ordens:{}}).os.impedidas,agrPainelRef({ordens:{}}).os.n.impedidas],[[],0]);
const dl=cenClone(CEN0); dl.man.ativos.a01.cond='Disponível'; delete dl.ordens['OS-0420'];
chk('agrPainelRef: ordem fora do estado não volta (a01 apto, OS-0420 apagada)',agrPainelRef(dl).os.impedidas.map(x=>x.id),['OS-0418','OS-0502','OS-0507']);
const dl2=cenClone(CEN0); delete dl2.ordens['OS-0420'];
chk('agrPainelRef: OS-0420 apagada com a01 bloqueado também não volta',agrPainelRef(dl2).os.impedidas.map(x=>x.id),['OS-0418','OS-0431','OS-0502','OS-0507']);
const sb=cenClone(CEN0); sb.ordens['OS-9999']={id:'OS-9999',etapa:'A liberar'};
chk('agrPainelRef: ordem do estado sem registro nem emissão = Sem dados',agrPainelRef(sb).os,null);
const ce=cenClone(CEN0); ce.ordens['OS-0507'].id='OS-0508';
chk('agrPainelRef: chave diferente do id = Sem dados',agrPainelRef(ce).os,null);
const se=cenClone(CEN0); delete se.ordens['OS-0418'].etapa;
chk('agrPainelRef: ordem sem etapa = Sem dados',agrPainelRef(se).os,null);
const ob=cenClone(CEN0);
chk('agrPainelRef: beneficiamento fora do registro não invalida o estado',agrPainelRef(ob).os.n.impedidas,5);
const em=cenClone(CEN0); const bz=JSON.parse(JSON.stringify(OSD.ords.find(o=>o.id==='OS-0431'))); bz.id='OS-0600';
em.ordens['OS-0600']={id:'OS-0600',etapa:'A liberar',osc:{novo:bz}};
chk('agrPainelRef: ordem emitida na tela (osc.novo) entra pela base dela',agrPainelRef(em).os.impedidas.map(x=>x.id).includes('OS-0600'),true);
// PAINEL-02 · agrCustoRef (contrato 6166150698): mesmas regras da camada Custos do Mapa (custo_dominio.js)
{ const k0=cenClone(CEN0), j0=JSON.stringify(k0), K=agrCustoRef(k0);
  chk('agrCustoRef: não muda o estado',JSON.stringify(k0),j0);
  chk('agrCustoRef: seed = 4 culturas (fazenda · cultura)',K.cultivos.map(x=>x.faz+' · '+x.cultura),['Santa Rita · Soja','Santa Rita · Mamão Formosa','Santa Rita · Café','Lagoa Grande · Mamão Formosa']);
  const so=K.cultivos[0];
  chk('agrCustoRef: Soja com talhões sem plano = R$/ha orçado null, sem_orc listado e parcial',[so.orcado_rs_ha,so.sem_orc,so.parcial],[null,['T4','T3','P1','P2'],true]);
  chk('agrCustoRef: realizado = soma de cusTalhao por talhão (mesma conta do Mapa)',so.real_prov_rs,Math.round(so.talhoes.reduce((s,t)=>s+cusTalhao(CUSD,t,osProjecaoEstado(k0,id=>/^OB-/.test(id))).rs,0)*100)/100);
  chk('agrCustoRef: O.S. de vários talhões (OS-0421, T1 + T2) fica em sem_rateio',K.sem_rateio.map(x=>[x.os,x.talhoes]),[['OS-0421',['T1','T2']]]);
  chk('agrCustoRef: recorte Lagoa Grande = só a cultura da Lagoa',agrCustoRef(k0,{faz:'Lagoa Grande'}).cultivos.map(x=>x.cultura),['Mamão Formosa']);
  const pr=CUSD.preco, semP=Object.assign({},pr); const prodLG=Object.keys(pr)[0]; delete semP[prodLG]; CUSD.preco=semP;
  const Kp=agrCustoRef(cenClone(CEN0)); CUSD.preco=pr;
  chk('agrCustoRef: preço removido não vira zero: alguma cultura fica parcial com o item em pend',Kp.cultivos.some(x=>x.parcial&&x.pend.some(p=>p.indexOf(prodLG)>=0)),true);
  chk('agrCustoRef: estado vazio = custos zerados (válido), não null',agrCustoRef({ordens:{}}).cultivos.every(x=>x.real_prov_rs===0&&x.ha_exec===0),true);
  chk('agrCustoRef: estado inválido = Sem dados',[agrCustoRef({}),agrCustoRef({ordens:{x:{id:'OS-9',etapa:'A liberar'}}})],[null,null]); }
chk('agrPainelRef: estado não objeto = Sem dados',[agrPainelRef({ordens:[]}).os,agrPainelRef(null).os],[null,null]);
console.log('RESULTADO '+n+'/'+n);
'''

def unit():
    from areas.processo_os import JS_NUCLEO, _ordens
    import dados2 as D2
    osd='const OSD = '+json.dumps(dict(ords=_ordens(),hoje=D2.HOJE_ISO),ensure_ascii=False)+';\n'
    import areas.custo_dominio as CU
    src=cenario.perfis_js()+cenario.js_prefixo()+DM.js_regras()+osd+JS_NUCLEO+CU.js_prefixo()+P.JS+TEST
    with tempfile.TemporaryDirectory(prefix='painel01-') as d:
        p=Path(d)/'oracle.js';p.write_text(src)
        r=subprocess.run(['node',str(p)],text=True,capture_output=True)
        print(r.stdout);print(r.stderr,end='');return r.returncode

def ui():
    from comp_lib import Chrome, servir
    import ui37
    port,srv=servir(os.environ.get('RENDER_DIR') or str(Path(__file__).parent/'_render'));c=Chrome();J=c.js;checks=[]
    def chk(n,yes,detail=''):
        checks.append(bool(yes));print(('OK ' if yes else 'FALHA ')+n+('' if yes else ' '+str(detail)),flush=True)
    def wait(expr):
        end=time.monotonic()+4
        while time.monotonic()<end:
            if J(expr):return True
            time.sleep(.05)
        return False
    U=lambda p:f'http://127.0.0.1:{port}/{p}'
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__pnErrors=[];addEventListener('error',e=>__pnErrors.push(e.message));addEventListener('unhandledrejection',e=>__pnErrors.push(String(e.reason)));"})
    try:
        for width,touch in [(1440,False),(390,True)]:
            c.aparelho(width,844,1,touch)
            for fid,(mod,_,items,links) in P.PAINEIS.items():
                c.goto(U(ui37.HUB37[mod]),.4)
                chk(fid+' primeiro cartão '+str(width),J("document.querySelector('a.mod-cartao').getAttribute('href')")==fid+'.dc.html')
                J("document.querySelector('a.mod-cartao').click()")
                chk(fid+' quatro indicadores renderizados '+str(width),wait("document.querySelectorAll('.pn-value').length===4 && !document.querySelector('.pn-value').textContent.includes('{{')"))
                data=J("({err:__pnErrors,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth, vals:[...document.querySelectorAll('.pn-value')].map(x=>x.textContent), links:[...document.querySelectorAll('.pn-link')].map(a=>a.getAttribute('href'))})")
                chk(fid+' sem JS/overflow '+str(width),not data['err'] and not data['overflow'],data)
                chk(fid+' destinos existentes '+str(width),data['links']==[h for _,h in links])
                chk(fid+' fonte completa no seed '+str(width),'Sem dados' not in data['vals'],data)
                J("document.querySelector('main').scrollTop=100000")
                chk(fid+' ação primária alcançável ao rolar '+str(width),J("(()=>{let a=document.querySelector('header .pn-link'),r=a.getBoundingClientRect();return r.height>=40&&r.top>=0&&r.bottom<=innerHeight&&a.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))})()"))
                J("document.querySelector('main').scrollTop=0;document.querySelector('.pn-tip').focus()")
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
                chk(fid+' fórmula por teclado '+str(width),wait("(()=>{let d=document.querySelector('#g2-dica');return d&&!d.hidden&&d.textContent.includes('Fonte:')})()"))
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
                chk(fid+' Escape fecha dica '+str(width),wait("!document.querySelector('#g2-dica')||document.querySelector('#g2-dica').hidden"))
                if touch:
                    xy=J("(()=>{let r=document.querySelector('.pn-tip').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height}})()")
                    c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':xy['x'],'y':xy['y']}]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                    chk(fid+' toque abre fórmula e alvo44',xy['w']>=44 and xy['h']>=44 and wait("(()=>{let d=document.querySelector('#g2-dica');return d&&!d.hidden&&d.textContent.includes('Fonte:')})()"))
                J("document.querySelector('.volta37').click()")
                chk(fid+' volta devolve foco ao cartão '+str(width),wait("!!document.activeElement && document.activeElement.getAttribute('href')==="+json.dumps(fid+'.dc.html')))
        seed=cenario.seed();seed['ordens']={}
        c.goto(U('PAGR.dc.html'),.4)
        J("localStorage.setItem('talhao-os-cenario-v1',"+json.dumps(json.dumps(seed))+ ");location.reload()")
        chk('Vazio é zero com mensagem explícita',wait("document.querySelector('.pn-value')&&[...document.querySelectorAll('.pn-value')].every(x=>x.textContent==='0')&&document.body.innerText.includes('Nenhum registro neste recorte')"))
        seed['ordens']={'OS-QA':{'id':'OS-QA','etapa':'A liberar'}}
        J("localStorage.setItem('talhao-os-cenario-v1',"+json.dumps(json.dumps(seed))+");dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))")
        chk('Mudança do cenário atualiza painel sem recarregar',wait("document.querySelector('.pn-value').textContent==='1'"))
        del seed['ordens']
        J("localStorage.setItem('talhao-os-cenario-v1',"+json.dumps(json.dumps(seed))+");location.reload()")
        chk('Fonte ausente: sem dados e caminho de recuperação',wait("document.querySelector('.pn-value')&&[...document.querySelectorAll('.pn-value')].every(x=>x.textContent==='Sem dados')&&document.body.innerText.includes('Há dados incompletos')&&document.querySelector('.pn-link').getAttribute('href')==='OS.dc.html'"))
        c.goto(U('MOD-COM.dc.html'),.4)
        chk('Comercial reutiliza PCOM como primeiro cartão',J("document.querySelector('a.mod-cartao').getAttribute('href')")=='PCOM.dc.html')
    finally:c.close();srv.terminate()
    print(f'RESULTADO {sum(checks)}/{len(checks)}');return 0 if all(checks) else 1

if __name__=='__main__':sys.exit(ui() if '--ui' in sys.argv else unit())
