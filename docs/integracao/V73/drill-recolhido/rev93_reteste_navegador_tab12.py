# -*- coding: utf-8 -*-
"""Cópia adaptada à TAB-12 (17/10/2026, frente DRILL-RECOLHIDO): abre a faixa da fazenda em abre(); o resto é o original.
EX47 · reteste Claude do PR #93 no HEAD 4cbfa71 (correção A1/A2), no navegador, dados sintéticos. Planejar safra › etapa 2.
R1 S2526 (menu sem dele, nenhuma ação): trilhas = cabeçalhos à vista, todos com nome; a última coluna de dados vai até a borda da tabela
   (Plantio a 1440, Plano agronômico a 390): sem coluna vazia nem coluna fantasma de 0 px.
R2 S2526 com ação injetada no estado (T1 com plano de Milho): a coluna aparece com o cabeçalho "Ações" e o ⋯ "Mais ações de T1" (só Reaplicar);
   buscar "T2" (some a única linha com ação) tira a coluna; buscar "zzz" (nada) mantém cabeçalho e total alinhados; limpar a busca devolve a coluna.
   Teclado: ↓ abre e foca o item, Esc fecha e devolve o foco, Enter no item executa (trava: "Safra encerrada").
R3 S2627 (menu + dele): como antes — ⋯ com Excluir só nos cultivos, cabeçalho "Ações"; buscar e filtro rápido mantêm o alinhamento e o total.
R4 Cartões: S2526 sem espaço de ação; S2526 injetada com 1 ⋯; S2627 com os mesmos ⋯ da Tabela.
Alinhamento (todas as medidas): em cada linha (cabeçalho, linhas, total) a soma dos spans = trilhas, e a borda esquerda de cada célula coincide com a do
cabeçalho da mesma coluna (±1,5 px; a faixa fgrp com span confere a 1ª e a última borda). A 1440 e a 390 (toque). R5 sem erro de JS.
Uso (de gen37, depois do build): python3 -B <este arquivo> · RENDER_DIR escolhe outro _render (contraprova)."""
import os, sys, time, json
GEN = os.environ.get('GEN37') or os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(GEN, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK    ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + json.dumps(det, ensure_ascii=False)[:600], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def espera(cond, lim=8.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
def abre(saf, w):
    c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U(f'SAF.dc.html#saf={saf}&etapa=2'), .6)
    # TAB-12 (17/10/2026): a tabela agrupa por fazenda também com uma só e a faixa nasce recolhida; a pessoa abre a faixa (cópia adaptada
    # do reteste do PR #93: só esta abertura muda; o que se mede é o mesmo)
    espera(f"document.querySelector('[data-g2g=g_cult_{saf}] [role=row].g2fgrp button.g2car')")
    J(f"(()=>{{const b=document.querySelector('[data-g2g=g_cult_{saf}] [role=row].g2fgrp button.g2car[aria-expanded=false]'); if(b) b.click();}})()")
    return espera(f"document.querySelectorAll('[data-g2g=g_cult_{saf}] [role=row]').length>=4")
MEDE = r"""((gid)=>{ const t=document.querySelector('[role=table][data-g2g='+gid+']'); if(!t) return null; const vis=e=>e&&e.getClientRects().length>0;
  const tr=getComputedStyle(t).gridTemplateColumns.split(' ').filter(Boolean); const tb=t.getBoundingClientRect();
  const rows=[...t.querySelectorAll('[role=row]')].filter(r=>r.closest('[role=table]')===t&&vis(r));
  const cel=r=>[...r.querySelectorAll('[role=cell],[role=columnheader]')].filter(x=>x.closest('[role=row]')===r);
  const sp=x=>{ const m=/span (\d+)/.exec(getComputedStyle(x).gridColumnEnd)||/span (\d+)/.exec(getComputedStyle(x).gridColumnStart); return m?+m[1]:1; };
  const hs=cel(rows[0]); const hl=hs.map(h=>h.getBoundingClientRect());
  const cab=hs.map((h,i)=>({t:(h.innerText||'').replace(/[⇅▾▴▲▼]/g,'').replace(/\s+/g,' ').trim(), nome:((h.getAttribute('aria-label')||'')||(h.innerText||'')).replace(/[⇅▾▴▲▼]/g,'').trim(), w:Math.round(hl[i].width*10)/10}));
  const ruins=[]; let nTot=0;
  rows.slice(1).forEach(r=>{ const cs=cel(r); const soma=cs.reduce((a,x)=>a+sp(x),0); const rid=r.getAttribute('data-rid')||(r.classList.contains('g2tot')?'TOTAL':r.className);
    if(r.classList.contains('g2tot')) nTot++;
    if(soma!==tr.length){ ruins.push({rid,soma,tr:tr.length}); return; }
    let k=0; cs.forEach(x=>{ const b=x.getBoundingClientRect(); if(Math.abs(b.left-hl[k].left)>1.5) ruins.push({rid,col:k,l:Math.round(b.left),h:Math.round(hl[k].left)}); k+=sp(x); }); });
  const mais=[...t.querySelectorAll('button.g2mais')].filter(vis).map(b=>{ const r=b.closest('[role=row]'); const br=b.getBoundingClientRect(); const u=hl[hl.length-1];
    return {rid:r.getAttribute('data-rid'), lab:b.getAttribute('aria-label'), its:[...b.parentElement.querySelectorAll('[role=menuitem]')].map(i=>i.textContent.trim()), naUltima:br.left+br.width/2>=u.left-1&&br.left+br.width/2<=u.right+1}; });
  const semNome=cab.filter(h=>!h.nome).length, zero=cab.filter(h=>h.w<1).length;
  return {tracks:tr.length, ncab:hs.length, cab, semNome, zero, borda:Math.round((tb.right-hl[hl.length-1].right)*10)/10, linhas:rows.length-1, nTot, ruins, mais,
          vazioTxt:/Nenhuma linha corresponde/.test((t.closest('.g2rola')||t).parentElement.innerText), lado:document.documentElement.scrollWidth>innerWidth+1}; })"""
def mede(gid): return J(MEDE + "(%s)" % json.dumps(gid))
def alinhado(rot, gid, extra=''):
    m = mede(gid)
    if not m: chk(rot + ' grade à vista', False, gid); return None
    chk(f'{rot} alinhamento: {m["tracks"]} trilhas = {m["ncab"]} cabeçalhos; {m["linhas"]} linhas (total: {m["nTot"]}) com spans e bordas do cabeçalho{extra}',
        m['tracks'] == m['ncab'] and not m['ruins'] and m['nTot'] == 1, {'ruins': m['ruins'][:4], 'tracks': m['tracks'], 'ncab': m['ncab'], 'nTot': m['nTot']})
    return m
def busca(gid, q):
    J(r"""((gid,q)=>{ const t=document.querySelector('[data-g2g='+gid+']'); const sec=t.closest('section')||document; const i=[...sec.querySelectorAll('input[type=search]')].find(x=>x.getClientRects().length)||[...document.querySelectorAll('main input[type=search]')].find(x=>x.getClientRects().length);
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,q); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); })(%s,%s)""" % (json.dumps(gid), json.dumps(q)))
    time.sleep(.6)
def cartoes(gid, rot, n_mais, sem_trilha):
    J("(()=>{const b=document.querySelector('[data-g2md=%s] button[data-modo=cartoes]'); if(b) b.click();})()" % gid)
    espera("!document.querySelector('[role=table][data-g2g=%s]')" % gid); time.sleep(.4)
    r = J(r"""((gid)=>{ const vis=e=>e&&e.getClientRects().length>0; const box=document.querySelector('[data-g2md='+gid+']'); const raiz=box?(box.closest('section')||document):document;
      const mais=[...raiz.querySelectorAll('.g2cd-a button.g2mais')].filter(vis); const esp=[...raiz.querySelectorAll('.g2cd-a')].filter(a=>vis(a)&&a.getBoundingClientRect().width>1);
      const bt=[...raiz.querySelectorAll('button')].filter(b=>vis(b)&&!(b.getAttribute('aria-label')||b.innerText||'').trim()).length;
      return {mais:mais.length, its:mais.map(b=>[...b.parentElement.querySelectorAll('[role=menuitem]')].map(i=>i.textContent.trim())), largAcao:esp.length?Math.round(esp[0].getBoundingClientRect().width):0, bt, lado:document.documentElement.scrollWidth>innerWidth+1}; })(%s)""" % json.dumps(gid))
    chk(f'{rot} Cartões: {r["mais"]} ⋯ = {n_mais} da Tabela; sem botão sem nome; sem rolagem lateral', r['mais'] == n_mais and r['bt'] == 0 and not r['lado'], r)
    if sem_trilha: chk(f'{rot} Cartões sem trilha de ação reservada', r['largAcao'] == 0, r)
    J("(()=>{const b=document.querySelector('[data-g2md=%s] button[data-modo=tabela]'); if(b) b.click();})()" % gid)
    espera("document.querySelector('[role=table][data-g2g=%s]')" % gid); time.sleep(.3)
INJ = r"""(async ()=>{ const s=window.__safSelf; const html=await (await fetch(location.href.split('#')[0])).text();
  const i=html.indexOf('const GRIDS = ')+14, j=html.indexOf(';\nconst NAV = ',i); const sp=JSON.parse(html.slice(i,j)).find(g=>g.id==='g_cult_S2526');
  const st=(s.state.g2||{})['g_cult_S2526']||{}; const rs=JSON.parse(JSON.stringify(st.rows||sp.rows)); const w=l=>{ for(const r of l){ if(r.id==='e1') return r; const k=r.kids&&w(r.kids); if(k) return k; } return null; };
  const e1=w(rs); e1.v.plano='MILHO-SF'; const all=Object.assign({},s.state.g2||{}); all['g_cult_S2526']=Object.assign({},st,{rows:rs}); s.setState({g2:all}); return e1.v.cult; })()"""
ULT = {1440: 'PLANTIO', 390: 'PLANO AGRONÔMICO'}
try:
    for w in (1440, 390):
        W = str(w)
        # ---------- R1 S2526 sem ação ----------
        chk(f'{W} S2526 abre', abre('S2526', w))
        m = alinhado(f'{W} S2526 R1', 'g_cult_S2526')
        if m:
            chk(f'{W} S2526 R1 sem coluna vazia: todos os cabeçalhos com nome, nenhum de 0 px; último = {ULT[w]}; a última coluna vai até a borda da tabela',
                m['semNome'] == 0 and m['zero'] == 0 and m['cab'][-1]['t'] == ULT[w] and abs(m['borda']) <= 2 and not m['mais'] and not m['lado'],
                {'cab': m['cab'], 'borda': m['borda'], 'mais': m['mais'], 'lado': m['lado']})
            print(f'      {W} S2526 R1 larguras: ' + ', '.join(f"{h['t'] or h['nome'] or '∅'} {h['w']}" for h in m['cab']), flush=True)
        cartoes('g_cult_S2526', f'{W} S2526 R4', 0, True)
        # ---------- R2 S2526 com ação injetada ----------
        J(INJ); espera("!!document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais')", 4)
        m = alinhado(f'{W} S2526 R2 com ação', 'g_cult_S2526')
        if m:
            chk(f'{W} S2526 R2 a coluna aparece com o cabeçalho "Ações" e o ⋯ de T1 (só Reaplicar) na última coluna',
                m['cab'][-1]['nome'] == 'Ações' and len(m['mais']) == 1 and m['mais'][0]['its'] == ['Reaplicar'] and m['mais'][0]['lab'] == 'Mais ações de T1' and m['mais'][0]['naUltima'] and m['semNome'] == 0,
                {'ult': m['cab'][-1], 'mais': m['mais']})
            n_com = m['tracks']
        busca('g_cult_S2526', 'T2'); espera("!document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1]')", 4)
        m = alinhado(f'{W} S2526 R2 busca "T2"', 'g_cult_S2526')
        if m: chk(f'{W} S2526 R2 busca "T2" (sem linha com ação): a coluna sai; último cabeçalho {ULT[w]} até a borda', m['cab'][-1]['t'] == ULT[w] and m['semNome'] == 0 and abs(m['borda']) <= 2 and m['tracks'] == n_com - 1, {'cab': m['cab'][-2:], 'borda': m['borda'], 'tracks': m['tracks']})
        busca('g_cult_S2526', 'zzz'); time.sleep(.3)
        m = alinhado(f'{W} S2526 R2 busca "zzz" (nada)', 'g_cult_S2526', '; aviso "Nenhuma linha corresponde"')
        if m: chk(f'{W} S2526 R2 busca sem resultado: cabeçalho e total sem coluna de ações, aviso à vista', m['semNome'] == 0 and m['linhas'] == 1 and m['vazioTxt'], {'cab': m['cab'][-2:], 'linhas': m['linhas'], 'vazio': m['vazioTxt']})
        busca('g_cult_S2526', ''); espera("!!document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais')", 4)
        m = alinhado(f'{W} S2526 R2 busca limpa', 'g_cult_S2526')
        if m: chk(f'{W} S2526 R2 busca limpa: a coluna "Ações" volta com o ⋯ de T1', m['cab'][-1]['nome'] == 'Ações' and len(m['mais']) == 1 and m['tracks'] == n_com, {'ult': m['cab'][-1], 'mais': len(m['mais'])})
        if w == 1440:
            sel = "[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais"
            J("document.querySelector('%s').focus()" % sel); c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.2)
            st = J("(()=>{const b=document.querySelector('%s'); const a=document.activeElement; return {exp:b.getAttribute('aria-expanded'), t:a&&a.textContent.trim()};})()" % sel)
            c.tecla('Escape', 'Escape', 27); time.sleep(.2)
            st2 = J("(()=>{const b=document.querySelector('%s'); return {exp:b.getAttribute('aria-expanded'), foco:document.activeElement===b};})()" % sel)
            c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.2); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5)
            st3 = J("(()=>{const b=document.querySelector('%s'); return {exp:b&&b.getAttribute('aria-expanded'), foco:document.activeElement===b, toast:[...document.querySelectorAll('.g2toast,[role=status]')].map(x=>x.innerText.trim()).filter(Boolean)};})()" % sel)
            chk(f'{W} S2526 R2 teclado: ↓ abre e foca "Reaplicar"; Esc fecha e devolve o foco; Enter executa (trava "Safra encerrada") e devolve o foco',
                st['exp'] == 'true' and st['t'] == 'Reaplicar' and st2['exp'] == 'false' and st2['foco'] and st3['exp'] == 'false' and st3['foco'] and any('Safra encerrada' in t for t in st3['toast']), [st, st2, st3])
        cartoes('g_cult_S2526', f'{W} S2526 R4 com ação', 1, False)
        # ---------- R3 S2627 com exclusão ----------
        chk(f'{W} S2627 abre', abre('S2627', w))
        m = alinhado(f'{W} S2627 R3', 'g_cult_S2627')
        if m:
            cult = set(x['id'] for x in (J("window.__safRef.cultivos('S2627')") or []))
            ruins = [x for x in m['mais'] if ('Excluir' in x['its']) != (x['rid'] in cult) or not x['naUltima']]
            chk(f'{W} S2627 R3 ⋯ ({len(m["mais"])}) na última coluna, Excluir só nos cultivos, cabeçalho "Ações", nenhum cabeçalho sem nome',
                m['mais'] and not ruins and m['cab'][-1]['nome'] == 'Ações' and m['semNome'] == 0, {'ruins': ruins[:4], 'ult': m['cab'][-1]})
            n_mais = len(m['mais'])
        busca('g_cult_S2627', 'T1'); time.sleep(.3)
        m = alinhado(f'{W} S2627 R3 busca "T1"', 'g_cult_S2627')
        if m: chk(f'{W} S2627 R3 busca "T1": a coluna de ações continua (grade com exclusão)', m['cab'][-1]['nome'] == 'Ações' and m['linhas'] >= 2, {'ult': m['cab'][-1], 'linhas': m['linhas']})
        busca('g_cult_S2627', ''); time.sleep(.3)
        qfs = J("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
        alvo = next((q for q in qfs if not q.startswith('Tod')), None)
        if alvo:
            J("(()=>{const b=[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].find(b=>b.offsetParent&&b.innerText.replace(/\\s+/g,' ').trim()===%s); b.click();})()" % json.dumps(alvo)); time.sleep(.6)
            m = alinhado(f'{W} S2627 R3 filtro rápido "{alvo}"', 'g_cult_S2627')
            J("(()=>{const b=[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].find(b=>b.offsetParent&&/^Tod/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.5)
        else: chk(f'{W} S2627 R3 há filtro rápido', False, qfs)
        cartoes('g_cult_S2627', f'{W} S2627 R4', n_mais, False)
        c.shot(os.path.join(os.environ.get('SHOTS', '/tmp'), f'rev93_reteste_S2627_{w}.png'))
    errs = J("window.__errs||[]") or []
    chk('R5 sem erro de JS', not errs, errs[:4])
finally:
    c.close(); srv.terminate()
print(f'\n{ok_n} OK, {len(falhas)} falhas', flush=True)
for f in falhas: print('  FALHA', f)
sys.exit(1 if falhas else 0)
