/* Sonda de revisão (Claude) · dados sintéticos · carrega o núcleo real gerado (mesmo carregador do os_lote_unit.js). Uso: node sonda_lote.js <gen37> */
const vm=require('node:vm'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const dir=process.argv[2],data=new Map();
const runtime=JSON.parse(execFileSync('python3',['-c',`
import json
from pathlib import Path
import cenario
from areas import processo_os as P
s=P.JS;a=s.index('// OS-LOTE: mesma coleção');b=s.index('function EXTRAVALS(self,v){',a)
osd='const OSD='+json.dumps(dict(ords=P._ordens(),nova=dict(emb={})),ensure_ascii=False)+';\\n'
print(json.dumps(dict(prefix=Path('g2lib.js').read_text()+cenario.js_prefixo()+osd+P.JS_NUCLEO,ui=s[a:b])))
`],{cwd:dir,env:{...process.env,SAFRION_DADOS:'sintetico',PYTHONDONTWRITEBYTECODE:'1'},encoding:'utf8',maxBuffer:8*1024*1024}));
const ctx=vm.createContext({console,Date,setTimeout:()=>{},clearTimeout:()=>{},URLSearchParams,
 localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)}});
vm.runInContext(runtime.prefix,ctx);vm.runInContext(runtime.ui,ctx);
ctx.assert=assert;
vm.runInContext(String.raw`
const out=(n,v)=>console.log(n+' => '+(typeof v==='string'?v:JSON.stringify(v)));
const T=f=>{try{return {ok:f()}}catch(e){return {erro:String(e.message||e)}}};
const DS=['OS-0590','OS-0591','OS-0592'];
const plano=()=>({maquina:'T03',implemento:'PJ',operador:'MAR',caldeiro:'PAU',inicio:'2026-09-29T08:00:00-03:00'});
const snap=(c,ids)=>Object.fromEntries(ids.map(id=>[id,cenGrupoSnapshot(c,id)]));
function grupo(c,prog){ const p=cenGrupoPrevia(c,DS,'Caio',undefined,prog?plano():null); const r=cenGrupoCriar(c,p,'Caio','g-'+Math.random()); return r.grupo; }

// S1: Ana (AL-01+AL-02) libera grupo sem nenhuma aprovação: nenhuma liberada, nenhum CMD-42
{ const c=cenClone(CEN0), g=grupo(c,true); const r=T(()=>cenGrupoLiberar(c,g,DS,1,snap(c,DS),'Ana','lib1'));
  out('S1 sem aprovação: estados', r.ok?r.ok.itens.map(x=>x.os+':'+x.estado+':'+(x.motivo||'')):r);
  out('S1 CMD-42 criados', DS.map(id=>((c.ordens[id].osc||{}).ev||[]).filter(e=>e.cmd==='CMD-42').length));
  out('S1 etapas', DS.map(id=>c.ordens[id].etapa)); }
// S1b: aprovação de outra versão (v1 aprovada, ordem v2) não vale
{ const c=cenClone(CEN0), g=grupo(c,true); osc_aprovar(c,DS[0],'Ana'); c.ordens[DS[0]].versao='v2'; const r=T(()=>cenGrupoLiberar(c,g,[DS[0]],1,snap(c,[DS[0]]),'Ana','lib1b'));
  out('S1b aprovação v1 com ordem v2', r.ok?r.ok.itens:r); out('S1b etapa', c.ordens[DS[0]].etapa); }
// S1c: Caio (PCP) tenta liberar
{ const c=cenClone(CEN0), g=grupo(c,true); osc_aprovar(c,DS[0],'Ana'); out('S1c Caio libera', T(()=>cenGrupoLiberar(c,g,[DS[0]],1,snap(c,[DS[0]]),'Caio','lib1c'))); }
// S1d: Marcos (operador) tenta compor e liberar
{ const c=cenClone(CEN0); out('S1d Marcos compõe', T(()=>cenGrupoPrevia(c,DS,'Marcos'))); }
// S1e: aprovação com perfil duplo grava só CMD-06 na liberação (CMD-42 anterior preservado, sem novo CMD-42)
{ const c=cenClone(CEN0), g=grupo(c,true); osc_aprovar(c,DS[0],'Ana'); const r=cenGrupoLiberar(c,g,[DS[0]],1,snap(c,[DS[0]]),'Ana','lib1e');
  out('S1e itens', r.itens); out('S1e eventos', (c.ordens[DS[0]].osc.ev||[]).map(e=>e.cmd+' '+e.v)); }

// S2: origem ajustada por fluxo existente (osc_ajustar lib=false → v2) dentro do grupo: liberar e separar
{ const c=cenClone(CEN0), g=grupo(c,true); const a=T(()=>osc_ajustar(c,DS[1],c.ordens[DS[1]].area,{'Sulfato de magnésio':2.5},'',[],[],false,'Ana'));
  out('S2 ajuste aceito em origem agrupada', a.erro||('versão '+c.ordens[DS[1]].versao));
  osc_aprovar(c,DS[1],'Ana');
  const l=T(()=>cenGrupoLiberar(c,g,[DS[1]],1,snap(c,[DS[1]]),'Ana','lib2')); out('S2 liberar pelo grupo', l.ok?l.ok.itens:l);
  const s=T(()=>cenGrupoSeparar(c,g,DS[1],1,snap(c,c.gruposExec[g].ids),'Caio','sep2')); out('S2 separar a origem alterada', s);
  const s2=T(()=>cenGrupoSeparar(c,g,DS[0],1,snap(c,c.gruposExec[g].ids),'Caio','sep2b')); out('S2 separar outra origem', s2);
  const pr=T(()=>cenGrupoPrevia(c,c.gruposExec[g].ids,'Caio',g,plano())); out('S2 reprogramar grupo', pr.erro||'ok');
  // a liberação individual da O.S. alterada continua possível pela O.S.?
  out('S2 liberar pela O.S. (fluxo existente)', T(()=>osc_liberar(c,DS[1],false,'','Ana').msg)); }
// S3: origem cancelada (CMD-46) dentro do grupo: separar e reprogramar
{ const c=cenClone(CEN0), g=grupo(c,false); const k=T(()=>osc_cancelar(c,DS[2],'Teste de revisão','Ana')); out('S3 cancelar', k.erro||c.ordens[DS[2]].etapa);
  out('S3 separar cancelada', T(()=>cenGrupoSeparar(c,g,DS[2],1,snap(c,DS),'Caio','sep3')));
  out('S3 separar outra', T(()=>cenGrupoSeparar(c,g,DS[0],1,snap(c,DS),'Caio','sep3b')));
  out('S3 programar grupo', T(()=>cenGrupoPrevia(c,DS,'Caio',g,plano())).erro||'ok'); }
// S4: resíduo de ponto flutuante nas cargas
for(const areas of [[10.1,15.3,4.7],[0.1,0.2,0.3],[7.3,8.9,12.35]]){ const c=cenClone(CEN0); DS.forEach((id,i)=>{c.ordens[id].area=areas[i];c.ordens[id].saldo=areas[i];c.ordens[id].ins[0].tot=cenQtd(2,areas[i]);c.ordens[id].loteFicha.tanqueUtil=2000;});
  const p=cenGrupoPrevia(c,DS,'Caio'); out('S4 cargas '+areas, p.cargas.map(x=>x.vol+'L:'+x.destinos.map(d=>d.os.slice(-2)+'='+d.area).join('/')));
  out('S4 quantidade '+areas, p.produtos.map(x=>x.q+' '+x.un+' vs cenQtd '+cenQtd(x.dose,p.area))); }
// S5: borda da janela com horas fracionárias (3 × 10 ha a 3 ha/h = 10 h, janela 08–18)
{ const c=cenClone(CEN0); DS.forEach(id=>{const f=c.ordens[id].loteFicha;c.ordens[id].area=10;c.ordens[id].saldo=10;c.ordens[id].ins[0].tot=20;f.capacidadeHaH=3;f.deslocamentoH=0;f.setupH=0;});
  const p=T(()=>cenGrupoPrevia(c,DS,'Caio',undefined,plano())); out('S5 cabe exatamente', p.erro||('ok horas='+p.ok.horas+' pend='+p.ok.pendencias.join('|'))); }
// S6: meia-noite e fuso: início 22:00 UTC−3 recusado; início com fuso diferente do da janela
{ const c=cenClone(CEN0); DS.forEach(id=>c.ordens[id].loteFicha.janela=['2026-09-29T08:00:00-03:00','2026-09-30T18:00:00-03:00']);
  const p=plano(); p.inicio='2026-09-29T20:00:00-03:00'; out('S6 cruza meia-noite', T(()=>cenGrupoPrevia(c,DS,'Caio',undefined,p)).erro||'ok');
  const q=plano(); q.inicio='2026-09-29T08:00-04:00'; const r=T(()=>cenGrupoPrevia(cenClone(CEN0),DS,'Caio',undefined,q)); out('S6 fuso −4 na janela −3', r.erro||Object.values(r.ok.programacao).map(x=>x.blocos[0].dia+' '+x.blocos[0].ini+'-'+x.blocos[0].fim+' '+x.fuso)); }
// S7: habilitação: pessoa sem mapeamento (João irrigante como operador não aparece; Carlos sem pulverizador)
{ const p=plano(); p.operador='CAR'; out('S7 Carlos', T(()=>cenGrupoPrevia(cenClone(CEN0),DS,'Caio',undefined,p)).erro);
  const q=plano(); q.caldeiro='MAR'; q.operador='CAR'; out('S7 Marcos como caldeiro', T(()=>cenGrupoPrevia(cenClone(CEN0),DS,'Caio',undefined,q)).erro);
  out('S7 mapa de pessoas', Object.fromEntries(Object.entries(AL0.pessoas).map(([r,v])=>[r,v.nome+'|'+v.hab+'|v31='+v.v31]))); }
// S8: trator abaixo do PREQ e implemento sem PREQ
{ const p=plano(); p.maquina='T04'; out('S8 T04+PJ', T(()=>cenGrupoPrevia(cenClone(CEN0),DS,'Caio',undefined,p)).erro);
  out('S8 potências', Object.fromEntries(['T1','T02','T03','T04'].map(r=>[r,(AL0.ativos[AL0.ativo[r]]||{}).pot])), 'preq', AL0.preq); }
// S9: conflito com trabalho fora do lote (bloco existente de T03 no dia) e manutenção
{ const c=cenClone(CEN0); const A=alVigente(c).filter(x=>x.r==='T03'||x.r==='PJ'||x.r==='MAR'||x.r==='PAU'); out('S9 blocos vigentes desses recursos', A.map(x=>x.r+' '+x.os+' '+x.dia+' '+x.ini+'-'+x.fim+' '+x.sit)); }
`,ctx);
