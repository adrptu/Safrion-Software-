# -*- coding: utf-8 -*-
"""Revisão do Codex 6220145128 (PR #47) na frente CADASTROS-PADRAO, em 0d37cc1. Dados sintéticos.
  R1 (S2) documentos para crédito acompanham a mudança do CD-01 para o Crédito (credito_docs.js):
      R1a cadastro salvo ANTES da mudança (CAR, matrícula, módulos fiscais e contrato editados no formulário antigo), depois a Santa Rita é
          renomeada e uma fazenda é criada no CD-01: o Crédito mostra os valores editados com o nome novo, a fazenda criada tem CAR e
          matrícula a informar e aparece no seletor "Fazenda ou parceiro"; o nome antigo some
      R1b os campos movidos saem do cadastro salvo (uma fonte só) e ficam no Crédito
      R1c editar um documento no Crédito, recarregar, passar pelo CD-01 (salvar a fazenda) e voltar: nada reverte nem duplica
      R1d o que já foi editado no Crédito vence o valor antigo do cadastro (migração idempotente, sem sobrescrever)
      R1e 390 px: a lista de documentos abre com o nome atual e o painel do documento abre pelo toque na linha
      R1f o CD-01det (que também regrava as fazendas) migra antes de ler o cadastro
  R2 (S3) "A resolver" alcança a pendência da fazenda (linha-pai), sem somar área e sem inventar talhão:
      R2a fazenda incompleta sem talhões (Fazenda Teste) e fazenda incompleta com talhões em dia (Lagoa Grande) aparecem; contagem 3
      R2b talhão pendente (B1) aparece com a fazenda dele (Boa Vista, em dia) como contexto; talhões em dia ficam fora
      R2c "Todos" recupera tudo (mesmas linhas e a mesma abertura de antes) e conta fazendas + talhões
      R2d teclado: Enter no chip filtra; Enter na linha da fazenda abre o painel dela
      R2e 390 px: o filtro mostra as três pendências sem rolagem lateral da página
  Revisão do Codex 6221423767 (rev2), na 16ffe95:
  R3 (S2) gravação do documento que falha não é anunciada como salva: com o navegador recusando só safrion-credito-docs-v1 (QuotaExceededError
      sintético, ativo desde o carregamento), o cadastro antigo (CAR-LEGADO) aparece no Crédito; Salvar o CAR novo não confirma, o formulário
      fica aberto com o rascunho e o motivo, nada é gravado; com a gravação de volta, o mesmo Salvar grava; recarregar mostra o valor novo
  R4 (S2) documento automático (CAR, matrícula, contrato da fazenda) tem tipo e fazenda fixos: só leitura com o motivo no formulário; a mudança
      forçada no formulário e a chamada direta a credSalvarDoc (fonte da própria página) são recusadas sem gravar; nada muda de fazenda (1 CAR
      na Santa Rita, 1 na Fazenda Teste). Documento incluído pela pessoa continua editável (fazenda trocada, gravada e mantida ao recarregar)
Contraprova: CONTRAPROVA=1 RENDER_DIR=<_render da versão revisada> — a 0d37cc1 tem de reprovar R1a a R1d e R2a a R2c; a 16ffe95, R3 e R4
(CONTRA_ESPERA=R3,R4 diz o que a versão tem de reprovar; o padrão é o conjunto da rev1).
Uso (de gen37/, depois do build): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B cadastros_rev1_test.py   (fotos em REV1_FOTOS, se dado)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import dados_cad as DC

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
CONTRA = os.environ.get('CONTRAPROVA') == '1'
FOTOS = os.environ.get('REV1_FOTOS') or ''
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK    ' + nome, flush=True)
    else: falhas.append(nome.split(' ')[0]); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

CKEY, DKEY = 'talhao-os-cd01-v1', 'safrion-credito-docs-v1'
def faz_atual(f, **mud):   # fazenda no formato salvo de hoje (sem os campos que foram para o Crédito)
    mun, uf = f['mun'].rsplit('/', 1)
    v = dict(nome=f['nome'], empresa=f['empresa'], mun=mun, uf=uf, fuso=f['fuso'], area=f['area'], posse=f['posse'], fim=f['fim'], sit=f['sit']); v.update(mud)
    return dict(id=f['id'], v=v)
def faz_antiga(f, **mud):   # formato salvo ANTES de 16/10 (formulário antigo do CD-01, com CAR, matrícula, módulos fiscais e contrato)
    x = faz_atual(f); x['v'].update(arrend=f['arrend'], custo=f['custo'], car=f['car'], matr=f['matr'], pend=f['pend'], mf=f.get('mf', ''), kml=''); x['v'].update(mud); return x
SR, BV, LG = DC.FAZENDAS[0], DC.FAZENDAS[1], DC.FAZENDAS[2]
LEGADO = {'faz': [faz_antiga(SR, car='GO-CAR-EDITADO-77', matr='12.401-E · CRI de Rio Verde', mf=4.1),
                  faz_antiga(BV, arrend='Otávio Almeida · contrato editado', custo=9), faz_antiga(LG)], 'tal': []}

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
# R3: o navegador recusa só a chave dos documentos do Crédito, desde o carregamento da página, enquanto a marca __falha_docs estiver ligada
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "(()=>{ try{ if(localStorage.getItem('__falha_docs')==='1'){ const s0=Storage.prototype.setItem; window.__setItem0=s0;"
       " Storage.prototype.setItem=function(k,v){ if(k==='safrion-credito-docs-v1') throw new DOMException('quota sintética','QuotaExceededError'); return s0.call(this,k,v); }; } }catch(e){} })()"})
VOLTA = "(()=>{ localStorage.removeItem('__falha_docs'); if(window.__setItem0) Storage.prototype.setItem=window.__setItem0; return 1; })()"
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def limpa(estado=None, docs=None):
    c.goto(U('Main.dc.html'), .3)
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    if estado is not None: J(f"localStorage.setItem({json.dumps(CKEY)}, {json.dumps(json.dumps(estado, ensure_ascii=False))})")
    if docs is not None: J(f"localStorage.setItem({json.dumps(DKEY)}, {json.dumps(json.dumps(docs, ensure_ascii=False))})")
def ir(url, esp=1.4):   # carga nova sempre (ir para o mesmo endereço com # seria só troca de âncora, sem recarregar)
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.2); c.goto(U(url), esp)
def foto(nome):
    if FOTOS: os.makedirs(FOTOS, exist_ok=True); c.shot(os.path.join(FOTOS, nome + '.png'))
SETV = ("((sel,val)=>{const i=document.querySelector(sel); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;"
        " Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return true;})")
def fset(k, val, gid): r = J(f"({SETV})('aside[role=dialog] #fx_{gid}_{k}',{json.dumps(val)})"); time.sleep(.2); return r
def btn(t, raiz='aside[role=dialog]'):
    r = J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(raiz + ' button')})].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()")
    time.sleep(.5); return r
def abre_linha(gid, pref):   # clique no texto da 1ª célula (como a pessoa), não na seta
    r = J(f"(()=>{{const t=document.querySelector('[data-g2g={gid}]'); if(!t) return 'sem grade'; const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.replace(/\\s+/g,' ').trim().replace(/^[▾▸]\\s*/,'').indexOf({json.dumps(pref)})===0);"
          " if(!r) return 'sem linha'; const a=r.querySelector('[role=cell] .g2pw')||r.querySelector('[role=cell]'); a.click(); return 'ok';})()")
    time.sleep(.5); return r
LINHAS = r"""(gid=>{ const t=document.querySelector('[data-g2g='+gid+']'); if(!t) return [];
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\s+/g,' ').trim());
  return [...t.querySelectorAll('[role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>{ const o={_id:r.dataset.rid}; [...r.querySelectorAll('[role=cell]')].forEach((c,i)=>{ if(hs[i]) o[hs[i]]=c.innerText.replace(/\s+/g,' ').trim(); }); return o; }); })"""
def docs(): return J(f"({LINHAS})('g_doc')") or []
def doc(tipo, tit): return [d for d in docs() if d.get('Documento') == tipo and (d.get('Fazenda ou parceiro') or '').startswith(tit)]
def ler(k): return J(f"JSON.parse(localStorage.getItem({json.dumps(k)})||'null')")
DOCS = 'GE-08.dc.html#vis=documentos'
try:
    c.aparelho(1440, 900, 1, False)
    # ================= R1 · documentos para crédito =================
    limpa(LEGADO); ir('CD-01.dc.html')
    abre_linha('g_tal', 'Santa Rita'); fset('nome', 'Santa Rita do Sul', 'g_faz'); btn('Salvar')
    J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Criar fazenda'); b&&b.click();})()"); time.sleep(.5)
    fset('nome', 'Fazenda Teste', 'g_faz'); fset('mun', 'Jataí', 'g_faz'); fset('area', '100', 'g_faz'); btn('Salvar')
    cad = ler(CKEY) or {}; nomes = [f['v'].get('nome') for f in cad.get('faz', [])]
    ir(DOCS); ds = docs()
    car = doc('CAR', 'Santa Rita do Sul'); mat = doc('Matrícula', 'Santa Rita do Sul'); arr = doc('Contrato de arrendamento', 'Boa Vista')
    ft = [d for d in ds if (d.get('Fazenda ou parceiro') or '').startswith('Fazenda Teste')]; velho = [d for d in ds if d.get('Fazenda ou parceiro') == 'Santa Rita']
    chk('R1a valores editados antes da mudança seguem no Crédito com o nome novo (CAR, módulos fiscais, matrícula e contrato); o nome antigo some',
        'Santa Rita do Sul' in nomes and len(car) == 1 and 'GO-CAR-EDITADO-77' in car[0].get('Número ou registro', '') and '4,1 módulos fiscais' in car[0].get('Número ou registro', '')
        and len(mat) == 1 and '12.401-E · CRI de Rio Verde' in mat[0].get('Número ou registro', '') and len(arr) == 1 and 'contrato editado' in arr[0].get('Número ou registro', '')
        and '9 sc/ha/ano' in arr[0].get('Número ou registro', '') and not velho, [nomes, car, mat, arr, velho[:2]])
    chk('R1a fazenda criada no CD-01 aparece no Crédito com CAR e matrícula a informar (pendentes)',
        sorted(d.get('Documento') for d in ft) == ['CAR', 'Matrícula'] and all(d.get('Situação', '').startswith('Pendente') for d in ft), ft)
    J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Incluir documento'); b&&b.click();})()"); time.sleep(.5)
    ops = J("[...document.querySelectorAll('aside[role=dialog] #fx_g_doc_tit option')].map(o=>o.textContent.trim())") or []
    chk('R1a seletor "Fazenda ou parceiro" segue o cadastro atual: Santa Rita do Sul, Boa Vista, Lagoa Grande e Fazenda Teste; sem o nome antigo',
        all(n in ops for n in ('Santa Rita do Sul', 'Boa Vista', 'Lagoa Grande', 'Fazenda Teste')) and 'Santa Rita' not in ops, ops)
    btn('Cancelar'); btn('Descartar alterações')
    sr = next((f for f in (ler(CKEY) or {}).get('faz', []) if f.get('id') == 'SR'), {}); ed = (ler(DKEY) or {}).get('ed', {})
    chk('R1b os campos movidos saem do cadastro salvo e ficam no Crédito pelo id estável da fazenda (dc_car_SR, dc_mat_SR, dc_arr_BV)',
        sr and not any(k in sr.get('v', {}) for k in ('car', 'matr', 'mf', 'arrend', 'custo', 'pend')) and ed.get('dc_car_SR', {}).get('num') == 'GO-CAR-EDITADO-77'
        and ed.get('dc_mat_SR', {}).get('num') == '12.401-E · CRI de Rio Verde' and ed.get('dc_arr_BV', {}).get('custo') == 9, [sr.get('v'), {k: ed.get(k) for k in ('dc_car_SR', 'dc_mat_SR', 'dc_arr_BV')}])
    foto('r1_documentos_1440')
    # R1c: editar o CAR da fazenda criada, recarregar, passar pelo CD-01 (salvar a Santa Rita do Sul) e voltar
    n0 = len(docs())
    abrir_ft = J("(()=>{const t=document.querySelector('[data-g2g=g_doc]'); const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.indexOf('Fazenda Teste')>=0&&x.innerText.indexOf('CAR')>=0); if(!r) return false; (r.querySelector('[role=cell] .g2pw')||r).click(); return true;})()")
    time.sleep(.5); fset('num', 'CAR-TESTE-9', 'g_doc'); btn('Salvar')
    ir(DOCS); a1 = doc('CAR', 'Fazenda Teste'); n1 = len(docs())
    ir('CD-01.dc.html'); abre_linha('g_tal', 'Santa Rita do Sul'); fset('area', '1490', 'g_faz'); btn('Salvar')
    ir(DOCS); a2 = doc('CAR', 'Fazenda Teste'); n2 = len(docs()); ids = [d['_id'] for d in docs()]
    chk('R1c editar no Crédito, recarregar, salvar a fazenda no CD-01 e voltar: o CAR editado fica, nenhum documento duplica ou volta ao antigo',
        abrir_ft and len(a1) == 1 and 'CAR-TESTE-9' in a1[0].get('Número ou registro', '') and len(a2) == 1 and 'CAR-TESTE-9' in a2[0].get('Número ou registro', '')
        and n0 == n1 == n2 and len(ids) == len(set(ids)) and len(doc('CAR', 'Santa Rita do Sul')) == 1 and 'GO-CAR-EDITADO-77' in doc('CAR', 'Santa Rita do Sul')[0].get('Número ou registro', ''),
        [abrir_ft, a1, a2, n0, n1, n2])
    # R1d: o Crédito já tem o CAR editado e o cadastro ainda traz o valor antigo (outra aba, por exemplo): o Crédito vence
    limpa({'faz': [faz_antiga(SR, car='CAR-LEGADO'), faz_atual(BV), faz_atual(LG)], 'tal': []},
          {'v': 1, 'ed': {'dc_car_SR': {'tipo': 'CAR', 'fid': 'SR', 'num': 'CAR-DO-CREDITO', 'mf': '', 'val': '', 'pend': '', 'exig': ''}}})
    ir(DOCS); cr = doc('CAR', 'Santa Rita'); sr = next((f for f in (ler(CKEY) or {}).get('faz', []) if f.get('id') == 'SR'), {})
    chk('R1d a edição do Crédito vence o valor antigo do cadastro, que sai do cadastro sem duplicar o documento',
        len(cr) == 1 and 'CAR-DO-CREDITO' in cr[0].get('Número ou registro', '') and 'car' not in sr.get('v', {}), [cr, sr.get('v')])
    # ================= R2 · "A resolver" alcança a fazenda =================
    FT = dict(id='FT', v=dict(nome='Fazenda Teste', empresa='', mun='Jataí', uf='GO', fuso=SR['fuso'], area=100, posse='', fim='', sit='Ativa'))
    limpa({'faz': [faz_atual(SR), faz_atual(BV), faz_atual(LG), FT], 'tal': []}); ir('CD-01.dc.html')
    CHIPS = "[...document.querySelectorAll('[data-g2g=g_tal]')].length?[...document.querySelectorAll('button[aria-pressed]')].filter(b=>b.getClientRects().length&&/^(Todos|A resolver|Inativos)/.test(b.innerText.trim())).map(b=>b.innerText.replace(/\\s+/g,' ').trim()):[]"
    PAIS = "(()=>{const t=document.querySelector('[data-g2g=g_tal]'); return [...t.querySelectorAll('[role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.innerText.replace(/\\s+/g,' ').trim());})()"
    def vis(): return [x.lstrip('▾▸ ').strip() for x in (J(PAIS) or [])]
    def chip(t): return J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-pressed]')].find(b=>b.getClientRects().length&&b.innerText.trim().indexOf({json.dumps(t)})===0); if(!b) return false; b.click(); return true;}})()")
    antes = vis(); x0 = J("JSON.stringify([...document.querySelectorAll('[data-g2g=g_tal] [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.dataset.rid))")
    ch0 = J(CHIPS) or []
    chip('A resolver'); time.sleep(.4); res = vis(); ch1 = J(CHIPS) or []
    tem = lambda pref: any(x.startswith(pref) for x in res)
    chk('R2a "A resolver" mostra a fazenda incompleta sem talhões (Fazenda Teste) e a incompleta com talhões em dia (Lagoa Grande); conta 3 (B1 + 2 fazendas)',
        tem('Fazenda Teste') and tem('Lagoa Grande') and any(x.startswith('A resolver 3') for x in ch1), [res, ch1])
    chk('R2b B1 (sem polígono) aparece com a Boa Vista como contexto; talhões em dia (T1, PV01) ficam fora; nenhuma área somada ou talhão inventado',
        tem('Boa Vista') and tem('B1') and not tem('T1 ') and not tem('PV01') and len(res) == 4, res)
    foto('r2_a_resolver_1440')
    chip('Todos'); time.sleep(.4); dep = vis(); x1 = J("JSON.stringify([...document.querySelectorAll('[data-g2g=g_tal] [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.dataset.rid))")
    chk('R2c "Todos" recupera tudo (mesmas linhas e abertura de antes) e conta fazendas + talhões (4 + 32 = 36)',
        dep == antes and x1 == x0 and any(x.startswith('Todos 36') for x in (J(CHIPS) or [])), [len(antes), len(dep), ch0, J(CHIPS)])
    # R2d teclado
    J("(()=>{const b=[...document.querySelectorAll('button[aria-pressed]')].find(b=>b.getClientRects().length&&b.innerText.trim().indexOf('A resolver')===0); b&&b.focus();})()")
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5); kres = vis()
    J("(()=>{const t=document.querySelector('[data-g2g=g_tal]'); const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.indexOf('Fazenda Teste')>=0); r&&r.focus();})()")
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5)
    tit = J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''") or ''
    chk('R2d teclado: Enter no chip "A resolver" filtra; Enter na linha da Fazenda Teste abre o painel dela', any(x.startswith('Fazenda Teste') for x in kres) and 'Fazenda Teste' in tit, [kres, tit])
    btn('Cancelar'); btn('Fechar')
    # R2e 390 px
    c.aparelho(390, 844, 2, True); ir('CD-01.dc.html'); chip('A resolver'); time.sleep(.4); r390 = vis()
    larg = J("document.documentElement.scrollWidth<=window.innerWidth+1")
    chk('R2e 390 px: "A resolver" mostra Fazenda Teste, Lagoa Grande e B1 sem rolagem lateral da página',
        any(x.startswith('Fazenda Teste') for x in r390) and any(x.startswith('Lagoa Grande') for x in r390) and any(x.startswith('B1') for x in r390) and larg, [r390, larg])
    foto('r2_a_resolver_390')
    # R1e 390 px: documentos com o nome atual e o painel pelo toque na linha
    limpa(LEGADO); ir('CD-01.dc.html'); abre_linha('g_tal', 'Santa Rita'); fset('nome', 'Santa Rita do Sul', 'g_faz'); btn('Salvar')
    ir(DOCS); d390 = doc('CAR', 'Santa Rita do Sul')
    b = J("(()=>{const t=document.querySelector('[data-g2g=g_doc]'); const r=t&&[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.indexOf('Santa Rita do Sul')>=0); if(!r) return null; r.scrollIntoView({block:'center'}); const q=(r.querySelector('[role=cell] .g2pw')||r).getBoundingClientRect(); return {x:q.left+8,y:q.top+q.height/2};})()")
    if b: c.toque(b['x'], b['y']); time.sleep(.6)
    t390 = J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''") or ''
    chk('R1e 390 px: documentos com o nome atual (Santa Rita do Sul) e o painel do documento abre pelo toque na linha',
        len(d390) == 1 and 'GO-CAR-EDITADO-77' in d390[0].get('Número ou registro', '') and 'Documento' in t390, [d390, t390])
    foto('r1_documentos_390')
    # R1f o detalhe do talhão (CD-01det) também migra antes de ler o cadastro (ele regrava as fazendas ao salvar)
    c.aparelho(1440, 900, 1, False); limpa(LEGADO); ir('CD-01det.dc.html#talhao=T1')
    sr = next((f for f in (ler(CKEY) or {}).get('faz', []) if f.get('id') == 'SR'), {}); ed = (ler(DKEY) or {}).get('ed', {})
    chk('R1f CD-01det com cadastro antigo: migra para o Crédito antes de ler (o CAR editado fica no Crédito, sai do cadastro) e abre sem erro',
        'car' not in sr.get('v', {}) and ed.get('dc_car_SR', {}).get('num') == 'GO-CAR-EDITADO-77' and 'T1' in (J("(document.querySelector('main')||{}).innerText||''") or ''), [sr.get('v'), ed.get('dc_car_SR')])
    # ================= R3 · gravação que falha não é anunciada como salva =================
    c.aparelho(1440, 900, 1, False)
    # a recusa vale desde antes do CD-01: a migração também não grava, e o Crédito mostra o CAR antigo que o cadastro ainda guarda
    limpa({'faz': [faz_antiga(SR, car='CAR-LEGADO'), faz_atual(BV), faz_atual(LG)], 'tal': []}); J("localStorage.setItem('__falha_docs','1')")
    ir('CD-01.dc.html'); abre_linha('g_tal', 'Santa Rita'); fset('nome', 'Santa Rita renomeada', 'g_faz'); btn('Salvar')
    ir(DOCS)
    leg = doc('CAR', 'Santa Rita renomeada')
    abriu = J("(()=>{const t=document.querySelector('[data-g2g=g_doc]'); const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.indexOf('Santa Rita renomeada')>=0&&/(^|\\s)CAR(\\s|$)/.test(x.innerText)); if(!r) return false; (r.querySelector('[role=cell] .g2pw')||r).click(); return true;})()")
    time.sleep(.5); fset('num', 'CAR-NOVO-1', 'g_doc'); J("window.__t=[]; new MutationObserver(()=>{ const s=[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | '); if(s) window.__t.push(s); }).observe(document.body,{subtree:true,childList:true,characterData:true})")
    btn('Salvar'); time.sleep(.3)
    aberto = J("!!document.querySelector('aside[role=dialog] #fx_g_doc_num')"); rasc = J("(document.querySelector('aside[role=dialog] #fx_g_doc_num')||{}).value||''")
    dlg = J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''; hist = J("window.__t") or []
    avisos = J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    ed0 = (ler(DKEY) or {}).get('ed', {}); foto('r3_nao_salvo_1440')
    chk('R3a navegador recusando os documentos: o valor antigo do cadastro (CAR-LEGADO) aparece no Crédito com o nome novo; Salvar não confirma, o formulário fica com o rascunho e o motivo, nada gravado',
        len(leg) == 1 and 'CAR-LEGADO' in leg[0].get('Número ou registro', '') and abriu and aberto and rasc == 'CAR-NOVO-1' and 'não gravou' in dlg
        and 'Não salvo' in avisos and not any('Salvo: CAR' in x for x in hist + [avisos]) and (ed0.get('dc_car_SR') or {}).get('num') != 'CAR-NOVO-1', [leg, abriu, aberto, rasc, 'não gravou' in dlg, avisos[:300], hist[-3:], ed0])
    J(VOLTA); btn('Salvar'); time.sleep(.3)
    fechou = not J("!!document.querySelector('aside[role=dialog] #fx_g_doc_num')"); ed1 = (ler(DKEY) or {}).get('ed', {})
    ir(DOCS); novo = doc('CAR', 'Santa Rita renomeada'); sr = next((f for f in (ler(CKEY) or {}).get('faz', []) if f.get('id') == 'SR'), {})
    chk('R3b com a gravação de volta, o mesmo Salvar grava; recarregar mostra CAR-NOVO-1 uma vez, e o cadastro já não guarda o CAR antigo',
        fechou and ed1.get('dc_car_SR', {}).get('num') == 'CAR-NOVO-1' and len(novo) == 1 and 'CAR-NOVO-1' in novo[0].get('Número ou registro', '') and 'car' not in sr.get('v', {}),
        [fechou, ed1.get('dc_car_SR'), novo, sorted(sr.get('v', {}).keys())])
    # ================= R4 · tipo e fazenda do documento automático são fixos =================
    FT2 = dict(id='FT', v=dict(nome='Fazenda Teste', empresa='Santa Rita Agro', mun='Jataí', uf='GO', fuso=SR['fuso'], area=100, posse='Própria', fim='', sit='Ativa'))
    limpa({'faz': [faz_atual(SR), faz_atual(BV), faz_atual(LG), FT2], 'tal': []}); ir(DOCS)
    J("(()=>{const t=document.querySelector('[data-g2g=g_doc]'); const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.dataset.rid==='dc_car_SR'); r&&(r.querySelector('[role=cell] .g2pw')||r).click();})()"); time.sleep(.5)
    ro = J("(()=>{const q=s=>document.querySelector('aside[role=dialog] '+s); const a=q('#fx_g_doc_tipo'), b=q('#fx_g_doc_tit'); const d=(document.querySelector('aside[role=dialog]')||{}).innerText||'';"
           " return {tipo:!!a&&a.disabled, tit:!!b&&b.disabled, motivo:/tipo e a fazenda não mudam/.test(d)};})()") or {}
    foto('r4_automatico_so_leitura_1440')
    J(f"({SETV})('aside[role=dialog] #fx_g_doc_tit','Fazenda Teste')"); J(f"({SETV})('aside[role=dialog] #fx_g_doc_num','FORCADO-1')"); time.sleep(.2); btn('Salvar'); time.sleep(.3)
    ainda = J("!!document.querySelector('aside[role=dialog] #fx_g_doc_num')"); btn('Cancelar'); btn('Descartar alterações')
    ed2 = (ler(DKEY) or {}).get('ed', {}); ir(DOCS); ncar = (len(doc('CAR', 'Santa Rita')), len(doc('CAR', 'Fazenda Teste')))
    chk('R4a formulário: tipo e fazenda do CAR automático só para leitura, com o motivo; a troca forçada para a Fazenda Teste é recusada, nada gravado (1 CAR em cada fazenda)',
        ro.get('tipo') and ro.get('tit') and ro.get('motivo') and ainda and 'dc_car_SR' not in ed2 and ncar == (1, 1), [ro, ainda, ed2, ncar])
    # chamada direta ao comando, com a fonte que a própria página carrega (credito_docs.js embutido no GE-08)
    pg = open(os.path.join(R, 'GE-08.dc.html'), encoding='utf-8').read(); i = pg.find('const CRED_CADKEY'); j = pg.find(';\n', pg.find('const CRED_SEED_FAZ=')) + 2
    src = pg[i:j] if i >= 0 and j > i else ''
    dire = J("(()=>{ " + src + " const fz=credFazendas(CRED_SEED_FAZ); const a=credSalvarDoc({id:'dc_car_SR',v:{tipo:'CAR',tit:'Fazenda Teste',num:'DIRETO-1'}},fz,CRED_SEED_DOCS);"
             " const b=credSalvarDoc({id:'dc_car_SR',v:{tipo:'Matrícula',tit:'Santa Rita',num:'DIRETO-2'}},fz,CRED_SEED_DOCS);"
             " const c=credSalvarDoc({id:'dc_mat_FT',v:{tipo:'Matrícula',tit:'Santa Rita',num:'DIRETO-3'}},fz,CRED_SEED_DOCS);"
             " return {a:a, b:b, c:c, ed:(JSON.parse(localStorage.getItem('safrion-credito-docs-v1')||'{}').ed||{})}; })()") if src else None
    dd = dire or {}
    chk('R4b chamada direta a credSalvarDoc: trocar a fazenda ou o tipo de documento automático é recusado com o motivo e nada é gravado',
        bool(src) and all(isinstance(dd.get(k), str) and 'não mudam' in dd.get(k) for k in ('a', 'b', 'c')) and not any(k in dd.get('ed', {}) for k in ('dc_car_SR', 'dc_mat_FT')), dd)
    # documento incluído pela pessoa: identidade própria, continua editável (inclusive a fazenda)
    J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Incluir documento'); b&&b.click();})()"); time.sleep(.5)
    fset('tipo', 'Outro', 'g_doc'); fset('tit', 'Fazenda Teste', 'g_doc'); fset('num', 'OUT-1', 'g_doc'); btn('Salvar')
    J("(()=>{const t=document.querySelector('[data-g2g=g_doc]'); const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getClientRects().length&&x.innerText.indexOf('OUT-1')>=0); r&&(r.querySelector('[role=cell] .g2pw')||r).click();})()"); time.sleep(.5)
    livre = J("(()=>{const a=document.querySelector('aside[role=dialog] #fx_g_doc_tipo'), b=document.querySelector('aside[role=dialog] #fx_g_doc_tit'); return !!a&&!!b&&!a.disabled&&!b.disabled;})()")
    fset('tit', 'Boa Vista', 'g_doc'); btn('Salvar'); ir(DOCS); out = [d for d in docs() if 'OUT-1' in d.get('Número ou registro', '')]
    chk('R4c documento incluído pela pessoa continua editável: a fazenda troca para Boa Vista, grava e se mantém ao recarregar (um só)',
        livre and len(out) == 1 and out[0].get('Fazenda ou parceiro') == 'Boa Vista', [livre, out])
    chk('R0 sem erro de JS', not (J("window.__e") or []), J("window.__e"))
finally:
    c.close(); srv.terminate()
tot = ok_n + len(falhas)
if CONTRA:
    print(f'CONTRAPROVA: a versão revisada reprova {sorted(set(falhas))} · {ok_n}/{tot} passam')
    esp = set((os.environ.get('CONTRA_ESPERA') or 'R1a,R1b,R1c,R1d,R2a,R2b,R2c').split(','))
    sys.exit(0 if esp <= set(falhas) else 1)
print(f'RESULTADO: {ok_n}/{tot}' + ('' if not falhas else ' · FALHAS: ' + ', '.join(falhas)))
sys.exit(1 if falhas else 0)
