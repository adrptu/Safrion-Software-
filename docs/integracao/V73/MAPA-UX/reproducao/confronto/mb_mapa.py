"""MB-* tem mapa? Varredura estática do render publicado (só leitura).

Uso: python3 -I -B mb_mapa.py <_render>   (render da composição 05947ad).
Conta, por tela MB-*: SVG com viewBox de 200 un ou mais (mapa; ícones têm 24), 'maplibre', <polygon>
e o código de link para o mapa (IN-04.dc.html#car e #talhao=). O #car vem do aviso de carência
compartilhado ('Ver restrição no mapa' / 'Ver pendência no mapa'), que só aparece com restrição ou pendência:
a contagem diz que a tela PODE levar ao IN-04, não quantas mostram o link no cenário inicial.
"""
import sys, re, glob, os
R = sys.argv[1]
tot = com_mapa = com_link = 0
for f in sorted(glob.glob(os.path.join(R, 'MB-*.dc.html'))):
    s = open(f, encoding='utf-8').read()
    vb = re.findall(r'<svg[^>]*viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', s)
    grande = [v for v in vb if float(v[0]) >= 200]
    ml = s.count('maplibre'); poly = len(re.findall(r'<polygon', s))
    car = s.count('IN-04.dc.html#car'); tal = s.count('IN-04.dc.html#talhao=')
    tot += 1; com_mapa += bool(grande or ml or poly); com_link += bool(car or tal)
    print(f"{os.path.basename(f):24} svg={len(vb):3} svg>=200un={len(grande)} maplibre={ml} polygon={poly} link_IN-04#car={car} #talhao={tal}")
print(f"\nTOTAL telas MB={tot} · com mapa={com_mapa} · com código de link para o IN-04 (aviso de carência)={com_link}")
