# -*- coding: utf-8 -*-
"""EX-26 (complemento) · capacidade por mês no Planejar safra (passo Operações), cargas de saída (EXPED) e desvio da colheita (COLH) · executado."""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, OUT
s = S(1440, 1400); s.reset('Ana')
s.go('SAF.dc.html#saf=S2627&passo=operacoes', espera=2.5); time.sleep(1.0)
t = s.body(); open(os.path.join(OUT, 'ex26', 'SAF_operacoes.txt'), 'w', encoding='utf-8').write(t)
cap = re.findall(r'[^\n]*(?:[Cc]apacidade|[Oo]cupa|[Dd]éficit|[Nn]ecessárias)[^\n]*', t)
s.p('# SAF › Operações e recursos (S2627): linhas com capacidade/ocupação/déficit'); s.p(json.dumps(cap[:12], ensure_ascii=False))
ab = s.J("(()=>{const b=[...document.querySelectorAll('button,summary,[role=button]')].find(e=>e.getClientRects().length&&/Capacidade por mês/.test(e.innerText)); if(!b) return 'sem'; b.click(); return 'ok';})()"); time.sleep(.9)
t2 = s.body(); i = t2.find('Capacidade por mês')
s.p(f'  aberto ({ab}): ' + re.sub(r'\n+', ' · ', t2[i:i+1500]))
s.go('EXPED.dc.html', espera=2.0); time.sleep(.6)
t = s.body(); open(os.path.join(OUT, 'ex26', 'EXPED.txt'), 'w', encoding='utf-8').write(t)
s.p('\n# EXPED (texto, 900 c.): ' + re.sub(r'\n+', ' · ', t[t.find('Expedição'):])[:900])
s.p(f"erros JS: {s.errs()}")
s.fim('p13_ex26_extra.log')
