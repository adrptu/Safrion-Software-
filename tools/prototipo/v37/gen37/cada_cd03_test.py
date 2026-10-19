# -*- coding: utf-8 -*-
"""CD-03 · máquinas, instalações e conjuntos (14 verificações no Chrome): estado calculado e clicável, condição técnica só leitura
vinda da Manutenção com 'Ver ordens afetadas', classe primeiro com capacidade condicional, custo por hora com fonte, horímetro,
bloco Conjuntos com substituto, potência insuficiente barrada no campo e conjunto montado."""
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
# TAB-02 (16/10/2026, padrão comum): com filtro rápido a barra não mostra "x de 15"; conta as linhas de máquina à vista na tabela
def conta(): return str(J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].filter(r=>r.querySelector('[role=cell]')).length"))
try:
    t.goto('CD-03.dc.html')
    t.chk('cabeçalho: estado calculado "1 máquina bloqueada · 2 calibrações a resolver" (condição única, PCM S3) e primária "Criar máquina ou instalação" no cabeçalho (BOT-01/03, 16/10)',
          '1 máquina bloqueada · 2 calibrações a resolver' in t.header() and 'Criar máquina ou instalação' in t.header() and not t.errs(), t.header()+' '+t.errs())
    r=t.rowtxt(0,'Trator T1') or ''; href=J(f"(()=>{{const r={t.ROW(0,'Trator T1')}; const a=r&&[...r.querySelectorAll('a')].find(a=>a.innerText.indexOf('Ver ordens afetadas')>=0); return a?a.getAttribute('href'):null;}})()")
    # 16/10/2026 (padrão comum, TAB-06): sem faixa de atenção; o motivo e o retorno previsto ficam na dica do selo da linha
    fx=J(f"(()=>{{const r={t.ROW(0,'Trator T1')}; const c=r&&[...r.querySelectorAll('[data-dica]')].find(x=>x.innerText.indexOf('Bloqueado')>=0); return c?c.getAttribute('data-dica'):'';}})()") or ''
    t.chk('Trator T1: linha "Bloqueado" (condição única da Manutenção) com "Ver ordens afetadas" → OS.dc.html; o selo diz "OM-0233 · … retorno previsto 24/09" na dica',
          'Bloqueado' in r and 'OM-0233' in fx and 'retorno previsto 24/09' in fx and href=='OS.dc.html', [r,fx,href])
    t.clk('A resolver'); time.sleep(.2); n1=conta(); vis=[x for x in ('Trator T1','Máquina TSI','Bomba do Pivô 2','Trator 02') if t.rowtxt(0,x)]
    t.clk('Limpar filtros'); n2=conta()
    t.chk('filtro rápido "A resolver" (no bloco) filtra as exceções (T1, TSI vencida, bomba a aferir) e "Limpar filtros" volta às 16 (ATIVO-UNICO, 18/10: o Comboio CB-01 entrou no cadastro)',
          n1=='3' and vis==['Trator T1','Máquina TSI','Bomba do Pivô 2'] and n2=='16', [n1,vis,n2])
    t.openrow(0,'Trator T1'); L=t.labels(); orig=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'|'+a.getAttribute('href'))")
    # 16/10/2026 (formulário só com o essencial): "Responsável técnico" (só leitura, da Manutenção) saiu do cadastro; segue na Manutenção
    t.chk('formulário do T1: condição técnica só leitura, vinda da Manutenção (OM-0233), classe fixa, origem "Ver ordens afetadas", sem "Valor do ativo" e sem "Responsável técnico"',
          t.fdis('cond_t') and 'Bloqueado · OM-0233' in (t.fv('cond_t') or '') and 'Responsável técnico' not in L and t.fdis('classe') and 'Valor do ativo' not in L
          and any(o.startswith('Ver ordens afetadas · OS-0420 e OS-0431') and o.endswith('|OS.dc.html') for o in orig), [t.fv('cond_t'),L,orig])
    t.cancel()
    t.openrow(0,'Trator 02'); hv=t.fv('cont_tr'); hd=t.fdis('cont_tr')
    t.chk('leitura do horímetro só leitura no CD-03, lida da Manutenção (2988 h); a decisão de leitura e troca de contador é lá (PCM S3, AC-PCM-15)', hd and hv in ('2988','2.988'), [hv,hd])
    t.cancel()
    # cadastro novo: classe primeiro, capacidade condicional
    t.clk('Criar máquina ou instalação'); L0=t.labels()
    t.chk('novo cadastro: a classe é o primeiro campo e Trator abre só a potência',
          L0[0]=='Classe' and 'Potência' in L0 and 'Largura da barra' not in L0 and 'Linhas' not in L0 and 'Custo R$/h da máquina' in L0, L0)
    t.fset('classe','Plantadeira'); t.fset('linhas_pl','20'); t.fset('esp_pl','0,45'); lv=t.fv('larg_pl')
    t.chk('Plantadeira: linhas × espaçamento calcula a largura de trabalho (20 × 0,45 = 9 m) e marca "Exige calibração"',
          lv=='9' and t.fv('exige')=='Sim' and 'Potência' not in t.labels(), [lv,t.fv('exige'),t.labels()])
    t.fset('classe','Pulverizador'); L1=t.labels()
    t.chk('Pulverizador abre largura da barra, tanque útil e potência mínima do trator',
          'Largura da barra' in L1 and 'Tanque útil' in L1 and 'Potência mínima do trator' in L1 and 'Linhas' not in L1, L1)
    for k,v in [('nome','Pulverizador PJ-2500'),('barra_pv','30'),('tanque_pv','2500'),('preq_pv','90'),('cont_pv','0'),('interv','90')]: t.fset(k,v)
    t.btn('Salvar'); a=t.alerts()
    t.fset('custo_h','90'); t.fset('custo_f','Tabela de referência'); t.btn('Salvar'); time.sleep(.2)
    r=t.rowtxt(0,'Pulverizador PJ-2500') or ''; op=t.isopen(); t.openrow(0,'Pulverizador PJ-2500'); cf=t.fv('custo_f'); tq=t.fv('tanque_pv'); br=t.fv('barra_pv'); t.cancel()
    # TABELAS-FOCO (06/10/2026): uma variável por coluna. Revisão TABR (09/10/2026, A1/A4): tanque e barra no painel da máquina (a capacidade
    # muda de grandeza com a classe e só tem coluna com o filtro de Classe)
    t.chk('sem custo por hora o cadastro é barrado no campo; com custo e fonte grava, a linha mostra R$/h e o painel barra, tanque e a fonte',
          'Informe o custo por hora' in a and not op and tq in ('2500','2.500') and br=='30' and 'R$ 90,00/h' in r and cf=='Tabela de referência', [a,r,tq,br,cf,t.alerts()])
    t.chk('estado do cabeçalho é recalculado (nova máquina sem calibração: 3 a resolver)', '1 máquina bloqueada · 3 calibrações a resolver' in t.header(), t.header())
    # conjuntos
    t.aba('Conjuntos'); k2=t.card('Trator T1 + Plantadeira 24 linhas') or ''
    t.chk('conjunto do T1 fica Indisponível pela manutenção e sugere o substituto Trator 02 (190 cv)',
          'Indisponível' in k2 and 'Trator T1 bloqueado' in k2 and 'substituto: Trator 02 (190 cv)' in k2 and 'Carlos' in k2, k2)
    t.clk('Criar conjunto'); t.fset('maq','Trator 03'); t.fset('impl','Plantadeira 24 linhas'); marca('Plantio'); pc=t.fv('pot_c'); t.btn('Salvar'); a=t.alerts()
    t.chk('Criar conjunto (BOT-03, antes "Montar conjunto"): Trator 03 (110 cv) com a plantadeira (exige 140 cv) dá erro no campo da máquina',
          'Trator 03 tem 110 cv; Plantadeira 24 linhas exige 140 cv' in a and 'abaixo dos 140 cv' in (pc or ''), [a,pc])
    t.fset('maq','Trator 02'); t.btn('Salvar'); time.sleep(.2); r=t.card('Trator 02 + Plantadeira 24 linhas') or ''
    # 16/10/2026: o conjunto é linha da grade do motor; a Situação tem um estado (Sem rendimento, com o próximo passo), e não mais "Disponível" no
    # rodapé do cartão ao lado do selo
    t.chk('com o Trator 02 o conjunto é montado: largura 12 m herdada, máquinas disponíveis, Carlos alocável e sem rendimento',
          not t.isopen() and '12 m' in r and 'Indisponível' not in r and 'Carlos' in r and 'sem rendimento' in r.lower() and 'Conjunto montado' in t.toast(), [r,t.toast(),t.alerts()])
    t.shot('cada_cd03.png')
    t.chk('nenhum erro de JS na jornada', not t.errs(), t.errs())
finally:
    t.fim()
