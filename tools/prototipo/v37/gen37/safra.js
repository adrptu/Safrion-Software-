// ===== Processo · Planejar safra (6 etapas numa só tela de trabalho) =====
const SAFKEYS={S2627:1,S27SF:1,S2526:1,LG2627:1};
function GR(id){ return GRIDS.find(g=>g.id===id); }
function sk(s){ return SAFKEYS[s]?s:'NOVA'; }
function planById(id){ return D2.planos.find(p=>p.id===id)||null; }
// Opções do campo Plano agronômico no formulário do cultivo: planos publicados da cultura do formulário; o plano atual de
// outra cultura continua visível, marcado como incompatível, para o usuário trocar.
function planOpts(d){ const cult=String(d.cult||''); const cur=planById(String(d.plano||''));
  const out=[{v:'',t:'Sem plano'}].concat(D2.planos.filter(p=>p.cultura===cult).map(p=>({v:p.id,t:p.nome+' v'+p.versao+' · '+p.atividades.length+' atividades'})));
  if(cur&&cur.cultura!==cult) out.push({v:cur.id,t:cur.nome+' v'+cur.versao+' · plano de '+cur.cultura+', incompatível'});
  return out; }
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function rs(n){ return 'R$ '+nf(n,2); }
function iso(d){ return d.toISOString().slice(0,10); }
function addDays(s,n){ const d=new Date(s+'T12:00:00'); d.setDate(d.getDate()+n); return iso(d); }
function br(s){ if(!s) return '—'; const a=s.split('-'); return a[2]+'/'+a[1]+'/'+a[0]; }
function prodNome(p,c){ if(p.indexOf('variedade do cultivo')>=0||p.indexOf('híbrido do cultivo')>=0){ return p.split(' · ')[0]+' '+String(c.v.var||'').replace('Híbrido ',''); } return p; }
function colheitaDe(c,pl){ if(c.v.colheita) return c.v.colheita; const ca=pl.atividades.find(a=>a.op.indexOf('Colheita')===0);
  if(ca&&ca.g.tipo==='DAP') return addDays(c.v.plantio,ca.g.dias); if(ca&&ca.g.tipo==='DATA') return ca.g.data; return c.v.plantio; }
function dataAtv(c,a,pl){ const g=a.g; if(g.tipo==='DAP') return addDays(c.v.plantio,g.dias); if(g.tipo==='DATA') return g.data;
  const col=colheitaDe(c,pl); return addDays(col, g.tipo==='DAPC'? g.dias : -g.dias); }
function gatLabel(g){ if(g.tipo==='DAP') return 'DAP '+(g.dias>0?'+':(g.dias<0?'−':''))+Math.abs(g.dias); if(g.tipo==='DATA') return br(g.data); if(g.tipo==='DAPC') return g.dias+' dias após a colheita'; return g.dias+' dias antes da colheita'; }
function gatOrder(g){ if(g.tipo==='DATA') return g.data; return g.tipo==='DANC'? -g.dias : g.dias; }
function grupoGat(t){ return t==='DAP'?'DAP':(t==='DATA'?'DATA':'DAC'); }
const GLABEL={DAP:'DAP · dias após o plantio',DAC:'DAC · dias em relação à colheita (antes/depois explícito)',DATA:'Data do calendário'};
function mesIdx(s){ return D2.meses.findIndex(m=>m[0]===String(s).slice(0,7)); }
// rendimentos: uma grade por safra (g_rend_S2627, g_rend_S27SF, g_rend_S2526, g_rend_NOVA)
function rendGid(saf){ return 'g_rend_'+sk(saf); }
// >>> REPARTIR (REND-MULTICONJUNTOS-20261003) · funções puras, sem tela; espelho em dados2.repartir; teste rend_multiconjuntos_unit.py
// Uma ocorrência (cultivo × atividade) com área Q (ha) dividida entre configurações (conjuntos). Cada configuração c:
//   rend ha/h: ausente, zero ou inválido não divide área (fica pendente com motivo, nunca vira 0 h)
//   part % fixo da área (vazio = divide pelo rendimento, partindo das mesmas horas) · jan prazo em h, contado do início da ocorrência (vazio = sem limite; 0 = sem capacidade)
//   custo_h R$/h (vazio = tarifa desconhecida, nunca R$ 0) · diesel L/h (vazio = não informado) · pess pessoas (horas-homem = h × pessoas)
//   seq true = divide trator, implemento ou operador com as outras marcadas · troca h para entrar depois de outra da mesma sequência
//   ativos ids do cadastro (o mesmo id em duas = sequência) · rec unidades por grupo de recursos; pools = quantas a fazenda tem de cada grupo
// 1) Antes de dividir a área, junta quem trabalha em sequência (mesmo ativo, sequência declarada ou grupo de recursos da fazenda que não
//    cobre todas ao mesmo tempo). Em sequência, cada uma termina dentro da própria janela (prazo do início da ocorrência; a janela maior de
//    outra não amplia a dela, D-01); começa a de menor troca e cada outra entra com a sua troca. PRD 44.3: a capacidade vale depois de
//    respeitar simultaneidade e conflitos.
// 2) Atribuição: % fixos primeiro (o que passa da janela fica sem conjunto); o resto vai às sem % na proporção do rendimento, terminando
//    juntas (as mesmas horas); cada uma para na própria janela e a sequência para quando a soma das horas dela com as trocas enche a
//    janela; o que não cabe fica sem conjunto. Σ q + sem conjunto = Q, sem negativos.
// Grandezas separadas: horas-conjunto = Σ q/r (produtivas); decorrido = maior soma entre os grupos que trabalham ao mesmo tempo (quem
// divide recurso trabalha em sequência, com a troca); custo, diesel e horas-homem seguem as horas de cada configuração. Sem arredondar.
// Pendente (nada atribuído) diz a causa: sem conjunto, sem rendimento, sem horas na janela ou partes fixas abaixo de 100 %.
// 3) REND-RETORNO-1818 (S5): três grandezas separadas, nenhuma cortada pela outra. PLANO = a demanda inteira pela partilha do usuário,
//    sem janela (parte fixa inteira; resto pelo rendimento, terminando juntas): dele saem a necessidade da sequência e o déficit (conflito).
//    ATENDIDO = o que cabe nas janelas (passo 2). SALDO = área sem conjunto + horas que faltam, pelas premissas do plano (parte fixa: o que
//    faltou dela na própria configuração; resto: pelo rendimento entre as sem %), sem nova troca, local ou jornada. nec = atendido + saldo,
//    em ha e em horas-conjunto. A parte fixa é a intenção para a demanda inteira; na janela vale como teto (cada uma faz até a própria parte,
//    limitada pela própria janela; a sequência reduz todas na mesma fração). Não prioriza a configuração mais rápida.
function rpNum(x){ if(x===null||x===undefined) return null; if(typeof x==='number') return isFinite(x)?x:NaN;
  const t=String(x).trim().replace(',','.'); if(t==='') return null; if(!/^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$/.test(t)) return NaN; const n=Number(t); return isFinite(n)?n:NaN; }   // igual a dados2._rp_num
function rpF(n){ return String(Math.round(Number(n)*100)/100).replace('.',','); }
function rendCalc(larg,vel,efic){ return (Number(larg)||0)*(Number(vel)||0)/10*(Number(efic)||0)/100; }   // ha/h = m × km/h ÷ 10 × eficiência
function repartir(Q,cfgs,pools){ const mot=[], motS=new Set(); const add=(m)=>{ if(!motS.has(m)){ motS.add(m); mot.push(m); } };
  Q=rpNum(Q); if(Q===null||isNaN(Q)||Q<0){ add('área inválida'); Q=0; }
  const PV=Object.keys(pools||{}).map(k=>[k,pools[k]||{},rpNum((pools[k]||{}).un)]).filter(z=>z[2]!==null&&!isNaN(z[2])&&z[2]>=0);   // grupos com unidades válidas
  const it=(cfgs||[]).map((c,i)=>{ const r=rpNum(c.rend), p=rpNum(c.part), H=rpNum(c.jan), ch=rpNum(c.custo_h), d=rpNum(c.diesel), tr=rpNum(c.troca), pe=rpNum(c.pess);
    const x={i,id:c.id,nome:c.nome||('Configuração '+(i+1)),r:(r!==null&&r>0)?r:null,p:(p!==null&&p>=0)?p:null,H:(H===null||isNaN(H)||H<0)?Infinity:H,
      ch:(ch!==null&&ch>=0)?ch:null,d:(d!==null&&d>=0)?d:null,troca:(tr!==null&&tr>0)?tr:0,pess:(pe!==null&&pe>0)?pe:0,seq:!!c.seq,
      ativos:(c.ativos||[]).filter(Boolean),rec:c.rec||{},t:0,q:0,h:0,ht:0,custo:null,diesel:null,emSeq:false,seqEst:false,grupo:i};
    if(H!==null&&(isNaN(H)||H<0)) add(x.nome+': janela inválida, considerada sem limite');
    x.Hin=x.H; const fr=PV.find(z=>{ const u=rpNum(x.rec[z[0]])||0; return u>0&&u>z[2]+1e-9; });   // sozinha precisa de mais unidades que a fazenda tem: não trabalha (PRE-REV)
    if(fr){ x.H=0; x.semRec=true; add(x.nome+': precisa de '+rpF(rpNum(x.rec[fr[0]]))+' em '+(fr[1].nome||fr[0])+', a fazenda tem '+rpF(fr[2])+'; não trabalha nesta ocorrência'); }
    return x; });
  const fx=it.filter(x=>x.p!==null); const sp=fx.reduce((a,x)=>a+x.p,0); const esc=sp>100?100/sp:1;
  if(sp>100+1e-9) add('partes fixas somam '+rpF(sp)+' %: reduzidas na proporção para fechar 100 %');
  let R=Q; fx.forEach(x=>{ x.t=Q*x.p*esc/100; R-=x.t; }); if(R<=1e-9*Math.max(1,Q)) R=0;   // tolerância relativa à área (PRE-REV R3)
  const livres=it.filter(x=>x.p===null); const livOk=livres.length>0&&!livres.some(x=>x.r===null);
  // 1) No plano: rendimento válido e parte > 0 (sem % só as que entram na divisão pelo rendimento); recebem área: janela > 0.
  //    Fecho de quem trabalha em sequência (mesmo ativo, sequência declarada, grupo de recursos que não cobre todas ao mesmo tempo): dá o
  //    decorrido e a simultaneidade. Janela (PRE-REV): uma restrição por recurso físico (a sequência declarada, cada ativo do cadastro e cada
  //    grupo de recursos que serializa) com a maior janela dos SEUS membros, mais os cortes por prazo dos grupos que se excluem (D-01,
  //    abaixo); todas valem ao mesmo tempo. Janela 0 não recebe área nem divide janela, mas a sequência continua precisando das horas dela no plano (R1). A troca
  //    reservada é a que o decorrido cobra: a de cada membro, menos a menor troca do fecho se um membro a tem (sem depender da ordem).
  //    Grupo de recursos: serializa quando o maior conjunto de usuários que podem trabalhar juntos (fora da mesma sequência declarada e sem
  //    ativo em comum) precisaria de mais unidades que a fazenda tem; decidido no plano (com janela 0) e na divisão (só com horas).
  // sem % que entram no plano e no saldo: as que têm horas (janela > 0); se nenhuma tem, todas (premissa: com janela)
  const livH=livres.filter(x=>x.H>0); const planLiv=livH.length?livH:livres;
  const candP=it.filter(x=>x.r!==null&&(x.p!==null?x.t>1e-12:(livOk&&R>0&&planLiv.indexOf(x)>=0))); const cand=candP.filter(x=>x.H>0);
  const uf=()=>{ const pai=it.map((_,i)=>i); const raiz=(i)=>{ while(pai[i]!==i){ pai[i]=pai[pai[i]]; i=pai[i]; } return i; };
    return {raiz,une:(a,b)=>{ a=raiz(a); b=raiz(b); if(a!==b) pai[Math.max(a,b)]=Math.min(a,b); }}; };
  const U=uf(), UP=uf(); const raiz=U.raiz;   // U: quem recebe área; UP: o plano
  [[cand,U],[candP,UP]].forEach(([xs,V])=>{ xs.forEach((x,a)=>xs.slice(a+1).forEach(y=>{ if(x.ativos.some(z=>y.ativos.indexOf(z)>=0)) V.une(x.i,y.i); }));
    const sq=xs.filter(x=>x.seq); sq.forEach(x=>V.une(sq[0].i,x.i)); });
  if(cand.some((x,a)=>cand.slice(a+1).some(y=>x.ativos.some(z=>y.ativos.indexOf(z)>=0)))) add('configurações com a mesma máquina do cadastro trabalham em sequência');
  if(cand.filter(x=>x.seq).length>1) add('sequência declarada: dividem trator, implemento ou operador');
  const RS=[]; const sqP=candP.filter(x=>x.seq); if(sqP.length>1) RS.push(['sq',sqP,sqP.filter(x=>x.H>0)]);
  const ats=[]; candP.forEach(x=>x.ativos.forEach(z=>{ if(ats.indexOf(z)<0) ats.push(z); }));
  ats.forEach(z=>{ const xs=candP.filter(x=>x.ativos.indexOf(z)>=0); if(xs.length>1) RS.push(['at:'+z,xs,xs.filter(x=>x.H>0)]); });
  const um=PV.filter(z=>z[2]<=1).map(z=>z[0]); const SERp=[], SERa=[];   // grupo de 1 unidade: uma máquina só; SERp/SERa: grupos de 2+ que serializam no plano / na divisão (W2)
  const junto=(x,y,fora)=>(x.seq&&y.seq)||x.ativos.some(z=>y.ativos.indexOf(z)>=0)||um.some(k=>k!==fora&&(rpNum(x.rec[k])||0)>0&&(rpNum(y.rec[k])||0)>0);   // nunca ao mesmo tempo (fora: o grupo cujo pico se mede, B5a)
  // maior uso simultâneo do grupo k entre quem pode trabalhar junto: conjunto independente de peso máximo do grafo "junto", por componente
  //    (quem é independente soma), busca exata com cota por cobertura de cliques (W3). pare=true para assim que passa de un (só importa se
  //    passa). Teto de 65 536 passos por componente: acima disso conta a soma do componente (conservador: serializa) e devolve o estouro,
  //    para o motivo não afirmar um pico que não conferiu. Devolve [valor, estouro].
  const simul=(us,k,un,pare)=>{ const W0=us.map(x=>rpNum(x.rec[k])||0), n=us.length; const tot=W0.reduce((a,b)=>a+b,0); if(tot<=un+1e-9) return [tot,false];
    const J=us.map((x,a)=>us.map((y,b)=>a!==b&&junto(x,y,k))); const vis=us.map(()=>false); let soma=0, est=false;
    const cota=(P)=>{ let ub=0; const r=P.slice(); while(r.length){ const c=[r.shift()]; for(let j=0;j<r.length;){ if(c.every(u=>J[u][r[j]])){ c.push(r[j]); r.splice(j,1); } else j++; } ub+=W0[c[0]]; } return ub; };   // P em peso decrescente: o 1º de cada clique é o maior
    for(let s0=0;s0<n;s0++){ if(vis[s0]) continue; const cp=[]; const pl0=[s0]; vis[s0]=true; while(pl0.length){ const a=pl0.pop(); cp.push(a); for(let b=0;b<n;b++) if(!vis[b]&&J[a][b]){ vis[b]=true; pl0.push(b); } }
      cp.sort((a,b)=>(W0[b]-W0[a])||(a-b)); let best=0, passos=0, estouro=false, passou=false;
      const vai=(P,s)=>{ if(++passos>65536){ estouro=true; return; } if(s>best) best=s; if(pare&&soma+best>un+1e-9){ passou=true; return; }
        if(!P.length||s+cota(P)<=best) return; const v=P[0];
        vai(P.filter(u=>u!==v&&!J[v][u]),s+W0[v]); if(estouro||passou) return; vai(P.slice(1),s); };
      vai(cp,0); if(estouro){ est=true; soma+=cp.reduce((a,i)=>a+W0[i],0); } else soma+=best;
      if(pare&&soma>un+1e-9) return [soma,est]; }
    return [soma,est]; };
  Object.keys(pools||{}).forEach(k=>{ const pv=pools[k]||{}; const un=rpNum(pv.un); if(un===null||isNaN(un)||un<0) return;
    const uP=candP.filter(x=>!x.semRec&&(rpNum(x.rec[k])||0)>0), uA=uP.filter(x=>x.H>0);   // quem não trabalha por falta de recurso já tem o motivo
    const [sA,eA]=uA.length>1?simul(uA,k,un,true):[0,false], [sP,eP]=uP.length>1?simul(uP,k,un,true):[0,false];
    const ea=uA.length>1&&(un<=1||sA>un+1e-9), ep=uP.length>1&&(un<=1||sP>un+1e-9);   // 1 unidade: uma máquina só, como um ativo do cadastro
    if(ea) uA.forEach(x=>U.une(uA[0].i,x.i)); if(ep) uP.forEach(x=>UP.une(uP[0].i,x.i));
    if(ea||ep){ RS.push(['pl:'+k,ep?uP:[],ea?uA:[]]); if(!(un<=1)){ if(ep&&SERp.indexOf(k)<0) SERp.push(k); if(ea&&SERa.indexOf(k)<0) SERa.push(k); }
      const [sm,es]=simul(ea?uA:uP,k,un,false); const dp=ea?(sA>un+1e-9&&!eA):(sP>un+1e-9&&!eP);   // dp: a decisão achou mais do que un sem estourar
      add((pv.nome||k)+(es?(dp?': ao mesmo tempo precisariam de mais do que as '+rpF(un)+' da fazenda; configurações consideradas em sequência nesta estimativa':': combinações demais para conferir quantas trabalham ao mesmo tempo; configurações consideradas em sequência nesta estimativa (conservador)')
        :(sm>un+1e-9?': ao mesmo tempo precisariam de '+rpF(sm)+', a fazenda tem '+rpF(un)+((un<=1||(ea?uA:uP).every((x,a,l)=>l.slice(a+1).every(y=>(rpNum(x.rec[k])||0)+(rpNum(y.rec[k])||0)>un+1e-9)))?'; trabalham uma de cada vez':'; configurações consideradas em sequência nesta estimativa'):': a fazenda tem '+rpF(un)+'; quem a usa divide a janela dela'))); } });
  // grupo inteiro de quem se exclui duas a duas (clique maximal do grafo "nunca ao mesmo tempo": sequência, ativo, grupo de 1 unidade ou que
  // serializa), com a janela temporal da ocorrência (D-01, 5983640246): cada janela é um prazo contado do início comum; para cada prazo finito t
  // do grupo, quem tem janela ≤ t cabe em t (cortes por prazo, a condição EDF de um recurso). Um membro de prazo maior ou sem janela não amplia
  // a disponibilidade dos outros; sem enumerar subconjuntos: os cortes de cada clique maximal cobrem todo subgrupo. Em grafo perfeito (sem buraco ímpar de 5+ vértices no grafo nem
  // no complemento: cordal, ciclo de 4, trator × implemento) as cliques bastam (W1). O teste olha só quem tem janela finita: quem não tem
  // prazo vai por último e não muda a viabilidade das outras (R2-2). Nos outros (ex.: ciclo de 5) o componente inteiro faz os cortes por
  // prazo com todos os membros (conservador, com motivo). Cliques demais (> 4 096), cortes demais (> 8 192) ou busca acima do teto: só esse
  // componente fica no conservador (R2-1), com motivo, e a viabilidade não é declarada exata (W4, D-01). No plano (com janela 0) e na divisão (só com horas), cada um com o seu grafo e a sua lista de grupos que serializam (W2).
  const exclui=(x,y,S)=>junto(x,y)||S.some(k=>(rpNum(x.rec[k])||0)>0&&(rpNum(y.rec[k])||0)>0);
  // ciclo induzido com número ímpar (5+) de vértices em cs (adjacência A): true, false ou null (passou do teto, não conferiu)
  const buraco=(cs,A)=>{ let passos=0;
    const ext=(c,v0)=>{ if(++passos>65536) return null; const u=c[c.length-1];
      for(const w of cs){ if(w<=v0||!A[u][w]||c.indexOf(w)>=0) continue; let corda=false; for(let i=1;i<c.length-1;i++) if(A[c[i]][w]){ corda=true; break; } if(corda) continue;
        if(c.length>1&&A[v0][w]){ if(c.length>=4&&c.length%2===0) return true; continue; }   // fecha o ciclo c + w (c.length + 1 vértices)
        c.push(w); const r=ext(c,v0); c.pop(); if(r!==false) return r; }
      return false; };
    for(const v0 of cs){ const r=ext([v0],v0); if(r!==false) return r; } return false; };
  const grafo=(V,pref,S)=>{ const n=V.length; if(n<2) return; const adj=V.map((x,a)=>V.map((y,b)=>a!==b&&exclui(x,y,S))); const cl=[], fc=[];
    // cortes por prazo de um grupo (D-01): um por conjunto de membros e prazo, sem repetir; sub: o corte não pega o grupo inteiro (prazo menor)
    const cortes=(xs,tipo,out,visto)=>{ const ts=xs.map(x=>x.H).filter(h=>isFinite(h)).filter((h,i,a)=>a.indexOf(h)===i).sort((a,b)=>a-b);
      ts.forEach(t=>{ const st=xs.filter(x=>x.H<=t); if(st.length<2) return; const k=pref+tipo+':'+st.map(x=>x.i).join(',')+'@'+t; if(visto[k]) return; visto[k]=1; out.push([k,st,t,st.length<xs.length]); }); };
    const vis=V.map(()=>false); for(let s0=0;s0<n;s0++){ if(vis[s0]) continue; const comp=[]; const pilha=[s0]; vis[s0]=true;
      while(pilha.length){ const a=pilha.pop(); comp.push(a); for(let b=0;b<n;b++) if(adj[a][b]&&!vis[b]){ vis[b]=true; pilha.push(b); } } comp.sort((a,b)=>a-b);
      if(comp.length<2) continue; const cc=[]; let passos=0, est=false;
      const bk=(R,P,X)=>{ if(est) return; if(++passos>65536||cc.length>4096){ est=true; return; } if(!P.length&&!X.length){ if(R.length>1) cc.push(R.slice().sort((a,b)=>a-b)); return; } const u=P.concat(X)[0];
        for(const v of P.filter(v=>!adj[u][v])){ bk(R.concat([v]),P.filter(w=>adj[v][w]),X.filter(w=>adj[v][w])); if(est) return; P=P.filter(w=>w!==v); X=X.concat([v]); } };
      bk([],comp.slice(),[]);
      if(!est){ const nc=[], v0={}; for(const c of cc){ cortes(c.map(i=>V[i]),'cq',nc,v0); if(nc.length>8192){ est=true; break; } } }   // teto de cortes deste componente
      let imp=est;
      if(!est){ cc.forEach(c=>cl.push(c)); const cf0=comp.filter(i=>isFinite(V[i].H));
        // R3-1: com 2+ prazos distintos, os cortes por clique só bastam se quem tem prazo se exclui todo entre si (um recurso: EDF); senão,
        // conservador do componente (P4 de trator × implemento com prazos diferentes aceitava plano inviável)
        const fin=cf0.filter(i=>V[i].H>0), dl=fin.map(i=>V[i].H).filter((h,k,a)=>a.indexOf(h)===k), cliq=fin.every((a,k)=>fin.slice(k+1).every(b=>adj[a][b]));
        // P4 induzido entre quem tem prazo (a-b-c-d sem a-c, b-d, a-d): o contraexemplo de trator × implemento; sem P4 (P3, estrela) os cortes bastam
        const p4=()=>fin.some(b=>fin.some(c=>c!==b&&adj[b][c]&&fin.some(a=>a!==c&&adj[a][b]&&!adj[a][c]&&fin.some(d=>d!==b&&d!==a&&adj[c][d]&&!adj[b][d]&&!adj[a][d]))));
        if(!cliq&&dl.length>1&&p4()){ imp=true; add('prazos diferentes em recursos compartilhados: as configurações ligadas são consideradas juntas em cada janela nesta estimativa (conservador)'); }
        else if(!cliq){ let h=buraco(cf0,adj); if(h===false) h=buraco(cf0,adj.map((r,a)=>r.map((e,b)=>a!==b&&!e)));
          if(h!==false) imp=true; if(h===null) est=true;
          else if(h) add('arranjo de recursos compartilhados que esta estimativa não confere exatamente: as configurações ligadas são consideradas juntas em cada janela (conservador)'); } }
      if(est) add('combinações demais para conferir quem trabalha ao mesmo tempo: as configurações ligadas são consideradas juntas em cada janela nesta estimativa (conservador)');
      if(imp) fc.push(comp); }
    cl.sort((a,b)=>{ for(let i=0;i<Math.min(a.length,b.length);i++) if(a[i]!==b[i]) return a[i]-b[i]; return a.length-b.length; });
    const cc=[]; const vc={}; cl.forEach(c=>cortes(c.map(i=>V[i]),'cq',cc,vc));
    const cf=[]; const vf={}; fc.forEach(c=>cortes(c.map(i=>V[i]),'fc',cf,vf));
    cc.concat(cf).forEach(([k,st,t,sub])=>RS.push([k,pref==='p'?st:[],pref==='a'?st:[],t,sub])); };
  grafo(candP.filter(x=>!x.semRec),'p',SERp); grafo(cand,'a',SERa);
  const trocaDe=(xs)=>{ if(xs.length<2) return 0; let s=0, mn=Infinity; xs.forEach(x=>{ s+=x.troca; if(x.troca<mn) mn=x.troca; }); return s-mn; };
  const trocaR=(xs,P,V)=>{ if(xs.length<2) return 0; const g=V.raiz(xs[0].i); let mn=Infinity; P.forEach(y=>{ if(V.raiz(y.i)===g&&y.troca<mn) mn=y.troca; });
    return xs.reduce((a,x)=>a+x.troca,0)-(xs.some(x=>x.troca===mn)?mn:0); };
  // quem tem a troca reservada numa restrição: todos com troca, menos uma que tenha a menor troca do fecho (a que começa) — regra (a)
  const trocaQuem=(xs,P,V)=>{ const g=V.raiz(xs[0].i); let mn=Infinity; P.forEach(y=>{ if(V.raiz(y.i)===g&&y.troca<mn) mn=y.troca; }); let tirou=false;
    return xs.filter(x=>{ if(!tirou&&x.troca===mn){ tirou=true; return false; } return x.troca>0; }).map(x=>x.nome); };
  // origem de uma restrição: sequência declarada, mesma máquina do cadastro, recurso da fazenda ou mista; estimativa: algum par só se exclui
  // por grupo de recursos de 2+ unidades que serializa (a sequência é suposição desta estimativa, não fato do cadastro)
  const poolNome=(k)=>((pools||{})[k]||{}).nome||k;
  // sequência de fato entre duas (calculada uma vez): sequência declarada, mesma máquina, grupo de 1 unidade ou par que sozinho passa das unidades
  const JM=it.map(x=>it.map(y=>x!==y&&(junto(x,y)||PV.some(z=>{ const a=rpNum(x.rec[z[0]])||0, b=rpNum(y.rec[z[0]])||0; return a>0&&b>0&&a+b>z[2]+1e-9; }))));
  const estDe=(k,ms)=>{ if(k==='sq'||k.indexOf('at:')===0) return false; return ms.some((x,a)=>ms.slice(a+1).some(y=>!JM[x.i][y.i])); };
  const nomes=(xs)=>{ const n=xs.map(x=>x.nome); if(n.length>4) return n.slice(0,3).join(', ')+' e mais '+(n.length-3); return n.length>1?n.slice(0,-1).join(', ')+' e '+n[n.length-1]:n.join(''); };
  // todas as origens comuns aos membros (R3-4): sequência declarada, máquina do cadastro, grupo da fazenda
  const origens=(ms)=>{ const o=[]; if(ms.every(x=>x.seq)) o.push('sq'); ms[0].ativos.forEach(a=>{ if(ms.every(x=>x.ativos.indexOf(a)>=0)&&o.indexOf('at:'+a)<0) o.push('at:'+a); });
    Object.keys(pools||{}).forEach(p=>{ if((um.indexOf(p)>=0||SERp.indexOf(p)>=0||SERa.indexOf(p)>=0)&&ms.every(x=>(rpNum(x.rec[p])||0)>0)) o.push('pl:'+p); }); return o; };
  const W={}, jan={}, pista={}, pistaA={}, TRC={}, SUB={}, MS={}, EC={};
  const EST=(k)=>(k in EC)?EC[k]:(EC[k]=estDe(k,MS[k]));   // só para quem vira motivo
  RS.forEach(([k,xs,xa,wx,sub])=>{ const w=(wx!==undefined)?wx:Math.max.apply(null,xs.concat(xa).map(x=>x.H)); if(!isFinite(w)) return; W[k]=w;   // corte por prazo: janela t
    MS[k]=xs.length>1?xs:xa; SUB[k]=!!sub;
    if(xs.length>1) pista[k]=xs; if(xa.length>1){ pistaA[k]=xa; const tr=trocaR(xa,cand,U); jan[k]=w-tr; if(tr>1e-12) TRC[k]=trocaQuem(xa,cand,U); } });
  const PL={}; Object.keys(jan).forEach(g=>pistaA[g].forEach(x=>{ (PL[x.i]||(PL[x.i]=[])).push(g); }));
  const pl=(x)=>PL[x.i]||[];   // restrições de janela da divisão de uma configuração (indexadas, W4)
  // 2) divide a área respeitando as janelas (a própria e a da sequência): é o que cabe, o atendido
  const aloca=(ad)=>{ const q=it.map(()=>0); let saldo=0; const cz={}; const uso={}; const liga={};
    fx.forEach(x=>{ const t=x.t; if(t<=1e-12) return;
      if(x.r===null){ saldo+=t; cz.rend=1; ad(x.nome+': sem rendimento válido (ha/h), a parte dela fica sem conjunto'); return; }
      q[x.i]=Math.min(t,x.r*x.H); if(t-q[x.i]>1e-9){ saldo+=t-q[x.i]; if(x.semRec) cz.rec=1; else { cz.jan=1; ad(x.nome+': a parte fixa não cabe na janela de '+rpF(x.H)+' h'); } } });
    const cab=q.slice(), cortes=[];   // o que cabia na própria janela; o motivo diz a fração final, depois de todas as restrições
    const gs=Object.keys(jan); gs.filter(g=>!SUB[g]).concat(gs.filter(g=>SUB[g])).forEach(g=>{ const xs=pistaA[g].filter(x=>x.p!==null&&q[x.i]>0); const hf=xs.reduce((a,x)=>a+q[x.i]/x.r,0); const B=Math.max(0,jan[g]);
      if(hf>B+1e-9){ const f=B/hf; xs.forEach(x=>{ const n=q[x.i]*f; saldo+=q[x.i]-n; q[x.i]=n; }); cz.seq=1; cortes.push(g); liga[g]=1; } });
    // um motivo por grupo e janela: a restrição da menor fração final (R2-4; cortes e máquinas não repetem o mesmo aviso)
    const pfG={}, pfO=[];
    cortes.forEach(g=>{ const fs=pistaA[g].filter(x=>x.p!==null&&cab[x.i]>0).map(x=>q[x.i]/cab[x.i]); const mn=Math.min.apply(null,fs), mx=Math.max.apply(null,fs);
      const r0=raiz(pistaA[g][0].i)+'@'+W[g], c=pfG[r0];
      if(!c){ pfG[r0]={g,mn,mx}; pfO.push(pfG[r0]); } else if(mn<c.mn-1e-9){ c.g=g; c.mn=mn; c.mx=mx; } });
    pfO.forEach(({g,mn,mx})=>{
      ad('as partes fixas '+(EST(g)?'consideradas em sequência nesta estimativa':'em sequência')+' não cabem na janela de '+rpF(W[g])+' h: '+(mx-mn<=1e-9?'cada uma faz '+rpF(mn*100)+' %':'fazem de '+rpF(mn*100)+' % a '+rpF(mx*100)+' %')+' do que cabia na própria janela ('+nomes(pistaA[g].filter(x=>x.p!==null&&cab[x.i]>0))+')'); });
    Object.keys(jan).forEach(g=>{ uso[g]=pistaA[g].filter(x=>x.p!==null).reduce((a,x)=>a+q[x.i]/x.r,0); });   // depois de todas as restrições
    if(R>0){
      if(!livres.length){ saldo+=R; if(it.length) cz.part=1; else cz.cfg=1; ad(it.length?'as partes fixas não cobrem toda a área':'atividade sem conjunto'); }
      else if(!livOk){ saldo+=R; cz.rend=1; livres.filter(x=>x.r===null).forEach(x=>ad(x.nome+': sem rendimento válido (ha/h); '+(livres.length>1?'a divisão pelo rendimento fica pendente':'horas pendentes'))); }
      else { let rest=R, at=livres.slice(), bj=false, bs=false, bsF=false, br=false; const lg={};
        while(at.length){ const sr=at.reduce((a,x)=>a+x.r,0); const T=rest/sr; let e=T; at.forEach(x=>{ if(x.H<e) e=x.H; });
          const na={}, tl={}; at.forEach(x=>pl(x).forEach(g=>{ na[g]=(na[g]||0)+1; }));
          Object.keys(na).forEach(g=>{ tl[g]=Math.max(0,jan[g]-(uso[g]||0))/na[g]; if(tl[g]<e) e=tl[g]; });
          if(!(e<T)){ at.forEach(x=>{ q[x.i]=x.r*T; }); rest=0; break; }
          const fz=at.filter(x=>x.H<=e||pl(x).some(g=>tl[g]<=e));
          fz.forEach(x=>{ q[x.i]=x.r*e; rest-=q[x.i]; pl(x).forEach(g=>{ uso[g]=(uso[g]||0)+e; if(tl[g]<=e){ bs=true; lg[g]=1; if(!bsF&&!EST(g)) bsF=true; } }); if(x.H<=e){ if(x.semRec) br=true; else bj=true; } });
          at=at.filter(x=>fz.indexOf(x)<0); }
        if(rest>1e-9){ saldo+=rest; Object.keys(lg).forEach(g=>{ liga[g]=1; });
          if(bs){ cz.seq=1; ad((bsF?'em sequência':'consideradas em sequência nesta estimativa,')+' dividem a mesma janela: a área que não cabe fica sem conjunto'); } if(bj||(!bs&&!br)){ cz.jan=1; ad('as janelas não comportam toda a área'); } if(br) cz.rec=1; } } }
    // regra (a): a troca reservada fica (conservadora), mas o motivo diz de quem é e o próximo ajuste; se ela ocupa a janela inteira, é a causa
    // um motivo por grupo e janela: a troca que ocupa a janela ou, senão, a maior reservada (R2-4)
    const tcG={}, tcO=[];
    Object.keys(liga).forEach(g=>{ const ns=TRC[g]; if(!ns||!ns.length) return; if(jan[g]<=1e-9) cz.troca=1; const v=[jan[g]<=1e-9?1:0,W[g]-jan[g]];
      const r0=raiz(pistaA[g][0].i)+'@'+W[g], c=tcG[r0];
      if(!c){ tcG[r0]={g,v}; tcO.push(tcG[r0]); } else if(v[0]>c.v[0]||(v[0]===c.v[0]&&v[1]>c.v[1]+1e-9)){ c.g=g; c.v=v; } });
    tcO.forEach(({g})=>{ const ns=TRC[g]; const quem=ns.join(', '); const os=origens(pistaA[g]);
      const rot=(o)=>o==='sq'?'sequência declarada':(o.indexOf('at:')===0?'mesma máquina do cadastro':poolNome(o.slice(3))+' da fazenda');
      const de=os.map(rot).filter((t,k,a)=>a.indexOf(t)===k).join(' e '), o=os.length===1?os[0]:'';
      const aj=o==='sq'?'tire '+quem+' da sequência declarada':(o.indexOf('at:')===0?'use outro conjunto para '+quem:(o.indexOf('pl:')===0?'tenha mais '+poolNome(o.slice(3))+' na fazenda':'separe '+quem+' das outras ('+(de||'sequência declarada, mesma máquina ou recurso da fazenda')+')'));
      ad(quem+': troca de '+rpF(W[g]-jan[g])+' h reservada na janela de '+rpF(W[g])+' h de '+nomes(pistaA[g])+' ('+(de?de+(EST(g)?', em sequência nesta estimativa':''):(EST(g)?'em sequência nesta estimativa':'em sequência'))+'); para liberar horas, reduza a troca ou '+aj); });
    return {q,saldo,cz}; };
  const p2=aloca(add); let saldo=p2.saldo; const cz=p2.cz; it.forEach(x=>{ x.q=p2.q[x.i]; });
  // PLANO: a demanda inteira pela partilha do usuário, sem cortar em janela nenhuma (REND-RETORNO-1818: cortar a parte fixa na própria
  // janela antes de somar escondia 5 h no S5). A sequência precisa disso para a parte dela; o que passa da janela é o déficit (conflito à vista).
  const q1=it.map(()=>0); fx.forEach(x=>{ if(x.r!==null&&x.t>1e-12) q1[x.i]=x.t; });
  if(R>0&&livOk){ const sr=planLiv.reduce((a,x)=>a+x.r,0); planLiv.forEach(x=>{ q1[x.i]=x.r*R/sr; }); }
  // conflito (R3-2): fato e estimativa separados. Fato = restrição física (sequência, máquina, grupo de 1) ou corte por prazo de uma clique
  // do grafo de fato (JM) no plano; estimativa = o resto. Por grupo, o maior déficit de fato e, se maior, o de estimativa; conta as demais.
  let conflito=false, deficit=0, cfF=false; const cfG={}, cfO=[];
  const P1=candP.filter(x=>q1[x.i]>1e-12);
  const viol=(xs,t,est,g)=>{ if(xs.length<2) return; const nec=xs.reduce((a,x)=>a+q1[x.i]/x.r,0)+trocaR(xs,P1,UP); if(!(nec>t+1e-9)) return;
    conflito=true; const d=nec-t; if(g) deficit=Math.max(deficit,d); if(!est) cfF=true; const r0=UP.raiz(xs[0].i); let c=cfG[r0]; if(!c){ c=cfG[r0]={f:null,e:null,n:0}; cfO.push(r0); }
    if(g) c.n++; const k=est?'e':'f'; if(!c[k]||d>c[k].d+1e-9) c[k]={xs,nec,d,t}; };
  Object.keys(pista).forEach(g=>{ viol(pista[g].filter(x=>q1[x.i]>1e-12),W[g],EST(g),g); });
  { const ns=P1.filter(x=>!x.semRec), m=ns.length, cl=[]; let ps=0;
    const bk=(R_,P,X)=>{ if(++ps>65536||cl.length>4096) return; if(!P.length&&!X.length){ if(R_.length>1) cl.push(R_); return; } const u=P.concat(X)[0];
      for(const v of P.filter(v=>!JM[ns[u].i][ns[v].i])){ bk(R_.concat([v]),P.filter(w=>JM[ns[v].i][ns[w].i]),X.filter(w=>JM[ns[v].i][ns[w].i])); P=P.filter(w=>w!==v); X=X.concat([v]); } };
    if(m>1) bk([],ns.map((_,k)=>k),[]);
    cl.forEach(c=>{ const xs=c.map(k=>ns[k]); xs.map(x=>x.H).filter(h=>isFinite(h)).filter((h,k,a)=>a.indexOf(h)===k).forEach(t=>viol(xs.filter(x=>x.H<=t),t,false,null)); }); }
  cfO.forEach(r0=>{ const c=cfG[r0]; const ms=[]; if(c.f) ms.push([c.f,false]); if(c.e&&(!c.f||c.e.d>c.f.d+1e-9)) ms.push([c.e,true]);
    const mais=c.n-ms.length; ms.forEach(([v,est],k)=>add(nomes(v.xs)+(est?': consideradas em sequência nesta estimativa, precisam de ':': em sequência precisam de ')+rpF(v.nec)+' h para '+rpF(v.xs.reduce((a,x)=>a+q1[x.i],0))+' ha; a janela tem '+rpF(v.t)+' h'+(k===ms.length-1&&mais>0?' (e mais '+mais+(mais>1?' combinações que também não cabem)':' combinação que também não cabe)'):''))); });
  const ativ=it.filter(x=>x.q>1e-12); const grp={}; ativ.forEach(x=>{ const g=raiz(x.i); (grp[g]||(grp[g]=[])).push(x); });
  const UI=uf(); cand.forEach((x,a)=>cand.slice(a+1).forEach(y=>{ if(JM[x.i][y.i]) UI.une(x.i,y.i); }));   // sequência de fato
  let decorrido=0, trocaT=0;
  const emR=(x)=>Object.keys(jan).some(k=>pistaA[k].indexOf(x)>=0);
  Object.keys(grp).forEach(g=>{ const xs=grp[g]; let soma=0; const mn=Math.min.apply(null,xs.map(x=>x.troca));
    const ini=xs.find(x=>x.troca===mn&&emR(x))||xs.find(x=>x.troca===mn);   // começa a de menor troca; no empate, a que divide janela (como na reserva, regra a)
    xs.forEach(x=>{ x.h=x.q/x.r; let tr=0; if(xs.length>1&&x!==ini) tr=x.troca; x.ht=x.h+tr; trocaT+=tr; x.emSeq=xs.length>1; x.seqEst=x.emSeq&&!xs.some(y=>y!==x&&UI.raiz(y.i)===UI.raiz(x.i)); x.grupo=Number(g); soma+=x.ht; });
    if(soma>decorrido) decorrido=soma; });
  it.forEach(x=>{ if(x.q<=1e-12) x.grupo=raiz(x.i); });
  let hc=0, custo=0, custoOk=true, diesel=0, dieselOk=true, hh=0;
  it.forEach(x=>{ if(x.q<=1e-12){ x.q=0; x.h=0; x.ht=0; x.custo=(x.ch===null?null:0); x.diesel=(x.d===null?null:0); return; }
    hc+=x.h; hh+=x.h*x.pess;
    if(x.ch===null){ custoOk=false; add(x.nome+': tarifa desconhecida (R$/h), custo não calculado'); } else { x.custo=x.h*x.ch; custo+=x.custo; }
    if(x.d===null) dieselOk=false; else { x.diesel=x.h*x.d; diesel+=x.diesel; } });
  const alocado=it.reduce((a,x)=>a+x.q,0); if(saldo<1e-9) saldo=0;
  const pend=Q>1e-12&&alocado<=1e-12;   // nada atribuído: horas, prazo e custo ficam pendentes (nunca 0 h), com a causa
  const causa=!pend?'':(cz.cfg?'sem conjunto':(cz.rend?'sem rendimento':((cz.jan||cz.seq)?(cz.troca?'troca reservada ocupa a janela':'sem horas na janela'):(cz.rec?'sem recurso na fazenda':'partes fixas abaixo de 100 %'))));
  // 3) SALDO em horas, pelas premissas do plano: parte fixa → o que faltou dela, na própria configuração; resto → pelo rendimento entre as
  //    sem % (terminam juntas). Sem rendimento, sem conjunto ou partes abaixo de 100 %: área sem horas calculáveis (semHoras), nunca 0 h.
  //    NECESSÁRIO = atendido + saldo (ha e horas-conjunto); decorrido necessário = cada sequência inteira com as trocas, a maior entre as que
  //    trabalham ao mesmo tempo. Vale para paralelo e sequência; não é prazo de reprogramação com novas trocas, locais ou jornadas.
  let semH=0; const fq=it.map(()=>0);
  fx.forEach(x=>{ if(x.t<=1e-12) return; if(x.r===null){ semH+=x.t; return; } const u=x.t-x.q; if(u>1e-9) fq[x.i]=u; });
  if(R>0){ if(!livOk) semH+=R; else { const rest=R-livres.reduce((a,x)=>a+x.q,0); if(rest>1e-9){ const sr=planLiv.reduce((a,x)=>a+x.r,0); planLiv.forEach(x=>{ fq[x.i]+=x.r*rest/sr; }); } } }
  let nhc=0, fhc=0, necDec=0; const pis={};
  it.forEach(x=>{ x.fq=fq[x.i]; x.fh=x.fq>0?x.fq/x.r:0; x.nq=x.q+x.fq; x.nh=x.h+x.fh; nhc+=x.nh; fhc+=x.fh; if(x.nq>1e-12){ const g=UP.raiz(x.i); (pis[g]||(pis[g]=[])).push(x); } });
  Object.keys(pis).forEach(g=>{ const xs=pis[g]; const s=xs.reduce((a,x)=>a+x.nh,0)+trocaDe(xs); if(s>necDec) necDec=s; });
  const semNada=Q>1e-12&&Q-semH<=1e-9;   // nenhuma hora calculável: a necessidade também fica pendente
  const nec={area:Q,hconj:semNada?null:nhc,decorrido:semNada?null:necDec,semHoras:semH};
  const falta={area:saldo,hconj:semNada?null:fhc,decorrido:semNada?null:Math.max(0,necDec-(pend?0:decorrido)),semHoras:semH};
  return {Q,alocado,saldo,pendente:pend,causa,hconj:pend?null:hc,decorrido:pend?null:decorrido,troca:trocaT,custo,custoOk,custoHa:(custoOk&&alocado>1e-12)?custo/alocado:null,
    diesel,dieselOk,hh,conflito,conflitoEst:conflito&&!cfF,deficit,nec,falta,motivos:mot,itens:it}; }
// <<< REPARTIR
// configurações de uma atividade nesta safra (uma ou várias); sem nenhuma → pendência com motivo, nunca o conjunto de outra atividade
function cfgLeaves(rows){ const o=[]; const w=(l)=>(l||[]).forEach(r=>{ if(r.livre) return; if(r.kids&&r.kids.length) w(r.kids); else if(!r.grp) o.push(r); }); w(rows); return o; }
function cfgsOf(self,saf,op,atv){ return cfgLeaves(g2rows(self,GR(rendGid(saf)))).filter(k=>k.v.op===op&&k.v.atv===atv); }
const SEQ_T='Em sequência: divide trator, implemento ou operador', PAR_T='Ao mesmo tempo, com recursos próprios';
function ativosDe(id){ const s=String(id||''); return (!s||s==='classe'||s==='prestador')?[]:s.split('+'); }
// o prestador traz a equipe dele: não conta horas-homem da fazenda (a etapa 5 também não conta pessoas dele)
function cfgIn(k){ const x=k.v; return {id:k.id,nome:x.nome,rend:x.rend,part:x.part,jan:x.jan,custo_h:x.custo_h,diesel:x.diesel,pess:(x.conj_id==='prestador'?0:x.pess),seq:x.seq===SEQ_T,troca:x.troca,ativos:ativosDe(x.conj_id),rec:k.rec||{}}; }
// quantas unidades a fazenda tem de cada grupo de recursos (etapa 5): duas configurações não usam a mesma plantadeira ao mesmo tempo
function poolsOf(self){ const o={}; ['g_recp_maq','g_recp_pes'].forEach(g=>{ const sp=GR(g); if(sp) g2rows(self,sp).forEach(r=>{ o[r.id]={un:Number(r.v.un)||0,nome:r.v.nome}; }); }); return o; }
function partTxt(x){ const p=rpNum(x.part); return (p===null||isNaN(p))?'pelo rendimento':(nfa(p)+' % da área'); }
function leaves(rows){ const o=[]; (rows||[]).forEach(r=>{ if(r.livre) return; if(r.grp) (r.kids||[]).forEach(k=>o.push(k)); else o.push(r); }); return o; }
// etapa 2: todos os talhões da fazenda aparecem; o que ainda não tem cultivo nesta safra vira linha livre "sem cultivo · Planejar talhão"
// (calculada a cada exibição; não entra em área, contagem, demanda nem aplicação de plano)
function syncLivres(self,k,v){ const sp=GR('g_cult_'+k); if(!sp) return; const rows=g2rows(self,sp);
  for(let i=rows.length-1;i>=0;i--){ if(rows[i].livre) rows.splice(i,1); }
  if(k==='S2526') return;   // safra encerrada: só consulta
  const usados={}; leaves(rows).forEach(c=>{ usados[c.v.talhao]=1; });
  // só os talhões da fazenda da safra (a safra nova ainda sem fazenda usa a Santa Rita)
  const sr=g2rows(self,GR('g_saf')).find(r=>r.id===k); const faz=(sr&&sr.v.faz)||'Santa Rita';
  Object.keys(D2.talhoes||{}).forEach(t=>{ if(usados[t]) return; if(((D2.talfaz||{})[t]||'Santa Rita')!==faz) return; const ha=talhaoArea(t); const fn='livre_'+k+'_'+t;
    v[fn]=()=>cultNovoTalhao(self,k,t);
    rows.push({id:'livre_'+t, livre:true, ro:true, dr:fn, v:{talhao:t,local:t,faz}, s:{local:t,faz},
      p:{local:[{k:'b',t:t},{k:'mut',t:'sem cultivo · '+nf(ha)+' ha'}], faz:[{k:'mut',t:faz}], cult:[{k:'act',t:'Planejar talhão ›',fn:fn,lk:true}]}}); }); }
// abre "Novo cultivo" já com o talhão e a área toda dele
function cultNovoTalhao(self,k,t){ const sp=GR('g_cult_'+k); const ed=sp.edit||{}; const draft={}; (ed.fields||[]).forEach(f=>{ draft[f.k]=(f.def!==undefined?String(f.def):''); });
  draft.talhao=t; draft.area=String(talhaoArea(t)).replace('.',',');
  g2set(self,sp.id,{fm:{rid:null,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:false,isNew:true,mode:'form'},fl:null,fmc:null}); }
function cultRows(self,saf){ return saf? leaves(g2rows(self,GR('g_cult_'+sk(saf)))):[]; }
function talhaoArea(t){ return Number((D2.talhoes||{})[t])||0; }
function nfa(n){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:2}); }
function r2(n){ return Math.round(Number(n)*100)/100; }
// valor em R$ na composição: inteiro sem casas, com centavos quando houver (a soma mostrada fecha com o total)
function nm(n){ const x=r2(Number(n)||0); return Number.isInteger(x)?nf(x,0):nf(x,2); }
// coluna de data ordenável: a grade ordena colunas 'date' pelo texto dd/mm/aaaa (dia primeiro);
// por isso a coluna usa t:'num' com a chave aaaammdd em v, mostra a data em p e busca/filtra pelo texto em s
function dcol(r,k,iso,txt){ const ok=/^\d{4}-\d{2}-\d{2}/.test(String(iso||'')); const t=txt||(ok?br(String(iso).slice(0,10)):'—');
  r.v[k]=ok?Number(String(iso).slice(0,10).replace(/-/g,'')):''; r.p[k]=[{k:'txt',t}]; r.s[k]=ok?t:''; }
function letra(i){ let s=''; i++; while(i>0){ const m=(i-1)%26; s=String.fromCharCode(65+m)+s; i=Math.floor((i-1)/26); } return s; }
function nextNome(t,usados){ for(let i=0;;i++){ const n=t+'-'+letra(i); if(usados.indexOf(n)<0) return n; } }
function copyAdj(self,id){ const a=adjOf(self)[id]; return a?JSON.parse(JSON.stringify(a)):null; }
function adjOf(self){ return self.state.adj||D2.ajustes; }
function ocorr(self,saf){ const out=[]; const adj=adjOf(self); const pools=poolsOf(self);
  cultRows(self,saf).forEach(c=>{ const pl=planById(c.v.plano); if(!pl||pl.cultura!==c.v.cult) return; const area=Number(c.v.area)||0;
    pl.atividades.forEach(a=>{ const dt=dataAtv(c,a,pl); const cfs=cfgsOf(self,saf,a.op,a.nome);
      // a área da ocorrência se divide entre as configurações da etapa 3; os insumos seguem dose × área e não mudam com a divisão
      const rp=repartir(area,cfs.map(cfgIn),pools); const horas=rp.hconj||0; const aj=adj[c.id]||{}; const A=String(a.id);
      // recursos da etapa 5: horas × multiplicador = Σ horas de cada configuração × unidades dela (máquinas por grupo e pessoas)
      const rec={}; if(horas>0) rp.itens.forEach((x,i)=>{ const rc=(cfs[i]&&cfs[i].rec)||{}; Object.keys(rc).forEach(k=>{ rec[k]=(rec[k]||0)+x.h*rc[k]/horas; }); });
      const prods=a.prods.map((p,i)=>{ const key=A+'|'+i; if(aj[key]==='-') return null; const dose=(aj[key]!==undefined)?Number(aj[key]):p.dose;
        return {nome:prodNome(p.prod,c),grupo:p.grupo,un:p.un,preco:p.preco,dose,q:dose*area}; }).filter(Boolean)
        .concat(Object.keys(aj).filter(k=>k.indexOf(A+'|+')===0).map(k=>{ const x=aj[k]; return {nome:prodNome(x.prod,c),grupo:x.grupo,un:x.un,preco:x.preco,dose:Number(x.dose),q:Number(x.dose)*area}; }));
      out.push({c,a,pl,dt,mi:mesIdx(dt),area,horas,dec:rp.decorrido,cop:rp.custo,cins:prods.reduce((s,p)=>s+p.q*p.preco,0),prods,rec,rp,cfs,
        saldo:rp.saldo,diesel:rp.diesel,hh:rp.hh,pend:rp.pendente}); }); });
  return out; }
// demanda por produto (CAL-01, cal01.js): uso = 1º uso de hoje em diante; a necessidade sai da projeção datada do insumo com as outras
// origens do mesmo estoque — safras abertas da mesma fazenda (agregadas por data), reservas para outros destinos e recebimentos com data.
// Uso planejado antes de hoje já foi realizado (sai da demanda residual: bruta = residual, real = realizado); compra nova só chega na data viável.
function demanda(self,saf){ const m={}; const safRows=g2rows(self,GR('g_saf')); const me=safRows.find(r=>r.id===saf); const faz=(me&&me.v.faz)||'Santa Rita';
  const ordem=(id)=>{ const i=safRows.findIndex(r=>r.id===id); return i<0?99:i; };
  ocorr(self,saf).forEach(o=>o.prods.forEach(p=>{ const d=m[p.nome]||(m[p.nome]={nome:p.nome,grupo:p.grupo,un:p.un,preco:p.preco,bruta:0,uso:'',evs:[]});
   d.bruta+=p.q; if(o.dt&&o.dt>=(D2.hoje||'')&&(!d.uso||o.dt<d.uso)) d.uso=o.dt;
   d.evs.push({dt:o.dt||'',q:p.q,tipo:'dem',own:true,ord:ordem(saf),chave:o.c.id+'|'+o.a.id,t:o.c.v.local+' · '+o.a.nome,calc:nf(p.dose,2)+' '+p.un+'/ha × '+nfa(o.area)+' ha'}); }));   // área com até 2 casas (PRE-REV R5)
  const vistos={}; vistos[sk(saf)]=1;
  safRows.forEach(r=>{ if(r.id===saf||r.ro||(r.v.faz||'Santa Rita')!==faz||vistos[sk(r.id)]) return; vistos[sk(r.id)]=1; const ag={}, ks=[];
    ocorr(self,r.id).forEach(o=>o.prods.forEach(p=>{ if(!m[p.nome]) return; const k=p.nome+'|'+o.dt; if(!ag[k]){ ag[k]={nome:p.nome,dt:o.dt||'',q:0,n:0,chaves:[]}; ks.push(k); }
      ag[k].q+=p.q; ag[k].n++; ag[k].chaves.push(o.c.id+'|'+o.a.id); }));
    ks.forEach(k=>{ const x=ag[k]; m[x.nome].evs.push({dt:x.dt,q:x.q,tipo:'dem',own:false,ord:ordem(r.id),chaves:x.chaves,t:r.v.nome+' · '+x.n+(x.n>1?' usos':' uso')}); }); });
  Object.values(m).forEach(d=>{
    (D2.reservas||[]).forEach(x=>{ if(x.item===d.nome&&x.faz===faz) d.evs.push({dt:x.dt,q:x.q,tipo:'res',own:false,ord:0,chave:x.chave,t:x.t}); });
    (D2.recebDt||[]).forEach(x=>{ if(x.item===d.nome) d.evs.push({dt:x.dt,q:x.q,tipo:'rec',own:false,ord:0,ref:x.ref,t:x.t}); });
    d.res=(D2.reservas||[]).filter(x=>x.item===d.nome&&x.faz===faz).reduce((a,x)=>a+x.q,0);
    d.est=(D2.fisico||{})[d.nome]!==undefined?D2.fisico[d.nome]:(D2.estoque[d.nome]||0); d.rec=D2.receb[d.nome]||0;
    const c=cal01(d.est,d.evs,0,{hoje:D2.hoje,viavel:D2.viavel}); d.liq=c.liq; d.falta=c.falta; d.antes=c.antes; d.tarde=c.tarde; d.valor=d.liq*d.preco;
    d.plano=d.bruta; d.bruta=c.bruta; d.real=c.real; d.rup=c.rupRec; d.cob=c.cob;
    d.quar=(D2.quar||{})[d.nome]||0; d.memo=cal01Memo(c,{un:d.un,res:d.res,quar:d.quar}); }); return m; }
// produtividade da colheita (kg/ha) por cultura, a partir dos cultivos da safra aberta cujo plano (compatível) usa a operação; média ponderada pela área
const KG_UN={'sc/ha':60,'t/ha/ano':1000,'kg/ha':1};
function prodColheita(self,saf,op){ const by={};
  cultRows(self,saf).forEach(c=>{ const pl=planById(c.v.plano); if(!pl||pl.cultura!==c.v.cult||!pl.atividades.some(a=>a.op===op)) return;
    const a=Number(c.v.area)||0, kg=(Number(c.v.meta)||0)*(KG_UN[c.v.unm]||0); if(a<=0||kg<=0) return;
    const b=by[c.v.cult]||(by[c.v.cult]={a:0,s:0}); b.a+=a; b.s+=kg*a; });
  return Object.keys(by).map(cu=>({cult:cu,kg:by[cu].s/by[cu].a})); }
// rendimentos em árvore: operação (grupo) → atividade · conjunto (linha editável). Atividade com duas ou mais configurações vira grupo
// (atividade → configurações), como o talhão dividido em parcelas; com uma só volta a ser linha. Nenhuma média entre configurações.
function rendRo(self,saf){ const so=g2rows(self,GR('g_saf')).find(r=>r.id===saf); return !!(so&&so.ro); }
function compRend(self,saf){ if(!saf) return; const ro=rendRo(self,saf);
  const jan=(x)=>{ const j=rpNum(x.jan); return (j===null||isNaN(j))?[]:[{k:'mut',t:'janela '+nfa(j)+' h por talhão'}]; };
  // incluir outra configuração: no formulário da atividade; na linha só da atividade já dividida (que não abre formulário)
  const mais=(id)=>ro?[]:[{k:'act',t:'+ Outra configuração',fn:'rendnova:'+id,lk:true}];
  const cfgP=(k,cj0,multi)=>{ const x=k.v; const inf=(x.modo==='Informado'); x.multi=multi?'sim':'não'; k.p.custo_kg=[{k:'mut',t:'—'}]; k.s.custo_kg='';
    // conjunto igual ao da operação fica discreto; o diferente aparece em destaque; sem patrimônio diz de onde vem
    const orig=x.conj_id==='classe'?[{k:'mut',t:'por classe, sem patrimônio'}]:(x.conj_id==='prestador'?[{k:'mut',t:'prestador de serviço'}]:[]);
    k.p.nome=[{k:(cj0&&x.nome===cj0&&!multi?'mut':'b'),t:x.nome}].concat(orig); k.s.nome=x.nome;
    // TABELAS-FOCO (5983172395): uma variável por coluna — operação, atividade, planos, modo, largura, velocidade, eficiência, parte, sequência e janela
    k.p.op=[{k:'mut',t:x.op}]; k.s.op=x.op;
    if(multi){ k.p.atv=[{k:'mut',t:x.atv}]; k.s.atv=x.atv; const pp=rpNum(x.part); k.p.part=(pp===null||isNaN(pp))?[{k:'mut',t:'pelo rendimento'}]:[{k:'txt',t:nfa(pp)}];
      k.p.seq=x.seq===SEQ_T?[{k:'chip',t:'Em sequência',c:'yellow'}]:[{k:'txt',t:'Ao mesmo tempo'}]; k.s.seq=x.seq===SEQ_T?'Em sequência':'Ao mesmo tempo'; }
    else { k.p.atv=[{k:'txt',t:x.atv}].concat(x.aj?[{k:'chip',t:'ajustado nesta safra',c:'blue'}]:[]); k.s.atv=x.atv; k.p.part=[{k:'mut',t:'—'}]; k.s.part=''; k.p.seq=[{k:'mut',t:'—'}]; k.s.seq=''; }
    k.s.planos=x.planos||''; k.p.planos=x.planos?[{k:'txt',t:x.planos}]:[{k:'mut',t:'—'}];
    { const j=rpNum(x.jan); k.s.jan=(j===null||isNaN(j))?'':nfa(j); }
    k.v.param=inf?'':(nfa(x.larg)+' m × '+nfa(x.vel)+' km/h × '+nfa(x.efic)+' %'); k.s.modo=inf?'Informado':'Largura × velocidade';
    ['larg','vel','efic'].forEach(f=>{ if(inf){ k.p[f]=[{k:'mut',t:'—'}]; k.s[f]=''; } else { delete k.p[f]; delete k.s[f]; } });
    const rv=rpNum(x.rend); const okR=rv!==null&&!isNaN(rv)&&rv>0;
    k.p.rend=okR?[{k:'b',t:nf(rv,2)}]:[{k:'chip',t:'sem rendimento',c:'red'}]; k.s.rend=okR?nf(rv,2):'sem rendimento';
    // custo por hora: só o número; a composição (máquina, implemento, pessoas) fica no formulário da linha
    delete k.p.custo_h; delete k.s.custo_h;
    // custo por hectare = custo por hora ÷ rendimento, sem arredondar no meio (só na exibição)
    const cha=okR?(Number(x.custo_h)||0)/rv:null; x.custo_ha=(cha===null?'':cha);
    k.p.custo_ha=[{k:(cha===null?'mut':'txt'),t:(cha===null?'—':nf(cha,2))}]; k.s.custo_ha=(cha===null?'':nf(cha,2));
    // custo por quilo só na colheita, abaixo do custo por hectare, com a produtividade das culturas da safra (sem média entre culturas)
    if(String(x.op||'').indexOf('Colheita')!==0) return;
    const pc=prodColheita(self,saf,x.op);
    const kg=(!pc.length||!cha)?'R$/kg não calculável':pc.map(q=>(pc.length>1?q.cult+' ':'')+nf(Math.round(cha/q.kg*10000)/10000,4)+' R$/kg').join(' · ');
    // custo por quilo com a unidade junto (decisão do proprietário, 05/10/2026): "R$ 0,0606/kg"; várias culturas: uma por cultura
    const ckg=(pc.length&&cha)?pc.map(q=>(pc.length>1?q.cult+' ':'')+'R$ '+nf(Math.round(cha/q.kg*10000)/10000,4)+'/kg').join(' · '):'';
    k.p.custo_kg=[{k:(ckg?'txt':'mut'),t:(ckg||'não calculável')}]; k.s.custo_kg=ckg; };
  // atividade com várias configurações: como a área se divide e o rendimento de cada uma (sem somar nem tirar média)
  const atvP=(a)=>{ const ks=cfgLeaves(a.kids); const x=a.v; const fx=ks.filter(k=>{ const p=rpNum(k.v.part); return p!==null&&!isNaN(p); });
    const div=!fx.length?'divide a área pelo rendimento':(fx.length===ks.length?fx.map(k=>nfa(rpNum(k.v.part))+' %').join(' + '):(fx.map(k=>nfa(rpNum(k.v.part))+' %').join(' + ')+' + resto pelo rendimento'));
    a.p.op=[{k:'mut',t:x.op}]; a.s.op=x.op;
    a.p.atv=[{k:'txt',t:x.atv},{k:'chip',t:ks.length+' configurações',c:'blue'}].concat(mais(ks[0]?ks[0].id:'')); a.s.atv=x.atv;
    a.p.planos=x.planos?[{k:'txt',t:x.planos}]:[{k:'mut',t:'—'}]; a.s.planos=x.planos||'';
    a.p.nome=[{k:'mut',t:ks.length+' conjuntos'}]; a.s.nome=ks.map(k=>k.v.nome).join(' '); a.p.part=[{k:'mut',t:div}]; a.s.part='';
    ['modo','larg','vel','efic','rend','custo_ha','custo_kg','seq','jan'].forEach(f=>{ a.p[f]=[{k:'mut',t:f==='modo'?'por configuração':''}]; a.s[f]=''; }); };
  g2rows(self,GR(rendGid(saf))).forEach(g=>{
    if(!g.grp){ cfgP(g,'',false); return; }
    const ks=g.kids||[]; const all=cfgLeaves(ks); const cj=all.map(k=>k.v.nome).filter((n,i,a)=>a.indexOf(n)===i);
    g.p.op=[{k:'b',t:g.v.op}].concat(g.v.aj?[{k:'chip',t:'ajustado nesta safra',c:'blue'}]:[]); g.s.op=g.v.op;
    g.p.atv=[{k:'mut',t:ks.length+(ks.length>1?' atividades':' atividade')}]; g.s.atv='';
    ['modo','larg','vel','efic','rend','custo_h','custo_ha','custo_kg','part','seq','jan','planos'].forEach(f=>{ g.p[f]=[{k:'mut',t:''}]; g.s[f]=''; });
    g.p.nome=[{k:'mut',t:cj.length===1?cj[0]:cj.length+' conjuntos'}]; g.s.nome=cj.join(' ');
    const cj0=ks.length?(ks[0].grp?((cfgLeaves(ks[0].kids)[0]||{v:{}}).v.nome||''):ks[0].v.nome):'';
    ks.forEach(k=>{ if(k.grp){ atvP(k); (k.kids||[]).forEach(q=>cfgP(q,cj0,true)); } else cfgP(k,cj0,false); }); }); }
// equipe em pessoas inteiras: a demanda de Operadores é horas × pessoas (etapa 5)
// safra: início e fim por calendário; o período curto da lista sai das datas
const SAF_MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
function safPeriodo(ini,fim){ if(!/^\d{4}-\d{2}-\d{2}$/.test(String(ini||''))||!/^\d{4}-\d{2}-\d{2}$/.test(String(fim||''))) return ''; const a=ini.split('-'), b=fim.split('-'); const mi=SAF_MES[Number(a[1])-1], mf=SAF_MES[Number(b[1])-1];
  return a[0]===b[0]?(mi+' – '+mf+'/'+b[0]):(mi+'/'+a[0]+' – '+mf+'/'+b[0]); }
function safCheck(d){ const e={}; if(d.ini&&d.fim&&String(d.fim)<=String(d.ini)) e.fim='O fim precisa ser depois do início.'; return e; }
// confere a configuração: pessoas inteiras e partes fixas da mesma atividade até 100 %
function rendCheck(self,rows,r,d,isNew){ const e={}; const n=g2num(d.pess); if(!isNaN(n)&&Math.round(n)!==n) e.pess='Use um número inteiro de pessoas.';
  const nv=isNew?(self._novaCfg||{}):null; const op=nv?nv.op:(r&&r.v.op), atv=nv?nv.atv:(r&&r.v.atv); const p=g2num(d.part);
  if(String(d.multi)==='sim'&&!isNaN(p)){ const s=cfgLeaves(rows).filter(k=>k.v.op===op&&k.v.atv===atv&&(!r||k.id!==r.id)).reduce((a,k)=>{ const q=rpNum(k.v.part); return a+((q===null||isNaN(q))?0:q); },0);
    if(s+p>100+1e-9) e.part='As partes fixas somariam '+nfa(s+p)+' %; o máximo é 100 % (livre: '+nfa(Math.max(0,100-s))+' %).'; }
  return e; }
function rendLive(k,d){ const n=(f)=>{ const x=g2num(d[f]); return isNaN(x)?0:x; };
  if(k==='rend_c'){ const L=n('larg'),V=n('vel'),E=n('efic'); return (L&&V&&E)?nf(rendCalc(L,V,E),2):'—'; }
  // prestador: a tarifa por hora dele é a de Máquina (traz implemento, operador e diesel); implemento e pessoas da fazenda não entram
  if(k==='custo_c') return String(d.conj_id)==='prestador'?nf(n('maq'),2):nf(n('maq')+n('impl')+n('pess')*n('pess_rs'),2);
  return null; }
// conjuntos possíveis para um rendimento: tratores com potência para o implemento, ou o equipamento único da operação; planejar sem
// patrimônio (por classe, ou prestador que traz máquina e equipe) também vale: o cadastro não é obrigatório antes
function cfgBase(r){ return (r&&r.v&&r.v.base)||String((r&&r.id)||'').split('.')[0]; }
function conjOpts(rid){ const c=(D2.conj_opts||{})[String(rid||'').split('.')[0]]; const fim=[{v:'classe',t:'Por classe, sem patrimônio'},{v:'prestador',t:'Prestador de serviço'}];
  return (c?c.opts.map(o=>({v:o.id,t:o.nome+(o.pot?' · '+o.pot+' cv':'')+' · máquina '+nm(o.maq)+' + implemento '+nm(o.impl)+' R$/h'})):[]).concat(fim); }
// atividade com duas ou mais configurações vira grupo; com uma só volta a linha (partes, sequência e troca saem, a janela fica)
function normRend(rows){ rows.forEach(g=>{ if(!g.grp) return; g.kids=(g.kids||[]).map(a=>{ if(!a.grp) return a; const ks=a.kids||[];
    if(ks.length===1){ const k=ks[0]; k.v.part=''; k.v.seq=''; k.v.troca=''; k.v.multi='não'; return k; } ks.forEach(k=>{ k.v.multi='sim'; }); return a; }).filter(a=>!a.grp||(a.kids||[]).length); }); return rows; }
function rendAfter(self,gid,rows,r,isNew){ const x=r.v; let trocou=''; const nv=isNew?self._novaCfg:null; self._novaCfg=null; let novaMsg='';
  if(isNew){ const i=rows.indexOf(r); if(i>=0) rows.splice(i,1); if(!nv){ g2set(self,gid,{rows:g2clone(rows)}); return; }
    // a nova configuração entra na atividade de origem; a anterior continua como estava
    r.id=nv.base+'.c'+String(Date.now()).slice(-7); Object.assign(x,{op:nv.op,atv:nv.atv,opatv:nv.op+' · '+nv.atv,planos:nv.planos,base:nv.base,aj:true}); r.rec=Object.assign({},nv.rec); r.s=r.s||{}; r.p=r.p||{};
    const g=rows.find(q=>q.grp&&q.v.op===nv.op); const ai=g?(g.kids||[]).findIndex(a=>(a.grp?((cfgLeaves(a.kids)[0]||{v:{}}).v.atv):a.v.atv)===nv.atv):-1;
    if(!g||ai<0){ g2set(self,gid,{rows:g2clone(rows)}); self.setState({g2toast:'Atividade não encontrada: configuração não incluída.'}); return; }
    const a=g.kids[ai]; if(a.grp) a.kids.push(r); else g.kids[ai]={id:'atv_'+a.id,grp:true,ro:true,v:{atv:a.v.atv,op:a.v.op,opatv:a.v.opatv,planos:a.v.planos},s:{},p:{},kids:[a,r]};
    const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); x0[g.id]=true; x0[g.kids[ai].id]=true; g2set(self,gid,{x:x0});
    novaMsg=' A área de '+nv.atv+' agora se divide entre '+cfgLeaves([g.kids[ai]]).length+' configurações.'; }
  const co=(D2.conj_opts||{})[cfgBase(r)]; const antes=self._conjAntes; self._conjAntes=undefined;
  if(co&&(isNew||(antes!=null&&antes!==String(x.conj_id||'')))){ const o=co.opts.find(q=>q.id===x.conj_id); if(o){ x.nome=o.nome; if(r.s) r.s.nome=o.nome; if(r.p) delete r.p.nome; x.maq=o.maq; x.impl=o.impl; trocou=' Conjunto trocado: custos por hora do cadastro (máquina '+nm(o.maq)+', implemento '+nm(o.impl)+').'; } }
  // rendimento com a precisão toda (largura × velocidade ÷ 10 × eficiência); a tela arredonda só ao mostrar
  if(x.modo!=='Informado'){ x.rend=rendCalc(x.larg,x.vel,x.efic); } else { x.larg=''; x.vel=''; x.efic=''; }
  ['maq','impl','pess_rs'].forEach(f=>{ if(x[f]!==''&&x[f]!==undefined&&x[f]!==null) x[f]=r2(x[f]); }); // R$/h em centavos
  // prestador traz implemento, operador e diesel: a tarifa é a de Máquina; o que veio copiado da configuração de origem sai (e o aviso diz)
  let prest=''; if(x.conj_id==='prestador'&&((Number(x.impl)||0)>0||(Number(x.pess)||0)>0||(Number(x.pess_rs)||0)>0)){ x.impl=0; x.pess=0; x.pess_rs=0; prest=' Prestador: a tarifa é a de Máquina (R$ '+nf(Number(x.maq)||0,2)+'/h); implemento e pessoas da fazenda não entram.'; }
  x.pes_h=(Number(x.pess)||0)*(Number(x.pess_rs)||0);
  // a equipe do conjunto é a demanda de 'Operadores e equipe' na etapa 5 (h-pessoa = h do conjunto × pessoas); o prestador não usa recursos da fazenda
  r.rec=Object.assign({},r.rec||{});
  if(x.conj_id==='prestador') r.rec={};
  else { if(!Object.keys(r.rec).some(k=>k!=='oper')){ const b=(D2.conj||[]).find(c=>c.id===cfgBase(r)); if(b) r.rec=Object.assign({},b.rec); }
    if(Number(x.pess)>0) r.rec.oper=Number(x.pess); else delete r.rec.oper; }
  x.custo_h=r2((Number(x.maq)||0)+(Number(x.impl)||0)+x.pes_h);
  x.custo_ha=x.rend?x.custo_h/x.rend:'';
  // Aplicar em: todas as atividades da operação (padrão) ou só esta; só para atividade de uma configuração, e só copia para
  // atividades de uma configuração (as divididas entre conjuntos ficam como estão). O selo fica na operação quando vale para todas.
  let n=0, nd=0; const g=rows.find(q=>q.grp&&(q.kids||[]).some(k=>k.id===r.id)); const todas=!!g&&!isNew&&(x.esc!=='Só esta atividade'); delete x.esc;
  if(g&&!isNew) x.aj=!todas;
  if(todas){ g.v.aj=true;
    g.kids.forEach(k=>{ if(k.id===r.id) return; if(k.grp){ nd++; return; } ['conj_id','nome','modo','larg','vel','efic','rend','maq','impl','pess','pess_rs','pes_h','custo_h','custo_ha','diesel'].forEach(f=>{ k.v[f]=x[f]; }); k.v.aj=false; k.rec=Object.assign({},r.rec); if(k.s) delete k.s.nome; n++; }); }
  normRend(rows);
  g2set(self,gid,{rows:g2clone(rows),fl:r.id});
  self.setState({g2toast:(isNew?('Configuração incluída em '+x.atv+' · '+x.nome+': '+nf(x.rend,2)+' ha/h.'+novaMsg+prest)
    :('Rendimento de '+(n?x.op+' ('+(n+1)+' atividades)':x.atv)+' · '+x.nome+': '+nf(x.rend,2)+' ha/h · '+rs(x.custo_ha||0)+'/ha.'+trocou+prest+(nd?(' '+nd+(nd>1?' atividades divididas entre conjuntos não mudaram.':' atividade dividida entre conjuntos não mudou.')):'')))
    +' Plano operacional e recursos recalculados.'}); }
// + Outra configuração: abre o formulário já preenchido com a configuração de origem; só entra na atividade ao salvar
function rendNova(self,rid){ const saf=self.state.saf; if(!saf) return; if(rendRo(self,saf)){ self.setState({g2toast:'Safra encerrada: somente consulta.'}); return; }
  const gid=rendGid(saf); const sp=GR(gid); const rows=g2rows(self,sp); const b=g2find(rows,rid); if(!b||b.grp) return;
  const st=g2st(self,gid); if(st.fm&&!st.fm.ro&&g2dirty(st.fm)){ self.setState({g2toast:'Salve ou descarte as alterações da configuração aberta antes de incluir outra.'}); return; }
  const draft={}; ((sp.edit||{}).fields||[]).forEach(f=>{ const v0=b.v[f.k]; draft[f.k]=(v0===undefined||v0===null)?'':(f.t==='num'?String(v0).replace('.',','):String(v0)); });
  Object.assign(draft,{multi:'sim',base:cfgBase(b),opatv:b.v.op+' · '+b.v.atv,conj_id:'classe',nome:'',part:'',seq:PAR_T,troca:'',esc:''});
  self._novaCfg={op:b.v.op,atv:b.v.atv,planos:b.v.planos||'',base:cfgBase(b),rec:Object.assign({},b.rec||{})};
  g2set(self,gid,{fm:{rid:null,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:false,isNew:true,mode:'form'},fl:null,fmc:null}); }
function rendRemover(self,gid,rid){ const rows=g2clone(g2rows(self,GR(gid))); let nome='', atv='';
  rows.forEach(g=>{ if(!g.grp) return; (g.kids||[]).forEach(a=>{ if(!a.grp) return; const i=(a.kids||[]).findIndex(k=>k.id===rid); if(i>=0&&a.kids.length>1){ nome=a.kids[i].v.nome; atv=a.kids[i].v.atv; a.kids.splice(i,1); } }); });
  if(!nome){ self.setState({rmCfg:null}); return; }
  normRend(rows); g2set(self,gid,{rows,fm:null}); self.setState({rmCfg:null,g2toast:'Configuração removida de '+atv+': '+nome+'. A área volta para as outras; plano operacional e recursos recalculados.'}); }
// ações do formulário da configuração: incluir outra (a atual continua) e remover (só quando há mais de uma, com confirmação)
function rendActs(self,gid,r){ if(!r||r.grp) return []; const saf=self.state.saf; if(!saf||rendRo(self,saf)) return [];
  const n=cfgsOf(self,saf,r.v.op,r.v.atv).length;
  const out=[{t:'+ Outra configuração para '+r.v.atv, h:'Divide a área desta atividade com outro conjunto (outro tamanho, rendimento ou tarifa). Esta configuração continua.',
    go:()=>{ const cur=g2st(self,gid).fm; if(cur&&!cur.ro&&g2dirty(cur)){ self.setState({g2toast:'Salve ou descarte as alterações desta configuração antes de incluir outra.'}); return; } g2set(self,gid,{fm:null}); rendNova(self,r.id); }}];
  if(n>1){ const ask=self.state.rmCfg===r.id;
    out.push({t:ask?('Confirmar: remover '+r.v.nome):'Remover esta configuração', h:ask?'A área dela volta a ser dividida entre as outras configurações.':'Vale só para esta atividade nesta safra.',
      go:()=>{ if(!ask){ self.setState({rmCfg:r.id}); return; } rendRemover(self,gid,r.id); }}); }
  return out; }
function leafParts(r,adj,kid){ const pl=planById(r.v.plano); const na=Object.keys(adj[r.id]||{}).length; const t=r.v.talhao||r.v.local;
  // TABELAS-FOCO (5983172395): local | tipo | … | meta (com a unidade junto, decisão de 05/10/2026) | plano | versão | ajustes; a ação fica com a entidade
  r.p.local=[{k:'b',t:r.v.local||'—'}].concat((!kid&&!r.ro)?[{k:'act',t:'Dividir',fn:'divide:'+t,lk:true}]:[]); r.s.local=r.v.local;
  r.v.tipo=(kid?'Parcela':'Talhão inteiro')+(r.decl?' (sem polígono)':''); r.p.tipo=[{k:'txt',t:r.v.tipo}]; r.s.tipo=r.v.tipo; r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre='';
  r.p.meta=[{k:'txt',t:nfa(r.v.meta)+(r.v.unm?' '+r.v.unm:'')}]; r.s.meta=r.p.meta[0].t; dcol(r,'dt_plantio',r.v.plantio);   // meta exata (até 2 casas) com a unidade junto (decisão do proprietário, 05/10/2026)
  r.v.ver=(pl&&pl.cultura===r.v.cult)?pl.versao:''; r.p.ver=r.v.ver?[{k:'txt',t:'v'+r.v.ver}]:[{k:'mut',t:'—'}]; r.s.ver=r.v.ver?'v'+r.v.ver:'';
  if(pl && pl.cultura===r.v.cult){ r.p.plano=[{k:'txt',t:pl.nome},{k:'br'},{k:'act',t:(r.ro?'Ver insumos':'Ajustar insumos'),fn:'openlp:'+r.id,lk:true}]; r.s.plano=pl.nome; }
  else if(pl){ r.p.plano=[{k:'chip',t:'Plano de '+pl.cultura+' incompatível',c:'red'},{k:'act',t:'Reaplicar',fn:'applyone:'+r.id}]; r.s.plano='incompatível'; }
  else { r.p.plano=r.ro?[{k:'mut',t:'sem plano'}]:[{k:'act',t:'Aplicar plano',fn:'applyone:'+r.id}]; r.s.plano=''; }
  r.v.aj=na; r.p.aj=na?[{k:'chip',t:String(na),c:'yellow'}]:[{k:'mut',t:'—'}]; r.s.aj=String(na); }
function grpParts(r,adj){ const ks=r.kids||[]; const t=r.v.talhao; const T=talhaoArea(t); const A=ks.reduce((a,c)=>a+(Number(c.v.area)||0),0); const L=T-A;
  const uniq=(f)=>[...new Set(ks.map(c=>c.v[f]).filter(x=>x!==''&&x!==undefined&&x!==null))];
  r.v.area=r2(A); r.v.faz=(ks[0]&&ks[0].v.faz)||r.v.faz; r.v.cult=uniq('cult').join(', '); r.v.var=uniq('var').join(', ');
  const ds=uniq('plantio').sort(); r.v.plantio=ds[0]||''; dcol(r,'dt_plantio',ds[0],(ds.length>1?(br(ds[0]).slice(0,5)+' a '+br(ds[ds.length-1])):''));
  r.v.meta=''; r.p.meta=[{k:'mut',t:'por parcela'}]; r.s.meta='';
  const pls=uniq('plano').map(planById).filter(Boolean); r.p.plano=pls.length?[{k:'txt',t:(pls.length===1?pls[0].nome:(pls.length+' planos'))}]:[{k:'mut',t:'sem plano'}]; r.s.plano=pls.map(x=>x.nome).join(', ');
  const vs=[...new Set(pls.map(x=>'v'+x.versao))]; r.v.ver=''; r.p.ver=vs.length?[{k:'txt',t:vs.join(', ')}]:[{k:'mut',t:'—'}]; r.s.ver=vs.join(', ');
  const na=ks.reduce((a,c)=>a+Object.keys(adj[c.id]||{}).length,0); r.v.aj=na; r.p.aj=na?[{k:'txt',t:String(na)}]:[{k:'mut',t:'—'}]; r.s.aj=String(na);
  // área livre (ha) do talhão dividido: positiva = livre, negativa = excede (aviso em vermelho)
  r.v.livre=Math.abs(L)<=0.005?0:r2(L); r.p.livre=[{k:L< -0.005?'cn':'txt',t:nfa(Math.abs(L)<=0.005?0:L),c:'red'}]; r.s.livre=nfa(Math.abs(L)<=0.005?0:L);
  r.v.tipo=ks.length+(ks.length>1?' parcelas':' parcela'); r.p.tipo=[{k:'txt',t:r.v.tipo}]; r.s.tipo=r.v.tipo;
  r.p.local=[{k:'b',t:t}].concat(r.ro?[]:[{k:'act',t:'Dividir',fn:'divide:'+t,lk:true}]); r.s.local=t; }
// Uma parcela com a área toda volta a talhão inteiro; talhão inteiro com área menor vira parcela com área livre visível.
function normCult(rows){ const out=[];
  rows.forEach(r=>{ const t=r.v.talhao, T=talhaoArea(t);
    if(r.grp){ const ks=r.kids||[]; if(!ks.length) return;
      if(ks.length===1 && Math.abs((Number(ks[0].v.area)||0)-T)<=0.005){ const k=ks[0]; k.v.local=t; k.v.tipo='Talhão inteiro'; k.s.local=t; k.decl=false; out.push(k); return; }
      ks.forEach(k=>{ k.v.tipo='Parcela'; }); out.push(r); return; }
    if(T && (Number(r.v.area)||0)<T-0.005){ if(r.v.local===t){ r.v.local=t+'-A'; r.s.local=r.v.local; } r.v.tipo='Parcela'; r.decl=true;
      out.push({id:'grp_'+t,grp:true,dr:'div_'+t,ro:!!r.ro,v:{talhao:t,faz:r.v.faz,local:t},s:{},p:{},kids:[r]}); return; }
    r.v.tipo='Talhão inteiro'; out.push(r); });
  return out; }
function cultCheck(self,gid,rows,r,d,isNew){ const e={}; const t=isNew?String(d.talhao||''):(r&&r.v.talhao); const T=talhaoArea(t); const a=g2num(d.area);
  const outros=leaves(rows).filter(c=>!r||c.id!==r.id);
  if(!isNaN(a)&&T&&a>T+0.005) e.area='Máximo '+nfa(T)+' ha: é a área do talhão '+t+'.';
  else if(!isNew&&!isNaN(a)){ const s=outros.filter(c=>c.v.talhao===t).reduce((x,c)=>x+(Number(c.v.area)||0),0); if(s+a>T+0.005) e.area='As parcelas de '+t+' somariam '+nfa(s+a)+' ha; o talhão tem '+nfa(T)+' ha (livre: '+nfa(Math.max(0,T-s))+' ha).'; }
  const nm=String(d.local||'').trim();
  if(!isNew&&r&&r.v.tipo!=='Parcela'&&nm&&nm!==t) e.local='Talhão inteiro usa o nome do talhão ('+t+'). Para criar parcelas, use Dividir em parcelas.';
  else if(!isNew&&r&&r.v.tipo==='Parcela'&&!nm) e.local='Informe o nome da parcela.';
  if(nm&&!e.local&&outros.some(c=>c.v.local===nm)) e.local='Já existe '+nm+' nesta safra.';
  const pl=planById(String(d.plano||'')); if(pl&&pl.cultura!==String(d.cult||'')) e.plano='Este plano é de '+pl.cultura+'. Escolha um plano de '+d.cult+' ou deixe sem plano.';
  self._planoAntes=(!Object.keys(e).length&&!isNew&&r)?{id:r.id,plano:String(r.v.plano||'')}:null;
  return e; }
function cultAfter(self,gid,rows,r,isNew){ let all=g2clone(rows.filter(x=>!x.livre)); let msg='';  // linhas livres são recalculadas a cada exibição
  if(r&&isNew){ const t=r.v.talhao; const x=g2find(all,r.id); all=all.filter(y=>y.id!==r.id);
    x.v.faz=x.v.faz||'Santa Rita'; x.v.plano=x.v.plano||''; x.v.colheita='';
    if(leaves(all).some(c=>c.v.talhao===t)){ g2set(self,gid,{rows:all,fl:null}); openDiv(self,t,x); self.setState({g2toast:t+' já está nesta safra: confira a divisão em parcelas e salve.'}); return; }
    const T=talhaoArea(t); const a=Number(x.v.area)||0;
    if(a>=T-0.005){ x.v.local=t; x.v.tipo='Talhão inteiro'; x.decl=false; } else { x.v.local=x.v.local||(t+'-A'); x.v.tipo='Parcela'; x.decl=true; }
    x.s.local=x.v.local; all.push(x); const fim=planById(x.v.plano)?(' · plano '+planById(x.v.plano).nome+'.'):'. Escolha o plano agronômico na linha.';
    msg=(x.v.tipo==='Parcela')?('Cultivo incluído como parcela '+x.v.local+' · '+nfa(T-a)+' ha livres em '+t+fim):('Cultivo incluído: '+t+' inteiro'+fim); }
  const pa=self._planoAntes; self._planoAntes=null;
  if(r&&!isNew&&pa&&pa.id===r.id&&pa.plano!==String(r.v.plano||'')){ const adj=JSON.parse(JSON.stringify(adjOf(self))); const n=Object.keys(adj[r.id]||{}).length; const pl=planById(r.v.plano);
    if(n){ delete adj[r.id]; self.setState({adj}); }
    msg=(pl?('Plano de '+r.v.local+': '+pl.nome+' v'+pl.versao):('Plano retirado de '+r.v.local))+(n?(' · '+n+(n>1?' ajustes de dose descartados':' ajuste de dose descartado')):'')+'. Plano operacional, recursos e demanda recalculados.'; }
  const norm=normCult(all); const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); norm.forEach(y=>{ if(y.grp&&x0[y.id]!==false) x0[y.id]=true; });
  g2set(self,gid,{rows:norm,x:x0}); if(msg) self.setState({g2toast:msg}); }
// ---- painel: dividir o talhão em quantas parcelas precisar ----
function dvRow(c){ return {id:c.id||null,local:c.v.local||'',area:(c.v.area===''||c.v.area===undefined)?'':String(r2(c.v.area)).replace('.',','),cult:c.v.cult||'Soja',var:c.v.var||'',plantio:c.v.plantio||'',
  meta:(c.v.meta===''||c.v.meta===undefined)?'':String(c.v.meta).replace('.',','),unm:c.v.unm||'sc/ha',plano:c.v.plano||'',colheita:c.v.colheita||'',adj:null,from:'',decl:!!c.decl,ask:false}; }
function dvDist(lst,T){ const n=lst.length; if(!n) return lst; const each=Math.floor(T*100/n)/100; return lst.map((x,i)=>Object.assign({},x,{area:String(i<n-1?each:r2(T-each*(n-1))).replace('.',',')})); }
function openDiv(self,t,extra){ const saf=self.state.saf; if(!saf){ self.setState({g2toast:'Escolha a safra primeiro.'}); return; }
  const gid='g_cult_'+sk(saf); const rows=g2rows(self,GR(gid)); const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf);
  const cur=leaves(rows).filter(c=>c.v.talhao===t); const ro=!!(safObj&&safObj.ro)||cur.some(c=>c.ro);
  let lst=cur.map(dvRow); let base;
  const inteiro=(cur.length===1&&cur[0].v.tipo!=='Parcela');
  if(!ro&&inteiro&&!extra){ lst[0].local=t+'-A'; lst.push(Object.assign({},lst[0],{id:null,local:t+'-B',from:t+'-A',decl:true,adj:copyAdj(self,cur[0].id)})); lst=dvDist(lst,talhaoArea(t)); base=JSON.stringify(lst); }
  else { base=JSON.stringify(lst); if(extra){ if(inteiro) lst[0].local=t+'-A'; const e=dvRow(extra); e.id=null; e.decl=true;
      const usados=lst.map(x=>x.local).concat(leaves(rows).filter(c=>c.v.talhao!==t).map(c=>c.v.local)); if(!e.local||e.local===t||usados.indexOf(e.local)>=0) e.local=nextNome(t,usados); lst.push(e); } }
  self.setState({dv:{t,rows:lst,base,ro,err:{},gerr:'',warn:false}}); }
function dvSave(self){ const dv=self.state.dv; if(!dv||dv.ro) return; const t=dv.t, T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf); const rows=g2rows(self,GR(gid));
  if(!dv.rows.length){ self.setState({dv:Object.assign({},dv,{gerr:'Mantenha pelo menos uma parcela. Para tirar o talhão da safra, exclua a linha dele na tabela.'})}); return; }
  const outros=leaves(rows).filter(c=>c.v.talhao!==t); const err={}; let A=0; const nomes={};
  dv.rows.forEach((x,i)=>{ const e={}; const nm=String(x.local||'').trim(); const a=g2num(x.area); const m=g2num(x.meta);
    if(!nm) e.local='Informe o nome da parcela'; else if(nomes[nm]||outros.some(c=>c.v.local===nm)) e.local='Nome '+nm+' repetido'; nomes[nm]=1;
    if(isNaN(a)||a<0.01) e.area='Informe a área (mínimo 0,01 ha)'; else A+=a;
    if(!x.cult) e.cult='Escolha a cultura'; if(!String(x.var||'').trim()) e.var='Informe a variedade';
    if(!/^\d{4}-\d{2}-\d{2}$/.test(String(x.plantio||''))) e.plantio='Informe o plantio';
    if(String(x.meta).trim()===''||isNaN(m)||m<0) e.meta='Informe a meta (≥ 0)';
    const plx=planById(x.plano); if(plx&&plx.cultura!==x.cult) e.plano='Plano de '+plx.cultura+' não serve para '+x.cult+': escolha outro ou deixe sem plano';
    if(Object.keys(e).length) err[i]=e; });
  const exc=A>T+0.005;
  if(Object.keys(err).length||exc){ self.setState({dv:Object.assign({},dv,{err,gerr:(exc?('As parcelas somam '+nfa(A)+' ha; o talhão tem '+nfa(T)+' ha. Reduza '+nfa(A-T)+' ha.'):'Corrija os campos destacados; o que você digitou foi mantido.'),warn:false})}); return; }
  const all=g2clone(rows.filter(x=>!x.livre)); const adj=JSON.parse(JSON.stringify(adjOf(self))); const old=leaves(all).filter(c=>c.v.talhao===t); const byId={}; old.forEach(c=>{ byId[c.id]=c; });
  const stamp=String(Date.now()).slice(-6);
  const kids=dv.rows.map((x,i)=>{ const b=(x.id&&byId[x.id])||null; const c=b||{id:'p'+t+'_'+stamp+'_'+i,v:{},s:{},p:{},decl:true};
    if(b&&String(b.v.plano||'')!==String(x.plano||'')) delete adj[b.id];
    Object.assign(c.v,{talhao:t,faz:(b?b.v.faz:(old[0]?old[0].v.faz:'Santa Rita')),local:String(x.local).trim(),cult:x.cult,var:String(x.var).trim(),area:r2(g2num(x.area)),plantio:x.plantio,meta:g2num(x.meta),unm:x.unm,plano:x.plano||'',colheita:x.colheita||''});
    if(b&&b.v.tipo!=='Parcela') c.decl=true;
    c.s={}; c.p={}; if(!b&&x.adj&&Object.keys(x.adj).length) adj[c.id]=JSON.parse(JSON.stringify(x.adj)); return c; });
  const keep=kids.map(c=>c.id); old.forEach(c=>{ if(keep.indexOf(c.id)<0) delete adj[c.id]; });
  const isT=(r)=>r.v.talhao===t; let pos=all.findIndex(isT); const rest=all.filter(r=>!isT(r)); if(pos<0) pos=rest.length;
  rest.splice(pos,0,{id:'grp_'+t,grp:true,dr:'div_'+t,ro:false,v:{talhao:t,faz:kids[0].v.faz,local:t},s:{},p:{},kids});
  const norm=normCult(rest); const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); x0['grp_'+t]=true;
  g2set(self,gid,{rows:norm,x:x0,sel:{},fl:null});
  const inteiro=norm.some(r=>!r.grp&&r.v.talhao===t);
  self.setState({adj,dv:null,g2toast:(inteiro?(t+' volta a talhão inteiro.'):(t+' dividido em '+kids.length+(kids.length>1?' parcelas':' parcela')+(A<T-0.005?(' · '+nfa(T-A)+' ha livres'):'')+'.'))+' Plano operacional, recursos e demanda recalculados.'}); }
function divVals(self,v){ const dv=self.state.dv; v.dv_open=!!dv; if(!dv){ v.dv_rows=[]; return; } const t=dv.t, T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf);
  const lst=dv.rows; const A=lst.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const L=T-A; const exc=L< -0.005, ok=Math.abs(L)<=0.005;
  v.dv_titulo=dv.ro?('Parcelas de '+t):('Dividir '+t+' em parcelas'); v.dv_n=lst.length+(lst.length>1?' parcelas':' parcela');
  v.dv_resumo='Talhão '+nfa(T)+' ha · alocado '+nfa(A)+' ha · livre '+nfa(Math.max(0,L))+' ha';
  v.dv_selo=exc?('Excede em '+nfa(-L)+' ha'):(ok?'Área conferida':(nfa(L)+' ha livres'));
  const cc=exc?['#B42318','#FDE8E6']:(ok?['#1E7A4C','#E4F3E9']:['#8A5A00','#FFF4D6']);
  v.dv_selost='display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';';
  v.dv_ro=!!dv.ro; v.dv_edit=!dv.ro; const adj=adjOf(self);
  const CULT=['Soja','Milho','Feijão','Café','Mamão Formosa'], UNM=['sc/ha','t/ha/ano','kg/ha'];
  const upd=(i,patch)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],patch); return Object.assign({},cur,{rows:rs}); };
  v.dv_rows=lst.map((x,i)=>{ const pl=planById(x.plano); const na=x.id?Object.keys(adj[x.id]||{}).length:Object.keys(x.adj||{}).length; const e=(dv.err||{})[i]||{};
    const set=(f)=>(ev)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],{[f]:ev.target.value}); const er=Object.assign({},cur.err||{}); if(er[i]){ er[i]=Object.assign({},er[i]); delete er[i][f]; if(!Object.keys(er[i]).length) delete er[i]; }
      self.setState({dv:Object.assign({},cur,{rows:rs,err:er,warn:false,gerr:(Object.keys(er).length?cur.gerr:'')})}); };
    const ist=(f,x2)=>'font-family:inherit;font-size:13px;padding:6px 8px;border-radius:8px;box-sizing:border-box;width:100%;min-width:0;color:#15201A;border:1px solid '+(e[f]?'#B42318':'#E4E9E5')+';background:'+(dv.ro?'#F4F6F3':'#FFFFFF')+';'+(x2||'');
    let pt; if(!pl) pt=''; else if(pl.cultura!==x.cult) pt='Plano de '+pl.cultura+': escolha um plano de '+x.cult; else pt=(na?na+(na>1?' ajustes deste talhão':' ajuste deste talhão'):'')+(x.from?((na?' · ':'')+'copiado de '+x.from):'');
    const lab=x.local||('parcela '+(i+1)); const errs=Object.keys(e).map(k=>e[k]);
    return {i,local:x.local,area:x.area,cult:x.cult,var:x.var,plantio:x.plantio,meta:x.meta,unm:x.unm,plano:pt,temNota:!!pt,pwarn:!!(pl&&pl.cultura!==x.cult),dis:!!dv.ro,lab,
      planoId:x.plano||'', op:planOpts({cult:x.cult,plano:x.plano}), s_plano:set('plano'), st_plano:ist('plano'),
      oc:CULT.map(o=>({v:o,t:o})), ou:UNM.map(o=>({v:o,t:o})),
      s_local:set('local'),s_area:set('area'),s_cult:set('cult'),s_var:set('var'),s_plantio:set('plantio'),s_meta:set('meta'),s_unm:set('unm'),
      st_local:ist('local','font-weight:700;'),st_area:ist('area','text-align:right;'),st_cult:ist('cult'),st_var:ist('var'),st_plantio:ist('plantio'),st_meta:ist('meta','text-align:right;'),st_unm:ist('unm'),
      pst:'font-size:12px;line-height:1.3;color:'+(pl&&pl.cultura!==x.cult?'#B42318':'#5B6660')+';',
      hasErr:errs.length>0,errMsg:errs.join(' · '),ask:!!x.ask,notAsk:!x.ask&&!dv.ro,askMsg:'Excluir '+lab+'? Sai do plano operacional e da demanda.',
      rm:()=>{ const cur=self.state.dv; const y=cur.rows[i]; const tem=!!y.plano||!!(y.id&&Object.keys(adjOf(self)[y.id]||{}).length)||!!Object.keys(y.adj||{}).length;
        if(tem&&!y.ask){ self.setState({dv:upd(i,{ask:true})}); return; } self.setState({dv:Object.assign({},cur,{rows:cur.rows.filter((_,j)=>j!==i),err:{},gerr:'',warn:false})}); },
      rmNo:()=>self.setState({dv:upd(i,{ask:false})}) }; });
  v.dv_add=()=>{ const cur=self.state.dv; const rs=cur.rows.slice(); const last=rs[rs.length-1];
    const usados=rs.map(x=>x.local).concat(leaves(g2rows(self,GR(gid))).filter(c=>c.v.talhao!==t).map(c=>c.v.local));
    const A2=rs.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const livre=r2(T-A2); const area=livre>0.005?String(livre).replace('.',','):'';
    const nw=last?Object.assign({},last,{id:null,local:nextNome(t,usados),area,from:last.local,decl:true,ask:false,adj:(last.id?copyAdj(self,last.id):(last.adj?JSON.parse(JSON.stringify(last.adj)):null))})
                 :{id:null,local:nextNome(t,usados),area,cult:'Soja',var:'',plantio:'',meta:'',unm:'sc/ha',plano:'',colheita:'',adj:null,from:'',decl:true,ask:false};
    rs.push(nw); self.setState({dv:Object.assign({},cur,{rows:rs,warn:false,gerr:''})});
    // inserção repetitiva (UX-ACAO-UNICA-20261003 · DS-33): o foco vai ao nome da parcela nova, à vista e fora do rodapé do painel
    setTimeout(()=>{ try{ const ins=[...document.querySelectorAll('aside[role=dialog] input[aria-label^="Nome da parcela"]')]; const el=ins[ins.length-1]; if(el){ el.focus({preventScroll:true}); el.scrollIntoView({block:'nearest',inline:'nearest'}); } }catch(e){} },60); };
  v.dv_dist=()=>{ const cur=self.state.dv; self.setState({dv:Object.assign({},cur,{rows:dvDist(cur.rows,T),err:{},gerr:'',warn:false})}); };
  v.dv_gerr=dv.gerr||''; v.dv_hasg=!!dv.gerr; v.dv_warn=!!dv.warn;
  const clean=(l)=>JSON.stringify(l.map(x=>Object.assign({},x,{ask:false})));
  const dirty=()=>clean(self.state.dv.rows)!==clean(JSON.parse(self.state.dv.base));
  v.dv_close=()=>{ const cur=self.state.dv; if(cur&&!cur.ro&&dirty()){ self.setState({dv:Object.assign({},cur,{warn:true})}); return; } self.setState({dv:null}); };
  v.dv_discard=()=>self.setState({dv:null}); v.dv_keep=()=>self.setState({dv:Object.assign({},self.state.dv,{warn:false})});
  v.dv_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.dv_close(); } };
  v.dv_save=()=>dvSave(self); }
// próximo passo de uma safra (etapa 1): o que falta primeiro, com o verbo; encerrada só consulta
function semPlano(cs){ return cs.filter(c=>{ const pl=planById(c.v.plano); return !(pl&&pl.cultura===c.v.cult); }); }
// CAL-01 na etapa 6, 2ª linha do estoque apto: quanto dele outras origens usam antes (safra anterior, reserva de outro destino) ou, sem isso, o reservado
function notaEst(d,dec){ return (d.liq>0.001&&d.antes>0.001)?[{k:'br'},{k:'mut',t:'usado antes: '+nf(d.antes,dec)}]:(d.res>0.001?[{k:'br'},{k:'mut',t:'res. '+nf(d.res,dec)}]:[]); }
// solicitações enviadas: as iniciais (D2.sol) + as gravadas no navegador (mesmo registro que Compras lê)
const SOL_KEY='talhao-os-compras-v1';
function solLer(){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); return (o&&o.sols)||{}; }catch(e){ return {}; } }
function solGravar(rec){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null')||{v:1,sols:{}}; o.sols=o.sols||{}; o.sols[rec.safra]=rec; localStorage.setItem(SOL_KEY,JSON.stringify(o)); return true; }catch(e){ return false; } }
function solMap(self){ if(self.state.sol) return self.state.sol; if(!self._sol0) self._sol0=Object.assign({},D2.sol,solLer()); return self._sol0; }
// andamento gravado por Compras (talhao-os-compras-v1 · proc): o planejamento vê em que pé está a compra da mesma solicitação
// SUP §7 (06/10): a situação é a de Compras (estado() em processo_compras), lida daqui; recusa da Direção = nada contratado e a necessidade segue aberta
function solEstado(saf,sol){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); const p=o&&o.proc&&o.proc[saf];
  const e=(p&&sol&&p.sol===sol.id&&(p.comp||0)===(sol.comp||0)&&p.estado&&p.estado!=='A cotar')?p.estado:''; return e==='Recusada'?'Não contratado · necessidade aberta':e; }catch(e){ return ''; } }
function solHref(saf,sol){ return 'CMP.dc.html#sol='+encodeURIComponent(sol.id)+'&saf='+encodeURIComponent(saf); }
function proxSaf(self,r){ if(r.ro) return ['Consultar safra',2];
  const cs=leaves(g2rows(self,GR('g_cult_'+sk(r.id)))); if(!cs.length) return ['Continuar: cadastrar cultivos',2];
  const sp=semPlano(cs).length; if(sp) return ['Continuar: aplicar plano em '+sp+(sp>1?' cultivos':' cultivo'),2];
  if(!solMap(self)[r.id]) return ['Continuar: enviar demanda para cotação',6];
  return ['Continuar: conferir plano operacional',4]; }
function PREVALS(self,v){ compRend(self,self.state.saf||null);
  const st=self.state; const saf=st.saf||null; const safObj=saf?(g2rows(self,GR('g_saf')).find(r=>r.id===saf)):null; const ro=!!(safObj&&safObj.ro);
  // ---- etapa 1: contagens por safra ----
  g2rows(self,GR('g_saf')).forEach(r=>{ const cs=leaves(g2rows(self,GR('g_cult_'+sk(r.id)))); r.v.n=cs.length; r.v.area=cs.reduce((s,c)=>s+(Number(c.v.area)||0),0);
    const est=r.v.estado||'Rascunho'; r.p.estado=[{k:'chip',t:est,c:(est==='Encerrada'?'gray':(est==='Em planejamento'?'green':'yellow'))}].concat(r.id===saf?[{k:'chip',t:'Selecionada',c:'blue'}]:[]);
    r.v.periodo=safPeriodo(r.v.ini,r.v.fim)||r.v.periodo||''; r.p.nome=[{k:'b',t:r.v.nome},{k:'mut',t:r.v.periodo}].concat(r.ro?[]:[{k:'act',t:'Editar',fn:'safedit:'+r.id,lk:true}]); r.s.nome=r.v.nome;
    const px=proxSaf(self,r); r._prox=px[1]; r.dr='open_'+r.id; r.drDup=true;   // o clique na linha repete o botão "Continuar" da linha: uma parada de Tab só (v3.1)
    r.p.acao=[{k:'act',t:px[0],fn:'pickat:'+r.id+'|'+px[1],u:false}]; r.s.acao=px[0]; });
  // ---- etapa 2: partes calculadas do cultivo (plano aplicado, ajustes) ----
  const adj=adjOf(self);
  ['S2627','S27SF','S2526','LG2627','NOVA'].forEach(k=>syncLivres(self,k,v));
  ['S2627','S27SF','S2526','LG2627','NOVA'].forEach(k=>{ g2rows(self,GR('g_cult_'+k)).forEach(r=>{ if(r.livre) return; if(r.grp){ grpParts(r,adj); (r.kids||[]).forEach(c=>leafParts(c,adj,true)); } else leafParts(r,adj,false); }); });
  if(!saf) return;
  // ---- etapa 4: plano operacional ----
  // operação → atividade → cultivo (→ configurações, quando a atividade divide a área entre conjuntos). Grandezas com nomes distintos:
  // horas-conjunto (Σ horas de cada conjunto), decorrido (até terminar a ocorrência, só no cultivo e na configuração), horas-homem (resumo)
  // e horas por máquina/pessoa na etapa 5. Área sem conjunto e ocorrência sem rendimento ficam à vista, com o motivo; nunca viram 0 h.
  const oc=ocorr(self,saf); const byA={};
  oc.forEach(o=>{ const key=o.a.nome+'|'+o.a.op; const g=byA[key]||(byA[key]={id:'A'+Object.keys(byA).length,nome:o.a.nome,op:o.a.op,items:[],mis:{}}); g.items.push(o); g.mis[o.mi]=1; });
  const acts=Object.values(byA); const ini=(its)=>its.map(i=>i.dt).sort()[0]||'';
  acts.sort((x,y)=>{ const a=ini(x.items), b=ini(y.items); return a<b?-1:(a>b?1:0); });
  // operação → atividades → cultivos; operações na ordem da primeira atividade
  const byO={}; acts.forEach(g=>{ const o=byO[g.op]||(byO[g.op]={id:'OP'+Object.keys(byO).length,op:g.op,acts:[],items:[],mis:{}}); o.acts.push(g); o.items=o.items.concat(g.items); Object.assign(o.mis,g.mis); });
  const opsL=Object.values(byO).sort((x,y)=>{ const a=ini(x.items), b=ini(y.items); return a<b?-1:(a>b?1:0); });
  const mlab=(mis)=>{ const ks=Object.keys(mis).map(Number).filter(i=>i>=0).sort((a,b)=>a-b); if(!ks.length) return 'fora do período'; const a=D2.meses[ks[0]][1], b=D2.meses[ks[ks.length-1]][1]; return a===b?a:a+' – '+b; };
  // diesel só soma o que foi informado; sem nenhum conjunto com L/h (gotejo, máquina elétrica) a célula fica vazia, não 0
  const dInf=(i)=>i.rp.itens.some(x=>x.q>0&&x.d!==null);
  // ocorrência pendente não soma 0 h nem R$ 0: com todas pendentes a célula fica vazia (o aviso vermelho diz a causa)
  const soma=(its)=>{ const s=(f)=>its.reduce((t,i)=>t+(Number(i[f])||0),0); const area=s('area'), cop=s('cop'), cins=s('cins'); const tp=its.length>0&&its.every(i=>i.pend);
    return {area,horas:tp?'':s('horas'),dec:'',cop:tp?'':cop,cins,ctot:cop+cins,rha:area?(cop+cins)/area:0,diesel:its.some(dInf)?s('diesel'):''}; };
  // pendências por causa (sem conjunto, sem rendimento, sem horas na janela…): o rótulo diz a causa real, não sempre "sem rendimento"
  const causas=(its)=>{ const o={}; its.forEach(i=>{ if(i.pend){ const c=i.rp.causa||'pendente'; o[c]=(o[c]||0)+1; } }); return o; };
  // avisos da linha: sem rendimento (pendente), área sem conjunto, sequência que não cabe na janela, tarifa desconhecida
  const avisos=(its)=>{ const sal=its.reduce((a,i)=>a+i.saldo,0), np=its.filter(i=>i.pend).length, nc=its.filter(i=>i.rp.conflito).length, nt=its.filter(i=>!i.pend&&!i.rp.custoOk).length; const o=[];
    if(np){ const pc=causas(its); Object.keys(pc).forEach(c=>o.push({k:'chip',t:c+' · '+(its.length>1?pc[c]+(pc[c]>1?' pendentes':' pendente'):'pendente'),c:'red'})); }
    if(sal>1e-9) o.push({k:'chip',t:nfa(sal)+' ha sem conjunto',c:'red'});
    if(nc) o.push({k:'chip',t:its.some(i=>i.rp.conflito&&!i.rp.conflitoEst)?'sequência não cabe na janela':'não cabe na janela nesta estimativa',c:'red'});
    if(nt) o.push({k:'chip',t:'tarifa desconhecida',c:'yellow'}); return o; };
  const ncfg=(its)=>{ const n=its.length?its[0].cfs.length:0; return n>1?[{k:'mut',t:n+' configurações'}]:[]; };
  // necessário × atendido × saldo da ocorrência, com unidades (REND-RETORNO-1818): necessário = atendido + saldo, em ha e em horas-conjunto;
  // o saldo leva as horas pelas premissas do plano (sem nova troca, local ou jornada); pendente nunca vira 0 h
  const hs=(hc,dc)=>' · '+nf(hc,1)+' horas-conjunto · '+nf(dc,1)+' h decorridas';
  const trio=(rp)=>{ const n=rp.nec, f=rp.falta;
    return [{k:'br'},{k:'mut',t:'Necessário: '+nfa(n.area)+' ha'+(n.hconj===null?' · horas pendentes':hs(n.hconj,n.decorrido))},
      {k:'br'},{k:'mut',t:'Atendido: '+nfa(rp.alocado)+' ha'+(rp.pendente?'':hs(rp.hconj,rp.decorrido))},
      {k:'br'},{k:'mut',t:'Saldo: '+nfa(rp.saldo)+' ha'+(f.hconj===null?' · horas pendentes':' · faltam '+hs(f.hconj,f.decorrido).slice(3))+(f.hconj!==null&&f.semHoras>1e-9?' ('+nfa(f.semHoras)+' ha sem horas calculáveis)':'')}]; };
  const linhaCfg=(id,i,x,j)=>{ const fixo=x.p!==null; const sem=x.r===null;
    const r={id:id+'_c'+j,ro:true,v:{nome:x.nome,gat:'',data:'',tal:'',mes:'',area:x.q,horas:sem?'':x.h,dec:(sem||!x.q)?'':x.ht,cop:(x.custo===null||sem)?'':x.custo,cins:'',ctot:'',rha:(x.q>0&&x.custo!==null)?x.custo/x.q:'',diesel:(x.diesel===null||!x.q)?'':x.diesel},s:{nome:x.nome},p:{}};
    r.p.nome=[{k:'txt',t:x.nome}].concat(sem?[{k:'chip',t:'sem rendimento',c:'red'}]:[]).concat(x.emSeq?[{k:'chip',t:x.seqEst?'em sequência nesta estimativa':'em sequência',c:'yellow'}]:[]);
    // TABELAS-FOCO: parte e janela da configuração em colunas próprias (antes ficavam na coluna do gatilho)
    { const jh=(x.Hin!==undefined?x.Hin:x.H); r.v.part=fixo?x.p:''; r.p.part=[{k:fixo?'txt':'mut',t:fixo?nfa(x.p):'pelo rendimento'}]; r.s.part=fixo?nfa(x.p):'pelo rendimento';
      r.v.jan=jh!==Infinity?jh:''; r.p.jan=jh!==Infinity?[{k:'txt',t:nfa(jh)}]:[{k:'mut',t:'—'}]; }
    r.p.gat=[{k:'mut',t:''}]; r.s.gat=''; r.p.mes=[{k:'mut',t:''}];
    // a área da linha é o atendido; quando falta, a parte da demanda inteira (necessário) e o saldo dela, com as horas
    if(x.fq>1e-9) r.p.nome=r.p.nome.concat([{k:'br'},{k:'mut',t:'precisa de '+nfa(x.nq)+' ha = '+nf(x.nh,1)+' h · faltam '+nfa(x.fq)+' ha = '+nf(x.fh,1)+' h'}]);
    if(x.q>0&&x.ht>x.h+1e-9) r.p.dec=[{k:'txt',t:nf(x.ht,1)},{k:'br'},{k:'mut',t:'com '+nfa(x.ht-x.h)+' h de troca'}];
    return r; };
  const linhaOc=(g,i,ix)=>{ const id=g.id+'_'+ix; const rp=i.rp; const multi=i.cfs.length>1;
    const r={id,ro:true,v:{nome:i.c.v.local+' · '+i.c.v.cult+' '+i.c.v.var,gat:'',tal:i.c.v.local,mes:(i.mi>=0?D2.meses[i.mi][1]:'fora do período'),area:i.area,horas:i.pend?'':i.horas,dec:(i.pend||rp.alocado<=0)?'':i.dec,
      cop:i.pend?'':i.cop,cins:i.cins,ctot:i.cop+i.cins,rha:i.area?(i.cop+i.cins)/i.area:0,diesel:dInf(i)?i.diesel:''},s:{},p:{}}; dcol(r,'data',i.dt);
    const avs=avisos([i]); if(avs.length||multi) r.p.nome=[{k:'txt',t:r.v.nome}].concat(multi?[{k:'mut',t:i.cfs.length+' configurações'}]:[]).concat(avs)
      .concat((i.pend||i.saldo>1e-9||rp.conflito||rp.itens.some(x=>x.emSeq))&&rp.motivos.length?[{k:'br'},{k:'mut',t:rp.motivos.join(' · ')}]:[]);
    if(rp.saldo>1e-9) r.p.nome=(r.p.nome||[{k:'txt',t:r.v.nome}]).concat(trio(rp));
    if(rp.saldo>1e-9&&!i.pend) r.p.dec=[{k:'txt',t:nf(i.dec,1)},{k:'br'},{k:'mut',t:'só da parte com conjunto'}];
    if(multi) r.kids=rp.itens.map((x,j)=>linhaCfg(id,i,x,j));
    return r; };
  const linhaAtv=(g)=>{ const gs=[...new Set(g.items.map(i=>gatLabel(i.a.g)))];
    return {id:g.id,v:Object.assign({nome:g.nome,gat:gs.join(', '),data:'',tal:'',mes:mlab(g.mis)},soma(g.items)),s:{},p:{nome:[{k:'txt',t:g.nome}].concat(ncfg(g.items)).concat(avisos(g.items))},
      kids:g.items.slice().sort((a,b)=>a.dt<b.dt?-1:1).map((i,ix)=>linhaOc(g,i,ix))}; };
  GR('g_op').rows=opsL.map(o=>{ const n=o.acts.length;
    return {id:o.id,v:Object.assign({nome:o.op,gat:'',data:'',tal:'',mes:mlab(o.mis)},soma(o.items)),s:{nome:o.op},p:{nome:[{k:'b',t:o.op},{k:'mut',t:n+(n>1?' atividades':' atividade')}].concat(avisos(o.items)),gat:[{k:'mut',t:''}]},kids:o.acts.map(linhaAtv)}; });
  const selO=st.atv? opsL.find(o=>o.id===st.atv):null; const selA=(!selO&&st.atv)? acts.find(a=>a.id===st.atv):null; const base=selO?selO.items:(selA?selA.items:oc);
  const vis0=st.opv==='mes'?'mes':'op'; const M=D2.meses.length; const z=()=>new Array(M).fill(0); const mat={area:z(),horas:z(),cop:z(),cins:z(),diesel:z()};
  base.forEach(i=>{ if(i.mi<0) return; mat.area[i.mi]+=i.area; mat.horas[i.mi]+=i.horas; mat.cop[i.mi]+=(i.cop||0); mat.cins[i.mi]+=i.cins; mat.diesel[i.mi]+=(i.diesel||0); });
  const mrow=(id,l,arr,d)=>{ const r={id,v:{ind:l,tot:arr.reduce((a,b)=>a+b,0)},s:{},p:{}}; arr.forEach((x,ix)=>{ r.v['m'+ix]=x; });
    if(d==='ha'){ arr.forEach((x,ix)=>{ if(x) r.p['m'+ix]=[{k:'txt',t:nfa(x)}]; }); if(r.v.tot) r.p.tot=[{k:'txt',t:nfa(r.v.tot)}]; }   // área com até 2 casas (PRE-REV R7)
    return r; };
  const ctot=mat.cop.map((x,i)=>x+mat.cins[i]);
  GR('g_mat').rows=[mrow('ma','Área trabalhada (ha)',mat.area,'ha'),mrow('mh','Horas-conjunto (h)',mat.horas),mrow('mo','Custo de operação (R$)',mat.cop),mrow('mi','Custo de insumos (R$)',mat.cins),mrow('mt','Custo total (R$)',ctot),mrow('md','Diesel estimado (L)',mat.diesel)];
  v.mat_titulo=selO?('Detalhamento mensal · '+selO.op):(selA?('Detalhamento mensal · '+selA.nome):'Detalhamento mensal · todas as operações da safra'); v.mat_sel=!!(selO||selA);
  v.mat_nome=selO?selO.op:(selA?selA.nome+' ('+selA.op+')':'');
  const vis=st.opv==='mes'?'mes':'op'; v.vis_op=vis==='op'; v.vis_mes=vis==='mes';
  const segSt=(on)=>'font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;border:0;cursor:pointer;'+(on?'background:#1E7A4C;color:#fff;':'background:transparent;color:#15201A;');
  v.vis_op_st=segSt(v.vis_op); v.vis_mes_st=segSt(v.vis_mes); v.ver_op=()=>self.setState({opv:'op'}); v.ver_mes=()=>self.setState({opv:'mes'});
  v.op_titulo=v.vis_op?'Plano operacional por operação':('Plano operacional por mês · '+(v.mat_sel?v.mat_nome:'todas as operações')); v.mat_todas=()=>self.setState({atv:null});
  const S=(f)=>oc.reduce((a,i)=>a+(Number(i[f])||0),0); const TA=S('area'), TH=S('horas'), TC=S('cop')+S('cins'), THH=S('hh'), TD=S('diesel'), TS=S('saldo'), NP=oc.filter(i=>i.pend).length, NC=oc.filter(i=>i.rp.conflito&&!i.rp.conflitoEst).length, NCE=oc.filter(i=>i.rp.conflito&&i.rp.conflitoEst).length;
  // necessário = atendido + saldo também nos totais (etapas 4 e 5): horas-conjunto necessárias, que faltam e área sem horas calculáveis
  const TF=oc.reduce((a,i)=>a+(i.rp.falta.hconj||0),0), TN=oc.reduce((a,i)=>a+(i.rp.nec.hconj||0),0), TSH=oc.reduce((a,i)=>a+i.rp.falta.semHoras,0);
  const semHtxt=TSH>1e-9?' ('+nfa(TSH)+' ha sem horas calculáveis)':'';
  const areaSaf=cultRows(self,saf).reduce((a,c)=>a+(Number(c.v.area)||0),0);
  v.k4=nfa(TA)+' ha trabalhados · '+nf(TH)+' horas-conjunto · '+nf(THH)+' horas-homem · '+nf(TD)+' L de diesel · '+rs(TC)+' · '+rs(areaSaf?TC/areaSaf:0)+'/ha da safra'
    +(TS>1e-9?' · dos '+nfa(TA)+' ha, '+nfa(TS)+' ha sem conjunto, fora das horas-conjunto: faltam '+nf(TF,1)+' horas-conjunto'+semHtxt:'')+(NP?' · '+NP+(NP>1?' ocorrências pendentes':' ocorrência pendente')+' ('+(()=>{ const pc=causas(oc); const ks=Object.keys(pc); return ks.length===1?ks[0]:ks.map(c=>pc[c]+' '+c).join(', '); })()+')':'')+(NC?' · '+NC+(NC>1?' sequências não cabem na janela':' sequência não cabe na janela'):'')+(NCE?' · '+NCE+(NCE>1?' sequências não cabem na janela nesta estimativa':' sequência não cabe na janela nesta estimativa'):'')
    +(vis0==='mes'?'':' · clique numa linha para ver os meses dela');
  // ---- etapa 5: recursos ----
  const recpM=g2rows(self,GR('g_recp_maq')), recpP=g2rows(self,GR('g_recp_pes')); const recp=recpM.concat(recpP);
  const cls=st.rcl==='pes'?'pes':'maq'; const daClasse=(id)=>(cls==='pes')===recpP.some(r=>r.id===id);
  const dem={}; recp.forEach(r=>{ dem[r.id]=z(); });
  const demA={}; oc.forEach(i=>{ if(i.mi<0) return; Object.keys(i.rec||{}).forEach(k=>{ if(!dem[k]) return; const h=i.horas*i.rec[k]; dem[k][i.mi]+=h; const dk=k+'|'+i.a.nome; (demA[dk]||(demA[dk]=z()))[i.mi]+=h; }); });
  let faltas=0;
  GR('g_res').rows=recp.map(r=>{
    // horas de uma unidade no mês = dias úteis × jornada × turnos × fator; capacidade = unidades × esse valor
    // fator: máquinas = disponibilidade (%); pessoas = 1 − absenteísmo (%)
    const pes=recpP.some(x=>x.id===r.id); const ul=pes?'pessoas':'unidades';
    const pc=k=>Math.min(100,Math.max(0,Number(r.v[k])||0))/100;
    const un=Number(r.v.un)||0, J=Number(r.v.jornada)||0, T=pes?1:(Number(r.v.turnos)||0), DP=pes?1-pc('abs'):pc('disp');
    const porUn=D2.meses.map(m=>(D2.dias[m[0]]||0)*J*T*DP); const cap=porUn.map(p=>un*p);
    const d=dem[r.id]; const sal=cap.map((c,i)=>c-d[i]);
    // horas → quantidade: necessárias = demanda ÷ horas de uma unidade, arredondado para cima (−1 = sem horas no mês)
    const nec=d.map((h,i)=>h>0.0001?(porUn[i]>0?Math.ceil(h/porUn[i]-1e-9):-1):0); const row={id:'R_'+r.id,v:{ind:r.v.nome},s:{ind:r.v.nome},p:{ind:[{k:'b',t:r.v.nome},{k:'mut',t:'saldo (h)'}]},kids:[],_f:0};
    sal.forEach((x,i)=>{ row.v['m'+i]=x; const neg=nec[i]<0||nec[i]>un; if(neg){ faltas++; row._f++; } row.p['m'+i]=[{k:'cn',t:(x>=0?'+':'−')+nf(Math.abs(x),(neg&&Math.abs(x)<1)?1:0),c:(neg?'red':(d[i]>0?'green':'gray'))}]; row.s['m'+i]=x; });
    const tS=sal.reduce((a,b)=>a+b,0); row.v.tot=tS; row.p.tot=[{k:'b',t:(tS>=0?'+':'−')+nf(Math.abs(tS))+' h'}];
    const kid=(id,l,arr)=>{ const k={id,ro:true,v:{ind:l,tot:arr.reduce((a,b)=>a+b,0)},s:{},p:{}}; arr.forEach((x,i)=>{ k.v['m'+i]=x; }); return k; };
    const kn={id:r.id+'_n',ro:true,v:{ind:'Necessárias ('+ul+')'},s:{},p:{}}; let pico=0, mp=-1;
    nec.forEach((n,i)=>{ kn.v['m'+i]=n<0?'':n; if(n<0){ kn.p['m'+i]=[{k:'cn',t:'sem horas',c:'red'}]; } else if(n>un){ kn.p['m'+i]=[{k:'cn',t:String(n),c:'red'}]; } if(n>pico){ pico=n; mp=i; } });
    kn.v.tot=pico; kn.p.tot=[{k:'b',t:'pico '+pico}];
    const ku={id:r.id+'_u',ro:true,v:{ind:'Você tem ('+ul+')',tot:un},s:{},p:{tot:[{k:'txt',t:String(un)}]}}; D2.meses.forEach((m,i)=>{ ku.v['m'+i]=un; });
    row.kids=[kid(r.id+'_d','Demanda (h)',d),kid(r.id+'_c','Capacidade (h)',cap),kn,ku];
    // parâmetros: pico de necessidade e o mês em que acontece, ao lado do que existe
    r.v.pico=pico; r.p.pico=[pico>un?{k:'cn',t:String(pico),c:'red'}:{k:'b',t:String(pico)}]; r.s.pico=String(pico);
    r.v.mpico=mp>=0?D2.meses[mp][1]:'—'; r.p.mpico=[{k:mp>=0?'txt':'mut',t:r.v.mpico}]; r.s.mpico=r.v.mpico;
    return row; });
  const todas=GR('g_res').rows; const fM=todas.filter(r=>recpM.some(x=>'R_'+x.id===r.id)).reduce((a,r)=>a+r._f,0), fP=faltas-fM;
  GR('g_res').rows=todas.filter(r=>daClasse(String(r.id).replace('R_','')));
  // o aviso diz quanto falta em quantidade, não só em meses
  const curtos=recp.filter(r=>(Number(r.v.pico)||0)>(Number(r.v.un)||0)).map(r=>r.v.nome+': precisa de '+r.v.pico+', tem '+(Number(r.v.un)||0)+' em '+r.v.mpico);
  const fora=TS>1e-9?('A demanda não inclui '+nfa(TS)+' ha sem conjunto'+(NP?' ('+NP+(NP>1?' ocorrências pendentes':' ocorrência pendente')+')':'')
    +': conta '+nf(TH,1)+' das '+nf(TN,1)+' horas-conjunto necessárias, faltam '+nf(TF,1)+semHtxt+'; defina rendimento e janela na etapa 3 · '):'';
  v.k5=fora+(faltas?((curtos.length?curtos.join(' · '):(fM+fP)+' mês(es) com falta')+' — em vermelho na visão por mês'):'Capacidade atende a demanda'+(fora?' calculada':'')+' em todos os meses');
  const rv=st.rv==='mes'?'mes':'par'; v.vis_par=rv==='par'; v.vis_rmes=rv==='mes'; v.cl_maq=cls==='maq'; v.cl_pes=cls==='pes';
  const sg=(on)=>'font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;border:0;cursor:pointer;white-space:nowrap;'+(on?'background:#1E7A4C;color:#fff;':'background:transparent;color:#15201A;');
  v.vis_par_st=sg(v.vis_par); v.vis_rmes_st=sg(v.vis_rmes); v.cl_maq_st=sg(v.cl_maq); v.cl_pes_st=sg(v.cl_pes);
  v.ver_par=()=>self.setState({rv:'par'}); v.ver_rmes=()=>self.setState({rv:'mes'}); v.ver_maq=()=>self.setState({rcl:'maq',rec:null}); v.ver_pes=()=>self.setState({rcl:'pes',rec:null});
  v.rec_titulo=(cls==='pes'?'Pessoas':'Máquinas e implementos')+(rv==='mes'?' · demanda × capacidade por mês':' · parâmetros');
  v.rec_sub=rv==='mes'?'Faltas em vermelho; clique num recurso para ver de onde vem a demanda.':('Clique num recurso para ajustar o que você tem; necessárias = horas da demanda ÷ horas de '+(cls==='pes'?'uma pessoa':'uma unidade')+' no mês.');
  v.k5st=faltas?'color:#B42318;font-weight:700;':(fora?'color:#8A5A00;font-weight:700;':'color:#1E7A4C;font-weight:700;');
  const selR=(st.rec&&daClasse(st.rec))?st.rec:null; v.resd_sel=!!selR; v.resd_titulo=selR?('Origem da demanda · '+((recp.find(r=>r.id===selR)||{v:{}}).v.nome||'')):'';
  GR('g_resd').rows=selR?Object.keys(demA).filter(k=>k.indexOf(selR+'|')===0).map((k,ix)=>{ const r={id:'D'+ix,v:{ind:k.split('|')[1],tot:demA[k].reduce((a,b)=>a+b,0)},s:{},p:{}}; demA[k].forEach((x,i)=>{ r.v['m'+i]=x; }); return r; }):[];
  // ---- etapa 6: demanda de insumos ----
  const dm=demanda(self,saf); const sol=solMap(self)[saf]; const grupos={};
  Object.values(dm).forEach(d=>{ (grupos[d.grupo]||(grupos[d.grupo]=[])).push(d); });
  let tot=0, nliq=0, npend=0;
  GR('g_dem').rows=Object.keys(grupos).sort((a,b)=>a.localeCompare(b,'pt-BR')).map((g,gi)=>{ const its=grupos[g].sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR'));
    const val=its.reduce((a,d)=>a+d.valor,0); tot+=val; const uso=its.map(d=>d.uso).filter(Boolean).sort()[0]||'';
    // TABELAS-FOCO (5983172395): uma variável por coluna — grupo, insumo, quantidades (com a unidade junto), datas, situação, solicitação e complemento próprios
    const gr={id:'G'+gi,v:{grp:g,ins:'',valor:val},s:{grp:g,ins:''},p:{grp:[{k:'b',t:g}],ins:[{k:'mut',t:its.length+(its.length>1?' insumos':' insumo')}]},
      kids:its.map((d,ix)=>{ const dec=(d.un==='L')?1:0; const sent=sol&&sol.itens?(sol.itens[d.nome]||0):0; if(d.liq>0) nliq++;
        let sit, sid=''; if(d.liq<=0.001&&d.rup>0.001) sit={k:'chip',t:'Coberto pelo recebimento',c:'yellow'}; else if(d.liq<=0.001) sit={k:'chip',t:'Coberto pelo estoque',c:'green'}; else if(sol && sent>=d.liq-0.01){ sit={k:'chip',t:'Em cotação',c:'blue'}; sid=sol.id; } else if(sol){ sit={k:'chip',t:'Complemento',c:'yellow'}; sid=sol.id; npend++; } else { sit={k:'chip',t:'A enviar',c:'gray'}; npend++; }
        // decisão do proprietário (05/10/2026): a unidade fica junto do valor ("62.500 kg"); o valor tipado (v) continua número para ordenar e filtrar
        const qt=(x)=>nf(x,dec)+' '+d.un, q=(x)=>[{k:'txt',t:qt(x)}], z=(x)=>x>0.001?[{k:'txt',t:qt(x)}]:[{k:'mut',t:'—'}];
        const kr={id:'G'+gi+'_'+ix,ro:true,v:{grp:d.grupo,ins:d.nome,bruta:d.bruta,real:(d.real>0.001?d.real:''),est:d.est,antes:(d.liq>0.001&&d.antes>0.001?d.antes:''),res:(!(d.liq>0.001&&d.antes>0.001)&&d.res>0.001?d.res:''),
               rec:d.rec,tarde:((d.liq>0.001||d.rup>0.001)&&d.tarde>0.001?d.tarde:''),liq:d.liq,un:d.un,preco:d.preco,valor:d.valor,sol:sid,comp:(sit.t==='Complemento'?d.liq-sent:'')},s:{sit:sit.t,sol:sid},
          p:{grp:[{k:'mut',t:d.grupo}],bruta:q(d.bruta),real:z(d.real),est:q(d.est),antes:z(d.liq>0.001?d.antes:0),res:z((d.liq>0.001&&d.antes>0.001)?0:d.res),rec:q(d.rec),
             tarde:z(((d.liq>0.001||d.rup>0.001)&&d.tarde>0.001)?d.tarde:0),liq:[{k:'b',t:qt(d.liq)}],sit:[sit],sol:sid?[{k:'txt',t:sid}]:[{k:'mut',t:'—'}],
             comp:sit.t==='Complemento'?q(d.liq-sent):[{k:'mut',t:'—'}],preco:[{k:'txt',t:rs(d.preco)+'/'+d.un}]},
          o:d.memo.map(t=>({t})).concat(sol?[{t:'Ver '+sol.id+' em Compras',h:solHref(saf,sol)}]:[]) }; dcol(kr,'uso',d.uso);
        // filtro e busca leem o mesmo texto da célula (com a unidade)
        ['bruta','real','est','antes','res','rec','tarde','liq','comp','preco'].forEach(f=>{ const c=kr.p[f]&&kr.p[f][0]; kr.s[f]=(c&&c.t!=='—')?c.t:''; });
        // falta: quando o estoque acaba (com necessidade líquida ou só ruptura coberta por recebimento); coberta em: o recebimento que cobre a ruptura
        dcol(kr,'falta',(d.liq>0.001||d.rup>0.001)?d.falta:''); if(kr.s.falta) kr.p.falta=[{k:'cn',t:kr.s.falta,c:'red'}]; dcol(kr,'cob',(d.liq<=0.001&&d.rup>0.001)?d.cob:''); return kr; })};
    // situação do grupo: contagem por situação dos insumos (o que falta enviar primeiro)
    const cnt={}; gr.kids.forEach(k=>{ const t=String(k.s.sit||'').replace(/ · .*/,'').replace(/^Complemento.*/,'Complemento'); cnt[t]=(cnt[t]||0)+1; });
    const ord=['A enviar','Complemento','Em cotação','Coberto pelo recebimento','Coberto pelo estoque']; const cor={'A enviar':'gray','Complemento':'yellow','Em cotação':'blue','Coberto pelo recebimento':'yellow','Coberto pelo estoque':'green'};
    gr.p.sit=ord.filter(t=>cnt[t]).map(t=>({k:'chip',t:cnt[t]+' '+(t==='Coberto pelo estoque'?'coberto'+(cnt[t]>1?'s':''):(t==='Coberto pelo recebimento'?'coberto'+(cnt[t]>1?'s':'')+' pelo recebimento':t.toLowerCase())),c:cor[t]})); gr.s.sit='';
    ['bruta','real','est','antes','res','rec','tarde','liq','falta','cob','preco','sol','comp'].forEach(f=>{ gr.p[f]=[{k:'mut',t:''}]; gr.s[f]=''; });
    dcol(gr,'uso',uso); return gr; });
  const est=sol?solEstado(saf,sol):'';
  v.k6='Valor da necessidade líquida '+rs(tot)+' · '+nliq+' insumos a comprar'+(sol?(' · solicitação '+sol.id+(est?' · '+est:' em cotação')+(sol.comp?' (+'+sol.comp+' complemento'+(sol.comp>1?'s':'')+')':'')):' · ainda não enviada');
  v.k6pend=npend; v.sol_link=!!sol; v.sol_id=sol?sol.id:''; v.sol_href=sol?solHref(saf,sol):'CMP.dc.html';
}
function EXTRAVALS(self,v){
  const st=self.state; const step=st.step||1; const saf=st.saf||null;
  const safRows=g2rows(self,GR('g_saf')); const safObj=saf?safRows.find(r=>r.id===saf):null; const ro=!!(safObj&&safObj.ro);
  for(let i=1;i<=6;i++) v['s'+i]=(step===i);
  const temPlano=saf && cultRows(self,saf).some(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; });
  const whys={}; for(let i=2;i<=6;i++){ if(!saf) whys[i]='Escolha a safra'; else if(i>=4 && !temPlano) whys[i]='Aplique um plano'; }
  g2steps(self,v,'stp',6,step,whys);   // só informa (UX-ACAO-UNICA-20261003): avanço e retorno na área de ações
  v.saf_nome=safObj?safObj.v.nome:'nenhuma safra escolhida'; v.saf_ro=ro; v.saf_ok=!!saf; v.saf_none=!saf;
  v.ctx_saf=safObj?(safObj.v.nome+(ro?' · consulta':'')):'Nenhuma safra escolhida';
  v.ctx_faz='Fazenda '+((safObj&&safObj.v.faz)||'Santa Rita');
  for(const k of ['S2627','S27SF','S2526','LG2627','NOVA']){ v['cult_'+k]=(saf&&sk(saf)===k); v['rend_'+k]=(saf&&sk(saf)===k); }
  const cs=cultRows(self,saf); const area=cs.reduce((a,c)=>a+(Number(c.v.area)||0),0); const comp=cs.filter(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; }).length;
  const adj=adjOf(self); const naj=cs.reduce((a,c)=>a+Object.keys(adj[c.id]||{}).length,0);
  const sp=semPlano(cs);
  v.k2=cs.length+' cultivos · '+nf(area)+' ha · '+comp+' com plano'+(sp.length?' · '+sp.length+' sem plano':'')+' · '+naj+(naj===1?' ajuste local':' ajustes locais');
  // ação primária por etapa: nomeia o próximo passo (na etapa 2, o que falta: aplicar plano; depois, avançar)
  const cultSp={}; sp.forEach(c=>{ (cultSp[c.v.cult]||(cultSp[c.v.cult]=[])).push(c.id); }); const cuK=Object.keys(cultSp).sort((a,b)=>cultSp[b].length-cultSp[a].length)[0];
  const apIds=cuK?cultSp[cuK]:[]; const apT='Aplicar plano em '+apIds.length+(apIds.length>1?' cultivos':' cultivo')+(Object.keys(cultSp).length>1?' de '+cuK.toLowerCase():'');
  const solA=saf?solMap(self)[saf]:null; const enviado=!!solA;
  // SUP §7 (06/10): o atalho nomeia a solicitação que abre em Compras (antes "Abrir Compra de insumos ›")
  const p6=(enviado&&!v.k6pend)?{t:'Abrir '+solA.id+' ›',h:solHref(saf,solA),a:'abrir'}:{t:'Enviar para cotação',fn:()=>enviar(self),a:'comando'};
  v.sol_link=v.sol_link&&!p6.h;   // "Abrir em Compras ›" do bloco só quando a primária é enviar (complemento pendente): sem cópia do mesmo link
  safAcoes(self,v,{step,saf,ro,cs,sp,apIds,apT,cultSp,temPlano,p6});
  // escolher safra (botão da linha)
  v.pick=(id)=>{ g2etapa(self,{saf:id,step:2,atv:null,rec:null,corr:null,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')}); };
  v.pickat=(arg)=>{ const a=String(arg).split('|'); const id=a[0], s=Number(a[1])||2; g2etapa(self,{saf:id,step:s,atv:null,rec:null,corr:null,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')+' · etapa '+s}); };
  safRows.forEach(r=>{ v['open_'+r.id]=()=>v.pickat(r.id+'|'+(r._prox||2)); });
  v.safedit=(id)=>{ const sp=GR('g_saf'); const r=g2rows(self,sp).find(x=>x.id===id); if(!r) return; const dr=r.dr; r.dr=null; g2open(self,sp,id,null); r.dr=dr; };
  v.applyone=(cid)=>openApply(self,[cid]); v.openlp=(cid)=>openLP(self,cid);
  Object.keys(D2.talhoes||{}).forEach(t=>{ v['div_'+t]=()=>openDiv(self,t); }); v.divide=(t)=>openDiv(self,t);
  // painéis
  apVals(self,v); lpVals(self,v); divVals(self,v);
  // SAF.dc.html#saf=S27SF&etapa=6 (vindo da Compra de insumos): abre a safra na etapa pedida, uma vez e a cada troca de endereço
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const ms=/[#&]saf=([^&]+)/.exec(h), me=/[#&]etapa=(\d)/.exec(h); if(!ms) return;
    const r=g2rows(self,GR('g_saf')).find(x=>x.id===ms[1]); if(!r) return; const e=Math.min(6,Math.max(1,Number(me&&me[1])||6));
    setTimeout(()=>self.setState({saf:r.id,step:e,atv:null,rec:null,g2toast:'Safra aberta: '+r.v.nome+' · etapa '+e}),0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
}
// ---- UX-ACAO-UNICA-20261003 · área de ações do Planejar safra (DS-02, DS-33 §74.5.7.1, DS-61) ----
// Uma primária e uma rota de avanço por etapa; a faixa só informa. Retorno secundário nomeia a etapa anterior (na etapa 2, voltar à
// escolha é o "Trocar safra" do topo: sem cópia aqui). Pendência mostra a causa e um passo que resolve (Aplicar plano), sem aplicar e
// avançar em silêncio. Avançar só troca de etapa: não envia cotação, não publica, não aprova. Na revisão (etapa 6), "Corrigir cultivos"
// leva aos cultivos sem plano e "Voltar à revisão" devolve à mesma posição, com filtros e rascunho da tela preservados (estado).
const SAF_CURTO=['Escolha da safra','Cultivos e planos','Rendimentos','Plano operacional','Recursos','Demanda de insumos'];
function safMaior(cs){ const by={}; cs.forEach(c=>{ (by[c.v.cult]||(by[c.v.cult]=[])).push(c.id); }); const k=Object.keys(by).sort((a,b)=>by[b].length-by[a].length)[0]; return k?{ids:by[k],cult:k,mix:Object.keys(by).length>1}:{ids:[],cult:'',mix:false}; }
function safAplicarT(m){ return 'Aplicar plano em '+m.ids.length+(m.ids.length>1?' cultivos':' cultivo')+(m.mix?' de '+m.cult.toLowerCase():''); }
function safLocs(cs){ return cs.slice(0,4).map(c=>c.v.local).join(', ')+(cs.length>4?' e mais '+(cs.length-4):''); }
function safRolagem(){ const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div');
  return (col&&col.scrollHeight>col.clientHeight+1&&getComputedStyle(col).overflowY==='auto')?col:m; }
function safCorrigir(self,ids){ const r=safRolagem(); const m=document.querySelector('main[data-scroll]');
  self.__revPos={top:r?r.scrollTop:0,rolas:m?[...m.querySelectorAll('.g2rola,.rola')].map(x=>x.scrollTop):[],foco:'[data-acoes] [data-acao=corrigir]'};
  g2etapa(self,{step:2,corr:{ids:ids.slice()}});
  setTimeout(()=>{ try{ const row=document.querySelector('[role=row][data-rid="'+ids[0]+'"]'); if(row){ row.scrollIntoView({block:'center'}); row.focus({preventScroll:true}); } }catch(e){} },120); }
function nSel(self,saf){ return Object.values((g2st(self,'g_cult_'+sk(saf)).sel)||{}).filter(Boolean).length; }
function safAcoes(self,v,x){ const st=self.state, step=x.step, ro=x.ro, corr=st.corr||null;
  const ir=(i)=>({t:'‹ '+SAF_CURTO[i-1],fn:()=>g2etapa(self,{step:i,corr:null}),to:i,a:'voltar'});
  const av=(i,t)=>({t:t+' ›',fn:()=>g2etapa(self,{step:i,corr:null}),to:i,a:'avancar'});
  const aplicar={t:x.apT,fn:()=>openApply(self,x.apIds),a:'resolver'};
  const nSp=x.sp.length; const semTxt=nSp+(nSp>1?' cultivos sem plano agronômico':' cultivo sem plano agronômico')+' ('+safLocs(x.sp)+')';
  // Adicionar cultivo: uma instância junto da lista; primária só com a lista vazia (é a única ação da etapa)
  v.add_fn=()=>{ const f=v['g_cult_'+sk(x.saf)+'_new']; if(f) f(); };
  v.add_prim=step===2&&!!x.saf&&!ro&&!x.cs.length; v.add_sec=step===2&&!!x.saf&&!ro&&x.cs.length>0;
  let c={};
  if(step===1) c={};   // escolher é a ação da linha ("Próximo passo"); criar fica junto do título da lista
  else if(!x.saf) c={nota:'Nenhuma safra escolhida: escolha a safra para seguir.',prim:{t:'‹ Escolher a safra',fn:()=>g2etapa(self,{step:1}),to:1,a:'voltar'}};
  else if(step===2){
    if(corr){ const pend=x.sp.filter(c=>corr.ids.indexOf(c.id)>=0); const m=safMaior(pend);
      const volta={t:'Voltar à revisão ›',fn:()=>{ const pos=self.__revPos||null; self.__revPos=null; g2etapa(self,{step:6,corr:null},pos); },to:6,a:'avancar'};
      c=pend.length?{nota:'Correção pedida pela revisão: '+pend.length+(pend.length>1?' cultivos sem plano':' cultivo sem plano')+' ('+safLocs(pend)+').',prim:{t:safAplicarT(m),fn:()=>openApply(self,m.ids),a:'resolver'},sec:volta}
                   :{nota:'Cultivos corrigidos: volte à revisão para conferir a demanda.',prim:volta}; }
    else if(ro) c={prim:av(3,'Ver rendimentos')};
    else if(!x.cs.length) c={nota:'Nenhum cultivo nesta safra: adicione o primeiro para definir rendimentos e o plano operacional.'};
    else if(nSel(self,x.saf)) c={nota:(nSp?semTxt+'. ':'')+'Seleção ativa: o plano dos selecionados é aplicado pela barra da lista.',sec:av(3,'Definir rendimentos')};   // lote = comando da tarefa ativa (DS-02/DS-40): sem 2ª primária de "aplicar"
    else if(x.apIds.length) c={nota:semTxt+': sem plano não entram operações nem insumos.',prim:aplicar,sec:av(3,'Definir rendimentos')};
    else c={prim:av(3,'Definir rendimentos')}; }
  else if(!ro&&step>=3&&!x.temPlano&&step<6) c={volta:ir(step-1),nota:'Nenhum cultivo tem plano agronômico: o plano operacional, os recursos e a demanda dependem dele.',prim:x.apIds.length?aplicar:null};
  else if(step===3) c={volta:ir(2),prim:av(4,ro?'Ver plano operacional':'Conferir plano operacional')};
  else if(step===4) c={volta:ir(3),prim:av(5,ro?'Ver recursos':'Dimensionar recursos')};
  else if(step===5) c={volta:ir(4),prim:av(6,ro?'Ver demanda de insumos':'Conferir demanda de insumos')};
  else if(step===6){ c={volta:ir(5)};
    if(!ro){ c.prim=x.p6; if(nSp){ c.nota=semTxt+' ficam fora desta demanda.'; c.ctx={t:'Corrigir cultivos',fn:()=>safCorrigir(self,x.sp.map(r=>r.id))}; } } }
  g2acoes(v,'aa',c); }
function openApply(self,ids){ const saf=self.state.saf; if(!saf){ self.setState({g2toast:'Escolha a safra primeiro.'}); return; }
  const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); if(safObj&&safObj.ro){ self.setState({g2toast:'Safra encerrada: somente consulta.'}); return; }
  const gsel=(g2st(self,'g_cult_'+sk(saf)).sel)||{}; const all=g2rows(self,GR('g_cult_'+sk(saf)));
  const sel=[...new Set([].concat(...(ids||Object.keys(gsel).filter(k=>gsel[k]&&k.indexOf('livre_')!==0)).map(id=>{ const r=g2find(all,id); return (r&&r.grp)?(r.kids||[]).map(k=>k.id):[id]; })))];
  if(!sel.length){ self.setState({g2toast:'Selecione cultivos na caixa à esquerda de cada linha para aplicar um plano em lote.'}); return; }
  // sugestão: o plano mais usado pela mesma cultura nesta safra (a pessoa pode trocar)
  const cs=cultRows(self,saf); const cu=(cs.find(c=>c.id===sel[0])||{v:{}}).v.cult; const uso={};
  cs.forEach(c=>{ const pl=planById(c.v.plano); if(pl&&pl.cultura===cu&&c.v.cult===cu) uso[c.v.plano]=(uso[c.v.plano]||0)+1; });
  const sug=Object.keys(uso).sort((a,b)=>uso[b]-uso[a])[0]||'';
  self.setState({ap:{ids:sel,plan:sug,confirm:false}}); }
function apVals(self,v){ const ap=self.state.ap; v.ap_open=!!ap; if(!ap) return; const saf=self.state.saf; const rows=cultRows(self,saf).filter(r=>ap.ids.indexOf(r.id)>=0);
  const culturas=[...new Set(rows.map(r=>r.v.cult))]; v.ap_itens=rows.map(r=>({t:r.v.local+' · '+r.v.cult+' '+r.v.var+' · '+nf(r.v.area)+' ha'+(planById(r.v.plano)?' · plano atual: '+planById(r.v.plano).nome:'')}));
  v.ap_titulo='Aplicar plano a '+rows.length+(rows.length>1?' cultivos':' cultivo'); v.ap_mix=culturas.length>1; v.ap_mixmsg='Culturas diferentes na seleção ('+culturas.join(', ')+'). Selecione cultivos de uma só cultura: o plano precisa respeitar a cultura.';
  const opts=culturas.length===1? D2.planos.filter(p=>p.cultura===culturas[0]):[];
  v.ap_opts=[{v:'',t:'Escolha o plano'}].concat(opts.map(p=>({v:p.id,t:p.nome+' v'+p.versao+' · '+p.atividades.length+' atividades'}))); v.ap_plan=ap.plan; v.ap_has_opts=opts.length>0; v.ap_no_opts=(culturas.length===1&&!opts.length);
  v.ap_setplan=(e)=>self.setState({ap:Object.assign({},self.state.ap,{plan:e.target.value,confirm:false,err:''})});
  const adj=adjOf(self); const subst=rows.filter(r=>r.v.plano); const najs=rows.reduce((a,r)=>a+Object.keys(adj[r.id]||{}).length,0);
  v.ap_confirm=!!ap.confirm; v.ap_normal=!ap.confirm; v.ap_err=ap.err||''; v.ap_haserr=!!ap.err;
  v.ap_cmsg='Isto substitui o plano de '+subst.length+(subst.length===1?' cultivo':' cultivos')+(najs?' e descarta '+najs+(najs===1?' ajuste local':' ajustes locais'):'')+'. O plano padrão e os demais cultivos não mudam.';
  v.ap_cancel=()=>self.setState({ap:null});
  v.ap_apply=()=>{ const a=self.state.ap; if(culturas.length>1) return; if(!a.plan){ self.setState({ap:Object.assign({},a,{err:'Escolha o plano a aplicar.'})}); return; }
    if(subst.length && !a.confirm){ self.setState({ap:Object.assign({},a,{confirm:true})}); return; } doApply(self,rows,a.plan); };
  v.ap_yes=()=>doApply(self,rows,self.state.ap.plan); v.ap_back=()=>self.setState({ap:Object.assign({},self.state.ap,{confirm:false})}); }
function doApply(self,rows,pid){ const saf=self.state.saf; const gid='g_cult_'+sk(saf); const all=g2clone(g2rows(self,GR(gid)).filter(x=>!x.livre)); const adj=JSON.parse(JSON.stringify(adjOf(self)));
  rows.forEach(r=>{ const x=g2find(all,r.id); if(x){ x.v.plano=pid; delete adj[r.id]; } });
  const pl=planById(pid); g2set(self,gid,{rows:all,sel:{}}); self.setState({adj,ap:null,g2toast:pl.nome+' v'+pl.versao+' aplicado a '+rows.length+(rows.length>1?' cultivos':' cultivo')+'. Plano operacional, recursos e demanda recalculados.'}); }
// Insumos e doses de um cultivo, sem mudar o plano padrão. adj[cultivo] guarda só o que difere do padrão:
// 'atividade|i' = dose nova (número) ou '-' (insumo retirado deste talhão); 'atividade|+n' = insumo incluído {prod,grupo,un,preco,dose}.
// autocompletar do cadastro no "+ Incluir insumo nesta atividade": nome (semente com a variedade do cultivo), grupo, unidade e preço
function lpAc(self,A,cat,pk,upd,ERR,c,o){ const itens=cat.map(p=>({v:p.prod, t:prodNome(p.prod,c), sub:p.grupo+' · '+p.un+' · R$ '+nf(p.preco,2)+'/'+p.un}));
  return g2ac(self,'saf-lp-'+A,itens,pk||'',(val)=>{ const cur=self.state.lp; const er=Object.assign({},cur.err||{}); delete er['pick'+A]; upd({pick:Object.assign({},cur.pick||{},{[A]:val}),err:er}); },
    {ph:'Buscar insumo no cadastro', err:!!ERR('pick'+A), enter:()=>o.pkOk(), esc:()=>o.pkNo()}); }
function catalogo(){ if(catalogo._c) return catalogo._c; const m={}; D2.planos.forEach(pl=>pl.atividades.forEach(a=>a.prods.forEach(p=>{ if(!m[p.prod]) m[p.prod]={prod:p.prod,grupo:p.grupo,un:p.un,preco:p.preco}; })));
  catalogo._c=Object.values(m).sort((a,b)=>(a.grupo+' '+a.prod).localeCompare(b.grupo+' '+b.prod,'pt-BR')); return catalogo._c; }
function cultActs(self,gid,r){ if(!r||r.grp) return []; const pl=planById(r.v.plano); const na=Object.keys(adjOf(self)[r.id]||{}).length; const ro=!!r.ro;
  const t=(ro?'Ver insumos e doses de ':'Ajustar insumos e doses de ')+r.v.local;
  if(!pl||pl.cultura!==r.v.cult) return [{t, h:'Escolha um plano agronômico de '+r.v.cult+' e salve; depois ajuste os insumos só deste talhão.',
    go:()=>self.setState({g2toast:'Escolha e salve um plano agronômico de '+r.v.cult+' antes de ajustar os insumos.'})}];
  return [{t, h:(na?(na+(na>1?' ajustes deste talhão':' ajuste deste talhão')+' · '):'')+'Mude dose, retire ou inclua insumos só neste talhão; o plano padrão não muda.',
    go:()=>{ const cur=g2st(self,gid).fm; if(cur&&!cur.ro&&g2dirty(cur)){ self.setState({g2toast:'Salve ou descarte as alterações do cultivo antes de ajustar os insumos.'}); return; } g2set(self,gid,{fm:null}); openLP(self,r.id); }}]; }
function openLP(self,cid){ const saf=self.state.saf; const c=cultRows(self,saf).find(r=>r.id===cid); if(!c) return; const a=adjOf(self)[cid]||{}; const d={}, rm={}, add={};
  Object.keys(a).forEach(k=>{ const val=a[k]; const parts=k.split('|'); const A=parts[0], pi=parts[1]||'';
    if(pi.charAt(0)==='+'){ (add[A]||(add[A]=[])).push({prod:val.prod,grupo:val.grupo,un:val.un,preco:val.preco,dose:String(val.dose).replace('.',',')}); }
    else if(val==='-') rm[k]=true; else d[k]=String(val).replace('.',','); });
  self.setState({lp:{cid,draft:d,rm,add,pick:{},orig:JSON.stringify({d,rm,add}),warn:false,err:{}},lpx:{}}); }
function lpVals(self,v){ const lp=self.state.lp; v.lp_open=!!lp; if(!lp) return; const saf=self.state.saf; const c=cultRows(self,saf).find(r=>r.id===lp.cid); if(!c){ v.lp_open=false; return; }
  const pl=planById(c.v.plano); const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); const ro=!!(c.ro||(safObj&&safObj.ro));
  v.lp_titulo='Insumos e doses de '+c.v.local+' · '+c.v.cult+' '+c.v.var+', '+nf(c.v.area)+' ha';
  v.lp_sub='Plano padrão: '+pl.nome+' v'+pl.versao+' · plantio '+br(c.v.plantio)+'. '+(ro?'Safra encerrada: somente consulta.':'Mude a dose, retire ou inclua insumos só neste talhão. O plano padrão e os outros talhões não mudam.');
  v.lp_ro=ro; v.lp_edit=!ro; const ex=self.state.lpx||{};
  const upd=(patch)=>{ const cur=self.state.lp; self.setState({lp:Object.assign({},cur,patch,{warn:false})}); };
  const ERR=(k)=>(lp.err||{})[k]||'';
  const doseSt=(k,aj,dis)=>'width:84px;font-family:inherit;font-size:13px;padding:5px 7px;border-radius:8px;border:1px solid '+(ERR(k)?'#B42318':(aj?'#8A5A00':'#E4E9E5'))+';background:'+(dis?'#F4F6F3':(aj?'#FFF8E6':'#fff'))+';text-align:right;';
  const grupos={}; pl.atividades.forEach(a=>{ const g=grupoGat(a.g.tipo); ((grupos[g]||(grupos[g]={}))[gatLabel(a.g)+'||'+gatOrder(a.g)]||(grupos[g][gatLabel(a.g)+'||'+gatOrder(a.g)]=[])).push(a); });
  const order=['DAP','DAC','DATA'].filter(g=>grupos[g]);
  v.lp_grupos=order.map(g=>({t:GLABEL[g],gats:Object.keys(grupos[g]).sort((x,y)=>{ const a=x.split('||')[1], b=y.split('||')[1]; return g==='DATA'? (a<b?-1:1) : (Number(a)-Number(b)); }).map(key=>{
      const atvs=grupos[g][key]; const gid=g+key; const open=ex[gid]!==false;
      return {t:key.split('||')[0], dt:br(dataAtv(c,atvs[0],pl)), sym:open?'▾':'▸', open, lab:(open?'Recolher ':'Expandir ')+key.split('||')[0], tog:()=>{ const x=Object.assign({},self.state.lpx||{}); x[gid]=!open; self.setState({lpx:x}); },
        atvs:atvs.map(a=>{ const aid='a'+a.id; const ao=ex[aid]!==false; const A=String(a.id); const rmMap=lp.rm||{}; const adds=((lp.add||{})[A])||[];
          const prods=a.prods.map((p,i)=>{ const key=A+'|'+i; const removed=!!rmMap[key]; const dv=lp.draft[key]; const local=removed?0:((dv!==undefined&&dv!=='')?g2num(dv):p.dose);
              const aj=!removed&&dv!==undefined&&dv!==''&&Math.abs(local-p.dose)>1e-9;
              return {grupo:p.grupo, nome:prodNome(p.prod,c), padrao:nf(p.dose,2)+' '+p.un+'/ha', v:removed?'':(dv!==undefined?dv:String(p.dose).replace('.',',')), un:p.un+'/ha', preco:rs(p.preco)+'/'+p.un,
                custo:removed?'—':(rs((isNaN(local)?0:local)*p.preco)+'/ha'), aj, rmv:removed, novo:false, err:ERR(key), hasErr:!!ERR(key), dis:ro||removed, fid:'lp_'+key.replace('|','_'), ist:doseSt(key,aj,ro||removed),
                podeRet:!ro&&!removed, podeDesf:!ro&&removed, podeRest:!ro&&aj,
                set:(e)=>{ const cur=self.state.lp; const d=Object.assign({},cur.draft,{[key]:e.target.value}); const er=Object.assign({},cur.err||{}); delete er[key]; upd({draft:d,err:er}); },
                reset:()=>{ const cur=self.state.lp; const d=Object.assign({},cur.draft); delete d[key]; upd({draft:d}); },
                ret:()=>{ const cur=self.state.lp; const rr=Object.assign({},cur.rm||{},{[key]:true}); const d=Object.assign({},cur.draft); delete d[key]; const er=Object.assign({},cur.err||{}); delete er[key]; upd({rm:rr,draft:d,err:er}); },
                desf:()=>{ const cur=self.state.lp; const rr=Object.assign({},cur.rm||{}); delete rr[key]; upd({rm:rr}); } }; })
            .concat(adds.map((x,j)=>{ const key=A+'|+'+j; const n=g2num(x.dose);
              return {grupo:x.grupo, nome:prodNome(x.prod,c), padrao:'—', v:x.dose, un:x.un+'/ha', preco:rs(x.preco)+'/'+x.un, custo:(x.dose===''||isNaN(n))?'—':(rs(n*x.preco)+'/ha'), aj:false, rmv:false, novo:true,
                err:ERR(key), hasErr:!!ERR(key), dis:ro, fid:'lp_'+A+'_n'+j, ist:doseSt(key,true,ro), podeRet:!ro, podeDesf:false, podeRest:false,
                set:(e)=>{ const cur=self.state.lp; const ad=Object.assign({},cur.add||{}); ad[A]=(ad[A]||[]).slice(); ad[A][j]=Object.assign({},ad[A][j],{dose:e.target.value}); const er=Object.assign({},cur.err||{}); delete er[key]; upd({add:ad,err:er}); },
                reset:()=>{}, desf:()=>{},
                ret:()=>{ const cur=self.state.lp; const ad=Object.assign({},cur.add||{}); ad[A]=(ad[A]||[]).filter((_,q)=>q!==j); if(!ad[A].length) delete ad[A]; upd({add:ad,err:{}}); } }; }));
          const usados=a.prods.filter((p,i)=>!rmMap[A+'|'+i]).map(p=>p.prod).concat(adds.map(x=>x.prod));
          const pk=(lp.pick||{})[A]; const pkOpen=pk!==undefined; const cat=catalogo().filter(p=>usados.indexOf(p.prod)<0);
          return (o=>Object.assign(o,lpAc(self,A,cat,pk,upd,ERR,c,o)))({t:a.nome, op:a.op, sym:ao?'▾':'▸', open:ao, lab:(ao?'Recolher ':'Expandir ')+a.nome, tog:()=>{ const x=Object.assign({},self.state.lpx||{}); x[aid]=!ao; self.setState({lpx:x}); },
            semProd:!prods.length, prods, podeIncl:!ro&&!pkOpen, pkOpen:!ro&&pkOpen,
            pkOpts:[{v:'',t:'Escolha o insumo'}].concat(cat.map(p=>({v:p.prod,t:p.grupo+' · '+prodNome(p.prod,c)+' ('+p.un+')'}))), pkV:pk||'', pkErr:ERR('pick'+A), pkHasErr:!!ERR('pick'+A), pkFid:'lp_pick_'+A,
            incl:()=>{ const cur=self.state.lp; self.setState({g2ac:null}); upd({pick:Object.assign({},cur.pick||{},{[A]:''})}); setTimeout(()=>{ const el=document.getElementById(('ac-saf-lp-'+A).replace(/[^A-Za-z0-9_-]/g,'_')+'-in'); if(el) el.focus(); },0); },
            pkSet:(e)=>{ const cur=self.state.lp; const er=Object.assign({},cur.err||{}); delete er['pick'+A]; upd({pick:Object.assign({},cur.pick||{},{[A]:e.target.value}),err:er}); },
            pkOk:()=>{ const cur=self.state.lp; const val=(cur.pick||{})[A]; const p=catalogo().find(q=>q.prod===val);
              if(!p){ upd({err:Object.assign({},cur.err||{},{['pick'+A]:'Escolha o insumo a incluir.'})}); return; }
              const ad=Object.assign({},cur.add||{}); ad[A]=(ad[A]||[]).concat([{prod:p.prod,grupo:p.grupo,un:p.un,preco:p.preco,dose:''}]); const pkm=Object.assign({},cur.pick||{}); delete pkm[A]; upd({add:ad,pick:pkm}); },
            pkNo:()=>{ const cur=self.state.lp; const pkm=Object.assign({},cur.pick||{}); delete pkm[A]; const er=Object.assign({},cur.err||{}); delete er['pick'+A]; upd({pick:pkm,err:er}); } }); }) }; }) }));
  const dirty=()=>{ const cur=self.state.lp; return JSON.stringify({d:cur.draft,rm:cur.rm||{},add:cur.add||{}})!==cur.orig; };
  v.lp_warn=!!lp.warn; v.lp_nerr=Object.keys(lp.err||{}).length>0;
  v.lp_close=()=>{ if(!ro && dirty()){ self.setState({lp:Object.assign({},self.state.lp,{warn:true})}); return; } self.setState({lp:null}); };
  v.lp_discard=()=>self.setState({lp:null}); v.lp_keep=()=>self.setState({lp:Object.assign({},self.state.lp,{warn:false})});
  v.lp_save=()=>{ const cur=self.state.lp; const er={}; const out={};
    pl.atividades.forEach(a=>{ const A=String(a.id);
      a.prods.forEach((p,i)=>{ const key=A+'|'+i; if((cur.rm||{})[key]){ out[key]='-'; return; } const dv=cur.draft[key]; if(dv===undefined||dv==='') return; const n=g2num(dv);
        if(isNaN(n)||n<0){ er[key]='Use um número ≥ 0'; return; } if(Math.abs(n-p.dose)>1e-9) out[key]=n; });
      (((cur.add||{})[A])||[]).forEach((x,j)=>{ const key=A+'|+'+j; const n=g2num(x.dose); if(String(x.dose).trim()===''||isNaN(n)||n<=0){ er[key]='Informe a dose por hectare (maior que zero)'; return; }
        out[key]={prod:x.prod,grupo:x.grupo,un:x.un,preco:x.preco,dose:n}; }); });
    if(Object.keys(er).length){ self.setState({lp:Object.assign({},cur,{err:er})}); return; }
    const adj=JSON.parse(JSON.stringify(adjOf(self))); if(Object.keys(out).length) adj[cur.cid]=out; else delete adj[cur.cid];
    const vals=Object.values(out); const nr=vals.filter(x=>x==='-').length, ni=vals.filter(x=>x&&typeof x==='object').length, nd=vals.length-nr-ni;
    const partes=[nd?nd+(nd>1?' doses alteradas':' dose alterada'):'', nr?nr+(nr>1?' insumos retirados':' insumo retirado'):'', ni?ni+(ni>1?' insumos incluídos':' insumo incluído'):''].filter(Boolean);
    self.setState({adj,lp:null,g2toast:(partes.length?partes.join(' · ')+' em '+c.v.local:'Sem ajustes em '+c.v.local+': vale o plano padrão')+'. Plano operacional, recursos e demanda recalculados; o plano padrão e os outros talhões não mudaram.'}); };
}
function enviar(self){ const saf=self.state.saf; const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); if(safObj&&safObj.ro){ self.setState({g2toast:'Safra encerrada: não gera solicitações.'}); return; }
  const dm=demanda(self,saf); const sols=Object.assign({},solMap(self)); const sol=sols[saf];
  const itens=Object.values(dm).filter(d=>d.liq>0.001);
  if(!itens.length){ self.setState({g2toast:'Nada a cotar: o estoque e os recebimentos cobrem a demanda.'}); return; }
  // registro único da solicitação: o que a Compra de insumos mostra (mesmos itens, quantidades, valores e memória CAL-01)
  const det=Object.values(dm).map(d=>({nome:d.nome,grupo:d.grupo,un:d.un,preco:d.preco,bruta:d.bruta,est:d.est,res:d.res,rec:d.rec,liq:d.liq,valor:d.valor,falta:d.falta,uso:d.uso,quar:d.quar,evs:d.evs}));
  const EM='23/09/2026 11:05';   // horário do cenário de demonstração (a SOL-2026-07 inicial é de 10:40)
  const base={safra:saf,nome:safObj.v.nome,faz:safObj.v.faz||'Santa Rita',estado:'Enviada · a cotar',por:'Ana (gestora)',
    origem:{t:'Planejar safra · '+safObj.v.nome+' · etapa 6',h:'SAF.dc.html#saf='+encodeURIComponent(saf)+'&etapa=6'},det};
  const grava=(rec)=>{ const ok=solGravar(rec); return ok?'':' Atenção: este navegador não guarda dados; Compras não verá a solicitação.'; };
  if(!sol){ const ids={S27SF:'SOL-2027-02',S2627:'SOL-2026-07',LG2627:'SOL-2026-09'}; const usados=Object.values(sols).map(x=>x.id); let id=ids[saf];
    for(let k=10;!id||usados.indexOf(id)>=0;k++) id='SOL-2026-'+k;
    const it={}; itens.forEach(d=>{ it[d.nome]=d.liq; }); const tot=itens.reduce((a,d)=>a+d.valor,0);
    sols[saf]=Object.assign({},base,{id,at:'23/09/2026',em:EM,itens:it,comp:0,total:tot});
    const av=grava(sols[saf]);
    self.setState({sol:sols,g2toast:'Solicitação '+id+' enviada a Compras: '+itens.length+' insumos, '+rs(tot)+'. Origem: '+safObj.v.nome+' · Planejar safra, etapa 6.'+av}); return; }
  const novos=itens.filter(d=>d.liq>(sol.itens[d.nome]||0)+0.01);
  if(!novos.length){ self.setState({g2toast:'Nada novo para cotar: tudo já está na '+sol.id+'. Nenhuma solicitação duplicada foi criada.'}); return; }
  const it=Object.assign({},sol.itens); novos.forEach(d=>{ it[d.nome]=d.liq; }); const comp=(sol.comp||0)+1;
  const val=novos.reduce((a,d)=>a+(d.liq-(sol.itens[d.nome]||0))*d.preco,0);
  sols[saf]=Object.assign({},base,sol,{estado:'Enviada · a cotar',itens:it,comp,det,total:Object.keys(it).reduce((a,n)=>a+it[n]*((dm[n]||{}).preco||0),0),em:sol.em||(saf==='S2627'?'23/09/2026 10:40':EM)});
  const av=grava(sols[saf]);
  self.setState({sol:sols,g2toast:'Complemento '+sol.id+'-C'+comp+' enviado com só a diferença: '+novos.length+' insumos, '+rs(val)+'. A solicitação original não foi duplicada.'+av}); }
