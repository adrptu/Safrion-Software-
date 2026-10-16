# -*- coding: utf-8 -*-
"""Base comum (só leitura): serve o render limpo de ff3903d e abre Chrome por CDP. Nada é escrito no repositório."""
import os, sys, time, json
G = '/home/user/sp-v69/tools/prototipo/v37/gen37'
R = '/tmp/claude-0/v69b/tools/prototipo/v37/gen37/_render'
OUT = '/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/ex38/out'
sys.dont_write_bytecode = True
sys.path.insert(0, G)
from comp_lib import Chrome, servir

class S:
    def __init__(self, w=1440, h=1000, toque=False):
        self.port, self.srv = servir(R)
        self.c = Chrome(); self.c.aparelho(w, h, 1, toque); self.J = self.c.js
        self.base = f'http://127.0.0.1:{self.port}/'
    def reset(self, perfil='Ana'):
        self.c.goto(self.base + 'Main.dc.html')
        self.J(f"localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)}); 1")
    def perfil(self, p):
        self.J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(p)}); 1")
    def go(self, page, espera=1.0):
        self.c.goto(self.base + page, espera=espera)
        self.J("window.__errs=window.__errs||[]; if(!window.__ouve){window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message));} 1")
    def body(self):
        return self.J("document.body.innerText") or ''
    def save(self, nome, txt):
        open(os.path.join(OUT, nome), 'w', encoding='utf-8').write(txt)
    def shot(self, nome):
        self.c.shot(os.path.join(OUT, nome))
    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
