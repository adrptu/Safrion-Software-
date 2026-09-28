"""Confere inventário de produção do pnpm; não substitui o exit-code do Trivy.

FERR-05: o Trivy antigo lia só o primeiro documento YAML do pnpm 11+ e
terminava com sucesso sem varrer as dependências do projeto. Este smoke
test exige as dependências diretas fixadas dos manifestos do workspace.
Não certifica cobertura de transitivas, dependências de desenvolvimento
ou ausência de vulnerabilidades. Novos formatos exigem revisar o contrato.
"""

import argparse
import json
from pathlib import Path
import re
import sys


VERSAO_EXATA = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")


def ler_objeto(caminho):
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if not isinstance(dados, dict):
        raise ValueError(f"{caminho.name}: esperado objeto JSON")
    return dados


def dependencias_esperadas(raiz):
    # Estrutura contratada em AGENTS.md; não lê node_modules nem fixtures.
    manifestos = [raiz / "package.json", *sorted(raiz.glob("packages/*/package.json")),
                  *sorted(raiz.glob("apps/*/package.json"))]
    dados = [(caminho, ler_objeto(caminho)) for caminho in manifestos]
    internos = set()
    for caminho, manifesto in dados[1:]:
        nome = manifesto.get("name")
        if nome is None:
            continue
        if not isinstance(nome, str) or not nome:
            raise ValueError(f"{caminho.relative_to(raiz)}: nome interno inválido")
        if nome in internos:
            raise ValueError(f"nome interno duplicado: {nome}")
        internos.add(nome)
    esperadas = set()
    for caminho, manifesto in dados:
        for campo in ("dependencies", "optionalDependencies"):
            dependencias = manifesto.get(campo, {})
            if not isinstance(dependencias, dict):
                raise ValueError(f"{caminho.relative_to(raiz)}: {campo} inválido")
            for nome, versao in dependencias.items():
                if versao == "workspace:*":
                    if nome not in internos:
                        raise ValueError(f"{caminho.relative_to(raiz)}: pacote interno ausente: {nome}")
                    # Código local não aparece no inventário do registro. Suas
                    # dependências externas continuam examinadas neste laço.
                    continue
                if not isinstance(versao, str) or not VERSAO_EXATA.fullmatch(versao):
                    raise ValueError(f"{caminho.relative_to(raiz)}: {nome} exige versão exata; revisar contrato")
                esperadas.add((nome, versao))
    if not esperadas:
        raise ValueError("nenhuma dependência de produção declarada; revisar aplicabilidade, não aprovar vazio")
    return esperadas


def conferir(relatorio, esperadas):
    resultados = relatorio.get("Results")
    if not isinstance(resultados, list):
        raise ValueError("relatório sem Results válido")
    encontrados = set()
    alvos = 0
    for resultado in resultados:
        if not isinstance(resultado, dict):
            raise ValueError("Results contém alvo inválido")
        if (resultado.get("Target"), resultado.get("Class"), resultado.get("Type")) != (
            "pnpm-lock.yaml", "lang-pkgs", "pnpm"
        ):
            continue
        alvos += 1
        pacotes = resultado.get("Packages")
        if not isinstance(pacotes, list) or not pacotes:
            raise ValueError("pnpm-lock.yaml sem inventário; habilitar list-all-pkgs e conferir o parser")
        for pacote in pacotes:
            if not isinstance(pacote, dict) or not all(
                isinstance(pacote.get(campo), str) and pacote[campo] for campo in ("Name", "Version")
            ):
                raise ValueError("inventário contém pacote inválido")
            encontrados.add((pacote["Name"], pacote["Version"]))
    if alvos != 1:
        raise ValueError("esperado exatamente um inventário pnpm de pnpm-lock.yaml")
    faltantes = esperadas - encontrados
    if faltantes:
        raise ValueError("dependências sem cobertura: " + ", ".join(
            f"{nome}@{versao}" for nome, versao in sorted(faltantes)
        ))
    return encontrados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("relatorio", type=Path)
    parser.add_argument("raiz", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    try:
        esperadas = dependencias_esperadas(args.raiz)
        encontrados = conferir(ler_objeto(args.relatorio), esperadas)
    except (OSError, ValueError) as erro:
        print(f"FERR-05: cobertura NÃO comprovada: {erro}", file=sys.stderr)
        return 1
    print(f"Cobertura direta de produção conferida: {len(esperadas)} dependência(s); "
          f"{len(encontrados)} pacote(s) no inventário pnpm.")
    for nome, versao in sorted(esperadas):
        print(f"  {nome}@{versao}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
