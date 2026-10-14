# -*- coding: utf-8 -*-
"""PAINEL02 / PN-DECISAO: colheita por cultivo e período comparável.

Autoria Codex; Claude integra secao() abaixo dos cartões no ramo PAGR.
Sem build() automático: o compositor chama pnaVals no EXTRAVALS existente.
Regras e unidades vêm de producao.js. Esta leitura não executa comandos.
"""
import engine as E
import json

H = lambda s: '{{' + s + '}}'

JS = 'const PNA_CORES='+json.dumps(dict(impedida=E.RED,atrasada=E.YEL))+';\n'+r'''
function pnaLeitura(c,id) {
 const X=prTal(c,id), k=X.k, R=X.R;
 const semana=k.semanal?prSem(prHoje()):null;
 const ps=semana?R.passes.filter(p=>p.sem===semana):R.passes;
 const versao=semana?prVersaoSem(c,id,semana):null;
 const prev=semana?(versao?versao.sem[semana]:null):prPrevTxt(c,X).v;
 const medido=semana?{
  kg:prSoma(ps.map(p=>p.kg)),cafe:prSoma(ps.map(p=>p.cafe||0)),
  apurar:ps.some(p=>p.apurar),comecou:ps.some(p=>p.apurar||p.kg>0||p.area>0)
 }:R;
 const recebimentos=ps.reduce((n,p)=>n+p.aPesar.length,0);
 const periodo=semana?prSemTxt(semana)+' · '+prBr(prSemIni(semana))+'–'+prBr(prDiaMais(prSemIni(semana),6))+' (em curso)':
  ((PRDC.safras[k.saf]||{}).nome||('Safra '+k.saf));
 return {id,k,periodo,prev,medido,recebimentos,situacao:X.sit,proximo:X.nx,
  previsao:prev===null?'Sem previsão publicada':prUnTxt(k.cultura,prev),
  recebido:prProdTxt(k.cultura,medido),href:'COLH.dc.html#'+encodeURIComponent(id)};
}
function pnaLinhas(c) {
 if(!c||!c.ordens||!c.producao||!c.producao.previsoes) return null;
 return Object.keys(PRDC.cult).filter(id=>PRDC.cult[id].prod).map(id=>pnaLeitura(c,id));
}
function pnaRow(x) {
 const cultivo=x.k.local+' · '+x.k.cultura+(x.k.var?' '+x.k.var:'');
 const situacao=x.situacao+(x.recebimentos?' · '+x.recebimentos+' carga(s) a receber':'');
 return {id:x.id,ro:true,ordk:{prev:x.prev,recebido:x.medido.apurar&&!(x.medido.kg>0)?null:x.medido.kg},v:{cultivo,periodo:x.periodo,prev:x.prev,
  recebido:x.medido.apurar&&!(x.medido.kg>0)?null:x.medido.kg,situacao},
  s:{cultivo:cultivo+' · '+x.k.faz,periodo:x.periodo,prev:x.previsao,recebido:x.recebido,situacao:situacao+' · '+x.proximo},
  p:{cultivo:[{k:'b',t:cultivo},{k:'br'},{k:'mut',t:x.k.faz}],periodo:[{k:'txt',t:x.periodo}],
   prev:[{k:x.prev===null?'mut':'txt',t:x.previsao}],recebido:[{k:'txt',t:x.recebido}],
   situacao:[{k:'chip',t:x.situacao,c:PR_SITCOR[x.situacao]||'gray'},
    {k:'br'},{k:'mut',t:x.recebimentos?x.recebimentos+' carga(s) a receber':x.proximo}]}};
}
// Apresentação do contrato agrPainelRef; regras, prazos e bloqueios pertencem ao domínio.
function pnaOSLinhas(ref) {
 const os=ref&&ref.os;
 if(!os) return null;
 const imp=Array.isArray(os.impedidas)?os.impedidas:os.impedidas===null?[]:null;
 const atr=Array.isArray(os.atrasadas)?os.atrasadas:os.atrasadas===null?[]:null;
 if(!imp||!atr||(os.impedidas===null&&os.atrasadas===null)) return null;
 const itens=imp.concat(atr);
 if(!itens.every(x=>x&&typeof x.id==='string'&&/^OS-[A-Za-z0-9-]+$/.test(x.id)&&
   typeof x.origem==='string'&&x.origem==='OS.dc.html#'+x.id)) return null;
 const m=new Map();
 imp.forEach(x=>m.set(x.id,{...x,impedida:true,atrasada:false}));
 atr.forEach(x=>{const a=m.get(x.id);m.set(x.id,a?{...a,atrasada:true,prevista:x.prevista,dias:x.dias}:{...x,impedida:false,atrasada:true});});
 return [...m.values()];
}
function pnaOSGrupos(os,campo) {
 if(os===null)return null;
 const m=new Map();
 os.forEach(x=>{
  const raw=campo==='causa'?(x.impedida?x.causa:'Janela prevista ultrapassada'):x.dono;
  const label=typeof raw==='string'&&raw.trim()?raw.trim():campo==='causa'?'Causa não informada':'Responsável não informado';
  if(!m.has(label))m.set(label,{label,ids:[],impedidas:0,atrasadas:0});
  const g=m.get(label);g.ids.push(x.id);g.impedidas+=x.impedida?1:0;g.atrasadas+=x.atrasada?1:0;
 });
 const groups=[...m.values()].sort((a,b)=>b.ids.length-a.ids.length||a.label.localeCompare(b.label,'pt-BR'));
 const max=Math.max(1,...groups.map(g=>g.ids.length));
 return groups.map(g=>({...g,n:g.ids.length,
  href:'OS.dc.html#painel='+g.ids.join(','),foco:campo+':'+g.label,
  abrir:'Abrir '+g.ids.length+' O.S. '+(campo==='causa'?'por causa: ':'por quem resolve: ')+g.label,
  situacao:g.impedidas&&g.atrasadas?[g.impedidas+' impedida(s)',g.atrasadas+' atrasada(s)'].join(' · '):'',
  barra:'display:block;height:8px;border-radius:3px;width:'+(100*g.ids.length/max)+'%;background:'+(g.impedidas?PNA_CORES.impedida:PNA_CORES.atrasada)}));
}
// O getter valida o calendário; a apresentação apenas formata a referência devolvida.
function pnaOSReferencia(ref) {
 const data=ref&&ref.os&&ref.os.referencia;
 return typeof data==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(data)?'Prazos até '+data.split('-').reverse().join('/'):'Referência de prazos indisponível';
}

// Só formatação do contrato agrCustoRef. Nenhuma soma, rateio ou desvio de negócio aqui.
function pnaCustoNumero(n) {return typeof n==='number'&&Number.isFinite(n)&&n>=0;}
function pnaCustoValor(n,unidade) {
 return pnaCustoNumero(n)?n.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+' '+unidade:'Indisponível';
}
function pnaCustos(ref) {
 if(!ref||!Array.isArray(ref.cultivos)||!Array.isArray(ref.sem_rateio)||!Array.isArray(ref.fora))return null;
 if(!ref.cultivos.every(x=>x&&typeof x.id==='string'&&typeof x.cultura==='string'&&
   Array.isArray(x.pend)&&Array.isArray(x.sem_orc)))return null;
 const rows=ref.cultivos.map(x=>{
  const parcial=!!x.parcial||!!ref.cobertura_incerta;
  const r=x.real_rs_ha,b=x.orcado_rs_ha,max=Math.max(1,pnaCustoNumero(r)?r:0,pnaCustoNumero(b)?b:0);
  const barra=(n,cor)=>'display:block;height:8px;border-radius:3px;width:'+(pnaCustoNumero(n)?100*n/max:0)+'%;background:'+cor;
  const pend=x.pend.slice();
  if(x.sem_orc.length)pend.unshift('Sem orçamento de plano: '+x.sem_orc.join(', '));
  if(ref.cobertura_incerta)pend.push('Há O.S. executada fora da cobertura do custo; o subtotal não cobre todo o realizado.');
  return {id:x.id,titulo:x.cultura+' · '+x.faz+' · Safra '+x.saf,
   area:pnaCustoValor(x.area_ha,'ha plantados'),parcial,
   estado:parcial?'Parcial · conferir cobertura':'Acumulado da safra',
   orcado:pnaCustoNumero(b)?pnaCustoValor(b,'R$/ha'):'Orçamento por hectare indisponível',
   realizado:pnaCustoNumero(r)?(parcial?'Subtotal conhecido: ':'')+pnaCustoValor(r,'R$/ha'):'Realizado por hectare indisponível',
   barOrcado:barra(b,'#65736A'),barReal:barra(r,'#4976A8'),
   conferido:pnaCustoValor(x.real_conf_rs,'R$'),provisorio:pnaCustoValor(x.real_prov_rs,'R$'),
   pend:pend.map(t=>({texto:t})),temPend:pend.length>0};
 });
 const fora=ref.sem_rateio.map(x=>({...x,tipo:'Sem rateio por talhão'})).concat(
  ref.fora.map(x=>({...x,tipo:'Fora da cobertura do custo'}))).map(x=>({
   titulo:x.os+' · '+x.tipo,
   valor:pnaCustoValor(x.rs,'R$')+(x.pend&&x.pend.length?' conhecidos · parcial':' conhecidos'),
   motivo:[x.motivo||'',...(x.pend||[])].filter(Boolean).join(' · '),
   estados:'Conferido: '+pnaCustoValor(x.real_conf_rs,'R$')+' · Provisório: '+pnaCustoValor(x.real_prov_rs,'R$')
  }));
 return {rows,fora};
}

// Apresentação do contrato agrPainelRef.execucao; não estima área nem soma apontamentos.
function pnaExecucao(ref) {
 const e=ref&&ref.execucao;
 if(!e||!Array.isArray(e.ordens)||!e.ordens.every(x=>x&&typeof x.id==='string'&&
   ['Em execução','Em conferência'].includes(x.etapa)&&x.origem==='OS.dc.html#'+encodeURIComponent(x.id))||
   new Set(e.ordens.map(x=>x.id)).size!==e.ordens.length)return null;
 return e.ordens.map(x=>{
  const area=pnaCustoNumero(x.prevista_ha)&&x.prevista_ha>0&&pnaCustoNumero(x.realizada_ha);
  const percentual=area&&Number.isInteger(x.pct)&&x.pct>=0&&x.pct<=100;
  return {id:x.id,href:x.origem,foco:'execucao:'+x.id,
   titulo:x.id+' · '+(x.talhao||'Talhão não informado'),
   contexto:[x.faz||'Fazenda não informada',x.saf?(/^Safra\s/i.test(x.saf)?x.saf:'Safra '+x.saf):'Safra não informada',x.tipo].filter(Boolean).join(' · '),
   etapa:x.etapa,dono:x.dono||'Responsável não informado',prazo:x.prazo||'Prazo não informado',
   area:area?'Enviada: '+pnaCustoValor(x.realizada_ha,'ha')+' de '+pnaCustoValor(x.prevista_ha,'ha previstos'):'Área de execução indisponível',
   progresso:percentual?x.pct+'% da área prevista enviada':'',
   barra:'display:block;height:8px;background:#4976A8;width:'+(percentual?x.pct:0)+'%',
   sinal:pnaCustoNumero(x.sinal_ha)?(x.sinal_ha>0?pnaCustoValor(x.sinal_ha,'ha no aparelho · ainda sem envio'):''):'Envio dos apontamentos indisponível',
   pendencia:x.pendencia||'',acao:x.etapa==='Em conferência'?'Conferir O.S.':'Acompanhar O.S.',
   abrir:(x.etapa==='Em conferência'?'Conferir ':'Acompanhar ')+x.id};
 });
}

function pnaMip(ref) {
 const m=ref&&ref.mip, keys=['decidir','atrasadas','coleta'];
 if(!m||!keys.every(k=>Array.isArray(m[k])))return null;
 const all=keys.flatMap(k=>m[k]);
 if(!all.every(x=>x&&/^VIS-\d+$/.test(x.vis)&&x.origem==='AG-01.dc.html#'+x.vis)||
   new Set(all.map(x=>x.vis)).size!==all.length)return null;
 const data=x=>typeof x==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(x)?x.split('-').reverse().join('/'):'Data indisponível';
 const dias=x=>Number.isInteger(x)&&x>=0?x+(x===1?' dia':' dias'):'Tempo indisponível';
 const row=(x,k)=>{
  let leitura='',tempo='',estado=x.rotulo||'',detalhe=x.detalhe||'';
  if(k==='decidir') {
   leitura=x.leitura||'Leitura indisponível';
   if(x.unidade)leitura+=' · '+x.unidade;
   if(Number.isInteger(x.pct_nc)&&x.pct_nc>=0)leitura+=' · '+x.pct_nc+'% do NC';
   tempo='Vistoria '+data(x.data)+' · '+dias(x.dias)+' até a referência';
  } else if(k==='atrasadas') {
   estado='Vistoria atrasada';tempo='Prevista '+data(x.prevista)+' · '+dias(x.dias)+' de atraso';
  } else {
   leitura=x.pontos||'Pontos indisponíveis';
   if(x.parcial)detalhe='Resultado parcial: '+(typeof MIP_SIT!=='undefined'&&MIP_SIT[x.parcial]?MIP_SIT[x.parcial][0]:'consulte a vistoria');
  }
  return {id:x.vis,titulo:x.vis+' · '+(x.talhao||'Talhão não informado'),
   contexto:[x.faz||'Fazenda não informada',x.cultura,x.alvo].filter(Boolean).join(' · '),
   estado,leitura,tempo,detalhe,dono:x.dono||'Responsável não informado',
   href:x.origem,foco:'mip:'+x.vis,abrir:'Conferir vistoria '+x.vis};
 };
 return {referencia:'Referência '+data(m.referencia),decidir:m.decidir.map(x=>row(x,'decidir')),
  atrasadas:m.atrasadas.map(x=>row(x,'atrasadas')),coleta:m.coleta.map(x=>row(x,'coleta'))};
}

function pnaVals(self,v) {
 if(typeof mipOuvir==='function')mipOuvir(self);
 g2keep(self,'g_pna');
 if(!self.__pnaFocus){self.__pnaFocus=true;
  const restaura=()=>{const h=history.state||{},grupo=h.pnaGrupo,id=h.pnaFoco;if(!grupo&&!id)return;let n=0;
   const f=()=>{const atributo=grupo?'data-pna-grupo':'data-rid',valor=grupo||id;
    const r=[...document.querySelectorAll('['+atributo+']')].find(e=>e.getAttribute(atributo)===valor);
    if(r){r.focus({preventScroll:true});return;}if(++n<40)setTimeout(f,50);
    else if(grupo){const titulo=document.querySelector('#pna-os-titulo');if(titulo)titulo.focus();}};setTimeout(f,0);};
  document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[data-pna-grupo]');
   if(a&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey&&!e.altKey&&e.button===0)
    history.replaceState(Object.assign({},history.state||{},{pnaGrupo:a.getAttribute('data-pna-grupo'),pnaFoco:null}),'',location.href);});
  restaura();window.addEventListener('pageshow',restaura);
 }
 const c=cenGet(), rows=pnaLinhas(c);
 const ref=typeof agrPainelRef==='function'?agrPainelRef(c,{}):null, os=pnaOSLinhas(ref);
 v.pna_causas=pnaOSGrupos(os,'causa')||[];v.pna_donos=pnaOSGrupos(os,'dono')||[];
 v.pna_os_referencia=pnaOSReferencia(ref);
 const execucao=pnaExecucao(ref);
 v.pna_execucao=execucao||[];v.pna_exec_missing=execucao===null;
 v.pna_exec_empty=execucao!==null&&!execucao.length;
 const mip=pnaMip(ref);v.pna_mip_missing=mip===null;
 v.pna_mip_referencia=mip?mip.referencia:'';
 ['decidir','atrasadas','coleta'].forEach(k=>{v['pna_mip_'+k]=mip?mip[k]:[];v['pna_mip_'+k+'_empty']=!!mip&&!mip[k].length;});
 const custos=pnaCustos(typeof agrCustoRef==='function'?agrCustoRef(c,{}):null);
 v.pna_custos=custos?custos.rows:[];v.pna_custos_fora=custos?custos.fora:[];
 v.pna_custo_missing=custos===null;v.pna_custo_empty=custos!==null&&!custos.rows.length;
 v.pna_custo_fora=!!custos&&custos.fora.length>0;

 v.pna_os_total=os===null?'Indisponível':os.length+' O.S. precisam de ação';
 v.pna_os_missing=os===null;
 v.pna_os_has_data=os!==null&&os.length>0;
 v.pna_os_atraso_missing=os!==null&&ref.os.atrasadas===null;
 v.pna_os_imp_missing=os!==null&&ref.os.impedidas===null;
 v.pna_sem_prazo=ref&&ref.os&&ref.os.n&&Number.isInteger(ref.os.n.sem_prazo)&&ref.os.n.sem_prazo>0?ref.os.n.sem_prazo:0;
 v.pna_os_empty=os!==null&&os.length===0&&!v.pna_os_atraso_missing&&!v.pna_os_imp_missing&&!v.pna_sem_prazo;
 GRIDS.find(g=>g.id==='g_pna').rows=(rows||[]).map(pnaRow);
 v.pna_missing=rows===null;
 self.g2pick=(gid,id)=>{const x=gid==='g_pna'?(rows||[]).find(x=>x.id===id):null;if(x){
  history.replaceState(Object.assign({},history.state||{},{pnaFoco:id,pnaGrupo:null}),'',location.href);location.href=x.href;}};
}
'''


def secao():
    """Retorna (HTML, JS) para a tela já iniciada; não substitui cartões/shell."""
    table=E.grid([
        dict(k='cultivo',l='Cultivo · fazenda',w=220),
        dict(k='periodo',l='Período',w=170),
        dict(k='prev',l='Previsão publicada',t='num',a='r',w=145),
        dict(k='recebido',l='Recebido',t='num',a='r',w=145),
        dict(k='situacao',l='Situação · próximo passo',w=245),
    ],[],gid='g_pna',edit=dict(m='pick'),total=False)
    formula=('Previsão publicada e cargas recebidas do mesmo cultivo: semana em curso para culturas semanais; safra para anuais. '
             'Recebido soma os passes daquele período pelas regras de Previsão e colheita. '
             'Sem previsão não significa zero; café sem rendimento medido fica a apurar. '
             'Não soma culturas, períodos ou unidades e não calcula desvio final em período aberto. Fonte: Previsão e colheita.')
    body=(f'<section aria-label="Colheita por cultivo"><h2 style="font-size:16px;color:{E.INK}">Colheita · previsto e recebido '
          f'<button type="button" class="g2dica-i" aria-label="Como comparar a colheita" data-dica="{E.esc(formula)}" '
          f'style="width:44px;height:44px;border:0;background:transparent;color:{E.MUTED};font:inherit">ⓘ</button></h2>'
          '<p role="status" hidden="'+H('!pna_missing')+'">Dados de produção indisponíveis. Abra Previsão e colheita para conferir a origem.</p>'+
          table+'</section>')
    explicacao=('Cada O.S. é contada uma vez em cada gráfico, mesmo impedida e atrasada. '
                'Causa e responsável vêm da projeção da O.S.; a causa agrupa os impedimentos pela classificação da origem, ou atraso quando não há impedimento. '
                'As duas distribuições descrevem as mesmas ordens e não devem ser somadas. '
                'Barras relativas ao maior grupo. Fonte: O.S., todas as fazendas e safras disponíveis. '
                'Área afetada não fornecida pela origem; não estimamos hectares por contagem de ordens.')
    def grafico(titulo, campo):
        return ('<section class="pn-chart"><h3 style="font-size:15px;margin:0 0 12px">'+titulo+'</h3>'
                '<ul style="list-style:none;padding:0;margin:0"><sc-for list="'+H(campo)+'" as="g" hint-placeholder-count="3">'
                '<li class="pna-grupo" style="margin:16px 0;overflow-wrap:anywhere">'
                '<a href="'+H('g.href')+'" data-pna-grupo="'+H('g.foco')+'" aria-label="'+H('g.abrir')+'" '
                'style="display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:44px;color:inherit">'
                '<span>'+H('g.label')+'</span><strong style="white-space:nowrap">'+H('g.n')+' O.S.</strong></a>'
                '<div aria-hidden="true" style="height:8px;background:#EEF1EE;border-radius:3px;margin:6px 0"><span style="'+H('g.barra')+'"></span></div>'
                '<span hidden="'+H('!g.situacao')+'" style="font-size:12px">'+H('g.situacao')+'</span></li></sc-for></ul></section>')
    pendencias=('<sc-if value="'+H('pna_os_has_data')+'" hint-placeholder-val="{{true}}"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px">'+
                grafico('Por causa','pna_causas')+grafico('Por quem resolve','pna_donos')+'</div></sc-if>')
    osbody=('<section aria-label="O.S. que precisam de atenção">'
        f'<h2 id="pna-os-titulo" tabindex="-1" style="font-size:16px;color:{E.INK}">O.S. · onde agir primeiro</h2>'
        '<p>'+H('pna_os_total')+' <button type="button" class="g2dica-i" aria-label="Como ler os impedimentos e atrasos" data-dica="'+E.esc(explicacao)+'" style="width:44px;height:44px;border:0;background:transparent">ⓘ</button></p>'
        '<p style="font-size:12px">'+H('pna_os_referencia')+'</p>'
        '<p role="status" hidden="'+H('!pna_os_missing')+'">Dados de impedimentos e prazos indisponíveis. Consulte a origem em O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_atraso_missing')+'">Prazos indisponíveis para verificar atrasos. Consulte a janela na O.S.; os impedimentos disponíveis seguem abaixo.</p>'
        '<p role="status" hidden="'+H('!pna_os_imp_missing')+'">Impedimentos indisponíveis. Os atrasos disponíveis seguem abaixo.</p>'
        '<p role="status" hidden="'+H('!pna_sem_prazo')+'">'+H('pna_sem_prazo')+' O.S. sem prazo válido; não avaliadas quanto a atraso. Confira a janela na O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_empty')+'">Nenhuma O.S. impedida ou atrasada neste recorte.</p>'+
        pendencias+'</section>')

    custo_formula=('Orçado por hectare vem do plano da safra; realizado é acumulado até o estado atual, dividido pela área plantada. '
                   'Não representa economia ou desvio final da safra. Provisório e conferido são partes distintas do realizado. '
                   'Barras comparam valores dentro da mesma cultura, fazenda e safra; cada par tem sua própria escala. '
                   'Custos sem preço, sem vínculo ou sem rateio ficam identificados e não são distribuídos automaticamente. '
                   'Fonte: mesma conta da camada Custos do Mapa. Não soma razões entre culturas.')
    custos=('<section aria-label="Custos por cultura">'
        f'<h2 style="font-size:16px;color:{E.INK}">Custos · orçado e realizado '
        '<button type="button" class="g2dica-i" aria-label="Como comparar os custos" data-dica="'+E.esc(custo_formula)+'" style="width:44px;height:44px;border:0;background:transparent">ⓘ</button></h2>'
        '<p>Orçamento da safra × realizado acumulado · R$/ha plantado · Fonte: Custos do Mapa</p>'
        '<p role="status" hidden="'+H('!pna_custo_missing')+'">Dados de custos indisponíveis. Consulte Custos para conferir a origem.</p>'
        '<p role="status" hidden="'+H('!pna_custo_empty')+'">Nenhuma cultura com custo disponível neste recorte.</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px">'
        '<sc-for list="'+H('pna_custos')+'" as="custo" hint-placeholder-count="2">'
        '<section class="pn-chart pna-custo" style="overflow-wrap:anywhere">'
        '<h3 style="font-size:15px;margin:0 0 8px">'+H('custo.titulo')+'</h3>'
        '<p>'+H('custo.estado')+' · '+H('custo.area')+'</p>'
        '<p>Orçado: '+H('custo.orcado')+'</p>'
        '<div aria-hidden="true" style="height:8px;background:#EEF1EE"><span style="'+H('custo.barOrcado')+'"></span></div>'
        '<p>Realizado: '+H('custo.realizado')+'</p>'
        '<div aria-hidden="true" style="height:8px;background:#EEF1EE"><span style="'+H('custo.barReal')+'"></span></div>'
        '<p style="font-size:12px;font-variant-numeric:tabular-nums">Conferido: '+H('custo.conferido')+' · Provisório: '+H('custo.provisorio')+'</p>'
        '<ul hidden="'+H('!custo.temPend')+'" style="padding-left:18px;font-size:12px"><sc-for list="'+H('custo.pend')+'" as="p">'
        '<li>'+H('p.texto')+'</li></sc-for></ul></section></sc-for></div>'
        '<section hidden="'+H('!pna_custo_fora')+'"><h3 style="font-size:15px">O.S. fora dos totais por cultura</h3>'
        '<ul style="padding-left:18px"><sc-for list="'+H('pna_custos_fora')+'" as="f">'
        '<li style="margin-bottom:12px;overflow-wrap:anywhere"><strong>'+H('f.titulo')+'</strong> · '+H('f.valor')+
        '<br>'+H('f.estados')+'<br>'+H('f.motivo')+'</li></sc-for></ul></section>'
        '<a href="GE-03.dc.html" style="display:inline-flex;align-items:center;min-height:44px">Conferir composição dos custos</a></section>')
    exec_formula=('Área enviada e prevista pela mesma projeção da O.S., incluindo ajustes da liberação. '
                  'Apontamentos ainda no aparelho não entram na enviada. 100% da área não significa O.S. encerrada. '
                  'Uma mesma área pode receber mais de uma operação; não representa área única da fazenda. '
                  'Fonte: O.S., todas as fazendas e safras disponíveis.')
    execucao=('<section aria-label="Execução das O.S.">'
        f'<h2 style="font-size:16px;color:{E.INK}">Execução · prevista e enviada '
        '<button type="button" class="g2dica-i" aria-label="Como comparar a execução" data-dica="'+E.esc(exec_formula)+'" style="width:44px;height:44px;border:0;background:transparent">ⓘ</button></h2>'
        '<p role="status" hidden="'+H('!pna_exec_missing')+'">Execução indisponível. Consulte a origem em O.S.</p>'
        '<p role="status" hidden="'+H('!pna_exec_empty')+'">Nenhuma O.S. em execução ou em conferência neste recorte.</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px">'
        '<sc-for list="'+H('pna_execucao')+'" as="exec" hint-placeholder-count="3">'
        '<section class="pn-chart pna-exec" style="overflow-wrap:anywhere" data-pna-exec="'+H('exec.id')+'">'
        '<h3 style="font-size:15px;margin:0 0 8px">'+H('exec.titulo')+'</h3>'
        '<p>'+H('exec.contexto')+'</p><strong>'+H('exec.etapa')+'</strong>'
        '<p>'+H('exec.area')+'</p>'
        '<div hidden="'+H('!exec.progresso')+'"><span>'+H('exec.progresso')+'</span>'
        '<div aria-hidden="true" style="height:8px;background:#EEF1EE;margin-top:6px"><span style="'+H('exec.barra')+'"></span></div></div>'
        '<p hidden="'+H('!exec.sinal')+'">'+H('exec.sinal')+'</p>'
        '<p hidden="'+H('!exec.pendencia')+'">'+H('exec.pendencia')+'</p>'
        '<p style="font-size:12px">'+H('exec.dono')+' · '+H('exec.prazo')+'</p>'
        '<a href="'+H('exec.href')+'" data-pna-grupo="'+H('exec.foco')+'" aria-label="'+H('exec.abrir')+'" '
        'style="display:inline-flex;align-items:center;min-height:44px">'+H('exec.acao')+'</a>'
        '</section></sc-for></div></section>')
    def mip_lista(titulo,key,vazio):
        return ('<section class="pn-chart"><h3 style="font-size:15px;margin:0 0 12px">'+titulo+'</h3>'
            '<p hidden="'+H('!pna_mip_'+key+'_empty')+'">'+vazio+'</p>'
            '<ul style="list-style:none;padding:0;margin:0"><sc-for list="'+H('pna_mip_'+key)+'" as="vis" hint-placeholder-count="2">'
            '<li class="pna-mip" data-pna-mip="'+H('vis.id')+'" style="padding:12px 0;border-top:1px solid #E4E9E5;overflow-wrap:anywhere">'
            '<strong>'+H('vis.titulo')+'</strong><p>'+H('vis.contexto')+'</p><strong>'+H('vis.estado')+'</strong>'
            '<p hidden="'+H('!vis.leitura')+'">'+H('vis.leitura')+'</p>'
            '<p hidden="'+H('!vis.tempo')+'" style="font-size:12px">'+H('vis.tempo')+'</p>'
            '<p hidden="'+H('!vis.detalhe')+'">'+H('vis.detalhe')+'</p><p style="font-size:12px">'+H('vis.dono')+'</p>'
            '<a href="'+H('vis.href')+'" data-pna-grupo="'+H('vis.foco')+'" aria-label="'+H('vis.abrir')+'" '
            'style="display:inline-flex;align-items:center;min-height:44px">Conferir vistoria</a></li></sc-for></ul></section>')
    mip_formula=('Situação pela mesma regra do Monitoramento (MIP). NC = nível de controle do protocolo. '
                 'Percentual do NC não é percentual de área afetada; critério por presença não tem percentual do NC. '
                 'Coleta parcial ou no aparelho não significa vistoria concluída. '
                 'A O.S. de controle cancelada devolve a decisão ao responsável técnico. '
                 'Fonte: Monitoramento, todas as fazendas. A origem não informa safra por vistoria.')
    mip=('<section aria-label="Atenção no MIP">'
        f'<h2 style="font-size:16px;color:{E.INK}">MIP · onde agir '
        '<button type="button" class="g2dica-i" aria-label="Como ler o MIP" data-dica="'+E.esc(mip_formula)+'" style="width:44px;height:44px;border:0;background:transparent">ⓘ</button></h2>'
        '<p role="status" hidden="'+H('!pna_mip_missing')+'">Dados de MIP indisponíveis neste recorte. Consulte Monitoramento; a vistoria não informa safra.</p>'
        '<sc-if value="'+H('!pna_mip_missing')+'" hint-placeholder-val="{{true}}"><p style="font-size:12px">'+H('pna_mip_referencia')+'</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px;align-items:start">'+
        mip_lista('Decisão do responsável técnico','decidir','Nenhuma decisão pendente neste recorte.')+
        mip_lista('Vistorias atrasadas','atrasadas','Nenhuma vistoria atrasada neste recorte.')+
        mip_lista('Coleta a resolver','coleta','Nenhuma coleta pendente neste recorte.')+
        '</div></sc-if></section>')
    return osbody+execucao+mip+custos+body, JS
