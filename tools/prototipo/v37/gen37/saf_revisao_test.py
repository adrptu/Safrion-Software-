# -*- coding: utf-8 -*-
"""Teste de navegador · Planejar safra, correções da revisão adversarial de 06/10/2026 (papel do Codex; S1, S2.1, S2.2, S3.1–S3.8, S4).
Cada caso reproduz o passo do achado (rev_probe2…10 do revisor) e confere o comportamento corrigido. As safras novas são criadas no
MESMO estado, sem recarregar a página: é o caso do R-22 que o ocupacao_test não cobria (o mutante E1 sobrevivia). Também cobre PlantioMin
no painel (E4), unidade da meta ao gravar (E5), etiqueta do calendário (B10), chip de falta de recurso (B11) e ocorrência pendente sem
horas (B15). Emulação no Chrome headless a 1440 × 900: não é aparelho físico.
Uso: python3 saf_revisao_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, cv_todas_sempre
import dados2 as D2
import saf_nav_lib as L
from saf_nav_lib import *   # chk, rows, nivel0, faixa, toast, nota, painel, campos, fset, botao, salvar, na_linha, clica_linha, abre, estado, linha…
PAINEL = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)||document"
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def fm(gid): return c.js(f"(()=>{{const g=window.__safSelf.state.g2['{gid}']; return g&&g.fm?JSON.parse(JSON.stringify({{rid:g.fm.rid,draft:g.fm.draft}})):null;}})()")
def editaveis(): return c.js("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>x.offsetParent&&!x.readOnly&&!x.disabled).map(x=>x.id.replace(/^fx_g_cult_[A-Z0-9]+_/,''))") or []
def cancela():
    botao('Cancelar', PAINEL)
    if 'Há alterações' in painel(): botao('Descartar alterações')
def saf_atual(): return c.js("window.__safSelf.state.saf")
def dv(): return c.js("JSON.parse(JSON.stringify(window.__safSelf.state.dv||null))")
def dv_muda(i, **kw): c.js(f"(()=>{{const s=window.__safSelf; const d=s.state.dv; const rs=d.rows.map(x=>Object.assign({{}},x)); Object.assign(rs[{i}],{json.dumps(kw)}); s.setState({{dv:Object.assign({{}},d,{{rows:rs}})}}); }})()"); time.sleep(.4)
def veredito(): return c.js(f"(()=>{{const e=document.querySelector('#saf-v3-ver [role=status]'); return e?{N}(e.innerText):'';}})()") or ''
GRADE = r"""((h0)=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const hn=h=>n(h.innerText).replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase();
  const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&(()=>{ const h=t.querySelector('[role=columnheader]'); return h&&hn(h).indexOf(h0)===0; })()); if(!t) return null;
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(hn);
  return {hs, rows:[...t.querySelectorAll('[role=row]')].slice(1).map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; const o={_id:r.getAttribute('data-rid'),_kid:r.classList.contains('g2kid')};
    cs.forEach((c,i)=>{ let x=c.innerText; c.querySelectorAll('.g2sr').forEach(e=>{ x=x.replace(e.innerText,''); }); o[hs[i]||('C'+i)]=n(x).replace(/^[▾▸] ?/,''); }); return o; })}; })"""
def grade(h0): return c.js(f"({GRADE})({json.dumps(h0)})") or {'hs': [], 'rows': []}
try:
    c = L.c = Chrome()
    cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
    # ================= S2.1, S1 e E1: duas safras novas no mesmo estado =================
    abre('#saf=S2627&passo=safra')
    n1 = cria_safra('Safra 2027/28', '2027-09-01', '2028-08-31')
    na_linha('T1', 'Planejar ›'); g = 'g_cult_NOVA'
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('plantio', '2027-10-15'), ('meta', '60')): fset(g, k, v)
    salvar(); t = toast()
    chk('S2.1 N1 (Safra 2027/28): soja no T1 inteiro', 'Cultivo incluído: T1 inteiro' in t, (alerta(), t))
    n2 = cria_safra('Safrinha 2028', '2028-02-01', '2028-07-31'); t1 = linha('T1') or {}
    chk('S2.1 N2 (Safrinha 2028) no mesmo estado: T1 Livre 312 ha depois da soja da N1', n2 != n1 and (t1.get('SITUAÇÃO'), t1.get('ÁREA LIVRE')) == ('Livre', '312 ha'), (n1, n2, t1))
    na_linha('T1', 'Planejar ›')
    for k, v in (('cult', 'Milho'), ('var', 'AG 8700'), ('plano', 'MILHO-SF'), ('meta', '170')): fset(g, k, v)
    salvar(); t = toast(); al = alerta()
    chk('S2.1 N2: Planejar T1 com os padrões grava (nunca "Já existe T1 nesta safra", que vinha do T1 da N1)', 'Cultivo incluído: T1 inteiro' in t and 'Já existe' not in al, (al, t))
    nv = folhas(g); por = sorted((x['v'].get('saf'), x['v'].get('local'), x['v'].get('area')) for x in nv)
    chk('S2.1/R-22 g_cult_NOVA com um T1 de 312 ha em cada safra nova', por == sorted([(n1, 'T1', 312), (n2, 'T1', 312)]), por)
    chk('E5 meta gravada na unidade de mercado do Milho: "170 sc/ha"', (linha('T1') or {}).get('META') == '170 sc/ha', linha('T1'))
    # ================= S1: Dividir numa safra nova não puxa nem move o cultivo da outra (cenário do rev_probe2) =================
    abre('#saf=S2627&passo=safra')
    n1 = cria_safra('N1 2027/28', '2027-09-01', '2028-08-31'); na_linha('T1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('area', '150'), ('local', 'T1-A'), ('meta', '60')): fset(g, k, v)
    salvar(); t = toast()
    n2 = cria_safra('N2 2028/29', '2028-09-01', '2029-08-31'); na_linha('T1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('meta', '60')): fset(g, k, v)
    salvar(); t2 = toast()
    chk('S1 preparo: N1 com T1-A (150 ha) e N2 com T1 inteiro, no mesmo estado', 'parcela T1-A' in t and 'Cultivo incluído: T1 inteiro' in t2, (t, t2))
    ids_n1 = [x['id'] for x in folhas(g) if x['v'].get('saf') == n1]
    na_linha('T1', 'Dividir'); d = dv() or {'rows': []}
    chk('S1 Dividir T1 na N2 abre só o cultivo da N2 (o T1-A da N1 não entra no painel)', len(d['rows']) == 2 and ids_n1 and not any(r.get('id') in ids_n1 for r in d['rows']), [(r.get('id'), r.get('local'), r.get('area')) for r in d['rows']])
    botao('Salvar', PAINEL); time.sleep(.4); t = toast()
    nv = folhas(g); por = sorted((x['v'].get('saf'), x['v'].get('local'), x['v'].get('area')) for x in nv)
    chk('S1 depois de dividir: o T1-A da N1 continua na N1 (150 ha) e a N2 tem T1-A e T1-B', 'dividido em 2 parcelas' in t and por == sorted([(n1, 'T1-A', 150), (n2, 'T1-A', 156), (n2, 'T1-B', 156)]), (t, por))
    st = estado(g) or []; ids = [r['id'] for r in st]
    chk('S1 estado da g_cult_NOVA sem id de grupo repetido (um grupo por safra e talhão)', len(ids) == len(set(ids)), ids)
    vai_safra(n1)
    chk('S1 N1 intacta: "Nesta safra 150" e o T1-A dela na tabela', faixa().startswith('Nesta safra 150') and any(r.get('TALHÃO OU PARCELA') == 'T1-A' and r.get('ÁREA') == '150 ha' for r in rows()), (faixa(), [(r.get('TALHÃO OU PARCELA'), r.get('ÁREA')) for r in rows()][:4]))
    # ================= S2.2: o nome checado é o nome gravado =================
    abre('#saf=S27SF&passo=cultivos'); na_linha('T1', 'Planejar ›'); g = 'g_cult_S27SF'
    pm = campos(g).get('pmin_txt')
    chk('E4/OC-21 painel mostra o plantio mínimo: "Plantio a partir de 21/02/2027 com este plano"', pm == '21/02/2027 com este plano' and 'Plantio a partir de' in painel(), pm)
    for k, v in (('cult', 'Soja'), ('var', '62 X'), ('plano', 'SOJA-AT'), ('area', '152'), ('local', 'T1'), ('plantio', '2027-02-10'), ('meta', '60')): fset(g, k, v)
    salvar(); al = alerta()
    chk('S2.2 Parcela "T1" com área parcial não contorna a trava: recusa M2 com o nome que seria gravado (T1-B), nada gravado',
        'T1-B está com Soja 62 X da Safra 2026/27' in al and 'ocupa a área até pelo menos' in al and faixa() == FX27SF, (al, faixa()))
    abre('#saf=S27SF&passo=cultivos'); na_linha('T1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '62 X'), ('plano', 'SOJA-AT'), ('area', '152'), ('local', ''), ('plantio', '2027-02-21'), ('meta', '60')): fset(g, k, v)
    salvar(); t = toast(); al = alerta()
    chk('S2.2 Parcela vazia em 21/02/2027 (o PlantioMin): grava como T1-B, sem recusa falsa citando o Milho de T1-A', 'Cultivo incluído como parcela T1-B' in t and al == '(painel fechado)', (al, t))
    # ================= S3.4 e S4: sobreposição (estado antigo injetado) =================
    abre('#saf=S27SF&passo=cultivos'); clica_linha('d2'); salvar(); time.sleep(.3)   # grava sem mudar: o estado da grade passa a existir
    c.js("""(()=>{const s=window.__safSelf; const g=Object.assign({},s.state.g2['g_cult_S27SF']); const rs=JSON.parse(JSON.stringify(g.rows));
      rs.push({id:'x9',v:{talhao:'T1',faz:'Santa Rita',local:'T1-B',tipo:'Parcela',cult:'Soja',var:'62 X',area:152,plantio:'2027-02-10',meta:60,unm:'sc/ha',plano:'SOJA-AT',colheita:''},s:{},p:{}});
      g.rows=rs; s.setState({g2:Object.assign({},s.state.g2,{g_cult_S27SF:g})}); return 'ok';})()"""); time.sleep(1.0)
    n = nota()
    chk('S4 nota da sobreposição sem o rótulo repetido ("Sobreposição em T1: Soja (T1-B, Safra 2026/27) × Soja (T1-B, Safrinha 2027) em 10/02/2027")',
        n.startswith('Sobreposição em T1: Soja (T1-B, Safra 2026/27) × Soja (T1-B, Safrinha 2027) em 10/02/2027.') and 'Sobreposição: ' not in n, n)
    botao('Corrigir T1'); f = fm(g) or {}
    chk('S3.4 "Corrigir T1" abre o cultivo da trava (x9, T1-B), não o d1 (T1-A, fora do conflito)', f.get('rid') == 'x9', f)
    # ================= S3.3: "Informar colheita" só onde o painel tem o campo =================
    abre('#saf=S2627&passo=cultivos'); clica_linha('c1'); fset('g_cult_S2627', 'plantio', '2026-10-30'); salvar(); time.sleep(.3)
    c.js("location.hash='#saf=S27SF&passo=cultivos'"); time.sleep(1.3); lk = links_nota()
    chk('S3.3 c1 tem plano: o atalho é "Ver T1-A na Safra 2026/27 ›" (nunca "Informar colheita", sem campo no painel)', 'Ver T1-A na Safra 2026/27 ›' in lk and not any(x.startswith('Informar colheita de T1-A') for x in lk), lk)
    chk('S3.3 sem plano continua "Informar colheita" (T3 da Safra 2026/27)', 'Informar colheita de T3 na Safra 2026/27 ›' in lk, lk)
    clica_link('Ver T1-A na Safra 2026/27 ›'); time.sleep(1.6); f = fm('g_cult_S2627') or {}
    chk('S3.3 o atalho abre o c1 na Safra 2026/27', saf_atual() == 'S2627' and f.get('rid') == 'c1', (saf_atual(), f.get('rid')))
    # ================= S3.5: o mesmo atalho no 2º toque =================
    abre('#saf=S27SF&passo=cultivos'); clica_link('Informar colheita de T3 na Safra 2026/27 ›'); time.sleep(1.6)
    p1 = (saf_atual(), painel()[:20]); cancela(); time.sleep(.3)
    vai_safra('S27SF'); h = c.js("location.hash")
    clica_link('Informar colheita de T3 na Safra 2026/27 ›'); time.sleep(1.6); p2 = (saf_atual(), painel()[:20])
    chk('S3.5 2º toque no mesmo atalho (endereço igual) abre de novo a S2627 com o painel do T3', p1 == p2 == ('S2627', 'Cultivo · T3 × Santa') and 'cult=c5' in h, (p1, p2, h))
    # ================= S3.6, E5 e S3.2: safra nova sem cultivo; ciclo vinculado travado =================
    abre('#saf=S2627&passo=safra'); n3 = cria_safra('Safra 2028/29', '2028-09-01', '2029-08-31'); g = 'g_cult_NOVA'
    na_linha('T1', 'Planejar ›')
    sel = c.js("(()=>{const e=document.getElementById('fx_g_cult_NOVA_cult'); return e?[e.value,e.selectedIndex>=0?e.options[e.selectedIndex].text:'']:null;})()")
    chk('S3.6 1º Planejar de safra sem cultivo: Cultura mostra "Escolha a cultura", como o rascunho (vazio)', sel == ['', 'Escolha a cultura'] and (fm(g) or {}).get('draft', {}).get('cult') == '', sel)
    chk('S3.6 Ocupação prevista "—" enquanto não há cultura', campos(g).get('ocup_txt') == '—', campos(g).get('ocup_txt'))
    fset(g, 'var', 'Formosa'); fset(g, 'meta', '45'); salvar(); al = alerta()
    chk('S3.6 Salvar sem cultura pede a cultura, e o que se vê bate com o motivo', 'Informe cultura' in al, al)
    fset(g, 'cult', 'Mamão Formosa'); fset(g, 'plano', ''); fset(g, 'var', 'Formosa'); fset(g, 'area', '100'); fset(g, 'meta', '45'); salvar(); t = toast()
    m = [r.get('META') for r in rows() if (r.get('TALHÃO OU PARCELA') or '').startswith('T1-')]
    chk('E5 meta do Mamão gravada na unidade de mercado: "45 t/ha/ano"', 'Cultivo incluído como parcela' in t and m == ['45 t/ha/ano'], (t, m))
    na_linha('C1', 'Vincular ciclo ›'); fset(g, 'meta', '38'); salvar(); t = toast()
    cid = next((x['id'] for x in folhas(g) if x['v'].get('ciclo') == 'c9'), None)
    chk('S3.2 C1 vinculado sem "Dividir" na linha', 'Ciclo vinculado' in t and cid and 'Dividir' not in (linha('C1') or {}).get('TALHÃO OU PARCELA', 'Dividir'), (t, linha('C1')))
    fx0 = faixa(); clica_linha(cid); ed = editaveis()
    chk('S3.2 ao editar o vinculado, cultura, variedade, plantio, área e parcela ficam só leitura; meta e plano seguem editáveis',
        not any(k in ed for k in ('cult', 'var', 'plantio', 'area', 'local')) and 'meta' in ed and 'plano' in ed, ed)
    for k, v in (('area', '20'), ('plantio', '2027-10-01'), ('meta', '40')): fset(g, k, v)
    salvar(); x = next((x for x in folhas(g) if x['id'] == cid), {'v': {}})
    chk('S3.2 salvar não muda área, plantio nem cultura do ciclo (só a meta)', (x['v'].get('area'), x['v'].get('plantio'), x['v'].get('cult'), x['v'].get('meta')) == (38, '2019-01-15', 'Café', 40) and faixa() == fx0, (x['v'], faixa(), fx0))
    # ================= S3.7: unidade da meta no Dividir =================
    abre('#saf=S27SF&passo=cultivos'); na_linha('T2', 'Dividir')
    chk('S3.7 Dividir sem seletor de unidade da meta', c.js("document.querySelectorAll('aside[role=dialog] select[aria-label^=\"Unidade da meta\"]').length") == 0)
    dv_muda(1, cult='Mamão Formosa', var='Formosa', plano='', meta='45')
    un = c.js("[...document.querySelectorAll('aside[role=dialog] [data-un=meta]')].map(e=>e.innerText.trim())")
    chk('S3.7 a unidade segue a cultura da linha: sc/ha (Milho) e t/ha/ano (Mamão Formosa)', un == ['sc/ha', 't/ha/ano'], un)
    botao('Salvar', PAINEL); time.sleep(.4)
    t2 = [(x['v'].get('local'), x['v'].get('cult'), x['v'].get('unm')) for x in folhas('g_cult_S27SF') if x['v'].get('talhao') == 'T2']
    chk('S3.7 gravado com a unidade de mercado de cada cultura', sorted(t2) == [('T2-A', 'Milho', 'sc/ha'), ('T2-B', 'Mamão Formosa', 't/ha/ano')], t2)
    # ================= S3.8 (13/10/2026): sem caixas de seleção nos cultivos, nem "Selecionar as N linhas visíveis" =================
    abre('#saf=S27SF&passo=cultivos')
    sx = c.js("(()=>({cx:document.querySelectorAll('[role=table] input[type=checkbox]').length, todas:[...document.querySelectorAll('[role=columnheader] button')].some(b=>/^Selecionar as|^Desmarcar/.test(b.getAttribute('aria-label')||''))}))()")
    chk('S3.8 sem caixas de seleção nem "Selecionar as N linhas visíveis" na grade de cultivos (pedido do proprietário, 13/10)', sx == {'cx': 0, 'todas': False}, sx)
    # ================= S3.1 e B10: ocorrência depois do fim fora da capacidade =================
    abre('#saf=S27SF&passo=cultivos'); clica_linha('d3'); fset('g_cult_S27SF', 'plantio', '2027-05-20'); salvar(); time.sleep(.3)
    c.js("window.__safSelf.setState({step:3})"); time.sleep(1.2); v = veredito()
    chk('S3.1 veredito: "Fora da conta: 2 ocorrências depois do fim da safra", sem falta em ago/27', 'Fora da conta: 2 ocorrências depois do fim da safra' in v and 'ago/27' not in v, v)
    ago = c.js("(()=>{const e=window.__safSelf.__e3; return Object.values(e.G).map(g=>[g.id,g.cells[11].dThis]);})()")
    chk('S3.1 nenhuma hora desta safra em ago/27 (Colhedoras e Operadores somavam 19 h e 42,4 h)', all(h == 0 for _, h in ago), ago)
    botao('Capacidade por mês ▾'); K = grade('RECURSO')
    chk('S3.1 g_cap da S27SF com os meses do período (fev/27 a jul/27), sem ago/27', K['hs'][3:] == ['FEV/27', 'MAR/27', 'ABR/27', 'MAI/27', 'JUN/27', 'JUL/27'], K['hs'])
    c.js("(()=>{const r=document.querySelector('[role=row][data-rid=\"op:Colheita de grãos\"] .g2car'); if(r&&r.getAttribute('aria-expanded')!=='true') r.click();})()"); time.sleep(.5)
    sits = [r.get('SITUAÇÃO', '') for r in grade('OPERAÇÃO')['rows']]
    chk('B10 g_op: etiqueta "depois do fim da safra" na colheita do P1', any('depois do fim da safra' in s for s in sits), sits)
    # safra nova com período parcial no calendário: a g_cap_NOVA mostra só os meses dela (capMeses), não os 12
    abre('#saf=S2627&passo=safra'); cria_safra('Safrinha BV 2027', '2027-03-01', '2027-08-31', 'Boa Vista'); na_linha('B1', 'Planejar ›')
    for k, v in (('cult', 'Soja'), ('var', '58 W'), ('plano', 'SOJA-AT'), ('meta', '60')): fset('g_cult_NOVA', k, v)
    salvar(); c.js("window.__safSelf.setState({step:3})"); time.sleep(1.2); botao('Capacidade por mês ▾'); K = grade('RECURSO')
    chk('S3.1 g_cap de safra nova (mar/27 a ago/27) com os meses do período, pelos dados', K['hs'][3:] == ['MAR/27', 'ABR/27', 'MAI/27', 'JUN/27', 'JUL/27', 'AGO/27'] and len(K['rows']) == 6, (K['hs'], len(K['rows'])))
    # ================= E3 (R-16): o lote não aplica o plano em quem trava =================
    abre('#saf=S27SF&passo=cultivos'); na_linha('T3', 'Planejar ›'); g = 'g_cult_S27SF'
    for k, v in (('cult', 'Milho'), ('var', 'AG 8700'), ('plano', ''), ('plantio', '2027-02-05'), ('meta', '170')): fset(g, k, v)
    salvar(); t = toast(); mid = next((x['id'] for x in folhas(g) if x['v'].get('local') == 'T3' and x['v'].get('cult') == 'Milho'), None)
    chk('E3 preparo: milho sem plano no T3 em 05/02/2027 grava (previsão não trava)', 'Cultivo incluído: T3 inteiro' in t and mid, (alerta(), t))
    botao('Aplicar plano', f"document.querySelector('[role=row][data-rid=\\'{mid}\\']')"); time.sleep(.3)   # sem caixas de seleção (13/10): o botão da linha
    c.js("(()=>{const e=document.getElementById('ap_sel'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,'MILHO-SF'); e.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
    pn = painel()
    chk('E3 prévia do lote: com o plano, o T3 trava (núcleo da soja até 10/02/2027) e "não recebe"; botão conta 0', 'não recebe' in pn and 'Aplicar plano em 0 cultivos' in pn, pn[:500])
    botao('Aplicar plano em 0 cultivos'); pn = painel(); x = next((x for x in folhas(g) if x['id'] == mid), {'v': {}})
    chk('E3 aplicar recusa ("Nenhum cultivo pode receber") e o cultivo continua sem plano', 'Nenhum cultivo pode receber este plano' in pn and not x['v'].get('plano'), (pn[:300], x['v'].get('plano')))
    # ================= B1: Custo R$/ha divide pela área atendida (com área sem conjunto) =================
    abre('#saf=S2627&passo=operacoes')
    c.js("(()=>{const r=document.querySelector('[role=row][data-rid=\"op:Colheita de grãos\"]'); const x=r&&[...r.querySelectorAll('[role=cell]')].find(z=>!z.querySelector('input,button')&&z.innerText.trim()&&!z.classList.contains('g2nr')&&!z.classList.contains('g2c0')); if(x) x.click();})()"); time.sleep(.6)
    fset('g_rend_S2627', 'esc', 'Só esta atividade'); fset('g_rend_S2627', 'jan', '50'); botao('Salvar', PAINEL); time.sleep(.6)
    oc = [o for o in D2.ocorr_op('S2627', None, {('Colheita de grãos', 'Colheita', 'r5'): dict(jan=50)}) if o['a']['op'] == 'Colheita de grãos']
    at = sum(o['rp']['alocado'] for o in oc); cop = sum(o['cop'] for o in oc); sal = sum(o['rp']['saldo'] for o in oc)
    esp = 'R$ ' + f'{cop / at:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + '/ha-op'
    cg = next((r for r in grade('OPERAÇÃO')['rows'] if r.get('OPERAÇÃO › ATIVIDADE › TALHÃO', '').startswith('Colheita de grãos')), {})
    chk('B1 janela 50 h na Colheita: 48 ha sem conjunto e Custo R$/ha = custo ÷ área atendida (%s, nunca ÷ 610 ha)' % esp, round(sal, 2) == 48 and cg.get('CUSTO R$/HA') == esp and '48 ha sem conjunto' in cg.get('SITUAÇÃO', ''), (sal, cg))
    # ================= B11 e B15: LG2627 (falta de recurso e ocorrências pendentes) =================
    abre('#saf=LG2627&passo=operacoes'); time.sleep(.4); R = grade('OPERAÇÃO')['rows']
    chk('B11 g_op LG2627: chip de falta de recurso na operação ("Operadores e equipe … %")', any('Operadores e equipe' in r.get('SITUAÇÃO', '') and '%' in r.get('SITUAÇÃO', '') for r in R), [r.get('SITUAÇÃO') for r in R][:6])
    hk = next((k for k in (R[0] if R else {}) if k.startswith('HORAS')), 'HORAS')
    pend = [r for r in R if r['_kid'] and 'pendente' in r.get('SITUAÇÃO', '') and ' · ' in r.get('OPERAÇÃO › ATIVIDADE › TALHÃO', '')]
    chk('B15 ocorrência pendente (sem alocação) não mostra horas', pend and all(r.get(hk) == '' for r in pend), [(r.get('OPERAÇÃO › ATIVIDADE › TALHÃO'), r.get('SITUAÇÃO'), r.get(hk)) for r in pend[:3]])
    chk('sem erro de JS', erros() == '', erros())
finally:
    try:
        if L.c: L.c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
