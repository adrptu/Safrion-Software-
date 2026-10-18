// EX-55 F1 · mapa embutido: preenche o desenho de mapa_emb.py. O adaptador da tela entrega, por talhão do recorte, a classe do Mapa
// (mapa_camadas.js · MC_COR), o rótulo curto, a dica com 3 ou 4 valores e a ação. Talhão fora do recorte fica neutro, sem foco e
// sem ação; "sem dado" (classe none) fica em hachura e conta na legenda. O mapa nunca aprova nem libera: a ação é a da própria tela.
function meTinta(hex){ const h=String(hex||'#FFFFFF').replace('#',''); if(h.length!==6) return '#15201A';
  const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16); return (0.299*r+0.587*g+0.114*b)>150?'#15201A':'#FFFFFF'; }
// porT: {talhão: {c, l2, al, go}}; o: {foraTxt, leg:[{k,t}]}
function meVals(v,pref,ME,faz,porT,o){ o=o||{}; const G=ME.geo[faz]||null; const cont={};
  if(v[pref+'_temRec']===undefined){ v[pref+'_temRec']=false; v[pref+'_rec']=[]; v[pref+'_recLimpar']=()=>{}; }
  Object.keys(ME.fk).forEach(f=>{ v[pref+'_f_'+ME.fk[f]]=f===faz; });
  v[pref+'_esq']=!!(G&&G.esq);
  ME.idx.forEach(x=>{ const P=pref+'t'+x.i, R=x.faz===faz?porT[x.t]:null;
    if(!R){ v[P+'_fill']='#FFFFFF'; v[P+'_stk']='#C8D0CA'; v[P+'_sw']='1'; v[P+'_dash']='4 3'; v[P+'_hach']='0'; v[P+'_l2']=''; v[P+'_c']='fora';
      v[P+'_tc']='#8A968E'; v[P+'_th']='#FFFFFF'; v[P+'_tab']='-1'; v[P+'_al']=x.t+' · '+(o.foraTxt||'fora do recorte'); v[P+'_go']=()=>{}; v[P+'_key']=()=>{}; return; }
    const sem=R.c==='none', cor=sem?'#FFFFFF':((typeof MC_COR!=='undefined'&&MC_COR[R.c])||['#C9CFCB'])[0], tc=meTinta(cor);
    v[P+'_fill']=cor; v[P+'_stk']='#5B6660'; v[P+'_sw']='1.2'; v[P+'_dash']=''; v[P+'_hach']=sem?'1':'0'; v[P+'_l2']=R.l2||''; v[P+'_c']=R.c;
    v[P+'_tc']=tc; v[P+'_th']=tc==='#FFFFFF'?'rgba(0,0,0,.35)':'rgba(255,255,255,.85)'; v[P+'_tab']='0'; v[P+'_al']=R.al;
    v[P+'_go']=R.go; v[P+'_key']=(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); R.go(); } };
    cont[R.c]=(cont[R.c]||0)+1; });
  // 2ª linha do rótulo: camada HTML sobre o desenho (texto ligado dentro de <text> não aparece: o motor o envolve em <span>)
  Object.keys(ME.fk).forEach(f=>{ v[pref+'_lbl_'+ME.fk[f]]=f!==faz?[]:ME.idx.filter(x=>x.faz===f&&porT[x.t]&&porT[x.t].l2).map(x=>{ const P=pref+'t'+x.i;
    return {k:x.t,t:porT[x.t].l2,st:'left:'+x.px+'%;top:'+x.py+'%;max-width:'+Math.max(8,Math.min(24,(x.pw||24)*0.9)).toFixed(1)+'%;color:'+v[P+'_tc']+';text-shadow:0 0 3px '+(v[P+'_tc']==='#FFFFFF'?'rgba(0,0,0,.55)':'rgba(255,255,255,.95)')+';'}; }); });
  v[pref+'_leg']=(o.leg||[]).filter(x=>x.k).map(x=>{ const sem=x.k==='none', cor=sem?'#FFFFFF':((typeof MC_COR!=='undefined'&&MC_COR[x.k])||['#C9CFCB'])[0];
    return {t:x.t,n:String(cont[x.k]||0),st:'display:inline-block;width:14px;height:14px;border-radius:4px;flex-shrink:0;border:1px '+(sem?'dashed #8A968E;background:repeating-linear-gradient(45deg,#FFFFFF 0 3px,#C9CFCB 3px 4px)':'solid rgba(0,0,0,.12);background:'+cor)+';'}; });
  return cont; }
// linhas folha visíveis da grade (filtro rápido, busca e filtros de coluna; grupos descem aos filhos): o mapa pinta só o que a Tabela mostra
function meVisiveis(self,sp,gid){ const st=g2st(self,gid), out=new Set();
  const vai=l=>(l||[]).forEach(r=>{ if(r.kids&&r.kids.length) vai(r.kids); else if(g2match(r,sp,st)) out.add(String(r.id)); });
  vai(g2qrows(sp,st,sp.rows||[])); return out; }
// o mesmo recorte em chips removíveis acima do mapa (VISOES-2 §8): sem eles, a busca feita na Tabela ficaria escondida na visão Mapa
function meRecorte(self,v,pref,sp,gid){ const st=g2st(self,gid), rch=[], lab=(c,x)=>x==='(vazio)'?'vazio':((typeof g2flab==='function'&&g2flab(sp.rows||[],c,x))||String(x));
  if(sp.qf&&st.qv) rch.push({t:sp.qf.l+': '+st.qv,lab:'Remover filtro '+sp.qf.l,rm:()=>g2set(self,gid,{qv:''})});
  Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).forEach(k=>{ const c=sp.cols.find(x=>x.k===k)||{k,l:k}; const t=c.l+': '+st.f[k].map(x=>lab(c,x)).join(', ');
    rch.push({t,lab:'Remover filtro '+t,rm:()=>{ const f=Object.assign({},g2st(self,gid).f||{}); delete f[k]; g2set(self,gid,{f,fmc:null}); }}); });
  if((st.q||'').trim()) rch.push({t:'Busca: “'+st.q.trim()+'”',lab:'Limpar a busca',rm:()=>g2set(self,gid,{q:''})});
  v[pref+'_temRec']=rch.length>0; v[pref+'_rec']=rch; v[pref+'_recLimpar']=()=>g2set(self,gid,{q:'',f:{},qv:'',fmc:null});
  return rch.length>0; }
