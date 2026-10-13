# -*- coding: utf-8 -*-
"""CD-01 Fazendas, áreas e talhões · CD-01det Detalhe do talhão (módulo próprio; areas.cadastros.build usa este se existir).

Layout de 01/10/2026 (padrão dos cadastros em areas/cadastros.py): um bloco com abas Talhões | Fazendas | Ambiental | Água; cada aba com a
sua faixa "precisa de atenção", o filtro rápido e a sua ação (Cadastrar talhão / Cadastrar fazenda); Lista | Mapa na aba Talhões (Santa Rita
desenhada; Lagoa Grande com os pivôs do KML). Fazenda Lagoa Grande (KML do proprietário): 23 pivôs viram talhões com geometria "Círculo do
KML" (centro + área declarada, não polígono validado); perímetros, Reserva Legal, APP e pontos de água ficam no cadastro da fazenda.
CD-01 (listagem): entidade Fazenda (cadastrar, editar pelo cartão, inativar sem excluir) e talhões em árvore por fazenda,
com subtotal por fazenda (sem total que some fazendas). Formulário do talhão: fazenda da lista cadastrada + "Cadastrar fazenda…"
(volta ao talhão sem perder o preenchido), área cultivável × polígono com motivo acima de 1 %, sistema e pivô/setor, situação.
CD-01det (detalhe): qualquer talhão, escolhido no seletor do cabeçalho (ou por #talhao=ID vindo da lista); resumo por safra
(cultivável · alocado · livre), parcelas em consulta com origem no Planejar safra, abas Parcelas por safra ("Planejar Tn na safra"
leva ao SAF) | Geometria (versões do polígono e "Definir polígono", importar ou desenhar, simulados); "Reativar" na linha do talhão.
Geometria das parcelas: dados.GEO_PARC (fonte única com o Mapa). Fazendas, sistemas e versões: dados_cad.
As duas telas gravam fazendas e talhões em localStorage (talhao-os-cd01-v1) para que o detalhe abra o talhão salvo na lista."""
import json, os
from engine import grid, esc, _MINI, BTN_ST, INK, MUTED, LINE, BG, SURF, ACC, DISP
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2
import dados_cad as DC
from areas.cadastros import H, sel, num, txt, dat, R, js
from areas.cadastros import (cadx_css, abas, pane, se, faixa, prim, secbtn, qf_chips, seg, barra, cartoes, bloco_cad, estado_cab, estado_html, acoes_form, PRIM_ST, arv,
                             md, mestre, det_cab, vazio, md_css, criar_cab, ncol_dinamico)

F_=H('false'); T_=H('true')
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
SIS=['Sequeiro','Pivô central','Gotejo']
NOVA_FAZ='+ Criar fazenda…'   # AC-72-12: cria a fazenda sem sair do talhão (verbo Criar, BOT-03)
SAF_ATUAL=D2.SAFRAS[0]
SAF_ABERTAS=[s for s in D2.SAFRAS if not s['ro']]
def _br(n): return f'{n:,.2f}'.replace(',','X').replace('.',',').replace('X','.').rstrip('0').rstrip(',')
def _tal_de(local): return local.split('-')[0]

# ---------------- dados ----------------
def _doc_agua(tipo):
    """documento do ponto de água: Outorga ou Certidão (de uso insignificante); sem descrição no KML fica vazio."""
    return '' if not tipo else ('Outorga' if tipo.startswith('Outorga') else 'Certidão')
def _vazao_m3h(txt):
    """vazão do documento em m³/h para ordenar (L/s × 3,6); '—' ou texto sem número fica vazio."""
    import re as _r
    m=_r.match(r'^\s*([\d.]+(?:,\d+)?)\s*(m³/h|L/s)\s*$',txt or '')
    if not m: return ''
    n=float(m.group(1).replace('.','').replace(',','.'))
    return round(n*3.6,2) if m.group(2)=='L/s' else n
def _br2(n): return f'{n:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def _lg_textos():
    """perímetros, restrição ambiental e água da Lagoa Grande resumidos para o painel da fazenda (o detalhe fica nas abas Ambiental e Água)."""
    per='; '.join((f"{p['nome']}: {_br2(p['area'])} ha · {p['mun']} · {str(p['mf']).replace('.',',')} módulos fiscais · recibo do CAR {p['car']}" if p['area'] else
                   f"{p['nome']}: área não informada no KML") for p in DC.LG_PERIMETROS)
    tot={g:a for g,t,a,tt in DC.LG_AMBIENTAL if tt}
    amb=f"Reserva legal {_br2(tot.get('Reserva legal',0))} ha · APP total {_br2(tot.get('APP',0))} ha (categorias na aba Ambiental)"
    agua=f"{len(DC.LG_AGUA)} pontos de outorga ou certidão (detalhe na aba Água)"
    return per,amb,agua
def _faz_rows():
    out=[]
    for f in DC.FAZENDAS:
        mun,uf=f['mun'].rsplit('/',1)
        v=dict(nome=f['nome'],empresa=f['empresa'],mun=mun,uf=uf,fuso=f['fuso'],area=f['area'],posse=f['posse'],arrend=f['arrend'],
               fim=f['fim'],custo=f['custo'],car=f['car'],matr=f['matr'],pend=f['pend'],sit=f['sit'],mf=f.get('mf',''),kml='')
        if f['id']=='LG':
            per,amb,agua=_lg_textos(); v.update(kml='Sim',perim=per,ambs=amb,aguas=agua)
        out.append(R(f['id'],v))
    return out
def _tal_rows():
    out=[]
    for t,ha,cult,fase,obs in D.TALHOES:
        sis,setor=DC.SISTEMA.get(obs,('Sequeiro',''))
        out.append(R(t,dict(t=t,faz='Santa Rita',sis=sis,setor=setor,decl=float(ha),calc=DC.CALC[t],motivo='',sit='Ativo',inat='',ver=DC.geo_vers(t)[-1][0])))
    out.append(R('B1',dict(t='B1',faz='Boa Vista',sis='Sequeiro',setor='',decl=120.0,calc='',motivo='',sit='Ativo',inat='',ver='')))
    # Lagoa Grande: só os pivôs centrais viram talhão; a geometria é o círculo do KML (centro + área declarada), não polígono validado
    for pid,nm,ha,lon,lat,raio in DC.LG_PIVOS:
        out.append(R(pid,dict(t=pid,faz='Lagoa Grande',sis='Pivô central',setor='',decl=ha,calc='',motivo='',sit='Ativo',inat='',ver='',geo='circ',
                              geo_t=f"{DC.LG_GEO} · {nm} · raio {_br2(raio)} m · centro {lat:.5f}; {lon:.5f}".replace('.',','))))
    return out
def _aloc():
    """área alocada em parcelas por talhão e safra aberta (a área cultivável não pode ficar abaixo dela)."""
    a={}
    for s in SAF_ABERTAS:
        for c in D2.CULTIVOS[s['id']]:
            d=a.setdefault(_tal_de(c['local']),{}); d[s['nome']]=round(d.get(s['nome'],0)+c['area'],2)
    return a
def _nparc():
    n={}
    for c in D2.CULTIVOS[SAF_ATUAL['id']]: n[_tal_de(c['local'])]=n.get(_tal_de(c['local']),0)+1
    # Lagoa Grande: pivôs (PVxx) com o cultivo da Safra Mamão 2026/27 (dados_lagoa_safra.py)
    import dados_lagoa_safra as DL
    for c in D2.CULTIVOS.get(DL.SAFRA['id'],[]): k=DL.PID_DE[c['local']]; n[k]=n.get(k,0)+1
    return n

# ---------------- campos ----------------
SUB_TAL='Altere o talhão. A área do polígono só muda com nova versão, no detalhe do talhão; para tirar de uso, marque Inativo (nada é excluído).'
SUB_FAZ='Altere a fazenda. Para tirar de uso, marque Inativa: nada é excluído.'
# formulário de cadastro novo: texto de cadastro, sem instrução de inativar e sem campo que só existe depois (polígono, situação)
SUB_NOVO={'g_faz':'Crie a fazenda com empresa, município, área total e posse.',
          'g_tal':'Crie o talhão com fazenda, sistema e área cultivável; o polígono fica pendente e aparece no Próximo passo do talhão.'}
NOVO_OCULTO={'g_faz':['sit'],'g_tal':['calc','sit'],'g_idt':['calc','sit']}
def campos_tal(fazs):
    return [txt('t','Identificação do talhão',help='Ex.: T8. Não pode repetir na mesma fazenda.'),
            sel('faz','Fazenda',fazs,**{'def':fazs[0]}),
            sel('sis','Sistema',SIS,**{'def':'Sequeiro'}),
            sel('setor','Pivô ou setor de irrigação',DC.SETORES,req=False,help='Ativo de irrigação de Máquinas, instalações e setores; o balanço hídrico usa este vínculo.'),
            num('decl','Área cultivável','ha',min=0.1,max=5000,help='Área plantável, sem carreador, APP e sede. Parcelas, doses e custo por hectare partem dela.'),
            num('calc','Área do polígono','ha',req=False,ro=True,help='Da versão atual do polígono; em branco enquanto não houver polígono.'),
            dict(k='geo_t',l='Geometria',t='area',ro=True,req=False,cond=dict(k='geo',eq='circ'),help='Não é polígono validado; defina o polígono no detalhe do talhão.'),
            dict(k='geo',l='geo',t='txt',req=False,cond=dict(k='_nunca',eq='1')),
            sel('motivo','Motivo da diferença',DC.MOTIVOS_DIF,req=False,help='Pedido quando a área cultivável difere mais de 1 % do polígono.'),
            sel('sit','Situação',['Ativo','Inativo'],**{'def':'Ativo'},help='Inativo sai do Planejar safra e do Mapa; safras e O.S. antigas seguem consultáveis.')]
CAMPOS_FAZ=[txt('nome','Nome da fazenda'),
            sel('empresa','Empresa',DC.EMPRESAS,**{'def':DC.EMPRESAS[0]},help='Responde pelos custos e pelo crédito (Estrutura gerencial).'),
            txt('mun','Município'),sel('uf','UF',UFS,**{'def':'GO'}),
            sel('fuso','Fuso horário',DC.FUSOS,**{'def':DC.FUSOS[0]},help='Sugerido pela UF. Gatilhos da safra e janelas da O.S. usam este fuso.'),
            num('area','Área total do imóvel','ha',min=1,max=100000,help='Inclui reserva, APP, sede e carreadores.'),
            sel('posse','Posse',DC.POSSE,**{'def':'Própria'}),
            txt('arrend','Arrendador ou parceiro',req=False),
            dat('fim','Fim do contrato',req=False),
            num('custo','Custo da terra','sc/ha/ano',req=False,min=0,help='Entra no custo por hectare de cada talhão.'),
            num('mf','Módulos fiscais',req=False,min=0,help='Do recibo do CAR.'),
            txt('car','CAR',req=False,help='Recibo do CAR. Em branco fica pendente: bloqueia só o crédito rural.'),
            txt('matr','Matrícula e cartório',req=False,help='Ex.: 12.401 · CRI de Rio Verde.'),
            txt('pend','Pendência nos documentos',req=False,help='Ex.: contrato sem registro em cartório. Não bloqueia o planejamento.'),
            dict(k='perim',l='Perímetros',t='area',ro=True,req=False,cond=dict(k='kml',eq='Sim'),help=('Demonstração sintética (fictício)' if __import__('dados_lagoa_fonte').ROTULO else 'Do KML do proprietário')+'; perímetro não vira talhão.'),
            dict(k='ambs',l='Restrição ambiental',t='area',ro=True,req=False,cond=dict(k='kml',eq='Sim')),
            dict(k='aguas',l='Recursos hídricos',t='area',ro=True,req=False,cond=dict(k='kml',eq='Sim')),
            dict(k='kml',l='kml',t='txt',req=False,cond=dict(k='_nunca',eq='1')),
            sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]

# ---------------- JS comum às duas telas (regras do talhão, campos condicionais, cenário salvo) ----------------
TALJS=r'''
const TOL=0.01, NOVA_FAZ=__NOVA__, CKEY='talhao-os-cd01-v1';
function r1(n){ return Math.round(Number(n)*10)/10; }
function sgn(n,d){ return (n>0?'+':(n<0?'−':''))+nf(Math.abs(n),d); }
function precisaMotivo(d){ const a=g2num(d.decl), c=g2num(d.calc); return !isNaN(a)&&a>0&&!isNaN(c)&&Math.abs(c-a)/a>TOL; }
function difInfo(V){ const a=Number(V.decl)||0; if(!isnum(V.calc)||!a) return null; const c=Number(V.calc); return {d:r1(c-a),pct:Math.abs(c-a)/a,fora:Math.abs(c-a)/a>TOL}; }
// geometria do KML (Lagoa Grande): círculo calculado pelo centro e pela área declarada; não é polígono validado nem pendência
function circ(V){ return V.geo==='circ'&&!isnum(V.calc); }
// campos que só aparecem sob condição diferente de igualdade (a cond do motor aceita só "igual a")
// fazenda cujos pivôs ainda não estão em Máquinas, instalações e setores: o campo do setor não aparece (nem é exigido)
const SEM_SETOR=['Lagoa Grande'];
const CXF={posse3:d=>!!d.posse&&d.posse!=='Própria', irrig:d=>!!d.sis&&d.sis!=='Sequeiro'&&SEM_SETOR.indexOf(d.faz)<0, motivo:d=>precisaMotivo(d)};
const CX={g_faz:{arrend:'posse3',fim:'posse3',custo:'posse3'},g_tal:{setor:'irrig',motivo:'motivo'},g_idt:{setor:'irrig',motivo:'motivo'}};
const CXMSG={arrend:'Informe o arrendador ou parceiro.',fim:'Informe o fim do contrato.',custo:'Informe o custo da terra.',setor:'Escolha o pivô ou setor que irriga o talhão.'};
function cxVis(gid,k,d){ const c=(CX[gid]||{})[k]; return !c||CXF[c](d||{}); }
function cxForm(self,v,gid){ const F=v[gid+'_F']; const fm=g2st(self,gid).fm; if(!F||!F.open||!F.fields||!fm||!fm.draft) return; const pre='fx_'+gid+'_';
  const oc=fm.isNew?(NOVO_OCULTO[gid]||[]):[]; if(fm.isNew&&SUB_NOVO[gid]) F.sub=SUB_NOVO[gid];
  F.fields=F.fields.filter(f=>{ const k=f.fid.slice(pre.length); return cxVis(gid,k,fm.draft)&&oc.indexOf(k)<0; });
  F.fields.forEach(f=>{ if(f.isSel&&!f.dis&&!f.v&&!f.opts.some(o=>o.v==='')) f.opts=[{v:'',t:'Escolha…'}].concat(f.opts); }); }
function cxCampo(v,gid,k){ const F=v[gid+'_F']; return ((F&&F.fields)||[]).find(f=>f.fid==='fx_'+gid+'_'+k); }
function cxLimpa(gid,r){ Object.keys(CX[gid]||{}).forEach(k=>{ if(!cxVis(gid,k,r.v)){ r.v[k]=''; if(r.s) r.s[k]=''; } }); }
function draftSet(self,gid,patch){ const cur=g2st(self,gid).fm; if(!cur) return; const er=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>{ delete er[k]; });
  g2set(self,gid,{fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,patch),errs:er,warn:false})}); }
// validação: campos escondidos não validam nem gravam valor antigo; o que foi digitado fica no formulário quando há erro
function valida2(self,v,gid,fn){ const F=v[gid+'_F']; if(!F||!F.open||!F.edit) return; const sp=GR(gid);
  F.save=()=>{ const fm0=g2st(self,gid).fm; if(!fm0) return; const dr=Object.assign({},fm0.draft);
    Object.keys(CX[gid]||{}).forEach(k=>{ if(!cxVis(gid,k,dr)) dr[k]=''; });
    const fm=Object.assign({},fm0,{draft:dr}); const e=Object.assign(basic(sp,fm),fn(dr,fm)||{});
    Object.keys(CX[gid]||{}).forEach(k=>{ if(!cxVis(gid,k,dr)) delete e[k]; else if(!String(dr[k]||'').trim()&&!e[k]&&CXMSG[k]) e[k]=CXMSG[k]; });
    if(Object.keys(e).length){ g2set(self,gid,{fm:Object.assign({},fm0,{errs:e,warn:false})}); return; }
    g2set(self,gid,{fm:fm}); g2save(self,sp); }; }
// regras do talhão (lista e detalhe). ctx: {tals:[linhas], fazs:[linhas], aloc:{id:{safra:ha}}}
function talErros(d,fm,ctx){ const e={}; const id=fm.rid; const nome=String(d.t||'').trim(); const out=ctx.tals.filter(r=>r.id!==id);
  const fz=ctx.fazs.find(f=>f.v.nome===d.faz); const al=(id&&ctx.aloc[id])||{}; const comParc=Object.keys(al).filter(s=>al[s]>0);
  const antes=id?ctx.tals.find(r=>r.id===id):null;
  // PLAT-01 R12: assinatura inadimplente não amplia a área medida (talhão novo ou reativado); editar o existente segue (defesa ao gravar)
  const tv=(typeof assinTrava==='function'&&d.sit!=='Inativo'&&(!id||(antes&&antes.v.sit==='Inativo')))?assinTrava('ampliar_area'):''; if(tv){ if(id) e.sit=tv; else e.t=tv; }
  if(!d.faz||d.faz===NOVA_FAZ) e.faz='Escolha a fazenda.';
  // parcelas de safra aberta pertencem à fazenda da safra: o talhão só muda de fazenda depois de tirá-las no Planejar safra
  else if(antes&&antes.v.faz&&d.faz!==antes.v.faz&&comParc.length) e.faz=(nome||'O talhão')+' tem parcelas na '+comParc.join(' e na ')+' da '+antes.v.faz+'. Tire-as no Planejar safra antes de mudar de fazenda.';
  else if(d.sit!=='Inativo'&&fz&&fz.v.sit==='Inativa') e.faz='A '+d.faz+' está inativa: reative a fazenda ou escolha outra.';
  if(nome&&out.some(r=>r.v.faz===d.faz&&String(r.v.t).trim().toLowerCase()===nome.toLowerCase())) e.t='Já existe '+nome+' na '+d.faz+'.';
  if(d.sis!=='Sequeiro'&&d.setor){ const piv=d.setor.indexOf('Pivô')>=0;
    if(d.sis==='Pivô central'&&!piv) e.setor='Escolha a bomba de um pivô.';
    else if(d.sis==='Gotejo'&&piv) e.setor='Escolha um setor de gotejo.';
    else if(d.sis==='Pivô central'&&d.sit!=='Inativo'){ const o=out.find(r=>r.v.sis==='Pivô central'&&r.v.setor===d.setor&&r.v.sit!=='Inativo'); if(o) e.setor=d.setor+' já irriga o '+o.v.t+' ('+o.v.faz+').'; } }
  const a=g2num(d.decl);
  if(!isNaN(a)){ const pior=Object.keys(al).filter(s=>al[s]>a+0.005)[0];
    if(pior) e.decl='As parcelas da '+pior+' somam '+nfa(al[pior])+' ha; reduza-as no Planejar safra antes.';
    else if(fz&&d.sit!=='Inativo'&&isnum(fz.v.area)){ const soma=r1(out.filter(r=>r.v.faz===d.faz&&r.v.sit!=='Inativo').reduce((s,r)=>s+(Number(r.v.decl)||0),0)+a);
      if(soma>Number(fz.v.area)+0.005) e.decl='Os talhões ativos da '+d.faz+' somariam '+nfa(soma)+' ha; a fazenda tem '+nfa(fz.v.area)+' ha.'; }
    if(precisaMotivo(d)&&!d.motivo){ const c=g2num(d.calc); e.motivo='Diferença de '+nf(Math.abs(c-a)/a*100,1)+' % entre área cultivável e polígono: informe o motivo.'; } }
  if(d.sit==='Inativo'&&id&&comParc.length) e.sit=(nome||'O talhão')+' tem parcelas na '+comParc.join(' e na ')+'. Tire-as no Planejar safra antes de inativar.';
  return e; }
function talToast(r,sit0){ return r.v.sit==='Inativo'?(r.v.t+' inativo: sai do Planejar safra e do Mapa; safras e O.S. antigas seguem consultáveis.')
  :(sit0==='Inativo'?(r.v.t+' reativado: volta ao Planejar safra e ao Mapa.'):('Salvo: '+r.v.t+' · '+r.v.faz+'.')); }
function cadLer(){ try{ const s=localStorage.getItem(CKEY); return s?JSON.parse(s):null; }catch(e){ return null; } }
function cadGravar(patch){ try{ const cur=cadLer()||{}; localStorage.setItem(CKEY,JSON.stringify(Object.assign(cur,patch))); }catch(e){} }
function linhaPk(r){ return {id:r.id,v:Object.assign({},r.v)}; }
function chipSt(c){ const cc=G2C[c]||G2C.gray; return ['display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';',
  'width:6px;height:6px;border-radius:999px;background:'+cc[0]+';']; }
'''.replace('__NOVA__',json.dumps(NOVA_FAZ,ensure_ascii=False)+', SUB_NOVO='+json.dumps(SUB_NOVO,ensure_ascii=False)+', NOVO_OCULTO='+json.dumps(NOVO_OCULTO))

def _chip_dyn(p):
    """chip de estado no cabeçalho, com texto e cor vindos do estado da tela."""
    return f'<span style="{H(p+"_stst")}"><span style="{H(p+"_stdot")}"></span>{H(p+"_st")}</span>'
def _injeta(fname,titulo,html):
    """põe o conteúdo dinâmico logo depois do título h1 do cabeçalho (o shell só aceita estado fixo)."""
    p=os.path.join(E.P,fname); s=open(p).read(); alvo=f'>{esc(titulo)}</h1>'
    assert s.count(alvo)==1, (fname,alvo)
    open(p,'w').write(s.replace(alvo,alvo+html,1))
def _rolagem(fname):
    """o conteúdo cresce com cada fazenda, talhão ou versão cadastrada: o corpo rola dentro do artboard em vez de ser cortado
    pelo overflow: clip da altura fixa (mesmo padrão das telas de processo; pack37 expande main[data-scroll="1"] no PDF)."""
    p=os.path.join(E.P,fname); s=open(p).read()
    if '<main data-scroll="1"' in s: return   # a casca (ui37) já trava a tela na janela e rola só os dados em todas as telas
    alvo='<main data-scroll="0" style="flex-grow: 1; padding: 18px 32px 22px;  display: grid;'
    assert s.count(alvo)==1, (fname,'main')
    open(p,'w').write(s.replace(alvo,'<main data-scroll="1" style="flex-grow: 1; padding: 18px 32px 22px; overflow-y: auto; min-height: 0; display: grid;',1))

# ================= CD-01 · Fazendas, áreas e talhões =================
# CADUX (09/10/2026): mestre de fazendas (+ Todas) → detalhe da fazenda (cabeçalho, Próximo passo, abas Talhões · Ambiental · Água, mapa e
# grade sincronizados) → painel do talhão em consulta (o aside do _g2form, 820 px). "+ Criar talhão" no cabeçalho herda a fazenda escolhida.
GEO_MAPA=[('T1','poly','30,30 290,22 300,205 40,215'),('T2','poly','315,22 560,28 555,200 318,206'),
          ('T4','poly','40,250 300,240 305,430 45,438'),('T3','poly','320,240 555,236 560,430 325,434'),
          ('P1','circ','685,118,88'),('P2','circ','890,118,82'),
          ('T7','poly','590,245 780,240 785,430 595,434'),('C1','poly','800,240 970,236 975,430 805,434')]
MAPA_FID=next(f['id'] for f in DC.FAZENDAS if f['nome']=='Santa Rita')   # o mapa desenhado é desta fazenda (pelo id: sobrevive a renomear)
def _alvo_mapa(tid):
    """atributos de um talhão no mapa: cor pela situação, contorno de 6 px no aberto, um ponto de Tab no grupo (setas movem, Enter abre)."""
    return (f'fill="{H("mf_"+tid)}" stroke="{H("ms_"+tid)}" stroke-width="{H("mw_"+tid)}" role="button" tabIndex="{H("mt_"+tid)}" aria-label="{H("ml_"+tid)}" '
            f'data-tid="{tid}" onClick="{H("mc_"+tid)}" style="cursor: pointer;"')
def _mapa_sr():
    """mapa da Santa Rita (desenho, sem satélite nem rede) colorido pela situação; tocar no talhão abre o painel dele."""
    g=[]
    for tid,tp,geo in GEO_MAPA:
        if tp=='poly':
            pts=[tuple(map(float,p.split(','))) for p in geo.split()]; cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            g.append(f'<polygon points="{geo}" {_alvo_mapa(tid)}/>')
        else:
            cx,cy,r=map(float,geo.split(',')); g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {_alvo_mapa(tid)}/>')
        g.append(f'<text x="{cx}" y="{cy+11}" text-anchor="middle" pointer-events="none" font-family="Sora, Manrope, sans-serif" font-size="32" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="5" paint-order="stroke">{tid}</text>')
    return (f'<svg viewBox="0 0 1000 460" width="{H("cd_mzw")}" preserveAspectRatio="xMidYMid meet" style="display: block; background: #DDE5D4; border-radius: 12px; max-height: {H("cd_mzh")};">'
            '<rect x="0" y="0" width="1000" height="460" fill="#DDE5D4"/><path d="M0 225 C 250 219, 520 231, 1000 225" stroke="#B9C6AE" stroke-width="10" fill="none"/>'+''.join(g)+'</svg>')
def _proj_lg():
    """projeção local (metros) dos pivôs da Lagoa Grande no SVG; o JS usa a mesma para os contornos desenhados ou importados no IN-04."""
    import math
    pv=DC.LG_PIVOS; lat0=sum(p[4] for p in pv)/len(pv); kx=111320*math.cos(math.radians(lat0)); ky=110540
    pts=[(p[0],p[3]*kx,-p[4]*ky,p[5]) for p in pv]
    x0=min(x-r for _,x,y,r in pts); x1=max(x+r for _,x,y,r in pts); y0=min(y-r for _,x,y,r in pts); y1=max(y+r for _,x,y,r in pts)
    pad=120; VW=1000; sc=VW/(x1-x0+2*pad); VH=round((y1-y0+2*pad)*sc)
    return dict(kx=kx,ky=ky,x0=x0,y0=y0,pad=pad,sc=sc,VW=VW,VH=VH),pts
def _mapa_lg():
    """pivôs da Lagoa Grande na posição do KML (círculo pelo centro e pela área declarada) e, por cima, os contornos que o IN-04 gravou no mesmo
    cadastro (talhao-os-cd01-v1, chave geom): uma só fonte de geometria (R18)."""
    P,pts=_proj_lg(); g=[]
    for pid,x,y,r in pts:
        cx=round((x-P['x0']+P['pad'])*P['sc'],1); cy=round((y-P['y0']+P['pad'])*P['sc'],1); rr=round(r*P['sc'],1)
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" {_alvo_mapa(pid)}/>')
        g.append(f'<text x="{cx}" y="{round(cy+7,1)}" text-anchor="middle" pointer-events="none" font-family="Sora, Manrope, sans-serif" font-size="{20 if rr>30 else 15}" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="4" paint-order="stroke">{pid}</text>')
    tu=(f'<sc-for list="{H("cd_mtu")}" as="u" hint-placeholder-count="0"><polygon points="{H("u.pts")}" fill="{H("u.f")}" stroke="{H("u.s")}" stroke-width="{H("u.w")}" role="button" '
        f'tabIndex="{H("u.tab")}" aria-label="{H("u.lab")}" data-tid="{H("u.id")}" onClick="{H("u.go")}" style="cursor: pointer;"/></sc-for>')
    return (f'<svg viewBox="0 0 {P["VW"]} {P["VH"]}" width="{H("cd_mzw")}" preserveAspectRatio="xMidYMid meet" style="display: block; background: #DDE5D4; border-radius: 12px; max-height: {H("cd_mzh")};">'
            f'<rect x="0" y="0" width="{P["VW"]}" height="{P["VH"]}" fill="#DDE5D4"/>'+''.join(g)+tu+'</svg>')
def _mapa_html():
    """mapa da fazenda escolhida acima da grade (computador) ou no lugar dela (celular, "Mapa"); um grupo com nome e um só ponto de Tab."""
    zb=f'width: 32px; height: 32px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; font-size: 17px; font-weight: 700; color: {INK}; cursor: pointer; font-family: inherit;'
    leg=lambda itens: ' · '.join(f'<span style="color: {c}; font-weight: 700;">■ {esc(t)}</span>' for c,t in itens)
    return (se('cd_mapa_on',f'<div class="cd-mapa" role="group" aria-label="{H("cd_mapaLab")}" onKeyDown="{H("cd_mkey")}">'
            f'<div class="cd-mapa-zoom" role="group" aria-label="Aproximar ou afastar o mapa"><button type="button" aria-label="Aproximar o mapa" onClick="{H("cd_zin")}" style="{zb}">+</button>'
            f'<button type="button" aria-label="Afastar o mapa" onClick="{H("cd_zout")}" style="{zb}">−</button></div>'
            f'<div class="cd-mapa-caixa">'+se('cd_mapa_sr',_mapa_sr())+se('cd_mapa_lg',_mapa_lg())+'</div>'
            + se('cd_mapa_sr',f'<div class="cd-mapa-leg">{leg([("#1E7A4C","polígono validado"),("#8A5A00","diferença sem motivo"),("#5B6660","inativo")])}</div>')
            + se('cd_mapa_lg',f'<div class="cd-mapa-leg">{leg([("#4F7A55","círculo do KML (centro e área declarada)"),("#1E7A4C","polígono validado"),("#5B6660","inativo")])}</div>')
            + '</div>')
            + se('cd_semgeo',f'<p class="cd-mapa-sem">{H("cd_semgeoT")}</p>')
            + se('cd_temFora',f'<div class="cd-fora" role="group" aria-label="Talhões fora do mapa"><span>Fora do mapa:</span><sc-for list="{H("cd_fora")}" as="x" hint-placeholder-count="1">'
                 f'<button type="button" onClick="{H("x.go")}" style="{_MINI}">{H("x.t")}</button></sc-for></div>'))
CD01_CSS=(".cd-tal{display:flex;flex-direction:column;flex:1 1 0;min-height:0}.cd-tal .g2caixa{display:contents}.cd-tal .g2caixa>div:first-child{order:-2}"
          ".cd-tal .cd-mapa-bloco{order:-1}.cd-mapa{position:relative;padding:10px 16px 6px}.cd-mapa-caixa{overflow:auto;max-height:260px;border-radius:12px;touch-action:pan-x pan-y pinch-zoom}"
          ".cd-mapa-zoom{position:absolute;right:24px;top:18px;z-index:2;display:flex;flex-direction:column;gap:6px}.cd-mapa-leg{font-size:11.5px;color:#65736A;padding:6px 2px 0}"
          ".cd-mapa-sem{margin:10px 16px 0;font-size:13px;color:#4B5A51}.cd-fora{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:6px 16px 8px;font-size:12.5px;color:#4B5A51;font-weight:700}"
          ".cd-vis{display:inline-flex}.cd-so-estreita{display:none}@media (max-width:1023px){.cd-so-larga{display:none!important}.cd-so-estreita{display:inline-flex}.cd-mapa-caixa{max-height:none}}"
          "svg [data-tid]:focus-visible{outline:none;stroke:#15201A;stroke-width:5px;stroke-dasharray:8 4}")

def _parc_open():
    """parcelas das safras abertas, por talhão (pelo id) e só da fazenda da safra: Santa Rita 2026/27 e Safrinha 2027; Lagoa Grande Mamão 2026/27."""
    import dados_lagoa_safra as DL
    out={}
    for s in SAF_ABERTAS:
        for c in D2.CULTIVOS[s['id']]:
            tid=DL.PID_DE.get(c['local']) if s.get('fazenda')=='Lagoa Grande' else _tal_de(c['local'])
            if not tid: continue
            out.setdefault(tid,[]).append(dict(sid=s['id'],safra=s['nome'],local=c['local'],tipo=c['tipo'],cult=c['cultura'],var=c['variedade'],area=c['area'],plantio=c['plantio'],cid=c['id']))
    return out
def cd01():
    fname='CD-01.dc.html'; E._reset_screen(fname)
    fr=_faz_rows(); tr=_tal_rows(); nome={r['id']:r['v']['nome'] for r in fr}
    grupos=[dict(id='F_'+fid,ro=True,v=dict(t=n,fid=fid),s={},p={},kids=[t for t in tr if t['v']['faz']==n]) for fid,n in nome.items()]
    # fazenda: fonte do mestre e da ficha (painel em consulta; "Editar fazenda" abre o formulário de hoje)
    grid([dict(k='nome',l='Fazenda',w=220),dict(k='area',l='Área total',t='num',a='r',un='ha',d=0)],
        fr,gid='g_faz',total=False,search=False,
        edit=dict(m='form',title='Fazenda',newTitle='Criar fazenda',sub=SUB_FAZ,fields=CAMPOS_FAZ))
    # talhões: Identificação | Situação | dados (≤ 7 colunas, uma variável por coluna, unidade na célula). Com uma fazenda escolhida a grade é a
    # lista dela (G2DISP); em "Todas", a árvore de hoje com subtotal por fazenda. A linha tem um alvo único que abre o painel (BOT-07)
    gt=grid(COLS_TAL,grupos,gid='g_tal',tree=True,search=False,total=False,frame=False,x0={g['id']:True for g in grupos},
        tools=(f'<span class="cmd-conta">{H("cd_conta")}</span>'+qf_chips('g_tal')
               + f'<span class="cd-so-larga">'+se('cd_temMapa',f'<button type="button" class="g2lk" onClick="{H("cd_mtog")}">{H("cd_mtogT")}</button>')+'</span>'
               + f'<span class="cd-so-estreita">'+se('cd_temMapa',seg('cdv',['Lista','Mapa'],'Visualização dos talhões'))+'</span>'),
        edit=dict(m='form',title='Talhão',newTitle='Criar talhão',leafOnly=True,sub=SUB_TAL,fields=campos_tal(list(nome.values())+[NOVA_FAZ]),alvo='talhão'))
    acoes_form('g_tal'); acoes_form('g_faz'); cadx_css(); md_css(); E.EXTRA.append('<style>'+CD01_CSS+'</style>')
    # restrição ambiental e recursos hídricos (do CAR e do KML da fazenda): consulta com a origem; não viram talhão nem se criam aqui (R15)
    tot={g:a for g,t,a,tt in DC.LG_AMBIENTAL if tt}
    amb_rows=[R(f'am{i}',dict(tema=t,faz='Lagoa Grande',tipo=g,area=a,total='Sim' if tt else '',car=DC.LG_PERIMETROS[0]['car']))
              for i,(g,t,a,tt) in enumerate(sorted(DC.LG_AMBIENTAL,key=lambda x:(x[0]!='Reserva legal',not x[3],-x[2])),1)]
    for r in amb_rows: r['o']=[dict(t=f"CAR {r['v']['car']} · {DC.LG_FONTE}")]
    ga=grid(COLS_AMB,amb_rows,gid='g_amb',total=False,frame=False,search=False,qf=dict(k='tipo',todas='Todos'),
        tools=f'<span class="cmd-conta">{H("cd_contaAmb")}</span><span style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("cd_ambNota")}</span>',
        edit=dict(m='origin',title='Área ambiental',alvo='área ambiental',fields=[txt('tema','Tema do CAR',ro=True),txt('faz','Fazenda',ro=True),txt('tipo','Tipo',ro=True),
                                                           num('area','Área','ha',ro=True),txt('car','Recibo do CAR',ro=True)]))
    ag_rows=[R(a['id'],dict(nome=a['nome'],faz='Lagoa Grande',tipo=a['tipo'],doc=_doc_agua(a['tipo']),num=a['num'],proc=a['proc'],modo=a['modo'],curso=a['curso'],vazao=a['vazao'],
                           vazn=_vazao_m3h(a['vazao']),regime=a['regime'],fin=a['fin'],venc=a['venc'],renov=a['renov'],desc=a['desc'],coord=f"{a['lat']:.6f}; {a['lon']:.6f}".replace('.',','))) for a in DC.LG_AGUA]
    for r in ag_rows: r['o']=[dict(t=DC.LG_FONTE)]
    gw=grid(COLS_AGUA,ag_rows,gid='g_agua',total=False,frame=False,search=False,tools=f'<span class="cmd-conta">{H("cd_contaAgua")}</span>'+qf_chips('g_agua'),
        edit=dict(m='origin',title='Ponto de água',alvo='ponto de água',fields=[txt('nome','Nome no KML',ro=True),txt('tipo','Documento',ro=True),txt('num','Número',ro=True),
            txt('proc','Processo',ro=True),txt('modo','Modo de uso',ro=True),txt('curso','Curso d’água',ro=True),txt('vazao','Vazão',ro=True),txt('regime','Regime',ro=True),
            txt('fin','Finalidade',ro=True),dat('venc','Vencimento',ro=True),txt('renov','Processo de renovação',ro=True),txt('coord','Coordenadas (latitude; longitude)',ro=True),
            dict(k='desc',l='Descrição no KML',t='area',ro=True)]))
    p0=f'<div class="cd-tal"><div class="cd-mapa-bloco">{_mapa_html()}</div>'+vazio('cd_vt')+se('cd_lista_on',arv(gt),True)+'</div>'
    det=(det_cab()+f'<div class="cadx-topo">{abas("cdt",["Talhões","Ambiental","Água"],"Cadastros da fazenda")}</div>'
         + f'<div class="cadx-dados">{pane("cdt",0,p0)+pane("cdt",1,vazio("cd_va")+ga)+pane("cdt",2,vazio("cd_vg")+gw)}</div>')
    corpo=md(mestre('Fazendas','Buscar fazenda ou talhão',secbtn('cd_nfaz','+ Criar fazenda')),det,'Fazendas, áreas e talhões')
    P,_=_proj_lg()
    js({},
       TALJS+'const FUSO_UF='+json.dumps(DC.FUSO_UF,ensure_ascii=False)+', FUSO_PAD='+json.dumps(DC.FUSOS[0],ensure_ascii=False)
       +', ALOC='+json.dumps(_aloc(),ensure_ascii=False)+', PARC='+json.dumps(_parc_open(),ensure_ascii=False)+', MAPA='+json.dumps([g[0] for g in GEO_MAPA])
       +', MAPA_FID='+json.dumps(MAPA_FID)+', MAPA_LG='+json.dumps([p[0] for p in DC.LG_PIVOS])+', LG_SINT='+json.dumps(__import__('dados_lagoa_fonte').ROTULO,ensure_ascii=False)
       +', LGP='+json.dumps(P)+', SAFOPEN='+json.dumps([dict(sid=s['id'],nome=s['nome'],faz=s['fazenda']) for s in SAF_ABERTAS],ensure_ascii=False)
       +', COLS_TAL='+json.dumps([E._col_un(c) for c in COLS_TAL],ensure_ascii=False)
       +', COLS_AMB='+json.dumps([E._col_un(c) for c in COLS_AMB],ensure_ascii=False)+', COLS_AGUA='+json.dumps([E._col_un(c) for c in COLS_AGUA],ensure_ascii=False)+';\n'+CD01JS)
    # tela sem rolagem de página: só a área de dados rola (a prancheta tem a altura da janela)
    ui37.H_OVR.pop(fname,None); HEIGHTS37[fname]=1000
    shell37('CD-01','Fazendas, áreas e talhões',corpo,fname=fname,status=None,primary_html=criar_cab('cd_criar','+ Criar talhão'),search=False)
    estado_cab(fname,'Fazendas, áreas e talhões','cd'); _rolagem(fname)
    ncol_dinamico(fname,['cd_nctal','cd_ncamb','cd_ncagua'])
COLS_TAL=[dict(k='t',l='Talhão',w=170),dict(k='est',l='Situação',w=190),dict(k='sis',l='Sistema',w=120),dict(k='decl',l='Área cultivável',t='num',a='r',un='ha',d=1),
          dict(k='calc',l='Polígono',t='num',a='r',un='ha',d=1),dict(k='difp',l='Diferença',t='num',a='r',un='%',d=1),dict(k='parc',l='Parcelas',t='num',a='r',multi=True)]
COLS_AMB=[dict(k='tema',l='Área ambiental',w=420),dict(k='tipo',l='Tipo'),dict(k='area',l='Área',t='num',a='r',un='ha',d=2),dict(k='faz',l='Fazenda')]
COLS_AGUA=[dict(k='nome',l='Ponto de água',w=210),dict(k='est',l='Situação',w=170),dict(k='doc',l='Documento'),dict(k='modo',l='Uso',w=160),
           dict(k='vazn',l='Vazão',t='num',a='r'),dict(k='venc',l='Vencimento',t='date'),dict(k='faz',l='Fazenda')]
CD01JS=r'''
function tals(rows){ const o=[]; rows.forEach(g=>{ if(g.kids) g.kids.forEach(k=>o.push(k)); else o.push(g); }); return o; }
function arvore(fz,ts){ const gs=fz.map(f=>({id:'F_'+f.id,ro:true,v:{t:f.v.nome,fid:f.id},s:{},p:{},kids:[]}));
  ts.forEach(t=>{ let g=gs.find(x=>x.v.t===t.v.faz); if(!g){ g={id:'F_'+t.v.faz,ro:true,v:{t:t.v.faz,fid:''},s:{},p:{},kids:[]}; gs.push(g); } g.kids.push(t); }); return gs; }
// fazendas e talhões salvos (nesta tela, no detalhe do talhão ou no Mapa IN-04) voltam ao abrir a tela
function cadIni(self){ if(self._ini) return; self._ini=1; const st=cadLer(); if(!st||!st.faz||!st.tal) return;
  const fz=st.faz.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}})); const tl=st.tal.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}}));
  GR('g_faz').rows.forEach(r=>{ if(!fz.some(x=>x.id===r.id)) fz.push({id:r.id,v:Object.assign({},r.v),s:{},p:{}}); });
  tals(GR('g_tal').rows).forEach(r=>{ if(!tl.some(x=>x.id===r.id)) tl.push({id:r.id,v:Object.assign({},r.v),s:{},p:{}}); });
  const gs=arvore(fz,tl);
  GR('g_faz').rows=fz; GR('g_tal').rows=gs; const x0={}; gs.forEach(g=>{ x0[g.id]=true; }); GR('g_tal').x0=x0; }
function cadSalvar(self){ cadGravar({faz:RW(self,'g_faz').map(linhaPk),tal:tals(RW(self,'g_tal')).map(linhaPk)}); }
// situação do talhão: um só cálculo para a linha (chip, sem verbo: o verbo fica uma vez, no painel), o filtro "A resolver", o mestre e o cabeçalho
function talSit(r){ const V=r.v;
  if(V.sit==='Inativo') return {t:'Inativo',p:[chipc('Inativo','gray')]};
  if(circ(V)) return {t:'Círculo do KML',p:sitInfo('Círculo do KML')};
  if(!isnum(V.calc)) return {t:'Sem polígono',p:sitX('Sem polígono','yellow'),res:'sem'};
  const di=difInfo(V); if(di&&di.fora&&!V.motivo) return {t:'Diferença sem motivo',p:sitX('Diferença sem motivo','yellow'),res:'mot'};
  return {t:'Em dia',p:sitOk('Em dia')}; }
function fazDocs(V){ return [!V.empresa?'empresa':'',!V.car?'CAR':'',!V.matr?'matrícula':'',!V.posse?'posse':''].filter(Boolean); }
// ponto de água (outorga ou certidão): vigente, a vencer em 90 dias, vencido ou em renovação; sem descrição no KML não tem situação.
// A linha mostra só o estado (chip); o que fazer fica no Próximo passo da fazenda (regra 3 da CADUX; BOT-07)
function aguaSit(V){ if(!V.tipo) return {t:'Sem descrição no KML',p:sitInfo('Sem descrição no KML')};
  if(V.renov) return {t:'Em renovação',p:[chipc('Em renovação','yellow')],res:'ren'};
  if(V.venc&&V.venc<HOJE) return {t:'Vencida',p:sitX('Vencida','red'),res:'venc'};
  if(V.venc&&ddiff(HOJE,V.venc)<=90) return {t:'Vence em 90 dias',p:sitX('Vence em 90 dias','yellow'),res:'avenc'};
  return {t:'Vigente',p:sitOk('Vigente')}; }
function aguaNome(V){ return /^\d+$/.test(String(V.nome))?'Ponto '+V.nome:V.nome; }
// documento pelo tipo gravado ("Outorga" ou "Certidão de uso insignificante"): outorga não aparece como certidão
function aguaDoc(V){ return !V.tipo?'':((/^Outorga/.test(V.tipo)?'Outorga ':'Certidão ')+V.num); }
function fazPend(V){ return V.sit!=='Inativa'&&(fazDocs(V).length>0||!!V.pend); }
function lista(a){ return a.length<2?(a[0]||''):a.slice(0,-1).join(', ')+' e '+a[a.length-1]; }
// as ações do talhão e da fazenda ficam no painel em consulta (Próximo passo e Editar); o formulário não repete atalhos (uma porta por efeito)
CAD_ACTS.g_tal=()=>[]; CAD_ACTS.g_faz=()=>[];
// ===== CADUX · mestre de fazendas → detalhe da fazenda → painel do talhão =====
const CD_ABAS=['talhoes','ambiental','agua'];
// IN-04 desenha e importa só no mapa real (hoje, a Lagoa Grande): a porta só aparece onde ele abre o mapa da fazenda do talhão (R18)
function in04(nome){ return nome==='Lagoa Grande'; }
function cdSel(self){ const s=self.state.mx_sel; return (s===undefined||s===null)?'':s; }
function cdFaz(self,id){ return id?RW(self,'g_faz').find(f=>f.id===id)||null:null; }
function cdFazDeTal(self,t){ return RW(self,'g_faz').find(f=>f.v.nome===t.v.faz)||null; }
function cdTalsDe(self,nome,todos){ return tals(RW(self,'g_tal')).filter(t=>t.v.faz===nome&&(todos||t.v.sit!=='Inativo')); }
// busca da tela: nome, sistema, pivô ou setor, tema, documento e o nome da fazenda (o pai), sem acento nem caixa (regra 11)
function cdCasa(r,q){ if(!q) return true; const V=r.v||{}; const h=g2norm([V.t,V.faz,V.sis,V.setor,V.nome,V.tema,V.tipo,V.doc,V.num,V.curso,V.modo].filter(Boolean).join(' '));
  return g2norm(q).split(/\s+/).filter(Boolean).every(w=>h.indexOf(w)>=0); }
function cdGeomU(){ const st=cadLer()||{}; return st.geom||{}; }
function cdAba(self,i){ cadIrAba(self,'cd_aba',i,CD_ABAS[i]); }
// pendências da fazenda na ordem da regra 4: bloqueio legal → falta que impede usar a fazenda → documento ou dado; s = forma curta do "e mais"
function cdPends(self,f){ const V=f.v; const ts=cdTalsDe(self,V.nome); const ag=RW(self,'g_agua').filter(r=>r.v.faz===V.nome);
  const vc=ag.filter(r=>aguaSit(r.v).res==='venc'), rn=ag.filter(r=>aguaSit(r.v).res==='ren'), av=ag.filter(r=>aguaSit(r.v).res==='avenc'); const out=[];
  const abrirAgua=()=>{ self.setState({cd_qfa:'res'}); cdAba(self,2); };
  const outras=[rn.length?rn.length+' em renovação':'',av.length?av.length+(av.length>1?' vencem':' vence')+' em 90 dias':''].filter(Boolean);
  if(vc.length){ const s=vc.length+(vc.length>1?' outorgas vencidas':' outorga vencida');
    out.push({n:0,cor:'red',t:s+': captação sem outorga válida',quem:'Resolve o gestor, no órgão ambiental'+(outras.length?'. Também '+lista(outras)+'.':'.'),lks:[{t:'Abrir pontos de água a resolver',go:abrirAgua}],s:s}); }
  else if(outras.length) out.push({n:0,cor:'yellow',t:'Outorga a renovar: '+lista(outras),quem:'Resolve o gestor, no órgão ambiental.',lks:[{t:'Abrir pontos de água a resolver',go:abrirAgua}],s:'outorga a renovar'});
  if(!ts.length&&V.sit!=='Inativa') out.push({n:1,cor:'gray',t:'A '+V.nome+' não tem talhão. Crie o 1º em + Criar talhão, no topo'+(in04(V.nome)?', ou importe do KML.':'.'),
    lks:in04(V.nome)?[{t:'Importar talhões do KML',h:'IN-04.dc.html#importar'}]:[],s:'sem talhão'});
  const falta=fazDocs(V); const ed=(k)=>()=>g2editar(self,GR('g_faz'),f.id,k);
  if(falta.indexOf('CAR')>=0) out.push({n:2,cor:'yellow',t:'CAR em branco: bloqueia só o crédito rural.',prim:{t:'Informar CAR',go:ed('car')},s:'CAR em branco'});
  const fo=falta.filter(x=>x!=='CAR'); const fk={empresa:'empresa','matrícula':'matr',posse:'posse'};
  if(fo.length) out.push({n:2,cor:'yellow',t:'Cadastro da fazenda incompleto: falta '+lista(fo)+'.',prim:{t:'Completar cadastro',go:ed(fk[fo[0]])},s:'cadastro da fazenda incompleto ('+lista(fo)+')'});
  if(V.pend) out.push({n:2,cor:'yellow',t:V.pend+'.',prim:{t:'Resolver documento',go:ed('pend')},s:V.pend.charAt(0).toLowerCase()+V.pend.slice(1)});
  const tr=ts.filter(t=>talSit(t).res);
  if(tr.length){ const s=tr.length===1?(tr[0].v.t+' '+talSit(tr[0]).t.toLowerCase()):(tr.length+' talhões a resolver');
    out.push({n:2,cor:'yellow',t:s+'.',lks:[tr.length===1?{t:'Abrir o '+tr[0].v.t,go:()=>g2open(self,GR('g_tal'),tr[0].id,null)}:{t:'Abrir talhões a resolver',go:()=>{ self.setState({cd_qf:'res'}); cdAba(self,0); }}],s:s}); }
  return out.sort((a,b)=>a.n-b.n); }
// "N a resolver" conta cada pendência de documento da fazenda como o Próximo passo lista (CAR; cadastro incompleto; pendência do documento),
// mais os talhões e os pontos de água a resolver (achado 10 da revisão: a Boa Vista dizia 2 e o Próximo passo listava 3)
function fazNpend(V){ if(V.sit==='Inativa') return 0; const f=fazDocs(V); return (f.indexOf('CAR')>=0?1:0)+(f.some(x=>x!=='CAR')?1:0)+(V.pend?1:0); }
function cdNres(self,f){ const V=f.v; if(V.sit==='Inativa') return 0; return fazNpend(V)+cdTalsDe(self,V.nome).filter(t=>talSit(t).res).length
  +RW(self,'g_agua').filter(r=>r.v.faz===V.nome&&aguaSit(r.v).res).length; }
function cdProx(ps){ if(!ps.length) return {cor:'green',t:'Em dia: nada a resolver nesta fazenda.'}; const p=ps[0], r=ps.slice(1);
  return {cor:p.cor,t:p.t,quem:p.quem||'',prim:p.prim||null,lks:p.lks||[],mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
function cdEndObj(self,fid,tid){ const o={}; if(fid) o.faz=fid; if(tid) o.talhao=tid; const a=self.state.cd_aba||0; if(a) o.aba=CD_ABAS[a]; return o; }
// escolher no mestre só mostra (não muda dado nem o contexto das outras telas); abaixo de 1024 px abre um nível (o voltar sobe)
function cdEscolhe(self,id,o){ o=o||{}; const f=cdFaz(self,id); const larga=cadLarga(); const at=f?cdTalsDe(self,f.v.nome):tals(RW(self,'g_tal')).filter(t=>t.v.sit!=='Inativo');
  const n=f?cdNres(self,f):0;
  const an=(f?f.v.nome:'Todas as fazendas')+': '+at.length+(at.length===1?' talhão':' talhões')+(f?(' · '+(n?n+' a resolver':'Em dia')):'');
  self.setState({mx_sel:id,mx_nivel:'d',cd_ind:null,mx_anuncio:an,cd_mk:null,cd_zoom:1});
  if(!o.semEnd) cadHashPoe(self,cdEndObj(self,id,null),larga?null:'g');
  if(!larga) cadFoco('#dx-t',90); }
function cdVolta(self){ let st=null; try{ st=history.state; }catch(e){} self.setState({mx_nivel:'m'});
  if(st&&st.cadux==='g'){ self.__cadHash=''; try{ history.back(); }catch(e){} } else cadHashPoe(self,{});
  cadFoco('.cmd-lista .cmd-it[aria-current=true]',90); }
function cdCriar(self,d){ const tv=typeof assinTrava==='function'?assinTrava('ampliar_area'):''; if(tv){ self.setState({g2toast:tv}); return; }
  g2set(self,'g_tal',{fm:null}); g2new(self,GR('g_tal'),{draft:Object.assign({t:'',decl:'',setor:'',motivo:''},d||{})});
  setTimeout(()=>{ try{ const e=document.getElementById('fx_g_tal_t'); if(e) e.focus(); }catch(x){} },90); }
function cdAbreTal(self,tid){ const t=g2find(RW(self,'g_tal'),tid); if(!t) return; const f=cdFazDeTal(self,t);
  self.setState({mx_sel:f?f.id:'',mx_nivel:'d',mx_q:''}); cadKeepPoe('q',''); setTimeout(()=>g2open(self,GR('g_tal'),tid,null),0); }
// endereço (SEL-02): #faz= #talhao= (também tal= e reg=, da NAV) e aba=; o valor é o id. Registro indisponível: a lista, com aviso e saída
function cdAplica(self,o,pop,set){ set=set||(p=>self.setState(p)); const fz=RW(self,'g_faz'); const ts=tals(RW(self,'g_tal')); const larga=cadLarga();
  let tid=o.talhao||o.tal||''; let fid=o.faz||''; const reg=o.reg||''; let reescreve=!!(o.tal&&!o.talhao)||!!reg;
  if(reg&&!tid){ if(ts.some(t=>t.id===reg)) tid=reg; else if(fz.some(f=>f.id===reg)){ fid=reg; } else tid=reg; }
  const ab=CD_ABAS.indexOf(o.aba||''); const patch={cd_ind:null}; if(ab>=0) patch.cd_aba=ab; else if(pop) patch.cd_aba=0;
  const fmT=g2st(self,'g_tal').fm, fmF=g2st(self,'g_faz').fm;
  if(pop&&fmF) g2set(self,'g_faz',{fm:null});
  if(tid){ const t=ts.find(x=>x.id===tid);
    if(!t){ const fv=cdFaz(self,fid); patch.cd_ind={t:'Talhão “'+tid+'” indisponível: não existe neste cadastro ou não está liberado para o seu perfil. Nada foi aberto.'};
      patch.mx_sel=fv?fv.id:''; patch.mx_nivel=fv?'d':'m'; if(fmT) g2set(self,'g_tal',{fm:null}); set(patch); cadHashPoe(self,fv?{faz:fv.id}:{}); return; }
    const f=cdFazDeTal(self,t); patch.mx_sel=f?f.id:''; patch.mx_nivel='d'; patch.cd_aba=0; patch.cd_mk=tid; if(t.v.sit==='Inativo') patch.cd_qf='inat';
    // faz= diferente da do talhão: vale o talhão (o id é único) e o endereço é corrigido, com aviso visível (achado 13: não trocar de fazenda em silêncio)
    if(fid&&fid!==patch.mx_sel){ reescreve=true; const fv=cdFaz(self,fid); const m='O talhão “'+t.v.t+'” é da '+(f?f.v.nome:'outra fazenda')+(fv?', não da '+fv.v.nome+' pedida no endereço':'')+': a '+(f?f.v.nome:'fazenda dele')+' foi selecionada.';
      patch.cd_ind={t:m,info:true}; patch.g2toast=m; }
    set(patch); if(!fmT||fmT.rid!==tid) setTimeout(()=>g2open(self,GR('g_tal'),tid,null,{end:true}),0);
    if(reescreve) cadHashPoe(self,patch.mx_sel?{faz:patch.mx_sel,talhao:tid}:{talhao:tid}); return; }
  if(fmT&&pop) g2set(self,'g_tal',{fm:null});
  if(fid){ if(cdFaz(self,fid)){ patch.mx_sel=fid; patch.mx_nivel='d'; }
    else { patch.cd_ind={t:'Fazenda “'+fid+'” indisponível: não existe neste cadastro ou não está liberada para o seu perfil.'}; patch.mx_sel=''; patch.mx_nivel='m'; set(patch); cadHashPoe(self,{}); return; }
    if(reg){ set(patch); cadHashPoe(self,cdEndObj(self,fid,null)); return; } }   /* #reg=SR (X-REG da NAV) vira #faz=SR (§0.8) */
  else if(!pop){ const cx=cadCtxFaz(); const at=fz.filter(f=>f.v.sit!=='Inativa'); const fc=cx?at.find(f=>f.v.nome===cx):(at.length===1?at[0]:null);
    patch.mx_sel=fc?fc.id:''; patch.mx_nivel=fc?'d':'m'; }
  else { patch.mx_sel=larga?'':cdSel(self); patch.mx_nivel='m'; }
  set(patch); }
// alvo do toque no mapa menor que 24 px (WCAG 2.5.8): no toque, aproxima em vez de abrir; a lista é a alternativa
function cdMapaClique(self,e,id){ try{ const b=e&&e.currentTarget&&e.currentTarget.getBoundingClientRect(); const fino=window.matchMedia('(pointer: fine)').matches;
    if(b&&!fino&&Math.min(b.width,b.height)<24&&(self.state.cd_zoom||1)<4){ self.setState({cd_zoom:Math.min(4,(self.state.cd_zoom||1)+1),mx_anuncio:'Mapa aproximado: toque de novo no '+id+' para abrir.'}); return; } }catch(x){}
  g2open(self,GR('g_tal'),id,null); }
function cdMapaTecla(self,e){ const k=e.key; const el=[...document.querySelectorAll('.cd-mapa [data-tid]')].filter(x=>x.getClientRects().length&&x.getAttribute('stroke')!=='transparent');
  const i=el.indexOf(document.activeElement); if(i<0) return;
  if(k==='Enter'||k===' '){ e.preventDefault(); g2open(self,GR('g_tal'),el[i].getAttribute('data-tid'),null); return; }
  if(['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','Home','End'].indexOf(k)<0) return; e.preventDefault();
  const n=k==='Home'?0:(k==='End'?el.length-1:(i+((k==='ArrowRight'||k==='ArrowDown')?1:-1)+el.length)%el.length); el.forEach((x,j)=>x.setAttribute('tabindex',j===n?'0':'-1')); el[n].focus(); }
function cdProj(ring){ return (ring||[]).map(p=>{ const x=p[0]*LGP.kx, y=-p[1]*LGP.ky; return ((x-LGP.x0+LGP.pad)*LGP.sc).toFixed(1)+','+((y-LGP.y0+LGP.pad)*LGP.sc).toFixed(1); }).join(' '); }
function cdMapa(self,v,fs){ const larga=cadLarga(); const ts=fs?cdTalsDe(self,fs.v.nome,true):[]; const sr=!!fs&&fs.id===MAPA_FID, lg=!!fs&&fs.id==='LG'; const gu=lg?cdGeomU():{}; const mk=self.state.cd_mk;
  const naMapa=t=>(sr&&MAPA.indexOf(t.id)>=0)||(lg&&(MAPA_LG.indexOf(t.id)>=0||!!gu[t.id]));
  const no=ts.filter(naMapa), fora=ts.filter(t=>!naMapa(t)&&t.v.sit!=='Inativo');
  const wOn=self.state.cd_mapa_w!==false; const vis=self.state.cd_vis||0;
  v.cd_temMapa=no.length>0; v.cd_mapa_on=no.length>0&&(larga?wOn:vis===1); v.cd_lista_on=larga||vis===0||!no.length;
  v.cd_mtogT=wOn?'Ocultar mapa':'Mostrar mapa'; v.cd_mtog=()=>self.setState({cd_mapa_w:!wOn}); cadSeg(v,'cdv',2,vis,i=>self.setState({cd_vis:i}));
  v.cd_mapa_sr=sr; v.cd_mapa_lg=lg; v.cd_mapaLab='Mapa dos talhões da '+(fs?fs.v.nome:'')+': setas percorrem os talhões, Enter abre';
  v.cd_semgeo=!!fs&&!no.length&&ts.length>0;
  v.cd_semgeoT=fs?('Nenhum talhão da '+fs.v.nome+' tem polígono'+(in04(fs.v.nome)?'.':': o mapa desta fazenda ainda não existe no protótipo; o planejamento usa a área cultivável.')):'';
  v.cd_fora=fora.map(t=>({t:t.v.t+(isnum(t.v.calc)||circ(t.v)?'':' (sem polígono)'),go:()=>g2open(self,GR('g_tal'),t.id,null)})); v.cd_temFora=!!fs&&fora.length>0&&no.length>0;
  const z=self.state.cd_zoom||1; v.cd_mzw=Math.round(z*100)+'%'; v.cd_mzh=(z>1||!larga)?'none':'240px';
  v.cd_zin=()=>self.setState({cd_zoom:Math.min(4,z+0.5)}); v.cd_zout=()=>self.setState({cd_zoom:Math.max(1,z-0.5)}); v.cd_mkey=(e)=>cdMapaTecla(self,e);
  const cor=(t)=>{ const V=t.v; if(V.sit==='Inativo') return ['#C9CFCB','#5B6660']; if(isnum(V.calc)){ const di=difInfo(V); return (di&&di.fora&&!V.motivo)?['#FFD500','#8A5A00']:['#8FD67F','#1E7A4C']; }
    if(circ(V)) return ['#CFE3C2','#4F7A55']; return ['#E9EEE6','#8A968E']; };
  const ids=sr?MAPA:(lg?MAPA_LG.filter(id=>!gu[id]):[]); const foco=(mk&&ids.indexOf(mk)>=0)?mk:ids[0];
  MAPA.concat(MAPA_LG).forEach(id=>{ const t=ts.find(x=>x.id===id); const c=t?cor(t):['#E9EEE6','#8A968E']; const sob=lg&&!!gu[id];
    v['mf_'+id]=sob?'transparent':c[0]; v['ms_'+id]=sob?'transparent':c[1]; v['mw_'+id]=(mk===id&&!sob)?6:2; v['mt_'+id]=(id===foco&&!sob)?'0':'-1';
    v['ml_'+id]=t?(t.v.t+': '+talSit(t).t):id; v['mc_'+id]=(e)=>cdMapaClique(self,e,id); });
  v.cd_mtu=lg?Object.keys(gu).filter(id=>ts.some(t=>t.id===id)).map(id=>{ const t=ts.find(x=>x.id===id); const c=isnum(t.v.calc)?cor(t):['#8FD67F','#1E7A4C'];
    return {id:id,pts:cdProj(gu[id]),f:c[0],s:c[1],w:mk===id?6:2,tab:(!ids.length&&id===Object.keys(gu)[0])?'0':'-1',lab:t.v.t+': '+(isnum(t.v.calc)?talSit(t).t:'Polígono do Mapa'),go:(e)=>cdMapaClique(self,e,id)}; }):[]; }
// painel do talhão em consulta (DS-41): Próximo passo, ficha, parcelas das safras abertas da fazenda, geometria e origem; Editar troca pelo formulário
function cdConsTal(self,r){ const V=r.v; const nome=V.faz||''; const S=talSit(r); const ina=V.sit==='Inativo'; const di=difInfo(V); const tem=isnum(V.calc); const des='IN-04.dc.html#desenhar='+encodeURIComponent(r.id);
  let prox;
  if(ina) prox={cor:'gray',t:'Inativo desde '+br(V.inat||HOJE)+': fora do Planejar safra e do Mapa; safras e O.S. antigas seguem consultáveis.',prim:{t:'Reativar '+V.t,go:()=>{ g2editar(self,GR('g_tal'),r.id,'sit'); setTimeout(()=>draftSet(self,'g_tal',{sit:'Ativo'}),20); }}};
  else if(!tem&&!circ(V)) prox=in04(nome)?{cor:'yellow',t:'Polígono do '+V.t+' pendente: o planejamento usa a área cultivável e o mapa de taxa variável fica bloqueado.',lks:[{t:'Definir polígono do '+V.t+' no mapa',h:des}]}
    :{cor:'yellow',t:'Polígono do '+V.t+' pendente: o mapa da '+nome+' ainda não existe no protótipo; o planejamento usa a área cultivável.'};
  else if(di&&di.fora&&!V.motivo) prox={cor:'yellow',t:'Diferença de '+nf(di.pct*100,1)+' % entre a área cultivável e o polígono, sem motivo.',prim:{t:'Informar motivo da diferença',go:()=>g2editar(self,GR('g_tal'),r.id,'motivo')}};
  else if(circ(V)) prox={cor:'gray',t:'Círculo do KML: estimativa pelo centro e pela área declarada, não é polígono validado.',lks:[{t:'Desenhar o polígono do '+V.t+' no mapa',h:des}]};
  else prox={cor:'green',t:'Em dia: polígono validado'+(V.ver?' ('+V.ver+')':'')+' e área conferida.'};
  const sec=[{t:'Editar talhão',go:()=>g2editar(self,GR('g_tal'),r.id)}];
  if(self.state.cd_novo===r.id&&!ina) sec.push({t:'+ Criar outro talhão na '+nome,go:()=>cdCriar(self,{faz:nome,sis:V.sis||'Sequeiro'})});
  const ps=PARC[r.id]||[]; const saf=SAFOPEN.filter(s=>s.faz===nome); const det='CD-01det.dc.html#talhao='+encodeURIComponent(r.id);
  const pd=di?Math.round(di.d/(Number(V.decl)||1)*1000)/10:null;
  const blocos=[{t:'Ficha',id:'ficha',lin:[{l:'Fazenda',v:nome},{l:'Sistema',v:V.sis||'Sequeiro'},(V.sis&&V.sis!=='Sequeiro')?{l:'Pivô ou setor',v:V.setor||'a informar'}:null,
      {l:'Área cultivável',v:nf(V.decl,1)+' ha'},{l:'Polígono',v:tem?(nf(V.calc,1)+' ha'+(V.ver?' · '+V.ver:'')):(circ(V)?'Círculo do KML (estimativa)':'Sem polígono')},
      di?{l:'Diferença',v:sgn(r1(di.d),1)+' ha · '+sgn(pd,1)+' %'+(V.motivo?' · '+V.motivo:''),cor:(di.fora&&!V.motivo)?'yellow':''}:null,
      circ(V)?{l:'Geometria',v:V.geo_t||''}:null,{l:'Situação',v:S.t}]}];
  if(!saf.length) blocos.push({t:'Parcelas',id:'parcelas',nota:'Sem safra aberta na '+nome+'.'});
  saf.forEach((s,i)=>{ const p=ps.filter(x=>x.sid===s.sid);
    blocos.push({t:'Parcelas na '+s.nome,id:'parcelas',tab:p.length?{cols:['Parcela','Cultura','Cultivar','Área','Plantio'],rows:p.map(x=>[x.local,x.cult,x.var,nfa(x.area)+' ha',br(x.plantio)])}:null,
      nota:p.length?'':('O '+V.t+' ainda não tem parcela na '+s.nome+'.'),
      lks:[ina?null:{t:'Planejar '+V.t+' na '+s.nome,h:'SAF.dc.html#saf='+encodeURIComponent(s.sid)+'&passo=cultivos'+(p.length?'&cult='+encodeURIComponent(p[0].cid):'')},
           i===saf.length-1?{t:'Abrir parcelas de todas as safras',h:det}:null]}); });
  blocos.push({t:'Geometria',id:'geometria',nota:tem?('Versão atual '+(V.ver||'v1')+'; as anteriores ficam em consulta para as O.S. já emitidas.'):(circ(V)?'Círculo do KML, sem versão de polígono.':'Sem versão de polígono.'),
    lks:[{t:'Abrir versões e importação',h:det+'&aba=geometria'}]});
  blocos.push({t:'Origem e histórico',id:'origem',lin:[{l:'Origem',v:circ(V)?('KML da fazenda'+(LG_SINT?' · '+LG_SINT:'')):'Cadastro da fazenda'},ina?{l:'Inativado em',v:br(V.inat||HOJE)}:null]});
  return {titulo:'Talhão · '+V.t,sub:nome+' · '+(ina?'Inativo':'Ativo')+' · '+nf(V.decl,1)+' ha cultivável',prox:prox,sec:sec,blocos:blocos}; }
// ficha da fazenda (C26): documentos, posse e vigência sem abrir o formulário; o verbo da pendência fica no Próximo passo do detalhe (uma vez)
function cdConsFaz(self,f){ const V=f.v; const ts=cdTalsDe(self,V.nome); const cult=r1(ts.reduce((s,t)=>s+(Number(t.v.decl)||0),0)); const ps=cdPends(self,f); const p=ps[0];
  const prox=p?{cor:p.cor,t:p.t,quem:p.quem||'',mais:ps.length>1?('e mais '+(ps.length-1)+': '+ps.slice(1).map(x=>x.s).join('; ')+'.'):''}:{cor:'green',t:'Em dia: documentos, posse e outorgas sem pendência.'};
  const arr=V.posse&&V.posse!=='Própria';
  return {titulo:'Fazenda · '+V.nome,sub:(V.empresa||'Empresa a informar')+' · '+(V.mun||'')+'/'+(V.uf||'')+' · '+(V.sit||'Ativa'),prox:prox,sec:[{t:'Editar fazenda',go:()=>g2editar(self,GR('g_faz'),f.id)}],
    blocos:[{t:'Identificação',lin:[{l:'Empresa',v:V.empresa||'a informar',cor:V.empresa?'':'yellow'},{l:'Município',v:(V.mun||'')+'/'+(V.uf||'')},{l:'Fuso horário',v:V.fuso}]},
      {t:'Área',lin:[{l:'Área total do imóvel',v:nf(V.area,0)+' ha'},{l:'Módulos fiscais',v:(isnum(V.mf)&&String(V.mf)!=='')?nfa(V.mf):'—'},{l:'Área cultivável',v:nf(cult,1)+' ha'},{l:'Talhões ativos',v:String(ts.length)}]},
      {t:'Posse',lin:[{l:'Posse',v:V.posse||'a informar',cor:V.posse?'':'yellow'},arr?{l:'Arrendador ou parceiro',v:V.arrend}:null,arr?{l:'Fim do contrato',v:br(V.fim)}:null,arr?{l:'Custo da terra',v:isnum(V.custo)?nfa(V.custo)+' sc/ha/ano':'—'}:null]},
      {t:'Documentos',lin:[{l:'CAR',v:V.car||'em branco: bloqueia só o crédito rural',cor:V.car?'':'yellow'},{l:'Matrícula e cartório',v:V.matr||'a informar',cor:V.matr?'':'yellow'},{l:'Pendência nos documentos',v:V.pend||'nenhuma',cor:V.pend?'yellow':''}]},
      V.kml==='Sim'?{t:'Do KML da fazenda',lin:[{l:'Perímetros',v:V.perim},{l:'Restrição ambiental',v:V.ambs},{l:'Recursos hídricos',v:V.aguas}],nota:LG_SINT?('Demonstração sintética (fictício): '+LG_SINT+'.'):''}:null]}; }
function cdHooks(self){ if(self.__cdHk) return; self.__cdHk=1;
  self.g2cons=(gid,r,v)=>{ if(gid==='g_tal') return (r&&String(r.id).indexOf('F_')!==0)?(v?cdConsTal(self,r):true):null; if(gid==='g_faz') return r?(v?cdConsFaz(self,r):true):null; return null; };
  self.g2aberto=(gid,rid,o)=>{ if(gid!=='g_tal'||(o&&o.end)) return; self.setState({cd_mk:rid}); cadHashPoe(self,cdEndObj(self,cdSel(self),rid),(o&&(o.nav||o.pai||o.salvo))?null:'i'); };
  self.g2criou=(gid)=>{ if(gid!=='g_tal') return; let st=null; try{ st=history.state; }catch(e){} const ja=/(^|&)novo=1/.test(String(location.hash||'').replace(/^#/,''));
    cadHashPoe(self,Object.assign(cdEndObj(self,cdSel(self),null),{novo:'1'}),((st&&st.cadux==='i')||ja)?null:'i'); };
  self.g2fechou=(gid,fm)=>{ if(gid!=='g_tal'||!fm) return; if(!fm.rid){ cadEndFechaItem(self,cdEndObj(self,cdSel(self),null)); return; } const rid=fm.rid; cadEndFechaItem(self,cdEndObj(self,cdSel(self),null)); g2set(self,'g_tal',{fl:rid});
    setTimeout(()=>{ try{ const a=document.activeElement; if(!a||a===document.body){ const b=document.querySelector('[data-rid="'+rid+'"] .g2alvo')||document.querySelector('.cd-mapa [data-tid="'+rid+'"]'); if(b) b.focus(); } }catch(e){} },160); };
  cadEndIni(self,(o,pop,set)=>cdAplica(self,o,pop,set));
  // #faz=BV&novo=1 (recarregar no meio da criação, ou link de outra tela): abre "+ Criar talhão" com a fazenda do endereço, uma vez
  if(cadHashLe().novo==='1'&&!self.__cdNovo){ self.__cdNovo=1; setTimeout(()=>{ const f=cdFaz(self,cdSel(self)); cdCriar(self,{faz:f?f.v.nome:''}); },0); }
  try{ document.addEventListener('keydown',(e)=>{ if(e.key!=='Escape'||e.defaultPrevented||cadLarga()||self.state.mx_nivel!=='d') return; if(document.querySelector('aside[role=dialog]')) return;
    const t=e.target; if(t&&/^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName)) return; e.preventDefault(); cdVolta(self); }); }catch(e){} }
function PREVALS(self,v){ cadIni(self); cadActsIni(self); cdHooks(self); const fz=RW(self,'g_faz'), tr=RW(self,'g_tal'), ts=tals(tr);
  if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const fs=cdFaz(self,cdSel(self)); const q=self.state.mx_q||'';
  fz.forEach(r=>{ const V=r.v; const at=ts.filter(t=>t.v.faz===V.nome&&t.v.sit!=='Inativo');
    V.cult=r1(at.reduce((s,t)=>s+(Number(t.v.decl)||0),0)); V.nt=at.length; r.s.nome=V.nome||''; });
  tr.forEach(g=>{ if(!g.kids) return; const f=fz.find(x=>x.id===g.v.fid)||fz.find(x=>x.v.nome===g.v.t); if(f){ g.v.t=f.v.nome; g.v.fid=f.id; }
    const at=g.kids.filter(k=>k.v.sit!=='Inativo'); const sub=r1(at.reduce((s,k)=>s+(Number(k.v.decl)||0),0)); g.v.decl=sub;
    // a linha da fazenda (em "Todas") escolhe a fazenda: alvo único com nome acessível (BOT-07), a seta só expande
    const fid=f?f.id:''; g.p.t=[{k:'act',alvo:true,t:g.v.t,al:'Abrir fazenda '+g.v.t,go:()=>cdEscolhe(self,fid)}].concat(f&&f.v.sit==='Inativa'?[chipc('Inativa','gray')]:[])
      .concat([{k:'mut',t:at.length?(at.length+(at.length>1?' talhões ativos':' talhão ativo')):'sem talhão ativo'}]); g.s.t=g.v.t;
    g.p.decl=[{k:'b',t:nf(sub,1)+' ha'}]; g.s.decl=String(sub);
    ['sis','calc','difp','parc','est'].forEach(k=>{ g.p[k]=[{k:'mut',t:''}]; g.s[k]=''; });
    g.kids.forEach(r=>{ const V=r.v; const ina=V.sit==='Inativo'; const di=difInfo(V); const tem=isnum(V.calc);
      r.p.t=[{k:'b',t:V.t||''}]; r.s.t=V.t||''; r.p.sis=[{k:'txt',t:V.sis||'Sequeiro'}]; r.s.sis=V.sis||'Sequeiro';
      r.p.decl=[{k:ina?'mut':'txt',t:nf(V.decl,1)+' ha'}];
      r.p.calc=tem?[{k:'txt',t:nf(V.calc,1)+' ha'}]:[{k:'mut',t:'—'}]; r.s.calc=tem?nf(V.calc,1)+' ha':'';
      V.difp=di?Math.round(di.d/(Number(V.decl)||1)*1000)/10:''; r.p.difp=di?[{k:(di.fora&&!V.motivo?'b':'txt'),t:sgn(V.difp,1)+' %'}]:[{k:'mut',t:'—'}]; r.s.difp=di?sgn(V.difp,1)+' %':'';
      // parcelas das safras abertas da fazenda do talhão (pelo id: homônimo de outra fazenda não soma); o filtro da coluna separa por safra
      const ps=ina?[]:(PARC[r.id]||[]).filter(x=>SAFOPEN.some(s=>s.sid===x.sid&&s.faz===V.faz)); V.parc=ps.length; r.p.parc=[{k:(ps.length?'txt':'mut'),t:String(ps.length)}]; r.s.parc=String(ps.length);
      r.m=Object.assign({},r.m||{},{parc:[...new Set(ps.map(x=>x.safra))].map(x=>({id:x,l:x}))});
      const S=talSit(r); r.p.est=S.p; r.s.est=S.t; }); });
  // seleção do mestre → busca da tela → filtro rápido (cada um marca as linhas que esconde; a contagem "N de M" é dos filhos do grupo)
  cmdPasse(tr,'cadm_g_tal',r=>!fs||r.v.faz===fs.v.nome);
  cmdPasse(tr,'cadb_g_tal',r=>cdCasa(r,q),!!q);
  cmdQf(self,v,'g_tal','cd_qf',[{k:'res',t:'A resolver',f:r=>!!talSit(r).res},{k:'inat',t:'Inativos',f:r=>r.v.sit==='Inativo',oculta:true}],tr);
  if(fs){ const g=tr.find(x=>x.kids&&x.v.fid===fs.id); G2DISP.g_tal=g?g.kids:[]; } else delete G2DISP.g_tal;
  const temSaf=!fs||SAFOPEN.some(s=>s.faz===fs.v.nome);
  GR('g_tal').cols=COLS_TAL.filter(c=>c.k!=='parc'||temSaf).map((c,i)=>(i===0&&!fs)?Object.assign({},c,{l:'Fazenda › talhão'}):c); v.cd_nctal=GR('g_tal').cols.length;
  // restrição ambiental e água: da fazenda escolhida (em "Todas", com a coluna Fazenda)
  const am=RW(self,'g_amb'), ag=RW(self,'g_agua');
  am.forEach(r=>{ const V=r.v; r.p.tema=[{k:V.total?'b':'txt',t:V.tema}]; r.s.tema=V.tema; });
  ag.forEach(r=>{ const V=r.v; const S=aguaSit(V); r.p.nome=[{k:'b',t:aguaNome(V)}]; r.s.nome=aguaNome(V);
    r.p.modo=[V.modo?{k:'txt',t:V.modo}:{k:'mut',t:'—'}]; r.s.modo=V.modo||'';
    const vz=isnum(V.vazn)&&V.vazn!==''; r.p.vazn=[vz?{k:'txt',t:V.vazao}:{k:'mut',t:'—'}]; r.s.vazn=vz?V.vazao:'';
    r.p.est=S.p; r.s.est=S.t; });
  [['g_amb',am],['g_agua',ag]].forEach(([gid,rows])=>{ cmdPasse(rows,'cadm_'+gid,r=>!fs||r.v.faz===fs.v.nome); cmdPasse(rows,'cadb_'+gid,r=>cdCasa(r,q)); });
  cmdQf(self,v,'g_agua','cd_qfa',[{k:'res',t:'A resolver',f:r=>!!aguaSit(r.v).res}],ag);
  GR('g_amb').cols=COLS_AMB.filter(c=>c.k!=='faz'||!fs); v.cd_ncamb=GR('g_amb').cols.length;
  GR('g_agua').cols=COLS_AGUA.filter(c=>c.k!=='faz'||!fs); v.cd_ncagua=GR('g_agua').cols.length; }
function retoma(self,nome){ const s=self._stash; if(!s) return; self._stash=null; const d=Object.assign({},s.draft); if(nome) d.faz=nome; const er=Object.assign({},s.errs||{}); delete er.faz;
  g2set(self,'g_tal',{fm:Object.assign({},s,{draft:d,errs:er,warn:false})}); }
function fazErros(self,d,fm){ const e={}; const fz=RW(self,'g_faz'); const antes=fm.rid?(g2find(fz,fm.rid)||{v:{}}).v.nome:null; self._fazOld=antes;
  const nome=String(d.nome||'').trim();
  if(nome===NOVA_FAZ) e.nome='Use outro nome.';
  else if(nome&&fz.some(r=>r.id!==fm.rid&&String(r.v.nome).trim().toLowerCase()===nome.toLowerCase())) e.nome='Já existe a fazenda '+nome+'.';
  const at=antes?tals(RW(self,'g_tal')).filter(t=>t.v.faz===antes&&t.v.sit!=='Inativo'):[]; const soma=r1(at.reduce((s,t)=>s+(Number(t.v.decl)||0),0)); const a=g2num(d.area);
  if(!isNaN(a)&&a>=1&&at.length&&soma>a+0.005) e.area='Os talhões ativos somam '+nfa(soma)+' ha; a área total não pode ser menor.';
  if(d.sit==='Inativa'&&at.length) e.sit='Há '+at.length+(at.length>1?' talhões ativos':' talhão ativo')+' ('+at.map(t=>t.v.t).join(', ')+'). Inative-os antes da fazenda.';
  if(d.posse!=='Própria'&&d.fim&&d.fim<HOJE&&d.sit!=='Inativa') e.fim='Contrato vencido em '+br(d.fim)+': informe a renovação ou marque a fazenda como inativa.';
  return e; }
function EXTRAVALS(self,v){ simv(self,v); const fz=RW(self,'g_faz'), tr=RW(self,'g_tal'), ts=tals(tr); const fs=cdFaz(self,cdSel(self)); const q=self.state.mx_q||''; const larga=cadLarga();
  // ---- mestre: Todas as fazendas + uma linha por fazenda ativa (talhões, área cultivável e "n a resolver"); inativas no fim ----
  const ativas=fz.filter(f=>f.v.sit!=='Inativa'), inat=fz.filter(f=>f.v.sit==='Inativa');
  // a busca filtra o mestre (fazendas que casam pelo nome ou por um talhão), mas a fazenda escolhida continua à vista (a seleção não some)
  const casaF=f=>!q||f.id===cdSel(self)||cdCasa({v:{t:f.v.nome}},q)||ts.some(t=>t.v.faz===f.v.nome&&cdCasa(t,q));
  const item=f=>{ const at=cdTalsDe(self,f.v.nome); const n=cdNres(self,f); const red=RW(self,'g_agua').some(r=>r.v.faz===f.v.nome&&aguaSit(r.v).res==='venc');
    return {id:f.id,t:f.v.nome,n:String(at.length),sub:at.length+(at.length===1?' talhão':' talhões')+' · '+nf(f.v.cult||0,1)+' ha',res:f.v.sit==='Inativa'?'Inativa':(n?(n+' a resolver'):'Em dia'),cor:f.v.sit==='Inativa'?'gray':(n?(red?'red':'yellow'):'green'),inat:f.v.sit==='Inativa'}; };
  const ntot=ts.filter(t=>t.v.sit!=='Inativo').length;
  cadMestreVals(self,v,{todos:{t:'Todas as fazendas',sub:ntot+' talhões',n:''},itens:ativas.filter(casaF).map(item).concat(self.state.mx_inat?inat.filter(casaF).map(item):[]),
    sel:cdSel(self),inatN:inat.length,escolhe:id=>cdEscolhe(self,id)});
  const res=[]; if(q&&!larga){ fz.filter(f=>cdCasa({v:{t:f.v.nome}},q)).forEach(f=>res.push({t:f.v.nome,sub:'Fazenda · '+(f.v.nt||0)+' talhões',go:()=>{ self.setState({mx_q:''}); cdEscolhe(self,f.id); }}));
    ts.filter(t=>t.v.sit!=='Inativo'&&cdCasa(t,q)).forEach(t=>res.push({t:t.v.t+' · '+t.v.faz,sub:'Talhão · '+(t.v.sis||'Sequeiro')+' · '+nf(t.v.decl,1)+' ha',go:()=>cdAbreTal(self,t.id)})); }
  cadResVals(v,res); v.cd_nfaz=()=>{ g2set(self,'g_tal',{fm:null}); g2new(self,GR('g_faz')); };
  // ---- detalhe: cabeçalho, Próximo passo e abas ----
  const ind=self.state.cd_ind; const aviso=ind?ind.t:''; const saida=ind?{t:'Ver todas as fazendas',go:()=>{ self.setState({cd_ind:null,mx_sel:'',mx_nivel:larga?'d':'m'}); cadHashPoe(self,{}); }}:null;
  const nAg=(rows)=>rows.filter(r=>!r.sh||String(r.sh).indexOf('cadm_')!==0);
  if(!fs){ const at=ts.filter(t=>t.v.sit!=='Inativo'); const cult=r1(at.reduce((s,t)=>s+(Number(t.v.decl)||0),0)); const nr=ativas.map(f=>[f,cdNres(self,f)]).filter(x=>x[1]);
    const tot=nr.reduce((s,x)=>s+x[1],0);
    cadDetVals(self,v,{t:'Todas as fazendas',sub:ativas.length+' fazendas · '+at.length+' talhões · '+nf(cult,1)+' ha cultiváveis · subtotal por fazenda, sem total geral',
      chip:tot?{t:tot+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'},prox:tot?{cor:'gray',t:tot+(tot>1?' pendências':' pendência')+' em '+lista(nr.map(x=>x[0].v.nome+' ('+x[1]+')'))+'. Escolha a fazenda na lista para ver o próximo passo dela.'}:null,
      volta:'Fazendas',voltar:()=>cdVolta(self),aviso:aviso,avisoSaida:saida}); }
  else { const V=fs.v; const at=cdTalsDe(self,V.nome); const n=cdNres(self,fs); const ps=cdPends(self,fs);
    const posse=!V.posse?'posse a informar':(V.posse==='Própria'?'Própria':V.posse+(V.fim?' até '+br(V.fim):''));
    cadDetVals(self,v,{t:V.nome,sub:[V.empresa||'empresa a informar',(V.mun||'')+'/'+(V.uf||''),posse,nf(V.area,0)+' ha total',nf(V.cult||0,1)+' ha cultivável',at.length+(at.length===1?' talhão':' talhões')].join(' · '),
      chip:V.sit==='Inativa'?{t:'Inativa',c:'gray'}:(n?{t:n+' a resolver',c:ps.some(p=>p.cor==='red')?'red':'yellow'}:{t:'Em dia',c:'green'}),
      ficha:{t:'Ver ficha da fazenda',go:()=>g2open(self,GR('g_faz'),fs.id,null)},lks:in04(V.nome)?[{t:'Importar talhões do KML',h:'IN-04.dc.html#importar'}]:[],
      prox:V.sit==='Inativa'?{cor:'gray',t:'Fazenda inativa: fora do Planejar safra; talhões e O.S. antigas seguem consultáveis.'}:cdProx(ps),volta:'Fazendas',voltar:()=>cdVolta(self),aviso:aviso,avisoSaida:saida}); }
  const tvis=nAg(ts), avis=nAg(RW(self,'g_amb')), gvis=nAg(RW(self,'g_agua')); const gres=gvis.filter(r=>aguaSit(r.v).res).length;
  const aba=cadAbas(self,v,'cdt','cd_aba',[{slug:'talhoes',n:String(tvis.filter(t=>t.v.sit!=='Inativo').length),cor:''},{slug:'ambiental',n:String(avis.length),cor:''},
    {slug:'agua',n:String(gvis.length),cor:gres?'yellow':'',sr:gres?', '+gres+' a resolver':''}]);   /* I33: "16" e o ponto amarelo cabem a 390 px; o número a resolver fica no filtro e no Próximo passo */
  // "+ Criar talhão": a primária da tela, no cabeçalho; herda a fazenda escolhida (em "Todas", vem "Escolha…"); some em Ambiental e Água (R15)
  v.cab_criar_on=aba===0; v.cab_criarT='+ Criar talhão'; v.cd_criar=()=>cdCriar(self,{faz:fs?fs.v.nome:''});
  // ---- talhões: contagem, mapa, vazio com próximo passo ----
  cadQfPos(self,v,'g_tal','cd_qf'); cadQfPos(self,v,'g_agua','cd_qfa');
  const ct=cmdConta(self,'g_tal',tr); v.cd_conta=ct.n+' de '+ct.tot; const ca=cmdConta(self,'g_amb',RW(self,'g_amb')); v.cd_contaAmb=ca.n+' de '+ca.tot;
  const cg=cmdConta(self,'g_agua',RW(self,'g_agua')); v.cd_contaAgua=cg.n+' de '+cg.tot;
  const tot=RW(self,'g_amb').filter(r=>r.v.total&&(!fs||r.v.faz===fs.v.nome)); const rl=tot.find(r=>r.v.tipo==='Reserva legal'), app=tot.find(r=>r.v.tipo==='APP');
  v.cd_ambNota=(rl||app)?('Reserva legal '+nfa((rl&&rl.v.area)||0)+' ha · APP total '+nfa((app&&app.v.area)||0)+' ha · categorias de APP se sobrepõem (não somar)'):'';
  cdMapa(self,v,fs);
  const vt=(()=>{ if(fs&&!cdTalsDe(self,fs.v.nome,true).length) return {t:'A '+fs.v.nome+' não tem talhão. Crie o 1º em + Criar talhão, no topo'+(in04(fs.v.nome)?', ou importe do KML':'')+'.',lk:in04(fs.v.nome)?{t:'Importar talhões do KML',h:'IN-04.dc.html#importar'}:null};
    if(ct.n) return null;
    if(q){ const out=ts.filter(t=>t.v.sit!=='Inativo'&&cdCasa(t,q)&&(!fs||t.v.faz!==fs.v.nome)); const fo={}; out.forEach(t=>{ fo[t.v.faz]=(fo[t.v.faz]||0)+1; }); const k=Object.keys(fo)[0];
      if(fs&&k){ const fk=fz.find(f=>f.v.nome===k); return {t:'Nenhum talhão da '+fs.v.nome+' para “'+q+'” · '+fo[k]+' na '+k+'.',go:fk?{t:'Ver na '+k,fn:()=>cdEscolhe(self,fk.id)}:null}; }
      return {t:'Nenhum talhão encontrado para “'+q+'”. Para cadastrar, use + Criar talhão, no topo.'}; }
    if(self.state.cd_qf) return {t:'Nenhum talhão '+(self.state.cd_qf==='inat'?'inativo':'a resolver')+(fs?' na '+fs.v.nome:'')+'.',go:{t:'Mostrar todos',fn:()=>self.setState({cd_qf:''})}};
    return null; })();
  cadVazioSe(self,v,'cd_vt',vt,['g_tal']);
  const va=(!ca.n&&fs)?{t:(q?'Nenhuma área ambiental da '+fs.v.nome+' para “'+q+'”.':('Sem área ambiental da '+fs.v.nome+': vem do CAR da fazenda ('+(fs.v.car?'recibo '+fs.v.car:'recibo em branco')+').'))}:(!ca.n&&q?{t:'Nenhuma área ambiental encontrada para “'+q+'”.'}:null);
  cadVazioSe(self,v,'cd_va',va,['g_amb']);
  const vg=(!cg.n&&fs&&!gvis.length)?{t:'Sem ponto de água da '+fs.v.nome+': vem do KML da fazenda (outorga e certidão de uso).'}:(!cg.n&&q?{t:'Nenhum ponto de água encontrado para “'+q+'”.'}:null);
  cadVazioSe(self,v,'cd_vg',vg,['g_agua']);
  // linha da fazenda na árvore ("Todas"): o alvo escolhe a fazenda; tocar na linha também (a seta só expande)
  (v.g_tal_rows||[]).forEach(x=>{ if(String(x.id).indexOf('F_')===0){ const g=tr.find(y=>y.id===x.id); const fid=g?g.v.fid:''; x.cls='g2r g2ed'; x.tab='-1';
    x.open=(e)=>{ if(e&&e.target&&e.target.closest&&e.target.closest('button')) return; cdEscolhe(self,fid); }; x.key=()=>{}; } });
  // estado da tela no cabeçalho (uma linha): o que pede atenção em todas as fazendas
  const sem=ts.filter(t=>talSit(t).res==='sem'), mot=ts.filter(t=>talSit(t).res==='mot'); const docs=fz.filter(f=>fazPend(f.v)); const ag=RW(self,'g_agua');
  const agV=ag.filter(r=>aguaSit(r.v).res==='venc'), nAgR=ag.filter(r=>aguaSit(r.v).res).length; const pe=[];
  if(sem.length) pe.push(sem.length===1?(sem[0].v.t+' sem polígono'):(sem.length+' talhões sem polígono'));
  if(docs.length) pe.push(docs.length===1?('cadastro da '+docs[0].v.nome+' pendente'):(docs.length+' fazendas com cadastro pendente'));
  if(mot.length) pe.push(mot.length+(mot.length>1?' diferenças sem motivo':' diferença sem motivo'));
  if(nAgR) pe.push(nAgR+(nAgR>1?' outorgas a renovar':' outorga a renovar'));
  cadEstado(v,'cd',pe.length?pe.join(' · '):'Cadastro em dia',agV.length?'red':(pe.length?'yellow':'green'));
  // painéis de consulta do que veio do KML (não é valor calculado): dizem a origem e, no ponto de água, a situação
  const FA=v.g_agua_F, fa=g2st(self,'g_agua').fm; if(FA&&FA.open&&fa&&fa.rid){ const r=g2find(RW(self,'g_agua'),fa.rid); if(r){ const S=aguaSit(r.v);
    FA.sub=(LG_SINT?'Consulta · '+LG_SINT+', sem dado real · ':'Consulta do KML do proprietário · ')+S.t+(aguaDoc(r.v)?' · '+aguaDoc(r.v):'')+(r.v.venc?' · vencimento '+br(r.v.venc):'')+(r.v.curso?' · '+r.v.curso:'')+'. Para mudar, atualize o KML ou o documento no órgão.'; } }
  const FB=v.g_amb_F; if(FB&&FB.open) FB.sub='Consulta do CAR ('+(LG_SINT?LG_SINT+', sem dado real':'KML do proprietário')+'): restrição ambiental da fazenda, não vira talhão. As categorias de APP se sobrepõem; o total é o tema "APP Total".';
  // ---- formulário da fazenda (Editar fazenda, + Criar fazenda) ----
  cxForm(self,v,'g_faz');
  const uf=cxCampo(v,'g_faz','uf'); if(uf&&!uf.dis) uf.set=(e)=>{ const u=e.target.value; draftSet(self,'g_faz',{uf:u,fuso:FUSO_UF[u]||FUSO_PAD}); };
  valida2(self,v,'g_faz',(d,fm)=>fazErros(self,d,fm));
  const FF=v.g_faz_F; if(FF&&FF.open&&self._stash){ FF.sub='Ao salvar, você volta ao talhão '+(self._stash.draft.t||'em cadastro')+' com esta fazenda escolhida; o que já foi preenchido fica mantido.';
    ['close','cancel','discard','key'].forEach(k=>{ const o=FF[k]; if(o) FF[k]=(e)=>{ o(e); if(!g2st(self,'g_faz').fm) retoma(self,null); }; }); }
  // ---- formulário do talhão (Editar talhão, + Criar talhão) ----
  cxForm(self,v,'g_tal');
  const ff=cxCampo(v,'g_tal','faz'); if(ff&&!ff.dis){ const at=fz.filter(f=>f.v.sit!=='Inativa').map(f=>f.v.nome); if(ff.v&&ff.v!==NOVA_FAZ&&at.indexOf(ff.v)<0) at.push(ff.v);
    ff.opts=(ff.v?[]:[{v:'',t:'Escolha…'}]).concat(at.map(n=>({v:n,t:n}))).concat([{v:NOVA_FAZ,t:NOVA_FAZ}]);
    ff.set=(e)=>{ const val=e.target.value; if(val!==NOVA_FAZ){ draftSet(self,'g_tal',{faz:val}); return; }
      self._stash=Object.assign({},g2st(self,'g_tal').fm); g2set(self,'g_tal',{fm:null}); g2new(self,GR('g_faz')); }; }
  valida2(self,v,'g_tal',(d,fm)=>{ const o=fm.rid?ts.find(t=>t.id===fm.rid):null; self._sit0=o?o.v.sit:''; return talErros(d,fm,{tals:ts,fazs:fz,aloc:ALOC}); });
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_faz'){ cxLimpa('g_faz',r); const old=self._fazOld; const trc=g2clone(RW(self,'g_tal')); g2set(self,'g_faz',{rows:rows});
      if(isNew){ trc.push({id:'F_'+r.id,ro:true,v:{t:r.v.nome,fid:r.id},s:{},p:{},kids:[]}); const x=Object.assign({},g2st(self,'g_tal').x||GR('g_tal').x0||{}); x['F_'+r.id]=true; g2set(self,'g_tal',{rows:trc,x:x}); }
      else if(old&&old!==r.v.nome){ tals(trc).forEach(t=>{ if(t.v.faz===old){ t.v.faz=r.v.nome; t.s.faz=r.v.nome; } }); g2set(self,'g_tal',{rows:trc}); }
      if(isNew&&self._stash){ g2set(self,'g_faz',{fm:null}); retoma(self,r.v.nome); self.setState({g2toast:'Fazenda '+r.v.nome+' criada. Continue o talhão.'}); }
      else if(isNew){ g2set(self,'g_faz',{fm:null}); self.setState({mx_sel:r.id,mx_nivel:'d',g2toast:'Fazenda '+r.v.nome+' criada. Próximo passo: crie os talhões dela em + Criar talhão.'}); cadHashPoe(self,{faz:r.id}); }
      else self.setState({g2toast:r.v.sit==='Inativa'?(r.v.nome+' inativa: sai do Planejar safra; talhões e O.S. antigas seguem consultáveis.'):('Salvo: '+r.v.nome+'.')}); }
    if(gid==='g_tal'){ cxLimpa('g_tal',r); if(r.v.sit==='Inativo'){ if(!r.v.inat) r.v.inat=HOJE; } else r.v.inat='';
      const f=RW(self,'g_faz').find(x=>x.v.nome===r.v.faz); const gk='F_'+(f?f.id:r.v.faz); const cur=rows.find(g=>g.kids&&g.kids.some(k=>k.id===r.id));
      if(!cur||cur.id!==gk){ const i=rows.indexOf(r); if(i>=0) rows.splice(i,1); if(cur) cur.kids.splice(cur.kids.indexOf(r),1);
        let g=rows.find(x=>x.id===gk); if(!g){ g={id:gk,ro:true,v:{t:r.v.faz,fid:f?f.id:''},s:{},p:{},kids:[]}; rows.push(g); } g.kids.push(r); }
      const x=Object.assign({},g2st(self,'g_tal').x||GR('g_tal').x0||{}); x[gk]=true; g2set(self,'g_tal',{rows:rows,x:x,fl:r.id});
      if(isNew) self.setState({cd_novo:r.id,cd_mk:r.id,g2toast:r.v.t+' criado na '+r.v.faz+'. Próximo passo: '+(in04(r.v.faz)?'definir o polígono no mapa.':'o polígono fica pendente; o planejamento usa a área cultivável.')});
      else self.setState({g2toast:talToast(r,self._sit0)}); }
    cadSalvar(self); }; }
'''

# ================= CD-01det · detalhe de qualquer talhão =================
def _parc_rows(tal_ids,faz):
    """grupos por talhão × safra (safra com cultivo do talhão ou safra aberta DA FAZENDA do talhão) com as parcelas do Planejar safra, em consulta."""
    rows=[]; x0={}
    for t in tal_ids:
        for s in D2.SAFRAS:
            if s.get('fazenda',faz)!=faz: continue   # safra de outra fazenda (ex.: Safra Mamão da Lagoa Grande) não é do talhão da Santa Rita
            cs=[c for c in D2.CULTIVOS[s['id']] if _tal_de(c['local'])==t]
            if not cs and s['ro']: continue
            kids=[]
            for c in cs:
                pl=D2.PLANO.get(c['plano']) if c['plano'] else None
                kids.append(R(c['id'],dict(tal=t,parc=c['local'],tipo=c['tipo'],safra=s['nome'],cult=c['cultura'],var=c['variedade'],
                                           area=c['area'],plantio=c['plantio'],meta=f"{_br(c['meta'])} {c['un_meta']}",plano=(f"{pl['nome']} v{pl['versao']}" if pl else 'sem plano'),
                                           geo0=D.GEO_PARC.get(c['id'],''),geo=''),ro=True))
            gid=f'G_{t}_{s["id"]}'
            rows.append(dict(id=gid,ro=True,grp=True,v=dict(tal=t,sid=s['id'],safra=s['nome'],estado=s['estado']),s={},p={},kids=kids))
            if not s['ro']: x0[gid]=True
    return rows,x0
def cd01det():
    fname='CD-01det.dc.html'; E._reset_screen(fname); PARENT37[fname]='CD-01.dc.html'
    fr=_faz_rows(); tr=_tal_rows(); fazs=[r['v']['nome'] for r in fr]
    prow,px0=_parc_rows([r['id'] for r in tr if r['v']['faz']=='Santa Rita'],'Santa Rita')
    # ficha do talhão: uma linha (o registro aberto), sem filtro nem ordem (eles valem na lista do CD-01); uma variável por coluna (TABELAS-FOCO):
    # setor de irrigação, versão do polígono e diferença em ha e em % em colunas próprias; município e fuso ficam no cadastro da fazenda, o motivo no painel
    gi=grid([dict(k='faz',l='Fazenda',w=160),dict(k='sis',l='Sistema',w=130),dict(k='setor',l='Setor de irrigação',w=150),dict(k='decl',l='Área cultivável',t='num',a='r',un='ha',d=1),
             dict(k='calc',l='Polígono',t='num',a='r',un='ha',d=1),dict(k='ver',l='Versão'),dict(k='difha',l='Diferença (ha)',t='num',a='r',d=1),
             dict(k='difp',l='Diferença (%)',t='num',a='r',d=1),dict(k='est',l='Situação',w=220)],
        tr,gid='g_idt',search=False,total=False,headtools=False,frame=False,
        edit=dict(m='form',title='Talhão',newTitle='Criar talhão',sub=SUB_TAL,fields=campos_tal(fazs)))
    # "Planejar Tn na safra" só leva a outra tela: é link, não verde (BOT-08); vai à safra aberta da fazenda do talhão, com o cultivo (X-LNK da NAV)
    plan=se('det_ativo',f'<span class="cadx-prim"><a href="{H("det_planH")}" style="color: {ACC}; font-weight: 700; font-size: 13px; text-decoration: none; white-space: nowrap;">{H("det_plan")} ›</a></span>')
    # árvore safra › parcela: cada linha mostra a sua entidade (safra: área alocada, livre e estado; parcela: tipo, cultura, cultivar, área, plantio
    # e polígono); a área livre é número (negativo = excede), a cor diz se confere
    gp=grid([dict(k='parc',l='Safra › parcela',w=190),dict(k='tipo',l='Tipo'),dict(k='cult',l='Cultura'),dict(k='var',l='Cultivar'),dict(k='area',l='Área',t='num',a='r',un='ha',d=1),
             dict(k='livre',l='Livre',t='num',a='r',un='ha',d=1),dict(k='plantio',l='Plantio',t='date'),dict(k='est',l='Situação',w=180)],
        prow,gid='g_parc',tree=True,search=False,total=False,x0=px0,frame=False,tools=plan,
        edit=dict(m='origin',title='Parcela',leafOnly=True,alvo='parcela',
            fields=[txt('parc','Parcela',ro=True),txt('safra','Safra',ro=True),txt('cult','Cultura',ro=True),txt('var','Cultivar',ro=True),num('area','Área','ha',ro=True),
                    dat('plantio','Plantio',ro=True),txt('meta','Meta de produtividade',ro=True),txt('plano','Plano agronômico',ro=True),txt('geo','Polígono',ro=True)]))
    link_mini=f'{_MINI} text-decoration: none; display: inline-block;'
    geo_html=(f'<div style="display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 18px; align-items: start;">'
              f'<div style="display: flex; flex-direction: column; gap: 6px;">'
              f'<div role="img" aria-label="{H("geo_aria")}" style="display: flex; height: 190px; background: #DDE5D4; clip-path: polygon(2% 5%, 97% 0, 100% 95%, 0 100%);">'
              f'<sc-for list="{H("geo_parts")}" as="g" hint-placeholder-count="2"><div style="{H("g.st")}"><span style="font-family: {DISP}; font-size: 22px; font-weight: 700;">{H("g.t")}</span><span style="font-size: 12px; font-weight: 700;">{H("g.s")}</span></div></sc-for></div></div>'
              f'<div style="display: flex; flex-direction: column;"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em; padding-bottom: 4px;">VERSÕES DO POLÍGONO</div>'
              f'<sc-for list="{H("geo_vers")}" as="x" hint-placeholder-count="2"><div style="display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; border-top: 1px solid {LINE};">'
              f'<span style="{H("x.cst")}"><span style="{H("x.cdot")}"></span>{H("x.chip")}</span><div style="display: flex; flex-direction: column; gap: 1px; min-width: 0;"><b style="font-size: 13px;">{H("x.tit")}</b><span style="font-size: 12px; color: {MUTED};">{H("x.sub")}</span></div></div></sc-for>'
              f'<sc-if value="{H("geo_novers")}" hint-placeholder-val="{F_}"><div style="font-size: 12.5px; color: {MUTED}; padding: 8px 0; border-top: 1px solid {LINE};">Sem polígono: o planejamento usa a área cultivável; mapa de taxa variável fica bloqueado.</div></sc-if></div></div>')
    # um só bloco: identificação do talhão (linha que abre o formulário) e abas Parcelas por safra | Geometria, cada uma com a sua ação
    p0=(se('det_parc_tem',arv(gp),True)
        +se('det_parc_vazio',barra(f'<span style="font-size: 13px; color: {MUTED};">{H("det_parc_msg")}</span>',plan)))
    mapa_lk=(f'<a href="{H("geo_ver")}" style="{link_mini}">Ver no mapa ›</a><a href="IN-04.dc.html#importar" style="{link_mini}">Importar KML ou GeoJSON ›</a>'
             f'<span class="cadx-prim"><a href="{H("geo_des")}" style="{link_mini}">{H("geo_dest")}</a></span>')   # navegação: link, não verde (BOT-08)
    # R18/AC-25 (achado 5 da revisão): desenhar e importar só onde o IN-04 abre o mapa da fazenda (Lagoa Grande); nas outras, a frase do limite,
    # a mesma do CD-01, e nenhum editor simulado (ele gravava uma versão "validada" que o CD-01 contradizia)
    p1=(barra(f'<b style="font-size: 13px;">{H("geo_leg")}</b>',se('geo_mapa',mapa_lk)
              +se('geo_lim',f'<span style="font-size: 12.5px; color: {MUTED}; max-width: 560px;">{H("geo_limT")}</span>'))
        + f'<div class="cadx-rola" style="padding: 16px;">{geo_html}</div>')
    # SEL-02: talhão indisponível pelo endereço: aviso visível e acessível, nada aberto, sem dizer se existe, com saída (seletor ou a lista)
    corpo=(se('det_nf',f'<section class="cadx" aria-label="Talhão indisponível"><div role="alert" class="cmd-aviso" style="margin: 16px;"><span>{H("det_nfT")}</span>'
                       f'<a href="CD-01.dc.html" style="color: {E.ACC}; font-weight: 700; font-size: 13px; text-decoration: none;">Ver todas as fazendas ›</a></div>'
                       f'<p style="margin: 0 16px; font-size: 13px; color: {MUTED};">Ou escolha um talhão no seletor do cabeçalho.</p></section>')
           + se('det_ok',f'<section class="cadx" aria-label="Talhão"><div class="cmd-dc"><div class="cmd-dt"><p class="cmd-ds" style="flex: 1 1 320px;">{H("det_sub")}</p>'
                         f'<span class="cmd-dsec">'+se('det_ativo',f'<button type="button" onClick="{H("det_editar")}" style="{BTN_ST(False,True)}">Editar talhão</button>',True)
                         + se('det_inat',f'<button type="button" onClick="{H("det_reativar")}" style="{BTN_ST(True,True)}">{H("det_reat")}</button>')+f'</span></div></div><div class="cadx-topo">{abas("dtt",["Parcelas por safra","Geometria"],"Detalhe do talhão")}</div>'
                         f'<div class="cadx-dados">{pane("dtt",0,p0)+pane("dtt",1,p1)}</div></section>',True))
    fazjs=[dict(id=r['id'],v=r['v']) for r in fr]
    vers={t:[list(x) for x in DC.geo_vers(t)] for t in DC.CALC}
    safo=[dict(sid=s['id'],nome=s['nome'],estado=s['estado'],faz=s['fazenda']) for s in SAF_ABERTAS]
    js({},TALJS+'const FAZ0='+json.dumps(fazjs,ensure_ascii=False)+', VERS0='+json.dumps(vers,ensure_ascii=False)+', SAFOPEN='+json.dumps(safo,ensure_ascii=False)
       # área cultivável da época de cada safra encerrada (registro fechado não é recalculado com a área atual)
       +', CULT_EP='+json.dumps({s['id']:{t:float(ha) for t,ha,*_ in D.TALHOES} for s in D2.SAFRAS if s['ro']})+';\nlet FAZL=FAZ0;\n'+r'''
const HATCH='repeating-linear-gradient(45deg,#C9CFCB 0 7px,#EEF1EE 7px 14px)';
function detIni(self){ if(self._ini) return; self._ini=1; const st=cadLer();
  if(st&&st.faz){ const f0=FAZ0; FAZL=st.faz.map(x=>({id:x.id,v:Object.assign({},x.v)})); f0.forEach(f=>{ if(!FAZL.some(x=>x.id===f.id)) FAZL.push({id:f.id,v:Object.assign({},f.v)}); }); }
  if(st&&st.tal){ const t0=GR('g_idt').rows; const tl=st.tal.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}}));
    t0.forEach(r=>{ if(!tl.some(x=>x.id===r.id)) tl.push({id:r.id,v:Object.assign({},r.v),s:{},p:{}}); }); GR('g_idt').rows=tl; }
  self._vers0=(st&&st.vers)||{}; self._pgeo0=(st&&st.pgeo)||{};
  const pr=GR('g_parc').rows; const x0=Object.assign({},GR('g_parc').x0||{});
  GR('g_idt').rows.forEach(t=>{ if(pr.some(g=>g.v.tal===t.id)) return;
    SAFOPEN.filter(s=>s.faz===t.v.faz).forEach(s=>{ const id='G_'+t.id+'_'+s.sid; pr.push({id:id,ro:true,grp:true,v:{tal:t.id,sid:s.sid,safra:s.nome,estado:s.estado},s:{},p:{},kids:[]}); x0[id]=true; }); });
  GR('g_parc').x0=x0; self._rowt={}; pr.forEach(g=>{ self._rowt[g.id]=g.v.tal; (g.kids||[]).forEach(k=>{ self._rowt[k.id]=g.v.tal; }); });
  let m=null; try{ m=/[?&#]talhao=([^&]+)/.exec((location.search||'')+(location.hash||'')); }catch(e){}
  self._t0=m?decodeURIComponent(m[1]):'T1'; }
function curT(self){ return self.state.det_t||self._t0; }
function versOf(self,t){ return ((self.state.vers||{})[t])||self._vers0[t]||VERS0[t]||[]; }
function pgeoOf(self,k,T){ const o=(self.state.pgeo||{})[k.id]||self._pgeo0[k.id]||k.v.geo0; if(o) return o;
  return k.v.tipo==='Talhão inteiro'&&T&&isnum(T.v.calc)?'Polígono do talhão':'Sem polígono'; }
function aberta(sid){ return SAFOPEN.some(s=>s.sid===sid); }
function alocDe(self){ const a={}; RW(self,'g_parc').forEach(g=>{ if(!g.grp||!aberta(g.v.sid)) return; const s=r1((g.kids||[]).reduce((x,k)=>x+(Number(k.v.area)||0),0)); if(s>0){ (a[g.v.tal]=a[g.v.tal]||{})[g.v.safra]=s; } }); return a; }
function pendDe(self,T){ if(!T) return null; if(!isnum(T.v.calc)) return {alvo:T.v.t,art:'do',cid:null,ref:Number(T.v.decl)||0};
  for(const g of RW(self,'g_parc')){ if(!g.grp||g.v.tal!==T.id||!aberta(g.v.sid)) continue;
    for(const k of (g.kids||[])){ if(pgeoOf(self,k,T)==='Sem polígono') return {alvo:k.v.parc,art:'da',cid:k.id,ref:Number(k.v.area)||0,safra:g.v.safra}; } }
  return null; }
function detSalvar(self){ cadGravar({faz:FAZL.map(linhaPk),tal:RW(self,'g_idt').map(linhaPk),vers:Object.assign({},self._vers0,self.state.vers||{}),pgeo:Object.assign({},self._pgeo0,self.state.pgeo||{})}); }
function PREVALS(self,v){ detIni(self); const t=curT(self); const T=g2find(RW(self,'g_idt'),t);
  RW(self,'g_idt').forEach(r=>{ const V=r.v; const tem=isnum(V.calc); const di=difInfo(V);
    r.p.faz=[{k:'b',t:V.faz||''}]; r.s.faz=V.faz||'';
    r.p.sis=[{k:'txt',t:V.sis||'Sequeiro'}]; r.s.sis=V.sis||'Sequeiro';
    const se=(V.sis&&V.sis!=='Sequeiro'&&V.setor)?V.setor:''; r.p.setor=[se?{k:'txt',t:se}:{k:'mut',t:'—'}]; r.s.setor=se;
    r.p.calc=tem?[{k:'txt',t:nf(V.calc,1)+' ha'}]:[{k:'mut',t:'—'}]; r.s.calc=tem?nf(V.calc,1)+' ha':'';
    r.p.ver=[tem&&V.ver?{k:'txt',t:V.ver}:{k:'mut',t:'—'}]; r.s.ver=tem?(V.ver||''):'';
    V.difha=di?di.d:''; V.difp=di?Math.round(di.d/(Number(V.decl)||1)*1000)/10:''; const bd=di&&di.fora&&!V.motivo?'b':'txt';
    r.p.difha=di?[{k:bd,t:sgn(di.d,1)+' ha'}]:[{k:'mut',t:'—'}]; r.s.difha=di?sgn(di.d,1)+' ha':'';
    r.p.difp=di?[{k:bd,t:sgn(V.difp,1)+' %'}]:[{k:'mut',t:'—'}]; r.s.difp=di?sgn(V.difp,1)+' %':'';
    // situação: um estado por vez (inativo, círculo do KML, sem polígono, diferença sem motivo ou ativo); a data da inativação fica no cabeçalho
    const S=V.sit==='Inativo'?['Inativo',[chipc('Inativo','gray'),{k:'act',t:'Reativar '+(V.t||''),fn:'det_reativar:'+r.id}]]
      :(circ(V)?['Círculo do KML',sitInfo('Círculo do KML')]:(!tem?['Sem polígono',sitX('Sem polígono','yellow')]
      :(di&&di.fora&&!V.motivo?['Diferença sem motivo',sitX('Diferença sem motivo','yellow','Informar motivo')]:['Ativo',sitOk('Ativo')])));
    r.p.est=S[1]; r.s.est=S[0]; });
  RW(self,'g_parc').forEach(g=>{ if(!g.grp) return; const Tg=g2find(RW(self,'g_idt'),g.v.tal); const ks=g.kids||[];
    const A=r1(ks.reduce((s,k)=>s+(Number(k.v.area)||0),0)); const ab=aberta(g.v.sid); const ep=(CULT_EP[g.v.sid]||{})[g.v.tal];
    const cult=ab?(Tg?Number(Tg.v.decl)||0:0):(ep!==undefined?ep:A); const L=r1(cult-A);
    // safra: área alocada e livre como números (livre negativo = excede; a cor diz se confere) e o estado da safra no chip da Situação
    g.p.parc=[{k:'b',t:g.v.safra}]; g.s.parc=g.v.safra; g.v.area=A; g.p.area=[{k:'txt',t:nfa(A)+' ha'}]; g.s.area=nfa(A)+' ha';
    const lt=(L<-0.005?'−':'')+nfa(Math.abs(L))+' ha'; g.v.livre=L;
    g.p.livre=[{k:'cn',t:lt,c:Math.abs(L)<=0.005?'green':(!ab?'gray':(L<0?'red':'yellow'))}]; g.s.livre=lt;
    ['tipo','cult','var','plantio'].forEach(x=>{ g.p[x]=[{k:'mut',t:''}]; g.s[x]=''; });
    g.p.est=[chipc(g.v.estado,'gray')]; g.s.est=g.v.estado;
    ks.forEach(k=>{ const V=k.v; const gs=pgeoOf(self,k,Tg); V.geo=gs;
      k.p.parc=[{k:'b',t:V.parc}]; k.s.parc=V.parc; k.p.tipo=[{k:'txt',t:V.tipo}]; k.s.tipo=V.tipo;
      k.p.cult=[{k:'txt',t:V.cult}]; k.s.cult=V.cult; k.p.var=[{k:'txt',t:V.var}]; k.s.var=V.var; k.p.livre=[{k:'mut',t:''}]; k.s.livre='';
      const gt=gs==='Validada'?'Polígono validado':gs; k.p.est=[chipc(gt,gs==='Validada'?'green':(gs==='Polígono do talhão'?'gray':'yellow'))]; k.s.est=gt;
      k.o=[{t:'Planejar safra › '+V.safra+' › '+V.parc,h:'SAF.dc.html'}]; }); }); }
function geoVals(self,v,T){ const ina=T.v.sit==='Inativo'; const cal=isnum(T.v.calc); const dec=Number(T.v.decl)||0;
  const g=RW(self,'g_parc').find(x=>x.grp&&x.v.tal===T.id&&x.v.sid===SAFOPEN[0].sid); const ks=((g&&g.kids)||[]).filter(k=>k.v.tipo==='Parcela');
  const cell=(t,s,w,ok)=>({t:t,s:s,st:'flex:0 0 '+w+'%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-width:0;box-sizing:border-box;border-right:2px dashed rgba(255,255,255,.9);color:#15201A;background:'+(ina?'#DADFDB':(ok?'#8FD67F':HATCH))+';'});
  let parts;
  if(ks.length&&cal){ const tot=ks.reduce((a,k)=>a+(Number(k.v.area)||0),0); const base=Math.max(tot,dec)||1;
    parts=ks.map(k=>{ const gs=pgeoOf(self,k,T); return cell(k.v.parc,nfa(k.v.area)+' ha · '+(gs==='Validada'?'validada':'sem polígono'),r1(k.v.area/base*100),gs==='Validada'); });
    if(tot<dec-0.005) parts.push(cell('Livre',nfa(r1(dec-tot))+' ha',r1((dec-tot)/base*100),true)); }
  else parts=[cell(T.v.t,cal?(nf(T.v.calc,1)+' ha · '+(T.v.ver||'')):(circ(T.v)?nfa(dec)+' ha · círculo do KML':'sem polígono'),100,cal)];
  if(!ks.length&&circ(T.v)&&!ina) parts[0].st=parts[0].st.replace(HATCH,'#CFE3C2');
  v.geo_parts=parts; v.geo_leg=ks.length&&cal?('Divisão da '+SAFOPEN[0].nome):(cal?'Polígono do talhão':(circ(T.v)?'Círculo do KML (centro e área declarada)':'Talhão sem polígono'));
  v.geo_aria=v.geo_leg+': '+parts.map(p=>p.t+' '+p.s).join('; ');
  const vs=versOf(self,T.id); const rv=vs.slice().reverse();
  v.geo_vers=rv.map((x,i)=>{ const c=chipSt(i?'gray':'green'); return {chip:i?'Consulta':'Atual',cst:c[0],cdot:c[1],tit:x[0]+' · '+nf(x[3],1)+' ha',
    sub:br(x[1])+' · '+x[2]+(i?' · O.S. emitidas antes de '+br(rv[i-1][1]):'')}; });
  v.geo_novers=!vs.length;
  // Lagoa Grande: a geometria vem do KML como círculo (centro + área declarada); aparece como estimada, sem inventar polígono
  if(!vs.length&&circ(T.v)){ const c=chipSt('gray'); v.geo_vers=[{chip:'Estimado',cst:c[0],cdot:c[1],tit:'Círculo do KML · '+nfa(dec)+' ha',sub:T.v.geo_t||''}]; v.geo_novers=false; } }
function EXTRAVALS(self,v){ const t=curT(self); const T=g2find(RW(self,'g_idt'),t); const ina=!!T&&T.v.sit==='Inativo';
  // seletor do cabeçalho: o talhão mostrado é sempre o escolhido (nunca um registro em silêncio)
  // agrupado por fazenda (o homônimo aparece como "T2 · Boa Vista"); a busca é a do próprio seletor (digitar o início do nome)
  v.det_t=T?t:''; const gr={}; RW(self,'g_idt').forEach(r=>{ (gr[r.v.faz]=gr[r.v.faz]||[]).push({v:r.id,t:r.v.t+' · '+r.v.faz+(r.v.sit==='Inativo'?' · inativo':'')}); });
  v.det_grp=Object.keys(gr).map(k=>({t:k,opts:gr[k]})); v.det_opts=v.det_grp.reduce((a,g)=>a.concat(g.opts),[]);
  v.det_set=(e)=>{ const id=e.target.value; if(!id) return; try{ history.replaceState(null,'','#talhao='+encodeURIComponent(id)); }catch(x){}
    g2set(self,'g_idt',{fm:null}); g2set(self,'g_parc',{fm:null}); self.setState({det_t:id,pg:null}); };
  v.det_ok=!!T; v.det_nf=!T; v.det_nfT='Talhão “'+(self._t0||'')+'” indisponível: não existe neste cadastro ou não está liberado para o seu perfil. Nada foi aberto.'; v.det_ativo=!!T&&!ina; v.det_crumb=T?(T.v.t+' · '+nfa(T.v.decl)+' ha'):'Talhão';
  // cabeçalho do talhão (DS-58) no lugar da ficha de 1 linha: o que é, onde e a geometria; voltar leva à fazenda e ao talhão no CD-01 (I25)
  if(T){ const V=T.v; const di=difInfo(V); const fz=FAZL.find(f=>f.v.nome===V.faz);
    v.det_sub=[V.faz,V.sis||'Sequeiro'].concat(V.sis&&V.sis!=='Sequeiro'&&V.setor?[V.setor]:[]).concat([nf(V.decl,1)+' ha cultivável',
      isnum(V.calc)?('polígono '+nf(V.calc,1)+' ha'+(V.ver?' ('+V.ver+')':'')):(circ(V)?'círculo do KML (estimativa)':'sem polígono')]).concat(di?['diferença '+sgn(Math.round(di.d/(Number(V.decl)||1)*1000)/10,1)+' %'+(V.motivo?' ('+V.motivo+')':'')]:[]).join(' · ');
    v.det_volta='CD-01.dc.html#'+(fz?'faz='+encodeURIComponent(fz.id)+'&':'')+'talhao='+encodeURIComponent(T.id);
    const so=SAFOPEN.filter(s=>s.faz===V.faz); const gp=RW(self,'g_parc').find(g=>g.grp&&g.v.tal===T.id&&so.some(s=>s.sid===g.v.sid)&&(g.kids||[]).length);
    const sid=gp?gp.v.sid:(so[0]?so[0].sid:''); const cid=gp&&gp.kids[0]?gp.kids[0].id:'';
    v.det_planH=sid?('SAF.dc.html#saf='+encodeURIComponent(sid)+'&passo=cultivos'+(cid?'&cult='+encodeURIComponent(cid):'')):'SAF.dc.html'; }
  else { v.det_sub=''; v.det_volta='CD-01.dc.html'; v.det_planH='SAF.dc.html'; }
  v.det_editar=()=>{ if(T) g2open(self,GR('g_idt'),T.id,null); };
  const p=T&&!ina?pendDe(self,T):null;
  // Lagoa Grande tem mapa real: desenhar e importar o contorno acontecem no Mapa e voltam para este cadastro
  v.geo_mapa=!!T&&!ina&&T.v.faz==='Lagoa Grande'; v.geo_lim=!!T&&!ina&&!v.geo_mapa;
  v.geo_limT=!T?'':(p?'Polígono '+p.art+' '+p.alvo+' pendente: o mapa da '+T.v.faz+' ainda não existe no protótipo; o planejamento usa a área cultivável.'
    :'Redesenhar ou importar o polígono: o mapa da '+T.v.faz+' ainda não existe no protótipo.');
  v.geo_ver='IN-04.dc.html#talhao='+encodeURIComponent(T?T.id:''); v.geo_des='IN-04.dc.html#desenhar='+encodeURIComponent(T?T.id:'');
  v.geo_dest=T&&isnum(T.v.calc)?'Redesenhar no mapa ›':'Desenhar no mapa ›';
  v.det_plan='Planejar '+(T?T.v.t:'')+' na safra';
  // talhão inativo: a primária é reativar (abre o formulário do talhão com a Situação em Ativo, focada)
  v.det_inat=ina; v.det_reat='Reativar '+(T?T.v.t:'');
  v.det_reativar=()=>{ if(!T) return; g2open(self,GR('g_idt'),T.id,null); draftSet(self,'g_idt',{sit:'Ativo'});
    setTimeout(()=>{ try{ const s=document.getElementById('fx_g_idt_sit'); if(s) s.focus(); }catch(e){} },60); };
  const ci=!!T&&!ina&&circ(T.v)&&!!p&&!p.cid;
  const st=!T?['Escolha um talhão','gray']:(ina?['Inativo desde '+br(T.v.inat||HOJE),'gray']:(ci?['Círculo do KML · sem polígono validado','gray']:(p?[p.alvo+' sem polígono','yellow']:['Polígono validado','green'])));
  cadEstado(v,'det',st[0],st[1]);
  // abas do detalhe (a ativa vai para o endereço junto com o talhão); a pendência de polígono fica no estado e na aba Geometria (C12)
  const nparc=RW(self,'g_parc').filter(g=>g.v.tal===t).reduce((s,g)=>s+(g.kids||[]).length,0);
  const vs=T?versOf(self,T.id):[];
  cadAbas(self,v,'dtt','det_aba',[{slug:'parcelas',n:nparc,cor:''},{slug:'geometria',n:vs.length?vs[vs.length-1][0]:'',cor:p&&!ci?'yellow':''}]);
  // só as linhas do talhão escolhido
  v.g_idt_rows=(v.g_idt_rows||[]).filter(x=>x.id===t);
  v.g_parc_rows=(v.g_parc_rows||[]).filter(x=>self._rowt[x.id]===t);
  v.g_parc_rows.forEach(x=>{ if(String(x.id).indexOf('G_')===0){ x.cls='g2r'; x.tab='-1'; x.open=()=>{}; x.key=()=>{}; } });
  v.det_parc_tem=v.g_parc_rows.length>0; v.det_parc_vazio=!v.det_parc_tem;
  v.det_parc_msg='Nenhuma safra da '+(T?T.v.faz:'fazenda')+' ainda. Planeje o talhão no Planejar safra.';
  const FP=v.g_parc_F; if(FP&&FP.open) FP.sub='Consulta: cultura, variedade, plantio, meta e plano mudam no Planejar safra.';
  // formulário do talhão no próprio detalhe
  cxForm(self,v,'g_idt'); const FI=v.g_idt_F; if(FI&&FI.open&&T) FI.title='Talhão · '+T.v.t;
  const ff=cxCampo(v,'g_idt','faz'); if(ff&&!ff.dis){ const at=FAZL.filter(f=>f.v.sit!=='Inativa').map(f=>f.v.nome); if(ff.v&&at.indexOf(ff.v)<0) at.push(ff.v); ff.opts=at.map(n=>({v:n,t:n})); }
  valida2(self,v,'g_idt',(d,fm)=>{ const o=fm.rid?g2find(RW(self,'g_idt'),fm.rid):null; self._sit0=o?o.v.sit:''; return talErros(d,fm,{tals:RW(self,'g_idt'),fazs:FAZL,aloc:alocDe(self)}); });
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_idt'||!r) return; cxLimpa('g_idt',r); if(r.v.sit==='Inativo'){ if(!r.v.inat) r.v.inat=HOJE; } else r.v.inat='';
    g2set(self,'g_idt',{rows:rows}); self.setState({g2toast:talToast(r,self._sit0)}); detSalvar(self); };
  if(T) geoVals(self,v,T); else { v.geo_parts=[]; v.geo_vers=[]; v.geo_novers=false; } }
''')
    # tela sem rolagem de página: só a área de dados da aba rola; as ações ficam no bloco e na aba onde agem
    ui37.H_OVR.pop(fname,None); HEIGHTS37[fname]=1000; cadx_css(); md_css()
    shell37('CD-01','Talhão',corpo,fname=fname,crumbs_extra=[H('det_crumb')],status=None,primary_html=None,search=False)
    seletor=(f'<select aria-label="Talhão" value="{H("det_t")}" onChange="{H("det_set")}" style="font-family: inherit; font-size: 15px; font-weight: 800; color: {INK}; padding: 6px 30px 6px 12px; border-radius: 10px; border: 1px solid {LINE}; background: {SURF}; cursor: pointer;">'
             + se('det_nf','<option value="">Escolha o talhão</option>')
             + f'<sc-for list="{H("det_grp")}" as="g" hint-placeholder-count="2"><optgroup label="{H("g.t")}"><sc-for list="{H("g.opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></optgroup></sc-for></select>')
    _injeta(fname,'Talhão',seletor+estado_html('det')); _rolagem(fname)
    # "Voltar" do cabeçalho leva à fazenda e ao talhão no CD-01 (#faz=&talhao=), com o painel dele aberto (I25)
    pth=os.path.join(E.P,fname); h=open(pth,encoding='utf-8').read(); a='<a href="CD-01.dc.html" aria-label="Voltar"'
    assert h.count(a)==1, 'voltar do CD-01det'; open(pth,'w',encoding='utf-8').write(h.replace(a,'<a href="{{det_volta}}" aria-label="Voltar"',1))
