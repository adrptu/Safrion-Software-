"""Semgrep local: fixtures nativas e varredura com inventário obrigatório (FERR-06).

Não interpreta regras nem substitui o scanner. Falha em análise parcial, achado ou
ausência de prova. Sem conta, regras remotas, upload ou alterações no produto.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

VERSION = "1.178.0"
RULES = {"safrion-tls-verification-disabled", "safrion-request-in-sql"}
EXTENSIONS = {".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"}


def targets(root):
    files = sorted({p.relative_to(root).as_posix()
                    for area in ("packages", "apps")
                    for package in (root / area).glob("*") if package.is_dir()
                    for p in [*package.glob("*"), *(package / "src").rglob("*")]
                    if p.is_file() and p.suffix in EXTENSIONS})
    if not files:
        raise ValueError("nenhum arquivo de aplicação no escopo")
    return files


def check_fixtures(report):
    for key in ("config_missing_tests", "config_with_errors"):
        if report.get(key) != []:
            raise ValueError("fixture ausente ou configuração inválida")
    results = report.get("results")
    if not isinstance(results, dict) or len(results) != 1:
        raise ValueError("relatório de fixtures vazio ou inesperado")
    checks = next(iter(results.values())).get("checks", {})
    if set(checks) != RULES:
        raise ValueError("regras sem prova nativa")
    for check in checks.values():
        if check.get("passed") is not True or check.get("errors") != []:
            raise ValueError("positivo/negativo não passou")
        matches = check.get("matches", {})
        if not matches or any(not m.get("expected_lines") or
                              m.get("expected_lines") != m.get("reported_lines")
                              for m in matches.values()):
            raise ValueError("prova sem detecção esperada")


def check_scan(report, expected):
    if report.get("version") != VERSION:
        raise ValueError("versão inesperada do scanner")
    if report.get("errors") != []:
        raise ValueError("análise parcial ou erro do scanner")
    if report.get("skipped_rules") != [] or report.get("time", {}).get("fixpoint_timeouts") != []:
        raise ValueError("regra ignorada ou análise interrompida")
    if report.get("results") != []:
        raise ValueError("achado de segurança ou resultado ausente")
    scanned = report.get("paths", {}).get("scanned", [])
    if not expected or not isinstance(scanned, list) or set(scanned) != set(expected):
        raise ValueError("inventário analisado não corresponde aos arquivos esperados")


def run(binary, args, root, env, output):
    result = subprocess.run([binary, *args], cwd=root, env=env, capture_output=True,
                            text=True, timeout=180, check=False)
    output.write_text(result.stdout, encoding="utf-8")
    output.with_suffix(".log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise ValueError(f"scanner recusou {output.stem}: saída {result.returncode}")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--semgrep", default="semgrep")
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        expected = targets(root)
        with tempfile.TemporaryDirectory(prefix="safrion-semgrep-") as temporary:
            state = Path(temporary)
            output = args.report_dir.resolve() if args.report_dir else state
            output.mkdir(parents=True, exist_ok=True)
            env = {**os.environ, "XDG_CONFIG_HOME": str(state),
                   "SEMGREP_SEND_METRICS": "off", "SEMGREP_ENABLE_VERSION_CHECK": "0",
                   "SEMGREP_SETTINGS_FILE": str(state / "settings.yml"),
                   "SEMGREP_LOG_FILE": str(state / "semgrep.log")}
            common = ["--config", ".semgrep/safrion.yml", "--metrics=off",
                      "--disable-version-check", "--disable-nosem", "--json", "--jobs", "2"]
            fixtures = run(args.semgrep, ["--test", *common, ".semgrep/safrion.ts"],
                           root, env, output / "fixtures.json")
            check_fixtures(fixtures)
            scan = run(args.semgrep, ["scan", *common, "--strict", "--error", "--no-git-ignore",
                                     *expected], root, env, output / "scan.json")
            check_scan(scan, expected)
            print(f"FERR-06: {len(RULES)} regras com fixtures; {len(expected)} alvos JS/TS de src e raiz dos pacotes sem achados.")
        return 0
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        # Não imprimir relatório bruto: um achado pode conter código privado.
        print(f"FERR-06: falha ({type(error).__name__}): {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
