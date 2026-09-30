# -*- coding: utf-8 -*-
"""Regressão do cloudshell.sh sem rede nem nuvem: gcloud, gh, terraform, tflint, curl, uname e git fetch falsos.
Roda na CI: python3 -m unittest discover -s infra/terraform -p 'test_*.py'"""
import hashlib, io, json, os, re, shutil, stat, subprocess, tempfile, unittest, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ_REAL = AQUI.parent.parent
REPO = 'https://github.com/adrptu/Safrion-Software-.git'
DONO = 'dono@example.com'
PROJETO = 'safrion-hml-teste'
COMPUTE = '999-compute@developer.gserviceaccount.com'

# Estado do projeto falso em gcloud.json. Os erros simulados trazem o e-mail da conta, como os do Google.
GCLOUD = r'''#!/usr/bin/env python3
import json, os, sys
d = os.environ['FALSO']
e = json.load(open(os.path.join(d, 'gcloud.json'), encoding='utf-8'))
a = sys.argv[1:]
j = ' '.join(a)
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write('gcloud ' + j + '\n')
def salvar():
    json.dump(e, open(os.path.join(d, 'gcloud.json'), 'w', encoding='utf-8'))
def sai(texto=''):
    if texto:
        print(texto)
    sys.exit(0)
def erro(texto):
    print('ERROR: ' + texto, file=sys.stderr)
    sys.exit(1)
def opcao(nome):
    return next((x.split('=', 1)[1] for x in a if x.startswith(nome + '=')), None)
if any(j.startswith(f) for f in e.get('falhas', [])):
    erro(f'[{e["conta"]}] does not have permission (403)')
if a[:3] == ['config', 'get-value', 'account']:
    sai(e['conta'])
if a[:2] == ['auth', 'print-access-token']:
    sai('token-falso')
if a[:3] == ['storage', 'buckets', 'describe']:
    if not e['bucket']:
        erro('HTTPError 404: The specified bucket does not exist.')
    if 'value(projectNumber)' in j:
        sai(e['bucket']['projectNumber'])
    sai(e['bucket']['name'] if 'value(name)' in j else json.dumps(e['bucket']))
if a[:3] == ['storage', 'buckets', 'create']:
    e['bucket'] = {'name': a[3][len('gs://'):], 'projectNumber': e['numero'], 'versioning': {'enabled': False},
                   'iamConfiguration': {'uniformBucketLevelAccess': {'enabled': True}, 'publicAccessPrevention': 'enforced'}}
    e['politica_bucket'] = {'bindings': [
        {'role': 'roles/storage.legacyBucketOwner', 'members': [f'projectEditor:{os.environ["PROJ"]}', f'projectOwner:{os.environ["PROJ"]}']},
        {'role': 'roles/storage.legacyBucketReader', 'members': [f'projectViewer:{os.environ["PROJ"]}']}]}
    salvar(); sai()
if a[:3] == ['storage', 'buckets', 'update']:
    if '--versioning' in a:
        e['bucket']['versioning'] = {'enabled': True}
    salvar(); sai()
if a[:3] == ['storage', 'buckets', 'get-iam-policy']:
    sai(json.dumps(e['politica_bucket']))
if a[:3] == ['storage', 'buckets', 'remove-iam-policy-binding']:
    membro, papel = opcao('--member'), opcao('--role')
    for b in e['politica_bucket']['bindings']:
        if b['role'] == papel and membro in b['members']:
            b['members'].remove(membro); salvar(); sai()
    erro('IamPolicyBindingNotFound')
if a[:3] == ['storage', 'managed-folders', 'list']:
    sai('\n'.join(e.get('pastas', [])))
if a[:3] == ['storage', 'objects', 'describe']:
    if a[3] in e.get('indisponivel', []):
        erro('HTTPError 503: Service Unavailable')
    o = e.setdefault('objetos', {}).get(a[3])
    if not o:
        erro('HTTPError 404: No URLs matched')
    geracao = o['geracao']
    # Corrida: outro processo regrava o objeto logo depois desta leitura da geração.
    if a[3] in e.get('trocar_apos_describe', []):
        e['objetos'][a[3]] = {'geracao': geracao + 100, 'conteudo': 'TROCADO-DEPOIS-DO-DESCRIBE'}
        salvar()
    sai(str(geracao))
if a[:2] == ['storage', 'cp']:
    origem, destino = a[2], a[3]
    objs = e.setdefault('objetos', {})
    if destino.startswith('gs://'):
        if '--if-generation-match=0' in a and destino in objs:
            erro('PreconditionFailed')
        if destino in e.get('falhar_upload', []):
            erro('HTTPError 503: upload interrompido')
        conteudo = '{}' if e.get('corromper') or destino in e.get('corromper_objetos', []) else open(origem, encoding='utf-8').read()
        objs[destino] = {'geracao': 1000 + len(objs), 'conteudo': conteudo}
        salvar()
        if destino in e.get('ack_perdido', []):
            erro('connection reset: resposta perdida depois da gravação')
        sai()
    nome, _, geracao = origem.partition('#')
    o = objs.get(nome)
    if not o or (geracao and str(o['geracao']) != geracao):
        erro('HTTPError 404')
    open(destino, 'w', encoding='utf-8').write(o['conteudo']); sai()
if a[:2] == ['projects', 'describe']:
    sai(e['pai'] if 'parent.type' in j else e['numero'])
if a[:2] == ['projects', 'get-iam-policy']:
    sai(json.dumps(e['politica_projeto']))
if a[:2] == ['projects', 'remove-iam-policy-binding']:
    membro, papel = opcao('--member'), opcao('--role')
    for b in e['politica_projeto']['bindings']:
        if b['role'] == papel and membro in b['members']:
            b['members'].remove(membro); salvar(); sai()
    erro('Policy binding with the specified principal, role, and condition not found!')
if a[:3] == ['iam', 'roles', 'describe']:
    nome = a[3]
    if '/' in nome and not nome.startswith('roles/'):
        erro('INVALID_ARGUMENT: papel customizado vai pelo ID, com --project ou --organization')
    if opcao('--project'):
        nome = f'projects/{opcao("--project")}/roles/{nome}'
    elif opcao('--organization'):
        nome = f'organizations/{opcao("--organization")}/roles/{nome}'
    sai(json.dumps({'name': nome, 'includedPermissions': e['papeis'].get(nome, [])}, indent=2))
contas = e.setdefault('contas_sa', {})
if a[:3] == ['iam', 'service-accounts', 'list']:
    email = opcao('--filter').split('=', 1)[1]
    sai(email if email in contas else '')
if a[:3] == ['iam', 'service-accounts', 'describe']:
    sai('True' if contas[a[3]]['disabled'] else '')
if a[:3] == ['iam', 'service-accounts', 'disable']:
    contas[a[3]]['disabled'] = True; salvar(); sai()
SEGREDOS = ['hml-db-admin-senha', 'hml-db-migrator-senha', 'hml-db-app-runtime-senha', 'hml-oidc-client-secret']
if a[:3] == ['sql', 'instances', 'describe']:
    if e.get('sem_instancia'):
        erro('HTTPError 404: instance does not exist')
    sai(e.get('sql_estado', 'RUNNABLE'))
if a[:3] == ['sql', 'operations', 'wait']:
    if e.get('falha_operacao'):
        erro('operation failed')
    sai()
if a[:2] == ['secrets', 'describe']:
    if a[2] not in e.get('segredos', SEGREDOS):
        erro('NOT_FOUND: Secret not found')
    sai(f'projects/999/secrets/{a[2]}')
if a[:3] == ['secrets', 'versions', 'list']:
    versoes = e.setdefault('versoes', {}).get(a[3], [])
    estados = e.get('estados', {}).get(a[3], {})
    linhas = [f'projects/999/secrets/{a[3]}/versions/{v}\t{estados.get(str(v), "ENABLED")}' for v in reversed(versoes)
              if estados.get(str(v), 'ENABLED') != 'DESTROYED']
    sai('\n'.join(linhas))
if a[:3] == ['secrets', 'versions', 'add']:
    s = a[3]
    valor = sys.stdin.read()
    if s in e.get('falhar_add', []):
        e['falhar_add'].remove(s); salvar()
        erro('UNAVAILABLE')
    versoes = e.setdefault('versoes', {}).setdefault(s, [])
    versoes.append(len(versoes) + 1)
    e.setdefault('valores', {}).setdefault(s, []).append(valor)
    salvar()
    sai(f'projects/999/secrets/{s}/versions/{versoes[-1]}')
if a[:3] == ['compute', 'networks', 'list']:
    sai('default' if e.get('rede_default') else '')
if a[:3] == ['compute', 'firewall-rules', 'list']:
    sai('\n'.join(e.get('regras', [])))
if a[:3] == ['compute', 'firewall-rules', 'delete']:
    e['regras'].remove(a[3]); salvar(); sai()
if a[:3] == ['compute', 'networks', 'delete']:
    e['rede_default'] = False
    if e.get('falhar_releitura'):
        e['falhas'] = ['compute networks list']
    salvar(); sai()
print('gcloud falso: comando não previsto: ' + j, file=sys.stderr)
sys.exit(9)
'''

GH = r'''#!/usr/bin/env python3
import json, os, sys
d = os.environ['FALSO']
a = sys.argv[1:]
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write('gh ' + ' '.join(a) + '\n')
if a[0] == 'api' and '/check-runs' in a[1]:
    print(open(os.path.join(d, 'checks.json'), encoding='utf-8').read()); sys.exit(0)
if a[0] == 'api' and a[1] == 'repos/adrptu/Safrion-Software-/branches/main':
    # main-depois.txt, se existir, vale a partir da 2ª leitura: a main anda durante o comando.
    contador = os.path.join(d, 'main-leituras')
    n = int(open(contador).read()) if os.path.exists(contador) else 0
    open(contador, 'w').write(str(n + 1))
    depois = os.path.join(d, 'main-depois.txt')
    arquivo = depois if n >= 1 and os.path.exists(depois) else os.path.join(d, 'main.txt')
    print(open(arquivo, encoding='utf-8').read().strip()); sys.exit(0)
if a[0] == 'api' and a[1] == 'repos/adrptu/Safrion-Software-':
    print({'.id': '111', '.owner.id': '222'}[a[a.index('--jq') + 1]]); sys.exit(0)
if a[0] == 'api' and a[1].startswith('repos/adrptu/Safrion-Software-/actions/runs/'):
    # Uma resposta por execução e tentativa, como a API real; o resto é 404.
    partes = a[1].split('/')
    caminho = os.path.join(d, f'execucao-{partes[5]}-{partes[7]}.json') if len(partes) == 8 and partes[6] == 'attempts' else ''
    if not caminho or not os.path.exists(caminho):
        print('gh: Not Found (HTTP 404) para dono@example.com', file=sys.stderr); sys.exit(1)
    print(open(caminho, encoding='utf-8').read()); sys.exit(0)
sys.exit(9)
'''

# Registra variáveis TF_VAR_* e TF_CLI_ARGS* que chegarem ao Terraform (não deveriam chegar).
TERRAFORM = r'''#!/usr/bin/env python3
import hashlib, json, os, sys
d = os.environ['FALSO']
a = sys.argv[1:]
vazou = sorted(k for k in os.environ if k.startswith(('TF_VAR_', 'TF_CLI_ARGS')))
# show e apply registram o SHA-256 do arquivo que receberam: prova de que o plano conferido é o aplicado.
arquivo = a[-1] if a and a[0] in ('show', 'apply') and os.path.isfile(a[-1]) else None
sha = ' sha=' + hashlib.sha256(open(arquivo, 'rb').read()).hexdigest() if arquivo else ''
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write('terraform ' + ' '.join(a) + sha + (' VAZOU=' + ','.join(vazou) if vazou else '') + ' dd=' + os.path.basename(os.environ.get('TF_DATA_DIR', '-')) + ' @' + os.path.basename(os.getcwd()) + '\n')
if a[0] == 'show' and not arquivo:
    print('Error: plano não encontrado', file=sys.stderr)
    sys.exit(1)
if a[0] == 'apply' and os.environ.get('TRAVADO_SEM_ID'):
    print('Error: Error acquiring the state lock\n\nError message: 401 Unauthorized', file=sys.stderr)
    sys.exit(1)
if a[0] == 'apply' and os.environ.get('GRAVAR_ERRORED'):
    open('errored.tfstate', 'w').write('{"version": 4}')
    print('Error: Failed to save state', file=sys.stderr)
    sys.exit(1)
if a[0] == 'apply' and os.environ.get('TROCAR_MARCA'):
    g = json.load(open(os.path.join(d, 'gcloud.json'), encoding='utf-8'))
    g['objetos'][os.environ['TROCAR_MARCA']]['conteudo'] = 'OUTRA-MARCA'
    json.dump(g, open(os.path.join(d, 'gcloud.json'), 'w', encoding='utf-8'))
if a[0] in ('plan', 'apply') and os.environ.get('TRAVADO'):
    print('Error: Error acquiring the state lock\n\nLock Info:\n  ID:        1712345678\n  Path:      x/default.tflock',
          file=sys.stderr)
    sys.exit(1)
if a[0] == 'plan':
    if os.environ.get('PLANO_FALHA'):
        sys.exit(1)
    saida = next(x.split('=', 1)[1] for x in a if x.startswith('-out='))
    open(saida, 'wb').write(b'plano-falso ' + os.environ.get('PLANO_EXTRA', '').encode())
elif a[0] == 'show':
    nome = 'plano-hml.json' if os.path.basename(os.getcwd()) == 'hml' else 'plano.json'
    print(open(os.path.join(d, nome), encoding='utf-8').read())
elif a[0] == 'apply' and os.environ.get('APLICAR_FALHA'):
    print('Error: googleapi: Error 409', file=sys.stderr)
    sys.exit(1)
elif a[0] == 'output':
    print(json.dumps({k: {'value': v} for k, v in {
        'wif_provider': 'projects/1/locations/global/workloadIdentityPools/github/providers/github',
        'sa_deploy_github': 'sa-deploy-github@x.iam.gserviceaccount.com',
        'sa_infra_github': 'sa-infra-github@x.iam.gserviceaccount.com', 'bucket_state': 'x-tfstate-hml',
        'rede_self_link': f'https://www.googleapis.com/compute/v1/projects/{os.environ["PROJ"]}/global/networks/safrion-hml',
        'subrede_self_link': f'https://www.googleapis.com/compute/v1/projects/{os.environ["PROJ"]}/regions/southamerica-east1/subnetworks/safrion-hml-run',
        'faixa_psa_nome': os.environ.get('FAIXA', 'safrion-hml-psa')}.items()}))
sys.exit(0)
'''

TFLINT = '#!/bin/sh\necho "tflint $*" >> "$FALSO/chamadas.log"\n'
CURL = '''#!/usr/bin/env python3
import json, os, shutil, sys
a = sys.argv[1:]
d = os.environ['FALSO']
open(os.path.join(d, 'chamadas.log'), 'a').write('curl ' + ' '.join(a) + '\\n')
destino = a[a.index('--output') + 1]
if '-X' in a:
    e = json.load(open(os.path.join(d, 'gcloud.json'), encoding='utf-8'))
    cabecalhos = [a[i + 1] for i, x in enumerate(a) if x == '-H']
    arquivo = next(h[1:] for h in cabecalhos if h.startswith('@'))
    if open(arquivo, encoding='utf-8').read() != 'Authorization: Bearer token-falso\\n':
        sys.exit(3)
    corpo = json.loads(sys.stdin.read())
    if e.get('falha_sql'):
        print('curl: (22) The requested URL returned error: 403', file=sys.stderr)
        sys.exit(22)
    e.setdefault('postgres', []).append(corpo['password'])
    e['url_sql'] = a[-1]
    json.dump(e, open(os.path.join(d, 'gcloud.json'), 'w', encoding='utf-8'))
    open(destino, 'w', encoding='utf-8').write(json.dumps({'name': 'op-senha-1', 'user': 'dono@example.com'}))
    sys.exit(0)
nome = 'terraform' if 'hashicorp' in a[-1] else 'tflint'
shutil.copy(os.path.join(os.environ['FALSO'], nome + '.zip'), destino)
'''
# git fetch não sai para a rede; o resto é o git real sobre a cópia temporária.
GIT = '''#!/bin/sh
for x in "$@"; do [ "$x" = fetch ] && exit 0; done
exec "$GIT_REAL" "$@"
'''
# O Cloud Shell é x86_64; a máquina que roda o teste pode não ser.
UNAME = '#!/bin/sh\necho x86_64\n'


def executavel(caminho, texto):
    caminho.write_text(texto, encoding='utf-8')
    caminho.chmod(caminho.stat().st_mode | stat.S_IEXEC)


def zip_com(nome):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr(zipfile.ZipInfo(nome), TERRAFORM if nome == 'terraform' else TFLINT)
    return buf.getvalue()


class CloudShell(unittest.TestCase):
    def setUp(self):
        # Caminho real: o script resolve links (no macOS, /var aponta para /private/var).
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.repo = self.tmp / 'repo'
        for rel in ('infra/terraform', 'tools/github', 'tools/hml', '.github/workflows'):
            shutil.copytree(RAIZ_REAL / rel, self.repo / rel, ignore=shutil.ignore_patterns('__pycache__', '.terraform'))
        # O planejar.py real (validar_config é a fonte única), com o projeto do teste no lugar do fixo.
        self.projeto_fixo(PROJETO)
        (self.repo / '.gitignore').write_text('*.tfvars\n__pycache__/\n', encoding='utf-8')
        self.falso = self.tmp / 'falso'
        self.falso.mkdir()
        self.bin = self.tmp / 'bin'
        self.bin.mkdir()
        self.home = self.tmp / 'home'
        self.home.mkdir()
        self.trabalho = self.home / '.safrion' / PROJETO
        zips = {n: zip_com(n) for n in ('terraform', 'tflint')}
        for n, dados in zips.items():
            (self.falso / f'{n}.zip').write_bytes(dados)
        self.infra_yml(hashlib.sha256(zips['terraform']).hexdigest(), hashlib.sha256(zips['tflint']).hexdigest())
        self.git_real = shutil.which('git')
        for nome, texto in (('gcloud', GCLOUD), ('gh', GH), ('curl', CURL), ('git', GIT), ('uname', UNAME)):
            executavel(self.bin / nome, texto)
        for c in (['init', '-q', '-b', 'main'], ['config', 'user.email', 't@example.com'], ['config', 'user.name', 't'],
                  ['add', '-A'], ['commit', '-q', '-m', 'base'], ['remote', 'add', 'origin', REPO]):
            self.git(*c)
        self.publicar()
        self.gcloud({})
        self.checks('success')
        (self.falso / 'plano.json').write_text(json.dumps({'resource_changes': [
            {'address': 'google_storage_bucket.state', 'change': {'actions': ['create']}},
            {'address': f'google_service_account_iam_member.x["user:{DONO}"]', 'change': {'actions': ['create']}}]}),
            encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args):
        return subprocess.run([self.git_real, '-C', str(self.repo), *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def projeto_fixo(self, projeto):
        p = self.repo / 'tools/hml/planejar.py'
        t = p.read_text(encoding='utf-8')
        t, n = re.subn(r"^PROJETO = '[a-z0-9-]+'$", f"PROJETO = '{projeto}'", t, flags=re.M)
        self.assertEqual(n, 1)
        p.write_text(t, encoding='utf-8')

    def publicar(self):
        """O commit local vira a main do GitHub falso (ref local e API)."""
        self.commit = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', 'HEAD')
        (self.falso / 'main.txt').write_text(self.commit, encoding='utf-8')

    def infra_yml(self, sha_tf, sha_tl):
        p = self.repo / '.github/workflows/infra.yml'
        t = p.read_text(encoding='utf-8').splitlines(keepends=True)
        t = [(l[:l.index('TERRAFORM_SHA256:')] + f'TERRAFORM_SHA256: {sha_tf}\n') if 'TERRAFORM_SHA256:' in l else
             (l[:l.index('TFLINT_SHA256:')] + f'TFLINT_SHA256: {sha_tl}\n') if 'TFLINT_SHA256:' in l else l for l in t]
        p.write_text(''.join(t), encoding='utf-8')

    def gcloud(self, extra):
        base = {'conta': DONO, 'numero': '999', 'pai': '', 'bucket': None, 'politica_bucket': {'bindings': []},
                'politica_projeto': {'bindings': [{'role': 'roles/owner', 'members': [f'user:{DONO}']}]},
                'papeis': {'roles/owner': ['storage.objects.get'], 'roles/editor': ['storage.objects.get'],
                           'roles/run.viewer': ['run.services.get'],
                           'roles/run.serviceAgent': ['storage.objects.get']}}
        (self.falso / 'gcloud.json').write_text(json.dumps({**base, **extra}), encoding='utf-8')

    def mudar(self, **campos):
        (self.falso / 'gcloud.json').write_text(json.dumps({**self.estado(), **campos}), encoding='utf-8')

    def checks(self, conclusao):
        exigidos = json.loads((self.repo / 'tools/github/protecao-main.json').read_text(encoding='utf-8'))
        nomes = [c['context'] for r in exigidos['rules'] if r['type'] == 'required_status_checks'
                 for c in r['parameters']['required_status_checks']]
        runs = [{'name': n, 'conclusion': 'success', 'app': {'id': 15368}} for n in nomes]
        runs[0]['conclusion'] = conclusao
        (self.falso / 'checks.json').write_text(json.dumps({'check_runs': runs}), encoding='utf-8')

    def rodar(self, *args, entrada='', extra_env=None):
        env = {**os.environ, 'PATH': f'{self.bin}{os.pathsep}{os.environ["PATH"]}', 'FALSO': str(self.falso),
               'PROJ': PROJETO, 'HOME': str(self.home), 'GIT_REAL': self.git_real}
        env.pop('SAFRION_DIR', None)
        env.update(extra_env or {})
        r = subprocess.run(['bash', str(self.repo / 'infra/terraform/cloudshell.sh'), *args], input=entrada,
                           capture_output=True, text=True, env=env, cwd=self.tmp)
        log = self.falso / 'chamadas.log'
        return r, (log.read_text(encoding='utf-8').splitlines() if log.exists() else [])

    def estado(self):
        return json.loads((self.falso / 'gcloud.json').read_text(encoding='utf-8'))

    def assertMascarado(self, r):
        self.assertNotIn(DONO, r.stdout + r.stderr)

    # uso e contexto -------------------------------------------------------------------------------------------------

    def test_sem_comando_mostra_o_uso(self):
        r, _ = self.rodar()
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stdout.startswith('infra/terraform/cloudshell.sh conferir'), r.stdout)
        self.assertIn('limpar <projeto>', r.stdout)

    def test_projeto_invalido(self):
        for p in ('Safrion', 'a', 'x-', '../etc'):
            with self.subTest(p=p):
                r, _ = self.rodar('state', p)
                self.assertIn('ID de projeto inválido', r.stderr)

    def test_safrion_dir_relativo_ou_dentro_do_repositorio(self):
        r, _ = self.rodar('state', PROJETO, extra_env={'SAFRION_DIR': 'relativo'})
        self.assertIn('caminho absoluto', r.stderr)
        r, chamadas = self.rodar('state', PROJETO, extra_env={'SAFRION_DIR': str(self.repo / 'infra' / '..' / 'x')})
        self.assertIn('não pode ficar dentro da cópia', r.stderr)
        self.assertFalse(chamadas)
        (self.tmp / 'atalho').symlink_to(self.repo / 'infra')
        r, chamadas = self.rodar('state', PROJETO, extra_env={'SAFRION_DIR': str(self.tmp / 'atalho' / 'x')})
        self.assertIn('não pode ficar dentro da cópia', r.stderr)
        self.assertFalse(chamadas)

    def test_um_comando_por_vez_no_projeto(self):
        (self.trabalho / '.trava').mkdir(parents=True)
        r, chamadas = self.rodar('state', PROJETO)
        self.assertIn('outro comando do cloudshell.sh está em andamento', r.stderr)
        self.assertFalse(chamadas)
        (self.trabalho / '.trava').rmdir()
        r, _ = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.trabalho / '.trava').exists())
        self.gcloud({'pai': 'organization'})
        r, _ = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.trabalho / '.trava').exists())

    # conferir -------------------------------------------------------------------------------------------------------

    def test_conferir_main_com_checks_verdes(self):
        r, _ = self.rodar('conferir')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f'OK: main {self.commit}', r.stdout)

    def test_conferir_para_com_check_vermelho(self):
        self.checks('failure')
        r, _ = self.rodar('conferir')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('check sem success', r.stderr)

    def test_conferir_para_fora_da_main_ou_com_mudanca_local(self):
        (self.repo / 'x.txt').write_text('x', encoding='utf-8')
        r, _ = self.rodar('conferir')
        self.assertIn('mudanças locais', r.stderr)
        os.remove(self.repo / 'x.txt')
        self.git('checkout', '-q', '-b', 'outra')
        r, _ = self.rodar('conferir')
        self.assertIn("está em 'outra'", r.stderr)

    def test_conferir_para_com_tfvars_ignorado_nos_modulos(self):
        for nome in ('bootstrap/x.auto.tfvars', 'hml/terraform.tfvars'):
            with self.subTest(nome=nome):
                arquivo = self.repo / 'infra/terraform' / nome
                arquivo.write_text('projeto_id = "outro"\n', encoding='utf-8')
                self.assertEqual(self.git('status', '--porcelain'), '')
                r, _ = self.rodar('conferir')
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('arquivos ignorados pelo Git', r.stderr)
                arquivo.unlink()

    def test_conferir_compara_com_a_main_do_github(self):
        self.git('commit', '-q', '--allow-empty', '-m', 'local')
        r, _ = self.rodar('conferir')
        self.assertIn('não é a main atual', r.stderr)
        self.publicar()
        (self.falso / 'main.txt').write_text('a' * 40, encoding='utf-8')
        r, _ = self.rodar('conferir')
        self.assertIn(f'não é a main atual ({"a" * 40})', r.stderr)

    # state ----------------------------------------------------------------------------------------------------------

    def test_state_cria_confere_e_tira_so_os_vinculos_presentes(self):
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('sem pasta gerenciada e só o dono no IAM', r.stdout)
        self.assertIn('não cobre abuso dos próprios agentes do Google', r.stdout)
        remocoes = [c for c in chamadas if 'remove-iam-policy-binding' in c]
        self.assertEqual(len(remocoes), 2, remocoes)
        self.assertTrue(any('--uniform-bucket-level-access --public-access-prevention' in c for c in chamadas))
        self.assertTrue(any(c.startswith('gcloud storage buckets describe') and '--raw' in c for c in chamadas))
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse([c for c in chamadas if 'remove-iam-policy-binding' in c and c not in remocoes])
        self.assertEqual(len([c for c in chamadas if 'buckets create' in c]), 1)

    def test_state_nao_cria_sem_ler_e_mascara_o_erro_do_google(self):
        self.gcloud({'falhas': ['storage buckets describe']})
        r, chamadas = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('nada foi criado', r.stderr)
        self.assertFalse([c for c in chamadas if 'buckets create' in c])
        self.assertMascarado(r)
        self.gcloud({'falhas': ['projects get-iam-policy']})
        r, _ = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('***@example.com] does not have permission', r.stderr)
        self.assertMascarado(r)

    def test_state_nao_mexe_em_bucket_de_outro_projeto(self):
        self.rodar('state', PROJETO)
        self.mudar(bucket={**self.estado()['bucket'], 'projectNumber': '123'})
        politica = self.estado()['politica_bucket']
        politica['bindings'].append({'role': 'roles/storage.legacyBucketReader', 'members': ['projectViewer:outro']})
        self.mudar(politica_bucket=politica)
        (self.falso / 'chamadas.log').unlink()
        r, chamadas = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(f'não é do projeto {PROJETO}; nada foi alterado', r.stderr)
        self.assertFalse([c for c in chamadas if ' update ' in c or 'remove-iam' in c or ' create ' in c])
        self.mudar(falhas=['storage buckets describe gs://' + PROJETO + '-tfstate-bootstrap --raw'])
        r, chamadas = self.rodar('state', PROJETO)
        self.assertIn('nada foi alterado', r.stderr)
        self.assertMascarado(r)

    def test_state_para_com_membro_extra_no_bucket(self):
        self.rodar('state', PROJETO)
        politica = self.estado()['politica_bucket']
        politica['bindings'].append({'role': 'roles/storage.objectViewer', 'members': ['user:outro@x.com']})
        self.mudar(politica_bucket=politica)
        r, _ = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('membro(s) além do dono', r.stderr)
        self.assertNotIn('outro@x.com', r.stderr + r.stdout)

    def test_state_para_com_bucket_fora_do_padrao(self):
        self.rodar('state', PROJETO)
        certo = self.estado()['bucket']
        iam = certo['iamConfiguration']
        casos = {
            'o bucket não é deste projeto': {**certo, 'projectNumber': '123'},
            'acesso uniforme desligado': {**certo, 'iamConfiguration': {**iam, 'uniformBucketLevelAccess': {'enabled': False}}},
            'prevenção de acesso público': {**certo, 'iamConfiguration': {**iam, 'publicAccessPrevention': 'inherited'}},
            'versionamento desligado': {**certo, 'versioning': {'enabled': False}},
        }
        for mensagem, bucket in casos.items():
            with self.subTest(mensagem=mensagem):
                self.mudar(bucket=bucket)
                r, _ = self.rodar('planejar', PROJETO)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(mensagem, r.stderr)
        self.mudar(bucket=certo, pastas=[f'gs://{PROJETO}-tfstate-bootstrap/x/'])
        r, _ = self.rodar('planejar', PROJETO)
        self.assertIn('tem pasta gerenciada', r.stderr)

    def test_state_para_com_pasta_ou_organizacao_acima(self):
        self.gcloud({'pai': 'organization'})
        r, _ = self.rodar('state', PROJETO)
        self.assertIn('acesso herdado ao state não é conferível', r.stderr)

    def test_state_para_com_acesso_herdado_do_projeto(self):
        sa = 'serviceAccount:sa-infra-github@x.iam.gserviceaccount.com'
        casos = [
            ('roles/editor', sa, {}),
            ('roles/storage.objectViewer', sa, {}),
            ('projects/x/roles/custom', sa, {'projects/x/roles/custom': ['storage.managedFolders.setIamPolicy']}),
            ('organizations/7/roles/org', 'group:equipe@x.com', {'organizations/7/roles/org': ['storage.objects.list']}),
            ('roles/iam.securityAdmin', 'user:outro@x.com', {'roles/iam.securityAdmin': ['resourcemanager.projects.setIamPolicy']}),
            ('roles/iam.roleAdmin', 'user:outro@x.com', {'roles/iam.roleAdmin': ['iam.roles.update']}),
            ('roles/owner', 'user:segundo-dono@x.com', {}),
            ('roles/iam.serviceAccountTokenCreator', 'user:outro@x.com',
             {'roles/iam.serviceAccountTokenCreator': ['iam.serviceAccounts.getAccessToken', 'iam.serviceAccounts.signBlob']}),
            ('roles/iam.serviceAccountUser', 'user:outro@x.com', {'roles/iam.serviceAccountUser': ['iam.serviceAccounts.actAs']}),
            ('roles/iam.serviceAccountKeyAdmin', 'user:outro@x.com',
             {'roles/iam.serviceAccountKeyAdmin': ['iam.serviceAccountKeys.create']}),
            ('roles/iam.workloadIdentityPoolAdmin', 'user:outro@x.com',
             {'roles/iam.workloadIdentityPoolAdmin': ['iam.workloadIdentityPoolProviders.update']}),
            ('roles/run.serviceAgent', 'serviceAccount:service-123@serverless-robot-prod.iam.gserviceaccount.com', {}),
        ]
        for papel, membro, papeis in casos:
            with self.subTest(papel=papel, membro=membro):
                self.gcloud({'politica_projeto': {'bindings': [
                    {'role': 'roles/owner', 'members': [f'user:{DONO}']}, {'role': papel, 'members': [membro]}]}})
                self.mudar(papeis={**self.estado()['papeis'], **papeis})
                r, chamadas = self.rodar('state', PROJETO)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f'{membro.split(":")[0]} com {papel} alcança o state', r.stderr)
                self.assertNotIn(membro.split(':')[1], r.stderr + r.stdout)
                if papel.startswith('projects/'):
                    self.assertIn('gcloud iam roles describe custom --project=x --format=json', chamadas)
                if papel.startswith('organizations/'):
                    self.assertIn('gcloud iam roles describe org --organization=7 --format=json', chamadas)

    def test_state_reconhece_o_dono_com_outra_caixa_so_em_user_e_ascii(self):
        # O IAM guarda user:Owner@Example.test e a conta logada é owner@example.test: é o mesmo dono (o gcloud compara
        # conta e e-mail do token com lower()). Os papéis dele não são expandidos nem viram achado.
        self.gcloud({'conta': 'owner@example.test', 'politica_projeto': {'bindings': [
            {'role': 'roles/owner', 'members': ['user:Owner@Example.test']},
            {'role': 'roles/storage.admin', 'members': ['user:OWNER@example.TEST']}]}})
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse([c for c in chamadas if 'roles describe roles/storage.admin' in c])
        # Continuam negados: dono diferente (mesmo com caixa trocada), o mesmo texto como conta de serviço ou grupo, prefixo
        # de tipo com outra caixa e diferença de caixa fora de A–Z (sem casefold nem normalização Unicode).
        casos = [
            ('owner@example.test', 'user:Outro@Example.test'),
            ('owner@example.test', 'serviceAccount:owner@example.test'),
            ('owner@example.test', 'serviceAccount:Owner@Example.test'),
            ('owner@example.test', 'group:owner@example.test'),
            ('owner@example.test', 'USER:owner@example.test'),
            ('öwner@example.test', 'user:Öwner@example.test'),
        ]
        for conta, membro in casos:
            with self.subTest(conta=conta, membro=membro):
                self.gcloud({'conta': conta, 'politica_projeto': {'bindings': [
                    {'role': 'roles/owner', 'members': [f'user:{conta}']}, {'role': 'roles/owner', 'members': [membro]}]}})
                r, _ = self.rodar('state', PROJETO)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f'{membro.split(":")[0]} com roles/owner alcança o state', r.stderr)

    def test_state_aponta_o_depois_para_a_conta_padrao_do_compute(self):
        self.gcloud({'politica_projeto': {'bindings': [
            {'role': 'roles/owner', 'members': [f'user:{DONO}']}, {'role': 'roles/editor', 'members': [f'serviceAccount:{COMPUTE}']}]}})
        r, _ = self.rodar('state', PROJETO)
        self.assertIn('conta padrão do Compute: rode depois antes', r.stderr)

    def test_state_aceita_dono_agente_de_servico_e_papel_sem_storage(self):
        self.gcloud({'politica_projeto': {'bindings': [
            {'role': 'roles/owner', 'members': [f'user:{DONO}']},
            {'role': 'roles/storage.admin', 'members': [f'user:{DONO}']},
            {'role': 'roles/run.serviceAgent', 'members': ['serviceAccount:service-999@serverless-robot-prod.iam.gserviceaccount.com']},
            {'role': 'roles/editor', 'members': ['serviceAccount:999@cloudservices.gserviceaccount.com']},
            {'role': 'roles/run.viewer', 'members': ['serviceAccount:sa-agentes-leitura@x.iam.gserviceaccount.com']}]}})
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('agente de serviço do Google (serverless-robot-prod.iam.gserviceaccount.com)', r.stdout)
        self.assertIn('agente de serviço do Google (cloudservices.gserviceaccount.com)', r.stdout)
        self.assertFalse([c for c in chamadas if 'roles describe roles/storage.admin' in c])

    # planejar e aplicar ---------------------------------------------------------------------------------------------

    def planejar(self, **env):
        self.assertEqual(self.rodar('state', PROJETO)[0].returncode, 0)
        return self.rodar('planejar', PROJETO, extra_env=env)

    def test_planejar_fora_do_checkout_com_saida_mascarada(self):
        r, chamadas = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.trabalho / 'bootstrap.tfvars').exists())
        self.assertTrue((self.trabalho / 'bootstrap.tfplan').exists())
        self.assertFalse((self.trabalho / 'bootstrap.tfplan.novo').exists())
        self.assertEqual(oct(self.trabalho.stat().st_mode & 0o777), '0o700')
        self.assertFalse(list((self.repo / 'infra/terraform/bootstrap').glob('*.tfvars')))
        self.assertFalse((self.repo / 'infra/terraform/bootstrap/.terraform').exists())
        self.assertMascarado(r)
        self.assertIn('***@example.com', r.stdout)
        hash_ = hashlib.sha256((self.trabalho / 'bootstrap.tfplan').read_bytes()).hexdigest()
        self.assertIn(f'SHA-256: {hash_}', r.stdout)
        self.assertIn('Criar 2 · mudar 0 · destruir 0', r.stdout)
        tfvars = (self.trabalho / 'bootstrap.tfvars').read_text(encoding='utf-8')
        self.assertIn('github_repository_id = "111"', tfvars)
        self.assertIn(f'operador             = "user:{DONO}"', tfvars)
        self.assertTrue(any(c.startswith('terraform init') and f'bucket={PROJETO}-tfstate-bootstrap' in c for c in chamadas))
        self.assertTrue(any(c.startswith('curl') and '--max-time' in c for c in chamadas))
        self.assertTrue((self.trabalho / 'bin' / 'terraform.sha256').exists())

    def test_planejar_ignora_tf_var_e_tf_cli_args_do_shell(self):
        r, chamadas = self.planejar(TF_VAR_projeto_id='outro', TF_CLI_ARGS_plan='-destroy', TF_CLI_ARGS='-no-color')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue([c for c in chamadas if c.startswith('terraform plan')])
        self.assertFalse([c for c in chamadas if 'VAZOU' in c])

    def test_planejar_que_para_no_meio_apaga_o_plano_anterior(self):
        r, _ = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        r, _ = self.rodar('planejar', PROJETO, extra_env={'PLANO_FALHA': '1'})
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.trabalho / 'bootstrap.tfplan').exists())
        self.assertFalse((self.trabalho / 'bootstrap.tfplan.sha256').exists())
        r, _ = self.planejar()
        self.assertTrue((self.trabalho / 'bootstrap.tfplan').exists())
        self.checks('failure')
        r, _ = self.rodar('planejar', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.trabalho / 'bootstrap.tfplan').exists())

    def test_download_com_sha_errado_para_antes_de_executar(self):
        self.infra_yml('0' * 64, '0' * 64)
        self.git('commit', '-q', '-am', 'sha errado')
        self.publicar()
        r, chamadas = self.planejar()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('SHA-256 do terraform diferente do infra.yml', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform ')])

    def test_planejar_com_state_travado_mostra_como_destravar(self):
        r, _ = self.planejar(TRAVADO='1')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(f'infra/terraform/cloudshell.sh destravar {PROJETO} 1712345678', r.stderr)

    def test_destravar_so_com_s(self):
        r, chamadas = self.rodar('destravar', PROJETO, '1712345678', entrada='n\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse([c for c in chamadas if 'force-unlock' in c])
        r, chamadas = self.rodar('destravar', PROJETO, '1712345678', entrada='s\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len([c for c in chamadas if c.startswith('terraform force-unlock -force 1712345678')]), 1)
        r, _ = self.rodar('destravar', PROJETO, '1;rm')
        self.assertIn('informe o ID do lock', r.stderr)

    def test_aplicar_so_com_o_hash_do_plano(self):
        r, _ = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        certo = hashlib.sha256((self.trabalho / 'bootstrap.tfplan').read_bytes()).hexdigest()
        r, chamadas = self.rodar('aplicar', PROJETO, 'f' * 64)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('outro SHA-256', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform apply')])
        r, chamadas = self.rodar('aplicar', PROJETO, certo)
        self.assertEqual(r.returncode, 0, r.stderr)
        aplicados = [c for c in chamadas if c.startswith('terraform apply')]
        self.assertEqual(len(aplicados), 1)
        self.assertIn(str(self.trabalho / 'aplicar.'), aplicados[0])
        self.assertIn('Não feche esta aba', r.stdout)
        self.assertFalse((self.trabalho / 'bootstrap.tfplan').exists())
        self.assertFalse(list(self.trabalho.glob('aplicar.*')))

    def test_aplicar_para_se_o_terraform_mudou_ou_o_state_saiu_do_padrao(self):
        r, _ = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        certo = hashlib.sha256((self.trabalho / 'bootstrap.tfplan').read_bytes()).hexdigest()
        self.mudar(pastas=['gs://x/p/'])
        r, chamadas = self.rodar('aplicar', PROJETO, certo)
        self.assertIn('tem pasta gerenciada', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform apply')])
        self.mudar(pastas=[])
        with open(self.trabalho / 'bin' / 'terraform', 'a', encoding='utf-8') as f:
            f.write('\n# alterado\n')
        r, chamadas = self.rodar('aplicar', PROJETO, certo)
        self.assertIn('o Terraform local mudou', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform apply')])

    def test_aplicar_recusa_hash_malformado(self):
        r, chamadas = self.rodar('aplicar', PROJETO, 'abc')
        self.assertIn('64 caracteres', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform')])

    def aplicado(self):
        r, _ = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        certo = hashlib.sha256((self.trabalho / 'bootstrap.tfplan').read_bytes()).hexdigest()
        r, _ = self.rodar('aplicar', PROJETO, certo)
        self.assertEqual(r.returncode, 0, r.stderr)

    # depois ---------------------------------------------------------------------------------------------------------

    def projeto_com_padroes_do_google(self):
        self.gcloud({'contas_sa': {COMPUTE: {'disabled': False}}, 'rede_default': True,
                     'regras': ['default-allow-ssh', 'default-allow-icmp'],
                     'politica_projeto': {'bindings': [{'role': 'roles/owner', 'members': [f'user:{DONO}']},
                                                       {'role': 'roles/editor', 'members': [f'serviceAccount:{COMPUTE}']}]}})

    def test_depois_com_s_tira_editor_desativa_e_apaga_a_rede(self):
        self.projeto_com_padroes_do_google()
        r, chamadas = self.rodar('depois', PROJETO, entrada='s\ns\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('sem Editor e desativada (conferido)', r.stdout)
        self.assertIn('Rede default: apagada (conferido)', r.stdout)
        self.assertEqual(len([c for c in chamadas if 'firewall-rules delete' in c]), 2)
        e = self.estado()
        self.assertTrue(e['contas_sa'][COMPUTE]['disabled'])
        self.assertFalse(any(f'serviceAccount:{COMPUTE}' in b['members'] for b in e['politica_projeto']['bindings']))
        self.assertFalse(e['rede_default'])
        self.assertEqual(e['regras'], [])
        r, _ = self.rodar('depois', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Rede default: não existe', r.stdout)

    def test_depois_com_outra_resposta_mantem_e_avisa(self):
        self.projeto_com_padroes_do_google()
        r, chamadas = self.rodar('depois', PROJETO, entrada='sim\n\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Conta padrão do Compute: mantida', r.stdout)
        self.assertIn('Rede default: mantida', r.stdout)
        self.assertFalse([c for c in chamadas if ' delete ' in c or ' disable ' in c or 'remove-iam' in c])

    def test_depois_para_se_o_google_recusa(self):
        self.projeto_com_padroes_do_google()
        self.mudar(falhas=['iam service-accounts disable'])
        r, _ = self.rodar('depois', PROJETO, entrada='s\ns\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não consegui desativar a conta padrão do Compute', r.stderr)
        self.assertMascarado(r)
        self.mudar(falhas=['compute networks list'])
        r, _ = self.rodar('depois', PROJETO, entrada='s\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não consegui listar as redes', r.stderr)

    def test_depois_nao_da_rede_por_apagada_sem_reler(self):
        self.projeto_com_padroes_do_google()
        self.mudar(falhar_releitura=True)
        r, _ = self.rodar('depois', PROJETO, entrada='n\ns\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não consegui conferir a rede default depois de apagar', r.stderr)
        self.assertNotIn('apagada (conferido)', r.stdout)
        self.assertMascarado(r)

    # variaveis, config-hml e limpar ---------------------------------------------------------------------------------

    def test_variaveis_le_o_state_sem_tf_var_no_hml_infra(self):
        self.aplicado()
        os.remove(self.trabalho / 'saidas.json')
        r, _ = self.rodar('variaveis', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('HML_PROJECT_NUMBER = 999', r.stdout)
        self.assertIn('DEPLOY_SA = sa-deploy-github@x.iam.gserviceaccount.com', r.stdout)
        self.assertNotIn('TF_VAR_', r.stdout)
        self.assertMascarado(r)

    def test_config_hml_grava_uma_vez_e_imprime_geracao_e_sha(self):
        self.aplicado()
        r, chamadas = self.rodar('config-hml', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        arquivo = self.trabalho / 'hml.tfvars.json'
        cfg = json.loads(arquivo.read_text(encoding='utf-8'))
        self.assertEqual(set(cfg), {'projeto_id', 'projeto_numero', 'rede_self_link', 'subrede_self_link',
                                    'faixa_psa_nome', 'operador', 'criar_cloud_run'})
        self.assertIs(cfg['criar_cloud_run'], False)
        sha = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        self.assertIn(f'config_generation = 1000 · config_sha256 = {sha}', r.stdout)
        self.assertMascarado(r)
        self.assertTrue(any('--if-generation-match=0' in c for c in chamadas))
        r, chamadas2 = self.rodar('config-hml', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('config_generation = 1000', r.stdout)
        self.assertFalse([c for c in chamadas2[len(chamadas):] if c.startswith('gcloud storage cp ') and 'gs://' in c.split()[-1]])

    def test_config_hml_para_se_ja_existe_outra_ou_se_nao_le(self):
        self.aplicado()
        objeto = f'gs://{PROJETO}-tfstate-hml/config/hml.tfvars.json'
        self.mudar(objetos={objeto: {'geracao': 7, 'conteudo': '{}'}})
        r, _ = self.rodar('config-hml', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('já existe outra configuração', r.stderr)
        self.mudar(objetos={}, falhas=['storage objects describe'])
        r, chamadas = self.rodar('config-hml', PROJETO)
        self.assertIn('não consegui ler', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('gcloud storage cp ') and 'gs://' in c.split()[-1]])

    def test_config_hml_para_com_outro_projeto_ou_saidas_incoerentes(self):
        self.aplicado()
        self.projeto_fixo('safrion-hml-outro')
        r, chamadas = self.rodar('config-hml', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('só planeja o projeto safrion-hml-outro', r.stderr)
        self.projeto_fixo(PROJETO)
        r, chamadas = self.rodar('config-hml', PROJETO, extra_env={'FAIXA': 'outra-faixa'})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('validar_config do tools/hml/planejar.py recusou: CONFIG_DESTINO', r.stderr)
        self.assertIn('nada foi gravado', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('gcloud storage cp ') and 'gs://' in c.split()[-1]])
        self.assertMascarado(r)

    def test_config_hml_sem_o_planejar_da_main(self):
        (self.repo / 'tools/hml/planejar.py').unlink()
        r, _ = self.rodar('config-hml', PROJETO)
        self.assertIn('tools/hml/planejar.py ausente nesta cópia', r.stderr)

    def test_config_hml_para_se_a_releitura_difere(self):
        self.aplicado()
        self.mudar(corromper=True)
        r, _ = self.rodar('config-hml', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('difere da gravada; não use estes valores', r.stderr)
        self.assertNotIn('config_sha256', r.stdout)

    def test_limpar_apaga_so_o_projeto(self):
        (self.home / '.safrion' / 'outro').mkdir(parents=True)
        self.planejar()
        r, _ = self.rodar('limpar', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.trabalho.exists())
        self.assertTrue((self.home / '.safrion' / 'outro').exists())
        self.assertIn('gh auth logout --hostname github.com', r.stdout)

    # senhas ----------------------------------------------------------------------------------------------------------

    def senhas(self, entrada='s\n', **env):
        return self.rodar('senhas', PROJETO, entrada=entrada, extra_env=env or None)

    def valores(self):
        e = self.estado()
        return e.get('valores', {}), e.get('postgres', [])

    def assertSemSenha(self, r, chamadas):
        valores, postgres = self.valores()
        todos = [v for lista in valores.values() for v in lista] + postgres
        self.assertTrue(todos)
        for v in todos:
            self.assertNotIn(v, r.stdout + r.stderr)
            self.assertFalse([c for c in chamadas if v in c], 'senha em argumento de comando')

    def test_senhas_gera_grava_e_mostra_so_as_versoes(self):
        r, chamadas = self.senhas()
        self.assertEqual(r.returncode, 0, r.stderr)
        for s in ('hml-db-admin-senha', 'hml-db-migrator-senha', 'hml-db-app-runtime-senha'):
            self.assertIn(f'{s}: versão 1', r.stdout)
        valores, postgres = self.valores()
        self.assertEqual(set(valores), {'hml-db-admin-senha', 'hml-db-migrator-senha', 'hml-db-app-runtime-senha'})
        senhas = [v[0] for v in valores.values()]
        self.assertEqual(len(set(senhas)), 3)
        for v in senhas:
            self.assertRegex(v, r'^[0-9a-f]{32}$')
        self.assertEqual(postgres, [valores['hml-db-admin-senha'][0]])
        self.assertEqual(self.estado()['url_sql'],
                         f'https://sqladmin.googleapis.com/v1/projects/{PROJETO}/instances/safrion-hml/users?name=postgres')
        self.assertIn(f'gcloud sql operations wait op-senha-1 --project={PROJETO} --timeout=300', chamadas)
        self.assertFalse((self.trabalho / 'cabecalho-sql').exists())
        self.assertFalse([c for c in chamadas if 'versions access' in c or '--password' in c])
        self.assertSemSenha(r, chamadas)
        self.assertMascarado(r)

    def test_senhas_mantem_segredo_que_ja_tem_versao(self):
        self.gcloud({'versoes': {'hml-db-migrator-senha': [1]}})
        r, chamadas = self.senhas()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('hml-db-migrator-senha: já tem a versão 1 ativa; mantida, sem gerar outra.', r.stdout)
        self.assertFalse([c for c in chamadas if c.startswith('gcloud secrets versions add hml-db-migrator-senha')])
        self.assertIn('hml-db-app-runtime-senha: versão 1', r.stdout)

    def test_senhas_nao_da_por_pronta_versao_desativada(self):
        # Achado do Codex (720e910): o filtro state!=DESTROYED contava versão DISABLED como pronta; nos três segredos.
        # Nada é gerado em nenhum dos três, mesmo quando o desativado não é o primeiro da lista.
        for s in ('hml-db-admin-senha', 'hml-db-migrator-senha', 'hml-db-app-runtime-senha'):
            with self.subTest(segredo=s):
                (self.falso / 'chamadas.log').unlink(missing_ok=True)
                self.gcloud({'versoes': {s: [1]}, 'estados': {s: {'1': 'DISABLED'}}})
                r, chamadas = self.senhas()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f'só com versão desativada: {s} (versão 1)', r.stderr)
                self.assertIn('nada foi gerado', r.stderr)
                self.assertFalse([c for c in chamadas if 'versions add' in c or c.startswith('curl')])
                self.assertFalse([c for c in chamadas if 'secrets versions enable' in c])
        (self.falso / 'chamadas.log').unlink(missing_ok=True)
        # Com uma ativa ao lado da desativada, vale a ativa.
        self.gcloud({'versoes': {'hml-db-admin-senha': [1, 2]}, 'estados': {'hml-db-admin-senha': {'1': 'DISABLED'}}})
        r, chamadas = self.senhas()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('hml-db-admin-senha: já tem a versão 2 ativa', r.stdout)
        self.assertFalse([c for c in chamadas if c.startswith('curl')])
        # Só destruída: gera a próxima.
        (self.falso / 'chamadas.log').unlink(missing_ok=True)
        self.gcloud({'versoes': {'hml-db-app-runtime-senha': [1]}, 'estados': {'hml-db-app-runtime-senha': {'1': 'DESTROYED'}}})
        r, _ = self.senhas()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('hml-db-app-runtime-senha: versão 2', r.stdout)

    def test_senhas_falha_de_listagem_nao_muda_nada(self):
        for s in ('hml-db-admin-senha', 'hml-db-migrator-senha', 'hml-db-app-runtime-senha'):
            with self.subTest(segredo=s):
                (self.falso / 'chamadas.log').unlink(missing_ok=True)
                self.gcloud({'falhas': [f'secrets versions list {s}']})
                r, chamadas = self.senhas()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f'não li as versões de {s}; nada foi gerado', r.stderr)
                self.assertFalse([c for c in chamadas if 'versions add' in c or c.startswith('curl')])
                self.assertMascarado(r)

    def test_senhas_sem_fase1_ou_sem_s_nao_gera_nada(self):
        casos = [({'sem_instancia': True}, 'aplique a fase 1 do hml/ antes'),
                 ({'sql_estado': 'PENDING_CREATE'}, "está em 'PENDING_CREATE', não RUNNABLE"),
                 ({'segredos': ['hml-db-admin-senha']}, 'segredo hml-db-migrator-senha ausente')]
        for extra, mensagem in casos:
            with self.subTest(mensagem=mensagem):
                self.gcloud(extra)
                r, chamadas = self.senhas()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(mensagem, r.stderr)
                self.assertFalse([c for c in chamadas if 'versions add' in c or c.startswith('curl')])
        self.gcloud({})
        r, chamadas = self.senhas(entrada='sim\n')
        self.assertIn('nada foi gerado', r.stderr)
        self.assertFalse([c for c in chamadas if 'versions add' in c or c.startswith('curl')])

    def test_senhas_recusa_rastreamento(self):
        r, chamadas = self.senhas(SHELLOPTS='xtrace')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('rode sem -x', r.stderr)
        self.assertFalse([c for c in chamadas if 'versions add' in c or c.startswith('curl')])

    def test_senhas_falha_no_banco_nao_grava_o_segredo(self):
        self.gcloud({'falha_sql': True})
        r, chamadas = self.senhas()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não confirmei a troca da senha do postgres; o segredo não foi gravado', r.stderr)
        self.assertFalse([c for c in chamadas if 'versions add' in c])
        self.assertFalse((self.trabalho / 'cabecalho-sql').exists())
        self.gcloud({'falha_operacao': True})
        r, _ = self.senhas()
        self.assertIn('não confirmei a troca da senha do postgres', r.stderr)
        self.assertFalse(self.valores()[0])

    def test_senhas_retoma_sem_senha_perdida_no_banco(self):
        self.gcloud({'falhar_add': ['hml-db-admin-senha']})
        r, chamadas = self.senhas()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não confirmei a gravação da versão de hml-db-admin-senha; rode senhas de novo', r.stderr)
        self.assertEqual(len(self.valores()[1]), 1)
        r, chamadas = self.senhas()
        self.assertEqual(r.returncode, 0, r.stderr)
        valores, postgres = self.valores()
        self.assertEqual(len(postgres), 2)
        self.assertNotEqual(postgres[0], postgres[1])
        self.assertEqual(valores['hml-db-admin-senha'][-1], postgres[-1])
        self.assertIn('hml-db-admin-senha: versão 1', r.stdout)
        self.assertSemSenha(r, chamadas)

    def test_senhas_fonte_sem_leitura_de_volta_nem_eco(self):
        codigo = [l for l in (AQUI / 'cloudshell.sh').read_text(encoding='utf-8').splitlines() if not l.lstrip().startswith('#')]
        for proibido in ('versions access', '--password=', 'set -x', '--prompt-for-password', 'echo "$senha', 'echo $senha'):
            with self.subTest(proibido=proibido):
                self.assertFalse([l for l in codigo if proibido in l])

    # aplicar-hml ------------------------------------------------------------------------------------------------------

    RUN, TENTATIVA = '555', '1'

    def prefixo_hml(self):
        return f'gs://{PROJETO}-tfstate-hml/planos/{self.RUN}/{self.TENTATIVA}'

    def plano_hml(self, extra=()):
        instancia = {
            'address': 'google_sql_database_instance.hml', 'mode': 'managed', 'type': 'google_sql_database_instance',
            'change': {'actions': ['create'], 'after_unknown': {}, 'after': {
                'project': PROJETO,
                'settings': [{'connector_enforcement': 'REQUIRED', 'data_api_access': 'DISALLOW_DATA_API',
                              'ip_configuration': [{
                                  'ssl_mode': 'ENCRYPTED_ONLY', 'authorized_networks': [], 'ipv4_enabled': False,
                                  'private_network': f'https://www.googleapis.com/compute/v1/projects/{PROJETO}/global/networks/safrion-hml',
                                  'psc_config': [], 'enable_private_path_for_google_cloud_services': None}]}]}}}
        return {'format_version': '1.2', 'terraform_version': '1.16.3', 'resource_changes': [instancia, *extra]}

    def preparar_hml(self, recibo=None, execucao=None, plano=None, binario=b'PLANO-HML-SINTETICO', recibo_bruto=None, **gcloud):
        """Bucket e GitHub falsos com um plano oficial coerente; os argumentos trocam uma peça de cada vez."""
        digest = hashlib.sha256(binario).hexdigest()
        base_recibo = {'repositorio': 'adrptu/Safrion-Software-', 'workflow': '.github/workflows/infra-hml.yml',
                       'evento': 'workflow_dispatch', 'ref': 'refs/heads/main', 'head_sha': self.commit,
                       'run_id': self.RUN, 'tentativa': self.TENTATIVA, 'config_generation': '1790700000000000',
                       'config_sha256': 'cd' * 32, 'plan_sha256': digest, 'plan_generation': '2001', 'escopo': 'fase1'}
        base_recibo.update(recibo or {})
        base_recibo = {k: v for k, v in base_recibo.items() if v is not None}
        pre = self.prefixo_hml()
        self.gcloud({'objetos': {
            f'{pre}/tfplan': {'geracao': 2001, 'conteudo': binario.decode()},
            f'{pre}/recibo.json': {'geracao': 2002, 'conteudo': recibo_bruto if recibo_bruto is not None else json.dumps(base_recibo, sort_keys=True, indent=2) + '\n'},
        }, **gcloud})
        base_execucao = {'id': int(self.RUN), 'run_attempt': int(self.TENTATIVA), 'path': '.github/workflows/infra-hml.yml',
                         'event': 'workflow_dispatch', 'head_branch': 'main', 'status': 'completed',
                         'conclusion': 'success', 'head_sha': self.commit}
        base_execucao.update(execucao or {})
        for velho in self.falso.glob('execucao-*.json'):
            velho.unlink()
        (self.falso / f'execucao-{self.RUN}-{self.TENTATIVA}.json').write_text(json.dumps(base_execucao), encoding='utf-8')
        (self.falso / 'plano-hml.json').write_text(json.dumps(plano or self.plano_hml()), encoding='utf-8')
        return digest

    def aplicar_hml(self, digest, entrada='s\n', **env):
        (self.falso / 'chamadas.log').unlink(missing_ok=True)
        (self.falso / 'main-leituras').unlink(missing_ok=True)
        return self.rodar('aplicar-hml', PROJETO, self.RUN, self.TENTATIVA, digest, entrada=entrada, extra_env=env or None)

    def aplicou(self, chamadas):
        return [c for c in chamadas if c.startswith('terraform apply')]

    def marca(self, nome='aplicacao-inicio.json'):
        return self.estado()['objetos'].get(f'{self.prefixo_hml()}/{nome}')

    def test_aplicar_hml_positivo(self):
        digest = self.preparar_hml()
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f'Aplicado na HML: commit {self.commit[:12]}, execução 555/1, plano {digest}', r.stdout)
        self.assertIn('criar 1, mudar 0', r.stdout)
        self.assertIn(f'Aplicar na HML o plano {digest[:12]} do commit {self.commit[:12]}, execução 555/1: criar 1, mudar 0?', r.stderr)
        # O arquivo conferido pelo show é o mesmo aplicado, e tem os bytes do hash aprovado.
        shows = [c for c in chamadas if c.startswith('terraform show')]
        self.assertEqual(len(shows), 1)
        self.assertIn(f' sha={digest}', shows[0])
        self.assertIn(f' sha={digest}', self.aplicou(chamadas)[0])
        self.assertIn('-lock-timeout=', self.aplicou(chamadas)[0])
        self.assertTrue([c for c in chamadas if c.startswith('terraform init') and '-lockfile=readonly' in c and c.endswith(' @hml')])
        # Terraform baixado e conferido pelo infra.yml; credencial renovada depois da marca, antes do apply.
        self.assertTrue([c for c in chamadas if c.startswith('curl') and 'hashicorp' in c])
        tokens = [i for i, c in enumerate(chamadas) if c == 'gcloud auth print-access-token']
        marca = next(i for i, c in enumerate(chamadas)
                     if c.startswith('gcloud storage cp') and 'aplicacao-inicio.json' in c and '--if-generation-match=0' in c)
        self.assertGreaterEqual(len(tokens), 2)
        self.assertGreater(tokens[-1], marca)
        self.assertLess(tokens[-1], chamadas.index(self.aplicou(chamadas)[0]))
        aplicados = self.aplicou(chamadas)
        self.assertEqual(len(aplicados), 1)
        self.assertTrue(aplicados[0].endswith(' @hml'), aplicados[0])
        self.assertIn(str(self.trabalho / 'aplicar-hml.'), aplicados[0])
        self.assertTrue([c for c in chamadas if c.startswith('terraform init') and f'bucket={PROJETO}-tfstate-hml' in c and c.endswith(' @hml')])
        self.assertIn(f'gh api repos/adrptu/Safrion-Software-/actions/runs/{self.RUN}/attempts/{self.TENTATIVA}', chamadas)
        inicio, fim = json.loads(self.marca()['conteudo']), json.loads(self.marca('aplicacao-fim.json')['conteudo'])
        self.assertEqual((inicio['commit'], inicio['plan_sha256'], inicio['plan_generation']), (self.commit, digest, '2001'))
        self.assertEqual(fim['resultado'], 'aplicado')
        # Estado próprio da HML: nenhuma chamada do terraform usa o .terraform do bootstrap.
        tf = [c for c in chamadas if c.startswith('terraform ')]
        self.assertTrue(tf and all(' dd=.terraform-hml @hml' in c for c in tf), tf)
        self.assertFalse(list(self.trabalho.glob('aplicar-hml.*')))
        self.assertMascarado(r)

    def test_aplicar_hml_recusa_recibo_fora_do_contrato(self):
        casos = {
            'sem recibo': dict(recibo=None),
            'campo a mais': dict(recibo={'extra': 'x'}),
            'campo faltando': dict(recibo={'config_sha256': None}),
            'outra execução': dict(recibo={'run_id': '556'}),
            'fase 2': dict(recibo={'escopo': 'fase2'}),
            'outro workflow': dict(recibo={'workflow': '.github/workflows/outro.yml'}),
            'outro commit': dict(recibo={'head_sha': 'a' * 40}, execucao={'head_sha': 'a' * 40}),
            'hash do recibo diferente do digitado': dict(recibo={'plan_sha256': 'b' * 64}),
        }
        for nome, kw in casos.items():
            with self.subTest(caso=nome):
                digest = self.preparar_hml(**kw)
                if nome == 'sem recibo':
                    e = self.estado(); e['objetos'].pop(f'{self.prefixo_hml()}/recibo.json'); self.mudar(objetos=e['objetos'])
                r, chamadas = self.aplicar_hml(digest)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('nada foi aplicado', r.stderr)
                self.assertFalse(self.aplicou(chamadas))
                self.assertIsNone(self.marca())
                self.assertMascarado(r)

    def test_aplicar_hml_recusa_execucao_que_nao_e_a_oficial_com_sucesso(self):
        casos = {
            'outro arquivo de workflow': {'path': '.github/workflows/outro.yml'},
            'evento push': {'event': 'push'},
            'outro ramo': {'head_branch': 'dev'},
            'em andamento': {'status': 'in_progress'},
            # Recibo órfão de um job que falhou depois de gravá-lo (ACK perdido no produtor).
            'job falhou': {'conclusion': 'failure'},
            'outra tentativa': {'run_attempt': 2},
            'outro commit na execução': {'head_sha': 'c' * 40},
        }
        for nome, execucao in casos.items():
            with self.subTest(caso=nome):
                digest = self.preparar_hml(execucao=execucao)
                r, chamadas = self.aplicar_hml(digest)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('a origem do plano não confere; nada foi aplicado', r.stderr)
                self.assertFalse(self.aplicou(chamadas))
                self.assertIsNone(self.marca())
        digest = self.preparar_hml()
        (self.falso / f'execucao-{self.RUN}-{self.TENTATIVA}.json').unlink()
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('não li a execução 555/1 no GitHub', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.assertMascarado(r)

    def test_aplicar_hml_plano_com_outro_hash_ou_recusado(self):
        digest = self.preparar_hml()
        e = self.estado(); e['objetos'][f'{self.prefixo_hml()}/tfplan']['conteudo'] = 'OUTRO-PLANO'; self.mudar(objetos=e['objetos'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('o plano no bucket tem outro SHA-256', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        destroy = {'address': 'google_storage_bucket.x', 'mode': 'managed', 'type': 'google_storage_bucket',
                   'change': {'actions': ['delete'], 'after': None}}
        nunca = {'address': 'google_sql_user.postgres', 'mode': 'managed', 'type': 'google_sql_user',
                 'change': {'actions': ['create'], 'after': {'name': 'postgres'}}}
        for nome, extra, mensagem in (('destroy', destroy, 'destroy, replace, outro projeto'),
                                      ('tipo Nunca', nunca, 'checar_travas.py recusou o plano')):
            with self.subTest(caso=nome):
                digest = self.preparar_hml(plano=self.plano_hml([extra]))
                r, chamadas = self.aplicar_hml(digest)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(mensagem, r.stderr)
                self.assertFalse(self.aplicou(chamadas))
                self.assertIsNone(self.marca())

    def test_aplicar_hml_sem_s_nao_consome_o_plano(self):
        digest = self.preparar_hml()
        r, chamadas = self.aplicar_hml(digest, entrada='sim\n')
        self.assertIn('nada foi aplicado; o plano continua disponível', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.assertIsNone(self.marca())
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.aplicou(chamadas)), 1)

    def test_aplicar_hml_uso_unico_e_ack_perdido_da_marca(self):
        digest = self.preparar_hml()
        e = self.estado()
        e['objetos'][f'{self.prefixo_hml()}/aplicacao-inicio.json'] = {'geracao': 3001, 'conteudo': '{"outra": "sessao"}'}
        self.mudar(objetos=e['objetos'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('a marca de uso deste plano já existe', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        # ACK perdido depois de gravar a nossa marca: a releitura byte a byte prova que é nossa, e o apply segue.
        digest = self.preparar_hml(ack_perdido=[f'{self.prefixo_hml()}/aplicacao-inicio.json'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.aplicou(chamadas)), 1)

    def test_aplicar_hml_lock_preso_e_falha_conservam_a_marca(self):
        digest = self.preparar_hml()
        r, chamadas = self.aplicar_hml(digest, TRAVADO='1')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('O state da HML está travado (ID 1712345678)', r.stderr)
        self.assertIn(f'infra/terraform/cloudshell.sh destravar-hml {PROJETO} 1712345678', r.stderr)
        self.assertNotIn(f'cloudshell.sh destravar {PROJETO}', r.stderr)
        self.assertIn('A marca de uso fica', r.stderr)
        self.assertEqual(json.loads(self.marca('aplicacao-fim.json')['conteudo'])['resultado'], 'falhou')
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('a marca de uso deste plano já existe', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        digest = self.preparar_hml()
        r, _ = self.aplicar_hml(digest, APLICAR_FALHA='1')
        self.assertIn('terraform apply falhou (código 1', r.stderr)
        self.assertIsNotNone(self.marca())

    def test_aplicar_hml_recibo_final_indisponivel_nao_repete(self):
        digest = self.preparar_hml(falhar_upload=[f'{self.prefixo_hml()}/aplicacao-fim.json'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn('Apply executado (código do Terraform: 0); recibo final indisponível no bucket. Não repita o apply', r.stderr)
        self.assertEqual(len(self.aplicou(chamadas)), 1)
        self.assertIsNotNone(self.marca())
        self.assertNotIn('Aplicado na HML', r.stdout)

    def test_aplicar_hml_outra_tentativa_e_path_com_ref(self):
        self.TENTATIVA = '2'
        digest = self.preparar_hml(execucao={'path': '.github/workflows/infra-hml.yml@refs/heads/main'})
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('execução 555/2', r.stdout)
        self.assertIn('gh api repos/adrptu/Safrion-Software-/actions/runs/555/attempts/2', chamadas)

    def test_aplicar_hml_recusa_recibo_com_campo_ou_formato_errado(self):
        casos = {
            'evento': dict(recibo={'evento': 'push'}),
            'ref': dict(recibo={'ref': 'refs/heads/dev'}),
            'repositorio': dict(recibo={'repositorio': 'outro/repo'}),
            'tentativa': dict(recibo={'tentativa': '2'}),
            'run_id numérico': dict(recibo={'run_id': 555}),
            'plan_generation zero': dict(recibo={'plan_generation': '0'}),
            'plan_generation texto': dict(recibo={'plan_generation': 'abc'}),
            'chave duplicada': dict(recibo_bruto='{"escopo": "fase1", "escopo": "fase1"}'),
            'id da execução': dict(execucao={'id': 556}),
        }
        for nome, kw in casos.items():
            with self.subTest(caso=nome):
                digest = self.preparar_hml(**kw)
                r, chamadas = self.aplicar_hml(digest)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('a origem do plano não confere; nada foi aplicado', r.stderr)
                self.assertFalse([c for c in chamadas if c.startswith('terraform')])
                self.assertIsNone(self.marca())

    def test_aplicar_hml_le_pela_geracao_do_recibo(self):
        pre = self.prefixo_hml()
        # O tfplan no bucket não está mais na geração que o recibo cita.
        digest = self.preparar_hml(recibo={'plan_generation': '2999'})
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('não li o plano em', r.stderr)
        self.assertIn('na geração do recibo; nada foi aplicado', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        # O recibo é regravado logo depois da leitura da geração: a cópia pela geração lida falha, sem usar o novo.
        digest = self.preparar_hml(trocar_apos_describe=[f'{pre}/recibo.json'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('não li o recibo em', r.stderr)
        self.assertFalse(self.aplicou(chamadas))

    def test_aplicar_hml_confere_a_main_antes_e_depois_da_pergunta(self):
        digest = self.preparar_hml()
        (self.falso / 'main.txt').write_text('f' * 40, encoding='utf-8')
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('não é a main atual', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.publicar()
        self.checks('failure')
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('check sem success', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.checks('success')
        (self.falso / 'main-depois.txt').write_text('e' * 40, encoding='utf-8')
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('a main andou depois da conferência: planeje de novo; nada foi aplicado', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.assertIsNone(self.marca())

    def test_aplicar_hml_falhas_da_marca_e_do_fim(self):
        pre = self.prefixo_hml()
        digest = self.preparar_hml(falhar_upload=[f'{pre}/aplicacao-inicio.json'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('não gravei a marca de uso (erro acima); nada foi aplicado; o plano continua disponível', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        for nome, kw, env in (('fim corrompido', {'corromper_objetos': [f'{pre}/aplicacao-fim.json']}, {}),
                              ('marca trocada no apply', {}, {'TROCAR_MARCA': f'{pre}/aplicacao-inicio.json'})):
            with self.subTest(caso=nome):
                digest = self.preparar_hml(**kw)
                r, chamadas = self.aplicar_hml(digest, **env)
                self.assertEqual(r.returncode, 4, r.stderr)
                self.assertIn('recibo final indisponível no bucket. Não repita o apply', r.stderr)
                self.assertNotIn('Aplicado na HML', r.stdout)
                self.assertEqual(len(self.aplicou(chamadas)), 1)
                # Retomar o mesmo plano não aplica de novo: a marca continua no bucket.
                r, chamadas = self.aplicar_hml(digest, **env)
                self.assertIn('a marca de uso deste plano já existe', r.stderr)
                self.assertFalse(self.aplicou(chamadas))

    def test_aplicar_hml_marca_incerta_nao_promete_plano(self):
        marca = f'{self.prefixo_hml()}/aplicacao-inicio.json'
        # A marca foi gravada, mas o ACK se perdeu e a releitura dá 503: não se sabe se o plano foi consumido.
        digest = self.preparar_hml(ack_perdido=[marca], indisponivel=[marca])
        r, chamadas = self.aplicar_hml(digest)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('não consegui confirmar se a marca de uso foi gravada', r.stderr)
        self.assertIn('503', r.stderr)
        self.assertNotIn('o plano continua disponível', r.stderr)
        self.assertFalse(self.aplicou(chamadas))
        self.assertIsNotNone(self.marca())
        # O gcloud volta: o mesmo comando recusa, porque a marca existe; o apply nunca roda.
        self.mudar(indisponivel=[])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('a marca de uso deste plano já existe', r.stderr)
        self.assertFalse(self.aplicou(chamadas))

    def test_aplicar_hml_errored_tfstate_sai_da_copia(self):
        digest = self.preparar_hml()
        r, _ = self.aplicar_hml(digest, GRAVAR_ERRORED='1')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('State não gravado no bucket: guardado em ~/.safrion/', r.stderr)
        self.assertFalse((self.repo / 'infra/terraform/hml/errored.tfstate').exists())
        guardado = self.trabalho / 'errored-hml.tfstate'
        self.assertTrue(guardado.is_file())
        self.assertEqual(oct(guardado.stat().st_mode & 0o777), '0o600')

    def test_aplicar_hml_lock_sem_id_nao_manda_destravar(self):
        digest = self.preparar_hml()
        r, _ = self.aplicar_hml(digest, TRAVADO_SEM_ID='1')
        self.assertIn('não li o ID do lock', r.stderr)
        self.assertNotIn('destravar-hml', r.stderr)

    def test_aplicar_hml_erro_do_gcloud_mascarado(self):
        pre = self.prefixo_hml()
        digest = self.preparar_hml(falhas=[f'storage objects describe {pre}/recibo.json'])
        r, chamadas = self.aplicar_hml(digest)
        self.assertIn('sem recibo do plano', r.stderr)
        self.assertIn('***@example.com', r.stderr)
        self.assertMascarado(r)
        self.assertFalse(self.aplicou(chamadas))

    def test_aplicar_hml_nao_reusa_terraform_antigo(self):
        digest = self.preparar_hml()
        binario = self.trabalho / 'bin' / 'terraform'
        binario.parent.mkdir(parents=True, exist_ok=True)
        binario.write_text('#!/bin/sh\necho antigo\n', encoding='utf-8')
        binario.chmod(0o700)
        (self.trabalho / 'bin' / 'terraform.sha256').write_text(hashlib.sha256(binario.read_bytes()).hexdigest() + '\n')
        r, chamadas = self.aplicar_hml(digest)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue([c for c in chamadas if c.startswith('curl') and 'hashicorp' in c])

    def test_aplicar_hml_so_o_projeto_fixo(self):
        self.projeto_fixo('safrion-hml-outro')
        r, chamadas = self.rodar('aplicar-hml', PROJETO, self.RUN, self.TENTATIVA, 'a' * 64)
        self.assertIn('só planeja o projeto safrion-hml-outro', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform')])
        self.projeto_fixo(PROJETO)
        for args, mensagem in ((('x', '1', 'a' * 64), 'informe a execução e a tentativa'),
                               (('555', '0', 'a' * 64), 'informe a execução e a tentativa'),
                               (('555', '1', 'abc'), 'informe o SHA-256 aprovado'),
                               (('555', '1', 'A' * 64), 'informe o SHA-256 aprovado')):
            with self.subTest(args=args):
                (self.falso / 'chamadas.log').unlink(missing_ok=True)
                r, chamadas = self.rodar('aplicar-hml', PROJETO, *args)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(mensagem, r.stderr)
                self.assertFalse([c for c in chamadas if c.startswith(('gcloud', 'gh'))])

    def test_destravar_hml_so_no_modulo_da_hml(self):
        r, chamadas = self.rodar('destravar-hml', PROJETO, '1;rm', entrada='s\n')
        self.assertIn('informe o ID do lock', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform')])
        r, chamadas = self.rodar('destravar-hml', PROJETO, '1712345678', entrada='n\n')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('lock mantido', r.stderr)
        self.assertFalse([c for c in chamadas if 'force-unlock' in c])
        r, chamadas = self.rodar('destravar-hml', PROJETO, '1712345678', entrada='s\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        destravas = [c for c in chamadas if c.startswith('terraform force-unlock')]
        self.assertEqual(len(destravas), 1)
        self.assertTrue(destravas[0].endswith(' dd=.terraform-hml @hml'), destravas[0])
        self.assertTrue([c for c in chamadas if c.startswith('terraform init') and f'bucket={PROJETO}-tfstate-hml' in c])
        self.assertFalse([c for c in chamadas if 'tfstate-bootstrap' in c])

    def test_sintaxe(self):
        self.assertEqual(subprocess.run(['bash', '-n', str(AQUI / 'cloudshell.sh')]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
