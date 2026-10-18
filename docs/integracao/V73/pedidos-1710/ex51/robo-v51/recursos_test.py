"""Prazo do script real com recursos substitutos; não abre Chrome."""
import pathlib,tempfile,subprocess,sys,json,hashlib
base=pathlib.Path(__file__).parent
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);(p/'robo-v5-isolado.html').write_text('fixture');(p/'saida-isolado').mkdir()
 (p/'v3.sha256').write_bytes(b'fixture')
 (p/'saida-isolado/execucao-v51.json').write_text(json.dumps({'execucao':'teste','renderManifestSha256':hashlib.sha256(b'fixture').hexdigest()}))
 fake=p/'fake.py'
 fake.write_text('''import time,pathlib
CHROME='substituto'
def esperar_vaga(): pass
def log(s): pass
def limpar_origem(*a): pass
class Aba:
 def goto(self,*a,**k): return True
 def js(self,*a,**k): time.sleep(2)
class Chrome:
 def __init__(self,*a): self.abas=[Aba()]; self.p=type('P',(),{'pid':0})()
 def close(self): pathlib.Path(__file__).with_name('chrome-fechado').touch()
class Servidores:
 def subir(self,*a): return 'http://fixture'
 def parar(self): pathlib.Path(__file__).with_name('servidor-fechado').touch()
''')
 r=subprocess.run([sys.executable,'-I',str(base/'casos_criticos.py'),'--rodar',str(fake),'--trabalho',d,'--saida',str(p/'resultado.json'),'--limite-seg','.05'],capture_output=True,text=True,timeout=5)
 assert r.returncode!=0 and 'TimeoutError' in r.stderr,r
 assert (p/'chrome-fechado').exists() and (p/'servidor-fechado').exists()
 assert not (p/'resultado.json').exists()
print('PASS prazo encerra ambos recursos e não produz recibo de sucesso; recursos substitutos')
import ast,os,shutil
source=(base/'rodar.py').read_text();tree=ast.parse(source)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fase_resumo')
seen=[]
ctx={'os':os,'shutil':shutil,'json':json,'resumir':lambda trab,saida,dest:seen.append(set(os.listdir(saida)))}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<resumo>','exec'),ctx)
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d,'saida-isolado');p.mkdir()
 names={'OS.v5.json','OS.v5err.json','casos-criticos.json','casos-criticos-endereco.json','execucao-v51.json'}
 for name in names|{'leva-check.json'}:(p/name).write_text('{}')
 ctx['fase_resumo'](d,['isolado'])
 assert seen[1]==names,seen
print('PASS primeira passada conserva recibos, vínculo e erros, exclui somente segunda passada')
