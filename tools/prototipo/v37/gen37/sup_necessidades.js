// SUP / ENG-011: consulta de necessidade de uma OM, sem reservar ou emitir compra.
// c é o estado canônico da manutenção; manNec e manLivreIt são do mesmo domínio.
function supPedirAte(data, politica) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data || '') || !politica) return null;
  const prazo = politica.prazo, seguranca = politica.seguranca;
  if (!Number.isSafeInteger(prazo) || prazo < 0 || !Number.isSafeInteger(seguranca) || seguranca < 0) return null;
  const dia = new Date(data + 'T00:00:00Z');
  if (!Number.isFinite(dia.getTime()) || dia.toISOString().slice(0,10) !== data) return null;
  dia.setUTCDate(dia.getUTCDate() - prazo - seguranca);
  return Number.isFinite(dia.getTime()) ? dia.toISOString().slice(0,10) : null;
}
function supNecMan(c, id, politica) {
  const o = c && c.oms && c.oms[id];
  const out = {origem:id, ativo:o ? o.aid : null, servico:o ? o.serv : null,
    necessaria:o ? o.janIso : null, pedirAte:null, itens:[], pendencias:[]};
  if (!o) { out.pendencias.push('Ordem de manutenção não encontrada.'); return out; }
  // A consulta segue a mesma etapa que manFalta; execução já reservada não compra novamente.
  if (o.etapa !== 'A liberar') return out;
  out.pedirAte = supPedirAte(o.janIso, politica);
  const itens = new Map(), invalidos = new Set();
  for (const p of o.pecas || []) {
    const it = c.itens && c.itens[p.item];
    if (!it) { out.pendencias.push('Peça sem cadastro de estoque: ' + (p.nome || p.item || 'não identificada')); continue; }
    if (![p.qtd,p.res,it.saldo,it.reservado].every(n=>Number.isFinite(n)&&n>=0) || p.res>p.qtd || it.reservado>it.saldo) {
      invalidos.add(p.item); out.pendencias.push('Conferir quantidades e reservas de ' + it.nome); continue;
    }
    if (!itens.has(p.item)) itens.set(p.item,{item:p.item,nome:it.nome,un:it.un,demanda:0,reservaPropria:0,necessidade:0,livre:manLivreIt(c,p.item),falta:0});
    const r=itens.get(p.item);
    r.demanda+=p.qtd; r.reservaPropria+=p.res; r.necessidade+=manNec(p);
  }
  for (const r of itens.values()) { if(invalidos.has(r.item)) continue; r.falta=Math.max(0,r.necessidade-r.livre); r.pendenciaPrazo=r.falta>0&&!out.pedirAte; out.itens.push(r); }
  return out;
}
function supAtualizaNec(self) {
  const x=supNecMan(manGet(),'OM-0234',null), rows=RW(self,'g_nec');
  for(let i=rows.length-1;i>=0;i--) if(String(rows[i].id).startsWith('MAN|')) rows.splice(i,1);
  for(const it of x.itens) rows.push({id:'MAN|'+it.item,ro:true,
    v:{item:it.nome,data:x.necessaria,dem:it.demanda,disp:it.livre,firm:0,falta:it.falta,un:it.un,pedir:null},s:{},
    p:{item:[B(it.nome),M(x.origem+' · '+x.servico)],dem:[T(nf(it.demanda)+' '+it.un)],
      disp:[T(nf(it.livre)+' '+it.un),M('reserva própria '+nf(it.reservaPropria)+' '+it.un)],
      firm:[M('Conferir em Compras de materiais')],
      falta:[chipc(it.falta>0?nf(it.falta)+' '+it.un:'Coberta no estoque',it.falta>0?'yellow':'green')],
      pedir:[M(it.falta>0?'Pendente · sem prazo de fornecedor/segurança cadastrado':'Sem necessidade de comprar'),M('necessária '+dm(x.necessaria))],
      acao:[{k:'link',t:'Conferir origem',h:'MA.dc.html#om='+x.origem}]},
    o:[{t:'Necessidade '+nf(it.demanda)+' − reserva própria '+nf(it.reservaPropria)+' − livre '+nf(it.livre)+' = '+nf(it.falta)+' '+it.un},
      {t:it.pendenciaPrazo?'Conferir data necessária e política de prazo/segurança.':'Saldo da manutenção atual. Entregas futuras não presumidas.'},
      {t:'Abrir a ordem',h:'MA.dc.html#om='+x.origem}]});
  if(x.pendencias.length) rows.push({id:'MAN|pendencias',ro:true,v:{item:x.origem},s:{},
    p:{item:[B(x.origem)],falta:[M(x.pendencias.join(' '))],acao:[{k:'link',t:'Conferir origem',h:'MA.dc.html#om='+x.origem}]}});
}
