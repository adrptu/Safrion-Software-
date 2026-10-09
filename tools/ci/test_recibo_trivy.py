"""Recibo do Trivy (CI-DIAG-20261008): identifica achados sem revelar conteúdo; ausente ou inválido nunca é zero."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("recibo_trivy.py")
# Valor sintético e inofensivo (ENG-017): só serve para provar que o recibo não o copia.
VALOR_FALSO = "VALOR-SINTETICO-NAO-SECRETO-7f3a9c"


def vulnerabilidade(**extra):
    return {"VulnerabilityID": "CVE-2026-94483", "PkgName": "next", "InstalledVersion": "16.3.6",
            "FixedVersion": "16.3.8", "Severity": "HIGH", "Title": VALOR_FALSO, "Description": VALOR_FALSO, **extra}


def relatorio(*resultados):
    return {"SchemaVersion": 2, "ArtifactName": "/home/runner/work/x/x", "Results": list(resultados)}


class ReciboTrivy(unittest.TestCase):
    def rodar(self, conteudo):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "trivy-report.json"
            if conteudo is not None:
                origem.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo), encoding="utf-8")
            destino = Path(pasta) / "publicado" / "recibo.json"
            processo = subprocess.run([sys.executable, str(SCRIPT), str(origem), str(destino)],
                                      capture_output=True, text=True, check=False)
            gravado = destino.read_text(encoding="utf-8")
        recibo = json.loads(gravado)
        for saida in (gravado, processo.stdout, processo.stderr):
            self.assertNotIn(VALOR_FALSO, saida)
            self.assertNotIn("/home/runner", saida)
        self.assertEqual(json.loads(processo.stdout.splitlines()[0]), recibo)
        return processo.returncode, recibo

    def test_vulnerabilidade_com_pacote_e_versoes(self):
        codigo, recibo = self.rodar(relatorio({"Target": "pnpm-lock.yaml", "Vulnerabilities": [vulnerabilidade()]}))
        self.assertEqual(codigo, 0)
        self.assertEqual((recibo["relatorio"], recibo["total"]), ("lido", 1))
        self.assertEqual(recibo["contagem"], {"vulnerabilidade:HIGH": 1})
        self.assertEqual(recibo["achados"], [{
            "categoria": "vulnerabilidade", "identificador": "CVE-2026-94483", "gravidade": "HIGH",
            "pacote": "next", "versao_instalada": "16.3.6", "versao_corrigida": "16.3.8", "alvo": "pnpm-lock.yaml",
        }])

    def test_segredo_guarda_regra_e_gravidade_sem_match_nem_code(self):
        segredo = {"RuleID": "generic-api-key", "Category": "Generic", "Severity": "CRITICAL", "Title": VALOR_FALSO,
                   "StartLine": 3, "EndLine": 3, "Match": f"API_KEY={VALOR_FALSO}", "Secret": VALOR_FALSO,
                   "Code": {"Lines": [{"Number": 3, "Content": f"API_KEY={VALOR_FALSO}", "Highlighted": VALOR_FALSO}]}}
        codigo, recibo = self.rodar(relatorio({"Target": "apps/web/.env.local", "Secrets": [segredo]}))
        self.assertEqual(codigo, 0)
        self.assertEqual(recibo["achados"], [{"categoria": "segredo", "identificador": "generic-api-key",
                                              "gravidade": "CRITICAL", "linha": 3, "alvo": "apps/web/.env.local"}])

    def test_configuracao_guarda_identificador_gravidade_e_estado(self):
        configuracao = {"Type": "Dockerfile", "ID": "DS-0002", "AVDID": "AVD-DS-0002", "Severity": "HIGH",
                        "Status": "FAIL", "Message": VALOR_FALSO, "Resolution": VALOR_FALSO,
                        "CauseMetadata": {"Code": {"Lines": [{"Content": VALOR_FALSO}]}}}
        codigo, recibo = self.rodar(relatorio({"Target": "Dockerfile", "Misconfigurations": [configuracao]}))
        self.assertEqual(codigo, 0)
        self.assertEqual(recibo["achados"], [{"categoria": "configuracao", "identificador": "DS-0002",
                                              "gravidade": "HIGH", "estado": "FAIL", "alvo": "Dockerfile"}])

    def test_alvo_absoluto_ou_fora_do_repositorio_e_descartado_e_o_achado_continua_contado(self):
        for alvo in ("/home/runner/work/safrion/pnpm-lock.yaml", "../fora/pnpm-lock.yaml", "C:/x/pnpm-lock.yaml",
                     "~/pnpm-lock.yaml", "pasta\\pnpm-lock.yaml"):
            with self.subTest(alvo=alvo):
                codigo, recibo = self.rodar(relatorio({"Target": alvo, "Vulnerabilities": [
                    vulnerabilidade(PkgPath="/home/runner/work/safrion/node_modules/next/package.json")]}))
                self.assertEqual((codigo, recibo["total"]), (0, 1))
                self.assertIsNone(recibo["achados"][0]["alvo"])
                self.assertIsNone(recibo["achados"][0]["caminho_pacote"])

    def test_caractere_de_controle_descarta_o_campo(self):
        for controle in ("\n::add-mask::x", "\x1b[31m", "\u202e", "\x00"):
            with self.subTest(controle=repr(controle)):
                codigo, recibo = self.rodar(relatorio({"Target": "apps/web" + controle, "Vulnerabilities": [
                    vulnerabilidade(PkgName="next" + controle, FixedVersion="16.3.8" + controle)]}))
                achado = recibo["achados"][0]
                self.assertEqual((codigo, recibo["total"]), (0, 1))
                self.assertEqual((achado["alvo"], achado["pacote"], achado["versao_corrigida"]), (None, None, None))
                self.assertEqual(achado["identificador"], "CVE-2026-94483")

    def test_relatorio_ausente_nao_e_zero_achados(self):
        codigo, recibo = self.rodar(None)
        self.assertEqual(codigo, 1)
        self.assertEqual((recibo["relatorio"], recibo["motivo"]), ("ausente", "RELATORIO_AUSENTE"))
        self.assertIsNone(recibo["achados"])
        self.assertNotIn("total", recibo)

    def test_json_invalido_nao_e_zero_achados(self):
        codigo, recibo = self.rodar('{"SchemaVersion": 2, "Results": [' + VALOR_FALSO)
        self.assertEqual(codigo, 1)
        self.assertEqual((recibo["relatorio"], recibo["motivo"]), ("invalido", "JSON_INVALIDO"))
        self.assertIsNone(recibo["achados"])

    def test_estrutura_inesperada_nao_e_zero_achados(self):
        casos = {
            "ESQUEMA_DESCONHECIDO": [[], {"Results": []}, {"SchemaVersion": 3, "Results": []}],
            "SEM_RESULTS": [{"SchemaVersion": 2}, {"SchemaVersion": 2, "Results": {}}],
            "RESULTADO_INVALIDO": [relatorio("pnpm-lock.yaml")],
            "SECAO_INVALIDA": [relatorio({"Target": "x", "Vulnerabilities": {"VulnerabilityID": VALOR_FALSO}}),
                               relatorio({"Target": "x", "Secrets": [VALOR_FALSO]})],
        }
        for motivo, relatorios in casos.items():
            for conteudo in relatorios:
                with self.subTest(motivo=motivo, conteudo=conteudo):
                    codigo, recibo = self.rodar(conteudo)
                    self.assertEqual((codigo, recibo["relatorio"], recibo["motivo"]), (1, "invalido", motivo))
                    self.assertIsNone(recibo["achados"])

    def test_relatorio_lido_sem_achados_e_o_unico_zero(self):
        codigo, recibo = self.rodar(relatorio({"Target": "pnpm-lock.yaml", "Packages": [{"Name": "next"}]}))
        self.assertEqual((codigo, recibo["relatorio"], recibo["total"], recibo["achados"]), (0, "lido", 0, []))


if __name__ == "__main__":
    unittest.main()
