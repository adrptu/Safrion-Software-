function supMovLotes(){const c=cenGet();return Object.keys(c.lotes).map(key=>({key,l:c.lotes[key],label:c.lotes[key].prod+' · '+c.lotes[key].lote+' · '+c.lotes[key].local}));}
function supMovLote(label){const x=supMovLotes().find(x=>x.label===label);if(!x)throw Error('Lote indisponível; reabra o formulário.');return x;}
const SUP_MOV_TIPOS={ajuste:"Ajuste de estoque",entrega:"Entrega à custódia",devolucao:"Devolução recebida",reserva:"Reserva",consumo:"Consumo",contagem:"Contagem",recebimento:"Recebimento",inspecao:"Liberação de quarentena","recebimento-nf":"Entrada por compra","inspecao-reprovada":"Quarentena reprovada"};
function supMovLocal(c,m){const l=Object.values(c.lotes).find(l=>l.prod===m.prod&&l.lote===m.lote);return l?l.local:"Local não informado no recibo";}
function supMovRows(){const c=cenGet();const rows=(c.movs||[]).map(m=>({id:m.id,v:{doc:m.id,dh:m.at||'—',mov:SUP_MOV_TIPOS[m.tipo]||m.tipo,it:[m.prod,m.lote].filter(Boolean).join(' · ')||'Consulte a origem',q:m.qtd||0,un:m.un||'',od:m.tipo==='ajuste'?supMovLocal(c,m)+' → ajuste':m.req||m.os||m.doc||supMovLocal(c,m),mot:m.motivo||m.rev||'',st:'Registrado',req:m.req,os:m.os},s:{},p:{},o:[{t:'Recibo canônico · '+(m.quem||'autor não informado')},{t:'Abrir Estoque',h:'EST.dc.html'}]}));
 (c.ajustes||[]).filter(a=>a.tipo==='perda').forEach(a=>{const l=c.lotes[a.key]||{};rows.push({id:a.id,v:{doc:a.id,dh:a.em0,mov:'Perda por ajuste',it:a.prod+' · '+a.lote,q:-a.dif,un:a.un,od:(l.local||'Local indisponível')+' → perda',mot:a.motivo,st:a.estado},s:{},p:{},o:[{t:a.motivo},{t:'Registrada por '+a.reg},{t:a.estado==='Aguardando gestor'?'Revise e aprove a perda aqui na SU-08 (AL-09).':'Saldo aprovado disponível no Estoque.'}]});});return rows.reverse().concat((SUP_MOV_HIST||[]).map(r=>({id:'hist:'+r.id,ro:true,v:Object.assign({},r.v,{st:'Histórico (exemplo)'}),p:{},s:{},o:[{t:'Histórico de demonstração, somente leitura; não compõe saldos ou movimentos canônicos.'}]})));}
function supMovRefresh(self){const rows=RW(self,'g_mov');rows.splice(0,rows.length,...supMovRows());}
function supMovCommit(self,fn){const r=cenMudar(self,fn,{estrito:true});if(r.erro)throw Error(r.erro);return r.msg;}
function supMovPerda(self,d){const x=supMovLote(d.it),q=g2num(d.q),key=self.state.supMovChave;
 if(!key)throw Error('Reabra o formulário para identificar o registro.');
 const motivo=String(d.causa||'').trim(),ev=String(d.ev||'').trim();if(!ev)throw Error('Informe a evidência.');
 return supMovCommit(self,c=>cenIdem(c,key,JSON.stringify([x.key,q,motivo,ev]),'Perda',()=>{const r=cenPerdaNova(c,x.key,q,motivo,g2perfil());c.ajustes.find(a=>a.id===r.id).evidencia=ev;return r;}));}
function supMovPrevia(self,d,tipo){const q=g2num(d.q);if(tipo==='transferência'){const x=supMovLote(d.it);if(!(q>0&&Number.isFinite(q)))throw Error('Informe quantidade positiva.');if(d.d===x.l.local)throw Error('O destino precisa ser diferente da origem.');return 'Prévia: '+q+' '+x.l.un+' de '+x.label+' → '+d.d+' · '+d.mot+'. Registro pendente de comando de transferência; nenhum saldo alterado.';}
 return 'Prévia de estorno de '+d.orig+' · '+d.mot+'. Estorno genérico indisponível: nenhum movimento ou vínculo criado. Entregas são conferidas no Estoque e na O.S.';}
RUN.per=supMovPerda;RUN.trf=(s,d)=>supMovPrevia(s,d,'transferência');RUN.est=(s,d)=>supMovPrevia(s,d,'estorno');
LINES.per=LINES.trf=(self,d)=>{try{const x=supMovLote(d.it);return [['Origem',x.l.local],['Unidade',x.l.un],['Físico',cenNum(x.l.fisico)+' '+x.l.un],['Reservado',cenNum(x.l.reservado)+' '+x.l.un],['Efeito',self.state.pn==='per'?'Submeter ajuste; saldo só muda após aprovação AL-09.':'Somente prévia; não registra transferência.']];}catch(e){return [['Lote',e.message]];}};
function PREVALS(self,v){supMovRefresh(self);RW(self,'g_mov').forEach(r=>{const a=r.v;r.p.doc=[B(a.doc),BRK,M(a.dh)];r.s.doc=a.doc+' '+a.dh;r.p.mov=[T(a.mov),BRK,M(a.mot)];r.s.mov=a.mov+' '+a.mot;r.p.q=[T(cenNum(a.q)+' '+a.un)];r.p.od=[T(a.od)];r.p.est=[chipc(a.st,a.st==='Aguardando gestor'?'yellow':'gray')];r.s.est=a.st;
 if(a.st==='Aguardando gestor')r.p.est.push(BRK,{k:'act',t:'Revisar perda',fn:'apr:'+r.id});});}
function EXTRAVALS(self,v){pnVals(self,v);cenOuvir(self);
 const open=id=>{const lots=supMovLotes();if(id!=='est'&&!lots.length){toast(self,'Nenhum lote disponível no Estoque.');return;}
 if(id==='per'||id==='trf'){PN[id].fields.find(f=>f.k==='it').opts=lots.map(x=>x.label);PN[id].fields.find(f=>f.k==='it').def=lots[0].label;}
 if(id==='est'){const opts=(cenGet().movs||[]).map(x=>x.id);if(!opts.length){toast(self,'Nenhum movimento para conferir no Estoque.');return;}PN.est.fields[0].opts=opts;PN.est.fields[0].def=opts[0];}
 pnOpen(self,id);self.setState({supMovChave:'su08:'+Date.now()+':'+Math.random().toString(36).slice(2)});};
 v.open_per=()=>open('per');v.open_trf=()=>open('trf');v.open_est=()=>open('est');
 v.apr=id=>{const a=(cenGet().ajustes||[]).find(x=>x.id===id);if(!a)return;pnOpen(self,'aprovar',{id});};
 v.conf=()=>toast(self,'Transferência ainda sem comando canônico: nenhum saldo foi alterado.');
 const ok=v.pn_ok;v.pn_ok=()=>{try{ok();}catch(e){self.setState({pe:{causa:e.message,mot:e.message,id:e.message},g2toast:'Não concluído: '+e.message});}};
 const pend=(cenGet().ajustes||[]).filter(a=>a.tipo==='perda'&&a.estado==='Aguardando gestor');
 v.k_tr='—';v.k_tr_s='Transferência disponível somente como prévia';v.k_pe=String(pend.length);v.k_pe_s=pend.map(a=>a.id).join(' · ')||'Nenhuma perda aguardando';v.k_es='—';v.k_es_s='Estorno genérico disponível somente como prévia';hstatus(v,pend.length?pend.length+(pend.length===1?' perda aguardando gestor':' perdas aguardando gestor'):'Sem perda pendente',pend.length?'yellow':'gray');}
LINES.aprovar=(s,d)=>{const a=(cenGet().ajustes||[]).find(x=>x.id===d.id);return a?[['Lote',a.prod+' · '+a.lote],['Perda',cenNum(-a.dif)+' '+a.un],['Motivo',a.motivo],['Evidência',a.evidencia||'Não informada'],['Aprovação','Alçada AL-09; revalida saldo e reservas.']]:[['Estado','Ajuste indisponível']];};
RUN.aprovar=(self,d)=>supMovCommit(self,c=>cenAprovarAjuste(c,d.id,true,g2perfil()));
