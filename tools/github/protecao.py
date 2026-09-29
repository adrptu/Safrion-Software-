# -*- coding: utf-8 -*-
"""Validação sem rede do ruleset da main (protecao-main.json) contra o ruleset atual e os jobs reais da CI.

Usado por configurar_protecao.sh e pela regressão tools/ci/test_protecao_main.py. Falha fechado: forma de
workflow que não reconhece gera erro, nunca lista incompleta de checks.

  python3 protecao.py escolher-id --lista LISTA.json --payload P.json
  python3 protecao.py verificar --payload P.json --atual GET.json --raiz RAIZ
  python3 protecao.py conferir-retorno --payload P.json --atual GET.json
"""
import argparse, glob, itertools, json, os, re, sys

APP_GITHUB_ACTIONS = 15368
CAMPOS = ('name', 'target', 'enforcement', 'conditions', 'bypass_actors')
PADROES_RSC = {'do_not_enforce_on_create': False}
EXPR = re.compile(r'\$\{\{\s*(.*?)\s*\}\}')


class FormaNaoReconhecida(Exception):
    pass


def _sem_aspas(v):
    v = v.split(' #', 1)[0].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        return v[1:-1]
    return v


def _bloco(linhas, i, recuo):
    """Linhas depois de linhas[i] com recuo maior que `recuo` (ignora vazias e comentários)."""
    fim = i + 1
    while fim < len(linhas):
        l = linhas[fim]
        if l.strip() and not l.lstrip().startswith('#') and len(l) - len(l.lstrip()) <= recuo:
            break
        fim += 1
    return linhas[i + 1:fim]


def _dispara_em_pr(linhas, arq):
    for i, l in enumerate(linhas):
        m = re.match(r'^(on|"on"|\'on\'):\s*(.*)$', l)
        if not m:
            continue
        resto = _sem_aspas(m.group(2))
        if resto:
            if resto.startswith('{'):
                raise FormaNaoReconhecida(f'{arq}: on: em forma de mapa na mesma linha')
            itens = [x.strip() for x in resto.strip('[]').split(',')]
            return 'pull_request' in itens
        bloco = _bloco(linhas, i, 0)
        for k, x in enumerate(bloco):
            if re.match(r'^\s+-\s*pull_request\s*$', x):
                return True
            mp = re.match(r'^(\s+)pull_request:\s*(.*)$', x)
            if not mp:
                continue
            filtros = [y.strip() for y in _bloco(bloco, k, len(mp.group(1)))
                       if y.strip() and not y.lstrip().startswith('#')]
            if _sem_aspas(mp.group(2)) or filtros:
                raise FormaNaoReconhecida(f'{arq}: pull_request com filtro ({(filtros or [mp.group(2)])[0]}); '
                                          'o check obrigatório poderia não rodar e travar o merge')
            return True
        return False
    raise FormaNaoReconhecida(f'{arq}: sem bloco on:')


def _matriz(bloco, chave, arq):
    for i, l in enumerate(bloco):
        m = re.match(r'^(\s+)matrix:\s*(.*)$', l)
        if not m:
            continue
        if m.group(2).strip():
            raise FormaNaoReconhecida(f'{arq}/{chave}: matrix por expressão')
        valores = {}
        for x in _bloco(bloco, i, len(m.group(1))):
            if not x.strip() or x.lstrip().startswith('#'):
                continue
            mv = re.match(r'^\s+([A-Za-z0-9_-]+):\s*\[(.*)\]\s*$', x)
            if not mv or mv.group(1) in ('include', 'exclude'):
                raise FormaNaoReconhecida(f'{arq}/{chave}: matrix fora da forma "var: [a, b]": {x.strip()}')
            valores[mv.group(1)] = [_sem_aspas(v) for v in mv.group(2).split(',') if v.strip()]
        return valores
    raise FormaNaoReconhecida(f'{arq}/{chave}: nome usa matrix, mas o job não tem matrix')


def contextos_dos_workflows(raiz):
    """Nomes de check que cada job disparado em pull_request publica, com a matrix expandida."""
    arqs = sorted(glob.glob(os.path.join(raiz, '.github', 'workflows', '*.yml')) +
                  glob.glob(os.path.join(raiz, '.github', 'workflows', '*.yaml')))
    nomes = []
    for caminho in arqs:
        arq = os.path.relpath(caminho, raiz)
        with open(caminho, encoding='utf-8') as f:
            linhas = f.read().splitlines()
        if not _dispara_em_pr(linhas, arq):
            continue
        inicio = next((i for i, l in enumerate(linhas) if re.match(r'^jobs:\s*$', l)), None)
        if inicio is None:
            raise FormaNaoReconhecida(f'{arq}: sem jobs:')
        corpo = _bloco(linhas, inicio, 0)
        for i, l in enumerate(corpo):
            m = re.match(r'^  ([A-Za-z0-9_-]+):\s*$', l)
            if not m:
                if re.match(r'^  \S', l) and not l.lstrip().startswith('#'):
                    raise FormaNaoReconhecida(f'{arq}: job fora da forma "  chave:": {l.strip()}')
                continue
            chave, bloco = m.group(1), _bloco(corpo, i, 2)
            for x in bloco:
                mc = re.match(r'^    (if|continue-on-error):', x)
                if mc:
                    raise FormaNaoReconhecida(f'{arq}/{chave}: job com {mc.group(1)}:; o check poderia ser pulado '
                                              'ou falhar e ainda contar como aprovado')
            nome = next((_sem_aspas(x.split(':', 1)[1]) for x in bloco if re.match(r'^    name:', x)), chave)
            exprs = EXPR.findall(nome)
            if not exprs:
                nomes.append(nome)
                continue
            vars_ = []
            for e in exprs:
                mv = re.fullmatch(r'matrix\.([A-Za-z0-9_-]+)', e)
                if not mv:
                    raise FormaNaoReconhecida(f'{arq}/{chave}: expressão no nome fora de matrix.*: {e}')
                vars_.append(mv.group(1))
            matriz = _matriz(bloco, chave, arq)
            if any(v not in matriz for v in vars_):
                raise FormaNaoReconhecida(f'{arq}/{chave}: variável de matrix ausente')
            for combo in itertools.product(*(matriz[v] for v in vars_)):
                troca = dict(zip(vars_, combo))
                nomes.append(EXPR.sub(lambda mm: troca[mm.group(1).split('.', 1)[1]], nome))
    repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
    if repetidos:
        raise FormaNaoReconhecida(f'nomes de check repetidos entre jobs: {repetidos}')
    return nomes


def _regras(ruleset):
    regras = {}
    for r in ruleset.get('rules', []):
        if r['type'] in regras:
            raise ValueError(f'regra repetida: {r["type"]}')
        par = dict(r.get('parameters') or {})
        if r['type'] == 'required_status_checks':
            par = {**PADROES_RSC, **par}
            par['required_status_checks'] = sorted(
                par.get('required_status_checks', []), key=lambda c: (c.get('context', ''), c.get('integration_id', 0)))
        regras[r['type']] = par
    return regras


def normalizar(ruleset):
    """Só os campos graváveis por PUT, em forma comparável (ordem de regras e de checks irrelevante)."""
    return {**{c: ruleset.get(c) for c in CAMPOS}, 'rules': _regras(ruleset)}


def diferencas(atual, desejado):
    a, d = normalizar(atual), normalizar(desejado)
    saida = [f'{c}: {json.dumps(a[c], ensure_ascii=False)} -> {json.dumps(d[c], ensure_ascii=False)}'
             for c in CAMPOS if a[c] != d[c]]
    for tipo in sorted(set(a['rules']) | set(d['rules'])):
        if a['rules'].get(tipo) != d['rules'].get(tipo):
            if tipo not in a['rules']:
                saida.append(f'regra nova: {tipo} {json.dumps(d["rules"][tipo], ensure_ascii=False)}')
            elif tipo not in d['rules']:
                saida.append(f'regra removida: {tipo}')
            else:
                saida.append(f'regra alterada: {tipo} {json.dumps(a["rules"][tipo], ensure_ascii=False)} -> '
                             f'{json.dumps(d["rules"][tipo], ensure_ascii=False)}')
    return saida


def problemas(payload, atual, contextos):
    """O que impede aplicar: só a regra de checks pode mudar, e ela precisa bater com os jobs reais."""
    p, a, erros = normalizar(payload), normalizar(atual), []
    for c in CAMPOS:
        if p[c] != a[c]:
            erros.append(f'{c} difere do ruleset atual; este arquivo só acrescenta checks')
    if p['bypass_actors'] != []:
        erros.append('bypass_actors precisa ficar vazio')
    for tipo in sorted((set(p['rules']) | set(a['rules'])) - {'required_status_checks'}):
        if p['rules'].get(tipo) != a['rules'].get(tipo):
            erros.append(f'regra {tipo} difere do ruleset atual (preservar exatamente)')
    rsc = p['rules'].get('required_status_checks')
    if rsc is None:
        return erros + ['falta a regra required_status_checks']
    if rsc.get('strict_required_status_checks_policy') is not True:
        erros.append('strict_required_status_checks_policy precisa ser true')
    checks = rsc.get('required_status_checks', [])
    nomes = [c.get('context') for c in checks]
    for n in sorted({n for n in nomes if nomes.count(n) > 1}):
        erros.append(f'check repetido: {n}')
    for c in checks:
        if c.get('integration_id') != APP_GITHUB_ACTIONS:
            erros.append(f'check sem o app GitHub Actions ({APP_GITHUB_ACTIONS}): {c.get("context")}')
    for n in sorted(set(nomes) - set(contextos)):
        erros.append(f'check sem job que o publique (travaria todo merge): {n}')
    for n in sorted(set(contextos) - set(nomes)):
        erros.append(f'job da CI fora dos checks obrigatórios: {n}')
    return erros


def escolher_id(lista, nome):
    ids = [r['id'] for r in lista if r.get('name') == nome and r.get('target') == 'branch']
    if len(ids) != 1:
        raise ValueError(f'esperado 1 ruleset de branch "{nome}"; achados: {len(ids)}. Nada foi alterado.')
    return ids[0]


def _ler(caminho):
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('escolher-id'); e.add_argument('--lista', required=True); e.add_argument('--payload', required=True)
    v = sub.add_parser('verificar'); v.add_argument('--payload', required=True); v.add_argument('--atual', required=True)
    v.add_argument('--raiz', required=True)
    r = sub.add_parser('conferir-retorno'); r.add_argument('--payload', required=True); r.add_argument('--atual', required=True)
    a = ap.parse_args(argv)
    payload = _ler(a.payload)
    try:
        if a.cmd == 'escolher-id':
            print(escolher_id(_ler(a.lista), payload['name']))
            return 0
        atual = _ler(a.atual)
        if a.cmd == 'verificar':
            erros = problemas(payload, atual, contextos_dos_workflows(a.raiz))
            for d in diferencas(atual, payload) or ['nenhuma: o ruleset atual já é o do arquivo']:
                print(f'diferença: {d}')
            for x in erros:
                print(f'ERRO: {x}', file=sys.stderr)
            return 1 if erros else 0
        resto = diferencas(atual, payload)
        for d in resto:
            print(f'ERRO na leitura de volta: {d}', file=sys.stderr)
        if not resto:
            print('OK: a leitura de volta é igual ao arquivo nos campos graváveis')
        return 1 if resto else 0
    except (FormaNaoReconhecida, ValueError, KeyError) as x:
        print(f'ERRO: {x}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
