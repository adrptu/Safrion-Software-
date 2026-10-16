# -*- coding: utf-8 -*-
"""Conferências complementares (só leitura; perfil Ana; capturas cap/sup_*.png):
1) AG-02 "Registrar laudo" com filtro Fazenda = Lagoa Grande e = Boa Vista: a fazenda do formulário acompanha?
2) OS: filtros da tela (fazenda/safra) no estado inicial × campo Safra do "Nova ordem".
3) CA-02 "Reabrir saldo da OS-0417": o que abre e quantos campos.
4) CO-06det: botões de decisão (verde/branco) e se há decisão neutra."""
import json, time, re
from lib import *
SETF = r"""((rot,val)=>{ const s=[...document.querySelectorAll('select')].filter(e=>e.getClientRects().length&&!e.closest('[role=dialog]')&&new RegExp(rot,'i').test(e.getAttribute('aria-label')||''));
  if(!s.length) return 'sem filtro '+rot; const e=s[0]; const o=[...e.options].find(o=>o.value===val||o.text.trim()===val); if(!o) return 'sem opção '+val;
  e.value=o.value; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); return 'ok '+o.text.trim(); })"""
FILTROS = r"""(()=>[...document.querySelectorAll('select')].filter(e=>e.getClientRects().length&&!e.closest('[role=dialog]')&&!/perfil/i.test(e.getAttribute('aria-label')||'')).map(e=>(e.getAttribute('aria-label')||'')+'='+(e.selectedOptions[0]||{text:''}).text.trim()))()"""
out = {}
c = novo()
try:
    for faz in ('Lagoa Grande', 'Boa Vista'):
        abre(c, 'AG-02'); a = c.js(f"({SETF})('fazenda',{json.dumps(faz)})"); time.sleep(.5)
        clica(c, 'Registrar laudo'); time.sleep(.6)
        d = dialogo(c) or []
        out[f'1_ag02_{faz}'] = dict(aplica=a, filtros=c.js(FILTROS), campos=[(f['lab'][:30], f['val']) for f in (d[0]['campos'] if d else [])][:3])
        shot(c, f'sup_1_ag02_registrar_laudo_{faz.replace(" ", "_")}')
    abre(c, 'OS'); out['2_os_filtros'] = c.js(FILTROS); t = texto(c); i = t.find('Safra'); out['2_os_topo'] = t[:900]
    clica(c, 'Criar ordem'); time.sleep(.6); d = dialogo(c) or []
    out['2_os_form'] = [(f['lab'][:60], f['val'], f['tipo'] if 'tipo' in f else f.get('type')) for f in (d[0]['campos'] if d else [])]
    out['2_os_safra_opcoes'] = c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const s=d&&d.querySelector('select'); return s?[...s.options].map(o=>o.text.trim()):null;})()")
    shot(c, 'sup_2_os_nova_ordem')
    abre(c, 'CA-02'); r = clica(c, 'Reabrir saldo da OS-0417'); time.sleep(.8)
    out['3_ca02_clique'] = r; out['3_ca02_dlg'] = resume_dlg(dialogo(c))
    out['3_ca02_painel_qualquer'] = c.js("""(()=>{ const v=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'; const c=[...document.querySelectorAll('aside,[role=dialog],[data-drawer],.drawer,[class*=drawer]')].filter(v); return c.map(e=>({tag:e.tagName,role:e.getAttribute('role'),txt:e.innerText.replace(/\\s+/g,' ').slice(0,500),inputs:[...e.querySelectorAll('input,select,textarea')].filter(v).length})); })()""")
    out['3_ca02_inputs_tela'] = c.js("[...document.querySelectorAll('input,select,textarea')].filter(e=>e.getClientRects().length&&!/perfil|Filtrar|Agrupar/i.test(e.getAttribute('aria-label')||'')).map(e=>{const l=e.closest('label'); return (l?l.innerText:(e.getAttribute('aria-label')||e.placeholder||'')).replace(/\\s+/g,' ').slice(0,50)})")
    shot(c, 'sup_3_ca02_reabrir_saldo')
    abre(c, 'CO-06det'); out['4_co06det_botoes'] = botoes(c, 'document.querySelector("main")||document')
    t = texto(c); out['4_co06det_topo'] = t[t.find('INSP'):t.find('INSP') + 700] if 'INSP' in t else t[:700]
    shot(c, 'sup_4_co06det')
finally:
    c.close()
json.dump(out, open(os.path.join(EX, 'ex_sup.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:12000])
