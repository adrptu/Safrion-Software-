# -*- coding: utf-8 -*-
"""CADUX · regras dos Cadastros sem navegador (roda depois do build.py; lê project/ e executa a lógica da página no node, cadux_node.py).
Prova as regras da ESPECIFICACAO §3 que não dependem de layout: seleção pelo id e "N de M" (R02), herança do pai na criação (R03),
nada muda ao só olhar (R01), inativo só com o filtro (R08), fonte só para leitura (R09, X-CAD-1), custo de pessoa fora da lista (R10),
último valor (R11), restrição legal no mestre (R13), criação sem padrão escondido (R14/X01), só cria onde é a fonte (R15), assinatura (R16),
endereços de outras frentes (R19, SEL-02 indisponível), unidade só na mesma grandeza (B24), homônimos, contexto da fazenda (X-CTX) e um alvo
por linha (BOT-07). O que depende de layout, foco e toque fica no teste de navegador (cadux_cd01_test.py, cadux_tarefas_test.py).
Uso: python3 cadux_unit_test.py   (sai com 1 se alguma regra falhar)"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:500]), flush=True)
def run(pag, cen, **k):
    o = roda(pag, AUX + cen, **k)
    if o.get('__errs'): chk(f'{pag} sem erro de script ({k.get("hash","")})', False, o['__errs'])
    return o

# ---------------- CD-01 · Fazendas, áreas e talhões ----------------
o = run('CD-01', r'''let x=v(); OUT.m=x.mx_itens.map(i=>i.id+'|'+i.lab);
  OUT.n={}; ['SR','BV','LG'].forEach(id=>{ x=mestre(id); OUT.n[id]=x.cd_conta; }); OUT.h=hash();
  // R01: abrir 10 registros não muda dado
  const dados=()=>JSON.stringify(RW(C,'g_tal').map(r=>({id:r.id,v:r.v,k:(r.kids||[]).map(k=>({id:k.id,v:k.v}))}))); const antes=dados(); x=mestre(''); const ids=v().g_tal_rows.filter(r=>!/^F/.test(r.id)).map(r=>r.id).slice(0,10); ids.forEach(id=>{ try{ abre('g_tal',id); }catch(e){} });
  OUT.r01=[ids.length, dados()===antes];
  // BOT-07: cada linha de talhão tem 1 alvo e a linha não é ponto de Tab
  x=mestre('SR'); OUT.alvos=alvos('g_tal');''')
chk('R02 Santa Rita 8 de 8, Boa Vista 1 de 1, Lagoa Grande 23 de 23 (filhos pelo id da fazenda)', o.get('n') == {'SR': '8 de 8', 'BV': '1 de 1', 'LG': '23 de 23'}, o.get('n'))
chk('R13 Lagoa Grande com as outorgas vencidas no número a resolver do mestre', any(m.startswith('LG|Lagoa Grande · 23 · 7 a resolver') for m in o.get('m', [])), o.get('m'))
chk('R01 abrir 10 registros não muda nenhum dado do cenário', o.get('r01') == [10, True], o.get('r01'))
al = o.get('alvos', [])
chk('BOT-07 CD-01: cada linha tem um único alvo (botão com nome acessível) e a linha não é ponto de Tab', al and all(a['n'] == 1 and a['tab'] == '-1' for a in al), al)

o = run('CD-01', r'''let x=mestre('BV'); x.cd_criar(); x=v(); OUT.herda=[fval('g_tal','faz'),fdis('g_tal','faz')]; painel('g_tal').cancel(); v();
  x=mestre(''); x.cd_criar(); x=v(); OUT.todas=fval('g_tal','faz'); fset('g_tal','t','T9'); salva('g_tal'); OUT.err=erros('g_tal'); painel('g_tal').cancel(); v();
  // homônimo: T2 na Boa Vista
  x=mestre('BV'); x.cd_criar(); x=v(); fset('g_tal','t','T2'); fset('g_tal','decl','50'); salva('g_tal'); OUT.err2=erros('g_tal'); OUT.p=cons('g_tal'); OUT.h=hash();
  const F=painel('g_tal'); const ou=F&&F.c&&(F.c.sec||[]).find(s=>/^\+ Criar outro talhão/.test(s.t)); OUT.outro=ou&&ou.t;
  // R11: "+ Criar outro talhão" não repete a área
  if(ou) ou.go(); v(); OUT.r11=[fval('g_tal','faz'),fval('g_tal','decl'),fval('g_tal','t')]; painel('g_tal').cancel(); v();
  x=mestre(''); x.mx_setq({target:{value:'T2'}}); x=v(); OUT.busca=v().g_tal_rows.filter(r=>!/^F/.test(r.id)).map(r=>r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '));''')
chk('R03 "+ Criar talhão" com a Boa Vista escolhida abre com Fazenda = Boa Vista, trocável', o.get('herda') == ['Boa Vista', False], o.get('herda'))
chk('R03 em "Todas", a fazenda vem vazia e é obrigatória', o.get('todas') == '' and any(e.startswith('faz:') for e in (o.get('err') or [])), [o.get('todas'), o.get('err')])
chk('Homônimo: "T2" na Boa Vista é aceito (outra fazenda) e abre o painel do novo, com o endereço da Boa Vista',
    not o.get('err2') and o.get('p') and 'T2' in o['p']['t'] and 'faz=BV' in (o.get('h') or ''), [o.get('err2'), o.get('p') and o['p']['t'], o.get('h')])
chk('R11 "+ Criar outro talhão na Boa Vista" (no painel do novo) herda a fazenda e deixa nome e área vazios', o.get('outro') == '+ Criar outro talhão na Boa Vista' and o.get('r11') == ['Boa Vista', '', ''], [o.get('outro'), o.get('r11')])
bs = o.get('busca', [])
chk('R02 busca "T2" mostra os dois homônimos, cada um com a sua fazenda', len([b for b in bs if b.startswith('T2')]) == 2, bs)

o = run('CD-01', r'''OUT.h=hash(); const F=painel('g_tal'); OUT.p=cons('g_tal');''', hash='#tal=T2')
chk('R19 CD-01 #tal=T2 abre o T2 da Santa Rita e reescreve o endereço (#faz=SR&talhao=T2)', o.get('h') == '#faz=SR&talhao=T2' and o.get('p') and 'T2' in o['p']['t'], [o.get('h'), o.get('p')])
o = run('CD-01', r'''let x=v(); OUT.h=hash(); OUT.av=[x.dx_temAviso,x.dx_aviso,x.dx_avisoT]; OUT.p=!!painel('g_tal'); OUT.sel=st().mx_sel; OUT.prox=x.dx_p&&x.dx_p.proxCor;''', hash='#talhao=ZZ9')
av = o.get('av') or [None, '', '']
chk('SEL-02 talhão indisponível: lista sem seleção, aviso visível com saída, nada aberto, sem dizer se existe', av[0] and 'indisponível' in av[1] and 'Nada foi aberto' in av[1] and av[2] and not o.get('p') and o.get('sel') == '' and o.get('h') == '', o)
o = run('CD-01', r'''let x=v(); OUT.sel=st().mx_sel; OUT.dx=x.dx_t; OUT.ss=sessionStorage.getItem('mapa-ctx');''', hash='#faz=BV',
        antes="sessionStorage.setItem('mapa-ctx',JSON.stringify({esc:true,mf_faz:'Santa Rita'}));")
chk('X-CTX link direto para a Boa Vista com a Santa Rita global: mostra a Boa Vista e não troca o contexto global', o.get('sel') == 'BV' and o.get('dx') == 'Boa Vista' and json.loads(o.get('ss') or '{}').get('mf_faz') == 'Santa Rita', o)
o = run('CD-01', r'''let x=v(); OUT.sel=st().mx_sel; OUT.dx=x.dx_t;''', antes="sessionStorage.setItem('mapa-ctx',JSON.stringify({esc:true,mf_faz:'Lagoa Grande'}));")
chk('X-CTX sem endereço, a fazenda escolhida no seletor global vem selecionada', o.get('dx') == 'Lagoa Grande', o)
o = run('CD-01', r'''let x=v(); OUT.dx=x.dx_t;''', antes="sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Lagoa Grande'}));")
chk('X-CTX fazenda que não foi escolhida num seletor (sem esc) não vale', o.get('dx') != 'Lagoa Grande', o)
o = run('CD-01', r'''assinTrava=()=>'Assinatura inadimplente: ampliar a área está suspenso até regularizar (Configurações › Assinatura).';
  let x=mestre('SR'); x.cd_criar(); OUT.toast=st().g2toast; x=v(); OUT.form=!!painel('g_tal');''')
chk('R16 assinatura inadimplente: "+ Criar talhão" recusa antes de abrir, com o motivo', o.get('form') is False and 'inadimplente' in (o.get('toast') or ''), o)
o = run('CD-01', r'''let x=mestre('SR'); const ab=st().cdaba; OUT.on=[x.cab_criar_on];
  ['cdt1_go','cdt2_go'].forEach(k=>{ if(x[k]){ x[k](); x=v(); OUT.on.push(x.cab_criar_on); } });''')
chk('R15 CD-01: Ambiental e Água sem "+ Criar" (a fonte é o CAR, o KML e a outorga do CONTROLE-01)', o.get('on', [None])[0] is True and len(o.get('on', [])) >= 3 and not any(o['on'][1:]), o)

# ---------------- CD-02 · Culturas, cultivares e operações ----------------
o = run('CD-02', r'''let x=v(); x.mx_setq({target:{value:'Soja'}}); x=v(); OUT.c=x.c2_conta;''')
chk('AC-10 CD-02: a busca "Soja" traz as 3 cultivares da soja (3 de 7)', o.get('c') == '3 de 7', o)
o = run('CD-02', r'''let x=v(); OUT.h=hash(); OUT.f=['conj','larg','maq','impl'].map(k=>k+':'+fdis('g_rend',k)+':'+fval('g_rend',k)); OUT.op=fval('g_rend','op');
  fset('g_rend','vel','8'); fset('g_rend','efic','70'); fset('g_rend','pess','1'); fset('g_rend','vig','2027-06-30'); salva('g_rend'); OUT.e=erros('g_rend');''', hash='#aba=operacoes&cj=k1&novo=1')
chk('X-CAD-1 cj=k1&novo=1: criação do rendimento com o conjunto e a operação do CD-03; largura e R$/h só leitura',
    o.get('op') == 'Pulverização' and all(':true:' in f for f in o.get('f', [])) and o.get('h') == '#aba=operacoes&op=OP1', o)
chk('X-CAD-1 conjunto que já tem rendimento na mesma cultura é recusado no campo do conjunto', any(e.startswith('cjid:') and 'já tem rendimento' in e for e in (o.get('e') or [])), o.get('e'))
o = run('CD-02', r'''OUT.p=cons('g_rend'); OUT.l=v().g_rend_rows.map(r=>r.id);''', hash='#aba=operacoes&op=OP1&rend=r1',
        antes="localStorage.setItem('talhao-os-cadastros-v1',JSON.stringify({ativos:{a02:{nome:'Trator 02',custo_h:200}}}));")
chk('X-CAD-1 mudar o R$/h do Trator 02 no CD-03 (180 → 200) muda o custo do rendimento (R$ 333,00/h e R$ 15,42/ha)',
    o.get('p') and 'R$ 333,00/h' in o['p']['txt'] and 'R$ 15,42/ha' in o['p']['txt'], o.get('p'))
o = run('CD-02', r'''let x=mestre('OP6'); x.c2_criar(); x=v(); const f=painel('g_rend').fields.find(f=>f.fid==='fx_g_rend_cjid'); const eq=f.opts.find(o=>/pessoas\)$/.test(o.t)); f.set({target:{value:eq.v}}); v();
  OUT.eq=eq.t; OUT.ids=painel('g_rend').fields.map(f=>f.fid.replace('fx_g_rend_','')); OUT.pess=[fval('g_rend','pess'),fdis('g_rend','pess')]; OUT.modo=fval('g_rend','modo');''', hash='#aba=operacoes')
chk('X-CAD-1 rendimento de equipe do CD-04 continua possível; custo só somado (sem "Custo por pessoa", G1)',
    o.get('eq') and 'pess_rs' not in o.get('ids', []) and o.get('pess', [None, None])[1] is True and o.get('modo') == 'Informado', o)
o = run('CD-02', r'''OUT.p=cons('g_cv'); OUT.h=hash();''', hash='#reg=cv3')
chk('R19 CD-02 #reg=cv3 abre a cultivar 64 Z com "Vincular semente da 64 Z"; rendimentos só em consulta (I07)',
    o.get('p') and o['p']['prim'] == 'Vincular semente da 64 Z' and 'Abrir em Operações' in o['p']['txt'] and o.get('h') == '#cul=CU1&cv=cv3', o)

# ---------------- CD-03 · Máquinas ----------------
o = run('CD-03', r'''OUT.p=cons('g_atv'); OUT.h=hash();''', hash='#reg=a02')
chk('R19 CD-03 #reg=a02 abre o Trator 02', o.get('p') and 'Trator 02' in o['p']['t'], o)
o = run('CD-03', r'''let x=v(); x.c3_criar(); x=v(); OUT.cl0=[fval('g_atv','classe'),fval('g_atv','exige')]; painel('g_atv').cancel(); v();
  x=mestre('pulverizador'); x.c3_criar(); x=v(); OUT.pul=[fval('g_atv','classe'),fval('g_atv','exige'),fdis('g_atv','classe')];''')
chk('R14/X01 CD-03: em "Todos" a classe vem vazia; no Pulverizador, classe herdada e "Exige calibração: Sim" visível',
    o.get('cl0', [1])[0] == '' and o.get('pul', [0, 0])[:2] == ['Pulverizador', 'Sim'], o)

o = run('CD-03', r'''let x=v(); g2open(C,GR('g_atv'),'a05',null); v(); g2editar(C,GR('g_atv'),'a05'); v(); fset('g_atv','sit','Inativo'); salva('g_atv'); OUT.err=erros('g_atv');
  painel('g_atv')&&painel('g_atv').close(); x=v(); OUT.vis=v().g_atv_rows.map(r=>r.id).indexOf('a05'); OUT.qf=(v().g_atv_cqf||[]).map(c=>c.t+' '+c.n);
  location.hash='#reg=a05'; __ev.hashchange.forEach(f=>f({})); x=v(); OUT.h=hash(); OUT.p=painel('g_atv')&&painel('g_atv').title; OUT.qf2=st().c3qf; OUT.vis2=v().g_atv_rows.map(r=>r.id).indexOf('a05');''')
chk('R08 ativo inativado sai de "Todos" e só aparece no filtro "Inativos"', o.get('vis') == -1 and 'Inativos 1' in (o.get('qf') or []), [o.get('err'), o.get('vis'), o.get('qf')])
chk('R08 pedido pelo endereço, o inativo abre em consulta com o filtro "Inativos" ligado', o.get('p') == 'Ativo · Pulverizador PJ-3030' and o.get('qf2') == 'inat' and o.get('vis2', -1) >= 0 and o.get('h') == '#atv=a05', o)

# ---------------- CD-04 · Pessoas ----------------
o = run('CD-04', r'''OUT.p=cons('g_pes'); OUT.h=hash(); OUT.cols=GR('g_pes').cols.map(c=>c.l);''', hash='#reg=p2')
chk('R19 CD-04 #reg=p2 abre o Marcos', o.get('p') and 'Marcos' in o['p']['t'], o)
chk('R10 CD-04: custo-hora fora das colunas da lista', o.get('cols') and not any('R$' in c or 'Custo' in c for c in o['cols']), o.get('cols'))
o = run('CD-04', r'''OUT.p=cons('g_pes');''', hash='#reg=p1')
chk('P3 rótulo "Aprovar O.S. (agrônomo)" e a Ana mantém a habilidade', o.get('p') and 'Aprovar O.S. (agrônomo)' in o['p']['txt'], o.get('p'))

# ---------------- CD-05 · Parceiros ----------------
o = run('CD-05', r'''OUT.p=cons('g_forn'); OUT.h=hash();''', hash='#reg=F03')
chk('R19 CD-05 #reg=F03 abre a Agro Norte', o.get('p') and 'Agro Norte' in o['p']['t'], o)
o = run('CD-05', r'''let x=v(); x.mx_setq({target:{value:'Tebuconazol'}}); x=v(); OUT.c=x.cd5_conta; OUT.crt=[]; x.mx_setq({target:{value:''}}); x=v();
  const g=x.mx_itens.find(i=>/Grupos de insumo/.test(i.t)); if(g){ g.go(); x=v(); } OUT.crt=x.cab_criar_on;''')
chk('AC-10 CD-05: "Tebuconazol" acha os fornecedores homologados do grupo do insumo', (o.get('c') or '').startswith('3 de'), o)
chk('R15 CD-05: Grupos de insumo sem "+ Criar" (a fonte é o CD-06)', o.get('crt') is False, o)

# ---------------- CD-06 · Produtos ----------------
o = run('CD-06', r'''let x=v(); x.mx_setq({target:{value:'Herbicidas'}}); x=v(); OUT.c=x.c6_conta;
  OUT.un=[c6unTroca('kg','t',''),c6unTroca('kg','L',''),c6unTroca('kg','t','há saldo no Estoque'),c6unTroca('L','L','x')];''')
chk('AC-10 CD-06: "Herbicidas" traz os itens do grupo', (o.get('c') or '').startswith('5 de'), o)
u = o.get('un', [None] * 4)
chk('B24 unidade-base: troca só dentro da mesma grandeza (kg → t sim; kg → L não); com saldo, travada', u[0] == '' and 'mesma grandeza' in (u[1] or '') and 'travada' in (u[2] or '') and u[3] == '', u)
o = run('CD-06', r'''let x=mestre(RW(C,'g_grp').find(g=>g.v.nome==='Fungicidas').id); x.c6_criar(); x=v(); OUT.f=['grupo','un','emb','ctrl','local'].map(k=>k+'='+fval('g_itm',k));
  fset('g_itm','item','Fungicida teste'); salva('g_itm'); OUT.e=erros('g_itm');''')
fs = dict(x.split('=', 1) for x in o.get('f', []))
chk('R14/X01 CD-06: fungicida novo com o grupo herdado, sem unidade, sem "Saco", controle do grupo e local vazio',
    fs.get('grupo') == 'Fungicidas' and fs.get('un') == '' and fs.get('emb') == '' and fs.get('ctrl') and fs.get('local') == '', fs)
es = o.get('e') or []
chk('R14 item sem unidade-base não salva; defensivo pede o local (NR-31)', any(e.startswith('un:') for e in es) and any(e.startswith('local:') for e in es), es)
o = run('CD-06', r'''const g=RW(C,'g_grp').find(g=>g.v.nome==='Fungicidas'); let x=mestre(g.id); x.dx_ficha(); v(); consGo('g_grp','Editar grupo'); fset('g_grp','nome','Fungicidas agrícolas'); salva('g_grp'); fecha('g_grp');
  x=mestre(g.id); x.c6_criar(); v(); OUT.d=[fval('g_itm','grupo'),fval('g_itm','ctrl')]; fset('g_itm','item','Fungicida Z'); fset('g_itm','un','L'); fset('g_itm','emb','Galão'); fset('g_itm','cont','5'); salva('g_itm'); OUT.e=erros('g_itm');''')
chk('R14 renomear o grupo de defensivos não tira o local próprio (NR-31) nem o controle padrão do grupo',
    o.get('d') == ['Fungicidas agrícolas', 'Lote e validade'] and any(e.startswith('local:') and 'NR-31' in e for e in (o.get('e') or [])), o)
o = run('CD-06', r'''OUT.p=cons('g_itm'); OUT.h=hash();''', hash='#reg=i5')
chk('R19 CD-06 #reg= abre o item no painel', o.get('p') is not None, o)

# ---------------- CD-07 · Estrutura gerencial ----------------
o = run('CD-07', r'''let x=v(); OUT.prim=x.dx_p.primT; OUT.on=[x.cab_criar_on]; ['cultura','processo','natureza'].forEach(d=>{ x=mestre(d); OUT.on.push(x.cab_criar_on); });''')
chk('CD-07 Próximo passo da tela: "Publicar estrutura v6 (3 alterações)"', o.get('prim') == 'Publicar estrutura v6 (3 alterações)', o)
chk('R15 CD-07 sem "+ Criar código" em Cultura e Processo; com ele em Todas e Natureza', o.get('on') == [True, False, False, True], o.get('on'))
o = run('CD-07', r'''OUT.p=cons('g_dim'); OUT.h=hash(); painel('g_dim').c.sec[0] && 0; g2editar(C,GR('g_dim'),'d12'); v(); OUT.acts=(painel('g_dim').acts||[]).map(a=>a.h);
  painel('g_dim').cancel(); v(); g2editar(C,GR('g_dim'),'d12'); v(); fset('g_dim','sup','3.1.02'); salva('g_dim'); OUT.ciclo=erros('g_dim');''', hash='#dim=natureza&cod=3.1.02')
chk('CD-07 #dim=natureza&cod=3.1.02 (link do CD-06) abre o código com os grupos que usam a natureza', o.get('p') and 'Defensivos' in o['p']['t'] and 'Fungicidas' in o['p']['txt'], o.get('p'))
chk('CD-07 código com subcódigos não se exclui; superior não pode ser subcódigo do próprio código',
    any('subcódigos' in (a or '') for a in o.get('acts', [])) and any(e.startswith('sup:') for e in (o.get('ciclo') or [])), [o.get('acts'), o.get('ciclo')])
o = run('CD-07', r'''let x=v(); OUT.av=x.dx_aviso; OUT.p=!!painel('g_dim');''', hash='#cod=XX9')
chk('SEL-02 CD-07 código indisponível: aviso, nada aberto', 'indisponível' in (o.get('av') or '') and o.get('p') is False, o)

# vazio com filtro de coluna (achado do tabelas_cad_test reescrito, 09/10): o registro escondido pelo filtro da coluna não pode virar
# "nenhum encontrado, crie um" (risco de duplicar); com coluna filtrada vale o vazio da grade, com "Limpar filtros"
o = run('CD-03', r'''let x=v(); g2set(C,'g_atv',{f:{classe:['Irrigação']}}); x=v(); x.mx_setq({target:{value:'Silo'}}); x=v();
  OUT.cad=x.c3_v_tem; OUT.cadT=x.c3_v_t; OUT.grade=x.g_atv_empty; OUT.limpa=typeof x.g_atv_clear; x.g_atv_clear(); x=v(); OUT.n=x.c3_conta;
  x.mx_setq({target:{value:'Silo XYZ'}}); x=v(); OUT.cad2=x.c3_v_t; OUT.grade2=x.g_atv_empty;''')
chk('Vazio com filtro de coluna: o CD-03 não diz "nenhum ativo encontrado, crie" (Silo existe, escondido pela coluna Classe); a grade mostra "Limpar filtros", que traz o Silo',
    o.get('cad') is False and o.get('grade') is True and o.get('limpa') == 'function' and o.get('n') == '1 de 15', o)
chk('Vazio sem filtro de coluna: a busca sem resultado diz o termo e onde criar (e não o vazio da grade)', 'Silo XYZ' in (o.get('cad2') or '') and o.get('grade2') is False, o)

# X01 no CD-02 (achado do verif_cad2 reescrito, 09/10): em "Todas as operações" o rendimento novo vem sem operação e a lista mostra
# "Escolha…" (sem isso o navegador exibe "Pulverização" e o salvar diz "Informe operação")
o = run('CD-02', r'''let x=v(); x.c2t1_go(); x=v(); x.c2_criar(); v(); OUT.op=fval('g_rend','op'); OUT.o=fopts('g_rend','op'); OUT.cj=fopts('g_rend','cjid').filter(t=>t==='Escolha…').length;''')
chk('X01 CD-02: rendimento novo em "Todas as operações" com a operação vazia e "Escolha…" à vista (uma vez em cada lista)', o.get('op') == '' and (o.get('o') or [''])[0] == 'Escolha…' and o.get('cj') == 1, o)

# AC-13: os três controles "sem teste: criar" do REQUISITOS §4 (A5, A6 e talhão único na fazenda, D2)
o = run('CD-02', r'''let x=v(); x.c2t1_go(); x=v(); edita('g_op','OP1'); OUT.op=rotulos('g_op'); fecha('g_op');
  x=v(); x.c2_criar(); v(); OUT.rend=rotulos('g_rend'); fecha('g_rend');''')
dis = [l for l in (o.get('op') or []) + (o.get('rend') or []) if any(w in (l or '').lower() for w in ('dispens', 'aprova', 'isent'))]
chk('A5 CD-02: o formulário da operação e o do rendimento não têm campo de dispensa de aprovação (APROV-04)', o.get('op') and o.get('rend') and not dis, [dis, o.get('op')])
o = run('CD-02', r'''let x=v(); abre('g_cv','cv1'); OUT.p=cons('g_cv'); fecha('g_cv'); x=v(); x.c2_criar(); v(); OUT.reg=fopts('g_cv','reg'); OUT.regv=fval('g_cv','reg'); fecha('g_cv');''')
chk('A6 CD-02: a cultivar mostra o registro como "RNC · referência" e a criação só oferece referência oficial ou cadastro próprio (sem valor livre)',
    o.get('p') and 'RNC · referência' in o['p']['txt'] and o.get('reg') == ['RNC · referência', 'Cadastro próprio'] and o.get('regv') == 'RNC · referência', o)
o = run('CD-01', r'''let x=mestre('SR'); x.cd_criar(); x=v(); fset('g_tal','t','T2'); fset('g_tal','decl','10'); salva('g_tal'); OUT.e=erros('g_tal'); OUT.n=v().cd_conta; fecha('g_tal'); OUT.n2=v().cd_conta;''')
chk('D2 CD-01: talhão com nome repetido na mesma fazenda é recusado no campo e nada é gravado (T2 na Santa Rita)',
    any(e.startswith('t:') for e in (o.get('e') or [])) and o.get('n2') == '8 de 8', o)

# NAV-CLAREZA (nada ambíguo; achado na conferência de 09/10) e achado 4 da revisão (saldo do build ≠ Estoque): a trava diz o estoque físico
# e o disponível, com os mesmos nomes e números das colunas Físico e Disponível da tabela de lotes, que vem do cenário do Estoque; trava pelo
# físico (lote todo reservado continua na unidade dele). Muda a expectativa de 09/10 ("saldo de 480 L disponíveis") pela regra nova
o = run('CD-06', r'''let x=v(); const ids=v().g_itm_rows.filter(r=>!/^G/.test(r.id)).map(r=>r.id); OUT.r=[];
  ids.forEach(id=>{ try{ abre('g_itm',id); const F=painel('g_itm'); const b=(F.c.blocos||[]); const u=b.find(k=>k.t==='Unidade e embalagem'); const l=b.find(k=>k.t==='Locais');
    if(l&&l.temTab) OUT.r.push({t:F.title,trava:(u.lin.find(z=>z&&z.l==='Unidade-base')||{}).v,cols:l.cols,fis:l.rows.map(rr=>rr.c[2].t),livre:l.rows.map(rr=>rr.c[3].t)}); fecha('g_itm'); }catch(e){ OUT.r.push({erro:String(e)}); } });''')
import re
def _n(t):
    m = re.search(r'([\d.]+(?:,\d+)?)', t or ''); return float(m.group(1).replace('.', '').replace(',', '.')) if m else None
def _trava(t):
    m = re.search(r'travada: item com ([\d.]+(?:,\d+)?) \S+ no Estoque \(([\d.]+(?:,\d+)?) \S+ disponíveis\)$', t or ''); return (_n(m.group(1)), _n(m.group(2))) if m else None
def _ruim(r):
    if r.get('erro') or r.get('cols') != ['Lote', 'Local', 'Físico', 'Disponível', 'Validade']: return True
    tv = _trava(r.get('trava')); fis = sum(_n(x) or 0 for x in r['fis']); liv = sum(_n(x) or 0 for x in r['livre'])
    return fis > 0 and (not tv or abs(tv[0] - fis) > 1e-6 or abs(tv[1] - liv) > 1e-6)
ruins = [r for r in (o.get('r') or []) if _ruim(r)]
fa = next((r for r in (o.get('r') or []) if r.get('t') == 'Item · Fungicida A'), {})
chk('NAV-CLAREZA CD-06: a trava diz o físico e o disponível com os números das colunas Físico e Disponível dos lotes, em todo item com lote (Fungicida A: 545 L no Estoque, 480 L disponíveis)',
    bool(o.get('r')) and not ruins and fa.get('trava') == 'L · travada: item com 545 L no Estoque (480 L disponíveis)' and fa.get('fis') == ['545 L'] and fa.get('livre') == ['480 L'], [ruins[:3], fa, len(o.get('r') or [])])

# marcação que vazou do gerador (achado do cadf_det_test reescrito, 09/10): um trecho sem o prefixo f do Python deixou o texto
# "{abas(...)}" na página do CD-01det, e as abas Parcelas por safra · Geometria (com "Definir polígono") sumiram
import re
for pg in ('CD-01', 'CD-01det', 'CD-02', 'CD-03', 'CD-04', 'CD-05', 'CD-06', 'CD-07'):
    h = open(os.path.join(HERE, 'project', pg + '.dc.html'), encoding='utf-8').read()
    vaz = re.findall(r'(?<!\{)\{(?:abas|pane|se|H|prim|secbtn|barra|faixa|arv|grid)\([^}]{0,60}', h)
    chk(f'{pg}: nenhum trecho do gerador vazou como texto na página', not vaz, vaz[:3])
h = open(os.path.join(HERE, 'project', 'CD-01det.dc.html'), encoding='utf-8').read()
chk('CD-01det: as abas "Parcelas por safra" e "Geometria" existem (role=tab)', h.count('role="tab"') >= 2 and 'Geometria' in h, h.count('role="tab"'))

print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
