# Teste real (Chrome) — Planejar safra: dividir o talhão em quantas parcelas precisar
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__))
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('  ok  ' if cond else '  FALHOU ')+nome+(' · '+str(det) if det else ''))
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
SETV="""((lab,val)=>{const e=[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].find(x=>x.getAttribute('aria-label')===lab); if(!e) return 'NÃO ACHEI '+lab;
  const proto=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(proto,'value').set.call(e,val); e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true})); return 'ok';})"""
def setv(lab,val): r=J(f"({SETV})({json.dumps(lab)},{json.dumps(val)})"); time.sleep(.25); return r
# TABELAS-FOCO (5983172395): a etapa 2 tem uma variável por coluna (Talhão ou parcela | Tipo | … | Área livre | … | Ajustes locais; a Meta leva a unidade
# junto, decisão de 05/10/2026); LEGT lê as
# colunas pelo cabeçalho e remonta o texto de antes ("T1 2 parcelas · área toda alocada Dividir …"), para as mesmas asserções valerem
LEGT="""(r=>{ const t=r.closest('[role=table]'); const hs=t?[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase()):[];
  const raw=r.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸] /,''); const iT=hs.indexOf('TIPO'); if(hs.indexOf('TALHÃO OU PARCELA')<0||iT<0) return raw;
  const cs=[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\\s+/g,' ').trim()); const g=k=>(cs[hs.indexOf(k)]||'').replace(/^[▾▸] ?/,'');
  const L=g('TALHÃO OU PARCELA'), div=/ Dividir$/.test(L), nm=L.replace(/ Dividir$/,''), tp=g('TIPO'), lv=g('ÁREA LIVRE').replace(/ ha$/,''), aj=g('AJUSTES LOCAIS');
  let head; if(/^\\d+ parcelas?$/.test(tp)){ const v=lv.replace(/^[-−]/,''); head=nm+' '+tp+' · '+(lv==='0'?'área toda alocada':(/^[-−]/.test(lv)?'excede '+v+' ha':lv+' ha livres'))+(div?' Dividir':''); }
  else head=nm+' '+tp.toLowerCase().replace(' (sem polígono)',' · sem polígono')+(div?' Dividir':'');
  const n=/^\\d+$/.test(aj)?Number(aj):0; const ajt=n?(/^\\d+ parcelas?$/.test(tp)?(' '+n+(n>1?' ajustes locais':' ajuste local')):(' '+n+(n>1?' ajustes deste talhão':' ajuste deste talhão'))):'';
  return [head,g('CULTURA'),g('VARIEDADE'),g('ÁREA'),g('PLANTIO'),g('META'),g('PLANO AGRONÔMICO'),g('VERSÃO')].join(' ').replace(/\\s+/g,' ').trim()+ajt; })"""
ROWS=f"""(()=>[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')].slice(1)).map(r=>({LEGT})(r)))()"""
def rows(): return J(ROWS) or []
def rowbtn(prefix,label):
    return J(f"""(()=>{{const rs=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]);
      const r=rs.find(x=>({LEGT})(x).startsWith({json.dumps(prefix)})); if(!r) return 'SEM LINHA';
      const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(label)}); if(!b) return 'SEM BOTÃO'; b.click(); return 'ok';}})()""")
def rowclick(prefix):
    return J(f"""(()=>{{const rs=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]);
      const r=rs.find(x=>({LEGT})(x).startsWith({json.dumps(prefix)})); if(!r) return 'SEM LINHA'; const cell=[...r.children].find(x=>!x.querySelector('input,button')&&x.innerText.trim())||r; cell.click(); return 'ok';}})()""")
def panel(): return J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def pvals(): return J("[...document.querySelectorAll('aside[role=dialog] input')].filter(i=>/^Nome da parcela|^Área de/.test(i.getAttribute('aria-label'))).map(i=>i.value)")
def k(txt_re): return J(f"(document.body.innerText.match({txt_re})||[''])[0]")
from comp_lib import IR_ETAPA
def etapa(i): r=J(f"({IR_ETAPA})({i})"); time.sleep(.5); return r   # a faixa só informa (UX-ACAO-UNICA-20261003): anda pela área de ações
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
    chk('sem erro de JS ao abrir', (J("window.__err||''") or '')=='', J("window.__err||''"))
    clk('Continuar'); time.sleep(.3)   # 01/10: a ação da safra nomeia o próximo passo (2026/27: aplicar plano, etapa 2)
    rs=rows(); print('   linhas:', rs[:4])
    chk('T1 aparece como linha do talhão com 2 parcelas', any(r.startswith('T1 2 parcelas · área toda alocada Dividir') for r in rs), [r for r in rs if r.startswith('T1')][:3])
    chk('T1-A e T1-B são sublinhas', any(r.startswith('T1-A parcela') for r in rs) and any(r.startswith('T1-B parcela') for r in rs))
    k2a=k(r"/\d+ cultivos · [^\n]+/"); print('   k2:',k2a)
    chk('k2 conta 9 cultivos (folhas)', k2a.startswith('9 cultivos · 1.165 ha'), k2a)
    etapa(4); k4a=k(r"/[\d.]+ ha trabalhados[^\n]+/"); etapa(6); k6a=k(r"/Valor da necessidade[^\n]+/"); etapa(2)
    print('   k4:',k4a); print('   k6:',k6a)
    # --- invariante: dividir T2 em 3 com o mesmo plano não muda k4/k6
    chk('abre Dividir T2', rowbtn('T2 talhão inteiro','Dividir')=='ok' and 'Dividir T2 em parcelas' in panel())
    chk('proposta inicial T2-A/T2-B 149/149', pvals()==['T2-A','149','T2-B','149'], pvals())
    clk('+ Adicionar parcela','aside[role=dialog]')
    chk('T2-C adicionada (sem área livre → vazia)', pvals()[-2:]==['T2-C',''], pvals())
    chk('T2-C copia plano de T2-B', 'copiado de T2-B' in panel())
    clk('Distribuir área igualmente','aside[role=dialog]')
    chk('distribui 99,33/99,33/99,34', pvals()==['T2-A','99,33','T2-B','99,33','T2-C','99,34'], pvals())
    chk('selo Área conferida', 'Área conferida' in panel())
    clk('Salvar divisão','aside[role=dialog]'); t=toast()
    chk('salvou T2 em 3 parcelas', 'T2 dividido em 3 parcelas' in t and not panel(), t)
    rs=rows(); chk('T2 tem sublinhas T2-A..C', all(any(r.startswith(f'T2-{x} parcela') for r in rs) for x in 'ABC'))
    etapa(4); k4b=k(r"/[\d.]+ ha trabalhados[^\n]+/"); etapa(6); k6b=k(r"/Valor da necessidade[^\n]+/"); etapa(2)
    chk('k4 idêntico após dividir T2', k4b==k4a, k4b); chk('k6 idêntico após dividir T2', k6b==k6a, k6b)
    # --- T4 em 5 parcelas
    rowbtn('T4 talhão inteiro','Dividir')
    for _ in range(3): clk('+ Adicionar parcela','aside[role=dialog]')
    clk('Distribuir área igualmente','aside[role=dialog]')
    chk('T4 em 5 × 40,8', pvals()==['T4-A','40,8','T4-B','40,8','T4-C','40,8','T4-D','40,8','T4-E','40,8'], pvals())
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('salvou T4 em 5', 'T4 dividido em 5 parcelas' in t, t)
    rs=rows(); chk('5 sublinhas de T4', sum(1 for r in rs if r.startswith('T4-'))==5 and any(r.startswith('T4 5 parcelas') for r in rs))
    k2b=k(r"/\d+ cultivos · [^\n]+/"); chk('k2 conta folhas (15 cultivos, mesma área)', k2b.startswith('15 cultivos · 1.165 ha'), k2b)
    tot=J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const r=[...t.querySelectorAll('[role=row]')].pop(); return r.innerText.replace(/\\s+/g,' ');})()")
    chk('total da tabela 1.165 ha (unidade na célula, cabeçalho "Área": decisão de 05/10/2026)', 'Total 1.165 ha' in (tot or '') and bool(J("[...document.querySelectorAll('[role=columnheader]')].some(h=>/^Área\\b/i.test(h.innerText.trim())&&!/livre|\\(/i.test(h.innerText))")), tot)
    # --- 27 parcelas: nomes após Z viram AA
    rowbtn('T1 2 parcelas','Dividir')
    for _ in range(25): clk('+ Adicionar parcela','aside[role=dialog]')
    v=pvals(); chk('27 parcelas: última é T1-AA', v[-2]=='T1-AA' and len(v)==54, v[-4:])
    clk('Distribuir área igualmente','aside[role=dialog]')
    ar=[float(x.replace(',','.')) for x in pvals()[1::2]]; chk('soma exata 312 ha em 27 parcelas', abs(sum(ar)-312)<1e-6, round(sum(ar),4))
    chk('T1-C copia ajuste do T1-B', '1 ajuste · copiado de T1-B' in panel())
    J("(()=>{const a=document.querySelector('aside[role=dialog]'); a.scrollTop=a.scrollHeight;})()")
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('salvou T1 em 27 parcelas', 'T1 dividido em 27 parcelas' in t, t)
    rs=rows(); chk('27 sublinhas de T1', sum(1 for r in rs if r.startswith('T1-'))==27)
    chk('T1-B mantém o ajuste', any(r.startswith('T1-B parcela') and '1 ajuste' in r for r in rs))
    # --- excesso bloqueia; área livre permitida
    rowbtn('T3 talhão inteiro','Dividir')
    setv('Área de T3-A em hectares','90'); setv('Área de T3-B em hectares','48')
    chk('selo Excede em 42 ha', 'Excede em 42 ha' in panel(), panel()[:160])
    clk('Salvar divisão','aside[role=dialog]')
    chk('erro de excesso e não salvou', 'As parcelas somam 138 ha; o talhão tem 96 ha. Reduza 42 ha.' in panel(), panel()[:300])
    setv('Área de T3-B em hectares','1')
    chk('selo 5 ha livres', '5 ha livres' in panel())
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('salvou T3 com área livre', 'T3 dividido em 2 parcelas · 5 ha livres' in t, t)
    chk('linha do T3 mostra 5 ha livres', any(r.startswith('T3 2 parcelas · 5 ha livres') for r in rows()))
    # --- erros de campo
    rowclick('T4 5 parcelas'); time.sleep(.3)
    chk('clique na linha do talhão abre o painel', 'Dividir T4 em parcelas' in panel())
    setv('Variedade de T4-B',''); setv('Nome da parcela T4-C','T4-A')
    clk('Salvar divisão','aside[role=dialog]')
    pt=panel(); chk('erros de campo (variedade e nome repetido)', 'Informe a variedade' in pt and 'Nome T4-A repetido' in pt, pt[-400:])
    clk('Cancelar','aside[role=dialog]'); chk('aviso de alterações não salvas', 'Há alterações não salvas' in panel())
    clk('Descartar alterações','aside[role=dialog]'); chk('descartou e fechou', not panel())
    # --- excluir com confirmação e voltar a talhão inteiro
    rowbtn('T2 3 parcelas','Dividir')
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.getAttribute('aria-label')==='Excluir parcela T2-C'); b&&b.click();})()"); time.sleep(.3)
    chk('excluir parcela com plano pede confirmação', 'Excluir T2-C? Sai do plano operacional e da demanda.' in panel())
    clk('Excluir parcela','aside[role=dialog] [role=alert]')
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.getAttribute('aria-label')==='Excluir parcela T2-B'); b&&b.click();})()"); time.sleep(.3)
    clk('Excluir parcela','aside[role=dialog] [role=alert]')
    setv('Área de T2-A em hectares','298')
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('T2 volta a talhão inteiro', 'T2 volta a talhão inteiro' in t, t)
    chk('linha T2 talhão inteiro', any(r.startswith('T2 talhão inteiro') for r in rows()))
    etapa(4); k4c=k(r"/[\d.]+ ha trabalhados[^\n]+/"); etapa(2)
    print('   k4 depois das divisões:',k4c)
    # --- formulário: validação cruzada de área
    rowclick('T3-A'); time.sleep(.3)
    setv('Área','200') if False else None
    lab=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?[...a.querySelectorAll('label')].map(l=>l.innerText).join('|'):''})()"); print('   campos do formulário:',lab)
    J("""(()=>{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith('Área')); const i=document.getElementById(l.getAttribute('for')); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'96'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Salvar','aside[role=dialog]')
    chk('formulário bloqueia soma acima do talhão', 'As parcelas de T3 somariam 97 ha; o talhão tem 96 ha (livre: 95 ha).' in panel(), panel()[-300:])
    J("""(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"""); time.sleep(.3)
    if panel(): clk('Descartar alterações','aside[role=dialog]')
    # --- Safrinha: novo cultivo em talhão livre e em talhão já planejado
    etapa(1); J("(()=>{const rs=[...document.querySelectorAll('[role=row]')]; const r=rs.find(x=>/Safrinha/.test(x.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); b.click();})()"); time.sleep(.5); etapa(2)   # a Safrinha pode abrir noutra etapa
    rs=rows(); chk('Safrinha: T1 com 1 parcela e 152 ha livres', any(r.startswith('T1 1 parcela · 152 ha livres') for r in rs), [r for r in rs if r.startswith('T1')])
    clk('Adicionar cultivo'); time.sleep(.3)   # AÇÃO: o "Novo cultivo" do topo virou "Adicionar cultivo" junto da lista (abre o mesmo formulário Novo cultivo)
    def fset(label,val,sel=False):
        return J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith({json.dumps(label)})); if(!l) return 'sem '+{json.dumps(label)}; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    for lab_,val in [('Talhão','T4'),('Cultura','Milho'),('Variedade','AG 8700'),('Área','100'),('Plantio','2027-02-28'),('Meta de produtividade','170')]: fset(lab_,val); time.sleep(.15)
    clk('Salvar','aside[role=dialog]'); t=toast()
    chk('novo cultivo em talhão livre vira parcela T4-A com 104 ha livres', 'parcela T4-A · 104 ha livres em T4' in t, t)
    clk('Adicionar cultivo'); time.sleep(.3)   # AÇÃO: o "Novo cultivo" do topo virou "Adicionar cultivo" junto da lista (abre o mesmo formulário Novo cultivo)
    for lab_,val in [('Talhão','T2'),('Cultura','Milho'),('Variedade','AG 8700'),('Área','50'),('Plantio','2027-03-01'),('Meta de produtividade','170')]: fset(lab_,val); time.sleep(.15)
    clk('Salvar','aside[role=dialog]'); time.sleep(.3); t=toast(); pt=panel()
    chk('novo cultivo em talhão planejado abre o painel com a nova parcela', 'T2 já está nesta safra' in t and 'Dividir T2 em parcelas' in pt and 'Excede em 50 ha' in pt, (t,pt[:200]))
    setv('Área de T2-A em hectares','248'); clk('Salvar divisão','aside[role=dialog]'); t=toast()
    chk('salvou T2 com 2 parcelas na Safrinha', 'T2 dividido em 2 parcelas' in t, t)
    # --- safra encerrada: sem Dividir
    etapa(1); J("(()=>{const rs=[...document.querySelectorAll('[role=row]')]; const r=rs.find(x=>/2025\\/26/.test(x.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/Consultar safra/.test(b.innerText)); b.click();})()"); time.sleep(.5)
    chk('safra encerrada sem "Dividir"', not any('Dividir' in r for r in rows()), rows()[:2])
    chk('sem erro de JS no fim', (J("window.__err||''") or '')=='', J("window.__err||''"))
    c.shot(os.path.join(HERE,'_probe','partest_fim.png'))
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
