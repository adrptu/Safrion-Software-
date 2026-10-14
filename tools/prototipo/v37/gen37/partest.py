# Teste real (Chrome) — Planejar safra: dividir o talhão em quantas parcelas precisar
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
from comp_lib import cv_todas_sempre
HERE=os.path.dirname(os.path.abspath(__file__))
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
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
  const L=g('TALHÃO OU PARCELA').replace(/ (Planejar|Vincular ciclo) ›$/,''), div=/ Dividir$/.test(L), nm=L.replace(/ Dividir$/,''), tp=g('TIPO'), lv=g('ÁREA LIVRE').replace(/ ha$/,''), aj=g('AJUSTES LOCAIS');
  let head; if(/^\\d+ parcelas?$/.test(tp)){ const v=lv.replace(/^[-−]/,''); head=nm+' '+tp+' · '+((lv==='0'||lv==='—')?'área toda alocada':(/^[-−]/.test(lv)?'excede '+v+' ha':lv+' ha livres'))+(div?' Dividir':''); }
  else head=nm+' '+tp.toLowerCase().replace(' (sem polígono)',' · sem polígono')+(div?' Dividir':'');
  const n=/^\\d+$/.test(aj)?Number(aj):0; const ajt=n?(/^\\d+ parcelas?$/.test(tp)?(' '+n+(n>1?' ajustes locais':' ajuste local')):(' '+n+(n>1?' ajustes deste talhão':' ajuste deste talhão'))):'';
  return [head,g('CULTURA'),g('VARIEDADE'),g('ÁREA'),g('PLANTIO'),g('META'),g('PLANO AGRONÔMICO'),g('VERSÃO')].join(' ').replace(/\\s+/g,' ').trim()+ajt; })"""
FORA="""(r=>{ const t=r.closest('[role=table]'); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase()); const i=hs.indexOf('SAFRA'); const cs=[...r.querySelectorAll('[role=cell]')]; return r.classList.contains('g2kid')&&i>=0&&cs[i]&&/›$/.test(cs[i].innerText.trim()); })"""
ROWS=f"""(()=>[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')].slice(1)).filter(r=>!({FORA})(r)).map(r=>({LEGT})(r)))()"""
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
def etapa(i): r=J(f"({IR_ETAPA})({i})"); time.sleep(.5); return r
def k3(): return J("(()=>{ const c=(document.body.innerText.match(/Custo de operação R\\$ [\\d.,]+/)||[''])[0]; const t=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&/^Total\\b/.test(r.innerText.trim())).map(r=>r.innerText.replace(/\\s+/g,' ').trim()).join(' | '); return c+' · '+t; })()") or ''   # a faixa só informa (UX-ACAO-UNICA-20261003): anda pela área de ações
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
    chk('sem erro de JS ao abrir', (J("window.__err||''") or '')=='', J("window.__err||''"))
    clk('Continuar'); time.sleep(.3)   # 01/10: a ação da safra nomeia o próximo passo (2026/27: aplicar plano, etapa 2)
    rs=rows(); print('   linhas:', rs[:4])
    chk('T1 aparece como linha do talhão com 2 parcelas', any(r.startswith('T1 2 parcelas · área toda alocada Dividir') for r in rs), [r for r in rs if r.startswith('T1')][:3])
    chk('T1-A e T1-B são sublinhas', any(r.startswith('T1-A parcela') for r in rs) and any(r.startswith('T1-B parcela') for r in rs))
    # etapa 2 nova: a faixa diz os hectares desta safra; a contagem é das linhas desta safra (sem a linha do talhão nem as de fora)
    NFOLHAS=f"""(()=>[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]).filter(r=>r.querySelector('button.g2del')&&!({FORA})(r)).length)()"""
    k2a=k(r"/Nesta safra [^\n]+/"); print('   faixa:',k2a)
    chk('faixa "Nesta safra 1.165" e 9 cultivos (folhas)', k2a.startswith('Nesta safra 1.165') and J(NFOLHAS)==9, (k2a,J(NFOLHAS)))
    # etapa única (05/10/2026): o k4 saiu; horas e custo de operação ficam na etapa 3 (Total da g_op e linha do título); a demanda na 4
    etapa(3); k4a=k3(); etapa(4); k6a=k(r"/Valor da necessidade[^\n]+/"); etapa(2)
    print('   etapa 3:',k4a); print('   k6:',k6a)
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
    etapa(3); k4b=k3(); etapa(4); k6b=k(r"/Valor da necessidade[^\n]+/"); etapa(2)
    chk('horas-conjunto e custo de operação (etapa 3) idênticos após dividir T2', k4b==k4a and 'Custo de operação' in k4a, k4b); chk('k6 idêntico após dividir T2', k6b==k6a, k6b)
    # --- T4 em 5 parcelas
    rowbtn('T4 talhão inteiro','Dividir')
    for _ in range(3): clk('+ Adicionar parcela','aside[role=dialog]')
    clk('Distribuir área igualmente','aside[role=dialog]')
    chk('T4 em 5 × 40,8', pvals()==['T4-A','40,8','T4-B','40,8','T4-C','40,8','T4-D','40,8','T4-E','40,8'], pvals())
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('salvou T4 em 5', 'T4 dividido em 5 parcelas' in t, t)
    rs=rows(); chk('5 sublinhas de T4', sum(1 for r in rs if r.startswith('T4-'))==5 and any(r.startswith('T4 5 parcelas') for r in rs))
    k2b=k(r"/Nesta safra [^\n]+/"); chk('faixa e folhas (15 cultivos, mesma área)', k2b.startswith('Nesta safra 1.165') and J(NFOLHAS)==15, (k2b,J(NFOLHAS)))
    tot=J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const r=[...t.querySelectorAll('[role=row]')].pop(); return r.innerText.replace(/\\s+/g,' ');})()")
    chk('total da tabela 1.165 ha (unidade na célula, cabeçalho "Área": decisão de 05/10/2026)', 'Total 1.165 ha' in (tot or '') and bool(J("[...document.querySelectorAll('[role=columnheader]')].some(h=>/^Área\\b/i.test(h.innerText.trim())&&!/livre|\\(/i.test(h.innerText))")), tot)
    # --- 27 parcelas: nomes após Z viram AA
    rowbtn('T1 2 parcelas','Dividir')
    for _ in range(25): clk('+ Adicionar parcela','aside[role=dialog]')
    v=pvals(); chk('27 parcelas: última é T1-AA', v[-2]=='T1-AA' and len(v)==54, v[-4:])
    clk('Distribuir área igualmente','aside[role=dialog]')
    ar=[float(x.replace(',','.')) for x in pvals()[1::2]]; chk('soma exata 312 ha em 27 parcelas', abs(sum(ar)-312)<1e-6, round(sum(ar),4))
    # oráculo do texto vigente do painel (safra.js divVals: "N ajuste(s) deste talhão · copiado de X"; o "· copiado de" é o mesmo)
    chk('T1-C copia ajuste do T1-B', '1 ajuste deste talhão · copiado de T1-B' in panel(), panel()[:300])
    J("(()=>{const a=document.querySelector('aside[role=dialog]'); a.scrollTop=a.scrollHeight;})()")
    clk('Salvar divisão','aside[role=dialog]'); t=toast(); chk('salvou T1 em 27 parcelas', 'T1 dividido em 27 parcelas' in t, t)
    rs=rows(); chk('27 sublinhas de T1', sum(1 for r in rs if r.startswith('T1-'))==27)
    chk('T1-B mantém o ajuste', any(r.startswith('T1-B parcela') and '1 ajuste' in r for r in rs))
    # o ajuste copiado persiste depois de salvar a divisão (produto e dose no destino, iguais aos do T1-B) e editar a cópia não muda o
    # original: painel "Insumos e doses de …" (clique no plano da linha), insumo da chave a6|0 (#lp_a6_0; c2 = T1-B, dados2.AJUSTES 0,60)
    LPABRE="""(pref=>{ const rs=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')]);
      const r=rs.find(x=>({LEGT})(x).startsWith(pref)); if(!r) return 'SEM LINHA'; const t=r.closest('[role=table]');
      const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase()); const i=hs.indexOf('PLANO AGRONÔMICO');
      const cel=[...r.querySelectorAll('[role=cell]')][i]; const b=cel&&cel.querySelector('button'); if(!b) return 'SEM PLANO'; b.click(); return 'ok'; })""".replace('{LEGT}',LEGT)
    LPLE="""(()=>{ const d=document.querySelector('aside[role=dialog]'); const i=d&&d.querySelector('#lp_a6_0'); if(!i) return null; let r=i.parentElement;
      while(r&&r!==d&&!/R\\$/.test(r.innerText)) r=r.parentElement;
      return {tit:(d.querySelector('h2')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim(), dose:i.value, linha:(r||i.parentElement).innerText.replace(/\\s+/g,' ').trim()}; })()"""
    def lp(pref): r=J(f"({LPABRE})({json.dumps(pref)})"); time.sleep(.5); return [r,J(LPLE)]
    def lpfecha():
        J("(()=>{const d=document.querySelector('aside[role=dialog]'); const b=d&&(d.querySelector('[aria-label=Fechar]')||[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Cancelar')); b&&b.click();})()"); time.sleep(.35)
        if panel(): clk('Descartar alterações','aside[role=dialog]')
    oB=lp('T1-B parcela'); lpfecha(); oC=lp('T1-C parcela')
    chk('T1-C (salvo) tem o ajuste copiado do T1-B: mesmo produto e dose 0,6 no painel de insumos e doses', oB[0]=='ok' and oC[0]=='ok' and oB[1] and oC[1] and 'T1-C' in oC[1]['tit'] and 'T1-B' in oB[1]['tit']
        and oC[1]['dose']==oB[1]['dose']=='0,6' and oC[1]['linha'].replace(oC[1]['dose'],'')==oB[1]['linha'].replace(oB[1]['dose'],''), [oB,oC])
    J("""(()=>{const i=document.querySelector('aside[role=dialog] #lp_a6_0'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'0,75'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.25)
    clk('Salvar','aside[role=dialog]'); t=toast()
    chk('editar a cópia (T1-C 0,75) salva só no T1-C', '1 dose alterada em T1-C' in t and not panel(), t)
    nB=lp('T1-B parcela'); lpfecha(); nC=lp('T1-C parcela'); lpfecha()
    chk('o original (T1-B) continua 0,6 e a cópia (T1-C) fica 0,75', nB[1] and nC[1] and nB[1]['dose']=='0,6' and nC[1]['dose']=='0,75', [nB,nC])
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
    etapa(3); k4c=k3(); etapa(2)
    print('   etapa 3 depois das divisões:',k4c)
    # --- formulário: validação cruzada de área
    rowclick('T3-A'); time.sleep(.3)
    setv('Área','200') if False else None
    lab=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?[...a.querySelectorAll('label')].map(l=>l.innerText).join('|'):''})()"); print('   campos do formulário:',lab)
    J("""(()=>{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith('Área')); const i=document.getElementById(l.getAttribute('for')); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'96'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Salvar','aside[role=dialog]')
    chk('formulário bloqueia soma acima do talhão (M1: período e máximo)', 'Máximo 95 ha nesse período.' in panel() and 'ha de T3 estão com Soja (T3-B, Safra 2026/27)' in panel(), panel()[-400:])
    J("""(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"""); time.sleep(.3)
    if panel(): clk('Descartar alterações','aside[role=dialog]')
    # --- Safrinha: novo cultivo em talhão livre e em talhão já planejado
    etapa(1); J("(()=>{const rs=[...document.querySelectorAll('[role=row]')]; const r=rs.find(x=>/Safrinha/.test(x.innerText)); const b=[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); b.click();})()"); time.sleep(.5); etapa(2)   # a Safrinha pode abrir noutra etapa
    rs=rows(); chk('Safrinha: T1 com 1 parcela e 152 ha livres a partir de 21/02/2027', any(r.startswith('T1 1 parcela · 152 ha livres') for r in rs) and '21/02/2027' in J("document.body.innerText"), [r for r in rs if r.startswith('T1')])
    # etapa 2 nova: sem "Adicionar cultivo"; planeja-se pela linha do talhão (Planejar ›, Dividir)
    chk('sem "Adicionar cultivo"', J("document.querySelectorAll('[data-acao=adicionar]').length")==0)
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.querySelector('.g2c0')&&/^[▾▸]?\\s?T4\\s/.test(x.querySelector('.g2c0').innerText.trim())); const b=r&&[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Planejar ›'); b&&b.click();})()"""); time.sleep(.4)
    def fset(label,val,sel=False):
        return J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith({json.dumps(label)})); if(!l) return 'sem '+{json.dumps(label)}; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    for lab_,val in [('Cultura','Milho'),('Variedade','AG 8700'),('Área','100'),('Plantio','2027-02-28'),('Meta de produtividade','170')]: fset(lab_,val); time.sleep(.15)
    clk('Salvar','aside[role=dialog]'); t=toast()
    # o Parcela veio "T4" (sugestão para a área cheia) e a área baixou para 100 ha: o nome final é o mesmo que a trava conferiu (parcelaFinal,
    # revisão SAF S2.2), a próxima letra livre no talhão; T4-A a T4-E já são faixas da Safra 2026/27 (divididas acima) e não se repetem,
    # senão a parcela de 100 ha seria tratada como a mesma área da T4-A de 40,8 ha
    chk('Planejar › no T4 livre vira parcela T4-F com 104 ha livres', 'parcela T4-F · 104 ha livres em T4' in t, t)
    T4=J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.querySelector('.g2c0')&&/^[▾▸]?\\s?T4\\s/.test(x.querySelector('.g2c0').innerText.trim()+' ')); return r?r.innerText.replace(/\\s+/g,' '):'';})()""")
    chk('T4 continua A conferir e a ocupação da soja (c4) continua na linha', 'A conferir' in (T4 or '') and J("!!document.querySelector('[role=row][data-rid=fora_c4]')"), T4)
    T2c=J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.querySelector('.g2c0')&&/^[▾▸]?\\s?T2\\s/.test(x.querySelector('.g2c0').innerText.trim()+' ')); return r?r.querySelector('.g2c0').innerText.replace(/\\s+/g,' '):'';})()""")
    chk('T2 planejado não oferece Planejar ›, só Dividir', 'Planejar' not in (T2c or 'Planejar') and 'Dividir' in T2c, T2c)
    rowbtn('T2 talhão inteiro','Dividir'); time.sleep(.3)   # o caminho do talhão já planejado é o Dividir (proposta T2-A/T2-B)
    setv('Área de T2-A em hectares','298')
    setv('Área de T2-B em hectares','50'); pt=panel()
    chk('Dividir T2 + 50 ha: "Excede em 50 ha"', 'Dividir T2 em parcelas' in pt and 'Excede em 50 ha' in pt, pt[:200])
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
