#!/usr/bin/env python3
# Travas do Cloud SQL e do Cloud Run da HML que sustentam a exceção GCP-0015 do Trivy e o fechamento do GCP-0017 pelo
# desenho de rede privada (ADR 0006; hml/README.md, "Achados do scanner"). Sem elas, a exceção e o fechamento caem.
# Também: o segredo hml-vinculo-pedido sem version_destroy_ttl, num recurso literal que o job e o IAM usam, para o pedido
# destruído sumir na hora (R-006 3b e 3c).
# Dois modos:
#   python3 checar_travas.py [módulo]           confere o código (padrão: hml/), sem credencial; roda em PR;
#   python3 checar_travas.py --plano p.json     confere o plan (terraform show -json), com os valores resolvidos.
# Saída 0 = todas as travas presentes; 1 = alguma faltou (lista na saída); 2 = uso incorreto ou arquivo ilegível.
#
# O código é lido por um analisador léxico de HCL (comentários #, // e /* */, strings com ${...}), não por expressão
# regular sobre o texto: comentário ou string que contenha a trava não conta como trava.
# O guard aceita só um SUBCONJUNTO explícito de HCL e falha fechado fora dele, em vez de tentar entender todo o HCL
# (HML-TF-04): nada de arquivo de override, .tf.json ou .tofu; nenhum heredoc; dentro de ${...}, só referência, índice
# e chamada simples, sem aspas, chaves, comentário nem quebra de linha; nenhuma diretiva %{; rótulos só com
# [A-Za-z0-9_-] (sem escape \u); blocos de topo só os que o módulo usa; nenhum bloco dynamic na instância do Cloud SQL;
# no Cloud Run, só dynamic "env" e, de google_cloud_run*, só v2 service, v2 job e o IAM deles (no código e no plan).
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
DATA_API = 'DISALLOW_DATA_API'
EGRESS = 'PRIVATE_RANGES_ONLY'
SEGREDO = 'google_secret_manager_secret'
SEGREDO_IAM = 'google_secret_manager_secret_iam_member'
PEDIDO = 'hml-vinculo-pedido'
VARIAVEL_PEDIDO = 'SAFRION_PEDIDO_SEGREDO'
# IAM do pedido (R-006 §3c): exatamente estes dois vínculos, na forma escrita no hml/segredos.tf.
PAPEL_PEDIDO = 'safrionVinculoPedido'
VINCULOS_PEDIDO = {
    ((('texto', 'roles/secretmanager.secretVersionAdder'),), (('nome', 'var'), ('simbolo', '.'), ('nome', 'operador'))):
        'operador com roles/secretmanager.secretVersionAdder',
    ((('modelo', 'projects/${var.projeto_id}/roles/' + PAPEL_PEDIDO),), (('modelo', 'serviceAccount:${local.sa.preparo}'),)):
        f'sa-preparo com o papel {PAPEL_PEDIDO}',
}
# O papel customizado do bootstrap: só o que a fila usa. versions.add, versions.enable ou secrets.rotate deixariam a conta
# do job gravar pedido ou reativar versão desativada.
PERMISSOES_PEDIDO = frozenset({'secretmanager.versions.list', 'secretmanager.versions.get', 'secretmanager.versions.access',
                               'secretmanager.versions.disable', 'secretmanager.versions.destroy'})
PAPEL_CUSTOMIZADO = 'google_project_iam_custom_role'
ARQUIVO_PAPEL = 'contas.tf'
# IAM de segredo no hml: só estas formas de secret_id são conferíveis (revisão do Codex de 7d71682). Alias em local,
# parênteses ou outra expressão escondiam do guard um vínculo largo no segredo do pedido.
FORMA_BANCO = [('nome', SEGREDO), ('simbolo', '.'), ('nome', 'hml'), ('simbolo', '['), ('nome', 'each'), ('simbolo', '.'),
               ('nome', 'value'), ('simbolo', '.'), ('nome', 'segredo'), ('simbolo', ']'), ('simbolo', '.'),
               ('nome', 'secret_id')]
PAPEL_BANCO = [('texto', 'roles/secretmanager.secretAccessor')]
# IAM acima do segredo (projeto, pasta, organização) daria acesso a todos os segredos: no hml, nenhum.
IAM_ACIMA_DO_SEGREDO = ('google_project_iam', 'google_folder_iam', 'google_organization_iam')
# O wif.tf tem aspas dentro de ${...}, fora do subconjunto do analisador. Arquivo não analisável só passa se o texto não
# tiver nada de IAM de projeto, Secret Manager, papel customizado ou papel básico amplo.
NAO_ANALISAVEIS = {'wif.tf'}
PROIBIDO_SEM_ANALISE = ('google_project_iam', 'google_folder_iam', 'google_organization_iam', 'secretmanager',
                        'custom_role', PAPEL_PEDIDO.lower(), 'roles/owner', 'roles/editor')
PAPEIS_AMPLOS = ('roles/owner', 'roles/editor')
# Blocos, a partir do recurso, até o que leva o vpc_access. Todo recurso destes tipos precisa do egress privado.
CLOUD_RUN = {'google_cloud_run_v2_service': ('template',), 'google_cloud_run_v2_job': ('template', 'template')}
CLOUD_RUN_IAM = {'google_cloud_run_v2_service_iam_member', 'google_cloud_run_v2_job_iam_member'}
TOPO_ACEITO = {'terraform', 'provider', 'resource', 'variable', 'locals', 'output'}
ROTULO = re.compile(r'[A-Za-z_][A-Za-z0-9_-]*')
# Arquivos que o Terraform (ou o OpenTofu) mescla ou lê além dos .tf comuns: fora do subconjunto.
FORA_DO_SUBCONJUNTO = ('*.tf.json', '*.tofu', '*.tofu.json', 'override.tf', '*_override.tf')
# Caminhos que o ignore_changes não pode cobrir: deixaria a trava mudar fora do Terraform sem o plan mostrar.
PROTEGIDOS = ('settings', 'ip_configuration', 'ssl_mode', 'connector_enforcement', 'authorized_networks',
              'ipv4_enabled', 'private_network', 'data_api_access', 'psc_config',
              'enable_private_path_for_google_cloud_services')
# Caracteres aceitos dentro de ${...}: o que o módulo usa (var.x, local.x, recurso.atributo, índice e chamada simples).
# Aspas, chaves, comentário, diretiva ou quebra de linha ali fariam o guard e o Terraform discordarem de onde a string
# termina.
INTERPOLACAO = re.compile(r'[A-Za-z0-9_.\-\[\]() ,*]')


class ErroHcl(Exception):
    pass


@dataclass
class Token:
    tipo: str  # nome, texto (string literal sem interpolação), modelo (string com ${}), simbolo, fim_linha
    valor: str
    linha: int


def _string(fonte: str, i: int, linha: int, saida: list[Token]) -> int:
    """String entre aspas numa linha só, a partir das aspas em `i`. Devolve a posição depois do fechamento."""
    n, i, modelo, dentro = len(fonte), i + 1, False, False
    partes = []
    while True:
        if i >= n or fonte[i] == '\n':
            raise ErroHcl(f'linha {linha}: string sem fechamento ou com quebra de linha')
        c = fonte[i]
        if dentro:
            if c == '}':
                dentro = False
            elif not INTERPOLACAO.fullmatch(c):
                raise ErroHcl(f'linha {linha}: {c!r} dentro de ${{...}}, fora do subconjunto aceito')
            partes.append(c)
            i += 1
            continue
        if c == '"':
            saida.append(Token('modelo' if modelo else 'texto', ''.join(partes), linha))
            return i + 1
        if c == '\\':
            if i + 1 >= n or fonte[i + 1] == '\n':
                raise ErroHcl(f'linha {linha}: escape sem caractere')
            partes.append(fonte[i : i + 2])
            i += 2
        elif fonte.startswith('$${', i) or fonte.startswith('%%{', i):
            # Escapes do HCL: o texto "${" ou "%{" em si, sem abrir interpolação.
            partes.append(fonte[i : i + 3])
            i += 3
        elif fonte.startswith('%{', i):
            raise ErroHcl(f'linha {linha}: diretiva %{{ fora do subconjunto aceito')
        elif fonte.startswith('${', i):
            modelo, dentro = True, True
            partes.append('${')
            i += 2
        else:
            partes.append(c)
            i += 1


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
            i = _string(fonte, i, linha, saida)
        elif fonte.startswith('<<', i):
            # O módulo não usa heredoc, e o marcador do HCL aceita formas (hífen, sufixo) que o guard leria diferente.
            raise ErroHcl(f'linha {linha}: heredoc fora do subconjunto aceito')
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


def falso_literal(expr: list[Token]) -> bool:
    """Só o booleano false sem aspas: "false", variável ou expressão não contam (o Trivy lê o não resolvido como true)."""
    return [(t.tipo, t.valor) for t in expr] == [('nome', 'false')]


def caminho(item: list[tuple[str, str]]) -> list[str] | None:
    """Nomes de uma referência nome(.nome | [n] | .n)*, sem os índices; outra forma (string, splat, função) dá None."""
    if not item or item[0][0] != 'nome':
        return None
    nomes, i = [item[0][1]], 1
    while i < len(item):
        if item[i] == ('simbolo', '.') and i + 1 < len(item) and item[i + 1][0] in ('nome', 'numero'):
            if item[i + 1][0] == 'nome':
                nomes.append(item[i + 1][1])
            i += 2
        elif item[i] == ('simbolo', '[') and i + 2 < len(item) and item[i + 1][0] == 'numero' and item[i + 2] == ('simbolo', ']'):
            i += 3
        else:
            return None
    return nomes


def referencia(expr: list[Token]) -> bool:
    """Referência a variável, local ou atributo (var.x, local.x, tipo.nome.atributo): nada de literal, null ou função."""
    nomes = caminho([(t.tipo, t.valor) for t in expr])
    return nomes is not None and len(nomes) >= 2 and nomes[0] not in ('null', 'true', 'false')


def itens_da_lista(expr: list[Token]) -> list[list[tuple[str, str]]] | None:
    """Itens de uma lista [a, b, ...] em tokens; outra forma (all, string, expressão) dá None."""
    valores = [(t.tipo, t.valor) for t in expr]
    if len(valores) < 2 or valores[0] != ('simbolo', '[') or valores[-1] != ('simbolo', ']'):
        return None
    itens, atual = [], []
    for par in valores[1:-1]:
        if par == ('simbolo', ','):
            itens.append(atual)
            atual = []
        else:
            atual.append(par)
    if atual:
        itens.append(atual)
    return itens


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
    faltas, instancias, cloud_run, pedidos, iam_segredos, lexicos = [], [], [], [], [], []
    for arq in arquivos:
        try:
            fonte = arq.read_text(encoding='utf-8')
            raiz = analisar(fonte)
        except ErroHcl as erro:
            return [f'{arq.name}: {erro}']
        lexicos.append((arq.name, tokens(fonte)))
        for b in raiz.blocos:
            if b.tipo not in TOPO_ACEITO:
                faltas.append(f'{arq.name}:{b.linha}: bloco de topo {b.tipo} fora do subconjunto aceito')
        for b in todos(raiz):
            for r in b.rotulos:
                if not ROTULO.fullmatch(r):
                    faltas.append(f'{arq.name}:{b.linha}: rótulo {r!r} fora do subconjunto (escape ou caractere especial)')
        for r in blocos(raiz, 'resource'):
            tipo = r.rotulos[0] if r.rotulos else ''
            if tipo == TIPO:
                instancias.append((arq.name, r))
            elif tipo in CLOUD_RUN:
                cloud_run.append((arq.name, r))
            elif tipo == SEGREDO and literal(r.atributos.get('secret_id', [])) == PEDIDO:
                pedidos.append((arq.name, r))
            elif tipo.startswith(SEGREDO + '_iam'):
                iam_segredos.append((arq.name, r))
            elif tipo.startswith(IAM_ACIMA_DO_SEGREDO):
                faltas.append(f'{arq.name}:{r.linha} {".".join(r.rotulos)}: IAM de projeto, pasta ou organização no hml; '
                              'fica no bootstrap, onde é conferido')
            elif tipo.startswith('google_cloud_run') and tipo not in CLOUD_RUN_IAM:
                faltas.append(f'{arq.name}:{r.linha}: {tipo} fora do subconjunto aceito (Cloud Run só v2 service, v2 job e IAM)')
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
    else:
        if literal(ip[0].atributos.get('ssl_mode', [])) != SSL:
            faltas.append(f'ssl_mode = "{SSL}" ausente ou não literal')
        if not falso_literal(ip[0].atributos.get('ipv4_enabled', [])):
            faltas.append('ipv4_enabled = false ausente ou não literal; sem ele, o IP público volta (GCP-0017)')
        if not referencia(ip[0].atributos.get('private_network', [])):
            faltas.append('private_network ausente ou fora da forma de referência (var.x, local.x, recurso.atributo)')
    for b in todos(recurso):
        if b.tipo == 'dynamic':
            faltas.append(f'linha {b.linha}: bloco dynamic na instância do Cloud SQL, fora do subconjunto aceito')
        if b.tipo == 'authorized_networks':
            faltas.append(f'linha {b.linha}: authorized_networks presente; nenhuma rede autorizada é a trava')
        if 'authorized_networks' in b.atributos:
            faltas.append('authorized_networks como atributo')
        if b.tipo == 'data_api_access' or ('data_api_access' in b.atributos and literal(b.atributos['data_api_access']) != DATA_API):
            faltas.append(f'linha {b.linha}: data_api_access diferente de "{DATA_API}" literal; o ExecuteSql abriria o banco pela internet')
        # Private Service Connect abriria a instância a outro projeto, e o caminho privado a serviços do Google, a eles:
        # o desenho é só a conexão PSA da VPC do bootstrap (ADR 0006).
        if b.tipo == 'psc_config' or 'psc_config' in b.atributos:
            faltas.append(f'linha {b.linha}: psc_config presente; o acesso é só pela conexão PSA da VPC')
        caminho_google = 'enable_private_path_for_google_cloud_services'
        if b.tipo == caminho_google or (caminho_google in b.atributos and not falso_literal(b.atributos[caminho_google])):
            faltas.append(f'linha {b.linha}: {caminho_google} diferente de ausente ou false literal')
    for ciclo in blocos(recurso, 'lifecycle'):
        if not _ignore_changes_seguro(ciclo.atributos.get('ignore_changes', [])):
            faltas.append('lifecycle.ignore_changes cobre uma trava (ou tem forma não reconhecida)')
    for arq, r in cloud_run:
        faltas += _conferir_cloud_run(arq, r)
    return faltas + _conferir_pedido(pedidos, iam_segredos, lexicos)


def _conferir_pedido(pedidos: list[tuple[str, Bloco]], iam_segredos: list[tuple[str, Bloco]],
                     lexicos: list[tuple[str, list[Token]]]) -> list[str]:
    """O hml-vinculo-pedido guarda pedidos de uso único com o código de referência. Com version_destroy_ttl, destruir só
    desativaria a versão, que seguiria legível por dias (R-006 3b). O nome precisa ser literal num único recurso: em
    for_each ou variável, o código não o resolve (o plan confere o valor resolvido).
    O recurso literal só vale se é ele que o job e o IAM usam: sem count nem for_each, o nome em nenhuma outra string do
    módulo e SAFRION_PEDIDO_SEGREDO e o IAM do pedido como referência a ele. Sem isso, uma isca com count = 0 passava e
    o segredo real vinha de local.segredos, com TTL (revisão de 28/09). Nome ou chave montados por função (join, format)
    não são reconhecidos: ficam para a revisão do diff, e o plan confere o TTL de todo segredo resolvido com esse nome."""
    if len(pedidos) != 1:
        achados = ', '.join(f'{a}:{r.linha} {".".join(r.rotulos)}' for a, r in pedidos) or 'nenhum'
        return [f'o módulo deve ter exatamente um {SEGREDO} com secret_id = "{PEDIDO}" literal; achados: {achados}']
    arq, r = pedidos[0]
    nome = f'{arq}:{r.linha} {".".join(r.rotulos)}'
    rotulo = r.rotulos[1] if len(r.rotulos) > 1 else ''
    faltas = []
    if any('version_destroy_ttl' in b.atributos or b.tipo == 'version_destroy_ttl' for b in todos(r)):
        faltas.append(f'{nome}: version_destroy_ttl presente; o pedido destruído tem de sumir na hora')
    for ciclo in blocos(r, 'lifecycle'):
        if not _ignore_changes_fora_de(ciclo.atributos.get('ignore_changes', []), ['version_destroy_ttl']):
            faltas.append(f'{nome}: lifecycle.ignore_changes cobre o version_destroy_ttl (ou tem forma não reconhecida)')
    for meta in ('count', 'for_each'):
        if meta in r.atributos:
            faltas.append(f'{nome}: {meta} no recurso do pedido; ele existe sempre, uma vez')
    # O nome só no secret_id do recurso: em local.segredos ou num id escrito à mão, o código não sabe qual TTL vale.
    strings = [(a, t) for a, lista in lexicos for t in lista if t.tipo in ('texto', 'modelo')]
    outras = [f'{a}:{t.linha}' for a, t in strings if 'vinculo-pedido' in t.valor.lower()]
    outras.remove(f'{arq}:{r.atributos["secret_id"][0].linha}')
    if outras:
        faltas.append(f'"{PEDIDO}" em string fora do secret_id de {nome}: {outras}')
    # O job lê o segredo de SAFRION_PEDIDO_SEGREDO: uma declaração só, chave = id do próprio recurso.
    esperado = [('nome', SEGREDO), ('simbolo', '.'), ('nome', rotulo), ('simbolo', '.'), ('nome', 'id')]
    declaracoes = [(a, t, _valor_atribuido(lista, i)) for a, lista in lexicos
                   for i, t in enumerate(lista) if (t.tipo, t.valor) == ('nome', VARIAVEL_PEDIDO)]
    citacoes = [f'{a}:{t.linha}' for a, t in strings if VARIAVEL_PEDIDO.lower() in t.valor.lower()]
    if citacoes:
        faltas.append(f'{VARIAVEL_PEDIDO} em string ({citacoes}); só a forma chave = referência é reconhecida')
    if len(declaracoes) != 1 or declaracoes[0][2] != esperado:
        achadas = ', '.join(f'{a}:{t.linha}' for a, t, _ in declaracoes) or 'nenhuma'
        faltas.append(f'{VARIAVEL_PEDIDO} deve aparecer uma vez, como {SEGREDO}.{rotulo}.id; achadas: {achadas}')
    # IAM do pedido: o que aponta para o recurso usa o próprio recurso, e são exatamente os dois vínculos do desenho,
    # explícitos: operador só grava versão; a sa-preparo tem o papel customizado, sem secretAccessor nem
    # secretVersionManager (revisão do Codex de 8537b81). _iam_binding e _iam_policy trocariam a lista inteira.
    # Todo IAM de segredo do módulo passa por aqui, não só o que parece ser do pedido: secret_id fora das formas
    # conhecidas falha, em vez de ser ignorado (revisão do Codex de 7d71682).
    do_pedido = 0
    achados: dict[tuple, int] = {}
    for a, b in iam_segredos:
        ref = [(t.tipo, t.valor) for t in b.atributos.get('secret_id', [])]
        onde = f'{a}:{b.linha} {".".join(b.rotulos)}'
        if ref == FORMA_BANCO:
            if b.rotulos[0] != SEGREDO_IAM:
                faltas.append(f'{onde}: {b.rotulos[0]} em segredo do banco; só {SEGREDO_IAM}')
            elif [(t.tipo, t.valor) for t in b.atributos.get('role', [])] != PAPEL_BANCO:
                faltas.append(f'{onde}: segredo do banco com papel diferente de "{PAPEL_BANCO[0][1]}"')
            continue
        if ref[:3] != [('nome', SEGREDO), ('simbolo', '.'), ('nome', rotulo)]:
            faltas.append(f'{onde}: secret_id fora das formas conferíveis ({SEGREDO}.hml[each.value.segredo].secret_id '
                          f'ou {SEGREDO}.{rotulo}.secret_id); alias, parênteses ou outra expressão não são reconhecidos')
            continue
        do_pedido += 1
        if ref[3:] not in ([('simbolo', '.'), ('nome', 'secret_id')], [('simbolo', '.'), ('nome', 'id')]):
            faltas.append(f'{onde}: secret_id fora da forma {SEGREDO}.{rotulo}.secret_id')
        if b.rotulos[0] != SEGREDO_IAM:
            faltas.append(f'{onde}: {b.rotulos[0]} no pedido; só {SEGREDO_IAM}')
            continue
        for meta in ('count', 'for_each'):
            if meta in b.atributos:
                faltas.append(f'{onde}: {meta} no IAM do pedido; os vínculos são explícitos')
        par = tuple(tuple((t.tipo, t.valor) for t in b.atributos.get(c, [])) for c in ('role', 'member'))
        if par in VINCULOS_PEDIDO:
            achados[par] = achados.get(par, 0) + 1
        else:
            faltas.append(f'{onde}: papel ou membro fora do desenho no IAM do pedido')
    if not do_pedido:
        faltas.append(f'nenhum {SEGREDO_IAM} com secret_id = {SEGREDO}.{rotulo}.secret_id')
    for par, descricao in VINCULOS_PEDIDO.items():
        if achados.get(par, 0) != 1:
            faltas.append(f'IAM do pedido: {descricao} deve aparecer exatamente uma vez; apareceu {achados.get(par, 0)}')
    return faltas


def conferir_bootstrap(modulo: Path) -> list[str]:
    """Papel customizado da fila (R-006 §3c) e IAM de projeto do bootstrap, falhando fechado fora das formas conhecidas
    (revisão do Codex de 7d71682):
    - um só google_project_iam_custom_role "safrionVinculoPedido", em contas.tf, com as 5 permissões literais, e nenhuma
      referência a ele (comentários não contam: a leitura é por tokens);
    - Secret Manager só em papel customizado (permissões) e no nome da API; papel básico amplo (owner, editor) em
      nenhum lugar;
    - IAM de projeto só como google_project_iam_member, com papel literal, each.value de um local só com papéis
      literais ou referência a outro papel customizado sem acesso a versões de segredo;
    - arquivo fora do subconjunto do analisador (NAO_ANALISAVEIS) só passa sem nenhum desses assuntos no texto."""
    arquivos = sorted(modulo.glob('*.tf'))
    if not arquivos:
        return [f'nenhum .tf em {modulo}']
    fora = sorted({p.name for padrao in FORA_DO_SUBCONJUNTO for p in modulo.glob(padrao)})
    if fora:
        return [f'arquivos fora do subconjunto aceito (override, JSON ou OpenTofu): {fora}']
    faltas, raizes, lexicos = [], {}, []
    for arq in arquivos:
        texto = arq.read_text(encoding='utf-8')
        try:
            raizes[arq.name] = analisar(texto)
            lexicos.append((arq.name, tokens(texto)))
        except ErroHcl as erro:
            if arq.name not in NAO_ANALISAVEIS:
                return [f'{arq.name}: {erro}']
            achados = [p for p in PROIBIDO_SEM_ANALISE if p in texto.lower()]
            if achados:
                faltas.append(f'{arq.name}: fora do subconjunto do analisador e com {achados} no texto; IAM de projeto e '
                              'papéis só em arquivo conferível')
    if ARQUIVO_PAPEL not in raizes:
        return faltas + [f'{ARQUIVO_PAPEL} ausente ou fora do subconjunto do analisador']
    recursos = [(a, r) for a, raiz in raizes.items() for r in blocos(raiz, 'resource')]
    customizados = {r.rotulos[1]: (a, r) for a, r in recursos if len(r.rotulos) > 1 and r.rotulos[0] == PAPEL_CUSTOMIZADO}
    papeis = [(a, r) for a, r in customizados.values() if literal(r.atributos.get('role_id', [])) == PAPEL_PEDIDO]
    if [a for a, _ in papeis] != [ARQUIVO_PAPEL]:
        achados = ', '.join(f'{a}:{r.linha} {".".join(r.rotulos)}' for a, r in papeis) or 'nenhum'
        return faltas + [f'{ARQUIVO_PAPEL} deve ter exatamente um {PAPEL_CUSTOMIZADO} com role_id = "{PAPEL_PEDIDO}"; '
                         f'achados: {achados}']
    _, r = papeis[0]
    nome = f'{ARQUIVO_PAPEL}:{r.linha} {".".join(r.rotulos)}'
    rotulo = r.rotulos[1]
    for meta in ('count', 'for_each'):
        if meta in r.atributos:
            faltas.append(f'{nome}: {meta} no papel da fila')
    textos = _lista_literal(r.atributos.get('permissions', []))
    if textos is None:
        faltas.append(f'{nome}: permissions fora da forma de lista de strings literais')
    elif len(textos) != len(set(textos)) or set(textos) != PERMISSOES_PEDIDO:
        a_mais = sorted(set(textos) - PERMISSOES_PEDIDO)
        a_menos = sorted(PERMISSOES_PEDIDO - set(textos))
        faltas.append(f'{nome}: permissions diferente do conjunto da fila (a mais: {a_mais}; faltando: {a_menos}; '
                      f'repetidas: {len(textos) - len(set(textos))})')
    for ciclo in blocos(r, 'lifecycle'):
        if not _ignore_changes_fora_de(ciclo.atributos.get('ignore_changes', []), ['permissions']):
            faltas.append(f'{nome}: lifecycle.ignore_changes cobre permissions (ou tem forma não reconhecida)')
    # Tokens: comentário não esconde referência nem conta como menção.
    permitidos = {(a, t.linha, t.valor) for a, c in customizados.values() for t in c.atributos.get('permissions', [])
                  if t.tipo == 'texto'}
    mencoes = 0
    for a, lista in lexicos:
        # Quebra de linha dentro de parênteses é HCL válido: não separa uma referência.
        lista = [t for t in lista if t.tipo != 'fim_linha']
        for i, t in enumerate(lista):
            if t.tipo in ('texto', 'modelo'):
                baixo = t.valor.lower()
                mencoes += PAPEL_PEDIDO.lower() in baixo
                if 'secretmanager' in baixo and baixo != 'secretmanager.googleapis.com' and (a, t.linha, t.valor) not in permitidos:
                    faltas.append(f'{a}:{t.linha}: Secret Manager fora de papel customizado ({t.valor!r}); papel de '
                                  'segredo só no próprio segredo, pelo hml')
                if any(p in baixo for p in PAPEIS_AMPLOS):
                    faltas.append(f'{a}:{t.linha}: papel básico amplo ({t.valor!r}); dá acesso aos segredos')
            elif ((t.tipo, t.valor) == ('nome', PAPEL_CUSTOMIZADO) and i + 2 < len(lista)
                  and (lista[i + 1].tipo, lista[i + 1].valor) == ('simbolo', '.') and lista[i + 2].valor == rotulo):
                faltas.append(f'{a}:{t.linha}: o papel da fila é usado no bootstrap; ele só se vincula no segredo do '
                              'pedido, pelo hml')
    if mencoes != 1:
        faltas.append(f'"{PAPEL_PEDIDO}" aparece {mencoes} vezes no bootstrap; só no role_id do papel')
    locais = {k: v for raiz in raizes.values() for b in blocos(raiz, 'locals') for k, v in b.atributos.items()}
    for a, v in recursos:
        tipo = v.rotulos[0]
        if not tipo.startswith(IAM_ACIMA_DO_SEGREDO) or tipo == PAPEL_CUSTOMIZADO:
            continue
        onde = f'{a}:{v.linha} {".".join(v.rotulos)}'
        if tipo != 'google_project_iam_member':
            faltas.append(f'{onde}: {tipo} fora do subconjunto; IAM de projeto só como google_project_iam_member')
            continue
        erro = _papel_de_projeto(v, locais, customizados, rotulo)
        if erro:
            faltas.append(f'{onde}: {erro}')
    return faltas


def _lista_literal(expr: list[Token]) -> list[str] | None:
    """Os valores de uma lista só de strings literais ([ "a", "b", ]); outra forma dá None."""
    expr = [t for t in expr if t.tipo != 'fim_linha']
    estrutura = [(t.tipo, t.valor) for t in expr if t.tipo != 'texto']
    if (not expr or (expr[0].tipo, expr[0].valor) != ('simbolo', '[') or (expr[-1].tipo, expr[-1].valor) != ('simbolo', ']')
            or any(x not in (('simbolo', '['), ('simbolo', ']'), ('simbolo', ',')) for x in estrutura)):
        return None
    return [t.valor for t in expr if t.tipo == 'texto']


def _papel_de_projeto(v: Bloco, locais: dict[str, list[Token]], customizados: dict, rotulo_pedido: str) -> str | None:
    """None se o papel de um google_project_iam_member está numa forma conferível; senão, o motivo."""
    papel = [(t.tipo, t.valor) for t in v.atributos.get('role', []) if t.tipo != 'fim_linha']
    if len(papel) == 1 and papel[0][0] == 'texto':
        return None
    if papel == [('nome', 'each'), ('simbolo', '.'), ('nome', 'value')]:
        origem = [(t.tipo, t.valor) for t in v.atributos.get('for_each', []) if t.tipo != 'fim_linha']
        if len(origem) != 3 or origem[:2] != [('nome', 'local'), ('simbolo', '.')] or origem[2][1] not in locais:
            return 'papel each.value com for_each fora da forma local.<nome>'
        valor = [t for t in locais[origem[2][1]] if t.tipo != 'fim_linha']
        # Só strings literais "roles/…"; referência só como condição (var.x ? … : …), que não produz papel.
        for i, t in enumerate(valor):
            if t.tipo == 'modelo' or (t.tipo == 'texto' and not t.valor.startswith('roles/')):
                return f'local.{origem[2][1]} com valor que não é papel literal ({t.valor!r})'
            if t.tipo == 'nome' and t.valor in ('var', 'local', 'data', 'module'):
                seguinte = valor[i + 3] if i + 3 < len(valor) else None
                if not (seguinte and (seguinte.tipo, seguinte.valor) == ('simbolo', '?')):
                    return f'local.{origem[2][1]} com referência que pode produzir papel ({t.valor}.…)'
        return None
    if (len(papel) == 5 and papel[:2] == [('nome', PAPEL_CUSTOMIZADO), ('simbolo', '.')]
            and papel[3] == ('simbolo', '.') and papel[4] in (('nome', 'name'), ('nome', 'id'))):
        alvo = papel[2][1]
        if alvo == rotulo_pedido or alvo not in customizados:
            return f'papel customizado {alvo} não conferível aqui'
        permissoes = _lista_literal(customizados[alvo][1].atributos.get('permissions', []))
        if permissoes is None or any(p.startswith('secretmanager.versions.') for p in permissoes):
            return f'papel customizado {alvo} com acesso a versões de segredo ou fora da forma literal'
        return None
    return 'papel fora das formas conferíveis (literal, each.value de local literal ou papel customizado)'

def _valor_atribuido(lista: list[Token], i: int) -> list[tuple[str, str]] | None:
    """Tokens do valor de `nome =` na posição i, até o fim da linha, a vírgula ou o fecho do mapa; None sem o `=`."""
    if i + 1 >= len(lista) or (lista[i + 1].tipo, lista[i + 1].valor) != ('simbolo', '='):
        return None
    valor, profundidade = [], 0
    for t in lista[i + 2:]:
        if t.tipo == 'fim_linha' and profundidade == 0:
            break
        if t.tipo == 'simbolo' and t.valor in '([{':
            profundidade += 1
        elif t.tipo == 'simbolo' and t.valor in ')]}':
            if profundidade == 0:
                break
            profundidade -= 1
        elif t.tipo == 'simbolo' and t.valor == ',' and profundidade == 0:
            break
        valor.append((t.tipo, t.valor))
    return valor


def _conferir_cloud_run(arq: str, r: Bloco) -> list[str]:
    """Web e jobs saem pela VPC só para destinos privados: vpc_access único com egress literal PRIVATE_RANGES_ONLY e
    network_interfaces (Direct VPC, sem conector), sem ignore_changes que esconda o vpc_access."""
    nome = f'{arq}:{r.linha} {".".join(r.rotulos)}'
    faltas = [f'{nome}: dynamic {b.rotulos} fora do subconjunto aceito (só dynamic "env")'
              for b in todos(r) if b.tipo == 'dynamic' and b.rotulos != ['env']]
    alvo = r
    for passo in CLOUD_RUN[r.rotulos[0]]:
        filhos = blocos(alvo, passo)
        if len(filhos) != 1:
            return faltas + [f'{nome}: {passo} deve aparecer uma vez; apareceu {len(filhos)}']
        alvo = filhos[0]
    vpc = blocos(alvo, 'vpc_access')
    if len(vpc) != 1:
        faltas.append(f'{nome}: vpc_access deve aparecer uma vez; apareceu {len(vpc)}')
    else:
        if literal(vpc[0].atributos.get('egress', [])) != EGRESS:
            faltas.append(f'{nome}: egress = "{EGRESS}" ausente ou não literal')
        if 'connector' in vpc[0].atributos:
            faltas.append(f'{nome}: connector no vpc_access; o desenho é Direct VPC (network_interfaces)')
        interfaces = blocos(vpc[0], 'network_interfaces')
        if len(interfaces) != 1:
            faltas.append(f'{nome}: network_interfaces deve aparecer uma vez no vpc_access')
        elif not _interface_utilizavel(interfaces[0]):
            faltas.append(f'{nome}: network_interfaces sem network nem subnetwork em forma aceita '
                          '(referência ou texto não vazio)')
    protegido = [*CLOUD_RUN[r.rotulos[0]], 'vpc_access']
    for ciclo in blocos(r, 'lifecycle'):
        if not _ignore_changes_fora_de(ciclo.atributos.get('ignore_changes', []), protegido):
            faltas.append(f'{nome}: lifecycle.ignore_changes cobre o vpc_access (ou tem forma não reconhecida)')
    return faltas


def _interface_utilizavel(b: Bloco) -> bool:
    """O Direct VPC exige network ou subnetwork (doc do provider 8.3.0, cloud_run_v2_service, network_interfaces); cada
    um que aparece é referência ou texto não vazio. Bloco vazio, null, "" ou função: recusado (HML-TF-05)."""
    campos = [b.atributos[c] for c in ('network', 'subnetwork') if c in b.atributos]
    return bool(campos) and all(referencia(e) or bool((literal(e) or '').strip()) for e in campos)


def _ignore_changes_fora_de(expr: list[Token], protegido: list[str]) -> bool:
    """Aceita só lista de referências que não sejam prefixo do caminho protegido nem entrem nele (índices ignorados).
    all, string, splat ou expressão: recusado (falha fechado)."""
    if not expr:
        return True
    itens = itens_da_lista(expr)
    if itens is None:
        return False
    for item in itens:
        nomes = caminho(item)
        if nomes is None or nomes[0] == 'all':
            return False
        n = min(len(nomes), len(protegido))
        if nomes[:n] == protegido[:n]:
            return False
    return True


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
    if ip_desc.get('ipv4_enabled') or ip[0].get('ipv4_enabled') is not False:
        faltas.append(f'ipv4_enabled = {ip[0].get("ipv4_enabled")!r} (desconhecido: {bool(ip_desc.get("ipv4_enabled"))})')
    rede = ip[0].get('private_network')
    if ip_desc.get('private_network') or not isinstance(rede, str) or not rede.strip():
        faltas.append(f'private_network ausente, vazio ou desconhecido (desconhecido: {bool(ip_desc.get("private_network"))})')
    if s_desc.get('data_api_access') or s.get('data_api_access') not in (None, DATA_API):
        faltas.append(f'data_api_access = {s.get("data_api_access")!r} (desconhecido: {bool(s_desc.get("data_api_access"))})')
    psc = ip[0].get('psc_config')
    if ip_desc.get('psc_config') or not (psc in (None, []) or (
            isinstance(psc, list) and all(isinstance(x, dict) and x.get('psc_enabled') is False for x in psc))):
        faltas.append(f'psc_config ligado ou desconhecido (desconhecido: {bool(ip_desc.get("psc_config"))})')
    caminho_google = 'enable_private_path_for_google_cloud_services'
    if ip_desc.get(caminho_google) or ip[0].get(caminho_google) not in (None, False):
        faltas.append(f'{caminho_google} = {ip[0].get(caminho_google)!r} (desconhecido: {bool(ip_desc.get(caminho_google))})')
    return faltas + _plano_cloud_run(plano) + _plano_pedido(plano)


def _plano_cloud_run(plano: dict) -> list[str]:
    """No plan, todo Cloud Run v2 criado ou mantido tem vpc_access conhecido, com egress PRIVATE_RANGES_ONLY e uma
    network_interfaces. Outro google_cloud_run* (v1, worker pool) fica fora do subconjunto, como no código."""
    faltas = []
    for m in plano.get('resource_changes', []):
        tipo = m.get('type', m.get('address', '').split('.')[0])
        mudanca = m.get('change') or {}
        if m.get('mode', 'managed') != 'managed' or mudanca.get('after') is None:
            continue
        endereco = m.get('address')
        if tipo.startswith('google_cloud_run') and tipo not in CLOUD_RUN and tipo not in CLOUD_RUN_IAM:
            faltas.append(f'{endereco}: {tipo} fora do subconjunto aceito (Cloud Run só v2 service, v2 job e IAM)')
            continue
        if tipo not in CLOUD_RUN:
            continue
        valor, desc = mudanca['after'], mudanca.get('after_unknown') or {}
        for passo in [*CLOUD_RUN[tipo], 'vpc_access']:
            lista = valor.get(passo) if isinstance(valor, dict) else None
            lista_desc = desc.get(passo) if isinstance(desc, dict) else None
            if lista_desc is True or not isinstance(lista, list) or len(lista) != 1:
                faltas.append(f'{endereco}: {passo} ausente, repetido ou desconhecido no plan')
                break
            valor = lista[0]
            desc = lista_desc[0] if isinstance(lista_desc, list) and lista_desc else {}
            if not isinstance(valor, dict) or not isinstance(desc, dict):
                faltas.append(f'{endereco}: {passo} desconhecido no plan')
                break
        else:
            if desc.get('egress') or valor.get('egress') != EGRESS:
                faltas.append(f'{endereco}: egress = {valor.get("egress")!r} (desconhecido: {bool(desc.get("egress"))})')
            interfaces = valor.get('network_interfaces')
            desc_interfaces = desc.get('network_interfaces')
            if desc_interfaces is True or not isinstance(interfaces, list) or len(interfaces) != 1:
                faltas.append(f'{endereco}: network_interfaces ausente, repetido ou desconhecido no plan')
            else:
                faltas += _interface_do_plano(endereco, interfaces[0], desc_interfaces)
    return faltas


def _interface_do_plano(endereco: str, interface: object, desc: object) -> list[str]:
    """No plan, network ou subnetwork resolvido e não vazio, e nenhum dos dois desconhecido: o código dá os dois, e um
    valor que só se resolve no apply não é conferível aqui (falha fechado, HML-TF-05)."""
    d = desc[0] if isinstance(desc, list) and desc else {}
    if d is True or not isinstance(interface, dict) or not isinstance(d, dict):
        return [f'{endereco}: network_interfaces desconhecida no plan']
    desconhecidos = [c for c in ('network', 'subnetwork') if d.get(c)]
    validos = [c for c in ('network', 'subnetwork') if isinstance(interface.get(c), str) and interface[c].strip()]
    if desconhecidos or not validos:
        return [f'{endereco}: network_interfaces sem network nem subnetwork resolvido e não vazio '
                f'(desconhecidos: {desconhecidos})']
    return []


def _plano_pedido(plano: dict) -> list[str]:
    """No plan, todo segredo resolvido como hml-vinculo-pedido tem version_destroy_ttl nulo (ou vazio) e conhecido. Pega o
    nome vindo de for_each ou variável, que o código não resolve; secret_id desconhecido falha fechado."""
    faltas = []
    for m in plano.get('resource_changes', []):
        mudanca = m.get('change') or {}
        tipo = m.get('type', m.get('address', '').split('.')[0])
        if m.get('mode', 'managed') != 'managed' or tipo != SEGREDO or mudanca.get('after') is None:
            continue
        endereco, valor, desc = m.get('address'), mudanca['after'], mudanca.get('after_unknown') or {}
        if not isinstance(valor, dict) or not isinstance(desc, dict) or desc.get('secret_id'):
            faltas.append(f'{endereco}: secret_id desconhecido ou em formato inesperado no plan')
        elif valor.get('secret_id') == PEDIDO and (desc.get('version_destroy_ttl') or valor.get('version_destroy_ttl') not in (None, '')):
            faltas.append(f'{endereco}: version_destroy_ttl = {valor.get("version_destroy_ttl")!r} '
                          f'(desconhecido: {bool(desc.get("version_destroy_ttl"))})')
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
        if not argv:
            faltas += conferir_bootstrap(aqui / 'bootstrap')
    else:
        print('Uso: checar_travas.py [módulo] | checar_travas.py --plano plano.json')
        return 2
    for f in faltas:
        print(f'FALTA: {f}')
    print('OK: travas do Cloud SQL, do Cloud Run e do pedido de vínculo presentes' if not faltas
          else f'{len(faltas)} trava(s) faltando')
    return 1 if faltas else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
