# -*- coding: utf-8 -*-
"""Correções do verificador · Estoque, parte 2 (EST.dc.html no Chrome headless, 1440×1000, cenário limpo, ≤ 15 verificações, < 50 s):
recebimento conferido sem rolagem (etapas 1 e 4), trilha de movimentos com documento da contagem e do ajuste, confirmação do app
só com o que foi entregue, consumo do app com unidade e quantidade, chip "Aguardando sinal" inteiro e que some quando o sinal volta."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

OVF = "[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).map(x=>[x.parentElement.scrollWidth,x.parentElement.clientWidth])"
INTEIRO = """((ts,t)=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(x=>r.innerText.indexOf(x)>=0)); if(!r) return 'sem linha';
  const e=[...r.querySelectorAll('button,span')].find(x=>x.innerText.trim()===t); if(!e) return 'sem '+t; const sc=r.closest('[role=table]').parentElement;
  const den=()=>{ const box=sc.getBoundingClientRect(), b=e.getBoundingClientRect(); return b.width>0&&b.left>=box.left-0.5&&b.right<=box.right+0.5; };
  sc.scrollLeft=0; if(den()) return true;   // à vista sem rolar a grade
  const f=e.closest('button'); if(f){ f.focus(); f.dispatchEvent(new FocusEvent('focusin',{bubbles:true})); return den()?'teclado':false; }   // ação: o foco do teclado traz inteira para a caixa (focusin despachado: sem janela ativa o Chrome não o dispara)
  e.scrollIntoView({block:'nearest',inline:'nearest'}); return den()?'rolando':false; })"""
# linhas da trilha com o tipo do movimento: [texto da linha]
MOV = "(t=>[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.innerText.indexOf(t)>=0).map(r=>r.innerText.replace(/\\s+/g,' ')))"


# TABELAS-FOCO (5983172395) item 6: com uma variável por coluna a grade pode rolar dentro da própria caixa; a página não rola
def cabe(E): return bool(E.J("document.documentElement.scrollWidth<=innerWidth+1"))
def inteiro(E, ts, t): return E.J(f"({INTEIRO})({ts!r},{t!r})".replace("'", '"')) in (True, 'teclado', 'rolando')
def movs(E, t): return E.J(f"({MOV})({t!r})".replace("'", '"'))


E = Est()
try:
    E.abrir()
    # 1 · NF 4533 conferida com validade: a grade da etapa 1 continua cabendo, chips inteiros
    E.clk('Conferir NF 4533'); E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '20000'); E.setv('fx_g_rec_quar', '0'); E.setv('fx_g_rec_val', '05/2027'); E.salvar()
    print('etapa 1:', E.J(OVF), E.rowtxt('NF 4533'))
    E.ok(cabe(E) and inteiro(E, ['NF 4533'], 'Conferido') and inteiro(E, ['NF 4501'], 'Aguarda laudo'), 'etapa 1 após conferir NF 4533: página sem rolagem, "Conferido" e "Aguarda laudo" inteiros na grade', E.J(OVF))
    E.etapa(4); print('etapa 4:', E.J(OVF))
    # os dois lotes sob o item e, com a grade no início, Item › lote e Disponível à vista (não basta a página não rolar)
    l4 = E.J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const sc=t.parentElement; sc.scrollLeft=0; const R=sc.getBoundingClientRect();
      const hs=[...t.querySelectorAll('[role=columnheader]')].filter(h=>h.getBoundingClientRect().right<=R.right+0.5).map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
      const rs=[...t.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()); const i=rs.findIndex(x=>/^[▾▸]?\\s*Semente de soja 58 W/.test(x));
      return {vis:hs, kids:rs.slice(i+1,i+3).map(x=>x.split(' ')[0])};})()""")
    E.ok(cabe(E) and sorted(l4['kids']) == ['S58-0801', 'S58-0926'] and 'ITEM › LOTE' in l4['vis'] and 'DISPONÍVEL' in l4['vis'],
         'etapa 4 com Semente de soja 58 W em 2 lotes (S58-0801 e S58-0926 sob o item); Item › lote e Disponível à vista sem rolar a grade', l4)
    # 2 · contagem sem diferença: documento e contador na trilha
    E.etapa(5); E.clk('Contar INV-2611'); E.setv('fx_g_cnt_contador', 'Paula (almoxarife)'); E.setv('fx_g_cnt_cont', '1200'); E.salvar(); print('toast:', E.toast())  # revisão CONF F6: o contador não tem mais valor padrão (era o 1º da lista fixa); a pessoa escolhe quem contou
    E.rowbtn('INV-2609', 'Aprovar ajuste'); print('toast:', E.toast())
    E.etapa(6); c0, a0 = movs(E, 'Contagem sem diferença'), movs(E, 'Ajuste de inventário'); print(' ', c0, a0)
    E.ok(len(c0) == 1 and 'INV-2611' in c0[0] and 'Paula (almoxarife)' in c0[0], 'contagem sem diferença na trilha com INV-2611 e o contador', c0)
    E.ok(len(a0) == 1 and 'INV-2609' in a0[0] and 'AJ-71' in a0[0] and '−600 kg' in a0[0], 'ajuste de inventário na trilha com INV-2609 · AJ-71 e −600 kg', a0)
    # 3 · OS-0430 liberada; só Glifosato entregue pela tela; o app confirma: a trilha mostra só o Glifosato
    E.mudar("return cenLiberar(c,'OS-0430');"); RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')")
    E.J("localStorage.setItem('safrion.perfilDemo','Rui')")   # CTL-3 (revisão, achado 4): a entrega grava o perfil de quem entrega
    E.abrir(); E.etapa(2); E.row(RQ, 'Glifosato 480'); E.salvar(); print('toast:', E.toast())
    print('app:', E.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');"))
    E.abrir(); E.etapa(6); r = movs(E, 'Recebimento confirmado no app'); print(' ', r)
    E.ok(len(r) == 1 and 'Glifosato 480' in r[0] and '320 L' in r[0] and '2,4-D' not in r[0] and 'Óleo mineral' not in r[0], 'confirmação do app lista só o Glifosato 480 (320 L) entregue', r)
    # 4 · entrega dos outros 2 itens e turno de 5 ha fechado sem sinal: consumo com unidade e chip "Aguardando sinal" inteiro
    E.mudar(f"cenEntregar(c,'{RQ}','2,4-D 806',160,'Marcos','Rui'); return cenEntregar(c,'{RQ}','Óleo mineral',80,'Marcos','Rui');")
    print('app:', E.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))   # CTL-2 · B: o turno exige o recebimento confirmado
    E.abrir(); E.etapa(6); r = movs(E, 'Consumo apontado no app'); k = E.k(); print(' ', r, '|', k)
    E.ok(len(r) == 1 and all(x in r[0] for x in ('Glifosato 480', '10 L', '2,4-D 806', '5 L', 'Óleo mineral', '2,5 L')) and 'Glifosato 480 10,' not in r[0],
         'consumo do app: cada item com quantidade e unidade (10 L, 5 L, 2,5 L) na coluna Quantidade', r)
    E.ok('Aguardando sinal' in r[0] and '1 aguardando sinal do app' in k and cabe(E) and inteiro(E, ['Consumo apontado no app'], 'Aguardando sinal'),
         'sem sinal: chip "Aguardando sinal" inteiro, grade sem rolagem, faixa com 1 aguardando', [k, E.J(OVF)])
    E.shot('est_fix_e6.png')
    # 5 · o sinal volta: o apontamento é enviado e o consumo deixa de aguardar
    print('sinal:', E.mudar("return cenSinal(c,true);")); E.abrir(); E.etapa(6); r = movs(E, 'Consumo apontado no app'); k = E.k(); print(' ', r, '|', k)
    E.ok('Aguardando sinal' not in r[0] and '0 aguardando sinal do app' in k, 'sinal de volta: consumo sem "Aguardando sinal" e faixa com 0 aguardando', [r, k])
    # 6 · novo turno sem sinal: só o consumo novo aguarda; o já enviado continua enviado
    print('app:', E.mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,2,0.5);"))
    E.abrir(); E.etapa(6); r = movs(E, 'Consumo apontado no app'); k = E.k(); print(' ', r, '|', k)
    E.ok(len(r) == 2 and 'Aguardando sinal' in r[0] and 'Aguardando sinal' not in r[1] and '1 aguardando sinal do app' in k and '4 L' in r[0],
         'segundo turno sem sinal: só o consumo novo (4 L de Glifosato) aguarda; o anterior segue enviado', [r, k])
    q = movs(E, 'Entrega'); E.ok(q and all('Rui (almoxarife)' in x for x in q), 'entregas na trilha por "Rui (almoxarife)", quem entregou (perfil Rui na tela; Rui nas chamadas diretas), o mesmo papel do contador', q[:1])
    er = E.erros(); E.ok(not er, 'sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
