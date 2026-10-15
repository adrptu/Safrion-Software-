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
    cs.forEach((c,i)=>{ const h=hs[i]||('C'+i); let x=c.innerText; c.querySelectorAll('.g2sr').forEach(e=>{ x=x.replace(e.innerText,''); }); o[h]=n(x).replace(/^[▾▸] ?/,''); const ch=c.querySelector('[data-dica]:not([data-dica=""]),[title]'); if(h==='SITUAÇÃO') o._dica=ch?(ch.getAttribute('data-dica')||ch.getAttribute('title')||''):'';   /* DS-DICA (v56): a dica fica em data-dica, não em title */ });
    return o; }); })()"""
def rows(): return c.js(ROWS) or []
def nivel0(): return [r for r in rows() if not r['_kid']]
def faixa(): return c.js("(document.body.innerText.match(/Nesta safra[^\\n]+/)||[''])[0]") or ''
def chips(): return c.js(f"[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).map(b=>{N}(b.innerText))") or []
def toast(): return c.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
# barra limpa (15/10/2026): a nota vira dica do principal (texto para o leitor de tela) e os atalhos ficam no "⋯ Mais ações"; a leitura junta os três
def nota(): return c.js(f"(()=>{{const a=document.querySelector('[data-acoes]'); if(!a) return ''; const m=[...a.querySelectorAll('.acoes-menu [role=menuitem]')].map(b=>b.textContent); return {N}(a.innerText+' '+m.join(' '));}})()") or ''
def painel(): return c.js(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?{N}(a.innerText):'';}})()") or ''
def erros(): return c.js("(window.__errs||[]).join(' | ')") or ''
def campos(gid):
    return c.js(f"Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>x.offsetParent&&x.id.indexOf('fx_{gid}_')===0).map(x=>[x.id.slice({len('fx_' + gid + '_')}),x.value]))") or {}
def fazendas(vals):   # SAF-FAZ-2: o campo Fazendas é de caixas de marcar; marca só as pedidas
    w = [x.strip() for x in str(vals).split(';') if x.strip()]
    r = c.js(f"""(()=>{{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); if(!a) return 'sem painel'; const w={json.dumps(w)}; let n=0;
      [...a.querySelectorAll('label')].forEach(l=>{{const i=l.querySelector('input[type=checkbox]'); if(!i) return; const q=w.indexOf(l.innerText.trim())>=0; if(i.checked!==q){{ i.click(); }} if(q) n++; }}); return n===w.length?'ok':'faltou fazenda';}})()"""); time.sleep(.25); return r
def fset(gid, k, val):
    if gid == 'g_saf' and k == 'fazs': return fazendas(val)
    r = c.js(f"""(()=>{{const e=document.getElementById('fx_{gid}_{k}'); if(!e) return 'sem campo {k}'; const pr=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(pr,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.25); return r
def botao(lab, raiz='document'):
    c.js("document.querySelectorAll('[data-acoes] details.acoes-mais').forEach(d=>{ d.open=true; })")   # atalho no ⋯: a pessoa abre o menu antes
    r = c.js(f"""(()=>{{const R={raiz}; const bs=[...R.querySelectorAll('button,a')].filter(b=>b.offsetParent); const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const mi=[...R.querySelectorAll('.g2mais-menu [role=menuitem]')]; const b=bs.find(b=>n(b.innerText)==={json.dumps(lab)})||bs.find(b=>n(b.innerText).startsWith({json.dumps(lab)}))||mi.find(b=>n(b.textContent)==={json.dumps(lab)}); if(!b) return 'sem botão '+{json.dumps(lab)}; if(b.getAttribute('role')==='menuitem'){{ const w=b.closest('.g2mais-w'); const m=w&&w.querySelector('button.g2mais'); if(m) m.click(); }} b.click(); return 'ok';}})()"""); time.sleep(.45); return r   # 15/10: a ação da linha mora no ⋯ (abre o menu e escolhe, como a pessoa)
def salvar(): return botao('Salvar', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)||document")
def expande_tudo():
    """SAF-TAB (14/10): talhão com um só cultivo abre recolhido; o teste abre tudo, como a pessoa faria, antes de procurar a linha de dentro."""
    r = c.js("(()=>{const b=[...document.querySelectorAll('button.g2xtog')].find(b=>b.offsetParent&&/Expandir tudo/.test(b.innerText)); if(!b) return 'sem'; b.click(); return 'ok';})()"); time.sleep(.4); return r
def na_linha(t, lab, _de_novo=True):
    r = c.js(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const rs=[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).flatMap(x=>[...x.querySelectorAll('[role=row]')]);
      const r=rs.find(x=>{{const c=[...x.querySelectorAll('[role=cell]')].find(z=>z.classList.contains('g2c0')); return c&&n(c.innerText).replace(/^[▾▸] ?/,'').split(' ')[0]==={json.dumps(t)};}}); if(!r) return 'sem linha '+{json.dumps(t)};
      const b=[...r.querySelectorAll('button')].find(b=>n(b.innerText)==={json.dumps(lab)}); if(!b) return 'sem botão '+{json.dumps(lab)}+' em '+{json.dumps(t)}; b.click(); return 'ok';}})()"""); time.sleep(.5)
    if _de_novo and str(r).startswith('sem linha') and expande_tudo() == 'ok': return na_linha(t, lab, False)
    return r
def clica_linha(rid, _de_novo=True):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid="{rid}"]'); if(!r) return 'sem linha'; const cs=[...r.querySelectorAll('[role=cell]')]; const x=cs.find(z=>!z.querySelector('input,button')&&z.innerText.trim()&&!z.classList.contains('g2c0'))||cs[2]; x.click(); return 'ok';}})()"""); time.sleep(.5)
    if _de_novo and r == 'sem linha' and expande_tudo() == 'ok': return clica_linha(rid, False)
    return r
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
FX27SF = 'Nesta safra 553 · Livre 152 · A conferir 380 · Perene 80 · de 1.165 ha · 1 sucessão a conferir'
FX2627 = 'Nesta safra 1.165 · de 1.165 ha · 1 sucessão a conferir'
def nova_safra(nome, ini, fim, faz='Santa Rita'):
    abre('#saf=S2627&passo=safra'); botao('Criar safra'); time.sleep(.3)
    for k, v in (('nome', nome), ('ini', ini), ('fim', fim), ('fazs', faz)): fset('g_saf', k, v)   # SAF-FAZ-2: o campo é Fazendas (uma ou mais)
    salvar(); time.sleep(.8)
    r = c.js(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.innerText.indexOf({json.dumps(nome)})>=0); const b=rs.length&&[...rs[rs.length-1].querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem continuar'; b.click(); return 'ok';}})()"""); time.sleep(.8); return r
# safra nova SEM recarregar a página (o estado continua): é o caso de duas safras novas no mesmo estado (R-22)
def etapa1(): return c.js("(()=>{const s=window.__safSelf; s.setState({step:1}); return 'ok';})()")
def cria_safra(nome, ini, fim, faz='Santa Rita'):
    etapa1(); time.sleep(.5); botao('Criar safra'); time.sleep(.3)
    for k, v in (('nome', nome), ('ini', ini), ('fim', fim), ('fazs', faz)): fset('g_saf', k, v)   # SAF-FAZ-2: o campo é Fazendas (uma ou mais)
    salvar(); time.sleep(.6); etapa1(); time.sleep(.5)
    c.js(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.innerText.indexOf({json.dumps(nome)})>=0); const b=rs.length&&[...rs[rs.length-1].querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(b) b.click();}})()"""); time.sleep(.8)
    return c.js("window.__safSelf.state.saf")
def vai_safra(sid, passo=2): etapa1(); time.sleep(.4); c.js(f"window.__safSelf.setState({{saf:{json.dumps(sid)},step:{passo}}})"); time.sleep(.9)
def alerta(): return c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?[...a.querySelectorAll('[role=alert]')].map(e=>e.innerText).join(' | '):'(painel fechado)';})()")
def folhas(gid): return [x for r in (estado(gid) or []) for x in [r] + (r.get('kids') or []) if not x.get('grp')]
def links_nota(): return c.js("[...document.querySelectorAll('[data-acoes] [data-acao=atalho]')].map(b=>b.textContent.trim())") or []
def clica_link(t): return c.js(f"(()=>{{const b=[...document.querySelectorAll('[data-acoes] [data-acao=atalho]')].find(b=>b.textContent.trim()==={json.dumps(t)}); if(!b) return 'sem link'; const d=b.closest('details'); if(d) d.open=true; b.click(); return 'ok';}})()")   # atalho no ⋯ (15/10)
