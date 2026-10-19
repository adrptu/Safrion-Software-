# -*- coding: utf-8 -*-
"""PA-OPER F1 · versão do plano lida pela O.S. (revisão Codex 6271563229, item 3), em Node, com as funções reais da tela O.S.
(osPlanoVer e osCaldaPlano, extraídas de areas/processo_os.py) e o serviço único operacoes.js. Dados inventados.
  V1 versão pedida que não está guardada nem é a da semente (v5 com a semente na v6): nada volta; a calda fica "pendente",
     nunca a da v6 com o número da v5
  V2 versão da semente (v6): os parâmetros da semente (100 L/ha)
  V3 versão histórica guardada no cenário (v5 = 80 L/ha): a calda dela, não a da semente
Uso (de gen37/): python3 -B pa_oper_versao_test.py   (GEN=<gen37 de outra árvore> roda contra ela; sai 1 se falhar)"""
import os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.environ.get('GEN') or HERE
src = open(os.path.join(GEN, 'areas', 'processo_os.py'), encoding='utf-8').read()
def funcao(nome):
    m = re.search(r'function ' + nome + r'\(.*?\n(?=function |//)', src, re.S)
    if not m: raise SystemExit(f'{nome} não encontrada em processo_os.py')
    return m.group(0)
js = (open(os.path.join(GEN, 'operacoes.js'), encoding='utf-8').read() + '\n' + funcao('osPlanoVer') + funcao('osCaldaPlano') + r"""
const OSD = {nova: {planos: {P: {versao: 6, params: {'Pulverização': {calda: 100}}}}}};
const R = []; const ok = (n, c, info) => { R.push(!!c); console.log((c ? 'OK    ' : 'FALHA ') + n + (c ? '' : ' · ' + JSON.stringify(info))); };
let v = osPlanoVer({}, 'P', 5), cal = osCaldaPlano({}, 'P', 5, 'Pulverização', 'A');
ok('V1 v5 pedida, ausente do cenário, semente na v6: nada volta e a calda fica pendente (nunca 100 L/ha da v6 rotulada v5)', v === null && cal.valor === null && cal.origem === 'pendente', [v, cal]);
cal = osCaldaPlano({}, 'P', 6, 'Pulverização', 'A');
ok('V2 v6 (a da semente): 100 L/ha da operação', cal.valor === 100, cal);
const cc = {pa: {P: {versoes: {5: {params: {'Pulverização': {calda: 80}}, atividades: [{id: 'A'}]}}}}};
cal = osCaldaPlano(cc, 'P', 5, 'Pulverização', 'A');
ok('V3 v5 histórica guardada (80 L/ha): a calda dela, não a da semente', cal.valor === 80, cal);
const n = R.filter(Boolean).length; console.log(`\n${n}/${R.length} OK`); process.exitCode = n === R.length ? 0 : 1;
""")
node = os.environ.get('NODE') or shutil.which('node')
if not node: raise SystemExit('Node indisponível')
run = subprocess.run([node], input=js, text=True, capture_output=True)
print(run.stdout, end=''); print(run.stderr, end='', file=sys.stderr); sys.exit(run.returncode)
