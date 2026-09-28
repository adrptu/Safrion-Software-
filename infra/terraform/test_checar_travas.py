# Regressões do checar_travas.py: o módulo hml real passa; cada forma conhecida de parecer travado sem estar falha.
# Rodar: python3 -m unittest discover -s infra/terraform -p 'test_*.py'
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import checar_travas as ct

AQUI = Path(__file__).resolve().parent
BANCO = (AQUI / 'hml' / 'banco.tf').read_text(encoding='utf-8')
SSL = 'ssl_mode       = "ENCRYPTED_ONLY"'
CONECTOR = 'connector_enforcement = "REQUIRED"'
CA = 'server_ca_mode = "GOOGLE_MANAGED_INTERNAL_CA"'
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


class Plano(unittest.TestCase):
    def plano(self, ssl='ENCRYPTED_ONLY', conector='REQUIRED', redes=None, desconhecido=None, extra=()):
        mudanca = {
            'address': 'google_sql_database_instance.hml', 'type': 'google_sql_database_instance',
            'change': {
                'actions': ['create'],
                'after': {'settings': [{'connector_enforcement': conector,
                                        'ip_configuration': [{'ssl_mode': ssl, 'authorized_networks': redes}]}]},
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


if __name__ == '__main__':
    unittest.main()
