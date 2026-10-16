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


{ const c=cenClone(CEN0); const base=JSON.stringify(c).length; const r0=JSON.stringify(c.recibos||{}).length;
  const p=cenGrupoPrevia(c,DS,'Caio'); const g=cenGrupoCriar(c,p,'Caio','k1').grupo; const a1=JSON.stringify(c.recibos).length;
  const pv=cenGrupoPrevia(c,DS,'Caio',g,plano()); cenGrupoProgramar(c,g,1,pv,'Caio','k2'); const a2=JSON.stringify(c.recibos).length;
  DS.forEach(id=>osc_aprovar(c,id,'Ana')); cenGrupoLiberar(c,g,DS,2,snap(c,DS),'Ana','k3'); const a3=JSON.stringify(c.recibos).length;
  out('R tamanho do cenário inicial (bytes JSON)', base); out('R recibos: antes/criar/programar/liberar', [r0,a1,a2,a3]);
  out('R maior recibo', Object.entries(c.recibos).map(([k,v])=>[k,JSON.stringify(v).length]).sort((x,y)=>y[1]-x[1]).slice(0,5)); }
`,ctx);
