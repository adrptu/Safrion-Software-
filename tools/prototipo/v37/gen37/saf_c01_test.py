# -*- coding: utf-8 -*-
"""Teste de navegador · SAF-C01 (Codex + Gemini, PR #47, comentário 6079770308): a trava de soma (R-14/T-soma) vale com uma perene antiga
no talhão. Tudo pela tela, sem injetar dado para a trava: cria a safra "Café antigo BV" (2020) e grava café 40 ha numa parcela do B1
(Boa Vista, 120 ha); cria a "Safra BV 2027" e tenta, com a soja de 2027:
  gravar 90 ha (café 40 + 90 = 130 > 120) → recusa com a mensagem da trava, nada gravado; o limite 80 ha (soma = 120) grava;
  editar a soja para 90 ha → recusa, a área gravada continua 80 ha;
  dividir o B1 em 50 + 40 ha (130 > 120) → recusa ("A divisão travaria a área"), nada gravado; 50 + 30 ha (120) grava.
Só a última parte injeta estado (dado antigo, como o S3.4 do saf_revisao_test): soja com 90 ha já gravada → Situação "Sobreposição",
motivo, nota e faixa "· 10 ha em sobreposição". Em 1440 × 900 e 390 × 844 (toque). Emulação no Chrome headless, não aparelho físico.
Uso: python3 saf_c01_test.py [desktop|celular|tudo]   (padrão: tudo)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome
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
    botao('+ Adicionar parcela', PAINEL); d = dv() or {'rows': []}; sug = d['rows'][-1]['local'] if len(d['rows']) > 1 else '?'
    # a parcela nova vem com o nome sugerido (nextNome não olha as outras safras: sugere a parcela do café, que a trava de faixa recusa);
    # aqui ela vai para B1-C, faixa livre, para a soma ser a única trava em jogo
    info(f'{tag}: nome sugerido para a parcela nova (a do café é {pc})', sug); nova = 'B1-C'; dv_nome(sug, nova)
    dv_area(ps, '50'); dv_area(nova, '40'); botao('Salvar', PAINEL); time.sleep(.3); al = alerta()
    chk(f'{tag}: dividir em 50 + 40 ha (café 40 + 90 = 130 > 120): "A divisão travaria a área… Nada foi gravado", com a mensagem da trava na parcela',
        'A divisão travaria a área: 2 parcelas com ocupação certa no período. Nada foi gravado.' in al and 'estão com Café (%s, Café BV 2026/27)' % pc in al
        and [x['v'].get('area') for x in soja(n1)] == [80], (al, soja(n1)))
    dv_area(nova, '30'); botao('Salvar', PAINEL); time.sleep(.4); t = toast(); s2 = sorted(x['v'].get('area') for x in soja(n1))
    chk(f'{tag}: dividir em 50 + 30 ha (soma = 120 ha) grava', 'B1 dividido em 2 parcelas' in t and s2 == [30, 50], (alerta(), t, s2))
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
try:
    c = L.c = Chrome()
    for w, h, toque in ((1440, 900, False),) * (MODO in ('desktop', 'tudo')) + ((390, 844, True),) * (MODO in ('celular', 'tudo')):
        fluxo_gravar_editar(w, h, toque); fluxo_dividir(w, h, toque)
finally:
    try:
        if L.c: L.c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
