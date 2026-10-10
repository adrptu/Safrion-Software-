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
// Cultura do painel do cultivo: sem cultura no rascunho, a 1ª opção é "Escolha a cultura" (o seletor nunca mostra uma cultura que o
// rascunho não tem; revisão SAF, S3.6)
function cultOpts(d){ return (d.cult?[]:[{v:'',t:'Escolha a cultura'}]).concat(Object.keys(D2.culturas||{}).map(c=>({v:c,t:c}))); }
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
// >>> CAPACIDADE (SAF etapa única "Dimensione operações e recursos" · ESPECIFICACAO §3.3) · funções puras, sem tela; espelho em
// dados2.capacidade; teste capacidade_unit.py. Uma fonte para a célula da g_cap, o filtro, os atalhos, o veredito, a prévia e o espelho.
// capacidade do grupo no mês = unidades × horas de uma unidade; horas de uma unidade = dias úteis × jornada × turnos × disponibilidade
// (pessoas: × (1 − absenteísmo), turnos = 1). Demanda = Σ x.nh × rc[k] (necessário = atendido + saldo: inclui o que ainda não tem alocação,
// PRD 53.2, "não truncar déficit"), desta safra e das outras safras abertas da mesma fazenda. Ocupação = demanda ÷ capacidade (capacidade 0
// com demanda: não calculável). Necessárias = o maior entre teto(demanda ÷ horas de uma unidade) e a maior equipe que trabalha ao mesmo tempo.
function capRec(r,meses,dias){ const pes=!!r.pes; const pc=(x)=>Math.min(100,Math.max(0,Number(x)||0))/100;
  const un=Number(r.un)||0, J=Number(r.jornada)||0, T=pes?1:(Number(r.turnos)||0), DP=pes?1-pc(r.abs):pc(r.disp);
  const porUn=meses.map(m=>(dias[m[0]]||0)*J*T*DP); return {id:r.id,nome:r.nome,pes,un,porUn,cap:porUn.map(p=>un*p)}; }
// carga de cada configuração de uma ocorrência por grupo de recursos: necessário (nh) × unidades (rc); ha = só o atendido; sim = equipe
// que trabalha ao mesmo tempo quando a configuração tem área necessária
function cargaItens(i){ const o=[]; ((i.rp&&i.rp.itens)||[]).forEach((x,j)=>{ const rc=(i.cfs&&i.cfs[j]&&i.cfs[j].rec)||{};
  Object.keys(rc).forEach(k=>{ const u=Number(rc[k])||0; if(u<=0) return; o.push({k,j,u,h:(Number(x.nh)||0)*u,ha:(Number(x.h)||0)*u,sim:(Number(x.nq)||0)>1e-12?u:0,semRec:!!x.semRec,nome:x.nome}); }); }); return o; }
function cargaRec(i,k){ return cargaItens(i).filter(c=>c.k===k).reduce((a,c)=>a+c.h,0); }
// etiqueta do calendário de uma ocorrência (uma só): antes do início, depois do fim ou fora do calendário; conta no custo, não na capacidade
function classeOc(dt,mi,ini,fim){ if(ini&&dt<ini) return 'antes'; if(fim&&dt>fim) return 'depois'; if(mi<0) return 'fora'; return 'cal'; }
// texto único da ocupação (célula, aria-label, filtro, atalhos e espelho): "<1 %" abaixo de 1 %; "—" sem demanda; null = não calculável
function fmtOcup(o){ if(o===null||o===undefined) return 'não calculável'; if(o<=0) return '—'; if(o<1) return '<1 %'; return Math.round(o).toLocaleString('pt-BR')+' %'; }
// atividades em uso de uma operação nesta safra (fonte única do "N atividades" da g_op e do alcance do "Todas")
function atvEmUso(oc,op){ const s=new Set(); oc.forEach(i=>{ if(i.a&&i.a.op===op) s.add(i.a.nome); }); return s; }
// capSaf(oc, outras, recursos, meses, dias): oc = ocorrências desta safra; outras = [{id, nome, oc}] das safras abertas da mesma fazenda.
// Ocorrência desta safra com etiqueta do calendário (i.cls de classeOc: antes do início, depois do fim, fora) conta no custo e não na
// capacidade (§3.4, FORA-DE-ESCOPO "Regra A"; revisão SAF, S3.1). As das outras safras entram como estão: são a carga real do mês.
function capSaf(oc,outras,recursos,meses,dias){ const M=meses.length; const Z=()=>new Array(M).fill(0); const G={};
  recursos.forEach(r=>{ G[r.id]=Object.assign(capRec(r,meses,dias),{dThis:Z(),dThisAt:Z(),dOth:Z(),oth:{},sim:Z(),semH:Z(),pendSR:Z()}); });
  const add=(i,own,sid)=>{ if(!(i.mi>=0)||(own&&i.cls&&i.cls!=='cal')) return; const cs=cargaItens(i);
    cs.forEach(c=>{ const g=G[c.k]; if(!g) return; if(own){ g.dThis[i.mi]+=c.h; g.dThisAt[i.mi]+=c.ha; if(c.semRec) g.pendSR[i.mi]++; } else { g.dOth[i.mi]+=c.h; (g.oth[sid]||(g.oth[sid]=Z()))[i.mi]+=c.h; }
      g.sim[i.mi]=Math.max(g.sim[i.mi],c.sim); });
    if(own&&i.rp&&i.rp.falta&&i.rp.falta.semHoras>1e-9){ const ks={}; cs.forEach(c=>{ ks[c.k]=1; }); Object.keys(ks).forEach(k=>{ if(G[k]) G[k].semH[i.mi]+=i.rp.falta.semHoras; }); } };
  (oc||[]).forEach(i=>add(i,true,null)); (outras||[]).forEach(s=>(s.oc||[]).forEach(i=>add(i,false,s.id)));
  Object.values(G).forEach(g=>{ g.cells=meses.map((m,mi)=>{ const d=g.dThis[mi]+g.dOth[mi], cap=g.cap[mi], pu=g.porUn[mi];
      const nc=(h)=>h>1e-4?(pu>0?Math.max(Math.ceil(h/pu-1e-9),g.sim[mi]):-1):0;   // −1: sem horas de uma unidade no mês (guarda)
      const nec=nc(d), necThis=nc(g.dThis[mi]); const falta=(n)=>n<0||n>g.un; const red=d>1e-4&&falta(nec);
      return {mi,mes:m[1],d,dThis:g.dThis[mi],dOth:g.dOth[mi],cap,porUn:pu,ocup:d>1e-4?(cap>0?100*d/cap:null):0,nec,red,soma:red&&!falta(necThis),own:g.dThis[mi]>1e-4,ge:g.semH[mi]>1e-9,pendSR:g.pendSR[mi]}; });
    const own=g.cells.filter(c=>c.own), calc=own.filter(c=>c.ocup!==null);
    g.max=calc.length?calc.reduce((b,c)=>(!b||c.ocup>b.ocup+1e-12)?c:b,null):(own[0]||null);   // empate: o 1º
    g.reds=own.filter(c=>c.red); g.necMax=g.reds.reduce((b,c)=>(!b||c.nec>b.nec||(b.nec>=0&&c.nec<0))?c:b,null);
    g.horasSafra=g.dThis.reduce((a,b)=>a+b,0); g.horasSafraAt=g.dThisAt.reduce((a,b)=>a+b,0); });
  return G; }
// atividades com ocorrência no calendário (M) e as que têm configuração com área necessária e janela vazia (J): a janela é de cada atividade
function capJanelas(oc){ const A={}; oc.forEach(i=>{ if(!(i.mi>=0)) return; const key=i.a.op+'|'+i.a.nome; const a=A[key]||(A[key]={sem:false});
  ((i.rp&&i.rp.itens)||[]).forEach(x=>{ const H=(x.Hin===undefined||x.Hin===null)?Infinity:x.Hin; if((x.nq||0)>1e-12&&!isFinite(H)) a.sem=true; }); });   // sem janela = Infinity (null no JSON)
  const ks=Object.keys(A); return {M:ks.length,J:ks.filter(k=>A[k].sem).length}; }
function capNomes(l){ return l.length>1?l.slice(0,-1).join(', ')+' e '+l[l.length-1]:l.join(''); }
function capH(n){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1}); }
// veredito (§3.1): o único lugar de "cabe", do que falta e do que ficou fora da conta. x = {semPlano:[{local,area}], aPlano, cls (contagens antes/
// fora/depois/cal), ini (dd/mm/aaaa), outras {id: nome}, pend (ocorrências sem alocação), semHoras (ha), incompleto (texto do R3)}
function capVeredito(G,oc,x){ const nfa0=(n)=>Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:2});
  const fora=[]; if(x.semPlano.length) fora.push(capNomes(x.semPlano.map(c=>c.local))+' ('+nfa0(x.semPlano.reduce((a,c)=>a+(Number(c.area)||0),0))+' ha), sem plano');
  if(x.cls.antes) fora.push(x.cls.antes+(x.cls.antes>1?' ocorrências':' ocorrência')+' antes do início da safra ('+x.ini+')');
  if(x.cls.fora) fora.push(x.cls.fora+(x.cls.fora>1?' ocorrências':' ocorrência')+' fora do calendário');
  if(x.cls.depois) fora.push(x.cls.depois+(x.cls.depois>1?' ocorrências':' ocorrência')+' depois do fim da safra');
  const foraTxt=fora.length?' Fora da conta: '+fora.join('; ')+'.':'';
  const jn=capJanelas(oc); const prazo=jn.J?' Prazo por talhão não verificado: '+jn.J+' de '+jn.M+(jn.M>1?' atividades':' atividade')+' sem janela.':'';
  if(!x.aPlano) return {R:'R0',cor:'',txt:''};
  if(!x.cls.cal) return {R:'R1',cor:'gray',txt:'Capacidade não calculada: '+(oc.length>1?'as '+oc.length+' ocorrências desta safra ficam':'a ocorrência desta safra fica')+' fora do calendário do protótipo ('+x.periodoCal+').'};
  const aperto=(g)=>{ const c=g.necMax; return c.nec<0?Infinity:c.nec/Math.max(g.un,1e-9); };
  const reds=Object.values(G).filter(g=>g.reds.length).sort((a,b)=>aperto(b)-aperto(a));
  if(reds.length){ const tr=reds.map((g,ix)=>{ const c=g.necMax; const n=c.nec<0?'horas':c.nec;
      const so=g.reds.every(q=>q.soma)?', somando '+Object.keys(g.oth).filter(o=>g.oth[o][c.mi]>1e-4).map(o=>'a '+(x.outras[o]||o)+' ('+capH(g.oth[o][c.mi])+' h)').join(' e '):'';
      return (ix===0?g.nome+(/s$/.test(g.nome)||g.pes?' precisam de ':' precisa de '):g.nome+', ')+n+' em '+c.mes+' e você tem '+g.un+(g.reds.length>1?' ('+g.reds.length+' meses)':'')+so; });
    const pend=x.pend?' Inclui '+x.pend+(x.pend>1?' ocorrências ainda sem alocação.':' ocorrência ainda sem alocação.'):'';
    const sh=x.semHoras>1e-9?' '+nfa0(x.semHoras)+' ha sem horas calculáveis ficam fora: a falta pode ser maior.':'';
    return {R:'R2',cor:'red',txt:'Falta recurso: '+tr.join('; ')+'.'+pend+sh+foraTxt}; }
  if(x.incompleto) return {R:'R3',cor:'yellow',txt:'Cálculo incompleto: '+x.incompleto+'.'+foraTxt};
  if(fora.length) return {R:'R4',cor:'yellow',txt:'Na estimativa mensal, cabe nos '+nfa0(x.aPlano)+' ha com plano.'+foraTxt+prazo};
  return {R:'R5',cor:'green',txt:'Na estimativa mensal, cabe com o que você tem.'+prazo}; }
// <<< CAPACIDADE
// configurações de uma atividade nesta safra (uma ou várias); sem nenhuma → pendência com motivo, nunca o conjunto de outra atividade
function cfgLeaves(rows){ const o=[]; const w=(l)=>(l||[]).forEach(r=>{ if(r.livre) return; if(r.kids&&r.kids.length) w(r.kids); else if(!r.grp) o.push(r); }); w(rows); return o; }
function cfgsOf(self,saf,op,atv){ return cfgLeaves(g2rows(self,GR(rendGid(saf)))).filter(k=>k.v.op===op&&k.v.atv===atv); }
const SEQ_T='Em sequência: divide trator, implemento ou operador', PAR_T='Ao mesmo tempo, com recursos próprios';
function ativosDe(id){ const s=String(id||''); return (!s||s==='classe'||s==='prestador')?[]:s.split('+'); }
// o prestador traz a equipe dele: não conta horas-homem da fazenda (a capacidade da etapa 3 também não conta pessoas dele)
function cfgIn(k){ const x=k.v; return {id:k.id,nome:x.nome,rend:x.rend,part:x.part,jan:x.jan,custo_h:x.custo_h,diesel:x.diesel,pess:(x.conj_id==='prestador'?0:x.pess),seq:x.seq===SEQ_T,troca:x.troca,ativos:ativosDe(x.conj_id),rec:k.rec||{}}; }
// quantas unidades a fazenda tem de cada grupo de recursos (formulário Recurso da etapa 3): duas configurações não usam a mesma plantadeira ao mesmo tempo
function poolsOf(self){ const o={}; ['g_recp_maq','g_recp_pes'].forEach(g=>{ const sp=GR(g); if(sp) g2rows(self,sp).forEach(r=>{ o[r.id]={un:Number(r.v.un)||0,nome:r.v.nome}; }); }); return o; }
function partTxt(x){ const p=rpNum(x.part); return (p===null||isNaN(p))?'pelo rendimento':(nfa(p)+' % da área'); }
function leaves(rows){ const o=[]; (rows||[]).forEach(r=>{ if(r.livre||r.fora||r.tal&&r.nosel) return; if(r.grp) (r.kids||[]).forEach(k=>{ if(!k.livre&&!k.fora) o.push(k); }); else o.push(r); }); return o; }
// ===== etapa 2 · Talhões e cultivos (ESPECIFICACAO etapa-2-talhoes) =====
// Todos os talhões Ativos do CD-01 da fazenda da safra; a ocupação no tempo (esta safra, outras safras, perenes, lavoura em campo) vem do
// serviço único ocupacao.js. O estado g_cult_* guarda só cultivos desta safra; a tabela mostra uma cópia (G2DISP) com a linha de cada talhão
// e as ocupações de fora esmaecidas (R-13). Trava só com o certo (R-14); previsão cruzada vira pendência visível (R-15).
function ocCtxSaf(){ if(!ocCtxSaf._c) ocCtxSaf._c=ocCtx(D2.culturas||{},D2.cultivares||[],D2.planos,D2.folga===undefined?1:D2.folga); return ocCtxSaf._c; }
function safById(self,id){ return g2rows(self,GR('g_saf')).find(r=>r.id===id)||null; }
function safFaz(self,id){ const r=safById(self,id); return (r&&r.v.faz)||'Santa Rita'; }
function safList(self){ const o={}; g2rows(self,GR('g_saf')).forEach(r=>{ o[r.id]={id:r.id,nome:r.v.nome,ini:r.v.ini,fim:r.v.fim,faz:r.v.faz||'Santa Rita',ro:!!r.ro}; }); return o; }
// fonte única das linhas de uma safra (R-22, REG-08): a grade dela; as safras novas dividem a g_cult_NOVA, separadas por v.saf
function cultsDe(self,saf){ if(!saf) return []; const k=sk(saf); const sp=GR('g_cult_'+k); if(!sp) return []; const ls=leaves(g2rows(self,sp)); return k==='NOVA'?ls.filter(c=>c.v.saf===saf):ls; }
function cultRows(self,saf){ return cultsDe(self,saf); }
// antes de gravar: só cultivos desta safra, sem linha de exibição (livre, fora, talhão) e sem grupo vazio (REG-09)
function soDaSafra(rows){ return (rows||[]).filter(r=>!r.livre&&!r.fora&&!r.tal).map(r=>r.kids?Object.assign({},r,{kids:soDaSafra(r.kids)}):r).filter(r=>!r.grp||(r.kids||[]).length); }
function ocCult(r,saf,faz){ const x=r.v; const tipo=x.tipo||'Talhão inteiro';
  return {id:r.id,saf,faz,faixa:x.local,tipo,talhao:x.talhao||ocTalhaoDe(x.local,tipo),area:Number(x.area)||0,cult:x.cult,var:x.var||'',plantio:x.plantio,plano:x.plano||null,
    colheita:x.colheita||null,colheita_real:x.colheita_real||null,ciclo:x.ciclo||null,origem:x.origem||''}; }
function ocTodos(self){ const S=safList(self); const out=[]; Object.keys(S).forEach(id=>{ cultsDe(self,id).forEach(r=>{ out.push(ocCult(r,id,S[id].faz)); }); }); return out; }
function talOrd(faz){ return ((D2.talOrd||{})[faz]||[]).map(x=>[x[0],Number(x[1])]); }
function talTot(faz){ return talOrd(faz).reduce((a,x)=>a+x[1],0); }
// data para a coluna (ordena e filtra por chave própria, REG-07): perene ordena como a mais tardia; "sem data" é valor próprio do filtro
function ocDcol(r,k,d,cl){ if(d===null||d===undefined){ r.v[k]=''; r.p[k]=[{k:cl||'mut',t:'sem data'}]; r.s[k]='sem data'; return; }
  if(d>=OC_INF){ r.v[k]=99991231; r.p[k]=[{k:cl||'txt',t:'sem fim'}]; r.s[k]='sem fim'; return; }
  const t=ocBr(d); r.v[k]=Number(ocIso(d).replace(/-/g,'')); r.p[k]=[{k:cl||'txt',t}]; r.s[k]=t; }
const SIT_COR={'Sobreposição':'red','A conferir':'yellow','Livre':'green','Planejado':'blue','Perene':'gray','Ocupado':'gray'};
// abaixo de 400 px a coluna Situação tem cerca de 98 px: rótulo curto, com o texto inteiro no title e no leitor de tela (OC-18)
const SIT_CURTO={'A conferir':'Conferir','Sobreposição':'Sobrepor','Planejado':'Planej.'};
function estreito360(){ try{ return window.innerWidth<400; }catch(e){ return false; } }
// motivo da Situação (dica e leitor de tela): a causa do A conferir ou da Sobreposição à vista (R-10)
function ocMotivo(L,info){ const by=info.byO, ctx=info.ctx;
  if(L.sit==='Sobreposição'){ const x=L.trav[0]; const nm=(id)=>{ const o=by[id]; return o?o.cult+' ('+o.faixa+', '+o.safnome+')':id; };
    if(x[0]==='soma') return 'Sobreposição: '+String(x[1]).split('+').concat([x[2]]).map(nm).join(' + ')+' somam '+ocHa(x[4])+' ha em '+ocBr(x[3]);
    return 'Sobreposição: '+nm(x[1])+' × '+nm(x[2])+' em '+ocBr(x[3]); }
  if(L.sit==='A conferir'){ const ps=[];
    if(L.seq.length){ const [xi,yi]=L.seq[0]; const x=by[xi], y=by[yi]; if(x&&y) ps.push('Sucessão a conferir: '+ocMinus(x.cult)+' sem fim confirmado ('+(x.fim!==null?ocBr(x.fim)+' est.':'sem data')+') antes '+ocDe(y.cult)+' '+ocMinus(y.cult)+' em '+ocBr(y.ini)); }
    if(L.conf>0.005){ const e=L.fora.filter(o=>o.classe==='estimado'||o.classe==='semdata'); if(e.length) ps.push(ocHa(L.conf)+' ha a conferir: saída '+ocDe(e[0].cult)+' '+ocMinus(e[0].cult)+' da '+e[0].safnome+(e[0].classe==='estimado'?' estimada em '+ocBr(e[0].fim)+' (sem plano, CD-02)':' sem data (sem ciclo no CD-02)')); }
    Object.keys(L.pend_own).forEach(k=>{ const o=by[k]; if(o) L.pend_own[k].forEach(p=>ps.push(o.faixa+': '+ocPendCurta(ctx,o,p,by))); });
    return ps.join(' · '); }
  if(L.sit==='Livre') return ocHa(L.area_livre)+' ha livres a partir de '+ocBr(L.desde)+' (folga '+ocDias(ctx.folga)+')';
  return ''; }
// monta a tabela da etapa 2 da safra aberta sobre cópia (nunca altera o estado nem grava) e devolve a ocupação calculada
function syncTalhoes(self,saf,v){ const k=sk(saf); const sp=GR('g_cult_'+k); const S=safList(self); const safra=S[saf]; if(!sp||!safra){ return null; }
  const ctx=ocCtxSaf(); const todos=ocTodos(self); const occ=ocOcupacoes(ctx,S,todos); const byO={}, byCiclo={}; occ.forEach(o=>{ byO[o.id]=o; byCiclo[o.ciclo]=o; });
  const adj=adjOf(self); const info={ctx,S,todos,occ,byO,safra,linhas:[],band:null,own:{}};
  const ocDe=(r)=>byCiclo[r.v.ciclo||r.id]||byO[r.id]||null;
  const ownParts=(r,o,kid,L)=>{ leafParts(r,adj,kid);
    r.p.sit=[{k:'mut',t:''}]; r.s.sit=''; r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre=''; ocDcol(r,'desde',undefined); r.p.desde=[{k:'mut',t:'—'}]; r.s.desde=''; r.v.desde='';
    r.p.saf=[{k:'mut',t:'—'}]; r.s.saf=''; r.v.saf_='';
    if(o){ ocDcol(r,'ate',o.classe==='semdata'?null:o.fim); r.v.fimpor=OC_ROT[o.classe]; r.p.fimpor=[{k:'txt',t:r.v.fimpor}]; r.s.fimpor=r.v.fimpor;
      const pe=L&&(L.pend[o.id]||[]); const tv=L&&L.trav.some(x=>x[1]===o.id||x[2]===o.id);
      if(tv){ r.p.sit=[{k:'chip',t:'Sobreposição',c:'red',dica:ocMotivo(L,info)}]; r.s.sit='Sobreposição'; }
      else if(pe&&pe.length){ const d=pe.map(p=>ocPendCurta(ctx,o,p,byO)).join(' · '); r.p.sit=[{k:'chip',t:'A conferir',c:'yellow',dica:d}]; r.s.sit='A conferir'; }
      if(o.avisos.length){ const a=o.avisos[0]; r.p.plano=(r.p.plano||[]).concat([{k:'br'},{k:'mut',t:'O plano '+a[1]+' tem datas fixas fora desta safra (ex.: '+ocBr(a[2])+'). Revise o plano ou troque o gatilho para DAP/DAPC.'}]); } }
    else { r.v.ate=''; r.p.ate=[{k:'mut',t:'—'}]; r.s.ate=''; r.v.fimpor=''; r.p.fimpor=[{k:'mut',t:'—'}]; r.s.fimpor=''; } };
  const foraRow=(o)=>{ const pl=planById(o.plano); const r={id:'fora_'+o.id,fora:true,ro:true,v:{talhao:o.t,local:o.faixa,cult:o.cult,var:o.var,area:'',ver:'',meta:'',aj:'',tipo:o.tipo},s:{},p:{}};
    r.p.local=[{k:'mut',t:o.faixa}]; r.s.local=o.faixa; r.p.sit=[{k:'mut',t:''}]; r.s.sit=''; r.p.livre=[{k:'mut',t:'—'}]; r.p.desde=[{k:'mut',t:'—'}];
    r.p.area=[{k:'mut',t:ocHa(o.area)+' ha'}]; r.s.area=ocHa(o.area)+' ha'; r.p.cult=[{k:'mut',t:o.cult}]; r.s.cult=o.cult; r.p.var=[{k:'mut',t:o.var||'—'}]; r.s.var=o.var;
    ocDcol(r,'ate',o.classe==='semdata'?null:o.fim,'mut'); r.v.fimpor=OC_ROT[o.classe]; r.p.fimpor=[{k:'mut',t:r.v.fimpor}]; r.s.fimpor=r.v.fimpor;
    r.p.saf=[{k:'act',t:o.safnome+' ›',fn:'abrirsaf:'+o.saf+'|'+o.id,lk:true}]; r.s.saf=o.safnome;
    r.p.plano=[{k:'mut',t:pl?pl.nome:'sem plano'}]; r.s.plano=pl?pl.nome:''; r.p.ver=[{k:'mut',t:pl?'v'+pl.versao:'—'}]; r.s.ver=pl?'v'+pl.versao:'';
    ocDcol(r,'dt_plantio',o.plantio,'mut'); r.p.meta=[{k:'mut',t:'—'}]; r.s.meta=''; r.p.aj=[{k:'mut',t:'—'}]; r.s.aj=''; r.p.tipo=[{k:'mut',t:o.tipo}]; r.s.tipo=o.tipo; return r; };
  if(safra.ro){   // R-20 safra encerrada: consulta só dos cultivos dela, com Plantio, Ocupa até, Fim por e Safra
    const rows=g2clone(g2rows(self,sp)).filter(r=>!r.livre&&!r.fora);
    rows.forEach(r=>{ const fill=(c,kid)=>{ ownParts(c,ocDe(c),kid,null); c.p.sit=[{k:'mut',t:'—'}]; c.p.saf=[{k:'mut',t:'—'}]; if(c.v.origem) c.p.local=(c.p.local||[]).concat([{k:'mut',t:c.v.origem}]); };
      if(r.grp){ grpParts(r,adj); (r.kids||[]).forEach(c=>fill(c,true)); ['sit','livre','desde','ate','fimpor','saf'].forEach(f=>{ r.p[f]=[{k:'mut',t:'—'}]; r.s[f]=''; }); } else fill(r,false); });
    G2DISP[sp.id]=rows; info.ro=true; return info; }
  const [linhas,band]=ocTabela(ctx,safra,occ,talOrd(safra.faz),S); info.linhas=linhas; info.band=band;
  const own=cultsDe(self,saf).map(r=>g2clone([r])[0]); const rows=[]; const x0={}; const estreito=g2estreito();
  linhas.forEach(L=>{ const t=L.t; const mine=own.filter(r=>(r.v.talhao||ocTalhaoDe(r.v.local,r.v.tipo))===t);
    const dica=ocMotivo(L,info); const curto=SIT_CURTO[L.sit]&&estreito360(); const sitP=[{k:'chip',t:curto?SIT_CURTO[L.sit]:L.sit,c:SIT_COR[L.sit]||'gray',dica:curto?(L.sit+(dica?': '+dica:'')):dica}];
    const acts=[]; let dr=null;
    if(L.planejar){ acts.push({k:'act',t:'Planejar ›',fn:'planejar:'+t,lk:true}); dr='plan_'+t; }
    else if(L.vinc.length){ acts.push({k:'act',t:'Vincular ciclo ›',fn:'vincular:'+t+'|'+L.vinc[0],lk:true}); dr='vinc_'+t; }
    else if(mine.length&&!mine.some(r=>r.v.ciclo)){ acts.push({k:'act',t:'Dividir',fn:'divide:'+t,lk:true}); dr='div_'+t; }   // ciclo vinculado não se divide (R-24)
    v['plan_'+t]=()=>abrirPlanejar(self,t); if(L.vinc.length) v['vinc_'+t]=()=>abrirVincular(self,t,L.vinc[0]);
    const tal=(r)=>{ r.tal=t; r.p.sit=sitP; r.s.sit=L.sit; r.v.sit=L.sit;
      if(L.area_livre>0.005){ r.v.livre=L.area_livre; r.p.livre=[{k:'txt',t:nfa(L.area_livre)}]; r.s.livre=nfa(L.area_livre);
        const sd=L.est&&L.fora.some(o=>o.classe==='semdata'&&o.ini<=L.desde&&L.desde<ocLib(ctx,o,'pior'));
        if(sd){ r.v.desde=''; r.p.desde=[{k:'txt',t:'sem data'}]; r.s.desde='sem data'; } else { ocDcol(r,'desde',L.desde); if(L.est){ r.p.desde=[{k:'txt',t:ocBr(L.desde)+' est.'}]; r.s.desde=ocBr(L.desde)+' est.'; } } }
      else { r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre=''; r.v.desde=''; r.p.desde=[{k:'mut',t:'—'}]; r.s.desde=''; } };
    const ownRows=mine.map(r=>{ const o=ocDe(r); ownParts(r,o,mine.length>1||r.v.tipo==='Parcela'||L.vis.length>0,L); return {r,ini:o?o.ini:ocDia(r.v.plantio)}; });
    if(mine.length===1&&mine[0].v.tipo!=='Parcela'&&!L.vis.length){   // folha: o próprio cultivo de talhão inteiro
      const r=ownRows[0].r; tal(r); if(!safra.ro) r.p.local=[{k:'b',t:t}].concat(acts); r.s.local=t; rows.push(r); return; }
    if(!mine.length&&L.vis.length<=1){   // folha: talhão sem cultivo desta safra, com no máximo uma ocupação de fora (esmaecida)
      const o=L.vis[0]; const r=o?foraRow(o):{id:'tal_'+t,v:{},s:{},p:{}}; r.id='tal_'+t; r.fora=false; r.nosel=true; r.ro=true; r.dr=dr; r.v.talhao=t; r.v.local=t;
      r.p.local=[{k:'b',t}].concat(acts); r.s.local=t; r.v.area=''; r.p.area=[{k:'mut',t:'—'}]; r.s.area=''; if(!o){ ['cult','var','ate','fimpor','saf','plano','ver','dt_plantio','meta','aj','tipo'].forEach(f=>{ r.p[f]=[{k:'mut',t:'—'}]; r.s[f]=''; }); }
      else { r.p.tipo=[{k:'mut',t:'—'}]; r.s.tipo=''; }
      tal(r); rows.push(r); return; }
    const kids=ownRows.concat(L.vis.map(o=>({r:foraRow(o),ini:o.ini}))).sort((a,b)=>(a.ini-b.ini)||(a.r.id<b.r.id?-1:1)).map(x=>x.r);
    const g={id:'grp_'+t,grp:true,nosel:true,ro:true,dr,v:{talhao:t,faz:safra.faz,local:t},s:{},p:{},kids:mine.length?kids:kids};
    if(mine.length){ grpParts(Object.assign(g,{kids:mine}),adj); g.kids=kids;
      if(mine.length===1&&mine[0].v.tipo!=='Parcela'){ const m=mine[0]; g.v.tipo='Talhão inteiro'; g.p.tipo=[{k:'txt',t:'Talhão inteiro'}]; g.s.tipo='Talhão inteiro'; g.v.meta=m.v.meta; g.p.meta=m.p.meta; g.s.meta=m.s.meta; } } else { ['cult','var','plano','ver','dt_plantio','meta','aj'].forEach(f=>{ g.p[f]=[{k:'mut',t:''}]; g.s[f]=''; }); g.v.area=''; g.p.area=[{k:'mut',t:'—'}]; g.p.tipo=[{k:'mut',t:'—'}]; g.s.tipo=''; }
    g.p.local=[{k:'b',t}].concat(acts); g.s.local=t; ['ate','fimpor','saf'].forEach(f=>{ g.p[f]=[{k:'mut',t:''}]; g.s[f]=''; g.v[f]=''; });
    tal(g); rows.push(g); x0[g.id]=!estreito; });
  sp.x0=x0; G2DISP[sp.id]=rows; return info; }
// fazenda e talhões da safra para os textos do painel
function talhaoArea(t){ return Number((D2.talhoes||{})[t])||0; }
// ---- painel "Planejar T1" e "Vincular ciclo C1" (§2, R-17, R-19, R-24) ----
function ocLinha(self,t){ const info=self.__oc; return info&&info.linhas?info.linhas.find(x=>x.t===t)||null:null; }
function maisUsado(cs,f){ const n={}; cs.forEach(c=>{ const x=c.v[f]; if(x) n[x]=(n[x]||0)+1; }); return Object.keys(n).sort((a,b)=>n[b]-n[a])[0]||''; }
// parcela sugerida (R-19): a faixa de fora que libera exatamente a Área livre no dia de "Livre a partir de"; senão a próxima letra
function sugerirParcela(self,saf,L,area,rid){ const t=L.t, T=talhaoArea(t); if(area>=T-0.005) return t; const ctx=ocCtxSaf();
  const usados=cultsDe(self,saf).filter(c=>c.id!==rid).map(c=>c.v.local);
  const f=L.fora.find(o=>o.faixa!==t&&usados.indexOf(o.faixa)<0&&Math.abs(o.area-area)<=0.005&&(ocLib(ctx,o,'pior')===L.desde||ocLib(ctx,o,'est')===L.desde));
  return f?f.faixa:nextNome(t,usados.concat(L.fora.map(o=>o.faixa))); }
// nome final da parcela (R-19): o MESMO na trava, no plantio mínimo, na prévia e no que se grava (revisão SAF, S2.2). Área cheia = talhão
// inteiro; nome digitado vale (repetido nesta safra o cultCheck recusa); vazio ou o nome do talhão = a parcela sugerida
function parcelaFinal(self,saf,t,area,local,rid){ const T=talhaoArea(t); if(!(area<T-0.005)) return t; const nm=String(local||'').trim();
  if(nm&&nm!==t) return nm; const L=ocLinha(self,t); if(L) return sugerirParcela(self,saf,L,area,rid);
  return nextNome(t,cultsDe(self,saf).filter(c=>c.id!==rid).map(c=>c.v.local)); }
function ocNovoRec(self,saf,d,id){ const t=d.talhao; const T=talhaoArea(t); const a=g2num(d.area); const area=isNaN(a)?0:a; const inteiro=area>=T-0.005;
  return {id:id||'__novo',saf,faz:safFaz(self,saf),faixa:parcelaFinal(self,saf,t,area,d.local,id||'__novo'),tipo:inteiro?'Talhão inteiro':'Parcela',talhao:t,area,cult:d.cult,var:d.var||'',
    plantio:d.plantio||'',plano:d.plano||null,colheita:(!d.plano&&d.colheita)?d.colheita:null,colheita_real:d.colheita_real||null,ciclo:d.ciclo||null,origem:''}; }
// PlantioMin do rascunho (cache por entrada: a busca anda dia a dia contra todas as ocupações do talhão)
function pminDraft(self,saf,d,desde){ const rec=ocNovoRec(self,saf,d,d._rid||'__novo'); const T=talhaoArea(d.talhao); const todos=ocTodos(self).filter(c=>c.id!==rec.id);
  const key=JSON.stringify([rec.cult,rec.var,rec.plano,rec.area,rec.faixa,rec.tipo,desde,self.state.g2&&self.state.g2['g_cult_'+sk(saf)]?Object.keys(self.state.g2).length:0,todos.length]);
  self._pm=self._pm||{}; if(key in self._pm) return self._pm[key];
  const S=safList(self); const r=ocPlantioMin(ocCtxSaf(),S,todos,saf,rec,desde,T,null); self._pm[key]=r; return r; }
function abrirPlanejar(self,t){ const saf=self.state.saf; const L=ocLinha(self,t); if(!saf||!L||!L.planejar) return;
  const sp=GR('g_cult_'+sk(saf)); const cs=cultsDe(self,saf);
  // contexto herdado da safra (cultura, variedade e plano mais usados); quantidade e meta nunca vêm do último valor (AGENTS §3.3)
  const cult=maisUsado(cs,'cult'); const vr=cult?maisUsado(cs.filter(c=>c.v.cult===cult),'var'):''; const pl=cult?maisUsado(cs.filter(c=>c.v.cult===cult&&planById(c.v.plano)),'plano'):'';
  const area=L.area_livre; const d={modo:'plan',talhao:t,cult,var:vr,plano:pl,plantio:'',local:sugerirParcela(self,saf,L,area),area:String(r2(area)).replace('.',','),colheita:'',meta:''};
  const pm=pminDraft(self,saf,d,L.desde); d.plantio=ocIso(pm!==null?pm:L.desde);
  self._plan={t,saf,desde:L.desde};
  g2set(self,sp.id,{fm:{rid:null,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro:false,isNew:true,mode:'form',title:'Planejar '+t},fl:null,fmc:null}); }
function abrirVincular(self,t,cid){ const saf=self.state.saf; const info=self.__oc; if(!saf||!info) return; const o=info.byO[cid]; if(!o) return;
  const src=ocTodos(self).find(c=>c.id===cid); const sp=GR('g_cult_'+sk(saf));
  const d={modo:'vinc',talhao:t,cult:o.cult,var:o.var,plano:'',plantio:ocIso(o.plantio),local:o.faixa,area:String(o.area).replace('.',','),colheita:'',meta:''};
  self._plan={t,saf,vinc:{ciclo:o.ciclo,src}};
  g2set(self,sp.id,{fm:{rid:null,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro:false,isNew:true,mode:'form',title:'Vincular ciclo '+t},fl:null,fmc:null}); }
// subtítulo do painel: contexto herdado, só leitura (fazenda · safra · talhão e área) e quanto está livre
function cultSub(self,gid,r,fm){ const saf=self.state.saf; const so=safById(self,saf); if(!so) return '';
  const t=(fm&&fm.draft&&fm.draft.talhao)||(r&&r.v&&r.v.talhao)||''; const L=t?ocLinha(self,t):null; const ctx=ocCtxSaf();
  let s=(so.v.faz||'Santa Rita')+' · '+so.v.nome+(t?' · '+t+' '+nfa(talhaoArea(t))+' ha':'');
  if(fm&&fm.draft&&fm.draft.modo==='vinc') return s+'. Ciclo perene da '+((self.__oc&&self.__oc.byO&&Object.values(self.__oc.byO).find(o=>o.faixa===fm.draft.local&&o.classe==='perene')||{}).safnome||'outra safra')+': cultura, cultivar, plantio real e área vêm do ciclo; escolha o plano (opcional) e a meta. O plano não é copiado.';
  if(fm&&fm.isNew&&L) s+='. Livre: '+nfa(L.area_livre)+' ha a partir de '+ocBr(L.desde)+(L.est?' (estimado)':'')+' (folga '+ocDias(ctx.folga)+').';
  else if(r&&!r.ro) s+='. Altere o cultivo e o plano agronômico e salve.';
  return s; }
function cultLive(self,gid,k,d){ const saf=self.state.saf; if(!saf) return null; const ctx=ocCtxSaf();
  if(k==='unm_txt') return unMetaDe(d.cult,d.unm);
  if(k==='colh_txt'){ const pl=planById(d.plano); if(!pl||!/^\d{4}-\d{2}-\d{2}$/.test(String(d.plantio||''))) return '—'; const rec=ocNovoRec(self,saf,d,d._rid); const so=safList(self)[saf];
    const o=ocMk(ctx,Object.assign({},rec,{colheita:null}),so); return ocBr(o.fim)+' · do plano'; }
  if(k==='pmin_txt'){ if(!d.talhao) return '—'; const L=ocLinha(self,d.talhao); const desde=(self._plan&&self._plan.desde!==undefined&&self._plan.t===d.talhao)?self._plan.desde:(L?L.desde:null);
    if(desde===null||desde===undefined) return '—'; const pm=pminDraft(self,saf,d,desde); if(pm===null) return 'sem janela antes do fim da safra';
    const dig=ocDia(d.plantio); return ocBr(pm)+(planById(d.plano)?' com este plano':'')+((dig!==null&&dig<pm)?' · a data digitada é anterior: confira a trava ou a pendência ao salvar':''); }
  if(k==='ocup_txt'){ if(!d.cult||!/^\d{4}-\d{2}-\d{2}$/.test(String(d.plantio||''))) return '—'; const rec=ocNovoRec(self,saf,d,d._rid); const o=ocMk(ctx,rec,safList(self)[saf]); return ocBr(o.ini)+' a '+(o.classe==='semdata'?'sem data':ocBr(o.fim))+(o.classe==='estimado'?' (estimado)':''); }
  return null; }
// rascunho: trocar a cultura traz a variedade e o plano mais usados dela; trocar plano, área ou parcela recalcula o plantio enquanto a
// pessoa não digitou a data (R-17)
function cultDraft(self,gid,k,d,fm){ const saf=self.state.saf; if(!saf||d.modo==='vinc') return null; const cs=cultsDe(self,saf);
  if(k==='plantio'){ d._pt='1'; return d; }
  if(k==='cult'){ d.var=maisUsado(cs.filter(c=>c.v.cult===d.cult),'var')||''; d.plano=maisUsado(cs.filter(c=>c.v.cult===d.cult&&planById(c.v.plano)),'plano')||''; }
  if(fm&&fm.isNew&&!d._pt&&['cult','plano','area','local'].indexOf(k)>=0&&self._plan&&self._plan.desde!==undefined){ const pm=pminDraft(self,saf,d,self._plan.desde); if(pm!==null) d.plantio=ocIso(pm); }
  return d; }
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
/* ---- análise de solo (SOLO-01): aceites do cenário compartilhado, uma leitura por cenrev; a dose efetiva de cada chave (ajuste manual da
   sessão, senão aceite, senão padrão), as atividades incluídas e as retiradas pela análise vêm de soloAtividades (solo.js, R14/R16) ---- */
function soloSaf(self){ const k=self.state.cenrev||0; if(!self.__sac||self.__sac.k!==k){ const c=cenGet(); self.__sac={k,c,ac:((c.solo||{}).aceites)||{},ls:soloLaudos(c,SOLO0)}; } return self.__sac; }
function soloCu(self,saf,c){ const pl=planById(c.v.plano); if(!pl||pl.cultura!==c.v.cult) return null; const S=safList(self)[saf]||{};
  return {id:c.id,saf,faz:S.faz||'Santa Rita',local:c.v.local,tal:c.v.talhao||c.v.local,cultura:c.v.cult,area:Number(c.v.area)||0,meta:c.v.meta,plano:pl,plantio:c.v.plantio,dt:(a)=>dataAtv(c,a,pl)}; }
function soloAlvoSaf(self){ const S=safList(self); const cs=[]; const sn={};
  Object.keys(S).forEach(id=>{ sn[id]={nome:S[id].nome,ro:S[id].ro}; if(S[id].ro) return; cultsDe(self,id).forEach(c=>cs.push({faz:S[id].faz,tal:c.v.talhao||c.v.local,saf:id,plantio:c.v.plantio})); });
  return soloAlvo(cs,sn); }
/* limpo: sem aceites e sem sessão (a sugestão crua de cada chave, para o painel de insumos comparar com o rascunho); senão, contra a dose efetiva */
function soloSugsSaf(self,saf,c,limpo){ const cu=soloCu(self,saf,c); if(!cu) return {sug:[],info:[],cu:null}; const x=soloSaf(self);
  const ac=limpo?Object.fromEntries(Object.entries(x.ac).filter(e=>e[1].tipo==='incluir')):x.ac;   /* limpo (painel): doses comparadas com o rascunho; as inclusões gravadas entram (R22, revisão A3) */
  const R=soloSugestoes({S0:SOLO0,ls:x.ls,aceites:ac,c:x.c,adj:limpo?{}:(adjOf(self)[c.id]||{}),alvo:soloAlvoSaf(self),todas:!!limpo},cu); R.cu=cu; return R; }
function soloNacSaf(self,c){ return soloAcAtivos(soloSaf(self).ac,c.id,c.v.plano).length; }
function ocorr(self,saf,poolsX){ const out=[]; const adj=adjOf(self); const pools=poolsX||poolsOf(self); const AC=soloSaf(self).ac;
  cultRows(self,saf).forEach(c=>{ const pl=planById(c.v.plano); if(!pl||pl.cultura!==c.v.cult) return; const area=Number(c.v.area)||0;
    soloAtividades({id:c.id,plano:pl},adj[c.id]||{},AC).atvs.forEach(x=>{ const a=x.a; const dt=dataAtv(c,a,pl); const cfs=cfgsOf(self,saf,a.op,a.nome);
      // a área da ocorrência se divide entre as configurações do formulário Rendimento; os insumos seguem dose × área e não mudam com a divisão
      const rp=repartir(area,cfs.map(cfgIn),pools); const horas=rp.hconj||0;
      // recursos (capacidade da etapa 3): horas × multiplicador = Σ horas de cada configuração × unidades dela (máquinas por grupo e pessoas)
      const rec={}; if(horas>0) rp.itens.forEach((x2,i)=>{ const rc=(cfs[i]&&cfs[i].rec)||{}; Object.keys(rc).forEach(k=>{ rec[k]=(rec[k]||0)+x2.h*rc[k]/horas; }); });
      // dose efetiva por chave (R14): sessão > aceite da análise > padrão; a origem segue para a memória da demanda (R21)
      const prods=x.prods.filter(q=>q.dose!=='-').map(q=>{ const p=q.p; const dose=Number(q.dose); return {nome:prodNome(p.prod,c),grupo:p.grupo,un:p.un,preco:p.preco,dose,q:dose*area,orig:q.orig,laudo:q.ac?q.ac.laudo:''}; });
      out.push({c,a,pl,dt,mi:mesIdx(dt),area,horas,dec:rp.decorrido,cop:rp.custo,cins:prods.reduce((s2,p)=>s2+p.q*p.preco,0),prods,rec,rp,cfs,
        saldo:rp.saldo,diesel:rp.diesel,hh:rp.hh,pend:rp.pendente,incl:!!x.incl}); }); });
  return out; }
// demanda por produto (CAL-01, cal01.js): uso = 1º uso de hoje em diante; a necessidade sai da projeção datada do insumo com as outras
// origens do mesmo estoque — safras abertas da mesma fazenda (agregadas por data), reservas para outros destinos e recebimentos com data.
// Uso planejado antes de hoje já foi realizado (sai da demanda residual: bruta = residual, real = realizado); compra nova só chega na data viável.
function demanda(self,saf){ const m={}; const safRows=g2rows(self,GR('g_saf')); const me=safRows.find(r=>r.id===saf); const faz=(me&&me.v.faz)||'Santa Rita';
  const ordem=(id)=>{ const i=safRows.findIndex(r=>r.id===id); return i<0?99:i; };
  ocorr(self,saf).forEach(o=>o.prods.forEach(p=>{ const d=m[p.nome]||(m[p.nome]={nome:p.nome,grupo:p.grupo,un:p.un,preco:p.preco,bruta:0,uso:'',evs:[]});
   d.bruta+=p.q; if(o.dt&&o.dt>=(D2.hoje||'')&&(!d.uso||o.dt<d.uso)) d.uso=o.dt;
   d.evs.push({dt:o.dt||'',q:p.q,tipo:'dem',own:true,ord:ordem(saf),chave:o.c.id+'|'+o.a.id,t:o.c.v.local+' · '+o.a.nome,calc:nf(p.dose,2)+' '+p.un+'/ha'+(p.orig==='análise'?' (pela análise · '+p.laudo+')':(p.orig==='sessão'?' (ajustado pelo usuário)':''))+' × '+nfa(o.area)+' ha'}); }));   // área com até 2 casas (PRE-REV R5)
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
    const cha=custoHa(x.custo_h,x.rend); x.custo_ha=(cha===null?'':cha);   // fonte única do R$/ha (ENG-011)
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
// equipe em pessoas inteiras: a demanda de Operadores é horas × pessoas (capacidade da etapa 3)
// safra: início e fim por calendário; o período curto da lista sai das datas
const SAF_MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
function safPeriodo(ini,fim){ if(!/^\d{4}-\d{2}-\d{2}$/.test(String(ini||''))||!/^\d{4}-\d{2}-\d{2}$/.test(String(fim||''))) return ''; const a=ini.split('-'), b=fim.split('-'); const mi=SAF_MES[Number(a[1])-1], mf=SAF_MES[Number(b[1])-1];
  return a[0]===b[0]?(mi+' – '+mf+'/'+b[0]):(mi+'/'+a[0]+' – '+mf+'/'+b[0]); }
function safCheck(d){ const e={}; if(d.ini&&d.fim&&String(d.fim)<=String(d.ini)) e.fim='O fim precisa ser depois do início.'; return e; }
// confere a configuração: pessoas inteiras e partes fixas da mesma atividade até 100 %
function rendCheck(self,rows,r,d,isNew){ const e={}; const n=g2num(d.pess); if(!isNaN(n)&&Math.round(n)!==n) e.pess='Use um número inteiro de pessoas.';
  // "Todas" não copia janela (§4.1): janela digitada com "Todas" é recusada no "Aplicar em" e o que foi digitado fica
  if(!isNew&&r&&String(d.multi)==='não'&&d.esc!=='Só esta atividade'){ const j0=rpNum(r.v.jan), j1=rpNum(d.jan); const z=(x)=>(x===null||isNaN(x))?null:x; if(z(j0)!==z(j1)) e.esc='A janela é de cada atividade. Para gravar '+(z(j1)===null?'a janela':nfa(j1)+' h')+", escolha 'Só esta atividade'."; }
  const nv=isNew?(self._novaCfg||{}):null; const op=nv?nv.op:(r&&r.v.op), atv=nv?nv.atv:(r&&r.v.atv); const p=g2num(d.part);
  if(String(d.multi)==='sim'&&!isNaN(p)){ const s=cfgLeaves(rows).filter(k=>k.v.op===op&&k.v.atv===atv&&(!r||k.id!==r.id)).reduce((a,k)=>{ const q=rpNum(k.v.part); return a+((q===null||isNaN(q))?0:q); },0);
    if(s+p>100+1e-9) e.part='As partes fixas somariam '+nfa(s+p)+' %; o máximo é 100 % (livre: '+nfa(Math.max(0,100-s))+' %).'; }
  return e; }
function rendLive(k,d,self){ const n=(f)=>{ const x=g2num(d[f]); return isNaN(x)?0:x; };
  if(k==='rend_c'){ const L=n('larg'),V=n('vel'),E=n('efic'); return (L&&V&&E)?nf(rendCalc(L,V,E),2):'—'; }
  // prestador: a tarifa por hora dele é a de Máquina (traz implemento, operador e diesel); implemento e pessoas da fazenda não entram
  const ch=()=>String(d.conj_id)==='prestador'?n('maq'):n('maq')+n('impl')+n('pess')*n('pess_rs');
  if(k==='custo_c') return nf(ch(),2);
  const rr=()=>d.modo==='Informado'?rpNum(d.rend):rendCalc(n('larg'),n('vel'),n('efic'));
  if(k==='custo_ha_c'){ const c=custoHa(ch(),rr()); return c===null?'—':rs(c)+'/ha'; }
  if(k==='custo_kg_c'){ const saf=self&&self.state.saf; const op=String(d.opatv||'').split(' · ')[0]; const cha=custoHa(ch(),rr()); const pc=saf?prodColheita(self,saf,op):[];
    return (!pc.length||!cha)?'não calculável':pc.map(q=>(pc.length>1?q.cult+' ':'')+'R$ '+nf(Math.round(cha/q.kg*10000)/10000,4)+'/kg').join(' · '); }
  if(k==='origem_c') return origemCfg(d);
  if(k==='jan_op') return self?janOp(self,String(d.opatv||'').split(' · ')[0]):'';
  if(k==='neste_c') return self?e3Neste(self._e3ctx):'';
  if(k==='nesta_c') return self?e3Nesta(self._e3ctx):'';
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
  // a equipe do conjunto é a demanda de 'Operadores e equipe' na capacidade da etapa 3 (h-pessoa = h do conjunto × pessoas); o prestador não usa recursos da fazenda
  r.rec=Object.assign({},r.rec||{});
  if(x.conj_id==='prestador') r.rec={};
  else { if(!Object.keys(r.rec).some(k=>k!=='oper')){ const b=(D2.conj||[]).find(c=>c.id===cfgBase(r)); if(b) r.rec=Object.assign({},b.rec); }
    if(Number(x.pess)>0) r.rec.oper=Number(x.pess); else delete r.rec.oper; }
  x.custo_h=r2((Number(x.maq)||0)+(Number(x.impl)||0)+x.pes_h);
  { const cha=custoHa(x.custo_h,x.rend); x.custo_ha=cha===null?'':cha; }   // fonte única do R$/ha (ENG-011)
  // Aplicar em: todas as atividades da operação (padrão) ou só esta; só para atividade de uma configuração, e só copia para
  // atividades de uma configuração (as divididas entre conjuntos ficam como estão). O selo fica na operação quando vale para todas.
  let n=0, nd=0; const g=rows.find(q=>q.grp&&(q.kids||[]).some(k=>k.id===r.id)); const todas=!!g&&!isNew&&(x.esc!=='Só esta atividade'); delete x.esc;
  // "Todas" alcança só as atividades em uso nesta safra (a mesma fonte do "N atividades" da g_op); as de planos ainda não aplicados ficam
  const uso=atvEmUso(ocorr(self,self.state.saf),x.op);
  if(g&&!isNew) x.aj=!todas;
  if(todas){ g.v.aj=true;
    g.kids.forEach(k=>{ if(k.id===r.id) return; const atvK=k.grp?((cfgLeaves(k.kids)[0]||{v:{}}).v.atv):k.v.atv; if(!uso.has(atvK)) return; if(k.grp){ nd++; return; } ['conj_id','nome','modo','larg','vel','efic','rend','maq','impl','pess','pess_rs','pes_h','custo_h','custo_ha','diesel'].forEach(f=>{ k.v[f]=x[f]; }); k.v.aj=false; k.rec=Object.assign({},r.rec); if(k.s) delete k.s.nome; n++; }); }
  normRend(rows);
  g2set(self,gid,{rows:g2clone(rows),fl:r.id}); const antE3=self._antes; self._antes=null; const orow=self._e3row; self._recPrev=null;
  const msg=(isNew?('Configuração incluída em '+x.atv+' · '+x.nome+': '+nf(x.rend,2)+' ha/h.'+novaMsg+prest)
    :('Rendimento de '+(n?x.op+' ('+(n+1)+' atividades)':x.atv)+' · '+x.nome+': '+nf(x.rend,2)+' ha/h · '+rs(x.custo_ha||0)+'/ha.'+trocou+prest+(nd?(' '+nd+(nd>1?' atividades divididas entre conjuntos não mudaram.':' atividade dividida entre conjuntos não mudou.')):'')))
    ;
  self.setState({g2toast:msg}); setTimeout(()=>{ self.setState({g2toast:msg+e3Diff(self,antE3,x.op)}); e3Foco(self,'g_op',orow); },0); }
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
  r.p.local=[{k:'b',t:r.v.local||'—'}].concat((!kid&&!r.ro&&!r.v.ciclo)?[{k:'act',t:'Dividir',fn:'divide:'+t,lk:true}]:[]); r.s.local=r.v.local;
  r.v.tipo=(r.v.tipo==='Parcela'||(kid&&r.v.tipo!=='Talhão inteiro')?'Parcela':'Talhão inteiro'); const tp=r.v.tipo+(r.decl?' (sem polígono)':''); r.p.tipo=[{k:'txt',t:tp}]; r.s.tipo=tp; r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre='';
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
// Um grupo por talhão (e, na g_cult_NOVA, por safra: R-22); parcelas do mesmo talhão entram no mesmo grupo, sem id repetido.
function grpId(t,saf){ return 'grp_'+(saf?saf+'_':'')+t; }
function normCult(rows){ const out=[], gs={};
  const poe=(g,ks)=>{ const s=(ks[0]&&ks[0].v.saf)||''; const id=grpId(g.v.talhao,s); ks.forEach(k=>{ k.v.tipo='Parcela'; });
    if(gs[id]){ gs[id].kids=gs[id].kids.concat(ks); return; } const x=Object.assign(g,{id,kids:ks.slice()}); if(s) x.v.saf=s; gs[id]=x; out.push(x); };
  rows.forEach(r=>{ const t=r.v.talhao, T=talhaoArea(t);
    if(r.grp){ const ks=r.kids||[]; if(ks.length) poe(r,ks); return; }
    if(T && (Number(r.v.area)||0)<T-0.005){ if(r.v.local===t){ r.v.local=t+'-A'; r.s.local=r.v.local; } r.decl=true;
      poe({grp:true,dr:'div_'+t,ro:!!r.ro,v:{talhao:t,faz:r.v.faz,local:t},s:{},p:{}},[r]); return; }
    r.v.tipo='Talhão inteiro'; out.push(r); });
  // grupo de uma parcela com a área toda volta a talhão inteiro
  return out.map(g=>{ if(!g.grp) return g; const T=talhaoArea(g.v.talhao); const ks=g.kids;
    if(ks.length===1&&Math.abs((Number(ks[0].v.area)||0)-T)<=0.005){ const k=ks[0]; k.v.local=g.v.talhao; k.v.tipo='Talhão inteiro'; k.s.local=g.v.talhao; k.decl=false; return k; } return g; }); }
// trava (R-14) e pendência/aviso (R-15) do serviço para um cultivo novo ou editado; devolve {erro, campo, pend, aviso}
function ocAvaliaCultivo(self,saf,rec){ const S=safList(self); const ctx=ocCtxSaf(); const todos=ocTodos(self); const depois=ocTroca(todos,rec); const T=talhaoArea(rec.talhao);
  const chk=ocChecar(ctx,S,todos,depois,saf,rec.id,T); if(!chk.o) return {erro:'',pend:'',aviso:''};
  const base=ocBaseMin(chk); let pmin=null;
  if(chk.trav.some(x=>x[0]==='observado')||Object.keys(chk.pend).length){ pmin=ocPlantioMin(ctx,S,todos,saf,rec,base,T,null); }
  if(chk.trav.length){ const tp=chk.trav[0][0]; const msg=ocMsgTrava(ctx,chk,saf,T,pmin);
    const seg=chk.trav.find(x=>x[0]==='faixa')&&chk.mesmo.find(y=>y!==chk.o&&y.plantio>chk.o.plantio&&ocMesmaArea(y,chk.o)&&chk.trav.some(x=>x[1]===y.id||x[2]===y.id));
    const p3=(seg&&ocPlantioMin(ctx,S,todos,saf,rec,base,T,null)===null)?' '+ocMsgSemJanela(ctx,chk.o,seg,base,saf):'';
    return {erro:msg+p3,campo:(tp==='safra'||tp==='soma')?'area':'plantio',pend:'',aviso:''}; }
  return {erro:'',pend:ocMsgPend(ctx,chk,saf,pmin),aviso:ocMsgAviso(ctx,chk)}; }
// começo da busca do plantio mínimo de um cultivo: a liberação da ocupação anterior na mesma faixa (ou o início da safra)
function ocBaseMin(chk){ const o=chk.o; const ctx=ocCtxSaf(); let b=o.safini; chk.mesmo.forEach(y=>{ if(y!==o&&ocMesmaArea(y,o)&&y.ini<o.ini&&y.classe!=='perene'){ const l=ocLib(ctx,y,'est'); if(l>b&&l<OC_INF) b=l; } }); return b; }
function cultCheck(self,gid,rows,r,d,isNew){ const e={}; const saf=self.state.saf; const t=isNew?String(d.talhao||''):(r&&r.v.talhao); const T=talhaoArea(t);
  const pv=isNew&&self._plan&&self._plan.vinc; const vc=!isNew&&r&&!!r.v.ciclo;   // ciclo vinculado: cultura, cultivar, plantio, área e faixa vêm do ciclo (R-24)
  // o que vale para a conta: o rascunho, menos o que vem do ciclo (vincular ou cultivo já vinculado)
  const dd=Object.assign({},(r&&r.v)||{},d,{talhao:t});
  if(pv) Object.assign(dd,{cult:pv.src.cult,var:pv.src.var,plantio:pv.src.plantio,area:pv.src.area,local:pv.src.faixa,ciclo:pv.ciclo});
  if(vc) Object.assign(dd,{cult:r.v.cult,var:r.v.var,plantio:r.v.plantio,area:r.v.area,local:r.v.local});
  const a=g2num(dd.area);
  const outros=cultsDe(self,saf).filter(c=>!r||c.id!==r.id);   // R-22: só os cultivos desta safra (as safras novas dividem a g_cult_NOVA)
  const nm=String(dd.local||'').trim();
  if(!isNew&&r&&!vc&&r.v.tipo!=='Parcela'&&nm&&nm!==t) e.local='Talhão inteiro usa o nome do talhão ('+t+'). Para criar parcelas, use Dividir em parcelas.';
  else if(!isNew&&r&&!vc&&r.v.tipo==='Parcela'&&!nm) e.local='Informe o nome da parcela.';
  const nmF=isNew?parcelaFinal(self,saf,t,isNaN(a)?0:a,nm,'__novo'):nm;   // o nome que vai ser gravado (S2.2)
  if(nmF&&!e.local&&outros.some(c=>c.v.local===nmF)) e.local='Já existe '+nmF+' nesta safra.';
  const pl=planById(String(dd.plano||'')); if(pl&&pl.cultura!==String(dd.cult||'')) e.plano='Este plano é de '+pl.cultura+'. Escolha um plano de '+dd.cult+' ou deixe sem plano.';
  if(!isNaN(a)&&T&&a>T+0.005) e.area='Máximo '+nfa(T)+' ha: é a área do talhão '+t+'.';
  if(pv&&cultsDe(self,saf).some(c=>(c.v.ciclo||c.id)===pv.ciclo)) e.cult='Este ciclo já está vinculado nesta safra.';
  self._ocMsg=null;
  if(!Object.keys(e).length&&saf&&!isNaN(a)){   // R-14 trava (nada gravado) e R-15 pendência (salva, com aviso)
    const rec=ocNovoRec(self,saf,dd,r?r.id:'__novo'); if(!isNew&&r){ rec.faixa=nm||r.v.local; rec.tipo=r.v.tipo||rec.tipo; rec.colheita_real=r.v.colheita_real||null; rec.ciclo=r.v.ciclo||null; }
    const av=ocAvaliaCultivo(self,saf,rec);
    if(av.erro) e[av.campo]=av.erro; else self._ocMsg=av.aviso||av.pend; }   // o aviso da saída estimada já diz a sobreposição; senão, a pendência
  self._planoAntes=(!Object.keys(e).length&&!isNew&&r)?{id:r.id,plano:String(r.v.plano||'')}:null;
  return e; }
function cultAfter(self,gid,rows,r,isNew){ let all=g2clone(soDaSafra(rows)); let msg=''; const saf=self.state.saf; const extra=self._ocMsg; self._ocMsg=null; let tNovo='';
  if(r&&isNew){ const pl=self._plan||{}; self._plan=null; const t=pl.t||r.v.talhao; tNovo=t||''; const x=g2find(all,r.id); all=all.filter(y=>y.id!==r.id); if(!x||!t){ g2set(self,gid,{rows:normCult(all)}); return; }
    x.v.talhao=t; x.v.faz=safFaz(self,saf); if(sk(saf)==='NOVA') x.v.saf=saf; x.v.plano=x.v.plano||''; x.v.colheita=(!x.v.plano&&x.v.colheita)?x.v.colheita:'';
    // vínculo (R-24): cultura, cultivar, plantio, área e faixa ficam do ciclo; modo 'vinc' trava esses campos ao editar depois (revisão SAF, S3.2)
    if(pl.vinc){ const src=pl.vinc.src||{}; Object.assign(x.v,{cult:src.cult,var:src.var,plantio:src.plantio,area:src.area,local:src.faixa,ciclo:pl.vinc.ciclo,colheita:'',modo:'vinc'}); }
    x.v.unm=unMetaDe(x.v.cult,x.v.unm);
    const T=talhaoArea(t); const a=Number(x.v.area)||0; const daSaf=(c)=>sk(saf)!=='NOVA'||c.v.saf===saf;   // R-22: só os cultivos desta safra
    // o mesmo nome que a trava conferiu (parcelaFinal, S2.2)
    if(a>=T-0.005){ x.v.local=t; x.v.tipo='Talhão inteiro'; x.decl=false; } else { x.v.local=parcelaFinal(self,saf,t,a,x.v.local,r.id); x.v.tipo='Parcela'; x.decl=true; }
    x.s.local=x.v.local; all.push(x); const fim=planById(x.v.plano)?(' · plano '+planById(x.v.plano).nome+'.'):(pl.vinc?'. Escolha o plano agronômico na linha (Aplicar plano).':'. Escolha o plano agronômico na linha.');
    const livre=T-leaves(all).filter(c=>c.v.talhao===t&&daSaf(c)).reduce((q,c)=>q+(Number(c.v.area)||0),0);
    msg=pl.vinc?('Ciclo vinculado: '+x.v.local+' · '+x.v.cult+' '+x.v.var+' desde '+br(x.v.plantio)+fim)
      :((x.v.tipo==='Parcela')?('Cultivo incluído como parcela '+x.v.local+' · '+nfa(Math.max(0,livre))+' ha livres em '+t+fim):('Cultivo incluído: '+t+' inteiro'+fim)); }
  else if(r){ const x=g2find(all,r.id); if(x){ x.v.unm=unMetaDe(x.v.cult,x.v.unm); if(x.v.plano) x.v.colheita=''; } }
  const pa=self._planoAntes; self._planoAntes=null;
  if(r&&!isNew&&pa&&pa.id===r.id&&pa.plano!==String(r.v.plano||'')){ const adj=JSON.parse(JSON.stringify(adjOf(self))); const n=Object.keys(adj[r.id]||{}).length; const pl=planById(r.v.plano);
    if(n){ delete adj[r.id]; self.setState({adj}); }
    msg=(pl?('Plano de '+r.v.local+': '+pl.nome+' v'+pl.versao):('Plano retirado de '+r.v.local))+(n?(' · '+n+(n>1?' ajustes de dose descartados':' ajuste de dose descartado')):'')+'. Plano operacional, recursos e demanda recalculados.'; }
  if(extra) msg=(msg?msg+' ':'')+'Atenção: '+extra+'.';
  // grupo aberto depois de salvar: pelo id gravado e pelo id da tabela (grp_<talhão>, o da linha de exibição da safra aberta)
  // (o padrão da tabela, x0 da exibição, continua valendo: planejar um talhão com ocupação de fora não recolhe o grupo dele)
  const norm=normCult(all); const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); norm.forEach(y=>{ if(!y.grp) return; [y.id,'grp_'+y.v.talhao].forEach(k=>{ if(x0[k]!==false) x0[k]=true; }); });
  if(tNovo&&x0['grp_'+tNovo]!==false) x0['grp_'+tNovo]=true;
  g2set(self,gid,{rows:norm,x:x0}); if(msg) self.setState({g2toast:msg}); }
// ---- painel: dividir o talhão em quantas parcelas precisar ----
// unidade da meta = unidade de mercado da cultura (DEC-0510-03), nunca escolhida na linha (revisão SAF, S3.7)
function unMetaDe(cult,un0){ return (D2.unMeta||{})[cult]||un0||'sc/ha'; }
function dvRow(c){ return {id:c.id||null,local:c.v.local||'',area:(c.v.area===''||c.v.area===undefined)?'':String(r2(c.v.area)).replace('.',','),cult:c.v.cult||'Soja',var:c.v.var||'',plantio:c.v.plantio||'',
  meta:(c.v.meta===''||c.v.meta===undefined)?'':String(c.v.meta).replace('.',','),unm:unMetaDe(c.v.cult,c.v.unm),plano:c.v.plano||'',colheita:c.v.colheita||'',adj:null,from:'',decl:!!c.decl,ask:false}; }
function dvDist(lst,T){ const n=lst.length; if(!n) return lst; const each=Math.floor(T*100/n)/100; return lst.map((x,i)=>Object.assign({},x,{area:String(i<n-1?each:r2(T-each*(n-1))).replace('.',',')})); }
function openDiv(self,t,extra){ const saf=self.state.saf; if(!saf){ self.setState({g2toast:'Escolha a safra primeiro.'}); return; }
  const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); const minhas=cultsDe(self,saf);   // R-22: só os cultivos desta safra (revisão SAF, S1)
  const cur=minhas.filter(c=>c.v.talhao===t); const ro=!!(safObj&&safObj.ro)||cur.some(c=>c.ro);
  // ciclo vinculado (R-24): área, plantio e cultura vêm do ciclo; dividir mudaria o que é do ciclo (revisão SAF, S3.2)
  if(!ro&&cur.some(c=>c.v.ciclo)){ self.setState({g2toast:'Ciclo perene vinculado: área, plantio e cultura vêm do ciclo; não se divide aqui.'}); return; }
  let lst=cur.map(dvRow); let base;
  const inteiro=(cur.length===1&&cur[0].v.tipo!=='Parcela');
  if(!ro&&inteiro&&!extra){ lst[0].local=t+'-A'; lst.push(Object.assign({},lst[0],{id:null,local:t+'-B',from:t+'-A',decl:true,adj:copyAdj(self,cur[0].id)})); lst=dvDist(lst,talhaoArea(t)); base=JSON.stringify(lst); }
  else { base=JSON.stringify(lst); if(extra){ if(inteiro) lst[0].local=t+'-A'; const e=dvRow(extra); e.id=null; e.decl=true;
      const usados=lst.map(x=>x.local).concat(minhas.filter(c=>c.v.talhao!==t).map(c=>c.v.local)); if(!e.local||e.local===t||usados.indexOf(e.local)>=0) e.local=nextNome(t,usados); lst.push(e); } }
  self.setState({dv:{t,rows:lst,base,ro,err:{},gerr:'',warn:false}}); }
function dvSave(self){ const dv=self.state.dv; if(!dv||dv.ro) return; const t=dv.t, T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf); const rows=g2rows(self,GR(gid));
  const daSaf=(c)=>sk(saf)!=='NOVA'||c.v.saf===saf;   // R-22: a g_cult_NOVA guarda as safras novas; só as linhas desta safra mudam (revisão SAF, S1)
  if(!dv.rows.length){ self.setState({dv:Object.assign({},dv,{gerr:'Mantenha pelo menos uma parcela. Para tirar o talhão da safra, exclua a linha dele na tabela.'})}); return; }
  const outros=cultsDe(self,saf).filter(c=>c.v.talhao!==t); const err={}; let A=0; const nomes={};
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
  const all=g2clone(soDaSafra(rows)); const adj=JSON.parse(JSON.stringify(adjOf(self))); const old=leaves(all).filter(c=>c.v.talhao===t&&daSaf(c)); const byId={}; old.forEach(c=>{ byId[c.id]=c; });
  const stamp=String(Date.now()).slice(-6);
  const kids=dv.rows.map((x,i)=>{ const b=(x.id&&byId[x.id])||null; const c=b||{id:'p'+t+'_'+stamp+'_'+i,v:{},s:{},p:{},decl:true};
    if(b&&String(b.v.plano||'')!==String(x.plano||'')) delete adj[b.id];
    Object.assign(c.v,{talhao:t,faz:(b?b.v.faz:(old[0]?old[0].v.faz:safFaz(self,saf))),local:String(x.local).trim(),cult:x.cult,var:String(x.var).trim(),area:r2(g2num(x.area)),plantio:x.plantio,meta:g2num(x.meta),unm:unMetaDe(x.cult,x.unm),plano:x.plano||'',colheita:x.colheita||''});
    if(b&&b.v.tipo!=='Parcela') c.decl=true; if(sk(saf)==='NOVA') c.v.saf=saf; c.v.tipo='Parcela';
    c.s={}; c.p={}; if(!b&&x.adj&&Object.keys(x.adj).length) adj[c.id]=JSON.parse(JSON.stringify(x.adj)); return c; });
  { const S=safList(self), ctx=ocCtxSaf(), todos=ocTodos(self); const faz=safFaz(self,saf); const ids=old.map(c=>c.id);
    const recs=kids.map(c=>{ const rr=ocCult(c,saf,faz); rr.tipo=(kids.length===1&&Math.abs(rr.area-T)<=0.005)?'Talhão inteiro':'Parcela'; if(rr.tipo==='Talhão inteiro') rr.faixa=t; return rr; });
    const depois=todos.filter(c=>ids.indexOf(c.id)<0).concat(recs); const er2={};
    recs.forEach((rr,i)=>{ const chk=ocChecar(ctx,S,todos,depois,saf,rr.id,T); if(chk.o&&chk.trav.length){ const m=ocMsgTrava(ctx,chk,saf,T,null); er2[i]=(chk.trav[0][0]==='safra'||chk.trav[0][0]==='soma')?{area:m}:{plantio:m}; } });
    if(Object.keys(er2).length){ self.setState({dv:Object.assign({},dv,{err:er2,gerr:'A divisão travaria a área: '+Object.keys(er2).length+(Object.keys(er2).length>1?' parcelas':' parcela')+' com ocupação certa no período. Nada foi gravado.',warn:false})}); return; } }
  const keep=kids.map(c=>c.id); old.forEach(c=>{ if(keep.indexOf(c.id)<0) delete adj[c.id]; });
  const isT=(r)=>r.v.talhao===t&&(r.grp?(r.kids||[]).some(daSaf):daSaf(r)); let pos=all.findIndex(isT); const rest=all.filter(r=>!isT(r)); if(pos<0) pos=rest.length;
  const gi=grpId(t,sk(saf)==='NOVA'?saf:''); rest.splice(pos,0,{id:gi,grp:true,dr:'div_'+t,ro:false,v:{talhao:t,faz:kids[0].v.faz,local:t},s:{},p:{},kids});
  const norm=normCult(rest); const st=g2st(self,gid); const x0=Object.assign({},GR(gid).x0||{},st.x||{}); x0[gi]=true; x0['grp_'+t]=true;
  g2set(self,gid,{rows:norm,x:x0,sel:{},fl:null});
  const inteiro=norm.some(r=>!r.grp&&r.v.talhao===t&&daSaf(r));
  self.setState({adj,dv:null,g2toast:(inteiro?(t+' volta a talhão inteiro.'):(t+' dividido em '+kids.length+(kids.length>1?' parcelas':' parcela')+(A<T-0.005?(' · '+nfa(T-A)+' ha livres'):'')+'.'))+' Plano operacional, recursos e demanda recalculados.'}); }
function divVals(self,v){ const dv=self.state.dv; v.dv_open=!!dv; if(!dv){ v.dv_rows=[]; return; } const t=dv.t, T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf);
  const lst=dv.rows; const A=lst.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const L=T-A; const exc=L< -0.005, ok=Math.abs(L)<=0.005;
  v.dv_titulo=dv.ro?('Parcelas de '+t):('Dividir '+t+' em parcelas'); v.dv_n=lst.length+(lst.length>1?' parcelas':' parcela');
  v.dv_resumo='Talhão '+nfa(T)+' ha · alocado '+nfa(A)+' ha · livre '+nfa(Math.max(0,L))+' ha';
  v.dv_selo=exc?('Excede em '+nfa(-L)+' ha'):(ok?'Área conferida':(nfa(L)+' ha livres'));
  const cc=exc?['#B42318','#FDE8E6']:(ok?['#1E7A4C','#E4F3E9']:['#8A5A00','#FFF4D6']);
  v.dv_selost='display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';';
  v.dv_ro=!!dv.ro; v.dv_edit=!dv.ro; const adj=adjOf(self);
  const CULT=Object.keys(D2.culturas||{}).length?Object.keys(D2.culturas):['Soja','Milho','Feijão','Café','Mamão Formosa'];
  const upd=(i,patch)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],patch); return Object.assign({},cur,{rows:rs}); };
  v.dv_rows=lst.map((x,i)=>{ const pl=planById(x.plano); const na=x.id?Object.keys(adj[x.id]||{}).length:Object.keys(x.adj||{}).length; const e=(dv.err||{})[i]||{};
    const set=(f)=>(ev)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],{[f]:ev.target.value}); const er=Object.assign({},cur.err||{}); if(er[i]){ er[i]=Object.assign({},er[i]); delete er[i][f]; if(!Object.keys(er[i]).length) delete er[i]; }
      self.setState({dv:Object.assign({},cur,{rows:rs,err:er,warn:false,gerr:(Object.keys(er).length?cur.gerr:'')})}); };
    const ist=(f,x2)=>'font-family:inherit;font-size:13px;padding:6px 8px;border-radius:8px;box-sizing:border-box;width:100%;min-width:0;color:#15201A;border:1px solid '+(e[f]?'#B42318':'#E4E9E5')+';background:'+(dv.ro?'#F4F6F3':'#FFFFFF')+';'+(x2||'');
    let pt; if(!pl) pt=''; else if(pl.cultura!==x.cult) pt='Plano de '+pl.cultura+': escolha um plano de '+x.cult; else pt=(na?na+(na>1?' ajustes deste talhão':' ajuste deste talhão'):'')+(x.from?((na?' · ':'')+'copiado de '+x.from):'');
    const lab=x.local||('parcela '+(i+1)); const errs=Object.keys(e).map(k=>e[k]);
    return {i,local:x.local,area:x.area,cult:x.cult,var:x.var,plantio:x.plantio,meta:x.meta,unm:unMetaDe(x.cult,x.unm),plano:pt,temNota:!!pt,pwarn:!!(pl&&pl.cultura!==x.cult),dis:!!dv.ro,lab,
      planoId:x.plano||'', op:planOpts({cult:x.cult,plano:x.plano}), s_plano:set('plano'), st_plano:ist('plano'),
      oc:CULT.map(o=>({v:o,t:o})),
      s_local:set('local'),s_area:set('area'),s_cult:set('cult'),s_var:set('var'),s_plantio:set('plantio'),s_meta:set('meta'),
      st_local:ist('local','font-weight:700;'),st_area:ist('area','text-align:right;'),st_cult:ist('cult'),st_var:ist('var'),st_plantio:ist('plantio'),st_meta:ist('meta','text-align:right;'),
      pst:'font-size:12px;line-height:1.3;color:'+(pl&&pl.cultura!==x.cult?'#B42318':'#5B6660')+';',
      hasErr:errs.length>0,errMsg:errs.join(' · '),ask:!!x.ask,notAsk:!x.ask&&!dv.ro,askMsg:'Excluir '+lab+'? Sai do plano operacional e da demanda.',
      rm:()=>{ const cur=self.state.dv; const y=cur.rows[i]; const tem=!!y.plano||!!(y.id&&Object.keys(adjOf(self)[y.id]||{}).length)||!!Object.keys(y.adj||{}).length;
        if(tem&&!y.ask){ self.setState({dv:upd(i,{ask:true})}); return; } self.setState({dv:Object.assign({},cur,{rows:cur.rows.filter((_,j)=>j!==i),err:{},gerr:'',warn:false})}); },
      rmNo:()=>self.setState({dv:upd(i,{ask:false})}) }; });
  v.dv_add=()=>{ const cur=self.state.dv; const rs=cur.rows.slice(); const last=rs[rs.length-1];
    const usados=rs.map(x=>x.local).concat(cultsDe(self,saf).filter(c=>c.v.talhao!==t).map(c=>c.v.local));
    const A2=rs.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const livre=r2(T-A2); const area=livre>0.005?String(livre).replace('.',','):'';
    const nw=last?Object.assign({},last,{id:null,local:nextNome(t,usados),area,from:last.local,decl:true,ask:false,adj:(last.id?copyAdj(self,last.id):(last.adj?JSON.parse(JSON.stringify(last.adj)):null))})
                 :{id:null,local:nextNome(t,usados),area,cult:'Soja',var:'',plantio:'',meta:'',unm:unMetaDe('Soja'),plano:'',colheita:'',adj:null,from:'',decl:true,ask:false};
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
// ---- SAF etapa 3 "Dimensione operações e recursos" (ESPECIFICACAO etapa-unica-3-4-5 §2–§4) ----
// Uma tela responde se a safra cabe no que a fazenda tem (veredito, atalhos e g_cap), de onde vem a carga de um mês (filtro recurso ×
// mês na g_op) e que conjunto, rendimento e custo cada operação assume (g_op → formulário Rendimento). As contas são as do motor
// (ocorr → repartir) e do bloco CAPACIDADE: nada aqui tem fórmula nova (ENG-011).
// recursos da fazenda (g_recp_maq + g_recp_pes, na ordem do cadastro); rid + dv = rascunho de um recurso (prévia do formulário)
function recursosDe(self,rid,dv){ const o=[]; ['g_recp_maq','g_recp_pes'].forEach(g=>{ const sp=GR(g); if(sp) g2rows(self,sp).forEach(r=>{ let x=r.v;
    if(rid&&r.id===rid&&dv){ x=Object.assign({},r.v); ['un','jornada','turnos','disp','abs'].forEach(k=>{ if(dv[k]!==undefined){ const n=g2num(dv[k]); x[k]=isNaN(n)?0:n; } }); }
    o.push({id:r.id,nome:x.nome,pes:g==='g_recp_pes',un:Number(x.un)||0,jornada:x.jornada,turnos:x.turnos,disp:x.disp,abs:x.abs}); }); }); return o; }
function poolsDe(recs){ const o={}; recs.forEach(r=>{ o[r.id]={un:Number(r.un)||0,nome:r.nome}; }); return o; }
// outras safras que dividem os recursos: abertas (não encerradas) e da mesma fazenda; a própria encerrada não soma nada (o predicado do estoque)
function outrasSafras(self,saf,pools){ const S=safList(self); const me=S[saf]; if(!me||me.ro) return [];
  return Object.keys(S).filter(id=>id!==saf&&!S[id].ro&&S[id].faz===me.faz).map(id=>({id,nome:S[id].nome,oc:ocorr(self,id,pools)})); }
function capCalc(self,saf,rid,dv){ const recs=recursosDe(self,rid,dv); const pools=poolsDe(recs); const oc=ocorr(self,saf,pools); const outras=outrasSafras(self,saf,pools);
  const me=safList(self)[saf]||{}; oc.forEach(i=>{ i.cls=classeOc(i.dt,i.mi,me.ini,me.fim); });   // etiqueta antes da conta: a mesma na tela, no veredito e na capacidade
  return {oc,outras,recs,pools,G:capSaf(oc,outras,recs,D2.meses,D2.dias)}; }
// meses da g_cap (§3.3): os do calendário dentro do período da safra; sem interseção, o calendário inteiro. A demanda desta safra fora do
// período não conta na capacidade (capSaf), então nenhum mês com demanda dela fica de fora
function capMeses(ini,fim){ const a=String(ini||'').slice(0,7), b=String(fim||'').slice(0,7); const ms=D2.meses.map((m,i)=>i).filter(i=>a<=D2.meses[i][0]&&D2.meses[i][0]<=b);
  return ms.length?ms:D2.meses.map((m,i)=>i); }
function custoHa(ch,rend){ const r=rpNum(rend); return (r===null||isNaN(r)||!(r>0))?null:(Number(ch)||0)/r; }
function e3Mes(s){ return SAF_MES[Number(String(s).slice(5,7))-1]+'/'+String(s).slice(2,4); }
function e3Faixa(its){ const ds=its.map(i=>i.dt).filter(Boolean).sort(); if(!ds.length) return ''; const a=e3Mes(ds[0]), b=e3Mes(ds[ds.length-1]); return a===b?a:a+' – '+b; }
function e3SemJan(x){ return (x.nq||0)>1e-12&&!isFinite(x.Hin===undefined?x.H:x.Hin); }
function e3Dinf(i){ return i.rp.itens.some(x=>x.q>0&&x.d!==null); }
// "precisa de N, tem M" da configuração que ficou sem recurso na fazenda (a equipe simultânea passa do que existe)
function e3SemRec(i,pools){ for(let j=0;j<i.rp.itens.length;j++){ const x=i.rp.itens[j]; if(!x.semRec) continue; const rc=(i.cfs[j]&&i.cfs[j].rec)||{};
    for(const k of Object.keys(rc)){ const u=Number(rc[k])||0, p=pools[k]; if(p&&u>p.un) return 'precisa de '+nfa(u)+', tem '+nfa(p.un); } } return ''; }
// R3 do veredito: o que deixa a conta incompleta sem ser falta de recurso (sem conjunto, sem rendimento, janela, sequência, tarifa)
function e3Incompleto(oc){ const by={}, ord=[]; oc.forEach(i=>{ const rp=i.rp; const semR=rp.causa==='sem recurso na fazenda';
    const sal=(!semR&&!i.pend&&rp.saldo>1e-9)?rp.saldo:0, pend=(i.pend&&!semR)?1:0, conf=(rp.conflito&&!rp.conflitoEst)?1:0, tar=(!i.pend&&!rp.custoOk)?1:0;
    if(!sal&&!pend&&!conf&&!tar) return; const o=by[i.a.op]||(by[i.a.op]={sal:0,pend:{},conf:0,tar:0,mot:[]}); if(!o.mot.length&&!o.sal&&!o.conf&&!o.tar&&!Object.keys(o.pend).length) ord.push(i.a.op);
    o.sal+=sal; if(pend){ const c=rp.causa||'pendente'; o.pend[c]=(o.pend[c]||0)+1; } o.conf+=conf; o.tar+=tar;
    if(sal) (rp.motivos||[]).forEach(m=>{ if(m.indexOf(':')<0&&o.mot.indexOf(m)<0) o.mot.push(m); }); });
  return ord.map(op=>{ const o=by[op]; const t=[];
    if(o.sal>1e-9) t.push(nfa(o.sal)+' ha sem conjunto'+(o.mot.length?' ('+o.mot.join('; ')+')':''));
    Object.keys(o.pend).forEach(c=>t.push(o.pend[c]+(o.pend[c]>1?' ocorrências pendentes':' ocorrência pendente')+' ('+c+')'));
    if(o.conf) t.push(o.conf>1?o.conf+' sequências que não cabem na janela':'sequência que não cabe na janela'); if(o.tar) t.push('tarifa desconhecida');
    return op+' com '+t.join(', '); }).join('; '); }
// texto, aria-label e estado de uma célula recurso × mês (o mesmo fmtOcup da célula, do filtro, dos atalhos e do espelho)
function e3CelTxt(g,c){ return (c.ge?'≥ ':'')+(c.red?('precisa '+(c.nec<0?'horas':c.nec)):fmtOcup(c.ocup)); }
function e3CelAria(g,c,outN){ let t=g.nome+', '+c.mes+': '+fmtOcup(c.ocup)+', '+capH(c.d)+' h de '+capH(c.cap)+' h';
  if(c.dOth>1e-4) t+=' (desta safra '+capH(c.dThis)+' h; '+Object.keys(g.oth).filter(o=>g.oth[o][c.mi]>1e-4).map(o=>(outN[o]||o)+' '+capH(g.oth[o][c.mi])+' h').join('; ')+')';
  t+=', precisa de '+(c.nec<0?'horas':c.nec)+', tem '+nfa(g.un); if(c.ge) t+=', mais '+nfa(g.semH[c.mi])+' ha sem horas calculáveis'; return t; }
function e3Aperto(g){ const c=g.necMax; return c.nec<0?Infinity:c.nec/Math.max(g.un,1e-9); }
function etapa3(self,v,saf,ro){ const st=self.state; const S=safList(self); const me=S[saf]||{}; const E=capCalc(self,saf); const oc=E.oc, G=E.G;
  const outN={}; E.outras.forEach(o=>{ outN[o.id]=o.nome; });
  const cs=cultRows(self,saf), sp=semPlano(cs); const aPlano=cs.filter(c=>sp.indexOf(c)<0).reduce((a,c)=>a+(Number(c.v.area)||0),0);
  const cls={antes:0,fora:0,depois:0,cal:0}; oc.forEach(i=>{ cls[i.cls]++; });
  const ver=capVeredito(G,oc,{semPlano:sp.map(c=>({local:c.v.local,area:c.v.area})),aPlano,cls,ini:br(me.ini),outras:outN,pend:oc.filter(i=>i.pend).length,
    semHoras:oc.reduce((a,i)=>a+(i.rp.falta.semHoras||0),0),incompleto:e3Incompleto(oc),periodoCal:D2.meses[0][1]+' – '+D2.meses[D2.meses.length-1][1]});
  self.__e3={saf,oc,G,outras:E.outras,outN,pools:E.pools,recs:E.recs,ver};
  const COR={red:'#B42318',yellow:'#8A5A00',green:'#1E7A4C',gray:'#5B6660'};
  v.v3_ver=ver.txt; v.v3_vst='font-weight:700;color:'+(COR[ver.cor]||'#15201A')+';';
  // custo de operação (máquinas e pessoas): 2 casas e o qualificador do que entra e do que fica de fora
  const cop=oc.reduce((a,i)=>a+(Number(i.cop)||0),0); const antes=oc.filter(i=>i.cls==='antes'); const np=oc.filter(i=>i.pend).length;
  v.v3_cop=rs(cop); v.v3_copq=(antes.length?'inclui '+rs(antes.reduce((a,i)=>a+(Number(i.cop)||0),0))+' de antes de '+br(me.ini):'máquinas e pessoas, sem insumos')+(np?'; não inclui as ocorrências pendentes':'');
  // atalhos de capacidade (fora do role=status): em falta, um por recurso (do mais apertado); sem falta, o maior uso; somem com a g_cap aberta
  const capAb=!!st.capAberta, ver01=(ver.R==='R0'||ver.R==='R1'); const at=[];
  const atalho=(g,c,t,red)=>({t,al:t+': '+e3CelAria(g,c,outN)+'. Mostra as operações desse mês',go:()=>capSel(self,g.id,c.mi),st:'min-height:24px;'+(red?'color:#B42318;':'')});
  if(!ver01&&!capAb){ const reds=Object.values(G).filter(g=>g.reds.length).sort((a,b)=>e3Aperto(b)-e3Aperto(a));
    if(reds.length){ reds.slice(0,3).forEach(g=>{ const c=g.max||g.reds[0]; at.push(atalho(g,c,g.nome+' '+fmtOcup(c.ocup)+' · '+c.mes,true)); });
      if(reds.length>3) at.push({t:'e mais '+(reds.length-3),al:'e mais '+(reds.length-3)+' recursos em falta: abrir a capacidade por mês',go:()=>capTog(self),st:'min-height:24px;'}); }
    else { let b=null; Object.values(G).forEach(g=>{ const c=g.max; if(c&&c.ocup!==null&&c.ocup>0&&(!b||c.ocup>b.c.ocup+1e-12)) b={g,c}; });
      if(b) at.push(atalho(b.g,b.c,'Maior uso: '+b.g.nome+' '+fmtOcup(b.c.ocup)+' · '+b.c.mes,false)); } }
  v.v3_atalhos=at; v.v3_capexp=String(capAb); v.v3_captog=()=>capTog(self); v.v3_capt='Capacidade por mês '+(capAb?'▴':'▾'); v.v3_capab=capAb;
  // g_cap: recurso × mês (ocupação); só a célula com demanda desta safra é tocável (filtra a g_op); "—" e cinza ficam inertes
  const capF=(st.cap&&st.cap.saf===saf&&G[st.cap.rec])?st.cap:null; const gc=GR('g_cap_'+sk(saf));
  if(gc){ const mis=capMeses(me.ini,me.fim); gc._c0=gc._c0||gc.cols.slice(); gc.cols=gc._c0.filter(c=>!/^m\d+$/.test(c.k)||mis.indexOf(Number(c.k.slice(1)))>=0); }
  if(gc) gc.rows=E.recs.map(rr=>{ const g=G[rr.id]; const r={id:rr.id,v:{rec:g.nome},s:{rec:g.nome},p:{rec:[{k:'txt',t:g.nome}]}}; const mx=g.max;
    if(!mx){ r.v.maior=''; r.p.maior=[{k:'mut',t:'—'}]; r.s.maior=''; r.v.mes=''; r.p.mes=[{k:'mut',t:'—'}]; r.s.mes=''; }
    else { const t=fmtOcup(mx.ocup); r.v.maior=mx.ocup===null?1e9:mx.ocup; r.p.maior=[g.reds.length?{k:'cn',t,c:'red'}:{k:'txt',t}]; r.s.maior=t;
      r.v.mes=Number(D2.meses[mx.mi][0].replace('-','')); r.p.mes=[{k:'txt',t:mx.mes}]; r.s.mes=mx.mes; }
    g.cells.forEach(c=>{ const k='m'+c.mi;
      if(c.own){ const t=e3CelTxt(g,c); const on=!!capF&&capF.rec===g.id&&capF.mi===c.mi;
        r.p[k]=[{k:'act',t,fn:'capcel:'+g.id+'|'+c.mi,full:true,c:c.red?'red':'',on,al:e3CelAria(g,c,outN)+(on?'. Filtro ativo: toque de novo para ver todas':'. Mostra as operações desse mês')}]; r.v[k]=c.ocup===null?1e9:c.ocup; r.s[k]=t; }
      else if(c.dOth>1e-4){ const t='('+fmtOcup(c.ocup)+')'; r.p[k]=[{k:'mut',t}]; r.v[k]=''; r.s[k]=t; }
      else { r.p[k]=[{k:'mut',t:'—'}]; r.v[k]=''; r.s[k]=''; } });
    return r; });
  v.capcel=(arg)=>{ const a=String(arg).split('|'); capSel(self,a[0],Number(a[1])); };
  // linha de filtro (recurso × mês escolhido): números da célula, com o que vem de cada outra safra
  v.v3_fil=!!capF; v.v3_filx=()=>capSel(self,null,null);
  if(capF){ const g=G[capF.rec], c=g.cells[capF.mi]; const oth=Object.keys(g.oth).filter(o=>g.oth[o][c.mi]>1e-4);
    v.v3_filn=g.nome+' · '+c.mes; v.v3_filt=capH(c.d)+' h de '+capH(c.cap)+' h ('+fmtOcup(c.ocup)+')'+(oth.length?' · desta safra '+capH(c.dThis)+' h · '+oth.map(o=>(outN[o]||o)+' '+capH(g.oth[o][c.mi])+' h').join(' · '):'')
      +' · precisa de '+(c.nec<0?'horas':c.nec)+', tem '+nfa(g.un)+(c.ge?' · mais '+nfa(g.semH[c.mi])+' ha sem horas calculáveis':''); }
  else { v.v3_filn=''; v.v3_filt=''; }
  e3Op(self,saf,oc,G,capF);
}
// g_op: operação › atividade › talhão (› configuração, quando a atividade divide a área); 8 colunas, uma variável por coluna (§3.4)
function e3Op(self,saf,oc,G,capF){ const kF=capF?capF.rec:null; const pools=self.__e3.pools; const map={}; self.__opmap=map;
  const naConta=(i)=>i.mi>=0&&(!i.cls||i.cls==='cal');   // a mesma regra do capSaf: com etiqueta do calendário, fora da capacidade
  const base=capF?oc.filter(i=>i.mi===capF.mi&&naConta(i)&&cargaRec(i,kF)>1e-9):oc;
  const grupo=(lst)=>{ const by={}, ord=[]; lst.forEach(i=>{ let o=by[i.a.op]; if(!o){ o=by[i.a.op]={op:i.a.op,atv:{},ordA:[],its:[]}; ord.push(o); } o.its.push(i);
      let a=o.atv[i.a.nome]; if(!a){ a=o.atv[i.a.nome]={nome:i.a.nome,its:[]}; o.ordA.push(a); } a.its.push(i); });
    const d0=(its)=>its.map(i=>i.dt).sort()[0]||''; const cmp=(x,y)=>{ const a=d0(x.its), b=d0(y.its); return a<b?-1:(a>b?1:0); };
    ord.sort(cmp); ord.forEach(o=>o.ordA.sort(cmp)); return ord; };
  // conjunto e rendimento comuns às atividades em uso da operação (todas as ocorrências, mesmo com filtro)
  const comum={}; grupo(oc).forEach(o=>{ const L=o.ordA.map(a=>a.its[0].cfs); const uma=L.every(l=>l.length===1);
    const nomes=[...new Set(L.map(l=>(l[0]&&l[0].v.nome)||''))], rends=[...new Set(L.map(l=>String(rpNum(l[0]&&l[0].v.rend))))];
    comum[o.op]={divSo:(L.length===1&&L[0].length>1),n:L.length&&L[0].length,conj:(uma&&nomes.length===1)?nomes[0]:null,rend:(uma&&rends.length===1)?rpNum(L[0][0].v.rend):null,
      leaf:(L[0]&&L[0][0])?L[0][0].id:null,atv:(o.ordA[0]||{}).nome,nAtv:atvEmUso(oc,o.op).size}; });
  const H=(i)=>kF?cargaRec(i,kF):(i.pend?null:(Number(i.horas)||0));
  const somaH=(its)=>{ if(kF) return its.reduce((a,i)=>a+cargaRec(i,kF),0); return its.every(i=>i.pend)?'':its.reduce((a,i)=>a+(Number(i.horas)||0),0); };
  const rha=(its)=>{ const at=its.reduce((a,i)=>a+(Number(i.rp.alocado)||0),0), c=its.reduce((a,i)=>a+(Number(i.cop)||0),0); return at>1e-9?c/at:null; };
  const rend=(x)=>{ const n=rpNum(x); return (n===null||isNaN(n)||!(n>0))?null:n; };
  // Situação (§3.4): chips de problema onde ocorrem; "Janela não informada" e "Cabe na janela" só quando diferem do pai; etiqueta do calendário
  const avisos=(its)=>{ const o=[]; const pc={}; its.forEach(i=>{ if(i.pend){ const c=i.rp.causa||'pendente'; (pc[c]||(pc[c]=[])).push(i); } });
    Object.keys(pc).forEach(c=>{ const n=pc[c].length; const sr=c==='sem recurso na fazenda'?e3SemRec(pc[c][0],pools):'';
      o.push({k:'chip',t:c+(sr?' · '+sr:'')+(its.length>1?' · '+n+(n>1?' pendentes':' pendente'):(sr?'':' · pendente')),c:'red'}); });
    const sal=its.reduce((a,i)=>a+(i.rp.causa==='sem recurso na fazenda'?0:i.saldo),0); if(sal>1e-9) o.push({k:'chip',t:nfa(sal)+' ha sem conjunto',c:'red'});
    const nc=its.filter(i=>i.rp.conflito).length; if(nc) o.push({k:'chip',t:its.some(i=>i.rp.conflito&&!i.rp.conflitoEst)?'sequência não cabe na janela':'não cabe na janela nesta estimativa',c:'red'});
    if(its.some(i=>!i.pend&&!i.rp.custoOk)) o.push({k:'chip',t:'tarifa desconhecida',c:'yellow'});
    const cap={}; its.forEach(i=>{ if(!naConta(i)) return; cargaItens(i).forEach(c=>{ const g=G[c.k]; if(!g) return; const cel=g.cells[i.mi]; if(!cel.red) return;
        const q=cap[c.k]||(cap[c.k]={g,cel,ms:{}}); q.ms[i.mi]=1; if((cel.ocup===null?1e9:cel.ocup)>(q.cel.ocup===null?1e9:q.cel.ocup)) q.cel=cel; }); });
    Object.values(cap).forEach(q=>{ const n=Object.keys(q.ms).length; o.push({k:'chip',t:q.g.nome+' '+fmtOcup(q.cel.ocup)+' · '+q.cel.mes+(n>1?' (+'+(n-1)+(n>2?' meses)':' mês)'):''),c:'red'}); });
    return o; };
  const ETQ={antes:'antes do início da safra',fora:'fora do calendário',depois:'depois do fim da safra'};
  const etq=(its,um)=>{ const n={}; its.forEach(i=>{ if(i.cls&&i.cls!=='cal') n[i.cls]=(n[i.cls]||0)+1; }); return Object.keys(n).map(k=>({k:'chip',t:ETQ[k]+(um?'':' · '+n[k]),c:'gray'})); };
  const sitDe=(its,av)=>av.length?'Com pendência':(its.some(i=>i.rp.itens.some(e3SemJan))?'Janela não informada':'Cabe na janela');
  const sitP=(sit,pai,av,eq)=>{ let p=av.slice(); if(sit!=='Com pendência'&&sit!==pai) p.push(sit==='Cabe na janela'?{k:'chip',t:'Cabe na janela',c:'green'}:{k:'mut',t:'Janela não informada'});
    p=p.concat(eq); return p.length?p:[{k:'mut',t:''}]; };
  const linha=(id,nome,its,pai,tipo,un)=>{ const av=avisos(its); const sit=sitDe(its,av); const r={id,ro:true,v:{nome,sit},s:{nome,sit},p:{}};
    r.p.sit=sitP(sit,pai,av,etq(its,tipo==='oc'));
    const fx=e3Faixa(its); if(tipo==='oc') dcol(r,'data',its[0].dt); else dcol(r,'data',its.map(i=>i.dt).sort()[0],fx);
    const A=its.reduce((a,i)=>a+(Number(i.area)||0),0); r.v.area=A; r.s.area=nfa(A)+' '+un; r.p.area=[{k:'txt',t:r.s.area}];
    const h=somaH(its); r.v.horas=h; if(h===''){ r.p.horas=[{k:'mut',t:''}]; }
    const c=rha(its); r.v.rha=c===null?'':c; r.s.rha=c===null?'':rs(c)+'/'+un; r.p.rha=c===null?[{k:'mut',t:''}]:[{k:'txt',t:r.s.rha}];
    return r; };
  const x0={};
  const rows=grupo(base).map(o=>{ const cm=comum[o.op]||{}; const id='op:'+o.op; const r=linha(id,o.op,o.its,'','op','ha-op');
    r.p.nome=[{k:'b',t:o.op},{k:'mut',t:cm.nAtv+(cm.nAtv>1?' atividades':' atividade')}];
    const opConj=!!cm.conj&&!cm.divSo, opRend=opConj&&cm.rend!==null;
    r.v.conj=cm.divSo?cm.n+' conjuntos':(cm.conj||'varia'); r.s.conj=r.v.conj; r.p.conj=[{k:opConj?'txt':'mut',t:r.v.conj}];
    r.v.rend=opRend?cm.rend:''; r.s.rend=cm.divSo?'':(opRend?nf(cm.rend,2)+' ha/h':'varia'); r.p.rend=[{k:opRend?'txt':'mut',t:r.s.rend}];
    map[id]={t:'op',op:o.op,comum:opRend,leaf:cm.leaf};
    if(r.v.sit==='Com pendência'||capF) x0[id]=true;
    r.kids=o.ordA.map(a=>{ const aid='at:'+o.op+'|'+a.nome; const cfs=a.its[0].cfs; const div=cfs.length>1;
      const rep=new Set(a.its.map(i=>i.c.id)).size<a.its.length; const ra=linha(aid,a.nome,a.its,r.v.sit,'at',rep?'ha-op':'ha');
      ra.p.nome=[{k:'txt',t:a.nome}];
      const vz=(f)=>{ ra.v[f]=''; ra.p[f]=[{k:'mut',t:''}]; ra.s[f]=''; };
      if(div){ ra.v.conj=cfs.length+' conjuntos'; ra.s.conj=ra.v.conj; ra.p.conj=[{k:'mut',t:ra.v.conj}]; vz('rend'); }
      else { const rr=rend(cfs[0].v.rend);
        if(opConj) vz('conj'); else { ra.v.conj=cfs[0].v.nome; ra.s.conj=ra.v.conj; ra.p.conj=[{k:'txt',t:ra.v.conj}]; }
        if(opRend) vz('rend'); else { ra.v.rend=rr===null?'':rr; ra.s.rend=rr===null?'sem rendimento':nf(rr,2)+' ha/h'; ra.p.rend=[{k:rr===null?'mut':'txt',t:ra.s.rend}]; } }
      map[aid]={t:'at',op:o.op,atv:a.nome,div,leaf:cfs[0]?cfs[0].id:null};
      if(capF||ra.v.sit==='Com pendência') x0[aid]=true;
      ra.kids=a.its.slice().sort((p,q)=>p.dt<q.dt?-1:(p.dt>q.dt?1:0)).map(i=>{ const oid='oc:'+i.c.id+'|'+i.a.id+'|'+i.dt; const ro=linha(oid,i.c.v.local+' · '+i.c.v.cult+' '+i.c.v.var,[i],ra.v.sit,'oc','ha');
        ro.p.nome=[{k:'txt',t:ro.v.nome}]; ['conj','rend'].forEach(f=>{ ro.v[f]=''; ro.s[f]=''; ro.p[f]=[{k:'mut',t:''}]; });
        // o filtro e a busca da grade leem as folhas: a ocorrência leva o conjunto e o rendimento no texto (a célula fica vazia, a linha-pai mostra)
        if(!div&&cfs[0]){ const rr=rend(cfs[0].v.rend); ro.s.conj=cfs[0].v.nome; ro.s.rend=rr===null?'sem rendimento':nf(rr,2)+' ha/h'; }
        if(i.pend&&!kF){ ro.v.horas=''; ro.p.horas=[{k:'mut',t:''}]; }
        { const at=Number(i.rp.alocado)||0; const c=at>1e-9?(Number(i.cop)||0)/at:null; ro.v.rha=c===null?'':c; ro.s.rha=c===null?'':rs(c)+'/ha'; ro.p.rha=c===null?[{k:'mut',t:''}]:[{k:'txt',t:ro.s.rha}]; }
        map[oid]={t:'oc',op:o.op,atv:a.nome,div,i,leaf:i.cfs[0]?i.cfs[0].id:null};
        if(div){ ro.kids=i.rp.itens.map((x,j)=>{ const cid=oid+'|c'+j; const rc=(i.cfs[j]&&i.cfs[j].rec)||{}; const sem=x.r===null;
            const rx={id:cid,ro:true,v:{nome:x.nome,sit:'',conj:'',data:''},s:{nome:x.nome,sit:'',conj:x.nome,data:''},p:{nome:[{k:'txt',t:x.nome}],conj:[{k:'mut',t:''}],data:[{k:'mut',t:''}]}};
            const ch=[]; if(sem) ch.push({k:'chip',t:'sem rendimento',c:'red'}); if(x.emSeq) ch.push({k:'chip',t:x.seqEst?'em sequência nesta estimativa':'em sequência',c:'yellow'});
            rx.p.sit=ch.length?ch:[{k:'mut',t:''}]; rx.s.sit=ch.map(q=>q.t).join(' ');
            const rr=rend(i.cfs[j]&&i.cfs[j].v.rend); rx.v.rend=rr===null?'':rr; rx.s.rend=rr===null?'':nf(rr,2)+' ha/h'; rx.p.rend=[{k:rr===null?'mut':'txt',t:rx.s.rend}];
            rx.v.area=x.q; rx.s.area=nfa(x.q)+' ha'; rx.p.area=[{k:'txt',t:rx.s.area}];
            if(kF){ const u=Number(rc[kF])||0; if(u>0){ rx.v.horas=(Number(x.nh)||0)*u; } else { rx.v.horas=''; rx.p.horas=[{k:'mut',t:'não usa'}]; rx.s.horas='não usa'; } }
            else { rx.v.horas=sem?'':x.h; if(sem) rx.p.horas=[{k:'mut',t:''}]; }
            const cq=(x.q>0&&x.custo!==null)?x.custo/x.q:null; rx.v.rha=cq===null?'':cq; rx.s.rha=cq===null?'':rs(cq)+'/ha'; rx.p.rha=cq===null?[{k:'mut',t:''}]:[{k:'txt',t:rx.s.rha}];
            map[cid]={t:'cf',op:o.op,atv:a.nome,i,j,leaf:i.cfs[j]?i.cfs[j].id:null}; return rx; }); }
        return ro; });
      return ra; });
    return r; });
  const sp=GR('g_op'); sp.rows=rows; sp.x0=x0;
  const c6=sp.cols.find(c=>c.k==='horas'); if(c6){ if(c6._l0===undefined) c6._l0=c6.l; c6.l=kF?('Horas de '+G[kF].nome):c6._l0; } }
// toque na célula ou no atalho: grava state.cap (recurso × mês desta safra) e filtra a g_op; tocar de novo limpa
function capSel(self,rid,mi){ const cur=self.state.cap; const saf=self.state.saf; const igual=!rid||(!!cur&&cur.rec===rid&&cur.mi===mi&&cur.saf===saf);
  const st=g2st(self,'g_op'); const f=Object.assign({},st.f||{}); delete f.horas; const pa={f,x:null}; if(st.so&&st.so.k==='horas') pa.so=null; g2set(self,'g_op',pa);
  self.setState({cap:igual?null:{rec:rid,mi,saf}});
  setTimeout(()=>{ try{ const e=document.getElementById(igual?'saf-v3-ver':'saf-cap-filtro'); if(e){ e.scrollIntoView({block:'nearest'}); if(!igual) e.focus({preventScroll:true}); } }catch(x){} },80); }
function capTog(self){ const ab=!self.state.capAberta; self.setState({capAberta:ab});
  if(ab) setTimeout(()=>{ try{ const e=document.getElementById('saf-cap'); if(e) e.scrollIntoView({block:'nearest'}); }catch(x){} },80); }
// g_op → formulário Rendimento (§4.1): operação com conjunto e rendimento comuns abre a 1ª atividade em uso com "Todas"; atividade de uma
// configuração e talhão abrem "Só esta atividade" (talhão com "Neste talhão"); configuração abre a própria folha ("Nesta configuração")
function abrirRend(self,rid){ const m=(self.__opmap||{})[rid]; const saf=self.state.saf; if(!m||!saf) return; const gid=rendGid(saf); const sp=GR(gid);
  const tog=()=>{ const st=g2st(self,'g_op'); const x=Object.assign({},st.x||GR('g_op').x0||{}); x[rid]=!x[rid]; g2set(self,'g_op',{x}); };
  let esc='', ctx='';
  if(m.t==='op'){ if(!m.comum){ tog(); return; } esc='Todas as atividades da operação'; }
  else if(m.t==='at'){ if(m.div){ tog(); return; } esc='Só esta atividade'; }
  else if(m.t==='oc'){ esc=m.div?'':'Só esta atividade'; ctx='talhao'; }
  else ctx='cfg';
  if(!m.leaf||!sp) return; self._e3ctx=m; self._e3row=rid; g2open(self,sp,m.leaf,null); const fm=g2st(self,gid).fm; if(!fm) return;
  const pa={esc,ctx,colh:String(m.op||'').indexOf('Colheita')===0?'sim':'não'};
  g2set(self,gid,{fm:Object.assign({},fm,{draft:Object.assign({},fm.draft,pa),orig:Object.assign({},fm.orig,pa)})}); }
function abrirRec(self,rid){ const gid=rid==='oper'?'g_recp_pes':'g_recp_maq'; const sp=GR(gid); if(!sp) return; self._e3cap=rid; self._recPrev=null; g2open(self,sp,rid,null); }   // prévia recalculada com o plano atual
// origem da configuração (§4.1): "Padrão do cadastro (CD-02)" só quando igual ao conjunto padrão da operação; o rendimento calculado fica fora
function origemCfg(d){ const base=String(d.base||''); const c=(D2.conj||[]).find(x=>x.id===base); if(!c) return 'Ajustado nesta safra';
  const co=(D2.conj_opts||{})[base]; const N=(x)=>{ const n=g2num(x); return isNaN(n)?null:Math.round(n*1e6)/1e6; }; const eq=(a,b)=>N(a)===N(b); const AJ='Ajustado nesta safra';
  if(String(d.conj_id||'')!==String(co?co.atual:base)) return AJ; const calc=!!c.larg; if((d.modo==='Informado')===calc) return AJ;
  if(calc){ if(!eq(d.larg,c.larg)||!eq(d.vel,c.vel)||!eq(d.efic,c.efic)) return AJ; } else if(!eq(d.rend,c.rend)) return AJ;
  for(const f of ['maq','impl','pess','pess_rs','diesel']) if(!eq(d[f],c[f])) return AJ;
  return 'Padrão do cadastro (CD-02)'; }
// janela de cada atividade em uso da operação ("Todas" não copia janela)
function janOp(self,op){ const saf=self.state.saf; const e=self.__e3; if(!saf||!e) return ''; const uso=[...atvEmUso(e.oc,op)];
  const com=uso.map(a=>{ const ks=cfgsOf(self,saf,op,a); const j=ks.length===1?rpNum(ks[0].v.jan):null; return (j===null||isNaN(j))?null:a+' '+nfa(j)+' h'; }).filter(Boolean);
  return 'é de cada atividade · '+(com.length?com.length+' de '+uso.length+' com janela ('+com.join(', ')+')':'nenhuma das '+uso.length+' com janela')+' · para mudar, toque na atividade.'; }
// "Neste talhão" e "Nesta configuração": motivo, necessário × atendido × saldo (a mesma conta de repartir) e o decorrido
function e3Neste(m){ if(!m||!m.i) return ''; const rp=m.i.rp; const n=rp.nec, f=rp.falta; const hs=(hc,dc)=>' · '+nf(hc,1)+' horas-conjunto · '+nf(dc,1)+' h decorridas';
  const l=[m.i.c.v.local+' · '+m.i.c.v.cult+' '+m.i.c.v.var+' · '+br(m.i.dt),'Necessário: '+nfa(n.area)+' ha'+(n.hconj===null?' · horas pendentes':hs(n.hconj,n.decorrido)),
    'Atendido: '+nfa(rp.alocado)+' ha'+(rp.pendente?'':hs(rp.hconj,rp.decorrido)),
    'Saldo: '+nfa(rp.saldo)+' ha'+(f.hconj===null?' · horas pendentes':' · faltam '+hs(f.hconj,f.decorrido).slice(3))+(f.hconj!==null&&f.semHoras>1e-9?' ('+nfa(f.semHoras)+' ha sem horas calculáveis)':'')];
  if(rp.motivos&&rp.motivos.length) l.push('Motivo: '+rp.motivos.join(' · ')); return l.join('\n'); }
function e3Nesta(m){ if(!m||!m.i) return ''; const x=m.i.rp.itens[m.j]; if(!x) return ''; return m.i.c.v.local+' · '+br(m.i.dt)+': precisa de '+nfa(x.nq)+' ha = '+nf(x.nh,1)+' h · faltam '+nfa(x.fq)+' ha = '+nf(x.fh,1)+' h'; }
// antes → depois ao salvar (§4.4): o "antes" sai do último desenho; o "depois", de ocorr + capSaf com o estado salvo
function opAntes(self,r){ const e=self.__e3; if(!e){ self._antes=null; return null; } const hs={}; e.oc.forEach(i=>{ hs[i.a.op]=(hs[i.a.op]||0)+(i.pend?0:(Number(i.horas)||0)); });
  self._antes={saf:e.saf,hs,G:e.G}; return null; }
function e3Diff(self,antes,op){ const saf=self.state.saf; if(!antes||!saf||antes.saf!==saf) return ''; const E=capCalc(self,saf); const out=[];
  if(op){ let h1=0; E.oc.forEach(i=>{ if(i.a.op===op) h1+=(i.pend?0:(Number(i.horas)||0)); }); const h0=antes.hs[op]||0; if(Math.abs(h1-h0)>0.05) out.push(op+': '+capH(h0)+' → '+capH(h1)+' h'); }
  Object.values(E.G).forEach(g=>{ const m=g.max; if(!m) return; const g0=antes.G[g.id]; const c0=g0?g0.cells[m.mi]:null; const t0=c0?fmtOcup(c0.ocup):'—', t1=fmtOcup(m.ocup); if(t0!==t1) out.push(g.nome+' '+m.mes+': '+t0+' → '+t1); });
  return out.length?' '+out.join(' · ')+'.':' Horas e capacidade não mudaram.'; }
function e3Foco(self,gid,rid){ if(!rid) return; g2set(self,gid,{fl:rid}); setTimeout(()=>{ try{ const r=document.querySelector('[role=row][data-rid="'+String(rid).replace(/"/g,'\\"')+'"]'); if(r){ r.scrollIntoView({block:'nearest'}); r.focus({preventScroll:true}); } }catch(x){} },120); }
// formulário Recurso (§4.2): horas de uma unidade, horas na safra e prévia (recalcula a demanda com o rascunho; ao salvar, todas as safras)
function recSub(self){ const saf=self.state.saf; const so=safList(self)[saf]; return 'Conta as safras abertas desta fazenda. Cadastro único no protótipo: mudar aqui muda também a outra fazenda.'+(so&&so.ro?' Para ajustar, abra uma safra aberta.':''); }
function recPrev(self,gid,d){ const saf=self.state.saf; const fm=g2st(self,gid).fm; if(!saf||!fm||!self.__e3) return null; const rid=fm.rid;
  const key=JSON.stringify([saf,rid,d.un,d.jornada,d.turnos,d.disp,d.abs]); if(!self._recPrev||self._recPrev.key!==key) self._recPrev={key,rid,E:capCalc(self,saf,rid,d)}; return self._recPrev; }
function recLive(self,gid,k,d){ const P=recPrev(self,gid,d); if(!P) return null; const e=self.__e3; const g1=P.E.G[P.rid], g0=e.G[P.rid]; if(!g1) return null;
  if(k==='h1_c'){ const m=g1.max; if(!m) return 'sem demanda desta safra no calendário'; return capH(g1.porUn[m.mi])+' h em '+m.mes; }
  if(k==='hs_c') return capH(g1.horasSafra)+' h ('+D2.meses[0][1]+' – '+D2.meses[D2.meses.length-1][1]+')';
  if(k==='prev_c'){ const m1=g1.max, m0=g0&&g0.max; if(!m1&&!m0) return 'Sem demanda desta safra no calendário.';
    let t='Maior uso: '+(m0?fmtOcup(m0.ocup):'—')+' → '+(m1?fmtOcup(m1.ocup):'—')+' ('+(m1||m0).mes+')';
    if(g1.reds.length){ const c=g1.necMax; t+=' · precisa de '+(c.nec<0?'horas':c.nec)+', tem '+nfa(g1.un); }
    const sr=(oc)=>{ const o={}; oc.forEach(i=>i.rp.itens.forEach(x=>{ if(x.semRec){ const kk=i.a.op+' · '+x.nome; o[kk]=(o[kk]||0)+1; } })); return o; };
    const a=sr(e.oc), b=sr(P.E.oc); [...new Set(Object.keys(a).concat(Object.keys(b)))].forEach(kk=>{ const dd=(b[kk]||0)-(a[kk]||0); const n=Math.abs(dd);
      if(dd) t+=' · '+kk+(dd>0?' deixa de trabalhar em ':' volta a trabalhar em ')+n+(n>1?' ocorrências':' ocorrência'); });
    return t; }
  return null; }
function recAfter(self,gid,rows,r){ const antes=self._antes; self._antes=null; self._recPrev=null; const rid=r.id; const saf=self.state.saf;
  const base=r.v.nome+': '+nfa(r.v.un)+(gid==='g_recp_pes'?' pessoas':' unidades')+', jornada de '+nfa(r.v.jornada)+' h.';
  self.setState({g2toast:base}); setTimeout(()=>{ self.setState({g2toast:base+e3Diff(self,antes,null)}); e3Foco(self,'g_cap_'+sk(saf),rid); },0); }
// painel "Resumo da safra" (§4.3): custo por cultura (operação + insumos do plano ÷ ha físico com plano), trabalho da safra e a conta
function resumoCultura(oc,ini){ const by={}, ord=[], vistos={};
  oc.forEach(i=>{ const cu=i.c.v.cult; let b=by[cu]; if(!b){ b=by[cu]={cult:cu,area:0,cop:0,cins:0,npend:0,ntar:0,copAntes:0,cinsAntes:0}; ord.push(b); }
    if(!vistos[i.c.id]){ vistos[i.c.id]=1; b.area+=Number(i.area)||0; } b.cop+=Number(i.cop)||0; b.cins+=Number(i.cins)||0;
    if(i.pend) b.npend++; else if(!i.rp.custoOk) b.ntar++; if(ini&&i.dt<ini){ b.copAntes+=Number(i.cop)||0; b.cinsAntes+=Number(i.cins)||0; } });
  ord.forEach(b=>{ b.tot=b.cop+b.cins; b.rha=(b.npend||b.ntar)?null:(b.area?b.tot/b.area:null); }); return ord; }
function resumoVals(self,v){ const st=self.state; const saf=st.saf; const e=self.__e3;
  v.rs_abrir=()=>{ self.setState({rsOpen:true}); setTimeout(()=>{ try{ const a=document.querySelector('aside[aria-label="Resumo da safra"]'); const b=a&&a.querySelector('button[aria-label=Fechar]'); if(b) b.focus(); }catch(x){} },80); };
  v.rs_open=!!st.rsOpen&&!!e&&e.saf===saf&&(st.step||1)===3;
  const fechar=()=>{ self.setState({rsOpen:false}); setTimeout(()=>{ try{ const b=document.querySelector('[data-acao=resumo]'); if(b) b.focus(); }catch(x){} },60); };
  v.rs_fechar=fechar; v.rs_key=(ev)=>{ if(ev&&ev.key==='Escape'){ ev.preventDefault(); fechar(); } };
  if(!v.rs_open){ v.rs_lin=[]; v.rs_conta=[]; v.rs_saf=''; v.rs_nota=''; v.rs_trab=''; return; }
  const me=safList(self)[saf]||{}; const oc=e.oc; const L=resumoCultura(oc,me.ini); v.rs_saf=me.nome||'';
  const lin=L.map(b=>{ const nota=[]; if(b.rha===null) nota.push('parcial · '+(b.npend?b.npend+(b.npend>1?' ocorrências pendentes':' ocorrência pendente'):b.ntar+(b.ntar>1?' ocorrências com tarifa desconhecida':' ocorrência com tarifa desconhecida')));
      if(b.copAntes>0.005||b.cinsAntes>0.005) nota.push('inclui '+rs(b.copAntes)+' de operação e '+rs(b.cinsAntes)+' de insumos antes de '+br(me.ini));
      return {cult:b.cult,area:nfa(b.area)+' ha',cop:rs(b.cop),cins:rs(b.cins),rha:b.rha===null?'parcial':rs(b.rha)+'/ha',temNota:nota.length>0,nota:nota.join(' · ')}; });
  const T=(f)=>L.reduce((a,b)=>a+b[f],0); lin.push({cult:'Total',area:nfa(T('area'))+' ha',cop:rs(T('cop')),cins:rs(T('cins')),rha:'—',temNota:false,nota:''}); v.rs_lin=lin;
  const dm=demanda(self,saf); const Z=Object.values(dm).reduce((a,d)=>a+(Number(d.bruta)||0)*(Number(d.preco)||0),0); const Y=T('cins')-Z;
  v.rs_nota='Insumos do plano: dose × área × preço de todas as datas, antes do estoque. '+(Y>0.005?'Deles, '+rs(Y)+' são de antes de hoje ('+br(D2.hoje)+', já realizados) e '+rs(Z)+' de hoje em diante (a "Demanda bruta" da etapa 4).'
    :'Todos de hoje em diante ('+br(D2.hoje)+'): são a "Demanda bruta" da etapa 4.')+' A necessidade líquida está na etapa 4.';
  const S=(lst,f)=>lst.reduce((a,i)=>a+(Number(f(i))||0),0); const tr=(lst)=>nfa(S(lst,i=>i.area))+' ha-op · '+nf(S(lst,i=>i.horas),2)+' horas-conjunto · '+nf(S(lst,i=>i.hh),2)+' horas-homem · '+nf(S(lst,i=>i.diesel),2)+' L';
  const semL=oc.filter(i=>!e3Dinf(i)).length; const an=oc.filter(i=>i.cls==='antes');
  v.rs_trab=nfa(S(oc,i=>i.area))+' ha-op (hectares-operação) · '+nf(S(oc,i=>i.horas),2)+' horas-conjunto · '+nf(S(oc,i=>i.hh),2)+' horas-homem · '+nf(S(oc,i=>i.diesel),2)+' L de diesel estimado'+(semL?' ('+semL+(semL>1?' ocorrências sem L/h)':' ocorrência sem L/h)'):'')
    +(an.length?'; das quais antes do início: '+tr(an)+'; horas-homem no calendário: '+nf(S(oc.filter(i=>i.cls==='cal'),i=>i.hh),2):'')+'.';
  v.rs_conta=['capacidade = unidades × dias úteis × jornada × turnos × disponibilidade; para pessoas, × (1 − absenteísmo) e turnos = 1',
    'ocupação = demanda ÷ capacidade; a demanda inclui o que ainda não tem alocação (PRD 53.2)',
    'necessárias = o maior entre teto(horas ÷ horas de uma unidade) e a maior equipe que trabalha ao mesmo tempo',
    'soma as safras abertas desta fazenda',
    'dias úteis: '+D2.meses.map(m=>m[1]+' '+(D2.dias[m[0]]||0)).join(' · '),
    'estimativa mensal: a ocorrência entra inteira no mês da data e não prova viabilidade; o conflito por semana e turno fica em Ordem de Serviço › Recursos',
    'a capacidade usa o plano inteiro, pela data do plano, sem descontar o realizado das O.S.',
    'sem janela, o prazo por talhão não é verificado',
    'ha-op: cada passada conta; Custo R$/ha-op = custo da operação ÷ ha-op; custo total R$/ha da cultura = (operação + insumos) ÷ área com plano (PRD 44.1, 51.4)',
    'ocorrências antes do início, fora do calendário ou depois do fim contam no custo e não na capacidade'].map(t=>({t})); }
// CAL-01 na etapa 4 (demanda de insumos), 2ª linha do estoque apto: quanto dele outras origens usam antes (safra anterior, reserva de outro destino) ou, sem isso, o reservado
function notaEst(d,dec){ return (d.liq>0.001&&d.antes>0.001)?[{k:'br'},{k:'mut',t:'usado antes: '+nf(d.antes,dec)}]:(d.res>0.001?[{k:'br'},{k:'mut',t:'res. '+nf(d.res,dec)}]:[]); }
// solicitações enviadas: as iniciais (D2.sol) + as gravadas no navegador (mesmo registro que a Compra de insumos lê)
const SOL_KEY='talhao-os-compras-v1';
function solLer(){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); return (o&&o.sols)||{}; }catch(e){ return {}; } }
function solGravar(rec){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null')||{v:1,sols:{}}; o.sols=o.sols||{}; o.sols[rec.safra]=rec; localStorage.setItem(SOL_KEY,JSON.stringify(o)); return true; }catch(e){ return false; } }
function solMap(self){ if(self.state.sol) return self.state.sol; if(!self._sol0) self._sol0=Object.assign({},D2.sol,solLer()); return self._sol0; }
// andamento gravado pela Compra de insumos (talhao-os-compras-v1 · proc): o planejamento vê em que pé está a compra da mesma solicitação
function solEstado(saf,sol){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); const p=o&&o.proc&&o.proc[saf];
  return (p&&sol&&p.sol===sol.id&&(p.comp||0)===(sol.comp||0)&&p.estado&&p.estado!=='A cotar')?p.estado:''; }catch(e){ return ''; } }
function solHref(saf,sol){ return 'CMP.dc.html#sol='+encodeURIComponent(sol.id)+'&saf='+encodeURIComponent(saf); }
function proxSaf(self,r){ if(r.ro) return ['Consultar safra',2];
  const cs=cultsDe(self,r.id); if(!cs.length) return ['Continuar: planejar talhões',2];
  const sp=semPlano(cs).length; if(sp) return ['Continuar: aplicar plano em '+sp+(sp>1?' cultivos':' cultivo'),2];
  if(!solMap(self)[r.id]) return ['Continuar: enviar demanda para cotação',4];
  return ['Continuar: dimensionar operações e recursos',3]; }
function PREVALS(self,v){ cenOuvir(self); compRend(self,self.state.saf||null);
  { const gs=GR('g_sug'); if(gs) gs.rows=sgRows(self); }   /* Sugestões pelas análises (SOLO-01 §3.4) */
  const st=self.state; const saf=st.saf||null; const safObj=saf?(g2rows(self,GR('g_saf')).find(r=>r.id===saf)):null; const ro=!!(safObj&&safObj.ro);
  // ---- etapa 1: contagens por safra ----
  g2rows(self,GR('g_saf')).forEach(r=>{ const cs=cultsDe(self,r.id); r.v.n=cs.length; r.v.area=cs.reduce((s,c)=>s+(Number(c.v.area)||0),0);
    const est=r.v.estado||'Rascunho'; r.p.estado=[{k:'chip',t:est,c:(est==='Encerrada'?'gray':(est==='Em planejamento'?'green':'yellow'))}].concat(r.id===saf?[{k:'chip',t:'Selecionada',c:'blue'}]:[]);
    r.v.periodo=safPeriodo(r.v.ini,r.v.fim)||r.v.periodo||''; r.p.nome=[{k:'b',t:r.v.nome},{k:'mut',t:r.v.periodo}].concat(r.ro?[]:[{k:'act',t:'Editar',fn:'safedit:'+r.id,lk:true}]); r.s.nome=r.v.nome;
    const px=proxSaf(self,r); r._prox=px[1]; r.dr='open_'+r.id; r.drDup=true;   // o clique na linha repete o botão "Continuar" da linha: uma parada de Tab só (v3.1)
    r.p.acao=[{k:'act',t:px[0],fn:'pickat:'+r.id+'|'+px[1],u:false}]; r.s.acao=px[0]; });
  // ---- etapa 2: partes calculadas do cultivo (plano aplicado, ajustes) ----
  const adj=adjOf(self);
  ['S2627','S27SF','S2526','LG2627','NOVA'].forEach(k=>{ delete G2DISP['g_cult_'+k]; });
  self.__oc=(saf&&(st.step||1)===2)?syncTalhoes(self,saf,v):null;
  // etapa 3: valores de partida (o bloco só aparece com safra e plano; os buracos existem sempre)
  Object.assign(v,{v3_ver:'',v3_vst:'',v3_cop:'',v3_copq:'',v3_atalhos:[],v3_capexp:'false',v3_capt:'Capacidade por mês ▾',v3_capab:false,v3_fil:false,v3_filn:'',v3_filt:''});
  v.v3_captog=()=>capTog(self); v.v3_filx=()=>capSel(self,null,null);
  self.__e3=null;
  if(!saf) return;
  // ---- etapa 3: Dimensione operações e recursos (ESPECIFICACAO etapa-unica-3-4-5): veredito, capacidade por mês e operações ----
  // safra encerrada: recursos também só em consulta (PRD 52.1); a prévia mostraria 0 % enquanto salvar muda as safras abertas
  ['g_recp_maq','g_recp_pes'].forEach(g=>{ const sp=GR(g); if(sp) g2rows(self,sp).forEach(r=>{ r.ro=ro; }); });
  if((st.step||1)===3) etapa3(self,v,saf,ro);
  // ---- etapa 4: demanda de insumos ----
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
          o:d.memo.map(t=>({t})).concat(sol?[{t:'Ver '+sol.id+' na Compra de insumos',h:solHref(saf,sol)}]:[]) }; dcol(kr,'uso',d.uso);
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
function EXTRAVALS(self,v){ try{ window.__safSelf=self; }catch(e){}   // testes leem o estado (OC-13)
  const st=self.state; const step=st.step||1; const saf=st.saf||null;
  const safRows=g2rows(self,GR('g_saf')); const safObj=saf?safRows.find(r=>r.id===saf):null; const ro=!!(safObj&&safObj.ro);
  const temPlano=saf && cultRows(self,saf).some(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; });
  // 4 etapas (05/10/2026: as antigas 3, 4 e 5 viraram "Dimensione operações e recursos"); sem plano (R0) o bloco da etapa 3 não aparece
  for(let i=1;i<=4;i++) v['s'+i]=(step===i); v.s3=step===3&&!!temPlano;
  const whys={}; for(let i=2;i<=4;i++){ if(!saf) whys[i]='Escolha a safra'; else if(i>=3 && !temPlano) whys[i]='Aplique um plano'; }
  g2steps(self,v,'stp',4,step,whys);   // só informa (UX-ACAO-UNICA-20261003): avanço e retorno na área de ações
  v.saf_nome=safObj?safObj.v.nome:'nenhuma safra escolhida'; v.saf_ro=ro; v.saf_ok=!!saf; v.saf_none=!saf;
  v.ctx_saf=safObj?(safObj.v.nome+(ro?' · consulta':'')):'Nenhuma safra escolhida';
  v.ctx_faz='Fazenda '+((safObj&&safObj.v.faz)||'Santa Rita');
  for(const k of ['S2627','S27SF','S2526','LG2627','NOVA']){ v['cult_'+k]=(saf&&sk(saf)===k); v['cap_'+k]=(saf&&sk(saf)===k); }
  const cs=cultRows(self,saf); const area=cs.reduce((a,c)=>a+(Number(c.v.area)||0),0); const comp=cs.filter(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; }).length;
  const adj=adjOf(self); const naj=cs.reduce((a,c)=>a+Object.keys(adj[c.id]||{}).length,0);
  const sp=semPlano(cs);
  // faixa de resumo (§3.4): hectares por classe; os chips contam talhões pela Situação. Safra encerrada: consulta dos cultivos dela
  const oci=self.__oc; v.k2=(oci&&oci.band)?ocFaixaTxt(oci.band,oci.linhas,talTot(oci.safra.faz)):(cs.length+' cultivos · '+nf(area)+' ha · '+comp+' com plano'+(sp.length?' · '+sp.length+' sem plano':'')+' · '+naj+(naj===1?' ajuste local':' ajustes locais'));
  // ação primária por etapa: nomeia o próximo passo (na etapa 2, o que falta: aplicar plano; depois, avançar)
  const cultSp={}; sp.forEach(c=>{ (cultSp[c.v.cult]||(cultSp[c.v.cult]=[])).push(c.id); }); const cuK=Object.keys(cultSp).sort((a,b)=>cultSp[b].length-cultSp[a].length)[0];
  const apIds=cuK?cultSp[cuK]:[]; const apT='Aplicar plano em '+apIds.length+(apIds.length>1?' cultivos':' cultivo')+(Object.keys(cultSp).length>1?' de '+cuK.toLowerCase():'');
  const solA=saf?solMap(self)[saf]:null; const enviado=!!solA;
  const p6=(enviado&&!v.k6pend)?{t:'Abrir Compra de insumos ›',h:solHref(saf,solA),a:'abrir'}:{t:'Enviar para cotação',fn:()=>enviar(self),a:'comando'};
  v.sol_link=v.sol_link&&!p6.h;   // "Abrir em Compra de insumos ›" do bloco só quando a primária é enviar (complemento pendente): sem cópia do mesmo link
  safAcoes(self,v,{step,saf,ro,cs,sp,apIds,apT,cultSp,temPlano,p6});
  // escolher safra (botão da linha)
  v.pick=(id)=>{ g2etapa(self,{saf:id,step:2,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')}); };
  v.pickat=(arg)=>{ const a=String(arg).split('|'); const id=a[0], s=Number(a[1])||2; g2etapa(self,{saf:id,step:s,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')+' · '+SAF_CURTO[s-1]}); };
  safRows.forEach(r=>{ v['open_'+r.id]=()=>v.pickat(r.id+'|'+(r._prox||2)); });
  v.safedit=(id)=>{ const sp=GR('g_saf'); const r=g2rows(self,sp).find(x=>x.id===id); if(!r) return; const dr=r.dr; r.dr=null; g2open(self,sp,id,null); r.dr=dr; };
  v.applyone=(cid)=>openApply(self,[cid]); v.openlp=(cid)=>openLP(self,cid);
  Object.keys(D2.talhoes||{}).forEach(t=>{ v['div_'+t]=()=>openDiv(self,t); }); v.divide=(t)=>openDiv(self,t);
  v.planejar=(t)=>abrirPlanejar(self,t); v.vincular=(arg)=>{ const a=String(arg).split('|'); abrirVincular(self,a[0],a[1]); };
  v.abrirsaf=(arg)=>{ const a=String(arg).split('|'); abrirCultivo(self,a[0],a[1]||''); };
  // painéis
  apVals(self,v); lpVals(self,v); divVals(self,v); sgVals(self,v); pqSafVals(self,v);
  try{ window.__solo={cen:()=>cenGet(),aceitarLote:(itens,ch,a)=>cenMudar(self,c=>soloAceitarLote(c,itens,ch,a||'Ana')),desfazer:(k,ch,a)=>cenMudar(self,c=>soloDesfazer(c,k,'desfeito',ch,a||'Ana')),
    registrar:(d,ch,a)=>cenMudar(self,c=>soloRegistrar(c,d,ch,a||'Ana')),validar:(id,ch,a)=>cenMudar(self,c=>soloValidar(c,id,ch,a||'Ana')),   /* teste: o que outra aba (AG-02) grava */
    sugs:(saf)=>sgSugs(self,saf||self.state.saf).map(x=>x.s),
    ocorr:(saf)=>ocorr(self,saf||self.state.saf).map(o=>({cid:o.c.id,local:o.c.v.local,atv:String(o.a.id),nome:o.a.nome,op:o.a.op,dt:o.dt,incl:o.incl,horas:o.horas,prods:o.prods.map(p=>({nome:p.nome,dose:p.dose,q:p.q,orig:p.orig,laudo:p.laudo}))})),
    dem:(saf)=>{ const m=demanda(self,saf||self.state.saf); const o={}; Object.keys(m).forEach(k=>{ o[k]={bruta:m[k].plano,un:m[k].un,preco:m[k].preco,memo:m[k].memo}; }); return o; },salvar:(c)=>{ cenSave(c); self.setState({cenrev:Date.now()}); }}; }catch(e){}
  // SAF.dc.html#saf=S27SF&passo=demanda (vindo da Compra de insumos): abre a safra na etapa pedida, uma vez e a cada troca de endereço
  // endereço por nome (#saf=<id>&passo=safra|cultivos|operacoes|demanda[&cult=<id>]); o antigo etapa=N continua lido (SAF_PASSO)
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const ms=/[#&]saf=([^&]+)/.exec(h); if(!ms) return;
    const me=/[#&]etapa=(\d+)/.exec(h), mp=/[#&]passo=([a-z]+)/.exec(h), mc=/[#&]cult=([^&]+)/.exec(h);
    const r=g2rows(self,GR('g_saf')).find(x=>x.id===ms[1]); if(!r) return; const e=safPasso(mp?mp[1]:'',me?Number(me[1]):null);
    const msg=/[#&]sug=1/.test(h);   /* vindo do AG-02 (Ver no plano): abre as Sugestões pelas análises */
    setTimeout(()=>{ self.setState({saf:r.id,step:e,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+r.v.nome+' · '+SAF_CURTO[e-1]}); if(mc&&e===2) setTimeout(()=>abrirCultivo(self,r.id,mc[1]),90); if(msg&&e===2) setTimeout(()=>{ if(sgN(self,r.id)) sgAbrir(self); },120); },0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
}
// ---- UX-ACAO-UNICA-20261003 · área de ações do Planejar safra (DS-02, DS-33 §74.5.7.1, DS-61) ----
// Uma primária e uma rota de avanço por etapa; a faixa só informa. Retorno secundário nomeia a etapa anterior (na etapa 2, voltar à
// escolha é o "Trocar safra" do topo: sem cópia aqui). Pendência mostra a causa e um passo que resolve (Aplicar plano), sem aplicar e
// avançar em silêncio. Avançar só troca de etapa: não envia cotação, não publica, não aprova. Na revisão (etapa 4), "Corrigir cultivos"
// leva aos cultivos sem plano e "Voltar à revisão" devolve à mesma posição, com filtros e rascunho da tela preservados (estado).
const SAF_CURTO=['Escolha da safra','Cultivos e planos','Operações e recursos','Demanda de insumos'];
function safMaior(cs){ const by={}; cs.forEach(c=>{ (by[c.v.cult]||(by[c.v.cult]=[])).push(c.id); }); const k=Object.keys(by).sort((a,b)=>by[b].length-by[a].length)[0]; return k?{ids:by[k],cult:k,mix:Object.keys(by).length>1}:{ids:[],cult:'',mix:false}; }
function safAplicarT(m){ return 'Aplicar plano em '+m.ids.length+(m.ids.length>1?' cultivos':' cultivo')+(m.mix?' de '+m.cult.toLowerCase():''); }
function safLocs(cs){ return cs.slice(0,4).map(c=>c.v.local).join(', ')+(cs.length>4?' e mais '+(cs.length-4):''); }
function safRolagem(){ const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div');
  return (col&&col.scrollHeight>col.clientHeight+1&&getComputedStyle(col).overflowY==='auto')?col:m; }
function safCorrigir(self,ids){ const r=safRolagem(); const m=document.querySelector('main[data-scroll]');
  self.__revPos={top:r?r.scrollTop:0,rolas:m?[...m.querySelectorAll('.g2rola,.rola')].map(x=>x.scrollTop):[],foco:'[data-acoes] [data-acao=corrigir]'};
  g2etapa(self,{step:2,corr:{ids:ids.slice()}});
  setTimeout(()=>{ try{ const row=document.querySelector('[role=row][data-rid="'+ids[0]+'"]'); if(row){ row.scrollIntoView({block:'center'}); row.focus({preventScroll:true}); } }catch(e){} },120); }
// atalho para o cultivo que responde pela saída: "Informar colheita" só quando o painel dele tem o campo (sem plano, safra aberta, fora de
// ciclo vinculado); com plano a colheita sai do plano e o atalho só abre o cultivo ("Ver"); safra encerrada também é "Ver" (revisão SAF, S3.3)
function lnkSaida(self,S,o,saf){ const fech=!!(S[o.saf]&&S[o.saf].ro); const r=cultsDe(self,o.saf).find(c=>c.id===o.id);
  const campo=!fech&&!!r&&!r.v.plano&&r.v.modo!=='vinc'&&o.classe!=='perene'&&o.classe!=='observado';
  return {t:(campo?'Informar colheita de ':'Ver ')+o.faixa+(o.safs.indexOf(saf)>=0?'':' na '+o.safnome)+' ›',fn:()=>abrirCultivo(self,o.saf,o.id)}; }
// frase de A conferir/pendência da etapa 2 (§5.1): até 3 talhões e "+N", com o atalho que resolve (informar colheita, mudar plantio)
function ocFrase(self,info,saf){ const out={t:'',lnks:[]}; if(!info||!info.linhas) return out; const S=info.S; const L=info.linhas.filter(l=>l.sit==='A conferir'); const ps=[];
  const nomeSaf=(o)=>o.safs.indexOf(saf)>=0?'':' na '+o.safnome;
  const NMAX=g2estreito()?1:3; L.slice(0,NMAX).forEach(l=>{ const by=info.byO;
    const po=Object.keys(l.pend_own)[0];
    if(po){ const p=l.pend_own[po][0]; const o=by[po]; const A=by[p[1]];
      if(o&&A&&o.safs.indexOf(saf)>=0&&p[0]!=='soma'){ const fech=!!(S[A.saf]&&S[A.saf].ro);
        ps.push(o.faixa+': sobreposição prevista de '+ocDias(p[4])+' com '+ocArt(A.cult)+' '+A.cult+' da '+A.safnome+' (até '+(A.fim!==null?ocBr(A.fim):'sem data')+').'+(fech?' A confirmação depende de quem responde pela '+A.safnome+'.':''));
        out.lnks.push({t:'Mudar plantio de '+o.faixa+' ›',fn:()=>abrirCultivo(self,saf,o.id,{pmin:true})});
        out.lnks.push(lnkSaida(self,S,A,saf)); return; }
      if(o&&A){ ps.push(o.faixa+': sobreposição prevista de '+ocDias(p[4])+' entre '+ocArt(A.cult)+' '+A.cult+nomeSaf(A).replace(' na ',' da ')+' e '+ocArt(o.cult)+' '+o.cult+nomeSaf(o).replace(' na ',' da ')+'.');
        const meu=A.safs.indexOf(saf)>=0?A:o; out.lnks.push(lnkSaida(self,S,meu,saf)); return; } }
    if(l.seq.length){ const x=by[l.seq[0][0]], y=by[l.seq[0][1]]; if(x&&y){
      ps.push(l.t+': '+ocArt(y.cult)+' '+y.cult+' '+(y.safs.indexOf(saf)>=0?'desta safra':'da '+y.safnome)+' começa em '+ocBr(y.ini)+'; a saída '+ocDe(x.cult)+' '+ocMinus(x.cult)+' é estimada em '+(x.fim!==null?ocBr(x.fim):'sem data')+' (sem plano, CD-02).');
      out.lnks.push(lnkSaida(self,S,x,saf)); return; } }
    if(l.conf>0.005){ const e=l.fora.find(o=>o.classe==='estimado'||o.classe==='semdata'); if(e){
      ps.push(l.t+': '+ocHa(l.conf)+' ha a conferir a partir de '+ocBr(l.desde)+'; a saída '+ocDe(e.cult)+' '+ocMinus(e.cult)+' da '+e.safnome+' é estimada (sem plano, CD-02).');
      out.lnks.push(lnkSaida(self,S,e,saf)); } } });
  out.t=ps.join(' ')+(L.length>NMAX?' +'+(L.length-NMAX)+' a conferir (ver Situação).':''); return out; }
// abre a safra (outra ou a mesma) na etapa 2 com o painel do cultivo; pmin: "Mudar plantio" já com o plantio mínimo (R-17)
function abrirCultivo(self,saf,cid,o){ if(saf!==self.state.saf||(self.state.step||1)!==2){ const h='#saf='+saf+'&passo=cultivos'+(cid?'&cult='+cid:''); let cur='';
    try{ cur=decodeURIComponent(location.hash||''); }catch(e){ cur=''; }
    if(cur!==h){ try{ location.hash=h; }catch(e){} return; }
    // mesmo endereço (2º toque no mesmo link): o hashchange não dispara; abre direto, como o abrirHash (revisão SAF, S3.5)
    const r=safById(self,saf); if(!r) return; self.setState({saf,step:2,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+r.v.nome+' · '+SAF_CURTO[1]});
    if(cid) setTimeout(()=>abrirCultivo(self,saf,cid,o),90); return; }
  if(!cid) return; const sp=GR('g_cult_'+sk(saf)); g2open(self,sp,cid,null);
  if(o&&o.pmin){ const fm=g2st(self,sp.id).fm; const info=self.__oc; if(!fm||!info) return; const r=cultsDe(self,saf).find(c=>c.id===cid); if(!r) return;
    const rec=ocCult(r,saf,safFaz(self,saf)); const chk=ocChecar(info.ctx,info.S,info.todos,info.todos,saf,cid,talhaoArea(rec.talhao)); if(!chk.o) return;
    const pm=ocPlantioMin(info.ctx,info.S,info.todos,saf,rec,ocBaseMin(chk),talhaoArea(rec.talhao),null);
    if(pm!==null) g2set(self,sp.id,{fm:Object.assign({},fm,{draft:Object.assign({},fm.draft,{plantio:ocIso(pm)})})}); } }
// endereço por nome: passo=safra|cultivos|operacoes|demanda; etapa=N antigo é sempre lido na numeração de 6 etapas (3, 4 e 5 → 3; 6 → 4);
// só saf=, ou etapa fora de 1–6, abre a demanda (4). O código novo nunca grava etapa= (§5.3)
const SAF_PASSO={safra:1,cultivos:2,operacoes:3,demanda:4};
const SAF_ETAPA6={1:1,2:2,3:3,4:3,5:3,6:4};
function safPasso(p,e){ if(p&&SAF_PASSO[p]) return SAF_PASSO[p]; if(e&&SAF_ETAPA6[e]) return SAF_ETAPA6[e]; return 4; }
function nSel(self,saf){ return Object.values((g2st(self,'g_cult_'+sk(saf)).sel)||{}).filter(Boolean).length; }
function safAcoes(self,v,x){ const st=self.state, step=x.step, ro=x.ro, corr=st.corr||null;
  const ir=(i)=>({t:'‹ '+SAF_CURTO[i-1],fn:()=>g2etapa(self,{step:i,corr:null}),to:i,a:'voltar'});
  const av=(i,t)=>({t:t+' ›',fn:()=>g2etapa(self,{step:i,corr:null}),to:i,a:'avancar'});
  const aplicar={t:x.apT,fn:()=>openApply(self,x.apIds),a:'resolver'};
  const nSp=x.sp.length; const semTxt=nSp+(nSp>1?' cultivos sem plano agronômico':' cultivo sem plano agronômico')+' ('+safLocs(x.sp)+')';
  let c={};
  if(step===1) c={};   // escolher é a ação da linha ("Próximo passo"); criar fica junto do título da lista
  else if(!x.saf) c={nota:'Nenhuma safra escolhida: escolha a safra para seguir.',prim:{t:'‹ Escolher a safra',fn:()=>g2etapa(self,{step:1}),to:1,a:'voltar'}};
  else if(step===2){ const info=self.__oc; const fr=ocFrase(self,info,x.saf);
    if(corr){ const pend=x.sp.filter(c=>corr.ids.indexOf(c.id)>=0); const m=safMaior(pend);
      const volta={t:'Voltar à revisão ›',fn:()=>{ const pos=self.__revPos||null; self.__revPos=null; g2etapa(self,{step:4,corr:null},pos); },to:4,a:'avancar'};
      c=pend.length?{nota:'Correção pedida pela revisão: '+pend.length+(pend.length>1?' cultivos sem plano':' cultivo sem plano')+' ('+safLocs(pend)+').',prim:{t:safAplicarT(m),fn:()=>openApply(self,m.ids),a:'resolver'},sec:volta}
                   :{nota:'Cultivos corrigidos: volte à revisão para conferir a demanda.',prim:volta}; }
    else if(ro) c={prim:av(3,'Ver operações e recursos')};
    else { const L=(info&&info.linhas)||[]; const sob=L.find(l=>l.sit==='Sobreposição');
      // "Corrigir" abre o cultivo desta safra que está na trava mostrada (o mais tardio do par), não o 1º do talhão (revisão SAF, S3.4);
      // a nota descreve essa mesma trava, sem repetir o rótulo "Sobreposição" (S4)
      if(sob){ const ids=(y)=>[y[2]].concat(String(y[1]).split('+')); const tv=sob.trav.find(y=>ids(y).some(i=>sob.own.some(q=>q.id===i)))||sob.trav[0];
        const o=ids(tv).map(i=>sob.own.find(q=>q.id===i)).find(Boolean)||sob.own[0];
        c={nota:'Sobreposição em '+sob.t+': '+ocMotivo(Object.assign({},sob,{trav:[tv]}),info).replace(/^Sobreposição: /,'')+'.',prim:{t:'Corrigir '+sob.t,fn:()=>{ if(o) abrirCultivo(self,x.saf,o.id); else openDiv(self,sob.t); },a:'resolver'},sec:x.cs.length?av(3,'Dimensionar operações'):null}; }
      else if(!x.cs.length){ const nl=L.filter(l=>l.sit==='Livre'), nc=L.filter(l=>l.sit==='A conferir'), nv=L.reduce((a,l)=>a+l.vinc.length,0); const b=(info&&info.band)||{};
        const sop=L.length&&L.every(l=>!l.planejar&&!l.vinc.length&&l.sit==='Perene');
        if(sop){ const o=L[0].fora.find(y=>y.classe==='perene'); const per=L.reduce((a,l)=>a+l.T,0);
          c={nota:'Todos os talhões estão com perenes da '+(o?o.safnome:'outra safra')+' neste período ('+ocHa(per)+' ha).',lnks:o?[{t:'Planeje por ela ›',fn:()=>abrirCultivo(self,o.saf,'')}]:[]}; }
        else { const ps=[]; if(nl.length) ps.push(nl.length+(nl.length>1?' talhões livres':' talhão livre')+' ('+ocHa(b.livre||0)+' ha)'); if(nc.length) ps.push(nc.length+' a conferir ('+ocHa(b.conf||0)+' ha)'); if(nv) ps.push(nv+(nv>1?' ciclos perenes a vincular':' ciclo perene a vincular'));
          c={nota:'Nenhum cultivo nesta safra'+(ps.length?': '+ps.join(', '):'')+'. Use Planejar ›'+(nv?' ou Vincular ciclo ›':'')+' na linha.'+(fr.t?' '+fr.t:''),lnks:fr.lnks}; } }
      else if(nSel(self,x.saf)) c={nota:(nSp?semTxt+'. ':'')+'Seleção ativa: o plano dos selecionados é aplicado pela barra da lista.',sec:av(3,'Dimensionar operações')};   // lote = comando da tarefa ativa (DS-02/DS-40): sem 2ª primária de "aplicar"
      else if(x.apIds.length) c={nota:semTxt+': sem plano não entram operações nem insumos.'+(fr.t?' '+fr.t:''),lnks:fr.lnks,prim:aplicar,sec:av(3,'Dimensionar operações')};
      else c={nota:fr.t||'',lnks:fr.lnks,prim:av(3,'Dimensionar operações')}; } }
  else if(!ro&&step===3&&!x.temPlano) c={volta:ir(2),nota:'Nenhum cultivo tem plano agronômico: operações, recursos e demanda dependem dele.',prim:x.apIds.length?aplicar:null};
  // etapa 3: cultivo sem plano vira só o atalho "Aplicar plano em N cultivos" (o veredito já diz o que ficou fora); falta de recurso é aviso,
  // não trava: planejar não reserva, não contrata e não compra (AGENTS §4)
  else if(step===3) c=Object.assign({volta:ir(2),prim:av(4,ro?'Ver demanda de insumos':'Conferir demanda de insumos')},(!ro&&x.apIds.length)?{lnks:[{t:x.apT,fn:()=>openApply(self,x.apIds)}]}:{});
  else if(step===4){ c={volta:ir(3)};
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
  const culturas=[...new Set(rows.map(r=>r.v.cult))]; const av=apAvalia(self,saf,rows,ap.plan); const tv={}, pv={}; av.trava.forEach(x=>{ tv[x.r.id]=x.t; }); av.pend.forEach(x=>{ pv[x.r.id]=x.t; });
  v.ap_itens=rows.map(r=>({t:r.v.local+' · '+r.v.cult+' '+r.v.var+' · '+nf(r.v.area)+' ha'+(planById(r.v.plano)?' · plano atual: '+planById(r.v.plano).nome:'')+(tv[r.id]?' · não recebe: '+tv[r.id]:(pv[r.id]?' · recebe com pendência: '+pv[r.id]:''))}));
  const nOk=rows.length-av.trava.length; v.ap_btn='Aplicar plano em '+nOk+(nOk===1?' cultivo':' cultivos');
  v.ap_titulo='Aplicar plano a '+rows.length+(rows.length>1?' cultivos':' cultivo'); v.ap_mix=culturas.length>1; v.ap_mixmsg='Culturas diferentes na seleção ('+culturas.join(', ')+'). Selecione cultivos de uma só cultura: o plano precisa respeitar a cultura.';
  const opts=culturas.length===1? D2.planos.filter(p=>p.cultura===culturas[0]):[];
  v.ap_opts=[{v:'',t:'Escolha o plano'}].concat(opts.map(p=>({v:p.id,t:p.nome+' v'+p.versao+' · '+p.atividades.length+' atividades'}))); v.ap_plan=ap.plan; v.ap_has_opts=opts.length>0; v.ap_no_opts=(culturas.length===1&&!opts.length);
  v.ap_setplan=(e)=>self.setState({ap:Object.assign({},self.state.ap,{plan:e.target.value,confirm:false,err:''})});
  const adj=adjOf(self); const subst=rows.filter(r=>r.v.plano); const najs=rows.reduce((a,r)=>a+Object.keys(adj[r.id]||{}).length,0);
  const nac=rows.reduce((a,r)=>a+soloNacSaf(self,r),0);   /* R16 (A13): o aceite guarda o plano; trocar o plano faz o uso da análise deixar de valer, sem apagá-lo */
  v.ap_confirm=!!ap.confirm; v.ap_normal=!ap.confirm; v.ap_err=ap.err||''; v.ap_haserr=!!ap.err;
  v.ap_cmsg='Isto substitui o plano de '+subst.length+(subst.length===1?' cultivo':' cultivos')+(najs?' e descarta '+najs+(najs===1?' ajuste local':' ajustes locais'):'')+(nac?'; '+nac+(nac===1?' uso da análise deixa':' usos da análise deixam')+' de valer (ficam gravados no laudo)':'')+'. O plano padrão e os demais cultivos não mudam.';
  v.ap_cancel=()=>self.setState({ap:null});
  v.ap_apply=()=>{ const a=self.state.ap; if(culturas.length>1) return; if(!a.plan){ self.setState({ap:Object.assign({},a,{err:'Escolha o plano a aplicar.'})}); return; }
    if(!nOk){ self.setState({ap:Object.assign({},a,{err:'Nenhum cultivo pode receber este plano: todos travam pela ocupação do talhão.'})}); return; }
    if(subst.length && !a.confirm){ self.setState({ap:Object.assign({},a,{confirm:true})}); return; } doApply(self,rows,a.plan); };
  v.ap_yes=()=>doApply(self,rows,self.state.ap.plan); v.ap_back=()=>self.setState({ap:Object.assign({},self.state.ap,{confirm:false})}); }
// R-16 lote: antes de confirmar, quem trava (não recebe) e quem recebe com pendência; cada cultivo é avaliado com o plano novo
function apAvalia(self,saf,rows,pid){ const out={trava:[],pend:[]}; const so=safList(self)[saf]; if(!pid||!planById(pid)||!so||so.ro) return out; const faz=so.faz;
  rows.forEach(r=>{ const rec=ocCult(r,saf,faz); rec.plano=pid; const av=ocAvaliaCultivo(self,saf,rec); if(av.erro) out.trava.push({r,t:av.erro}); else if(av.pend) out.pend.push({r,t:av.pend}); }); return out; }
function doApply(self,rows,pid){ const saf=self.state.saf; const gid='g_cult_'+sk(saf); const all=g2clone(soDaSafra(g2rows(self,GR(gid)))); const adj=JSON.parse(JSON.stringify(adjOf(self)));
  const av=apAvalia(self,saf,rows,pid); const fora=av.trava.map(x=>x.r.id); const ok=rows.filter(r=>fora.indexOf(r.id)<0);
  ok.forEach(r=>{ const x=g2find(all,r.id); if(x){ x.v.plano=pid; x.v.colheita=''; delete adj[r.id]; } });
  const pl=planById(pid); g2set(self,gid,{rows:all,sel:{}});
  const pend=av.pend.length?' Com pendência: '+av.pend.map(x=>x.t).join(' '):''; const tr=av.trava.length?' Não receberam ('+av.trava.length+'): '+av.trava.map(x=>x.r.v.local).join(', ')+'.':'';
  self.setState({adj,ap:null,g2toast:pl.nome+' v'+pl.versao+' aplicado a '+ok.length+(ok.length>1?' cultivos':' cultivo')+'.'+pend+tr+' Plano operacional, recursos e demanda recalculados.'}); }
// Insumos e doses de um cultivo, sem mudar o plano padrão. adj[cultivo] guarda só o que difere do padrão:
// 'atividade|i' = dose nova (número) ou '-' (insumo retirado deste talhão); 'atividade|+n' = insumo incluído {prod,grupo,un,preco,dose}.
// autocompletar do cadastro no "+ Incluir insumo nesta atividade": nome (semente com a variedade do cultivo), grupo, unidade e preço
function lpAc(self,A,cat,pk,upd,ERR,c,o){ const itens=cat.map(p=>({v:p.prod, t:prodNome(p.prod,c), sub:p.grupo+' · '+p.un+' · R$ '+nf(p.preco,2)+'/'+p.un}));
  return g2ac(self,'saf-lp-'+A,itens,pk||'',(val)=>{ const cur=self.state.lp; const er=Object.assign({},cur.err||{}); delete er['pick'+A]; upd({pick:Object.assign({},cur.pick||{},{[A]:val}),err:er}); },
    {ph:'Buscar insumo no cadastro', err:!!ERR('pick'+A), enter:()=>o.pkOk(), esc:()=>o.pkNo()}); }
function catalogo(){ if(catalogo._c) return catalogo._c; const m={}; D2.planos.forEach(pl=>pl.atividades.forEach(a=>a.prods.forEach(p=>{ if(!m[p.prod]) m[p.prod]={prod:p.prod,grupo:p.grupo,un:p.un,preco:p.preco}; })));
  catalogo._c=Object.values(m).sort((a,b)=>(a.grupo+' '+a.prod).localeCompare(b.grupo+' '+b.prod,'pt-BR')); return catalogo._c; }
function cultActs(self,gid,r){ if(!r||r.grp) return []; const pl=planById(r.v.plano); const na=Object.keys(adjOf(self)[r.id]||{}).length+soloNacSaf(self,r); const ro=!!r.ro;
  const t=(ro?'Ver insumos e doses de ':'Ajustar insumos e doses de ')+r.v.local;
  if(!pl||pl.cultura!==r.v.cult) return [{t, h:'Escolha um plano agronômico de '+r.v.cult+' e salve; depois ajuste os insumos só deste talhão.',
    go:()=>self.setState({g2toast:'Escolha e salve um plano agronômico de '+r.v.cult+' antes de ajustar os insumos.'})}];
  return [{t, h:(na?(na+(na>1?' ajustes deste talhão':' ajuste deste talhão')+' · '):'')+'Mude dose, retire ou inclua insumos só neste talhão; o plano padrão não muda.',
    go:()=>{ const cur=g2st(self,gid).fm; if(cur&&!cur.ro&&g2dirty(cur)){ self.setState({g2toast:'Salve ou descarte as alterações do cultivo antes de ajustar os insumos.'}); return; } g2set(self,gid,{fm:null}); openLP(self,r.id); }}]; }
/* painel de insumos (PRD 40): o rascunho marca a origem de cada dose (src: pela análise). Os aceites gravados entram no rascunho com a origem
   e nunca viram ajuste da sessão (R14); "Usar", "Retirar pela análise" e "Incluir calagem" só preenchem o rascunho; o Salvar grava (D-25) */
function openLP(self,cid){ const saf=self.state.saf; const c=cultRows(self,saf).find(r=>r.id===cid); if(!c) return; const a=adjOf(self)[cid]||{}; const d={}, rm={}, add={}, src={};
  Object.keys(a).forEach(k=>{ const val=a[k]; const parts=k.split('|'); const A=parts[0], pi=parts[1]||'';
    if(pi.charAt(0)==='+'){ (add[A]||(add[A]=[])).push({prod:val.prod,grupo:val.grupo,un:val.un,preco:val.preco,dose:String(val.dose).replace('.',',')}); }
    else if(val==='-') rm[k]=true; else d[k]=String(val).replace('.',','); });
  const pl=planById(c.v.plano);
  if(pl) soloAcAtivos(soloSaf(self).ac,cid,pl.id).forEach(x=>{ if(x.tipo==='incluir') return; const at=pl.atividades.find(q=>String(q.id)===String(x.atv.id)); const i=at?at.prods.findIndex(q=>q.prod===x.prod):-1; if(i<0) return;
    const key=String(at.id)+'|'+i; if(a[key]!==undefined) return; if(x.dose==='-') rm[key]=true; else d[key]=String(x.dose).replace('.',','); src[key]={laudo:x.laudo,dose:x.dose,ac:x.k}; });
  self.setState({lp:{cid,draft:d,rm,add,src,incl:{},inclRm:{},chave:'LP-'+cid+'-'+Date.now(),pick:{},orig:JSON.stringify({d,rm,add,incl:{},inclRm:{}}),warn:false,err:{},cmdErr:''},lpx:{},pq:null}); }
function lpVals(self,v){ const lp=self.state.lp; v.lp_open=!!lp; if(!lp) return; const saf=self.state.saf; const c=cultRows(self,saf).find(r=>r.id===lp.cid); if(!c){ v.lp_open=false; return; }
  const pl=planById(c.v.plano); const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); const ro=!!(c.ro||(safObj&&safObj.ro));
  const SG=soloSugsSaf(self,saf,c,true); const area=Number(c.v.area)||0; const sugBy={}; SG.sug.forEach(s=>{ if(s.tipo!=='incluir'&&!s.nega) sugBy[s.atv.id+'|'+s.prod]=s; });
  const acSt=soloAcAtivos(soloSaf(self).ac,c.id,c.v.plano); const acDe=(A,prod)=>acSt.find(x=>x.tipo!=='incluir'&&String(x.atv.id)===A&&x.prod===prod)||null;
  /* dose da análise mudada à mão (R15): o aceite ativo sobrescrito no rascunho ou o já substituído por ajuste manual → "ajustado pelo usuário" */
  const acMan=(A,prod)=>{ const x=soloSaf(self).ac[c.id+'|'+A+'|'+prod]; return !!(x&&(x.st==='ativo'||x.st==='substituído por ajuste manual')); };
  /* R11 no desfazer (revisão A5): uso da análise com O.S. fora de A liberar ou data passada fica travado no painel, com o motivo; o comando recusa igual */
  const cenC=soloSaf(self).c; const ngAc=(a0)=>a0?soloNega(cenC,a0):'';
  v.lp_titulo='Insumos e doses de '+c.v.local+' · '+c.v.cult+' '+c.v.var+', '+nf(c.v.area)+' ha';
  v.lp_sub='Plano padrão: '+pl.nome+' v'+pl.versao+' · plantio '+br(c.v.plantio)+'. '+(ro?'Safra encerrada: somente consulta.':'Mude a dose, retire ou inclua insumos só neste talhão. O plano padrão e os outros talhões não mudam.');
  /* laudo validado sem regra ou correção em outra safra (R17): uma frase só aqui, com o caminho para o laudo */
  v.lp_info=SG.info.map(t=>{ const m=/LAU-\d+/.exec(t); return {t, h:m?'AG-02.dc.html#'+m[0]:'AG-02.dc.html'}; }); v.lp_hasInfo=v.lp_info.length>0;
  v.lp_ro=ro; v.lp_edit=!ro; const ex=self.state.lpx||{};
  const upd=(patch)=>{ const cur=self.state.lp; self.setState({lp:Object.assign({},cur,patch,{warn:false,cmdErr:''})}); };
  const ERR=(k)=>(lp.err||{})[k]||'';
  const doseSt=(k,aj,dis,an)=>'width:84px;font-family:inherit;font-size:13px;padding:5px 7px;border-radius:8px;border:1px solid '+(ERR(k)?'#B42318':(an?'#1E5F8F':(aj?'#8A5A00':'#E4E9E5')))+';background:'+(dis?'#F4F6F3':(an?'#E3F0FB':(aj?'#FFF8E6':'#fff')))+';text-align:right;';
  const chipSt=(c0)=>'display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:700;color:'+(G2C[c0]||G2C.gray)[0]+';background:'+(G2C[c0]||G2C.gray)[1]+';';
  const pqAbre=(s,fid)=>{ self.__pqFoco=fid; self.setState({pq:{k:s.k,from:'lp'}}); };
  const usar=(s,key)=>{ const cur=self.state.lp; const d=Object.assign({},cur.draft), rr=Object.assign({},cur.rm||{}), sr=Object.assign({},cur.src||{}), er=Object.assign({},cur.err||{}); delete er[key];
    if(s.tipo==='retirar'){ rr[key]=true; delete d[key]; } else { d[key]=String(s.sug).replace('.',','); delete rr[key]; } sr[key]={laudo:s.laudo.id,dose:s.tipo==='retirar'?'-':s.sug,s}; upd({draft:d,rm:rr,src:sr,err:er}); };
  const grupos={}; pl.atividades.forEach(a=>{ const g=grupoGat(a.g.tipo); ((grupos[g]||(grupos[g]={}))[gatLabel(a.g)+'||'+gatOrder(a.g)]||(grupos[g][gatLabel(a.g)+'||'+gatOrder(a.g)]=[])).push(a); });
  const order=['DAP','DAC','DATA'].filter(g=>grupos[g]);
  v.lp_grupos=order.map(g=>({t:GLABEL[g],gats:Object.keys(grupos[g]).sort((x,y)=>{ const a=x.split('||')[1], b=y.split('||')[1]; return g==='DATA'? (a<b?-1:1) : (Number(a)-Number(b)); }).map(key=>{
      const atvs=grupos[g][key]; const gid=g+key; const open=ex[gid]!==false;
      return {t:key.split('||')[0], dt:br(dataAtv(c,atvs[0],pl)), sym:open?'▾':'▸', open, lab:(open?'Recolher ':'Expandir ')+key.split('||')[0], tog:()=>{ const x=Object.assign({},self.state.lpx||{}); x[gid]=!open; self.setState({lpx:x}); },
        atvs:atvs.map(a=>{ const aid='a'+a.id; const ao=ex[aid]!==false; const A=String(a.id); const rmMap=lp.rm||{}; const adds=((lp.add||{})[A])||[]; const SRC=lp.src||{};
          const prods=a.prods.map((p,i)=>{ const key=A+'|'+i; const removed=!!rmMap[key]; const dv=lp.draft[key]; const local=removed?0:((dv!==undefined&&dv!=='')?g2num(dv):p.dose);
              const an=!!SRC[key]; const a0=acDe(A,p.prod); const aj=!removed&&dv!==undefined&&dv!==''&&Math.abs(local-p.dose)>1e-9; const ng=ngAc(a0);
              const ajT=an?('pela análise · '+SRC[key].laudo+(ng?' · '+ng+': vale a dose da O.S.':'')):((a0||acMan(A,p.prod))?'ajustado pelo usuário':'dose deste talhão');
              /* linha "Análise sugere" (§3.2): só quando a sugestão difere do rascunho; ações secundárias que preenchem o rascunho */
              const s=sugBy[A+'|'+p.prod]; let sg=null;
              if(s&&!ro){ const curD=removed?0:(isNaN(local)?null:local);
                if(s.tipo==='retirar'&&!removed) sg={d:'retirar ('+(s.motivo||'pela análise')+')',q:soloQtdTxt(-cenQtd(curD||0,area),p.un,true)+(s.unico?' · a '+a.nome+' sai do '+c.v.local+' (único insumo)':''),u:'Retirar pela análise'};
                else if(s.tipo==='dose'&&(removed||curD===null||prCmp(curD,s.sug)!==0)) sg={d:soloDoseTxt(s.sug,s.un),q:soloQtdTxt(prSub(cenQtd(s.sug,area),cenQtd(curD||0,area)),p.un,true)+' no talhão',u:'Usar '+soloDoseTxt(s.sug,s.un)}; }
              const fid='lp_'+key.replace('|','_');
              return {grupo:p.grupo, nome:prodNome(p.prod,c), padrao:nf(p.dose,2)+' '+p.un+'/ha', v:removed?'':(dv!==undefined?dv:String(p.dose).replace('.',',')), un:p.un+'/ha', preco:rs(p.preco)+'/'+p.un,
                custo:removed?'—':(rs((isNaN(local)?0:local)*p.preco)+'/ha'), aj:aj||(an&&!removed), ajT, ajSt:chipSt(an?'blue':'yellow'), rmv:removed, rmT:an?('retirado pela análise · '+SRC[key].laudo+(ng?' · '+ng:'')):'retirado deste talhão', novo:false,
                err:ERR(key), hasErr:!!ERR(key), dis:ro||removed||!!ng, fid, ist:doseSt(key,aj,ro||removed||!!ng,an&&!removed),
                podeRet:!ro&&!removed&&!ng, podeDesf:!ro&&removed&&!ng, podeRest:!ro&&aj&&!ng,
                hasSug:!!sg, sugD:sg?sg.d:'', sugQ:sg?sg.q:'', sugU:sg?sg.u:'', sugPq:()=>{ if(s) pqAbre(s,'pq_'+fid); }, pqId:'pq_'+fid, sugGo:()=>{ if(s) usar(s,key); },
                set:(e)=>{ const cur=self.state.lp; const d=Object.assign({},cur.draft,{[key]:e.target.value}); const er=Object.assign({},cur.err||{}); delete er[key]; const sr=Object.assign({},cur.src||{}); delete sr[key]; upd({draft:d,err:er,src:sr}); },
                reset:()=>{ const cur=self.state.lp; const d=Object.assign({},cur.draft); delete d[key]; const sr=Object.assign({},cur.src||{}); delete sr[key]; upd({draft:d,src:sr}); },
                ret:()=>{ const cur=self.state.lp; const rr=Object.assign({},cur.rm||{},{[key]:true}); const d=Object.assign({},cur.draft); delete d[key]; const er=Object.assign({},cur.err||{}); delete er[key]; const sr=Object.assign({},cur.src||{}); delete sr[key]; upd({rm:rr,draft:d,err:er,src:sr}); },
                desf:()=>{ const cur=self.state.lp; const rr=Object.assign({},cur.rm||{}); delete rr[key]; const sr=Object.assign({},cur.src||{}); delete sr[key]; const d=Object.assign({},cur.draft); delete d[key]; upd({rm:rr,src:sr,draft:d}); } }; })
            .concat(adds.map((x,j)=>{ const key=A+'|+'+j; const n=g2num(x.dose);
              return {grupo:x.grupo, nome:prodNome(x.prod,c), padrao:'—', v:x.dose, un:x.un+'/ha', preco:rs(x.preco)+'/'+x.un, custo:(x.dose===''||isNaN(n))?'—':(rs(n*x.preco)+'/ha'), aj:false, ajT:'', ajSt:'', rmv:false, rmT:'', novo:true,
                err:ERR(key), hasErr:!!ERR(key), dis:ro, fid:'lp_'+A+'_n'+j, ist:doseSt(key,true,ro,false), podeRet:!ro, podeDesf:false, podeRest:false, hasSug:false, sugD:'', sugQ:'', sugU:'', sugPq:()=>{}, pqId:'', sugGo:()=>{},
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
  /* operação incluída pela análise (R18): gravada (aceite) ou a salvar (rascunho), no topo do painel; e a sugestão de incluir */
  const tipoInc=(s)=>/:ges$/.test(s.atv.id)?'gessagem':'calagem';
  const incG=acSt.filter(x=>x.tipo==='incluir'&&!(lp.inclRm||{})[x.k]); const incP=Object.values(lp.incl||{});
  v.lp_incl=incG.map(x=>{ const ng=ngAc(x); return {t:x.atv.nome+' · '+x.prod, d:soloDoseTxt(x.dose,x.un)+' · '+soloBr(x.dt)+' · '+soloQtdTxt(cenQtd(x.dose,area),x.un,false)+(ng?' · '+ng+': não se desfaz':''), chip:'incluída pela análise · '+x.laudo,
      podeDesf:!ro&&!ng, desf:()=>upd({inclRm:Object.assign({},self.state.lp.inclRm||{},{[x.k]:true})}), desfT:'Desfazer inclusão'}; })
    .concat(incP.map(s=>({t:s.atv.nome+' · '+s.prod, d:soloDoseTxt(s.sug,s.un)+' · '+soloBr(s.dt)+' · '+soloQtdTxt(cenQtd(s.sug,area),s.un,false), chip:'incluída pela análise · '+s.laudo.id+' (a salvar)',
      podeDesf:!ro, desf:()=>{ const x=Object.assign({},self.state.lp.incl||{}); delete x[s.k]; upd({incl:x}); }, desfT:'Desfazer'})));
  v.lp_hasIncl=v.lp_incl.length>0;
  v.lp_incSug=ro?[]:SG.sug.filter(s=>s.tipo==='incluir'&&!s.nega&&!(lp.incl||{})[s.k]).filter(s=>{ const g0=incG.find(x=>soloTipoAtv(x.incl)===soloTipoAtv(s.incl)); return !g0||prCmp(g0.dose,s.sug)!==0; })
    .map(s=>{ const g0=incG.find(x=>soloTipoAtv(x.incl)===soloTipoAtv(s.incl)); const fid='lp_inc_'+tipoInc(s);
      return {d:(g0?s.atv.nome+' '+soloDoseTxt(s.sug,s.un)+' (incluída '+soloDoseTxt(g0.dose,g0.un)+')':'incluir '+s.atv.nome+' · '+s.prod+' '+soloDoseTxt(s.sug,s.un)+' em '+soloBr(s.dt)),
        q:soloQtdTxt(g0?prSub(cenQtd(s.sug,area),cenQtd(g0.dose,area)):cenQtd(s.sug,area),s.un,true), u:g0?'Usar '+soloDoseTxt(s.sug,s.un):'Incluir '+tipoInc(s), pqId:'pq_'+fid,
        pq:()=>pqAbre(s,'pq_'+fid), go:()=>{ const x=Object.assign({},self.state.lp.incl||{},{[s.k]:s}); const r0=Object.assign({},self.state.lp.inclRm||{}); if(g0) r0[g0.k]=true; upd({incl:x,inclRm:r0}); }}; })
    /* R22 (revisão A3): o laudo vigente dispensa a correção incluída → "retirar"; preenche o rascunho (inclRm guarda a sugestão) e o Salvar grava */
    .concat(SG.sug.filter(s=>s.incl0&&!s.nega&&incG.some(x=>x.k===s.k)).map(s=>{ const fid='lp_ret_'+tipoInc(s);
      return {d:'retirar a '+s.atv.nome+' incluída ('+(s.motivo||'pela análise')+')', q:soloQtdTxt(s.dif,s.un,true), u:'Retirar pela análise', pqId:'pq_'+fid,
        pq:()=>pqAbre(s,'pq_'+fid), go:()=>upd({inclRm:Object.assign({},self.state.lp.inclRm||{},{[s.k]:s})})}; }));
  v.lp_hasIncSug=v.lp_incSug.length>0;
  const dirty=()=>{ const cur=self.state.lp; return JSON.stringify({d:cur.draft,rm:cur.rm||{},add:cur.add||{},incl:Object.keys(cur.incl||{}),inclRm:cur.inclRm||{}})!==JSON.stringify(Object.assign(JSON.parse(cur.orig),{incl:[]})); };
  v.lp_warn=!!lp.warn; v.lp_nerr=Object.keys(lp.err||{}).length>0; v.lp_cmdErr=lp.cmdErr||''; v.lp_hasCmdErr=!!lp.cmdErr;
  v.lp_close=()=>{ if(!ro && dirty()){ self.setState({lp:Object.assign({},self.state.lp,{warn:true})}); return; } self.setState({lp:null,pq:null}); };
  v.lp_discard=()=>self.setState({lp:null,pq:null}); v.lp_keep=()=>self.setState({lp:Object.assign({},self.state.lp,{warn:false})});
  v.lp_save=()=>lpSalvar(self,c,pl); }
/* Salvar do painel: sessão (ajuste manual) e cenário (aceites) com uma dose por chave (R14). Nada se copia do aceite para a sessão; mudar à mão a
   dose da análise desfaz o aceite ("substituído por ajuste manual", R15); Restaurar dose volta ao padrão e desfaz o aceite */
function lpSalvar(self,c,pl){ const cur=self.state.lp; const er={}; const out={}; const aceitar=[], desfazer=[]; const SRC=cur.src||{};
  const acSt=soloAcAtivos(soloSaf(self).ac,c.id,c.v.plano); 
  pl.atividades.forEach(a=>{ const A=String(a.id);
    a.prods.forEach((p,i)=>{ const key=A+'|'+i; const a0=acSt.find(x=>x.tipo!=='incluir'&&String(x.atv.id)===A&&x.prod===p.prod)||null; const sr=SRC[key];
      const rmv=!!(cur.rm||{})[key]; const dv=cur.draft[key]; const n=(dv===undefined||dv==='')?p.dose:g2num(dv);
      if(!rmv&&(isNaN(n)||n<0)){ er[key]='Use um número ≥ 0'; return; }
      const val=rmv?'-':n;
      if(sr){ const igual=(sr.dose==='-'&&val==='-')||(sr.dose!=='-'&&val!=='-'&&Math.abs(Number(sr.dose)-val)<1e-9);
        if(igual){ if(sr.s&&!(a0&&String(a0.dose)===String(sr.dose))) aceitar.push(Object.assign({},sr.s,{local:c.v.local})); return; } }   /* pela análise: fica no cenário, nunca na sessão */
      /* revisão A7: digitar de novo a dose do uso gravado (ou retirar o que a análise já retirou) não o desfaz nem vira ajuste da sessão */
      if(a0&&((a0.dose==='-'&&val==='-')||(a0.dose!=='-'&&val!=='-'&&Math.abs(Number(a0.dose)-val)<1e-9))) return;
      if(rmv){ out[key]='-'; if(a0) desfazer.push({k:a0.k,motivo:'substituído por ajuste manual'}); return; }
      if(Math.abs(n-p.dose)>1e-9){ out[key]=n; if(a0) desfazer.push({k:a0.k,motivo:'substituído por ajuste manual'}); return; }
      if(a0) desfazer.push({k:a0.k,motivo:'desfeito: dose do plano restaurada'}); });
    (((cur.add||{})[A])||[]).forEach((x,j)=>{ const key=A+'|+'+j; const n=g2num(x.dose); if(String(x.dose).trim()===''||isNaN(n)||n<=0){ er[key]='Informe a dose por hectare (maior que zero)'; return; }
      out[key]={prod:x.prod,grupo:x.grupo,un:x.un,preco:x.preco,dose:n}; }); });
  if(Object.keys(er).length){ self.setState({lp:Object.assign({},cur,{err:er})}); return; }
  Object.values(cur.incl||{}).forEach(s=>aceitar.push(Object.assign({},s,{local:c.v.local})));
  const tk=(k)=>(/\|solo:[^|]+:(cal|ges)\|/.exec(k)||[])[1]||'';
  Object.keys(cur.inclRm||{}).forEach(k=>{ const x=cur.inclRm[k]; if(x&&x.incl0){ aceitar.push(Object.assign({},x,{local:c.v.local})); return; }   /* retirar pela análise (R22) */
    if(!aceitar.some(s=>s.tipo==='incluir'&&tipoInc0(s)===tk(k))) desfazer.push({k,motivo:'desfeito'}); });   /* a nova inclusão do mesmo tipo já substitui a antiga no comando */
  let msgSolo='';
  if(aceitar.length||desfazer.length){ const r=cenMudar(null,cc=>soloAceitar(cc,{cid:c.id,aceitar,desfazer},cur.chave,g2perfil().k));
    if(r.erro){ self.setState({lp:Object.assign({},cur,{cmdErr:r.erro})}); return; } msgSolo=r.msg; }
  const adj=JSON.parse(JSON.stringify(adjOf(self))); if(Object.keys(out).length) adj[cur.cid]=out; else delete adj[cur.cid];
  const vals=Object.values(out); const nr=vals.filter(x=>x==='-').length, ni=vals.filter(x=>x&&typeof x==='object').length, nd=vals.length-nr-ni;
  const partes=[nd?nd+(nd>1?' doses alteradas':' dose alterada'):'', nr?nr+(nr>1?' insumos retirados':' insumo retirado'):'', ni?ni+(ni>1?' insumos incluídos':' insumo incluído'):''].filter(Boolean);
  const nac=soloAcAtivos(soloSaf(self).ac,c.id,c.v.plano).length;   /* revisão A7 (S4): sem mudança, diz o que vale de fato */
  const semMud=!partes.length&&!msgSolo?(nac?'Sem mudanças em '+c.v.local+': valem o plano padrão e '+nac+(nac>1?' usos':' uso')+' da análise. ':'Sem ajustes em '+c.v.local+': vale o plano padrão. '):'';
  self.setState({adj,lp:null,pq:null,cenrev:Date.now(),g2toast:(partes.length?partes.join(' · ')+' em '+c.v.local+'. ':'')+(msgSolo?msgSolo.replace(/\.$/,'')+' em '+c.v.local+'. ':'')+semMud+'Plano operacional, recursos e demanda recalculados; o plano padrão e os outros talhões não mudaram.'}); }
function tipoInc0(s){ return /:ges$/.test(String((s.atv||{}).id))?'ges':'cal'; }
/* ---- Sugestões pelas análises (safra, §3.4): lista lado a lado padrão × sugestão; nada vem marcado (D-16); usa só as escolhidas, uma chave por envio ---- */
function sgSugs(self,saf,manter){ const out=[]; cultRows(self,saf).forEach(c=>{ const R=soloSugsSaf(self,saf,c,false); R.sug.forEach(s=>{ if(!s.nega||(manter&&manter[s.k])) out.push({s,c,cu:R.cu}); }); }); return out; }   /* manter: linha negada no último envio continua com o motivo */
function sgN(self,saf){ if(!saf) return 0; const k=(self.state.cenrev||0)+'|'+saf+'|'+JSON.stringify(adjOf(self))+'|'+cultRows(self,saf).map(c=>c.id+c.v.meta+c.v.plano+c.v.area).join(',');
  if(self.__sgn&&self.__sgn.k===k) return self.__sgn.n; const n=sgSugs(self,saf).length; self.__sgn={k,n}; return n; }
function sgAbrir(self){ const saf=self.state.saf; if(!saf) return; g2set(self,'g_sug',{sel:{},rows:null,q:'',f:{},qv:''}); self.setState({sg:{saf,chave:'LOTE-'+saf+'-'+Date.now(),neg:{}},pq:null}); }
function sgRows(self){ const sg=self.state.sg; if(!sg) return []; const L=sgSugs(self,sg.saf,sg.neg); self.__sgL=L;
  return L.map(x=>{ const s=x.s, c=x.c; const r={id:s.k,v:{},s:{},p:{}}; const tp={dose:'Outra dose',retirar:'Retirar',incluir:'Incluir'}[s.tipo];
    r.p.tal=[{k:'b',t:c.v.local},{k:'mut',t:nf(c.v.area)+' ha'}]; r.s.tal=c.v.local; r.p.item=[{k:'txt',t:s.atv.nome},{k:'br'},{k:'mut',t:s.prod}]; r.s.item=s.atv.nome+' · '+s.prod;
    const efV=s.ef!==null&&s.ef!=='-'&&s.efOrig!=='padrão';   /* a dose que vale hoje: a do uso (inclusão de outro laudo, revisão A1/A3) ou a do padrão */
    r.p.pad=[{k:'txt',t:efV?soloDoseTxt(s.ef,s.un):(s.padrao===null?'—':soloDoseTxt(s.padrao,s.un))}].concat(s.efOrig&&s.efOrig!=='padrão'?[{k:'br'},{k:'mut',t:s.efOrig==='análise'?'pela análise':'ajustado pelo usuário'}]:[]); r.s.pad=r.p.pad[0].t;
    r.p.sug=[{k:'b',t:s.tipo==='retirar'?(s.incl0?'retirar a inclusão':'retirar'):(s.tipo==='incluir'?'incluir '+soloDoseTxt(s.sug,s.un):soloDoseTxt(s.sug,s.un)+(s.desf?' (padrão)':''))}]; r.s.sug=r.p.sug[0].t;
    r.v.dif=s.dif; r.p.dif=[{k:'txt',t:soloQtdTxt(s.dif,s.un,true)}]; r.s.dif=r.p.dif[0].t; r.p.tipo=[{k:'txt',t:tp}]; r.s.tipo=tp;
    r.p.lau=[{k:'act',t:s.laudo.id+' · Por quê',fn:'sgpq:'+s.k,lk:true,al:'Por quê: '+s.atv.nome+' · '+s.prod+' no '+c.v.local}]; r.s.lau=s.laudo.id;
    const ng=(sg.neg||{})[s.k]; r.p.res=ng?[{k:'chip',t:'não gravada: '+ng,c:'red'}]:[{k:'mut',t:'—'}]; r.s.res=ng?'não gravada':''; return r; }); }
function sgVals(self,v){ const sg=self.state.sg; v.sg_open=!!sg; const saf=self.state.saf; const n=(saf&&(self.state.step||1)===2)?sgN(self,saf):0; v.sg_has=n>0; v.sg_lnk='Sugestões pelas análises · '+n; v.sg_abrir=()=>sgAbrir(self);
  v.sgpq=(k)=>{ self.__pqFoco='sg_x'; self.setState({pq:{k,from:'sg'}}); };
  if(!sg) return; const S=safList(self)[sg.saf]||{}; const sel=(g2st(self,'g_sug').sel)||{}; const L=self.__sgL||[]; const ks=L.filter(x=>sel[x.s.k]&&!(sg.neg||{})[x.s.k]&&!x.s.nega).map(x=>x.s.k);
  v.sg_titulo='Sugestões pelas análises · '+(S.nome||sg.saf); v.sg_sub='Padrão ao lado da sugestão, por talhão. Marque as que quer usar; as outras seguem como estão.';
  v.sg_pe='Os demais talhões seguem a dose do plano.'; v.sg_closeT='Fechar'; v.sg_sec=[]; v.sg_hasPA=false; v.sg_ph='#';
  v.sg_hasPB=true; v.sg_pt='Usar '+ks.length+(ks.length===1?' sugestão':' sugestões'); v.sg_pdis=!ks.length; v.sg_pst=ks.length?'':'opacity:.5;cursor:not-allowed;';
  v.sg_err=sg.err||''; v.sg_hasErr=!!sg.err;
  v.sg_close=()=>self.setState({sg:null,pq:null}); v.sg_key=(e)=>{ if(e&&e.key==='Escape'&&!self.state.pq){ e.preventDefault(); v.sg_close(); } };
  v.sg_pgo=()=>{ if(!ks.length){ self.setState({sg:Object.assign({},self.state.sg,{err:'Marque ao menos uma sugestão.'})}); return; }
    const itens=L.filter(x=>ks.indexOf(x.s.k)>=0).map(x=>Object.assign({},x.s,{local:x.c.v.local}));
    const r=cenMudar(null,cc=>soloAceitarLote(cc,itens,self.state.sg.chave,g2perfil().k));
    if(r.erro){ self.setState({sg:Object.assign({},self.state.sg,{err:r.erro})}); return; }
    /* R14: gravar o aceite apaga o ajuste manual da sessão naquela chave */
    const neg={}; (r.neg||[]).forEach(x=>{ neg[x.k]=x.motivo; }); const adj=JSON.parse(JSON.stringify(adjOf(self)));
    itens.filter(it=>!neg[it.k]&&it.i>=0&&it.tipo!=='incluir'&&!it.incl0&&!it.desf).forEach(it=>{ const k0=it.atv.id+'|'+it.i; if(adj[it.cid]&&adj[it.cid][k0]!==undefined){ delete adj[it.cid][k0]; if(!Object.keys(adj[it.cid]).length) delete adj[it.cid]; } });
    g2set(self,'g_sug',{sel:{},rows:null});
    if(Object.keys(neg).length) self.setState({adj,cenrev:Date.now(),g2toast:r.msg,sg:Object.assign({},self.state.sg,{neg,err:'',chave:'LOTE-'+sg.saf+'-'+Date.now()})});
    else self.setState({adj,cenrev:Date.now(),g2toast:r.msg,sg:null}); }; }
/* Por quê (no painel de insumos ou no lote): a primária pelo contexto; negada pela R11, sem primária */
function pqSafVals(self,v){ const pq=self.state.pq; let s=null, cu=null, prim=null;
  if(pq&&pq.from==='lp'&&self.state.lp){ const c=cultRows(self,self.state.saf).find(r=>r.id===self.state.lp.cid); if(c){ const R=soloSugsSaf(self,self.state.saf,c,true); s=R.sug.find(x=>x.k===pq.k)||null; cu=R.cu; }
    if(s&&!s.nega) prim={t:s.tipo==='retirar'?'Retirar pela análise':(s.tipo==='incluir'?'Incluir '+(/:ges$/.test(s.atv.id)?'gessagem':'calagem'):'Usar '+soloDoseTxt(s.sug,s.un)),go:()=>{ lpUsarPq(self,s); }}; }
  if(pq&&pq.from==='sg'){ const x=(self.__sgL||[]).find(q=>q.s.k===pq.k); if(x){ s=x.s; cu=x.cu; prim={t:'Marcar esta sugestão',go:()=>{ const sel=Object.assign({},(g2st(self,'g_sug').sel)||{}); sel[s.k]=true; g2set(self,'g_sug',{sel}); self.setState({pq:null}); }}; } }
  soloPqVals(self,v,s,{cu,prim,ver:s?'AG-02.dc.html#'+s.laudo.id:'',fechar:()=>self.setState({pq:null})}); }
function lpUsarPq(self,s){ const lp=self.state.lp; if(!lp) return; if(s.tipo==='incluir'){ const x=Object.assign({},lp.incl||{},{[s.k]:s}); self.setState({lp:Object.assign({},lp,{incl:x,warn:false}),pq:null}); return; }
  if(s.incl0){ self.setState({lp:Object.assign({},lp,{inclRm:Object.assign({},lp.inclRm||{},{[s.k]:s}),warn:false}),pq:null}); return; }   /* R22: retirar a inclusão */
  const c=cultRows(self,self.state.saf).find(r=>r.id===lp.cid); const pl=c&&planById(c.v.plano); const a=pl&&pl.atividades.find(q=>String(q.id)===String(s.atv.id)); const i=a?a.prods.findIndex(q=>q.prod===s.prod):-1; if(i<0){ self.setState({pq:null}); return; }
  const key=String(a.id)+'|'+i; const d=Object.assign({},lp.draft), rr=Object.assign({},lp.rm||{}), sr=Object.assign({},lp.src||{});
  if(s.tipo==='retirar'){ rr[key]=true; delete d[key]; } else { d[key]=String(s.sug).replace('.',','); delete rr[key]; } sr[key]={laudo:s.laudo.id,dose:s.tipo==='retirar'?'-':s.sug,s};
  self.setState({lp:Object.assign({},lp,{draft:d,rm:rr,src:sr,warn:false}),pq:null}); }
function enviar(self){ const saf=self.state.saf; const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); if(safObj&&safObj.ro){ self.setState({g2toast:'Safra encerrada: não gera solicitações.'}); return; }
  const dm=demanda(self,saf); const sols=Object.assign({},solMap(self)); const sol=sols[saf];
  const itens=Object.values(dm).filter(d=>d.liq>0.001);
  if(!itens.length){ self.setState({g2toast:'Nada a cotar: o estoque e os recebimentos cobrem a demanda.'}); return; }
  // registro único da solicitação: o que a Compra de insumos mostra (mesmos itens, quantidades, valores e memória CAL-01)
  const det=Object.values(dm).map(d=>({nome:d.nome,grupo:d.grupo,un:d.un,preco:d.preco,bruta:d.bruta,est:d.est,res:d.res,rec:d.rec,liq:d.liq,valor:d.valor,falta:d.falta,uso:d.uso,quar:d.quar,evs:d.evs}));
  const EM='23/09/2026 11:05';   // horário do cenário de demonstração (a SOL-2026-07 inicial é de 10:40)
  const base={safra:saf,nome:safObj.v.nome,faz:safObj.v.faz||'Santa Rita',estado:'Enviada · a cotar',por:'Ana (gestora)',
    origem:{t:'Planejar safra · '+safObj.v.nome+' · demanda de insumos',h:'SAF.dc.html#saf='+encodeURIComponent(saf)+'&passo=demanda'},det};
  const grava=(rec)=>{ const ok=solGravar(rec); return ok?'':' Atenção: este navegador não guarda dados; a Compra de insumos não verá a solicitação.'; };
  if(!sol){ const ids={S27SF:'SOL-2027-02',S2627:'SOL-2026-07',LG2627:'SOL-2026-09'}; const usados=Object.values(sols).map(x=>x.id); let id=ids[saf];
    for(let k=10;!id||usados.indexOf(id)>=0;k++) id='SOL-2026-'+k;
    const it={}; itens.forEach(d=>{ it[d.nome]=d.liq; }); const tot=itens.reduce((a,d)=>a+d.valor,0);
    sols[saf]=Object.assign({},base,{id,at:'23/09/2026',em:EM,itens:it,comp:0,total:tot});
    const av=grava(sols[saf]);
    self.setState({sol:sols,g2toast:'Solicitação '+id+' enviada a Compras: '+itens.length+' insumos, '+rs(tot)+'. Origem: '+safObj.v.nome+' · Planejar safra, demanda de insumos.'+av}); return; }
  const novos=itens.filter(d=>d.liq>(sol.itens[d.nome]||0)+0.01);
  if(!novos.length){ self.setState({g2toast:'Nada novo para cotar: tudo já está na '+sol.id+'. Nenhuma solicitação duplicada foi criada.'}); return; }
  const it=Object.assign({},sol.itens); novos.forEach(d=>{ it[d.nome]=d.liq; }); const comp=(sol.comp||0)+1;
  const val=novos.reduce((a,d)=>a+(d.liq-(sol.itens[d.nome]||0))*d.preco,0);
  sols[saf]=Object.assign({},base,sol,{estado:'Enviada · a cotar',itens:it,comp,det,total:Object.keys(it).reduce((a,n)=>a+it[n]*((dm[n]||{}).preco||0),0),em:sol.em||(saf==='S2627'?'23/09/2026 10:40':EM)});
  const av=grava(sols[saf]);
  self.setState({sol:sols,g2toast:'Complemento '+sol.id+'-C'+comp+' enviado com só a diferença: '+novos.length+' insumos, '+rs(val)+'. A solicitação original não foi duplicada.'+av}); }
