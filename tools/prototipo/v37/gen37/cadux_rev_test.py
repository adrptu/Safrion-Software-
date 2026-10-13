# -*- coding: utf-8 -*-
"""CADUX · regressão dos achados da revisão adversarial do Codex (base 5d533a8), sem navegador (lê project/ e roda a lógica no node,
cadux_node.py). Cada bloco cobre um achado pelo caminho real (formulário, endereço, voltar do navegador), não pela função isolada:
os mutantes MB, MD, MA e MC da revisão sobreviviam porque os testes chamavam a regra direto ou gravavam o armazenamento à mão.
O que depende de layout, foco e toque (toque duplo a 390, 1ª linha acima da dobra) fica no cadux_rev_nav_test.py.
Uso: python3 cadux_rev_test.py   (sai com 1 se alguma regra falhar)"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:600]), flush=True)
def run(pag, cen, **k):
    o = roda(pag, AUX + cen, **k)
    if o.get('__errs'): chk(f'{pag} sem erro de script ({k.get("hash","")})', False, o['__errs'])
    return o
# voltar do navegador (o stub do cadux_node dispara o popstate; na 1ª entrada da pilha, marca que saiu da tela) e o estado do painel
VOLTA = r'''
function volta(){ history.back(); v(); }
function saiu(){ return !!location.saiu; }
function pn(gid){ const F=painel(gid); return F?{cons:!!F.cons,edit:!!F.edit,warn:!!F.warn,t:F.title,pai:!!F.temPai}:null; }
'''

# ---------------- 1 · S3: voltar do navegador ou do Android com alteração não salva (R06, AC-21) ----------------
for larga in (True, False):
    L = '1440' if larga else '390'
    # painel aberto pelo endereço de outra frente (X-REG da MA): era a 1ª entrada da pilha, e o voltar saía da tela
    o = run('CD-03', VOLTA + r'''OUT.h0=history._pilha.length; consGo('g_atv','Editar ativo'); fset('g_atv','custo_h','222'); OUT.antes=pn('g_atv');
      volta(); OUT.saiu=saiu(); OUT.p=pn('g_atv'); OUT.val=fval('g_atv','custo_h');
      painel('g_atv').keep(); v(); OUT.cont=[pn('g_atv'),fval('g_atv','custo_h')];
      cancela('g_atv'); OUT.cons=pn('g_atv'); OUT.custo=g2find(RW(C,'g_atv'),'a02').v.custo_h; OUT.pil=[history._i,history._pilha.length];
      volta(); OUT.saiu2=saiu();''', hash='#reg=a02', larga=larga)
    chk(f'R06/AC-21 {L} CD-03#reg=a02 (link da MA) › Editar ativo › R$/h 222 › voltar: fica na tela, painel em edição com o aviso e o 222',
        o.get('saiu') is False and (o.get('p') or {}).get('warn') and o.get('val') == '222', o)
    chk(f'R06 {L} "Continuar editando" mantém o 222; Cancelar › Descartar volta à consulta sem gravar (R$ 180/h) e o voltar seguinte sai da tela (sem toque morto)',
        (o.get('cont') or [{}])[0].get('edit') and o['cont'][1] == '222' and (o.get('cons') or {}).get('cons') and o.get('custo') == 180 and o.get('saiu2') is True, o)
    # ficha da fazenda (CD-01): o grupo não é parâmetro de item no endereço, e a ficha não empilhava nada
    o = run('CD-01', VOLTA + r'''let x=mestre('SR'); x.dx_ficha(); v(); consGo('g_faz','Editar fazenda'); fset('g_faz','nome','Santa Rita EDITADA');
      volta(); OUT.saiu=saiu(); OUT.p=pn('g_faz'); OUT.val=fval('g_faz','nome');''', larga=larga)
    chk(f'R06/AC-21 {L} CD-01 › Santa Rita › Ver ficha › Editar fazenda › digitar › voltar: fica, com o aviso e o nome digitado',
        o.get('saiu') is False and (o.get('p') or {}).get('warn') and o.get('val') == 'Santa Rita EDITADA', o)
    o = run('CD-01', VOLTA + r'''let x=v(); x.cd_nfaz(); v(); fset('g_faz','nome','Fazenda Nova X'); volta(); OUT.saiu=saiu(); OUT.p=pn('g_faz'); OUT.val=fval('g_faz','nome');''', larga=larga)
    chk(f'R06/AC-21 {L} CD-01 › + Criar fazenda › nome › voltar: fica, com o aviso e o nome', o.get('saiu') is False and (o.get('p') or {}).get('warn') and o.get('val') == 'Fazenda Nova X', o)
    o = run('CD-04', VOLTA + r'''const e=RW(C,'g_eq').find(r=>/Campo 1/.test(r.v.nome)); let x=mestre(e.id); x.dx_ficha(); v(); consGo('g_eq','Editar');
      const k=painel('g_eq').fields.find(f=>!f.dis&&f.isTxt).fid.replace('fx_g_eq_',''); fset('g_eq',k,'Campo 1 X'); volta(); OUT.saiu=saiu(); OUT.p=pn('g_eq'); OUT.val=fval('g_eq',k);''', larga=larga)
    chk(f'R06/AC-21 {L} CD-04 › Campo 1 › Ver ficha › Editar › digitar › voltar: fica, com o aviso e o digitado', o.get('saiu') is False and (o.get('p') or {}).get('warn') and o.get('val') == 'Campo 1 X', o)
# sem alteração, o voltar fecha a edição (volta à consulta) em vez de ficar sem efeito; e Salvar consome a entrada da edição
o = run('CD-03', VOLTA + r'''consGo('g_atv','Editar ativo'); volta(); OUT.p=pn('g_atv'); OUT.saiu=saiu();
  consGo('g_atv','Editar ativo'); fset('g_atv','custo_h','200'); salva('g_atv'); OUT.s=pn('g_atv'); OUT.pil=[history._i,history._pilha.length]; volta(); OUT.saiu2=saiu();''', hash='#reg=a02')
chk('R06 voltar sem alteração fecha a edição e volta à consulta (sem toque morto); depois de Salvar, o voltar seguinte sai da tela',
    (o.get('p') or {}).get('cons') and o.get('saiu') is False and (o.get('s') or {}).get('cons') and o.get('saiu2') is True, o)

# ---------------- 2 · S3: "‹ {pai}" no painel em edição descartava a alteração (R06) ----------------
o = run('CD-03', VOLTA + r'''let x=mestre('conjuntos'); x=v(); const cj=RW(C,'g_cj').find(r=>/Trator 02/.test(r.v.maq)&&/PJ-3030/.test(r.v.impl||''))||RW(C,'g_cj')[0]; abre('g_cj',cj.id);
  let F=painel('g_cj'); const fil=F.c.blocos.find(b=>b.temFil); const f=fil.fil.find(z=>/Trator 02/.test(z.t))||fil.fil[0]; OUT.filho=f.t; f.go(); v();
  const Fc=painel('g_atv'); OUT.cons=pn('g_atv'); const rid=g2st(C,'g_atv').fm.rid; const antes=g2find(RW(C,'g_atv'),rid).v.custo_h;
  consGo('g_atv','Editar ativo'); OUT.ed=pn('g_atv'); fset('g_atv','custo_h','999');
  Fc.paiGo(); v(); OUT.depois=pn('g_atv'); OUT.cj=!!painel('g_cj'); OUT.custo=[antes,g2find(RW(C,'g_atv'),rid).v.custo_h];''')
chk('R06 CD-03 conjunto › Trator 02: "‹ {conjunto}" na consulta, some na edição (A04)', (o.get('cons') or {}).get('pai') and (o.get('ed') or {}).get('pai') is False, o)
chk('R06 CD-03 "‹ {pai}" chamado com R$/h 999 não salvo: avisa e mantém a edição; o Trator continua com o valor de antes',
    (o.get('depois') or {}).get('warn') and (o.get('depois') or {}).get('edit') and o.get('cj') is False and o.get('custo', [0, 1])[0] == o['custo'][1], o)

# ---------------- 3 · S3: R$/h do conjunto com uma fonte só entre CD-03 e CD-02 (X-CAD-1); mutante MD (CD-03 deixa de gravar) ----------------
# caminho real: o CD-03 salva pelo formulário; o armazenamento que ele deixou é o que o CD-02 e o próprio CD-03 leem ao abrir (nada gravado à mão)
o = run('CD-03', r'''consGo('g_atv','Editar ativo'); fset('g_atv','custo_h','200'); OUT.t=salva('g_atv'); OUT.ls=ls();''', hash='#reg=a02')
ls3 = json.loads(o.get('ls') or '{}')
antes = 'Object.entries(' + json.dumps(ls3) + ').forEach(([k,x])=>localStorage.setItem(k,x));'
o2 = run('CD-02', r'''OUT.p=cons('g_rend');''', hash='#aba=operacoes&op=OP1&rend=r1', antes=antes)
o3 = run('CD-03', r'''OUT.p=cons('g_atv'); OUT.lin=linhaTxt('g_atv','a02');''', hash='#reg=a02', antes=antes)
o0 = run('CD-02', r'''OUT.p=cons('g_rend');''', hash='#aba=operacoes&op=OP1&rend=r1')
chk('X-CAD-1 sem nada salvo, o rendimento do Trator 02 + PJ-3030 soma R$ 313,00/h e R$ 14,49/ha (base)', o0.get('p') and 'R$ 313,00/h' in o0['p']['txt'] and 'R$ 14,49/ha' in o0['p']['txt'], o0.get('p'))
chk('X-CAD-1 CD-03 › Trator 02 › R$/h 200 › Salvar: o CD-02 soma R$ 333,00/h e R$ 15,42/ha (lê o que o CD-03 salvou)',
    'R$ 200,00/h' in (o.get('t') or '') and o2.get('p') and 'R$ 333,00/h' in o2['p']['txt'] and 'R$ 15,42/ha' in o2['p']['txt'], [o.get('t'), ls3, o2.get('p')])
chk('X-CAD-1 voltar ao CD-03#reg=a02 mostra R$ 200,00/h no painel e na linha (antes: R$ 180,00/h, um 3º valor)',
    o3.get('p') and 'R$ 200,00/h' in o3['p']['txt'] and '200,00' in (o3.get('lin') or ''), [o3.get('p') and o3['p']['txt'][:400], o3.get('lin')])
# o Planejar safra lê o mesmo armazenamento pela mesma função (cadCustoH, cadls.js): a configuração "Padrão do cadastro" das safras abertas
# segue o CD-03; a safra encerrada guarda o da época e continua "Padrão do cadastro" (registro fechado); a troca de conjunto oferece o valor salvo
SAFQ = r'''const S=(k)=>{ const g=GR('g_rend_'+k); const x=cfgLeaves(g2rows(C,g)).find(q=>q.id==='r1.1'); return x?[x.v.maq,x.v.custo_h,Math.round(x.v.custo_ha*100)/100]:null; };
  OUT.ab=S('S2627'); OUT.lg=S('LG2627'); OUT.enc=S('S2526'); OUT.op=conjOpts('r1').map(o=>o.t).find(t=>/Trator 02/.test(t));
  C.state.saf='S2627'; OUT.oa=rendLive('origem_c',cfgLeaves(g2rows(C,GR('g_rend_S2627'))).find(q=>q.id==='r1.1').v,C);
  C.state.saf='S2526'; OUT.oe=rendLive('origem_c',cfgLeaves(g2rows(C,GR('g_rend_S2526'))).find(q=>q.id==='r1.1').v,C);'''
os_ = run('SAF', SAFQ, antes=antes); os0 = run('SAF', SAFQ)
chk('X-CAD-1 SAF sem nada salvo: Pulverização r1 com R$ 180/h de máquina, 313 R$/h e 14,49 R$/ha (base)', os0.get('ab') == [180, 313, 14.49] and os0.get('enc') == [180, 313, 14.49], os0)
chk('X-CAD-1 SAF depois do CD-03 (Trator 02 R$/h 200): safras abertas com 333 R$/h e 15,42 R$/ha, os números do CD-02; "Padrão do cadastro (CD-02)" continua',
    os_.get('ab') == [200, 333, 15.42] and os_.get('lg') == [200, 333, 15.42] and os_.get('oa') == 'Padrão do cadastro (CD-02)', os_)
chk('X-CAD-1 SAF safra encerrada (25/26) guarda o da época (313 R$/h) e a origem continua "Padrão do cadastro (CD-02)"; a troca de conjunto oferece o Trator 02 com máquina 200',
    os_.get('enc') == [180, 313, 14.49] and os_.get('oe') == 'Padrão do cadastro (CD-02)' and 'máquina 200 ' in (os_.get('op') or ''), os_)
h = open(os.path.join(HERE, 'project', 'CD-03.dc.html'), encoding='utf-8').read()
chk('X-CAD-1 a ajuda do CD-03 diz onde o valor vale ("custo da O.S." saiu; rendimento do conjunto e "Padrão do cadastro" das safras abertas)',
    'o rendimento e o custo da O.S. usam este valor' not in h and 'O rendimento usa este valor.' not in h and 'das safras abertas no Planejar safra leem este valor' in h)

# ---------------- 4 · S3: CD-06 com saldo e lotes do cenário do Estoque (não do build) ----------------
# cenário como fica depois de liberar uma O.S. que reserva 100 L a mais do Fungicida A (F26-02: 545 físico, 165 reservado); o EST lê o mesmo
import cenario
cen = cenario.seed(); cen['lotes']['Fungicida A|F26-02']['reservado'] = 165
antes = "localStorage.setItem('talhao-os-cenario-v1'," + json.dumps(json.dumps(cen)) + ");"
oe = run('EST', r'''OUT.l=(linhas('g_lot').find(r=>/F26-02/.test(r.t))||{}).t;''', antes=antes)
o = run('CD-06', r'''const r=leaves(RW(C,'g_itm')).find(r=>r.v.item==='Fungicida A'); abre('g_itm',r.id); const F=painel('g_itm'); const b=F.c.blocos;
  OUT.trava=(b.find(k=>k.t==='Unidade e embalagem').lin.find(z=>z&&z.l==='Unidade-base')||{}).v; OUT.lot=b.find(k=>k.t==='Locais').rows.map(x=>x.c.map(c=>c.t).join(' | ')); fecha('g_itm');
  const n=leaves(RW(C,'g_itm')).find(r=>r.v.item==='NPK 20-05-20'); abre('g_itm',n.id); OUT.npk=(painel('g_itm').c.blocos[0].lin.find(z=>z&&z.l==='Unidade-base')||{}).v;
  consGo('g_itm','Editar item'); OUT.npkDis=fdis('g_itm','un'); fecha('g_itm'); OUT.acts=(CAD_ACTS.g_itm(C,n)||[]).map(a=>a.h);''', antes=antes)
chk('Estoque (EST) com o cenário: F26-02 com 545 L físico, 165 L reservado e 380 L disponível', '545 L | 165 L' in (oe.get('l') or '') and '380 L' in (oe.get('l') or ''), oe)
chk('Achado 4 CD-06: o painel do Fungicida A lê o mesmo cenário (545 L no Estoque, 380 L disponíveis; lote F26-02 545 L | 380 L), não o 480 do build',
    o.get('trava') == 'L · travada: item com 545 L no Estoque (380 L disponíveis)' and any('545 L | 380 L' in x for x in (o.get('lot') or [])), o)
chk('Achado 4 CD-06: NPK 20-05-20 todo reservado (8.000 kg físicos, 0 disponível) continua com a unidade travada e sem Excluir (trava pelo físico)',
    (o.get('npk') or '').startswith('kg · travada: item com 8.000 kg no Estoque (0 kg disponíveis)') and o.get('npkDis') is True and any('saldo' in (h or '') for h in (o.get('acts') or [])), o)

# ---------------- 7 · mutante MB: unidade-base pelo formulário (filtro da grandeza e validação ao salvar) ----------------
o = run('CD-06', r'''const r=leaves(RW(C,'g_itm')).find(r=>r.v.item==='Calcário dolomítico'); abre('g_itm',r.id); consGo('g_itm','Editar item');
  OUT.o=fopts('g_itm','un'); fset('g_itm','un','L'); OUT.t=salva('g_itm'); OUT.e=erros('g_itm'); OUT.un=g2find(RW(C,'g_itm'),r.id).v.un;
  fset('g_itm','un','kg'); OUT.t2=salva('g_itm'); OUT.un2=g2find(RW(C,'g_itm'),r.id).v.un;''')
chk('B24 pelo formulário: Calcário dolomítico (t, sem saldo nem plano) só oferece kg, sc 60 kg e t; L forçado é recusado no campo e nada muda; kg salva',
    sorted(x for x in (o.get('o') or []) if x and x != 'Escolha…') == ['kg', 'sc 60 kg', 't'] and any(e.startswith('un:') and 'mesma grandeza' in e for e in (o.get('e') or []))
    and o.get('un') == 't' and o.get('un2') == 'kg', o)

# ---------------- 6 · S3: defensivo criado com "Outro grupo…" pede o local próprio (NR-31) e nasce com lote e validade (R14) ----------------
o = run('CD-06', r'''let x=v(); x.c6_criar(); v(); fset('g_itm','item','Nematicida X'); painel('g_itm').fields.find(f=>f.fid==='fx_g_itm_grupo').set({target:{value:OUTRO_G}}); v();
  OUT.nnat0=fval('g_itm','nnat'); fset('g_itm','ngrupo','Nematicidas'); salva('g_itm'); OUT.e0=erros('g_itm');
  painel('g_itm').fields.find(f=>f.fid==='fx_g_itm_nnat').set({target:{value:'3.1.02 · Defensivos'}}); v(); OUT.ctrl=fval('g_itm','ctrl');
  fset('g_itm','un','L'); fset('g_itm','emb','Galão'); fset('g_itm','cont','5'); fset('g_itm','ctrl','Sem lote'); OUT.t=salva('g_itm'); OUT.e=erros('g_itm');
  fset('g_itm','local','Almox. defensivos'); OUT.t2=salva('g_itm'); OUT.sub=(v().mx_itens.find(i=>i.t==='Nematicidas')||{}).sub;''')
chk('R14/X01 "Outro grupo…": a natureza do grupo novo nasce vazia e é obrigatória (antes: Fertilizantes escondido, que desligava o local próprio)',
    o.get('nnat0') == '' and any(e.startswith('nnat:') for e in (o.get('e0') or [])), o)
chk('Achado 6 "Outro grupo…" Nematicidas + natureza Defensivos: controle vira "Lote e validade"; sem local é recusado (NR-31); com o local, cria o grupo com "Lote e validade"',
    o.get('ctrl') == 'Lote e validade' and o.get('t') == '' and any(e.startswith('local:') and 'NR-31' in e for e in (o.get('e') or []))
    and 'grupo Nematicidas criado (3.1.02 · Defensivos)' in (o.get('t2') or '') and o.get('sub') == 'Lote e validade', o)

# ---------------- 5 · S3: Boa Vista sem "Definir polígono" no CD-01det; a mesma frase do limite do CD-01 (R18, AC-25) ----------------
for t in ('B1', 'T1', 'T2'):
    od = run('CD-01det', r'''let x=v(); OUT.r=[x.geo_mapa,x.geo_lim,x.geo_limT]; OUT.pg=Object.keys(x).filter(k=>/^pg_|^det_prim|^det_pend|^det_planok/.test(k));''', hash='#talhao=' + t)
    oc = run('CD-01', r'''OUT.p=cons('g_tal');''', hash='#talhao=' + t)
    r = od.get('r') or [None, None, '']
    chk(f'R18/AC-25 CD-01det {t}: sem editor de polígono simulado (nenhum "Definir polígono" nem "Nova versão"), com a frase do limite da fazenda',
        r[0] is False and r[1] is True and 'ainda não existe no protótipo' in (r[2] or '') and not od.get('pg'), od)
    if t == 'B1':
        chk('R18 B1: o CD-01det e o painel do CD-01 dizem a mesma coisa (sem contradição "validado" × "sem polígono")', oc.get('p') and oc['p']['prox'] == r[2], [oc.get('p') and oc['p']['prox'], r[2]])
olg = run('CD-01det', r'''let x=v(); OUT.r=[x.geo_mapa,x.geo_lim,x.geo_des];''', hash='#talhao=PV01')
chk('R18 Lagoa Grande (PV01): a porta continua sendo o Mapa IN-04 ("Desenhar no mapa ›", link)', olg.get('r') == [True, False, 'IN-04.dc.html#desenhar=PV01'], olg)
h = open(os.path.join(HERE, 'project', 'CD-01det.dc.html'), encoding='utf-8').read()
chk('Achado 12 CD-01det: sem "Nova versão do polígono", sem "Definir polígono" e sem "Cadastrar talhão" (BOT-03: "Criar talhão")',
    'Nova versão do polígono' not in h and 'Definir polígono' not in h and 'Cadastrar talhão' not in h and 'Criar talhão' in h)

# ---------------- 8 · S4: aviso SEL-02 com a entidade do parâmetro do endereço e o valor cru ----------------
casos = [('CD-05', '#grp=zz', 'Grupo de insumo “zz”'), ('CD-06', '#local=zz', 'Local de estoque “zz”'), ('CD-03', '#cj=zz', 'Conjunto “zz”'),
         ('CD-03', '#atv=zz', 'Ativo “zz”'), ('CD-02', '#cv=zz', 'Cultivar “zz”'), ('CD-05', '#par=zz', 'Parceiro “zz”'), ('CD-06', '#item=zz', 'Item “zz”')]
for larga in (True, False):
    for pg, hh, ent in casos:
        o = run(pg, r'''let x=v(); OUT.a=x.dx_aviso; OUT.p=GRIDS.some(g=>painel(g.id)); OUT.sel=st().mx_sel;''', hash=hh, larga=larga)
        chk(f'SEL-02 {"1440" if larga else "390"} {pg}{hh}: "{ent} indisponível", nada aberto, nenhum outro selecionado',
            (o.get('a') or '').startswith(ent + ' indisponível') and 'c_zz' not in (o.get('a') or '') and o.get('p') is False and o.get('sel') == '', o)

# ---------------- 10 · S4: o número a resolver da Boa Vista fecha com o Próximo passo ----------------
o = run('CD-01', r'''OUT.m=(v().mx_itens.find(i=>i.id==='BV')||{}).lab; let x=mestre('BV'); OUT.ch=x.dx_chT; OUT.p=[x.dx_p.proxT,x.dx_p.mais];''')
chk('Achado 10 Boa Vista: "3 a resolver" no mestre e no detalhe = CAR + contrato BV-03 + B1 do Próximo passo', o.get('m') == 'Boa Vista · 1 · 3 a resolver' and o.get('ch') == '3 a resolver'
    and (o.get('p') or ['', ''])[1].startswith('e mais 2:'), o)

# ---------------- 13 · S4: endereço ----------------
o = run('CD-01', r'''OUT.h=hash(); OUT.sel=st().mx_sel;''', hash='#reg=SR')
chk('Achado 13 CD-01#reg=SR é reescrito para #faz=SR (§0.8) e mostra a Santa Rita', o.get('h') == '#faz=SR' and o.get('sel') == 'SR', o)
o = run('CD-01', r'''let x=v(); OUT.h=hash(); OUT.sel=st().mx_sel; OUT.av=x.dx_aviso; OUT.toast=st().g2toast; OUT.p=cons('g_tal');''', hash='#faz=BV&talhao=T2')
chk('Achado 13 CD-01#faz=BV&talhao=T2: abre o T2 da Santa Rita com aviso visível (não troca de fazenda em silêncio)',
    o.get('h') == '#faz=SR&talhao=T2' and o.get('sel') == 'SR' and 'é da Santa Rita, não da Boa Vista' in (o.get('av') or '') and 'é da Santa Rita' in (o.get('toast') or ''), o)
o = run('CD-05', r'''OUT.h=hash(); OUT.sel=st().mx_sel; OUT.p=cons('g_forn');''', hash='#papel=fornecedor&par=F03')
chk('Achado 13 CD-05#papel=fornecedor&par=F03 abre a Agro Norte com o papel Fornecedor escolhido (não descarta o papel)', o.get('sel') == 'fornecedor' and o.get('p') and 'Agro Norte' in o['p']['t'] and 'papel=fornecedor' in (o.get('h') or ''), o)

# ---------------- 11 · S4: a 390, o painel do item tem "‹ {grupo}" (ESPECIFICACAO §2.1) e volta ao grupo ----------------
o = run('CD-01', VOLTA + r'''let x=mestre('SR'); abre('g_tal','T2'); const F=painel('g_tal'); OUT.p=[F.temPai,F.paiT]; F.paiGo(); v(); OUT.depois=!!painel('g_tal'); OUT.sel=st().mx_sel;''', larga=False)
chk('Achado 11 a 390 o painel do T2 tem "‹ Santa Rita", que fecha o painel e deixa a Santa Rita escolhida', o.get('p') == [True, '‹ Santa Rita'] and o.get('depois') is False and o.get('sel') == 'SR', o)
o = run('CD-01', r'''let x=mestre('SR'); abre('g_tal','T2'); OUT.p=painel('g_tal').temPai;''')
chk('Achado 11 a 1440 o painel não ganha "‹ {grupo}" (o detalhe continua à vista ao lado)', o.get('p') is False, o)
h = open(os.path.join(HERE, 'project', 'CD-01.dc.html'), encoding='utf-8').read()
chk('Achado 11 BOT-01 abaixo de 1024 px: a ação do Próximo passo do detalhe é secundária (o verde fica no "+ Criar" do cabeçalho)', '.cmd-dc .g2prox-prim{background:#FFFFFF!important' in h)

# ---------------- 7 · mutantes MA ("‹ ›" com o filtro de coluna) e MC (escolher no mestre não grava o contexto global) ----------------
o = run('CD-01', r'''let x=mestre('SR'); globalThis.document={getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[]};
  const ci=GR('g_tal').cols.findIndex(c=>c.k==='sis'); v().g_tal_head[ci].fmenu(); let fm=v().g_tal_fm; fm.vals.filter(z=>z.t!=='Pivô central').forEach(z=>z.tog()); v().g_tal_fm.ok(); v();
  const vis=v().g_tal_rows.map(r=>r.id); OUT.vis=vis; abre('g_tal',vis[0]); const F=painel('g_tal'); OUT.nav=[F.pos,F.proxL,F.antOff];''')
vis = o.get('vis') or []
chk('MA "‹ ›" percorre só o que a grade mostra com o filtro de coluna (Sistema = Pivô central na Santa Rita: "1 de 3", e não "1 de 8"; o próximo é o 2º visível)',
    len(vis) == 3 and (o.get('nav') or [None])[0] == '1 de 3' and o['nav'][2] is True and o['nav'][1] == 'Próximo: ' + vis[1], o)
o = run('CD-01', r'''let x=mestre('BV'); x=mestre('LG'); OUT.ss=sessionStorage.getItem('mapa-ctx');''', antes="sessionStorage.setItem('mapa-ctx',JSON.stringify({esc:true,mf_faz:'Santa Rita'}));")
o2 = run('CD-01', r'''let x=mestre('BV'); OUT.ss=sessionStorage.getItem('mapa-ctx');''')
chk('MC X-CTX/C04: escolher Boa Vista e Lagoa Grande no mestre não grava o contexto global (continua Santa Rita; sem contexto, continua sem)',
    json.loads(o.get('ss') or '{}').get('mf_faz') == 'Santa Rita' and o2.get('ss') is None, [o, o2])

print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
