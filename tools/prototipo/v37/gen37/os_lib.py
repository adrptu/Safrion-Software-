# -*- coding: utf-8 -*-
"""Apoio dos testes da O.S. com o cenário compartilhado (os_*.py): servidor local de _render/, Chrome headless (cdp.py) e ações curtas
na OS.dc.html. Cada execução usa um perfil novo do Chrome (cenário limpo). O Estoque e o App são simulados por cenMudar na própria
página (window.__cen) seguido do aviso de mudança (StorageEvent), como faria outro quadro do Canvas."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')


class Os:
    def __init__(self, copiar=True):
        if copiar:
            open(os.path.join(R, 'OS.dc.html'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'project', 'OS.dc.html'), encoding='utf-8').read())
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free()); self.c.size(1440, 1000); self.J = self.c.js; self.FAIL = []; self.n = 0

    def abrir(self, wait=1.0):
        self.c.goto(f'http://127.0.0.1:{self.p}/OS.dc.html', wait=wait)
        self.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }")

    # ---- tela ----
    def linha(self, id_):
        return self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    def ordem(self, id_):
        self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r&&r.click();}})()"); time.sleep(.4)
    def pan(self): return self.J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
    def ins(self): return self.J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const t=a.innerText; return t.slice(t.indexOf('INSUMOS'),t.indexOf('APONTAMENTOS')).replace(/\\s+/g,' ');})()") or ''
    def aps(self): return self.J("[...document.querySelectorAll('aside[role=dialog] [style*=\"grid-template-columns: 64px\"]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' '))") or []
    def temb(self, t): return bool(self.J(f"[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==={json.dumps(t)})"))
    def btn(self, t, root='aside[role=dialog]'):
        r = self.J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root + ' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.35); return r
    def link(self, t): return self.J(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.innerText.trim().startsWith({json.dumps(t)})); return a?a.getAttribute('href'):'';}})()") or ''
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def fechar(self): self.J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
    def erros(self): return self.J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText)).concat(window.__err?[window.__err]:[])") or []
    def shot(self, nome): self.c.shot(os.path.join(HERE, '_probe', nome))

    # ---- cenário ----
    def cen(self, expr):
        """Lê o cenário na própria página (cenGet) — expr recebe c."""
        return self.J(f"(()=>{{const X=window.__cen; const c=X.cenGet(); return ({expr});}})()")
    def mudar(self, fnbody, avisar=True):
        """Muda o cenário como outra tela (Estoque/App): cenMudar sem a tela da O.S. e, depois, o aviso de mudança (StorageEvent)."""
        r = self.J(f"(()=>{{const X=window.__cen; with(X){{ const r=cenMudar(null,c=>{{{fnbody}}}); return r.erro||r.msg||''; }} }})()")
        if avisar:
            self.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
        return r

    def ok(self, cond, msg, extra=''):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg + ((' · ' + str(extra)[:300]) if (extra != '' and not cond) else ''))
        if not cond: self.FAIL.append(msg)

    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'RESULTADO: {self.n - len(self.FAIL)}/{self.n} ok' + (' · FALHAS: ' + '; '.join(self.FAIL) if self.FAIL else ''))
        return not self.FAIL
