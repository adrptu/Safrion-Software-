"""Recusa verde vazio/parcial do Playwright e publica só resultado, nunca logs/traces/cookies."""
import json
import os
from pathlib import Path
import re
import sys


MINIMOS = {"desktop": 12, "celular": 1}
# Provas nomeadas que não podem sumir, mesmo que outra jornada mantenha a contagem: o ID abre o título ("HML-ISO-01: …").
OBRIGATORIAS = {"desktop": ("HML-ISO-01", "HML-ISO-02", "HML-ISO-03")}
ID_DO_TITULO = re.compile(r"^([A-Z]+(?:-[A-Z]+)*-\d{2}): ")


def conferir(relatorio):
    if relatorio["errors"] != []:
        raise ValueError("ERRO_GLOBAL")
    testes = []
    ids = set()

    def visitar(suites):
        if not isinstance(suites, list):
            raise ValueError("SUITES_INVALIDAS")
        for suite in suites:
            for spec in suite["specs"]:
                if spec["ok"] is not True or not spec["tests"]:
                    raise ValueError("CASO_INCOMPLETO")
                for teste in spec["tests"]:
                    chave = (spec["id"], teste["projectName"])
                    if chave in ids or not all(isinstance(x, str) and x for x in chave):
                        raise ValueError("IDENTIDADE_INVALIDA")
                    ids.add(chave)
                    resultados = teste["results"]
                    if (teste["expectedStatus"] != "passed" or teste["status"] != "expected"
                            or len(resultados) != 1 or resultados[0]["status"] != "passed"
                            or resultados[0]["retry"] != 0 or resultados[0]["errors"] != []):
                        raise ValueError("TESTE_NAO_APROVADO")
                    testes.append({"projeto": chave[1], "teste": spec["title"], "resultado": "passou"})
            visitar(suite.get("suites", []))

    visitar(relatorio["suites"])
    stats = relatorio["stats"]
    for campo, esperado in {"expected": len(testes), "unexpected": 0, "flaky": 0, "skipped": 0}.items():
        if type(stats[campo]) is not int or stats[campo] != esperado:
            raise ValueError("TOTAIS_INCONSISTENTES")
    if any(sum(t["projeto"] == p for t in testes) < minimo for p, minimo in MINIMOS.items()):
        raise ValueError("JORNADAS_INCOMPLETAS")
    for projeto, ids in OBRIGATORIAS.items():
        presentes = {m.group(1) for t in testes if t["projeto"] == projeto and (m := ID_DO_TITULO.match(t["teste"]))}
        if not set(ids) <= presentes:
            raise ValueError("PROVA_OBRIGATORIA_AUSENTE")
    return {"aprovado": True, "quantidade": len(testes), "testes": testes}


def main():
    destino = Path(sys.argv[2])
    recibo = {"aprovado": False, "commit": os.environ.get("GITHUB_SHA", "local")}
    try:
        recibo.update(conferir(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        recibo["motivo"] = "EVIDENCIA_E2E_INCOMPLETA_OU_REPROVADA"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(recibo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(recibo, ensure_ascii=False))
    return 0 if recibo["aprovado"] else 1


if __name__ == "__main__":
    sys.exit(main())
