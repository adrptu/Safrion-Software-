# -*- coding: utf-8 -*-
"""EX-41 · reprodução dirigida (2 a 3 telas por sub-item) no render G/_render (62f2c35, dados sintéticos), 1440 × 900:
F  formulários: rótulo, obrigatório/opcional, ajuda, unidade, teclado decimal, "Mais opções", verbo da primária (CD-04, PL-01, VE-04, VEN, SAF, EST)
L  lote: Aprovações (IN-02) com decisão que exige revisão individual na seleção
V  vazio e sem resultado: busca sem resultado em CD-04, OS e EST
A  aviso temporário: o componente comum aceita botão (Desfazer)? (IN-04 e Planos)
D  componente por tarefa: as duas "Nova safra" (PL-01 × SAF) e as duas vendas (VE-04 × VEN), com os campos de cada uma
Só leitura (o estado de demonstração é limpo a cada tela). Saídas: out/p5_ex41_alvos.log/.json, png/ex41_*.png."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, PNG, G
R_DIR = os.path.join(G, '_render')
L = open(os.path.join(OUT, 'p5_ex41_alvos.log'), 'w', encoding='utf-8'); R = {}
port = server(R_DIR); c = chrome(); J = c.js; c.aparelho(1440, 900)
U = lambda pg: f'http://127.0.0.1:{port}/{pg}'
def abre(pg, esp=1.0):
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U(pg), esp)
def clica(txt, exato=True, raiz='document'):
    r = J(f"""(()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const vis=e=>e.getClientRects().length>0;
      const b=[...{raiz}.querySelectorAll('button,a,[role=button],[role=menuitem]')].filter(vis).find(b=>{'(n(b.innerText)===' if exato else 'n(b.innerText).startsWith('}{json.dumps(txt)})||(b.getAttribute('aria-label')||'')==={json.dumps(txt)});
      if(!b) return false; b.click(); return n(b.innerText)||b.getAttribute('aria-label');}})()"""); time.sleep(.8); return r
FORM = r"""JSON.stringify((()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&getComputedStyle(e).visibility!=='hidden';};
 const ps=[...document.querySelectorAll('[role=dialog],aside')].filter(vis); const P=ps[ps.length-1]||document.querySelector('main');
 const ctl=[...P.querySelectorAll('input,select,textarea')].filter(vis).filter(i=>!['hidden','checkbox','radio','search'].includes(i.type));
 const rot=i=>{ if(i.id){ const l=document.querySelector('label[for="'+i.id+'"]'); if(l&&vis(l)) return n(l.innerText); } const w=i.closest('label'); if(w) return n(w.innerText);
   if(i.getAttribute('aria-labelledby')){ return n(i.getAttribute('aria-labelledby').split(' ').map(id=>(document.getElementById(id)||{textContent:''}).textContent).join(' ')); } return '';};
 const campos=ctl.map(i=>{ const box=i.parentElement; const suf=[...box.querySelectorAll('span')].filter(s=>vis(s)&&s!==i&&!s.contains(i)&&/^(ha|kg|L|t|%|sc|R\$|mL|g|m|km\/h|L\/ha|kg\/ha|h|dias?)\b/.test(n(s.innerText))).map(s=>n(s.innerText));
   return {rot:rot(i),aria:i.getAttribute('aria-label')||'',tipo:i.tagName.toLowerCase()+(i.type?':'+i.type:''),im:i.getAttribute('inputmode')||i.inputMode||'',req:i.getAttribute('aria-required')||(i.required?'required':''),suf}; });
 const txt=n(P.innerText);
 const bts=[...P.querySelectorAll('button')].filter(vis).map(b=>[n(b.innerText)||b.getAttribute('aria-label'),getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)']);
 return {titulo:n((P.querySelector('h2,h3')||{innerText:''}).innerText),papel:P.getAttribute('role')||P.tagName,largura:Math.round(P.getBoundingClientRect().width),campos,
   n:campos.length,sem_rotulo:campos.filter(f=>!f.rot&&!f.aria).length,com_rotulo_visivel:campos.filter(f=>f.rot).length,aria_required:campos.filter(f=>f.req).length,
   opcional:(txt.match(/\(opcional\)/g)||[]).length,asterisco:campos.filter(f=>/\*\s*$/.test(f.rot)).length,decimal:campos.filter(f=>f.im==='decimal'||f.im==='numeric').length,
   sufixo:campos.filter(f=>f.suf.length).length,mais_opcoes:/Mais opções/.test(txt),botoes:bts};})())"""
def form(nome, pg, passos, shot=None):
    abre(pg); ok = []
    for p in passos: ok.append(clica(p, exato=False))
    time.sleep(.4)
    try: x = json.loads(J(FORM))
    except Exception as e: x = {'falha': str(e)[:200]}
    x['passos'] = ok; R['F_' + nome] = x
    if shot: c.shot(os.path.join(PNG, shot))
    log(L, f'F {nome}', json.dumps({k: v for k, v in x.items() if k != 'campos'}, ensure_ascii=False)); log(L, '   campos', json.dumps(x.get('campos', [])[:14], ensure_ascii=False))

# ---------- F · formulários ----------
form('CD-04 Criar pessoa', 'CD-04.dc.html', ['Criar pessoa'], 'ex41_1440_form_cd04.png')
form('PL-01 Nova safra', 'PL-01.dc.html', ['+ Criar safra'], 'ex41_1440_form_pl01_nova_safra.png')
form('SAF Criar safra', 'SAF.dc.html', ['Criar safra'], 'ex41_1440_form_saf_criar_safra.png')
form('VE-04 Novo pedido', 'VE-04.dc.html', ['+ Criar pedido'], 'ex41_1440_form_ve04.png')
form('VEN Registrar venda', 'VEN.dc.html', ['Registrar venda'], 'ex41_1440_form_ven.png')
form('EST Registrar recebimento', 'EST.dc.html', ['Registrar recebimento'], 'ex41_1440_form_est.png')
form('CMP Registrar recebimento', 'CMP.dc.html', ['Registrar recebimento'], 'ex41_1440_form_cmp.png')
form('OS Criar ordem', 'OS.dc.html', ['Criar ordem'], 'ex41_1440_form_os.png')

# ---------- L · ação em lote (IN-02) ----------
abre('IN-02.dc.html')
L0 = json.loads(J(r"""JSON.stringify((()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const rows=[...document.querySelectorAll('[role=row]')].filter(r=>r.querySelector('input[type=checkbox],[role=checkbox]'));
 return rows.map(r=>{const c=r.querySelector('input[type=checkbox],[role=checkbox]'); return [n(r.innerText).slice(0,60), !(c.disabled||c.getAttribute('aria-disabled')==='true')];});})())"""))
R['L_linhas'] = L0
sel = J(r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const rows=[...document.querySelectorAll('[role=row]')].filter(r=>r.querySelector('input[type=checkbox],[role=checkbox]'));
 const alvo=rows.filter(r=>/Orçamento revisado|Política de estoque/.test(r.innerText)); alvo.forEach(r=>r.querySelector('input[type=checkbox],[role=checkbox]').click()); return alvo.map(r=>n(r.innerText).slice(0,40));})()"""); time.sleep(.6)
R['L_barra'] = J(r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); return [...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&/selecionad/i.test(b.innerText)).map(b=>n(b.innerText)+' | desabilitado='+(b.disabled||b.getAttribute('aria-disabled')==='true'));})()""")
R['L_texto_barra'] = J(r"""(()=>{const m=document.body.innerText.match(/\d+ selecionad[ao]s?[^\n]{0,80}/); return m?m[0]:'';})()""")
c.shot(os.path.join(PNG, 'ex41_1440_in02_lote.png'))
clica('Aprovar selecionados'); time.sleep(.3)
R['L_resultado'] = J("(document.querySelector('.g2toast')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()")
log(L, 'L IN-02', json.dumps({k: R[k] for k in ('L_linhas', 'L_barra', 'L_texto_barra', 'L_resultado')}, ensure_ascii=False), 'selecionadas', sel)

# ---------- V · busca sem resultado ----------
for pg in ['CD-04.dc.html', 'OS.dc.html', 'EST.dc.html']:
    abre(pg)
    J("""(()=>{const i=[...document.querySelectorAll('input')].find(i=>i.getClientRects().length&&/Buscar/.test((i.placeholder||'')+(i.getAttribute('aria-label')||''))); if(!i) return false;
      const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(i,'zzzz'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return true;})()"""); time.sleep(.8)
    R['V_' + pg] = json.loads(J(r"""JSON.stringify((()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const m=document.querySelector('main')||document.body;
      const t=[...m.querySelectorAll('div,p,span,td')].filter(e=>e.getClientRects().length&&e.children.length<=2&&/^(Nenhum|Nenhuma|Nada|Sem resultado|Sem itens)/.test(n(e.innerText))).map(e=>n(e.innerText)).slice(0,3);
      const near=[...m.querySelectorAll('button,a')].filter(b=>b.getClientRects().length&&/Limpar|Criar|Cadastrar|Registrar/.test(n(b.innerText))).map(b=>n(b.innerText));
      return {msg:t, acoes:near};})())"""))
    log(L, 'V', pg, R['V_' + pg])
c.shot(os.path.join(PNG, 'ex41_1440_est_sem_resultado.png'))

# ---------- A · aviso temporário ----------
abre('IN-04.dc.html', 1.6)
J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>b.innerText.trim()==='Pragas e doenças'); if(b) b.click();})()"); time.sleep(.8)
J("(()=>{const b=[...document.querySelectorAll('main [role=group] button')].find(b=>b.innerText.trim()==='Últimos 30 dias'); if(b) b.click();})()"); time.sleep(.5)
R['A_toast'] = json.loads(J("JSON.stringify((t=>t?{txt:t.innerText.replace(/\\s+/g,' ').trim(),pe:getComputedStyle(t).pointerEvents,botoes:t.querySelectorAll('button').length,role:t.getAttribute('role')}:null)(document.querySelector('.g2toast')))"))
log(L, 'A toast comum', R['A_toast'])

# ---------- B · indisponível: o motivo aparece em texto junto do botão? (PM, MA-02, MA-04det) ----------
for pg, rot in [('PM.dc.html', 'Criar plano'), ('MA-02.dc.html', 'Gerar 3 ordens preventivas'), ('MA-04det.dc.html', 'Concluir serviço')]:
    abre(pg)
    R['B_' + pg] = json.loads(J(f"""JSON.stringify((()=>{{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const b=[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&n(b.innerText)==={json.dumps(rot)});
      if(!b) return null; const r=b.getBoundingClientRect(); const perto=[...document.querySelectorAll('div,span,p,small')].filter(e=>e.children.length===0&&e.getClientRects().length&&!b.contains(e)).filter(e=>{{const q=e.getBoundingClientRect(); return Math.abs(q.top-r.bottom)<40&&q.left<r.right+40&&q.right>r.left-200;}}).map(e=>n(e.innerText)).filter(Boolean);
      return {{dis:b.disabled||b.getAttribute('aria-disabled'),dica:b.getAttribute('data-dica')||b.title||'',desc:(b.getAttribute('aria-describedby')||''),texto_perto:perto.slice(0,4)}};}})())"""))
    log(L, 'B', pg, R['B_' + pg])
    c.shot(os.path.join(PNG, 'ex41_1440_indisp_' + pg.split('.')[0] + '.png'))
# ---------- C · CD-04: colunas disponíveis (a Função tem coluna com funil?) ----------
abre('CD-04.dc.html'); clica('Colunas', exato=False); time.sleep(.4)
R['C_cd04_colunas'] = J("[...document.querySelectorAll('[role=menu] [role^=menuitem],[role=dialog] label,[role=listbox] [role=option]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').trim()).slice(0,20)")
log(L, 'C CD-04 colunas', R['C_cd04_colunas']); c.tecla('Escape', 'Escape', 27)

# ---------- D · um componente por tarefa (entrada pelo menu) ----------
R['D_menu'] = {}
for mod in ['MOD-AGR.dc.html', 'MOD-COM.dc.html', 'MOD-SUP.dc.html', 'Main.dc.html']:
    abre(mod)
    R['D_menu'][mod] = J("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>/^(PL-01|SAF|VE-04|VEN|EST|CMP|SU-0)/.test(h))")
log(L, 'D links de entrada', R['D_menu'])
R['erros_js'] = J("window.__errs||[]"); dump('p5_ex41_alvos.json', R); log(L, 'FIM')
