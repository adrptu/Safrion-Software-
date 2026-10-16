# -*- coding: utf-8 -*-
"""EX-04 (acréscimos da v2): contexto herdado nos modais. Só leitura; estado inicial perfil Ana; capturas em cap/ex04_*.png.
1) OS "Nova ordem"/"Criar ordem": o formulário pede a safra?
2) AG-01 "Programar vistoria", AG-03 "Criar diagnóstico", AG-02 "Registrar laudo": com filtro de fazenda/talhão aplicado, o formulário herda?
3) AG-06 EF-021 "Programar pós": aonde leva e o que vem preenchido.
4) SU-01 "Reprogramar proposta": item padrão × linha; há ação por linha?
5) SU-01 primária "Abrir cotação da SOL-2026-07": estado do CMP ao chegar."""
import json, time, re
from lib import *
SETF = r"""((rot,val)=>{ const s=[...document.querySelectorAll('select')].filter(e=>e.getClientRects().length&&!e.closest('[role=dialog]')&&new RegExp(rot,'i').test((e.getAttribute('aria-label')||'')+' '+((e.closest('label')||{}).innerText||'')));
  if(!s.length) return 'sem filtro '+rot; const e=s[0]; const o=[...e.options].find(o=>o.value===val||o.text.trim()===val); if(!o) return 'sem opção '+val+' em '+[...e.options].map(o=>o.text.trim()).join('|');
  e.value=o.value; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); return 'ok '+(e.getAttribute('aria-label')||'')+'='+o.text.trim(); })"""
FILTROS = r"""(()=>[...document.querySelectorAll('select')].filter(e=>e.getClientRects().length&&!e.closest('[role=dialog]')).map(e=>(e.getAttribute('aria-label')||((e.closest('label')||{}).innerText||'').split('\n')[0])+'='+(e.selectedOptions[0]||{text:''}).text.trim()+' ['+[...e.options].map(o=>o.text.trim()).slice(0,12).join('|')+']'))()"""
out = {}
def form(c):
    d = dialogo(c) or []
    return [dict(titulo=x['titulo'], campos=[(f['lab'][:45], f['val']) for f in x['campos'] if f['vis']], verdes=[b['t'] for b in x['bts'] if b['verde']]) for x in d]
c = novo()
try:
    # 1) Nova ordem
    abre(c, 'OS'); bs = [b['t'] for b in botoes(c) if re.match(r'(\+ )?(Nova ordem|Criar ordem|Criar O\.S\.|Nova O\.S\.)', b['t'])]
    out['1_os_botoes'] = bs
    if bs:
        clica(c, bs[0]); time.sleep(.6); out['1_os_form'] = form(c); shot(c, 'ex04_1_os_nova_ordem')
    # 2) filtros × modais
    for tela, rot, filtros in [('AG-01', 'Programar vistoria', [('fazenda', 'Santa Rita'), ('talh', 'P1')]),
                               ('AG-03', 'Criar diagnóstico', [('fazenda', 'Santa Rita'), ('talh', 'P1')]),
                               ('AG-02', 'Registrar laudo', [('fazenda', 'Santa Rita'), ('talh', 'P1')])]:
        abre(c, tela); f0 = c.js(FILTROS); res = []
        for rx, v in filtros:
            res.append(c.js(f"({SETF})({json.dumps(rx)},{json.dumps(v)})")); time.sleep(.5)
        f1 = c.js(FILTROS)
        r = clica(c, rot); time.sleep(.6)
        out[f'2_{tela}'] = dict(filtros_iniciais=f0, aplica=res, filtros_aplicados=f1, clique=r, form=form(c))
        shot(c, f'ex04_2_{tela}_{re.sub(chr(92)+"W+","_",rot)}_com_filtro')
    # 3) Programar pós
    abre(c, 'AG-06'); r = clica(c, 'Programar pós'); time.sleep(1.2)
    out['3_pos'] = dict(clique=r, url=c.js('location.href'), form=form(c), paineis=(paineis(c) or '')[:400], filtros=c.js(FILTROS), topo=texto(c)[:600])
    shot(c, 'ex04_3_programar_pos_destino')
    # 4) SU-01 Reprogramar
    abre(c, 'SU-01'); out['4_su01_botoes'] = [b['t'] for b in botoes(c) if re.search(r'Reprogram', b['t'])]
    linhas = c.js("[...document.querySelectorAll('main [role=row]')].filter(r=>r.getClientRects().length).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,70)).slice(0,12)")
    out['4_su01_linhas'] = linhas
    r = clica(c, 'Reprogramar proposta'); time.sleep(.6); out['4_su01_form'] = form(c); shot(c, 'ex04_4_su01_reprogramar')
    # tenta o ⋯ da 3ª linha, se houver
    abre(c, 'SU-01')
    out['4_su01_menu_linha'] = c.js("""(()=>{ const r=[...document.querySelectorAll('main [role=row]')].filter(r=>r.getClientRects().length&&r.querySelector('[role=cell]'))[2]; if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>/⋯|Mais ações|Ações/.test(b.innerText+(b.getAttribute('aria-label')||''))); if(!b) return 'linha sem ⋯: '+r.innerText.replace(/\\s+/g,' ').slice(0,80); b.click(); return 'ok'; })()""")
    time.sleep(.5); out['4_su01_menu_itens'] = c.js("[...document.querySelectorAll('[role=menu] [role=menuitem],[role=menu] button')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim())")
    # 5) SU-01 Abrir cotação
    abre(c, 'SU-01'); prim = [b['t'] for b in botoes(c) if b['verde']]; out['5_su01_verdes'] = prim
    r = clica(c, 'Abrir cotação da SOL-2026-07'); time.sleep(1.5)
    t = texto(c); out['5_cmp'] = dict(clique=r, url=c.js('location.href'), nenhuma_safra='Nenhuma safra escolhida' in t, trecho=t[t.find('TRABALHANDO EM'):t.find('TRABALHANDO EM') + 200] if 'TRABALHANDO EM' in t else t[:300])
    shot(c, 'ex04_5_cmp_ao_chegar')
finally:
    c.close()
json.dump(out, open(os.path.join(EX, 'ex04_modais.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:9000])
