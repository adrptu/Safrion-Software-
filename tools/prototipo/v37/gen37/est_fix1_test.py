# -*- coding: utf-8 -*-
"""Correções do verificador · Estoque, parte 1 (EST.dc.html no Chrome headless, 1440×1000, cenário limpo, ≤ 15 verificações, < 40 s):
lote vencido não volta ao disponível, grades sem rolagem horizontal (etapas 1, 4 e 5), faixa da etapa 2 com O.S. impedida,
contador com o mesmo papel da trilha e Restaurar demonstração limpando o filtro de local."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

# grade visível: [scrollWidth, clientWidth] da área que rola
OVF = "[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).map(x=>[x.parentElement.scrollWidth,x.parentElement.clientWidth])"
# botão/chip inteiro dentro da caixa da grade (linha que contém ts, elemento com texto t): true = à vista sem rolar; 'teclado' = ação
# alcançável pelo foco; 'rolando' = selo inteiro ao rolar a grade (TABELAS-FOCO item 6: a grade rola dentro da caixa, a página não)
INTEIRO = """((ts,t)=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(x=>r.innerText.indexOf(x)>=0)); if(!r) return 'sem linha';
  const e=[...r.querySelectorAll('button,span')].find(x=>x.innerText.trim()===t); if(!e) return 'sem '+t; const sc=r.closest('[role=table]').parentElement;
  const den=()=>{ const box=sc.getBoundingClientRect(), b=e.getBoundingClientRect(); return b.width>0&&b.left>=box.left-0.5&&b.right<=box.right+0.5; };
  sc.scrollLeft=0; if(den()) return true;   // à vista sem rolar a grade
  const f=e.closest('button'); if(f){ f.focus(); f.dispatchEvent(new FocusEvent('focusin',{bubbles:true})); return den()?'teclado':false; }   // ação: o foco do teclado traz inteira para a caixa (focusin despachado: sem janela ativa o Chrome não o dispara)
  e.scrollIntoView({block:'nearest',inline:'nearest'}); return den()?'rolando':false; })"""


# TABELAS-FOCO (5983172395) item 6: com uma variável por coluna a grade pode rolar dentro da própria caixa; a página não rola
def cabe(E): return bool(E.J("document.documentElement.scrollWidth<=innerWidth+1"))


E = Est()
try:
    E.abrir()
    # 1 · recebimento de lote vencido: tudo em quarentena, situação "Vencido" e a grade continua cabendo
    E.clk('Conferir NF 4533')
    E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '0'); E.setv('fx_g_rec_quar', '20000'); E.setv('fx_g_rec_val', '08/2026'); E.setv('fx_g_rec_obs', 'Lote vencido'); E.salvar()
    t = E.rowtxt('NF 4533'); print('NF 4533:', t, E.J(OVF))
    E.ok('Vencido' in t and 'Aguarda laudo' not in t and cabe(E), 'NF 4533 vencida: situação "Vencido" (não "Aguarda laudo") e grade sem rolagem', t)
    # 2 · etapa 4: lote vencido sem "Liberar após inspeção"; faixa separa vencido de inspeção
    E.etapa(4); t = E.rowtxt('S58-0926'); k = E.k(); print('S58-0926:', t, '| k4:', k)
    sl, vl = E.cel('S58-0926', 'Situação do lote'), E.cel('S58-0926', 'Validade')   # TABELAS-FOCO: situação e validade em colunas próprias
    E.ok('Liberar após inspeção' not in t and sl == 'Vencido não volta ao disponível' and vl == '08/2026', 'lote vencido S58-0926: sem "Liberar após inspeção"; Situação do lote "Vencido · não volta ao disponível", Validade 08/2026', (t, sl, vl))
    E.ok('Bloqueado para inspeção: KCl 60% 10.000 kg' in k and 'vencido, fora do disponível: Semente de soja 58 W 20.000 kg' in k, 'faixa da etapa 4 separa inspeção de vencido', k)
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['K26-11'],'Liberar após inspeção')") in (True, 'teclado'), 'etapa 4: página sem rolagem; "Liberar após inspeção" do KCl inteiro (à vista ou pelo teclado)', E.J(OVF))
    st = E.cen("[c.lotes['Semente de soja 58 W|S58-0926'].quarentena, c.movs.filter(m=>m.tipo==='inspecao').length]")
    E.ok(st == [20000, 0], 'cenário: 20.000 kg do lote vencido seguem bloqueados, nenhuma liberação', st)
    # 3 · lote vencido que entra por outra tela (cenReceber, Óleo mineral 07/2026) também fica sem liberação
    print('cenReceber:', E.mudar("return cenReceber(c,'Óleo mineral','O26-07V',40,'L','Almox. defensivos','07/2026','NF 9001',false);"))
    E.abrir(); E.etapa(4); t = E.rowtxt('O26-07V'); print('O26-07V:', t)
    sl, vl = E.cel('O26-07V', 'Situação do lote'), E.cel('O26-07V', 'Validade')
    E.ok('Liberar após inspeção' not in t and sl.startswith('Vencido') and vl == '07/2026', 'lote vencido recebido por cenReceber: sem "Liberar após inspeção", Situação do lote "Vencido", Validade 07/2026', (t, sl, vl))
    # 4 · etapa 5: grade cabe e "Aprovar ajuste" inteiro, antes e depois de uma nova contagem com diferença
    E.etapa(5)
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['INV-2609'],'Aprovar ajuste')") in (True, 'teclado'), 'etapa 5: página sem rolagem; "Aprovar ajuste" da INV-2609 inteiro (à vista ou pelo teclado)', E.J(OVF))
    ops = E.J("[...document.querySelectorAll('#fx_g_cnt_contador option')].map(o=>o.value)") if E.clk('+ Nova contagem') == 'ok' else []
    print('contadores:', ops)
    E.setv('fx_g_cnt_lote', E.J("[...document.querySelector('#fx_g_cnt_lote').options].map(o=>o.value).find(v=>v.startsWith('D26-01'))")); E.setv('fx_g_cnt_cont', '290'); E.salvar()
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['INV-2612'],'Aprovar ajuste')") in (True, 'teclado') and E.J(f"({INTEIRO})(['INV-2612'],'Recontar')") in (True, 'teclado'),
         'nova contagem INV-2612 com diferença: grade sem rolagem, Recontar e Aprovar ajuste inteiros', E.J(OVF))
    # 5 · mesma palavra para Rui em toda a tela (contador = almoxarife, como na trilha)
    E.row('INV-2609'); a = E.val('fx_g_cnt_contador'); b = E.J("document.body.innerText"); E.fechar()
    E.ok(ops == ['Paula (almoxarife)', 'Rui (almoxarife)'] and a == 'Rui (almoxarife)' and 'conferente' not in b,
         'contador "Rui (almoxarife)" (mesmo papel da trilha), sem "conferente" na tela', [ops, a])
    # 6 · faixa da etapa 2 separa consulta por fase de bloqueio por O.S. impedida
    E.etapa(2); k = E.k(); print('k2:', k)
    # contagens da faixa = linhas da grade (a Lagoa Grande sintética trouxe OS-0507 impedida e OS-0508 em conferência)
    sits = E.J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(x=>x.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
      const io=hs.indexOf('O.S.'), is=hs.indexOf('SITUAÇÃO'); return [...t.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent).map(r=>{const c=r.querySelectorAll('[role=cell]'); return [c[io].innerText.trim(), c[is].innerText.replace(/\\s+/g,' ').trim()];});})()""") or []
    bl = [o for o, s_ in sits if s_.startswith('Bloqueada')]; co = [o for o, s_ in sits if 'sem nova entrega' in s_]
    E.ok(f'{len(co)} só consulta (O.S. fora de Liberadas e Em execução) · {len(bl)} bloqueado{"s" if len(bl) != 1 else ""} por O.S. impedida' in k and 'OS-0420' in bl and 'OS-0418' in co and 'OS-0417' in co,
         f'faixa da etapa 2: {len(co)} só consulta por fase e {len(bl)} bloqueados por O.S. impedida, iguais às linhas da grade (OS-0420 bloqueada; OS-0417 e OS-0418 só consulta)', (k, bl, co))
    d31 = E.cel('REQ-031', 'Detalhe')
    E.ok(d31 == '5.000 kg solicitado − 3.500 kg consumido − 500 kg em custódia', 'REQ-031 (em conferência): Detalhe mostra a conta do saldo (Entregue 5.000 kg inclui o que voltou; A entregar 1.000 kg)', d31)
    # 7 · Restaurar demonstração limpa o filtro de local
    E.etapa(4); E.clk('Câmara fria'); f0 = E.J("[...document.querySelectorAll('[role=row].g2kid')].length")
    E.clk('Restaurar demonstração'); E.clk('Restaurar')
    on = E.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"); n = E.J("[...document.querySelectorAll('[role=row].g2kid')].length"); print('filtro:', f0, on, n)
    E.ok(f0 == 2 and on == ['Todos os locais'] and n > f0,'Restaurar demonstração volta o filtro para "Todos os locais"', [f0, on, n])
    er = E.erros(); E.ok(not er, 'sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
