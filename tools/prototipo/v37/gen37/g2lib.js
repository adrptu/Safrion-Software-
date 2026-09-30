// ===== G2 · grade interativa, formulário lateral e navegação (motor do protótipo v3.7) =====
const G2C={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],blue:['#1E5F8F','#E3F0FB'],orange:['#9A3F00','#FFE8D6']};
const G2CTA='display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;white-space:nowrap;background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;cursor:pointer;font-family:inherit;line-height:1.25;';
const G2CTAU='display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;white-space:nowrap;background:#FFFFFF;color:#B42318;border:1px solid #B42318;cursor:pointer;font-family:inherit;line-height:1.25;';
function g2num(s){ if(typeof s==='number') return s; if(s===null||s===undefined) return NaN; let t=String(s).trim(); if(!t) return NaN; t=t.replace(/[^0-9,.\-]/g,''); if(t.indexOf(',')>=0){ t=t.replace(/\./g,'').replace(',','.'); } else if((t.match(/\./g)||[]).length>1 || /^\-?\d{1,3}(\.\d{3})+$/.test(t)){ t=t.replace(/\./g,''); } return parseFloat(t); }
function g2fmtn(n,d,dmin){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:(dmin!==undefined?dmin:(d||0)),maximumFractionDigits:d||0}); }
function g2fmt(v,c){ if(v===null||v===undefined||v==='') return '—'; if(c&&c.t==='date'&&/^\d{4}-\d{2}-\d{2}$/.test(String(v))){ const a=String(v).split('-'); return a[2]+'/'+a[1]+'/'+a[0]; } if(c&&c.zdash&&Number(v)===0) return '—'; if(c&&c.t==='num'){ const n=Number(v); if(isNaN(n)) return String(v); return (c.pre||'')+g2fmtn(n,c.d,c.dmin)+(c.u?' '+c.u:''); } return String(v); }
function g2st(self,id){ return ((self.state.g2||{})[id])||{}; }
function g2set(self,id,patch){ const all=Object.assign({},self.state.g2||{}); all[id]=Object.assign({},all[id]||{},patch); self.setState({g2:all}); }
function g2rows(self,sp){ const st=g2st(self,sp.id); return st.rows||sp.rows; }
function g2find(list,id){ for(const r of list){ if(r.id===id) return r; if(r.kids){ const k=g2find(r.kids,id); if(k) return k; } } return null; }
function g2text(r,c){ if(r.s&&r.s[c.k]!==undefined&&r.s[c.k]!==null) return String(r.s[c.k]); if(r.v&&r.v[c.k]!==undefined&&r.v[c.k]!==null) return g2fmt(r.v[c.k],c); return ''; }
function g2key(r,c){ if(c.t==='num'){ let n=(r.v&&r.v[c.k]!==undefined&&r.v[c.k]!==null&&r.v[c.k]!=='')?Number(r.v[c.k]):g2num(r.s&&r.s[c.k]); return isNaN(n)?null:n; } const t=g2text(r,c); return (t===''||t==='—')?null:t; }
function g2match(r,sp,st,mask,added){
  if(r.sh && !(added||{})[r.sh]) return false;
  if(mask && r.ri!==undefined && mask[r.ri]===false) return false;
  const q=(st.q||'').trim().toLowerCase();
  if(q){ const all=sp.cols.map(c=>g2text(r,c)).join(' ').toLowerCase(); if(all.indexOf(q)<0) return false; }
  const f=st.f||{}; for(const k in f){ const vals=f[k]; if(!vals||!vals.length) continue; const c=sp.cols.find(x=>x.k===k); if(!c) continue; if(vals.indexOf(g2text(r,c))<0) return false; }
  return true; }
function g2sort(arr,sp,st){ const so=st.so||sp.so; if(!so||!so.k) return arr; const c=sp.cols.find(x=>x.k===so.k); if(!c) return arr; const d=so.d?-1:1;
  return arr.slice().sort((a,b)=>{ const x=g2key(a,c), y=g2key(b,c); if(x===null&&y===null) return 0; if(x===null) return 1; if(y===null) return -1;
    if(typeof x==='number'&&typeof y==='number') return (x-y)*d; return String(x).localeCompare(String(y),'pt-BR',{numeric:true,sensitivity:'base'})*d; }); }
function g2filtering(st){ return !!((st.q||'').trim()) || Object.keys(st.f||{}).some(k=>(st.f[k]||[]).length); }
function g2flat(sp,st,rows,mask,added){
  const out=[]; const exp=st.x||sp.x0||{}; const filt=g2filtering(st);
  const deep=(r)=>g2match(r,sp,st,mask,added)||(r.kids||[]).some(deep);
  const walk=(list,lvl,parentOk)=>{ g2sort(list,sp,st).forEach(r=>{ const kids=r.kids||[]; const selfOk=g2match(r,sp,st,mask,added);
      const anyKid=kids.some(deep); if(!(selfOk||anyKid||parentOk)) return;
      out.push({r,lvl,has:kids.length>0});
      if(kids.length && (exp[r.id] || (filt && anyKid && !selfOk))) walk(kids,lvl+1,selfOk&&!filt); }); };
  walk(rows,0,false); return out; }
function g2part(p,v){ const o={isCn:false,isTxt:false,isB:false,isMut:false,isChip:false,isTag:false,isLink:false,isCta:false,isAct:false,isBr:false,t:p.t||'',st:'',dot:'',href:p.h||'#',fn:null,title:p.t||''};
  switch(p.k){ case 'b': o.isB=true; break; case 'mut': o.isMut=true; break;
    case 'chip': { const cc=G2C[p.c]||G2C.gray; o.isChip=true; o.st='display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; o.dot='width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'; break; }
    case 'cn': { const cc=G2C[p.c]||G2C.gray; o.isCn=true; o.st='font-weight:800;white-space:nowrap;color:'+cc[0]+';'; break; }
    case 'tag': o.isTag=true; break; case 'link': o.isLink=true; break;
    case 'cta': o.isCta=true; o.st=p.u?G2CTAU:G2CTA; break;
    case 'act': o.isAct=true; if(p.lk) { o.lk=true; } if(p.fn&&p.fn.indexOf(':')>0){ const nm=p.fn.split(':')[0], ar=p.fn.slice(nm.length+1); o.fn=()=>{ if(v&&v[nm]) v[nm](ar); }; } else o.fn=(v&&p.fn&&v[p.fn])||(()=>{}); o.st=p.lk?'border:0;background:transparent;padding:0;color:#1E7A4C;font-weight:700;cursor:pointer;font-family:inherit;font-size:13px;text-decoration:underline;text-underline-offset:3px;text-align:left;':(p.u?G2CTAU:G2CTA); break;
    case 'br': o.isBr=true; break; default: o.isTxt=true; }
  return o; }
function g2sum(sp,flat,c){ let s=0,n=0; flat.forEach(x=>{ if(x.lvl!==0) return; const k=g2key(x.r,c); if(typeof k==='number'){ s+=k; n++; } }); return n? (c.agg==='avg'? s/n : s) : null; }
function g2open(self,sp,rid,e){
  if(e&&e.target&&e.target.closest&&e.target.closest('a,button,input,select,textarea,label,[data-noedit]')) return;
  const ed=sp.edit||{m:'none'}; if(ed.m==='none') return;
  const r=g2find(g2rows(self,sp),rid); if(!r) return;
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
  const vis=(ed.fields||[]).filter(f=>!f.cond || String(fm.draft[f.cond.k])===String(f.cond.eq));
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
  const id=sp.id, st=g2st(self,id), rows=g2rows(self,sp), added=self.state.added||{};
  const flat=g2flat(sp,st,rows,mask,added); const ed=sp.edit||{m:'none'}; const editable=ed.m&&ed.m!=='none';
  const so=st.so||sp.so||{};
  v[id+'_head']=sp.cols.map((c,ci)=>({l:c.l, st:'display:flex;align-items:center;gap:2px;justify-content:'+(c.a==='r'?'flex-end':'flex-start')+';'+(ci===0?'position:sticky;left:0;z-index:2;background:#F4F6F3;box-shadow:1px 0 0 #E4E9E5;':''),
     arrow:(so.k===c.k?(so.d?'▼':'▲'):'⇅'), astyle:(so.k===c.k?'color:#1E7A4C;':'color:#B7C1BA;'), sortLabel:'Ordenar por '+c.l,
     sort:()=>{ const cur=g2st(self,id).so||sp.so||{}; let nx; if(cur.k!==c.k) nx={k:c.k,d:false}; else if(!cur.d) nx={k:c.k,d:true}; else nx={}; g2set(self,id,{so:nx}); },
     fil:(((st.f||{})[c.k]||[]).length?' · '+((st.f||{})[c.k]||[]).length:''), fcolor:(((st.f||{})[c.k]||[]).length?'#1E7A4C':'#8A968E'),
     fmenu:()=>{ const cur=g2st(self,id).fmc; g2set(self,id,{fmc:(cur===c.k?null:c.k)}); }, flabel:'Filtrar '+c.l}));
  // valores do filtro aberto
  const fmc=st.fmc; const fcol=sp.cols.find(c=>c.k===fmc);
  if(fcol){ const cnt={}; const leaf=(list)=>list.forEach(r=>{ if(r.kids&&r.kids.length) leaf(r.kids); if(!(r.kids&&r.kids.length)||sp.tree===false||!sp.tree){ const t=g2text(r,fcol)||'(vazio)'; cnt[t]=(cnt[t]||0)+1; } }); leaf(rows);
    const cur=(st.f||{})[fmc]||[]; const keys=Object.keys(cnt).sort((a,b)=>a.localeCompare(b,'pt-BR',{numeric:true}));
    v[id+'_fm']={open:true, l:fcol.l, vals:keys.map(k=>({t:k,n:cnt[k],on:cur.indexOf(k)>=0,
        tog:()=>{ const f=Object.assign({},g2st(self,id).f||{}); const a=(f[fmc]||[]).slice(); const i=a.indexOf(k); if(i>=0) a.splice(i,1); else a.push(k); f[fmc]=a; g2set(self,id,{f}); }})),
      asc:()=>g2set(self,id,{so:{k:fmc,d:false}}), desc:()=>g2set(self,id,{so:{k:fmc,d:true}}),
      clear:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[fmc]; g2set(self,id,{f}); }, close:()=>g2set(self,id,{fmc:null})};
  } else v[id+'_fm']={open:false,vals:[]};
  const total=(sp.total!==false) && sp.cols.some(c=>c.agg);
  v[id+'_rows']=flat.map(({r,lvl,has})=>{
    const cells=[]; const exp=(st.x||sp.x0||{});
    if(sp.sel) cells.push({isSel:true,isData:false,isDel:false,on:!!(st.sel||{})[r.id],selLabel:'Selecionar '+g2text(r,sp.cols[0]),
      tog:()=>{ const s2=Object.assign({},g2st(self,id).sel||{}); s2[r.id]=!s2[r.id]; g2set(self,id,{sel:s2}); },st:'padding:6px 4px 6px 12px;'});
    sp.cols.forEach((c,ci)=>{
      const empty=(has && ci>0 && !(r.p&&r.p[c.k]) && (!r.v || r.v[c.k]===undefined || r.v[c.k]===''));
      const raw=empty?[]:((r.p&&r.p[c.k]&&r.p[c.k].length)?r.p[c.k]:[{k:(ci===0&&lvl===0&&has?'b':'txt'),t:g2fmt(r.v?r.v[c.k]:'',c)}]);
      const cell={isSel:false,isData:true,isDel:false,parts:raw.map(p=>g2part(p,v)),pw:'max-width:'+(c.w||340)+'px;',
        st:'padding:6px 8px;'+(c.a==='r'?'text-align:right;justify-content:flex-end;white-space:nowrap;font-variant-numeric:tabular-nums;':'')+(ci===0&&sp.tree?'padding-left:'+(8+lvl*20)+'px;':'')+(ci===0?'position:sticky;left:0;z-index:1;background:'+(lvl>0?'#FBFCFA':'#FFFFFF')+';box-shadow:1px 0 0 #E4E9E5;':'')};
      if(ci===0 && sp.tree){ cell.hasCaret=true; cell.caretOk=has; cell.caretNo=!has; const open=!!exp[r.id]||(g2filtering(st)&&has);
        cell.caretSym=open?'▾':'▸'; cell.caretLabel=(open?'Recolher ':'Expandir ')+g2text(r,c);
        cell.toggle=()=>{ const x=Object.assign({},g2st(self,id).x||sp.x0||{}); x[r.id]=!x[r.id]; g2set(self,id,{x}); }; }
      else { cell.hasCaret=false; }
      cells.push(cell); });
    if(sp.del){ const asking=(st.cf===r.id); cells.push({isSel:false,isData:false,isDel:true,asking,notAsking:!asking,st:'padding:4px 10px;white-space:nowrap;',
        delLabel:'Excluir '+g2text(r,sp.cols[0]), ask:()=>g2set(self,id,{cf:r.id}), no:()=>g2set(self,id,{cf:null}),
        yes:()=>{ const rs=g2clone(g2rows(self,sp)); const rm=(list)=>{ const i=list.findIndex(x=>x.id===r.id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&rm(x.kids)); }; rm(rs); g2set(self,id,{rows:rs,cf:null}); self.setState({g2toast:'Excluído: '+g2text(r,sp.cols[0])}); if(self.g2after) self.g2after(id,rs,null); }}); }
    const canOpen=editable && !(ed.leafOnly && has);
    return {id:r.id, cls:'g2r'+(canOpen?' g2ed':'')+(st.fl===r.id?' g2flash':'')+(lvl>0?' g2kid':''), tab:canOpen?'0':'-1',
      open:(e)=>{ if(canOpen) g2open(self,sp,r.id,e); }, key:(e)=>{ if(canOpen && e && (e.key==='Enter'||e.key===' ')){ e.preventDefault(); g2open(self,sp,r.id,null); } }, cells}; });
  v[id+'_count']=flat.filter(x=>x.lvl===0).length; v[id+'_all']=rows.length;
  v[id+'_empty']=flat.length===0; v[id+'_some']=flat.length>0;
  v[id+'_q']=st.q||''; v[id+'_setq']=(e)=>g2set(self,id,{q:e.target.value});
  v[id+'_filtered']=g2filtering(st); v[id+'_clear']=()=>g2set(self,id,{q:'',f:{}});
  v[id+'_fchips']=Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).map(k=>{ const c=sp.cols.find(x=>x.k===k)||{l:k}; return {t:c.l+': '+st.f[k].join(', '), rm:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[k]; g2set(self,id,{f}); }}; });
  v[id+'_selcount']=Object.values(st.sel||{}).filter(Boolean).length; v[id+'_hassel']=v[id+'_selcount']>0;
  v[id+'_selclear']=()=>g2set(self,id,{sel:{}});
  v[id+'_selall']=()=>{ const s2={}; const allOn=flat.every(x=>(st.sel||{})[x.r.id]); if(!allOn) flat.forEach(x=>{ s2[x.r.id]=true; }); g2set(self,id,{sel:s2}); };
  v[id+'_new']=()=>g2new(self,sp);
  v[id+'_expall']=()=>{ const x={}; const w=(l)=>l.forEach(r=>{ if(r.kids&&r.kids.length){ x[r.id]=true; w(r.kids);} }); w(rows); g2set(self,id,{x}); };
  v[id+'_colall']=()=>g2set(self,id,{x:{}});
  if(total){ v[id+'_tot']=sp.cols.map((c,ci)=>{ const s=c.agg?g2sum(sp,flat,c):null; return {t:(ci===0?'Total':(s===null?'':g2fmt(s,c))), st:'padding:8px 10px;font-weight:800;'+(ci===0?'position:sticky;left:0;z-index:1;background:#F4F6F3;':'')+(c.a==='r'?'text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;':'')}; });
    v[id+'_totopen']=()=>g2set(self,id,{fm:{tot:true,ro:true,mode:'total',draft:{},orig:{},errs:{}},fmc:null}); }
  // formulário lateral
  const fm=st.fm; const F={open:!!fm};
  if(fm){ const r=fm.rid?g2find(rows,fm.rid):null;
    F.isTot=!!fm.tot; F.isRec=!fm.tot;
    F.title=fm.tot?('Composição do total'):(fm.isNew?(ed.newTitle||'Novo registro'):((ed.title?ed.title+' · ':'')+(r?g2text(r,sp.cols[0]):'')));
    F.sub=fm.tot?'Linhas que formam o total, com os filtros atuais. Totais são calculados: altere os registros de origem.':(fm.ro?(fm.mode==='origin'?'Valor calculado — consulte a origem abaixo. Para mudar, altere o registro de origem.':(r&&r.ro?'Consulta: você não tem permissão para editar este registro.':'Consulta')):(ed.sub||'Altere os campos e salve. Os cálculos da tabela são refeitos ao salvar.'));
    F.ro=!!fm.ro; F.edit=!fm.ro; F.warn=!!fm.warn;
    F.items=fm.tot? flat.filter(x=>x.lvl===0).map(x=>({t:g2text(x.r,sp.cols[0]), v:sp.cols.filter(c=>c.agg).map(c=>c.l+': '+g2text(x.r,c)).join(' · ')})):[];
    F.origins=(r&&r.o)?r.o.map(o=>({t:o.t,h:o.h||'#',isLink:!!o.h,isTxt:!o.h})):[]; F.hasOrigins=F.origins.length>0;
    const visf=(ed.fields||[]).filter(f=>!f.cond || String(fm.draft[f.cond.k])===String(f.cond.eq));
    F.fields=fm.tot?[]:visf.map(f=>{ let val=fm.draft[f.k]; if(f.live&&self.g2live){ const lv=self.g2live(id,f.k,fm.draft); if(lv!==undefined&&lv!==null) val=lv; } const err=(fm.errs||{})[f.k]; const dis=!!fm.ro||!!f.ro||(!!f.newOnly&&!fm.isNew); const mv=(String(val||'').split(';').map(x=>x.trim()).filter(Boolean));
      return {l:f.l, fid:'fx_'+id+'_'+f.k, isSel:f.t==='sel', isMulti:f.t==='multi', isTxt:(f.t!=='sel'&&f.t!=='area'&&f.t!=='multi'), isArea:f.t==='area', type:(f.t==='date'?'date':(f.t==='email'?'email':(f.t==='tel'?'tel':'text'))),
        mopts:(f.t==='multi'?(f.opts||[]).map(o=>({t:o,on:mv.indexOf(o)>=0,dis,tog:()=>{ const cur=g2st(self,id).fm; if(!cur||dis) return; let a=String(cur.draft[f.k]||'').split(';').map(x=>x.trim()).filter(Boolean); const i=a.indexOf(o); if(i>=0) a.splice(i,1); else a.push(o); const d=Object.assign({},cur.draft,{[f.k]:a.join('; ')}); const er=Object.assign({},cur.errs||{}); delete er[f.k]; g2set(self,id,{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }})):[]), v:(val===undefined?'':val), u:f.u||'', hasU:!!f.u, help:f.help||'', hasHelp:!!f.help,
        dis, err:!!err, errMsg:err||'', ist:'font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;border:1px solid '+(err?'#B42318':'#E4E9E5')+';background:'+(dis?'#F4F6F3':'#FFFFFF')+';color:#15201A;',
        opts:(f.opts||[]).map(o=>({v:o,t:o})),
        set:(e)=>{ const cur=g2st(self,id).fm; if(!cur) return; const d=Object.assign({},cur.draft,{[f.k]:e.target.value}); const er=Object.assign({},cur.errs||{}); delete er[f.k]; g2set(self,id,{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }}; });
    F.nerr=Object.keys(fm.errs||{}).length; F.hasErr=F.nerr>0;
    F.save=()=>g2save(self,sp); F.cancel=()=>g2close(self,sp); F.close=()=>g2close(self,sp);
    F.discard=()=>g2set(self,id,{fm:null}); F.keep=()=>{ const cur=g2st(self,id).fm; g2set(self,id,{fm:Object.assign({},cur,{warn:false})}); };
    F.key=(e)=>{ if(e && e.key==='Escape'){ e.preventDefault(); g2close(self,sp); } };
  }
  v[id+'_F']=F; }
function g2navvals(self,v,nav){ (nav||[]).forEach((m,i)=>{ const o=(self.state.nav||{}); const open=(o[i]===undefined)?!!m.open:!!o[i];
  v['nav'+i+'_open']=open; v['nav'+i+'_sym']=open?'▾':'▸'; v['nav'+i+'_tog']=()=>{ const n=Object.assign({},self.state.nav||{}); n[i]=!open; self.setState({nav:n}); }; }); }

// faixa de etapas controlada pelo estado da tela (processos numa só tela de trabalho)
function g2steps(self,v,pre,n,cur,whys,go){ for(let i=1;i<=n;i++){ const on=(i===cur); const w=(whys&&whys[i])||'';
  v[pre+i+'_st']='display:flex;align-items:center;gap:7px;padding:5px 8px;border-radius:10px;border:0;font-family:inherit;cursor:pointer;text-align:left;min-width:0;color:#15201A;'+(on?'background:#E4F3E9;box-shadow:inset 0 -2px 0 #1E7A4C;':'background:transparent;');
  v[pre+i+'_bst']='width:22px;height:22px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:800;flex-shrink:0;'+(on?'background:#1E7A4C;color:#fff;':(w?'background:#FDE8E6;color:#B42318;':'background:#EEF1EE;color:#15201A;'));
  v[pre+i+'_tst']='font-size:12.5px;line-height:1.2;font-weight:'+(on?'800':'600')+';';
  v[pre+i+'_why']=w; v[pre+i+'_hasWhy']=!!w; v[pre+i+'_cur']=on?'step':'false';
  v[pre+i+'_go']=()=>go(i); } }
