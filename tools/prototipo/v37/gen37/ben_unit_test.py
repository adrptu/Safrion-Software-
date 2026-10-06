# -*- coding: utf-8 -*-
"""Beneficiamento BEN-1 · testes de unidade das regras (ben.js) no node, sem navegador; espelho em Decimal (ben_massa.py) e fonte única.
Uso: SAFRION_DADOS=sintetico python3 ben_unit_test.py   → uma linha por verificação e 'RESULTADO: OK n/n' no fim.
Casos: docs/beneficiamento/ESPECIFICACAO.md §10.3 (K01..K31) com a caixa formosa de 10 kg (DECISOES.md §12)."""
import os, sys, json, re, subprocess, random
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)


def motor():
    """o mesmo motor das telas: perfis + cenário (CEN0, cenario.js, producao.js, ben.js) + núcleo da O.S. com a carência"""
    import cenario
    from areas.processo_os import JS_NUCLEO
    return 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO


def node(src, nome):
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True); p = os.path.join(HERE, '_probe', nome); open(p, 'w', encoding='utf-8').write(src)
    return subprocess.run(['node', p], capture_output=True, text=True, timeout=180)


def main():
    M = motor()
    r = node(M + open(os.path.join(HERE, 'ben_unit.js'), encoding='utf-8').read(), 'ben_unit_all.js')
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-800:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])
    # espelho Decimal = JS (BigInt): tara, caixas, faixa, balanço, alçada e rateio em casos aleatórios com semente fixa (ESPECIFICACAO §11.3)
    import ben_massa as BM, dados_ben as DB
    par = DB.PACK3['par']; cx = DB.CXD; rnd = random.Random(20261006); casos = []
    for _ in range(400):
        n = rnd.randint(1, 4); ent = [round(rnd.uniform(100, 40000), rnd.choice([0, 1, 3, 6])) for _ in range(n)]; proc = sum(BM.D(str(e)) for e in ent)
        cxs = rnd.randint(1, 4000); pal = rnd.randint(0, 40); sai = [str(round(rnd.uniform(0, float(proc) / 3), rnd.choice([0, 2, 6]))) for _ in range(rnd.randint(1, 4))]
        casos.append(dict(ent=[str(e) for e in ent], proc=str(proc), cx=cxs, pal=pal, sai=sai))
    js = M + 'const CS=' + json.dumps(casos) + ''';
const r=benRota('PACK-FRU|3'); const out=CS.map(k=>{ const o={ben:{rota:'PACK-FRU|3',ent:k.ent.map(kg=>({lote:'X',kg:Number(kg)}))}}; const sai=prSoma(k.sai.map(Number)); const dif=prSub(benEntrada(o),sai); const al=benAlcada(o,dif);
  return {tara:prFmt(benTara(k.cx,k.pal,r),6),cx:benCaixas(benEntrada(o),r),faixa:prFmt(benFaixa(benEntrada(o),r),6),dif:prFmt(dif,6),lim:prFmt(al.lim,6),passa:al.passa,
          rat:prRateio(sai,k.ent.map(Number)).map(x=>prFmt(x,6))}; }); print(JSON.stringify(out));'''
    rr = node(js, 'ben_espelho.js'); res = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.returncode == 0 else []
    f = lambda d: format(BM.q6(d), 'f').replace('-', '−').replace('.', ',')
    def br(d):   # mesma forma de prFmt(x, 6): milhar com ponto, decimal com vírgula, sinal −
        s = format(BM.q6(d), 'f'); neg = s.startswith('-'); s = s.lstrip('-'); i, fr = s.split('.'); i = f'{int(i):,}'.replace(',', '.'); return ('−' if neg else '') + i + ',' + fr
    bad = []
    for k, j in zip(casos, res):
        sai = sum(BM.D(x) for x in k['sai']); proc = BM.D(k['proc']); b = BM.bal(proc, k['sai'], par['tol_pesado']); al = BM.alcada(proc, b['dif'], par['alcada_pct'], par['alcada_kg'])
        esp = dict(tara=br(BM.tara(k['cx'], k['pal'], cx['tara'], par['tara_pallet'])), cx=BM.caixas(proc, par['frac_vend'], cx['massa']), faixa=br(b['faixa']), dif=br(b['dif']),
                   lim=br(al['lim']), passa=al['passa'], rat=[br(x) for x in BM.rateio(sai, k['ent'])])
        if esp != j: bad.append((k, esp, j))
    ok(f'espelho Decimal (ben_massa.py) = JS (BigInt) em {len(casos)} casos: tara, caixas, faixa, diferença, alçada e rateio', rr.returncode == 0 and len(res) == len(casos) and not bad, (rr.stderr[-300:], bad[:1]))
    # nenhum nome global de producao.js, cenario.js ou ben.js redefinido por outro bloco do motor (a tela, a carência ou entre si)
    defs = lambda t: set(re.findall(r'^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', t, re.M)) | set(re.findall(r'(?<![\w.])function\s+([A-Za-z_$][\w$]*)\s*\(', t))
    ben = defs(open(os.path.join(HERE, 'ben.js'), encoding='utf-8').read())
    outros = {n: open(os.path.join(HERE, n), encoding='utf-8').read() for n in ('cenario.js', 'producao.js')}
    outros['dados_carencia.JS'] = __import__('dados_carencia').JS
    from areas import producao as AP
    outros.update({'areas/producao.py:' + k: getattr(AP, k) for k in dir(AP) if k.endswith('_JS') and isinstance(getattr(AP, k), str)})
    try:
        from areas import processo_beneficiamento as AB
        outros.update({'areas/processo_beneficiamento.py:' + k: getattr(AB, k) for k in dir(AB) if k.endswith('_JS') and isinstance(getattr(AB, k), str)})
    except ImportError: pass
    for nome, t in outros.items():
        dup = sorted(ben & defs(t)); ok(f'nomes de ben.js não são redefinidos em {nome}', not dup, dup)
    # fonte única: nenhuma conta de saca nem caixa fixa no ben.js; caixa e tara vêm de dados_cad.EMB_PACK
    src = open(os.path.join(HERE, 'ben.js'), encoding='utf-8').read()
    ok('ben.js sem "/60", sem 20 kg nem tara literal (a caixa vem do cadastro)', '/60' not in src and '20 kg' not in src and '0.6' not in src and '1.2' not in src, '')
    import dados_cad as DC
    ok('CD-04: Igor (responsável de produção) e Marta (qualidade) no cadastro, equipe e8; Igor sem homônimo', sum(p['nome'] == 'Igor' for p in DC.PESSOAS) == 1 and any(p['nome'] == 'Marta' and p['funcao'] == 'Qualidade' for p in DC.PESSOAS) and any(e[0] == 'e8' for e in DC.EQUIPES), '')
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
