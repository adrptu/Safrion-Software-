# -*- coding: utf-8 -*-
"""CD-03 Máquinas, instalações e setores · CD-04 Pessoas e equipes (módulo próprio; areas.cadastros.build() usa estes cd03()/cd04()).
CD-03 · a classe vem primeiro e abre só a capacidade dela (potência; barra + tanque; linhas × espaçamento; largura e carga; plataforma;
  vazão; kg/h; sacas). Custo por hora com fonte substitui o valor do ativo. A condição técnica é só leitura e vem da Manutenção
  (Trator T1 em manutenção pela OM-0233, com 'Ver ordens afetadas'). Aba Conjuntos (cartões): máquina + implemento + operações, com largura
  herdada, condição derivada, substituto sugerido, operadores alocáveis (habilidades do CD-04) e rendimento do CD-02.
CD-04 · habilidades em múltipla escolha (a habilitação exigida aparece conforme a habilidade), várias habilitações com validade, vínculo
  e vigência, calendário herdado da equipe, custo-hora com encargos. Habilitação vencida ou pendente grava e marca 'Não alocável em O.S.'.
  Filtro do bloco: Todas · A resolver (estado) e Função (lista: operadores, caldeiros, irrigantes…); 'Solicitar acesso ao app' é simulado.
  Layout de 01/10/2026: abas Pessoas | Equipes (cartões) e Máquinas e instalações | Conjuntos (cartões), cada uma com a sua ação.
  Líder inativo continua visível no formulário da equipe, com aviso, e salvar pede um líder ativo; renomear a pessoa atualiza o líder.
Dados: dados_cad (lido e copiado; Paula passa a caldeira da OS-0424, como em alocacao.py) e dados2.CONJ (rendimentos)."""
import json
from engine import grid, MUTED
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37
import dados2 as D2
import dados_cad as DC
from areas.cadastros import sel, num, txt, dat, cond, R, js, LOC_ATV
from areas.cadastros import (cadx_css, abas, pane, se, faixa, prim, secbtn, qf_chips, filtro_sel, barra, cartoes, bloco_cad, estado_cab, acoes_form,
                             md, mestre, det_cab, vazio, md_css, criar_cab, ncol_dinamico)

H=lambda s: '{{'+s+'}}'
for _f in ('CD-03.dc.html','CD-04.dc.html'): ui37.H_OVR.pop(_f,None)   # layout novo: a altura vem de HEIGHTS37

# ---------------- pessoas, habilidades e habilitações (fonte do CD-04; o CD-03 lê para os operadores do conjunto) ----------------
CALDA='Preparar calda (caldeiro)'; AGRO='Aprovar O.S. (agrônomo)'   # aprovar não libera; liberar é o CMD-06 (DEC-2609-05, L13)
HABILIDADES=['Operar trator','Operar pulverizador','Operar plantadeira','Operar colhedora',CALDA,'Irrigar','Almoxarifado',AGRO,'Conferir','Manutenção de máquinas',
             'Autorizar rota e liberar ordem de processo','Liberar lote (qualidade)']   # BEN-1: Igor e Marta (dados_cad, docs/beneficiamento §2.3)
HAB_EXIGE={'Operar trator':'NR-31','Operar pulverizador':'NR-31','Operar plantadeira':'NR-31','Operar colhedora':'NR-31',CALDA:'NR-31',
           'Irrigar':'NR-10','Manutenção de máquinas':'NR-12',AGRO:'CREA'}
HABIL=[('NR-31','v31','Validade da NR-31'),('NR-10','v10','Validade da NR-10'),('NR-12','v12','Validade da NR-12'),('CREA','vcrea','Validade do registro no CREA')]
_REN={'Preparar calda':CALDA,'Liberar O.S. (agrônomo)':AGRO}   # o rótulo antigo (dados_cad, cenários salvos) vale como sinônimo: a Ana não perde a habilidade nem o CREA exigido
# ajustes sobre dados_cad: Paula é a caldeira das O.S. de pulverização (alocacao.py: 'Paula · caldeiro' na OS-0421/0424/0430);
# Rui é o almoxarife que entrega (os_campo.py, cenario.js); habilidade fora da lista (empilhadeira) sai.
_OVR={'p6':dict(funcao='Caldeiro',equipe='Campo 1',hab=[CALDA,'Conferir'],v31='2027-04-30'),
      'p7':dict(funcao='Almoxarife',hab=['Almoxarifado','Conferir']),
      'p10':dict(equipe='Campo 2')}
_ORDEM=['p1','p2','p3','p6','p10','p4','p5','p7','p8','p9','p12','p13']   # p12 Igor e p13 Marta: equipe e8 Beneficiamento e qualidade (BEN-1)
def pessoas():
    by={p['id']:dict(p,**_OVR.get(p['id'],{})) for p in DC.PESSOAS}
    out=[]
    for pid in _ORDEM:
        p=by[pid]; hab=[_REN.get(h,h) for h in p['hab'] if _REN.get(h,h) in HABILIDADES]
        v=dict(nome=p['nome'],equipe=p['equipe'],hab='; '.join(hab),vinc=p['vinc'],adm=p.get('adm',''),ate=p.get('ate',''),cal='Da equipe',
               custo=p['custo'],acesso='Com login' if p.get('login') else 'Sem login',sit='Ativa')
        for _,k,_l in HABIL: v[k]=p.get(k,'')
        out.append((pid,v))
    return out
EQUIPES=DC.EQUIPES; CALS=DC.CALS
# JS comum às duas telas: quem é alocável em O.S. (habilitação exigida válida e dentro da vigência)
ALOC_JS=('const AL='+json.dumps(dict(exige=HAB_EXIGE,campo={a:k for a,k,_ in HABIL}),ensure_ascii=False)+';\n'+r'''
function habExig(habs){ const s=[]; ml(habs).forEach(h=>{ const x=AL.exige[h]; if(x&&s.indexOf(x)<0) s.push(x); }); return s; }
function alocavel(V){ const m=[], t=[]; if(V.sit==='Inativa') return {ok:false,inat:true,m:'inativa',t:t,vence:false};
  habExig(V.hab).forEach(x=>{ const d=V[AL.campo[x]]; if(!d){ m.push(x+' pendente'); t.push({x:x,s:'pend'}); return; } const dd=ddiff(HOJE,d);
    if(dd<0){ m.push(x+' vencida em '+br(d)); t.push({x:x,s:'venc',d:d}); } else t.push({x:x,s:(dd<=30?'vence':'ok'),d:d}); });
  if(V.adm&&V.adm>HOJE) m.push('admissão em '+br(V.adm)); if(V.ate&&V.ate<HOJE) m.push('contrato encerrado em '+br(V.ate));
  return {ok:!m.length,inat:false,m:m.join(' · '),t:t,vence:t.some(y=>y.s==='vence')}; }
// lista em português: "A", "A e B", "A, B e C"
function lista(a){ return a.length<2?(a[0]||''):a.slice(0,-1).join(', ')+' e '+a[a.length-1]; }
// frase termina com um só ponto (evita "O.S..")
function ponto(s){ return /\.$/.test(s)?s:s+'.'; }
// o select do formulário mostra sempre o valor gravado: vazio vira "Escolha…"; valor fora das opções (inativo, excluído) continua visível
function selFiel(F,suf){ if(!F||!F.open||!F.fields) return; F.fields.forEach(f=>{ if(!f.isSel) return; const val=String(f.v||'');
  if((f.opts||[]).some(o=>o.v===val)) return; f.opts=[{v:val,t:val?val+((suf||{})[f.fid]||''):'Escolha…'}].concat(f.opts||[]); }); }
''')
# ================= CD-03 · Máquinas, instalações e setores =================
CLS=[('Trator','tr'),('Pulverizador','pv'),('Plantadeira','pl'),('Distribuidor','di'),('Colhedora','co'),('Implemento','im'),
     ('Tratamento de sementes','ts'),('Irrigação','ir'),('Beneficiamento','be'),('Armazenagem','ar')]
COD=dict(CLS)
IMPL=['Pulverizador','Plantadeira','Distribuidor','Implemento']            # vão num trator e exigem potência mínima
CALIB_CLS=['Pulverizador','Plantadeira','Distribuidor','Tratamento de sementes','Irrigação','Beneficiamento','Armazenagem']
MEDIDOR=[c for c,_ in CLS if c!='Armazenagem']                             # classes com horímetro
_PREQ=('preq','Potência mínima do trator','cv',dict(min=0,max=700,req=False,help='Montar conjunto com trator abaixo desta potência dá erro.'))
CAP={'Trator':[('pot','Potência','cv',dict(min=20,max=700))],
     'Pulverizador':[('barra','Largura da barra','m',dict(min=6,max=60)),
                     ('tanque','Tanque útil','L',dict(min=200,max=10000,help='A ficha do caldeiro divide a calda em cargas deste volume.')),_PREQ],
     'Plantadeira':[('linhas','Linhas','linhas',dict(min=1,max=60)),('esp','Espaçamento entre linhas','m',dict(min=0.2,max=1.5)),
                    ('larg','Largura de trabalho','m','live'),_PREQ],
     'Distribuidor':[('larg','Largura de trabalho','m',dict(min=1,max=60)),('carga','Carga','kg',dict(min=100,max=20000)),_PREQ],
     'Colhedora':[('plat','Plataforma','m',dict(min=3,max=20))],
     'Implemento':[('larg','Largura de trabalho','m',dict(min=0.5,max=30)),_PREQ],
     'Tratamento de sementes':[('kgh','Capacidade','kg/h',dict(min=100,max=20000))],
     'Irrigação':[('vazao','Vazão','m³/h',dict(min=1,max=2000))],
     'Beneficiamento':[('kgh','Capacidade','kg/h',dict(min=100,max=50000))],
     'Armazenagem':[('capsc','Capacidade','sc de 60 kg',dict(min=100,max=1000000))]}
_DK={'capsc':'cap_sc'}                                                       # chave em dados_cad quando difere
PREQ={'a05':100,'a06':140,'a07':75,'a10':75}                                # potência mínima exigida pelo implemento (cv)
CFONTES=['Apurado na fazenda','Tabela de referência','Premissa a validar']
CFONTE={'a07':'Tabela de referência','a09':'Tabela de referência','a10':'Tabela de referência','a13':'Tabela de referência','a15':'Premissa a validar'}
LOCAIS=LOC_ATV+['Pivô 1']
OPS=list(dict.fromkeys(c['op'] for c in D2.CONJ))
# habilidades exigidas do operador por operação (o conjunto mostra quem pode operá-lo)
OPHAB={'Pulverização':['Operar trator','Operar pulverizador'],'Plantio':['Operar trator','Operar plantadeira'],'Adubação a lanço':['Operar trator'],
       'Tratamento de sementes':[],'Colheita de grãos':['Operar colhedora'],'Colheita de café':[],'Poda':['Operar trator'],'Fertirrigação':['Irrigar']}
SEM_IMPL='Sem implemento'
# subtítulo do formulário: no cadastro a classe vem primeiro; na edição ela fica fixa
SUB_NEW='Escolha a classe para abrir a capacidade dela.'
SUB_EDIT='Altere capacidade, custo por hora e calibração; inative em vez de excluir, o histórico continua.'

def _campos_ativo():
    cap=[]; cont=[]
    for cl,cd in CLS:
        for k,l,u,o in CAP[cl]:
            if o=='live': cap.append(dict(k=f'{k}_{cd}',l=l,ro=True,live=True,u=u,cond=cond('classe',cl),help='Linhas × espaçamento.'))
            else: cap.append(num(f'{k}_{cd}',l,u,cond=cond('classe',cl),**o))
        if cl in MEDIDOR:
            cont.append(num(f'cont_{cd}','Horímetro atual','h',min=0,cond=cond('classe',cl),help='Não pode ser menor que a última leitura; troca de medidor é registrada na Manutenção.'))
    return ([sel('classe','Classe',[c for c,_ in CLS],newOnly=True,help='Abre só a capacidade desta classe; fica fixa depois do cadastro.'),
             txt('nome','Nome',help='Ex.: Trator 05. Não pode repetir.'),txt('modelo','Modelo',req=False),
             dict(k='cond_t',l='Condição técnica',t='area',ro=True,help='Vem da Manutenção; não se altera no cadastro.',**{'def':'Apto'})]
            + cap
            + [num('custo_h','Custo por hora','R$/h',min=0,req=False,help='Combustível, manutenção e depreciação; o operador entra em Pessoas. O rendimento do conjunto em Culturas e operações e o Planejar safra usam este valor.'),
               sel('custo_f','Fonte do custo',CFONTES,req=False,**{'def':'Premissa a validar'})]
            + cont
            + [sel('exige','Exige calibração ou aferição?',['Sim','Não'],help='Vem da classe (pulverizador, plantadeira, distribuidor, tratamento de sementes, irrigação, beneficiamento e armazenagem exigem); mude só com motivo.'),
               dat('calib','Última calibração',cond=cond('exige','Sim'),req=False,help='Em branco: aferir antes de usar.'),
               num('interv','Intervalo entre calibrações','dias',min=7,max=730,cond=cond('exige','Sim')),
               sel('local','Local',LOCAIS,**{'def':'Galpão 1'}),sel('sit','Situação',['Ativo','Inativo'],**{'def':'Ativo'})])

def _linhas_ativo():
    rows=[]
    for a in DC.ATIVOS:
        cl=a['classe']; cd=COD[cl]
        v=dict(classe=cl,nome=a['nome'],modelo=a['modelo'],cond_t='',custo_h=a.get('custo_h',''),custo_f=(CFONTE.get(a['id'],'Apurado na fazenda') if a.get('custo_h')!='' else ''),
               exige=a['exige'],calib=a.get('calib',''),interv=a.get('interv','') or '',local=a['local'],sit='Ativo')
        for k,l,u,o in CAP[cl]:
            if o=='live': continue
            v[f'{k}_{cd}']=PREQ.get(a['id'],'') if k=='preq' else a.get(_DK.get(k,k),'')
        if cl in MEDIDOR: v[f'cont_{cd}']=a['cont']
        rows.append(R(a['id'],v))
    return rows

# CADUX (09/10/2026): mestre com as 10 classes de CLS (a família só como título de seção: Máquinas, Implementos, Irrigação, Instalações),
# "Todos os ativos" e "Conjuntos" → ativos da classe, com as grandezas dela uma por coluna (C18) → painel do ativo em consulta (condição da
# Manutenção, contador, calibração, conjuntos selecionáveis e custo com a fonte). Selecionar e herdar é sempre uma classe, nunca a família.
FAMILIAS=[('Máquinas',['Trator','Colhedora']),('Implementos',['Pulverizador','Plantadeira','Distribuidor','Implemento']),('Irrigação',['Irrigação']),
          ('Instalações',['Tratamento de sementes','Beneficiamento','Armazenagem'])]
def _slug(t): import unicodedata; return ''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn').replace(' ','-')
CLS_SLUG={c:_slug(c) for c,_ in CLS}
# grandezas da classe, uma por coluna (unidade na célula): chave em dados (k_cod), rótulo, unidade
GRANDEZAS={'Trator':[('pot','Potência','cv')],'Pulverizador':[('barra','Barra','m'),('tanque','Tanque','L')],'Plantadeira':[('linhas','Linhas','linhas'),('larg','Largura','m')],
           'Distribuidor':[('larg','Largura','m'),('carga','Carga','kg')],'Colhedora':[('plat','Plataforma','m')],'Implemento':[('larg','Largura','m')],
           'Tratamento de sementes':[('kgh','Capacidade','kg/h')],'Irrigação':[('vazao','Vazão','m³/h')],'Beneficiamento':[('kgh','Capacidade','kg/h')],
           'Armazenagem':[('capsc','Capacidade','sc')]}
# Ativo | Situação | Classe | Modelo | Custo R$/h | Próxima calibração | Conjuntos (em "Todos"); com uma classe, Classe sai e entram as grandezas dela
COLS_ATV=[dict(k='nome',l='Ativo',w=190),dict(k='est',l='Situação',w=190),dict(k='classe',l='Classe',w=150),dict(k='modelo',l='Modelo',w=150),
          dict(k='custo_h',l='R$/h',t='num',a='r',d=2),dict(k='calv',l='Próxima calibração',t='date'),dict(k='ncj',l='Conjuntos',t='num',a='r')]
COLS_CJ=[dict(k='nome',l='Conjunto',w=250),dict(k='est',l='Situação',w=190),dict(k='ops',l='Operações',w=150),dict(k='larg',l='Largura',t='num',a='r',un='m'),
         dict(k='rend',l='Rendimento',t='num',a='r',un='ha/h',d=2),dict(k='oper',l='Operadores alocáveis',w=200)]
def cd03():
    fname='CD-03.dc.html'; E._reset_screen(fname)
    g=grid(COLS_ATV,_linhas_ativo(),gid='g_atv',total=False,frame=False,search=False,
        tools=f'<span class="cmd-conta">{H("c3_conta")}</span>'+qf_chips('g_atv'),
        edit=dict(m='form',title='Ativo',newTitle='Criar ativo',alvo='ativo',sub=SUB_EDIT,fields=_campos_ativo()))
    rend={c['id']:c['rend'] for c in D2.CONJ}
    maqs=[a['nome'] for a in DC.ATIVOS if a['classe'] not in IMPL]; imps=[a['nome'] for a in DC.ATIVOS if a['classe'] in IMPL]
    cj=grid(COLS_CJ,[R(k,dict(maq=m,impl=i or SEM_IMPL,ops=op,rend=rend.get(rid,''),rid=rid)) for k,m,i,op,rid in DC.CONJUNTOS],
        gid='g_cj',dele=False,total=False,search=False,frame=False,tools=f'<span class="cmd-conta">{H("c3_contaCj")}</span>',
        edit=dict(m='form',title='Conjunto',newTitle='Montar conjunto',alvo='conjunto',sub='Escolha a máquina, o implemento e as operações; a largura vem do implemento.',
            fields=[sel('maq','Máquina',maqs),sel('impl','Implemento',[SEM_IMPL]+imps,**{'def':SEM_IMPL}),
                    dict(k='ops',l='Operações',t='multi',opts=OPS,req=True),
                    dict(k='larg_c',l='Largura de trabalho',ro=True,live=True,u='m',help='Herdada do implemento (ou da plataforma da colhedora).'),
                    dict(k='pot_c',l='Potência',ro=True,live=True,help='O trator precisa ter ao menos a potência que o implemento exige.')]))
    acoes_form('g_atv'); acoes_form('g_cj'); cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('c3_v')+se('c3_atv_on',g,True)+se('c3_cj_on',cj)+'</div>'
    corpo=md(mestre('Classes de ativos','Buscar ativo, modelo ou classe'),det,'Máquinas, instalações e setores')
    dados=dict(cod=COD,impl=IMPL,calib=CALIB_CLS,sem=SEM_IMPL,ophab=OPHAB,subnew=SUB_NEW,fam=FAMILIAS,slug=CLS_SLUG,gr=GRANDEZAS,
               cols=[E._col_un(c) for c in COLS_ATV],
               cond={k:dict(t=c['t'],m=c['om']+' · '+c['det'],ordens=c['ordens'],om=c['om']) for k,c in DC.CONDICAO.items()},
               pes=[dict(v,id=pid) for pid,v in pessoas()],rops={c['id']:c['op'] for c in D2.CONJ})
    js({},ALOC_JS+'const C3='+json.dumps(dados,ensure_ascii=False)+';\n'+CD03JS)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a lista rola
    shell37('CD-03','Máquinas, instalações e setores',corpo,fname=fname,status=None,primary_html=criar_cab('c3_criar','+ Criar ativo'),search=False)
    estado_cab(fname,'Máquinas, instalações e setores','c3e')
    ncol_dinamico(fname,['c3_ncol',None])
CD03JS=r'''
// X-CAD-1 (achado 3 da revisão): o custo-hora salvo aqui volta ao abrir a tela, pela mesma leitura do CD-02 (cadCustoH); antes o CD-03 gravava e
// não lia, e mostrava R$ 180,00/h enquanto o rendimento do conjunto já somava R$ 200,00/h
(function(){ const g=GR('g_atv'); if(!g) return; leaves(g.rows).forEach(r=>{ const a=cadAtivoLS(r.id); if(!a) return;
  if(isnum(a.custo_h)) r.v.custo_h=Number(a.custo_h); if(a.custo_f) r.v.custo_f=a.custo_f; }); })();
function c3v(V,k){ return V[k+'_'+(C3.cod[V.classe]||'')]; }
function c3n(V,k){ const x=c3v(V,k); return isnum(x)?Number(x):null; }
function c3larg(V){ const c=V.classe; if(c==='Plantadeira'){ const a=c3n(V,'linhas'), b=c3n(V,'esp'); return (a!==null&&b!==null)?Math.round(a*b*100)/100:null; }
  if(c==='Pulverizador') return c3n(V,'barra'); if(c==='Distribuidor'||c==='Implemento') return c3n(V,'larg'); if(c==='Colhedora') return c3n(V,'plat'); return null; }
function c3cap(V){ const n=k=>c3n(V,k), f=(x,u)=>x===null?'—':nfa(x)+' '+u;
  switch(V.classe){ case 'Trator': return f(n('pot'),'cv');
    case 'Pulverizador': return 'barra '+f(n('barra'),'m')+' · tanque '+f(n('tanque'),'L');
    case 'Plantadeira': return nfa(n('linhas')||0)+' linhas × '+f(n('esp'),'m')+' = '+f(c3larg(V),'m');
    case 'Distribuidor': return f(n('larg'),'m')+' · carga '+f(n('carga'),'kg');
    case 'Colhedora': return 'plataforma '+f(n('plat'),'m'); case 'Implemento': return f(n('larg'),'m');
    case 'Irrigação': return f(n('vazao'),'m³/h'); case 'Armazenagem': return f(n('capsc'),'sc de 60 kg');
    default: return f(n('kgh'),'kg/h'); } }
// grandeza k da classe para a coluna (a largura da plantadeira é linhas × espaçamento)
function c3gr(V,k){ if(k==='larg'&&V.classe==='Plantadeira') return c3larg(V); return c3n(V,k); }
function c3cond(r){ const V=r.v; if(V.sit==='Inativo') return {t:'Inativo',c:'gray',ok:false,curto:'inativo'}; const x=C3.cond[r.id];
  if(x) return {t:x.t,c:'red',ok:false,m:x.m,x:x,curto:x.t.toLowerCase()}; return {t:'Apto',c:'green',ok:true}; }
function c3calib(V){ if(V.exige!=='Sim') return {p:[{k:'mut',t:'não exige'}],s:'não exige',bad:false};
  if(!V.calib) return {p:[chipc('Aferir','yellow'),{k:'mut',t:'sem registro'}],s:'Aferir',bad:true};
  const venc=addd(V.calib,V.interv||0); const d=ddiff(HOJE,venc);
  if(d<0) return {p:[chipc('Vencida em '+br(venc),'red')],s:'Vencida',bad:true,venc:venc};
  if(d<=15) return {p:[chipc('Vence '+br(venc),'yellow')],s:'Vence',bad:false,venc:venc};
  return {p:[chipc('Em dia até '+br(venc),'green')],s:'Em dia',bad:false,venc:venc}; }
const CONT0={}; function c3lei(r){ const c=c3v(r.v,'cont'); if(isnum(c)&&String(c)!=='') CONT0[r.id]=Number(c); }
GR('g_atv').rows.forEach(c3lei);
function c3opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }
function c3oper(ops){ const req=[]; ml(ops).forEach(o=>(C3.ophab[o]||[]).forEach(h=>{ if(req.indexOf(h)<0) req.push(h); }));
  if(!req.length) return {p:[{k:'mut',t:'sem habilidade exigida'}],s:'—'};
  const qs=C3.pes.filter(P=>P.sit!=='Inativa'&&req.every(h=>ml(P.hab).indexOf(h)>=0)); const ok=qs.filter(P=>alocavel(P).ok), no=qs.filter(P=>!alocavel(P).ok);
  if(ok.length) return {p:[{k:'txt',t:ok.map(P=>P.nome).join(', ')}].concat(no.length?[{k:'mut',t:no.map(P=>P.nome).join(', ')+(no.length>1?' não alocáveis':' não alocável')}]:[]),s:ok.map(P=>P.nome).join(', ')};
  return {p:[chipc('Nenhum operador alocável','yellow')].concat(no.length?[{k:'mut',t:no.map(P=>P.nome+' · '+alocavel(P).m).join(' · ')}]:[{k:'mut',t:'cadastre em Pessoas e equipes'}]),s:'Nenhum operador alocável'}; }
function c3conj(self,V){ const atv=RW(self,'g_atv'); const M=atv.find(r=>r.v.nome===V.maq); const I=(V.impl&&V.impl!==C3.sem)?atv.find(r=>r.v.nome===V.impl):null;
  const bad=[M,I].filter(Boolean).map(x=>({x:x,c:c3cond(x)})).filter(y=>!y.c.ok);
  let sub=null; if(M&&M.v.classe==='Trator'&&bad.some(y=>y.x===M)){ const q=I?c3n(I.v,'preq'):null;
    sub=atv.filter(r=>r!==M&&r.v.classe==='Trator'&&c3cond(r).ok&&(q===null||(c3n(r.v,'pot')||0)>=q)).sort((a,b)=>(c3n(b.v,'pot')||0)-(c3n(a.v,'pot')||0))[0]||null; }
  const cal=[M,I].filter(Boolean).filter(x=>c3calib(x.v).bad);
  return {M:M,I:I,bad:bad,sub:sub,cal:cal,ok:!!M&&!bad.length}; }
// situação do ativo: um só cálculo para a linha (só o estado), o filtro "A resolver", o mestre e o cabeçalho
function c3sit(r){ const V=r.v; const C=c3cond(r), K=c3calib(V);
  if(V.sit==='Inativo') return {t:'Inativo',p:[chipc('Inativo','gray')]};
  if(C.t==='Em manutenção') return {t:'Em manutenção',p:sitX('Em manutenção','red'),res:'man'};
  if(K.s==='Vencida') return {t:'Calibração vencida',p:sitX('Calibração vencida','red'),res:'cal'};
  if(K.s==='Aferir') return {t:'Sem aferição',p:sitX('Sem aferição','yellow'),res:'cal'};
  return {t:'Apta',p:sitOk('Apta')}; }
function c3usos(self){ const u={}; RW(self,'g_cj').forEach(r=>{ [r.v.maq,r.v.impl].forEach(n=>{ if(n&&n!==C3.sem) (u[n]=u[n]||[]).push(r); }); }); return u; }
function c3temR(V){ return isnum(V.rend)&&String(V.rend)!==''; }
function c3cjSit(self,r){ const X=c3conj(self,r.v); if(X.bad.length) return {t:'Indisponível',c:'red',res:'bad',X:X}; if(X.cal.length) return {t:'Calibrar antes de usar',c:'yellow',res:'cal',X:X};
  if(!c3temR(r.v)) return {t:'Sem rendimento',c:'yellow',res:'rend',X:X}; return {t:'Disponível',c:'green',X:X}; }
CAD_ACTS.g_atv=()=>[];
CAD_ACTS.g_cj=(self,r)=>[cadExcluir(self,'g_cj',r,'conjunto',r.nd?'tem rendimento em Culturas e operações; troque o conjunto lá antes':'')];
const C3CJ='conjuntos';
function c3clsDe(id){ return Object.keys(C3.slug).find(c=>C3.slug[c]===id)||''; }
function c3cjNome(r){ return (r.v.maq||'')+(r.v.impl&&r.v.impl!==C3.sem?' + '+r.v.impl:''); }
// X-CAD-1: o rendimento do conjunto nasce no CD-02 com o conjunto e a operação (a largura e o R$/h vêm daqui, só leitura lá)
function c3rendH(r){ return 'CD-02.dc.html#aba=operacoes&cj='+encodeURIComponent(r.id)+'&novo=1'; }
// pendências da classe (ou de todos), na ordem: em manutenção (vermelho; resolve a Manutenção) → calibração vencida → aferição; o verbo abre o formulário
function c3pends(self,cls){ const out=[]; RW(self,'g_atv').filter(r=>!cls||r.v.classe===cls).forEach(r=>{ const S=c3sit(r); if(!S.res) return; const V=r.v;
    if(S.res==='man'){ const x=C3.cond[r.id]; out.push({n:0,cor:'red',t:V.nome+' em manutenção pela '+x.om+': '+x.m.split(' · ').slice(1).join(' · ')+'.',quem:'Resolve a Manutenção; as ordens que usam o '+V.nome+' esperam o retorno.',
      lks:x.ordens.map(o=>({t:'Abrir '+o,h:'OS.dc.html#'+o})).concat([{t:'Abrir '+x.om,h:'MA-04det.dc.html#'+x.om}]),s:V.nome+' em manutenção'}); return; }
    out.push({n:S.t==='Calibração vencida'?1:2,cor:S.t==='Calibração vencida'?'red':'yellow',t:V.nome+': '+(S.t==='Calibração vencida'?'calibração vencida em '+br(c3calib(V).venc):'sem aferição registrada')+'.',
      prim:{t:'Registrar calibração do '+V.nome,go:()=>{ g2open(self,GR('g_atv'),r.id,null); setTimeout(()=>g2editar(self,GR('g_atv'),r.id,'calib'),0); }},s:V.nome+(S.t==='Calibração vencida'?' calibração vencida':' sem aferição')}); });
  return out.sort((a,b)=>a.n-b.n); }
function c3prox(ps,ok){ if(!ps.length) return {cor:'green',t:ok||'Em dia: ativos aptos e calibrados.'}; const p=ps[0], r=ps.slice(1);
  return {cor:p.cor,t:p.t,quem:p.quem||'',prim:p.prim||null,lks:p.lks||[],mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
function c3consAtv(self,r){ const V=r.v; const C=c3cond(r), K=c3calib(V); const S=c3sit(r); const us=c3usos(self)[V.nome]||[];
  let prox;
  if(V.sit==='Inativo') prox={cor:'gray',t:'Inativo: fora dos conjuntos e das O.S.; o histórico continua.'};
  else if(C.x) prox={cor:'red',t:'Em manutenção pela '+C.x.om+': '+C.x.m.split(' · ').slice(1).join(' · ')+'.',quem:'Resolve a Manutenção.',lks:C.x.ordens.map(o=>({t:'Abrir '+o,h:'OS.dc.html#'+o})).concat([{t:'Abrir '+C.x.om,h:'MA-04det.dc.html#'+C.x.om}])};
  else if(K.bad) prox={cor:K.s==='Vencida'?'red':'yellow',t:K.s==='Vencida'?('Calibração vencida em '+br(K.venc)+': calibre antes de usar.'):'Sem aferição registrada: afira antes de usar.',prim:{t:'Registrar calibração',go:()=>g2editar(self,GR('g_atv'),r.id,'calib')}};
  else prox={cor:'green',t:'Apto'+(V.exige==='Sim'?' e calibrado até '+br(K.venc):'')+'.'};
  const gs=(C3.gr[V.classe]||[]).map(([k,l,u])=>{ const x=c3gr(V,k); return {l:l,v:x===null?'—':nfa(x)+' '+u}; });
  const ct=c3v(V,'cont'); const pr=c3n(V,'preq');
  return {titulo:'Ativo · '+V.nome,sub:V.classe+(V.modelo?' · '+V.modelo:'')+' · '+(V.local||'—')+' · '+S.t,prox:prox,sec:[{t:'Editar ativo',go:()=>g2editar(self,GR('g_atv'),r.id)}],
    blocos:[{t:'Condição técnica',lin:[{l:'Condição',v:C.m?C.t+' · '+C.m:C.t,cor:C.ok?'':(C.c==='red'?'red':'')}],nota:'Vem da Manutenção; não se altera no cadastro.'},
      {t:'Contador',lin:(V.classe==='Armazenagem')?[]:[{l:'Horímetro',v:isnum(ct)&&String(ct)!==''?nf(ct)+' h':'—'}],nota:V.classe==='Armazenagem'?'Instalação sem horímetro.':'Última leitura gravada; não pode regredir. O histórico de leituras é lacuna L06.'},
      {t:'Calibração',lin:[{l:'Exige calibração ou aferição',v:V.exige||'—'}].concat(V.exige==='Sim'?[{l:'Última',v:V.calib?br(V.calib):'sem registro',cor:V.calib?'':'yellow'},{l:'Intervalo',v:V.interv?V.interv+' dias':'—'},{l:'Próxima',v:K.venc?br(K.venc):'—',cor:K.s==='Vencida'?'red':(K.s==='Vence'?'yellow':'')}]:[])},
      {t:'Capacidade',lin:gs.concat(pr!==null?[{l:'Potência mínima do trator',v:nfa(pr)+' cv'}]:[])},
      {t:'Conjuntos',fil:us.map(c=>{ const Sc=c3cjSit(self,c); return {t:c3cjNome(c),sub:ml(c.v.ops).join(', '),chip:{t:Sc.t,c:Sc.c},al:'Abrir conjunto '+c3cjNome(c),
          go:()=>{ g2set(self,'g_atv',{fm:null}); g2open(self,GR('g_cj'),c.id,null,{pai:{gid:'g_atv',rid:r.id,t:V.nome}}); }}; }),nota:us.length?'':'Nenhum conjunto usa este ativo.'},
      {t:'Custo',lin:[{l:'Custo R$/h',v:isnum(V.custo_h)&&String(V.custo_h)!==''?'R$ '+nf(V.custo_h,2)+'/h':'—'},{l:'Fonte',v:V.custo_f||'—'}],nota:'Combustível, manutenção e depreciação; o operador entra em Pessoas e equipes.'}]}; }
function c3consCj(self,r){ const V=r.v; const Sc=c3cjSit(self,r); const X=Sc.X; const O=c3oper(V.ops); const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null);
  const pot=X.M&&X.M.v.classe==='Trator'?c3n(X.M.v,'pot'):null, q=X.I?c3n(X.I.v,'preq'):null;
  let prox;
  if(X.bad.length) prox={cor:'red',t:'Indisponível: '+X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(' · ')+'.',quem:X.sub?('Substituto sugerido: '+X.sub.v.nome+' ('+nfa(c3n(X.sub.v,'pot'))+' cv).'):'',prim:X.sub?{t:'Trocar pelo '+X.sub.v.nome,go:()=>{ g2editar(self,GR('g_cj'),r.id,'maq'); setTimeout(()=>draftSet(self,'g_cj',{maq:X.sub.v.nome}),20); }}:null};
  else if(X.cal.length) prox={cor:'yellow',t:'Calibrar antes de usar: '+X.cal.map(x=>x.v.nome+' · '+c3calib(x.v).s.toLowerCase()).join(' · ')+'.',lks:X.cal.map(x=>({t:'Abrir '+x.v.nome,go:()=>{ g2set(self,'g_cj',{fm:null}); g2open(self,GR('g_atv'),x.id,null,{pai:{gid:'g_cj',rid:r.id,t:c3cjNome(r)}}); }}))};
  else if(!c3temR(V)) prox={cor:'yellow',t:'Sem rendimento: o planejamento não calcula horas nem custo deste conjunto.',lks:[{t:'Criar rendimento do conjunto',h:c3rendH(r)}]};
  else prox={cor:'green',t:'Disponível: rende '+nf(V.rend,2)+' ha/h.'};
  const comp=[X.M,X.I].filter(Boolean).map(x=>{ const S=c3sit(x); return {t:x.v.nome,sub:x.v.classe+(x.v.modelo?' · '+x.v.modelo:''),chip:{t:S.t,c:S.res?(S.res==='man'||S.t==='Calibração vencida'?'red':'yellow'):'green'},al:'Abrir ativo '+x.v.nome,
    go:()=>{ g2set(self,'g_cj',{fm:null}); g2open(self,GR('g_atv'),x.id,null,{pai:{gid:'g_cj',rid:r.id,t:c3cjNome(r)}}); }}; });
  return {titulo:'Conjunto · '+c3cjNome(r),sub:ml(V.ops).join(' · ')+' · '+Sc.t,prox:prox,sec:[{t:'Editar conjunto',go:()=>g2editar(self,GR('g_cj'),r.id)}],
    blocos:[{t:'Máquina e implemento',fil:comp},
      {t:'Trabalho',lin:[{l:'Operações',v:ml(V.ops).join(', ')},{l:'Largura de trabalho',v:lg===null?'—':nfa(lg)+' m'},{l:'Potência',v:pot===null?'—':(nfa(pot)+' cv'+(q!==null?(pot>=q?' · atende os ':' · abaixo dos ')+nfa(q)+' cv exigidos':''))},
        {l:'Operadores alocáveis',v:O.s}]},
      {t:'Rendimento',lin:[{l:'Rendimento',v:c3temR(V)?nf(V.rend,2)+' ha/h':'sem rendimento',cor:c3temR(V)?'':'yellow'}],
        lks:[c3temR(V)?{t:'Abrir rendimento em Culturas e operações',h:'CD-02.dc.html#aba=operacoes&rend='+encodeURIComponent(V.rid||'')}:{t:'Criar rendimento do conjunto',h:c3rendH(r)}]}]}; }
function c3cfg(self){ cmdIni(self,{gp:'classe',ip:{g_atv:'atv',g_cj:'cj'},
  grupoDe:(s,gid,r)=>{ if(gid==='g_cj') return C3CJ; const sel=cmdSel(s); return (sel===''&&s.state.mx_sel!==undefined)?'':(C3.slug[r.v.classe]||''); },
  existeGrupo:(s,id)=>id===C3CJ||!!c3clsDe(id),
  reg:(s,id)=>RW(s,'g_atv').some(r=>r.id===id)?{gid:'g_atv',rid:id}:(RW(s,'g_cj').some(r=>r.id===id)?{gid:'g_cj',rid:id}:null),
  indisp:(id,gid)=>cmdIndisp(gid==='g_cj'?'Conjunto':'Ativo',id),
  indispGrupo:(id)=>'Classe “'+id+'” não existe nos Cadastros.',
  inativo:(gid,r)=>(gid==='g_atv'&&r.v.sit==='Inativo')?{c3qf:'inat'}:null,
  novo:(s)=>{ if(s.__v&&s.__v.c3_criar) s.__v.c3_criar(); },
  anuncio:(s,id)=>{ if(id===C3CJ) return 'Conjuntos: '+RW(s,'g_cj').length+' conjuntos'; const c=c3clsDe(id); const n=RW(s,'g_atv').filter(r=>(!c||r.v.classe===c)&&r.v.sit!=='Inativo').length; const p=c3pends(s,c).length;
    return (c||'Todos os ativos')+': '+n+(n===1?' ativo':' ativos')+' · '+(p?p+' a resolver':'Em dia'); },
  cons:{g_atv:c3consAtv,g_cj:c3consCj}}); }
function PREVALS(self,v){ cadActsIni(self); c3cfg(self); if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const atv=RW(self,'g_atv'); self._c3nomes=self._c3nomes||{}; const usos=c3usos(self); const sel=cmdSel(self); const cls=c3clsDe(sel); const q=self.state.mx_q||'';
  atv.forEach(r=>{ const V=r.v; self._c3nomes[r.id]=V.nome; const C=c3cond(r);
    r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.p.modelo=[V.modelo?{k:'txt',t:V.modelo}:{k:'mut',t:'—'}]; r.s.modelo=V.modelo||'';
    r.p.classe=[{k:'txt',t:V.classe||'—'}]; r.s.classe=V.classe||'';
    (C3.gr[V.classe]||[]).forEach(([k,l,u],i)=>{ const x=c3gr(V,k); V['g'+i]=x===null?'':x; r.p['g'+i]=[x===null?{k:'mut',t:'—'}:{k:'txt',t:nfa(x)+' '+u}]; r.s['g'+i]=x===null?'':nfa(x)+' '+u; });
    const K=c3calib(V); V.calv=K.venc||''; r.p.calv=[K.venc?(K.s==='Em dia'?{k:'txt',t:br(K.venc)}:{k:'cn',t:br(K.venc),c:K.s==='Vencida'?'red':'yellow'}):{k:'mut',t:'—'}]; r.s.calv=K.venc?br(K.venc):'';
    V.cond_t=C.m?C.t+' · '+C.m:C.t; r.o=null;
    const ch=isnum(V.custo_h)&&String(V.custo_h)!==''; r.p.custo_h=ch?[{k:'txt',t:nf(V.custo_h,2)}]:[{k:'mut',t:'—'}]; r.s.custo_h=ch?nf(V.custo_h,2):'';
    const n=(usos[V.nome]||[]).length; V.ncj=n; r.p.ncj=[{k:(n?'txt':'mut'),t:n?String(n):'—'}]; r.s.ncj=n?String(n):'';
    const S=c3sit(r); r.p.est=S.p; r.s.est=S.t; });
  cmdPasse(atv,'cadm_g_atv',r=>!cls||r.v.classe===cls);
  cmdPasse(atv,'cadb_g_atv',r=>cmdCasa([r.v.nome,r.v.modelo,r.v.classe,r.v.local].join(' '),q));
  cmdQf(self,v,'g_atv','c3qf',[{k:'res',t:'A resolver',f:r=>!!c3sit(r).res},{k:'inat',t:'Inativos',f:r=>r.v.sit==='Inativo',oculta:true}],atv);
  // com uma classe, Classe sai e entram as grandezas dela, uma por coluna (C18); com duas grandezas, Modelo vai para o painel (≤ 7 colunas)
  const gr=cls?(C3.gr[cls]||[]):[]; const gc=gr.map(([k,l,u],i)=>({k:'g'+i,l:l,t:'num',a:'r',un:u}));
  GR('g_atv').cols=cls?[C3.cols[0],C3.cols[1]].concat(gr.length<2?[C3.cols[3]]:[]).concat(gc).concat([C3.cols[4],C3.cols[5],C3.cols[6]]):C3.cols; v.c3_ncol=GR('g_atv').cols.length;
  c3opts('g_cj','maq',atv.filter(r=>C3.impl.indexOf(r.v.classe)<0).map(r=>r.v.nome));
  c3opts('g_cj','impl',[C3.sem].concat(atv.filter(r=>C3.impl.indexOf(r.v.classe)>=0).map(r=>r.v.nome)));
  const cjs=RW(self,'g_cj');
  cjs.forEach(r=>{ const V=r.v; const X=c3conj(self,V); const nm=c3cjNome(r); r.p.nome=[{k:'b',t:nm}]; r.s.nome=nm; const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null); V.larg=lg===null?'':lg;
    r.p.larg=[lg===null?{k:'mut',t:'—'}:{k:'txt',t:nfa(lg)}]; r.s.larg=lg===null?'':nfa(lg); r.nd=c3temR(V)?'tem rendimento':'';
    r.p.ops=[{k:'txt',t:ml(V.ops).join(', ')}]; r.s.ops=ml(V.ops).join(', '); const Sc=c3cjSit(self,r); r.p.est=[chipc(Sc.t,Sc.c)]; r.s.est=Sc.t;
    const O=c3oper(V.ops); r.p.oper=O.p; r.s.oper=O.s; r.p.rend=c3temR(V)?[{k:'txt',t:nf(V.rend,2)}]:[{k:'mut',t:'—'}]; r.s.rend=c3temR(V)?nf(V.rend,2):''; });
  cmdPasse(cjs,'cadb_g_cj',r=>cmdCasa([r.s.nome,r.v.ops].join(' '),q)); }
function EXTRAVALS(self,v){ const atv=RW(self,'g_atv'); const cjs=RW(self,'g_cj'); const sel=cmdSel(self); const cls=c3clsDe(sel); const q=self.state.mx_q||''; const larga=cadLarga();
  // ---- mestre: Todos os ativos · as 10 classes sob o título da família · Conjuntos ----
  const its=[]; const casa=(c)=>!q||C3.slug[c]===sel||cmdCasa(c,q)||atv.some(r=>r.v.classe===c&&cmdCasa([r.v.nome,r.v.modelo].join(' '),q));
  C3.fam.forEach(([fam,cl])=>{ const vis=cl.filter(casa); if(!vis.length) return; its.push({tit:true,t:fam});
    vis.forEach(c=>{ const n=atv.filter(r=>r.v.classe===c&&r.v.sit!=='Inativo').length; const p=c3pends(self,c);
      its.push({id:C3.slug[c],t:c,n:String(n),sub:C3.calib.indexOf(c)>=0?'exige calibração':'',res:p.length?p.length+' a resolver':'Em dia',cor:p.length?(p.some(x=>x.cor==='red')?'red':'yellow'):'green'}); }); });
  const cjBad=cjs.filter(r=>c3cjSit(self,r).res).length; its.push({tit:true,t:'Máquina e implemento'});
  its.push({id:C3CJ,t:'Conjuntos',n:String(cjs.length),sub:'máquina + implemento',res:cjBad?cjBad+' a resolver':'Em dia',cor:cjBad?(cjs.some(r=>c3cjSit(self,r).res==='bad')?'red':'yellow'):'green'});
  cadMestreVals(self,v,{todos:{t:'Todos os ativos',sub:atv.filter(r=>r.v.sit!=='Inativo').length+' ativos'},itens:its,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga){ atv.filter(r=>r.v.sit!=='Inativo'&&cmdCasa([r.v.nome,r.v.modelo,r.v.classe].join(' '),q)).forEach(r=>rs.push({t:r.v.nome+' · '+r.v.classe,sub:'Ativo · '+(r.v.modelo||'—'),go:()=>cmdAbre(self,'g_atv',r.id,C3.slug[r.v.classe])})); }
  cadResVals(v,rs);
  // ---- detalhe ----
  const av=cmdAviso(self,'Ver todos os ativos'); v.c3_atv_on=sel!==C3CJ; v.c3_cj_on=sel===C3CJ;
  if(sel===C3CJ){ const ps=cjs.filter(r=>c3cjSit(self,r).res).map(r=>{ const Sc=c3cjSit(self,r); return {cor:Sc.c,t:c3cjNome(r)+': '+Sc.t.toLowerCase()+'.',s:c3cjNome(r)+' '+Sc.t.toLowerCase(),
      lks:[{t:'Abrir o conjunto',go:()=>g2open(self,GR('g_cj'),r.id,null)}]}; }).sort((a,b)=>(a.cor==='red'?0:1)-(b.cor==='red'?0:1));
    cadDetVals(self,v,Object.assign({t:'Conjuntos',sub:cjs.length+' conjuntos de máquina e implemento · a largura vem do implemento; o rendimento, de Culturas e operações',
      chip:ps.length?{t:ps.length+' a resolver',c:ps.some(x=>x.cor==='red')?'red':'yellow'}:{t:'Em dia',c:'green'},prox:c3prox(ps,'Em dia: conjuntos disponíveis e com rendimento.'),volta:'Classes',voltar:()=>cmdVolta(self)},av)); }
  else { const ps=c3pends(self,cls); const n=atv.filter(r=>(!cls||r.v.classe===cls)&&r.v.sit!=='Inativo').length;
    cadDetVals(self,v,Object.assign({t:cls||'Todos os ativos',sub:n+(n===1?' ativo':' ativos')+(cls?(C3.calib.indexOf(cls)>=0?' · exige calibração ou aferição':' · sem calibração exigida')+' · '+(C3.gr[cls]||[]).map(x=>x[1].toLowerCase()).join(' e ')+' em colunas próprias':' · '+C3.fam.length+' famílias e 10 classes'),
      chip:ps.length?{t:ps.length+' a resolver',c:ps.some(x=>x.cor==='red')?'red':'yellow'}:{t:'Em dia',c:'green'},prox:c3prox(ps),volta:'Classes',voltar:()=>cmdVolta(self)},av)); }
  // "+ Criar ativo": herda a classe (uma das 10; fica fixa) e já marca "Exige calibração" pela classe; em Conjuntos, "+ Criar conjunto"
  v.cab_criar_on=true; v.cab_criarT=sel===C3CJ?'+ Criar conjunto':'+ Criar ativo';
  v.c3_criar=()=>{ if(sel===C3CJ){ g2new(self,GR('g_cj')); return; } g2set(self,'g_atv',{fm:null}); g2new(self,GR('g_atv'),{draft:c3novoDraft(cls)});
    setTimeout(()=>{ try{ const x=document.getElementById(cls?'fx_g_atv_nome':'fx_g_atv_classe'); if(x) x.focus(); }catch(z){} },90); };
  // ---- grade, estado do cabeçalho e vazio ----
  const manL=atv.filter(r=>c3sit(r).res==='man'), calL=atv.filter(r=>c3sit(r).res==='cal'); const man=manL.length, cal=calL.length;
  cadEstado(v,'c3e',[man?man+(man>1?' máquinas em manutenção':' máquina em manutenção'):'',cal?cal+(cal>1?' calibrações a resolver':' calibração a resolver'):''].filter(Boolean).join(' · ')||'Máquinas aptas e calibradas',man?'red':(cal?'yellow':'green'));
  cadQfPos(self,v,'g_atv','c3qf'); const ct=cmdConta(self,'g_atv',atv); v.c3_conta=ct.n+' de '+ct.tot; const cc=cmdConta(self,'g_cj',cjs); v.c3_contaCj=cc.n+' de '+cc.tot;
  const vz=sel===C3CJ?(!cc.n?{t:q?'Nenhum conjunto encontrado para “'+q+'”.':'Nenhum conjunto. Monte o 1º em + Criar conjunto, no topo.'}:null)
    :(!ct.n?(q?{t:'Nenhum ativo encontrado para “'+q+'”. Para cadastrar, use + Criar ativo, no topo.'}:(ct.tot?{t:'Nenhum ativo com este filtro.',go:{t:'Mostrar todos',fn:()=>self.setState({c3qf:''})}}:{t:'Nenhum '+(cls||'ativo').toLowerCase()+' cadastrado. Crie o 1º em + Criar ativo, no topo.'})):null);
  cadVazioSe(self,v,'c3_v',vz,['g_atv','g_cj']);
  // ---- formulários ----
  const F=v.g_atv_F; if(F&&F.open&&F.fields){ const f=F.fields.find(x=>x.fid==='fx_g_atv_classe');
    if(f&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_atv').fm; if(!cur) return; const val=e.target.value; const d=Object.assign({},cur.draft,{classe:val});
      if(cur.isNew) d.exige=c3exige(val); const er=Object.assign({},cur.errs||{}); delete er.classe;
      g2set(self,'g_atv',{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); };
    F.fields.forEach(x=>{ if(x.isSel&&!x.dis&&x.v===''&&!x.opts.some(o=>o.v==='')) x.opts=[{v:'',t:'Escolha…'}].concat(x.opts); });
    const fc=F.fields.find(x=>x.fid==='fx_g_atv_custo_h'); if(fc){ fc.help='Combustível, manutenção e depreciação; o operador entra em Pessoas. O rendimento do conjunto em Culturas e operações e a configuração “Padrão do cadastro” das safras abertas no Planejar safra leem este valor (só leitura lá); a safra encerrada guarda o da época.'; } }
  if(F&&F.open&&F.edit&&(g2st(self,'g_atv').fm||{}).isNew) F.sub=C3.subnew;
  selFiel(v.g_atv_F); selFiel(v.g_cj_F);
  self.g2live=(gid,k,d)=>{ const n=x=>{ const y=g2num(d[x]); return isNaN(y)?null:y; };
    if(gid==='g_atv'&&k==='larg_pl'){ const a=n('linhas_pl'), b=n('esp_pl'); return (a!==null&&b!==null)?nfa(Math.round(a*b*100)/100):'—'; }
    if(gid==='g_cj'){ const atv=RW(self,'g_atv'); const M=atv.find(r=>r.v.nome===d.maq); const I=(d.impl&&d.impl!==C3.sem)?atv.find(r=>r.v.nome===d.impl):null;
      if(k==='larg_c'){ const l=I?c3larg(I.v):(M?c3larg(M.v):null); return l===null?'—':nfa(l); }
      if(k==='pot_c'){ const p=M&&M.v.classe==='Trator'?c3n(M.v,'pot'):null, q=I?c3n(I.v,'preq'):null;
        if(p===null) return q===null?'—':'implemento exige '+nfa(q)+' cv'; return nfa(p)+' cv'+(q!==null?(p>=q?' · atende os ':' · abaixo dos ')+nfa(q)+' cv exigidos':''); } }
    return null; };
  valida(self,v,'g_atv',(d,fm)=>{ const e={}; const cd=C3.cod[d.classe]; const c=g2num(d['cont_'+cd]);
    if(fm.rid&&CONT0[fm.rid]!==undefined&&!isNaN(c)&&c<CONT0[fm.rid]) e['cont_'+cd]='A última leitura foi '+nf(CONT0[fm.rid])+' h. Se o medidor foi trocado, registre a troca na Manutenção.';
    if(d.exige==='Sim'&&d.calib&&d.calib>HOJE) e.calib='A calibração não pode ser em data futura.';
    if(d.classe!=='Armazenagem'&&!String(d.custo_h||'').trim()) e.custo_h='Informe o custo por hora; o rendimento do conjunto e o Planejar safra usam este valor.';
    else if(String(d.custo_h||'').trim()&&!d.custo_f) e.custo_f='Informe de onde vem o custo.';
    const dup=unico(self,'g_atv',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe '+dup.v.nome+'.'; return e; });
  valida(self,v,'g_cj',(d,fm)=>{ const e={}; const atv=RW(self,'g_atv'); const M=atv.find(r=>r.v.nome===d.maq); const I=(d.impl&&d.impl!==C3.sem)?atv.find(r=>r.v.nome===d.impl):null;
    if(M&&I&&M.v.classe!=='Trator') e.impl='Implemento vai num trator; '+M.v.nome+' é '+String(M.v.classe).toLowerCase()+'.';
    else if(M&&I){ const p=c3n(M.v,'pot'), q=c3n(I.v,'preq'); if(p!==null&&q!==null&&p<q) e.maq=M.v.nome+' tem '+nfa(p)+' cv; '+I.v.nome+' exige '+nfa(q)+' cv. Escolha um trator mais potente.'; }
    if(!e.maq&&!e.impl){ const dup=RW(self,'g_cj').find(r=>r.id!==fm.rid&&r.v.maq===d.maq&&(r.v.impl||C3.sem)===(d.impl||C3.sem)); if(dup) e.maq='Este conjunto já existe ('+ml(dup.v.ops).join(', ')+'); edite a linha dele.'; }
    return e; });
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_atv'){ const old=(self._c3nomes||{})[r.id]; c3lei(r);
      // X-CAD-1: o R$/h salvo aqui vale no rendimento do conjunto em Culturas e operações (só leitura lá; o R$/ha acompanha)
      cadLSPoe(o=>{ o.ativos=o.ativos||{}; o.ativos[r.id]={nome:r.v.nome,custo_h:r.v.custo_h,custo_f:r.v.custo_f||''}; });
      if(old&&old!==r.v.nome){ const cs=g2clone(RW(self,'g_cj')); cs.forEach(c=>{ if(c.v.maq===old) c.v.maq=r.v.nome; if(c.v.impl===old) c.v.impl=r.v.nome; }); g2set(self,'g_cj',{rows:cs}); }
      const C=c3cond(r); self.setState({g2toast:(isNew?'Criado: ':'Salvo: ')+r.v.nome+' · '+c3cap(r.v)+(isnum(r.v.custo_h)&&String(r.v.custo_h)!==''?' · R$ '+nf(r.v.custo_h,2)+'/h':'')+' · '+C.t+'.'}); }
    if(gid==='g_cj'){ const X=c3conj(self,r.v); const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null);
      self.setState({g2toast:(isNew?'Conjunto montado: ':'Salvo: ')+r.v.maq+(X.I?' + '+r.v.impl:'')+' · '+ml(r.v.ops).join(', ')+(lg!==null?' · '+nfa(lg)+' m':'')
        +(X.bad.length?' · indisponível: '+X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(', '):' · disponível')+(isNew?'. Próximo passo: criar o rendimento do conjunto.':'.')}); } }; }
// criação mínima sem padrão escondido (regra 6, X01): a classe herdada é uma das 10 e "Exige calibração" nasce pela classe (CALIB_CLS), visível;
// em "Todos" a classe vem vazia ("Escolha…") e a calibração também, até a classe ser escolhida
function c3exige(cls){ return cls?(C3.calib.indexOf(cls)>=0?'Sim':'Não'):''; }
function c3novoDraft(cls){ return {classe:cls||'',exige:c3exige(cls)}; }
'''

# ================= CD-04 · Pessoas e equipes =================
# CADUX (09/10/2026): mestre Todas as pessoas · equipes · Sem equipe → detalhe da equipe (líder, calendário, Próximo passo e as pessoas dela)
# → painel da pessoa em consulta (habilitações com validade, vínculo, calendário, acesso ao app e o custo-hora restrito, recolhido)
QF=[('ope','Operadores'),('cal','Caldeiros'),('irr','Irrigantes'),('alm','Almoxarifes'),('agr','Agrônomos'),('nao','Não alocáveis')]
SEM_EQ='__sem'
# Pessoa | Situação | Habilidades | Vínculo | Habilitação | Próxima validade | Acesso ao app (em "Todas as pessoas", Equipe no lugar do Acesso ao app);
# o custo-hora sai da lista (G1, C15) e o calendário e o "disponível até" vão para o painel
COLS_PES=[dict(k='nome',l='Pessoa',w=140),dict(k='est',l='Situação',w=190),dict(k='habs',l='Habilidades',multi=True,w=240),dict(k='vinc',l='Vínculo',w=100),
          dict(k='habx',l='Habilitação',multi=True),dict(k='habv',l='Próxima validade',t='date'),dict(k='acesso',l='Acesso ao app',w=140)]
COL_EQ=dict(k='equipe',l='Equipe',w=120)
def cd04():
    fname='CD-04.dc.html'; E._reset_screen(fname)
    eqn=[e[1] for e in EQUIPES]; pes=pessoas()
    # a equipe vem do grupo escolhido no mestre (visível e trocável); em "Todas", "Escolha…" (nunca a 1ª da lista)
    campos=([txt('nome','Nome'),sel('equipe','Equipe',eqn),
             dict(k='hab',l='Habilidades',t='multi',opts=HABILIDADES,req=True)]
            + [dat(k,l,req=False) for _,k,l in HABIL]
            + [sel('vinc','Vínculo',['CLT','Safrista','Diarista','Terceiro'],**{'def':'CLT'}),dat('adm','Admissão'),
               dat('ate','Disponível até',req=False,help='Fim do contrato de safrista ou diarista.'),
               sel('cal','Calendário de trabalho',['Da equipe']+CALS,**{'def':'Da equipe'},help='Mude só se a pessoa foge do calendário da equipe.'),
               num('custo','Custo-hora com encargos','R$/h',min=0,help='Salário e encargos por hora trabalhada; visível só para quem tem permissão de custos.'),
               sel('acesso','Acesso ao app',['Com login','Sem login','Acesso solicitado','Solicitar acesso ao app'],**{'def':'Sem login'}),
               sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})])
    gp=grid(COLS_PES,[R(pid,v) for pid,v in pes],gid='g_pes',total=False,frame=False,search=False,
        tools=f'<span class="cmd-conta">{H("c4_conta")}</span>'+qf_chips('g_pes')+filtro_sel('c4fun','Função'),
        edit=dict(m='form',title='Pessoa',newTitle='Criar pessoa',alvo='pessoa',
            sub='Marque o que a pessoa faz; a habilitação exigida aparece abaixo. Criar a pessoa não cria login. Inative em vez de excluir.',fields=campos))
    grid([dict(k='nome',l='Equipe'),dict(k='lider',l='Líder'),dict(k='membros',l='Pessoas ativas',t='num',a='r'),dict(k='cal',l='Calendário',w=220)],
        [R(i,dict(nome=n,lider=l,cal=c)) for i,n,l,c in EQUIPES],gid='g_eq',dele=False,total=False,search=False,
        edit=dict(m='form',title='Equipe',newTitle='Criar equipe',sub='Altere nome, líder e calendário; quem segue a equipe herda o calendário.',
            fields=[txt('nome','Nome da equipe'),sel('lider','Líder',[v['nome'] for _,v in pes]),sel('cal','Calendário',CALS,**{'def':'seg–sáb · 06–15h'})]))
    acoes_form('g_eq'); cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('c4_v')+gp+'</div>'
    corpo=md(mestre('Equipes','Buscar pessoa, equipe ou habilidade',secbtn('c4_neq','+ Criar equipe')),det,'Pessoas e equipes')
    dados=dict(qf=QF,habil=[[a,k] for a,k,_ in HABIL],calda=CALDA,agro=AGRO,sem=SEM_EQ,cols=[E._col_un(c) for c in COLS_PES],coleq=COL_EQ)
    js({},ALOC_JS+'const C4='+json.dumps(dados,ensure_ascii=False)+';\n'+CD04JS)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a lista rola
    shell37('CD-04','Pessoas e equipes',corpo,fname=fname,status=None,primary_html=criar_cab('c4_criar','+ Criar pessoa'),search=False)
    estado_cab(fname,'Pessoas e equipes','c4e')
    ncol_dinamico(fname,['c4_ncol'])
CD04JS=r'''
function c4hdia(c){ const m=/(\d{2})–(\d{2})h/.exec(c||''); if(m) return (Number(m[2])-Number(m[1]))+' h/dia'; const n=/(\d+)h$/.exec(c||''); return n?n[1]+' h/dia':''; }
function c4qf(k,V,A){ const h=ml(V.hab);
  if(k==='ope') return h.some(x=>x.indexOf('Operar')===0); if(k==='cal') return h.indexOf(C4.calda)>=0; if(k==='irr') return h.indexOf('Irrigar')>=0;
  if(k==='alm') return h.indexOf('Almoxarifado')>=0; if(k==='agr') return h.indexOf(C4.agro)>=0; if(k==='nao') return !A.ok&&!A.inat;
  if(k==='res') return (!A.ok&&!A.inat)||A.vence; return true; }
function c4eqcal(self){ const o={}; RW(self,'g_eq').forEach(e=>{ o[e.v.nome]=e.v.cal; }); return o; }
// situação da pessoa: um só cálculo para a linha (só o estado: o verbo fica uma vez, no painel), o filtro "A resolver", o mestre e o cabeçalho
function c4sit(V){ const A=alocavel(V);
  if(A.inat) return {t:'Inativa',p:[chipc('Inativa','gray')]};
  if(!A.ok) return {t:'Não alocável',p:[chipc('Não alocável em O.S.','red')],res:'nao'};
  if(A.vence) return {t:'Vence em 30 dias',p:sitX('Vence em 30 dias','yellow'),res:'ven'};
  return {t:'Alocável',p:sitOk('Alocável')}; }
function c4val(A){ const ds=A.t.filter(y=>y.d).map(y=>y.d).sort(); return ds.length?ds[0]:''; }
// o que fazer com a pessoa, na ordem: não alocável (habilitação pendente ou vencida) → vence em 30 dias; o verbo nomeia a habilitação
function c4pend(r){ const V=r.v; const A=alocavel(V); if(A.inat) return null; const cp=k=>(C4.habil.find(x=>x[0]===k)||[])[1];
  const ruim=A.t.find(y=>y.s==='venc'||y.s==='pend'); if(ruim) return {cor:'red',t:V.nome+' não alocável em O.S.: '+ruim.x+(ruim.s==='venc'?' vencida em '+br(ruim.d):' pendente')+'.',
    prim:{t:(ruim.s==='venc'?'Renovar ':'Informar ')+ruim.x+' de '+V.nome,campo:cp(ruim.x)},s:V.nome+' não alocável ('+ruim.x+')'};
  if(!A.ok) return {cor:'red',t:V.nome+' não alocável em O.S.: '+A.m+'.',prim:{t:'Editar '+V.nome,campo:''},s:V.nome+' não alocável'};
  const vz=A.t.find(y=>y.s==='vence'); if(vz) return {cor:'yellow',t:'A '+vz.x+' de '+V.nome+' vence em '+br(vz.d)+'.',prim:{t:'Renovar '+vz.x+' de '+V.nome,campo:cp(vz.x)},s:vz.x+' de '+V.nome+' vence em '+br(vz.d)};
  return null; }
function c4eqDe(self,r){ const e=RW(self,'g_eq').find(x=>x.v.nome===r.v.equipe); return e?e.id:C4.sem; }
function c4membros(self,gid){ const ps=RW(self,'g_pes'); if(!gid) return ps; if(gid===C4.sem) return ps.filter(p=>c4eqDe(self,p)===C4.sem); const e=RW(self,'g_eq').find(x=>x.id===gid); return e?ps.filter(p=>p.v.equipe===e.v.nome):[]; }
function c4lidInat(self,e){ const L=RW(self,'g_pes').find(p=>p.v.nome===e.v.lider); return !!e.v.lider&&(!L||L.v.sit==='Inativa'); }
function c4pends(self,gid){ const out=[]; const e=gid&&gid!==C4.sem?RW(self,'g_eq').find(x=>x.id===gid):null;
  if(e&&c4lidInat(self,e)) out.push({cor:'yellow',t:'A líder '+e.v.lider+' está inativa: a equipe precisa de um líder ativo.',prim:{t:'Escolher líder ativo',go:()=>g2editar(self,GR('g_eq'),e.id,'lider')},s:'líder inativa'});
  c4membros(self,gid).forEach(r=>{ const p=c4pend(r); if(p) out.push(Object.assign({},p,{prim:{t:p.prim.t,go:()=>{ g2open(self,GR('g_pes'),r.id,null); setTimeout(()=>g2editar(self,GR('g_pes'),r.id,p.prim.campo),0); }}})); });
  return out.sort((a,b)=>(a.cor==='red'?0:1)-(b.cor==='red'?0:1)); }
function c4prox(ps){ if(!ps.length) return {cor:'green',t:'Em dia: todos alocáveis e habilitações válidas.'}; const p=ps[0], r=ps.slice(1);
  return {cor:p.cor,t:p.t,prim:p.prim||null,mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
CAD_ACTS.g_eq=(self,r)=>[cadExcluir(self,'g_eq',r,'equipe',r.nd?'tem pessoas ativas; mude-as de equipe antes':'')];
function c4consPes(self,r){ const V=r.v; const A=alocavel(V); const eqc=c4eqcal(self); const p=c4pend(r);
  const cal=(!V.cal||V.cal==='Da equipe')?((eqc[V.equipe]||'—')+' (da equipe '+(V.equipe||'—')+')'):V.cal+' (próprio)';
  const ver=(self.state.c4_custo||{})[r.id]; const ex=habExig(V.hab);
  return {titulo:'Pessoa · '+V.nome,sub:(V.equipe||'Sem equipe')+' · '+(V.vinc||'—')+' · '+c4sit(V).t,
    prox:p?{cor:p.cor,t:p.t,prim:{t:p.prim.t,go:()=>g2editar(self,GR('g_pes'),r.id,p.prim.campo)}}:(A.inat?{cor:'gray',t:'Inativa: fora da alocação em O.S.; o histórico continua.'}:{cor:'green',t:'Alocável em O.S.: habilitações exigidas válidas.'}),
    sec:[{t:'Editar pessoa',go:()=>g2editar(self,GR('g_pes'),r.id)}],
    blocos:[{t:'Habilidades e habilitações',lin:[{l:'Habilidades',v:ml(V.hab).join(', ')||'—'}].concat(ex.map(x=>{ const y=A.t.find(z=>z.x===x)||{}; const k=(C4.habil.find(h=>h[0]===x)||[])[1];
        return {l:x,v:y.s==='pend'?'pendente: não alocável em O.S.':(y.s==='venc'?'vencida em '+br(y.d)+': não alocável em O.S.':'válida até '+br(V[k])+(y.s==='vence'?' (vence em 30 dias)':'')),cor:(y.s==='pend'||y.s==='venc')?'red':(y.s==='vence'?'yellow':'')}; }))},
      {t:'Vínculo',lin:[{l:'Vínculo',v:V.vinc},{l:'Admissão',v:br(V.adm)},{l:'Disponível até',v:V.ate?br(V.ate):'sem data'}]},
      {t:'Calendário e acesso',lin:[{l:'Calendário',v:cal},{l:'Acesso ao app',v:V.acesso||'Sem login',h:(V.acesso==='Sem login'||!V.acesso)?('CF-01.dc.html#reg='+encodeURIComponent(r.id)):'',ht:'Solicitar acesso'}],
        nota:'Pessoa não é usuário: o login é criado em Configurações (CF-01).'},
      {t:'Custo-hora (restrito)',lin:ver?[{l:'Custo-hora com encargos',v:isnum(V.custo)&&String(V.custo)!==''?'R$ '+nf(V.custo,2)+'/h':'—'}]:[],
        nota:ver?'Visível só para quem tem permissão de custos (no software real, decide o servidor).':'Recolhido: visível só para quem tem permissão de custos.',
        lks:[{t:ver?'Ocultar custo-hora':'Mostrar custo-hora',go:()=>self.setState({c4_custo:Object.assign({},self.state.c4_custo||{},{[r.id]:!ver})})}]}]}; }
function c4consEq(self,r){ const V=r.v; const ms=c4membros(self,r.id).filter(p=>p.v.sit!=='Inativa'); const ps=c4pends(self,r.id);
  return {titulo:'Equipe · '+V.nome,sub:'Líder '+(V.lider||'—')+' · '+(V.cal||'')+' · '+ms.length+(ms.length===1?' pessoa ativa':' pessoas ativas'),
    prox:ps.length?{cor:ps[0].cor,t:ps[0].t,mais:ps.length>1?('e mais '+(ps.length-1)+'.'):''}:{cor:'green',t:'Em dia: líder ativo e todos alocáveis.'},
    sec:[{t:'Editar equipe',go:()=>g2editar(self,GR('g_eq'),r.id)}],
    blocos:[{t:'Pessoas da equipe',fil:ms.map(p=>{ const S=c4sit(p.v); return {t:p.v.nome,sub:ml(p.v.hab).join(', '),chip:{t:S.t,c:S.res==='nao'?'red':(S.res?'yellow':'green')},al:'Abrir pessoa '+p.v.nome,
        go:()=>{ g2set(self,'g_eq',{fm:null}); g2open(self,GR('g_pes'),p.id,null,{pai:{gid:'g_eq',rid:r.id,t:V.nome}}); }}; }),nota:ms.length?'':'Nenhuma pessoa ativa nesta equipe.'},
      {t:'Calendário',lin:[{l:'Calendário',v:V.cal},{l:'Jornada',v:c4hdia(V.cal)||'—'},{l:'Líder',v:V.lider||'—'}]}]}; }
function c4cfg(self){ cmdIni(self,{gp:'eq',ip:{g_pes:'pes'},
  grupoDe:(s,gid,r)=>{ const g=c4eqDe(s,r); const sel=cmdSel(s); return (sel===''&&s.state.mx_sel!==undefined)?'':g; },
  existeGrupo:(s,id)=>id===C4.sem||RW(s,'g_eq').some(e=>e.id===id),
  reg:(s,id)=>RW(s,'g_pes').some(p=>p.id===id)?{gid:'g_pes',rid:id}:(RW(s,'g_eq').some(e=>e.id===id)?{grupo:id}:null),
  indisp:(id)=>cmdIndisp('Pessoa',id,true),
  indispGrupo:(id)=>'Equipe “'+id+'” indisponível: não existe neste cadastro ou não está liberada para o seu perfil.',
  inativo:(gid,r)=>r.v.sit==='Inativa'?{c4qf:'inat'}:null,
  anuncio:(s,id)=>{ const ms=c4membros(s,id).filter(p=>p.v.sit!=='Inativa'); const n=c4pends(s,id).length; const e=RW(s,'g_eq').find(x=>x.id===id);
    return (id===C4.sem?'Sem equipe':(e?e.v.nome:'Todas as pessoas'))+': '+ms.length+(ms.length===1?' pessoa':' pessoas')+' · '+(n?n+' a resolver':'Em dia'); },
  cons:{g_pes:c4consPes,g_eq:c4consEq}}); }
function PREVALS(self,v){ cadActsIni(self); c4cfg(self); if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const ps=RW(self,'g_pes'); self._c4eq=self._c4eq||{}; self._c4pes=self._c4pes||{}; const sel=cmdSel(self); const q=self.state.mx_q||'';
  ps.forEach(r=>{ const V=r.v; self._c4pes[r.id]=V.nome;
    r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.p.equipe=[{k:'txt',t:V.equipe||'—'}]; r.s.equipe=V.equipe||'';
    const hs=ml(V.hab); r.m=Object.assign({},r.m||{},{habs:hs.map(h=>({id:h,l:h}))}); r.p.habs=[hs.length?{k:'txt',t:hs.join(', ')}:{k:'mut',t:'—'}]; r.s.habs=hs.join(', ');
    r.p.vinc=[{k:'txt',t:V.vinc||'—'}]; r.s.vinc=V.vinc||'';
    const A=alocavel(V); const ex=habExig(V.hab); r.m.habx=ex.map(x=>({id:x,l:x})); r.p.habx=[ex.length?{k:'txt',t:ex.join(', ')}:{k:'mut',t:'—'}]; r.s.habx=ex.join(', ');
    const hv=c4val(A); V.habv=hv; const pend=A.t.some(y=>y.s==='pend'); const hvc=A.t.some(y=>y.s==='venc')?'red':(A.vence?'yellow':'');
    r.p.habv=[hv?(hvc?{k:'cn',t:br(hv),c:hvc}:{k:'txt',t:br(hv)}):(pend?{k:'cn',t:'pendente',c:'red'}:{k:'mut',t:'—'})]; r.s.habv=hv?br(hv):(pend?'pendente':'');
    const ac=V.acesso||'Sem login'; r.p.acesso=[{k:ac==='Com login'?'mut':'txt',t:ac}]; r.s.acesso=ac;
    const S=c4sit(V); r.p.est=S.p; r.s.est=S.t; });
  // mestre → busca da tela (nome, equipe, habilidade, vínculo) → filtro rápido e função
  cmdPasse(ps,'cadm_g_pes',r=>!sel||c4eqDe(self,r)===sel);
  cmdPasse(ps,'cadb_g_pes',r=>cmdCasa([r.v.nome,r.v.equipe,r.v.hab,r.v.vinc,r.v.funcao].join(' '),q));
  const fun=cadSel(self,v,'c4fun',[{v:'',t:'Todas'}].concat(C4.qf.filter(([k])=>k!=='nao').map(([k,t])=>({v:k,t:t+' ('+ps.filter(r=>c4qf(k,r.v,alocavel(r.v))).length+')'}))));
  cmdQf(self,v,'g_pes','c4qf',Object.assign([{k:'res',t:'A resolver',f:r=>!!c4sit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oculta:true}],{todos:'Todas'}),ps);
  if(fun) ps.forEach(r=>{ if(!r.sh&&!c4qf(fun,r.v,alocavel(r.v))) r.sh='cadqf_g_pes'; });
  GR('g_pes').cols=sel?C4.cols:C4.cols.slice(0,6).concat([C4.coleq]); v.c4_ncol=GR('g_pes').cols.length;
  const eqs=RW(self,'g_eq');
  eqs.forEach(r=>{ self._c4eq[r.id]=r.v.nome; const n=ps.filter(p=>p.v.equipe===r.v.nome&&p.v.sit!=='Inativa').length; r.v.membros=n; r.nd=n?'tem pessoas':''; r.s.nome=r.v.nome||''; });
  const fe=(GR('g_eq').edit.fields||[]).find(x=>x.k==='lider'); if(fe) fe.opts=ps.filter(p=>p.v.sit!=='Inativa').map(p=>p.v.nome);
  const fq=(GR('g_pes').edit.fields||[]).find(x=>x.k==='equipe'); if(fq) fq.opts=eqs.map(e=>e.v.nome); }
function EXTRAVALS(self,v){ const ps=RW(self,'g_pes'); const eqc=c4eqcal(self); const eqs=RW(self,'g_eq'); const sel=cmdSel(self); const q=self.state.mx_q||''; const larga=cadLarga();
  // ---- mestre: Todas as pessoas · equipes (líder, pessoas, pendência) · Sem equipe ----
  const at=ps.filter(p=>p.v.sit!=='Inativa'); const sem=at.filter(p=>c4eqDe(self,p)===C4.sem);
  const casa=(id,nome)=>!q||id===sel||cmdCasa(nome,q)||c4membros(self,id).some(p=>cmdCasa([p.v.nome,p.v.hab].join(' '),q));
  const res=(id)=>{ const ps2=c4pends(self,id); return ps2.length?{t:ps2.length+' a resolver',c:ps2.some(x=>x.cor==='red')?'red':'yellow'}:{t:'Em dia',c:'green'}; };
  const its=eqs.filter(e=>casa(e.id,e.v.nome)).map(e=>{ const ms=c4membros(self,e.id).filter(p=>p.v.sit!=='Inativa'); const r=res(e.id);
    return {id:e.id,t:e.v.nome,n:String(ms.length),sub:'Líder '+(e.v.lider||'—')+(c4hdia(e.v.cal)?' · '+c4hdia(e.v.cal):''),res:r.t,cor:r.c}; });
  if(sem.length&&casa(C4.sem,'Sem equipe')){ const r=res(C4.sem); its.push({id:C4.sem,t:'Sem equipe',n:String(sem.length),sub:'calendário da própria pessoa',res:r.t,cor:r.c}); }
  cadMestreVals(self,v,{todos:{t:'Todas as pessoas',sub:at.length+' pessoas ativas',n:''},itens:its,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga){ eqs.filter(e=>cmdCasa(e.v.nome,q)).forEach(e=>rs.push({t:e.v.nome,sub:'Equipe · '+(e.v.membros||0)+' pessoas',go:()=>{ self.setState({mx_q:''}); cmdEscolhe(self,e.id); }}));
    ps.filter(p=>p.v.sit!=='Inativa'&&cmdCasa([p.v.nome,p.v.equipe,p.v.hab].join(' '),q)).forEach(p=>rs.push({t:p.v.nome+' · '+(p.v.equipe||'Sem equipe'),sub:'Pessoa · '+(ml(p.v.hab).join(', ')||'—'),go:()=>cmdAbre(self,'g_pes',p.id,c4eqDe(self,p))})); }
  cadResVals(v,rs); v.c4_neq=()=>{ g2new(self,GR('g_eq')); };
  // ---- detalhe do grupo ----
  const e=sel&&sel!==C4.sem?eqs.find(x=>x.id===sel):null; const pd=c4pends(self,sel);
  const chip=pd.length?{t:pd.length+' a resolver',c:pd.some(x=>x.cor==='red')?'red':'yellow'}:{t:'Em dia',c:'green'}; const av=cmdAviso(self,'Ver todas as pessoas');
  if(e){ const ms=c4membros(self,e.id).filter(p=>p.v.sit!=='Inativa');
    cadDetVals(self,v,Object.assign({t:e.v.nome,sub:'Líder '+(e.v.lider||'—')+' · '+(e.v.cal||'')+(c4hdia(e.v.cal)?' · '+c4hdia(e.v.cal):'')+' · '+ms.length+(ms.length===1?' pessoa ativa':' pessoas ativas'),
      chip:chip,ficha:{t:'Ver ficha da equipe',go:()=>g2open(self,GR('g_eq'),e.id,null)},prox:c4prox(pd),volta:'Equipes',voltar:()=>cmdVolta(self)},av)); }
  else if(sel===C4.sem) cadDetVals(self,v,Object.assign({t:'Sem equipe',sub:sem.length+(sem.length===1?' pessoa ativa':' pessoas ativas')+' sem equipe: o calendário vem da própria pessoa',chip:chip,
      prox:pd.length?c4prox(pd):{cor:'gray',t:'Para incluir numa equipe, use Editar pessoa no painel da pessoa.'},volta:'Equipes',voltar:()=>cmdVolta(self)},av));
  else { const nao=at.filter(p=>!alocavel(p.v).ok).length;
    cadDetVals(self,v,Object.assign({t:'Todas as pessoas',sub:at.length+' pessoas ativas · '+eqs.length+' equipes'+(nao?' · '+nao+' não alocáveis em O.S.':''),chip:chip,prox:c4prox(pd),volta:'Equipes',voltar:()=>cmdVolta(self)},av)); }
  // "+ Criar pessoa": a primária da tela; herda a equipe escolhida (em "Todas" e "Sem equipe", "Escolha…")
  v.cab_criar_on=true; v.cab_criarT='+ Criar pessoa';
  v.c4_criar=()=>{ g2set(self,'g_pes',{fm:null}); g2new(self,GR('g_pes'),{draft:{equipe:e?e.v.nome:''}}); setTimeout(()=>{ try{ const x=document.getElementById('fx_g_pes_nome'); if(x) x.focus(); }catch(z){} },90); };
  // ---- grade: contagem, filtro e vazio com próximo passo ----
  const nao=ps.filter(r=>c4sit(r.v).res==='nao').length, ven=ps.filter(r=>c4sit(r.v).res==='ven').length;
  cadEstado(v,'c4e',[nao?nao+(nao>1?' não alocáveis':' não alocável'):'',ven?ven+' a renovar em 30 dias':''].filter(Boolean).join(' · ')||'Todos alocáveis',nao?'red':(ven?'yellow':'green'));
  cadQfPos(self,v,'g_pes','c4qf'); const ct=cmdConta(self,'g_pes',ps); v.c4_conta=ct.n+' de '+ct.tot;
  if(self.state.c4fun){ v.g_pes_filtered=true; v.g_pes_clear=()=>{ g2set(self,'g_pes',{q:'',f:{}}); self.setState({c4qf:'',c4fun:''}); }; }
  const vz=!ct.n?(q?{t:'Nenhuma pessoa encontrada para “'+q+'”. Para cadastrar, use + Criar pessoa, no topo.'}:(ct.tot?{t:'Nenhuma pessoa com este filtro.',go:{t:'Mostrar todas',fn:()=>self.setState({c4qf:'',c4fun:''})}}:{t:(e?'A equipe '+e.v.nome+' não tem pessoa. Crie em + Criar pessoa, no topo, ou mude a equipe de alguém em Editar pessoa.':'Nenhuma pessoa aqui.')})):null;
  cadVazioSe(self,v,'c4_v',vz,['g_pes']);
  // ---- formulários (Editar pessoa, + Criar pessoa, Editar equipe) ----
  const F=v.g_pes_F; if(F&&F.open&&F.fields){ const fm=g2st(self,'g_pes').fm||{}; const d=fm.draft||{}; const ex=habExig(d.hab);
    F.fields=F.fields.filter(f=>{ const h=C4.habil.find(y=>f.fid==='fx_g_pes_'+y[1]); return !h||ex.indexOf(h[0])>=0; });
    C4.habil.forEach(([x,k])=>{ const f=F.fields.find(y=>y.fid==='fx_g_pes_'+k); if(!f) return; const dv=d[k];
      if(!dv||dv<HOJE){ f.help=(dv?'Vencida':'Pendente')+': grava, mas a pessoa fica não alocável em O.S.'; f.hasHelp=true; } else { f.help=''; f.hasHelp=false; } });
    const fh=F.fields.find(f=>f.fid==='fx_g_pes_hab'); if(fh){ fh.help=ex.length?'Exige '+lista(ex)+' com validade.':'Nenhuma habilitação exigida.'; fh.hasHelp=true; }
    const fq=F.fields.find(f=>f.fid==='fx_g_pes_equipe'); if(fq){ const c=eqc[d.equipe]; fq.help=c?'Calendário da equipe: '+c+' · '+c4hdia(c):''; fq.hasHelp=!!c; }
    const fa=F.fields.find(f=>f.fid==='fx_g_pes_acesso'); if(fa){ const cur=(fm.orig||{}).acesso||'Sem login';
      if(cur==='Com login'||cur==='Acesso solicitado'){ fa.opts=[{v:cur,t:cur}]; fa.dis=true; fa.ist=fa.ist.replace('background:#FFFFFF','background:#F4F6F3'); fa.help=cur==='Com login'?'A ficha de execução no app usa este login.':'Pedido enviado ao administrador (simulado).'; }
      else { fa.opts=['Sem login','Solicitar acesso ao app'].map(o=>({v:o,t:o})); fa.help='Solicitar envia o pedido ao administrador ao salvar (simulado).'; }
      fa.hasHelp=true; } }
  const FE=v.g_eq_F; const lidInat=(n)=>{ const P=ps.find(p=>p.v.nome===n); return !!n&&(!P||P.v.sit==='Inativa'); };
  if(FE&&FE.open&&FE.fields){ const d=(g2st(self,'g_eq').fm||{}).draft||{}; const fl=FE.fields.find(f=>f.fid==='fx_g_eq_lider');
    if(fl&&lidInat(d.lider)&&!fl.err&&FE.edit){ fl.help=d.lider+' está inativa; escolha um líder ativo.'; fl.hasHelp=true; } }
  selFiel(v.g_pes_F,{fx_g_pes_equipe:' · equipe excluída'}); selFiel(FE,{fx_g_eq_lider:' · inativa'});
  valida(self,v,'g_pes',(d,fm)=>{ const e={};
    if(d.ate&&d.adm&&d.ate<d.adm) e.ate='Disponível até não pode ser antes da admissão ('+br(d.adm)+').';
    else if((d.vinc==='Safrista'||d.vinc==='Diarista')&&!d.ate) e.ate='Informe até quando o '+d.vinc.toLowerCase()+' fica disponível.';
    const dup=unico(self,'g_pes',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe '+dup.v.nome+'.'; return e; });
  valida(self,v,'g_eq',(d,fm)=>{ const e={}; const dup=unico(self,'g_eq',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe a equipe '+d.nome+'.';
    if(lidInat(d.lider)) e.lider=d.lider+' está inativa; escolha um líder ativo.'; return e; });
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_pes'){ let ped=false; if(r.v.acesso==='Solicitar acesso ao app'){ r.v.acesso='Acesso solicitado'; ped=true; g2set(self,'g_pes',{rows:g2clone(rows)}); }
      const old=(self._c4pes||{})[r.id]; const es=g2clone(RW(self,'g_eq')); const ren=[];
      if(old&&old!==r.v.nome){ es.forEach(e=>{ if(e.v.lider===old){ e.v.lider=r.v.nome; ren.push(e.v.nome); } }); if(ren.length) g2set(self,'g_eq',{rows:es}); }
      const A=alocavel(r.v); const lid=es.filter(e=>e.v.lider===r.v.nome).map(e=>e.v.nome);
      self.setState({g2toast:ponto((isNew?'Criada: ':'Salvo: ')+r.v.nome+' · '+(A.inat?'inativa':(A.ok?'alocável em O.S.':'não alocável em O.S. até resolver '+A.m))
        +(ped?' · pedido de acesso ao app enviado ao administrador (simulado)':'')
        +(A.inat&&lid.length?' · escolha outro líder para '+lista(lid):(ren.length?' · líder de '+lista(ren)+' atualizado':'')))}); }
    if(gid==='g_eq'){ const old=(self._c4eq||{})[r.id]; let n=0;
      if(old&&old!==r.v.nome){ const ps2=g2clone(RW(self,'g_pes')); ps2.forEach(p=>{ if(p.v.equipe===old){ p.v.equipe=r.v.nome; n++; } }); g2set(self,'g_pes',{rows:ps2}); }
      if(isNew){ g2set(self,'g_eq',{fm:null}); self.setState({mx_sel:r.id,mx_nivel:'d'}); cadHashPoe(self,{eq:r.id}); }
      self.setState({g2toast:(isNew?'Equipe criada: ':'Salvo: ')+r.v.nome+' · '+r.v.cal+' · '+c4hdia(r.v.cal)+(n?' · '+n+(n>1?' pessoas seguem':' pessoa segue')+' a equipe':'')+'.'}); } }; }
'''
