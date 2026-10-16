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


// S3 (corrigido: assinatura osc_cancelar(c,id,mot,cx,ator)): origem cancelada (CMD-46) dentro do grupo
{ const c=cenClone(CEN0), g=grupo(c,false); const k=T(()=>osc_cancelar(c,DS[2],'Teste de revisão','','Ana')); out('S3 cancelar', k.erro||c.ordens[DS[2]].etapa);
  out('S3 separar cancelada', T(()=>cenGrupoSeparar(c,g,DS[2],1,snap(c,DS),'Caio','sep3')));
  out('S3 separar outra', T(()=>cenGrupoSeparar(c,g,DS[0],1,snap(c,DS),'Caio','sep3b')));
  out('S3 programar grupo', T(()=>cenGrupoPrevia(c,DS,'Caio',g,plano())).erro||'ok');
  out('S3 linhas do grupo', c.gruposExec[g].ids); }
// S4b: prévia × demanda das origens (regra única cenQtd por O.S.)
{ const c=cenClone(CEN0); const areas=[10.03,15.03,5.03]; DS.forEach((id,i)=>{const o=c.ordens[id];o.area=areas[i];o.saldo=areas[i];o.ins[0].dose=0.15;o.ins[0].tot=cenQtd(0.15,areas[i]);});
  const p=cenGrupoPrevia(c,DS,'Caio'); const dem=DS.reduce((s,id)=>s+c.ordens[id].ins[0].tot,0);
  out('S4b prévia q (bruto)', p.produtos[0].q); out('S4b prévia exibida nf', nf(p.produtos[0].q)+' '+p.produtos[0].un); out('S4b soma das demandas (tot por O.S.)', DS.map(id=>c.ordens[id].ins[0].tot).join(' + ')+' = '+cenNum(dem)); }
// S6b: fuso escolhido diferente do da fazenda esconde conflito real com bloco existente (horas locais sem fuso no AL0)
{ const c=cenClone(CEN0); DS.forEach(id=>c.ordens[id].loteFicha.janela=['2026-09-29T06:00:00-03:00','2026-09-29T20:00:00-03:00']);
  AL0.aloc.push({r:'T03',os:'OS-0415',dia:'2026-09-29',ini:16,fim:19,h:3,sit:'firme'});
  try{ const a=plano(); a.inicio='2026-09-29T11:00:00-03:00'; out('S6b −03:00 (11:00 local)', T(()=>cenGrupoPrevia(cenClone(c),DS,'Caio',undefined,a)).erro||'aceita');
       const b=plano(); b.inicio='2026-09-29T09:00:00-05:00'; const r=T(()=>cenGrupoPrevia(cenClone(c),DS,'Caio',undefined,b)); out('S6b −05:00 (mesmo instante, 11:00 local)', r.erro||('aceita · blocos '+Object.values(r.ok.programacao).map(x=>x.blocos[0].ini+'–'+x.blocos[0].fim+' '+x.fuso).join(', ')));
  } finally { AL0.aloc.pop(); } }
`,ctx);
