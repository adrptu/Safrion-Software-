const CA_DECISOES={'Conferir dia':'conferir','Registrar divergência':'divergencia','Vincular evidência':'vincular','Arquivar caso substituído':'arquivar'};
function caFila(){const c=cenGet(),out=[];Object.values(c.ordens||{}).forEach(o=>(o.ap||[]).filter(a=>a.st!=='Previsto').forEach(a=>{
 const r=a.conferenciaDia,caso=r&&r.caso,resolver=!!r&&r.estado==='Não conforme',imp=cdImpedimento(c,o.id,a.dia);
 const estado=imp||((r&&r.fato!==cdFato(c,o.id,a.dia))?'Dados alterados · revisar':r?r.estado:a.st);
 const decisao=resolver?(a.st===CEN_AP_DESC?'Arquivar caso substituído':'Vincular evidência'):'Conferir dia';
 out.push({id:o.id+':'+a.dia,ro:!!imp,v:{ap:o.id+' · dia '+a.dia+' · '+a.d,os:o.id,dia:a.dia,eq:a.quem||o.resp||'Responsável não informado',real:a.ha,horas:a.h,cons:Object.entries(a.cons||{}).map(([p,q])=>p+': '+q+' '+(((o.ins||[]).find(x=>x.p===p)||{}).un||'unidade não informada')).join(' · ')||'Sem consumo informado',orig:(a.origem||'web')+' · '+(a.sinc===false?'aguarda envio':'sincronizado'),cf:estado,motivo:'',decisao,referencia:resolver?cdCasoReferencia(c,o.id,a.dia):cdReferencia(c,o.id,a.dia)},s:{},p:{},o:[{t:'Conferir não altera a fase, a área executada, as horas ou o consumo.'},{t:r?'Última decisão: '+r.estado+' · '+r.por+' · '+r.motivo:'Sem recibo de conferência diária.'},{t:caso?'Caso '+caso.id+' · '+caso.estado:'Correção de quantidade ainda não disponível; registre divergência se o fato precisar de ajuste.'},{t:'Abrir O.S.',h:'OS.dc.html#'+o.id}]});}));return out;}
function caRefresh(self){const sp=GRIDS.find(g=>g.id==='g_fila'),rows=g2rows(self,sp);rows.splice(0,rows.length,...caFila());}
function PREVALS(self,v){caRefresh(self);}
function EXTRAVALS(self,v){cenOuvir(self);
 self.g2openDraft=(gid,r,d)=>gid==='g_fila'?Object.assign({},d,{referencia:r.v.referencia,os:r.v.os,dia:r.v.dia}):d;
 self.g2check=(gid,rows,r,d)=>{if(gid!=='g_fila')return {};self.caReferencia=d.referencia;const a=CA_DECISOES[d.decisao];if(!a)return {decisao:'Escolha uma decisão.'};if(a!=='conferir'&&!String(d.motivo||'').trim())return {motivo:'Informe o motivo e a evidência pertinente.'};return {};};
 self.g2after=(gid,rows,r)=>{if(gid!=='g_fila'||!r)return;self.caPendente=Object.assign({},r.v,{referencia:self.caReferencia});};
 self.g2persist=gid=>{if(gid!=='g_fila')return null;const d=self.caPendente;self.caPendente=null;if(!d)return 'Reabra o apontamento.';
 const decisao=CA_DECISOES[d.decisao];const r=cenMudar(self,c=>['conferir','divergencia'].includes(decisao)?cdConferir(c,d.os,Number(d.dia),decisao,d.motivo,d.referencia,g2perfil()):cdResolverRelato(c,d.os,Number(d.dia),decisao,d.motivo,d.referencia,g2perfil()),{estrito:true});return r.erro||null;};
 v.ca_revisar=id=>{const sp=GRIDS.find(g=>g.id==='g_fila');g2open(self,sp,id);};
 v.ca_proximo=()=>{const r=caFila().find(r=>!r.ro&&!['Conferido'].includes(r.v.cf));if(r)v.ca_revisar(r.id);else self.setState({g2toast:'Nenhum apontamento disponível para revisão.'});};
 v.ca_pendentes=String(caFila().filter(r=>!r.ro&&r.v.cf!=='Conferido').length);
}
