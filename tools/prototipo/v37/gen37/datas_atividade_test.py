"""Paridade EX57 F0a contra funções extraídas das seis fontes originais.

Uso: NODE_BINARY=node python datas_atividade_test.py --base /checkout/gen37
Base do contrato: 68a0fe90cec749353bf42f37751b4005413a3098.
Não importa os geradores (evita efeitos colaterais); AST/VM executam as funções
originais. Aceita também os snapshots *.base.* para reprodução local.

Divergências preservadas, sem escolher regra por maioria:
1. Sem colheita informada, inicio retorna None; outras cópias derivam/fallback.
2. Colheita do plano DATA: dados2 ignora e recai no plantio; safra/solo/ocupação usam DATA.
3. Sem colheita no plano: cinco variantes usam plantio; inicio continua None.
4. safra soma em horário local e serializa UTC; outras em dia civil/UTC.
   Pacific/Kiritimati torna a diferença observável; não corrigida em F0a.
Retorno normalizado ISO|None; wrappers de ocupação continuam responsáveis pela
conversão de dias inteiros e pelo caso plano inexistente (lista vazia).
processo_os/planos formatam/validam gatilhos; patest/verif_pa são testes de UI,
não outras funções de cálculo de data. Sem alteração destes consumidores.
"""
import argparse
import ast
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datas_atividade import calcular_lote

HASHES = {
    'safra.js': '2514af963a011bc3377dfdf2ae0d4132a2063615',
    'solo.js': '5f001b784b7a0334175813ea483df00db8c9da6c',
    'ocupacao.js': '9ab43a91a0928ea02a9daa035e501cf5ae53b1fa',
    'ocupacao.py': '6cbc245e2696ca4f4d2b466a20130d206907a280',
    'dados2.py': '035a44e030aa07981c46645e6567919772fe5211',
    'areas/inicio.py': '349c02181b751d0d00a42aaf28c388c8118f5e0a',
}


def ler(base, nome):
    p = base / nome
    if not p.exists():
        p = base / (Path(nome).stem + '.base' + Path(nome).suffix)
    raw = p.read_bytes()
    def blob(b):
        return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
    if blob(raw) != HASHES[nome] and raw.endswith(b'\n') and blob(raw[:-1]) == HASHES[nome]:
        raw = raw[:-1]  # snapshot local com LF adicional; hash final obrigatório
    assert blob(raw) == HASHES[nome], ('base divergente', nome, blob(raw))
    return raw.decode()


def funcoes_py(texto, nomes, ns):
    arv = ast.parse(texto)
    funcoes = [n for n in arv.body if isinstance(n, ast.FunctionDef) and n.name in nomes]
    assert {n.name for n in funcoes} == set(nomes)
    exec(compile(ast.Module(body=funcoes, type_ignores=[]), '<base verificada>', 'exec'), ns)
    return ns


JS = r"""
const fs=require('fs'), vm=require('vm'), assert=require('assert');
const p=JSON.parse(fs.readFileSync(0,'utf8'));
function extrair(s,n){
 const start=s.indexOf('function '+n+'('); assert(start>=0,n);
 let i=s.indexOf('{',start), level=1, end=i+1;
 // Estas funções verificadas não contêm chaves em strings/comentários.
 for(;level&&end<s.length;end++){if(s[end]==='{')level++;if(s[end]==='}')level--;}
 assert.equal(level,0);return s.slice(start,end);
}
function contexto(file,names){const c={};vm.createContext(c);vm.runInContext(names.map(n=>extrair(p.fontes[file],n)).join('\n'),c);return c;}
const saf=contexto('safra.js',['iso','addDays','colheitaDe','dataAtv']);
const sol=contexto('solo.js',['soloMaisDias','soloDataAtv']);
const ocu=contexto('ocupacao.js',['ocDia','ocColheitaPlano','ocAtividades']);
const kernel={};vm.createContext(kernel);vm.runInContext(p.kernel,kernel);
const out=p.casos.map(e=>{
 const a=e.atividade,c=e.cultivo,pl=e.contexto.plano,v=e.contexto.variante;
 let esperado;
 if(v==='safra')esperado=saf.dataAtv({v:c},a,pl);
 if(v==='solo')esperado=sol.soloDataAtv(c,a,pl);
 if(v==='ocupacao_js'){
  const plano={...pl,atividades:[...pl.atividades,a]};
  const d=ocu.ocAtividades({planos:{p:plano}},ocu.ocDia(c.plantio),'p',ocu.ocDia(c.colheita)).slice(-1)[0][2];
  esperado=new Date(d*86400000).toISOString().slice(0,10);
 }
 const antes=JSON.stringify(e),r=kernel.daDataAtividade(a,c,e.contexto);
 assert.equal(JSON.stringify(e),antes,'imutabilidade');
 if(esperado!==undefined)assert.equal(r.data,esperado,JSON.stringify(e));
 return r;
});
process.stdout.write(JSON.stringify(out));
"""


def casos():
    out=[]
    for plantio in ['2019-01-15','2024-02-28','2024-02-29','2026-12-31','1969-12-31']:
        for colheita in [None, '', '1970-01-01', '2026-10-15']:
            for gat_col in [None, {'tipo':'DAP','dias':270}, {'tipo':'DATA','data':'2026-09-30'}, {'tipo':'DANC','dias':5}]:
                plano={'id':'p','atividades': [] if gat_col is None else [dict(nome='Colher',op='Colheita mecanizada',g=gat_col)]}
                for tipo in ['DAP','DANC','DAPC','DATA']:
                    for dias in [-180,0,1,30,400]:
                        for variante in ['safra','solo','ocupacao_js','ocupacao_py','dados2','inicio']:
                            out.append(dict(atividade=dict(nome='Teste',op='Adubação',g=dict(tipo=tipo,dias=dias,data='2027-02-28')),
                                            cultivo=dict(plantio=plantio,colheita=colheita,plano='p'),contexto=dict(variante=variante,plano=plano)))
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,default=Path(__file__).parent);args=parser.parse_args()
    fontes={n:ler(args.base,n) for n in HASHES}
    inicio=funcoes_py(fontes['areas/inicio.py'],['_iso','_data_atv'],dict(_dt=dt))
    dados=funcoes_py(fontes['dados2.py'],['data_atividade'],dict(_dt=dt,ddate=dt.date.fromisoformat))
    ocu=funcoes_py(fontes['ocupacao.py'],['dia','_colheita_plano','atividades'],dict(_dt=dt,_EPOCH=dt.date(1970,1,1)))
    entradas=casos();antes=copy.deepcopy(entradas)
    kernel=Path(__file__).with_name('datas_atividade.js').read_text()
    node=os.environ.get('NODE_BINARY','node')
    def executar(fonte, zona):
        return subprocess.run([node,'-e',JS],input=json.dumps(dict(fontes=fontes,kernel=fonte,casos=entradas)),
            env=dict(os.environ,TZ=zona),text=True,capture_output=True,timeout=30)
    def conferir_python(saidas, zona):
        for e,r in zip(entradas,saidas):
            v=e['contexto']['variante'];a=e['atividade'];c=e['cultivo'];pl=e['contexto']['plano']
            if v=='inicio':esperado=inicio['_data_atv'](c,a)
            elif v=='dados2':
                dados['PLANO']={'p':pl};esperado=dados['data_atividade'](c,a)
            elif v=='ocupacao_py':
                plano=dict(pl,atividades=pl['atividades']+[a])
                d=ocu['atividades']({'planos':{'p':plano}},ocu['dia'](c['plantio']),'p',ocu['dia'](c['colheita']))[-1][2]
                esperado=dt.date(1970,1,1)+dt.timedelta(days=d)
            else:continue
            assert r['data']==(esperado.isoformat() if esperado else None),(zona,e,r,esperado)
    total=0
    for zona in ['UTC','America/Sao_Paulo','Pacific/Kiritimati']:
        proc=executar(kernel,zona);assert proc.returncode==0,proc.stderr
        conferir_python(json.loads(proc.stdout),zona)
        total+=len(entradas)
        print(zona,len(entradas),'comparações PASS')
    saida=calcular_lote(entradas);assert entradas==antes
    assert len(saida)==len(entradas)
    conferir_python(saida,'adaptador Python')
    # Metadados/origens independentes da paridade (não inferidos do próprio núcleo).
    a={'g':{'tipo':'DAPC','dias':30}};c={'plantio':'2019-01-15'}
    pl={'atividades':[{'op':'Colheita','g':{'tipo':'DATA','data':'2026-09-30'}}]}
    amostra=calcular_lote([dict(atividade=a,cultivo=c,contexto=dict(variante=v,plano=pl)) for v in ['solo','dados2','inicio']])
    assert [(x['data'],x['origem']) for x in amostra]==[
        ('2026-10-30','colheita_plano_data'),('2019-02-14','fallback_plantio_legado'),(None,'sem_ancora')]
    for antigo,novo in [("variante !== 'dados2'","true"),("!cultivo.colheita","false"),("variante === 'safra'","false")]:
        assert antigo in kernel
        mutante=kernel.replace(antigo,novo)
        # Inclui oráculos Python para mutações que apenas os afetam.
        p=executar(mutante,'Pacific/Kiritimati')
        detectado=p.returncode!=0
        if not detectado:
            try: conferir_python(json.loads(p.stdout),'mutante')
            except AssertionError: detectado=True
        assert detectado,('mutação não detectada',antigo)
    print('PASS:',total,'comparações originais; adaptador',len(saida),'; origens; imutabilidade; 3 mutantes detectados')


if __name__=='__main__':main()
