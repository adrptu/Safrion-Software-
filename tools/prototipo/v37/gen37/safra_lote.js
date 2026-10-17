// ===== EDL-01 · Editar talhões da fazenda numa grade só (proprietário, 16/10/2026: "coloque um botao para poder editar de uma vez todos
// talhoes de uma fazenda numa tela só. como no outro anexo. todos inputs do usuário no sistema devem ser mais rápido e fácil.")
// Uma linha por talhão da fazenda nesta safra (as parcelas embaixo, recuadas), as colunas do Dividir e a Situação. Rapidez: navegação de
// planilha (Tab, Enter/↓, ↑, Esc), marcar linhas e "Aplicar aos marcados", colar bloco do Excel/Planilhas e contador de alterações.
// Regras: as mesmas funções do painel do cultivo (cultCheck) e do Dividir (dvConferir); nada é gravado antes do "Salvar alterações", e a
// gravação é atômica por fazenda, com chave do comando gerada ao abrir (duplo clique não duplica). Docs: docs/integracao/V73/SAF-LOTE.md.

// >>> SL-PURO (sem estado da tela: testado no node por saf_lote_unit_test.py)
const SL_COLS=['area','cult','var','plantio','meta','plano'];
const SL_ROT={area:'Área',cult:'Cultura',var:'Variedade',plantio:'Plantio',meta:'Meta',plano:'Plano agronômico'};
function slSemAc(s){ return String(s==null?'':s).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/\s+/g,' ').trim(); }
// bloco copiado de planilha (TSV): linhas por \r\n, \n ou \r; células por tabulação; célula entre aspas pode ter tabulação, quebra e "" (aspas)
function slTsv(txt){ const s=String(txt==null?'':txt); const M=[]; let lin=[], cel='', q=false, i=0, ini=true;
  while(i<s.length){ const ch=s[i];
    if(q){ if(ch==='"'){ if(s[i+1]==='"'){ cel+='"'; i+=2; continue; } q=false; i++; continue; } cel+=ch; i++; continue; }
    if(ch==='"'&&ini){ q=true; ini=false; i++; continue; }
    if(ch==='\t'){ lin.push(cel); cel=''; ini=true; i++; continue; }
    if(ch==='\r'||ch==='\n'){ lin.push(cel); M.push(lin); lin=[]; cel=''; ini=true; i+=(ch==='\r'&&s[i+1]==='\n')?2:1; continue; }
    cel+=ch; ini=false; i++; }
  if(cel!==''||lin.length) { lin.push(cel); M.push(lin); }
  while(M.length&&M[M.length-1].every(c=>String(c).trim()==='')) M.pop();
  return M.map(l=>l.map(c=>String(c).trim())); }
// número pt-BR da planilha ("1.234,5", "12,5", "64 sc/ha") → texto com vírgula ("1234,5"); inválido ou negativo → null (g2num, fonte única)
function slNumTxt(t){ const s=String(t==null?'':t).trim(); if(!s||/^-/.test(s)) return null; const n=g2num(s); if(isNaN(n)||n<0||!isFinite(n)) return null;
  return String(Math.round(n*1e6)/1e6).replace('.',','); }
// data digitada ou colada → aaaa-mm-dd. Aceita aaaa-mm-dd, dd/mm/aaaa, dd/mm/aa, dd/mm (o ano que cai dentro da safra), ddmmaaaa e ddmm;
// vazio → ''; inválida → null. ctx.ini e ctx.fim: o período da safra (aaaa-mm-dd)
function slData(t,ctx){ const s=String(t==null?'':t).trim(); if(!s) return ''; let d,m,y=null, x;
  if((x=/^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(s))){ y=+x[1]; m=+x[2]; d=+x[3]; }
  else if((x=/^(\d{1,2})[\/.\-](\d{1,2})(?:[\/.\-](\d{2}|\d{4}))?$/.exec(s))){ d=+x[1]; m=+x[2]; if(x[3]) y=x[3].length===2?2000+(+x[3]):+x[3]; }
  else if((x=/^(\d{2})(\d{2})(\d{4})?$/.exec(s))){ d=+x[1]; m=+x[2]; if(x[3]) y=+x[3]; }
  else return null;
  const ok=(yy)=>{ const D=new Date(Date.UTC(yy,m-1,d)); return D.getUTCFullYear()===yy&&D.getUTCMonth()===m-1&&D.getUTCDate()===d; };
  const iso=(yy)=>yy+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0');
  if(y===null){ const ini=String((ctx&&ctx.ini)||''), fim=String((ctx&&ctx.fim)||''); const y0=Number(ini.slice(0,4))||new Date().getFullYear(), y1=Number(fim.slice(0,4))||y0;
    for(let yy=y0; yy<=y1; yy++){ if(ok(yy)&&iso(yy)>=ini&&(!fim||iso(yy)<=fim)) return iso(yy); }
    y=y0; }
  if(y<1900||y>2200||!ok(y)) return null; return iso(y); }
// cultura e plano pelo texto (sem acento, sem diferença de maiúscula)
function slCultura(t,ctx){ const k=slSemAc(t); return (ctx.culturas||[]).find(c=>slSemAc(c)===k)||null; }
// plano pelo texto, só com correspondência exata (revisão do Codex 6229216931, PR #47: o prefixo e o nome repetido aplicavam outra receita):
// 1) o código do plano; 2) nome + versão ("Soja alta tecnologia v6"; o rótulo da lista, com "· N atividades", também vale); 3) o nome sem a
// versão, só se for único entre os planos da cultura da linha (sem cultura, no catálogo inteiro). Nada por prefixo, e a ordem do catálogo
// não decide nada. Devolve {id:''} (sem plano), o plano, {ambiguo:[planos]} ou null (não encontrado)
function slPlano(t,ctx,cult){ const k=slSemAc(t).replace(/\s*·\s*\d+\s+atividades?$/,''); if(!k||/^(sem plano|—|-|nenhum)$/.test(k)) return {id:''};
  const ps=ctx.planos||[]; const um=(l)=>{ if(!l.length) return null; const dc=cult?l.filter(p=>p.cultura===cult):[]; const m=dc.length?dc:l; return m.length===1?m[0]:{ambiguo:m}; };
  return um(ps.filter(p=>slSemAc(p.id)===k))||um(ps.filter(p=>slSemAc(p.nome+' v'+p.versao)===k))||um(ps.filter(p=>slSemAc(p.nome)===k)); }
function slCultDoPlano(id,ctx){ const p=(ctx.planos||[]).find(x=>x.id===id); return p?p.cultura:null; }
// pode receber o valor? {ok, v} ou {ok:false, motivo}. A linha traz o que trava (trava[col]: motivo da O.S., do ciclo ou da área calculada) e a
// cultura do rascunho (o plano tem de ser dela). Mesmas mensagens do Dividir e do painel do cultivo, curtas para o resumo da colagem
function slPode(lin,col,txt,ctx,cultAtual){ if(!lin||lin.tipo==='grp') return {ok:false,motivo:'linha de título'};
  if(lin.tipo==='ro') return {ok:false,motivo:lin.motivoRo||'só leitura'};
  if(lin.trava&&lin.trava[col]) return {ok:false,motivo:lin.trava[col]};
  const s=String(txt==null?'':txt).trim();
  if(col==='area'){ const n=slNumTxt(s); if(n===null) return {ok:false,motivo:'área inválida'}; const a=g2num(n);
    if(a<0.01) return {ok:false,motivo:'área mínima 0,01 ha'}; if(lin.T&&a>lin.T+0.005) return {ok:false,motivo:'acima dos '+String(lin.T).replace('.',',')+' ha do talhão'}; return {ok:true,v:n}; }
  if(col==='meta'){ const n=slNumTxt(s); return n===null?{ok:false,motivo:'meta inválida'}:{ok:true,v:n}; }
  if(col==='plantio'){ const d=slData(s,ctx); return d===null?{ok:false,motivo:'data inválida (use dd/mm/aaaa)'}:{ok:true,v:d}; }
  if(col==='cult'){ const c=slCultura(s,ctx); return c?{ok:true,v:c}:{ok:false,motivo:'cultura "'+s+'" não está no cadastro'}; }
  if(col==='var'){ const vc=s&&(ctx.cultivares||[]).find(x=>slSemAc(x[1])===slSemAc(s));   // revisão do app do Codex (#98, P2): a mesma regra do slTrocaCult
    if(vc&&cultAtual&&vc[0]!==cultAtual) return {ok:false,motivo:'cultivar de '+vc[0]+', não de '+cultAtual}; return {ok:true,v:s}; }
  if(col==='plano'){ const cu=cultAtual===undefined?lin.cult:cultAtual; const p=slPlano(s,ctx,cu);
    if(!p) return {ok:false,motivo:'plano "'+s+'" não encontrado (use o código ou o nome com a versão)'};
    if(p.ambiguo) return {ok:false,motivo:'plano "'+s+'" ambíguo: '+[...p.ambiguo].map(x=>x.nome+' v'+x.versao).sort().join(', ')+'; informe com a versão'};
    if(!p.id) return {ok:true,v:''};
    if(p.cultura!==cu) return {ok:false,motivo:'plano de '+p.cultura+' não serve para '+(cu||'linha sem cultura')}; return {ok:true,v:p.id}; }
  return {ok:false,motivo:'coluna sem edição'}; }
// trocar a cultura do rascunho: o plano e a variedade da cultura anterior saem; vazios, recebem a sugestão do contexto (ctx.sugere: a
// variedade e o plano mais usados nesta safra para a cultura; nunca área, meta, dose ou lote) e, na linha nova, o primeiro plantio possível
function slTrocaCult(v,nova,ctx,lin){ const o=Object.assign({},v,{cult:nova});
  if(o.plano&&slCultDoPlano(o.plano,ctx)!==nova) o.plano='';
  const vc=(ctx.cultivares||[]).find(x=>slSemAc(x[1])===slSemAc(o.var)); if(o.var&&vc&&vc[0]!==nova) o.var='';
  const sg=(ctx.sugere&&nova)?(ctx.sugere(nova,lin)||{}):{};
  if(!o.var&&sg.var&&!(lin&&lin.trava&&lin.trava.var)) o.var=sg.var;
  if(!o.plano&&sg.plano&&!(lin&&lin.trava&&lin.trava.plano)) o.plano=sg.plano;
  if(lin&&lin.tipo==='novo'&&!o.plantio&&sg.plantio) o.plantio=sg.plantio;
  return o; }
// põe um valor conferido no rascunho de uma linha (a cultura arrasta plano e variedade, como no formulário)
function slPor(vals,lin,col,v,ctx){ const cur=vals[lin.k]||{}; return Object.assign({},vals,{[lin.k]:col==='cult'?slTrocaCult(cur,v,ctx,lin):Object.assign({},cur,{[col]:v})}); }
// colar um bloco a partir da célula (l0 = índice na lista de linhas de dados, sem os títulos; col0 = coluna): célula vazia não apaga;
// devolve {vals, n (células coladas), recusas:[{rot, col, motivo}], dim:[linhas, colunas]}
function slColarBloco(lins,vals,l0,col0,M,ctx){ const c0=SL_COLS.indexOf(col0); let out=vals, n=0; const rec=[], feitos=[]; const nc=M.reduce((a,l)=>Math.max(a,l.length),0);
  if(c0<0) return {vals,n:0,recusas:[{rot:'',col:col0,motivo:'coluna sem edição'}],dim:[M.length,nc]};
  M.forEach((row,i)=>{ const lin=lins[l0+i];
    row.forEach((txt,j)=>{ const col=SL_COLS[c0+j]; if(String(txt).trim()==='') return;
      if(!lin){ rec.push({rot:'linha '+(l0+i+1),col:col||'',motivo:'além da última linha'}); return; }
      if(!col){ rec.push({rot:lin.rot,col:'',motivo:'além da última coluna'}); return; }
      const r=slPode(lin,col,txt,ctx,(out[lin.k]||{}).cult); if(!r.ok){ rec.push({rot:lin.rot,col,motivo:r.motivo}); return; }
      out=slPor(out,lin,col,r.v,ctx); n++; feitos.push([lin.k,col]); }); });
  return {vals:out,n,recusas:rec,dim:[M.length,nc],feitos}; }
// aplicar aos marcados: os campos preenchidos da faixa (ap) em cada linha marcada, na ordem das colunas (a cultura antes do plano)
function slAplicarSel(lins,vals,sel,ap,ctx){ let out=vals, n=0; const rec=[], feitos=[]; const cols=SL_COLS.filter(c=>String(ap[c]==null?'':ap[c]).trim()!=='');
  lins.filter(l=>sel[l.k]).forEach(lin=>{ cols.forEach(col=>{ const r=slPode(lin,col,ap[col],ctx,(out[lin.k]||{}).cult);
    if(!r.ok){ rec.push({rot:lin.rot,col,motivo:r.motivo}); return; } out=slPor(out,lin,col,r.v,ctx); n++; feitos.push([lin.k,col]); }); });
  return {vals:out,n,recusas:rec,cols,feitos}; }
// célula corrigida pela colagem ou pelo "Aplicar aos marcados" sai do erro, como na edição da célula (revisão do app do Codex, #98, P2)
function slSemErro(err,feitos){ const er=Object.assign({},err||{}); (feitos||[]).forEach(([k,col])=>{ if(!er[k]) return; const e=Object.assign({},er[k]); delete e[col]; if(col==='cult') delete e.plano;
  if(Object.keys(e).length) er[k]=e; else delete er[k]; }); return er; }
// células alteradas (o contador do Salvar e o destaque)
function slMudou(v,b,col){ return String((v||{})[col]==null?'':(v||{})[col]).trim()!==String((b||{})[col]==null?'':(b||{})[col]).trim(); }
function slContar(lins,vals,base){ let n=0; lins.forEach(l=>{ SL_COLS.forEach(c=>{ if(slMudou(vals[l.k],base[l.k],c)) n++; }); }); return n; }
// resumo das recusas: "2 recusados (T4 · Cultura: OS-0420 em execução; P1 · Plano: plano de Milho não serve para Soja)"
function slRecusasTxt(rec){ if(!rec.length) return ''; const it=rec.slice(0,4).map(r=>(r.rot?r.rot+(r.col?' · '+(SL_ROT[r.col]||r.col):''):(SL_ROT[r.col]||r.col))+': '+r.motivo);
  return rec.length+(rec.length>1?' recusados':' recusado')+' ('+it.join('; ')+(rec.length>4?'; e mais '+(rec.length-4):'')+')'; }
// <<< SL-PURO

// ---- O.S. que prende a receita do cultivo (resultado técnico) ----
// A ordem que já saiu do "A liberar" (Liberadas ou Em execução) foi emitida com a cultura, a variedade e o plano vigentes. Mudar esses campos
// no planejamento deixaria a ordem em campo diferente do plano. Fonte: o registro das ordens com safra e local (D2.osb, o mesmo da demanda,
// cenOsDem) e as ordens emitidas no cenário (osc.novo), com a fase viva do cenário compartilhado (outra aba que libera uma ordem conta)
const SL_OS_PRENDE=['Liberadas','Em execução'];
function slOsTravas(self,saf){ const out={}; const so=safById(self,saf); if(!so) return out; const c=cenGet(); const ords=(c&&c.ordens)||{}; const b=D2.osb||{};
  const poe=(l,id)=>{ const a=out[l]||(out[l]=[]); if(!a.some(x=>x.id===id)) a.push({id,etapa:ords[id].etapa}); };
  (b.ords||[]).forEach(o=>{ if(o.saf!==saf||!ords[o.id]||SL_OS_PRENDE.indexOf(ords[o.id].etapa)<0) return; (o.loc||[]).forEach(l=>poe(l,o.id)); });
  const safDe=(faz,lab)=>((b.safs||[]).find(s=>s.faz===faz&&String(s.nome).endsWith(String(lab||'')))||{}).id||'';   // como o cenOsDem
  Object.keys(ords).forEach(k=>{ const no=ords[k]&&ords[k].osc&&ords[k].osc.novo; if(!no||SL_OS_PRENDE.indexOf(ords[k].etapa)<0) return;
    if(safDe(no.faz||'Santa Rita',no.saf||'')===saf) poe(no.talhao,k); });
  return out; }
function slOsDe(trv,c){ const t=c.v.talhao||ocTalhaoDe(c.v.local,c.v.tipo); const l=(trv[c.v.local]||[]).concat(c.v.local!==t?(trv[t]||[]):[]); const vis={};
  return l.filter(x=>{ if(vis[x.id]) return false; vis[x.id]=1; return true; }); }
function slOsMotivo(os){ const o=os[0]; return o.id+' '+(o.etapa==='Em execução'?'em execução':'liberada')+': a ordem saiu com esta cultura, variedade e plano. Para mudar, conclua ou cancele a ordem'+(os.length>1?' (e '+os.slice(1).map(x=>x.id).join(', ')+')':'')+'.'; }

// ---- linhas do painel a partir da ocupação já calculada da sub-safra (talMontar) ----
function slInfo(self,saf){ return (self.__ocG&&self.__ocG[saf])||((self.__oc&&self.__oc.safra&&self.__oc.safra.id===saf)?self.__oc:null); }
function slSig(self,saf){ const trv=slOsTravas(self,saf); return JSON.stringify([cultsDe(self,saf).map(c=>[c.id,c.v.local,c.v.tipo,c.v.area,c.v.cult,c.v.var,c.v.plantio,c.v.meta,c.v.unm,c.v.plano,c.v.ciclo||'']),
  Object.keys(sempDe(self,saf)).sort(),Object.keys(trv).sort().map(k=>k+':'+trv[k].map(x=>x.id+'/'+x.etapa).join(','))]); }
function slLinhas(self,saf){ const info=slInfo(self,saf); if(!info||!info.linhas) return null; const trv=slOsTravas(self,saf); const own=cultsDe(self,saf);
  const tal=(r)=>r.v.talhao||ocTalhaoDe(r.v.local,r.v.tipo); const out=[]; const ctx=ocCtxSaf();
  const sitDe=(L)=>({t:L.sit,c:SIT_COR[L.sit]||'gray',d:L.semp?'Fora do plantio nesta safra.':ocMotivo(L,info)});
  const valsDe=(c)=>{ const m=metaRascunho(c.v.cult,c.v.meta,c.v.unm); return {v:{area:String(r2(c.v.area)).replace('.',','),cult:c.v.cult||'',var:c.v.var||'',plantio:c.v.plantio||'',meta:m.meta,plano:c.v.plano||''},m}; };
  const linCult=(c,tipo,nivel,L)=>{ const os=slOsDe(trv,c); const x=valsDe(c); const trava={};
    if(tipo==='tal') trava.area='A área do talhão inteiro vem do cadastro (CD-01). Para plantar parte dele, use Dividir.';
    if(c.v.ciclo){ const mc='Ciclo perene vinculado (R-24): cultura, cultivar, plantio e área vêm do ciclo.'; ['area','cult','var','plantio'].forEach(k=>{ trava[k]=mc; }); }
    if(os.length){ const mo=slOsMotivo(os); ['cult','var','plano'].forEach(k=>{ trava[k]=trava[k]||mo; }); }
    const sit=os.length?{t:'Bloqueado · '+os[0].id,c:'yellow',d:slOsMotivo(os)}:(c.v.ciclo?{t:'Ciclo vinculado',c:'gray',d:'Ciclo perene vinculado: plano e meta seguem editáveis.'}:sitDe(L));
    return {k:c.id,id:c.id,tipo:c.v.ciclo?'vinc':tipo,t:L.t,T:talhaoArea(L.t),nivel,rot:c.v.local,sub:(tipo==='par'?'Parcela':'Talhão inteiro')+' · '+nfa(c.v.area)+' ha',
      trava,sit,os,base:x.v,meta0:x.m,cult:c.v.cult,dv:(tipo==='par'?dvRow(c):null)}; };
  info.linhas.forEach(L=>{ const t=L.t, T=talhaoArea(t); const mine=own.filter(r=>tal(r)===t).sort((a,b)=>String(a.v.local).localeCompare(String(b.v.local),'pt-BR'));
    const livre=L.planejar&&!L.semp;
    const novo=(nivel,rot)=>{ const area=L.area_livre; return {k:'novo:'+t,id:null,tipo:'novo',t,T,nivel,rot,L,sub:'Livre · '+nfa(area)+' ha a partir de '+ocBr(L.desde)+(L.est?' (est.)':''),
      trava:{area:'Área livre calculada pela ocupação do talhão ('+nfa(area)+' ha). Para outra área, use Dividir depois de salvar.'},
      sit:{t:'Livre',c:'green',d:ocMotivo(L,info)||(nfa(area)+' ha livres')},os:[],base:{area:String(r2(area)).replace('.',','),cult:'',var:'',plantio:'',meta:'',plano:''},meta0:null,cult:'',area}; };
    if(mine.length===1&&mine[0].v.tipo!=='Parcela'){ out.push(linCult(mine[0],'tal',0,L)); return; }
    if(mine.length){ const A=mine.reduce((a,c)=>a+(Number(c.v.area)||0),0);
      out.push({k:'grp:'+t,tipo:'grp',t,T,nivel:0,rot:t,sub:mine.length+(mine.length>1?' parcelas':' parcela')+' · '+nfa(A)+' de '+nfa(T)+' ha',sit:sitDe(L),os:[],trava:{},base:{},
        acao:mine.some(c=>c.v.ciclo)?null:{t:'Dividir',fn:'div'}});
      mine.forEach(c=>out.push(linCult(c,'par',1,L)));
      if(livre) out.push(novo(1,t+' · área livre'));
      return; }
    if(livre){ out.push(novo(0,t)); return; }
    const vinc=L.vinc&&L.vinc.length;
    const oc=((L.vis||[])[0])||((L.fora||[])[0])||null;
    const motivo=L.semp?'Sem plantio nesta safra: para planejar, use ⋯ › Voltar a planejar na tabela.':(vinc?'Ciclo perene de outra safra: cultura, cultivar, plantio e área vêm do ciclo. Use Vincular ciclo.':('Ocupado'+(oc?' por '+oc.cult+(oc.safnome?' ('+oc.safnome+')':''):' por outra safra')+' no período desta safra.'));
    out.push({k:'ro:'+t,tipo:'ro',t,T,nivel:0,rot:t,sub:nfa(T)+' ha',motivoRo:motivo,trava:{},os:[],base:{},
      sit:L.semp?{t:'Sem plantio',c:'gray',d:motivo}:((vinc||L.sit==='Perene')?{t:'Perene · só leitura',c:'gray',d:motivo}:{t:L.sit||'Ocupado',c:SIT_COR[L.sit]||'gray',d:motivo}),
      acao:vinc?{t:'Vincular ciclo ›',fn:'vinc',arg:L.vinc[0]}:null}); });
  return out; }
// contexto das conversões (cultura, plano, data da safra) e das sugestões
function slCtx(self,saf,dados){ const so=safById(self,saf)||{v:{}}; const cs=cultsGrupo(self,saf).map(x=>x.c);
  return {culturas:Object.keys(D2.culturas||{}),planos:D2.planos.map(p=>({id:p.id,nome:p.nome,versao:p.versao,cultura:p.cultura})),cultivares:D2.cultivares||[],ini:so.v.ini,fim:so.v.fim,
    sugere:(cu,lin)=>{ const o={var:maisUsado(cs.filter(c=>c.v.cult===cu),'var')||'',plano:maisUsado(cs.filter(c=>c.v.cult===cu&&planById(c.v.plano)),'plano')||''};
      if(lin&&lin.tipo==='novo'&&lin.L){ try{ const pm=pltPmin(self,{cult:cu,var:o.var,plano:o.plano,meta:''},{sub:saf,t:lin.t,L:lin.L}); if(pm!==null&&pm!==undefined) o.plantio=ocIso(pm); }catch(e){} }
      return o; }}; }

// ---- abrir, editar, navegar e colar ----
function slTem(self,saf){ const so=safById(self,saf); return !!(so&&!so.ro); }
function slAbrir(self){ const saf=self.state.saf; if(!slTem(self,saf)){ self.setState({g2toast:'Safra encerrada: somente consulta.'}); return; }
  const lins=slLinhas(self,saf); if(!lins){ self.setState({g2toast:'Abra a etapa Cultivos e planos para editar os talhões.'}); return; }
  const vals={}, base={}; lins.forEach(l=>{ if(l.tipo==='grp'||l.tipo==='ro') return; vals[l.k]=Object.assign({},l.base); base[l.k]=Object.assign({},l.base); });
  self.__slLin=lins;   // estrutura das linhas: fixa enquanto o painel está aberto (só o rascunho muda)
  self.setState({sl:{saf,faz:safFaz(self,saf),ch:'saf-lote:'+saf+':'+Date.now()+':'+Math.random().toString(36).slice(2,8),sig:slSig(self,saf),vals,base,sel:{},ap:{},err:{},gerr:'',info:'',warn:false,ir:null}});
  // no computador o foco vai à 1ª célula editável (digitar já preenche); no celular não, para o teclado não cobrir a lista ao abrir
  if(!g2estreito()) setTimeout(()=>{ try{ const el=document.querySelector('#sl-grade [data-c]:not([disabled]):not([readonly])'); if(el){ el.focus({preventScroll:true}); if(el.select) el.select(); } }catch(e){} },60); }
function slDados(self){ const sl=self.state.sl; if(!sl) return null; const lins=(self.__slLin||[]); return {sl,lins,dados:lins.filter(l=>l.tipo!=='grp')}; }
function slSet(self,k,col,val){ const sl=self.state.sl; if(!sl) return; const lin=(self.__slLin||[]).find(l=>l.k===k); if(!lin||lin.tipo==='ro'||(lin.trava||{})[col]) return;
  const ctx=slCtx(self,sl.saf);
  // plano escolhido na célula: a mesma conferência da colagem e do "Aplicar aos marcados" (código exato e da cultura da linha)
  if((col==='plano'||col==='var')&&String(val||'')!==''){ const r=slPode(lin,col,val,ctx,(sl.vals[k]||{}).cult); if(!r.ok){ const er=Object.assign({},sl.err); er[k]=Object.assign({},er[k]||{},{[col]:r.motivo});
    self.setState({sl:Object.assign({},sl,{err:er,warn:false})}); return; } val=r.v; }
  // linha livre: "Não planejar agora" na cultura limpa a linha inteira (volta ao que era: nada a gravar)
  const vals=(lin.tipo==='novo'&&col==='cult'&&!String(val||'').trim())?Object.assign({},sl.vals,{[k]:Object.assign({},sl.base[k])}):slPor(sl.vals,lin,col,val,ctx); const er=Object.assign({},sl.err); if(er[k]){ const e=Object.assign({},er[k]); delete e[col]; if(col==='cult') delete e.plano; if(Object.keys(e).length) er[k]=e; else delete er[k]; }
  self.setState({sl:Object.assign({},sl,{vals,err:er,warn:false,info:'',gerr:Object.keys(er).length?sl.gerr:''})}); }
function slDirty(sl,lins){ return slContar(lins.filter(l=>l.tipo!=='grp'&&l.tipo!=='ro'),sl.vals,sl.base)>0; }
function slFoco(el,d){ const col=el.getAttribute('data-c'); const all=[...document.querySelectorAll('#sl-grade [data-l][data-c="'+col+'"]')].filter(x=>x.offsetParent);
  let i=all.indexOf(el); for(;;){ i+=d; if(i<0||i>=all.length) return false; const x=all[i]; if(x.disabled) continue; x.focus(); try{ if(x.select&&x.type!=='date') x.select(); }catch(e){} x.scrollIntoView({block:'nearest'}); return true; } }
function slColar(self,l0k,col,txt){ const D=slDados(self); if(!D) return; const {sl,dados}=D; const M=slTsv(txt); if(!M.length) return; const l0=dados.findIndex(l=>l.k===l0k);
  const r=slColarBloco(dados,sl.vals,Math.max(0,l0),col,M,slCtx(self,sl.saf));
  const info='Colados '+r.dim[0]+' × '+r.dim[1]+': '+r.n+(r.n===1?' célula':' células')+(r.recusas.length?'; '+slRecusasTxt(r.recusas):'')+'. Nada foi salvo ainda.';
  const er=slSemErro(sl.err,r.feitos); self.setState({sl:Object.assign({},sl,{vals:r.vals,info,warn:false,err:er,gerr:Object.keys(er).length?sl.gerr:''})}); }
function slAplicar(self){ const D=slDados(self); if(!D) return; const {sl,dados}=D; const n0=dados.filter(l=>sl.sel[l.k]).length;
  if(!n0){ self.setState({sl:Object.assign({},sl,{info:'Marque as linhas que vão receber os valores.'})}); return; }
  const r=slAplicarSel(dados,sl.vals,sl.sel,sl.ap||{},slCtx(self,sl.saf));
  if(!r.cols.length){ self.setState({sl:Object.assign({},sl,{info:'Preencha ao menos um campo da faixa "Aplicar aos marcados".'})}); return; }
  const info='Aplicado em '+r.n+(r.n===1?' célula':' células')+' de '+n0+(n0===1?' linha':' linhas')+(r.recusas.length?'; '+slRecusasTxt(r.recusas):'')+'. Nada foi salvo ainda.';
  const er=slSemErro(sl.err,r.feitos); self.setState({sl:Object.assign({},sl,{vals:r.vals,info,warn:false,err:er,gerr:Object.keys(er).length?sl.gerr:''})}); }
// sair do painel por um link (Dividir, Vincular ciclo, O.S.): com alteração, pergunta antes (o rascunho não se perde em silêncio)
function slSair(self,fn){ const D=slDados(self); if(!D) return; if(slDirty(D.sl,D.lins)){ self.setState({sl:Object.assign({},D.sl,{warn:true,ir:fn})}); return; } self.setState({sl:null}); setTimeout(fn,0); }

// ---- gravar: tudo ou nada, por fazenda ----
function slGravar(self){ const D=slDados(self); if(!D) return; const {sl,lins}=D; self.__slRec=self.__slRec||{};
  if(self.__slRec[sl.ch]){ self.setState({sl:null}); return; }   // o mesmo comando repetido (duplo clique) não grava de novo (ENG-021)
  const ed=lins.filter(l=>l.tipo!=='grp'&&l.tipo!=='ro'); const n=slContar(ed,sl.vals,sl.base);
  if(!n){ self.setState({sl:Object.assign({},sl,{info:'Nada a salvar: nenhuma célula mudou.'})}); return; }
  const saf=sl.saf; const recusa=(err,gerr)=>self.setState({sl:Object.assign({},sl,{err,gerr,warn:false})});
  if(self.state.saf!==saf){ recusa({},'A fazenda aberta mudou. Nada foi gravado; seu rascunho continua aqui.'); return; }
  // conflito: os cultivos, as marcas de sem plantio ou as O.S. desta safra mudaram depois de abrir (outra aba liberou uma ordem, por exemplo)
  if(slSig(self,saf)!==sl.sig){ recusa({},'Os talhões desta fazenda mudaram depois que você abriu o painel (cultivo, divisão ou O.S. liberada em outra aba). Nada foi gravado; seu rascunho continua aqui: feche, abra de novo e refaça só o que falta.'); return; }
  const plan0=self._plan; self._plan=null; self._ocMsg=null;
  try{
    const gid='g_cult_'+sk(saf); const rows=g2rows(self,GR(gid)); const err={}; const avisos=[]; const mudouT={};
    ed.forEach(l=>{ if(SL_COLS.some(c=>slMudou(sl.vals[l.k],sl.base[l.k],c))) mudouT[l.t]=true; });
    // trava da O.S. conferida de novo no gravar (defesa: nenhum caminho do painel muda campo travado)
    ed.forEach(l=>{ ['cult','var','plano'].forEach(c=>{ if((l.trava||{})[c]&&slMudou(sl.vals[l.k],sl.base[l.k],c)) (err[l.k]||(err[l.k]={}))[c]=l.trava[c]; }); });
    let all=g2clone(soDaSafra(rows)); let adj=JSON.parse(JSON.stringify(adjOf(self))); let nDesc=0; const salvos=[]; const novos=[]; const stamp=String(Date.now()).slice(-6);
    const draft=(l)=>{ const v=sl.vals[l.k]; const m=l.meta0||metaRascunho(v.cult,'',''); return Object.assign({},m,{cult:v.cult,var:String(v.var||'').trim(),plantio:v.plantio,meta:v.meta,plano:v.plano||''}); };
    Object.keys(mudouT).forEach(t=>{ const L=ed.filter(l=>l.t===t); if(L.some(l=>err[l.k])) return;
      const par=L.filter(l=>l.tipo==='par'||(l.tipo==='vinc'&&l.dv)), tl=L.filter(l=>l.tipo==='tal'||(l.tipo==='vinc'&&!l.dv)), nv=L.find(l=>l.tipo==='novo');
      const nvUsa=nv&&String(sl.vals[nv.k].cult||'').trim()!=='';
      if(nv&&!nvUsa&&SL_COLS.some(c=>c!=='area'&&slMudou(sl.vals[nv.k],sl.base[nv.k],c))){ err[nv.k]={cult:'Escolha a cultura para planejar '+t+' (ou limpe a linha).'}; return; }
      if(par.length){   // talhão dividido: a conferência do Dividir (soma, nomes, ocupação), com a área livre que se planeja junto
        const lst=par.map(l=>Object.assign({},l.dv,draft(l),{area:sl.vals[l.k].area}));
        if(nvUsa){ const d=draft(nv); lst.push(Object.assign({id:null,local:sugerirParcela(self,saf,nv.L,nv.area),area:String(r2(nv.area)).replace('.',','),colheita:'',adj:null,from:'',decl:true,ask:false,unm:unMetaDe(d.cult,'')},d)); }
        const r=dvConferir(self,t,lst,adj);
        if(!r.kids){ const ks=par.concat(nvUsa?[nv]:[]); Object.keys(r.err||{}).forEach(i=>{ const l=ks[Number(i)]; if(l) err[l.k]=Object.assign({},r.err[i]); });
          if(!Object.keys(r.err||{}).length||r.gerr&&!/^Corrija/.test(r.gerr)) (err[ks[0].k]||(err[ks[0].k]={})).area=r.gerr; return; }
        par.forEach(l=>{ if(String(sl.base[l.k].plano||'')!==String(sl.vals[l.k].plano||'')&&Object.keys(adjOf(self)[l.id]||{}).length) nDesc+=Object.keys(adjOf(self)[l.id]).length; });
        adj=r.adj; all=dvAplicar(all,t,r.kids,saf,r.daSaf).rest; salvos.push(t); return; }
      tl.forEach(l=>{ const v=sl.vals[l.k]; const x0=g2find(rows,l.id); if(!x0){ err[l.k]={cult:'Este cultivo não existe mais nesta safra.'}; return; }
        const d=draft(l); const e=Object.assign({},dvCampos(d),cultCheck(self,gid,rows,x0,Object.assign({},d,{local:x0.v.local,area:x0.v.area}),false,saf));
        self._metaDraft=null; self._planoAntes=null;
        if(Object.keys(e).length){ err[l.k]=e; return; } if(self._ocMsg) avisos.push(l.rot+': '+String(self._ocMsg).replace(/\.$/,'')); self._ocMsg=null;
        const x=g2find(all,l.id); const g=metaGravar(Object.assign({},d,{cult:v.cult}));
        Object.assign(x.v,{cult:d.cult,var:d.var,plantio:d.plantio,plano:d.plano,meta:g.meta}); x.v.unm=unMetaDe(x.v.cult,g.unm); if(x.v.plano) x.v.colheita='';
        if(String(x0.v.plano||'')!==String(x.v.plano||'')){ const na=Object.keys(adj[l.id]||{}).length; if(na){ nDesc+=na; delete adj[l.id]; } } salvos.push(t); });
      if(nvUsa&&!par.length){   // talhão livre: o mesmo caminho do "Planejar ›" (cultCheck de cultivo novo e pltCultivo)
        const d=Object.assign({modo:'plan',talhao:t,local:sugerirParcela(self,saf,nv.L,nv.area),area:String(r2(nv.area)).replace('.',','),colheita:''},draft(nv));
        const e=Object.assign({},dvCampos(d),cultCheck(self,gid,rows,null,d,true,saf)); self._metaDraft=null; self._planoAntes=null;
        if(Object.keys(e).length){ err[nv.k]=e; return; } if(self._ocMsg) avisos.push(t+': '+String(self._ocMsg).replace(/\.$/,'')); self._ocMsg=null;
        novos.push(pltCultivo(self,{t,faz:sl.faz,sub:saf},d,'c'+String(t).replace(/\W/g,'')+'_'+stamp+'_'+novos.length)); salvos.push(t); } });
    if(Object.keys(err).length){ const nt=[...new Set(Object.keys(err).map(k=>(lins.find(l=>l.k===k)||{}).t))].length;
      recusa(err,nt+(nt>1?' talhões precisam':' talhão precisa')+' de correção nas células destacadas. Nada foi gravado; o que você digitou foi mantido.'); return; }
    novos.forEach(c=>all.push(c));
    const norm=normCult(all); const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); norm.forEach(y=>{ if(y.grp&&x0[y.id]!==false) x0[y.id]=true; });
    const g2all=Object.assign({},self.state.g2||{}); g2all[gid]=Object.assign({},st,{rows:norm,x:x0,fl:null});
    const ts=[...new Set(salvos)];
    self.__slRec[sl.ch]={n,ts};
    self.setState({g2:g2all,adj,sl:null,g2toast:sl.faz+': '+ts.length+(ts.length>1?' talhões salvos':' talhão salvo')+' ('+n+(n>1?' alterações':' alteração')+': '+ts.join(', ')+')'
      +(nDesc?' · '+nDesc+(nDesc>1?' ajustes de dose descartados pela troca de plano':' ajuste de dose descartado pela troca de plano'):'')+'. Plano operacional, recursos e demanda recalculados.'+(avisos.length?' Confira: '+avisos.join('; ')+'.':'')});
  }catch(e){ recusa({},'Não foi possível salvar ('+String((e&&e.message)||e).slice(0,140)+'). Nada foi gravado; seu rascunho continua aqui.'); }
  finally{ self._plan=plan0; self._metaDraft=null; self._planoAntes=null; self._ocMsg=null; } }

// ---- valores da tela ----
function slVals(self,v,saf,step,ro){ const multi=sgSubs(self,saf).length>1;
  // "Editar talhões…" no título do bloco com uma fazenda só; com várias, cada faixa de fazenda da tabela tem o seu "Editar talhões ›"
  // (filtrada uma fazenda, a faixa dela continua à vista: sem cópia da ação)
  v.sl_tem=!!saf&&step===2&&!ro&&!multi; v.sl_abrir=()=>slAbrir(self);
  v.slfaz=(sub)=>sgNaFazenda(self,sub,()=>slAbrir(self));
  const sl=self.state.sl; v.sl_open=!!sl&&step===2; if(!v.sl_open){ v.sl_lins=[]; return; }
  const lins=self.__slLin||[]; const ctx=slCtx(self,sl.saf); const ed=lins.filter(l=>l.tipo!=='grp'&&l.tipo!=='ro'); const dados=lins.filter(l=>l.tipo!=='grp');
  const n=slContar(ed,sl.vals,sl.base); const so=safById(self,sl.saf)||{v:{}};
  v.sl_titulo='Editar talhões da '+sl.faz; v.sl_sub=so.v.nome+' · '+sl.faz;
  // resumo: área total dos talhões, a planejada nesta safra (com o rascunho), a livre e o selo
  const T=talTot(sl.faz); let A=0; lins.forEach(l=>{ if(l.tipo==='par'||l.tipo==='tal'||l.tipo==='vinc') A+=g2num(sl.vals[l.k].area)||0; else if(l.tipo==='novo'&&String(sl.vals[l.k].cult||'').trim()) A+=l.area; });
  const nT=new Set(lins.map(l=>l.t)).size; const nPl=new Set(lins.filter(l=>(l.tipo==='par'||l.tipo==='tal'||l.tipo==='vinc')||(l.tipo==='novo'&&String(sl.vals[l.k].cult||'').trim())).map(l=>l.t)).size;
  const livre=lins.filter(l=>l.tipo==='novo'&&!String(sl.vals[l.k].cult||'').trim()).reduce((a,l)=>a+l.area,0);
  v.sl_n=nT+(nT>1?' talhões':' talhão'); v.sl_resumo='Área '+nfa(T)+' ha · planejada '+nfa(r2(A))+' ha · livre '+nfa(r2(livre))+' ha · '+nPl+' de '+nT+' planejados';
  const nerr=Object.keys(sl.err||{}).length; const sel=(nerr||sl.gerr)?['A corrigir','#B42318','#FDE8E6']:(n?[n+(n>1?' alterações':' alteração')+' não salvas','#8A5A00','#FFF4D6']:['Tudo salvo','#1E7A4C','#E4F3E9']);
  v.sl_selo=sel[0]; v.sl_selost='display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+sel[1]+';background:'+sel[2]+';';
  v.sl_gerr=sl.gerr||''; v.sl_hasg=!!sl.gerr; v.sl_info=sl.info||''; v.sl_hasinfo=!!sl.info; v.sl_warn=!!sl.warn;
  v.sl_salvarT='Salvar alterações ('+n+')'; v.sl_salvarSt=n?'':'opacity:.55;cursor:not-allowed;'; v.sl_salvarDis=n?'false':'true';
  // faixa "Aplicar aos marcados": os mesmos campos da linha, uma vez
  const ap=sl.ap||{}; const nSel=dados.filter(l=>sl.sel[l.k]).length; const setAp=(c)=>(e)=>{ const cur=self.state.sl; const a=Object.assign({},cur.ap||{},{[c]:e.target.value});
    if(c==='cult'){ if(a.plano&&slCultDoPlano(a.plano,ctx)!==a.cult) a.plano=''; const vc=a.var&&(ctx.cultivares||[]).find(x=>slSemAc(x[1])===slSemAc(a.var)); if(a.cult&&vc&&vc[0]!==a.cult) a.var=''; } self.setState({sl:Object.assign({},cur,{ap:a,info:''})}); };
  v.sl_apN=nSel; v.sl_apVazio=nSel?'false':'true'; v.sl_apSub=nSel?(nSel+(nSel===1?' linha marcada':' linhas marcadas')):'marque as linhas'; v.sl_apT='Aplicar a '+nSel+(nSel===1?' marcado':' marcados'); v.sl_apSt=nSel?'':'opacity:.55;';
  v.sl_apCults=[{v:'',t:'Cultura…'}].concat(ctx.culturas.map(c=>({v:c,t:c}))); v.sl_apCult=ap.cult||''; v.sl_apSetCult=setAp('cult');
  v.sl_apVar=ap.var||''; v.sl_apSetVar=setAp('var'); v.sl_apDl='sl-dl-'+Math.max(0,ctx.culturas.indexOf(ap.cult||''));
  v.sl_apPlantio=ap.plantio||''; v.sl_apSetPlantio=setAp('plantio'); v.sl_apMeta=ap.meta||''; v.sl_apSetMeta=setAp('meta');
  v.sl_apUn=ap.cult?metaRascunho(ap.cult,'','')._un:''; v.sl_apPlanos=[{v:'',t:'Plano…'}].concat(D2.planos.filter(p=>!ap.cult||p.cultura===ap.cult).map(p=>({v:p.id,t:p.nome+' v'+p.versao+(ap.cult?'':' · '+p.cultura)})));
  v.sl_apPlano=ap.plano||''; v.sl_apSetPlano=setAp('plano'); v.sl_aplicar=()=>slAplicar(self);
  const selaveis=dados.filter(l=>l.tipo!=='ro'); v.sl_todas=selaveis.length>0&&selaveis.every(l=>sl.sel[l.k]);
  v.sl_togTodas=()=>{ const cur=self.state.sl; const on=!selaveis.every(l=>cur.sel[l.k]); const s={}; if(on) selaveis.forEach(l=>{ s[l.k]=true; }); self.setState({sl:Object.assign({},cur,{sel:s})}); };
  v.sl_dl=ctx.culturas.map((c,i)=>({id:'sl-dl-'+i,ops:[...new Set((ctx.cultivares||[]).filter(x=>x[0]===c).map(x=>x[1]).concat(cultsGrupo(self,sl.saf).map(x=>x.c).filter(x=>x.v.cult===c).map(x=>x.v.var)))].filter(Boolean).map(t=>({t}))}));
  // linhas
  const CULT=ctx.culturas; const E=sl.err||{};
  v.sl_lins=lins.map((l,i)=>{ const o={i,k:l.k,grp:l.tipo==='grp',ro:l.tipo==='ro',ed:l.tipo!=='grp'&&l.tipo!=='ro',rot:l.rot,sub:l.sub,
      lst:'padding-left:'+(l.nivel?22:0)+'px;',sit:l.sit.t,sitDica:l.sit.d||l.sit.t,sitSt:'display:inline-flex;align-items:center;max-width:100%;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:'+(G2C[l.sit.c]||G2C.gray)[0]+';background:'+(G2C[l.sit.c]||G2C.gray)[1]+';'};
    o.temOs=!!(l.os&&l.os.length); o.osT=o.temOs?l.os[0].id+' ›':''; o.osAl=o.temOs?'Abrir a '+l.os[0].id+' na Ordem de Serviço':''; o.osGo=()=>{ if(o.temOs) slSair(self,()=>{ location.href='OS.dc.html#'+l.os[0].id; }); };
    o.temAc=!!l.acao; o.acT=l.acao?(l.acao.fn==='div'?'Dividir '+l.t:l.acao.t):''; o.acAl=o.acT;
    o.acGo=()=>{ if(!l.acao) return; if(l.acao.fn==='div') slSair(self,()=>openDiv(self,l.t)); else if(l.acao.fn==='vinc') slSair(self,()=>abrirVincular(self,l.t,l.acao.arg)); };
    if(!o.ed){ o.motivo=l.motivoRo||''; o.motivoSep=o.motivo?' · ':''; return o; }
    const vv=sl.vals[l.k]||{}, bb=sl.base[l.k]||{}, e=E[l.k]||{};
    o.sel=!!sl.sel[l.k]; o.selAl='Marcar '+l.rot; o.lnSt=o.sel?'background:#F2F8F4;':''; o.tog=()=>{ const cur=self.state.sl; const s=Object.assign({},cur.sel); if(s[l.k]) delete s[l.k]; else s[l.k]=true; self.setState({sl:Object.assign({},cur,{sel:s})}); };
    SL_COLS.forEach(c=>{ const tr=(l.trava||{})[c]||''; const mud=slMudou(vv,bb,c); o[c]=String(vv[c]==null?'':vv[c]); o['ro_'+c]=!!tr; o['tt_'+c]=tr||(e[c]||'');
      o['al_'+c]=SL_ROT[c]+' de '+l.rot+(c==='area'||c==='meta'?'':'')+(tr?' (só leitura)':''); o['s_'+c]=(ev)=>slSet(self,l.k,c,ev.target.value);
      o['st_'+c]='font-family:inherit;font-size:13px;padding:6px 8px;border-radius:8px;box-sizing:border-box;width:100%;min-width:0;color:'+(tr?'#5B6660':'#15201A')+';border:1px solid '+(e[c]?'#B42318':(mud?'#8A5A00':'#E4E9E5'))+';background:'+(tr?'#F4F6F3':(e[c]?'#FDE8E6':(mud?'#FFF8E6':'#FFFFFF')))+';'+(c==='area'||c==='meta'?'text-align:right;':'')+(c==='area'&&tr?'font-weight:700;':''); });
    o.oc=((l.tipo==='novo')?[{v:'',t:vv.cult?'Não planejar agora':'Cultura…'}]:(vv.cult?[]:[{v:'',t:'Cultura…'}])).concat(CULT.map(x=>({v:x,t:x}))); o.op=planOpts({cult:vv.cult,plano:vv.plano}); o.dl='sl-dl-'+Math.max(0,CULT.indexOf(vv.cult||''));
    o.unm=vv.cult?(l.meta0?metaUnTela(Object.assign({},l.meta0,{cult:vv.cult,meta:vv.meta})):metaRascunho(vv.cult,'','')._un):'—';
    const errs=Object.keys(e).map(c=>(SL_ROT[c]?SL_ROT[c]+': ':'')+e[c]); o.hasErr=errs.length>0; o.errMsg=l.rot+' · '+errs.join(' · ');
    return o; });
  const fechar=()=>{ const cur=self.state.sl; if(cur&&slDirty(cur,lins)){ self.setState({sl:Object.assign({},cur,{warn:true,ir:null})}); return; } self.setState({sl:null}); };
  v.sl_close=fechar; v.sl_discard=()=>{ const ir=(self.state.sl||{}).ir; self.setState({sl:null,g2toast:'Alterações descartadas'}); if(ir) setTimeout(ir,0); };
  v.sl_keep=()=>self.setState({sl:Object.assign({},self.state.sl,{warn:false,ir:null})});
  v.sl_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); fechar(); } };
  v.sl_salvar=()=>slGravar(self);
  // planilha: Enter ou ↓ desce, Shift+Enter ou ↑ sobe na mesma coluna (Tab e Shift+Tab andam nas colunas, como no navegador)
  v.sl_nav=(e)=>{ const t=e&&e.target; if(!t||!t.getAttribute||t.getAttribute('data-l')===null) return; const k=e.key; let d=0;
    if(k==='Enter') d=e.shiftKey?-1:1; else if((k==='ArrowDown'||k==='ArrowUp')&&!e.altKey) d=k==='ArrowDown'?1:-1;
    if(!d) return; e.preventDefault(); slFoco(t,d); };
  // colar do Excel/Planilhas a partir da célula focada: bloco (tabulação ou quebra de linha) e também um valor só em lista, data, número ou
  // célula travada passam pela conferência (o resumo diz o que entrou e o que foi recusado); texto solto na variedade cola como sempre
  v.sl_colar=(e)=>{ const t=e&&e.target; if(!t||!t.getAttribute||t.getAttribute('data-l')===null) return; let txt=''; try{ txt=(e.clipboardData||window.clipboardData).getData('text/plain')||''; }catch(er){ txt=''; }
    const bloco=/[\t\n\r]/.test(String(txt).replace(/[\r\n]+$/,'')); const col=t.getAttribute('data-c');
    if(!bloco&&!(t.tagName==='SELECT'||t.readOnly||t.disabled||col==='area'||col==='meta'||col==='plantio')) return;
    e.preventDefault(); slColar(self,t.getAttribute('data-l'),col,txt); }; }
