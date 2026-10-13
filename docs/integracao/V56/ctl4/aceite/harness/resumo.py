import json,sys
V=json.load(open(sys.argv[1]))
L=V['leituras']
def show(tag,tela):
    x=L.get(tag,{}).get(tela)
    if not x: return
    print(f'--- {tag} · {tela} · expandir={x["expandir"]}')
    for n,rows in x['linhas'].items():
        for r in rows: print('   ',n,'|',json.dumps(r,ensure_ascii=False))
    print('    total_k:',x['total_k']); print('    g2tot:',x['g2tot'],'linha_total:',x['linha_total']); print('    primaria:',x['primaria'])
    for n,m in x['memoria'].items(): print('    memo',n,':',' ¦ '.join(m[5:]))
for tag in ('0_antes','1_apos_devolucao','3_final'):
    for tela in ('SAF','CMP'): show(tag,tela)
for tag in ('0_antes','1_apos_devolucao','2_apos_quarentena'):
    s=L[tag].get('EST_saldos'); print('--- EST saldos',tag,json.dumps(s,ensure_ascii=False)[:1500])
print('--- cen antes',json.dumps(L['0_antes'].get('EST_cenario'),ensure_ascii=False))
for p in ('passo1','passo2'): print('---',p,json.dumps(V[p],ensure_ascii=False)[:2500])
print('--- cen final',json.dumps(L['3_final'].get('EST_cenario'),ensure_ascii=False))
print('erros',V.get('erros_js'))
