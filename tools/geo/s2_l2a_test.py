# -*- coding: utf-8 -*-
"""Regras do s2_l2a.py com um KML fictício (mesma estrutura de pastas do KML do proprietário, valores inventados, no mar),
sem rede e sem dado real. Uso: python3 -m unittest tools.geo.s2_l2a_test -v (numpy só no caso da reflectância)."""
import math, os, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(RAIZ, 'tools', 'prototipo', 'v37', 'gen37'))
import s2_l2a as S

KML = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>KML FICTICIO.kml</name>
<Folder><name>PIVÔS</name>
 <Placemark><name>PIVÔ 1</name><description>HECTARE: 40</description><Point><coordinates>-47.20,-34.60,0</coordinates></Point></Placemark>
 <Placemark><name>PIVÔ 3</name><description>HECTARES: 18,5</description><Point><coordinates>-47.18,-34.61,0</coordinates></Point></Placemark>
</Folder>
<Folder><name>POLIGONO</name><Placemark><name>Pivô</name><LineString><coordinates>@@CIRCULO@@</coordinates></LineString></Placemark></Folder>
<Folder><name>PERÍMETRO</name><Folder><name>PERÍMETRO</name>
 <Placemark><ExtendedData><Data name="recibo"><value>SINTETICO-0001</value></Data><Data name="modfiscais"><value>12.34</value></Data>
  <Data name="tema"><value>Área do Imovel</value></Data><Data name="area"><value>500.126</value></Data><Data name="municipio"><value>Fictícia</value></Data></ExtendedData>
  <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.21,-34.59 -47.17,-34.59 -47.17,-34.62 -47.21,-34.62 -47.21,-34.59</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
 <Placemark><ExtendedData><Data name="recibo"><value>SINTETICO-0001</value></Data><Data name="modfiscais"><value>12.34</value></Data>
  <Data name="tema"><value>Área Líquida do Imóvel</value></Data><Data name="area"><value>500.126</value></Data></ExtendedData>
  <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.21,-34.59 -47.17,-34.59 -47.17,-34.62 -47.21,-34.59</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
</Folder>
 <Placemark><name>PERÍMETRO ARRENDO</name><Polygon><outerBoundaryIs><LinearRing><coordinates>-47.20,-34.60 -47.19,-34.60 -47.19,-34.61 -47.20,-34.61 -47.20,-34.60</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
</Folder>
<Folder><name>RECURSOS HIDRICOS_FICTICIO</name>
 <Placemark><name>1</name><description>OUTORGA ESTADUAL 0000001/2020 PROCESSO: 00001/2019 Modo de Uso: Captação Direta Curso d'água: Rio Fictício Vazão: 100,5 (l/s) durante 21:00 horas/dia Finalidade: Irrigação de uma área de 10 hectares através do método de pivô central. VENCIMENTO: 01/02/2025 EM RENOVAÇÃO - PROCESSO TÉCNICO: 00002/2024</description><Point><coordinates>-47.19,-34.60,0</coordinates></Point></Placemark>
 <Placemark><name>2</name><description>CERTIDÃO DE USO INSIGNIFICANTE 000003/2023 PROCESSO: 00003/2023 Modo de Uso: Cisterna Vazão: 1,500 m³/h durante 06:00 horas/dia Finalidade: Consumo Humano VENCIMENTO: 17/11/2030</description><Point><coordinates>-47.19,-34.61,0</coordinates></Point></Placemark>
 <Placemark><name>N°0000004</name><Point><coordinates>-47.18,-34.60,0</coordinates></Point></Placemark>
</Folder>
<Folder><name>KML GERAL</name>
 <Folder><name>RESERVA LEGAL</name><Placemark><ExtendedData><Data name="recibo"><value>SINTETICO-0001</value></Data><Data name="area"><value>100.5</value></Data><Data name="tema"><value>Área de Reserva Legal Total</value></Data></ExtendedData>
  <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.21,-34.59 -47.20,-34.59 -47.20,-34.60 -47.21,-34.59</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Folder>
 <Folder><name>APP</name>
  <Placemark><name>[1:Polygon]</name><ExtendedData><Data name="area"><value>20.25</value></Data><Data name="tema"><value>APP Total</value></Data></ExtendedData>
   <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.21,-34.59 -47.20,-34.59 -47.20,-34.60 -47.21,-34.59</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
  <Placemark><name>[2:Polygon]</name><ExtendedData><Data name="area"><value>20.25</value></Data><Data name="tema"><value>APP Total</value></Data></ExtendedData>
   <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.20,-34.60 -47.19,-34.60 -47.19,-34.61 -47.20,-34.60</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
  <Placemark><ExtendedData><Data name="area"><value>3.1</value></Data><Data name="tema"><value>Vereda</value></Data></ExtendedData>
   <Polygon><outerBoundaryIs><LinearRing><coordinates>-47.20,-34.60 -47.19,-34.60 -47.19,-34.61 -47.20,-34.60</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
 </Folder>
</Folder>
<Placemark><name>Captação Rio Fictício - N°0000005</name><Point><coordinates>-47.185,-34.605,0</coordinates></Point></Placemark>
</Document></kml>'''


def _kml():
    r = math.sqrt(40 * 1e4 / math.pi); circ = ' '.join(f'{x},{y}' for x, y in S.circulo(-47.20, -34.60, r))
    f = tempfile.NamedTemporaryFile('w', suffix='.kml', delete=False, encoding='utf-8'); f.write(KML.replace('@@CIRCULO@@', circ)); f.close()
    return f.name


class LeituraDoKml(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.K = S.ler_kml(_kml())

    def test_pivos_pelo_ponto_central_e_area_declarada(self):
        p = self.K['pivos']
        self.assertEqual([x[0] for x in p], ['PV01', 'PV03'])
        self.assertEqual([x[2] for x in p], [40.0, 18.5])                      # "HECTARE" e "HECTARES", vírgula decimal
        self.assertAlmostEqual(p[0][5], math.sqrt(40 * 1e4 / math.pi), places=2)

    def test_conferencia_com_o_circulo_desenhado(self):
        c = dict((a, (b, d)) for a, b, d in S.conferir_circulos(self.K['pivos'], self.K['circulos']))
        self.assertAlmostEqual(c['PV01'][1], 40.0, delta=0.5)                 # círculo do mesmo pivô: área próxima da declarada
        self.assertIsNone(c['PV03'][1])                                        # sem círculo a menos de 150 m

    def test_imovel_do_car_e_perimetro_sem_car(self):
        P = self.K['perimetros']
        self.assertEqual((P[0]['area'], P[0]['car'], P[0]['mf']), (500.13, 'SINTETICO-0001', 12.3))
        self.assertEqual([p['nome'] for p in P[1:]], ['Perímetro arrendo'])
        self.assertGreater(P[1]['area'], 0)

    def test_ambiental_sem_duplicar_partes_do_mesmo_tema(self):
        self.assertEqual(self.K['ambiental'], [('Reserva legal', 'Área de Reserva Legal Total', 100.5, True),
                                               ('APP', 'APP Total', 20.25, True), ('APP', 'Vereda', 3.1, False)])

    def test_agua_no_formato_do_cadastro(self):
        A = self.K['agua']
        self.assertEqual(len(A), 4)
        a = A[0]
        self.assertEqual((a['tipo'], a['num'], a['proc'], a['curso'], a['vazao'], a['regime'], a['fin'], a['venc'], a['renov']),
                         ('Outorga', '0000001/2020', '00001/2019', 'Rio Fictício', '100,5 L/s', '21 h/dia', 'Irrigação', '2025-02-01', '00002/2024'))
        self.assertIn('captação superficial', a['modo'].lower())
        b = A[1]
        self.assertEqual((b['tipo'], b['vazao'], b['regime'], b['fin'], b['venc']),
                         ('Certidão de uso insignificante', '1,500 m³/h', '6 h/dia', 'Consumo Humano', '2030-11-17'))
        self.assertEqual((A[2]['tipo'], A[2]['num']), ('', '0000004'))         # ponto sem descrição
        self.assertEqual((A[3]['nome'], A[3]['num']), ('Captação Rio Fictício - N°0000005', '0000005'))

    def test_compativel_com_a_regra_de_outorga_do_cadastro(self):
        import dados_lagoa_fonte as F                                          # a mesma regra do CD-01 e da irrigação (CTL-5)
        a, b, c = self.K['agua'][:3]
        self.assertEqual((F.agua_ls(a['vazao']), F.agua_h(a['regime'])), (100.5, 21.0))
        self.assertAlmostEqual(F.agua_ls(b['vazao']), 1.5 / 3.6)
        self.assertEqual(F.agua_sit(a, '2026-10-19'), 'Em renovação')
        self.assertEqual(F.agua_sit(c, '2026-10-19'), 'Sem descrição no KML')


class EscopoPublicavel(unittest.TestCase):
    """exceção de 19/10: só imagem, índices e geometria; CAR, APP/RL e outorgas do KML não saem (demonstração no lugar)"""
    @classmethod
    def setUpClass(cls):
        cls.K = S.ler_kml(_kml()); cls.P = S.publicavel(cls.K, os.path.join(RAIZ, 'tools', 'prototipo', 'v37', 'gen37'))

    def test_nada_do_cadastro_do_kml_sai(self):
        txt = repr(self.P)
        for a in self.K['agua']:
            for c in ('num', 'proc', 'desc', 'curso', 'vazao'):
                if a[c]: self.assertNotIn(a[c], txt, (c, a[c]))
        for g, t, a, _ in self.K['ambiental']: self.assertNotIn(t, txt)
        self.assertNotIn('SINTETICO-0001', txt)                                  # recibo do CAR do KML
        self.assertNotIn('12.3', txt)                                            # módulos fiscais do KML

    def test_no_lugar_a_demonstracao_rotulada(self):
        from dados_lagoa_sintetico import kml as SK
        self.assertEqual(self.P['agua'], SK.LG_AGUA)
        self.assertEqual(self.P['ambiental'], SK.LG_AMBIENTAL)
        self.assertTrue(all('demonstração' in (a['nome'] + a['curso']) or not a['curso'] for a in self.P['agua']))
        self.assertIn('SINTETICO', self.P['perimetros'][0]['car'])
        self.assertIn('demonstração sintética', S.LG_FONTE)

    def test_perimetro_pela_geometria(self):
        anel = next(p['anel'] for p in self.K['perim_kml'] if p['car'] and 'Líquida' not in p['tema'])
        self.assertEqual(self.P['perimetros'][0]['area'], round(S.area_ha(anel), 2))   # área da geometria, não o atributo do CAR (500,126)
        self.assertNotEqual(self.P['perimetros'][0]['area'], 500.13)
        self.assertEqual([p['nome'] for p in self.P['perimetros']], ['Imóvel (perímetro do KML)', 'Perímetro arrendo'])
        self.assertTrue(all(c['recibo_car'] == '' and c['modulos_fiscais'] == '' for c in self.P['cad_perim']))


class Reflectancia(unittest.TestCase):
    def test_deslocamento_ja_aplicado_pelo_catalogo_nao_se_desconta_de_novo(self):
        try: import numpy as np
        except ImportError: self.skipTest('numpy ausente')
        banda = {'raster:bands': [{'scale': 0.0001, 'offset': -0.1}]}
        red, nir = np.array([296.0]), np.array([2500.0])                      # vegetação densa (vermelho bruto p5 dos pivôs em 19/10)
        nd = lambda r, n: float(((n - r) / (n + r))[0])
        certo = nd(S.refl(red, banda, True), S.refl(nir, banda, True))
        errado = nd(S.refl(red, banda, False), S.refl(nir, banda, False))
        self.assertTrue(0.7 < certo < 0.85, certo)
        self.assertGreater(errado, 1.0)                                        # contraprova: descontar de novo satura o NDVI (defeito de 19/10)
        self.assertTrue(math.isnan(S.refl(np.array([0.0]), banda, True)[0]))  # 0 = sem dado


class Formato(unittest.TestCase):
    def test_quantizacao_e_fase(self):
        self.assertEqual((S.quant(-1.0), S.quant(1.0), S.quant(0.0)), (0, 250, 125))
        self.assertAlmostEqual(S.deq(S.quant(0.6)), 0.6, places=2)
        self.assertEqual((S.fase_de(0.1), S.fase_de(0.5), S.fase_de(1.0), S.fase_de(None)), ('preparo · solo exposto', 'formação', 'produção', 'sem leitura (nuvem)'))
        self.assertEqual(S.cor_ndvi(1.0), (0x0B, 0x7A, 0x1E))

    def test_circulo_fechado(self):
        c = S.circulo(-47.2, -34.6, 100.0)
        self.assertEqual(len(c), 73); self.assertEqual(c[0], c[-1])


class SaidaForaDoGit(unittest.TestCase):
    def test_recusa_dentro_de_repositorio_e_aceita_fora(self):
        self.assertFalse(S.fora_do_git(os.path.join(RAIZ, 'tools', 'prototipo', 'v37', 'gen37')))
        with tempfile.TemporaryDirectory() as d: self.assertTrue(S.fora_do_git(d))


if __name__ == '__main__':
    unittest.main()
