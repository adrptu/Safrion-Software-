# Esquema dos dados da Lagoa Grande (só estrutura: nomes de campo, tipos e tamanhos; NENHUM valor real)

Gerado no Mac a partir dos originais (CORTE-REMOTO-01). A camada sintética da nuvem deve produzir arquivos com a MESMA estrutura em `dados_lagoa_sintetico/saida/` e o módulo `dados_lagoa_sintetico/kml.py` (com `__init__.py`). Chaves que seriam identificadores de cena aparecem como `<id-de-cena>`.

## lagoa_s2_resumo.json  (20201 bytes)
`{pivos: [23 × {id: str, rot: str, nome: str, ha: float, lon: float, lat: float, r_m: float}], cantos: [4 × [2 × float]], idx: [5 × str], H: int, W: int, cenas: [2 × {id: str, dt: str, hora_utc: str, nuvem: float, png: str, est: {…}}]}`

## lagoa_pivos.geojson  (45993 bytes)
`{type: str, features: [23 × {type: str, properties: {…}, geometry: {…}}]}`

## lagoa_cadastro.json  (12849 bytes)
`{fazenda: str, municipio: str, uf: str, fonte: str, pivos: [23 × {id: str, nome: str, area_ha: float, centro: [2 × float], raio_m: float, geometria: str}], perimetros: [3 × {nome: str, tema: str, area_ha: NoneType, municipio: str, estado: str, modulos_fiscais: str, recibo_car: str}], ambiental: [19 × {grupo: str, tema: str, area_ha: float, recibo_car: str}], agua: [16 × {nome: str, descricao: str, lon: float, lat: float}]}`

## lagoa_rgb.json  (533 bytes)
`{lagoa_rgb_20260925.png: {H: int, W: int, cantos: [4 × [2 × float]], seg: float}, lagoa_rgb_20260910.png: {H: int, W: int, cantos: [4 × [2 × float]], seg: float}}`

## lagoa_s2.json  (2332956 bytes)
`{pivos: [23 × {id: str, rot: str, nome: str, ha: float, lon: float, lat: float, r_m: float}], cenas: [2 × {id: str, dt: str, nuvem: float, png: str, q: {…}, est: {…}}], idx: [5 × str], H: int, W: int, cantos: [4 × [2 × float]], pix: str, dono: str}`

## lagoa_analise.json  (135692 bytes)
`{desc: {NDVI: {o: str, tec: str, uso: str}, NDRE: {o: str, tec: str, uso: str}, EVI: {o: str, tec: str, uso: str}, SAVI: {o: str, tec: str, uso: str}, NDMI: {o: str, tec: str, uso: str}}, fases: [5 × {nome: str, faixa: [2 × float]}], cenas: {25/09: {dt: str, ant: str, piv: {…}, faz: {…}}, 10/09: {dt: str, ant: NoneType, piv: {…}, faz: {…}}}}`

## cenas.json  (1590 bytes)
`{<id-de-cena>: {crs: str, transform: [6 × float], H: int, W: int, meta: {blue: {…}, green: {…}, red: {…}, nir: {…}, rededge1: {…}, swir16: {…}, scl: {…}}, dt: str, nuvem: float, seg: float}, <id-de-cena>: {crs: str, transform: [6 × float], H: int, W: int, meta: {blue: {…}, green: {…}, red: {…}, nir: {…}, rededge1: {…}, swir16: {…}, scl: {…}}, dt: str, nuvem: float, seg: float}}`

- lagoa_20260910.png: PNG 733×753
- lagoa_20260925.png: PNG 733×753
- lagoa_rgb_20260910.png: PNG 1491×837
- lagoa_rgb_20260925.png: PNG 1491×837

## dados_lagoa_kml.py → dados_lagoa_sintetico/kml.py (mesmas constantes)
- LG_FONTE: str · LG_GEO: str
- LG_PIVOS: lista de 23 tuplas (id "PVnn", nome "Pivô n", área ha float, longitude float, latitude float, raio m float); ids PV01–PV24 sem PV16; raio = sqrt(área×10⁴/π)
- LG_PERIMETROS: lista de 2 dicts com chaves ['area', 'car', 'mf', 'mun', 'nome', 'temas'] (o 1º é o imóvel: area, car, mf usados por dados_cad.FAZENDAS)
- LG_AMBIENTAL: lista de 18 tuplas (grupo, tema, área ha, é total do grupo bool)
- LG_AGUA: lista de 16 dicts com chaves ['curso', 'desc', 'fin', 'id', 'lat', 'lon', 'modo', 'nome', 'num', 'proc', 'regime', 'renov', 'tipo', 'vazao', 'venc']

## Consumidores
- dados_cad.py (FAZENDAS.append usa LG_PERIMETROS[0] area/car/mf) · areas/cad_fazendas.py (LG_PIVOS, LG_AMBIENTAL, LG_AGUA)
- dados_lagoa_safra.py (PIVOS_HA) · dados_irrigacao.py (lagoa_cadastro.json) · dados_mip.py e areas/inicio.py (lagoa_s2_resumo.json, lagoa_pivos.geojson, lagoa_rgb.json, PNG) · montar_render.py (lagoa_s2.json + PNG no site) · a página IN-04 busca lagoa_s2.json no navegador
