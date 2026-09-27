# -*- coding: utf-8 -*-
"""Regressão persistente do portão do job de código (R001-01, R-003). Roda na CI: python3 -m unittest discover -s tools/ci"""
import json, os, subprocess, sys, tempfile, unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checar_contrato_codigo.py')
COMPLETO = {'packageManager': 'pnpm@11.25.0', 'engines': {'node': '>=24'},
            'scripts': {'format:check': 'a', 'lint': 'a', 'typecheck': 'a', 'test': 'a', 'build': 'a'}}


class PortaoContrato(unittest.TestCase):
    def rodar(self, arquivos):
        with tempfile.TemporaryDirectory() as d:
            for nome, conteudo in arquivos.items():
                with open(os.path.join(d, nome), 'w', encoding='utf-8') as f:
                    f.write(conteudo if isinstance(conteudo, str) else json.dumps(conteudo))
            saida = os.path.join(d, 'gh_output')
            p = subprocess.run([sys.executable, SCRIPT, d], capture_output=True, text=True, env={**os.environ, 'GITHUB_OUTPUT': saida})
            ativo = ''
            if os.path.exists(saida):
                with open(saida, encoding='utf-8') as f: ativo = f.read().strip()
            return p.returncode, ativo, p.stdout

    def test_so_documentacao_e_na(self):
        self.assertEqual(self.rodar({})[:2], (0, 'ativo=false'))

    def test_manifesto_sem_lockfile_falha(self):
        self.assertEqual(self.rodar({'package.json': {}})[0], 1)

    def test_lockfile_sem_manifesto_falha(self):
        self.assertEqual(self.rodar({'pnpm-lock.yaml': 'lockfileVersion: 9.0'})[0], 1)

    def test_script_obrigatorio_ausente_falha(self):
        pkg = json.loads(json.dumps(COMPLETO)); del pkg['scripts']['format:check']
        code, _, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
        self.assertEqual(code, 1); self.assertIn('format:check', out)

    def test_versao_nao_fixada_falha(self):
        pkg = dict(COMPLETO, packageManager='pnpm')
        self.assertEqual(self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24'})[0], 1)

    def test_contrato_completo_ativa(self):
        self.assertEqual(self.rodar({'package.json': COMPLETO, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})[:2], (0, 'ativo=true'))

    def test_manifesto_deve_ser_objeto(self):
        for pkg in [None, [], 42, True, '"texto"']:
            with self.subTest(pkg=pkg):
                code, ativo, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
                self.assertEqual((code, ativo), (1, 'ativo=false'))
                self.assertIn('package.json deve conter um objeto', out)

    def test_package_manager_deve_ser_texto(self):
        for valor in [None, 123, True, [], {}]:
            with self.subTest(valor=valor):
                pkg = dict(COMPLETO, packageManager=valor)
                code, ativo, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
                self.assertEqual((code, ativo), (1, 'ativo=false'))
                self.assertIn('packageManager', out)

    def test_engines_deve_conter_node_textual(self):
        for valor in [None, 123, True, '>=24', [], {'node': 24}, {'node': True}, {'node': ['>=24']}, {'node': '   '}]:
            with self.subTest(valor=valor):
                pkg = dict(COMPLETO, engines=valor)
                code, ativo, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
                self.assertEqual((code, ativo), (1, 'ativo=false'))
                self.assertIn('engines.node', out)

    def test_scripts_deve_ser_objeto(self):
        for valor in [None, 123, True, 'test', []]:
            with self.subTest(valor=valor):
                pkg = dict(COMPLETO, scripts=valor)
                code, ativo, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
                self.assertEqual((code, ativo), (1, 'ativo=false'))
                self.assertIn('scripts', out)

    def test_cada_script_obrigatorio_deve_ser_texto_nao_vazio(self):
        for nome in COMPLETO['scripts']:
            for valor in [None, 0, 1, False, True, [], {}, '', '   ']:
                with self.subTest(script=nome, valor=valor):
                    pkg = dict(COMPLETO, scripts={**COMPLETO['scripts'], nome: valor})
                    code, ativo, out = self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
                    self.assertEqual((code, ativo), (1, 'ativo=false'))
                    self.assertIn(nome, out)

    def test_json_malformado_falha_com_diagnostico(self):
        code, ativo, out = self.rodar({'package.json': '{invalido', 'pnpm-lock.yaml': 'x', '.nvmrc': '24.19.0'})
        self.assertEqual((code, ativo), (1, 'ativo=false'))
        self.assertIn('package.json inválido', out)

    def test_nvmrc_invalido_falha_com_diagnostico(self):
        for valor in ['', '24', 'lts/*']:
            with self.subTest(valor=valor):
                code, ativo, out = self.rodar({'package.json': COMPLETO, 'pnpm-lock.yaml': 'x', '.nvmrc': valor})
                self.assertEqual((code, ativo), (1, 'ativo=false'))
                self.assertIn('.nvmrc', out)

    def test_contrato_com_hash_e_prefixo_v_ativa(self):
        pkg = dict(COMPLETO, packageManager='pnpm@11.25.0+sha512.ab12')
        self.assertEqual(self.rodar({'package.json': pkg, 'pnpm-lock.yaml': 'x', '.nvmrc': 'v24.19.0\n'})[:2], (0, 'ativo=true'))


if __name__ == '__main__':
    unittest.main()
