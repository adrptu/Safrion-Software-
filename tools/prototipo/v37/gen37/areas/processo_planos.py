# -*- coding: utf-8 -*-
"""Agrícola › Planos agronômicos — uma só tela de trabalho (PA.dc.html) com 3 etapas:
1 Escolha o plano (biblioteca por cultura, cards) · 2 Edite as atividades (Gatilho → Atividades → Produtos e doses)
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
function paOpen(self,id){ const p=paPlan(self,id); self.setState({pid:id,step:2,del:null,disc:false,flash:null,g2toast:'Plano aberto: '+p.nome+(p.rasc?' · rascunho v'+p.rasc.v:'')}); }
// ---------- biblioteca ----------
function paLib(self){ const ps=paPlans(self); const cu=[]; ps.forEach(p=>{ if(cu.indexOf(p.cultura)<0) cu.push(p.cultura); }); const sel=self.state.pid;
  return cu.map(c=>{ const cs=ps.filter(p=>p.cultura===c);
    return {t:c, n:cs.length+(cs.length>1?' planos':' plano'), cards:cs.map(p=>{ const atv=paShown(p); const tp=[];
      atv.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
      const est=p.versao===0?['Rascunho v1','y']:(p.rasc?['Rascunho v'+p.rasc.v+' em edição','y']:['Publicado','g']); const nc=paCults(p.id).length;
      return {nome:p.nome, ver:(p.versao?'v'+p.versao:'sem versão publicada'), est:est[0], est_st:paChip(est[1]), natv:String(atv.length), custo:paRS(paCt(atv)),
        gats:tp.map(t=>({t})), semgat:!tp.length, apl:nc?('Aplicado em '+nc+(nc>1?' cultivos':' cultivo')):'Sem cultivos aplicados', apl2:nc?paAplCurto(p.id):'', aplst:nc?'font-weight:700;':'color:#65736A;',
        st:'display:flex;flex-direction:column;gap:9px;padding:12px 15px;border-radius:12px;background:#fff;text-align:left;font-family:inherit;color:#15201A;min-width:0;width:100%;box-sizing:border-box;cursor:pointer;'+(p.id===sel?'border:1px solid #1E7A4C;box-shadow:0 0 0 1px #1E7A4C;':'border:1px solid #E4E9E5;'),
        lab:'Abrir plano '+p.nome, open:()=>paOpen(self,p.id)}; })}; }); }
// ---------- etapa 2 · cards Gatilho → Atividades → Produtos ----------
function paAtvV(self,p,a,pub){ const xa=self.state.xa||{}; const open=!!xa[a.id]; const del=self.state.del===a.id; const o=pub[a.id];
  let chg=''; if(p.rasc&&p.versao){ if(!o) chg='Nova'; else if(paNorm(o)!==paNorm(a)) chg='Alterada'; }
  const np=a.prods.length; const nv=p.rasc?p.rasc.v:p.versao+1; const fl=self.state.flash===a.id;
  const noBtn=(e)=>!(e&&e.target&&e.target.closest&&e.target.closest('button,input,select,a'));
  return {nome:a.nome, op:a.op, np:np?(np+(np>1?' produtos':' produto')):'só operação', custo:np?paRS(paCa(a))+'/ha':'—', open, sym:open?'▾':'▸', lab:(open?'Recolher ':'Expandir ')+a.nome,
    tog:()=>{ const n=Object.assign({},self.state.xa||{}); n[a.id]=!open; self.setState({xa:n}); },
    edit:()=>paEdit(self,a.id), openr:(e)=>{ if(noBtn(e)) paEdit(self,a.id); },
    key:(e)=>{ if(!e||(e.key!=='Enter'&&e.key!==' ')||!noBtn(e)) return; e.preventDefault(); paEdit(self,a.id); },
    rst:'display:grid;grid-template-columns:22px minmax(0,1fr) 110px 130px 34px;gap:10px;align-items:center;padding:7px 12px;border-top:1px solid #E4E9E5;font-size:13px;'+(fl?'background:#E4F3E9;':''),
    chg, hasChg:!!chg, chgst:paChip(chg==='Nova'?'g':'y'),
    asking:del, notAsking:!del, ask:()=>self.setState({del:a.id}), no:()=>self.setState({del:null}), yes:()=>paDel(self,p.id,a.id), dlab:'Excluir atividade '+a.nome,
    delmsg:'Excluir “'+a.nome+'”'+(p.versao?' do rascunho v'+nv+'? A v'+p.versao+' publicada e os cultivos que a usam não mudam.':' do rascunho?'),
    semProd:!np, temProd:!!np,
    prods:a.prods.map(x=>({grupo:x.grupo, prod:x.prod, dose:paQ(x.dose)+' '+x.un+'/ha', preco:paRS(x.preco)+'/'+x.un, custo:paRS(x.dose*x.preco)+'/ha'})) }; }
function paS2(self,v,p){ const atv=paWork(p); const xg=self.state.xg||{}; const pub={}; (p.atividades||[]).forEach(a=>{ pub[a.id]=a; });
  const G={}; atv.forEach(a=>{ const g=paGrp(a.g); const k=paGkey(a.g); const m=G[g]||(G[g]={}); (m[k]||(m[k]={g:a.g,atvs:[]})).atvs.push(a); });
  v.grp=['DAP','DATA','COL'].filter(g=>G[g]).map(g=>{ const list=Object.values(G[g]).sort((A,B)=>{ const a=paOrd(A.g), b=paOrd(B.g);
      if(g==='DATA') return a<b?-1:(a>b?1:0); if(a!==b) return a-b; return A.g.tipo<B.g.tipo?-1:1; });
    const nat=list.reduce((s,t)=>s+t.atvs.length,0);
    return {t:PA_GRP[g].t, d:PA_GRP[g].d, n:list.length+(list.length>1?' gatilhos':' gatilho')+' · '+nat+(nat>1?' atividades':' atividade'),
      gats:list.map(t=>{ const key=paGkey(t.g); const open=xg[key]!==false; const gl=paGat(t.g);
        return {t:gl.t, full:gl.full, hasFull:!!gl.full, open, sym:open?'▾':'▸', lab:(open?'Recolher ':'Expandir ')+gl.t,
          tog:()=>{ const n=Object.assign({},self.state.xg||{}); n[key]=!open; self.setState({xg:n}); },
          res:t.atvs.length+(t.atvs.length>1?' atividades':' atividade')+' · '+(paCt(t.atvs)>0?paRS(paCt(t.atvs))+'/ha':'só operação'),
          atvs:t.atvs.map(a=>paAtvV(self,p,a,pub))}; })}; });
  v.vazio=!atv.length; v.tem_atv=!!atv.length;
  v.x_all=()=>{ const xa={}; atv.forEach(a=>{ xa[a.id]=true; }); self.setState({xg:{},xa}); };
  v.x_none=()=>{ const n={}; atv.forEach(a=>{ n[paGkey(a.g)]=false; }); self.setState({xg:n,xa:{}}); };
  const est=p.versao===0?['Rascunho v1 · ainda não publicado','y']:(p.rasc?['Rascunho v'+p.rasc.v+' em edição','y']:['Publicado · v'+p.versao,'g']);
  v.p_nome=p.nome; v.p_est=est[0]; v.p_est_st=paChip(est[1]);
  const tp=[]; atv.forEach(a=>{ const t=PA_TAG[a.g.tipo]; if(tp.indexOf(t)<0) tp.push(t); }); tp.sort((a,b)=>PA_TORD.indexOf(a)-PA_TORD.indexOf(b));
  v.k2=p.cultura+' · '+atv.length+(atv.length===1?' atividade':' atividades')+' · '+paRS(paCt(atv))+'/ha de insumos'+(tp.length?' · gatilhos: '+tp.join(', '):'');
  const apl=paApl(p.id); const nd=paDiff(p).length; const nv=p.rasc?p.rasc.v:p.versao+1;
  v.ban_r=!!p.rasc; v.ban_n=!p.rasc;
  if(p.versao===0) v.ban_t='Rascunho v1 · ainda não publicado. Publique na etapa 3 para poder aplicar em Planejar safra.';
  else if(p.rasc) v.ban_t='Rascunho v'+p.rasc.v+' · '+nd+(nd===1?' alteração não publicada. ':' alterações não publicadas. ')+(apl?'Aplicado em '+apl+' — não serão alterados.':'Nenhum cultivo usa este plano.');
  else v.ban_t='Editar cria o rascunho v'+nv+'; a v'+p.versao+' publicada'+(apl?' e os cultivos que a usam ('+apl+')':'')+' não mudam.';
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
  const d=a?{op:a.op,nome:a.nome,outra:(PA0.atvs[a.op]||[]).indexOf(a.nome)<0,tipo:(antes?'DAPA':a.g.tipo),dias:(a.g.tipo==='DATA'?'':String(Math.abs(Number(a.g.dias)))),data:(a.g.data||''),prods:a.prods.map(x=>({prod:x.prod,dose:String(x.dose).replace('.',',')}))}
           :{op:'',nome:'',outra:false,tipo:'DAP',dias:'',data:'',prods:[]};
  self.setState({fm:{aid:aid||null,draft:d,orig:JSON.stringify(d),errs:{},warn:false,rm:null},del:null}); }
function paFmUpd(self,patch,errk){ const cur=self.state.fm; const nd=Object.assign({},cur.draft,patch); const ne=Object.assign({},cur.errs||{}); (errk||Object.keys(patch)).forEach(k=>{ delete ne[k]; });
  self.setState({fm:Object.assign({},cur,{draft:nd,errs:ne,warn:false})}); }
function paSetProd(self,i,patch){ const cur=self.state.fm; const ps=cur.draft.prods.map((x,j)=>j===i?Object.assign({},x,patch):x); paFmUpd(self,{prods:ps},['p'+i]); }
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
  let tot=0;
  v.fm_prods=d.prods.map((x,i)=>{ const c=PA0.cat[x.prod]; const n=g2num(x.dose); const e=er['p'+i]||''; const ask=fm.rm===i; if(c&&!isNaN(n)) tot+=n*c.preco;
    return {prod:x.prod, opts:PA0.popts, dose:x.dose, un:c?c.un+'/ha':'/ha', preco:c?paRS(c.preco)+'/'+c.un:'—', custo:(c&&!isNaN(n))?paRS(n*c.preco)+'/ha':'—',
      err:e, hasErr:!!e, sid:'fm_prod_'+i, fid:'fm_dose_'+i, sst:paIst(e&&!x.prod), ist:paIst(e&&x.prod,'84px')+'text-align:right;',
      setp:(ev)=>paSetProd(self,i,{prod:ev.target.value}), setd:(ev)=>paSetProd(self,i,{dose:ev.target.value}),
      asking:ask, notAsking:!ask, lab:'Remover '+(x.prod||'produto'), dlab:'Dose de '+(x.prod||'produto'),
      ask:()=>self.setState({fm:Object.assign({},self.state.fm,{rm:i})}), no:()=>self.setState({fm:Object.assign({},self.state.fm,{rm:null})}),
      yes:()=>{ const cur=self.state.fm; const ne={}; Object.keys(cur.errs||{}).forEach(k=>{ if(k.charAt(0)!=='p') ne[k]=cur.errs[k]; });
        self.setState({fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,{prods:cur.draft.prods.filter((y,j)=>j!==i)}),errs:ne,rm:null,warn:false})}); } }; });
  v.fm_semprod=!d.prods.length; v.fm_temprod=!!d.prods.length; v.fm_tot=paRS(tot)+'/ha';
  v.fm_addp=()=>{ const cur=self.state.fm; self.setState({fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,{prods:cur.draft.prods.concat([{prod:'',dose:''}])}),warn:false})}); };
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
  const seen={}; const prods=[];
  d.prods.forEach((x,i)=>{ const c=PA0.cat[x.prod]; if(!x.prod||!c){ er['p'+i]='Escolha o produto.'; return; } if(seen[x.prod]){ er['p'+i]='Produto repetido nesta atividade.'; return; } seen[x.prod]=1;
    const n=paNum(x.dose); if(String(x.dose).trim()===''||isNaN(n)||n<=0){ er['p'+i]='Informe a dose por hectare (maior que zero).'; return; }
    prods.push({grupo:c.grupo,prod:x.prod,dose:n,un:c.un,preco:c.preco}); });
  if(Object.keys(er).length){ self.setState({fm:Object.assign({},fm,{errs:er,warn:false})}); return; }
  const ps=paClone(paPlans(self)); const p=ps.find(x=>x.id===self.state.pid); const novo=!p.rasc;
  if(novo) p.rasc={v:p.versao+1,atividades:paClone(p.atividades)};
  const atv={id:fm.aid||('n'+Date.now().toString(36)),nome:String(d.nome).trim(),op:d.op,g:{tipo:(d.tipo==='DAPA'?'DAP':d.tipo),dias,data},prods};
  const L=p.rasc.atividades; const ix=L.findIndex(a=>a.id===fm.aid); if(ix>=0) L[ix]=atv; else L.push(atv);
  const xg=Object.assign({},self.state.xg||{}); xg[paGkey(atv.g)]=true; const xa=Object.assign({},self.state.xa||{}); xa[atv.id]=true;
  const nc=paCults(p.id).length;
  const msg=(novo&&p.versao)?('Rascunho v'+p.rasc.v+' criado com a alteração. A v'+p.versao+' publicada'+(nc?paUsam(nc):'')+' não mudam.')
                            :((fm.aid?'Atividade salva':'Atividade incluída')+' no rascunho v'+p.rasc.v+'.');
  self.setState({pl:ps,fm:null,xg,xa,flash:atv.id,g2toast:msg}); }
// ---------- novo plano ----------
function paNewPlan(self){ const d={nome:'',cultura:'',base:''}; self.setState({np:{draft:d,orig:JSON.stringify(d),errs:{},warn:false}}); }
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
  v.lib=paLib(self);
  v.ctx_pl=p?(p.nome+' · '+(p.rasc?'rascunho v'+p.rasc.v:'v'+p.versao)):'Nenhum plano escolhido';
  if(p){ paS2(self,v,p); paS3(self,v,p); } else { v.grp=[]; v.dif=[]; v.hist=[]; }
  paFm(self,v); paNp(self,v);
  const prim={1:['Novo plano',()=>paNewPlan(self)],2:['Incluir atividade',()=>paEdit(self,null)],3:[(p&&p.rasc)?('Publicar versão v'+p.rasc.v):'Publicar versão',()=>paPub(self)]}[step];
  v.prim_t=prim[0]; v.prim_fn=prim[1]; const hide=(step>1&&!p)||(step===3&&!(p&&p.rasc));
  v.prim_st='padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;'+(hide?'display:none;':'');
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


def navpe():
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">'
            + IF('has_prev', f'<button type="button" onClick="{H("prev")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">{H("prev_t")}</button>')
            + '<span style="flex-grow: 1;"></span>'
            + IF('has_next', f'<button type="button" onClick="{H("next")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">{H("next_t")}</button>') + '</div>')


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


def build():
    fname = 'PA.dc.html'; E._reset_screen(fname)
    dd = _dados()
    # ---------- etapa 1 · biblioteca por cultura (cards compactos) ----------
    card = (f'<button type="button" class="g2ed" onClick="{H("c.open")}" aria-label="{H("c.lab")}" style="{H("c.st")}">'
            f'<span style="display: flex; align-items: flex-start; gap: 8px; width: 100%;"><b style="font-size: 14.5px; flex-grow: 1; line-height: 1.3;">{H("c.nome")}</b>'
            f'<span style="font-size: 12px; font-weight: 700; color: {MUTED}; white-space: nowrap; padding-top: 2px;">{H("c.ver")}</span></span>'
            f'<span style="display: flex; width: 100%;"><span style="{H("c.est_st")}">{H("c.est")}</span></span>'
            f'<span style="display: flex; gap: 18px; font-size: 12.5px; color: {MUTED};"><span><b style="font-size: 15px; color: {INK};">{H("c.natv")}</b> atividades</span>'
            f'<span><b style="font-size: 15px; color: {INK};">{H("c.custo")}</b> insumos/ha</span></span>'
            f'<span style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;"><span style="font-size: 11.5px; color: {MUTED}; margin-right: 2px;">Gatilhos</span>'
            + FOR('c.gats', 'g', f'<span style="display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 600; color: {INK}; border: 1px solid {LINE};">{H("g.t")}</span>')
            + IF('c.semgat', f'<span style="font-size: 11.5px; color: {MUTED};">—</span>') + '</span>'
            f'<span style="display: flex; flex-direction: column; gap: 1px; width: 100%; border-top: 1px solid {LINE}; padding-top: 8px; font-size: 12.5px;"><span style="{H("c.aplst")}">{H("c.apl")}</span>'
            f'<span style="font-size: 11.5px; color: {MUTED};">{H("c.apl2")}</span></span></button>')
    lib = (f'<div style="display: flex; flex-wrap: wrap; gap: 16px 18px; align-items: flex-start;">'
           + FOR('lib', 'cu',
              f'<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px; min-width: 0; max-width: 100%;"><div style="{SEC}">{H("cu.t")} <span style="font-weight: 600; letter-spacing: 0; text-transform: none;">· {H("cu.n")}</span></div>'
              f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch;">'
              + FOR('cu.cards', 'c', f'<div style="display: flex; width: 336px; max-width: 100%;">{card}</div>') + '</div></div>', 2)
           + '</div>')
    s1 = bloco('Biblioteca de planos por cultura', 'Abra um plano para editar as atividades ou crie um novo; cada plano tem versões publicadas.', lib)

    # ---------- etapa 2 · plano aberto ----------
    prod_hdr = (f'<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr) 110px 120px 110px; gap: 10px; padding: 6px 0 4px; {SEC} font-size: 10px;">'
                f'<span>Grupo</span><span>Produto</span><span style="text-align: right;">Dose/ha</span><span style="text-align: right;">Preço unitário</span><span style="text-align: right;">Custo/ha</span></div>')
    prod_row = (f'<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr) 110px 120px 110px; gap: 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: center;">'
                f'<span style="color: {MUTED};">{H("p.grupo")}</span><span style="font-weight: 600;">{H("p.prod")}</span><span style="text-align: right; font-variant-numeric: tabular-nums;">{H("p.dose")}</span>'
                f'<span style="text-align: right; color: {MUTED}; font-variant-numeric: tabular-nums;">{H("p.preco")}</span><span style="text-align: right; font-weight: 700; font-variant-numeric: tabular-nums;">{H("p.custo")}</span></div>')
    atv = (f'<div role="row" class="g2ed" tabIndex="0" onClick="{H("a.openr")}" onKeyDown="{H("a.key")}" style="{H("a.rst")}">'
           f'<button type="button" class="g2car" aria-label="{H("a.lab")}" title="{H("a.lab")}" aria-expanded="{H("a.open")}" onClick="{H("a.tog")}">{H("a.sym")}</button>'
           f'<span style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0;"><button type="button" onClick="{H("a.edit")}" title="Editar atividade" style="border: 0; background: transparent; padding: 0; font-family: inherit; font-size: 13.5px; font-weight: 700; color: {ACC}; cursor: pointer; text-align: left; text-decoration: underline; text-underline-offset: 3px;">{H("a.nome")}</button>'
           f'<span style="font-size: 12px; color: {MUTED};">{H("a.op")}</span>' + IF('a.hasChg', f'<span style="{H("a.chgst")}">{H("a.chg")}</span>') + '</span>'
           f'<span style="font-size: 12.5px; color: {MUTED}; text-align: right;">{H("a.np")}</span>'
           f'<span style="text-align: right; font-weight: 700; font-variant-numeric: tabular-nums;">{H("a.custo")}</span>'
           + IF('a.notAsking', f'<button type="button" class="g2del" aria-label="{H("a.dlab")}" title="Excluir atividade" onClick="{H("a.ask")}">{E._TRASH}</button>', True)
           + IF('a.asking', '<span></span>') + '</div>'
           + IF('a.asking', f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 12px 8px 44px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">'
                f'<span style="flex-grow: 1;">{H("a.delmsg")}</span><button type="button" onClick="{H("a.yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir atividade</button><button type="button" onClick="{H("a.no")}" style="{_MINI}">Manter</button></div>')
           + IF('a.open', f'<div style="padding: 2px 12px 10px 44px; background: #FBFCFA;">'
                + IF('a.semProd', f'<div style="font-size: 12.5px; color: {MUTED}; padding: 6px 0;">Sem insumos · só operação</div>')
                + IF('a.temProd', prod_hdr + FOR('a.prods', 'p', prod_row, 2)) + '</div>'))
    gat = (f'<div style="border: 1px solid {LINE}; border-radius: 12px; overflow: hidden;">'
           f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: {BG};">'
           f'<button type="button" class="g2car" aria-label="{H("t.lab")}" title="{H("t.lab")}" aria-expanded="{H("t.open")}" onClick="{H("t.tog")}">{H("t.sym")}</button>'
           f'<b style="font-size: 13.5px; white-space: nowrap;">{H("t.t")}</b>' + IF('t.hasFull', f'<span style="font-size: 12.5px; color: {MUTED};">{H("t.full")}</span>')
           + f'<span style="flex-grow: 1;"></span><span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H("t.res")}</span></div>'
           + IF('t.open', FOR('t.atvs', 'a', atv, 1), True) + '</div>')
    grp = FOR('grp', 'g', bloco(H('g.t'), H('g.d'), FOR('g.gats', 't', gat, 2),
                                acao=f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap; padding-top: 2px;">{H("g.n")}</span>', hole=True), 1)
    head2 = (f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h2 style="margin: 0; font-family: {DISP}; font-size: 20px; letter-spacing: -.02em;">{H("p_nome")}</h2>'
             f'<span style="{H("p_est_st")}">{H("p_est")}</span><span style="font-size: 13px; color: {MUTED};">{H("k2")}</span></div>')
    banner = (IF('ban_r', f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
                 f'<span style="flex-grow: 1; min-width: 0;">{H("ban_t")}</span>'
                 + IF('nodisc', f'<button type="button" onClick="{H("disc_ask")}" style="{_MINI}">Descartar rascunho</button><button type="button" onClick="{H("ban_pub")}" style="{_MINIP}">Revisar e publicar ›</button>', True)
                 + IF('disc', f'<span role="alert" style="flex-basis: 100%; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: {RED};"><span style="flex-grow: 1;">{H("disc_t")}</span>'
                      f'<button type="button" onClick="{H("disc_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Descartar rascunho</button><button type="button" onClick="{H("disc_no")}" style="{_MINI}">Manter</button></span>')
                 + '</div>')
              + IF('ban_n', f'<div style="padding: 9px 14px; border-radius: 12px; background: {GRAYS}; color: {INK}; font-size: 12.8px;">{H("ban_t")}</div>'))
    tool2 = (f'<div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 12.8px; color: {MUTED}; flex-grow: 1;">Clique no nome da atividade para editar gatilho, operação e produtos; a seta só expande.</span>'
             f'<button type="button" onClick="{H("x_all")}" title="Expandir tudo" style="{_MINI}">Expandir tudo</button><button type="button" onClick="{H("x_none")}" title="Recolher tudo" style="{_MINI}">Recolher tudo</button></div>')
    vazio = bloco('Nenhuma atividade ainda', 'Inclua a primeira atividade: defina o gatilho, a operação e os produtos com dose por hectare.',
                  f'<div><button type="button" onClick="{H("prim_fn")}" style="{_MINIP} font-size: 13px; padding: 8px 12px;">Incluir atividade</button></div>')
    s2 = head2 + banner + IF('tem_atv', tool2) + IF('vazio', vazio) + grp

    # ---------- etapa 3 · publicar ----------
    g_cv = grid([dict(k='saf', l='Safra'), dict(k='local', l='Talhão ou parcela'), dict(k='cult', l='Cultura e variedade'),
                 dict(k='area', l='Área', t='num', a='r', u='ha'), dict(k='ver', l='Versão aplicada'), dict(k='sit', l='Situação', w=420)],
                [], edit=dict(m='none'), search=False, total=False, gid='g_cv')
    dif = (FOR('dif', 'd', f'<div style="display: grid; grid-template-columns: 86px minmax(0, 1fr); gap: 10px; align-items: baseline; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                           f'<span><span style="{H("d.st")}">{H("d.k")}</span></span><span><b>{H("d.n")}</b> <span style="color: {MUTED};">· {H("d.t")}</span></span></div>', 2)
           + IF('dif_vazio', f'<div style="font-size: 13px; color: {MUTED};">O rascunho está igual à versão publicada.</div>')
           + f'<div style="font-size: 13px; font-weight: 700; padding-top: 6px; border-top: 1px solid {LINE};">{H("dif_custo")}</div>')
    s3 = (IF('s3_has', bloco(H('dif_tit'), 'Confira cada alteração antes de publicar; publicar cria a nova versão sem mudar os cultivos.', dif, hole=True))
          + IF('s3_none', bloco('Nada a publicar', 'Edite as atividades na etapa 2; salvar cria o rascunho da próxima versão.',
                                f'<div><button type="button" onClick="{H("go2")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">‹ Edite as atividades</button></div>'))
          + bloco('Cultivos que usam este plano', 'Confira quem continua na versão em que foi aplicado; a troca de versão é decidida por cultivo em Planejar safra.',
                  f'<div style="{H("imp_st")}">{H("imp")}</div>' + IF('tem_cv', g_cv))
          + bloco('Versões', 'Consulte as versões do plano e quantos cultivos usam cada uma.',
                  FOR('hist', 'h', f'<div style="display: grid; grid-template-columns: 48px 180px 110px minmax(0, 1fr); gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                                   f'<b>{H("h.t")}</b><span style="color: {MUTED};">{H("h.at")}</span><span><span style="{H("h.stst")}">{H("h.st")}</span></span><span>{H("h.uso")}</span></div>', 2)))

    corpo = ''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{T() if i == 1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}{navpe()}</div></sc-if>'
                    for i, s in enumerate([s1, s2, s3], 1))

    # ---------- painel: atividade (gatilho, nome, operação, produtos e doses) ----------
    prow = (f'<div style="display: grid; grid-template-columns: minmax(0, 1fr) auto 104px 30px; gap: 8px; align-items: center; padding: 8px 0; border-top: 1px solid {LINE};">'
            f'<select id="{H("p.sid")}" aria-label="Produto" value="{H("p.prod")}" onChange="{H("p.setp")}" style="{H("p.sst")}">' + FOR('p.opts', 'o', f'<option value="{H("o.v")}">{H("o.t")}</option>', 3) + '</select>'
            f'<span style="display: inline-flex; align-items: center; gap: 5px;"><input id="{H("p.fid")}" aria-label="{H("p.dlab")}" value="{H("p.dose")}" onChange="{H("p.setd")}" inputMode="decimal" style="{H("p.ist")}">'
            f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap; min-width: 34px;">{H("p.un")}</span></span>'
            f'<span style="display: flex; flex-direction: column; text-align: right; font-size: 12px; line-height: 1.3;"><b style="font-size: 12.8px;">{H("p.custo")}</b><span style="color: {MUTED};">{H("p.preco")}</span></span>'
            + IF('p.notAsking', f'<button type="button" class="g2del" aria-label="{H("p.lab")}" title="Remover produto" onClick="{H("p.ask")}">{E._TRASH}</button>', True)
            + IF('p.asking', '<span></span>') + '</div>'
            + IF('p.asking', f'<div role="alert" style="display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 8px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;"><span style="flex-grow: 1;">Remover este produto da atividade?</span>'
                 f'<button type="button" onClick="{H("p.yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Remover</button><button type="button" onClick="{H("p.no")}" style="{_MINI}">Manter</button></div>')
            + err('p.hasErr', 'p.err'))
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
               f'<div style="display: flex; flex-direction: column; gap: 0;"><div style="display: flex; align-items: baseline; gap: 8px; padding-bottom: 6px;"><span style="{SEC} flex-grow: 1;">Produtos e doses por hectare</span>'
               f'<span style="font-size: 12.5px; color: {MUTED};">Insumos: <b style="color: {INK};">{H("fm_tot")}</b></span></div>'
               + FOR('fm_prods', 'p', prow, 2)
               + IF('fm_semprod', f'<div style="font-size: 12.5px; color: {MUTED}; padding: 8px 0; border-top: 1px solid {LINE};">Sem produtos: a atividade é só operação (ex.: colheita, poda).</div>')
               + f'<div style="padding-top: 8px;"><button type="button" onClick="{H("fm_addp")}" style="{_MINI}">+ Incluir produto</button></div></div>')
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
            steps=steps_state(NOMES), primary_html=prim, ctx=('Fazenda Santa Rita', H('ctx_pl'), None), search=False)
    return fname


if __name__ == '__main__':
    import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(build())
