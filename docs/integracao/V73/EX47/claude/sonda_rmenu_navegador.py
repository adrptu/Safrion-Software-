# -*- coding: utf-8 -*-
"""EX47 · revisão Claude do PR #93: sonda de navegador da grade com menu_linha (⋯) com e sem exclusão, dados sintéticos.
Grades reais do Planejar safra, etapa 2: g_cult_S2627 (menu_linha + dele) e g_cult_S2526 (safra encerrada: menu_linha sem dele).
N1 alinhamento: em cada linha à vista (cabeçalho, linhas, total) a soma dos spans das células = trilhas da grade; o ⋯ cai na última coluna.
N2 Excluir só onde é permitido (linha sem ro/livre/fora/nosel e grade com dele); nunca na grade sem dele.
N3 nenhum controle vazio: todo botão à vista na grade tem nome; todo ⋯ tem item; rótulo "Mais ações de <linha>".
N4 grade sem dele com ação na linha (contraexemplo injetado no estado: plano incompatível em T1 da safra encerrada): ⋯ com "Reaplicar" e sem
   Excluir; teclado: ↓ abre e foca o 1º item, Esc fecha e devolve o foco ao ⋯, Enter no item executa e devolve o foco; cf obsoleto não pergunta.
N5 confirmação na grade com dele: Excluir no ⋯ → "Excluir?" na linha; Manter volta ao ⋯ (nada é excluído).
N6 Cartões: o ⋯ de cada linha da Tabela está no cartão; nenhum espaço de ação vazio.
N7 a 390 (toque): N1, N3, ⋯ alcançável, sem rolagem lateral da página; Cartões idem.
N8 sem erro de JS.
Uso (de tools/prototipo/v37/gen37, depois de build.py e montar_render.py): python3 -B <este arquivo>"""
import os, sys, time, json
GEN = os.environ.get('GEN37') or os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(GEN, '_render')
SHOTS = os.environ.get('SHOTS') or os.path.dirname(os.path.abspath(__file__))
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK    ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + json.dumps(det, ensure_ascii=False)[:700], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def espera(cond, lim=10.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
def abre(saf, w):
    c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U(f'SAF.dc.html#saf={saf}&etapa=2'), .6)
    return espera(f"document.querySelectorAll('[data-g2g=g_cult_{saf}] [role=row]').length>=4")
# medida da grade em Tabela
MEDE = r"""((gid)=>{ const t=document.querySelector('[role=table][data-g2g='+gid+']'); if(!t) return null;
  const vis=e=>e&&e.getClientRects().length>0;
  const tracks=getComputedStyle(t).gridTemplateColumns.split(' ').filter(Boolean).length;
  const rows=[...t.querySelectorAll('[role=row]')].filter(r=>r.closest('[role=table]')===t&&vis(r));
  const hd=rows[0]; const hcs=[...hd.querySelectorAll('[role=columnheader]')].filter(x=>x.closest('[role=row]')===hd);
  const lastH=hcs[hcs.length-1].getBoundingClientRect();
  const out={tracks, n:rows.length, ruins:[], fora:[], mais:[], vazios:[], semItem:[]};
  rows.forEach(r=>{ const cs=[...r.querySelectorAll('[role=cell],[role=columnheader]')].filter(x=>x.closest('[role=row]')===r);
    const soma=cs.reduce((a,x)=>{ const m=/span (\d+)/.exec(getComputedStyle(x).gridColumnEnd)||/span (\d+)/.exec(getComputedStyle(x).gridColumnStart); return a+(m?+m[1]:1); },0);
    if(soma!==tracks) out.ruins.push({rid:r.getAttribute('data-rid')||r.className||'cab', soma, cells:cs.length});
    const b=r.querySelector('button.g2mais'); if(b){ const br=b.getBoundingClientRect(), cx=br.left+br.width/2;
      if(!(cx>=lastH.left-1&&cx<=lastH.right+1)) out.fora.push({rid:r.getAttribute('data-rid'),cx,l:lastH.left,r:lastH.right});
      const its=[...b.parentElement.querySelectorAll('.g2mais-menu [role=menuitem]')].map(i=>i.textContent.trim());
      out.mais.push({rid:r.getAttribute('data-rid'), lab:b.getAttribute('aria-label'), menu:(b.parentElement.querySelector('[role=menu]')||{}).getAttribute?.('aria-label'), its});
      if(!its.length) out.semItem.push(r.getAttribute('data-rid')); } });
  [...t.querySelectorAll('button')].filter(vis).forEach(b=>{ const nm=(b.getAttribute('aria-label')||b.innerText||'').trim(); if(!nm) out.vazios.push(b.outerHTML.slice(0,120)); });
  out.lixeira=[...t.querySelectorAll('button.g2del')].filter(vis).length;
  out.excluirTxt=/Excluir\?/.test(t.innerText);
  return out; })"""
# cultivos (registros que se excluem) pela API de teste da tela; as demais linhas da grade (talhão, grupo, ocupação de fora, fazenda) são de exibição
FLAGS = r"""((saf)=>{ const out={}; (window.__safRef.cultivos(saf)||[]).forEach(c=>{ out[c.id]={cultivo:true}; }); return out; })"""
def mede(gid): return J(MEDE + "(%s)" % json.dumps(gid))
def flags(gid): return J(FLAGS + "(%s)" % json.dumps(gid.split('_')[-1])) or {}
def tabela(gid, rot, com_del):
    m = mede(gid)
    if not m: chk(rot + ' grade à vista', False, gid); return None
    chk(f'{rot} N1 alinhamento: {m["n"]} linhas, {m["tracks"]} trilhas, soma dos spans = trilhas em todas', not m['ruins'], m['ruins'][:5])
    chk(f'{rot} N1 o ⋯ ({len(m["mais"])}) cai na última coluna', not m['fora'], m['fora'][:4])
    fl = flags(gid); ruins = []
    for x in m['mais']:
        f = fl.get(x['rid'], {})   # S2627: cultivos sem ro (dados2); S2526: safra encerrada, cultivos ro
        if ('Excluir' in x['its']) != (com_del and bool(f.get('cultivo'))): ruins.append([x['rid'], f, x['its']])
    chk(f'{rot} N2 Excluir só onde é permitido (dele={com_del})', not ruins, ruins[:5])
    chk(f'{rot} N2 sem lixeira solta numa grade com ⋯', m['lixeira'] == 0, m['lixeira'])
    lab = [x for x in m['mais'] if not (x['lab'] or '').startswith('Mais ações de ') or len(x['lab']) <= len('Mais ações de ') or x['menu'] != x['lab']]
    chk(f'{rot} N3 nenhum controle vazio; ⋯ com item e rótulo "Mais ações de <linha>"', not m['vazios'] and not m['semItem'] and not lab, [m['vazios'][:2], m['semItem'][:3], lab[:2]])
    return m
def cartoes(gid, rot, n_mais):
    J("(()=>{const b=document.querySelector('[data-g2md=%s] button[data-modo=cartoes]'); if(b) b.click();})()" % gid)
    espera("!document.querySelector('[role=table][data-g2g=%s]') && document.querySelectorAll('[data-rid]').length>0" % gid)
    time.sleep(.3)
    r = J(r"""(()=>{ const vis=e=>e&&e.getClientRects().length>0; const as=[...document.querySelectorAll('.g2cd-a')].filter(a=>a.closest('[data-rid]')&&a.closest('main'));
      const box=[...document.querySelectorAll('[data-g2md=%s]')][0]; const raiz=box?box.closest('section')||document:document;
      const mais=[...raiz.querySelectorAll('.g2cd-a button.g2mais')].filter(vis); const esp=[...raiz.querySelectorAll('.g2cd-a')].filter(a=>vis(a)&&!a.querySelector('button')&&a.getBoundingClientRect().width>1);
      const vaz=[...raiz.querySelectorAll('.g2cd-a')].filter(a=>vis(a)&&(a.querySelector('[tabindex],a,input,select')||a.getAttribute('role')||a.getAttribute('aria-label')||a.querySelector('.g2mais')&&!a.querySelector('[role=menuitem]')));
      const bt=[...raiz.querySelectorAll('button')].filter(b=>vis(b)&&!(b.getAttribute('aria-label')||b.innerText||'').trim()).map(b=>b.outerHTML.slice(0,100));
      return {mais:mais.length, its:mais.map(b=>[...b.parentElement.querySelectorAll('[role=menuitem]')].map(i=>i.textContent.trim())), vaz:vaz.length, espacador:esp.length, bt, lado:document.documentElement.scrollWidth>innerWidth+1}; })()""" % gid)
    chk(f'{rot} N6 Cartões: {r["mais"]} ⋯ no cartão = {n_mais} da Tabela', r['mais'] == n_mais, r)
    chk(f'{rot} N6 Cartões sem controle vazio (o espaçador da trilha de ações, sem papel nem foco, é estrutural: {r["espacador"]})', r['vaz'] == 0 and not r['bt'], r)
    J("(()=>{const b=document.querySelector('[data-g2md=%s] button[data-modo=tabela]'); if(b) b.click();})()" % gid)
    espera("document.querySelector('[role=table][data-g2g=%s]')" % gid)
    return r
# contraexemplo injetado no estado (sem tocar no produto): T1 (e1, Soja) da safra encerrada com plano de Milho → leafParts põe "Reaplicar" na linha
INJ = r"""(async ()=>{ const s=window.__safSelf; const html=await (await fetch(location.href.split('#')[0])).text();
  const i=html.indexOf('const GRIDS = ')+14, j=html.indexOf(';\nconst NAV = ',i); const sp=JSON.parse(html.slice(i,j)).find(g=>g.id==='g_cult_S2526');
  const st=(s.state.g2||{})['g_cult_S2526']||{}; const rs=JSON.parse(JSON.stringify(st.rows||sp.rows)); const w=l=>{ for(const r of l){ if(r.id==='e1') return r; const k=r.kids&&w(r.kids); if(k) return k; } return null; };
  const e1=w(rs); e1.v.plano='MILHO-SF'; const all=Object.assign({},s.state.g2||{}); all['g_cult_S2526']=Object.assign({},st,{rows:rs}); s.setState({g2:all}); return e1.v.cult; })()"""
CF = r"""(()=>{ const s=window.__safSelf; const all=Object.assign({},s.state.g2||{}); all['g_cult_S2526']=Object.assign({},all['g_cult_S2526']||{},{cf:'e1'}); s.setState({g2:all}); })()"""
try:
    for w in (1440, 390):
        W = f'{w}'
        chk(f'{W} S2627 abre', abre('S2627', w))
        m = tabela('g_cult_S2627', f'{W} S2627 (menu+del)', True)
        if m:
            print(f'      {W} S2627: ⋯ em', [(x['rid'], x['its']) for x in m['mais']][:12], flush=True)
            if w == 390:
                al = J(r"""(()=>{ const b=[...document.querySelectorAll('[data-g2g=g_cult_S2627] button.g2mais')].filter(x=>x.getClientRects().length)[0]; if(!b) return 'sem ⋯';
                  b.scrollIntoView({block:'center',inline:'nearest'}); const r=b.getBoundingClientRect(); const t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return {ok:!!t&&(t===b||b.contains(t)), lado:document.documentElement.scrollWidth>innerWidth+1, w:r.width, h:r.height}; })()""")
                chk(f'{W} S2627 N7 ⋯ alcançável, sem rolagem lateral da página', isinstance(al, dict) and al['ok'] and not al['lado'], al)
                print(f'OBS   {W} S2627 N7b tamanho do ⋯ no toque: {al.get("w")}×{al.get("h")} px (DS: 44 px; anterior ao PR)', flush=True)
            c.shot(os.path.join(SHOTS, f'rev93_S2627_tabela_{w}.png'))
            if w == 1440:
                # N5 confirmação: Excluir no ⋯ do 1º cultivo com Excluir → "Excluir?"; Manter volta
                alvo = next((x['rid'] for x in m['mais'] if 'Excluir' in x['its']), None)
                if alvo:
                    J("(()=>{const r=document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"]'); const b=r.querySelector('button.g2mais'); b.click(); const it=[...r.querySelectorAll('[role=menuitem]')].find(i=>i.textContent.trim()==='Excluir'); it.click();})()" % alvo)
                    espera("/Excluir\\?/.test(document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"]').innerText)" % alvo, 4)
                    q = J("(()=>{const r=document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"]'); return {txt:r.innerText.replace(/\\s+/g,' ').slice(-40), mais:!!r.querySelector('button.g2mais')};})()" % alvo)
                    chk(f'{W} S2627 N5 Excluir no ⋯ pergunta "Excluir?" na linha {alvo}', 'Excluir?' in q['txt'] and 'Manter' in q['txt'] and not q['mais'], q)
                    m2 = mede('g_cult_S2627'); chk(f'{W} S2627 N5 alinhamento com a pergunta aberta', m2 and not m2['ruins'], m2 and m2['ruins'][:3])
                    J("(()=>{const r=document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"]'); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Manter').click();})()" % alvo)
                    espera("!!document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"] button.g2mais')" % alvo, 4)
                    q2 = J("(()=>{const r=document.querySelector('[data-g2g=g_cult_S2627] [role=row][data-rid=\"%s\"]'); return {mais:!!(r&&r.querySelector('button.g2mais')), existe:!!r};})()" % alvo)
                    chk(f'{W} S2627 N5 Manter volta ao ⋯ e a linha continua', q2['mais'] and q2['existe'], q2)
                else: chk(f'{W} S2627 N5 há cultivo com Excluir', False, m['mais'][:3])
            cartoes('g_cult_S2627', f'{W} S2627', len(m['mais']))
        # safra encerrada: menu_linha sem dele
        chk(f'{W} S2526 abre', abre('S2526', w))
        m = tabela('g_cult_S2526', f'{W} S2526 (menu sem del)', False)
        if m:
            chk(f'{W} S2526 sem ação na linha nos dados sintéticos: nenhum ⋯ e nenhum "Excluir"', len(m['mais']) == 0 and not m['excluirTxt'], m['mais'][:3])
            cartoes('g_cult_S2526', f'{W} S2526', 0)
            cu = J(INJ); espera("!!document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais')", 4)
            m = tabela('g_cult_S2526', f'{W} S2526 + ação injetada (T1 {cu} com plano de Milho)', False)
            if m:
                e1 = [x for x in m['mais'] if x['rid'] == 'e1']
                chk(f'{W} S2526 N4 ⋯ de T1 só com "Reaplicar" (sem Excluir), rótulo "Mais ações de T1"', len(m['mais']) == 1 and e1 and e1[0]['its'] == ['Reaplicar'] and e1[0]['lab'] == 'Mais ações de T1', m['mais'])
                c.shot(os.path.join(SHOTS, f'rev93_S2526_injetado_tabela_{w}.png'))
                if w == 1440:
                    sel = "[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais"
                    J("document.querySelector('%s').focus()" % sel)
                    c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.2)
                    st = J("(()=>{const b=document.querySelector('%s'); const a=document.activeElement; return {exp:b.getAttribute('aria-expanded'), foco:a&&a.getAttribute('role'), t:a&&a.textContent.trim()};})()" % sel)
                    chk(f'{W} S2526 N4 ↓ no ⋯ abre o menu e foca "Reaplicar"', st['exp'] == 'true' and st['foco'] == 'menuitem' and st['t'] == 'Reaplicar', st)
                    c.tecla('Escape', 'Escape', 27); time.sleep(.2)
                    st = J("(()=>{const b=document.querySelector('%s'); return {exp:b.getAttribute('aria-expanded'), foco:document.activeElement===b};})()" % sel)
                    chk(f'{W} S2526 N4 Esc fecha e devolve o foco ao ⋯', st['exp'] == 'false' and st['foco'], st)
                    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.25)
                    st = J("(()=>{const b=document.querySelector('%s'); const a=document.activeElement; return {exp:b.getAttribute('aria-expanded'), t:a&&a.textContent.trim()};})()" % sel)
                    chk(f'{W} S2526 N4 Enter no ⋯ abre e foca o item', st['exp'] == 'true' and st['t'] == 'Reaplicar', st)
                    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5)
                    st = J("(()=>{const b=document.querySelector('%s'); const tt=[...document.querySelectorAll('.g2toast,[role=status]')].map(x=>x.innerText.trim()).filter(Boolean); return {exp:b&&b.getAttribute('aria-expanded'), foco:document.activeElement===b, toast:tt};})()" % sel)
                    chk(f'{W} S2526 N4 Enter no item executa (trava de domínio: "Safra encerrada: somente consulta."), fecha e devolve o foco', st['exp'] == 'false' and st['foco'] and any('Safra encerrada' in t for t in st['toast']), st)
                    J(CF); time.sleep(.3)
                    m3 = mede('g_cult_S2526')
                    chk(f'{W} S2526 N4 cf obsoleto (cf=e1) não pergunta "Excluir?" na grade sem exclusão', m3 and not m3['excluirTxt'] and len(m3['mais']) == 1, m3 and m3['mais'])
                if w == 390:
                    al = J(r"""(()=>{ const b=document.querySelector('[data-g2g=g_cult_S2526] [role=row][data-rid=e1] button.g2mais'); b.scrollIntoView({block:'center',inline:'nearest'}); const r=b.getBoundingClientRect(); const t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return {ok:!!t&&(t===b||b.contains(t)), lado:document.documentElement.scrollWidth>innerWidth+1, w:r.width, h:r.height}; })()""")
                    chk(f'{W} S2526 N7 ⋯ alcançável, sem rolagem lateral da página', al['ok'] and not al['lado'], al)
                    print(f'OBS   {W} S2526 N7b tamanho do ⋯ no toque: {al.get("w")}×{al.get("h")} px (DS: 44 px; anterior ao PR)', flush=True)
                cartoes('g_cult_S2526', f'{W} S2526 + ação injetada', 1)
                c.shot(os.path.join(SHOTS, f'rev93_S2526_injetado_{w}_fim.png'))
    errs = J("window.__errs||[]") or []
    chk('N8 sem erro de JS', not errs, errs[:4])
finally:
    c.close(); srv.terminate()
print(f'\n{ok_n} OK, {len(falhas)} falhas', flush=True)
for f in falhas: print('  FALHA', f)
sys.exit(1 if falhas else 0)
