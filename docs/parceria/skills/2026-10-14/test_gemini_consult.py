"""Provas do transporte portátil, sem autenticação nem rede reais."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("consult", Path(__file__).with_name("gemini-consult.py"))
consult = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consult)


class ConsultaPortatil(unittest.TestCase):
    def setUp(self):
        session = patch.dict(os.environ, {"CLOUD_SHELL": "true"})
        session.start()
        self.addCleanup(session.stop)
        # O pacote versionado tem raízes próprias; nunca validar cópias instaladas
        # no lugar dos arquivos em revisão. Na instalação, conservar o catálogo real.
        package = Path(__file__).resolve().parent
        shared, specific = package / "shared", package / "gemini"
        if shared.is_dir() or specific.is_dir():
            catalog = {name: (shared if path.is_relative_to(consult.SHARED_SKILLS_DIR)
                              else specific) / name / "SKILL.md"
                       for name, path in consult.SKILL_CATALOG.items()}
            self.enterContext(patch.object(consult, "SHARED_SKILLS_DIR", shared))
            self.enterContext(patch.object(consult, "SKILLS_DIR", specific))
            self.enterContext(patch.dict(consult.SKILL_CATALOG, catalog, clear=True))

    def invoke(self, arguments, auth=None, response=None):
        stdin = io.TextIOWrapper(io.BytesIO(b"Revisar apenas esta fixture sintetica."), encoding="utf-8")
        output, error = io.StringIO(), io.StringIO()
        with patch.object(consult.sys, "argv", ["consult", *arguments]), \
                patch.object(consult.sys, "stdin", stdin), \
                patch.object(consult.sys, "stdout", output), \
                patch.object(consult.sys, "stderr", error), \
                patch.object(consult.subprocess, "run", **(auth or {})) as auth_call, \
                patch.object(consult.urllib.request, "urlopen", **(response or {})) as http:
            try:
                code = consult.main()
            except SystemExit as exit_error:
                code = exit_error.code
        return code, output.getvalue(), error.getvalue(), auth_call, http

    def skill_fixture(self, files):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name) / "skills"
        root.mkdir()
        for relative, contents in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        catalog = {Path(relative).parts[0]: root / Path(relative).parts[0] / "SKILL.md"
                   for relative in files}
        self.enterContext(patch.object(consult, "SKILLS_DIR", root))
        self.enterContext(patch.object(consult, "SHARED_SKILLS_DIR", Path(folder.name) / "shared"))
        self.enterContext(patch.dict(consult.SKILL_CATALOG, catalog, clear=True))
        return root

    def assert_skill_rejected_before_external_calls(self, names):
        arguments = ["--cloud-shell"]
        for name in names:
            arguments.extend(["--skill", name])
        with patch.object(consult, "authentication_context") as identity:
            code, out, err, auth, http = self.invoke(arguments)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("nenhuma chamada foi enviada", err)
        identity.assert_not_called()
        auth.assert_not_called()
        http.assert_not_called()
        return err

    def test_all_twenty_owned_skills_are_available_without_loading_them_together(self):
        shared = {"agro-gestao-conhecimento", "benchmark-top5", "dev-backend",
                  "dev-ciclo-completo", "dev-frontend-mobile", "dev-infra",
                  "dev-revisao", "dev-testes", "growth-receita-implantacao",
                  "indicadores-satelite", "master-detail-ux", "minimalismo-essencial",
                  "negocios-ecossistema", "safrion-equipe", "tabelas-interativas", "ux-essencial"}
        specific = {"gcp-infra-essencial", "gcp-custos", "gcp-desempenho-incidentes", "revisao-terceira-opiniao"}
        self.assertEqual(set(consult.SKILL_CATALOG), shared | specific)
        for name in sorted(shared | specific):
            with self.subTest(skill=name):
                code, out, err, auth, http = self.invoke(["--dry-run", "--skill", name])
                self.assertEqual((code, err), (0, ""))
                receipt = json.loads(out)
                self.assertEqual({item["name"] for item in receipt["skills"]}, {name})
                for item in receipt["skills"]:
                    source = (consult.SKILL_CATALOG[name].parent / item["file"]).resolve()
                    self.assertEqual(item["resolvedPath"], str(source))
                    self.assertEqual(item["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(receipt["payload"]["generationConfig"]["thinkingConfig"]["thinkingLevel"], "HIGH")
                auth.assert_not_called()
                http.assert_not_called()

    def test_remote_preserves_session_identity_and_runtime(self):
        session = {"CLOUD_SHELL": "true", "PATH": "/google/bin", "CLOUDSDK_CONFIG": "/session/config", "CLOUDSDK_PYTHON": "/session/python"}
        with patch.dict(os.environ, session, clear=True), \
                patch.object(consult.shutil, "which", return_value="/google/bin/gcloud"), \
                patch.object(consult.tempfile, "gettempdir", return_value="/tmp"):
            executable, env, cwd = consult.authentication_context(True)
        self.assertEqual((executable, env, cwd), ("/google/bin/gcloud", session, "/tmp"))

    def test_remote_does_not_introduce_a_local_profile(self):
        with patch.dict(os.environ, {"CLOUD_SHELL": "true", "PATH": "/google/bin"}, clear=True), \
                patch.object(consult.shutil, "which", return_value="/google/bin/gcloud"):
            _, env, cwd = consult.authentication_context(True)
        self.assertNotIn("CLOUDSDK_CONFIG", env)
        self.assertNotIn("CLOUDSDK_PYTHON", env)
        self.assertTrue(Path(cwd).is_dir())

    def test_existing_local_profile_is_preserved(self):
        with patch.object(consult.Path, "home", return_value=Path("/local-user")):
            executable, env, cwd = consult.authentication_context(False)
        self.assertEqual(env["CLOUDSDK_CONFIG"], "/local-user/.config/safrion-gcloud")
        self.assertEqual(cwd, "/private/tmp")
        self.assertTrue(executable.startswith("/local-user/.local/share/safrion-google-cloud/"))

    def test_dry_run_works_without_gcloud_or_network(self):
        with patch.object(consult.shutil, "which", side_effect=AssertionError("must not resolve gcloud")):
            code, out, err, auth, http = self.invoke(["--cloud-shell", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(json.loads(out)["model"], "gemini-3.1-pro-preview")
        auth.assert_not_called()
        http.assert_not_called()

    def test_missing_remote_gcloud_does_not_fall_back_to_mac(self):
        with patch.object(consult.shutil, "which", return_value=None):
            code, out, err, auth, http = self.invoke(["--cloud-shell"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Falha ao obter autenticação", err)
        auth.assert_not_called()
        http.assert_not_called()

    def test_missing_cloud_shell_marker_stops_before_auth(self):
        for marker in (None, "false", "TRUE"):
            with self.subTest(marker=marker), patch.dict(os.environ, {}, clear=True), \
                    patch.object(consult.shutil, "which") as lookup:
                if marker is not None:
                    os.environ["CLOUD_SHELL"] = marker
                code, out, _, auth, http = self.invoke(["--cloud-shell"])
            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            lookup.assert_not_called()
            auth.assert_not_called()
            http.assert_not_called()

    def test_failed_auth_stops_before_http_without_leaking_error(self):
        with patch.object(consult.shutil, "which", return_value="/google/bin/gcloud"):
            code, out, err, _, http = self.invoke(["--cloud-shell"], auth={"side_effect": subprocess.CalledProcessError(1, ["gcloud"], stderr="SENSITIVE_CANARY")})
        self.assertEqual(code, 1)
        self.assertNotIn("SENSITIVE_CANARY", out + err)
        http.assert_not_called()

    def test_auth_timeout_stops_before_http(self):
        with patch.object(consult.shutil, "which", return_value="/google/bin/gcloud"):
            code, _, _, _, http = self.invoke(["--cloud-shell"], auth={"side_effect": subprocess.TimeoutExpired("gcloud", 30)})
        self.assertEqual(code, 1)
        http.assert_not_called()

    def test_receipt_binds_exact_payload_and_keeps_token_out_of_logs(self):
        reply = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "Parecer da fixture."}]}}], "modelVersion": "fixture-version", "responseId": "fixture-id"}
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(consult.shutil, "which", return_value="/google/bin/gcloud"):
            destination = Path(folder) / "receipt.json"
            code, out, err, auth, http = self.invoke(
                ["--cloud-shell", "--output", str(destination)],
                auth={"return_value": subprocess.CompletedProcess([], 0, "TOKEN_CANARY\n")},
                response={"return_value": io.BytesIO(json.dumps(reply).encode())},
            )
            receipt = json.loads(destination.read_text())
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        self.assertEqual(code, 0)
        request = http.call_args.args[0]
        self.assertEqual(receipt["payloadSha256"], hashlib.sha256(request.data).hexdigest())
        self.assertEqual(receipt["authenticationMode"], "cloud-shell-session")
        self.assertTrue(receipt["cloudShellEnvironment"])
        self.assertEqual(receipt["modelRequested"], "gemini-3.1-pro-preview")
        self.assertEqual(receipt["generationConfig"]["thinkingConfig"]["thinkingLevel"], "HIGH")
        self.assertEqual(request.get_header("Authorization"), "Bearer TOKEN_CANARY")
        self.assertNotIn("TOKEN_CANARY", out + err + json.dumps(receipt))
        auth.assert_called_once()
        http.assert_called_once()

    def test_utf8_final_text_budget_accepts_exact_limit_and_rejects_one_more_byte(self):
        root = self.skill_fixture({
            "master-detail-ux/SKILL.md": b"x",
            "master-detail-ux/references/anatomia.md": "Anatomia: ação.".encode(),
            "master-detail-ux/references/checklist.md": "Checklist: conclusão.".encode(),
        })
        parts, _ = consult.load_skills(["master-detail-ux"])
        # Derive presentation overhead from a small result; independently count the
        # actual UTF-8 texts that will be sent, including both reference documents.
        overhead = sum(len(part["text"].encode("utf-8")) for part in parts) - 1
        remaining = consult.MAX_SKILL_BYTES - overhead
        contents = ("á" * (remaining // 2) + "x" * (remaining % 2)).encode("utf-8")
        source = root / "master-detail-ux/SKILL.md"
        source.write_bytes(contents)

        code, out, err, auth, http = self.invoke(["--dry-run", "--skill", "master-detail-ux"])
        self.assertEqual((code, err), (0, ""))
        sent = json.loads(out)["payload"]["systemInstruction"]["parts"][1:]
        self.assertEqual(len(sent), 3)
        self.assertEqual(sum(len(part["text"].encode("utf-8")) for part in sent), 24000)
        auth.assert_not_called()
        http.assert_not_called()

        source.write_bytes(contents + b"x")
        self.assert_skill_rejected_before_external_calls(["master-detail-ux"])

    def test_invalid_utf8_reference_stops_before_authentication_and_http(self):
        self.skill_fixture({
            "master-detail-ux/SKILL.md": b"Main instructions.",
            "master-detail-ux/references/anatomia.md": b"Invalid UTF-8: \xc3",
            "master-detail-ux/references/checklist.md": b"Checklist.",
        })
        self.assert_skill_rejected_before_external_calls(["master-detail-ux"])

    def test_external_skill_symlink_is_rejected_without_reading_its_target(self):
        root = self.skill_fixture({"ux-essencial/SKILL.md": b"placeholder"})
        outside = root.parent / "skills-escape" / "private.md"
        outside.parent.mkdir()
        outside.write_bytes(b"EXTERNAL_CONTENT_CANARY")
        source = root / "ux-essencial/SKILL.md"
        source.unlink()
        source.symlink_to(outside)
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            self.assertNotEqual(path.resolve(), outside.resolve(), "External skill must not be read")
            return original_open(path, *args, **kwargs)

        with patch.object(consult.Path, "open", guarded_open):
            err = self.assert_skill_rejected_before_external_calls(["ux-essencial"])
        self.assertNotIn("EXTERNAL_CONTENT_CANARY", err)

    def test_external_reference_symlink_stops_before_authentication_and_http(self):
        root = self.skill_fixture({
            "master-detail-ux/SKILL.md": b"Main instructions.",
            "master-detail-ux/references/anatomia.md": b"placeholder",
            "master-detail-ux/references/checklist.md": b"Checklist.",
        })
        outside = root.parent / "outside-reference.md"
        outside.write_bytes(b"EXTERNAL_REFERENCE_CANARY")
        reference = root / "master-detail-ux/references/anatomia.md"
        reference.unlink()
        reference.symlink_to(outside)
        err = self.assert_skill_rejected_before_external_calls(["master-detail-ux"])
        self.assertNotIn("EXTERNAL_REFERENCE_CANARY", err)

    def test_missing_required_reference_stops_before_authentication_and_http(self):
        self.skill_fixture({
            "master-detail-ux/SKILL.md": b"Main instructions.",
            "master-detail-ux/references/anatomia.md": b"Anatomy.",
        })
        self.assert_skill_rejected_before_external_calls(["master-detail-ux"])

    def test_selected_order_is_stable_deduplicated_and_hashes_bind_each_supplied_file(self):
        files = {
            "ux-essencial/SKILL.md": b"UX_MARKER [do not read](assets/not-listed.md)",
            "ux-essencial/assets/not-listed.md": b"UNSELECTED_ASSET_CANARY",
            "master-detail-ux/SKILL.md": "MASTER_MARKER ação".encode(),
            "master-detail-ux/references/anatomia.md": b"ANATOMY_MARKER",
            "master-detail-ux/references/checklist.md": b"CHECKLIST_MARKER",
        }
        root = self.skill_fixture(files)
        code, out, err, auth, http = self.invoke([
            "--dry-run", "--skill", "ux-essencial", "--skill", "master-detail-ux",
            "--skill", "ux-essencial", "--skill", "master-detail-ux",
        ])
        self.assertEqual((code, err), (0, ""))
        result = json.loads(out)
        supplied = result["skills"]
        self.assertEqual([(item["name"], item["file"]) for item in supplied], [
            ("ux-essencial", "SKILL.md"), ("master-detail-ux", "SKILL.md"),
            ("master-detail-ux", "references/anatomia.md"),
            ("master-detail-ux", "references/checklist.md"),
        ])
        for item in supplied:
            relative = f"{item['name']}/{item['file']}"
            self.assertEqual(item["sha256"], hashlib.sha256(files[relative]).hexdigest())
            self.assertEqual(item["resolvedPath"], str((root / relative).resolve()))
        texts = result["payload"]["systemInstruction"]["parts"][1:]
        self.assertEqual(len(texts), 4)
        for part, marker in zip(texts, ["UX_MARKER", "MASTER_MARKER", "ANATOMY_MARKER", "CHECKLIST_MARKER"], strict=True):
            self.assertIn(marker, part["text"])
        self.assertNotIn("UNSELECTED_ASSET_CANARY", out)
        auth.assert_not_called()
        http.assert_not_called()

    def test_four_large_skills_do_not_bypass_the_combined_budget(self):
        self.skill_fixture({
            "ux-essencial/SKILL.md": b"U" * 6000,
            "master-detail-ux/SKILL.md": b"M" * 6000,
            "master-detail-ux/references/anatomia.md": b"Anatomy.",
            "master-detail-ux/references/checklist.md": b"Checklist.",
            "minimalismo-essencial/SKILL.md": b"E" * 6000,
            "tabelas-interativas/SKILL.md": b"T" * 6000,
        })
        self.assert_skill_rejected_before_external_calls([
            "ux-essencial", "master-detail-ux", "minimalismo-essencial", "tabelas-interativas",
        ])


if __name__ == "__main__":
    unittest.main()
