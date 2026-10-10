"""As exceções do .gitleaks.toml continuam estreitas: HML-SECRET-03 (um literal exato em 25 arquivos exatos do protótipo)
e HML-SECRET-04 (cinco nomes exatos de chave de localStorage, só no protótipo e em dois arquivos de especificação).
O .gitleaksignore tem só o achado exato da HML-SECRET-05 (commit, arquivo, regra e linha), sem curinga."""
from pathlib import Path
import re
import tomllib
import unittest

RAIZ = Path(__file__).resolve().parents[2]
LITERAL = 'talhao-os-cenario-v1'
PREFIXO = 'tools/prototipo/v37/gen37/'


def excecao():
    cfg = tomllib.loads((RAIZ / '.gitleaks.toml').read_text(encoding='utf-8'))
    regra = next(r for r in cfg['rules'] if r['id'] == 'generic-api-key')
    return next(a for a in regra['allowlists'] if f'^{LITERAL}$' in a.get('regexes', []))


class ExcecaoDoPrototipo(unittest.TestCase):
    def test_literal_e_arquivos_exatos_com_as_duas_condicoes(self):
        a = excecao()
        self.assertEqual(a['condition'], 'AND')
        self.assertEqual(a['regexTarget'], 'secret')
        self.assertEqual(a['regexes'], [f'^{LITERAL}$'])
        self.assertEqual(len(a['paths']), 25)
        self.assertEqual(len(set(a['paths'])), 25)
        for p in a['paths']:
            with self.subTest(p=p):
                # Arquivo exato: ancorado, sem curinga, grupo, alternativa ou classe; só o ponto escapado.
                self.assertRegex(p, r'^\^tools/prototipo/v37/gen37/[A-Za-z0-9_/-]+(\\\.[A-Za-z0-9_-]+)+\$$')

    def test_outro_valor_ou_outro_arquivo_nao_entram(self):
        a = excecao()
        segredo = re.compile(a['regexes'][0])
        caminhos = [re.compile(p) for p in a['paths']]
        self.assertTrue(segredo.search(LITERAL))
        for outro in ('talhao-os-cenario-v2', 'ghp_' + 'A' * 36, f'x{LITERAL}', f'{LITERAL}x'):
            self.assertIsNone(segredo.search(outro), outro)
        self.assertTrue(any(c.search(PREFIXO + 'cenario.js') for c in caminhos))
        for fora in (PREFIXO + 'engine.py', PREFIXO + 'cenario.jsx', PREFIXO + 'cenarioXjs',
                     'apps/web/src/cenario.js', PREFIXO + 'project/OS.dc.html.bak'):
            self.assertFalse(any(c.search(fora) for c in caminhos), fora)


CHAVES = ['talhao-os-cenario-v1', 'talhao-os-compras-v1', 'talhao-os-irrigacao-v1', 'talhao-os-mip-v1',
          'talhao-os-manutencao-v1']
CAMINHOS_04 = ['^tools/prototipo/v37/gen37/', r'^docs/pcm-suprimentos/verificacao/man_prefix\.js$',
               r'^docs/beneficiamento/verificacao/revisao\.json$']


def excecao_04():
    cfg = tomllib.loads((RAIZ / '.gitleaks.toml').read_text(encoding='utf-8'))
    regra = next(r for r in cfg['rules'] if r['id'] == 'generic-api-key')
    return next(a for a in regra['allowlists'] if '^talhao-os-manutencao-v1$' in a.get('regexes', []))


class ExcecaoDasChavesDoPrototipo(unittest.TestCase):
    def test_cinco_literais_exatos_e_tres_caminhos_com_as_duas_condicoes(self):
        a = excecao_04()
        self.assertEqual(a['condition'], 'AND')
        self.assertEqual(a['regexTarget'], 'secret')
        self.assertEqual(a['regexes'], [f'^{k}$' for k in CHAVES])
        self.assertEqual(a['paths'], CAMINHOS_04)

    def test_outro_valor_ou_outro_caminho_nao_entram(self):
        a = excecao_04()
        segredos = [re.compile(r) for r in a['regexes']]
        caminhos = [re.compile(p) for p in a['paths']]
        for k in CHAVES:
            self.assertTrue(any(s.search(k) for s in segredos), k)
        for outro in ('talhao-os-estoque-v1', 'talhao-os-mip-v2', 'ghp_' + 'A' * 36, 'xtalhao-os-mip-v1',
                      'talhao-os-mip-v1x', 'talhao-os-.*-v1'):
            self.assertFalse(any(s.search(outro) for s in segredos), outro)
        for dentro in (PREFIXO + 'mip.js', PREFIXO + 'project/MA-01.dc.html',
                       'docs/pcm-suprimentos/verificacao/man_prefix.js', 'docs/beneficiamento/verificacao/revisao.json'):
            self.assertTrue(any(c.search(dentro) for c in caminhos), dentro)
        for fora in ('apps/web/src/mip.js', 'packages/db/x.ts', 'tools/prototipo/v38/gen37/mip.js',
                     'docs/pcm-suprimentos/verificacao/outro.js', 'docs/beneficiamento/verificacao/revisao.json.bak',
                     'x/tools/prototipo/v37/gen37/mip.js'):
            self.assertFalse(any(c.search(fora) for c in caminhos), fora)


HML_SECRET_05 = ['7d38e5d50083a96b03d5a1247c31cd7518803b09:docs/integracao/PCM/diff-cdc185f-ba03515.patch:generic-api-key:3922']


class IgnoreSoComAchadoExato(unittest.TestCase):
    def test_gitleaksignore_so_com_o_fingerprint_da_hml_secret_05(self):
        linhas = [l.strip() for l in (RAIZ / '.gitleaksignore').read_text(encoding='utf-8').splitlines()]
        efetivas = [l for l in linhas if l and not l.startswith('#')]
        self.assertEqual(efetivas, HML_SECRET_05)
        for l in efetivas:
            with self.subTest(l=l):
                # commit de 40 hex, caminho exato, regra e linha: sem curinga nem fingerprint de arquivo inteiro
                self.assertRegex(l, r'^[0-9a-f]{40}:[A-Za-z0-9_./-]+:generic-api-key:[0-9]+$')
                self.assertNotIn('*', l)


if __name__ == '__main__':
    unittest.main()
