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
from areas.cadastros import (cadx_css, abas, pane, faixa, prim, qf_chips, filtro_sel, barra, cartoes, bloco_cad, estado_cab, acoes_form)

H=lambda s: '{{'+s+'}}'
for _f in ('CD-03.dc.html','CD-04.dc.html'): ui37.H_OVR.pop(_f,None)   # layout novo: a altura vem de HEIGHTS37

# ---------------- pessoas, habilidades e habilitações (fonte do CD-04; o CD-03 lê para os operadores do conjunto) ----------------
CALDA='Preparar calda (caldeiro)'; AGRO='Liberar O.S. (agrônomo)'
HABILIDADES=['Operar trator','Operar pulverizador','Operar plantadeira','Operar colhedora',CALDA,'Irrigar','Almoxarifado',AGRO,'Conferir','Manutenção de máquinas',
             'Testar reparo','Aprovar O.S. de manutenção','Liberar ativo',   # PCM simplificado (05/10): teste do reparo (D-36) e responsável de manutenção (D-20)
             'Autorizar rota e liberar ordem de processo','Liberar lote (qualidade)']   # BEN-1: Igor e Marta (dados_cad, docs/beneficiamento §2.3)
HAB_EXIGE={'Operar trator':'NR-31','Operar pulverizador':'NR-31','Operar plantadeira':'NR-31','Operar colhedora':'NR-31',CALDA:'NR-31',
           'Irrigar':'NR-10','Manutenção de máquinas':'NR-12',AGRO:'CREA'}
HABIL=[('NR-31','v31','Validade da NR-31'),('NR-10','v10','Validade da NR-10'),('NR-12','v12','Validade da NR-12'),('CREA','vcrea','Validade do registro no CREA')]
_REN={'Preparar calda':CALDA}
# ajustes sobre dados_cad: Paula é a caldeira das O.S. de pulverização (alocacao.py: 'Paula · caldeiro' na OS-0421/0424/0430);
# Rui é o almoxarife que entrega (os_campo.py, cenario.js); habilidade fora da lista (empilhadeira) sai.
_OVR={'p6':dict(funcao='Caldeiro',equipe='Campo 1',hab=[CALDA,'Conferir'],v31='2027-04-30'),
      'p7':dict(funcao='Almoxarife',hab=['Almoxarifado','Conferir']),
      'p10':dict(equipe='Campo 2')}
_ORDEM=['p1','p2','p3','p6','p10','p4','p5','p7','p8','p11','p9','p12','p13']   # p11 Otávio (PCM); p12 Igor e p13 Marta: equipe e8 Beneficiamento e qualidade (BEN-1)
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
            cont.append(dict(k=f'cont_{cd}',l='Leitura do horímetro',t='num',u='h',ro=True,cond=cond('classe',cl),help='Só leitura: vem da Manutenção (abastecimento, conclusão da OM, leitura avulsa); troca de contador se decide lá (PCM S3).'))
    return ([sel('classe','Classe',[c for c,_ in CLS],newOnly=True,help='Abre só a capacidade desta classe; fica fixa depois do cadastro.',**{'def':'Trator'}),
             txt('nome','Nome',help='Ex.: Trator 05. Não pode repetir.'),txt('modelo','Modelo',req=False),
             dict(k='cond_t',l='Condição técnica',t='area',ro=True,help='Vem da Manutenção (condição única); não se altera no cadastro.',**{'def':'Apto'}),
             dict(k='rt',l='Responsável técnico',ro=True,help='Vem da Manutenção (painel Condição); só leitura no cadastro.')]
            + cap
            + [num('custo_h','Custo R$/h da máquina','R$/h',min=0,req=False,help='Combustível, manutenção e depreciação; o operador entra em Pessoas. O rendimento usa este valor (≠ Custo R$/h da oficina, na OM).'),
               sel('custo_f','Fonte do custo',CFONTES,req=False,**{'def':'Premissa a validar'})]
            + cont
            + [sel('exige','Exige calibração ou aferição?',['Sim','Não'],**{'def':'Não'}),
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

def cd03():
    fname='CD-03.dc.html'; E._reset_screen(fname)
    g=grid([dict(k='nome',l='Máquina ou instalação',w=236),dict(k='classe',l='Classe',w=150),dict(k='cap',l='Capacidade',w=190),
            dict(k='custo_h',l='Custo R$/h da máquina',t='num',a='r'),dict(k='ncj',l='Conjuntos',t='num',a='r'),dict(k='est',l='Situação',w=290)],
        _linhas_ativo(),gid='g_atv',total=False,frame=False,
        tools=qf_chips('g_atv')+prim('g_atv_new','Cadastrar máquina ou instalação'),
        edit=dict(m='form',title='Máquina',newTitle='Cadastrar máquina ou instalação',
            sub=SUB_EDIT,fields=_campos_ativo()))
    rend={c['id']:c['rend'] for c in D2.CONJ}
    maqs=[a['nome'] for a in DC.ATIVOS if a['classe'] not in IMPL]; imps=[a['nome'] for a in DC.ATIVOS if a['classe'] in IMPL]
    cj=grid([dict(k='nome',l='Conjunto',w=210),dict(k='ops',l='Operações',w=130),dict(k='larg',l='Largura',t='num',a='r',u='m'),
             dict(k='cond',l='Condição',w=210),dict(k='oper',l='Operadores alocáveis',w=180),dict(k='rend',l='Rendimento',t='num',a='r')],
        [R(k,dict(maq=m,impl=i or SEM_IMPL,ops=op,rend=rend.get(rid,''))) for k,m,i,op,rid in DC.CONJUNTOS],
        gid='g_cj',dele=False,total=False,search=False,
        edit=dict(m='form',title='Conjunto',newTitle='Montar conjunto',sub='Escolha a máquina, o implemento e as operações; a largura vem do implemento.',
            fields=[sel('maq','Máquina',maqs),sel('impl','Implemento',[SEM_IMPL]+imps,**{'def':SEM_IMPL}),
                    dict(k='ops',l='Operações',t='multi',opts=OPS,req=True),
                    dict(k='larg_c',l='Largura de trabalho',ro=True,live=True,u='m',help='Herdada do implemento (ou da plataforma da colhedora).'),
                    dict(k='pot_c',l='Potência',ro=True,live=True,help='O trator precisa ter ao menos a potência que o implemento exige.')]))
    # um bloco com abas: Máquinas e instalações (tabela) | Conjuntos (cartões); a ação de cada entidade fica na sua aba
    acoes_form('g_atv'); acoes_form('g_cj'); cadx_css()
    p1=(barra(f'<span style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("c3_ncj")}</span>',prim('g_cj_new','Montar conjunto'))+cartoes('c3_cjs','Conjuntos'))
    corpo=bloco_cad(abas('c3t',['Máquinas e instalações','Conjuntos'],'Cadastros de máquinas'),pane('c3t',0,faixa('c3_fx0')+g)+pane('c3t',1,p1),'Máquinas, instalações e setores')
    dados=dict(cod=COD,impl=IMPL,calib=CALIB_CLS,sem=SEM_IMPL,ophab=OPHAB,subnew=SUB_NEW,
               cond={k:dict(t=c['t'],m=c['om']+' · '+c['det'],ordens=c['ordens'],om=c['om']) for k,c in DC.CONDICAO.items()},
               pes=[dict(v,id=pid) for pid,v in pessoas()])
    import cenario   # PCM simplificado S3: condição, responsável técnico e leitura do cenário único (c.man)
    js({},cenario.js_prefixo()+ALOC_JS+'const C3='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
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
/* condição única (PCM simplificado S3, F107): lida de c.man do cenário, a mesma da Manutenção e da O.S.; o cadastro não a altera */
function c3man(id){ try{ return ((cenGet().man||{}).ativos||{})[id]||null; }catch(e){ return null; } }
function c3cond(r){ const V=r.v; if(V.sit==='Inativo') return {t:'Inativo',c:'gray',ok:false,curto:'inativo'}; const a=c3man(r.id); const x=C3.cond[r.id];
  if(a&&a.cond==='Bloqueado'){ const i=a.condInfo||{}; const om=i.om||''; const o=om?(cenGet().man.oms||{})[om]:null;
    const nm=(i.mais||[]).length;   /* revisão 09/10 (A1): outros motivos de bloqueio, cada um com a sua OM, na Manutenção */
    const xx={t:'Bloqueado',om,ordens:(x&&x.ordens)||[],m:(om?om+' · ':'')+(i.motivo||'')+(o&&o.ret?' · retorno previsto '+o.ret:'')+(nm?' · +'+nm+(nm>1?' motivos':' motivo')+' na Manutenção':'')};
    return {t:'Bloqueado',c:'red',ok:false,m:xx.m,x:xx,curto:'bloqueado',aid:a.id}; }
  if(a&&a.cond==='Restrito'){ const i=a.condInfo||{}; return {t:'Restrito',c:'yellow',ok:true,m:(i.lim||i.motivo||'')+(i.ate?' · até '+i.ate.split('-').reverse().slice(0,2).join('/'):''),curto:'restrito',aid:a.id}; }
  return {t:'Apto',c:'green',ok:true}; }
function c3calib(V){ if(V.exige!=='Sim') return {p:[{k:'mut',t:'não exige'}],s:'não exige',bad:false};
  if(!V.calib) return {p:[chipc('Aferir','yellow'),{k:'mut',t:'sem registro'}],s:'Aferir',bad:true};
  const venc=addd(V.calib,V.interv||0); const d=ddiff(HOJE,venc);
  if(d<0) return {p:[chipc('Vencida em '+br(venc),'red')],s:'Vencida',bad:true};
  if(d<=15) return {p:[chipc('Vence '+br(venc),'yellow')],s:'Vence',bad:false};
  return {p:[chipc('Em dia até '+br(venc),'green')],s:'Em dia',bad:false}; }
// última leitura gravada do horímetro por máquina (atualizada a cada salvar; a trava compara com ela)
const CONT0={}; function c3lei(r){ const c=c3v(r.v,'cont'); if(isnum(c)&&String(c)!=='') CONT0[r.id]=Number(c); }
GR('g_atv').rows.forEach(c3lei);
function c3opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }
// quem opera o conjunto: tem todas as habilidades das operações e está alocável (CD-04)
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
// situação da máquina: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o estado do cabeçalho
function c3sit(r){ const V=r.v; const C=c3cond(r), K=c3calib(V);
  if(V.sit==='Inativo') return {t:'Inativa',p:[chipc('Inativa','gray')]};
  if(C.t==='Bloqueado') return {t:'Bloqueado',p:sitX('Bloqueado','red','Ver ordens afetadas','OS.dc.html'),res:'man'};
  if(K.s==='Vencida') return {t:'Calibração vencida',p:sitX('Calibração vencida','red','Registrar calibração'),res:'cal'};
  if(K.s==='Aferir') return {t:'Sem aferição',p:sitX('Sem aferição','yellow','Registrar aferição'),res:'cal'};
  if(K.s==='Vence') return {t:'Apta',p:sitOk('Apta · calibrar até '+br(addd(V.calib,V.interv||0)))};
  return {t:'Apta',p:sitOk('Apta')}; }
function c3usos(self){ const u={}; RW(self,'g_cj').forEach(r=>{ [r.v.maq,r.v.impl].forEach(n=>{ if(n&&n!==C3.sem) (u[n]=u[n]||[]).push(r); }); }); return u; }
function c3temR(V){ return isnum(V.rend)&&String(V.rend)!==''; }
// painel da máquina: os conjuntos que a usam (cada um abre o conjunto); painel do conjunto: rendimento e exclusão
CAD_ACTS.g_atv=(self,r,fm)=>{ if(g2dirty(fm)) return []; const us=(c3usos(self)[r.v.nome]||[]);
  return us.map((c,i)=>{ const o=c.v.maq===r.v.nome?(c.v.impl&&c.v.impl!==C3.sem?c.v.impl:''):c.v.maq;
    return {t:(o?o+' · ':'')+(ml(c.v.ops).join(', ')||'conjunto')+' ›',h:i===us.length-1?(us.length>1?'Conjuntos que usam esta máquina.':'Conjunto que usa esta máquina.'):'',go:()=>{ g2set(self,'g_atv',{fm:null}); g2open(self,GR('g_cj'),c.id,null); }}; }); };
CAD_ACTS.g_cj=(self,r)=>[c3temR(r.v)?null:{t:'Cadastrar rendimento ›',h:'Sem rendimento o planejamento não calcula horas nem custo deste conjunto.',go:()=>{ location.href='CD-02.dc.html#aba=operacoes'; }},
  cadExcluir(self,'g_cj',r,'conjunto',r.nd?'tem rendimento em Culturas e operações; troque o conjunto lá antes':'')];
function PREVALS(self,v){ cadActsIni(self); const atv=RW(self,'g_atv'); self._c3nomes=self._c3nomes||{}; const usos=c3usos(self);
  atv.forEach(r=>{ const V=r.v; self._c3nomes[r.id]=V.nome; const C=c3cond(r);
    r.p.nome=[{k:'b',t:V.nome||''}].concat(V.modelo?[{k:'mut',t:V.modelo}]:[]); r.s.nome=(V.nome||'')+' '+(V.modelo||'');
    r.p.classe=[{k:'txt',t:V.classe||'—'}]; r.s.classe=V.classe||'';
    r.p.cap=[{k:'txt',t:c3cap(V)}]; r.s.cap=c3cap(V);
    V.cond_t=C.m?C.t+' · '+C.m:C.t; const am=c3man(r.id); if(am){ V.rt=am.rt||'Otávio'; const cd=C3.cod[V.classe]; if(cd&&am.leit) V['cont_'+cd]=am.leit.val; }
    r.o=(C.x?[{t:'Ver ordens afetadas · '+C.x.ordens.join(' e '),h:'OS.dc.html'}].concat(C.x.om?[{t:'Abrir '+C.x.om+' na Manutenção',h:'MA.dc.html#om='+C.x.om}]:[]):[]).concat(am?[{t:'Abrir '+V.nome+' na Manutenção',h:'MA.dc.html#ativo='+r.id}]:[]);
    r.p.custo_h=isnum(V.custo_h)&&String(V.custo_h)!==''?[{k:'txt',t:'R$ '+nf(V.custo_h,2)+'/h'}]:[{k:'mut',t:'—'}];
    const n=(usos[V.nome]||[]).length; V.ncj=n; r.p.ncj=[{k:(n?'txt':'mut'),t:n?String(n):'—'}]; r.s.ncj=n?String(n):'';
    const S=c3sit(r); r.p.est=S.p; r.s.est=S.t; });
  cadQf(self,v,'g_atv','c3qf',[{k:'res',t:'A resolver',f:r=>!!c3sit(r).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativo',oz:true}]);
  c3opts('g_cj','maq',atv.filter(r=>C3.impl.indexOf(r.v.classe)<0).map(r=>r.v.nome));
  c3opts('g_cj','impl',[C3.sem].concat(atv.filter(r=>C3.impl.indexOf(r.v.classe)>=0).map(r=>r.v.nome)));
  // conjuntos em cartões: máquina + implemento, operações, largura, rendimento e potência; operadores no rodapé; exceção no chip
  const cjs=RW(self,'g_cj'); v.c3_ncj=cjs.length+(cjs.length===1?' conjunto':' conjuntos');
  cjs.forEach(r=>{ const V=r.v; const X=c3conj(self,V); r.s.nome=(V.maq||'')+(X.I?' + '+V.impl:''); const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null); V.larg=lg===null?'':lg;
    r.nd=c3temR(V)?'tem rendimento':''; });
  cadCartoes(self,v,'c3_cjs','g_cj',cjs.map(r=>{ const V=r.v; const X=c3conj(self,V); const O=c3oper(V.ops); const temR=c3temR(V);
    const pot=X.M&&X.M.v.classe==='Trator'?c3n(X.M.v,'pot'):null; let chip=null, verbo='', det='';
    if(X.bad.length){ chip={t:'Indisponível',c:'red'}; det=X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(' · ')+(X.sub?' · substituto: '+X.sub.v.nome+' ('+nfa(c3n(X.sub.v,'pot'))+' cv)':''); verbo=X.sub?'Trocar pelo '+X.sub.v.nome:'Trocar máquina'; }
    else if(X.cal.length){ chip={t:'Calibrar antes de usar',c:'yellow'}; det=X.cal.map(x=>x.v.nome+' · '+c3calib(x.v).s.toLowerCase()).join(' · '); verbo='Registrar calibração'; }
    else if(!temR) chip={t:'Sem rendimento',c:'yellow'};
    return {id:r.id,nome:r.s.nome,chip:chip,sub:ml(V.ops).join(' · ')+(det?' · '+det:''),
      nums:[{v:V.larg===''?'—':nfa(V.larg),u:V.larg===''?'':'m',l:'Largura'},{v:temR?nf(V.rend,2):'—',u:temR?'ha/h':'',l:'Rendimento'}].concat(pot!==null?[{v:nfa(pot),u:'cv',l:'Potência'}]:[]),
      rod:'Operadores: '+O.p.map(x=>x.t).join(' · '),verbo:verbo,sitT:'Disponível'}; })); }
function EXTRAVALS(self,v){
  const atv=RW(self,'g_atv'); const manL=atv.filter(r=>c3sit(r).res==='man'), calL=atv.filter(r=>c3sit(r).res==='cal'); const man=manL.length, cal=calL.length;
  cadEstado(v,'c3e',[man?man+(man>1?' máquinas bloqueadas':' máquina bloqueada'):'',cal?cal+(cal>1?' calibrações a resolver':' calibração a resolver'):''].filter(Boolean).join(' · ')||'Máquinas aptas e calibradas',
            man?'red':(cal?'yellow':'green'));
  const cjs=RW(self,'g_cj'); const cjBad=cjs.filter(r=>c3conj(self,r.v).bad.length).length, cjAv=cjs.filter(r=>{ const X=c3conj(self,r.v); return !X.bad.length&&(X.cal.length||!c3temR(r.v)); }).length;
  cadAbas(self,v,'c3t','c3aba',[{slug:'maquinas',n:atv.length,cor:man?'red':(cal?'yellow':'')},{slug:'conjuntos',n:cjs.length,cor:cjBad?'red':(cjAv?'yellow':'')}]);
  cadQfPos(self,v,'g_atv','c3qf');
  const res=()=>self.setState({c3qf:'res'}); const venc=calL.some(r=>c3calib(r.v).s==='Vencida');
  cadFaixa(v,'c3_fx0',[man?{n:man,rot:man>1?'máquinas bloqueadas':'máquina bloqueada',reg:manL.map(r=>{ const x=c3cond(r); return r.v.nome+(x.m?' · '+x.m:''); }).join(', '),verbo:'Ver ordens afetadas',cor:'red',
                            go:()=>{ location.href='OS.dc.html'; }}:null,
                        cal?{n:cal,rot:cal>1?'calibrações a resolver':'calibração a resolver',reg:calL.map(r=>r.v.nome).join(', '),verbo:'Registrar calibração',cor:venc?'red':'yellow',
                            go:cal===1?()=>g2open(self,GR('g_atv'),calL[0].id,null):res}:null],res);
  // classe escolhida no cadastro novo já marca se exige calibração (continua editável)
  const F=v.g_atv_F; if(F&&F.open&&F.fields){ const f=F.fields.find(x=>x.fid==='fx_g_atv_classe');
    if(f&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_atv').fm; if(!cur) return; const val=e.target.value; const d=Object.assign({},cur.draft,{classe:val});
      if(cur.isNew) d.exige=C3.calib.indexOf(val)>=0?'Sim':'Não'; const er=Object.assign({},cur.errs||{}); delete er.classe;
      g2set(self,'g_atv',{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }; }
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
    if(d.exige==='Sim'&&d.calib&&d.calib>HOJE) e.calib='A calibração não pode ser em data futura.';
    if(d.classe!=='Armazenagem'&&!String(d.custo_h||'').trim()) e.custo_h='Informe o custo por hora; o rendimento e o custo da O.S. usam este valor.';
    else if(String(d.custo_h||'').trim()&&!d.custo_f) e.custo_f='Informe de onde vem o custo.';
    const dup=unico(self,'g_atv',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe '+dup.v.nome+'.'; return e; });
  valida(self,v,'g_cj',(d,fm)=>{ const e={}; const atv=RW(self,'g_atv'); const M=atv.find(r=>r.v.nome===d.maq); const I=(d.impl&&d.impl!==C3.sem)?atv.find(r=>r.v.nome===d.impl):null;
    if(M&&I&&M.v.classe!=='Trator') e.impl='Implemento vai num trator; '+M.v.nome+' é '+String(M.v.classe).toLowerCase()+'.';
    else if(M&&I){ const p=c3n(M.v,'pot'), q=c3n(I.v,'preq'); if(p!==null&&q!==null&&p<q) e.maq=M.v.nome+' tem '+nfa(p)+' cv; '+I.v.nome+' exige '+nfa(q)+' cv. Escolha um trator mais potente.'; }
    if(!e.maq&&!e.impl){ const dup=RW(self,'g_cj').find(r=>r.id!==fm.rid&&r.v.maq===d.maq&&(r.v.impl||C3.sem)===(d.impl||C3.sem)); if(dup) e.maq='Este conjunto já existe ('+ml(dup.v.ops).join(', ')+'); edite a linha dele.'; }
    return e; });
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_atv'){ const old=(self._c3nomes||{})[r.id]; c3lei(r);
      if(old&&old!==r.v.nome){ const cs=g2clone(RW(self,'g_cj')); cs.forEach(c=>{ if(c.v.maq===old) c.v.maq=r.v.nome; if(c.v.impl===old) c.v.impl=r.v.nome; }); g2set(self,'g_cj',{rows:cs}); }
      const C=c3cond(r); self.setState({g2toast:(isNew?'Cadastrado: ':'Salvo: ')+r.v.nome+' · '+c3cap(r.v)+(isnum(r.v.custo_h)&&String(r.v.custo_h)!==''?' · R$ '+nf(r.v.custo_h,2)+'/h':'')+' · '+C.t+'.'}); }
    if(gid==='g_cj'){ const X=c3conj(self,r.v); const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null);
      self.setState({g2toast:(isNew?'Conjunto montado: ':'Salvo: ')+r.v.maq+(X.I?' + '+r.v.impl:'')+' · '+ml(r.v.ops).join(', ')+(lg!==null?' · '+nfa(lg)+' m':'')
        +(X.bad.length?' · indisponível: '+X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(', '):' · disponível')+(isNew?'. Cadastre o rendimento em Culturas e operações.':'.')}); } }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela ou os cartões da aba rolam
    shell37('CD-03','Máquinas, instalações e setores',corpo,fname=fname,status=None,primary_html=None,search=False)
    estado_cab(fname,'Máquinas, instalações e setores','c3e')

# ================= CD-04 · Pessoas e equipes =================
QF=[('ope','Operadores'),('cal','Caldeiros'),('irr','Irrigantes'),('alm','Almoxarifes'),('agr','Agrônomos'),('nao','Não alocáveis')]
def cd04():
    fname='CD-04.dc.html'; E._reset_screen(fname)
    eqn=[e[1] for e in EQUIPES]; pes=pessoas()
    campos=([txt('nome','Nome'),sel('equipe','Equipe',eqn,**{'def':'Campo 1'}),
             dict(k='hab',l='Habilidades',t='multi',opts=HABILIDADES,req=True)]
            + [dat(k,l,req=False) for _,k,l in HABIL]
            + [sel('vinc','Vínculo',['CLT','Safrista','Diarista','Terceiro'],**{'def':'CLT'}),dat('adm','Admissão'),
               dat('ate','Disponível até',req=False,help='Fim do contrato de safrista ou diarista.'),
               sel('cal','Calendário de trabalho',['Da equipe']+CALS,**{'def':'Da equipe'},help='Mude só se a pessoa foge do calendário da equipe.'),
               num('custo','Custo-hora com encargos','R$/h',min=0,help='Salário e encargos por hora trabalhada; visível só para quem tem permissão de custos.'),
               sel('acesso','Acesso ao app',['Com login','Sem login','Acesso solicitado','Solicitar acesso ao app'],**{'def':'Sem login'}),
               sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})])
    # pessoa numa linha: nome e equipe · habilidades · vínculo · custo-hora · situação (alocável em O.S. ou o que falta)
    gp=grid([dict(k='nome',l='Pessoa · equipe',w=300),dict(k='habs',l='Habilidades',w=210),dict(k='vig',l='Vínculo',w=170),
             dict(k='custo',l='Custo-hora',t='num',a='r'),dict(k='est',l='Situação',w=300)],
        [R(pid,v) for pid,v in pes],gid='g_pes',total=False,frame=False,
        tools=qf_chips('g_pes')+filtro_sel('c4fun','Função')+prim('g_pes_new','Cadastrar pessoa'),
        edit=dict(m='form',title='Pessoa',newTitle='Cadastrar pessoa',
            sub='Marque o que a pessoa faz; a habilitação exigida aparece abaixo. Cadastrar não cria login. Inative em vez de excluir.',fields=campos))
    ge=grid([dict(k='nome',l='Equipe'),dict(k='lider',l='Líder'),dict(k='membros',l='Pessoas ativas',t='num',a='r'),dict(k='cal',l='Calendário',w=220)],
        [R(i,dict(nome=n,lider=l,cal=c)) for i,n,l,c in EQUIPES],gid='g_eq',dele=False,total=False,search=False,
        edit=dict(m='form',title='Equipe',newTitle='Cadastrar equipe',sub='Altere nome, líder e calendário; quem segue a equipe herda o calendário.',
            fields=[txt('nome','Nome da equipe'),sel('lider','Líder',[v['nome'] for _,v in pes]),sel('cal','Calendário',CALS,**{'def':'seg–sáb · 06–15h'})]))
    # um bloco com abas: Pessoas (tabela) | Equipes (cartões); cada aba com a sua ação
    acoes_form('g_eq'); cadx_css()
    p1=(barra(f'<span style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("c4_neq")}</span>',prim('g_eq_new','Cadastrar equipe'))+cartoes('c4_eqs','Equipes'))
    corpo=bloco_cad(abas('c4t',['Pessoas','Equipes'],'Cadastros de pessoas'),pane('c4t',0,faixa('c4_fx0')+gp)+pane('c4t',1,p1),'Pessoas e equipes')
    dados=dict(qf=QF,habil=[[a,k] for a,k,_ in HABIL],calda=CALDA,agro=AGRO)
    js({},ALOC_JS+'const C4='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
function c4hdia(c){ const m=/(\d{2})–(\d{2})h/.exec(c||''); if(m) return (Number(m[2])-Number(m[1]))+' h/dia'; const n=/(\d+)h$/.exec(c||''); return n?n[1]+' h/dia':''; }
function c4qf(k,V,A){ const h=ml(V.hab);
  if(k==='ope') return h.some(x=>x.indexOf('Operar')===0); if(k==='cal') return h.indexOf(C4.calda)>=0; if(k==='irr') return h.indexOf('Irrigar')>=0;
  if(k==='alm') return h.indexOf('Almoxarifado')>=0; if(k==='agr') return h.indexOf(C4.agro)>=0; if(k==='nao') return !A.ok&&!A.inat;
  if(k==='res') return (!A.ok&&!A.inat)||A.vence; return true; }
function c4eqcal(self){ const o={}; RW(self,'g_eq').forEach(e=>{ o[e.v.nome]=e.v.cal; }); return o; }
// situação da pessoa: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o estado do cabeçalho
function c4sit(V){ const A=alocavel(V);
  if(A.inat) return {t:'Inativa',p:[chipc('Inativa','gray')]};
  if(!A.ok) return {t:'Não alocável',p:[chipc('Não alocável em O.S.','red'),{k:'mut',t:A.m}],res:'nao'};
  if(A.vence){ const y=A.t.find(x=>x.s==='vence'); return {t:'Vence em 30 dias',p:sitX(y.x+' vence '+br(y.d),'yellow','Renovar'),res:'ven'}; }
  const ok=A.t.map(y=>y.x+' até '+br(y.d)); return {t:'Alocável',p:sitOk('Alocável'+(ok.length?' · '+ok.join(' · '):''))}; }
function c4acesso(V){ const ac=V.acesso||'Sem login'; return ac==='Com login'?'':(ac==='Acesso solicitado'?'Acesso solicitado · simulado':'Sem acesso ao app'); }
CAD_ACTS.g_eq=(self,r)=>[cadExcluir(self,'g_eq',r,'equipe',r.nd?'tem pessoas ativas; mude-as de equipe antes':'')];
function PREVALS(self,v){ cadActsIni(self); const ps=RW(self,'g_pes'); const eqc=c4eqcal(self); self._c4eq=self._c4eq||{}; self._c4pes=self._c4pes||{};
  ps.forEach(r=>{ const V=r.v; self._c4pes[r.id]=V.nome; const herd=!V.cal||V.cal==='Da equipe'; const ac=c4acesso(V);
    r.p.nome=[{k:'b',t:V.nome||''},{k:'mut',t:(V.equipe||'—')+(herd?'':' · calendário próprio: '+V.cal)}].concat(ac?[{k:'mut',t:ac}]:[]); r.s.nome=V.nome||'';
    r.p.habs=[{k:'txt',t:ml(V.hab).join(' · ')||'—'}]; r.s.habs=ml(V.hab).join(' · ');
    r.p.vig=[{k:'txt',t:V.vinc||'—'}].concat(V.ate?[{k:'mut',t:'até '+br(V.ate)}]:[]); r.s.vig=V.vinc||'';
    r.p.custo=[{k:'txt',t:isnum(V.custo)?'R$ '+nf(V.custo,2)+'/h':'—'}];
    const S=c4sit(V); r.p.est=S.p; r.s.est=S.t; });
  // filtro do bloco: estado (Todas · A resolver) e função (lista), que valem juntos
  const fun=cadSel(self,v,'c4fun',[{v:'',t:'Todas'}].concat(C4.qf.filter(([k])=>k!=='nao').map(([k,t])=>({v:k,t:t+' ('+ps.filter(r=>c4qf(k,r.v,alocavel(r.v))).length+')'}))));
  cadQf(self,v,'g_pes','c4qf',Object.assign([{k:'res',t:'A resolver',f:r=>!!c4sit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oz:true}],{todos:'Todas'}),
        {extra:fun?(r=>c4qf(fun,r.v,alocavel(r.v))):null});
  const eqs=RW(self,'g_eq');
  eqs.forEach(r=>{ self._c4eq[r.id]=r.v.nome; const n=ps.filter(p=>p.v.equipe===r.v.nome&&p.v.sit!=='Inativa').length; r.v.membros=n; r.nd=n?'tem pessoas':''; r.s.nome=r.v.nome||''; });
  // equipes em cartões: líder, pessoas ativas e jornada; calendário no rodapé; exceção (líder inativa, gente não alocável) no chip
  v.c4_neq=eqs.length+(eqs.length===1?' equipe':' equipes');
  cadCartoes(self,v,'c4_eqs','g_eq',eqs.map(r=>{ const V=r.v; const mem=ps.filter(p=>p.v.equipe===V.nome&&p.v.sit!=='Inativa'); const nao=mem.filter(p=>!alocavel(p.v).ok).length;
    const L=ps.find(p=>p.v.nome===V.lider); const linat=!!V.lider&&(!L||L.v.sit==='Inativa'); const hd=c4hdia(V.cal);
    return {id:r.id,nome:V.nome||'',chip:linat?{t:'Líder inativa',c:'yellow'}:(nao?{t:nao+(nao>1?' não alocáveis':' não alocável'),c:'red'}:null),
      sub:'Líder '+(V.lider||'—')+(linat?' · Inativa':''),
      nums:[{v:String(mem.length),u:'',l:mem.length===1?'Pessoa ativa':'Pessoas ativas'},{v:hd?hd.replace(' h/dia',''):'—',u:hd?'h/dia':'',l:'Jornada'}],
      rod:V.cal||'',verbo:linat?'Escolher líder ativo':'',sitT:'Em dia'}; }));
  const fe=(GR('g_eq').edit.fields||[]).find(x=>x.k==='lider'); if(fe) fe.opts=ps.filter(p=>p.v.sit!=='Inativa').map(p=>p.v.nome);
  const fq=(GR('g_pes').edit.fields||[]).find(x=>x.k==='equipe'); if(fq) fq.opts=eqs.map(e=>e.v.nome); }
function EXTRAVALS(self,v){ const ps=RW(self,'g_pes'); const eqc=c4eqcal(self);
  const naoL=ps.filter(r=>c4sit(r.v).res==='nao'), venL=ps.filter(r=>c4sit(r.v).res==='ven'); const nao=naoL.length, ven=venL.length;
  cadEstado(v,'c4e',[nao?nao+(nao>1?' não alocáveis':' não alocável'):'',ven?ven+' a renovar em 30 dias':''].filter(Boolean).join(' · ')||'Todos alocáveis',nao?'red':(ven?'yellow':'green'));
  const eqs=RW(self,'g_eq'); const eqLid=eqs.filter(e=>{ const L=ps.find(p=>p.v.nome===e.v.lider); return !!e.v.lider&&(!L||L.v.sit==='Inativa'); }).length;
  const eqNao=eqs.filter(e=>ps.some(p=>p.v.equipe===e.v.nome&&p.v.sit!=='Inativa'&&!alocavel(p.v).ok)).length;
  cadAbas(self,v,'c4t','c4aba',[{slug:'pessoas',n:ps.length,cor:nao?'red':(ven?'yellow':'')},{slug:'equipes',n:eqs.length,cor:eqNao?'red':(eqLid?'yellow':'')}]);
  cadQfPos(self,v,'g_pes','c4qf'); cadConta(self,v,'g_pes');
  if(self.state.c4fun){ v.g_pes_filtered=true; v.g_pes_clear=()=>{ g2set(self,'g_pes',{q:'',f:{}}); self.setState({c4qf:'',c4fun:''}); }; }
  const res=()=>self.setState({c4qf:'res',c4fun:''});
  cadFaixa(v,'c4_fx0',[nao?{n:nao,rot:nao>1?'não alocáveis em O.S.':'não alocável em O.S.',reg:naoL.map(r=>r.v.nome).join(', '),verbo:'Regularizar habilitação',cor:'red',
                            go:nao===1?()=>g2open(self,GR('g_pes'),naoL[0].id,null):res}:null,
                        ven?{n:ven,rot:ven>1?'habilitações vencem em 30 dias':'habilitação vence em 30 dias',reg:venL.map(r=>r.v.nome).join(', '),verbo:'Renovar',cor:'yellow',
                            go:ven===1?()=>g2open(self,GR('g_pes'),venL[0].id,null):res}:null],res);
  // formulário: validade só das habilitações exigidas; ajuda com a habilitação e o calendário; acesso ao app simulado
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
  // formulário da equipe: o líder gravado continua visível mesmo inativo, com aviso para escolher outro
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
      // renomear a pessoa atualiza o líder das equipes (como equipe → pessoas)
      const old=(self._c4pes||{})[r.id]; const es=g2clone(RW(self,'g_eq')); const ren=[];
      if(old&&old!==r.v.nome){ es.forEach(e=>{ if(e.v.lider===old){ e.v.lider=r.v.nome; ren.push(e.v.nome); } }); if(ren.length) g2set(self,'g_eq',{rows:es}); }
      const A=alocavel(r.v); const lid=es.filter(e=>e.v.lider===r.v.nome).map(e=>e.v.nome);
      self.setState({g2toast:ponto((isNew?'Cadastrado: ':'Salvo: ')+r.v.nome+' · '+(A.inat?'inativa':(A.ok?'alocável em O.S.':'não alocável em O.S. até resolver '+A.m))
        +(ped?' · pedido de acesso ao app enviado ao administrador (simulado)':'')
        +(A.inat&&lid.length?' · escolha outro líder para '+lista(lid):(ren.length?' · líder de '+lista(ren)+' atualizado':'')))}); }
    if(gid==='g_eq'){ const old=(self._c4eq||{})[r.id]; let n=0;
      if(old&&old!==r.v.nome){ const ps=g2clone(RW(self,'g_pes')); ps.forEach(p=>{ if(p.v.equipe===old){ p.v.equipe=r.v.nome; n++; } }); g2set(self,'g_pes',{rows:ps}); }
      self.setState({g2toast:(isNew?'Equipe criada: ':'Salvo: ')+r.v.nome+' · '+r.v.cal+' · '+c4hdia(r.v.cal)+(n?' · '+n+(n>1?' pessoas seguem':' pessoa segue')+' a equipe':'')+'.'}); } }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela ou os cartões da aba rolam
    shell37('CD-04','Pessoas e equipes',corpo,fname=fname,status=None,primary_html=None,search=False)
    estado_cab(fname,'Pessoas e equipes','c4e')
