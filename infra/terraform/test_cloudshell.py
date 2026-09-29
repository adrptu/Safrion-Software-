# -*- coding: utf-8 -*-
"""Regressão do cloudshell.sh sem rede nem nuvem: gcloud, gh, terraform, tflint, curl e git fetch falsos.
Roda na CI: python3 -m unittest discover -s infra/terraform -p 'test_*.py'"""
import hashlib, io, json, os, shutil, stat, subprocess, tempfile, textwrap, unittest, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ_REAL = AQUI.parent.parent
REPO = 'https://github.com/adrptu/Safrion-Software-.git'
DONO = 'dono@example.com'
PROJETO = 'safrion-hml-teste'

GCLOUD = r'''#!/usr/bin/env python3
import json, os, sys
d = os.environ['FALSO']
e = json.load(open(os.path.join(d, 'gcloud.json'), encoding='utf-8'))
a = sys.argv[1:]
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write('gcloud ' + ' '.join(a) + '\n')
def salvar():
    json.dump(e, open(os.path.join(d, 'gcloud.json'), 'w', encoding='utf-8'))
def sai(texto='', rc=0):
    if texto:
        print(texto)
    sys.exit(rc)
j = ' '.join(a)
if a[:3] == ['config', 'get-value', 'account']:
    sai(e['conta'])
if a[:2] == ['auth', 'print-access-token']:
    sai('token-falso')
if a[:3] == ['storage', 'buckets', 'describe']:
    if not e['bucket']:
        sai('', 1)
    sai(e['bucket']['nome'] if 'value(name)' in j else json.dumps(e['bucket']))
if a[:3] == ['storage', 'buckets', 'create']:
    e['bucket'] = {'nome': a[3], 'uniform_bucket_level_access': True, 'public_access_prevention': 'enforced',
                   'versioning_enabled': False}
    e['politica_bucket'] = {'bindings': [
        {'role': 'roles/storage.legacyBucketOwner', 'members': [f'projectEditor:{os.environ["PROJ"]}', f'projectOwner:{os.environ["PROJ"]}']},
        {'role': 'roles/storage.legacyBucketReader', 'members': [f'projectViewer:{os.environ["PROJ"]}']}]}
    salvar(); sai()
if a[:3] == ['storage', 'buckets', 'update']:
    if '--versioning' in a:
        e['bucket']['versioning_enabled'] = True
    salvar(); sai()
if a[:3] == ['storage', 'buckets', 'get-iam-policy']:
    sai(json.dumps(e['politica_bucket']))
if a[:3] == ['storage', 'buckets', 'remove-iam-policy-binding']:
    membro = next(x.split('=', 1)[1] for x in a if x.startswith('--member='))
    papel = next(x.split('=', 1)[1] for x in a if x.startswith('--role='))
    for b in e['politica_bucket']['bindings']:
        if b['role'] == papel and membro in b['members']:
            b['members'].remove(membro); salvar(); sai()
    print('ERROR: IamPolicyBindingNotFound', file=sys.stderr); sys.exit(1)
if a[:2] == ['projects', 'describe']:
    sai(e['pai'] if 'parent.type' in j else e['numero'])
if a[:2] == ['projects', 'get-iam-policy']:
    sai(json.dumps(e['politica_projeto']))
if a[:3] == ['iam', 'roles', 'describe']:
    sai(json.dumps({'name': a[3], 'includedPermissions': e['papeis'].get(a[3], [])}))
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
if a[0] == 'api' and a[1] == 'repos/adrptu/Safrion-Software-':
    print({'.id': '111', '.owner.id': '222'}[a[a.index('--jq') + 1]]); sys.exit(0)
sys.exit(9)
'''

TERRAFORM = r'''#!/usr/bin/env python3
import json, os, sys
d = os.environ['FALSO']
a = sys.argv[1:]
with open(os.path.join(d, 'chamadas.log'), 'a', encoding='utf-8') as f:
    f.write('terraform ' + ' '.join(a) + '\n')
if a[0] == 'plan':
    saida = next(x.split('=', 1)[1] for x in a if x.startswith('-out='))
    open(saida, 'wb').write(b'plano-falso ' + os.environ.get('PLANO_EXTRA', '').encode())
elif a[0] == 'show':
    print(open(os.path.join(d, 'plano.json'), encoding='utf-8').read())
elif a[0] == 'output':
    print(json.dumps({k: {'value': v} for k, v in {
        'wif_provider': 'projects/1/locations/global/workloadIdentityPools/github/providers/github',
        'sa_deploy_github': 'sa-deploy-github@x.iam.gserviceaccount.com',
        'sa_infra_github': 'sa-infra-github@x.iam.gserviceaccount.com', 'bucket_state': 'x-tfstate-hml',
        'rede_self_link': 'r', 'subrede_self_link': 's', 'faixa_psa_nome': 'f'}.items()}))
sys.exit(0)
'''

TFLINT = '#!/bin/sh\necho "tflint $*" >> "$FALSO/chamadas.log"\n'
CURL = '''#!/usr/bin/env python3
import os, shutil, sys
a = sys.argv[1:]
open(os.path.join(os.environ['FALSO'], 'chamadas.log'), 'a').write('curl ' + ' '.join(a) + '\\n')
destino = a[a.index('--output') + 1]
nome = 'terraform' if 'hashicorp' in a[-1] else 'tflint'
shutil.copy(os.path.join(os.environ['FALSO'], nome + '.zip'), destino)
'''
# git fetch não sai para a rede; o resto é o git real sobre a cópia temporária.
GIT = '''#!/bin/sh
for x in "$@"; do [ "$x" = fetch ] && exit 0; done
exec "$GIT_REAL" "$@"
'''


def executavel(caminho, texto):
    caminho.write_text(texto, encoding='utf-8')
    caminho.chmod(caminho.stat().st_mode | stat.S_IEXEC)


def zip_com(nome):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        info = zipfile.ZipInfo(nome)
        info.external_attr = 0o755 << 16
        z.writestr(info, TERRAFORM if nome == 'terraform' else TFLINT)
    return buf.getvalue()


class CloudShell(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / 'repo'
        for rel in ('infra/terraform', 'tools/github', '.github/workflows'):
            shutil.copytree(RAIZ_REAL / rel, self.repo / rel, ignore=shutil.ignore_patterns('__pycache__', '.terraform'))
        self.falso = self.tmp / 'falso'
        self.falso.mkdir()
        self.bin = self.tmp / 'bin'
        self.bin.mkdir()
        self.home = self.tmp / 'home'
        self.home.mkdir()
        zips = {n: zip_com(n) for n in ('terraform', 'tflint')}
        for n, dados in zips.items():
            (self.falso / f'{n}.zip').write_bytes(dados)
        self.infra_yml(hashlib.sha256(zips['terraform']).hexdigest(), hashlib.sha256(zips['tflint']).hexdigest())
        git_real = shutil.which('git')
        for nome, texto in (('gcloud', GCLOUD), ('gh', GH), ('curl', CURL), ('git', GIT)):
            executavel(self.bin / nome, texto)
        env = {**os.environ, 'GIT_REAL': git_real}
        for c in (['init', '-q', '-b', 'main'], ['config', 'user.email', 't@example.com'], ['config', 'user.name', 't'],
                  ['add', '-A'], ['commit', '-q', '-m', 'base'], ['remote', 'add', 'origin', REPO],
                  ['update-ref', 'refs/remotes/origin/main', 'HEAD']):
            subprocess.run([git_real, '-C', str(self.repo), *c], check=True, env=env)
        self.commit = subprocess.run([git_real, '-C', str(self.repo), 'rev-parse', 'HEAD'], capture_output=True,
                                     text=True, check=True).stdout.strip()
        self.gcloud({})
        self.checks('success')
        (self.falso / 'plano.json').write_text(json.dumps({'resource_changes': [
            {'address': 'google_storage_bucket.state', 'change': {'actions': ['create']}},
            {'address': f'google_service_account_iam_member.x["user:{DONO}"]', 'change': {'actions': ['create']}}]}),
            encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def infra_yml(self, sha_tf, sha_tl):
        p = self.repo / '.github/workflows/infra.yml'
        t = p.read_text(encoding='utf-8').splitlines(keepends=True)
        t = [(l[:l.index('TERRAFORM_SHA256:')] + f'TERRAFORM_SHA256: {sha_tf}\n') if 'TERRAFORM_SHA256:' in l else
             (l[:l.index('TFLINT_SHA256:')] + f'TFLINT_SHA256: {sha_tl}\n') if 'TFLINT_SHA256:' in l else l for l in t]
        p.write_text(''.join(t), encoding='utf-8')
        subprocess.run(['git', '-C', str(self.repo), 'status'], capture_output=True)

    def gcloud(self, extra):
        base = {'conta': DONO, 'numero': '999', 'pai': '', 'bucket': None, 'politica_bucket': {'bindings': []},
                'politica_projeto': {'bindings': [{'role': 'roles/owner', 'members': [f'user:{DONO}']}]},
                'papeis': {'roles/owner': ['storage.objects.get'], 'roles/editor': ['storage.objects.get'],
                           'roles/run.viewer': ['run.services.get'],
                           'roles/run.serviceAgent': ['storage.objects.get']}}
        (self.falso / 'gcloud.json').write_text(json.dumps({**base, **extra}), encoding='utf-8')

    def checks(self, conclusao):
        exigidos = json.loads((self.repo / 'tools/github/protecao-main.json').read_text(encoding='utf-8'))
        nomes = [c['context'] for r in exigidos['rules'] if r['type'] == 'required_status_checks'
                 for c in r['parameters']['required_status_checks']]
        runs = [{'name': n, 'conclusion': 'success', 'app': {'id': 15368}} for n in nomes]
        runs[0]['conclusion'] = conclusao
        (self.falso / 'checks.json').write_text(json.dumps({'check_runs': runs}), encoding='utf-8')

    def rodar(self, *args, entrada='', extra_env=None):
        env = {**os.environ, 'PATH': f'{self.bin}{os.pathsep}{os.environ["PATH"]}', 'FALSO': str(self.falso),
               'PROJ': PROJETO, 'HOME': str(self.home), 'GIT_REAL': shutil.which('git'), **(extra_env or {})}
        r = subprocess.run(['bash', str(self.repo / 'infra/terraform/cloudshell.sh'), *args], input=entrada,
                           capture_output=True, text=True, env=env, cwd=self.tmp)
        log = self.falso / 'chamadas.log'
        return r, (log.read_text(encoding='utf-8').splitlines() if log.exists() else [])

    def estado(self):
        return json.loads((self.falso / 'gcloud.json').read_text(encoding='utf-8'))

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
        subprocess.run(['git', '-C', str(self.repo), 'checkout', '-q', '-b', 'outra'], check=True)
        r, _ = self.rodar('conferir')
        self.assertIn("está em 'outra'", r.stderr)

    def test_conferir_para_se_a_main_andou(self):
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-q', '--allow-empty', '-m', 'local'], check=True)
        r, _ = self.rodar('conferir')
        self.assertIn('não é a main atual', r.stderr)

    # state ----------------------------------------------------------------------------------------------------------

    def test_state_cria_confere_e_tira_so_os_vinculos_presentes(self):
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('só com o dono do projeto', r.stdout)
        remocoes = [c for c in chamadas if 'remove-iam-policy-binding' in c]
        self.assertEqual(len(remocoes), 2, remocoes)
        self.assertTrue(any('--uniform-bucket-level-access --public-access-prevention' in c for c in chamadas))
        r, chamadas = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse([c for c in chamadas if 'remove-iam-policy-binding' in c and c not in remocoes])

    def test_state_para_com_membro_extra_no_bucket(self):
        self.rodar('state', PROJETO)
        e = self.estado()
        e['politica_bucket']['bindings'].append({'role': 'roles/storage.objectViewer', 'members': ['user:outro@x.com']})
        (self.falso / 'gcloud.json').write_text(json.dumps(e), encoding='utf-8')
        r, _ = self.rodar('state', PROJETO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('membro(s) além do dono', r.stderr)
        self.assertNotIn('outro@x.com', r.stderr + r.stdout)

    def test_state_para_com_pasta_ou_organizacao_acima(self):
        self.gcloud({'pai': 'organization'})
        r, _ = self.rodar('state', PROJETO)
        self.assertIn('acesso herdado ao state não é conferível', r.stderr)

    def test_state_para_com_storage_herdado_do_projeto(self):
        for papel in ('roles/editor', 'roles/storage.objectViewer', 'projects/x/roles/custom'):
            with self.subTest(papel=papel):
                self.gcloud({'politica_projeto': {'bindings': [
                    {'role': 'roles/owner', 'members': [f'user:{DONO}']},
                    {'role': papel, 'members': ['serviceAccount:sa-infra-github@x.iam.gserviceaccount.com']}]},
                    'papeis': {'roles/editor': ['storage.objects.get'], 'roles/storage.objectViewer': ['storage.objects.list'],
                               'projects/x/roles/custom': ['storage.objects.get']}})
                r, _ = self.rodar('state', PROJETO)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f'serviceAccount com {papel} alcança objetos do Storage', r.stderr)
                self.assertNotIn('sa-infra-github@', r.stderr)

    def test_state_aceita_agente_de_servico_e_papel_sem_storage(self):
        self.gcloud({'politica_projeto': {'bindings': [
            {'role': 'roles/owner', 'members': [f'user:{DONO}']},
            {'role': 'roles/run.serviceAgent', 'members': ['serviceAccount:service-999@serverless-robot-prod.iam.gserviceaccount.com']},
            {'role': 'roles/run.viewer', 'members': ['serviceAccount:sa-agentes-leitura@x.iam.gserviceaccount.com']}]}})
        r, _ = self.rodar('state', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)

    # planejar e aplicar ---------------------------------------------------------------------------------------------

    def planejar(self):
        self.assertEqual(self.rodar('state', PROJETO)[0].returncode, 0)
        return self.rodar('planejar', PROJETO)

    def test_planejar_fora_do_checkout_com_saida_mascarada(self):
        r, chamadas = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        trabalho = self.home / '.safrion' / PROJETO
        self.assertTrue((trabalho / 'bootstrap.tfvars').exists())
        self.assertTrue((trabalho / 'bootstrap.tfplan').exists())
        self.assertEqual(oct(trabalho.stat().st_mode & 0o777), '0o700')
        self.assertFalse(list((self.repo / 'infra/terraform/bootstrap').glob('*.tfvars')))
        self.assertFalse((self.repo / 'infra/terraform/bootstrap/.terraform').exists())
        self.assertNotIn(DONO, r.stdout + r.stderr)
        self.assertIn('***@example.com', r.stdout)
        hash_ = hashlib.sha256((trabalho / 'bootstrap.tfplan').read_bytes()).hexdigest()
        self.assertIn(f'SHA-256: {hash_}', r.stdout)
        self.assertIn('Criar 2 · mudar 0 · destruir 0', r.stdout)
        tfvars = (trabalho / 'bootstrap.tfvars').read_text(encoding='utf-8')
        self.assertIn('github_repository_id = "111"', tfvars)
        self.assertIn(f'operador             = "user:{DONO}"', tfvars)
        self.assertTrue(any(c.startswith('terraform init') and f'bucket={PROJETO}-tfstate-bootstrap' in c for c in chamadas))

    def test_download_com_sha_errado_para_antes_de_executar(self):
        self.infra_yml('0' * 64, '0' * 64)
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-q', '-am', 'sha errado'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'update-ref', 'refs/remotes/origin/main', 'HEAD'], check=True)
        r, chamadas = self.planejar()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('SHA-256 do terraform diferente do infra.yml', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform ')])

    def test_aplicar_so_com_o_hash_do_plano(self):
        r, _ = self.planejar()
        self.assertEqual(r.returncode, 0, r.stderr)
        plano = self.home / '.safrion' / PROJETO / 'bootstrap.tfplan'
        certo = hashlib.sha256(plano.read_bytes()).hexdigest()
        r, chamadas = self.rodar('aplicar', PROJETO, 'f' * 64)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('outro SHA-256', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform apply')])
        r, chamadas = self.rodar('aplicar', PROJETO, certo)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len([c for c in chamadas if c.startswith('terraform apply')]), 1)
        self.assertTrue((self.home / '.safrion' / PROJETO / 'saidas.json').exists())

    def test_aplicar_recusa_hash_malformado(self):
        r, chamadas = self.rodar('aplicar', PROJETO, 'abc')
        self.assertIn('64 caracteres', r.stderr)
        self.assertFalse([c for c in chamadas if c.startswith('terraform')])

    def test_projeto_invalido(self):
        for p in ('Safrion', 'a', 'x-', '../etc'):
            with self.subTest(p=p):
                r, _ = self.rodar('state', p)
                self.assertIn('ID de projeto inválido', r.stderr)

    def test_limpar_apaga_so_o_projeto(self):
        (self.home / '.safrion' / 'outro').mkdir(parents=True)
        self.planejar()
        r, _ = self.rodar('limpar', PROJETO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.home / '.safrion' / PROJETO).exists())
        self.assertTrue((self.home / '.safrion' / 'outro').exists())

    def test_sintaxe(self):
        self.assertEqual(subprocess.run(['bash', '-n', str(AQUI / 'cloudshell.sh')]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
