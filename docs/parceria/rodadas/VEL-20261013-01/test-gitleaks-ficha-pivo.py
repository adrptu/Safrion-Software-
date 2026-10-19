"""Portable focal Gitleaks regression; Python 3.9+ and Git are required.

All fixture values are fabricated. Only disposable fixture Git histories are
scanned. The output is one aggregate JSON containing assertions, redacted raw
reports and logs with machine-specific paths replaced by named placeholders.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


LITERAL = "talhao-os-ficha-pivo-v1"
PY_PATH = "tools/prototipo/v37/gen37/ficha_pivo.py"
JS_PATH = "tools/prototipo/v37/gen37/irrigacao_estado.js"
# Deterministically fabricated canary; no account or authority exists for it.
GITHUB_CANARY = "ghp_" + hashlib.sha256(b"local-synthetic-regression-only").hexdigest()[:36]
ENV = {key: value for key, value in os.environ.items()
       if not key.startswith(("GIT_", "GITLEAKS_"))}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_DATE": "2026-10-12T23:00:00Z",
            "GIT_COMMITTER_DATE": "2026-10-12T23:00:00Z"})


def run(args, cwd, timeout=60):
    return subprocess.run([str(arg) for arg in args], cwd=cwd, env=ENV,
                          text=True, capture_output=True, timeout=timeout)


def git(root, *args):
    result = run(["git", *args], root, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sanitize(value, replacements):
    if isinstance(value, dict):
        return {key: sanitize(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item, replacements) for item in value]
    if isinstance(value, str):
        for source, target in sorted(replacements.items(), key=lambda pair: -len(pair[0])):
            value = value.replace(source, target)
    return value


def content(path, value):
    if ".js" in path:
        return ("// Fabricated fixture; not an environment credential.\n"
                "const FPV_KEY='" + value + "';\n"
                "const previous = localStorage.getItem(FPV_KEY);\n"
                "localStorage.setItem(FPV_KEY, previous || '{}');\n")
    return "# Fabricated fixture; not an environment credential.\nKEY='" + value + "'\n"


def make_fixture(directory, name, path, value):
    root = directory / name
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Synthetic fixture")
    git(root, "config", "user.email", "canary@example.invalid")
    git(root, "config", "commit.gpgsign", "false")
    file = root / path
    file.parent.mkdir(parents=True)
    file.write_text(content(path, value))
    git(root, "add", "--", path)
    git(root, "commit", "-qm", "introduce fabricated fixture")
    introduced = git(root, "rev-parse", "HEAD")
    git(root, "rm", "-q", "--", path)
    git(root, "commit", "-qm", "remove fixture; test historical detection")
    return root, introduced, git(root, "rev-parse", "HEAD")


def verify_config_delta(configs):
    base = configs["base"].read_text()
    candidate = configs["candidate"].read_text()
    start = candidate.index("# VEL-20261013-01:")
    end = candidate.index("# HML-SECRET-02:", start)
    block = candidate[start:end]
    paths_block = re.search(r"paths\s*=\s*\[(.*?)\]", block, re.S).group(1)
    regexes_block = re.search(r"regexes\s*=\s*\[(.*?)\]", block, re.S).group(1)
    checks = {
        "all_existing_config_preserved_byte_for_byte": candidate[:start] + candidate[end:] == base,
        "defaults_enabled_in_both": "useDefault = true" in base and "useDefault = true" in candidate,
        "exactly_two_anchored_paths": re.findall(r"'''(.*?)'''", paths_block) == [
            r"^tools/prototipo/v37/gen37/ficha_pivo\.py$",
            r"^tools/prototipo/v37/gen37/irrigacao_estado\.js$"],
        "only_exact_anchored_literal": re.findall(r"'''(.*?)'''", regexes_block) == ["^" + LITERAL + "$"],
        "and_condition": 'condition = "AND"' in block,
        "secret_target": 'regexTarget = "secret"' in block,
        "only_one_new_rule_allowlist": block.count("[[rules.allowlists]]") == 1,
    }
    return {"passed": all(checks.values()), "checks": checks}


def execute(binary, configs, output):
    started = time.monotonic()
    initial_config_hashes = {name: sha256(path) for name, path in configs.items()}
    version = run([binary, "version"], output.parent)
    if version.returncode or version.stdout.strip() != "8.30.1":
        raise RuntimeError("Expected Gitleaks 8.30.1")
    structural = verify_config_delta(configs)
    cases = [
        ("exact_literal_py", PY_PATH, LITERAL, 0, "generic-api-key"),
        ("exact_literal_js", JS_PATH, LITERAL, 0, "generic-api-key"),
        ("other_literal_py", PY_PATH, "talhao-os-ficha-pivo-v2", 1, "generic-api-key"),
        ("other_literal_js", JS_PATH, "talhao-os-ficha-pivo-v2", 1, "generic-api-key"),
        ("exact_literal_other_file", "tools/prototipo/v37/gen37/outra_ficha.py", LITERAL, 1, "generic-api-key"),
        ("exact_literal_py_suffix", PY_PATH + ".bak", LITERAL, 1, "generic-api-key"),
        ("exact_literal_js_suffix", JS_PATH + ".bak", LITERAL, 1, "generic-api-key"),
        ("exact_literal_similar_dir_py", PY_PATH.replace("gen37/", "gen370/"), LITERAL, 1, "generic-api-key"),
        ("exact_literal_similar_dir_js", JS_PATH.replace("gen37/", "gen370/"), LITERAL, 1, "generic-api-key"),
        ("exact_literal_prefixed_path", "backup/" + PY_PATH, LITERAL, 1, "generic-api-key"),
        ("exact_literal_dot_not_wildcard", PY_PATH.replace(".py", "Xpy"), LITERAL, 1, "generic-api-key"),
        ("prefixed_literal_py", PY_PATH, "Q9x7-" + LITERAL, 1, "generic-api-key"),
        ("suffixed_literal_js", JS_PATH, LITERAL + "-7zW2", 1, "generic-api-key"),
        ("default_github_rule_py", PY_PATH, GITHUB_CANARY, 1, "github-pat"),
        ("default_github_rule_js", JS_PATH, GITHUB_CANARY, 1, "github-pat"),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="gitleaks-focal-", dir=output.parent) as temporary:
        directory = Path(temporary)
        for name, path, value, candidate_exit, rule in cases:
            root, introduced, head = make_fixture(directory, name, path, value)
            for config_name, config in configs.items():
                expected_exit = 1 if config_name == "base" else candidate_exit
                report = directory / (name + "--" + config_name + ".json")
                command = [binary, "git", "--no-banner", "--no-color", "--redact",
                           "--ignore-gitleaks-allow", "--gitleaks-ignore-path", root,
                           "--config", config, "--report-format", "json", "--report-path", report, root]
                process = run(command, root)
                raw_report = json.loads(report.read_text()) if report.exists() else None
                findings = [] if raw_report is None else [
                    {key: finding.get(key) for key in ("RuleID", "File", "StartLine", "Commit")}
                    for finding in raw_report]
                expected_findings = ([] if expected_exit == 0 else [
                    {"RuleID": rule, "File": path, "StartLine": 2, "Commit": introduced}])
                report_redacted = raw_report is not None and all(
                    finding.get("Secret") == "REDACTED" and value not in json.dumps(finding)
                    for finding in raw_report)
                raw_report_matches_assertions = raw_report is not None and findings == expected_findings
                replacements = {str(root): "<fixture_repo>", str(report): "<report_json>",
                                str(binary): "<gitleaks>", str(config): "<" + config_name + "_config>",
                                str(directory): "<temporary_root>"}
                results.append(sanitize({
                    "case": name, "config": config_name, "fixture_path": path,
                    "introduction_commit": introduced, "fixture_head": head,
                    "file_absent_at_head": not (root / path).exists(),
                    "expected_exit": expected_exit, "actual_exit": process.returncode,
                    "expected_findings": expected_findings, "findings": findings,
                    "raw_report": raw_report, "raw_report_sha256": sha256(report) if report.exists() else None,
                    "raw_report_matches_assertions": raw_report_matches_assertions,
                    "raw_report_redacted": report_redacted,
                    "command": [str(arg) for arg in command],
                    "stdout": process.stdout, "stderr": process.stderr,
                    "passed": process.returncode == expected_exit and raw_report_matches_assertions
                              and report_redacted and not (root / path).exists(),
                }, replacements))
    final_config_hashes = {name: sha256(path) for name, path in configs.items()}
    configs_unchanged = initial_config_hashes == final_config_hashes
    evidence = {
        "schema": "focal-gitleaks-evidence-v1",
        "scope": "Gitleaks 8.30.1; isolated local Git histories with fabricated fixture values only",
        "sanitization": "Reports use Gitleaks --redact. Only machine-specific paths in commands/logs are replaced; finding paths, rule IDs, commits, locations and outcomes are preserved.",
        "limits": ["No product repository or real credentials were scanned.",
                   "Focal config regression, not a repository security audit.",
                   "This script exercises Git history mode; CI and other invocation modes are outside its scope.",
                   "Default preservation proven by identical preexisting config plus synthetic github-pat detections."],
        "gitleaks_version": version.stdout.strip(), "binary_sha256": sha256(binary),
        "config_sha256": initial_config_hashes, "configs_unchanged_after_scans": configs_unchanged,
        "script_sha256": sha256(Path(__file__)), "config_contract": structural,
        "tests": results, "scans": len(results),
        "passed_scans": sum(test["passed"] for test in results),
        "passed": configs_unchanged and structural["passed"] and all(test["passed"] for test in results),
        "duration_seconds": round(time.monotonic() - started, 3),
        "temporary_repositories_removed": not directory.exists(),
    }
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: evidence[key] for key in
                      ("passed", "scans", "passed_scans", "duration_seconds", "temporary_repositories_removed")}))
    return evidence["passed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gitleaks", required=True, help="Gitleaks 8.30.1 executable path or command")
    parser.add_argument("--base-config", required=True, type=Path)
    parser.add_argument("--candidate-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New aggregate JSON file; parent must exist")
    args = parser.parse_args()
    located_binary = shutil.which(args.gitleaks)
    if located_binary is None:
        parser.error("Gitleaks executable not found")
    binary = Path(located_binary).resolve()
    configs = {"base": args.base_config.resolve(), "candidate": args.candidate_config.resolve()}
    output = args.output.resolve()
    if not all(path.is_file() for path in configs.values()):
        parser.error("Both configuration files must exist")
    if not output.parent.is_dir() or output.exists():
        parser.error("Output parent must exist and output file must not already exist")
    return execute(binary, configs, output)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
