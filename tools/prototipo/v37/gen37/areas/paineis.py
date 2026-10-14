# -*- coding: utf-8 -*-
"""PAINEL-01: leitura do cenário, sem comando e sem persistência paralela.
Base f6b31f7; autoria Codex, revisão/integração Claude. Menu via patch separado.
Contagens (não soma de ha, kg, L ou moedas); ausente/incompleto nunca vira zero.
"""
import json
import engine as E
import cenario
import dados_manutencao as DM
from ui37 import shell37, HEIGHTS37
from areas.modulos import JS_VOLTA
H = lambda s: '{{' + s + '}}'

# ID, módulo, título do gráfico, indicadores (nome, fórmula/fonte, desvio), atalhos.
PAINEIS = {
 'PAGR': ('Agrícola', 'O.S. por estado', [
  ('A liberar', 'Contagem das O.S. agrícolas com etapa A liberar. Fonte: cenário compartilhado de O.S.; exclui ordens de beneficiamento.', False),
  ('Liberadas', 'Contagem das O.S. agrícolas com etapa Liberadas. Fonte: cenário compartilhado de O.S.', False),
  ('Em execução', 'Contagem das O.S. agrícolas com etapa Em execução. Fonte: cenário compartilhado de O.S.', False),
  ('Em conferência', 'Contagem das O.S. agrícolas com etapa Em conferência. Fonte: cenário compartilhado de O.S.', False)],
  [('Consultar O.S.', 'OS.dc.html'), ('Planejar safra', 'SAF.dc.html'), ('Consultar colheita', 'COLH.dc.html')]),
 'PMAN': ('Manutenção', 'Ordens por estado', [
  ('Pendências sem ordem', 'Contagem de serviços devidos sem ordem do ciclo nem outra ordem preventiva equivalente. Fonte: manSemOm, planos publicados e leituras da Manutenção.', True),
  ('Ordens abertas', 'Contagem de ordens não encerradas nem canceladas. Fonte: manAberta, cenário da Manutenção.', False),
  ('Em execução', 'Contagem de ordens com etapa Em execução. Fonte: cenário da Manutenção.', False),
  ('Ativos bloqueados', 'Contagem de ativos com condição Bloqueado. Fonte: cenário da Manutenção.', True)],
  [('Tratar pendências', 'MA.dc.html#vis=semordem'), ('Consultar ordens', 'MA.dc.html#vis=ordens'), ('Consultar ativos', 'MA.dc.html#vis=ativos'), ('Consultar planos', 'MA.dc.html#vis=planos')]),
 'PSUP': ('Suprimentos', 'Lotes com saldo físico', [
  ('Lotes com saldo físico', 'Contagem de lotes com saldo físico maior que zero. Inclui reservado e quarentena; não significa disponível para uso. Fonte: cenário do Estoque.', False),
  ('Lotes com reserva', 'Contagem de lotes com quantidade reservada maior que zero. Um lote pode também ter quarentena. Fonte: cenário do Estoque.', False),
  ('Lotes em quarentena', 'Contagem de lotes com quantidade em quarentena maior que zero. Fonte: cenário do Estoque; a liberação exige decisão própria.', True),
  ('Requisições a entregar', 'Contagem de requisições de ordens Liberadas ou Em execução com pelo menos um item cujo saldo a entregar é positivo segundo a regra da requisição vigente. Fonte: cenSaldoEntregar. Não soma unidades.', False)],
  [('Conferir estoque', 'EST.dc.html'), ('Acompanhar compras', 'CMP.dc.html')]),
}

JS = r'''
// Indicadores leem somente a fonte canônica. Coleção vazia = zero; ausente/inválida = sem dados.
function pnObjs(x) { return x && typeof x==='object' && !Array.isArray(x) ? Object.values(x) : null; }
function pnNum(x) { return typeof x==='number' && Number.isFinite(x) && x>=0; }
function pnConta(xs, pred) { return xs===null ? null : xs.filter(pred).length; }
function pnValores(c,k) {
 const validOs=x=>x&&typeof x.id==='string'&&typeof x.etapa==='string';
 const all=pnObjs(c&&c.ordens), os=all&&all.every(validOs)?all.filter(o=>o.id.startsWith('OS-')&&o.fam!=='BEN'):null;
 let vals, bars, labels;
 if(k==='PAGR') {
  labels=['A liberar','Liberadas','Em execução','Em conferência'];
  vals=labels.map(s=>pnConta(os,o=>o.etapa===s)); bars=vals;
 } else if(k==='PMAN') {
  const m=c&&c.man, oo=pnObjs(m&&m.oms), aa=pnObjs(m&&m.ativos);
  const oms=oo&&oo.every(x=>x&&typeof x.etapa==='string')?oo:null;
  const ativos=aa&&aa.every(x=>x&&typeof x.cond==='string')?aa:null;
  let sem=null;
  if(m&&oms&&ativos&&pnObjs(m.planos)&&pnObjs(m.vinc)&&typeof m.hoje==='string'&&pnNum(m.horiz)) {
   try { sem=manSemOm(m).length; } catch(e) { sem=null; }
  }
  vals=[sem,pnConta(oms,manAberta),pnConta(oms,o=>o.etapa==='Em execução'),pnConta(ativos,a=>a.cond==='Bloqueado')];
  labels=['A liberar','Liberadas','Em execução','Em conferência']; bars=labels.map(s=>pnConta(oms,o=>o.etapa===s));
 } else {
  const ll=pnObjs(c&&c.lotes), rr=pnObjs(c&&c.reqs);
  const ls=ll&&ll.every(l=>l&&pnNum(l.fisico)&&pnNum(l.reservado)&&pnNum(l.quarentena))?ll:null;
  const rs=all&&all.every(validOs)&&rr&&rr.every(r=>r&&c.ordens[r.os]&&Array.isArray(r.itens)&&r.itens.every(i=>i&&['solicitado','consumido','custodia'].every(n=>pnNum(i[n]))&&(i.dispensado===undefined||pnNum(i.dispensado))))?rr:null;
  vals=[pnConta(ls,l=>l.fisico>0),pnConta(ls,l=>l.reservado>0),pnConta(ls,l=>l.quarentena>0),pnConta(rs,r=>['Liberadas','Em execução'].includes(c.ordens[r.os].etapa)&&r.itens.some(i=>cenSaldoEntregar(i)>1e-6))];
  labels=['Com quarentena','Com reserva, sem quarentena','Sem reserva nem quarentena'];
  bars=[pnConta(ls,l=>l.fisico>0&&l.quarentena>0),pnConta(ls,l=>l.fisico>0&&l.quarentena===0&&l.reservado>0),pnConta(ls,l=>l.fisico>0&&l.quarentena===0&&l.reservado===0)];
 }
 return {vals,bars,labels};
}
function EXTRAVALS(self,v) {
 cenOuvir(self); modVolta(self);
 const p=pnValores(cenGet(),PN_ID), max=Math.max(1,...p.bars.filter(x=>x!==null));
 const fmt=x=>x===null?'Sem dados':x.toLocaleString('pt-BR');
 p.vals.forEach((x,i)=>{v['pn_v'+i]=fmt(x);v['pn_alert'+i]=PN_ALERT[i]&&x>0;});
 p.bars.forEach((x,i)=>{v['pn_b'+i]=fmt(x);v['pn_w'+i]=x===null?0:Math.round(x/max*100);});
 v.pn_missing=p.vals.some(x=>x===null)||p.bars.some(x=>x===null);
 v.pn_empty=p.bars.every(x=>x===0);
}
'''

CSS = '''<style>
.pn{display:flex;flex-direction:column;gap:20px;min-width:0}.pn-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.pn-card,.pn-chart{border:1px solid #E4E9E5;border-radius:14px;padding:16px;background:#fff;min-width:0}
.pn-card h2{font-size:14px;font-weight:600;margin:0;display:flex;align-items:center;justify-content:space-between;gap:4px}
.pn-value{font-size:28px;font-weight:700;color:#15201A}.pn-value[data-alert=true]{color:#B42318}
.pn-tip{flex-shrink:0;width:44px;height:44px;border:0;background:transparent;color:#65736A;cursor:pointer;font:inherit}
.pn-chart h2{font-size:16px;margin:0 0 16px}.pn-row{display:grid;grid-template-columns:minmax(130px,1fr) 2fr 80px;align-items:center;gap:12px;margin:12px 0;font-size:14px}
.pn-row svg{width:100%;height:16px;display:block}.pn-row strong{text-align:right;font-size:14px}
.pn-links{display:flex;flex-wrap:wrap;gap:12px}.pn-links a{min-height:44px;display:inline-flex;align-items:center;padding:0 14px;border:1px solid #E4E9E5;border-radius:10px;color:#15201A;text-decoration:none;background:#fff;font-size:14px}
.pn :focus-visible{outline:2px solid #1E7A4C;outline-offset:3px}
.pn-context{color:#65736A;font-size:13px;margin:0}.pn [hidden]{display:none!important}
@media(max-width:900px){.pn-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){.pn-grid{grid-template-columns:1fr}.pn-row{grid-template-columns:1fr 70px;gap:6px}.pn-row svg{grid-row:2;grid-column:1 / -1}.pn-links{flex-direction:column}}
</style>'''


def build():
    for fid, (mod, titulo, itens, atalhos) in PAINEIS.items():
        fname=fid+'.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1050
        E.EXTRAJS[0]=(cenario.js_prefixo()+DM.js_regras()+JS_VOLTA+
                       'const PN_ID='+json.dumps(fid)+';const PN_ALERT='+json.dumps([i[2] for i in itens])+';\n'+JS)
        cards=''.join('<section class="pn-card"><h2>'+E.esc(nome)+
          '<button type="button" class="pn-tip g2dica-i" aria-label="Como calcular: '+E.esc(nome)+'" data-dica="'+E.esc(formula)+'">ⓘ</button></h2>'+
          '<strong class="pn-value" data-alert="'+H('pn_alert'+str(i))+'">'+H('pn_v'+str(i))+'</strong></section>' for i,(nome,formula,_) in enumerate(itens))
        labels=(['Com quarentena','Com reserva, sem quarentena','Sem reserva nem quarentena'] if fid=='PSUP' else ['A liberar','Liberadas','Em execução','Em conferência'])
        rows=''.join('<div class="pn-row"><span>'+E.esc(l)+'</span><svg viewBox="0 0 100 8" preserveAspectRatio="none" aria-hidden="true"><rect width="100" height="8" rx="2" fill="#EEF1EE"/><rect width="'+H('pn_w'+str(i))+'" height="8" rx="2" fill="#65736A"/></svg><strong>'+H('pn_b'+str(i))+'</strong></div>' for i,l in enumerate(labels))
        links=''.join('<a class="mod-cartao pn-link" href="'+h+'">'+E.esc(n)+'</a>' for n,h in atalhos[1:])
        empty='<p hidden="'+H('!pn_empty')+'">Nenhum registro neste recorte.</p>'
        chart=(empty if fid=='PAGR' else '<section class="pn-chart" aria-label="'+E.esc(titulo)+'"><h2>'+E.esc(titulo)+'</h2>'+rows+empty+'</section>')
        body=(CSS+'<div class="pn"><p class="pn-context">'+E.esc(mod)+' · Todas as fazendas e safras · Estado atual</p>'+
          '<div class="pn-grid" aria-label="Indicadores">'+cards+'</div>'+
          '<p hidden="'+H('!pn_missing')+'" role="status">Há dados incompletos. Consulte a origem pelos acessos abaixo.</p>'+
          chart+
          '<nav class="pn-links" aria-label="Acessos do painel">'+links+'</nav></div>')
        prim=E.btn(atalhos[0][0],True,href=atalhos[0][1]).replace('<a ', '<a class="pn-link mod-cartao" ')
        shell37(fid,'Painel',body,fname=fname,status=None,primary_html=prim,search=False)
