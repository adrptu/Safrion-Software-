// ===== SAF-MAPA · Planejar a safra no mapa (proprietário, 18/10/2026: "Em planejar safra coloque o modo de visão mapa para ver
// geograficamente como está o plano da safra e permita clicar nos talhões e fazer todo o trabalho"; especificação docs/integracao/V71/SAF-MAPA.md)
// A visão Mapa é a segunda visão do MESMO estado do "Editar talhões…" (EDL-01, safra_lote.js): tocar no talhão marca as linhas dele (sl.sel),
// o painel "Planejar N talhões" é a faixa "Aplicar aos marcados" (slAplicar, as mesmas recusas por talhão) e "Salvar alterações" é o slGravar
// (atômico por fazenda, chave do comando gerada ao abrir). O mapa colore pelo rascunho (sl.vals): Tabela e Mapa mostram o mesmo. Nenhuma regra
// nova; a geometria vem de geo_talhoes.py (a mesma do Mapa IN-04). SM_GEO e SM_IDX vêm do build (saf_lote.mapa_dados).

// >>> SM-PURO (sem estado da tela)
// cor da cultura: fixa por cultura conhecida; as outras pela posição no cadastro (paleta estável)
const SM_CULT={Soja:'#D9A62E','Milho':'#E07B39','Feijão':'#9C6B4E','Café':'#7B4A2D','Mamão Formosa':'#3F9E5A','Algodão':'#A9B4BF','Trigo':'#C9A35C','Sorgo':'#B5523B'};
const SM_PAL=['#5B8DB8','#8E6CB8','#3E9C9C','#C26B91','#7FA33B','#B88A3E','#4F6FA6','#A65B5B'];
const SM_VERDES=['#E4F3E9','#BFE3CC','#94CFA9','#66B886','#3F9E65','#257A4B','#14532F'];
function smCorCult(c,culturas){ if(!c) return null; if(SM_CULT[c]) return SM_CULT[c]; const i=Math.max(0,(culturas||[]).indexOf(c)); return SM_PAL[i%SM_PAL.length]; }
function smCorPlano(id,planos){ const i=(planos||[]).findIndex(p=>p.id===id); return i<0?null:SM_PAL[i%SM_PAL.length]; }
// semana do plantio desde o início da safra (0..6+), para a rampa de verdes
function smSemana(plantio,ini){ if(!plantio||!ini) return null; const d=(Date.parse(plantio)-Date.parse(ini))/864e5; if(!isFinite(d)) return null; return Math.max(0,Math.floor(d/7)); }
// texto contrastante sobre a cor de fundo (luminância relativa simples)
function smTinta(hex){ const h=String(hex||'#FFFFFF').replace('#',''); if(h.length!==6) return '#15201A'; const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16);
  return (0.299*r+0.587*g+0.114*b)>150?'#15201A':'#FFFFFF'; }
// resumo de um talhão a partir das linhas do EDL-01 (tal, par, vinc, novo, ro) e do rascunho: o que ele mostra e quem pode ser marcado
function smTalhao(ls,vals,base){ const eds=ls.filter(l=>l.tipo!=='grp'&&l.tipo!=='ro'); const ro=ls.find(l=>l.tipo==='ro')||null;
  const cults=eds.map(l=>vals[l.k]||{}).filter(v=>String(v.cult||'').trim());
  const v0=cults[0]||null; const par=eds.filter(l=>l.tipo==='par').length;
  const mud=eds.some(l=>SL_COLS.some(c=>slMudou(vals[l.k],base[l.k],c)));
  return {eds,ro,v0,par,mud,semCult:!cults.length,semPlano:cults.some(v=>!String(v.plano||'').trim()),cults}; }
// <<< SM-PURO

// área de uma linha do EDL-01 (rascunho, senão a base), em ha
function smHa(l,vals){ const a=String(((vals||{})[l.k]||l.base||{}).area||'').replace(',','.'); const n=Number(a); return isFinite(n)?n:0; }
function smSet(self,patch){ const cur=self.state.sl; if(!cur) return; self.setState({sl:Object.assign({},cur,patch)}); }
function smMarcar(self,ks,on){ const cur=self.state.sl; if(!cur) return; const s=Object.assign({},cur.sel); ks.forEach(k=>{ if(on) s[k]=true; else delete s[k]; }); self.setState({sl:Object.assign({},cur,{sel:s,info:''})}); }
function smVals(self,v){ const sl=self.state.sl; const lins=self.__slLin||[];
  const vista=sl.vista==='mapa'?'mapa':'tabela'; v.sl_vTab=vista==='tabela'; v.sl_vMapa=vista==='mapa';
  // VIS-08: seletor pelo ícone (engine.visoes_locais 'sl', visões lista e mapa); a Tabela do painel é a visão 'lista' do registro
  [['lista','tabela'],['mapa','mapa']].forEach(([k,x])=>{ v['sl_lv_'+k+'_p']=String(vista===x); v['sl_lv_'+k+'_go']=()=>smSet(self,{vista:x,info:''}); });
  const G=SM_GEO[sl.faz]||null; v.sm_temGeo=!!G;
  Object.keys(SM_GEO).forEach(f=>{ v['sm_f_'+SM_FK[f]]=v.sl_vMapa&&f===sl.faz; });
  if(!v.sl_vMapa){ return; }
  const ctx=slCtx(self,sl.saf); const so=safById(self,sl.saf)||{v:{}}; const ini=so.v.ini||'';
  const porT={}; lins.forEach(l=>{ (porT[l.t]=porT[l.t]||[]).push(l); });
  const cor=sl.cor||'cult'; const leg={};
  const addLeg=(k,c,t,ha)=>{ const x=leg[k]=leg[k]||{c,t,ha:0,ord:Object.keys(leg).length}; x.ha+=ha; };
  const resumo={};   // talhão → {S, area, sel, fill, ...}
  Object.keys(porT).forEach(t=>{ const S=smTalhao(porT[t],sl.vals,sl.base); const area=talhaoArea(t)||porT[t].reduce((a,l)=>a+(l.T||0),0);
    // seleção por linha (sl.sel é a fonte única): inteiro, em parte (parcela marcada na Tabela) ou nada. Em parte aparece como tal e conta só
    // as linhas e a área marcadas: o "Aplicar" anuncia exatamente o que vai mudar (Codex 6252809331, S2)
    const selE=S.eds.filter(l=>sl.sel[l.k]); const sel=S.eds.length>0&&selE.length===S.eds.length; const parc=selE.length>0&&!sel;
    let fill='#FFFFFF', dash='6 5', rotC='Sem cultivo';
    if(S.ro){ fill='#D9DED9'; dash=''; rotC=S.ro.sit.t; addLeg('ro','#D9DED9','Indisponível nesta safra',area); }
    else if(S.semCult){ addLeg('sem','#FFFFFF','Sem cultivo',area); }
    else { dash=''; const v0=S.v0; rotC=v0.cult+(v0.var?' · '+v0.var:'');
      if(cor==='cult'){ fill=smCorCult(v0.cult,ctx.culturas)||'#A9B4BF'; addLeg('c:'+v0.cult,fill,v0.cult,area); }
      else if(cor==='plano'){ const pc=v0.plano?smCorPlano(v0.plano,ctx.planos):null; if(pc){ fill=pc; const p=ctx.planos.find(x=>x.id===v0.plano); addLeg('p:'+v0.plano,fill,p?p.nome+' v'+p.versao:v0.plano,area); } else { fill='#F2C94C'; addLeg('semp','#F2C94C','Sem plano',area); } }
      else if(cor==='plantio'){ const w=smSemana(v0.plantio,ini); if(w===null){ fill='#FFFFFF'; dash='6 5'; addLeg('semd','#FFFFFF','Sem data de plantio',area); } else { const i=Math.min(SM_VERDES.length-1,w); fill=SM_VERDES[i]; addLeg('w:'+i,fill,i===SM_VERDES.length-1?('Semana '+(i+1)+' ou depois'):('Semana '+(i+1)+' da safra'),area); } }
      else { const L=S.eds[0]; const cc=(G2C[(L.sit||{}).c]||G2C.gray)[1]; fill=cc; addLeg('s:'+(L.sit||{}).t,cc,(L.sit||{}).t||'—',area); } }
    if(cor==='sit'&&(S.ro||S.semCult)){ const L=S.ro||S.eds[0]; if(L){ fill=(G2C[(L.sit||{}).c]||G2C.gray)[1]; } }
    const pl=S.v0&&S.v0.plano?ctx.planos.find(x=>x.id===S.v0.plano):null;
    const rotP=S.ro?'':(S.semCult?'':(pl?pl.nome:'Sem plano'));
    const haSel=sel?area:selE.reduce((a,l)=>a+smHa(l,sl.vals),0);
    const parT=parc?('em parte: '+selE.map(l=>l.rot).join(', ')+' ('+selE.length+' de '+S.eds.length+')'):'';
    resumo[t]={S,area,sel,parc,selE,haSel,parT,fill,dash,rotC,rotP}; });
  // o que o "Salvar alterações" recusou (sl.err por linha): no mapa o talhão fica com contorno vermelho e "A corrigir", e o painel lista o que
  // corrigir com um toque que marca o talhão (resolver onde o problema aparece; antes a recusa só aparecia na Tabela)
  const SM_COLN={cult:'Cultura',var:'Variedade',plano:'Plano',plantio:'Plantio',meta:'Meta',area:'Área'};
  const errT={}; Object.keys(porT).forEach(t=>porT[t].forEach(l=>{ const e=(sl.err||{})[l.k]; if(e) Object.keys(e).forEach(c=>{ if(e[c]) (errT[t]=errT[t]||[]).push((SM_COLN[c]||c)+': '+String(e[c]).replace(/\.$/,'')); }); }));
  // desenho fixo do build (um <g> por talhão com contorno): cor, rótulo, seleção, marca de alterado e a ação
  SM_IDX.forEach(x=>{ const P='smt'+x.i; const R=resumo[x.t]; const on=!!R&&x.faz===sl.faz;
    if(!on){ v[P+'_fill']='#FFFFFF'; v[P+'_stk']='#C8D0CA'; v[P+'_sw']='1'; v[P+'_dash']=''; v[P+'_l2']=''; v[P+'_tc']='#5B6660'; v[P+'_th']='#FFFFFF'; v[P+'_sel']='false'; v[P+'_mud']='0';
      v[P+'_al']=x.t+' · fora desta safra'; v[P+'_go']=()=>{}; v[P+'_key']=()=>{}; return; }
    const S=R.S; const ks=S.eds.map(l=>l.k);
    v[P+'_fill']=R.fill; v[P+'_stk']=(R.sel||R.parc)?'#1E7A4C':(S.mud?'#8A5A00':'#5B6660'); v[P+'_sw']=R.sel?'4':(R.parc?'3':(S.mud?'2.5':'1.2')); v[P+'_dash']=R.parc?'5 3':R.dash;
    v[P+'_l2']=S.ro?'Indisponível':(S.semCult?'Sem cultivo':(S.par?(S.par+' parcelas'):(S.v0.cult+(S.semPlano?' · sem plano':''))));
    v[P+'_tc']=smTinta(R.fill); v[P+'_th']=smTinta(R.fill)==='#FFFFFF'?'rgba(0,0,0,.35)':'rgba(255,255,255,.85)';
    v[P+'_sel']=R.sel?'true':(R.parc?'mixed':'false'); v[P+'_mud']=S.mud?'1':'0';
    if(R.parc) v[P+'_l2']='Em parte · '+R.selE.length+' de '+S.eds.length;
    if(errT[x.t]&&!R.sel&&!R.parc){ v[P+'_stk']='#B42318'; v[P+'_sw']='3.5'; v[P+'_dash']=''; }
    if(errT[x.t]) v[P+'_l2']='A corrigir';
    v[P+'_al']=x.t+' · '+nfa(R.area)+' ha · '+R.rotC+(R.rotP?' · '+R.rotP:'')+(S.ro?' · '+(S.ro.motivoRo||''):'')+(S.mud?' · alterado, não salvo':'')+(errT[x.t]?' · a corrigir: '+errT[x.t].join('; '):'')+(R.sel?' · marcado':(R.parc?' · marcado '+R.parT+'; tocar marca o talhão inteiro':''));
    const tog=()=>{ if(S.ro||!ks.length){ smSet(self,{info:x.t+': '+((S.ro&&S.ro.motivoRo)||'não pode ser planejado nesta safra.')}); return; } smMarcar(self,ks,!R.sel); };
    v[P+'_go']=tog; v[P+'_key']=(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); tog(); } }; });
  // 2ª linha do rótulo numa camada HTML sobre o desenho: texto ligado dentro de <text> não aparece (o motor o envolve em <span>; EX-55 F1)
  Object.keys(SM_FK).forEach(f=>{ v['sm_lbl_'+SM_FK[f]]=f!==sl.faz?[]:SM_IDX.filter(x=>x.faz===f&&v['smt'+x.i+'_l2']).map(x=>{ const P='smt'+x.i;
    return {k:x.t,t:v[P+'_l2'],st:'left:'+x.px+'%;top:'+x.py+'%;color:'+v[P+'_tc']+';text-shadow:0 0 3px '+(v[P+'_tc']==='#FFFFFF'?'rgba(0,0,0,.55)':'rgba(255,255,255,.95)')+';'}; }); });
  // talhões sem contorno no mapa (B1 da Boa Vista, talhão novo do cadastro): selecionáveis aqui
  const comGeo=new Set(SM_IDX.filter(x=>x.faz===sl.faz).map(x=>x.t));
  v.sm_sem=Object.keys(resumo).filter(t=>!comGeo.has(t)).map(t=>{ const R=resumo[t]; const ks=R.S.eds.map(l=>l.k);
    return {t,sub:R.rotC+(R.rotP?' · '+R.rotP:'')+(R.parc?' · '+R.parT:''),on:R.sel?'true':(R.parc?'mixed':'false'),al:(R.sel?'Desmarcar ':(R.parc?'Marcar inteiro ':'Marcar '))+t,
      st:'min-height:40px;padding:4px 12px;border-radius:10px;font:inherit;font-size:12.5px;cursor:pointer;text-align:left;border:'+(R.sel?'2px solid #1E7A4C':'1px dashed #8A968E')+';background:'+R.fill+';color:'+smTinta(R.fill)+';',
      go:()=>{ if(R.S.ro||!ks.length){ smSet(self,{info:t+': '+((R.S.ro&&R.S.ro.motivoRo)||'não pode ser planejado nesta safra.')}); return; } smMarcar(self,ks,!R.sel); }}; });
  v.sm_temSem=v.sm_sem.length>0; v.sm_desenhar=sl.faz==='Lagoa Grande'?'IN-04.dc.html#importar':'IN-04.dc.html';
  // legenda: classe, cor e área
  v.sm_leg=Object.values(leg).sort((a,b)=>a.ord-b.ord).map(x=>({t:x.t,ha:nfa(r2(x.ha))+' ha',st:'display:inline-block;width:14px;height:14px;border-radius:4px;flex-shrink:0;border:1px '+(x.c==='#FFFFFF'?'dashed #8A968E':'solid rgba(0,0,0,.12)')+';background:'+x.c+';'}));
  v.sm_cores=[['cult','Cultura'],['plano','Plano'],['plantio','Plantio'],['sit','Situação']].map(([k,t])=>({t,on:String(cor===k),go:()=>smSet(self,{cor:k}),
    st:'padding:0 12px;border-radius:999px;font:inherit;font-size:12.5px;font-weight:700;cursor:pointer;border:1px solid '+(cor===k?'#1E7A4C;background:#E4F3E9;color:#1E7A4C;':'#E4E9E5;background:#FFFFFF;color:#15201A;')}));
  // atalhos de seleção (um toque); Esc limpa a seleção antes de fechar o painel
  const todosT=Object.keys(resumo).filter(t=>!resumo[t].S.ro&&resumo[t].S.eds.length);
  const marcarSo=(ts)=>{ const s={}; ts.forEach(t=>resumo[t].S.eds.forEach(l=>{ s[l.k]=true; })); smSet(self,{sel:s,info:''}); };
  const culturas=[...new Set(todosT.map(t=>resumo[t].S.v0&&resumo[t].S.v0.cult).filter(Boolean))];
  v.sm_atalhos=[{t:'Todos',go:()=>marcarSo(todosT)},{t:'Sem cultivo',go:()=>marcarSo(todosT.filter(t=>resumo[t].S.semCult))},{t:'Sem plano',go:()=>marcarSo(todosT.filter(t=>!resumo[t].S.semCult&&resumo[t].S.semPlano))}]
    .concat(culturas.map(c=>({t:c,go:()=>marcarSo(todosT.filter(t=>resumo[t].S.v0&&resumo[t].S.v0.cult===c))})))
    .concat([{t:'Limpar',go:()=>smSet(self,{sel:{},info:''})}]).map(x=>Object.assign(x,{al:x.t==='Limpar'?'Limpar a seleção':'Marcar: '+x.t}));
  v.sm_err=Object.keys(errT).map(t=>({t,msg:errT[t].join(' · '),al:'Marcar '+t+' para corrigir: '+errT[t].join('; '),go:()=>marcarSo([t])}));
  v.sm_temGerr=!!sl.gerr; v.sm_gerr=sl.gerr||''; v.sm_temErr=v.sm_err.length>0||v.sm_temGerr;
  const selT=Object.keys(resumo).filter(t=>resumo[t].sel||resumo[t].parc); const selHa=selT.reduce((a,t)=>a+resumo[t].haSel,0);
  const nParc=selT.filter(t=>resumo[t].parc).length; const emParte=nParc?' ('+nParc+' em parte)':'';
  const selK={}; selT.forEach(t=>resumo[t].selE.forEach(l=>{ selK[l.k]=true; }));
  v.sm_n=selT.length; v.sm_cont=selT.length?(selT.length+(selT.length>1?' talhões':' talhão')+emParte+' · '+nfa(r2(selHa))+' ha'):'Nenhum talhão marcado';
  v.sm_tit=selT.length?('Planejar '+selT.length+(selT.length>1?' talhões':' talhão')):'Planejar talhões'; v.sm_vazio=!selT.length; v.sm_tem=selT.length>0;
  v.sm_apT=selT.length?('Aplicar a '+selT.length+(selT.length>1?' talhões':' talhão')+emParte):'Aplicar'; v.sm_apSt=selT.length?'':'opacity:.55;cursor:not-allowed;';
  v.sm_selL=selT.map(t=>({t,sub:resumo[t].rotC+(resumo[t].rotP?' · '+resumo[t].rotP:'')+(resumo[t].parc?' · '+resumo[t].parT:''),al:'Tirar '+t+' da seleção',go:()=>smMarcar(self,resumo[t].S.eds.map(l=>l.k),false)}));
  // um talhão marcado: os atalhos da linha da tabela (paridade, M13)
  const um=selT.length===1&&!nParc?resumo[selT[0]]:null; const t1=um?selT[0]:''; const L1=um?um.S.eds[0]:null;
  const cult1=L1&&L1.id?cultsDe(self,sl.saf).find(c=>c.id===L1.id):null; const pl1=cult1?planById(cult1.v.plano):null;
  v.sm_um=!!um; v.sm_umT=t1;
  v.sm_acoes=um?[].concat(cult1&&pl1&&pl1.cultura===cult1.v.cult?[{t:'Ajustar insumos e doses ›',al:'Ajustar insumos e doses de '+cult1.v.local,go:()=>slSair(self,()=>openLP(self,cult1.id))}]:[])
      .concat(!um.S.ro&&!(L1&&L1.tipo==='vinc')?[{t:'Dividir '+t1+' em parcelas ›',al:'Dividir '+t1+' em parcelas',go:()=>slSair(self,()=>openDiv(self,t1))}]:[])
      .concat([{t:'Ver na tabela',al:'Ver '+t1+' na tabela',go:()=>{ smSet(self,{vista:'tabela'}); setTimeout(()=>{ try{ const el=document.querySelector('#sl-grade [data-l="'+(L1?L1.k:'')+'"]'); if(el){ el.scrollIntoView({block:'center'}); el.focus({preventScroll:true}); } }catch(e){} },60); }}]):[];
  v.sm_aplicar=()=>{ if(!selT.length){ smSet(self,{info:'Toque nos talhões no mapa para marcar.'}); return; } slAplicar(self,selK); };
  // Esc no mapa: limpa a seleção primeiro; sem seleção, o Esc do painel (fechar, com aviso se houver alteração)
  const escPainel=v.sl_key; v.sl_key=(e)=>{ if(e&&e.key==='Escape'&&selT.length&&self.state.sl&&self.state.sl.vista==='mapa'){ e.preventDefault(); smSet(self,{sel:{}}); return; } if(escPainel) escPainel(e); };
}
