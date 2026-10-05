# Copia por programa (sem edição) rev.json itens[8]: achado e os dois vereditos, campo a campo.
import json,sys,hashlib
src=sys.argv[1]; d=json.load(open(src)); it=d['itens'][8]
o=[f'# Achado 8 — texto exato (rev.json, itens[8])\n',f'Fonte: `{src}` (sha256 `{hashlib.sha256(open(src,"rb").read()).hexdigest()}`), chave `itens[8]`. Cada campo abaixo é o valor JSON impresso sem edição (bloco de texto). Revisão feita sobre 04bf6f2.\n',
   f'- lente: `{it["lente"]}`\n','## Achado\n']
for k,v in it['achado'].items(): o.append(f'### {k}\n\n```text\n{v}\n```\n')
for n,ve in enumerate(it['vereditos']):
    o.append(f'## Veredito {n} (verif-restricao-falsa-0-{n})\n')
    for k,v in ve.items(): o.append(f'### {k}\n\n```text\n{v}\n```\n')
print('\n'.join(o))
