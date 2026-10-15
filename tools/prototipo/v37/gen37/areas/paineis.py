# -*- coding: utf-8 -*-
"""PAINEL-01: leitura do cenário, sem comando e sem persistência paralela.
Base f6b31f7; autoria Codex, revisão/integração Claude. Menu via patch separado.
Contagens (não soma de ha, kg, L ou moedas); ausente/incompleto nunca vira zero.
"""
import re
import json
import engine as E
import cenario
import dados_manutencao as DM
from ui37 import shell37, HEIGHTS37
from areas.modulos import JS_VOLTA
H = lambda s: '{{' + s + '}}'

# ID, módulo, título do gráfico, indicadores (nome, fórmula/fonte, desvio), atalhos.
PAINEIS = {
 'PAGR': ('Agrícola', 'O.S. por estado', [
  ('A liberar', 'Contagem das O.S. agrícolas com etapa A liberar. Fonte: cenário compartilhado de O.S.; exclui ordens de beneficiamento.', False),
  ('Liberadas', 'Contagem das O.S. agrícolas com etapa Liberadas. Fonte: cenário compartilhado de O.S.', False),
  ('Em execução', 'Contagem das O.S. agrícolas com etapa Em execução. Fonte: cenário compartilhado de O.S.', False),
  ('Em conferência', 'Contagem das O.S. agrícolas com etapa Em conferência. Fonte: cenário compartilhado de O.S.', False)],
  [('Consultar O.S.', 'OS.dc.html'), ('Planejar safra', 'SAF.dc.html'), ('Consultar colheita', 'COLH.dc.html')]),
 'PMAN': ('Manutenção', 'Ordens por estado', [
  ('Pendências sem ordem', 'A lista Sem ordem da Manutenção: vencimentos de plano vencidos ou com janela até o horizonte, mais achados de inspeção, relatos e alertas ainda sem ordem. Fonte: manSemOrdem, a mesma da visão Sem ordem.', True),   # 14/10 (Claude, integrador): antes contava só os devidos (manSemOm, 3) e a visão mostrava 6
  ('Ordens abertas', 'Contagem de ordens não encerradas nem canceladas. Fonte: manAberta, cenário da Manutenção.', False),
  ('Em execução', 'Contagem de ordens com etapa Em execução. Fonte: cenário da Manutenção.', False),
  ('Ativos bloqueados', 'Contagem de ativos com condição Bloqueado. Fonte: cenário da Manutenção.', True)],
  [('Tratar pendências', 'MA.dc.html#vis=semordem'), ('Consultar ordens', 'MA.dc.html#vis=ordens'), ('Consultar ativos', 'MA.dc.html#vis=ativos'), ('Consultar planos', 'MA.dc.html#vis=planos')]),
 'PSUP': ('Suprimentos', 'Lotes com saldo físico', [
  ('Lotes com saldo físico', 'Contagem de lotes com saldo físico maior que zero. Inclui reservado e quarentena; não significa disponível para uso. Fonte: cenário do Estoque.', False),
  ('Lotes com reserva', 'Contagem de lotes com quantidade reservada maior que zero. Um lote pode também ter quarentena. Fonte: cenário do Estoque.', False),
  ('Lotes em quarentena', 'Contagem de lotes com quantidade em quarentena maior que zero. Fonte: cenário do Estoque; a liberação exige decisão própria.', True),
  ('Requisições a entregar', 'Contagem de requisições de ordens Liberadas ou Em execução com pelo menos um item cujo saldo a entregar é positivo segundo a regra da requisição vigente. Fonte: cenSaldoEntregar. Não soma unidades.', False)],
  [('Conferir estoque', 'EST.dc.html'), ('Acompanhar compras', 'CMP.dc.html')]),
}

JS = r'''
// Indicadores leem somente a fonte canônica. Coleção vazia = zero; ausente/inválida = sem dados.
// PAINEL-02 · leitura agrícola única para o Painel (contrato 6163002343/6163029779): sem comando nem mutação; null = Sem dados.
// O.S. impedidas pela projeção do estado (osProjecaoEstado: as ordens de c.ordens, cada uma com a base do registro e o mesmo osMerge/osManCond
// da tela de O.S.; vazio = [], ordem fora do estado não volta, estado inconsistente = null) e pelo selo do cabeçalho da O.S. (OS_IMP_RE):
// só abertas e só agrícolas (sem OB-); motivo = o selo vigente; dono = o da projeção; desde: o estado não tem (null).
// Recorte por fazenda e safra do registro; ordem aberta sem fazenda ou safra com recorte pedido = Sem dados (não some nem entra por engano).
// Atrasadas: A liberar, Liberadas ou Em execução com o fim da janela (fim, ISO, do registro) antes de OSD.hoje (D2.HOJE_ISO, a data das telas e
// do Mapa; não a DIA_OP, que é só a data padrão do apontamento). Em conferência já foi executada. Ordem aberta sem fim (emitida na tela) não é
// julgada: conta em n.sem_prazo. Sem hoje válido = null. Custos: etapa seguinte (null).
// causa estruturada da impedida (Codex 6166235821: agrupar sem ler o texto do selo): vem dos campos da projeção da O.S. —
// libErr (o Estoque segura a liberação: saldo, lote ou insumo) e bloq (máquina, implemento ou equipamento do registro ou da Manutenção)
function agrCausa(o){ if(o.libErr) return 'Insumo no Estoque'; if(o.bloq) return 'Máquina ou equipamento'; return 'Outro impedimento'; }
/* PAINEL-02 · execução (contrato desta função; apresentação no painel_agricola.py): O.S. agrícolas Em execução e Em conferência do recorte,
   da mesma projeção da tela O.S.; área em ha (prevista = a da O.S., já com o ajuste da liberação; realizada = apontada e enviada; sinal =
   apontada no aparelho, ainda sem envio, fora do realizado); pendencia = o texto do domínio que segura o apontamento ou o encerramento. */
function agrExecucao(ab,rec,ref){
 const r2=x=>Math.round(x*100)/100, num=x=>typeof x==='number'&&Number.isFinite(x);
 const ordens=ab.filter(o=>(!rec.faz||o.faz===rec.faz)&&(!rec.saf||o.saf===rec.saf)&&['Em execução','Em conferência'].includes(o.etapa)).map(o=>{
  const tem=num(o.area)&&o.area>0, real=tem?(num(o.realizado)?o.realizado:0):null;
  return {id:o.id,talhao:o.talhao||'',faz:o.faz||null,saf:o.saf||null,tipo:o.tipo||'',etapa:o.etapa,prevista_ha:tem?r2(o.area):null,realizada_ha:tem?r2(real):null,
   pct:tem?Math.round(real/o.area*100):null,sinal_ha:r2(osApPend(o)),pendencia:(o.etapa==='Em conferência'?o.encM:(o.esg&&o.esg.t))||null,dono:o.dono||null,prazo:o.prazo||null,
   origem:'OS.dc.html#'+encodeURIComponent(o.id)}; });
 const ar=ordens.filter(x=>x.prevista_ha!==null);
 return {referencia:ref,ordens,total:{prevista_ha:r2(ar.reduce((s,x)=>s+x.prevista_ha,0)),realizada_ha:r2(ar.reduce((s,x)=>s+x.realizada_ha,0)),sinal_ha:r2(ordens.reduce((s,x)=>s+x.sinal_ha,0))},
  n:{em_execucao:ordens.filter(x=>x.etapa==='Em execução').length,em_conferencia:ordens.filter(x=>x.etapa==='Em conferência').length,com_pendencia:ordens.filter(x=>x.pendencia).length,sem_area:ordens.length-ar.length}};
}
/* PAINEL-02 · MIP: a situação de cada vistoria pela mesma regra do AG-01 (mipSit, com as O.S. do cenário c). decidir = acima do NC, foco ou
   O.S. de controle cancelada (decisão do RT); atrasadas = ritmo vencido; coleta = no aparelho ou incompleta (parcial = o resultado com o que já
   foi coletado). A vistoria não tem safra no registro do MIP: com recorte de safra = Sem dados (null), como a O.S. sem safra. */
function agrMip(c,rec){
 if(typeof mipGet!=='function'||typeof mipSit!=='function'||typeof MIPD==='undefined'||rec.saf) return null;
 let s=null; try { s=mipGet(); } catch(e) { return null; }
 const vs=s&&s.vis&&typeof s.vis==='object'&&!Array.isArray(s.vis)?Object.values(s.vis):null;
 if(!vs||!vs.every(v=>v&&typeof v.id==='string'&&MIPD.tal[v.tal]&&MIPD.prot[v.prot]&&typeof v.data==='string')) return null;
 const fazDe=v=>v.faz||MIPD.tal[v.tal].faz||null; if(rec.faz&&vs.some(v=>!fazDe(v))) return null;
 const its=[]; for(const v of vs.filter(v=>!rec.faz||fazDe(v)===rec.faz)) { let S=null; try { S=mipSit(s,v,c); } catch(e) { return null; } its.push([v,S]); }
 const ref=MIPD.hoje, base=v=>({vis:v.id,talhao:MIPD.tal[v.tal].rot||v.tal,faz:fazDe(v),cultura:MIPD.tal[v.tal].cultura||null,alvo:MIPD.prot[v.prot].alvo,origem:'AG-01.dc.html#'+encodeURIComponent(v.id)});
 const de=ks=>its.filter(([v,S])=>ks.includes(S.k)).sort((a,b)=>(a[1].ord-b[1].ord)||(a[0].data<b[0].data?-1:1));
 const decidir=de(['acima','foco','cancelada']).map(([v,S])=>Object.assign(base(v),{sit:S.k,rotulo:S.t,leitura:S.R.ctxt,unidade:S.R.un||null,
  pct_nc:S.R.pct===null?null:mipPct(S.R.pct),data:v.data,dias:mipDif(v.data,ref),detalhe:S.sub||null,dono:MIPD.rt||null}));
 const atrasadas=de(['atrasada']).map(([v,S])=>Object.assign(base(v),{prevista:S.prev,dias:mipDif(S.prev,ref),dono:v.resp||null}));
 const coleta=de(['sinc','incompleta']).map(([v,S])=>Object.assign(base(v),{sit:S.k,rotulo:S.t,pontos:S.R.ptxt,parcial:S.R.kr||null,dono:v.resp||null}));
 return {referencia:ref,decidir,atrasadas,coleta,n:{decidir:decidir.length,atrasadas:atrasadas.length,coleta:coleta.length,em_controle:its.filter(([v,S])=>['controle','pos','avaliacao'].includes(S.k)).length}};
}
function agrPainelRef(c,rec) { rec=rec||{};
 let os=null, execucao=null;
 if(typeof osProjecaoEstado==='function'&&typeof OSD!=='undefined') {
  let pj=null; try { pj=osProjecaoEstado(c,id=>/^OB-/.test(id)); } catch(e) { pj=null; }
  const ok=pj&&pj.every(o=>o&&typeof o.id==='string'&&typeof o.etapa==='string'&&Array.isArray(o.selos));
  const ab=ok?pj.filter(o=>!/^OB-/.test(o.id)&&o.etapa!=='Encerradas'&&o.etapa!=='Canceladas'):null;
  const semCtx=ab&&((rec.faz&&ab.some(o=>typeof o.faz!=='string'||!o.faz))||(rec.saf&&ab.some(o=>typeof o.saf!=='string'||!o.saf)));
  if(ab&&!semCtx) {
   const imp=ab.filter(o=>(!rec.faz||o.faz===rec.faz)&&(!rec.saf||o.saf===rec.saf))
    .map(o=>[o,o.selos.find(s=>s&&OS_IMP_RE.test(s.t||''))]).filter(x=>x[1])
    .map(([o,s])=>({id:o.id,talhao:o.talhao||'',faz:o.faz||null,saf:o.saf||null,etapa:o.etapa,motivo:s.t,causa:agrCausa(o),dono:o.dono||null,desde:null,origem:'OS.dc.html#'+encodeURIComponent(o.id)}));
   /* data de calendário de verdade (Codex 6166305618): formato e ida e volta UTC (2026-99-99 e 2026-02-30 não passam; 2028-02-29 passa) */
   const iso=x=>{ if(typeof x!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(x)) return false; const d=new Date(x+'T00:00:00Z'); return !isNaN(d.getTime())&&d.toISOString().slice(0,10)===x; }, hoje=OSD.hoje;
   let atr=null, semPrazo=null;
   if(iso(hoje)) { const rc=ab.filter(o=>(!rec.faz||o.faz===rec.faz)&&(!rec.saf||o.saf===rec.saf)&&['A liberar','Liberadas','Em execução'].includes(o.etapa));
    semPrazo=rc.filter(o=>!iso(o.fim)).length;
    atr=rc.filter(o=>iso(o.fim)&&o.fim<hoje).map(o=>({id:o.id,talhao:o.talhao||'',faz:o.faz||null,saf:o.saf||null,etapa:o.etapa,prevista:o.fim,
     dias:Math.round((Date.parse(hoje)-Date.parse(o.fim))/864e5),dono:o.dono||null,origem:'OS.dc.html#'+encodeURIComponent(o.id)})); }
   os={impedidas:imp,atrasadas:atr,referencia:iso(hoje)?hoje:null,n:{impedidas:imp.length,atrasadas:atr?atr.length:null,sem_prazo:semPrazo}};
   execucao=agrExecucao(ab,rec,iso(hoje)?hoje:null);   /* referencia: a data contra a qual o atraso é medido (a apresentação diz "Referência dd/mm/aaaa", não "hoje") */
  }
 }
 return {os,custos:null,execucao,mip:agrMip(c,rec)};
}
function pnObjs(x) { return x && typeof x==='object' && !Array.isArray(x) ? Object.values(x) : null; }
function pnNum(x) { return typeof x==='number' && Number.isFinite(x) && x>=0; }
function pnConta(xs, pred) { return xs===null ? null : xs.filter(pred).length; }
function pnValores(c,k) {
 const validOs=x=>x&&typeof x.id==='string'&&typeof x.etapa==='string';
 const all=pnObjs(c&&c.ordens), os=all&&all.every(validOs)?all.filter(o=>o.id.startsWith('OS-')&&o.fam!=='BEN'):null;
 let vals, bars, labels;
 if(k==='PAGR') {
  labels=['A liberar','Liberadas','Em execução','Em conferência'];
  vals=labels.map(s=>pnConta(os,o=>o.etapa===s)); bars=vals;
 } else if(k==='PMAN') {
  const m=c&&c.man, oo=pnObjs(m&&m.oms), aa=pnObjs(m&&m.ativos);
  const oms=oo&&oo.every(x=>x&&typeof x.etapa==='string')?oo:null;
  const ativos=aa&&aa.every(x=>x&&typeof x.cond==='string')?aa:null;
  let sem=null;
  const ach=pnObjs(m&&m.achados);   /* a lista Sem ordem inclui os achados: sem a coleção, a contagem fica Sem dados (ausente não vira parcial) */
  if(m&&oms&&ativos&&pnObjs(m.planos)&&pnObjs(m.vinc)&&ach&&ach.every(q=>q&&typeof q.estado==='string')&&typeof m.hoje==='string'&&pnNum(m.horiz)) {
   try { sem=manSemOrdem(m).n; } catch(e) { sem=null; }
  }
  vals=[sem,pnConta(oms,manAberta),pnConta(oms,o=>o.etapa==='Em execução'),pnConta(ativos,a=>a.cond==='Bloqueado')];
  labels=['A liberar','Liberadas','Em execução','Em conferência']; bars=labels.map(s=>pnConta(oms,o=>o.etapa===s));
 } else {
  const ll=pnObjs(c&&c.lotes), rr=pnObjs(c&&c.reqs);
  const ls=ll&&ll.every(l=>l&&pnNum(l.fisico)&&pnNum(l.reservado)&&pnNum(l.quarentena))?ll:null;
  const rs=all&&all.every(validOs)&&rr&&rr.every(r=>r&&c.ordens[r.os]&&Array.isArray(r.itens)&&r.itens.every(i=>i&&['solicitado','consumido','custodia'].every(n=>pnNum(i[n]))&&(i.dispensado===undefined||pnNum(i.dispensado))))?rr:null;
  vals=[pnConta(ls,l=>l.fisico>0),pnConta(ls,l=>l.reservado>0),pnConta(ls,l=>l.quarentena>0),pnConta(rs,r=>['Liberadas','Em execução'].includes(c.ordens[r.os].etapa)&&r.itens.some(i=>cenSaldoEntregar(i)>1e-6))];
  labels=['Com quarentena','Com reserva, sem quarentena','Sem reserva nem quarentena'];
  bars=[pnConta(ls,l=>l.fisico>0&&l.quarentena>0),pnConta(ls,l=>l.fisico>0&&l.quarentena===0&&l.reservado>0),pnConta(ls,l=>l.fisico>0&&l.quarentena===0&&l.reservado===0)];
 }
 return {vals,bars,labels};
}
function EXTRAVALS(self,v) {
 cenOuvir(self); modVolta(self);
 if(PN_ID==='PAGR'&&typeof pnaVals==='function') pnaVals(self,v);   /* PAINEL-02: seção de colheita (painel_agricola.py) */
 const p=pnValores(cenGet(),PN_ID), max=Math.max(1,...p.bars.filter(x=>x!==null));
 const fmt=x=>x===null?'Sem dados':x.toLocaleString('pt-BR');
 p.vals.forEach((x,i)=>{v['pn_v'+i]=fmt(x);v['pn_alert'+i]=PN_ALERT[i]&&x>0;});
 p.bars.forEach((x,i)=>{v['pn_b'+i]=fmt(x);v['pn_w'+i]=x===null?0:Math.round(x/max*100);});
 v.pn_missing=p.vals.some(x=>x===null)||p.bars.some(x=>x===null);
 v.pn_empty=p.bars.every(x=>x===0);
}
'''

CSS = '''<style>
.pn{display:flex;flex-direction:column;gap:20px;min-width:0}.pn-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.pn-card,.pn-chart{border:1px solid #E4E9E5;border-radius:14px;padding:16px;background:#fff;min-width:0}
.pn-card h2{font-size:14px;font-weight:600;margin:0;display:flex;align-items:center;justify-content:space-between;gap:4px}
.pn-value{font-size:28px;font-weight:700;color:#15201A}.pn-value[data-alert=true]{color:#B42318}
.pn-tip{flex-shrink:0;width:44px;height:44px;border:0;background:transparent;color:#65736A;cursor:pointer;font:inherit}
.pn-chart h2{font-size:16px;margin:0 0 16px}.pn-row{display:grid;grid-template-columns:minmax(130px,1fr) 2fr 80px;align-items:center;gap:12px;margin:12px 0;font-size:14px}
.pn-row svg{width:100%;height:16px;display:block}.pn-row strong{text-align:right;font-size:14px}
.pn-links{display:flex;flex-wrap:wrap;gap:12px}.pn-links a{min-height:44px;display:inline-flex;align-items:center;padding:0 14px;border:1px solid #E4E9E5;border-radius:10px;color:#15201A;text-decoration:none;background:#fff;font-size:14px}
.pn :focus-visible{outline:2px solid #1E7A4C;outline-offset:3px}
.pn-context{color:#65736A;font-size:13px;margin:0}.pn [hidden]{display:none!important}
@media(max-width:900px){.pn-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){.pn-grid{grid-template-columns:1fr}.pn-row{grid-template-columns:1fr 70px;gap:6px}.pn-row svg{grid-row:2;grid-column:1 / -1}.pn-links{flex-direction:column}}
</style>'''


def build():
    for fid, (mod, titulo, itens, atalhos) in PAINEIS.items():
        fname=fid+'.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1050
        E.EXTRAJS[0]=(cenario.js_prefixo()+DM.js_regras()+JS_VOLTA+
                       'const PN_ID='+json.dumps(fid)+';const PN_ALERT='+json.dumps([i[2] for i in itens])+';\n'+JS)
        pna=''
        if fid=='PAGR':   # PAINEL-02 (Codex, PR #62): colheita por cultivo e período, abaixo dos cartões; pnaVals no EXTRAVALS
            from areas.painel_agricola import secao
            pna, pna_js = secao(); E.EXTRAJS[0] += pna_js
            # agrPainelRef lê a projeção do estado (osProjecaoEstado no núcleo da O.S.), com as mesmas ordens do registro que a tela O.S. e o Mapa usam
            from areas.processo_os import JS_NUCLEO as _OSN, _ordens as _ords
            import dados2 as _D2
            E.EXTRAJS[0] += 'const OSD = '+json.dumps(dict(ords=_ords(),hoje=_D2.HOJE_ISO),ensure_ascii=False).replace('</','<\\/')+';\n'+_OSN
            import areas.custo_dominio as _CUS   # agrCustoRef: custo por cultura com as regras da camada Custos do Mapa
            E.EXTRAJS[0] += _CUS.js_prefixo()
            import dados_mip as _MIP   # agrPainelRef().mip: a mesma base do AG-01 (MIPD, MIP0 e mip.js)
            E.EXTRAJS[0] += _MIP.js_prefixo()
        cards=''.join('<section class="pn-card"><h2>'+E.esc(nome)+
          '<button type="button" class="pn-tip g2dica-i" aria-label="Como calcular: '+E.esc(nome)+'" data-dica="'+E.esc(formula)+'">ⓘ</button></h2>'+
          '<strong class="pn-value" data-alert="'+H('pn_alert'+str(i))+'">'+H('pn_v'+str(i))+'</strong></section>' for i,(nome,formula,_) in enumerate(itens))
        labels=(['Com quarentena','Com reserva, sem quarentena','Sem reserva nem quarentena'] if fid=='PSUP' else ['A liberar','Liberadas','Em execução','Em conferência'])
        rows=''.join('<div class="pn-row"><span>'+E.esc(l)+'</span><svg viewBox="0 0 100 8" preserveAspectRatio="none" aria-hidden="true"><rect width="100" height="8" rx="2" fill="#EEF1EE"/><rect width="'+H('pn_w'+str(i))+'" height="8" rx="2" fill="#65736A"/></svg><strong>'+H('pn_b'+str(i))+'</strong></div>' for i,l in enumerate(labels))
        links=''.join('<a class="mod-cartao pn-link" href="'+h+'">'+E.esc(n)+'</a>' for n,h in atalhos[1:])
        empty='<p hidden="'+H('!pn_empty')+'">Nenhum registro neste recorte.</p>'
        chart=(empty if fid=='PAGR' else '<section class="pn-chart" aria-label="'+E.esc(titulo)+'"><h2>'+E.esc(titulo)+'</h2>'+rows+empty+'</section>')
        body=(CSS+'<div class="pn">'+   # 14/10 (menos é mais): saiu "<Módulo> · Todas as fazendas e safras · Estado atual"; o recorte está na faixa de filtros
          '<div class="pn-grid" aria-label="Indicadores">'+cards+'</div>'+
          '<p hidden="'+H('!pn_missing')+'" role="status">Há dados incompletos. Consulte a origem pelos acessos abaixo.</p>'+
          chart+pna+
          '<nav class="pn-links" aria-label="Acessos do painel">'+links+'</nav></div>')
        prim=E.btn(atalhos[0][0],not re.match(r'^(Consultar|Abrir|Ver|Voltar)\b',atalhos[0][0]),href=atalhos[0][1]).replace('<a ', '<a class="pn-link mod-cartao" ')   # BOT-08: só navegar não é verde
        shell37(fid,'Painel',body,fname=fname,status=None,primary_html=prim,search=False)
