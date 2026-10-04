# gera ACHADO7_TEXTO.md com o texto VERBATIM de rev.json itens[7] (achado e os dois vereditos), sem editar nada
import json,sys,hashlib
src,dst=sys.argv[1],sys.argv[2]
raw=open(src,'rb').read(); d=json.loads(raw); it=d['itens'][7]
L=['# Achado 7: texto exato (rev.json itens[7])','',
   f'Fonte: `{src}` (sha256 {hashlib.sha256(raw).hexdigest()}). Campos copiados sem edição; cada campo vai dentro de um bloco de texto para preservar quebras de linha.','']
a=it['achado']
L+=['## Achado','',f'- lente: `{it.get("lente")}`']
for k in ('titulo','severidade','arquivo','linha','introduzido_pelo_delta'):
    L.append(f'- {k}: `{a.get(k)}`')
for k in ('cenario_de_falha','evidencia','correcao_proposta'):
    L+=['',f'### achado.{k}','','```text',a[k],'```']
for j,v in enumerate(it['vereditos']):
    L+=['',f'## Veredito {j}','']
    for k in ('refutado','reproduzido','severidade','introduzido_pelo_delta'):
        L.append(f'- {k}: `{v.get(k)}`')
    for k in ('comando','saida','fundamento'):
        L+=['',f'### vereditos[{j}].{k}','','```text',v[k],'```']
L+=['','## JSON bruto de itens[7]','','```json',json.dumps(it,ensure_ascii=False,indent=1),'```','']
open(dst,'w').write('\n'.join(L))
# conferência: cada campo de texto aparece byte a byte no arquivo gerado
out=open(dst).read(); falt=[k for k in ('cenario_de_falha','evidencia','correcao_proposta','titulo') if a[k] not in out]+[f'v{j}.{k}' for j,v in enumerate(it['vereditos']) for k in ('comando','saida','fundamento') if v[k] not in out]
print('campos ausentes:',falt or 'nenhum')
