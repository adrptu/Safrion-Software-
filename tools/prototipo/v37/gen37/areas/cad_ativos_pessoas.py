# -*- coding: utf-8 -*-
"""CD-03 Máquinas, instalações e setores · CD-04 Pessoas e equipes (módulo próprio; areas.cadastros.build() usa estes cd03()/cd04()).
CD-03 · a classe vem primeiro e abre só a capacidade dela (potência; barra + tanque; linhas × espaçamento; largura e carga; plataforma;
  vazão; kg/h; sacas). Custo por hora com fonte substitui o valor do ativo. A condição técnica é só leitura e vem da Manutenção
  (Trator T1 em manutenção pela OM-0233, com 'Ver ordens afetadas'). Bloco Conjuntos: máquina + implemento + operações, com largura
  herdada, condição derivada, substituto sugerido, operadores alocáveis (habilidades do CD-04) e rendimento do CD-02.
CD-04 · habilidades em múltipla escolha (a habilitação exigida aparece conforme a habilidade), várias habilitações com validade, vínculo
  e vigência, calendário herdado da equipe, custo-hora com encargos. Habilitação vencida ou pendente grava e marca 'Não alocável em O.S.'.
  Filtros rápidos por habilidade e 'Não alocáveis'; 'Solicitar acesso ao app' é simulado no formulário.
  Líder inativo continua visível no formulário da equipe, com aviso, e salvar pede um líder ativo; renomear a pessoa atualiza o líder.
Dados: dados_cad (lido e copiado; Paula passa a caldeira da OS-0424, como em alocacao.py) e dados2.CONJ (rendimentos)."""
import json, os
from engine import grid, esc, MUTED
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37
import dados2 as D2
import dados_cad as DC
from areas.cadastros import bloco, novo, mini, sel, num, txt, dat, cond, R, js, LOC_ATV

H=lambda s: '{{'+s+'}}'
for _f in ('CD-03.dc.html','CD-04.dc.html'): ui37.H_OVR.pop(_f,None)   # layout novo: a altura vem de HEIGHTS37

# ---------------- pessoas, habilidades e habilitações (fonte do CD-04; o CD-03 lê para os operadores do conjunto) ----------------
CALDA='Preparar calda (caldeiro)'; AGRO='Aprovar O.S. (agrônomo)'
HABILIDADES=['Operar trator','Operar pulverizador','Operar plantadeira','Operar colhedora',CALDA,'Irrigar','Almoxarifado',AGRO,'Conferir','Manutenção de máquinas']
HAB_EXIGE={'Operar trator':'NR-31','Operar pulverizador':'NR-31','Operar plantadeira':'NR-31','Operar colhedora':'NR-31',CALDA:'NR-31',
           'Irrigar':'NR-10','Manutenção de máquinas':'NR-12',AGRO:'CREA'}
HABIL=[('NR-31','v31','Validade da NR-31'),('NR-10','v10','Validade da NR-10'),('NR-12','v12','Validade da NR-12'),('CREA','vcrea','Validade do registro no CREA')]
_REN={'Preparar calda':CALDA,'Aprovar O.S. (agrônomo)':AGRO}
# ajustes sobre dados_cad: Paula é a caldeira das O.S. de pulverização (alocacao.py: 'Paula · caldeiro' na OS-0421/0424/0430);
# Rui é o almoxarife que entrega (os_campo.py, cenario.js); habilidade fora da lista (empilhadeira) sai.
_OVR={'p6':dict(funcao='Caldeiro',equipe='Campo 1',hab=[CALDA,'Conferir'],v31='2027-04-30'),
      'p7':dict(funcao='Almoxarife',hab=['Almoxarifado','Conferir']),
      'p10':dict(equipe='Campo 2')}
_ORDEM=['p1','p2','p3','p6','p10','p4','p5','p7','p8','p9']
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
// estado do cabeçalho calculado e clicável (filtra as exceções)
function stBtn(v,pre,t,c,go,tt){ const cc=G2C[c]||G2C.gray; v[pre+'_st']=t; v[pre+'_stgo']=go; v[pre+'_sttt']=tt;
  v[pre+'_stst']='display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;border:0;cursor:pointer;font-family:inherit;color:'+cc[0]+';background:'+cc[1]+';';
  v[pre+'_stdot']='width:6px;height:6px;border-radius:999px;background:'+cc[0]+';'; }
// filtro rápido da tela entra no "Limpar filtros" e nos chips da grade
function qfGrade(self,v,gid,skey,rot){ const q=self.state[skey]||''; if(!q) return; v[gid+'_filtered']=true;
  v[gid+'_fchips']=(v[gid+'_fchips']||[]).concat([{t:rot,rm:()=>self.setState({[skey]:''})}]);
  v[gid+'_clear']=()=>{ g2set(self,gid,{q:'',f:{}}); self.setState({[skey]:''}); }; }
// lista em português: "A", "A e B", "A, B e C"
function lista(a){ return a.length<2?(a[0]||''):a.slice(0,-1).join(', ')+' e '+a[a.length-1]; }
// frase termina com um só ponto (evita "O.S..")
function ponto(s){ return /\.$/.test(s)?s:s+'.'; }
// o select do formulário mostra sempre o valor gravado: vazio vira "Escolha…"; valor fora das opções (inativo, excluído) continua visível
function selFiel(F,suf){ if(!F||!F.open||!F.fields) return; F.fields.forEach(f=>{ if(!f.isSel) return; const val=String(f.v||'');
  if((f.opts||[]).some(o=>o.v===val)) return; f.opts=[{v:val,t:val?val+((suf||{})[f.fid]||''):'Escolha…'}].concat(f.opts||[]); }); }
const QCH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
function qchip(t,n,on,go){ return {t:t,n:String(n),on:String(!!on),go:go,st:QCH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')}; }
''')
def _status_clicavel(fname,pre,tt):
    """troca o chip estático do estado (shell37) por um botão com texto, cor e filtro calculados na tela."""
    p=os.path.join(E.P,fname); h=open(p).read(); old=ui37.chip(H(pre+'_st'),'yellow')
    new=(f'<button type="button" onClick="{H(pre+"_stgo")}" title="{H(pre+"_sttt")}" aria-label="{esc(tt)}" style="{H(pre+"_stst")}">'
         f'<span style="{H(pre+"_stdot")}"></span>{H(pre+"_st")}</button>')
    assert h.count(old)==1, 'estado do cabeçalho não encontrado em '+fname
    open(p,'w').write(h.replace(old,new))

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
    return ([sel('classe','Classe',[c for c,_ in CLS],newOnly=True,help='Abre só a capacidade desta classe; fica fixa depois do cadastro.',**{'def':'Trator'}),
             txt('nome','Nome',help='Ex.: Trator 05. Não pode repetir.'),txt('modelo','Modelo',req=False),
             dict(k='cond_t',l='Condição técnica',t='area',ro=True,help='Vem da Manutenção; não se altera no cadastro.',**{'def':'Apto'})]
            + cap
            + [num('custo_h','Custo por hora','R$/h',min=0,req=False,help='Combustível, manutenção e depreciação; o operador entra em Pessoas. O rendimento usa este valor.'),
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
    g=grid([dict(k='nome',l='Máquina ou instalação',w=190),dict(k='classe',l='Classe e capacidade',w=180),dict(k='cond',l='Condição técnica',w=170),
            dict(k='calib',l='Calibração',w=170),dict(k='custo_h',l='Custo por hora',t='num',a='r',w=120),dict(k='cj',l='Conjuntos',w=180)],
        _linhas_ativo(),gid='g_atv',total=False,
        edit=dict(m='form',title='Máquina',newTitle='Cadastrar máquina ou instalação',
            sub=SUB_EDIT,fields=_campos_ativo()))
    rend={c['id']:c['rend'] for c in D2.CONJ}
    maqs=[a['nome'] for a in DC.ATIVOS if a['classe'] not in IMPL]; imps=[a['nome'] for a in DC.ATIVOS if a['classe'] in IMPL]
    cj=grid([dict(k='nome',l='Conjunto',w=210),dict(k='ops',l='Operações',w=130),dict(k='larg',l='Largura',t='num',a='r',u='m'),
             dict(k='cond',l='Condição',w=210),dict(k='oper',l='Operadores alocáveis',w=180),dict(k='rend',l='Rendimento',t='num',a='r')],
        [R(k,dict(maq=m,impl=i or SEM_IMPL,ops=op,rend=rend.get(rid,''))) for k,m,i,op,rid in DC.CONJUNTOS],
        gid='g_cj',dele=True,total=False,search=False,
        edit=dict(m='form',title='Conjunto',newTitle='Montar conjunto',sub='Escolha a máquina, o implemento e as operações; a largura vem do implemento.',
            fields=[sel('maq','Máquina',maqs),sel('impl','Implemento',[SEM_IMPL]+imps,**{'def':SEM_IMPL}),
                    dict(k='ops',l='Operações',t='multi',opts=OPS,req=True),
                    dict(k='larg_c',l='Largura de trabalho',ro=True,live=True,u='m',help='Herdada do implemento (ou da plataforma da colhedora).'),
                    dict(k='pot_c',l='Potência',ro=True,live=True,help='O trator precisa ter ao menos a potência que o implemento exige.')]))
    corpo=(bloco('Máquinas e instalações','Clique na linha para editar capacidade, custo por hora e calibração; a condição técnica vem da Manutenção.',g)
           + bloco('Conjuntos','Monte máquina + implemento por operação; a O.S. e o rendimento usam o conjunto.',cj,acao=mini('g_cj_new','Montar conjunto')))
    dados=dict(cod=COD,impl=IMPL,calib=CALIB_CLS,sem=SEM_IMPL,ophab=OPHAB,subnew=SUB_NEW,
               cond={k:dict(t=c['t'],m=c['om']+' · '+c['det'],ordens=c['ordens'],om=c['om']) for k,c in DC.CONDICAO.items()},
               pes=[dict(v,id=pid) for pid,v in pessoas()])
    js({},ALOC_JS+'const C3='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
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
function c3cond(r){ const V=r.v; if(V.sit==='Inativo') return {t:'Inativo',c:'gray',ok:false,curto:'inativo'}; const x=C3.cond[r.id];
  if(x) return {t:x.t,c:'red',ok:false,m:x.m,x:x,curto:x.t.toLowerCase()}; return {t:'Apto',c:'green',ok:true}; }
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
function PREVALS(self,v){ const atv=RW(self,'g_atv'); const qf=self.state.c3qf||''; self._c3nomes=self._c3nomes||{};
  const usos={}; RW(self,'g_cj').forEach(r=>{ [r.v.maq,r.v.impl].forEach(n=>{ if(n&&n!==C3.sem) (usos[n]=usos[n]||[]).push(r); }); });
  atv.forEach(r=>{ const V=r.v; self._c3nomes[r.id]=V.nome; const C=c3cond(r), K=c3calib(V);
    r.p.nome=[{k:'b',t:V.nome||''}].concat(V.modelo?[{k:'mut',t:V.modelo}]:[]); r.s.nome=(V.nome||'')+' '+(V.modelo||'');
    r.p.classe=[{k:'tag',t:V.classe||'—'},{k:'br'},{k:'txt',t:c3cap(V)}]; r.s.classe=V.classe||'';
    r.p.cond=[chipc(C.t,C.c)].concat(C.m?[{k:'mut',t:C.m},{k:'link',t:'Ver ordens afetadas',h:'OS.dc.html'}]:[]); r.s.cond=C.t;
    V.cond_t=C.m?C.t+' · '+C.m:C.t; r.o=C.x?[{t:'Ver ordens afetadas · '+C.x.ordens.join(' e '),h:'OS.dc.html'},{t:'Abrir '+C.x.om+' na Manutenção',h:'MA-04det.dc.html'}]:null;
    r.p.calib=K.p; r.s.calib=K.s;
    r.p.custo_h=isnum(V.custo_h)&&String(V.custo_h)!==''?[{k:'txt',t:'R$ '+nf(V.custo_h,2)+'/h'},{k:'br'},V.custo_f==='Premissa a validar'?chipc('Premissa a validar','yellow'):{k:'mut',t:V.custo_f||''}]:[{k:'mut',t:'—'}];
    // cada link identifica o conjunto pelo outro membro (implemento ou trator) + operações; um por linha
    const us=(usos[V.nome]||[]).map(c=>{ const o=c.v.maq===V.nome?(c.v.impl&&c.v.impl!==C3.sem?c.v.impl:''):c.v.maq; return {id:c.id,t:(o?o+' · ':'')+(ml(c.v.ops).join(', ')||'conjunto')}; });
    r.p.cj=us.length?[].concat(...us.map((c,i)=>(i?[{k:'br'}]:[]).concat([{k:'act',t:c.t,fn:'c3cj:'+c.id,lk:true}]))):[{k:'mut',t:'—'}]; r.s.cj=us.map(c=>c.t).join(' · ');
    const exc=V.sit!=='Inativo'&&(C.t==='Em manutenção'||K.bad); if(qf&&!exc) r.sh='c3oculto'; else delete r.sh; });
  c3opts('g_cj','maq',atv.filter(r=>C3.impl.indexOf(r.v.classe)<0).map(r=>r.v.nome));
  c3opts('g_cj','impl',[C3.sem].concat(atv.filter(r=>C3.impl.indexOf(r.v.classe)>=0).map(r=>r.v.nome)));
  RW(self,'g_cj').forEach(r=>{ const V=r.v; const X=c3conj(self,V);
    r.p.nome=[{k:'b',t:(V.maq||'')+(X.I?' + '+V.impl:'')}]; r.s.nome=(V.maq||'')+(X.I?' + '+V.impl:'');
    const pot=X.M&&X.M.v.classe==='Trator'?c3n(X.M.v,'pot'):null, q=X.I?c3n(X.I.v,'preq'):null;
    if(pot!==null) r.p.nome.push({k:'mut',t:nfa(pot)+' cv'+(q!==null?' · exige '+nfa(q)+' cv':'')});
    r.p.ops=[{k:'txt',t:ml(V.ops).join(' · ')}]; r.s.ops=ml(V.ops).join(' · ');
    const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null); V.larg=lg===null?'':lg; r.p.larg=[lg===null?{k:'mut',t:'—'}:{k:'txt',t:nfa(lg)+' m'}];
    if(X.bad.length){ r.p.cond=[chipc('Indisponível','red'),{k:'mut',t:X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(' · ')+(X.sub?' · substituto: '+X.sub.v.nome+' ('+nfa(c3n(X.sub.v,'pot'))+' cv)':'')}]; r.s.cond='Indisponível'; }
    else if(X.cal.length){ r.p.cond=[chipc('Calibrar antes de usar','yellow'),{k:'mut',t:X.cal.map(x=>x.v.nome+' · '+c3calib(x.v).s.toLowerCase()).join(' · ')}]; r.s.cond='Calibrar antes de usar'; }
    else { r.p.cond=[chipc('Disponível','green')]; r.s.cond='Disponível'; }
    const O=c3oper(V.ops); r.p.oper=O.p; r.s.oper=O.s;
    r.p.rend=isnum(V.rend)&&String(V.rend)!==''?[{k:'link',t:nf(V.rend,2)+' ha/h ›',h:'CD-02.dc.html'}]:[{k:'mut',t:'sem rendimento'},{k:'link',t:'Cadastrar ›',h:'CD-02.dc.html'}];
    r.nd=isnum(V.rend)&&String(V.rend)!==''?'tem rendimento':''; }); }
function EXTRAVALS(self,v){ protege(self,v,'g_cj');
  const atv=RW(self,'g_atv'); const man=atv.filter(r=>r.v.sit!=='Inativo'&&c3cond(r).t==='Em manutenção').length; const cal=atv.filter(r=>r.v.sit!=='Inativo'&&c3calib(r.v).bad).length;
  stBtn(v,'c3',[man?man+(man>1?' máquinas em manutenção':' máquina em manutenção'):'',cal?cal+(cal>1?' calibrações a resolver':' calibração a resolver'):''].filter(Boolean).join(' · ')||'Máquinas aptas e calibradas',
        man?'red':(cal?'yellow':'green'),()=>self.setState({c3qf:self.state.c3qf?'':'exc'}),'Filtrar máquinas em manutenção ou com calibração a resolver');
  qfGrade(self,v,'g_atv','c3qf','Em manutenção ou calibração a resolver');
  v.c3cj=(id)=>g2open(self,GR('g_cj'),id,null);
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
    if(fm.rid&&CONT0[fm.rid]!==undefined&&!isNaN(c)&&c<CONT0[fm.rid]) e['cont_'+cd]='A última leitura foi '+nf(CONT0[fm.rid])+' h. Se o medidor foi trocado, registre a troca na Manutenção.';
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
    HEIGHTS37[fname]=1880
    shell37('CD-03','Máquinas, instalações e setores',corpo,fname=fname,
            subtitle='Cadastre máquinas e instalações pela classe, com capacidade, custo por hora e calibração; monte os conjuntos que as O.S. usam.',
            status=(H('c3_st'),'yellow'),primary_html=novo('g_atv','Cadastrar máquina ou instalação'),search=False)
    _status_clicavel(fname,'c3','Filtrar máquinas em manutenção ou com calibração a resolver')

# ================= CD-04 · Pessoas e equipes =================
QF=[('ope','Operadores'),('cal','Caldeiros'),('irr','Irrigantes'),('alm','Almoxarifes'),('agr','Agrônomos'),('nao','Não alocáveis')]
def cd04():
    fname='CD-04.dc.html'; E._reset_screen(fname)
    eqn=[e[1] for e in EQUIPES]; pes=pessoas()
    chips=(f'<sc-for list="{H("c4_qf")}" as="qc" hint-placeholder-count="7"><button type="button" aria-pressed="{H("qc.on")}" onClick="{H("qc.go")}" style="{H("qc.st")}">'
           f'{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button></sc-for>')
    campos=([txt('nome','Nome'),sel('equipe','Equipe',eqn,**{'def':'Campo 1'}),
             dict(k='hab',l='Habilidades',t='multi',opts=HABILIDADES,req=True)]
            + [dat(k,l,req=False) for _,k,l in HABIL]
            + [sel('vinc','Vínculo',['CLT','Safrista','Diarista','Terceiro'],**{'def':'CLT'}),dat('adm','Admissão'),
               dat('ate','Disponível até',req=False,help='Fim do contrato de safrista ou diarista.'),
               sel('cal','Calendário de trabalho',['Da equipe']+CALS,**{'def':'Da equipe'},help='Mude só se a pessoa foge do calendário da equipe.'),
               num('custo','Custo-hora com encargos','R$/h',min=0,help='Salário e encargos por hora trabalhada; visível só para quem tem permissão de custos.'),
               sel('acesso','Acesso ao app',['Com login','Sem login','Acesso solicitado','Solicitar acesso ao app'],**{'def':'Sem login'}),
               sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})])
    gp=grid([dict(k='nome',l='Pessoa',w=250),dict(k='equipe',l='Equipe e calendário',w=170),dict(k='hab',l='Habilitações',w=250),dict(k='vig',l='Vínculo e vigência',w=150),
             dict(k='custo',l='Custo-hora com encargos',t='num',a='r'),dict(k='acesso',l='Acesso ao app',w=150)],
        [R(pid,v) for pid,v in pes],gid='g_pes',total=False,tools=chips,
        edit=dict(m='form',title='Pessoa',newTitle='Cadastrar pessoa',
            sub='Marque o que a pessoa faz; a habilitação exigida aparece abaixo. Cadastrar não cria login. Inative em vez de excluir.',fields=campos))
    ge=grid([dict(k='nome',l='Equipe'),dict(k='lider',l='Líder'),dict(k='membros',l='Pessoas ativas',t='num',a='r'),dict(k='cal',l='Calendário',w=220)],
        [R(i,dict(nome=n,lider=l,cal=c)) for i,n,l,c in EQUIPES],gid='g_eq',dele=True,total=False,search=False,
        edit=dict(m='form',title='Equipe',newTitle='Nova equipe',sub='Altere nome, líder e calendário; quem segue a equipe herda o calendário.',
            fields=[txt('nome','Nome da equipe'),sel('lider','Líder',[v['nome'] for _,v in pes]),sel('cal','Calendário',CALS,**{'def':'seg–sáb · 06–15h'})]))
    corpo=(bloco('Pessoas','Clique na linha para editar habilidades, habilitações e vigência.',gp)
           + bloco('Equipes','Defina líder e calendário; a pessoa herda o calendário da equipe.',ge,acao=mini('g_eq_new','Nova equipe')))
    dados=dict(qf=QF,habil=[[a,k] for a,k,_ in HABIL],calda=CALDA,agro=AGRO)
    js({},ALOC_JS+'const C4='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
function c4hdia(c){ const m=/(\d{2})–(\d{2})h/.exec(c||''); if(m) return (Number(m[2])-Number(m[1]))+' h/dia'; const n=/(\d+)h$/.exec(c||''); return n?n[1]+' h/dia':''; }
function c4qf(k,V,A){ const h=ml(V.hab);
  if(k==='ope') return h.some(x=>x.indexOf('Operar')===0); if(k==='cal') return h.indexOf(C4.calda)>=0; if(k==='irr') return h.indexOf('Irrigar')>=0;
  if(k==='alm') return h.indexOf('Almoxarifado')>=0; if(k==='agr') return h.indexOf(C4.agro)>=0; if(k==='nao') return !A.ok&&!A.inat;
  if(k==='res') return (!A.ok&&!A.inat)||A.vence; return true; }
function c4eqcal(self){ const o={}; RW(self,'g_eq').forEach(e=>{ o[e.v.nome]=e.v.cal; }); return o; }
function PREVALS(self,v){ const ps=RW(self,'g_pes'); const eqc=c4eqcal(self); const qf=self.state.c4qf||''; self._c4eq=self._c4eq||{}; self._c4pes=self._c4pes||{};
  ps.forEach(r=>{ const V=r.v; const A=alocavel(V); self._c4pes[r.id]=V.nome;
    r.p.nome=[{k:'b',t:V.nome||''},{k:'mut',t:ml(V.hab).join(' · ')}].concat(V.sit==='Inativa'?[chipc('Inativa','gray')]:[]); r.s.nome=V.nome||'';
    if(A.inat){ r.p.hab=[{k:'mut',t:'inativa'}]; r.s.hab='Inativa'; }
    else if(!A.ok){ r.p.hab=[chipc('Não alocável em O.S.','red'),{k:'mut',t:A.m}]; r.s.hab='Não alocável'; }
    else if(!A.t.length){ r.p.hab=[{k:'mut',t:'não exige'}]; r.s.hab='Não exige'; }
    else { r.p.hab=A.t.map(y=>chipc(y.x+(y.s==='vence'?' vence ':' até ')+br(y.d),y.s==='vence'?'yellow':'green')); r.s.hab=A.vence?'Vence em 30 dias':'Válida'; }
    r.p.vig=[{k:'txt',t:V.vinc||'—'},{k:'mut',t:V.ate?'até '+br(V.ate):(V.adm?'desde '+br(V.adm):'')}]; r.s.vig=V.vinc||'';
    const herd=!V.cal||V.cal==='Da equipe'; r.p.equipe=[{k:'txt',t:V.equipe||'—'}].concat(herd?[]:[{k:'br'},{k:'mut',t:'calendário próprio: '+V.cal}]); r.s.equipe=V.equipe||'';
    r.p.custo=[{k:'txt',t:isnum(V.custo)?'R$ '+nf(V.custo,2)+'/h':'—'}];
    const ac=V.acesso||'Sem login'; r.p.acesso=ac==='Com login'?[chipc('Com login','green')]:(ac==='Acesso solicitado'?[chipc('Acesso solicitado','yellow'),{k:'mut',t:'simulado'}]:[chipc('Sem login','yellow')]); r.s.acesso=ac;
    if(qf&&!c4qf(qf,V,A)) r.sh='c4oculto'; else delete r.sh; });
  RW(self,'g_eq').forEach(r=>{ self._c4eq[r.id]=r.v.nome; const n=ps.filter(p=>p.v.equipe===r.v.nome&&p.v.sit!=='Inativa').length; r.v.membros=n; r.nd=n?'tem pessoas':'';
    r.p.nome=[{k:'b',t:r.v.nome||''}]; r.s.nome=r.v.nome||'';
    const L=ps.find(p=>p.v.nome===r.v.lider); r.p.lider=[{k:'txt',t:r.v.lider||'—'}].concat(L&&L.v.sit==='Inativa'?[{k:'br'},chipc('Inativa','gray')]:[]); r.s.lider=r.v.lider||'';
    r.p.cal=[{k:'txt',t:r.v.cal||'—'},{k:'mut',t:c4hdia(r.v.cal)}]; r.s.cal=r.v.cal||''; });
  const fe=(GR('g_eq').edit.fields||[]).find(x=>x.k==='lider'); if(fe) fe.opts=ps.filter(p=>p.v.sit!=='Inativa').map(p=>p.v.nome);
  const fq=(GR('g_pes').edit.fields||[]).find(x=>x.k==='equipe'); if(fq) fq.opts=RW(self,'g_eq').map(e=>e.v.nome); }
function EXTRAVALS(self,v){ protege(self,v,'g_eq'); const ps=RW(self,'g_pes'); const eqc=c4eqcal(self); const qf=self.state.c4qf||'';
  const all=ps.map(r=>({V:r.v,A:alocavel(r.v)}));
  v.c4_qf=[qchip('Todas',all.length,!qf,()=>self.setState({c4qf:''}))].concat(C4.qf.map(([k,t])=>qchip(t,all.filter(x=>c4qf(k,x.V,x.A)).length,qf===k,()=>self.setState({c4qf:qf===k?'':k}))));
  const nao=all.filter(x=>!x.A.ok&&!x.A.inat).length, ven=all.filter(x=>x.A.ok&&x.A.vence).length;
  stBtn(v,'c4',[nao?nao+(nao>1?' não alocáveis':' não alocável'):'',ven?ven+' a renovar em 30 dias':''].filter(Boolean).join(' · ')||'Todos alocáveis',
        nao?'red':(ven?'yellow':'green'),()=>self.setState({c4qf:qf==='res'?'':'res'}),'Filtrar quem precisa de ação');
  if(qf==='res') qfGrade(self,v,'g_pes','c4qf','Habilitação a resolver');
  else if(qf){ v.g_pes_filtered=true; v.g_pes_clear=()=>{ g2set(self,'g_pes',{q:'',f:{}}); self.setState({c4qf:''}); }; }
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
    HEIGHTS37[fname]=1100
    shell37('CD-04','Pessoas e equipes',corpo,fname=fname,
            subtitle='Cadastre quem faz o quê na fazenda; habilitação vencida ou pendente grava, mas tira a pessoa da alocação das O.S.',
            status=(H('c4_st'),'yellow'),primary_html=novo('g_pes','Cadastrar pessoa'),search=False)
    _status_clicavel(fname,'c4','Filtrar quem precisa de ação')
