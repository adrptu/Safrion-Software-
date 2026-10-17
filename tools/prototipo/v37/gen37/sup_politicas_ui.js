function supPolCurrent(){return supPolRead(localStorage,SUP_POL_SEED);}
function supPolCommit(n,expected){return supPolWrite(localStorage,SUP_POL_SEED,n,expected);}
function supPolRefresh(self){let state;try{state=supPolCurrent();}catch(e){RW(self,'g_pol').forEach(r=>{r.ro=true;r.p.estado=[M(e.message)];});return null;}
 RW(self,'g_pol').forEach(r=>{const p=state.politicas[r.id];if(!p)return;r.ro=false;r.v=Object.assign({},p.proposta?p.proposta.dados:p.vigente,{_rev:state.rev,estado:p.proposta?p.proposta.estado+' r'+p.proposta.rev+' · vigente v'+p.versao:p.vigente.estado});
 r.o=[{t:'Vigente v'+p.versao+': segurança '+p.vigente.seg+' dias; prazo '+p.vigente.prazo+' dias; limite R$ '+nf(p.vigente.lim)},
 {t:p.proposta?'Proposta r'+p.proposta.rev+': '+p.proposta.dados.just:'Nenhuma proposta pendente.'}].concat(p.recibos.map(x=>({t:'Recibo '+x.id+' · v'+x.versao+' · publicado por '+x.por})),(p.excecoes||[]).map(x=>({t:'Exceção submetida · '+x.alteracao+' · '+x.inicio+' a '+x.fim+' · '+x.just})));});return state;}
function supPolActions(self,state){if(!state)return;RW(self,'g_pol').forEach(r=>{const p=state.politicas[r.id],q=p&&p.proposta;if(q)r.p.estado.push({k:'act',t:q.estado==='Aprovada'?'Publicar versão aprovada':'Revisar proposta',fn:(q.estado==='Aprovada'?'pol_publicar:':'pol_aprovar:')+r.id,sec:true});});}
function supPolBind(self,v){
 v.pol_aprovar=id=>{const p=supPolCurrent().politicas[id];if(!p||!p.proposta)return;pnOpen(self,'aprovar',{id,rev:p.proposta.rev});};
 v.pol_publicar=id=>{const p=supPolCurrent().politicas[id];if(!p||!p.proposta)return;pnOpen(self,'publicar',{id,rev:p.proposta.rev});};
 v.sim_sim=()=>pnOpen(self,'simular');v.sim_pub=()=>toast(self,'Abra a política e publique a proposta aprovada na própria linha.');
 const ok=v.pn_ok;v.pn_ok=()=>{try{ok();}catch(e){self.setState({pe:{id:e.message,just:e.message},g2toast:'Não concluído: '+e.message});}};
 self.g2check=(gid,rows,r,d)=>{if(gid!=='g_pol')return {};try{const s=supPolCurrent(),fm=g2st(self,gid).fm;if(!fm||Number(fm.orig._rev)!==s.rev)throw Error('Versão alterada; reabra a proposta.');supPolValida(Object.assign({},r.v,d,{seg:g2num(d.seg),prazo:g2num(d.prazo),lim:g2num(d.lim)}));return {};}catch(e){return {just:e.message};}};
 self.g2after=(gid,rows,r)=>{if(gid!=='g_pol'||!r)return;self._supPolPending=null;self._supPolError=null;try{const s=supPolCurrent();self._supPolPending={next:supPolPropor(s,r.id,r.v,r.v._rev),rev:s.rev};}catch(e){self._supPolError=e.message;}};
 self.g2persist=gid=>{if(gid!=='g_pol')return null;if(self._supPolError)return self._supPolError;const p=self._supPolPending;if(!p)return 'Proposta não preparada.';try{supPolCommit(p.next,p.rev);self._supPolPending=null;self.setState({g2toast:'Proposta salva; a política vigente foi preservada.'});return null;}catch(e){return e.message;}};
}
LINES.aprovar=LINES.publicar=(self,d)=>{const p=supPolCurrent().politicas[d.id],q=p&&p.proposta;return p?[['Política',p.vigente.grp],['Vigente','v'+p.versao+' · segurança '+p.vigente.seg+' d · prazo '+p.vigente.prazo+' d'],['Proposta',q?'r'+q.rev+' · segurança '+q.dados.seg+' d · prazo '+q.dados.prazo+' d':'Indisponível'],['Justificativa',q?q.dados.just:'—']]:[];};
RUN.aprovar=(self,d)=>{const s=supPolCurrent(),n=supPolAprovar(s,d.id,Number(d.rev),g2perfil());supPolCommit(n,s.rev);return 'Proposta aprovada; publique a versão na linha para alterar a vigência.';};
RUN.publicar=(self,d)=>{const s=supPolCurrent(),r=supPolPublicar(s,d.id,Number(d.rev),g2perfil());if(!r.repetido)supPolCommit(r.state,s.rev);return 'Publicação confirmada · recibo '+r.recibo.id+' · vigente v'+r.recibo.versao;};
RUN.simular=(self,d)=>{const s=supPolCurrent(),id=Object.keys(s.politicas).find(k=>s.politicas[k].vigente.grp===d.id),x=supPolSimular(s,id);return x.origem+': '+x.prazo+' dias de prazo + '+x.seg+' dias de segurança = '+x.totalDias+' dias de antecedência. Sem previsão de consumo, não estima ruptura; vigente preservada.';};
