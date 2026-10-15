// ===== G2 · grade interativa, formulário lateral e navegação (motor do protótipo v3.7) =====
const G2C={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],blue:['#1E5F8F','#E3F0FB'],orange:['#9A3F00','#FFE8D6']};
// a não quebra de linha das ações da célula vem da classe g2cta (engine): numa tabela com a 1ª coluna limitada (celular) elas quebram
// DS-ALVO-20261015: a ação de célula é o _MINI do engine (5px 10px, raio 8, 12 px/700) e ganha 44 px no toque (--g2-alvo, ALVO_CSS)
const G2CTA='display:inline-flex;align-items:center;gap:6px;padding:5px 10px;max-width:100%;min-width:0;white-space:normal;overflow-wrap:anywhere;text-align:left;border-radius:8px;font-size:12px;font-weight:700;min-height:var(--g2-alvo,0px);box-sizing:border-box;text-decoration:none;background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;cursor:pointer;font-family:inherit;line-height:1.25;';
const G2CTAU='display:inline-flex;align-items:center;gap:6px;padding:5px 10px;max-width:100%;min-width:0;white-space:normal;overflow-wrap:anywhere;text-align:left;border-radius:8px;font-size:12px;font-weight:700;min-height:var(--g2-alvo,0px);box-sizing:border-box;text-decoration:none;background:#FFFFFF;color:#B42318;border:1px solid #B42318;cursor:pointer;font-family:inherit;line-height:1.25;';
function g2num(s){ if(typeof s==='number') return s; if(s===null||s===undefined) return NaN; let t=String(s).trim(); if(!t) return NaN; t=t.replace(/[^0-9,.\-]/g,''); if(t.indexOf(',')>=0){ t=t.replace(/\./g,'').replace(',','.'); } else if((t.match(/\./g)||[]).length>1 || /^\-?\d{1,3}(\.\d{3})+$/.test(t)){ t=t.replace(/\./g,''); } return parseFloat(t); }
function g2fmtn(n,d,dmin){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:(dmin!==undefined?dmin:(d||0)),maximumFractionDigits:d||0}); }
// unidade junto do valor (c.un, decisão de 05/10/2026): "160 ha", "54 %", "R$ 14,49/ha"; só em texto que é um número puro
function g2unf(t,c){ const s=String(t==null?'':t).trim(); if(!c||!c.un||!/^[+−-]?[\d.]+(,\d+)?$/.test(s)) return String(t==null?'':t);
  const u=c.un; if(u.indexOf('R$')===0){ const neg=/^[−-]/.test(s); return (neg?'−':'')+'R$ '+s.replace(/^[+−-]/,'')+u.slice(2); } return s+' '+u; }
function g2fmt(v,c){ if(v===null||v===undefined||v==='') return '—'; if(c&&c.t==='date'&&/^\d{4}-\d{2}-\d{2}$/.test(String(v))){ const a=String(v).split('-'); return a[2]+'/'+a[1]+'/'+a[0]; } if(c&&c.zdash&&Number(v)===0) return '—'; if(c&&c.t==='num'){ const n=Number(v); if(isNaN(n)) return String(v); const t=(c.pre||'')+g2fmtn(n,c.d,c.dmin)+(c.u?' '+c.u:''); return c.un?g2unf(t,c):t; } return String(v); }
function g2st(self,id){ return ((self.state.g2||{})[id])||{}; }
// Um campo de busca por tela (proprietário, 13/10/2026: "quero somente 1 campo de busca por tela. 2 fica confuso"): das tabelas à vista com
// busca, só a primeira mostra o campo ("Buscar nesta tela") e o termo dela vale para todas as outras à vista. Recalculado depois de cada
// desenho, porque abas, etapas e visões mudam o que está à vista; cada tabela guarda o próprio termo para quando voltar a ser a primeira.
function g2qSeg(self,id){ return !!self.__g2qS&&(' '+self.__g2qS+' ').indexOf(' '+id+' ')>=0; }
function g2stBusca(self,id,st){ return g2qSeg(self,id)?Object.assign({},st,{q:(g2st(self,self.__g2qL).q||'')}):st; }
function g2buscaUnica(self){ if(typeof document==='undefined') return;
  const vis=[...document.querySelectorAll('[data-g2q]')].filter(m=>m.parentElement&&m.parentElement.getClientRects().length>0);
  const dlg=vis.filter(m=>m.closest('[role=dialog]'));   // com um diálogo aberto (fundo inerte), a busca da tela é a do diálogo (AC-SOLO-18)
  const ids=(dlg.length?dlg:vis).map(m=>m.getAttribute('data-g2q'));
  const L=ids[0]||'', S=ids.slice(1).join(' '); if(L===(self.__g2qL||'')&&S===(self.__g2qS||'')) return;
  self.__g2qL=L; self.__g2qS=S; self.setState({g2qrev:(self.state.g2qrev||0)+1}); }
function g2set(self,id,patch){ const all=Object.assign({},self.state.g2||{}); all[id]=Object.assign({},all[id]||{},patch); self.setState({g2:all});
  if(G2KEEP[id]) g2keepGrava(self,id,all[id]); }
// grava o recorte guardado (g2keep): filtros, busca, ordenação, filtro rápido e, quando a tela pede (VISOES-1), Fazenda e Safra do topo
function g2keepGrava(self,id,x){ if(!G2KEEP[id]) return; x=x||g2st(self,id); const o={f:x.f||{},q:x.q||'',so:x.so||null,qv:x.qv||''};
  if(G2KEEP_TOPO[id]){ const s=self.state||{}; G2TOPO.forEach(c=>{ if(s[c]) o[c]=s[c]; }); }
  try{ sessionStorage.setItem(G2KEEP[id],JSON.stringify(o)); }catch(e){} }
// recorte guardado na sessão (TABELAS-FOCO): filtros, busca e ordenação sobrevivem a abrir o detalhe e voltar; só a tabela que pede (g2keep)
const G2KEEP={}, G2KEEP_TOPO={};
// filtros da faixa guardados com a grade (VISOES-1 §2.3; Cultura e Talhão desde 13/10, PROD-C961-CONTEXTO-01 da revisão Codex)
const G2TOPO=['mf_faz','mf_saf','mf_cult','mf_tal'];
function g2topoK(s){ return G2TOPO.map(c=>(s&&s[c])||'').join('|'); }
// opt.topo (VISOES-1, §2.3): guarda também a Fazenda e a Safra do topo (mf_faz, mf_saf); opt.v: valores da tela já montados (o seletor do topo
// mostra o valor restaurado no mesmo desenho). Na volta do detalhe, um talhão de outra fazenda não esvazia a lista com "filtro ativo".
function g2keep(self,id,opt){ let key='g2:'+id; try{ key='g2:'+String(location.pathname).split('/').pop()+':'+id; }catch(e){} G2KEEP[id]=key;
  if(opt&&opt.topo) G2KEEP_TOPO[id]=1;
  if(self.__g2kept&&self.__g2kept[id]){ if(G2KEEP_TOPO[id]){ const k=g2topoK(self.state); if(self.__g2keptTopo!==k){ self.__g2keptTopo=k; g2keepGrava(self,id); } } return; }
  (self.__g2kept=self.__g2kept||{})[id]=1;
  try{ const o=JSON.parse(sessionStorage.getItem(key)||'null'); if(o&&typeof o==='object'){ const all=Object.assign({},self.state.g2||{}); all[id]=Object.assign({},all[id]||{},{f:o.f||{},q:o.q||'',so:o.so||null,qv:o.qv||''}); self.state.g2=all;
    if(G2KEEP_TOPO[id]){ G2TOPO.forEach(c=>{ if(typeof o[c]==='string'&&o[c]&&self.state[c]===undefined){ self.state[c]=o[c]; if(opt&&opt.v) opt.v[c]=o[c]; } }); } } }catch(e){}
  if(G2KEEP_TOPO[id]){ self.__g2keptTopo=g2topoK(self.state); } }
function g2rows(self,sp){ const st=g2st(self,sp.id); return st.rows||sp.rows; }
function g2find(list,id){ for(const r of list){ if(r.id===id) return r; if(r.kids){ const k=g2find(r.kids,id); if(k) return k; } } return null; }
function g2text(r,c){ if(r.s&&r.s[c.k]!==undefined&&r.s[c.k]!==null) return (c&&c.un)?g2unf(r.s[c.k],c):String(r.s[c.k]); if(r.v&&r.v[c.k]!==undefined&&r.v[c.k]!==null) return g2fmt(r.v[c.k],c); return ''; }
// coluna multivalorada (c.multi, TABELAS-FOCO): a linha traz r.m[k]=[{id,l}] (vínculos estruturados, ex.: talhões); filtro por pertinência
// do ID, nunca por texto (T1 não pega T10 nem T1-A); vazio é um valor próprio do filtro, nos dois sentidos
function g2mem(r,c){ return (c.multi&&r.m&&r.m[c.k])||null; }
// chave estável (r.ordk[k], UNID-PROD R-U11): a coluna mostra um texto que muda com a unidade escolhida; a ordem e o filtro por valores
// usam a chave (número em kg/ha; texto para os estados), não o texto. O menu do filtro continua mostrando o texto da célula
function g2ordk(r,c){ return (r&&r.ordk&&r.ordk[c.k]!==undefined)?r.ordk[c.k]:undefined; }
function g2fkeys(r,c){ const o=g2ordk(r,c); if(o!==undefined) return [(o===null||o===''||o==='vazio')?'(vazio)':String(o)];
  const m=g2mem(r,c); if(m) return m.length?m.map(x=>x.id):['(vazio)']; const t=g2text(r,c); return [(t===''||t==='—')?'(vazio)':t]; }
// rótulo de um valor do filtro: com chave estável, o texto da célula de hoje (na unidade escolhida); senão a própria chave
function g2flab(rows,c,k){ if(k==='(vazio)') return k; const ach=(list)=>{ for(const r of list||[]){ const o=g2ordk(r,c); if(o!==undefined&&String(o)===k) return g2text(r,c)||k; const x=ach(r.kids); if(x) return x; } return ''; }; return ach(rows)||k; }
function g2key(r,c){ const o=g2ordk(r,c); if(o!==undefined) return typeof o==='number'?o:null;
  if(c.t==='date'){ const d=r.v&&r.v[c.k]; return (d===undefined||d===null||d==='')?null:String(d); }   // ISO: ordena por data
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
  const ST='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;min-height:var(--g2-alvo,0px);box-sizing:border-box;';   /* 44 px no toque (DS-ALVO) */
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
// Selos e chips de estado com significado e próximo passo (DS-DICA-20261009): fonte única das dicas de estado; o texto segue as regras do
// motor (fases da O.S. do AGENTS §4, PEND-OS-01 e as exceções da aprovação; bloqueios nas mensagens de osEncBloq/osLibErro). Chave = texto
// do selo antes de " · ". Só vale onde a tela pede (data-dica-de ou parte {de:1}): o mesmo texto noutro contexto pode significar outra coisa.
const G2_DICAS={
  'A liberar':'Criada e ainda fora do campo. Próximo passo: liberar. O.S. agrícola: Aprovar e liberar (o agrônomo aprova a versão e o gestor libera, em dois registros); irrigação só com água, manutenção e beneficiamento: libera o responsável próprio.',
  'Liberadas':'Liberada para o campo; os insumos da ordem ficam reservados no Estoque. Próximo passo: entregar os insumos a quem executa e iniciar.',
  'Em execução':'Em execução: cada turno aponta o que foi feito (área ou quantidade, horas e consumo). Próximo passo: terminar e levar à conferência.',
  'Em conferência':'Execução terminada: apontamentos, consumo e sobras em conferência. Próximo passo: conferir (sobra em custódia volta ao Estoque) e encerrar.',
  'Encerradas':'Fechada: realizado, consumo e custo gravados. Sem próximo passo.',
  'Canceladas':'Cancelada sem execução, com o motivo registrado. Sem próximo passo.',
  'Aguardando sinal do app':'Turno apontado no aparelho que ainda não chegou. Próximo passo: quem executou reconecta o app; o envio é automático e não duplica.',
  'Sobras a receber':'Sobra de insumo em custódia com quem executou. Próximo passo: o almoxarife recebe a devolução no Estoque; só então a ordem encerra.',
  'Apontamento em conferência':'Apontamento em possível duplicidade. Próximo passo: a conferência decide na linha do apontamento (mesmo turno conta uma vez; outro turno soma).',
  'Falta insumo':'O saldo do lote no Estoque não cobre dose × área. Próximo passo: o Estoque recebe o insumo ou o agrônomo ajusta dose, área ou produto antes de liberar.',
  'Fora do registro':'Produto, dose ou cultura fora do registro (bula e AGROFIT). Próximo passo: o agrônomo ajusta produto ou dose antes de liberar.',
  'Total 0':'Dose × área dá 0 na precisão do Estoque. Próximo passo: o agrônomo ajusta a dose ou a área.',
  'Insumo esgotado':'Um insumo acabou com área ainda a fazer. Próximo passo: o agrônomo decide a área restante.'};
// revisão DS (achado 6): sem caminho de menu no texto (o nome do item muda). O selo do bloqueio do encerramento em conferência (Carga a pesar,
// Sobras a receber, Aguardando sinal do app, Apontamento em conferência) leva a dica do próprio bloqueio (processo_os.osSeloDica ← osEncBloq,
// o mesmo texto do painel e do comando); "Carga a pesar" só existe aí e saiu daqui. As três outras ficam para o selo antes da conferência.
function g2dicaDe(t){ const s=String(t||'').trim(); return G2_DICAS[s]||G2_DICAS[s.split(' · ')[0].trim()]||''; }
/* cortes visuais (13/10): parte que abre linha (1ª da célula ou depois de uma quebra) não começa com o separador "·" */
function g2semSep(raw,i){ const p=raw[i]; if(!p||typeof p.t!=='string'||!/^\s*·\s/.test(p.t)) return p; if(i>0&&!(raw[i-1]&&raw[i-1].k==='br')) return p; return Object.assign({},p,{t:p.t.replace(/^\s*·\s*/,'')}); }
function g2part(p,v){ const o={isIco:false,isCn:false,isTxt:false,isB:false,isMut:false,isChip:false,isTag:false,isLink:false,isCta:false,isAct:false,isBr:false,t:p.t||'',st:'',cls:'',dot:'',href:p.h||'#',fn:null,title:p.t||'',dica:'',hasDica:false};
  switch(p.k){ case 'b': o.isB=true; break; case 'mut': o.isMut=true; break;
    case 'chip': { const cc=G2C[p.c]||G2C.gray; o.isChip=true; o.dica=p.dica||p.dv||(p.de?g2dicaDe(p.t):''); o.hasDica=!!p.dica;   /* p.de: dica de estado do dicionário; p.dv: texto pronto da tela (selo do bloqueio, osSeloDica); os dois só visuais (o leitor de tela lê o motivo explícito p.dica; a linha focada recebe a dica do selo, g2dicaSelo) */ o.st='display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:normal;max-width:100%;min-width:0;overflow-wrap:anywhere;line-height:1.3;color:'+cc[0]+';background:'+cc[1]+';';   /* cortes visuais (13/10): selo longo quebra na própria célula, nunca invade a vizinha */ o.dot='width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'; break; }
    case 'ico': { const cc=G2C[p.c]||G2C.gray; o.isIco=true; o.dica=p.t||''; o.st='display:inline-flex;align-items:center;gap:4px;flex-shrink:'+(p.curto?'1;min-width:0;line-height:1.2;':'0;')+'color:'+cc[0]+';font-size:11.5px;font-weight:700;';   /* texto curto quebra linha no celular em vez de sair da célula (visual_corte C1) */ o.icoTxt=p.curto||''; o.icoTem=!!p.curto; break; }   /* C2: bloqueio/erro com texto curto, não só cor e dica */   /* VISOES-2 §3.6: situação como ícone com cor, texto na dica e no leitor */
    case 'cn': { const cc=G2C[p.c]||G2C.gray; o.isCn=true; o.st='font-weight:800;white-space:nowrap;color:'+cc[0]+';'; break; }
    case 'tag': o.isTag=true; break; case 'link': o.isLink=true; break;
    case 'cta': o.isCta=true; o.cls='g2cta'; o.st=p.u?G2CTAU:G2CTA; break;
    case 'act': o.isAct=true; o.al=p.al||p.t; if(p.lk) { o.lk=true; } if(p.fn&&p.fn.indexOf(':')>0){ const nm=p.fn.split(':')[0], ar=p.fn.slice(nm.length+1); o.fn=()=>{ if(v&&v[nm]) v[nm](ar); }; } else o.fn=(v&&p.fn&&v[p.fn])||(()=>{}); o.cls=(p.lk?'':'g2cta')+(p.sec?' g2sec':''); if(p.desce){ o.cls='g2desce'; o.st='border:0;background:transparent;padding:0;color:#15201A;font-weight:800;cursor:pointer;font-family:inherit;font-size:13px;text-align:left;'; o.t=p.t+' ›'; } else o.st=p.lk?'border:0;background:transparent;padding:0;color:#1E7A4C;font-weight:700;cursor:pointer;font-family:inherit;font-size:13px;text-decoration:underline;text-underline-offset:3px;text-align:left;':(p.u?G2CTAU:G2CTA);
      // célula inteira tocável (DS: alvo ≥ 44 px): texto da célula, sem negrito, na cor do estado; aria-pressed quando é o filtro ativo
      if(p.full){ o.cls='g2full'; o.st='width:100%;min-height:44px;border:0;background:'+(p.on?'#E4F3E9':'transparent')+';padding:0 6px;cursor:pointer;font-family:inherit;font-size:13px;font-weight:'+(p.on?'700':'400')+';text-align:right;font-variant-numeric:tabular-nums;color:'+((G2C[p.c]||[])[0]||'#15201A')+';'+(p.on?'outline:2px solid #1E7A4C;outline-offset:-2px;border-radius:6px;':''); } break;
    case 'br': o.isBr=true; break; default: o.isTxt=true; }
  // separador no começo da parte ("· TK-4502" depois de "CG-2107"): vai para um elemento próprio, que o g2sepIni esconde quando a parte
  // começa a linha (a quebra da célula não deixa linha começando com "·"); o texto lido continua "· TK-4502"
  if((o.isTxt||o.isMut||o.isB)&&/^\s*·\s/.test(o.t)){ o.sepL=true; o.t=o.t.replace(/^\s*·\s*/,''); }
  return o; }
// marca (data-ini) o separador que caiu no começo de uma linha: nada visível à esquerda dele na mesma linha, dentro da mesma lista de partes.
// Roda depois de cada desenho e ao mudar o tamanho da janela; só mexe na opacidade, então não muda a quebra (sem efeito sanfona).
function g2sepIni(){ if(typeof document==='undefined') return; document.querySelectorAll('.g2sepd').forEach(d=>{ const r=d.getBoundingClientRect(); if(!r.width) return;
    const pw=d.closest('.g2pw')||d.parentElement; const parte=d.parentElement&&d.parentElement.closest('span:not(.g2sepd),b'); let ini=true;
    for(const o of pw.querySelectorAll('span,b,a,button')){ if(o===d||(parte&&(o===parte||o.contains(parte)||parte.contains(o)))) continue; const q=o.getBoundingClientRect();
      if(q.width>0&&q.bottom>r.top+2&&q.top<r.bottom-2&&q.right<=r.left+2){ ini=false; break; } }
    if(ini){ if(!d.hasAttribute('data-ini')) d.setAttribute('data-ini',''); } else if(d.hasAttribute('data-ini')) d.removeAttribute('data-ini'); }); }
(function(){ if(typeof document==='undefined'||typeof MutationObserver==='undefined'||typeof requestAnimationFrame==='undefined') return; let q=0;
  const vez=()=>{ if(q) return; q=requestAnimationFrame(()=>{ q=0; try{ g2sepIni(); }catch(e){} }); };
  try{ new MutationObserver(vez).observe(document.documentElement,{subtree:true,childList:true,characterData:true}); addEventListener('resize',vez);
    if(document.fonts&&document.fonts.ready) document.fonts.ready.then(vez); vez(); }catch(e){} })();
// revisão DS (achado 8): sigla ou unidade que está na célula ("62,4 sc/ha", "35 DAP") e não no rótulo dá a dica do cabeçalho da coluna, só onde é da
// coluna (em ao menos 30 % das células com texto; termo solto numa observação não conta); código de registro (COT-0031) não é sigla. Texto: G2_GLOSS
// (engine._GLOSS_CEL, fonte única). Guardado por grade enquanto as linhas são as mesmas (o desenho não refaz a varredura); com linhas novas, lê até
// 200 linhas e só conta célula a célula o termo que aparece no texto junto (pior caso medido em node: ds_unit.js 2b.8).
const G2GC={};
function g2glossCol(sp,c,rows){ if(typeof G2_GLOSS==='undefined'||!rows||!rows.length) return '';
  let m=G2GC[sp.id]; if(!m||m.rows!==rows){ m=G2GC[sp.id]={rows,k:{}}; } if(m.k[c.k]!==undefined) return m.k[c.k];
  if(!G2GC.__re) G2GC.__re=G2_GLOSS.map(x=>[new RegExp(x[0]),x[1]]);
  const cel=[]; let n=0; const walk=(l)=>{ for(const r of l){ if(++n>200) return; const t=(g2text(r,c)+' '+(((r.p&&r.p[c.k])||[]).map(p=>(p&&p.t)||'').join(' '))).replace(/\b[A-Z]{2,5}-\d[\w-]*/g,'').trim();
      if(t&&t!=='—') cel.push(t); if(r.kids) walk(r.kids); } }; walk(rows);
  const all=cel.join('\n'); const out=cel.length?G2GC.__re.filter(([re])=>re.test(all)&&cel.filter(x=>re.test(x)).length>=Math.max(1,0.3*cel.length)).slice(0,2).map(x=>x[1]).join(' '):'';
  return (m.k[c.k]=out); }
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
  let r=g2find(g2disp(self,sp),rid)||g2find(g2rows(self,sp),rid);
  // VISOES-2 (defeito F do teste adaptado): dentro de um grupo a linha é uma cópia com id "OS-0421@T1"; abre a linha original (OS-0421)
  if(!r&&String(rid).indexOf('@')>0&&String(rid).indexOf('grp@')!==0){ rid=String(rid).split('@')[0]; r=g2find(g2disp(self,sp),rid)||g2find(g2rows(self,sp),rid); }
  if(!r||r.fora) return;
  if(r.dr && self.__v && self.__v[r.dr]){ self.__v[r.dr](); return; }
  if(ed.m==='pick'){ if(self.g2pick) self.g2pick(sp.id,rid,r); g2set(self,sp.id,{fl:rid}); return; }
  let draft={}; (ed.fields||[]).forEach(f=>{ let val=''; if(r.v&&r.v[f.k]!==undefined&&r.v[f.k]!==null&&r.v[f.k]!=='') val=(f.t==='num'? String(r.v[f.k]).replace('.',','):String(r.v[f.k])); else if(r.s&&r.s[f.k]!==undefined) val=String(r.s[f.k]); draft[f.k]=val; });
  // gancho de abertura (UNID-PROD R-U06): a tela pode pôr no rascunho um valor mostrado em outra unidade e guardar a origem; o "alterado?" compara com o que abriu
  if(self.g2openDraft) draft=self.g2openDraft(sp.id,r,draft)||draft;
  g2set(self,sp.id,{fm:{rid,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:(ed.m!=='form'||!!r.ro),isNew:false,mode:ed.m},fl:null,fmc:null}); }
function g2new(self,sp){ const ed=sp.edit||{}; const draft={}; (ed.fields||[]).forEach(f=>{ draft[f.k]=(f.def!==undefined?String(f.def):''); });
  if(self.g2newDraft) Object.assign(draft,self.g2newDraft(sp.id,draft)||{});   // contexto da tela no registro novo (SAF-FAZ-1-CONTEXTO-01: a fazenda do filtro)
  g2set(self,sp.id,{fm:{rid:null,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:false,isNew:true,mode:'form'},fl:null,fmc:null}); }
function g2calc(r,calc){ (calc||[]).forEach(cx=>{ const a=(cx.a||[]).map(k=>Number(r.v[k])||0); let x=null;
   if(cx.op==='mul') x=a.reduce((p,q)=>p*q,1); else if(cx.op==='div') x=a[1]?a[0]/a[1]:0; else if(cx.op==='sum') x=a.reduce((p,q)=>p+q,0);
   else if(cx.op==='sub') x=a.slice(1).reduce((p,q)=>p-q,a[0]); else if(cx.op==='max0sub') x=Math.max(0,a.slice(1).reduce((p,q)=>p-q,a[0]));
   if(x!==null){ r.v[cx.k]=Math.round(x*100)/100; if(r.s) delete r.s[cx.k]; if(r.p) delete r.p[cx.k]; } }); }
function g2clone(list){ return list.map(r=>Object.assign({},r,{v:Object.assign({},r.v||{}),s:Object.assign({},r.s||{}),p:Object.assign({},r.p||{}),kids:r.kids?g2clone(r.kids):undefined})); }
function g2save(self,sp){ const st=g2st(self,sp.id); const fm=st.fm; if(!fm) return; const ed=sp.edit||{}; const errs={}; const g2_0=self.state.g2;
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
  if(self.g2after) self.g2after(sp.id,rows,r,fm.isNew);
  g2persiste(self,sp.id,g2_0,{fm:Object.assign({},fm,{errs:{},warn:false})},'Não salvo'); }
// gravação da tela (CD08-GRAVA-01, revisão Codex de 14/10, S2): quando a tela grava no navegador (self.g2persist), o "salvo" só vale se a
// gravação deu certo. Falhou: o estado volta ao de antes do comando, o formulário reabre com o rascunho e o motivo, e nada é confirmado.
function g2persiste(self,id,g2_0,volta,pre){ if(!self.g2persist) return true; const er=self.g2persist(id); if(!er) return true;
  const all=Object.assign({},g2_0||{}); all[id]=Object.assign({},all[id]||{},volta||{},volta&&volta.fm?{fm:Object.assign({},volta.fm,{errG:er,errP:pre})}:{});
  self.setState({g2:all,g2toast:pre+': '+er}); return false; }
function g2dirty(fm){ if(!fm) return false; for(const k in fm.draft){ if(String(fm.draft[k])!==String(fm.orig[k])) return true; } return false; }
function g2close(self,sp){ const fm=g2st(self,sp.id).fm; if(fm && !fm.ro && g2dirty(fm)) { g2set(self,sp.id,{fm:Object.assign({},fm,{warn:true})}); return; } g2set(self,sp.id,{fm:null});
  if(fm && !fm.ro) self.setState({g2toast:'Edição cancelada'}); }   /* 14/10: cancelar também confirma (salvar já confirmava); sem afirmar o que outra ação já gravou (Codex) */
// VISOES-2 §3.6 · colunas só o essencial. c.ess = posição no padrão ("Abre com"); c.pq = pergunta (oque, quem, quando, onde, medida,
// situacao) que agrupa o painel de colunas. Grade sem nenhum ess mostra todas, como antes. A escolha é por perfil × tela × grade (no
// protótipo, perfil = usuário) e guarda o conjunto, não a ordem: a ordem é sempre a do desenho (identidade, padrão pelo ess, depois as
// demais na ordem da grade). Coluna oculta continua valendo para busca, filtro e agrupamento (g2match usa sp.cols).
const G2_CV_PERG=[['oque','O quê'],['quem','Quem'],['quando','Quando'],['onde','Onde'],['medida','Medidas'],['situacao','Situação'],['','Outras']];
// VISOES-2 §3.6 · Situação oculta vira ícone antes da identidade (sp.sico = {k, cores}): só nas cores que pedem atenção (padrão vermelho,
// laranja e amarelo), com o texto completo na dica e no leitor; o estado normal (Planejado, Livre) fica sem ícone
// sp.sico.ks: mais de uma coluna de situação oculta (ex.: Pendência e Situação); cada uma dá o seu ícone, na ordem do quadro
function g2sicoPart(r,sp,k){ k=k||sp.sico.k; const cores=sp.sico.cores||['red','orange','yellow'], c=sp.cols.find(x=>x.k===k); if(!c) return null;
  const ps=(r.p&&r.p[k])||[], ch=ps.find(p=>p&&p.c&&['chip','ico','cn'].indexOf(p.k)>=0); let cor=null, t='', d='';
  // selo de estado (de): o ícone leva o significado e o próximo passo (G2_DICAS), como o selo
  if(ch){ cor=ch.c; t=String(ch.t||''); d=String(ch.dica||ch.dv||(ch.de?g2dicaDe(ch.t):'')||''); } else { t=g2text(r,c); cor=(c.chips||{})[t]||null; }
  t=t.trim(); if(!cor||!t||cores.indexOf(cor)<0) return null;
  return {k:'ico',c:cor,t:c.l+': '+t+(d?' · '+d:''),curto:cor==='red'?t:''}; }   // texto curto ao lado só no bloqueio (vermelho, visual_corte C2); atenção fica no ícone e na dica
// V2-3: tela que troca sp.cols em tempo de execução (CD-05 pelo papel; Irrigação sem a Fazenda) recebe de volta as marcas da coluna
// pela chave (sp.marcas, do quadro): a coluna nova não perde a posição no padrão nem a pergunta
function g2marca(sp){ if(!sp||!sp.marcas||!sp.cols) return; sp.cols.forEach(c=>{ const m=sp.marcas[c.k]; if(!m) return; if(c.ess==null&&m.ess) c.ess=m.ess; if(!c.pq&&m.pq) c.pq=m.pq; }); }
function g2cvTem(sp){ g2marca(sp); return !!(sp&&sp.cols&&sp.cols.some(c=>c.ess)); }
function g2cvChave(sp){ let pg=''; try{ pg=String(location.pathname).split('/').pop(); }catch(e){} let pf=''; try{ pf=g2perfil().k; }catch(e){} return 'g2cv:'+pg+':'+sp.id+':'+pf; }
function g2cvPadrao(sp){ return sp.cols.filter(c=>c.ess).sort((a,b)=>a.ess-b.ess).map(c=>c.k); }
function g2cvLer(self,sp){ if(typeof window!=='undefined'&&window.__g2cvTodasSempre) return sp.cols.map(c=>c.k);   // só teste de domínio (comp_lib.cv_todas_sempre)
  const st=g2st(self,sp.id); if(st.cvpf===undefined||st.cvpf===g2pfk()){ if(Array.isArray(st.cv)) return st.cv; if(st.cv===false) return null; } let x=null;
  try{ x=JSON.parse(localStorage.getItem(g2cvChave(sp))||'null'); }catch(e){ x=null; } return Array.isArray(x)?x.filter(k=>sp.cols.some(c=>c.k===k)):null; }
function g2cvCel(){ try{ return window.matchMedia('(max-width: 640px)').matches; }catch(e){ return false; } }
function g2colsVis(self,sp){ if(!g2cvTem(sp)) return sp.cols; const esc=g2cvLer(self,sp), pad=g2cvPadrao(sp), k0=sp.cols[0].k;
  let S=new Set(esc||pad); S.add(k0);
  // o padrão vem na ordem do "Abre com"; cada coluna a mais gruda na vizinha da grade que está no padrão (a anterior; senão a seguinte) e, sem
  // vizinha no padrão, entra depois da anterior já à vista: a tabela completa mantém os pares desenhados (Custo total no fim, decisão do
  // proprietário de 13/10; "1º uso" ao lado do insumo; R$/ha ao lado do total; NR-31 junto da validade; vínculo junto da vigência)
  let ord=[k0].concat(pad.filter(k=>k!==k0&&S.has(k))); const gk=sp.cols.map(c=>c.k), base=new Set(ord);
  gk.forEach((k,i)=>{ if(k===k0||ord.indexOf(k)>=0||!S.has(k)) return; const pv=gk[i-1], nx=gk[i+1]; let at;
    if(base.has(pv)) at=ord.indexOf(pv)+1; else if(base.has(nx)) at=ord.indexOf(nx);
    else { let j=-1; for(let a=i-1;a>=0&&j<0;a--) j=ord.indexOf(gk[a]); at=j+1; }
    ord.splice(at,0,k); });
  if(gk.every(k=>S.has(k))) ord=gk.slice();   // todas à vista: a tabela completa como foi desenhada (ordem da grade)
  if(!esc&&g2cvCel()) ord=ord.slice(0,3);   // celular: as 3 primeiras do padrão; a escolha explícita vale em qualquer tela
  return ord.map(k=>sp.cols.find(c=>c.k===k)).filter(Boolean); }
function g2cvGrava(self,sp,ks){ try{ if(ks) localStorage.setItem(g2cvChave(sp),JSON.stringify(ks)); else localStorage.removeItem(g2cvChave(sp)); }catch(e){}
  g2set(self,sp.id,{cv:ks?ks.slice():false,cvpf:g2pfk()}); }
// ganchos de teste (como window.__cen): "todas as colunas" para todos os perfis da tela (testes de domínio que leem colunas fora do padrão) e se
// o perfil atual já tem escolha; o padrão em si é conferido no teste da VISOES-2
if(typeof window!=='undefined'&&!window.__g2cvTodas){ window.__g2cvTodas=(gid)=>{ const sp=(typeof GRIDS!=='undefined'?GRIDS:[]).find(g=>g.id===gid); if(!sp) return false; const ks=sp.cols.map(c=>c.k);
    g2perfis().concat([g2todos()]).forEach(pf=>{ try{ localStorage.setItem(g2cvChave(sp).replace(/:[^:]*$/,':'+pf.k),JSON.stringify(ks)); }catch(e){} }); return true; };
  window.__g2cvEscolha=(gid)=>{ try{ return localStorage.getItem(g2cvChave({id:gid})); }catch(e){ return null; } }; }
function g2cvVals(self,sp,v,cols){ const id=sp.id; if(!g2cvTem(sp)||(sp.cols.length<=5&&cols.length>=sp.cols.length)){ v[id+'_cvhas']=false; v[id+'_cvopen']=false; v[id+'_cvg']=[]; return; }
  const st=g2st(self,id), vis=new Set(cols.map(c=>c.k)), n=sp.cols.length-vis.size, k0=sp.cols[0].k, open=!!st.cvo;
  v[id+'_cvhas']=true; v[id+'_cvn']=n?'+'+n:''; v[id+'_cvlab']='Colunas'+(n?' · '+n+(n>1?' ocultas':' oculta'):' · todas visíveis'); v[id+'_cvopen']=open; v[id+'_cvexp']=String(open);
  const P=st.cvpos||{xr:0,y:0}, W=290, vw=(typeof window!=='undefined'?window.innerWidth:1440), vh=(typeof window!=='undefined'?window.innerHeight:900);
  const top=Math.max(8,Math.min(P.y+6,vh-260)); v[id+'_cvpos']='top:'+top+'px;left:'+Math.max(8,Math.min(P.xr-W,vw-W-8))+'px;max-height:'+Math.max(240,vh-top-16)+'px;';
  v[id+'_cvtog']=(e)=>{ const el=e&&e.currentTarget; const rr=el&&el.getBoundingClientRect?el.getBoundingClientRect():{right:0,bottom:0}; const ab=!g2st(self,id).cvo;
    g2set(self,id,ab?{cvo:true,cvpos:{xr:rr.right,y:rr.bottom}}:{cvo:false}); if(ab) setTimeout(()=>{ const c=document.querySelector('[data-g2cv="'+id+'"] input:not([disabled])'); if(c) c.focus(); },0); };
  v[id+'_cvfecha']=()=>{ g2set(self,id,{cvo:false}); setTimeout(()=>{ const b=document.querySelector('[data-g2cvb="'+id+'"]'); if(b) b.focus(); },0); };
  v[id+'_cvkey']=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); v[id+'_cvfecha'](); } };
  v[id+'_cvg']=G2_CV_PERG.map(([pk,t])=>({t,cols:sp.cols.filter(c=>pk?c.pq===pk:!G2_CV_PERG.some(x=>x[0]&&x[0]===c.pq)).map(c=>({l:c.l,on:vis.has(c.k),dis:c.k===k0,
    tog:()=>{ if(c.k===k0) return; const cur=new Set(g2colsVis(self,sp).map(x=>x.k)); if(cur.has(c.k)) cur.delete(c.k); else cur.add(c.k); g2cvGrava(self,sp,[...cur]); }}))})).filter(g=>g.cols.length);
  const pad=g2cvPadrao(sp), esc=g2cvLer(self,sp); v[id+'_cvmudou']=!!esc;
  v[id+'_cvrest']=()=>g2cvGrava(self,sp,null); }
// VISOES-2 §3.3 · Agrupar por e descer. sp.ag = [{pq, l, niv:[nomes dos níveis]}] (engine.grid ag=); cada linha traz r.g[pq] = [valor do
// nível 0, valor do nível 1, ...] (valor pode ser lista: a linha entra em cada grupo, e o grupo conta itens distintos). Estado {d, t}: a pergunta
// e a trilha (valores já descidos). O grupo nasce só das linhas do recorte (busca, filtros); clicar no nome desce um nível (vira filtro), a
// seta expande no lugar; no último nível ficam as linhas. Endereço ?ag=&trilha= (replaceState) e preferência por perfil × tela × grade.
// ?view=agrupada (VISOES-1) chega como Agrupar por Onde.
function g2agTem(sp){ return !!(sp&&sp.ag&&sp.ag.length); }
function g2agChave(sp){ let pf=''; try{ pf=g2perfil().k; }catch(e){} return 'g2ag:'+g2arq()+':'+sp.id+':'+pf; }
function g2agOk(sp,a){ return !!a&&typeof a==='object'&&sp.ag.some(x=>x.pq===a.d)&&Array.isArray(a.t)&&a.t.every(x=>typeof x==='string'); }
function g2agUrl(pathname,search,hash,a){ const s=String(search||'').replace(/^\?/,''); const nome=p=>p.indexOf('=')<0?p:p.slice(0,p.indexOf('='));
  const ps=s?s.split('&').filter(p=>p&&['ag','trilha'].indexOf(nome(p))<0&&!(nome(p)==='view'&&p==='view=agrupada')):[];
  if(a){ ps.push('ag='+encodeURIComponent(a.d)); if(a.t.length) ps.push('trilha='+a.t.map(encodeURIComponent).join('/')); }
  return String(pathname||'')+(ps.length?'?'+ps.join('&'):'')+String(hash||''); }
// trilha no endereço: cada nível com encodeURIComponent, unidos por "/"; a leitura usa o texto cru do parâmetro, porque URLSearchParams
// decodifica %2F antes da divisão e "Safra 2026/27" viraria dois níveis (Codex 6168779649, achado 1)
function g2agTrilha(search){ const p=String(search||'').replace(/^\?/,'').split('&').find(x=>x.slice(0,7)==='trilha='); if(!p) return [];
  return p.slice(7).split('/').filter(Boolean).map(x=>{ try{ return decodeURIComponent(x); }catch(e){ return x; } }); }
// o estado em memória guarda o perfil de quem escolheu (agpf, cvpf): trocar o perfil sem recarregar (aqui ou em outra aba) relê a preferência
// do novo perfil e o endereço passa a refletir o agrupamento dele; o ?ag= do endereço só vale na chegada (V2-3-PERFIL-01, Codex 6179592748)
function g2pfk(){ try{ return g2perfil().k; }catch(e){ return ''; } }
function g2agLer(self,sp){ const st=g2st(self,sp.id), pf=g2pfk(); if(st.ag!==undefined&&(st.agpf===undefined||st.agpf===pf)) return st.ag;   // sem marca de perfil (estado montado pela própria tela): vale como está
  const troca=st.agpf!==undefined&&st.agpf!==pf; let a=null;
  if(!troca) try{ const q=new URLSearchParams(location.search), d=q.get('ag'); if(d) a={d,t:g2agTrilha(location.search)};
    else if(q.get('view')==='agrupada'&&sp.ag.some(x=>x.pq==='onde')) a={d:'onde',t:[]}; }catch(e){ a=null; }
  if(!g2agOk(sp,a)){ a=null; try{ const x=JSON.parse(localStorage.getItem(g2agChave(sp))||'null'); if(g2agOk(sp,x)) a={d:x.d,t:x.t}; }catch(e){ a=null; } }
  const all=Object.assign({},self.state.g2||{}); all[sp.id]=Object.assign({},all[sp.id]||{},{ag:a,agpf:pf},troca?{agm:false,agx:null}:{}); self.state.g2=all;
  if(troca) try{ history.replaceState(history.state,'',g2agUrl(location.pathname,location.search,location.hash,a)); }catch(e){}
  return a; }
function g2agGrava(self,sp,a){ try{ if(a) localStorage.setItem(g2agChave(sp),JSON.stringify(a)); else localStorage.setItem(g2agChave(sp),'null'); }catch(e){}
  try{ history.replaceState(history.state,'',g2agUrl(location.pathname,location.search,location.hash,a)); }catch(e){}
  g2set(self,sp.id,{ag:a,agpf:g2pfk(),agm:false,agx:null}); }
// lista vazia (O.S. de processo sem talhão) vira "Sem talhão", como o valor ausente: a linha nunca some do agrupamento (Σ grupos = total)
// V2-3: grade marcada pelo quadro (visoes_marcas) agrupa pela própria coluna (D.ck[i]); data agrupa por mês (D.dt[i]); multivalor conta em
// cada membro. Sem D.ck, os níveis vêm da linha (r.g), como na O.S.
const G2_MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
function g2agCol(r,D,i,sp){ const c=sp&&sp.cols.find(x=>x.k===D.ck[i]); if(!c) return [undefined];
  if(D.dt&&D.dt[i]){ const m=String((r.v||{})[c.k]||'').match(/^(\d{4})-(\d{2})/); return [m?(G2_MES[Number(m[2])-1]+'/'+m[1].slice(2)):undefined]; }
  const mm=g2mem(r,c); if(mm&&mm.length) return mm.map(x=>String(x.l||x.id)); const t=g2text(r,c); return [(t==='—'||t==='-')?undefined:t]; }
function g2agSo(r,a,D,i,sp){ if(D.ck&&D.ck[i]&&D.dt&&D.dt[i]){ const c=sp&&sp.cols.find(x=>x.k===D.ck[i]); const m=c&&String((r.v||{})[c.k]||'').match(/^(\d{4}-\d{2})/); return m?m[1]:undefined; }
  return ((r.gs||{})[a.d]||[])[i]; }
function g2agVals_(r,a,D,i,sp){ if(D.ck&&D.ck[i]) return g2agCol(r,D,i,sp).map(y=>(y===undefined||y===null||String(y).trim()==='')?'Sem '+D.niv[i].toLowerCase():String(y));
  const g=(r.g||{})[a.d]; const x=g?g[i]:undefined; const xs=Array.isArray(x)?(x.length?x:[undefined]):[x]; return xs.map(y=>(y===undefined||y===null||y==='')?'Sem '+D.niv[i].toLowerCase():String(y)); }
// a O.S. de T1 e T2 sob o filtro Talhão = T1 entra só no grupo T1 (Codex 6168779649, achado 2): o nível com coluna de filtro (D.fc[i]) usa só
// os membros escolhidos no filtro; o vínculo completo continua no detalhe da O.S., e o total conta cada O.S. uma vez
function g2agValsF(r,a,D,i,sp,st){ const vs=g2agVals_(r,a,D,i,sp), fk=(D.fc||[])[i], f=fk&&st&&st.f&&st.f[fk];
  if(!f||!f.length) return vs; const c=sp.cols.find(x=>x.k===fk), m=c?g2mem(r,c):null; if(!m||!m.length) return vs;
  const k=m.filter(x=>f.indexOf(x.id)>=0).map(x=>String(x.l||x.id)); return k.length?k:vs; }
// recorte da trilha para as outras formas (Kanban, Calendário, Carga): as linhas dentro da trilha escolhida, com o mesmo filtro por nível
// (D.fc) da Tabela; null sem agrupamento ou sem trilha. Sem efeito colateral (VISOES-2 §3.4: toda visão lê o mesmo recorte)
function g2agNoTrilha(self,sp,st,rows){ if(!g2agTem(sp)||sp.suspende) return null; const a=g2agLer(self,sp); if(!a||!a.t.length) return null; const D=sp.ag.find(x=>x.pq===a.d); if(!D) return null;
  const lv=Math.min(a.t.length,D.niv.length); return rows.filter(r=>a.t.slice(0,lv).every((t,i)=>g2agValsF(r,a,D,i,sp,st).indexOf(t)>=0)); }
function g2agRows(self,sp,st,rows){ const a=g2agLer(self,sp); if(!a) return {rows,a:null}; const D=sp.ag.find(x=>x.pq===a.d), niv=D.niv.length; let lv=Math.min(a.t.length,niv);
  let base=rows.filter(r=>a.t.slice(0,lv).every((t,i)=>g2agValsF(r,a,D,i,sp,st).indexOf(t)>=0)); const auto=[];
  // nível com um valor só no recorte (uma fazenda) não pede escolha: desce sozinho, e o valor aparece na trilha
  while(lv<niv-1){ const vs=new Set(); base.filter(r=>g2match(r,sp,st)).forEach(r=>g2agValsF(r,a,D,lv,sp,st).forEach(k=>vs.add(k))); if(vs.size!==1) break;
    const k=[...vs][0]; auto.push(k); base=base.filter(r=>g2agValsF(r,a,D,lv,sp,st).indexOf(k)>=0); lv++; }
  const path=a.t.slice(0,Math.min(a.t.length,niv)).concat(auto);
  if(lv>=niv) return {rows:base,a,D,lv,base,path};   // último nível: as linhas, filtradas pela trilha
  const gs={}, ord=[], ok={}, c0=sp.cols[0].k, somas=sp.cols.filter(c=>c.agg==='sum');
  base.filter(r=>g2match(r,sp,st)).forEach(r=>{ const vs=g2agValsF(r,a,D,lv,sp,st), so=g2agSo(r,a,D,lv,sp);
    vs.forEach(k=>{ if(!gs[k]){ gs[k]=[]; ord.push(k); } gs[k].push(Object.assign({},r,{id:r.id+'@'+k})); if(so!==undefined&&so!==null&&(ok[k]===undefined||String(so)<String(ok[k]))) ok[k]=so; }); });
  // ordem: a chave própria do nível quando a linha traz (r.gs: mês e semana em ordem de calendário), senão o nome
  ord.sort((x,y)=>(ok[x]!==undefined&&ok[y]!==undefined&&String(ok[x])!==String(ok[y]))?(String(ok[x])<String(ok[y])?-1:1):x.localeCompare(y,'pt-BR',{numeric:true}));
  const out=ord.map(k=>{ const kids=gs[k], n=new Set(kids.map(x=>x.id.split('@')[0])).size; const row={id:'grp@'+k,ro:true,nosel:true,grp:{k,lv},kids,v:{},s:{},p:{},m:{}};
    row.v[c0]=k; row.s[c0]=k; row.p[c0]=[{k:'act',t:k,fn:sp.id+'_agdesce:'+encodeURIComponent(k),desce:true,al:'Descer em '+k+' ('+D.niv[lv].toLowerCase()+')'}];
    const c1=g2colsVis(self,sp)[1]; if(c1){ row.p[c1.k]=[{k:'mut',t:n+' '+(n>1?(D.plural||'itens'):(D.um||'item'))}]; }
    somas.forEach(c=>{ const tot=kids.reduce((s2,x)=>s2+(Number((x.v||{})[c.k])||0),0); row.v[c.k]=tot; });
    return row; });
  // grupos começam abertos a cada novo agrupamento ou nível (a seta recolhe no lugar)
  // defeito G: a chave inclui o nível que desceu sozinho (trocar Fazenda muda o nível e os grupos novos nascem abertos)
  const ch=a.d+'|'+path.join('/')+'|'+lv; if(st.agx!==ch){ const x={}; out.forEach(r=>{ x[r.id]=true; }); const all=Object.assign({},self.state.g2||{}); all[sp.id]=Object.assign({},all[sp.id]||{},{x,agx:ch}); self.state.g2=all; }
  return {rows:out,a,D,lv,base,path}; }
const G2_AG_ICO={oque:'O quê',quem:'Quem',quando:'Quando',onde:'Onde'};
function g2agMenuVals(self,sp,v,R){ const id=sp.id; if(!g2agTem(sp)){ v[id+'_aghas']=false; v[id+'_agmenu']=false; v[id+'_agtr']=[]; v[id+'_agtrilha']=false; return; }
  const st=g2st(self,id), a=R.a, D=R.D;
  v[id+'_aghas']=true; v[id+'_agl']=a?D.l:''; v[id+'_agexp']=String(!!st.agm); v[id+'_agmenu']=!!st.agm;
  ['oque','quem','quando','onde'].forEach(k=>{ v[id+'_agi_'+k]=!!a&&a.d===k; }); v[id+'_agi_0']=!a;
  // defeito D (390 × 844): o menu abria abaixo da borda; agora cabe na janela (sobe quando falta espaço embaixo; rola por dentro se ainda faltar)
  const P=st.agpos||{x:0,y:0,t:0}, W=260, vw=(typeof window!=='undefined'?window.innerWidth:1440), vh=(typeof window!=='undefined'?window.innerHeight:900);
  const Hm=(sp.ag.length+1)*50+16; let top=P.y+6; if(top+Hm>vh-8) top=Math.max(8,Math.min((P.t||P.y)-Hm-6,vh-Hm-8));
  v[id+'_agpos']='top:'+top+'px;left:'+Math.max(8,Math.min(P.x,vw-W-8))+'px;max-height:'+Math.max(160,vh-top-8)+'px;overflow-y:auto;';
  v[id+'_agtog']=(e)=>{ const el=e&&e.currentTarget; const rr=el&&el.getBoundingClientRect?el.getBoundingClientRect():{left:0,bottom:0}; const ab=!g2st(self,id).agm;
    g2set(self,id,ab?{agm:true,agpos:{x:rr.left,y:rr.bottom,t:rr.top||0}}:{agm:false}); if(ab) setTimeout(()=>{ const b=document.querySelector('[data-g2agm="'+id+'"] [aria-checked=true]')||document.querySelector('[data-g2agm="'+id+'"] button'); if(b) b.focus(); },0); };
  const fecha=()=>{ g2set(self,id,{agm:false}); setTimeout(()=>{ const b=document.querySelector('[data-g2agb="'+id+'"]'); if(b) b.focus(); },0); };
  v[id+'_agfecha']=fecha; v[id+'_agkey']=(e)=>{ if(!e) return; if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); fecha(); return; }
    // defeito H: menu (role=menu) anda por ↓ ↑ Home End, como o padrão ARIA de menu; Tab continua saindo
    const m=document.querySelector('[data-g2agm="'+id+'"]'), its=m?[...m.querySelectorAll('[role^=menuitem]')]:[], i=its.indexOf(document.activeElement); let j=null;
    if(e.key==='ArrowDown') j=(i+1)%its.length; else if(e.key==='ArrowUp') j=(i-1+its.length)%its.length; else if(e.key==='Home') j=0; else if(e.key==='End') j=its.length-1;
    if(j!==null&&its[j]){ e.preventDefault(); its[j].focus(); } };
  v[id+'_agops']=[{pq:'',t:'Sem agrupar',niv:''}].concat(sp.ag.map(x=>({pq:x.pq,t:x.l,niv:x.niv.length>1?x.niv.join(' › '):''}))).map(o=>({t:o.t,niv:o.niv,temNiv:!!o.niv,on:String((a?a.d:'')===o.pq),
    i0:!o.pq,iOque:o.pq==='oque',iQuem:o.pq==='quem',iQuando:o.pq==='quando',iOnde:o.pq==='onde',perg:G2_AG_ICO[o.pq]||'',
    go:()=>{ g2agGrava(self,sp,o.pq?{d:o.pq,t:[]}:null); setTimeout(()=>{ const b=document.querySelector('[data-g2agb="'+id+'"]'); if(b) b.focus(); },0); }}));
  // trilha: "Todas › Lagoa Grande › T4"; cada item volta ao nível dele; o último é onde se está
  const sobe=(n)=>{ const a2=g2st(self,id).ag; if(!a2) return; g2agGrava(self,sp,{d:a2.d,t:a2.t.slice(0,n)}); };
  const path=(R.path||[]); v[id+'_agtrilha']=!!a&&path.length>0;
  v[id+'_agtr']=a?[{t:'Todas',go:()=>sobe(0)}].concat(path.slice(0,-1).map((x,i)=>({t:x,go:()=>sobe(i+1)}))):[];
  v[id+'_agatual']=a&&path.length?path[path.length-1]:'';
  v[id+'_agnivel']=a?(R.lv<D.niv.length?'por '+D.niv[R.lv].toLowerCase():''):'';
  v[id+'_agdesce']=(kEnc)=>{ const a2=g2st(self,id).ag; if(!a2) return; let k=kEnc; try{ k=decodeURIComponent(kEnc); }catch(e){} g2agGrava(self,sp,{d:a2.d,t:path.concat([k])});
    setTimeout(()=>{ const n=document.querySelector('[data-g2agtr="'+id+'"] b'); if(n){ n.setAttribute('tabindex','-1'); n.focus(); } },0); };
  // Esc sobe um nível (fora de campo, menu ou painel aberto)
  if(typeof window!=='undefined'){ window.__g2agSobe=window.__g2agSobe||{}; window.__g2agSobe[id]=()=>{ const a2=g2st(self,id).ag; if(a2&&a2.t.length){ sobe(a2.t.length-1); return true; } return false; };
    if(!window.__g2agEsc){ window.__g2agEsc=1; document.addEventListener('keydown',(e)=>{ if(e.key!=='Escape'||e.defaultPrevented) return; const t=e.target;
      if(t&&t.closest&&t.closest('input,select,textarea,[role=dialog],aside,[role=menu]')) return; if(document.querySelector('aside[role=dialog],[role=dialog][aria-modal=true]')) return;
      for(const k in window.__g2agSobe){ if(window.__g2agSobe[k]()){ e.preventDefault(); return; } } }); } } }
function g2vals(self,sp,v,mask){
  const id=sp.id, rows0=g2disp(self,sp), added=self.state.added||{};
  // sp.suspende (posto pela tela: recorte do Painel na O.S.): a grade lê o estado sem busca, filtros nem agrupamento, sem apagá-los; a busca
  // some até o recorte acabar. O agrupamento e a trilha também ficam suspensos: senão a trilha esconderia O.S. do recorte (mesma classe do S3 6167883199)
  const susp=(x)=>sp.suspende?Object.assign({},x,{q:'',f:{},qv:''}):x;
  const st0=susp(g2stBusca(self,id,g2st(self,id)));
  const AG=(g2agTem(sp)&&!sp.suspende)?g2agRows(self,sp,st0,rows0):{rows:rows0,a:null}, rows=AG.rows, st=susp(g2stBusca(self,id,g2st(self,id)));   // VISOES-2 §3.3
  const arv=!!(sp.tree||AG.a);   // V2-3: grade plana do quadro só ganha a seta do grupo quando está agrupada
  const flat=g2flat(sp,st,g2qrows(sp,st,rows),mask,added); const ed=sp.edit||{m:'none'}; const editable=ed.m&&ed.m!=='none';
  g2qvals(self,sp,v,st,rows,added);
  const so=st.so||sp.so||{};
  const cols=g2colsVis(self,sp); g2cvVals(self,sp,v,cols); v[id+'_ncols']=cols.length+(sp.sel?1:0)+(sp.del?1:0);   // trilhas da grade = colunas visíveis
  v[id+'_head']=cols.map((c,ci)=>({l:c.l, tt:c.ajuda||g2glossCol(sp,c,rows), un:c.un||'', cls:(ci===0?'g2c0':''), st:'display:flex;align-items:center;gap:2px;justify-content:'+(c.a==='r'?'flex-end':'flex-start')+';'+(ci===0?'position:sticky;left:0;z-index:2;background:#F4F6F3;box-shadow:1px 0 0 #E4E9E5;':''),
     arrow:(so.k===c.k?(so.d?'▼':'▲'):'⇅'), astyle:(so.k===c.k?'color:#1E7A4C;':'color:#B7C1BA;'), sortLabel:'Ordenar por '+c.l,
     sort:()=>{ const cur=g2st(self,id).so||sp.so||{}; let nx; if(cur.k!==c.k) nx={k:c.k,d:false}; else if(!cur.d) nx={k:c.k,d:true}; else nx={}; g2set(self,id,{so:nx}); },
     // 15/10/2026 (proprietário: "troque o ícone de filtrar a coluna por um ícone mais intuitivo de filtro"): funil vazado sem filtro;
     // com filtro, funil cheio verde (sem número: o funil cheio basta; a dica e o leitor de tela dizem "filtro ativo")
     fcolor:(((st.f||{})[c.k]||[]).length?'#1E7A4C':'#8A968E'),
     ffill:(((st.f||{})[c.k]||[]).length?'currentColor':'none'),
     flabel:'Filtrar '+c.l, ftit:'Filtrar '+c.l+(((st.f||{})[c.k]||[]).length?' · filtro ativo':''),   // nome fixo; o estado vai na dica (descrição)
     fmenu:(e)=>{ const cur=g2st(self,id).fmc; if(cur===c.k){ g2set(self,id,{fmc:null}); return; }
       const el=e&&e.currentTarget; const rr=el&&el.getBoundingClientRect?el.getBoundingClientRect():{left:0,right:0,bottom:0};
       g2set(self,id,{fmc:c.k,fpos:{x:rr.left,xr:rr.right,y:rr.bottom,dir:c.a==='r'},fmd:null,fmq:''}); setTimeout(()=>{ const q=document.getElementById('g2fq_'+id); if(q) q.focus(); },0); }}));
  // valores do filtro aberto
  const fmc=st.fmc; const fcol=sp.cols.find(c=>c.k===fmc);
  if(fcol){ const cnt={}, lab={}; const leaf=(list)=>list.forEach(r=>{ if(r.livre||r.fora) return; if(r.kids&&r.kids.length) leaf(r.kids); if(!(r.kids&&r.kids.length)||sp.tree===false||!sp.tree||(fcol.niv0&&r.tal)){
      const m=g2mem(r,fcol); const ok=g2ordk(r,fcol)!==undefined; g2fkeys(r,fcol).forEach(k=>{ cnt[k]=(cnt[k]||0)+1; if(!lab[k]){ const x=m&&m.find(y=>y.id===k); lab[k]=x?x.l:((ok&&k!=='(vazio)')?(g2text(r,fcol)||k):k); } }); } }); leaf(rows);
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
      clear:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[fmc]; g2set(self,id,{f,fmc:null,fmd:null,fmq:''}); }, close:fechar,
      podeOcultar:g2cvTem(sp)&&sp.cols.length>5&&fmc!==sp.cols[0].k, ocultar:()=>{ const cur=new Set(g2colsVis(self,sp).map(x=>x.k)); cur.delete(fmc); fechar(); g2cvGrava(self,sp,[...cur]); }};
  } else v[id+'_fm']={open:false,vals:[]};
  const total=(sp.total!==false) && sp.cols.some(c=>c.agg);
  const qn=g2norm((st.q||'').trim()), visK=new Set(cols.map(c=>c.k));
  // VISOES-2 C3: busca que casa só em coluna oculta diz na linha onde casou (a coluna continua valendo para a busca)
  const ondeCasou=(r)=>{ if(!qn||!g2cvTem(sp)||r.grp) return ''; if(cols.some(c=>g2norm(g2text(r,c)).indexOf(qn)>=0)) return ''; const oc=sp.cols.filter(c=>!visK.has(c.k)&&g2norm(g2text(r,c)).indexOf(qn)>=0).map(c=>c.l); return oc.length?'encontrado em: '+oc.join(', '):''; };
  const sicoKs=sp.sico?(sp.sico.ks||[sp.sico.k]).filter(k=>!visK.has(k)):[];
  v[id+'_rows']=flat.map(({r,lvl,has})=>{
    const cells=[]; const exp=(st.x||sp.x0||{}); const casou=ondeCasou(r); const sicoP=sicoKs.map(k=>g2sicoPart(r,sp,k)).filter(Boolean);
    // linha livre (convite para cadastrar, ex.: talhão sem cultivo): sem seleção e sem lixeira
    if(sp.sel&&(r.livre||r.fora||r.nosel)) cells.push({isSel:false,isData:false,isDel:false,st:'',cls:''}); else if(sp.sel) cells.push({isSel:true,isData:false,isDel:false,cls:'',on:!!(st.sel||{})[r.id],selLabel:'Selecionar '+g2text(r,sp.cols[0]),
      tog:()=>{ const s2=Object.assign({},g2st(self,id).sel||{}); s2[r.id]=!s2[r.id]; g2set(self,id,{sel:s2}); },st:'padding:6px 4px 6px 12px;'});
    cols.forEach((c,ci)=>{
      const empty=(has && ci>0 && !(r.p&&r.p[c.k]) && (!r.v || r.v[c.k]===undefined || r.v[c.k]===''));
      const raw0=empty?[]:((r.p&&r.p[c.k]&&r.p[c.k].length)?r.p[c.k]:[{k:(ci===0&&lvl===0&&has?'b':'txt'),t:g2fmt(r.v?r.v[c.k]:'',c)}]);
      // partes próprias (p) com número puro ganham a unidade (cópia: r.p não muda)
      const raw1=c.un?raw0.map(p=>(p&&typeof p.t==='string'&&['txt','b','cn','chip'].indexOf(p.k)>=0)?Object.assign({},p,{t:g2unf(p.t,c)}):p):raw0;
      const raw=(ci===0&&sicoP.length)?sicoP.concat(raw1):raw1;
      const cell={isSel:false,isData:true,isDel:false,cls:(ci===0?'g2c0':'')+(c.nr?' g2nr':'')+(c.a==='r'?' g2celn':''),parts:(ci===0&&casou?raw.concat([{k:'br'},{k:'mut',t:casou}]):raw).map((p,i,arr)=>g2part(g2semSep(arr,i),v)),pw:'max-width:'+(c.w||340)+'px;',
        st:(c.nr?'padding:0 2px;':'padding:6px 8px;')+(c.a==='r'?'text-align:right;justify-content:flex-end;white-space:nowrap;font-variant-numeric:tabular-nums;':'')+(ci===0&&arv?'padding-left:'+(8+lvl*20)+'px;':'')+(ci===0?'position:sticky;left:0;z-index:1;background:inherit;box-shadow:1px 0 0 #E4E9E5;':'')};
      if(ci===0 && arv){ cell.hasCaret=true; cell.caretOk=has; cell.caretNo=!has; const open=!!exp[r.id]||(g2filtering(st)&&has);
        cell.caretSym=open?'▾':'▸'; cell.caretExp=String(open); cell.caretLabel=(open?'Recolher ':'Expandir ')+g2text(r,c);
        cell.toggle=()=>{ const x=Object.assign({},g2st(self,id).x||sp.x0||{}); x[r.id]=!x[r.id]; g2set(self,id,{x}); }; }
      else { cell.hasCaret=false; }
      cells.push(cell); });
    if(sp.del&&(r.livre||r.fora||r.nosel)) cells.push({isSel:false,isData:false,isDel:false,st:'',cls:''}); else if(sp.del){ const asking=(st.cf===r.id); cells.push({isSel:false,isData:false,isDel:true,cls:'',asking,notAsking:!asking,st:'padding:4px 10px;white-space:nowrap;',
        delLabel:'Excluir '+g2text(r,sp.cols[0]), ask:()=>g2set(self,id,{cf:r.id}), no:()=>g2set(self,id,{cf:null}),
        yes:()=>{ const g2_0=self.state.g2; const rs=g2clone(g2rows(self,sp)); const rm=(list)=>{ const i=list.findIndex(x=>x.id===r.id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&rm(x.kids)); }; rm(rs); g2set(self,id,{rows:rs,cf:null}); self.setState({g2toast:'Excluído: '+g2text(r,sp.cols[0])}); if(self.g2after) self.g2after(id,rs,null); g2persiste(self,id,g2_0,{cf:null},'Não excluído'); }}); }
    const canOpen=editable && !(ed.leafOnly && has) && !r.fora && !(r.nosel && !r.dr);
    return {id:r.id, cls:'g2r'+(canOpen?' g2ed':'')+(st.fl===r.id?' g2flash':'')+(lvl>0?' g2kid':''), tab:(canOpen&&!r.drDup)?'0':'-1',
      open:(e)=>{ if(canOpen) g2open(self,sp,r.id,e); }, key:(e)=>{ if(!canOpen || !e || (e.key!=='Enter'&&e.key!==' ')) return; const t=e.target; if(t&&t.closest&&t.closest('a,button,input,select,textarea,label,[data-noedit],.g2nr')) return; e.preventDefault(); g2open(self,sp,r.id,null); }, cells}; });
  v[id+'_count']=flat.filter(x=>x.lvl===0).length; v[id+'_all']=rows.length;
  if(AG.a){ const ids=new Set(); (AG.base||[]).forEach(r=>{ if(g2match(r,sp,st,mask,added)) ids.add(String(r.id)); }); v[id+'_count']=ids.size; v[id+'_all']=rows0.length; }   // agrupado: itens distintos do recorte, não grupos
  g2agMenuVals(self,sp,v,AG);
  v[id+'_empty']=flat.length===0; v[id+'_some']=flat.length>0;
  v[id+'_q']=st.q||''; v[id+'_setq']=(e)=>g2set(self,id,{q:e.target.value});
  v[id+'_qon']=!g2qSeg(self,id)&&!sp.suspende; v[id+'_qlab']=(self.__g2qL===id&&self.__g2qS)?'Buscar nesta tela':'Buscar nesta tabela';
  v[id+'_filtered']=g2filtering(st)||!!(sp.qf&&st.qv);
  v[id+'_clear']=()=>{ g2set(self,id,{q:'',f:{},qv:''}); if(g2qSeg(self,id)) g2set(self,self.__g2qL,{q:''}); };   // a busca da tela também filtra esta tabela
  v[id+'_fchips']=Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).map(k=>{ const c=sp.cols.find(x=>x.k===k)||{l:k}; return {t:c.l+': '+st.f[k].map(x=>g2flab(rows,c,x)).join(', '), rm:()=>{ const f=Object.assign({},g2st(self,id).f||{}); delete f[k]; g2set(self,id,{f}); }}; });
  { const soA=st.so||sp.so||{}, cs=soA.k&&sp.cols.find(c=>c.k===soA.k); if(cs&&!cols.some(c=>c.k===cs.k)) v[id+'_fchips'].push({t:'Ordenado por '+cs.l+(soA.d?' ▼':' ▲'), rm:()=>g2set(self,id,{so:{}})}); }   // VISOES-2 C3: ordenação por coluna oculta à vista
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
  // sp.totf (opcional, posto pela tela em tempo de execução): total vindo do serviço de domínio quando a soma simples não serve (R$/ha, unidade);
  // recebe a coluna, as linhas de 1º nível visíveis e o critério do filtro da grade (F.filt, F.match: a mesma regra da lista, para o serviço
  // totalizar o recorte filtrado e não a linha-pai inteira — revisão Codex V58-TOTAL-FILTRO-01); undefined = soma padrão. agg 'fn' = só o serviço.
  if(total){ const topo=flat.filter(x=>x.lvl===0).map(x=>x.r); const F={filt:g2filtering(st),match:(r)=>g2match(r,sp,st,mask,added)};
    v[id+'_tot']=cols.map((c,ci)=>{ const h=(ci&&c.agg&&typeof sp.totf==='function')?sp.totf(c,topo,F):undefined;
      const s=(h===undefined&&c.agg&&c.agg!=='fn')?g2sum(sp,flat,c):null; return {t:(ci===0?'Total':(h!==undefined?h:(s===null?'':g2fmt(s,c)))), cls:(ci===0?'g2c0':''), st:'padding:8px 10px;font-weight:800;'+(ci===0?'position:sticky;left:0;z-index:1;background:#F4F6F3;':'')+(c.a==='r'?'text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;':'')}; });
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
    F.nerr=Object.keys(fm.errs||{}).length; F.hasErr=F.nerr>0; F.errG=fm.errG||''; F.errP=fm.errP||'Não salvo'; F.hasErrG=!!fm.errG;
    F.save=()=>g2save(self,sp); F.cancel=()=>g2close(self,sp); F.close=()=>g2close(self,sp);
    F.discard=()=>{ g2set(self,id,{fm:null}); self.setState({g2toast:'Alterações descartadas'}); }; F.keep=()=>{ const cur=g2st(self,id).fm; g2set(self,id,{fm:Object.assign({},cur,{warn:false})}); };
    F.key=(e)=>{ if(e && e.key==='Escape'){ e.preventDefault(); g2close(self,sp); } };
  }
  v[id+'_F']=F; }
// barra lateral recolhível: a escolha vale entre telas (guardada no navegador de quem usa). Em tela estreita (até 1023 px:
// celular, tablet em pé, zoom de 200 %) o menu aberto passa por cima do conteúdo e é passageiro: toda tela começa com ele
// recolhido (a escolha "aberto" do computador não cobre o título no estreito), abrir/fechar ali não muda a escolha guardada,
// e ao estreitar a janela (girar o aparelho) ele recolhe sem recarregar.
const G2_ESTREITO='(max-width: 1023px)';
function g2estreito(){ try{ return window.matchMedia(G2_ESTREITO).matches; }catch(e){ return false; } }
function g2menuRec(){ return true; }   // 13/10/2026 (proprietário): a barra lateral fica sempre recolhida, só com ícones e dica, sem expandir
// <perfis> Perfil de demonstração (sem login; PRD 2.1): quem age nas decisões que exigem papel. Vale entre telas, no navegador de quem usa;
// demonstra a experiência, não é segurança (no software o servidor tira o ator da sessão). Pessoas e papéis: CF-01 e telas vizinhas.
// O papel vem sempre desta lista (g2pf), nunca do objeto que o comando recebe. Bloco único, lido também pelos testes sem navegador.
// G2_PERFIS é o PADRÃO (sem estado de Configurações); o efetivo (g2perfis) lê c.conf do cenário salvo: o CF-01 concede e retira papel,
// convida e desativa (CONF-01 R2). G2_ALCADAS diz quem decide cada comando e é lida pelos próprios comandos (cenExigeAlc, R7).
const G2_PERFIS=[{k:'Ana',t:'Ana · Gestora e RT',papeis:{gestor:'gestora',agronomo:'agrônoma'}},{k:'Caio',t:'Caio · PCP',papeis:{pcp:'PCP'}},
  {k:'Rui',t:'Rui · Almoxarife e expedição',papeis:{almoxarife:'almoxarife',expedicao:'expedição'}},{k:'Paula',t:'Paula · Conferência',papeis:{almoxarife:'almoxarife',conferente:'conferência'}},{k:'Zé',t:'Zé · Mecânico',papeis:{mecanico:'mecânico'}},
  {k:'Otávio',t:'Otávio · Manutenção (PCM)',papeis:{pcm:'responsável de manutenção'}},
  {k:'João',t:'João · Irrigante (eletricista NR-10)',papeis:{eletricista:'irrigante'}},   /* PCM simplificado (05/10, D-20): Ver como da Manutenção = Otávio · Zé · João · Ana; João executa as OMs de eletricista (revisão 09/10, A8) */
  {k:'Igor',t:'Igor · Produção',papeis:{producao:'responsável de produção'}},   // BEN-1: beneficiamento
  {k:'Dora',t:'Dora · Comercial',papeis:{comercial:'comercial'}},{k:'Marta',t:'Marta · Qualidade',papeis:{qualidade:'qualidade'}}];   // Comercial (D-C13): Dora vende, reserva e programa carga; Rui confirma a saída física; Ana (gestora) pode tudo e aprova crédito. Marta (Qualidade, R-13 da Colheita e BEN-1): libera lote em inspeção, inclusive o devolvido (A3 da revisão do Comercial)
// catálogo de papéis (CONF-D03): papel = permissão de decidir; função e habilidade ficam no CD-04. Rótulo pelo gênero da pessoa (CONF0.pessoas[].fem)
const G2_PAPEIS=[{k:'gestor',t:'Gestor',m:'gestor',f:'gestora'},{k:'agronomo',t:'Agrônomo',m:'agrônomo',f:'agrônoma'},{k:'pcp',t:'PCP',m:'PCP',f:'PCP'},
  {k:'almoxarife',t:'Almoxarife',m:'almoxarife',f:'almoxarife'},{k:'conferente',t:'Conferência',m:'conferência',f:'conferência'},{k:'mecanico',t:'Mecânico',m:'mecânico',f:'mecânica'},
  {k:'producao',t:'Produção',m:'responsável de produção',f:'responsável de produção'},{k:'qualidade',t:'Qualidade',m:'qualidade',f:'qualidade'},   /* BEN-1 (merge CONF × BEN) */
  {k:'expedicao',t:'Expedição',m:'expedição',f:'expedição'},{k:'pcm',t:'Manutenção (PCM)',m:'responsável de manutenção',f:'responsável de manutenção'},   /* v57: papéis da v56 (Comercial e PCM) no catálogo, senão o perfil efetivo os descarta */
  {k:'eletricista',t:'Irrigante (NR-10)',m:'irrigante',f:'irrigante'},{k:'comercial',t:'Comercial',m:'comercial',f:'comercial'},
  {k:'direcao',t:'Direção',m:'direção',f:'direção'}];
// alçadas (CONF-01 §4, R7): papeis/modo = quem decide ('todos' os papéis ou 'um' deles); acima = nível acima do limite; edita = o que o CF-01 muda
// ('papel', 'lim', 'acima' ou '' = fixa, com o motivo em fixa). Versão e vigência vêm dos eventos de Configurações (c.conf); a v1 vale desde a implantação.
const G2_ALCADAS=[
  {id:'AL-01',t:'Liberar O.S. agrícola',cmd:'CMD-06',papeis:['gestor'],modo:'todos',edita:'papel',opc:['gestor','pcp','agronomo'],obs:'fora desta alçada: irrigação só com água, que libera pela prontidão (DEC-2609-10)',pend:'PEND-OS-01'},
  {id:'AL-02',t:'Aprovar a versão da O.S. e ajustar antes de liberar',cmd:'CMD-42',papeis:['agronomo'],modo:'todos',edita:'',fixa:'lei (receituário agronômico) e PRD 41'},
  {id:'AL-04',t:'Cancelar O.S. sem execução',cmd:'CMD-46',papeis:['gestor'],modo:'todos',edita:'',lim:'só sem realizado',fixa:'ordem com realizado não se cancela: dispensa o saldo (AL-05)'},
  {id:'AL-05',t:'Dispensar saldo da O.S.',cmd:'CMD-47',papeis:['gestor','agronomo'],modo:'todos',lim:20,un:'%',acima:{papeis:['direcao','agronomo'],modo:'todos'},edita:'lim',faixa:[1,100]},
  {id:'AL-09',t:'Aprovar ajuste de inventário',cmd:'Ajuste',papeis:['gestor'],modo:'todos',edita:'papel',opc:['gestor','direcao'],obs:'quem contou e aprova fica com revisão posterior',pend:'PEND-CTL-02'},
  {id:'AL-10',t:'Aceitar consumo informado',cmd:'CMD-50',papeis:['almoxarife','gestor'],modo:'um',lim:'a custódia',acima:{papeis:['gestor'],modo:'todos'},edita:'acima',opc:['gestor','direcao'],pend:'PEND-CTL-02'},
  {id:'AL-11',t:'Liberar lote da quarentena com laudo',cmd:'CMD-24',papeis:['gestor'],modo:'todos',edita:'',fixa:'qualidade do insumo: quem guarda o estoque não libera o próprio bloqueio'},
  {id:'AL-12',t:'Conferir o dia e decidir duplicidade de apontamento',cmd:'CMD-09 · conferência diária',papeis:['conferente'],modo:'todos',edita:'',fixa:'conferência separada de quem executa: quem apontou e decide a própria duplicidade fica com revisão posterior'},
  {id:'AL-13',t:'Conceder e retirar papel, convidar e desativar acesso',cmd:'Configurações',papeis:['gestor'],modo:'todos',edita:'',fixa:'protege o próprio controle (R3, R4, R5)'},
  {id:'AL-14',t:'Alterar alçada',cmd:'Configurações',papeis:['gestor'],modo:'todos',conf:{papeis:['gestor','direcao'],modo:'um'},edita:'',fixa:'protege o próprio controle; ampliar o próprio poder pede 2º aprovador (R10)'},
  {id:'AL-15',t:'Pagar fatura, mudar plano, desfazer, pedir proposta e contestar',cmd:'Assinatura e cobrança',papeis:['gestor'],modo:'todos',edita:'',fixa:'contrato e pagamento da organização; o backoffice (conciliar, resolver) é da plataforma (Admin plataforma)'},
  {id:'AL-17',t:'Publicar previsão de colheita',cmd:'Colheita (R-17)',papeis:['agronomo'],modo:'todos',edita:'papel',opc:['agronomo','gestor','pcp'],obs:'a contagem do campo não muda a previsão: só quem publica (a oferta do Comercial lê a publicada)'},
  {id:'AL-18',t:'Publicar referência técnica do plano operacional',cmd:'CONTROLE-02 F2 (comando do PR #58)',papeis:['gestor'],modo:'todos',edita:'',fixa:'contrato da CONTROLE-02 F2 (6147460986): gestor, fixo nesta fatia',obs:'publicar registra a versão de referência: não aprova orçamento nem libera O.S. (alçada própria, sem reaproveitar a de orçamento ou de O.S.)'}];
const G2_PERFIL_KEY='safrion.perfilDemo'; let G2_PERFIL_MEM='';
// 14/10 (proprietário: "me coloque sempre no perfil que tem todos acessos para testar tudo"): perfil de teste com todos os papéis do catálogo.
// Fica fora das pessoas (g2perfis): não entra em "quem decide", no cadastro nem nas alçadas; a casca do artefato o põe a cada abertura.
// Não é segurança de acesso; para testar um papel isolado, troca-se o perfil no avatar.
const G2_TODOS_K='Proprietário';
function g2todos(){ if(!g2todos._v){ const papeis={}; G2_PAPEIS.forEach(x=>{ papeis[x.k]=x.m; }); g2todos._v={k:G2_TODOS_K,t:'Proprietário · todos os papéis (teste)',papeis,todos:true}; } return g2todos._v; }
// estado de Configurações: c.conf do cenário salvo (talhao-os-cenario-v1), válido só com a versão deste build (CONF0.v); ausente → padrão.
// Cache pelo texto salvo e pelo tamanho de G2_PERFIS (os testes injetam perfis): g2pf roda muitas vezes por desenho. Nunca chamado no carregamento.
const G2_CF={raw:null,conf:null,src:undefined,np:-1,pf:null};
function g2confOk(c){ if(!c||!c.conf||typeof CONF0==='undefined'||c.conf.v!==CONF0.v) return false;
  return c.v===((typeof CEN0!=='undefined')?CEN0.v:((typeof ASSIN_CENV!=='undefined')?ASSIN_CENV:null)); }
function g2conf(){ if(typeof CONF0==='undefined') return null; let raw=null; try{ raw=localStorage.getItem('talhao-os-cenario-v1'); }catch(e){ raw=null; }
  if(raw===null){ const m=(typeof CEN_MEM!=='undefined')?CEN_MEM:null; return (m&&g2confOk(m))?m.conf:null; }   /* sem nada salvo: o cenário da página (cenGet) */
  if(raw!==G2_CF.raw){ G2_CF.raw=raw; let c=null; try{ c=JSON.parse(raw); }catch(e){ c=null; } G2_CF.conf=(c&&g2confOk(c))?c.conf:null; }
  return G2_CF.conf; }
function g2papRot(k,papel,fem){ const d=G2_PERFIS.find(p=>p.k===k); if(d&&d.papeis[papel]) return d.papeis[papel]; const P=G2_PAPEIS.find(x=>x.k===papel); return P?(fem?P.f:P.m):papel; }
// perfis efetivos de um estado (R2): sem conf, exatamente G2_PERFIS; com conf, quem tem acesso Ativo e ao menos um papel (ordem de G2_PERFIS, depois a do CD-04)
function g2perfisDe(conf){ if(!conf||typeof CONF0==='undefined') return G2_PERFIS; const out=[], vis={};
  const add=(p)=>{ if(vis[p.k]) return; vis[p.k]=1; const e=(conf.pessoas||{})[p.id]; if(!e||e.a!=='ativo'||!(e.papeis||[]).length) return;
    const papeis={}; G2_PAPEIS.forEach(x=>{ if(e.papeis.indexOf(x.k)>=0) papeis[x.k]=g2papRot(p.k,x.k,p.fem); });
    const d=G2_PERFIS.find(q=>q.k===p.k); const igual=!!d&&Object.keys(d.papeis).sort().join()===Object.keys(papeis).sort().join();
    out.push({k:p.k,t:igual?d.t:p.k+' · '+Object.values(papeis).map((x,i)=>i?x:x.charAt(0).toUpperCase()+x.slice(1)).join(' e '),papeis}); };
  G2_PERFIS.forEach(d=>{ const p=CONF0.pessoas.find(x=>x.k===d.k); if(p) add(p); else if(!vis[d.k]){ vis[d.k]=1; out.push(d); } });   /* perfil fora do CD-04 (outra frente): segue o padrão */
  CONF0.pessoas.forEach(add); return out; }
function g2perfis(){ const conf=g2conf(); if(!conf) return G2_PERFIS;
  if(G2_CF.src!==conf||G2_CF.np!==G2_PERFIS.length){ G2_CF.src=conf; G2_CF.np=G2_PERFIS.length; G2_CF.pf=g2perfisDe(conf); } return G2_CF.pf; }
function g2pf(p){ const k=(typeof p==='string')?p:(p&&p.k); if(k===G2_TODOS_K) return g2todos(); return g2perfis().find(x=>x.k===k)||null; }   // perfil efetivo pela chave ("Ana" ou {k:'Ana'})
function g2perfil(){ let k=G2_PERFIL_MEM; try{ k=localStorage.getItem(G2_PERFIL_KEY)||k; }catch(e){} return g2pf(k)||g2perfis()[0]||G2_PERFIS[0]; }   // o desativado cai no 1º efetivo
function g2papel(p,papel){ const q=g2pf(p); return !!q&&[].concat(papel).every(x=>!!q.papeis[x]); }   // papel ou lista (todos exigidos)
function g2ator(p,papel){ const q=g2pf(p); if(!q) return ''; const n=[].concat(papel).map(x=>q.papeis[x]).filter(Boolean);
  return q.k+' ('+(n.length?n.join(' e '):Object.values(q.papeis)[0])+')'; }   // "Ana (gestora)" · "Ana (gestora e agrônoma)"; fora do cadastro: ''
function g2quem(papel){ return g2perfis().filter(p=>g2papel(p,papel)).map(p=>g2ator(p,papel)).join(' ou '); }
function g2umPapel(p,papeis){ const q=g2pf(p); return (q&&papeis.find(x=>!!q.papeis[x]))||''; }   // o primeiro papel da lista que o perfil tem (basta um): '' se nenhum
function g2quemUm(papeis){ return g2perfis().filter(p=>g2umPapel(p,papeis)).map(p=>g2ator(p,g2umPapel(p,papeis))).join(' ou '); }   // "Ana (gestora) ou Rui (almoxarife) ou …"
function g2mesma(a,b){ const n=s=>String(s||'').split(/[\s(]/)[0]; return !!n(a)&&n(a)===n(b); }   // "Ana" × "Ana (gestora)"
// alçada vigente: a linha de G2_ALCADAS com a mudança gravada em c.conf.alc (versão, papéis, limite ou nível acima)
function g2alcDe(conf,id){ const b=G2_ALCADAS.find(a=>a.id===id); if(!b) return null; const o=conf&&conf.alc&&conf.alc[id]; return Object.assign({v:1},b,o||{}); }
function g2alc(id){ return g2alcDe(g2conf(),id); }
function g2alcN(a,nivel){ return (a&&nivel==='acima'&&a.acima)?a.acima:a; }   // nível 'base' (padrão) ou 'acima' do limite
function g2papT(papeis){ return [].concat(papeis).map(x=>((G2_PAPEIS.find(y=>y.k===x)||{}).m||x)).join(' e '); }   // "gestor e agrônomo"
// quem decide a alçada (texto das telas, nunca nome fixo): sem titular ativo, diz onde conceder
function g2alcQuem(id,nivel){ const n=g2alcN(g2alc(id),nivel); if(!n) return ''; const q=n.modo==='um'?g2quemUm(n.papeis):g2quem(n.papeis);
  return q||(g2papT(n.papeis)+' sem titular: conceda em Configurações › Usuários e alçadas'); }
// UNID-PROD (R-U10, D-U13): unidade de produtividade por perfil × cultura, no navegador de quem usa (exibição; nunca vai para o cenário).
// Leitura e gravação em try/catch, com a memória da página como reserva (janela privada, testes sem navegador); o valor inicial é o Padrão.
const G2_UNID_KEY='safrion.pref.unidprod:'; const G2_UNID_MEM={};
function g2unidChave(cultura){ return G2_UNID_KEY+g2perfil().k+':'+cultura; }
function g2unidPref(cultura){ const k=g2unidChave(cultura); let v=G2_UNID_MEM[k]; try{ const x=localStorage.getItem(k); if(x) v=x; }catch(e){} return v||'padrao'; }
function g2unidSet(cultura,op){ const k=g2unidChave(cultura); G2_UNID_MEM[k]=String(op||'padrao'); try{ localStorage.setItem(k,G2_UNID_MEM[k]); }catch(e){} }
// </perfis>
// trocar o perfil (aqui ou em outra aba) fecha a confirmação ou o formulário de decisão aberto, montado para o perfil anterior (revisão do CTL-3,
// achado 1; dano evitado: a tela afirmar que decide quem não tem o papel). Cada tela diz o que fecha em self.g2perfilFecha (O.S., Mapa, Estoque)
function g2navvals(self,v,nav){ const rec=g2menuRec();
  const pf=g2perfil(); v.perfil_k=pf.k; v.perfil_ini=pf.k.charAt(0); v.perfil_opts=[{v:G2_TODOS_K,t:g2todos().t}].concat(g2perfis().map(p=>({v:p.k,t:p.t})));
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

// V55-RESP-01: altura do aviso temporário (role=status fixo no pé) medida no aviso real, com a quebra do texto na largura atual; 0 sem
// aviso. Com a área de ações em fluxo (altura curta) a área reserva a faixa dele no fim da rolagem e nos controles (ACOES_CSS: distância
// do pé + safe-area + esta altura), em vez de uma altura estimada. Não depende da altura da janela (abrir o teclado não a muda). Medida a
// cada troca do aviso (componentDidUpdate, no mesmo quadro) e no quadro do g2glob (redimensionar, rolar, mudar a página)
function g2avisoH(){ g2toastLugar(); try{ let h=0; document.querySelectorAll('[role=status]').forEach(t=>{ const cs=getComputedStyle(t); if(cs.position!=='fixed'||cs.bottom==='auto') return;
    const r=t.getBoundingClientRect(); if(r.height>2&&r.width>2) h=Math.max(h,Math.ceil(r.height)); });
  const v=h+'px', de=document.documentElement; if(de.style.getPropertyValue('--aviso-h')!==v) de.style.setProperty('--aviso-h',v); }catch(e){} }
// o aviso não cobre controle (UX-BEN35-AVISO-01, revisões Codex 6159767011 e 6160359100, S3). Fica centrado na área de conteúdo (main),
// nunca acima dela (cabeçalho, retorno do módulo) nem sobre a barra lateral, no pé (a âncora do G2_TOAST, guardada e sempre restaurada).
// Se ali cobrir um botão, link ou campo VISÍVEL (o fundo de tela inteira atrás de um painel não conta), sobe até a primeira faixa livre.
// Sem faixa livre (aviso de 4 linhas a 390 px sobre uma lista com um link a cada 44 px), RESERVA a faixa: o contêiner que rola debaixo
// dela deixa de desenhar e de receber toque ali (clip-path com um vão) e ganha folga no fim para o conteúdo subir acima dela; o aviso
// passa a receber o toque, para nada vazar a um controle escondido. A reserva sai quando o aviso some, muda de texto ou o contêiner muda
// de lugar ou tamanho. Roda antes da medida do g2avisoH, que reserva o pé (--aviso-h).
function g2toastSolta(t){ const r=t.__res; if(!r) return; t.__res=null; try{ r.S.style.clipPath=r.cp0; r.S.style.paddingBottom=r.pb0; }catch(e){} t.style.pointerEvents='none'; }
// botões, links e campos VISÍVEIS (o que está no topo no centro deles; o aviso não pode estar recebendo toque) fora do aviso
function g2ctl(t,H,W){ const ctl=[]; document.querySelectorAll('button,a[href],[role=button],input,select,textarea').forEach(e=>{ if(t.contains(e)) return; const q=e.getBoundingClientRect();
    if(!(q.width>0&&q.height>0)||q.bottom<0||q.top>H||q.right<0||q.left>W||(q.width>=W*.9&&q.height>=H*.5)) return;   /* o fundo de tela inteira atrás do painel não conta */
    const x=Math.min(Math.max(q.left+q.width/2,0),W-1), y=Math.min(Math.max(q.top+q.height/2,0),H-1);
    const h=document.elementFromPoint(x,y); if(h&&(h===e||e.contains(h))) ctl.push({e,q}); }); return ctl; }
function g2rolaPai(e){ for(let a=e;a&&a!==document.body&&a!==document.documentElement;a=a.parentElement){ const cs=getComputedStyle(a);
    if(/(auto|scroll)/.test(cs.overflowY)&&a.scrollHeight>a.clientHeight+1) return a; if(cs.position==='fixed') return null; } return null; }
function g2toastLugar(){ try{ const t=document.querySelector('.g2toast'); if(!t) return;
  if(!t.getClientRects().length){ g2toastSolta(t); t.__tx=null; return; }
  const tx=t.textContent, rs=t.__res, H=window.innerHeight||document.documentElement.clientHeight, W=window.innerWidth||document.documentElement.clientWidth;
  // a reserva fica enquanto nada visível novo aparece debaixo do aviso (ex.: um painel aberto por cima dela) e o contêiner não muda
  if(rs&&tx===t.__tx&&rs.S.isConnected){ const q=rs.S.getBoundingClientRect(); if(q.top===rs.q.top&&q.bottom===rs.q.bottom&&q.left===rs.q.left&&q.right===rs.q.right){
      t.style.pointerEvents='none'; const a=t.getBoundingClientRect(), u=g2ctl(t,H,W).filter(c=>c.q.left<a.right&&c.q.right>a.left&&c.q.top<a.bottom&&c.q.bottom>a.top); t.style.pointerEvents='auto';
      if(!u.length) return; } }
  g2toastSolta(t); t.__tx=tx;
  if(t.__b0===undefined){ t.__b0=t.style.bottom; t.__l0=t.style.left; t.__w0=t.style.maxWidth; }
  t.style.top=''; t.style.bottom=t.__b0; t.style.left=t.__l0; t.style.maxWidth=t.__w0;
  const m=document.querySelector('main'); const mq=m&&m.getBoundingClientRect();
  if(mq&&mq.width>200){ const l=Math.max(mq.left,0), r=Math.min(mq.right,W); t.style.left=((l+r)/2)+'px'; t.style.maxWidth=Math.min(560,r-l-24)+'px'; }
  const ctl=g2ctl(t,H,W);
  const topo=Math.max(mq&&mq.width>200?mq.top:0,8);   // nunca acima da área de conteúdo
  // salvaguarda: se a âncora ficar acima da área de conteúdo (ex.: área de ações presa mais alta que a tela), volta ao pé da janela
  if(t.getBoundingClientRect().top<topo) t.style.bottom='22px';
  const r0=t.getBoundingClientRect(), h=r0.height, b0=H-r0.bottom;
  // folga de 6 px entre o aviso e o controle (15/10/2026): encostado, meio pixel de diferença (alvo de 44 px, altura fracionária) ou o quadro
  // da rolagem bastavam para o aviso ficar por cima da borda do botão (UX-BEN35-AVISO-01, roteiro 390 do Beneficiamento)
  const sob=(b)=>{ const top=H-b-h-6, bot=H-b+6; return ctl.filter(c=>c.q.left<r0.right&&c.q.right>r0.left&&c.q.top<bot&&c.q.bottom>top); };
  if(!sob(b0).length) return;
  for(let b=b0+1;H-b-h>=topo;b++){ if(!sob(b).length){ t.style.bottom=b+'px'; return; } }
  // sem faixa livre: a mais baixa em que tudo o que fica debaixo do aviso é de um mesmo contêiner que rola
  for(let b=b0;H-b-h>=topo;b++){ const u=sob(b); const S=g2rolaPai(u[0].e); if(!S||u.some(c=>!S.contains(c.e))) continue;
    const q=S.getBoundingClientRect(), y1=Math.max(Math.floor(H-b-h-4-q.top),0), y2=Math.min(Math.ceil(H-b+4-q.top),q.height); if(y2<=y1) continue;
    const pb0=S.style.paddingBottom, cp0=S.style.clipPath, pb=parseFloat(getComputedStyle(S).paddingBottom)||0;
    S.style.clipPath="path(evenodd,'M0 0H"+q.width+"V"+q.height+"H0Z M0 "+y1+"H"+q.width+"V"+y2+"H0Z')"; S.style.paddingBottom=(pb+q.height-y1)+'px';
    if(b!==b0) t.style.bottom=b+'px'; t.style.pointerEvents='auto'; t.__res={S,pb0,cp0,q:S.getBoundingClientRect(),y1,y2}; return; } }catch(e){} }
// foco (Tab ou programático) num elemento debaixo da faixa reservada: o contêiner rola até ele ficar inteiro acima dela (revisão Codex
// 6160750498: o foco ia para a linha recortada e ficava invisível). Roda na hora e de novo no quadro seguinte, depois da rolagem do navegador
function g2toastFoco(el){ try{ const t=document.querySelector('.g2toast'), rs=t&&t.__res; if(!rs||!el||!rs.S.contains(el)||el===rs.S) return;
  const q=rs.S.getBoundingClientRect(), r=el.getBoundingClientRect(), topo=q.top+rs.y1; if(r.bottom>topo&&r.top<q.bottom) rs.S.scrollTop+=r.bottom-topo+8; }catch(e){} }
if(typeof document!=='undefined'&&!window.__g2toastFoco){ window.__g2toastFoco=1;
  document.addEventListener('focusin',(e)=>{ const el=e.target; g2toastFoco(el); requestAnimationFrame(()=>{ if(document.activeElement===el) g2toastFoco(el); }); },true); }
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
    // refaz também quando o número de colunas muda (AG-07: 6 por produto, 8 por uso na cultura): --g2cols tem uma trilha por coluna
    if(r.hasAttribute('data-c0')&&(r.__c0w!==cw||r.__c0n!==hs.length)){ r.removeAttribute('data-c0'); r.style.removeProperty('--g2cols'); }
    const cap=Math.max(96,Math.round(cw*.45));
    if(!r.hasAttribute('data-c0')&&r.scrollWidth-cw>2&&h.getBoundingClientRect().width>cap+1){
      const c0='minmax(min-content, '+cap+'px)'; r.setAttribute('data-c0',''); r.style.setProperty('--g2cols',hs.map(x=>x===h?c0:'auto').join(' '));
      const vis=Math.max(96,Math.floor(cw-h.getBoundingClientRect().width-4)); r.style.setProperty('--g2cols',hs.map(x=>x===h?c0:'fit-content('+vis+'px)').join(' ')); }
    r.__c0w=cw; r.__c0n=hs.length; r.style.setProperty('--g2c0w',Math.round(h.getBoundingClientRect().width)+'px'); r.style.setProperty('--g2hh',Math.round(hr.getBoundingClientRect().height)+'px'); };
  const faixa=()=>{ const col=document.querySelector('.ml-tog+div'); if(!col) return; const nv=col.querySelector(':scope>.etp'); col.style.setProperty('--etp-h',(nv&&nv.getClientRects().length?nv.offsetHeight:0)+'px'); };
  const acoes=()=>{ const a=[...document.querySelectorAll('main .acoes')].find(vis); const h=(a&&getComputedStyle(a).position==='sticky')?Math.round(a.getBoundingClientRect().height):0; document.documentElement.style.setProperty('--acoes-h',h+'px'); g2avisoH(); };
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
    if(d&&d!==aberto){ aberto=d; const ae=document.activeElement, o=(ae&&ae!==document.body&&!(ae.closest&&ae.closest('aside[role=dialog]')))?ae:fora; d.__volta=o; d.__marca=marca(o); if(d.getAttribute('aria-modal')!=='true') d.setAttribute('aria-modal','true');
      if(d.dataset&&d.dataset.foco==='1') setTimeout(()=>{ if(aberto!==d||d.contains(document.activeElement)) return; const f=foc(d)[0]; if(f) try{ f.focus({preventScroll:true}); }catch(e){} },0); }   /* opt-in (Configurações): o foco entra no painel ao abrir; Esc fecha sem um Tab antes */
    else if(!d&&aberto){ const v=aberto.__volta, m=aberto.__marca; aberto=null;
      devolve(v,m); setTimeout(()=>devolve(v,m),0); setTimeout(()=>devolve(v,m),80); } };   // de novo depois do redesenho da tela (só age se o foco caiu no BODY)
  try{ new MutationObserver(olha).observe(document.documentElement,{childList:true,subtree:true}); }catch(e){} })();
// Indicador de progresso do processo guiado: só informa (atual, concluída, pendente, impedida) com a palavra do estado para o leitor
// de tela; não navega (sem handler, sem foco, sem hover de ação). O argumento go fica por compatibilidade e não é usado.
// Progresso do processo em cartões (15/10/2026): número (✓ concluída, ! impedida), nome, situação com ponto de cor e contagem opcional
// (info[i] = {cnt, sub}: a tela informa o número da etapa e a frase curta); a seta › entre os cartões vem do CSS (ui37._etp_css).
// Clicar no cartão leva à etapa (15/10/2026, proprietário: "permita clicar diretamente na etapa do fluxo de processos desejado e ir para a tela"):
// go(i) da tela valida a etapa; sem go, a etapa travada mostra o motivo e as outras vão por g2etapa. A etapa atual não faz nada.
function g2steps(self,v,pre,n,cur,whys,go,info){ const ir=go||((i)=>{ if(whys&&whys[i]){ self.setState({g2toast:whys[i]}); return; } g2etapa(self,{step:i}); });
 for(let i=1;i<=n;i++){ const on=(i===cur); const w=(i<=cur&&whys&&whys[i])||''; const feita=(!on&&i<cur&&!w); const x=(info&&info[i])||{};   // etapa futura neutra (ETP-01)
  const trava=!on&&!!(whys&&whys[i]); v[pre+i+'_go']=()=>{ try{ document.querySelectorAll('.etp-chk:checked').forEach(c=>{ c.checked=false; }); }catch(e){} if(i!==cur) ir(i); };   /* na faixa estreita, fecha a folha */ v[pre+i+'_dis']=trava?'true':'false'; v[pre+i+'_tt']=trava?whys[i]:'';
  v[pre+i+'_st']='position:relative;display:flex;align-items:stretch;padding:0;border-radius:12px;min-width:0;flex:1 1 0;box-sizing:border-box;color:#15201A;'
    +(on?'background:#E4F3E9;border:1.5px solid #1E7A4C;box-shadow:0 2px 8px -2px rgba(30,122,76,.25);':(w?'background:#FFFFFF;border:1px solid #F3C4BE;':'background:#FFFFFF;border:1px solid #E4E9E5;'));
  v[pre+i+'_bst']='width:26px;height:26px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;flex-shrink:0;'
    +(on?'background:#1E7A4C;color:#fff;':(w?'background:#FDE8E6;color:#B42318;':(feita?'background:#E3F2E8;color:#1E6B47;':'background:#EEF1EE;color:#4B5A51;')));
  v[pre+i+'_tst']='font-size:13px;line-height:1.2;font-weight:'+(on?'800':'700')+';color:'+(on||feita||w?'#15201A':'#4B5A51')+';display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;overflow-wrap:anywhere;';   // nome em até 2 linhas (cartão estreito)
  const cor=w?'#B42318':(on?'#1E7A4C':(feita?'#3FBF2A':'#C4CCC6'));
  v[pre+i+'_sst']='display:flex;align-items:center;gap:5px;font-size:11.5px;line-height:1.2;font-weight:600;color:'+(w?'#B42318':'#5F6B64')+';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
  v[pre+i+'_dot']='width:7px;height:7px;border-radius:999px;flex-shrink:0;background:'+cor+';';
  v[pre+i+'_sub']=w||x.sub||(on?'em andamento':(feita?'concluída':'a fazer'));
  v[pre+i+'_hasCnt']=x.cnt!==undefined&&x.cnt!==null&&x.cnt!==''; v[pre+i+'_cnt']=v[pre+i+'_hasCnt']?String(x.cnt):'';
  v[pre+i+'_cst']='margin-left:auto;padding-left:8px;font-size:20px;font-weight:800;letter-spacing:-.02em;color:'+(on?'#1E6B47':'#15201A')+';font-variant-numeric:tabular-nums;';
  v[pre+i+'_num']=w?'!':(feita?'✓':String(i)); v[pre+i+'_sr']=on?'etapa atual':(w?'impedida':(feita?'concluída':(trava?'travada: '+whys[i]:'pendente')));   // o motivo da trava também para o leitor de tela
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
  { const ae0=document.activeElement; if(ae0&&ae0.closest&&ae0.closest('[role=dialog]')) return; }   // painel aberto antes deste passo atrasado: o foco fica nele (sem isto o Esc do painel não chegava; diagnóstico 13/10)
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
  /* troca de contexto do processo (14/10, proprietário: "o trocar safra tem que ficar embaixo nos botões de fluxo de processo"): à esquerda, junto do retorno */
  const troca=c.troca||null; v[pre+'_hasTroca']=!!troca; v[pre+'_trocaT']=troca?troca.t:''; v[pre+'_troca']=troca?troca.fn:nada;
  v[pre+'_hasSec']=!!sec; v[pre+'_secT']=sec?sec.t:''; v[pre+'_secFn']=sec?sec.fn:nada; v[pre+'_secA']=(sec&&sec.a)||'avancar';
  const lk=!!(prim&&prim.h); v[pre+'_hasPrim']=!!prim&&!lk; v[pre+'_hasLink']=lk; v[pre+'_primT']=prim?prim.t:''; v[pre+'_primFn']=(prim&&prim.fn)||nada; v[pre+'_href']=lk?prim.h:'#';
  v[pre+'_primA']=(prim&&prim.a)||'avancar'; v[pre+'_desc']=c.nota?(pre+'-nota'):'';
  /* barra limpa (15/10/2026): nota visível só na decisão do momento (c.decide); senão, dica do principal; atalhos no "⋯ Mais ações" */
  const dec=!!c.decide; v[pre+'_hasNotaVis']=dec&&!!(c.nota||lnks.length); v[pre+'_hasNotaSr']=!dec&&!!c.nota; v[pre+'_dica']=(!dec&&c.nota)?c.nota:'';
  v[pre+'_hasMais']=!dec&&(lnks.length>0||!!c.ctx);
  v[pre+'_has']=!!(c.nota||lnks.length||volta||c.troca||sec||prim); }
// ===== DS-MAIS-20261015 · "⋯ Mais ações" (engine.mais): comportamento único do menu =====
// botão .g2mais (aria-haspopup=menu, aria-expanded) seguido do menu .g2mais-menu (role=menu, itens role=menuitem). O estado aberto é o
// aria-expanded do botão (o CSS esconde o menu fechado). Um menu aberto por vez.
function g2maisMenu(b){ const m=b&&b.nextElementSibling; return m&&m.classList&&m.classList.contains('g2mais-menu')?m:null; }
function g2maisItens(m){ return m?[...m.querySelectorAll('[role=menuitem]')].filter(x=>x.getClientRects().length&&!x.disabled&&x.getAttribute('aria-disabled')!=='true'):[]; }
function g2maisFecha(b,foco){ if(!b) return; if(b.getAttribute('aria-expanded')==='true') b.setAttribute('aria-expanded','false'); if(foco&&b.isConnected) b.focus(); }
function g2maisAbre(b,ult){ document.querySelectorAll('.g2mais[aria-expanded=true]').forEach(x=>{ if(x!==b) g2maisFecha(x); });
  const m=g2maisMenu(b); if(!m) return; m.removeAttribute('data-cima'); m.removeAttribute('data-esq'); b.setAttribute('aria-expanded','true');
  const r=b.getBoundingClientRect(), h=m.offsetHeight, w=m.offsetWidth;
  if(r.bottom+4+h>innerHeight-8&&r.top-4-h>=8) m.setAttribute('data-cima','');   // falta espaço embaixo: sobe
  if(r.right-w<8) m.setAttribute('data-esq','');                                  // falta espaço à esquerda: abre para a direita
  const its=g2maisItens(m); if(its.length) (ult?its[its.length-1]:its[0]).focus(); }
try{ if(!window.__g2maisC){ window.__g2maisC=1;
  document.addEventListener('click',e=>{ const t=e.target&&e.target.closest?e.target:null; const b=t&&t.closest('button.g2mais');
    if(b){ if(b.getAttribute('aria-expanded')==='true') g2maisFecha(b); else g2maisAbre(b); return; }
    const it=t&&t.closest('.g2mais-menu [role=menuitem]');
    document.querySelectorAll('.g2mais[aria-expanded=true]').forEach(x=>{ const m=g2maisMenu(x); if(!m) return;
      if(it&&m.contains(it)){ g2maisFecha(x); setTimeout(()=>{ const a=document.activeElement; if((!a||a===document.body||m.contains(a))&&x.isConnected) x.focus(); },0); }
      else if(!m.contains(t)) g2maisFecha(x); }); },true);
  document.addEventListener('keydown',e=>{ const a=document.activeElement; const w=a&&a.closest&&a.closest('.g2mais-w'); if(!w) return;
    const b=w.querySelector('button.g2mais'); const m=g2maisMenu(b); const aberto=!!b&&b.getAttribute('aria-expanded')==='true';
    if(a===b&&!aberto&&(e.key==='ArrowDown'||e.key==='ArrowUp')){ e.preventDefault(); g2maisAbre(b,e.key==='ArrowUp'); return; }
    if(!aberto) return;
    if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); g2maisFecha(b,true); return; }
    if(e.key==='Tab'){ g2maisFecha(b); return; }
    const its=g2maisItens(m); if(!its.length) return; const i=its.indexOf(a);
    if(e.key==='ArrowDown'||e.key==='ArrowUp'){ e.preventDefault(); const n=its.length; its[i<0?(e.key==='ArrowDown'?0:n-1):(i+(e.key==='ArrowDown'?1:n-1))%n].focus(); }
    else if(e.key==='Home'||e.key==='End'){ e.preventDefault(); its[e.key==='Home'?0:its.length-1].focus(); } },true);
  // a barra de ações (details.acoes-mais): o ⋯ diz se está aberto (aria-expanded), como o do componente
  document.addEventListener('toggle',e=>{ const d=e.target; if(d&&d.matches&&d.matches('details.acoes-mais')){ const sm=d.querySelector('summary'); if(sm) sm.setAttribute('aria-expanded',d.open?'true':'false'); } },true);
} }catch(e){}
// "⋯ Mais ações" da barra (details.acoes-mais): fecha com Esc (o foco volta ao ⋯), ao clicar fora e depois de escolher um item
try{ if(!window.__g2mais){ window.__g2mais=1;
  document.addEventListener('keydown',e=>{ if(e.key!=='Escape') return; const a=document.activeElement; const d=a&&a.closest&&a.closest('details.acoes-mais[open]'); if(!d) return;
    e.preventDefault(); e.stopPropagation(); d.open=false; const sm=d.querySelector('summary'); if(sm) sm.focus(); },true);
  document.addEventListener('click',e=>{ document.querySelectorAll('details.acoes-mais[open]').forEach(d=>{ if(!d.contains(e.target)||(e.target.closest&&e.target.closest('[role=menuitem]'))) d.open=false; }); },true); } }catch(e){}
// ===== DS-RETORNO-20261009 · retorno visual de mudança (g2flash) =====
// Proprietário (09/10/2026): "quando muda de tela e avança no processo não está dando aquele feedback ao usuário em tempo real como se fosse um
// flash de atualização e mudança de contexto". Uma só função de realce (g2flash), chamada só pelos pontos centrais do motor (engine.ENGINE_JS2):
// carga da tela (componentDidMount → g2montou), troca de etapa ou seção (faixa de progresso lida depois de cada desenho → g2mudou) e mudança de
// estado com aviso (g2toast novo: gravar, aprovar, liberar, mover cartão → g2mudou). Realce = camada verde que esmaece em 520 ms no bloco que
// mudou; com "menos movimento" fica um realce estático curto (CSS). Não atrasa a ação nem esconde o resultado: o desenho novo já está na tela.
// Anúncio: região viva única (aria-live polite) com o novo estado. Navegação entre telas: barra fina no topo (g2carga) do clique até a tela nova.
const G2_REALCE_MS=520;
function g2menos(){ try{ return window.matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){ return false; } }
function g2txt(el){ return String((el&&el.textContent)||'').replace(/\s+/g,' ').trim(); }
function g2vis(el){ return !!el&&el.isConnected&&el.getClientRects().length>0; }
// região viva única: repetir a mesma frase anuncia de novo (esvazia e preenche)
function g2vivo(msg){ if(typeof document==='undefined'||!document.body) return null; let r=document.getElementById('g2-vivo');
  if(!r){ r=document.createElement('div'); r.id='g2-vivo'; r.setAttribute('aria-live','polite'); r.setAttribute('aria-atomic','true'); r.className='g2sr';
    r.style.cssText='position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap'; document.body.appendChild(r); }
  // duas frases no mesmo instante (ex.: o resultado e a recusa do 2º clique) saem juntas, sem uma apagar a outra
  const t=(r.__pend?r.__pend+' ':'')+String(msg||''); clearTimeout(r.__t); r.textContent=''; r.__pend=t;
  r.__t=setTimeout(()=>{ r.textContent=t; r.__pend=''; },60); r.dataset.ultimo=t; return r; }
// realce passageiro de um elemento (ou seletor) + anúncio opcional; window.__g2realces guarda os últimos 20 (o teste de navegador lê)
function g2flash(alvo,msg){ let el=null; try{ if(typeof document==='undefined') return null;
    el=(typeof alvo==='string')?document.querySelector(alvo):alvo; if(!g2vis(el)) el=null;
    if(el){ el.classList.remove('g2-realce'); void el.offsetWidth; el.classList.add('g2-realce'); clearTimeout(el.__g2r);
      el.__g2r=setTimeout(()=>el.classList.remove('g2-realce'),G2_REALCE_MS+80);
      const L=(window.__g2realces=window.__g2realces||[]); L.push({t:Date.now(),tag:el.tagName,txt:g2txt(el).slice(0,80),msg:String(msg||'')}); if(L.length>20) L.shift(); }
    if(msg) g2vivo(msg); }catch(e){} return el; }
// barra fina de carga no topo: 'ini' (clique num link de outra tela), 'chega' + 'fim' (tela nova montada)
function g2carga(fase){ if(typeof document==='undefined'||!document.body) return; let b=document.getElementById('g2-carga');
  if(!b){ b=document.createElement('div'); b.id='g2-carga'; b.setAttribute('aria-hidden','true'); document.body.appendChild(b); }
  clearTimeout(b.__t); b.className=''; void b.offsetWidth; b.className=fase||''; if(fase==='fim') b.__t=setTimeout(()=>{ b.className=''; },700); }
// etapa ou seção atual (faixa de progresso SAF/CMP/PA/PM ou seções do Estoque): '' se a tela não tem faixa
function g2passo(){ if(typeof document==='undefined') return '';
  const e=document.querySelector('.etp-ind li[aria-current="step"],.etp-sec .etp-itens>[aria-current="true"]'); if(!e) return '';
  const nm=e.querySelector('.etp-nome')||e.querySelector(':scope>span:not([aria-hidden="true"])>span')||e.querySelector('span');   /* cartão-botão (15/10): o nome tem classe própria */ const c=nm?nm.cloneNode(true):null;
  if(c) c.querySelectorAll('.etp-sr').forEach(x=>x.remove()); const nome=c?g2txt(c):g2txt(e);
  if(e.tagName==='LI'){ const ls=[...e.parentElement.children].filter(x=>x.tagName==='LI'); return 'Etapa '+(ls.indexOf(e)+1)+' de '+ls.length+': '+nome; }
  return 'Seção: '+nome; }
// bloco do contexto atual: o cartão do 1º título visível do conteúdo (o mesmo que g2etapa foca)
function g2blocoAtual(){ const m=document.querySelector('main'); if(!m) return null; const h=[...m.querySelectorAll('h2,h3')].find(g2vis);
  if(h) return h.closest('section')||h.parentElement; return [...m.children].find(g2vis)||m; }
// contexto do conteúdo: o 1º título visível do main (o mesmo bloco que g2blocoAtual realça); '' sem título
function g2contexto(){ if(typeof document==='undefined') return ''; const m=document.querySelector('main'); if(!m) return '';
  const h=[...m.querySelectorAll('h2,h3')].find(x=>g2vis(x)&&!x.closest('aside,[role=dialog]')); return h?g2txt(h).slice(0,80):''; }   // painel e diálogo não mudam o contexto da tela
// filhos com caixa (sc-if e sc-for são display:contents)
function g2blocos(p){ const out=[]; for(const c of p.children){ if(/^SC-/.test(c.tagName)) out.push(...g2blocos(c)); else out.push(c); } return out; }
// foto do que está na tela, por chave estável e nível (1 = linha/cartão, 2 = região rotulada/estado do cabeçalho, 3 = bloco do conteúdo)
function g2foto(){ const f={}; if(typeof document==='undefined') return f;
  const add=(k,el,nv,s)=>{ if(el&&!f[k]) f[k]={el,nv,s:(s===undefined?g2txt(el):s)}; };
  document.querySelectorAll('[role=table][data-g2g] [role=row][data-rid]').forEach(r=>add('r:'+r.closest('[role=table]').getAttribute('data-g2g')+':'+r.getAttribute('data-rid'),r,1));
  document.querySelectorAll('[role=list]').forEach(l=>g2blocos(l).forEach((col,ci)=>col.querySelectorAll('[role=button],[role=listitem]').forEach(k=>{
    const b=k.querySelector('b'); add('k:'+(b?g2txt(b):(k.getAttribute('aria-label')||g2txt(k).slice(0,40))),k,1,ci+'|'+g2txt(k)); })));
  document.querySelectorAll('[data-g2k]').forEach(e=>add('x:'+e.getAttribute('data-g2k'),e,1));
  const h=document.querySelector('header h1'); const he=g2estadoCab(h); if(he) add('h:estado',he,2);
  document.querySelectorAll('[role=region][aria-label],section[aria-label]').forEach(e=>add('g:'+e.getAttribute('aria-label'),e,2));
  document.querySelectorAll('aside[role=dialog] h2').forEach(t=>add('d:'+g2txt(t).slice(0,60),t.parentElement,2));
  document.querySelectorAll('main section').forEach((s,i)=>{ const t=s.querySelector('h2,h3'); add('s:'+(t?g2txt(t).slice(0,60):i),s,3); });
  return f; }
// estado do cabeçalho: o irmão do título, pulando o ⓘ "Regras desta tela" (TEXTO-2, 14/10/2026: com o ⓘ logo depois do h1, o anúncio dizia
// "Tela: … · i" e o realce do estado olhava o ⓘ em vez do selo)
function g2estadoCab(h){ let e=h&&h.nextElementSibling; while(e&&e.classList&&e.classList.contains('g2-info')) e=e.nextElementSibling; return e||null; }
// tela montada: barra de carga termina, título realçado e anunciado; vindo de um link do protótipo, o foco vai ao título da tela nova
function g2montou(self){ if(typeof document==='undefined') return; g2buscaUnica(self);   /* um campo de busca por tela (13/10) */
  setTimeout(()=>{ try{
    const h=document.querySelector('header h1')||document.querySelector('h1');
    let veio=false; try{ const t=Number(sessionStorage.getItem('g2nav')||0); sessionStorage.removeItem('g2nav'); veio=t>0&&Date.now()-t<15000; }catch(e){}
    g2carga('chega'); setTimeout(()=>g2carga('fim'),g2menos()?300:40);
    const st=g2estadoCab(h); const stT=st?g2txt(st):''; const tit=h?g2txt(h):document.title;
    const ae=document.activeElement; const foca=veio&&h&&!location.hash&&(!ae||ae===document.body);
    /* revisão DS (achado 10): com o foco no título o leitor de tela já lê o título; o anúncio leva só o estado (sem ler o título duas vezes) */
    g2flash(h,foca?stT:('Tela: '+tit+(stT?' · '+stT:'')));
    if(foca){ if(!h.hasAttribute('tabindex')) h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); }
    self.__g2foto=g2foto(); self.__g2passo=g2passo(); self.__g2ctx=g2contexto(); self.__g2toastVisto=(self.state&&self.state.g2toast)||''; }catch(e){} },60); }
// depois de cada desenho: troca de etapa/seção realça o bloco do novo contexto; aviso novo (g2toast) realça o que mudou e anuncia
function g2mudou(self){ if(typeof document==='undefined') return; g2buscaUnica(self); if(!self.__g2foto) return;   // antes da 1ª foto (montagem) não compara
  const f=g2foto(), ant=self.__g2foto, agora=Date.now(); self.__g2foto=f;
  const mud=self.__g2mud=(self.__g2mud||[]).filter(x=>agora-x.t<1200);   // mudanças recentes (o aviso pode vir num desenho seguinte ao do dado)
  for(const k in f){ if(ant[k]&&ant[k].s!==f[k].s) mud.push({k,t:agora}); }
  const t=(self.state&&self.state.g2toast)||''; const tNovo=!!t&&t!==self.__g2toastVisto; if(!t) self.__g2toastVisto='';
  const p=g2passo();
  if(p&&self.__g2passo&&p!==self.__g2passo){ self.__g2passo=p; if(tNovo) self.__g2toastVisto=t; self.__g2mud=[]; const b=g2blocoAtual(); g2flash(b,p+(tNovo?'. '+t:''));
    /* revisão DS (achado 3): o botão que trocou a etapa sumiu (foco no BODY ou fora da página): o foco vai ao título do novo contexto (rola só se ele estiver fora da vista) */
    const ae=document.activeElement; if(!ae||ae===document.body||!ae.isConnected){ const hh=b&&b.querySelector('h2,h3'); if(hh){ if(!hh.hasAttribute('tabindex')) hh.setAttribute('tabindex','-1'); hh.focus({preventScroll:false}); } }
    /* DS-RETORNO-2-DUP-01 (Codex 6174131920): a troca de etapa já anunciou; o título novo que chega no desenho seguinte não é outra mudança */
    self.__g2ctx=g2contexto(); self.__g2ctxCalmo=agora+800;
    return; }
  if(p) self.__g2passo=p;
  /* 14/10 (proprietário: "não está dando flash de feedback quando muda para a tela de destino"): abrir um detalhe ou trocar a visão na mesma
     tela (o 1º título do conteúdo muda) realça o bloco novo e anuncia, como a troca de etapa; o foco vai ao título se o botão sumiu */
  const cx=g2contexto();
  if(cx&&self.__g2ctx&&cx!==self.__g2ctx&&agora<(self.__g2ctxCalmo||0)) self.__g2ctx=cx;   // ainda é a mesma troca de etapa: um anúncio só
  if(cx&&self.__g2ctx&&cx!==self.__g2ctx){ self.__g2ctx=cx; if(tNovo) self.__g2toastVisto=t; self.__g2mud=[]; const b=g2blocoAtual(); g2flash(b,tNovo?t:cx);   /* o aviso da ação, quando há, é o que se anuncia */
    const ae=document.activeElement; if(!ae||ae===document.body||!ae.isConnected){ const hh=b&&b.querySelector('h2,h3'); if(hh){ if(!hh.hasAttribute('tabindex')) hh.setAttribute('tabindex','-1'); hh.focus({preventScroll:true}); } }
    return; }
  if(cx) self.__g2ctx=cx;
  if(!tNovo) return; self.__g2toastVisto=t;
  const ks=[...new Set(mud.map(x=>x.k).concat(Object.keys(f).filter(k=>!ant[k]&&f[k].nv===1&&f[k].el.classList.contains('g2flash'))))]; self.__g2mud=[];
  const nivel=(n)=>ks.filter(k=>f[k]&&f[k].nv===n).map(k=>f[k].el).filter(g2vis);
  let alvos=nivel(1).slice(0,3).concat(nivel(2).slice(0,2)); if(!alvos.length) alvos=nivel(3).slice(0,1);
  alvos.forEach(e=>g2flash(e)); g2vivo(t); }
(function g2retGlob(){ if(typeof document==='undefined'||window.__g2ret) return; window.__g2ret=1;
  // revisão DS (achado 1): a tela que volta da memória do navegador (voltar/avançar, bfcache) não monta de novo: a barra ligada no clique termina aqui
  window.addEventListener('pageshow',(e)=>{ if(!e.persisted) return; g2carga('fim'); try{ sessionStorage.removeItem('g2nav'); }catch(er){} });
  // 14/10 (proprietário: "faça o mesmo para todas telas e botoes"): o controle acionado pulsa um anel verde (320 ms) — o usuário vê que o
  // clique pegou mesmo quando a resposta vem noutro lugar da tela ou noutra tela; indisponível não pulsa (a recusa tem o próprio retorno)
  document.addEventListener('click',(e)=>{ const el=e.target&&e.target.closest&&e.target.closest('button,a[href],[role=button],[role=tab],[role=menuitem],[role=option],summary,.g2card,a.mod-cartao');
    if(!el||el.disabled||el.getAttribute('aria-disabled')==='true'||el.closest('.g2dica')) return;
    el.classList.remove('g2-acionado'); void el.offsetWidth; el.classList.add('g2-acionado'); clearTimeout(el.__g2ac); el.__g2ac=setTimeout(()=>el.classList.remove('g2-acionado'),360); },true);
  // clique num link para outra tela do protótipo: a barra começa já (a navegação segue sem espera); a tela nova termina a barra e foca o título
  document.addEventListener('click',(e)=>{ if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey) return;
    const a=e.target&&e.target.closest&&e.target.closest('a[href]'); if(!a||(a.target&&a.target!=='_self')||a.hasAttribute('download')) return;
    let u=null; try{ u=new URL(a.getAttribute('href'),location.href); }catch(er){ return; }
    if(u.origin!==location.origin||u.pathname===location.pathname) return;   // âncora na mesma tela não carrega outra
    g2carga('ini'); try{ sessionStorage.setItem('g2nav',String(Date.now())); }catch(er){} });
})();
// ===== DS-DICA-20261009 · dica acessível (g2dica) =====
// Proprietário (09/10/2026): "coloque tooltip onde for necessária para melhorar feedback ao usuário". Componente único: abre no hover (ponteiro
// fino, 300 ms) e no foco de teclado; no toque, com toque longo (500 ms) ou no ícone ⓘ (.g2dica-i); fecha com Esc, ao sair e ao perder o foco.
// role=tooltip e o gatilho passa a ser descrito por ela (aria-describedby) enquanto aberta. Texto: data-dica (explícito; vazio = sem dica),
// data-dica-de (selo: o texto do selo busca o significado e o próximo passo em G2_DICAS) ou
// o title que acrescenta algo ao rótulo visível; ícone sem texto mostra o nome do comando. Nunca repete o rótulo visível. Botão indisponível
// com motivo usa aria-disabled="true" (continua focável): o clique é recusado aqui e a dica diz o porquê; o motivo também fica em texto junto do
// botão (engine.acao_motivo, PRD DS-06 e 74.5.0, VIS-04), realçado na recusa: a dica complementa, não substitui.
const G2_DICA_ID='g2-dica';
const G2D={el:null,desc:null,modo:'',sai:0,entra:0,lp:0,lpXY:null,toque:0,tt:null};
function g2visTxt(el){ return String((el&&el.innerText)||'').replace(/\s+/g,' ').trim(); }
function g2contem(vis,t){ const n=(s)=>g2norm(s).replace(/[^a-z0-9]+/g,' ').trim(); const b=n(t); return !!b&&n(vis).indexOf(b)>=0; }
// regra do texto (pura, testada em ds_unit.js): explícito > title que acrescenta > nome do ícone sem texto > nada
function g2dicaRegra(o){ if(o.dica!==null&&o.dica!==undefined) return String(o.dica).trim();
  if(o.de!==null&&o.de!==undefined) return g2dicaDe(o.de);   // data-dica-de="texto do selo": dica de estado do dicionário (G2_DICAS)
  const t=String(o.title||'').trim(), vis=String(o.vis||'').trim(), al=String(o.aria||'').trim();
  if(t&&!g2contem(vis,t)) return t;
  if(al&&o.comando&&!/[\p{L}\p{N}]/u.test(vis)) return al;   // sem letra nem número visível (×, ‹, ▾, só ícone)
  return ''; }
function g2dicaTexto(el){ if(!el||el.nodeType!==1||!el.getAttribute) return '';
  const d=el.getAttribute('data-dica'), de=el.getAttribute('data-dica-de'), t=el.getAttribute('title')||el.__g2tt||'', al=el.getAttribute('aria-label')||'';
  if(d===null&&de===null&&!t&&!al) return '';   // sem fonte de dica: nem mede o texto visível (innerText custa layout)
  return g2dicaRegra({dica:d,de,title:t,vis:(d===null&&de===null)?g2visTxt(el):'',aria:al,
    comando:el.matches('button,a[href],[role=button]')&&!(typeof SVGElement!=='undefined'&&el instanceof SVGElement)}); }   // polígono do mapa não vira dica
function g2dicaAlvo(n){ for(let e=n,i=0;e&&e.nodeType===1&&i<6;e=e.parentElement,i++){
    if(e.id===G2_DICA_ID) return null; if(e.closest&&e.closest('svg')&&e.tagName!=='svg'&&!(e.matches&&e.matches('svg [role=button]'))) continue;
    const t=g2dicaTexto(e); if(t) return {el:e,t};
    if(e.matches&&e.matches('main,header,nav,aside,section,[role=table],[role=row],[role=list],body')) break; }
  return null; }
// revisão DS (achado 2): o selo de estado não recebe foco; a linha da grade e o cartão do Kanban, sim. Com foco de teclado (:focus-visible) numa
// linha ou cartão sem dica própria, a dica é a do selo mais grave de dentro dele (vermelho > amarelo/laranja > os demais; empate: o primeiro),
// com o nome do selo à frente; ela descreve a linha ou o cartão (aria-describedby). O clique do ponteiro na linha não abre dica.
function g2dicaSelo(n){ if(!n||n.nodeType!==1||!n.matches('[role=row],[role=list] [role=button],[role=list] [role=listitem]')) return null;
  try{ if(!n.matches(':focus-visible')) return null; }catch(e){}
  const ss=[...n.querySelectorAll('[data-dica-de],span[data-dica][style*="border-radius"]')].filter(s=>g2vis(s)&&!s.closest('[role=columnheader]')).map(s=>({s,t:g2dicaTexto(s)})).filter(x=>x.t);
  if(!ss.length) return null;
  const grav=(s)=>{ const c=getComputedStyle(s).color; return c==='rgb(180, 35, 24)'?3:((c==='rgb(138, 90, 0)'||c==='rgb(154, 63, 0)')?2:1); };
  let m=ss[0], g=grav(m.s); ss.slice(1).forEach(x=>{ const k=grav(x.s); if(k>g){ m=x; g=k; } });
  const nome=g2txt(m.s).split(' · ')[0].trim();
  return {el:m.s,t:(nome&&!g2contem(m.t,nome)?nome+': ':'')+m.t}; }
function g2dicaEl(){ let d=document.getElementById(G2_DICA_ID);
  if(!d){ d=document.createElement('div'); d.id=G2_DICA_ID; d.setAttribute('role','tooltip'); d.className='g2dica'; d.hidden=true; document.body.appendChild(d);
    d.addEventListener('pointerenter',()=>clearTimeout(G2D.sai)); d.addEventListener('pointerleave',()=>g2dicaSai(120)); }
  return d; }
function g2dicaPos(){ const d=document.getElementById(G2_DICA_ID), el=G2D.el; if(!d||d.hidden||!el) return;
  if(!g2vis(el)){ g2dicaFecha(); return; }
  const r=(el.closest('.g2ind')||el).getBoundingClientRect(), W=window.innerWidth, H=window.innerHeight;   /* botão com motivo visível (acao_motivo): a dica fica fora do par e não cobre o motivo */ d.style.maxWidth=Math.min(320,W-16)+'px'; d.style.left='0px'; d.style.top='0px';
  const w=d.offsetWidth, h=d.offsetHeight; let x=Math.round(r.left+r.width/2-w/2); x=Math.max(8,Math.min(x,W-w-8));
  let y=Math.round(r.top-h-8), lado='cima'; if(y<8){ y=Math.round(r.bottom+8); lado='baixo'; } if(y+h>H-8) y=Math.max(8,H-h-8);
  d.style.left=x+'px'; d.style.top=y+'px'; d.dataset.lado=lado; }
// desc: quem o leitor de tela descreve (o elemento focado; no hover, o próprio gatilho)
function g2dicaMostra(el,t,modo,desc){ if(typeof document==='undefined') return; const d=g2dicaEl(); clearTimeout(G2D.sai); clearTimeout(G2D.entra);
  if(G2D.el&&(G2D.el!==el||G2D.desc!==(desc||el))) g2dicaLimpa();
  d.textContent=t; d.hidden=false; d.dataset.modo=modo; G2D.el=el; G2D.desc=desc||el; G2D.modo=modo;
  const ds=G2D.desc, nome=String(ds.getAttribute('aria-label')||g2visTxt(ds)).trim();
  if(g2norm(nome)!==g2norm(t)){ const db=String(ds.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean); if(db.indexOf(G2_DICA_ID)<0){ db.push(G2_DICA_ID); ds.setAttribute('aria-describedby',db.join(' ')); } }
  if(modo==='ponteiro'&&el.hasAttribute('title')){ el.__g2tt=el.getAttribute('title'); el.removeAttribute('title'); }   // sem a dica nativa por cima; volta ao fechar
  g2dicaPos(); }
function g2dicaLimpa(){ const el=G2D.el, ds=G2D.desc; if(ds){ const db=String(ds.getAttribute('aria-describedby')||'').split(/\s+/).filter(x=>x&&x!==G2_DICA_ID);
    if(db.length) ds.setAttribute('aria-describedby',db.join(' ')); else ds.removeAttribute('aria-describedby'); }
  if(el&&el.__g2tt!==undefined){ if(!el.hasAttribute('title')) el.setAttribute('title',el.__g2tt); delete el.__g2tt; }
  G2D.el=null; G2D.desc=null; G2D.modo=''; }
function g2dicaFecha(){ clearTimeout(G2D.sai); clearTimeout(G2D.entra); const d=document.getElementById(G2_DICA_ID); if(d) d.hidden=true; g2dicaLimpa(); }
function g2dicaSai(ms){ clearTimeout(G2D.sai); G2D.sai=setTimeout(g2dicaFecha,ms); }
// revisão DS (achado 9): title igual ao rótulo visível (ex.: item do menu aberto) faria o navegador mostrar a dica nativa repetida: ele sai enquanto
// o ponteiro está em cima e volta ao sair (com o menu recolhido o texto fica oculto e o title vira a dica do sistema, como antes)
function g2ttVolta(){ const el=G2D.tt; G2D.tt=null; if(el&&el.__g2ttR!==undefined){ if(!el.hasAttribute('title')) el.setAttribute('title',el.__g2ttR); delete el.__g2ttR; } }
function g2ttTira(n){ if(G2D.tt&&n&&G2D.tt.contains(n)) return; g2ttVolta();
  let el=null; for(let e=n,i=0;e&&e.nodeType===1&&i<6;e=e.parentElement,i++){ if(e.hasAttribute('title')){ el=e; break; } } if(!el) return;
  const t=String(el.getAttribute('title')||'').trim(); if(!t||!g2contem(g2visTxt(el),t)) return;
  el.__g2ttR=el.getAttribute('title'); el.removeAttribute('title'); G2D.tt=el; }
(function g2dicaGlob(){ if(typeof document==='undefined'||window.__g2dica) return; window.__g2dica=1;
  const dentro=(n)=>!!(n&&n.closest&&n.closest('#'+G2_DICA_ID));
  // hover: abre depois de 300 ms parado no gatilho (sem espera se outra dica já está aberta); sair do gatilho e da dica fecha em 120 ms
  document.addEventListener('pointerover',(e)=>{ if(e.pointerType==='touch'||dentro(e.target)) return; g2ttTira(e.target); const a=g2dicaAlvo(e.target);
    if(!a){ clearTimeout(G2D.entra); if(G2D.el&&G2D.modo==='ponteiro') g2dicaSai(120); return; }
    if(a.el===G2D.el){ clearTimeout(G2D.sai); return; }
    clearTimeout(G2D.entra); G2D.entra=setTimeout(()=>g2dicaMostra(a.el,a.t,'ponteiro'),(G2D.el&&G2D.modo==='ponteiro')?0:300); },true);
  document.addEventListener('pointerout',(e)=>{ if(e.pointerType==='touch'||e.relatedTarget) return; g2ttVolta(); clearTimeout(G2D.entra); if(G2D.el&&G2D.modo==='ponteiro') g2dicaSai(120); },true);
  // foco de teclado: abre já; descreve o elemento focado (a dica pode vir do cabeçalho da coluna do botão de ordenar). Linha de grade ou cartão
  // (Kanban) sem dica própria, com foco de teclado: a dica do selo de estado de dentro dela (revisão DS, achado 2: o selo não é focável)
  // Só o foco de teclado (:focus-visible) abre a dica: o clique do mouse e o toque curto também focam o botão, e a dica aberta ficava presa por
  // cima da ação vizinha (revisão VISOES-1, achado B1: cobria "Nova ordem" e os chips de fase e engolia o 1º clique). Hover e toque longo seguem
  document.addEventListener('focusin',(e)=>{ let fv=true; try{ fv=e.target.matches(':focus-visible'); }catch(er){}
    const a=fv?(g2dicaAlvo(e.target)||g2dicaSelo(e.target)):null; if(a) g2dicaMostra(a.el,a.t,'foco',e.target); else if(G2D.el&&G2D.modo!=='ponteiro') g2dicaFecha(); },true);
  document.addEventListener('focusout',(e)=>{ if(G2D.el&&G2D.modo!=='ponteiro'&&G2D.modo!=='recusa'&&(!e.relatedTarget||!G2D.el.contains(e.relatedTarget))) g2dicaFecha(); },true);
  // Esc fecha a dica; a dica explícita (data-dica) consome a tecla, para não fechar também o painel em que o foco está (WCAG 1.4.13)
  document.addEventListener('keydown',(e)=>{ if(e.key!=='Escape') return; const d=document.getElementById(G2_DICA_ID); if(!d||d.hidden||!G2D.el) return;
    const exp=G2D.el.hasAttribute('data-dica'); g2dicaFecha(); if(exp){ e.preventDefault(); e.stopPropagation(); } },true);
  // toque longo (500 ms parado) mostra a dica e não aciona o comando; tocar fora fecha
  document.addEventListener('pointerdown',(e)=>{ if(e.pointerType!=='touch') return; const a=g2dicaAlvo(e.target);
    if(!a){ if(G2D.el&&!dentro(e.target)) g2dicaFecha(); return; }
    clearTimeout(G2D.lp); G2D.lpXY=[e.clientX,e.clientY]; G2D.lp=setTimeout(()=>{ G2D.lp=0; G2D.toque=Date.now(); g2dicaMostra(a.el,a.t,'toque'); g2dicaSai(4000); },500); },true);
  document.addEventListener('pointermove',(e)=>{ if(e.pointerType==='touch'&&G2D.lp&&G2D.lpXY&&Math.hypot(e.clientX-G2D.lpXY[0],e.clientY-G2D.lpXY[1])>10){ clearTimeout(G2D.lp); G2D.lp=0; } },true);
  const solta=()=>{ clearTimeout(G2D.lp); G2D.lp=0; }; document.addEventListener('pointerup',solta,true); document.addEventListener('pointercancel',solta,true);
  document.addEventListener('contextmenu',(e)=>{ if(G2D.toque&&Date.now()-G2D.toque<900) e.preventDefault(); },true);
  document.addEventListener('click',(e)=>{
    if(G2D.toque&&Date.now()-G2D.toque<900){ G2D.toque=0; e.preventDefault(); e.stopPropagation(); return; }   // o toque longo foi para ler a dica
    const t=e.target;
    // ícone ⓘ: tocar (ou Enter) abre e fecha a dica; não é comando
    const i=t&&t.closest&&t.closest('.g2dica-i,.g2-info'); if(i){ e.preventDefault(); e.stopPropagation(); if(G2D.el===i) g2dicaFecha(); else { g2dicaMostra(i,g2dicaTexto(i),'toque'); g2dicaSai(6000); } return; }
    // indisponível com motivo (aria-disabled="true"): o comando não roda; a dica diz o porquê e o leitor de tela ouve a recusa
    const b=t&&t.closest&&t.closest('[aria-disabled="true"]'); if(b&&b.matches('button,a,[role=button]')){ e.preventDefault(); e.stopPropagation();
      const m=g2dicaTexto(b)||'Indisponível agora.'; g2dicaMostra(b,m,'recusa'); g2dicaSai(4000);
      const mv=b.closest('.g2ind'); g2flash(mv&&mv.querySelector('.g2motivo'),'Indisponível: '+m); } },true);   /* o motivo visível junto do botão (acao_motivo) é realçado */
  const repos=()=>{ if(G2D.el) g2dicaPos(); }; window.addEventListener('resize',()=>{ if(G2D.el) g2dicaFecha(); }); document.addEventListener('scroll',repos,true);
  try{ new MutationObserver(()=>{ if(G2D.el&&!g2vis(G2D.el)) g2dicaFecha(); }).observe(document.documentElement,{childList:true,subtree:true}); }catch(e){}
})();
// ===== VISOES-1 · seletor de visões das listagens (pedido do proprietário, 10/10/2026: "a visão nasce do atributo dominante") =====
// A lista de visões válidas vem pronta do build (visoes.py → engine.visoes → G2_VISOES); aqui só o comportamento, sem recalcular regra.
// Estado na grade (self.state.g2[gid].visao); endereço ?view=<k> gravado em toda escolha explícita, a Lista também (revisão Codex
// 6093255041, item 1: sem o parâmetro vale a preferência só na entrada sem escolha); preferência por perfil × entidade no localStorage
// (safrion.pref.visao:<perfil>:<entidade>, prefixo que o TF02 ignora); precedência URL › preferência › Lista. Trocar de visão nunca é ação
// de negócio (não grava no cenário). Trocar o perfil não muda a visão aberta; a preferência do novo perfil vale na próxima entrada sem ?view.
const G2_VISAO_PREF='safrion.pref.visao:'; const G2_VISAO_MEM={};
/* VISOES-2 · semana do Calendário (segunda a domingo) em ISO e sem fuso: a janela da O.S. é de dias, não de instantes */
function g2isoDia(iso){ const a=String(iso||'').split('-').map(Number); return (a.length===3&&a.every(n=>n>0))?new Date(Date.UTC(a[0],a[1]-1,a[2])):null; }
function g2somaDias(iso,n){ const d=g2isoDia(iso); if(!d) return ''; d.setUTCDate(d.getUTCDate()+n); return d.toISOString().slice(0,10); }
function g2segunda(iso){ const d=g2isoDia(iso); return d?g2somaDias(iso,-((d.getUTCDay()+6)%7)):''; }
function g2semana(seg){ return g2isoDia(seg)?Array.from({length:7},(_,i)=>g2somaDias(seg,i)):[]; }
/* a ordem está no dia se o dia cai na janela (início a fim; sem fim ou fim antes do início, só o dia do início); sem início, não está em dia nenhum */
function g2noDia(ini,fim,dia){ if(!ini) return false; const f=(fim&&fim>=ini)?fim:ini; return ini<=dia&&dia<=f; }
function g2visaoValida(k,validas){ return typeof k==='string'&&/^[a-z]+$/.test(k)&&(validas||[]).indexOf(k)>=0; }
// precedência (pura): ?view válida › preferência válida › a primeira das válidas (Lista); valor fora das válidas ou fora de ^[a-z]+$: aviso
function g2visaoInicial(search,pref,validas){ let q=null; try{ q=new URLSearchParams(String(search||'')).get('view'); }catch(e){ q=null; }
  if((q==='tabela'||q==='agrupada')&&(validas||[]).indexOf('lista')>=0&&(validas||[]).indexOf(q)<0) q='lista';   // VISOES-2: Tabela única (agrupada → Agrupar por Onde, g2agLer)
  if(pref==='agrupada'&&(validas||[]).indexOf('agrupada')<0) pref='lista';
  if(q!==null&&g2visaoValida(q,validas)) return {k:q,fonte:'url',aviso:false};
  const lista=(validas&&validas.length)?validas[0]:'lista', p=g2visaoValida(pref,validas)?pref:'';
  return {k:p||lista,fonte:p?'pref':'lista',aviso:q!==null}; }
// aviso do valor inválido no endereço: nunca repete o valor cru (só o nome da visão aberta)
function g2visaoAviso(ini,nome){ if(!ini||!ini.aviso) return '';
  return 'A visão pedida no endereço não existe nesta lista: aberta em '+(ini.fonte==='pref'?(nome||ini.k)+' (sua última escolha)':(nome||'Lista'))+'.'; }
// endereço com a visão (puro): k grava ?view=<k>; k vazio tira o parâmetro; o hash e os outros parâmetros ficam como estavam, em texto cru
// (revisão VISOES-1, achado A8: URLSearchParams.toString() recodificava a query inteira, "%20" virava "+" e "flag" virava "flag=")
function g2visaoUrl(pathname,search,hash,k){ const s=String(search||'').replace(/^\?/,'');
  const ps=s?s.split('&').filter(p=>p&&(p.indexOf('=')<0?p:p.slice(0,p.indexOf('=')))!=='view'):[];
  if(k) ps.push('view='+encodeURIComponent(k)); return String(pathname||'')+(ps.length?'?'+ps.join('&'):'')+String(hash||''); }
// teclado da barra horizontal (pura): ← → movem o foco com volta, Home e End vão às pontas; ↑ ↓ não movem (no "mais", ↓ abre o menu).
// Nenhuma seta ativa: ativar é Enter ou Espaço, nativos do botão (devolve nulo para elas e para as outras teclas)
function g2visaoTecla(i,tecla,n,noMais){ if(!(n>0)||!(i>=0)||i>=n) return null;
  if(tecla==='ArrowRight') return {foco:(i+1)%n}; if(tecla==='ArrowLeft') return {foco:(i-1+n)%n};
  if(tecla==='Home') return {foco:0}; if(tecla==='End') return {foco:n-1};
  if(tecla==='ArrowDown'&&noMais) return {abre:true};
  return null; }
function g2visaoChave(perfil,ent){ return G2_VISAO_PREF+String(perfil||'')+':'+String(ent||''); }
// preferência: leitura e escrita com try/catch e cópia em memória (janela privada ou armazenamento bloqueado abre a Lista, sem erro)
function g2visaoPrefLer(chave,st){ let v=null; try{ const s=st||(typeof localStorage!=='undefined'?localStorage:null); v=s?s.getItem(chave):null; }catch(e){ v=null; }
  return (v!==null&&v!==undefined)?v:(G2_VISAO_MEM[chave]||null); }
function g2visaoPrefGrava(chave,k,st){ G2_VISAO_MEM[chave]=k; try{ const s=st||(typeof localStorage!=='undefined'?localStorage:null); if(s) s.setItem(chave,k); }catch(e){} }
// celular (pura): até 3 visões, todas na barra; 4 ou mais, as 3 primeiras e "mais" com as demais; a ativa dentro do "mais" marca o "mais"
function g2visoesCelular(validas,ativa){ const v=(validas||[]).slice(); if(v.length<2) return {barra:[],mais:[],maisAtivo:false};
  if(v.length<=3) return {barra:v,mais:[],maisAtivo:false}; const mais=v.slice(3); return {barra:v.slice(0,3),mais,maisAtivo:mais.indexOf(ativa)>=0}; }
// volta do detalhe (puras; DESENHO §2.11, rev. Codex 01 e 02, VISOES-REV-20261010-02/03). O "Voltar" e a trilha da página de detalhe SEMPRE
// navegam ao destino canônico da lista (o arquivo com ?view e a ficha ?volta=<nt> do contexto de retorno): nunca o "voltar" do histórico, nunca
// adivinhar a entrada anterior. A lista só aplica o contexto se ele for válido (g2voltaValida); senão abre canônica, sem estado antigo.
const G2_VOLTA_MS=3600000;   // contexto de retorno vale até 1 h
function g2voltaForma(c){ return !!c&&typeof c==='object'&&/^[A-Za-z0-9][A-Za-z0-9_-]*(\.[A-Za-z0-9_-]+)*\.html$/.test(String(c.arq||''))&&/^[a-z]+$/.test(String(c.ent||''))
  &&/^[a-z]+$/.test(String(c.view||''))&&/^[A-Za-z0-9_]+$/.test(String(c.gid||''))&&/^[a-z0-9]+$/.test(String(c.nt||'')); }
// '' quando o contexto vale para esta chegada (a: nt da ficha no endereço, origem, arquivo e entidade da lista, perfil e escopo Fazenda/Safra
// atuais, agora); senão o motivo da recusa. Usado uma vez, não vale de novo
function g2voltaValida(c,a){ if(!c) return 'ausente'; if(!g2voltaForma(c)) return 'forma'; if(!a||String(a.nt||'')!==c.nt) return 'outra ficha';
  if(c.usado) return 'usado'; if(c.origem!==a.origem) return 'outra origem'; if(c.arq!==a.arq) return 'outro arquivo'; if(c.ent!==a.ent) return 'outra entidade';
  if(c.perfil!==a.perfil) return 'outro perfil'; if(c.faz!==a.faz||c.saf!==a.saf) return 'outro escopo';
  const t=Number(c.t)||0; if(!(a.agora>=t&&a.agora-t<G2_VOLTA_MS)) return 'antigo'; return ''; }
// destino canônico do "Voltar": a lista na visão em que estava, com os outros parâmetros dela e a ficha do contexto
function g2voltaUrl(c){ const u=g2visaoUrl(c.arq,c.q||'','',c.view); return u+(u.indexOf('?')<0?'?':'&')+'volta='+c.nt; }

function g2visaoSpec(gid){ return (typeof G2_VISOES!=='undefined'&&G2_VISOES&&G2_VISOES[gid])||null; }
function g2arq(){ try{ return String(location.pathname).split('/').pop(); }catch(e){ return ''; } }
// visão aberta da grade; na primeira leitura da tela aplica a precedência; o aviso do valor inválido sai uma vez e o endereço perde o valor
// inválido (o F5 não repete o aviso)
function g2visao(self,gid){ const sp=g2visaoSpec(gid); if(!sp) return 'lista'; const st=g2st(self,gid); if(st.visao&&sp.validas.indexOf(st.visao)>=0) return st.visao;
  g2voltaChegada(self,gid,sp);   // antes da visão inicial: a ficha de retorno recusada tira do endereço a visão que veio com ela
  let search=''; try{ search=location.search; }catch(e){}
  const ini=g2visaoInicial(search,g2visaoPrefLer(g2visaoChave(g2perfil().k,sp.ent)),sp.validas);
  const all=Object.assign({},self.state.g2||{}); all[gid]=Object.assign({},all[gid]||{},{visao:ini.k}); self.state.g2=all;
  if(ini.aviso){ try{ history.replaceState(history.state,'',g2visaoUrl(location.pathname,location.search,location.hash,'')); }catch(e){}
    const m=g2visaoAviso(ini,(sp.nomes||{})[ini.k]); setTimeout(()=>self.setState({g2toast:m}),0); }
  g2visaoLiga(self,gid); return ini.k; }
// rolagem por visão: casca, conteúdo e as caixas que rolam dentro do corpo das visões
function g2rolCaixas(gid){ return [...document.querySelectorAll('main .g2rola,main .rola,main [style*="overflow-x: auto"],main [style*="overflow: auto"]')].filter(e=>g2vis(e)&&!e.closest('aside[role=dialog],[role=dialog]')); }
function g2rolLe(gid){ if(typeof document==='undefined') return null; const col=document.querySelector('.ml-tog+div'), m=document.querySelector('main[data-scroll]')||document.querySelector('main');
  return {col:col?col.scrollTop:0,main:m?m.scrollTop:0,cx:g2rolCaixas(gid).map(e=>[e.scrollTop,e.scrollLeft])}; }
function g2rolPoe(r,gid){ if(!r||typeof document==='undefined') return; const col=document.querySelector('.ml-tog+div'), m=document.querySelector('main[data-scroll]')||document.querySelector('main');
  if(col) col.scrollTop=r.col||0; if(m) m.scrollTop=r.main||0; g2rolCaixas(gid).forEach((e,i)=>{ const x=(r.cx||[])[i]; if(x){ e.scrollTop=x[0]; e.scrollLeft=x[1]; } }); }
// trocar de visão: grava o endereço (?view, replaceState: o Voltar sai da tela, não percorre visões) e, só na escolha pelo seletor, a preferência;
// "Ver em tabela" de um estado (origem fallback) não grava a preferência. A rolagem da visão de saída fica guardada e a da nova volta.
function g2visaoIr(self,gid,k,origem){ const sp=g2visaoSpec(gid); if(!sp||sp.validas.indexOf(k)<0) return; const ant=g2visao(self,gid);
  if(k!==ant){ (self.__g2rol=self.__g2rol||{})[gid+':'+ant]=g2rolLe(gid); }
  if(origem==='seletor') g2visaoPrefGrava(g2visaoChave(g2perfil().k,sp.ent),k);
  try{ history.replaceState(history.state,'',g2visaoUrl(location.pathname,location.search,location.hash,k)); }catch(e){}
  g2set(self,gid,{visao:k,vf:null,vm:false});
  setTimeout(()=>{ try{ if(k!==ant){ const r=(self.__g2rol||{})[gid+':'+k]; if(r) g2rolPoe(r,gid); }
    if(origem==='seletor'){ const b=g2visaoBotao(gid,k); if(b&&document.activeElement!==b) b.focus({preventScroll:true}); } }catch(e){} },0); }
// o botão visível da visão k na barra (no estreito, a visão do "mais" é o próprio "mais")
function g2visaoBotao(gid,k){ if(typeof document==='undefined') return null; const bar=document.querySelector('[data-visoes-gid="'+gid+'"]'); if(!bar) return null;
  const b=[...bar.querySelectorAll('[data-visao="'+k+'"]')].find(g2vis)||bar.querySelector('[data-visao-mais]'); return b&&g2vis(b)?b:null; }
// a visão não montou: o erro fica no estado da visão (§2.8) e o painel some; "Ver em tabela" leva à Lista, que não depende dela.
// window.__g2visaoFalha = '<k>' simula a falha (teste), como o ?falha=1 do AGROFIT
function g2visaoTenta(self,gid,k,fn){ const e=(self.__g2vErr=self.__g2vErr||{}); const m=(e[gid]=e[gid]||{}); delete m[k];
  try{ if(typeof window!=='undefined'&&window.__g2visaoFalha===k) throw new Error('falha simulada pelo teste'); fn(); return true; }
  catch(er){ m[k]=String((er&&er.message)||er).replace(/\.$/,'').slice(0,160); return false; } }
function g2visaoMenuFoco(gid){ const m=document.querySelector('[data-visoes-menu="'+gid+'"]'); if(!m) return;
  const its=[...m.querySelectorAll('[role=menuitemradio]')]; const c=its.find(x=>x.getAttribute('aria-checked')==='true')||its[0]; if(c) c.focus(); }
function g2visaoTeclaBarra(self,gid,e){ const bar=e.currentTarget, t=e.target; if(!bar||!t||!t.matches||!t.matches('[data-visao],[data-visao-mais]')) return;
  const bs=[...bar.querySelectorAll('[data-visao],[data-visao-mais]')].filter(g2vis); const i=bs.indexOf(t);
  const r=g2visaoTecla(i,e.key,bs.length,t.hasAttribute('data-visao-mais')); if(!r) return; e.preventDefault();
  if(r.abre){ g2set(self,gid,{vm:true,vf:'__mais'}); setTimeout(()=>g2visaoMenuFoco(gid),0); return; }
  const b=bs[r.foco]; b.focus(); g2set(self,gid,{vf:b.getAttribute('data-visao')||'__mais'}); }
function g2visaoTeclaMenu(self,gid,e){ const m=e.currentTarget; const its=[...m.querySelectorAll('[role=menuitemradio]')]; const i=its.indexOf(e.target);
  if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); g2set(self,gid,{vm:false});
    setTimeout(()=>{ const b=document.querySelector('[data-visoes-gid="'+gid+'"] [data-visao-mais]'); if(b) b.focus(); },0); return; }
  if(e.key==='Tab'){ g2set(self,gid,{vm:false}); return; }
  let j=null; if(e.key==='ArrowDown') j=(i+1)%its.length; else if(e.key==='ArrowUp') j=(i-1+its.length)%its.length; else if(e.key==='Home') j=0; else if(e.key==='End') j=its.length-1;
  if(j!==null&&its[j]){ e.preventDefault(); its[j].focus(); } }
// buracos do componente, depois do EXTRAVALS da tela (o estado da visão usa o recorte que a tela calculou)
function g2visoesFim(self,v){ if(typeof G2_VISOES==='undefined'||!G2_VISOES) return;
  for(const gid in G2_VISOES){ const sp=G2_VISOES[gid]; const k=g2visao(self,gid), st=g2st(self,gid), err=((self.__g2vErr||{})[gid])||{};
    const cel=g2visoesCelular(sp.validas,k), ir=(x)=>()=>g2visaoIr(self,gid,x,'seletor');
    // a parada de Tab lembrada pelas setas (vf) só vale se o botão dela aparece nesta largura (revisão VISOES-1, achados A6/B2: depois de
    // estreitar, alargar ou girar, ela ficava num botão oculto e o Tab pulava o seletor); senão volta à ativa (ou ao "mais" com a ativa nele)
    let vf=st.vf||null; if(vf){ let est=false; try{ est=matchMedia('(max-width:640px)').matches; }catch(e){} const i=sp.validas.indexOf(vf);
      if((vf==='__mais'&&(!est||sp.validas.length<=3))||(i>=3&&est)||(vf!=='__mais'&&i<0)) vf=null; }
    sp.validas.forEach(x=>{ v[gid+'_vb_'+x+'_p']=x===k?'true':'false'; v[gid+'_vb_'+x+'_t']=((vf?vf===x:x===k))?'0':'-1'; v[gid+'_vb_'+x+'_go']=ir(x);
      v[gid+'_vmi_'+x+'_c']=x===k?'true':'false'; v[gid+'_vmi_'+x+'_go']=ir(x); });
    (sp.paineis||[]).forEach(pn=>{ v[gid+'_vp_'+pn[0]]=pn.indexOf(k)>=0&&!err[k]; });
    const maisFoc=vf?vf==='__mais':cel.maisAtivo;
    v[gid+'_vm_t']=maisFoc?'0':'-1'; v[gid+'_vm_on']=cel.maisAtivo?'true':'false'; v[gid+'_vm_x']=st.vm?'true':'false'; v[gid+'_vm_open']=!!st.vm;
    v[gid+'_vm_lab']='Mais visões'+(cel.maisAtivo?' (atual: '+String((sp.nomes||{})[k]||k).toLowerCase()+')':'');
    v[gid+'_vm_go']=()=>{ const ab=!g2st(self,gid).vm; g2set(self,gid,{vm:ab}); if(ab) setTimeout(()=>g2visaoMenuFoco(gid),0); };
    v[gid+'_vk']=(e)=>g2visaoTeclaBarra(self,gid,e); v[gid+'_vmk']=(e)=>g2visaoTeclaMenu(self,gid,e);
    // estado em toda visão (§2.8): o erro da visão vem primeiro (a Lista continua disponível); depois o que a tela informa
    let es=null;
    if(err[k]) es={tipo:'erro',texto:'Não foi possível mostrar a visão '+((sp.nomes||{})[k]||k)+': '+err[k]+'.',acao:'Ver em tabela',fn:()=>g2visaoIr(self,gid,sp.validas[0],'fallback')};
    else if(self.g2visaoEstado) es=self.g2visaoEstado(gid,k)||null;
    v[gid+'_vest_on']=!!es; v[gid+'_vest_t']=es?es.texto:''; v[gid+'_vest_tipo']=es?es.tipo:''; v[gid+'_vest_a']=(es&&es.acao)||'';
    // a ação do estado some no redesenho e levava o foco ao <body> (revisão VISOES-1, achados B4/C4): o foco vai ao botão da visão aberta
    v[gid+'_vest_tema']=!!(es&&es.acao&&es.fn); v[gid+'_vest_go']=(es&&es.fn)?(()=>{ es.fn(); setTimeout(()=>{ try{ const a=document.activeElement;
      if(a&&a!==document.body&&g2vis(a)) return; const b=g2visaoBotao(gid,g2visao(self,gid)); if(b) b.focus({preventScroll:true}); }catch(e){} },0); }):(()=>{});
    // rolagem e foco restaurados na volta: reafirmados depois de cada desenho até a 1ª interação da pessoa (revisão VISOES-1, achado A4)
    const fg=self.__g2focoGuarda; if(fg){ if(Date.now()>fg.ate) self.__g2focoGuarda=null; else setTimeout(fg.fn,0); } } }
// ---- volta do detalhe (§2.11, rev. Codex 01 e 02; VISOES-REV-20261010-02/03): contexto de retorno na sessão da aba, validado na lista ----
// Ao sair da lista por um link (clique, Ctrl ou meio para nova aba), ela grava o contexto: arquivo, entidade, perfil, Fazenda e Safra, visão,
// filtros da grade (g2keep), rolagem e o registro aberto (foco). O "Voltar"/trilha do detalhe leva ao destino canônico com a ficha (?volta=<nt>);
// a lista aplica o contexto só se for válido (g2voltaValida) e o marca como usado. Recusado (antigo, de outro perfil ou escopo, já usado, de
// outra ficha): a lista abre canônica, no escopo atual, sem a visão, os filtros nem a posição antigos. O Voltar nativo do navegador
// (back_forward) continua restaurando a rolagem e o foco da entrada que a lista marcou ao sair.
const G2_VOLTA='g2volta';
function g2voltaLer(){ try{ const c=JSON.parse(sessionStorage.getItem(G2_VOLTA)||'null'); return g2voltaForma(c)?c:null; }catch(e){ return null; } }
function g2voltaNt(){ return (Math.random().toString(36).slice(2,10)+Date.now().toString(36)).replace(/[^a-z0-9]/g,''); }
function g2escopo(self){ const s=(self&&self.state)||{}; return {faz:s.mf_faz||'Santa Rita',saf:s.mf_saf||'Todas'}; }   // padrões do motor (ENGINE_JS2: mf_faz, mf_saf)
function g2voltaGuarda(self,gid,dest){ const sp=g2visaoSpec(gid); if(!sp) return; const k=g2visao(self,gid), arq=g2arq(), nt=g2voltaNt(), st=g2st(self,gid), es=g2escopo(self);
  let q=''; try{ q=String(location.search||'').replace(/^\?/,'').split('&').filter(p=>p&&!/^(view|volta)(=|$)/.test(p)).join('&'); }catch(e){}
  const c={arq,ent:sp.ent,gid,view:k,q,foco:String((self.g2visaoFoco&&self.g2visaoFoco(gid))||''),nt,t:Date.now(),dest:String(dest||''),
    origem:String(location.origin),perfil:g2perfil().k,faz:es.faz,saf:es.saf,keep:{f:st.f||{},q:st.q||'',so:st.so||null,qv:st.qv||''},rol:g2rolLe(gid)};
  try{ sessionStorage.setItem('g2rol:'+arq+':'+gid+':'+k,JSON.stringify(c.rol)); sessionStorage.setItem(G2_VOLTA,JSON.stringify(c)); }catch(e){}
  try{ history.replaceState(Object.assign({},history.state||{},{g2volta:nt}),'',location.href); }catch(e){} }
// chegada na lista (1º desenho, antes da visão inicial): a ficha ?volta=<nt> sai do endereço; válida → filtros do contexto, foco e rolagem;
// recusada → sem ?view, filtros limpos (o g2keep também), sem posição. Escopo Fazenda/Safra: o da sessão (g2keep), que já está no estado
function g2voltaChegada(self,gid,sp){ if(self.__g2chegou) return; self.__g2chegou=1; if(typeof location==='undefined') return;
  let nt=null; try{ nt=new URLSearchParams(location.search).get('volta'); }catch(e){} if(nt===null) return;
  const c=g2voltaLer(), es=g2escopo(self);
  const mot=g2voltaValida(c,{nt,origem:String(location.origin),arq:g2arq(),ent:sp.ent,perfil:g2perfil().k,faz:es.faz,saf:es.saf,agora:Date.now()});
  // a ficha sai do endereço; recusada, sai também a visão (g2visaoUrl troca só o view= e mantém o resto da query cru)
  // recusada (defeito B): sai também o agrupamento que veio com a ficha (ag, trilha); vale a preferência do perfil, como a visão
  const q=String(location.search||'').replace(/^\?/,'').split('&').filter(p=>p&&!/^volta(=|$)/.test(p)&&!(mot&&/^(ag|trilha)(=|$)/.test(p))).join('&');
  let vw=''; try{ vw=mot?'':(new URLSearchParams(location.search).get('view')||''); }catch(e){}
  try{ history.replaceState(history.state,'',g2visaoUrl(location.pathname,q,location.hash,vw)); }catch(e){}
  self.__g2voltaMotivo=mot; const all=Object.assign({},self.state.g2||{});
  // recusada: também o agrupamento da sessão sai (ag/agx/x); vale a preferência do perfil atual, como a visão (defeito B, perfil Caio)
  if(mot){ all[gid]=Object.assign({},all[gid]||{},{f:{},q:'',so:null,qv:'',sel:{}}); delete all[gid].ag; delete all[gid].agx; delete all[gid].x; self.state.g2=all; g2keepGrava(self,gid,all[gid]); return; }
  c.usado=Date.now(); try{ sessionStorage.setItem(G2_VOLTA,JSON.stringify(c)); }catch(e){}
  const kp=(c.keep&&typeof c.keep==='object')?c.keep:{}; all[gid]=Object.assign({},all[gid]||{},{f:kp.f||{},q:kp.q||'',so:kp.so||null,qv:kp.qv||''}); self.state.g2=all; g2keepGrava(self,gid,all[gid]);
  self.__g2voltaAlvo={foco:c.foco||'',rol:c.rol||null}; }
// na lista: volta válida (g2voltaChegada) ou Voltar nativo com a marca desta entrada → rolagem e foco no registro aberto; o foco é reafirmado a
// cada desenho até a 1ª interação da pessoa (um redesenho do runtime reaproveitava a linha focada para outra ordem)
function g2visaoLiga(self,gid){ if(typeof window==='undefined'||window.__g2visaoTela) return; window.__g2visaoTela={self,gid};
  let nav=''; try{ nav=((performance.getEntriesByType('navigation')||[])[0]||{}).type||''; }catch(e){}
  const arq=g2arq(); let alvo=self.__g2voltaAlvo||null;
  if(!alvo&&nav==='back_forward'){ const c=g2voltaLer(), marca=(history.state||{}).g2volta; if(c&&c.arq===arq&&c.gid===gid&&marca===c.nt) alvo={foco:c.foco||'',rol:null}; }
  if(!alvo) return;
  const linha=()=>alvo.foco?([...document.querySelectorAll('[data-g2g="'+gid+'"] [role=row][data-rid]')].find(x=>g2vis(x)&&String(x.getAttribute('data-rid')).split('@')[0]===alvo.foco)
      ||[...document.querySelectorAll('[role=list] [role=button][aria-label]')].find(x=>g2vis(x)&&String(x.getAttribute('aria-label')).indexOf('Abrir '+alvo.foco+' ')===0)):null;
  const foca=()=>{ try{ const el=linha(); if(el&&document.activeElement!==el) el.focus({preventScroll:true}); }catch(e){} };
  // rolagem e foco reafirmados a cada desenho até a 1ª interação (sob carga a lista cresce depois dos 450 ms e a rolagem ficava em 0)
  const poe=()=>{ try{ const k=g2visao(self,gid); let ro=alvo.rol; if(!ro){ try{ ro=JSON.parse(sessionStorage.getItem('g2rol:'+arq+':'+gid+':'+k)||'null'); }catch(e){} }
    if(ro) g2rolPoe(ro,gid); foca(); }catch(e){} };
  self.__g2focoGuarda={fn:poe,ate:Date.now()+10000};
  const ev=['pointerdown','keydown','wheel','touchstart'], solta=()=>{ self.__g2focoGuarda=null; ev.forEach(t=>document.removeEventListener(t,solta,true)); };
  ev.forEach(t=>document.addEventListener(t,solta,true));
  setTimeout(poe,80); setTimeout(poe,450); setTimeout(()=>{ if(self.__g2focoGuarda) poe(); },1200); }
(function g2visaoGlob(){ if(typeof document==='undefined'||window.__g2visaoGlob) return; window.__g2visaoGlob=1;
  // menu "mais" aberto: tocar fora fecha
  document.addEventListener('pointerdown',(e)=>{ const t=window.__g2visaoTela; if(!t||!g2st(t.self,t.gid).vm) return;
    if(!(e.target&&e.target.closest&&e.target.closest('.g2visoes-w'))) g2set(t.self,t.gid,{vm:false}); },true);
  // a parada de Tab lembrada pelas setas (vf) só vale com o foco na barra: ao sair, volta à ativa (revisão VISOES-1, achados A6/B2); mudar a
  // largura em torno de 640 px (giro, janela, zoom) também a esquece e fecha o "mais", que some no largo (achado B5)
  document.addEventListener('focusout',(e)=>{ const w=e.target&&e.target.closest&&e.target.closest('.g2visoes-w'); if(!w) return; const rt=e.relatedTarget;
    if(rt&&w.contains(rt)) return; const t=window.__g2visaoTela; if(t&&g2st(t.self,t.gid).vf) g2set(t.self,t.gid,{vf:null}); },true);
  try{ const mq=matchMedia('(max-width:640px)'), muda=()=>{ const t=window.__g2visaoTela; if(!t) return; const st=g2st(t.self,t.gid); if(st.vf||st.vm) g2set(t.self,t.gid,{vf:null,vm:false}); };
    if(mq.addEventListener) mq.addEventListener('change',muda); else if(mq.addListener) mq.addListener(muda); }catch(e){}
  const lnk=(e)=>{ const a=e.target&&e.target.closest&&e.target.closest('a[href]'); if(!a) return null; let u=null; try{ u=new URL(a.getAttribute('href'),location.href); }catch(er){ return null; }
    return u.origin===location.origin?{a,u,dest:u.pathname.split('/').pop()}:null; };
  // sair da lista por um link (clique, Ctrl/meio para nova aba): guarda o contexto de retorno
  const sai=(e)=>{ const t=window.__g2visaoTela; if(!t) return; const l=lnk(e); if(!l||l.dest===g2arq()) return; g2voltaGuarda(t.self,t.gid,l.dest); };
  document.addEventListener('click',sai,true); document.addEventListener('auxclick',sai,true);
  // "Voltar" (seta da página de detalhe) e a trilha do cabeçalho: sempre o destino canônico com a ficha do contexto desta aba; sem contexto desta
  // aba para esta lista (link direto, aba sem opener, contexto já usado), o link segue como está. Nunca o "voltar" do histórico
  document.addEventListener('click',(e)=>{ if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||window.__g2visaoTela) return;
    const l=lnk(e); if(!l) return; const a=l.a; if(!(a.getAttribute('aria-label')==='Voltar'||(a.closest('header')&&!a.closest('.menu-lat')))) return;
    const c=g2voltaLer(); if(!c||c.usado||c.arq!==l.dest||c.dest!==g2arq()) return;
    a.setAttribute('href',g2voltaUrl(c)); },true);
})();
