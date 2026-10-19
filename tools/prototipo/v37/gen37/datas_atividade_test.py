"""Paridade EX57 F0a contra funções extraídas das seis fontes originais.

Uso: NODE_BINARY=node python datas_atividade_test.py --base /checkout/gen37
Histórico: --base /checkout --git 68a0fe90 (git show, sem alterar checkout).
Impacto: --cenario /checkout/gen37 --impacto /tmp/impacto.json
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
import re
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


def ler(base, nome, git_ref=None):
    p = base / nome
    if not p.exists():
        p = base / (Path(nome).stem + '.base' + Path(nome).suffix)
    raw = subprocess.run(['git','-C',str(base),'show',git_ref+':tools/prototipo/v37/gen37/'+nome],capture_output=True,check=True,timeout=30).stdout if git_ref else p.read_bytes()
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
    for v in ['safra','solo','ocupacao_js','ocupacao_py','dados2','inicio']:
        out.append(dict(atividade=dict(nome='Teste',op='Adubação',g=dict(tipo='DAPC',dias=2)),cultivo=dict(plantio='2026-01-01',colheita=None,plano='p'),contexto=dict(variante=v,plano={'atividades':[{'nome':'Colheita 1','op':'Colheita 1','g':{'tipo':'DAP','dias':30}},{'nome':'Colheita 2','op':'Colheita 2','g':{'tipo':'DATA','data':'2026-12-01'}}]})))
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,default=Path(__file__).parent);parser.add_argument('--git',dest='git_ref');parser.add_argument('--cenario',type=Path);parser.add_argument('--impacto',type=Path);args=parser.parse_args()
    if args.git_ref and not re.fullmatch(r'[0-9a-fA-F]{7,40}',args.git_ref): parser.error('--git exige SHA de commit (7–40 hex)')
    fontes={n:ler(args.base,n,args.git_ref) for n in HASHES}
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
    testar_canonica()
    if args.cenario:
        assert args.impacto, '--impacto requerido com --cenario'
        impacto(args.cenario,args.impacto)
    print('PASS:',total,'comparações originais; adaptador',len(saida),'; origens; imutabilidade; 3 mutantes detectados')



def testar_canonica():
    def e(tipo, col=None, plano=None, data=None, plantio='2024-02-28', dias=1):
        return dict(atividade={'g':dict(tipo=tipo,dias=dias,data=data)},cultivo=dict(plantio=plantio,colheita=col),contexto=dict(variante='canonica',plano=plano or {'atividades':[]}))
    dap={'atividades':[{'op':'Colheita','g':{'tipo':'DAP','dias':2}}]}
    data={'atividades':[{'op':'Colheita','g':{'tipo':'DATA','data':'2024-03-10'}}]}
    duas={'atividades':dap['atividades']+data['atividades']}
    entradas=[e('DAP'),e('DAP',dias=-1),e('DAPC'),e('DANC'),e('DATA'),e('DATA',data='2026-01-01'),e('DAPC',plano=dap),e('DAPC',plano=data),e('DANC',plano=data),e('DAPC',col='2024-03-20',plano=dap),e('DAPC',plano=duas),e('DAPC',plano=data,plantio=None),e('DAPC',plano=dap,plantio=None),e('DAP',plantio=None),e('DESCONHECIDO')]
    esperado=[('2024-02-29','plantio'),('2024-02-27','plantio'),(None,'ancora_ausente'),(None,'ancora_ausente'),(None,'data_ausente'),('2026-01-01','data_fixa'),('2024-03-02','colheita_plano_dap'),('2024-03-11','colheita_plano_data'),('2024-03-09','colheita_plano_data'),('2024-03-21','colheita_informada'),('2024-03-02','colheita_plano_dap'),('2024-03-11','colheita_plano_data'),(None,'ancora_ausente'),(None,'ancora_ausente'),(None,'gatilho_desconhecido')]
    anterior=os.environ.get('TZ')
    try:
        for zona in ['UTC','America/Sao_Paulo','Pacific/Kiritimati']:
            os.environ['TZ']=zona
            out=calcular_lote(entradas)
            assert [(r['data'],r['origem']) for r in out]==esperado,(zona,out)
    finally:
        if anterior is None:os.environ.pop('TZ',None)
        else:os.environ['TZ']=anterior
    print('canonica: 45 regressões PASS (C3, divergências 2/4, primeira Colheita, sem data)')


def impacto(cenario, destino):
    """Cenário sintético do repositório, nunca dados de cliente. Não gera O.S.

    --cenario aponta gen37 da base; importa dados2 com dependências locais.
    Relatório JSON contém todas as alterações (inclusive impacto zero por variante).
    Fora do recorte de safra não é filtrado nem corrigido nesta fatia.
    """
    import sys
    import importlib.util
    import collections
    sys.path.insert(0,str(cenario.resolve()))
    try:
        spec=importlib.util.spec_from_file_location('_cenario_ex57',cenario/'dados2.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    finally:sys.path.pop(0)
    entradas=[]; chaves=[]
    for safra,cultivos in mod.CULTIVOS.items():
        for c in cultivos:
            pl=mod.PLANO.get(c.get('plano'))
            if not pl:continue
            for a in pl['atividades']:
                for variante in ['safra','solo','ocupacao_js','ocupacao_py','dados2','inicio']:
                    base=dict(atividade=a,cultivo=c,contexto=dict(variante=variante,plano=pl))
                    nova=copy.deepcopy(base);nova['contexto']['variante']='canonica'
                    entradas.extend([base,nova]);chaves.append(dict(safra=safra,cultivo=c['id'],plano=pl['id'],atividade=a.get('id',a.get('nome')),variante=variante))
    rel=dict(fontes_sha256={n:hashlib.sha256((cenario/n).read_bytes()).hexdigest() for n in ['dados2.py','dados_lagoa_safra.py']},comparacoes_por_fuso=len(chaves),fusos={})
    anterior=os.environ.get('TZ')
    try:
        for zona in ['UTC','America/Sao_Paulo','Pacific/Kiritimati']:
            os.environ['TZ']=zona;out=calcular_lote(entradas);mudancas=[];cont=collections.Counter()
            for i,chave in enumerate(chaves):
                ant,novo=out[2*i:2*i+2]
                if ant['data']==novo['data']:continue
                ref='C3' if novo['origem']=='ancora_ausente' or ant['origem']=='sem_ancora' else ('divergencia_2' if chave['variante']=='dados2' else 'divergencia_4')
                mudancas.append(dict(chave,antes=ant,depois=novo,referencia=ref));cont[chave['variante']]+=1
            rel['fusos'][zona]=dict(contagem={v:cont[v] for v in ['safra','solo','ocupacao_js','ocupacao_py','dados2','inicio']},mudancas=mudancas)
    finally:
        if anterior is None:os.environ.pop('TZ',None)
        else:os.environ['TZ']=anterior
    destino.write_text(json.dumps(rel,ensure_ascii=False,indent=2)+'\n')
    print('impacto:',rel['comparacoes_por_fuso'],'por fuso', {z:r['contagem'] for z,r in rel['fusos'].items()})


if __name__=='__main__':main()
