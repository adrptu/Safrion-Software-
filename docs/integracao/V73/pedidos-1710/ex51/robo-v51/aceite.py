"""Portão da medição: ausência ou inconclusão nunca passa por taxa agregada."""
import json, os, re

def avaliar(diretorio, taxas, erros):
    if not isinstance(taxas,dict):taxas={"chegada":taxas}
    casos=[]; bloqueios=[]
    for nome in ('casos-criticos.json','casos-criticos-endereco.json'):
        path=os.path.join(diretorio,nome)
        if not os.path.exists(path):
            bloqueios.append('Execução ausente: '+nome); continue
        data=json.load(open(path,encoding='utf-8'))
        casos.extend(data.get('casos',[]))
        if data.get('naoRodados'): bloqueios.append('Percursos críticos não executados: '+nome)
        if any(o.get('linhas',0)>1000 for o in data.get('origens',[])): bloqueios.append('Inventário truncado: '+nome)
    # Inventário mínimo explícito da candidata; cada linha precisa de prova própria.
    req=[('OS→EST','entregar','OS-0424'),('OS→EST','entregar','OS-0425'),('OS→EST','devolver','OS-0417'),('OS→EST','saldo','OS-0418'),
         ('OS→receituário',None,'OS-0504'),('OS→receituário',None,'OS-0508'),('receituário→OS',None,'VIS-051'),('receituário→OS',None,'VIS-052'),
         ('Aprovações→OS',None,None),('OM→OS',None,'OM-0233'),('OS→OM',None,'OS-0420'),('OS→OM',None,'OS-0431'),('OS→OM',None,'OS-0507')]
    def origem(c,id):
        if id is None:return True
        text=c.get('detalhe') or c.get('visao') or ''
        first=re.search(r'\b[A-Z]+-\d+[A-Z]?\b',text)
        return bool(first and first.group()==id)
    def grupo(c):return c.get('percurso','').replace('OS impedida→OM','OS→OM')
    def passa(c):
        r=c.get('res') or {}
        return bool(r.get('alvo') and not r.get('inconclusivo') and (r.get('abriu') or r.get('destacou')) and r.get('r')=='navega' and r.get('de') and r.get('telaDestino') and r['de']!=r['telaDestino'])
    for g,sub,id in req:
        selected=[c for c in casos if grupo(c)==g and (sub is None or c.get('sub')==sub) and origem(c,id)]
        if not selected or not all(passa(c) for c in selected):bloqueios.append('Crítico ausente ou falhou: '+str((g,sub,id)))
    # RA é uma entidade própria; VIS/REC não substituem as duas direções.
    for reverse in (False,True):
        selected=[c for c in casos if grupo(c)==('receituário→OS' if reverse else 'OS→receituário') and re.search(r'\bRA-\d+', ((c.get('detalhe') or '')+' '+(c.get('visao') or '')) if reverse else str((c.get('res') or {}).get('alvo') or ''))]
        if not selected or not all(passa(c) for c in selected):bloqueios.append('Crítico RA→OS ausente/falhou' if reverse else 'Crítico OS→RA ausente/falhou')
    informativos=[c for c in casos if grupo(c)=='OS→EST' and c.get('sub')=='outro']
    for c in casos:
        if c not in informativos and not passa(c):bloqueios.append('Caso crítico inconclusivo ou falho: '+json.dumps({k:c.get(k) for k in ('percurso','sub','detalhe','visao','el')},ensure_ascii=False))
    for k in ('ids','chegada','volta','voltar'):
        if taxas.get(k) is None or taxas[k]<0.95:bloqueios.append(k+': abaixo de 95% ou sem denominador')
    if erros:bloqueios.append('Há erros de execução')
    return {'estado':'BLOQUEADO' if bloqueios else 'PASSOU_MEDICAO', 'taxas':taxas,'informativos':len(informativos),'criticosExecutados':len(casos),'bloqueios':bloqueios,'limite':'Medição de navegação; não substitui T3/T5, acessibilidade ou aceite integral do produto.'}
