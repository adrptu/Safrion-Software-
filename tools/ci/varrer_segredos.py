# -*- coding: utf-8 -*-
"""Varredura de segredos com a CLI do Gitleaks em todo o histórico (ENG-017, ENG-047).
Substitui a gitleaks-action, que no primeiro push montava o intervalo "<commit raiz>^..HEAD": o pai do commit raiz não
existe, a varredura saía parcial com 0 bytes e o job falhava sem validar nada.
Sem --log-opts, a CLI usa "git log -p -U0 --full-history --all" (sources/git.go da v8.30.1): histórico inteiro,
sem intervalo. Passos, todos obrigatórios:
1. Canário: repositório temporário em que o commit raiz grava um segredo sintético, gerado na hora (nunca gravado neste
   repositório), e o commit seguinte o apaga. O Gitleaks tem de encontrá-lo (saída 1): prova que o histórico e o
   commit raiz são lidos, não só os arquivos atuais.
2. Varredura real, com segredos mascarados (--redact).
3. Resumo conferido (cmd/root.go da v8.30.1): "scanned ~N bytes" com N > 0, nenhuma "partial scan" e resumo coerente
   com o código de saída ("no leaks found" com 0, "leaks found: N" com 1). O log sai colorido na CI
   ("ESC[1mleaks found: 1ESC[0m", run 36339876662): as sequências ANSI são removidas antes dos regexes, porque o "m" final
   do código encosta na palavra e anula o limite \b.
4. Checkout inteiro: clone raso é recusado. No evento pull_request o checkout fica no commit de merge
   (refs/remotes/pull/N/merge); com fetch-depth 0 o "--all" alcança os commits do PR, da main e dos outros ramos. A CLI
   não chama a API do GitHub nem precisa de token, então não depende da permissão pull-requests (a gitleaks-action
   falhava com 403 em GET /pulls/N/commits no PR #2).
Saída 0 = nada encontrado e varredura conferida; 1 = segredo encontrado; 2 = verificação inválida.
Uso: python3 tools/ci/varrer_segredos.py [--gitleaks CAMINHO] [raiz]"""
import os, re, secrets, string, subprocess, sys, tempfile

args = sys.argv[1:]
gitleaks = 'gitleaks'
if '--gitleaks' in args:
    i = args.index('--gitleaks'); gitleaks = args[i + 1]; del args[i:i + 2]
raiz = os.path.abspath(args[0] if args else os.getcwd())
FLAGS = ['git', '--no-banner', '--redact', '--exit-code', '1', '--log-level', 'info']
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
BYTES = re.compile(r'scanned ~(\d+) bytes')
PARCIAL = re.compile(r'partial scan', re.I)
SEM_VAZAMENTO = re.compile(r'\bno leaks found\b')
COM_VAZAMENTO = re.compile(r'\bleaks found: (\d+)')


def git(cwd, *a):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def invalida(msg, saida=''):
    if saida:
        print(saida[-2000:])
    print('INVÁLIDO:', msg); sys.exit(2)


def varrer(repo):
    """Roda o Gitleaks e confere o resumo; devolve (saída, texto) só quando a varredura é íntegra."""
    p = subprocess.run([gitleaks, *FLAGS, repo], capture_output=True, text=True)
    texto = ANSI.sub('', (p.stdout or '') + (p.stderr or ''))
    if p.returncode not in (0, 1):
        invalida(f'Gitleaks terminou com erro (saída {p.returncode}) em {repo}', texto)
    if PARCIAL.search(texto):
        invalida(f'varredura parcial em {repo}', texto)
    b = BYTES.findall(texto)
    if not b or int(b[-1]) <= 0:
        invalida(f'Gitleaks não informou bytes varridos, ou informou 0, em {repo}', texto)
    coerente = SEM_VAZAMENTO.search(texto) if p.returncode == 0 else COM_VAZAMENTO.search(texto)
    if not coerente or (p.returncode == 0 and COM_VAZAMENTO.search(texto)):
        invalida(f'resumo do Gitleaks contradiz a saída {p.returncode} em {repo}', texto)
    return p.returncode, texto


# 1. Canário: segredo no commit raiz, apagado no commit seguinte (o caso que quebrava a action)
with tempfile.TemporaryDirectory(prefix='canario-segredos-') as d:
    git(d, 'init', '-q')
    git(d, 'config', 'user.email', 'canario@exemplo.invalid'); git(d, 'config', 'user.name', 'canario')
    token = 'ghp' + '_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36))
    with open(os.path.join(d, 'config.env'), 'w', encoding='utf-8') as f:
        f.write('GITHUB_TOKEN=' + token + '\n')
    git(d, 'add', '.'); git(d, 'commit', '-q', '-m', 'raiz com segredo')
    git(d, 'rm', '-q', 'config.env'); git(d, 'commit', '-q', '-m', 'apaga o segredo')
    code, _ = varrer(d)
    if code != 1:
        invalida('o segredo sintético do commit raiz não foi detectado; o scanner não está validando o histórico')
    print('OK canário: segredo do commit raiz, já apagado, detectado no histórico')

# 2, 3 e 4. Varredura real de todo o histórico, só com o checkout inteiro
try:
    raso = git(raiz, 'rev-parse', '--is-shallow-repository')
    total = int(git(raiz, 'rev-list', '--all', '--count'))
except subprocess.CalledProcessError as e:
    invalida(f'{raiz} não é um repositório git legível: {e.stderr.strip()}')
if raso != 'false':
    invalida('checkout raso: o histórico não está inteiro; use actions/checkout com fetch-depth: 0')
if total < 1:
    invalida('repositório sem commits')
code, texto = varrer(raiz)
if code == 1:
    print(texto[-4000:]); print(f'FALHA: segredo encontrado no histórico ({total} commits); valores mascarados.')
    sys.exit(1)
print(f'OK: histórico inteiro varrido ({total} commits), nenhum segredo encontrado.')
sys.exit(0)
