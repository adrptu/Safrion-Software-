"""Varre as páginas e lista ações duplicadas na mesma tela: mesmo comando + mesmo alvo (link: destino; botão: o registro/seção que o contém) visível mais de uma vez; e destinos iguais com rótulos diferentes (revisar). v3.1: a mesma ação em registros diferentes não é duplicata.
Uso: python3 acoes_duplicadas.py <gen37> <saida.json> [filtro]
Fora da conta: menu lateral, faixa de etapas, ações por linha de grade (uma por registro), paginação/ordenação de grade."""
import sys,os,subprocess,time,json,re
G=sys.argv[1]; OUT=sys.argv[2]; FIL=sys.argv[3] if len(sys.argv)>3 else ''
sys.path.insert(0,G)
from cdp import Chrome
from journeys import free
R=os.path.join(G,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
JS=r"""(()=>{const norm=s=>(s||'').replace(/\s+/g,' ').replace(/[›→←‹▾▸]/g,'').trim().toLowerCase();
 const vis=e=>{const r=e.getBoundingClientRect(); if(!r.width||!r.height) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'&&e.closest('[hidden],[aria-hidden=true]')===null;};
 const fora=e=>e.closest('.menu-lat,nav.etp,nav[aria-label*="Etapas"],[role=row],[role=columnheader],[role=tablist],.g2pag,[aria-label*="breadcrumb" i],nav[aria-label*="Trilha" i],aside[role=dialog],[aria-modal=true]');
 const els=[...document.querySelectorAll('button,a[href],[role=button]')].filter(e=>vis(e)&&!fora(e));
 const it=els.map(e=>{const lab=norm(e.innerText)||norm(e.getAttribute('aria-label'))||norm(e.title); const href=e.tagName==='A'?(e.getAttribute('href')||''):''; const ID=/\b(?:(?:OS|OM|OC|OB|REQ|SOL|CG|LC|PC|PED|REC|DIA|INSP|LT|L27|LG26|AT|T|RS|PV|CT|TK|CNT|MP|RM|CRE|BT)-?[0-9][0-9A-Z-]*|L\d\d-\d+)\b/; let alvo='tela', a=e;
 for(let i=0;a&&i<8&&a.tagName!=='MAIN'&&a.tagName!=='HEADER';i++,a=a.parentElement){ const m=(a.innerText||'').match(ID); if(m){ alvo=m[0]; break; } } const reg=(e.closest('header')?'cabeçalho':e.closest('footer,[data-rodape]')?'rodapé':e.closest('section')?'seção':e.closest('main')?'conteúdo':'outro'); return {lab,href,reg,alvo};}).filter(x=>x.lab&&x.lab.length>1&&!/^(×|fechar|limpar|limpar filtros|cancelar|ok|voltar|excluir|manter|descartar alterações|continuar editando|selecionar tudo)$/.test(x.lab));
 const by={}; it.forEach(x=>{const k=x.lab+'|'+x.href+'|'+x.alvo; (by[k]=by[k]||[]).push(x.reg);});
 const dl=Object.entries(by).filter(([k,v])=>v.length>1).map(([k,v])=>({rot:k.split('|')[0],onde:v}));
 const bh={}; it.filter(x=>x.href&&!x.href.startsWith('#')).forEach(x=>{(bh[x.href]=bh[x.href]||new Set()).add(x.lab);});
 const dh=Object.entries(bh).filter(([k,v])=>v.size>1).map(([k,v])=>({destino:k,rotulos:[...v]}));
 return {n:it.length,mesmoRotulo:dl,mesmoDestino:dh};})()"""
res={}; c=None
try:
    c=Chrome(port=free()); c.size(1440,900)
    pages=sorted(f for f in os.listdir(R) if f.endswith('.dc.html') and FIL in f)
    for f in pages:
        try:
            c.goto(f'http://127.0.0.1:{p}/{f}',wait=1.0); res[f]=c.js(JS)
        except Exception as e: res[f]={'erro':str(e)[:200]}
finally:
    if c: c.close()
    srv.kill()
json.dump(res,open(OUT,'w'),ensure_ascii=False,indent=1)
com=[k for k,v in res.items() if v.get('mesmoRotulo') or v.get('mesmoDestino')]
print(f'RESULTADO: {len(res)} páginas · {len(com)} com ação repetida · erros {sum(1 for v in res.values() if "erro" in v)}')
for k in com[:200]:
    v=res[k]; print(k,'|',' ; '.join(f"{d['rot']}×{len(d['onde'])}({','.join(d['onde'])})" for d in v['mesmoRotulo'])[:300],'|',' ; '.join(f"{d['destino']}←{d['rotulos']}" for d in v['mesmoDestino'])[:300])
