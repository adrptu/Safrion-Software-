p='areas/processo_os.py'; s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1, a[:90]
    s=s.replace(a,b)

# ---------- 1) dados da atividade, insumos e bloqueios por ordem ----------
rep("""_RED=('impedid','bloquead','atrasad','conflito','vencid','fora da política')""",
"""# atividade de cada ordem (operação, atividade, gatilho, origem do padrão, operação do conjunto em dados2.CONJ)
ATV={
 'OS-0415':('Pulverização','Dessecação pós-colheita','5 dias após a colheita','Recomendação da safra 2025/26','Pulverização'),
 'OS-0417':('Adubação a lanço','Adubação de cobertura','DAP +25','Recomendação de cobertura · Feijão P1','Adubação a lanço'),
 'OS-0418':('Fertirrigação','Fertirrigação de nitrogênio','janela 24–25/09','Tarefa de água do Pivô 1 reclassificada · v2','Fertirrigação'),
 'OS-0419':('Irrigação','Irrigação por política','lâmina de 12,0 mm hoje','Política de água PA-07 v3',None),
 'OS-0420':('Plantio','Plantio e adubação de base','DAP 0 · 22/09','Soja alta tecnologia v6 · REC-014 v2','Plantio'),
 'OS-0421':('Pulverização','Fungicida 1ª aplicação','DAP +45','Soja alta tecnologia v6','Pulverização'),
 'OS-0422':('Irrigação','Irrigação do próximo ciclo','lâmina pedida de 13,5 mm','Recomendação de irrigação · fora da PA-07 v3',None),
 'OS-0423':('Irrigação','Irrigação por gotejo','hoje 14:00–16:00','Recomendação de irrigação · fora da PA-07 v3',None),
 'OS-0424':('Pulverização','Fungicida','24/09','Safra 2026/27 · Pivô 2','Pulverização'),
 'OS-0425':('Adubação a lanço','Adubação 1ª parcela','data 15/10/2026','Café arábica produção v2','Adubação a lanço'),
 'OS-0430':('Pulverização','Dessecação pré-plantio','DAP −20 · 25/09','Soja alta tecnologia v6','Pulverização'),
 'OS-0431':('Plantio','Plantio e adubação de base','DAP 0 · 24/09','Soja alta tecnologia v6 · REC-014 v2','Plantio'),
 'OB-0104':('Beneficiamento','Beneficiamento de grãos','15–18/09','Rota de beneficiamento aprovada',None),
}
# insumos por ordem: (grupo, produto, dose por ha, unidade, quantidade fixa da ordem ou None = dose × área, situação)
INS={
 'OS-0415':[('Herbicidas','Glifosato 480',2.0,'L',None,'Consumo conferido')],
 'OS-0417':[('Fertilizantes','MAP 11-52',36.84,'kg',3500,'Entregues 100 sc · usadas 70 · devolvidas 20 · 10 sc com Paula')],
 'OS-0418':[('Fertilizantes','Ureia 45%',12.0,'kg',None,'Requisição REQ-038 ao liberar')],
 'OS-0420':[('Sementes','Semente de soja 58 W',52.0,'kg',None,'Entregue · saldo pausado'),('Fertilizantes','MAP 11-52',250.0,'kg',None,'Entregue · saldo pausado')],
 'OS-0421':[('Fungicidas','Fungicida A',0.5,'L',None,'Entregue ao operador'),('Adjuvantes','Adjuvante espalhante',0.25,'L',None,'Entregue ao operador')],
 'OS-0424':[('Fungicidas','Fungicida A',0.8,'L',None,'Reservado 65 L · lote F26-02 · REQ-039')],
 'OS-0425':[('Fertilizantes','NPK 20-05-20',300.0,'kg',None,'REQ-040 · lote N26-03 tem 8.000 kg · faltam 3.400 kg')],
 'OS-0430':[('Herbicidas','Glifosato 480',2.0,'L',None,'Reserva ao liberar'),('Herbicidas','2,4-D 806',1.0,'L',None,'Reserva ao liberar'),('Adjuvantes','Óleo mineral',0.5,'L',None,'Reserva ao liberar')],
 'OS-0431':[('Sementes','Semente de soja 58 W',52.0,'kg',None,'Reserva ao liberar'),('Fertilizantes','MAP 11-52',250.0,'kg',None,'Reserva ao liberar')],
}
SEM_INS={'OS-0419':'Água · lâmina de 12,0 mm · sem almoxarifado (política PA-07 v3).','OS-0422':'Água · lâmina pedida de 13,5 mm; o limite da PA-07 v3 é 12,0 mm.',
         'OS-0423':'Água · gotejo de 2 h; a política exige sonda ativa.','OB-0104':'Ordem de processo: entradas e saídas por etapa do beneficiamento, sem dose por hectare.'}
# impedimento que segura o próximo passo da fase atual: o quê, quem resolve e onde
BLOQ={
 'OS-0431':dict(t='Liberar bloqueado: Trator T1 em manutenção (OM-0233).',q='PCP confirma a máquina substituta.'),
 'OS-0420':dict(t='Apontamento pausado: v3 em revisão por Ana (agrônoma) e Trator T1 bloqueado (OM-0233).',q='Ana aprova a v3; o Trator 02 assume a partir de 24/09.',h='CA-01x-os0420.dc.html',hl='Abrir a ordem completa'),
 'OS-0417':dict(t='Encerrar bloqueado: 10 sc de MAP 11-52 sob custódia de Paula.',q='Rui recebe a devolução no Estoque.',h='EST.dc.html',hl='Receber devolução no Estoque'),
 'OS-0422':dict(t='Liberar bloqueado: a lâmina de 13,5 mm passa do limite de 12,0 mm da PA-07 v3.',q='Ana (agrônoma) decide a exceção na Irrigação.',h='IR-02.dc.html',hl='Revisar na Irrigação'),
 'OS-0423':dict(t='Liberar bloqueado: a sonda do setor está sem dado há 3 dias.',q='Manutenção da sonda ou revisão de Ana (agrônoma).',h='IR-02.dc.html',hl='Revisar na Irrigação'),
}
AVISO={'OS-0425':'O lote N26-03 cobre 26,7 dos 38 ha; Suprimentos completa a entrega até 15/10.'}
CJ={c['op']:c for c in D2.CONJ}
_RED=('impedid','bloquead','atrasad','conflito','vencid','fora da política')""")
rep("""                        link=(o['detalhe'] or '')))
    return out""",
"""                        link=(o['detalhe'] or ''),atv=_atv(o),ins=[dict(g=g,p=pr,dose=d,un=u,tot=(t if t is not None else (round(d*(o.get('area') or 0),2))),sit=si) for g,pr,d,u,t,si in INS.get(o['id'],[])],
                        semins=SEM_INS.get(o['id'],''),bloq=(dict(BLOQ[o['id']],fase=o['etapa']) if o['id'] in BLOQ else None),aviso=AVISO.get(o['id'],'')))
    return out
def _atv(o):
    op,nome,gat,orig,cop=ATV[o['id']]; c=CJ.get(cop) if cop else None
    return dict(op=op,nome=nome,gat=gat,orig=orig,conj=(c['conj'] if c else ''),rend=(c['rend'] if c else 0))""")

# ---------- 2) lógica do painel: dados, próximo passo e transições ----------
rep("""    v.pan_link=o.link||'#'; v.pan_hasLink=!!o.link;
  }""",
"""    v.pan_link=o.link||'#'; v.pan_hasLink=!!o.link;
    osWork(self,v,o);
  }""")
rep("""function EXTRAVALS(self,v){""",
"""function nd(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:(d===undefined?2:d)}); }
function osUpd(self,id,patch){ const all=ords(self).map(x=>x.id===id?Object.assign({},x,patch):x); return all; }
// tela de trabalho da ordem: atividade, insumos e doses, e o botão do próximo passo da fase
function osWork(self,v,o){ const st=self.state; const a=o.atv||{};
  const kv=[['Operação',a.op||'—'],['Atividade',a.nome||o.tipo],['Gatilho',a.gat||'—'],['Local · área',o.talhao+(o.area?' · '+nf(o.area)+' ha':'')],['Janela',o.janela],['Responsável',o.resp]];
  if(a.conj){ kv.push(['Conjunto',a.conj+' · '+nd(a.rend)+' ha/h']); if(o.area) kv.push(['Horas previstas',nd(o.area/a.rend,1)+' h ('+nd((o.saldo||0)/a.rend,1)+' h no saldo)']); }
  kv.push(['Padrão · versão',(a.orig||'—')+' · '+o.versao]);
  v.pan_atv=kv.map(x=>({l:x[0],v:x[1]}));
  v.pan_ins=(o.ins||[]).map(x=>{ const usado=(o.id==='OS-0417')?x.tot:(o.area?x.dose*(o.realizado||0):0);
    return {p:x.p,g:x.g,dose:nd(x.dose)+' '+x.un+'/ha',tot:nd(x.tot)+' '+x.un,usado:(usado?nd(usado)+' '+x.un:'—'),sit:(o.reservado&&o.etapa!=='A liberar'&&/Reserva ao liberar|REQ-038/.test(x.sit)?'Reservado no Estoque':x.sit)}; });
  v.pan_hasIns=v.pan_ins.length>0; v.pan_semIns=!v.pan_hasIns; v.pan_semInsT=o.semins||'Sem insumos: a atividade é só operação.';
  // próximo passo por fase
  const b=o.bloq&&o.bloq.fase===o.etapa?o.bloq:null; let P;
  if(o.etapa==='A liberar') P={t:'Aprove a versão e libere para execução. Ao liberar, os insumos são reservados no Estoque.',btn:'Aprovar e liberar',fn:'liberar'};
  else if(o.etapa==='Liberadas') P={t:'Confira máquina, equipe e insumos e inicie a execução na janela '+o.janela+'.',btn:'Iniciar execução',fn:'iniciar'};
  else if(o.etapa==='Em execução') P=(o.area&&(o.saldo||0)<=0.001)?{t:'A área toda foi feita. Envie a ordem para conferência.',btn:'Enviar para conferência',fn:'conferencia'}
      :{t:'Registre o apontamento do turno: data e área feita. Os insumos usados são calculados pela dose. Fechar o turno não encerra a ordem.',btn:'Registrar apontamento',fn:'apontar'};
  else if(o.etapa==='Em conferência') P={t:'Confira apontamentos, consumo e sobras e encerre a ordem.',btn:'Conferir e encerrar',fn:'encerrar'};
  else P={t:'Ordem encerrada: somente consulta.',btn:'',fn:''};
  v.pan_pt=P.t; v.pan_pbtn=P.btn; v.pan_hasBtn=!!P.btn&&!b; v.pan_bloq=!!b; v.pan_bt=b?b.t:''; v.pan_bq=b?('Quem resolve: '+b.q):'';
  v.pan_hasBl=!!(b&&b.h); v.pan_bh=(b&&b.h)||'#'; v.pan_bhl=(b&&b.hl)||'';
  v.pan_aviso=(o.aviso&&o.etapa==='Liberadas')?o.aviso:''; v.pan_hasAviso=!!v.pan_aviso;
  v.pan_pst='display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:12px;'+(b?'background:#FDE8E6;border:1px solid #F4C7C1;':(P.btn?'background:#E4F3E9;border:1px solid #BFE0CB;':'background:#F4F6F3;border:1px solid #E4E9E5;'));
  const pa=(st.pa&&st.pa.id===o.id)?st.pa:null;
  v.pan_go=()=>{ if(P.fn==='apontar'){ const prox=(o.ap||[]).find(x=>x.st==='Previsto'); self.setState({pa:{id:o.id,fn:'apontar',d:'2026-09-26',ha:String(Math.min(o.saldo||0,prox?prox.ha:(o.saldo||0))).replace('.',','),err:''}}); return; } self.setState({pa:{id:o.id,fn:P.fn}}); };
  v.pan_conf=!!pa&&pa.fn!=='apontar'; v.pan_apf=!!pa&&pa.fn==='apontar'; v.pan_idle=!pa;
  const insTxt=(o.ins||[]).map(x=>x.p+' '+nd(x.tot)+' '+x.un).join(', ');
  v.pan_ct={liberar:'Liberar '+o.id+': aprova a versão '+o.versao+(insTxt?' e reserva no Estoque: '+insTxt+'.':'.'),iniciar:'Iniciar '+o.id+' agora: máquina, equipe e insumos confirmados na janela '+o.janela+'.',
    conferencia:'Enviar '+o.id+' para conferência: execução física concluída ('+nf(o.realizado)+' ha).',encerrar:'Encerrar '+o.id+': apontamentos conferidos, consumo e sobras destinados.'}[pa?pa.fn:'']||'';
  v.pan_cbtn={liberar:'Confirmar liberação',iniciar:'Confirmar início',conferencia:'Confirmar envio',encerrar:'Confirmar encerramento'}[pa?pa.fn:'']||'';
  v.pan_back=()=>self.setState({pa:null});
  v.pan_yes=()=>{ const f=pa.fn; let patch, msg;
    if(f==='liberar'){ patch={etapa:'Liberadas',reservado:true,selos:o.selos.filter(x=>!/Aguardando/.test(x.t)),versao:String(o.versao).replace('emitida','aprovada').replace('submetida','aprovada'),cond:'Liberada · insumos reservados no Estoque. Próximo passo: iniciar na janela '+o.janela+'.'}; msg=o.id+' liberada'+(insTxt?'. Reservado no Estoque: '+insTxt:'')+'.'; }
    else if(f==='iniciar'){ patch={etapa:'Em execução',cond:'Em execução · registre o apontamento de cada turno.'}; msg=o.id+' em execução. Registre o apontamento de cada turno.'; }
    else if(f==='conferencia'){ patch={etapa:'Em conferência',selos:[],cond:'Aguardando conferência de apontamentos, consumo e sobras.'}; msg=o.id+' enviada para conferência.'; }
    else if(f==='encerrar'){ patch={etapa:'Encerradas',selos:[],cond:'Nenhuma · ordem encerrada, somente consulta.'}; msg=o.id+' encerrada.'; }
    self.setState({ords:osUpd(self,o.id,patch),pa:null,g2toast:msg}); };
  v.pan_ad=pa&&pa.d||''; v.pan_aha=pa&&pa.ha||''; v.pan_aerr=pa&&pa.err||''; v.pan_hasAerr=!!(pa&&pa.err);
  v.pan_asub='Saldo da ordem: '+nf(o.saldo)+' ha';
  v.pan_setad=(e)=>self.setState({pa:Object.assign({},self.state.pa,{d:e.target.value,err:''})}); v.pan_setaha=(e)=>self.setState({pa:Object.assign({},self.state.pa,{ha:e.target.value,err:''})});
  v.pan_asave=()=>{ const cur=self.state.pa; const n=g2num(cur.ha);
    if(!cur.d){ self.setState({pa:Object.assign({},cur,{err:'Informe a data do turno.'})}); return; }
    if(isNaN(n)||n<=0){ self.setState({pa:Object.assign({},cur,{err:'Informe a área feita (maior que 0 ha).'})}); return; }
    if(n>(o.saldo||0)+0.001){ self.setState({pa:Object.assign({},cur,{err:'Máximo '+nf(o.saldo)+' ha: é o saldo da ordem.'})}); return; }
    const ap=(o.ap||[]).filter(x=>x.st!=='Previsto'); const d=cur.d.split('-'); const nx={d:d[2]+'/'+d[1],dia:ap.length+1,ha:n,st:'Provisório'};
    const prev=(o.ap||[]).filter(x=>x.st==='Previsto').slice(1).map((x,i)=>Object.assign({},x,{dia:ap.length+2+i}));
    const real=(o.realizado||0)+n, sal=Math.max(0,(o.saldo||0)-n);
    const ins=(o.ins||[]).map(x=>x.p+' '+nd(x.dose*n)+' '+x.un).join(', ');
    self.setState({ords:osUpd(self,o.id,{ap:ap.concat([nx]).concat(sal>0?prev:[]),realizado:real,saldo:sal}),pa:null,
      g2toast:'Apontamento do dia '+nx.dia+': '+nd(n)+' ha (provisório)'+(ins?' · usado: '+ins:'')+'. Saldo '+nf(sal)+' ha; a ordem continua em execução.'}); };
}
function EXTRAVALS(self,v){""")

# ---------- 3) painel: tela de trabalho ----------
i0=s.index("def _painel():"); i1=s.index("def _form():")
s=s[:i0]+'''def _painel():
    lab=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    aprow=(f'<div style="display: grid; grid-template-columns: 64px 56px 1fr 1.3fr auto; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; font-variant-numeric: tabular-nums; {H("a.rst")}">'
           f'<span>{H("a.d")}</span><span>{H("a.dia")}</span><span style="text-align: right;">{H("a.ha")}</span><span style="text-align: right; font-weight: 700;">{H("a.ac")}</span>{_chip_hole("a.t","a.st","a.dot")}</div>')
    aphead=(f'<div style="display: grid; grid-template-columns: 64px 56px 1fr 1.3fr auto; gap: 8px; padding: 4px 0; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;">'
            f'<span>Data</span><span>Turno</span><span style="text-align: right;">Realizado</span><span style="text-align: right;">Acumulado</span><span>Situação</span></div>')
    IC='minmax(0,1.6fr) 96px 110px 110px minmax(0,1.5fr)'
    inshead=(f'<div style="display: grid; grid-template-columns: {IC}; gap: 10px; padding: 4px 0; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;">'
             f'<span>Produto</span><span style="text-align: right;">Dose</span><span style="text-align: right;">Na ordem</span><span style="text-align: right;">Usado</span><span>Situação</span></div>')
    insrow=(f'<div style="display: grid; grid-template-columns: {IC}; gap: 10px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; font-variant-numeric: tabular-nums;">'
            f'<span style="min-width: 0;"><b>{H("i.p")}</b><br><span style="font-size: 11.5px; color: {MUTED};">{H("i.g")}</span></span>'
            f'<span style="text-align: right; white-space: nowrap;">{H("i.dose")}</span><span style="text-align: right; white-space: nowrap; font-weight: 700;">{H("i.tot")}</span>'
            f'<span style="text-align: right; white-space: nowrap;">{H("i.usado")}</span><span style="font-size: 12px; color: {MUTED};">{H("i.sit")}</span></div>')
    kvbox=lambda lst: (f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;"><sc-for list="{H(lst)}" as="x" hint-placeholder-count="6"><div style="min-width: 0;">'
             f'<div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div><div style="font-size: 13.5px; font-weight: 600; margin-top: 2px;">{H("x.v")}</div></div></sc-for></div>')
    passo=(f'<div role="region" aria-label="Próximo passo" style="{H("pan_pst")}">{lab("Próximo passo")}'
      f'<div style="font-size: 13.5px; line-height: 1.45;">{H("pan_pt")}</div>'
      f'<sc-if value="{H("pan_bloq")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 13px; font-weight: 700; color: {RED}; line-height: 1.45;">{H("pan_bt")}<br><span style="font-weight: 600;">{H("pan_bq")}</span></div>'
      f'<sc-if value="{H("pan_hasBl")}" hint-placeholder-val="{F()}"><div><a href="{H("pan_bh")}" style="{_MINI} text-decoration: none; display: inline-flex;">{H("pan_bhl")} ›</a></div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_hasAviso")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 700; color: {YEL}; background: {YELS}; padding: 7px 10px; border-radius: 8px;">{H("pan_aviso")}</div></sc-if>'
      f'<sc-if value="{H("pan_idle")}" hint-placeholder-val="{T()}"><sc-if value="{H("pan_hasBtn")}" hint-placeholder-val="{T()}"><div><button type="button" onClick="{H("pan_go")}" style="{BTN_ST(True,True)}">{H("pan_pbtn")}</button></div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_conf")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE}; font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_ct")}'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_yes")}" style="{_MINIP}">{H("pan_cbtn")}</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_apf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Data do turno<input type="date" aria-label="Data do turno" value="{H("pan_ad")}" onChange="{H("pan_setad")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE};"></label>'
      f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Área feita (ha)<input aria-label="Área feita em hectares" inputMode="decimal" value="{H("pan_aha")}" onChange="{H("pan_setaha")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 110px; text-align: right;"></label>'
      f'<span style="font-size: 12px; color: {MUTED}; padding-bottom: 9px;">{H("pan_asub")}</span></div>'
      f'<sc-if value="{H("pan_hasAerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_aerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Cancelar</button><button type="button" onClick="{H("pan_asave")}" style="{_MINIP}">Salvar apontamento</button></div></div></sc-if></div>')
    return (f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar painel" onClick="{H("pan_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("pan_t")}" onKeyDown="{H("pan_key")}" style="position: relative; width: 820px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1; line-height: 1.3;">{H("pan_t")}</h2>'
      f'<sc-if value="{H("pan_hasLink")}" hint-placeholder-val="{F()}"><a href="{H("pan_link")}" style="{_MINI} text-decoration: none; display: inline-flex; align-items: center; white-space: nowrap;">Abrir ordem completa ›</a></sc-if>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">{_chip_hole("pan_fase","pan_fst","pan_fdot")}<sc-for list="{H("pan_selos")}" as="s" hint-placeholder-count="1">{_chip_hole("s.t","s.st","s.dot")}</sc-for></div>'
      f'<div role="list" aria-label="Fase da ordem" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;"><sc-for list="{H("pan_steps")}" as="p" hint-placeholder-count="5"><div role="listitem" aria-current="{H("p.cur")}" style="{H("p.st")}"><span style="{H("p.bst")}"></span>{H("p.t")}</div></sc-for></div>'
      + passo +
      f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Atividade")}{kvbox("pan_atv")}</div>'
      f'<div style="display: flex; flex-direction: column; gap: 2px;">{lab("Insumos e doses")}'
      f'<sc-if value="{H("pan_hasIns")}" hint-placeholder-val="{T()}">{inshead}<sc-for list="{H("pan_ins")}" as="i" hint-placeholder-count="2">{insrow}</sc-for></sc-if>'
      f'<sc-if value="{H("pan_semIns")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_semInsT")}</div></sc-if></div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Apontamentos diários")}'
      f'<sc-if value="{H("pan_hasAp")}" hint-placeholder-val="{T()}">{aphead}<sc-for list="{H("pan_ap")}" as="a" hint-placeholder-count="4">{aprow}</sc-for>'
      f'<sc-if value="{H("pan_hasAcum")}" hint-placeholder-val="{T()}"><div style="padding: 8px 0 0; border-top: 2px solid {INK}; font-size: 13px; font-weight: 800;">{H("pan_acum")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasNota")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED};">{H("pan_nota")}</div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_noAp")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_noApT")}</div></sc-if></div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Situação atual")}<div style="font-size: 13px; line-height: 1.45;">{H("pan_cond")}</div></div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Origem")}<sc-for list="{H("pan_orig")}" as="og" hint-placeholder-count="2"><div style="font-size: 13px; padding: 5px 0; border-bottom: 1px solid {LINE};">{H("og.t")}</div></sc-for></div>'
      f'</aside></div></sc-if>')

'''+s[i1:]
rep("""corpo=bloco('Ordens por fase','Clique numa ordem para consultar fase, saldo, apontamentos e origem.',panes,acao=bar)""",
"""corpo=bloco('Ordens por fase','Clique numa ordem para ver atividade, insumos e doses e seguir para a próxima fase.',panes,acao=bar)""")
open(p,'w').write(s); print('patch os ok')
