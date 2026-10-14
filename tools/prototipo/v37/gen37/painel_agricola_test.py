# -*- coding: utf-8 -*-
"""PAINEL02: unidade; --prepare compõe em memória; --ui após montar_render.
Oráculos explícitos: não confundir semana corrente, seguinte e acumulado.
"""
import os,sys,json,tempfile,subprocess,time
from pathlib import Path
os.environ.setdefault('SAFRION_DADOS','sintetico')
from areas import painel_agricola as P
import cenario

TEST=r'''
const assert=require('node:assert/strict');let n=0;
function chk(t,a,b){assert.deepEqual(a,b,t);console.log('OK '+t);n++;}
const c=cenClone(CEN0), before=JSON.stringify(c);
const x=pnaLeitura(c,'lg19');
chk('Pivô19: 72.9t publicadas e 36.42t recebidas na S39',[x.prev,x.medido.kg],[72900,36420]);
chk('Perene identifica semana em curso',x.periodo,'S39 · 21/09–27/09 (em curso)');
chk('Recebido conserva unidade de produção',x.recebido,'36,42 t');
chk('Cultivo abre a origem exata',x.href,'COLH.dc.html#lg19');
chk('Anual lê a previsão da safra',pnaLeitura(c,'c1').prev,614400);
chk('Safra tem nome sem prefixo repetido',pnaLeitura(c,'c1').periodo,'Safra 2026/27');
chk('Ausência de previsão não é zero',pnaLeitura(c,'lg02').prev,null);
chk('Leitura não altera cenário',JSON.stringify(c),before);
chk('Fonte ausente fica indisponível',pnaLinhas({}),null);
// Versão futura não substitui a previsão da semana que está sendo comparada.
const seguinte=prSemMais(prSem(prHoje()),1);
c.producao.previsoes.lg19.push({v:99,sem:{[seguinte]:999999}});
chk('Previsão de outra semana não contamina S39',pnaLeitura(c,'lg19').prev,72900);
// Contraprova de projeção: domínio fornece passes de semanas distintas e café a apurar.
const realTal=prTal;
prTal=(c,id)=>{const z=realTal(c,id);z.R.passes=z.R.passes.concat([{sem:seguinte,kg:900000,area:0,cafe:0,apurar:false,aPesar:[]}]);return z;};
chk('Recebido futuro não vira acumulado da semana',pnaLeitura(c,'lg19').medido.kg,36420);
prTal=(c,id)=>{const z=realTal(c,id);z.R.apurar=true;z.R.kg=0;z.R.cafe=1200;z.R.comecou=true;return z;};
const cafe=pnaLeitura(c,'c9');
chk('Café a apurar permanece explícito',cafe.recebido.includes('a apurar'),true);
chk('Café a apurar não ordena como zero medido',pnaRow(cafe).v.recebido,null);
prTal=realTal;
const sem=cenClone(CEN0);sem.producao.previsoes.c1=[];
const anual=pnaRow(pnaLeitura(sem,'c1'));
chk('Anual sem previsão publicada preserva nulo',anual.ordk.prev,null);
for(const d of [0,1]) {
 const sp={cols:[{k:'prev',t:'num'}]}, rows=[anual,pnaRow(pnaLeitura(CEN0,'lg19')),pnaRow(pnaLeitura(CEN0,'c1'))];
 chk('G2 anual ausente por último direção '+d,g2sort(rows,sp,{so:{k:'prev',d}}).map(r=>r.id),d?['c1','lg19','c1']:['lg19','c1','c1']);
 chk('G2 último é o objeto sem previsão direção '+d,g2sort(rows,sp,{so:{k:'prev',d}}).at(-1)===anual,true);
 const medido={id:'medido',ordk:{recebido:500},v:{recebido:500}};
 chk('G2 café a apurar não usa 1200 do rótulo direção '+d,g2sort([pnaRow(cafe),medido],{cols:[{k:'recebido',t:'num'}]},{so:{k:'recebido',d}}).map(r=>r.id),['medido','c9']);
}
// Contrato sintético da apresentação; não substitui os testes do getter de domínio.
const impedida={id:'OS-0420',talhao:'T4',faz:'Santa Rita',saf:'Safra 2026/27',motivo:'Falta máquina',causa:'Máquina ou equipamento',dono:'Caio',desde:null,origem:'OS.dc.html#OS-0420'};
const atrasada={...impedida,prevista:'2026-09-22',dias:1};
const ref={os:{impedidas:[impedida],atrasadas:[atrasada],n:{impedidas:1,atrasadas:1}},custos:null};
const refAntes=JSON.stringify(ref), leitura=pnaOSLinhas(ref), grupo=pnaOSGrupos(leitura,'causa')[0];
chk('Mesma O.S. impedida e atrasada é contada uma vez',leitura.length,1);
chk('Duas situações não duplicam a contagem',[grupo.n,grupo.impedidas,grupo.atrasadas],[1,1,1]);
chk('Causa da origem e IDs recuperáveis',[grupo.label,grupo.ids],['Máquina ou equipamento',['OS-0420']]);
chk('Destino do grupo não duplica ordem em duas situações',grupo.href,'OS.dc.html#painel=OS-0420');
chk('Foco distingue causa de responsável',grupo.foco,'causa:Máquina ou equipamento');
chk('Impedimento tem vermelho do DS',grupo.barra.endsWith('background:#B42318'),true);
chk('Sem mutação do retorno do domínio',JSON.stringify(ref),refAntes);
chk('Ausente não significa sem pendência',pnaOSLinhas(null),null);
chk('Vazio válido permite mensagem sem pendência',pnaOSLinhas({os:{impedidas:[],atrasadas:[]}}),[]);
chk('Lista inválida não mostra zero',pnaOSLinhas({os:{impedidas:{},atrasadas:[]}}),null);
chk('Origem inválida não cria navegação',pnaOSLinhas({os:{impedidas:[{...impedida,origem:'javascript:alert(1)'}],atrasadas:[]}}),null);
chk('Responsável ausente explícito',pnaOSGrupos([{...leitura[0],dono:null}],'dono')[0].label,'Responsável não informado');
const outras=pnaOSLinhas({os:{impedidas:[impedida,{...impedida,id:'OS-0421',origem:'OS.dc.html#OS-0421',motivo:'Outra máquina indisponível'},
 {...impedida,id:'OS-0422',origem:'OS.dc.html#OS-0422',dono:'Lia',motivo:'Falta insumo',causa:'Insumo no Estoque'}],atrasadas:[atrasada]}});
chk('Agrupa responsável sem duplicar OS em duas situações',pnaOSGrupos(outras,'dono').map(g=>[g.label,g.n]),[['Caio',2],['Lia',1]]);
chk('Destino leva exatamente o subconjunto por responsável',pnaOSGrupos(outras,'dono').map(g=>g.href),['OS.dc.html#painel=OS-0420,OS-0421','OS.dc.html#painel=OS-0422']);
chk('Maior causa primeiro e barra proporcional',pnaOSGrupos(outras,'causa').map(g=>[g.n,/width:([\d.]+)%/.exec(g.barra)[1]]),[[2,'100'],[1,'50']]);
chk('Não soma as duas distribuições',pnaOSGrupos(outras,'dono').reduce((a,g)=>a+g.n,0),3);
chk('Gráfico ausente não vira zero',pnaOSGrupos(null,'dono'),null);
chk('Situação homogênea não repete contagem sob a barra',pnaOSGrupos([{...leitura[0],atrasada:false}],'causa')[0].situacao,'');
chk('Causa ausente não é inventada a partir do selo',pnaOSGrupos([{...leitura[0],causa:null}],'causa')[0].label,'Causa não informada');
chk('Referência vem da origem',pnaOSReferencia({os:{referencia:'2026-09-23'}}),'Prazos até 23/09/2026');
chk('Referência ausente explícita',pnaOSReferencia({os:{referencia:null}}),'Referência de prazos indisponível');
chk('Gráfico vazio preservado',pnaOSGrupos([],'causa'),[]);
chk('Atraso ausente não esconde impedimento conhecido',pnaOSLinhas({os:{impedidas:[impedida],atrasadas:null}}).length,1);
chk('Ambos ausentes não viram vazio',pnaOSLinhas({os:{impedidas:null,atrasadas:null}}),null);

const cost={id:'F|2026/27|Soja',cultura:'Soja',faz:'F',saf:'2026/27',area_ha:10,orcado_rs_ha:10,
 real_rs_ha:20,real_conf_rs:100,real_prov_rs:100,parcial:false,sem_orc:[],pend:[]};
const cr={cultivos:[cost],sem_rateio:[],fora:[],cobertura_incerta:false}, crAntes=JSON.stringify(cr);
const cv=pnaCustos(cr).rows[0];
chk('Custo apresenta razões do domínio, sem dividir por passagens',[cv.orcado,cv.realizado],['10,00 R$/ha','20,00 R$/ha']);
chk('Conferido e provisório separados',[cv.conferido,cv.provisorio],['100,00 R$','100,00 R$']);
chk('Mesmo par usa uma escala',[cv.barOrcado.includes('width:50%'),cv.barReal.includes('width:100%')],[true,true]);
chk('Custo leitura sem mutação',JSON.stringify(cr),crAntes);
chk('Custo ausente não vira vazio',pnaCustos(null),null);
chk('Custo vazio válido',pnaCustos({cultivos:[],sem_rateio:[],fora:[]}),{rows:[],fora:[]});
const parc=pnaCustos({...cr,cultivos:[{...cost,parcial:true,real_rs_ha:0,orcado_rs_ha:null,
 sem_orc:['T4'],pend:['Sem preço: X']}],cobertura_incerta:true,
 fora:[{os:'OS-9002',rs:0,real_conf_rs:0,real_prov_rs:0,executada:true,pend:['Sem preço: X'],motivo:'Sem vínculo'}]} );
chk('Orçamento nulo não vira zero',parc.rows[0].orcado,'Orçamento por hectare indisponível');
chk('Zero parcial não se apresenta como total',parc.rows[0].realizado,'Subtotal conhecido: 0,00 R$/ha');
chk('Cobertura e preço ausente visíveis',parc.rows[0].pend.map(x=>x.texto),
 ['Sem orçamento de plano: T4','Sem preço: X','Há O.S. executada fora da cobertura do custo; o subtotal não cobre todo o realizado.']);
chk('Fora sem preço ainda aparece',[parc.fora.length,parc.fora[0].valor,parc.fora[0].motivo],[1,'0,00 R$ conhecidos · parcial','Sem vínculo · Sem preço: X']);
chk('Razão inválida é indisponível',pnaCustos({...cr,cultivos:[{...cost,real_rs_ha:null}]}).rows[0].realizado,'Realizado por hectare indisponível');
chk('Zero válido permanece zero',pnaCustos({...cr,cultivos:[{...cost,real_rs_ha:0}]}).rows[0].realizado,'0,00 R$/ha');
chk('Sem rateio listado sem somar ao grupo',pnaCustos({...cr,sem_rateio:[{os:'OS-9001',rs:200,real_conf_rs:100,real_prov_rs:100,pend:[]}]}).fora[0].titulo,'OS-9001 · Sem rateio por talhão');

console.log('RESULTADO '+n+'/'+n);
'''

def unit():
    with tempfile.TemporaryDirectory(prefix='pn02-') as d:
        # Usa o comparador de produção, sem reimplementar seu algoritmo no teste.
        g2=Path(__file__).with_name('g2lib.js').read_text().split('function g2filtering(')[0]
        p=Path(d)/'probe.js';p.write_text(cenario.perfis_js()+cenario.js_prefixo()+g2+P.JS+TEST)
        r=subprocess.run(['node',str(p)],capture_output=True,text=True)
        print(r.stdout);print(r.stderr,end='');return r.returncode

def prepare():
    """Contrato de composição exercitado sem editar paineis.py do Claude."""
    import engine as E
    from areas import paineis
    original=paineis.shell37
    def composto(fid,title,body,**kwargs):
        if fid=='PAGR':
            html,js=P.secao()
            body=body.replace('<nav class="pn-links"',html+'<nav class="pn-links"',1)
            E.EXTRAJS[0]=E.EXTRAJS[0].replace('function EXTRAVALS(', 'function pnBaseVals(',1)+js+'\nfunction EXTRAVALS(self,v){pnBaseVals(self,v);pnaVals(self,v);}'
        return original(fid,title,body,**kwargs)
    paineis.shell37=composto
    try:paineis.build()
    finally:paineis.shell37=original
    return 0

def ui():
    from comp_lib import Chrome,servir
    port,srv=servir(str(Path(__file__).parent/'_render'));c=Chrome();J=c.js;checks=[]
    def chk(t,v,detail=''):
        checks.append(bool(v));print(('OK ' if v else 'FALHA ')+t+(' '+str(detail) if not v else ''),flush=True)
    def wait(e):
        end=time.monotonic()+8
        while time.monotonic()<end:
            if J(e):return True
            time.sleep(.1)
        return False
    url=lambda p:f'http://127.0.0.1:{port}/{p}'
    try:
        c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errors=[];addEventListener('error',e=>__errors.push(e.message));"})
        for w,touch in [(1440,False),(390,True)]:
            c.aparelho(w,844,1,touch);c.goto(url('PAGR.dc.html'),1)
            chk('Linhas renderizadas '+str(w),wait("document.querySelectorAll('[data-rid]').length>=23"))
            chk('Quatro cartões e ação originais preservados '+str(w),J("document.querySelectorAll('.pn-card').length===4&&[...document.querySelectorAll('a')].some(a=>a.textContent.trim()==='Consultar O.S.')"))
            chk('Seção abaixo dos cartões sem frase redundante '+str(w),J("(()=>{let s=document.querySelector('[aria-label=\"Colheita por cultivo\"]'),g=document.querySelector('.pn-grid');return g.getBoundingClientRect().bottom<=s.getBoundingClientRect().top&&!s.innerText.includes('Todas as fazendas e safras')})()"))
            chk('Valores comparáveis '+str(w),J("(()=>{let r=document.querySelector('[data-rid=lg19]');return !!r&&r.innerText.includes('72,9 t')&&r.innerText.includes('36,42 t')&&r.innerText.includes('S39')})()"))
            chk('Sem JS nem overflow da página '+str(w),J("__errors.length===0&&document.documentElement.scrollWidth<=innerWidth"),J('__errors'))
            chk('Sem total somando culturas '+str(w),not J("document.querySelector('[role=table]').innerText.includes('Total')"))
            J("document.querySelector('[aria-label=\"Como comparar a colheita\"]').focus()")
            c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Origem e período por teclado '+str(w),wait("(()=>{let t=document.querySelector('#g2-dica');return t&&!t.hidden&&t.innerText.includes('semana em curso')})()"))
            c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
            chk('Escape fecha fórmula '+str(w),wait("document.querySelector('#g2-dica').hidden"))
            # Busca pelo controle real, não alterando o estado interno da aplicação.
            J("(()=>{let i=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Pivô 19');i.dispatchEvent(new Event('input',{bubbles:true}));})()")
            chk('Recorte do cultivo '+str(w),wait("document.querySelectorAll('[data-rid]').length===1&&!!document.querySelector('[data-rid=lg19]')"))
            if touch:
                xy=J("(()=>{let e=document.querySelector('[data-rid=lg19] [role=cell]');e.scrollIntoView({block:'center',inline:'start'});let r=e.getBoundingClientRect();return {x:r.left+30,y:r.top+30}})()")
                c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            else:
                J("document.querySelector('[data-rid=lg19]').focus()")
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Toque/Enter abre cultivo na origem '+str(w),wait("location.pathname.endsWith('COLH.dc.html')&&location.hash==='#lg19'&&!!document.querySelector('aside[role=dialog]')"))
            J('history.back()');time.sleep(1)
            chk('Voltar preserva busca '+str(w),wait("location.pathname.endsWith('PAGR.dc.html')&&document.querySelectorAll('[data-rid]').length===1&&!!document.querySelector('[data-rid=lg19]')"))
            chk('Voltar restaura foco no cultivo '+str(w),wait("!!document.activeElement&&document.activeElement.getAttribute('data-rid')==='lg19'"))
            J("(()=>{let i=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'');i.dispatchEvent(new Event('input',{bubbles:true}));})()")
        Path('_probe').mkdir(exist_ok=True);c.shot(str(Path('_probe/painel02-390.png').resolve()))
    finally:c.close();srv.terminate()
    print('RESULTADO '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1

def os_contract_ui():
    """Prova UI com retorno sintético: não constitui integração de agrPainelRef."""
    from comp_lib import Chrome,servir
    # Isola a fronteira do getter só no HTML temporário servido pelo teste.
    # O bundle fecha funções no escopo local; window.agrPainelRef não substitui a função real.
    render=Path(__file__).parent/'_render'; tmp=tempfile.TemporaryDirectory(prefix='pn02-contrato-'); root=Path(tmp.name)
    for item in render.iterdir():
        if item.name!='PAGR.dc.html': (root/item.name).symlink_to(item.resolve(),target_is_directory=item.is_dir())
    html=(render/'PAGR.dc.html').read_text(); marker='function pnaVals(self,v) {'
    assert html.count(marker)==1, 'Gancho de apresentação ausente ou ambíguo'
    (root/'PAGR.dc.html').write_text(html.replace(marker,marker+'\n const agrPainelRef=window.__pnOSFixture;',1))
    port,srv=servir(str(root));c=Chrome();J=c.js;checks=[]
    def chk(t,v):
        checks.append(bool(v));print(('OK ' if v else 'FALHA ')+t,flush=True)
    def wait(e):
        end=time.monotonic()+8
        while time.monotonic()<end:
            if J(e):return True
            time.sleep(.1)
        return False
    fixture={"os":{"referencia":"2026-09-23","impedidas":[{"id":"OS-0420","talhao":"T4","faz":"Santa Rita","saf":"Safra 2026/27","motivo":"Falta máquina","causa":"Máquina ou equipamento","dono":"Caio","desde":None,"origem":"OS.dc.html#OS-0420"}],"atrasadas":[{"id":"OS-0420","prevista":"2026-09-22","dias":1,"origem":"OS.dc.html#OS-0420"}]},"custos":None}
    try:
        for w,touch in [(1440,False),(390,True)]:
            absence=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>null;'})['identifier']
            c.aparelho(w,844,1,touch);c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Fonte ausente explícita '+str(w),wait("document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]').innerText.includes('Dados de impedimentos e prazos indisponíveis')&&!document.querySelector('.pna-grupo')"))
            J("(()=>{let e=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'');e.dispatchEvent(new Event('input',{bubbles:true}));})()")
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':absence})
            # O adaptador é fixture exclusiva desta prova; montagem do produto não recebe seed paralelo.
            fixture_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(fixture,ensure_ascii=False)+');'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Dois gráficos sem lista operacional '+str(w),wait("document.querySelectorAll('.pna-grupo').length===2&&!document.querySelector('[data-rid^=\"os:\"]')"))
            chk('Contagem única e situações textuais '+str(w),J("(()=>{let s=document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]');return ['1 O.S. precisam de ação','Máquina ou equipamento','Prazos até 23/09/2026','Caio','1 impedida(s) · 1 atrasada(s)'].every(t=>s.innerText.includes(t))&&!s.querySelector('[role=table]')})()"))
            chk('Impedimento vermelho '+str(w),J("[...document.querySelectorAll('.pna-grupo [aria-hidden] span')].every(e=>getComputedStyle(e).backgroundColor==='rgb(180, 35, 24)')"))
            chk('Cartões e colheita preservados '+str(w),J("document.querySelectorAll('.pn-card').length===4&&!!document.querySelector('[data-rid=lg19]')&&document.documentElement.scrollWidth<=innerWidth"))
            button="document.querySelector('[aria-label=\"Como ler os impedimentos e atrasos\"]')"
            if touch:
                xy=J("(()=>{let e="+button+";e.scrollIntoView({block:'center'});let r=e.getBoundingClientRect();return {x:r.left+20,y:r.top+20}})()")
                c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            else:
                J(button+'.focus()')
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Fórmula por teclado/toque '+str(w),wait("(()=>{let e=document.querySelector('#g2-dica');return e&&!e.hidden&&e.innerText.includes('não devem ser somadas')&&e.innerText.includes('Área afetada não fornecida')})()"))
            c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
            chk('Escape fecha explicação '+str(w),wait("document.querySelector('#g2-dica').hidden"))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':fixture_script})
            parcial=json.loads(json.dumps(fixture));parcial['os']['atrasadas']=None;parcial['os']['referencia']=None
            partial_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(parcial,ensure_ascii=False)+');'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Atrasos sem dados preservam impedimento e explicação '+str(w),wait("(()=>{let s=document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]');return s&&s.innerText.includes('Prazos indisponíveis')&&s.innerText.includes('Máquina ou equipamento')&&s.innerText.includes('Referência de prazos indisponível')&&!s.innerText.includes('Nenhuma O.S. impedida')})()"))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':partial_script})
            incomplete={"os":{"impedidas":[],"atrasadas":[],"n":{"sem_prazo":2}}}
            incomplete_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(incomplete)+');'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Sem prazo não permite falsa ausência de pendência '+str(w),wait("(()=>{let s=document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]');return s.innerText.includes('2 O.S. sem prazo válido')&&!s.innerText.includes('Nenhuma O.S. impedida')})()"))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':incomplete_script})
        final_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(fixture,ensure_ascii=False)+');'})['identifier']
        c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
        J("document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]').scrollIntoView({block:'start'})")
        Path('_probe').mkdir(exist_ok=True);c.shot(str(Path('_probe/painel-os-contrato-390.png').resolve()))
    finally:c.close();srv.terminate();tmp.cleanup()
    print('RESULTADO contrato sintético '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1


def custos_ui():
    """Composição real 1b6 + apresentação; ausência exercitada em fixture isolada."""
    from comp_lib import Chrome,servir
    render=Path(__file__).parent/'_render';tmp=tempfile.TemporaryDirectory(prefix='pn02-custos-');root=Path(tmp.name)
    for item in render.iterdir():
        if item.name!='PAGR.dc.html':(root/item.name).symlink_to(item.resolve(),target_is_directory=item.is_dir())
    html=(render/'PAGR.dc.html').read_text();marker='function pnaVals(self,v) {'
    assert html.count(marker)==1
    (root/'PAGR.dc.html').write_text(html.replace(marker,marker+"\n const agrCustoRef=window.__semCusto?()=>null:globalCusto;\n",1).replace(
        'function pnaVals(self,v)', 'const globalCusto=agrCustoRef;\nfunction pnaVals(self,v)',1))
    port,srv=servir(str(root));c=Chrome();J=c.js;checks=[]
    def chk(t,v):
        checks.append(bool(v));print(('OK ' if v else 'FALHA ')+t,flush=True)
    def wait(e):
        end=time.monotonic()+8
        while time.monotonic()<end:
            if J(e):return True
            time.sleep(.1)
        return False
    try:
        c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errors=[];addEventListener('error',e=>__errors.push(e.message));"})
        for w,touch in [(1440,False),(390,True)]:
            c.aparelho(w,844,1,touch);c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Quatro culturas do getter '+str(w),wait("document.querySelectorAll('.pna-custo').length===4"))
            chk('Soja: área plantada, razão e estados corretos '+str(w),J("""(()=>{let t=document.querySelector('.pna-custo').innerText;
              return ['Soja · Santa Rita · Safra 2026/27','1.085,00 ha plantados','62,18 R$/ha','49.135,88 R$','18.326,88 R$','Parcial','Orçamento por hectare indisponível','Sem orçamento de plano: T4, T3, P1, P2'].every(x=>t.includes(x))})()"""))
            chk('Sem rateio explícito '+str(w),J("""document.querySelector('[aria-label="Custos por cultura"]').innerText.includes('OS-0421 · Sem rateio por talhão')"""))
            chk('Sem JS/overflow '+str(w),J("__errors.length===0&&document.documentElement.scrollWidth<=innerWidth"))
            J("""document.querySelector('[aria-label="Como comparar os custos"]').focus()""")
            c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Fórmula pelo teclado '+str(w),wait("document.querySelector('#g2-dica')&&!document.querySelector('#g2-dica').hidden&&document.querySelector('#g2-dica').innerText.includes('Não representa economia')"))
            c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27})
            chk('Escape fecha fórmula '+str(w),wait("document.querySelector('#g2-dica').hidden"))
            J("""document.querySelector('[aria-label="Custos por cultura"]').scrollIntoView({block:'start'})""")
            Path('_probe').mkdir(exist_ok=True);c.shot(str(Path('_probe/painel-custos-'+str(w)+'.png').resolve()))
            link="""document.querySelector('[aria-label="Custos por cultura"] a')"""
            if touch:
                xy=J("(()=>{let e="+link+";e.scrollIntoView({block:'center'});let r=e.getBoundingClientRect();return {x:r.left+30,y:r.top+22}})()")
                c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            else:
                J(link+".focus()")
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
                c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Conferir composição abre origem '+str(w),wait("location.pathname.endsWith('GE-03.dc.html')"))
            J('history.back()')
            chk('Volta aos quatro grupos '+str(w),wait("document.querySelectorAll('.pna-custo').length===4"))
            absent=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__semCusto=true;'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Ausência explícita sem falso zero '+str(w),wait("""(()=>{let e=document.querySelector('[aria-label="Custos por cultura"]');return e&&e.innerText.includes('Dados de custos indisponíveis')&&e.querySelectorAll('.pna-custo').length===0})()"""))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':absent})
    finally:c.close();srv.terminate();tmp.cleanup()
    print('RESULTADO custos '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1


def grupos_ui():
    """Ponte real: grupo, busca anterior da O.S., retorno e foco nas duas larguras."""
    from comp_lib import Chrome,servir
    port,srv=servir(str(Path(__file__).parent/'_render'));c=Chrome();J=c.js;checks=[]
    def chk(t,v):
        checks.append(bool(v));print(('OK ' if v else 'FALHA ')+t,flush=True)
    def wait(e):
        end=time.monotonic()+8
        while time.monotonic()<end:
            if J(e):return True
            time.sleep(.1)
        return False
    def busca(valor):
        J("(()=>{let i=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,"+json.dumps(valor)+");i.dispatchEvent(new Event('input',{bubbles:true}));})()")
    try:
        c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errors=[];addEventListener('error',e=>__errors.push(e.message));"})
        for w,touch in [(1440,False),(390,True)]:
            c.aparelho(w,844,1,touch);c.goto(f'http://127.0.0.1:{port}/OS.dc.html',1)
            J("(()=>{let b=document.querySelector('[data-visao=lista]');if(b)b.click();})()")
            busca('OS-0430');time.sleep(.2)
            guardado=J("sessionStorage.getItem('g2:OS.dc.html:g_os')")
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1);busca('Café');time.sleep(.2)
            chk('Grupos independem da busca de colheita '+str(w),wait("document.querySelectorAll('a[data-pna-grupo]').length>1"))
            for campo in ['causa','dono']:
                sel='a[data-pna-grupo^="'+campo+':"]'
                dados=J("(()=>{let e=document.querySelector("+json.dumps(sel)+");let r=e.getBoundingClientRect();return {href:e.getAttribute('href'),foco:e.getAttribute('data-pna-grupo'),aria:e.getAttribute('aria-label'),h:r.height}})()")
                chk('Link nomeado e alvo44 '+campo+' '+str(w),dados['aria'].startswith('Abrir ') and dados['h']>=44)
                if touch:
                    xy=J("(()=>{let e=document.querySelector("+json.dumps(sel)+");e.scrollIntoView({block:'center'});let r=e.getBoundingClientRect();return {x:r.left+20,y:r.top+22}})()")
                    c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                else:
                    J('document.querySelector('+json.dumps(sel)+').focus()')
                    c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
                chk('Destino exato '+campo+' '+str(w),wait('location.hash==='+json.dumps('#'+dados['href'].split('#')[1])))
                ids=sorted(dados['href'].split('=')[1].split(','))
                expr="JSON.stringify([...new Set([...document.querySelectorAll('[data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid')).filter(x=>/^OS-/.test(x)))].sort())==="+json.dumps(json.dumps(ids,separators=(',',':')))
                chk('Subconjunto visível apesar da busca anterior '+campo+' '+str(w),wait(expr))
                chk('Busca de OS não sobrescrita '+campo+' '+str(w),J("sessionStorage.getItem('g2:OS.dc.html:g_os')")==guardado)
                J('history.back()')
                chk('Retorno ao grupo com foco '+campo+' '+str(w),wait("location.pathname.endsWith('PAGR.dc.html')&&document.activeElement.getAttribute('data-pna-grupo')==="+json.dumps(dados['foco'])))
                chk('Busca Café preservada '+campo+' '+str(w),J("document.querySelector('main input[type=search]').value==='Café'"))
            chk('Sem erro ou overflow '+str(w),J('__errors.length===0&&document.documentElement.scrollWidth<=innerWidth'))
    finally:c.close();srv.terminate()
    print('RESULTADO grupos '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1

if __name__=='__main__':sys.exit(grupos_ui() if '--grupos-ui' in sys.argv else custos_ui() if '--custos-ui' in sys.argv else os_contract_ui() if '--os-contract-ui' in sys.argv else prepare() if '--prepare' in sys.argv else ui() if '--ui' in sys.argv else unit())
