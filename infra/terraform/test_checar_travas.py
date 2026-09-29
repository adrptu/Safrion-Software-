# Regressões do checar_travas.py: o módulo hml real passa; cada forma conhecida de parecer travado sem estar falha.
# Rodar: python3 -m unittest discover -s infra/terraform -p 'test_*.py'
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import checar_travas as ct

AQUI = Path(__file__).resolve().parent
BANCO = (AQUI / 'hml' / 'banco.tf').read_text(encoding='utf-8')
CLOUD_RUN = (AQUI / 'hml' / 'cloud_run.tf').read_text(encoding='utf-8')
SEGREDOS = (AQUI / 'hml' / 'segredos.tf').read_text(encoding='utf-8')
SSL = 'ssl_mode           = "ENCRYPTED_ONLY"'
CONECTOR = 'connector_enforcement = "REQUIRED"'
CA = 'server_ca_mode     = "GOOGLE_MANAGED_INTERNAL_CA"'
IPV4 = 'ipv4_enabled       = false'
REDE = 'private_network    = var.rede_self_link'
DATA_API = 'data_api_access = "DISALLOW_DATA_API"'
EGRESS = 'egress = "PRIVATE_RANGES_ONLY"'
PEDIDO = 'secret_id           = "hml-vinculo-pedido"'
IGNORE_WEB = '      template[0].containers[0].image,'
IGNORE_JOB = '      template[0].template[0].containers[0].image,'
SEGUNDA = '''
resource "google_sql_database_instance" "outra" {
  name             = "outra"
  database_version = "POSTGRES_17"
  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled = true
    }
  }
}
'''


class Codigo(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.restaurar()

    def restaurar(self):
        """Volta a cópia ao módulo real: faltas() grava por cima, e um subTest herdaria a mutação do anterior."""
        for arq in (AQUI / 'hml').glob('*.tf'):
            shutil.copy(arq, self.dir / arq.name)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def faltas(self, banco=None, extra=None):
        if banco is not None:
            (self.dir / 'banco.tf').write_text(banco, encoding='utf-8')
        for nome, texto in (extra or {}).items():
            (self.dir / nome).write_text(texto, encoding='utf-8')
        return ct.conferir_codigo(self.dir)

    def troca(self, velho, novo):
        self.assertIn(velho, BANCO)
        return BANCO.replace(velho, novo, 1)

    def test_controle_positivo_modulo_real(self):
        self.assertEqual(self.faltas(), [])

    def test_ssl_so_em_comentario_de_bloco(self):
        # Contraprova do Codex (guard-review-35f4d32): a trava num /* */ e o valor real frouxo.
        b = self.troca(SSL, '/* ssl_mode = "ENCRYPTED_ONLY" */\n      ssl_mode = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"')
        self.assertTrue(self.faltas(b))

    def test_ssl_so_em_comentario_de_linha(self):
        for prefixo in ('#', '//'):
            with self.subTest(prefixo=prefixo):
                self.assertTrue(self.faltas(self.troca(SSL, f'{prefixo} {SSL}')))

    def test_trava_dentro_de_string_ou_heredoc_nao_conta(self):
        b = self.troca(SSL, 'ssl_mode = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"')
        b = b.replace('name                = "safrion-hml"',
                      'name                = "safrion-hml"\n  # nota\n  user_nota = <<EOT\nssl_mode = "ENCRYPTED_ONLY"\nEOT', 1)
        self.assertTrue(self.faltas(b))

    def test_valor_nao_literal(self):
        self.assertTrue(self.faltas(self.troca(SSL, 'ssl_mode = var.ssl')))
        self.assertTrue(self.faltas(self.troca(SSL, 'ssl_mode = "${var.ssl}"')))
        self.assertTrue(self.faltas(self.troca(CONECTOR, 'connector_enforcement = local.conector')))

    def test_conector_frouxo(self):
        self.assertTrue(self.faltas(self.troca(CONECTOR, 'connector_enforcement = "NOT_REQUIRED"')))

    def test_rede_autorizada(self):
        rede = CA + '\n      authorized_networks {\n        value = "0.0.0.0/0"\n      }'
        self.assertTrue(self.faltas(self.troca(CA, rede)))
        dinamica = CA + '\n      dynamic "authorized_networks" {\n        for_each = var.redes\n        content {\n          value = authorized_networks.value\n        }\n      }'
        self.assertTrue(self.faltas(self.troca(CA, dinamica)))

    def test_segunda_instancia_no_mesmo_arquivo(self):
        # Contraprova do Codex: a exceção é por arquivo, então nenhuma outra instância pode morar em banco.tf.
        self.assertTrue(self.faltas(BANCO + SEGUNDA))

    def test_segunda_instancia_em_outro_arquivo(self):
        self.assertTrue(self.faltas(extra={'outro.tf': SEGUNDA}))

    def test_instancia_com_outro_nome_ou_em_outro_arquivo(self):
        self.assertTrue(self.faltas(BANCO.replace('"google_sql_database_instance" "hml"', '"google_sql_database_instance" "x"')))
        (self.dir / 'banco.tf').unlink()
        self.assertTrue(self.faltas(extra={'sql.tf': BANCO}))

    def test_ignore_changes_que_esconde_trava(self):
        for alvo in ('settings[0].ip_configuration', 'settings', 'settings[0]', 'all'):
            with self.subTest(alvo=alvo):
                b = self.troca('ignore_changes = [settings[0].disk_size]', f'ignore_changes = [settings[0].disk_size, {alvo}]')
                self.assertTrue(self.faltas(b))

    def test_ignore_changes_com_indice_legado_ou_forma_estranha(self):
        # Achado da revisão do autor: "settings.0.ip_configuration" era lido como número e passava.
        for alvo in ('settings.0.ip_configuration', 'settings.0', 'settings[0].ip_configuration[0].ssl_mode',
                     'settings[0].connector_enforcement', '"settings"'):
            with self.subTest(alvo=alvo):
                b = self.troca('ignore_changes = [settings[0].disk_size]', f'ignore_changes = [settings[0].disk_size, {alvo}]')
                self.assertTrue(self.faltas(b))
        self.assertTrue(self.faltas(self.troca('ignore_changes = [settings[0].disk_size]', 'ignore_changes = all')))
        self.assertEqual(self.faltas(self.troca('ignore_changes = [settings[0].disk_size]', 'ignore_changes = [settings.0.disk_size]')), [])

    def test_override_e_json_nao_escapam(self):
        sobreposicao = 'resource "google_sql_database_instance" "hml" {\n  settings {\n    ip_configuration {\n      ssl_mode = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"\n    }\n  }\n}\n'
        self.assertTrue(self.faltas(extra={'banco_override.tf': sobreposicao}))
        self.assertTrue(self.faltas(extra={'override.tf.json': '{"resource": {}}'}))

    def test_rotulo_com_escape_unicode(self):
        # HML-TF-04 (Codex): o Terraform interpreta \u0067 e \u006e nos rótulos; o guard não pode aceitar a forma.
        escapado = 'resource "\\u0067oogle_sql_database_instance" "hml" {\n  settings {\n    ip_configuration {\n      ssl_mode = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"\n    }\n  }\n}\n'
        self.assertTrue(self.faltas(extra={'rede.tf': escapado}))
        rede = CA + '\n      dynamic "authorized_\\u006eetworks" {\n        for_each = ["0.0.0.0/0"]\n        content {\n          value = authorized_networks.value\n        }\n      }'
        self.assertTrue(self.faltas(self.troca(CA, rede)))

    def test_fora_do_subconjunto(self):
        for nome in ('override.tf', 'x_override.tf', 'x.tofu', 'x.tofu.json', 'x.tf.json'):
            with self.subTest(arquivo=nome):
                self.assertTrue(self.faltas(extra={nome: '# vazio\n'}))
                (self.dir / nome).unlink()
        self.assertTrue(self.faltas(extra={'mod.tf': 'module "m" {\n  source = "./m"\n}\n'}))
        qualquer = CA + '\n      dynamic "x" {\n        for_each = []\n        content {}\n      }'
        self.assertTrue(self.faltas(self.troca(CA, qualquer)))

    def test_hcl_ilegivel_falha(self):
        self.assertTrue(self.faltas(self.troca(SSL, '/* ssl_mode = "ENCRYPTED_ONLY"')))

    # --- Rede privada (ADR 0006): IP público desligado, rede privada, sem ExecuteSql, egress privado no Cloud Run ---

    def test_ipv4_ligado_ausente_ou_nao_literal(self):
        for novo in ('ipv4_enabled = true', '# ipv4_enabled = false', 'ipv4_enabled = "false"',
                     'ipv4_enabled = var.ipv4', 'ipv4_enabled = !true', 'ipv4_enabled = false && var.x'):
            with self.subTest(novo=novo):
                self.assertTrue(self.faltas(self.troca(IPV4, novo)))

    def test_rede_privada_ausente_vazia_ou_nao_referencia(self):
        for novo in ('# private_network = var.rede_self_link', 'private_network = ""', 'private_network = null',
                     'private_network = "${var.rede_self_link}"', 'private_network = trimspace(var.rede_self_link)',
                     'private_network = var'):
            with self.subTest(novo=novo):
                self.assertTrue(self.faltas(self.troca(REDE, novo)))
        # Controle positivo: outra referência simples também serve.
        self.assertEqual(self.faltas(self.troca(REDE, 'private_network = local.rede_privada')), [])

    def test_data_api_liberado_ou_nao_literal(self):
        for novo in ('data_api_access = "ALLOW_DATA_API"', 'data_api_access = var.data_api', 'data_api_access = "${var.x}"'):
            with self.subTest(novo=novo):
                self.assertTrue(self.faltas(self.troca(DATA_API, novo)))
        # O ALLOW também não pode entrar por outro bloco da instância.
        self.assertTrue(self.faltas(self.troca(CA, CA + '\n      data_api_access = "ALLOW_DATA_API"')))

    def test_data_api_ausente_passa(self):
        # O padrão da API é DISALLOW: ausente é aceito no código (o plan confere o valor resolvido).
        self.assertEqual(self.faltas(self.troca(DATA_API, '# sem data_api_access')), [])

    def test_ignore_changes_na_rede_privada(self):
        for alvo in ('settings[0].data_api_access', 'settings[0].ip_configuration[0].ipv4_enabled',
                     'settings[0].ip_configuration[0].private_network', 'settings.0.data_api_access'):
            with self.subTest(alvo=alvo):
                b = self.troca('ignore_changes = [settings[0].disk_size]', f'ignore_changes = [settings[0].disk_size, {alvo}]')
                self.assertTrue(self.faltas(b))

    # --- Subconjunto do analisador léxico (revisão de 28/09: heredoc e strings que o guard lia diferente do Terraform) ---

    def test_heredoc_fora_do_subconjunto(self):
        # Contraprova da revisão: <<EOT-X fechava no guard na linha "EOT" e no Terraform só em "EOT-X". O Terraform lia
        # a versão frouxa e comentava a travada; o guard lia o contrário e passava. Agora todo heredoc é recusado (o
        # módulo não usa nenhum).
        def disfarce(frouxo, travado):
            return f'locals {{\n  nota = <<EOT-X\nx\nEOT-X\n}}\n{frouxo}\n/*\nEOT\n}}\n{travado}# */\n'
        frouxo = self.troca(IPV4, 'ipv4_enabled = true').replace(DATA_API, 'data_api_access = "ALLOW_DATA_API"')
        self.assertTrue(self.faltas(disfarce(frouxo, BANCO)))
        self.assertTrue(self.faltas(extra={'cloud_run.tf': disfarce(CLOUD_RUN.replace(EGRESS, 'egress = "ALL_TRAFFIC"'), CLOUD_RUN)}))
        for forma in ('<<EOT', '<<-EOT', '<<EOT-X', '<< EOT'):
            with self.subTest(forma=forma):
                self.assertTrue(self.faltas(BANCO, extra={'nota.tf': f'locals {{\n  nota = {forma}\nx\nEOT\n}}\n'}))

    def test_escape_de_interpolacao_e_aspas_aninhadas(self):
        # Contraprovas da revisão: "$${" é o texto "${" no HCL, e "${"{"}" tem aspas dentro da interpolação. O guard
        # antigo abria interpolação nos dois e engolia a linha seguinte, com o data_api_access liberado.
        for abertura in ('"$${")', '"${"{"}")'):
            with self.subTest(abertura=abertura):
                b = self.troca('tier                        = "db-f1-micro"',
                               f'tier = trimsuffix("db-f1-micro", {abertura}\n    data_api_access = "ALLOW_DATA_API"\n    # }}")')
                b = b.replace(DATA_API, '# sem data_api_access', 1)
                self.assertTrue(self.faltas(b))
        # Controle positivo: os escapes "$${" e "%%{" são texto e passam.
        self.assertEqual(self.faltas(BANCO, extra={'nota.tf': 'locals {\n  nota = "custo $${x} e %%{y}"\n}\n'}), [])

    def test_interpolacao_fora_do_subconjunto(self):
        for texto in ('"${"{"}"', '"${ 1 /* } */ }"', '"${ a # b }"', '"%{ if true }x%{ endif }"', '"${ {a = 1} }"',
                      '"${ var.a\n}"', '"${var.a}\\\n"', '"${ var.a == "x" }"', '"${~ var.a ~}"'):
            with self.subTest(texto=texto):
                self.assertTrue(self.faltas(extra={'nota.tf': f'locals {{\n  nota = {texto}\n}}\n'}))
        self.assertEqual(self.faltas(extra={'nota.tf': 'locals {\n  nota = "${var.a[0].b}-${f(var.c, 1)}"\n}\n'}), [])

    def test_psc_e_caminho_privado_do_google(self):
        # Revisão: psc_config abriria a instância a outro projeto com o guard verde.
        psc = CA + '\n      psc_config {\n        psc_enabled               = true\n        allowed_consumer_projects = ["projeto-de-terceiro"]\n      }'
        self.assertTrue(self.faltas(self.troca(CA, psc)))
        self.assertTrue(self.faltas(self.troca(CA, CA + '\n      psc_config = []')))
        for valor in ('true', 'var.caminho', '"false"'):
            with self.subTest(valor=valor):
                self.assertTrue(self.faltas(self.troca(CA, f'{CA}\n      enable_private_path_for_google_cloud_services = {valor}')))
        self.assertEqual(self.faltas(self.troca(CA, f'{CA}\n      enable_private_path_for_google_cloud_services = false')), [])
        b = self.troca('ignore_changes = [settings[0].disk_size]', 'ignore_changes = [settings[0].disk_size, settings[0].psc_config]')
        self.assertTrue(self.faltas(b))

    def cloud_run(self, velho, novo, vezes=1):
        self.assertEqual(CLOUD_RUN.count(velho), vezes)
        return self.faltas(extra={'cloud_run.tf': CLOUD_RUN.replace(velho, novo)})

    def test_egress_frouxo_ou_nao_literal_na_web_e_nos_jobs(self):
        # 4 ocorrências: web, preparo, demo-reset e vínculo; cada uma sozinha basta para falhar.
        for novo in ('egress = "ALL_TRAFFIC"', '# egress = "PRIVATE_RANGES_ONLY"', 'egress = var.egress',
                     'egress = "${var.x}"'):
            for ordem in range(4):
                with self.subTest(novo=novo, ordem=ordem):
                    partes = CLOUD_RUN.split(EGRESS)
                    self.assertEqual(len(partes), 5)
                    texto = EGRESS.join(partes[: ordem + 1]) + novo + EGRESS.join(partes[ordem + 1 :])
                    self.assertTrue(self.faltas(extra={'cloud_run.tf': texto}))

    def test_sem_vpc_access_ou_com_conector(self):
        sem_vpc = re.sub(r'\n *vpc_access \{.*?\n( *)network_interfaces \{.*?\n\1\}\n *\}\n', '\n', CLOUD_RUN, count=1, flags=re.S)
        self.assertNotEqual(sem_vpc, CLOUD_RUN)
        self.assertTrue(self.faltas(extra={'cloud_run.tf': sem_vpc}))
        self.assertTrue(self.cloud_run(EGRESS, EGRESS + '\n      connector = "projects/p/locations/r/connectors/c"', 4))
        self.assertTrue(self.cloud_run('network_interfaces {', 'network_interfaces_x {', 4))
        dinamico = 'dynamic "vpc_access" {\n      for_each = []\n      content {\n        egress = "ALL_TRAFFIC"\n      }\n    }\n\n    vpc_access {'
        self.assertTrue(self.cloud_run('vpc_access {', dinamico, 4))

    def test_ignore_changes_que_esconde_o_vpc_access(self):
        for alvo in ('template[0].vpc_access', 'template[0].vpc_access[0].egress', 'template', 'template[0]',
                     'template.0.vpc_access', 'all', '"template"', 'template[*].vpc_access'):
            with self.subTest(servico=alvo):
                self.assertTrue(self.cloud_run(IGNORE_WEB, f'{IGNORE_WEB}\n      {alvo},'))
        for alvo in ('template[0].template[0].vpc_access', 'template[0].template', 'template'):
            with self.subTest(job=alvo):
                self.assertTrue(self.cloud_run(IGNORE_JOB, f'{IGNORE_JOB}\n      {alvo},', 3))
        self.assertTrue(self.cloud_run('ignore_changes = [', 'ignore_changes = all\n    x = [', 4))

    def test_ignore_changes_fora_do_vpc_access_passa(self):
        self.assertEqual(self.cloud_run(IGNORE_WEB, f'{IGNORE_WEB}\n      template[0].scaling,'), [])
        self.assertEqual(self.cloud_run(IGNORE_JOB, f'{IGNORE_JOB}\n      template[0].template[0].timeout,', 3), [])

    def test_cloud_run_fora_do_subconjunto(self):
        v1 = 'resource "google_cloud_run_service" "velho" {\n  name     = "velho"\n  location = "southamerica-east1"\n}\n'
        self.assertTrue(self.faltas(extra={'velho.tf': v1}))
        sem_egress = ('resource "google_cloud_run_v2_job" "outro" {\n  name     = "outro"\n  location = "southamerica-east1"\n'
                      '  template {\n    template {\n      containers {\n        image = "x"\n      }\n    }\n  }\n}\n')
        self.assertTrue(self.faltas(extra={'outro.tf': sem_egress}))

    def test_network_interfaces_sem_destino_utilizavel(self):
        # HML-TF-05 (revisão do Codex de eb90a5f): bloco vazio ou sem network/subnetwork aceitável passava.
        interface = 'network_interfaces {\n        network    = local.rede\n        subnetwork = local.subrede\n      }'
        self.assertEqual(CLOUD_RUN.count(interface), 1)  # a web; os jobs têm um recuo a mais
        for novo in ('network_interfaces {\n      }', 'network_interfaces {\n        tags = ["x"]\n      }',
                     'network_interfaces {\n        network = ""\n      }',
                     'network_interfaces {\n        network = null\n      }',
                     'network_interfaces {\n        subnetwork = trimspace(local.subrede)\n      }',
                     'network_interfaces {\n        network    = local.rede\n        subnetwork = "  "\n      }'):
            with self.subTest(novo=novo):
                self.assertEqual(self.faltas(extra={'cloud_run.tf': CLOUD_RUN.replace(interface, novo)}),
                                 ['cloud_run.tf:65 google_cloud_run_v2_service.web: network_interfaces sem network nem '
                                  'subnetwork em forma aceita (referência ou texto não vazio)'])
        # Controle positivo: basta um dos dois, em forma aceita.
        for novo in ('network_interfaces {\n        subnetwork = local.subrede\n      }',
                     'network_interfaces {\n        network = "projects/p/global/networks/n"\n      }'):
            with self.subTest(positivo=novo):
                self.assertEqual(self.faltas(extra={'cloud_run.tf': CLOUD_RUN.replace(interface, novo)}), [])
        # Nos jobs também.
        do_job = 'network_interfaces {\n          network    = local.rede\n          subnetwork = local.subrede\n        }'
        self.assertEqual(CLOUD_RUN.count(do_job), 3)  # preparo, demo-reset e vínculo
        texto = CLOUD_RUN.replace(do_job, 'network_interfaces {\n        }', 1)
        self.assertEqual(len(self.faltas(extra={'cloud_run.tf': texto})), 1)

    # --- R006-01..05: fixtures do Gemini revisadas pelo Codex. Cada mutação atinge um único trecho, identificado sem
    # "primeira ocorrência", e o diagnóstico tem de ser exatamente o da trava alvo, nada além. Os textos esperados
    # prendem a versão entregue: mudou a mensagem ou a linha, o teste é revisto junto.

    def trecho_unico(self, texto, trecho):
        self.assertEqual(texto.count(trecho), 1, trecho)
        return trecho

    def test_r006_01_ipv4_ligado(self):
        self.assertEqual(self.faltas(), [])
        velho = self.trecho_unico(BANCO, IPV4)
        self.assertEqual(self.faltas(BANCO.replace(velho, 'ipv4_enabled       = true')),
                         ['ipv4_enabled = false ausente ou não literal; sem ele, o IP público volta (GCP-0017)'])

    def test_r006_03_data_api_liberado_direto_em_settings(self):
        inicio = BANCO.index(self.trecho_unico(BANCO, 'resource "google_sql_database_instance" "hml" {'))
        settings = BANCO.index('settings {', inicio) + len('settings {')
        linha = BANCO.index(self.trecho_unico(BANCO, DATA_API), settings)
        meio = BANCO[settings:linha]
        self.assertEqual(meio.count('{'), meio.count('}'))  # direto em settings, fora de bloco aninhado
        # Controles positivos: DISALLOW explícito (o módulo real) e ausente.
        self.assertEqual(self.faltas(), [])
        self.assertEqual(self.faltas(BANCO.replace('    ' + DATA_API + '\n', '')), [])
        self.assertEqual(self.faltas(BANCO.replace(DATA_API, 'data_api_access = "ALLOW_DATA_API"')),
                         ['linha 11: data_api_access diferente de "DISALLOW_DATA_API" literal; o ExecuteSql abriria o '
                          'banco pela internet'])

    def test_r006_04_egress_aberto_so_no_job_preparo(self):
        inicio = CLOUD_RUN.index(self.trecho_unico(CLOUD_RUN, 'resource "google_cloud_run_v2_job" "preparo" {'))
        fim = CLOUD_RUN.index(EGRESS, inicio) + len(EGRESS)
        trecho = self.trecho_unico(CLOUD_RUN, CLOUD_RUN[inicio:fim])
        texto = CLOUD_RUN.replace(trecho, trecho.replace(EGRESS, 'egress = "ALL_TRAFFIC"'))
        self.assertEqual(texto.count(EGRESS), 3)  # web, demo-reset e vínculo seguem privados
        self.assertEqual(self.faltas(extra={'cloud_run.tf': texto}),
                         ['cloud_run.tf:200 google_cloud_run_v2_job.preparo: egress = "PRIVATE_RANGES_ONLY" ausente ou '
                          'não literal'])

    def test_r006_05_ignore_changes_esconde_ip_configuration(self):
        velho = self.trecho_unico(BANCO, 'ignore_changes = [settings[0].disk_size]')
        novo = 'ignore_changes = [settings[0].disk_size, settings[0].ip_configuration]'
        self.assertEqual(self.faltas(BANCO.replace(velho, novo)),
                         ['lifecycle.ignore_changes cobre uma trava (ou tem forma não reconhecida)'])
        # Os lifecycles do Cloud Run ficam intactos: o mesmo diagnóstico, sozinho.
        self.assertEqual(CLOUD_RUN.count('ignore_changes = ['), 4)

    # --- Vínculo (R-006 3c): o hml-vinculo-pedido sem destruição adiada e o job safrion-vinculo com egress privado.
    # Mesmo padrão dos R006: mutação num trecho único e diagnóstico exato, com a linha da versão entregue.

    def no_pedido(self, velho, novo):
        """Troca `velho` pela 1ª ocorrência dele a partir do recurso do pedido, sem tocar nos outros segredos."""
        inicio = SEGREDOS.index(self.trecho_unico(SEGREDOS, 'resource "google_secret_manager_secret" "vinculo_pedido" {'))
        trecho = self.trecho_unico(SEGREDOS, SEGREDOS[inicio : SEGREDOS.index(velho, inicio) + len(velho)])
        return self.faltas(extra={'segredos.tf': SEGREDOS.replace(trecho, trecho[: -len(velho)] + novo)})

    def test_vinculo_controle_positivo(self):
        self.assertEqual(self.faltas(), [])
        self.trecho_unico(SEGREDOS, PEDIDO)
        self.trecho_unico(CLOUD_RUN, 'name                = "safrion-vinculo"')
        self.assertEqual(self.no_pedido('prevent_destroy = true', 'prevent_destroy = true\n    ignore_changes  = [labels]'), [])

    def test_vinculo_pedido_com_destruicao_adiada(self):
        # Com o TTL, destruir só desativa: o pedido com o código seguiria legível por dias. Qualquer valor é recusado.
        for valor in ('"604800s"', '"0s"', 'var.ttl', 'null'):
            with self.subTest(valor=valor):
                self.assertEqual(self.no_pedido(PEDIDO, f'{PEDIDO}\n  version_destroy_ttl = {valor}'),
                                 ['segredos.tf:80 google_secret_manager_secret.vinculo_pedido: version_destroy_ttl presente; '
                                  'o pedido destruído tem de sumir na hora'])

    def test_vinculo_pedido_ignore_changes_esconde_o_ttl(self):
        # Um TTL posto fora do Terraform (console) sumiria do plan.
        for alvo in ('[version_destroy_ttl]', '[labels, version_destroy_ttl]', 'all', '[all]', '["version_destroy_ttl"]'):
            with self.subTest(alvo=alvo):
                self.assertEqual(self.no_pedido('prevent_destroy = true', f'prevent_destroy = true\n    ignore_changes  = {alvo}'),
                                 ['segredos.tf:80 google_secret_manager_secret.vinculo_pedido: lifecycle.ignore_changes cobre o '
                                  'version_destroy_ttl (ou tem forma não reconhecida)'])

    def test_vinculo_pedido_ausente_nao_literal_ou_repetido(self):
        # Fora de um recurso com o nome literal (for_each, variável, interpolação), o código não sabe se tem TTL.
        for novo in ('secret_id           = local.pedido', 'secret_id           = "hml-vinculo-${local.x}"'):
            with self.subTest(novo=novo):
                self.assertEqual(self.no_pedido(PEDIDO, novo),
                                 ['o módulo deve ter exatamente um google_secret_manager_secret com secret_id = '
                                  '"hml-vinculo-pedido" literal; achados: nenhum'])
        copia = 'resource "google_secret_manager_secret" "copia" {\n  secret_id           = "hml-vinculo-pedido"\n}\n'
        # segredos.tf volta ao original: o laço acima o trocou no diretório do teste.
        self.assertEqual(self.faltas(extra={'segredos.tf': SEGREDOS, 'copia.tf': copia}),
                         ['o módulo deve ter exatamente um google_secret_manager_secret com secret_id = "hml-vinculo-pedido" '
                          'literal; achados: copia.tf:1 google_secret_manager_secret.copia, '
                          'segredos.tf:80 google_secret_manager_secret.vinculo_pedido'])

    def isca(self, meta):
        """Contraprova da revisão de 28/09: o recurso literal vira isca (`meta`), o nome entra em local.segredos (com TTL)
        e o job, o IAM e a saída passam a usar o segredo do for_each."""
        real = 'google_secret_manager_secret.hml["hml-vinculo-pedido"]'
        segredos = SEGREDOS.replace(self.trecho_unico(SEGREDOS, '    "hml-oidc-client-secret",\n'),
                                    '    "hml-oidc-client-secret",\n    "hml-vinculo-pedido",\n')
        segredos = segredos.replace(PEDIDO, f'{meta}\n  {PEDIDO}')
        segredos = segredos.replace(self.trecho_unico(segredos, 'secret_id = google_secret_manager_secret.vinculo_pedido.secret_id'),
                                    f'secret_id = {real}.secret_id')
        cloud_run = CLOUD_RUN.replace(self.trecho_unico(CLOUD_RUN, 'google_secret_manager_secret.vinculo_pedido.id'), f'{real}.id')
        saidas = (AQUI / 'hml' / 'outputs.tf').read_text(encoding='utf-8')
        saidas = saidas.replace(self.trecho_unico(saidas, '[google_secret_manager_secret.vinculo_pedido.secret_id]'), '[]')
        self.restaurar()
        return self.faltas(extra={'segredos.tf': segredos, 'cloud_run.tf': cloud_run, 'outputs.tf': saidas})

    def test_vinculo_isca_com_count_ou_for_each(self):
        # Antes: "OK", saída 0, com o segredo que o job lê sob destruição adiada de 7 dias.
        for meta in ('count = 0', 'for_each = toset([])'):
            with self.subTest(meta=meta):
                self.assertEqual(self.isca(meta), [
                    f'segredos.tf:81 google_secret_manager_secret.vinculo_pedido: {meta.split()[0]} no recurso do pedido; '
                    'ele existe sempre, uma vez',
                    '"hml-vinculo-pedido" em string fora do secret_id de segredos.tf:81 '
                    "google_secret_manager_secret.vinculo_pedido: ['cloud_run.tf:49', 'segredos.tf:10', 'segredos.tf:102']",
                    'SAFRION_PEDIDO_SEGREDO deve aparecer uma vez, como google_secret_manager_secret.vinculo_pedido.id; '
                    'achadas: cloud_run.tf:49',
                    'nenhum google_secret_manager_secret_iam_member com secret_id = '
                    'google_secret_manager_secret.vinculo_pedido.secret_id',
                ])
        # Só a isca, sem mais nada: também recusada.
        for meta in ('count = 1', 'for_each = toset(["x"])'):
            with self.subTest(so=meta):
                self.restaurar()
                self.assertEqual(self.no_pedido(PEDIDO, f'{meta}\n  {PEDIDO}'), [
                    f'segredos.tf:80 google_secret_manager_secret.vinculo_pedido: {meta.split()[0]} no recurso do pedido; '
                    'ele existe sempre, uma vez'])

    def test_vinculo_nome_em_outra_string(self):
        # Em local.segredos (TTL de 7 dias) ou num id escrito à mão, o código não sabe que é o mesmo segredo.
        for velho, novo, linha in (
                ('    "hml-oidc-client-secret",\n', '    "hml-oidc-client-secret",\n    "hml-vinculo-pedido",\n', 'segredos.tf:10'),
                ('    "hml-oidc-client-secret",\n', '    "hml-oidc-client-secret",\n    "HML-VINCULO-PEDIDO",\n', 'segredos.tf:10'),
                ('    "hml-oidc-client-secret",\n', '    "hml-oidc-client-secret",\n    "${var.x}-vinculo-pedido",\n', 'segredos.tf:10')):
            with self.subTest(novo=novo):
                texto = SEGREDOS.replace(self.trecho_unico(SEGREDOS, velho), novo)
                self.assertEqual(self.faltas(extra={'segredos.tf': texto}), [
                    '"hml-vinculo-pedido" em string fora do secret_id de segredos.tf:81 '
                    f"google_secret_manager_secret.vinculo_pedido: ['{linha}']"])

    def test_vinculo_variavel_do_job_fora_do_recurso(self):
        ref = 'SAFRION_PEDIDO_SEGREDO     = google_secret_manager_secret.vinculo_pedido.id'
        self.trecho_unico(CLOUD_RUN, ref)
        erro = ('SAFRION_PEDIDO_SEGREDO deve aparecer uma vez, como google_secret_manager_secret.vinculo_pedido.id; '
                'achadas: ')
        for novo, esperado in (
                # Outro segredo, atributo errado, expressão ou mais de uma declaração.
                ('SAFRION_PEDIDO_SEGREDO     = google_secret_manager_secret.hml["hml-db-admin-senha"].id', [erro + 'cloud_run.tf:49']),
                ('SAFRION_PEDIDO_SEGREDO     = google_secret_manager_secret.vinculo_pedido.name', [erro + 'cloud_run.tf:49']),
                ('SAFRION_PEDIDO_SEGREDO     = var.segredo', [erro + 'cloud_run.tf:49']),
                (f'{ref} == "" ? var.x : var.y', [erro + 'cloud_run.tf:49']),
                (f'{ref}\n    SAFRION_PEDIDO_SEGREDO     = var.x', [erro + 'cloud_run.tf:49, cloud_run.tf:50']),
                ('SAFRION_ADMIN_URL_2        = google_secret_manager_secret.vinculo_pedido.id', [erro + 'nenhuma']),
                # Chave entre aspas ou montada num modelo: fora da forma reconhecida.
                ('"SAFRION_PEDIDO_SEGREDO"   = google_secret_manager_secret.vinculo_pedido.id',
                 ["SAFRION_PEDIDO_SEGREDO em string (['cloud_run.tf:49']); só a forma chave = referência é reconhecida",
                  erro + 'nenhuma'])):
            with self.subTest(novo=novo):
                self.assertEqual(self.faltas(extra={'cloud_run.tf': CLOUD_RUN.replace(ref, novo)}), esperado)

    def test_vinculo_iam_fora_do_recurso(self):
        velho = self.trecho_unico(SEGREDOS, 'secret_id = google_secret_manager_secret.vinculo_pedido.secret_id')
        for novo, esperado in (
                ('secret_id = google_secret_manager_secret.hml["hml-db-admin-senha"].secret_id',
                 ['nenhum google_secret_manager_secret_iam_member com secret_id = '
                  'google_secret_manager_secret.vinculo_pedido.secret_id']),
                ('secret_id = google_secret_manager_secret.vinculo_pedido.name',
                 ['segredos.tf:97 google_secret_manager_secret_iam_member.vinculo_pedido: secret_id fora da forma '
                  'google_secret_manager_secret.vinculo_pedido.secret_id'])):
            with self.subTest(novo=novo):
                self.assertEqual(self.faltas(extra={'segredos.tf': SEGREDOS.replace(velho, novo)}), esperado)
        self.assertEqual(self.faltas(extra={'segredos.tf': SEGREDOS.replace(
            velho, 'secret_id = google_secret_manager_secret.vinculo_pedido.id')}), [])

    def test_vinculo_egress_aberto_so_no_job_vinculo(self):
        # Confirma que a checagem de egress, feita em todo google_cloud_run_v2_job, cobre o job novo.
        inicio = CLOUD_RUN.index(self.trecho_unico(CLOUD_RUN, 'resource "google_cloud_run_v2_job" "vinculo" {'))
        fim = CLOUD_RUN.index(EGRESS, inicio) + len(EGRESS)
        trecho = self.trecho_unico(CLOUD_RUN, CLOUD_RUN[inicio:fim])
        texto = CLOUD_RUN.replace(trecho, trecho.replace(EGRESS, 'egress = "ALL_TRAFFIC"'))
        self.assertEqual(texto.count(EGRESS), 3)  # web, preparo e demo-reset seguem privados
        self.assertEqual(self.faltas(extra={'cloud_run.tf': texto}),
                         ['cloud_run.tf:353 google_cloud_run_v2_job.vinculo: egress = "PRIVATE_RANGES_ONLY" ausente ou '
                          'não literal'])


REDE_PLANO = 'https://www.googleapis.com/compute/v1/projects/safrion-hml-exemplo/global/networks/safrion-hml'


def web(egress='PRIVATE_RANGES_ONLY', interfaces=1, desconhecido=None, tipo='google_cloud_run_v2_service'):
    vpc = {'egress': egress, 'network_interfaces': [{'network': 'n', 'subnetwork': 's'}] * interfaces}
    depois = {'vpc_access': [vpc]}
    if tipo == 'google_cloud_run_v2_job':
        depois = {'template': [depois]}
    return {'address': f'{tipo}.x[0]', 'type': tipo,
            'change': {'actions': ['create'], 'after': {'template': [depois]}, 'after_unknown': desconhecido or {}}}


class Plano(unittest.TestCase):
    def plano(self, ssl='ENCRYPTED_ONLY', conector='REQUIRED', redes=None, desconhecido=None, extra=(),
              ipv4=False, rede=REDE_PLANO, data_api='DISALLOW_DATA_API', psc=(), caminho_google=None):
        mudanca = {
            'address': 'google_sql_database_instance.hml', 'type': 'google_sql_database_instance',
            'change': {
                'actions': ['create'],
                'after': {'settings': [{'connector_enforcement': conector, 'data_api_access': data_api,
                                        'ip_configuration': [{'ssl_mode': ssl, 'authorized_networks': redes,
                                                              'ipv4_enabled': ipv4, 'private_network': rede,
                                                              'psc_config': list(psc) if psc is not None else None,
                                                              'enable_private_path_for_google_cloud_services': caminho_google}]}]},
                'after_unknown': desconhecido or {},
            },
        }
        return {'resource_changes': [mudanca, *extra]}

    def faltas(self, plano):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(plano, f)
        try:
            return ct.conferir_plano(Path(f.name))
        finally:
            Path(f.name).unlink()

    def test_controle_positivo(self):
        self.assertEqual(self.faltas(self.plano(redes=[])), [])
        self.assertEqual(self.faltas(self.plano(redes=None)), [])

    def test_redes_desconhecidas(self):
        # Contraprova do Codex: authorized_networks null com after_unknown true passava.
        d = {'settings': [{'ip_configuration': [{'authorized_networks': True}]}]}
        self.assertTrue(self.faltas(self.plano(redes=None, desconhecido=d)))

    def test_valores_desconhecidos(self):
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': [{'ssl_mode': True}]}]})))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'connector_enforcement': True}]})))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': True})))

    def test_valores_frouxos_e_redes(self):
        self.assertTrue(self.faltas(self.plano(ssl='ALLOW_UNENCRYPTED_AND_ENCRYPTED')))
        self.assertTrue(self.faltas(self.plano(conector='NOT_REQUIRED')))
        self.assertTrue(self.faltas(self.plano(redes=[{'value': '1.2.3.4/32'}])))

    def test_segunda_instancia_no_plano(self):
        outra = {'address': 'google_sql_database_instance.outra', 'type': 'google_sql_database_instance',
                 'change': {'actions': ['create'], 'after': {'settings': [{}]}}}
        self.assertTrue(self.faltas(self.plano(extra=[outra])))

    def test_fonte_de_dados_nao_conta_e_formatos_estranhos_falham(self):
        dado = {'address': 'data.google_sql_database_instance.x', 'mode': 'data', 'type': 'google_sql_database_instance',
                'change': {'actions': ['read'], 'after': {'settings': [{}]}}}
        self.assertEqual(self.faltas(self.plano(redes=[], extra=[dado])), [])
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': [True]}]})))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [True]})))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': True}]})))

    def test_instancia_ausente(self):
        self.assertTrue(self.faltas({'resource_changes': []}))

    # --- Rede privada (ADR 0006) ---

    def test_rede_privada_controle_positivo(self):
        self.assertEqual(self.faltas(self.plano(data_api=None)), [])
        job = web(tipo='google_cloud_run_v2_job')
        self.assertEqual(self.faltas(self.plano(extra=[web(), job])), [])
        # Cloud Run que sai do plan (after nulo) não conta.
        saindo = web()
        saindo['change'] = {'actions': ['delete'], 'after': None}
        self.assertEqual(self.faltas(self.plano(extra=[saindo])), [])

    def test_ipv4_ligado_ausente_ou_desconhecido(self):
        for ipv4 in (True, None, 'false', 0):
            with self.subTest(ipv4=ipv4):
                self.assertTrue(self.faltas(self.plano(ipv4=ipv4)))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': [{'ipv4_enabled': True}]}]})))

    def test_rede_privada_vazia_ausente_ou_desconhecida(self):
        for rede in ('', '  ', None, ['x']):
            with self.subTest(rede=rede):
                self.assertTrue(self.faltas(self.plano(rede=rede)))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': [{'private_network': True}]}]})))

    def test_data_api_liberado_ou_desconhecido(self):
        self.assertTrue(self.faltas(self.plano(data_api='ALLOW_DATA_API')))
        self.assertTrue(self.faltas(self.plano(data_api=None, desconhecido={'settings': [{'data_api_access': True}]})))

    def test_cloud_run_egress_frouxo_ou_desconhecido(self):
        for tipo in ('google_cloud_run_v2_service', 'google_cloud_run_v2_job'):
            with self.subTest(tipo=tipo):
                self.assertTrue(self.faltas(self.plano(extra=[web(egress='ALL_TRAFFIC', tipo=tipo)])))
                self.assertTrue(self.faltas(self.plano(extra=[web(egress=None, tipo=tipo)])))
                self.assertTrue(self.faltas(self.plano(extra=[web(interfaces=0, tipo=tipo)])))
        d = {'template': [{'vpc_access': [{'egress': True}]}]}
        self.assertTrue(self.faltas(self.plano(extra=[web(desconhecido=d)])))
        self.assertTrue(self.faltas(self.plano(extra=[web(desconhecido={'template': [{'vpc_access': True}]})])))
        self.assertTrue(self.faltas(self.plano(extra=[web(desconhecido={'template': True})])))
        sem_vpc = web()
        sem_vpc['change']['after'] = {'template': [{'vpc_access': []}]}
        self.assertTrue(self.faltas(self.plano(extra=[sem_vpc])))


    def test_cloud_run_fora_do_subconjunto_no_plano(self):
        # Revisão: o modo plano só olhava v2 service e v2 job; um v1 ou um worker pool com all-traffic passava.
        v1 = {'address': 'google_cloud_run_service.x', 'type': 'google_cloud_run_service',
              'change': {'actions': ['create'], 'after': {'metadata': [{'annotations': {'run.googleapis.com/vpc-access-egress': 'all-traffic'}}]}}}
        pool = {'address': 'google_cloud_run_v2_worker_pool.x', 'type': 'google_cloud_run_v2_worker_pool',
                'change': {'actions': ['create'], 'after': {'template': [{'vpc_access': [{'egress': 'ALL_TRAFFIC'}]}]}}}
        for extra in (v1, pool):
            with self.subTest(tipo=extra['type']):
                self.assertTrue(self.faltas(self.plano(extra=[extra])))
        iam = {'address': 'google_cloud_run_v2_service_iam_member.x', 'type': 'google_cloud_run_v2_service_iam_member',
               'change': {'actions': ['create'], 'after': {'role': 'roles/run.invoker'}}}
        saindo = {**v1, 'change': {'actions': ['delete'], 'after': None}}
        self.assertEqual(self.faltas(self.plano(extra=[iam, saindo])), [])

    def test_psc_e_caminho_privado_no_plano(self):
        for psc in ([{'psc_enabled': True, 'allowed_consumer_projects': ['projeto-de-terceiro']}], [{}], ['x'], 'x'):
            with self.subTest(psc=psc):
                self.assertTrue(self.faltas(self.plano(psc=psc)))
        self.assertTrue(self.faltas(self.plano(desconhecido={'settings': [{'ip_configuration': [{'psc_config': True}]}]})))
        for caminho in (True, 'false', 1):
            with self.subTest(caminho=caminho):
                self.assertTrue(self.faltas(self.plano(caminho_google=caminho)))
        d = {'settings': [{'ip_configuration': [{'enable_private_path_for_google_cloud_services': True}]}]}
        self.assertTrue(self.faltas(self.plano(desconhecido=d)))
        for psc in ((), None, [{'psc_enabled': False, 'allowed_consumer_projects': []}]):
            with self.subTest(psc_ok=psc):
                self.assertEqual(self.faltas(self.plano(psc=psc, caminho_google=False)), [])

    def test_network_interfaces_vazia_ou_desconhecida_no_plano(self):
        # HML-TF-05: [{}], campos nulos ou desconhecidos passavam no plan.
        for tipo in ('google_cloud_run_v2_service', 'google_cloud_run_v2_job'):
            for interface, d in (({}, {}), ({'network': None, 'subnetwork': None}, {}),
                                 ({'network': '', 'subnetwork': '  '}, {}),
                                 ({'network': None, 'subnetwork': None}, {'network': True, 'subnetwork': True}),
                                 ({'network': 'n', 'subnetwork': None}, {'subnetwork': True})):
                with self.subTest(tipo=tipo, interface=interface, desconhecido=d):
                    r = web(tipo=tipo)
                    alvo = r['change']['after']['template'][0]
                    alvo = alvo['template'][0] if tipo == 'google_cloud_run_v2_job' else alvo
                    alvo['vpc_access'][0]['network_interfaces'] = [interface]
                    desc = {'network_interfaces': [d]}
                    r['change']['after_unknown'] = ({'template': [{'template': [{'vpc_access': [desc]}]}]}
                                                    if tipo == 'google_cloud_run_v2_job'
                                                    else {'template': [{'vpc_access': [desc]}]})
                    faltas = self.faltas(self.plano(extra=[r]))
                    self.assertEqual(len(faltas), 1, faltas)
                    self.assertIn('network_interfaces sem network nem subnetwork resolvido e não vazio', faltas[0])
        r = web()
        r['change']['after_unknown'] = {'template': [{'vpc_access': [{'network_interfaces': [True]}]}]}
        self.assertEqual(self.faltas(self.plano(extra=[r])), [f'{r["address"]}: network_interfaces desconhecida no plan'])
        # Controle positivo: só a sub-rede, resolvida.
        r = web()
        r['change']['after']['template'][0]['vpc_access'][0]['network_interfaces'] = [{'network': None, 'subnetwork': 's'}]
        self.assertEqual(self.faltas(self.plano(extra=[r])), [])

    # --- Vínculo (R-006 3c): no plan, o nome resolvido pega também o segredo vindo de for_each ou variável ---

    def segredo(self, secret_id=ct.PEDIDO, ttl=None, desconhecido=None, endereco='google_secret_manager_secret.vinculo_pedido'):
        return {'address': endereco, 'type': 'google_secret_manager_secret',
                'change': {'actions': ['create'], 'after': {'secret_id': secret_id, 'version_destroy_ttl': ttl},
                           'after_unknown': desconhecido or {}}}

    def test_vinculo_pedido_controle_positivo_no_plano(self):
        outro = self.segredo('hml-db-admin-senha', '604800s', endereco='google_secret_manager_secret.hml["hml-db-admin-senha"]')
        for ttl in (None, ''):
            with self.subTest(ttl=ttl):
                self.assertEqual(self.faltas(self.plano(extra=[self.segredo(ttl=ttl), outro])), [])
        saindo = self.segredo(ttl='604800s')
        saindo['change'] = {'actions': ['delete'], 'after': None}
        self.assertEqual(self.faltas(self.plano(extra=[saindo])), [])

    def test_vinculo_pedido_com_destruicao_adiada_no_plano(self):
        endereco = 'google_secret_manager_secret.hml["hml-vinculo-pedido"]'
        self.assertEqual(self.faltas(self.plano(extra=[self.segredo(ttl='604800s', endereco=endereco)])),
                         [f"{endereco}: version_destroy_ttl = '604800s' (desconhecido: False)"])
        self.assertEqual(self.faltas(self.plano(extra=[self.segredo(desconhecido={'version_destroy_ttl': True})])),
                         ['google_secret_manager_secret.vinculo_pedido: version_destroy_ttl = None (desconhecido: True)'])
        self.assertEqual(self.faltas(self.plano(extra=[self.segredo(secret_id=None, desconhecido={'secret_id': True})])),
                         ['google_secret_manager_secret.vinculo_pedido: secret_id desconhecido ou em formato inesperado no plan'])

    # --- R006-02 (fixture do Gemini revisada pelo Codex): rede privada desconhecida no plan ---

    def test_r006_02_rede_privada_desconhecida(self):
        self.assertEqual(self.faltas(self.plano(redes=[])), [])
        d = {'settings': [{'ip_configuration': [{'private_network': True}]}]}
        self.assertEqual(self.faltas(self.plano(redes=[], rede=None, desconhecido=d)),
                         ['private_network ausente, vazio ou desconhecido (desconhecido: True)'])


if __name__ == '__main__':
    unittest.main()
