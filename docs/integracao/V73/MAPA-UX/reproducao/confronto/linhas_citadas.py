"""Confere, na fonte vigente, as linhas citadas pelas duas avaliações (Claude 6c03d7e e Codex b39dccb).

Uso: python3 -I -B linhas_citadas.py <G>   (G = tools/prototipo/v37/gen37 de 47ccc1d; os arquivos do mapa
são iguais aos de b989864). Para cada citação, procura o token esperado (regex) nas linhas citadas e imprime
OK com a primeira linha que casa, ou FALHA. Só leitura.
"""
import re, sys, os

G = sys.argv[1]
I = 'areas/inicio.py'
CF = 'areas/cad_fazendas.py'
# (quem, item, arquivo, linha_ini, linha_fim, regex esperado)
CIT = [
 # ---- Codex (avaliacao-codex.md, b39dccb) ----
 ('codex','D1',I,631,646,r"role','img'|role.{0,6}img"),
 ('codex','D1',I,631,646,r"pv-fill"),
 ('codex','D2',I,1411,1411,r"role=\"button\"|role=\\\"button|tabIndex"),
 ('codex','D2',I,1434,1434,r'role="img"'),
 ('codex','D3',I,632,632,r"mouseenter"),
 ('codex','D4',I,1126,1126,r"scale\("),
 ('codex','D5',I,1191,1191,r"has_full=!v\.map_lg"),
 ('codex','D6',I,1101,1102,r"FAZ=\(faz0==='Lagoa Grande'\)"),
 ('codex','D7',I,1016,1016,r"AG-06"),
 ('codex','D7',I,1127,1127,r"'Ver histórico','AG-06"),
 ('codex','D8',I,1074,1074,r"Nova O\.S\. neste talhão',\{h:'OS\.dc\.html'"),
 ('codex','D8',I,1127,1127,r"'Abrir ordens','OS\.dc\.html'"),
 ('codex','D9',I,347,347,r"."),
 ('codex','D9',I,861,865,r"Talhão"),
 ('codex','D9',I,1007,1011,r"ka|kOf"),
 ('codex','D9',I,1148,1150,r"lim|px"),
 ('codex','D10',I,353,353,r"10 m"),
 ('codex','D10',I,1011,1011,r"10 m"),
 ('codex','D11/12',I,1423,1429,r"foreignObject"),
 ('codex','D13',I,645,645,r"0\.55"),
 ('codex','D13',I,645,645,r"0\.35"),
 ('codex','D13',I,854,854,r"."),
 ('codex','D14/15',I,430,430,r"none"),
 ('codex','D14/15',I,866,869,r"produção contínua|granação"),
 ('codex','D16',I,605,608,r"px"),
 ('codex','D16',I,1143,1146,r"px"),
 ('codex','D17',I,1111,1111,r"sessionStorage\.setItem\('mapa-ctx'"),
 ('codex','D18','talmapa.js',163,167,r"talhao=\(\[\^&\]\+\)"),
 ('codex','D19',I,602,602,r"Medição"),
 ('codex','D19',I,1142,1142,r"Medição"),
 ('codex','D19',I,1168,1168,r"Medir"),
 ('codex','D20',I,1159,1162,r"pan_close"),
 ('codex','D20',I,1159,1162,r"scrollTop"),
 ('codex','D21',I,1634,1638,r'role="tab"'),
 ('codex','D22',I,1498,1498,r"30px"),
 ('codex','D22',I,1523,1523,r"36px"),
 ('codex','D23',I,1562,1562,r"position: absolute"),
 ('codex','D24',I,1127,1127,r"const FL="),
 ('codex','D25',I,911,915,r"const ICN=\["),
 ('codex','D25',I,1398,1400,r"ic:'Colheita'"),
 ('codex','D25','engine.py',12,30,r"'Colheita':'M12"),
 ('codex','D26',I,569,569,r"cdn\.jsdelivr\.net/npm/maplibre-gl@5\.9\.0"),
 ('codex','D26',I,571,571,r"lagoa_s2\.json"),
 ('codex','D27',CF,232,232,r"\{pid\}</text>"),
 ('codex','D27',I,646,646,r"rot|lg-rot"),
 ('codex','D28',I,565,566,r"max-width: ?120px"),
 ('codex','D28',I,635,636,r"peq"),
 ('codex','D29',I,619,621,r"maplibregl\.Map"),
 ('codex','D30',I,1174,1174,r"clique para somar talhões"),
 ('codex','CD-01',CF,205,216,r"mc_|g2open"),
 ('codex','CD-01',CF,424,424,r"g2open"),
 ('codex','CD-01',CF,449,449,r"g2open"),
 ('codex','CD-01det',CF,546,546,r"clip-path: polygon\(2% 5%"),
 ('codex','PL-06','areas/planejamento.py',86,89,r"<svg|polygon|T1"),
 ('codex','CA-01','areas/campo.py',154,157,r"190/350"),
 ('codex','AG-01det','areas/agronomia.py',834,834,r"880"),
 # ---- Claude (avaliacao-claude.md, 6c03d7e) ----
 ('claude','D1',I,632,633,r"cursor"),
 ('claude','D1',I,646,646,r"img"),
 ('claude','D1',I,1558,1558,r"mapa-real"),
 ('claude','D3','g2lib.js',1170,1170,r"SVGElement"),
 ('claude','D3','engine.py',1091,1091,r"brightness\(\.92\)"),
 ('claude','D4',I,1556,1556,r"overflow: hidden"),
 ('claude','D6',I,1189,1189,r"aviso_bv=\(faz==='Todas'\)"),
 ('claude','D8','areas/processo_os.py',969,976,r"tal="),
 ('claude','D9',I,116,116,r"Talhão"),
 ('claude','D9',I,833,833,r"ka"),
 ('claude','D9',I,987,987,r"ka"),
 ('claude','D11',I,349,351,r"T7"),
 ('claude','D11',I,745,745,r"T7"),
 ('claude','D12',I,1403,1406,r"15px|13px|font-size"),
 ('claude','D15',I,785,785,r"."),
 ('claude','D15',I,1370,1370,r"."),
 ('claude','D16',I,1435,1435,r"<rect"),
 ('claude','D16','talmapa.js',67,67,r"tmClique|dw"),
 ('claude','D17',I,620,620,r"bbox"),
 ('claude','D18','talmapa.js',166,169,r"talhao=\(\[\^&\]\+\)"),
 ('claude','D18',I,1110,1110,r"TIDS\(\)"),
 ('claude','D19',I,606,606,r"perímetro"),
 ('claude','D19',I,1143,1143,r"medir"),
 ('claude','D19','engine.py',2149,2149,r"4500"),
 ('claude','D19','g2lib.js',1130,1130,r"g2vivo\(t\)"),
 ('claude','D19','engine.py',2177,2177,r"região viva"),
 ('claude','D20',I,1162,1162,r"scrollTop"),
 ('claude','D20',I,1659,1659,r"62vh"),
 ('claude','D20',I,1660,1660,r'role="dialog"'),
 ('claude','D21','g2lib.js',1355,1355,r"data-visao"),
 ('claude','D22',I,1165,1165,r"padding:6px 10px|6px 10px"),
 ('claude','D22',I,1535,1535,r"g2-alvo|44px"),
 ('claude','D23',I,1659,1659,r"30%"),
 ('claude','D25',I,911,911,r"const ICN=\["),
 ('claude','D25',I,1445,1445,r"ICS=\["),
 ('claude','D25',I,1080,1080,r"'Colheita'\]"),
 ('claude','D26',I,649,649,r"Pixels do satélite indisponíveis"),
 ('claude','D27',I,986,986,r"Pivô"),
 ('claude','D27',CF,231,231,r"onClick=.*mc_"),
 ('claude','D27',I,103,103,r"P1|P2"),
 ('claude','D30',I,1527,1527,r"'Selecionar área'.*'Selecionar vários talhões'"),
 ('claude','D30',I,1167,1167,r"Selecionar área"),
 ('claude','N1',I,1495,1495,r"384px"),
 ('claude','N1',I,1554,1554,r"flex"),
 ('claude','N2',I,1361,1364,r"Abrir laudo"),
 ('claude','N2',I,948,948,r"a\.k==='op'"),
 ('claude','N2',I,968,968,r"ST_P"),
 ('claude','N3',I,619,619,r"maplibregl\.Map"),
 ('claude','N4',I,1425,1425,r"mancha"),
 ('claude','N5',I,176,177,r"INTEG="),
 ('claude','N5',I,714,719,r"integ"),
 ('claude','CD-01det',CF,624,634,r"geoVals"),
 ('claude','CA-01','areas/campo.py',154,154,r'viewBox="0 0 1180 190"'),
]

def ler(f):
    with open(os.path.join(G, f), encoding='utf-8') as fh:
        return fh.read().split('\n')

cache = {}
ok = falha = 0
for quem, item, f, a, b, rx in CIT:
    if f not in cache:
        cache[f] = ler(f)
    L = cache[f]
    achou = None
    for n in range(a, b + 1):
        if n - 1 < len(L) and re.search(rx, L[n - 1]):
            achou = n; break
    if achou:
        ok += 1
        trecho = L[achou - 1].strip()
        m = re.search(rx, trecho); i = max(0, m.start() - 40) if m else 0
        print(f"OK    {quem:6} {item:9} {f}:{a}-{b}  casa na {achou}: …{trecho[i:i+110]}…")
    else:
        falha += 1
        viz = [n for n in range(max(1, a - 6), b + 7) if n - 1 < len(L) and re.search(rx, L[n - 1])]
        dica = f"; casa na vizinha {viz[0]} (deslocamento {viz[0]-a:+d})" if viz else "; nenhuma vizinha em ±6"
        print(f"FALHA {quem:6} {item:9} {f}:{a}-{b}  sem /{rx}/{dica}")
print(f"\nTOTAL {len(CIT)} citações · OK {ok} · FALHA {falha}")
