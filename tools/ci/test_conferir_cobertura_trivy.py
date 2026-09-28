"""FERR-05: sucesso sem inventário não comprova varredura de dependências."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("conferir_cobertura_trivy.py")
PACOTE = {"Name": "decimal.js", "Version": "10.6.0"}


def relatorio(pacotes=None, **alvo):
    return {"SchemaVersion": 2, "Results": [{
        "Target": "pnpm-lock.yaml", "Class": "lang-pkgs", "Type": "pnpm",
        "Packages": [PACOTE] if pacotes is None else pacotes, **alvo,
    }]}


class CoberturaTrivy(unittest.TestCase):
    def rodar(self, report, manifesto=None, extras=None):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            arquivos = {
                "package.json": {"private": True},
                "packages/domain/package.json": manifesto if manifesto is not None else {
                    "dependencies": {"decimal.js": "10.6.0"}},
                **(extras or {}),
            }
            for nome, dados in arquivos.items():
                destino = raiz / nome
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(json.dumps(dados), encoding="utf-8")
            caminho = raiz / "report.json"
            if report is not None:
                caminho.write_text(report if isinstance(report, str) else json.dumps(report), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(caminho), str(raiz)],
                capture_output=True, text=True, check=False,
            )

    def exigir_falha(self, resultado, motivo):
        self.assertEqual(resultado.returncode, 1, resultado.stdout + resultado.stderr)
        self.assertIn(motivo, resultado.stdout + resultado.stderr)

    def test_inventario_com_dependencia_de_producao_passou(self):
        resultado = self.rodar(relatorio())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn("decimal.js@10.6.0", resultado.stdout)

    def test_sem_results_reproduz_scanner_que_le_apenas_env_lockfile(self):
        self.exigir_falha(self.rodar({"SchemaVersion": 2}), "Results")

    def test_results_vazios_nao_sao_varredura_limpa(self):
        self.exigir_falha(self.rodar({"SchemaVersion": 2, "Results": []}), "pnpm-lock.yaml")

    def test_sem_inventario_bloqueia(self):
        self.exigir_falha(self.rodar(relatorio([])), "inventário")

    def test_relatorio_ausente_bloqueia(self):
        self.exigir_falha(self.rodar(None), "FERR-05")

    def test_json_invalido_bloqueia(self):
        self.exigir_falha(self.rodar("{"), "FERR-05")

    def test_estrutura_invalida_bloqueia(self):
        self.exigir_falha(self.rodar({"Results": "ok"}), "Results")

    def test_versao_errada_nao_prova_cobertura(self):
        self.exigir_falha(self.rodar(relatorio([{"Name": "decimal.js", "Version": "1.0.0"}])), "decimal.js@10.6.0")

    def test_pacote_em_outro_lockfile_nao_compensa_falta_no_principal(self):
        self.exigir_falha(self.rodar(relatorio(Target="fixture/pnpm-lock.yaml")), "pnpm-lock.yaml")

    def test_outro_ecossistema_nao_compensa_falta_no_pnpm(self):
        self.exigir_falha(self.rodar(relatorio(Type="npm")), "pnpm-lock.yaml")

    def test_segunda_dependencia_ausente_bloqueia(self):
        self.exigir_falha(self.rodar(relatorio(), extras={
            "apps/web/package.json": {"dependencies": {"exemplo": "1.2.3"}},
        }), "exemplo@1.2.3")

    def test_dependencia_opcional_tambem_exige_cobertura(self):
        self.exigir_falha(self.rodar(relatorio(), extras={
            "package.json": {"optionalDependencies": {"exemplo": "1.2.3"}},
        }), "exemplo@1.2.3")

    def test_versao_nao_fixada_exige_revisar_o_contrato(self):
        self.exigir_falha(self.rodar(relatorio(), manifesto={
            "dependencies": {"decimal.js": "^10.6.0"},
        }), "versão exata")

    def test_manifesto_sem_dependencias_nao_da_aprovacao_vazia(self):
        self.exigir_falha(self.rodar(relatorio(), manifesto={}), "dependência de produção")

    def test_workspace_resolve_nome_interno_e_mantem_externas(self):
        resultado = self.rodar(relatorio(), manifesto={
            "name": "@safrion/domain", "dependencies": {"decimal.js": "10.6.0"},
        }, extras={
            "packages/db/package.json": {
                "name": "@safrion/db", "dependencies": {"@safrion/domain": "workspace:*"},
            },
            "apps/web/package.json": {
                "name": "@safrion/web", "dependencies": {"@safrion/db": "workspace:*"},
            },
        })
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn("decimal.js@10.6.0", resultado.stdout)
        self.assertNotIn("@safrion/", resultado.stdout)

    def test_externa_do_pacote_interno_nao_pode_sumir_do_inventario(self):
        self.exigir_falha(self.rodar(relatorio(), extras={
            "packages/db/package.json": {
                "name": "@safrion/db", "optionalDependencies": {"exemplo": "1.2.3"},
            },
            "apps/web/package.json": {"dependencies": {"@safrion/db": "workspace:*"}},
        }), "exemplo@1.2.3")

    def test_workspace_opcional_exige_pacote_local_e_cobre_suas_externas(self):
        resultado = self.rodar(relatorio(), manifesto={
            "name": "@safrion/domain", "dependencies": {"decimal.js": "10.6.0"},
        }, extras={"package.json": {
            "optionalDependencies": {"@safrion/domain": "workspace:*"},
        }})
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    def test_workspace_ausente_falha_mesmo_com_homonimo_no_relatorio(self):
        self.exigir_falha(self.rodar(relatorio([PACOTE, {
            "Name": "@safrion/ausente", "Version": "1.0.0",
        }]), extras={"package.json": {
            "dependencies": {"@safrion/ausente": "workspace:*"},
        }}), "pacote interno ausente")

    def test_nome_duplicado_entre_packages_e_apps_bloqueia(self):
        self.exigir_falha(self.rodar(relatorio(), manifesto={
            "name": "@safrion/domain", "dependencies": {"decimal.js": "10.6.0"},
        }, extras={"apps/duplicado/package.json": {"name": "@safrion/domain"}}),
            "nome interno duplicado")

    def test_manifesto_fora_do_escopo_nao_resolve_workspace(self):
        self.exigir_falha(self.rodar(relatorio(), extras={
            "fixtures/domain/package.json": {"name": "@safrion/domain"},
            "package.json": {"dependencies": {"@safrion/domain": "workspace:*"}},
        }), "pacote interno ausente")

    def test_nome_da_raiz_nao_finge_pacote_interno(self):
        self.exigir_falha(self.rodar(relatorio(), extras={"package.json": {
            "name": "@safrion/root", "dependencies": {"@safrion/root": "workspace:*"},
        }}), "pacote interno ausente")

    def test_formas_nao_contratadas_continuam_bloqueadas(self):
        for versao in ("workspace:^", "workspace:~", "workspace:1.0.0", "workspace:../domain",
                       "file:../domain", "link:../domain", "^1.0.0", "*", None):
            with self.subTest(versao=versao):
                self.exigir_falha(self.rodar(relatorio(), manifesto={
                    "name": "@safrion/domain", "dependencies": {"decimal.js": "10.6.0"},
                }, extras={"packages/db/package.json": {
                    "dependencies": {"@safrion/domain": versao},
                }}), "versão exata")

    def test_nome_local_nao_dispensa_cobertura_quando_referencia_e_externa(self):
        self.exigir_falha(self.rodar(relatorio(), manifesto={
            "name": "@safrion/domain", "dependencies": {"decimal.js": "10.6.0"},
        }, extras={"packages/db/package.json": {
            "dependencies": {"@safrion/domain": "1.0.0"},
        }}), "@safrion/domain@1.0.0")

    def test_so_pacotes_internos_nao_aprova_inventario_vazio(self):
        self.exigir_falha(self.rodar(relatorio(), manifesto={"name": "@safrion/domain"},
            extras={"package.json": {"dependencies": {"@safrion/domain": "workspace:*"}}}),
            "dependência de produção")


if __name__ == "__main__":
    unittest.main()
