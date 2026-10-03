#!/usr/bin/env python3
"""Processa os arquivos abertos do AGROFIT (MAPA) e das monografias (ANVISA)
em arquivos JSON compactos para a Consulta Agrofit (AG-07) do protótipo.

Só biblioteca padrão. Lê os CSVs em fluxo (uma linha por vez) e escreve em
<saida>/ (padrão: dados_agrofit/site/):

  agrofit_meta.json                 fontes, cabeçalhos HTTP, contagens, data, formato
  agrofit_indice.json               dicionários + 1 registro compacto por produto formulado
  agrofit_usos_cultura_<n>.json     usos agrupados por cultura (cultura -> alvo -> produtos)
  agrofit_usos_produto_<n>.json     usos agrupados por produto (produto -> cultura -> alvos)
  agrofit_lmr.json                  LMR vigente da ANVISA por monografia x cultura
  agrofit_tecnicos.json             produtos técnicos (matéria-prima registrada)

Uso:  python3 processar.py [--raw DIR] [--saida DIR]
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAW_PADRAO = os.environ.get('AGROFIT_RAW') or os.path.normpath(os.path.join(AQUI, '..', '..', '..', 'agrofit_raw'))
SAIDA_PADRAO = os.path.join(AQUI, 'site')
FORMATO = 1                      # sobe quando o formato dos arquivos mudar
PRODUTOS_POR_ARQUIVO = 500       # fatia dos usos por produto
ALVO_BYTES_CULTURA = 300_000     # tamanho-alvo de cada fatia de usos por cultura
LIMITE_ARQUIVO = 5 * 1024 * 1024

FONTES = {
    'formulados': {
        'arquivo': 'agrofitprodutosformulados.csv',
        'url': 'https://dados.agricultura.gov.br/dataset/6c913699-e82e-4da3-a0a1-fb6c431e367f/resource/d30b30d7-e256-484e-9ab8-cd40974e1238/download/agrofitprodutosformulados.csv',
        'pagina': 'https://dados.agricultura.gov.br/dataset/sistema-de-agrotoxicos-fitossanitarios-agrofit',
        'orgao': 'MAPA - AGROFIT (dados abertos)',
        'licenca': 'CC-BY',
        'headers_legado': 'form.headers',
        'codificacao': 'utf-8',
    },
    'tecnicos': {
        'arquivo': 'agrofitprodutostecnicos.csv',
        'url': 'https://dados.agricultura.gov.br/dataset/6c913699-e82e-4da3-a0a1-fb6c431e367f/resource/a200c70b-e025-4a9a-be1b-ec7275d7921f/download/agrofitprodutostecnicos.csv',
        'pagina': 'https://dados.agricultura.gov.br/dataset/sistema-de-agrotoxicos-fitossanitarios-agrofit',
        'orgao': 'MAPA - AGROFIT (dados abertos)',
        'licenca': 'CC-BY',
        'headers_legado': 'tec.headers',
        'codificacao': 'utf-8',
    },
    'monografias': {
        'arquivo': 'TA_MONOGRAFIA_AGROTOXICO.csv',
        'url': 'https://dados.anvisa.gov.br/dados/TA_MONOGRAFIA_AGROTOXICO.csv',
        'pagina': 'https://dados.gov.br/dados/conjuntos-dados/monografias-de-agrotoxicos',
        'orgao': 'ANVISA - Monografias de agrotóxicos (dados abertos)',
        'licenca': 'dados abertos (conferir termos no portal)',
        'headers_legado': 'mono.headers',
        'codificacao': 'cp1252',
    },
}

COLUNAS_FORMULADOS = ['NR_REGISTRO', 'MARCA_COMERCIAL', 'FORMULACAO', 'INGREDIENTE_ATIVO', 'TITULAR_DE_REGISTRO',
                      'CLASSE', 'MODO_DE_ACAO', 'CULTURA', 'PRAGA_NOME_CIENTIFICO', 'PRAGA_NOME_COMUM',
                      'EMPRESA_PAIS_TIPO', 'CLASSE_TOXICOLOGICA', 'CLASSE_AMBIENTAL', 'ORGANICOS', 'SITUACAO']


# ----------------------------------------------------------------------------- texto

def c1(s):
    """Corrige caracteres de controle C1 (\x80-\x9f) vindos de cp1252 lido como latin-1, e o SUB (\x1a)."""
    if not s:
        return s
    if any('\x80' <= ch <= '\x9f' or ch == '\x1a' for ch in s):
        out = []
        for ch in s:
            if '\x80' <= ch <= '\x9f':
                try:
                    out.append(bytes([ord(ch)]).decode('cp1252'))
                except UnicodeDecodeError:
                    out.append(' ')
            elif ch == '\x1a':
                out.append('–')
            else:
                out.append(ch)
        s = ''.join(out)
    return s


def limpa(s):
    return re.sub(r'\s+', ' ', c1(s or '')).strip()


def chave(s):
    """Chave de comparação: minúsculas, sem acento, hífens e espaços colapsados."""
    s = unicodedata.normalize('NFKD', limpa(s).lower())
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'[\s\-]+', ' ', s).strip()


def esqueleto(s):
    """Grafia aproximada para casar nomes em inglês/português (benzovindiflupyr ~ benzovindiflupir)."""
    palavras = []
    for w in re.split(r'[\s,]+', chave(s)):
        if not w:
            continue
        w = w.replace('ph', 'f').replace('y', 'i').replace('k', 'c').replace('w', 'v').replace('z', 's')
        w = re.sub(r's+', 's', w)
        w = re.sub(r'(ico|ica)$', '', w)
        w = re.sub(r'[aeo]$', '', w)
        w = re.sub(r'[mn](?=[^aeiou]|$)', 'n', w)
        palavras.append(w)
    return ' '.join(palavras)


def chave_modo(s):
    return re.sub(r'\s*([/;,])\s*', r'\1', chave(s)).strip(' .;,')


def mais_frequente(contador):
    return sorted(contador.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def frase(s):
    s = limpa(s)
    return s[:1].upper() + s[1:].lower() if s else s


# ----------------------------------------------------------------------------- ingredientes

def separa_topo(s, sep='+'):
    partes, prof, atual = [], 0, []
    for ch in s:
        if ch == '(':
            prof += 1
        elif ch == ')':
            prof = max(0, prof - 1)
        if ch == sep and prof == 0:
            partes.append(''.join(atual))
            atual = []
        else:
            atual.append(ch)
    partes.append(''.join(atual))
    return [limpa(p) for p in partes if limpa(p)]


def grupos_finais(s, n=2):
    """Retira até n grupos entre parênteses do fim: 'x (grupo) (480 g/L)' -> ('x', ['grupo', '480 g/L'])."""
    grupos = []
    s = s.strip()
    while s.endswith(')') and len(grupos) < n:
        prof, j = 0, len(s) - 1
        while j >= 0:
            if s[j] == ')':
                prof += 1
            elif s[j] == '(':
                prof -= 1
                if prof == 0:
                    break
            j -= 1
        if j < 0:
            break
        grupos.insert(0, s[j + 1:-1].strip())
        s = s[:j].strip()
    return s, grupos


def concentracao(txt):
    m = re.match(r'^\s*([\d.,]*\d|\.\d+)\s*(.*)$', txt or '')
    if not m:
        return None, limpa(txt)
    num = m.group(1)
    if ',' in num and '.' not in num:
        num = num.replace(',', '.')
    try:
        v = float(num)
    except ValueError:
        return None, limpa(txt)
    if v == int(v):
        v = int(v)
    return v, limpa(m.group(2))


def parse_ingredientes(texto):
    """'a (grupo) (480 g/L) + b (grupo) (1 g/kg)' -> [(nome, grupo, valor, unidade)]"""
    out = []
    for comp in separa_topo(texto):
        nome, g = grupos_finais(comp, 2)
        grupo, conc = '', ''
        if len(g) == 2:
            grupo, conc = g
        elif len(g) == 1:
            if re.match(r'^\s*[\d.,]', g[0]):
                conc = g[0]
            else:
                grupo = g[0]
        valor, unidade = concentracao(conc) if conc else (None, '')
        out.append((limpa(nome), limpa(grupo), valor, unidade))
    return out


# ----------------------------------------------------------------------------- classificações

TOX = [  # (padrão em chave(), código, rótulo curto, faixa da bula)
    (r'^categoria 1', '1', 'Categoria 1 – Extremamente tóxico', 'vermelha'),
    (r'^categoria 2', '2', 'Categoria 2 – Altamente tóxico', 'vermelha'),
    (r'^categoria 3', '3', 'Categoria 3 – Moderadamente tóxico', 'amarela'),
    (r'^categoria 4', '4', 'Categoria 4 – Pouco tóxico', 'azul'),
    (r'^categoria 5', '5', 'Categoria 5 – Improvável de causar dano agudo', 'azul'),
    (r'^nao classificado', 'NC', 'Não classificado', 'verde'),
    (r'^extremamente toxico', 'I', 'Classe I – Extremamente tóxico (classificação anterior)', 'vermelha'),
    (r'^altamente toxico', 'II', 'Classe II – Altamente tóxico (classificação anterior)', 'amarela'),
    (r'^medianamente toxico', 'III', 'Classe III – Medianamente tóxico (classificação anterior)', 'azul'),
    (r'^pouco toxico', 'IV', 'Classe IV – Pouco tóxico (classificação anterior)', 'verde'),
    (r'^nao determinado', 'ND', 'Não determinado (natureza do produto)', ''),
    (r'^baixa exposicao', 'BE', 'Baixa exposição – uso restrito em armadilhas', ''),
]
AMB = [
    (r'altamente perigoso', 'I', 'Classe I – Altamente perigoso ao meio ambiente'),
    (r'muito perigoso', 'II', 'Classe II – Muito perigoso ao meio ambiente'),
    (r'pouco perigoso', 'IV', 'Classe IV – Pouco perigoso ao meio ambiente'),
    (r'baixo risco', 'BR', 'Baixo risco ao meio ambiente'),
    (r'perigoso', 'III', 'Classe III – Perigoso ao meio ambiente'),
]
ORGANICOS = {'SIM': 'S', 'NAO': 'N', 'NÃO': 'N', 'OUTROS': 'O'}

FAMILIAS = [  # ordem importa: primeiro que casar
    ('herbicida', 'Herbicida'), ('fungicida', 'Fungicida'), ('bactericida', 'Bactericida'),
    ('acaricida', 'Acaricida'), ('nematicida', 'Nematicida'), ('cupinicida', 'Cupinicida'),
    ('formicida', 'Formicida'), ('moluscicida', 'Moluscicida'), ('inseticida', 'Inseticida'),
    ('regulador', 'Regulador de crescimento'), ('feromonio', 'Feromônio/semioquímico'),
    ('semioquimico', 'Feromônio/semioquímico'), ('ativador', 'Ativador de planta'),
    ('protetor de sementes', 'Protetor de sementes'), ('agente biologico', 'Agente biológico de controle'),
]
TIPO_ALVO = {'Herbicida': 'D', 'Fungicida': 'O', 'Bactericida': 'O', 'Inseticida': 'P', 'Acaricida': 'P',
             'Nematicida': 'P', 'Cupinicida': 'P', 'Formicida': 'P', 'Moluscicida': 'P'}

MODO_TYPOS = [('sitemic', 'sistemic'), ('sistemitc', 'sistemic'), ('sistemcio', 'sistemico'),
              ('sistemco', 'sistemico'), ('seeltiv', 'seletiv'), ('seletvo', 'seletivo'), ('seletico', 'seletivo'),
              ('acaonao', 'acao nao'), ('transmilar', 'translaminar'), ('tanslaminar', 'translaminar'),
              ('mesosistemic', 'mesostemic'), ('herbecida', 'herbicida'), ('fumegante', 'fumigante'),
              ('cresimento', 'crescimento'), ('endoarasit', 'endoparasit'), ('endorasit', 'endoparasit')]
MODO_TAGS = [  # (regex sobre texto normalizado, rótulo, remove o trecho após casar)
    (r'nao sistemic\w*', 'Não sistêmico', True),
    (r'mesostemic\w*', 'Mesostêmico', True),
    (r'sistemic\w*|sistemica', 'Sistêmico', True),
    (r'nao seletiv\w*', 'Não seletivo', True),
    (r'seletiv\w*\s*(/\s*)?condicional', 'Seletivo condicional', True),
    (r'seletiv\w*', 'Seletivo', True),
    (r'contato', 'Contato', False),
    (r'ingest', 'Ingestão', False),
    (r'translaminar', 'Translaminar', False),
    (r'profundidade', 'Profundidade', False),
    (r'\btotal\b', 'Total', False),
    (r'protet|protetiv|preventiv', 'Protetor', False),
    (r'curativ', 'Curativo', False),
    (r'erradicant', 'Erradicante', False),
    (r'fumiga', 'Fumigante', False),
    (r'residual', 'Residual', False),
    (r'pre e pos', 'Pré-emergência', False),
    (r'pre e pos', 'Pós-emergência', False),
    (r'pre emergen', 'Pré-emergência', False),
    (r'pos emergen', 'Pós-emergência', False),
    (r'repelen', 'Repelente', False),
    (r'antialimentar|bloqueador .*alimenta', 'Antialimentar', False),
    (r'fisiologic', 'Fisiológico', False),
    (r'quitina', 'Inibidor da síntese de quitina', False),
    (r'ecdise', 'Acelerador de ecdise', False),
    (r'dessecante|desfolhante', 'Dessecante/desfolhante', False),
    (r'biologic|microbiol|parasit|predad|inimigo natural|inseto esteril', 'Controle biológico', False),
    (r'atra[cit]|feromon|confusao sexual', 'Atração/feromônio', False),
    (r'competicao|antibiose|inducao de resistencia|metabolic', 'Competição/antibiose', False),
    (r'regulador|etileno|estimulante', 'Regulador de crescimento', False),
]


def classifica(tabela, texto):
    k = chave(texto)
    for item in tabela:
        if re.search(item[0], k):
            return item[1:]
    return None


def tags_modo(texto):
    k = chave(texto).replace('-', ' ')
    for a, b in MODO_TYPOS:
        k = k.replace(a, b)
    tags = []
    for padrao, rotulo, remove in MODO_TAGS:
        if re.search(padrao, k):
            if rotulo not in tags:
                tags.append(rotulo)
            if remove:
                k = re.sub(padrao, ' ', k)
    return tags


def familia_classe(componente):
    k = chave(componente)
    for padrao, fam in FAMILIAS:
        if padrao in k:
            return fam
    return 'Outros'


# ----------------------------------------------------------------------------- culturas x ANVISA

CULTURA_CORRECAO = {  # grafia exibida -> só correções evidentes; o nome oficial fica em "oficial"
    'pessego': 'Pêssego', 'lupulo': 'Lúpulo', 'salvia': 'Sálvia', 'eucalipito ogm': 'Eucalipto OGM',
}
CULTURA_ANVISA_ALIAS = {
    'pastagens': 'pastagem', 'kiwi': 'quiui', 'uva de mesa': 'uva', 'arroz irrigado': 'arroz',
    'arroz sequeiro': 'arroz', 'arroz armazenado': 'arroz', 'milho armazenado': 'milho',
    'trigo armazenado': 'trigo', 'cevada armazenado': 'cevada', 'farinha de trigo armazenada': 'trigo (farinha)',
    'tomate rasteiro industrial': 'tomate (rasteiro)', 'tomate industrial': 'tomate (rasteiro)',
    'tomate envarado': 'tomate', 'mandioquinha salsa': 'mandioquinha salsa / batata baroa',
    'batata salsa': 'mandioquinha salsa / batata baroa', 'alho porro': 'alho poro', 'pinhao manso': 'pinhao manso',
    'trigo mourisco': 'trigo mourisco', 'aveia branca': 'aveia', 'limao': 'citros', 'atemoia': 'anonaceas',
    'cherimoia': 'anonaceas', 'fruta de conde': 'anonaceas', 'pinha': 'anonaceas', 'araticum': 'anonaceas',
    'oliveira': 'azeitona', 'erva mate': 'erva mate',
}
CULTURAS_ESPECIAIS = {'todas as culturas', 'nao atrelado a cultura', 'tratamento de solo', ''}

INGREDIENTE_ANVISA_ALIAS = {
    'diquate': 'dibrometo de diquate', 'paraquate': 'dicloreto de paraquate',
    'oxicloreto de cobre': 'compostos a base de cobre', 'hidroxido de cobre': 'compostos a base de cobre',
    'oxido cuproso': 'compostos a base de cobre', 'sulfato de cobre': 'compostos a base de cobre',
    'carbonato de cobre': 'compostos a base de cobre', 'sulfato de cobre tribasico': 'compostos a base de cobre',
    'fosfeto de aluminio': 'fosfina', 'fosfeto de magnesio': 'fosfina',
    'cloreto de benzalconio': 'cloretos de benzalconio', 'oleo de neem': 'azadiractina',
    'azadiracti na a': 'azadiractina', 'azadiracti na b': 'azadiractina', 'fosfito de potassio': 'fosfonato de potassio',
}


# ----------------------------------------------------------------------------- utilidades de arquivo

def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def le_headers(raw, nome_fonte):
    """Lê estado_fontes.json (gravado por atualizar.py) ou o arquivo .headers do download original."""
    info = {}
    estado = os.path.join(raw, 'estado_fontes.json')
    if os.path.exists(estado):
        try:
            with open(estado, encoding='utf-8') as f:
                e = json.load(f).get(nome_fonte) or {}
            info.update({k: e.get(k) for k in ('etag', 'last_modified', 'baixado_em', 'verificado_em') if e.get(k)})
        except (OSError, ValueError):
            pass
    leg = os.path.join(raw, FONTES[nome_fonte]['headers_legado'])
    if not info.get('etag') and os.path.exists(leg):
        with open(leg, encoding='latin-1') as f:
            for linha in f:
                if ':' in linha:
                    k, v = linha.split(':', 1)
                    k = k.strip().lower()
                    if k == 'etag':
                        info['etag'] = v.strip()
                    elif k == 'last-modified':
                        info['last_modified'] = v.strip()
                    elif k == 'date':
                        info.setdefault('baixado_em', v.strip())
    return info


def escreve_json(caminho, obj):
    tmp = caminho + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, caminho)
    return os.path.getsize(caminho)


def agora_local():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
    except Exception:
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))


# ----------------------------------------------------------------------------- formulados

def processa_formulados(caminho):
    prod = collections.OrderedDict()   # registro -> dados do produto (1ª linha)
    usos = collections.defaultdict(set)  # registro -> {(cultura_k, alvo_k)}
    culturas_raw = collections.Counter()
    culturas_grafia = collections.defaultdict(collections.Counter)
    alvos_raw = set()
    alvos_grafia = collections.defaultdict(collections.Counter)
    alvos_comum = collections.defaultdict(collections.Counter)  # alvo_k -> chave(comum) -> n
    comum_grafia = collections.defaultdict(collections.Counter)  # chave(comum) -> grafia -> n
    cache_cult = {}
    cache_alvo = {}
    cache_comum = {}
    linhas = 0
    linhas_por_registro = collections.Counter()
    divergencias = collections.Counter()

    with open(caminho, encoding='utf-8', newline='') as f:
        r = csv.reader(f, delimiter=';')
        cab = [c.strip().lstrip('﻿') for c in next(r)]
        if cab != COLUNAS_FORMULADOS:
            raise SystemExit('Cabeçalho inesperado em %s: %s' % (caminho, cab))
        for row in r:
            if not row:
                continue
            if len(row) != len(COLUNAS_FORMULADOS):
                raise SystemExit('Linha %d com %d colunas' % (linhas + 2, len(row)))
            linhas += 1
            reg = row[0].strip()
            linhas_por_registro[reg] += 1
            if reg not in prod:
                prod[reg] = (row[1], row[2], row[3], row[4], row[5], row[6], row[11], row[12], row[13], row[14])
            elif prod[reg] != (row[1], row[2], row[3], row[4], row[5], row[6], row[11], row[12], row[13], row[14]):
                divergencias[reg] += 1
            cult = row[7]
            culturas_raw[cult] += 1
            cc = cache_cult.get(cult)
            if cc is None:
                cc = cache_cult[cult] = (chave(cult) if cult else '', limpa(cult))
            ck = cc[0]
            culturas_grafia[ck][cc[1]] += 1
            sci, com = row[8], row[9]
            alvos_raw.add(sci)
            ca = cache_alvo.get(sci)
            if ca is None:
                s_ = limpa(sci)
                if s_.startswith('(') and ')' not in s_:
                    s_ = s_[1:].strip()
                ca = cache_alvo[sci] = (chave(s_), s_)
            ak = ca[0]
            alvos_grafia[ak][ca[1]] += 1
            nomes = cache_comum.get(com)
            if nomes is None:
                nomes = []
                for n in c1(com).split(';'):
                    n = re.sub(r'\s*\(\d+\)', '', n)
                    n = limpa(n).strip(' .,-')
                    if n and n != '-' and chave(n) != ak:
                        nomes.append((chave(n), n))
                cache_comum[com] = nomes
            for nk, n in nomes:
                alvos_comum[ak][nk] += 1
                comum_grafia[nk][n] += 1
            usos[reg].add((ck, ak))
    return dict(prod=prod, usos=usos, culturas_raw=culturas_raw, culturas_grafia=culturas_grafia,
                alvos_raw=alvos_raw, alvos_grafia=alvos_grafia, alvos_comum=alvos_comum, comum_grafia=comum_grafia,
                linhas=linhas, linhas_por_registro=linhas_por_registro, divergencias=divergencias)


# ----------------------------------------------------------------------------- monografias (ANVISA)

def data_mdy(s):
    s = (s or '').strip()
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s.split(' ')[0], '%m/%d/%Y').date()
    except ValueError:
        return None


def processa_monografias(caminho, hoje):
    mono = {}          # código -> {nome, cas, culturas: {cultura_k: (nome, registro vigente)}}
    culturas_citadas = {}
    atos = {}
    contagem = collections.Counter()
    with open(caminho, encoding='cp1252', newline='') as f:
        r = csv.reader(f, delimiter=';')
        cab = [c.strip() for c in next(r)]
        I = {c: i for i, c in enumerate(cab)}
        for row in r:
            if len(row) != len(cab):
                contagem['linhas_invalidas'] += 1
                continue
            contagem['linhas'] += 1
            cod = row[I['CO_MONOGRAFIA']].strip()
            nome = limpa(row[I['DS_INGREDIENTE_ATIVO']]) or limpa(row[I['NO_SUBSTANCIA']])
            if nome.isupper():
                nome = nome.lower()
            cultura = limpa(row[I['NO_CULTURA']])
            if not cod and nome:  # definição de resíduo de grupo (ex.: ditiocarbamatos) vem sem código
                cod = '~' + chave(nome)
            if not cod or not cultura:
                contagem['sem_codigo_ou_cultura'] += 1
                continue
            m = mono.setdefault(cod, {'nome': nome, 'cas': limpa(row[I['NU_CAS']]), 'culturas': {}, 'nomes': set()})
            m['nomes'].add(nome)
            culturas_citadas.setdefault(chave(cultura), cultura)
            ini, fim = data_mdy(row[I['DT_INICIO_VIGENCIA']]), data_mdy(row[I['DT_FIM_VIGENCIA']])
            if fim and fim < hoje:
                contagem['expiradas'] += 1
                continue
            if ini and ini > hoje:
                contagem['futuras'] += 1
                continue
            tipo_txt = chave(row[I['TIPO_LIMITE']])
            tipo = 'M' if 'maximo' in tipo_txt else 'T' if 'toleranc' in tipo_txt else 'N' if 'nao estab' in tipo_txt else ''
            try:
                lmr = float(row[I['NU_LMR']].replace(',', '.'))
                lmr = float('%.6g' % lmr)
            except ValueError:
                lmr = None
            if tipo == 'N':
                lmr = None
            ato = limpa(row[I['DS_ATO_LEGAL']])
            ato_id = atos.setdefault(ato, len(atos))
            aut = 1 if chave(row[I['ST_AUTORIZADO']]) == 'sim' else 0
            reg = [lmr, tipo, aut, ato_id, ini.isoformat() if ini else None]
            ck = chave(cultura)
            atual = m['culturas'].get(ck)
            if atual is None or (reg[4] or '') > (atual[1][4] or ''):
                if atual is not None:
                    contagem['substituidas_por_mais_recente'] += 1
                m['culturas'][ck] = (cultura, reg)
            else:
                contagem['duplicadas_ou_mais_antigas'] += 1
            contagem['vigentes_lidas'] += 1
    return mono, [a for a, _ in sorted(atos.items(), key=lambda kv: kv[1])], contagem, culturas_citadas


def casador_anvisa(mono):
    por_chave = {}
    for cod, m in mono.items():
        for n in sorted(m['nomes'] | {m['nome']}):
            por_chave.setdefault(chave(n), cod)
    por_esq = {}
    for k, cod in por_chave.items():
        por_esq.setdefault(esqueleto(k), cod)

    def casa(nome):
        k = chave(nome)
        if k in por_chave:
            return por_chave[k], 'exato'
        if k in INGREDIENTE_ANVISA_ALIAS and INGREDIENTE_ANVISA_ALIAS[k] in por_chave:
            return por_chave[INGREDIENTE_ANVISA_ALIAS[k]], 'sinonimo'
        melhor = None
        for mk in por_chave:  # sal/éster: monografia é prefixo do nome (glifosato-sal de ... -> glifosato)
            if k.startswith(mk + ' ') or k.startswith(mk + ','):
                if melhor is None or len(mk) > len(melhor):
                    melhor = mk
        if melhor:
            return por_chave[melhor], 'sal_ester'
        e = esqueleto(k)
        if e in por_esq:
            return por_esq[e], 'grafia'
        cand = [ek for ek in por_esq if e.startswith(ek + ' ')]
        if cand:
            return por_esq[max(cand, key=len)], 'grafia_sal'
        cand = [cod for ek, cod in por_esq.items() if ek.startswith(e + ' ')]
        if len(cand) == 1:
            return cand[0], 'grafia_prefixo'
        return None, None
    return casa


# ----------------------------------------------------------------------------- técnicos

def processa_tecnicos(caminho, ing_idx_por_chave):
    out, titulares, classes = [], {}, {}
    with open(caminho, encoding='utf-8', newline='') as f:
        r = csv.reader(f, delimiter=';')
        next(r)
        for row in r:
            if len(row) < 8:
                continue
            ings = []
            for nome, grupo, valor, unidade in parse_ingredientes(c1(row[2])):
                idx = ing_idx_por_chave.get(chave(nome))
                ings.append([idx if idx is not None else nome, valor, unidade])
            t = titulares.setdefault(limpa(row[4]), len(titulares))
            c = classes.setdefault(limpa(row[3]), len(classes))
            out.append([limpa(row[0]), limpa(row[1]), ings, c, t, limpa(row[6]), limpa(row[7])])
    out.sort(key=lambda x: chave(x[1]))
    return out, list(titulares), list(classes)


# ----------------------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--raw', default=RAW_PADRAO, help='pasta com os CSVs oficiais')
    ap.add_argument('--saida', default=SAIDA_PADRAO, help='pasta de saída dos JSON do site')
    args = ap.parse_args()
    raw, saida = args.raw, args.saida
    os.makedirs(saida, exist_ok=True)
    t0 = datetime.datetime.now()
    agora = agora_local()
    hoje = agora.date()

    caminhos = {k: os.path.join(raw, v['arquivo']) for k, v in FONTES.items()}
    for k, p in caminhos.items():
        if not os.path.exists(p):
            raise SystemExit('Arquivo não encontrado: %s' % p)
    fontes_meta = {}
    for k, p in caminhos.items():
        h = le_headers(raw, k)
        fontes_meta[k] = {
            'orgao': FONTES[k]['orgao'], 'url': FONTES[k]['url'], 'pagina': FONTES[k]['pagina'],
            'licenca': FONTES[k]['licenca'], 'arquivo': FONTES[k]['arquivo'], 'bytes': os.path.getsize(p),
            'sha256': sha256_arquivo(p), 'etag': h.get('etag'), 'last_modified': h.get('last_modified'),
            'baixado_em': h.get('baixado_em'), 'codificacao': FONTES[k]['codificacao'],
        }
    versao = hashlib.sha256(('%d|' % FORMATO + '|'.join(fontes_meta[k]['sha256'] for k in sorted(fontes_meta)) +
                             '|' + hoje.isoformat()).encode()).hexdigest()[:12]

    # ---- formulados
    F = processa_formulados(caminhos['formulados'])
    prod, usos = F['prod'], F['usos']

    # ---- monografias
    mono, atos, cont_mono, cultura_anvisa_por_chave = processa_monografias(caminhos['monografias'], hoje)
    casa_anvisa = casador_anvisa(mono)

    # ---- dicionários de produto
    grupos_c = collections.defaultdict(collections.Counter)
    ing_grafia = collections.defaultdict(collections.Counter)
    ing_grupo = collections.defaultdict(collections.Counter)
    ing_prod = collections.Counter()
    tit_grafia = collections.defaultdict(collections.Counter)
    form_c = collections.Counter()
    classe_comp = collections.defaultdict(collections.Counter)
    modo_c = collections.defaultdict(collections.Counter)
    tox_c, amb_c = {}, {}
    sem_classe_tox, sem_classe_amb = collections.Counter(), collections.Counter()
    pre = {}
    for reg, (marca, form, ia, tit, classe, modo, tox, amb, org, sit) in prod.items():
        ings = parse_ingredientes(c1(ia))
        for nome, grupo, valor, unidade in ings:
            k = chave(nome)
            ing_grafia[k][nome] += 1
            if grupo:
                ing_grupo[k][grupo] += 1
                grupos_c[chave(grupo)][grupo] += 1
            ing_prod[k] += 1
        tk = chave(tit)
        tit_grafia[tk][limpa(tit)] += 1
        fl = limpa(form)
        form_c[fl] += 1
        comps = [frase(c) for c in limpa(classe).split('/') if limpa(c)]
        for c in comps:
            classe_comp[chave(c)][c] += 1
        ml = limpa(modo).rstrip(' .;,')
        if ml:
            modo_c[chave_modo(ml)][ml] += 1
        t = classifica(TOX, tox)
        if t is None:
            sem_classe_tox[limpa(tox)] += 1
            t = ('?', limpa(tox) or 'Não informado', '')
        tox_c[t[0]] = t
        a = classifica(AMB, amb)
        if a is None:
            sem_classe_amb[limpa(amb)] += 1
            a = ('?', limpa(amb) or 'Não informado')
        amb_c[a[0]] = a
        pre[reg] = (ings, tk, fl, comps, ml, t[0], a[0], ORGANICOS.get(limpa(org).upper(), '?'), sit)

    def ordena(chaves, nome):
        return sorted(chaves, key=lambda k: (chave(nome(k)), nome(k)))

    grupos_lista = ordena(list(grupos_c), lambda k: mais_frequente(grupos_c[k]))
    grupo_id = {k: i for i, k in enumerate(grupos_lista)}
    ing_lista = ordena(list(ing_grafia), lambda k: mais_frequente(ing_grafia[k]))
    ing_id = {k: i for i, k in enumerate(ing_lista)}
    tit_lista = ordena(list(tit_grafia), lambda k: mais_frequente(tit_grafia[k]))
    tit_id = {k: i for i, k in enumerate(tit_lista)}
    form_lista = sorted(form_c, key=chave)
    form_id = {k: i for i, k in enumerate(form_lista)}
    classe_lista = ordena(list(classe_comp), lambda k: mais_frequente(classe_comp[k]))
    classe_id = {k: i for i, k in enumerate(classe_lista)}
    modo_lista = ordena(list(modo_c), lambda k: mais_frequente(modo_c[k]))
    modo_id = {k: i for i, k in enumerate(modo_lista)}
    tag_lista = []
    for _, rot, _ in MODO_TAGS:
        if rot not in tag_lista:
            tag_lista.append(rot)
    tag_id = {t: i for i, t in enumerate(tag_lista)}
    modo_tags = {k: [tag_id[t] for t in tags_modo(mais_frequente(modo_c[k]))] for k in modo_lista}
    ordem_tox = ['1', '2', '3', '4', '5', 'NC', 'I', 'II', 'III', 'IV', 'ND', 'BE', '?']
    tox_lista = sorted(tox_c, key=lambda c: ordem_tox.index(c) if c in ordem_tox else 99)
    tox_id = {c: i for i, c in enumerate(tox_lista)}
    ordem_amb = ['I', 'II', 'III', 'IV', 'BR', '?']
    amb_lista = sorted(amb_c, key=lambda c: ordem_amb.index(c) if c in ordem_amb else 99)
    amb_id = {c: i for i, c in enumerate(amb_lista)}

    # culturas
    cult_lista = sorted(F['culturas_grafia'], key=lambda k: (k in CULTURAS_ESPECIAIS and k != 'todas as culturas', k))
    cult_id = {k: i for i, k in enumerate(cult_lista)}
    # alvos
    alvo_lista = sorted(F['alvos_grafia'], key=lambda k: (k == '', k))
    alvo_id = {k: i for i, k in enumerate(alvo_lista)}

    # ---- produtos ordenados pela 1ª marca
    def marcas_de(texto):
        return [limpa(m) for m in c1(texto).split(';') if limpa(m)]

    regs = sorted(prod, key=lambda r: (chave(marcas_de(prod[r][0])[0] if marcas_de(prod[r][0]) else r), r))
    prod_idx = {r: i for i, r in enumerate(regs)}

    cult_prod = collections.defaultdict(set)
    cult_usos = collections.Counter()
    alvo_prod = collections.defaultdict(set)
    alvo_fam = collections.defaultdict(collections.Counter)
    produtos = []
    usos_por_produto = []
    total_usos = 0
    for r in regs:
        ings, tk, fl, comps, ml, tc, ac, org, sit = pre[r]
        i = prod_idx[r]
        pares = usos[r]
        total_usos += len(pares)
        por_cult = collections.defaultdict(list)
        tipos = {TIPO_ALVO.get(familia_classe(c)) for c in comps} - {None}
        fam_alvo = next(iter(tipos)) if len(tipos) == 1 else None
        for ck, ak in pares:
            por_cult[cult_id[ck]].append(alvo_id[ak])
            cult_prod[ck].add(i)
            cult_usos[ck] += 1
            alvo_prod[ak].add(i)
            if fam_alvo:
                alvo_fam[ak][fam_alvo] += 1
        culturas_ids = sorted(por_cult)
        usos_por_produto.append([[c, sorted(por_cult[c])] for c in culturas_ids])
        ing_out = []
        for nome, grupo, valor, unidade in ings:
            ing_out.append([ing_id[chave(nome)], valor, unidade])
        produtos.append([
            r, marcas_de(prod[r][0]), form_id[fl], ing_out, tit_id[tk],
            sorted({classe_id[chave(c)] for c in comps}),
            modo_id[chave_modo(ml)] if ml else -1,
            modo_tags[chave_modo(ml)] if ml else [],
            tox_id[tc], amb_id[ac], org, 1 if limpa(sit).upper() == 'TRUE' else 0,
            culturas_ids, len(pares), len({a for _, a in pares}),
        ])

    # ---- dicionário de culturas (com ANVISA e fatia)
    def nome_cultura(k):
        grafia = mais_frequente(F['culturas_grafia'][k]) if F['culturas_grafia'][k] else ''
        if k == '':
            return '(cultura não informada)', None
        corr = CULTURA_CORRECAO.get(k)
        return (corr, grafia) if corr and corr != grafia else (grafia, None)

    def anvisa_de(k):
        if k in CULTURAS_ESPECIAIS:
            return None
        if k in cultura_anvisa_por_chave:
            return cultura_anvisa_por_chave[k]
        base = re.sub(r' (ogm|armazenad[oa])$', '', k).strip()
        alias = CULTURA_ANVISA_ALIAS.get(k) or CULTURA_ANVISA_ALIAS.get(base) or base
        return cultura_anvisa_por_chave.get(alias)

    # fatias por cultura: empacota em ordem de id até ~ALVO_BYTES_CULTURA
    blocos_cult = {}
    for k in cult_lista:
        cid = cult_id[k]
        por_alvo = collections.defaultdict(list)
        for i in sorted(cult_prod[k]):
            for c, alvos in usos_por_produto[i]:
                if c == cid:
                    for a in alvos:
                        por_alvo[a].append(i)
        blocos_cult[cid] = [[a, por_alvo[a]] for a in sorted(por_alvo)]
    fatias_cult, atual, tam = [], {}, 0
    for k in cult_lista:
        cid = cult_id[k]
        t = len(json.dumps(blocos_cult[cid], separators=(',', ':')))
        if atual and tam + t > ALVO_BYTES_CULTURA:
            fatias_cult.append(atual)
            atual, tam = {}, 0
        atual[cid] = blocos_cult[cid]
        tam += t
    if atual:
        fatias_cult.append(atual)
    fatia_de_cultura = {cid: n for n, f in enumerate(fatias_cult) for cid in f}

    culturas_out = []
    anvisa_sem_par = []
    for k in cult_lista:
        nome, oficial = nome_cultura(k)
        anv = anvisa_de(k)
        if anv is None and k not in CULTURAS_ESPECIAIS:
            anvisa_sem_par.append(nome)
        culturas_out.append([nome, oficial, anv, len(cult_prod[k]), cult_usos[k], fatia_de_cultura[cult_id[k]],
                             1 if k in CULTURAS_ESPECIAIS else 0])

    alvos_out = []
    tipo_alvo_cont = collections.Counter()
    for k in alvo_lista:
        sci = mais_frequente(F['alvos_grafia'][k]) if k else ''
        comuns = [mais_frequente(F['comum_grafia'][nk]) for nk, _ in
                  sorted(F['alvos_comum'][k].items(), key=lambda kv: (-kv[1], kv[0]))]
        fam = alvo_fam[k]
        tipo = ''
        if fam and k:
            top, n = fam.most_common(1)[0]
            if n >= 0.6 * sum(fam.values()):
                tipo = top
        tipo_alvo_cont[tipo] += 1
        alvos_out.append([sci, comuns, tipo, len(alvo_prod[k])])

    ing_out_dic = []
    casamento = collections.Counter()
    sem_monografia_quimicos = []
    for k in ing_lista:
        nome = mais_frequente(ing_grafia[k])
        grupo = mais_frequente(ing_grupo[k]) if ing_grupo[k] else ''
        cod, como = casa_anvisa(nome)
        casamento[como or 'sem_monografia'] += 1
        gk = chave(grupo)
        if not cod and not re.search(r'biol|microb|nemat|virus|extrato|vegetal|feromon|parasit|predador|fung|acar|'
                                     r'insaturad|aldeid|alifatic|semioq', gk) and not re.search(
                r'^(bacillus|cordyceps|metarhizium|beauveria|trichoderma|neoseiulus|phytoseiulus|amblyseius|'
                r'stratiolaelaps|acetato de \(|\(|e 11)|lure|extrato', chave(nome)):
            sem_monografia_quimicos.append(nome)
        ing_out_dic.append([nome, grupo_id[gk] if grupo else -1, cod, ing_prod[k]])

    classes_out = []
    for k in classe_lista:
        nome = mais_frequente(classe_comp[k])
        classes_out.append([nome, familia_classe(nome), 1 if re.search(r'microbiol|biologic', k) else 0])

    formulacoes_out = []
    for fl in form_lista:
        m = re.match(r'^([A-Z]{2})\s*-\s*(.+)$', fl)
        formulacoes_out.append([m.group(1), m.group(2)] if m else ['', fl or 'Não informada'])

    # ---- LMR por monografia (só as usadas por algum ingrediente, mais as demais para consulta)
    lmr_out = {}
    for cod, m in sorted(mono.items()):
        lmr_out[cod] = [m['nome'], m['cas'], {nome: reg for _, (nome, reg) in sorted(m['culturas'].items())}]

    # ---- técnicos
    tecnicos, tec_tit, tec_classes = processa_tecnicos(caminhos['tecnicos'], {k: i for i, k in enumerate(ing_lista)})

    # ---- verificação de consistência
    erros = []
    if len(produtos) != len(prod):
        erros.append('produtos != registros')
    if sum(F['linhas_por_registro'].values()) != F['linhas']:
        erros.append('linhas por registro não somam')
    soma_usos_cult = sum(len(ps) for f in fatias_cult for blocos in f.values() for _, ps in blocos)
    soma_usos_prod = sum(len(a) for u in usos_por_produto for _, a in u)
    if not (soma_usos_cult == soma_usos_prod == total_usos == sum(p[13] for p in produtos)):
        erros.append('usos divergentes: cultura=%d produto=%d total=%d' % (soma_usos_cult, soma_usos_prod, total_usos))
    if F['divergencias']:
        erros.append('%d registros com campos de produto diferentes entre linhas' % len(F['divergencias']))
    if erros:
        raise SystemExit('Falha de consistência: ' + '; '.join(erros))

    # ---- escrita
    arquivos = {}
    base = {'versao': versao, 'formato': FORMATO}
    novos = set()

    def grava(nome, obj):
        caminho = os.path.join(saida, nome)
        arquivos[nome] = escreve_json(caminho, obj)
        novos.add(nome)
        if arquivos[nome] > LIMITE_ARQUIVO:
            raise SystemExit('%s passou de 5 MB (%d bytes)' % (nome, arquivos[nome]))

    todas_id = cult_id.get('todas as culturas')
    grava('agrofit_indice.json', dict(base, **{
        'campos': ['registro', 'marcas', 'formulacao', 'ingredientes', 'titular', 'classes', 'modo', 'modoTags',
                   'tox', 'amb', 'organico', 'ativo', 'culturas', 'nUsos', 'nAlvos'],
        'culturas': culturas_out, 'todasCulturas': todas_id,
        'alvos': alvos_out, 'ingredientes': ing_out_dic, 'gruposQuimicos': [mais_frequente(grupos_c[k]) for k in grupos_lista],
        'titulares': [mais_frequente(tit_grafia[k]) for k in tit_lista], 'classes': classes_out,
        'formulacoes': formulacoes_out, 'modos': [mais_frequente(modo_c[k]) for k in modo_lista], 'modoTags': tag_lista,
        'tox': [[tox_c[c][1], c, tox_c[c][2]] for c in tox_lista],
        'amb': [[amb_c[c][1], c] for c in amb_lista],
        'organicos': {'S': 'Sim', 'N': 'Não', 'O': 'Outros'},
        'produtosPorArquivo': PRODUTOS_POR_ARQUIVO,
        'produtos': produtos,
    }))
    for n, f in enumerate(fatias_cult):
        grava('agrofit_usos_cultura_%d.json' % n, dict(base, culturas={str(c): b for c, b in f.items()}))
    for n in range(0, len(usos_por_produto), PRODUTOS_POR_ARQUIVO):
        grava('agrofit_usos_produto_%d.json' % (n // PRODUTOS_POR_ARQUIVO),
              dict(base, inicio=n, produtos=usos_por_produto[n:n + PRODUTOS_POR_ARQUIVO]))
    grava('agrofit_lmr.json', dict(base, **{
        'campos': ['lmr_mg_kg', 'tipo', 'autorizado', 'ato', 'inicioVigencia'],
        'tipos': {'M': 'Limite máximo', 'T': 'Limite de tolerância', 'N': 'Não estabelecido'},
        'referencia': hoje.isoformat(), 'atos': atos, 'monografias': lmr_out,
    }))
    grava('agrofit_tecnicos.json', dict(base, **{
        'campos': ['registro', 'marca', 'ingredientes', 'classe', 'titular', 'tox', 'amb'],
        'titulares': tec_tit, 'classes': tec_classes, 'produtos': tecnicos,
    }))

    contagens = {
        'linhas_formulados': F['linhas'],
        'registros': len(produtos),
        'usos_distintos': total_usos,
        'linhas_repetidas_apos_normalizar': F['linhas'] - total_usos,
        'culturas_distintas_brutas': len(F['culturas_raw']),
        'culturas': len(culturas_out),
        'culturas_com_par_anvisa': sum(1 for c in culturas_out if c[2]),
        'alvos_distintos_brutos': len(F['alvos_raw']),
        'alvos': len(alvos_out),
        'alvos_por_tipo': {({'D': 'daninha', 'P': 'praga', 'O': 'doenca', '': 'indefinido'}[k]): v
                           for k, v in sorted(tipo_alvo_cont.items())},
        'ingredientes': len(ing_out_dic),
        'ingredientes_com_monografia': sum(1 for x in ing_out_dic if x[2]),
        'casamento_ingrediente_anvisa': dict(casamento),
        'grupos_quimicos': len(grupos_lista),
        'titulares': len(tit_lista),
        'classes_componentes': len(classes_out),
        'formulacoes': len(formulacoes_out),
        'modos_de_acao_texto': len(modo_lista),
        'produtos_por_toxicologica': {tox_c[c][1]: sum(1 for p in produtos if p[8] == tox_id[c]) for c in tox_lista},
        'produtos_por_ambiental': {amb_c[c][1]: sum(1 for p in produtos if p[9] == amb_id[c]) for c in amb_lista},
        'produtos_organicos': dict(collections.Counter(p[10] for p in produtos)),
        'produtos_ativos': sum(p[11] for p in produtos),
        'monografias': len(mono),
        'monografias_com_lmr_vigente': sum(1 for m in mono.values() if m['culturas']),
        'monografias_lmr': dict(cont_mono),
        'lmr_vigentes': sum(len(m['culturas']) for m in mono.values()),
        'tecnicos': len(tecnicos),
        'fatias_cultura': len(fatias_cult),
        'fatias_produto': (len(usos_por_produto) + PRODUTOS_POR_ARQUIVO - 1) // PRODUTOS_POR_ARQUIVO,
    }
    meta = dict(base, **{
        'processado_em': agora.isoformat(timespec='seconds'),
        'processador': 'dados_agrofit/processar.py',
        'fontes': fontes_meta,
        'contagens': contagens,
        'avisos': {
            'sem_dose_carencia': 'Os dados abertos do AGROFIT não trazem dose, carência, intervalo de reentrada nem número '
                                 'de aplicações; esses dados estão só na bula/rótulo do produto.',
            'sem_irac_frac_hrac': 'O AGROFIT não informa o grupo de resistência (IRAC/FRAC/HRAC); só o texto de modo de ação '
                                  'e o grupo químico de cada ingrediente.',
            'so_ativos': 'O arquivo de formulados lista só registros ativos (SITUACAO = TRUE). Produto que some entre '
                         'duas publicações deve ser tratado como cancelado/suspenso até conferência no AGROFIT.',
            'todas_as_culturas': 'Usos na cultura "Todas as culturas" valem para qualquer cultura e devem entrar nos filtros '
                                 'por cultura.',
            'tipo_alvo': 'O tipo do alvo (daninha/praga/doença) é derivado da classe dos produtos indicados para ele; '
                         'não vem da fonte.',
            'lmr': 'LMR vigente na data de referência; para ingredientes biológicos, em geral não há monografia com LMR.',
            'organicos_outros': 'O valor OUTROS da coluna ORGANICOS não tem significado documentado na fonte.',
            'culturas_sem_anvisa': sorted(anvisa_sem_par),
            'ingredientes_quimicos_sem_monografia': sorted(sem_monografia_quimicos),
            'toxicologica_nao_mapeada': dict(sem_classe_tox),
            'ambiental_nao_mapeada': dict(sem_classe_amb),
        },
        'arquivos': {},
        'formato_descricao': {
            'agrofit_indice.json': 'produtos[i] segue "campos". formulacao/titular/tox/amb/modo são índices nos dicionários '
                                   'de mesmo nome (modo -1 = não informado); ingredientes = [[idIngrediente, valor, unidade]]; '
                                   'classes e modoTags = listas de índices; culturas = ids em "culturas". '
                                   'culturas[id] = [nome, nomeOficialSeCorrigido, culturaAnvisa, nProdutos, nUsos, '
                                   'fatiaUsosCultura, especial]. alvos[id] = [cientifico, [comuns], tipo D/P/O/"", nProdutos]. '
                                   'ingredientes[id] = [nome, idGrupoQuimico, codigoMonografiaAnvisa, nProdutos].',
            'agrofit_usos_cultura_<n>.json': 'culturas["<idCultura>"] = [[idAlvo, [idxProduto...]], ...]. A fatia de cada '
                                             'cultura está em indice.culturas[id][5].',
            'agrofit_usos_produto_<n>.json': 'produtos[i - inicio] = [[idCultura, [idAlvo...]], ...]; n = floor(i / '
                                             'produtosPorArquivo).',
            'agrofit_lmr.json': 'monografias[codigo] = [nome, cas, {culturaAnvisa: [lmr_mg_kg, tipo, autorizado, idAto, '
                                'inicioVigencia]}]; casar por indice.ingredientes[id][2] e indice.culturas[id][2].',
            'agrofit_tecnicos.json': 'produtos técnicos (matéria-prima); ingredientes = [[idIngrediente ou nome, valor, '
                                     'unidade]].',
            'versao': 'Todos os arquivos de uma mesma geração têm o mesmo "versao"; a página deve recarregar se divergir.',
        },
    })
    # meta por último, com o tamanho dos demais arquivos desta geração
    meta['arquivos'] = dict(sorted(arquivos.items()))
    grava('agrofit_meta.json', meta)

    # remove fatias velhas que não fazem mais parte desta geração
    for nome in os.listdir(saida):
        if nome.startswith('agrofit_') and nome.endswith('.json') and nome not in novos:
            os.remove(os.path.join(saida, nome))

    seg = (datetime.datetime.now() - t0).total_seconds()
    print('versao', versao, '| processado em %.1f s' % seg)
    print('linhas', F['linhas'], '| registros', len(produtos), '| usos distintos', total_usos,
          '| culturas brutas/normalizadas', len(F['culturas_raw']), '/', len(culturas_out),
          '| alvos brutos/normalizados', len(F['alvos_raw']), '/', len(alvos_out))
    print('ingredientes', len(ing_out_dic), '| com monografia ANVISA', contagens['ingredientes_com_monografia'],
          dict(casamento))
    print('monografias', len(mono), '| LMR vigentes', contagens['lmr_vigentes'], dict(cont_mono))
    print('técnicos', len(tecnicos), '| culturas sem par ANVISA', len(anvisa_sem_par))
    total = 0
    for nome, b in sorted(arquivos.items()):
        total += b
        print('  %-34s %10d bytes' % (nome, b))
    print('  %-34s %10d bytes' % ('TOTAL', total))


if __name__ == '__main__':
    main()
