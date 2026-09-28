"""Contraprovas: um runner verde não basta se a evidência omite ou mascara jornadas."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from conferir_e2e import conferir


def relatorio():
    specs = []
    for i, projeto in enumerate(["desktop"] * 8 + ["celular"]):
        specs.append({"id": str(i), "title": f"jornada {i}", "ok": True, "tests": [{
            "projectName": projeto, "expectedStatus": "passed", "status": "expected",
            "results": [{"status": "passed", "retry": 0, "errors": [],
                         "stdout": [{"text": "CANARIO_PRIVADO"}], "attachments": [{"body": "CANARIO_PRIVADO"}]}],
        }]})
    return {"errors": [], "suites": [{"specs": [], "suites": [{"specs": specs}]}],
            "stats": {"expected": 9, "unexpected": 0, "skipped": 0, "flaky": 0}}


class ConferirE2E(unittest.TestCase):
    def setUp(self):
        self.r = relatorio()
        self.specs = self.r["suites"][0]["suites"][0]["specs"]
        self.t = self.specs[0]["tests"][0]

    def test_jornadas_aninhadas_e_recibo_sem_canario(self):
        resultado = conferir(self.r)
        self.assertEqual(resultado["quantidade"], 9)
        self.assertNotIn("CANARIO_PRIVADO", json.dumps(resultado))

    def test_vazio_nao_e_verde(self):
        self.r["suites"] = []
        self.r["stats"]["expected"] = 0
        with self.assertRaises(ValueError): conferir(self.r)

    def test_celular_omitido_recusado_mesmo_com_nove_desktop(self):
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
        self.r["stats"]["expected"] = 10
        with self.assertRaises(ValueError): conferir(self.r)

    def test_id_duplicado_nao_infla_contagem(self):
        self.specs[-1] = copy.deepcopy(self.specs[0])
        with self.assertRaises(ValueError): conferir(self.r)

    def test_resultado_com_erro_nao_passa(self):
        self.t["results"][0]["errors"] = [{"message": "CANARIO_PRIVADO"}]
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
