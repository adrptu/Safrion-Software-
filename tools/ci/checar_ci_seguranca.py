# -*- coding: utf-8 -*-
"""Portão das regras de segurança da própria CI (FERR-01, PRD 25.2: nenhuma alta/crítica aplicável sem resolução).
Confere em .github/workflows/*.yml:
- todo passo do Trivy bloqueia (exit-code "1"), cobre HIGH e CRITICAL e não ignora vulnerabilidade sem correção
  (ignore-unfixed ausente ou false);
- nenhum passo ou job com continue-on-error: true;
- exceção só em .trivyignore.yaml (formato do Trivy, referenciado em trivyignores), cada item com statement
  (não aplicabilidade comprovada) e expired_at (aaaa-mm-dd, no máximo 90 dias à frente). .trivyignore simples, sem
  motivo nem validade, é recusado.
Sem PyYAML: o .trivyignore.yaml é lido num subconjunto estrito, com as chaves em qualquer ordem. O que fica fora dele
é recusado, nunca aprovado (FERR-03). Nulo do YAML 1.2 (null, Null, NULL, ~) é ausência de valor, não texto: é
recusado em qualquer campo, também entre aspas, porque nunca é id, motivo, data ou caminho válido (FERR-04).
O YAML dos workflows é lido por texto, no formato deste repositório.
Uso: python3 tools/ci/checar_ci_seguranca.py [raiz] [--hoje=AAAA-MM-DD]"""
import datetime, glob, os, re, sys

VALIDADE_MAX_DIAS = 90
args = [a for a in sys.argv[1:] if not a.startswith('--hoje=')]
raiz = os.path.abspath(args[0] if args else os.getcwd())
hoje = next((datetime.date.fromisoformat(a.split('=', 1)[1]) for a in sys.argv[1:] if a.startswith('--hoje=')), datetime.date.today())
erros = []


def indent(linha):
    return len(linha) - len(linha.lstrip(' '))


def valor(v):
    return v.split(' #', 1)[0].strip().strip('"\'')


def blocos_trivy(linhas):
    """Cada passo da trivy-action, com "- uses:" ou com "- name:" e "uses:" abaixo: do hífen do passo até a próxima
    linha com a mesma indentação ou menor."""
    for i, l in enumerate(linhas):
        if 'aquasecurity/trivy-action@' not in l or not re.match(r'\s*(-\s*)?uses:', l):
            continue
        ini = i
        while ini >= 0 and not (linhas[ini].lstrip().startswith('- ') and indent(linhas[ini]) <= indent(l)):
            ini -= 1
        if ini < 0:
            ini = i
        base = indent(linhas[ini])
        bloco = [linhas[ini][base + 2:]] if ini != i else []
        for m in linhas[ini + 1:]:
            if m.strip() and indent(m) <= base:
                break
            bloco.append(m)
        chaves = {}
        for m in bloco:
            k = re.match(r'\s*([A-Za-z-]+):\s*(.*)$', m)
            if k:
                chaves[k.group(1)] = valor(k.group(2))
        yield i + 1, chaves


workflows = sorted(glob.glob(os.path.join(raiz, '.github', 'workflows', '*.yml')) + glob.glob(os.path.join(raiz, '.github', 'workflows', '*.yaml')))
if not workflows:
    erros.append('nenhum workflow em .github/workflows')
passos = 0
referencias_ignore = set()
for wf in workflows:
    nome = os.path.relpath(wf, raiz)
    linhas = open(wf, encoding='utf-8').read().splitlines()
    for n, l in enumerate(linhas, 1):
        if re.match(r'\s*continue-on-error:\s*["\']?true', l):
            erros.append(f'{nome}:{n}: continue-on-error: true esconde falha')
    for n, k in blocos_trivy(linhas):
        passos += 1
        if k.get('exit-code') != '1':
            erros.append(f'{nome}:{n}: passo do Trivy sem exit-code "1" (não bloqueia)')
        if k.get('ignore-unfixed', 'false').lower() != 'false':
            erros.append(f'{nome}:{n}: ignore-unfixed deixa passar alta/crítica sem correção (PRD 25.2)')
        sev = {s.strip().upper() for s in k.get('severity', 'UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL').split(',')}
        if not {'HIGH', 'CRITICAL'} <= sev:
            erros.append(f'{nome}:{n}: severity precisa incluir HIGH e CRITICAL')
        if k.get('trivyignores'):
            for r in k['trivyignores'].split(','):
                r = r.strip()
                referencias_ignore.add(r)
                if r != '.trivyignore.yaml':
                    erros.append(f'{nome}:{n}: trivyignores só aceita .trivyignore.yaml (com motivo e validade), não {r!r}')
if workflows and passos == 0:
    erros.append('nenhum passo do Trivy encontrado nos workflows')

if os.path.exists(os.path.join(raiz, '.trivyignore')):
    erros.append('.trivyignore simples não registra motivo nem validade; use .trivyignore.yaml')
SECOES = ('vulnerabilities', 'misconfigurations', 'secrets', 'licenses')
NULOS = {'null', 'Null', 'NULL', '~'}


def nulo(bruto):
    """Verdadeiro para o nulo do YAML 1.2 (Core Schema), com ou sem aspas e com ou sem comentário (FERR-04)."""
    v = bruto.split(' #', 1)[0].strip()
    return v in NULOS or valor(v) in NULOS
CHAVES = {'id', 'paths', 'purls', 'statement', 'expired_at'}
LISTAS = {'paths', 'purls'}


def ler_trivyignore(texto):
    """Lê o subconjunto de YAML aceito para .trivyignore.yaml, com as chaves de cada item em qualquer ordem.
    Qualquer construção fora desse subconjunto (tab, documento múltiplo, âncora, tag, estilo em chaves, bloco
    multilinha, chave desconhecida ou repetida, linha que não se encaixa) é recusada: nunca vira aprovação (FERR-03).
    Devolve (itens, erros); cada item é {'linha', 'id', 'statement', 'expired_at', ...}."""
    itens, erros_f = [], []
    secao = recuo_item = None
    item = lista_aberta = None
    for n, bruta in enumerate(texto.splitlines(), 1):
        if '\t' in bruta:
            erros_f.append(f'.trivyignore.yaml:{n}: tab não é aceito; use espaços'); continue
        linha = bruta.rstrip()
        if not linha.strip() or linha.lstrip().startswith('#'):
            continue
        if linha.strip() in ('---', '...'):
            erros_f.append(f'.trivyignore.yaml:{n}: documento múltiplo não é aceito'); continue
        rec = indent(linha)
        conteudo = linha.strip()
        if rec == 0:
            m = re.fullmatch(r'([a-z]+):\s*(\[\s*\])?', conteudo)
            if not m or m.group(1) not in SECOES:
                erros_f.append(f'.trivyignore.yaml:{n}: seção não suportada {conteudo!r}; use {", ".join(SECOES)}')
                secao = None; continue
            secao, recuo_item, item, lista_aberta = m.group(1), None, None, None
            continue
        if secao is None:
            erros_f.append(f'.trivyignore.yaml:{n}: linha fora de uma seção'); continue
        m_item = re.fullmatch(r'-\s+(.*)', conteudo)
        if m_item and (recuo_item is None or rec == recuo_item):
            recuo_item = rec
            item = {'linha': n}; itens.append(item); lista_aberta = None
            conteudo, rec = m_item.group(1), rec + 2
        elif item is None:
            erros_f.append(f'.trivyignore.yaml:{n}: esperado um item começando por "- "'); continue
        elif m_item and lista_aberta and rec > recuo_item + 2 - 1:
            v = valor(m_item.group(1))
            if nulo(m_item.group(1)):
                erros_f.append(f'.trivyignore.yaml:{n}: {lista_aberta} com item nulo não é aceito')
            elif not v or v[0] in '&*!{[|>':
                erros_f.append(f'.trivyignore.yaml:{n}: valor não suportado em {lista_aberta}')
            else:
                item[lista_aberta].append(v)
            continue
        if rec != recuo_item + 2:
            erros_f.append(f'.trivyignore.yaml:{n}: indentação não suportada'); continue
        m_chave = re.fullmatch(r'([a-z_]+):(?:\s+(.*))?', conteudo)
        if not m_chave:
            erros_f.append(f'.trivyignore.yaml:{n}: linha não suportada {conteudo!r}'); continue
        chave, bruto = m_chave.group(1), (m_chave.group(2) or '').strip()
        if chave not in CHAVES:
            erros_f.append(f'.trivyignore.yaml:{n}: chave não suportada {chave!r}'); continue
        if chave in item:
            erros_f.append(f'.trivyignore.yaml:{n}: chave repetida {chave!r}'); continue
        if bruto[:1] in ('&', '*', '!', '{', '|', '>'):
            erros_f.append(f'.trivyignore.yaml:{n}: {chave} com âncora, tag, chaves ou bloco multilinha não é aceito'); continue
        if nulo(bruto):
            erros_f.append(f'.trivyignore.yaml:{n}: {chave} nulo ({bruto.split(" #", 1)[0].strip()}) é ausência de valor, não é aceito'); continue
        lista_aberta = None
        if chave in LISTAS:
            if not bruto:
                item[chave] = []; lista_aberta = chave
            elif re.fullmatch(r'\[(.*)\]', bruto.split(' #', 1)[0].strip()):
                interior = bruto.split(' #', 1)[0].strip()[1:-1]
                if any(nulo(x) for x in interior.split(',')):
                    erros_f.append(f'.trivyignore.yaml:{n}: {chave} com item nulo não é aceito'); continue
                item[chave] = [valor(x) for x in interior.split(',') if x.strip()]
            else:
                erros_f.append(f'.trivyignore.yaml:{n}: {chave} deve ser uma lista'); continue
        elif bruto.startswith('['):
            erros_f.append(f'.trivyignore.yaml:{n}: {chave} deve ser um valor simples'); continue
        else:
            item[chave] = valor(bruto)
    return itens, erros_f


arq = os.path.join(raiz, '.trivyignore.yaml')
if os.path.exists(arq):
    if '.trivyignore.yaml' not in referencias_ignore:
        erros.append('.trivyignore.yaml existe mas nenhum passo do Trivy o referencia em trivyignores')
    with open(arq, encoding='utf-8') as f:
        itens, erros_formato = ler_trivyignore(f.read())
    erros.extend(erros_formato)
    for it in itens:
        onde = f'.trivyignore.yaml:{it["linha"]} ({it.get("id") or "sem id"})'
        if not it.get('id'):
            erros.append(f'{onde}: falta id')
        if not it.get('statement'):
            erros.append(f'{onde}: falta statement com a prova de não aplicabilidade')
        exp = it.get('expired_at', '')
        try:
            data = datetime.date.fromisoformat(exp)
        except ValueError:
            erros.append(f'{onde}: expired_at obrigatório no formato aaaa-mm-dd')
            continue
        if data < hoje:
            erros.append(f'{onde}: exceção vencida em {exp}; revisar ou remover')
        elif (data - hoje).days > VALIDADE_MAX_DIAS:
            erros.append(f'{onde}: validade acima de {VALIDADE_MAX_DIAS} dias ({exp})')

if erros:
    for e in erros:
        print('ERRO:', e)
    sys.exit(1)
print(f'OK: {passos} passo(s) do Trivy bloqueiam alta/crítica com ou sem correção; nenhuma exceção sem motivo e validade.')
sys.exit(0)
