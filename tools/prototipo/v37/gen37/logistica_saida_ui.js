/* LO-02det: projeção da RM oficial; nenhum ledger de logística paralelo. */
function loRm(c,hash){const ex=comP(c).expedicoes||{};const q=new URLSearchParams(String(hash||'').replace(/^#/,''));if(q.has('rm'))return ex[q.get('rm')]||null;return Object.values(ex).find(r=>r.st==='Programada')||null;}
function loRef(rm){return JSON.stringify([rm.id,rm.pedido,rm.st,rm.lotes,rm.saida||null]);}
function loRow(id,v,ro=true){return {id,v,ro,s:{},p:{}};}
function loRows(self,id,rows){const sp=GRIDS.find(g=>g.id===id);if(sp){const a=g2rows(self,sp);a.splice(0,a.length,...rows);}return sp;}
function loRefresh(self){const c=cenGet(),hash=String(location.hash||'');let rm;
 if(self.loHash!==hash){self.loHash=hash;self.loId=null;}
 if(self.loId)rm=(comP(c).expedicoes||{})[self.loId]||null;else{rm=loRm(c,hash);if(rm)self.loId=rm.id;}
 const P=comP(c),pedido=rm?(P.pedidos[rm.pedido]||{}):{};
 loRows(self,'g_cf',rm?comLotesRm(rm).map(l=>loRow(l.lote,{item:pedido.prod||'Produto não informado',lote:l.lote,ped:rm.pedido,sep:'Não informado',car:rm.saida?(l.kg+' kg'):'Ainda não saiu',saldo:'Previsto: '+l.prev+' kg',conf:rm.st})):[]);
 const sp=loRows(self,'g_ps',rm?[loRow(rm.id,{tk:rm.id,bruto:rm.saida?rm.saida.bruto:'',tara:rm.saida?rm.saida.tara:'',liq:rm.saida?rm.saida.liq+' kg':'Bruto − tara',base:'kg',orig:rm.saida?'Saída por '+rm.saida.quem:'Informar pesos do ticket'},rm.st!=='Programada')]:[]);
 if(sp&&!g2st(self,sp.id).fm){sp.edit.fields=[{k:'bruto',l:'Peso bruto (kg)',t:'txt',req:true},{k:'tara',l:'Tara (kg)',t:'txt',req:true}];
  if(rm&&comLotesRm(rm).length>1)comLotesRm(rm).forEach((l,i)=>sp.edit.fields.push({k:'kg_'+i,l:'Peso do lote '+l.lote+' (kg)',t:'txt',req:true}));
 }
 loRows(self,'g_ck',rm?[loRow('preview',{item:'Lacre e autorização de saída',estado:'Prévia · sem registro ou autorização neste detalhe',resp:'Conferir no processo responsável'})]:[]);
 loRows(self,'g_sa',rm?(P.movs||[]).filter(m=>m.rm===rm.id).map(m=>loRow(m.id,{ev:m.id+' · '+m.tipo,estado:m.lote+' · '+m.kg+' kg',quem:(m.quem||'')+' · '+(m.d||'')+' '+(m.at||'')})):[]);
 return {rm,pedido};
}
function PREVALS(self,v){loRefresh(self);}
function EXTRAVALS(self,v){cenOuvir(self);const x=loRefresh(self),rm=x.rm;
 v.lo_id=rm?rm.id:'';v.lo_contexto=rm?rm.id+' · '+rm.pedido+' · '+(x.pedido.cliente||''):'Nenhuma carga programada';
 v.lo_estado=rm?rm.st:'Nenhuma carga programada';
 v.lo_proximo=rm&&rm.st==='Programada'?'Informar pesos e confirmar saída':'Abrir Expedição';
 v.lo_expedicao='EXPED.dc.html'+(rm?'#'+encodeURIComponent(rm.id):'');
 v.lo_revisar=()=>{if(rm&&rm.st==='Programada')g2open(self,GRIDS.find(g=>g.id==='g_ps'),rm.id);else self.setState({g2toast:'Nenhuma carga programada neste detalhe. Abra Expedição.'});};
 self.g2openDraft=(gid,r,d)=>{if(gid!=='g_ps')return d;const atual=(comP(cenGet()).expedicoes||{})[r.id];return Object.assign({},d,{_rm:r.id,_ref:atual?loRef(atual):'',_lotes:JSON.stringify(atual?comLotesRm(atual).map(l=>l.lote):[]),_chave:'LO-SAI-'+Date.now()+'-'+Math.random().toString(36).slice(2)});};
 self.g2check=(gid,rows,r,d)=>{if(gid!=='g_ps')return {};const errs={};
  if(!prNumOk(d.bruto)||!(prNum(d.bruto)>0))errs.bruto='Informe o peso bruto positivo em kg.';
  if(!prNumOk(d.tara)||prNum(d.tara)<0)errs.tara='Informe a tara em kg (zero ou mais).';
  if(!errs.bruto&&!errs.tara&&prCmp(prNum(d.bruto),prNum(d.tara))<=0)errs.tara='A tara deve ser menor que o bruto.';
  const lotes=JSON.parse(d._lotes||'[]');let kgs=null;
  if(lotes.length>1){kgs={};lotes.forEach((l,i)=>{const k='kg_'+i;if(!prNumOk(d[k])||prNum(d[k])<0)errs[k]='Informe kg válidos (zero ou mais).';kgs[l]=d[k];});
   if(!Object.keys(errs).length&&prCmp(prSoma(Object.values(kgs).map(prNum)),prSub(prNum(d.bruto),prNum(d.tara)))!==0)errs.bruto='A soma dos lotes deve ser igual ao líquido (bruto − tara).';}
  self.loPendente={rm:d._rm,ref:d._ref,bruto:d.bruto,tara:d.tara,kgs,chave:d._chave};return errs;};
 self.g2persist=gid=>{if(gid!=='g_ps')return null;const k=self.loPendente;if(!k)return 'Reabra a pesagem.';
  const r=cenMudar(self,c=>{const atual=(comP(c).expedicoes||{})[k.rm];if(!atual)throw Error('Carga não encontrada. Abra Expedição.');
   if(!atual.saida&&loRef(atual)!==k.ref)throw Error('A carga mudou. Reabra a pesagem para conferir os dados atuais.');
   return comSair(c,Object.assign({},k,{ator:g2perfil()}));},{estrito:true});return r.erro||null;};
}

