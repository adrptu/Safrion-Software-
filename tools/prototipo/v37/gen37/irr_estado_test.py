# -*- coding: utf-8 -*-
"""Teste do núcleo de estado da irrigação (irrigacao_estado.js + semente de dados_irrigacao.py) no Chrome headless, sem tela:
semente (P2 11,2 · P1 ≈8,4 · T7 ≈10,0), tarefas automáticas da Lagoa Grande (tarefa única, OS-0601…), prontidão, conflito, execução,
crédito parcial só na área coberta, conferência dentro e fora de 3 %, sem leitura não credita, limites só para as próximas e IDs sem colisão.
Uso: python3 irr_estado_test.py  (≈ 15 s)"""
import sys, os, time, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
import cenario, dados_irrigacao as DI
R = os.path.join(HERE, '_render'); os.makedirs(R, exist_ok=True)
open(os.path.join(R, '_irr_estado.html'), 'w', encoding='utf-8').write(
    '<!doctype html><html><head><meta charset="utf-8"><title>irr</title></head><body>irr<script>window.__err="";window.onerror=(m)=>{window.__err+=m+" | ";};\n'
    + cenario.js_prefixo() + DI.js_prefixo() + "function g2perfil(){return {k:'Ana',papeis:{gestor:'gestora'}};}" + '</script></body></html>')
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = None; OK = []; FAIL = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:600]))
try:
    c = Chrome(port=free()); J = c.js
    c.goto(f'http://127.0.0.1:{p}/_irr_estado.html', wait=0.8)
    J("localStorage.clear(); irrReset(); cenReset();")
    E = lambda expr: J(f"(()=>{{ try{{ const s=irrGet(); return {expr}; }}catch(e){{ return 'ERRO '+e.message; }} }})()")
    M = lambda fn: J(f"(()=>{{ const r=irrMudar(null,s=>{fn}); return r.erro||r.msg||''; }})()")
    chk('1 sem erro de carga', J("window.__err") == '', J("window.__err"))
    d = E("['P2','P1','T7'].map(k=>[irrN(irrDef(s,k),1),irrEst(s,s.setores[k])])")
    chk('2 semente: P2 11,2 medido · P1 ≈8,4 (sonda suspeita) · T7 ≈10,0 (sem dado)', d == [['11,2', False], ['8,4', True], ['10,0', True]], d)
    g = E("Object.values(s.ordens).filter(o=>o.faz==='LG').map(o=>[o.id,o.setor,o.etapa,o.passadas.length,irrJanO(o)])")
    print('    LG:', g)
    chk('3 Lagoa Grande: 6 tarefas automáticas (PV02, PV08, PV09, PV18, PV21, PV24) a partir de OS-0601, liberadas pela prontidão',
        [x[1] for x in g] == ['PV02', 'PV08', 'PV09', 'PV18', 'PV21', 'PV24'] and g[0][0] == 'OS-0601' and all(x[2] == 'Liberadas' for x in g), g)
    chk('4 gerar de novo não duplica (idempotente) e programar recupera a tarefa', E("(irrGerar(s), Object.keys(s.ordens).length)") == E("Object.keys(s.ordens).length")
        and 'recuperada' in M("irrProgramar(s,'PV02')") and E("Object.values(s.ordens).filter(o=>o.setor==='PV02').length") == 1)
    sel = E("['OS-0419','OS-0422','OS-0423','OS-0394'].map(id=>[id,irrEtapa(s,s.ordens[id]),irrSelos(s,s.ordens[id]).map(x=>x.t).join('|'),(irrProx(s,s.ordens[id])||{}).t])")
    print('    SR:', sel)
    chk('5 SR: OS-0419 Liberadas (Iniciar) · OS-0422 Janela a definir · OS-0423 conflito com a parada da B3 · OS-0394 divergência (Conferir medição)',
        sel[0][1] == 'Liberadas' and sel[0][3] == 'Iniciar irrigação' and 'Janela a definir' in sel[1][2] and 'Conflito · parada da B3' in sel[2][2] and sel[2][3] == 'Resolver conflito'
        and 'Divergência · −3,8 %' in sel[3][2].replace('-', '−') and sel[3][3] == 'Conferir medição', sel)
    av = E("irrChecar(s,s.ordens['OS-0419']).av.map(a=>a.t)"); cb = E("(x=>[irrN(x.cob,0),irrN(x.resta,1)])(irrCobre(s,s.ordens['OS-0419']))")
    chk('6 OS-0419: aviso de ponta parcial (20–21 h) e cobre 87 % da necessidade (resta 1,5 mm)', 'Ponta parcial (20–21 h)' in av and cb == ['87', '1,5'], [av, cb])
    op = E("irrOpcoes(s,'OS-0423').map(o=>o.t)")
    chk('7 conflito da OS-0423: opções calculadas 15:00–17:00 (logo depois da parada) e 21:00–23:00', op == ['Logo depois · hoje 15:00–17:00', 'À noite · hoje 21:00–23:00'], op)
    r = M("irrDefinirJanela(s,'OS-0423',irrOpcoes(s,'OS-0423')[0].inis)")
    chk('8 resolver conflito libera a OS-0423 com LIB-2292 (estimativa por ET não bloqueia)', 'LIB-2292' in r and E("s.ordens['OS-0423'].etapa") == 'Liberadas', r)
    jn = E("irrSugerir(s,'P2',s.ordens['OS-0422'].passadas.map(p=>p.dur),s.agora,'OS-0422').map(q=>irrQuando(q))")
    chk('9 janela sugerida da OS-0422: depois da OS-0419 na B2, fora da ponta e com 18 h entre passadas', jn == ['amanhã 21:00', '25/09 21:00'], jn)
    r = M("irrDefinirJanela(s,'OS-0422',[1260,1260])")
    chk('10 passadas sobrepostas são recusadas (a 2ª começa antes do fim da 1ª) e nada é gravado', E("s.ordens['OS-0422'].etapa") == 'A liberar' and 'começa antes do fim da passada 1' in r and E("s.ordens['OS-0422'].passadas[0].ini") is None, r)
    r = M("irrDefinirJanela(s,'OS-0422',[3*1440+1260,2*1440+1260])")
    chk('10b passada 2 antes da passada 1 é recusada (ordem de tempo)', 'A passada 2 começa antes do fim da passada 1' in r and E("s.ordens['OS-0422'].etapa") == 'A liberar', r)
    r = M("irrDefinirJanela(s,'OS-0422',irrSugerir(s,'P2',s.ordens['OS-0422'].passadas.map(p=>p.dur),s.agora,'OS-0422'))")
    chk('11 janela válida libera a OS-0422 com LIB-2291', 'LIB-2291' in r and E("s.ordens['OS-0422'].etapa") == 'Liberadas', r)
    chk('12 terminar sem iniciar é bloqueado com motivo', 'inicie' in M("irrTerminar(s,'OS-0419',80,8480)").lower())
    M("irrIniciar(s,'OS-0419')"); M("irrPausar(s,'OS-0419')")
    chk('13 pausa vira selo; término bloqueado enquanto pausada', E("irrSelos(s,s.ordens['OS-0419']).map(x=>x.t)") == ['Pausada'] and 'Retome' in M("irrTerminar(s,'OS-0419',80,8480)"))
    M("irrRetomar(s,'OS-0419')")
    M("{const o=s.ordens['OS-0419']; o.trilha.push({q:irrFimP(o,irrPassAtual(o)),ev:'Fixture: tempo decorrido'});}"); r = M("irrTerminar(s,'OS-0419',80,8480)")
    chk('14 término com hidrômetro 8.480 m³ (−1,9 %) encerra sozinho e credita 9,5 mm líquidos: P2 1,7 mm',
        E("s.ordens['OS-0419'].etapa") == 'Encerradas' and E("irrN(irrDef(s,'P2'),1)") == '1,7' and E("irrQuando(s.ordens['OS-0419'].passadas[0].fimReal)") == 'amanhã 10:41', [r, E("irrQuando(s.ordens['OS-0419'].passadas[0].fimReal)")])
    chk('15 crédito uma vez: repetir o término não duplica', 'Nenhuma passada' in M("irrTerminar(s,'OS-0419',80,8480)") and E("s.setores.P2.bal.ap.filter(a=>a.os==='OS-0419').length") == 1)
    # parcial na área coberta e conferência fora da tolerância
    M("irrIniciar(s,'OS-0423')"); M("{const o=s.ordens['OS-0423']; o.trilha.push({q:irrPassAtual(o).iniReal+60,ev:'Fixture: uma hora decorrida'});}"); r = M("irrTerminar(s,'OS-0423',21,800,true)")
    chk('16 parada antes (21 de 42 ha, 800 m³): crédito só na faixa coberta (3,8 mm × 95 % nos 21 ha); o T7 segue 10,0 mm fora da faixa',
        E("s.ordens['OS-0423'].etapa") == 'Em conferência' and E("irrN(irrDef(s,'T7'),1)") == '10,0' and E("(f=>f&&[irrN(f.cob,1),irrN(f.d,1)])(irrFaixaCob(s,'T7'))") == ['21,0', '6,4'] and 'divergência' in r.lower(),
        [r, E("irrN(irrDef(s,'T7'),1)"), E("irrFaixaCob(s,'T7')")])
    r = M("irrConferir(s,'OS-0423',null,'Leitura de campo conferida')")
    chk('17 conferir medição: hidrômetro prevalece e encerra sem novo crédito (T7 10,0 · faixa 6,4)', E("s.ordens['OS-0423'].etapa") == 'Encerradas' and E("irrN(irrDef(s,'T7'),1)") == '10,0' and 'faixa de 21,0 ha: 6,4 mm' in r, r)
    # Ausência não vira leitura estimada. Fixture de tempo não é um comando da UI.
    M("irrIniciar(s,'OS-0602')")
    M("{const o=s.ordens['OS-0602']; o.trilha.push({q:irrFimP(o,irrPassAtual(o)),ev:'Fixture: tempo decorrido'});}")
    antes = E("JSON.stringify(s.ordens['OS-0602'])")
    r = M("irrTerminar(s,'OS-0602',s.setores.PV08.ha,null)")
    vol = E("Math.round(s.ordens['OS-0602'].passadas[0].lam*s.setores.PV08.ha*10)")
    chk('18 ausência de leitura recusa sem alterar ordem/crédito; volume explícito permite concluir', 'volume medido' in r
        and E("JSON.stringify(s.ordens['OS-0602'])") == antes and E("irrN(irrDef(s,'PV08'),1)") == '6,4'
        and isinstance(vol, int) and vol > 0 and 'encerrada' in M(f"irrTerminar(s,'OS-0602',s.setores.PV08.ha,{vol})") and E("irrDef(s,'PV08')<6.4"), [r, vol])
    r = M("irrLimites(s,'P2',{lmax:4.5,imin:18,efic:90})")
    chk('19 limites valem só para as próximas: OS-0422 liberada mantém 2 passadas', E("s.ordens['OS-0422'].passadas.length") == 2 and 'OS-0422 não muda' in r, r)
    r = M("irrSondaMarcar(s,'SO-P2','Suspeita','salto')")
    chk('20 marcar sonda P2 suspeita: P2 passa a estimativa por ET', E("irrEst(s,s.setores.P2)") is True and 'estimativa' in r, r)
    r = M("irrProgramar(s,'P2')")
    chk('21 programar P2 recupera a OS-0422 aberta (tarefa única)', 'OS-0422 recuperada' in r, r)
    J("cenMudar(null,c=>{ c.ordens['OS-0603']={id:'OS-0603',etapa:'A liberar',ins:[],selos:[],ap:[]}; return {msg:''}; })")
    r = M("irrProgramar(s,'PV03')")
    chk('22 IDs não colidem com o cenário da O.S. (OS-0603 ocupado no cenário)', E("Object.keys(s.ordens).includes('OS-0603')") is False or 'OS-0603' not in r, r)
    r = J("irrReclassTudo(null,'OS-0422',{prod:'Nitrato de cálcio',dose:5,mot:'deficiência de Ca'}).msg||''")
    chk('23 adicionar produtos: v2 volta a A liberar com o agrônomo e entra no cenário da O.S. (gravação única)', E("irrEtapa(s,s.ordens['OS-0422'])") == 'A liberar' and E("(irrProx(s,s.ordens['OS-0422'])||{}).t") == 'Liberar na O.S.'
        and J("cenGet().ordens['OS-0422'].osc.novo.versao") == 'v2' and E("s.ordens['OS-0422'].fert.cen") is True, r)
    # ---- correções da verificação v43 (STEP 4) ----
    J("localStorage.clear(); irrReset(); cenReset();")
    # v2 não fura o bloqueio: ordem em conflito com a parada não aceita produtos
    r = J("(irrReclassTudo(null,'OS-0423',{prod:'Nitrato de cálcio',dose:5,mot:'Ca'}).erro)||''")
    chk('25 adicionar produtos na OS-0423 em conflito com a parada da B3 é recusado (nada no cenário da O.S.)', 'Resolva antes' in r and 'parada da B3' in r and J("!!cenGet().ordens['OS-0423']") is False and E("!!s.ordens['OS-0423'].fert") is False, r)
    # v2 liberada ocupa a bomba: outra ordem na mesma bomba e horário não libera
    r = J("(irrReclassTudo(null,'OS-0419',{prod:'Nitrato de cálcio',dose:5,mot:'Ca'}).msg)||''"); J("cenMudar(null,c=>cenLiberar(c,'OS-0419'))")
    r2 = M("irrDefinirJanela(s,'OS-0422',[22*60,1440+22*60])")
    chk('26 v2 da OS-0419 liberada na O.S. segura a B2: OS-0422 na mesma janela fica A liberar com conflito', E("irrEtapa(s,s.ordens['OS-0419'])") == 'Liberadas' and E("s.ordens['OS-0422'].etapa") == 'A liberar' and 'OS-0419' in r2, [r, r2])
    J("localStorage.clear(); irrReset(); cenReset();")
    # adicionar produtos durante a execução: v1 fica na faixa coberta, a v2 segue as etapas da O.S. e a água apontada lá entra no balanço
    M("irrIniciar(s,'OS-0419')"); M("irrAvanco(s,'OS-0419',30)")
    r = J("(irrReclassTudo(null,'OS-0419',{prod:'Nitrato de potássio',dose:7,mot:'K'}).msg)||''")
    st = E("[irrEtapa(s,s.ordens['OS-0419']),irrSelos(s,s.ordens['OS-0419']).map(x=>x.t).join('|'),(irrProx(s,s.ordens['OS-0419'])||{}).t,s.ordens['OS-0419'].passadas[0].st,irrN(irrDef(s,'P2'),1),(f=>f&&irrN(f.cob,1))(irrFaixaCob(s,'P2'))]")
    chk('27 v2 durante a execução: Em execução · Revisão de saldo pendente · Liberar saldo na O.S.; passada 1 Parcial (v1, 30 ha creditados só na faixa)',
        st[0] == 'Em execução' and 'Revisão de saldo pendente' in st[1] and st[2] == 'Liberar saldo na O.S.' and st[3] == 'Parcial' and st[4] == '11,2' and st[5] == '30,0' and J("cenGet().ordens['OS-0419'].area") == 50, [r, st])
    J("cenMudar(null,c=>cenLiberar(c,'OS-0419'))")
    chk('28 depois da liberação na O.S.: a ordem na irrigação segue a O.S. (Liberadas → Iniciar execução na O.S.), sem beco sem saída',
        E("[irrEtapa(s,s.ordens['OS-0419']),(irrProx(s,s.ordens['OS-0419'])||{}).t]") == ['Liberadas', 'Iniciar execução na O.S.'], E("[irrEtapa(s,s.ordens['OS-0419']),(irrProx(s,s.ordens['OS-0419'])||{}).t]"))
    J("cenMudar(null,c=>{ const o=c.ordens['OS-0419']; o.etapa='Em execução'; o.realizado=50; o.saldo=0; return {msg:''}; })")
    d = E("[irrN(irrDef(s,'P2'),1),irrFaixaCob(s,'P2'),irrApsSetor(s,'P2').filter(a=>a.os==='OS-0419').length,irrEtapa(s,s.ordens['OS-0419'])]")
    chk('29 O.S. apontou os 50 ha do saldo: v1 (30 ha) + v2 (50 ha) completam a volta e o P2 recebe o crédito (menor lâmina líquida), sem faixa pendente',
        d[0] != '11,2' and float(d[0].replace(',', '.')) < 2.5 and d[1] is None and d[2] == 2 and d[3] == 'Em execução', d)
    J("cenMudar(null,c=>{ c.ordens['OS-0419'].etapa='Encerradas'; return {msg:''}; })")
    chk('30 O.S. encerrada: a ordem fica Encerradas na irrigação e o crédito vira definitivo', E("[irrEtapa(s,s.ordens['OS-0419']),irrAberta(s.ordens['OS-0419']),irrApsSetor(s,'P2').filter(a=>a.os==='OS-0419').some(a=>a.prov)]") == ['Encerradas', False, False])
    # Restaurar demonstração (cenário zerado) leva a irrigação junto: sem v2 órfã
    J("cenReset();")
    chk('31 cenário da O.S. restaurado: a irrigação volta à semente (sem v2 órfã)', E("[!!s.ordens['OS-0419'].fert,s.ordens['OS-0419'].etapa]") == [False, 'Liberadas'], E("[!!s.ordens['OS-0419'].fert,s.ordens['OS-0419'].etapa]"))
    # fertirrigação parada por falta de insumo: mesma situação da O.S. e a água do setor pode ir sem o produto
    si = E("(x=>[x.c,x.sit,x.l,x.acao,x.dono])(irrSituacao(s,'P1'))")
    chk('32 P1: OS-0418 parada por falta de insumo (vermelho, como na O.S.) e próximo passo Programar só água · João', si[0] == 'red' and si[1] == 'Impedida' and si[2] == 'falta insumo · OS-0418' and si[3] == ['Programar só água', 'IR-02.dc.html#programar=P1'] and si[4] == 'João', si)
    r = M("irrProgramar(s,'P1')")
    chk('33 programar P1 cria a ordem só de água (OS-0418 segue parada na O.S.)', 'criada' in r and 'só água' in r and E("Object.values(s.ordens).filter(o=>o.setor==='P1').length") == 1, r)
    # avisos de lâmina: acima da necessidade e abaixo do limiar
    J("localStorage.clear(); irrReset(); cenReset();")
    M("irrIniciar(s,'OS-0419')"); M("{const o=s.ordens['OS-0419']; o.trilha.push({q:irrFimP(o,irrPassAtual(o)),ev:'Fixture: tempo decorrido'});}"); M("irrTerminar(s,'OS-0419',80,8480)")
    av = E("(o=>{ const t=irrClone(o); t.passadas[0].ini=22*60; t.passadas[1].ini=1440+22*60; return irrChecar(s,t).av.map(a=>a.t); })(s.ordens['OS-0422'])")
    chk('34 P2 com 1,7 mm: OS-0422 (12,15 mm líquidos) na janela 23/09 22:00 → aviso Lâmina acima da necessidade (não bloqueia)', any(a.startswith('Lâmina acima da necessidade') for a in av), av)
    av2 = E("irrChecar(s,s.ordens['OS-0422']).av.map(a=>a.t)")
    chk('35 sem janela: OS-0422 avisa Abaixo do limiar (1,7 de 8,0 mm)', 'Abaixo do limiar · déficit 1,7 de 8,0 mm' in av2, av2)
    av3 = E("(()=>{ const x=s.setores.PV06; const n=irrNec(s,'PV06'); const t={id:'novo',faz:'LG',setor:'PV06',passadas:[{n:1,ini:21*60,dur:n.dur,lam:n.por,st:'Programada'}],exec:{pausas:[]}}; return irrChecar(s,t).av.map(a=>a.t); })()")
    chk('36 programar PV06 (3,2 mm, limiar 9,0) mostra o aviso Abaixo do limiar', 'Abaixo do limiar · déficit 3,2 de 9,0 mm' in av3, av3)
    # ações por link direto só quando valem
    va = E("[irrAcaoVale(s,s.ordens['OS-0422'],'conferir'),irrAcaoVale(s,s.ordens['OS-0392'],'janela'),irrAcaoVale(s,s.ordens['OS-0422'],'conflito'),irrAcaoVale(s,s.ordens['OS-0423'],'conflito'),irrAcaoVale(s,s.ordens['OS-0422'],'janela')]")
    chk('37 link direto: conferir/janela/conflito inválidos no estado são recusados com motivo; válidos passam', all(va[:3]) and va[3] == '' and va[4] == '', va)
    chk('24 sem erro de execução', J("window.__err") == '', J("window.__err"))
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\n{len(OK)} ok · {len(FAIL)} falhas', FAIL)
sys.exit(1 if FAIL or not OK else 0)   # SINT-T01: falha não sai com 0

