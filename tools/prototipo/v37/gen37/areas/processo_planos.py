# -*- coding: utf-8 -*-
"""Agrícola › Planos agronômicos — uma só tela de trabalho (PA.dc.html) com 3 etapas:
1 Escolha o plano (biblioteca por cultura, cards) · 2 Edite as atividades (Gatilho + atividade → Insumos e doses)
· 3 Publique a versão (diferenças, cultivos que continuam na versão antiga, histórico).
Salvar grava num rascunho v(n+1); publicar cria a nova versão; cultivos aplicados nunca são alterados aqui."""
import json, os
from engine import grid, esc, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, GRAYS, DISP, BTN_ST, EXTRA, EXTRAJS, _MINI, _MINIP
import engine as E
from ui37 import shell37, steps_state, HEIGHTS37
import dados2 as D2

H = lambda s: '{{' + s + '}}'
F = lambda: H('false')
T = lambda: H('true')
def IF(cond, html, dflt=False): return f'<sc-if value="{H(cond)}" hint-placeholder-val="{T() if dflt else F()}">{html}</sc-if>'
def FOR(lst, as_, html, n=2): return f'<sc-for list="{H(lst)}" as="{as_}" hint-placeholder-count="{n}">{html}</sc-for>'

NOMES = ['Escolha o plano', 'Edite as atividades', 'Publique a versão']

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
function paAplCurto(pid){ const m=paByVer(pid); return Object.keys(m).map(Number).sort((a,b)=>b-a).map(v=>m[v].length+' na v'+v).join(' · '); }
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
// abrir um plano guarda a posição da biblioteca; ao voltar à etapa 1, a rolagem volta e o foco vai ao cartão aberto por último
function paOpen(self,id){ const p=paPlan(self,id); try{ self.__paPos=[...document.querySelectorAll('main[data-scroll],.ml-tog+div')].map(e=>[e,e.scrollTop]); }catch(e){} self.setState({pid:id,step:2,del:null,disc:false,flash:null,ied:null,iadd:null,rmv:null,g2toast:'Plano aberto: '+p.nome+(p.rasc?' · rascunho v'+p.rasc.v:'')}); }
// ---------- biblioteca ----------
// Filtro rápido por cultura: "Todas" ou uma cultura; tocar de novo na cultura escolhida volta a "Todas".
const PA_QCH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
function paCulturas(ps){ const cu=[]; ps.forEach(p=>{ if(cu.indexOf(p.cultura)<0) cu.push(p.cultura); }); return cu; }
function paCuf(self,cu){ const f=self.state.cuf||''; return cu.indexOf(f)<0?'':f; }
function paQf(self){ const ps=paPlans(self); const cu=paCulturas(ps); const f=paCuf(self,cu);
  const ch=(t,n,on,go)=>({t:t,n:String(n),on:String(!!on),go:go,st:PA_QCH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  return [ch('Todas',ps.length,!f,()=>self.setState({cuf:''}))].concat(cu.map(c=>ch(c,ps.filter(p=>p.cultura===c).length,f===c,()=>self.setState({cuf:f===c?'':c})))); }
function paLib(self){ const ps=paPlans(self); const cu=paCulturas(ps); const f=paCuf(self,cu); const sel=self.state.pid;
  return cu.filter(c=>!f||c===f).map(c=>{ const cs=ps.filter(p=>p.cultura===c);
    return {t:c, n:cs.length+(cs.length>1?' planos':' plano'), cards:cs.map(p=>{ const atv=paShown(p); const tp=[];
      atv.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
      const est=p.versao===0?['Rascunho v1','y']:(p.rasc?['Rascunho v'+p.rasc.v+' em edição','y']:['Publicado','g']); const nc=paCults(p.id).length;
      return {nome:p.nome, ver:(p.versao?'v'+p.versao:'sem versão publicada'), est:est[0], est_st:paChip(est[1]), natv:String(atv.length), custo:paRS(paCt(atv)),
        gats:tp.map(t=>({t})), semgat:!tp.length, apl:nc?('Aplicado em '+nc+(nc>1?' cultivos':' cultivo')):'Sem cultivos aplicados', apl2:nc?paAplCurto(p.id):'', aplst:nc?'font-weight:700;':'color:#65736A;',
        st:'display:flex;flex-direction:column;gap:9px;padding:12px 15px;border-radius:12px;text-align:left;font-family:inherit;color:#15201A;min-width:0;width:100%;box-sizing:border-box;cursor:pointer;',
        cur:String(p.id===sel), lab:'Abrir plano '+p.nome, open:()=>paOpen(self,p.id)}; })}; }); }
// ---------- etapa 2 · filtro rápido por operação: "Todas" ou uma operação; tocar de novo volta a "Todas" ----------
// as operações seguem a ordem do catálogo (PA0.ops); a escolha vale entre planos e cai para "Todas" se o plano não tiver a operação
function paOps(atv){ const tem={}; atv.forEach(a=>{ tem[a.op]=(tem[a.op]||0)+1; }); const ord=PA0.ops.filter(o=>tem[o]).concat(Object.keys(tem).filter(o=>PA0.ops.indexOf(o)<0).sort()); return ord.map(o=>({op:o,n:tem[o]})); }
function paOpf(self,ops){ const f=self.state.opf||''; return ops.some(o=>o.op===f)?f:''; }
function paOpChips(self,todas,ops,f){
  const ch=(t,n,on,go,lab)=>({t:t,n:String(n),on:String(!!on),go:go,lab:lab,st:PA_QCH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  return [ch('Todas',todas.length,!f,()=>self.setState({opf:''}),'Mostrar todas as operações')].concat(ops.map(o=>ch(o.op,o.n,f===o.op,()=>self.setState({opf:f===o.op?'':o.op}),(f===o.op?'Mostrar todas as operações':'Mostrar só '+o.op)))); }
// ---------- etapa 2 · gatilho e atividade na mesma linha; expansão direta dos insumos ----------
function paAtvV(self,p,a,pub){ const xa=self.state.xa||{}; const open=!!xa[a.id]; const del=self.state.del===a.id; const o=pub[a.id];
  let chg=''; if(p.rasc&&p.versao){ if(!o) chg='Nova'; else if(paNorm(o)!==paNorm(a)) chg='Alterada'; }
  const gat=paGat(a.g); const np=a.prods.length; const nv=p.rasc?p.rasc.v:p.versao+1; const fl=self.state.flash===a.id;
  return Object.assign({nome:a.nome, op:a.op, gatilho:gat.t, gatilhoFull:gat.full, hasFull:!!gat.full, detalhesId:'pa-insumos-'+p.id+'-'+a.id, detalhesLab:'Insumos de '+a.nome, np:np?(np+(np>1?' insumos':' insumo')):'Só operação', custo:np?paRS(paCa(a))+'/ha':'—', open, sym:open?'▾':'▸', lab:(open?'Recolher insumos de ':'Mostrar insumos de ')+a.nome,
    tog:()=>{ const n=Object.assign({},self.state.xa||{}); n[a.id]=!open; self.setState({xa:n}); },
    edit:()=>paEdit(self,a.id), rst:fl?'background:#E4F3E9;':'',
    chg, hasChg:!!chg, chgst:paChip(chg==='Nova'?'g':'y'),
    asking:del, notAsking:!del, ask:()=>self.setState({del:a.id}), no:()=>self.setState({del:null}), yes:()=>paDel(self,p.id,a.id), dlab:'Excluir atividade '+a.nome,
    delmsg:'Excluir “'+a.nome+'”'+(p.versao?' do rascunho v'+nv+'? A v'+p.versao+' publicada e os cultivos que a usam não mudam.':' do rascunho?'),
    semProd:!np, temProd:!!np,
    prods:a.prods.map((x,i)=>paProdV(self,p,a,x,i,(p.rasc&&p.versao&&o)?o:null)) }, paAddV(self,a), paRmvV(self,p,a)); }
// ---------- drill-down editável: dose, retirar e incluir insumo direto na tabela ----------
// grava no rascunho como o formulário (cria a v(n+1) na primeira mudança); o formulário continua para gatilho, operação e nome
const PA_DOSE_ST='font-family:inherit;font-size:12.8px;font-variant-numeric:tabular-nums;text-align:right;width:78px;padding:4px 6px;border-radius:8px;box-sizing:border-box;background:#fff;color:#15201A;';
function paRasc(self,aid,fn){ const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===self.state.pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)}; fn(p.rasc.atividades.find(x=>x.id===aid)); const nc=paCults(p.id).length;
  return {ps, fim:(novo&&p.versao)?(' Rascunho v'+p.rasc.v+' criado; a v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.'):' Gravado no rascunho v'+p.rasc.v+'.'}; }
function paFoco(id,sel){ setTimeout(()=>{ const el=document.getElementById(id); if(el){ el.focus(); if(sel&&el.select) el.select(); } },0); }
function paDoseId(aid,prod){ return 'pa-dose-'+aid+'-'+String(prod).replace(/[^A-Za-z0-9]/g,'_'); }
function paDoseIni(self,a,x){ self._paEsc=false; self.setState({ied:{aid:a.id,prod:x.prod,val:paQ(x.dose),err:''},iadd:null}); paFoco(paDoseId(a.id,x.prod),true); }
// Enter ou sair do campo grava; Esc cancela (a marca evita que o blur da saída grave o que foi cancelado)
function paDoseOk(self){ if(self._paEsc){ self._paEsc=false; return; } const ed=self.state.ied; if(!ed) return; const n=paNum(ed.val);
  if(String(ed.val).trim()===''||isNaN(n)||n<=0){ self.setState({ied:Object.assign({},ed,{err:'Informe a dose por hectare, maior que zero.'})}); return; }
  const a0=paWork(paPlan(self,self.state.pid)).find(y=>y.id===ed.aid); const x0=a0&&a0.prods.find(y=>y.prod===ed.prod);
  if(!x0||Math.abs(x0.dose-n)<1e-9){ self.setState({ied:null}); return; }
  const r=paRasc(self,ed.aid,(a)=>{ const x=a.prods.find(y=>y.prod===ed.prod); if(x) x.dose=n; });
  self.setState({pl:r.ps,ied:null,g2toast:'Dose de '+ed.prod+': '+paQ(x0.dose)+' → '+paQ(n)+' '+x0.un+'/ha.'+r.fim}); }
function paProdV(self,p,a,x,i,o){ const ed=self.state.ied; const em=!!ed&&ed.aid===a.id&&ed.prod===x.prod; const x0=o?o.prods.find(y=>y.prod===x.prod):null;
  const marca=(o&&!x0)?'novo':((x0&&Math.abs(x0.dose-x.dose)>1e-9)?'dose alterada':''); const dt=paQ(x.dose)+' '+x.un+'/ha';
  return {grupo:x.grupo, prod:x.prod, dose:dt, preco:paRS(x.preco)+'/'+x.un, custo:paRS(x.dose*x.preco)+'/ha',
    marca, temMarca:!!marca, marcaSt:paChip(marca==='novo'?'g':'y'), marcaT:x0?('Na v'+p.versao+' publicada: '+paQ(x0.dose)+' '+x0.un+'/ha'):'Não existe na v'+p.versao+' publicada',
    lendo:!em, editando:em, dlab:'Alterar a dose de '+x.prod+', hoje '+dt, ini:()=>paDoseIni(self,a,x),
    fid:paDoseId(a.id,x.prod), val:em?ed.val:'', un:x.un+'/ha', ist:PA_DOSE_ST+'border:1px solid '+(em&&ed.err?'#B42318':'#1E7A4C')+';',
    setv:(e)=>self.setState({ied:Object.assign({},self.state.ied,{val:e.target.value,err:''})}),
    tecla:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); paDoseOk(self); } else if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); self._paEsc=true; self.setState({ied:null}); } },
    sai:()=>paDoseOk(self), err:em?ed.err:'', temErr:em&&!!ed.err,
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
    addIst:paIst(e&&!!(on&&ad.prod),'84px')+'text-align:right;'}, ac); }
function paS2(self,v,p){ const todas=paWork(p); const ops=paOps(todas); const of=paOpf(self,ops); const atv=of?todas.filter(a=>a.op===of):todas; const pub={};
  v.pa_opf=paOpChips(self,todas,ops,of); v.tem_opf=ops.length>1; (p.atividades||[]).forEach(a=>{ pub[a.id]=a; });
  const G={}; atv.forEach(a=>{ const g=paGrp(a.g); const k=paGkey(a.g); const m=G[g]||(G[g]={}); (m[k]||(m[k]={g:a.g,atvs:[]})).atvs.push(a); });
  v.grp=['DAP','DATA','COL'].filter(g=>G[g]).map(g=>{ const list=Object.values(G[g]).sort((A,B)=>{ const a=paOrd(A.g), b=paOrd(B.g);
      if(g==='DATA') return a<b?-1:(a>b?1:0); if(a!==b) return a-b; return A.g.tipo<B.g.tipo?-1:1; });
    const nat=list.reduce((s,t)=>s+t.atvs.length,0);
    return {t:PA_GRP[g].t, d:PA_GRP[g].d, n:list.length+(list.length>1?' gatilhos':' gatilho')+' · '+nat+(nat>1?' atividades':' atividade'),
      gats:list.map(t=>({atvs:t.atvs.map(a=>paAtvV(self,p,a,pub))}))}; });
  v.vazio=!todas.length; v.tem_atv=!!todas.length;
  v.x_all=()=>{ const xa={}; atv.forEach(a=>{ xa[a.id]=true; }); self.setState({xg:{},xa}); };
  v.x_none=()=>self.setState({xa:{}});
  // um só botão: "Expandir tudo" até todas as atividades visíveis estarem abertas; aí vira "Recolher tudo"
  const xa0=self.state.xa||{}; const todasAb=atv.length>0&&atv.every(a=>xa0[a.id]); v.x_lab=todasAb?'Recolher tudo':'Expandir tudo'; v.x_tog=todasAb?v.x_none:v.x_all; v.x_up=todasAb; v.x_down=!todasAb;
  const est=p.versao===0?['Rascunho v1 · ainda não publicado','y']:(p.rasc?['Rascunho v'+p.rasc.v+' em edição','y']:['Publicado · v'+p.versao,'g']);
  v.p_nome=p.nome; v.p_est=est[0]; v.p_est_st=paChip(est[1]);
  const tp=[]; todas.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
  v.k2=p.cultura+' · '+todas.length+(todas.length===1?' atividade':' atividades')+' · '+paRS(paCt(todas))+'/ha de insumos'+(tp.length?' · gatilhos: '+tp.join(', '):'');
  const apl=paApl(p.id); const nd=paDiff(p).length; const nv=p.rasc?p.rasc.v:p.versao+1;
  v.ban_r=!!p.rasc;
  if(p.versao===0) v.ban_t='Rascunho v1 · ainda não publicado. Publique na etapa 3 para poder aplicar em Planejar safra.';
  else if(p.rasc) v.ban_t='Rascunho v'+p.rasc.v+' · '+nd+(nd===1?' alteração não publicada. ':' alterações não publicadas. ')+(apl?'Aplicado em '+apl+' — não serão alterados.':'Nenhum cultivo usa este plano.');
  v.disc=!!self.state.disc&&!!p.rasc; v.nodisc=!v.disc;
  v.disc_t=p.versao?('Descartar o rascunho v'+(p.rasc?p.rasc.v:'')+' e suas '+nd+' alterações? A v'+p.versao+' publicada continua valendo.'):'Descartar este plano novo? Ele ainda não foi publicado e será removido da biblioteca.';
  v.disc_ask=()=>self.setState({disc:true}); v.disc_no=()=>self.setState({disc:false}); v.disc_yes=()=>paDiscard(self,p.id);
  v.ban_pub=()=>self.setState({step:3,del:null});
}
function paDiscard(self,pid){ const ps=paClone(paPlans(self)); const i=ps.findIndex(x=>x.id===pid); const p=ps[i];
  if(p.versao===0){ ps.splice(i,1); self.setState({pl:ps,pid:null,step:1,disc:false,g2toast:'Plano novo descartado: '+p.nome+'.'}); return; }
  const v=p.rasc.v; p.rasc=null; self.setState({pl:ps,disc:false,g2toast:'Rascunho v'+v+' descartado. A v'+p.versao+' publicada continua valendo.'}); }
function paDel(self,pid,aid){ const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)}; const a=p.rasc.atividades.find(x=>x.id===aid); p.rasc.atividades=p.rasc.atividades.filter(x=>x.id!==aid);
  self.setState({pl:ps,del:null,g2toast:'“'+a.nome+'” excluída do rascunho v'+p.rasc.v+(novo&&p.versao?' (criado agora)':'')+'.'+(p.versao?' A v'+p.versao+' publicada não muda.':'')}); }
// ---------- formulário lateral da atividade ----------
function paEdit(self,aid){ const p=paPlan(self,self.state.pid); if(!p) return; const a=aid?paWork(p).find(x=>x.id===aid):null;
  // DAP negativo abre como "Dias antes do plantio" com o número positivo: o sentido fica no tipo, nunca no sinal
  const antes=!!a&&a.g.tipo==='DAP'&&Number(a.g.dias)<0;
  const d=a?{op:a.op,nome:a.nome,outra:(PA0.atvs[a.op]||[]).indexOf(a.nome)<0,tipo:(antes?'DAPA':a.g.tipo),dias:(a.g.tipo==='DATA'?'':String(Math.abs(Number(a.g.dias)))),data:(a.g.data||'')}
           :{op:paOpf(self,paOps(paWork(p))),nome:'',outra:false,tipo:'DAP',dias:'',data:''};
  self.setState({fm:{aid:aid||null,draft:d,orig:JSON.stringify(d),errs:{},warn:false,rm:null},del:null,ied:null,iadd:null}); }
function paFmUpd(self,patch,errk){ const cur=self.state.fm; const nd=Object.assign({},cur.draft,patch); const ne=Object.assign({},cur.errs||{}); (errk||Object.keys(patch)).forEach(k=>{ delete ne[k]; });
  self.setState({fm:Object.assign({},cur,{draft:nd,errs:ne,warn:false})}); }
function paIst(err,w){ return 'font-family:inherit;font-size:14px;padding:8px 10px;border-radius:10px;box-sizing:border-box;'+(w?'width:'+w+';':'width:100%;')+'border:1px solid '+(err?'#B42318':'#E4E9E5')+';background:#fff;color:#15201A;'; }
function paFm(self,v){ const fm=self.state.fm; v.fm_open=!!fm; if(!fm) return; const p=paPlan(self,self.state.pid); if(!p){ v.fm_open=false; return; } const d=fm.draft; const er=fm.errs||{};
  const nv=p.rasc?p.rasc.v:p.versao+1; const nc=paCults(p.id).length; const a0=fm.aid?paWork(p).find(x=>x.id===fm.aid):null;
  v.fm_titulo=a0?('Atividade · '+a0.nome):'Nova atividade';
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
  const a0=fm.aid?paWork(paPlan(self,self.state.pid)).find(x=>x.id===fm.aid):null; const prods=a0?paClone(a0.prods):[];
  if(Object.keys(er).length){ self.setState({fm:Object.assign({},fm,{errs:er,warn:false})}); return; }
  const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===self.state.pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)};
  const atv={id:fm.aid||('n'+Date.now().toString(36)),nome:String(d.nome).trim(),op:d.op,g:{tipo:(d.tipo==='DAPA'?'DAP':d.tipo),dias,data},prods};
  const L=p.rasc.atividades; const ix=L.findIndex(a=>a.id===fm.aid); if(ix>=0) L[ix]=atv; else L.push(atv);
  const xg=Object.assign({},self.state.xg||{}); xg[paGkey(atv.g)]=true; const xa=Object.assign({},self.state.xa||{}); xa[atv.id]=true;
  const nc=paCults(p.id).length;
  const msg=(novo&&p.versao)?('Rascunho v'+p.rasc.v+' criado com a alteração. A v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.')
                            :((fm.aid?'Atividade salva':'Atividade incluída')+' no rascunho v'+p.rasc.v+'.');
  // atividade nova: abre na lista com "+ Incluir insumo" pronto; se o filtro por operação a esconderia, volta a "Todas"
  const nova=!fm.aid; const opf=self.state.opf||'';
  self.setState({pl:ps,fm:null,xg,xa,flash:atv.id,g2toast:msg+(nova?' Inclua os insumos na tabela.':''),opf:(opf&&opf!==atv.op)?'':opf,
    iadd:nova?{aid:atv.id,prod:'',dose:'',err:''}:null,ied:null,g2ac:null});
  if(nova) paFoco(paAcId('pa-add-'+atv.id)); }
// ---------- novo plano ----------
function paNewPlan(self){ const d={nome:'',cultura:paCuf(self,paCulturas(paPlans(self))),base:''}; self.setState({np:{draft:d,orig:JSON.stringify(d),errs:{},warn:false}}); }
function paNp(self,v){ const np=self.state.np; v.np_open=!!np; v.np_titulo='Novo plano'; v.np_sub='O plano nasce como rascunho v1; publique na etapa 3 para aplicar em Planejar safra.'; if(!np) return; const d=np.draft; const er=np.errs||{};
  const upd=(patch)=>{ const cur=self.state.np; const ne=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>{ delete ne[k]; }); self.setState({np:Object.assign({},cur,{draft:Object.assign({},cur.draft,patch),errs:ne,warn:false})}); };
  v.np_nome=d.nome; v.np_setnome=(e)=>upd({nome:e.target.value}); v.np_en=er.nome||''; v.np_hen=!!er.nome; v.np_nst=paIst(er.nome);
  v.np_cults=[{v:'',t:'Escolha a cultura'}].concat(PA0.culturas.map(c=>({v:c,t:c}))); v.np_cult=d.cultura; v.np_setcult=(e)=>upd({cultura:e.target.value,base:''}); v.np_ec=er.cultura||''; v.np_hec=!!er.cultura; v.np_cst=paIst(er.cultura);
  const bs=paPlans(self).filter(p=>p.cultura===d.cultura&&p.versao>0);
  v.np_bases=[{v:'',t:'Começar em branco'}].concat(bs.map(p=>({v:p.id,t:'Copiar atividades de '+p.nome+' v'+p.versao}))); v.np_base=d.base; v.np_setbase=(e)=>upd({base:e.target.value}); v.np_hasbase=!!d.cultura; v.np_bst=paIst(false);
  v.np_warn=!!np.warn; v.np_nerr=Object.keys(er).length>0;
  v.np_close=()=>{ const cur=self.state.np; if(JSON.stringify(cur.draft)!==cur.orig){ self.setState({np:Object.assign({},cur,{warn:true})}); return; } self.setState({np:null}); };
  v.np_discard=()=>self.setState({np:null}); v.np_keep=()=>self.setState({np:Object.assign({},self.state.np,{warn:false})});
  v.np_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.np_close(); } };
  v.np_save=()=>{ const cur=self.state.np; const dd=cur.draft; const e={}; const nome=String(dd.nome||'').trim();
    if(!nome) e.nome='Informe o nome do plano.'; else if(paPlans(self).some(p=>p.cultura===dd.cultura&&p.nome.toLowerCase()===nome.toLowerCase())) e.nome='Já existe um plano com este nome nesta cultura.';
    if(!dd.cultura) e.cultura='Escolha a cultura.';
    if(Object.keys(e).length){ self.setState({np:Object.assign({},cur,{errs:e,warn:false})}); return; }
    const base=dd.base?paPlan(self,dd.base):null; const id='NP'+Date.now().toString(36);
    const atv=base?paClone(base.atividades).map((a,i)=>Object.assign(a,{id:id+'_'+i})):[];
    const ps=paPlans(self).concat([{id,nome,cultura:dd.cultura,versao:0,atividades:[],rasc:{v:1,atividades:atv},hist:[]}]);
    self.setState({pl:ps,np:null,pid:id,step:2,xg:{},xa:{},g2toast:'Plano “'+nome+'” criado como rascunho v1'+(base?' a partir de '+base.nome+' v'+base.versao:'')+'. Ajuste as atividades e publique na etapa 3.'}); }; }
// ---------- publicar ----------
function paPub(self){ const pid=self.state.pid; const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===pid);
  if(!p||!p.rasc){ self.setState({g2toast:'Nada a publicar: edite as atividades na etapa 2.'}); return; }
  if(!p.rasc.atividades.length){ self.setState({g2toast:'Inclua ao menos uma atividade antes de publicar.'}); return; }
  p.versao=p.rasc.v; p.atividades=p.rasc.atividades; p.rasc=null; p.hist=[{v:p.versao,at:PA0.hoje}].concat(p.hist||[]);
  const apl=paApl(pid);
  self.setState({pl:ps,g2toast:'Versão v'+p.versao+' publicada.'+(apl?' Os cultivos continuam como estavam ('+apl+'); decida a adoção em Planejar safra.':' Já pode ser aplicada em Planejar safra.')}); }
function paS3(self,v,p){ const nd=paDiff(p); v.s3_has=!!p.rasc; v.s3_none=!p.rasc;
  v.dif=nd.map(d=>({k:d.k,st:paChip(d.c),n:d.n,t:d.t})); v.dif_vazio=!!p.rasc&&!nd.length;
  const nv=p.rasc?p.rasc.v:p.versao;
  v.dif_tit=p.versao?('Alterações do rascunho v'+nv+' em relação à v'+p.versao):'Primeira versão do plano (v1)';
  const c0=paCt(p.atividades), c1=p.rasc?paCt(p.rasc.atividades):c0, dl=c1-c0;
  v.dif_custo=p.versao?('Custo de insumos: '+paRS(c0)+'/ha na v'+p.versao+' → '+paRS(c1)+'/ha na v'+nv+(Math.abs(dl)>0.004?' ('+(dl>0?'+':'−')+paRS(Math.abs(dl))+'/ha)':' (sem mudança)')):('Custo de insumos: '+paRS(c1)+'/ha');
  const apl=paApl(p.id);
  v.imp=apl?('Aplicado em '+apl+' — não serão alterados. '+(p.rasc?'Depois de publicar a v'+nv+', decida a adoção por cultivo em Planejar safra.':'A adoção de uma versão nova é decidida por cultivo em Planejar safra.')):'Nenhum cultivo usa este plano; publicar não altera nenhuma safra.';
  v.imp_st='padding:9px 12px;border-radius:10px;font-size:12.8px;font-weight:700;'+(apl?'background:#FFF3D6;color:#8A5A00;':'background:#EEF1EE;color:#5B6660;');
  v.tem_cv=paCults(p.id).length>0;
  const bv=paByVer(p.id);
  v.hist=(p.rasc?[{t:'v'+p.rasc.v,at:'rascunho em edição',st:'Rascunho',stst:paChip('y'),uso:'—'}]:[]).concat((p.hist||[]).map(h=>{ const u=(bv[h.v]||[]).length;
    return {t:'v'+h.v, at:'publicada em '+h.at, st:(h.v===p.versao?'Em vigor':'Substituída'), stst:paChip(h.v===p.versao?'g':'n'), uso:u?(u+(u>1?' cultivos':' cultivo')):'nenhum cultivo'}; })); }
function PREVALS(self,v){ const G=GRIDS.find(g=>g.id==='g_cv'); if(!G) return; const pid=self.state.pid; const p=pid?paPlan(self,pid):null;
  G.rows=p?paCults(pid).map(c=>{ let sit;
    if(c.ro) sit=[{k:'chip',t:'Safra encerrada · fica na v'+c.ver,c:'gray'}];
    else if(p.rasc) sit=[{k:'chip',t:'Continua na v'+c.ver+' ao publicar',c:'yellow'}];
    else if(c.ver<p.versao) sit=[{k:'chip',t:'Na v'+c.ver+' · decidir adoção da v'+p.versao,c:'yellow'},{k:'link',t:'Decidir em Planejar safra ›',h:'SAF.dc.html'}];
    else sit=[{k:'chip',t:'Na versão em vigor',c:'green'}];
    return {id:c.id,ro:true,v:{saf:c.safraNome,local:c.local,cult:c.cultura+' '+c.variedade,area:c.area,ver:'v'+c.ver},s:{sit:sit[0].t},p:{local:[{k:'b',t:c.local}],ver:[{k:'tag',t:'v'+c.ver}],sit}}; }):[]; }
function EXTRAVALS(self,v){ const st=self.state; const step=st.step||1; const pid=st.pid||null; const p=pid?paPlan(self,pid):null;
  for(let i=1;i<=3;i++) v['s'+i]=(step===i);
  const whys={}; if(!p){ whys[2]='Escolha um plano'; whys[3]='Escolha um plano'; } else if(!p.rasc) whys[3]='Nada a publicar';
  g2steps(self,v,'stp',3,step,whys,(i)=>{ if(i>1&&!self.state.pid){ self.setState({step:1,g2toast:'Escolha um plano para abrir esta etapa.'}); return; } self.setState({step:i,del:null,disc:false}); });
  v.lib=paLib(self); v.pa_qf=paQf(self);
  if(step===1&&self.__paPos){ const pos=self.__paPos; self.__paPos=null; setTimeout(()=>{ try{ pos.forEach(([e,t])=>{ e.scrollTop=t; }); const c=document.querySelector('main .g2card[aria-current=true]'); if(c){ c.scrollIntoView({block:'nearest'}); c.focus({preventScroll:true}); } }catch(e){} },0); }
  v.ctx_pl=p?(p.nome+' · '+(p.rasc?'rascunho v'+p.rasc.v:'v'+p.versao)):'Nenhum plano escolhido';
  if(p){ paS2(self,v,p); paS3(self,v,p); } else { v.grp=[]; v.dif=[]; v.hist=[]; }
  paFm(self,v); paNp(self,v);
  const prim={1:['Novo plano',()=>paNewPlan(self)],2:['Incluir atividade',()=>paEdit(self,null)],3:[(p&&p.rasc)?('Publicar versão v'+p.rasc.v):'Publicar versão',()=>paPub(self)]}[step];
  v.prim_t=prim[0]; v.prim_fn=prim[1]; const hide=(step>1&&!p)||(step===3&&!(p&&p.rasc));
  v.prim_st='padding:7px 14px;border-radius:9px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;flex-shrink:0;'+(hide?'display:none;':'');
  const N=['Escolha o plano','Edite as atividades','Publique a versão'];
  v.prev_t=step>1?('‹ '+N[step-2]):''; v.next_t=step<3?(N[step]+' ›'):''; v.has_prev=step>1; v.has_next=step<3&&!!p;
  v.prev=()=>self.setState({step:Math.max(1,step-1),del:null,disc:false}); v.next=()=>{ if(!self.state.pid){ self.setState({g2toast:'Escolha um plano para avançar.'}); return; } self.setState({step:Math.min(3,step+1),del:null,disc:false}); };
  v.go2=()=>self.setState({step:2}); }
'''


def bloco(titulo, desc, corpo, acao='', hole=False):
    t = titulo if hole else esc(titulo)
    d = desc if hole else esc(desc)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{d}</div></div>{acao}</div>'
            f'<div style="padding: 0 16px 14px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')


def aside(pre, titulo_hole, sub_hole, corpo, w=560):
    """Painel lateral pela direita com Salvar/Cancelar e aviso de alterações não salvas (holes: {pre}_open/_close/_key/_save/_warn/_discard/_keep/_nerr)."""
    return IF(f'{pre}_open',
        f'<div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
        f'<button type="button" aria-label="Fechar" onClick="{H(pre+"_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
        f'<aside role="dialog" aria-label="{H(titulo_hole)}" onKeyDown="{H(pre+"_key")}" style="position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
        f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1; letter-spacing: -.02em;">{H(titulo_hole)}</h2>'
        f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45; margin-top: -6px;">{H(sub_hole)}</div>'
        + IF(f'{pre}_nerr', f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div>')
        + corpo + '<div style="flex-grow: 1;"></div>'
        + IF(f'{pre}_warn', f'<div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
             f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div>')
        + f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; border-top: 1px solid {LINE};">'
          f'<button type="button" onClick="{H(pre+"_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H(pre+"_save")}" style="{BTN_ST(True,True)}">Salvar</button></div>'
        f'</aside></div>')


LBL = f'font-size: 12px; font-weight: 600; color: {MUTED};'
SEC = f'font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;'
ERR = f'font-size: 12px; font-weight: 700; color: {RED};'


def err(hole_has, hole_msg): return IF(hole_has, f'<span role="alert" style="{ERR}">{H(hole_msg)}</span>')


PA_LINHA_CSS = '\n.pa-atividade{border:1px solid #E4E9E5;border-radius:12px;background:#fff;container-type:inline-size}\n.pa-atividade-linha{display:grid;grid-template-columns:38px 175px minmax(0,1fr) 80px 115px 38px;gap:10px;align-items:center;padding:8px 10px;font-size:13px}\n.pa-gatilho,.pa-atividade-nome{display:flex;flex-direction:column;gap:3px;min-width:0;overflow-wrap:anywhere}\n.pa-gatilho b{font-size:13px}.pa-gatilho>span,.pa-operacao,.pa-contagem{font-size:12px;color:#65736A}\n.pa-editar{border:0;background:transparent;padding:6px 0;font:inherit;font-size:13.5px;font-weight:700;color:#1E7A4C;cursor:pointer;text-align:left;text-decoration:underline;text-underline-offset:3px}\n.pa-contagem,.pa-custo{text-align:right}.pa-custo{font-weight:700;font-variant-numeric:tabular-nums}\n.pa-expandir.g2car,.pa-excluir.g2del{width:38px;height:44px}.pa-atividade button:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px;border-radius:4px}\n.pa-insumos{padding:8px 16px 12px 58px;background:#FBFCFA;border-top:1px solid #E4E9E5;border-radius:0 0 12px 12px}\n.pa-insumos-rolagem{overflow-x:auto}.pa-insumos-rolagem>div,.pa-insumos-rolagem>sc-for>div{min-width:720px}\n.pa-dose{font:inherit;font-variant-numeric:tabular-nums;color:inherit;background:transparent;border:0;border-bottom:1px dashed #A9B4AC;border-radius:4px 4px 0 0;padding:3px 5px;cursor:text}\n@media (hover:hover){.pa-dose:hover{background:#EEF5F0;border-bottom-color:#1E7A4C}}.pa-dose:focus-visible{background:#EEF5F0;border-bottom-color:#1E7A4C}\n@container (max-width:760px){.pa-atividade-linha{grid-template-columns:38px minmax(90px,1fr) minmax(0,2fr) 38px;gap:4px 8px}.pa-expandir{grid-column:1;grid-row:1 / 3}.pa-gatilho{grid-column:2;grid-row:1 / 3}.pa-atividade-nome{grid-column:3;grid-row:1}.pa-excluir{grid-column:4;grid-row:1 / 3}.pa-contagem{grid-column:3;grid-row:2;text-align:left}.pa-custo{grid-column:3;grid-row:3;text-align:left}.pa-insumos{padding:8px 12px}}\n'

def build():
    fname = 'PA.dc.html'; E._reset_screen(fname)
    EXTRA.append('<style>'+PA_LINHA_CSS+'</style>')
    dd = _dados()
    # ---------- etapa 1 · biblioteca por cultura (cards compactos) ----------
    card = (f'<button type="button" class="g2card" aria-current="{H("c.cur")}" onClick="{H("c.open")}" aria-label="{H("c.lab")}" style="{H("c.st")}">'
            f'<span style="display: flex; align-items: flex-start; gap: 8px; width: 100%;"><b style="font-size: 14.5px; flex-grow: 1; line-height: 1.3;">{H("c.nome")}</b>'
            f'<span style="font-size: 12px; font-weight: 700; color: {MUTED}; white-space: nowrap; padding-top: 2px;">{H("c.ver")}</span></span>'
            f'<span style="display: flex; width: 100%;"><span style="{H("c.est_st")}">{H("c.est")}</span></span>'
            f'<span style="display: flex; gap: 18px; font-size: 12.5px; color: {MUTED};"><span><b style="font-size: 15px; color: {INK};">{H("c.natv")}</b> atividades</span>'
            f'<span><b style="font-size: 15px; color: {INK};">{H("c.custo")}</b> insumos/ha</span></span>'
            f'<span style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;"><span style="font-size: 11.5px; color: {MUTED}; margin-right: 2px;">Gatilhos</span>'
            + FOR('c.gats', 'g', f'<span style="display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 600; color: {INK}; border: 1px solid {LINE};">{H("g.t")}</span>')
            + IF('c.semgat', f'<span style="font-size: 11.5px; color: {MUTED};">—</span>') + '</span>'
            f'<span style="display: flex; align-items: flex-end; gap: 10px; width: 100%; border-top: 1px solid {LINE}; padding-top: 8px; font-size: 12.5px;">'
            f'<span style="display: flex; flex-direction: column; gap: 1px; flex-grow: 1; min-width: 0;"><span style="{H("c.aplst")}">{H("c.apl")}</span>'
            f'<span style="font-size: 11.5px; color: {MUTED};">{H("c.apl2")}</span></span>'
            f'<span class="g2card-cta" aria-hidden="true">Abrir plano <span style="font-size: 14px; line-height: 1;">→</span></span></span></button>')
    lib = (f'<div style="display: flex; flex-wrap: wrap; gap: 16px 18px; align-items: flex-start;">'
           + FOR('lib', 'cu',
              f'<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px; min-width: 0; max-width: 100%;"><div style="{SEC}">{H("cu.t")} <span style="font-weight: 600; letter-spacing: 0; text-transform: none;">· {H("cu.n")}</span></div>'
              f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch;">'
              + FOR('cu.cards', 'c', f'<div style="display: flex; width: 336px; max-width: 100%;">{card}</div>') + '</div></div>', 2)
           + '</div>')
    qf = (f'<div role="group" aria-label="Filtrar planos por cultura" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">'
          + FOR('pa_qf', 'qc', f'<button type="button" aria-pressed="{H("qc.on")}" onClick="{H("qc.go")}" style="{H("qc.st")}">{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button>', 6)
          + '</div>')
    acao_bloco = f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'
    s1 = bloco('Biblioteca de planos por cultura', 'Abra um plano para editar as atividades ou crie um novo; cada plano tem versões publicadas.', qf + lib, acao=acao_bloco)

    # ---------- etapa 2 · plano aberto ----------
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
               f'<button type="button" onClick="{H("a.addOk")}" style="{_MINIP}">Incluir</button><button type="button" onClick="{H("a.addNao")}" style="{_MINI}">Cancelar</button></div>'
               + IF('a.addTemErr', f'<div role="alert" style="font-size: 12px; color: {RED}; padding-top: 4px;">{H("a.addErr")}</div>'))
    inl = (IF('a.rmvTem', f'<div role="status" style="display: flex; align-items: center; gap: 10px; margin-top: 6px; padding: 6px 10px; border-radius: 8px; background: {GRAYS}; font-size: 12.5px;"><span style="flex-grow: 1;">{H("a.rmvT")}</span>'
                          f'<button type="button" onClick="{H("a.volta")}" style="{_MINI}">Desfazer</button></div>')
           + IF('a.addOff', f'<div style="padding-top: 8px;"><button type="button" aria-label="{H("a.addLab")}" onClick="{H("a.addIni")}" style="{_MINI}">+ Incluir insumo</button></div>', True)
           + IF('a.addOn', add_row))
    atv = (f'<div class="pa-atividade" style="{H("a.rst")}">'
           f'<div class="pa-atividade-linha">'
           f'<button type="button" class="g2car pa-expandir" aria-label="{H("a.lab")}" title="{H("a.lab")}" aria-expanded="{H("a.open")}" aria-controls="{H("a.detalhesId")}" onClick="{H("a.tog")}">{H("a.sym")}</button>'
           f'<span class="pa-gatilho"><b>{H("a.gatilho")}</b>' + IF('a.hasFull', f'<span>{H("a.gatilhoFull")}</span>') + '</span>'
           f'<span class="pa-atividade-nome"><button type="button" class="pa-editar" onClick="{H("a.edit")}" title="Editar atividade">{H("a.nome")}</button>'
           f'<span style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0;"><span class="pa-operacao">{H("a.op")}</span>' + IF('a.hasChg', f'<span style="{H("a.chgst")} padding: 0 8px; font-size: 11px; line-height: 16px;">{H("a.chg")}</span>') + '</span></span>'
           f'<span class="pa-contagem">{H("a.np")}</span><span class="pa-custo">{H("a.custo")}</span>'
           + IF('a.notAsking', f'<button type="button" class="g2del pa-excluir" aria-label="{H("a.dlab")}" title="Excluir atividade" onClick="{H("a.ask")}">{E._TRASH}</button>', True)
           + IF('a.asking', '<span class="pa-excluir"></span>') + '</div>'
           + IF('a.asking', f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 12px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">'
                f'<span style="flex-grow: 1;">{H("a.delmsg")}</span><button type="button" onClick="{H("a.yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir atividade</button><button type="button" onClick="{H("a.no")}" style="{_MINI}">Manter</button></div>')
           + f'<div id="{H("a.detalhesId")}" role="region" aria-label="{H("a.detalhesLab")}">'
           + IF('a.open', '<div class="pa-insumos">'
                + IF('a.semProd', f'<div style="font-size: 12.5px; color: {MUTED}; padding: 6px 0;">Sem insumos · só operação</div>')
                + IF('a.temProd', '<div class="pa-insumos-rolagem">' + prod_hdr + FOR('a.prods', 'p', prod_row, 2) + '</div>') + inl + '</div>') + '</div></div>')
    gat = FOR('t.atvs', 'a', atv, 1)
    grp = FOR('grp', 'g', f'<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px;">'
                          f'<div style="display: flex; align-items: baseline; gap: 10px; border-top: 1px solid {LINE}; padding-top: 10px;"><div style="display: flex; flex-direction: column; gap: 1px; flex-grow: 1; min-width: 0;">'
                          f'<span style="font-size: 13.5px; font-weight: 800;">{H("g.t")}</span><span style="font-size: 12.3px; color: {MUTED};">{H("g.d")}</span></div>'
                          f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{H("g.n")}</span></div>'
                          + FOR('g.gats', 't', gat, 2) + '</div>', 1)
    head2 = (f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h2 style="margin: 0; font-family: {DISP}; font-size: 20px; letter-spacing: -.02em;">{H("p_nome")}</h2>'
             f'<span style="{H("p_est_st")}">{H("p_est")}</span><span style="font-size: 13px; color: {MUTED};">{H("k2")}</span></div>')
    banner = (IF('ban_r', f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
                 f'<span style="flex-grow: 1; min-width: 0;">{H("ban_t")}</span>'
                 + IF('nodisc', f'<button type="button" onClick="{H("disc_ask")}" style="{_MINI}">Descartar rascunho</button><button type="button" onClick="{H("ban_pub")}" style="{_MINIP}">Revisar e publicar ›</button>', True)
                 + IF('disc', f'<span role="alert" style="flex-basis: 100%; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: {RED};"><span style="flex-grow: 1;">{H("disc_t")}</span>'
                      f'<button type="button" onClick="{H("disc_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Descartar rascunho</button><button type="button" onClick="{H("disc_no")}" style="{_MINI}">Manter</button></span>')
                 + '</div>'))
    xbtn = f'<button type="button" onClick="{H("x_tog")}" style="{_MINI} display: inline-flex; align-items: center; gap: 5px; flex-shrink: 0;">{E.seta_xtog(H("x_up"),H("x_down"))}{H("x_lab")}</button>'
    vazio = bloco('Nenhuma atividade ainda', 'Inclua a primeira atividade: defina o gatilho, a operação e os produtos com dose por hectare.',
                  f'<div><button type="button" onClick="{H("prim_fn")}" style="{_MINIP} font-size: 13px; padding: 8px 12px;">Incluir atividade</button></div>')
    qf_op = (f'<div role="group" aria-label="Filtrar atividades por operação" style="display: flex; flex-wrap: wrap; gap: 6px;">'
             + FOR('pa_opf', 'qo', f'<button type="button" aria-pressed="{H("qo.on")}" title="{H("qo.lab")}" onClick="{H("qo.go")}" style="{H("qo.st")}">{H("qo.t")} <span style="opacity: .75;">{H("qo.n")}</span></button>', 5)
             + '</div>')
    barra = (f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="flex-grow: 1; min-width: 0;">' + IF('tem_opf', qf_op) + '</div>' + xbtn + acao_bloco + '</div>')
    s2 = head2 + banner + IF('vazio', vazio) + IF('tem_atv', bloco('Atividades do plano', 'Na seta, altere dose e insumos direto na tabela. Clique na atividade para mudar gatilho e operação.', barra + f'<div class="rola" style="display: flex; flex-direction: column; gap: 10px;">{grp}</div>'))

    # ---------- etapa 3 · publicar ----------
    g_cv = grid([dict(k='saf', l='Safra'), dict(k='local', l='Talhão ou parcela'), dict(k='cult', l='Cultura e variedade'),
                 dict(k='area', l='Área', t='num', a='r', u='ha'), dict(k='ver', l='Versão aplicada'), dict(k='sit', l='Situação', w=420)],
                [], edit=dict(m='none'), search=False, total=False, gid='g_cv')
    dif = (FOR('dif', 'd', f'<div style="display: grid; grid-template-columns: 86px minmax(0, 1fr); gap: 10px; align-items: baseline; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                           f'<span><span style="{H("d.st")}">{H("d.k")}</span></span><span><b>{H("d.n")}</b> <span style="color: {MUTED};">· {H("d.t")}</span></span></div>', 2)
           + IF('dif_vazio', f'<div style="font-size: 13px; color: {MUTED};">O rascunho está igual à versão publicada.</div>')
           + f'<div style="font-size: 13px; font-weight: 700; padding-top: 6px; border-top: 1px solid {LINE};">{H("dif_custo")}</div>')
    s3 = (IF('s3_has', bloco(H('dif_tit'), 'Confira cada alteração antes de publicar; publicar cria a nova versão sem mudar os cultivos.', dif, acao=acao_bloco, hole=True))
          + IF('s3_none', bloco('Nada a publicar', 'Edite as atividades na etapa 2; salvar cria o rascunho da próxima versão.',
                                f'<div><button type="button" onClick="{H("go2")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">‹ Edite as atividades</button></div>'))
          + bloco('Cultivos que usam este plano', 'Confira quem continua na versão em que foi aplicado; a troca de versão é decidida por cultivo em Planejar safra.',
                  f'<div style="{H("imp_st")}">{H("imp")}</div>' + IF('tem_cv', g_cv))
          + bloco('Versões', 'Consulte as versões do plano e quantos cultivos usam cada uma.',
                  FOR('hist', 'h', f'<div style="display: grid; grid-template-columns: 48px 180px 110px minmax(0, 1fr); gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                                   f'<b>{H("h.t")}</b><span style="color: {MUTED};">{H("h.at")}</span><span><span style="{H("h.stst")}">{H("h.st")}</span></span><span>{H("h.uso")}</span></div>', 2)))

    corpo = ''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{T() if i == 1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}</div></sc-if>'
                    for i, s in enumerate([s1, s2, s3], 1))

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
    prim = f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'
    HEIGHTS37[fname] = 1500
    shell37('PA', 'Planos agronômicos', corpo, fname=fname,
            subtitle='Mantenha os planos padrão por cultura: gatilho, atividades, produtos e doses. Cada alteração vira uma nova versão; cultivos já aplicados não mudam sozinhos.',
            steps=steps_state(NOMES), primary_html=None,  # a ação principal mora no bloco onde age (Novo plano, Incluir atividade, Publicar versão)
            ctx=('Fazenda Santa Rita', H('ctx_pl'), None), search=False)
    return fname


if __name__ == '__main__':
    import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(build())
