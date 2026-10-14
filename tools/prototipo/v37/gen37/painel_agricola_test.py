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
// Contrato sintético da apresentação; NÃO valida o getter de domínio ainda não entregue.
const impedida={id:'OS-0420',talhao:'T4',faz:'Santa Rita',saf:'Safra 2026/27',motivo:'Falta máquina',dono:'Caio',desde:null,origem:'OS.dc.html#OS-0420'};
const atrasada={...impedida,prevista:'2026-09-22',dias:1};
const ref={os:{impedidas:[impedida],atrasadas:[atrasada],n:{impedidas:1,atrasadas:1}},custos:null};
const refAntes=JSON.stringify(ref), leitura=pnaOSLinhas(ref), row=pnaOSRow(leitura[0]);
chk('Mesma O.S. impedida e atrasada ocupa uma linha',leitura.length,1);
chk('Ambas situações e dono permanecem visíveis',[row.v.situacao,row.v.motivo,row.v.dono],['Impedida · Atrasada','Falta máquina','Caio']);
chk('Janela ISO apresentada sem cálculo novo',row.v.prazo,'22/09/2026 · 1 dia(s) de atraso');
chk('Origem exata e ID sem colisão com cultivo',[row.href,row.id],['OS.dc.html#OS-0420','os:OS-0420']);
chk('Sem mutação do retorno do domínio',JSON.stringify(ref),refAntes);
chk('Ausente não significa sem pendência',pnaOSLinhas(null),null);
chk('Vazio válido permite mensagem sem pendência',pnaOSLinhas({os:{impedidas:[],atrasadas:[]}}),[]);
chk('Lista inválida não mostra zero',pnaOSLinhas({os:{impedidas:{},atrasadas:[]}}),null);
chk('Origem inválida não cria navegação',pnaOSLinhas({os:{impedidas:[{...impedida,origem:'javascript:alert(1)'}],atrasadas:[]}}),null);
const semDono=pnaOSRow({...leitura[0],dono:null,prevista:null,dias:null});
chk('Ausência de dono e prazo explícita',[semDono.v.dono,semDono.v.prazo],['Responsável não informado','Data não informada']);
chk('Atraso ausente não esconde impedimento conhecido',pnaOSLinhas({os:{impedidas:[impedida],atrasadas:null}}).length,1);
chk('Ambos ausentes não viram vazio',pnaOSLinhas({os:{impedidas:null,atrasadas:null}}),null);
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
    fixture={"os":{"impedidas":[{"id":"OS-0420","talhao":"T4","faz":"Santa Rita","saf":"Safra 2026/27","motivo":"Falta máquina","dono":"Caio","desde":None,"origem":"OS.dc.html#OS-0420"}],"atrasadas":[{"id":"OS-0420","prevista":"2026-09-22","dias":1,"origem":"OS.dc.html#OS-0420"}]},"custos":None}
    try:
        for w,touch in [(1440,False),(390,True)]:
            absence=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>null;'})['identifier']
            c.aparelho(w,844,1,touch);c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Fonte ausente explícita '+str(w),wait("document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]').innerText.includes('Dados de impedimentos e prazos indisponíveis')"))
            J("(()=>{let e=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'');e.dispatchEvent(new Event('input',{bubbles:true}));})()")
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':absence})
            # O adaptador é fixture exclusiva desta prova; montagem do produto não recebe seed paralelo.
            fixture_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(fixture,ensure_ascii=False)+');'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Uma linha para dois motivos '+str(w),wait("document.querySelectorAll('[data-rid=\"os:OS-0420\"]').length===1"))
            chk('Motivo, responsável e prazo '+str(w),J("(()=>{let r=document.querySelector('[data-rid=\"os:OS-0420\"]');return !!r&&['Impedida · Atrasada','Falta máquina','Caio','22/09/2026'].every(t=>r.innerText.includes(t))})()"))
            chk('Cartões e colheita preservados '+str(w),J("document.querySelectorAll('.pn-card').length===4&&!!document.querySelector('[data-rid=lg19]')&&document.documentElement.scrollWidth<=innerWidth"))
            J("(()=>{let e=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'OS-0420');e.dispatchEvent(new Event('input',{bubbles:true}));})()")
            chk('Busca na tarefa '+str(w),wait("document.querySelectorAll('[data-rid]').length===1"))
            if touch:
                xy=J("(()=>{let e=document.querySelector('[data-rid=\"os:OS-0420\"] [role=cell]');e.scrollIntoView({block:'center',inline:'start'});let r=e.getBoundingClientRect();return {x:r.left+25,y:r.top+25}})()")
                c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            else:
                J("document.querySelector('[data-rid=\"os:OS-0420\"]').focus()")
                c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
            chk('Abre O.S. por teclado/toque '+str(w),wait("location.pathname.endsWith('OS.dc.html')&&location.hash==='#OS-0420'&&!!document.querySelector('aside[role=dialog]')"))
            J('history.back()');time.sleep(1)
            chk('Volta preserva filtro e foco '+str(w),wait("location.pathname.endsWith('PAGR.dc.html')&&document.querySelectorAll('[data-rid]').length===1&&document.activeElement.getAttribute('data-rid')==='os:OS-0420'"))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':fixture_script})
            parcial=json.loads(json.dumps(fixture));parcial['os']['atrasadas']=None
            partial_script=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':'window.__pnOSFixture=()=>('+json.dumps(parcial,ensure_ascii=False)+');'})['identifier']
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Atrasos sem dados preservam impedimento e explicação '+str(w),wait("(()=>{let s=document.querySelector('[aria-label=\"O.S. que precisam de atenção\"]');return s&&s.innerText.includes('Prazos indisponíveis')&&s.innerText.includes('Falta máquina')&&!s.innerText.includes('Nenhuma O.S. impedida')})()"))
            c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':partial_script})
        Path('_probe').mkdir(exist_ok=True);c.shot(str(Path('_probe/painel-os-contrato-390.png').resolve()))
    finally:c.close();srv.terminate();tmp.cleanup()
    print('RESULTADO contrato sintético '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1

if __name__=='__main__':sys.exit(os_contract_ui() if '--os-contract-ui' in sys.argv else prepare() if '--prepare' in sys.argv else ui() if '--ui' in sys.argv else unit())
