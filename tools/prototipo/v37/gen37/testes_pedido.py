# -*- coding: utf-8 -*-
"""Bateria dos 12 testes pedidos pelo proprietário em 25/09/2026 — executados no protótipo servido localmente (Chrome headless).
Atualizado em 01/10/2026 (decisões do proprietário): o T12 lê o mapa da Santa Rita na camada Ordens de serviço e compara app e mapa
só nas ordens que a tela O.S. mostra (as ordens só de água OS-0419/0422/0423 saíram da O.S. e seguem no app do irrigante)."""
import sys, os, time, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'..','validacao','pedido-2509')
os.makedirs(OUT,exist_ok=True)
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'sem raiz'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.innerText).includes(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
class T:
    def __init__(s,c,base,nome): s.c=c; s.base=base; s.nome=nome; s.passos=[]; s.ok=True; s.n=0
    def js(s,x): return s.c.js(x)
    def abrir(s,f): s.c.goto(s.base+f,wait=1.4); s.log(f'Abrir {f}',True)
    def clk(s,t,root=None,esperado=True):
        r=s.js(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.5); s.log(f'Clicar "{t}"',r=='ok' if esperado else True,r); return r
    def setv(s,sel,val): r=s.js(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.3); s.log(f'Preencher {sel} = {val}',r=='ok',r)
    def aviso(s): return s.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def form(s): return s.js("!!document.querySelector('aside[role=dialog]')")
    def check(s,desc,cond,obs=''): s.log(desc,bool(cond),obs)
    def log(s,desc,ok,obs=''):
        s.passos.append(dict(passo=desc,ok=bool(ok),obs=str(obs)[:300]))
        if not ok: s.ok=False
    def foto(s,nome):
        s.n+=1; f=f'{s.nome}_{s.n:02d}_{nome}.png'
        w=s.js("Math.max(document.documentElement.scrollWidth,390)"); h=s.js("Math.min(Math.max(document.documentElement.scrollHeight,600),2600)")
        s.c.size(w,h); time.sleep(.3); s.c.shot(os.path.join(OUT,f)); s.c.size(1440,1000); s.passos.append(dict(passo='Evidência',ok=True,obs=f))
def row_click(t,texto,sel="[role=row].g2ed"):
    return t.js(f"""(()=>{{const r=[...document.querySelectorAll('{sel}')].find(r=>r.innerText.indexOf({json.dumps(texto)})>=0); if(!r) return 'sem linha'; const c=r.querySelector('[role=cell] span')||r.querySelector('[role=cell]'); c.click(); return 'ok';}})()""")
def abrir_safra(t):
    t.abrir('SAF.dc.html'); t.js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.5)
from comp_lib import IR_ETAPA
def etapa(t,i): r=t.js(f"({IR_ETAPA})({i})"); time.sleep(.5); return r   # a faixa só informa (UX-ACAO-UNICA-20261003): anda pela área de ações
# ---------------------------------------------------------------- testes
def t01(t):
    """Escolher/criar safra e percorrer as seis etapas."""
    t.abrir('SAF.dc.html')
    t.check('Nenhuma safra escolhida automaticamente',t.js("document.body.innerText.indexOf('Nenhuma safra escolhida')>=0"))
    t.clk('Nova safra'); t.check('Formulário "Nova safra" abriu pela direita',t.form())
    ids=t.js("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].map(i=>i.id)")
    t.setv('#'+ids[0],'Safra 2027/28'); t.setv('#'+ids[1],'set/2027 – ago/2028')
    t.clk('Salvar','aside[role=dialog]'); t.check('Safra criada e aberta na etapa 2',t.js("document.querySelector('[aria-current=step]').innerText.indexOf('Defina cultivos')>=0"),t.aviso())
    t.foto('nova-safra')
    r1=etapa(t,1); t.log('Voltar à etapa 1 (área de ações; a faixa só informa)',r1==1,r1); t.clk('Continuar')  # abre a 2026/27 no próximo passo (etapa 2)
    for i in range(2,7):
        etapa(t,i); cur=t.js("document.querySelector('[aria-current=step]').innerText.replace(/\\s+/g,' ')")
        t.check(f'Etapa {i} aberta pela área de ações',cur.startswith(str(i)),cur)
    t.foto('etapa6')
def t02(t):
    """Aplicar um plano a vários cultivos e ajustar somente um."""
    abrir_safra(t)
    n=t.js("""(()=>{let n=0; [...document.querySelectorAll('[role=row].g2ed')].forEach(r=>{ if(/\\b(T4|T3|P1|P2)\\b/.test(r.innerText)){ r.querySelector('input[type=checkbox]').click(); n++; } }); return n;})()"""); time.sleep(.4)
    t.check('4 cultivos selecionados (seleção não abre edição)',n==4 and not t.form(),n)
    t.clk('Aplicar plano'); t.setv('#ap_sel','SOJA-AT'); t.clk('Aplicar plano','aside[role=dialog]')
    t.check('Plano aplicado aos 4',('aplicado a 4 cultivos' in t.aviso()),t.aviso())
    r=t.js("""(()=>{const row=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bT4\\b/.test(r.innerText)); const b=[...row.querySelectorAll('button')].find(b=>/Soja alta tecnologia/.test(b.innerText)); b.click(); return 'ok';})()"""); time.sleep(.5)
    t.check('Clique no nome do plano abre atividades locais do T4',t.js("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''").find('T4')>=0)
    t.setv('#lp_a6_0','0,65'); t.clk('Salvar','aside[role=dialog]')
    t.check('Ajuste salvo só para T4',('só para T4' in t.aviso()),t.aviso())
    t.check('Somente T4 ganhou ajuste local (T3 continua sem)',t.js("""(()=>{const rs=[...document.querySelectorAll('[role=row].g2ed')]; const a=rs.find(r=>/\\bT4\\b/.test(r.innerText)).innerText; const b=rs.find(r=>/\\bT3\\b/.test(r.innerText)).innerText; return /ajuste/.test(a) && !/ajuste/.test(b);})()"""))
    t.foto('ajuste-so-T4')
def t03(t):
    """Expandir gatilhos, atividades e insumos."""
    t.abrir('PA.dc.html')
    t.check('Biblioteca de planos por cultura em cards',t.js("document.body.innerText.indexOf('Soja alta tecnologia')>=0"))
    r=t.clk('Soja alta tecnologia')
    t.check('Plano abriu com gatilhos agrupados (DAP)',t.js("document.body.innerText.indexOf('DAP')>=0"))
    carets=t.js("document.querySelectorAll('button[aria-label^=\"Expandir\"],button[aria-label^=\"Recolher\"]').length")
    t.check('Há setas de expandir/recolher',carets>0,carets)
    before=t.js("document.body.innerText.length"); t.js("(()=>{const b=document.querySelector('button[aria-label^=\"Recolher\"],button[aria-label^=\"Expandir\"]'); b.click();})()"); time.sleep(.4)
    t.check('Seta expande/recolhe sem abrir edição',not t.form() and t.js("document.body.innerText.length")!=before)
    t.foto('planos')
    abrir_safra(t); etapa(t,6); t.clk('Expandir tudo')
    t.check('Demanda: grupos expandidos mostram insumos',t.js("document.body.innerText.indexOf('Glifosato 480')>=0"))
def t04(t):
    """Encaminhar demanda para compras mantendo a origem."""
    abrir_safra(t); etapa(t,6)
    # 01/10: com tudo já enviado, a etapa 6 não oferece novo envio (não há como duplicar) e a ação principal abre a Compra
    tem_env=t.js("[...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Enviar para cotação')")
    if tem_env: t.clk('Enviar para cotação'); t.check('Envio não duplica solicitação existente',('Nenhuma solicitação duplicada' in t.aviso()) or ('enviada' in t.aviso()),t.aviso())
    else: t.check('Envio não duplica solicitação existente (nada a enviar: só "Abrir Compra de insumos")',t.js("[...document.querySelectorAll('button,a')].some(b=>/^Abrir Compra de insumos/.test(b.innerText.trim()))"),'')   # AÇÃO: ir a outra tela é link (área de ações)
    t.clk('Abrir Compra de insumos'); time.sleep(1.2)
    t.check('Abriu Compra de insumos',t.js("location.pathname").endswith('CMP.dc.html'))
    t.check('Compras mostra a SOL-2026-07',t.js("document.body.innerText.indexOf('SOL-2026-07')>=0"))
    t.check('Compras mostra a origem (Planejar safra · Safra 2026/27)',t.js("/Planejar safra/.test(document.body.innerText) && /2026\\/27/.test(document.body.innerText)"))
    t.foto('compras-origem')
def t05(t):
    """Navegar entre etapas sem perder dados."""
    abrir_safra(t)
    row_click(t,'T2'); time.sleep(.4); fid=t.js("[...document.querySelectorAll('aside[role=dialog] input')].find(i=>/_area$/.test(i.id)).id")
    t.setv('#'+fid,'250'); t.clk('Salvar','aside[role=dialog]')
    etapa(t,4); k1=t.js("document.body.innerText.match(/[\\d.]+ ha trabalhados/)[0]")
    etapa(t,2); t.check('Área editada preservada ao voltar (250 ha, 48 ha livres)',t.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bT2\\b/.test(r.innerText)).innerText.indexOf('250 ha')>=0") and t.js("document.body.innerText.indexOf('48 ha livres')>=0"))
    etapa(t,6); etapa(t,4); k2=t.js("document.body.innerText.match(/[\\d.]+ ha trabalhados/)[0]")
    t.check('Plano operacional mantém o recálculo entre idas e voltas',k1==k2,f'{k1} = {k2}')
def t06(t):
    """Clicar na linha para editar pelo formulário lateral."""
    for f,txt in [('SAF.dc.html',None),('CD-05.dc.html','Fertisul'),('EST.dc.html',None)]:
        if f=='SAF.dc.html': abrir_safra(t); r=row_click(t,'T1-A')
        else:
            t.abrir(f); r=row_click(t,txt) if txt else t.js("(()=>{const r=document.querySelector('[role=row].g2ed'); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})()")
        time.sleep(.4); t.check(f'{f}: clique na linha abre formulário preenchido',t.form() and t.js("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].some(i=>i.value)"),r)
        if f=='CD-05.dc.html': t.foto('fornecedor-form')
        t.clk('Cancelar','aside[role=dialog]',esperado=False); t.clk('Fechar','aside[role=dialog]',esperado=False)
def t07(t):
    """Expandir, selecionar ou excluir sem abrir acidentalmente a edição."""
    abrir_safra(t)
    t.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bP2\\b/.test(r.innerText)).querySelector('input[type=checkbox]').click()"); time.sleep(.3)
    t.check('Selecionar não abre edição',not t.form())
    t.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bP2\\b/.test(r.innerText)).querySelector('button.g2del').click()"); time.sleep(.3)
    t.check('Excluir pede confirmação e não abre edição',not t.form() and t.js("document.body.innerText.indexOf('Excluir?')>=0"))
    t.clk('Manter'); t.check('Manter preserva o registro',t.js("[...document.querySelectorAll('[role=row].g2ed')].some(r=>/\\bP2\\b/.test(r.innerText))"))
    etapa(t,3); t.js("document.querySelector('button.g2car').click()"); time.sleep(.3)
    t.check('Seta de drill só recolhe/expande',not t.form())
    etapa(t,6); t.js("document.querySelector('button.g2car').click()"); time.sleep(.3)
    t.check('Seta de drill na demanda não abre painel',not t.form())
def t08(t):
    """Salvar, cancelar e tratar alterações não salvas."""
    abrir_safra(t); row_click(t,'T3'); time.sleep(.4)
    fid=t.js("[...document.querySelectorAll('aside[role=dialog] input')].find(i=>/_area$/.test(i.id)).id")
    t.setv('#'+fid,''); t.clk('Salvar','aside[role=dialog]'); t.check('Erro junto ao campo, preenchido preservado',t.js("document.querySelector('aside[role=dialog]').innerText.indexOf('Informe área')>=0"))
    t.setv('#'+fid,'99'); t.clk('Cancelar','aside[role=dialog]'); t.check('Aviso de alterações não salvas',t.js("document.body.innerText.indexOf('Há alterações não salvas')>=0"))
    t.foto('nao-salvo')
    t.clk('Descartar alterações'); t.check('Cancelar preserva o valor anterior (96 ha)',t.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bT3\\b/.test(r.innerText)).innerText.indexOf('96 ha')>=0"))
    row_click(t,'T3'); time.sleep(.3); t.setv('#'+fid,'90'); t.clk('Salvar','aside[role=dialog]')
    t.check('Salvar atualiza a linha e o total',t.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/\\bT3\\b/.test(r.innerText)).innerText.indexOf('90 ha')>=0") and t.js("document.body.innerText.indexOf('1.159 ha')>=0"),t.aviso())
def t09(t):
    """Consultar registros sem permissão de edição."""
    t.abrir('SAF.dc.html'); t.clk('Consultar safra'); time.sleep(.3)
    r=row_click(t,'T1'); time.sleep(.4)
    t.check('Cultivo de safra encerrada abre em consulta (sem Salvar)',t.form() and not t.js("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Salvar')"),r)
    t.foto('consulta')
    t.clk('Fechar','aside[role=dialog]')
def t10(t):
    """Abrir a origem de indicadores calculados."""
    abrir_safra(t); etapa(t,6); t.clk('Expandir tudo'); row_click(t,'Fungicida A'); time.sleep(.4)
    t.check('Insumo calculado abre origem (consulta com cultivos e atividades)',t.form() and t.js("document.querySelector('aside[role=dialog]').innerText.indexOf('ORIGEM')>=0 && /T1-B/.test(document.querySelector('aside[role=dialog]').innerText)"))
    t.foto('origem-demanda')
    t.clk('Fechar','aside[role=dialog]')
    t.js("document.querySelector('.g2tot').click()"); time.sleep(.4)
    t.check('Total abre a composição (sem edição)',t.form() and t.js("document.querySelector('aside[role=dialog]').innerText.indexOf('Composição do total')>=0 && ![...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Salvar')"))
def t12(t):
    """Conferir a consistência das fases das O.S. entre as diferentes visualizações.
    Decisões de 01/10/2026: as ordens só de água (OS-0419/0422/0423) não são O.S. agrícolas, saem da tela O.S. e da camada Ordens de serviço
    do mapa e seguem no app do irrigante; por isso app e mapa são comparados só nas ordens que a tela O.S. mostra, e o mapa (Santa Rita) é lido
    na camada Ordens de serviço, a única cujo painel do talhão traz os cartões das O.S."""
    import dados as D
    FASES='A liberar|Liberadas|Em execução|Em conferência|Encerradas'
    esperado={o['id']:o['etapa'] for o in D.ORDENS if o['id'].startswith('OS-')}
    agua={o['id'] for o in D.ORDENS if o['id'].startswith('OS-') and str(o.get('tipo','')).startswith('Irrigação')}
    def blocos(txt):
        out={}
        ids=[(m.start(),m.group(0)) for m in re.finditer(r'OS-04\d\d',txt)]
        for i,(pos,oid) in enumerate(ids):
            fim=ids[i+1][0] if i+1<len(ids) else len(txt)
            m=re.search(FASES,txt[pos:min(fim,pos+400)])
            if m and oid not in out: out[oid]=m.group(0)
        return out
    vistas={}
    t.abrir('OS.dc.html'); vistas['Lista (OS)']=blocos(t.js("document.body.innerText"))
    t.clk('Kanban'); time.sleep(.4)
    kb=t.js("""(()=>{const o={}; const F=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']; const t=document.body.innerText; let cur=null; t.split('\\n').forEach(l=>{ const s=l.trim(); const f=F.find(x=>s.toUpperCase().startsWith(x.toUpperCase())); if(f && s.length<40) cur=f; const m=s.match(/^OS-04\\d\\d/); if(m && cur && !o[m[0]]) o[m[0]]=cur; }); return o;})()""")
    vistas['Kanban (OS)']=kb
    t.abrir('MB-02.dc.html'); vistas['App (MB-02)']=blocos(t.js("document.body.innerText"))
    t.abrir('CA-01det.dc.html'); vistas['Detalhe (CA-01det)']=blocos(t.js("document.body.innerText"))
    # mapa da Santa Rita na camada Ordens de serviço (01/10: o mapa abre na Lagoa Grande e só essa camada mostra as O.S. no painel do talhão)
    t.js("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita',lay:'O.S./prazos'}))"); t.abrir('IN-04.dc.html'); mp={}
    TAL="document.querySelectorAll('svg [role=button]')"
    n=t.js(f"{TAL}.length")
    for i in range(n or 0):
        t.js(f"{TAL}[{i}].dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
        pan=t.js("(()=>{const a=[...document.querySelectorAll('aside')].map(x=>x.innerText).join('\\n'); return a;})()") or ''
        for k,v in blocos(pan).items(): mp.setdefault(k,v)
        t.js(f"{TAL}[{i}].dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.2)
    vistas['Mapa (IN-04, painel do talhão)']=mp
    na_os=set(vistas['Lista (OS)'])
    t.check('Tela O.S. sem as ordens só de água; as demais O.S. do registro aparecem',na_os.isdisjoint(agua) and na_os==set(esperado)-agua,f'tela O.S.: {sorted(na_os)} · só de água no registro: {sorted(agua)}')
    t.check('Mapa (camada Ordens de serviço) só com ordens da tela O.S. (sem as de água)',set(mp)<=na_os,sorted(set(mp)-na_os))
    difs=[]; total=0
    for vn,d in vistas.items():
        lidas=[o for o in d if o in esperado and o in na_os]  # app e mapa: só as ordens que a tela O.S. mostra
        for oid in lidas:
            total+=1
            if d[oid]!=esperado[oid]: difs.append(f'{vn}: {oid} mostra "{d[oid]}", registro diz "{esperado[oid]}"')
        fora=sorted(o for o in d if o not in na_os)
        t.log(f'{vn}: {len(lidas)} ordens lidas'+(f' (fora da tela O.S., não comparadas: {", ".join(fora)})' if fora else ''),len(lidas)>0,json.dumps(d,ensure_ascii=False)[:280])
    t.check(f'Mesma fase em todas as visualizações ({total} leituras de fase comparadas)',not difs and total>=20,'; '.join(difs)[:600] if difs else f'{total} leituras, 0 divergências')
TESTES=[('T01','Escolher/criar safra e percorrer as seis etapas',t01),('T02','Aplicar um plano a vários cultivos e ajustar somente um',t02),
 ('T03','Expandir gatilhos, atividades e insumos',t03),('T04','Encaminhar demanda para compras mantendo a origem',t04),('T05','Navegar entre etapas sem perder dados',t05),
 ('T06','Clicar na linha para editar pelo formulário lateral',t06),('T07','Expandir, selecionar ou excluir sem abrir acidentalmente a edição',t07),
 ('T08','Salvar, cancelar e tratar alterações não salvas',t08),('T09','Consultar registros sem permissão de edição',t09),('T10','Abrir a origem de indicadores calculados',t10),
 ('T12','Conferir a consistência das fases das O.S. entre as visualizações',t12)]
if __name__=='__main__':
    sel=sys.argv[1:]
    p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
    res=[]
    try:
        for cod,nome,fn in TESTES:
            if sel and cod not in sel: continue
            c=Chrome(port=free()); c.size(1440,1000); t=T(c,f'http://127.0.0.1:{p}/',cod)
            try: fn(t)
            except Exception as ex: t.log('Execução',False,f'erro: {ex}')
            finally: c.close()
            res.append(dict(id=cod,teste=nome,resultado='passou' if t.ok else 'falhou',passos=t.passos,executado=time.strftime('%d/%m/%Y %H:%M')))
            print(f"{cod} {'PASSOU' if t.ok else 'FALHOU'} · {nome}"); [print('   ✗',x['passo'],'→',x['obs']) for x in t.passos if not x['ok']]
    finally: srv.terminate()
    old={}
    fp=os.path.join(OUT,'resultado.json')
    if os.path.exists(fp): old={r['id']:r for r in json.load(open(fp))}
    for r in res: old[r['id']]=r
    json.dump(sorted(old.values(),key=lambda r:r['id']),open(fp,'w'),ensure_ascii=False,indent=1)
