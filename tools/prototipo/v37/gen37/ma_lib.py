# -*- coding: utf-8 -*-
"""Apoio dos testes da tela única da Manutenção (MA.dc.html, PCM simplificado): Chrome headless (cadc_lib.T), endereço por âncora,
Ver como (localStorage 'safrion.perfilDemo'), painel #ma-painel, grades por data-rid e o estado lido de window.__man (cenário único)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cadc_lib import T, SETV

CLKJS = """((t,root)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root;
 const els=[...r.querySelectorAll('button,a,[role=row]')].filter(e=>e.getClientRects().length&&!e.disabled);
 const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.getAttribute('aria-label'))===t); if(!e) return 'NAO ACHEI: '+t; e.click(); return 'ok';})"""


class MA:
    def __init__(self, w=1440, h=1000):
        self.t = T(); self.J = self.t.J; self.c = self.t.c; self.FALHAS = []; self.n = 0
        self.c.size(w, h)

    # ---------- navegação ----------
    def ir(self, ancora='', perfil=None, limpa=False, pagina='MA.dc.html'):
        """abre a página com a âncora; limpa o localStorage e/ou fixa o Ver como antes de carregar (espera o documento novo)"""
        if limpa or perfil:
            self.t.goto(pagina)
            if limpa: self.J("localStorage.clear()")
            if perfil: self.J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
        # documento novo sempre (só a âncora mudando não recarrega): passa por about:blank; o localStorage da origem fica
        self.c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.15)
        self.c.call('Page.navigate', {'url': f'http://127.0.0.1:{self.t.p}/{pagina}' + (('#' + ancora) if ancora else '')})
        for _ in range(60):
            time.sleep(.1)
            try:
                if self.J("location.protocol==='http:' && document.readyState==='complete' && document.body && document.body.innerText.length>50"): break
            except Exception: pass
        time.sleep(.6)

    def recarregar(self):
        self.J("window.__velho=1; location.reload()")
        for _ in range(40):
            time.sleep(.1)
            try:
                if self.J("!window.__velho && document.readyState==='complete' && document.body.innerText.length>50"): break
            except Exception: pass
        time.sleep(.6)

    # ---------- leitura ----------
    def body(self): return self.J("document.body.innerText") or ''
    def pan(self): return self.J("(document.querySelector('#ma-painel')||{}).innerText||''") or ''
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].filter(x=>!x.classList.contains('ma-sr')).map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def hdr(self): return self.J("(document.querySelector('header')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    def man(self, expr): return self.J(f"(()=>{{const m=window.__man.manGet(); return ({expr});}})()")
    def errs(self): return self.t.errs()
    def hash(self): return self.J("location.hash")
    def linha(self, rid): return self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.getClientRects().length); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
    def linhas(self, i=0): return self.J(f"(()=>{{const t=[...document.querySelectorAll('[role=table]')].filter(t=>t.getClientRects().length)[{i}]; return t?[...t.querySelectorAll('[role=row][data-rid]')].map(r=>r.getAttribute('data-rid')):[];}})()") or []
    def prims(self):
        """botões primários visíveis (fundo verde cheio), com o texto"""
        return self.J("[...document.querySelectorAll('button,a')].filter(b=>b.getClientRects().length&&/background: rgb\\(30, 122, 76\\)|background:#1E7A4C|background: #1E7A4C/i.test(b.getAttribute('style')||'')||(getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.getClientRects().length)).map(b=>b.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)") or []
    def largura(self): return self.J("document.documentElement.scrollWidth-document.documentElement.clientWidth")

    # ---------- ação ----------
    def clk(self, txt, root='', w=.45):
        r = self.J(f"({CLKJS})({json.dumps(txt)},{json.dumps(root)})"); time.sleep(w); return r
    def abre(self, rid, w=.5):
        r = self.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.getClientRects().length); if(!r) return false; ((r.querySelector('.g2pw'))||r).click(); return true;}})()"); time.sleep(w); return r
    def setv(self, sel, val):
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
    def responder(self, resp='Feito'):
        """responde, uma a uma, as tarefas do painel ainda sem resposta (PRD 54.2: nada vem marcado); devolve quantas"""
        n = 0
        for _ in range(30):
            r = self.J(f"(()=>{{const g=[...document.querySelectorAll('#ma-painel [role=group]')].find(g=>{{const bs=[...g.querySelectorAll('button')]; return bs.some(b=>b.innerText.trim()==={json.dumps(resp)}&&!b.disabled)&&!bs.some(b=>b.getAttribute('aria-pressed')==='true');}}); if(!g) return false; [...g.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(resp)}).click(); return true;}})()")
            time.sleep(.3)
            if not r: break
            n += 1
        return n
    def bloco(self, titulo):
        """abre o bloco recolhível do painel/detalhe pelo título (se fechado)"""
        return self.J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-expanded]')].find(b=>b.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(titulo)})>=0&&b.getClientRects().length); if(!b) return 'NAO ACHEI'; if(b.getAttribute('aria-expanded')!=='true') b.click(); return 'ok';}})()")
    def tecla(self, k, code, vk, shift=False):
        m = 8 if shift else 0
        for tp in ('keyDown', 'keyUp'): self.c.call('Input.dispatchKeyEvent', {'type': tp, 'key': k, 'code': code, 'windowsVirtualKeyCode': vk, 'modifiers': m})
        time.sleep(.05)

    # ---------- registro ----------
    def ok(self, cond, msg, extra=''):
        self.n += 1
        print(('  ok  ' if cond else '  FALHA ') + msg + ('' if cond else ' · ' + str(extra)[:300]), flush=True)
        if not cond: self.FALHAS.append(msg)
    def sem_erro(self, onde):
        e = self.errs(); self.ok(not e, f'{onde}: sem erro de JS', e[:200])
    def fim(self):
        try: self.c.close()
        finally: self.t.srv.terminate()
        print(f'RESULTADO: {self.n - len(self.FALHAS)}/{self.n} ok' + (' · FALHAS: ' + '; '.join(self.FALHAS) if self.FALHAS else ''))
        return 1 if self.FALHAS else 0
