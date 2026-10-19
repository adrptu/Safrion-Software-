"""As exceções do .gitleaks.toml continuam estreitas: HML-SECRET-03 (um literal exato em 25 arquivos exatos do protótipo)
e HML-SECRET-04 (cinco nomes exatos de chave de localStorage, só no protótipo e em dois arquivos de especificação).
O .gitleaksignore tem só os achados exatos da HML-SECRET-05, HML-SECRET-06 (DEC-1610-15: 31 nomes de chave de
localStorage em commits antigos) e HML-SECRET-07 (duas fingerprints autorizadas no recibo6265042151),
cada um com commit, arquivo, regra e linha, sem curinga."""
from pathlib import Path
import re
import json
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


HML_SECRET_06 = [
    '207f3623cdfb9059b46774f64245bc4ef735993f:work/prototipo-fase1/gen37/painel_modulos_test.py:generic-api-key:91',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/CD-03.dc.html:generic-api-key:3724',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IN-03.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IN-03.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IN-04.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IN-04.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-01.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-01.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-02.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-02.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-03.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-03.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-03det.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-03det.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-04.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/_render/IR-04.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/CD-03.dc.html:generic-api-key:3724',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IN-03.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IN-03.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IN-04.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IN-04.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-01.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-01.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-02.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-02.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-03.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-03.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-03det.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-03det.dc.html:generic-api-key:3648',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-04.dc.html:generic-api-key:3591',
    'f6d7486eb732c259bdf89cfbaaf26ef269299b8d:tools/prototipo/v37/gen37/project/IR-04.dc.html:generic-api-key:3648',
]
# Só os dois commits antigos listados no PR #73 (comentário 6217016316); nenhum é ponta de branch ativa.
COMMITS_06 = {'f6d7486eb732c259bdf89cfbaaf26ef269299b8d', '207f3623cdfb9059b46774f64245bc4ef735993f'}

HML_SECRET_07 = [
    '6cd9919ac5ede6e43a60e877463bb0f6bd7b7785:tools/prototipo/v37/gen37/sup_politicas.js:generic-api-key:2',
    '0a9c4a70180c9fcf2ea9f79f2b492ed389b5eae4:docs/integracao/V71/ex38-codex/r2/gitleaks.txt:generic-api-key:1',
]


class IgnoreSoComAchadoExato(unittest.TestCase):
    def test_gitleaksignore_so_com_os_achados_exatos_autorizados(self):
        linhas = [l.strip() for l in (RAIZ / '.gitleaksignore').read_text(encoding='utf-8').splitlines()]
        efetivas = [l for l in linhas if l and not l.startswith('#')]
        self.assertEqual(efetivas, HML_SECRET_05 + HML_SECRET_06 + HML_SECRET_07)
        self.assertEqual(len(set(efetivas)), len(efetivas))
        self.assertEqual({l.split(':')[0] for l in HML_SECRET_06}, COMMITS_06)
        for l in efetivas:
            with self.subTest(l=l):
                # commit de 40 hex, caminho exato, regra e linha: sem curinga nem fingerprint de arquivo inteiro
                self.assertRegex(l, r'^[0-9a-f]{40}:[A-Za-z0-9_./-]+:generic-api-key:[0-9]+$')
                self.assertNotIn('*', l)


class ExcecaoDaFichaDePivo(unittest.TestCase):
    """Contrato descoberto pela CI; os scans reais estão na rodada VEL-20261013-01."""

    def excecao(self):
        cfg = tomllib.loads((RAIZ / '.gitleaks.toml').read_text(encoding='utf-8'))
        self.assertTrue(cfg['extend']['useDefault'])
        regra = next(r for r in cfg['rules'] if r['id'] == 'generic-api-key')
        candidatas = [a for a in regra['allowlists'] if '^talhao-os-ficha-pivo-v1$' in a.get('regexes', [])]
        self.assertEqual(len(candidatas), 1)
        return candidatas[0]

    def test_um_literal_dois_arquivos_e_duas_condicoes(self):
        a = self.excecao()
        self.assertEqual(a['condition'], 'AND')
        self.assertEqual(a['regexTarget'], 'secret')
        self.assertEqual(a['regexes'], ['^talhao-os-ficha-pivo-v1$'])
        self.assertEqual(a['paths'], [r'^tools/prototipo/v37/gen37/ficha_pivo\.py$',
                                      r'^tools/prototipo/v37/gen37/irrigacao_estado\.js$'])

    def test_outras_excecoes_nao_ampliam_a_permissao_efetiva(self):
        cfg = tomllib.loads((RAIZ / '.gitleaks.toml').read_text(encoding='utf-8'))
        # Novas formas de exceção precisam de revisão e contraprova do detector real.
        self.assertFalse(cfg.get('allowlist'))
        self.assertFalse(cfg.get('allowlists'))
        regras = [r for r in cfg['rules'] if r['id'] == 'generic-api-key']
        self.assertEqual(len(regras), 1, 'Regra duplicada pode sobrescrever a configuração efetiva.')
        regra = regras[0]
        self.assertEqual(set(regra), {'id', 'allowlists'}, 'A regra padrão não pode receber sobrescritas.')
        self.assertEqual(cfg['extend'], {'useDefault': True}, 'Manter todas as regras herdadas, sem configuração adicional.')
        self.assertFalse(regra.get('allowlist'))
        referencia = json.loads((RAIZ / 'tools/ci/fixtures/gitleaks_generic_allowlists.json').read_text(encoding='utf-8'))
        self.assertEqual(regra['allowlists'], referencia,
                         'Exceção nova ou alterada exige revisão explícita da referência autorizada.')
        literais = ('talhao-os-ficha-pivo-v1', 'talhao-os-ficha-pivo-v2',
                    'Q9x7-talhao-os-ficha-pivo-v1', 'talhao-os-ficha-pivo-v1-7zW2', 'ghp_' + 'A' * 36)
        autorizados = (PREFIXO + 'ficha_pivo.py', PREFIXO + 'irrigacao_estado.js')
        caminhos = list(autorizados) + [PREFIXO + 'outra_ficha.py']
        for dentro in autorizados:
            caminhos.extend((dentro + '.bak', 'backup/' + dentro,
                             dentro.replace('gen37/', 'gen370/'), dentro.replace('.', 'X')))
        for a in regra['allowlists']:
            with self.subTest(excecao=a.get('description')):
                self.assertLessEqual(set(a), {'description', 'condition', 'regexTarget', 'paths', 'regexes'})
                self.assertEqual(a.get('regexTarget'), 'secret')
                self.assertEqual(a.get('condition'), 'AND')
                self.assertTrue(a.get('paths'))
                self.assertTrue(a.get('regexes'))
                for valor in literais:
                    for caminho in caminhos:
                        permitido = (valor == literais[0] and caminho in autorizados)
                        combina = (any(re.search(r, valor) for r in a['regexes'])
                                   and any(re.search(r, caminho) for r in a['paths']))
                        with self.subTest(valor=valor, caminho=caminho):
                            self.assertFalse(combina and not permitido)

    def test_limites_do_valor_e_do_caminho(self):
        a = self.excecao()
        segredo = re.compile(a['regexes'][0])
        caminhos = [re.compile(p) for p in a['paths']]
        literal = 'talhao-os-ficha-pivo-v1'
        self.assertTrue(segredo.search(literal))
        for outro in ('talhao-os-ficha-pivo-v2', 'Q9x7-' + literal, literal + '-7zW2', 'ghp_' + 'A' * 36):
            self.assertIsNone(segredo.search(outro), outro)
        for arquivo in ('ficha_pivo.py', 'irrigacao_estado.js'):
            dentro = PREFIXO + arquivo
            self.assertTrue(any(c.search(dentro) for c in caminhos), dentro)
            for fora in (dentro + '.bak', 'backup/' + dentro, dentro.replace('gen37/', 'gen370/'),
                         dentro.replace('.', 'X'), PREFIXO + 'outra_ficha.py'):
                self.assertFalse(any(c.search(fora) for c in caminhos), fora)


if __name__ == '__main__':
    unittest.main()
