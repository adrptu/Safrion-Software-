# -*- coding: utf-8 -*-
"""Contrato do planejador HML: somente funções locais, sem credenciais, Terraform ou rede.

Execução: python3 -m unittest discover -s tools/ci -p test_hml_plan.py
As recusas protegem o destino e a fase autorizados; o resumo nunca transporta valores do plano.
"""
import copy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


RAIZ = Path(__file__).resolve().parents[2]
ESPEC = importlib.util.spec_from_file_location('hml_planejar_test', RAIZ / 'tools/hml/planejar.py')
planejar = importlib.util.module_from_spec(ESPEC)
sys.modules[ESPEC.name] = planejar
ESPEC.loader.exec_module(planejar)

PROJETO = 'safrion-hml-1390827288'
NUMERO = '123456789012'
SHA = 'ab' * 20
CANARIO = 'DADO_PRIVADO_SINTETICO_NAO_DEVE_SAIR'
BASE_REDE = f'https://www.googleapis.com/compute/v1/projects/{PROJETO}'


def ambiente():
    return {
        'GITHUB_EVENT_NAME': 'workflow_dispatch',
        'GITHUB_REF': 'refs/heads/main',
        'GITHUB_REPOSITORY': 'adrptu/Safrion-Software-',
        'GITHUB_REPOSITORY_ID': '1390827288',
        'GITHUB_REPOSITORY_OWNER_ID': '121058752',
        'GITHUB_WORKFLOW_REF': 'adrptu/Safrion-Software-/.github/workflows/infra-hml.yml@refs/heads/main',
        'GITHUB_SHA': SHA,
        'GITHUB_RUN_ID': '1234',
        'GITHUB_RUN_ATTEMPT': '2',
        'HML_PROJECT_NUMBER': NUMERO,
        'CONFIG_GENERATION': '1790700000000000',
        'CONFIG_SHA256': 'cd' * 32,
    }


def configuracao():
    return {
        'projeto_id': PROJETO,
        'projeto_numero': NUMERO,
        'operador': 'user:operador@example.com',
        'rede_self_link': f'{BASE_REDE}/global/networks/safrion-hml',
        'subrede_self_link': f'{BASE_REDE}/regions/southamerica-east1/subnetworks/safrion-hml-run',
        'faixa_psa_nome': 'safrion-hml-psa',
    }


def codificar(config):
    return json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def contexto_do_raw(raw):
    env = ambiente()
    env['CONFIG_SHA256'] = hashlib.sha256(raw).hexdigest()
    return planejar.validar_contexto(env)


def recurso(acao):
    return {
        'address': f'google_storage_bucket.{CANARIO}',
        'mode': 'managed',
        'type': 'google_storage_bucket',
        'name': CANARIO,
        'change': {
            'actions': [acao],
            'before': {'valor': CANARIO},
            'after': {'valor': CANARIO},
            'before_sensitive': {'valor': True},
            'after_sensitive': {'valor': True},
        },
    }


def plano():
    return {
        'format_version': '1.2',
        'terraform_version': '1.16.3',
        'errored': False,
        'resource_changes': [],
        'resource_drift': [],
    }


class RecusasSemDados(unittest.TestCase):
    def recusa(self, funcao, *args):
        with self.assertRaises(planejar.Recusa) as erro:
            funcao(*args)
        self.assertRegex(str(erro.exception), r'^[A-Z][A-Z0-9_]*$')
        self.assertNotIn(CANARIO, str(erro.exception))


class Contexto(RecusasSemDados):
    def test_dispatch_da_main_devolve_identidade_da_execucao(self):
        self.assertEqual(planejar.PROJETO, PROJETO)
        self.assertEqual(planejar.validar_contexto(ambiente()), {
            'projeto_numero': NUMERO, 'sha': SHA, 'run_id': '1234', 'tentativa': '2',
            'geracao': '1790700000000000', 'config_sha': 'cd' * 32,
        })

    def test_identidade_e_origem_divergentes_sao_recusadas(self):
        casos = {
            'GITHUB_EVENT_NAME': 'pull_request_target',
            'GITHUB_REF': 'refs/heads/feature',
            'GITHUB_REPOSITORY': 'outro/Safrion-Software-',
            'GITHUB_REPOSITORY_ID': '1390827289',
            'GITHUB_REPOSITORY_OWNER_ID': '121058753',
            'GITHUB_WORKFLOW_REF': 'adrptu/Safrion-Software-/.github/workflows/outro.yml@refs/heads/main',
        }
        for chave, valor in casos.items():
            with self.subTest(chave=chave):
                env = ambiente()
                env[chave] = valor
                self.recusa(planejar.validar_contexto, env)

    def test_variavel_obrigatoria_ausente_e_recusada(self):
        for chave in ambiente():
            with self.subTest(chave=chave):
                env = ambiente()
                del env[chave]
                self.recusa(planejar.validar_contexto, env)

    def test_ids_nao_aceitam_injecao_zero_sinal_ou_espaco(self):
        for chave in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'HML_PROJECT_NUMBER', 'CONFIG_GENERATION'):
            for valor in ('', '0', '-1', ' 12', '12\n', f'12;{CANARIO}', f'$(echo {CANARIO})'):
                with self.subTest(chave=chave, valor=valor):
                    env = ambiente()
                    env[chave] = valor
                    self.recusa(planejar.validar_contexto, env)

    def test_hashes_exigem_tamanho_e_hexadecimal(self):
        for chave, tamanho in (('GITHUB_SHA', 40), ('CONFIG_SHA256', 64)):
            for valor in ('a' * (tamanho - 1), 'a' * (tamanho + 1), 'g' * tamanho, 'a' * tamanho + '\n'):
                with self.subTest(chave=chave, valor=valor):
                    env = ambiente()
                    env[chave] = valor
                    self.recusa(planejar.validar_contexto, env)


class Configuracao(RecusasSemDados):
    def validar(self, config):
        raw = codificar(config)
        return planejar.validar_config(raw, contexto_do_raw(raw))

    def test_configuracao_minima_da_primeira_fase_e_aceita(self):
        config = configuracao()
        validada = self.validar(config)
        for chave, valor in config.items():
            self.assertEqual(validada[chave], valor)

    def test_defaults_seguros_podem_ser_explicitos(self):
        config = configuracao()
        config.update(criar_cloud_run=False, url_controlada='iap', oidc_client_id='',
                      versoes_segredos=None, iap_permitidos=[], origem=None, regiao='southamerica-east1')
        validada = self.validar(config)
        for chave, valor in config.items():
            self.assertEqual(validada[chave], valor)

    def test_hash_vale_para_os_bytes_exatos_recebidos(self):
        raw = codificar(configuracao())
        contexto = contexto_do_raw(raw)
        self.recusa(planejar.validar_config, raw + b'\n', contexto)

    def test_json_invalido_duplicado_bom_e_constantes_sao_recusados(self):
        raw = codificar(configuracao())
        casos = [b'\xef\xbb\xbf' + raw, raw + b'\xff', raw[:-1], b'[]', b'null',
                 raw[:-1] + b',"projeto_id":"' + PROJETO.encode() + b'"}',
                 raw[:-1] + b',"origem":NaN}', raw[:-1] + b',"origem":Infinity}']
        for invalido in casos:
            with self.subTest(raw=invalido):
                self.recusa(planejar.validar_config, invalido, contexto_do_raw(invalido))

    def test_chave_desconhecida_nao_e_repassada_ao_terraform(self):
        config = configuracao()
        config[CANARIO] = '--destroy'
        raw = codificar(config)
        self.recusa(planejar.validar_config, raw, contexto_do_raw(raw))

    def test_todos_os_campos_de_destino_sao_obrigatorios(self):
        for chave in configuracao():
            with self.subTest(chave=chave):
                config = configuracao()
                del config[chave]
                raw = codificar(config)
                self.recusa(planejar.validar_config, raw, contexto_do_raw(raw))

    def test_outro_projeto_rede_regiao_ou_operador_amplo_sao_recusados(self):
        casos = {
            'projeto_id': 'safrion-producao',
            'projeto_numero': '987654321098',
            'rede_self_link': 'https://www.googleapis.com/compute/v1/projects/outro/global/networks/safrion-hml',
            'subrede_self_link': f'{BASE_REDE}/regions/us-central1/subnetworks/safrion-hml-run',
            'faixa_psa_nome': 'outra-faixa',
            'regiao': 'us-central1',
            'operador': 'allUsers',
        }
        for chave, valor in casos.items():
            with self.subTest(chave=chave):
                config = configuracao()
                config[chave] = valor
                raw = codificar(config)
                self.recusa(planejar.validar_config, raw, contexto_do_raw(raw))

    def test_configuracao_nao_antecipa_publicacao_ou_login(self):
        casos = {
            'criar_cloud_run': True,
            'url_controlada': 'publico',
            'oidc_client_id': 'cliente.apps.googleusercontent.com',
            'versoes_segredos': {'admin': 1, 'migrator': 1, 'app_runtime': 1, 'oidc': 1},
            'iap_permitidos': ['group:outros@example.com'],
            'origem': 'https://outro.example.com',
        }
        for chave, valor in casos.items():
            with self.subTest(chave=chave):
                config = configuracao()
                config[chave] = valor
                raw = codificar(config)
                self.recusa(planejar.validar_config, raw, contexto_do_raw(raw))

    def test_falso_booleano_nao_equivale_a_desligado(self):
        for valor in (0, 'false', None):
            with self.subTest(valor=valor):
                config = configuracao()
                config['criar_cloud_run'] = valor
                raw = codificar(config)
                self.recusa(planejar.validar_config, raw, contexto_do_raw(raw))


class ResumoDoPlano(RecusasSemDados):
    def test_conta_acoes_e_drift_sem_enderecos_ou_valores(self):
        p = plano()
        p['resource_changes'] = [recurso(a) for a in ('create', 'create', 'update', 'read', 'no-op')]
        p['resource_drift'] = [recurso('update'), recurso('update')]
        p['output_changes'] = {'segredo': {'after': CANARIO, 'after_sensitive': True}}
        original = copy.deepcopy(p)
        resumo = planejar.resumir_plano(p)
        self.assertEqual(resumo, {
            'contagens': {'adicionar': 2, 'alterar': 1, 'apagar': 0, 'ler': 1, 'sem_mudanca': 1},
            'drift': 2,
        })
        self.assertNotIn(CANARIO, json.dumps(resumo))
        self.assertEqual(p, original, 'Resumir não deve alterar o plano que será conferido.')

    def test_plano_vazio_tem_contagens_zero(self):
        self.assertEqual(planejar.resumir_plano(plano()), {
            'contagens': {'adicionar': 0, 'alterar': 0, 'apagar': 0, 'ler': 0, 'sem_mudanca': 0},
            'drift': 0,
        })

    def test_delete_e_replacement_sao_recusados(self):
        for acoes in (['delete'], ['delete', 'create'], ['create', 'delete']):
            with self.subTest(acoes=acoes):
                p = plano()
                r = recurso('create')
                r['change']['actions'] = acoes
                p['resource_changes'] = [r]
                self.recusa(planejar.resumir_plano, p)

    def test_data_source_ou_modo_desconhecido_sao_recusados(self):
        for modo in ('data', 'outro', None):
            with self.subTest(modo=modo):
                p = plano()
                r = recurso('read')
                r['mode'] = modo
                p['resource_changes'] = [r]
                self.recusa(planejar.resumir_plano, p)

    def test_plano_com_erro_nao_gera_recibo_de_aceite(self):
        p = plano()
        p['errored'] = True
        self.recusa(planejar.resumir_plano, p)

    def test_versao_e_formato_divergentes_sao_recusados(self):
        for chave, valor in (('format_version', '2.0'), ('format_version', None),
                             ('terraform_version', '1.16.2'), ('terraform_version', '1.16.3-extra')):
            with self.subTest(chave=chave, valor=valor):
                p = plano()
                p[chave] = valor
                self.recusa(planejar.resumir_plano, p)

    def test_schema_incompleto_e_recusado_sem_erro_python_ou_dados(self):
        sem_mudancas = plano()
        del sem_mudancas['resource_changes']
        casos = [None, [], {}, sem_mudancas,
                 {**plano(), 'resource_changes': None}, {**plano(), 'resource_changes': {}},
                 {**plano(), 'resource_changes': [None]},
                 {**plano(), 'resource_changes': [{'mode': 'managed'}]},
                 {**plano(), 'resource_drift': {}}]
        for invalido in casos:
            with self.subTest(plano=invalido):
                self.recusa(planejar.resumir_plano, invalido)

    def test_acoes_fora_do_contrato_sao_recusadas(self):
        for acoes in ([], ['forget'], ['create', 'update'], 'create', None):
            with self.subTest(acoes=acoes):
                p = plano()
                r = recurso('create')
                r['change']['actions'] = acoes
                p['resource_changes'] = [r]
                self.recusa(planejar.resumir_plano, p)


class PlanejamentoLocal(RecusasSemDados):
    """Exercita a orquestração real; só git, ferramentas e transporte GCS são simulados."""

    def setUp(self):
        pasta = tempfile.TemporaryDirectory(prefix='safrion-plan-teste-')
        self.addCleanup(pasta.cleanup)
        self.raiz = Path(pasta.name)
        self.modulo = self.raiz / 'infra/terraform/hml'
        self.modulo.mkdir(parents=True)
        (self.modulo / 'terraform.tfvars.example').write_text('# Exemplo versionado, sem valores reais.\n')
        self.runner = self.raiz / 'runner'
        self.runner.mkdir()
        self.adc = self.raiz / 'adc.json'
        self.adc.write_text('{}')
        self.tf = self.raiz / 'terraform'
        self.gc = self.raiz / 'gcloud'
        self.tf.write_text('# Ferramenta simulada, nunca executada.\n')
        self.gc.write_text('# Ferramenta simulada, nunca executada.\n')
        self.raw = codificar(configuracao())
        self.ctx = contexto_do_raw(self.raw)
        self.env = {**ambiente(), 'CONFIG_SHA256': self.ctx['config_sha'],
                    'GOOGLE_APPLICATION_CREDENTIALS': str(self.adc), 'RUNNER_TEMP': str(self.runner),
                    'SAFRION_TERRAFORM': str(self.tf), 'HOME': str(self.raiz)}
        self.binario = b'PLANO_SINTETICO_' + CANARIO.encode()
        self.digest = hashlib.sha256(self.binario).hexdigest()
        self.pj = plano()
        self.pj['resource_changes'] = [recurso('create')]
        self.pj['output_changes'] = {'privado': {'after': CANARIO, 'after_sensitive': True}}
        self.chamadas = []
        self.falha = None
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        mascara = os.umask(0o077)
        os.umask(mascara)
        self.addCleanup(os.umask, mascara)

    def comando_falso(self, args, *, env, cwd, saida, codigo, permitidos=(0,)):
        args = [str(a) for a in args]
        self.chamadas.append((codigo, args))
        self.assertEqual(cwd, self.modulo)
        self.assertFalse(any(a == 'apply' for a in args))
        self.assertFalse(any(k.startswith(('TF_VAR_', 'TF_LOG', 'TF_CLI_ARGS')) for k in env))
        # Simula também saída privada de erro: nada dela pode sobreviver fora do workspace temporário.
        saida.write_text(CANARIO)
        saida.with_suffix('.stderr').write_text(CANARIO)
        if codigo == self.falha:
            raise planejar.Recusa(codigo)
        if codigo == 'BAIXAR_CONFIG':
            self.assertIn('#' + self.ctx['geracao'], args[-2])
            Path(args[-1]).write_bytes(self.raw)
        elif codigo == 'PLAN':
            self.assertIn(2, permitidos, 'Mudanças previstas retornam 2, não uma falha.')
            Path(next(a.removeprefix('-out=') for a in args if a.startswith('-out='))).write_bytes(self.binario)
            return 2
        elif codigo == 'SHOW':
            saida.write_text(json.dumps(self.pj))
        elif codigo.startswith('GRAVAR_'):
            self.assertIn('--if-generation-match=0', args, 'Artefato de revisão anterior não pode ser sobrescrito.')
        elif codigo == 'METADADOS':
            saida.write_text('{"generation":"456789"}')
        elif codigo == 'LER_PLANO':
            self.assertIn('#456789', args[-2])
            Path(args[-1]).write_bytes(b'PLANO_DIVERGENTE' if self.falha == 'BINARIO_DIVERGENTE' else self.binario)
        elif codigo == 'LER_HASH':
            conteudo = ('0' * 64 if self.falha == 'HASH_DIVERGENTE' else self.digest) + '\n'
            Path(args[-1]).write_text(conteudo)
        elif codigo not in ('TRAVAS_CODIGO', 'INIT', 'TRAVAS_PLANO'):
            self.fail('Ferramenta inesperada na simulação: ' + codigo)
        return 0

    def executar(self):
        with mock.patch.object(planejar, 'RAIZ', self.raiz), \
                mock.patch.object(planejar.shutil, 'which', return_value=str(self.gc)), \
                mock.patch.object(planejar.subprocess, 'check_output', return_value=SHA + '\n') as git, \
                mock.patch.object(planejar, 'comando', side_effect=self.comando_falso), \
                redirect_stdout(self.stdout), redirect_stderr(self.stderr):
            try:
                return planejar.planejar(self.ctx, self.env)
            finally:
                git.assert_called_once_with(['/usr/bin/git', 'rev-parse', 'HEAD'], cwd=self.raiz, text=True)

    def conferir_limpeza(self):
        self.assertEqual(list(self.runner.iterdir()), [], 'Config, plano, JSON e stderr privados devem ser removidos.')
        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(self.stderr.getvalue(), '')
        self.assertTrue((self.modulo / 'terraform.tfvars.example').is_file())

    def conferir_sem_upload(self):
        self.assertFalse(any(c.startswith('GRAVAR_') for c, _ in self.chamadas))

    def test_plan_exit2_com_exemplo_versionado_publica_recibo_minimo_e_limpa(self):
        recibo = self.executar()
        self.assertEqual(recibo['plan_sha256'], self.digest)
        self.assertEqual(recibo['plan_generation'], '456789')
        self.assertEqual(recibo['contagens']['adicionar'], 1)
        self.assertEqual(recibo['travas'], 'aprovadas')
        self.assertNotIn(CANARIO, json.dumps(recibo))
        self.assertNotIn('output_changes', recibo)
        self.assertEqual([c for c, _ in self.chamadas if c.startswith('GRAVAR_')],
                         ['GRAVAR_TFPLAN', 'GRAVAR_TFPLAN_SHA256'])
        self.assertIn('LER_HASH', [c for c, _ in self.chamadas])
        self.conferir_limpeza()

    def test_readback_divergente_do_binario_ou_hash_nao_entrega_recibo(self):
        for falha in ('BINARIO_DIVERGENTE', 'HASH_DIVERGENTE'):
            with self.subTest(falha=falha):
                self.falha = falha
                self.chamadas.clear()
                self.recusa(self.executar)
                self.conferir_limpeza()

    def test_plano_destrutivo_nao_faz_upload(self):
        self.pj['resource_changes'][0]['change']['actions'] = ['delete', 'create']
        self.recusa(self.executar)
        self.conferir_sem_upload()
        self.conferir_limpeza()

    def test_guard_recusado_nao_faz_upload(self):
        self.falha = 'TRAVAS_PLANO'
        self.recusa(self.executar)
        self.assertIn('TRAVAS_PLANO', [c for c, _ in self.chamadas])
        self.conferir_sem_upload()
        self.conferir_limpeza()

    def test_tfvars_ativo_no_checkout_e_recusado_antes_das_ferramentas(self):
        (self.modulo / 'terraform.tfvars').write_text('operador = "' + CANARIO + '"\n')
        self.recusa(self.executar)
        self.assertEqual(self.chamadas, [])
        self.conferir_limpeza()

    def test_ambiente_das_ferramentas_nao_herda_injecoes_terraform(self):
        hostil = {**self.env, 'TF_VAR_operador': CANARIO, 'TF_LOG': 'TRACE', 'TF_LOG_PATH': CANARIO,
                  'TF_CLI_ARGS': '-destroy', 'TF_CLI_ARGS_plan': '-target=privado',
                  'CLOUDSDK_AUTH_ACCESS_TOKEN': CANARIO, 'GOOGLE_OAUTH_ACCESS_TOKEN': CANARIO}
        limpo = planejar.ambiente_ferramentas(hostil, self.runner)
        self.assertFalse(any(k.startswith(('TF_VAR_', 'TF_LOG', 'TF_CLI_ARGS')) for k in limpo))
        self.assertNotIn(CANARIO, json.dumps(limpo))
        self.assertEqual(limpo['GOOGLE_APPLICATION_CREDENTIALS'], str(self.adc))
        self.assertEqual(limpo['TF_INPUT'], 'false')
        self.assertTrue(Path(limpo['TF_DATA_DIR']).is_relative_to(self.runner))

    def test_adc_symlink_e_recusado_antes_de_ler_config_remota(self):
        link = self.raiz / 'adc-link.json'
        link.symlink_to(self.adc)
        self.env['GOOGLE_APPLICATION_CREDENTIALS'] = str(link)
        self.recusa(self.executar)
        self.assertEqual(self.chamadas, [])
        self.conferir_limpeza()


if __name__ == '__main__':
    unittest.main()
