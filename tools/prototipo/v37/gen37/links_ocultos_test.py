# Frente F (CTL-1) · links_ocultos_test.py: testes estruturais sem navegador: (a) só a O.S. e o Mapa liberam ordem agrícola (logo, todo caminho grava CMD-42/CMD-06);
# (b) nenhum elo de tela visível para tela oculta e fixa no escopo; o resto da varredura fica numa lista por PAR (origem → destino) com motivo.
import sys, os, re, json, glob
G=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,G); os.chdir(G)   # rode depois de build.py + montar_render.py (lê project/)
OK=[]; FA=[]
def ok(n,c,i=''): (OK if c else FA).append(n); print(('OK   ' if c else 'FALHA'),n,('' if c else '· '+str(i)[:500]))
import areas.processo_os as P, cenario
# (a) código de produto = .py e .js do gerador, sem testes, sondas, reproduções e saídas
fontes=[f for f in glob.glob('*.py')+glob.glob('*.js')+glob.glob('areas/*.py')
        if not re.search(r'test|_unit|unit_|repro|probe|verif|qa37|_lib\.py$',os.path.basename(f))]
src={f:open(f,encoding='utf-8').read() for f in fontes}
cham=sorted(f for f,s in src.items() if re.search(r'\bosc_liberar\(',s))
ok('E1 em todo o código de produto, só a O.S. e o Mapa chamam osc_liberar', cham==['areas/inicio.py','areas/processo_os.py'], cham)
cl=sorted(f for f,s in src.items() if re.search(r'\bcenLiberar\(c',s) and not f.endswith('cenario.js'))
ok('E1b só osc_liberar (processo_os) chama cenLiberar: nenhum atalho libera sem gravar CMD-42/CMD-06', cl==['areas/processo_os.py'], cl)
seed=cenario.seed()['ordens']
ok('E2 nenhuma ordem de beneficiamento ou manutenção em A liberar no cenário (OB-0104 Encerradas)', not [k for k,o in seed.items() if re.match(r'O[BM]-',k) and o['etapa']=='A liberar'])
ops={a['op'] for p in P._nova_ordem_dados()['planos'].values() for a in p['atv']}
ok('E3 "Nova ordem" só emite atividade agrícola do plano', not [o for o in ops if re.search('Benef|Manut|Oficina',o)], sorted(ops))
# (b) elos
PJ=os.path.join(G,'project'); c=json.load(open(os.path.join(PJ,'canvas.json')))
pag={k:v.get('page') for k,v in c['boards'].items()}; oc={k for k,v in pag.items() if v=='ocultos'}
pares=set()
for f in sorted(k for k,v in pag.items() if v=='menu'):
    t=open(os.path.join(PJ,f),encoding='utf-8').read()
    for h in {m.split('#')[0] for m in re.findall(r'([A-Z]{2}-[0-9A-Za-z\-]+\.dc\.html(?:#[^"\'\s<]*)?)',t)} & oc: pares.add((f,h))
p=lambda o,*ds: {(o+'.dc.html',d+'.dc.html') for d in ds}
ESCOPO=(p('IN-04','PL-05','CA-02','CO-06det')|p('OS','CA-02','CO-06det')|p('MA-01','PL-04')|p('MA-02','PL-05det')|p('MA-03','PL-05')|p('MA-04det','PL-05','PL-05det')
        |p('MA-05','MB-09')|p('IR-04','GE-07')|p('MB-01','MB-07','MB-08','MB-09','MB-10')|p('MB-02','MB-08')|p('MB-05','MB-05det','SU-03det'))
ok('L1 nenhum elo do escopo (PL-04/PL-05/PL-05det, CA-02, CO-06det, GE-07, MB-05det, MB-07..MB-10, SU-03det a partir de telas visíveis)', not (pares & ESCOPO), sorted(pares & ESCOPO))
RESIDUAL={  # por PAR: um elo novo, mesmo numa tela já listada, quebra o teste
 **{x:'índice do protótipo: aponta de propósito para módulos ocultos' for x in p('Main','AG-02','BO-01','CA-01','CA-04','CF-01','CO-01','CO-06','GE-01','IN-01','LO-01','LO-02','ON-01','PL-01','PL-05','PT-01','SU-01','SU-07','VE-01')},
 **{x:'vivo (cenário ou MIP), só falta pôr na página visível (build.py VIS_ROWS)' for x in p('MB-01','MB-02det','MB-03x-recibo','MB-06')|p('MB-02','MB-02det','MB-03x-recibo')
    |p('MB-03','MB-02det','MB-03x-recibo')|p('MB-04','MB-03x-recibo')|p('MB-05','MB-03x-recibo')|p('AG-01','MB-06')|p('AG-01det','MB-06')|p('IN-04','MB-06','CO-06')
    |p('PROD','CO-06')|p('MB-07','MB-03x-recibo')|p('MB-10','MB-03x-recibo')},   # colheita (06/10): a avaliação de carência e destino do lote vive na CO-06; MB-07 e MB-10 (no estado) levam aos envios do aparelho como as outras telas do app
 ('MB-01.dc.html','IN-01.dc.html'):'"voltar" do app',
 **{x:'cadeia MIP → diagnóstico e recomendação (frente própria)' for x in p('AG-01','AG-03','AG-03det','AG-04det')|p('AG-01det','AG-03det','AG-04det','AG-06','PL-02')|p('AG-07','AG-04det')|p('IN-04','AG-06')},
 **{x:'detalhe fixo na página visível (frente própria)' for x in p('CA-01det','AG-04','CA-02','CA-04','PL-05','SU-07')|p('CA-01x-os0420','AG-04det','CA-02','CA-03det','PL-05','SU-07')}}
fora=sorted(pares-set(RESIDUAL))
ok('L2 todo o resto da varredura está na lista residual, por par e com motivo', not fora, fora)
import areas.inicio as I, dados_manutencao as DM
a420=[a for a in I._ORD_MAPA if a[0]=='OS-0420'][0][4]
ok('L3 Mapa · OS-0420: o passo vai para a OM-0233 viva (MA-04, visível e com âncora no estado da manutenção), não para PL-05',
   a420 and a420[1]=='MA-04.dc.html#OM-0233' and 'OM-0233' in DM.seed()['oms'] and pag.get('MA-04.dc.html')=='menu', a420)
print('TOTAL',len(OK)+len(FA),'· falhas',len(FA)); sys.exit(1 if FA else 0)
