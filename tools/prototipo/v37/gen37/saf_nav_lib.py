# -*- coding: utf-8 -*-
"""Ajudantes de navegador do Planejar safra, etapa 2 (tabela de talhões, painel do cultivo, nota e faixa), usados por ocupacao_test.py e
saf_revisao_test.py. Quem importa atribui o navegador: `import saf_nav_lib as L; L.c = Chrome()`. Sobe o servidor do _render ao importar."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
c = None
OK, FAIL, INFO = [], [], []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else ' · ' + str(det)[:1200]), flush=True)
def info(t, v): INFO.append((t, v)); print('     (medido) ' + t + ': ' + str(v)[:600], flush=True)
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')); c = None
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
# linhas da tabela visível como dicionários pelo cabeçalho; Situação = só o texto do chip (o motivo vai no title e no leitor de tela)
ROWS = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return [];
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText).replace(/[⇅▾▴▲▼]/g,'').replace(/\s*·\s*\d+$/,'').trim().toUpperCase());
  return [...t.querySelectorAll('[role=row]')].slice(1).filter(r=>!r.classList.contains('g2tot')).map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; const o={_id:r.getAttribute('data-rid'),_kid:r.classList.contains('g2kid')};
    cs.forEach((c,i)=>{ const h=hs[i]||('C'+i); let x=c.innerText; c.querySelectorAll('.g2sr').forEach(e=>{ x=x.replace(e.innerText,''); }); o[h]=n(x).replace(/^[▾▸] ?/,''); const ch=c.querySelector('[title]'); if(h==='SITUAÇÃO') o._dica=ch?ch.getAttribute('title'):''; });
    return o; }); })()"""
def rows(): return c.js(ROWS) or []
def nivel0(): return [r for r in rows() if not r['_kid']]
def faixa(): return c.js("(document.body.innerText.match(/Nesta safra[^\\n]+/)||[''])[0]") or ''
def chips(): return c.js(f"[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).map(b=>{N}(b.innerText))") or []
def toast(): return c.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def nota(): return c.js(f"(()=>{{const a=document.querySelector('[data-acoes]'); return a?{N}(a.innerText):'';}})()") or ''
def painel(): return c.js(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?{N}(a.innerText):'';}})()") or ''
def erros(): return c.js("(window.__errs||[]).join(' | ')") or ''
def campos(gid):
    return c.js(f"Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>x.offsetParent&&x.id.indexOf('fx_{gid}_')===0).map(x=>[x.id.slice({len('fx_' + gid + '_')}),x.value]))") or {}
def fset(gid, k, val):
    r = c.js(f"""(()=>{{const e=document.getElementById('fx_{gid}_{k}'); if(!e) return 'sem campo {k}'; const pr=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(pr,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.25); return r
def botao(lab, raiz='document'):
    r = c.js(f"""(()=>{{const R={raiz}; const bs=[...R.querySelectorAll('button,a')].filter(b=>b.offsetParent); const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const b=bs.find(b=>n(b.innerText)==={json.dumps(lab)})||bs.find(b=>n(b.innerText).startsWith({json.dumps(lab)})); if(!b) return 'sem botão '+{json.dumps(lab)}; b.click(); return 'ok';}})()"""); time.sleep(.45); return r
def salvar(): return botao('Salvar', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)||document")
def na_linha(t, lab):
    r = c.js(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const rs=[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).flatMap(x=>[...x.querySelectorAll('[role=row]')]);
      const r=rs.find(x=>{{const c=[...x.querySelectorAll('[role=cell]')].find(z=>z.classList.contains('g2c0')); return c&&n(c.innerText).replace(/^[▾▸] ?/,'').split(' ')[0]==={json.dumps(t)};}}); if(!r) return 'sem linha '+{json.dumps(t)};
      const b=[...r.querySelectorAll('button')].find(b=>n(b.innerText)==={json.dumps(lab)}); if(!b) return 'sem botão '+{json.dumps(lab)}+' em '+{json.dumps(t)}; b.click(); return 'ok';}})()"""); time.sleep(.5); return r
def clica_linha(rid):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid="{rid}"]'); if(!r) return 'sem linha'; const cs=[...r.querySelectorAll('[role=cell]')]; const x=cs.find(z=>!z.querySelector('input,button')&&z.innerText.trim()&&!z.classList.contains('g2c0'))||cs[2]; x.click(); return 'ok';}})()"""); time.sleep(.5); return r
def seleciona(rid): return c.js(f"(()=>{{const r=document.querySelector('[role=row][data-rid=\"{rid}\"]'); const i=r&&r.querySelector('input[type=checkbox]'); if(!i) return 'sem caixa'; i.click(); return 'ok';}})()")
NAV = [0]
def abre(h, w=1440, hh=900, toque=False):
    # endereço novo a cada abertura (?r=N): a página recarrega e o estado volta ao inicial (mudar só o # não recarrega)
    NAV[0] += 1; c.aparelho(w, hh, 1, toque); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html?r={NAV[0]}{h}'); time.sleep(1.0)
def estado(gid): return c.js(f"(()=>{{const s=window.__safSelf; const g=s&&s.state.g2&&s.state.g2['{gid}']; return g&&g.rows?JSON.parse(JSON.stringify(g.rows)):null;}})()")
def linha(t, rs=None):
    rs = rs if rs is not None else nivel0()
    return next((r for r in rs if r.get('TALHÃO OU PARCELA', '').split(' ')[0] == t), None)
def sit(t): r = linha(t); return r and r.get('SITUAÇÃO')
# colunas essenciais (COLUNAS-1, 10/10): meta, versão, variedade, ocupa até e fim por saíram da linha e ficam no formulário do cultivo.
# detalhe(t): abre o formulário pela linha cujo 1º texto começa com t (kid=True: só sublinha) e devolve os campos; fecha sem gravar
def detalhe(t, kid=False):
    r = c.js(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const rs=[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).flatMap(x=>[...x.querySelectorAll('[role=row].g2ed')]);
      const r=rs.find(x=>{{const z=x.querySelector('.g2c0'); return z&&n(z.innerText).replace(/^[▾▸] ?/,'').split(' ')[0]==={json.dumps(t)}&&(!{json.dumps(kid)}||x.classList.contains('g2kid'));}}); if(!r) return 'sem linha';
      const z=[...r.querySelectorAll('[role=cell]')].find(z=>z.innerText.trim()&&!z.querySelector('button,input,a')&&!z.classList.contains('g2c0')); (z||r).click(); return 'ok';}})()"""); time.sleep(.5)
    f = c.js("Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>x.offsetParent&&/^fx_g_cult_/.test(x.id)).map(x=>[x.id.replace(/^fx_g_cult_[A-Za-z0-9]+_/,''),x.value]))") or {}
    c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); const b=a&&[...a.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); b&&b.click();})()"); time.sleep(.3)
    f['_r'] = r; return f
FX27SF = 'Nesta safra 553 · Livre 152 · A conferir 380 · Perene 80 · de 1.165 ha · 1 sucessão a conferir'
FX2627 = 'Nesta safra 1.165 · de 1.165 ha · 1 sucessão a conferir'
def nova_safra(nome, ini, fim, faz='Santa Rita'):
    abre('#saf=S2627&passo=safra'); botao('Nova safra'); time.sleep(.3)
    for k, v in (('nome', nome), ('ini', ini), ('fim', fim), ('faz', faz)): fset('g_saf', k, v)
    salvar(); time.sleep(.8)
    r = c.js(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.innerText.indexOf({json.dumps(nome)})>=0); const b=rs.length&&[...rs[rs.length-1].querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem continuar'; b.click(); return 'ok';}})()"""); time.sleep(.8); return r
# safra nova SEM recarregar a página (o estado continua): é o caso de duas safras novas no mesmo estado (R-22)
def etapa1(): return c.js("(()=>{const s=window.__safSelf; s.setState({step:1}); return 'ok';})()")
def cria_safra(nome, ini, fim, faz='Santa Rita'):
    etapa1(); time.sleep(.5); botao('Nova safra'); time.sleep(.3)
    for k, v in (('nome', nome), ('ini', ini), ('fim', fim), ('faz', faz)): fset('g_saf', k, v)
    salvar(); time.sleep(.6); etapa1(); time.sleep(.5)
    c.js(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.innerText.indexOf({json.dumps(nome)})>=0); const b=rs.length&&[...rs[rs.length-1].querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(b) b.click();}})()"""); time.sleep(.8)
    return c.js("window.__safSelf.state.saf")
def vai_safra(sid, passo=2): etapa1(); time.sleep(.4); c.js(f"window.__safSelf.setState({{saf:{json.dumps(sid)},step:{passo}}})"); time.sleep(.9)
def alerta(): return c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?[...a.querySelectorAll('[role=alert]')].map(e=>e.innerText).join(' | '):'(painel fechado)';})()")
def folhas(gid): return [x for r in (estado(gid) or []) for x in [r] + (r.get('kids') or []) if not x.get('grp')]
def links_nota(): return c.js("[...document.querySelectorAll('[data-acoes] [data-acao=atalho]')].filter(b=>b.offsetParent).map(b=>b.innerText.trim())") or []
def clica_link(t): return c.js(f"(()=>{{const b=[...document.querySelectorAll('[data-acoes] [data-acao=atalho]')].filter(b=>b.offsetParent).find(b=>b.innerText.trim()==={json.dumps(t)}); if(!b) return 'sem link'; b.click(); return 'ok';}})()")
