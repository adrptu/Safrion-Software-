# -*- coding: utf-8 -*-
"""MAPA-REAL F1 · KMZ no Mapa (proprietário, 18/10/2026: "quero baixar uma fazenda real kml para fazer os testes mais realistas no protótipo").
O .kmz que o Google Earth exporta abre direto em Importar talhões (zip lido no navegador; o arquivo não sai do aparelho). Arquivo sintético:
um quadrado de 200 m no centro de um pivô da Lagoa Grande sintética (dados_lagoa_fonte fora do Mac) e um ponto sem área.
  K1 o campo de arquivo aceita .kmz e diz "KML, KMZ ou GeoJSON"
  K2 escolher o .kmz abre a revisão: o arquivo aparece como .kml, 2 linhas (o polígono e o ponto), sem erro
  K3 o polígono cai no pivô (destino "Novo contorno de …") e o ponto sem área explica por que não vira talhão
  K4 .kmz sem .kml dentro mostra o motivo, sem travar a tela
  K5 sem erro de JavaScript
  K6 KMZ corrompido (deslocamento fora do arquivo, tamanho maior que o arquivo): mensagem de formato com o que fazer, sem erro técnico
Contraprova: o render da v132 reprova K1 e K2 ("KMZ é compactado: abra no Google Earth e salve como .kml").
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B mapa_kmz_test.py"""
import os, sys, json, time, zipfile, tempfile, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
import dados_lagoa_fonte as F

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:500])

p0 = F.LG_PIVOS[4]; lon, lat = p0[3], p0[4]; k = 111320 * math.cos(lat * math.pi / 180); h = 100
q = [(lon - h / k, lat - h / 110540), (lon + h / k, lat - h / 110540), (lon + h / k, lat + h / 110540), (lon - h / k, lat + h / 110540), (lon - h / k, lat - h / 110540)]
KML = ('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Fazenda teste</name>'
       '<Placemark><name>Talhão de teste</name><Polygon><outerBoundaryIs><LinearRing><coordinates>' + ' '.join(f'{a:.7f},{b:.7f},0' for a, b in q) +
       '</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'
       f'<Placemark><name>Sede</name><Point><coordinates>{lon:.7f},{lat:.7f},0</coordinates></Point></Placemark></Document></kml>')
tmp = tempfile.mkdtemp(prefix='kmz-'); ARQ = os.path.join(tmp, 'fazenda_teste.kmz'); RUIM = os.path.join(tmp, 'sem_kml.kmz')
with zipfile.ZipFile(ARQ, 'w', zipfile.ZIP_DEFLATED) as z: z.writestr('files/leia.txt', 'imagens'); z.writestr('doc.kml', KML)
with zipfile.ZipFile(RUIM, 'w', zipfile.ZIP_DEFLATED) as z: z.writestr('leia.txt', 'nada aqui')
# K6 (revisão do Codex 6252555281): central directory apontando para fora do arquivo e arquivo truncado
QUEB = os.path.join(tmp, 'quebrado.kmz'); TRUNC = os.path.join(tmp, 'truncado.kmz')
_b = bytearray(open(ARQ, 'rb').read()); _e = _b.rfind(b'PK\x05\x06'); _b[_e + 16:_e + 20] = (len(_b) + 5000).to_bytes(4, 'little'); open(QUEB, 'wb').write(bytes(_b))
_b = bytearray(open(ARQ, 'rb').read()); _c = _b.find(b'PK\x01\x02'); _off = int.from_bytes(_b[_c + 42:_c + 46], 'little')
for _i in range(_c, _b.rfind(b'PK\x05\x06')):
    if _b[_i:_i + 4] == b'PK\x01\x02' and _b[_i + 46:_i + 46 + int.from_bytes(_b[_i + 28:_i + 30], 'little')].endswith(b'doc.kml'): _b[_i + 20:_i + 24] = (len(_b) * 3).to_bytes(4, 'little')
open(TRUNC, 'wb').write(bytes(_b))

port, srv = servir(R); c = Chrome(); J = c.js
def espera(cond, s=40):
    fim = time.time() + s
    while time.time() < fim:
        try:
            if J(cond): return True
        except Exception: pass
        time.sleep(.3)
    return False
def escolhe(arq):
    doc = c.call('DOM.getDocument', {'depth': -1, 'pierce': True})
    nid = c.call('DOM.querySelector', {'nodeId': doc['root']['nodeId'], 'selector': 'input[type=file][accept*=".kml"]'})['nodeId']
    c.call('DOM.setFileInputFiles', {'files': [arq], 'nodeId': nid}); time.sleep(1.5)
PAINEL = "(()=>{const t=[...document.querySelectorAll('main *')].find(e=>e.children.length===0&&e.textContent.trim()==='Importar talhões'); const a=t&&t.closest('aside,section,[role=dialog]')||document.querySelector('main'); return a?a.innerText:'';})()"
try:
    c.aparelho(1440, 900); J("window.__errs=window.__errs||[]")
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .4)
    J("localStorage.removeItem('talhao-os-cd01-v1'); sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}')")
    c.goto(f'http://127.0.0.1:{port}/IN-04.dc.html#importar', 1.5)
    espera("!!(window.__LGI&&window.__LGI.pronto)", 60); espera("!!document.querySelector('input[type=file][accept*=\".kml\"]')", 15)
    inp = J("(()=>{const i=document.querySelector('input[type=file][accept*=\".kml\"]'); return i?[i.getAttribute('accept'),i.getAttribute('aria-label')]:null;})()")
    chk('K1 o campo de arquivo aceita .kmz e diz "KML, KMZ ou GeoJSON"', inp and '.kmz' in inp[0] and inp[1] == 'Arquivo KML, KMZ ou GeoJSON', inp)
    escolhe(ARQ); espera("document.body.innerText.includes('fazenda_teste.kml')", 10)
    t = J(PAINEL) or ''
    chk('K2 o .kmz abre a revisão (o arquivo aparece como .kml), sem erro de leitura', 'fazenda_teste.kml' in t and 'KMZ é compactado' not in t and 'ilegível' not in t, t[:400])
    chk('K3 o polígono cai no pivô ("Novo contorno de …") e o ponto sem área explica por que não vira talhão',
        'Talhão de teste' in t and 'Novo contorno de' in t and 'Ponto sem área' in t, t[:600])
    J("(()=>{const b=[...document.querySelectorAll('main button')].find(x=>/Outro arquivo|Escolher outro/i.test(x.innerText)); if(b) b.click();})()"); time.sleep(.6)
    if J("!!document.querySelector('input[type=file][accept*=\".kml\"]')"):
        escolhe(RUIM); espera("document.body.innerText.includes('não tem arquivo .kml')", 8)
        t2 = J(PAINEL) or ''
        chk('K4 .kmz sem .kml dentro mostra o motivo, sem travar a tela', 'não tem arquivo .kml' in t2, t2[:300])
    else:
        chk('K4 .kmz sem .kml dentro mostra o motivo, sem travar a tela', False, 'sem o campo de arquivo depois de "Outro arquivo"')
    res6 = []
    for arq in (QUEB, TRUNC):
        J("(()=>{const b=[...document.querySelectorAll('main button')].find(x=>/Outro arquivo|Escolher outro/i.test(x.innerText)); if(b) b.click();})()"); time.sleep(.6)
        if J("!!document.querySelector('input[type=file][accept*=\".kml\"]')"): escolhe(arq); espera("document.body.innerText.includes('KMZ ilegível')", 8)
        res6.append((J(PAINEL) or '')[:400])
    chk('K6 KMZ com deslocamento fora do arquivo ou tamanho maior que o arquivo: "KMZ ilegível…" com o que fazer, sem o erro técnico do leitor',
        all('KMZ ilegível' in t and 'salve como .kml' in t and 'DataView' not in t and 'Offset' not in t for t in res6), res6)
    ee = [e for e in (J("window.__errs||[]") or []) if 'maplibre' not in e.lower()]
    chk('K5 sem erro de JavaScript', not ee, ee[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK} ok · {FAIL} falhas')
sys.exit(1 if FAIL else 0)
