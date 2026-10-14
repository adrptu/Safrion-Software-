# -*- coding: utf-8 -*-
"""PAINEL02 / PN-DECISAO: colheita por cultivo e período comparável.

Autoria Codex; Claude integra secao() abaixo dos cartões no ramo PAGR.
Sem build() automático: o compositor chama pnaVals no EXTRAVALS existente.
Regras e unidades vêm de producao.js. Esta leitura não executa comandos.
"""
import engine as E

H = lambda s: '{{' + s + '}}'

JS = r'''
function pnaLeitura(c,id) {
 const X=prTal(c,id), k=X.k, R=X.R;
 const semana=k.semanal?prSem(prHoje()):null;
 const ps=semana?R.passes.filter(p=>p.sem===semana):R.passes;
 const versao=semana?prVersaoSem(c,id,semana):null;
 const prev=semana?(versao?versao.sem[semana]:null):prPrevTxt(c,X).v;
 const medido=semana?{
  kg:prSoma(ps.map(p=>p.kg)),cafe:prSoma(ps.map(p=>p.cafe||0)),
  apurar:ps.some(p=>p.apurar),comecou:ps.some(p=>p.apurar||p.kg>0||p.area>0)
 }:R;
 const recebimentos=ps.reduce((n,p)=>n+p.aPesar.length,0);
 const periodo=semana?prSemTxt(semana)+' · '+prBr(prSemIni(semana))+'–'+prBr(prDiaMais(prSemIni(semana),6))+' (em curso)':
  ((PRDC.safras[k.saf]||{}).nome||('Safra '+k.saf));
 return {id,k,periodo,prev,medido,recebimentos,situacao:X.sit,proximo:X.nx,
  previsao:prev===null?'Sem previsão publicada':prUnTxt(k.cultura,prev),
  recebido:prProdTxt(k.cultura,medido),href:'COLH.dc.html#'+encodeURIComponent(id)};
}
function pnaLinhas(c) {
 if(!c||!c.ordens||!c.producao||!c.producao.previsoes) return null;
 return Object.keys(PRDC.cult).filter(id=>PRDC.cult[id].prod).map(id=>pnaLeitura(c,id));
}
function pnaRow(x) {
 const cultivo=x.k.local+' · '+x.k.cultura+(x.k.var?' '+x.k.var:'');
 const situacao=x.situacao+(x.recebimentos?' · '+x.recebimentos+' carga(s) a receber':'');
 return {id:x.id,ro:true,ordk:{prev:x.prev,recebido:x.medido.apurar&&!(x.medido.kg>0)?null:x.medido.kg},v:{cultivo,periodo:x.periodo,prev:x.prev,
  recebido:x.medido.apurar&&!(x.medido.kg>0)?null:x.medido.kg,situacao},
  s:{cultivo:cultivo+' · '+x.k.faz,periodo:x.periodo,prev:x.previsao,recebido:x.recebido,situacao:situacao+' · '+x.proximo},
  p:{cultivo:[{k:'b',t:cultivo},{k:'br'},{k:'mut',t:x.k.faz}],periodo:[{k:'txt',t:x.periodo}],
   prev:[{k:x.prev===null?'mut':'txt',t:x.previsao}],recebido:[{k:'txt',t:x.recebido}],
   situacao:[{k:'chip',t:x.situacao,c:PR_SITCOR[x.situacao]||'gray'},
    {k:'br'},{k:'mut',t:x.recebimentos?x.recebimentos+' carga(s) a receber':x.proximo}]}};
}
// Apresentação do contrato agrPainelRef; regras, prazos e bloqueios pertencem ao domínio.
function pnaOSLinhas(ref) {
 const os=ref&&ref.os;
 if(!os||!Array.isArray(os.impedidas)||!Array.isArray(os.atrasadas)) return null;
 const itens=os.impedidas.concat(os.atrasadas);
 if(!itens.every(x=>x&&typeof x.id==='string'&&/^OS-[A-Za-z0-9-]+$/.test(x.id)&&
   typeof x.origem==='string'&&x.origem==='OS.dc.html#'+x.id)) return null;
 const m=new Map();
 os.impedidas.forEach(x=>m.set(x.id,{...x,impedida:true,atrasada:false}));
 os.atrasadas.forEach(x=>{const a=m.get(x.id);m.set(x.id,a?{...a,atrasada:true,prevista:x.prevista,dias:x.dias}:{...x,impedida:false,atrasada:true});});
 return [...m.values()];
}
function pnaOSRow(x) {
 const txt=(v,ausente)=>typeof v==='string'&&v.trim()?v:ausente;
 const id='os:'+x.id, local=txt(x.talhao,'Talhão não informado'), faz=txt(x.faz,'Fazenda não informada');
 const saf=txt(x.saf,'Safra não informada');
 const situacao=[x.impedida?'Impedida':'',x.atrasada?'Atrasada':''].filter(Boolean).join(' · ');
 const motivo=x.impedida?txt(x.motivo,'Consulte o impedimento na O.S.'):'Janela prevista ultrapassada';
 const dono=txt(x.dono,'Responsável não informado');
 const iso=typeof x.prevista==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(x.prevista)?x.prevista:null;
 const data=iso?iso.split('-').reverse().join('/'):'Data não informada';
 const dias=typeof x.dias==='number'&&Number.isInteger(x.dias)&&x.dias>0?x.dias:null;
 const prazo=x.atrasada?data+(dias===null?'':' · '+dias+' dia(s) de atraso'):'Consulte a janela na O.S.';
 return {id,ro:true,href:x.origem,v:{ordem:x.id,local,contexto:faz+' · '+saf,situacao,motivo,dono,prazo},
  s:{ordem:x.id+' · Abrir O.S.',local:local+' · '+faz+' · '+saf,situacao:situacao+' · '+motivo,dono,prazo},
  p:{ordem:[{k:'b',t:x.id},{k:'br'},{k:'chip',t:situacao,c:'yellow'},{k:'br'},{k:'txt',t:motivo},{k:'br'},{k:'mut',t:'Abrir O.S.'}],
   local:[{k:'txt',t:local},{k:'br'},{k:'mut',t:faz+' · '+saf}],
   situacao:[{k:'chip',t:situacao,c:'yellow'},{k:'br'},{k:'txt',t:motivo}],
   dono:[{k:'txt',t:dono}],prazo:[{k:'txt',t:prazo}]}};
}
function pnaVals(self,v) {
 g2keep(self,'g_pna');g2keep(self,'g_pna_os');
 if(!self.__pnaFocus){self.__pnaFocus=true;
  const restaura=()=>{const id=(history.state||{}).pnaFoco;if(!id)return;let n=0;
   const f=()=>{const r=[...document.querySelectorAll('[data-rid]')].find(e=>e.getAttribute('data-rid')===id);
    if(r){r.focus({preventScroll:true});return;}if(++n<40)setTimeout(f,50);};setTimeout(f,0);};
  restaura();window.addEventListener('pageshow',restaura);
 }
 const c=cenGet(), rows=pnaLinhas(c);
 const os=pnaOSLinhas(typeof agrPainelRef==='function'?agrPainelRef(c,{}):null);
 GRIDS.find(g=>g.id==='g_pna_os').rows=(os||[]).map(pnaOSRow);
 v.pna_os_missing=os===null;v.pna_os_empty=os!==null&&os.length===0;
 GRIDS.find(g=>g.id==='g_pna').rows=(rows||[]).map(pnaRow);
 v.pna_missing=rows===null;
 self.g2pick=(gid,id)=>{const x=gid==='g_pna_os'?(os||[]).map(pnaOSRow).find(x=>x.id===id):gid==='g_pna'?(rows||[]).find(x=>x.id===id):null;if(x){
  history.replaceState(Object.assign({},history.state||{},{pnaFoco:id}),'',location.href);location.href=x.href;}};
}
'''


def secao():
    """Retorna (HTML, JS) para a tela já iniciada; não substitui cartões/shell."""
    table=E.grid([
        dict(k='cultivo',l='Cultivo · fazenda',w=220),
        dict(k='periodo',l='Período',w=170),
        dict(k='prev',l='Previsão publicada',t='num',a='r',w=145),
        dict(k='recebido',l='Recebido',t='num',a='r',w=145),
        dict(k='situacao',l='Situação · próximo passo',w=245),
    ],[],gid='g_pna',edit=dict(m='pick'),total=False)
    formula=('Previsão publicada e cargas recebidas do mesmo cultivo: semana em curso para culturas semanais; safra para anuais. '
             'Recebido soma os passes daquele período pelas regras de Previsão e colheita. '
             'Sem previsão não significa zero; café sem rendimento medido fica a apurar. '
             'Não soma culturas, períodos ou unidades e não calcula desvio final em período aberto. Fonte: Previsão e colheita.')
    body=(f'<section aria-label="Colheita por cultivo"><h2 style="font-size:16px;color:{E.INK}">Colheita · previsto e recebido '
          f'<button type="button" class="g2dica-i" aria-label="Como comparar a colheita" data-dica="{E.esc(formula)}" '
          f'style="width:44px;height:44px;border:0;background:transparent;color:{E.MUTED};font:inherit">ⓘ</button></h2>'
          '<p role="status" hidden="'+H('!pna_missing')+'">Dados de produção indisponíveis. Abra Previsão e colheita para conferir a origem.</p>'+
          table+'</section>')
    pendencias=E.grid([
        dict(k='ordem',l='O.S. · situação · motivo',w=240),
        dict(k='local',l='Talhão · fazenda · safra',w=210),
        dict(k='dono',l='Quem resolve',w=170),
        dict(k='prazo',l='Prazo',w=185),
    ],[],gid='g_pna_os',edit=dict(m='pick'),total=False)
    osbody=('<section aria-label="O.S. que precisam de atenção">'
        f'<h2 style="font-size:16px;color:{E.INK}">O.S. · impedimentos e atrasos</h2>'
        '<p role="status" hidden="'+H('!pna_os_missing')+'">Dados de impedimentos e prazos indisponíveis. Consulte a origem em O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_empty')+'">Nenhuma O.S. impedida ou atrasada neste recorte.</p>'+
        pendencias+'</section>')
    return osbody+body, JS
