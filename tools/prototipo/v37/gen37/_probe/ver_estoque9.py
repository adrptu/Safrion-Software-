# -*- coding: utf-8 -*-
"""Verificador · Estoque 9: reprodução dos defeitos encontrados (cada FALHA = defeito reproduzido), 1440x1000, cenário limpo."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"
# células que passam da borda direita da área visível da grade (grade rola na horizontal)
FORA = """(()=>{const box=[...document.querySelectorAll('main *')].find(p=>{const cs=getComputedStyle(p); return /auto|scroll/.test(cs.overflowX)&&p.scrollWidth>p.clientWidth+1&&p.querySelector('[role=row]');}); if(!box) return []; const R=box.getBoundingClientRect(); const o=[]; box.querySelectorAll('[role=cell] button,[role=cell] span').forEach(c=>{const b=c.getBoundingClientRect(); if(c.offsetParent&&b.width&&b.right>R.right+1&&c.innerText.trim()) o.push(c.innerText.trim().slice(0,30));}); return [...new Set(o)];})()"""
v = V()
try:
    v.abrir()
    # 1 · Contagens: "Aprovar ajuste" da INV-2609 passa da borda (cenário inicial)
    v.etapa(5); f = v.J(FORA); v.ok('Aprovar ajuste' not in f, 'etapa 5: botões da linha cabem na área da grade', f)
    # 2 · Recebimentos: após conferir a NF 4533 pela primária, Situação passa da borda
    v.etapa(1); v.clk(v.prim())
    for k, val in [('conf', '20000'), ('apto', '20000'), ('quar', '0'), ('val', '05/2027')]: v.setv('fx_g_rec_' + k, val)
    v.clk('Salvar', 'aside[role=dialog]'); f = v.J(FORA); v.ok(not f, 'etapa 1 após conferir NF 4533: coluna Situação cabe na área', f)
    # 3 · Lote vencido: recebido todo em quarentena, mas "Liberar após inspeção" o põe no disponível
    v.mudar("return cenReceber(c,'Óleo mineral','O25-01',40,'L','Almox. defensivos','07/2026','NF 4700',false);")
    v.abrir(); v.etapa(4); t = v.rowtxt('O25-01'); print('  O25-01:', t)
    v.rowbtn('O25-01', 'Liberar após inspeção'); v.rowbtn('O25-01', 'Confirmar liberação'); d = v.cen("X.cenGet().lotes['Óleo mineral|O25-01'].quarentena"); print('  toast:', v.toast())
    v.ok('Vencido' in t and d == 40, 'lote vencido (07/2026) não é liberado para o disponível', f'quarentena depois = {d}; linha: {v.rowtxt("O25-01")}')
    # 4 · Restaurar demonstração mantém o filtro de local
    v.clk('Câmara fria'); v.clk('Restaurar demonstração'); v.clk('Restaurar'); fl = v.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)")
    v.ok(fl == ['Todos os locais'], 'Restaurar demonstração limpa o filtro de local', fl)
    # 5 · faixa da etapa 2: REQ-036 (OS-0420 Em execução) contada como "fora de Liberadas e Em execução"
    v.etapa(2); k2 = v.J(K); ph = v.rowtxt('REQ-036'); print('  k2:', k2)
    v.ok(not ('Em execução' in ph and '3 só consulta (O.S. fora de Liberadas e Em execução)' in k2), 'faixa da etapa 2 descreve certo as O.S. só consulta', k2)
    # 6 · confirmação no app lista itens não entregues
    v.mudar("c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const r=c.ordens['OS-0430'].req; cenEntregar(c,r,'Glifosato 480',320,'Marcos'); return cenConfirmarRecebimento(c,r);")
    v.abrir(); v.etapa(6); t = v.rowtxt('Recebimento confirmado no app'); print('  ', t)
    v.ok('2,4-D 806' not in t, 'movimento "Recebimento confirmado no app" lista só o que foi entregue e confirmado', t)
    # 7 · consumo do app sem sinal: chip "Aguardando sinal" passa da borda; números sem unidade
    v.mudar("const r=c.ordens['OS-0430'].req; cenEntregar(c,r,'2,4-D 806',160,'Marcos'); cenEntregar(c,r,'Óleo mineral',80,'Marcos'); cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);")
    v.abrir(); v.etapa(6); f = v.J(FORA); t = v.rowtxt('Consumo apontado no app'); print('  ', t)
    v.ok('Aguardando sinal' not in f, 'etapa 6: chip "Aguardando sinal" cabe na área', f)
    v.ok(' L' in t.split('Consumo apontado no app')[1].split('Marcos')[0], 'consumo apontado mostra quantidades com unidade', t)
    v.shot('ver_est_def_e6.png')
    # 8 · sinal volta: apontamento enviado, mas o movimento de consumo continua "Aguardando sinal"
    print('  ', v.mudar("return cenSinal(c,true);")); v.abrir(); v.etapa(6); t = v.rowtxt('Consumo apontado no app'); k6 = v.J(K)
    ap = v.cen("JSON.stringify([c.ordens['OS-0430'].ap.map(a=>a.sinc), c.app.fila])"); print('  ap/fila:', ap, '| k6:', k6)
    v.ok('Aguardando sinal' not in t and '0 aguardando sinal' in k6, 'após o sinal voltar, consumo deixa de aparecer "Aguardando sinal"', [t, k6])
    # 9 · ajuste aprovado sem documento na trilha
    v.etapa(5); v.rowbtn('INV-2609', 'Aprovar ajuste'); v.etapa(6); t = v.rowtxt('Ajuste de inventário'); print('  ', t)
    v.ok('INV-2609' in t or 'AJ-' in t, 'trilha do ajuste mostra o documento (INV/AJ)', t)
    v.ok(not v.erros(), 'sem erro de script', v.erros())
finally:
    v.fim()
