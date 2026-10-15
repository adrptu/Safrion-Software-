# -*- coding: utf-8 -*-
"""Agrícola › Planos agronômicos (PA.dc.html) · NAV-1 (docs/navegacao/ESPECIFICACAO.md): lista → detalhe, sem etapas.
Lista: biblioteca por cultura (cartões) com filtro por cultura; "Criar plano" no cabeçalho (BOT-02/03/05).
Detalhe (PA.dc.html#plano=<id>, como o PM da PCM, D-03): atividades (dose na tabela; "Incluir atividade" secundária no bloco)
e, com rascunho, as alterações vN × vM logo acima de "Publicar versão vN" (Próximo passo). Cultivos e Versões saíram (14/10).
Salvar grava num rascunho v(n+1); publicar cria a nova versão; cultivos aplicados nunca são alterados aqui (a adoção é por
cultivo, no Planejar safra: PRD 40.3)."""
import json, os
from engine import grid, esc, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, GRAYS, DISP, BTN_ST, EXTRA, EXTRAJS, _MINI, _MINIP
import engine as E
from ui37 import shell37, HEIGHTS37
import dados2 as D2

H = lambda s: '{{' + s + '}}'
F = lambda: H('false')
T = lambda: H('true')
def IF(cond, html, dflt=False): return f'<sc-if value="{H(cond)}" hint-placeholder-val="{T() if dflt else F()}">{html}</sc-if>'
def FOR(lst, as_, html, n=2): return f'<sc-for list="{H(lst)}" as="{as_}" hint-placeholder-count="{n}">{html}</sc-for>'

# "+" de Criar e Incluir (BOT-05): o mesmo desenho em todos os botões desse papel, sempre com rótulo; aria-hidden (o nome é o rótulo)
def MAIS(tam=14): return (f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
                          f'stroke-linecap="round" aria-hidden="true" style="flex-shrink: 0;"><path d="M12 5v14M5 12h14"/></svg>')
ICO = 'display: inline-flex; align-items: center; gap: 6px;'

# ---- dados locais coerentes com dados2 (declarados em observações) ----
# versão do plano aplicada a cada cultivo quando difere da versão publicada atual (safra encerrada usou versões anteriores)
VER_APLICADA = {'e1': 5, 'e2': 5, 'e3': 3}
# datas de publicação das versões conhecidas
HIST = {'SOJA-AT': [(6, '12/08/2026'), (5, '18/08/2025')], 'SOJA-PD': [(3, '05/06/2026')], 'MILHO-SF': [(4, '10/09/2026'), (3, '02/09/2025')],
        'FEIJ-PV': [(3, '22/07/2026')], 'CAFE-AR': [(2, '15/01/2026')], 'MAMAO-F': [(3, '28/03/2026')]}


# atividades usuais de cada macro operação (o filtro do formulário parte daqui e dos planos já cadastrados)
ATV_PADRAO = {
    'Pulverização': ['Dessecação pré-plantio', 'Herbicida pré-emergente', 'Herbicida pós-emergente', 'Inseticida', 'Fungicida 1ª aplicação',
                     'Fungicida 2ª aplicação + inseticida', 'Fungicida 3ª aplicação', 'Adubação foliar', 'Controle de ácaro', 'Dessecação pré-colheita'],
    'Plantio': ['Plantio e adubação de base', 'Plantio', 'Replantio'],
    'Adubação a lanço': ['Calagem', 'Gessagem', 'Potássio pré-plantio', 'Adubação de cobertura', 'Adubação 1ª parcela', 'Adubação 2ª parcela'],
    'Tratamento de sementes': ['Tratamento de sementes', 'Inoculação'],
    'Colheita de grãos': ['Colheita'],
    'Colheita de café': ['Colheita', 'Repasse'],
    'Poda': ['Poda de esqueletamento', 'Recepa', 'Desbrota'],
    'Fertirrigação': ['Fertirrigação de nitrogênio', 'Fertirrigação de potássio', 'Fertirrigação de cálcio'],
}


def _dados():
    cat = {}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']:
                cat.setdefault(x['prod'], dict(grupo=x['grupo'], un=x['un'], preco=x['preco']))
    ops = []
    for c in D2.CONJ:
        if c['op'] not in ops: ops.append(c['op'])
    culturas = []
    for p in D2.PLANOS:
        if p['cultura'] not in culturas: culturas.append(p['cultura'])
    saf = {s['id']: s for s in D2.SAFRAS}
    cults = []
    for sk, cs in D2.CULTIVOS.items():
        for c in cs:
            if not c['plano']: continue
            cults.append(dict(id=c['id'], safra=sk, safraNome=saf[sk]['nome'], ro=bool(saf[sk]['ro']), local=c['local'], cultura=c['cultura'],
                              variedade=c['variedade'], area=c['area'], plano=c['plano'], ver=VER_APLICADA.get(c['id'], D2.PLANO[c['plano']]['versao'])))
    popts = sorted(cat.items(), key=lambda kv: (D2.GRUPOS.index(kv[1]['grupo']) if kv[1]['grupo'] in D2.GRUPOS else 99, kv[0]))
    atvs = {op: list(ATV_PADRAO.get(op, [])) for op in ops}
    for p in D2.PLANOS:
        for a in p['atividades']:
            l = atvs.setdefault(a['op'], [])
            if a['nome'] not in l: l.append(a['nome'])
    return dict(planos=D2.PLANOS, cat=cat, ops=ops, atvs=atvs, culturas=culturas, cultivos=cults, hoje=D2.HOJE,
                hist={k: [dict(v=v, at=at) for v, at in vs] for k, vs in HIST.items()},
                popts=[dict(v='', t='Escolha o produto')] + [dict(v=k, t=f"{c['grupo']} · {k} ({c['un']})") for k, c in popts])


JS = r'''
function paClone(o){ return JSON.parse(JSON.stringify(o)); }
function paN(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function paQ(n){ return Number(n||0).toLocaleString('pt-BR',{maximumFractionDigits:3}); }
function paRS(n){ return 'R$ '+paN(n,2); }
function paBr(s){ if(!s) return '—'; const a=String(s).split('-'); return a.length===3? a[2]+'/'+a[1]+'/'+a[0] : String(s); }
const PA_C={g:['#1E7A4C','#E4F3E9'],y:['#8A5A00','#FFF3D6'],r:['#B42318','#FDE8E6'],n:['#5B6660','#EEF1EE'],b:['#1E5F8F','#E3F0FB']};
function paChip(c){ const k=PA_C[c]||PA_C.n; return 'display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
const PA_TIPOS=[{v:'DAPA',t:'Dias antes do plantio'},{v:'DAP',t:'Dias após o plantio (DAP)'},{v:'DANC',t:'Dias antes da colheita'},{v:'DAPC',t:'Dias após a colheita'},{v:'DATA',t:'Data do calendário'}];
const PA_TAG={DAP:'DAP',DANC:'Antes da colheita',DAPC:'Após a colheita',DATA:'Data'};
const PA_TORD=['DAP','Data','Antes da colheita','Após a colheita'];
function paUsam(nc){ return nc===1?' e o cultivo que usa o plano':' e os '+nc+' cultivos que usam o plano'; }
function paDias(n){ n=Math.abs(Number(n)); return n+(n===1?' dia':' dias'); }
function paGat(g){ const d=Number(g.dias);
  if(g.tipo==='DAP') return {t:'DAP '+(d<0?'−':'')+Math.abs(d), full:(d===0?'no dia do plantio':paDias(d)+(d<0?' antes do plantio':' após o plantio'))};
  if(g.tipo==='DANC') return {t:paDias(d)+' antes da colheita',full:''};
  if(g.tipo==='DAPC') return {t:paDias(d)+' após a colheita',full:''};
  return {t:paBr(g.data),full:''}; }
function paGrp(g){ return g.tipo==='DAP'?'DAP':(g.tipo==='DATA'?'DATA':'COL'); }
function paOrd(g){ if(g.tipo==='DATA') return String(g.data||''); if(g.tipo==='DANC') return -Number(g.dias); return Number(g.dias); }
function paGkey(g){ return g.tipo+'|'+(g.tipo==='DATA'?g.data:Number(g.dias)); }
const PA_GRP={DAP:{t:'Dias após o plantio (DAP)',d:'Confira as atividades pela distância do plantio; valores negativos acontecem antes do plantio.'},
  COL:{t:'Em relação à colheita',d:'Confira as atividades antes e depois da colheita, na ordem em que acontecem.'},
  DATA:{t:'Data do calendário',d:'Confira as atividades de data fixa, em ordem cronológica.'}};
function paCa(a){ return (a.prods||[]).reduce((s,p)=>s+Number(p.dose||0)*Number(p.preco||0),0); }
function paCt(atvs){ return (atvs||[]).reduce((s,a)=>s+paCa(a),0); }
const PA_BASE=PA0.planos.map(p=>({id:p.id,nome:p.nome,cultura:p.cultura,versao:p.versao,atividades:p.atividades,rasc:null,hist:(PA0.hist[p.id]||[{v:p.versao,at:'—'}])}));
function paPlans(self){ return self.state.pl||PA_BASE; }
function paPlan(self,id){ return paPlans(self).find(p=>p.id===id)||null; }
function paWork(p){ return p.rasc?p.rasc.atividades:p.atividades; }
function paShown(p){ return p.versao?p.atividades:paWork(p); }
function paCults(pid){ return PA0.cultivos.filter(c=>c.plano===pid); }
function paByVer(pid){ const m={}; paCults(pid).forEach(c=>{ (m[c.ver]||(m[c.ver]=[])).push(c); }); return m; }
function paApl(pid){ const m=paByVer(pid); const vs=Object.keys(m).map(Number).sort((a,b)=>b-a); if(!vs.length) return '';
  return vs.map((v,i)=>{ const n=m[v].length; return (i===0?(n+(n>1?' cultivos':' cultivo')):String(n))+' na v'+v+(m[v].every(c=>c.ro)?' (safra encerrada)':''); }).join(' e '); }
function paNorm(a){ return JSON.stringify({n:a.nome,o:a.op,g:paGkey(a.g),p:a.prods.map(x=>x.prod+'='+Number(x.dose))}); }
function paDiff(p){ if(!p||!p.rasc) return []; const pub={}; p.atividades.forEach(a=>{ pub[a.id]=a; }); const out=[]; const seen={};
  const pl=(x)=>x.prod+' '+paQ(x.dose)+' '+x.un+'/ha';
  p.rasc.atividades.forEach(a=>{ seen[a.id]=1; const o=pub[a.id];
    if(!o){ out.push({k:'Incluída',c:'g',n:a.nome,t:paGat(a.g).t+' · '+a.op+' · '+(a.prods.length?a.prods.map(pl).join(', '):'só operação')}); return; }
    const ch=[]; if(o.nome!==a.nome) ch.push('nome: '+o.nome+' → '+a.nome); if(paGkey(o.g)!==paGkey(a.g)) ch.push('gatilho: '+paGat(o.g).t+' → '+paGat(a.g).t); if(o.op!==a.op) ch.push('operação: '+o.op+' → '+a.op);
    const om={}; o.prods.forEach(x=>{ om[x.prod]=x; }); const am={}; a.prods.forEach(x=>{ am[x.prod]=x; });
    a.prods.forEach(x=>{ const y=om[x.prod]; if(!y) ch.push('inclui '+pl(x)); else if(Number(y.dose)!==Number(x.dose)) ch.push(x.prod+': '+paQ(y.dose)+' → '+paQ(x.dose)+' '+x.un+'/ha'); });
    o.prods.forEach(y=>{ if(!am[y.prod]) ch.push('retira '+y.prod); });
    if(ch.length) out.push({k:'Alterada',c:'y',n:a.nome,t:ch.join(' · ')}); });
  p.atividades.forEach(o=>{ if(!seen[o.id]) out.push({k:'Excluída',c:'r',n:o.nome,t:paGat(o.g).t+' · '+o.op}); });
  return out; }
// ---------- lista → detalhe (NAV-1 · SEL-02): endereço #plano=<id>, voltar com posição e foco ----------
// endereço: lido ao carregar e no hashchange, gravado ao abrir (replaceState, como a MA da PCM); id inexistente abre a lista, sem erro
function paHashId(h){ const m=/[#&]plano=([^&]*)/.exec(String(h||'')); if(!m||!m[1]) return ''; try{ return decodeURIComponent(m[1]); }catch(e){ return m[1]; } }
function paHashSet(id){ try{ const h=id?'#plano='+encodeURIComponent(id):''; if((location.hash||'')!==h) history.replaceState(null,'',location.pathname+location.search+h); }catch(e){} }
// abrir um plano guarda a posição da biblioteca; ao voltar, a rolagem volta e o foco vai ao cartão aberto por último (ult)
function paOpen(self,id,o){ o=o||{}; const p=paPlan(self,id); if(!p) return;
  if(!self.state.pid){ try{ self.__paPos=[...document.querySelectorAll('main[data-scroll],.ml-tog+div')].map(e=>[e,e.scrollTop]); }catch(e){} }
  if(o.hash!==false) paHashSet(id);
  g2etapa(self,{pid:id,ult:id,del:null,disc:false,flash:null,ied:null,iadd:null,rmv:null,saiAv:null,g2toast:o.msg||('Plano aberto: '+p.nome+(p.rasc?' · rascunho v'+p.rasc.v:''))}); }
function paLista(self,msg){ paHashSet(''); self.__paVolta=true; const patch={pid:null,del:null,disc:false,flash:null,ied:null,iadd:null,rmv:null,saiAv:null}; if(msg) patch.g2toast=msg; self.setState(patch); }
// sair do detalhe com a dose ou a inclusão de insumo digitadas e não concluídas avisa antes de descartar (aceite comum NAV: "formulário
// alterado avisa antes de descartar"); o aviso fica na nota do Próximo passo, ao lado do botão que levou a sair (dano evitado: perder o
// que foi digitado sem saber). A dose aberta sem mudança e a inclusão aberta em branco saem sem aviso.
function paPend(st){ const ad=st.iadd; if(ad&&(String(ad.prod||'').trim()||String(ad.dose||'').trim())) return 'a inclusão de insumo';
  const ed=st.ied; if(ed) return 'a dose de '+ed.prod; return ''; }
function paSair(self,dest){ const pd=paPend(self.state); if(!pd){ if(dest.pid) paOpen(self,dest.pid,{hash:dest.hash}); else paLista(self); return; }
  paHashSet(self.state.pid||''); self.setState({saiAv:{pid:dest.pid||null,o:pd}}); }
function paSaiOk(self){ const d=self.state.saiAv; if(!d) return; self._paEsc=true; self.setState({saiAv:null,ied:null,iadd:null}); if(d.pid) paOpen(self,d.pid); else paLista(self); }
function paSaiNao(self){ self.setState({saiAv:null}); const st=self.state; if(st.ied) paFoco(paDoseId(st.ied.aid,st.ied.prod)); else if(st.iadd) paFoco(st.iadd.prod?('pa-add-dose-'+st.iadd.aid):paAcId('pa-add-'+st.iadd.aid)); }
// Esc no detalhe (sem painel, edição, confirmação, filtro de coluna ou menu sobreposto abertos e fora de campo) volta à lista.
// Fase de bolha, depois de quem fecha a própria camada (painel, filtro da grade e o menu do g2glob chamam preventDefault ou param o
// evento): o Esc fecha só a camada de cima (revisão NAV-1, R6)
function paEsc(self,e){ if(e.key!=='Escape'||e.defaultPrevented||!self.state.pid) return; const st=self.state;
  if(st.fm||st.np||st.ied||st.iadd||st.disc||st.del||st.g2ac||st.saiAv) return; const t=e.target; const vis=(x)=>!!x&&x.getClientRects().length>0;
  if(t&&t.closest&&(t.closest('[role=dialog]')||t.closest('[role=listbox]')||t.closest('[role=menu]')||t.closest('.menu-lat')||/^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName))) return;
  if([...document.querySelectorAll('[role=dialog],[role=listbox],[role=menu]')].some(vis)) return;
  const m=document.querySelector('.menu-lat:not(.rec)'); if(m&&getComputedStyle(m).position==='absolute') return;
  e.preventDefault(); paLista(self); }
function paHashIni(self){ if(self.__paHash) return; self.__paHash=1;
  // trocar o endereço com o painel aberto não troca de plano (o endereço volta; R4); com a dose ou a inclusão digitadas, avisa antes (R8);
  // id inexistente abre a lista com um aviso sem o id interno (R7)
  const aplica=()=>{ let h=''; try{ h=location.hash||''; }catch(e){} let id=paHashId(h); const cur=self.state.pid||''; if(id===cur) return;
    const st=self.state; if(st.fm||st.np){ paHashSet(cur); self.setState({g2toast:'Feche o painel antes de trocar de plano.'}); return; }
    let msg=''; if(id&&!paPlan(self,id)){ msg='Plano do endereço não encontrado (no protótipo, um plano criado aqui não fica guardado ao recarregar): escolha um plano da biblioteca.'; id=''; paHashSet(cur); }
    if(id||cur) paSair(self,{pid:id||null,hash:false}); if(msg) self.setState({g2toast:msg}); };
  setTimeout(aplica,0);
  try{ window.addEventListener('hashchange',aplica); document.addEventListener('keydown',(e)=>paEsc(self,e));
    /* gesto que começa com "Publicar" desabilitado (dose ou inclusão abertas) não publica, mesmo que o botão se habilite no meio do
       clique (o blur da dose grava ao apertar o botão; revisão NAV-1, R1); teclado zera a marca */
    window.addEventListener('pointerdown',(e)=>{ const b=e.target&&e.target.closest&&e.target.closest('[data-acoes] [data-acao=comando]'); self.__paPubDis=!!(b&&b.disabled); },true);
    window.addEventListener('keydown',()=>{ self.__paPubDis=false; },true); }catch(e){} }
// ---------- biblioteca ----------
// Filtro rápido por cultura: "Todas" ou uma cultura; tocar de novo na cultura escolhida volta a "Todas".
const PA_QCH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
function paCulturas(ps){ const cu=[]; ps.forEach(p=>{ if(cu.indexOf(p.cultura)<0) cu.push(p.cultura); }); return cu; }
function paCuf(self,cu){ const f=self.state.cuf||''; return cu.indexOf(f)<0?'':f; }
function paQf(self){ const ps=paPlans(self); const cu=paCulturas(ps); const f=paCuf(self,cu);
  const ch=(t,n,on,go)=>({t:t,n:String(n),on:String(!!on),go:go,st:PA_QCH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  return [ch('Todas',ps.length,!f,()=>self.setState({cuf:''}))].concat(cu.map(c=>ch(c,ps.filter(p=>p.cultura===c).length,f===c,()=>self.setState({cuf:f===c?'':c})))); }
function paLib(self){ const ps=paPlans(self); const cu=paCulturas(ps); const f=paCuf(self,cu); const sel=self.state.ult;
  return cu.filter(c=>!f||c===f).map(c=>{ const cs=ps.filter(p=>p.cultura===c);
    return {t:c, n:cs.length+(cs.length>1?' planos':' plano'), cards:cs.map(p=>{ const atv=paShown(p); const tp=[];
      atv.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
      /* 14/10 (proprietário: "coloque abrir plano na parte de cima do card e elimina da linha para baixo"): sem o rodapé dos cultivos;
         a versão entra no selo, o mesmo texto do cabeçalho do plano */
      const est=p.versao===0?['Rascunho v1','y']:(p.rasc?['Rascunho v'+p.rasc.v+' · v'+p.versao+' em vigor','y']:['Publicado · v'+p.versao,'g']);
      return {nome:p.nome, est:est[0], est_st:paChip(est[1]), natv:String(atv.length), custo:paRS(paCt(atv)),
        gats:tp.map(t=>({t})), semgat:!tp.length,
        st:'display:flex;flex-direction:column;gap:9px;padding:12px 15px;border-radius:12px;text-align:left;font-family:inherit;color:#15201A;min-width:0;width:100%;box-sizing:border-box;cursor:pointer;',
        cur:String(p.id===sel), lab:'Abrir plano '+p.nome, open:()=>paOpen(self,p.id)}; })}; }); }
// ---------- detalhe · filtro rápido por operação: "Todas" ou uma operação; tocar de novo volta a "Todas" ----------
// as operações seguem a ordem do catálogo (PA0.ops); a escolha vale entre planos e cai para "Todas" se o plano não tiver a operação
function paOps(atv){ const tem={}; atv.forEach(a=>{ tem[a.op]=(tem[a.op]||0)+1; }); const ord=PA0.ops.filter(o=>tem[o]).concat(Object.keys(tem).filter(o=>PA0.ops.indexOf(o)<0).sort()); return ord.map(o=>({op:o,n:tem[o]})); }
function paOpf(self,ops){ const f=self.state.opf||''; return ops.some(o=>o.op===f)?f:''; }
// VISOES-2 §3.5 (exemplo "hoje × passa a ser" do proprietário): o tipo da operação vira ícone, o mesmo no chip e na atividade (Lucide, ISC)
function paOpIco(op){ const s=String(op||'').toLowerCase(); const k=/pulveriz|dessec|herbic|fungic|inset/.test(s)?'pulv':(/plant/.test(s)?'plant':(/adub|calag|gess|fertil/.test(s)?'adub':(/semente/.test(s)?'sem':(/colheit/.test(s)?'colh':(/irriga|água|agua/.test(s)?'agua':'outra')))));
  const o={}; ['pulv','plant','adub','sem','colh','agua','outra'].forEach(x=>{ o['io_'+x]=(x===k); }); return o; }
function paOpChips(self,todas,ops,f){
  const ch=(t,n,on,go,lab,op)=>Object.assign({t:t,n:String(n),on:String(!!on),go:go,lab:lab,temIco:!!op,st:PA_QCH+'display:inline-flex;align-items:center;gap:6px;'+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')},paOpIco(op||''));
  return [ch('Todas',todas.length,!f,()=>self.setState({opf:''}),'Mostrar todas as operações')].concat(ops.map(o=>ch(o.op,o.n,f===o.op,()=>self.setState({opf:f===o.op?'':o.op}),(f===o.op?'Mostrar todas as operações':'Mostrar só '+o.op),o.op))); }
// ---------- detalhe · gatilho e atividade na mesma linha; expansão direta dos insumos ----------
function paAtvV(self,p,a,pub){ const xa=self.state.xa||{}; const open=!!xa[a.id]; const del=self.state.del===a.id; const o=pub[a.id];
  let chg=''; if(p.rasc&&p.versao){ if(!o) chg='Nova'; else if(paNorm(o)!==paNorm(a)) chg='Alterada'; }
  const gat=paGat(a.g); const np=a.prods.length; const nv=p.rasc?p.rasc.v:p.versao+1; const fl=self.state.flash===a.id;
  const d0=Number(a.g.dias), gatC=a.g.tipo==='DAP'?((d0<0?'−':'')+Math.abs(d0)):gat.t;   /* só o número: a seção já diz DAP; o texto inteiro fica na dica e no leitor */
  return Object.assign({nome:a.nome, op:a.op, gatilho:gatC, gatlab:gat.t+(gat.full?' · '+gat.full:''), gatilhoFull:gat.full, hasFull:false, detalhesId:'pa-insumos-'+p.id+'-'+a.id, detalhesLab:'Insumos de '+a.nome, np:np?(np+(np>1?' insumos':' insumo')):'Só operação', custo:np?paRS(paCa(a))+'/ha':'—', open, sym:open?'▾':'▸', lab:(open?'Recolher insumos de ':'Mostrar insumos de ')+a.nome,
    tog:()=>{ const n=Object.assign({},self.state.xa||{}); n[a.id]=!open; self.setState({xa:n}); },
    edit:()=>paEdit(self,a.id), rst:fl?'background:#E4F3E9;':'',
    excluir:()=>paDelDesf(self,p.id,a.id),
    rowtog:(e)=>{ const t=e&&e.target; if(t&&t.closest&&t.closest('button,input,a,[role=menu]')) return; const n=Object.assign({},self.state.xa||{}); n[a.id]=!open; self.setState({xa:n}); },
    chg, hasChg:!!chg, chgst:paChip(chg==='Nova'?'g':'y'),
    asking:del, notAsking:!del, ask:()=>self.setState({del:a.id}), no:()=>self.setState({del:null}), yes:()=>paDel(self,p.id,a.id), dlab:'Excluir atividade '+a.nome,
    delmsg:'Excluir “'+a.nome+'”'+(p.versao?' do rascunho v'+nv+'? A v'+p.versao+' publicada e os cultivos que a usam não mudam.':' do rascunho?'),
    semProd:!np, temProd:!!np,
    prods:a.prods.map((x,i)=>paProdV(self,p,a,x,i,(p.rasc&&p.versao&&o)?o:null)) }, paAddV(self,a), paRmvV(self,p,a)); }
// ---------- drill-down editável: dose, retirar e incluir insumo direto na tabela ----------
// grava no rascunho como o formulário (cria a v(n+1) na primeira mudança); o formulário continua para gatilho, operação e nome
const PA_DOSE_ST='font-family:inherit;font-size:12.8px;font-variant-numeric:tabular-nums;text-align:right;width:78px;padding:4px 6px;border-radius:8px;box-sizing:border-box;background:#fff;color:#15201A;';
function paRascNo(ps0,pid,aid,fn){ const ps=paClone(ps0); const p=ps.find(x=>x.id===pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)}; fn(p.rasc.atividades.find(x=>x.id===aid)); const nc=paCults(p.id).length;
  return {ps, novo, v:p.rasc.v, fim:(novo&&p.versao)?(' Rascunho v'+p.rasc.v+' criado; a v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.'):' Gravado no rascunho v'+p.rasc.v+'.'}; }
function paRasc(self,aid,fn){ return paRascNo(paPlans(self),self.state.pid,aid,fn); }
function paFoco(id,sel){ setTimeout(()=>{ const el=document.getElementById(id); if(el){ el.focus(); if(sel&&el.select) el.select(); } },0); }
function paDoseId(aid,prod){ return 'pa-dose-'+aid+'-'+String(prod).replace(/[^A-Za-z0-9]/g,'_'); }
function paDoseIni(self,a,x){ self._paEsc=false; self.setState({ied:{aid:a.id,prod:x.prod,val:paQ(x.dose),err:''},iadd:null}); paFoco(paDoseId(a.id,x.prod),true); }
// Enter ou sair do campo grava; Esc cancela (a marca evita que o blur da saída grave o que foi cancelado). Gravar pela saída do campo
// marca a hora (__paSaiT): um "Publicar" no mesmo gesto é recusado (paPub), porque a pessoa não viu essa dose nas alterações (R1)
function paDoseOk(self,o){ o=o||{}; if(self._paEsc){ self._paEsc=false; return; } const ed=self.state.ied; if(!ed) return; const n=paNum(ed.val);
  if(String(ed.val).trim()===''||isNaN(n)||n<=0){ self.setState({ied:Object.assign({},ed,{err:'Informe a dose por hectare, maior que zero.'})}); return; }
  const a0=paWork(paPlan(self,self.state.pid)).find(y=>y.id===ed.aid); const x0=a0&&a0.prods.find(y=>y.prod===ed.prod);
  if(!x0||Math.abs(x0.dose-n)<1e-9){ self.setState({ied:null}); return; }
  const r=paRasc(self,ed.aid,(a)=>{ const x=a.prods.find(y=>y.prod===ed.prod); if(x) x.dose=n; }); const mud=ed.prod+': '+paQ(x0.dose)+' → '+paQ(n)+' '+x0.un+'/ha';
  if(o.sai){ self.__paSaiT=Date.now(); self.__paSaiTxt=mud; }
  self.setState({pl:r.ps,ied:null,g2toast:'Dose de '+mud+'.'+r.fim}); }
function paProdV(self,p,a,x,i,o){ const ed=self.state.ied; const em=!!ed&&ed.aid===a.id&&ed.prod===x.prod; const x0=o?o.prods.find(y=>y.prod===x.prod):null;
  const marca=(o&&!x0)?'novo':((x0&&Math.abs(x0.dose-x.dose)>1e-9)?'dose alterada':''); const dt=paQ(x.dose)+' '+x.un+'/ha';
  return {grupo:x.grupo, prod:x.prod, dose:dt, preco:paRS(x.preco)+'/'+x.un, custo:paRS(x.dose*x.preco)+'/ha',
    marca, temMarca:!!marca, marcaSt:paChip(marca==='novo'?'g':'y'), marcaT:x0?('Na v'+p.versao+' publicada: '+paQ(x0.dose)+' '+x0.un+'/ha'):'Não existe na v'+p.versao+' publicada',
    lendo:!em, editando:em, dlab:'Alterar a dose de '+x.prod+', hoje '+dt, ini:()=>paDoseIni(self,a,x),
    fid:paDoseId(a.id,x.prod), val:em?ed.val:'', un:x.un+'/ha', ist:PA_DOSE_ST+'border:1px solid '+(em&&ed.err?'#B42318':'#1E7A4C')+';',
    setv:(e)=>self.setState({ied:Object.assign({},self.state.ied,{val:e.target.value,err:''})}),
    tecla:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); paDoseOk(self); } else if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); self._paEsc=true; self.setState({ied:null}); } },
    sai:()=>paDoseOk(self,{sai:true}), err:em?ed.err:'', temErr:em&&!!ed.err,
    tlab:'Retirar '+x.prod+' da atividade '+a.nome, tirar:()=>paTirar(self,a,i) }; }
// retirar não pergunta: vai para o rascunho e o "Desfazer" fica no próprio drill-down
function paTirar(self,a,i){ const x=a.prods[i]; const r=paRasc(self,a.id,(aa)=>{ aa.prods=aa.prods.filter(y=>y.prod!==x.prod); });
  self.setState({pl:r.ps,ied:null,rmv:{pid:self.state.pid,aid:a.id,item:paClone(x),i},g2toast:x.prod+' retirado de '+a.nome+'.'+r.fim}); }
function paVolta(self){ const rm=self.state.rmv; if(!rm) return; const r=paRasc(self,rm.aid,(aa)=>{ if(!aa.prods.some(y=>y.prod===rm.item.prod)) aa.prods.splice(Math.min(rm.i,aa.prods.length),0,rm.item); });
  self.setState({pl:r.ps,rmv:null,g2toast:rm.item.prod+' voltou para a atividade.'}); }
function paRmvV(self,p,a){ const rm=self.state.rmv; const on=!!rm&&rm.pid===p.id&&rm.aid===a.id; return {rmvTem:on, rmvT:on?(rm.item.prod+' retirado desta atividade.'):'', volta:()=>paVolta(self)}; }
function paAcId(chave){ return ('ac-'+chave).replace(/[^A-Za-z0-9_-]/g,'_')+'-in'; }
function paAddIni(self,a){ self.setState({iadd:{aid:a.id,prod:'',dose:'',err:''},ied:null,g2ac:null}); paFoco(paAcId('pa-add-'+a.id)); }
function paAddOk(self,a){ const ad=self.state.iadd; if(!ad) return; const c=PA0.cat[ad.prod]; const n=paNum(ad.dose); let err='';
  if(!ad.prod||!c) err='Escolha o produto.'; else if(a.prods.some(y=>y.prod===ad.prod)) err='Este produto já está na atividade; altere a dose na linha dele.';
  else if(String(ad.dose).trim()===''||isNaN(n)||n<=0) err='Informe a dose por hectare, maior que zero.';
  if(err){ self.setState({iadd:Object.assign({},ad,{err})}); return; }
  const r=paRasc(self,a.id,(aa)=>{ aa.prods.push({grupo:c.grupo,prod:ad.prod,dose:n,un:c.un,preco:c.preco}); });
  self.setState({pl:r.ps,iadd:null,rmv:null,g2toast:ad.prod+' incluído em '+a.nome+': '+paQ(n)+' '+c.un+'/ha.'+r.fim}); }
function paAddV(self,a){ const ad=self.state.iadd; const on=!!ad&&ad.aid===a.id; const c=on?PA0.cat[ad.prod]:null; const n=on?paNum(ad.dose):NaN; const ja={}; a.prods.forEach(y=>{ ja[y.prod]=1; });
  const e=on?ad.err:'';
  // autocompletar do cadastro de produtos: nome, grupo, unidade e preço; o que já está na atividade não aparece
  const itens=Object.keys(PA0.cat).filter(k=>!ja[k]).map(k=>{ const x=PA0.cat[k]; return {v:k, t:k, sub:x.grupo+' · '+x.un+' · '+paRS(x.preco)+'/'+x.un}; });
  const ac=g2ac(self,'pa-add-'+a.id,itens,on?ad.prod:'',(val)=>{ const cur=self.state.iadd; if(!cur) return; self.setState({iadd:Object.assign({},cur,{prod:val,err:''})}); if(val) paFoco('pa-add-dose-'+a.id,true); },
    {ph:'Buscar insumo no cadastro', err:!!e&&!(on&&ad.prod), esc:()=>self.setState({iadd:null})});
  return Object.assign({addOn:on, addOff:!on, addIni:()=>paAddIni(self,a), addLab:'Incluir insumo em '+a.nome, addDoseId:'pa-add-dose-'+a.id,
    addDose:on?ad.dose:'', addUn:c?c.un+'/ha':'/ha', addInfo:c?(paRS(c.preco)+'/'+c.un+((!isNaN(n)&&n>0)?' · '+paRS(n*c.preco)+'/ha':'')):'',
    addSetD:(ev)=>self.setState({iadd:Object.assign({},self.state.iadd,{dose:ev.target.value,err:''})}),
    addTecla:(ev)=>{ if(ev.key==='Enter'){ ev.preventDefault(); paAddOk(self,a); } else if(ev.key==='Escape'){ ev.preventDefault(); ev.stopPropagation(); self.setState({iadd:null}); } },
    addOk:()=>paAddOk(self,a), addNao:()=>self.setState({iadd:null}), addErr:e, addTemErr:!!e,
    addIst:paIst(e&&!!(on&&ad.prod),'84px')+'text-align:right;'}, ac, paOpIco(a.op)); }
function paS2(self,v,p){ const todas=paWork(p); const ops=paOps(todas); const of=paOpf(self,ops); const atv=of?todas.filter(a=>a.op===of):todas; const pub={};
  v.pa_opf=paOpChips(self,todas,ops,of); v.tem_opf=ops.length>1; (p.atividades||[]).forEach(a=>{ pub[a.id]=a; });
  const G={}; atv.forEach(a=>{ const g=paGrp(a.g); const k=paGkey(a.g); const m=G[g]||(G[g]={}); (m[k]||(m[k]={g:a.g,atvs:[]})).atvs.push(a); });
  v.grp=['DAP','DATA','COL'].filter(g=>G[g]).map(g=>{ const list=Object.values(G[g]).sort((A,B)=>{ const a=paOrd(A.g), b=paOrd(B.g);
      if(g==='DATA') return a<b?-1:(a>b?1:0); if(a!==b) return a-b; return A.g.tipo<B.g.tipo?-1:1; });
    const nat=list.reduce((s,t)=>s+t.atvs.length,0), tot=list.reduce((s,t)=>s+t.atvs.reduce((s2,a)=>s2+(a.prods.length?paCa(a):0),0),0);
    /* "8 atividades" e o custo por ha da seção, à direita e alinhado aos custos; gatilhos só quando diferem das atividades */
    return {t:PA_GRP[g].t, d:PA_GRP[g].d, n:nat+(nat>1?' atividades':' atividade')+(list.length!==nat?' · '+list.length+(list.length>1?' gatilhos':' gatilho'):''), tot:paRS(tot)+'/ha',
      gats:list.map(t=>({atvs:t.atvs.map(a=>paAtvV(self,p,a,pub))}))}; });
  v.vazio=!todas.length; v.tem_atv=!!todas.length;
  const u=self.state.paUndo; v.pa_undo=!!(u&&u.pid===p.id); v.pa_undo_t=u?u.t:''; v.pa_desfaz=()=>paDesfaz(self);
  v.x_all=()=>{ const xa={}; atv.forEach(a=>{ xa[a.id]=true; }); self.setState({xg:{},xa}); };
  v.x_none=()=>self.setState({xa:{}});
  // um só botão: "Expandir tudo" até todas as atividades visíveis estarem abertas; aí vira "Recolher tudo"
  const xa0=self.state.xa||{}; const todasAb=atv.length>0&&atv.every(a=>xa0[a.id]); v.x_lab=todasAb?'Recolher tudo':'Expandir tudo'; v.x_tog=todasAb?v.x_none:v.x_all; v.x_up=todasAb; v.x_down=!todasAb;
  // 14/10 (Versões saiu do detalhe): com rascunho, o selo diz também a versão que segue valendo para as O.S.
  const est=p.versao===0?['Rascunho v1 · ainda não publicado','y']:(p.rasc?['Rascunho v'+p.rasc.v+' · v'+p.versao+' em vigor','y']:['Publicado · v'+p.versao,'g']);
  v.p_nome=p.nome; v.p_est=est[0]; v.p_est_st=paChip(est[1]);
  const tp=[]; todas.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
  v.k2=p.cultura+' · '+todas.length+(todas.length===1?' atividade':' atividades')+' · '+paRS(paCt(todas))+'/ha de insumos'+(tp.length?' · gatilhos: '+tp.join(', '):'');
  const apl=paApl(p.id); const nd=paDiff(p).length; const nv=p.rasc?p.rasc.v:p.versao+1;
  v.ban_r=!!p.rasc;
  v.ed_show=p.versao>0&&!p.rasc; v.ed_t='Editar cria o rascunho v'+(p.versao+1)+'; a v'+p.versao+' publicada e os cultivos que a usam não mudam.';   // estado sempre visível (PRD 4.2)
  if(p.versao===0) v.ban_t='Rascunho v1 · ainda não publicado. Publique a versão v1 para poder aplicar em Planejar safra.';
  else if(p.rasc) v.ban_t='Rascunho v'+p.rasc.v+' · '+nd+(nd===1?' alteração não publicada. ':' alterações não publicadas. ')+(apl?'Aplicado em '+apl+' — não serão alterados.':'Nenhum cultivo usa este plano.');
  v.disc=!!self.state.disc&&!!p.rasc; v.nodisc=!v.disc;
  v.disc_t=p.versao?('Descartar o rascunho v'+(p.rasc?p.rasc.v:'')+' e suas '+nd+' alterações? A v'+p.versao+' publicada continua valendo.'):'Descartar este plano novo? Ele ainda não foi publicado e será removido da biblioteca.';
  v.disc_ask=()=>self.setState({disc:true}); v.disc_no=()=>self.setState({disc:false}); v.disc_yes=()=>paDiscard(self,p.id);
}
// descartar: plano novo (v0) sai da biblioteca; plano publicado perde só o rascunho e continua na versão em vigor
function paDescartaNo(ps0,pid){ const ps=paClone(ps0); const i=ps.findIndex(x=>x.id===pid); const p=ps[i]; if(!p||!p.rasc) return {ps:ps0,erro:'Sem rascunho para descartar.'};
  if(p.versao===0){ ps.splice(i,1); return {ps,saiu:true,msg:'Plano novo descartado: '+p.nome+'.'}; }
  const v=p.rasc.v; p.rasc=null; return {ps,saiu:false,msg:'Rascunho v'+v+' descartado. A v'+p.versao+' publicada continua valendo.'}; }
function paDiscard(self,pid){ const r=paDescartaNo(paPlans(self),pid); if(r.erro) return; self.setState({pl:r.ps,disc:false,paUndo:null});
  if(r.saiu) paLista(self,r.msg); else self.setState({g2toast:r.msg}); }
function paDel(self,pid,aid){ const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)}; const a=p.rasc.atividades.find(x=>x.id===aid); p.rasc.atividades=p.rasc.atividades.filter(x=>x.id!==aid);
  self.setState({pl:ps,del:null,g2toast:'“'+a.nome+'” excluída do rascunho v'+p.rasc.v+(novo&&p.versao?' (criado agora)':'')+'.'+(p.versao?' A v'+p.versao+' publicada não muda.':'')}); }
// VISOES-2 §3.5/§8.6: excluir do rascunho sem janela de confirmação, com "Desfazer" por 5 s (o rascunho também pode ser descartado inteiro)
function paDelDesf(self,pid,aid){ const ps0=paPlans(self), p0=ps0.find(x=>x.id===pid), lista=paWork(p0), idx=lista.findIndex(x=>x.id===aid); if(idx<0) return;
  const atv=paClone(lista[idx]), tinhaRasc=!!p0.rasc, tok=Date.now();
  paDel(self,pid,aid); self.setState({pam:null,paUndo:{pid,atv,idx,tinhaRasc,tok,t:'“'+atv.nome+'” excluída do rascunho.'}});
  setTimeout(()=>{ if(self.state.paUndo&&self.state.paUndo.tok===tok) self.setState({paUndo:null}); },5000); }
/* Desfazer volta SÓ a atividade excluída ao rascunho de agora, na posição dela, preservando o que mudou depois (Codex PA-DESFAZER-01, S2:
   antes, "a exclusão criou o rascunho" apagava o rascunho inteiro e levava junto uma dose alterada depois). O rascunho só sai quando,
   com a atividade de volta, ficou igual à versão publicada. Rascunho descartado ou publicado na janela: o recibo vale mais nada. */
function paDesfaz(self){ const u=self.state.paUndo; if(!u) return; const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===u.pid);
  if(!p||!p.rasc||p.rasc.atividades.some(x=>x.id===u.atv.id)){ self.setState({paUndo:null}); return; }
  p.rasc.atividades.splice(Math.min(u.idx,p.rasc.atividades.length),0,u.atv);
  if(!u.tinhaRasc&&p.versao&&p.rasc.atividades.length===p.atividades.length&&p.rasc.atividades.every((x,i)=>p.atividades[i]&&x.id===p.atividades[i].id&&paNorm(x)===paNorm(p.atividades[i]))) delete p.rasc;
  self.setState({pl:ps,paUndo:null,flash:u.atv.id,g2toast:'“'+u.atv.nome+'” voltou ao plano.'});
  setTimeout(()=>{ const b=[...document.querySelectorAll('main button.pa-titulo')].find(x=>x.innerText.trim()===u.atv.nome); if(b) b.focus(); },60); }
// ---------- formulário lateral da atividade ----------
function paEdit(self,aid){ const p=paPlan(self,self.state.pid); if(!p) return; const a=aid?paWork(p).find(x=>x.id===aid):null;
  // DAP negativo abre como "Dias antes do plantio" com o número positivo: o sentido fica no tipo, nunca no sinal
  const antes=!!a&&a.g.tipo==='DAP'&&Number(a.g.dias)<0;
  const d=a?{op:a.op,nome:a.nome,outra:(PA0.atvs[a.op]||[]).indexOf(a.nome)<0,tipo:(antes?'DAPA':a.g.tipo),dias:(a.g.tipo==='DATA'?'':String(Math.abs(Number(a.g.dias)))),data:(a.g.data||'')}
           :{op:paOpf(self,paOps(paWork(p))),nome:'',outra:false,tipo:'DAP',dias:'',data:''};
  self.setState({fm:{pid:p.id,aid:aid||null,draft:d,orig:JSON.stringify(d),errs:{},warn:false,rm:null},del:null,ied:null,iadd:null}); paFoco('fm_op'); }
function paFmUpd(self,patch,errk){ const cur=self.state.fm; const nd=Object.assign({},cur.draft,patch); const ne=Object.assign({},cur.errs||{}); (errk||Object.keys(patch)).forEach(k=>{ delete ne[k]; });
  self.setState({fm:Object.assign({},cur,{draft:nd,errs:ne,warn:false})}); }
function paIst(err,w){ return 'font-family:inherit;font-size:14px;padding:8px 10px;border-radius:10px;box-sizing:border-box;'+(w?'width:'+w+';':'width:100%;')+'border:1px solid '+(err?'#B42318':'#E4E9E5')+';background:#fff;color:#15201A;'; }
function paFm(self,v){ const fm=self.state.fm; v.fm_open=!!fm; if(!fm) return; const p=paPlan(self,self.state.pid); const a0=(p&&fm.aid)?paWork(p).find(x=>x.id===fm.aid):null;
  /* o painel vale só para o plano e a atividade em que foi aberto: se não existem mais aqui, fecha sem gravar (R4) */
  if(!p||fm.pid!==p.id||(fm.aid&&!a0)){ v.fm_open=false; setTimeout(()=>{ if(self.state.fm===fm) self.setState({fm:null}); },0); return; } const d=fm.draft; const er=fm.errs||{};
  const nv=p.rasc?p.rasc.v:p.versao+1; const nc=paCults(p.id).length;
  v.fm_titulo=a0?('Atividade · '+a0.nome):'Nova atividade'; v.fm_savet=a0?'Salvar':'Incluir atividade';
  v.fm_sub=p.nome+' · salvar grava no rascunho v'+nv+(p.versao?('; a v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.'):'.');
  v.fm_tipos=PA_TIPOS; v.fm_tipo=d.tipo; v.fm_settipo=(e)=>paFmUpd(self,{tipo:e.target.value},['g']);
  v.fm_isData=d.tipo==='DATA'; v.fm_isDias=d.tipo!=='DATA';
  v.fm_dias=d.dias; v.fm_setdias=(e)=>paFmUpd(self,{dias:e.target.value},['g']); v.fm_data=d.data; v.fm_setdata=(e)=>paFmUpd(self,{data:e.target.value},['g']);
  v.fm_diasl={DAPA:'dias antes do plantio',DAP:'dias após o plantio',DANC:'dias antes da colheita',DAPC:'dias após a colheita'}[d.tipo]||'dias';
  v.fm_ghelp=(d.tipo==='DAP'||d.tipo==='DAPA')?'Zero é o dia do plantio. Todos os produtos da atividade herdam este gatilho.':(d.tipo==='DATA'?'Data fixa do calendário. Todos os produtos da atividade herdam este gatilho.':'Contado a partir da colheita do cultivo. Todos os produtos da atividade herdam este gatilho.');
  v.fm_eg=er.g||''; v.fm_heg=!!er.g; v.fm_gst=paIst(er.g,'96px'); v.fm_tst=paIst(false,'230px'); v.fm_dst=paIst(er.g,'170px');
  v.fm_nome=d.nome; v.fm_setnome=(e)=>paFmUpd(self,{nome:e.target.value}); v.fm_en=er.nome||''; v.fm_hen=!!er.nome; v.fm_nst=paIst(er.nome);
  v.fm_ops=[{v:'',t:'Escolha a operação'}].concat(PA0.ops.map(o=>({v:o,t:o}))); v.fm_op=d.op; v.fm_eo=er.op||''; v.fm_heo=!!er.op; v.fm_ost=paIst(er.op);
  v.fm_setop=(e)=>{ const op=e.target.value; const cur=self.state.fm.draft; const keep=!!op&&(cur.outra||(PA0.atvs[op]||[]).indexOf(cur.nome)>=0); paFmUpd(self,{op,nome:keep?cur.nome:'',outra:keep&&!!cur.outra},['op','nome']); };
  const lst=PA0.atvs[d.op]||[];
  v.fm_atvs=[{v:'',t:(d.op?'Escolha a atividade':'Escolha a operação primeiro')}].concat(lst.map(o=>({v:o,t:o}))).concat(d.op?[{v:'__outra',t:'Outra atividade…'}]:[]);
  v.fm_atv=d.outra?'__outra':(lst.indexOf(d.nome)>=0?d.nome:''); v.fm_atvdis=!d.op; v.fm_outra=!!d.outra;
  v.fm_ast=paIst(er.nome&&!d.outra)+(d.op?'':'background:#F4F6F3;color:#8A968E;');
  v.fm_setatv=(e)=>{ const x=e.target.value; if(x==='__outra') paFmUpd(self,{outra:true,nome:''},['nome']); else paFmUpd(self,{outra:false,nome:x},['nome']); };
  // insumos e doses ficam só na tabela da atividade; aqui só o resumo, para quem procurar
  v.fm_temIns=!!a0; v.fm_nova=!a0; v.fm_ins=a0?(a0.prods.length?(a0.prods.length+(a0.prods.length>1?' insumos':' insumo')+' · '+paRS(paCa(a0))+'/ha'):'Só operação, sem insumos'):'';
  v.fm_warn=!!fm.warn; v.fm_nerr=Object.keys(er).length>0;
  v.fm_close=()=>{ const cur=self.state.fm; if(JSON.stringify(cur.draft)!==cur.orig){ self.setState({fm:Object.assign({},cur,{warn:true})}); return; } self.setState({fm:null}); };
  v.fm_discard=()=>self.setState({fm:null}); v.fm_keep=()=>self.setState({fm:Object.assign({},self.state.fm,{warn:false})});
  v.fm_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.fm_close(); } };
  v.fm_save=()=>paSave(self); }
// número com sinal: g2num descarta o menos tipográfico (−, –, —), que a lista mostra em 'DAP −20'; aqui ele conta como negativo
function paNum(s){ const n=g2num(s); return (!isNaN(n)&&/[\u2010-\u2015\u2212\uFE63\uFF0D]/.test(String(s)))?-Math.abs(n):n; }
function paSave(self){ const fm=self.state.fm; const d=fm.draft; const er={}; let dias=null, data=null;
  if(d.tipo==='DATA'){ if(!d.data) er.g='Informe a data.'; else data=d.data; }
  else { const n=paNum(d.dias); const antes=(d.tipo==='DAPA'||d.tipo==='DANC'); const lim=antes?180:400;
    if(String(d.dias).trim()===''||isNaN(n)) er.g='Informe os dias (número inteiro).'; else if(Math.round(n)!==n) er.g='Use um número inteiro de dias.';
    else if(n<0) er.g='Use zero ou mais: o sentido já está no tipo.'; else if(n>lim) er.g='Use de 0 a '+lim+' dias.'; else dias=((d.tipo==='DAPA'&&n>0)?-n:n); }
  if(!String(d.nome||'').trim()) er.nome=d.outra?'Informe o nome da nova atividade.':(d.op?'Escolha a atividade.':'Escolha a operação e depois a atividade.');
  if(!d.op) er.op='Escolha a operação.';
  if(fm.pid!==self.state.pid){ self.setState({fm:null,g2toast:'O painel era de outro plano: nada foi gravado.'}); return; }
  const a0=fm.aid?paWork(paPlan(self,self.state.pid)).find(x=>x.id===fm.aid):null; const prods=a0?paClone(a0.prods):[];
  if(fm.aid&&!a0){ self.setState({fm:null,g2toast:'A atividade não existe mais neste plano: nada foi gravado.'}); return; }
  if(Object.keys(er).length){ self.setState({fm:Object.assign({},fm,{errs:er,warn:false})}); return; }
  const atv={id:fm.aid||('n'+Date.now().toString(36)),nome:String(d.nome).trim(),op:d.op,g:{tipo:(d.tipo==='DAPA'?'DAP':d.tipo),dias,data},prods};
  /* salvar sem mudar nada não cria rascunho (seria um rascunho igual à versão publicada; revisão NAV-1, R3) */
  if(a0&&paNorm(atv)===paNorm(a0)){ self.setState({fm:null,g2toast:'Nada mudou em “'+a0.nome+'”: o plano continua como estava.'}); return; }
  const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===self.state.pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)};
  const L=p.rasc.atividades; const ix=L.findIndex(a=>a.id===fm.aid); if(ix>=0) L[ix]=atv; else L.push(atv);
  const xg=Object.assign({},self.state.xg||{}); xg[paGkey(atv.g)]=true; const xa=Object.assign({},self.state.xa||{}); xa[atv.id]=true;
  const nc=paCults(p.id).length;
  const msg=(novo&&p.versao)?('Rascunho v'+p.rasc.v+' criado com a alteração. A v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.')
                            :((fm.aid?'Atividade salva':'Atividade incluída')+' no rascunho v'+p.rasc.v+'.');
  // atividade nova: abre na lista com "Incluir insumo" pronto; se o filtro por operação a esconderia, volta a "Todas"
  const nova=!fm.aid; const opf=self.state.opf||'';
  self.setState({pl:ps,fm:null,xg,xa,flash:atv.id,g2toast:msg+(nova?' Inclua os insumos na tabela.':''),opf:(opf&&opf!==atv.op)?'':opf,
    iadd:nova?{aid:atv.id,prod:'',dose:'',err:''}:null,ied:null,g2ac:null});
  if(nova) paFoco(paAcId('pa-add-'+atv.id)); }
// ---------- novo plano ----------
// o painel recebe o foco no 1º campo ao abrir (Esc fecha; ao fechar, o foco volta a quem abriu: g2lib, painel modal)
function paNewPlan(self){ const d={nome:'',cultura:paCuf(self,paCulturas(paPlans(self))),base:''}; self.setState({np:{draft:d,orig:JSON.stringify(d),errs:{},warn:false}}); paFoco('np_nome'); }
function paNp(self,v){ const np=self.state.np; v.np_open=!!np; v.np_titulo='Novo plano'; v.np_sub='O plano nasce como rascunho v1; publique a versão para aplicar em Planejar safra.'; v.np_savet='Criar plano'; if(!np) return; const d=np.draft; const er=np.errs||{};
  const upd=(patch)=>{ const cur=self.state.np; const ne=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>{ delete ne[k]; }); self.setState({np:Object.assign({},cur,{draft:Object.assign({},cur.draft,patch),errs:ne,warn:false})}); };
  v.np_nome=d.nome; v.np_setnome=(e)=>upd({nome:e.target.value}); v.np_en=er.nome||''; v.np_hen=!!er.nome; v.np_nst=paIst(er.nome);
  v.np_cults=[{v:'',t:'Escolha a cultura'}].concat(PA0.culturas.map(c=>({v:c,t:c}))); v.np_cult=d.cultura; v.np_setcult=(e)=>upd({cultura:e.target.value,base:''}); v.np_ec=er.cultura||''; v.np_hec=!!er.cultura; v.np_cst=paIst(er.cultura);
  const bs=paPlans(self).filter(p=>p.cultura===d.cultura&&p.versao>0);
  v.np_bases=[{v:'',t:'Começar em branco'}].concat(bs.map(p=>({v:p.id,t:'Copiar atividades de '+p.nome+' v'+p.versao}))); v.np_base=d.base; v.np_setbase=(e)=>upd({base:e.target.value}); v.np_hasbase=!!d.cultura; v.np_bst=paIst(false);
  v.np_warn=!!np.warn; v.np_nerr=Object.keys(er).length>0;
  v.np_close=()=>{ const cur=self.state.np; if(JSON.stringify(cur.draft)!==cur.orig){ self.setState({np:Object.assign({},cur,{warn:true})}); return; } self.setState({np:null}); };
  v.np_discard=()=>self.setState({np:null}); v.np_keep=()=>self.setState({np:Object.assign({},self.state.np,{warn:false})});
  v.np_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.np_close(); } };
  v.np_save=()=>{ const cur=self.state.np; const dd=cur.draft; const e=paNovoErro(paPlans(self),dd);
    if(Object.keys(e).length){ self.setState({np:Object.assign({},cur,{errs:e,warn:false})}); return; }
    const r=paNovoFaz(paPlans(self),dd,'NP'+Date.now().toString(36));
    self.setState({pl:r.ps,np:null,xg:{},xa:{}});
    paOpen(self,r.id,{msg:'Plano “'+r.nome+'” criado como rascunho v1'+(r.base?' a partir de '+r.base.nome+' v'+r.base.versao:'')+'. Ajuste as atividades e publique a versão v1.'}); }; }
// regras do novo plano (puras, testadas em pa_regras_test.py): nome obrigatório e único por cultura (sem diferenciar maiúsculas); cópia só das atividades
function paNovoErro(ps,dd){ const e={}; const nome=String(dd.nome||'').trim();
  if(!nome) e.nome='Informe o nome do plano.'; else if(ps.some(p=>p.cultura===dd.cultura&&p.nome.toLowerCase()===nome.toLowerCase())) e.nome='Já existe um plano com este nome nesta cultura.';
  if(!dd.cultura) e.cultura='Escolha a cultura.'; return e; }
function paNovoFaz(ps,dd,id){ const nome=String(dd.nome||'').trim(); const base=dd.base?(ps.find(p=>p.id===dd.base)||null):null;
  const atv=base?paClone(base.atividades).map((a,i)=>Object.assign(a,{id:id+'_'+i})):[];
  return {id,nome,base,ps:ps.concat([{id,nome,cultura:dd.cultura,versao:0,atividades:[],rasc:{v:1,atividades:atv},hist:[]}])}; }
// ---------- publicar ----------
// Próximo passo do detalhe (BOT-01/02): "Publicar versão vN" só com rascunho; sem rascunho, nenhuma primária. Desabilitado com o
// motivo (VIS-04) quando publicar sairia diferente do que a pessoa vê (a versão publicada é imutável):
// - sem atividade;
// - com a dose em edição (R1/R2: a dose digitada e não confirmada não aparece nas alterações);
// - com a inclusão de insumo aberta (o insumo que está sendo digitado ficaria de fora);
// - com o rascunho igual à versão publicada (R3: uma versão vazia marcaria os cultivos como desatualizados sem mudança nenhuma).
// Habilitado, a nota resume as alterações ao lado do botão (paResumo).
// 14/10/2026 (proprietário: "tire essa parte de alterações de rascunho. lá embaixo deixe o botão salvar (as mudanças)"): a primária é
// "Salvar alterações" (cria a versão vN, imutável; os cultivos não mudam) e, habilitada, vem sem nota; o que mudou fica na própria
// atividade (selo Alterada/Incluída) e no aviso depois de salvar. Desabilitada, segue com o motivo (VIS-04).
function paAcoes(p,ui){ ui=ui||{}; if(!p||!p.rasc) return {prim:null,nota:''}; const v=p.rasc.v; const t='Salvar alterações';
  const no=(w)=>({prim:{t,dis:w},nota:w});
  if(!p.rasc.atividades.length) return no('Inclua ao menos uma atividade para salvar.');
  if(ui.ied) return no('Confirme (Enter) ou cancele (Esc) a dose de '+ui.ied.prod+' para salvar.');
  if(ui.iadd) return no('Conclua ou cancele a inclusão do insumo para salvar.');
  if(p.versao>0&&!paDiff(p).length) return no('O rascunho v'+v+' está igual à v'+p.versao+': altere algo ou descarte o rascunho.');
  return {prim:{t,dis:''},nota:''}; }
// resumo das alterações na nota do Próximo passo, ao lado de "Publicar" (R1): até 2 itens e "e mais N"; o bloco "Alterações" tem todas,
// o custo e o impacto nos cultivos
function paResumo(p){ const d=paDiff(p); if(!p||!p.rasc||!d.length) return ''; const n=d.length;
  if(!p.versao) return 'A v'+p.rasc.v+' publica '+n+(n>1?' atividades.':' atividade.');
  const it=d.map(x=>x.k==='Alterada'?(x.n+' ('+x.t+')'):((x.k==='Incluída'?'inclui ':'exclui ')+x.n));
  return n+(n>1?' alterações':' alteração')+' na v'+p.rasc.v+': '+it.slice(0,2).join('; ')+(n>2?'; e mais '+(n-2):'')+'.'; }
// publicar (puro): a versão do rascunho vira a vigente e entra no histórico; os cultivos (PA0.cultivos) não mudam (PRD 40.3)
function paPubFaz(ps0,pid,hoje){ const ps=paClone(ps0); const p=ps.find(x=>x.id===pid); if(!p||!p.rasc) return {erro:'Sem rascunho para publicar.'};
  const w=paAcoes(p).prim.dis; if(w) return {erro:w};
  p.versao=p.rasc.v; p.atividades=p.rasc.atividades; p.rasc=null; p.hist=[{v:p.versao,at:hoje}].concat(p.hist||[]); return {ps,p}; }
// clique em "Publicar" (R1): recusa se o gesto começou com o botão desabilitado (__paPubDis) ou se a saída do campo acabou de gravar uma
// dose (__paSaiT, até 1 s: o mesmo clique). A dose fica no rascunho e aparece na nota; a pessoa confere e clica de novo
const PA_SAI_MS=1000;
function paPubAgora(self,agora){ const tarde=!self.__paSaiT||(agora-self.__paSaiT)>=PA_SAI_MS; if(!self.__paPubDis&&tarde) return '';
  const txt=self.__paSaiTxt; self.__paPubDis=false; self.__paSaiT=0; self.__paSaiTxt='';
  return (txt?'A dose de '+txt+' entrou no rascunho agora':'O rascunho mudou neste clique')+': confira e clique em Salvar alterações de novo.'; }
function paPub(self){ const pid=self.state.pid; const st=self.state; const ac=paAcoes(paPlan(self,pid),{iadd:!!st.iadd,ied:st.ied}); if(!ac.prim||ac.prim.dis) return;
  const ag=paPubAgora(self,Date.now()); if(ag){ self.setState({g2toast:ag}); return; }
  const res=paResumo(paPlan(self,pid)); const r=paPubFaz(paPlans(self),pid,PA0.hoje); if(r.erro){ self.setState({g2toast:r.erro}); return; } const apl=paApl(pid);
  /* o aviso diz o que foi salvo (o bloco de alterações saiu) e que os cultivos não mudam */
  self.setState({pl:r.ps,disc:false,del:null,paUndo:null,g2toast:'Alterações salvas na v'+r.p.versao+'. '+(res&&r.p.versao>1?res+' ':'')+(apl?'Os cultivos continuam como estavam ('+apl+'); a troca de versão é por cultivo, no Planejar safra. ':'')+PA_PROTO});
  /* o comando sai da tela com o rascunho: o foco vai ao nome do plano (o aviso diz que os cultivos continuam como estavam) */
  setTimeout(()=>{ try{ const h=document.getElementById('pa-det-tit'); if(h){ h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); h.scrollIntoView({block:'start'}); } }catch(e){} },40); }
// R5: a troca de versão por cultivo (PRD 40.3) ainda não existe no Planejar safra do protótipo, e a PA não grava no cenário: o texto
// diz isso em vez de prometer a adoção (pendência da frente Planejar safra, docs/navegacao/ESPECIFICACAO.md §4)
const PA_PROTO='No protótipo, a versão publicada aqui ainda não chega ao Planejar safra.';
// situação do cultivo no plano (X-AGR-6): versão aplicada × publicada; o link abre o próprio cultivo no Planejar safra
function paSitCult(c,p){ const lk=(!c.ro&&c.ver<p.versao)?[{k:'link',t:'Abrir cultivo no Planejar safra ›',h:'SAF.dc.html#saf='+c.safra+'&passo=cultivos&cult='+c.id}]:[];
  if(c.ro) return [{k:'chip',t:'Safra encerrada · fica na v'+c.ver,c:'gray'}];
  if(p.rasc) return [{k:'chip',t:'Continua na v'+c.ver+' ao publicar',c:'yellow'}].concat(lk);
  if(c.ver<p.versao) return [{k:'chip',t:'Na v'+c.ver+' · v'+p.versao+' publicada',c:'yellow'}].concat(lk);
  return [{k:'chip',t:'Na versão em vigor',c:'green'}]; }
// ---------- detalhe · com rascunho, as alterações acima do Próximo passo ----------
function paDet(self,v,p){ const nd=paDiff(p); v.alt_tem=!!p.rasc;
  v.dif=nd.map(d=>({k:d.k,st:paChip(d.c),n:d.n,t:d.t})); v.dif_vazio=!!p.rasc&&!nd.length;
  const nv=p.rasc?p.rasc.v:p.versao;
  v.dif_tit=p.versao?('Alterações do rascunho v'+nv+' em relação à v'+p.versao):'Primeira versão do plano (v1)';
  const c0=paCt(p.atividades), c1=p.rasc?paCt(p.rasc.atividades):c0, dl=c1-c0;
  v.dif_custo=p.versao?('Custo de insumos: '+paRS(c0)+'/ha na v'+p.versao+' → '+paRS(c1)+'/ha na v'+nv+(Math.abs(dl)>0.004?' ('+(dl>0?'+':'−')+paRS(Math.abs(dl))+'/ha)':' (sem mudança)')):('Custo de insumos: '+paRS(c1)+'/ha');
  const apl=paApl(p.id);
  v.imp=apl?('Aplicado em '+apl+': publicar não os altera; a troca de versão é por cultivo, no Planejar safra.'):'Nenhum cultivo usa este plano; publicar não altera nenhuma safra.';
  v.imp_st='padding:9px 12px;border-radius:10px;font-size:12.8px;font-weight:700;'+(apl?'background:#FFF3D6;color:#8A5A00;':'background:#EEF1EE;color:#5B6660;');
  v.tem_cv=paCults(p.id).length>0; v.cv_vazio=!v.tem_cv; v.imp_cv=v.tem_cv&&!p.rasc;
  const bv=paByVer(p.id);
  v.hist=(p.rasc?[{t:'v'+p.rasc.v,at:'rascunho em edição',st:'Rascunho',stst:paChip('y'),uso:'—'}]:[]).concat((p.hist||[]).map(h=>{ const u=(bv[h.v]||[]).length;
    return {t:'v'+h.v, at:'publicada em '+h.at, st:(h.v===p.versao?'Em vigor':'Substituída'), stst:paChip(h.v===p.versao?'g':'n'), uso:u?(u+(u>1?' cultivos':' cultivo')):'nenhum cultivo'}; }));
  const np=(p.hist||[]).length; const vig=(p.hist||[]).find(h=>h.v===p.versao);
  v.hist_res=(p.versao?('v'+p.versao+' em vigor'+(vig&&vig.at!=='—'?' desde '+vig.at:'')):'Nenhuma versão publicada')+(p.rasc?' · rascunho v'+p.rasc.v+' em edição':'')+(np?' · '+np+(np>1?' versões publicadas':' versão publicada'):'');
  v.hist_open=!!self.state.histOpen; v.hist_sym=v.hist_open?'▾':'▸'; v.hist_lab=(v.hist_open?'Recolher':'Mostrar')+' as versões do plano';
  v.hist_tog=()=>self.setState({histOpen:!self.state.histOpen}); }
function PREVALS(self,v){ const G=GRIDS.find(g=>g.id==='g_cv'); if(!G) return; const pid=self.state.pid; const p=pid?paPlan(self,pid):null;
  G.rows=p?paCults(pid).map(c=>{ const sit=paSitCult(c,p);
    return {id:c.id,ro:true,v:{saf:c.safraNome,local:c.local,cult:c.cultura+' '+c.variedade,area:c.area,ver:'v'+c.ver},s:{sit:sit[0].t},p:{local:[{k:'b',t:c.local}],ver:[{k:'tag',t:'v'+c.ver}],sit}}; }):[]; }
function EXTRAVALS(self,v){ paHashIni(self); const st=self.state; const pid=st.pid||null; const p=pid?paPlan(self,pid):null;
  v.lista=!p; v.det=!!p;
  v.lib=paLib(self); v.pa_qf=paQf(self);
  // volta à lista: a rolagem volta à posição guardada e o foco vai ao cartão aberto por último (sem ele, ao "Criar plano")
  if(!p&&self.__paVolta){ const pos=self.__paPos||[]; self.__paVolta=false; self.__paPos=null; setTimeout(()=>{ try{ pos.forEach(([e,t])=>{ e.scrollTop=t; }); const c=document.querySelector('main .g2card[aria-current=true]')||document.querySelector('header [data-acao=criar]'); if(c){ if(c.classList.contains('g2card')) c.scrollIntoView({block:'nearest'}); c.focus({preventScroll:true}); } }catch(e){} },0); }
  v.ctx_pl=p?(p.nome+' · '+(p.rasc?'rascunho v'+p.rasc.v:'v'+p.versao)):'Biblioteca · '+paPlans(self).length+' planos';
  if(p){ paS2(self,v,p); paDet(self,v,p); } else { v.grp=[]; v.dif=[]; v.hist=[]; v.pa_opf=[]; }
  paFm(self,v); paNp(self,v);
  // Criar plano (lista, cabeçalho) e Incluir atividade (bloco Atividades) são as entradas dos painéis; Publicar é o Próximo passo do detalhe
  v.pa_novo=()=>paNewPlan(self); v.pa_incl=()=>paEdit(self,null);
  let A={}; const ac=p?paAcoes(p,{iadd:!!st.iadd,ied:st.ied}):null; const sa=(p&&st.saiAv&&paPend(st))?st.saiAv:null;
  if(p){ A={volta:{t:'‹ Biblioteca de planos',fn:()=>paSair(self,{pid:null}),a:'voltar'},nota:ac.nota,prim:ac.prim?{t:ac.prim.t,fn:()=>paPub(self),a:'comando'}:null};
    /* aviso de saída (R8) no lugar da nota, ao lado do botão que levou a sair; sem ele, com alterações, o atalho para o bloco completo */
    if(sa){ const pd=paPend(st); const pp=sa.pid?paPlan(self,sa.pid):null; A.nota=pd.charAt(0).toUpperCase()+pd.slice(1)+' não foi concluída: o que foi digitado se perde ao sair.';
      A.lnks=[{t:pp?'Descartar e abrir '+pp.nome:'Descartar e voltar à biblioteca',fn:()=>paSaiOk(self)},{t:'Continuar editando',fn:()=>paSaiNao(self)}]; A.decide=true; }   // decisão do momento: fica à vista
  }
  if(ac&&ac.prim&&ac.prim.dis) A.decide=true;   // principal travado: o motivo fica à vista (estado sempre visível, PRD 4.3)
  g2acoes(v,'aa',A); v.aa_pdis=!!(ac&&ac.prim&&ac.prim.dis); v.aa_pwhy=(ac&&ac.prim&&ac.prim.dis)||''; }
'''


def bloco(titulo, desc, corpo, acao='', hole=False):
    if not hole: desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    t = titulo if hole else esc(titulo)
    d = desc if hole else esc(desc)
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{d}</div></div>{acao}</div>'
            f'<div style="padding: 0 16px 14px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')


def aside(pre, titulo_hole, sub_hole, corpo, w=560):
    """Painel lateral pela direita com Cancelar e o verbo do efeito (BOT-02: {pre}_savet, ex.: "Incluir atividade", "Criar plano", "Salvar")
    e aviso de alterações não salvas (holes: {pre}_open/_close/_key/_save/_savet/_warn/_discard/_keep/_nerr)."""
    return IF(f'{pre}_open',
        f'<div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
        f'<button type="button" aria-label="Fechar" onClick="{H(pre+"_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
        f'<aside role="dialog" aria-label="{H(titulo_hole)}" onKeyDown="{H(pre+"_key")}" style="position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
        f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1; letter-spacing: -.02em;">{H(titulo_hole)}</h2>'
        f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45; margin-top: -6px;">{H(sub_hole)}</div>'
        + IF(f'{pre}_nerr', f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div>')
        + corpo + '<div style="flex-grow: 1;"></div>'
        + IF(f'{pre}_warn', f'<div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
             f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div>')
        + f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; border-top: 1px solid {LINE};">'
          f'<button type="button" onClick="{H(pre+"_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H(pre+"_save")}" style="{BTN_ST(True,True)}">{H(pre+"_savet")}</button></div>'
        f'</aside></div>')


LBL = f'font-size: 12px; font-weight: 600; color: {MUTED};'
SEC = f'font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;'
ERR = f'font-size: 12px; font-weight: 700; color: {RED};'


def err(hole_has, hole_msg): return IF(hole_has, f'<span role="alert" style="{ERR}">{H(hole_msg)}</span>')


PA_LINHA_CSS = '\n.pa-atividade{border:1px solid #E4E9E5;border-radius:12px;background:#fff;container-type:inline-size}\n.pa-atividade-linha{display:grid;grid-template-columns:38px 56px minmax(0,1fr) 80px 115px 44px;gap:10px;align-items:center;padding:8px 10px;font-size:13px;cursor:pointer}\n.pa-gatilho,.pa-atividade-nome{display:flex;flex-direction:column;gap:3px;min-width:0;overflow-wrap:anywhere}\n.pa-gatilho b{font-size:13px}.pa-gatilho>span,.pa-operacao,.pa-contagem{font-size:12px;color:#65736A}\n.pa-titulo{border:0;background:transparent;padding:6px 0;min-height:32px;font:inherit;font-size:13.5px;font-weight:700;color:#15201A;cursor:pointer;text-align:left}.pa-op-ico{display:inline-flex;color:#4B5A51;flex-shrink:0}.pa-gatilho b{font-variant-numeric:tabular-nums;text-align:right}.pa-mais-w{position:relative;display:flex;justify-content:center}.pa-mais{width:44px;height:44px;border:0;background:transparent;border-radius:8px;font-size:18px;color:#4B5A51;cursor:pointer;opacity:.35}.pa-atividade:hover .pa-mais,.pa-atividade:focus-within .pa-mais,.pa-mais[aria-expanded=true]{opacity:1}@media (hover:none){.pa-mais{opacity:1}}.pa-grp-tot{width:115px;text-align:right;font-size:13px;font-weight:800;font-variant-numeric:tabular-nums;padding-right:64px}.pa-grp{container-type:inline-size}.pa-opf{white-space:nowrap}@media (pointer:coarse){.pa-desfaz{min-height:44px}}@container (max-width:760px){.pa-grp-cab{flex-wrap:wrap;row-gap:2px}.pa-grp-cab>div:first-child{flex-basis:100%}.pa-grp-tot{width:auto;padding-right:0}}\n.pa-contagem,.pa-custo{text-align:right}.pa-custo{font-weight:700;font-variant-numeric:tabular-nums}\n.pa-expandir.g2car,.pa-excluir.g2del{width:38px;height:44px}.pa-atividade button:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px;border-radius:4px}\n.pa-insumos{padding:8px 16px 12px 58px;background:#FBFCFA;border-top:1px solid #E4E9E5;border-radius:0 0 12px 12px}\n.pa-insumos-rolagem{overflow-x:auto}.pa-insumos-rolagem>div,.pa-insumos-rolagem>sc-for>div{min-width:720px}\n.pa-dose{font:inherit;font-variant-numeric:tabular-nums;color:inherit;background:transparent;border:0;border-bottom:1px dashed #A9B4AC;border-radius:4px 4px 0 0;padding:3px 5px;cursor:text}\n@media (hover:hover){.pa-dose:hover{background:#EEF5F0;border-bottom-color:#1E7A4C}}.pa-dose:focus-visible{background:#EEF5F0;border-bottom-color:#1E7A4C}\n@container (max-width:760px){.pa-atividade-linha{grid-template-columns:38px minmax(36px,64px) minmax(0,1fr) 44px;gap:4px 8px}.pa-expandir{grid-column:1;grid-row:1 / 4}.pa-gatilho{grid-column:2;grid-row:1 / 4}.pa-atividade-nome{grid-column:3;grid-row:1}.pa-excluir,.pa-mais-w{grid-column:4;grid-row:1 / 4}.pa-contagem{grid-column:3;grid-row:2;text-align:left}.pa-custo{grid-column:3;grid-row:3;text-align:left}.pa-insumos{padding:8px 12px}}\n.pa-disc{border:0;background:transparent;padding:0;font:inherit;color:inherit;cursor:pointer;display:inline-flex;align-items:center;gap:6px;text-align:left}.pa-disc:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px;border-radius:4px}\n@container (max-width:480px){.pa-atividade-linha{grid-template-columns:32px auto auto minmax(0,1fr) 44px;grid-template-areas:"e n n n m" "e g c k m";gap:2px 10px;padding:6px 6px 8px}.pa-expandir{grid-area:e}.pa-atividade-nome{grid-area:n}.pa-gatilho{grid-area:g}.pa-gatilho b{text-align:left}.pa-contagem{grid-area:c;text-align:left}.pa-custo{grid-area:k;text-align:right;white-space:nowrap}.pa-excluir,.pa-mais-w{grid-area:m}}\n'

# ícones do tipo de operação (Lucide, ISC; LICENSES/lucide-ISC.txt): o mesmo no chip e na atividade (VISOES-2 §3.5)
_OPI = {'pulv': 'M3 3h.01M7 5h.01M11 7h.01M3 7h.01M7 9h.01M3 11h.01M15 5h4v4h-4zM19 9l2 2v10c0 .6-.4 1-1 1h-6c-.6 0-1-.4-1-1V11l2-2M13 14l8-2M13 19l8-2',   # spray-can
        'plant': 'M7 20h10M10 20c5.5-2.5.8-6.4 3-10M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8zM14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z',   # sprout
        'adub': 'M2 22v-5l5-5 5 5-5 5zM9.5 14.5L16 8M17 2l5 5-.5.5a3.53 3.53 0 0 1-5 0 3.53 3.53 0 0 1 0-5L17 2',   # shovel
        'sem': 'M10.165 6.598C9.954 7.478 9.64 8.36 9 9c-.64.64-1.521.954-2.402 1.165A6 6 0 0 0 8 22c7.732 0 14-6.268 14-14a6 6 0 0 0-11.835-1.402zM5.341 10.62a4 4 0 1 0 5.279-5.28',   # bean
        'colh': 'M10 11l11 .9a1 1 0 0 1 .8 1.1l-.665 4.158a1 1 0 0 1-.988.842H20M16 18h-5M18 5a1 1 0 0 0-1 1v5.573M3 4h8.129a1 1 0 0 1 .99.863L13 11.246M4 11V4M7 15h.01M8 10.1V4M16 18a2 2 0 1 0 4 0 2 2 0 1 0-4 0M2 15a5 5 0 1 0 10 0 5 5 0 1 0-10 0',   # tractor
        'agua': E.ICONS['drop'], 'outra': E.ICONS['leaf']}
def _opico(pre):
    svg = lambda d: f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>'
    return ''.join(IF(f'{pre}.io_{k}', svg(d)) for k, d in _OPI.items())

def build():
    fname = 'PA.dc.html'; E._reset_screen(fname)
    EXTRA.append('<style>'+PA_LINHA_CSS+'</style>')
    dd = _dados()
    # ---------- lista · biblioteca por cultura (cards compactos) ----------
    card = (f'<button type="button" class="g2card" aria-current="{H("c.cur")}" onClick="{H("c.open")}" aria-label="{H("c.lab")}" style="{H("c.st")}">'
            f'<span style="display: flex; align-items: flex-start; gap: 8px; width: 100%;"><b style="font-size: 14.5px; flex-grow: 1; line-height: 1.3;">{H("c.nome")}</b>'
            f'<span class="g2card-cta" aria-hidden="true" style="padding-top: 1px;">Abrir plano <span style="font-size: 14px; line-height: 1;">→</span></span></span>'
            f'<span style="display: flex; width: 100%;"><span style="{H("c.est_st")}">{H("c.est")}</span></span>'
            f'<span style="display: flex; gap: 18px; font-size: 12.5px; color: {MUTED};"><span><b style="font-size: 15px; color: {INK};">{H("c.natv")}</b> atividades</span>'
            f'<span><b style="font-size: 15px; color: {INK};">{H("c.custo")}</b> insumos/ha</span></span>'
            f'<span style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;"><span style="font-size: 11.5px; color: {MUTED}; margin-right: 2px;">Gatilhos</span>'
            + FOR('c.gats', 'g', f'<span style="display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 600; color: {INK}; border: 1px solid {LINE};">{H("g.t")}</span>')
            + IF('c.semgat', f'<span style="font-size: 11.5px; color: {MUTED};">—</span>') + '</span></button>')
    lib = (f'<div style="display: flex; flex-wrap: wrap; gap: 16px 18px; align-items: flex-start;">'
           + FOR('lib', 'cu',
              f'<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px; min-width: 0; max-width: 100%;"><div style="{SEC}">{H("cu.t")} <span style="font-weight: 600; letter-spacing: 0; text-transform: none;">· {H("cu.n")}</span></div>'
              f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch;">'
              + FOR('cu.cards', 'c', f'<div style="display: flex; width: 336px; max-width: 100%;">{card}</div>') + '</div></div>', 2)
           + '</div>')
    qf = (f'<div role="group" aria-label="Filtrar planos por cultura" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">'
          + FOR('pa_qf', 'qc', f'<button type="button" aria-pressed="{H("qc.on")}" onClick="{H("qc.go")}" style="{H("qc.st")}">{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button>', 6)
          + '</div>')
    # Botões de criar e incluir (design system 09/10, BOT-01 a BOT-06):
    # - "Criar plano": registro novo e independente → verde, tamanho padrão, no cabeçalho da tela do menu, à direita do título; só na lista
    #   (no detalhe o cabeçalho fica sem verde e o verde é o Próximo passo).
    # - "Incluir atividade": item dentro do plano → branco e compacto no cabeçalho do bloco Atividades, sempre no mesmo lugar (também
    #   com o plano vazio: bloco comum não tem verde).
    # - "Incluir insumo": item dentro da atividade → mini, ao pé da tabela da atividade. Todos com o mesmo "+" e o rótulo.
    criar_cab = IF('lista', f'<button type="button" data-acao="criar" onClick="{H("pa_novo")}" style="{E.BTN_ST(True)} {ICO}">{MAIS(15)}Criar plano</button>', True)
    incl_sec = f'<button type="button" data-acao="adicionar" onClick="{H("pa_incl")}" style="{E.BTN_ST(False, True)} {ICO}">{MAIS(14)}Incluir atividade</button>'
    s1 = bloco('Biblioteca de planos por cultura', 'Abra um plano para editar as atividades ou crie um novo; cada plano tem versões publicadas.', qf + lib)

    # ---------- detalhe · plano aberto (PA.dc.html#plano=<id>) ----------
    prod_hdr = (f'<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr) 150px 120px 110px 32px; gap: 10px; padding: 6px 0 4px; {SEC} font-size: 10px;">'
                f'<span>Grupo</span><span>Produto</span><span style="text-align: right;">Dose/ha</span><span style="text-align: right;">Preço unitário</span><span style="text-align: right;">Custo/ha</span><span></span></div>')
    prod_row = (f'<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr) 150px 120px 110px 32px; gap: 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: center;">'
                f'<span style="color: {MUTED};">{H("p.grupo")}</span>'
                f'<span style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-width: 0;"><span style="font-weight: 600;">{H("p.prod")}</span>'
                + IF('p.temMarca', f'<span title="{H("p.marcaT")}" style="{H("p.marcaSt")}">{H("p.marca")}</span>') + '</span>'
                f'<span style="display: flex; justify-content: flex-end; align-items: center;">'
                + IF('p.lendo', f'<button type="button" class="pa-dose" aria-label="{H("p.dlab")}" title="Alterar dose" onClick="{H("p.ini")}">{H("p.dose")}</button>', True)
                + IF('p.editando', f'<span style="display: inline-flex; align-items: center; gap: 5px;"><input id="{H("p.fid")}" aria-label="{H("p.dlab")}" value="{H("p.val")}" onChange="{H("p.setv")}" onKeyDown="{H("p.tecla")}" onBlur="{H("p.sai")}" inputMode="decimal" style="{H("p.ist")}">'
                     f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{H("p.un")}</span></span>') + '</span>'
                f'<span style="text-align: right; color: {MUTED}; font-variant-numeric: tabular-nums;">{H("p.preco")}</span><span style="text-align: right; font-weight: 700; font-variant-numeric: tabular-nums;">{H("p.custo")}</span>'
                f'<button type="button" class="g2del" aria-label="{H("p.tlab")}" title="Retirar insumo" onClick="{H("p.tirar")}">{E._TRASH}</button></div>'
                + IF('p.temErr', f'<div role="alert" style="font-size: 12px; color: {RED}; text-align: right; padding: 0 42px 4px 0;">{H("p.err")}</div>'))
    add_row = (f'<div role="group" aria-label="{H("a.addLab")}" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 8px 0 2px; border-top: 1px solid {LINE};">'
               + E.ac_campo('a.','Produto','300px') +
               f'<span style="display: inline-flex; align-items: center; gap: 5px;"><input id="{H("a.addDoseId")}" aria-label="Dose por hectare" value="{H("a.addDose")}" onChange="{H("a.addSetD")}" onKeyDown="{H("a.addTecla")}" inputMode="decimal" style="{H("a.addIst")}">'
               f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{H("a.addUn")}</span></span>'
               f'<span style="font-size: 12px; color: {MUTED}; flex-grow: 1; min-width: 120px;">{H("a.addInfo")}</span>'
               f'<button type="button" onClick="{H("a.addOk")}" style="{_MINI}">Incluir</button><button type="button" onClick="{H("a.addNao")}" style="{_MINI}">Cancelar</button></div>'
               + IF('a.addTemErr', f'<div role="alert" style="font-size: 12px; color: {RED}; padding-top: 4px;">{H("a.addErr")}</div>'))
    inl = (IF('a.rmvTem', f'<div role="status" style="display: flex; align-items: center; gap: 10px; margin-top: 6px; padding: 6px 10px; border-radius: 8px; background: {GRAYS}; font-size: 12.5px;"><span style="flex-grow: 1;">{H("a.rmvT")}</span>'
                          f'<button type="button" onClick="{H("a.volta")}" style="{_MINI}">Desfazer</button></div>')
           + IF('a.addOff', f'<div style="padding-top: 8px;"><button type="button" aria-label="{H("a.addLab")}" onClick="{H("a.addIni")}" style="{_MINI} {ICO} gap: 4px;">{MAIS(12)}Incluir insumo</button></div>', True)
           + IF('a.addOn', add_row))
    atv = (f'<div class="pa-atividade" style="{H("a.rst")}">'
           f'<div class="pa-atividade-linha" onClick="{H("a.rowtog")}">'
           f'<button type="button" class="g2car pa-expandir" aria-label="{H("a.lab")}" title="{H("a.lab")}" aria-expanded="{H("a.open")}" aria-controls="{H("a.detalhesId")}" onClick="{H("a.tog")}">{H("a.sym")}</button>'
           f'<span class="pa-gatilho" title="{H("a.gatlab")}"><b aria-hidden="true">{H("a.gatilho")}</b><span class="g2sr">{H("a.gatlab")}</span></span>'
           f'<span class="pa-atividade-nome"><span style="display: flex; align-items: center; gap: 8px; min-width: 0;"><span class="pa-op-ico" role="img" aria-label="{H("a.op")}" title="{H("a.op")}">' + _opico('a') + '</span>'
           f'<button type="button" class="pa-titulo" aria-expanded="{H("a.open")}" aria-controls="{H("a.detalhesId")}" onClick="{H("a.tog")}">{H("a.nome")}</button>'
           + IF('a.hasChg', f'<span style="{H("a.chgst")} padding: 0 8px; font-size: 11px; line-height: 16px;">{H("a.chg")}</span>') + '</span></span>'
           f'<span class="pa-contagem">{H("a.np")}</span><span class="pa-custo">{H("a.custo")}</span>'
           f'<span class="pa-mais-w">' + E.mais(H('a.nome'), [('Editar atividade', H('a.edit')), ('Excluir atividade', H('a.excluir'), True)], linha=True, cls='pa-mais') + '</span></div>'
           + f'<div id="{H("a.detalhesId")}" role="region" aria-label="{H("a.detalhesLab")}">'
           + IF('a.open', '<div class="pa-insumos">'
                + IF('a.semProd', f'<div style="font-size: 12.5px; color: {MUTED}; padding: 6px 0;">Sem insumos · só operação</div>')
                + IF('a.temProd', '<div class="pa-insumos-rolagem">' + prod_hdr + FOR('a.prods', 'p', prod_row, 2) + '</div>') + inl + '</div>') + '</div></div>')
    gat = FOR('t.atvs', 'a', atv, 1)
    grp = FOR('grp', 'g', f'<div class="pa-grp" style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px;">'
                          f'<div class="pa-grp-cab" style="display: flex; align-items: baseline; gap: 10px; border-top: 1px solid {LINE}; padding-top: 10px;"><div style="display: flex; align-items: center; gap: 4px; flex-grow: 1; min-width: 0;">'
                          f'<span style="font-size: 13.5px; font-weight: 800;">{H("g.t")}</span><button type="button" class="g2dica-i" aria-label="Como ler: {H("g.t")}" data-dica="{H("g.d")}" style="width: 32px; height: 32px; border: 0; background: transparent; color: {MUTED}; cursor: help;">ⓘ</button></div>'
                          f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{H("g.n")}</span><span class="pa-grp-tot">{H("g.tot")}</span></div>'
                          + FOR('g.gats', 't', gat, 2) + '</div>', 1)
    head2 = (f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h2 id="pa-det-tit" style="margin: 0; font-family: {DISP}; font-size: 20px; letter-spacing: -.02em;">{H("p_nome")}</h2>'
             f'<span style="{H("p_est_st")}">{H("p_est")}</span></div>')
    # 14/10/2026 (proprietário: "termine de tirar essas descrições abaixo dos títulos e também textos soltos na tela. menos é mais"): saíram
    # a linha "cultura · N atividades · R$/ha · gatilhos" (a seção já diz atividades, custo e gatilho) e "Editar cria o rascunho…" (o aviso
    # do rascunho aparece quando ele nasce)
    banner = (IF('ban_r', f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
                 f'<span style="flex-grow: 1; min-width: 0;">{H("ban_t")}</span>'
                 + IF('nodisc', f'<button type="button" onClick="{H("disc_ask")}" style="{_MINI}">Descartar rascunho</button>', True)
                 + IF('disc', f'<span role="alert" style="flex-basis: 100%; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: {RED};"><span style="flex-grow: 1;">{H("disc_t")}</span>'
                      f'<button type="button" onClick="{H("disc_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Descartar rascunho</button><button type="button" onClick="{H("disc_no")}" style="{_MINI}">Manter</button></span>')
                 + '</div>'))
    xbtn = f'<button type="button" class="g2xtog" onClick="{H("x_tog")}" style="flex-shrink: 0;">{E.seta_xtog(H("x_up"),H("x_down"))}{H("x_lab")}</button>'
    # plano vazio: o bloco Atividades continua com "Incluir atividade" no mesmo lugar; o Próximo passo diz o que falta para publicar
    vazio = f'<div style="padding: 12px 14px; border: 1px dashed {LINE}; border-radius: 12px; font-size: 13px; color: {MUTED};">Nenhuma atividade ainda. Inclua a primeira: defina o gatilho e a operação; depois, os insumos com dose por hectare.</div>'
    qf_op = (f'<div role="group" aria-label="Filtrar atividades por operação" style="display: flex; flex-wrap: wrap; gap: 6px;">'
             + FOR('pa_opf', 'qo', f'<button type="button" class="pa-opf" aria-pressed="{H("qo.on")}" title="{H("qo.lab")}" onClick="{H("qo.go")}" style="{H("qo.st")}">' + IF('qo.temIco', _opico('qo')) + f'{H("qo.t")} <span style="opacity: .75;">{H("qo.n")}</span></button>', 5)
             + '</div>')
    # barra da coleção (v3 · DS-33): filtros rápidos no começo, expandir/recolher (apresentação) no fim; "Incluir atividade" (filho) no
    # cabeçalho da seção, à direita, separado do avanço
    barra = (f'<div style="display: flex; align-items: flex-start; gap: 10px; flex-wrap: wrap;"><div style="flex: 1 1 280px; min-width: 0;">' + IF('tem_opf', qf_op) + '</div>' + xbtn + '</div>')
    atividades = bloco('Atividades do plano', 'Na seta, altere dose e insumos direto na tabela. Clique na atividade para mudar gatilho e operação.',
                       IF('pa_undo', f'<div role="status" style="display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 8px; background: {GRAYS}; font-size: 12.5px;"><span style="flex-grow: 1;">{H("pa_undo_t")}</span><button type="button" class="pa-desfaz" onClick="{H("pa_desfaz")}" style="{_MINI}">Desfazer</button></div>') + IF('vazio', vazio) + IF('tem_atv', barra + f'<div class="rola" style="display: flex; flex-direction: column; gap: 10px;">{grp}</div>', True), acao=incl_sec)

    # ---------- detalhe · com rascunho, as alterações logo acima do Próximo passo ----------
    # 14/10/2026 (proprietário: "tire cultivos que usam esse plano e versões. não agregam quase nada"): os blocos saíram do detalhe.
    # A regra continua no domínio: publicar cria a versão nova e o cultivo fica na versão em que foi aplicado (a troca é no Planejar safra);
    # o cabeçalho e o aviso de "Editar cria o rascunho" dizem isso, e o cartão da biblioteca diz em quantos cultivos o plano está aplicado.
    s2 = head2 + banner + atividades   # o bloco de alterações saiu (proprietário, 14/10/2026); o que mudou fica no selo da atividade e no aviso ao salvar

    # Próximo passo do detalhe (BOT-01/02): "‹ Biblioteca de planos" à esquerda e "Salvar alterações" à direita, com o motivo quando
    # desabilitado (VIS-04). O componente comum (engine.area_acoes) ainda não leva "disabled": o atributo entra aqui, conferido no build.
    area = E.area_acoes('aa', 'Próximo passo')
    alvo = 'class="acoes-prim" data-acao="{{aa_primA}}"'
    assert area.count(alvo) == 1, 'engine.area_acoes mudou: rever o disabled do Publicar (processo_planos)'
    area = area.replace(alvo, f'class="acoes-prim" disabled="{H("aa_pdis")}" title="{H("aa_pwhy")}" data-acao="{{{{aa_primA}}}}"')
    corpo = (IF('lista', f'<div style="display: flex; flex-direction: column; gap: 14px;">{s1}</div>', True)
             + IF('det', f'<div style="display: flex; flex-direction: column; gap: 14px;">{s2}</div>') + area)

    # ---------- painel: atividade (gatilho, nome, operação, produtos e doses) ----------
    fm_body = (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="fm_op" style="{LBL}">Operação</label><select id="fm_op" value="{H("fm_op")}" onChange="{H("fm_setop")}" style="{H("fm_ost")}">'
               + FOR('fm_ops', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 3) + '</select>' + err('fm_heo', 'fm_eo') + '</div>'
               f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="fm_atv" style="{LBL}">Atividade</label><select id="fm_atv" value="{H("fm_atv")}" onChange="{H("fm_setatv")}" disabled="{H("fm_atvdis")}" style="{H("fm_ast")}">'
               + FOR('fm_atvs', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 4) + '</select>'
               + IF('fm_outra', f'<input id="fm_nome" aria-label="Nome da nova atividade" placeholder="Nome da nova atividade" value="{H("fm_nome")}" onChange="{H("fm_setnome")}" style="{H("fm_nst")}">')
               + err('fm_hen', 'fm_en') + '</div>'
               f'<div style="display: flex; flex-direction: column; gap: 6px;"><div style="{SEC}">Gatilho da atividade</div>'
               f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><label for="fm_tipo" style="position: absolute; left: -9999px;">Tipo de gatilho</label>'
               f'<select id="fm_tipo" value="{H("fm_tipo")}" onChange="{H("fm_settipo")}" style="{H("fm_tst")}">' + FOR('fm_tipos', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 4) + '</select>'
               + IF('fm_isDias', f'<input id="fm_dias" aria-label="Dias" value="{H("fm_dias")}" onChange="{H("fm_setdias")}" inputMode="numeric" style="{H("fm_gst")} text-align: right;"><span style="font-size: 13px; color: {MUTED};">{H("fm_diasl")}</span>', True)
               + IF('fm_isData', f'<input id="fm_data" type="date" aria-label="Data" value="{H("fm_data")}" onChange="{H("fm_setdata")}" style="{H("fm_dst")}">')
               + '</div>' + err('fm_heg', 'fm_eg') + f'<span style="font-size: 11.5px; color: {MUTED};">{H("fm_ghelp")}</span></div>'
               + IF('fm_temIns', f'<div style="display: flex; flex-direction: column; gap: 3px; padding-top: 10px; border-top: 1px solid {LINE};"><span style="{SEC}">Insumos</span>'
                    f'<span style="font-size: 13px;">{H("fm_ins")}</span><span style="font-size: 11.5px; color: {MUTED};">Altere doses e insumos na tabela da atividade.</span></div>')
               + IF('fm_nova', f'<div style="font-size: 12px; color: {MUTED}; padding-top: 10px; border-top: 1px solid {LINE};">Depois de salvar, a atividade abre na lista para você incluir os insumos.</div>'))
    EXTRA.append(aside('fm', 'fm_titulo', 'fm_sub', fm_body, w=600))
    np_body = (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="np_nome" style="{LBL}">Nome do plano</label><input id="np_nome" value="{H("np_nome")}" onChange="{H("np_setnome")}" style="{H("np_nst")}">' + err('np_hen', 'np_en') + '</div>'
               f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="np_cult" style="{LBL}">Cultura</label><select id="np_cult" value="{H("np_cult")}" onChange="{H("np_setcult")}" style="{H("np_cst")}">'
               + FOR('np_cults', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 3) + '</select>' + err('np_hec', 'np_ec') + '</div>'
               + IF('np_hasbase', f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="np_base" style="{LBL}">Começar de</label><select id="np_base" value="{H("np_base")}" onChange="{H("np_setbase")}" style="{H("np_bst")}">'
                    + FOR('np_bases', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 2) + f'</select><span style="font-size: 11.5px; color: {MUTED};">Copiar só traz as atividades; o plano de origem não muda.</span></div>'))
    EXTRA.append(aside('np', 'np_titulo', 'np_sub', np_body, w=460))

    EXTRAJS[0] = 'const PA0 = ' + json.dumps(dd, ensure_ascii=False) + ';\n' + JS
    HEIGHTS37[fname] = 1000   # tela de trabalho com rolagem interna (mesma altura de quando tinha a faixa de etapas), como a MA da PCM
    shell37('PA', 'Planos agronômicos', corpo, fname=fname,
            subtitle='Mantenha os planos padrão por cultura: gatilho, atividades, produtos e doses. Cada alteração vira uma nova versão; cultivos já aplicados não mudam sozinhos.',
            primary_html=criar_cab,   # sem faixa de etapas (NAV-1): lista → detalhe
            ctx=('Fazenda Santa Rita', H('ctx_pl'), None), search=False)
    return fname


if __name__ == '__main__':
    import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(build())
