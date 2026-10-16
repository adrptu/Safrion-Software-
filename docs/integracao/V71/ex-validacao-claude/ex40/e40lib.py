# -*- coding: utf-8 -*-
"""Base comum da reprodução EX-40/EX-26 (só leitura): serve o render limpo de b87f79b (worktree próprio) e abre Chrome por CDP.
Nada é escrito no código do protótipo; as saídas vão para ./out. Dados sintéticos."""
import os, sys, time, json
os.environ.setdefault('CHROME_BIN', '/tmp/cloudchrome/chrome')
WT = '/tmp/claude-0/ex40'
G = WT + '/tools/prototipo/v37/gen37'
R = G + '/_render'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
sys.dont_write_bytecode = True
sys.path.insert(0, G)
from comp_lib import Chrome, servir

class S:
    def __init__(self, w=1440, h=1000, toque=False):
        self.port, self.srv = servir(R)
        self.c = Chrome(); self.c.aparelho(w, h, 1, toque); self.J = self.c.js
        try: open('/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/cdp_meus.txt', 'a').write(str(self.c.dir) + '\n')
        except Exception: pass
        self.base = f'http://127.0.0.1:{self.port}/'
        self.log = []
    def reset(self, perfil='Ana'):
        self.c.goto(self.base + 'Main.dc.html')
        self.J(f"localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)}); 1")
    def perfil(self, p):
        self.J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(p)}); 1")
    def go(self, page, espera=1.0):
        self.c.goto(self.base + page, espera=espera)
    def body(self):
        return self.J("document.body.innerText") or ''
    def errs(self):
        return self.J("(window.__errs||[]).slice(0,5)") or []
    def toast(self):
        return self.J("(()=>{const t=[...document.querySelectorAll('[role=status],[role=alert],.g2toast,[aria-live]')].map(e=>e.innerText.trim()).filter(Boolean);return t.join(' | ').slice(0,600);})()") or ''
    def clk(self, txt, raiz='document', exato=False, idx=0):
        """clica no idx-ésimo elemento visível (button, a, [role=menuitem], [role=tab]) cujo texto (ou aria-label) contém/é txt. Devolve o texto clicado ou None."""
        r = self.J("((t,ex,i)=>{const R=%s; const vis=e=>e.getClientRects().length>0; const nm=e=>(e.innerText||e.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim();"
                   " const L=[...R.querySelectorAll('button,a,[role=menuitem],[role=tab],[role=option],summary')].filter(e=>vis(e)&&(ex?nm(e)===t:nm(e).includes(t)));"
                   " const e=L[i]; if(!e) return null; e.scrollIntoView({block:'center'}); e.click(); return nm(e).slice(0,120);})(%s,%s,%d)" % (raiz, json.dumps(txt), 'true' if ex else 'false', idx))
        time.sleep(.5); return r
    def conta(self, txt):
        """quantos elementos visíveis de ação têm o texto txt (contém)."""
        return self.J("((t)=>[...document.querySelectorAll('button,a,[role=menuitem],[role=tab],summary,label')].filter(e=>e.getClientRects().length>0&&(e.innerText||e.getAttribute('aria-label')||'').includes(t)).length)(%s)" % json.dumps(txt))
    def save(self, nome, txt):
        open(os.path.join(OUT, nome), 'w', encoding='utf-8').write(txt if isinstance(txt, str) else json.dumps(txt, ensure_ascii=False, indent=1))
    def shot(self, nome):
        self.c.shot(os.path.join(OUT, nome))
    def p(self, *a):
        s = ' '.join(str(x) for x in a); print(s, flush=True); self.log.append(s)
    def fim(self, nome_log=None):
        if nome_log: self.save(nome_log, '\n'.join(self.log) + '\n')
        try: self.c.close()
        finally: self.srv.terminate()

# ---------- clique de verdade (mouse no centro do elemento), contado ----------
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def BTN(txt, raiz='document'):
    return f"[...{raiz}.querySelectorAll('button,a,[role=menuitem],[role=tab],summary')].find(b=>b.getClientRects().length&&{N}(b.innerText||b.getAttribute('aria-label'))==={json.dumps(txt)})"
def BTNC(txt, raiz='document'):
    return f"[...{raiz}.querySelectorAll('button,a,[role=menuitem],[role=tab],summary')].find(b=>b.getClientRects().length&&{N}(b.innerText||b.getAttribute('aria-label')).startsWith({json.dumps(txt)}))"
def LAB(txt):
    return f"[...document.querySelectorAll('button,a,select,input')].find(b=>b.getClientRects().length&&(b.getAttribute('aria-label')||'').startsWith({json.dumps(txt)}))"
def _centro(s, sel, limite=2.0):
    fim = time.time() + limite
    while True:
        r = s.J(f"(()=>{{const e={sel}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); const x=r.left+r.width/2, y=r.top+r.height/2; const t=document.elementFromPoint(x,y); return [x,y,!!t&&(e===t||e.contains(t))];}})()")
        if not r or r[2] or time.time() >= fim: return r[:2] if r else None
        time.sleep(.15)
def clique(s, sel, w=.6):
    xy = _centro(s, sel)
    if not xy: return 'NÃO ACHEI'
    s.cliques = getattr(s, 'cliques', 0) + 1
    s.c.mouse(*xy); s.c.mouse(*xy, 'mousePressed', 'left'); s.c.mouse(*xy, 'mouseReleased', 'left')
    time.sleep(w); return 'ok'
