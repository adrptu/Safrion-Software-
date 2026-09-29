# -*- coding: utf-8 -*-
"""Regressão da varredura de segredos (commit raiz, merge, histórico normal, cobertura e canário), com um Gitleaks simulado.
O Gitleaks real roda no job de segredos da CI, com checksum conferido; aqui se testa o contrato do script. O simulado lê
o git log -p com as mesmas --log-opts recebidas, então a detecção de merge depende das opções que o script passa."""
import json, os, stat, subprocess, sys, tempfile, textwrap, unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'varrer_segredos.py')
CI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.github', 'workflows', 'ci.yml')
SIMULADO = textwrap.dedent('''
    # Imita o resumo da CLI 8.30.1 (cmd/root.go): "scanned ~N bytes", "no leaks found" / "leaks found: N", "partial scan".
    import json, os, subprocess, sys
    modo = os.environ.get('SIM_MODO', 'ok'); repo = sys.argv[-1]; cor = os.environ.get('SIM_COR') == '1'
    def diz(nivel, msg):
        # Com SIM_COR=1 imita o console colorido da CI: hora cinza, nível colorido e mensagem em negrito.
        print(f'\x1b[90m3:04PM\x1b[0m \x1b[32m{nivel}\x1b[0m \x1b[1m{msg}\x1b[0m' if cor else f'{nivel} {msg}')
    def git(*a, ok=(0,)):
        p = subprocess.run(['git', *a], cwd=repo, capture_output=True, text=True)
        assert p.returncode in ok, (a, p.stderr)
        return p
    def tem_segredo(rev, arquivo):
        p = git('show', f'{rev}:{arquivo}', ok=(0, 128))
        return p.returncode == 0 and 'GITHUB_TOKEN=ghp' in p.stdout
    canario = os.path.basename(repo).startswith('canario-segredos-')
    # Como a CLI: com --log-opts, "git log -p -U0" mais as opções recebidas; sem, o padrão de sources/git.go.
    opcoes = [a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--log-opts=')]
    opcoes = opcoes[0].split(' ') if opcoes else ['--full-history', '--all', '--diff-filter=tuxdb']
    if canario and modo == 'canario_sem_merge': opcoes = [o for o in opcoes if o not in ('-m', '--diff-merges=separate')]
    achados, atual = [], None
    for linha in git('log', '-p', '-U0', *opcoes).stdout.splitlines():
        if linha.startswith('commit '): atual = linha.split()[1]
        elif linha.startswith('+') and not linha.startswith('+++') and 'GITHUB_TOKEN=ghp' in linha: achados.append(atual)
    if canario and modo == 'canario_sem_raiz':
        raizes = set(git('rev-list', '--max-parents=0', '--all').stdout.split()); achados = [c for c in achados if c not in raizes]
    info = {'args': sys.argv[1:], 'canario': canario, 'token': 'GITHUB_TOKEN' in os.environ,
            'commits': int(git('rev-list', '--all', '--count').stdout)}
    if canario:
        raiz = git('rev-list', '--max-parents=0', '--all').stdout.split()
        merges = git('rev-list', '--min-parents=2', '--all').stdout.split()
        pais = git('show', '-s', '--format=%P', merges[0]).stdout.split() if len(merges) == 1 else []
        info['raiz_com_segredo'] = len(raiz) == 1 and tem_segredo(raiz[0], 'config.env')
        info['merge_com_segredo'] = bool(pais) and tem_segredo(merges[0], 'modo.env')
        info['pais_do_merge'] = len(pais)
        info['pais_sem_segredo'] = bool(pais) and not any(tem_segredo(p, 'modo.env') for p in pais)
        info['conflito'] = bool(pais) and git('merge-tree', '--write-tree', *pais, ok=(0, 1)).returncode == 1
        info['segredo_na_arvore'] = any(tem_segredo('HEAD', a) for a in ('config.env', 'modo.env'))
        info['commits_achados'] = sorted(set(achados)); info['raiz'] = raiz; info['merges'] = merges
    with open(os.environ['SIM_LOG'], 'a', encoding='utf-8') as f: f.write(json.dumps(info) + '\\n')
    if '--report-path' in sys.argv and modo != 'sem_relatorio':
        with open(sys.argv[sys.argv.index('--report-path') + 1], 'w', encoding='utf-8') as f:
            json.dump([{'Commit': c, 'RuleID': 'github-pat', 'Secret': 'REDACTED'} for c in achados], f)
    if modo == 'erro': diz('ERR', 'fatal'); sys.exit(126)
    if modo == 'sem_resumo': sys.exit(0)
    if modo == 'parcial': diz('WRN', 'scanned ~0 bytes (0)'); diz('WRN', 'partial scan completed in 1ms'); diz('WRN', 'no leaks found in partial scan'); sys.exit(1)
    if modo == 'zero_bytes': diz('INF', 'scanned ~0 bytes (0) in 1ms'); diz('INF', 'no leaks found'); sys.exit(0)
    diz('INF', 'scanned ~2048 bytes (2.05 KB) in 12ms')
    if canario:
        if modo == 'canario_cego' or not achados: diz('INF', 'no leaks found'); sys.exit(0)
        diz('WRN', f'leaks found: {len(achados)}'); sys.exit(1)
    if modo == 'contraditorio': diz('WRN', 'leaks found: 2'); sys.exit(0)
    if modo == 'vazamento' or achados: diz('WRN', f'leaks found: {len(achados) or 1}'); sys.exit(1)
    diz('INF', 'no leaks found'); sys.exit(0)
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

    def repo_com_segredo_no_merge(self, octopus=False):
        """Contraprova A do Codex: segredo sintético só no commit de merge (conflito resolvido ou arquivo novo no octopus),
        ausente em todos os pais e apagado no commit seguinte. Valor fixo de teste, montado na hora."""
        r = self.repo(False); segredo = 'GITHUB_TOKEN=ghp' + '_' + 'x' * 36 + '\n'
        escrever(os.path.join(r, 'modo.env'), 'MODO=base\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'base')
        ramos = ['um', 'dois'] if octopus else ['lado']
        for ramo in ramos:
            git(r, 'checkout', '-q', '-b', ramo, 'main'); escrever(os.path.join(r, ramo + '.txt'), ramo + '\n')
            if not octopus:
                escrever(os.path.join(r, 'modo.env'), 'MODO=lado\n')
            git(r, 'add', '.'); git(r, 'commit', '-q', '-m', ramo)
        git(r, 'checkout', '-q', 'main')
        if octopus:
            git(r, 'merge', '-q', '--no-ff', '--no-commit', *ramos); escrever(os.path.join(r, 'novo.env'), segredo)
        else:
            escrever(os.path.join(r, 'modo.env'), 'MODO=principal\n'); git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'principal')
            p = subprocess.run(['git', 'merge', '-q', '--no-ff', '--no-commit', 'lado'], cwd=r, capture_output=True, text=True)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            escrever(os.path.join(r, 'modo.env'), 'MODO=resolvido\n' + segredo)
        git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'merge com segredo')
        pais = subprocess.run(['git', 'show', '-s', '--format=%P'], cwd=r, capture_output=True, text=True).stdout.split()
        self.assertEqual(len(pais), 3 if octopus else 2)
        git(r, 'rm', '-q', '--ignore-unmatch', 'novo.env'); escrever(os.path.join(r, 'modo.env'), 'MODO=resolvido\n')
        git(r, 'add', '.'); git(r, 'commit', '-q', '-m', 'apaga o segredo')
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

    def rodar(self, repo, modo='ok', sem_token=False, cor=False):
        env = {**os.environ, 'SIM_MODO': modo, 'SIM_LOG': self.log, 'SIM_COR': '1' if cor else '0'}
        if sem_token:
            env.pop('GITHUB_TOKEN', None)
        p = subprocess.run([sys.executable, SCRIPT, '--gitleaks', self.bin, repo], capture_output=True, text=True, env=env)
        return p.returncode, p.stdout

    def chamadas(self):
        with open(self.log, encoding='utf-8') as f:
            return [json.loads(l) for l in f.read().splitlines()]

    def test_repositorio_so_com_commit_raiz_passa(self):
        code, out = self.rodar(self.repo(False))
        self.assertEqual(code, 0, out); self.assertIn('1 commits enumerados', out)

    def test_historico_normal_passa(self):
        code, out = self.rodar(self.repo(True))
        self.assertEqual(code, 0, out); self.assertIn('nenhum segredo encontrado', out)
        # A contagem do rev-list é do repositório; a mensagem não pode apresentá-la como cobertura do scanner.
        self.assertIn('não do que o Gitleaks leu', out); self.assertNotIn('histórico inteiro varrido', out)

    def test_padrao_da_cli_mais_diff_de_merge_sem_intervalo_e_mascarado(self):
        self.rodar(self.repo(True))
        cs = self.chamadas(); self.assertEqual([c['canario'] for c in cs], [True, False])
        for c in cs:
            opcoes = [a for a in c['args'] if a.startswith('--log-opts')]
            self.assertEqual(opcoes, ['--log-opts=--full-history --all --diff-merges=separate --diff-filter=tuxdb'])
            texto = ' '.join(c['args']); self.assertNotIn('^', texto); self.assertNotIn('..', texto); self.assertIn('--redact', texto)
        # Só o canário pede relatório: é nele que o commit de cada achado é conferido.
        self.assertIn('--report-path', cs[0]['args']); self.assertNotIn('--report-path', cs[1]['args'])

    def test_canario_tem_segredos_so_no_historico_da_raiz_e_da_resolucao_de_merge(self):
        self.rodar(self.repo(False))
        c = self.chamadas()[0]
        self.assertEqual(c['commits'], 6); self.assertTrue(c['raiz_com_segredo']); self.assertFalse(c['segredo_na_arvore'])
        self.assertEqual(c['pais_do_merge'], 2); self.assertTrue(c['conflito'])
        self.assertTrue(c['merge_com_segredo']); self.assertTrue(c['pais_sem_segredo'])
        self.assertEqual(c['commits_achados'], sorted(c['raiz'] + c['merges']))

    def test_segredo_so_na_resolucao_de_merge_falha(self):
        # Contraprova A sobre 70a8bb6: sem diff de merge, a varredura dava 0 e "histórico inteiro varrido".
        code, out = self.rodar(self.repo_com_segredo_no_merge())
        self.assertEqual(code, 1, out); self.assertIn('segredo encontrado', out)

    def test_segredo_so_no_merge_octopus_falha(self):
        code, out = self.rodar(self.repo_com_segredo_no_merge(octopus=True))
        self.assertEqual(code, 1, out); self.assertIn('segredo encontrado', out)

    def test_canario_sem_diff_de_merge_invalida(self):
        code, out = self.rodar(self.repo(False), 'canario_sem_merge')
        self.assertEqual(code, 2, out); self.assertIn('não lê o diff de merge', out)

    def test_canario_sem_commit_raiz_invalida(self):
        code, out = self.rodar(self.repo(False), 'canario_sem_raiz')
        self.assertEqual(code, 2, out); self.assertIn('commit raiz não foi detectado', out)

    def test_canario_sem_relatorio_invalida(self):
        code, out = self.rodar(self.repo(False), 'sem_relatorio')
        self.assertEqual(code, 2, out); self.assertIn('relatório JSON do canário ilegível', out)

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
        self.assertEqual(code, 0, out); self.assertIn('9 commits enumerados', out)
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

    def test_log_colorido_da_ci(self):
        # Run 36339876662: o canário achou o segredo (saída 1), mas "ESC[1mleaks found: 1" não casava com \bleaks.
        r = self.repo(True)
        casos = [('ok', 0, 'nenhum segredo encontrado'), ('vazamento', 1, 'segredo encontrado'),
                 ('parcial', 2, 'parcial'), ('zero_bytes', 2, 'bytes varridos'), ('contraditorio', 2, 'contradiz'),
                 ('canario_cego', 2, 'não está validando')]
        for modo, esperado, trecho in casos:
            with self.subTest(modo=modo):
                code, out = self.rodar(r, modo, cor=True)
                self.assertEqual(code, esperado, out); self.assertIn(trecho, out)

    def test_canario_nao_fica_gravado_no_repositorio(self):
        with open(SCRIPT, encoding='utf-8') as a, open(__file__, encoding='utf-8') as b:
            texto = a.read() + b.read()
        self.assertNotRegex(texto, r'ghp_[0-9A-Za-z]{36}')


if __name__ == '__main__':
    unittest.main()
