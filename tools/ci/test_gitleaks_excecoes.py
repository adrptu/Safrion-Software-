"""A exceção HML-SECRET-03 do .gitleaks.toml continua estreita: um literal exato em 25 arquivos exatos do protótipo."""
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


if __name__ == '__main__':
    unittest.main()
