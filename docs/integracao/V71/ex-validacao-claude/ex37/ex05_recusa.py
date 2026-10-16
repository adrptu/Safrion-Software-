# -*- coding: utf-8 -*-
"""EX-05 "Ativas que só recusam depois do clique": para cada (tela, rótulo) abre a tela no estado inicial (perfil Ana),
registra se o botão está visível/ativo/verde e a dica, clica e registra o aviso (role=status / toast) e o diálogo aberto.
Se abrir diálogo, clica também a primária do diálogo (sem preencher) e registra a recusa. Saída: ex05_recusa.json + capturas."""
import json, time, re, sys
from lib import *
CASOS = [('GE-03', 'Fechar competência'), ('CA-02', 'Encerrar'), ('CA-04', 'Confirmar recebimento'),
         ('SU-07', 'Confirmar entrega'), ('SU-07', 'Separar FEFO'), ('SU-02', 'Publicar vigência'), ('SU-09', 'Submeter ajuste'),
         ('PL-01', 'Autorizar execução'), ('PL-01', 'Encerrar período'), ('AG-05', 'Publicar'), ('OS-0424-app', 'Retirar')]
if len(sys.argv) > 2: CASOS = [(sys.argv[1], sys.argv[2])]
INFO = r"""((t)=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{ const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const els=[...document.querySelectorAll('button,a,[role=button]')].filter(e=>vis(e)&&!e.closest('[role=dialog]'));
 const m=els.filter(e=>n(e.innerText)===t||n(e.innerText).startsWith(t));
 return m.map(e=>({t:n(e.innerText).slice(0,70),dis:!!e.disabled||e.getAttribute('aria-disabled')==='true',verde:getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)',title:n(e.title||e.getAttribute('aria-description')||'').slice(0,200),desc:(()=>{const id=e.getAttribute('aria-describedby'); const d=id&&document.getElementById(id); return d?n(d.innerText).slice(0,200):'';})()})); })"""
TOAST = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); return [...document.querySelectorAll('[role=status],[role=alert],[aria-live]')].map(e=>n(e.innerText)).filter(Boolean).join(' | ').slice(0,600); })()"""
res = []
c = novo()
try:
    for tela, rot in CASOS:
        abre(c, tela)
        info = c.js(f"({INFO})({json.dumps(rot)})")
        t0 = c.js(TOAST)
        r = clica(c, rot); time.sleep(.6)
        t1 = c.js(TOAST); dl = resume_dlg(dialogo(c))
        nome = re.sub(r'\W+', '_', f'{tela}_{rot}')
        cap1 = shot(c, 'ex05_' + nome)
        prim = None; t2 = None; dl2 = None
        if dl and dl[0]['verdes']:
            prim = dl[0]['verdes'][-1]
            c.js(f"""(()=>{{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const b=[...d.querySelectorAll('button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').pop(); b&&b.click();}})()""")
            time.sleep(.8); t2 = c.js(TOAST); dl2 = c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); return d?d.innerText.replace(/\\s+/g,' ').slice(0,700):null;})()")
            shot(c, 'ex05_' + nome + '_primaria')
        res.append(dict(tela=tela, rotulo=rot, antes=info, aviso_antes=t0, clique=r, aviso_depois=t1, dialogo=dl, primaria_dialogo=prim, aviso_primaria=t2, dialogo_apos_primaria=dl2, cap=cap1))
        print(json.dumps(res[-1], ensure_ascii=False)[:1500]); print()
finally:
    c.close()
json.dump(res, open(os.path.join(EX, 'ex05_recusa.json' if len(sys.argv) <= 2 else f'ex05_{re.sub(chr(92)+"W+","_",sys.argv[1]+sys.argv[2])}.json'), 'w'), ensure_ascii=False, indent=1)
