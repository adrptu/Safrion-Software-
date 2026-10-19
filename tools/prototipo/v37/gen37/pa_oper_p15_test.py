# -*- coding: utf-8 -*-
"""PA-OPER F1 · P15 (migração), sem navegador (docs/integracao/V71/PA-OPER.md, P15 e "Contraprova").
Compara a ponta antes da F1 (P15_BASE, commit; padrão e32ada5e, base da F1) com esta árvore:
  P15a demanda de todas as safras igual (dados2.demanda e dados2.demanda_datada, todos os campos);
  P15b impressão digital do conteúdo dos planos igual (tudo menos o campo novo 'params');
  P15c ajuste c2 preservado (a6|0 = 0,60 L/ha);
  P15d campos novos sem valor de código: só a semente de demonstração (SOJA-AT · Pulverização · calda 100, origem "demonstração");
       nenhuma atividade ganha calda ou alvo por código.
Mutante obrigatório (M1): a cópia desta árvore com a calda preenchida por código em todos os planos tem de reprovar o P15d.
O P15 passa nas duas versões quanto à demanda (a F1 não muda a demanda); a abertura seccionada dos 8 planos e o "Pendente" na tela
estão no pa_oper_test.py (P15e/P15f).
Uso: SAFRION_DADOS=sintetico python3 -B pa_oper_p15_test.py   [P15_BASE=<commit>]"""
import os, sys, json, shutil, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get('P15_BASE') or 'e32ada5e8bcb4e4069571baffa6eb8ccc3d7926a'
OK = []; FAIL = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:1200]), flush=True)
DUMP = r'''
import sys, os, json, hashlib
sys.path.insert(0, os.getcwd())
import dados2 as D2
saf = [s['id'] for s in D2.SAFRAS]
dem = {s: D2.demanda(s) for s in saf}
dat = {s: D2.demanda_datada(s) for s in saf} if hasattr(D2, 'demanda_datada') else {}
cont = [{k: v for k, v in p.items() if k != 'params'} for p in D2.PLANOS]
fp = hashlib.sha256(json.dumps(cont, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
novos = sorted({p['id'] + ':' + a.get('nome', '') + ':' + k for p in D2.PLANOS for a in p['atividades'] for k in ('calda', 'alvo') if k in a})
print(json.dumps(dict(saf=saf, dem=dem, dat=dat, fp=fp, ids=[p['id'] for p in D2.PLANOS], c2=D2.AJUSTES.get('c2'),
                     params={p['id']: p.get('params') for p in D2.PLANOS}, novos=novos), sort_keys=True, ensure_ascii=False, default=str))
'''
def dump(pasta):
    env = dict(os.environ, SAFRION_DADOS='sintetico', PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, '-B', '-c', DUMP], cwd=pasta, env=env, capture_output=True, text=True, timeout=600)
    if r.returncode: raise RuntimeError(r.stderr[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])
SEMENTE = {'SOJA-AT': {'Pulverização': {'calda': 100, 'origem': 'demonstração'}}}
def so_semente(d):
    return all((v or {}) == SEMENTE.get(k, {}) for k, v in d['params'].items()) and not d['novos']
IGN = shutil.ignore_patterns('_render', 'project', '_probe', '_shots', '__pycache__', '*.png', '*.jpg', 'node_modules')
tmp = tempfile.mkdtemp(prefix='p15_')
try:
    raiz = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    V37 = os.path.dirname(HERE); rel = os.path.relpath(V37, raiz)   # o gerador lê arquivos de v37 (catalogo.json, menu.json…)
    arq = subprocess.run(['git', 'archive', BASE, rel], cwd=raiz, capture_output=True, check=True).stdout
    subprocess.run(['tar', '-x', '-C', tmp], input=arq, check=True)
    antes, depois = dump(os.path.join(tmp, rel, 'gen37')), dump(HERE)
    dif = [s for s in sorted(set(antes['saf']) | set(depois['saf'])) if antes['dem'].get(s) != depois['dem'].get(s) or antes['dat'].get(s) != depois['dat'].get(s)]
    chk(f'P15a demanda igual antes e depois nas {len(depois["saf"])} safras ({", ".join(depois["saf"])}), todos os insumos e campos, inclusive por data',
        antes['saf'] == depois['saf'] and not dif and depois['dem'], dif)
    chk(f'P15b impressão digital do conteúdo dos {len(depois["ids"])} planos igual (sem o campo novo "params"): {depois["fp"][:12]}',
        antes['ids'] == depois['ids'] and antes['fp'] == depois['fp'], [antes['fp'], depois['fp'], antes['ids'], depois['ids']])
    chk('P15c ajuste c2 preservado: a6|0 = 0,60 L/ha antes e depois', antes['c2'] == depois['c2'] == {'a6|0': 0.6}, [antes['c2'], depois['c2']])
    chk('P15d campos novos sem valor de código: só a semente de demonstração (SOJA-AT · Pulverização · 100 L/ha); nenhuma atividade com calda ou alvo',
        so_semente(depois), [depois['params'], depois['novos']])
    # ---------------- M1 · mutante: calda preenchida por código em todos os planos ----------------
    mut = os.path.join(tmp, 'mutante', 'v37'); shutil.copytree(V37, mut, ignore=IGN); mut = os.path.join(mut, 'gen37')
    f = os.path.join(mut, 'dados2.py'); s = open(f, encoding='utf-8').read()
    a = "_p.setdefault('params',PARAMS_DEMO.get(_p['id'],{}))"
    assert s.count(a) == 1, 'a linha da migração mudou; ajuste o mutante'
    open(f, 'w', encoding='utf-8').write(s.replace(a, "_p.setdefault('params',{'Pulverização':{'calda':100,'origem':'código'}})"))
    dm = dump(mut)
    chk('M1 contraprova: calda por código em todos os planos reprova o P15d (a demanda segue igual: a calda não entra na demanda de produto)',
        not so_semente(dm) and dm['dem'] == depois['dem'], [k for k, v in dm['params'].items() if v != SEMENTE.get(k, {})][:8])
except Exception as ex:
    chk('roteiro', False, repr(ex)[:1500])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas', flush=True); sys.exit(1 if FAIL else 0)
