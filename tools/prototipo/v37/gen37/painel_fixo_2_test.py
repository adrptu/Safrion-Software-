"""Verificação local proporcional; requer runtime gen37 e base recuperada. Não abre navegador."""
import ast, importlib.util, json, pathlib, subprocess, sys, tempfile, re
runtime, base = map(pathlib.Path, sys.argv[1:3])
draft = pathlib.Path(sys.argv[4]) if len(sys.argv)>4 else runtime/'areas'
sys.path.insert(0, str(runtime))
import engine as E
counts = {}
for kind, src in [('base', base), ('draft', draft)]:
    with tempfile.TemporaryDirectory() as out:
        E.P = out
        for name, funcs in [('campo', ['_ca02']), ('gestao', ['_ge02', '_ge03', '_ge08'])]:
            ast.parse((src / (name+'.py')).read_text())
            spec = importlib.util.spec_from_file_location('pf2_'+kind+name, src/(name+'.py'))
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            m.__file__ = str(runtime/'areas'/(name+'.py'))  # dependência credito_docs do runtime
            for f in funcs: getattr(m, f)()
        panels = 0; previews = []
        for p in pathlib.Path(out).glob('*.dc.html'):
            line = next(l for l in p.read_text().splitlines() if l.startswith('const SPEC = '))
            items = json.loads(line[len('const SPEC = '):].rstrip(';'))
            panels += sum(x.get('type') == 'drawer' for x in items)
            previews += [msg for x in items for msg in x.get('msgs', []) if msg.startswith('Prévia · nada foi alterado.')]
        counts[kind] = panels
        if kind == 'draft': assert len(previews) == 4
assert counts == {'base': 4, 'draft': 0}, counts
for name in ['campo.py', 'gestao.py']:
    old, new = (base/name).read_text(), (draft/name).read_text()
    assert [l for l in old.splitlines() if 'x0=' in l] == [l for l in new.splitlines() if 'x0=' in l]
p = (draft/'gestao.py').read_text()
assert 'PP-014' not in p and 'DDID' not in p
fn = re.search(r'function docSit\(self,V\)\{[\s\S]*?(?=function PREVALS)', p).group()
js = 'const assert=require("node:assert/strict"); const HOJE_DOC="2026-09-23";'+fn+'''
for(const added of [{},{qualquer:true}]) {
 const self={state:{added}};
 assert.deepEqual(docSit(self,{id:'dc_cert_SR',num:'',pend:'Condição'}),['Pendente','yellow']);
 assert.deepEqual(docSit(self,{num:'123',val:'2026-09-22'}),['Vencido','red']);
 assert.deepEqual(docSit(self,{num:'123',val:'2026-09-24'}),['Registrado','green']);
 assert.deepEqual(docSit(self,{num:'123',tipo:'Contrato de arrendamento'}),['Vigente','green']);
}
'''
subprocess.run([sys.argv[3] if len(sys.argv)>3 else 'node', '-e', js], check=True)
print('PASS: AST; cinco páginas geradas; painéis afetados 4→0; quatro prévias; oito estados documentais; x0 preservados. Sem navegador ou contagem global.')
