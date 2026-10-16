# -*- coding: utf-8 -*-
"""Conferências pontuais (só leitura; perfil Ana; capturas em cap/misc_*.png):
a) PL-02 status da v4 e PL-02det "Publicar ajuste do T1-A" (aviso "publicado na v4");
b) ON-01det primária "Validar prévia": dica e aviso depois do clique;
c) VE-04det formulário da revisão v3: primária e texto;
d) CA-02 "Reabrir saldo" e CA-03 formulários: campos."""
import json, time, re
from lib import *
TOAST = r"""(()=>[...document.querySelectorAll('[role=status],[role=alert],[aria-live]')].map(e=>e.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).join(' | ').slice(0,600))()"""
out = {}
c = novo()
try:
    abre(c, 'PL-02'); t = texto(c); out['a_pl02_status'] = re.findall(r'[^\n]*v4[^\n]*', t)[:8]
    abre(c, 'PL-02det'); t = texto(c); out['a_pl02det_topo'] = re.findall(r'[^\n]*(?:v4|v3|rascunho|Rascunho)[^\n]*', t)[:10]
    out['a_pl02det_verdes'] = [b['t'] for b in botoes(c) if b['verde']]
    r = clica(c, 'Publicar ajuste do T1-A'); time.sleep(.8); out['a_clique'] = r; out['a_aviso'] = c.js(TOAST); out['a_dlg'] = resume_dlg(dialogo(c))
    shot(c, 'misc_a_pl02det_publicar_ajuste')
    if out['a_dlg'] and out['a_dlg'][0]['verdes']:
        c.js("""(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const b=[...d.querySelectorAll('button')].filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').pop(); b&&b.click();})()""")
        time.sleep(.8); out['a_aviso2'] = c.js(TOAST); shot(c, 'misc_a_pl02det_publicar_ajuste_2')
    abre(c, 'PL-02'); out['a_pl02_depois_status_inicial'] = re.findall(r'[^\n]*v4[^\n]*', texto(c))[:4]
    # b) ON-01det
    abre(c, 'ON-01det'); out['b_on01det_btn'] = [b for b in botoes(c) if 'Validar' in b['t']]
    r = clica(c, 'Validar prévia'); time.sleep(.8); out['b_aviso'] = c.js(TOAST); shot(c, 'misc_b_on01det_validar')
    # c) VE-04det
    abre(c, 'VE-04det'); bs = botoes(c); out['c_ve04det_botoes'] = [b['t'] for b in bs][:40]
    cand = [b['t'] for b in bs if re.search(r'Revis|v3|Renegoci|\+', b['t'])]
    out['c_cand'] = cand
    for rot in cand[:3]:
        abre(c, 'VE-04det'); clica(c, rot); time.sleep(.6); d = resume_dlg(dialogo(c))
        if d:
            out['c_form'] = dict(rot=rot, dlg=d, txt=(dialogo(c) or [{}])[0].get('txt', '')[:600]); shot(c, 'misc_c_ve04det_revisao'); break
    # d) CA-02 Reabrir saldo; CA-03 formulários
    for tela in ('CA-02', 'CA-03'):
        abre(c, tela); bs = [b['t'] for b in botoes(c) if not re.match(r'(Filtrar|i$|Colunas|Cartões|Tabela|Agrupar|Todas|Todos|Restaurar)', b['t'])]
        out[f'd_{tela}_botoes'] = bs[:40]
finally:
    c.close()
json.dump(out, open(os.path.join(EX, 'ex_misc.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:12000])
