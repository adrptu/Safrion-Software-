# -*- coding: utf-8 -*-
"""CADUX · auxiliar dos testes de navegador dos Cadastros (cadux_cd01_test.py, cadux_tarefas_test.py).
Clica como a pessoa: rola o alvo até o centro, acha o ponto e manda o clique do mouse (1440, ponteiro fino) ou o toque (390, touch);
conta cliques, campos digitados e caracteres com a contagem da linha de base (antes/tarefas.json: o menu conta 1; escolher numa
lista conta 1; digitar conta campo e caracteres, sem clique). Digitar usa Input.insertText (o mesmo evento do teclado virtual).
Uso: n = Nav(Chrome(), porta, toque=False); n.menu('CD-01'); n.clica("[...].find(...)", 'Santa Rita'); n.digita('#mx-q', 'PV07')"""
import time, json

ACHA = r"""(()=>{ const e=(%s); if(!e) return null; e.scrollIntoView({block:'center',inline:'nearest'}); const r=e.getBoundingClientRect();
  if(r.width<1||r.height<1) return {oculto:true}; const x=r.left+r.width/2, y=r.top+r.height/2; const t=document.elementFromPoint(x,y);
  return {x:x,y:y,cobre:!!t&&(t===e||e.contains(t)||t.contains(e)),aviso:!!t&&!!t.closest&&!!t.closest('[role=status]'),t:(t&&(t.innerText||t.getAttribute('aria-label')||t.tagName)||'').slice(0,60)}; })()"""

class Nav:
    def __init__(self, c, porta, toque=False):
        self.c, self.porta, self.toque = c, porta, toque
        self.cliques = 0; self.campos = 0; self.chars = 0; self.passos = []
    def zera(self):
        self.cliques = 0; self.campos = 0; self.chars = 0; self.passos = []
    def url(self, pag, h=''):
        return f'http://127.0.0.1:{self.porta}/{pag}.dc.html{h}'
    def abre(self, pag, h='', espera=.8):
        """abre sem contar (preparação do cenário)"""
        self.c.goto(self.url(pag, h), espera)
    def menu(self, pag, h=''):
        """1 clique: o item do menu (abre a tela como o menu abre)"""
        self.cliques += 1; self.passos.append(f'clique {self.cliques}: menu {pag}'); self.c.goto(self.url(pag, h), .8)
    def js(self, x):
        return self.c.js(x)
    def clica(self, expr, rot='', conta=True, espera=.45):
        """expr: JS que devolve o elemento. Falha (exceção) se não acha ou se outro elemento cobre o ponto."""
        p = self.c.js(ACHA % expr)
        # o aviso de retorno (role=status, some sozinho) pode cobrir o alvo por alguns segundos: a pessoa espera; o teste também (até 8 s)
        for _ in range(16):
            if not p or p.get('cobre') or not p.get('aviso'): break
            time.sleep(.5); p = self.c.js(ACHA % expr)
        if not p or p.get('oculto'): raise AssertionError(f'não achei o alvo para clicar: {rot or expr}')
        if not p['cobre']: raise AssertionError(f'alvo coberto por "{p["t"]}": {rot or expr}')
        x, y = p['x'], p['y']
        if self.toque: self.c.toque(x, y)
        else:
            self.c.mouse(x, y); self.c.mouse(x, y, 'mousePressed', 'left'); self.c.mouse(x, y, 'mouseReleased', 'left')
        if conta: self.cliques += 1; self.passos.append(f'clique {self.cliques}: {rot}')
        time.sleep(espera)
    def digita(self, sel, texto, rot='', espera=.4, foco_conta=False):
        """foca o campo, apaga o que tinha e digita (conta campo e caracteres). Como na linha de base (antes/tarefas.json), tocar no
        campo para digitar não conta clique; foco_conta=True conta."""
        self.clica(f"document.querySelector({json.dumps(sel)})", f'campo {rot or sel}', conta=foco_conta)
        self.c.js(f"(()=>{{ const e=document.querySelector({json.dumps(sel)}); e.focus(); e.select&&e.select(); }})()")
        self.c.call('Input.insertText', {'text': texto}); time.sleep(espera)
        self.campos += 1; self.chars += len(texto); self.passos.append(f'digita {rot or sel}: "{texto}"')
    def escolhe(self, sel, valor, rot=''):
        """select nativo: escolher na lista conta 1 clique, como na linha de base ("clique 3: escolhe Boa Vista em Fazenda")"""
        self.clica(f"document.querySelector({json.dumps(sel)})", f'abre {rot or sel}', conta=False, espera=.1)
        self.c.js(f"(()=>{{ const e=document.querySelector({json.dumps(sel)}); const s=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set; s.call(e,{json.dumps(valor)}); e.dispatchEvent(new Event('change',{{bubbles:true}})); }})()")
        self.cliques += 1; self.passos.append(f'clique {self.cliques}: escolhe {valor}'); time.sleep(.35)
    def tecla(self, k):
        codes = {'Enter': ('Enter', 13), 'Escape': ('Escape', 27), 'ArrowDown': ('ArrowDown', 40), 'ArrowUp': ('ArrowUp', 38), 'Tab': ('Tab', 9), ' ': ('Space', 32)}
        code, vk = codes.get(k, (k, 0))
        self.c.tecla(k, code, vk, text='\r' if k == 'Enter' else (' ' if k == ' ' else None)); time.sleep(.35)
    def volta(self):
        """voltar do navegador (ou do Android)"""
        self.c.js('history.back()'); time.sleep(.7)
    def conta(self):
        return {'cliques': self.cliques, 'campos_digitados': self.campos, 'caracteres': self.chars, 'passos': list(self.passos)}

# seletores comuns da seleção que abre detalhe
def mestre_item(txt):
    return f"[...document.querySelectorAll('.cmd-lista .cmd-it')].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)}))"
def alvo_linha(rid):
    return f"document.querySelector('[data-rid={json.dumps(rid)}] .g2alvo')"
def botao(txt, dentro='document'):
    return f"[...{dentro}.querySelectorAll('button,a')].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)})"
def botao_ini(txt, dentro='document'):
    return f"[...{dentro}.querySelectorAll('button,a')].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)}))"
PAINEL = "document.querySelector('aside[role=dialog]')"
# verdes por contexto (BOT-01): cabeçalho, Próximo passo do detalhe, painel (consulta ou edição)
VERDES = r"""(()=>{ const vis=e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&getComputedStyle(e).visibility!=='hidden'; };
  const v=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'; const n=e=>e.innerText.replace(/\s+/g,' ').trim();
  const em=(sel)=>{ const r=document.querySelector(sel); return r?[...r.querySelectorAll('button,a')].filter(e=>vis(e)&&v(e)&&!e.closest('aside')).map(n):[]; };
  const d=document.querySelector('aside[role=dialog]');
  return {cab:em('header'),det:em('.cmd-dc')+''?em('.cmd-dc'):[],prox:(document.querySelector('.cmd-d .g2prox')?[...document.querySelector('.cmd-d .g2prox').querySelectorAll('button')].filter(e=>vis(e)&&v(e)).map(n):[]),
    painel:d?[...d.querySelectorAll('button,a')].filter(e=>vis(e)&&v(e)).map(n):[],
    secPainel:d?[...d.querySelectorAll('.g2sec>button')].filter(vis).map(n):[]}; })()"""
# BOT-07: comandos dentro das linhas da grade (só o alvo) e linhas fora do Tab
LINHAS = r"""(()=>{ const rs=[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length);
  return rs.map(r=>({id:r.getAttribute('data-rid'),tab:r.getAttribute('tabindex'),cmds:[...r.querySelectorAll('button,a,[role=button]')].filter(e=>e.getClientRects().length&&!e.closest('.g2nr')).map(e=>e.className+':'+(e.getAttribute('aria-label')||e.innerText).slice(0,40))})); })()"""
