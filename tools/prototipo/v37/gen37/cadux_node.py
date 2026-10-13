# -*- coding: utf-8 -*-
"""CADUX · roda a lógica de uma página gerada (project/*.dc.html) no node, sem navegador: o script da tela (GRIDS, g2lib, g2end e o JS da
tela) recebe uma janela mínima (location, history, sessionStorage/localStorage em memória, matchMedia pela largura) e um componente que
desenha de novo a cada setState. Serve aos testes de unidade das regras (cadux_unit_test.py): o que a tela calcula e mostra nos buracos
(v.*), sem medir layout, foco nem toque (isso é do teste de navegador, cadux_*_test.py).
Uso: from cadux_node import roda; out = roda('CD-01', cenario_js, larga=True, hash='#faz=SR')  → dict (o que o cenário pôs em OUT)."""
import os, re, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, 'project')
STUB = r"""
const __mem=(o)=>({getItem:k=>(k in o?o[k]:null),setItem:(k,x)=>{o[k]=String(x);},removeItem:k=>{delete o[k];},clear:()=>{for(const k in o) delete o[k];}});
const __ls={}, __ss={}; globalThis.localStorage=__mem(__ls); globalThis.sessionStorage=__mem(__ss);
const __hist=[]; const __L={hash:__HASH__,pathname:'/'+__PAG__+'.dc.html',search:''};
globalThis.location=__L;
const __ev={}; globalThis.window={matchMedia:(q)=>({matches:/min-width: 1024px/.test(q)?__LARGA__:(/max-width: 1023px/.test(q)?!__LARGA__:(/pointer: ?fine/.test(q)?__LARGA__:false)),addEventListener(){},addListener(){}}),
  addEventListener:(t,f)=>{(__ev[t]=__ev[t]||[]).push(f);},innerWidth:__LARGA__?1440:390,innerHeight:__LARGA__?1000:844};
globalThis.history={state:null,_pilha:[{state:null,hash:__HASH__}],_i:0,
  pushState(s,t,u){ this._pilha=this._pilha.slice(0,this._i+1); this._pilha.push({state:s,hash:(String(u).split('#')[1]?'#'+String(u).split('#')[1]:'')}); this._i++; this.state=s; __L.hash=this._pilha[this._i].hash; },
  replaceState(s,t,u){ this._pilha[this._i]={state:s,hash:(String(u).split('#')[1]?'#'+String(u).split('#')[1]:'')}; this.state=s; __L.hash=this._pilha[this._i].hash; },
  back(){ if(this._i>0){ this._i--; this.state=this._pilha[this._i].state; __L.hash=this._pilha[this._i].hash; (__ev.popstate||[]).forEach(f=>f({})); } else { __L.saiu=true; } }};
globalThis.document=undefined;
let __tq=[]; globalThis.setTimeout=(f,ms)=>{ __tq.push(f); return __tq.length; }; globalThis.clearTimeout=()=>{};
globalThis.requestAnimationFrame=(f)=>{ __tq.push(f); return 1; };
const __errs=[];
// setState como o runtime do protótipo (support.js, __setLogicState): o estado da lógica muda na hora (this.state = {...antes, ...novo})
// e o desenho fica para depois do tratador, em lote. Quem lê this.state logo depois do setState já vê o novo estado; o renderVals
// (PREVALS/EXTRAVALS) só roda no fim (o g2after do salvar depende disso para ler o nome antigo guardado no último desenho).
let __pend=new Map();
class DCLogic{ constructor(p){ this.props=p||{}; } setState(p){ const x=(typeof p==='function')?p(this.state):p; if(!__pend.has(this)) __pend.set(this,this.state); this.state=Object.assign({},this.state,x||{}); } }
function __flush(){ if(!__pend.size) return; const q=__pend; __pend=new Map();
  q.forEach((ps,c)=>{ c.__v=null; try{ c.__v=c.renderVals(); }catch(e){ __errs.push('render: '+String(e&&e.stack||e).slice(0,500)); } if(c.componentDidUpdate) try{ c.componentDidUpdate({},ps); }catch(e){} }); }
function __roda(){ __flush(); for(let n=0;n<50&&(__tq.length||__pend.size);n++){ __flush(); const q=__tq; __tq=[]; q.forEach(f=>{ try{ f(); }catch(e){ __errs.push('timeout: '+String(e&&e.stack||e).slice(0,300)); } __flush(); }); } }
"""
TAIL = r"""
const C=new Component({}); let V=null; try{ V=C.renderVals(); C.__v=V; }catch(e){ __errs.push('render0: '+String(e&&e.stack||e).slice(0,600)); }
__roda();
const OUT={};
function v(){ __roda(); return C.__v||C.renderVals(); }
function st(){ __flush(); return C.state; }   // depois do tratador o runtime desenha
function linhas(gid){ return (v()[gid+'_rows']||[]).map(r=>({id:r.id,t:r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | ')})); }
function painel(gid){ const F=v()[gid+'_F']; return F&&F.open?F:null; }
function hash(){ return location.hash; }
try{
__CENARIO__
}catch(e){ __errs.push('cenario: '+String(e&&e.stack||e).slice(0,600)); }
__roda(); OUT.__errs=__errs; console.log(JSON.stringify(OUT));
"""
# auxiliares dos cenários (cadux_unit_test.py e os testes de Cadastros reescritos no P9): campo do formulário aberto, erros, salvar
# (com o aviso lido antes de os temporizadores o limparem), painel em consulta, alvo da linha, mestre e o armazenamento do navegador
AUX = r"""
function fset(gid,k,val){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); if(!f) throw new Error('sem campo '+k+' em '+gid); f.set({target:{value:val,checked:val}}); v(); }
function fmulti(gid,k,vals){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); if(!f) throw new Error('sem campo '+k); (f.mopts||[]).forEach(o=>{ const on=vals.indexOf(o.t||o.v)>=0; if(!!o.on!==on&&o.tog) { o.tog(); v(); } }); v(); }
function fval(gid,k){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); return f?f.v:undefined; }
function fdis(gid,k){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); return f?!!f.dis:undefined; }
function fopts(gid,k){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); return f?(f.opts||[]).map(o=>(o&&o.t!==undefined)?o.t:o):undefined; }
function fhelp(gid,k){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); return f?(f.help||''):undefined; }
function rotulos(gid){ const F=painel(gid); return F?F.fields.map(f=>f.l):[]; }
function erros(gid){ const F=painel(gid); return F?F.fields.filter(f=>f.err).map(f=>f.fid.replace('fx_'+gid+'_','')+': '+f.errMsg):null; }
function errosT(gid){ return (erros(gid)||[]).join(' | '); }
function salva(gid){ painel(gid).save(); const t=st().g2toast||''; v(); return t; }
function cancela(gid){ const F=painel(gid); if(F) F.cancel(); v(); const G=painel(gid); if(G&&G.warn&&G.discard){ G.discard(); v(); } }
function fecha(gid){ const F=painel(gid); if(F) F.close(); v(); const G=painel(gid); if(G&&G.warn&&G.discard){ G.discard(); v(); } }
function cons(gid){ const F=painel(gid); return (F&&F.cons)?{t:F.title,sub:F.sub,prox:F.c.proxT,prim:F.c.primT,sec:(F.c.sec||[]).map(s=>s.t),txt:JSON.stringify(F.c.blocos)}:null; }
function consGo(gid,txt){ const F=painel(gid); const s=[(F.c.prim?{t:F.c.primT,go:F.c.prim}:null)].concat(F.c.sec||[]).concat(F.c.menu||[]).filter(Boolean).find(x=>x.t===txt||String(x.t).indexOf(txt)===0); if(!s) throw new Error('sem ação '+txt); s.go(); v(); }
function alvos(gid){ return (v()[gid+'_rows']||[]).map(r=>({id:r.id,tab:r.tab,n:r.cells.filter(c=>c.isData).reduce((a,c)=>a+c.parts.filter(p=>p.isAct&&p.cls==='g2alvo').length,0)})); }
function abre(gid,rid){ const r=(v()[gid+'_rows']||[]).find(x=>x.id===rid); if(!r) throw new Error('sem linha '+rid+' em '+gid); const p=r.cells.find(c=>c.isData).parts.find(p=>p.isAct&&p.cls==='g2alvo'); if(!p) throw new Error('linha sem alvo '+rid); p.fn(); v(); }
function edita(gid,rid,foco){ g2open(C,GR(gid),rid,null); v(); g2editar(C,GR(gid),rid,foco); v(); }
function mestre(id){ const i=v().mx_itens.find(i=>i.id===id||i.t===id); if(!i) throw new Error('sem item no mestre '+id); i.go(); return v(); }
function linhaTxt(gid,rid){ const r=(v()[gid+'_rows']||[]).find(x=>x.id===rid); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):null; }
function ls(){ return JSON.stringify(__ls); }
"""
def script(pag):
    s = open(os.path.join(P, pag + '.dc.html'), encoding='utf-8').read()
    m = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S)
    return m.group(1)
def roda(pag, cenario, larga=True, hash='', antes=''):
    """antes: JS que roda antes do 1º desenho (ex.: gravar localStorage/sessionStorage)."""
    js = (STUB.replace('__HASH__', json.dumps(hash)).replace('__PAG__', json.dumps(pag)).replace('__LARGA__', 'true' if larga else 'false')
          + antes + '\n' + script(pag) + '\n' + TAIL.replace('__CENARIO__', cenario))
    f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(js); f.close()
    try:
        r = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=120)
    finally:
        os.unlink(f.name)
    if r.returncode:
        return {'__errs': ['node: ' + (r.stderr or '')[-800:]]}
    try: return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: return {'__errs': ['saída: ' + (r.stdout or '')[-500:] + (r.stderr or '')[-300:]]}
