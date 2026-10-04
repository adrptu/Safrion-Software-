// carrega o bloco REPARTIR de <raiz>/tools/prototipo/v37/gen37/safra.js; instr=true acrescenta só registro (resultado e passos de cada
// chamada do buraco, e as decisões linhaBip/forçado das cópias de proposta), sem mudar a lógica
const fs=require('fs');
function troca(b,a,c){ const n=b.split(a).length-1; if(n!==1) throw new Error('âncora '+n+'x: '+a.slice(0,60)); return b.replace(a,()=>c); }
function carrega(raiz,instr){ let b=fs.readFileSync(raiz+'/tools/prototipo/v37/gen37/safra.js','utf8').match(/\/\/ >>> REPARTIR[\s\S]*?\/\/ <<< REPARTIR/)[0];
  if(instr){
    b=troca(b,"for(const v0 of cs){ const r=ext([v0],v0); if(r!==false) return r; } return false; };",
      "for(const v0 of cs){ const r=ext([v0],v0); if(r!==false){ globalThis.__BL.push([globalThis.__PF,cs.length,r,passos]); return r; } } globalThis.__BL.push([globalThis.__PF,cs.length,false,passos]); return false; };");
    b=troca(b,"const grafo=(V,pref,S)=>{ const n=V.length;","const grafo=(V,pref,S)=>{ const n=V.length; globalThis.__PF=pref;");
    if(b.indexOf("const lb=linhaBip(cf0,adj,V);")>=0) b=troca(b,"const lb=linhaBip(cf0,adj,V);","const lb=linhaBip(cf0,adj,V); if(lb) globalThis.__BL.push([globalThis.__PF,cf0.length,'linhaBip',0]);");
    if(b.indexOf("let h=false;   /* MEDIÇÃO")>=0) b=troca(b,"let h=false;   /* MEDIÇÃO","globalThis.__BL.push([globalThis.__PF,comp.length,'forçado',0]); let h=false;   /* MEDIÇÃO");
  }
  return new Function(b+'\nreturn repartir;')(); }
function caminho(m){ const est=m.some(x=>x.indexOf('combinações demais para conferir quem trabalha ao mesmo tempo')>=0), ci=m.some(x=>x.indexOf('máquinas compartilhadas em ciclo')>=0);
  return est?(ci?'conservador (estouro e ciclo)':'conservador (estouro do teto)'):(ci?'conservador (ciclo ímpar)':'cliques'); }
function resumo(r){ return {alocado:r.alocado,saldo:r.saldo,deficit:r.deficit,conflito:r.conflito,pendente:r.pendente,decorrido:r.decorrido,hconj:r.hconj,
  q:r.itens.map(x=>x.q),h:r.itens.map(x=>x.h),motivos:r.motivos,caminho:caminho(r.motivos)}; }
module.exports={carrega,caminho,resumo};
