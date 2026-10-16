# -*- coding: utf-8 -*-
"""CD-04 · pessoas e equipes (15 verificações no Chrome): caldeira da OS-0424 (Paula), habilidades em múltipla escolha com a habilitação
exigida, habilitação vencida grava e marca 'Não alocável em O.S.', filtros rápidos por habilidade e 'Não alocáveis', estado calculado e
clicável, vigência do safrista, calendário herdado da equipe, 'Irrigante' e o acesso ao app só leitura (Configurações › Usuários e alçadas, CONF-01)."""
# TABELAS-FOCO (06/10/2026): vínculo | disponível até | habilitação | validade (vencida em vermelho) em colunas próprias; calendário e acesso no painel
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
# TAB-02 (16/10/2026, padrão comum): com filtro rápido a barra não mostra "x de y"; conta as linhas à vista e o total do chip "Todas N"
def conta(): return J("(()=>{const tb=document.querySelectorAll('[role=table]')[0]; const n=[...tb.querySelectorAll('[role=row]')].filter(r=>r.querySelector('[role=cell]')).length; const c=[...tb.closest('.g2caixa').querySelectorAll('[role=group] [aria-pressed]')].find(b=>/^Todas/.test(b.innerText.trim())); return n+'/'+(c?(c.innerText.match(/\\d+/)||[''])[0]:'');})()")
def nomes(): return J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.querySelector('b').innerText)")
def help_(rot): return J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label[for]')].find(x=>x.innerText.trim()==={json.dumps(rot)}); return l?l.parentElement.innerText:'';}})()")
try:
    t.goto('CD-04.dc.html')
    t.chk('cabeçalho: estado calculado "2 não alocáveis · 1 a renovar em 30 dias" e primária "Criar pessoa" no cabeçalho (BOT-01/03, 16/10)',
          '2 não alocáveis · 1 a renovar em 30 dias' in t.header() and 'Criar pessoa' in t.header() and not t.errs(), t.header()+' '+t.errs())
    # TABELAS-FOCO (06/10/2026): habilitação e validade em colunas próprias ("NR-31 | 30/04/2027"), o estado no chip da Situação
    p=t.rowtxt(0,'Paula') or ''
    t.chk('Paula é caldeira da equipe Campo 1 (OS-0424) com NR-31 válida; "Irrigante" no lugar de "Irrigacionista"',
          'Preparar calda (caldeiro)' in p and 'Campo 1' in p and 'NR-31 30/04/2027' in p and 'Alocável' in p and 'Irrigacionista' not in J("document.body.innerText")
          and 'Irrigantes (1)' in J("[...document.querySelectorAll('main select option')].map(o=>o.text).join(' | ')"), p)
    l=t.rowtxt(0,'Lucas') or ''
    t.chk('Lucas (safrista) com NR-31 vencida aparece "Não alocável em O.S." com o motivo e a vigência do contrato',
          'Não alocável em O.S.' in l and 'NR-31 15/08/2026' in l and 'Safrista 31/07/2027' in l, l)
    t.mainsel('cal'); a=nomes(); t.clk('A resolver'); b=nomes(); t.mainsel(''); b2=nomes(); t.clk('Todas'); c=conta()
    # PCM simplificado (S1): Otávio (p14) entra no cadastro; CONF-D04: Caio (p11); BEN-1: Igor e Marta (equipe e8) · 14 pessoas na v57
    t.chk('filtros do bloco: Função Caldeiros → Paula e Nilton; com A resolver → nenhum caldeiro; Todas → 15 (Caio da CONF-D04; Otávio da manutenção; Dora do comercial; Igor e Marta do beneficiamento)', a==['Paula','Nilton'] and b==[] and c=='15/15', [a,b,c])
    t.clk('A resolver'); a=nomes(); ch=J("(()=>{const b=[...document.querySelectorAll('main .g2caixa [role=group] button')].find(b=>b.innerText.trim().startsWith('A resolver')); return !!b&&b.getAttribute('aria-pressed')==='true';})()"); t.clk('Limpar filtros'); c=conta()
    t.chk('filtro rápido "A resolver" (no bloco) mostra quem precisa de ação (Marcos a renovar, Lucas, Beto) e "Limpar filtros" volta às 15',
          a==['Marcos','Lucas','Beto'] and b2==['Marcos','Lucas','Beto'] and ch and c=='15/15', [a,b2,ch,c])
    t.openrow(0,'Lucas'); L=t.labels()
    # 16/10/2026 (formulário só com o essencial): "Calendário de trabalho" da pessoa saiu (nenhuma tela o lia; vale o da equipe)
    t.chk('formulário: Nome → Equipe → Habilidades → validade da habilitação exigida → vínculo e vigência → custo com encargos; sem "Função" nem calendário próprio',
          L==['Nome','Equipe','Habilidades','Validade da NR-31','Vínculo','Admissão','Disponível até','Custo-hora com encargos','Situação'], L)   # acesso ao app saiu do formulário (CONF-01 P4, CONF-D05)
    t.fset('custo','40'); t.btn('Salvar'); time.sleep(.2); l=t.rowtxt(0,'Lucas') or ''; ts=t.toast()
    t.chk('salvar com NR-31 vencida grava (sem bloquear) e mantém "Não alocável em O.S." com aviso do efeito',
          not t.isopen() and 'R$ 40,00/h' in l and 'Não alocável em O.S.' in l and 'não alocável em O.S. até resolver NR-31 vencida em 15/08/2026' in ts, [l,ts,t.alerts()])
    t.openrow(0,'Lucas'); t.fset('v31','2027-08-15'); t.btn('Salvar'); time.sleep(.2); l=t.rowtxt(0,'Lucas') or ''
    t.chk('renovar a NR-31 libera o Lucas e o estado do cabeçalho é recalculado',
          'NR-31 15/08/2027' in l and 'Não alocável' not in l and '1 não alocável · 1 a renovar em 30 dias' in t.header(), [l,t.header()])
    t.openrow(0,'Rui'); h0=help_('Habilidades'); marca('Irrigar'); L=t.labels(); h1=help_('Habilidades')
    t.chk('marcar "Irrigar" faz aparecer a validade da NR-10 exigida (Rui não exigia nenhuma)',
          'Nenhuma habilitação exigida' in h0 and 'Validade da NR-10' in L and 'Exige NR-10 com validade' in h1, [h0,L,h1])
    t.cancel()
    # CONF-01 P4 (CONF-D05): o acesso ao app sai do formulário; o CD-04 só lê o estado de Configurações e leva a Usuários e alçadas para gerenciar.
    # Revisão TABR (09/10, A1): calendário e acesso ficam no painel da pessoa (não na linha).
    t.openrow(0,'Beto'); he=help_('Equipe'); og=t.dlg(); lk=t.J("!![...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.getAttribute('href')==='CF-01.dc.html#pessoa=Beto')")
    t.chk('calendário herdado da equipe aparece no campo Equipe; o acesso ao app é só leitura ("Sem acesso") com o link para gerenciar em Configurações',
          'Calendário da equipe: seg–sáb · 06–15h · 9 h/dia' in he and 'Acesso ao app: Sem acesso · gerenciar em Configurações › Usuários e alçadas' in og and lk and t.fv('cal') is None and t.fv('acesso') is None, [he,og[-250:],lk,t.fv('cal')])
    t.fset('custo','31'); t.btn('Salvar'); time.sleep(.2); ts=t.toast()
    t.openrow(0,'Beto'); b=t.fv('custo'); t.cancel()
    t.chk('a pessoa segue o calendário da equipe (sem campo próprio, 16/10) e salvar não envia pedido de acesso', b=='31' and 'pedido de acesso' not in ts, [b,ts])
    t.openrow(0,'Ana'); og=t.dlg(); t.cancel()
    t.chk('quem tem acesso vê "Acesso ao app: Ativo desde 28/06/2026" só em consulta, com o link para Configurações', 'Acesso ao app: Ativo desde 28/06/2026' in og and t.fv('acesso') is None, og[-250:])
    t.clk('Criar pessoa')
    for k,v in [('nome','Rita'),('vinc','Safrista'),('adm','2026-09-20'),('custo','32')]: t.fset(k,v)
    marca('Preparar calda (caldeiro)'); t.btn('Salvar'); a=t.alerts()
    t.chk('safrista sem "Disponível até" é barrado no campo', 'Informe até quando o safrista fica disponível' in a, a)
    t.fset('ate','2027-03-31'); t.btn('Salvar'); time.sleep(.2); r=t.rowtxt(0,'Rita') or ''
    t.chk('caldeira nova sem NR-31 grava como "Não alocável em O.S. · NR-31 pendente" e entra no filtro Caldeiros (3)',
          not t.isopen() and 'Não alocável em O.S.' in r and 'NR-31 pendente' in r and 'Caldeiros (3)' in J("[...document.querySelectorAll('main select option')].map(o=>o.text).join(' | ')"), [r,t.alerts()])
    t.shot('cada_cd04.png')
    t.chk('nenhum erro de JS na jornada', not t.errs(), t.errs())
finally:
    t.fim()
