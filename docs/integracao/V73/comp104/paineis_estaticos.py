"""Conta painéis laterais (drawer) com confirmação de texto fixo ('done') no _render, por menu/oculta. Uso: python3 paineis_estaticos.py <gen37> [render]"""
import sys, os, glob, json, collections
G=sys.argv[1]; R=sys.argv[2] if len(sys.argv)>2 else os.path.join(G,'_render'); sys.path.insert(0,G)
import ui37
cont=collections.Counter(); linhas=[]
for f in sorted(glob.glob(os.path.join(R,'*.dc.html'))):
    pg=os.path.basename(f)
    for l in open(f,encoding='utf-8'):
        if l.startswith('const SPEC = '):
            for x in json.loads(l[len('const SPEC = '):].rstrip().rstrip(';')):
                if x.get('type')=='drawer' and x.get('done'):
                    esc='menu' if ui37.menu_item(pg)[0] is not None else 'oculta'
                    cont[esc]+=1; linhas.append(f"{esc}\t{pg[:-8]}\t{x.get('label') or x.get('title','')}\t{x['done']}")
            break
print('painéis estáticos (confirmar com texto fixo):',dict(cont)); print('\n'.join(linhas))
