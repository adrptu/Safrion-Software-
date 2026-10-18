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
// capSaf(oc, outras, recursos, meses, dias): oc = ocorrências desta safra, com i.cls (classeOc pelo período dela); outras = [{id, nome,
// ini, fim, oc}] das safras abertas da mesma fazenda. Ocorrência com etiqueta do calendário (antes do início, depois do fim, fora) conta
// no custo e não na capacidade (§3.4, FORA-DE-ESCOPO "Regra A"; revisão SAF, S3.1). SAF-C02: a etiqueta de cada ocorrência sai do
// período da safra de ORIGEM, a desta e a de cada outra, qualquer que seja a safra aberta: a demanda do mês não depende da navegação.
// g.fora = carga que ficou fora da conta num mês do calendário ({sid: null = desta safra, cls, mi, h, n = ocorrência}), para o veredito.
// Contrato (verificação SAF-C02): cada ocorrência desta safra traz cls e cada outra safra traz ini e fim (null = sem período); sem eles a
// conta voltaria a depender da safra aberta, então o erro é explícito. A célula soma as parcelas de cada safra em ordem fixa (crescente):
// com 3 ou mais safras, a ordem da soma em ponto flutuante não muda o texto exibido conforme a safra aberta.
function capContrato(oc,outras){ (oc||[]).forEach(i=>{ if(!('cls' in i)) throw new Error('capSaf: ocorrência desta safra sem a etiqueta cls do período dela'); });
  (outras||[]).forEach(s=>{ if(!('ini' in s)||!('fim' in s)) throw new Error('capSaf: a safra '+s.id+' chegou sem o período (ini e fim)'); }); }
function capSaf(oc,outras,recursos,meses,dias){ capContrato(oc,outras); const M=meses.length; const Z=()=>new Array(M).fill(0); const G={}; let n=0;
  recursos.forEach(r=>{ G[r.id]=Object.assign(capRec(r,meses,dias),{dThis:Z(),dThisAt:Z(),dOth:Z(),oth:{},sim:Z(),semH:Z(),pendSR:Z(),fora:[]}); });
  const add=(i,own,s)=>{ const sid=own?null:s.id, ix=n++; if(!(i.mi>=0)) return; const cl=own?i.cls:classeOc(i.dt,i.mi,s.ini,s.fim);
    if(cl&&cl!=='cal'){ cargaItens(i).forEach(c=>{ const g=G[c.k]; if(g&&c.h>0) g.fora.push({sid,cls:cl,mi:i.mi,h:c.h,n:ix}); }); return; } const cs=cargaItens(i);
    cs.forEach(c=>{ const g=G[c.k]; if(!g) return; if(own){ g.dThis[i.mi]+=c.h; g.dThisAt[i.mi]+=c.ha; if(c.semRec) g.pendSR[i.mi]++; } else { g.dOth[i.mi]+=c.h; (g.oth[sid]||(g.oth[sid]=Z()))[i.mi]+=c.h; }
      g.sim[i.mi]=Math.max(g.sim[i.mi],c.sim); });
    if(i.rp&&i.rp.falta&&i.rp.falta.semHoras>1e-9){ /* "≥" com a área sem horas de qualquer safra elegível: a mesma marca nas duas vistas */ const ks={}; cs.forEach(c=>{ ks[c.k]=1; }); Object.keys(ks).forEach(k=>{ if(G[k]) G[k].semH[i.mi]+=i.rp.falta.semHoras; }); } };
  (oc||[]).forEach(i=>add(i,true,null)); (outras||[]).forEach(s=>(s.oc||[]).forEach(i=>add(i,false,s)));
  Object.values(G).forEach(g=>{ g.cells=meses.map((m,mi)=>{ const d=[g.dThis[mi]].concat(Object.keys(g.oth).map(o=>g.oth[o][mi])).sort((a,b)=>a-b).reduce((a,b)=>a+b,0), cap=g.cap[mi], pu=g.porUn[mi];
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
// carga de outras safras fora da conta (SAF-C02) nas células com demanda desta safra: por safra e motivo, ocorrências e horas por recurso
function capForaOutras(G){ const by={}, ord=[]; Object.values(G).forEach(g=>(g.fora||[]).forEach(f=>{ if(f.sid===null||!g.cells[f.mi].own) return;
    const k=f.sid+'|'+f.cls; let x=by[k]; if(!x){ x=by[k]={sid:f.sid,cls:f.cls,oc:{},h:{},rec:[]}; ord.push(x); } x.oc[f.n]=1;
    if(!(g.nome in x.h)){ x.h[g.nome]=0; x.rec.push(g.nome); } x.h[g.nome]+=f.h; }));
  return ord.map(x=>({sid:x.sid,cls:x.cls,n:Object.keys(x.oc).length,h:x.rec.map(r=>[r,x.h[r]])})); }
// veredito (§3.1): o único lugar de "cabe", do que falta e do que ficou fora da conta. x = {semPlano:[{local,area}], aPlano, cls (contagens antes/
// fora/depois/cal), ini e fim (dd/mm/aaaa), outras {id: nome}, pend (ocorrências sem alocação), semHoras (ha), incompleto (texto do R3)}
function capVeredito(G,oc,x){ const nfa0=(n)=>Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:2});
  const fora=[]; if(x.semPlano.length) fora.push(capNomes(x.semPlano.map(c=>c.local))+' ('+nfa0(x.semPlano.reduce((a,c)=>a+(Number(c.area)||0),0))+' ha), sem plano');
  if(x.cls.antes) fora.push(x.cls.antes+(x.cls.antes>1?' ocorrências':' ocorrência')+' antes do início da safra ('+x.ini+')');
  if(x.cls.fora) fora.push(x.cls.fora+(x.cls.fora>1?' ocorrências':' ocorrência')+' fora do calendário');
  if(x.cls.depois) fora.push(x.cls.depois+(x.cls.depois>1?' ocorrências':' ocorrência')+' depois do fim da safra');
  capForaOutras(G).forEach(f=>fora.push(f.n+(f.n>1?' ocorrências da ':' ocorrência da ')+(x.outras[f.sid]||f.sid)+(f.cls==='antes'?' antes do início':' depois do fim')+' dela ('+capNomes(f.h.map(r=>r[0]+' '+capH(r[1])+' h'))+')'));
  const foraTxt=fora.length?' Fora da conta: '+fora.join('; ')+'.':'';
  const jn=capJanelas(oc); const prazo=jn.J?' Prazo por talhão não verificado: '+jn.J+' de '+jn.M+(jn.M>1?' atividades':' atividade')+' sem janela.':'';
  if(!x.aPlano) return {R:'R0',cor:'',txt:''};
  // R1: o motivo sai das etiquetas (verificação SAF-C02): todas fora do calendário, ou nenhuma no período da safra (antes, depois e fora contadas)
  if(!x.cls.cal) return {R:'R1',cor:'gray',txt:(oc.length&&x.cls.fora===oc.length)?'Capacidade não calculada: '+(oc.length>1?'as '+oc.length+' ocorrências desta safra ficam':'a ocorrência desta safra fica')+' fora do calendário do protótipo ('+x.periodoCal+').'
    :'Capacidade não calculada: nenhuma ocorrência desta safra cai no período dela'+(x.fim?' ('+x.ini+' a '+x.fim+')':'')+(x.cls.fora?' dentro do calendário do protótipo ('+x.periodoCal+')':'')+'.'+foraTxt};
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
const SIT_COR={'Sobreposição':'red','A conferir':'yellow','Livre':'green','Planejado':'blue','Perene':'gray','Ocupado':'gray','Sem plantio':'gray'};
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
// SAF-FAZ-3 (proprietário, 15/10/2026: "selecionar fazendas e talhões de mais de 1 fazenda por vez… bem produtiva, rápida, prática e fácil";
// "pode ser que algum talhão o produtor não deseje plantar nada"): a safra de várias fazendas mostra os talhões de todas juntos, um grupo por
// fazenda; cada fazenda continua com a própria sub-safra (SAF-FAZ-2: cultivos, ocupação, capacidade e demanda por fazenda). A tabela é a da
// sub-safra aberta; a linha de outra fazenda leva a ação à sub-safra dela (sgNaFazenda), sem mudar o que a pessoa vê
function talBase(self,S){ const ctx=ocCtxSaf(); const todos=ocTodos(self); const occ=ocOcupacoes(ctx,S,todos); const byO={}, byCiclo={}; occ.forEach(o=>{ byO[o.id]=o; byCiclo[o.ciclo]=o; });
  return {ctx,S,todos,occ,byO,byCiclo,adj:adjOf(self)}; }
function syncTalhoes(self,saf,v){ const k=sk(saf); const sp=GR('g_cult_'+k); const S=safList(self); if(!sp||!S[saf]){ self.__ocG=null; return null; }
  // 17/10 (proprietário: "quando so tem 1 fazenda nao agrupa por fazenda, só quando tem 2 ou mais. corrija."): a tabela agrupa por fazenda
  // sempre, também com uma fazenda só; a faixa nasce recolhida, como todo drill down (TAB-12), e mostra a área e quantos talhões estão
  // planejados; o filtro rápido por fazenda continua só com duas ou mais (ffzVals)
  const subs0=sgSubs(self,saf); const subs=subs0.length?subs0:[{id:saf,faz:safFaz(self,saf)}]; const B=talBase(self,S);
  const ffz=subs.some(x=>x.faz===self.state.ffz)?self.state.ffz:''; const grupos=[], G={}; let info=null;
  const band={nesta:0,livre:0,conf:0,perene:0,ocup:0,semp:0}; let linhas=[], tot=0;
  subs.forEach(su=>{ const m=talMontar(self,su.id,v,B); G[su.id]=m.info; if(su.id===saf) info=m.info;
    if(m.info.band) Object.keys(band).forEach(q=>{ band[q]=ocR2(band[q]+(Number(m.info.band[q])||0)); }); linhas=linhas.concat(m.info.linhas||[]); tot+=talTot(su.faz);
    if(su.id!==saf) talDeOutra(self,su.id,m.rows,v);
    if(ffz&&su.faz!==ffz) return;   // filtro rápido por fazenda (ao lado da busca)
    const L=m.info.linhas||[]; const nPl=L.filter(l=>l.own.length).length, nSp=L.filter(l=>l.semp).length, nLv=L.filter(l=>l.planejar).length;
    const area=r2(cultsDe(self,su.id).reduce((a,c)=>a+(Number(c.v.area)||0),0));
    const res=nPl+' de '+L.length+(L.length===1?' talhão planejado':' talhões planejados')+(nSp?' · '+nSp+' sem plantio':'');
    grupos.push({id:'fzg_'+su.id,fgrp:true,nosel:true,ro:true,v:{local:su.faz,area},s:{local:su.faz+' · '+nfa(area)+' ha · '+res},
      p:{local:[{k:'b',t:su.faz},{k:'mut',t:nfa(area)+' ha · '+res}].concat(nLv&&!m.info.safra.ro?[{k:'act',t:'Planejar talhões livres ›',fn:'pltfaz:'+su.faz,lk:true,alvo:true}]:[])
        .concat(!m.info.safra.ro&&L.length?[{k:'act',t:'Editar talhões ›',fn:'slfaz:'+su.id,lk:true,alvo:true,al:'Editar talhões da '+su.faz}]:[])
        .concat(!m.info.safra.ro&&L.length?[{k:'act',t:'Planejar no mapa ›',fn:'slmapa:'+su.id,lk:true,alvo:true,al:'Planejar a safra no mapa da '+su.faz}]:[])   // SAF-MAPA (18/10)
        .concat(!m.info.safra.ro&&L.length&&g2estreito()?[{k:'act',t:'Editar talhões',fn:'slfaz:'+su.id,al:'Editar talhões da '+su.faz}]:[]),area:[{k:'b',t:nfa(area)}]},kids:m.rows}); });   // EDL-01: todos os talhões da fazenda numa grade (safra_lote.js); no estreito, também no ⋯ da faixa
  G2DISP[sp.id]=grupos; self.__ocG=G;
  if(info){ info.bandG=band; info.linhasG=linhas; info.totG=tot; } return info; }
// linha de outra fazenda na tabela da sub-safra aberta: abrir e Excluir levam antes à sub-safra dela (os atalhos da linha já vão pelo talhão)
function talDeOutra(self,sub,rows,v){ const gid='g_cult_'+sk(sub);
  v['xdel_'+sub]=(rid)=>sgNaFazenda(self,sub,()=>g2set(self,gid,{cf:rid}));
  const w=(l)=>(l||[]).forEach(r=>{ if(!r.fora&&!r.livre&&!r.nosel){ r.xdel='xdel_'+sub; if(!r.dr){ r.dr='xr_'+r.id; v[r.dr]=()=>sgNaFazenda(self,sub,()=>g2open(self,GR(gid),r.id,null)); } } w(r.kids); }); w(rows); }
// tabela de uma sub-safra (o que era o syncTalhoes de uma fazenda): linhas de exibição sobre cópia, sem gravar
function talMontar(self,saf,v,B){ const S=B.S; const safra=S[saf]; const ctx=B.ctx, todos=B.todos, occ=B.occ, byO=B.byO, byCiclo=B.byCiclo, adj=B.adj;
  const sp=GR('g_cult_'+sk(saf)); const info={ctx,S,todos,occ,byO,safra,linhas:[],band:null,own:{}}; const sem=sempDe(self,saf);
  const ocDe=(r)=>byCiclo[r.v.ciclo||r.id]||byO[r.id]||null;
  const ownParts=(r,o,kid,L)=>{ leafParts(r,adj,kid);
    r.p.sit=[{k:'mut',t:''}]; r.s.sit=''; r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre=''; ocDcol(r,'desde',undefined); r.p.desde=[{k:'mut',t:'—'}]; r.s.desde=''; r.v.desde='';
    r.p.saf=[{k:'mut',t:'—'}]; r.s.saf=''; r.v.saf_='';
    if(o){ ocDcol(r,'ate',o.classe==='semdata'?null:o.fim); r.v.fimpor=OC_ROT[o.classe]; r.p.fimpor=[{k:'txt',t:r.v.fimpor}]; r.s.fimpor=r.v.fimpor;
      const pe=L&&(L.pend[o.id]||[]); const tv=L&&L.trav.some(x=>x[1]===o.id||x[2]===o.id);
      if(tv){ r.p.sit=[{k:'chip',t:'Sobreposição',c:'red',dica:ocMotivo(L,info)}]; r.s.sit='Sobreposição'; }
      else if(pe&&pe.length){ const d=pe.map(p=>ocPendCurta(ctx,o,p,byO)).join(' · '); r.p.sit=[{k:'chip',t:'A conferir',c:'yellow',dica:d}]; r.s.sit='A conferir'; }
      if(o.avisos.length){ const a=o.avisos[0]; r.p.plano=(r.p.plano||[]).concat([{k:'ico',c:'yellow',t:'O plano '+a[1]+' tem datas fixas fora desta safra (ex.: '+ocBr(a[2])+'). Revise o plano ou troque o gatilho para DAP/DAPC.'}]); } }   // SAF-TAB: ícone com a dica
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
    info.ro=true; return {info,rows}; }
  const [linhas,band]=ocTabela(ctx,safra,occ,talOrd(safra.faz),S); info.linhas=linhas; info.band=band;
  const own=cultsDe(self,saf).map(r=>g2clone([r])[0]); const rows=[];
  linhas.forEach(L=>{ const t=L.t; const mine=own.filter(r=>(r.v.talhao||ocTalhaoDe(r.v.local,r.v.tipo))===t); L._saf=saf;
    // sem plantio (pedido 2): talhão livre, sem cultivo desta safra, que a pessoa decidiu não plantar. Cinza, sem alerta: não é pendência,
    // não trava a etapa, não entra em área plantada, demanda, operações nem custo (nenhum cultivo existe); a faixa conta à parte
    if(!mine.length&&sem[t]&&L.planejar){ band.livre=ocR2(band.livre-L.livre); band.conf=ocR2(band.conf-L.conf); band.semp=ocR2((band.semp||0)+L.livre+L.conf);
      Object.assign(L,{sit:'Sem plantio',semp:true,planejar:false}); }
    const dica=L.semp?'Fora do plantio nesta safra: não entra em área plantada, demanda, operações nem custo. Para desfazer: ⋯ › Voltar a planejar.':ocMotivo(L,info);
    const curto=SIT_CURTO[L.sit]&&estreito360(); const sitP=[{k:'chip',t:curto?SIT_CURTO[L.sit]:L.sit,c:SIT_COR[L.sit]||'gray',dica:curto?(L.sit+(dica?': '+dica:'')):dica}];
    const acts=[]; let dr=null;
    if(L.semp) acts.push({k:'chip',t:'Sem plantio',c:'gray',dica:dica},{k:'act',t:'Voltar a planejar',fn:'replanejar:'+t});   // o estado à vista na célula do talhão (a Situação fica em "Colunas")
    else if(L.planejar){ acts.push({k:'act',t:'Planejar ›',fn:'planejar:'+t,lk:true}); dr='plan_'+t; if(!mine.length) acts.push({k:'act',t:'Não plantar nesta safra',fn:'semplantio:'+t}); }
    else if(L.vinc.length){ acts.push({k:'act',t:'Vincular ciclo ›',fn:'vincular:'+t+'|'+L.vinc[0],lk:true}); dr='vinc_'+t; }
    else if(mine.length&&!mine.some(r=>r.v.ciclo)){ acts.push({k:'act',t:'Dividir',fn:'divide:'+t,lk:true,sec:true}); dr='div_'+t; }   // ciclo vinculado não se divide (R-24)
    v['plan_'+t]=()=>sgNaFazenda(self,saf,()=>abrirPlanejar(self,t)); if(L.vinc.length) v['vinc_'+t]=()=>sgNaFazenda(self,saf,()=>abrirVincular(self,t,L.vinc[0]));
    const tal=(r)=>{ r.tal=t; r.p.sit=sitP; r.s.sit=L.sit; r.v.sit=L.sit;
      if(L.area_livre>0.005&&!L.semp){ r.v.livre=L.area_livre; r.p.livre=[{k:'txt',t:nfa(L.area_livre)}]; r.s.livre=nfa(L.area_livre);
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
      if(mine.length===1&&mine[0].v.tipo!=='Parcela'){ const m=mine[0]; g.v.tipo='Talhão inteiro'; g.p.tipo=[{k:'txt',t:'Talhão inteiro'}]; g.s.tipo='Talhão inteiro'; g.v.meta=m.v.meta; g.p.meta=m.p.meta; g.s.meta=m.s.meta; g.ordk=Object.assign({},g.ordk||{},{meta:(m.ordk||{}).meta}); } } else { ['cult','var','plano','ver','dt_plantio','meta','aj'].forEach(f=>{ g.p[f]=[{k:'mut',t:''}]; g.s[f]=''; }); g.v.area=''; g.p.area=[{k:'mut',t:'—'}]; g.p.tipo=[{k:'mut',t:'—'}]; g.s.tipo=''; }
    g.p.local=[{k:'b',t}].concat(acts); g.s.local=t; ['ate','fimpor','saf'].forEach(f=>{ g.p[f]=[{k:'mut',t:''}]; g.s[f]=''; g.v[f]=''; });
    tal(g); rows.push(g); });   // TAB-12 (17/10/2026): o talhão com parcelas nasce recolhido; a linha dele já diz a situação (A conferir, Sobreposição)
  return {info,rows}; }
// fazenda e talhões da safra para os textos do painel
function talhaoArea(t){ return Number((D2.talhoes||{})[t])||0; }
// ---- painel "Planejar T1" e "Vincular ciclo C1" (§2, R-17, R-19, R-24) ----
function ocLinha(self,t){ const info=self.__oc; const L=info&&info.linhas?info.linhas.find(x=>x.t===t)||null:null; if(L||!self.__ocG) return L;
  for(const k in self.__ocG){ const x=(self.__ocG[k].linhas||[]).find(y=>y.t===t); if(x) return x; } return null; }   // SAF-FAZ-3: talhão de outra fazenda da mesma safra
function maisUsado(cs,f){ const n={}; cs.forEach(c=>{ const x=c.v[f]; if(x) n[x]=(n[x]||0)+1; }); return Object.keys(n).sort((a,b)=>n[b]-n[a])[0]||''; }
// nomes que uma parcela nova não pode repetir (R-19): os desta safra e as faixas do talhão ainda ocupadas no início dela, inclusive as de
// ocupações futuras (SAF-C01: o café plantado numa safra de 2020 não recebe a parcela da soja de 2027, que a T-faixa recusaria)
function faixasEmUso(self,saf,t,rid){ const S=safList(self); const so=S[saf]; const usados=cultsDe(self,saf).filter(c=>c.id!==rid).map(c=>c.v.local); if(!so) return usados;
  const ctx=ocCtxSaf(); const a=ocDia(so.ini);
  return usados.concat(ocOcupacoes(ctx,S,ocTodos(self).filter(c=>c.faz===so.faz&&c.talhao===t&&c.saf!==saf)).filter(o=>ocLib(ctx,o,'pior')>a).map(o=>o.faixa)); }
// parcela sugerida (R-19): a faixa de fora que libera exatamente a Área livre no dia de "Livre a partir de"; senão a próxima letra livre
function sugerirParcela(self,saf,L,area,rid){ const t=L.t, T=talhaoArea(t); if(area>=T-0.005) return t; const ctx=ocCtxSaf();
  const usados=cultsDe(self,saf).filter(c=>c.id!==rid).map(c=>c.v.local);
  const f=L.fora.find(o=>o.faixa!==t&&usados.indexOf(o.faixa)<0&&Math.abs(o.area-area)<=0.005&&(ocLib(ctx,o,'pior')===L.desde||ocLib(ctx,o,'est')===L.desde));
  return f?f.faixa:nextNome(t,faixasEmUso(self,saf,t,rid)); }
// nome final da parcela (R-19): o MESMO na trava, no plantio mínimo, na prévia e no que se grava (revisão SAF, S2.2). Área cheia = talhão
// inteiro; nome digitado vale (repetido nesta safra o cultCheck recusa); vazio ou o nome do talhão = a parcela sugerida
function parcelaFinal(self,saf,t,area,local,rid){ const T=talhaoArea(t); if(!(area<T-0.005)) return t; const nm=String(local||'').trim();
  if(nm&&nm!==t) return nm; const L=ocLinha(self,t); if(L) return sugerirParcela(self,saf,L,area,rid);
  return nextNome(t,faixasEmUso(self,saf,t,rid)); }
function ocNovoRec(self,saf,d,id){ const t=d.talhao; const T=talhaoArea(t); const a=g2num(d.area); const area=isNaN(a)?0:a; const inteiro=area>=T-0.005;
  return {id:id||'__novo',saf,faz:safFaz(self,saf),faixa:parcelaFinal(self,saf,t,area,d.local,id||'__novo'),tipo:inteiro?'Talhão inteiro':'Parcela',talhao:t,area,cult:d.cult,var:d.var||'',
    plantio:d.plantio||'',plano:d.plano||null,colheita:(!d.plano&&d.colheita)?d.colheita:null,colheita_real:d.colheita_real||null,ciclo:d.ciclo||null,origem:''}; }
// PlantioMin do rascunho (cache por entrada: a busca anda dia a dia contra todas as ocupações do talhão)
function pminDraft(self,saf,d,desde){ const rec=ocNovoRec(self,saf,d,d._rid||'__novo'); const T=talhaoArea(d.talhao); const todos=ocTodos(self).filter(c=>c.id!==rec.id);
  const key=JSON.stringify([rec.cult,rec.var,rec.plano,rec.area,rec.faixa,rec.tipo,desde,self.state.g2&&self.state.g2['g_cult_'+sk(saf)]?Object.keys(self.state.g2).length:0,todos.length]);
  self._pm=self._pm||{}; if(key in self._pm) return self._pm[key];
  const S=safList(self); const r=ocPlantioMin(ocCtxSaf(),S,todos,saf,rec,desde,T,null); self._pm[key]=r; return r; }
// sem janela: se a trava no plantio digitado (ou no primeiro possível) é de área, o "Máximo" da M1 (S4 da verificação SAF-C01; cache como o pminDraft)
function pmArea(self,saf,d,desde){ const rec=ocNovoRec(self,saf,d,d._rid||'__novo'); const T=talhaoArea(d.talhao); const ctx=ocCtxSaf();
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(rec.plantio||''))) rec.plantio=ocIso(desde+(rec.plano?ocAntecedencia(ctx,rec.plano):0));
  const todos=ocTodos(self); const key=JSON.stringify([rec.cult,rec.var,rec.plano,rec.area,rec.faixa,rec.tipo,rec.plantio,desde,todos]);
  self._pa=self._pa||{}; if(key in self._pa) return self._pa[key];
  const chk=ocChecar(ctx,safList(self),todos,ocTroca(todos,rec),saf,rec.id,T); const M=chk.o?ocMaximo(ctx,chk,T):null; const r=M?r2(M.max):null; self._pa[key]=r; return r; }
function abrirPlanejar(self,t){ const saf=self.state.saf; const L=ocLinha(self,t); if(!saf||!L||!L.planejar) return;
  const sp=GR('g_cult_'+sk(saf)); const cs=cultsDe(self,saf);
  // contexto herdado da safra (cultura, variedade e plano mais usados); quantidade e meta nunca vêm do último valor (AGENTS §3.3)
  const cult=maisUsado(cs,'cult'); const vr=cult?maisUsado(cs.filter(c=>c.v.cult===cult),'var'):''; const pl=cult?maisUsado(cs.filter(c=>c.v.cult===cult&&planById(c.v.plano)),'plano'):'';
  const area=L.area_livre; const d=Object.assign({modo:'plan',talhao:t,cult,var:vr,plano:pl,plantio:'',local:sugerirParcela(self,saf,L,area),area:String(r2(area)).replace('.',','),colheita:''},metaRascunho(cult,'',''));
  const pm=pminDraft(self,saf,d,L.desde); d.plantio=ocIso(pm!==null?pm:L.desde);
  self._plan={t,saf,desde:L.desde};
  g2set(self,sp.id,{fm:{rid:null,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro:false,isNew:true,mode:'form',title:'Planejar '+t},fl:null,fmc:null}); }
function abrirVincular(self,t,cid){ const saf=self.state.saf; const info=self.__oc; if(!saf||!info) return; const o=info.byO[cid]; if(!o) return;
  const src=ocTodos(self).find(c=>c.id===cid); const sp=GR('g_cult_'+sk(saf));
  const d=Object.assign({modo:'vinc',talhao:t,cult:o.cult,var:o.var,plano:'',plantio:ocIso(o.plantio),local:o.faixa,area:String(o.area).replace('.',','),colheita:''},metaRascunho(o.cult,'',''));
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
  if(k==='unm_txt') return metaUnTxt(d);   /* UNID-PROD: a unidade do rascunho, fixada ao abrir (D-U20) */
  if(k==='colh_txt'){ const pl=planById(d.plano); if(!pl||!/^\d{4}-\d{2}-\d{2}$/.test(String(d.plantio||''))) return '—'; const rec=ocNovoRec(self,saf,d,d._rid); const so=safList(self)[saf];
    const o=ocMk(ctx,Object.assign({},rec,{colheita:null}),so); return ocBr(o.fim)+' · do plano'; }
  if(k==='pmin_txt'){ if(!d.talhao) return '—'; const L=ocLinha(self,d.talhao); const desde=(self._plan&&self._plan.desde!==undefined&&self._plan.t===d.talhao)?self._plan.desde:(L?L.desde:null);
    if(desde===null||desde===undefined) return '—'; const pm=pminDraft(self,saf,d,desde); if(pm===null){ const mx=pmArea(self,saf,d,desde); return mx!==null?'reduza a área: máximo '+ocHa(mx)+' ha':'sem janela antes do fim da safra'; }
    const dig=ocDia(d.plantio); return ocBr(pm)+(planById(d.plano)?' com este plano':'')+((dig!==null&&dig<pm)?' · a data digitada é anterior: confira a trava ou a pendência ao salvar':''); }
  if(k==='ocup_txt'){ if(!d.cult||!/^\d{4}-\d{2}-\d{2}$/.test(String(d.plantio||''))) return '—'; const rec=ocNovoRec(self,saf,d,d._rid); const o=ocMk(ctx,rec,safList(self)[saf]); return ocBr(o.ini)+' a '+(o.classe==='semdata'?'sem data':ocBr(o.fim))+(o.classe==='estimado'?' (estimado)':''); }
  return null; }
// rascunho: trocar a cultura traz a variedade e o plano mais usados dela; trocar plano, área ou parcela recalcula o plantio enquanto a
// pessoa não digitou a data (R-17)
function cultDraft(self,gid,k,d,fm){ const saf=self.state.saf; if(!saf||d.modo==='vinc') return null; const cs=cultsDe(self,saf);
  if(k==='plantio'){ d._pt='1'; return d; }
  if(k==='cult'){ d.var=maisUsado(cs.filter(c=>c.v.cult===d.cult),'var')||''; d.plano=maisUsado(cs.filter(c=>c.v.cult===d.cult&&planById(c.v.plano)),'plano')||''; }   /* a unidade da meta sai de metaUnTela (R-U06): _un fica a fixada ao abrir */
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
// demanda por produto (CTL-4): a conta única demFazenda (cal01.js) com as ocorrências do plano desta safra e das outras safras abertas da mesma
// fazenda (ocorr, com os ajustes da tela) e, do MESMO cenário compartilhado (cenDemEntradas), as O.S. (cenOsDem: o que cada ordem ainda tira do
// almoxarifado; a parte do plano que ela cobre sai do plano), o físico apto da própria fazenda, as reservas e os recebimentos (cenEstDem).
// A Compra e o Mapa › Insumos leem a mesma conta.
function demanda(self,saf){ const safRows=g2rows(self,GR('g_saf')); const me=safRows.find(r=>r.id===saf); const faz=(me&&me.v.faz)||'Santa Rita';
  const ordem={}, nomes={}; safRows.forEach((r,i)=>{ ordem[r.id]=i; nomes[r.id]=r.v.nome; });
  const occ=[]; const vistos={}; vistos[sk(saf)]=1;
  const add=(s)=>ocorr(self,s).forEach(o=>occ.push({saf:s,k:o.c.id+'|'+o.a.id,a:String(o.a.id),local:o.c.v.local,tal:o.c.v.talhao||ocTalhaoDe(o.c.v.local,o.c.v.tipo),
    area:o.area,dt:o.dt||'',nome:o.a.nome,prods:o.prods}));   // área com até 2 casas na conta escrita (PRE-REV R5)
  add(saf); safRows.forEach(r=>{ if(r.id===saf||r.ro||(r.v.faz||'Santa Rita')!==faz||vistos[sk(r.id)]) return; vistos[sk(r.id)]=1; add(r.id); });
  const X=cenDemEntradas(cenGet(),{saf,faz,hoje:D2.hoje,viavel:D2.viavel,ordem,nomes,occ},{osb:D2.osb,est:D2.estb}); const m=demFazenda(X);   // ordens e estoque do mesmo cenário (revisão, achado 1)
  Object.values(m).forEach(d=>{ d.quar=(X.quar||{})[d.nome]||0; d.memo=cal01Memo(d.cal,{un:d.un,res:d.res,quar:d.quar,cust:d.cust,custT:d.custT,quarC:d.quarC,quarRef:d.quarRef,cond:d.cond,condFalta:d.condFalta}); });
  // partes fixas desta conta (plano da tela, sem ordens e estoque): a versão da SOL as guarda e a Compra refaz a conta com o cenário de agora
  const ent={saf,faz,hoje:D2.hoje,viavel:D2.viavel,ordem,nomes,occ:occ.map(o=>Object.assign({},o,{prods:(o.prods||[]).map(p=>({nome:p.nome,grupo:p.grupo,un:p.un,preco:p.preco,dose:p.dose,q:p.q,orig:p.orig||'',laudo:p.laudo||''}))}))};   // origem da dose (R21 da análise de solo) vai junto: a Compra refaz a memória igual
  Object.defineProperty(m,'_ent',{value:ent,enumerable:false}); return m; }
// produtividade da colheita (kg/ha) por cultura, a partir dos cultivos da safra aberta cujo plano (compatível) usa a operação; média ponderada pela área.
// A meta em kg/ha sai do conversor único (producao.js, prUnpKgHa; UNID-PROD R-U01): uma tabela de fator só; unidade sem massa fica fora da conta
function prodColheita(self,saf,op){ const by={};
  cultRows(self,saf).forEach(c=>{ const pl=planById(c.v.plano); if(!pl||pl.cultura!==c.v.cult||!pl.atividades.some(a=>a.op===op)) return;
    let kg=0; try{ kg=prUnpKgHa(c.v.cult,Number(c.v.meta)||0,c.v.unm); }catch(e){ kg=0; } const a=Number(c.v.area)||0; if(a<=0||kg<=0) return;
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
    const xa=Object.assign({},g2st(self,gid).x||{}); xa[g.id]=true; xa[g.kids[ai].id]=true; g2set(self,gid,{x:xa});   // TAB-12: a ação abre o caminho da linha nova
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
  r.p.local=[{k:'b',t:r.v.local||'—'}].concat((!kid&&!r.ro&&!r.v.ciclo)?[{k:'act',t:'Dividir',fn:'divide:'+t,lk:true,sec:true}]:[]); r.s.local=r.v.local;
  r.v.tipo=(r.v.tipo==='Parcela'||(kid&&r.v.tipo!=='Talhão inteiro')?'Parcela':'Talhão inteiro'); const tp=r.v.tipo+(r.decl?' (sem polígono)':''); r.p.tipo=[{k:'txt',t:tp}]; r.s.tipo=tp; r.v.livre=''; r.p.livre=[{k:'mut',t:'—'}]; r.s.livre='';
  const mt=metaTela(r); r.p.meta=[{k:'txt',t:mt.t}]; r.s.meta=mt.t; r.ordk=Object.assign({},r.ordk||{},{meta:mt.k}); dcol(r,'dt_plantio',r.v.plantio);   // meta (até 2 casas) com a unidade junto (decisão do proprietário, 05/10/2026), na unidade escolhida (UNID-PROD)
  r.v.ver=(pl&&pl.cultura===r.v.cult)?pl.versao:''; r.p.ver=r.v.ver?[{k:'txt',t:'v'+r.v.ver}]:[{k:'mut',t:'—'}]; r.s.ver=r.v.ver?'v'+r.v.ver:'';
  if(pl && pl.cultura===r.v.cult){ r.p.plano=[{k:'txt',t:pl.nome}]; r.s.plano=pl.nome; }   // SAF-TAB: "Ajustar insumos" saiu da célula; fica no painel da linha (cultActs)
  else if(pl){ r.p.plano=[{k:'chip',t:'Plano de '+pl.cultura+' incompatível',c:'red'},{k:'act',t:'Reaplicar',fn:'applyone:'+r.id}]; r.s.plano='incompatível'; }
  else { r.p.plano=r.ro?[{k:'mut',t:'sem plano'}]:[{k:'mut',t:'sem plano'},{k:'act',t:'Aplicar plano',fn:'applyone:'+r.id}]; r.s.plano=''; }   // a ação vai para o ⋯ da linha (15/10)
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
  r.p.local=[{k:'b',t:t}].concat(r.ro?[]:[{k:'act',t:'Dividir',fn:'divide:'+t,lk:true,sec:true}]); r.s.local=t; }
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
    const p3=(seg&&ocPlantioMin(ctx,S,todos,saf,rec,base,T,null)===null)?' '+ocMsgSemJanela(ctx,chk.o,seg,base,saf,nextNome(chk.o.t,faixasEmUso(self,saf,chk.o.t,rec.id).concat([chk.o.faixa]))):'';
    return {erro:msg+p3,campo:(tp==='safra'||tp==='soma')?'area':'plantio',pend:'',aviso:''}; }
  return {erro:'',pend:ocMsgPend(ctx,chk,saf,pmin),aviso:ocMsgAviso(ctx,chk)}; }
// começo da busca do plantio mínimo de um cultivo: a liberação da ocupação anterior na mesma faixa (ou o início da safra)
function ocBaseMin(chk){ const o=chk.o; const ctx=ocCtxSaf(); let b=o.safini; chk.mesmo.forEach(y=>{ if(y!==o&&ocMesmaArea(y,o)&&y.ini<o.ini&&y.classe!=='perene'){ const l=ocLib(ctx,y,'est'); if(l>b&&l<OC_INF) b=l; } }); return b; }
function cultCheck(self,gid,rows,r,d,isNew,safArg){ const e={}; const saf=safArg||self.state.saf;   /* safArg: o lote do SAF-FAZ-3 confere cada talhão na sub-safra dele */ self._metaDraft={rid:r?r.id:null,d:Object.assign({},d)};   /* UNID-PROD: o cultAfter grava a meta pelo rascunho deste registro (R-U06) */ const t=isNew?String(d.talhao||''):(r&&r.v.talhao); const T=talhaoArea(t);
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
// meta gravada a partir do rascunho conferido no cultCheck: {meta, unm} de antes se o texto não mudou; senão {digitado, unidade do rascunho}
function metaDoRascunho(self,x,isNew){ const md=self._metaDraft; self._metaDraft=null; if(!md||!x||(isNew?md.rid!==null:md.rid!==x.id)) return; const g=metaGravar(Object.assign({},md.d,{cult:x.v.cult})); x.v.meta=g.meta; x.v.unm=g.unm; }
function cultAfter(self,gid,rows,r,isNew){ let all=g2clone(soDaSafra(rows)); let msg=''; const saf=self.state.saf; const extra=self._ocMsg; self._ocMsg=null; let tNovo='';
  if(r&&isNew){ const pl=self._plan||{}; self._plan=null; const t=pl.t||r.v.talhao; tNovo=t||''; const x=g2find(all,r.id); all=all.filter(y=>y.id!==r.id); if(!x||!t){ g2set(self,gid,{rows:normCult(all)}); return; }
    x.v.talhao=t; x.v.faz=safFaz(self,saf); if(sk(saf)==='NOVA') x.v.saf=saf; x.v.plano=x.v.plano||''; x.v.colheita=(!x.v.plano&&x.v.colheita)?x.v.colheita:'';
    // vínculo (R-24): cultura, cultivar, plantio, área e faixa ficam do ciclo; modo 'vinc' trava esses campos ao editar depois (revisão SAF, S3.2)
    if(pl.vinc){ const src=pl.vinc.src||{}; Object.assign(x.v,{cult:src.cult,var:src.var,plantio:src.plantio,area:src.area,local:src.faixa,ciclo:pl.vinc.ciclo,colheita:'',modo:'vinc'}); }
    metaDoRascunho(self,x,true); x.v.unm=unMetaDe(x.v.cult,x.v.unm);
    const T=talhaoArea(t); const a=Number(x.v.area)||0; const daSaf=(c)=>sk(saf)!=='NOVA'||c.v.saf===saf;   // R-22: só os cultivos desta safra
    // o mesmo nome que a trava conferiu (parcelaFinal, S2.2)
    if(a>=T-0.005){ x.v.local=t; x.v.tipo='Talhão inteiro'; x.decl=false; } else { x.v.local=parcelaFinal(self,saf,t,a,x.v.local,r.id); x.v.tipo='Parcela'; x.decl=true; }
    x.s.local=x.v.local; all.push(x); const fim=planById(x.v.plano)?(' · plano '+planById(x.v.plano).nome+'.'):(pl.vinc?'. Escolha o plano agronômico na linha (Aplicar plano).':'. Escolha o plano agronômico na linha.');
    const livre=livreDepois(self,saf,t,leaves(all).filter(c=>c.v.talhao===t&&daSaf(c)));
    msg=pl.vinc?('Ciclo vinculado: '+x.v.local+' · '+x.v.cult+' '+x.v.var+' desde '+br(x.v.plantio)+fim)
      :((x.v.tipo==='Parcela')?('Cultivo incluído como parcela '+x.v.local+' · '+nfa(Math.max(0,livre))+' ha livres em '+t+fim):('Cultivo incluído: '+t+' inteiro'+fim)); }
  else if(r){ const x=g2find(all,r.id); if(x){ metaDoRascunho(self,x,false); x.v.unm=unMetaDe(x.v.cult,x.v.unm); if(x.v.plano) x.v.colheita=''; } }
  const pa=self._planoAntes; self._planoAntes=null;
  if(r&&!isNew&&pa&&pa.id===r.id&&pa.plano!==String(r.v.plano||'')){ const adj=JSON.parse(JSON.stringify(adjOf(self))); const n=Object.keys(adj[r.id]||{}).length; const pl=planById(r.v.plano);
    if(n){ delete adj[r.id]; self.setState({adj}); }
    msg=(pl?('Plano de '+r.v.local+': '+pl.nome+' v'+pl.versao):('Plano retirado de '+r.v.local))+(n?(' · '+n+(n>1?' ajustes de dose descartados':' ajuste de dose descartado')):'')+'. Plano operacional, recursos e demanda recalculados.'; }
  if(extra) msg=(msg?msg+' ':'')+'Atenção: '+extra+'.';
  // TAB-12 (17/10/2026): gravar abre só o caminho do cultivo gravado (a faixa da fazenda e o grupo do talhão, pelo id gravado e pelo da
  // linha de exibição, grp_<talhão>); o resto da tabela fica como a pessoa deixou
  const norm=normCult(all); const st=g2st(self,gid); const xa=Object.assign({},st.x||{}); const tg=tNovo||(r&&r.v&&r.v.talhao)||'';
  if(tg){ xa['fzg_'+saf]=true; xa['grp_'+tg]=true; norm.forEach(y=>{ if(y.grp&&y.v.talhao===tg) xa[y.id]=true; }); }
  g2set(self,gid,{rows:norm,x:xa}); if(msg) self.setState({g2toast:msg}); }
// área livre do talhão depois de gravar (SAF-C01): a mesma conta da coluna Área livre e do painel (ocTabela, R-09), com as folhas novas desta
// safra no lugar das gravadas e as ocupações de fora (perene sem fim e outras safras)
function livreDepois(self,saf,t,folhas){ const S=safList(self); const so=S[saf]; if(!so) return 0; const ctx=ocCtxSaf();
  const todos=ocTodos(self).filter(c=>c.saf!==saf).concat(folhas.map(c=>ocCult(c,saf,so.faz)));
  const L=ocTabela(ctx,so,ocOcupacoes(ctx,S,todos),[[t,talhaoArea(t)]],S)[0]; return L.length?L[0].area_livre:0; }
// capacidade do Dividir (SAF-C01): área do talhão − maior área física das ocupações de fora (outras safras) em núcleo nos dias de núcleo das
// parcelas (ocPior, a conta da T-soma): parcelas que somam até ela não travam pela área. Sem parcela com plantio, o período desta safra
function dvCap(self,t,rows){ const saf=self.state.saf; const T=talhaoArea(t); const S=safList(self); const so=S[saf]; if(!so) return {cap:T,pior:0,p:null};
  const ctx=ocCtxSaf(); const fora=ocOcupacoes(ctx,S,ocTodos(self).filter(c=>c.faz===so.faz&&c.talhao===t&&c.saf!==saf));
  let g=(rows||[]).filter(x=>/^\d{4}-\d{2}-\d{2}$/.test(String(x.plantio||''))).map((x,i)=>ocMk(ctx,{id:'__dv'+i,saf,faz:so.faz,talhao:t,faixa:String(x.local||'').trim()||t+'-?'+i,tipo:'Parcela',
    area:g2num(x.area)||0,cult:x.cult,var:x.var||'',plantio:x.plantio,plano:x.plano||null,colheita:x.colheita||null},so));
  if(!g.length){ const a=ocDia(so.ini), b=ocDia(so.fim); g=[{plantio:a,ini:a,nuc:b,fim:b,folga:1}]; }
  const p=ocPior(ctx,g,fora); const pior=p?p.pior:0; return {cap:Math.max(0,Math.floor((T-pior)*100+1e-6)/100),pior:r2(pior),p,g}; }   // para baixo, como o "Máximo" da M1
// ---- painel: dividir o talhão em quantas parcelas precisar ----
// ---- meta de produtividade (UNID-PROD · docs/unidades-produtividade R-U06, D-U05, D-U20) ----
// A meta guarda o valor e a unidade informados ({meta, unm}); o kg/ha sai do conversor único a cada leitura. A unidade nunca é escolhida na
// linha (revisão SAF, S3.7): vem do seletor "Unidade de produtividade" da tabela, fixada no rascunho ao abrir o painel ou o Dividir. Salvar com
// o texto do campo igual ao mostrado ao abrir não regrava nada (sem deriva). Sem migração: as metas atuais já estão no Padrão (D2.unMeta).
function metaPer(cult){ return /\/ano$/.test(String((D2.unMeta||{})[cult]||''))?'/ano':''; }
function metaUnOk(cult,un){ if(!un) return false; try{ return !!prUnpMassa(cult,un)&&(/\/ano$/.test(un)?'/ano':'')===metaPer(cult); }catch(e){ return false; } }
// unidade da meta: a informada, se é massa válida para a cultura (com o período dela); senão o Padrão da cultura (CD-02, DEC-0510-03)
function unMetaDe(cult,un0){ return metaUnOk(cult,un0)?un0:((D2.unMeta||{})[cult]||un0||'sc/ha'); }
function metaPref(cult){ return (typeof g2unidPref==='function')?g2unidPref(cult):'padrao'; }
// meta na tabela: na unidade escolhida para a cultura (até 2 casas, R-U02); chave estável em kg/ha para ordenar e filtrar (R-U11)
function metaTela(r){ const m=r.v.meta; if(m===''||m===undefined||m===null) return {t:nfa(m)+(r.v.unm?' '+r.v.unm:''),k:null};
  try{ const x=prUnpMeta(r.v.cult,m,r.v.unm,metaPref(r.v.cult)); return {t:x.txt,k:x.kgHa}; }catch(e){ return {t:nfa(m)+(r.v.unm?' '+r.v.unm:''),k:null}; } }
// rascunho da meta ao abrir: o número na unidade da preferência, com a unidade fixa (_un) e a origem (_m0, _u0, _c0) e o texto mostrado (_t0)
function metaRascunho(cult,meta,unm){ const vz=(meta===''||meta===undefined||meta===null); let un=unMetaDe(cult,unm), t=vz?'':String(meta).replace('.',',');
  try{ const op=metaPref(cult); const ops=prUnpOpcoes(cult,'base'); const o=ops.find(x=>x.k===op&&x.ok)||ops[0];
    if(vz) un=o.un+metaPer(cult); else { const m=prUnpMeta(cult,meta,unm,op); if(m.ok){ t=prFmtT(m.n2,2).replace(/\./g,''); un=m.un; } } }catch(e){}
  return {meta:t,_t0:t,_m0:vz?'':String(meta),_u0:unm||'',_un:un,_c0:cult||''}; }
// o que gravar: texto igual ao mostrado ao abrir (e a mesma cultura) mantém {meta, unm} gravados; senão {número digitado, unidade do rascunho}
function metaGravar(d){ const t=String(d.meta===undefined||d.meta===null?'':d.meta).trim();
  if(d._t0!==undefined&&d._m0!==''&&t===d._t0&&String(d.cult||'')===String(d._c0||'')) return {meta:Number(d._m0),unm:unMetaDe(d.cult,d._u0)};
  return {meta:g2num(t),unm:metaUnTela(d)}; }
// unidade ao lado do campo e a gravada com o número digitado. Na cultura de abertura (_c0), a fixada ao abrir (_un, D-U20). Trocada a cultura
// (painel ou linha do Dividir), com o campo vazio vale a preferência da nova cultura (D-U01); com número, fica a mesma opção (kg/ha, t/ha,
// sc 60, cx 10) se ela existe na nova cultura, com o período dela (kg/ha → kg/ha/ano); sem a opção, o Padrão da nova cultura com o número
// como está (como hoje). Sem isso, 3.720 kg/ha da soja virava 3.720 t/ha/ano no mamão: mil vezes a meta (revisão v57, S2)
function metaUnTela(d){ const cu=d.cult, un=d._un||d.unm, c0=d._c0;
  if(c0===undefined||String(c0)===String(cu||'')) return unMetaDe(cu,un);
  try{ const vz=String(d.meta===undefined||d.meta===null?'':d.meta).trim()===''; const m=vz?null:prUnpMassa(c0,un); const k=vz?metaPref(cu):(m?m.k:'padrao');
    const o=prUnpOpcoes(cu,'base').find(x=>x.k===k&&x.ok); if(o) return o.un+metaPer(cu); }catch(e){}
  return unMetaDe(cu,''); }
// texto do campo "Unidade da meta": "kg/ha · Padrão da cultura: sc/ha (60 kg)"; no Padrão, "sc/ha · Padrão da cultura"
function metaUnTxt(d){ const un=metaUnTela(d); const pad=(D2.unMeta||{})[d.cult]||''; let rot=pad;
  try{ rot=prUnpOpcoes(d.cult,'base')[0].rot.replace('Padrão da cultura · ','').replace(/^(\S+)/,'$1'+metaPer(d.cult)); }catch(e){}
  return un===pad?un+' · Padrão da cultura':un+' · Padrão da cultura: '+rot; }
// gancho de abertura do formulário (g2open → self.g2openDraft): a meta entra no rascunho na unidade escolhida, com a origem guardada (R-U06, RC-02)
// SAF-FAZ-1-CONTEXTO-01 (Codex 6174131920, S3): "Nova safra" com o chip de uma fazenda escolhido nasce nessa fazenda; sem chip, o padrão do
// campo. Editar não passa por aqui: a safra existente conserva a própria fazenda
function safNovaDraft(self,gid){ if(gid!=='g_saf') return null; const fq=g2st(self,'g_saf').qv; const fd=((GR('g_saf').edit||{}).fields||[]).find(f=>f.k==='fazs');
  self.__sgCh='saf-form:'+Date.now()+':'+Math.random().toString(36).slice(2,8);   // chave do comando, gerada por quem abre o formulário (ENG-021)
  return (fq&&fd&&(fd.opts||[]).indexOf(fq)>=0)?{fazs:fq}:null; }
// ---- SAF-FAZ-2 · safra com várias fazendas: a tela chama o domínio único (safra_grupo.js); cada fazenda segue com a própria sub-safra ----
function sgLista(self){ return g2rows(self,GR('g_saf')).map(r=>Object.assign({id:r.id,nome:r.v.nome,ini:r.v.ini,fim:r.v.fim,faz:r.v.faz||'Santa Rita',estado:r.v.estado||'Rascunho'},r.v.mae?{mae:r.v.mae}:{},r.ro?{ro:true}:{})); }
function sgFazsTxt(d){ return String((d&&d.fazs)||'').split(';').map(x=>x.trim()).filter(Boolean); }
// o que prende a fazenda à safra: cultivos, solicitação enviada e O.S. (o protótipo não registra aprovação de plano e de orçamento por safra nova)
function sgDeps(self){ return (saf)=>{ const sol=solMap(self)[saf]; return {cultivos:cultsDe(self,saf).length,sol:sol?{id:sol.id,estado:solEstado(saf,sol)||sol.estado||''}:null,os:[]}; }; }   // estado da compra: o andamento gravado pela Compra (cenário) vale sobre o do envio
function sgPed(self,r,d,isNew){ return {chave:self.__sgCh||('saf-form:'+(r?r.id:'novo')),nome:d.nome,ini:d.ini,fim:d.fim,fazendas:sgFazsTxt(d),saf:isNew?undefined:(r&&r.id)}; }
function sgMotivos(b){ return b.map(x=>x.faz+' não pode sair da safra: '+x.motivos.map(m=>m.t.replace(/\.$/,'')+(m.destino?' (resolva em '+m.destino+')':'')).join('; ')+'.').join(' '); }
// antes de gravar: a mesma composição, sem efeito, para recusar com o motivo no próprio campo (nada muda)
function sgChecar(self,rows,r,d,isNew){ const e={}; let k=0; const lista=sgLista(self).filter(x=>!(isNew&&r&&x.id===r.id));
  const res=sgCompor(lista,Object.assign(sgPed(self,r,d,isNew),{chave:'conferir'}),{rec:{},deps:sgDeps(self),novoId:(t)=>'conf'+(++k)});
  if(res.ok) return e; if(res.bloqueios) e.fazs=sgMotivos(res.bloqueios); const er=res.erros||{}; if(er.fazendas) e.fazs=er.fazendas; if(er.fim&&!e.fim) e.fim=er.fim; if(er.ini) e.ini=er.ini; if(er.saf) e.fazs=er.saf; return e; }
// depois de gravar o formulário: aplica a composição nas linhas (as que ficam conservam o objeto, o ID e o estado; as novas nascem em rascunho)
function sgAplicar(self,rows,r,isNew){ const d={nome:r.v.nome,ini:r.v.ini,fim:r.v.fim,fazs:r.v.fazs||r.v.faz};
  const lista=sgLista(self).filter(x=>!(isNew&&x.id===r.id)); let usado=false, k=0;
  const novoId=(t,faz)=>{ if(t==='mae') return 'M'+String(Date.now()).slice(-6); if(isNew&&!usado){ usado=true; return r.id; } return 'n'+(rows.length+(++k))+'_'+String(Date.now()).slice(-5); };
  self.__sgRec=self.__sgRec||{};
  const res=sgCompor(lista,sgPed(self,r,d,isNew),{rec:self.__sgRec,deps:sgDeps(self),novoId}); self.__sgCh=null;
  if(!res.ok||res.repetido){ delete r.v.fazs; return res.ok?'':(res.bloqueios?sgMotivos(res.bloqueios):'Não salvo.'); }
  const novas=sgLinhasNovas(isNew?rows.concat(rows.indexOf(r)<0?[r]:[]):rows,res);
  g2set(self,'g_saf',{rows:novas}); const sp0=sempSem(self,res); if(sp0) self.setState({semp:sp0});
  if(isNew){ const sb=res.recibo.subs; const lst=(a)=>a.length>1?a.slice(0,-1).join(', ')+' e '+a[a.length-1]:a[0];
    return sb.length>1?(res.recibo.nome+' criada em '+sb.length+' fazendas: '+lst(sb.map(x=>x.faz))+'. Cada fazenda planeja os próprios talhões, recursos e demanda.'):''; }
  return sgMsgMuda(res); }
// linhas da etapa 1 depois da composição: as que ficam conservam o objeto, o ID e o estado; as novas nascem em rascunho
function sgLinhasNovas(rows,res){ const por={}; rows.forEach(x=>{ por[x.id]=x; });
  return res.safs.map(s=>{ const x=por[s.id]||{id:s.id,v:{},s:{},p:{}}; Object.assign(x.v,{nome:s.nome,ini:s.ini,fim:s.fim,faz:s.faz,estado:s.estado||'Rascunho'});
    if(s.mae) x.v.mae=s.mae; else delete x.v.mae; delete x.v.fazs; x.v.periodo=safPeriodo(s.ini,s.fim)||x.v.periodo||''; return x; }); }
function sgMsgMuda(res){ const sb=res.recibo.subs, ent=sb.filter(x=>x.acao==='criada'||x.acao==='trocada').map(x=>x.faz), sai=sb.filter(x=>x.acao==='removida').map(x=>x.faz).concat(sb.filter(x=>x.acao==='trocada').map(x=>x.de));
  const lst=(a)=>a.length>1?a.slice(0,-1).join(', ')+' e '+a[a.length-1]:a[0];
  return [ent.length?lst(ent)+(ent.length>1?' entraram':' entrou')+' na safra em rascunho.':'',sai.length?lst(sai)+(sai.length>1?' saíram':' saiu')+' da safra.':''].filter(Boolean).join(' '); }   // sem fazenda entrando ou saindo, fica o aviso de sempre ("Salvo · linha e totais atualizados")
// leitura reunida das fazendas da safra aberta (sgLeitura): área dos cultivos, estado, solicitação e demanda de cada uma
function sgInfo(self,G,comDem){ const o={}; G.subs.forEach(s=>{ const cs=cultsDe(self,s.id); const sol=solMap(self)[s.id];
  let dem=null; if(comDem){ try{ const dm=demanda(self,s.id); dem=Object.values(dm).filter(x=>x&&x.nome).map(x=>({insumo:x.nome,un:x.un,qtd:x.liq,destino:(dm._ent&&dm._ent.local)||('Almoxarifado '+s.faz)})); }catch(e){ dem=null; } }
  const ar=sgAreaDe(cs.map(c=>c.v.area));   // Codex 6179070575: área vazia não vira zero
  o[s.id]={area_ha:ar.area_ha,area_incompleta:ar.area_incompleta,cultivos:cs.length,estado:s.estado,sol:sol?{id:sol.id,estado:solEstado(s.id,sol)||sol.estado||''}:null,demanda:dem}; }); return o; }
// envio das fazendas da safra: uma solicitação por sub-safra pelo comando de sempre; a chave fica até tudo dar certo (repetir só tenta o que falhou)
function sgEnviarUm(self,saf){ const cap={msg:''}; const ant=(self.__solTmp||{})[saf]; self.__envCap=cap; try{ enviar(self,saf); }finally{ self.__envCap=null; }
  const m=cap.msg||''; const volta=()=>{ if(!self.__solTmp) return; if(ant) self.__solTmp[saf]=ant; else delete self.__solTmp[saf]; };   // o que não foi gravado não fica como enviado
  const sol=solMap(self)[saf];
  if(/^Safra encerrada/.test(m)||/Nada foi alterado/.test(m)){ volta(); return {ok:false,erro:m}; }
  if(/não guarda dados/.test(m)){ volta(); return {ok:false,erro:'este navegador não guardou a solicitação; a Compra de insumos não a veria'}; }
  return {ok:true,recibo:sol?(sol.id+(sol.comp?'-C'+sol.comp:'')):'nada a cotar'}; }
function sgEnviarTela(self,G){ self.__sgEnvRec=self.__sgEnvRec||{}; if(!self.__sgEnvCh) self.__sgEnvCh='env:'+(G.mae||'')+':'+Date.now();
  self.__solTmp=Object.assign({},solMap(self));
  let r; try{ r=sgEnviar(G,self.__sgEnvCh,self.__sgEnvRec,(saf)=>sgEnviarUm(self,saf)); }finally{ var sols=self.__solTmp; self.__solTmp=null; }
  const rec=r.recibos.map(x=>x.faz+': '+(x.recibo==='nada a cotar'?'nada a cotar':x.recibo)+(x.repetido?' (já enviada)':'')).join(' · ');
  const fal=r.falhas.map(x=>x.faz+': '+x.erro).join(' · ');
  if(r.ok) self.__sgEnvCh=null;
  self.setState({sol:sols,g2toast:r.ok?('Demanda das '+G.subs.length+' fazendas enviada. '+rec+'.'):((r.parcial?'Envio parcial. Enviado: '+rec+'. ':'Nada foi enviado. ')+'Falhou: '+fal+'. Tente de novo: só a que falhou é enviada.')}); }
// ===== SAF-FAZ-3 · várias fazendas por vez, com rapidez, e talhão sem plantio (proprietário, 15/10/2026) =====
// "em planejar safra ainda não aparece opção de selecionar fazendas e talhões de mais de 1 fazenda por vez… bem produtiva, rápida, prática e
// fácil e visualmente intuitiva e organizada"; "pode ser que algum talhão o produtor não deseje plantar nada, então isso tem que ser permitido".
// A. Faixa "Trabalhando em": as fazendas da safra em chips (✓) e "+ Fazenda" (lista do DS); marcar/desmarcar compõe a safra pelo domínio único
//    do SAF-FAZ-2 (sgCompor: tirar fazenda com vínculo é recusado com o motivo no próprio lugar; fazenda nova nasce em rascunho).
// B. A etapa 2 mostra os talhões de todas as fazendas juntos, um grupo por fazenda (syncTalhoes), com filtro rápido por fazenda.
// C. "Planejar talhões livres": vários talhões de uma ou mais fazendas de uma vez; cada um pela regra do cultivo único (cultCheck).
// D. "Não plantar nesta safra": o talhão livre fica "Sem plantio" (estado da safra, como os cultivos), sem pendência nem cultivo.
// Cada fazenda continua com a própria sub-safra (cultivos, ocupação, capacidade e demanda): nada de uma fazenda cobre a falta de outra.
function sgSubs(self,saf){ if(!saf) return []; const G=sgGrupo(sgLista(self),saf); return G?G.subs:[]; }
function sgSubDeTalhao(self,saf,t){ const f=(D2.talfaz||{})[t]; return sgSubs(self,saf).find(s=>s.faz===f)||null; }
function cultsGrupo(self,saf){ const subs=sgSubs(self,saf); const L=subs.length?subs:(saf?[{id:saf}]:[]); const o=[]; L.forEach(s=>cultsDe(self,s.id).forEach(c=>o.push({c,saf:s.id}))); return o; }
function temPlanoDe(self,saf){ return cultsDe(self,saf).some(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; }); }
// a tabela é a da sub-safra aberta; agir numa linha de outra fazenda abre antes a sub-safra dela (a mesma tabela: busca, filtros, colunas e
// grupos abertos vão junto) e só então age, com a ocupação já calculada para ela (a ação roda no desenho seguinte, PREVALS)
function sgNaFazenda(self,sub,fn){ const saf=self.state.saf; if(!sub||sub===saf){ fn(); return; }
  const de='g_cult_'+sk(saf), para='g_cult_'+sk(sub); const all=Object.assign({},self.state.g2||{});
  if(de!==para){ const o=all[de]||{}; const n=Object.assign({},all[para]||{}); ['q','qv','f','so','x','cv','cvpf'].forEach(k=>{ if(o[k]!==undefined) n[k]=o[k]; else delete n[k]; }); all[para]=n;
    all[de]=Object.assign({},o,{fm:null,cf:null,fmc:null}); }   // nada fica aberto escondido na grade de antes
  self.__xfn={sub,fn}; self.setState({saf:sub,g2:all}); }
function sgPorTalhao(self,t,fn){ const s=sgSubDeTalhao(self,self.state.saf,t); sgNaFazenda(self,s?s.id:null,fn); }
function sgPorCultivo(self,cid,fn){ const x=cultsGrupo(self,self.state.saf).find(y=>y.c.id===cid); sgNaFazenda(self,x?x.saf:null,fn); }
function safIrEtapa(self,i,extra){ const saf=self.state.saf; const subs=sgSubs(self,saf); let alvo=saf;
  if(i>=3&&subs.length>1&&!temPlanoDe(self,saf)){ const s=subs.find(x=>temPlanoDe(self,x.id)); if(s) alvo=s.id; }   // abre a fazenda que tem o que dimensionar
  g2etapa(self,Object.assign({step:i,corr:null},alvo!==saf?{saf:alvo}:{},extra||{})); }
// ---- D · talhão sem plantio: estado da safra (por sub-safra e fazenda); só talhão livre sem cultivo desta safra ----
function sempDe(self,saf){ const o=(self.state.semp||{})[saf]; if(!o) return {}; return o.faz===safFaz(self,saf)?(o.tal||{}):{}; }
function sempSem(self,res){ const x=self.state.semp; if(!x||!res||!res.recibo) return null; const o=Object.assign({},x); let mud=false;
  res.recibo.subs.forEach(y=>{ if((y.acao==='removida'||y.acao==='trocada')&&o[y.saf]){ delete o[y.saf]; mud=true; } }); return mud?o:null; }   // fazenda que sai leva as marcas
function sempMarcar(self,t,on){ const saf=self.state.saf; const su=sgSubDeTalhao(self,saf,t)||{id:saf,faz:safFaz(self,saf)}; const so=safById(self,su.id);
  if(!so||so.ro){ self.setState({g2toast:'Safra encerrada: somente consulta.'}); return; }
  if(on&&cultsDe(self,su.id).some(c=>(c.v.talhao||ocTalhaoDe(c.v.local,c.v.tipo))===t)){ self.setState({g2toast:'Não foi possível: '+t+' já tem cultivo nesta safra.'}); return; }
  const semp=Object.assign({},self.state.semp||{}); const cur=Object.assign({},sempDe(self,su.id)); if(on) cur[t]=true; else delete cur[t];
  semp[su.id]={faz:su.faz,tal:cur}; self.setState({semp,g2toast:on?(t+' sem plantio nesta safra.'):(t+' volta a ser planejado nesta safra.')}); }
// ---- A · fazendas da safra na faixa "Trabalhando em" ----
function sgAlternarFazenda(self,faz){ const saf=self.state.saf; const G=saf?sgGrupo(sgLista(self),saf):null; const so=safById(self,saf); if(!G||!so||so.ro) return;
  const atuais=G.subs.map(x=>x.faz); const tira=atuais.indexOf(faz)>=0; const fazendas=tira?atuais.filter(f=>f!==faz):atuais.concat([faz]);
  const ch='saf-faz:'+saf+':'+faz+':'+Date.now()+':'+Math.random().toString(36).slice(2,7);   // chave do comando, gerada por quem age (ENG-021)
  self.__sgRec=self.__sgRec||{}; const rows=g2clone(g2rows(self,GR('g_saf'))); let k=0;
  const novoId=(t)=>t==='mae'?('M'+String(Date.now()).slice(-6)):('n'+(rows.length+(++k))+'_'+String(Date.now()).slice(-5));
  const res=sgCompor(sgLista(self),{chave:ch,nome:G.nome,ini:G.ini,fim:G.fim,fazendas,saf},{rec:self.__sgRec,deps:sgDeps(self),novoId});
  const P=Object.assign({},self.state.sfz||{});
  if(!res.ok){ const er=res.bloqueios?sgMotivos(res.bloqueios):((res.erros||{}).fazendas?'A safra precisa de ao menos uma fazenda.':(Object.values(res.erros||{})[0]||'Nada foi alterado.'));
    self.setState({sfz:Object.assign(P,{err:{[faz]:er}})}); return; }   // recusa no próprio lugar; nada muda
  const all=Object.assign({},self.state.g2||{}); all.g_saf=Object.assign({},all.g_saf||{},{rows:sgLinhasNovas(rows,res)});
  const ficam=res.recibo.subs.filter(y=>y.acao!=='removida').map(y=>y.saf); const nsaf=ficam.indexOf(saf)>=0?saf:ficam[0];
  self.setState(Object.assign({g2:all,saf:nsaf,sfz:Object.assign(P,{err:{}}),g2toast:sgMsgMuda(res)||'Salvo.'},sempSem(self,res)?{semp:sempSem(self,res)}:{})); }
function sfzAbrir(self,e){ let x=16, y=120; try{ const r=e&&e.currentTarget&&e.currentTarget.getBoundingClientRect(); if(r){ x=r.left; y=r.bottom; } }catch(er){}
  self.setState({sfz:{open:true,x,y,err:{}}}); setTimeout(()=>{ try{ const i=document.querySelector('#sfz-pop input'); if(i) i.focus(); }catch(er){} },30); }
function sfzVals(self,v,saf,step,ro){ const G=saf?sgGrupo(sgLista(self),saf):null; const P=self.state.sfz||{}; const fz=G?G.subs.map(x=>x.faz):[];
  v.sfz_chips_on=!!G&&step<=2; v.sfz_txt_on=!v.sfz_chips_on; v.sfz_add=v.sfz_chips_on&&!ro; v.sfz_exp=String(!!P.open);
  v.sfz_chips=fz.map(f=>({t:'✓ '+f,al:'Fazenda '+f+(ro?'':', nesta safra: alterar as fazendas'),go:(e)=>{ if(!ro) sfzAbrir(self,e); },dis:ro}));
  v.sfz_abrir=(e)=>sfzAbrir(self,e);
  const fechar=()=>{ self.setState({sfz:{open:false}}); setTimeout(()=>{ try{ const b=document.getElementById('sfz-add'); if(b) b.focus(); }catch(er){} },30); };
  v.sfz_pop=!!P.open&&v.sfz_add; v.sfz_fechar=fechar; v.sfz_key=(e)=>{ if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); fechar(); } };
  const W=320, vw=(typeof window!=='undefined'?window.innerWidth:1440); v.sfz_pos='top:'+Math.round((P.y||120)+6)+'px;left:'+Math.round(Math.max(8,Math.min(P.x||16,vw-W-8)))+'px;width:'+Math.min(W,vw-16)+'px;';
  v.sfz_ops=Object.keys(D2.talOrd||{}).map((f,i)=>{ const er=(P.err||{})[f]||''; const n=talOrd(f).length;
    return {t:f,sub:nfa(talTot(f))+' ha · '+n+(n===1?' talhão':' talhões'),on:fz.indexOf(f)>=0,tog:()=>sgAlternarFazenda(self,f),err:er,hasErr:!!er,id:'sfz-o'+i}; }); }
// ---- B · filtro rápido por fazenda, ao lado da busca (só com mais de uma fazenda) ----
function ffzVals(self,v,saf,step){ const subs=step===2?sgSubs(self,saf):[]; const cur=subs.some(x=>x.faz===self.state.ffz)?self.state.ffz:'';
  v.ffz_tem=subs.length>1;
  v.ffz_l=v.ffz_tem?[{t:'Todas',on:String(!cur),al:'Mostrar todas as fazendas',go:()=>self.setState({ffz:''})}].concat(subs.map(x=>({t:x.faz,on:String(cur===x.faz),al:cur===x.faz?'Mostrar todas as fazendas':'Mostrar só '+x.faz,go:()=>self.setState({ffz:cur===x.faz?'':x.faz})}))):[]; }
// ---- C · planejar vários talhões livres de uma vez ----
// livres = com área a planejar (os mesmos do "Planejar ›" da linha, inclusive o resto livre de um talhão já dividido) e sem a marca "sem plantio";
// de uma fazenda (faz) ou de todas as da safra
function pltLivres(self,saf,faz){ const subs=sgSubs(self,saf); const L=subs.length?subs:[{id:saf,faz:safFaz(self,saf)}]; const out=[];
  L.forEach(su=>{ if(faz&&su.faz!==faz) return; const info=(self.__ocG&&self.__ocG[su.id])||(su.id===saf?self.__oc:null); if(!info||!info.linhas||info.ro) return;
    info.linhas.forEach(l=>{ if(l.planejar&&!l.semp) out.push({sub:su.id,faz:su.faz,t:l.t,L:l}); }); }); return out; }
function pltAbrir(self,faz){ const saf=self.state.saf; const so=safById(self,saf); if(!so||so.ro) return;
  const lv=pltLivres(self,saf,faz||''); if(!lv.length){ self.setState({g2toast:'Nenhum talhão livre para planejar.'}); return; }
  // contexto herdado: cultura, variedade e plano mais usados na safra (todas as fazendas); quantidade, meta e data nunca vêm do último valor
  const cs=cultsGrupo(self,saf).map(x=>x.c); const cult=maisUsado(cs,'cult'); const vr=cult?maisUsado(cs.filter(c=>c.v.cult===cult),'var'):''; const pl=cult?maisUsado(cs.filter(c=>c.v.cult===cult&&planById(c.v.plano)),'plano'):'';
  const sel={}; lv.forEach(x=>{ sel[x.t]=true; });
  self.setState({plt:{ch:'plt:'+saf+':'+Date.now()+':'+Math.random().toString(36).slice(2,7),faz:faz||'',sel,cult,var:vr,plano:pl,plantio:'',pt:false,meta:'',err:{},gerr:''}}); }
function pltRascunho(self,P,x,plantio){ const L=x.L; const area=L.area_livre;
  return Object.assign({modo:'plan',talhao:x.t,cult:P.cult,var:String(P.var||'').trim(),plano:P.plano||'',plantio,local:sugerirParcela(self,x.sub,L,area),area:String(r2(area)).replace('.',','),colheita:''},
    metaRascunho(P.cult,'',''),{meta:String(P.meta===undefined?'':P.meta)}); }
// primeiro plantio possível do talhão com a cultura e o plano escolhidos (a mesma busca do painel do cultivo, PlantioMin)
function pltPmin(self,P,x){ if(!P.cult) return x.L.desde; const d=pltRascunho(self,P,x,''); const pm=pminDraft(self,x.sub,d,x.L.desde); return pm!==null?pm:x.L.desde; }
function pltData(self,P,lv){ if(P.pt) return P.plantio||''; const ms=lv.filter(x=>P.sel[x.t]).map(x=>pltPmin(self,P,x)).filter(n=>n!==null&&n!==undefined); return ms.length?ocIso(Math.max.apply(null,ms)):''; }
function pltCultivo(self,x,d,id){ const T=talhaoArea(x.t); const a=g2num(d.area); const mg=metaGravar(d);
  const c={id,v:{talhao:x.t,faz:x.faz,cult:d.cult,var:d.var,plano:d.plano||'',plantio:d.plantio,area:r2(a),colheita:'',meta:mg.meta,unm:unMetaDe(d.cult,mg.unm)},s:{},p:{}};
  if(sk(x.sub)==='NOVA') c.v.saf=x.sub;
  if(a>=T-0.005){ c.v.local=x.t; c.v.tipo='Talhão inteiro'; c.decl=false; } else { c.v.local=parcelaFinal(self,x.sub,x.t,a,d.local,id); c.v.tipo='Parcela'; c.decl=true; }
  c.s.local=c.v.local; return c; }
function pltGravar(self){ const P=self.state.plt; if(!P) return; self.__pltRec=self.__pltRec||{};
  if(self.__pltRec[P.ch]){ self.setState({plt:null}); return; }   // o mesmo comando repetido (duplo clique) não grava de novo (ENG-021)
  const saf=self.state.saf; const lv=pltLivres(self,saf,P.faz).filter(x=>P.sel[x.t]); const e={};
  const plantio=pltData(self,P,pltLivres(self,saf,P.faz));
  if(!P.cult) e.cult='Escolha a cultura.'; if(!String(P.var||'').trim()) e.var='Informe a variedade.';
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(plantio))) e.plantio='Informe o plantio.';
  const m=g2num(P.meta); if(String(P.meta===undefined?'':P.meta).trim()===''||isNaN(m)||m<0) e.meta='Informe a meta (≥ 0).';
  const pl=planById(P.plano); if(pl&&pl.cultura!==P.cult) e.plano='Este plano é de '+pl.cultura+'. Escolha um plano de '+P.cult+' ou deixe sem plano.';
  if(Object.keys(e).length||!lv.length){ self.setState({plt:Object.assign({},P,{err:e,gerr:lv.length?'Corrija os campos destacados; o que você digitou foi mantido.':'Marque ao menos um talhão.'})}); return; }
  // cada talhão pela regra do cultivo único (cultCheck: plano da mesma cultura, área do talhão, plantio na janela, sobreposição); recusa atômica
  const errT={}, avisos=[], novos=[]; const plan0=self._plan; self._plan=null;
  lv.forEach(x=>{ const d=pltRascunho(self,P,x,plantio); const gid='g_cult_'+sk(x.sub); const er=cultCheck(self,gid,g2rows(self,GR(gid)),null,d,true,x.sub);
    if(Object.keys(er).length) errT['t:'+x.t]=Object.values(er)[0]; else { if(self._ocMsg) avisos.push(x.t+': '+String(self._ocMsg).replace(/\.$/,'')); novos.push({x,d}); } });
  self._plan=plan0; self._ocMsg=null; self._metaDraft=null; self._planoAntes=null;
  if(Object.keys(errT).length){ const n=Object.keys(errT).length;
    self.setState({plt:Object.assign({},P,{err:errT,gerr:n+(n>1?' talhões não podem ser planejados':' talhão não pode ser planejado')+' com estes dados: ajuste a data ou desmarque. Nada foi gravado.'})}); return; }
  // um cultivo por talhão, na grade da sub-safra dele; um setState só (as fazendas novas dividem a grade das safras novas)
  const all=Object.assign({},self.state.g2||{}); const porG={}; const stamp=String(Date.now()).slice(-6);
  novos.forEach(({x,d},i)=>{ const gid='g_cult_'+sk(x.sub); if(!porG[gid]) porG[gid]=g2clone(soDaSafra(g2rows(self,GR(gid)))); porG[gid].push(pltCultivo(self,x,d,'c'+String(x.t).replace(/\W/g,'')+'_'+stamp+'_'+i)); });
  Object.keys(porG).forEach(gid=>{ const st=all[gid]||{}; all[gid]=Object.assign({},st,{rows:normCult(porG[gid])}); });
  // TAB-12 (17/10/2026): a ação abre o caminho dos cultivos novos na tabela à vista (a da sub-safra aberta): a faixa de cada fazenda e o talhão
  { const gv='g_cult_'+sk(self.state.saf), xa=Object.assign({},(all[gv]||{}).x||{}); novos.forEach(({x})=>{ xa['fzg_'+x.sub]=true; xa['grp_'+x.t]=true; }); all[gv]=Object.assign({},all[gv]||{},{x:xa}); }
  self.__pltRec[P.ch]={n:novos.length};
  const fz={}; novos.forEach(({x})=>{ (fz[x.faz]||(fz[x.faz]=[])).push(x.t); }); const fks=Object.keys(fz);
  const onde=fks.length>1?fks.map(f=>fz[f].join(', ')+' ('+f+')').join(' e '):fz[fks[0]].join(', ');
  self.setState({g2:all,plt:null,g2toast:novos.length+(novos.length>1?' talhões planejados: ':' talhão planejado: ')+onde+' · '+P.cult+(pl?' · plano '+pl.nome+'.':'. Escolha o plano agronômico na linha.')+(avisos.length?' Atenção: '+avisos.join('; ')+'.':'')}); }
function pltVals(self,v,saf,step,ro){ const P=self.state.plt; const lv0=(saf&&step===2&&!ro)?pltLivres(self,saf,''):[];
  v.plt_tem=lv0.length>0; v.plt_abrir=()=>pltAbrir(self,(sgSubs(self,saf).some(x=>x.faz===self.state.ffz)?self.state.ffz:'')||'');   // com o filtro de uma fazenda, só ela
  v.plt_open=!!P&&step===2; if(!v.plt_open) return;
  const so=safById(self,saf); const lv=pltLivres(self,saf,P.faz); const set=(o)=>self.setState({plt:Object.assign({},self.state.plt,o)});
  const subs=sgSubs(self,saf); const fzs=[...new Set(lv.map(x=>x.faz))]; const E=P.err||{};
  v.plt_titulo='Planejar talhões livres'; v.plt_sub=(so?so.v.nome:'')+' · '+(fzs.length>1?fzs.slice(0,-1).join(', ')+' e '+fzs[fzs.length-1]:(fzs[0]||safFaz(self,saf)))+'. Um cultivo por talhão, na área livre de cada um.';
  v.plt_grupos=fzs.map(f=>{ const its=lv.filter(x=>x.faz===f); return {cab:f+' · '+its.length+(its.length>1?' livres':' livre'),multi:fzs.length>1||subs.length>1,
    itens:its.map(x=>{ const pm=pltPmin(self,P,x); const er=E['t:'+x.t]||''; return {t:x.t,id:'plt-'+String(x.t).replace(/\W/g,''),on:!!P.sel[x.t],
      txt:nfa(x.L.area_livre)+' ha livres'+(x.L.own.length?' (o resto do talhão)':'')+' · plantio a partir de '+ocBr(pm)+(x.L.est?' (estimado)':''),err:er,hasErr:!!er,
      tog:()=>{ const s2=Object.assign({},self.state.plt.sel); s2[x.t]=!s2[x.t]; const e2=Object.assign({},self.state.plt.err||{}); delete e2['t:'+x.t]; set({sel:s2,err:e2}); }}; })}; });
  const n=lv.filter(x=>P.sel[x.t]).length; v.plt_n=n; v.plt_btn='Planejar '+n+(n===1?' talhão':' talhões'); v.plt_btnSt=n?'':'opacity:.5;cursor:not-allowed;';
  v.plt_todos=()=>{ const s2={}; lv.forEach(x=>{ s2[x.t]=true; }); set({sel:s2}); }; v.plt_nenhum=()=>set({sel:{}});
  v.plt_cults=(P.cult?[]:[{v:'',t:'Escolha a cultura'}]).concat(Object.keys(D2.culturas||{}).map(c=>({v:c,t:c}))); v.plt_cult=P.cult||'';
  v.plt_setCult=(e)=>{ const cu=e.target.value; const cs=cultsGrupo(self,saf).map(x=>x.c); set({cult:cu,var:maisUsado(cs.filter(c=>c.v.cult===cu),'var')||'',plano:maisUsado(cs.filter(c=>c.v.cult===cu&&planById(c.v.plano)),'plano')||'',err:{}}); };
  v.plt_var=P.var||''; v.plt_setVar=(e)=>set({var:e.target.value});
  v.plt_planos=planOpts({cult:P.cult,plano:P.plano}); v.plt_plano=P.plano||''; v.plt_setPlano=(e)=>set({plano:e.target.value});
  v.plt_plantio=pltData(self,P,lv); v.plt_setPlantio=(e)=>set({plantio:e.target.value,pt:true});
  v.plt_pminT=P.pt?'':'O primeiro dia em que todos os talhões marcados estão livres.';
  v.plt_meta=String(P.meta===undefined?'':P.meta); v.plt_setMeta=(e)=>set({meta:e.target.value}); v.plt_un=P.cult?metaRascunho(P.cult,'','')._un:'';
  ['cult','var','plantio','meta','plano'].forEach(k=>{ v['plt_e_'+k]=E[k]||''; v['plt_he_'+k]=!!E[k]; });
  v.plt_gerr=P.gerr||''; v.plt_hasg=!!P.gerr;
  v.plt_fechar=()=>self.setState({plt:null}); v.plt_salvar=()=>pltGravar(self);
  v.plt_key=(e)=>{ if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); self.setState({plt:null}); } }; }
function safOpenDraft(self,gid,r,d){ if(gid==='g_saf'&&r){ self.__sgCh='saf-form:'+r.id+':'+Date.now(); const G=sgGrupo(sgLista(self),r.id); return Object.assign({},d,{fazs:G?G.subs.map(x=>x.faz).join('; '):(r.v.faz||'')}); }
  if(String(gid).indexOf('g_cult_')!==0||!r||!r.v) return d; return Object.assign({},d,metaRascunho(r.v.cult,r.v.meta,r.v.unm)); }
/* UNID-PROD · seletor "Unidade de produtividade" da tabela de cultivos (D-U01): contexto = cultura do cultivo com o painel aberto; sem painel,
   a 1ª cultura visível com os filtros aplicados. Trocar a unidade muda a tabela, não o rascunho aberto (D-U20); nada vai para o estado da safra */
function safUnidOk(cu){ try{ prUn(cu); return true; }catch(e){ return false; } }
function safUnidVals(self,v){ const saf=self.state.saf; const ga=(saf&&(self.state.step||1)===2)?('g_cult_'+sk(saf)):'';
  GRIDS.filter(g=>String(g.id).indexOf('g_cult_')===0).forEach(g=>{ const px='us_'+g.id.slice(7); if(g.id!==ga){ unpVals(self,v,px,'',''); v[px+'_vis']=false; return; }
    const fm=g2st(self,g.id).fm; const rf=fm&&fm.rid?g2find(g2rows(self,g),fm.rid):null;
    const cu=(fm&&fm.draft&&fm.draft.cult)||(rf&&rf.v&&rf.v.cult)||unpCultVis(self,g.id,r=>(r&&r.v&&r.v.cult)?String(r.v.cult).split(', ')[0]:'');
    unpVals(self,v,px,(cu&&safUnidOk(cu))?cu:'',''); v[px+'_vis']=g2colsVis(self,g).some(c=>c.k==='meta'); }); }   // SAF-TAB: o seletor vale para a Meta; sem ela à vista, sai da barra
function dvRow(c){ return Object.assign({id:c.id||null,local:c.v.local||'',area:(c.v.area===''||c.v.area===undefined)?'':String(r2(c.v.area)).replace('.',','),cult:c.v.cult||'Soja',var:c.v.var||'',plantio:c.v.plantio||'',
  unm:unMetaDe(c.v.cult,c.v.unm),plano:c.v.plano||'',colheita:c.v.colheita||'',adj:null,from:'',decl:!!c.decl,ask:false},metaRascunho(c.v.cult||'Soja',c.v.meta,c.v.unm)); }
function dvDist(lst,T){ const n=lst.length; if(!n) return lst; const each=Math.floor(T*100/n)/100; return lst.map((x,i)=>Object.assign({},x,{area:String(i<n-1?each:r2(T-each*(n-1))).replace('.',',')})); }
function openDiv(self,t,extra){ const saf=self.state.saf; if(!saf){ self.setState({g2toast:'Escolha a safra primeiro.'}); return; }
  const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); const minhas=cultsDe(self,saf);   // R-22: só os cultivos desta safra (revisão SAF, S1)
  const cur=minhas.filter(c=>c.v.talhao===t); const ro=!!(safObj&&safObj.ro)||cur.some(c=>c.ro);
  // ciclo vinculado (R-24): área, plantio e cultura vêm do ciclo; dividir mudaria o que é do ciclo (revisão SAF, S3.2)
  if(!ro&&cur.some(c=>c.v.ciclo)){ self.setState({g2toast:'Ciclo perene vinculado: área, plantio e cultura vêm do ciclo; não se divide aqui.'}); return; }
  let lst=cur.map(dvRow); let base;
  const inteiro=(cur.length===1&&cur[0].v.tipo!=='Parcela');
  if(!ro&&inteiro&&!extra){ const em=faixasEmUso(self,saf,t,cur[0].id); const n1=nextNome(t,em), n2=nextNome(t,em.concat([n1]));
    lst[0].local=n1; lst.push(Object.assign({},lst[0],{id:null,local:n2,from:n1,decl:true,adj:copyAdj(self,cur[0].id)})); lst=dvDist(lst,dvCap(self,t,lst).cap); base=JSON.stringify(lst); }
  else { base=JSON.stringify(lst); if(extra){ if(inteiro) lst[0].local=t+'-A'; const e=dvRow(extra); e.id=null; e.decl=true;
      const usados=lst.map(x=>x.local).concat(faixasEmUso(self,saf,t,null)); if(!e.local||e.local===t||usados.indexOf(e.local)>=0) e.local=nextNome(t,usados); lst.push(e); } }
  self.setState({dv:{t,rows:lst,base,ro,err:{},gerr:'',warn:false}}); }
// campos de um cultivo na grade (Dividir e Editar talhões, EDL-01): cultura, variedade, plantio, meta e plano da mesma cultura
function dvCampos(x){ const e={}; const m=g2num(x.meta);
  if(!x.cult) e.cult='Escolha a cultura'; if(!String(x.var||'').trim()) e.var='Informe a variedade';
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(x.plantio||''))) e.plantio='Informe o plantio';
  if(String(x.meta).trim()===''||isNaN(m)||m<0) e.meta='Informe a meta (≥ 0)';
  const plx=planById(x.plano); if(plx&&plx.cultura!==x.cult) e.plano='Plano de '+plx.cultura+' não serve para '+x.cult+': escolha outro ou deixe sem plano';
  return e; }
// conferência da divisão de um talhão da safra aberta (SAF-C01): a mesma no Dividir e no Editar talhões (EDL-01). lst no formato do dvRow;
// adj0: ajustes de partida (o lote encadeia os talhões). Devolve {gerr, soG} (só o aviso), {err, gerr} (recusa) ou {kids, adj, livreD, all, daSaf}
function dvConferir(self,t,lst,adj0){ const T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf); const rows=g2rows(self,GR(gid));
  const daSaf=(c)=>sk(saf)!=='NOVA'||c.v.saf===saf;   // R-22: a g_cult_NOVA guarda as safras novas; só as linhas desta safra mudam (revisão SAF, S1)
  if(!lst.length) return {soG:true,gerr:'Mantenha pelo menos uma parcela. Para tirar o talhão da safra, exclua a linha dele na tabela.'};
  const outros=cultsDe(self,saf).filter(c=>c.v.talhao!==t); const err={}; let A=0; const nomes={};
  lst.forEach((x,i)=>{ const e={}; const nm=String(x.local||'').trim(); const a=g2num(x.area);
    if(!nm) e.local='Informe o nome da parcela'; else if(nomes[nm]||outros.some(c=>c.v.local===nm)) e.local='Nome '+nm+' repetido'; nomes[nm]=1;
    if(isNaN(a)||a<0.01) e.area='Informe a área (mínimo 0,01 ha)'; else A+=a;
    Object.assign(e,dvCampos(x));
    if(Object.keys(e).length) err[i]=e; });
  const exc=A>T+0.005;
  if(Object.keys(err).length||exc) return {err,gerr:(exc?('As parcelas somam '+nfa(A)+' ha; o talhão tem '+nfa(T)+' ha. Reduza '+nfa(A-T)+' ha.'):'Corrija os campos destacados; o que você digitou foi mantido.')};
  const all=g2clone(soDaSafra(rows)); const adj=JSON.parse(JSON.stringify(adj0||adjOf(self))); const old=leaves(all).filter(c=>c.v.talhao===t&&daSaf(c)); const byId={}; old.forEach(c=>{ byId[c.id]=c; });
  const stamp=String(Date.now()).slice(-6);
  const kids=lst.map((x,i)=>{ const b=(x.id&&byId[x.id])||null; const c=b||{id:'p'+t+'_'+stamp+'_'+i,v:{},s:{},p:{},decl:true};
    if(b&&String(b.v.plano||'')!==String(x.plano||'')) delete adj[b.id];
    const mg=metaGravar(x);   /* UNID-PROD: linha a linha, sem regravar a meta que não mudou (R-U06) */
    Object.assign(c.v,{talhao:t,faz:(b?b.v.faz:(old[0]?old[0].v.faz:safFaz(self,saf))),local:String(x.local).trim(),cult:x.cult,var:String(x.var).trim(),area:r2(g2num(x.area)),plantio:x.plantio,meta:mg.meta,unm:mg.unm,plano:x.plano||'',colheita:x.colheita||''});
    if(b&&b.v.tipo!=='Parcela') c.decl=true; if(sk(saf)==='NOVA') c.v.saf=saf; c.v.tipo='Parcela';
    c.s={}; c.p={}; if(!b&&x.adj&&Object.keys(x.adj).length) adj[c.id]=JSON.parse(JSON.stringify(x.adj)); return c; });
  let livreD=0;
  { const S=safList(self), ctx=ocCtxSaf(), todos=ocTodos(self); const faz=safFaz(self,saf); const ids=old.map(c=>c.id);
    const recs=kids.map(c=>{ const rr=ocCult(c,saf,faz); rr.tipo=(kids.length===1&&Math.abs(rr.area-T)<=0.005)?'Talhão inteiro':'Parcela'; if(rr.tipo==='Talhão inteiro') rr.faixa=t; return rr; });
    const depois=todos.filter(c=>ids.indexOf(c.id)<0).concat(recs); const er2={}; const area=[], pl=[];
    // a trava de área de cada parcela conta as irmãs como ocupação; a mensagem sai agregada, com a capacidade do painel (SAF-C01)
    recs.forEach((rr,i)=>{ const chk=ocChecar(ctx,S,todos,depois,saf,rr.id,T); if(!chk.o||!chk.trav.length) return; const ar=chk.trav.filter(x=>x[0]==='safra'||x[0]==='soma'), ou=chk.trav.filter(x=>ar.indexOf(x)<0);
      if(ar.length) area.push(i); if(ou.length){ pl.push(i); er2[i]={plantio:ocMsgTrava(ctx,Object.assign({},chk,{trav:ou}),saf,T,null)}; } });
    if(area.length||pl.length){ const D=dvCap(self,t,lst);
      const ta=area.length?((D.p?ocPeriodoTxt(D.g,D.p)+', '+nfa(D.pior)+' ha de '+t+' estão com '+ocQuemTxt(D.p)+'. ':'')+'As parcelas somam '+nfa(A)+' ha; o máximo é '+nfa(D.cap)+' ha nesse período. '):'';
      area.forEach(i=>{ er2[i]=Object.assign({},er2[i]||{},{area:'Reduza a área: as parcelas somam '+nfa(A)+' ha e o máximo é '+nfa(D.cap)+' ha.'}); });
      const tp=pl.length?(pl.length+(pl.length>1?' parcelas':' parcela')+' com ocupação certa no período. '):'';
      return {err:er2,gerr:'A divisão travaria a área: '+ta+tp+'Nada foi gravado.'}; }
    livreD=ocTabela(ctx,S[saf],ocOcupacoes(ctx,S,depois),[[t,T]],S)[0][0].area_livre; }
  const keep=kids.map(c=>c.id); old.forEach(c=>{ if(keep.indexOf(c.id)<0) delete adj[c.id]; });
  return {kids,adj,livreD,all,daSaf}; }
// troca as linhas do talhão pelo grupo com as parcelas conferidas, na mesma posição da lista (antes do normCult)
function dvAplicar(all,t,kids,saf,daSaf){ const isT=(r)=>r.v.talhao===t&&(r.grp?(r.kids||[]).some(daSaf):daSaf(r)); let pos=all.findIndex(isT); const rest=all.filter(r=>!isT(r)); if(pos<0) pos=rest.length;
  const gi=grpId(t,sk(saf)==='NOVA'?saf:''); rest.splice(pos,0,{id:gi,grp:true,dr:'div_'+t,ro:false,v:{talhao:t,faz:kids[0].v.faz,local:t},s:{},p:{},kids}); return {rest,gi}; }
function dvSave(self){ const dv=self.state.dv; if(!dv||dv.ro) return; const t=dv.t; const saf=self.state.saf; const gid='g_cult_'+sk(saf);
  const R=dvConferir(self,t,dv.rows,null);
  if(R.soG){ self.setState({dv:Object.assign({},dv,{gerr:R.gerr})}); return; }
  if(!R.kids){ self.setState({dv:Object.assign({},dv,{err:R.err,gerr:R.gerr,warn:false})}); return; }
  const {rest,gi}=dvAplicar(R.all,t,R.kids,saf,R.daSaf); const kids=R.kids, livreD=R.livreD, daSaf=R.daSaf;
  const norm=normCult(rest); const xa=Object.assign({},g2st(self,gid).x||{}); xa['fzg_'+saf]=true; xa[gi]=true; xa['grp_'+t]=true;   // TAB-12: a ação abre o caminho do talhão dividido
  g2set(self,gid,{rows:norm,x:xa,sel:{},fl:null});
  const inteiro=norm.some(r=>!r.grp&&r.v.talhao===t&&daSaf(r));
  self.setState({adj:R.adj,dv:null,g2toast:(inteiro?(t+' volta a talhão inteiro.'):(t+' dividido em '+kids.length+(kids.length>1?' parcelas':' parcela')+(livreD>0.005?(' · '+nfa(livreD)+' ha livres'):'')+'.'))+' Plano operacional, recursos e demanda recalculados.'}); }
function divVals(self,v){ const dv=self.state.dv; v.dv_open=!!dv; if(!dv){ v.dv_rows=[]; return; } const t=dv.t, T=talhaoArea(t); const saf=self.state.saf; const gid='g_cult_'+sk(saf);
  // capacidade pelo serviço (SAF-C01): com ocupação de fora no período das parcelas (perene, outra safra), o livre e o selo saem dela, não de T
  const lst=dv.rows; const A=lst.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const D=dv.ro?{cap:T,pior:0}:dvCap(self,t,lst); const L=D.cap-A; const exc=L< -0.005, ok=Math.abs(L)<=0.005;
  v.dv_titulo=dv.ro?('Parcelas de '+t):('Dividir '+t+' em parcelas'); v.dv_n=lst.length+(lst.length>1?' parcelas':' parcela');
  v.dv_resumo='Talhão '+nfa(T)+' ha'+(D.pior>0.005?' · outras safras '+nfa(D.pior)+' ha':'')+' · alocado '+nfa(A)+' ha · livre '+nfa(Math.max(0,L))+' ha';
  // o verde só sem recusa à vista: com erro pendente no painel, a área que fecha aparece como "0 ha livres" (amarelo), não como conferida
  const pend=!!dv.gerr||Object.keys(dv.err||{}).length>0, conf=ok&&!pend;
  v.dv_selo=exc?('Excede em '+nfa(-L)+' ha'):(conf?'Área conferida':(nfa(Math.max(0,L))+' ha livres'));
  const cc=exc?['#B42318','#FDE8E6']:(conf?['#1E7A4C','#E4F3E9']:['#8A5A00','#FFF4D6']);
  v.dv_selost='display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';';
  v.dv_ro=!!dv.ro; v.dv_edit=!dv.ro; const adj=adjOf(self);
  const CULT=Object.keys(D2.culturas||{}).length?Object.keys(D2.culturas):['Soja','Milho','Feijão','Café','Mamão Formosa'];
  const upd=(i,patch)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],patch); return Object.assign({},cur,{rows:rs}); };
  v.dv_rows=lst.map((x,i)=>{ const pl=planById(x.plano); const na=x.id?Object.keys(adj[x.id]||{}).length:Object.keys(x.adj||{}).length; const e=(dv.err||{})[i]||{};
    // mudar uma área muda a soma: a recusa agregada (em todas as parcelas e no aviso do painel) fica vencida e sai; o Salvar recalcula (revisão do lote SAF, S3)
    const AGR=/^(Reduza a área: as parcelas somam|A divisão travaria a área|As parcelas somam)/;
    const set=(f)=>(ev)=>{ const cur=self.state.dv; const rs=cur.rows.slice(); rs[i]=Object.assign({},rs[i],{[f]:ev.target.value}); const er={};
      Object.keys(cur.err||{}).forEach(k=>{ const o=Object.assign({},cur.err[k]); if(Number(k)===i) delete o[f]; if(f==='area'&&AGR.test(o.area||'')) delete o.area; if(Object.keys(o).length) er[k]=o; });
      const venc=f==='area'&&AGR.test(cur.gerr||'');
      self.setState({dv:Object.assign({},cur,{rows:rs,err:er,warn:false,gerr:(!Object.keys(er).length?'':(venc?'Corrija os campos destacados; o que você digitou foi mantido.':cur.gerr))})}); };
    const ist=(f,x2)=>'font-family:inherit;font-size:13px;padding:6px 8px;border-radius:8px;box-sizing:border-box;width:100%;min-width:0;color:#15201A;border:1px solid '+(e[f]?'#B42318':'#E4E9E5')+';background:'+(dv.ro?'#F4F6F3':'#FFFFFF')+';'+(x2||'');
    let pt; if(!pl) pt=''; else if(pl.cultura!==x.cult) pt='Plano de '+pl.cultura+': escolha um plano de '+x.cult; else pt=(na?na+(na>1?' ajustes deste talhão':' ajuste deste talhão'):'')+(x.from?((na?' · ':'')+'copiado de '+x.from):'');
    const lab=x.local||('parcela '+(i+1)); const errs=Object.keys(e).map(k=>e[k]);
    return {i,local:x.local,area:x.area,cult:x.cult,var:x.var,plantio:x.plantio,meta:x.meta,unm:metaUnTela(x),plano:pt,temNota:!!pt,pwarn:!!(pl&&pl.cultura!==x.cult),dis:!!dv.ro,lab,
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
    const usados=rs.map(x=>x.local).concat(faixasEmUso(self,saf,t,null));   // nem o nome de uma ocupação de fora que ainda ocupa o talhão
    const A2=rs.reduce((a,x)=>{ const n=g2num(x.area); return a+(isNaN(n)?0:n); },0); const livre=r2(dvCap(self,t,rs).cap-A2); const area=livre>0.005?String(livre).replace('.',','):'';
    const nw=last?Object.assign({},last,{id:null,local:nextNome(t,usados),area,from:last.local,decl:true,ask:false,adj:(last.id?copyAdj(self,last.id):(last.adj?JSON.parse(JSON.stringify(last.adj)):null))})
                 :Object.assign({id:null,local:nextNome(t,usados),area,cult:'Soja',var:'',plantio:'',unm:unMetaDe('Soja'),plano:'',colheita:'',adj:null,from:'',decl:true,ask:false},metaRascunho('Soja','',''));
    rs.push(nw); self.setState({dv:Object.assign({},cur,{rows:rs,warn:false,gerr:''})});
    // inserção repetitiva (UX-ACAO-UNICA-20261003 · DS-33): o foco vai ao nome da parcela nova, à vista e fora do rodapé do painel
    setTimeout(()=>{ try{ const ins=[...document.querySelectorAll('aside[role=dialog] input[aria-label^="Nome da parcela"]')]; const el=ins[ins.length-1]; if(el){ el.focus({preventScroll:true}); el.scrollIntoView({block:'nearest',inline:'nearest'}); } }catch(e){} },60); };
  v.dv_dist=()=>{ const cur=self.state.dv; self.setState({dv:Object.assign({},cur,{rows:dvDist(cur.rows,dvCap(self,t,cur.rows).cap),err:{},gerr:'',warn:false})}); };
  v.dv_gerr=dv.gerr||''; v.dv_hasg=!!dv.gerr; v.dv_warn=!!dv.warn;
  const clean=(l)=>JSON.stringify(l.map(x=>Object.assign({},x,{ask:false})));
  const dirty=()=>clean(self.state.dv.rows)!==clean(JSON.parse(self.state.dv.base));
  v.dv_close=()=>{ const cur=self.state.dv; if(cur&&!cur.ro&&dirty()){ self.setState({dv:Object.assign({},cur,{warn:true})}); return; } self.setState({dv:null}); };
  v.dv_discard=()=>self.setState({dv:null}); v.dv_keep=()=>self.setState({dv:Object.assign({},self.state.dv,{warn:false})});
  v.dv_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.dv_close(); } };
  v.dv_save=()=>dvSave(self); }
// próximo passo de uma safra (etapa 1): o que falta primeiro, com o verbo; encerrada só consulta
/* CONTROLE-02 F2 · impedimentos da publicação da referência técnica (mapa no PR #58, 6152055144). Só recusa o que já trava no Planejar
   safra: sobreposição de ocupação (R-14, ocupacao.js) e plano de outra cultura no cultivo. O resto vai à prévia como aviso: sem plano
   (fica fora da referência), "A conferir" (R-15, pendência que salva) e sugestões das análises (opcionais). Falta de recurso também não
   trava (AGENTS §4) e fica fora desta conta. Puro: lê o estado da tela e as mesmas funções da etapa 2, sem escrever cache nem grade. */
function safImpedimentosRef(self,saf,c){ const imp=[], av=[]; const S=safList(self); const safra=S[saf];
  if(!safra) return {impedimentos:['Safra '+saf+' não encontrada no planejamento.'],avisos:av};
  const cs=cultRows(self,saf);
  cs.forEach(r=>{ const pl=planById(r.v.plano); if(pl&&pl.cultura!==r.v.cult) imp.push(r.v.local+': plano de '+pl.cultura+' num cultivo de '+r.v.cult+'. Reaplique o plano na linha.'); });
  const ctx=ocCtxSaf(); const occ=ocOcupacoes(ctx,S,ocTodos(self)); const ls=ocTabela(ctx,safra,occ,talOrd(safra.faz),S)[0]||[];
  ls.filter(l=>l.sit==='Sobreposição').forEach(l=>imp.push('Sobreposição em '+l.t+': corrija em Talhões e cultivos antes de publicar.'));
  const sp=cs.filter(r=>!planById(r.v.plano)); if(sp.length) av.push(sp.length+(sp.length>1?' cultivos sem plano ficam':' cultivo sem plano fica')+' fora da referência ('+safLocs(sp)+').');
  const nc=ls.filter(l=>l.sit==='A conferir').length; if(nc) av.push(nc+(nc>1?' talhões a conferir':' talhão a conferir')+' (sucessão estimada): pendência, não impede.');
  const ns=sgN(self,saf); if(ns) av.push(ns+(ns>1?' sugestões das análises de solo não aplicadas':' sugestão da análise de solo não aplicada')+': opcional.');
  return {impedimentos:imp,avisos:av}; }
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
  return Object.keys(S).filter(id=>id!==saf&&!S[id].ro&&S[id].faz===me.faz).map(id=>({id,nome:S[id].nome,ini:S[id].ini,fim:S[id].fim,oc:ocorr(self,id,pools)})); }   // período: a etiqueta de cada uma sai dela (SAF-C02)
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
// carga fora da conta numa célula (SAF-C02), desta safra e de cada outra, com o motivo: a mesma etiqueta do capSaf
function e3Fora(g,c,outN){ const by={}, ord=[]; (g.fora||[]).forEach(f=>{ if(f.mi!==c.mi) return; const k=(f.sid||'')+'|'+f.cls; if(!by[k]){ by[k]={sid:f.sid,cls:f.cls,h:0}; ord.push(by[k]); } by[k].h+=f.h; });
  return ord.map(x=>(x.sid?(outN[x.sid]||x.sid):'desta safra')+' '+capH(x.h)+' h '+(x.cls==='antes'?'antes do início':'depois do fim')+(x.sid?' dela':'')).join('; '); }
function e3CelAria(g,c,outN){ let t=g.nome+', '+c.mes+': '+fmtOcup(c.ocup)+', '+capH(c.d)+' h de '+capH(c.cap)+' h';
  if(c.dOth>1e-4) t+=' (desta safra '+capH(c.dThis)+' h; '+Object.keys(g.oth).filter(o=>g.oth[o][c.mi]>1e-4).map(o=>(outN[o]||o)+' '+capH(g.oth[o][c.mi])+' h').join('; ')+')';
  const fo=e3Fora(g,c,outN); if(fo) t+=', fora da conta: '+fo;
  t+=', precisa de '+(c.nec<0?'horas':c.nec)+', tem '+nfa(g.un); if(c.ge) t+=', mais '+nfa(g.semH[c.mi])+' ha sem horas calculáveis'; return t; }
function e3Aperto(g){ const c=g.necMax; return c.nec<0?Infinity:c.nec/Math.max(g.un,1e-9); }
function etapa3(self,v,saf,ro){ const st=self.state; const S=safList(self); const me=S[saf]||{}; const E=capCalc(self,saf); const oc=E.oc, G=E.G;
  const outN={}; E.outras.forEach(o=>{ outN[o.id]=o.nome; });
  const cs=cultRows(self,saf), sp=semPlano(cs); const aPlano=cs.filter(c=>sp.indexOf(c)<0).reduce((a,c)=>a+(Number(c.v.area)||0),0);
  const cls={antes:0,fora:0,depois:0,cal:0}; oc.forEach(i=>{ cls[i.cls]++; });
  const ver=capVeredito(G,oc,{semPlano:sp.map(c=>({local:c.v.local,area:c.v.area})),aPlano,cls,ini:br(me.ini),fim:me.fim?br(me.fim):'',outras:outN,pend:oc.filter(i=>i.pend).length,
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
  v.v3_atalhos=at; v.v3_captog=()=>capTog(self); v.v3_capexp=g2seta(capAb).exp;   /* TAB-09: a seta da seção vem antes do nome; TAB-11: a seta única, que gira com o aria-expanded (engine.seta) */ v.v3_capab=capAb;
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
    const fo=e3Fora(g,c,outN); v.v3_filn=g.nome+' · '+c.mes; v.v3_filt=capH(c.d)+' h de '+capH(c.cap)+' h ('+fmtOcup(c.ocup)+')'+(oth.length?' · desta safra '+capH(c.dThis)+' h · '+oth.map(o=>(outN[o]||o)+' '+capH(g.oth[o][c.mi])+' h').join(' · '):'')+(fo?' · fora da conta: '+fo:'')
      +' · precisa de '+(c.nec<0?'horas':c.nec)+', tem '+nfa(g.un)+(c.ge?' · mais '+nfa(g.semH[c.mi])+' ha sem horas calculáveis':''); }
  else { v.v3_filn=''; v.v3_filt=''; }
  e3Op(self,saf,oc,G,capF);
}
// g_op: operação › atividade › talhão (› configuração, quando a atividade divide a área); 9 colunas, uma variável por coluna (§3.4)
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
  const custo=(its)=>its.every(i=>i.pend)?null:its.reduce((a,i)=>a+(Number(i.cop)||0),0);   // pendente sem custo: vazio, não R$ 0 (ausente ≠ zero)
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
    const cu=custo(its); r.v.custo=cu===null?'':cu; r.s.custo=cu===null?'':rs(cu); r.p.custo=cu===null?[{k:'mut',t:''}]:[{k:'txt',t:r.s.custo}];
    return r; };
  const itsDe={};   // operação → ocorrências na tela (Total da grade)
  const xf={};   // TAB-12: caminho do filtro de recurso × mês (capF); sem filtro, tudo nasce recolhido
  const rows=grupo(base).map(o=>{ const cm=comum[o.op]||{}; const id='op:'+o.op; const r=linha(id,o.op,o.its,'','op','ha-op'); itsDe[id]=o.its;
    r.p.nome=[{k:'b',t:o.op},{k:'mut',t:cm.nAtv+(cm.nAtv>1?' atividades':' atividade')}];
    const opConj=!!cm.conj&&!cm.divSo, opRend=opConj&&cm.rend!==null;
    r.v.conj=cm.divSo?cm.n+' conjuntos':(cm.conj||'varia'); r.s.conj=r.v.conj; r.p.conj=[{k:opConj?'txt':'mut',t:r.v.conj}];
    r.v.rend=opRend?cm.rend:''; r.s.rend=cm.divSo?'':(opRend?nf(cm.rend,2)+' ha/h':'varia'); r.p.rend=[{k:opRend?'txt':'mut',t:r.s.rend}];
    map[id]={t:'op',op:o.op,comum:opRend,leaf:cm.leaf};
    if(capF) xf[id]=true;
    r.kids=o.ordA.map(a=>{ const aid='at:'+o.op+'|'+a.nome; const cfs=a.its[0].cfs; const div=cfs.length>1;
      const rep=new Set(a.its.map(i=>i.c.id)).size<a.its.length; const ra=linha(aid,a.nome,a.its,r.v.sit,'at',rep?'ha-op':'ha');
      ra.p.nome=[{k:'txt',t:a.nome}];
      const vz=(f)=>{ ra.v[f]=''; ra.p[f]=[{k:'mut',t:''}]; ra.s[f]=''; };
      if(div){ ra.v.conj=cfs.length+' conjuntos'; ra.s.conj=ra.v.conj; ra.p.conj=[{k:'mut',t:ra.v.conj}]; vz('rend'); }
      else { const rr=rend(cfs[0].v.rend);
        if(opConj) vz('conj'); else { ra.v.conj=cfs[0].v.nome; ra.s.conj=ra.v.conj; ra.p.conj=[{k:'txt',t:ra.v.conj}]; }
        if(opRend) vz('rend'); else { ra.v.rend=rr===null?'':rr; ra.s.rend=rr===null?'sem rendimento':nf(rr,2)+' ha/h'; ra.p.rend=[{k:rr===null?'mut':'txt',t:ra.s.rend}]; } }
      map[aid]={t:'at',op:o.op,atv:a.nome,div,leaf:cfs[0]?cfs[0].id:null};
      if(capF) xf[aid]=true;
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
            const cx=x.custo===null||x.custo===undefined?null:Number(x.custo); rx.v.custo=cx===null?'':cx; rx.s.custo=cx===null?'':rs(cx); rx.p.custo=cx===null?[{k:'mut',t:''}]:[{k:'txt',t:rx.s.custo}];
            map[cid]={t:'cf',op:o.op,atv:a.nome,i,j,leaf:i.cfs[j]?i.cfs[j].id:null}; return rx; }); }
        return ro; });
      return ra; });
    return r; });
  const sp=GR('g_op'); sp.rows=rows;
  // a célula de Capacidade escolhida é um filtro da pessoa (capSel): abre o caminho até as ocorrências achadas, uma vez por escolha (xcap);
  // a seta recolhe depois e a próxima escolha abre de novo
  if(capF){ const ck=capF.rec+'|'+capF.mi+'|'+saf, so=g2st(self,'g_op'); if(so.xcap!==ck){ const all=Object.assign({},self.state.g2||{}); all.g_op=Object.assign({},all.g_op||{},{x:xf,xcap:ck}); self.state.g2=all; } }
  // Total (proprietário, 13/10/2026), sobre o recorte visível: ha-op e custo somados; R$/ha = custo ÷ hectares físicos (cada cultivo uma vez, a
  // conta do Resumo da safra), "parcial" com ocorrência pendente ou tarifa desconhecida, como lá. Horas: soma padrão da grade (segue o filtro de recurso).
  // Revisão Codex V58-TOTAL-FILTRO-01 (S2): com busca ou filtro, soma só o que passou no filtro (e3Partes), não a operação inteira.
  sp.totf=(c,topo,F)=>{ const ps=e3Partes(map,topo,F,itsDe); if(!ps.length) return '';
    const cop=ps.reduce((a,p)=>a+(Number(p.cop)||0),0);
    if(c.k==='area') return nfa(ps.reduce((a,p)=>a+(Number(p.area)||0),0))+' ha-op';
    if(c.k==='custo') return rs(cop);
    if(c.k==='rha'){ if(ps.some(p=>p.pend||!p.ok)) return 'parcial'; const v={}; const af=ps.reduce((a,p)=>{ if(v[p.c]) return a; v[p.c]=1; return a+(Number(p.area)||0); },0); return af>1e-9?rs(cop/af)+'/ha':''; }
    return undefined; };
  self.__opTot=sp.totf;   // testes (saf_totais_test T7), como o __opmap
  const c6=sp.cols.find(c=>c.k==='horas'); if(c6){ if(c6._l0===undefined) c6._l0=c6.l; c6.l=kF?('Horas de '+G[kF].nome):c6._l0; } }
// toque na célula ou no atalho: grava state.cap (recurso × mês desta safra) e filtra a g_op; tocar de novo limpa
function capSel(self,rid,mi){ const cur=self.state.cap; const saf=self.state.saf; const igual=!rid||(!!cur&&cur.rec===rid&&cur.mi===mi&&cur.saf===saf);
  const st=g2st(self,'g_op'); const f=Object.assign({},st.f||{}); delete f.horas; const pa={f,x:null,xcap:null}; if(st.so&&st.so.k==='horas') pa.so=null; g2set(self,'g_op',pa);
  self.setState({cap:igual?null:{rec:rid,mi,saf}});
  setTimeout(()=>{ try{ const e=document.getElementById(igual?'saf-v3-ver':'saf-cap-filtro'); if(e){ e.scrollIntoView({block:'nearest'}); if(!igual) e.focus({preventScroll:true}); } }catch(x){} },80); }
function capTog(self){ const ab=!self.state.capAberta; self.setState({capAberta:ab});
  if(ab) setTimeout(()=>{ try{ const e=document.getElementById('saf-cap'); if(e) e.scrollIntoView({block:'nearest'}); }catch(x){} },80); }
// g_op → formulário Rendimento (§4.1): operação com conjunto e rendimento comuns abre a 1ª atividade em uso com "Todas"; atividade de uma
// configuração e talhão abrem "Só esta atividade" (talhão com "Neste talhão"); configuração abre a própria folha ("Nesta configuração")
function abrirRend(self,rid){ const m=(self.__opmap||{})[rid]; const saf=self.state.saf; if(!m||!saf) return; const gid=rendGid(saf); const sp=GR(gid);
  const tog=()=>{ const st=g2st(self,'g_op'); const x=Object.assign({},st.x||{}); x[rid]=!x[rid]; g2set(self,'g_op',{x}); };
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
  const um=Number(r.v.un)===1; const base=r.v.nome+': '+nfa(r.v.un)+(gid==='g_recp_pes'?(um?' pessoa':' pessoas'):(um?' unidade':' unidades'))+', jornada de '+nfa(r.v.jornada)+' h.';
  self.setState({g2toast:base}); setTimeout(()=>{ self.setState({g2toast:base+e3Diff(self,antes,null)}); e3Foco(self,'g_cap_'+sk(saf),rid); },0); }
// painel "Resumo da safra" (§4.3): custo por cultura (operação + insumos do plano ÷ ha físico com plano), trabalho da safra e a conta
// hectares físicos: cada cultivo (talhão) conta uma vez, com qualquer número de passadas; fonte única do denominador do R$/ha (Resumo e Total da etapa 3)
// partes do Total da etapa 3 no recorte filtrado (revisão Codex V58-TOTAL-FILTRO-01): a ocorrência que casa com o filtro entra inteira; numa
// ocorrência repartida em conjuntos, só a parte do conjunto que casa; a operação ou a atividade que casa por si (ex.: busca "Colheita") entra
// inteira quando nada abaixo dela casa. Cada ocorrência e cada parte uma vez só (expandir/recolher não muda nada). Sem filtro: tudo.
function e3Partes(map,topo,F,itsDe){ const filt=!!(F&&F.filt), m=(r)=>!F||!F.match||F.match(r); const out=[], vistos=new Set();
  const inteira=(i)=>{ const k='oc:'+i.c.id+'|'+i.a.id+'|'+i.dt; if(vistos.has(k)) return; vistos.add(k); out.push({c:i.c.id,area:Number(i.area)||0,cop:Number(i.cop)||0,pend:!!i.pend,ok:!!i.rp.custoOk}); };
  const desce=(r)=>(r.kids||[]).some(k=>m(k)||desce(k));
  const walk=(r,todo)=>{ const M=map[r.id]||{};
    if(M.t==='oc'){ if(!filt||todo||m(r)) { inteira(M.i); return; }
      (r.kids||[]).filter(k=>m(k)).forEach(k=>{ const C=map[k.id]; if(!C) return; const x=(C.i.rp.itens||[])[C.j]; const kk='cf:'+k.id; if(!x||vistos.has(kk)) return; vistos.add(kk);
        out.push({c:C.i.c.id,area:Number(x.q)||0,cop:x.custo===null||x.custo===undefined?0:Number(x.custo),pend:!!C.i.pend,ok:x.custo!==null&&x.custo!==undefined}); }); return; }
    const so=filt&&!todo&&m(r)&&!desce(r);
    (r.kids||[]).forEach(k=>walk(k,todo||so)); };
  topo.forEach(r=>{ if(!r.kids) { (itsDe[r.id]||[]).forEach(inteira); return; } walk(r,!filt); });
  return out; }
function areaFisica(its){ const v={}; return its.reduce((a,i)=>{ if(v[i.c.id]) return a; v[i.c.id]=1; return a+(Number(i.area)||0); },0); }
function resumoCultura(oc,ini){ const by={}, ord=[];
  oc.forEach(i=>{ const cu=i.c.v.cult; let b=by[cu]; if(!b){ b=by[cu]={cult:cu,area:0,cop:0,cins:0,npend:0,ntar:0,copAntes:0,cinsAntes:0,its:[]}; ord.push(b); }
    b.its.push(i); b.cop+=Number(i.cop)||0; b.cins+=Number(i.cins)||0;
    if(i.pend) b.npend++; else if(!i.rp.custoOk) b.ntar++; if(ini&&i.dt<ini){ b.copAntes+=Number(i.cop)||0; b.cinsAntes+=Number(i.cins)||0; } });
  ord.forEach(b=>{ b.area=areaFisica(b.its); b.tot=b.cop+b.cins; b.rha=(b.npend||b.ntar)?null:(b.area?b.tot/b.area:null); }); return ord; }
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
  // CTL-4 (DEM-06): data antes de hoje não é "realizado" (RN-003); a etapa 4 troca a parte do plano já emitida em O.S. pelo que elas ainda tiram do estoque
  const Z=oc.filter(i=>i.dt&&i.dt>=D2.hoje).reduce((a,i)=>a+(Number(i.cins)||0),0); const Y=T('cins')-Z;
  v.rs_nota='Insumos do plano: dose × área × preço de todas as datas, antes do estoque. '+(Y>0.005?'Deles, '+rs(Y)+' têm data antes de hoje ('+br(D2.hoje)+') e '+rs(Z)+' de hoje em diante.'
    :'Todos de hoje em diante ('+br(D2.hoje)+').')+' A etapa 4 troca a parte já emitida em O.S. pelo que elas ainda vão tirar do estoque e calcula a necessidade líquida.';
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
// a versão nova da SOL que só baixou itens (DEM-09) não muda o número de complementos: o andamento gravado era da versão anterior e sai
// C-3/C-4 (PR #114): o andamento da Compra mora no cenário (compras.proc, cenCompLer/cenCompEstado); a chave antiga só vale até a migração
function solProcLimpar(saf){ try{ if(typeof cenCompLer==='function'){ const r=cenCompLer(saf); if(r&&r.proc) cenMudar(null,c=>{ delete cenCompEstado(c,true).proc[saf]; return {}; },{estrito:true}); return; }
  const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); if(o&&o.proc&&o.proc[saf]){ delete o.proc[saf]; localStorage.setItem(SOL_KEY,JSON.stringify(o)); } }catch(e){} }
function solProcDe(saf){ try{ if(typeof cenCompLer==='function'){ const r=cenCompLer(saf); return (r&&!r.erro&&r.proc)||null; }
  const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); return (o&&o.proc&&o.proc[saf])||null; }catch(e){ return null; } }
function solMap(self){ if(self.__solTmp) return self.__solTmp; if(self.state.sol) return self.state.sol; if(!self._sol0) self._sol0=Object.assign({},D2.sol,solLer()); return self._sol0; }
// andamento gravado pela Compra de insumos (cenário · compras.proc): o planejamento vê em que pé está a compra da mesma solicitação
function solEstado(saf,sol){ const p=solProcDe(saf);
  return (p&&sol&&p.sol===sol.id&&(p.comp||0)===(sol.comp||0)&&p.estado&&p.estado!=='A cotar')?p.estado:''; }
function solHref(saf,sol){ return 'CMP.dc.html#sol='+encodeURIComponent(sol.id)+'&saf='+encodeURIComponent(saf); }
// DEM-09 · pedido já emitido para esta solicitação: nada baixa. Vale o andamento da versão de agora ou o de uma anterior, guardado na versão nova
// (pedEmit): o complemento muda a versão e a Compra recomeça o andamento, mas o pedido emitido antes continua valendo (revisão do CTL-4, risco 1:
// sem isto, depois de um complemento a redução tirava da solicitação um insumo já comprado)
function solPedEmit(saf,sol){ return !!(sol&&(sol.pedEmit||/^Pedidos emitidos/.test(solEstado(saf,sol)))); }
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
    r.v.periodo=safPeriodo(r.v.ini,r.v.fim)||r.v.periodo||''; r.p.nome=[{k:'b',t:r.v.nome},{k:'mut',t:r.v.periodo}].concat(r.v.mae?[{k:'mut',t:g2rows(self,GR('g_saf')).filter(x=>x.v.mae===r.v.mae).length+' fazendas'}]:[]).concat(r.ro?[]:[{k:'act',t:'Editar',fn:'safedit:'+r.id,lk:true}]); r.s.nome=r.v.nome;
    const px=proxSaf(self,r); r._prox=px[1]; r.dr='open_'+r.id; r.drDup=true;   // o clique na linha repete o botão "Continuar" da linha: uma parada de Tab só (v3.1)
    r.p.acao=[{k:'act',t:px[0],fn:'pickat:'+r.id+'|'+px[1],u:false}]; r.s.acao=px[0]; });
  // ---- etapa 2: partes calculadas do cultivo (plano aplicado, ajustes) ----
  const adj=adjOf(self);
  ['S2627','S27SF','S2526','LG2627','NOVA'].forEach(k=>{ delete G2DISP['g_cult_'+k]; });
  self.__oc=(saf&&(st.step||1)===2)?syncTalhoes(self,saf,v):null; if(!self.__oc) self.__ocG=null;
  if(self.__xfn&&self.__xfn.sub===saf){ const f=self.__xfn.fn; self.__xfn=null; setTimeout(f,0); }   // SAF-FAZ-3: a ação pedida numa linha de outra fazenda, já na sub-safra dela (sgNaFazenda)
  // etapa 3: valores de partida (o bloco só aparece com safra e plano; os buracos existem sempre)
  Object.assign(v,{v3_ver:'',v3_vst:'',v3_cop:'',v3_copq:'',v3_atalhos:[],v3_capexp:'false',v3_capab:false,v3_fil:false,v3_filn:'',v3_filt:''});
  v.v3_captog=()=>capTog(self); v.v3_filx=()=>capSel(self,null,null);
  self.__e3=null;
  if(!saf) return;
  // ---- etapa 3: Dimensione operações e recursos (ESPECIFICACAO etapa-unica-3-4-5): veredito, capacidade por mês e operações ----
  // safra encerrada: recursos também só em consulta (PRD 52.1); a prévia mostraria 0 % enquanto salvar muda as safras abertas
  ['g_recp_maq','g_recp_pes'].forEach(g=>{ const sp=GR(g); if(sp) g2rows(self,sp).forEach(r=>{ r.ro=ro; }); });
  if((st.step||1)===3) etapa3(self,v,saf,ro);
  // ---- etapa 4: demanda de insumos ----
  const dm=demanda(self,saf); const sol=solMap(self)[saf]; const grupos={}; const est=sol?solEstado(saf,sol):''; const pedEmit=solPedEmit(saf,sol);
  const dmx=Object.assign({},dm); if(sol&&sol.itens) Object.keys(sol.itens).forEach(n=>{ if(!dmx[n]&&(Number(sol.itens[n])||0)>0.01) dmx[n]=demFora(self,saf,n,sol); });
  Object.values(dmx).forEach(d=>{ (grupos[d.grupo]||(grupos[d.grupo]=[])).push(d); });
  let tot=0, nliq=0, npend=0, nexc=0, ncomp=0, nqual=0, vqual=0;
  GR('g_dem').rows=Object.keys(grupos).sort((a,b)=>a.localeCompare(b,'pt-BR')).map((g,gi)=>{ const its=grupos[g].sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR'));
    const val=its.reduce((a,d)=>a+d.valor,0); tot+=val; const uso=its.map(d=>d.uso).filter(Boolean).sort()[0]||'';
    // TABELAS-FOCO (5983172395): uma variável por coluna — grupo, insumo, quantidades (com a unidade junto), datas, situação, solicitação e complemento próprios
    const gr={id:'G'+gi,v:{grp:g,ins:'',valor:val},s:{grp:g,ins:''},p:{grp:[{k:'b',t:g}],ins:[{k:'mut',t:its.length+(its.length>1?' insumos':' insumo')}]},
      kids:its.map((d,ix)=>{ const dec=(d.un==='L')?1:0; const sent=sol&&sol.itens?(sol.itens[d.nome]||0):0; if(d.liq>0) nliq++;
        // decisão do proprietário (05/10/2026): a unidade fica junto do valor ("62.500 kg"); o valor tipado (v) continua número para ordenar e filtrar
        const qt=(x)=>nf(x,dec)+' '+d.un, q=(x)=>[{k:'txt',t:qt(x)}], z=(x)=>x>0.001?[{k:'txt',t:qt(x)}]:[{k:'mut',t:'—'}];
        // situação pela regra única (DEM-09, cal01.js): a SOL que pede mais do que a demanda de agora fica "Acima da demanda · <diferença>"
        const ss=demSolSit(d,sent,!!sol,pedEmit); const exc=ss.t==='Acima da demanda'; const qual=ss.t==='Qualidade pendente'; const sid=ss.sol?sol.id:'';
        const sit={k:'chip',t:exc?ss.t+' · '+qt(ss.dif):(qual?ss.t+' · '+qt(d.cond):ss.t),c:ss.c};
        // falta condicionada à qualidade (revisão do 853a6a8, achado 2; PRD 65.4): visível com a decisão, fora do total e da primária
        const condCh=(!qual&&(d.cond||0)>0.001)?[{k:'chip',t:'Qualidade pendente · '+qt(d.cond),c:'yellow'}]:[]; if((d.cond||0)>0.001){ nqual++; vqual+=d.cond*d.preco; }
        if(ss.pend) npend++; if(exc) nexc++; else if(ss.pend) ncomp++;
        const memoSol=exc?[sol.id+' pede '+qt(sent)+'; a necessidade líquida agora é '+qt(d.liq)+': '+qt(ss.dif)+' acima da demanda.',
          pedEmit?'Pedido já emitido: a solicitação não muda e o excedente entra no estoque (cancelar o pedido é decisão da Compra).':'Atualize a solicitação para não comprar a mais.']:[];
        const kr={id:'G'+gi+'_'+ix,ro:true,v:{grp:d.grupo,ins:d.nome,bruta:d.bruta,real:(d.real>0.001?d.real:''),est:d.est,antes:(d.liq>0.001&&d.antes>0.001?d.antes:''),res:(!(d.liq>0.001&&d.antes>0.001)&&d.res>0.001?d.res:''),
               rec:d.rec,tarde:((d.liq>0.001||d.rup>0.001)&&d.tarde>0.001?d.tarde:''),liq:d.liq,un:d.un,preco:d.preco,valor:d.valor,sol:sid,comp:(sit.t==='Complemento'?d.liq-sent:'')},s:{sit:sit.t,sol:sid},
          p:{grp:[{k:'mut',t:d.grupo}],bruta:q(d.bruta),real:z(d.real),est:q(d.est),antes:z(d.liq>0.001?d.antes:0),res:z((d.liq>0.001&&d.antes>0.001)?0:d.res),rec:q(d.rec),
             tarde:z(((d.liq>0.001||d.rup>0.001)&&d.tarde>0.001)?d.tarde:0),liq:[{k:'b',t:qt(d.liq)}],sit:[sit],sol:sid?[{k:'txt',t:sid}]:[{k:'mut',t:'—'}],
             comp:sit.t==='Complemento'?q(d.liq-sent):[{k:'mut',t:'—'}],preco:[{k:'txt',t:rs(d.preco)+'/'+d.un}]},
          o:memoSol.concat(d.memo).map(t=>({t})).concat((d.cond||0)>0.001?[{t:'Decidir a qualidade no Estoque (o gestor libera ou reprova com o laudo)',h:'EST.dc.html'}]:[]).concat(sol?[{t:'Ver '+sol.id+' na Compra de insumos',h:solHref(saf,sol)}]:[]) }; dcol(kr,'uso',d.uso);
        if(condCh.length) kr.p.sit=kr.p.sit.concat(condCh);
        // filtro e busca leem o mesmo texto da célula (com a unidade)
        ['bruta','real','est','antes','res','rec','tarde','liq','comp','preco'].forEach(f=>{ const c=kr.p[f]&&kr.p[f][0]; kr.s[f]=(c&&c.t!=='—')?c.t:''; });
        // falta: quando o estoque acaba (com necessidade líquida ou só ruptura coberta por recebimento); coberta em: o recebimento que cobre a ruptura
        dcol(kr,'falta',(d.liq>0.001||d.rup>0.001)?d.falta:''); if(kr.s.falta) kr.p.falta=[{k:'cn',t:kr.s.falta,c:'red'}]; dcol(kr,'cob',(d.liq<=0.001&&d.rup>0.001)?d.cob:''); return kr; })};
    // situação do grupo: contagem por situação dos insumos (o que falta enviar primeiro)
    const cnt={}; gr.kids.forEach(k=>{ const t=String(k.s.sit||'').replace(/ · .*/,'').replace(/^Complemento.*/,'Complemento'); cnt[t]=(cnt[t]||0)+1; });
    const ord=['Acima da demanda','A enviar','Complemento','Em cotação','Qualidade pendente','Coberto pelo recebimento','Coberto pelo estoque']; const cor={'Acima da demanda':'red','A enviar':'gray','Complemento':'yellow','Em cotação':'blue','Qualidade pendente':'yellow','Coberto pelo recebimento':'yellow','Coberto pelo estoque':'green'};
    gr.p.sit=ord.filter(t=>cnt[t]).map(t=>({k:'chip',t:cnt[t]+' '+(t==='Coberto pelo estoque'?'coberto'+(cnt[t]>1?'s':''):(t==='Coberto pelo recebimento'?'coberto'+(cnt[t]>1?'s':'')+' pelo recebimento':t.toLowerCase())),c:cor[t]})); gr.s.sit='';
    ['bruta','real','est','antes','res','rec','tarde','liq','falta','cob','preco','sol','comp'].forEach(f=>{ gr.p[f]=[{k:'mut',t:''}]; gr.s[f]=''; });
    dcol(gr,'uso',uso); return gr; });
  v.k6='Valor da necessidade líquida '+rs(tot)+' · '+nliq+' insumos a comprar'+(sol?(' · solicitação '+sol.id+(est?' · '+est:' em cotação')+(sol.comp?' (+'+sol.comp+' complemento'+(sol.comp>1?'s':'')+')':'')):' · ainda não enviada')
    +(nexc?' · '+nexc+(nexc>1?' insumos':' insumo')+' acima da demanda':'')
    +(nqual?' · '+nqual+(nqual>1?' insumos':' insumo')+' com qualidade pendente ('+rs(vqual)+' condicionados ao laudo, fora da compra)':'');
  v.k6pend=npend; v.k6exc=nexc&&!pedEmit; v.k6comp=ncomp; v.sol_link=!!sol; v.sol_id=sol?sol.id:''; v.sol_href=sol?solHref(saf,sol):'CMP.dc.html';
}
function EXTRAVALS(self,v){ try{ window.__safSelf=self; self.__cultivos=(k)=>leaves(g2rows(self,GR('g_cult_'+k))).map(c=>[c.id,c.v.local,c.v.meta,c.v.unm]); }catch(e){}   // testes leem o estado (OC-13) e a meta gravada (UNID-PROD)
  const st=self.state; const step=st.step||1; const saf=st.saf||null;
  const safRows=g2rows(self,GR('g_saf')); const safObj=saf?safRows.find(r=>r.id===saf):null; const ro=!!(safObj&&safObj.ro);
  const temPlano=saf && cultRows(self,saf).some(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; });
  // SAF-FAZ-3: na etapa 2 a safra de várias fazendas conta as fazendas juntas (cultivos, sem plano, primária e cartões); 3 e 4 seguem por fazenda
  const subsG=saf?sgSubs(self,saf):[]; const multi=subsG.length>1; const csG=multi?[].concat(...subsG.map(x=>cultsDe(self,x.id))):(saf?cultRows(self,saf):[]);
  const temPlanoG=multi?subsG.some(x=>temPlanoDe(self,x.id)):temPlano;
  // 4 etapas (05/10/2026: as antigas 3, 4 e 5 viraram "Dimensione operações e recursos"); sem plano (R0) o bloco da etapa 3 não aparece
  for(let i=1;i<=4;i++) v['s'+i]=(step===i); v.s3=step===3&&!!temPlano;
  const whys={}; for(let i=2;i<=4;i++){ if(!saf) whys[i]='Escolha a safra'; else if(i>=3 && !temPlanoG) whys[i]='Aplique um plano'; }
  // cartões do fluxo (15/10/2026): o número da etapa e a frase curta (safras abertas e a escolhida; cultivos da safra e quantos sem plano)
  const csx=saf?csG:[]; const semP=csx.filter(c=>{ const pl=planById(c.v.plano); return !(pl&&pl.cultura===c.v.cult); }).length;
  const info={1:{cnt:safRows.length,sub:safObj?String((safObj.s&&safObj.s.nome)||safObj.v.nome||''):''},2:saf?{cnt:csx.length,sub:semP?semP+' sem plano':''}:{}};
  g2steps(self,v,'stp',4,step,whys,(i)=>{ if(whys[i]){ self.setState({g2toast:whys[i]}); return; } safIrEtapa(self,i); },info);   // cartão leva à etapa (15/10); avanço e retorno também na área de ações
  v.saf_nome=safObj?safObj.v.nome:'nenhuma safra escolhida'; v.saf_ro=ro; v.saf_ok=!!saf; v.saf_none=!saf;
  v.ctx_saf=safObj?(safObj.v.nome+(ro?' · consulta':'')):'Nenhuma safra escolhida';
  // a faixa diz a fazenda da safra aberta; sem safra, a fazenda escolhida nos chips da etapa 1 (ou todas): antes dizia sempre Santa Rita
  const fq=g2st(self,'g_saf').qv; v.ctx_faz=safObj?('Fazenda '+(safObj.v.faz||'Santa Rita')):(fq?'Fazenda '+fq:'Todas as fazendas');
  for(const k of ['S2627','S27SF','S2526','LG2627','NOVA']){ v['cult_'+k]=(saf&&sk(saf)===k); v['cap_'+k]=(saf&&sk(saf)===k); }
  const cs=(multi&&step===2)?csG:cultRows(self,saf); const area=cs.reduce((a,c)=>a+(Number(c.v.area)||0),0); const comp=cs.filter(c=>{ const pl=planById(c.v.plano); return pl&&pl.cultura===c.v.cult; }).length;
  const adj=adjOf(self); const naj=cs.reduce((a,c)=>a+Object.keys(adj[c.id]||{}).length,0);
  const sp=semPlano(cs);
  // faixa de resumo (§3.4): hectares por classe; os chips contam talhões pela Situação. Safra encerrada: consulta dos cultivos dela
  const oci=self.__oc; v.k2=(oci&&oci.band)?ocFaixaTxt(oci.bandG||oci.band,oci.linhasG||oci.linhas,oci.totG||talTot(oci.safra.faz)):(cs.length+' cultivos · '+nf(area)+' ha · '+comp+' com plano'+(sp.length?' · '+sp.length+' sem plano':'')+' · '+naj+(naj===1?' ajuste local':' ajustes locais'));
  // ação primária por etapa: nomeia o próximo passo (na etapa 2, o que falta: aplicar plano; depois, avançar)
  const cultSp={}; sp.forEach(c=>{ (cultSp[c.v.cult]||(cultSp[c.v.cult]=[])).push(c.id); }); const cuK=Object.keys(cultSp).sort((a,b)=>cultSp[b].length-cultSp[a].length)[0];
  const apIds=cuK?cultSp[cuK]:[]; const apT='Aplicar plano em '+apIds.length+(apIds.length>1?' cultivos':' cultivo')+(Object.keys(cultSp).length>1?' de '+cuK.toLowerCase():'');
  const solA=saf?solMap(self)[saf]:null; const enviado=!!solA;
  // com SOL enviada e insumo acima da demanda, a primária diz "Atualizar" também quando há complemento junto (ela baixa e sobe na mesma versão)
  const p6=(enviado&&!v.k6pend)?{t:'Abrir Compra de insumos ›',h:solHref(saf,solA),a:'abrir'}:((enviado&&v.k6exc)?{t:'Atualizar '+solA.id,fn:()=>enviar(self),a:'comando'}:{t:'Enviar para cotação',fn:()=>enviar(self),a:'comando'});
  v.sol_link=v.sol_link&&!p6.h;   // "Abrir em Compra de insumos ›" do bloco só quando a primária é enviar (complemento pendente): sem cópia do mesmo link
  { const G=saf?sgGrupo(sgLista(self),saf):null; v.sg_tem=!!(G&&G.mae)&&step>=3;   // SAF-FAZ-3: na etapa 2 as fazendas ficam juntas na tabela; 3 e 4 seguem por fazenda
    v.sg_fz=v.sg_tem?G.subs.map(s=>({t:s.faz,on:s.id===saf?'true':'false',al:s.id===saf?'Fazenda '+s.faz+', aberta':'Abrir a fazenda '+s.faz+' nesta etapa',
      go:()=>{ if(s.id===saf) return; g2etapa(self,{saf:s.id,step,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Fazenda '+s.faz+' · '+SAF_CURTO[step-1]}); }})):[];
    if(v.sg_tem){ const L=sgLeitura(G,sgInfo(self,G,false)); const nf2=(x)=>nf(x);
      v.sg_res=nf2(L.area.ha)+' ha'+(L.area.completa?'':' (falta área de '+L.area.faltam.join(', ')+')')+' · '+L.estados.map(e=>e.n+' '+(e.t==='Rascunho'?'em rascunho':String(e.t).toLowerCase())).join(' · ')+' · '+L.sol.enviadas+' de '+L.sol.de+' solicitações enviadas'; }
    v.sg_env=v.sg_tem&&step===4&&!ro; v.sg_envT='Enviar as '+(G?G.subs.length:0)+' fazendas para cotação'; v.sg_envGo=()=>sgEnviarTela(self,G); }
  safAcoes(self,v,{step,saf,ro,cs,sp,apIds,apT,cultSp,temPlano,p6});
  // escolher safra (botão da linha)
  v.pick=(id)=>{ g2etapa(self,{saf:id,step:2,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')}); };
  v.pickat=(arg)=>{ const a=String(arg).split('|'); const id=a[0], s=Number(a[1])||2; g2etapa(self,{saf:id,step:s,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Safra aberta: '+((safRows.find(r=>r.id===id)||{v:{}}).v.nome||'')+' · '+SAF_CURTO[s-1]}); };
  safRows.forEach(r=>{ v['open_'+r.id]=()=>v.pickat(r.id+'|'+(r._prox||2)); });
  v.safedit=(id)=>{ const sp=GR('g_saf'); const r=g2rows(self,sp).find(x=>x.id===id); if(!r) return; const dr=r.dr; r.dr=null; g2open(self,sp,id,null); r.dr=dr; };
  // SAF-FAZ-3: a ação da linha vale na sub-safra da fazenda do talhão (ou do cultivo); com uma fazenda só, é a de sempre
  v.applyone=(cid)=>sgPorCultivo(self,cid,()=>openApply(self,[cid])); v.openlp=(cid)=>sgPorCultivo(self,cid,()=>openLP(self,cid));
  Object.keys(D2.talhoes||{}).forEach(t=>{ v['div_'+t]=()=>sgPorTalhao(self,t,()=>openDiv(self,t)); }); v.divide=(t)=>sgPorTalhao(self,t,()=>openDiv(self,t));
  v.planejar=(t)=>sgPorTalhao(self,t,()=>abrirPlanejar(self,t)); v.vincular=(arg)=>{ const a=String(arg).split('|'); sgPorTalhao(self,a[0],()=>abrirVincular(self,a[0],a[1])); };
  v.semplantio=(t)=>sempMarcar(self,t,true); v.replanejar=(t)=>sempMarcar(self,t,false); v.pltfaz=(f)=>pltAbrir(self,f);
  sfzVals(self,v,saf,step,ro); ffzVals(self,v,saf,step); pltVals(self,v,saf,step,ro); slVals(self,v,saf,step,ro);   // EDL-01 · Editar talhões (safra_lote.js)
  v.abrirsaf=(arg)=>{ const a=String(arg).split('|'); abrirCultivo(self,a[0],a[1]||''); };
  // painéis
  apVals(self,v); lpVals(self,v); divVals(self,v); sgVals(self,v); pqSafVals(self,v);
  try{ window.__safRef={impedimentos:(saf)=>safImpedimentosRef(self,saf||self.state.saf,cenGet()),linhas:()=>sgLista(self),
    semPlantio:()=>JSON.parse(JSON.stringify(self.state.semp||{})),cultivos:(saf)=>cultsGrupo(self,saf||self.state.saf).map(x=>({saf:x.saf,id:x.c.id,talhao:x.c.v.talhao,faz:x.c.v.faz,local:x.c.v.local,cult:x.c.v.cult,var:x.c.v.var,area:x.c.v.area,plano:x.c.v.plano,plantio:x.c.v.plantio,meta:x.c.v.meta,unm:x.c.v.unm}))}; }catch(e){}   /* SAF-FAZ-3: testes leem as marcas e os cultivos do grupo */   /* adaptador do comando da F2 (PR #58) e teste */
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
// escolha é o "Trocar safra" desta mesma área, à esquerda: sem cópia). Pendência mostra a causa e um passo que resolve (Aplicar plano), sem aplicar e
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
  // TAB-12 (17/10/2026): a ação que leva a um registro abre o caminho dele: a faixa da fazenda e o talhão do 1º cultivo sem plano nascem
  // recolhidos, então abre o caminho (g2caminho) antes de pôr o foco na linha (achado da integração DRILL × acao_unica item 7)
  setTimeout(()=>{ try{ GRIDS.filter(g=>/^g_cult_/.test(g.id)).forEach(sp=>g2caminho(self,sp,ids[0])); }catch(e){}
    setTimeout(()=>{ try{ const row=document.querySelector('[role=row][data-rid="'+ids[0]+'"]'); if(row){ row.scrollIntoView({block:'center'}); row.focus({preventScroll:true}); } }catch(e){} },90); },120); }
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
      ps.push(l.t+': '+ocArt(y.cult)+' '+y.cult+' '+(y.safs.indexOf(saf)>=0?'desta safra':'da '+y.safnome)+' começa em '+ocBr(y.ini)+'; a saída '+ocDe(x.cult)+' '+ocMinus(x.cult)+' é estimada em '+(x.fim!==null?ocBr(x.fim):'sem data')+'.');   // SAF-TAB: sem a referência técnica
      out.lnks.push(lnkSaida(self,S,x,saf)); return; } }
    if(l.conf>0.005){ const e=l.fora.find(o=>o.classe==='estimado'||o.classe==='semdata'); if(e){
      ps.push(l.t+': '+ocHa(l.conf)+' ha a conferir a partir de '+ocBr(l.desde)+'; a saída '+ocDe(e.cult)+' '+ocMinus(e.cult)+' da '+e.safnome+' é estimada.');
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
function safAcoes(self,v,x){ const st=self.state, step=x.step, ro=x.ro, corr=st.corr||null;
  const ir=(i)=>({t:'‹ '+SAF_CURTO[i-1],fn:()=>g2etapa(self,{step:i,corr:null}),to:i,a:'voltar'});
  const av=(i,t)=>({t:t+' ›',fn:()=>safIrEtapa(self,i),to:i,a:'avancar'});   // SAF-FAZ-3: com várias fazendas, a etapa 3 abre numa fazenda que tem plano
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
    else { const L=(info&&(info.linhasG||info.linhas))||[]; const sob=L.find(l=>l.sit==='Sobreposição');   // SAF-FAZ-3: todas as fazendas da tabela
      // "Corrigir" abre o cultivo desta safra que está na trava mostrada (o mais tardio do par), não o 1º do talhão (revisão SAF, S3.4);
      // a nota descreve essa mesma trava, sem repetir o rótulo "Sobreposição" (S4)
      if(sob){ const ids=(y)=>[y[2]].concat(String(y[1]).split('+')); const tv=sob.trav.find(y=>ids(y).some(i=>sob.own.some(q=>q.id===i)))||sob.trav[0];
        const o=ids(tv).map(i=>sob.own.find(q=>q.id===i)).find(Boolean)||sob.own[0];
        c={nota:'Sobreposição em '+sob.t+': '+ocMotivo(Object.assign({},sob,{trav:[tv]}),info).replace(/^Sobreposição: /,'')+'.',prim:{t:'Corrigir '+sob.t,fn:()=>{ const sf=sob._saf||x.saf; sgNaFazenda(self,sf,()=>{ if(o) abrirCultivo(self,sf,o.id); else openDiv(self,sob.t); }); },a:'resolver'},sec:x.cs.length?av(3,'Dimensionar operações'):null}; }
      else if(!x.cs.length){ const nl=L.filter(l=>l.sit==='Livre'), nc=L.filter(l=>l.sit==='A conferir'), nv=L.reduce((a,l)=>a+l.vinc.length,0); const b=(info&&(info.bandG||info.band))||{};
        const sop=L.length&&L.every(l=>!l.planejar&&!l.vinc.length&&l.sit==='Perene');
        if(sop){ const o=L[0].fora.find(y=>y.classe==='perene'); const per=L.reduce((a,l)=>a+l.T,0);
          c={nota:'Todos os talhões estão com perenes da '+(o?o.safnome:'outra safra')+' neste período ('+ocHa(per)+' ha).',lnks:o?[{t:'Planeje por ela ›',fn:()=>abrirCultivo(self,o.saf,'')}]:[]}; }
        else { const ps=[]; if(nl.length) ps.push(nl.length+(nl.length>1?' talhões livres':' talhão livre')+' ('+ocHa(b.livre||0)+' ha)'); if(nc.length) ps.push(nc.length+' a conferir ('+ocHa(b.conf||0)+' ha)'); if(nv) ps.push(nv+(nv>1?' ciclos perenes a vincular':' ciclo perene a vincular'));
          c={nota:'Nenhum cultivo nesta safra'+(ps.length?': '+ps.join(', '):'')+'. Use Planejar ›'+(nv?' ou Vincular ciclo ›':'')+' na linha.'+(fr.t?' '+fr.t:''),lnks:fr.lnks}; } }
      // sem descrição na área de ações (proprietário, 15/10: "retire essas descrições"): o botão diz quantos cultivos recebem o plano, o que
      // pede conferência fica no ícone da linha e só o atalho que resolve fica aqui (ex.: "Informar colheita de P1 ›", próximo passo com verbo)
      else if(x.apIds.length) c={lnks:fr.lnks,prim:aplicar,sec:av(3,'Dimensionar operações')};
      else c={lnks:fr.lnks,prim:av(3,'Dimensionar operações')}; } }
  else if(!ro&&step===3&&!x.temPlano) c={volta:ir(2),nota:'Nenhum cultivo tem plano agronômico: operações, recursos e demanda dependem dele.',prim:x.apIds.length?aplicar:null};
  // etapa 3: cultivo sem plano vira só o atalho "Aplicar plano em N cultivos" (o veredito já diz o que ficou fora); falta de recurso é aviso,
  // não trava: planejar não reserva, não contrata e não compra (AGENTS §4)
  else if(step===3) c=Object.assign({volta:ir(2),prim:av(4,ro?'Ver demanda de insumos':'Conferir demanda de insumos')},(!ro&&x.apIds.length)?{lnks:[{t:x.apT,fn:()=>openApply(self,x.apIds)}]}:{});
  else if(step===4){ c={volta:ir(3)};
    if(!ro){ c.prim=x.p6; if(nSp){ c.nota=semTxt+' ficam fora desta demanda.'; c.ctx={t:'Corrigir cultivos',fn:()=>safCorrigir(self,x.sp.map(r=>r.id))}; } } }
  // 14/10/2026 (proprietário): "Trocar safra" sai da faixa do topo e fica aqui, nos botões do fluxo, à esquerda (etapas 2 a 4)
  if(step>1&&x.saf) c.troca={t:'‹ Trocar safra',fn:()=>g2etapa(self,{step:1,atv:null,rec:null,corr:null,cap:null,rsOpen:false,g2toast:'Escolha a safra.'})};
  g2acoes(v,'aa',c); }
function openApply(self,ids){ const saf=self.state.saf; if(!saf){ self.setState({g2toast:'Escolha a safra primeiro.'}); return; }
  const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); if(safObj&&safObj.ro){ self.setState({g2toast:'Safra encerrada: somente consulta.'}); return; }
  const all=g2rows(self,GR('g_cult_'+sk(saf)));
  const sel=[...new Set([].concat(...(ids||[]).map(id=>{ const r=g2find(all,id); return (r&&r.grp)?(r.kids||[]).map(k=>k.id):[id]; })))];
  if(!sel.length){ self.setState({g2toast:'Nenhum cultivo sem plano nesta safra.'}); return; }
  // sugestão: o plano mais usado pela mesma cultura nesta safra (a pessoa pode trocar)
  const cs=cultsGrupo(self,saf).map(x=>x.c); const cu=(cs.find(c=>c.id===sel[0])||{v:{}}).v.cult; const uso={};   // SAF-FAZ-3: todas as fazendas da safra
  cs.forEach(c=>{ const pl=planById(c.v.plano); if(pl&&pl.cultura===cu&&c.v.cult===cu) uso[c.v.plano]=(uso[c.v.plano]||0)+1; });
  const sug=Object.keys(uso).sort((a,b)=>uso[b]-uso[a])[0]||'';
  self.setState({ap:{ids:sel,plan:sug,confirm:false}}); }
function apVals(self,v){ const ap=self.state.ap; v.ap_open=!!ap; if(!ap) return; const saf=self.state.saf; const CG=cultsGrupo(self,saf); const safDe={}; CG.forEach(x=>{ safDe[x.c.id]=x.saf; });
  const rows=CG.map(x=>x.c).filter(r=>ap.ids.indexOf(r.id)>=0);   // SAF-FAZ-3: o lote vale para os cultivos de todas as fazendas da safra, cada um na sub-safra dele
  const culturas=[...new Set(rows.map(r=>r.v.cult))]; const av=apAvalia(self,saf,rows,ap.plan,safDe); const tv={}, pv={}; av.trava.forEach(x=>{ tv[x.r.id]=x.t; }); av.pend.forEach(x=>{ pv[x.r.id]=x.t; });
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
function apAvalia(self,saf,rows,pid,safDe){ const out={trava:[],pend:[]}; const S=safList(self); const so=S[saf]; if(!pid||!planById(pid)||!so||so.ro) return out;
  rows.forEach(r=>{ const s2=(safDe&&safDe[r.id]&&S[safDe[r.id]])?safDe[r.id]:saf; const rec=ocCult(r,s2,S[s2].faz); rec.plano=pid; const av=ocAvaliaCultivo(self,s2,rec); if(av.erro) out.trava.push({r,t:av.erro}); else if(av.pend) out.pend.push({r,t:av.pend}); }); return out; }
function doApply(self,rows,pid){ const saf=self.state.saf; const safDe={}; cultsGrupo(self,saf).forEach(x=>{ safDe[x.c.id]=x.saf; }); const adj=JSON.parse(JSON.stringify(adjOf(self)));
  const av=apAvalia(self,saf,rows,pid,safDe); const fora=av.trava.map(x=>x.r.id); const ok=rows.filter(r=>fora.indexOf(r.id)<0);
  // cada cultivo na grade da sub-safra dele; as grades mudam juntas, num setState só (SAF-FAZ-3)
  const g0='g_cult_'+sk(saf); const porG={[g0]:g2clone(soDaSafra(g2rows(self,GR(g0))))};
  ok.forEach(r=>{ const gid='g_cult_'+sk(safDe[r.id]||saf); if(!porG[gid]) porG[gid]=g2clone(soDaSafra(g2rows(self,GR(gid)))); const x=g2find(porG[gid],r.id); if(x){ x.v.plano=pid; x.v.colheita=''; delete adj[r.id]; } });
  const pl=planById(pid); const g2all=Object.assign({},self.state.g2||{}); Object.keys(porG).forEach(gid=>{ g2all[gid]=Object.assign({},g2all[gid]||{},{rows:porG[gid],sel:{}}); });
  const pend=av.pend.length?' Com pendência: '+av.pend.map(x=>x.t).join(' '):''; const tr=av.trava.length?' Não receberam ('+av.trava.length+'): '+av.trava.map(x=>x.r.v.local).join(', ')+'.':'';
  self.setState({g2:g2all,adj,ap:null,g2toast:pl.nome+' v'+pl.versao+' aplicado a '+ok.length+(ok.length>1?' cultivos':' cultivo')+'.'+pend+tr+' Plano operacional, recursos e demanda recalculados.'}); }
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
    go:()=>self.setState({g2toast:'Escolha e salve um plano agronômico de '+r.v.cult+' antes de ajustar os insumos.'})}].concat(cultDividir(self,gid,r));
  return [{t, h:(na?(na+(na>1?' ajustes deste talhão':' ajuste deste talhão')+' · '):'')+'Mude dose, retire ou inclua insumos só neste talhão; o plano padrão não muda.',
    go:()=>{ const cur=g2st(self,gid).fm; if(cur&&!cur.ro&&g2dirty(cur)){ self.setState({g2toast:'Salve ou descarte as alterações do cultivo antes de ajustar os insumos.'}); return; } g2set(self,gid,{fm:null}); openLP(self,r.id); }}].concat(cultDividir(self,gid,r)); }
// "Dividir" no painel do cultivo de talhão inteiro: no celular a linha não mostra a ação (g2sec), e o toque na linha chega aqui
function cultDividir(self,gid,r){ if(!r||r.ro||r.v.ciclo||r.v.tipo==='Parcela') return []; const t=r.v.talhao||r.v.local;
  return [{t:'Dividir '+t+' em parcelas', h:'Planta parte do talhão com outra cultura ou data; cada parcela tem o próprio plano.',
    go:()=>{ const cur=g2st(self,gid).fm; if(cur&&!cur.ro&&g2dirty(cur)){ self.setState({g2toast:'Salve ou descarte as alterações do cultivo antes de dividir o talhão.'}); return; } g2set(self,gid,{fm:null}); openDiv(self,t); }}]; }
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
  // TAB-12 (17/10/2026): grupos e atividades nascem recolhidos (nome, gatilho e data à vista); só o erro de gravação abre o caminho até o campo
  const temErr=(A)=>Object.keys(lp.err||{}).some(k=>lp.err[k]&&(k.indexOf(A+'|')===0||k==='pick'+A)); const abre=(k,e)=>ex[k]===true||(ex[k]!==false&&e);
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
      const atvs=grupos[g][key]; const gid=g+key; const open=abre(gid,atvs.some(a=>temErr(String(a.id))));
      return {t:key.split('||')[0], dt:br(dataAtv(c,atvs[0],pl)), open, exp:g2seta(open).exp, lab:g2seta(open,key.split('||')[0]).lab, tog:()=>{ const x=Object.assign({},self.state.lpx||{}); x[gid]=!open; self.setState({lpx:x}); },
        atvs:atvs.map(a=>{ const aid='a'+a.id; const ao=abre(aid,temErr(String(a.id))); const A=String(a.id); const rmMap=lp.rm||{}; const adds=((lp.add||{})[A])||[]; const SRC=lp.src||{};
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
          return (o=>Object.assign(o,lpAc(self,A,cat,pk,upd,ERR,c,o)))({t:a.nome, op:a.op, open:ao, exp:g2seta(ao).exp, lab:g2seta(ao,a.nome).lab, tog:()=>{ const x=Object.assign({},self.state.lpx||{}); x[aid]=!ao; self.setState({lpx:x}); },
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
// SAF-FAZ-2: o envio de cada sub-safra é este mesmo comando; com self.__envCap (envio das fazendas da safra) o resultado volta para quem chamou
// em vez de virar aviso, e a solicitação gravada fica em self.__solTmp até o fim do lote (o estado só recebe o conjunto inteiro)
function enviar(self,safArg){ const saf=safArg||self.state.saf; const cap=self.__envCap||null;
  const SET=(o)=>{ if(!cap){ self.setState(o); return; } if(o.sol) self.__solTmp=o.sol; if(o.g2toast) cap.msg=o.g2toast; }; const safObj=g2rows(self,GR('g_saf')).find(r=>r.id===saf); if(safObj&&safObj.ro){ SET({g2toast:'Safra encerrada: não gera solicitações.'}); return; }
  const dm=demanda(self,saf); const sols=Object.assign({},solMap(self)); const sol=sols[saf];
  const itens=Object.values(dm).filter(d=>d.liq>0.001);
  if(!itens.length&&!sol){ SET({g2toast:'Nada a cotar: o estoque e os recebimentos cobrem a demanda.'}); return; }   // com SOL enviada, a demanda que zerou ainda baixa a SOL (DEM-09)
  // revisão do CTL-4, achado 3: enviar, complementar ou baixar a solicitação é decisão de quem planeja (gestor ou agrônomo; padrão do CTL-3, cenExigeUm):
  // grava quem agiu (perfil de demonstração) e quando; sem o papel, recusa e nada muda (dano: compra reduzida ou aumentada em nome de quem não decidiu)
  const quem=(acao)=>{ try{ return cenExigeUm(g2perfil(),['gestor','agronomo'],acao); }catch(e){ SET({g2toast:String(e.message||e)}); return ''; } };
  // registro único da solicitação: o que a Compra de insumos mostra (mesmos itens, quantidades, valores e memória CAL-01)
  const det=Object.values(dm).map(d=>({nome:d.nome,grupo:d.grupo,un:d.un,preco:d.preco,bruta:d.bruta,est:d.est,cust:d.cust||0,custT:d.custT||[],quarC:d.quarC||0,quarRef:d.quarRef||[],cond:d.cond||0,condFalta:d.condFalta||'',res:d.res,rec:d.rec,liq:d.liq,valor:d.valor,falta:d.falta,uso:d.uso,quar:d.quar,evs:d.evs}));
  const EM='23/09/2026 11:05';   // horário do cenário de demonstração (a SOL-2026-07 inicial é de 10:40)
  const base={safra:saf,nome:safObj.v.nome,faz:safObj.v.faz||'Santa Rita',estado:'Enviada · a cotar',
    origem:{t:'Planejar safra · '+safObj.v.nome+' · demanda de insumos',h:'SAF.dc.html#saf='+encodeURIComponent(saf)+'&passo=demanda'},det,ent:dm._ent};
  const grava=(rec)=>{ const ok=solGravar(rec); return ok?'':' Atenção: este navegador não guarda dados; a Compra de insumos não verá a solicitação.'; };
  if(!sol){ const ids={S27SF:'SOL-2027-02',S2627:'SOL-2026-07',LG2627:'SOL-2026-09'}; const usados=Object.values(sols).map(x=>x.id); let id=ids[saf];
    for(let k=10;!id||usados.indexOf(id)>=0;k++) id='SOL-2026-'+k;
    const por=quem('Enviar a solicitação '+id); if(!por) return;
    const it={}; itens.forEach(d=>{ it[d.nome]=d.liq; }); const tot=itens.reduce((a,d)=>a+d.valor,0);
    sols[saf]=Object.assign({},base,{id,at:'23/09/2026',em:EM,por,itens:it,comp:0,total:tot});
    const av=grava(sols[saf]);
    SET({sol:sols,g2toast:'Solicitação '+id+' enviada a Compras: '+itens.length+' insumos, '+rs(tot)+'. Origem: '+safObj.v.nome+' · Planejar safra, demanda de insumos.'+av}); return; }
  // DEM-09 (cal01.js): sobe o que a demanda pede a mais (complemento) e baixa o que ela pede a menos; com pedido emitido nada baixa
  const pe=solPedEmit(saf,sol); const R=demSolRevisar(sol.itens,dm,pe);
  if(!R.novos.length&&!R.menos.length){ SET({g2toast:'Nada novo para cotar: tudo já está na '+sol.id+'. Nenhuma solicitação duplicada foi criada.'}); return; }
  const por=quem('Atualizar a '+sol.id); if(!por) return; const est0=solEstado(saf,sol); const agora='23/09/2026 '+cenAgora();
  const it=R.it; const comp=(sol.comp||0)+(R.novos.length?1:0);
  const pr=(n)=>{ const x=dm[n]||demFora(self,saf,n,sol); return {un:x.un,preco:Number(x.preco)||0,dec:x.un==='L'?1:0}; };
  const val=R.novos.reduce((a,n)=>a+(it[n]-(sol.itens[n]||0))*pr(n).preco,0);
  const dif=R.menos.map(n=>{ const x=pr(n), q=(sol.itens[n]||0)-(it[n]||0); return {n,q,v:q*x.preco,t:nf(q,x.dec)+' '+x.un,sai:!(it[n]>0)}; }); const valM=dif.reduce((a,x)=>a+x.v,0);
  // insumo que fica na solicitação sem estar na demanda (pedido emitido): a Compra lê grupo, unidade e preço do registro
  const detX=det.concat(Object.keys(it).filter(n=>!dm[n]).map(n=>{ const x=demFora(self,saf,n,sol); return {nome:n,grupo:x.grupo,un:x.un,preco:x.preco,bruta:0,est:x.est,res:0,rec:0,liq:0,valor:0,falta:'',uso:'',quar:0,evs:[]}; }));
  // versão nova: o envio original (por, em) fica; a atualização grava quem, quando e o que subiu ou baixou (a Compra mostra "atualizada em … por …")
  const txt=R.novos.map(n=>n+' +'+nf((it[n]||0)-(sol.itens[n]||0),pr(n).dec)+' '+pr(n).un).concat(dif.map(x=>x.n+' −'+x.t)).join('; ');
  const atu={por,em:agora,txt}; const hist=(sol.hist||[]).concat([Object.assign({v:(sol.hist||[]).length+2},atu)]);
  sols[saf]=Object.assign({},base,sol,{estado:'Enviada · a cotar',itens:it,comp,det:detX,total:Object.keys(it).reduce((a,n)=>a+it[n]*pr(n).preco,0),em:sol.em||(saf==='S2627'?'23/09/2026 10:40':EM),atu,hist,pedEmit:pe,ent:dm._ent});
  const av=grava(sols[saf]); if(R.menos.length&&!R.novos.length) solProcLimpar(saf);
  const tC=R.novos.length?'Complemento '+sol.id+'-C'+comp+' enviado com só a diferença: '+R.novos.length+' insumos, '+rs(val)+'. A solicitação original não foi duplicada.':'';
  const tM=dif.length?(sol.id+' atualizada: '+(dif.length===1?(dif[0].n+(dif[0].sai?' sai (':' baixa ')+dif[0].t+(dif[0].sai?' · ':' · −')+rs(dif[0].v)+(dif[0].sai?')':'')):
    (dif.length+' insumos a menos ('+dif.map(x=>x.n+' −'+x.t).join('; ')+') · −'+rs(valM)))+', porque a demanda de agora pede menos. A Compra de insumos cota a versão nova.'
    +((est0&&!R.novos.length)?' O andamento da compra da versão anterior ('+est0+') recomeça nesta versão.':'')):'';
  SET({sol:sols,g2toast:[tC,tM].filter(Boolean).join(' ')+' Atualizada por '+por+'.'+av}); }
// insumo que a solicitação pede e a demanda de agora não pede mais (DEM-09): linha própria, para a diferença não sumir da tela
function demFora(self,saf,n,sol){ const me=g2rows(self,GR('g_saf')).find(r=>r.id===saf); const faz=(me&&me.v.faz)||'Santa Rita';
  const k=((D2.osb||{}).cat||{})[n]||{}; const dt=((sol&&sol.det)||[]).find(x=>x.nome===n)||{};
  return {nome:n,grupo:dt.grupo||k.g||'—',un:dt.un||k.un||'',preco:Number(dt.preco||k.preco)||0,bruta:0,real:0,est:Number(cenEstDem(cenGet(),faz,D2.estb,[]).fisico[n])||0,antes:0,res:0,rec:0,tarde:0,
    liq:0,valor:0,rup:0,falta:'',cob:'',uso:'',quar:0,memo:['Nenhum uso do plano desta safra nem O.S. aberta pede '+n+' agora (a O.S. que pedia foi cancelada ou o plano mudou).']}; }
