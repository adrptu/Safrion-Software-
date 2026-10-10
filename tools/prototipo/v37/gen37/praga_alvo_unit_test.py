# -*- coding: utf-8 -*-
"""AG-07 · Praga-alvo (pedido do proprietário, 09/10/2026: "na consulta agrofit tem que aparecer colunas das pragas alvo").
Com a cultura escolhida, a lista da Consulta Agrofit tem uma linha por USO na cultura (produto × praga-alvo), lida dos usos registrados
(agrofit_usos_cultura_*.json) e dos alvos do agrofit_indice.json: Praga-alvo (nomes comuns) e Nome científico, uma variável por coluna, com
filtro (coluna multivalorada por nome comum) e ordenação; busca por praga-alvo no mesmo uso; "Cultura do uso" separa o uso em "Todas as culturas".
Sem cultura, a lista continua por produto (6 colunas).
Parte 1 (node, sem navegador): g2lib.js + o JS da página (AGF_JS) com os arquivos reais; os esperados saem dos JSON, recalculados aqui.
Na base (9d4ff31) não existem agVisUso, agUsoLeaf, agModoUso nem AGF_COLS_U: os casos falham (stubs evitam parar no 1º).
Uso: python3 praga_alvo_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, json, subprocess, tempfile, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
sys.dont_write_bytecode = True
import areas.agronomia as AG
SITE = os.path.join(HERE, 'dados_agrofit', 'site')
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)
def nz(t): return ''.join(ch for ch in unicodedata.normalize('NFD', str(t)) if not unicodedata.combining(ch)).lower()
ld = lambda f: json.load(open(os.path.join(SITE, f), encoding='utf-8'))
META = ld('agrofit_meta.json'); IDX = ld('agrofit_indice.json')
NF = META['contagens']['fatias_cultura']; U = {}
for i in range(NF): U.update(ld(f'agrofit_usos_cultura_{i}.json')['culturas'])
CU = IDX['culturas']; TD = IDX['todasCulturas']; AL = IDX['alvos']
cid = lambda n: next(i for i, c in enumerate(CU) if c[0] == n)
aid = lambda s: next(i for i, a in enumerate(AL) if a[0] == s)
SJ, MA = cid('Soja'), cid('Mamão'); PH = aid('Phakopsora pachyrhizi')
F = {c: i for i, c in enumerate(IDX['campos'])}
REG = [str(r[F['registro']]) for r in IDX['produtos']]
def usos(cs): return {(REG[i], c, a) for c in cs for a, ps in U.get(str(c), []) for i in ps}

# ---------- node: g2lib + AGF_JS (a página) com os arquivos reais ----------
AGFD = AG.agf_dados()
COLS_U = getattr(AG, 'AGF_COLS_U', None)
COLS_P = getattr(AG, 'AGF_COLS_P', None) or [dict(k='prod', l='Produto · registro'), dict(k='ing', l='Ingrediente ativo · grupo químico'), dict(k='cls', l='Classe · modo de ação'),
                                              dict(k='cult', l='Culturas', t='num'), dict(k='tox', l='Tox · amb'), dict(k='faz', l='Na fazenda', t='num')]
SHIM = ("globalThis.print=(...a)=>console.log(...a);\nvar window={addEventListener(){}}; var location={hash:'',pathname:'/AG-07.dc.html'};\n"
        "const __fs=require('fs'), __p=require('path');\n")
dados = ('const AGF = ' + json.dumps(AGFD, ensure_ascii=False) + ';\nconst AGF_G = "g_agf";\n'
         + 'const AGF_COLS_U = ' + json.dumps(COLS_U, ensure_ascii=False) + ';\n'
         + 'const GRIDS = [' + json.dumps(dict(id='g_agf', cols=COLS_P, rows=[]), ensure_ascii=False) + '];\n')
caso = r'''
const SITE=__SITE__, NF=__NF__, SJ=__SJ__, MA=__MA__, PH=__PH__, FN=__FN__;
const ld=(f)=>JSON.parse(__fs.readFileSync(__p.join(SITE,f),'utf-8'));
const out={};
try{
  agPrep(ld('agrofit_indice.json')); AGX.st='ok'; const arr=[]; for(let i=0;i<NF;i++) arr.push(ld('agrofit_usos_cultura_'+i+'.json')); agPrepUsos(arr);
  out.fn={agVisUso:typeof agVisUso==='function',agUsoLeaf:typeof agUsoLeaf==='function',agModoUso:typeof agModoUso==='function',agUsoTot:typeof agUsoTot==='function'};
  if(out.fn.agVisUso&&out.fn.agModoUso&&out.fn.agUsoTot){
    AGX.uSt='carregando'; out.modoSemUsos=agModoUso({agf_cul:String(SJ)}); AGX.uSt='ok';
    out.modoSemCul=agModoUso({}); out.modoCul=agModoUso({agf_cul:String(SJ)});
    const S1={agf_cul:String(SJ)}; const R1=agVisUso(S1).rows;
    out.s1=R1.map(r=>r.id); out.s1pi=R1.map(r=>r.pi); out.tot1=agUsoTot(S1);
    out.s2=agVisUso({agf_cul:String(SJ),agf_semTD:true}).rows.map(r=>r.id); out.tot2=agUsoTot({agf_cul:String(SJ),agf_semTD:true});
    out.s3=agVisUso({agf_cul:String(SJ),agf_alvo:String(PH)}).rows.map(r=>r.id);
    out.s4=agVisUso({agf_cul:String(SJ),agf_q:'FERRUGEM asiatica'}).rows.map(r=>r.id);
    out.s5=agVisUso({agf_cul:String(MA),agf_cls:'Fungicida',agf_q:'antracnose'}).rows.map(r=>r.id);
    // repetição: a mesma consulta devolve as mesmas linhas (cache) e trocar de cultura e voltar não muda nada
    const a=agVisUso(S1).rows.length; agVisUso({agf_cul:String(MA)}); out.rep=[a,agVisUso({agf_cul:String(SJ)}).rows.length];
    // campos da linha: Praga-alvo (nomes comuns), Nome científico, Cultura do uso; filtro multivalorado pelos nomes comuns
    const pick=(st,a)=>agVisUso(st).rows.find(r=>String(r.id).split('@')[2]===String(a));
    const r=pick(S1,PH); out.rPH=r?{s:{alvo:r.s.alvo,cien:r.s.cien,ucul:r.s.ucul,prod:r.s.prod},m:r.m,p:{alvo:r.p.alvo,cien:r.p.cien}}:null;
    const semCom=AGX.I.alvos.findIndex(x=>x[0]&&!(x[1]||[]).length&&agUA(SJ).has(AGX.I.alvos.indexOf(x)));
    const rs=semCom>=0?pick(S1,semCom):null; out.rSem=rs?{a:semCom,s:{alvo:rs.s.alvo,cien:rs.s.cien},m:rs.m,p:rs.p.alvo}:null;
    const nada=AGX.I.alvos.findIndex(x=>!x[0]&&!(x[1]||[]).length);
    const rn=agVisUso({agf_cul:String(SJ),agf_alvo:String(nada)}).rows[0]||agVisUso({agf_cul:String(AGX.I.todasCulturas),agf_alvo:String(nada)}).rows[0]||null;
    out.rNada=rn?{s:{alvo:rn.s.alvo,cien:rn.s.cien},p:[rn.p.alvo,rn.p.cien]}:null;
    const td=agVisUso(S1).rows.find(x=>String(x.id).split('@')[1]===String(AGX.I.todasCulturas)); out.rTD=td?td.s.ucul:null;
    // ordenação e filtro da grade (g2sort/g2match da G2) sobre as colunas de uso
    const sp={id:'g_x',cols:AGF_COLS_U||[],rows:[]};
    const cmp=(a,b)=>a.localeCompare(b,'pt-BR',{numeric:true,sensitivity:'base'});
    const ordem=(L,d)=>{ const n=L.filter(Boolean); const k=L.findIndex(x=>!x); return {n:L.length,cheios:n.length,vaziosNoFim:k<0||L.slice(k).every(x=>!x),ok:n.every((x,i)=>i===0||d*cmp(x,n[i-1])>=0),ini:L.slice(0,4)}; };
    out.asc=ordem(g2sort(R1,sp,{so:{k:'alvo',d:false}}).map(x=>x.s.alvo),1);
    out.cienDesc=ordem(g2sort(R1,sp,{so:{k:'cien',d:true}}).map(x=>x.s.cien),-1);
    out.fil=R1.filter(x=>g2match(x,sp,{f:{alvo:[FN]}},null,{})).map(x=>x.id);
    out.filVazio=R1.filter(x=>g2match(x,sp,{f:{alvo:['(vazio)']}},null,{})).map(x=>x.id);
    out.ops=R1.slice(0,3).map(x=>[x.id,x.dr]);
    // chips de classe e de orgânicos contam usos, a mesma unidade da lista
    const V9=agVisUso({agf_cul:String(SJ)});
    out.u19={cntF:V9.cnt['Fungicida']||0,semCls:V9.semCls,nAll:V9.rows.length,orgN:V9.orgN,
      nF:agVisUso({agf_cul:String(SJ),agf_cls:'Fungicida'}).rows.length,nOrg:agVisUso({agf_cul:String(SJ),agf_org:true}).rows.length};
  }
  // A5 (revisão de 10/10): os chips contam as linhas que passam nos FILTROS DAS COLUNAS, cada chip sem o próprio filtro
  out.u20={fn:typeof agChipsCol==='function'};
  if(out.u20.fn&&out.fn.agVisUso){ const sp2=GR('g_agf'), P0=sp2.cols; sp2.cols=AGF_COLS_U; const gs={f:{alvo:[FN]}};
    const n=(st)=>agVisUso(st).rows.filter(x=>g2match(x,sp2,gs,null,{})).length;
    const C0=agChipsCol({agf_cul:String(SJ)},gs); out.u20.todas=[C0.semCls,n({agf_cul:String(SJ)})]; out.u20.fung=[C0.cnt['Fungicida']||0,n({agf_cul:String(SJ),agf_cls:'Fungicida'})];
    const C1=agChipsCol({agf_cul:String(SJ),agf_cls:'Fungicida'},gs); out.u20.org=[C1.orgN,n({agf_cul:String(SJ),agf_cls:'Fungicida',agf_org:true})];
    const C2=agChipsCol({agf_cul:String(SJ),agf_org:true},gs); out.u20.fungOrg=[C2.cnt['Fungicida']||0,n({agf_cul:String(SJ),agf_cls:'Fungicida',agf_org:true})];
    out.u20.semFiltro=agChipsCol({agf_cul:String(SJ)},{f:{}})===null;
    // praga-alvo com produtos para orgânicos (o nome com mais usos orgânicos em Soja): o chip de orgânicos = a lista com ele
    const cn={}; agVisUso({agf_cul:String(SJ),agf_org:true}).rows.forEach(r=>((r.m||{}).alvo||[]).forEach(x=>{ cn[x.id]=(cn[x.id]||0)+1; }));
    const FN2=Object.keys(cn).sort((a,b)=>cn[b]-cn[a])[0]; const g2={f:{alvo:[FN2]}}; const n2=(st)=>agVisUso(st).rows.filter(x=>g2match(x,sp2,g2,null,{})).length;
    const C3=agChipsCol({agf_cul:String(SJ)},g2); out.u20.org2=[FN2,C3.orgN,n2({agf_cul:String(SJ),agf_org:true}),C3.semCls,n2({agf_cul:String(SJ)}),C3.bio,n2({agf_cul:String(SJ),agf_cls:'Biológico'})];
    // lista por produto (sem cultura): filtro na coluna Classe · modo de ação
    sp2.cols=P0; const cc=P0.find(c=>c.k==='cls'); const L0=agVis({}).ids.map(i=>agLeaf(AGX.P[i])); const ck={}; L0.forEach(r=>g2fkeys(r,cc).forEach(x=>{ ck[x]=(ck[x]||0)+1; }));
    const fv=Object.keys(ck).filter(x=>/Herbicida/.test(x)).sort((a,b)=>ck[b]-ck[a])[0]; const gp={f:{cls:[fv]}};
    const np=(st)=>agVis(st).ids.filter(i=>g2match(agLeaf(AGX.P[i]),sp2,gp,null,{})).length; const CP=agChipsCol({},gp);
    out.u20.prod=[fv,CP.semCls,np({}),CP.cnt['Herbicida']||0,np({agf_cls:'Herbicida'}),CP.orgN,np({agf_org:true})]; }
}catch(e){ out.erro=String(e&&e.stack||e); }
console.log('JSON:'+JSON.stringify(out));
'''
for k, v in (('__SITE__', json.dumps(SITE)), ('__NF__', str(NF)), ('__SJ__', str(SJ)), ('__MA__', str(MA)), ('__PH__', str(PH)), ('__FN__', json.dumps(AL[PH][1][0]))): caso = caso.replace(k, v)
src = SHIM + open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read() + '\n' + dados + AG.AGF_JS + '\n' + caso
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(src)
r = subprocess.run(['node', '--max-old-space-size=2048', f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
lin = [l for l in r.stdout.splitlines() if l.startswith('JSON:')]
O = json.loads(lin[-1][5:]) if lin else {'erro': (r.stderr or r.stdout)[-1500:]}
chk('U0 o JS da página roda no node com os arquivos reais (sem erro)', 'erro' not in O, O.get('erro'))
fn = O.get('fn', {})
chk('U1 a página tem a lista por uso: agModoUso, agVisUso, agUsoLeaf e agUsoTot', all(fn.get(k) for k in ('agVisUso', 'agUsoLeaf', 'agModoUso', 'agUsoTot')), fn)
# colunas (fonte: AGF_COLS_U): Praga-alvo e Nome científico separados, uma variável por coluna, sem unidade entre parênteses
ks = [c['k'] for c in (COLS_U or [])]; ls = [c['l'] for c in (COLS_U or [])]
chk('U2 colunas por uso: Produto · registro | Praga-alvo | Nome científico | Cultura do uso | Ingrediente | Classe | Tox · amb | Na fazenda (Praga-alvo multivalorada; até 7 úteis + identificador)',
    ks == ['prod', 'alvo', 'cien', 'ucul', 'ing', 'cls', 'tox', 'faz'] and ls[1:3] == ['Praga-alvo', 'Nome científico'] and (COLS_U or [{}, {}])[1].get('multi') is True
    and not any('(' in l for l in ls) and [c['k'] for c in COLS_P] == ['prod', 'ing', 'cls', 'cult', 'tox', 'faz'], [ks, ls])
chk('U3 modo: sem cultura = por produto; com cultura e usos carregados = por uso; usos ainda carregando = por produto',
    O.get('modoSemCul') is False and O.get('modoCul') is True and O.get('modoSemUsos') is False, [O.get('modoSemCul'), O.get('modoCul'), O.get('modoSemUsos')])
E1 = usos((SJ, TD)); s1 = O.get('s1') or []
ids = lambda L: {tuple(x.split('@')[:1]) + tuple(int(y) for y in x.split('@')[1:]) for x in L}
chk(f'U4 Soja: uma linha por uso (produto × praga-alvo) em Soja + "Todas as culturas" = {len(E1)} linhas, nenhuma repetida, total "{len(E1)} usos em Soja"',
    len(s1) == len(E1) == len(set(s1)) and ids(s1) == E1 and O.get('tot1') == len(E1), [len(s1), len(E1), O.get('tot1')])
pis = O.get('s1pi') or []; vis = []
for p in pis:
    if not vis or vis[-1] != p: vis.append(p)
chk('U5 as linhas de cada produto ficam juntas (ordem dos produtos da lista)', len(vis) == len(set(vis)) and len(vis) > 100, [len(vis), len(set(vis))])
E2 = usos((SJ,)); s2 = O.get('s2') or []
chk(f'U6 "Ver só os de Soja" = {len(E2)} usos (= nUsos de Soja no índice, {CU[SJ][4]})', ids(s2) == E2 and len(s2) == len(E2) == CU[SJ][4] and O.get('tot2') == len(E2), [len(s2), len(E2), O.get('tot2')])
E3 = {x for x in E1 if x[2] == PH}; s3 = O.get('s3') or []
chk(f'U7 Praga-alvo (caixa de escolha) = Phakopsora pachyrhizi em Soja: {len(E3)} linhas, só desse alvo', ids(s3) == E3 and len(E3) > 10, [len(s3), len(E3)])
# busca sem acento e sem caixa: palavra no produto OU na praga-alvo do MESMO uso (cultura, nome científico e nomes comuns)
P = {}
for i, rr in enumerate(IDX['produtos']): P[REG[i]] = i
def hay_de():   # mesmo "hay" da página (agrofit_test.P), sem abrir o navegador: recalcula aqui
    IG = IDX['ingredientes']; GQ = IDX['gruposQuimicos']; CL = IDX['classes']
    import re as _re
    gr = AGFD['grupo_ref']; gen = {nz(g).strip() for g in AGFD['gq_gen']}; gn = {k: v[0] for k, v in AGFD['grupos'].items()}
    def casa(n, pt): return n == pt or (n.startswith(pt) and not (n[len(pt):len(pt) + 1].isalnum() and n[len(pt):len(pt) + 1].isascii()))
    refc = [[c for pts, c in gr if any(casa(nz(x[0]).strip(), pt) for pt in pts)] for x in IG]
    H = []
    for r_ in IDX['produtos']:
        idn = [x[0] for x in r_[F['ingredientes']]]; cls = r_[F['classes']]; gq = []
        for g in (IG[k][1] for k in idn):
            if g is not None and g not in gq: gq.append(g)
        codes = sorted({c for k in idn for c in refc[k]}); fo = IDX['formulacoes'][r_[F['formulacao']]]
        modo = IDX['modos'][r_[F['modo']]] if r_[F['modo']] is not None and r_[F['modo']] >= 0 else ''
        comp = list(dict.fromkeys(CL[c][1] for c in cls)); bio = any(CL[c][2] == 1 for c in cls)
        H.append((nz(' '.join([str(r_[F['registro']]), ' '.join(r_[F['marcas']]), ' + '.join(IG[k][0] for k in idn), ' + '.join(GQ[g] for g in gq), ' + '.join(codes),
                              ' + '.join(gn.get(k, k) for k in codes), IDX['titulares'][r_[F['titular']]], ', '.join(dict.fromkeys(CL[c][0] for c in cls)), ' '.join(comp),
                              'biologico' if bio else '', modo, fo[0], fo[1]])), comp))
    return H
HAY = hay_de()
def uh(c, a): al = AL[a]; return nz(CU[c][0] + ' ' + al[0] + ' ' + ' '.join(al[1] or []))
def busca(cs, q, cls=None):
    ws = nz(q).split(); out = set()
    for c in cs:
        for a, ps in U.get(str(c), []):
            for i in ps:
                h, comp = HAY[i]
                if cls and cls not in comp: continue
                if all(w in h or w in uh(c, a) for w in ws): out.add((REG[i], c, a))
    return out
E4 = busca((SJ, TD), 'FERRUGEM asiatica'); s4 = O.get('s4') or []
chk(f'U8 busca "FERRUGEM asiatica" em Soja = {len(E4)} usos (palavras no produto ou na praga-alvo do mesmo uso; sem acento e sem caixa)',
    len(E4) > 10 and ids(s4) == E4, [len(s4), len(E4)])
E5 = busca((MA, TD), 'antracnose', 'Fungicida'); s5 = O.get('s5') or []
chk(f'U9 Mamão + Classe Fungicida + busca "antracnose" = {len(E5)} usos', len(E5) > 0 and ids(s5) == E5, [len(s5), len(E5)])
chk('U10 REPETIÇÃO: a mesma consulta e a volta à cultura dão as mesmas linhas', O.get('rep') and O['rep'][0] == O['rep'][1] == len(E1), O.get('rep'))
alPH = AL[PH]; rPH = O.get('rPH') or {}
chk(f'U11 linha Phakopsora: Praga-alvo = "{", ".join(alPH[1])}" · Nome científico = "{alPH[0]}" · Cultura do uso = Soja (ou "Todas as culturas"); filtro pelos nomes comuns',
    (rPH.get('s') or {}).get('alvo') == ', '.join(alPH[1]) and (rPH.get('s') or {}).get('cien') == alPH[0] and (rPH.get('s') or {}).get('ucul') in ('Soja', 'Todas as culturas')
    and [x['id'] for x in ((rPH.get('m') or {}).get('alvo') or [])] == alPH[1], rPH)
rs = O.get('rSem') or {}
chk('U12 praga-alvo sem nome comum no AGROFIT: Praga-alvo vazia ("—", filtro "(vazio)") e o nome científico na sua coluna',
    bool(rs) and (rs.get('s') or {}).get('alvo') == '' and (rs.get('s') or {}).get('cien') == AL[rs.get('a', 0)][0] and (rs.get('m') or {}).get('alvo') == [] and (rs.get('p') or [{}])[0].get('t') == '—', rs)
rn = O.get('rNada') or {}
chk('U13 alvo não informado no AGROFIT: as duas colunas vazias, a de Praga-alvo diz "não informado"',
    bool(rn) and (rn.get('s') or {}).get('alvo') == '' and (rn.get('s') or {}).get('cien') == '' and (rn.get('p') or [[{}]])[0][0].get('t') == 'não informado', rn)
chk('U14 uso registrado em "Todas as culturas" aparece com Cultura do uso = "Todas as culturas"', O.get('rTD') == 'Todas as culturas', O.get('rTD'))
A_ = O.get('asc') or {}; C_ = O.get('cienDesc') or {}
chk('U15 ORDENAÇÃO da grade pela Praga-alvo (A → Z, sem nome comum no fim) e pelo Nome científico (Z → A)',
    A_.get('n') == len(E1) and A_.get('ok') and A_.get('vaziosNoFim') and A_.get('cheios', 0) > 1000 and C_.get('ok') and C_.get('vaziosNoFim') and C_.get('cheios', 0) > 1000, [A_, C_])
FN = AL[PH][1][0]; EF = {x for x in E1 if FN in (AL[x[2]][1] or [])}; fil = O.get('fil') or []
chk(f'U16 FILTRO da coluna Praga-alvo = "{FN}": {len(EF)} linhas (pertinência do nome, não texto parcial)', len(EF) > 0 and ids(fil) == EF, [len(fil), len(EF)])
EV = {x for x in E1 if not AL[x[2]][1]}; fv = O.get('filVazio') or []
chk(f'U17 FILTRO "(vazio)" na Praga-alvo = os {len(EV)} usos sem nome comum', ids(fv) == EV, [len(fv), len(EV)])
ops = O.get('ops') or []
chk('U18 cada linha de uso abre a ficha do registro com a cultura e o alvo do uso (id = registro@cultura@alvo; dr = agf_op_<id>)',
    len(ops) == 3 and all(len(i.split('@')) == 3 and d == 'agf_op_' + i for i, d in ops), ops)
u19 = O.get('u19') or {}
chk(f'U19 com a lista por uso, os chips contam usos (Soja): Fungicida = a lista com o chip, "Todas" = a lista sem chip ({len(E1)}), orgânicos = a lista com "Aprovados para orgânicos"',
    0 < u19.get('cntF', 0) == u19.get('nF') < u19.get('semCls', 0) == u19.get('nAll') == len(E1) and 0 < u19.get('orgN', 0) == u19.get('nOrg'), u19)
u20 = O.get('u20') or {}; print('    u20:', u20)
chk('U20 A5 · com o filtro da coluna Praga-alvo = "' + FN + '" (Soja), os chips contam as linhas filtradas: Todas = a lista sem chip, Fungicida = a lista com o chip, orgânicos = a lista com os dois; sem filtro de coluna valem as contagens de sempre; o mesmo na lista por produto',
    u20.get('fn') is True and (u20.get('todas') or [0, 1])[0] == u20['todas'][1] > 0 and (u20.get('fung') or [0, 1])[0] == u20['fung'][1] > 0
    and (u20.get('org') or [0, 1])[0] == u20['org'][1] and (u20.get('fungOrg') or [0, 1])[0] == u20['fungOrg'][1] and u20.get('semFiltro') is True
    and len(u20.get('org2') or []) == 7 and u20['org2'][1] == u20['org2'][2] > 0 and u20['org2'][3] == u20['org2'][4] > u20['org2'][1] and u20['org2'][5] == u20['org2'][6]
    and len(u20.get('prod') or []) == 7 and u20['prod'][1] == u20['prod'][2] > 0 and u20['prod'][3] == u20['prod'][4] > 0 and u20['prod'][5] == u20['prod'][6], u20)
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
