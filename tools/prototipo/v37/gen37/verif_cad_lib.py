# -*- coding: utf-8 -*-
"""Auxiliares das verificações independentes dos Cadastros (verif_cad.py, verif_cad2.py, verif_dirty.py) depois da CADUX (09/10/2026):
a linha abre o registro em consulta pelo alvo nomeado da 1ª célula (BOT-07, SEL-01) e "Editar {entidade}" abre o formulário lateral.
Antes, o clique na linha abria o formulário direto e as grades eram achadas pela posição na página; agora a linha é achada pelo texto em
qualquer grade visível. Só lê e imprime (não é teste de aceite)."""
import os, sys, time, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free

SETV = """((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN = """((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
CLK = """((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
EDIT = "[...document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled]),aside[role=dialog] select:not([disabled]),aside[role=dialog] textarea:not([readonly])')].filter(e=>e.getClientRects().length).length"


class V:
    def __init__(self):
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', os.path.join(HERE, '_render')],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.8); self.c = Chrome(port=free()); self.J = self.c.js

    def fim(self):
        self.c.close(); self.srv.terminate()

    def ir(self, pg, espera=1.0):
        self.c.goto(f'http://127.0.0.1:{self.p}/{pg}'); time.sleep(espera)

    def ROW(self, txt):
        return f"[...document.querySelectorAll('[role=table] [role=row][data-rid]')].filter(r=>r.offsetParent).find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"

    def abre(self, txt):
        """alvo da linha → painel em consulta"""
        r = self.J(f"(()=>{{const r={self.ROW(txt)}; const a=r&&r.querySelector('.g2alvo'); if(!a) return 'sem linha'; a.click(); return 'ok';}})()"); time.sleep(.45); return r

    def edita(self, txt):
        """alvo da linha → consulta → "Editar …" (quando o registro se edita aqui)"""
        r = self.abre(txt)
        if r == 'ok':
            self.J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/^Editar /.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
        return r

    def rowtxt(self, txt):
        return self.J(f"(()=>{{const r={self.ROW(txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")

    def linhas(self):
        return self.J("[...document.querySelectorAll('[role=table] [role=row][data-rid]')].filter(r=>r.offsetParent).map(r=>r.innerText.replace(/\\s+/g,' '))")

    def cabecalhos(self, i=0):
        return self.J(f"(()=>{{const t=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[{i}]; return t?[...t.querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim()):null;}})()")

    def mestre(self, txt):
        r = self.J(f"(()=>{{const b=[...document.querySelectorAll('.cmd-lista .cmd-it')].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})); if(!b) return 'sem item'; b.click(); return 'ok';}})()"); time.sleep(.5); return r

    def fv(self, k):
        return self.J(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")

    def fset(self, k, val):
        self.J(f"(()=>{{ if(!document.querySelector('aside[role=dialog] [id$=\"_{k}\"]')) return; ({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(val)}); }})()"); time.sleep(.25)

    def btn(self, t):
        r = self.J(f"({BTN})({json.dumps(t)})"); time.sleep(.45); return r

    def clk(self, t):
        r = self.J(f"({CLK})({json.dumps(t)})"); time.sleep(.45); return r

    def labels(self):
        return self.J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")

    def alerts(self):
        return self.J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")

    def toast(self):
        return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")

    def painel(self):
        return self.J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?(a.getAttribute('aria-label')||'')+(document.querySelectorAll('aside[role=dialog] input:not([readonly]),aside[role=dialog] select:not([disabled])').length?' · edição':' · consulta'):'';})()")

    def editando(self):
        return bool(self.J(EDIT))

    def fecha(self):
        """sai da edição (descarta) e fecha o painel"""
        self.J(f"({BTN})('Cancelar')"); time.sleep(.2); self.J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
        self.J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)

    def marca(self, t):
        """caixa de marcar do formulário pelo rótulo"""
        self.J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')); l&&l.querySelector('input').click();}})()"); time.sleep(.2)

    def altura(self):
        return self.J("(()=>{const R=document.querySelector('[data-root]'); if(!R) return null; const h0=R.getBoundingClientRect().height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); R.style.height=''; return [h0,h];})()")


def out(n, v):
    print('·', n, '→', v, flush=True)
