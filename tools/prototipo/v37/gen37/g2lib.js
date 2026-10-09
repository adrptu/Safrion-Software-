// ===== G2 · grade interativa, formulário lateral e navegação (motor do protótipo v3.7) =====
const G2C={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],blue:['#1E5F8F','#E3F0FB'],orange:['#9A3F00','#FFE8D6']};
// a não quebra de linha das ações da célula vem da classe g2cta (engine): numa tabela com a 1ª coluna limitada (celular) elas quebram
const G2CTA='display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;cursor:pointer;font-family:inherit;line-height:1.25;';
const G2CTAU='display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;background:#FFFFFF;color:#B42318;border:1px solid #B42318;cursor:pointer;font-family:inherit;line-height:1.25;';
function g2num(s){ if(typeof s==='number') return s; if(s===null||s===undefined) return NaN; let t=String(s).trim(); if(!t) return NaN; t=t.replace(/[^0-9,.\-]/g,''); if(t.indexOf(',')>=0){ t=t.replace(/\./g,'').replace(',','.'); } else if((t.match(/\./g)||[]).length>1 || /^\-?\d{1,3}(\.\d{3})+$/.test(t)){ t=t.replace(/\./g,''); } return parseFloat(t); }
function g2fmtn(n,d,dmin){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:(dmin!==undefined?dmin:(d||0)),maximumFractionDigits:d||0}); }
// unidade junto do valor (c.un, decisão de 05/10/2026): "160 ha", "54 %", "R$ 14,49/ha"; só em texto que é um número puro
function g2unf(t,c){ const s=String(t==null?'':t).trim(); if(!c||!c.un||!/^[+−-]?[\d.]+(,\d+)?$/.test(s)) return String(t==null?'':t);
  const u=c.un; if(u.indexOf('R$')===0){ const neg=/^[−-]/.test(s); return (neg?'−':'')+'R$ '+s.replace(/^[+−-]/,'')+u.slice(2); } return s+' '+u; }
function g2fmt(v,c){ if(v===null||v===undefined||v==='') return '—'; if(c&&c.t==='date'&&/^\d{4}-\d{2}-\d{2}$/.test(String(v))){ const a=String(v).split('-'); return a[2]+'/'+a[1]+'/'+a[0]; } if(c&&c.zdash&&Number(v)===0) return '—'; if(c&&c.t==='num'){ const n=Number(v); if(isNaN(n)) return String(v); const t=(c.pre||'')+g2fmtn(n,c.d,c.dmin)+(c.u?' '+c.u:''); return c.un?g2unf(t,c):t; } return String(v); }
function g2st(self,id){ return ((self.state.g2||{})[id])||{}; }
function g2set(self,id,patch){ const all=Object.assign({},self.state.g2||{}); all[id]=Object.assign({},all[id]||{},patch); self.setState({g2:all});
  if(G2KEEP[id]){ try{ const x=all[id]; sessionStorage.setItem(G2KEEP[id],JSON.stringify({f:x.f||{},q:x.q||'',so:x.so||null,qv:x.qv||''})); }catch(e){} } }
// recorte guardado na sessão (TABELAS-FOCO): filtros, busca e ordenação sobrevivem a abrir o detalhe e voltar; só a tabela que pede (g2keep)
const G2KEEP={};
function g2keep(self,id){ let key='g2:'+id; try{ key='g2:'+String(location.pathname).split('/').pop()+':'+id; }catch(e){} G2KEEP[id]=key;
  if(self.__g2kept&&self.__g2kept[id]) return; (self.__g2kept=self.__g2kept||{})[id]=1;
  try{ const o=JSON.parse(sessionStorage.getItem(key)||'null'); if(o&&typeof o==='object'){ const all=Object.assign({},self.state.g2||{}); all[id]=Object.assign({},all[id]||{},{f:o.f||{},q:o.q||'',so:o.so||null,qv:o.qv||''}); self.state.g2=all; } }catch(e){} }
function g2rows(self,sp){ const st=g2st(self,sp.id); return st.rows||sp.rows; }
function g2find(list,id){ for(const r of list){ if(r.id===id) return r; if(r.kids){ const k=g2find(r.kids,id); if(k) return k; } } return null; }
function g2text(r,c){ if(r.s&&r.s[c.k]!==undefined&&r.s[c.k]!==null) return (c&&c.un)?g2unf(r.s[c.k],c):String(r.s[c.k]); if(r.v&&r.v[c.k]!==undefined&&r.v[c.k]!==null) return g2fmt(r.v[c.k],c); return ''; }
// coluna multivalorada (c.multi, TABELAS-FOCO): a linha traz r.m[k]=[{id,l}] (vínculos estruturados, ex.: talhões); filtro por pertinência
// do ID, nunca por texto (T1 não pega T10 nem T1-A); vazio é um valor próprio do filtro, nos dois sentidos
function g2mem(r,c){ return (c.multi&&r.m&&r.m[c.k])||null; }
function g2fkeys(r,c){ const m=g2mem(r,c); if(m) return m.length?m.map(x=>x.id):['(vazio)']; const t=g2text(r,c); return [(t===''||t==='—')?'(vazio)':t]; }
function g2key(r,c){ if(c.t==='date'){ const d=r.v&&r.v[c.k]; return (d===undefined||d===null||d==='')?null:String(d); }   // ISO: ordena por data
  if(c.t==='num'){ let n=(r.v&&r.v[c.k]!==undefined&&r.v[c.k]!==null&&r.v[c.k]!=='')?Number(r.v[c.k]):g2num(r.s&&r.s[c.k]); return isNaN(n)?null:n; } const t=g2text(r,c); return (t===''||t==='—')?null:t; }
function g2match(r,sp,st,mask,added){
  if(r.sh && !(added||{})[r.sh]) return false;
  if(mask && r.ri!==undefined && mask[r.ri]===false) return false;
  const q=(st.q||'').trim().toLowerCase();
  if(q){ const all=sp.cols.map(c=>g2text(r,c)).join(' ').toLowerCase(); if(all.indexOf(q)<0) return false; }
  const f=st.f||{}; for(const k in f){ const vals=f[k]; if(!vals||!vals.length) continue; const c=sp.cols.find(x=>x.k===k); if(!c) continue; if(!g2fkeys(r,c).some(x=>vals.indexOf(x)>=0)) return false; }
  return true; }
function g2sort(arr,sp,st){ const so=st.so||sp.so; if(!so||!so.k) return arr; const c=sp.cols.find(x=>x.k===so.k); if(!c) return arr; const d=so.d?-1:1;
  return arr.slice().sort((a,b)=>{ const x=g2key(a,c), y=g2key(b,c); if(x===null&&y===null) return 0; if(x===null) return 1; if(y===null) return -1;
    if(typeof x==='number'&&typeof y==='number') return (x-y)*d; return String(x).localeCompare(String(y),'pt-BR',{numeric:true,sensitivity:'base'})*d; }); }
function g2filtering(st){ return !!((st.q||'').trim()) || Object.keys(st.f||{}).some(k=>(st.f[k]||[]).length); }
// ---------- filtro rápido: chips "Todas N · valor n" sobre uma coluna; vale no 1º nível (em árvore, o grupo fica se ele ou um filho tiver o valor) ----------
function g2qtok(r,c,qf){ let t=g2text(r,c); if(!t||t==='—') return []; if(qf.cut) t=t.split(qf.cut)[0]; if(qf.num) t=t.replace(/\s+\d.*$/,''); return (qf.sep?t.split(qf.sep):[t]).map(x=>x.trim()).filter(x=>x&&x!=='—'); }
function g2qhas(r,c,qf,val){ return g2qtok(r,c,qf).indexOf(val)>=0 || (!qf.nivel0&&(r.kids||[]).some(k=>g2qhas(k,c,qf,val))); }
function g2qrows(sp,st,rows){ if(!sp.qf||!st.qv) return rows; const c=sp.cols.find(x=>x.k===sp.qf.k); if(!c) return rows; return rows.filter(r=>g2qhas(r,c,sp.qf,st.qv)); }   // vazio continua vazio (TABELAS-FOCO)
// os chips contam só as linhas que os outros filtros da tela deixam ver (r.sh)
function g2qvals(self,sp,v,st,rows0,added){ const id=sp.id, qf=sp.qf; const rows=rows0.filter(r=>!(r.sh&&!(added||{})[r.sh])); v[id+'_hasqf']=false; v[id+'_qf']=[]; v[id+'_qfl']=''; if(!qf) return; const c=sp.cols.find(x=>x.k===qf.k); if(!c) return;
  const cnt={}; const tok=(r)=>{ const s=new Set(g2qtok(r,c,qf)); if(!qf.nivel0) (r.kids||[]).forEach(k=>tok(k).forEach(x=>s.add(x))); return s; };
  rows.forEach(r=>tok(r).forEach(x=>{ cnt[x]=(cnt[x]||0)+1; }));
  const cur=st.qv||''; if(cur&&!(cur in cnt)) cnt[cur]=0;   // escolha sem linhas continua à vista (com 0) para poder ser limpa
  let ks=Object.keys(cnt).sort((a,b)=>(cnt[b]-cnt[a])||a.localeCompare(b,'pt-BR',{numeric:true}));
  if(ks.length<2&&!cur) return; const MAX=10; if(ks.length>MAX){ const top=ks.slice(0,MAX); if(cur&&top.indexOf(cur)<0) top[MAX-1]=cur; ks=top; }
  const ST='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
  const ch=(t,n,on,go,lab)=>({t,n:String(n),on:String(!!on),go,lab,st:ST+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  v[id+'_qf']=[ch(qf.todas||'Todas',rows.length,!cur,()=>g2set(self,id,{qv:''}),'Mostrar todas as linhas')].concat(ks.map(k=>ch(k,cnt[k],cur===k,()=>g2set(self,id,{qv:cur===k?'':k}),cur===k?'Mostrar todas as linhas':('Mostrar só '+k))));
  v[id+'_qfl']='Filtro rápido por '+String(qf.l||c.l).toLowerCase(); v[id+'_hasqf']=true; }
// ---------- autocompletar do cadastro: busca sem acento e sem caixa no nome e no complemento; ↑↓ escolhem, Enter confirma, Esc fecha ----------
function g2norm(s){ return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(); }
// itens: [{v,t,sub}]; chave: identifica o campo (um aberto por vez); escolhido: valor atual; pick(v): grava a escolha ('' limpa)
function g2ac(self,chave,itens,escolhido,pick,o){ o=o||{}; const ac=self.state.g2ac||{}; const meu=ac.k===chave; const sel=itens.find(x=>x.v===escolhido);
  const q=meu?(ac.q||''):(sel?sel.t:''); const ws=g2norm(q).split(/\s+/).filter(Boolean); const aberto=meu&&!!ac.open;
  let res=[]; if(aberto){ res=itens.filter(x=>{ const t=g2norm(x.t+' '+(x.sub||'')); return ws.every(w=>t.indexOf(w)>=0); });
    const ini=(x)=>(ws.length&&g2norm(x.t).indexOf(ws[0])===0)?0:1; res.sort((a,b)=>(ini(a)-ini(b))||a.t.localeCompare(b.t,'pt-BR')); res=res.slice(0,o.max||8); }
  const i=Math.min(Math.max(meu?(ac.i||0):0,0),Math.max(res.length-1,0)); const id=('ac-'+chave).replace(/[^A-Za-z0-9_-]/g,'_');
  const escolher=(x)=>{ self.setState({g2ac:{k:chave,q:x.t,open:false,i:0}}); pick(x.v); };
  const err=!!o.err;
  return {acId:id+'-in', acLid:id+'-lista', acQ:q, acPh:o.ph||'Buscar no cadastro', acAberto:aberto&&res.length>0, acVazio:aberto&&ws.length>0&&!res.length,
    acVazioT:'Nenhum item com “'+q+'” no cadastro.', acExp:String(aberto&&res.length>0), acAtivo:(aberto&&res.length)?(id+'-o'+i):'',
    acSt:'font-family:inherit;font-size:13px;padding:7px 10px;border-radius:9px;box-sizing:border-box;width:100%;background:#fff;color:#15201A;border:1px solid '+(err?'#B42318':'#E4E9E5')+';',
    acItens:res.map((x,j)=>({t:x.t, sub:x.sub||'', id:id+'-o'+j, on:String(j===i), segura:(e)=>e.preventDefault(), pick:()=>escolher(x),
      st:'display:flex;flex-direction:column;align-items:flex-start;gap:1px;width:100%;text-align:left;padding:7px 10px;border:0;border-radius:8px;cursor:pointer;font-family:inherit;font-size:13px;color:#15201A;background:'+(j===i?'#E4F3E9':'transparent')+';'})),
    acSet:(e)=>{ self.setState({g2ac:{k:chave,q:e.target.value,open:true,i:0}}); if(escolhido) pick(''); },
    acFoco:()=>{ const cur=self.state.g2ac||{}; if(cur.k!==chave||!cur.open) self.setState({g2ac:{k:chave,q:q,open:true,i:0}}); },
    acSai:()=>{ setTimeout(()=>{ const cur=self.state.g2ac||{}; if(cur.k===chave&&cur.open) self.setState({g2ac:Object.assign({},cur,{open:false})}); },150); },
    acTecla:(e)=>{ if(e.key==='ArrowDown'||e.key==='ArrowUp'){ e.preventDefault(); if(!aberto){ self.setState({g2ac:{k:chave,q:q,open:true,i:0}}); return; } if(!res.length) return;
        const n=(i+(e.key==='ArrowDown'?1:-1)+res.length)%res.length; self.setState({g2ac:{k:chave,q:q,open:true,i:n}}); }
      else if(e.key==='Enter'){ if(aberto&&res.length){ e.preventDefault(); e.stopPropagation(); escolher(res[i]); } else if(o.enter){ e.preventDefault(); o.enter(); } }
      else if(e.key==='Escape'){ if(aberto){ e.preventDefault(); e.stopPropagation(); self.setState({g2ac:Object.assign({},ac,{open:false})}); } else if(o.esc){ e.preventDefault(); o.esc(); } } } }; }
function g2flat(sp,st,rows,mask,added){
  const out=[]; const exp=st.x||sp.x0||{}; const filt=g2filtering(st);
  const deep=(r)=>g2match(r,sp,st,mask,added)||(r.kids||[]).some(deep);
  const walk=(list,lvl,parentOk)=>{ g2sort(list,sp,st).forEach(r=>{ const kids=r.kids||[]; const selfOk=g2match(r,sp,st,mask,added);
      const anyKid=kids.some(deep); if(!(selfOk||anyKid||parentOk)) return;
      out.push({r,lvl,has:kids.length>0});
      if(kids.length && (exp[r.id] || (filt && anyKid && !selfOk))) walk(kids,lvl+1,selfOk&&!filt); }); };
  walk(rows,0,false); return out; }
function g2part(p,v){ const o={isCn:false,isTxt:false,isB:false,isMut:false,isChip:false,isTag:false,isLink:false,isCta:false,isAct:false,isBr:false,t:p.t||'',st:'',cls:'',dot:'',href:p.h||'#',fn:null,title:p.t||'',dica:'',hasDica:false};
  switch(p.k){ case 'b': o.isB=true; break; case 'mut': o.isMut=true; break;
    case 'chip': { const cc=G2C[p.c]||G2C.gray; o.isChip=true; o.dica=p.dica||''; o.hasDica=!!p.dica; o.st='display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; o.dot='width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'; break; }
    case 'cn': { const cc=G2C[p.c]||G2C.gray; o.isCn=true; o.st='font-weight:800;white-space:nowrap;color:'+cc[0]+';'; break; }
    case 'tag': o.isTag=true; break; case 'link': o.isLink=true; break;
    case 'cta': o.isCta=true; o.cls='g2cta'; o.st=p.u?G2CTAU:G2CTA; break;
    case 'act': o.isAct=true; o.al=p.al||p.t; if(p.lk) { o.lk=true; } if(p.fn&&p.fn.indexOf(':')>0){ const nm=p.fn.split(':')[0], ar=p.fn.slice(nm.length+1); o.fn=()=>{ if(v&&v[nm]) v[nm](ar); }; } else o.fn=(v&&p.fn&&v[p.fn])||(()=>{}); o.cls=p.lk?'':'g2cta'; o.st=p.lk?'border:0;background:transparent;padding:0;color:#1E7A4C;font-weight:700;cursor:pointer;font-family:inherit;font-size:13px;text-decoration:underline;text-underline-offset:3px;text-align:left;':(p.u?G2CTAU:G2CTA);
      // célula inteira tocável (DS: alvo ≥ 44 px): texto da célula, sem negrito, na cor do estado; aria-pressed quando é o filtro ativo
      if(p.full){ o.cls='g2full'; o.st='width:100%;min-height:44px;border:0;background:'+(p.on?'#E4F3E9':'transparent')+';padding:0 6px;cursor:pointer;font-family:inherit;font-size:13px;font-weight:'+(p.on?'700':'400')+';text-align:right;font-variant-numeric:tabular-nums;color:'+((G2C[p.c]||[])[0]||'#15201A')+';'+(p.on?'outline:2px solid #1E7A4C;outline-offset:-2px;border-radius:6px;':''); } break;
    case 'br': o.isBr=true; break; default: o.isTxt=true; }
  return o; }
function g2sum(sp,flat,c){ let s=0,n=0; flat.forEach(x=>{ if(x.lvl!==0) return; const k=g2key(x.r,c); if(typeof k==='number'){ s+=k; n++; } }); return n? (c.agg==='avg'? s/n : s) : null; }
// condição de campo do formulário: {k, eq} (igual) ou {k, ne} (diferente)
function g2cond(f,d){ if(!f.cond) return true; const um=(c)=>{ const v=String((d||{})[c.k]===undefined?'':d[c.k]); return (c.ne!==undefined)?v!==String(c.ne):v===String(c.eq); };
  return Array.isArray(f.cond)?f.cond.every(um):um(f.cond); }   // lista = todas valem
// linhas de exibição (etapa 2 do Planejar safra): a tela monta, a cada desenho, uma cópia com linhas que não são registro (talhão, ocupação
// de fora); a grade mostra a cópia e os gravadores continuam no estado (g2rows). Sem cópia, mostra o estado.
const G2DISP={};
function g2disp(self,sp){ return G2DISP[sp.id]||g2rows(self,sp); }
function g2open(self,sp,rid,e){
  if(e&&e.target&&e.target.closest&&e.target.closest('a,button,input,select,textarea,label,[data-noedit],.g2nr')) return;
  const ed=sp.edit||{m:'none'}; if(ed.m==='none') return;
  const r=g2find(g2disp(self,sp),rid)||g2find(g2rows(self,sp),rid); if(!r||r.fora) return;
  if(r.dr && self.__v && self.__v[r.dr]){ self.__v[r.dr](); return; }
  if(ed.m==='pick'){ if(self.g2pick) self.g2pick(sp.id,rid,r); g2set(self,sp.id,{fl:rid}); return; }
  const draft={}; (ed.fields||[]).forEach(f=>{ let val=''; if(r.v&&r.v[f.k]!==undefined&&r.v[f.k]!==null&&r.v[f.k]!=='') val=(f.t==='num'? String(r.v[f.k]).replace('.',','):String(r.v[f.k])); else if(r.s&&r.s[f.k]!==undefined) val=String(r.s[f.k]); draft[f.k]=val; });
  g2set(self,sp.id,{fm:{rid,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:(ed.m!=='form'||!!r.ro),isNew:false,mode:ed.m},fl:null,fmc:null}); }
function g2new(self,sp){ const ed=sp.edit||{}; const draft={}; (ed.fields||[]).forEach(f=>{ draft[f.k]=(f.def!==undefined?String(f.def):''); });
  g2set(self,sp.id,{fm:{rid:null,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:false,isNew:true,mode:'form'},fl:null,fmc:null}); }
function g2calc(r,calc){ (calc||[]).forEach(cx=>{ const a=(cx.a||[]).map(k=>Number(r.v[k])||0); let x=null;
   if(cx.op==='mul') x=a.reduce((p,q)=>p*q,1); else if(cx.op==='div') x=a[1]?a[0]/a[1]:0; else if(cx.op==='sum') x=a.reduce((p,q)=>p+q,0);
   else if(cx.op==='sub') x=a.slice(1).reduce((p,q)=>p-q,a[0]); else if(cx.op==='max0sub') x=Math.max(0,a.slice(1).reduce((p,q)=>p-q,a[0]));
   if(x!==null){ r.v[cx.k]=Math.round(x*100)/100; if(r.s) delete r.s[cx.k]; if(r.p) delete r.p[cx.k]; } }); }
function g2clone(list){ return list.map(r=>Object.assign({},r,{v:Object.assign({},r.v||{}),s:Object.assign({},r.s||{}),p:Object.assign({},r.p||{}),kids:r.kids?g2clone(r.kids):undefined})); }
function g2save(self,sp){ const st=g2st(self,sp.id); const fm=st.fm; if(!fm) return; const ed=sp.edit||{}; const errs={};
  const vis=(ed.fields||[]).filter(f=>g2cond(f,fm.draft));
  vis.forEach(f=>{ const val=(fm.draft[f.k]||'').trim(); if(f.ro||(f.newOnly&&!fm.isNew)) return;
    if(f.req && !val) { errs[f.k]='Informe '+f.l.toLowerCase().replace(/ \(.*\)$/,'')+'.'; return; }
    if(f.t==='email' && val && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val)) { errs[f.k]='E-mail inválido (ex.: compras@empresa.com.br).'; return; }
    if(f.t==='tel' && val){ const dg=val.replace(/\D/g,''); if(dg.length<10||dg.length>13) { errs[f.k]='Informe DDD e número (ex.: 65 99999-0000).'; return; } }
    if(f.t==='multi' && f.req && !val) { errs[f.k]='Escolha ao menos uma opção.'; return; }
    if(f.t==='num' && val){ const n=g2num(val); if(isNaN(n)) { errs[f.k]='Use um número (ex.: 12,5).'; return; } if(f.min!==undefined && n<f.min) { errs[f.k]='Mínimo '+g2fmtn(f.min,(String(f.min).split('.')[1]||'').length)+(f.u?' '+f.u:'')+'.'; return; } if(f.max!==undefined && n>f.max) { errs[f.k]='Máximo '+g2fmtn(f.max,(String(f.max).split('.')[1]||'').length)+(f.u?' '+f.u:'')+'.'; return; } } });
  if(!Object.keys(errs).length && self.g2check){ const cur=g2rows(self,sp); Object.assign(errs, self.g2check(sp.id,cur,fm.isNew?null:g2find(cur,fm.rid),fm.draft,fm.isNew)||{}); }
  if(Object.keys(errs).length){ g2set(self,sp.id,{fm:Object.assign({},fm,{errs,warn:false})}); return; }
  const rows=g2clone(g2rows(self,sp)); let r;
  if(fm.isNew){ r={id:'n'+(rows.length+1)+'_'+String(Date.now()).slice(-5),v:{},s:{},p:{}}; rows.push(r); } else r=g2find(rows,fm.rid);
  vis.forEach(f=>{ if(f.ro||(f.newOnly&&!fm.isNew)) return; const val=(fm.draft[f.k]||'').trim(); const col=sp.cols.find(c=>c.k===f.k);
    if(f.t==='num'){ r.v[f.k]=val===''?'':g2num(val); if(r.s) delete r.s[f.k]; if(r.p) delete r.p[f.k]; }
    else { r.v[f.k]=val; r.s[f.k]=val; if(col && col.chips && col.chips[val]) r.p[f.k]=[{k:'chip',t:val,c:col.chips[val]}]; else if(r.p) delete r.p[f.k]; } });
  g2calc(r,ed.calc);
  const patch={rows,fm:null,fl:r.id};
  g2set(self,sp.id,patch); self.setState({g2toast:(fm.isNew?'Registro incluído':'Salvo · linha e totais atualizados')});
  if(self.g2after) self.g2after(sp.id,rows,r,fm.isNew); }
function g2dirty(fm){ if(!fm) return false; for(const k in fm.draft){ if(String(fm.draft[k])!==String(fm.orig[k])) return true; } return false; }
function g2close(self,sp){ const fm=g2st(self,sp.id).fm; if(fm && !fm.ro && g2dirty(fm)) { g2set(self,sp.id,{fm:Object.assign({},fm,{warn:true})}); return; } g2set(self,sp.id,{fm:null}); }
function g2vals(self,sp,v,mask){
  const id=sp.id, st=g2st(self,id), rows=g2disp(self,sp), added=self.state.added||{};
  const flat=g2flat(sp,st,g2qrows(sp,st,rows),mask,added); const ed=sp.edit||{m:'none'}; const editable=ed.m&&ed.m!=='none';
  g2qvals(self,sp,v,st,rows,added);
  const so=st.so||sp.so||{};
  v[id+'_head']=sp.cols.map((c,ci)=>({l:c.l, tt:c.ajuda||'', un:c.un||'', cls:(ci===0?'g2c0':''), st:'display:flex;align-items:center;gap:2px;justify-content:'+(c.a==='r'?'flex-end':'flex-start')+';'+(ci===0?'position:sticky;left:0;z-index:2;background:#F4F6F3;box-shadow:1px 0 0 #E4E9E5;':''),
     arrow:(so.k===c.k?(so.d?'▼':'▲'):'⇅'), astyle:(so.k===c.k?'color:#1E7A4C;':'color:#B7C1BA;'), sortLabel:'Ordenar por '+c.l,
     sort:()=>{ const cur=g2st(self,id).so||sp.so||{}; let nx; if(cur.k!==c.k) nx={k:c.k,d:false}; else if(!cur.d) nx={k:c.k,d:true}; else nx={}; g2set(self,id,{so:nx}); },
     fil:(((st.f||{})[c.k]||[]).length?' · '+((st.f||{})[c.k]||[]).length:''), fcolor:(((st.f||{})[c.k]||[]).length?'#1E7A4C':'#8A968E'),
     fmenu:(e)=>{ const cur=g2st(self,id).fmc; if(cur===c.k){ g2set(self,id,{fmc:null}); return; }
       const el=e&&e.currentTarget; const rr=el&&el.getBoundingClientRect?el.getBoundingClientRect():{left:0,right:0,bottom:0};
       g2set(self,id,{fmc:c.k,fpos:{x:rr.left,xr:rr.right,y:rr.bottom,dir:c.a==='r'},fmd:null,fmq:''}); setTimeout(()=>{ const q=document.getElementById('g2fq_'+id); if(q) q.focus(); },0); },
     flabel:'Filtrar '+c.l}));
  // valores do filtro aberto
  const fmc=st.fmc; const fcol=sp.cols.find(c=>c.k===fmc);
  if(fcol){ const cnt={}, lab={}; const leaf=(list)=>list.forEach(r=>{ if(r.livre||r.fora) return; if(r.kids&&r.kids.length) leaf(r.kids); if(!(r.kids&&r.kids.length)||sp.tree===false||!sp.tree||(fcol.niv0&&r.tal)){
      const m=g2mem(r,fcol); g2fkeys(r,fcol).forEach(k=>{ cnt[k]=(cnt[k]||0)+1; if(!lab[k]){ const x=m&&m.find(y=>y.id===k); lab[k]=x?x.l:k; } }); } }); leaf(rows);
    const L=(k)=>lab[k]||k; const todos=Object.keys(cnt).sort((a,b)=>L(a).localeCompare(L(b),'pt-BR',{numeric:true})); const apl=(st.f||{})[fmc];
    // rascunho da seleção: abre com o filtro aplicado (ou tudo marcado); só vale no OK, como no Excel e no Google Sheets
    const sel=st.fmd?st.fmd.slice():(apl&&apl.length?apl.filter(k=>cnt[k]):todos.slice()); const q=st.fmq||''; const qn=g2norm(q);
    const vis=todos.filter(k=>!qn||g2norm(L(k)).indexOf(qn)>=0); const setd=(d)=>g2set(self,id,{fmd:d});
    const P=st.fpos||{x:0,xr:0,y:0}; const W=280, vw=(typeof window!=='undefined'?window.innerWidth:1440), vh=(typeof window!=='undefined'?window.innerHeight:900);
    let x=P.dir?(P.xr-W):P.x; x=Math.max(8,Math.min(x,vw-W-8)); const y=Math.min(P.y+4,vh-460);
    const fechar=()=>g2set(self,id,{fmc:null,fmd:null,fmq:''});
    const aplicar=()=>{ const s=(g2st(self,id).fmd)||sel; if(!s.length) return; const f=Object.assign({},g2st(self,id).f||{}); if(s.length>=todos.length) delete f[fmc]; else f[fmc]=s.slice(); g2set(self,id,{f,fmc:null,fmd:null,fmq:''}); };
    const tipo=fcol.t==='num'?'num':(fcol.t==='date'?'data':'txt');
    v[id+'_fm']={open:true, l:fcol.l, titulo:'Filtrar '+fcol.l, pos:'top:'+Math.max(8,y)+'px;left:'+x+'px;', qid:'g2fq_'+id, q,
      setq:(e)=>g2set(self,id,{fmq:e.target.value,fmd:sel}),
      vals:vis.map(k=>({t:L(k),n:cnt[k],on:sel.indexOf(k)>=0, tog:()=>{ const s=sel.slice(); const i=s.indexOf(k); if(i>=0) s.splice(i,1); else s.push(k); setd(s); }})),
      semRes:!vis.length, semMarca:!sel.length, okSt:sel.length?'':'opacity:.5;cursor:not-allowed;', conta:sel.length+' de '+todos.length+' marcados',
      todos:()=>setd([...new Set(sel.concat(vis))]), nenhum:()=>setd(sel.filter(k=>vis.indexOf(k)<0)),
      ascT:tipo==='num'?'↑ Classificar do menor para o maior':(tipo==='data'?'↑ Classificar do mais antigo para o mais recente':'↑ Classificar de A a Z'),
      descT:tipo==='num'?'↓ Classificar do maior para o menor':(tipo==='data'?'↓ Classificar do mais recente para o mais antigo':'↓ Classificar de Z a A'),
      asc:()=>g2set(self,id,{so:{k:fmc,d:false},fmc:null,fmd:null,fmq:''}), desc:()=>g2set(self,id,{so:{k:fmc,d:true},fmc:null,fmd:null,fmq:''}),
      ok:aplicar, cancel:fechar, key:(e)=>{ if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); fechar(); } else if(e.key==='Enter'&&e.target.type!=='checkbox'){ e.preventDefault(); aplicar(); } },
      clear:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[fmc]; g2set(self,id,{f,fmc:null,fmd:null,fmq:''}); }, close:fechar};
  } else v[id+'_fm']={open:false,vals:[]};
  const total=(sp.total!==false) && sp.cols.some(c=>c.agg);
  v[id+'_rows']=flat.map(({r,lvl,has})=>{
    const cells=[]; const exp=(st.x||sp.x0||{});
    // linha livre (convite para cadastrar, ex.: talhão sem cultivo): sem seleção e sem lixeira
    if(sp.sel&&(r.livre||r.fora||r.nosel)) cells.push({isSel:false,isData:false,isDel:false,st:'',cls:''}); else if(sp.sel) cells.push({isSel:true,isData:false,isDel:false,cls:'',on:!!(st.sel||{})[r.id],selLabel:'Selecionar '+g2text(r,sp.cols[0]),
      tog:()=>{ const s2=Object.assign({},g2st(self,id).sel||{}); s2[r.id]=!s2[r.id]; g2set(self,id,{sel:s2}); },st:'padding:6px 4px 6px 12px;'});
    sp.cols.forEach((c,ci)=>{
      const empty=(has && ci>0 && !(r.p&&r.p[c.k]) && (!r.v || r.v[c.k]===undefined || r.v[c.k]===''));
      const raw0=empty?[]:((r.p&&r.p[c.k]&&r.p[c.k].length)?r.p[c.k]:[{k:(ci===0&&lvl===0&&has?'b':'txt'),t:g2fmt(r.v?r.v[c.k]:'',c)}]);
      // partes próprias (p) com número puro ganham a unidade (cópia: r.p não muda)
      const raw=c.un?raw0.map(p=>(p&&typeof p.t==='string'&&['txt','b','cn','chip'].indexOf(p.k)>=0)?Object.assign({},p,{t:g2unf(p.t,c)}):p):raw0;
      const cell={isSel:false,isData:true,isDel:false,cls:(ci===0?'g2c0':'')+(c.nr?' g2nr':''),parts:raw.map(p=>g2part(p,v)),pw:'max-width:'+(c.w||340)+'px;',
        st:(c.nr?'padding:0 2px;':'padding:6px 8px;')+(c.a==='r'?'text-align:right;justify-content:flex-end;white-space:nowrap;font-variant-numeric:tabular-nums;':'')+(ci===0&&sp.tree?'padding-left:'+(8+lvl*20)+'px;':'')+(ci===0?'position:sticky;left:0;z-index:1;background:inherit;box-shadow:1px 0 0 #E4E9E5;':'')};
      if(ci===0 && sp.tree){ cell.hasCaret=true; cell.caretOk=has; cell.caretNo=!has; const open=!!exp[r.id]||(g2filtering(st)&&has);
        cell.caretSym=open?'▾':'▸'; cell.caretExp=String(open); cell.caretLabel=(open?'Recolher ':'Expandir ')+g2text(r,c);
        cell.toggle=()=>{ const x=Object.assign({},g2st(self,id).x||sp.x0||{}); x[r.id]=!x[r.id]; g2set(self,id,{x}); }; }
      else { cell.hasCaret=false; }
      cells.push(cell); });
    if(sp.del&&(r.livre||r.fora||r.nosel)) cells.push({isSel:false,isData:false,isDel:false,st:'',cls:''}); else if(sp.del){ const asking=(st.cf===r.id); cells.push({isSel:false,isData:false,isDel:true,cls:'',asking,notAsking:!asking,st:'padding:4px 10px;white-space:nowrap;',
        delLabel:'Excluir '+g2text(r,sp.cols[0]), ask:()=>g2set(self,id,{cf:r.id}), no:()=>g2set(self,id,{cf:null}),
        yes:()=>{ const rs=g2clone(g2rows(self,sp)); const rm=(list)=>{ const i=list.findIndex(x=>x.id===r.id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&rm(x.kids)); }; rm(rs); g2set(self,id,{rows:rs,cf:null}); self.setState({g2toast:'Excluído: '+g2text(r,sp.cols[0])}); if(self.g2after) self.g2after(id,rs,null); }}); }
    const canOpen=editable && !(ed.leafOnly && has) && !r.fora && !(r.nosel && !r.dr);
    return {id:r.id, cls:'g2r'+(canOpen?' g2ed':'')+(st.fl===r.id?' g2flash':'')+(lvl>0?' g2kid':''), tab:(canOpen&&!r.drDup)?'0':'-1',
      open:(e)=>{ if(canOpen) g2open(self,sp,r.id,e); }, key:(e)=>{ if(!canOpen || !e || (e.key!=='Enter'&&e.key!==' ')) return; const t=e.target; if(t&&t.closest&&t.closest('a,button,input,select,textarea,label,[data-noedit],.g2nr')) return; e.preventDefault(); g2open(self,sp,r.id,null); }, cells}; });
  v[id+'_count']=flat.filter(x=>x.lvl===0).length; v[id+'_all']=rows.length;
  v[id+'_empty']=flat.length===0; v[id+'_some']=flat.length>0;
  v[id+'_q']=st.q||''; v[id+'_setq']=(e)=>g2set(self,id,{q:e.target.value});
  v[id+'_filtered']=g2filtering(st)||!!(sp.qf&&st.qv); v[id+'_clear']=()=>g2set(self,id,{q:'',f:{},qv:''});
  v[id+'_fchips']=Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).map(k=>{ const c=sp.cols.find(x=>x.k===k)||{l:k}; return {t:c.l+': '+st.f[k].join(', '), rm:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[k]; g2set(self,id,{f}); }}; });
  v[id+'_selcount']=Object.values(st.sel||{}).filter(Boolean).length; v[id+'_hassel']=v[id+'_selcount']>0;
  // barra de seleção (DS-40 · UX-ACAO-UNICA-20261003): seleção por IDs; diz quantos estão fora da vista (filtro ou grupo recolhido),
  // sem perder nem ampliar a seleção; a prévia do comando de lote lista todos os incluídos
  { const ids=Object.keys(st.sel||{}).filter(k=>(st.sel||{})[k]); const vis=new Set(flat.map(x=>x.r.id)); const fora=ids.filter(k=>!vis.has(k)).length;
    v[id+'_selmsg']=ids.length+(ids.length>1?' selecionados':' selecionado')+(fora?' · '+fora+' fora da vista (filtro ou grupo recolhido)':'');
    // com seleção, a região de ações da barra dá lugar à do lote (o "+ Novo…" volta quando a seleção é limpa); "Selecionar todas" diz o alcance
    // só as linhas que têm caixa: linha de exibição (talhão, ocupação de fora, área livre) não é registro e não entra (R-23, revisão SAF S3.8)
    v[id+'_semsel']=!ids.length; const selv=flat.filter(x=>!(x.r.livre||x.r.fora||x.r.nosel)); const todas=selv.length>0&&selv.every(x=>(st.sel||{})[x.r.id]);
    v[id+'_selallLab']=todas?('Desmarcar as '+selv.length+' linhas visíveis'):('Selecionar as '+selv.length+' linhas visíveis (filtro e grupos recolhidos ficam de fora)'); }
  v[id+'_selclear']=()=>g2set(self,id,{sel:{}});
  v[id+'_selall']=()=>{ const s2={}; const selv=flat.filter(x=>!(x.r.livre||x.r.fora||x.r.nosel)); const allOn=selv.length>0&&selv.every(x=>(st.sel||{})[x.r.id]); if(!allOn) selv.forEach(x=>{ s2[x.r.id]=true; }); g2set(self,id,{sel:s2}); };
  v[id+'_new']=()=>g2new(self,sp);
  v[id+'_expall']=()=>{ const x={}; const w=(l)=>l.forEach(r=>{ if(r.kids&&r.kids.length){ x[r.id]=true; w(r.kids);} }); w(rows); g2set(self,id,{x}); };
  v[id+'_colall']=()=>g2set(self,id,{x:{}});
  // um só botão: "Expandir tudo" até tudo estar aberto; aí vira "Recolher tudo"
  const xids=[]; const wx=(l)=>l.forEach(r=>{ if(r.kids&&r.kids.length){ xids.push(r.id); wx(r.kids); } }); wx(rows);
  const xe=st.x||sp.x0||{}; const xtodos=xids.length>0&&xids.every(k=>xe[k]);
  v[id+'_xlab']=xtodos?'Recolher tudo':'Expandir tudo'; v[id+'_xtog']=xtodos?v[id+'_colall']:v[id+'_expall']; v[id+'_xup']=xtodos; v[id+'_xdown']=!xtodos;
  v[id+'_xhas']=rows.some(r=>(r.kids||[]).length>0);   // sem grupo na tela, sem botão de expandir
  if(total){ v[id+'_tot']=sp.cols.map((c,ci)=>{ const s=c.agg?g2sum(sp,flat,c):null; return {t:(ci===0?'Total':(s===null?'':g2fmt(s,c))), cls:(ci===0?'g2c0':''), st:'padding:8px 10px;font-weight:800;'+(ci===0?'position:sticky;left:0;z-index:1;background:#F4F6F3;':'')+(c.a==='r'?'text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;':'')}; });
    v[id+'_totopen']=()=>g2set(self,id,{fm:{tot:true,ro:true,mode:'total',draft:{},orig:{},errs:{}},fmc:null}); }
  // formulário lateral
  const fm=st.fm; const F={open:!!fm};
  if(fm){ const r=fm.rid?g2find(rows,fm.rid):null;
    F.isTot=!!fm.tot; F.isRec=!fm.tot;
    F.title=fm.title||(fm.tot?('Composição do total'):(fm.isNew?(ed.newTitle||'Novo registro'):((ed.title?ed.title+' · ':'')+(r?g2text(r,sp.cols[0]):''))));
    F.sub=fm.sub||(self.g2formSub&&!fm.tot?(self.g2formSub(id,r,fm)||''):'')||(fm.tot?'Linhas que formam o total, com os filtros atuais. Totais são calculados: altere os registros de origem.':(fm.ro?(fm.mode==='origin'?'Valor calculado — consulte a origem abaixo. Para mudar, altere o registro de origem.':(r&&r.ro?'Consulta: você não tem permissão para editar este registro.':'Consulta')):(ed.sub||'Altere os campos e salve. Os cálculos da tabela são refeitos ao salvar.')));
    F.ro=!!fm.ro; F.edit=!fm.ro; F.warn=!!fm.warn;
    F.items=fm.tot? flat.filter(x=>x.lvl===0).map(x=>({t:g2text(x.r,sp.cols[0]), v:sp.cols.filter(c=>c.agg).map(c=>c.l+': '+g2text(x.r,c)).join(' · ')})):[];
    F.origins=(r&&r.o)?r.o.map(o=>({t:o.t,h:o.h||'#',isLink:!!o.h,isTxt:!o.h})):[]; F.hasOrigins=F.origins.length>0;
    F.acts=(!fm.tot&&!fm.isNew&&r&&self.g2formActs)?(self.g2formActs(id,r,fm)||[]):[]; F.hasActs=F.acts.length>0;
    const visf=(ed.fields||[]).filter(f=>g2cond(f,fm.draft));
    F.fields=fm.tot?[]:visf.map(f=>{ let val=fm.draft[f.k]; if(f.live&&self.g2live){ const lv=self.g2live(id,f.k,fm.draft); if(lv!==undefined&&lv!==null) val=lv; } const err=(fm.errs||{})[f.k]; const dis=!!fm.ro||!!f.ro||(!!f.newOnly&&!fm.isNew); const mv=(String(val||'').split(';').map(x=>x.trim()).filter(Boolean));
      return {l:f.l, fid:'fx_'+id+'_'+f.k, im:(f.t==='num'?'decimal':''), isSel:f.t==='sel', isMulti:f.t==='multi', isTxt:(f.t!=='sel'&&f.t!=='area'&&f.t!=='multi'), isArea:f.t==='area', type:(f.t==='date'?'date':(f.t==='email'?'email':(f.t==='tel'?'tel':'text'))),
        mopts:(f.t==='multi'?(f.opts||[]).map(o=>({t:o,on:mv.indexOf(o)>=0,dis,tog:()=>{ const cur=g2st(self,id).fm; if(!cur||dis) return; let a=String(cur.draft[f.k]||'').split(';').map(x=>x.trim()).filter(Boolean); const i=a.indexOf(o); if(i>=0) a.splice(i,1); else a.push(o); const d=Object.assign({},cur.draft,{[f.k]:a.join('; ')}); const er=Object.assign({},cur.errs||{}); delete er[f.k]; g2set(self,id,{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }})):[]), v:(val===undefined?'':val), u:f.u||'', hasU:!!f.u, help:f.help||'', hasHelp:!!f.help,
        dis, err:!!err, errMsg:err||'', ist:'font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;border:1px solid '+(err?'#B42318':'#E4E9E5')+';background:'+(dis?'#F4F6F3':'#FFFFFF')+';color:#15201A;',
        opts:(f.dyn&&self.g2opts)?(self.g2opts(id,f.k,fm.draft,fm.rid)||[]):(f.opts||[]).map(o=>({v:o,t:o})),
        set:(e)=>{ const cur=g2st(self,id).fm; if(!cur) return; let d=Object.assign({},cur.draft,{[f.k]:e.target.value}); if(self.g2draft){ const d2=self.g2draft(id,f.k,d,cur); if(d2) d=d2; } const er=Object.assign({},cur.errs||{}); delete er[f.k]; g2set(self,id,{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }}; });
    F.nerr=Object.keys(fm.errs||{}).length; F.hasErr=F.nerr>0;
    F.save=()=>g2save(self,sp); F.cancel=()=>g2close(self,sp); F.close=()=>g2close(self,sp);
    F.discard=()=>g2set(self,id,{fm:null}); F.keep=()=>{ const cur=g2st(self,id).fm; g2set(self,id,{fm:Object.assign({},cur,{warn:false})}); };
    F.key=(e)=>{ if(e && e.key==='Escape'){ e.preventDefault(); g2close(self,sp); } };
  }
  v[id+'_F']=F; }
// barra lateral recolhível: a escolha vale entre telas (guardada no navegador de quem usa). Em tela estreita (até 1023 px:
// celular, tablet em pé, zoom de 200 %) o menu aberto passa por cima do conteúdo e é passageiro: toda tela começa com ele
// recolhido (a escolha "aberto" do computador não cobre o título no estreito), abrir/fechar ali não muda a escolha guardada,
// e ao estreitar a janela (girar o aparelho) ele recolhe sem recarregar.
const G2_ESTREITO='(max-width: 1023px)';
function g2estreito(){ try{ return window.matchMedia(G2_ESTREITO).matches; }catch(e){ return false; } }
function g2menuRec(){ if(g2estreito()) return true; try{ return localStorage.getItem('safrion.menuRecolhido')==='1'; }catch(e){ return false; } }
// <perfis> Perfil de demonstração (sem login; PRD 2.1): quem age nas decisões que exigem papel. Vale entre telas, no navegador de quem usa;
// demonstra a experiência, não é segurança (no software o servidor tira o ator da sessão). Pessoas e papéis: CF-01 e telas vizinhas.
// O papel vem sempre desta lista (g2pf), nunca do objeto que o comando recebe. Bloco único, lido também pelos testes sem navegador.
const G2_PERFIS=[{k:'Ana',t:'Ana · Gestora e RT',papeis:{gestor:'gestora',agronomo:'agrônoma'}},{k:'Caio',t:'Caio · PCP',papeis:{pcp:'PCP'}},
  {k:'Rui',t:'Rui · Almoxarife e expedição',papeis:{almoxarife:'almoxarife',expedicao:'expedição'}},{k:'Paula',t:'Paula · Conferência',papeis:{almoxarife:'almoxarife',conferente:'conferência'}},{k:'Zé',t:'Zé · Mecânico',papeis:{mecanico:'mecânico'}},
  {k:'Dora',t:'Dora · Comercial',papeis:{comercial:'comercial'}},{k:'Marta',t:'Marta · Qualidade',papeis:{qualidade:'qualidade'}}];   // Comercial (D-C13): Dora vende, reserva e programa carga; Rui confirma a saída física; Ana (gestora) pode tudo e aprova crédito. Marta (Qualidade, R-13 da Colheita): libera lote em inspeção, inclusive o devolvido (A3 da revisão do Comercial)
const G2_PERFIL_KEY='safrion.perfilDemo'; let G2_PERFIL_MEM='';
function g2pf(p){ const k=(typeof p==='string')?p:(p&&p.k); return G2_PERFIS.find(x=>x.k===k)||null; }   // perfil do cadastro pela chave ("Ana" ou {k:'Ana'})
function g2perfil(){ let k=G2_PERFIL_MEM; try{ k=localStorage.getItem(G2_PERFIL_KEY)||k; }catch(e){} return g2pf(k)||G2_PERFIS[0]; }
function g2papel(p,papel){ const q=g2pf(p); return !!q&&[].concat(papel).every(x=>!!q.papeis[x]); }   // papel ou lista (todos exigidos)
function g2ator(p,papel){ const q=g2pf(p); if(!q) return ''; const n=[].concat(papel).map(x=>q.papeis[x]).filter(Boolean);
  return q.k+' ('+(n.length?n.join(' e '):Object.values(q.papeis)[0])+')'; }   // "Ana (gestora)" · "Ana (gestora e agrônoma)"; fora do cadastro: ''
function g2quem(papel){ return G2_PERFIS.filter(p=>g2papel(p,papel)).map(p=>g2ator(p,papel)).join(' ou '); }
function g2umPapel(p,papeis){ const q=g2pf(p); return (q&&papeis.find(x=>!!q.papeis[x]))||''; }   // o primeiro papel da lista que o perfil tem (basta um): '' se nenhum
function g2quemUm(papeis){ return G2_PERFIS.filter(p=>g2umPapel(p,papeis)).map(p=>g2ator(p,g2umPapel(p,papeis))).join(' ou '); }   // "Ana (gestora) ou Rui (almoxarife) ou …"
function g2mesma(a,b){ const n=s=>String(s||'').split(/[\s(]/)[0]; return !!n(a)&&n(a)===n(b); }   // "Ana" × "Ana (gestora)"
// </perfis>
// trocar o perfil (aqui ou em outra aba) fecha a confirmação ou o formulário de decisão aberto, montado para o perfil anterior (revisão do CTL-3,
// achado 1; dano evitado: a tela afirmar que decide quem não tem o papel). Cada tela diz o que fecha em self.g2perfilFecha (O.S., Mapa, Estoque)
function g2navvals(self,v,nav){ const rec=(self.state.menuRec===undefined)?g2menuRec():!!self.state.menuRec;
  const pf=g2perfil(); v.perfil_k=pf.k; v.perfil_ini=pf.k.charAt(0); v.perfil_opts=G2_PERFIS.map(p=>({v:p.k,t:p.t}));
  v.perfil_set=(e)=>{ const k=e.target.value; G2_PERFIL_MEM=k; try{ localStorage.setItem(G2_PERFIL_KEY,k); }catch(er){} self.setState(Object.assign({perfil:k,g2toast:'Perfil de demonstração: '+((g2pf(k)||{}).t||k)+' (não é segurança de acesso).'},self.g2perfilFecha||{})); };
  if(!self.__g2pf){ self.__g2pf=1; try{ window.addEventListener('storage',(e)=>{ if(e.key===G2_PERFIL_KEY) self.setState(Object.assign({perfil:e.newValue},self.g2perfilFecha||{})); }); }catch(er){} }
  const fixa=(n)=>{ if(g2estreito()) return; try{ localStorage.setItem('safrion.menuRecolhido',n?'1':'0'); }catch(e){} };
  if(!self.__g2mq){ self.__g2mq=1; try{ window.matchMedia(G2_ESTREITO).addEventListener('change',(ev)=>self.setState({menuRec:ev.matches?true:undefined})); }catch(e){} }
  v.menu_rec=rec; v.menu_aberto=!rec; v.menu_cls=rec?'rec':''; v.menu_tog_lab=rec?'Expandir menu':'Recolher menu';
  v.menu_tog=()=>{ fixa(!rec); self.setState({menuRec:!rec}); };
  (nav||[]).forEach((m,i)=>{ const o=(self.state.nav||{}); const open=(o[i]===undefined)?!!m.open:!!o[i];
  v['nav'+i+'_open']=open; v['nav'+i+'_sym']=open?'▾':'▸';
  // com a barra recolhida, clicar no grupo abre a barra com esse grupo aberto
  v['nav'+i+'_tog']=()=>{ const n=Object.assign({},self.state.nav||{}); if(rec){ n[i]=true; fixa(false); self.setState({nav:n,menuRec:false}); return; } n[i]=!open; self.setState({nav:n}); }; }); }

(function g2glob(){ if(typeof document==='undefined'||window.__g2glob) return; window.__g2glob=1;
  const vis=(e)=>!!e&&e.getClientRects().length>0;
  const rotulo=()=>[...document.querySelectorAll('.etp-chk')].find(vis);
  document.addEventListener('touchstart',()=>{},{passive:true});
  document.addEventListener('keydown',(e)=>{
    const t=e.target;
    if(e.key==='Enter'&&t&&t.classList&&t.classList.contains('etp-chk')){ e.preventDefault(); t.click(); return; }
    if(e.key!=='Escape'||e.defaultPrevented) return;
    const ab=[...document.querySelectorAll('.etp-chk')].find(x=>x.checked&&vis(x));
    if(ab){ e.preventDefault(); ab.click(); ab.focus(); return; }
    const m=document.querySelector('.menu-lat:not(.rec)'); const tg=document.querySelector('.ml-tog');
    if(m&&tg&&g2estreito()&&getComputedStyle(m).position==='absolute'){ e.preventDefault(); tg.click(); setTimeout(()=>{ const b=document.querySelector('.ml-tog'); if(b) b.focus(); },0); } });
  // menu sobreposto: se o foco sai dele (Tab depois do último item), ele fecha; o foco segue no conteúdo, sem nada por cima
  document.addEventListener('focusin',(e)=>{ const m=document.querySelector('.menu-lat:not(.rec)'); const tg=document.querySelector('.ml-tog'); const t=e.target;
    if(!m||!tg||!t||m.contains(t)||tg.contains(t)||!g2estreito()||getComputedStyle(m).position!=='absolute') return; tg.click(); });
  document.addEventListener('click',(e)=>{ const it=e.target&&e.target.closest&&e.target.closest('.etp-itens>*'); if(!it) return;
    const ab=[...document.querySelectorAll('.etp-chk')].find(x=>x.checked&&vis(x)); if(!ab) return;
    setTimeout(()=>{ const k=rotulo(); if(k) k.focus({preventScroll:true}); },60); },true);
  // tabela mais larga que a caixa: a borda direita esmaece (data-mais) enquanto houver colunas à direita; some no fim da rolagem.
  // 1ª coluna presa (sticky): se ela passa de 45 % da caixa numa tabela que rola de lado, a trilha dela fica limitada a 45 %
  // (minmax: o nome quebra linha, nunca abaixo da maior palavra) e nenhuma outra coluna passa da área visível ao lado dela, para
  // as demais colunas e as ações da linha aparecerem inteiras ao rolar
  // (--g2cols + data-c0). A decisão só é refeita quando a largura da caixa muda (sem vaivém). A rolagem do foco desconta a
  // coluna presa e o cabeçalho preso (--g2c0w, --g2hh): nada focado fica por baixo deles.
  const presa=(r)=>{ const cw=r.clientWidth; if(!cw) return; const hr=r.querySelector('[role=table]>[role=row]'); if(!hr) return;
    const hs=[...hr.querySelectorAll('[role=columnheader]')]; const h=hs.find(x=>x.classList.contains('g2c0')); if(!h) return;
    if(r.hasAttribute('data-c0')&&r.__c0w!==cw){ r.removeAttribute('data-c0'); r.style.removeProperty('--g2cols'); }
    const cap=Math.max(96,Math.round(cw*.45));
    if(!r.hasAttribute('data-c0')&&r.scrollWidth-cw>2&&h.getBoundingClientRect().width>cap+1){
      const c0='minmax(min-content, '+cap+'px)'; r.setAttribute('data-c0',''); r.style.setProperty('--g2cols',hs.map(x=>x===h?c0:'auto').join(' '));
      const vis=Math.max(96,Math.floor(cw-h.getBoundingClientRect().width-4)); r.style.setProperty('--g2cols',hs.map(x=>x===h?c0:'fit-content('+vis+'px)').join(' ')); }
    r.__c0w=cw; r.style.setProperty('--g2c0w',Math.round(h.getBoundingClientRect().width)+'px'); r.style.setProperty('--g2hh',Math.round(hr.getBoundingClientRect().height)+'px'); };
  const faixa=()=>{ const col=document.querySelector('.ml-tog+div'); if(!col) return; const nv=col.querySelector(':scope>.etp'); col.style.setProperty('--etp-h',(nv&&nv.getClientRects().length?nv.offsetHeight:0)+'px'); };
  const acoes=()=>{ const a=[...document.querySelectorAll('main .acoes')].find(vis); const h=(a&&getComputedStyle(a).position==='sticky')?Math.round(a.getBoundingClientRect().height):0; document.documentElement.style.setProperty('--acoes-h',h+'px'); };
  const mais=()=>{ faixa(); acoes(); document.querySelectorAll('.g2rola,.rola').forEach(r=>{ if(r.classList.contains('g2rola')) presa(r); if(r.scrollWidth-r.clientWidth-r.scrollLeft>2) r.setAttribute('data-mais',''); else r.removeAttribute('data-mais'); }); };
  // o navegador não rola até um controle só em parte visível na caixa da tabela (ex.: botão do cabeçalho rente à borda, ou por
  // trás da coluna presa): ao receber o foco ele vem inteiro para a vista (a linha inteira e a coluna presa não precisam)
  document.addEventListener('focusin',(e)=>{ const t=e.target; const r=t&&t.closest&&t.closest('.g2rola'); if(!r||t===r||t.getAttribute('role')==='row') return;
    if(t.closest('.g2c0')) return;
    const b=t.getBoundingClientRect(), q=r.getBoundingClientRect(), pl=parseFloat(getComputedStyle(r).scrollPaddingLeft)||0;
    if(b.left<q.left+pl-1||b.right>q.left+r.clientWidth+1) t.scrollIntoView({block:'nearest',inline:'nearest'}); });
  let raf=0; const agenda=()=>{ if(raf) return; raf=requestAnimationFrame(()=>{ raf=0; mais(); }); };
  window.addEventListener('resize',agenda); document.addEventListener('scroll',agenda,true);
  try{ new MutationObserver(agenda).observe(document.documentElement,{childList:true,subtree:true}); }catch(e){} setTimeout(agenda,300);
  // o navegador tira o foco de um elemento que some (display:none) ao girar/redimensionar: guarda quem tinha o foco no início do
  // redimensionamento e, se ele sumiu, leva o foco ao equivalente visível
  let tmr=null, pre=null; window.addEventListener('resize',()=>{ const ae=document.activeElement; if(!pre&&ae&&ae!==document.body) pre=ae; clearTimeout(tmr); tmr=setTimeout(()=>{ const at=document.activeElement; const a=(at&&at!==document.body)?at:pre; pre=null; if(!a||vis(a)||!a.closest) return;
    if(at&&at!==document.body&&at!==a) return;
    if(a.closest('.etp')){ const k=rotulo(); if(k) k.focus({preventScroll:true}); else { const c=document.querySelector('.etp-sec .etp-itens [aria-current=page],.etp-sec .etp-itens [aria-current=true]'); if(c&&vis(c)) c.focus({preventScroll:true}); } }
    else if(a.closest('.menu-lat')){ const b=document.querySelector('.ml-tog'); if(b) b.focus({preventScroll:true}); } },150); });
})();
// ---- UX-ACAO-UNICA-20261003 (DS-02, DS-31 v2, DS-33 §74.5.7.1, DS-61) ----
// Painel modal (DS-02 v2 · v3.1 "um modal deixa o fundo inerte e devolve o foco ao fechar"): enquanto um painel lateral sobre véu
// está aberto, ele assume a tarefa: Tab e Shift+Tab circulam só dentro dele (o véu já bloqueia o ponteiro), o leitor de tela recebe
// aria-modal e, ao fechar, se o foco ficou perdido, ele volta ao último controle fora do painel (quem o abriu). Não apaga nem
// desabilita comandos do fundo; foco e cliques feitos pelo próprio código da tela não são afetados.
(function(){ if(typeof document==='undefined'||window.__g2modal) return; window.__g2modal=1;
  const vis=e=>!!e&&e.isConnected&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden';
  const modal=()=>[...document.querySelectorAll('aside[role=dialog]')].find(d=>vis(d)&&d.parentElement&&getComputedStyle(d.parentElement).position==='fixed');
  const foc=d=>[...d.querySelectorAll('a[href],button,input,select,textarea,[tabindex]')].filter(x=>!x.disabled&&x.tabIndex>=0&&vis(x));
  let fora=null, aberto=null;
  document.addEventListener('focusin',(e)=>{ const t=e.target; if(t&&t.closest&&t!==document.body&&!t.closest('aside[role=dialog]')) fora=t; },true);
  document.addEventListener('keydown',(e)=>{ if(e.key!=='Tab'||e.defaultPrevented) return; const d=modal(); if(!d) return; const fs=foc(d); if(!fs.length) return;
    const a=document.activeElement, i=fs.indexOf(a);
    if(!d.contains(a)){ e.preventDefault(); (e.shiftKey?fs[fs.length-1]:fs[0]).focus(); }
    else if(e.shiftKey&&i===0){ e.preventDefault(); fs[fs.length-1].focus(); }
    else if(!e.shiftKey&&i===fs.length-1){ e.preventDefault(); fs[0].focus(); } },true);
  // quem abriu: o foco atual fora do painel (focus() sem janela ativa não dispara focusin) ou, sem ele, o último foco fora do painel
  // o nó que abriu o painel pode ser redesenhado ao fechar (área de ações, cartão): guarda também como reencontrar o equivalente
  const marca=(v)=>v?{a:v.dataset&&v.dataset.acao,id:v.id,t:(v.innerText||'').replace(/\s+/g,' ').trim(),area:!!(v.closest&&v.closest('[data-acoes]'))}:null;
  const acha=(m)=>{ if(!m) return null; if(m.id){ const e=document.getElementById(m.id); if(vis(e)) return e; }
    const cs=[...document.querySelectorAll(m.area?'[data-acoes] button,[data-acoes] a':'main button,main a,header button,header a')].filter(vis);
    return (m.a&&cs.find(e=>e.dataset.acao===m.a))||cs.find(e=>(e.innerText||'').replace(/\s+/g,' ').trim()===m.t)||null; };
  const devolve=(v,m)=>{ const ae=document.activeElement; if(ae&&ae!==document.body&&ae.isConnected) return true; const alvo=vis(v)?v:acha(m); if(!alvo) return false; try{ alvo.focus({preventScroll:true}); }catch(e){} return document.activeElement===alvo; };
  const olha=()=>{ const d=modal();
    if(d&&d!==aberto){ aberto=d; const ae=document.activeElement, o=(ae&&ae!==document.body&&!(ae.closest&&ae.closest('aside[role=dialog]')))?ae:fora; d.__volta=o; d.__marca=marca(o); if(d.getAttribute('aria-modal')!=='true') d.setAttribute('aria-modal','true'); }
    else if(!d&&aberto){ const v=aberto.__volta, m=aberto.__marca; aberto=null;
      devolve(v,m); setTimeout(()=>devolve(v,m),0); setTimeout(()=>devolve(v,m),80); } };   // de novo depois do redesenho da tela (só age se o foco caiu no BODY)
  try{ new MutationObserver(olha).observe(document.documentElement,{childList:true,subtree:true}); }catch(e){} })();
// Indicador de progresso do processo guiado: só informa (atual, concluída, pendente, impedida) com a palavra do estado para o leitor
// de tela; não navega (sem handler, sem foco, sem hover de ação). O argumento go fica por compatibilidade e não é usado.
function g2steps(self,v,pre,n,cur,whys,go){ for(let i=1;i<=n;i++){ const on=(i===cur); const w=(whys&&whys[i])||''; const feita=(!on&&i<cur&&!w);
  v[pre+i+'_st']='display:flex;align-items:center;gap:6px;padding:5px 6px;border-radius:10px;min-width:0;color:#15201A;cursor:default;'+(on?'background:#E4F3E9;box-shadow:inset 0 -2px 0 #1E7A4C;':'background:transparent;');
  v[pre+i+'_bst']='width:22px;height:22px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:800;flex-shrink:0;'+(on?'background:#1E7A4C;color:#fff;':(w?'background:#FDE8E6;color:#B42318;':(feita?'background:#E3F2E8;color:#1E6B47;':'background:#EEF1EE;color:#15201A;')));
  v[pre+i+'_tst']='font-size:12px;line-height:1.2;font-weight:'+(on?'800':'600')+';color:'+(on||feita||w?'#15201A':'#4B5A51')+';';
  v[pre+i+'_num']=feita?'✓':String(i); v[pre+i+'_sr']=on?'etapa atual':(w?'impedida':(feita?'concluída':'pendente'));
  v[pre+i+'_why']=w; v[pre+i+'_hasWhy']=!!w; v[pre+i+'_cur']=on?'step':'false'; } }
// Seções de uma tela de trabalho paralelo (Estoque): navegação em qualquer ordem, sem número de etapa; pendência escrita
function g2secoes(self,v,pre,n,cur,whys,go){ for(let i=1;i<=n;i++){ const on=(i===cur); const w=(whys&&whys[i])||'';
  v[pre+i+'_st']='display:flex;flex-direction:column;justify-content:center;gap:1px;padding:6px 10px;border-radius:10px;border:0;font-family:inherit;font-size:12.5px;line-height:1.2;cursor:pointer;text-align:left;min-width:0;color:#15201A;'+(on?'background:#E4F3E9;box-shadow:inset 0 -2px 0 #1E7A4C;font-weight:800;':'background:transparent;font-weight:600;');
  v[pre+i+'_why']=w; v[pre+i+'_hasWhy']=!!w; v[pre+i+'_cur']=on?'true':'false'; v[pre+i+'_go']=()=>go(i); } }
// Troca de etapa pela área de ações: o conteúdo novo começa no topo e o foco vai ao título do primeiro bloco (não fica no pé da etapa
// anterior). pos: posição de rolagem a restaurar (volta à revisão) em vez do topo: {top, rolas (caixas roláveis da tela, em ordem), foco}.
function g2etapa(self,patch,pos){ self.setState(patch); setTimeout(()=>{ try{ const m=document.querySelector('main[data-scroll]'); if(!m) return;
  const col=document.querySelector('.ml-tog+div'); const rola=(col&&col.scrollHeight>col.clientHeight+1&&getComputedStyle(col).overflowY==='auto')?col:m;
  if(pos&&pos.top!==undefined){ rola.scrollTop=pos.top; [...m.querySelectorAll('.g2rola,.rola')].forEach((r,i)=>{ if(pos.rolas&&pos.rolas[i]!==undefined) r.scrollTop=pos.rolas[i]; }); }
  else { rola.scrollTop=0; if(rola!==m) m.scrollTop=0; }
  const alvo=(pos&&pos.foco)?document.querySelector(pos.foco):null; const h=alvo||[...m.querySelectorAll('h2,h3')].find(e=>e.getClientRects().length);
  if(h){ if(!h.matches('a,button,input,select,textarea,[tabindex]')) h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); } }catch(e){} },30); }
// Área de ações única do processo guiado (engine.area_acoes): nota com a causa da pendência e um atalho contextual, retorno secundário
// à esquerda (nomeia o destino), avanço secundário quando a primária é outra (resolver a pré-condição ou comando material) e uma
// primária à direita (botão ou link). Cada item: {t, fn | h, a (data-acao), to (etapa de destino)}. Se o avanço/primária leva ao mesmo
// destino do retorno, o retorno sai (um caminho por intenção). Sem nada a mostrar, a área não aparece.
function g2acoes(v,pre,c){ c=c||{}; const nada=()=>{};
  let volta=c.volta||null, sec=c.sec||null, prim=c.prim||null;
  if(volta&&volta.to!==undefined&&((prim&&prim.to===volta.to)||(sec&&sec.to===volta.to))) volta=null;
  if(sec&&prim&&sec.to!==undefined&&sec.to===prim.to) sec=null;
  const lnks=(c.lnks||[]).filter(l=>l&&l.t); v[pre+'_lnks']=lnks.map(l=>({t:l.t,fn:l.fn||nada})); v[pre+'_hasLnks']=lnks.length>0;   // atalhos da nota (um por fato)
  v[pre+'_hasNota']=!!(c.nota||lnks.length); v[pre+'_nota']=c.nota||''; v[pre+'_hasCtx']=!!c.ctx; v[pre+'_ctxT']=c.ctx?c.ctx.t:''; v[pre+'_ctxFn']=c.ctx?c.ctx.fn:nada;
  v[pre+'_hasVolta']=!!volta; v[pre+'_voltaT']=volta?volta.t:''; v[pre+'_volta']=volta?volta.fn:nada; v[pre+'_voltaA']=(volta&&volta.a)||'voltar';
  v[pre+'_hasSec']=!!sec; v[pre+'_secT']=sec?sec.t:''; v[pre+'_secFn']=sec?sec.fn:nada; v[pre+'_secA']=(sec&&sec.a)||'avancar';
  const lk=!!(prim&&prim.h); v[pre+'_hasPrim']=!!prim&&!lk; v[pre+'_hasLink']=lk; v[pre+'_primT']=prim?prim.t:''; v[pre+'_primFn']=(prim&&prim.fn)||nada; v[pre+'_href']=lk?prim.h:'#';
  v[pre+'_primA']=(prim&&prim.a)||'avancar'; v[pre+'_desc']=c.nota?(pre+'-nota'):'';
  v[pre+'_has']=!!(c.nota||lnks.length||volta||sec||prim); }
