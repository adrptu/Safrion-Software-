# -*- coding: utf-8 -*-
"""Teste de navegador · Planejar safra, etapa 3 "Dimensione operações e recursos" (ESPECIFICACAO etapa-unica-3-4-5 §9.2).
Endereços e faixa (N1–N7), operações (O1–O5, O8, O9, O11–O15), capacidade, veredito e layout (V1, V3, V4, V6, V8, V11–V13, L1, L2, L4),
recurso, resumo e aviso (P1, P2, P4, P7, P8). Números comparados com o espelho Python (dados2.ocorr_op, plano_op, capacidade, resumo_cultura)
ou com os oráculos do capacidade_unit.py. Fluxo normal, erro/recusa (janela em "Todas", pessoas fracionárias) e repetição (salvar sem
mudar). Emulação no Chrome headless: não é aparelho físico.
Uso: python3 saf_operacoes_test.py [desktop|celular|tudo]   (padrão: tudo)"""
import sys, os, time, json, re, subprocess, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, cv_todas_sempre
import dados2 as D2
MODO = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
OK, FAIL = [], []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else ' · ' + str(det)[:1200]), flush=True)
def info(t, v): print('     (medido) ' + t + ': ' + str(v)[:600], flush=True)
def fmt(x, d=0): s = f'{float(x):,.{d}f}'; return s.replace(',', 'X').replace('.', ',').replace('X', '.')
def nfa(x): s = fmt(round(float(x), 2), 2); return s.rstrip('0').rstrip(',')
def rs(x): return 'R$ ' + fmt(x, 2)
MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
def mlab(d): return MES[d.month - 1] + '/' + str(d.year)[2:]
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')); c = None
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
# linhas de uma grade visível (achada pelo 1º cabeçalho) como dicionários pelo cabeçalho; o triângulo sai do texto da 1ª célula
ROWS = r"""((h0)=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const hn=h=>n(h.innerText).replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase();
  const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&(()=>{ const h=t.querySelector('[role=columnheader]'); return h&&hn(h).indexOf(h0)===0; })()); if(!t) return null;
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(hn);
  return {hs, rows:[...t.querySelectorAll('[role=row]')].slice(1).map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; const o={_id:r.getAttribute('data-rid'),_kid:r.classList.contains('g2kid'),_tot:r.classList.contains('g2tot')};
    cs.forEach((c,i)=>{ let x=c.innerText; c.querySelectorAll('.g2sr').forEach(e=>{ x=x.replace(e.innerText,''); }); o[hs[i]||('C'+i)]=n(x).replace(/^[▾▸] ?/,''); }); return o; })}; })"""
def grade(h0): return c.js(f"({ROWS})({json.dumps(h0)})") or {'hs': [], 'rows': []}
def gop(): return grade('OPERAÇÃO')
def gcap(): return grade('RECURSO')
def op_linha(nome, rs=None):
    rs = rs if rs is not None else gop()['rows']
    return next((r for r in rs if r.get('OPERAÇÃO › ATIVIDADE › TALHÃO', '').startswith(nome)), None)
def toast(): return c.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def veredito(): return c.js(f"(()=>{{const e=document.querySelector('#saf-v3-ver [role=status]'); return e?{N}(e.innerText):'';}})()") or ''
def atalhos(): return c.js(f"[...document.querySelectorAll('[data-acao=atalho]')].filter(b=>b.offsetParent&&!b.closest('[data-acoes]')).map(b=>{N}(b.innerText))") or []
def filtro(): return c.js(f"(()=>{{const e=document.getElementById('saf-cap-filtro'); return e&&e.offsetParent?{N}(e.innerText):'';}})()") or ''
def custo(): return c.js(f"(()=>{{const b=document.querySelector('[data-acao=resumo]'); const s=b&&b.parentElement; return s?{N}(s.innerText):'';}})()") or ''
# barra limpa (15/10/2026): os atalhos ficam no "⋯ Mais ações" (fechado); a leitura junta os botões à vista e os itens do menu
def acoes(): return c.js(f"(()=>{{const a=document.querySelector('[data-acoes]'); return a?[...a.querySelectorAll('button,a')].filter(b=>b.offsetParent||b.closest('.acoes-menu')).map(b=>{N}(b.textContent)):[];}})()") or []
def painel(): return c.js(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?{N}(a.innerText):'';}})()") or ''
def erros(): return c.js("(window.__errs||[]).join(' | ')") or ''
def faixa_atual(): return c.js(f"(()=>{{const e=document.querySelector('.etp-ind [aria-current=step]'); return e?{N}(e.innerText):'';}})()") or ''
def etapa_n():
    t = faixa_atual(); m = re.match(r'(\d+)', t); return int(m.group(1)) if m else 0
def campos(gid):
    return c.js(f"Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].filter(x=>x.offsetParent&&x.id.indexOf('fx_{gid}_')===0).map(x=>[x.id.slice({len('fx_' + gid + '_')}),x.value]))") or {}
def fset(gid, k, val):
    r = c.js(f"""(()=>{{const e=document.getElementById('fx_{gid}_{k}'); if(!e) return 'sem campo {k}'; const pr=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(pr,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.3); return r
def botao(lab, raiz='document', inicio=False):
    r = c.js(f"""(()=>{{const R={raiz}; if(!R) return 'sem raiz'; const bs=[...R.querySelectorAll('button,a')].filter(b=>b.offsetParent); const n=s=>(s||'').replace(/\\s+/g,' ').trim();
      const b=bs.find(b=>n(b.innerText)==={json.dumps(lab)})||({json.dumps(inicio)}&&bs.find(b=>n(b.innerText).indexOf({json.dumps(lab)})===0)); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"""); time.sleep(.6); return r
def botao_cap():
    """abre "Capacidade por mês" se estiver fechada (TAB-11: a seta é o ícone que gira; fechada = aria-expanded=false, antes o texto "▸ Capacidade por mês")"""
    r = c.js("""(()=>{const b=[...document.querySelectorAll('button[aria-expanded=false]')].find(b=>b.offsetParent&&b.innerText.replace(/\\s+/g,' ').trim()==='Capacidade por mês'); if(!b) return 'sem botão'; b.click(); return 'ok';})()"""); time.sleep(.6); return r
PAINEL = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"
def salvar(): return botao('Salvar', PAINEL)
def fechar():   # fecha o painel aberto pelo botão (o Esc só chega ao painel com o foco dentro dele; ver P4 para o Esc)
    c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); if(!a) return; const bs=[...a.querySelectorAll('button')].filter(b=>b.offsetParent); const b=bs.find(b=>b.innerText.trim()==='Cancelar')||bs.find(b=>b.getAttribute('aria-label')==='Fechar')||bs.find(b=>b.innerText.trim()==='Fechar'); if(b) b.click();})()"); time.sleep(.4)
    c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); const b=a&&[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Descartar alterações'); if(b) b.click();})()"); time.sleep(.3)
def clica_rid(rid):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid={json.dumps(rid)}]'); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('[role=cell]')].find(z=>!z.querySelector('input,button')&&z.innerText.trim()&&!z.classList.contains('g2nr'))||r; x.click(); return 'ok';}})()"""); time.sleep(.6); return r
def cel_cap(rid, mes):
    """clica o botão da célula recurso × mês da g_cap (mes = 'fev/27')"""
    r = c.js(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/^RECURSO/i.test((t.querySelector('[role=columnheader]')||{{}}).innerText||'')); if(!t) return 'sem g_cap';
      const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').trim().toLowerCase()); const i=hs.indexOf({json.dumps(mes)}); const r=t.querySelector('[role=row][data-rid={json.dumps(rid)}]'); if(i<0||!r) return 'sem célula';
      const cel=r.querySelectorAll('[role=cell]')[i]; const b=cel&&cel.querySelector('button'); if(!b) return 'inerte'; b.click(); return 'ok';}})()"""); time.sleep(.7); return r
def expande(rid):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid={json.dumps(rid)}]'); const b=r&&r.querySelector('.g2car'); if(!b) return 'sem seta'; if(b.getAttribute('aria-expanded')!=='true') b.click(); return 'ok';}})()"""); time.sleep(.5); return r
def total_h(): t = next((r for r in gop()['rows'] if r['_tot']), None); return t and next((v for k, v in t.items() if k.startswith('HORAS')), None)
NAV = [0]
def abre(h, w=1440, hh=900, toque=False):
    NAV[0] += 1; c.aparelho(w, hh, 1, toque); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html?r={NAV[0]}{h}'); time.sleep(1.2)
def rec(**mod):
    rs_ = copy.deepcopy(D2.RECURSOS)
    for r in rs_:
        if r['id'] in mod: r.update(mod[r['id']])
    return rs_
# espelho: linha de operação da g_op (área ha-op, horas-conjunto, custo ÷ área atendida) e veredito/maior uso do capacidade_unit
def esp_op(safra, op, cfg=None):
    oc = [o for o in D2.ocorr_op(safra, None, cfg) if o['a']['op'] == op]
    area = sum(o['area'] for o in oc); h = sum(o['horas'] for o in oc); cop = sum(o['cop'] for o in oc); at = sum(o['rp']['alocado'] for o in oc)
    ds = sorted(o['dt'] for o in oc); fx = mlab(ds[0]) if mlab(ds[0]) == mlab(ds[-1]) else mlab(ds[0]) + ' – ' + mlab(ds[-1])
    return dict(area=nfa(area) + ' ha-op', horas=fmt(h, 1) + ' h', rha=rs(cop / at) + '/ha-op', data=fx)
VER = {'S2627': 'Na estimativa mensal, cabe nos 690 ha com plano. Fora da conta: T4, T3, P1 e P2 (475 ha), sem plano. Prazo por talhão não verificado: 17 de 17 atividades sem janela.',
       'S27SF': 'Na estimativa mensal, cabe com o que você tem. Prazo por talhão não verificado: 7 de 7 atividades sem janela.',
       'S2526': 'Capacidade não calculada: as 21 ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27).'}
try:
    c = Chrome()
    cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
    if MODO in ('desktop', 'tudo'):
        # ---------- N1–N4a, N6, N7: endereços, faixa e retomada ----------
        abre('#saf=S27SF&etapa=6'); chk('N1 etapa=6 abre a 4 "Confira a demanda de insumos"', etapa_n() == 4 and 'Confira a demanda de insumos' in faixa_atual(), faixa_atual())
        for e in (3, 4, 5):
            abre(f'#saf=S2627&etapa={e}'); chk(f'N2 etapa={e} abre a 3', etapa_n() == 3 and 'Dimensione operações e recursos' in faixa_atual(), faixa_atual())
        for h, n in (('passo=operacoes', 3), ('passo=demanda', 4), ('', 4)):
            abre('#saf=S2627' + ('&' + h if h else '')); chk(f'N3 {h or "só saf="} abre a {n}', etapa_n() == n, faixa_atual())
        abre('#saf=S2627&passo=cultivos'); c.js("location.hash='#saf=S2627&etapa=6'"); time.sleep(.8); e1 = etapa_n()
        c.js("location.hash='#saf=S2627&etapa=4'"); time.sleep(.8); e2 = etapa_n()
        chk('N4a hashchange: etapa=6 → 4 e etapa=4 → 3 (etapa=4 nunca abre a demanda)', (e1, e2) == (4, 3), (e1, e2))
        nf = c.js("document.querySelectorAll('.etp-ind .etp-itens > *').length") or c.js("[...document.querySelectorAll('.etp-ind [aria-current], .etp-ind li')].length")
        txt = c.js("document.body.innerText")
        chk('matriz 1: 4 etapas; sem "Definir rendimentos", "Conferir plano operacional" nem "Dimensionar recursos"', all(x not in txt for x in ('Definir rendimentos', 'Conferir plano operacional', 'Dimensionar recursos')) and 'Etapa 3 de 4' in (c.js("document.body.innerHTML") or '') or '4' in str(nf), nf)
        abre('#saf=S2627&passo=safra')
        bts = c.js(f"[...document.querySelectorAll('[role=row] button')].filter(b=>b.offsetParent&&/^Continuar|^Consultar/.test(b.innerText)).map(b=>{N}(b.innerText))") or []
        chk('N6 retomada (§5.4): S2627 aplicar plano em 4; S27SF enviar demanda; S2526 consultar', bts[:4] == ['Continuar: aplicar plano em 4 cultivos', 'Continuar: enviar demanda para cotação', 'Consultar safra', 'Continuar: enviar demanda para cotação'] or ('Continuar: enviar demanda para cotação' in bts and 'Continuar: aplicar plano em 4 cultivos' in bts), bts)
        r = c.js(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.innerText.indexOf('Safrinha 2027')>=0); const b=rs.length&&[...rs[0].querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText)); if(!b) return 'sem'; b.click(); return 'ok';}})()"""); time.sleep(.6)
        chk('N6 aviso do Continuar da S27SF sem número de etapa', 'Safra aberta: Safrinha 2027 · Demanda de insumos' in toast() and etapa_n() == 4, (toast(), etapa_n()))
        g1 = subprocess.run(['grep', '-nE', "['\"][^'\"]*[#&?]etapa=", 'safra.js', 'areas/processo_compras.py'], cwd=HERE, capture_output=True, text=True).stdout.strip()
        g2 = subprocess.run("grep -rnE \"Planejar safra[^'\\\"]{0,40}etapa [0-9]|Safra aberta: '[^;]*etapa \" safra.js dados2.py areas/*.py | grep -v '^[^:]*:[0-9]*: *#' | grep -v '// '", cwd=HERE, shell=True, capture_output=True, text=True).stdout.strip()
        chk('N7 guardas estáticos (§5.3) = 0', g1 == '' and g2 == '', (g1[:300], g2[:300]))
        # ---------- V1, O1, O2, O4: S2627 no topo e na g_op ----------
        abre('#saf=S2627&passo=operacoes', 1440, 1040)
        chk('V1 veredito S2627 (R4, âmbar)', veredito() == VER['S2627'], veredito())
        chk('V1 sem atalho fora da tabela (15/10, proprietário: avisos só dentro da tabela)', atalhos() == [], atalhos())
        pc = D2.plano_op('S2627'); chk('V1 custo de operação = espelho, "máquinas e pessoas, sem insumos"', custo().startswith('Custo de operação ' + rs(pc['cop']) + ' · máquinas e pessoas, sem insumos'), custo())
        G = gop()
        chk('O1 g_op: 9 colunas na ordem do §3.4 (Custo total no fim: proprietário, 13/10/2026)', G['hs'] == ['OPERAÇÃO › ATIVIDADE › TALHÃO', 'SITUAÇÃO', 'DATA', 'CONJUNTO', 'RENDIMENTO', 'ÁREA TRABALHADA', 'HORAS-CONJUNTO', 'CUSTO R$/HA', 'CUSTO TOTAL'], G['hs'])
        n0 = [r for r in G['rows'] if not r['_kid'] and not r['_tot']]
        OPS = ['Pulverização', 'Fertirrigação', 'Tratamento de sementes', 'Plantio', 'Adubação a lanço', 'Colheita de grãos', 'Colheita de café', 'Poda']
        chk('O1 operações na ordem da 1ª data (§2.1)', [r['OPERAÇÃO › ATIVIDADE › TALHÃO'].split(' ')[0] for r in n0] == [o.split(' ')[0] for o in OPS] and len(n0) == 8, [r['OPERAÇÃO › ATIVIDADE › TALHÃO'] for r in n0])
        pu = op_linha('Pulverização', n0); e = esp_op('S2627', 'Pulverização')
        chk('O2 Pulverização = espelho (data, conjunto, 21,60 ha/h, ha-op, horas, R$/ha-op)', pu and pu['DATA'] == e['data'] and pu['CONJUNTO'].startswith('Trator 02') and pu['RENDIMENTO'] == '21,60 ha/h' and pu['ÁREA TRABALHADA'] == e['area'] and pu['HORAS-CONJUNTO'] == e['horas'] and pu['CUSTO R$/HA'] == e['rha'], (pu, e))
        chk('O2 negativo: nenhuma operação com "ha" puro na área', all(r['ÁREA TRABALHADA'].endswith(' ha-op') for r in n0), [r['ÁREA TRABALHADA'] for r in n0])
        chk('O2 "6 atividades" na Pulverização', '6 atividades' in pu['OPERAÇÃO › ATIVIDADE › TALHÃO'], pu)
        chk('O4 S2627: 8 operações "Janela não informada", nenhum "Cabe na janela"; sem chips do filtro rápido', all(r['SITUAÇÃO'] == 'Janela não informada' for r in n0) and 'Cabe na janela' not in c.js("document.body.innerText") and not c.js("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"]')].some(g=>g.offsetParent)"), [r['SITUAÇÃO'] for r in n0])
        chk('Total da g_op só em horas-conjunto = espelho (561,8 h)', total_h() == fmt(pc['hconj'], 1) + ' h', total_h())
        chk('O18 negativo: "/ha da safra" não aparece', '/ha da safra' not in c.js("document.body.innerText"))
        ac = acoes(); chk('§5.2 área de ações: Aplicar plano em 4 cultivos, ‹ Cultivos e planos, ‹ Trocar safra (14/10: embaixo, no fluxo, com a seta de voltar), Conferir demanda de insumos ›', sorted(ac) == sorted(['Aplicar plano em 4 cultivos', '‹ Cultivos e planos', '‹ Trocar safra', 'Conferir demanda de insumos ›']), ac)
        # L1: as operações aparecem acima da área de ações (a página não rola)
        vis = c.js("""(()=>{ const a=document.querySelector('[data-acoes]'); const lim=a?a.getBoundingClientRect().top:innerHeight; const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/^OPERA/i.test(t.querySelector('[role=columnheader]').innerText));
          return [...t.querySelectorAll('[role=row]')].slice(1).filter(r=>{ const b=r.getBoundingClientRect(); return b.top>=0&&b.bottom<=lim+1; }).length; })()""")
        chk('L1 1440 × 1040: 8 operações e Total acima da área de ações', vis == 9, vis)
        # ---------- O3: Plantio, T2 (âncora) ----------
        expande('op:Plantio'); expande('at:Plantio|Plantio e adubação de base'); G = gop()
        t2 = next((r for r in G['rows'] if r['OPERAÇÃO › ATIVIDADE › TALHÃO'].startswith('T2 ')), None)
        if t2: expande(t2['_id']); G = gop()
        cfgs = [r for r in G['rows'] if r['_id'] and r['_id'].startswith(t2['_id'] + '|c')] if t2 else []
        o2 = next(o for o in D2.ocorr_op('S2627') if o['a']['op'] == 'Plantio' and o['c']['local'] == 'T2')
        chk('O3 Plantio T2: 2 configurações com a área atendida e o R$/ha de cada (espelho)', len(cfgs) == 2 and [x['ÁREA TRABALHADA'] for x in cfgs] == [nfa(x['q']) + ' ha' for x in o2['rp']['itens']] and [x['CUSTO R$/HA'] for x in cfgs] == [rs(x['custo'] / x['q']) + '/ha' for x in o2['rp']['itens']], ([(x['ÁREA TRABALHADA'], x['CUSTO R$/HA']) for x in cfgs], [(x['q'], x['custo']) for x in o2['rp']['itens']]))
        chk('O3 T2 horas = espelho (61,3 h) e Situação sem número', t2 and t2['HORAS-CONJUNTO'] == fmt(o2['horas'], 1) + ' h' and not re.search(r'\d', t2['SITUAÇÃO']), t2)
        clica_rid(t2['_id']); f = campos('g_rend_S2627')
        chk('O3 toque no talhão abre a configuração com "Neste talhão" (trio e decorrido)', 'Necessário: ' in f.get('neste_c', '') and 'Atendido: ' in f.get('neste_c', '') and 'h decorridas' in f.get('neste_c', ''), f.get('neste_c'))
        fechar()
        # ---------- O8, O13, O14, O11 (recusa), O9 (Todas nas atividades em uso) ----------
        clica_rid('op:Pulverização'); f = campos('g_rend_S2627')
        chk('O8 Pulverização: "Aplicar em" = Todas; sem Janela editável; janela por atividade "nenhuma das 6 com janela"', f.get('esc') == 'Todas as atividades da operação' and 'jan' not in f and 'nenhuma das 6 com janela' in f.get('jan_op', ''), f)
        chk('O13 Origem "Padrão do cadastro (CD-02)" e Custo R$/ha ao vivo', f.get('origem_c') == 'Padrão do cadastro (CD-02)' and f.get('custo_ha_c') == rs(313 / 21.6) + '/ha', (f.get('origem_c'), f.get('custo_ha_c')))
        fset('g_rend_S2627', 'vel', '12'); o1 = campos('g_rend_S2627').get('origem_c'); fset('g_rend_S2627', 'vel', '8'); o2_ = campos('g_rend_S2627').get('origem_c')
        chk('O13 ao vivo: velocidade 12 "Ajustado nesta safra", voltar a 8 "Padrão"', (o1, o2_) == ('Ajustado nesta safra', 'Padrão do cadastro (CD-02)'), (o1, o2_))
        fset('g_rend_S2627', 'pess', '2,5'); salvar(); pn = painel()
        chk('O14 "2,5" pessoas recusado e o digitado fica', 'Use um número inteiro de pessoas.' in pn and campos('g_rend_S2627').get('pess') == '2,5', pn[:300])
        fset('g_rend_S2627', 'pess', '1')
        # repetição: salvar sem mudar não muda horas nem capacidade
        salvar(); t = toast()
        chk('repetição: salvar sem mudar mantém horas e capacidade', 'Horas e capacidade não mudaram.' in t and total_h() == fmt(pc['hconj'], 1) + ' h', (t, total_h()))
        clica_rid('op:Pulverização'); fset('g_rend_S2627', 'vel', '12'); salvar(); time.sleep(.5); t = toast()
        cfg = {('Pulverização', '*', 'r1'): {'vel': 12}}; p9 = D2.plano_op('S2627', None, cfg)
        chk('O9 "Todas": aviso "(6 atividades)" e totais = espelho (horas-conjunto e custo)', '(6 atividades)' in t and total_h() == fmt(p9['hconj'], 1) + ' h' and custo().startswith('Custo de operação ' + rs(p9['cop'])), (t, total_h(), custo(), fmt(p9['hconj'], 2), rs(p9['cop'])))
        st = c.js("(()=>{ const s=window.__safSelf; const out={}; const w=(l)=>(l||[]).forEach(r=>{ if(r.kids) w(r.kids); else if(r.v.op==='Pulverização') out[r.v.atv]=Math.round(r.v.rend*100)/100; }); w(s.state.g2['g_rend_S2627'].rows); return out; })()") or {}
        uso = {o['a']['nome'] for o in D2.ocorr_op('S2627') if o['a']['op'] == 'Pulverização'}
        chk('O9 negativo: as 6 em uso com 32,4 ha/h; as fora de uso seguem 21,6', all(abs(v - 32.4) < .01 for k, v in st.items() if k in uso) and all(abs(v - 21.6) < .01 for k, v in st.items() if k not in uso) and len(st) > len(uso), st)
        # ---------- O12 e P7: Adubação de cobertura 24 → 12 m, só esta atividade (aviso antes → depois) ----------
        abre('#saf=S2627&passo=operacoes', 1440, 1040); expande('op:Adubação a lanço')
        clica_rid('at:Adubação a lanço|Adubação de cobertura'); f = campos('g_rend_S2627')
        chk('O12 atividade abre com "Só esta atividade"', f.get('esc') == 'Só esta atividade', f.get('esc'))
        fset('g_rend_S2627', 'larg', '12'); salvar(); time.sleep(.6); t = toast()
        cf = {('Adubação a lanço', 'Adubação de cobertura', 'r3'): {'larg': 12}}; e0 = esp_op('S2627', 'Adubação a lanço'); e1 = esp_op('S2627', 'Adubação a lanço', cf)
        chk('P7 aviso antes → depois (§4.4): Adubação a lanço 40,2 → 74,1 h · Distribuidores nov/26: 16 % → 31 %', ('Adubação a lanço: ' + e0['horas'].replace(' h', '') + ' → ' + e1['horas']) in t and 'Distribuidores nov/26: 16 % → 31 %' in t, (t, e0['horas'], e1['horas']))
        G = gop(); ad = op_linha('Adubação a lanço', G['rows']); cob = next((r for r in G['rows'] if r['OPERAÇÃO › ATIVIDADE › TALHÃO'] == 'Adubação de cobertura'), None)
        chk('O12 a atividade mostra 9,00 ha/h e R$ 25,89/ha; a operação "varia" no rendimento (o conjunto continua o mesmo, §3.4 coluna a coluna)', cob and cob['RENDIMENTO'] == '9,00 ha/h' and cob['CUSTO R$/HA'] == 'R$ 25,89/ha' and ad['CONJUNTO'] == 'Trator 03 + Distribuidor 3 t' and ad['RENDIMENTO'] == 'varia', (cob, ad))
        outras = [r for r in G['rows'] if r['_id'] and r['_id'].startswith('at:Adubação a lanço|') and r['_id'] != 'at:Adubação a lanço|Adubação de cobertura']
        chk('O12 as demais atividades da operação ficam com 18,00 ha/h', outras and all(r['RENDIMENTO'] == '18,00 ha/h' for r in outras), [(r['_id'], r['RENDIMENTO']) for r in outras])
        # ---------- O11: janela digitada em "Todas" é recusada; O5: janela 60 h na Colheita, só esta ----------
        clica_rid('op:Colheita de grãos'); f = campos('g_rend_S2627')
        chk('O11 Colheita de grãos (1 atividade): "Todas" sem campo de janela', f.get('esc') == 'Todas as atividades da operação' and 'jan' not in f, f)
        fset('g_rend_S2627', 'esc', 'Só esta atividade'); fset('g_rend_S2627', 'jan', '60'); fset('g_rend_S2627', 'esc', 'Todas as atividades da operação'); salvar(); pn = painel()
        chk('O11 janela com "Todas" é recusada no "Aplicar em"; nada gravado', 'A janela é de cada atividade.' in pn, pn[:400])
        fset('g_rend_S2627', 'esc', 'Só esta atividade'); salvar(); time.sleep(.6); G = gop(); cg = op_linha('Colheita de grãos', G['rows'])
        chk('O5 janela 60 h só na Colheita: "Cabe na janela" e veredito com "16 de 17"', cg and cg['SITUAÇÃO'] == 'Cabe na janela' and '16 de 17 atividades sem janela' in veredito(), (cg, veredito()))
        chk('O5 filtro rápido passa a mostrar 2 categorias', c.js("[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"]')].some(g=>g.offsetParent)"), '')
        # ---------- O15: R$/kg da colheita ----------
        clica_rid('op:Colheita de grãos'); f = campos('g_rend_S2627')
        chk('O15 Colheita de grãos S2627: Custo R$/kg da soja', f.get('custo_kg_c') == 'R$ 0,0606/kg', f.get('custo_kg_c')); fechar()
        # ---------- V3, V4, V6, V7: g_cap e filtro ----------
        abre('#saf=S2627&passo=operacoes', 1440, 1040)
        chk('V3 g_cap recolhida por padrão', gcap()['rows'] == [] and c.js("!document.getElementById('saf-cap')"), '')
        botao_cap(); K = gcap()
        G0 = D2.capacidade('S2627')
        chk('V3 g_cap aberta: 6 recursos e 15 colunas (Recurso, Maior uso, Mês e 12 meses)', len(K['rows']) == 6 and len(K['hs']) == 15, (len(K['rows']), K['hs']))
        colh = next(r for r in K['rows'] if r['_id'] == 'colh'); tr = next(r for r in K['rows'] if r['_id'] == 'trator')
        chk('V3 Colhedoras: Maior uso 81 %, Mês fev/27; Tratores mar/27 só da Safrinha entre parênteses', colh['MAIOR USO'] == '81 %' and colh['MÊS'] == 'fev/27' and tr['MAR/27'] == '(' + D2.fmt_ocup(G0['trator']['cells'][6]['ocup']) + ')', (colh, tr))
        chk('V3 atalhos somem com a g_cap aberta', atalhos() == [], atalhos())
        chk('V14 "—" inerte (sem botão)', cel_cap('trator', 'ago/27') == 'inerte', '')
        r = cel_cap('colh', 'fev/27')
        chk('V4 célula Colhedoras · fev/27: linha de filtro "122,0 h de 150,5 h (81 %) · precisa de 1, tem 1"', r == 'ok' and filtro() == 'Mostrando Colhedoras · fev/27: 122,0 h de 150,5 h (81 %) · precisa de 1, tem 1 Ver todas', filtro())
        G = gop(); chk('V4 cabeçalho "Horas de Colhedoras" e Total 122,0 h', 'HORAS DE COLHEDORAS' in G['hs'] and total_h() == '122,0 h', (G['hs'], total_h()))
        tal = sorted((r['OPERAÇÃO › ATIVIDADE › TALHÃO'].split(' ')[0], r['HORAS DE COLHEDORAS']) for r in G['rows'] if r['_kid'] and ' · ' in r['OPERAÇÃO › ATIVIDADE › TALHÃO'])
        chk('V4 T1-A 32,0, T1-B 30,4, T2 59,6 h', tal == [('T1-A', '32,0 h'), ('T1-B', '30,4 h'), ('T2', '59,6 h')], tal)
        botao('Ver todas'); G = gop(); chk('V4 "Ver todas" volta a Horas-conjunto e 561,8 h', 'HORAS-CONJUNTO' in G['hs'] and total_h() == fmt(pc['hconj'], 1) + ' h' and filtro() == '', (G['hs'], total_h()))
        cel_cap('trator', 'fev/27'); ft = filtro(); G = gop()
        chk('V6 Tratores · fev/27: desta safra 122,0 h · Safrinha 2027 67,3 h · precisa de 2, tem 4; só Colheita de grãos', ft == 'Mostrando Tratores · fev/27: 189,3 h de 699,2 h (27 %) · desta safra 122,0 h · Safrinha 2027 67,3 h · precisa de 2, tem 4 Ver todas' and [r['OPERAÇÃO › ATIVIDADE › TALHÃO'].split(' ')[0:3] for r in G['rows'] if not r['_kid'] and not r['_tot']] == [['Colheita', 'de', 'grãos']], (ft, [r['OPERAÇÃO › ATIVIDADE › TALHÃO'] for r in G['rows'] if not r['_kid']]))
        cel_cap('oper', 'out/26'); ft = filtro()
        chk('V7 Operadores out/26: 171,2 h de 1.425,6 h (12 %) · precisa de 2, tem 8; Total fecha', ft == 'Mostrando Operadores e equipe · out/26: 171,2 h de 1.425,6 h (12 %) · precisa de 2, tem 8 Ver todas' and total_h() == '171,2 h', (ft, total_h()))
        # ---------- P1: formulário do recurso (prévia = depois de salvar) ----------
        clica_rid('trator'); f = campos('g_recp_maq')
        chk('P1 Tratores: 174,8 h em fev/27; 366,9 h na safra', f.get('h1_c') == '174,8 h em fev/27' and f.get('hs_c', '').startswith('366,9 h'), f)
        fset('g_recp_maq', 'un', '5'); f = campos('g_recp_maq')
        chk('P1 prévia "Maior uso: 27 % → 22 % (fev/27)"', f.get('prev_c') == 'Maior uso: 27 % → 22 % (fev/27)', f.get('prev_c'))
        salvar(); time.sleep(.6); K = gcap(); tr = next(r for r in K['rows'] if r['_id'] == 'trator')
        chk('P1 depois de salvar: Tratores fev/27 22 % (C10)', tr['FEV/27'] == '22 %' and 'Tratores fev/27: 27 % → 22 %' in toast(), (tr['FEV/27'], toast()))
        # ---------- P2 e V13: Operadores 8 → 5 e Colhedoras 0 ----------
        clica_rid('oper'); fset('g_recp_pes', 'un', '5'); f = campos('g_recp_pes')
        chk('P2 prévia Operadores 8 → 5 (§9.2 P2)', f.get('prev_c') == 'Maior uso: 42 % → 67 % (mai/27) · precisa de 6, tem 5 · Colheita de café · Derriçadeiras portáteis · equipe de 6 deixa de trabalhar em 1 ocorrência', f.get('prev_c'))
        salvar(); time.sleep(.6); chk('P2 veredito R2 "Operadores e equipe precisam de 6 em mai/27 e você tem 5"', veredito().startswith('Falta recurso: Operadores e equipe precisam de 6 em mai/27 e você tem 5'), veredito())
        abre('#saf=S2627&passo=operacoes', 1440, 1040); botao_cap(); clica_rid('colh'); fset('g_recp_maq', 'un', '0'); salvar(); time.sleep(.6)
        chk('V13 Colhedoras 0: veredito com "precisam de 1 em fev/27 e você tem 0. Inclui 3 ocorrências ainda sem alocação."', veredito().startswith('Falta recurso: Colhedoras precisam de 1 em fev/27 e você tem 0. Inclui 3 ocorrências ainda sem alocação. Fora da conta:'), veredito())
        colh = next(r for r in gcap()['rows'] if r['_id'] == 'colh'); chk('V13 fev/27 "precisa 1"; Maior uso "não calculável"', colh['FEV/27'] == 'precisa 1' and colh['MAIOR USO'] == 'não calculável', colh)
        # ---------- P8: +1 pessoa na configuração própria do Plantio (C22): Operadores sobe no formulário do recurso e no Resumo ----------
        abre('#saf=S2627&passo=operacoes', 1440, 1040); botao_cap(); clica_rid('oper'); h0 = campos('g_recp_pes').get('hs_c', ''); fechar()
        expande('op:Plantio'); expande('at:Plantio|Plantio e adubação de base')
        rid = c.js("(()=>{const m=(window.__safSelf||{}).__opmap||{}; return Object.keys(m).find(k=>m[k].t==='oc'&&m[k].op==='Plantio'&&m[k].i.c.v.local==='T2')||null;})()")
        expande(rid); clica_rid(rid + '|c0'); pe0 = int(campos('g_rend_S2627').get('pess') or 0); fset('g_rend_S2627', 'pess', str(pe0 + 1)); salvar(); time.sleep(.5)
        clica_rid('oper'); h1 = campos('g_recp_pes').get('hs_c', ''); fechar()
        cf8 = {('Plantio', 'Plantio e adubação de base', 'r2'): {'pess': pe0 + 1}}; G8 = D2.capacidade('S2627', None, None, cf8); p8 = D2.plano_op('S2627', None, cf8)
        num = lambda t: float(t.split(' h')[0].replace('.', '').replace(',', '.')) if t else -1
        chk('P8 +1 pessoa no Plantio: horas de Operadores no formulário do recurso = espelho (sobe 62,70 h)', abs(num(h1) - G8['oper']['horasSafra']) <= 0.051 and abs(num(h1) - num(h0) - 62.70) <= 0.11 and abs(G8['oper']['horasSafra'] - D2.capacidade('S2627')['oper']['horasSafra'] - 62.70) < 0.01, (h0, h1, G8['oper']['horasSafra']))
        botao('Resumo da safra'); pn = painel(); fechar()
        chk('P8 horas-homem do Resumo = espelho (C22)', (fmt(p8['hh'], 2) + ' horas-homem') in pn, (fmt(p8['hh'], 2), pn[-400:]))
        # ---------- P4: Resumo da safra ----------
        abre('#saf=S2627&passo=operacoes', 1440, 1040); botao('Resumo da safra'); pn = painel(); R = D2.resumo_cultura('S2627')
        lin = all(f"{b['cult']} {nfa(b['area'])} ha {rs(b['cop'])} {rs(b['cins'])} {rs(b['rha'])}/ha" in pn for b in R.values())
        chk('P4 Resumo S2627: custo por cultura = espelho e Total', lin and ('Total ' + nfa(sum(b['area'] for b in R.values())) + ' ha ' + rs(sum(b['cop'] for b in R.values()))) in pn, pn[:900])
        chk('P4 nota "Todos de hoje em diante" e trabalho da safra', 'Todos de hoje em diante' in pn and (nfa(pc['area']) + ' ha-op (hectares-operação) · ' + fmt(pc['hconj'], 2) + ' horas-conjunto · ' + fmt(pc['hh'], 2) + ' horas-homem') in pn, pn[-900:])
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); foco = c.js("document.activeElement&&document.activeElement.getAttribute('data-acao')")
        chk('P4 Esc fecha o Resumo e o foco volta ao link', painel() == '' and foco == 'resumo', (painel()[:80], foco))
        # ---------- V12, V11, V8 ----------
        abre('#saf=S27SF&passo=operacoes'); chk('V12 S27SF veredito R5 (verde, para o leitor de tela) e nenhum atalho fora da tabela', veredito() == VER['S27SF'] and atalhos() == [], (veredito(), atalhos()))
        abre('#saf=S2526&passo=operacoes'); ac = acoes()
        chk('V11 S2526: veredito R1; sem atalho; primária "Ver demanda de insumos ›"', veredito() == VER['S2526'] and atalhos() == [] and 'Ver demanda de insumos ›' in ac, (veredito(), atalhos(), ac))
        botao_cap(); K = gcap(); clica_rid('trator'); pn = painel()
        chk('V11 S2526: g_cap toda "—" e recurso só em consulta ("Para ajustar, abra uma safra aberta.")', all(v in ('—', '') for r in K['rows'] for k, v in r.items() if not k.startswith('_') and k not in ('RECURSO',)) and 'Para ajustar, abra uma safra aberta.' in pn and 'Salvar' not in pn, pn[:300])
        fechar(); clica_rid('op:Pulverização'); pn = painel(); chk('V11 S2526: rendimento só em consulta', pn and 'Salvar' not in pn, pn[:200]); fechar()
        abre('#saf=LG2627&passo=operacoes'); vlg = veredito()
        chk('V8 LG2627 veredito R2', vlg.startswith('Falta recurso: Operadores e equipe precisam de 127 em nov/26 e você tem 8 (9 meses); Tratores, 10 em out/26 e você tem 4 (4 meses). Inclui 56 ocorrências ainda sem alocação. Fora da conta: 75 ocorrências antes do início da safra (01/09/2026).'), vlg)
        # 15/10 (TAB-06): o alerta fica só na linha. Com a coluna Situação à vista (o teste liga todas as colunas: cv_todas_sempre), ele é o chip
        # da célula; com ela recolhida, é o ⚠ da 1ª coluna com o texto na dica. Lê os dois, nas linhas da tabela
        ico = c.js("[...document.querySelectorAll('[data-g2g^=g_op] [role=row]')].map(r=>[r.innerText,...[...r.querySelectorAll('[data-dica]')].map(e=>e.dataset.dica)].filter(d=>/Operadores e equipe 1.584 %|Tratores 234 %/.test(d)).join('|')).filter(Boolean).join('|')") or ''
        chk('V8 sem atalho fora da tabela; Operadores e equipe 1.584 % e Tratores 234 % ficam nas linhas (chip da Situação ou dica do ⚠)', atalhos() == [] and 'Operadores e equipe 1.584 %' in ico and 'Tratores 234 %' in ico, [atalhos(), ico[:300]])
        chk('V8 qualificador do custo (antes do início e pendentes)', 'inclui ' + rs(919906.51) + ' de antes de 01/09/2026; não inclui as ocorrências pendentes' in custo(), custo())
        txt = c.js("document.body.innerText"); chk('V8 Colheita de frutas: "sem recurso na fazenda · precisa de 10, tem 8"', 'sem recurso na fazenda · precisa de 10, tem 8' in txt, '')
        botao_cap(); op_ = next(r for r in gcap()['rows'] if r['_id'] == 'oper')
        chk('V8 g_cap: Operadores nov/26 "precisa 127", Maior uso 1.584 %', op_['NOV/26'] == 'precisa 127' and op_['MAIOR USO'] == '1.584 %', op_)
        for s in ('S2627', 'S27SF', 'LG2627', 'S2526'):
            abre(f'#saf={s}&passo=operacoes'); chk(f'L4 sem erro de JS · {s}', erros() == '', erros())
        c.shot(os.path.join(PROBE, 'saf3_1440.png'))
    if MODO in ('celular', 'tudo'):
        # ---------- N5, L2 ----------
        for w, h in ((390, 844), (360, 800)):
            for s in ('S2627', 'LG2627'):
                abre(f'#saf={s}&passo=operacoes', w, h, True)
                m = c.js(r"""(()=>{ const vw=innerWidth, vh=innerHeight; const v=document.querySelector('#saf-v3-ver'); const a=document.querySelector('[data-acoes]'); const pb=a&&[...a.querySelectorAll('button,a')].filter(b=>b.offsetParent).pop();
                  const dentro=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); return r.top>=0&&r.bottom<=vh+1&&r.left>=0&&r.right<=vw+1; };
                  return {pag:document.documentElement.scrollWidth>vw+1, ver:dentro(v), prim:dentro(pb), fx:(document.body.innerText.match(/Etapa \d de \d · [^\n]+/)||[''])[0]}; })()""")
                chk(f'L2 {s} {w}×{h}: sem rolagem lateral; veredito e primária sem rolar', not m['pag'] and m['ver'] and m['prim'], m)
                if s == 'S2627' and w == 390: chk('N5 faixa a 390: "Etapa 3 de 4 · Dimensione operações e recursos"', m['fx'].startswith('Etapa 3 de 4 · Dimensione operações e recursos'), m['fx'])
                c.shot(os.path.join(PROBE, f'saf3_{s}_{w}.png'))
        abre('#saf=S2627&passo=operacoes', 390, 844, True); botao_cap(); r = cel_cap('colh', 'fev/27')
        chk('390: célula Colhedoras · fev/27 filtra a g_op', r == 'ok' and filtro().startswith('Mostrando Colhedoras · fev/27'), filtro())
        chk('390: sem erro de JS', erros() == '', erros())
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
