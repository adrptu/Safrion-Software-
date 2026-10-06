# -*- coding: utf-8 -*-
"""CD-03 · máquinas, instalações e conjuntos (14 verificações no Chrome): estado calculado e clicável, condição técnica só leitura
vinda da Manutenção com 'Ver ordens afetadas', classe primeiro com capacidade condicional, custo por hora com fonte, horímetro,
bloco Conjuntos com substituto, potência insuficiente barrada no campo e conjunto montado."""
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def conta(): return J("(document.body.innerText.match(/(\\d+) de 15/)||[])[1]||''")
try:
    t.goto('CD-03.dc.html')
    t.chk('cabeçalho: estado calculado "1 máquina em manutenção · 2 calibrações a resolver" e primária "Cadastrar máquina ou instalação"',
          '1 máquina em manutenção · 2 calibrações a resolver' in t.header() and 'Cadastrar máquina ou instalação' in t.bloco() and not t.errs(), t.header()+' '+t.errs())
    r=t.rowtxt(0,'Trator T1') or ''; href=J(f"(()=>{{const r={t.ROW(0,'Trator T1')}; const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.indexOf('Ver ordens afetadas')>=0); return a?a.getAttribute('href'):null;}})()")
    fx=J("(document.querySelector('.cadx-faixa')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    t.chk('Trator T1: linha "Em manutenção" com "Ver ordens afetadas" → OS.dc.html; faixa de atenção com "OM-0233 · retorno previsto 24/09"',
          'Em manutenção' in r and 'OM-0233' in fx and 'retorno previsto 24/09' in fx and href=='OS.dc.html', [r,fx,href])
    t.clk('A resolver'); time.sleep(.2); n1=conta(); vis=[x for x in ('Trator T1','Máquina TSI','Bomba do Pivô 2','Trator 02') if t.rowtxt(0,x)]
    t.clk('Limpar filtros'); n2=conta()
    t.chk('filtro rápido "A resolver" (no bloco) filtra as exceções (T1, TSI vencida, bomba a aferir) e "Limpar filtros" volta às 15',
          n1=='3' and vis==['Trator T1','Máquina TSI','Bomba do Pivô 2'] and n2=='15', [n1,vis,n2])
    t.openrow(0,'Trator T1'); L=t.labels(); orig=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'|'+a.getAttribute('href'))")
    t.chk('formulário do T1: condição técnica só leitura vinda da OM-0233, classe fixa, origem "Ver ordens afetadas" e sem "Valor do ativo"',
          t.fdis('cond_t') and 'Em manutenção · OM-0233' in (t.fv('cond_t') or '') and t.fdis('classe') and 'Valor do ativo' not in L
          and any(o.startswith('Ver ordens afetadas · OS-0420 e OS-0431') and o.endswith('|OS.dc.html') for o in orig), [t.fv('cond_t'),L,orig])
    t.cancel()
    t.openrow(0,'Trator 02'); t.fset('cont_tr','100'); t.btn('Salvar'); a=t.alerts()
    t.chk('horímetro menor que a última leitura é barrado no campo', 'A última leitura foi 2.988 h' in a, a)
    t.cancel()
    # cadastro novo: classe primeiro, capacidade condicional
    t.clk('Cadastrar máquina ou instalação'); L0=t.labels()
    t.chk('novo cadastro: a classe é o primeiro campo e Trator abre só a potência',
          L0[0]=='Classe' and 'Potência' in L0 and 'Largura da barra' not in L0 and 'Linhas' not in L0 and 'Custo por hora' in L0, L0)
    t.fset('classe','Plantadeira'); t.fset('linhas_pl','20'); t.fset('esp_pl','0,45'); lv=t.fv('larg_pl')
    t.chk('Plantadeira: linhas × espaçamento calcula a largura de trabalho (20 × 0,45 = 9 m) e marca "Exige calibração"',
          lv=='9' and t.fv('exige')=='Sim' and 'Potência' not in t.labels(), [lv,t.fv('exige'),t.labels()])
    t.fset('classe','Pulverizador'); L1=t.labels()
    t.chk('Pulverizador abre largura da barra, tanque útil e potência mínima do trator',
          'Largura da barra' in L1 and 'Tanque útil' in L1 and 'Potência mínima do trator' in L1 and 'Linhas' not in L1, L1)
    for k,v in [('nome','Pulverizador PJ-2500'),('barra_pv','30'),('tanque_pv','2500'),('preq_pv','90'),('cont_pv','0'),('interv','90')]: t.fset(k,v)
    t.btn('Salvar'); a=t.alerts()
    t.fset('custo_h','90'); t.fset('custo_f','Tabela de referência'); t.btn('Salvar'); time.sleep(.2)
    r=t.rowtxt(0,'Pulverizador PJ-2500') or ''; op=t.isopen(); t.openrow(0,'Pulverizador PJ-2500'); cf=t.fv('custo_f'); t.cancel()
    # TABELAS-FOCO (06/10/2026): tanque em Capacidade (2.500 L) e barra em Largura de trabalho (30 m), colunas próprias
    t.chk('sem custo por hora o cadastro é barrado no campo; com custo e fonte grava, a linha mostra barra, tanque e R$/h e o painel a fonte',
          'Informe o custo por hora' in a and not op and '2.500 L 30 m' in r and 'R$ 90,00/h' in r and cf=='Tabela de referência', [a,r,cf,t.alerts()])
    t.chk('estado do cabeçalho é recalculado (nova máquina sem calibração: 3 a resolver)', '1 máquina em manutenção · 3 calibrações a resolver' in t.header(), t.header())
    # conjuntos
    t.aba('Conjuntos'); k2=t.card('Trator T1 + Plantadeira 24 linhas') or ''
    t.chk('conjunto do T1 fica Indisponível pela manutenção e sugere o substituto Trator 02 (190 cv)',
          'Indisponível' in k2 and 'Trator T1 em manutenção' in k2 and 'substituto: Trator 02 (190 cv)' in k2 and 'Carlos' in k2, k2)
    t.clk('Montar conjunto'); t.fset('maq','Trator 03'); t.fset('impl','Plantadeira 24 linhas'); marca('Plantio'); pc=t.fv('pot_c'); t.btn('Salvar'); a=t.alerts()
    t.chk('Montar conjunto: Trator 03 (110 cv) com a plantadeira (exige 140 cv) dá erro no campo da máquina',
          'Trator 03 tem 110 cv; Plantadeira 24 linhas exige 140 cv' in a and 'abaixo dos 140 cv' in (pc or ''), [a,pc])
    t.fset('maq','Trator 02'); t.btn('Salvar'); time.sleep(.2); r=t.card('Trator 02 + Plantadeira 24 linhas') or ''
    t.chk('com o Trator 02 o conjunto é montado: largura 12 m herdada, Disponível, Carlos alocável e sem rendimento',
          not t.isopen() and '12 m' in r and 'Disponível' in r and 'Carlos' in r and 'sem rendimento' in r.lower() and 'Conjunto montado' in t.toast(), [r,t.toast(),t.alerts()])
    t.shot('cada_cd03.png')
    t.chk('nenhum erro de JS na jornada', not t.errs(), t.errs())
finally:
    t.fim()
