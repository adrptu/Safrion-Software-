"""Contraprovas: um runner verde não basta se a evidência omite ou mascara jornadas."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from conferir_e2e import conferir


ISOLAMENTO = ["HML-ISO-01: listas", "HML-ISO-02: comando", "HML-ISO-03: API"]


def relatorio():
    specs = []
    titulos = ISOLAMENTO + [f"jornada {i}" for i in range(3, 13)]
    for i, projeto in enumerate(["desktop"] * 12 + ["celular"]):
        specs.append({"id": str(i), "title": titulos[i], "ok": True, "tests": [{
            "projectName": projeto, "expectedStatus": "passed", "status": "expected",
            "results": [{"status": "passed", "retry": 0, "errors": [],
                         "stdout": [{"text": "CANARIO_PRIVADO"}], "attachments": [{"body": "CANARIO_PRIVADO"}]}],
        }]})
    return {"errors": [], "suites": [{"specs": [], "suites": [{"specs": specs}]}],
            "stats": {"expected": 13, "unexpected": 0, "skipped": 0, "flaky": 0}}


class ConferirE2E(unittest.TestCase):
    def setUp(self):
        self.r = relatorio()
        self.specs = self.r["suites"][0]["suites"][0]["specs"]
        self.t = self.specs[0]["tests"][0]

    def test_jornadas_aninhadas_e_recibo_sem_canario(self):
        resultado = conferir(self.r)
        self.assertEqual(resultado["quantidade"], 13)
        self.assertNotIn("CANARIO_PRIVADO", json.dumps(resultado))

    def test_vazio_nao_e_verde(self):
        self.r["suites"] = []
        self.r["stats"]["expected"] = 0
        with self.assertRaises(ValueError): conferir(self.r)

    def test_nove_jornadas_antigas_sem_a_nova_de_acesso_nao_bastam(self):
        self.r["suites"][0]["suites"][0]["specs"] = self.specs[:8] + [self.specs[-1]]
        self.r["stats"]["expected"] = 9
        with self.assertRaises(ValueError): conferir(self.r)

    def test_celular_omitido_recusado_mesmo_com_dez_desktop(self):
        self.specs[-1]["tests"][0]["projectName"] = "desktop"
        with self.assertRaises(ValueError): conferir(self.r)

    def test_skip_nao_conta_como_executado(self):
        self.t.update(expectedStatus="skipped", status="skipped", results=[])
        with self.assertRaises(ValueError): conferir(self.r)

    def test_falha_esperada_nao_e_sucesso(self):
        self.t["expectedStatus"] = "failed"
        self.t["results"][0]["status"] = "failed"
        with self.assertRaises(ValueError): conferir(self.r)

    def test_retry_verde_nao_esconde_primeira_falha(self):
        self.t["results"].append(copy.deepcopy(self.t["results"][0]))
        self.t["results"][0]["status"] = "failed"
        self.t["results"][1]["retry"] = 1
        with self.assertRaises(ValueError): conferir(self.r)

    def test_erro_global_reprova_mesmo_com_casos_verdes(self):
        self.r["errors"] = [{"message": "CANARIO_PRIVADO"}]
        with self.assertRaises(ValueError): conferir(self.r)

    def test_total_adulterado(self):
        self.r["stats"]["expected"] = 11
        with self.assertRaises(ValueError): conferir(self.r)

    def test_id_duplicado_nao_infla_contagem(self):
        self.specs[-1] = copy.deepcopy(self.specs[0])
        with self.assertRaises(ValueError): conferir(self.r)

    def test_resultado_com_erro_nao_passa(self):
        self.t["results"][0]["errors"] = [{"message": "CANARIO_PRIVADO"}]
        with self.assertRaises(ValueError): conferir(self.r)

    def test_jornadas_antigas_omitidas_sem_reposicao_recusadas(self):
        # As 3 provas de isolamento não compensam jornadas antigas que sumiram (acesso e os dois B2-C02, p. ex.).
        for omitidas in (1, 3):
            with self.subTest(omitidas=omitidas):
                r = relatorio()
                specs = r["suites"][0]["suites"][0]["specs"]
                del specs[3:3 + omitidas]
                r["stats"]["expected"] = 13 - omitidas
                with self.assertRaises(ValueError) as erro: conferir(r)
                self.assertEqual(str(erro.exception), "JORNADAS_INCOMPLETAS")

    def test_prova_de_isolamento_trocada_por_outra_jornada_com_os_mesmos_totais(self):
        # Mesmos 12 desktop + 1 celular, todos verdes, IDs únicos: só falta HML-ISO-02.
        self.specs[1] = copy.deepcopy(self.specs[3])
        self.specs[1].update(id="extra", title="jornada extra aprovada")
        with self.assertRaises(ValueError) as erro: conferir(self.r)
        self.assertEqual(str(erro.exception), "PROVA_OBRIGATORIA_AUSENTE")

    def test_prova_de_isolamento_so_no_celular_nao_vale(self):
        self.specs[0]["tests"][0]["projectName"] = "celular"
        self.specs.append(copy.deepcopy(self.specs[3]))
        self.specs[-1].update(id="extra", title="jornada extra desktop")
        self.r["stats"]["expected"] = 14
        with self.assertRaises(ValueError) as erro: conferir(self.r)
        self.assertEqual(str(erro.exception), "PROVA_OBRIGATORIA_AUSENTE")

    def test_id_so_no_inicio_do_titulo_e_com_dois_digitos(self):
        for titulo in ("jornada HML-ISO-03: API", "HML-ISO-030: API", "HML-ISO-03 API"):
            with self.subTest(titulo=titulo):
                self.specs[2]["title"] = titulo
                with self.assertRaises(ValueError): conferir(self.r)

    def test_cli_json_invalido_recibo_seguro_e_saida_um(self):
        with tempfile.TemporaryDirectory() as tmp:
            origem, destino = Path(tmp)/"bruto.json", Path(tmp)/"resumo.json"
            origem.write_text("CANARIO_PRIVADO")
            r = subprocess.run([sys.executable, str(Path(__file__).with_name("conferir_e2e.py")),
                                str(origem), str(destino)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(json.loads(destino.read_text())["aprovado"])
            self.assertNotIn("CANARIO_PRIVADO", r.stdout + r.stderr + destino.read_text())

    def test_cli_arquivo_ausente_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)/"resumo.json"
            r = subprocess.run([sys.executable, str(Path(__file__).with_name("conferir_e2e.py")),
                                str(Path(tmp)/"ausente.json"), str(destino)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(json.loads(destino.read_text())["aprovado"])


if __name__ == "__main__":
    unittest.main()
