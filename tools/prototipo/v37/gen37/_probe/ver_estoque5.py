# -*- coding: utf-8 -*-
"""Verificador · Estoque 5: fazenda (Boa Vista/Todas), restaurar demonstração (filtros e formulários), T06 da EST, movimentos do app sem sinal."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"
FAZ = 'select[aria-label="Filtrar por fazenda"]'
v = V()
try:
    v.abrir()
    # T06 (parte EST): clique na primeira linha abre formulário preenchido
    r = v.J("(()=>{const r=document.querySelector('[role=row].g2ed'); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})()"); time.sleep(.4)
    print('T06 EST:', r, v.aberto(), v.J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].some(i=>i.value)"), v.aside()[:120])
    v.clk('Fechar', 'aside[role=dialog]')
    print('opções fazenda:', v.J(f"[...document.querySelector('{FAZ}').options].map(o=>o.value)"))
    for f in ['Boa Vista', 'Todas', 'Santa Rita']:
        opt = v.J(f"[...document.querySelector('{FAZ}').options].map(o=>o.value).find(x=>x.indexOf('{f}')>=0)")
        v.setv(FAZ, opt); time.sleep(.2)
        out = []
        for i in range(1, 7):
            v.etapa(i); m = v.main(); out.append((i, v.prim(), 'Nenhum estoque na Boa Vista' in m, len(v.rows())))
        print(f, '->', out)
        if f == 'Boa Vista':
            v.shot('ver_est_bv.png'); print('bv main:', v.main()[:300])
    # restaurar com filtro de local e formulário aberto
    v.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');")
    v.abrir(); v.etapa(4); v.clk('Câmara fria'); print('filtro antes:', v.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"))
    print('restaurar:', v.clk('Restaurar demonstração'), '| pede confirmação:', 'Volta O.S., estoque e app' in v.main())
    print('manter:', v.clk('Manter'), v.cen("Object.keys(c.reqs).length"))
    v.clk('Restaurar demonstração'); v.clk('Restaurar'); print('toast:', v.toast()); print('reqs:', v.cen("Object.keys(c.reqs).length"))
    print('filtro depois:', v.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"), '| linhas lote:', v.J("[...document.querySelectorAll('[role=row].g2kid')].map(r=>r.innerText.split('\\n')[0].trim()).join(',')"))
    # app sem sinal: confirmar e apontar (liberar e entregar antes)
    print(v.mudar("c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const rid=c.ordens['OS-0430'].req; c.reqs[rid].itens.forEach(i=>cenEntregar(c,rid,i.prod,i.solicitado,'Marcos')); cenSinal(c,false); cenConfirmarRecebimento(c,rid); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))
    v.abrir(); v.etapa(6); print('k6:', v.J(K))
    for x in v.rows()[:5]: print('   mov|', x[:230])
    v.row('Consumo apontado no app'); print('origem consumo:', v.aside()[:300]); v.clk('Fechar', 'aside[role=dialog]')
    v.etapa(2); print('k2:', v.J(K)); print('linha glif:', v.rowtxt('OS-0430', 'Glifosato'))
    v.etapa(3); print('k3:', v.J(K)); print('linha glif:', v.rowtxt('OS-0430', 'Glifosato'))
    print('sinal:', v.mudar("return cenSinal(c,true);")); v.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    v.etapa(6); print('k6 após sinal:', v.J(K)); [print('   mov|', x[:200]) for x in v.rows()[:3]]
    print('erros:', v.erros())
finally:
    v.fim()
