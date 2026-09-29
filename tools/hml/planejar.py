#!/usr/bin/env python3
"""PLAN da primeira fase da HML. Sem apply; saídas brutas nunca vão ao log/artefato do GitHub."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile

PROJETO = 'safrion-hml-1390827288'
REPO = 'adrptu/Safrion-Software-'
RAIZ = Path(__file__).resolve().parents[2]
TEMPO_COMANDO = 600


class Recusa(Exception):
    """Só códigos definidos no programa; nunca valores recebidos ou erros de ferramentas."""


def exigir(condicao, codigo):
    if not condicao:
        raise Recusa(codigo)


def validar_contexto(env):
    fixos = {
        'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
        'GITHUB_REPOSITORY': REPO, 'GITHUB_REPOSITORY_ID': '1390827288',
        'GITHUB_REPOSITORY_OWNER_ID': '121058752',
        'GITHUB_WORKFLOW_REF': f'{REPO}/.github/workflows/infra-hml.yml@refs/heads/main',
    }
    exigir(all(env.get(k) == v for k, v in fixos.items()), 'CONTEXTO_RECUSADO')
    campos = {'projeto_numero': ('HML_PROJECT_NUMBER', r'[1-9][0-9]{0,19}'),
              'sha': ('GITHUB_SHA', r'[a-f0-9]{40}'), 'run_id': ('GITHUB_RUN_ID', r'[1-9][0-9]{0,19}'),
              'tentativa': ('GITHUB_RUN_ATTEMPT', r'[1-9][0-9]{0,8}'),
              'geracao': ('CONFIG_GENERATION', r'[1-9][0-9]{0,19}'),
              'config_sha': ('CONFIG_SHA256', r'[a-f0-9]{64}')}
    saida = {}
    for nome, (chave, padrao) in campos.items():
        valor = env.get(chave, '')
        exigir(isinstance(valor, str) and re.fullmatch(padrao, valor), 'ENTRADA_RECUSADA')
        saida[nome] = valor
    return saida


def json_estrito(raw):
    def pares(itens):
        obj = {}
        for chave, valor in itens:
            exigir(chave not in obj, 'JSON_DUPLICADO')
            obj[chave] = valor
        return obj

    def constante(_):
        raise Recusa('JSON_CONSTANTE')

    exigir(not raw.startswith(b'\xef\xbb\xbf'), 'JSON_BOM')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pares, parse_constant=constante)
    except (UnicodeError, ValueError, RecursionError):
        raise Recusa('JSON_INVALIDO') from None


def validar_config(raw, ctx):
    exigir(len(raw) <= 16384, 'CONFIG_TAMANHO')
    exigir(hashlib.sha256(raw).hexdigest() == ctx['config_sha'], 'CONFIG_HASH')
    obj = json_estrito(raw)
    prefixo = f'https://www.googleapis.com/compute/v1/projects/{PROJETO}'
    obrigatorios = {'projeto_id': PROJETO, 'projeto_numero': ctx['projeto_numero'],
                    'rede_self_link': f'{prefixo}/global/networks/safrion-hml',
                    'subrede_self_link': f'{prefixo}/regions/southamerica-east1/subnetworks/safrion-hml-run',
                    'faixa_psa_nome': 'safrion-hml-psa'}
    padroes = {'regiao': 'southamerica-east1', 'criar_cloud_run': False, 'url_controlada': 'iap',
               'oidc_client_id': '', 'versoes_segredos': None, 'iap_permitidos': [], 'origem': None}
    exigir(isinstance(obj, dict) and set(obj) <= set(obrigatorios) | set(padroes) | {'operador'}, 'CONFIG_CHAVES')
    exigir(all(obj.get(k) == v for k, v in obrigatorios.items()), 'CONFIG_DESTINO')
    for chave, valor in padroes.items():
        atual = obj.get(chave, valor)
        exigir(type(atual) is type(valor) and atual == valor, 'CONFIG_FASE1')
    operador = obj.get('operador')
    exigir(isinstance(operador, str) and re.fullmatch(r'user:[^@\s"\\]+@[^@\s"\\]+', operador), 'CONFIG_OPERADOR')
    return {**padroes, **obj}


def resumir_plano(plano):
    exigir(isinstance(plano, dict) and plano.get('errored', False) is False, 'PLANO_INVALIDO')
    exigir(isinstance(plano.get('format_version'), str) and plano['format_version'].startswith('1.'), 'PLANO_FORMATO')
    exigir(plano.get('terraform_version') == '1.16.3', 'PLANO_VERSAO')
    recursos = plano.get('resource_changes')
    drift = plano.get('resource_drift', [])
    exigir(isinstance(recursos, list) and isinstance(drift, list), 'PLANO_RECURSOS')
    contagens = dict.fromkeys(('adicionar', 'alterar', 'apagar', 'ler', 'sem_mudanca'), 0)
    mapa = {'create': 'adicionar', 'update': 'alterar', 'read': 'ler', 'no-op': 'sem_mudanca'}
    for recurso in recursos:
        exigir(isinstance(recurso, dict) and recurso.get('mode') == 'managed', 'PLANO_MODO')
        mudanca = recurso.get('change')
        exigir(isinstance(mudanca, dict), 'PLANO_MUDANCA')
        acoes = mudanca.get('actions')
        exigir(isinstance(acoes, list) and len(acoes) == 1 and acoes[0] in mapa, 'PLANO_DESTRUTIVO_OU_DESCONHECIDO')
        depois = mudanca.get('after')
        exigir(isinstance(depois, dict), 'PLANO_VALORES')
        exigir('project' not in depois or depois['project'] == PROJETO, 'PLANO_OUTRO_PROJETO')
        contagens[mapa[acoes[0]]] += 1
    # Nenhum endereço/índice for_each: pode conter dado pessoal. A revisão privada preserva o detalhe.
    return {'contagens': contagens, 'drift': len(drift)}


def ambiente_ferramentas(env, temp):
    adc = env.get('GOOGLE_APPLICATION_CREDENTIALS', '')
    exigir(adc and Path(adc).is_file() and not Path(adc).is_symlink(), 'ADC_AUSENTE')
    cli_config = temp / 'terraform.rc'
    cli_config.write_text('', encoding='utf-8')
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': env.get('HOME', ''),
            'TMPDIR': str(temp), 'GOOGLE_APPLICATION_CREDENTIALS': adc,
            'CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE': adc, 'CLOUDSDK_CONFIG': str(temp / 'gcloud'),
            'CLOUDSDK_PYTHON': sys.executable, 'CLOUDSDK_CORE_DISABLE_PROMPTS': '1',
            'TF_IN_AUTOMATION': 'true', 'TF_INPUT': 'false', 'TF_DATA_DIR': str(temp / 'tfdata'),
            'TF_CLI_CONFIG_FILE': str(cli_config)}


def comando(args, *, env, cwd, saida, codigo, permitidos=(0,)):
    # Erros de provider, validação de tfvars e guard podem conter valores privados.
    with saida.open('wb') as out, saida.with_suffix('.stderr').open('wb') as err:
        try:
            proc = subprocess.Popen(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, start_new_session=True)
        except OSError:
            raise Recusa(codigo) from None
        try:
            proc.wait(timeout=TEMPO_COMANDO)
        except subprocess.TimeoutExpired:
            # Dar à CLI chance de liberar o lock; depois encerrar seus descendentes antes de limpar os arquivos.
            try:
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
            raise Recusa(codigo) from None
    exigir(proc.returncode in permitidos, codigo)
    return proc.returncode


def planejar(ctx, env):
    exigir(subprocess.check_output(['/usr/bin/git', 'rev-parse', 'HEAD'], cwd=RAIZ, text=True).strip() == ctx['sha'], 'CHECKOUT_DIVERGENTE')
    tf = Path(env.get('SAFRION_TERRAFORM', ''))
    gc = Path(shutil.which('gcloud') or '')
    exigir(tf.is_absolute() and tf.is_file() and gc.is_absolute() and gc.is_file(), 'FERRAMENTA_AUSENTE')
    exigir(Path(env.get('RUNNER_TEMP', '')).is_dir(), 'RUNNER_TEMP_AUSENTE')
    modulo = RAIZ / 'infra/terraform/hml'
    automaticos = {'terraform.tfvars', 'terraform.tfvars.json'}
    exigir(not any(p.name in automaticos or p.name.endswith(('.auto.tfvars', '.auto.tfvars.json'))
                   for p in modulo.iterdir()), 'TFVARS_NO_CHECKOUT')
    # Um workspace novo por execução; nunca herdar state, TF_VAR, TF_CLI_ARGS ou TF_LOG da sessão.
    os.umask(0o077)
    bucket = f'gs://{PROJETO}-tfstate-hml'
    destino = f'{bucket}/planos/{ctx["run_id"]}/{ctx["tentativa"]}'
    with tempfile.TemporaryDirectory(prefix='safrion-plan-', dir=env['RUNNER_TEMP']) as tmp:
        temp = Path(tmp); limpo = ambiente_ferramentas(env, temp)
        def rodar(args, nome, permitidos=(0,)):
            return comando(args, env=limpo, cwd=modulo, saida=temp / (nome + '.stdout'), codigo=nome.upper(), permitidos=permitidos)

        config = temp / 'entrada.json'
        gcloud = [str(gc), '--quiet', '--project=' + PROJETO]
        rodar(gcloud + ['storage', 'cp', f'{bucket}/config/hml.tfvars.json#{ctx["geracao"]}', str(config)], 'baixar_config')
        valores = validar_config(config.read_bytes(), ctx)
        config.write_text(json.dumps(valores, sort_keys=True), encoding='utf-8')
        rodar([sys.executable, str(RAIZ / 'infra/terraform/checar_travas.py')], 'travas_codigo')
        rodar([str(tf), 'init', '-backend-config=bucket=' + PROJETO + '-tfstate-hml', '-input=false', '-lockfile=readonly', '-no-color'], 'init')
        plano = temp / 'tfplan'
        rodar([str(tf), 'plan', '-input=false', '-lock-timeout=120s', '-no-color', '-detailed-exitcode', '-var-file=' + str(config), '-out=' + str(plano)], 'plan', (0, 2))
        rodar([str(tf), 'show', '-json', str(plano)], 'show')
        pj = temp / 'show.stdout'
        resumo = resumir_plano(json_estrito(pj.read_bytes()))
        rodar([sys.executable, str(RAIZ / 'infra/terraform/checar_travas.py'), '--plano', str(pj)], 'travas_plano')
        digest = hashlib.sha256(plano.read_bytes()).hexdigest()
        hashfile = temp / 'tfplan.sha256'; hashfile.write_text(digest + '\n')
        for nome in ('tfplan', 'tfplan.sha256'):
            rodar(gcloud + ['storage', 'cp', str(temp / nome), f'{destino}/{nome}', '--if-generation-match=0'], 'gravar_' + nome.replace('.', '_'))
        rodar(gcloud + ['storage', 'objects', 'describe', f'{destino}/tfplan', '--format=json(generation)'], 'metadados')
        geracao = str(json_estrito((temp / 'metadados.stdout').read_bytes()).get('generation', ''))
        exigir(re.fullmatch(r'[1-9][0-9]{0,19}', geracao), 'GERACAO_INVALIDA')
        recibo = {**ctx, 'plan_sha256': digest, 'plan_generation': geracao, 'objeto': destino + '/tfplan',
                  **resumo, 'travas': 'aprovadas', 'escopo': 'PLAN fase1; nenhum apply ou homologacao comprovada'}
        conferido = temp / 'readback'
        rodar(gcloud + ['storage', 'cp', f'{destino}/tfplan#{geracao}', str(conferido)], 'ler_plano')
        exigir(hashlib.sha256(conferido.read_bytes()).hexdigest() == digest, 'PLANO_HASH_READBACK')
        conferido_hash = temp / 'readback.sha256'
        rodar(gcloud + ['storage', 'cp', f'{destino}/tfplan.sha256', str(conferido_hash)], 'ler_hash')
        exigir(conferido_hash.read_bytes() == (digest + '\n').encode(), 'RECIBO_HASH_READBACK')
        # Contrato aplicar-hml v3 (Claude, revisto por Codex/Gemini): origem separada do resumo humano.
        origem = {'repositorio': REPO, 'workflow': '.github/workflows/infra-hml.yml',
                  'evento': 'workflow_dispatch', 'ref': 'refs/heads/main', 'head_sha': ctx['sha'],
                  'run_id': ctx['run_id'], 'tentativa': ctx['tentativa'],
                  'config_generation': ctx['geracao'], 'config_sha256': ctx['config_sha'],
                  'plan_sha256': digest, 'plan_generation': geracao, 'escopo': 'fase1'}
        raw_origem = (json.dumps(origem, sort_keys=True, indent=2) + '\n').encode('utf-8')
        arquivo_origem = temp / 'recibo.json'; arquivo_origem.write_bytes(raw_origem)
        objeto_origem = destino + '/recibo.json'
        rodar(gcloud + ['storage', 'cp', str(arquivo_origem), objeto_origem, '--if-generation-match=0'], 'gravar_recibo')
        rodar(gcloud + ['storage', 'objects', 'describe', objeto_origem, '--format=json(generation)'], 'metadados_recibo')
        geracao_origem = str(json_estrito((temp / 'metadados_recibo.stdout').read_bytes()).get('generation', ''))
        exigir(re.fullmatch(r'[1-9][0-9]{0,19}', geracao_origem), 'RECIBO_GERACAO_INVALIDA')
        conferido_origem = temp / 'readback-recibo.json'
        rodar(gcloud + ['storage', 'cp', f'{objeto_origem}#{geracao_origem}', str(conferido_origem)], 'ler_recibo')
        exigir(conferido_origem.read_bytes() == raw_origem, 'ORIGEM_READBACK_DIVERGENTE')
        recibo.update(recibo_objeto=objeto_origem, recibo_generation=geracao_origem,
                      recibo_sha256=hashlib.sha256(raw_origem).hexdigest())
        # Só este esquema fechado sai do diretório efêmero. JSON do plan e erros brutos são eliminados no finally.
        return recibo


def main():
    try:
        exigir(sys.argv[1:] in (['conferir'], ['planejar']), 'COMANDO_RECUSADO')
        ctx = validar_contexto(os.environ)
        if sys.argv[1] == 'conferir':
            print('Contexto de planejamento da HML conferido; nenhum acesso GCP.')
            return 0
        recibo = planejar(ctx, os.environ)
        texto = json.dumps(recibo, ensure_ascii=False, indent=2)
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as f:
            f.write('### Plano privado da HML, para revisão\n\n```json\n' + texto + '\n```\n')
        print(texto)
        return 0
    except Recusa as erro:
        print('Planejamento interrompido: ' + str(erro), file=sys.stderr)
        return 1
    except Exception:
        print('Planejamento interrompido: FALHA_INTERNA (sem saída privada no log).', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
