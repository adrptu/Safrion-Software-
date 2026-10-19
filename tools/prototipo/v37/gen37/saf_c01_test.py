# -*- coding: utf-8 -*-
"""Teste de navegador · SAF-C01 (Codex + Gemini, PR #47, comentário 6079770308): a trava de soma (R-14/T-soma) vale com uma perene antiga
no talhão. Tudo pela tela, sem injetar dado para a trava: cria a safra "Café antigo BV" (2020) e grava café 40 ha numa parcela do B1
(Boa Vista, 120 ha); cria a "Safra BV 2027" e tenta, com a soja de 2027:
  gravar 90 ha (café 40 + 90 = 130 > 120) → recusa com a mensagem da trava, nada gravado; o limite 80 ha (soma = 120) grava;
  editar a soja para 90 ha → recusa, a área gravada continua 80 ha;
  dividir o B1 em 50 + 40 ha (130 > 120) → recusa ("A divisão travaria a área"), nada gravado; 50 + 30 ha (120) grava.
Só a última parte injeta estado (dado antigo, como o S3.4 do saf_revisao_test): soja com 90 ha já gravada → Situação "Sobreposição",
motivo, nota e faixa "· 10 ha em sobreposição".
Correções da verificação (3 verificadores, 09/10/2026), também só pela tela:
  área livre do aviso ao gravar e ao dividir pela mesma conta da tabela (com o café, 0 ha; antes "40 ha livres");
  painel Dividir com a capacidade do serviço: resumo "outras safras 40 ha", selo, "+ Adicionar parcela" (nome que não é o do café, área que
  cabe) e "Distribuir área igualmente" (reparte 80 ha, não 120); recusa com mensagem agregada, sem "Máximo 0 ha" por parcela;
  roteiro do ADENDO do Codex (C1 com café de 2019 reduzido a 20 ha, safra 2028): 30 ha recusado com "Máximo 18 ha" e a pista "reduza a área",
  18 ha grava com "0 ha livres em C1";
  perene numa safra antiga com anual futura: parcela digitada igual à da soja de 2027 → "use outra parcela (ex.: B1-B)", sem "replaneje";
  sem digitar, a parcela sugerida é a B1-B e grava.
Em 1440 × 900 e 390 × 844 (toque). Emulação no Chrome headless, não aparelho físico.
Uso: python3 saf_c01_test.py [desktop|celular|tudo]   (padrão: tudo)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, cv_todas_sempre
import saf_nav_lib as L
from saf_nav_lib import *   # chk, info, rows, nivel0, faixa, toast, nota, painel, campos, fset, botao, salvar, na_linha, clica_linha, abre, cria_safra, folhas, alerta, linha…
MODO = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
PAINEL = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)||document"
G = 'g_cult_NOVA'
def cancela():
    botao('Cancelar', PAINEL)
    if 'Há alterações' in painel(): botao('Descartar alterações')
def dv(): return c.js("JSON.parse(JSON.stringify(window.__safSelf.state.dv||null))")
def dv_area(local, val):
    r = c.js(f"""(()=>{{const e=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.offsetParent&&x.getAttribute('aria-label')==={json.dumps('Área de ' + local + ' em hectares')});
      if(!e) return 'sem campo'; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.3); return r
def dv_nome(atual, novo):
    r = c.js(f"""(()=>{{const e=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.offsetParent&&x.getAttribute('aria-label')==={json.dumps('Nome da parcela ' + atual)});
      if(!e) return 'sem campo'; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,{json.dumps(novo)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.3); return r
def soja(sid): return [x for x in folhas(G) if x['v'].get('saf') == sid and x['v'].get('cult') == 'Soja']
def de(sid, cult): return [x for x in folhas(G) if x['v'].get('saf') == sid and x['v'].get('cult') == cult]
def resumo(): return c.js("""(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); if(!a) return ''; const t=a.innerText.replace(/\\s+/g,' ');
  const m=t.match(/Talhão [\\d.,]+ ha( · outras safras [\\d.,]+ ha)? · alocado [\\d.,]+ ha · livre [\\d.,]+ ha/); return m?m[0]:'';})()""") or ''
def erros_dv(): return c.js("JSON.parse(JSON.stringify((window.__safSelf.state.dv||{}).err||{}))") or {}
def cafe_e_safra(nome_cafe, ini_cafe, fim_cafe):
    """Pela tela: safra do café na Boa Vista com café 40 ha plantado em 01/01/2020 numa parcela do B1; depois a "Safra BV 2027"."""
    n0 = cria_safra(nome_cafe, ini_cafe, fim_cafe, 'Boa Vista')
    na_linha('B1', 'Planejar ›')
    for k, v in (('cult', 'Café'), ('var', 'Catuaí 144'), ('plano', ''), ('area', '40'), ('plantio', '2020-01-01'), ('meta', '38')): fset(G, k, v)
    salvar(); t = toast(); cafe = [x for x in folhas(G) if x['v'].get('saf') == n0]
    pc = cafe[0]['v'].get('local') if cafe else '?'
    chk(f'{TAG[0]} preparo: café 40 ha plantado em 01/01/2020 na parcela {pc} do B1 ({nome_cafe})',
        'Cultivo incluído como parcela' in t and len(cafe) == 1 and cafe[0]['v'].get('area') == 40, (alerta(), t, cafe))
    n1 = cria_safra('Safra BV 2027', '2027-01-01', '2027-12-31', 'Boa Vista'); b1 = linha('B1') or {}
    chk(f'{TAG[0]} Safra BV 2027: B1 Livre 80 ha (o café de 2020 ocupa 40)', (b1.get('SITUAÇÃO'), b1.get('ÁREA LIVRE')) == ('Livre', '80 ha'), b1)
    return n1, pc
def planejar_soja(area):
    na_linha('B1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('area', area), ('plantio', '2027-06-01'), ('meta', '60')): fset(G, k, v)
    salvar()
def msg(pc, safra_cafe): return f'De 12/05/2027 a 27/09/2027, 40 ha de B1 estão com Café ({pc}, {safra_cafe}). Máximo 80 ha nesse período.'
TAG = ['']
def fluxo_gravar_editar(w, h, toque):
    """Café na safra dele, de 2020 (a 2027 oferece "Vincular ciclo ›" no B1): gravar e editar a soja."""
    tag = TAG[0] = f'{w}×{h} gravar/editar'
    abre('#saf=S2627&passo=safra', w, h, toque)
    n1, pc = cafe_e_safra('Café antigo BV', '2020-01-01', '2020-12-31'); MSG = msg(pc, 'Café antigo BV')
    planejar_soja('90'); al = alerta()
    chk(f'{tag}: gravar soja 90 ha (café 40 + 90 = 130 > 120 ha) é recusado com a mensagem da trava; painel aberto; nada gravado',
        MSG in al and painel() != '' and not soja(n1), (al, MSG, soja(n1)))
    fset(G, 'area', '80'); salvar(); t = toast(); s1 = soja(n1)
    chk(f'{tag}: limite, soja 80 ha (soma = 120 ha) grava', 'Cultivo incluído como parcela' in t and len(s1) == 1 and s1[0]['v'].get('area') == 80, (alerta(), t, s1))
    chk(f'{tag}: o aviso diz a área livre da tabela (café 40 + soja 80 = 120: "0 ha livres em B1"; antes "40 ha livres")', '· 0 ha livres em B1' in t, t)
    clica_linha(s1[0]['id'] if s1 else ''); fset(G, 'area', '90'); salvar(); al = alerta()
    chk(f'{tag}: editar a soja para 90 ha é recusado com a mensagem da trava; continua 80 ha', MSG in al and [x['v'].get('area') for x in soja(n1)] == [80], (al, soja(n1)))
    fset(G, 'area', '80'); fset(G, 'meta', '62'); salvar(); t = toast()
    chk(f'{tag}: editar só a meta (80 ha, no limite) grava', [x['v'].get('meta') for x in soja(n1)] == [62] and alerta() == '(painel fechado)', (alerta(), t, soja(n1)))
    chk(f'{tag}: sem rolagem lateral da página', not c.js("document.documentElement.scrollWidth>innerWidth+1"))
    chk(f'{tag}: sem erro de JS', erros() == '', erros())
def fluxo_dividir(w, h, toque):
    """Café de 2020 registrado na safra 2026/27 (lavoura em campo; cruza a 2027, então o B1 oferece "Dividir"): dividir e tabela."""
    tag = TAG[0] = f'{w}×{h} dividir'
    abre('#saf=S2627&passo=safra', w, h, toque)
    n1, pc = cafe_e_safra('Café BV 2026/27', '2026-09-01', '2027-08-31')
    planejar_soja('90'); al = alerta()
    chk(f'{tag}: gravar soja 90 ha também é recusado (café de 2020 numa safra que cruza)', msg(pc, 'Café BV 2026/27') in al and not soja(n1), al)
    fset(G, 'area', '80'); salvar(); s1 = soja(n1); ps = s1[0]['v'].get('local') if s1 else '?'
    na_linha('B1', 'Dividir'); d = dv() or {'rows': []}
    chk(f'{tag}: Dividir B1 abre só a soja desta safra ({ps}, 80 ha)', [(r.get('local'), r.get('area')) for r in d['rows']] == [(ps, '80')], d['rows'])
    pa = painel()
    chk(f'{tag}: resumo do Dividir pela capacidade do serviço: "outras safras 40 ha · alocado 80 ha · livre 0 ha" e "Área conferida" (antes "livre 40 ha")',
        resumo() == 'Talhão 120 ha · outras safras 40 ha · alocado 80 ha · livre 0 ha' and 'Área conferida' in pa, (resumo(), pa[:300]))
    botao('+ Adicionar parcela', PAINEL); d = dv() or {'rows': []}; nw = d['rows'][-1] if len(d['rows']) > 1 else {}
    chk(f'{tag}: "+ Adicionar parcela" não propõe o nome do café ({pc}) nem área que ele ocupa (antes: {pc} com 40 ha)',
        nw.get('local') not in (pc, None, '', ps) and nw.get('area') == '', nw)
    nova = nw.get('local') or 'B1-C'
    dv_area(ps, '50'); dv_area(nova, '40'); pa = painel()
    chk(f'{tag}: 50 + 40 ha: selo "Excede em 10 ha" (antes "Área conferida")', 'Excede em 10 ha' in pa and 'Área conferida' not in pa, pa[:300])
    botao('Salvar', PAINEL); time.sleep(.3); al = alerta(); e = erros_dv()
    chk(f'{tag}: dividir em 50 + 40 ha (café 40 + 90 = 130 > 120) recusado com a mensagem agregada: café, soma das parcelas e máximo 80 ha; nada gravado',
        'A divisão travaria a área: ' in al and '40 ha de B1 estão com Café (%s, Café BV 2026/27). As parcelas somam 90 ha; o máximo é 80 ha nesse período. Nada foi gravado.' % pc in al
        and [x['v'].get('area') for x in soja(n1)] == [80], (al, soja(n1)))
    chk(f'{tag}: na parcela, "Reduza a área… máximo 80 ha", sem o "Máximo 0 ha" de cada parcela contra a irmã',
        'Máximo 0 ha' not in al and any('Reduza a área: as parcelas somam 90 ha e o máximo é 80 ha.' == (v or {}).get('area') for v in e.values()), (al, e))
    # revisão do lote SAF (S3): depois da recusa, corrigir só uma parcela tira a recusa vencida; o verde nunca fica ao lado de "travaria"/"Reduza a área"
    dv_area(ps, '40'); time.sleep(.2); pa = painel(); al2 = alerta(); e2 = erros_dv()
    venc = 'travaria' in al2 or 'Reduza a área' in pa or any('Reduza a área' in ((v or {}).get('area') or '') for v in e2.values())
    chk(f'{tag}: depois da recusa, mudar só {ps} para 40 (40 + 40 = 80) tira a recusa vencida e só então mostra "Área conferida"',
        not venc and 'Área conferida' in pa, (pa[:300], al2, e2))
    dv_area(ps, '50'); time.sleep(.2)
    botao('Distribuir área igualmente', PAINEL); time.sleep(.3); d = dv() or {'rows': []}; pa = painel()
    chk(f'{tag}: "Distribuir área igualmente" reparte os 80 ha que cabem (40 + 40), com "Área conferida" (antes 60 + 60)',
        sorted(r.get('area') for r in d['rows']) == ['40', '40'] and 'Área conferida' in pa, (d['rows'], pa[:300]))
    dv_area(ps, '50'); dv_area(nova, '30'); botao('Salvar', PAINEL); time.sleep(.4); t = toast(); s2 = sorted(x['v'].get('area') for x in soja(n1))
    chk(f'{tag}: dividir em 50 + 30 ha (soma = 120 ha) grava', 'B1 dividido em 2 parcelas' in t and s2 == [30, 50], (alerta(), t, s2))
    chk(f'{tag}: o aviso do Dividir não anuncia área livre (o café ocupa os 40 ha; antes "40 ha livres")', 'ha livres' not in t, t)
    # ---------- tabela com dado antigo (injetado, como o S3.4 do saf_revisao_test): Situação, motivo, nota e faixa mostram o excesso ----------
    c.js(f"""(()=>{{const s=window.__safSelf; const g=Object.assign({{}},s.state.g2['{G}']); const rs=JSON.parse(JSON.stringify(g.rows));
      const fx=(r)=>{{ if(r.v&&r.v.saf==={json.dumps(n1)}&&r.v.cult==='Soja'&&Number(r.v.area)===50) r.v.area=60; (r.kids||[]).forEach(fx); }}; rs.forEach(fx);
      g.rows=rs; s.setState({{g2:Object.assign({{}},s.state.g2,{{'{G}':g}})}}); return 'ok';}})()"""); time.sleep(1.0)
    b1 = linha('B1') or {}; fx_ = faixa(); n = nota()
    chk(f'{tag}: dado antigo (soja 60 + 30 ha + café 40 = 130 ha): B1 em Sobreposição, motivo "somam 130 ha"',
        b1.get('SITUAÇÃO') in ('Sobreposição', 'Sobrepor') and 'somam 130 ha' in (b1.get('_dica') or ''), b1)
    chk(f'{tag}: faixa mostra o excesso: "· de 120 ha · 10 ha em sobreposição"', '· de 120 ha · 10 ha em sobreposição' in fx_, fx_)
    chk(f'{tag}: nota "Sobreposição em B1: … somam 130 ha …" com "Corrigir B1"', n.startswith('Sobreposição em B1: ') and 'somam 130 ha' in n and 'Corrigir B1' in n, n)
    chk(f'{tag}: sem rolagem lateral da página', not c.js("document.documentElement.scrollWidth>innerWidth+1"))
    c.shot(os.path.join(PROBE, f'saf_c01_{w}.png'))
    chk(f'{tag}: sem erro de JS', erros() == '', erros())
def fluxo_adendo(w, h, toque):
    """Roteiro do ADENDO do Codex (comentário 6079770308), só com botões e campos: C1 (38 ha) com café de 2019 reduzido a 20 ha; safra 2028."""
    tag = TAG[0] = f'{w}×{h} adendo'
    abre('#saf=S2627&passo=cultivos', w, h, toque)
    clica_linha('c9'); fset('g_cult_S2627', 'area', '20'); salvar()
    n1 = cria_safra('Contraprova perene 2028', '2028-01-01', '2028-12-31', 'Santa Rita')
    na_linha('C1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('plantio', '2028-06-01'), ('area', '30'), ('local', 'C1-B'), ('meta', '60')): fset(G, k, v)
    cp = campos(G)
    chk(f'{tag}: com 30 ha a pista do plantio aponta a área ("reduza a área: máximo 18 ha"), não "sem janela antes do fim da safra"',
        cp.get('pmin_txt') == 'reduza a área: máximo 18 ha', cp)
    salvar(); al = alerta()
    chk(f'{tag}: 30 ha recusado com o limite de 18 ha; painel aberto; nada gravado',
        'De 12/05/2028 a 27/09/2028, 20 ha de C1 estão com Café (C1-A, Safra 2026/27). Máximo 18 ha nesse período.' in al and painel() != '' and not de(n1, 'Soja'), (al, de(n1, 'Soja')))
    fset(G, 'area', '18'); salvar(); t = toast(); s = de(n1, 'Soja')
    chk(f'{tag}: 18 ha grava; o aviso diz "0 ha livres em C1" (a tabela mostra Área livre "—"; antes "20 ha livres")',
        len(s) == 1 and s[0]['v'].get('area') == 18 and '· 0 ha livres em C1' in t, (alerta(), t, s))
    chk(f'{tag}: sem erro de JS', erros() == '', erros())
def fluxo_perene_antes(w, h, toque):
    """Perene numa safra antiga com anual futura no talhão: soja 90 ha no B1 (BV 2027) e, depois, café 30 ha numa safra de 2020."""
    tag = TAG[0] = f'{w}×{h} perene antes'
    abre('#saf=S2627&passo=safra', w, h, toque)
    n27 = cria_safra('BV 2027 primeiro', '2027-01-01', '2027-12-31', 'Boa Vista'); planejar_soja('90'); sj = soja(n27)
    pj = sj[0]['v'].get('local') if sj else '?'
    n20 = cria_safra('Café 2020 depois', '2020-01-01', '2020-12-31', 'Boa Vista'); na_linha('B1', 'Planejar ›')
    for k, v in (('cult', 'Café'), ('var', 'Catuaí 144'), ('plano', ''), ('area', '30'), ('plantio', '2020-01-01'), ('meta', '38'), ('local', pj)): fset(G, k, v)
    salvar(); al = alerta()
    chk(f'{tag}: café 30 ha digitado em {pj} (a parcela da soja de 2027) é recusado com a saída "use outra parcela", sem mandar replanejar a soja',
        'O café é perene e não libera %s: use outra parcela (ex.: B1-B).' % pj in al and 'replaneje' not in al and not de(n20, 'Café'), (al, de(n20, 'Café')))
    fset(G, 'local', 'B1'); salvar(); t = toast(); cf = de(n20, 'Café')
    chk(f'{tag}: sem digitar a parcela, a sugerida não é a da soja ({pj}): grava em B1-B (30 + 90 = 120 ha)',
        len(cf) == 1 and cf[0]['v'].get('local') == 'B1-B' and 'Cultivo incluído como parcela B1-B' in t, (alerta(), t, cf))
    chk(f'{tag}: sem erro de JS', erros() == '', erros())
try:
    c = L.c = Chrome()
    cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
    for w, h, toque in ((1440, 900, False),) * (MODO in ('desktop', 'tudo')) + ((390, 844, True),) * (MODO in ('celular', 'tudo')):
        fluxo_gravar_editar(w, h, toque); fluxo_dividir(w, h, toque); fluxo_adendo(w, h, toque); fluxo_perene_antes(w, h, toque)
finally:
    try:
        if L.c: L.c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
