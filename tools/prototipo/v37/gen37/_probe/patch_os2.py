p='areas/processo_os.py'; s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1, a[:90]
    s=s.replace(a,b)
# bloqueio vale para a ação que ele segura; dono e prazo da pendência
rep(""" 'OS-0431':dict(t='Liberar bloqueado: Trator T1 em manutenção (OM-0233).',q='PCP confirma a máquina substituta.'),
 'OS-0420':dict(t='Apontamento pausado:""",""" 'OS-0431':dict(acao='liberar',t='Liberar bloqueado: Trator T1 em manutenção (OM-0233).',q='PCP confirma a máquina substituta antes de 24/09 06:00.'),
 'OS-0420':dict(acao='apontar',t='Apontamento pausado:""")
rep(""" 'OS-0417':dict(t='Encerrar bloqueado:""",""" 'OS-0417':dict(acao='encerrar',t='Encerrar bloqueado:""")
rep(""" 'OS-0422':dict(t='Liberar bloqueado: a lâmina""",""" 'OS-0422':dict(acao='revisar',t='Revisão individual na Irrigação: a lâmina""")
rep(""" 'OS-0423':dict(t='Liberar bloqueado: a sonda""",""" 'OS-0423':dict(acao='revisar',t='Revisão individual na Irrigação: a sonda""")
rep("""AVISO={'OS-0425':""","""DONO={'OS-0418':('Ana (agrônoma)','vence hoje'),'OS-0420':('Ana (agrônoma) · Manutenção','v3 hoje · OM-0233 até 24/09'),'OS-0421':('Paula','conferir o dia 4 hoje'),
      'OS-0417':('Rui (almoxarifado)','24/09'),'OS-0422':('Ana (agrônoma)','antes do próximo ciclo'),'OS-0423':('Manutenção (sonda do Gotejo T7)','hoje antes das 14:00; depois, revisão de Ana'),
      'OS-0425':('Suprimentos','entrega até 15/10'),'OS-0430':('Ana (agrônoma)','antes de 25/09'),'OS-0431':('PCP','substituto antes de 24/09 06:00')}
LINK={'OS-0417':'CA-02.dc.html'}
AVISO={'OS-0425':""")
rep("""                        link=(o['detalhe'] or ''),atv=_atv(o),""","""                        link=(LINK.get(o['id']) or o['detalhe'] or ''),dono=DONO.get(o['id'],('',''))[0],prazo=DONO.get(o['id'],('',''))[1],atv=_atv(o),""")
# lista e Kanban: dono · prazo sob a condição
rep("""       cond:(o.selos.length?o.selos.map(s=>({k:'chip',t:s.t,c:s.c})):[{k:'mut',t:'—'}]),""",
"""       cond:(o.selos.length?o.selos.map(s=>({k:'chip',t:s.t,c:s.c})):[{k:'mut',t:'—'}]).concat(o.dono?[{k:'br'},{k:'mut',t:o.dono+' · '+o.prazo}]:[]),""")
rep("""meta:o.resp+' · '+o.janela,lab:'Abrir '+o.id+' · '+o.tipo,""","""meta:o.resp+' · '+o.janela,dp:(o.dono?o.dono+' · '+o.prazo:''),hasDp:!!o.dono,lab:'Abrir '+o.id+' · '+o.tipo,""")
rep("""          f'<div style="font-size: 11.5px; color: {MUTED};">{H("k.meta")}</div></div>')""",
"""          f'<sc-if value="{H("k.hasDp")}" hint-placeholder-val="{F()}"><div style="font-size: 11.5px; font-weight: 700; color: {INK};">{H("k.dp")}</div></sc-if>'
          f'<div style="font-size: 11.5px; color: {MUTED};">{H("k.meta")}</div></div>')""")
# próximo passo: revisar versão (aprovar / devolver / rejeitar) separado de liberar
rep("""  if(o.etapa==='A liberar') P={t:'Aprove a versão e libere para execução. Ao liberar, os insumos são reservados no Estoque.',btn:'Aprovar e liberar',fn:'liberar'};""",
"""  if(o.etapa==='A liberar') P=o.rej?{t:'Versão rejeitada: '+o.rej+'. O PCP ajusta a ordem ou a cancela.',btn:'',fn:''}
      :(!o.aprov?{t:'Revise a versão '+o.versao+': atividade, área, produtos e doses abaixo. Aprovar não libera para execução.',btn:'Revisar versão',fn:'revisar'}
      :{t:'Versão aprovada. Libere para execução: os insumos são reservados no Estoque.',btn:'Liberar para execução',fn:'liberar'});""")
rep("""  const b=o.bloq&&o.bloq.fase===o.etapa?o.bloq:null; let P;""","""  let P;""")
rep("""  else P={t:'Ordem encerrada: somente consulta.',btn:'',fn:''};""","""  else P={t:'Ordem encerrada: somente consulta.',btn:'',fn:''};
  const b=(o.bloq&&o.bloq.fase===o.etapa&&o.bloq.acao===P.fn)?o.bloq:null;
  v.pan_dono=(!b&&o.dono)?('Pendência com '+o.dono+' · '+o.prazo):''; v.pan_hasDono=!!v.pan_dono;""")
rep("""  v.pan_conf=!!pa&&pa.fn!=='apontar'; v.pan_apf=!!pa&&pa.fn==='apontar'; v.pan_idle=!pa;""",
"""  v.pan_conf=!!pa&&pa.fn!=='apontar'&&pa.fn!=='revisar'; v.pan_apf=!!pa&&pa.fn==='apontar'; v.pan_rev=!!pa&&pa.fn==='revisar'; v.pan_idle=!pa;
  v.pan_rmot=(pa&&pa.motivo)||''; v.pan_rerr=(pa&&pa.err)||''; v.pan_hasRerr=!!(pa&&pa.err);
  v.pan_setrmot=(e)=>self.setState({pa:Object.assign({},self.state.pa,{motivo:e.target.value,err:''})});
  const decide=(k)=>()=>{ const cur=self.state.pa; const mot=String(cur.motivo||'').trim(); let patch,msg; const sel=o.selos.filter(x=>!/Aguardando|Devolvida|Aprovada/.test(x.t));
    if(k!=='aprovar'&&!mot){ self.setState({pa:Object.assign({},cur,{err:'Informe o motivo.'})}); return; }
    if(k==='aprovar'){ patch={aprov:true,versao:String(o.versao).replace('em revisão','aprovada').replace('emitida','aprovada'),selos:sel.concat([{t:'Aprovada pelo agrônomo',c:'green'}]),cond:'Versão aprovada por Ana (agrônoma). Próximo passo: liberar para execução.',dono:'',prazo:''}; msg='Versão aprovada · '+o.id+' ainda não foi liberada para execução.'; }
    else if(k==='devolver'){ patch={selos:sel.concat([{t:'Devolvida para ajuste',c:'yellow'}]),cond:'Devolvida para ajuste: '+mot+' · o PCP ajusta e reenvia.',dono:'PCP',prazo:'ajustar e reenviar'}; msg=o.id+' devolvida para ajuste. Continua em A liberar.'; }
    else { patch={rej:mot,selos:sel.concat([{t:'Rejeitada',c:'red'}]),cond:'Rejeitada: '+mot+'. A liberação fica bloqueada; a ordem não foi cancelada.',dono:'PCP',prazo:'ajustar ou cancelar'}; msg=o.id+' rejeitada. A ordem não foi cancelada.'; }
    self.setState({ords:osUpd(self,o.id,patch),pa:null,g2toast:msg}); };
  v.pan_raprov=decide('aprovar'); v.pan_rdev=decide('devolver'); v.pan_rrej=decide('rejeitar');""")
rep("""    if(f==='liberar'){ patch={etapa:'Liberadas',reservado:true,selos:o.selos.filter(x=>!/Aguardando/.test(x.t)),versao:String(o.versao).replace('emitida','aprovada').replace('submetida','aprovada'),cond:""",
"""    if(f==='liberar'){ patch={etapa:'Liberadas',reservado:true,dono:'',prazo:'',selos:o.selos.filter(x=>!/Aguardando|Aprovada/.test(x.t)),cond:""")
rep("""    else if(f==='iniciar'){ patch={etapa:'Em execução',""","""    else if(f==='iniciar'){ patch={etapa:'Em execução',dono:'',prazo:'',""")
rep("""    else if(f==='conferencia'){ patch={etapa:'Em conferência',selos:[],""","""    else if(f==='conferencia'){ patch={etapa:'Em conferência',selos:[],dono:o.resp,prazo:'conferir',""")
rep("""    else if(f==='encerrar'){ patch={etapa:'Encerradas',selos:[],""","""    else if(f==='encerrar'){ patch={etapa:'Encerradas',selos:[],dono:'',prazo:'',""")
# painel: bloco de revisão e dono da pendência
rep("""      f'<sc-if value="{H("pan_hasAviso")}" hint-placeholder-val="{F()}">""",
"""      f'<sc-if value="{H("pan_hasDono")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; font-weight: 700;">{H("pan_dono")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasAviso")}" hint-placeholder-val="{F()}">""")
rep("""      f'<sc-if value="{H("pan_apf")}" hint-placeholder-val="{F()}">""",
"""      f'<sc-if value="{H("pan_rev")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="font-size: 13px; font-weight: 600;">Decida sobre a versão. Devolver ou rejeitar exige motivo; nenhuma decisão libera a ordem.</div>'
      f'<textarea aria-label="Motivo da devolução ou rejeição" placeholder="Motivo (para devolver ou rejeitar)" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_raprov")}" style="{_MINIP}">Aprovar versão</button><button type="button" onClick="{H("pan_rdev")}" style="{_MINI}">Devolver para ajuste</button>'
      f'<button type="button" onClick="{H("pan_rrej")}" style="{_MINI} color: {RED}; border-color: {RED};">Rejeitar</button><span style="flex-grow: 1;"></span><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_apf")}" hint-placeholder-val="{F()}">""")
open(p,'w').write(s); print('patch os2 ok')
