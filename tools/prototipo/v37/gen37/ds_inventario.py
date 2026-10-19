# -*- coding: utf-8 -*-
"""Inventário de desvios do componente comum (skill padrao-safrion, passo 3; proprietário, 16/10/2026: "toda hora eu preciso ficar te
corrigindo, sobre padrões e outros"). Lista, por arquivo de área:
  css    regras de CSS da área que miram classe do motor (.g2…): estilo local que imita ou anula o componente comum (ex.: CADX_CSS, 01/10)
  tabela tabelas próprias (role="table" fora do motor): não ganham cabeçalho, ordenação, filtro e seta do E.grid
  cartao listas de cartões próprias (class com "card"/"cartao" fora do motor)
Catraca: com --catraca, falha se alguma contagem passar da base gravada (ds_inventario_base.json); --grava grava a base atual.
As exceções aceitas ficam em EXCECOES com o motivo (fala do proprietário ou peça sem equivalente no motor).
Uso (de gen37/): python3 -B ds_inventario.py [--catraca|--grava] [--det]"""
import os, re, sys, json, glob
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, 'ds_inventario_base.json')
# arquivo: motivo (peça sem equivalente no motor; revisar quando o motor ganhar a peça)
EXCECOES = {
    'mapa.py': 'mapa e camadas: peça própria do Mapa (PLA-01), sem tabela do motor',
}
# exceção contada (só aquelas ocorrências, o resto do arquivo segue na catraca): arquivo → (regra, quantas, motivo)
EXC_CONTA = {
    'os_campo.py': ('tabela', 1, 'ficha impressa da OS-0424: documento de papel, sem ordenar nem filtrar (exceção TAB-08 aceita pelo Codex, 6223504783)'),
}
RE_CSS = re.compile(r'([^{}"\'\n]*\.g2[\w-]*[^{}"\'\n]*)\{')
RE_TAB = re.compile(r'role=\\?"table\\?"|role="table"')
RE_CARD = re.compile(r'class=\\?"[^"]*\b(?:[a-z0-9]+-)?(?:card|cartao|cartoes)\b')

def varre():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'areas', '*.py'))):
        nome = os.path.basename(f)
        txt = open(f, encoding='utf-8').read()
        css = [m.group(1).strip() for m in RE_CSS.finditer(txt) if not m.group(1).strip().startswith(('#', 'def ', 'return'))]
        css = [s for s in css if not re.search(r'self\.|const |\|\||;|=>', s)]   # JS (self.state.g2…), não CSS
        css = [s for s in css if re.search(r'\.[a-z][\w-]*\s*[^,]*\.g2', s) or s.startswith('.g2')]
        tab = len(RE_TAB.findall(txt)); card = len(RE_CARD.findall(txt))
        if nome in EXC_CONTA and EXC_CONTA[nome][0] == 'tabela': tab = max(0, tab - EXC_CONTA[nome][1])
        if css or tab or card:
            out[nome] = dict(css=len(css), tabela=tab, cartao=card, exemplos=css[:6], excecao=EXCECOES.get(nome, ''))
    return out

def main():
    r = varre()
    tot = {k: sum(v[k] for v in r.values() if not v['excecao']) for k in ('css', 'tabela', 'cartao')}
    print(f'{"arquivo":34} {"css":>4} {"tabela":>6} {"cartao":>6}  exceção')
    for n, v in sorted(r.items(), key=lambda x: -(x[1]['css'] + x[1]['tabela'] + x[1]['cartao'])):
        print(f'{n:34} {v["css"]:>4} {v["tabela"]:>6} {v["cartao"]:>6}  {v["excecao"]}')
        if '--det' in sys.argv:
            for e in v['exemplos']: print('      ' + e[:150])
    print('TOTAL (sem exceções): ' + ' · '.join(f'{k} {n}' for k, n in tot.items()))
    if '--grava' in sys.argv:
        json.dump(dict(tot=tot, arquivos={n: {k: v[k] for k in ('css', 'tabela', 'cartao')} for n, v in r.items()}), open(BASE, 'w'), indent=1, ensure_ascii=False)
        print('base gravada'); return 0
    if '--catraca' in sys.argv:
        b = json.load(open(BASE))
        sob = []
        for n, v in r.items():
            if v['excecao']: continue
            bb = b['arquivos'].get(n, dict(css=0, tabela=0, cartao=0))
            sob += [f'{n} {k} {bb[k]}→{v[k]}' for k in ('css', 'tabela', 'cartao') if v[k] > bb[k]]
        print('RESULTADO: ' + ('catraca ok' if not sob else 'SUBIU: ' + '; '.join(sob)))
        return 1 if sob else 0
    return 0

if __name__ == '__main__':
    sys.exit(main())
