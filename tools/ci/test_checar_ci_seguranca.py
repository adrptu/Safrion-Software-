# -*- coding: utf-8 -*-
"""Regressão do portão das regras de segurança da CI (FERR-01). Roda na CI: python3 -m unittest discover -s tools/ci"""
import os, subprocess, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(AQUI, 'checar_ci_seguranca.py')
RAIZ_REAL = os.path.dirname(os.path.dirname(AQUI))
HOJE = '--hoje=2026-09-27'
PASSO = '''jobs:
  vulnerabilidades:
    runs-on: ubuntu-latest
    steps:
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: "1"
          ignore-unfixed: false
{extra}'''


class PortaoSegurancaCI(unittest.TestCase):
    def rodar(self, extra='', arquivos=None, workflow=None):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, '.github', 'workflows'))
            with open(os.path.join(d, '.github', 'workflows', 'ci.yml'), 'w', encoding='utf-8') as f:
                f.write(workflow if workflow is not None else PASSO.format(extra=extra))
            for nome, conteudo in (arquivos or {}).items():
                with open(os.path.join(d, nome), 'w', encoding='utf-8') as f:
                    f.write(conteudo)
            p = subprocess.run([sys.executable, SCRIPT, d, HOJE], capture_output=True, text=True)
            return p.returncode, p.stdout

    def test_ci_real_do_repositorio_passa(self):
        p = subprocess.run([sys.executable, SCRIPT, RAIZ_REAL, HOJE], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_passo_correto_passa(self):
        self.assertEqual(self.rodar()[0], 0)

    def test_ignore_unfixed_true_falha(self):
        code, out = self.rodar(workflow=PASSO.format(extra='').replace('ignore-unfixed: false', 'ignore-unfixed: true'))
        self.assertEqual(code, 1); self.assertIn('ignore-unfixed', out)

    def test_relatorio_que_nao_bloqueia_falha(self):
        code, out = self.rodar(workflow=PASSO.format(extra='').replace('exit-code: "1"', 'exit-code: "0"'))
        self.assertEqual(code, 1); self.assertIn('exit-code', out)

    def test_passo_com_nome_antes_do_uses_e_conferido(self):
        wf = PASSO.format(extra='') + '''      - name: Relatar sem bloquear
        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: "0"
'''
        code, out = self.rodar(workflow=wf)
        self.assertEqual(code, 1); self.assertIn(':12:', out); self.assertIn('exit-code', out)

    def test_severidade_sem_critical_falha(self):
        self.assertEqual(self.rodar(workflow=PASSO.format(extra='').replace('HIGH,CRITICAL', 'HIGH'))[0], 1)

    def test_continue_on_error_falha(self):
        self.assertEqual(self.rodar(extra='        continue-on-error: true\n')[0], 1)

    def test_trivyignore_simples_falha(self):
        self.assertEqual(self.rodar(arquivos={'.trivyignore': 'CVE-2026-0001\n'})[0], 1)

    def test_excecao_sem_motivo_ou_validade_falha(self):
        ref = '          trivyignores: .trivyignore.yaml\n'
        code, out = self.rodar(extra=ref, arquivos={'.trivyignore.yaml': 'vulnerabilities:\n  - id: CVE-2026-0001\n'})
        self.assertEqual(code, 1); self.assertIn('statement', out); self.assertIn('expired_at', out)

    def test_excecao_vencida_ou_longa_falha(self):
        ref = '          trivyignores: .trivyignore.yaml\n'
        for data in ('2026-09-01', '2027-03-01'):
            y = f'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: pacote só de teste, fora da imagem publicada\n    expired_at: {data}\n'
            self.assertEqual(self.rodar(extra=ref, arquivos={'.trivyignore.yaml': y})[0], 1, data)

    def test_excecao_completa_e_referenciada_passa(self):
        ref = '          trivyignores: .trivyignore.yaml\n'
        y = 'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: pacote só de teste, fora da imagem publicada\n    expired_at: 2026-11-30\n'
        self.assertEqual(self.rodar(extra=ref, arquivos={'.trivyignore.yaml': y})[0], 0)

    def test_excecao_nao_referenciada_falha(self):
        y = 'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: x\n    expired_at: 2026-11-30\n'
        self.assertEqual(self.rodar(arquivos={'.trivyignore.yaml': y})[0], 1)


    # FERR-03 (revisão do Codex): o item pode começar por qualquer chave; o formato fora do subconjunto é recusado.
    REF = '          trivyignores: .trivyignore.yaml\n'
    BOM = '    statement: pacote só de teste, fora da imagem publicada\n    expired_at: 2026-11-30\n'

    def ignore(self, y):
        return self.rodar(extra=self.REF, arquivos={'.trivyignore.yaml': y})

    def test_contraexemplo_do_codex_id_depois_de_paths_falha(self):
        code, out = self.ignore('vulnerabilities:\n  - paths: ["package-lock.json"]\n    id: CVE-2026-0001\n')
        self.assertEqual(code, 1, out); self.assertIn('statement', out); self.assertIn('expired_at', out)

    def test_ordem_das_chaves_nao_importa_quando_completo(self):
        y = 'vulnerabilities:\n  - paths: ["package-lock.json"]\n' + self.BOM + '    id: CVE-2026-0001\n'
        self.assertEqual(self.ignore(y)[0], 0)

    def test_lista_de_paths_em_bloco_passa(self):
        y = 'misconfigurations:\n  - id: AVD-DS-0002\n    paths:\n      - "docs/Dockerfile"\n' + self.BOM
        self.assertEqual(self.ignore(y)[0], 0)

    def test_item_sem_id_falha(self):
        self.assertEqual(self.ignore('vulnerabilities:\n  - paths: ["a"]\n' + self.BOM)[0], 1)

    def test_nulo_do_yaml_nao_vale_como_valor(self):
        # FERR-04 (revisão do Codex): "statement: null" passava como motivo; nulo é ausência de valor (YAML 1.2.2 Core).
        base = 'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: {s}\n    expired_at: 2026-11-30\n'
        for s in ('null', 'Null', 'NULL', '~', 'null # sem motivo', '"null"', "'~'"):
            with self.subTest(statement=s):
                code, out = self.ignore(base.format(s=s))
                self.assertEqual(code, 1, out); self.assertIn('nulo', out); self.assertIn('falta statement', out)
        outros = {
            'id nulo': 'vulnerabilities:\n  - id: ~\n' + self.BOM,
            'validade nula': 'vulnerabilities:\n  - id: CVE-1\n    statement: motivo\n    expired_at: NULL\n',
            'caminho nulo em lista': 'vulnerabilities:\n  - id: CVE-1\n    paths: [null]\n' + self.BOM,
            'caminho nulo em bloco': 'vulnerabilities:\n  - id: CVE-1\n    paths:\n      - ~\n' + self.BOM,
        }
        for nome, y in outros.items():
            with self.subTest(caso=nome):
                code, out = self.ignore(y)
                self.assertEqual(code, 1, out); self.assertIn('nulo', out)

    def test_controles_do_ferr04_continuam(self):
        # Os mesmos controles do Codex: ausente e vazio são recusados; motivo concreto com data válida passa;
        # palavra que só contém "null" no meio do texto é motivo, não nulo.
        sem = 'vulnerabilities:\n  - id: CVE-2026-0001\n    expired_at: 2026-11-30\n'
        vazio = 'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: ""\n    expired_at: 2026-11-30\n'
        self.assertEqual(self.ignore(sem)[0], 1)
        self.assertEqual(self.ignore(vazio)[0], 1)
        self.assertEqual(self.ignore('vulnerabilities:\n  - id: CVE-2026-0001\n' + self.BOM)[0], 0)
        texto = 'vulnerabilities:\n  - id: CVE-2026-0001\n    statement: null pointer só no teste\n    expired_at: 2026-11-30\n'
        self.assertEqual(self.ignore(texto)[0], 0)

    def test_formatos_fora_do_subconjunto_sao_recusados(self):
        casos = {
            'chave desconhecida': 'vulnerabilities:\n  - id: CVE-1\n    ignore_all: true\n' + self.BOM,
            'chave repetida': 'vulnerabilities:\n  - id: CVE-1\n    id: CVE-2\n' + self.BOM,
            'ancora': 'vulnerabilities:\n  - id: CVE-1\n    statement: &s motivo\n    expired_at: 2026-11-30\n',
            'bloco multilinha': 'vulnerabilities:\n  - id: CVE-1\n    statement: >\n      motivo\n    expired_at: 2026-11-30\n',
            'estilo em chaves': 'vulnerabilities: [{id: CVE-1, statement: x, expired_at: 2026-11-30}]\n',
            'lista sem recuo': 'vulnerabilities:\n- id: CVE-1\n' + self.BOM.replace('    ', '  '),
            'tab': 'vulnerabilities:\n\t- id: CVE-1\n',
            'secao desconhecida': 'ignorar:\n  - id: CVE-1\n' + self.BOM,
            'documento multiplo': 'vulnerabilities: []\n---\nvulnerabilities:\n  - id: CVE-1\n',
        }
        for nome, y in casos.items():
            self.assertEqual(self.ignore(y)[0], 1, nome)


if __name__ == '__main__':
    unittest.main()
