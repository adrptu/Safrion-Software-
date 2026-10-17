"""Alvos de toque a 390 px contra 48 px (pedido l.67), relidos do bruto M5 da avaliação do Claude (6c03d7e). Só leitura.
Uso: python3 -I -B alvos48.py <pasta reproducao/ da avaliação>
O bruto guarda, por grupo, n, o menor lado e quantos ficam abaixo de 44; e a lista inteira só de ferramentas, zoom e fechar.
Então a contagem abaixo de 48 é um mínimo garantido, e o máximo supõe que o grupo inteiro tem o tamanho do menor.
"""
import json, sys, os
m = json.load(open(os.path.join(sys.argv[1], 'repro_mapa.json'), encoding='utf-8'))['medidas']
m5 = [v for k, v in m.items() if k.startswith('M5 ')][0]['390px']
tot = minimo = maximo = 0
print(f"{'grupo':14} {'n':>3} {'menor lado':>10} {'<44':>4} {'<48 mín.':>9} {'<48 máx.':>9}")
for g, r in m5['resumo'].items():
    n = r['n']; men = r['menor']
    if not n: continue
    lst = m5.get(g)
    if isinstance(lst, list):
        b48 = sum(1 for x in lst if min(x['w'], x['h']) < 48); mn = mx = b48
    else:
        abaixo44 = r['abaixo_do_limite']
        mn = max(abaixo44, 1 if men < 48 else 0); mx = n if men < 48 else 0
    tot += n; minimo += mn; maximo += mx
    print(f"{g:14} {n:3} {men:10} {r['abaixo_do_limite']:4} {mn:9} {mx:9}")
print(f"\nTOTAL {tot} controles medidos a 390 px (toque): abaixo de 44 = {sum(r['abaixo_do_limite'] for r in m5['resumo'].values())}; abaixo de 48 = de {minimo} a {maximo}")
print('Fora desta conta: o próprio talhão como alvo (não medido no M5).')
