# -*- coding: utf-8 -*-
"""Regressão da varredura de segredos (commit raiz, histórico normal, cobertura e canário), com um Gitleaks simulado.
O Gitleaks real roda no job de segredos da CI, com checksum conferido; aqui se testa o contrato do script."""
import json, os, stat, subprocess, sys, tempfile, textwrap, unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'varrer_segredos.py')
CI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.github', 'workflows', 'ci.yml')
SIMULADO = textwrap.dedent('''
    # Imita o resumo da CLI 8.30.1 (cmd/root.go): "scanned ~N bytes", "no leaks found" / "leaks found: N", "partial scan".
    import json, os, subprocess, sys
    modo = os.environ.get('SIM_MODO', 'ok'); repo = sys.argv[-1]
    canario = os.path.basename(repo).startswith('canario-segredos-')
    info = {'args': sys.argv[1:], 'canario': canario, 'token': 'GITHUB_TOKEN' in os.environ,
            'commits': int(subprocess.run(['git', 'rev-list', '--all', '--count'], cwd=repo, capture_output=True, text=True).stdout)}
    if canario:
        log = subprocess.run(['git', 'log', '--all', '-p', '--format=%H'], cwd=repo, capture_output=True, text=True).stdout
        info['segredo_no_historico'] = '+GITHUB_TOKEN=ghp' in log
        info['segredo_na_arvore'] = os.path.exists(os.path.join(repo, 'config.env'))
    with open(os.environ['SIM_LOG'], 'a', encoding='utf-8') as f: f.write(json.dumps(info) + '\\n')
    if modo == 'erro': print('ERR fatal'); sys.exit(126)
    if modo == 'sem_resumo': sys.exit(0)
    if modo == 'parcial': print('WRN scanned ~0 bytes (0)'); print('WRN partial scan completed in 1ms'); print('WRN no leaks found in partial scan'); sys.exit(1)
    if modo == 'zero_bytes': print('INF scanned ~0 bytes (0) in 1ms'); print('INF no leaks found'); sys.exit(0)
    print('INF scanned ~2048 bytes (2.05 KB) in 12ms')
    if canario:
        if modo == 'canario_cego': print('INF no leaks found'); sys.exit(0)
        print('WRN leaks found: 1'); sys.exit(1)
    if modo == 'contraditorio': print('WRN leaks found: 2'); sys.exit(0)
    if modo == 'vazamento': print('WRN leaks found: 1'); sys.exit(1)
    print('INF no leaks found'); sys.exit(0)
''')


def git(cwd, *a):
    subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, check=True)


def escrever(caminho, texto):
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(texto)


class VarrerSegredos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = self.tmp.name
        sim = os.path.join(d, 'sim.py'); escrever(sim, SIMULADO)
        self.bin = os.path.join(d, 'gitleaks'); self.log = os.path.join(d, 'args.log')
        escrever(self.bin, f'#!/bin/sh\nexec "{sys.executable}" "{sim}" "$@"\n')
        os.chmod(self.bin, os.stat(self.bin).st_mode | stat.S_IEXEC)

    def tearDown(self):
        self.tmp.cleanup()

    def repo(self, historico_normal):
        r = tempfile.mkdtemp(dir=self.tmp.name)
        git(r, 'init', '-q', '-b', 'main'); git(r, 'config', 'user.email', 't@exemplo.invalid'); git(r, 'config', 'user.name', 't')
        escrever(os.path.join(r, 'a.txt'), 'a\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'raiz')
        if historico_normal:
            git(r, 'checkout', '-q', '-b', 'ramo'); escrever(os.path.join(r, 'b.txt'), 'b\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'b')
            git(r, 'checkout', '-q', 'main'); escrever(os.path.join(r, 'c.txt'), 'c\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'c')
            git(r, 'merge', '-q', '--no-ff', '-m', 'merge', 'ramo'); git(r, 'commit', '-q', '--allow-empty', '-m', 'vazio')
        return r

    def checkout_de_pull_request(self):
        """Estado do actions/checkout no evento pull_request com fetch-depth 0: HEAD destacado no commit de merge
        (refs/remotes/pull/2/merge) e os commits do PR alcançáveis só por esse ref."""
        r = self.repo(True)
        git(r, 'checkout', '-q', '-b', 'pr'); escrever(os.path.join(r, 'd.txt'), 'd\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'pr 1')
        git(r, 'commit', '-q', '--allow-empty', '-m', 'pr 2')
        git(r, 'checkout', '-q', 'main'); escrever(os.path.join(r, 'e.txt'), 'e\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'main nova')
        git(r, 'checkout', '-q', '--detach', 'main'); git(r, 'merge', '-q', '--no-ff', '-m', 'Merge pr into main', 'pr')
        git(r, 'update-ref', 'refs/remotes/pull/2/merge', 'HEAD'); git(r, 'branch', '-q', '-D', 'pr')
        return r

    def rodar(self, repo, modo='ok', sem_token=False):
        env = {**os.environ, 'SIM_MODO': modo, 'SIM_LOG': self.log}
        if sem_token:
            env.pop('GITHUB_TOKEN', None)
        p = subprocess.run([sys.executable, SCRIPT, '--gitleaks', self.bin, repo], capture_output=True, text=True, env=env)
        return p.returncode, p.stdout

    def chamadas(self):
        with open(self.log, encoding='utf-8') as f:
            return [json.loads(l) for l in f.read().splitlines()]

    def test_repositorio_so_com_commit_raiz_passa(self):
        code, out = self.rodar(self.repo(False))
        self.assertEqual(code, 0, out); self.assertIn('1 commits', out)

    def test_historico_normal_passa(self):
        code, out = self.rodar(self.repo(True))
        self.assertEqual(code, 0, out); self.assertIn('histórico inteiro varrido', out)

    def test_sem_intervalo_e_com_segredos_mascarados(self):
        self.rodar(self.repo(True))
        cs = self.chamadas(); self.assertEqual([c['canario'] for c in cs], [True, False])
        for c in cs:
            texto = ' '.join(c['args'])
            self.assertNotIn('--log-opts', texto); self.assertNotIn('^', texto); self.assertIn('--redact', texto)

    def test_canario_tem_segredo_so_no_historico_do_commit_raiz(self):
        self.rodar(self.repo(False))
        c = self.chamadas()[0]
        self.assertEqual(c['commits'], 2); self.assertTrue(c['segredo_no_historico']); self.assertFalse(c['segredo_na_arvore'])

    def test_segredo_no_historico_falha(self):
        code, out = self.rodar(self.repo(True), 'vazamento')
        self.assertEqual(code, 1, out); self.assertIn('segredo encontrado', out)

    def test_canario_nao_detectado_invalida(self):
        code, out = self.rodar(self.repo(False), 'canario_cego')
        self.assertEqual(code, 2, out); self.assertIn('não está validando', out)

    def test_varredura_parcial_invalida(self):
        code, out = self.rodar(self.repo(False), 'parcial')
        self.assertEqual(code, 2, out); self.assertIn('parcial', out)

    def test_zero_bytes_invalida(self):
        self.assertEqual(self.rodar(self.repo(False), 'zero_bytes')[0], 2)

    def test_resumo_contraditorio_invalida(self):
        self.assertEqual(self.rodar(self.repo(False), 'contraditorio')[0], 2)

    def test_sem_resumo_invalida(self):
        self.assertEqual(self.rodar(self.repo(False), 'sem_resumo')[0], 2)

    def test_erro_do_gitleaks_invalida(self):
        self.assertEqual(self.rodar(self.repo(False), 'erro')[0], 2)

    def test_evento_pull_request_varre_merge_e_commits_do_pr_sem_token(self):
        # PR #2: a gitleaks-action pedia GET /pulls/2/commits e recebia 403 sem pull-requests: read. A CLI não usa a API.
        r = self.checkout_de_pull_request()
        code, out = self.rodar(r, sem_token=True)
        self.assertEqual(code, 0, out); self.assertIn('(9 commits)', out)
        real = self.chamadas()[1]
        self.assertFalse(real['canario']); self.assertFalse(real['token']); self.assertEqual(real['commits'], 9)

    def test_checkout_raso_invalida(self):
        origem = self.checkout_de_pull_request()
        raso = os.path.join(self.tmp.name, 'raso')
        subprocess.run(['git', 'clone', '-q', '--depth', '1', 'file://' + origem, raso], capture_output=True, check=True)
        code, out = self.rodar(raso)
        self.assertEqual(code, 2, out); self.assertIn('checkout raso', out)

    def test_job_de_segredos_nao_depende_da_api_do_github(self):
        with open(CI, encoding='utf-8') as f:
            ci = f.read()
        inicio = ci.index('\n  segredos:\n')
        fim = ci.find('\n  ', ci.find('\n', inicio + 1))
        while fim != -1 and ci[fim + 3] == ' ':
            fim = ci.find('\n  ', fim + 1)
        job = '\n'.join(l for l in ci[inicio:fim if fim != -1 else len(ci)].splitlines() if not l.lstrip().startswith('#'))
        self.assertIn('pull_request:', ci.split('jobs:')[0])
        self.assertNotIn('pull-requests', ci.split('jobs:')[0])
        self.assertIn('fetch-depth: 0', job)
        for proibido in ('gitleaks-action', 'GITHUB_TOKEN', 'secrets.', 'api.github.com'):
            self.assertNotIn(proibido, job)
        self.assertIn('varrer_segredos.py', job)

    def test_canario_nao_fica_gravado_no_repositorio(self):
        with open(SCRIPT, encoding='utf-8') as a, open(__file__, encoding='utf-8') as b:
            texto = a.read() + b.read()
        self.assertNotRegex(texto, r'ghp_[0-9A-Za-z]{36}')


if __name__ == '__main__':
    unittest.main()
