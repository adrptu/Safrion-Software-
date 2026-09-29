# -*- coding: utf-8 -*-
"""Regressão do tools/docs/dados_pessoais.py (roteiro E21): o repositório real bate com o inventário, e coluna ou
variável nova com dado pessoal fora dele falha, assim como item do inventário que sumiu do código."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'tools' / 'docs'))
import dados_pessoais as dp  # noqa: E402


class DadosPessoais(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        for rel in ('packages/db/migrations', 'infra/terraform/bootstrap', 'infra/terraform/hml'):
            destino = self.raiz / rel
            destino.mkdir(parents=True)
            for arq in (RAIZ / rel).iterdir():
                if arq.is_file() and arq.suffix in ('.sql', '.tf'):
                    shutil.copy(arq, destino / arq.name)
        (self.raiz / 'docs').mkdir()
        shutil.copy(RAIZ / dp.INVENTARIO, self.raiz / dp.INVENTARIO)

    def tearDown(self):
        shutil.rmtree(self.raiz)

    def escrever(self, rel, texto):
        (self.raiz / rel).write_text(texto, encoding='utf-8')

    def test_controle_positivo_repositorio_real(self):
        self.assertEqual(dp.conferir(str(RAIZ)), [])
        self.assertEqual(dp.conferir(str(self.raiz)), [])

    def test_coluna_nova_com_dado_pessoal(self):
        for coluna in ('client_ip', 'ip', 'user_agent', 'contact_email', 'mail', 'subject_hint', 'responsible_name'):
            with self.subTest(coluna=coluna):
                self.escrever('packages/db/migrations/0099_teste.sql',
                              f'CREATE TABLE app.teste (\n  id uuid PRIMARY KEY,\n  {coluna} text NOT NULL\n);\n')
                self.assertEqual(dp.conferir(str(self.raiz)),
                                 [f'app.teste.{coluna} tem dado pessoal e não está no inventário'])

    def test_coluna_por_alter_table(self):
        self.escrever('packages/db/migrations/0099_teste.sql', 'ALTER TABLE app.session ADD COLUMN ip_origem inet;\n')
        self.assertEqual(dp.conferir(str(self.raiz)), ['app.session.ip_origem tem dado pessoal e não está no inventário'])

    def test_vizinhos_e_comentario_nao_contam(self):
        self.escrever('packages/db/migrations/0099_teste.sql',
                      '-- email e subject só em comentário\nCREATE TABLE app.teste (\n  id uuid PRIMARY KEY,\n'
                      '  shipment text,\n  equipment text, -- client_ip aqui é comentário\n  tipo text,\n'
                      '  CHECK (tipo <> \'\')\n);\n')
        self.assertEqual(dp.conferir(str(self.raiz)), [])

    def test_variavel_nova_com_email(self):
        for corpo in ('  description = "Contato, no formato user:e-mail."\n  type = string\n',
                      '  type = list(string)\n  # group:testadores\n'):
            with self.subTest(corpo=corpo):
                self.escrever('infra/terraform/hml/extra.tf', f'variable "contato" {{\n{corpo}}}\n')
                self.assertEqual(dp.conferir(str(self.raiz)), ['tf:hml.contato tem dado pessoal e não está no inventário'])

    def test_item_do_inventario_que_sumiu(self):
        texto = (self.raiz / 'packages/db/migrations/0001_fundacao.sql').read_text(encoding='utf-8')
        self.escrever('packages/db/migrations/0001_fundacao.sql',
                      texto.replace("  email text NOT NULL CHECK (email LIKE '%_@_%'),\n", ''))
        self.assertIn('app.app_user.email está no inventário e não existe mais', dp.conferir(str(self.raiz)))

    def test_inventario_ausente(self):
        os.remove(self.raiz / dp.INVENTARIO)
        self.assertEqual(dp.conferir(str(self.raiz)), [f'{dp.INVENTARIO} ausente'])


if __name__ == '__main__':
    unittest.main()
