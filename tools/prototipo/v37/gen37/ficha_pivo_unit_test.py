# -*- coding: utf-8 -*-
"""Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.").
A ficha é a capacidade do equipamento de irrigação, registrada como está na ficha técnica (dados sintéticos), no detalhe do equipamento
(CD-03 › Bomba do Pivô 2) e aberta pela Irrigação (IR-01 › setor P2) com o mesmo componente e os mesmos dados. Fonte: dados.PIVO
(tempo de volta e lâmina a 100 %) + dados.FICHA_PIVO; vínculo pivô → talhão do cadastro (dados_cad.SISTEMA). A conta
lâmina = lâmina a 100 % × 100 ÷ percentímetro é só conferência (mostra a divergência; não corrige a ficha nem prescreve lâmina).
"21 h" fica como regime de operação (h/dia, fora do horário de ponta), sem outro uso.
Parte 1 (python, sem navegador): dados, vínculo, fonte única da vazão e a conferência com Decimal.
Parte 2 (páginas geradas, depois do build.py): o componente está no CD-03 e no IR-01, com as colunas da tabela e as ações de entrada.
Na base (9d4ff31) não existem FICHA_PIVO nem ficha_pivo.py: os casos falham.
Uso: python3 ficha_pivo_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, re, json, importlib
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
sys.dont_write_bytecode = True
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)
import dados as D, dados_cad as DC, dados_irrigacao as DI
FP = getattr(D, 'FICHA_PIVO', None) or {}
try: FPM = importlib.import_module('ficha_pivo')
except Exception as e: FPM = None; print('sem ficha_pivo.py:', e)
f = FP.get('a11') or {}
at = {a['id']: a for a in DC.ATIVOS}
chk('F1 a ficha é do equipamento de irrigação do cadastro (a11 · Bomba do Pivô 2, classe Irrigação) e é a do Pivô 2',
    bool(f) and at['a11']['classe'] == 'Irrigação' and f.get('pivo') == D.PIVO['id'] == 'Pivô 2' and set(FP) <= {a['id'] for a in DC.ATIVOS if a['classe'] == 'Irrigação'}, [list(FP), f.get('pivo')])
chk('F2 tempo de volta e lâmina a 100 % vêm da fonte atual (dados.PIVO: 9,0 h e 6,7 mm), sem cópia; a linha 100 % da tabela é a mesma',
    f.get('volta_100_h') == D.PIVO['volta_h'] and f.get('lamina_100_mm') == D.PIVO['lamina_100'] and bool(f.get('tabela'))
    and Decimal(str(f['tabela'][0][0])) == 100 and Decimal(str(f['tabela'][0][1])) == Decimal(str(D.PIVO['volta_h'])) and Decimal(str(f['tabela'][0][2])) == Decimal(str(D.PIVO['lamina_100'])), [f.get('volta_100_h'), f.get('lamina_100_mm'), (f.get('tabela') or [None])[0]])
tal = FPM.talhoes('a11') if FPM and hasattr(FPM, 'talhoes') else None
chk('F3 vínculo pivô → talhão do cadastro (CD-01: o talhão P2 é irrigado pela Bomba do Pivô 2) e o setor P2 da Irrigação',
    tal == ['P2'] and (FPM.dados_pagina().get('a11', {}).get('setor') if FPM and hasattr(FPM, 'dados_pagina') else None) == 'P2' and 'P2' in DI.seed()['setores'], tal)
sem = DI.seed(); p2 = sem['setores'].get('P2', {})
chk('F4 vazão com fonte única: a Irrigação (setor P2) e o cadastro da bomba (CD-03, m³/h) leem a vazão da ficha (166 L/s = 597,6 m³/h)',
    f.get('vazao_ls') == p2.get('vazao') == 166 and Decimal(str(at['a11']['vazao'])) == Decimal('597.6'), [f.get('vazao_ls'), p2.get('vazao'), at['a11'].get('vazao')])
conf = FPM.conferencia(f) if FPM and hasattr(FPM, 'conferencia') and f else []
by = {int(r['pct']): r for r in conf}
L100 = Decimal(str(D.PIVO['lamina_100']))
chk('F5 conta de conferência = lâmina a 100 % × 100 ÷ percentímetro (Decimal) em todas as linhas',
    len(conf) == len(f.get('tabela') or []) >= 8 and all(r['conta'] == L100 * 100 / Decimal(str(r['pct'])) for r in conf), [(r['pct'], r['conta']) for r in conf][:4])
chk('F6 DIVERGÊNCIA: 60 % na ficha = 11,0 mm × 11,17 mm pela conta → diverge −0,17 mm; as outras linhas conferem (40 %: 16,8 × 16,75, dentro da meia casa)',
    60 in by and not by[60]['ok'] and by[60]['lam'] == Decimal('11.0') and by[60]['dif'].quantize(Decimal('0.01')) == Decimal('-0.17')
    and 40 in by and by[40]['ok'] and all(r['ok'] for p, r in by.items() if p != 60), [(p, str(r['lam']), str(r['conta']), r['ok']) for p, r in by.items()])
chk('F7 "21 h" fica como regime de operação (h/dia, fora do horário de ponta) e não entra em conta nenhuma da ficha',
    f.get('regime_h') == 21 and 'fora do horário de ponta' in (f.get('regime_obs') or '') and FPM is not None
    and 'regime' not in (open(os.path.join(HERE, 'ficha_pivo.py'), encoding='utf-8').read().split('def conferencia', 1)[1].split('\ndef ', 1)[0]), [f.get('regime_h'), f.get('regime_obs')])
J = FPM.dados_pagina() if FPM and hasattr(FPM, 'dados_pagina') else {}
jf = J.get('a11') or {}
kv = {x['l']: x['v'] for x in jf.get('kv', [])}
chk('F8 campos da ficha para a tela, com a unidade junto do valor: identificação, fabricante e modelo, raio, área irrigada, vazão, pressão, tempo de volta e lâmina a 100 %, regime de operação, talhão',
    kv.get('Raio') == '505 m' and kv.get('Área irrigada') == '80 ha' and kv.get('Vazão') == '166 L/s · 597,6 m³/h' and kv.get('Pressão') == '32 mca'
    and kv.get('Tempo de volta a 100 %') == '9,0 h' and kv.get('Lâmina a 100 %') == '6,7 mm' and kv.get('Regime de operação') == '21 h/dia · fora do horário de ponta'
    and 'Pivô 2' in (kv.get('Identificação') or '') and 'sintétic' in (kv.get('Fabricante e modelo') or '') and (kv.get('Talhão') or '').startswith('P2'), kv)
lin = {r['pct']: r for r in jf.get('linhas', [])}
chk('F9 linha 60 % da tabela para a tela: "60 %", "15,0 h", "11,0 mm", "11,17 mm", "Diverge −0,17 mm"; e o resumo diz qual linha diverge',
    lin.get('60 %', {}).get('t') == '15,0 h' and lin.get('60 %', {}).get('l') == '11,0 mm' and lin.get('60 %', {}).get('c') == '11,17 mm'
    and lin.get('60 %', {}).get('conf') == 'Diverge −0,17 mm' and lin.get('100 %', {}).get('conf') == 'Confere'
    and '60 %' in (jf.get('resumo') or '') and '11,0 mm' in (jf.get('resumo') or '') and '11,17 mm' in (jf.get('resumo') or ''), [lin.get('60 %'), jf.get('resumo')])
nota = jf.get('nota') or ''
chk('F10 a ficha não prescreve lâmina: diz que é capacidade do equipamento e que a lâmina vem da política de água (PA-07 v3) e do responsável técnico',
    'capacidade do equipamento' in nota.lower() and D.POLITICA_AGUA['id'] in nota and 'responsável técnico' in nota and 'não prescreve' in nota.lower()
    and not any(k in jf for k in ('lamina_rec', 'prescricao', 'recomendada')), nota)
# ---- parte 2 · páginas geradas (build.py) ----
P = os.path.join(HERE, 'project')
pg = lambda n: open(os.path.join(P, n), encoding='utf-8').read() if os.path.exists(os.path.join(P, n)) else ''
cd3, ir1 = pg('CD-03.dc.html'), pg('IR-01.dc.html')
COLS = ['Percentímetro', 'Tempo de volta', 'Lâmina', 'Lâmina pela conta', 'Conferência']
def cols_de(html):
    m = re.search(r'const GRIDS = (\[.*?\]);\n', html, re.S)
    if not m: return None
    g = [x for x in json.loads(m.group(1)) if x['id'] == 'g_fpv']
    return [c['l'] for c in g[0]['cols']] if g else None
chk('F11 o mesmo componente (gaveta "Ficha do pivô" + tabela com filtro e ordenação, uma variável por coluna) está no CD-03 e no IR-01',
    all('aria-label="Ficha do pivô' in h and cols_de(h) == COLS for h in (cd3, ir1)), [cols_de(cd3), cols_de(ir1)])
chk('F12 entradas: no CD-03 a ação "Ficha do pivô ›" no detalhe do equipamento; no IR-01 a ação no painel do setor e o link #P2:ficha; cada uma leva à outra tela',
    "t:'Ficha do pivô ›'" in cd3 and "t:'Ficha do pivô'" in ir1 and ":ficha" in ir1 and 'ficha=' in cd3
    and 'CD-03.dc.html#ficha=' in ir1 and 'IR-01.dc.html#' in cd3, ['Ficha do pivô ›' in cd3, 'Ficha do pivô' in ir1])
chk('F13 ponto de leitura da água disponível no solo (CAD) do talhão nomeado: lê irrCadTxt (frente SOLO) quando existir; sem ela, na Irrigação diz que não há medição e no cadastro diz onde ler (sem afirmar "sem medição")',
    all('function fpvCad(' in h and "typeof irrCadTxt==='function'" in h and 'sem medição de água no solo neste talhão' in h and "'lida no setor '+f.setor+' da Irrigação" in h for h in (cd3, ir1)))
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
