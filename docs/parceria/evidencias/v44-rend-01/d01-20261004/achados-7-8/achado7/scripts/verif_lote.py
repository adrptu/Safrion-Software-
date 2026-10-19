# uso: python3 verif_lote.py <entradas.json> <saida.jsonl> > relatório JSONL (violações por entrada)
import sys,json,math
sys.path.insert(0,sys.path[0]); import verif
L=json.load(open(sys.argv[1]))
for l in open(sys.argv[2]):
    s=json.loads(l); c=L[s['k']]; assert c['nome']==s['nome']
    try: v,th,mo=verif.verifica(c,s)
    except Exception as e: v,th,mo=['ERRO verificador: '+repr(e)],None,'erro'
    print(json.dumps(dict(k=s['k'],nome=s['nome'],cat=c.get('cat'),caminho=s['caminho'],violacoes=v,theta=(None if th is None else ('inf' if th==math.inf else th)),motor=mo),ensure_ascii=False),flush=True)
