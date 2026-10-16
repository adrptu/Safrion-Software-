# Revisão do Claude, PR #75 R2: PT-06 "Criar ação interna" no navegador (mouse, Enter, toque 390), opções, negativas e rascunho.
import sys, os, time, json
G=sys.argv[1]; sys.path.insert(0,G)
from comp_lib import Chrome, servir
R=os.environ.get('RENDER_DIR') or os.path.join(G,'_render')
OK,FAIL=[],[]
def chk(n,c,x=''): (OK if c else FAIL).append(n); print(('OK   ' if c else 'FALHA'),n,'' if c else str(x)[:400],flush=True)
p,srv=servir(R); c=Chrome(); J=c.js; U=lambda pg:f'http://127.0.0.1:{p}/{pg}'
DLG="[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getBoundingClientRect().width>1)"
def dlg(): return J(f"(()=>{{const d={DLG}; if(!d) return null; const r=d.getBoundingClientRect(); const s=d.querySelector('select'); return {{lab:d.getAttribute('aria-label'),txt:d.innerText,opts:s?[...s.options].map(o=>o.text):null,L:r.left,R:r.right,W:innerWidth,foco:d.contains(document.activeElement)}};}})()")
def alvo(txt):
    return J(f"(()=>{{const b=[...document.querySelectorAll('button,[role=button]')].find(b=>b.innerText.trim()==={json.dumps(txt)}&&b.getBoundingClientRect().width>0); if(!b) return null; b.scrollIntoView({{block:'center'}}); const r=b.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];}})()")
def clicar(txt, toque=False):
    r=alvo(txt)
    if not r: return False
    time.sleep(.3); r=alvo(txt)
    if toque: c.toque(r[0],r[1])
    else: c.mouse(r[0],r[1]); c.mouse(r[0],r[1],'mousePressed','left'); c.mouse(r[0],r[1],'mouseReleased','left')
    time.sleep(.8); return True
def preencher(campo,val):
    return J(f"""(()=>{{const d={DLG}; const e=d&&d.querySelector('#fx_g_co_{campo},[id="fx_g_co_{campo}"]'); if(!e) return false;
      const P=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(e,{json.dumps(val)});
      e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return e.value;}})()""")
def adulterar(nome):
    return J(f"""(()=>{{const s={DLG}.querySelector('select'); const o=document.createElement('option'); o.value=o.text={json.dumps(nome)}; s.appendChild(o);
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(nome)}); s.dispatchEvent(new Event('input',{{bubbles:true}})); s.dispatchEvent(new Event('change',{{bubbles:true}})); return s.value;}})()""")
def abrir_pt06():
    c.goto(U('PT-06.dc.html'),1.5); J("window.__errs=[];addEventListener('error',e=>__errs.push(e.message));1")
try:
    c.aparelho(1440,900); c.goto(U('Main.dc.html'),.3); J("localStorage.clear();sessionStorage.clear();1"); abrir_pt06()
    clicar('Criar ação interna'); d=dlg()
    chk('A1 clique de mouse abre o formulário',bool(d) and 'Ação interna da Fertisul' in (d or {}).get('lab',''),d)
    chk('A1b Responsável só com Marta e Diego',d and d['opts']==['Marta Nunes','Diego Prado'],d and d['opts'])
    clicar('Salvar'); d=dlg()
    chk('A2 salvar sem tema não grava e fica aberto',bool(d) and ('Tema' in d['txt'] and ('obrigat' in d['txt'].lower() or 'informe' in d['txt'].lower())),d and d['txt'][:300])
    preencher('tema','Rever condição comercial (sintético)'); preencher('prazo','2026-10-30'); adulterar('Ana')
    clicar('Salvar'); d=dlg()
    chk('A3 pessoa da fazenda adulterada é recusada junto do campo',bool(d) and 'Escolha uma pessoa ativa da Fertisul' in d['txt'],d and d['txt'][:300])
    chk('A3b rascunho preservado (tema e prazo)',J(f"(()=>{{const d={DLG}; return d&&d.querySelector('#fx_g_co_tema').value==='Rever condição comercial (sintético)'&&d.querySelector('#fx_g_co_prazo').value==='2026-10-30';}})()"))
    adulterar('Sônia Reis'); clicar('Salvar'); d=dlg()
    chk('A4 Sônia (convite pendente) é recusada',bool(d) and 'Escolha uma pessoa ativa da Fertisul' in d['txt'],d and d['txt'][:300])
    preencher('resp','Diego Prado'); clicar('Salvar'); d=dlg(); body=J("document.body.innerText")
    chk('A5 válido com Diego grava e fecha',d is None and 'Ação interna registrada nesta demonstração · Diego Prado' in body,(d and d['txt'][:200]) or body[-300:])
    chk('A5b linha mostra Revisar ação interna e responsável',bool(alvo('Revisar ação interna')) and 'Diego Prado · ' in body)
    clicar('Revisar ação interna'); d=dlg()
    chk('A6 revisar abre com os valores gravados',bool(d) and J(f"(()=>{{const d={DLG}; return d.querySelector('#fx_g_co_tema').value==='Rever condição comercial (sintético)'&&d.querySelector('select').value==='Diego Prado';}})()"),d)
    clicar('Cancelar'); time.sleep(.3)
    # A7 fechar rascunho alterado pede confirmação
    abrir_pt06(); clicar('Criar ação interna'); preencher('tema','rascunho X'); clicar('×'); time.sleep(.4)
    t=J("document.body.innerText"); d=dlg()
    chk('A7 fechar rascunho alterado pede confirmação',('Descartar' in t or 'descartar' in t or 'confirm' in t.lower()) or (d and 'rascunho X' in J(f"{DLG}.querySelector('#fx_g_co_tema').value")),t[-400:])
    # A8 teclado: foco no botão e Enter
    abrir_pt06(); J("(()=>{const b=[...document.querySelectorAll('button,[role=button]')].find(b=>b.innerText.trim()==='Criar ação interna'); b.scrollIntoView({block:'center'}); b.focus(); return document.activeElement===b;})()")
    c.tecla('Enter','Enter',13,text='\r'); time.sleep(.8); d=dlg()
    chk('A8 Enter no botão abre o formulário com Marta e Diego',bool(d) and d['opts']==['Marta Nunes','Diego Prado'],d)
    print('     nota: foco dentro do formulário após abrir =',d and d['foco'],'(o mesmo no PT-07 Convidar usuário: comportamento do motor, anterior ao PR)')
    c.tecla('Escape','Escape',27); time.sleep(.5)
    # A10 região principal (r1) fica em consulta
    abrir_pt06(); r=J("(()=>{const t=[...document.querySelectorAll('[role=row],tr')].find(x=>x.innerText.includes('Sudoeste GO')&&x.innerText.includes('Região principal')); if(!t) return null; t.scrollIntoView({block:'center'}); const r=t.getBoundingClientRect(); return [r.left+40,r.top+r.height/2];})()")
    if r: c.mouse(r[0],r[1]); c.mouse(r[0],r[1],'mousePressed','left'); c.mouse(r[0],r[1],'mouseReleased','left'); time.sleep(.8)
    d=dlg(); chk('A10 região principal sem campos de ação',(d is None) or ('Tema' not in d['txt'] and 'Responsável' not in d['txt']),d and d['txt'][:300])
    errs=J("window.__errs||[]"); chk('A11 sem erro de JavaScript',not errs,errs)
    # A9 celular 390 com toque
    c.aparelho(390,844,2,True); abrir_pt06(); clicar('Criar ação interna',toque=True); d=dlg()
    chk('A9 toque a 390 abre o formulário dentro da janela',bool(d) and d['L']>=-0.5 and d['R']<=d['W']+0.5 and d['opts']==['Marta Nunes','Diego Prado'],d)
    s=J(f"(()=>{{const b=[...{DLG}.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); b.scrollIntoView({{block:'nearest'}}); const r=b.getBoundingClientRect(); return [r.left,r.right,r.top,r.bottom,r.height,innerWidth,innerHeight];}})()")
    chk('A9b Salvar alcançável e com alvo ≥ 44 px',s and s[0]>=0 and s[1]<=s[5] and s[3]<=s[6] and s[4]>=44,s)
    c.shot(os.environ.get('SHOT','/dev/null') if os.environ.get('SHOT') else '/tmp/claude-0/pt06_390.png')
    # PT-07 inalterado
    c.aparelho(1440,900); c.goto(U('PT-07.dc.html'),1.2); t=J("document.body.innerText")
    chk('A12 PT-07 com Marta, Diego e Sônia (convite pendente)',all(x in t for x in ('Marta Nunes','Diego Prado','Sônia Reis','Convite pendente')),t[:200])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK)+len(FAIL)}')
