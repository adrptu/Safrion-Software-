# -*- coding: utf-8 -*-
"""Regressão da proteção da main (tools/github). Roda na CI: python3 -m unittest discover -s tools/ci

Garante que os checks obrigatórios do ruleset são exatamente os jobs reais da CI, com o app GitHub Actions e strict,
sem mexer nas demais regras, e que configurar_protecao.sh só faz PUT no ruleset existente. Nada aqui usa rede.
"""
import json, os, shutil, stat, subprocess, sys, tempfile, textwrap, unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_REAL = os.path.dirname(os.path.dirname(AQUI))
GITHUB = os.path.join(RAIZ_REAL, 'tools', 'github')
sys.path.insert(0, GITHUB)
import protecao  # noqa: E402

PAYLOAD = os.path.join(GITHUB, 'protecao-main.json')
SCRIPT = os.path.join(GITHUB, 'configurar_protecao.sh')
JOBS_REAIS = [
    'Integridade da documentação',
    'Varredura de segredos (Gitleaks, histórico inteiro)',
    'Vulnerabilidades e configuração (Trivy)',
    'Código (lockfile, lint, tipos, testes, build)',
    'Construção, execução e segurança das imagens',
    'Travas de segurança do Cloud SQL',
    'Terraform — bootstrap',
    'Terraform — hml',
    'Estoque e cadastros no navegador (desktop e celular)',
    'Semgrep (regras, fixtures e inventário)',
]
# Leitura do ruleset 24154464 em 29/09/2026 (GET, campos graváveis e metadados), antes dos checks obrigatórios.
ATUAL = {
    'id': 24154464, 'name': 'safrion-main-baseline', 'target': 'branch', 'source_type': 'Repository',
    'source': 'adrptu/Safrion-Software-', 'enforcement': 'active',
    'conditions': {'ref_name': {'exclude': [], 'include': ['refs/heads/main']}},
    'rules': [
        {'type': 'deletion'},
        {'type': 'non_fast_forward'},
        {'type': 'pull_request', 'parameters': {
            'required_approving_review_count': 0, 'dismiss_stale_reviews_on_push': False, 'required_reviewers': [],
            'require_code_owner_review': False, 'require_last_push_approval': False,
            'required_review_thread_resolution': False, 'require_extra_approval_for_unattributed_changes': True,
            'allowed_merge_methods': ['merge', 'squash', 'rebase']}},
    ],
    'bypass_actors': [], 'current_user_can_bypass': 'never',
}


def texto(caminho):
    with open(caminho, encoding='utf-8') as f:
        return f.read()


def carregar():
    return json.loads(texto(PAYLOAD))


def rsc(payload):
    return next(r for r in payload['rules'] if r['type'] == 'required_status_checks')['parameters']


class ChecksObrigatorios(unittest.TestCase):
    def test_jobs_reais_dos_workflows(self):
        self.assertEqual(protecao.contextos_dos_workflows(RAIZ_REAL), JOBS_REAIS)

    def test_arquivo_do_repositorio_aplicavel_sobre_o_ruleset_atual(self):
        p = carregar()
        self.assertEqual(protecao.problemas(p, ATUAL, JOBS_REAIS), [])
        self.assertEqual([d.split(':', 1)[0] for d in protecao.diferencas(ATUAL, p)],
                         ['regra nova'], 'o arquivo só pode acrescentar a regra de checks')

    def test_contraprovas_do_arquivo(self):
        casos = {
            'nome antigo que nenhum job publica': lambda p: rsc(p)['required_status_checks'][1].update(
                context='Varredura de segredos (Gitleaks)'),
            'check faltando': lambda p: rsc(p)['required_status_checks'].pop(),
            'check repetido': lambda p: rsc(p)['required_status_checks'].append(
                dict(rsc(p)['required_status_checks'][0])),
            'sem app fixado': lambda p: rsc(p)['required_status_checks'][0].pop('integration_id'),
            'outro app': lambda p: rsc(p)['required_status_checks'][0].update(integration_id=1),
            'strict desligado': lambda p: rsc(p).update(strict_required_status_checks_policy=False),
            'bypass': lambda p: p.update(bypass_actors=[{'actor_id': 5, 'actor_type': 'RepositoryRole',
                                                         'bypass_mode': 'always'}]),
            'alvo genérico': lambda p: p['conditions']['ref_name'].update(include=['~DEFAULT_BRANCH']),
            'outro nome de ruleset': lambda p: p.update(name='Proteção da main'),
            'aprovação alterada': lambda p: next(r for r in p['rules'] if r['type'] == 'pull_request')[
                'parameters'].update(required_approving_review_count=1),
            'parâmetro existente omitido': lambda p: next(r for r in p['rules'] if r['type'] == 'pull_request')[
                'parameters'].pop('require_extra_approval_for_unattributed_changes'),
            'regra existente removida': lambda p: p.update(
                rules=[r for r in p['rules'] if r['type'] != 'non_fast_forward']),
            'sem regra de checks': lambda p: p.update(
                rules=[r for r in p['rules'] if r['type'] != 'required_status_checks']),
        }
        for nome, mudar in casos.items():
            with self.subTest(nome):
                p = carregar()
                mudar(p)
                self.assertNotEqual(protecao.problemas(p, ATUAL, JOBS_REAIS), [], nome)


class LeituraDosWorkflows(unittest.TestCase):
    def ler(self, **arquivos):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, '.github', 'workflows'))
            for nome, texto in arquivos.items():
                with open(os.path.join(d, '.github', 'workflows', nome), 'w', encoding='utf-8') as f:
                    f.write(textwrap.dedent(texto))
            return protecao.contextos_dos_workflows(d)

    def test_job_renomeado_aparece_como_divergencia(self):
        ctx = self.ler(**{'ci.yml': '''\
            on:
              pull_request:
            jobs:
              docs:
                name: Documentação renomeada
                runs-on: ubuntu-latest
            '''})
        erros = protecao.problemas(carregar(), ATUAL, ctx)
        self.assertIn('job da CI fora dos checks obrigatórios: Documentação renomeada', erros)
        self.assertIn('check sem job que o publique (travaria todo merge): Integridade da documentação', erros)

    def test_sem_nome_usa_a_chave_e_so_conta_pull_request(self):
        ctx = self.ler(**{'a.yml': 'on: [push, pull_request]\njobs:\n  teste:\n    runs-on: x\n',
                          'b.yml': 'on:\n  push:\n    branches: [main]\njobs:\n  so_push:\n    runs-on: x\n'})
        self.assertEqual(ctx, ['teste'])

    def test_formas_nao_reconhecidas_falham_fechado(self):
        casos = {
            'matrix com include': '''\
                on:
                  pull_request:
                jobs:
                  t:
                    name: T — ${{ matrix.m }}
                    strategy:
                      matrix:
                        m: [a]
                        include:
                          - m: b
                ''',
            'matrix por expressão': '''\
                on:
                  pull_request:
                jobs:
                  t:
                    name: T — ${{ matrix.m }}
                    strategy:
                      matrix: ${{ fromJSON(needs.x.outputs.m) }}
                ''',
            'expressão fora de matrix': '''\
                on:
                  pull_request:
                jobs:
                  t:
                    name: T — ${{ github.ref }}
                ''',
            'nomes repetidos': '''\
                on:
                  pull_request:
                jobs:
                  a:
                    name: Mesmo
                  b:
                    name: Mesmo
                ''',
        }
        for nome, texto in casos.items():
            with self.subTest(nome), self.assertRaises(protecao.FormaNaoReconhecida):
                self.ler(**{'w.yml': texto})

    def test_matrix_inline_expandida(self):
        ctx = self.ler(**{'w.yml': '''\
            on:
              pull_request:
            jobs:
              t:
                name: "T — ${{ matrix.m }}"
                strategy:
                  fail-fast: false
                  matrix:
                    m: [b, 'a']
            '''})
        self.assertEqual(ctx, ['T — b', 'T — a'])


GH_FALSO = r'''#!/usr/bin/env python3
import json, os, sys
d = os.environ['GH_FALSO_DIR']
a = sys.argv[1:]
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write(' '.join(a) + '\n')
metodo = a[a.index('--method') + 1] if '--method' in a else 'GET'
caminho = [x for x in a[1:] if x.startswith('repos/')][0]
if metodo == 'GET' and caminho.endswith('/rulesets'):
    print(open(os.path.join(d, 'lista.json'), encoding='utf-8').read())
elif metodo == 'GET':
    print(open(os.path.join(d, 'ruleset.json'), encoding='utf-8').read())
elif metodo == 'PUT':
    corpo = json.load(open(a[a.index('--input') + 1], encoding='utf-8'))
    atual = json.load(open(os.path.join(d, 'ruleset.json'), encoding='utf-8'))
    novo = {**atual, **corpo}
    for r in novo['rules']:
        if r['type'] == 'required_status_checks' and os.environ.get('GH_FALSO_PERDE_CHECK'):
            r['parameters']['required_status_checks'].pop()
    novo['rules'] = list(reversed(novo['rules']))
    json.dump(novo, open(os.path.join(d, 'ruleset.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('{}')
else:
    sys.exit(9)
'''


class ScriptSemRede(unittest.TestCase):
    def rodar(self, *args, lista=None, ambiente=None, payload=None):
        """Roda o script numa cópia (workflows reais + tools/github), com gh falso; o repositório não é tocado."""
        with tempfile.TemporaryDirectory() as d:
            copia = os.path.join(d, 'repo')
            shutil.copytree(os.path.join(RAIZ_REAL, '.github', 'workflows'), os.path.join(copia, '.github', 'workflows'))
            os.makedirs(os.path.join(copia, 'tools', 'github'))
            for nome in ('configurar_protecao.sh', 'protecao.py'):
                shutil.copy(os.path.join(GITHUB, nome), os.path.join(copia, 'tools', 'github', nome))
            with open(os.path.join(copia, 'tools', 'github', 'protecao-main.json'), 'w', encoding='utf-8') as f:
                json.dump(payload if payload is not None else carregar(), f, ensure_ascii=False)
            bin_ = os.path.join(d, 'bin')
            os.makedirs(bin_)
            gh = os.path.join(bin_, 'gh')
            with open(gh, 'w', encoding='utf-8') as f:
                f.write(GH_FALSO)
            os.chmod(gh, os.stat(gh).st_mode | stat.S_IEXEC)
            with open(os.path.join(d, 'lista.json'), 'w', encoding='utf-8') as f:
                json.dump(lista if lista is not None else [
                    {'id': 24154464, 'name': 'safrion-main-baseline', 'target': 'branch'},
                    {'id': 7, 'name': 'outra', 'target': 'tag'}], f)
            with open(os.path.join(d, 'ruleset.json'), 'w', encoding='utf-8') as f:
                json.dump(ATUAL, f, ensure_ascii=False)
            env = {**os.environ, 'PATH': bin_ + os.pathsep + os.environ['PATH'], 'GH_FALSO_DIR': d, **(ambiente or {})}
            r = subprocess.run(['bash', os.path.join(copia, 'tools', 'github', 'configurar_protecao.sh'),
                                'adrptu/Safrion-Software-', *args], capture_output=True, text=True, env=env)
            log = os.path.join(d, 'chamadas.log')
            chamadas = texto(log).splitlines() if os.path.exists(log) else []
            final = json.loads(texto(os.path.join(d, 'ruleset.json')))
            return r, chamadas, final

    def test_simulacao_nao_grava(self):
        r, chamadas, final = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('regra nova: required_status_checks', r.stdout)
        self.assertFalse([c for c in chamadas if '--method' in c], chamadas)
        self.assertEqual(final, ATUAL)

    def test_aplicar_faz_um_put_no_mesmo_id_e_confere(self):
        r, chamadas, final = self.rodar('--aplicar')
        self.assertEqual(r.returncode, 0, r.stderr)
        escritas = [c for c in chamadas if '--method' in c]
        self.assertEqual(len(escritas), 1, chamadas)
        self.assertIn('--method PUT', escritas[0])
        self.assertIn('repos/adrptu/Safrion-Software-/rulesets/24154464', escritas[0])
        self.assertIn('OK: a leitura de volta é igual', r.stdout)
        self.assertEqual(protecao.diferencas(final, carregar()), [])

    def test_leitura_de_volta_divergente_falha(self):
        r, _, _ = self.rodar('--aplicar', ambiente={'GH_FALSO_PERDE_CHECK': '1'})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('ERRO na leitura de volta', r.stderr)

    def test_ruleset_ausente_ou_duplicado_nao_grava(self):
        for nome, lista in {'ausente': [], 'duplicado': [
                {'id': 1, 'name': 'safrion-main-baseline', 'target': 'branch'},
                {'id': 2, 'name': 'safrion-main-baseline', 'target': 'branch'}]}.items():
            with self.subTest(nome):
                r, chamadas, final = self.rodar('--aplicar', lista=lista)
                self.assertNotEqual(r.returncode, 0)
                self.assertFalse([c for c in chamadas if '--method' in c], chamadas)
                self.assertEqual(final, ATUAL)

    def test_arquivo_invalido_nao_grava(self):
        p = carregar()
        rsc(p)['strict_required_status_checks_policy'] = False
        r, chamadas, final = self.rodar('--aplicar', payload=p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('strict_required_status_checks_policy precisa ser true', r.stderr)
        self.assertFalse([c for c in chamadas if '--method' in c], chamadas)
        self.assertEqual(final, ATUAL)

    def test_script_nunca_cria_ruleset(self):
        self.assertNotIn('POST', texto(SCRIPT))
        self.assertEqual(subprocess.run(['bash', '-n', SCRIPT]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
