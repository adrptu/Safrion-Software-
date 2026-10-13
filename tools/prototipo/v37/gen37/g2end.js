// ===== CADUX · seleção que abre detalhe (SEL-01, SEL-02, DS-41, DS-60): endereço, mestre e teclado =====
// Mestre (lista curta dos grupos) → detalhe do grupo (filhos já listados) → painel do item (o aside do _g2form em consulta). Só as telas que
// chamam cadMD() usam isto; as demais telas não mudam. O endereço guarda a seleção (#faz=SR&talhao=T2&aba=talhoes): o valor é sempre o id.
// pushState só quando abre um nível (o painel e, abaixo de 1024 px, o detalhe do grupo): o voltar do navegador ou do Android sobe um nível;
// trocar de grupo no computador, aba, busca e filtro usam replaceState. Registro indisponível (inexistente ou fora da permissão) abre a lista
// com aviso visível e acessível e uma saída, sem selecionar outro registro e sem dizer se ele existe.
function cadHashLe(h){ const o={}; String(h===undefined?(location.hash||''):h).replace(/^#/,'').split('&').forEach(p=>{ if(!p) return; const i=p.indexOf('=');
  const k=i<0?p:p.slice(0,i); let x=i<0?'':p.slice(i+1); try{ x=decodeURIComponent(x); }catch(e){} o[k]=x; }); return o; }
function cadHashTxt(o){ return Object.keys(o).filter(k=>o[k]!==undefined&&o[k]!==null&&o[k]!=='').map(k=>k+'='+encodeURIComponent(o[k])).join('&'); }
// grava o endereço: nivel 'g' (detalhe do grupo no celular) ou 'i' (painel do item) empilha; sem nível, troca a entrada atual
function cadHashPoe(self,o,nivel){ const h=cadHashTxt(o); const url=location.pathname+location.search+(h?'#'+h:'');
  if(('#'+h)===(location.hash||'#')||(!h&&!location.hash)){ self.__cadHash=h; return; }
  try{ if(nivel) history.pushState({cadux:nivel},'',url); else history.replaceState(history.state,'',url); }catch(e){} self.__cadHash=h; }
function cadLarga(){ try{ return window.matchMedia('(min-width: 1024px)').matches; }catch(e){ return true; } }
function cadFoco(sel,t){ setTimeout(()=>{ try{ const e=typeof sel==='string'?document.querySelector(sel):sel; if(e){ if(!e.matches('a,button,input,select,textarea,[tabindex]')) e.setAttribute('tabindex','-1'); e.focus({preventScroll:false}); } }catch(x){} },t||60); }
// contexto da fazenda entre telas (X-CTX da NAV): só vale a fazenda escolhida num seletor (esc:true); os Cadastros só leem, nunca gravam
function cadCtxFaz(){ try{ const c=JSON.parse(sessionStorage.getItem('mapa-ctx')||'null'); return (c&&c.esc&&c.mf_faz&&c.mf_faz!=='Todas')?c.mf_faz:''; }catch(e){ return ''; } }
// recorte da tela guardado na sessão (busca do mestre, filtro rápido, aba): voltar de outra tela (CD-01det, Estoque) acha a lista como estava
function cadKeepLe(k){ try{ return JSON.parse(sessionStorage.getItem('cadux:'+String(location.pathname).split('/').pop()+':'+k)||'null'); }catch(e){ return null; } }
function cadKeepPoe(k,x){ try{ sessionStorage.setItem('cadux:'+String(location.pathname).split('/').pop()+':'+k,JSON.stringify(x)); }catch(e){} }

// ---- mestre: lista de botões com um só ponto de Tab (aria-current no escolhido); ↑/↓ movem o foco, Enter ou Espaço escolhem, Home/End ----
function cadMestreTecla(self,e){ const k=e&&e.key; if(['ArrowDown','ArrowUp','Home','End'].indexOf(k)<0) return; const bs=[...document.querySelectorAll('.cmd-lista .cmd-it')].filter(b=>b.getClientRects().length);
  if(!bs.length) return; e.preventDefault(); const i=bs.indexOf(document.activeElement); let n=k==='Home'?0:(k==='End'?bs.length-1:(i<0?0:i+(k==='ArrowDown'?1:-1)));
  n=Math.max(0,Math.min(bs.length-1,n)); bs.forEach((b,j)=>b.tabIndex=(j===n?0:-1)); bs[n].focus(); }
// itens: [{id, t, sub, n (contagem), res (texto da pendência), cor, tit (título de seção, sem ação), inat}]
// o: {rotulo, todos:{t,sub,n}|null, sel ('' = Todos), q, inatN, escolhe(id), anuncio}
function cadMestreVals(self,v,o){ const sel=o.sel; const its=[]; const st=(c)=>'color:'+((CADT[c]||CADT.gray)[0])+';';
  if(o.todos) its.push({id:'',t:o.todos.t,sub:o.todos.sub||'',n:o.todos.n===undefined?'':String(o.todos.n),res:'',est:'',cur:String(sel===''),item:true,tit:false});
  (o.itens||[]).forEach(x=>{ if(x.tit){ its.push({id:'',t:x.t,sub:'',n:'',res:'',est:'',cur:'false',item:false,tit:true}); return; }
    its.push({id:x.id,t:x.t,sub:x.sub||'',n:x.n===undefined?'':String(x.n),res:x.res||'',est:x.res?st(x.cor||'yellow'):'',cur:String(sel===x.id),item:true,tit:false,inat:!!x.inat}); });
  const cur=its.findIndex(x=>x.item&&x.cur==='true'); const foco=cur>=0?cur:its.findIndex(x=>x.item);
  v.mx_itens=its.map((x,i)=>Object.assign(x,{tab:i===foco?'0':'-1',cls:'cmd-it'+(x.inat?' cmd-inat-it':''),lab:x.t+(x.n?' · '+x.n:'')+(x.res?' · '+x.res:''),go:()=>o.escolhe(x.id)}));
  v.mx_key=(e)=>cadMestreTecla(self,e); v.mx_anuncio=self.state.mx_anuncio||'';
  v.mx_q=self.state.mx_q||''; v.mx_setq=(e)=>{ const q=e.target.value; self.setState({mx_q:q}); cadKeepPoe('q',q); };
  v.mx_qkey=(e)=>{ if(e.key==='Escape'&&(self.state.mx_q||'')){ e.preventDefault(); e.stopPropagation(); self.setState({mx_q:''}); cadKeepPoe('q',''); } };
  v.mx_temInat=!!o.inatN; v.mx_inatT=(self.state.mx_inat?'Ocultar inativas':'Inativas')+' · '+(o.inatN||0); v.mx_inatOn=String(!!self.state.mx_inat); v.mx_inat=()=>self.setState({mx_inat:!self.state.mx_inat});
  v.mx_nivel=cadLarga()?'l':(self.state.mx_nivel||'m'); }
// resultados da busca do mestre abaixo de 1024 px: grupos e itens ("T2 · Santa Rita"); tocar no item abre o painel dele direto
function cadResVals(v,res){ v.mx_res=(res||[]).slice(0,30); v.mx_temRes=v.mx_res.length>0; }

// ---- detalhe do grupo: cabeçalho (o que é · onde · estado), "Ver ficha", Próximo passo e voltar ao mestre no celular ----
function cadDetVals(self,v,o){ v.dx_t=o.t||''; v.dx_sub=o.sub||''; const c=o.chip?(CADT[o.chip.c]||CADT.gray):null; v.dx_temChip=!!c; v.dx_chT=o.chip?o.chip.t:'';
  v.dx_chSt=c?'display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+c[0]+';background:'+c[1]+';':'';
  v.dx_temFicha=!!o.ficha; v.dx_fichaT=o.ficha?o.ficha.t:''; v.dx_ficha=o.ficha?o.ficha.go:(()=>{});
  v.dx_lks=(o.lks||[]).filter(Boolean).map(l=>({t:l.t,h:l.h||'#',isA:!!l.h&&!l.go,isB:!!l.go,go:l.go||(()=>{})})); v.dx_temLks=v.dx_lks.length>0;
  v.dx_p=g2consVals({prox:o.prox||null}); v.dx_voltaT='‹ '+(o.volta||'Voltar'); v.dx_volta=o.voltar||(()=>{});
  // a 390 px o painel do item cobre a tela: "‹ {grupo}" no topo diz de onde veio e volta a ele (ESPECIFICACAO §2.1; achado 11 da revisão)
  if(!cadLarga()) GRIDS.forEach(sp=>{ const F=v[sp.id+'_F']; if(F&&F.open&&F.cons&&!F.temPai){ F.temPai=true; F.paiT='‹ '+(o.t||'Voltar'); F.paiGo=F.close; } });
  v.dx_aviso=o.aviso||''; v.dx_avisoT=(o.avisoSaida&&o.avisoSaida.t)||''; v.dx_avisoGo=(o.avisoSaida&&o.avisoSaida.go)||(()=>{}); v.dx_temAvisoSaida=!!o.avisoSaida;
  // SEL-02 abaixo de 1024 px: registro indisponível abre a lista (mestre) com o aviso em cima dela; o detalhe fica oculto nesse nível, e o aviso
  // vai para o mestre (uma cópia só no DOM, para o leitor de tela ouvir uma vez). Achado 11: com o detalhe oculto de fato, o aviso sumia a 390
  const noMestre=!!o.aviso&&!cadLarga()&&(self.state.mx_nivel||'m')==='m'; v.mx_temAviso=noMestre; v.dx_temAviso=!!o.aviso&&!noMestre; }
// vazio com próximo passo (4.3, DS-45): só texto e, quando houver, um link (nunca outro verde)
// vazio da tela só quando nenhuma coluna está filtrada: com filtro de coluna vale o vazio da grade ("Nenhuma linha corresponde aos filtros ·
// Limpar filtros"), para não dizer "nenhum encontrado, crie" quando o registro existe e só está escondido pelo filtro (risco de duplicar)
function cadVazioSe(self,v,key,o,gids){ const col=gids.some(g=>{ const st=g2st(self,g); return Object.keys(st.f||{}).some(k=>(st.f[k]||[]).length); });
  const oo=col?null:o; cadVazioVals(v,key,oo); if(oo) gids.forEach(g=>{ v[g+'_empty']=false; }); return oo; }
function cadVazioVals(v,key,o){ v[key+'_tem']=!!o; v[key+'_t']=o?o.t:''; v[key+'_temLk']=!!(o&&o.lk); v[key+'_lkT']=(o&&o.lk)?o.lk.t:''; v[key+'_lkH']=(o&&o.lk&&o.lk.h)||'#';
  v[key+'_temGo']=!!(o&&o.go); v[key+'_goT']=(o&&o.go)?o.go.t:''; v[key+'_go']=(o&&o.go)?o.go.fn:(()=>{}); }

// ---- endereço: leitura ao abrir, no voltar/avançar do navegador e no hashchange; o voltar com alteração não salva repõe o endereço e pergunta ----
function cadEndIni(self,aplica){ if(self.__cadEnd) return; self.__cadEnd=1; self.__cadHash=String(location.hash||'').replace(/^#/,'');
  const vai=(pop)=>{ const h=String(location.hash||'').replace(/^#/,''); let st=null; try{ st=history.state; }catch(e){}
    const emEd=(suj)=>GRIDS.find(sp=>{ const fm=g2st(self,sp.id).fm; return fm&&!fm.ro&&!fm.cons&&(!suj||g2dirty(fm)); });
    // saiu a entrada da edição ('e', mesmo endereço; cadNivelEd): com alteração não salva, ela volta e o aviso aparece (E4, R06);
    // sem alteração, a edição fecha como no Cancelar (volta à consulta do registro) e o voltar seguinte sobe um nível
    if(pop&&self.__cadEd&&!(st&&st.cadux==='e')){ self.__cadEd=0; const g=emEd(true);
      if(g){ cadNivelEd(self); g2set(self,g.id,{fm:Object.assign({},g2st(self,g.id).fm,{warn:true})}); return; }
      const e=emEd(false); if(e&&h===self.__cadEdH){ g2fecha(self,e,g2st(self,e.id).fm); return; } }
    if(pop&&h===self.__cadHash) return;
    // painel em edição com alteração não salva: o endereço volta ao do painel e o aviso aparece (E4, R06)
    const g=emEd(true);
    if(pop&&g){ try{ history.pushState({cadux:'i'},'',location.pathname+location.search+(self.__cadHash?'#'+self.__cadHash:'')); }catch(e){}
      g2set(self,g.id,{fm:Object.assign({},g2st(self,g.id).fm,{warn:true})}); return; }
    self.__cadHash=h; aplica(cadHashLe('#'+h),!!pop,pop?null:(p=>Object.assign(self.state,p))); };
  try{ window.addEventListener('popstate',()=>vai(true)); window.addEventListener('hashchange',()=>vai(true)); }catch(e){}
  vai(false); }   // 1ª leitura dentro do 1º desenho: o estado inicial já nasce com a seleção do endereço (sem piscar a lista)
// R06/AC-21: a edição e a criação ganham uma entrada no histórico ('e', com o mesmo endereço) quando a tela ainda não empilhou um nível
// (painel aberto pelo endereço, como o #reg= de outra frente; ficha do grupo; criação do grupo): sem ela, o voltar sai da tela e perde o
// digitado. Salvar ou sair sem alteração consome a entrada (history.back), para o voltar seguinte não ficar sem efeito
function cadNivelEd(self){ let st=null; try{ st=history.state; }catch(e){} if(st&&st.cadux) return; const h=String(location.hash||'').replace(/^#/,'');
  try{ history.pushState({cadux:'e'},'',location.pathname+location.search+(h?'#'+h:'')); }catch(e){ return; } self.__cadEd=1; self.__cadEdH=h; self.__cadHash=h; }
function cadNivelEdSai(self){ if(!self.__cadEd) return; self.__cadEd=0; let st=null; try{ st=history.state; }catch(e){}
  if(st&&st.cadux==='e'&&String(location.hash||'').replace(/^#/,'')===self.__cadEdH){ try{ history.back(); }catch(e){} } }
// fecha o painel: se a entrada do painel foi empilhada por nós, volta uma no histórico (o voltar seguinte sai da tela, sem reabrir o painel)
function cadEndFechaItem(self,o){ let st=null; try{ st=history.state; }catch(e){}
  if(st&&st.cadux==='i'){ self.__cadHash=cadHashTxt(o); try{ history.back(); }catch(e){} return; } cadHashPoe(self,o); }
