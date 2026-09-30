# -*- coding: utf-8 -*-
"""CD-04 · pessoas e equipes (15 verificações no Chrome): caldeira da OS-0424 (Paula), habilidades em múltipla escolha com a habilitação
exigida, habilitação vencida grava e marca 'Não alocável em O.S.', filtros rápidos por habilidade e 'Não alocáveis', estado calculado e
clicável, vigência do safrista, calendário herdado da equipe, 'Irrigante' e 'Solicitar acesso ao app' simulado no formulário."""
from cada_lib import T
import time, json
t=T(); J=t.J
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(1,3).join('/')")
def nomes(): return J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.querySelector('b').innerText)")
def help_(rot): return J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label[for]')].find(x=>x.innerText.trim()==={json.dumps(rot)}); return l?l.parentElement.innerText:'';}})()")
try:
    t.goto('CD-04.dc.html')
    t.chk('cabeçalho: estado calculado "2 não alocáveis · 1 a renovar em 30 dias" e primária "Cadastrar pessoa"',
          '2 não alocáveis · 1 a renovar em 30 dias' in t.header() and 'Cadastrar pessoa' in t.header() and not t.errs(), t.header()+' '+t.errs())
    p=t.rowtxt(0,'Paula') or ''
    t.chk('Paula é caldeira da equipe Campo 1 (OS-0424) com NR-31 válida; "Irrigante" no lugar de "Irrigacionista"',
          'Preparar calda (caldeiro)' in p and 'Campo 1' in p and 'NR-31 até 30/04/2027' in p and 'Irrigacionista' not in J("document.body.innerText")
          and 'Irrigantes 1' in J("document.body.innerText"), p)
    l=t.rowtxt(0,'Lucas') or ''
    t.chk('Lucas (safrista) com NR-31 vencida aparece "Não alocável em O.S." com o motivo e a vigência do contrato',
          'Não alocável em O.S.' in l and 'NR-31 vencida em 15/08/2026' in l and 'Safrista' in l and 'até 31/07/2027' in l, l)
    t.clk('Caldeiros 2'); a=nomes(); t.clk('Não alocáveis 2'); b=nomes(); t.clk('Todas 10'); c=conta()
    t.chk('filtros rápidos: Caldeiros → Paula e Nilton; Não alocáveis → Lucas e Beto; Todas → 10', a==['Paula','Nilton'] and b==['Lucas','Beto'] and c=='10/10', [a,b,c])
    t.clk('2 não alocáveis'); a=nomes(); ch=J("document.body.innerText.indexOf('Habilitação a resolver')>=0"); t.clk('Limpar filtros'); c=conta()
    t.chk('clicar no estado filtra quem precisa de ação (Marcos a renovar, Lucas, Beto) e "Limpar filtros" volta às 10',
          a==['Marcos','Lucas','Beto'] and ch and c=='10/10', [a,ch,c])
    t.openrow(0,'Lucas'); L=t.labels()
    t.chk('formulário: Nome → Equipe → Habilidades → validade da habilitação exigida → vínculo e vigência → calendário → custo com encargos; sem "Função"',
          L==['Nome','Equipe','Habilidades','Validade da NR-31','Vínculo','Admissão','Disponível até','Calendário de trabalho','Custo-hora com encargos','Acesso ao app','Situação'], L)
    t.fset('custo','40'); t.btn('Salvar'); time.sleep(.2); l=t.rowtxt(0,'Lucas') or ''; ts=t.toast()
    t.chk('salvar com NR-31 vencida grava (sem bloquear) e mantém "Não alocável em O.S." com aviso do efeito',
          not t.isopen() and 'R$ 40,00/h' in l and 'Não alocável em O.S.' in l and 'não alocável em O.S. até resolver NR-31 vencida em 15/08/2026' in ts, [l,ts,t.alerts()])
    t.openrow(0,'Lucas'); t.fset('v31','2027-08-15'); t.btn('Salvar'); time.sleep(.2); l=t.rowtxt(0,'Lucas') or ''
    t.chk('renovar a NR-31 libera o Lucas e o estado do cabeçalho é recalculado',
          'NR-31 até 15/08/2027' in l and 'Não alocável' not in l and '1 não alocável · 1 a renovar em 30 dias' in t.header(), [l,t.header()])
    t.openrow(0,'Rui'); h0=help_('Habilidades'); marca('Irrigar'); L=t.labels(); h1=help_('Habilidades')
    t.chk('marcar "Irrigar" faz aparecer a validade da NR-10 exigida (Rui não exigia nenhuma)',
          'Nenhuma habilitação exigida' in h0 and 'Validade da NR-10' in L and 'Exige NR-10 com validade' in h1, [h0,L,h1])
    t.cancel()
    t.openrow(0,'Beto'); he=help_('Equipe'); ops=t.fopts('acesso')
    t.chk('calendário herdado da equipe aparece no campo Equipe; acesso ao app oferece "Solicitar acesso ao app"',
          'Calendário da equipe: seg–sáb · 06–15h · 9 h/dia' in he and ops==['Sem login','Solicitar acesso ao app'] and t.fv('cal')=='Da equipe', [he,ops,t.fv('cal')])
    t.fset('acesso','Solicitar acesso ao app'); t.fset('cal','escala 6×2 · 8h'); t.btn('Salvar'); time.sleep(.2); b=t.rowtxt(0,'Beto') or ''; ts=t.toast()
    t.chk('"Solicitar acesso ao app" (simulado) grava o pedido e a exceção de calendário aparece na linha',
          'Acesso solicitado' in b and 'simulado' in b and 'calendário próprio: escala 6×2 · 8h' in b and 'pedido de acesso ao app enviado ao administrador (simulado)' in ts, [b,ts])
    t.openrow(0,'Ana'); acd=t.fdis('acesso'); t.cancel()
    t.chk('quem já tem login vê o acesso só em consulta', acd is True, acd)
    t.clk('Cadastrar pessoa')
    for k,v in [('nome','Rita'),('vinc','Safrista'),('adm','2026-09-20'),('custo','32')]: t.fset(k,v)
    marca('Preparar calda (caldeiro)'); t.btn('Salvar'); a=t.alerts()
    t.chk('safrista sem "Disponível até" é barrado no campo', 'Informe até quando o safrista fica disponível' in a, a)
    t.fset('ate','2027-03-31'); t.btn('Salvar'); time.sleep(.2); r=t.rowtxt(0,'Rita') or ''
    t.chk('caldeira nova sem NR-31 grava como "Não alocável em O.S. · NR-31 pendente" e entra no filtro Caldeiros (3)',
          not t.isopen() and 'Não alocável em O.S.' in r and 'NR-31 pendente' in r and 'Caldeiros 3' in J("document.body.innerText"), [r,t.alerts()])
    t.shot('cada_cd04.png')
    t.chk('nenhum erro de JS na jornada', not t.errs(), t.errs())
finally:
    t.fim()
