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
 if(!os) return null;
 const imp=Array.isArray(os.impedidas)?os.impedidas:os.impedidas===null?[]:null;
 const atr=Array.isArray(os.atrasadas)?os.atrasadas:os.atrasadas===null?[]:null;
 if(!imp||!atr||(os.impedidas===null&&os.atrasadas===null)) return null;
 const itens=imp.concat(atr);
 if(!itens.every(x=>x&&typeof x.id==='string'&&/^OS-[A-Za-z0-9-]+$/.test(x.id)&&
   typeof x.origem==='string'&&x.origem==='OS.dc.html#'+x.id)) return null;
 const m=new Map();
 imp.forEach(x=>m.set(x.id,{...x,impedida:true,atrasada:false}));
 atr.forEach(x=>{const a=m.get(x.id);m.set(x.id,a?{...a,atrasada:true,prevista:x.prevista,dias:x.dias}:{...x,impedida:false,atrasada:true});});
 return [...m.values()];
}
function pnaOSGrupos(os,campo) {
 if(os===null)return null;
 const m=new Map();
 os.forEach(x=>{
  const raw=campo==='motivo'?(x.impedida?x.motivo:'Janela prevista ultrapassada'):x.dono;
  const label=typeof raw==='string'&&raw.trim()?raw.trim():campo==='motivo'?'Impedimento não informado':'Responsável não informado';
  if(!m.has(label))m.set(label,{label,ids:[],impedidas:0,atrasadas:0});
  const g=m.get(label);g.ids.push(x.id);g.impedidas+=x.impedida?1:0;g.atrasadas+=x.atrasada?1:0;
 });
 const groups=[...m.values()].sort((a,b)=>b.ids.length-a.ids.length||a.label.localeCompare(b.label,'pt-BR'));
 const max=Math.max(1,...groups.map(g=>g.ids.length));
 return groups.map(g=>({...g,n:g.ids.length,
  situacao:[g.impedidas?g.impedidas+' impedida(s)':'',g.atrasadas?g.atrasadas+' atrasada(s)':''].filter(Boolean).join(' · '),
  barra:'display:block;height:8px;border-radius:3px;width:'+(100*g.ids.length/max)+'%;background:'+(g.impedidas?'#B42318':'#8A5A00')}));
}
function pnaVals(self,v) {
 g2keep(self,'g_pna');
 if(!self.__pnaFocus){self.__pnaFocus=true;
  const restaura=()=>{const id=(history.state||{}).pnaFoco;if(!id)return;let n=0;
   const f=()=>{const r=[...document.querySelectorAll('[data-rid]')].find(e=>e.getAttribute('data-rid')===id);
    if(r){r.focus({preventScroll:true});return;}if(++n<40)setTimeout(f,50);};setTimeout(f,0);};
  restaura();window.addEventListener('pageshow',restaura);
 }
 const c=cenGet(), rows=pnaLinhas(c);
 const ref=typeof agrPainelRef==='function'?agrPainelRef(c,{}):null, os=pnaOSLinhas(ref);
 v.pna_causas=pnaOSGrupos(os,'motivo')||[];v.pna_donos=pnaOSGrupos(os,'dono')||[];
 v.pna_os_total=os===null?'Indisponível':os.length+' O.S. com atenção identificada';
 v.pna_os_missing=os===null;
 v.pna_os_has_data=os!==null&&os.length>0;
 v.pna_os_atraso_missing=os!==null&&ref.os.atrasadas===null;
 v.pna_os_imp_missing=os!==null&&ref.os.impedidas===null;
 v.pna_sem_prazo=ref&&ref.os&&ref.os.n&&Number.isInteger(ref.os.n.sem_prazo)&&ref.os.n.sem_prazo>0?ref.os.n.sem_prazo:0;
 v.pna_os_empty=os!==null&&os.length===0&&!v.pna_os_atraso_missing&&!v.pna_os_imp_missing&&!v.pna_sem_prazo;
 GRIDS.find(g=>g.id==='g_pna').rows=(rows||[]).map(pnaRow);
 v.pna_missing=rows===null;
 self.g2pick=(gid,id)=>{const x=gid==='g_pna'?(rows||[]).find(x=>x.id===id):null;if(x){
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
    explicacao=('Cada O.S. é contada uma vez em cada gráfico, mesmo impedida e atrasada. '
                'Motivo e responsável vêm da O.S.; o motivo é o impedimento informado, ou atraso quando não há impedimento. '
                'As duas distribuições descrevem as mesmas ordens e não devem ser somadas. '
                'Barras relativas ao maior grupo. Fonte: O.S., todas as fazendas e safras disponíveis. '
                'Área afetada não fornecida pela origem; não estimamos hectares por contagem de ordens.')
    def grafico(titulo, campo):
        return ('<section class="pn-chart"><h3 style="font-size:15px;margin:0 0 12px">'+titulo+'</h3>'
                '<ul style="list-style:none;padding:0;margin:0"><sc-for list="'+H(campo)+'" as="g" hint-placeholder-count="3">'
                '<li class="pna-grupo" style="margin:16px 0;overflow-wrap:anywhere">'
                '<div style="display:flex;justify-content:space-between;gap:12px"><span>'+H('g.label')+'</span>'
                '<strong style="white-space:nowrap">'+H('g.n')+' O.S.</strong></div>'
                '<div aria-hidden="true" style="height:8px;background:#EEF1EE;border-radius:3px;margin:6px 0"><span style="'+H('g.barra')+'"></span></div>'
                '<span style="font-size:12px">'+H('g.situacao')+'</span></li></sc-for></ul></section>')
    pendencias=('<sc-if value="'+H('pna_os_has_data')+'" hint-placeholder-val="{{true}}"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px">'+
                grafico('Por motivo informado','pna_causas')+grafico('Por quem resolve','pna_donos')+'</div></sc-if>')
    osbody=('<section aria-label="O.S. que precisam de atenção">'
        f'<h2 style="font-size:16px;color:{E.INK}">O.S. · onde agir primeiro</h2>'
        '<p>'+H('pna_os_total')+' <button type="button" class="g2dica-i" aria-label="Como ler os impedimentos e atrasos" data-dica="'+E.esc(explicacao)+'" style="width:44px;height:44px;border:0;background:transparent">ⓘ</button></p>'
        '<p style="font-size:12px">Todas as fazendas e safras disponíveis · Fonte: O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_missing')+'">Dados de impedimentos e prazos indisponíveis. Consulte a origem em O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_atraso_missing')+'">Prazos indisponíveis para verificar atrasos. Consulte a janela na O.S.; os impedimentos disponíveis seguem abaixo.</p>'
        '<p role="status" hidden="'+H('!pna_os_imp_missing')+'">Impedimentos indisponíveis. Os atrasos disponíveis seguem abaixo.</p>'
        '<p role="status" hidden="'+H('!pna_sem_prazo')+'">'+H('pna_sem_prazo')+' O.S. sem prazo válido; não avaliadas quanto a atraso. Confira a janela na O.S.</p>'
        '<p role="status" hidden="'+H('!pna_os_empty')+'">Nenhuma O.S. impedida ou atrasada neste recorte.</p>'+
        pendencias+'</section>')
    return osbody+body, JS
