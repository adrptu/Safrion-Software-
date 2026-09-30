# -*- coding: utf-8 -*-
"""Mescla o canvas.json gerado com o publicado (lido por último): preserva quadros e chaves que não são do gerador."""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
pub=json.load(open(sys.argv[1])); mine=json.load(open(os.path.join(HERE,'project','canvas.json')))
ours=set(mine['boards'])
extra={k:v for k,v in pub.get('boards',{}).items() if k not in ours}
dx=0
if extra:  # desloca o layout do gerador para a direita dos quadros alheios
    dx=max(v['x']+v['w'] for v in extra.values())+200
    for b in mine['boards'].values(): b['x']+=dx
    for n in mine['notes'].values(): n['x']+=dx
out=dict(pub)
out['boards']={**extra,**mine['boards']}
out['order']=[k for k in pub.get('order',[]) if k in extra]+mine['order']
out['notes']={**{k:v for k,v in pub.get('notes',{}).items() if k not in mine['notes'] and not (v.get('kind')=='title1' and (k.startswith('row') or k.startswith('v_') or k.startswith('o_')))},**mine['notes']}
out['title']=mine['title']; out['launch']=mine['launch']; out['pages']=mine['pages']
out.setdefault('createdOnFiles',mine['createdOnFiles']); out.setdefault('designSystems',[]); out.setdefault('pages',[])
json.dump(out,open(os.path.join(HERE,'project','canvas.json'),'w'),ensure_ascii=False,indent=1)
print('mesclado · quadros alheios preservados:',list(extra),'· deslocamento x:',dx,'· total',len(out['boards']))
