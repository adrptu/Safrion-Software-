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


if __name__ == '__main__':
    unittest.main()
