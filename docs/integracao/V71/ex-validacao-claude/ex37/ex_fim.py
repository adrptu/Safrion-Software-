# -*- coding: utf-8 -*-
"""Últimas conferências (só leitura; perfil Ana; capturas cap/fim_*.png):
1) OS com filtro Safra = 2026/27: o "Nova ordem" herda a safra?
2) "Abrir caso" (VE-06), "Abrir manutenção" (CA-03det), "Abrir divergência" (PT-05det): formulário e campos.
3) AG-01#VIS-013 › Decidir controle › escolher Inseticida B: rótulo e unidade da dose.
4) CO-06det: clicar "Liberar para destinação compatível" (é travado pelo laudo?).
5) CD-08 "Comparar com o realizado": aviso e se há "Aplicar".
6) CD-04 "Cadastrar pessoa" vazio → Salvar: a obrigatoriedade só aparece depois do clique?"""
import json, time, re
from lib import *
TOAST = r"""(()=>[...document.querySelectorAll('[role=status],[role=alert],[aria-live]')].map(e=>e.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).join(' | ').slice(0,700))()"""
SETF = r"""((rot,val)=>{ const s=[...document.querySelectorAll('select')].filter(e=>e.getClientRects().length&&!e.closest('[role=dialog]')&&new RegExp(rot,'i').test(e.getAttribute('aria-label')||''));
  if(!s.length) return 'sem filtro '+rot; const e=s[0]; const o=[...e.options].find(o=>o.value===val||o.text.trim()===val); if(!o) return 'sem opção '+val;
  e.value=o.value; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); return 'ok '+o.text.trim(); })"""
PAINEL = r"""(()=>{ const v=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'; const c=[...document.querySelectorAll('aside,[role=dialog]')].filter(v); return c.map(e=>({tag:e.tagName,role:e.getAttribute('role'),txt:e.innerText.replace(/\s+/g,' ').slice(0,700),campos:[...e.querySelectorAll('input,select,textarea')].filter(v).map(i=>{const l=i.closest('label'); return (l?l.innerText.split('\n')[0]:(i.getAttribute('aria-label')||i.placeholder||'')).trim().slice(0,40)+'='+(i.value||'').slice(0,30)+'('+(i.type||i.tagName)+')';}),verdes:[...e.querySelectorAll('button,a')].filter(b=>v(b)&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText.trim())})); })()"""
out = {}
c = novo()
try:
    abre(c, 'OS'); out['1_aplica'] = c.js(f"({SETF})('safra','2026/27')"); time.sleep(.6)
    clica(c, 'Criar ordem'); time.sleep(.6); d = dialogo(c) or []
    out['1_form'] = [(f['lab'][:40], f['val']) for f in (d[0]['campos'] if d else [])]; shot(c, 'fim_1_os_nova_ordem_com_safra')
    for tela, rot in (('VE-06', 'Abrir caso'), ('CA-03det', 'Abrir manutenção'), ('PT-05det', 'Abrir divergência')):
        abre(c, tela); r = clica(c, rot); time.sleep(.8)
        out[f'2_{tela}'] = dict(clique=r, url=c.js('location.href'), painel=c.js(PAINEL), aviso=c.js(TOAST)); shot(c, f'fim_2_{tela}')
    abre(c, 'AG-01', '#VIS-013'); time.sleep(.8); clica(c, 'Decidir controle'); time.sleep(.8)
    out['3_antes'] = c.js("(()=>{const l=[...document.querySelectorAll('[role=dialog] label, aside label')].map(x=>x.innerText.trim()).filter(t=>/^Dose/.test(t)); return l;})()")
    c.js("""(()=>{const r=[...document.querySelectorAll('input[type=radio]')].find(i=>(i.closest('label')||i.parentElement).innerText.includes('Inseticida B')); r&&r.click();})()"""); time.sleep(.6)
    out['3_depois'] = c.js("(()=>{const l=[...document.querySelectorAll('[role=dialog] label, aside label, [role=dialog] div, aside div')].filter(x=>x.children.length<3&&/^Dose \\(/.test(x.innerText.trim())).map(x=>x.innerText.trim().split('\\n')[0]); return [...new Set(l)];})()")
    t = paineis(c) or ''; out['3_trecho'] = re.findall(r'(?:Estoque|Dose)[^\n]{0,120}', t)[:6]
    shot(c, 'fim_3_vis013_inseticida_b')
    abre(c, 'CO-06det'); r = clica(c, 'Liberar para destinação compatível'); time.sleep(.8)
    out['4_co06det'] = dict(clique=r, aviso=c.js(TOAST), painel=c.js(PAINEL)); shot(c, 'fim_4_co06det_liberar')
    abre(c, 'CD-08'); r = clica(c, 'Comparar com o realizado'); time.sleep(.8)
    out['5_cd08'] = dict(clique=r, aviso=c.js(TOAST), aplicar=[b['t'] for b in botoes(c) if 'Aplicar' in b['t']], painel=c.js(PAINEL)); shot(c, 'fim_5_cd08_comparar')
    abre(c, 'CD-04'); clica(c, 'Cadastrar pessoa'); time.sleep(.6)
    c.js("""(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); b&&b.click();})()"""); time.sleep(.6)
    out['6_cd04_vazio'] = dict(aviso=c.js(TOAST), dlg=c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); return d?d.innerText.replace(/\\s+/g,' ').slice(0,400):'fechou';})()"))
    shot(c, 'fim_6_cd04_salvar_vazio')
finally:
    c.close()
json.dump(out, open(os.path.join(EX, 'ex_fim.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:14000])
