# -*- coding: utf-8 -*-
"""Fluxogramas Mermaid do PRD v3.7 reconciliados com as telas do protótipo (IDs preservados)."""
import json, os, re
HERE=os.path.dirname(os.path.abspath(__file__))
F=json.load(open(os.path.join(HERE,'..','fluxos.json')))
CAT=json.load(open(os.path.join(HERE,'..','catalogo.json')))
PROP=json.load(open(os.path.join(HERE,'..','propostas_fluxos.json'))) if os.path.exists(os.path.join(HERE,'..','propostas_fluxos.json')) else {}
files=set(os.listdir(os.path.join(HERE,'project')))
# vínculo por assunto (fluxos cujo capítulo não é citado nas famílias): decidido pelo revisor a partir do conteúdo do fluxo
ASSUNTO={'FL-06':['PL-01','PL-02'],'FL-07':['PL-06','CO-01'],'FL-27':['PL-05','GE-03'],
 'FL-AG-01':['AG-05'],'FL-AG-02':['AG-02','AG-03','AG-04'],'FL-AG-04':['AG-04','CD-03'],'FL-AG-05':['PL-02','AG-04'],
 'FL-AG-06':['PL-02','PL-04','PL-05'],'FL-AG-08':['PL-03','PL-04'],'FL-BEN-01':['CO-04','CO-05','CO-06'],
 'FL-BEN-02':['CO-05','CO-06','CO-07'],'FL-BEN-03':['CO-05','CO-06'],'FL-COM-01':['VE-03','VE-04','VE-05']}
def telas_do_fluxo(fid,src):
    fams=sorted(set(f for f,c in CAT.items() if fid in c.get('fl',[]))|set(ASSUNTO.get(fid,[])))
    cmds=sorted(set(re.findall(r'CMD-\d{2}',src)))
    viacmd=sorted(f for f,c in CAT.items() if set(c.get('cmd',[]))&set(cmds) and f not in fams)
    return fams,viacmd,cmds
L=['# Fluxogramas reconciliados — PRD v3.7 × protótipo v3.7','',
 '**Fonte:** os 56 blocos Mermaid do PRD v3.7 (23/09/2026), copiados sem alteração e com os IDs preservados. Para cada fluxo: onde está no PRD, os comandos que ele usa e as telas do protótipo onde é percorrido (famílias que declaram o fluxo em "Dependências e aceite", e famílias que executam os mesmos comandos).','',
 '**Propostas de alteração:** '+('ver a seção de cada fluxo marcado com ⚑.' if PROP else 'nenhuma proposta de alteração de fluxo pendente nesta entrega; divergências encontradas durante a validação serão registradas aqui com problema, alternativa e decisão necessária.'),'',
 '| # | ID | Seção do PRD | Linha | Comandos | Telas (declaram o fluxo) |','|---|---|---|---|---|---|']
for b in F:
    fams,viacmd,cmds=telas_do_fluxo(b['id'],b['src'])
    L.append(f"| {b['n']} | {'⚑ ' if b['id'] in PROP else ''}{b['id']} | {b['secao'][:60]} | {b['linha']} | {' '.join(cmds) or '—'} | {' '.join(fams) or '—'} |")
L.append('')
for b in F:
    fams,viacmd,cmds=telas_do_fluxo(b['id'],b['src'])
    L.append(f"## {b['n']:02d} · {b['id']} — {b['secao']}")
    L.append(f"PRD linha {b['linha']}.")
    if fams: L.append('**Percorrido nas telas:** '+', '.join(f'`{f}.dc.html` ({CAT[f]["titulo"]})' for f in fams))
    if viacmd: L.append('**Comandos também executados em:** '+', '.join(f'`{f}`' for f in viacmd))
    if not fams and not viacmd: L.append('**Percorrido nas telas:** fluxo de engenharia/implantação ou transversal — sem tela própria no protótipo (validado na futura homologação técnica).')
    if b['id'] in PROP:
        p=PROP[b['id']]; L.append(f"\n⚑ **Proposta pendente:** {p['problema']} · alternativa: {p['alternativa']} · decisão necessária: {p['decisao']}")
    L.append('\n```mermaid\n'+b['src'].rstrip()+'\n```\n')
out=os.path.join(HERE,'..','entrega','Do-talhao-a-OS_v3.7_fluxogramas-reconciliados.md')
open(out,'w').write('\n'.join(L)); print(out,len(F),'fluxos')
sem=[b['id'] for b in F if not telas_do_fluxo(b['id'],b['src'])[0] and not telas_do_fluxo(b['id'],b['src'])[1]]
print('sem tela vinculada:',sem)
