# -*- coding: utf-8 -*-
"""Verificador CD-05 · listagem: filtros por papel, contagem, colunas, cobertura só em Fornecedores, largura e altura por filtro."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
CNT="(()=>{const t=document.querySelectorAll('[role=table]')[0]; const b=t.parentElement.parentElement; const m=b.innerText.match(/(\\d+) de (\\d+)/); return m?m[0]:null;})()"
WID="""(()=>{const out=[]; document.querySelectorAll('[role=table]').forEach(t=>{const p=t.parentElement; out.push([t.scrollWidth,p.clientWidth,t.getBoundingClientRect().right]);}); return out;})()"""
TRUNC="""(()=>{const o=[]; document.querySelectorAll('[role=table] [role=cell] *, h1, header *').forEach(e=>{const cs=getComputedStyle(e); if((cs.overflow==='hidden'||cs.textOverflow==='ellipsis'||cs.overflowX==='hidden') && e.scrollWidth>e.clientWidth+1 && e.innerText) o.push(e.innerText.slice(0,40));}); return o.slice(0,8);})()"""
try:
    t.load()
    t.chk('1 carrega sem erro JS', t.errs()=='', t.errs())
    res={}
    for f,n in [('Todos',17),('Fornecedores',7),('Clientes',5),('Parceiros de crédito',3),('Transportadores',2),('Prestadores',1)]:
        t.fil(f); rs=t.rows(); res[f]=dict(n=len(rs),cnt=t.J(CNT),heads=t.heads(),grades=t.J("document.querySelectorAll('[role=table]').length"),
            need=t.need(),docw=t.J("document.documentElement.scrollWidth"),wid=t.J(WID),trunc=t.J(TRUNC),rows=rs)
    for f,r in res.items(): print(f, {k:v for k,v in r.items() if k!='rows'})
    t.chk('2 filtro mostra o número de linhas da contagem', all(res[f]['n']==n for f,n in [('Todos',17),('Fornecedores',7),('Clientes',5),('Parceiros de crédito',3),('Transportadores',2),('Prestadores',1)]), {f:r['n'] for f,r in res.items()})
    t.chk('3 contador "N de M" da grade acompanha o filtro', all(res[f]['cnt'] in (None,f"{res[f]['n']} de {res[f]['n']}",f"{res[f]['n']} de 17") for f in res), {f:r['cnt'] for f,r in res.items()})
    t.chk('4 colunas comuns fora de Fornecedores', all(['PARCEIRO · CPF/CNPJ','PAPÉIS','CONTATO','SITUAÇÃO DO PAPEL']==[h.split(' ⇅')[0] for h in res[f]['heads']] for f in res if f!='Fornecedores'), res['Todos']['heads'])
    t.chk('5 Fornecedores: Grupos homologados e Homologado + cobertura', [h.split(' ⇅')[0] for h in res['Fornecedores']['heads']]==['PARCEIRO · CPF/CNPJ','GRUPOS HOMOLOGADOS','CONTATO','HOMOLOGADO'] and res['Fornecedores']['grades']==2 and all(res[f]['grades']==1 for f in res if f!='Fornecedores'), res['Fornecedores']['heads'])
    t.chk('6 sem rolagem horizontal e tabela cabe na área', all(r['docw']<=1440 and all(w[0]<=w[1]+1 for w in r['wid']) for r in res.values()), {f:(r['docw'],r['wid']) for f,r in res.items()})
    t.chk('7 altura necessária <= 1480 em todos os filtros', all(r['need']<=1480 for r in res.values()), {f:r['need'] for f,r in res.items()})
    t.chk('8 sem texto cortado nas células', all(not r['trunc'] for r in res.values()), {f:r['trunc'] for f,r in res.items() if r['trunc']})
    print('Clientes:',res['Clientes']['rows']); print('Crédito:',res['Parceiros de crédito']['rows']); print('Transp:',res['Transportadores']['rows']); print('Prest:',res['Prestadores']['rows'])
    print('Forn:',res['Fornecedores']['rows'])
    # ordenar em Fornecedores pela coluna Homologado e voltar para Todos
    t.fil('Fornecedores'); t.J("document.querySelectorAll('[role=table]')[0].querySelector('[aria-label=\"Ordenar por Homologado\"]').click()"); time.sleep(.3)
    a=t.rows(); t.fil('Todos'); b=t.rows()
    t.chk('9 ordenar por Homologado e voltar a Todos: 17 linhas e sem erro', len(b)==17 and t.errs()=='', (len(a),len(b),t.errs()))
    # ordenar por Situação do papel em Todos e ir a Fornecedores
    t.J("document.querySelectorAll('[role=table]')[0].querySelector('[aria-label=\"Ordenar por Situação do papel\"]').click()"); time.sleep(.3)
    t.fil('Fornecedores'); c=t.rows()
    t.chk('10 ordenar por Situação e ir a Fornecedores: 7 linhas e sem erro', len(c)==7 and t.errs()=='', (len(c),t.errs()))
    t.fil('Todos')
    tx=t.J("document.querySelector('[data-root]').innerText")
    t.chk('11 cortes: sem "não é fornecedor" nem nota repetida', 'não é fornecedor' not in tx and tx.count('Não homologado não recebe cotação')==0 and 'Cobertura de cotação' not in tx, '')
finally: t.close()
