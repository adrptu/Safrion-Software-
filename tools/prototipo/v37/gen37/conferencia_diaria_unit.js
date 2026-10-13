const assert = require('node:assert/strict');
const resultados = [];
function teste(nome, fn) { try { fn(); resultados.push({nome, ok:true}); } catch(e) { resultados.push({nome, ok:false, erro:e.stack}); } }
const novo = () => cenClone(CEN0), id = 'OS-0421', dia = 4;
const fato = c => JSON.stringify({etapa:c.ordens[id].etapa,real:c.ordens[id].realizado,saldo:c.ordens[id].saldo,req:c.reqs,movs:c.movs});
const decide = (c,dec='conferir',mot='',ator='Paula',ref=cdReferencia(c,id,dia)) => cdConferir(c,id,dia,dec,mot,ref,ator);
function recusa(c,fn,padrao) { const antes=JSON.stringify(c);assert.throws(fn,padrao);assert.equal(JSON.stringify(c),antes); }
teste('Conferir dia preserva fase, área, saldo, consumo e custódia',()=>{const c=novo(),antes=fato(c);const r=decide(c);assert.equal(r.recibo.estado,'Conferido');assert.match(r.recibo.por,/Paula/);assert.equal(fato(c),antes);});
teste('Reenvio devolve recibo sem histórico ou efeitos repetidos',()=>{const c=novo(),ref=cdReferencia(c,id,dia);decide(c,'conferir','','Paula',ref);const antes=JSON.stringify(c);const r=decide(c,'conferir','','Paula',ref);assert.equal(r.repetido,true);assert.equal(JSON.stringify(c),antes);});
teste('Papel sem alçada recusa sem alteração',()=>{const c=novo();recusa(c,()=>decide(c,'conferir','','Marcos'),/decisão/);});
teste('Versão alterada recusa prévia antiga',()=>{const c=novo(),ref=cdReferencia(c,id,dia);c.ordens[id].versao='v99';recusa(c,()=>decide(c,'conferir','','Paula',ref),/mudou/);});
teste('Fato alterado recusa prévia antiga',()=>{const c=novo(),ref=cdReferencia(c,id,dia);cdAp(c,id,dia).ap.ha++;recusa(c,()=>decide(c,'conferir','','Paula',ref),/mudou/);});
teste('Sem sinal não recebe conferência',()=>{const c=novo();cdAp(c,id,dia).ap.sinc=false;recusa(c,()=>decide(c),/sinal/);});
teste('Duplicidade não recebe conferência',()=>{const c=novo();cdAp(c,id,dia).ap.st=CEN_AP_DUP;recusa(c,()=>decide(c),/duplicidade/);});
teste('Divergência exige motivo e preserva fatos',()=>{const c=novo(),antes=fato(c);recusa(c,()=>decide(c,'divergencia',' '),/motivo/);decide(c,'divergencia','Horas do turno divergentes');assert.match(cdPendente(c,id),/dia 4/);assert.equal(fato(c),antes);});
teste('Resolver divergência exige motivo e guarda decisão anterior',()=>{const c=novo();decide(c,'divergencia','Conferir evidência');recusa(c,()=>decide(c),/resolvida/);decide(c,'conferir','Evidência do turno conferida');assert.equal(cdPendente(c,id),'');assert.equal(cdAp(c,id,dia).ap.conferenciasAnteriores.length,1);});
teste('Conferente não substitui revisão agronômica',()=>{const c=novo();cdAp(c,id,dia).ap.div=[{p:'X',plan:1,inf:2}];delete cdAp(c,id,dia).ap.rev;recusa(c,()=>decide(c),/agrônomo/);});
teste('Conferente não substitui decisão de estoque',()=>{const c=novo();c.confs=[{id:'CC-X',os:id,dia,sinc:true,estado:'Em conferência'}];recusa(c,()=>decide(c),/Estoque/);});
teste('Mesmo autor fica com revisão posterior explícita',()=>{const c=novo();cdAp(c,id,dia).ap.quem='Paula';assert.match(decide(c).recibo.revisaoPosterior,/revisão posterior/);});
teste('Mudança após conferência reabre pendência sem apagar recibo',()=>{const c=novo();decide(c);cdAp(c,id,dia).ap.ha++;assert.match(cdPendente(c,id),/dia 4/);assert.ok(cdAp(c,id,dia).ap.conferenciaDia);});
teste('Fase encerrada não aceita decisão nova',()=>{const c=novo();c.ordens[id].etapa='Encerradas';recusa(c,()=>decide(c),/fase/);});
teste('Divergência posterior retira confirmação diária anterior',()=>{const c=novo();decide(c);decide(c,'divergencia','Evidência posterior');assert.equal(cdAp(c,id,dia).ap.st,'Provisório');assert.match(cdPendente(c,id),/dia 4/);});
teste('Revisão futura da ordem preserva a conferência do fato anterior',()=>{const c=novo();decide(c);c.ordens[id].versao='v99';assert.equal(cdPendente(c,id),'');});
teste('Encerramento real recusa a divergência diária',()=>{const c=novo();decide(c,'divergencia','Conferir evidência');c.ordens[id].etapa='Em conferência';assert.throws(()=>osc_encerrar(c,id),/Reveja a conferência diária/);assert.equal(c.ordens[id].etapa,'Em conferência');});
teste('Bloqueio diário aponta conferente, não almoxarife',()=>{const c=novo();decide(c,'divergencia','Conferir evidência');const b=osEncBloq({encM:cdPendente(c,id)});assert.match(b.q,/conferência/);assert.doesNotMatch(b.q,/almoxarife/);});
teste('Apontamento provisório sem recibo impede encerramento',()=>{const c=novo();assert.match(cdPendente(c,id),/dia 4/);c.ordens[id].etapa='Em conferência';assert.throws(()=>osc_encerrar(c,id),/Reveja a conferência diária/);});
teste('Substituir duplicidade preserva recibo antigo sem bloquear ordem para sempre',()=>{const c=novo();decide(c);osc_apontar(c,id,'26/09',50);if(cdAp(c,id,5).ap.div)cenDivRever(c,id,5,'aceitar','Evidência sintética técnica','Ana');cdConferir(c,id,5,'conferir','',cdReferencia(c,id,5),'Paula');cenIniciarTurno(c,id);cenFecharTurno(c,50,8,undefined,'',[]);cenApDecidir(c,id,6,'este','Paula');const antigo=cdAp(c,id,5).ap;assert.equal(antigo.st,CEN_AP_DESC);assert.ok(antigo.conferenciaDia);if(cdAp(c,id,6).ap.div)cenDivRever(c,id,6,'aceitar','Evidência sintética técnica','Ana');cdConferir(c,id,6,'conferir','',cdReferencia(c,id,6),'Paula');assert.equal(cdPendente(c,id),'');});
console.log(JSON.stringify(resultados));process.exitCode=resultados.some(r=>!r.ok)?1:0;
