# -*- coding: utf-8 -*-
"""EX-01 (sub-itens novos da v2) repetido no render final (montado 13:42 UTC), fora da janela de remontagem.
Saída: ex01_rerun.json + capturas cap/ex01_*.png. Só leitura; perfil Ana; Main + storage limpo antes de cada cenário."""
import json, time, re
from lib import *
from comp_lib import IR_ETAPA
TOAST = r"""(()=>[...document.querySelectorAll('[role=status],[role=alert],[aria-live]')].map(e=>e.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).join(' | ').slice(0,700))()"""
def card(c, oid):
    return c.js("""(()=>{const e=[...document.querySelectorAll('main *')].filter(x=>x.children.length===0&&x.textContent.trim()===%s&&x.getClientRects().length&&!x.closest('select'))[0]; if(!e) return null; const k=e.closest('[role=row],tr,article,li,[data-card],button,[role=button]')||e; k.scrollIntoView({block:'center'}); k.click(); return k.innerText.replace(/\\s+/g,' ').slice(0,120);})()""" % json.dumps(oid))
out = {}
c = novo()
try:
    abre(c, 'COLH'); clica_linha(c, 'Pivô 19'); time.sleep(.6); p = paineis(c) or ''
    out['colh_pivo19'] = dict(tha=re.findall(r'[^\n]*\n?[\d.,]+ t/ha (?:parcial|final)', p), area=re.findall(r'Área colhida\n[^\n]*', p), passe=re.findall(r'OS-0505\n[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*', p))
    shot(c, 'ex01_colh_pivo19')
    abre(c, 'OS'); card(c, 'OS-0420'); time.sleep(.8); p = paineis(c) or ''
    out['os0420_painel'] = dict(insumos=re.findall(r'(?:MAP 11-52|KCl[^\n]*|Semente de soja 58 W)\n[^\n]*\n[^\n]*', p), quem=re.findall(r'Quem resolve:[^\n]*', p))
    shot(c, 'ex01_os0420_painel')
    clica(c, 'Abrir ordem completa'); time.sleep(1.2); t = texto(c)
    out['os0420_completa'] = dict(url=c.js('location.href'), kcl=re.findall(r'KCl 60 %\n[^\n]*\n[^\n]*\n[^\n]*', t), map='MAP 11-52' in t, subst=re.findall(r'Substituto proposto[^\n]*', t))
    shot(c, 'ex01_os0420_completa')
    abre(c, 'OS'); card(c, 'OS-0418'); time.sleep(.8); p = paineis(c) or ''
    out['os0418_painel'] = dict(maquina=re.findall(r'Máquina · [^\n]*', p), atividade=re.findall(r'ATIVIDADE\n[^\n]*', p))
    shot(c, 'ex01_os0418_painel')
    abre(c, 'SU-05'); clica(c, 'Formalizar contrato'); time.sleep(.6); d = dialogo(c) or []
    out['su05_contrato'] = [(f['lab'][:30], f['val']) for f in (d[0]['campos'] if d else [])]
    shot(c, 'ex01_su05_formalizar_contrato')
    abre(c, 'SU-04'); out['su04_fertisul'] = re.findall(r'SOL-2026-07 · Fertilizantes\n(?:[^\n]*\n){0,6}', texto(c))[:1]
    abre(c, 'CMP'); clica(c, 'Abrir compra'); time.sleep(1); c.js(f"({IR_ETAPA})(2)"); time.sleep(.6); t = texto(c)
    i = t.find('Fertilizantes\n6 insumos'); seg = t[i:i + 700]
    itens = re.findall(r'\n(KCl 60%|MAP 11-52|Nitrato de cálcio|Nitrato de potássio|NPK 20-05-20|Ureia 45%)\n[^\n]*\n([\d.]+)\nkg', seg)
    out['cmp_fert'] = dict(itens=itens, soma_kg=sum(int(q.replace('.', '')) for n, q in itens if n != 'KCl 60%'))
    shot(c, 'ex01_cmp_etapa2_fertilizantes')
    abre(c, 'CD-06'); t = texto(c); out['cd06_inseticida_b'] = re.findall(r'Inseticida B\n[^\n]*\n[^\n]*', t)
    abre(c, 'AG-01', '#VIS-013'); time.sleep(.8); clica(c, 'Decidir controle'); time.sleep(.8)
    c.js("""(()=>{const r=[...document.querySelectorAll('input[type=radio]')].find(i=>(i.closest('label')||i.parentElement).innerText.includes('Inseticida B')); r&&r.click();})()"""); time.sleep(.6)
    p = paineis(c) or ''; out['vis013_inseticida_b'] = dict(opcao=re.findall(r'Inseticida B\n[^\n]*', p)[:1], dose=re.findall(r'Dose \([^)]*\)', p)[:2], estoque=re.findall(r'Estoque:[^\n]*', p)[:1])
    out['vis013_verdes'] = c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog],aside')].filter(e=>e.getClientRects().length).pop(); return [...d.querySelectorAll('button')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText.trim());})()")
    shot(c, 'ex01_vis013_inseticida_b')
    abre(c, 'PL-02'); out['pl02_status'] = re.findall(r'[^\n]*v4 em rascunho[^\n]*', texto(c))[:1]
    abre(c, 'PL-02det'); clica(c, 'Publicar ajuste do T1-A'); time.sleep(.8); out['pl02det_aviso'] = c.js(TOAST)
    shot(c, 'ex01_pl02det_publicar_ajuste')
finally:
    c.close()
json.dump(out, open(os.path.join(EX, 'ex01_rerun.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
