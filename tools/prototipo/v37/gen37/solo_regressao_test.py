# -*- coding: utf-8 -*-
"""Análise de solo · regressão dos dois defeitos da base que o SOLO-01 corrige (sem navegador).
D1 (FX-002, D-22): a OS-0502 dizia "Calagem pela análise de solo", mas a dose dela (2 t/ha) é a dose fixa do plano MAMAO-IMP;
   sem laudo usado, a origem não pode citar a análise.
D2 (A4): dados_carencia._produtos() não lia dados_cad.ITENS_NOVOS; um item cadastrado fora dos planos (o Calcário dolomítico,
   grupo Corretivos) ficava fora do registro legal e a O.S. dele contava como agrotóxico sem registro, sem nunca liberar.
Uso: SAFRION_DADOS=sintetico python3 solo_regressao_test.py [pasta gen37]   (sem pasta: esta). Na base ecc8b00 os dois falham."""
import os, sys
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
GEN = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GEN); os.chdir(GEN)
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:400]), flush=True)

import dados_lagoa_safra as DLS, dados_cad as DC, dados_carencia as DCR
orig = ' · '.join(DLS.ORIG.get('OS-0502', []))
ok('D1 OS-0502: a origem diz a dose do plano, sem citar a análise de solo (nenhum laudo foi usado)',
   'análise' not in orig.lower() and 'dose do plano' in orig, orig)
pr = DCR._produtos()
for n, x in DC.ITENS_NOVOS.items():
    p = pr.get(n)
    ok(f'D2 {n} ({x["grupo"]}) está no registro legal com o grupo declarado e fora da trava de agrotóxico',
       p is not None and p['classe'] == x['grupo'] and p['defn'] is False, p)
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
