# -*- coding: utf-8 -*-
"""CD-03 Máquinas, instalações e setores · CD-04 Pessoas e equipes (módulo próprio; areas.cadastros.build() usa estes cd03()/cd04()).
CD-03 · a classe vem primeiro e abre só a capacidade dela (potência; barra + tanque; linhas × espaçamento; largura e carga; plataforma;
  vazão; kg/h; sacas). Custo por hora com fonte substitui o valor do ativo. A condição técnica é só leitura e vem da Manutenção
  (Trator T1 em manutenção pela OM-0233, com 'Ver ordens afetadas'). Aba Conjuntos (cartões): máquina + implemento + operações, com largura
  herdada, condição derivada, substituto sugerido, operadores alocáveis (habilidades do CD-04) e rendimento do CD-02.
CD-04 · habilidades em múltipla escolha (a habilitação exigida aparece conforme a habilidade), várias habilitações com validade, vínculo
  e vigência, calendário herdado da equipe, custo-hora com encargos. Habilitação vencida ou pendente grava e marca 'Não alocável em O.S.'.
  Filtro do bloco: Todas · A resolver (estado) e Função (lista: operadores, caldeiros, irrigantes…). Acesso ao app: só leitura do estado de
  Configurações (CONF-01, CONF-D05), com o link para gerenciar em Configurações › Usuários e alçadas.
  Layout de 01/10/2026: abas Pessoas | Equipes (cartões) e Máquinas e instalações | Conjuntos (cartões), cada uma com a sua ação.
  Líder inativo continua visível no formulário da equipe, com aviso, e salvar pede um líder ativo; renomear a pessoa atualiza o líder.
Dados: dados_cad (lido e copiado; Paula passa a caldeira da OS-0424, como em alocacao.py) e dados2.CONJ (rendimentos)."""
import json
from engine import grid, MUTED
import engine as E
import ficha_pivo as FP   # ficha do pivô no detalhe do equipamento de irrigação (09/10/2026)
import ui37
from ui37 import shell37, HEIGHTS37
import dados2 as D2
import dados_cad as DC
from areas.cadastros import sel, num, txt, dat, cond, R, js, LOC_ATV
from areas.cadastros import (abas, pane, prim_cab, QF_CAD, filtro_sel, bloco_cad, estado_cab, acoes_form)

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
_ORDEM=['p1','p11','p2','p3','p6','p10','p4','p5','p7','p8','p14','p9','p12','p13','p15']   # p11 Caio (PCP, Agronomia): CONF-D04 · p14 Otávio (PCM; p11 na v56, renumerado na v57 porque a CONF já usava p11) · p12 Igor e p13 Marta: equipe e8 Beneficiamento e qualidade (BEN-1)
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
# capacidade principal por classe (rótulo, unidade), a mesma de c3capn(): a coluna só aparece quando o filtro de Classe deixa uma grandeza
CAPCOL={'Trator':('Potência','cv'),'Pulverizador':('Tanque útil','L'),'Plantadeira':('Linhas','linhas'),'Distribuidor':('Carga','kg'),
        'Irrigação':('Vazão','m³/h'),'Armazenagem':('Capacidade','sc de 60 kg'),'Tratamento de sementes':('Capacidade','kg/h'),'Beneficiamento':('Capacidade','kg/h')}
# TABR-CTX-01 (revisão do Codex, 10/10/2026): a coluna de capacidade muda de grandeza com o filtro (Classe no CD-03, Tanque/Silo no CD-06);
# o filtro, a ordenação e o menu de filtro dela não podem sobrar de outra grandeza. Uma função para as duas telas (o CD-06 importa daqui).
# Revisão do TABR-CTX-01 (10/10/2026): a coluna Fazenda da Irrigação (só com "Todas" no topo) usa a mesma função (TABR-CTX-02); e a coluna
# presa do g2lib é refeita quando a coluna entra ou sai (a 390 px a última coluna caía para a linha de baixo).
CAPCOL_JS=r'''
// coluna que muda de grandeza com o filtro (tup = rótulo|unidade; '' sem coluna): filtro, ordenação e menu de filtro dela valem para uma tupla.
// Mudou a tupla ou a coluna saiu: só eles saem (busca, outros filtros, menu de outra coluna e rascunho do cadastro ficam); mesma tupla, ficam.
// Roda no PREVALS, antes de g2vals ler o estado (o mesmo desenho do talhão fora do recorte na O.S.). Serve também à coluna que só entra e sai
// (Fazenda da Irrigação: tup = 'Fazenda' ou '').
function capColDeps(self,gid,k,tup){ const m=self.__capTup=self.__capTup||{}; const ant=m[gid]; m[gid]=tup;
  // a coluna entrou ou saiu: a 1ª coluna presa do g2lib (data-c0, --g2cols) foi feita com o nº anterior de colunas e o motor só a refaz quando a
  // largura muda (a 390 px a última coluna caía para a linha de baixo). Desfeita aqui, antes do novo desenho, o motor a refaz com o nº novo de
  // cabeçalhos (o desenho muda a lista de cabeçalhos e o observador do g2lib roda). Só quando o nº de colunas muda: a troca de grandeza não refaz.
  if(ant!==undefined&&!ant!==!tup&&typeof document!=='undefined') document.querySelectorAll('.g2rola[data-c0]').forEach(r=>{ r.removeAttribute('data-c0'); r.style.removeProperty('--g2cols'); });
  if(tup&&(ant===undefined||ant===tup)) return;
  const st=g2st(self,gid), f=st.f||{}, p={}; if(k in f){ p.f=Object.assign({},f); delete p.f[k]; } if(st.so&&st.so.k===k) p.so=null; if(st.fmc===k) Object.assign(p,{fmc:null,fmd:null,fmq:''});
  if(!Object.keys(p).length) return; const all=Object.assign({},self.state.g2||{}); all[gid]=Object.assign({},st,p); self.state.g2=all;
  // foco: o × que a pessoa usou (ex.: Classe) pode sumir junto com o chip da capacidade; sem foco, ele vai ao chip vizinho ou à busca da grade
  if(!p.f||typeof document==='undefined') return; const a=document.activeElement, cx=a&&a.closest?a.closest('.g2caixa'):null;
  if(!cx||a.getAttribute('aria-label')!=='Remover filtro') return;
  /* TABR-CTX-02: só quando o × veio do teclado (:focus-visible). No toque e no mouse o foco não é conduzido, como nos outros chips do g2lib:
     levá-lo ao campo de busca abriria o teclado do celular sem a pessoa pedir */
  let kb=false; try{ kb=a.matches(':focus-visible'); }catch(e){} if(!kb) return;
  const RF='button[aria-label="Remover filtro"]', i=[...cx.querySelectorAll(RF)].indexOf(a);
  setTimeout(()=>{ const ae=document.activeElement; if(ae&&ae!==document.body) return; const xs=[...cx.querySelectorAll(RF)];
    const b=xs[Math.min(i,xs.length-1)]||cx.querySelector('input[aria-label="Buscar nesta tabela"]'); if(b) b.focus(); },0); }
'''
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
             dict(k='cond_t',l='Condição técnica',t='area',ro=True,help='Vem da Manutenção (condição única); não se altera no cadastro.',**{'def':'Apto'})]
            # 16/10/2026: "Responsável técnico" (só leitura, da Manutenção) saiu do cadastro: não muda decisão aqui; segue na Manutenção
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
    # uma variável por coluna (TABELAS-FOCO, 04/10/2026): classe, "Custo R$/h" (05/10/2026), conjuntos e próxima calibração em colunas próprias.
    # Revisão TABR (09/10): a Situação logo depois da máquina (A1); modelo, largura de trabalho, espaçamento e plataforma no painel. A capacidade
    # principal muda de grandeza com a classe (potência em cv, tanque em L, vazão em m³/h…), então não fica numa coluna só (A4: ordenava cv
    # com L): a coluna entra quando o filtro de Classe deixa uma só grandeza, com o rótulo e a unidade dela, e ordena pelo número
    g=grid([dict(k='nome',l='Máquina ou instalação',w=260),dict(k='est',l='Situação',w=230),dict(k='classe',l='Classe',w=150),
            dict(k='custo_h',l='R$/h',t='num',a='r',d=2),dict(k='ncj',l='Conjuntos',t='num',a='r'),dict(k='calv',l='Próxima calibração',t='date')],
        _linhas_ativo(),gid='g_atv',total=False,qf=QF_CAD,
        edit=dict(m='form',title='Máquina',newTitle='Cadastrar máquina ou instalação',
            sub=SUB_EDIT,fields=_campos_ativo()))
    rend={c['id']:c['rend'] for c in D2.CONJ}
    maqs=[a['nome'] for a in DC.ATIVOS if a['classe'] not in IMPL]; imps=[a['nome'] for a in DC.ATIVOS if a['classe'] in IMPL]
    # Conjuntos (16/10/2026): eram só cartões próprios; agora a grade do motor com Tabela | Cartões (VIS-05), com o que o cartão mostrava em
    # colunas (situação com o próximo passo, operações, largura, rendimento, potência e operadores alocáveis)
    cj=grid([dict(k='nome',l='Conjunto',w=330),dict(k='est',l='Situação',w=200),dict(k='ops',l='Operações',w=180),dict(k='larg',l='Largura',t='num',a='r',un='m'),
             dict(k='rend',l='Rendimento',t='num',a='r',un='ha/h',d=2),dict(k='pot',l='Potência',t='num',a='r',un='cv'),dict(k='oper',l='Operadores alocáveis',w=180)],
        [R(k,dict(maq=m,impl=i or SEM_IMPL,ops=op,rend=rend.get(rid,''))) for k,m,i,op,rid in DC.CONJUNTOS],
        gid='g_cj',dele=False,total=False,qf=QF_CAD,cartoes=True,
        edit=dict(m='form',title='Conjunto',newTitle='Montar conjunto',sub='Escolha a máquina, o implemento e as operações; a largura vem do implemento.',
            fields=[sel('maq','Máquina',maqs),sel('impl','Implemento',[SEM_IMPL]+imps,**{'def':SEM_IMPL}),
                    dict(k='ops',l='Operações',t='multi',opts=OPS,req=True),
                    dict(k='larg_c',l='Largura de trabalho',ro=True,live=True,u='m',help='Herdada do implemento (ou da plataforma da colhedora).'),
                    dict(k='pot_c',l='Potência',ro=True,live=True,help='O trator precisa ter ao menos a potência que o implemento exige.')]))
    # um bloco com abas: Máquinas e instalações | Conjuntos, as duas na grade do motor; a primária do cabeçalho segue a aba (BOT-01/03)
    acoes_form('g_atv'); acoes_form('g_cj')
    corpo=bloco_cad(abas('c3t',['Máquinas e instalações','Conjuntos'],'Cadastros de máquinas'),pane('c3t',0,g)+pane('c3t',1,cj),'Máquinas, instalações e setores')
    dados=dict(cod=COD,impl=IMPL,calib=CALIB_CLS,sem=SEM_IMPL,ophab=OPHAB,subnew=SUB_NEW,capcol=CAPCOL,
               cond={k:dict(t=c['t'],m=c['om']+' · '+c['det'],ordens=c['ordens'],om=c['om']) for k,c in DC.CONDICAO.items()},
               pes=[dict(v,id=pid) for pid,v in pessoas()])
    EXTRA_FP=FP.painel()   # gaveta "Ficha do pivô" (o mesmo componente do IR-01)
    import cenario   # PCM simplificado S3: condição, responsável técnico e leitura do cenário único (c.man)
    js({},cenario.js_prefixo()+ALOC_JS+CAPCOL_JS+FP.store_js()+FP.js('CD')+'const C3='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
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
// capacidade principal da classe (a largura de trabalho tem coluna própria): número para ordenar e texto com a unidade
function c3capn(V){ const n=k=>c3n(V,k), f=(x,u)=>x===null?null:{n:x,t:nfa(x)+' '+u};
  switch(V.classe){ case 'Trator': return f(n('pot'),'cv'); case 'Pulverizador': return f(n('tanque'),'L'); case 'Plantadeira': return f(n('linhas'),'linhas');
    case 'Distribuidor': return f(n('carga'),'kg'); case 'Irrigação': return f(n('vazao'),'m³/h'); case 'Armazenagem': return f(n('capsc'),'sc de 60 kg');
    case 'Tratamento de sementes': case 'Beneficiamento': return f(n('kgh'),'kg/h'); default: return null; } }
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
  if(d<0) return {p:[chipc('Vencida em '+br(venc),'red')],s:'Vencida',bad:true,venc:venc};
  if(d<=15) return {p:[chipc('Vence '+br(venc),'yellow')],s:'Vence',bad:false,venc:venc};
  return {p:[chipc('Em dia até '+br(venc),'green')],s:'Em dia',bad:false,venc:venc}; }
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
  // o motivo e o retorno previsto (antes na faixa de atenção, 16/10/2026) ficam na dica do selo, na própria linha (TAB-06)
  if(C.t==='Bloqueado') return {t:'Bloqueado',p:[Object.assign(chipc('Bloqueado','red'),{dica:C.m||''})].concat(sitX('Bloqueado','red','Ver ordens afetadas','OS.dc.html').slice(1)),res:'man'};
  if(K.s==='Vencida') return {t:'Calibração vencida',p:sitX('Calibração vencida','red','Registrar calibração'),res:'cal'};
  if(K.s==='Aferir') return {t:'Sem aferição',p:sitX('Sem aferição','yellow','Registrar aferição'),res:'cal'};
  // calibração que vence em 15 dias: o chip diz isso (a cor da data não é o único sinal, revisão TABR A10); continua apta, fora do "A resolver"
  if(K.s==='Vence') return {t:'Calibração a vencer',p:sitX('Calibração a vencer','yellow','Registrar calibração')};
  return {t:'Apta',p:sitOk('Apta')}; }
// coluna da capacidade: só com o filtro de Classe numa grandeza (rótulo e unidade da classe); sem isso a grade não mistura grandezas
function c3capCol(self){ const sp=GR('g_atv'); if(!sp.colsAll) sp.colsAll=sp.cols.slice(); const fc=((g2st(self,'g_atv').f||{}).classe)||[];
  const ks=[...new Set(fc.map(c=>C3.capcol[c]?C3.capcol[c].join('|'):'').filter(Boolean))];
  const ok=fc.length&&fc.every(c=>C3.capcol[c])&&ks.length===1; const cc=ok?{k:'capn',l:C3.capcol[fc[0]][0],t:'num',a:'r',un:C3.capcol[fc[0]][1],w:140}:null;
  capColDeps(self,'g_atv','capn',cc?cc.l+'|'+cc.un:'');   // TABR-CTX-01: Potência cv → Vazão m³/h (ou sem coluna) tira o filtro e a ordem; kg/h ↔ kg/h fica
  sp.cols=cc?sp.colsAll.slice(0,3).concat([cc],sp.colsAll.slice(3)):sp.colsAll; return sp.cols.length; }
function c3usos(self){ const u={}; RW(self,'g_cj').forEach(r=>{ [r.v.maq,r.v.impl].forEach(n=>{ if(n&&n!==C3.sem) (u[n]=u[n]||[]).push(r); }); }); return u; }
function c3temR(V){ return isnum(V.rend)&&String(V.rend)!==''; }
// painel da máquina: os conjuntos que a usam (cada um abre o conjunto); painel do conjunto: rendimento e exclusão
CAD_ACTS.g_atv=(self,r,fm)=>{ if(g2dirty(fm)) return []; const us=(c3usos(self)[r.v.nome]||[]);
  // equipamento do pivô de um setor da Irrigação: a ficha do pivô (capacidade) como sub-detalhe; sem ficha, registrá-la (revisão de 10/10, A4);
  // fechar volta a este painel
  const tf=FPV_EQ[r.id]?!!fpvFicha(r.id):null;
  const fp=tf===null?[]:[{t:tf?'Ficha do pivô ›':'Registrar ficha do pivô ›',h:tf?'Capacidade do equipamento: vazão, pressão, tempo de volta e lâmina pelo percentímetro.':'Digite a capacidade como está na ficha do fabricante: vazão, pressão, tempo de volta e lâmina pelo percentímetro.',
    go:()=>{ g2set(self,'g_atv',{fm:null}); fpvAbrir(self,r.id,{gid:'g_atv',rid:r.id},!tf); }}];
  return fp.concat(us.map((c,i)=>{ const o=c.v.maq===r.v.nome?(c.v.impl&&c.v.impl!==C3.sem?c.v.impl:''):c.v.maq;
    return {t:(o?o+' · ':'')+(ml(c.v.ops).join(', ')||'conjunto')+' ›',h:i===us.length-1?(us.length>1?'Conjuntos que usam esta máquina.':'Conjunto que usa esta máquina.'):'',go:()=>{ g2set(self,'g_atv',{fm:null}); g2open(self,GR('g_cj'),c.id,null); }}; })); };
CAD_ACTS.g_cj=(self,r)=>[c3temR(r.v)?null:{t:'Cadastrar rendimento ›',h:'Sem rendimento o planejamento não calcula horas nem custo deste conjunto.',go:()=>{ location.href='CD-08.dc.html'; }},
  cadExcluir(self,'g_cj',r,'conjunto',r.nd?'tem rendimento em Operações e rendimentos; troque o conjunto lá antes':'')];
function PREVALS(self,v){ cadActsIni(self); fpvVals(self,v);
  // CD-03.dc.html#ficha=<equipamento> (vindo da Irrigação) abre a ficha do pivô; fechar volta ao detalhe do equipamento
  if(!self.__fpvHash){ self.__fpvHash=1; try{ const m=/[#&]ficha=([^&]+)/.exec(location.hash||''); const id=m?decodeURIComponent(m[1]):''; if(FPV_EQ[id]&&fpvFicha(id)) setTimeout(()=>fpvAbrir(self,id,{gid:'g_atv',rid:id}),0); }catch(e){} }
  const atv=RW(self,'g_atv'); self._c3nomes=self._c3nomes||{}; const usos=c3usos(self); v.c3_ncol=c3capCol(self);
  /* TABR-CTX-02: a capacidade só nas linhas das classes do filtro que a coluna representa; nas outras a célula fica vazia. O menu de filtro (g2vals)
     conta todas as linhas da grade e punha a unidade da coluna no número de outra classe ("300 cv" era a vazão da bomba; escolher esvaziava a lista) */
  const emCap=GR('g_atv').cols.some(c=>c.k==='capn')?(V)=>(((g2st(self,'g_atv').f||{}).classe)||[]).indexOf(V.classe)>=0:()=>false;
  atv.forEach(r=>{ const V=r.v; self._c3nomes[r.id]=V.nome; const C=c3cond(r);
    // com ficha do pivô, a vazão do equipamento é a da ficha (uma fonte com a Irrigação; revisão de 10/10, A2)
    const fv=FPV_EQ[r.id]?fpvFicha(r.id):null; if(fv) V.vazao_ir=fpvM3(fv.vazao_ls);
    r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.p.modelo=[V.modelo?{k:'txt',t:V.modelo}:{k:'mut',t:'—'}]; r.s.modelo=V.modelo||'';
    r.p.classe=[{k:'txt',t:V.classe||'—'}]; r.s.classe=V.classe||'';
    const CP=emCap(V)?c3capn(V):null; V.capn=CP?CP.n:''; r.p.capn=[CP?{k:'txt',t:nfa(CP.n)}:{k:'mut',t:'—'}]; r.s.capn=CP?nfa(CP.n):'';   /* a coluna põe a unidade da classe */
    const K=c3calib(V); V.calv=K.venc||''; r.p.calv=[K.venc?(K.s==='Em dia'?{k:'txt',t:br(K.venc)}:{k:'cn',t:br(K.venc),c:K.s==='Vencida'?'red':'yellow'}):{k:'mut',t:'—'}]; r.s.calv=K.venc?br(K.venc):'';
    V.cond_t=C.m?C.t+' · '+C.m:C.t; const am=c3man(r.id); if(am){ V.rt=am.rt||'Otávio'; const cd=C3.cod[V.classe]; if(cd&&am.leit) V['cont_'+cd]=am.leit.val; }
    r.o=(C.x?[{t:'Ver ordens afetadas · '+C.x.ordens.join(' e '),h:'OS.dc.html'}].concat(C.x.om?[{t:'Abrir '+C.x.om+' na Manutenção',h:'MA.dc.html#om='+C.x.om}]:[]):[]).concat(am?[{t:'Abrir '+V.nome+' na Manutenção',h:'MA.dc.html#ativo='+r.id}]:[]);
    const ch=isnum(V.custo_h)&&String(V.custo_h)!==''; r.p.custo_h=ch?[{k:'txt',t:nf(V.custo_h,2)}]:[{k:'mut',t:'—'}]; r.s.custo_h=ch?nf(V.custo_h,2):'';   // a coluna põe "R$ …/h"
    const n=(usos[V.nome]||[]).length; V.ncj=n; r.p.ncj=[{k:(n?'txt':'mut'),t:n?String(n):'—'}]; r.s.ncj=n?String(n):'';
    const S=c3sit(r); r.p.est=S.p; r.s.est=S.t; });
  cadQf(self,v,'g_atv','c3qf',[{k:'res',t:'A resolver',f:r=>!!c3sit(r).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativo',oz:true}]);
  c3opts('g_cj','maq',atv.filter(r=>C3.impl.indexOf(r.v.classe)<0).map(r=>r.v.nome));
  c3opts('g_cj','impl',[C3.sem].concat(atv.filter(r=>C3.impl.indexOf(r.v.classe)>=0).map(r=>r.v.nome)));
  // conjuntos na grade do motor (antes cartões próprios): máquina + implemento, situação com o próximo passo (o motivo na dica), operações,
  // largura, rendimento, potência e operadores alocáveis
  RW(self,'g_cj').forEach(r=>{ const V=r.v; const X=c3conj(self,V); const nome=(V.maq||'')+(X.I?' + '+V.impl:''); r.p.nome=[{k:'b',t:nome}]; r.s.nome=nome;
    const lg=X.I?c3larg(X.I.v):(X.M?c3larg(X.M.v):null); V.larg=lg===null?'':lg; r.p.larg=[lg===null?{k:'mut',t:'—'}:{k:'txt',t:nfa(lg)}]; r.s.larg=lg===null?'':nfa(lg);
    const temR=c3temR(V); r.nd=temR?'tem rendimento':''; r.p.rend=[temR?{k:'txt',t:nf(V.rend,2)}:{k:'mut',t:'—'}]; r.s.rend=temR?nf(V.rend,2):'';
    const pot=X.M&&X.M.v.classe==='Trator'?c3n(X.M.v,'pot'):null; V.pot=pot===null?'':pot; r.p.pot=[pot===null?{k:'mut',t:'—'}:{k:'txt',t:nfa(pot)}]; r.s.pot=pot===null?'':nfa(pot);
    const ops=ml(V.ops); r.m=Object.assign({},r.m||{},{ops:ops.map(o=>({id:o,l:o}))}); r.p.ops=[ops.length?{k:'txt',t:ops.join(', ')}:{k:'mut',t:'—'}]; r.s.ops=ops.join(', ');
    const O=c3oper(V.ops); r.p.oper=O.p; r.s.oper=O.s; const S=c3cjSit(self,V); r.p.est=S.p; r.s.est=S.t; });
  cadQf(self,v,'g_cj','c3qfc',[{k:'res',t:'A resolver',f:r=>!!c3cjSit(self,r.v).res}]); }
// situação do conjunto: um só cálculo para a linha e o filtro "A resolver"; o motivo (máquina bloqueada, calibração, substituto) vai na dica
function c3cjSit(self,V){ const X=c3conj(self,V);
  if(X.bad.length){ const det=X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(' · ')+(X.sub?' · substituto: '+X.sub.v.nome+' ('+nfa(c3n(X.sub.v,'pot'))+' cv)':'');
    return {t:'Indisponível',p:[Object.assign(chipc('Indisponível','red'),{dica:det}),{k:'b',t:(X.sub?'Trocar pelo '+X.sub.v.nome:'Trocar máquina')+' ›'}],res:true}; }
  if(X.cal.length){ const det=X.cal.map(x=>x.v.nome+' · '+c3calib(x.v).s.toLowerCase()).join(' · ');
    return {t:'Calibrar antes de usar',p:[Object.assign(chipc('Calibrar antes de usar','yellow'),{dica:det}),{k:'b',t:'Registrar calibração ›'}],res:true}; }
  if(!c3temR(V)) return {t:'Sem rendimento',p:sitX('Sem rendimento','yellow','Cadastrar rendimento','CD-08.dc.html'),res:true};
  return {t:'Disponível',p:sitOk('Disponível')}; }
function EXTRAVALS(self,v){
  const atv=RW(self,'g_atv'); const manL=atv.filter(r=>c3sit(r).res==='man'), calL=atv.filter(r=>c3sit(r).res==='cal'); const man=manL.length, cal=calL.length;
  cadEstado(v,'c3e',[man?man+(man>1?' máquinas bloqueadas':' máquina bloqueada'):'',cal?cal+(cal>1?' calibrações a resolver':' calibração a resolver'):''].filter(Boolean).join(' · ')||'Máquinas aptas e calibradas',
            man?'red':(cal?'yellow':'green'));
  const cjs=RW(self,'g_cj'); const cjBad=cjs.filter(r=>c3conj(self,r.v).bad.length).length, cjAv=cjs.filter(r=>{ const X=c3conj(self,r.v); return !X.bad.length&&(X.cal.length||!c3temR(r.v)); }).length;
  const aba=cadAbas(self,v,'c3t','c3aba',[{slug:'maquinas',n:atv.length,cor:man?'red':(cal?'yellow':'')},{slug:'conjuntos',n:cjs.length,cor:cjBad?'red':(cjAv?'yellow':'')}]);
  cadPrim(v,aba===1?'Criar conjunto':'Criar máquina ou instalação',aba===1?v.g_cj_new:v.g_atv_new);   // BOT-03: registro novo e independente é Criar
  cadQfPos(self,v,'g_atv','c3qf'); cadQfPos(self,v,'g_cj','c3qfc');
  // classe escolhida no cadastro novo já marca se exige calibração (continua editável)
  const F=v.g_atv_F; if(F&&F.open&&F.fields){ const f=F.fields.find(x=>x.fid==='fx_g_atv_classe');
    if(f&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_atv').fm; if(!cur) return; const val=e.target.value; const d=Object.assign({},cur.draft,{classe:val});
      if(cur.isNew) d.exige=C3.calib.indexOf(val)>=0?'Sim':'Não'; const er=Object.assign({},cur.errs||{}); delete er.classe;
      g2set(self,'g_atv',{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }; }
  if(F&&F.open&&F.edit&&(g2st(self,'g_atv').fm||{}).isNew) F.sub=C3.subnew;
  selFiel(v.g_atv_F); selFiel(v.g_cj_F);
  // vazão do pivô (equipamento de um setor da Irrigação): só leitura aqui; muda-se na ficha do pivô, que o cadastro e a Irrigação leem
  // (revisão de 10/10, A2: uma fonte também durante o uso; sem ficha, vale a do setor até registrar a ficha)
  if(F&&F.open&&F.fields){ const fm=g2st(self,'g_atv').fm; const pv=fm&&fm.rid&&FPV_EQ[fm.rid]; const fv=pv?fpvFicha(fm.rid):null; const f=F.fields.find(x=>x.fid==='fx_g_atv_vazao_ir');
    if(f&&pv){ f.dis=true; if(fv) f.v=String(fpvM3(fv.vazao_ls)); f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); f.set=()=>{}; f.hasHelp=true;
      f.help=fv?('Vem da ficha do pivô ('+fpvNat(fv.vazao_ls)+' L/s): corrija na Ficha do pivô; o cadastro e a Irrigação usam a mesma vazão.')
        :('Vazão do setor '+pv.setor+' na Irrigação ('+fpvNat(pv.vaz)+' L/s). Para mudar, registre a ficha do pivô: o cadastro e a Irrigação passam a usá-la.'); } }
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
        +(X.bad.length?' · indisponível: '+X.bad.map(y=>y.x.v.nome+' '+y.c.curto).join(', '):' · disponível')+(isNew?'. Cadastre o rendimento em Operações e rendimentos.':'.')}); } }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela ou os cartões da aba rolam
    E.EXTRA.append(EXTRA_FP)
    shell37('CD-03','Máquinas, instalações e setores',corpo,fname=fname,status=None,primary_html=prim_cab(),search=False)
    estado_cab(fname,'Máquinas, instalações e setores','c3e')
    from areas.cadastros import ncol_dinamico
    ncol_dinamico(fname,['c3_ncol'])   # a coluna da capacidade entra e sai com o filtro de Classe

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
               # 16/10/2026: "Calendário de trabalho" saiu (nenhuma tela lia o da pessoa; vale o calendário da equipe)
               num('custo','Custo-hora com encargos','R$/h',min=0,help='Salário e encargos por hora trabalhada; visível só para quem tem permissão de custos.'),
               sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})])
    # pessoa numa linha, uma variável por coluna (TABELAS-FOCO, 04/10/2026): equipe, habilidades (filtro por habilidade), vínculo, disponível até,
    # "Custo R$/h", habilitação exigida e a validade que vence primeiro, calendário (o da equipe ou o próprio) e acesso ao app (a ficha de campo
    # depende dele); situação (alocável em O.S. ou não)
    # revisão TABR (09/10): a Situação logo depois da pessoa (A1), com o motivo e o próximo passo quando não alocável (A3); calendário e acesso
    # ao app no painel da pessoa (campos do formulário)
    # integração V56: com as equipes e pessoas do Beneficiamento e da Manutenção (Igor, Marta: "Beneficiamento e qualidade", "Autorizar rota e
    # liberar ordem de processo") a grade passava 37 px da caixa a 1440 px; Equipe e Habilidades quebram linha um pouco antes e a grade cabe (A1)
    gp=grid([dict(k='nome',l='Pessoa',w=200),dict(k='est',l='Situação',w=185),dict(k='equipe',l='Equipe',w=104),dict(k='habs',l='Habilidades',multi=True,w=136),
             dict(k='vinc',l='Vínculo',w=100),dict(k='ate',l='Disponível até',t='date'),dict(k='custo',l='R$/h',t='num',a='r',d=2),dict(k='habx',l='Habilitação',multi=True),
             dict(k='habv',l='Validade da habilitação',t='date')],
        [R(pid,v) for pid,v in pes],gid='g_pes',total=False,qf=QF_CAD,busca_extra=filtro_sel('c4fun','Função'),   # TAB-01: filtros à esquerda
        edit=dict(m='form',title='Pessoa',newTitle='Cadastrar pessoa',
            sub='Marque o que a pessoa faz; a habilitação exigida aparece abaixo. Cadastrar não cria login. Inative em vez de excluir.',fields=campos))
    # Equipes (16/10/2026): eram só cartões próprios; agora a grade do motor com Tabela | Cartões (VIS-05), com o que o cartão mostrava em colunas
    ge=grid([dict(k='nome',l='Equipe'),dict(k='est',l='Situação',w=200),dict(k='lider',l='Líder'),dict(k='membros',l='Pessoas ativas',t='num',a='r'),
             dict(k='jorn',l='Jornada',t='num',a='r',un='h/dia'),dict(k='cal',l='Calendário',w=220)],
        [R(i,dict(nome=n,lider=l,cal=c)) for i,n,l,c in EQUIPES],gid='g_eq',dele=False,total=False,qf=QF_CAD,cartoes=True,
        edit=dict(m='form',title='Equipe',newTitle='Cadastrar equipe',sub='Altere nome, líder e calendário; quem segue a equipe herda o calendário.',
            fields=[txt('nome','Nome da equipe'),sel('lider','Líder',[v['nome'] for _,v in pes]),sel('cal','Calendário',CALS,**{'def':'seg–sáb · 06–15h'})]))
    # um bloco com abas: Pessoas | Equipes, as duas na grade do motor; a primária do cabeçalho segue a aba (BOT-01/03)
    acoes_form('g_eq')
    corpo=bloco_cad(abas('c4t',['Pessoas','Equipes'],'Cadastros de pessoas'),pane('c4t',0,gp)+pane('c4t',1,ge),'Pessoas e equipes')
    dados=dict(qf=QF,habil=[[a,k] for a,k,_ in HABIL],calda=CALDA,agro=AGRO)
    js({},ALOC_JS+'const C4='+json.dumps(dados,ensure_ascii=False)+';\n'+r'''
function c4hdia(c){ const m=/(\d{2})–(\d{2})h/.exec(c||''); if(m) return (Number(m[2])-Number(m[1]))+' h/dia'; const n=/(\d+)h$/.exec(c||''); return n?n[1]+' h/dia':''; }
function c4qf(k,V,A){ const h=ml(V.hab);
  if(k==='ope') return h.some(x=>x.indexOf('Operar')===0); if(k==='cal') return h.indexOf(C4.calda)>=0; if(k==='irr') return h.indexOf('Irrigar')>=0;
  if(k==='alm') return h.indexOf('Almoxarifado')>=0; if(k==='agr') return h.indexOf(C4.agro)>=0; if(k==='nao') return !A.ok&&!A.inat;
  if(k==='res') return (!A.ok&&!A.inat)||A.vence; return true; }
function c4eqcal(self){ const o={}; RW(self,'g_eq').forEach(e=>{ o[e.v.nome]=e.v.cal; }); return o; }
// situação da pessoa: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o estado do cabeçalho
// a habilitação e a validade têm colunas próprias; a Situação é só o estado (chip) e o próximo passo
// não alocável: o chip diz a consequência e a dica diz o motivo; o verbo nomeia o que resolver (revisão TABR A3: o motivo tinha saído da linha)
function c4passo(V,A){ const h=A.t.find(y=>y.s==='venc'||y.s==='pend'); if(h) return (h.s==='pend'?'Registrar ':'Renovar ')+h.x;
  if(V.ate&&V.ate<HOJE) return 'Renovar contrato'; if(V.adm&&V.adm>HOJE) return 'Aguardar admissão em '+br(V.adm); return 'Regularizar'; }
function c4sit(V){ const A=alocavel(V);
  if(A.inat) return {t:'Inativa',p:[chipc('Inativa','gray')]};
  if(!A.ok){ const m=A.m.charAt(0).toUpperCase()+A.m.slice(1); return {t:'Não alocável',p:[Object.assign(chipc('Não alocável em O.S.','red'),{dica:m}),{k:'b',t:c4passo(V,A)+' ›'}],res:'nao'}; }
  if(A.vence) return {t:'Vence em 30 dias',p:sitX('Vence em 30 dias','yellow','Renovar'),res:'ven'};
  return {t:'Alocável',p:sitOk('Alocável')}; }
// validade que vale para alocar: a mais próxima entre as habilitações exigidas (pendente fica sem data)
function c4val(A){ const ds=A.t.filter(y=>y.d).map(y=>y.d).sort(); return ds.length?ds[0]:''; }
// acesso: só leitura do estado de Configurações (c.conf; CONF-D05): concede, convida e desativa em Configurações › Usuários e alçadas
function c4ac(V){ return (typeof confAcessoDe==='function'&&confAcessoDe(V.nome))||{a:'sem'}; }
function c4acesso(V){ const e=c4ac(V); return e.a==='ativo'?'':(e.a==='desativado'?'Acesso desativado em '+br(e.ate):'Sem acesso ao app'); }
function c4acOrig(V){ const e=c4ac(V); const t=e.a==='ativo'?'Ativo desde '+br(e.desde):(e.a==='desativado'?'Desativado em '+br(e.ate):'Sem acesso');
  return [{t:'Acesso ao app: '+t+' · gerenciar em Configurações › Usuários e alçadas',h:'CF-01.dc.html#pessoa='+encodeURIComponent(V.nome||'')}]; }
CAD_ACTS.g_eq=(self,r)=>[cadExcluir(self,'g_eq',r,'equipe',r.nd?'tem pessoas ativas; mude-as de equipe antes':'')];
function PREVALS(self,v){ cadActsIni(self); const ps=RW(self,'g_pes'); const eqc=c4eqcal(self); self._c4eq=self._c4eq||{}; self._c4pes=self._c4pes||{};
  ps.forEach(r=>{ const V=r.v; self._c4pes[r.id]=V.nome;
    r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.o=c4acOrig(V); r.p.equipe=[{k:'txt',t:V.equipe||'—'}]; r.s.equipe=V.equipe||'';
    const hs=ml(V.hab); r.m=Object.assign({},r.m||{},{habs:hs.map(h=>({id:h,l:h}))}); r.p.habs=[hs.length?{k:'txt',t:hs.join(', ')}:{k:'mut',t:'—'}]; r.s.habs=hs.join(', ');
    r.p.vinc=[{k:'txt',t:V.vinc||'—'}]; r.s.vinc=V.vinc||'';
    // disponível até: contrato encerrado em vermelho (o chip da Situação diz o motivo)
    r.p.ate=[V.ate?(V.ate<HOJE?{k:'cn',t:br(V.ate),c:'red'}:{k:'txt',t:br(V.ate)}):{k:'mut',t:'—'}]; r.s.ate=V.ate?br(V.ate):'';
    const cu=isnum(V.custo)&&String(V.custo)!==''; r.p.custo=[cu?{k:'txt',t:nf(V.custo,2)}:{k:'mut',t:'—'}]; r.s.custo=cu?nf(V.custo,2):'';   // a coluna põe "R$ …/h"
    const A=alocavel(V); const ex=habExig(V.hab); r.m.habx=ex.map(x=>({id:x,l:x})); r.p.habx=[ex.length?{k:'txt',t:ex.join(', ')}:{k:'mut',t:'—'}]; r.s.habx=ex.join(', ');
    const hv=c4val(A); V.habv=hv; const pend=A.t.some(y=>y.s==='pend'); const hvc=A.t.some(y=>y.s==='venc')?'red':(A.vence?'yellow':'');
    r.p.habv=[hv?(hvc?{k:'cn',t:br(hv),c:hvc}:{k:'txt',t:br(hv)}):(pend?{k:'cn',t:'pendente',c:'red'}:{k:'mut',t:'—'})]; r.s.habv=hv?br(hv):(pend?'pendente':'');
    const S=c4sit(V); r.p.est=S.p; r.s.est=S.t; });
  // filtro do bloco: estado (Todas · A resolver) e função (lista), que valem juntos
  const fun=cadSel(self,v,'c4fun',[{v:'',t:'Todas'}].concat(C4.qf.filter(([k])=>k!=='nao').map(([k,t])=>({v:k,t:t+' ('+ps.filter(r=>c4qf(k,r.v,alocavel(r.v))).length+')'}))));
  cadQf(self,v,'g_pes','c4qf',Object.assign([{k:'res',t:'A resolver',f:r=>!!c4sit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oz:true}],{todos:'Todas'}),
        {extra:fun?(r=>c4qf(fun,r.v,alocavel(r.v))):null});
  const eqs=RW(self,'g_eq');
  eqs.forEach(r=>{ self._c4eq[r.id]=r.v.nome; const n=ps.filter(p=>p.v.equipe===r.v.nome&&p.v.sit!=='Inativa').length; r.v.membros=n; r.nd=n?'tem pessoas':''; r.s.nome=r.v.nome||''; });
  // equipes na grade do motor (antes cartões próprios): situação (líder inativa, gente não alocável), líder, pessoas ativas, jornada e calendário
  eqs.forEach(r=>{ const V=r.v; const S=c4eqSit(ps,V); r.p.est=S.p; r.s.est=S.t; r.p.nome=[{k:'b',t:V.nome||''}];
    const L=ps.find(p=>p.v.nome===V.lider); const linat=!!V.lider&&(!L||L.v.sit==='Inativa');
    r.p.lider=[V.lider?{k:'txt',t:V.lider}:{k:'mut',t:'—'}].concat(linat?[{k:'mut',t:'inativa'}]:[]); r.s.lider=V.lider||'';
    r.p.membros=[{k:(V.membros?'txt':'mut'),t:String(V.membros||0)}]; r.s.membros=String(V.membros||0);
    const hd=c4hdia(V.cal); const hn=hd?Number(hd.replace(' h/dia','')):''; V.jorn=hn; r.p.jorn=[hd?{k:'txt',t:String(hn)}:{k:'mut',t:'—'}]; r.s.jorn=hd?String(hn):'';
    r.p.cal=[V.cal?{k:'txt',t:V.cal}:{k:'mut',t:'—'}]; r.s.cal=V.cal||''; });
  cadQf(self,v,'g_eq','c4qfe',Object.assign([{k:'res',t:'A resolver',f:r=>!!c4eqSit(ps,r.v).res}],{todos:'Todas'}));
  const fe=(GR('g_eq').edit.fields||[]).find(x=>x.k==='lider'); if(fe) fe.opts=ps.filter(p=>p.v.sit!=='Inativa').map(p=>p.v.nome);
  const fq=(GR('g_pes').edit.fields||[]).find(x=>x.k==='equipe'); if(fq) fq.opts=eqs.map(e=>e.v.nome); }
// situação da equipe: líder inativa (escolher outro) ou gente não alocável em O.S.; um só cálculo para a linha e o filtro "A resolver"
function c4eqSit(ps,V){ const mem=ps.filter(p=>p.v.equipe===V.nome&&p.v.sit!=='Inativa'); const nao=mem.filter(p=>!alocavel(p.v).ok).length;
  const L=ps.find(p=>p.v.nome===V.lider); const linat=!!V.lider&&(!L||L.v.sit==='Inativa');
  if(linat) return {t:'Líder inativa',p:sitX('Líder inativa','yellow','Escolher líder ativo'),res:true};
  if(nao) { const t=nao+(nao>1?' não alocáveis':' não alocável'); return {t:t,p:[chipc(t,'red')],res:true}; }
  return {t:'Em dia',p:sitOk('Em dia')}; }
function EXTRAVALS(self,v){ const ps=RW(self,'g_pes'); const eqc=c4eqcal(self);
  const naoL=ps.filter(r=>c4sit(r.v).res==='nao'), venL=ps.filter(r=>c4sit(r.v).res==='ven'); const nao=naoL.length, ven=venL.length;
  cadEstado(v,'c4e',[nao?nao+(nao>1?' não alocáveis':' não alocável'):'',ven?ven+' a renovar em 30 dias':''].filter(Boolean).join(' · ')||'Todos alocáveis',nao?'red':(ven?'yellow':'green'));
  const eqs=RW(self,'g_eq'); const eqLid=eqs.filter(e=>{ const L=ps.find(p=>p.v.nome===e.v.lider); return !!e.v.lider&&(!L||L.v.sit==='Inativa'); }).length;
  const eqNao=eqs.filter(e=>ps.some(p=>p.v.equipe===e.v.nome&&p.v.sit!=='Inativa'&&!alocavel(p.v).ok)).length;
  const aba=cadAbas(self,v,'c4t','c4aba',[{slug:'pessoas',n:ps.length,cor:nao?'red':(ven?'yellow':'')},{slug:'equipes',n:eqs.length,cor:eqNao?'red':(eqLid?'yellow':'')}]);
  cadPrim(v,aba===1?'Criar equipe':'Criar pessoa',aba===1?v.g_eq_new:v.g_pes_new);   // BOT-03: registro novo e independente é Criar
  cadQfPos(self,v,'g_pes','c4qf'); cadConta(self,v,'g_pes'); cadQfPos(self,v,'g_eq','c4qfe');
  if(self.state.c4fun){ v.g_pes_filtered=true; v.g_pes_clear=()=>{ g2set(self,'g_pes',{q:'',f:{}}); self.setState({c4qf:'',c4fun:''}); }; }
  // formulário: validade só das habilitações exigidas; ajuda com a habilitação e o calendário; acesso ao app simulado
  const F=v.g_pes_F; if(F&&F.open&&F.fields){ const fm=g2st(self,'g_pes').fm||{}; const d=fm.draft||{}; const ex=habExig(d.hab);
    F.fields=F.fields.filter(f=>{ const h=C4.habil.find(y=>f.fid==='fx_g_pes_'+y[1]); return !h||ex.indexOf(h[0])>=0; });
    C4.habil.forEach(([x,k])=>{ const f=F.fields.find(y=>y.fid==='fx_g_pes_'+k); if(!f) return; const dv=d[k];
      if(!dv||dv<HOJE){ f.help=(dv?'Vencida':'Pendente')+': grava, mas a pessoa fica não alocável em O.S.'; f.hasHelp=true; } else { f.help=''; f.hasHelp=false; } });
    const fh=F.fields.find(f=>f.fid==='fx_g_pes_hab'); if(fh){ fh.help=ex.length?'Exige '+lista(ex)+' com validade.':'Nenhuma habilitação exigida.'; fh.hasHelp=true; }
    const fq=F.fields.find(f=>f.fid==='fx_g_pes_equipe'); if(fq){ const c=eqc[d.equipe]; fq.help=c?'Calendário da equipe: '+c+' · '+c4hdia(c):''; fq.hasHelp=!!c; }
  }
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
    if(gid==='g_pes'){
      // renomear a pessoa atualiza o líder das equipes (como equipe → pessoas)
      const old=(self._c4pes||{})[r.id]; const es=g2clone(RW(self,'g_eq')); const ren=[];
      if(old&&old!==r.v.nome){ es.forEach(e=>{ if(e.v.lider===old){ e.v.lider=r.v.nome; ren.push(e.v.nome); } }); if(ren.length) g2set(self,'g_eq',{rows:es}); }
      const A=alocavel(r.v); const lid=es.filter(e=>e.v.lider===r.v.nome).map(e=>e.v.nome);
      self.setState({g2toast:ponto((isNew?'Cadastrado: ':'Salvo: ')+r.v.nome+' · '+(A.inat?'inativa':(A.ok?'alocável em O.S.':'não alocável em O.S. até resolver '+A.m))
        +(A.inat&&lid.length?' · escolha outro líder para '+lista(lid):(ren.length?' · líder de '+lista(ren)+' atualizado':'')))}); }
    if(gid==='g_eq'){ const old=(self._c4eq||{})[r.id]; let n=0;
      if(old&&old!==r.v.nome){ const ps=g2clone(RW(self,'g_pes')); ps.forEach(p=>{ if(p.v.equipe===old){ p.v.equipe=r.v.nome; n++; } }); g2set(self,'g_pes',{rows:ps}); }
      self.setState({g2toast:(isNew?'Equipe criada: ':'Salvo: ')+r.v.nome+' · '+r.v.cal+' · '+c4hdia(r.v.cal)+(n?' · '+n+(n>1?' pessoas seguem':' pessoa segue')+' a equipe':'')+'.'}); } }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela ou os cartões da aba rolam
    shell37('CD-04','Pessoas e equipes',corpo,fname=fname,status=None,primary_html=prim_cab(),search=False)
    estado_cab(fname,'Pessoas e equipes','c4e')
