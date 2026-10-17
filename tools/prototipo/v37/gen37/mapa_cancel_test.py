# -*- coding: utf-8 -*-
"""Mapa › Ordens de serviço › Avanço depois de CANCELAR uma O.S. de verdade (pedido do Codex 6216788760 sobre a correção 6216014054).
Fluxo real no navegador, perfil novo: tela O.S. → painel da ordem → "Cancelar sem execução" → motivo → "Confirmar cancelamento"; depois
o Mapa (IN-04, Santa Rita) em Ordens de serviço › Avanço: o rótulo do talhão é a conta das ordens ABERTAS lida do cenário gravado
(sem Encerradas nem Canceladas), antes e depois do cancelamento e de novo após recarregar. Contraprova: o render de e18fe1e (antes da
correção) reprova C4 (RENDER_DIR=<render de e18fe1e>). Dados sintéticos; render em RENDER_DIR ou _render.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B mapa_cancel_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK, FAIL = [], []
def chk(n, c, x=''):
    (OK if c else FAIL).append(n); print(('OK   ' if c else 'FALHA'), n, '' if c else str(x)[:600], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def espera(e, s=20):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.3)
    return False
TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
def mapa_avanco(tal, mutante=False):
    J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Santa Rita'})); 1"); c.goto(U('IN-04.dc.html'), 1.6)
    if mutante: J("osAb=function(os){ return os.filter(o=>o.fase!=='Encerradas'); }; 1")   # contraprova: a regra de antes da correção
    J(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==='Ordens de serviço'); b&&b.click();}})()"); time.sleep(.8)
    J("(()=>{const b=[...document.querySelectorAll('main [role=group][aria-label=\"Mostrar\"] button')].find(b=>b.innerText.trim()==='Avanço'); b&&b.click();})()"); time.sleep(.9)
    # MUX-F1 (17/10/2026): o nome acessível do talhão passou a ser o completo do pedido ("T4, 120 ha, …"); o talhão se acha por data-talhao e o
    # rótulo da camada vem de data-rotulo, o mesmo texto que vinha depois de "T4: " (oráculo obsoleto na forma de achar; a asserção não muda)
    return J(f"(()=>{{const e=[...document.querySelectorAll('svg [role=button]')].find(x=>x.getAttribute('data-talhao')==='{tal}'); return e?e.getAttribute('data-rotulo'):'';}})()") or ''
# oráculo: abertas do talhão no cenário gravado (a mesma fonte do mapa), sem Encerradas nem Canceladas
ORACULO = """((tal)=>{ const c=window.__cen.cenGet(); const os=Object.values(c.ordens||{}).filter(o=>o.talhao===tal);
  const ab=os.filter(o=>['Encerradas','Canceladas'].indexOf(o.etapa)<0&&(o.area||0)>0); const a=ab.reduce((s,o)=>s+o.area,0), r=ab.reduce((s,o)=>s+Math.min(o.realizado||0,o.area),0);
  return {n:ab.length,a,r,ids:ab.map(o=>o.id),todas:os.map(o=>o.id+':'+o.etapa)}; })"""
def oraculo(tal):   # lido na tela O.S. (window.__cen), que lê o mesmo cenário gravado que o Mapa
    c.goto(U('OS.dc.html'), 1.2); espera("!!(window.__cen&&window.__cen.cenGet)")
    return J(f"{ORACULO}({json.dumps(tal)})")
try:
    c.aparelho(1440, 900, 1, False)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('OS.dc.html'), 1.6); espera("!!(window.__cen&&window.__cen.cenGet)")
    # candidata: sem realizado, A liberar ou Liberadas, com área, num talhão de Santa Rita que tem outra ordem aberta com área
    cand = json.loads(J("""JSON.stringify((()=>{ const c=window.__cen.cenGet(); const L=Object.values(c.ordens||{}); const tal=o=>o.talhao||'';
      const ok=L.filter(o=>['A liberar','Liberadas'].indexOf(o.etapa)>=0&&!(o.realizado>0)&&(o.area||0)>0&&tal(o));
      const par=ok.find(o=>L.some(x=>x.id!==o.id&&tal(x)===tal(o)&&['Encerradas','Canceladas'].indexOf(x.etapa)<0&&(x.area||0)>0));
      const o=par||ok[0]; return o?{id:o.id,tal:tal(o),etapa:o.etapa,area:o.area}:null; })())""") or 'null')
    chk('C0 há O.S. elegível (sem realizado, A liberar ou Liberadas, com área)', bool(cand), cand)
    if cand:
        tal = cand['tal'].split(' ')[0]
        ora0 = oraculo(cand['tal']); antes = mapa_avanco(tal)
        chk(f'C1 antes: rótulo do {tal} no Avanço = conta das abertas do cenário ({ora0["r"]:g}/{ora0["a"]:g} ha)',
            f"/{ora0['a']:g} ha".replace('.', ',') in antes or (ora0['n'] == 0 and 'ordem' in antes), [antes, ora0])
        # cancelar pela interface, com o perfil que tem a alçada AL-04 (o primeiro do seletor que mostra a ação)
        perfis = json.loads(J("JSON.stringify([...(document.querySelector('select[aria-label=\"Trocar perfil de demonstração\"]')||{options:[]}).options].map(o=>o.value))") or '[]')
        feito = None
        for pf in perfis:
            J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(pf)}); 1"); c.goto(U('OS.dc.html#' + cand['id']), 1.6)
            espera(f"[...document.querySelectorAll('button')].some(b=>b.getClientRects().length&&b.innerText.trim()==='Cancelar sem execução')", 4)
            if J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Cancelar sem execução'); if(!b) return false; b.click(); return true;})()"):
                time.sleep(.5); feito = pf; break
        chk('C2 "Cancelar sem execução" disponível para um perfil com a alçada AL-04', bool(feito), perfis)
        if feito:
            J("(()=>{const t=document.querySelector('[aria-label=\"Motivo do cancelamento\"]'); const s=Object.getOwnPropertyDescriptor(t.__proto__,'value').set; s.call(t,'Teste: ordem duplicada'); t.dispatchEvent(new Event('input',{bubbles:true})); t.dispatchEvent(new Event('change',{bubbles:true}));})()")
            time.sleep(.3); J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Confirmar cancelamento'); b&&b.click();})()"); time.sleep(1.0)
            et = J(f"(Object.values(window.__cen.cenGet().ordens||{{}}).find(o=>o.id==={json.dumps(cand['id'])})||{{}}).etapa")
            chk(f'C3 {cand["id"]} cancelada pelo fluxo real (perfil {feito}) e gravada no cenário', et == 'Canceladas', et)
            ora1 = oraculo(cand['tal']); depois = mapa_avanco(tal)
            ok1 = (f"/{ora1['a']:g} ha".replace('.', ',') in depois) if ora1['n'] else ('cancelada' in depois or 'encerrada' in depois or 'sem ordem' in depois)
            chk(f'C4 depois: rótulo do {tal} = conta das abertas sem a cancelada ({ora1["r"]:g}/{ora1["a"]:g} ha; a {cand["id"]} de {cand["area"]:g} ha não entra)', ok1 and cand['id'] not in ora1['ids'], [depois, ora1])
            c.goto(U('Main.dc.html'), .3)   # recarga: sem estado em memória
            rec = mapa_avanco(tal)
            chk('C5 após recarregar: o mesmo rótulo (lido do cenário gravado, não de estado em memória)', rec == depois, [rec, depois])
finally:
    c.close()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
