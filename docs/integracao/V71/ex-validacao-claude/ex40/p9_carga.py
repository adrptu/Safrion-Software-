# -*- coding: utf-8 -*-
"""EX-40.5 (complemento) · no fluxo vigente, onde aparece "manutenção × produção": O.S. › Carga (PCP) e Manutenção › Ativos (executado)."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, G
sys.path.insert(0, G)
from comp_lib import troca_visao
s = S(1440, 1400); s.reset('Caio'); s.go('OS.dc.html', espera=1.6)
s.p('# O.S. › Carga (Caio · PCP, Santa Rita)'); s.p('visão: ' + str(troca_visao(s.J, 'carga'))); time.sleep(.9)
t = s.J("(()=>{const m=document.querySelector('[aria-label=\"Alocação de recursos na semana\"]'); return m?m.innerText:'SEM TABELA';})()") or ''
lin = [l for l in t.split('\n') if 'OM-0' in l or 'anuten' in l]
s.p('linhas com manutenção (OM-…/manutenção): ' + json.dumps(lin[:12], ensure_ascii=False))
conf = s.J("(document.body.innerText.match(/[^\\n]*(manutenção|OM-0233)[^\\n]*/g)||[]).slice(0,8)")
s.p('textos fora da tabela: ' + json.dumps(conf, ensure_ascii=False))
s.shot('p9_OS_carga.png')
s.reset('Ana'); s.go('MA.dc.html#vis=ativos', espera=1.8)
ag = s.J("(document.body.innerText.match(/[^\\n]*(OS-04\\d\\d)[^\\n]*/g)||[]).slice(0,8)")
s.p('\n# Manutenção › Ativos: menções a O.S. agrícolas: ' + json.dumps(ag, ensure_ascii=False))
s.p(f"erros JS: {s.errs()}")
s.fim('p9_carga.log')
