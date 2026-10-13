// Armazenamento dos cadastros no protótipo (no software real, o servidor): uma chave e uma leitura para todas as telas que a usam.
// Guarda o custo-hora dos ativos salvo no CD-03 (X-CAD-1, por id do ativo) e as sementes criadas no CD-02, que o CD-06 lê ao abrir.
// Fonte única do custo-hora entre o CD-03 (mostra e edita), o CD-02 (soma no rendimento do conjunto) e o Planejar safra (configuração
// "Padrão do cadastro" das safras abertas e a troca de conjunto): achado 3 da revisão da CADUX, três valores para o mesmo dado.
const CAD_LS='talhao-os-cadastros-v1';
function cadLS(){ try{ return JSON.parse(localStorage.getItem(CAD_LS)||'{}')||{}; }catch(e){ return {}; } }
function cadLSPoe(fn){ try{ const o=cadLS(); fn(o); localStorage.setItem(CAD_LS,JSON.stringify(o)); }catch(e){} }
function cadAtivoLS(id){ const a=id?(cadLS().ativos||{})[id]:null; return a||null; }
// o custo-hora salvo no CD-03 ou, sem nada salvo, o inicial (padrao)
function cadCustoH(id,padrao){ const a=cadAtivoLS(id); const x=a?a.custo_h:null; return (x!==''&&x!==null&&x!==undefined&&!isNaN(Number(x)))?Number(x):padrao; }
