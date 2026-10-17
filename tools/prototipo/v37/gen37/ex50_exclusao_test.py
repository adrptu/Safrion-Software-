#!/usr/bin/env python3
"""EX50: gate estrutural anterior à exclusão, sem alterar o render.

python3 ex50_exclusao_test.py --render _render [--json resultado.json]
--self-test executa contraprovas sintéticas, não valida o produto.

A classificação pode conter um único bloco ```ex50-provas com objeto JSON:
{"ID": {"row_sha256": "hash mostrado no relatório", "review": "recibo",
 "proofs": [{"function": "função preservada", "page": "EST.dc.html",
             "id": "elemento", "text": "texto literal do elemento"}]}}
As duas âncoras são opcionais individualmente; ao menos uma é obrigatória.
Para função inexistente a migrar, usar proofs: [] e no_migration: "justificativa".
O recibo deve atestar a cobertura de TODAS as funções/pré-condições da linha;
o programa verifica presença estática, nunca equivalência funcional ou permissão.
Linhas de funções (não páginas) ficam bloqueadas para inspeção específica.
Main permanece preservado pela decisão 6233013087, que supera a tabela antiga.
Referências literais em scripts são conservadoramente potenciais links; não
excluir exceções automaticamente. Links construídos em runtime exigem QA real.
"""
import argparse
import hashlib
import json
import re
import sys
import tempfile
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

DOCS = Path('docs/integracao/V73/pedidos-1710')


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def rows(markdown):
    result = []
    for line in markdown.splitlines():
        cells = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(cells) == 9 and cells[3] == 'Excluir':
            result.append({'id': cells[0], 'row_sha256': digest(line.strip()),
                           'destination': cells[4], 'preserve': cells[5],
                           'before_delete': cells[6]})
    if not result or len({r['id'] for r in result}) != len(result):
        raise ValueError('Tabela Excluir ausente ou IDs duplicados')
    return result


def manifest(markdown):
    blocks = re.findall(r'^```ex50-provas\s*\n(.*?)^```\s*$', markdown, re.M | re.S)
    if not blocks:
        return {}
    if len(blocks) != 1:
        raise ValueError('Exigir exatamente um bloco ex50-provas')
    def unique(pairs):
        d = {}
        for key, value in pairs:
            if key in d:
                raise ValueError('Chave duplicada: ' + key)
            d[key] = value
        return d
    data = json.loads(blocks[0], object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError('ex50-provas precisa ser objeto por ID')
    return data


class Page(HTMLParser):
    """Texto HTML fora de script/style e IDs reais; nunca texto de comentário."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.text = []
        self.ignore = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.ignore += 1
        if not self.ignore:
            attrs = dict(attrs)
            if attrs.get('id'):
                self.ids.add(attrs['id'])

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.ignore:
            self.ignore -= 1

    def handle_data(self, data):
        if not self.ignore:
            self.text.append(data)


def normalize(s):
    return ' '.join(s.split())


def check(render, decisions, proofs):
    files = sorted(render.rglob('*.html'))
    if not files:
        raise ValueError('Render inexistente/vazio: nenhum HTML')
    sources = {p.relative_to(render).as_posix(): p.read_text(encoding='utf-8') for p in files}
    names = {Path(p).name: p for p in sources}
    if len(names) != len(sources):
        raise ValueError('Nomes HTML duplicados no render: destino ambíguo')
    parsed = {p: Page(s) for p, s in sources.items()}
    # A limpeza independe do item: executar uma vez por página.
    reference_lines = {p: unquote(unescape(re.sub(r'<!--.*?-->', '', s, flags=re.S))).splitlines()
                       for p, s in sources.items()}
    results = []
    for row in decisions:
        item = dict(row, errors=[], incoming=[], status='BLOQUEADO')
        results.append(item)
        key = row['id']
        if key == 'Main':
            item['status'] = 'PRESERVAR'
            item['reason'] = 'Decisão 6233013087; página técnica não excluível'
            continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', key):
            item['errors'].append('Função/fragmento: requer verificação específica, não exclusão de página')
            continue
        target = key + '.dc.html'
        if target not in names:
            item['errors'].append('Página de origem ausente: não é prova anterior à exclusão')
        pattern = re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(target) + r'(?![A-Za-z0-9_.-])')
        for path, lines in reference_lines.items():
            if Path(path).name == target:
                continue
            # Decodificar entidades/URL evita ignorar href codificado.
            for number, line in enumerate(lines, 1):
                if pattern.search(line):
                    item['incoming'].append({'page': path, 'line': number})
        if item['incoming']:
            item['errors'].append('Referências potenciais em páginas que ainda existem')
        proof = proofs.get(key)
        if not isinstance(proof, dict):
            item['errors'].append('Destino migrado/cobertura ainda não documentado')
            continue
        if proof.get('row_sha256') != row['row_sha256']:
            item['errors'].append('Prova desatualizada: linha da decisão mudou')
        if not isinstance(proof.get('review'), str) or not proof['review'].strip():
            item['errors'].append('Falta recibo de revisão da cobertura das funções')
        checks = proof.get('proofs')
        if not isinstance(checks, list):
            item['errors'].append('proofs precisa ser lista explícita')
            continue
        if not checks and not str(proof.get('no_migration') or '').strip():
            item['errors'].append('Sem provas nem justificativa de ausência de migração')
        for n, entry in enumerate(checks, 1):
            if not isinstance(entry, dict):
                item['errors'].append('Prova %d inválida' % n)
                continue
            page = entry.get('page')
            anchor, text = entry.get('id'), entry.get('text')
            if (not isinstance(entry.get('function'), str) or not entry['function'].strip()
                    or not any(isinstance(x, str) and x.strip() for x in (anchor, text))):
                item['errors'].append('Prova %d: função e âncora/texto obrigatórios' % n)
                continue
            if page not in sources or Path(page).name == target:
                item['errors'].append('Prova %d: destino ausente ou igual à origem' % n)
                continue
            dom = parsed[page]
            if anchor and anchor not in dom.ids:
                item['errors'].append('Prova %d: ID não encontrado no HTML' % n)
            if text and (not isinstance(text, str) or normalize(text) not in normalize(' '.join(dom.text))):
                item['errors'].append('Prova %d: texto não encontrado fora de script/style' % n)
        if not item['errors']:
            item['status'] = 'ESTRUTURA_OK'
    return {'scope': 'Presença estática e referências literais; não autoriza exclusão nem substitui QA funcional.',
            'render_hashes': {p: digest(s) for p, s in sources.items()}, 'items': results,
            'blocked': sum(x['status'] == 'BLOQUEADO' for x in results)}


def self_test():
    row = {'id': 'OLD', 'row_sha256': 'fixture', 'destination': 'NEW', 'preserve': 'ação', 'before_delete': ''}
    proof = {'OLD': {'row_sha256': 'fixture', 'review': 'fixture sintética', 'proofs': [
        {'function': 'ação', 'page': 'NEW.dc.html', 'id': 'acao', 'text': 'Confirmar'}]}}
    with tempfile.TemporaryDirectory(prefix='ex50-self-') as d:
        root = Path(d)
        (root / 'OLD.dc.html').write_text('<p>Legado</p>')
        (root / 'NEW.dc.html').write_text('<button id="acao">Confirmar</button>')
        def blocked(p=proof):
            return bool(check(root, [row], p)['blocked'])
        assert not blocked(), 'controle positivo'
        assert blocked({}), 'manifesto ausente'
        for field, value in [('row_sha256', 'antigo'), ('review', ''), ('proofs', [])]:
            altered = {'OLD': dict(proof['OLD'], **{field: value})}
            assert blocked(altered), 'prova incompleta aceita: ' + field
        for html in ('<a href="OLD.dc.html#x">Abrir</a>', '<a href="OLD%2Edc%2Ehtml">Abrir</a>',
                     '<script>location.href="OLD.dc.html"</script>'):
            (root / 'IN-04.dc.html').write_text(html)
            assert blocked(), 'link injetado não detectado'
        (root / 'IN-04.dc.html').unlink()
        (root / 'NEW.dc.html').write_text('<script>const x="Confirmar";</script><p id="acao">Outro</p>')
        assert blocked(), 'texto só em script não é prova'
        (root / 'NEW.dc.html').unlink()
        assert blocked(), 'destino ausente'
        main = dict(row, id='Main')
        assert check(root, [main], {})['items'][0]['status'] == 'PRESERVAR'
        assert check(root, [dict(row, id='OS › ação')], {})['blocked'] == 1
        (root / 'OLD.dc.html').unlink()
        try:
            check(root, [row], proof)
        except ValueError:
            pass
        else:
            raise AssertionError('render vazio aceito')
    print('PASS: 13 verificações sintéticas (inclui 3 links injetados, prova desatualizada/incompleta, texto em script, destino/render ausentes, Main e função)')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--render', type=Path)
    parser.add_argument('--anexo', type=Path)
    parser.add_argument('--classificacao', type=Path)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.render:
        parser.error('--render obrigatório')
    repo = next((p for p in Path(__file__).resolve().parents if (p / DOCS).is_dir()), Path.cwd())
    try:
        anexo = (args.anexo or repo / DOCS / 'anexo-telas-ocultas.md').read_text(encoding='utf-8')
        classification = (args.classificacao or repo / DOCS / 'ex50-classificacao-codex.md').read_text(encoding='utf-8')
        report = check(args.render, rows(anexo), manifest(classification))
        report['input_hashes'] = {'anexo': digest(anexo), 'classificacao': digest(classification)}
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.json:
            args.json.write_text(encoded, encoding='utf-8')
        else:
            print(encoded)
        for item in report['items']:
            print(item['status'], item['id'], '; '.join(item['errors']), file=sys.stderr)
        return 1 if report['blocked'] else 0
    except (OSError, ValueError, TypeError) as exc:
        print('BLOQUEADO:', exc, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
