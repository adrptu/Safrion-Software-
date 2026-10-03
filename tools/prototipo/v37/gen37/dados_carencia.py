# -*- coding: utf-8 -*-
"""Carência e destino (MAPA-CARENCIA-LMR-20261003): regras, LMR Brasil e motor puro em JS, usados pelo Mapa (IN-04), pela O.S. e pela
qualidade dos lotes (CO-06). Pedido do proprietário: "no mapa dinâmico ver a carência das aplicações de defensivos para poder colher e
vender/exportar, como o mamão, super exigente em LMR".

Regras (PRD v3.9 §33.8, RN-016, CO-02, CO-06, CO-07, RAST-05) que o motor cumpre
- Carência (intervalo de segurança da bula) e reentrada são controles do campo; LMR é limite de resíduo do MERCADO. LMR vale também no
  Brasil (ANVISA). Não existe "LMR exportação" genérico: a regra é por mercado de destino.
- Só conta aplicação EFETIVA: apontamento com data e área de uma O.S. com produto e cultura. O.S. planejada (A liberar/Liberadas sem
  apontamento) ou cancelada nunca gera carência; aparece como previsão separada. Aplicação anterior pode vencer depois da mais recente
  (vale o maior prazo). Aplicação parcial restringe só a parcela apontada; sem a parcela no apontamento, o prazo vale para o talhão todo.
- Carência cumprida não é "conforme". Regra ausente, carência não conferida na bula, destino indefinido, regra do destino não carregada,
  apontamento aguardando sinal, O.S. de defensivo em execução sem apontamento completo ou histórico fora do sistema: nunca viram verde.
- Mamão colhe em sequência: lote = parcela + data de colheita (apontamento da O.S. de colheita). Aplicação de campo POSTERIOR à colheita
  não contamina o lote já colhido; tratamento pós-colheita liga-se ao lote. Mistura e divisão conservam a genealogia e as restrições
  (sem "diluição"). Trocar o destino reavalia e preserva a avaliação anterior.
- Comandos que autorizam colheita (liberar/iniciar O.S. de colheita) são impedidos com motivo e dono enquanto a carência corre; registrar
  uma colheita que já aconteceu nunca é impedido: vai para conferência (RN-018/CONC-07). A cor do mapa não é o controle.

Fontes e limites
- Carência por produto × cultura: agrofit_dados.py (base DEMONSTRATIVA; usa só usos com conferido=True; os demais ficam "pendente:
  conferir bula"). O uso (alvo) não é registrado na O.S.: vale a maior carência registrada do produto para a cultura.
- LMR Brasil: ANVISA, dados abertos TA_MONOGRAFIA_AGROTOXICO.csv (extraído em 02/10/2026; DT_ATUALIZACAO 02/10/2026), recorte dos
  ingredientes da base × culturas da fazenda em dados_carencia_lmr.json (gerado por `python3 dados_carencia.py --extrair <csv>`).
- Regras de destino de exportação NÃO carregadas: "regra do destino não carregada: pendente". O destino "Mercado sintético de
  demonstração" usa valores SINTÉTICOS (rotulados) só para mostrar a avaliação com laudo; não é regra de país algum.
- Lotes de campo derivam dos apontamentos das O.S. de colheita do cenário; pós-colheita, mistura, divisão, laudos e destinos iniciais
  abaixo (CAR0) são registros DEMONSTRATIVOS.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LMR_JSON = os.path.join(HERE, 'dados_carencia_lmr.json')
HOJE = '2026-09-23'          # mesma data do Mapa (inicio.HOJE): o protótipo vive em 23/09/2026
CULTURAS = ('Mamão', 'Soja', 'Milho', 'Feijão', 'Café')
_ALIAS = {'glufosinato de amônio': 'glufosinato', 'oxicloreto de cobre': 'compostos à base de cobre', 'diquate': 'diquate'}


def _ingr(s):
    """ingredientes normalizados para a monografia: sem sal/forma entre parênteses; mistura separada por ' + '."""
    out = []
    for p in str(s or '').split(' + '):
        p = re.sub(r'\s*\([^)]*\)', '', p).strip().lower()
        if p: out.append(_ALIAS.get(p, p))
    return out


def _cult(c):
    c = str(c or '').strip()
    for k in CULTURAS:
        if c.startswith(k): return k
    return c


# ------------------------------------------------------------------ LMR Brasil (ANVISA)
def extrair_lmr(csv_path, out=LMR_JSON):
    """Recorte da monografia ANVISA: ingredientes da base Agrofit × culturas da fazenda, vigentes em 2026 (ou sem fim)."""
    import csv, io
    import agrofit_dados as A
    raw = open(csv_path, 'rb').read()
    try: txt = raw.decode('utf-8')
    except UnicodeDecodeError: txt = raw.decode('cp1252')
    rows = list(csv.reader(io.StringIO(txt), delimiter=';')); H = rows[0]; ix = {h: i for i, h in enumerate(H)}
    ings = set(i for p in A.PRODUTOS for i in _ingr(p['ingrediente'])) | {'tiabendazol', 'imazalil'}   # + pós-colheita do mamão
    md = lambda s: (lambda m: f'{m.group(3)}-{m.group(1)}-{m.group(2)}' if m else '')(re.match(r'(\d{2})/(\d{2})/(\d{4})', s or ''))
    out_d = {}; atual = ''
    for x in rows[1:]:
        if len(x) < len(H): continue
        sub = x[ix['NO_SUBSTANCIA']].strip().lower(); cul = x[ix['NO_CULTURA']].strip()
        if sub not in ings or cul not in CULTURAS: continue
        ini, fim = md(x[ix['DT_INICIO_VIGENCIA']]), md(x[ix['DT_FIM_VIGENCIA']]); atual = max(atual, md(x[ix['DT_ATUALIZACAO']]))
        if fim and fim < '2026-01-01': continue
        out_d.setdefault(sub, {}).setdefault(cul, []).append(dict(
            v=float(x[ix['NU_LMR']]), un=x[ix['NO_UNIDADE_MEDIDA']].strip().replace('MILIGRAMA/KILOGRAMA', 'mg/kg'),
            tipo=x[ix['TIPO_LIMITE']].strip(), aut=x[ix['ST_AUTORIZADO']].strip(), mono=x[ix['CO_MONOGRAFIA']].strip(),
            ato=re.sub(r'\s+', ' ', x[ix['DS_ATO_LEGAL']].replace('\x1a', '-')).strip(), ini=ini, fim=fim))
    for s in out_d.values():
        for c in s.values(): c.sort(key=lambda r: r['ini'])
    doc = dict(fonte='ANVISA · dados abertos · monografias de agrotóxicos (TA_MONOGRAFIA_AGROTOXICO.csv)',
               link='https://www.gov.br/anvisa/pt-br/acessoainformacao/dadosabertos/informacoes-analiticas/monografias-de-agrotoxicos',
               extraido='2026-10-02', atualizacao=atual, recorte='ingredientes da base Agrofit demonstrativa × Mamão, Soja, Milho, Feijão e Café; '
               'linhas vigentes em 2026 ou sem fim de vigência', lmr=out_d)
    json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    return doc


def _lmr():
    return json.load(open(LMR_JSON, encoding='utf-8'))


# ------------------------------------------------------------------ carência por produto × cultura (Agrofit demonstrativo)
def _usos(p):
    """{cultura: dias (maior carência numérica conferida), conf, na (não se aplica), txt, alvos}."""
    import agrofit_dados as A
    out = {}
    por = {}
    for u in p['usos']: por.setdefault(_cult(u['cultura']), []).append(u)
    for c, us in por.items():
        num = [(int(m.group(1)), u) for u in us for m in [re.match(r'^(\d+) dias?$', str(u['carencia']))] if m]
        conf = [x for x in num if x[1]['conferido']]
        sem = [u for u in us if str(u['carencia']).startswith('sem restri') and u['conferido']]
        na = [u for u in us if u['carencia'] in (A._PRE, A._TS)]
        alvos = ', '.join(u['alvo'] for u in us)
        if conf:
            d = max(x[0] for x in conf); maior = max(x[0] for x in num)
            out[c] = dict(dias=d, conf=True, na=False, alvos=alvos,
                          txt=f'{d} dias (bula conferida)' + (f'; uso não conferido indica {maior} dias' if maior > d else ''))
        elif num:
            d = max(x[0] for x in num)
            out[c] = dict(dias=d, conf=False, na=False, alvos=alvos, txt=f'{d} dias · uso não conferido na bula (prazo provisório)')
        elif sem:
            out[c] = dict(dias=0, conf=True, na=False, alvos=alvos, txt='sem restrições na bula (conferida)')
        elif na:
            out[c] = dict(dias=None, conf=True, na=True, alvos=alvos, txt=na[0]['carencia'])
        else:
            out[c] = dict(dias=None, conf=False, na=False, alvos=alvos, txt=str(us[0]['carencia']))
    return out


def _produtos():
    import agrofit_dados as A, dados2 as D2, dados_lagoa_safra as DL
    out = {}
    for p in A.PRODUTOS:
        adj = p['classe'] == 'Adjuvante'
        for n in dict.fromkeys(p['nomes_fazenda'] + [p['nome']]):   # ordem estável (set variava com o hash do processo e a página mudava a cada build)
            out[n] = dict(ingr=' + '.join(_ingr(p['ingrediente'])), classe=p['classe'], defn=True, adj=adj, ficha=p['id'],
                          usos={} if adj else _usos(p))
    # insumos que não são agrotóxicos (fertilizante, corretivo, semente, muda): fora da carência
    DEF = ('Herbicida', 'Fungicida', 'Inseticida', 'Acaricida', 'Nematicida')
    for pl in D2.PLANOS + DL.PLANOS:
        for a in pl['atividades']:
            for x in a['prods']:
                if x['prod'] in out: continue
                d = any(x['grupo'].startswith(g) for g in DEF)
                out[x['prod']] = dict(ingr='', classe=x['grupo'], defn=d, adj=False, ficha='', usos={})   # defensivo sem ficha → pendente
    # pedidos de compra com grupo declarado (semente, fertilizante…); produto fora de todo cadastro conta como possível defensivo (pendente)
    for x in D2.PEDIDOS:
        if x['item'] not in out:
            out[x['item']] = dict(ingr='', classe=x['grupo'], defn=any(x['grupo'].startswith(g) for g in DEF + ('Herbicidas', 'Fungicidas', 'Inseticidas')),
                                  adj=False, ficha='', usos={})
    return out


def _talhoes():
    import dados as D, dados2 as D2, dados_lagoa_safra as DL
    import datetime as dt
    out = {}
    safra_ini = {s['id']: s['ini'] for s in D2.SAFRAS}
    for t, ha, c, fase, _ in D.TALHOES:
        out[t] = dict(nome=t, ha=ha, cult=_cult(c), faz='Santa Rita', reg=safra_ini['S2627'], continua=(c.startswith('Mamão') and fase == 'produção'),
                      parcs=sorted({c2['local'] for c2 in D2.CULTIVOS['S2627'] if c2['local'].startswith(t + '-')}))
    hoje = dt.date.fromisoformat(HOJE)
    cult = {DL.PID_DE[c['local']]: c for c in DL.CULTIVOS}
    for n, ha in DL.PIVOS.items():
        pid = DL.pid(n); c = cult.get(pid)
        dias = (hoje - dt.date.fromisoformat(c['plantio'])).days if c else -1
        out[pid] = dict(nome=DL.nome(n), ha=ha, cult=_cult(c['cultura']) if c else '', faz=DL.FAZ, reg=DL.SAFRA['ini'],
                        continua=bool(c) and dias >= 240, parcs=[])
    return out


def _nomes(tal):
    """nome do local (O.S. e cultivos) → id do mapa: 'Pivô 6' → PV06; 'T1-A' → T1 (parcela T1-A)."""
    import dados_lagoa_safra as DL
    out = {DL.nome(n): DL.pid(n) for n in DL.PIVOS}
    for t in tal:
        if not t.startswith('PV'): out[t] = t
    return out


# ------------------------------------------------------------------ destinos (regra por mercado)
DESTINOS = {
    'MI-BR': dict(nome='Mercado interno · Brasil', regra='LMR da ANVISA vigente na data da colheita (monografias)', carregada=True, lmr='anvisa',
                  laudo=False, escopo='uso registrado e carência cumprida nas aplicações apontadas até a colheita; LMR ANVISA vigente para cada '
                  'ingrediente aplicado; sem exigência legal de laudo por lote (requisito de comprador fica à parte)'),
    'EXP-ND': dict(nome='Exportação · mercado a definir', indef=True, carregada=False),
    'EXP-UE': dict(nome='Exportação · União Europeia', regra='LMR do mercado de destino (ato oficial vigente)', carregada=False),
    'DEMO-S': dict(nome='Mercado sintético de demonstração', regra='valores SINTÉTICOS de demonstração (não são regra de país algum)', carregada=True,
                   sint=True, laudo=True, lmr={'tiabendazol': dict(v=0.5, un='mg/kg'), 'tebuconazol': dict(v=0.05, un='mg/kg'),
                                               'abamectina': dict(v=0.01, un='mg/kg'), 'glifosato': dict(v=0.05, un='mg/kg'),
                                               'acetamiprido': dict(v=0.01, un='mg/kg'), 'mancozebe': dict(v=0.05, un='mg/kg')},
                   escopo='carência nas aplicações apontadas; limite sintético por ingrediente; laudo do lote obrigatório'),
}
QUEM = dict(ag='Ana (agrônoma)', com='Comercial', qual='Qualidade (Marta)', reg='Qualidade · regulatório')

# registros DEMONSTRATIVOS de lote (Lagoa Grande · mamão): pós-colheita, mistura, divisão, destinos e laudo sintético
CAR0 = dict(
    ops=[dict(k='pos', lote='LC-0510-2', p='Tiabendazol (imersão pós-colheita)', ingr='tiabendazol', d='2026-09-19', reg=False,
              fonte='registro demonstrativo do packing'),
         dict(k='divisao', d='2026-09-22', de=['LC-0505-2'], novos=[dict(id='LC-0505-2A', q='classe A'), dict(id='LC-0505-2B', q='classe B')],
              fonte='classificação no packing (demonstrativo)'),
         dict(k='mistura', d='2026-09-23', de=['LC-0510-2', 'LC-0505-1'], novos=[dict(id='LM-39-01', q='mistura no packing · classe A')],
              fonte='consolidação no packing (demonstrativo)')],
    dest={'LC-0510-1': 'MI-BR', 'LC-0510-2': 'DEMO-S', 'LM-39-01': 'EXP-UE', 'LC-0505-2A': 'EXP-ND'},
    laudos=[dict(id='LAB-3301', escopo=['LC-0510-2'], d='2026-09-20', amostra='AM-3330 · 12 frutos · composta', sint=True,
                 lab='laboratório (valores sintéticos)', res={'tiabendazol': dict(v=0.8, un='mg/kg', lq=0.01)})],
    comp={'LM-39-01': dict(t='Laudo multirresíduo do lote exigido pelo comprador (requisito comercial, não legal)', ex='laudo')},
)


def card():
    import dados as D
    tal = _talhoes(); L = _lmr()
    prod = _produtos()
    maxcar = {}
    for p in prod.values():
        for c, u in p['usos'].items():
            if isinstance(u.get('dias'), int): maxcar[c] = max(maxcar.get(c, 0), u['dias'])
    jan = {o['id']: o['janela'] for o in D.ORDENS + D.ORDENS_LG}
    return dict(hoje=HOJE, tal=tal, nomes=_nomes(tal), prod=prod, maxcar=maxcar, jan=jan, dest=DESTINOS, quem=QUEM, car0=CAR0,
                lmr=L['lmr'], lmrf=dict(fonte=L['fonte'], link=L['link'], extraido=L['extraido'], atualizacao=L['atualizacao'], recorte=L['recorte']),
                fonte_car='bula de referência (Agrofit demonstrativo: usos conferidos em bula pública do ingrediente; não substitui a bula do produto comercial)')


# ------------------------------------------------------------------ motor (JS puro: O.S., Mapa, CO-06 e testes no jsc)
JS = r'''
// ===== Carência e destino (MAPA-CARENCIA-LMR-20261003) · motor puro sobre o cenário compartilhado (cenGet) =====
// Só aplicação EFETIVA (apontamento com data e área) conta; O.S. planejada/cancelada nunca. Carência ≠ LMR; LMR é por mercado (Brasil = ANVISA).
// Regra ausente, destino indefinido ou prova insuficiente nunca viram "conforme". Ver dados_carencia.py.
function carIso(s,ref){ s=String(s||'').trim(); let m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s); if(m) return m[0];
  m=/^(\d{1,2})\/(\d{1,2})(?:\/(\d{4}))?/.exec(s); if(!m) return '';
  return (m[3]||String(ref||CARD.hoje).slice(0,4))+'-'+('0'+m[2]).slice(-2)+'-'+('0'+m[1]).slice(-2); }
function carAdd(iso,n){ const d=new Date(iso+'T12:00:00Z'); d.setUTCDate(d.getUTCDate()+n); return d.toISOString().slice(0,10); }
function carBr(iso){ if(!iso) return '—'; const a=String(iso).split('-'); return a[2]+'/'+a[1]; }
function carNum(n,d){ return Number(n||0).toLocaleString('pt-BR',{maximumFractionDigits:(d===undefined?1:d)}); }
function carNome(t){ return (CARD.tal[t]||{}).nome||t; }
// local da O.S. → talhões do mapa ('Pivô 6' → PV06 · 'T1-A' → T1, parcela T1-A · 'T1+T2' → T1 e T2)
function carTals(nome){ const s=String(nome||''); const out=[]; const add=(tid,parc)=>{ if(CARD.tal[tid]&&!out.some(x=>x.tid===tid&&x.parc===parc)) out.push({tid,parc}); };
  if(CARD.nomes[s]){ const t=CARD.nomes[s]; add(t,t===s?null:(s.indexOf(t+'-')===0?s:null)); return out; }
  (s.match(/Pivô\s*\d+/g)||[]).forEach(x=>{ const n=Number(x.replace(/\D/g,'')); add('PV'+('0'+n).slice(-2),null); });
  (s.match(/\b(T|P|C)\d+(-[A-Z])?\b/g)||[]).forEach(x=>{ const m=/^((?:T|P|C)\d+)(-[A-Z])?$/.exec(x); add(m[1],m[2]?x:null); });
  return out; }
function carRegra(p,cult){ const P=CARD.prod[p]; if(!P) return {def:false,desconhecido:true};
  if(!P.defn) return {def:false}; if(P.adj) return {def:true,adj:true};
  const u=(P.usos||{})[cult]; if(!u) return {def:true,semUso:true,ingr:P.ingr,ficha:P.ficha};
  return Object.assign({def:true,ingr:P.ingr,ficha:P.ficha},u); }
// carência conferida na bula pelo agrônomo (carc_bula) vale sobre o valor demonstrativo, ausente ou provisório do produto × cultura
function carBulaRec(cen,p,cult){ const b=(((cen&&cen.car)||{}).bula||{})[p+'|'+cult]; return (b&&b.length)?b[b.length-1]:null; }
function carRegraC(cen,p,cult){ const r=carRegra(p,cult); const b=carBulaRec(cen,p,cult); if(!b||r.adj||(r.def===false&&!r.desconhecido)) return r;
  return Object.assign({},r,{def:true,desconhecido:false,semUso:false,na:false,dias:b.dias,conf:true,txt:b.dias+' dias (bula conferida por '+b.por+')'}); }
// lote de campo = O.S. de colheita + dia do apontamento (OS-0505 → LC-0505-1; outro prefixo entra no id, sem colisão)
function carLid(oid,dia){ const s=String(oid||''); const m=/^OS-(\d+)$/.exec(s); return 'LC-'+(m?m[1]:s.replace(/[^A-Za-z0-9]/g,''))+'-'+dia; }
// fim = 1º dia em que a colheita pode começar; o texto "até" mostra o último dia ainda em carência
function carAte(fim){ return fim?carBr(carAdd(fim,-1)):'—'; }
function carEhColheita(o){ return /^Colheita/.test(String((o&&o.tipo)||'')); }
function carJanela(o){ const j=String((o.osc&&o.osc.janela)||(o.osc&&o.osc.novo&&o.osc.novo.janela)||o.janela||CARD.jan[o.id]||'');
  if(/^hoje/.test(j)) return {txt:j,ini:CARD.hoje,fim:CARD.hoje};
  const m=/(\d{1,2})(?:\s*[–-]\s*(\d{1,2}))?\/(\d{1,2})(?:\/(\d{4}))?/.exec(j); if(!m) return {txt:j||'a definir',ini:'',fim:''};
  const y=m[4]||CARD.hoje.slice(0,4), mm=('0'+m[3]).slice(-2); const ini=y+'-'+mm+'-'+('0'+m[1]).slice(-2);
  return {txt:j,ini,fim:m[2]?y+'-'+mm+'-'+('0'+m[2]).slice(-2):ini}; }
function carPush(arr,x){ if(!arr.some(y=>y.t===x.t)) arr.push(x); return arr; }
// aplicações efetivas de defensivo no talhão + pendências + previsões (planejado, não conta). corte = data da colheita do lote: aplicação
// posterior não conta para aquele lote. Sem corte (situação do talhão), toda aplicação apontada conta, mesmo com data depois da consultada.
function carAplic(cen,tid,ate,corte){ const T=CARD.tal[tid]||{}; const cult=T.cult||''; const apl=[], pend=[], prev=[]; ate=ate||CARD.hoje;
  Object.keys((cen&&cen.ordens)||{}).forEach(id=>{ const o=cen.ordens[id]; const ts=carTals(o.talhao).filter(x=>x.tid===tid); if(!ts.length) return;
    const reais=(o.ap||[]).filter(a=>a.st!=='Previsto'); const canc=o.etapa==='Canceladas';
    if(canc&&!reais.length) return;   // cancelada sem apontamento nunca conta; com apontamento, a aplicação aconteceu (fato) e conta
    const defs=(o.ins||[]).filter(x=>{ const r=carRegraC(cen,x.p,cult); return r.def||r.desconhecido; }); if(!defs.length) return;   // fora de todo cadastro: possível defensivo
    const parcO=ts[0].parc; const J=carJanela(o);
    if(canc) carPush(pend,{k:'canc',os:id,t:id+' cancelada com apontamento: a aplicação conta · conferir',q:o.resp||CARD.quem.ag});
    reais.forEach(a=>{ const d=carIso(a.d);
      if(!d){ carPush(pend,{k:'data',os:id,t:id+': apontamento sem data · conferir a aplicação',q:o.resp||CARD.quem.ag}); return; }
      if(corte&&d>corte) return;   // aplicação depois da colheita do lote não contamina o lote já colhido
      const ps=(a.cons&&Object.keys(a.cons).length)?defs.filter(x=>(Number(a.cons[x.p])||0)>0):defs;
      ps.forEach(x=>{ const r=carRegraC(cen,x.p,cult); if(r.adj) return;
        const it={os:id,dia:a.dia,d,p:x.p,ingr:r.ingr||'',ha:Number(a.ha)||0,parc:a.parc||parcO||null,sinc:a.sinc!==false,st:a.st,resp:o.resp||'',
                  dias:(typeof r.dias==='number')?r.dias:null,na:!!r.na,conf:!!r.conf,txt:r.txt||'',fim:null,ficha:r.ficha||''};
        it.faixa=!it.parc&&T.ha&&it.ha<T.ha-0.01;
        if(r.desconhecido) carPush(pend,{k:'regra',os:id,p:x.p,cult,t:x.p+': produto sem cadastro · conferir classe e carência na bula',q:CARD.quem.ag});
        else if(r.semUso) carPush(pend,{k:'regra',os:id,p:x.p,cult,t:x.p+': uso em '+cult.toLowerCase()+' não achado na bula · conferir',q:CARD.quem.ag});
        else if(r.na) it.fim=d;
        else if(it.dias===null) carPush(pend,{k:'regra',os:id,p:x.p,cult,t:x.p+': carência sem prazo em dias · conferir bula',q:CARD.quem.ag});
        else { it.fim=carAdd(d,it.dias); if(!r.conf) carPush(pend,{k:'bula',os:id,p:x.p,cult,t:x.p+': '+it.dias+' dias não conferidos na bula (provisório)',q:CARD.quem.ag}); }
        if(!it.sinc) carPush(pend,{k:'sinc',os:id,t:id+' dia '+a.dia+' ('+carBr(d)+') no aparelho, aguardando sinal: já conta',q:o.resp||''});
        apl.push(it); }); });
    if(canc) return;
    // execução sem apontamento completo: a aplicação pode ter ocorrido sem registro → pendente (nunca libera); planejada → só previsão
    const saldo=Number(o.saldo||0);
    if(o.etapa==='Em execução'&&saldo>0.001) carPush(pend,{k:'exec',os:id,t:id+' em execução, '+carNum(saldo)+' ha de saldo: pode haver aplicação não apontada',q:o.resp||CARD.quem.ag});
    else if(o.etapa==='Liberadas'&&J.ini&&J.ini<=ate&&!reais.length) carPush(pend,{k:'exec',os:id,t:id+' liberada, janela desde '+carBr(J.ini)+', sem apontamento: confirmar aplicação',q:o.resp||CARD.quem.ag});
    else if((o.etapa==='A liberar'||o.etapa==='Liberadas')&&!reais.length){ let fp=null; defs.forEach(x=>{ const r=carRegraC(cen,x.p,cult); if(typeof r.dias==='number'&&J.ini){ const f=carAdd(J.ini,r.dias); if(!fp||f>fp) fp=f; } });
      prev.push({os:id,etapa:o.etapa,jan:J.txt,ini:J.ini,ps:defs.map(x=>x.p),fimPrev:fp}); } });
  return {apl,pend,prev,cult}; }
function carOrdFim(a,b){ return (a.fim||'')<(b.fim||'')?1:((a.fim||'')>(b.fim||'')?-1:(a.d<b.d?1:-1)); }
// situação da carência no talhão (ou parcela) na data consultada: curso · insuf · cumprida · sem
function carEstado(cen,tid,ate,parc,corte){ ate=ate||CARD.hoje; const A=carAplic(cen,tid,ate,corte);
  const apl=A.apl.filter(r=>!parc||!r.parc||r.parc===parc); const ativos=apl.filter(r=>r.fim&&r.fim>ate).sort(carOrdFim);
  const det=ativos[0]||apl.filter(r=>r.fim).sort(carOrdFim)[0]||null;
  const k=ativos.length?'curso':(A.pend.length?'insuf':(apl.length?'cumprida':'sem'));
  const pa=[]; ativos.forEach(r=>{ if(r.parc&&pa.indexOf(r.parc)<0) pa.push(r.parc); });
  const parcial=ativos.length>0&&ativos.every(r=>r.parc)&&((CARD.tal[tid]||{}).parcs||[]).some(p=>pa.indexOf(p)<0);
  return {k,ate,tid,cult:A.cult,apl,ativos,det,pend:A.pend,prev:A.prev,parcs:pa,parcial}; }
function carRot(e){ if(e.k==='curso') return 'carência até '+carAte(e.det.fim)+(e.parcial?' em '+e.parcs.join(', '):'')+(e.pend.length?' · dados pendentes':'');
  if(e.k==='insuf') return 'dados insuficientes · conferir'; if(e.k==='cumprida') return 'prazo cumprido em '+carBr(e.det&&e.det.fim)+' · destino a avaliar';
  return 'sem aplicação apontada'; }
// ---- lotes: campo (parcela + data de colheita), pós-colheita, mistura e divisão com genealogia ----
function carOps(cen){ return ((CARD.car0||{}).ops||[]).concat(((cen&&cen.car)||{}).ops||[]); }
function carLotes(cen){ const L={};
  Object.keys((cen&&cen.ordens)||{}).forEach(id=>{ const o=cen.ordens[id]; if(!carEhColheita(o)) return; const ts=carTals(o.talhao); if(!ts.length) return;
    (o.ap||[]).forEach(a=>{ if(a.st==='Previsto') return; const lid=carLid(id,a.dia);
      L[lid]={id:lid,tipo:'campo',os:id,tal:ts[0].tid,parc:a.parc||ts[0].parc||null,d:carIso(a.d),ha:Number(a.ha)||0,st:a.st,sinc:a.sinc!==false,pais:[],pos:[],q:'colheita '+id+' dia '+a.dia}; }); });
  carOps(cen).forEach(op=>{ if(op.k==='mistura'||op.k==='divisao') (op.novos||[]).forEach(n=>{ L[n.id]={id:n.id,tipo:op.k,pais:(op.de||[]).slice(),d:op.d,pos:[],q:n.q||'',fonte:op.fonte||''}; });
    if(op.k==='pos'&&L[op.lote]) L[op.lote].pos.push(op); });
  return L; }
function carAncestrais(L,lid,seen){ seen=seen||{}; if(seen[lid]) return []; seen[lid]=1; const l=L[lid]; if(!l) return []; let out=[l]; (l.pais||[]).forEach(p=>{ out=out.concat(carAncestrais(L,p,seen)); }); return out; }
function carDestino(cen,lid){ const d=(((cen&&cen.car)||{}).dest||{}); return (d[lid]!==undefined)?d[lid]:(((CARD.car0||{}).dest||{})[lid]||''); }
function carLaudos(cen,L,lid){ const l=L[lid]; const ok=[lid]; if(l&&l.tipo==='divisao') (l.pais||[]).forEach(p=>ok.push(p));   // divisão: a amostra do lote de origem representa as partes; mistura precisa da própria amostra
  return ((CARD.car0||{}).laudos||[]).concat(((cen&&cen.car)||{}).laudos||[]).filter(x=>(x.escopo||[]).some(e=>ok.indexOf(e)>=0)); }
function carLaudosAnc(cen,anc){ const ids=anc.map(x=>x.id); return ((CARD.car0||{}).laudos||[]).concat(((cen&&cen.car)||{}).laudos||[]).filter(x=>(x.escopo||[]).some(e=>ids.indexOf(e)>=0)); }
function carLib(cen,lid){ const h=(((cen&&cen.car)||{}).lib||{})[lid]; return (h&&h.length)?h[h.length-1]:null; }
function carLimite(D,ingr,cult,data){ if(D.lmr==='anvisa'){ const rs=((CARD.lmr[ingr]||{})[cult]||[]).filter(r=>(!r.ini||r.ini<=data)&&(!r.fim||r.fim>=data)&&(!r.aut||r.aut==='SIM'));
    const r=rs[rs.length-1]; return r?Object.assign({fonte:'ANVISA · monografia '+(r.mono||'—')+' · '+r.ato},r):null; }
  const r=(D.lmr||{})[ingr]; return r?Object.assign({tipo:'Limite máximo',fonte:'valor sintético de demonstração'},r):null; }
// avaliação do lote para o destino: nao_avaliado · pendente · conforme (no escopo) · nao_conforme; faltas com quem resolve
function carAvaliar(cen,lid,destId){ const L=carLotes(cen); const l=L[lid]; const Q=CARD.quem;
  const R={lote:lid,st:'nao_avaliado',rot:'',faltas:[],motivos:[],ings:[],apl:[],orig:[],pos:[],escopo:'',regra:'',dest:'',sint:false};
  if(!l){ R.rot='Lote não encontrado'; R.faltas.push({t:'Lote '+lid+' não encontrado nos registros de colheita',q:Q.qual}); return R; }
  const dest=(destId===undefined)?carDestino(cen,lid):destId; const D=dest?CARD.dest[dest]:null; R.dest=dest;
  const anc=carAncestrais(L,lid); const folhas=anc.filter(x=>x.tipo==='campo'); R.orig=folhas; const ings={}; let cult='';
  if(!folhas.length) carPush(R.faltas,{t:'Origem do lote não identificada (parcela e data de colheita)',q:Q.qual});
  folhas.forEach(f=>{ const T=CARD.tal[f.tal]; if(!T){ carPush(R.faltas,{t:'Parcela de origem de '+f.id+' sem cadastro',q:Q.qual}); return; } cult=cult||T.cult;
    if(!f.sinc) carPush(R.faltas,{t:'Colheita '+f.id+' ainda no aparelho (aguardando sinal)',q:'equipe de colheita'});
    const lb=carAdd(f.d,-(CARD.maxcar[T.cult]||30)); if(T.reg&&lb<T.reg) carPush(R.faltas,{t:'Aplicações em '+T.nome+' antes de '+carBr(T.reg)+' não estão no sistema e a colheita de '+carBr(f.d)+' precisa de '+(CARD.maxcar[T.cult]||30)+' dias de histórico: conferir o caderno de campo',q:Q.ag});
    const A=carAplic(cen,f.tal,f.d,f.d);
    A.apl.filter(r=>!f.parc||!r.parc||r.parc===f.parc).forEach(r=>{ R.apl.push(Object.assign({lote:f.id},r));
      r.ingr.split(' + ').filter(Boolean).forEach(i=>{ (ings[i]=ings[i]||{ingr:i,de:[]}).de.push(r.p+' · '+r.os+' · '+carBr(r.d)); });
      if(r.fim&&r.fim>f.d) carPush(R.motivos,{t:'Colhido em '+carBr(f.d)+' ('+f.id+', '+T.nome+') dentro da carência de '+r.p+': aplicado em '+carBr(r.d)+' ('+r.os+'), carência até '+carAte(r.fim)+(r.conf?'':' (provisório)'),q:Q.ag+' registra a decisão sobre o lote'});
      if(r.st==='Provisório') carPush(R.faltas,{t:r.os+' dia '+r.dia+' ('+carBr(r.d)+'): apontamento provisório da aplicação · conferir',q:r.resp||Q.ag}); });
    A.pend.forEach(p=>carPush(R.faltas,{t:p.t,q:p.q||Q.ag})); });
  anc.forEach(x=>(x.pos||[]).forEach(t=>{ R.pos.push(Object.assign({lote:x.id},t)); String(t.ingr||'').split(' + ').filter(Boolean).forEach(i=>{ (ings[i]=ings[i]||{ingr:i,de:[]}).de.push('pós-colheita '+t.p+' · '+x.id+' · '+carBr(t.d)); });
    if(!t.reg) carPush(R.faltas,{t:'Tratamento pós-colheita '+t.p+' ('+x.id+'): uso pós-colheita não conferido no registro do produto',q:Q.ag}); }));
  const comp=(((cen&&cen.car)||{}).comp||{})[lid]||((CARD.car0||{}).comp||{})[lid];
  // laudos do lote e de toda a origem: resultado acima do limite numa origem não se dilui na mistura nem some na divisão; resíduo detectado
  // de ingrediente sem aplicação apontada também entra na avaliação (e vira pendência de origem)
  const lauA=carLaudosAnc(cen,anc); const ancIds=anc.map(x=>x.id);
  lauA.forEach(x=>Object.keys(x.res||{}).forEach(i=>{ const r=x.res[i]; if(!r||r.nd||!(Number(r.v)>0)||ings[i]) return;
    ings[i]={ingr:i,de:['detectado no laudo '+x.id+' sem aplicação apontada']}; carPush(R.faltas,{t:'Resíduo de '+i+' no laudo '+x.id+' sem aplicação apontada: conferir a origem',q:Q.ag}); }));
  // destino: a regra é do mercado; sem destino, indefinido ou sem regra carregada → pendente
  if(!dest) carPush(R.faltas,{t:'Destino do lote não definido',q:Q.com});
  else if(!D) carPush(R.faltas,{t:'Destino '+dest+' sem cadastro',q:Q.com});
  else if(D.indef) carPush(R.faltas,{t:'Mercado de destino não identificado: a regra depende do país e do comprador',q:Q.com});
  else if(!D.carregada) carPush(R.faltas,{t:'Regra do destino não carregada ('+D.nome+'): pendente',q:Q.reg});
  else { R.regra=D.regra; R.sint=!!D.sint; const data=folhas.reduce((m,f)=>f.d>m?f.d:m,'')||CARD.hoje; const lau=carLaudos(cen,L,lid);
    if(D.laudo&&!lau.length) carPush(R.faltas,{t:'Laudo de resíduos do lote exigido pelo destino: coletar e analisar amostra',q:Q.qual});
    Object.values(ings).forEach(g=>{ const lim=carLimite(D,g.ingr,cult,data); const row={ingr:g.ingr,de:g.de.join(' · '),lim:'',res:'',st:''};
      if(!lim){ row.st='sem limite'; carPush(R.faltas,{t:'Sem limite vigente de '+g.ingr+' para '+(cult||'a cultura').toLowerCase()+' em '+D.nome+': conferir regra',q:Q.reg}); }
      else if(lim.tipo==='Não estabelecido'){ row.lim='não estabelecido (dispensado) · '+lim.fonte; row.st='ok'; }
      else { row.lim=carNum(lim.v,3)+' '+lim.un+' · '+lim.fonte; row.st='ok';
        lauA.forEach(x=>{ const r=(x.res||{})[g.ingr]; if(!r||r.nd||row.st==='acima') return;   // contraprova: vale em qualquer destino
          if(r.un!==lim.un){ row.st='unidade'; carPush(R.faltas,{t:'Laudo '+x.id+': unidade de '+g.ingr+' ('+r.un+') incompatível com o limite ('+lim.un+')',q:Q.qual}); return; }
          if(r.v>lim.v){ const her=(x.escopo||[]).filter(e=>e!==lid&&ancIds.indexOf(e)>=0); row.st='acima'; row.res=carNum(r.v,3)+' '+r.un+' · '+x.id+(x.sint?' (sintético)':'')+(her.length?' · origem '+her.join(', '):'');
            carPush(R.motivos,{t:g.ingr+' '+carNum(r.v,3)+' '+r.un+' acima do limite '+carNum(lim.v,3)+' '+lim.un+' ('+lim.fonte+') · laudo '+x.id+(her.length?' do lote de origem '+her.join(', ')+': mistura ou divisão não dilui':''),q:Q.qual+' decide a destinação compatível'}); } });
        if(row.st==='ok'&&lau.length){ const x=lau[lau.length-1]; const r=(x.res||{})[g.ingr];
          if(!D.laudo){ if(r&&r.un===lim.un) row.res=(r.nd?'não detectado (< LQ '+carNum(r.lq,3)+' '+r.un+')':carNum(r.v,3)+' '+r.un)+' · '+x.id+(x.sint?' (sintético)':''); }
          else if(!r){ row.st='sem resultado'; carPush(R.faltas,{t:'Laudo '+x.id+' não inclui '+g.ingr+' no escopo analítico',q:Q.qual}); }
          else if(r.un!==lim.un){ row.st='unidade'; carPush(R.faltas,{t:'Laudo '+x.id+': unidade de '+g.ingr+' ('+r.un+') incompatível com o limite ('+lim.un+')',q:Q.qual}); }
          else if(r.nd){ row.res='não detectado (< LQ '+carNum(r.lq,3)+' '+r.un+') · '+x.id; if(r.lq>lim.v){ row.st='inconclusivo'; carPush(R.faltas,{t:'Laudo '+x.id+': LQ de '+g.ingr+' acima do limite, resultado inconclusivo',q:Q.qual}); } }
          else row.res=carNum(r.v,3)+' '+r.un+' · '+x.id+(x.sint?' (sintético)':''); } }
      R.ings.push(row); });
    if(comp&&!(comp.ex==='laudo'&&carLaudos(cen,L,lid).length)) carPush(R.faltas,{t:comp.t,q:Q.com}); }
  if(dest&&D&&!D.carregada&&comp) carPush(R.faltas,{t:comp.t,q:Q.com});
  R.st=R.motivos.length?'nao_conforme':(!dest?'nao_avaliado':(R.faltas.length?'pendente':'conforme'));
  const nm=D?D.nome:(dest||'sem destino');
  R.rot={nao_avaliado:'Não avaliado · sem destino',pendente:'Pendente · '+nm,conforme:'Conforme no escopo · '+nm,nao_conforme:'Não conforme'+(dest?' · '+nm:'')}[R.st];
  R.escopo=D&&D.escopo?D.escopo:''; R.cor={nao_avaliado:'gray',pendente:'yellow',conforme:'green',nao_conforme:'red'}[R.st];
  R.acao={nao_avaliado:'Definir destino',pendente:'Ver pendência',conforme:'Ver avaliação',nao_conforme:'Ver avaliação'}[R.st];
  // liberação comercial registrada (carc_liberar_lote): só vale para o mesmo destino enquanto a avaliação continua conforme
  const lb=carLib(cen,lid); R.lib=lb?Object.assign({valida:lb.dest===dest&&R.st==='conforme'},lb):null;
  if(R.lib&&!R.lib.valida) R.libSusp={t:'Liberação para '+((CARD.dest[lb.dest]||{}).nome||lb.dest)+(lb.at?' (registrada às '+lb.at+')':'')+' suspensa: agora '+R.rot,q:Q.com+' suspende reserva e expedição do lote'};
  return R; }
// ---- O.S.: colheita impedida enquanto a carência corre (comando, não cor) e aviso preventivo ao liberar aplicação ----
function carBloqColheita(c,o,fn){ if(!o||!carEhColheita(o)) return null; const ts=carTals(o.talhao); if(!ts.length) return null;
  const J=carJanela(o); const ini=(J.ini&&J.ini>CARD.hoje)?J.ini:CARD.hoje; const V=fn==='iniciar'?'Iniciar':'Liberar';
  for(const x of ts){ const e=carEstado(c,x.tid,ini,x.parc); const nm=carNome(x.tid)+(x.parc?' ('+x.parc+')':'');   // sem corte: aplicação apontada antes da colheita sempre conta
    if(e.k==='curso'){ const r=e.ativos[0];
      return {acao:fn,car:true,fim:r.fim,tid:x.tid,p:r.p,os:r.os,t:V+' bloqueado: carência em curso em '+nm+' até '+carAte(r.fim)+' · '+r.p+' ('+r.os+', aplicado em '+carBr(r.d)+', '+r.dias+' dias'+(r.conf?'':', prazo provisório')+'). A colheita começaria em '+carBr(ini)+'.',
        q:CARD.quem.ag+' reprograma a colheita para '+carBr(r.fim)+' ou depois. Colheita que já aconteceu é registrada normalmente e vai para conferência.',h:'IN-04.dc.html#car:'+x.tid,hl:'Ver restrição no mapa'}; }
    const pr=e.pend.filter(p=>p.k==='regra'||p.k==='bula'||p.k==='exec'||p.k==='data');
    if(pr.length){ const p=pr[0]; const bu=(p.k==='regra'||p.k==='bula')&&p.p;
      return {acao:fn,car:true,fim:'',tid:x.tid,pk:p.k,p:p.p||'',cult:p.cult||e.cult,t:V+' bloqueado: carência sem dados suficientes em '+nm+' · '+p.t+'.',
        q:(p.q||CARD.quem.ag)+(bu?' confere a carência na bula do produto comercial e registra aqui':' confere a aplicação')+'; sem prazo conhecido a colheita não é autorizada.',h:'IN-04.dc.html#car:'+x.tid,hl:'Ver pendência no mapa'}; } }
  return null; }
function carAvisoAplic(c,o){ if(!o||carEhColheita(o)||(o.etapa!=='A liberar'&&o.etapa!=='Liberadas')) return null; const ts=carTals(o.talhao); if(!ts.length) return null;
  const J=carJanela(o); const ini=(J.ini&&J.ini>CARD.hoje)?J.ini:CARD.hoje;
  for(const x of ts){ const T=CARD.tal[x.tid]; let mx=null, desc=''; (o.ins||[]).forEach(i=>{ const r=carRegraC(c,i.p,T.cult); if(r.desconhecido){ desc=i.p; return; } if(!r.def||r.adj||r.na) return;
      if(typeof r.dias!=='number'){ desc=i.p; return; } if(!mx||r.dias>mx.dias) mx={p:i.p,dias:r.dias,conf:r.conf}; });
    if(!mx&&!desc) continue; const fp=mx?carAdd(ini,mx.dias):'';
    const col=Object.keys(c.ordens||{}).map(k=>c.ordens[k]).filter(h=>carEhColheita(h)&&['Encerradas','Canceladas'].indexOf(h.etapa)<0&&carTals(h.talhao).some(y=>y.tid===x.tid))
      .map(h=>({h,j:carJanela(h)})).filter(z=>z.h.etapa==='Em execução'||!z.j.ini||!fp||(z.j.fim>=ini&&z.j.ini<fp));
    if(!col.length&&!T.continua) continue;
    const alvo=col.length?col.map(z=>z.h.id+' ('+z.j.txt+')').join(', '):'as colheitas semanais do mamão em produção';
    return {sel:'Conflito com colheita'+(fp?' até '+carAte(fp):''),fim:fp,tid:x.tid,
      t:'conflito com a colheita em '+carNome(x.tid)+': '+(mx?mx.p+' tem carência de '+mx.dias+' dias'+(mx.conf?'':' (não conferida na bula)')+'; aplicado a partir de '+carBr(ini)+', a colheita fica impedida até '+carAte(fp):desc+' sem carência conhecida para '+T.cult.toLowerCase())
        +'. Afeta '+alvo+'. Para exportação, o limite do mercado de destino pode exigir intervalo maior. '+CARD.quem.ag+' decide: rever programação da aplicação ou da colheita'}; }
  return null; }
// colheita apontada dentro da carência (app ou web): fato registrado, nunca impedido → conferência com dono
function carColhidoEmCarencia(c,o){ if(!o||!carEhColheita(o)) return []; const out=[]; const ts=carTals(o.talhao); if(!ts.length) return out;
  (o.ap||[]).forEach(a=>{ if(a.st==='Previsto') return; const d=carIso(a.d); if(!d) return; const e=carEstado(c,ts[0].tid,d,a.parc||ts[0].parc,d);
    const r=e.ativos.filter(x=>x.d<=d)[0]; if(r) out.push({dia:a.dia,d,lote:carLid(o.id,a.dia),r}); }); return out; }
// comandos sobre o cenário (só dentro de cenMudar): destino do lote (reavalia e preserva a avaliação anterior) e janela da colheita
function carc_destino(c,lid,dest){ const L=carLotes(c); if(!L[lid]) throw new Error('Lote '+lid+' não encontrado.'); if(dest&&!CARD.dest[dest]) throw new Error('Destino sem cadastro.');
  const ant=carDestino(c,lid); if(ant===dest) throw new Error(lid+' já está com este destino.');
  const a0=carAvaliar(c,lid,ant), a1=carAvaliar(c,lid,dest); c.car=c.car||{}; c.car.dest=c.car.dest||{}; c.car.hist=c.car.hist||{};
  (c.car.hist[lid]=c.car.hist[lid]||[]).push({at:(typeof cenAgora==='function'?cenAgora():''),de:ant,para:dest,rot0:a0.rot,st0:a0.st,rot1:a1.rot,st1:a1.st});
  c.car.dest[lid]=dest; return {msg:lid+' · destino '+(dest?CARD.dest[dest].nome:'removido')+' · reavaliado: '+a1.rot+'. A avaliação anterior ('+a0.rot+') fica no histórico.'}; }
function carc_bula(c,p,cult,dias){ if(!p||!cult) throw new Error('Produto e cultura não identificados.');
  const t=String(dias===undefined||dias===null?'':dias).trim(); const n=Number(t.replace(',','.'));
  if(!t||!(n>=0&&n<=365)||Math.floor(n)!==n) throw new Error('Informe a carência da bula em dias inteiros (0 a 365).');
  c.car=c.car||{}; c.car.bula=c.car.bula||{}; const k=p+'|'+cult; const at=(typeof cenAgora==='function'?cenAgora():'');
  (c.car.bula[k]=c.car.bula[k]||[]).push({dias:n,at,por:CARD.quem.ag,p,cult});
  return {msg:'Carência de '+p+' em '+cult.toLowerCase()+' registrada: '+n+' dias, conferida na bula por '+CARD.quem.ag+'. Talhões, colheitas e lotes recalculados.'}; }
function carc_liberar_lote(c,lid){ const a=carAvaliar(c,lid); const D=CARD.dest[a.dest]||{};
  if(a.st!=='conforme'){ const x=a.motivos[0]||a.faltas[0]; throw new Error('Liberação comercial impedida: '+lid+' está '+a.rot+(x?' · '+x.t+' (quem resolve: '+x.q+')':'')+'.'); }
  const l=carLib(c,lid); if(l&&l.dest===a.dest) throw new Error(lid+' já está liberado para '+D.nome+'.');
  c.car=c.car||{}; c.car.lib=c.car.lib||{}; const at=(typeof cenAgora==='function'?cenAgora():'');
  (c.car.lib[lid]=c.car.lib[lid]||[]).push({dest:a.dest,at,por:CARD.quem.com,rot:a.rot});
  return {msg:lid+' liberado para '+D.nome+' no escopo avaliado. Outro destino ou dado novo reavalia o lote e suspende a liberação.'}; }
function carc_janela(c,id,iso){ const o=c.ordens[id]; if(!o) throw new Error('Ordem '+id+' não encontrada.'); if(!carEhColheita(o)) throw new Error(id+' não é colheita.');
  if(o.etapa!=='A liberar'&&o.etapa!=='Liberadas') throw new Error(id+' já começou: registre a colheita feita; a janela não muda mais.');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(iso||''))) throw new Error('Informe a nova data de início da colheita.');
  if(iso<CARD.hoje) throw new Error('A nova data não pode ser anterior a hoje ('+carBr(CARD.hoje)+').');
  o.osc=o.osc||{}; const ant=carJanela(o).txt; const nv='a partir de '+carBr(iso)+'/'+iso.slice(0,4); o.osc.janela=nv; if(o.osc.novo) o.osc.novo.janela=nv;
  const at=(typeof cenAgora==='function'?cenAgora():''); o.osc.carh=(o.osc.carh||[]).concat([{at,t:'Colheita reprogramada por '+CARD.quem.ag+(at?' às '+at:'')+': '+ant+' → '+nv+' (carência)'}]);
  const b=carBloqColheita(c,o,o.etapa==='A liberar'?'liberar':'iniciar');
  return {msg:id+' reprogramada para '+carBr(iso)+'. '+(b?'Ainda impedida: '+b.t:'A carência não impede mais; o destino de cada lote continua a avaliar.')}; }
// O.S. na lista, no painel e no Mapa (osMerge): selo, dono, aviso preventivo e janela reprogramada
function carMerge(o,co,c){ if(!co||typeof CARD==='undefined') return; try{
  if(co.osc&&co.osc.janela) o.janela=co.osc.janela; if(co.osc&&co.osc.carh) o.orig=(o.orig||[]).concat(co.osc.carh.map(h=>h.t));
  o.selos=(o.selos||[]).filter(s=>!/^(Carência|Conflito com colheita|Colhido em carência)/.test(s.t)); o.carB=null; o.carW=null; o.carE=null;
  if(co.etapa==='A liberar'||co.etapa==='Liberadas'){ const b=carBloqColheita(c,co,co.etapa==='A liberar'?'liberar':'iniciar');
    if(b){ o.carB=b; o.selos=o.selos.concat([{t:b.fim?'Carência até '+carAte(b.fim):'Carência sem dados',c:'red'}]); o.dono=CARD.quem.ag; o.prazo='rever programação da colheita'; }
    const w=carAvisoAplic(c,co); if(w){ o.carW=w; o.selos=o.selos.concat([{t:w.sel,c:'yellow'}]); if(co.etapa==='A liberar') o.obs=w.t; else o.aviso=w.t.charAt(0).toUpperCase()+w.t.slice(1)+'.'; } }
  if(co.etapa==='Em execução'&&carEhColheita(co)){ const b=carBloqColheita(c,co,'iniciar');
    if(b){ o.carE=b; o.selos=o.selos.concat([{t:b.fim?'Carência até '+carAte(b.fim):'Carência sem dados',c:'red'}]); o.dono=CARD.quem.ag;
      o.prazo=b.fim?'suspender novos turnos até '+carAte(b.fim)+' · '+b.p+' ('+b.os+')':'conferir a aplicação antes do próximo turno'; } }
  const cc=carColhidoEmCarencia(c,co); if(cc.length){ o.carCol=cc; o.selos=o.selos.concat([{t:'Colhido em carência · conferir',c:'red'}]);
    if(co.etapa==='Em execução'||co.etapa==='Em conferência'){ o.dono=CARD.quem.ag; o.prazo='conferir '+cc.map(x=>x.lote).join(', ')+' (colhido em carência)'; } }
  }catch(e){} }
// gancho de teste/inspeção (o script da tela roda isolado): carencia_test.py lê e muda o cenário pelas mesmas funções
try{ window.__car={carEstado,carAvaliar,carLotes,carBloqColheita,carAvisoAplic,carColhidoEmCarencia,carc_janela,carc_destino,carc_bula,carc_liberar_lote,carJanela,cenGet,cenMudar}; }catch(e){}
'''


def js_nucleo(app=False):
    """app=True: só o necessário para a guarda de colheita no app (sem LMR, destinos e registros de lote), página mais leve."""
    c = card()
    if app:
        c = dict(c, lmr={}, car0={}, prod={k: dict(v, usos={cu: {kk: u[kk] for kk in ('dias', 'conf', 'na', 'txt')} for cu, u in v['usos'].items()})
                                          for k, v in c['prod'].items()})
    return 'const CARD = ' + json.dumps(c, ensure_ascii=False).replace('</', '<\\/') + ';\n' + JS


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    if len(sys.argv) > 2 and sys.argv[1] == '--extrair':
        d = extrair_lmr(sys.argv[2]); print('LMR:', sum(len(c) for s in d['lmr'].values() for c in s.values()), 'linhas ·', len(d['lmr']), 'ingredientes · atualização', d['atualizacao'])
    else:
        c = card(); print(len(c['prod']), 'produtos ·', len(c['tal']), 'talhões ·', len(json.dumps(c, ensure_ascii=False)), 'bytes')
