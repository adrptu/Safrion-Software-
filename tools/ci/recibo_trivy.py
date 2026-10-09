"""Recibo sanitizado dos achados de um relatório JSON do Trivy (CI-DIAG-20261008, comentário 6070588105 do PR #46).

Diagnóstico, não portão: quem bloqueia é o exit-code do próprio Trivy. Lê o JSON que o scanner já gravou e guarda,
por achado, só o que identifica o problema sem revelar conteúdo:
- vulnerabilidade: identificador, gravidade, pacote, versão instalada e corrigida;
- segredo: regra, gravidade e linha (número inteiro);
- configuração: identificador, gravidade e estado.
Target e PkgPath entram só como caminho relativo ao repositório, sem caminho absoluto, sem ".." e sem caractere de
controle; fora disso o campo é descartado e o achado continua contado. Cada texto copiado passa por uma lista fechada
de caracteres; o que não passa vira null. Nunca copia Match, Code, Secret, Title, Message, Description,
CauseMetadata nem o JSON bruto. Relatório ausente ou inválido gera recibo dizendo isso, com achados null (nunca lista
vazia), e termina com 1.

Uso: python3 tools/ci/recibo_trivy.py <relatorio.json> <recibo.json>
"""

import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata


GRAVIDADES = {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
ESTADOS = {"PASS", "FAIL", "EXCEPTION"}
IDENTIFICADOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+-]{0,127}")
PACOTE = re.compile(r"[A-Za-z0-9@][A-Za-z0-9@._~/+:-]{0,213}")
VERSAO = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+_~:-]{0,127}")
# FixedVersion pode listar várias linhas corrigidas ("4.17.21, 5.0.1") ou faixas (">= 2.0.1").
VERSOES = re.compile(r"[A-Za-z0-9.+_~:,=<> -]{1,200}")
SECOES = (("Vulnerabilities", "vulnerabilidade"), ("Secrets", "segredo"), ("Misconfigurations", "configuracao"))


class RelatorioInvalido(ValueError):
    pass


def texto(valor, padrao):
    return valor if isinstance(valor, str) and padrao.fullmatch(valor) else None


def enumerado(valor, permitidos):
    return valor if isinstance(valor, str) and valor in permitidos else None


def caminho_relativo(valor):
    """Devolve o caminho se for relativo ao repositório e só tiver caracteres imprimíveis; senão None."""
    if not isinstance(valor, str) or not valor or len(valor) > 400:
        return None
    if any(unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp", "Cs", "Co", "Cn") for c in valor):
        return None
    if "\\" in valor or valor.startswith(("/", "~")) or re.match(r"[A-Za-z]:", valor) or "://" in valor:
        return None
    if ".." in PurePosixPath(valor).parts:
        return None
    return valor


def lista_de_achados(resultado, secao):
    itens = resultado.get(secao)
    if itens is None:
        return []
    if not isinstance(itens, list) or not all(isinstance(i, dict) for i in itens):
        raise RelatorioInvalido("SECAO_INVALIDA")
    return itens


def achado(categoria, item, alvo):
    if categoria == "vulnerabilidade":
        registro = {
            "identificador": texto(item.get("VulnerabilityID"), IDENTIFICADOR),
            "gravidade": enumerado(item.get("Severity"), GRAVIDADES),
            "pacote": texto(item.get("PkgName"), PACOTE),
            "versao_instalada": texto(item.get("InstalledVersion"), VERSAO),
            "versao_corrigida": texto(item.get("FixedVersion"), VERSOES),
        }
        caminho_pacote = item.get("PkgPath")
        if caminho_pacote not in (None, ""):
            registro["caminho_pacote"] = caminho_relativo(caminho_pacote)
    elif categoria == "segredo":
        linha = item.get("StartLine")
        registro = {
            "identificador": texto(item.get("RuleID"), IDENTIFICADOR),
            "gravidade": enumerado(item.get("Severity"), GRAVIDADES),
            "linha": linha if type(linha) is int and linha > 0 else None,
        }
    else:
        registro = {
            "identificador": texto(item.get("ID"), IDENTIFICADOR) or texto(item.get("AVDID"), IDENTIFICADOR),
            "gravidade": enumerado(item.get("Severity"), GRAVIDADES),
            "estado": enumerado(item.get("Status"), ESTADOS),
        }
    return {"categoria": categoria, **registro, "alvo": alvo}


def extrair(relatorio):
    if not isinstance(relatorio, dict) or relatorio.get("SchemaVersion") != 2:
        raise RelatorioInvalido("ESQUEMA_DESCONHECIDO")
    resultados = relatorio.get("Results")
    if not isinstance(resultados, list):
        raise RelatorioInvalido("SEM_RESULTS")
    achados = []
    for resultado in resultados:
        if not isinstance(resultado, dict):
            raise RelatorioInvalido("RESULTADO_INVALIDO")
        alvo = caminho_relativo(resultado.get("Target"))
        for secao, categoria in SECOES:
            for item in lista_de_achados(resultado, secao):
                achados.append(achado(categoria, item, alvo))
    return achados


def gerar(origem):
    recibo = {"recibo": "trivy", "commit": os.environ.get("GITHUB_SHA", "local")}
    try:
        bruto = origem.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {**recibo, "relatorio": "ausente", "motivo": "RELATORIO_AUSENTE", "achados": None}
    except (OSError, UnicodeDecodeError):
        return {**recibo, "relatorio": "invalido", "motivo": "RELATORIO_ILEGIVEL", "achados": None}
    try:
        achados = extrair(json.loads(bruto))
    except RelatorioInvalido as erro:
        return {**recibo, "relatorio": "invalido", "motivo": str(erro), "achados": None}
    except ValueError:
        return {**recibo, "relatorio": "invalido", "motivo": "JSON_INVALIDO", "achados": None}
    contagem = {}
    for a in achados:
        chave = f'{a["categoria"]}:{a["gravidade"] or "desconhecida"}'
        contagem[chave] = contagem.get(chave, 0) + 1
    return {**recibo, "relatorio": "lido", "total": len(achados), "contagem": dict(sorted(contagem.items())),
            "achados": achados}


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    recibo = gerar(Path(argv[1]))
    destino = Path(argv[2])
    destino.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(recibo, ensure_ascii=False, indent=2) + "\n"
    destino.write_text(conteudo, encoding="utf-8")
    print(json.dumps(recibo, ensure_ascii=False))
    if recibo["relatorio"] != "lido":
        print(f'Recibo do Trivy SEM achados conferidos: relatório {recibo["relatorio"]} ({recibo["motivo"]}); '
              "isto não equivale a zero achados.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
