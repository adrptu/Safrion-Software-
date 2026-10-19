# -*- coding: utf-8 -*-
"""PAINEL-03 · Painel de gestão único (PG.dc.html). Especificação: docs/painel03/README.md.

Pedido do proprietário (18/10/2026): painéis "cirurgicamente úteis para uma gestão estratégica, tática e operacional ... mostrando com clareza
os pontos chave a serem atacados, decididos ... num só lugar". Um painel com uma fileira de abas (Prioridades e um módulo por aba); dentro do
módulo, um bloco por funcionalidade (o item do menu), na ordem do processo (ABA-01). Substitui os painéis PAGR, PMAN e PSUP (PAINEL-01/02, Codex),
que entram aqui com as mesmas contas: pnValores, agrPainelRef, agrCustoRef e a seção do PAINEL-02 (painel_agricola.secao).
Só lê (nenhum comando, nenhuma gravação); coleção ausente ou inválida = "Sem dados", nunca zero. Nenhuma fórmula agronômica ou econômica nova:
a única regra própria é a ordem de "Atacar agora" (classe do dano, depois impacto em R$, ha e dias; §3 da especificação).
"""
import json
import engine as E
import cenario
import dados_manutencao as DM
import dados2 as D2
from ui37 import shell37, HEIGHTS37
from areas.modulos import JS_VOLTA
from areas import paineis as PN

H = lambda s: '{{' + s + '}}'
FNAME = 'PG.dc.html'
# (chave, aba) na ordem da barra (MENU2); a chave vai no endereço (#mod=agr) e nos ganchos do teste
MODS = [('pri', 'Prioridades'), ('agr', 'Agrícola'), ('man', 'Manutenção'), ('sup', 'Suprimentos'), ('com', 'Comercial'), ('cre', 'Crédito')]
# blocos por módulo: (chave, título = nome do item do menu, destino do "Abrir"); a ordem é a do processo
BLOCOS = {
    'agr': [('os', 'Ordem de Serviço', 'OS.dc.html'), ('mip', 'Pragas e doenças (MIP/MID)', 'AG-01.dc.html'),
            ('colh', 'Previsão e colheita', 'COLH.dc.html'), ('cus', 'Custos e fechamento', 'GE-03.dc.html')],
    'man': [('sem', 'Pendências sem ordem', 'MA.dc.html#vis=semordem'), ('oms', 'Ordens de manutenção', 'MA.dc.html#vis=ordens'),
            ('atv', 'Ativos e disponibilidade', 'MA.dc.html#vis=ativos')],
    'sup': [('est', 'Estoque', 'EST.dc.html')],
    'com': [('ven', 'Contratos e pedidos', 'VEN.dc.html'), ('ofe', 'Oferta e compromissos', 'PCOM.dc.html'), ('rec', 'Recebíveis', 'PCOM.dc.html')],
    'cre': [('fic', 'Ficha do grupo', 'GE-08.dc.html#vis=ficha')],
}

JS = r'''
/* ===== PAINEL-03 · painel de gestão único (docs/painel03/README.md). Lê as contas canônicas; não grava; null = "Sem dados" ===== */
const PG_CLS={1:'Lei e segurança',2:'Lavoura',3:'Dinheiro e estoque',4:'Prazo e ativos'};
function pgNf(x,d){ return Number(x).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function pgRs(x){ return 'R$ '+pgNf(x,2); }
function pgDdmm(s){ return typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)?s.slice(8,10)+'/'+s.slice(5,7):(s||''); }
function pgDias(a,b){ const x=Date.parse(a+'T00:00:00Z'), y=Date.parse(b+'T00:00:00Z'); return isNaN(x)||isNaN(y)?null:Math.round((y-x)/864e5); }
/* Sem política de meta versionada (D11), desvio numérico não recebe avaliação de conformidade.
   Alertas de domínio continuam usando suas próprias regras (impedimento, déficit, receituário). */
function pgCor(){ return 'gray'; }
function pgSemMeta(texto,parcial){ return [texto,parcial?'Indicador parcial':'','Meta não configurada'].filter(Boolean).join(' · '); }
/* cartão de indicador: nível (Resultado | Plano | Hoje), nome, valor (número, texto ou null), referência e desvio (sub), cor, dica (fórmula,
   fonte e dono) e origem (href) */
function pgK(niv,nome,v,sub,cor,dica,href){ return {niv,nome,v:v===null||v===undefined?'Sem dados':(typeof v==='number'?pgNf(v):String(v)),sub:sub||'',
  cor:v===null||v===undefined?'gray':(cor||'none'),dica,href}; }
/* ordem de "Atacar agora" (§3): classe do dano; dentro dela, impacto em R$, depois ha, depois dias; entre iguais, o mais antigo; por fim a chave */
function pgOrdem(a,b){ if(a.classe!==b.classe) return a.classe-b.classe;
  for(const u of ['rs','ha','dias']){ const x=(a.imp&&a.imp[u])||0, y=(b.imp&&b.imp[u])||0; if(x!==y) return y-x; }
  const da=a.desde||'9999-99-99', db=b.desde||'9999-99-99'; if(da!==db) return da<db?-1:1; return a.k<b.k?-1:(a.k>b.k?1:0); }
// a classe do ativo bloqueado vem da causa (revisão do Codex 6252555281): bloqueio marcado com risco à segurança (seg no registro da condição)
// é "Lei e segurança"; o resto é "Prazo e ativos"
function pgClasseAtivo(a){ const h=(a&&a.condHist&&a.condHist[0])||{}; return (a&&(a.seg||h.seg))?1:4; }
function pgImpTxt(imp){ const p=[]; if(imp.rs) p.push(pgRs(imp.rs)); if(imp.ha) p.push(pgNf(imp.ha,1)+' ha'); if(imp.dias) p.push(imp.dias+(imp.dias>1?' dias':' dia')); return p.join(' · ')||'—'; }

function pgAgr(c,R){ const B=R.blocos.agr, I=R.itens;
  const pv=pnValores(c,'PAGR');
  let ref=null; try{ ref=agrPainelRef(c,{}); }catch(e){ ref=null; }
  const os=ref&&ref.os, ex=ref&&ref.execucao, mip=ref&&ref.mip;
  const area={}; try{ (osProjecaoEstado(c,id=>/^OB-/.test(id))||[]).forEach(o=>{ if(o&&typeof o.area==='number'&&o.area>0) area[o.id]=o.area; }); }catch(e){}
  const k=pv.labels.map((l,i)=>pgK('Hoje',l,pv.vals[i],'',null,'Contagem das O.S. agrícolas na fase '+l+'. Fonte: cenário das O.S. (a mesma contagem do kanban); fora o beneficiamento.','OS.dc.html'));
  const nA=os?os.n.atrasadas:null, nI=os?os.n.impedidas:null;
  k.push(pgK('Hoje','Atrasadas',nA,os&&os.n.sem_prazo?os.n.sem_prazo+' sem prazo':(os&&os.referencia?'referência '+pgDdmm(os.referencia):''),nA>0?'red':'green',
    'O.S. A liberar, Liberadas ou Em execução com o fim da janela antes da data de referência. Ordem sem prazo não é julgada (conta à parte). Dono: PCP.','OS.dc.html'));
  const causas={}; ((os&&os.impedidas)||[]).forEach(o=>{ causas[o.causa]=(causas[o.causa]||0)+1; });
  k.push(pgK('Hoje','Impedidas',nI,Object.keys(causas).map(x=>causas[x]+' '+x.toLowerCase()).join(' · '),nI>0?'red':'green',
    'O.S. abertas com selo de impedimento, pela causa: receituário divergente, insumo no Estoque, máquina ou equipamento, outro. Fonte: a projeção da tela O.S.','OS.dc.html'));
  const exT=ex&&ex.total&&typeof ex.total.prevista_ha==='number'?ex.total:null; let pct=null; if(exT&&exT.prevista_ha>0) pct=Math.round(exT.realizada_ha/exT.prevista_ha*100);
  k.push(pgK('Plano','Execução em andamento',pct===null?(exT?'—':null):pct+'%',exT?pgNf(exT.realizada_ha,1)+' de '+pgNf(exT.prevista_ha,1)+' ha enviados':'',null,
    'Área realizada (apontada e enviada) ÷ área prevista das O.S. Em execução e Em conferência. Apontado no aparelho e ainda não enviado fica fora. Fonte: agrExecucao (PAINEL-02).','OS.dc.html'));
  B.os=k;
  // itens: impedida e atrasada da mesma O.S. viram um item só (a impedida leva os dias de atraso)
  const por={};
  ((os&&os.impedidas)||[]).forEach(o=>{ por[o.id]={k:'os:'+o.id,mod:'agr',b:'os',func:'Ordem de Serviço',tipo:'atacar',classe:o.causa==='Receituário divergente'?1:2,
    titulo:o.id+' impedida · '+o.causa,onde:[o.talhao,o.faz].filter(Boolean).join(' · '),imp:{ha:area[o.id]||0},dono:o.dono||'',desde:'',quando:o.etapa,verbo:'Resolver',href:o.origem}; });
  ((os&&os.atrasadas)||[]).forEach(o=>{ const x=por[o.id]; if(x){ x.imp.dias=o.dias; x.quando=o.etapa+' · prazo '+pgDdmm(o.prevista); return; }
    por[o.id]={k:'os:'+o.id,mod:'agr',b:'os',func:'Ordem de Serviço',tipo:'atacar',classe:2,titulo:o.id+' atrasada · '+o.etapa,onde:[o.talhao,o.faz].filter(Boolean).join(' · '),
      imp:{ha:area[o.id]||0,dias:o.dias},dono:o.dono||'',desde:o.prevista,quando:'prazo '+pgDdmm(o.prevista),verbo:o.etapa==='A liberar'?'Liberar':(o.etapa==='Liberadas'?'Iniciar':'Concluir'),href:o.origem}; });
  Object.values(por).forEach(x=>I.push(x));
  // MIP: decidir (RT) e vistorias atrasadas
  B.mip=[pgK('Hoje','Acima do nível de controle',mip?mip.n.decidir:null,'decisão do RT',mip&&mip.n.decidir>0?'red':'green','Vistorias acima do nível de controle, com foco ou com O.S. de controle cancelada: o RT decide. Fonte: mipSit (a mesma regra do AG-01).','AG-01.dc.html'),
    pgK('Hoje','Vistorias atrasadas',mip?mip.n.atrasadas:null,'',mip&&mip.n.atrasadas>0?'yellow':'green','Vistorias com o ritmo do protocolo vencido. Fonte: mipSit.','AG-01.dc.html'),
    pgK('Hoje','Coleta pendente',mip?mip.n.coleta:null,'no aparelho ou incompleta',null,'Vistorias ainda no aparelho ou incompletas. Fonte: mipSit.','AG-01.dc.html')];
  (mip?mip.decidir:[]).forEach(x=>I.push({k:'mip:'+x.vis,mod:'agr',b:'mip',func:'Pragas e doenças',tipo:'decidir',classe:2,titulo:'Vistoria '+x.talhao+' · '+x.alvo+' · '+x.rotulo,
    onde:[x.talhao,x.faz].filter(Boolean).join(' · '),imp:{dias:Math.max(0,x.dias||0)},dono:x.dono||'RT',desde:x.data,quando:'desde '+pgDdmm(x.data),verbo:'Decidir',href:x.origem}));
  (mip?mip.atrasadas:[]).forEach(x=>I.push({k:'mipa:'+x.vis,mod:'agr',b:'mip',func:'Pragas e doenças',tipo:'atacar',classe:2,titulo:'Vistoria atrasada · '+x.talhao+' · '+x.alvo,
    onde:[x.talhao,x.faz].filter(Boolean).join(' · '),imp:{dias:Math.max(0,x.dias||0)},dono:x.dono||'',desde:x.prevista,quando:'prevista '+pgDdmm(x.prevista),verbo:'Vistoriar',href:x.origem}));
  // Custos: execução × previsto da mesma área (a conta da camada Custos do Mapa) e quanto do orçado já foi
  let cu=null; try{ cu=agrCustoRef(c,{}); }catch(e){ cu=null; }
  const cc=(cu&&cu.cultivos)||[]; R.custos=cc;
  B.cus=cu===null?[pgK('Resultado','Custo das O.S.',null,'','','Custo das O.S. por cultura. Fonte: agrCustoRef (camada Custos do Mapa).','GE-03.dc.html')]:
    cc.map(g=>{ const d=g.desvio_exec_pct, cons=g.consumo_orc_pct;
      return pgK('Resultado',g.cultura+' · '+g.faz+' '+g.saf,d===null?(g.parcial?'Parcial':'—'):(d>0?'+':'')+pgNf(d,1)+'%',
        pgSemMeta('execução × previsto de '+pgNf(g.ha_exec,1)+' ha'+(cons===null?'':' · '+cons+'% do orçado'),g.parcial),pgCor(),
        'Custo realizado da área executada contra o previsto da mesma área (acima = pior). Parcial: preço ausente, ordem sem rateio ou fora da cobertura ('+((g.pend||[]).slice(0,2).join('; ')||'sem pendência')+'). Fonte: agrCustoRef. Dono: gestor.','GE-03.dc.html'); });
}
function pgMan(c,R){ const B=R.blocos.man, I=R.itens, pm=pnValores(c,'PMAN'), m=c&&c.man;
  B.sem=[pgK('Hoje','Pendências sem ordem',pm.vals[0],'vencidas ou na janela',pm.vals[0]>0?'yellow':'green','Planos vencidos ou com janela até o horizonte, mais achados, relatos e alertas sem ordem. Fonte: manSemOrdem (a visão Sem ordem). Dono: PCM.','MA.dc.html#vis=semordem')];
  B.oms=[pgK('Hoje','Ordens abertas',pm.vals[1],'',null,'Ordens não encerradas nem canceladas. Fonte: manAberta.','MA.dc.html#vis=ordens'),
    pgK('Hoje','Em execução',pm.vals[2],'',null,'Ordens na etapa Em execução. Fonte: cenário da Manutenção.','MA.dc.html#vis=ordens')]
    .concat(pm.labels.slice(0,2).map((l,i)=>pgK('Hoje',l,pm.bars[i],'',null,'Ordens de manutenção na fase '+l+'. Fonte: cenário da Manutenção.','MA.dc.html#vis=ordens')));
  const at=m&&m.ativos&&typeof m.ativos==='object'?Object.values(m.ativos).filter(a=>a&&typeof a.cond==='string'):null;
  const disp=at&&at.length?Math.round(at.filter(a=>a.cond!=='Bloqueado').length/at.length*100):null;
  B.atv=[pgK('Hoje','Ativos bloqueados',pm.vals[3],'',pm.vals[3]>0?'red':'green','Ativos com condição Bloqueado. Fonte: cenário da Manutenção. Dono: PCM.','MA.dc.html#vis=ativos'),
    pgK('Plano','Ativos liberados',disp===null?null:disp+'%',pgSemMeta(at?at.filter(a=>a.cond!=='Bloqueado').length+' de '+at.length+' ativos':''),pgCor(),
      'Ativos sem condição Bloqueado ÷ ativos do cadastro da Manutenção (sem meta configurada). Não é a disponibilidade em horas (F2). Fonte: cenário da Manutenção.','MA.dc.html#vis=ativos')];
  let so=null; if(pm.vals[0]!==null){ try{ so=manSemOrdem(m); }catch(e){ so=null; } }
  if(so){ so.venc.forEach(l=>{ const venc=l.x.sit==='Vencida', d=l.x.prev&&venc?pgDias(l.x.prev,m.hoje):null;
      I.push({k:'man:'+l.vk+'|'+(l.sid||''),mod:'man',b:'sem',func:'Pendências sem ordem',tipo:'atacar',classe:4,titulo:(l.s?l.s.nome:'Plano')+' · '+(l.a.nome||l.aid),onde:l.p.nome||l.pid,
        imp:{dias:d&&d>0?d:0},dono:'PCM',desde:l.x.prev||'',quando:venc?'vencida':'na janela'+(l.x.prev?' · '+pgDdmm(l.x.prev):''),verbo:'Gerar ordem',href:'MA.dc.html#vis=semordem'}); });
    so.ach.forEach(q=>{ const a=m.ativos[q.aid]; I.push({k:'ach:'+q.id,mod:'man',b:'sem',func:'Pendências sem ordem',tipo:'atacar',classe:4,titulo:'Achado '+q.id+' · '+q.sint,onde:(a&&a.nome)||q.aid,
      imp:{dias:Math.max(0,pgDias(q.em,m.hoje)||0)},dono:'PCM',desde:q.em||'',quando:'desde '+pgDdmm(q.em),verbo:'Tratar',href:'MA.dc.html#vis=semordem'}); }); }
  (at||[]).filter(a=>a.cond==='Bloqueado').forEach(a=>I.push({k:'atv:'+a.id,mod:'man',b:'atv',func:'Ativos e disponibilidade',tipo:'atacar',classe:pgClasseAtivo(a),titulo:(a.nome||a.id)+' bloqueado'+(pgClasseAtivo(a)===1?' · risco à segurança':''),onde:a.local||'',
    imp:{},dono:'PCM',desde:'',quando:'',verbo:'Consultar ativo',href:'MA.dc.html#vis=ativos'}));
}
function pgSup(c,R){ const B=R.blocos.sup, I=R.itens, ps=pnValores(c,'PSUP');
  /* sem a coleção de lotes, o Estoque está ausente: Sem dados; com lotes e sem ajustes ainda (a coleção nasce no 1º ajuste), zero */
  const temL=!!(c&&c.lotes&&typeof c.lotes==='object'), aj=!temL?null:(Array.isArray(c.ajustes)?c.ajustes.filter(a=>a&&a.estado==='Aguardando gestor'):(c.ajustes===undefined?[]:null));
  B.est=[pgK('Hoje','Lotes com saldo físico',ps.vals[0],'',null,'Lotes com saldo físico maior que zero; inclui reservado e quarentena. Fonte: cenário do Estoque.','EST.dc.html'),
    pgK('Hoje','Lotes com reserva',ps.vals[1],'',null,'Lotes com quantidade reservada. Fonte: cenário do Estoque.','EST.dc.html'),
    pgK('Hoje','Lotes em quarentena',ps.vals[2],'liberar ou reprovar',ps.vals[2]>0?'yellow':'green','Lotes com quantidade em quarentena: a liberação exige decisão. Fonte: cenário do Estoque.','EST.dc.html'),
    pgK('Hoje','Requisições a entregar',ps.vals[3],'O.S. liberadas ou em execução',ps.vals[3]>0?'yellow':'green','Requisições de O.S. Liberadas ou Em execução com saldo a entregar. Fonte: cenSaldoEntregar. Dono: almoxarife.','EST.dc.html'),
    pgK('Hoje','Ajustes a aprovar',aj===null?null:aj.length,'inventário',aj&&aj.length?'yellow':'green','Ajustes de inventário aguardando o gestor. Fonte: cenário do Estoque.','EST.dc.html')];
  const ls=c&&c.lotes&&typeof c.lotes==='object'?Object.keys(c.lotes).map(k=>Object.assign({key:k},c.lotes[k])):[];
  ls.filter(l=>Number(l.quarentena)>0).forEach(l=>I.push({k:'qua:'+l.key,mod:'sup',b:'est',func:'Estoque',tipo:'decidir',classe:1,titulo:'Quarentena · '+l.prod+' · lote '+l.lote,onde:l.local||'',
    imp:{},dono:'Almoxarife e RT',desde:'',quando:pgNf(l.quarentena,2)+' '+(l.un||''),verbo:'Liberar ou reprovar',href:'EST.dc.html'}));
  (aj||[]).forEach(a=>I.push({k:'aj:'+a.id,mod:'sup',b:'est',func:'Estoque',tipo:'decidir',classe:3,titulo:'Ajuste '+a.id+' · '+a.prod+' · lote '+a.lote,onde:'',imp:{},dono:'Gestor',desde:'',
    quando:(a.dif>0?'+':'')+pgNf(a.dif,2)+' '+(a.un||''),verbo:'Aprovar ou recusar',href:'EST.dc.html'}));
  const imp=new Set(R.itens.filter(x=>x.k.indexOf('os:')===0).map(x=>x.k.slice(3)));
  const rs=c&&c.reqs&&typeof c.reqs==='object'?Object.values(c.reqs):[];
  if(ps.vals[3]!==null) rs.filter(r=>r&&c.ordens[r.os]&&['Liberadas','Em execução'].includes(c.ordens[r.os].etapa)&&r.itens.some(i=>cenSaldoEntregar(i)>1e-6)&&!imp.has(r.os))
    .forEach(r=>I.push({k:'req:'+r.id,mod:'sup',b:'est',func:'Estoque',tipo:'atacar',classe:3,titulo:'Entregar requisição '+r.id+' · '+r.os,onde:c.ordens[r.os].etapa,imp:{},dono:'Almoxarife',desde:'',
      quando:r.itens.filter(i=>cenSaldoEntregar(i)>1e-6).length+' item(ns) a entregar',verbo:'Entregar',href:'EST.dc.html'}));
}
function pgCom(c,R){ const B=R.blocos.com, I=R.itens; let pz=null, ind=null, pa=null, tit=null; const hoje=typeof prHoje==='function'?prHoje():null;
  if(c&&c.producao&&typeof c.producao==='object'){   // sem o estado da produção (vendas, lotes e cargas), o Comercial fica Sem dados, nunca zero
    try{ pz=comPrecos(c,hoje); }catch(e){ pz=null; } try{ ind=comIndicadores(c,hoje); }catch(e){ ind=null; } try{ pa=comPainel(c,hoje,'4'); }catch(e){ pa=null; } try{ tit=comTitulos(c); }catch(e){ tit=null; } }
  R.precos=pz||[];
  B.ven=pz===null?[pgK('Resultado','Preço médio vendido',null,'','','Média ponderada das vendas. Fonte: comPrecos.','VEN.dc.html')]:pz.filter(x=>x.medC!==null||x.ref).map(x=>{
    const d=x.medC!==null&&x.ref&&x.ref.p>0?(x.ref.p-x.medC)/x.ref.p:null;
    return pgK('Resultado','Preço médio · '+x.prod,x.medC===null?'—':comPrecoTxt(x.cu,x.medC),pgSemMeta(x.ref?'referência '+comPrecoTxt(x.cu,x.ref.p)+(d===null?'':' · '+(d>0?'−':'+')+pgNf(Math.abs(d)*100,1)+'%'):'sem cotação de referência',(x.amb||[]).length>0),
      pgCor(),'Preço médio contratado (Σ valor ÷ Σ quantidade, só venda) contra a referência de mercado; abaixo = pior. '+((x.amb||[]).length?'Fora da média, saca a conferir: '+x.amb.join(', ')+'. ':'')+'Fonte: comPrecos. Dono: comercial.','VEN.dc.html'); });
  const def=pa?pa.filter(r=>r.sit==='Déficit'):null, sus=pa?pa.filter(r=>r.sit==='Suspenso'):null;
  B.ofe=[pgK('Plano','Períodos em déficit',def?def.length:null,'compromisso acima da oferta',def&&def.length?'red':'green','Produto e período em que as vendas passam da oferta (estoque apto ou previsão publicada), próximas 4 semanas. Fonte: comPainel.','PCOM.dc.html'),
    pgK('Plano','Períodos suspensos',sus?sus.length:null,'saca a conferir',sus&&sus.length?'yellow':'green','Período cuja conta está suspensa por venda em saca sem a massa conhecida. Fonte: comPainel.','PCOM.dc.html')];
  B.rec=[pgK('Resultado','A receber',ind?pgRs(ind.aRec):null,'a vencer',null,'Títulos de venda entregues e não vencidos. Fonte: comIndicadores. O recebimento é do Financeiro.','PCOM.dc.html'),
    pgK('Hoje','Vencido',ind?pgRs(ind.venc):null,'cobrar',ind&&ind.venc>0?'red':'green','Títulos de venda vencidos e não recebidos. Fonte: comIndicadores. Dono: financeiro.','PCOM.dc.html'),
    pgK('Resultado','Entregue em 30 dias',ind?pgRs(ind.ent30):null,'valor entregue',null,'Valor das cargas de venda entregues nos últimos 30 dias (em trânsito fica fora). Fonte: comIndicadores.','PCOM.dc.html')];
  (tit||[]).filter(t=>comVencido(t,hoje)).forEach(t=>I.push({k:'tit:'+t.rm,mod:'com',b:'rec',func:'Recebíveis',tipo:'atacar',classe:3,titulo:'Cobrar '+t.cliente+' · '+t.venda,onde:t.prod,
    imp:{rs:t.valor,dias:Math.max(0,pgDias(t.venc,hoje)||0)},dono:'Financeiro',desde:t.venc,quando:'venceu '+pgDdmm(t.venc),verbo:'Cobrar',href:'VEN.dc.html#'+encodeURIComponent(t.venda)}));
  (def||[]).forEach(r=>I.push({k:'def:'+r.id,mod:'com',b:'ofe',func:'Oferta e compromissos',tipo:'atacar',classe:3,titulo:'Déficit · '+r.prod+' · '+r.perT,onde:'',imp:{},dono:'Comercial',desde:'',
    quando:'compromisso acima da oferta',verbo:'Rever vendas',href:'PCOM.dc.html'}));
}
function pgCre(c,R){ const B=R.blocos.cre, I=R.itens; let fi=null; try{ fi=credFichaLer().items; }catch(e){ fi=null; }
  const hoje=OSD.hoje, pend=fi?fi.filter(r=>r.valor===null):null, velha=fi?fi.filter(r=>r.data&&pgDias(r.data,hoje)>365):null;
  B.fic=[pgK('Resultado','Bens na ficha',fi?fi.length:null,'',null,'Bens declarados na ficha do grupo. Fonte: a ficha do Crédito (credito_docs.js).','GE-08.dc.html#vis=ficha'),
    pgK('Hoje','Valor pendente',pend?pend.length:null,'declaração sem valor',pend&&pend.length?'yellow':'green','Bens da ficha sem valor declarado. Fonte: a ficha do Crédito.','GE-08.dc.html#vis=ficha'),
    pgK('Hoje','Declarações com mais de 1 ano',velha?velha.length:null,'confirmar vigência',velha&&velha.length?'yellow':'green','Bens cuja declaração tem mais de 365 dias: o credor pede a vigência confirmada. Fonte: a ficha do Crédito.','GE-08.dc.html#vis=ficha')];
  (pend||[]).forEach(r=>I.push({k:'fic:'+r.id,mod:'cre',b:'fic',func:'Ficha do grupo',tipo:'atacar',classe:4,titulo:'Declarar o valor · '+r.nome,onde:r.tipo||'',imp:{},dono:r.responsavel||'Gestor',desde:'',quando:'',verbo:'Declarar',href:'GE-08.dc.html#vis=ficha'}));
}
/* tudo do painel numa leitura: blocos por módulo, itens (atacar e decidir) já em ordem, alavancas por cultura */
function pgDados(c){ const R={blocos:{agr:{},man:{},sup:{},com:{},cre:{}},itens:[],custos:[],precos:[]};
  [pgAgr,pgMan,pgSup,pgCom,pgCre].forEach(f=>{ try{ f(c,R); }catch(e){ R.erro=(R.erro||[]).concat(f.name+': '+e.message); } });
  const vistos=new Set(); R.itens=R.itens.filter(x=>{ if(vistos.has(x.k)) return false; vistos.add(x.k); return true; }).sort(pgOrdem);
  R.itens.forEach(x=>{ x.impTxt=pgImpTxt(x.imp||{}); x.cls=PG_CLS[x.classe]; });
  return R; }
/* alavancas do resultado (estratégico): por cultivo do custo, o desvio da execução e o consumo do orçado; o preço médio da cultura (empresa) */
function pgAlavancas(R){ const pc={}; (R.precos||[]).forEach(x=>{ if(!pc[x.cu]) pc[x.cu]=x; });
  return (R.custos||[]).map(g=>{ const d=g.desvio_exec_pct, cons=g.consumo_orc_pct, p=pc[g.cultura]||null;
    return {id:g.id,cult:g.cultura,ctx:g.faz+' · '+g.saf+' · '+pgNf(g.area_ha,1)+' ha',
      cus:d===null?(g.parcial?'Parcial':'—'):(d>0?'+':'')+pgNf(d,1)+'%',cusc:pgCor(),cons:pgSemMeta(cons===null?'—':cons+'% do orçado',g.parcial),
      pre:p&&p.medC!==null?comPrecoTxt(p.cu,p.medC):'—',prer:pgSemMeta(p&&p.ref?'ref. '+comPrecoTxt(p.cu,p.ref.p):'sem referência',p&&(p.amb||[]).length>0),prec:pgCor()}; }); }
/* leitura para os testes (como window.__com do Comercial): só funções que leem */
try{ window.__pg={pgDados,pgOrdem,pgClasseAtivo,pgAlavancas,pgCor,pnValores,agrPainelRef,agrCustoRef,cenGet,cenClone,CEN0}; }catch(e){}
const PG_COR={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],none:['#15201A','transparent']};
function pgSel(self,k){ self.setState({pg_mod:k,pg_todos:false}); try{ history.replaceState(history.state,'',location.pathname+location.search+(k==='pri'?'':'#mod='+k)); }catch(e){} }
function EXTRAVALS(self,v){
  cenOuvir(self); if(typeof mipOuvir==='function') mipOuvir(self);
  if(!self.__pgHash){ self.__pgHash=1; const leH=()=>{ const m=(String(location.hash).match(/mod=([a-z]+)/)||[])[1]; if(m&&PG_MODS.indexOf(m)>=0&&m!==self.state.pg_mod) self.setState({pg_mod:m}); };
    leH(); try{ window.addEventListener('hashchange',leH); }catch(e){} }
  if(typeof pnaVals==='function') pnaVals(self,v);   // PAINEL-02: a seção do Agrícola (colheita, O.S., execução, MIP e custos) com os mesmos dados
  const c=cenGet(), R=pgDados(c), mod=PG_MODS.indexOf(self.state.pg_mod)>=0?self.state.pg_mod:((String(location.hash).match(/mod=([a-z]+)/)||[])[1]||'pri');
  const at=mod==='pri'?PG_MODS[0]:mod; v.pg_erro=!!R.erro; v.pg_erro_t=R.erro?('Parte do painel sem dados: '+R.erro.join('; ')):'';
  PG_MODS.forEach(k=>{ const on=k===at, n=k==='pri'?0:R.itens.filter(x=>x.mod===k).length;
    v['pg_'+k+'_on']=on; v['pg_'+k+'_sel']=on?'true':'false'; v['pg_'+k+'_ti']=on?'0':'-1'; v['pg_'+k+'_st']=on?PG_SEG_ON:PG_SEG_OFF; v['pg_'+k+'_go']=()=>pgSel(self,k);
    v['pg_'+k+'_n']=n>0?String(n):''; v['pg_'+k+'_tem']=n>0; });
  v.pg_tk=(e)=>{ const i=PG_MODS.indexOf(at); let j=-1; if(e.key==='ArrowRight') j=(i+1)%PG_MODS.length; else if(e.key==='ArrowLeft') j=(i+PG_MODS.length-1)%PG_MODS.length;
    else if(e.key==='Home') j=0; else if(e.key==='End') j=PG_MODS.length-1; if(j<0) return; e.preventDefault(); pgSel(self,PG_MODS[j]);
    setTimeout(()=>{ const b=document.querySelector('[role=tab][data-pg="'+PG_MODS[j]+'"]'); if(b) b.focus(); },0); };
  const cor=x=>Object.assign(x,{bc:PG_COR[x.cor][0],bg:PG_COR[x.cor][1]});
  Object.keys(R.blocos).forEach(m=>Object.keys(R.blocos[m]).forEach(b=>{ v['pg_b_'+m+'_'+b]=R.blocos[m][b].map(x=>cor(Object.assign({},x))); }));
  const lin=x=>Object.assign({},x,{ccor:PG_COR[x.classe===1?'red':(x.classe===2?'yellow':'gray')][0],cbg:PG_COR[x.classe===1?'red':(x.classe===2?'yellow':'gray')][1],
    onde2:[x.func,x.onde].filter(Boolean).join(' · '),dono2:x.dono||'—',quando2:x.quando||''});
  const todos=!!self.state.pg_todos, LIM=7;
  ['atacar','decidir'].forEach(t=>{ const xs=R.itens.filter(x=>x.tipo===t).map(lin); v['pg_'+t]=todos?xs:xs.slice(0,LIM); v['pg_'+t+'_n']=xs.length;
    v['pg_'+t+'_mais']=xs.length>LIM; v['pg_'+t+'_vazio']=!xs.length;
  });
  // no módulo, cada funcionalidade mostra o que atacar e decidir nela, logo abaixo dos seus indicadores (a mesma ordem da lista geral)
  Object.keys(R.blocos).forEach(m=>Object.keys(PG_BLOCOS[m]||{}).forEach(b=>{ const ys=R.itens.filter(x=>x.mod===m&&x.b===b).map(lin); v['pg_i_'+m+'_'+b]=ys; v['pg_i_'+m+'_'+b+'_tem']=ys.length>0; v['pg_i_'+m+'_'+b+'_n']=ys.length; }));
  const VOLTA=PG_VOLTA[at]; v.pg_volta_tem=!!VOLTA; v.pg_volta_t=VOLTA?VOLTA[0]:''; v.pg_volta_href=VOLTA?VOLTA[1]:''; v.pg_volta_aria=VOLTA?'Voltar para '+VOLTA[0]:'';
  v.pg_mais_t=todos?'Mostrar só os 7 primeiros':'Ver todos'; v.pg_mais=()=>self.setState({pg_todos:!todos});
  v.pg_alav=pgAlavancas(R).map(a=>Object.assign(a,{cusbc:PG_COR[a.cusc][0],cusbg:PG_COR[a.cusc][1],prebc:PG_COR[a.prec][0],prebg:PG_COR[a.prec][1]}));
  v.pg_alav_vazio=!v.pg_alav.length;
}
'''

CSS = '''<style>
.pg{display:flex;flex-direction:column;gap:18px;min-width:0}
.pg-abas{display:flex;flex-wrap:nowrap;overflow-x:auto;padding:3px;border-radius:999px;background:#EEF1EE;gap:2px;max-width:100%;align-self:flex-start;scrollbar-width:none}
.pg-abas::-webkit-scrollbar{display:none}.pg-abas [role=tab]{min-height:44px}
.pg-abas .pg-n{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:999px;background:#FDE8E6;color:#B42318;font-size:11.5px;font-weight:800}
.pg-abas .pg-n[hidden],.pg-abas .pg-n:empty{display:none}
.pg-bloco{border:1px solid #E4E9E5;border-radius:14px;background:#fff;padding:14px 16px;display:flex;flex-direction:column;gap:12px;min-width:0}
.pg-bh{display:flex;align-items:center;justify-content:space-between;gap:8px;min-width:0}
.pg-bh h2{font-size:15px;font-weight:800;margin:0;color:#15201A;min-width:0}
.pg-bh a{min-height:44px;display:inline-flex;align-items:center;padding:0 6px;color:#1E7A4C;font-weight:700;font-size:13px;text-decoration:none;white-space:nowrap}
.pg-bh a:hover{text-decoration:underline}
.pg-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px;min-width:0}
.pg-card{border:1px solid #E4E9E5;border-radius:12px;background:#fff;display:flex;flex-direction:column;min-width:0;position:relative}
.pg-card:hover{border-color:#1E7A4C}
.pg-ct{display:flex;align-items:center;justify-content:space-between;gap:4px;padding:6px 4px 0 12px}
.pg-niv{font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#65736A}
.pg-tip{flex-shrink:0;width:44px;height:36px;border:0;background:transparent;color:#65736A;cursor:pointer;font:inherit;font-size:14px}
.pg-cl{display:flex;flex-direction:column;gap:2px;padding:0 12px 12px;color:#15201A;text-decoration:none;min-width:0;min-height:44px}
.pg-nome{font-size:13px;font-weight:700;color:#3E4A43;overflow-wrap:anywhere}
.pg-v{font-size:24px;font-weight:800;letter-spacing:-.01em;line-height:1.2;overflow-wrap:anywhere}
.pg-sub{font-size:12px;font-weight:600;align-self:flex-start;border-radius:999px;padding:1px 8px;overflow-wrap:anywhere;max-width:100%}
.pg-sub:empty{display:none}
.pg-lista{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.pg-it{display:grid;grid-template-columns:130px minmax(0,1fr) minmax(90px,auto) minmax(90px,auto) auto;align-items:center;gap:4px 12px;padding:8px 12px;border:1px solid #E4E9E5;border-radius:10px;background:#fff;color:#15201A;text-decoration:none;min-height:44px;font-size:13px}
.pg-it:hover{border-color:#1E7A4C;background:#F4FAF6}
.pg-cls{font-size:11.5px;font-weight:800;border-radius:999px;padding:2px 8px;justify-self:start;white-space:nowrap}
.pg-tt{font-weight:700;min-width:0;overflow-wrap:anywhere}.pg-tt small{display:block;font-weight:600;color:#65736A;font-size:12px}
.pg-imp{font-weight:700;white-space:nowrap}.pg-dono{color:#3E4A43;min-width:0;overflow-wrap:anywhere}.pg-dono small{display:block;color:#65736A;font-size:12px}
.pg-verbo{color:#1E7A4C;font-weight:800;white-space:nowrap}
.pg-vazio{color:#65736A;font-size:13px;margin:0}
.pg-mais{align-self:flex-start;min-height:44px;border:1px solid #E4E9E5;border-radius:10px;background:#fff;font:inherit;font-size:13px;font-weight:700;padding:0 14px;cursor:pointer;color:#15201A}
.pg-tab{width:100%;border-collapse:collapse;font-size:13px}.pg-tab th{text-align:left;font-size:12px;color:#65736A;font-weight:700;padding:6px 8px;border-bottom:1px solid #E4E9E5}
.pg-tab td{padding:8px;border-bottom:1px solid #EEF1EE;vertical-align:top}.pg-tab td small{display:block;color:#65736A;font-size:12px}
.pg-chip{display:inline-block;font-weight:800;border-radius:999px;padding:1px 8px}
.pg-rola{overflow-x:auto;min-width:0}
.pg-det>summary{min-height:44px;display:flex;align-items:center;gap:6px;cursor:pointer;font-weight:700;font-size:13px;color:#15201A;list-style:none}
.pg-det>summary::-webkit-details-marker{display:none}.pg-det>summary::before{content:'›';display:inline-block;transition:transform .15s;font-size:16px;color:#65736A}
.pg-det[open]>summary::before{transform:rotate(90deg)}
.pg :focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}
@media(max-width:700px){.pg-it{grid-template-columns:minmax(0,1fr) auto}.pg-cls{grid-column:1 / -1}.pg-imp,.pg-dono{grid-column:1}.pg-verbo{grid-column:2;grid-row:2}
 .pg-cards{grid-template-columns:repeat(2,minmax(0,1fr))}.pg-v{font-size:20px}}
@media(max-width:420px){.pg-cards{grid-template-columns:1fr}}
</style>'''


def _cards(lista):
    """cartões de um bloco (pgK): nível e ⓘ no alto; nome, valor e referência num link para a origem"""
    return (f'<div class="pg-cards"><sc-for list="{H(lista)}" as="k" hint-placeholder-count="3"><div class="pg-card">'
            f'<div class="pg-ct"><span class="pg-niv">{H("k.niv")}</span><button type="button" class="pg-tip g2dica-i" aria-label="Como calcular: {H("k.nome")}" data-dica="{H("k.dica")}">ⓘ</button></div>'
            f'<a class="pg-cl" href="{H("k.href")}"><span class="pg-nome">{H("k.nome")}</span><strong class="pg-v" style="color: {H("k.bc")};">{H("k.v")}</strong>'
            f'<span class="pg-sub" style="color: {H("k.bc")}; background: {H("k.bg")};">{H("k.sub")}</span></a></div></sc-for></div>')


def _lista(chave, vazio):
    """linhas de "Atacar agora" ou "Decidir": classe do dano, o quê e onde, impacto, dono e quando, verbo que leva à origem"""
    return (f'<sc-if value="{H(chave+"_vazio")}" hint-placeholder-val="false"><p class="pg-vazio">{E.esc(vazio)}</p></sc-if>'
            f'<ul class="pg-lista"><sc-for list="{H(chave)}" as="i" hint-placeholder-count="3"><li><a class="pg-it" href="{H("i.href")}" data-pg-item="{H("i.k")}">'
            f'<span class="pg-cls" style="color: {H("i.ccor")}; background: {H("i.cbg")};">{H("i.cls")}</span>'
            f'<span class="pg-tt">{H("i.titulo")}<small>{H("i.onde2")}</small></span><span class="pg-imp">{H("i.impTxt")}</span>'
            f'<span class="pg-dono">{H("i.dono2")}<small>{H("i.quando2")}</small></span><span class="pg-verbo">{H("i.verbo")} ›</span></a></li></sc-for></ul>')


def _itens_bloco(m, b):
    """o que atacar e decidir nesta funcionalidade, logo abaixo dos indicadores dela (a mesma ordem da lista geral)"""
    k = f'pg_i_{m}_{b}'
    return (f'<sc-if value="{H(k+"_tem")}" hint-placeholder-val="false"><ul class="pg-lista" aria-label="A atacar e decidir">'
            f'<sc-for list="{H(k)}" as="i" hint-placeholder-count="2"><li><a class="pg-it" href="{H("i.href")}" data-pg-item="{H("i.k")}">'
            f'<span class="pg-cls" style="color: {H("i.ccor")}; background: {H("i.cbg")};">{H("i.cls")}</span>'
            f'<span class="pg-tt">{H("i.titulo")}<small>{H("i.onde")}</small></span><span class="pg-imp">{H("i.impTxt")}</span>'
            f'<span class="pg-dono">{H("i.dono2")}<small>{H("i.quando2")}</small></span><span class="pg-verbo">{H("i.verbo")} ›</span></a></li></sc-for></ul></sc-if>')


def _bloco(m, b, titulo, href, extra='', cards=True):
    return (f'<section class="pg-bloco" data-pg-bloco="{m}-{b}" aria-label="{E.esc(titulo)}"><div class="pg-bh"><h2>{E.esc(titulo)}</h2>'
            f'<a href="{href}">Abrir ›</a></div>{_cards("pg_b_"+m+"_"+b) if cards else ""}{_itens_bloco(m, b)}{extra}</section>')


def build():
    E._reset_screen(FNAME); HEIGHTS37[FNAME] = 1500
    E.EXTRAJS[0] = (cenario.js_prefixo() + DM.js_regras() + JS_VOLTA
                    + 'const PN_ID="PG";const PN_ALERT=[];\n' + PN.JS[:PN.JS.index('function EXTRAVALS(')])
    # PAINEL-02 (Codex): a seção do Agrícola, repartida pelos blocos (O.S. e execução, MIP, custos, colheita), com o pnaVals de sempre
    from areas.painel_agricola import secao
    pna, pna_js = secao(); E.EXTRAJS[0] += pna_js
    from areas.processo_os import JS_NUCLEO as _OSN, _ordens as _ords
    E.EXTRAJS[0] += 'const OSD = ' + json.dumps(dict(ords=_ords(), hoje=D2.HOJE_ISO), ensure_ascii=False).replace('</', '<\\/') + ';\n' + _OSN
    import areas.custo_dominio as _CUS
    E.EXTRAJS[0] += _CUS.js_prefixo()
    import dados_mip as _MIP
    E.EXTRAJS[0] += _MIP.js_prefixo()
    import dados_comercial as _DCOM, os as _os
    E.EXTRAJS[0] += _DCOM.js_regras()   # o núcleo da carência (CARD) já vem com a O.S.
    E.EXTRAJS[0] += open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'credito_docs.js'), encoding='utf-8').read() + '\n'
    from ui37 import HUB37 as _HUB
    E.EXTRAJS[0] += ('const PG_VOLTA=' + json.dumps({k: [n, _HUB[n]] for k, n in MODS if n in _HUB}, ensure_ascii=False) + ';\n')
    E.EXTRAJS[0] += ('const PG_MODS=' + json.dumps([k for k, _ in MODS]) + ', PG_BLOCOS=' + json.dumps({m: {b: t for b, t, _ in bs} for m, bs in BLOCOS.items()}, ensure_ascii=False) + ', PG_SEG_ON=' + json.dumps(E.SEG_ON()) + ', PG_SEG_OFF=' + json.dumps(E.SEG_OFF()) + ';\n' + JS)
    marcas = ['<section aria-label="Execução das O.S.">', '<section aria-label="Atenção no MIP">', '<section aria-label="Custos por cultura">', '<section aria-label="Colheita por cultivo">']
    pos = [pna.index(x) for x in marcas]; assert pos == sorted(pos), 'PAINEL-02 mudou a ordem das seções'
    os_det, exe_det, mip_det, cus_det, colh_det = pna[:pos[0]], pna[pos[0]:pos[1]], pna[pos[1]:pos[2]], pna[pos[2]:pos[3]], pna[pos[3]:]
    det = lambda html, t='Detalhe': f'<details class="pg-det"><summary>{t}</summary>{html}</details>'
    abas = ''.join(f'<button type="button" role="tab" data-pg="{k}" id="pg-tab-{k}" aria-controls="pg-pane-{k}" aria-selected="{H("pg_"+k+"_sel")}" tabindex="{H("pg_"+k+"_ti")}" '
                   f'onClick="{H("pg_"+k+"_go")}" style="{H("pg_"+k+"_st")}">{E.esc(n)}<span class="pg-n" hidden="{H("!pg_"+k+"_tem")}" aria-label="itens a atacar ou decidir">{H("pg_"+k+"_n")}</span></button>' for k, n in MODS)
    tablist = f'<div role="tablist" aria-label="Painel por módulo" class="pg-abas" onKeyDown="{H("pg_tk")}">{abas}</div>'
    pane = lambda k, html: f'<sc-if value="{H("pg_"+k+"_on")}" hint-placeholder-val="{"true" if k == "pri" else "false"}"><div role="tabpanel" id="pg-pane-{k}" aria-labelledby="pg-tab-{k}" class="pg" tabindex="-1">{html}</div></sc-if>'
    alav = (f'<section class="pg-bloco" aria-label="Alavancas do resultado"><div class="pg-bh"><h2>Alavancas do resultado</h2>'
            f'<button type="button" class="pg-tip g2dica-i" aria-label="Como ler as alavancas" data-dica="Por cultivo: o custo realizado da área executada contra o previsto da mesma área (acima = pior) e quanto do orçado já foi; o preço médio vendido da cultura contra a referência de mercado (abaixo = pior). A margem prevista entra na próxima fatia.">ⓘ</button></div>'
            # SEP-20261015 (b): a tabela abre o corpo do bloco (o cabeçalho dela separa sozinho); o aviso de vazio vem depois (ds_test A2c)
            f'<div><div class="pg-rola g2caixa"><table class="pg-tab"><thead><tr><th scope="col">Cultivo</th><th scope="col">Custo da execução</th><th scope="col">Preço médio vendido</th></tr></thead><tbody>'
            f'<sc-for list="{H("pg_alav")}" as="a" hint-placeholder-count="3"><tr data-pg-alav="{H("a.id")}"><td><strong>{H("a.cult")}</strong><small>{H("a.ctx")}</small></td>'
            f'<td><a href="GE-03.dc.html" class="pg-chip" style="color: {H("a.cusbc")}; background: {H("a.cusbg")}; text-decoration: none;">{H("a.cus")}</a><small>{H("a.cons")}</small></td>'
            f'<td><a href="VEN.dc.html" class="pg-chip" style="color: {H("a.prebc")}; background: {H("a.prebg")}; text-decoration: none;">{H("a.pre")}</a><small>{H("a.prer")}</small></td></tr></sc-for>'
            f'</tbody></table></div><sc-if value="{H("pg_alav_vazio")}" hint-placeholder-val="false"><p class="pg-vazio">Sem custo por cultura no recorte.</p></sc-if></div></section>')
    sec = lambda t, chave, vazio, mais=False: (f'<section class="pg-bloco" aria-label="{E.esc(t)}"><div class="pg-bh"><h2>{E.esc(t)} · {H(chave+"_n")}</h2>'
            f'<button type="button" class="pg-tip g2dica-i" aria-label="Como a lista é ordenada" data-dica="Ordem: classe do dano (lei e segurança, lavoura, dinheiro e estoque, prazo e ativos); dentro dela, o maior impacto em R$, depois em ha, depois em dias; entre iguais, o mais antigo. O mesmo item não aparece duas vezes.">ⓘ</button></div>'
            + _lista(chave, vazio)
            + (f'<sc-if value="{H(chave+"_mais")}" hint-placeholder-val="false"><button type="button" class="pg-mais" onClick="{H("pg_mais")}">{H("pg_mais_t")}</button></sc-if>' if mais else '') + '</section>')
    pri = (alav + sec('Atacar agora', 'pg_atacar', 'Nada a atacar no recorte.', True) + sec('Decidir', 'pg_decidir', 'Nenhuma decisão esperando.', True))
    mod_html = {}
    for m, _ in MODS[1:]:
        extra = {('agr', 'os'): det(os_det + exe_det), ('agr', 'mip'): det(mip_det), ('agr', 'cus'): det(cus_det), ('agr', 'colh'): colh_det}
        mod_html[m] = (''.join(_bloco(m, b, t, h, extra.get((m, b), ''), cards=(m, b) != ('agr', 'colh')) for b, t, h in BLOCOS[m]))   # a colheita é a seção do PAINEL-02, sem cartões
    erro = f'<sc-if value="{H("pg_erro")}" hint-placeholder-val="false"><p role="status" class="pg-vazio">{H("pg_erro_t")}</p></sc-if>'
    body = PN.CSS + CSS + f'<div class="pg">{tablist}{erro}' + pane('pri', pri) + ''.join(pane(m, mod_html[m]) for m, _ in MODS[1:]) + '</div>'
    # "‹ Módulo" (CAB-1, nav_modulos N3): na aba de um módulo, a mesma pílula leva à tela de entrada dele; em Prioridades não aparece
    from ui37 import LINE, SURF, INK
    volta = (f'<sc-if value="{H("pg_volta_tem")}" hint-placeholder-val="false"><a href="{H("pg_volta_href")}" class="volta37" aria-label="{H("pg_volta_aria")}" '
             f'style="text-decoration: none; display: inline-flex; align-items: center; gap: 4px; min-height: 36px; padding: 0 14px 0 10px; border: 1px solid {LINE}; '
             f'border-radius: 999px; background: {SURF}; color: {INK}; font-size: 13px; font-weight: 700; flex-shrink: 0;"><span aria-hidden="true" style="font-size: 16px; line-height: 1;">‹</span>{H("pg_volta_t")}</a></sc-if>')
    shell37('PG', 'Painel', body, fname=FNAME, status=None, search=False, voltar_dyn=volta)
