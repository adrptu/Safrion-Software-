# -*- coding: utf-8 -*-
"""Teste CDP · UX-ACAO-UNICA-20261003 v2 (padrão de comandos, patch c691c431 · cap. 74 DS-02/26/29/31/33/40/54/61/63, DS-AC-08/17).
Pedido do Adrianus: no Planejar safra, clicar nas etapas, usar as setas e clicar em "Definir rendimentos" mudavam a etapa por três
caminhos; "com tantas opções o usuário fica perdido". Uma tarefa ativa = uma primária e uma rota de avanço; a faixa só informa.
Modos (cada um < 90 s; capturas em _probe/acao_*.png):
  python3 acao_unica_test.py saf          1-9   Planejar safra: faixa informativa, uma primária por estado, Planejar › na linha do talhão, falta de
                                                plano, vazio, filtro sem resultado, Corrigir cultivos → revisão, avançar não envia
  python3 acao_unica_test.py familias     10-16 uma ocorrência por família: CMP, PA, PM, EST (seções), IR/MA (telas), O.S. (Lista/Kanban/
                                                Recursos com o mesmo filtro), mapa (painel do talhão)
  python3 acao_unica_test.py responsivo   17-19 matriz RESPONSIVIDADE (360×800, 800×360, 768×1024, 1024×768, 1280×720, 1440×900, zoom 200 %)
                                                + teclado virtual aberto; 16ª parcela com o teclado aberto (contraprova Gemini)
  python3 acao_unica_test.py gemini       20-22 contraprovas Gemini: (a) alvo da faixa do app ao reordenar, (b) lote com IDs ocultos e
                                                prévia, (c) corrigir trecho e voltar direto à revisão (com o teclado)
  python3 acao_unica_test.py v3           23-29 PADRAO-COMANDOS v3/v3.1 nos estados: duplicatas (medida de acoes_duplicadas.py) e primárias
                                                com seleção ativa, painel aberto, decisão de saída, impedimento, consulta, 360/768/zoom 200 %;
                                                seleção → buscar outro → somar → abrir detalhe e voltar; tipo por função (expandir, filtro, visão)
Emulação no Chrome headless (largura × altura em px CSS, escala, toque, sem hover): não é aparelho físico."""
import sys, os, time, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from comp_lib import Chrome, servir, IR_ETAPA, troca_visao
MODO=sys.argv[1] if len(sys.argv)>1 else 'saf'
PROBE=os.path.join(HERE,'_probe'); os.makedirs(PROBE,exist_ok=True)
OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:1400]),flush=True)
def info(t,v): print('     (informativo)',t,str(v)[:900],flush=True)
p,srv=servir(os.environ.get('RENDER_DIR') or os.path.join(HERE,'_render')); c=None; ERRL=[]
N="(s=>(s||'').replace(/\\s+/g,' ').trim())"
# estado de comandos da tela: primárias visíveis (botão/link verde cheio no cabeçalho e no conteúdo), área de ações e etapa atual
EST=r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const dlg=[...document.querySelectorAll('aside[role=dialog]')].find(vis);
 const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
 const prims=[...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>vis(e)&&verde(e)&&!e.closest('.menu-lat')).map(e=>n(e.innerText).slice(0,48));
 const a=document.querySelector('[data-acoes]'); const area=a&&vis(a)?[...a.querySelectorAll('button,a,.acoes-nota')].filter(vis).map(e=>(e.dataset.acao||'nota')+':'+n(e.innerText).slice(0,90)):[];
 const cur=document.querySelector('.etp-ind [aria-current=step]'); const k=cur?Number((n(cur.innerText).match(/\d+/)||[0])[0]):0;
 return {etapa:k, prims, area, avancos:area.filter(x=>x.startsWith('avancar:')).length, dialogo:!!dlg};})()"""
def errs(): return [e for e in (c.js("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
def abre(pg,w=1440,h=900,e=1,t=False,hash='',espera=.7,limpa=True):
    if c and c.alvo: ERRL.extend(errs())
    c.aparelho(w,h,e,t)
    if limpa:
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html',.2); c.js("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/{pg}.dc.html{hash}',espera)
def J(x): return c.js(x)
def est(): return J(EST)
def clk(t,raiz=None,w=.45):
    r=J(f"""((t,root)=>{{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,label,[role=button],[role=tab]')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'').startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';}})({json.dumps(t)},{json.dumps(raiz)})"""); time.sleep(w); return r
def acao(tipo,w=.5):
    r=J(f"(()=>{{const b=document.querySelector('[data-acoes] [data-acao={tipo}]'); if(!b) return 'sem '+{json.dumps(tipo)}; b.scrollIntoView({{block:'center'}}); b.click(); return b.innerText.trim();}})()"); time.sleep(w); return r
def etapa(n): r=J(f"({IR_ETAPA})({n})"); time.sleep(.3); return r
def setv(sel,val):
    return J(f"""(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'sem campo'; const P=e.tagName==='SELECT'?HTMLSelectElement.prototype:(e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()""")
def shot(nome): c.shot(os.path.join(PROBE,f'acao_{nome}.png'))
def rolagem():   # posição de leitura: a soma das rolagens da casca, do conteúdo e das caixas de tabela da tela
    return J("(()=>{const col=document.querySelector('.ml-tog+div'); const m=document.querySelector('main[data-scroll]'); return Math.round((col?col.scrollTop:0)+(m?m.scrollTop:0)+[...document.querySelectorAll('main .g2rola,main .rola')].reduce((a,x)=>a+x.scrollTop,0));})()")
try:
    c=Chrome()
    if MODO=='saf':
        # 1 · faixa só informa: lista ordenada sem botão, link, handler ou parada de Tab; palavra do estado; clicar não navega; sem setas
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3)
        fx=J(r"""(()=>{const f=document.querySelector('.etp-ind'); const ol=f&&f.querySelector('ol[aria-label="Etapas do processo"]'); const lis=ol?[...ol.children]:[];
          return {tag:f?f.tagName:'', ol:!!ol, n:lis.length, li:lis.every(x=>x.tagName==='LI'), ctl:f?f.querySelectorAll('button,a,[tabindex],[onclick],[role=button]').length:-1,
            atual:(ol&&ol.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\s+/g,' ').trim(), sr:[...(f?f.querySelectorAll('.etp-sr'):[])].map(x=>x.textContent.trim()),
            setas:document.querySelectorAll('[aria-label^="Etapa anterior"],[aria-label^="Próxima etapa"]').length, cursor:lis[2]?getComputedStyle(lis[2]).cursor:''};})()""")
        J("document.querySelectorAll('.etp-ind ol>li')[2].click()"); time.sleep(.4); e1=est()
        J("document.activeElement&&document.activeElement.blur()"); paradas=[]
        for _ in range(45):
            c.tab(); paradas.append(J("(()=>{const a=document.activeElement; return a?(a.closest('.etp-ind')?'FAIXA':(a.closest('[data-acoes]')?'AREA':'')):'';})()"))
        shot('saf_faixa_1440')
        chk('1 SAF · faixa só informa: lista ordenada de 4 etapas sem botão/link/handler/Tab (0 controles), palavra do estado (concluída/etapa atual/pendente), cursor comum, clicar na etapa 3 não navega, nenhuma seta ‹ › e 45 Tabs nunca param na faixa',
            fx['tag']=='DIV' and fx['ol'] and fx['n']==4 and fx['li'] and fx['ctl']==0 and fx['atual'].startswith('2 ') and 'concluída' in ' '.join(fx['sr']) and 'etapa atual' in ' '.join(fx['sr']) and 'pendente' in ' '.join(fx['sr'])
            and fx['cursor']!='pointer' and fx['setas']==0 and e1['etapa']==2 and 'FAIXA' not in paradas, [fx,e1,paradas])
        # 2 · uma primária e uma rota de avanço por estado, sem cópia do mesmo comando (cabeçalho, bloco, faixa, área)
        estados={}
        abre('SAF'); estados['1 sem safra']=est()
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3); estados['2 falta plano']=est(); shot('saf_etapa2_falta_plano')
        # 2b · a área de ações não toma o lugar da lista: a tabela da etapa estica até a área, e a área fica no pé do conteúdo (1440×900)
        lay=J(r"""(()=>{const m=document.querySelector('main[data-scroll]'); const r=[...m.querySelectorAll('.g2rola')].find(x=>x.getClientRects().length); const a=document.querySelector('[data-acoes]'); const ra=a.getBoundingClientRect(), rm=m.getBoundingClientRect();
          return {tabela:Math.round(r.getBoundingClientRect().height), linhas:r.querySelectorAll('[role=row]').length, area:Math.round(ra.height), folga:Math.round(rm.bottom-ra.bottom), mainRola:m.scrollHeight>m.clientHeight+1};})()""")
        chk('2b SAF · a tabela de cultivos estica até a área de ações (≥ 300 px, todas as linhas cabem ou rolam dentro dela) e a área fica no pé do conteúdo (≤ 40 px do fim, altura ≤ 140 px), sem rolagem dupla',
            lay['tabela']>=300 and lay['area']<=140 and 0<=lay['folga']<=40 and not lay['mainRola'], lay)
        for i in (3,4): etapa(i); estados[f'{i}']=est()
        shot('saf_etapa4_revisao')
        def uma(s): return len(s['prims'])<=1 and s['avancos']<=1 and all(s['prims'].count(x)==1 for x in s['prims'])
        rotulos={k:[a.split(':',1)[1] for a in v['area'] if a.startswith(('avancar:','resolver:','comando:','abrir:'))] for k,v in estados.items()}
        sem_copia=all(sum(1 for x in J(f"[...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>e.getClientRects().length).map(e=>{N}(e.innerText))") if x==t)<=1 for t in rotulos['4'])
        chk('2 SAF · no máximo uma primária e uma rota de avanço em cada estado (sem safra, falta de plano, etapas 3 e 4), sem cópia do mesmo comando; Nova safra secundária',
            all(uma(s) for s in estados.values()) and estados['1 sem safra']['prims']==[] and estados['2 falta plano']['prims']==['Aplicar plano em 4 cultivos'] and estados['2 falta plano']['avancos']==1
            and estados['3']['prims']==['Conferir demanda de insumos ›'] and estados['4']['prims']==['Abrir Compra de insumos ›'] and sem_copia,
            {k:(v['etapa'],v['prims'],v['area']) for k,v in estados.items()})
        # 3 · etapa 2 nova (todos os talhões): sem "Adicionar cultivo"; "Planejar ›" na linha do talhão abre o painel sem trocar de etapa e
        #     preserva o rascunho (Esc → Continuar editando)
        abre('SAF',hash='#saf=S27SF&passo=cultivos'); time.sleep(.4); nadd=J("document.querySelectorAll('[data-acao=adicionar]').length")
        b=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.querySelector('.g2c0')&&/^[▾▸]?\\s?T3\\s/.test(x.querySelector('.g2c0').innerText.trim()+' ')); const b=r&&[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Planejar ›'); if(!b) return null; const h=b.closest('section')&&b.closest('section').querySelector('h3'); b.click(); return [b.innerText.trim(), h?h.innerText.trim():''];})()"); time.sleep(.5)
        campo=J("(()=>{const d=document.querySelector('aside[role=dialog]'); const i=d&&[...d.querySelectorAll('input')].find(x=>/_var$/.test(x.id)); return i?i.id:null;})()")
        setv('#'+campo,'Teste ação única') if campo else None; time.sleep(.2); J(f"document.getElementById({json.dumps(campo)}).focus()")
        c.tecla('Escape','Escape',27); time.sleep(.3); aviso='Há alterações não salvas' in (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '')
        clk('Continuar editando','aside[role=dialog]'); val=J(f"(document.getElementById({json.dumps(campo)})||{{value:''}}).value") if campo else ''; e3=est(); shot('saf_planejar_rascunho')
        clk('Cancelar','aside[role=dialog]'); clk('Descartar alterações','aside[role=dialog]')
        chk('3 SAF · sem "Adicionar cultivo" (0); "Planejar ›" do T3 na tabela "Talhões e cultivos" abre o painel sem trocar de etapa; Esc pede confirmação e "Continuar editando" mantém o texto digitado',
            nadd==0 and b and b[0]=='Planejar ›' and b[1]=='Talhões e cultivos' and bool(campo) and aviso and val=='Teste ação única' and e3['etapa']==2, [nadd,b,campo,aviso,val,e3['etapa']])
        # 4 · falta de plano: causa escrita + passo que resolve; avançar não aplica plano em silêncio
        abre('SAF',hash='#saf=S2627&passo=cultivos'); time.sleep(.3)
        e4=est(); k2a=' '.join(a for a in e4['area'] if a.startswith('nota:'))
        acao('avancar'); e4b=est(); etapa(2); k2b=' '.join(a for a in est()['area'] if a.startswith('nota:'))
        chk('4 SAF · falta de plano: nota com a causa e os talhões, "Aplicar plano em 4 cultivos" é a primária (resolver) e "Dimensionar operações ›" o único avanço, secundário; avançar leva à etapa 3 sem aplicar plano (4 sem plano antes e depois, na nota)',
            any(a.startswith('nota:4 cultivos sem plano agronômico (T4, T3, P1, P2)') for a in e4['area']) and 'resolver:Aplicar plano em 4 cultivos' in e4['area'] and 'avancar:Dimensionar operações ›' in e4['area']
            and e4b['etapa']==3 and '4 cultivos sem plano' in k2a and '4 cultivos sem plano' in k2b, [e4['area'],e4b['etapa'],k2a,k2b])
        # 5 · vazio: safra nova sem cultivos → nenhuma primária e nenhum avanço; a nota diz o que está livre e a conferir e manda planejar na linha
        abre('SAF'); clk('Nova safra'); time.sleep(.3)
        for k,vl in (('nome','Safra teste ação única'),('ini','2027-01-10'),('fim','2027-08-30')): setv(f'#fx_g_saf_{k}',vl)
        clk('Salvar','aside[role=dialog]'); time.sleep(.6); e5=est(); shot('saf_vazio')
        tal=J(r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return {}; const o={}; [...t.querySelectorAll('[role=row]')].slice(1).filter(r=>!r.classList.contains('g2kid')).forEach(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; const c0=r.querySelector('.g2c0'); if(!c0) return; const nm=c0.innerText.replace(/^[▾▸] ?/,'').trim().split(/\s+/)[0]; const sr=r.querySelectorAll('.g2sr'); let txt=cs.map(c=>{ let x=c.innerText; c.querySelectorAll('.g2sr').forEach(e=>{ x=x.replace(e.innerText,''); }); return x.replace(/\s+/g,' ').trim(); }); o[nm]={c0:c0.innerText.replace(/\s+/g,' ').trim(),cs:txt}; }); return o; })()""")
        t1=tal.get('T1',{}).get('cs',[]); t7=tal.get('T7',{}).get('c0',''); c1=tal.get('C1',{}).get('c0','')
        chk('5 SAF · safra nova sem cultivos: etapa 2 sem primária e sem avanço, nota "Nenhum cultivo nesta safra…"; T7 e C1 Perene sem Planejar nem Vincular; T1 Livre 152 ha a partir de 21/02/2027',
            e5['etapa']==2 and e5['prims']==[] and e5['avancos']==0 and any(a.startswith('nota:Nenhum cultivo nesta safra') for a in e5['area'])
            and 'Planejar' not in t7 and 'Vincular' not in t7 and 'Planejar' not in c1 and 'Vincular' not in c1 and 'Livre' in t1 and '152 ha' in t1 and '21/02/2027' in t1, [e5,t7,c1,t1])
        # 6 · filtro sem resultado: o próximo passo é limpar o filtro, dentro da lista; a área continua com o passo da etapa; uma primária
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3)
        r=setv('main input[type=search]','zzz-sem-resultado'); time.sleep(.5)
        e6=est(); lim=J("(()=>{const m=document.querySelector('main'); return [...m.querySelectorAll('button')].filter(b=>b.getClientRects().length&&/^Limpar/.test(b.innerText.trim())).map(b=>b.innerText.trim());})()")
        linhas=J("[...document.querySelectorAll('main [role=row].g2ed')].filter(e=>e.getClientRects().length).length"); shot('saf_filtro_sem_resultado')
        chk('6 SAF · filtro sem resultado: 0 linhas, "Limpar…" dentro da lista (secundário) e a área mantém o passo da etapa; no máximo uma primária',
            r=='ok' and linhas==0 and bool(lim) and len(e6['prims'])<=1 and e6['avancos']==1, [r,linhas,lim,e6])
        # 7 · revisão → "Corrigir cultivos" → trecho exato → "Voltar à revisão" com filtro, rascunho da tela e posição preservados
        abre('SAF',1280,640,hash='#saf=S2627&etapa=6'); time.sleep(.4)
        setv('main input[type=search]','o'); time.sleep(.4)
        J("(()=>{const m=document.querySelector('main[data-scroll]'); const rs=[m,...m.querySelectorAll('.g2rola,.rola')].filter(x=>x.scrollHeight>x.clientHeight+20); rs.forEach(x=>{ x.scrollTop=Math.min(240,x.scrollHeight-x.clientHeight); });})()"); time.sleep(.3)
        y0=rolagem(); nota0=[a for a in est()['area'] if a.startswith('nota:')]
        r=J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=corrigir]'); if(!b) return 'sem Corrigir'; b.click(); return b.innerText.trim();})()"); time.sleep(.7)
        e7=est(); foco=J("(()=>{const a=document.activeElement; const r=a&&a.closest('[role=row]'); return r?(r.innerText.match(/\\b(T4|T3|P1|P2)\\b/)||[''])[0]:(a?a.tagName:'');})()"); shot('saf_corrigir_trecho')
        acao('resolver'); time.sleep(.3)
        ok_sel=J("(()=>{const s=document.querySelector('#ap_sel'); if(!s) return 'sem plano'; const o=[...s.options].find(x=>x.value); if(!o) return 'sem opção'; const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,o.value); s.dispatchEvent(new Event('change',{bubbles:true})); return o.textContent;})()"); time.sleep(.3)
        clk('Aplicar plano','aside[role=dialog]'); time.sleep(.5); clk('Confirmar substituição','aside[role=dialog]',.4)
        e7b=est(); r2=acao('avancar',.9); e7c=est(); y1=rolagem(); q=J("(document.querySelector('main input[type=search]')||{value:''}).value"); nota1=[a for a in e7c['area'] if a.startswith('nota:')]
        f2=J("(()=>{const a=document.activeElement; return a?(a.dataset.acao||a.tagName):'';})()"); shot('saf_volta_revisao')
        chk('7 SAF · "Corrigir cultivos" na revisão leva à etapa 2 com o foco no 1º cultivo sem plano e "Aplicar plano" + "Voltar à revisão ›"; depois de aplicar, volta direto à etapa 4 na mesma posição de rolagem (±4 px), com a busca "o" e a pendência recalculada (1280×640)',
            r=='Corrigir cultivos' and e7['etapa']==2 and foco in ('T4','T3','P1','P2') and any('Correção pedida pela revisão' in a for a in e7['area']) and 'avancar:Voltar à revisão ›' in e7['area']
            and r2.startswith('Voltar à revisão') and e7c['etapa']==4 and y0>0 and abs(y1-y0)<=4 and q=='o' and nota1!=nota0, [r,e7['area'],foco,ok_sel,e7b['area'],r2,e7c['etapa'],y0,y1,q,nota0,nota1,f2])
        # 8 · avançar não envia: Safrinha 2027 (não enviada) → etapa 4 com "Enviar para cotação" (comando) distinto; andar 6→2→6 não cria solicitação
        abre('SAF'); r=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem'; b.click(); return b.innerText.trim();})()"); time.sleep(.6)
        e8=est(); etapa(2); etapa(4); e8b=est(); ls=J("localStorage.getItem('talhao-os-compras-v1')"); k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
        abr=J(f"[...document.querySelectorAll('main a,main button')].filter(e=>e.getClientRects().length&&/Abrir Compra de insumos/.test({N}(e.innerText))).length"); shot('saf_enviar_distinto')
        chk('8 SAF · avançar só troca de etapa: Safrinha 2027 na etapa 4 tem "Enviar para cotação" como comando (não avanço); 4→2→4 pela área não envia (nada gravado, "ainda não enviada") e não mostra "Abrir Compra de insumos"',
            e8['etapa']==4 and 'comando:Enviar para cotação' in e8['area'] and e8b['etapa']==4 and 'comando:Enviar para cotação' in e8b['area'] and not ls and 'ainda não enviada' in k6 and abr==0, [r,e8,e8b['area'],ls,k6,abr])
        ERRL.extend(errs()); chk('9 sem erro de JS (SAF)', not ERRL, ERRL[:5])
    elif MODO=='familias':
        fam={}
        # 10 · CMP: etapa 2 avanço único; 3 antes do envio só o comando; avançar até 6 não aprova
        abre('CMP'); clk('Abrir compra'); a2=est(); etapa(3); a3=est(); clk('Enviar convites (simulado)'); time.sleep(6.8); etapa(4); etapa(5); a5=est(); shot('cmp_etapa5')
        acao('avancar',.6); a6=est(); b=J("document.body.innerText")
        chk('10 CMP · etapa 2: "Solicitar cotações ›" único; etapa 3 antes do envio: só o comando "Enviar convites (simulado)" com a causa; etapa 5: comando "Enviar à Direção" + avanço secundário; ir à etapa 6 não aprova (sem "Compra aprovada", sem PC-101)',
            a2['prims']==['Solicitar cotações ›'] and a2['avancos']==1 and a3['prims']==['Enviar convites (simulado)'] and a3['avancos']==0 and a5['prims']==['Enviar à Direção'] and a5['avancos']==1 and a6['etapa']==6 and 'Compra aprovada' not in b and 'PC-101' not in b,
            [a2,a3,a5,a6['etapa']])
        # 11 · PA (NAV-1: lista → detalhe, sem etapas; design system 09/10, BOT-01/02/03/06): lista com o único verde "Criar plano" no
        #      cabeçalho; detalhe sem rascunho sem primária ("Incluir atividade" secundário no bloco); com rascunho, "Salvar alterações"
        #      a única primária, no Próximo passo; nenhum avanço que só navega ("Revisar e publicar", "Ver versões e cultivos")
        abre('PA'); p1=est(); novo=J(f"(()=>{{const b=[...document.querySelectorAll('header button')].find(b=>{N}(b.innerText)==='Criar plano'); return b?getComputedStyle(b).backgroundColor:null;}})()")
        J("document.querySelector('main .g2card').click()"); time.sleep(.5); p2=est(); inc=J(f"[...document.querySelectorAll('main button')].filter(b=>b.getClientRects().length&&{N}(b.innerText)==='Incluir atividade').map(b=>getComputedStyle(b).backgroundColor)")
        rp=J(f"[...document.querySelectorAll('main button,[data-acoes] button')].filter(b=>b.getClientRects().length&&/Revisar e publicar|Ver versões e cultivos/.test(b.innerText)).length")
        J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>(b.getAttribute('aria-label')||'').startsWith('Mostrar insumos de Fungicida 1ª aplicação')); b.click();})()"); time.sleep(.3)
        J("[...document.querySelectorAll('main button.pa-dose')][0].click()"); time.sleep(.3); c.call('Input.insertText',{'text':'0,6'}); c.tecla('Enter','Enter',13,text='\r'); time.sleep(.5); p3=est(); shot('pa_detalhe_rascunho')
        chk('11 PA · lista: "Criar plano" o único verde, no cabeçalho; detalhe sem rascunho: sem primária, "Incluir atividade" secundário e só "‹ Biblioteca de planos" na área; com rascunho: "Salvar alterações" a única primária, como comando; nenhum avanço que só navega',
            p1['prims']==['Criar plano'] and novo=='rgb(30, 122, 76)' and p1['etapa']==0 and p2['etapa']==0 and inc==['rgb(255, 255, 255)'] and rp==0 and p2['prims']==[] and p2['avancos']==0 and p2['area']==['voltar:‹ Biblioteca de planos']
            and p3['prims']==['Salvar alterações'] and p3['avancos']==0 and 'comando:Salvar alterações' in p3['area'],   # PA-SALVAR (14/10): "lá embaixo deixe o botão salvar"
            [p1,novo,p2,inc,rp,p3])
        # 12 · Planos (PCM simplificado S1: PM.dc.html virou a visão Planos da tela MA, ESPECIFICACAO §3.5 "primária: Novo plano"): uma primária na visão;
        #      plano aberto: retorno "‹ Planos", sem etapas e no máximo uma primária ("Publicar vN" só com rascunho)
        abre('MA',hash='#vis=planos'); J("localStorage.setItem('safrion.perfilDemo','Otávio')"); c.goto('about:blank',.2); c.goto(f'http://127.0.0.1:{p}/MA.dc.html#vis=planos',.8); m1=est()   # Ver como Otávio (o comando é dele)
        r=J("(()=>{const r=[...document.querySelectorAll('main [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='PM-01'); if(!r) return 'sem linha'; (r.querySelector('.g2pw')||r).click(); return 'PM-01';})()"); time.sleep(.6); m2=est(); shot('ma_plano')
        vt=J("[...document.querySelectorAll('main button,main a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim()).filter(t=>t.startsWith('‹'))")
        chk('12 Planos (tela MA) · visão com uma primária "Novo plano"; plano aberto: retorno "‹ Planos", sem etapas e no máximo uma primária',
            m1['prims']==['Novo plano'] and m1['etapa']==0 and r=='PM-01' and m2['etapa']==0 and '‹ Planos' in vt and len(m2['prims'])<=1, [m1,r,m2,vt])
        # 13 · EST: trabalho paralelo → seções (navegação em qualquer ordem), sem número de etapa e sem setas; seção sem trabalho não ganha "ir para a próxima"
        abre('EST'); s0=J(r"""(()=>{const n=document.querySelector('nav[aria-label="Seções do estoque"]'); const bs=n?[...n.querySelectorAll('.etp-itens>button')]:[]; return {n:bs.length, nums:bs.filter(b=>/^\d/.test(b.innerText.trim())).length, cur:(n&&n.querySelector('[aria-current=true]')||{innerText:''}).innerText.trim(), setas:document.querySelectorAll('[aria-label^="Etapa anterior"],[aria-label^="Próxima etapa"]').length, ind:!!document.querySelector('.etp-ind')};})()""")
        clk('Faça contagens','nav[aria-label="Seções do estoque"]'); s5=est(); clk('Confira saldos','nav[aria-label="Seções do estoque"]'); s4=est(); cur4=J("(document.querySelector('nav.etp-sec [aria-current=true]')||{innerText:''}).innerText.trim()"); shot('est_secoes')
        chk('13 EST · "Seções do estoque": 6 seções sem número e sem setas, atual com aria-current; ir direto a Contagens e a Saldos; Saldos (consulta) sem primária de navegação',
            s0['n']==6 and s0['nums']==0 and s0['setas']==0 and not s0['ind'] and s0['cur']=='Confira recebimentos' and len(s5['prims'])<=1 and s4['prims']==[] and cur4=='Confira saldos', [s0,s5,s4,cur4])
        # 14 · IR e MA: telas irmãs (navegação, aria-current=page), sem setas e sem número; pendência escrita
        tel={}
        for pg,lab,n in (('IR-02','Telas da irrigação',4),('MA','Telas da manutenção',5)):   # PCM simplificado (S1, D-05): a faixa da Manutenção sai (tela única MA)
            abre(pg); tel[pg]=J(f"""(()=>{{const n=document.querySelector('nav[aria-label="{lab}"]'); const as=n?[...n.querySelectorAll('.etp-itens>a')]:[]; return [as.length, as.filter(a=>a.getAttribute('aria-current')==='page').map(a=>a.innerText.replace(/\\s+/g,' ').trim()), as.filter(a=>/^\\d/.test(a.innerText.trim())).length, document.querySelectorAll('[aria-label^="Etapa anterior"],[aria-label^="Próxima etapa"]').length, as.map(a=>a.innerText.replace(/\\s+/g,' ').trim()).join(' | ')];}})()""")
        shot('ma03_telas')
        chk('14 IR · faixa de telas irmãs ("Telas da irrigação" 4): links com aria-current="page", sem número de etapa e sem setas; pendência escrita (ex.: "1 conflito"); MA sem a faixa "Telas da manutenção" (D-05: o seletor de visão a substitui)',
            tel['IR-02'][0]==4 and tel['IR-02'][1][:1] and tel['IR-02'][1][0].startswith('Programe a irrigação') and tel['IR-02'][2]==0 and tel['IR-02'][3]==0 and 'conflito' in tel['IR-02'][4]
            and tel['MA'][0]==0, tel)
        # 15 · O.S.: Lista e Kanban com o mesmo filtro (reproduzido antes: 2 × 10); Recursos explica a granularidade; fase não muda por clique
        abre('OS'); o0=est(); clk('Liberadas','[aria-label="Filtrar por fase"]'); lis=J("[...document.querySelectorAll('main [role=row].g2ed')].filter(e=>e.getClientRects().length).map(r=>r.innerText.split('\\n')[0].trim())")
        troca_visao(J,'kanban','[aria-label="Visão das ordens"]'); kb=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].filter(e=>e.getClientRects().length).map(b=>b.getAttribute('aria-label').split(' ')[1])")
        # VISOES-2 §8 ponto 3: o recorte vira a faixa [data-os-recorte] (contagem, chips removíveis e "Limpar filtros"); a fase fica nos chips de fase
        nota=J("(()=>{const n=[...document.querySelectorAll('main [data-os-recorte]')].find(e=>e.getClientRects().length); return n?n.innerText.replace(/\\s+/g,' ').trim():'';})()"); shot('os_kanban_filtro')
        troca_visao(J,'carga','[aria-label="Visão das ordens"]'); rc=J("(()=>{const n=[...document.querySelectorAll('main [role=note]')].find(e=>e.getClientRects().length); return n?n.innerText.replace(/\\s+/g,' ').trim():'';})()")
        troca_visao(J,'kanban','[aria-label="Visão das ordens"]'); clk('Limpar filtros'); kb2=J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].filter(e=>e.getClientRects().length).length")
        troca_visao(J,'lista','[aria-label="Visão das ordens"]'); J("(()=>{const r=document.querySelector('[role=row].g2ed'); (r.querySelector('[role=cell] b')||r).click();})()"); time.sleep(.5)
        fase0=J("(()=>{const d=document.querySelector('aside[role=dialog]'); return d?(d.innerText.match(/A liberar|Liberadas|Em execução|Em conferência|Encerradas/)||[''])[0]:'';})()")
        ctl=J("(()=>{const d=document.querySelector('aside[role=dialog]'); if(!d) return -1; return [...d.querySelectorAll('button,a,[role=button]')].filter(b=>/^(A liberar|Liberadas|Em execução|Em conferência|Encerradas)$/.test(b.innerText.trim())).length;})()")
        o1=est()
        chk('15 O.S. · Lista e Kanban com o mesmo filtro de fase (Liberadas: 2 = 2, antes 2 × 10), Kanban diz o filtro e oferece "Limpar filtros" (volta a 10), Recursos segue o mesmo recorte e diz qual (TABELAS-FOCO); "Nova ordem" a única primária; no painel a fase é texto, não comando',
            sorted(lis)==sorted(kb) and len(kb)==2 and '2 de 10 ordens no recorte' in nota and 'Limpar filtros' in nota and 'só os blocos das ordens de Santa Rita no recorte' in rc and kb2==10 and o0['prims']==['Nova ordem'] and fase0 and ctl==0 and len(o1['prims'])<=1, [lis,kb,nota,rc,kb2,o0['prims'],fase0,ctl,o1['prims']])
        # 15b · O.S. "Ajustar antes de liberar" (360×800, toque): rodapé do formulário preso ao pé do painel, Voltar à esquerda e a
        #       primária à direita, alcançável sem rolar até o fim e sem cobrir o campo focado
        abre('OS',360,800,3,True); aj='sem ordem'
        for oid in ('OS-0418','OS-0430','OS-0431','OS-0420'):
            J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(oid)})>=0); if(r) (r.querySelector('[role=cell] b')||r).click();}})()"); time.sleep(.5)
            if J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.getClientRects().length&&b.innerText.trim()==='Ajustar antes de liberar')"):
                clk('Ajustar antes de liberar','aside[role=dialog]',.5); aj=oid; break
            J("(()=>{const b=document.querySelector('aside[role=dialog] [aria-label=\"Fechar painel\"],[aria-label=\"Fechar painel\"]'); if(b) b.click();})()"); time.sleep(.3)
        J("(()=>{const i=document.getElementById('aj_area'); if(i){ i.scrollIntoView({block:'start'}); i.focus(); }})()"); time.sleep(.3)
        rf=J(r"""(()=>{const f=document.querySelector('.acoes-form'); if(!f) return null; const bs=[...f.querySelectorAll('button')]; const d=f.closest('aside'); const rd=d.getBoundingClientRect(); const p=bs[bs.length-1], v=bs[0]; const rp=p.getBoundingClientRect(), rv=v.getBoundingClientRect();
          const h=document.elementFromPoint(rp.left+rp.width/2,rp.top+rp.height/2); const i=document.getElementById('aj_area'); const ri=i.getBoundingClientRect(); const hi=document.elementFromPoint(ri.left+8,ri.top+ri.height/2);
          return {pos:getComputedStyle(f).position, ordem:[v.innerText.trim(),p.innerText.trim()], esquerdaDireita:rv.left<rp.left, primVisivel:!!h&&(h===p||p.contains(h))&&rp.bottom<=Math.min(rd.bottom,innerHeight)+1, campoLivre:!!hi&&(hi===i||i.contains(hi)), rolaFalta:Math.round(d.scrollHeight-d.clientHeight-d.scrollTop)};})()"""); shot('os_ajustar_rodape_360')
        chk('15b O.S. "Ajustar antes de liberar" (360×800) · rodapé do formulário preso (sticky): Voltar à esquerda, primária à direita e visível sem rolar até o fim; o campo de área focado continua livre',
            bool(rf) and rf['pos']=='sticky' and rf['ordem'][0]=='Voltar' and rf['esquerdaDireita'] and rf['primVisivel'] and rf['campoLivre'], [aj,rf])
        # 16 · mapa: painel do talhão com um próximo passo (sem cópia no cabeçalho)
        abre('IN-04'); J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); if(s){ s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true})); }})()"); time.sleep(.6)
        J("(()=>{const p=document.querySelector('main polygon[role=button],main circle[role=button],main path[role=button]'); if(p) p.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()"); time.sleep(.6)
        mp=est(); pn=J("(()=>{const a=[...document.querySelectorAll('main aside[aria-label]')].find(e=>e.getClientRects().length); return a?a.getAttribute('aria-label'):'';})()"); shot('mapa_painel_talhao')
        chk('16 mapa · painel do talhão aberto com no máximo uma primária na tela (próximo passo no painel, sem cópia no cabeçalho)', bool(pn) and len(mp['prims'])<=1, [pn,mp['prims']])
        ERRL.extend(errs()); info('erros de JS (famílias)',ERRL[:5])
    elif MODO=='responsivo':
        MAT=[('360x800',360,800,3,True),('800x360',800,360,3,True),('768x1024',768,1024,2,True),('1024x768',1024,768,2,True),
             ('1280x720',1280,720,1,False),('1440x900',1440,900,1,False),('zoom200',720,450,2,False)]
        # medida da área de ações: alcançável (rolando), não cobre a última linha do conteúdo, o foco levado à vista não fica sob ela,
        # a página não rola de lado, um avanço só; o aviso temporário não fica sobre a área presa nem, no fim da rolagem, sobre um
        # controle dela (V55-RESP-01). A medida espera dois quadros pintados (rAF, até 6 s): o g2lib põe a altura da área presa
        # (--acoes-h, que sobe o aviso) num rAF, e com a máquina carregada o Chrome headless pinta um quadro a cada ~2 s; sem a espera
        # a medida lia o estado entre a mutação e o quadro, que a pessoa nunca vê pintado (aviso sobre a área a 1440×900, V55-RESP-01)
        AREA=r"""(async()=>{ await new Promise(ok=>{ let k=0; const f=()=>{ if(++k>2) ok(); else requestAnimationFrame(f); }; f(); setTimeout(ok,6000); });
          const vis=e=>{const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&getComputedStyle(e).display!=='none';};
          const a=document.querySelector('[data-acoes]'); if(!a||!vis(a)) return {semArea:true};
          const col=document.querySelector('.ml-tog+div'); const m=document.querySelector('main[data-scroll]'); const R=(col&&col.scrollHeight>col.clientHeight+1&&getComputedStyle(col).overflowY==='auto')?col:m;
          const out={pos:getComputedStyle(a).position, lado:document.documentElement.scrollWidth>innerWidth+1};
          const b=a.querySelector('[data-acao=avancar],[data-acao=comando],[data-acao=abrir],[data-acao=resolver]')||a.querySelector('button,a');
          b.scrollIntoView({block:'center'}); const rb=b.getBoundingClientRect(); const h=document.elementFromPoint(Math.min(rb.left+rb.width/2,innerWidth-2),rb.top+rb.height/2);
          out.cmd=b.innerText.trim(); out.alcanca=!!h&&(b===h||b.contains(h))&&rb.bottom<=innerHeight+1&&rb.top>=0;
          R.scrollTop=R.scrollHeight; const blocos=[...m.children].filter(x=>vis(x)&&!x.contains(a)&&!x.matches('.acoes')); const ult=blocos[blocos.length-1];
          const ra=a.getBoundingClientRect(); const ru=ult?ult.getBoundingClientRect():null; out.cobreUltima=!!ru&&ru.bottom>ra.top+1&&ru.bottom<=innerHeight;
          const av=[...document.querySelectorAll('[role=status]')].find(x=>vis(x)&&getComputedStyle(x).position==='fixed'); out.aviso=av?av.innerText.trim().slice(0,40):'';
          out.avisoSobreCmd=av?[...a.querySelectorAll('button,a')].filter(vis).filter(x=>{ const r=x.getBoundingClientRect(); const y=r.top+r.height/2; if(y<0||y>innerHeight-1) return false; const hx=document.elementFromPoint(Math.min(r.left+r.width/2,innerWidth-2),y); return !!hx&&av.contains(hx); }).map(x=>x.innerText.trim().slice(0,30)):[];
          const foc=[...m.querySelectorAll('button,a[href],input,select,[tabindex="0"]')].filter(x=>vis(x)&&!a.contains(x)&&!x.closest('[role=dialog]'));
          const f=foc[Math.max(0,foc.length-2)]; R.scrollTop=0; if(f){ f.focus(); const rf=f.getBoundingClientRect(); const hf=document.elementFromPoint(Math.min(Math.max(rf.left+4,1),innerWidth-2),Math.min(rf.top+rf.height/2,innerHeight-1)); out.focoCoberto=!(hf&&(f===hf||f.contains(hf)||hf.contains(f))); out.foco=(f.innerText||f.getAttribute('aria-label')||f.tagName).trim().slice(0,30); }
          const at=document.querySelector('.etp-atual'); out.etapa=at&&vis(at)?at.innerText.replace(/\s+/g,' ').trim():''; out.avancos=a.querySelectorAll('[data-acao=avancar]').length;
          const t=document.querySelector('[role=status]'); const rt=t?t.getBoundingClientRect():null; out.toastSobre=!!(rt&&rt.height>2&&out.pos==='sticky'&&rt.bottom>a.getBoundingClientRect().top+1&&rt.top<a.getBoundingClientRect().bottom); return out;})()"""
        # progresso realmente renderizado (medido na carga, casca no topo). A faixa decide o modo por container query (ui37 _ETP_LIM: SAF,
        # 4 etapas, compacta abaixo de 640 px de faixa; CMP, 6 etapas, abaixo de 900 px), não pela largura da janela:
        #   compacta → "Etapa i de n · Nome" visível e livre;
        #   lista    → as n etapas visíveis, inteiras (sem texto cortado), dentro da faixa e da janela, sem sobreposição, e a atual
        #              (aria-current=step, começa por "i ") visível e livre (elementFromPoint).
        # Nos dois modos, o contexto (chip "Safra 2026/27…" do cabeçalho) visível e livre.
        PROG=r"""((n,i)=>{ const N=s=>(s||'').replace(/\s+/g,' ').trim();
          const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.display!=='none'&&cs.visibility!=='hidden'; };
          const R=e=>{ const r=e.getBoundingClientRect(); return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]; };
          const livre=e=>{ const r=e.getBoundingClientRect(); const x=Math.min(Math.max(r.left+r.width/2,1),innerWidth-2), y=r.top+r.height/2; if(y<0||y>innerHeight-1) return false; const h=document.elementFromPoint(x,y); return !!h&&(h===e||e.contains(h)); };
          const nav=document.querySelector('.etp-ind'); if(!nav) return {ok:false,semFaixa:true};
          const rn=nav.getBoundingClientRect(); const at=nav.querySelector('.etp-atual'); const comp=vis(at); const ol=nav.querySelector('ol.etp-itens');
          const out={modo:comp?'compacta':'lista', faixa:R(nav), classe:nav.className};
          if(comp){ out.texto=N(at.innerText); out.ok=out.texto.startsWith('Etapa '+i+' de '+n+' · ')&&livre(at); }
          else { const its=ol?[...ol.children].filter(vis):[]; const cur=ol&&ol.querySelector('[aria-current=step]'); let sob=0;
            for(let x=0;x<its.length;x++) for(let y=x+1;y<its.length;y++){ const a=its[x].getBoundingClientRect(), b=its[y].getBoundingClientRect(); if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1) sob++; }
            const fora=its.filter(x=>{ const r=x.getBoundingClientRect(); return r.left<Math.max(rn.left,0)-1||r.right>Math.min(rn.right,innerWidth)+1||r.top<-1||r.bottom>innerHeight+1; }).map(x=>N(x.innerText).slice(0,20));
            const corte=its.filter(x=>[x,...x.querySelectorAll('*')].some(y=>vis(y)&&!y.classList.contains('etp-sr')&&(y.scrollWidth>y.clientWidth+1&&getComputedStyle(y).overflowX!=='visible'))).map(x=>N(x.innerText).slice(0,20));
            out.itens=its.length; out.atual=cur?N(cur.innerText).slice(0,60):''; out.atualRet=cur?R(cur):null; out.atualLivre=!!cur&&livre(cur); out.sob=sob; out.fora=fora; out.corte=corte;
            out.ok=its.length===n&&out.atual.startsWith(i+' ')&&out.atualLivre&&sob===0&&!fora.length&&!corte.length; }
          const ch=[...document.querySelectorAll('header *')].find(e=>e.children.length===0&&/^Safra 2026\/27/.test(N(e.innerText))); out.contexto=ch?N(ch.innerText):''; out.contextoOk=!!ch&&vis(ch)&&livre(ch);
          return out; })"""
        res={}; ruins={}; prog={}
        for tag,w,h,e,t in MAT:
            for pg,hs,alvo,n in (('SAF','#saf=S2627&passo=demanda',4,4),('CMP','#saf=S2627',3,6)):   # passo=demanda = etapa 4 de 4 (o etapa=N antigo é lido na numeração de 6)
                abre(pg,w,h,e,t,hash=hs,espera=.6,limpa=(tag=='360x800'));
                if pg=='CMP': etapa(alvo)
                time.sleep(.2); pr=J(f"({PROG})({n},{alvo})"); prog[f'{pg} {tag}']=pr
                if tag in ('800x360','768x1024'): shot(f'{pg.lower()}_{tag}_progresso')
                m=J(AREA); m['progresso']=pr; res[f'{pg} {tag}']=m
                ruim=m.get('semArea') or not m['alcanca'] or m['cobreUltima'] or m['focoCoberto'] or m['lado'] or m['avancos']>1 or m['toastSobre'] or m['avisoSobreCmd'] or not pr.get('ok') or not pr.get('contextoOk')
                if ruim: ruins[f'{pg} {tag}']=m
                if tag in ('360x800','800x360','zoom200'): shot(f'{pg.lower()}_{tag}')
        info('área de ações por dimensão',{k:(v.get('pos'),v.get('cmd'),v.get('etapa','')[:22],v.get('aviso','')[:20]) for k,v in res.items()})
        info('progresso por dimensão',{k:(v.get('modo'),v.get('texto') or v.get('atual','')[:30],v.get('faixa',[0,0,0])[2],v.get('contexto')) for k,v in prog.items()})
        chk('17 matriz RESPONSIVIDADE (7 dimensões × SAF etapa 4 de 4 e CMP etapa 3 de 6) · área de ações alcançável, não cobre a última linha nem o foco; o aviso não fica sobre a área presa nem sobre um controle dela no fim da rolagem; sem rolagem lateral, um avanço; progresso renderizado: faixa compacta "Etapa i de n · Nome" ou a lista completa inteira com a atual visível, e o contexto (safra) visível', not ruins, ruins)
        # 18 · teclado virtual aberto (360×800 → 360×420, janela redimensionada pelo teclado): campo focado e comando alcançáveis
        abre('SAF',360,800,3,True,hash='#saf=S2627&etapa=2'); J("(()=>{const i=document.querySelector('main input[type=search]'); i.scrollIntoView({block:'center'}); i.focus();})()")
        c.aparelho(360,420,3,True); time.sleep(.5)
        kv=J(r"""(()=>{const i=document.activeElement; const r=i.getBoundingClientRect(); const h=document.elementFromPoint(Math.min(r.left+10,innerWidth-2),Math.min(r.top+r.height/2,innerHeight-1));
          const a=document.querySelector('[data-acoes]'); const b=a.querySelector('[data-acao=avancar],[data-acao=resolver]'); const vis=r.top>=0&&r.bottom<=innerHeight;
          b.scrollIntoView({block:'center'}); const rb=b.getBoundingClientRect(); const hb=document.elementFromPoint(rb.left+rb.width/2,rb.top+rb.height/2);
          const av=[...document.querySelectorAll('[role=status]')].find(x=>x.getClientRects().length&&x.getBoundingClientRect().height>2&&getComputedStyle(x).position==='fixed');
          return {campo:i.type, campoVisivel:vis, campoLivre:!!h&&(h===i||i.contains(h)||h.closest('label')===i.closest('label')), pos:getComputedStyle(a).position, cmd:b.innerText.trim(), cmdAlcanca:!!hb&&(hb===b||b.contains(hb)),
            cmdRet:[Math.round(rb.top),Math.round(rb.bottom)], noCentro:hb?(hb.getAttribute('role')||hb.tagName):'', aviso:av?[av.innerText.trim().slice(0,40),Math.round(av.getBoundingClientRect().top),Math.round(av.getBoundingClientRect().bottom)]:null};})()""")
        shot('saf_360x420_teclado')
        chk('18 teclado virtual aberto (360×420) · a busca focada continua visível e livre; a área de ações volta ao fluxo (static) e o comando é alcançável rolando', kv['campoVisivel'] and kv['campoLivre'] and kv['pos']=='static' and kv['cmdAlcanca'], kv)
        # 18b/18c · V55-RESP-01 (proteção de regressão): com o aviso temporário REAL na tela (fixo no pé), a área em fluxo não fica sob ele:
        #       no fim da rolagem nenhum controle da área está sob o aviso (elementFromPoint no centro de cada um) e o toque real
        #       (Input.dispatchTouchEvent) no centro de "Dimensionar operações ›", depois de rolar e com o aviso ainda na tela, avança à
        #       etapa 3. 18b: "Safra aberta…" (ao abrir). 18c: o aviso mais longo da etapa 2 ("Aplicar plano em 4 cultivos" com a P2 em
        #       sobreposição, ~340 caracteres) com env(safe-area-inset-bottom) = 34 px: a folga vem da faixa medida do aviso (--aviso-h),
        #       não de uma altura estimada. Antes da correção o centro caía no aviso e o toque se perdia.
        FIM18=r"""(()=>{const col=document.querySelector('.ml-tog+div'); col.scrollTop=col.scrollHeight; const a=document.querySelector('[data-acoes]');
          const av=[...document.querySelectorAll('[role=status]')].find(x=>x.getClientRects().length&&x.getBoundingClientRect().height>2&&getComputedStyle(x).position==='fixed');
          const cs=[...a.querySelectorAll('button,a')].filter(x=>x.getClientRects().length).map(x=>{ const r=x.getBoundingClientRect(); const h=document.elementFromPoint(r.left+r.width/2,Math.min(r.top+r.height/2,innerHeight-1)); return [x.innerText.trim().slice(0,30),Math.round(r.top),Math.round(r.bottom),!!h&&(h===x||x.contains(h)),!!h&&!!h.closest('[role=status]')]; });
          const alc=[...a.querySelectorAll('button,a')].filter(x=>x.getClientRects().length).map(x=>{ x.scrollIntoView({block:'nearest'}); const r=x.getBoundingClientRect(); const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return !!h&&(h===x||x.contains(h)); });
          const b=a.querySelector('[data-acao=avancar]'); b.scrollIntoView({block:'center'}); const rb=b.getBoundingClientRect(); const hb=document.elementFromPoint(rb.left+rb.width/2,rb.top+rb.height/2);
          const av2=[...document.querySelectorAll('[role=status]')].find(x=>x.getClientRects().length&&x.getBoundingClientRect().height>2&&getComputedStyle(x).position==='fixed');
          return {aviso:av?[av.innerText.trim().length,Math.round(av.getBoundingClientRect().top),Math.round(av.getBoundingClientRect().bottom)]:null, avisoH:getComputedStyle(document.documentElement).getPropertyValue('--aviso-h'),
            controles:cs, alcancaveis:alc, ponto:[rb.left+rb.width/2,rb.top+rb.height/2], noPonto:!!hb&&(hb===b||b.contains(hb)), avisoNoToque:!!av2};})()"""
        for cid,av,sf in (('18b','carga',0),('18c','longo',34)):
            abre('SAF',360,800,3,True,hash='#saf=S2627&etapa=2'); c.call('Emulation.setSafeAreaInsetsOverride',{'insets':{'bottom':sf,'bottomMax':sf}})
            J("(()=>{const i=document.querySelector('main input[type=search]'); i.scrollIntoView({block:'center'}); i.focus();})()")
            c.aparelho(360,420,3,True); time.sleep(.3); prep=''
            if av=='longo':
                prep=[acao('resolver',.6), J("(()=>{const d=document.querySelector('aside[role=dialog]'); const b=d&&[...d.querySelectorAll('button')].filter(b=>b.getClientRects().length).find(b=>b.innerText.trim().startsWith('Aplicar plano')); if(!b) return 'sem Aplicar'; b.click(); return b.innerText.trim();})()")]; time.sleep(.5)
            fim=J(FIM18); e0=est()['etapa']; c.toque(*fim['ponto']); time.sleep(.6); e1=est()['etapa']; shot(f'saf_360x420_toque_avanco_{av}')
            c.call('Emulation.setSafeAreaInsetsOverride',{'insets':{'bottom':0,'bottomMax':0}})
            # 18b: aviso curto, toda a área livre no fim da rolagem. 18c: o aviso longo + safe-area deixam acima dele menos altura que a área
            # (e a faixa de etapas presa no topo): no fim da rolagem nenhum controle fica sob o AVISO, e cada um, levado à vista (como o foco por
            # Tab), fica livre
            livres=all(x[3] for x in fim['controles']) if av=='carga' else all(fim['alcancaveis'])
            chk(f'{cid} aviso temporário real na tela (360×420, teclado aberto, aviso {av}, safe-area {sf} px) · no fim da rolagem nenhum controle da área fica sob o aviso'+(' (todos livres)' if av=='carga' else '; cada controle levado à vista fica livre')+'; o toque real em "Dimensionar operações ›" depois de rolar, com o aviso ainda na tela, leva da etapa 2 à 3',
                bool(fim['aviso']) and (av!='longo' or fim['aviso'][0]>300) and fim['controles'] and not any(x[4] for x in fim['controles']) and livres and all(fim['alcancaveis']) and fim['noPonto'] and fim['avisoNoToque'] and e0==2 and e1==3, [prep,fim,e0,e1])
        # 19 · inserção repetitiva com o teclado aberto (contraprova Gemini): 16ª parcela no "Dividir" do T4; uma instância de "+ Adicionar parcela",
        #      foco no nome da parcela nova, à vista e fora do rodapé do painel; contexto (talhão) mantido
        # no celular o "Dividir" sai da linha (print do proprietário, 14/10): o toque na linha do T4 abre o painel com "Dividir T4 em parcelas"
        abre('SAF',360,420,3,True,hash='#saf=S2627&etapa=2'); r=J("(()=>{const rw=[...document.querySelectorAll('main [role=row].g2ed')].find(x=>{const c=x.querySelector('.g2c0'); return c&&c.innerText.trim().split(/\\s+/)[0]==='T4';}); const z=rw&&[...rw.querySelectorAll('[role=cell]')].find(q=>!q.querySelector('button,input')&&q.innerText.trim()&&!q.classList.contains('g2c0')); if(!z) return 'sem T4'; z.click(); return 'ok';})()"); time.sleep(.6)
        r=J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Dividir T4 em parcelas'); if(!b) return 'sem Dividir'; b.click(); return 'ok';})()") if r=='ok' else r; time.sleep(.6)
        tit=J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText.trim()"); ruins=[]
        n0=J("document.querySelectorAll('aside[role=dialog] input[aria-label^=\"Nome da parcela\"]').length")
        for k in range(max(0,16-n0)):
            J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='+ Adicionar parcela'); b.scrollIntoView({block:'nearest'}); b.click();})()"); time.sleep(.25)
            st=J(r"""(()=>{const d=document.querySelector('aside[role=dialog]'); const ins=[...d.querySelectorAll('input[aria-label^="Nome da parcela"]')]; const a=document.activeElement; const r=a.getBoundingClientRect(); const rd=d.getBoundingClientRect();
              const h=document.elementFromPoint(Math.min(Math.max(r.left+6,rd.left+2),innerWidth-2),r.top+r.height/2);
              return {n:ins.length, foco:a===ins[ins.length-1], visivel:r.top>=rd.top-1&&r.bottom<=Math.min(rd.bottom,innerHeight)+1, livre:!!h&&(h===a||a.contains(h)), add:[...d.querySelectorAll('button')].filter(b=>b.innerText.trim()==='+ Adicionar parcela').length};})()""")
            if not (st['foco'] and st['visivel'] and st['livre'] and st['add']==1): ruins.append(st)
        fim=J(r"""(()=>{const d=document.querySelector('aside[role=dialog]'); return [d.querySelectorAll('input[aria-label^="Nome da parcela"]').length, (d.querySelector('h2')||{innerText:''}).innerText.trim()];})()"""); shot('saf_16a_parcela_teclado')
        chk('19 16ª parcela com o teclado aberto (360×420) · a cada "+ Adicionar parcela" o foco vai ao nome da nova, à vista e sem nada por cima; uma só instância do botão; o painel continua no mesmo talhão',
            r=='ok' and fim[0]>=16 and not ruins and fim[1]==tit, [r,tit,n0,fim,ruins[:3]])
        ERRL.extend(errs()); info('erros de JS (responsivo)',ERRL[:5])
    elif MODO=='gemini':
        # 20 · (a) app: a faixa inferior nomeia a ordem; reordenar a fila (outro quadro muda o cenário) atualiza o rótulo e o toque age
        #      na ordem escrita no rótulo, nunca na anterior em silêncio
        abre('OS-0424-app',390,844,3,True); J("(()=>{ if(window.__cen) localStorage.setItem('talhao-os-cenario-v1', JSON.stringify(window.__cen.cenGet())); })()")   # cenário gravado, como depois de qualquer ação
        abre('MB-01',390,844,3,True,limpa=False); time.sleep(.4)
        L=r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const bs=[...document.querySelectorAll('[data-mroot] button,[data-mroot] a')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); const b=bs[bs.length-1]; return b?n(b.innerText):'';})()"""
        l1=J(L); id1=(l1.split('· ')[-1] if '· ' in l1 else '')
        mud=J(f"""(()=>{{const k='talhao-os-cenario-v1'; let c=JSON.parse(localStorage.getItem(k)||'null'); if(!c) return 'sem cenário'; const o=c.ordens&&c.ordens[{json.dumps(id1)}]; if(!o) return 'sem ordem '+{json.dumps(id1)}; o.etapa='A liberar'; const t=JSON.stringify(c); localStorage.setItem(k,t); window.dispatchEvent(new StorageEvent('storage',{{key:k,newValue:t}})); return 'ok';}})()""")
        time.sleep(.6); l2=J(L); id2=(l2.split('· ')[-1] if '· ' in l2 else ''); shot('app_faixa_reordenada')
        J("(()=>{const bs=[...document.querySelectorAll('[data-mroot] button,[data-mroot] a')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); const b=bs[bs.length-1]; if(b) b.click();})()"); time.sleep(1.2)
        # o toque age na ordem do rótulo: inicia o turno dela ou abre a tela do passo dela (link), nunca a ordem anterior
        dep=J(f"""(()=>{{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null'); const t=c&&c.app&&c.app.turno; const b=document.body.innerText;
          return [t&&!t.fim?t.os:'', c&&c.ordens&&c.ordens[{json.dumps(id1)}]?c.ordens[{json.dumps(id1)}].etapa:'', location.pathname.split('/').pop()+location.hash, b.indexOf({json.dumps(id2)})>=0];}})()""")
        chk('20 (a) app · a faixa inferior nomeia a ordem do comando ("verbo · OS-…"); a fila reordenada por outro quadro troca o rótulo antes do toque, e o toque age na ordem escrita (não na anterior)',
            bool(id1) and mud=='ok' and bool(id2) and id2!=id1 and dep[0]!=id1 and dep[1]=='A liberar' and (dep[0]==id2 or ('MB-01' not in dep[2] and dep[3])), [l1,mud,l2,dep])
        info('faixa do app antes/depois da reordenação e turno aberto',[l1,l2,dep])
        # 21 · (b) lote com IDs ocultos e prévia: seleciona T1-A (parcela do T1) e P1; recolhe o T1 e filtra até sumir P1; a barra diz quantos
        #      estão fora da vista; recolher/expandir não muda o conjunto; "Aplicar plano" mostra a prévia com os 2 incluídos
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3)
        for lab in ('Selecionar T1-A','Selecionar P1'): J(f"(()=>{{const i=document.querySelector('main input[type=checkbox][aria-label={json.dumps(lab)}]'); if(i) i.click();}})()"); time.sleep(.25)
        s1=J("(()=>{const s=[...document.querySelectorAll('main [role=status]')].find(e=>e.getClientRects().length&&/selecionad/.test(e.innerText)); return s?s.innerText.trim():'';})()")
        J("(()=>{const b=[...document.querySelectorAll('main .g2car')].find(b=>/T1/.test(b.getAttribute('aria-label')||'')&&b.getAttribute('aria-expanded')==='true'); if(b) b.click();})()"); time.sleep(.3)
        setv('main input[type=search]','T'); time.sleep(.3); setv('main input[type=search]','T1'); time.sleep(.4)
        s2=J("(()=>{const s=[...document.querySelectorAll('main [role=status]')].find(e=>e.getClientRects().length&&/selecionad/.test(e.innerText)); return s?s.innerText.trim():'';})()"); shot('saf_lote_ocultos')
        J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Aplicar plano'); if(b) b.click();})()"); time.sleep(.5)
        pv=J("(()=>{const d=document.querySelector('aside[role=dialog]'); return d?[d.getAttribute('aria-label'), d.innerText.indexOf('T1-A')>=0, d.innerText.indexOf('P1 ')>=0||d.innerText.indexOf('P1 ·')>=0]:null;})()"); shot('saf_lote_previa')
        chk('21 (b) lote por IDs · 2 selecionados (T1-A e P1); com o T1 recolhido e a busca "T1" a barra diz "2 selecionados · 1 fora da vista…" (recolher não mudou o conjunto); "Aplicar plano" abre a prévia com os 2 incluídos, inclusive o oculto',
            s1.startswith('2 selecionados') and s2.startswith('2 selecionados') and 'fora da vista' in s2 and pv and pv[0].startswith('Aplicar plano a 2 cultivos') and pv[1] and pv[2], [s1,s2,pv])
        # 22 · (c) corrigir pelo teclado e voltar direto à revisão: Tab até "Corrigir cultivos", Enter; Tab até "Voltar à revisão ›", Enter
        abre('SAF',hash='#saf=S2627&etapa=6'); time.sleep(.4); J("document.activeElement&&document.activeElement.blur()"); k=0
        while k<120 and J("(document.activeElement&&document.activeElement.dataset.acao)||''")!='corrigir': c.tab(); k+=1
        c.tecla('Enter','Enter',13,text='\r'); time.sleep(.7); e2=est(); k2=0
        while k2<120 and J("(document.activeElement&&document.activeElement.innerText||'').trim()")!='Voltar à revisão ›': c.tab(); k2+=1
        c.tecla('Enter','Enter',13,text='\r'); time.sleep(.8); e6=est(); shot('saf_corrigir_teclado')
        chk('22 (c) teclado · Tab chega a "Corrigir cultivos" na nota da revisão; Enter leva à etapa 2 (correção); Tab chega a "Voltar à revisão ›"; Enter volta direto à etapa 4 (sem percorrer a etapa 3)',
            k<120 and e2['etapa']==2 and any('Correção pedida pela revisão' in a for a in e2['area']) and k2<120 and e6['etapa']==4, [k,e2['area'],k2,e6['etapa']])
        ERRL.extend(errs()); info('erros de JS (gemini)',ERRL[:5])
    elif MODO=='v3':
        import re as _re
        DUPF=os.environ.get('DUP_PY') or os.path.normpath(os.path.join(HERE,'..','ferramentas','acoes_duplicadas.py'))   # o verificador versionado
        DUPJS=_re.search(r'JS=r"""(.*?)"""',open(DUPF,encoding='utf-8').read(),_re.S).group(1)   # mesma medida da varredura, sem cópia
        # primárias visíveis: no painel modal aberto conta só o painel (o véu deixa o fundo inerte; v3.1); senão cabeçalho + conteúdo
        PRIM=r"""(()=>{const vis=e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none';};
          const n=s=>(s||'').replace(/\s+/g,' ').trim(); const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
          const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>vis(x)&&x.parentElement&&getComputedStyle(x.parentElement).position==='fixed');
          const raiz=d?[d]:[...document.querySelectorAll('header,main')];
          const ps=raiz.flatMap(r=>[...r.querySelectorAll('button,a')]).filter(e=>vis(e)&&verde(e)&&!e.closest('.menu-lat')).map(e=>n(e.innerText).slice(0,48));
          return {prims:ps, dialogo:!!d, setas:document.querySelectorAll('[aria-label^="Etapa anterior"],[aria-label^="Próxima etapa"]').length};})()"""
        def medida(nome):
            dd=J(DUPJS); pp=J(PRIM); n=len(dd.get('mesmoRotulo',[]))+len(dd.get('mesmoDestino',[]))
            return {'estado':nome,'dup':n,'dupdet':[x['rot'] for x in dd.get('mesmoRotulo',[])]+[x['destino'] for x in dd.get('mesmoDestino',[])],'prims':pp['prims'],'dialogo':pp['dialogo'],'setas':pp['setas']}
        SELMSG="(()=>{const s=[...document.querySelectorAll('main [role=status]')].find(e=>e.getClientRects().length&&/selecionad/.test(e.innerText)); return s?s.innerText.trim():'';})()"
        def marca(lab): return J(f"(()=>{{const i=document.querySelector('main input[type=checkbox][aria-label={json.dumps(lab)}]'); if(!i) return 'sem '+{json.dumps(lab)}; i.click(); return 'ok';}})()")
        M=[]
        # 23 · seleção ativa (SAF etapa 2): o lote "Aplicar plano" é a primária da tarefa; a área mantém nota + avanço secundário, sem 2ª
        #      primária de aplicar; busca e filtros continuam na barra (só a região de ações da coleção muda)
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3); marca('Selecionar T1-A'); time.sleep(.35)
        m=medida('SAF etapa 2 · seleção ativa'); M.append(m); e=est()
        barra=J("(()=>{const s=document.querySelector('main input[type=search]'); return [!!s&&s.getClientRects().length>0, [...document.querySelectorAll('main button')].filter(b=>b.getClientRects().length&&b.innerText.trim()==='Limpar seleção').length];})()"); shot('v3_selecao_ativa')
        chk('23 seleção ativa (SAF etapa 2, T1-A): 0 duplicatas, uma primária ("Aplicar plano" do lote, na barra da lista); a área fica com a nota e o avanço secundário, sem outra primária de aplicar; busca visível e "Limpar seleção" uma vez',
            m['dup']==0 and m['prims']==['Aplicar plano'] and e['avancos']==1 and not any(a.startswith('resolver:') for a in e['area']) and barra==[True,1], [m,e['area'],barra])
        # 24 · painel modal aberto (Aplicar plano): uma primária no painel; Tab circula só dentro dele; fechar devolve o foco a quem abriu
        J("document.querySelector('main input[type=checkbox][aria-label=\"Selecionar T1-A\"]').click()"); time.sleep(.3)
        J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=resolver]'); b.focus(); b.click();})()"); time.sleep(.6)
        m=medida('SAF etapa 2 · painel Aplicar plano'); M.append(m); dentro=[]
        for _ in range(30):
            c.tab(); dentro.append(J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))"))
        for _ in range(3):
            c.tab(shift=True); dentro.append(J("!!(document.activeElement&&document.activeElement.closest('aside[role=dialog]'))"))
        modal=J("(document.querySelector('aside[role=dialog]')||{getAttribute:()=>''}).getAttribute('aria-modal')"); shot('v3_painel_modal')
        J("(()=>{const b=document.querySelector('aside[role=dialog] [aria-label=Fechar]')||[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b.click();})()"); time.sleep(.5)
        volta=J("(()=>{const a=document.activeElement; return a?(a.dataset.acao||a.tagName):'';})()")
        chk('24 painel modal aberto (Aplicar plano): 0 duplicatas e uma primária no painel; aria-modal; 33 Tabs/Shift+Tab nunca saem do painel; ao fechar o foco volta a "Aplicar plano…" da área',
            m['dialogo'] and len(m['prims'])==1 and m['dup']==0 and modal=='true' and all(dentro) and volta=='resolver', [m,modal,dentro.count(False),volta])
        # 25 · decisão de saída (PA, Incluir atividade com texto digitado): "Continuar editando" é a única primária; Salvar some enquanto
        #      a decisão está aberta e volta ao continuar editando; o texto digitado continua lá
        abre('PA'); J("document.querySelector('main .g2card').click()"); time.sleep(.5); clk('Incluir atividade')
        campo=J("(()=>{const d=document.querySelector('aside[role=dialog]'); const i=d&&[...d.querySelectorAll('input:not([type=checkbox]),textarea')].find(x=>x.getClientRects().length&&!x.readOnly); if(!i) return null; if(!i.id) i.id='v3campo'; return i.id;})()")
        setv('#'+campo,'Teste saída') if campo else None; time.sleep(.2)
        J("(()=>{const b=document.querySelector('aside[role=dialog] [aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.4)
        m=medida('PA · decisão de saída aberta'); M.append(m); sal=J("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.getClientRects().length&&/^(Salvar|Incluir atividade|Cancelar)$/.test(b.innerText.trim())).length"); shot('v3_decisao_saida')
        clk('Continuar editando','aside[role=dialog]'); sal2=J("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.getClientRects().length&&/^(Salvar|Incluir atividade|Cancelar)$/.test(b.innerText.trim())).length")
        val=J(f"(document.getElementById({json.dumps(campo)})||{{value:''}}).value") if campo else ''
        chk('25 decisão de saída (PA · Incluir atividade): "Continuar editando" a única primária, "Descartar alterações" separado e o rodapé (Cancelar · Incluir atividade) fora enquanto a decisão está aberta; continuar editando devolve o rodapé e o texto',
            m['prims']==['Continuar editando'] and sal==0 and sal2==2 and val=='Teste saída', [campo,m,sal,sal2,val])
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); time.sleep(.3); clk('Descartar alterações','aside[role=dialog]')
        # 26 · impedimento e consulta: PA detalhe sem rascunho (nada a publicar; NAV-1 tirou a etapa 3) e SAF encerrada (S2526) na revisão: zero primária
        m1=medida('PA detalhe sem rascunho · nada a publicar'); M.append(m1)
        abre('SAF',hash='#saf=S2526&etapa=6'); time.sleep(.4); m2=medida('SAF S2526 etapa 6 · consulta'); M.append(m2); shot('v3_consulta')
        chk('26 impedimento (PA detalhe sem rascunho) e consulta (SAF S2526 encerrada, etapa 6): 0 primária e 0 duplicata',
            m1['prims']==[] and m1['dup']==0 and m2['prims']==[] and m2['dup']==0, [m1,m2])
        # 27 · celular, tablet e zoom de 200 %: SAF etapa 2 e 6, CMP etapa 2, PA, O.S.: 0 duplicata, no máximo uma primária, sem setas
        ruins=[]
        for tag,w,h,es,t in (('360x800',360,800,3,True),('768x1024',768,1024,2,True),('zoom200',720,450,2,False)):
            for pg,hs in (('SAF','#saf=S2627&etapa=2'),('SAF','#saf=S2627&etapa=6'),('CMP','#saf=S2627'),('PA',''),('PA','#plano=SOJA-AT'),('OS','')):
                abre(pg,w,h,es,t,hash=hs,espera=.6,limpa=False); time.sleep(.2); m=medida(f'{pg}{hs} @{tag}'); M.append(m)
                if m['dup'] or len(m['prims'])>1 or m['setas']: ruins.append(m)
        shot('v3_os_zoom200')
        chk('27 360×800, 768×1024 e zoom 200 % (SAF etapas 2 e 6, CMP etapa 2, PA lista e detalhe, O.S.): 0 duplicata, no máximo uma primária e nenhuma seta', not ruins, ruins)
        # 28 · v3.1: selecionar → buscar outro registro → somar à seleção → abrir o detalhe e voltar: seleção, busca e contexto preservados;
        #      a seleção não desmontou o campo de busca nem trocou a barra inteira
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3); marca('Selecionar T1-A'); time.sleep(.3)
        J("document.querySelector('main input[type=search]').focus()"); setv('main input[type=search]','P1'); time.sleep(.4)
        foco=J("(document.activeElement&&document.activeElement.type)||''"); marca('Selecionar P1'); time.sleep(.35); s1=J(SELMSG)
        J("(()=>{const r=[...document.querySelectorAll('main [role=row].g2ed')].find(x=>x.getClientRects().length&&/\\bP1\\b/.test(x.innerText)); (r.querySelector('[role=cell] b')||r).click();})()"); time.sleep(.5)
        dl=J("(document.querySelector('aside[role=dialog]')||{getAttribute:()=>''}).getAttribute('aria-label')")
        J("(()=>{const b=document.querySelector('aside[role=dialog] [aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.5)
        s2=J(SELMSG); q=J("(document.querySelector('main input[type=search]')||{value:''}).value"); e=est(); shot('v3_selecao_detalhe_volta')
        chk('28 v3.1 · T1-A selecionado → busca "P1" (campo segue focado) → soma P1 → abre o detalhe de P1 e fecha: "2 selecionados · 1 fora da vista…" antes e depois, busca "P1" mantida, etapa 2',
            foco=='search' and s1.startswith('2 selecionados') and 'fora da vista' in s1 and bool(dl) and s2==s1 and q=='P1' and e['etapa']==2, [foco,s1,dl,s2,q,e['etapa']])
        # 29 · tipo por função: expandir/recolher global é texto discreto (sem fundo, sem borda); filtro rápido escolhido e visão atual
        #      são estados de escolha (tonal), nunca o verde cheio da primária
        abre('SAF',hash='#saf=S2627&etapa=2'); time.sleep(.3)
        xt=J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.getClientRects().length&&/^(Expandir|Recolher) tudo$/.test(b.innerText.trim())); if(!b) return null; const cs=getComputedStyle(b); return [b.innerText.trim(), cs.backgroundColor, cs.borderTopWidth];})()")
        qf=J("(()=>{const b=[...document.querySelectorAll('main [aria-pressed=true]')].find(b=>b.getClientRects().length); return b?[b.innerText.replace(/\\s+/g,' ').trim(), getComputedStyle(b).backgroundColor]:null;})()")
        abre('OS',limpa=False); vs=J("(()=>{const b=[...document.querySelectorAll('main [aria-label=\"Visão das ordens\"] [aria-pressed=true]')].find(b=>b.getClientRects().length); return b?[b.innerText.trim()||b.getAttribute('aria-label'), getComputedStyle(b).backgroundColor]:null;})()")
        och=J("(()=>{const b=[...document.querySelectorAll('main [aria-label=\"Filtrar por fase\"] [aria-pressed=true]')].find(b=>b.getClientRects().length); return b?[b.innerText.replace(/\\s+/g,' ').trim(), getComputedStyle(b).backgroundColor]:null;})()")
        G='rgb(30, 122, 76)'
        chk('29 tipo por função: "Expandir/Recolher tudo" sem fundo e sem borda; filtro rápido escolhido (SAF), visão atual (O.S. Lista) e chip de fase escolhido sem o verde cheio da primária',
            xt and xt[1]=='rgba(0, 0, 0, 0)' and xt[2]=='0px' and qf and qf[1]!=G and vs and vs[1]!=G and (och is None or och[1]!=G), [xt,qf,vs,och])
        # 29b · a verificação reprova o que deve reprovar (controle negativo, v3 item 5): na SAF etapa 3, posição dos comandos guiados
        #       (avançar/voltar só dentro da área de ações; nada focável no indicador) e, numa cópia injetada da primária no cabeçalho, a
        #       medida acusa a duplicata, a 2ª primária e o avanço fora da posição. A injeção é removida antes de seguir.
        POS=r"""(()=>{const fora=[...document.querySelectorAll('[data-acao=avancar],[data-acao=voltar]')].filter(e=>e.getClientRects().length&&!e.closest('[data-acoes]')).length;
          const foc=[...document.querySelectorAll('.etp-ind a,.etp-ind button,.etp-ind [tabindex]')].length; return {fora,foc};})()"""
        abre('SAF',hash='#saf=S2627&etapa=3'); time.sleep(.3); limpo=dict(medida('SAF etapa 3'),**J(POS))
        J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=avancar]'); const k=b.cloneNode(true); k.id='injetado'; document.querySelector('header').appendChild(k);})()"); time.sleep(.2)
        sujo=dict(medida('SAF etapa 3 + cópia injetada'),**J(POS)); J("document.getElementById('injetado').remove()")
        chk('29b controle negativo da verificação: SAF etapa 3 limpa (0 duplicata, 1 primária, 0 avanço fora da área, 0 controle no indicador); com uma cópia do avanço injetada no cabeçalho a medida acusa duplicata, 2 primárias e avanço fora da área',
            limpo['dup']==0 and len(limpo['prims'])==1 and limpo['fora']==0 and limpo['foc']==0 and sujo['dup']>=1 and len(sujo['prims'])==2 and sujo['fora']==1, [limpo,sujo])
        info('duplicatas e primárias por estado',[(m['estado'],m['dup'],m['prims']) for m in M])
        # 31 · v3.1 em repouso nas páginas que tinham ação repetida no merge (e91a7f4; BO-01det, BO-02det e BO-03det saíram em 06/10, PLAT-01): trilha sem link no nível de área, cadeia sem elo que
        #      repete o primário, índice sem destino repetido, app sem rodapé/cartão em dobro; e estados: AG-01det com a OS-0420 encerrada (o elo
        #      volta a ser link e o primário muda), MB-01 → MB-05 pela âncora da ordem (o selo nomeia a ordem) e o MB-05 sem âncora igual
        P20=['AG-01det','AG-03det','AG-04det','AG-06','CA-01x-os0420','CD-01det','MB-01','MB-02','MB-09','MB-10','Main',
             'ON-01det','PL-02','PT-02det','PT-04det','PT-05det','SU-02']
        d20={}
        for pg in P20:
            abre(pg); d=J(DUPJS); d20[pg]=len(d.get('mesmoRotulo',[]))+len(d.get('mesmoDestino',[]))
        abre('AG-01det'); os0=J("[...document.querySelectorAll('a[href=\"OS.dc.html#OS-0420\"]')].filter(a=>a.getClientRects().length).length")
        # o AG-01det não expõe o cenário (cenGet/cenSave ficam no escopo da página): encerra a OS-0420 pela tela das O.S. (window.__cen) e grava
        # no cenário compartilhado (talhao-os-cenario-v1), como depois de qualquer ação; o AG-01det relê o cenário ao abrir
        abre('OS',limpa=False)
        fechou=J("(()=>{ try{ const C=window.__cen; if(!C) return 'sem window.__cen'; const c=C.cenGet(); const o=c.ordens['OS-0420']; if(!o) return 'sem OS-0420'; o.etapa='Encerradas'; c.rev=(c.rev||0)+1; localStorage.setItem('talhao-os-cenario-v1', JSON.stringify(c)); return 'ok'; }catch(e){ return 'erro '+e.message; } })()")
        abre('AG-01det',limpa=False); d=J(DUPJS); os1=J("[...document.querySelectorAll('a[href=\"OS.dc.html#OS-0420\"]')].filter(a=>a.getClientRects().length).map(a=>a.closest('header')?'cabeçalho':'conteúdo')")
        dupE=len(d.get('mesmoRotulo',[]))+len(d.get('mesmoDestino',[])); J("localStorage.clear()")
        abre('MB-01'); h5=J("(()=>{ const a=[...document.querySelectorAll('a[href^=\"MB-05.dc.html#OS-\"]')].find(a=>a.getClientRects().length); return a?a.getAttribute('href'):''; })()")
        sel=''; sel0=''
        if h5:
            abre('MB-05',hash=h5.split('MB-05.dc.html')[1],limpa=False); sel=J("(document.querySelector('header')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        abre('MB-05'); sel0=J("(document.querySelector('header')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        oid=h5.split('#')[1] if h5 else '?'
        chk('31 v3.1 · 0 ação repetida nas 17 páginas do merge que seguem geradas; AG-01det: 1 link para a OS-0420 em repouso e, com ela encerrada, o elo volta a ser link sem repetir; MB-01 → MB-05#ordem nomeia a ordem e o MB-05 sem âncora não',
            all(v==0 for v in d20.values()) and os0==1 and fechou=='ok' and dupE==0 and os1==['conteúdo'] and bool(h5) and oid in sel and oid not in sel0,
            [{k:v for k,v in d20.items() if v},os0,fechou,dupE,os1,h5,sel[:120],sel0[:120]])
        ERRL.extend(errs()); chk('30 sem erro de JS (v3)', not ERRL, ERRL[:5])
finally:
    if c: c.close()
    srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
