# -*- coding: utf-8 -*-
"""Teste real (Chrome) · Planejar safra, revisão v3.8 (26/09): etapa 3 em uma linha e dentro da largura (planos-safra-01),
equipe do rendimento = demanda de Operadores (02), custo por kg pela produtividade das culturas da safra (03),
rendimento por safra e safra encerrada só consulta (04), data do primeiro uso na demanda de insumos (06)."""
import sys, os, time, subprocess, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_render')
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
OK = []; FAIL = []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('  ok  ' if cond else '  FALHOU ') + nome + (' · ' + str(det) if det != '' else ''))
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def panel(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def etapa(i): J(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i-1}].click()"); time.sleep(.55)
def abrir(nome):
    etapa(1); r = J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf({json.dumps(nome)})>=0); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>/safra/.test(b.innerText)); b.click(); return 'ok';}})()""")
    time.sleep(.55); return r
def row(txt): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]).find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸] /,''):'';}})()") or ''
def rowclick(txt):
    r = J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.45); return r
def fset(label, val):
    r = J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim()==={json.dumps(label)}); if(!l) return 'sem '+{json.dumps(label)}; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    time.sleep(.25); return r
LARG = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()"""
CUSTOH = r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\s+/g,' ').trim());
  const ci=hs.findIndex(h=>/^CUSTO \(R\$\/H\)/i.test(h)); return [...t.querySelectorAll('[role=row].g2kid')].map(r=>{ const cell=r.querySelectorAll('[role=cell]')[ci]; const cr=cell.getBoundingClientRect();
    const sp=[...cell.querySelectorAll('.g2pw span')].filter(s=>s.children.length===0&&s.innerText.trim()); const tops=new Set(sp.map(s=>Math.round(s.getBoundingClientRect().top+s.getBoundingClientRect().height/2)));
    return {t:sp.map(s=>s.innerText).join(' | '), linhas:tops.size, esq:Math.round(Math.min(...sp.map(s=>s.getBoundingClientRect().left))-cr.left), dir:Math.round(sp[sp.length-1].getBoundingClientRect().right)}; });})()"""
def total_oper():
    return J(r"""(()=>{const rs=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[1].querySelectorAll('[role=row]'); let on=false;
      for(const r of rs){ const t=r.innerText.replace(/\s+/g,' ').trim(); if(/Operadores e equipe/.test(t)) on=true; else if(on && /^Demanda \(h\)/.test(t)){ const cs=r.querySelectorAll('[role=cell]'); return cs[cs.length-1].innerText.trim(); } } return '';})()""")
num = lambda s: float(str(s).replace('.', '').replace(',', '.').replace('h', '').replace('−', '-').strip() or 'nan')
try:
    c.size(1440, 1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', wait=1.3)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    abrir('Safra 2026/27')
    etapa(5); oper0 = total_oper(); print('   Operadores e equipe · demanda total antes:', oper0)
    # ---------- 01 · etapa 3 em uma linha, dentro da largura ----------
    etapa(3)
    w = J(LARG); chk('01 · tabela da etapa 3 cabe no quadro a 1440 px (sem rolagem lateral)', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    ch = J(CUSTOH); print('   custo/h:', [x['t'] for x in ch][:3])
    chk('01 · composição e custo/h na mesma linha em todos os conjuntos', len(ch) == 8 and all(x['linhas'] == 1 for x in ch), [x['linhas'] for x in ch])
    chk('01 · composição não invade a coluna vizinha', all(x['esq'] >= 0 for x in ch), [x['esq'] for x in ch])
    chk('01 · custos por hora alinhados à direita', len(set(x['dir'] for x in ch)) == 1, sorted(set(x['dir'] for x in ch)))
    chk('01 · texto da composição', any(x['t'] == 'máq. 180 · impl. 95 · 1 × 38 = | 313,00' for x in ch), ch[0]['t'])
    # ---------- 03 · custo por kg ----------
    chk('03 · colheita de grãos (soja da safra: 63 sc/ha ponderado) = 0,0606', row('Colhedora').endswith('229,20 0,0606'), row('Colhedora'))
    chk('03 · colheita de café (38 sc/ha) = 0,2907', row('Derriçadeiras').endswith('0,2907'), row('Derriçadeiras'))
    chk('03 · operação que não é colheita mostra —', row('Trator 03 + Distribuidor').endswith('—'), row('Trator 03 + Distribuidor'))
    rowclick('Trator T1 JD 6M 155')
    pt = panel()
    chk('03 · formulário sem "Produtividade para custo por kg"', 'Produtividade' not in pt and 'Rendimento · Trator T1' in pt, pt[:120])
    chk('04 · subtítulo diz o alcance: "Vale só para esta safra."', 'Vale só para esta safra.' in pt)
    chk('04 · ajuda do campo Máquina', 'Inclua combustível, manutenção e depreciação; o operador entra em Pessoas.' in pt)
    # ---------- 02 · pessoas da equipe → demanda de Operadores ----------
    fset('Pessoas na equipe', '3'); clk('Salvar', 'aside[role=dialog]'); t = toast()
    chk('02 · salvar recalcula custo/h (180 + 140 + 3 × 38 = 434,00)', '434,00' in row('Trator T1 JD 6M 155') and '3 × 38' in row('Trator T1 JD 6M 155'), row('Trator T1 JD 6M 155'))
    etapa(5); oper1 = total_oper(); print('   Operadores e equipe · demanda total depois:', oper1)
    d = num(oper1) - num(oper0)
    chk('02 · demanda de Operadores sobe 1 × horas do plantio (610 ha ÷ 6,8 ha/h ≈ 89,7 h)', 88.5 <= d <= 91, round(d, 1))
    # ---------- 04 · edição vale só para esta safra ----------
    abrir('Safrinha 2027'); etapa(3)
    chk('04 · Safrinha mantém Plantio com 2 pessoas (396,00)', '2 × 38' in row('Trator T1 JD 6M 155') and '396,00' in row('Trator T1 JD 6M 155'), row('Trator T1 JD 6M 155'))
    w = J(LARG); chk('01 · Safrinha: tabela cabe no quadro', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    r = row('Colhedora'); chk('03 · Safrinha: custo por kg por cultura, sem média (Milho 0,0216 · Feijão 0,0764)', 'Milho 0,0216' in r and 'Feijão 0,0764' in r, r)
    chk('03 · Safrinha: colheita de café sem cultivo → "não calculável"', row('Derriçadeiras').endswith('não calculável'), row('Derriçadeiras'))
    abrir('Safra 2025/26'); etapa(3)
    chk('04 · safra encerrada: Plantio com o padrão (2 pessoas)', '2 × 38' in row('Trator T1 JD 6M 155'), row('Trator T1 JD 6M 155'))
    r = row('Colhedora'); chk('03 · 2025/26: soja e milho separados', 'Soja ' in r and 'Milho ' in r, r)
    rowclick('Colhedora'); pt = panel()
    semSalvar = not J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Salvar')")
    todosRO = J("[...document.querySelectorAll('aside[role=dialog] input')].every(i=>i.readOnly)") and J("[...document.querySelectorAll('aside[role=dialog] select')].every(s=>s.disabled)")
    chk('04 · safra encerrada: rendimento abre só em consulta (sem falar em permissão)', pt.startswith('Rendimento') and semSalvar and todosRO and 'Consulta' in pt and 'permissão' not in pt, pt[:140])
    clk('Fechar', 'aside[role=dialog]')
    # ---------- 06 · data do primeiro uso ----------
    abrir('Safra 2026/27'); etapa(6)
    w = J(LARG); chk('06 · demanda (grupos recolhidos) cabe no quadro a 1440 px', w['tab'] <= 1116 and w['scroll'] <= w['box'], w)
    hs = J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').replace(/ ⇅.*$/,'').trim())")
    chk('06 · coluna "1º uso" logo depois de Grupo · insumo', len(hs) > 2 and hs[1].upper().startswith('1º USO'), hs)
    chk('06 · grupo Herbicidas mostra a menor data dos insumos (25/09/2026)', row('Herbicidas').startswith('Herbicidas 3 insumos 25/09/2026'), row('Herbicidas'))
    clk('Expandir tudo')
    chk('06 · Glifosato 480: primeiro uso 25/09/2026 e quantidades com unidade', row('Glifosato 480').startswith('Glifosato 480 25/09/2026') and ' L ' in row('Glifosato 480') + ' ', row('Glifosato 480'))
    chk('06 · Fungicida C: primeiro uso 20/01/2027', '20/01/2027' in row('Fungicida C'), row('Fungicida C'))
    rowclick('Glifosato 480'); pt = panel()
    ori = J("[...document.querySelectorAll('aside[role=dialog] li, aside[role=dialog] div')].map(x=>x.innerText).filter(t=>/ · \\d{2}\\/\\d{2}\\/\\d{4} · /.test(t) && t.split('\\n').length===1)")
    datas = [re.search(r' · (\d{2})/(\d{2})/(\d{4}) · ', x).groups() for x in ori]
    chk('06 · origem com a data: "T1-A · Dessecação pré-plantio · 25/09/2026 · 2,00 L/ha × 160 ha = 320,0 L"', 'T1-A · Dessecação pré-plantio · 25/09/2026 · 2,00 L/ha × 160 ha = 320,0 L' in pt, pt[:300])
    chk('06 · origem em ordem de data', len(datas) >= 3 and [d[::-1] for d in datas] == sorted(d[::-1] for d in datas), ori[:4])
    clk('Fechar', 'aside[role=dialog]')
    c.shot(os.path.join(HERE, '_probe', 'saf38_e6.png'))
    chk('sem erro de JS', not J("window.__errs.length"), J("window.__errs"))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -', f) for f in FAIL]
