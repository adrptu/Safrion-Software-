# -*- coding: utf-8 -*-
"""Prova sintética de montagem do s2_l2a.py (contrato MAPA-REAL; Codex 6270730787, itens 1 e 2): o processar() inteiro roda sobre
um catálogo e bandas inventados, sem rede e sem dado real, com um pivô todo sob nuvem e um índice inválido isolado no outro. Depois o
mesmo consumo do Mapa (gen37/lagoa_sat.py, usado por areas/inicio.py) lê a saída.
  M1 geração: pivô sob nuvem com os cinco índices None (nunca zero) e nuvem 100 %; índice inválido só no NDMI do outro pivô,
     contado em `invalidos`, com os outros quatro índices valendo; os demais pivôs e cenas seguem.
  M2 consumo: 'cloud' para o pivô sob nuvem e None só no NDMI do outro; contraprova: a expressão antiga do Mapa quebrava (TypeError).
  M3 sem estágio agronômico inferido do NDVI: a análise leva a legenda numérica, sem 'fase', sem 'ha_por_fase' e sem nome de estágio.
Uso: python -m unittest tools.geo.s2_l2a_montagem_test -v   (precisa de numpy e rasterio, como o processamento)"""
import json, os, shutil, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
GEN37 = os.path.join(RAIZ, 'tools', 'prototipo', 'v37', 'gen37')
sys.path.insert(0, AQUI); sys.path.insert(0, GEN37)
import s2_l2a as S
import s2_l2a_test as T
import lagoa_sat

DN = dict(blue=300, green=500, red=400, nir=3000, rededge1=1500, swir16=2000)   # inventados; reflectância = DN × 0,0001


def _item(data):
    banda = lambda n: {'href': 'sintetico://' + n, 'gsd': 10, 'raster:bands': [{'scale': 0.0001, 'offset': -0.1}]}
    return {'id': 'S2SINTETICO_' + data.replace('-', ''), 'properties': {'datetime': data + 'T13:20:00Z', 'proj:epsg': 32723, 'eo:cloud_cover': 1.5,
            'earthsearch:boa_offset_applied': True}, 'assets': {n: banda(n) for n in list(DN) + ['scl', 'visual']}}


class Montagem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: import numpy as np; import rasterio  # noqa: F401
        except ImportError: raise unittest.SkipTest('numpy/rasterio ausentes')
        def ler(href, b, H, W):
            n = href.split('//')[1]; leste = np.zeros((H, W), bool); leste[:, W // 2:] = True   # PV01 a oeste, PV03 a leste
            if n == 'scl': return np.where(leste, 9, 4).astype('uint8')                        # 9 = nuvem alta só sobre o PV03
            a = np.full((H, W), DN[n], dtype='uint16')
            if n == 'swir16': a[~leste] = 0                                                    # 0 = sem dado: NDMI inválido só no PV01
            return a
        cls.antes = (S.buscar, S.ler, S.ler_rgb)
        S.buscar = lambda bbox, data: _item(data); S.ler = ler; S.ler_rgb = lambda href, b, H, W: np.full((H, W, 3), 90, dtype='uint8')
        cls.dir = tempfile.mkdtemp(prefix='s2_montagem_')
        cls.res = S.processar(T._kml(), cls.dir, ['2026-09-25', '2026-09-10'])
        d = os.path.join(cls.dir, 'dados_lagoa')
        cls.R = json.load(open(os.path.join(d, 'lagoa_s2_resumo.json'), encoding='utf-8'))
        cls.A = json.load(open(os.path.join(d, 'lagoa_analise.json'), encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        S.buscar, S.ler, S.ler_rgb = cls.antes; shutil.rmtree(cls.dir, ignore_errors=True)

    def test_M1_geracao_preserva_ausencia(self):
        self.assertEqual(len(self.R['cenas']), 2)
        for c in self.R['cenas']:
            e1, e3 = c['est']['PV01'], c['est']['PV03']
            self.assertTrue(all(e3[n] is None for n in S.IDX) and e3['nuvem'] == 100.0, e3)
            self.assertIsNone(e1['NDMI']); self.assertEqual(e1['nuvem'], 0.0)
            self.assertTrue(all(isinstance(e1[n], dict) and e1[n]['n'] > 0 and -1 <= e1[n]['med'] <= 1 for n in ('NDVI', 'NDRE', 'EVI', 'SAVI')), e1)
        self.assertTrue(self.res['invalidos']['NDMI'] > 0 and all(self.res['invalidos'][n] == 0 for n in ('NDVI', 'NDRE', 'EVI', 'SAVI')), self.res['invalidos'])

    def test_M2_consumo_do_mapa_sem_quebrar(self):
        for c in self.R['cenas']:
            v = lagoa_sat.sat_v(c, ['PV01', 'PV03'], S.IDX)
            self.assertEqual(v['PV03'], 'cloud')
            self.assertEqual([x is None for x in v['PV01']], [n == 'NDMI' for n in S.IDX], v['PV01'])
            with self.assertRaises(TypeError):     # contraprova: a expressão anterior de areas/inicio.py
                [c['est']['PV01'][n]['med'] for n in S.IDX]

    def test_M3_sem_estagio_inferido(self):
        txt = json.dumps({k: v for k, v in self.A.items() if k != 'desc'}, ensure_ascii=False)   # 'desc' descreve o uso de cada índice (C4), não a observação
        self.assertNotIn('fases', self.A); self.assertEqual(self.A['legenda']['faixas'], S.legenda_ndvi())
        for k in self.A['cenas'].values():
            self.assertNotIn('ha_por_fase', k['faz'])
            self.assertTrue(all(set(p) == {'ndvi', 'dif'} for p in k['piv'].values()), k['piv'])
        for termo in ('produção', 'formação', 'plantio', 'preparo', 'solo exposto', '"fase"'): self.assertNotIn(termo, txt)


if __name__ == '__main__':
    unittest.main()
