# -*- coding: utf-8 -*-
"""Varredura de segredos com a CLI do Gitleaks em todo o histórico (ENG-017, ENG-047).
Substitui a gitleaks-action, que no primeiro push montava o intervalo "<commit raiz>^..HEAD": o pai do commit raiz não
existe, a varredura saía parcial com 0 bytes e o job falhava sem validar nada.
Sem --log-opts, a CLI usa "git log -p -U0 --full-history --all --diff-filter=tuxdb" (sources/git.go da v8.30.1), e o
git log -p não mostra diff de commit de merge: um segredo que só existe na resolução de um merge (ausente nos dois pais)
passava sem achado (contraprova do Codex sobre 70a8bb6). Por isso --log-opts repete o padrão e acrescenta
--diff-merges=separate: cada merge sai com o diff contra cada pai. É explícito, e não -m, porque o -m segue a
configuração log.diffMerges, e um formato combinado (--cc) muda o diff que o Gitleaks lê. O --diff-filter do padrão
(tuxdb) também excluía a troca de tipo (letra t): um atalho que vira arquivo com segredo passava; aqui é uxdb.
Continua sem intervalo.
Configuração efetiva única (cmd/root.go da v8.30.1): a CLI escolhe --config, GITLEAKS_CONFIG, GITLEAKS_CONFIG_TOML,
(alvo)/.gitleaks.toml ou o padrão embutido, e lê .gitleaksignore de --gitleaks-ignore-path (padrão ".", a pasta de
onde se roda) e do alvo. Sem fixar, o canário (outra pasta) e a varredura real podiam usar configurações diferentes, e
uma allowlist que calasse o canário não apareceria. Por isso: variável de ambiente de configuração é recusada;
o .gitleaks.toml do repositório, se existir, vai por --config aos dois; --gitleaks-ignore-path aponta o repositório nos
dois; arquivo existente mas ilegível (pasta, atalho quebrado, sem permissão) invalida; e qualquer linha FTL (a CLI
aborta com saída 1 em configuração inválida) invalida antes de ler o resumo.
Passos, todos obrigatórios:
1. Canário: repositório temporário com três segredos sintéticos, gerados na hora (nunca gravados neste repositório) e
   já apagados: um no commit raiz; outro só na resolução de um merge com conflito, ausente nos dois pais; outro num
   atalho que vira arquivo (troca de tipo). O relatório JSON do Gitleaks tem de apontar cada um desses commits, um a
   um: prova que o histórico, o commit raiz, o diff de merge e a troca de tipo são lidos com as mesmas opções e a
   mesma configuração da varredura real, não só os arquivos atuais.
2. Varredura real, com segredos mascarados (--redact).
3. Resumo conferido (cmd/root.go da v8.30.1): "scanned ~N bytes" com N > 0, nenhuma "partial scan" e resumo coerente
   com o código de saída ("no leaks found" com 0, "leaks found: N" com 1). O log sai colorido na CI
   ("ESC[1mleaks found: 1ESC[0m", run 36339876662): as sequências ANSI são removidas antes dos regexes, porque o "m" final
   do código encosta na palavra e anula o limite \b. Com o diff por pai, o segredo que atravessa um merge conta de novo
   em cada pai: "leaks found: N" é número de achados, não de segredos distintos.
4. Checkout inteiro: clone raso é recusado. No evento pull_request o checkout fica no commit de merge
   (refs/remotes/pull/N/merge); com fetch-depth 0 o "--all" alcança os commits do PR, da main e dos outros ramos. A CLI
   não chama a API do GitHub nem precisa de token, então não depende da permissão pull-requests (a gitleaks-action
   falhava com 403 em GET /pulls/N/commits no PR #2).
Limites: git rev-list --all conta commits alcançáveis por refs; não mede o que o Gitleaks leu. Objetos sem ref ficam
fora. Uma allowlist estreita do repositório (caminho ou valor que não sejam os do canário) não é testada pelo canário.
O canário prova o mecanismo, não cobertura universal.
Saída 0 = nada encontrado e varredura conferida; 1 = segredo encontrado; 2 = verificação inválida.
Uso: python3 tools/ci/varrer_segredos.py [--gitleaks CAMINHO] [raiz]"""
import json, os, re, secrets, string, subprocess, sys, tempfile

args = sys.argv[1:]
gitleaks = 'gitleaks'
if '--gitleaks' in args:
    i = args.index('--gitleaks'); gitleaks = args[i + 1]; del args[i:i + 2]
raiz = os.path.abspath(args[0] if args else os.getcwd())
# O padrão da CLI (--full-history --all --diff-filter=tuxdb) mais o diff de cada merge contra cada pai e a troca de tipo
# (sem o t), sem intervalo.
LOG_OPTS = '--full-history --all --diff-merges=separate --diff-filter=uxdb'
FLAGS = ['git', '--no-banner', '--redact', '--exit-code', '1', '--log-level', 'info', '--log-opts=' + LOG_OPTS]
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
BYTES = re.compile(r'scanned ~(\d+) bytes')
PARCIAL = re.compile(r'partial scan', re.I)
SEM_VAZAMENTO = re.compile(r'\bno leaks found\b')
COM_VAZAMENTO = re.compile(r'\bleaks found: (\d+)')
FATAL = re.compile(r'\bFTL\b')
CONFIG = []


def git(cwd, *a):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def invalida(msg, saida=''):
    if saida:
        print(saida[-2000:])
    print('INVÁLIDO:', msg); sys.exit(2)


def varrer(repo, *extra):
    """Roda o Gitleaks e confere o resumo; devolve (saída, texto) só quando a varredura é íntegra."""
    p = subprocess.run([gitleaks, *FLAGS, *CONFIG, *extra, repo], capture_output=True, text=True)
    texto = ANSI.sub('', (p.stdout or '') + (p.stderr or ''))
    if FATAL.search(texto):
        invalida(f'Gitleaks abortou (FTL; configuração ou .gitleaksignore inválidos?) em {repo}', texto)
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


def token():
    return 'ghp' + '_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36))


def gravar(d, nome, texto):
    with open(os.path.join(d, nome), 'w', encoding='utf-8') as f:
        f.write(texto)


def commit(d, msg):
    git(d, 'add', '-A'); git(d, 'commit', '-q', '-m', msg)
    return git(d, 'rev-parse', 'HEAD')


# Configuração efetiva: a mesma, explícita, no canário e na varredura real
for var in ('GITLEAKS_CONFIG', 'GITLEAKS_CONFIG_TOML'):
    if os.environ.get(var):
        invalida(f'configuração do Gitleaks pela variável {var} não é aceita; use o .gitleaks.toml revisado no repositório')
for nome in ('.gitleaks.toml', '.gitleaksignore'):
    caminho = os.path.join(raiz, nome)
    if os.path.lexists(caminho):
        try:
            with open(caminho, encoding='utf-8') as f:
                f.read()
        except (OSError, UnicodeDecodeError) as e:
            invalida(f'{nome} existe mas está ilegível em {raiz}: {e}')
if os.path.lexists(os.path.join(raiz, '.gitleaks.toml')):
    CONFIG += ['--config', os.path.join(raiz, '.gitleaks.toml')]
CONFIG += ['--gitleaks-ignore-path', raiz]
print('Configuração do Gitleaks no canário e na varredura:',
      '.gitleaks.toml do repositório' if '--config' in CONFIG else 'padrão embutido da CLI',
      '+ .gitleaksignore do repositório' if os.path.lexists(os.path.join(raiz, '.gitleaksignore')) else '')

# 1. Canário: segredo no commit raiz, só na resolução de um merge com conflito e numa troca de tipo, todos apagados
with tempfile.TemporaryDirectory(prefix='canario-segredos-') as d, tempfile.TemporaryDirectory() as fora:
    git(d, 'init', '-q')
    git(d, 'config', 'user.email', 'canario@exemplo.invalid'); git(d, 'config', 'user.name', 'canario')
    gravar(d, 'config.env', 'GITHUB_TOKEN=' + token() + '\n')
    raiz_canario = commit(d, 'raiz com segredo')
    git(d, 'rm', '-q', 'config.env'); gravar(d, 'modo.env', 'MODO=base\n'); commit(d, 'apaga o segredo')
    principal = git(d, 'rev-parse', '--abbrev-ref', 'HEAD')
    git(d, 'checkout', '-q', '-b', 'lado'); gravar(d, 'modo.env', 'MODO=lado\n'); commit(d, 'lado muda o modo')
    git(d, 'checkout', '-q', principal); gravar(d, 'modo.env', 'MODO=principal\n'); commit(d, 'principal muda o modo')
    p = subprocess.run(['git', 'merge', '-q', '--no-ff', '--no-commit', 'lado'], cwd=d, capture_output=True, text=True)
    if p.returncode != 1 or not git(d, 'ls-files', '-u'):
        invalida('o canário não produziu o conflito de merge esperado', p.stdout + p.stderr)
    gravar(d, 'modo.env', 'MODO=resolvido\nGITHUB_TOKEN=' + token() + '\n')
    merge_canario = commit(d, 'resolve o conflito com segredo')
    gravar(d, 'modo.env', 'MODO=resolvido\n'); commit(d, 'apaga o segredo do merge')
    os.symlink('modo.env', os.path.join(d, 'tipo.env')); commit(d, 'atalho')
    os.remove(os.path.join(d, 'tipo.env')); gravar(d, 'tipo.env', 'GITHUB_TOKEN=' + token() + '\n')
    tipo_canario = commit(d, 'atalho vira arquivo com segredo')
    if not git(d, 'diff-tree', '--no-commit-id', '-r', '--diff-filter=T', tipo_canario):
        invalida('o canário não produziu a troca de tipo esperada')
    git(d, 'rm', '-q', 'tipo.env'); commit(d, 'apaga o segredo da troca de tipo')
    relatorio = os.path.join(fora, 'canario.json')
    code, texto = varrer(d, '--report-format', 'json', '--report-path', relatorio)
    if code != 1:
        invalida('os segredos sintéticos do canário não foram detectados; o scanner não está validando o histórico', texto)
    try:
        with open(relatorio, encoding='utf-8') as f:
            achados = {a.get('Commit') for a in json.load(f) or []}
    except (OSError, ValueError, AttributeError) as e:
        invalida(f'relatório JSON do canário ilegível: {e}', texto)
    if raiz_canario not in achados:
        invalida('o segredo sintético do commit raiz não foi detectado; o scanner não está validando o histórico', texto)
    if merge_canario not in achados:
        invalida('o segredo sintético da resolução de merge não foi detectado; o scanner não lê o diff de merge', texto)
    if tipo_canario not in achados:
        invalida('o segredo sintético da troca de tipo não foi detectado; o scanner exclui a troca de tipo', texto)
    print('OK canário: segredos apagados detectados no commit raiz, na resolução de merge com conflito e na troca de tipo')

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
    print(texto[-4000:])
    print('FALHA: segredo encontrado no histórico; valores mascarados. Merge repete o achado por pai: N é de achados.')
    sys.exit(1)
print(f'OK: nenhum segredo encontrado em todas as refs, com diff de merge por pai; {total} commits enumerados pelo '
      'git rev-list, contagem do repositório, não do que o Gitleaks leu.')
sys.exit(0)
