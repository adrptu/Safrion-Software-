# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · B: entregas por O.S. com a OS-0430 liberada pelo cenário; confirmação do app vinda de outro documento (iframe)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':'')), ov:a.scrollWidth>a.clientWidth+1};})()"
v = V()
try:
    v.abrir(); v.etapa(2)
    r = v.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');"); print('liberar:', r); time.sleep(.5)
    rid = v.cen("c.ordens['OS-0430'].req"); print('req nova:', rid)
    print('k2:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"), '| prim:', v.prim())
    for x in v.rows(): print('   ', x[:280])
    # consulta: REQ-036 bloqueada
    v.row('REQ-036'); f = v.J(FORM); print('REQ-036 form:', f); print('   aside:', v.aside()[:300])
    v.ok(f and 'Salvar' not in f['btns'], 'REQ-036 abre só consulta (sem Salvar)', f)
    v.clk('Fechar', 'aside[role=dialog]')
    v.row(rid, 'Glifosato'); f = v.J(FORM); print('Glif form:', f); print('   aside:', v.aside()[:600])
    v.ok(v.val('fx_g_ent_qtd') in ('320',) and v.val('fx_g_ent_quem') == 'Marcos', 'padrões: 320 L e Marcos', (v.val('fx_g_ent_qtd'), v.val('fx_g_ent_quem')))
    v.setv('fx_g_ent_qtd', '321'); v.clk('Salvar', 'aside[role=dialog]'); e = v.err(); print('321:', e)
    v.ok('Acima do saldo a entregar: 320 L' in e, 'recusa 321 L', e)
    v.setv('fx_g_ent_qtd', '300'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| aberto:', v.aberto())
    print('lote G26-14:', v.cen("c.lotes['Glifosato 480|G26-14']"))
    t = v.rowtxt(rid, 'Glifosato'); print('linha:', t)
    v.ok('Aguardando confirmação no app' in t and '20 L' in t, 'parcial 300 L: aguardando app, faltam 20 L', t)
    print('prim agora:', v.prim())
    # abre de novo: padrão 20
    v.row(rid, 'Glifosato'); print('padrão após parcial:', v.val('fx_g_ent_qtd'), '| aside:', v.aside()[:400]); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    for p in ('2,4-D', 'Óleo'):
        v.row(rid, p); print(p, 'padrões:', v.val('fx_g_ent_qtd'), v.val('fx_g_ent_quem')); v.clk('Salvar', 'aside[role=dialog]'); print('   toast:', v.toast())
    for x in v.rows(): print('   ', x[:280])
    print('k2:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"), '| prim:', v.prim())
    print('lotes:', v.cen("['Glifosato 480|G26-14','2,4-D 806|D26-01','Óleo mineral|O26-05'].map(k=>[k,c.lotes[k].fisico,c.lotes[k].reservado])"))
    print('itens:', v.cen(f"c.reqs['{rid}'].itens.map(i=>[i.prod,i.entregue,i.custodia,i.confirmado,i.quem])"))
    # linha entregue abre em consulta
    v.row(rid, 'Glifosato'); f = v.J(FORM); print('entregue form:', f); print('   aside:', v.aside()[:300]); v.clk('Fechar', 'aside[role=dialog]')
    v.shot('ver_est_r4_b1.png')
    # confirmação do app vinda de outro documento (iframe da mesma origem, sem recarregar a tela)
    v.J("(()=>{const f=document.createElement('iframe'); f.id='ifr'; f.style='width:10px;height:10px;position:fixed;bottom:0;right:0'; f.src=location.href; document.body.appendChild(f);})()"); time.sleep(1.5)
    r = v.J(f"(()=>{{const X=document.getElementById('ifr').contentWindow.__cen; const r=X.cenMudar(null,c=>X.cenConfirmarRecebimento(c,'{rid}')); return r.erro||r.msg;}})()"); print('app confirma:', r); time.sleep(.8)
    t = v.rowtxt(rid, 'Glifosato'); print('linha após app:', t)
    v.ok('Aguardando confirmação' not in t, 'confirmação do app tira o Aguardando sem recarregar', t)
    print('k2:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.J("document.getElementById('ifr').remove()")
    v.etapa(6)
    for x in v.rows(): print('   ', x[:280])
    v.shot('ver_est_r4_b6.png')
    print('overflow e6:', v.overflow())
    print('erros:', v.erros())
finally:
    v.fim()
