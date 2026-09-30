# -*- coding: utf-8 -*-
"""CD-01 Fazendas, áreas e talhões · CD-01det Detalhe do talhão (módulo próprio; areas.cadastros.build usa este se existir).

CD-01 (listagem): entidade Fazenda (cadastrar, editar pela linha, inativar sem excluir) e talhões em árvore por fazenda,
com subtotal por fazenda (sem total que some fazendas). Formulário do talhão: fazenda da lista cadastrada + "Cadastrar fazenda…"
(volta ao talhão sem perder o preenchido), área cultivável × polígono com motivo acima de 1 %, sistema e pivô/setor, situação.
CD-01det (detalhe): qualquer talhão, escolhido no seletor do cabeçalho (ou por #talhao=ID vindo da lista); resumo por safra
(cultivável · alocado · livre), parcelas em consulta com origem no Planejar safra, "Dividir em parcelas" leva ao SAF,
versões do polígono e primária "Definir polígono" (importar ou desenhar, simulados).
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
from areas.cadastros import H, bloco, mini, novo, sel, num, txt, dat, R, js

F_=H('false'); T_=H('true')
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
SIS=['Sequeiro','Pivô central','Gotejo']
NOVA_FAZ='Cadastrar fazenda…'
SAF_ATUAL=D2.SAFRAS[0]
SAF_ABERTAS=[s for s in D2.SAFRAS if not s['ro']]
def _br(n): return f'{n:,.2f}'.replace(',','X').replace('.',',').replace('X','.').rstrip('0').rstrip(',')
def _tal_de(local): return local.split('-')[0]

# ---------------- dados ----------------
def _faz_rows():
    out=[]
    for f in DC.FAZENDAS:
        mun,uf=f['mun'].rsplit('/',1)
        out.append(R(f['id'],dict(nome=f['nome'],empresa=f['empresa'],mun=mun,uf=uf,fuso=f['fuso'],area=f['area'],posse=f['posse'],arrend=f['arrend'],
                                  fim=f['fim'],custo=f['custo'],car=f['car'],matr=f['matr'],pend=f['pend'],sit=f['sit'])))
    return out
def _tal_rows():
    out=[]
    for t,ha,cult,fase,obs in D.TALHOES:
        sis,setor=DC.SISTEMA.get(obs,('Sequeiro',''))
        out.append(R(t,dict(t=t,faz='Santa Rita',sis=sis,setor=setor,decl=float(ha),calc=DC.CALC[t],motivo='',sit='Ativo',inat='',ver=DC.geo_vers(t)[-1][0])))
    out.append(R('B1',dict(t='B1',faz='Boa Vista',sis='Sequeiro',setor='',decl=120.0,calc='',motivo='',sit='Ativo',inat='',ver='')))
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
    return n

# ---------------- campos ----------------
SUB_TAL='Altere o talhão. A área do polígono só muda com nova versão, no detalhe do talhão; para tirar de uso, marque Inativo (nada é excluído).'
SUB_FAZ='Altere a fazenda. Para tirar de uso, marque Inativa: nada é excluído.'
# formulário de cadastro novo: texto de cadastro, sem instrução de inativar e sem campo que só existe depois (polígono, situação)
SUB_NOVO={'g_faz':'Cadastre a fazenda com empresa, município, área total e posse.',
          'g_tal':'Cadastre o talhão com fazenda, sistema e área cultivável; o polígono é definido depois, no detalhe do talhão.'}
NOVO_OCULTO={'g_faz':['sit'],'g_tal':['calc','sit'],'g_idt':['calc','sit']}
def campos_tal(fazs):
    return [txt('t','Identificação do talhão',help='Ex.: T8. Não pode repetir na mesma fazenda.'),
            sel('faz','Fazenda',fazs,**{'def':fazs[0]}),
            sel('sis','Sistema',SIS,**{'def':'Sequeiro'}),
            sel('setor','Pivô ou setor de irrigação',DC.SETORES,req=False,help='Ativo de irrigação de Máquinas, instalações e setores; o balanço hídrico usa este vínculo.'),
            num('decl','Área cultivável','ha',min=0.1,max=5000,help='Área plantável, sem carreador, APP e sede. Parcelas, doses e custo por hectare partem dela.'),
            num('calc','Área do polígono','ha',req=False,ro=True,help='Da versão atual do polígono; em branco enquanto não houver polígono.'),
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
            txt('car','CAR',req=False,help='Recibo do CAR. Em branco fica pendente: bloqueia só o crédito rural.'),
            txt('matr','Matrícula e cartório',req=False,help='Ex.: 12.401 · CRI de Rio Verde.'),
            txt('pend','Pendência nos documentos',req=False,help='Ex.: contrato sem registro em cartório. Não bloqueia o planejamento.'),
            sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]

# ---------------- JS comum às duas telas (regras do talhão, campos condicionais, cenário salvo) ----------------
TALJS=r'''
const TOL=0.01, NOVA_FAZ=__NOVA__, CKEY='talhao-os-cd01-v1';
function r1(n){ return Math.round(Number(n)*10)/10; }
function sgn(n,d){ return (n>0?'+':(n<0?'−':''))+nf(Math.abs(n),d); }
function precisaMotivo(d){ const a=g2num(d.decl), c=g2num(d.calc); return !isNaN(a)&&a>0&&!isNaN(c)&&Math.abs(c-a)/a>TOL; }
function difInfo(V){ const a=Number(V.decl)||0; if(!isnum(V.calc)||!a) return null; const c=Number(V.calc); return {d:r1(c-a),pct:Math.abs(c-a)/a,fora:Math.abs(c-a)/a>TOL}; }
function difParts(V){ const di=difInfo(V); if(!di) return [{k:'mut',t:'—'}]; const t=sgn(di.d,1)+' ha';
  if(!di.fora) return [{k:'txt',t:t},{k:'mut',t:nf(di.pct*100,1)+' %'}]; return V.motivo?[{k:'txt',t:t},{k:'mut',t:V.motivo}]:[chipc(t+' · informe o motivo','yellow')]; }
function geoParts(V){ return isnum(V.calc)?[{k:'txt',t:nf(V.calc,1)+' ha'}].concat(V.ver?[{k:'mut',t:V.ver}]:[]):[chipc('Sem polígono','yellow')]; }
function sisTxt(V){ return V.sis==='Sequeiro'||!V.sis?'Sequeiro':(V.sis+(V.setor?' · '+V.setor.replace('Bomba do ',''):'')); }
// campos que só aparecem sob condição diferente de igualdade (a cond do motor aceita só "igual a")
const CXF={posse3:d=>!!d.posse&&d.posse!=='Própria', irrig:d=>!!d.sis&&d.sis!=='Sequeiro', motivo:d=>precisaMotivo(d)};
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
    alvo='<main data-scroll="0" style="flex-grow: 1; padding: 18px 32px 22px;  display: grid;'
    assert s.count(alvo)==1, (fname,'main')
    open(p,'w').write(s.replace(alvo,'<main data-scroll="1" style="flex-grow: 1; padding: 18px 32px 22px; overflow-y: auto; min-height: 0; display: grid;',1))

# ================= CD-01 · Fazendas, áreas e talhões =================
GEO_MAPA=[('T1','poly','30,30 290,22 300,205 40,215'),('T2','poly','315,22 560,28 555,200 318,206'),
          ('T4','poly','40,250 300,240 305,430 45,438'),('T3','poly','320,240 555,236 560,430 325,434'),
          ('P1','circ','685,118,88'),('P2','circ','890,118,82'),
          ('T7','poly','590,245 780,240 785,430 595,434'),('C1','poly','800,240 970,236 975,430 805,434')]
MAPA_FID=next(f['id'] for f in DC.FAZENDAS if f['nome']=='Santa Rita')   # o mapa é desta fazenda (pelo id: sobrevive a renomear)
def _mapa(h=250):
    """mapa da Santa Rita colorido pela situação do polígono; clicar no talhão abre o formulário da mesma linha."""
    g=[]
    for tid,tp,geo in GEO_MAPA:
        at=f'fill="{H("mf_"+tid)}" stroke="{H("ms_"+tid)}" stroke-width="2" onClick="{H("mc_"+tid)}" style="cursor: pointer;"'
        if tp=='poly':
            pts=[tuple(map(float,p.split(','))) for p in geo.split()]
            cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            g.append(f'<polygon points="{geo}" {at}/>')
        else:
            cx,cy,r=map(float,geo.split(','))
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {at}/>')
        # rótulo fixo (texto interpolado não renderiza dentro de <text>); a cor do polígono carrega a situação
        g.append(f'<text x="{cx}" y="{cy+11}" text-anchor="middle" pointer-events="none" font-family="Sora, Manrope, sans-serif" font-size="32" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="5" paint-order="stroke">{tid}</text>')
    svg=(f'<svg viewBox="0 0 1000 460" width="100%" height="{h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa dos polígonos da Santa Rita" style="display: block; background: #DDE5D4; border-radius: 14px;">'
         '<rect x="0" y="0" width="1000" height="460" fill="#DDE5D4"/><path d="M0 225 C 250 219, 520 231, 1000 225" stroke="#B9C6AE" stroke-width="10" fill="none"/>'+''.join(g)+'</svg>')
    leg=' · '.join(f'<span style="color: {c}; font-weight: 700;">■ {esc(t)}</span>' for c,t in [('#1E7A4C','polígono validado'),('#8A5A00','diferença sem motivo'),('#5B6660','inativo')])
    return svg+f'<div style="font-size: 11.5px; color: {MUTED}; padding: 8px 4px 0;">{leg} · talhão sem polígono não aparece no mapa</div>'

def cd01():
    fname='CD-01.dc.html'; E._reset_screen(fname)
    fr=_faz_rows(); tr=_tal_rows(); nome={r['id']:r['v']['nome'] for r in fr}
    grupos=[dict(id='F_'+fid,ro=True,v=dict(t=n,fid=fid),s={},p={},kids=[t for t in tr if t['v']['faz']==n]) for fid,n in nome.items()]
    gf=grid([dict(k='nome',l='Fazenda',w=220),dict(k='area',l='Área total',t='num',a='r',u='ha',d=0),dict(k='cult',l='Área cultivável',t='num',a='r',u='ha',d=1),
             dict(k='posse',l='Posse',w=210),dict(k='docs',l='Documentos',w=230),dict(k='nt',l='Talhões ativos',t='num',a='r')],
        fr,gid='g_faz',total=False,search=False,add='Cadastrar fazenda',
        edit=dict(m='form',title='Fazenda',newTitle='Cadastrar fazenda',sub=SUB_FAZ,fields=CAMPOS_FAZ))
    gt=grid([dict(k='t',l='Fazenda · talhão',w=260),dict(k='decl',l='Área cultivável',t='num',a='r',u='ha',d=1),dict(k='geo',l='Polígono',w=180),
             dict(k='dif',l='Diferença',w=230),dict(k='parc',l=SAF_ATUAL['nome'])],
        grupos,gid='g_tal',tree=True,search=False,total=False,x0={g['id']:True for g in grupos},
        edit=dict(m='form',title='Talhão',newTitle='Cadastrar talhão',leafOnly=True,sub=SUB_TAL,fields=campos_tal(list(nome.values())+[NOVA_FAZ])))
    corpo=(bloco('Fazendas','Cadastre cada fazenda com empresa, município, posse e documentos; clique na linha para editar.',gf)
           # "Importar geometrias" saiu: mostrava uma prévia fixa e não mudava nada; importar ou desenhar o polígono é o
           # "Definir polígono" do detalhe de cada talhão (o toast do talhão novo já nomeia esse próximo passo)
           + bloco('Talhões por fazenda','Confira área cultivável, polígono e diferença de cada talhão; clique na linha para editar.',gt)
           + bloco('Mapa · Santa Rita','Confira a posição dos talhões com polígono; clique no talhão para editar.',_mapa()))
    js({},
       TALJS+'const FUSO_UF='+json.dumps(DC.FUSO_UF,ensure_ascii=False)+', FUSO_PAD='+json.dumps(DC.FUSOS[0],ensure_ascii=False)
       +', ALOC='+json.dumps(_aloc(),ensure_ascii=False)+', NPARC='+json.dumps(_nparc())+', MAPA='+json.dumps([g[0] for g in GEO_MAPA])
       +', MAPA_FID='+json.dumps(MAPA_FID)+';\n'+r'''
function tals(rows){ const o=[]; rows.forEach(g=>{ if(g.kids) g.kids.forEach(k=>o.push(k)); else o.push(g); }); return o; }
function arvore(fz,ts){ const gs=fz.map(f=>({id:'F_'+f.id,ro:true,v:{t:f.v.nome,fid:f.id},s:{},p:{},kids:[]}));
  ts.forEach(t=>{ let g=gs.find(x=>x.v.t===t.v.faz); if(!g){ g={id:'F_'+t.v.faz,ro:true,v:{t:t.v.faz,fid:''},s:{},p:{},kids:[]}; gs.push(g); } g.kids.push(t); }); return gs; }
// fazendas e talhões salvos (nesta ou na tela do detalhe) voltam ao abrir a tela
function cadIni(self){ if(self._ini) return; self._ini=1; const st=cadLer(); if(!st||!st.faz||!st.tal) return;
  const fz=st.faz.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}})); const gs=arvore(fz,st.tal.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}})));
  GR('g_faz').rows=fz; GR('g_tal').rows=gs; const x0={}; gs.forEach(g=>{ x0[g.id]=true; }); GR('g_tal').x0=x0; }
function cadSalvar(self){ cadGravar({faz:RW(self,'g_faz').map(linhaPk),tal:tals(RW(self,'g_tal')).map(linhaPk)}); }
function PREVALS(self,v){ cadIni(self); const fz=RW(self,'g_faz'), tr=RW(self,'g_tal'), ts=tals(tr);
  fz.forEach(r=>{ const V=r.v; const at=ts.filter(t=>t.v.faz===V.nome&&t.v.sit!=='Inativo');
    V.cult=r1(at.reduce((s,t)=>s+(Number(t.v.decl)||0),0)); V.nt=at.length;
    r.p.nome=[{k:'b',t:V.nome||''}].concat(V.sit==='Inativa'?[chipc('Inativa','gray')]:[]).concat([{k:'br'},{k:'mut',t:(V.empresa||'')+' · '+(V.mun||'')+'/'+(V.uf||'')}]);
    r.s.nome=V.nome||'';
    r.p.posse=V.posse==='Própria'||!V.posse?[{k:'txt',t:'Própria'}]:[{k:'txt',t:V.posse+(V.fim?' até '+br(V.fim):'')},{k:'br'},{k:'mut',t:(V.arrend||'')+(isnum(V.custo)?' · '+nfa(V.custo)+' sc/ha/ano':'')}];
    r.s.posse=V.posse||'';
    const d=[]; if(!V.car) d.push(chipc('CAR pendente','yellow')); if(!V.matr) d.push(chipc('Matrícula pendente','yellow'));
    if(V.pend) d.push(chipc('Documento pendente','yellow'),{k:'br'},{k:'mut',t:V.pend});
    r.p.docs=d.length?d:[{k:'txt',t:'CAR e matrícula'},{k:'br'},{k:'mut',t:V.matr}]; r.s.docs=d.length?'pendente':'em dia'; });
  tr.forEach(g=>{ if(!g.kids) return; const f=fz.find(x=>x.id===g.v.fid)||fz.find(x=>x.v.nome===g.v.t); if(f) g.v.t=f.v.nome;
    const at=g.kids.filter(k=>k.v.sit!=='Inativo'); const sub=r1(at.reduce((s,k)=>s+(Number(k.v.decl)||0),0)); g.v.decl=sub;
    g.p.t=[{k:'b',t:g.v.t}].concat(f&&f.v.sit==='Inativa'?[chipc('Inativa','gray')]:[]).concat([{k:'mut',t:at.length?(at.length+(at.length>1?' talhões ativos':' talhão ativo')):'sem talhão ativo'}])
      .concat(!g.kids.length&&(!f||f.v.sit!=='Inativa')?[{k:'act',t:'Cadastrar talhão',fn:'tal_new:'+(f?f.id:''),lk:true}]:[]); g.s.t=g.v.t;
    g.p.decl=[{k:'b',t:nf(sub,1)+' ha'}]; g.s.decl=String(sub);
    const sem=at.filter(k=>!isnum(k.v.calc)).length; g.p.geo=[{k:'mut',t:sem?(sem+' sem polígono'):''}]; g.p.dif=[{k:'mut',t:''}]; g.p.parc=[{k:'mut',t:''}];
    g.kids.forEach(r=>{ const V=r.v; const ina=V.sit==='Inativo';
      r.p.t=[{k:'b',t:V.t||''}].concat(ina?[chipc('Inativo','gray')]:[]).concat([{k:'mut',t:sisTxt(V)},{k:'link',t:'Abrir ›',h:'CD-01det.dc.html#talhao='+encodeURIComponent(r.id)}]);
      r.s.t=V.t||'';
      r.p.decl=ina?[{k:'mut',t:nf(V.decl,1)+' ha'}]:[{k:'txt',t:nf(V.decl,1)+' ha'}];
      r.p.geo=geoParts(V); r.s.geo=isnum(V.calc)?'Validado':'Sem polígono';
      r.p.dif=difParts(V); const di=difInfo(V); r.s.dif=di?String(di.d):'';
      const n=ina?0:(NPARC[r.id]||0); r.p.parc=n?[{k:'link',t:(n>1?n+' parcelas':'talhão inteiro')+' ›',h:'SAF.dc.html'}]:[{k:'mut',t:'sem cultivo'}]; r.s.parc=String(n); }); });
  // mapa: cor pela situação do polígono; talhão que não é da fazenda do mapa não aparece nele
  const fm0=fz.find(f=>f.id===MAPA_FID); const nm=fm0?fm0.v.nome:'';
  MAPA.forEach(id=>{ const r0=g2find(tr,id); const r=r0&&r0.v.faz===nm?r0:null; const V=r?r.v:null; const tem=V&&isnum(V.calc); const ina=V&&V.sit==='Inativo'; const di=V&&difInfo(V);
    const cor=!tem?['#E9EEE6','#8A968E']:(ina?['#C9CFCB','#5B6660']:((di&&di.fora&&!V.motivo)?['#FFD500','#8A5A00']:['#8FD67F','#1E7A4C']));
    v['mf_'+id]=cor[0]; v['ms_'+id]=cor[1]; });
  // estado do cadastro no cabeçalho
  const sem=ts.filter(t=>t.v.sit!=='Inativo'&&!isnum(t.v.calc)), mot=ts.filter(t=>t.v.sit!=='Inativo'&&(difInfo(t.v)||{}).fora&&!t.v.motivo);
  const docs=fz.filter(f=>f.v.sit!=='Inativa'&&(!f.v.car||!f.v.matr||f.v.pend)); const ps=[];
  if(sem.length) ps.push(sem.length===1?(sem[0].v.t+' sem polígono'):(sem.length+' talhões sem polígono'));
  if(docs.length) ps.push(docs.length===1?('documentos da '+docs[0].v.nome+' pendentes'):(docs.length+' fazendas com documento pendente'));
  if(mot.length) ps.push(mot.length+(mot.length>1?' diferenças sem motivo':' diferença sem motivo'));
  const cs=chipSt(ps.length?'yellow':'green'); v.cd_st=ps.length?ps.join(' · '):'Cadastro em dia'; v.cd_stst=cs[0]; v.cd_stdot=cs[1]; }
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
function EXTRAVALS(self,v){ simv(self,v); const fz=RW(self,'g_faz'), ts=tals(RW(self,'g_tal'));
  // linha da fazenda na árvore é agrupador: não abre formulário
  (v.g_tal_rows||[]).forEach(x=>{ if(String(x.id).indexOf('F_')===0){ x.cls='g2r'; x.tab='-1'; x.open=()=>{}; x.key=()=>{}; } });
  // ---- fazenda ----
  cxForm(self,v,'g_faz');
  const uf=cxCampo(v,'g_faz','uf'); if(uf&&!uf.dis) uf.set=(e)=>{ const u=e.target.value; draftSet(self,'g_faz',{uf:u,fuso:FUSO_UF[u]||FUSO_PAD}); };
  valida2(self,v,'g_faz',(d,fm)=>fazErros(self,d,fm));
  const FF=v.g_faz_F; if(FF&&FF.open&&self._stash){ FF.sub='Ao salvar, você volta ao talhão '+(self._stash.draft.t||'em cadastro')+' com esta fazenda escolhida; o que já foi preenchido fica mantido.';
    ['close','cancel','discard','key'].forEach(k=>{ const o=FF[k]; if(o) FF[k]=(e)=>{ o(e); if(!g2st(self,'g_faz').fm) retoma(self,null); }; }); }
  // ---- talhão ----
  cxForm(self,v,'g_tal');
  const ff=cxCampo(v,'g_tal','faz'); if(ff&&!ff.dis){ const at=fz.filter(f=>f.v.sit!=='Inativa').map(f=>f.v.nome); if(ff.v&&ff.v!==NOVA_FAZ&&at.indexOf(ff.v)<0) at.push(ff.v);
    ff.opts=at.map(n=>({v:n,t:n})).concat([{v:NOVA_FAZ,t:NOVA_FAZ}]);
    ff.set=(e)=>{ const val=e.target.value; if(val!==NOVA_FAZ){ draftSet(self,'g_tal',{faz:val}); return; }
      self._stash=Object.assign({},g2st(self,'g_tal').fm); g2set(self,'g_tal',{fm:null}); g2new(self,GR('g_faz')); }; }
  valida2(self,v,'g_tal',(d,fm)=>{ const o=fm.rid?ts.find(t=>t.id===fm.rid):null; self._sit0=o?o.v.sit:''; return talErros(d,fm,{tals:ts,fazs:fz,aloc:ALOC}); });
  v.tal_new=(fid)=>{ const f=fz.find(x=>x.id===fid); g2new(self,GR('g_tal')); if(!f) return; const cur=g2st(self,'g_tal').fm;
    g2set(self,'g_tal',{fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,{faz:f.v.nome}),orig:Object.assign({},cur.orig,{faz:f.v.nome})})}); };
  const fmp=fz.find(f=>f.id===MAPA_FID);
  MAPA.forEach(id=>{ v['mc_'+id]=()=>{ const r=g2find(RW(self,'g_tal'),id); if(r&&fmp&&r.v.faz===fmp.v.nome) g2open(self,GR('g_tal'),id,null); }; });
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_faz'){ cxLimpa('g_faz',r); const old=self._fazOld; const tr=g2clone(RW(self,'g_tal')); g2set(self,'g_faz',{rows:rows});
      if(isNew){ tr.push({id:'F_'+r.id,ro:true,v:{t:r.v.nome,fid:r.id},s:{},p:{},kids:[]}); const x=Object.assign({},g2st(self,'g_tal').x||GR('g_tal').x0||{}); x['F_'+r.id]=true; g2set(self,'g_tal',{rows:tr,x:x}); }
      else if(old&&old!==r.v.nome){ tals(tr).forEach(t=>{ if(t.v.faz===old){ t.v.faz=r.v.nome; t.s.faz=r.v.nome; } }); g2set(self,'g_tal',{rows:tr}); }
      if(isNew&&self._stash){ retoma(self,r.v.nome); self.setState({g2toast:'Fazenda '+r.v.nome+' cadastrada. Continue o talhão.'}); }
      else self.setState({g2toast:isNew?('Fazenda '+r.v.nome+' cadastrada. Próximo passo: cadastrar os talhões dela.'):(r.v.sit==='Inativa'?(r.v.nome+' inativa: sai do Planejar safra; talhões e O.S. antigas seguem consultáveis.'):('Salvo: '+r.v.nome+'.'))}); }
    if(gid==='g_tal'){ cxLimpa('g_tal',r); if(r.v.sit==='Inativo'){ if(!r.v.inat) r.v.inat=HOJE; } else r.v.inat='';
      const f=RW(self,'g_faz').find(x=>x.v.nome===r.v.faz); const gk='F_'+(f?f.id:r.v.faz); const cur=rows.find(g=>g.kids&&g.kids.some(k=>k.id===r.id));
      if(!cur||cur.id!==gk){ const i=rows.indexOf(r); if(i>=0) rows.splice(i,1); if(cur) cur.kids.splice(cur.kids.indexOf(r),1);
        let g=rows.find(x=>x.id===gk); if(!g){ g={id:gk,ro:true,v:{t:r.v.faz,fid:f?f.id:''},s:{},p:{},kids:[]}; rows.push(g); } g.kids.push(r); }
      const x=Object.assign({},g2st(self,'g_tal').x||GR('g_tal').x0||{}); x[gk]=true; g2set(self,'g_tal',{rows:rows,x:x,fl:r.id});
      self.setState({g2toast:isNew?(r.v.t+' cadastrado na '+r.v.faz+'. Próximo passo: definir o polígono no detalhe do talhão.'):talToast(r,self._sit0)}); }
    cadSalvar(self); }; }
''')
    # folga para uma fazenda e um talhão novos sem rolar; além disso o corpo rola dentro do artboard (_rolagem)
    ui37.H_OVR.pop(fname,None); HEIGHTS37[fname]=1540
    shell37('CD-01','Fazendas, áreas e talhões',corpo,fname=fname,
            subtitle='Cadastre fazendas e talhões com área cultivável, polígono e documentos; pendências não bloqueiam o planejamento.',
            status=None,primary_html=novo('g_tal','Cadastrar talhão'),search=False)
    _injeta(fname,'Fazendas, áreas e talhões',_chip_dyn('cd')); _rolagem(fname)

# ================= CD-01det · detalhe de qualquer talhão =================
def _parc_rows(tal_ids):
    """grupos por talhão × safra (safra com cultivo do talhão ou safra aberta) com as parcelas do Planejar safra, em consulta."""
    rows=[]; x0={}
    for t in tal_ids:
        for s in D2.SAFRAS:
            cs=[c for c in D2.CULTIVOS[s['id']] if _tal_de(c['local'])==t]
            if not cs and s['ro']: continue
            kids=[]
            for c in cs:
                pl=D2.PLANO.get(c['plano']) if c['plano'] else None
                kids.append(R(c['id'],dict(tal=t,parc=c['local'],tipo=c['tipo'],safra=s['nome'],cult=c['cultura'],var=c['variedade'],cv=c['cultura']+' · '+c['variedade'],
                                           area=c['area'],plantio=c['plantio'],meta=f"{_br(c['meta'])} {c['un_meta']}",plano=(f"{pl['nome']} v{pl['versao']}" if pl else 'sem plano'),
                                           geo0=D.GEO_PARC.get(c['id'],''),geo=''),ro=True))
            gid=f'G_{t}_{s["id"]}'
            rows.append(dict(id=gid,ro=True,grp=True,v=dict(tal=t,sid=s['id'],safra=s['nome'],estado=s['estado']),s={},p={},kids=kids))
            if not s['ro']: x0[gid]=True
    return rows,x0
def _painel_poligono():
    lab=f'font-size: 12px; font-weight: 600; color: {MUTED};'
    seg=f'<div role="group" aria-label="Como definir" style="display: inline-flex; gap: 2px; padding: 3px; border-radius: 999px; background: #EEF1EE;">' \
        f'<button type="button" onClick="{H("pg_imp")}" style="{H("pg_st_imp")}">Importar arquivo</button><button type="button" onClick="{H("pg_des")}" style="{H("pg_st_des")}">Desenhar no mapa</button></div>'
    return (f'<sc-if value="{H("pg_open")}" hint-placeholder-val="{F_}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar" onClick="{H("pg_fechar")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-label="{H("pg_titulo")}" onKeyDown="{H("pg_key")}" style="position: relative; width: 460px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{H("pg_titulo")}</h2>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pg_fechar")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("pg_sub")}</div>'
            f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="{lab}">Como definir</span>{seg}</div>'
            f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: 1px dashed {LINE}; border-radius: 10px; font-size: 13px;"><span style="flex-grow: 1;">{H("pg_desc")}</span>'
            f'<button type="button" onClick="{H("pg_gerar")}" style="{_MINI}">Gerar prévia</button></div>'
            f'<sc-if value="{H("pg_hasprev")}" hint-placeholder-val="{F_}"><div style="display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border-radius: 10px; background: {BG};">'
            f'<div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">PRÉVIA</div>'
            f'<sc-for list="{H("pg_rows")}" as="x" hint-placeholder-count="3"><div style="display: flex; justify-content: space-between; gap: 10px; padding: 5px 0; border-bottom: 1px solid {LINE}; font-size: 13px;"><span style="color: {MUTED};">{H("x.t")}</span><b>{H("x.v")}</b></div></sc-for>'
            f'<sc-for list="{H("pg_checks")}" as="x" hint-placeholder-count="2"><div style="font-size: 12.5px; color: {ACC}; font-weight: 700; padding-top: 4px;">✓ {H("x.t")}</div></sc-for></div></sc-if>'
            f'<sc-if value="{H("pg_needmot")}" hint-placeholder-val="{F_}"><div style="display: flex; flex-direction: column; gap: 4px;"><label for="pg_mot" style="{lab}">Motivo da diferença</label>'
            f'<select id="pg_mot" value="{H("pg_mot")}" onChange="{H("pg_setmot")}" style="{H("pg_motst")}"><sc-for list="{H("pg_mopts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<span style="font-size: 11.5px; color: {MUTED};">Diferença acima de 1 % pede o motivo.</span></div></sc-if>'
            f'<sc-if value="{H("pg_haserr")}" hint-placeholder-val="{F_}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: #FDE8E6; color: #B42318; font-size: 12.5px; font-weight: 700;">{H("pg_err")}</div></sc-if>'
            f'<div style="flex-grow: 1;"></div>'
            f'<sc-if value="{H("pg_warn")}" hint-placeholder-val="{F_}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: #FFF3D6; color: #8A5A00; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
            f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pg_descartar")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("pg_continuar")}" style="{E._MINIP}">Continuar editando</button></div></div></sc-if>'
            f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("pg_fechar")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("pg_salvar")}" style="{BTN_ST(True,True)}">Salvar polígono</button></div></aside></div></sc-if>')
def cd01det():
    fname='CD-01det.dc.html'; E._reset_screen(fname); PARENT37[fname]='CD-01.dc.html'
    fr=_faz_rows(); tr=_tal_rows(); fazs=[r['v']['nome'] for r in fr]
    prow,px0=_parc_rows([r['id'] for r in tr if r['v']['faz']=='Santa Rita'])
    gi=grid([dict(k='faz',l='Fazenda',w=230),dict(k='sis',l='Sistema',w=190),dict(k='decl',l='Área cultivável',t='num',a='r',u='ha',d=1),
             dict(k='geo',l='Polígono',w=170),dict(k='dif',l='Diferença',w=220),dict(k='sit',l='Situação')],
        tr,gid='g_idt',search=False,total=False,headtools=False,
        edit=dict(m='form',title='Talhão',newTitle='Cadastrar talhão',sub=SUB_TAL,fields=campos_tal(fazs)))
    gp=grid([dict(k='parc',l='Safra · parcela',w=250),dict(k='cult',l='Cultura · variedade'),dict(k='area',l='Área',t='num',a='r',u='ha',d=1),
             dict(k='livre',l='Livre'),dict(k='plantio',l='Plantio',t='date'),dict(k='geo',l='Polígono')],
        prow,gid='g_parc',tree=True,search=False,total=False,x0=px0,
        edit=dict(m='origin',title='Parcela',leafOnly=True,
            fields=[txt('parc','Parcela',ro=True),txt('safra','Safra',ro=True),txt('cv','Cultura e variedade',ro=True),num('area','Área','ha',ro=True),
                    dat('plantio','Plantio',ro=True),txt('meta','Meta de produtividade',ro=True),txt('plano','Plano agronômico',ro=True),txt('geo','Polígono',ro=True)]))
    link_mini=f'{_MINI} text-decoration: none; display: inline-block;'
    geo_html=(f'<div style="display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 18px; align-items: start;">'
              f'<div style="display: flex; flex-direction: column; gap: 6px;"><div style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("geo_leg")}</div>'
              f'<div role="img" aria-label="{H("geo_aria")}" style="display: flex; height: 190px; background: #DDE5D4; clip-path: polygon(2% 5%, 97% 0, 100% 95%, 0 100%);">'
              f'<sc-for list="{H("geo_parts")}" as="g" hint-placeholder-count="2"><div style="{H("g.st")}"><span style="font-family: {DISP}; font-size: 22px; font-weight: 700;">{H("g.t")}</span><span style="font-size: 12px; font-weight: 700;">{H("g.s")}</span></div></sc-for></div></div>'
              f'<div style="display: flex; flex-direction: column;"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em; padding-bottom: 4px;">VERSÕES DO POLÍGONO</div>'
              f'<sc-for list="{H("geo_vers")}" as="x" hint-placeholder-count="2"><div style="display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; border-top: 1px solid {LINE};">'
              f'<span style="{H("x.cst")}"><span style="{H("x.cdot")}"></span>{H("x.chip")}</span><div style="display: flex; flex-direction: column; gap: 1px; min-width: 0;"><b style="font-size: 13px;">{H("x.tit")}</b><span style="font-size: 12px; color: {MUTED};">{H("x.sub")}</span></div></div></sc-for>'
              f'<sc-if value="{H("geo_novers")}" hint-placeholder-val="{F_}"><div style="font-size: 12.5px; color: {MUTED}; padding: 8px 0; border-top: 1px solid {LINE};">Sem polígono: o planejamento usa a área cultivável; mapa de taxa variável fica bloqueado.</div></sc-if></div></div>')
    parc_html=(f'<sc-if value="{H("det_parc_tem")}" hint-placeholder-val="{T_}">{gp}</sc-if>'
               f'<sc-if value="{H("det_parc_vazio")}" hint-placeholder-val="{F_}"><div style="font-size: 13px; color: {MUTED}; padding: 4px 4px 2px;">{H("det_parc_msg")}</div></sc-if>')
    corpo=(f'<sc-if value="{H("det_nf")}" hint-placeholder-val="{F_}">'+bloco('Talhão não encontrado','Escolha um talhão no seletor do cabeçalho.','')+'</sc-if>'
           + f'<sc-if value="{H("det_ok")}" hint-placeholder-val="{T_}">'
           + bloco('Talhão','Confira fazenda, sistema, áreas e situação; clique na linha para editar.',gi)
           + bloco('Parcelas por safra','Confira a área cultivável, alocada e livre de cada safra; as parcelas mudam no Planejar safra.',parc_html,
                   acao=f'<sc-if value="{H("det_ativo")}" hint-placeholder-val="{T_}"><a href="SAF.dc.html" style="{link_mini}">Dividir em parcelas</a></sc-if>')
           + bloco('Geometria','Confira o polígono atual e as versões mantidas para as O.S. já emitidas.',geo_html,
                   acao=f'<sc-if value="{H("det_planok")}" hint-placeholder-val="{F_}"><button type="button" onClick="{H("pg_nova")}" style="{_MINI}">Nova versão do polígono</button></sc-if>')
           + '</sc-if>')
    E.EXTRA.append(_painel_poligono())
    fazjs=[dict(id=r['id'],v=r['v']) for r in fr]
    vers={t:[list(x) for x in DC.geo_vers(t)] for t in DC.CALC}
    safo=[dict(sid=s['id'],nome=s['nome'],estado=s['estado'],faz=s['fazenda']) for s in SAF_ABERTAS]
    js({},TALJS+'const FAZ0='+json.dumps(fazjs,ensure_ascii=False)+', VERS0='+json.dumps(vers,ensure_ascii=False)+', SAFOPEN='+json.dumps(safo,ensure_ascii=False)
       +', MOTIVOS='+json.dumps(DC.MOTIVOS_DIF,ensure_ascii=False)
       # área cultivável da época de cada safra encerrada (registro fechado não é recalculado com a área atual)
       +', CULT_EP='+json.dumps({s['id']:{t:float(ha) for t,ha,*_ in D.TALHOES} for s in D2.SAFRAS if s['ro']})+';\nlet FAZL=FAZ0;\n'+r'''
const HATCH='repeating-linear-gradient(45deg,#C9CFCB 0 7px,#EEF1EE 7px 14px)';
function detIni(self){ if(self._ini) return; self._ini=1; const st=cadLer();
  if(st&&st.faz) FAZL=st.faz.map(x=>({id:x.id,v:Object.assign({},x.v)}));
  if(st&&st.tal) GR('g_idt').rows=st.tal.map(x=>({id:x.id,v:Object.assign({},x.v),s:{},p:{}}));
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
  RW(self,'g_idt').forEach(r=>{ const V=r.v; const F=FAZL.find(f=>f.v.nome===V.faz); const fu=F&&F.v.fuso?((/\((.*)\)/.exec(F.v.fuso)||[])[1]||F.v.fuso):'';
    r.p.faz=[{k:'b',t:V.faz||''}].concat(F?[{k:'br'},{k:'mut',t:F.v.mun+'/'+F.v.uf+(fu?' · fuso '+fu:'')}]:[]); r.s.faz=V.faz||'';
    r.p.sis=[{k:'txt',t:V.sis||'Sequeiro'}].concat(V.setor&&V.sis!=='Sequeiro'?[{k:'br'},{k:'mut',t:V.setor}]:[]); r.s.sis=V.sis||'';
    r.p.geo=geoParts(V); r.s.geo=isnum(V.calc)?'Validado':'Sem polígono'; r.p.dif=difParts(V); r.s.dif='';
    r.p.sit=[V.sit==='Inativo'?chipc('Inativo desde '+br(V.inat||HOJE),'gray'):chipc('Ativo','green')]; r.s.sit=V.sit||''; });
  RW(self,'g_parc').forEach(g=>{ if(!g.grp) return; const Tg=g2find(RW(self,'g_idt'),g.v.tal); const ks=g.kids||[];
    const A=r1(ks.reduce((s,k)=>s+(Number(k.v.area)||0),0)); const ab=aberta(g.v.sid); const ep=(CULT_EP[g.v.sid]||{})[g.v.tal];
    const cult=ab?(Tg?Number(Tg.v.decl)||0:0):(ep!==undefined?ep:A); const L=r1(cult-A);
    g.p.parc=[{k:'b',t:g.v.safra},{k:'mut',t:g.v.estado}]; g.s.parc=g.v.safra;
    g.p.area=[{k:'txt',t:nfa(A)+' de '+nfa(cult)+' ha'}]; g.s.area=String(A);
    // safra encerrada: resumo da época, sem chip de pendência
    g.p.livre=[Math.abs(L)<=0.005?chipc('Área conferida','green'):(!ab?{k:'mut',t:(L>0?nfa(L)+' ha sem cultivo':'excedeu '+nfa(-L)+' ha')}:(L<0?chipc('Excede em '+nfa(-L)+' ha','red'):chipc(nfa(L)+' ha livres','yellow')))]; g.s.livre=String(L);
    g.p.cult=[{k:'mut',t:ks.length?'':'sem cultivo'}]; g.p.plantio=[{k:'mut',t:''}]; g.p.geo=[{k:'mut',t:''}];
    ks.forEach(k=>{ const V=k.v; const gs=pgeoOf(self,k,Tg); V.geo=gs;
      k.p.parc=[{k:'b',t:V.parc},{k:'mut',t:V.tipo==='Parcela'?'parcela':'talhão inteiro'}]; k.s.parc=V.parc;
      k.p.cult=[{k:'txt',t:V.cv}]; k.s.cult=V.cv; k.p.livre=[{k:'mut',t:''}];
      k.p.geo=[gs==='Validada'?chipc('Validada','green'):(gs==='Polígono do talhão'?{k:'mut',t:'polígono do talhão'}:chipc('Sem polígono','yellow'))]; k.s.geo=gs;
      k.o=[{t:'Planejar safra › '+V.safra+' › '+V.parc,h:'SAF.dc.html'}]; }); }); }
function geoVals(self,v,T){ const ina=T.v.sit==='Inativo'; const cal=isnum(T.v.calc); const dec=Number(T.v.decl)||0;
  const g=RW(self,'g_parc').find(x=>x.grp&&x.v.tal===T.id&&x.v.sid===SAFOPEN[0].sid); const ks=((g&&g.kids)||[]).filter(k=>k.v.tipo==='Parcela');
  const cell=(t,s,w,ok)=>({t:t,s:s,st:'flex:0 0 '+w+'%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-width:0;box-sizing:border-box;border-right:2px dashed rgba(255,255,255,.9);color:#15201A;background:'+(ina?'#DADFDB':(ok?'#8FD67F':HATCH))+';'});
  let parts;
  if(ks.length&&cal){ const tot=ks.reduce((a,k)=>a+(Number(k.v.area)||0),0); const base=Math.max(tot,dec)||1;
    parts=ks.map(k=>{ const gs=pgeoOf(self,k,T); return cell(k.v.parc,nfa(k.v.area)+' ha · '+(gs==='Validada'?'validada':'sem polígono'),r1(k.v.area/base*100),gs==='Validada'); });
    if(tot<dec-0.005) parts.push(cell('Livre',nfa(r1(dec-tot))+' ha',r1((dec-tot)/base*100),true)); }
  else parts=[cell(T.v.t,cal?(nf(T.v.calc,1)+' ha · '+(T.v.ver||'')):'sem polígono',100,cal)];
  v.geo_parts=parts; v.geo_leg=ks.length&&cal?('Divisão da '+SAFOPEN[0].nome):(cal?'Polígono do talhão':'Talhão sem polígono');
  v.geo_aria=v.geo_leg+': '+parts.map(p=>p.t+' '+p.s).join('; ');
  const vs=versOf(self,T.id); const rv=vs.slice().reverse();
  v.geo_vers=rv.map((x,i)=>{ const c=chipSt(i?'gray':'green'); return {chip:i?'Consulta':'Atual',cst:c[0],cdot:c[1],tit:x[0]+' · '+nf(x[3],1)+' ha',
    sub:br(x[1])+' · '+x[2]+(i?' · O.S. emitidas antes de '+br(rv[i-1][1]):'')}; });
  v.geo_novers=!vs.length; }
function pgVals(self,v,T){ const pg=self.state.pg; v.pg_open=!!pg; const set=(p)=>self.setState({pg:Object.assign({},self.state.pg,p)});
  const abrir=(p,nova)=>{ const slug=String(p.alvo).toLowerCase().replace(/[^a-z0-9]+/g,'_');
    self.setState({pg:{t:T.id,alvo:p.alvo,art:p.art,cid:p.cid,ref:p.ref,safra:p.safra||'',nova:!!nova,modo:'imp',arq:'poligono_'+slug+'.kml',prev:null,mot:'',err:'',warn:false}}); };
  v.pg_abrir=()=>{ const p=pendDe(self,T); if(p) abrir(p,false); };
  v.pg_nova=()=>abrir({alvo:T.v.t,art:'do',cid:null,ref:Number(T.v.decl)||0},true);
  if(!pg){ v.pg_rows=[]; v.pg_checks=[]; v.pg_mopts=[]; return; }
  const ON='font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;border:0;cursor:pointer;background:#FFFFFF;color:#15201A;box-shadow:0 1px 2px rgba(21,32,26,.12);';
  const OFF='font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;border:0;cursor:pointer;background:transparent;color:#65736A;';
  v.pg_titulo=(pg.nova?'Nova versão do polígono do ':('Definir polígono '+pg.art+' '))+pg.alvo;
  const vs=versOf(self,pg.t); const ult=vs.length?vs[vs.length-1][0]:'';
  v.pg_sub=(pg.cid?('Parcela de '+nfa(pg.ref)+' ha do '+T.v.t+' na '+pg.safra+'. '):('Área cultivável de '+nfa(pg.ref)+' ha. '))+(ult?('Salvar cria uma nova versão; a '+ult+' fica em consulta para as O.S. já emitidas.'):'Salvar cria a versão v1 e libera o mapa de taxa variável.');
  v.pg_st_imp=pg.modo==='imp'?ON:OFF; v.pg_st_des=pg.modo==='des'?ON:OFF;
  v.pg_imp=()=>set({modo:'imp',prev:null,err:'',mot:''}); v.pg_des=()=>set({modo:'des',prev:null,err:'',mot:''});
  v.pg_desc=pg.modo==='imp'?('Arquivo '+pg.arq+' (simulado: nenhum arquivo real é lido)'):'Marque os vértices sobre a imagem e feche o polígono (simulado)';
  v.pg_gerar=()=>set({prev:{area:r1(pg.ref*(pg.modo==='imp'?0.997:0.974))},err:'',mot:''});
  const pv=pg.prev; v.pg_hasprev=!!pv; const pct=pv&&pg.ref?Math.abs(pv.area-pg.ref)/pg.ref:0; const need=!!pv&&pct>TOL;
  v.pg_rows=pv?[{t:'Área do polígono',v:nf(pv.area,1)+' ha'},{t:(pg.cid?'Área da parcela':'Área cultivável'),v:nfa(pg.ref)+' ha'},{t:'Diferença',v:sgn(r1(pv.area-pg.ref),1)+' ha · '+nf(pct*100,1)+' %'}]:[];
  v.pg_checks=pv?[{t:pg.cid?('Dentro do perímetro do '+T.v.t):('Dentro do perímetro da '+T.v.faz)},{t:'Sem sobreposição com outros talhões e parcelas'}]:[];
  v.pg_needmot=need; v.pg_mot=pg.mot||''; v.pg_setmot=(e)=>set({mot:e.target.value,err:''});
  v.pg_mopts=[{v:'',t:'Escolha…'}].concat(MOTIVOS.map(m=>({v:m,t:m})));
  v.pg_motst='font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;background:#FFFFFF;color:#15201A;border:1px solid '+(pg.err&&need&&!pg.mot?'#B42318':'#E4E9E5')+';';
  v.pg_err=pg.err||''; v.pg_haserr=!!pg.err; v.pg_warn=!!pg.warn;
  v.pg_fechar=()=>{ const c=self.state.pg; if(c&&c.prev&&!c.warn){ set({warn:true}); return; } self.setState({pg:null}); };
  v.pg_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.pg_fechar(); } };
  v.pg_descartar=()=>self.setState({pg:null}); v.pg_continuar=()=>set({warn:false});
  v.pg_salvar=()=>{ const c=self.state.pg; if(!c.prev){ set({err:'Gere a prévia antes de salvar.'}); return; }
    if(need&&!c.mot){ set({err:'Informe o motivo da diferença de '+nf(pct*100,1)+' %.'}); return; }
    const vs2=versOf(self,c.t); const n=vs2.length?(parseInt(String(vs2[vs2.length-1][0]).slice(1),10)+1):1; const vn='v'+n;
    const rows=g2clone(RW(self,'g_idt')); const R2=g2find(rows,c.t);
    const orig=(c.modo==='imp'?('Importado · '+c.arq):'Desenhado no mapa')+(c.cid?' · '+c.alvo:'')+(need?' · '+c.mot:'');
    const area=c.cid&&isnum(R2.v.calc)?Number(R2.v.calc):c.prev.area;
    const vers=Object.assign({},self._vers0,self.state.vers||{}); vers[c.t]=vs2.concat([[vn,HOJE,orig,area]]);
    const pgeo=Object.assign({},self._pgeo0,self.state.pgeo||{}); R2.v.ver=vn;
    if(c.cid) pgeo[c.cid]='Validada'; else { R2.v.calc=c.prev.area; R2.v.motivo=need?c.mot:''; }
    g2set(self,'g_idt',{rows:rows});
    self.setState({pg:null,vers:vers,pgeo:pgeo,g2toast:'Polígono '+c.art+' '+c.alvo+' salvo (simulado): '+vn+' do '+R2.v.t+' é a atual'+(vs2.length?('; a '+vs2[vs2.length-1][0]+' fica em consulta para as O.S. já emitidas.'):'; mapa de taxa variável liberado.')});
    detSalvar(self); }; }
function EXTRAVALS(self,v){ const t=curT(self); const T=g2find(RW(self,'g_idt'),t); const ina=!!T&&T.v.sit==='Inativo';
  // seletor do cabeçalho: o talhão mostrado é sempre o escolhido (nunca um registro em silêncio)
  v.det_t=T?t:''; v.det_opts=(T?[]:[{v:'',t:'Escolha o talhão'}]).concat(RW(self,'g_idt').map(r=>({v:r.id,t:r.v.t+' · '+r.v.faz+(r.v.sit==='Inativo'?' · inativo':'')})));
  v.det_set=(e)=>{ const id=e.target.value; if(!id) return; try{ history.replaceState(null,'','#talhao='+encodeURIComponent(id)); }catch(x){}
    g2set(self,'g_idt',{fm:null}); g2set(self,'g_parc',{fm:null}); self.setState({det_t:id,pg:null}); };
  v.det_ok=!!T; v.det_nf=!T; v.det_ativo=!!T&&!ina; v.det_crumb=T?(T.v.t+' · '+nfa(T.v.decl)+' ha'):'Talhão';
  const p=T&&!ina?pendDe(self,T):null; v.det_pend=!!p; v.det_planok=!!T&&!ina&&!p;
  v.det_prim=p?('Definir polígono '+p.art+' '+p.alvo):''; v.det_plan='Planejar '+(T?T.v.t:'')+' na safra';
  // talhão inativo: a primária é reativar (abre o formulário do talhão com a Situação em Ativo, focada)
  v.det_inat=ina; v.det_reat='Reativar '+(T?T.v.t:'');
  v.det_reativar=()=>{ if(!T) return; g2open(self,GR('g_idt'),T.id,null); draftSet(self,'g_idt',{sit:'Ativo'});
    setTimeout(()=>{ try{ const s=document.getElementById('fx_g_idt_sit'); if(s) s.focus(); }catch(e){} },60); };
  const st=!T?['Escolha um talhão','gray']:(ina?['Inativo desde '+br(T.v.inat||HOJE),'gray']:(p?[p.alvo+' sem polígono','yellow']:['Polígono validado','green']));
  const cs=chipSt(st[1]); v.det_st=st[0]; v.det_stst=cs[0]; v.det_stdot=cs[1];
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
  if(T) geoVals(self,v,T); else { v.geo_parts=[]; v.geo_vers=[]; v.geo_novers=false; }
  pgVals(self,v,T||{id:'',v:{}}); }
''')
    # folga para duas versões novas do polígono com tudo expandido; além disso o corpo rola dentro do artboard (_rolagem)
    ui37.H_OVR.pop(fname,None); HEIGHTS37[fname]=1140
    prim=(f'<sc-if value="{H("det_pend")}" hint-placeholder-val="{T_}"><button type="button" onClick="{H("pg_abrir")}" style="{BTN_ST(True)}">{H("det_prim")}</button></sc-if>'
          f'<sc-if value="{H("det_planok")}" hint-placeholder-val="{F_}"><a href="SAF.dc.html" style="{BTN_ST(True)} text-decoration: none; display: inline-block;">{H("det_plan")}</a></sc-if>'
          f'<sc-if value="{H("det_inat")}" hint-placeholder-val="{F_}"><button type="button" onClick="{H("det_reativar")}" style="{BTN_ST(True)}">{H("det_reat")}</button></sc-if>')
    shell37('CD-01','Talhão',corpo,fname=fname,crumbs_extra=[H('det_crumb')],
            subtitle='Confira área, polígono e parcelas do talhão em cada safra.',status=None,primary_html=prim,search=False)
    seletor=(f'<select aria-label="Talhão" value="{H("det_t")}" onChange="{H("det_set")}" style="font-family: inherit; font-size: 15px; font-weight: 800; color: {INK}; padding: 6px 30px 6px 12px; border-radius: 10px; border: 1px solid {LINE}; background: {SURF}; cursor: pointer;">'
             f'<sc-for list="{H("det_opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>')
    _injeta(fname,'Talhão',seletor+_chip_dyn('det')); _rolagem(fname)
