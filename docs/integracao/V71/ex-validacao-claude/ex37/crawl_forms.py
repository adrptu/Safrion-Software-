# -*- coding: utf-8 -*-
"""Robô de formulários (só leitura do protótipo; nada é gravado no repositório).
Para cada tela: cada botão candidato (inventário inv_botoes_*.json, sem filtros/visões/ordenação/contadores) é clicado numa
página nova (Main → limpa storage → perfil Ana → tela). Se abrir um diálogo com campo editável, registra o formulário:
título, campos visíveis por tipo e rótulo, marca de obrigatório (* no rótulo, required, aria-required), botões e verdes.
⋯ da linha: abre o menu e repete para cada item. Também a 1ª linha clicável de cada tabela.
Uso: EXCH=CHROME|CHROME2 python3 crawl_forms.py k n   (telas k::n)  → forms_k.jsonl"""
import json, time, os, sys, re
from lib import *

k, nparte = int(sys.argv[1]), int(sys.argv[2])
inv = {}
for i in (0, 1): inv.update(json.load(open(os.path.join(EX, f'inv_botoes_{i}.json'))))
RUIDO = re.compile(r'^(Filtrar|i|ⓘ|Colunas|Cartões|Tabela|Kanban|Lista|Matriz|Mapa|Calendário|Agrupar|Todas|Todos|Restaurar|Recolher|Expandir|Limpar|Por |Até |Hoje|Esta|Só |Sem |Com |Em |A |Ativos|Vencidas|Prevista|Encerradas|Liberadas|Aguardam|▾|‹|›|×|Fechar|Cancelar|Voltar|Anterior|Próxim|Trocar safra|Ver |Abrir |Baixar|Exportar|Imprimir|Pausar|Saca|DATA|\d)')
SAIDA = os.path.join(EX, f'forms_{k}.jsonl')

FORM = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const vis=e=>{ const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const ds=[...document.querySelectorAll('[role=dialog]')].filter(vis);
 return ds.map(d=>{ const lab=e=>{ let l=e.id&&document.querySelector('label[for="'+CSS.escape(e.id)+'"]'); if(!l) l=e.closest('label'); let t=l?n(l.innerText):'';
     if(!t){ const p=e.closest('div'); const pl=p&&p.previousElementSibling; t=n(e.getAttribute('aria-label')||(pl&&pl.innerText)||(p&&p.innerText)||e.placeholder||''); } return t.slice(0,70); };
   const ins=[...d.querySelectorAll('input,select,textarea')].filter(e=>e.type!=='hidden'&&vis(e)&&!/busca|buscar|search/i.test((e.placeholder||'')+(e.getAttribute('aria-label')||'')+e.type));
   const campos=ins.map(e=>({tipo:e.tagName==='INPUT'?e.type:e.tagName.toLowerCase(),lab:lab(e),req:!!e.required||e.getAttribute('aria-required')==='true',ast:/\*/.test(lab(e)),ro:!!e.readOnly||!!e.disabled,val:(e.type==='checkbox'||e.type==='radio')?(e.checked?'✓':''):(e.value||'').slice(0,40)}));
   const bts=[...d.querySelectorAll('button')].filter(vis).map(b=>({t:n(b.innerText||b.getAttribute('aria-label')).slice(0,60),verde:getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)',dis:!!b.disabled||b.getAttribute('aria-disabled')==='true'}));
   const h=d.querySelector('h1,h2,h3'); return {titulo:n((h&&h.innerText)||d.getAttribute('aria-label')).slice(0,90),modal:d.getAttribute('aria-modal')==='true',campos,bts,txt:n(d.innerText).slice(0,600)}; }); })()"""

CLK = r"""((t,menu)=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const vis=e=>{ const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const sel=menu?'[role=menu] [role=menuitem],[role=menu] button,[role=menu] a':'button,[role=button],a[href]';
 const els=[...document.querySelectorAll(sel)].filter(e=>vis(e)&&(menu||!e.closest('[role=dialog],.menu-lat,nav[aria-label],[role=tablist]')));
 const e=els.find(e=>(n(e.innerText)||n(e.getAttribute('aria-label'))||n(e.title))===t); if(!e) return null; e.scrollIntoView({block:'center'}); e.click(); return n(e.innerText||e.getAttribute('aria-label')).slice(0,60); })"""
MENU = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const m=[...document.querySelectorAll('[role=menu]')].filter(e=>e.getClientRects().length);
 return m.flatMap(x=>[...x.querySelectorAll('[role=menuitem],button,a')].map(b=>n(b.innerText||b.getAttribute('aria-label')))).filter(Boolean); })()"""
LINHA = r"""(()=>{ const vis=e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1; };
 const r=[...document.querySelectorAll('main [role=row], main tbody tr')].filter(x=>vis(x)&&!x.querySelector('[role=columnheader],th')&&getComputedStyle(x).cursor==='pointer')[0];
 if(!r) return null; r.scrollIntoView({block:'center'}); const c=r.querySelector('[role=cell]:nth-child(2),td:nth-child(2)')||r; c.click(); return r.innerText.replace(/\s+/g,' ').slice(0,80); })()"""

def registra(rec):
    with open(SAIDA, 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')

def tenta(c, tela, passos):
    abre(c, tela); url0 = c.js('location.href')
    feito = []
    for tipo, alvo in passos:
        if tipo == 'btn': r = c.js(f"({CLK})({json.dumps(alvo)},false)")
        elif tipo == 'menu': r = c.js(f"({CLK})({json.dumps(alvo)},true)")
        else: r = c.js(LINHA)
        feito.append(r); time.sleep(.75)
        if r is None: return {'tela': tela, 'passos': passos, 'erro': 'não achou', 'feito': feito}
    url1 = c.js('location.href')
    d = c.js(FORM) or []
    out = {'tela': tela, 'passos': passos, 'feito': feito, 'nav': url1 if url1.split('#')[0] != url0.split('#')[0] else None, 'dlg': d}
    if any(x['campos'] for x in d):
        nome = re.sub(r'\W+', '_', tela + '_' + '_'.join(str(a) for _, a in passos))[:80]
        out['cap'] = shot(c, 'form_' + nome)
    return out

telas = sorted(inv)[k::nparte]
FEITOS = set()
if os.path.exists(SAIDA):
    for l in open(SAIDA):
        x = json.loads(l); ps = x['passos']
        if len(ps) == 1: FEITOS.add((x['tela'], ps[0][1]))
c = novo()
try:
    for tela in telas:
        cands = [b['t'] for b in inv[tela] if not RUIDO.match(b['t']) and len(b['t']) < 60 and not b['dis']]
        cands = [t for t in cands if not re.search(r'\s\d+$', t)]
        cands = [t for t in cands if not re.fullmatch(r'(OS|OM|PM|NC|INSP|SM|CG|PV|PC|VIS|DIA|REC|LAU|CT|SOL|COT|REQ|RM|ROM|LO|EF)-[\w-]+.*', t)]
        for t in cands:
            if (tela, t) in FEITOS: continue
            try:
                o = tenta(c, tela, [('btn', t)])
                registra(o)
                if t == '⋯' and not o.get('erro'):
                    abre(c, tela); c.js(f"({CLK})('⋯',false)"); time.sleep(.5); itens = c.js(MENU) or []
                    for it in itens:
                        try: registra(tenta(c, tela, [('btn', '⋯'), ('menu', it)]))
                        except Exception as ex: registra({'tela': tela, 'passos': [('btn', '⋯'), ('menu', it)], 'erro': str(ex)[:200]})
            except Exception as ex:
                registra({'tela': tela, 'passos': [('btn', t)], 'erro': str(ex)[:200]})
        if (tela, None) in FEITOS: continue
        try: registra(tenta(c, tela, [('linha', None)]))
        except Exception as ex: registra({'tela': tela, 'passos': [('linha', None)], 'erro': str(ex)[:200]})
finally:
    c.close()
print('fim', k)
