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

const ordem={id:'OS-0421',talhao:'T1 + T2',faz:'Santa Rita',saf:'Safra 2026/27',tipo:'Aplicação',etapa:'Em execução',
 prevista_ha:350,realizada_ha:190,pct:54,sinal_ha:12,pendencia:null,dono:'Caio',prazo:'23/09',origem:'OS.dc.html#OS-0421'};
const er={execucao:{ordens:[ordem]}}, erAntes=JSON.stringify(er), ev=pnaExecucao(er)[0];
chk('Execução enviada não soma sinal local',ev.area,'Enviada: 190,00 ha de 350,00 ha previstos');
chk('Sinal local separado com consequência',ev.sinal,'12,00 ha no aparelho · ainda sem envio');
chk('Percentual vem do domínio sem nova conta',ev.progresso,'54% da área prevista enviada');
chk('Destino e recuperação exatos',[ev.href,ev.foco],['OS.dc.html#OS-0421','execucao:OS-0421']);
chk('Leitura de execução imutável',JSON.stringify(er),erAntes);
const ex=o=>pnaExecucao({execucao:{ordens:[{...ordem,...o}]}})[0];
chk('100% não encerra ordem em conferência',[ex({etapa:'Em conferência',pct:100,realizada_ha:350}).etapa,ex({etapa:'Em conferência'}).acao],['Em conferência','Conferir O.S.']);
chk('Pendência de domínio preservada',ex({pendencia:'Sobra em custódia'}).pendencia,'Sobra em custódia');
chk('Sem área não vira zero ou barra',[ex({prevista_ha:null,realizada_ha:null,pct:null}).area,ex({prevista_ha:null}).progresso],['Área de execução indisponível','']);
chk('Zero enviado legítimo',ex({realizada_ha:0,pct:0,sinal_ha:0}).area,'Enviada: 0,00 ha de 350,00 ha previstos');
chk('Ausência e vazio distintos',[pnaExecucao(null),pnaExecucao({execucao:{ordens:[]}})],[null,[]]);
chk('Origem ou estado inválidos recusados',[pnaExecucao({execucao:{ordens:[{...ordem,origem:'javascript:alert(1)'}]}}),pnaExecucao({execucao:{ordens:[{...ordem,etapa:'Encerrada'}]}})],[null,null]);
chk('Não mascara ordem duplicada como dois trabalhos',pnaExecucao({execucao:{ordens:[ordem,ordem]}}),null);
chk('Percentual inválido não mostra barra',ex({pct:Infinity}).progresso,'');
const visita={vis:'VIS-013',talhao:'T1',faz:'Santa Rita',cultura:'Soja',alvo:'Percevejo',origem:'AG-01.dc.html#VIS-013',rotulo:'Acima do NC',
 leitura:'5,1 / 4',unidade:'percevejos/m',pct_nc:128,data:'2026-09-18',dias:5,dono:'Ana'};
const mr={mip:{referencia:'2026-09-23',decidir:[visita],atrasadas:[],coleta:[]}}, mrAntes=JSON.stringify(mr), mv=pnaMip(mr);
chk('Leitura e NC não viram área afetada',mv.decidir[0].leitura,'5,1 / 4 · percevejos/m · 128% do NC');
chk('Referência do domínio explícita',mv.referencia,'Referência 23/09/2026');
chk('Idade da vistoria não inventa hoje',mv.decidir[0].tempo,'Vistoria 18/09/2026 · 5 dias até a referência');
chk('Leitura MIP não altera origem',JSON.stringify(mr),mrAntes);
const mx=o=>pnaMip({mip:{...mr.mip,decidir:[{...visita,...o}]}}).decidir[0];
chk('Presença não ganha percentual fictício',mx({leitura:'3 de 20 com sintoma',unidade:null,pct_nc:null}).leitura,'3 de 20 com sintoma');
chk('Cancelada preserva estado e responsável',[mx({rotulo:'O.S. cancelada'}).estado,mx({rotulo:'O.S. cancelada'}).dono],['O.S. cancelada','Ana']);
chk('MIP ausência não vira zero',[pnaMip(null),pnaMip({mip:{decidir:null,atrasadas:[],coleta:[]}})],[null,null]);
chk('MIP vazio válido preservado',pnaMip({mip:{...mr.mip,decidir:[]}}).decidir,[]);
chk('MIP origem inválida recusada',pnaMip({mip:{...mr.mip,decidir:[{...visita,origem:'javascript:alert(1)'}]}}),null);
chk('MIP não duplica mesma vistoria entre grupos',pnaMip({mip:{...mr.mip,coleta:[visita]}}),null);
chk('MIP foco identifica vistoria',mv.decidir[0].foco,'mip:VIS-013');
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

def execucao_ui():
    from comp_lib import Chrome,servir
    import shutil
    temp=tempfile.TemporaryDirectory(prefix='pna-exec-ui-');root=Path(temp.name)
    for name in ['PAGR.dc.html','OS.dc.html','support.js']:
        shutil.copy2(Path(__file__).parent/'_render'/name,root/name)
    html=(root/'PAGR.dc.html').read_text()
    fixture="window.__pnaTest={reset:cenReset,get:cenGet,save:cenSave,mode:m=>{const f=agrPainelRef;agrPainelRef=(...a)=>({...f(...a),execucao:m==='empty'?{ordens:[]}:null})}};if(window.__pnaMode)__pnaTest.mode(window.__pnaMode);\n"
    assert html.count('function pnaVals(self,v)')==1
    (root/'PAGR.dc.html').write_text(html.replace('function pnaVals(self,v)',fixture+'function pnaVals(self,v)',1))
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
            J('__pnaTest.reset()');c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Sete ordens e etapas '+str(w),wait("document.querySelectorAll('.pna-exec').length===7"))
            chk('Domínio refletido e conferência não encerrada '+str(w),J("(()=>{let a=document.querySelector('[data-pna-exec=\"OS-0417\"]'),b=document.querySelector('[data-pna-exec=\"OS-0421\"]');return a.innerText.includes('Em conferência')&&a.innerText.includes('Sobra em custódia')&&a.innerText.includes('100%')&&b.innerText.includes('190,00 ha de 350,00 ha')})()"))
            chk('Contexto e alvo44 '+str(w),J("[...document.querySelectorAll('.pna-exec')].every(e=>e.innerText.includes('Safra')&&e.querySelector('a').getBoundingClientRect().height>=44)"))
            J("document.querySelector('[aria-label=\"Como comparar a execução\"]').focus()")
            c.tecla('Enter','Enter',13)
            chk('Fórmula pelo teclado distingue área de encerramento '+str(w),wait("(()=>{let d=document.querySelector('#g2-dica');return d&&!d.hidden&&d.innerText.includes('100% da área não significa')})()"))
            c.tecla('Escape','Escape',27)
            # Apenas fixture sintética: simula apontamento ainda no aparelho, sem chamar comando de produção.
            J("(()=>{let s=__pnaTest.get();s.ordens['OS-0421'].ap.push({dia:9,ha:12,sinc:false});__pnaTest.save(s)})()")
            c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Sinal não aumenta enviada '+str(w),wait("(()=>{let e=document.querySelector('[data-pna-exec=\"OS-0421\"]');return e&&e.innerText.includes('12,00 ha no aparelho')&&e.innerText.includes('190,00 ha de 350,00 ha')})()"))
            J("(()=>{let i=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Café');i.dispatchEvent(new Event('input',{bubbles:true}))})()")
            sel='a[data-pna-grupo="execucao:OS-0421"]'
            J('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"})')
            if os.environ.get('PNA_SHOTS'):
                Path(os.environ['PNA_SHOTS']).mkdir(parents=True,exist_ok=True)
                c.shot(str(Path(os.environ['PNA_SHOTS'])/('execucao-'+str(w)+'.png')))
            if touch:
                xy=J('(()=>{let r=document.querySelector('+json.dumps(sel)+').getBoundingClientRect();return {x:r.left+25,y:r.top+22}})()');c.toque(xy['x'],xy['y'])
            else:
                J('document.querySelector('+json.dumps(sel)+').focus()');c.tecla('Enter','Enter',13)
            chk('Toque ou Enter abre O.S. exata '+str(w),wait("location.pathname.endsWith('OS.dc.html')&&location.hash==='#OS-0421'&&!!document.querySelector('aside[role=dialog]')"))
            J('history.back()')
            chk('Volta ao ponto de execução '+str(w),wait("location.pathname.endsWith('PAGR.dc.html')&&document.activeElement.getAttribute('data-pna-grupo')==='execucao:OS-0421'"))
            chk('Busca de colheita preservada '+str(w),J("document.querySelector('main input[type=search]').value==='Café'"))
            chk('Sem erro e sem overflow '+str(w),J('__errors.length===0&&document.documentElement.scrollWidth<=innerWidth'))
        # Ausência e coleção vazia na composição real, fixture no getter sem alterar o domínio.
        absent=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__pnaMode='missing';"})['identifier']
        c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
        chk('Ausência mostra indisponível sem cartões',wait("document.querySelector('[aria-label=\"Execução das O.S.\"]').innerText.includes('Execução indisponível')&&document.querySelectorAll('.pna-exec').length===0"))
        c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':absent})
        c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__pnaMode='empty';"})
        c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
        chk('Vazio válido mostra nenhuma ordem',wait("document.querySelector('[aria-label=\"Execução das O.S.\"]').innerText.includes('Nenhuma O.S. em execução')"))
    finally:c.close();srv.terminate();temp.cleanup()
    print('RESULTADO execução '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1

def mip_ui():
    from comp_lib import Chrome,servir
    import shutil
    temp=tempfile.TemporaryDirectory(prefix='pna-mip-ui-');root=Path(temp.name)
    for name in ['PAGR.dc.html','AG-01.dc.html','support.js']:
        shutil.copy2(Path(__file__).parent/'_render'/name,root/name)
    html=(root/'PAGR.dc.html').read_text()
    hook="window.__pnaMipReset=()=>{mipReset();cenReset()};if(window.__pnaMipMode){const f=agrPainelRef;agrPainelRef=(...a)=>({...f(...a),mip:window.__pnaMipMode==='empty'?{referencia:'2026-09-23',decidir:[],atrasadas:[],coleta:[]}:null})};\n"
    assert html.count('function pnaVals(self,v)')==1
    (root/'PAGR.dc.html').write_text(html.replace('function pnaVals(self,v)',hook+'function pnaVals(self,v)',1))
    other_html=(root/'AG-01.dc.html').read_text()
    sync_hook="window.__pnaSyncChange=()=>mipMudar(null,s=>{s.vis['VIS-006'].resp='Responsável atualizado na outra aba'});window.__pnaSyncReset=()=>mipReset();\n"
    assert other_html.count('function mipMudar(self, fn)')==1
    (root/'AG-01.dc.html').write_text(other_html.replace('function mipMudar(self, fn)',sync_hook+'function mipMudar(self, fn)',1))
    port,srv=servir(str(root));c=Chrome();J=c.js;checks=[]
    def chk(t,v):checks.append(bool(v));print(('OK ' if v else 'FALHA ')+t,flush=True)
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
            J('__pnaMipReset()');c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
            chk('Seis vistorias sem duplicação '+str(w),wait("document.querySelectorAll('.pna-mip').length===6"))
            chk('Referência e categorias '+str(w),J("(()=>{let e=document.querySelector('[aria-label=\"Atenção no MIP\"]');return e.innerText.includes('23/09/2026')&&e.innerText.includes('Decisão do responsável técnico')&&e.innerText.includes('Vistorias atrasadas')&&e.innerText.includes('Coleta a resolver')})()"))
            chk('NC e presença distintos '+str(w),J("document.querySelector('[data-pna-mip=\"VIS-013\"]').innerText.includes('128% do NC')&&!document.querySelector('[data-pna-mip=\"VIS-055\"]').innerText.includes('%')"))
            chk('Atraso e coleta no aparelho explícitos '+str(w),J("document.querySelector('[data-pna-mip=\"VIS-006\"]').innerText.includes('12 dias de atraso')&&document.querySelector('[data-pna-mip=\"VIS-016\"]').innerText.includes('6 no aparelho')"))
            chk('Alvos44 nomeados '+str(w),J("[...document.querySelectorAll('.pna-mip a')].every(e=>e.getBoundingClientRect().height>=44&&e.getAttribute('aria-label').startsWith('Conferir vistoria VIS-'))"))
            J("document.querySelector('[aria-label=\"Como ler o MIP\"]').focus()");c.tecla('Enter','Enter',13)
            chk('Explicação acessível por teclado '+str(w),wait("(()=>{let e=document.querySelector('#g2-dica');return e&&!e.hidden&&e.innerText.includes('não é percentual de área afetada')})()"));c.tecla('Escape','Escape',27)
            J("(()=>{let i=document.querySelector('main input[type=search]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Café');i.dispatchEvent(new Event('input',{bubbles:true}))})()")
            # Outra aba real, mesmo perfil isolado: gravação pelo domínio dispara storage nativo.
            old_port=os.environ.get('CDP_PORT');os.environ['CDP_PORT']=str(c.port)
            try:other=Chrome()
            finally:
                if old_port is None:os.environ.pop('CDP_PORT',None)
                else:os.environ['CDP_PORT']=old_port
            try:
                other.goto(f'http://127.0.0.1:{port}/AG-01.dc.html',1)
                J("window.__pnaSyncDocument=1;document.querySelector('main input[type=search]').focus()")
                other.js('__pnaSyncChange()')
                chk('MIP atualiza sem recarregar após outra aba '+str(w),wait("document.querySelector('[data-pna-mip=\"VIS-006\"]').innerText.includes('Responsável atualizado na outra aba')"))
                chk('Sincronização preserva documento, busca e foco '+str(w),J("__pnaSyncDocument===1&&document.querySelector('main input[type=search]').value==='Café'&&document.activeElement===document.querySelector('main input[type=search]')"))
                other.js('__pnaSyncReset()')
                chk('Reset externo também atualiza sem recarregar '+str(w),wait("!document.querySelector('[data-pna-mip=\"VIS-006\"]').innerText.includes('Responsável atualizado na outra aba')"))
            finally:other.close()
            sel='a[data-pna-grupo="mip:VIS-055"]'
            J('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"})')
            if os.environ.get('PNA_SHOTS'):
                Path(os.environ['PNA_SHOTS']).mkdir(parents=True,exist_ok=True)
                c.shot(str(Path(os.environ['PNA_SHOTS'])/('mip-'+str(w)+'.png')))
            if touch:
                xy=J('(()=>{let r=document.querySelector('+json.dumps(sel)+').getBoundingClientRect();return {x:r.left+25,y:r.top+22}})()');c.toque(xy['x'],xy['y'])
            else:J('document.querySelector('+json.dumps(sel)+').focus()');c.tecla('Enter','Enter',13)
            chk('Vistoria exata abre por Enter/toque '+str(w),wait("location.pathname.endsWith('AG-01.dc.html')&&location.hash==='#VIS-055'&&[...document.querySelectorAll('[role=dialog]')].some(e=>e.offsetParent&&e.innerText.includes('VIS-055'))"))
            J('history.back()')
            chk('Foco volta à vistoria '+str(w),wait("location.pathname.endsWith('PAGR.dc.html')&&document.activeElement.getAttribute('data-pna-grupo')==='mip:VIS-055'"))
            chk('Busca conservada e sem JS/overflow '+str(w),J("document.querySelector('main input[type=search]').value==='Café'&&__errors.length===0&&document.documentElement.scrollWidth<=innerWidth"))
        mode=c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__pnaMipMode='missing';"})['identifier']
        c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
        chk('MIP ausente não vira sem pendências',wait("document.querySelector('[aria-label=\"Atenção no MIP\"]').innerText.includes('Dados de MIP indisponíveis')&&document.querySelectorAll('.pna-mip').length===0"))
        c.call('Page.removeScriptToEvaluateOnNewDocument',{'identifier':mode});c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__pnaMipMode='empty';"})
        c.goto(f'http://127.0.0.1:{port}/PAGR.dc.html',1)
        chk('MIP vazio tem três mensagens específicas',wait("(()=>{let t=document.querySelector('[aria-label=\"Atenção no MIP\"]').innerText;return t.includes('Nenhuma decisão pendente')&&t.includes('Nenhuma vistoria atrasada')&&t.includes('Nenhuma coleta pendente')})()"))
    finally:c.close();srv.terminate();temp.cleanup()
    print('RESULTADO MIP '+str(sum(checks))+'/'+str(len(checks)));return 0 if all(checks) else 1

if __name__=='__main__':sys.exit(mip_ui() if '--mip-ui' in sys.argv else execucao_ui() if '--execucao-ui' in sys.argv else grupos_ui() if '--grupos-ui' in sys.argv else custos_ui() if '--custos-ui' in sys.argv else os_contract_ui() if '--os-contract-ui' in sys.argv else prepare() if '--prepare' in sys.argv else ui() if '--ui' in sys.argv else unit())
