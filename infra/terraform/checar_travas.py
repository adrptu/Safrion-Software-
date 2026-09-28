#!/usr/bin/env python3
# Travas do Cloud SQL da HML que sustentam a exceção GCP-0015 do Trivy e a decisão sobre GCP-0017
# (hml/README.md, "Achados do scanner"). Sem elas, a exceção cai. Dois modos:
#   python3 checar_travas.py [módulo]           confere o código (padrão: hml/), sem credencial; roda em PR;
#   python3 checar_travas.py --plano p.json     confere o plan (terraform show -json), com os valores resolvidos.
# Saída 0 = todas as travas presentes; 1 = alguma faltou (lista na saída); 2 = uso incorreto ou arquivo ilegível.
#
# O código é lido por um analisador léxico de HCL (comentários #, // e /* */, strings com ${...}, heredocs), não por
# expressão regular sobre o texto: comentário, string ou heredoc que contenha a trava não conta como trava.
# O guard aceita só um SUBCONJUNTO explícito de HCL e falha fechado fora dele, em vez de tentar entender todo o HCL
# (HML-TF-04): nada de arquivo de override, .tf.json ou .tofu; rótulos só com [A-Za-z0-9_-] (sem escape \u);
# blocos de topo só os que o módulo usa; nenhum bloco dynamic na instância do Cloud SQL.
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TIPO = 'google_sql_database_instance'
NOME = 'hml'
ARQUIVO = 'banco.tf'
SSL = 'ENCRYPTED_ONLY'
CONECTOR = 'REQUIRED'
TOPO_ACEITO = {'terraform', 'provider', 'resource', 'variable', 'locals', 'output'}
ROTULO = re.compile(r'[A-Za-z_][A-Za-z0-9_-]*')
# Arquivos que o Terraform (ou o OpenTofu) mescla ou lê além dos .tf comuns: fora do subconjunto.
FORA_DO_SUBCONJUNTO = ('*.tf.json', '*.tofu', '*.tofu.json', 'override.tf', '*_override.tf')
# Caminhos que o ignore_changes não pode cobrir: deixaria a trava mudar fora do Terraform sem o plan mostrar.
PROTEGIDOS = ('settings', 'ip_configuration', 'ssl_mode', 'connector_enforcement', 'authorized_networks')


class ErroHcl(Exception):
    pass


def _inicio_heredoc(fonte: str, i: int) -> bool:
    j = i + 2 + (1 if fonte[i + 2 : i + 3] == '-' else 0)
    return j < len(fonte) and (fonte[j].isalpha() or fonte[j] == '_')


@dataclass
class Token:
    tipo: str  # nome, texto (string literal sem interpolação), modelo (string com ${}), heredoc, simbolo, fim_linha
    valor: str
    linha: int


def tokens(fonte: str) -> list[Token]:
    """Analisador léxico do subconjunto de HCL nativo usado nos módulos."""
    saida: list[Token] = []
    i, n, linha = 0, len(fonte), 1
    while i < n:
        c = fonte[i]
        if c == '\n':
            saida.append(Token('fim_linha', '\n', linha))
            linha += 1
            i += 1
        elif c in ' \t\r':
            i += 1
        elif c == '#' or fonte.startswith('//', i):
            while i < n and fonte[i] != '\n':
                i += 1
        elif fonte.startswith('/*', i):
            fim = fonte.find('*/', i + 2)
            if fim < 0:
                raise ErroHcl(f'linha {linha}: comentário /* sem fechamento')
            linha += fonte.count('\n', i, fim)
            i = fim + 2
        elif c == '"':
            inicio, i, modelo, profundidade = linha, i + 1, False, 0
            partes = []
            while True:
                if i >= n or (fonte[i] == '\n' and profundidade == 0):
                    raise ErroHcl(f'linha {inicio}: string sem fechamento')
                if profundidade == 0 and fonte[i] == '"':
                    i += 1
                    break
                if fonte[i] == '\\' and i + 1 < n:
                    partes.append(fonte[i : i + 2])
                    i += 2
                    continue
                if fonte.startswith('${', i) or fonte.startswith('%{', i):
                    modelo, profundidade = True, profundidade + 1
                    partes.append(fonte[i : i + 2])
                    i += 2
                    continue
                if profundidade and fonte[i] == '{':
                    profundidade += 1
                elif profundidade and fonte[i] == '}':
                    profundidade -= 1
                if fonte[i] == '\n':
                    linha += 1
                partes.append(fonte[i])
                i += 1
            saida.append(Token('modelo' if modelo else 'texto', ''.join(partes), inicio))
        elif fonte.startswith('<<', i) and _inicio_heredoc(fonte, i):
            j = i + 2 + (1 if fonte[i + 2 : i + 3] == '-' else 0)
            k = j
            while k < n and (fonte[k].isalnum() or fonte[k] == '_'):
                k += 1
            marca = fonte[j:k]
            fim_linha = fonte.find('\n', k)
            if fim_linha < 0:
                raise ErroHcl(f'linha {linha}: heredoc sem corpo')
            p = fim_linha + 1
            inicio = linha
            while True:
                q = fonte.find('\n', p)
                atual = fonte[p : q if q >= 0 else n]
                if atual.strip() == marca:
                    break
                if q < 0:
                    raise ErroHcl(f'linha {inicio}: heredoc {marca} sem fechamento')
                p = q + 1
            linha += fonte.count('\n', i, p)
            i = p + len(atual)
            saida.append(Token('heredoc', marca, inicio))
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (fonte[j].isalnum() or fonte[j] in '_-'):
                j += 1
            saida.append(Token('nome', fonte[i:j], linha))
            i = j
        elif c.isdigit():
            j = i
            while j < n and fonte[j].isdigit():
                j += 1
            if fonte[j : j + 1] == '.' and fonte[j + 1 : j + 2].isdigit():
                j += 1
                while j < n and fonte[j].isdigit():
                    j += 1
            saida.append(Token('numero', fonte[i:j], linha))
            i = j
        else:
            dois = fonte[i : i + 2]
            if dois in ('==', '!=', '>=', '<=', '&&', '||', '=>', '...'):
                saida.append(Token('simbolo', dois, linha))
                i += 2
            else:
                saida.append(Token('simbolo', c, linha))
                i += 1
    return saida


@dataclass
class Bloco:
    tipo: str
    rotulos: list[str]
    linha: int
    atributos: dict[str, list[Token]] = field(default_factory=dict)
    blocos: list['Bloco'] = field(default_factory=list)


def analisar(fonte: str) -> Bloco:
    """Corpo HCL: atributos (nome = expressão até o fim da linha, com parênteses equilibrados) e blocos."""
    lista = tokens(fonte)
    pos = 0

    def corpo(fechar: bool) -> Bloco:
        nonlocal pos
        raiz = Bloco('', [], 0)
        while True:
            while pos < len(lista) and lista[pos].tipo == 'fim_linha':
                pos += 1
            if pos >= len(lista):
                if fechar:
                    raise ErroHcl('bloco sem "}"')
                return raiz
            t = lista[pos]
            if t.tipo == 'simbolo' and t.valor == '}':
                if not fechar:
                    raise ErroHcl(f'linha {t.linha}: "}}" sem bloco')
                pos += 1
                return raiz
            if t.tipo != 'nome':
                raise ErroHcl(f'linha {t.linha}: esperado nome, veio {t.valor!r}')
            pos += 1
            if pos < len(lista) and lista[pos].tipo == 'simbolo' and lista[pos].valor == '=':
                pos += 1
                expr, profundidade = [], 0
                while pos < len(lista):
                    x = lista[pos]
                    if x.tipo == 'fim_linha' and profundidade == 0:
                        break
                    if x.tipo == 'simbolo' and x.valor in '([{':
                        profundidade += 1
                    elif x.tipo == 'simbolo' and x.valor in ')]}':
                        if profundidade == 0:
                            break
                        profundidade -= 1
                    if x.tipo != 'fim_linha':
                        expr.append(x)
                    pos += 1
                if t.valor in raiz.atributos:
                    raise ErroHcl(f'linha {t.linha}: atributo {t.valor} repetido')
                raiz.atributos[t.valor] = expr
                continue
            rotulos = []
            while pos < len(lista) and lista[pos].tipo in ('texto', 'nome'):
                rotulos.append(lista[pos].valor)
                pos += 1
            if pos >= len(lista) or lista[pos].valor != '{':
                raise ErroHcl(f'linha {t.linha}: bloco {t.valor} sem "{{"')
            pos += 1
            filho = corpo(True)
            filho.tipo, filho.rotulos, filho.linha = t.valor, rotulos, t.linha
            raiz.blocos.append(filho)

    return corpo(False)


def literal(expr: list[Token]) -> str | None:
    """Valor de uma string literal sem interpolação; qualquer outra expressão devolve None."""
    return expr[0].valor if len(expr) == 1 and expr[0].tipo == 'texto' else None


def blocos(b: Bloco, tipo: str) -> list[Bloco]:
    return [x for x in b.blocos if x.tipo == tipo]


def todos(b: Bloco):
    yield b
    for x in b.blocos:
        yield from todos(x)


def conferir_codigo(modulo: Path) -> list[str]:
    arquivos = sorted(modulo.glob('*.tf'))
    if not arquivos:
        return [f'nenhum .tf em {modulo}']
    fora = sorted({p.name for padrao in FORA_DO_SUBCONJUNTO for p in modulo.glob(padrao)})
    if fora:
        return [f'arquivos fora do subconjunto aceito (override, JSON ou OpenTofu): {fora}']
    faltas, instancias = [], []
    for arq in arquivos:
        try:
            raiz = analisar(arq.read_text(encoding='utf-8'))
        except ErroHcl as erro:
            return [f'{arq.name}: {erro}']
        for b in raiz.blocos:
            if b.tipo not in TOPO_ACEITO:
                faltas.append(f'{arq.name}:{b.linha}: bloco de topo {b.tipo} fora do subconjunto aceito')
        for b in todos(raiz):
            for r in b.rotulos:
                if not ROTULO.fullmatch(r):
                    faltas.append(f'{arq.name}:{b.linha}: rótulo {r!r} fora do subconjunto (escape ou caractere especial)')
        for r in blocos(raiz, 'resource'):
            if r.rotulos[:1] == [TIPO]:
                instancias.append((arq.name, r))
    if faltas:
        return faltas
    # A exceção é por arquivo: nenhuma outra instância pode existir no módulo, nem no próprio banco.tf.
    if [(a, r.rotulos) for a, r in instancias] != [(ARQUIVO, [TIPO, NOME])]:
        achadas = ', '.join(f'{a}:{r.linha} {".".join(r.rotulos)}' for a, r in instancias) or 'nenhuma'
        return [f'o módulo deve ter exatamente uma {TIPO}.{NOME}, em {ARQUIVO}; achadas: {achadas}']
    recurso = instancias[0][1]
    settings = blocos(recurso, 'settings')
    if len(settings) != 1:
        return [f'settings deve aparecer uma vez; apareceu {len(settings)}']
    s = settings[0]
    if literal(s.atributos.get('connector_enforcement', [])) != CONECTOR:
        faltas.append(f'connector_enforcement = "{CONECTOR}" ausente ou não literal')
    ip = blocos(s, 'ip_configuration')
    if len(ip) != 1:
        faltas.append(f'ip_configuration deve aparecer uma vez; apareceu {len(ip)}')
    elif literal(ip[0].atributos.get('ssl_mode', [])) != SSL:
        faltas.append(f'ssl_mode = "{SSL}" ausente ou não literal')
    for b in todos(recurso):
        if b.tipo == 'dynamic':
            faltas.append(f'linha {b.linha}: bloco dynamic na instância do Cloud SQL, fora do subconjunto aceito')
        if b.tipo == 'authorized_networks':
            faltas.append(f'linha {b.linha}: authorized_networks presente; nenhuma rede autorizada é a trava')
        if 'authorized_networks' in b.atributos:
            faltas.append('authorized_networks como atributo')
    for ciclo in blocos(recurso, 'lifecycle'):
        if not _ignore_changes_seguro(ciclo.atributos.get('ignore_changes', [])):
            faltas.append('lifecycle.ignore_changes cobre uma trava (ou tem forma não reconhecida)')
    return faltas


def _ignore_changes_seguro(expr: list[Token]) -> bool:
    """Aceita só lista de referências settings[0].<campo> (ou settings.0.<campo>) com campo fora das travas.
    Qualquer outra forma (all, settings inteiro, ip_configuration, string, expressão) é recusada: falha fechado."""
    if not expr:
        return True
    valores = [(t.tipo, t.valor) for t in expr]
    if valores[0] != ('simbolo', '[') or valores[-1] != ('simbolo', ']'):
        return False
    itens, atual = [], []
    for tipo, v in valores[1:-1]:
        if (tipo, v) == ('simbolo', ','):
            itens.append(atual)
            atual = []
        else:
            atual.append((tipo, v))
    if atual:
        itens.append(atual)
    for item in itens:
        vs = [v for _, v in item]
        if vs[:5] in (['settings', '[', '0', ']', '.'],):
            campo = vs[5:]
        elif vs[:4] == ['settings', '.', '0', '.']:
            campo = vs[4:]
        else:
            return False
        if len(campo) != 1 or campo[0] in PROTEGIDOS or item[-1][0] != 'nome':
            return False
    return True


def conferir_plano(caminho: Path) -> list[str]:
    try:
        plano = json.loads(caminho.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as erro:
        return [f'plan ilegível: {erro}']
    ativas = [
        m for m in plano.get('resource_changes', [])
        if m.get('mode', 'managed') == 'managed'
        and m.get('type', m.get('address', '').split('.')[0]) == TIPO
        and m.get('change', {}).get('after') is not None
    ]
    if [m.get('address') for m in ativas] != [f'{TIPO}.{NOME}']:
        return [f'o plan deve ter exatamente {TIPO}.{NOME}; tem {[m.get("address") for m in ativas]}']
    mudanca = ativas[0]['change']
    depois, desconhecido = mudanca.get('after') or {}, mudanca.get('after_unknown') or {}
    settings = depois.get('settings') or []
    if len(settings) != 1:
        return [f'settings deve aparecer uma vez no plan; apareceu {len(settings)}']
    s = settings[0]
    s_desc = (desconhecido.get('settings') or [{}])[0] if isinstance(desconhecido.get('settings'), list) else desconhecido.get('settings')
    if s_desc is True:
        return ['settings inteiro desconhecido no plan']
    s_desc = s_desc or {}
    if not isinstance(s_desc, dict):
        return ['settings em formato inesperado no plan']
    faltas = []
    if s_desc.get('connector_enforcement') or s.get('connector_enforcement') != CONECTOR:
        faltas.append(f'connector_enforcement = {s.get("connector_enforcement")!r} (desconhecido: {bool(s_desc.get("connector_enforcement"))})')
    ip = s.get('ip_configuration') or []
    ip_desc_lista = s_desc.get('ip_configuration')
    if ip_desc_lista is True:
        return faltas + ['ip_configuration desconhecido no plan']
    if len(ip) != 1:
        return faltas + [f'ip_configuration deve aparecer uma vez no plan; apareceu {len(ip)}']
    ip_desc = (ip_desc_lista or [{}])[0] or {}
    if not isinstance(ip_desc, dict):
        return faltas + ['ip_configuration desconhecido no plan']
    if ip_desc.get('ssl_mode') or ip[0].get('ssl_mode') != SSL:
        faltas.append(f'ssl_mode = {ip[0].get("ssl_mode")!r} (desconhecido: {bool(ip_desc.get("ssl_mode"))})')
    if ip_desc.get('authorized_networks'):
        faltas.append('authorized_networks desconhecido no plan')
    elif ip[0].get('authorized_networks') not in (None, []):
        faltas.append('authorized_networks não vazio')
    return faltas


def main(argv: list[str]) -> int:
    aqui = Path(__file__).resolve().parent
    if len(argv) == 2 and argv[0] == '--plano':
        faltas = conferir_plano(Path(argv[1]))
    elif len(argv) <= 1 and not (argv and argv[0].startswith('-')):
        modulo = Path(argv[0]) if argv else aqui / 'hml'
        if not modulo.is_dir():
            print(f'Módulo inexistente: {modulo}')
            return 2
        faltas = conferir_codigo(modulo)
    else:
        print('Uso: checar_travas.py [módulo] | checar_travas.py --plano plano.json')
        return 2
    for f in faltas:
        print(f'FALTA: {f}')
    print('OK: travas do Cloud SQL presentes' if not faltas else f'{len(faltas)} trava(s) faltando')
    return 1 if faltas else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
