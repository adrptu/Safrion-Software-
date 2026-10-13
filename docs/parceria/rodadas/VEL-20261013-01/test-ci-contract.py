"""Discovery and controlled mutations of the focal CI contract in isolated copies."""
import argparse
import hashlib
import tempfile
import json
import os
from pathlib import Path
import re
import subprocess
import sys



def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-tests', type=int, default=8)
    args = parser.parse_args()
    CONFIG = args.repository / '.gitleaks.toml'
    SOURCE = args.repository / 'tools/ci/test_gitleaks_excecoes.py'
    IGNORE = (args.repository / '.gitleaksignore').read_text()
    if args.output.exists():
        parser.error('output exists; preserve evidence and choose another path')
    config = CONFIG.read_text()
    source = SOURCE.read_bytes()
    config_hash = digest(CONFIG)
    source_hash = digest(SOURCE)
    start = config.index("# VEL-20261013-01:")
    end = config.index("# HML-SECRET-02:", start)
    block = config[start:end]

    def substitute(changed):
        return config[:start] + changed + config[end:]

    cases = [
        ("unchanged_candidate", config, 0),
        ("and_to_or", substitute(block.replace('condition = "AND"', 'condition = "OR"')), 1),
        ("literal_without_end_anchor", substitute(block.replace("^talhao-os-ficha-pivo-v1$", "^talhao-os-ficha-pivo-v1")), 1),
        ("paths_without_end_anchors", substitute(block.replace("\\.py$", "\\.py").replace("\\.js$", "\\.js")), 1),
        ("broader_path", substitute(block.replace("^tools/prototipo/v37/gen37/ficha_pivo\\.py$", "^tools/prototipo/v37/gen37/")), 1),
        ("second_literal", substitute(block.replace("regexes = ['''^talhao-os-ficha-pivo-v1$''']", "regexes = ['''^talhao-os-ficha-pivo-v1$''', '''^talhao-os-ficha-pivo-v2$''']")), 1),
        ("remove_new_block", substitute(""), 1),
        ("defaults_false", config.replace("useDefault = true", "useDefault = false"), 1),
    ]
    broad = block.replace('^talhao-os-ficha-pivo-v1$', '^talhao-os-ficha-pivo-.*$').replace(
        '^tools/prototipo/v37/gen37/ficha_pivo\\.py$', '^tools/prototipo/v37/gen37/')
    cases.extend([
        ('additional_broad_allowlist', substitute(block + broad), 1),
        ('earlier_broad_allowlist', substitute(broad + block), 1),
        ('global_allowlist', config + '\n[allowlist]\npaths = [".*"]\n', 1),
    ])
    temporary = tempfile.TemporaryDirectory(prefix='safrion-vel-contract-')
    temporary_root = Path(temporary.name)
    results = []
    for name, text, expected in cases:
        root = temporary_root / name
        (root / "tools/ci").mkdir(parents=True, exist_ok=False)
        (root / "tools/ci/test_gitleaks_excecoes.py").write_bytes(source)
        (root / ".gitleaks.toml").write_text(text)
        (root / ".gitleaksignore").write_text(IGNORE)
        command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tools/ci", "-p", "test_*.py", "-v"]
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        stdout = completed.stdout.replace(str(root), "<isolated_copy>")
        stderr = completed.stderr.replace(str(root), "<isolated_copy>")
        ran = re.search(r"Ran (\d+) tests?", stderr)
        failure_headers = re.findall(r"^(?:FAIL|ERROR): (.+)$", stderr, re.M)
        mutation_applied = (text == config) if expected == 0 else (text != config)
        no_import_or_unrelated_failure = "ERROR:" not in stderr and all("ExcecaoDaFichaDePivo" in h for h in failure_headers)
        passed = (completed.returncode == expected and ran is not None and int(ran.group(1)) == args.expected_tests
                  and mutation_applied and no_import_or_unrelated_failure
                  and (not failure_headers if expected == 0 else bool(failure_headers)))
        results.append({"case": name, "expected_exit": expected, "actual_exit": completed.returncode,
                        "tests_discovered": int(ran.group(1)) if ran else None,
                        "mutation_applied": mutation_applied,
                        "failures_scoped_to_new_class": no_import_or_unrelated_failure,
                        "failure_headers": failure_headers, "passed": passed,
                        "command": ["<python>"] + command[1:], "stdout": stdout, "stderr": stderr,
                        "config_sha256": digest(root / ".gitleaks.toml")})
    evidence = {"python": sys.version, "scope": "unittest discovery in isolated copies; no Gitleaks rescans",
                "harness_sha256": digest(Path(__file__)), "expected_tests": args.expected_tests,
                "candidate_config_sha256": config_hash, "candidate_test_sha256": source_hash,
                "candidate_unchanged": config_hash == digest(CONFIG) and source_hash == digest(SOURCE),
                "tests": results, "runs": len(results), "passed_runs": sum(r["passed"] for r in results),
                "passed": all(r["passed"] for r in results)}
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: evidence[k] for k in ("candidate_unchanged", "runs", "passed_runs", "passed")}))
    temporary.cleanup()
    return evidence["passed"] and evidence["candidate_unchanged"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
