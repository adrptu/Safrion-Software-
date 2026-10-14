# -*- coding: utf-8 -*-
"""Teste CDP · REND-MULTICONJUNTOS-20261003 no Planejar safra (SAF.dc.html), Safra 2026/27 · Santa Rita, na etapa 3 "Dimensione operações
e recursos" (etapa única que juntou as antigas 3, 4 e 5 em 05/10/2026; ESPECIFICACAO etapa-unica-3-4-5 §9.3). O que não muda: as contas do
motor (repartir) e o espelho dados2; muda só por onde se vê e se edita: a g_op (operação › atividade › talhão › configuração) e o
formulário Rendimento aberto pela linha ("Neste talhão" e "Nesta configuração" trazem o trio necessário × atendido × saldo).
 1 dados iniciais: Total de horas-conjunto e custo de operação = dados2.plano_op; diesel e horas-homem no Resumo da safra
 2 T2 (298 ha) no Plantio: área atendida, horas-conjunto e R$/ha de cada configuração = dados2.repartir; Σ área = 298; decorrido no "Neste talhão"
 3 um conjunto só (Dessecação pré-plantio): horas = área ÷ 21,6
 4 incluir outra configuração em Adubação de cobertura pelo formulário (por classe, sem patrimônio): a anterior continua; totais recalculam
 5 mudar a repartição (prestador 30 % fixo): T2 segue o espelho; demanda de insumos (CAL-01) igual à inicial (dose × área)
 6 recurso compartilhado: a nova configuração usa o mesmo distribuidor do cadastro → em sequência; janela curta → "sequência não cabe na janela"
 7 partes fixas acima de 100 % são recusadas no formulário (o que foi digitado fica)
 8 remover a configuração incluída (com confirmação): volta a uma configuração e os totais voltam aos iniciais; sem erros de JS
 9 celular 390 px · 10 Safrinha 2027 e Lagoa Grande = espelho · 11 safra encerrada só consulta
Modos, cada um < 90 s: python3 rend_multiconjuntos_test.py [fluxo|telas|bordas|bordas2]   (fluxo = 1–8, padrão; telas = 9–11;
bordas = B1 janela 0 h (causa, linhas agregadas, veredito), B2 sequência × janela de 3 h (necessário × atendido × saldo no "Neste talhão" e no
"Nesta configuração"; S5 da decisão Codex REND-RETORNO-1818: partes 50/50), B3 teclado; bordas2 = B5 motivo do grupo da fazenda e troca da 1ª
configuração, B6 prestador fora das horas-homem). Capturas: _probe/rend_*.png."""
import sys, os, time, json, re
MODO = (sys.argv[1] if len(sys.argv) > 1 else 'fluxo')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, IR_ETAPA, cv_todas_sempre
import dados2 as D2
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render'))
OK = []; FAIL = []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + (f' · {str(det)[:700]}' if (det != '' and not cond) else ''), flush=True)
def fmt(x, d=0): s = f'{float(x):,.{d}f}'; return s.replace(',', 'X').replace('.', ',').replace('X', '.')
def nfa(x): s = fmt(round(float(x), 2), 2); return s.rstrip('0').rstrip(',')
def rs(x): return 'R$ ' + fmt(x, 2)
def trio_txt(e):   # as três linhas da ocorrência (safra.js · e3Neste): necessário, atendido e saldo, com unidades
    hs = lambda a, b: f' · {fmt(a, 1)} horas-conjunto · {fmt(b, 1)} h decorridas'; n, f = e['nec'], e['falta']
    return [f"Necessário: {nfa(n['area'])} ha" + hs(n['hconj'], n['decorrido']), f"Atendido: {nfa(e['alocado'])} ha" + hs(e['hconj'], e['decorrido']),
            f"Saldo: {nfa(e['saldo'])} ha · faltam " + hs(f['hconj'], f['decorrido'])[3:]]
def cfg_txt(x): return f"precisa de {nfa(x['nq'])} ha = {fmt(x['nh'], 1)} h · faltam {nfa(x['fq'])} ha = {fmt(x['fh'], 1)} h"
c = None
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
ROWS = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const hn=h=>n(h.innerText).replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase();
  const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/^OPERA/.test(hn(t.querySelector('[role=columnheader]')))); if(!t) return [];
  const hs=[...t.querySelectorAll('[role=columnheader]')].map(hn);
  return [...t.querySelectorAll('[role=row]')].slice(1).map(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; const o={_id:r.getAttribute('data-rid'),_tot:r.classList.contains('g2tot')};
    cs.forEach((c,i)=>{ const h=hs[i]||'C'+i; o[/^CUSTO TOTAL/.test(h)?'CUSTO TOTAL':h.split(' ')[0]]=n(c.innerText).replace(/^[▾▸] ?/,''); }); return o; }); })()"""
def rows(): return c.js(ROWS) or []
def linha(rid): return next((r for r in rows() if r['_id'] == rid), None)
def total(): t = next((r for r in rows() if r['_tot']), None); return t and (t.get('HORAS-CONJUNTO') or t.get('HORAS'))   # com o filtro recurso × mês: "Horas de <recurso>"
def custo(): return c.js("(document.body.innerText.match(/Custo de operação R\\$ [\\d.,]+/)||[''])[0]") or ''
def toast(): return c.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def veredito(): return c.js(f"(()=>{{const e=document.querySelector('#saf-v3-ver [role=status]'); return e?{N}(e.innerText):'';}})()") or ''
def painel(): return c.js(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?{N}(a.innerText):'';}})()") or ''
def k6(): return c.js("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
def erros(): return c.js("(window.__errs||[]).join(' | ')") or ''
def esc(): c.tecla('Escape', 'Escape', 27); time.sleep(.45)
PAINEL = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"
def botao(lab, raiz='document', inicio=False):
    r = c.js(f"""(()=>{{const R={raiz}; if(!R) return 'sem raiz'; const bs=[...R.querySelectorAll('button,a')].filter(b=>b.offsetParent); const n=s=>(s||'').replace(/\\s+/g,' ').trim();
      const b=bs.find(b=>n(b.innerText)==={json.dumps(lab)})||({json.dumps(inicio)}&&bs.find(b=>n(b.innerText).indexOf({json.dumps(lab)})===0)); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"""); time.sleep(.6); return r
def salvar(): r = botao('Salvar', PAINEL); time.sleep(.3); return r, toast()
def campo(k, v):
    r = c.js(f"""(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] [id$="_{k}"]')].find(x=>x.offsetParent); if(!i) return 'sem campo {k}'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.25); return r
def valor(k): return c.js(f"(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] [id$=\"_{k}\"]')].find(x=>x.offsetParent); return i?i.value:null;}})()")
def clica(rid):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid={json.dumps(rid)}]'); if(!r) return 'sem linha {rid}'; const x=[...r.querySelectorAll('[role=cell]')].find(z=>!z.querySelector('input,button')&&z.innerText.trim())||r; x.click(); return 'ok';}})()"""); time.sleep(.6); return r
def expande(rid):
    r = c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid={json.dumps(rid)}]'); const b=r&&r.querySelector('.g2car'); if(!b) return 'sem seta'; if(b.getAttribute('aria-expanded')!=='true') b.click(); return 'ok';}})()"""); time.sleep(.45); return r
# ids das linhas da g_op (safra.js · e3Op guarda o mapa em __opmap): a ocorrência de uma atividade num local; as configurações são <id>|c<j>
def rid_oc(op, atv, local):
    return c.js(f"""(()=>{{const m=(window.__safSelf||{{}}).__opmap||{{}}; return Object.keys(m).find(k=>m[k].t==='oc'&&m[k].op==={json.dumps(op)}&&m[k].atv==={json.dumps(atv)}&&m[k].i.c.v.local==={json.dumps(local)})||null;}})()""")
def abre_oc(op, atv, local):
    expande('op:' + op); expande('at:' + op + '|' + atv); rid = rid_oc(op, atv, local)
    if rid: expande(rid)
    return rid
def etapa(n): r = c.js(f"({IR_ETAPA})({n})"); time.sleep(.6); return r
NAV = [0]
def abre(h, w=1440, hh=1000, toque=False):
    NAV[0] += 1; c.aparelho(w, hh, 1, toque); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html?r={NAV[0]}{h}'); time.sleep(1.2)
pools = {r['id']: dict(un=r['un'], nome=r['nome']) for r in D2.RECURSOS}
def esperado_T2(part=None):
    cfs = [D2.cfg_in(x) for x in D2.cfgs_rend('S2627', 'Plantio', 'Plantio e adubação de base')]
    if part is not None: cfs[1]['part'] = part
    return D2.repartir(298, cfs, pools)
def ver_T2(part=None):
    """T2 no Plantio: a ocorrência e as duas configurações (área atendida, horas, R$/ha) = espelho; Σ área + saldo = 298"""
    e = esperado_T2(part); rid = abre_oc('Plantio', 'Plantio e adubação de base', 'T2'); o = linha(rid) if rid else None
    ks = [linha(rid + f'|c{j}') for j in range(2)] if rid else []
    okv = bool(o) and o['ÁREA'] == nfa(298) + ' ha' and o['HORAS-CONJUNTO'] == fmt(e['hconj'], 1) + ' h'
    okk = len(ks) == 2 and all(ks) and all(k['ÁREA'] == nfa(x['q']) + ' ha' and k['HORAS-CONJUNTO'] == fmt(x['h'], 1) + ' h' and k['CUSTO'] == rs(x['custo'] / x['q']) + '/ha' for k, x in zip(ks, e['itens']))
    soma = sum(x['q'] for x in e['itens']) + e['saldo']
    return okv and okk and abs(soma - 298) < 1e-9, [o, ks, [(nfa(x['q']), fmt(x['h'], 1), rs(x['custo'] / x['q'])) for x in e['itens']]], rid, e
try:
    c = Chrome()
    cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
    if MODO == 'fluxo':
        abre('#saf=S2627&passo=operacoes')
        # ---------- 1 · totais iniciais × espelho ----------
        m = D2.plano_op('S2627'); t0 = (total(), custo())
        chk('1 Total de horas-conjunto da g_op = espelho dados2.plano_op', t0[0] == fmt(m['hconj'], 1) + ' h', [t0, fmt(m['hconj'], 1)])
        chk('1b custo de operação da etapa = espelho', t0[1] == 'Custo de operação ' + rs(m['cop']), [t0[1], rs(m['cop'])])
        botao('Resumo da safra'); pn = painel()
        chk('1c horas-homem e diesel (Resumo da safra) = espelho', (fmt(m['hh'], 2) + ' horas-homem · ' + fmt(m['diesel'], 2) + ' L de diesel estimado') in pn, pn[-500:]); esc()
        etapa(4); k6a = k6(); etapa(3)
        # ---------- 2 · T2 dividido entre dois conjuntos ----------
        ok, det, rid, e = ver_T2(); c.shot(os.path.join(PROBE, 'rend_depois_plano_operacional.png'))
        chk('2 T2 (298 ha): duas configurações com área, horas-conjunto e R$/ha do espelho; Σ área = 298 ha', ok, det)
        clica(rid); nt = valor('neste_c') or ''
        chk('2b "Neste talhão": decorrido do espelho, menor que as horas-conjunto', ('Atendido: ' + nfa(e['alocado']) + ' ha · ' + fmt(e['hconj'], 1) + ' horas-conjunto · ' + fmt(e['decorrido'], 1) + ' h decorridas') in nt and e['decorrido'] < e['hconj'], nt)
        esc()
        # ---------- 3 · um conjunto só ----------
        rid3 = abre_oc('Pulverização', 'Dessecação pré-plantio', 'T2'); one = linha(rid3) if rid3 else None
        chk('3 um conjunto só (Dessecação pré-plantio em T2): sem linhas de configuração, horas = 298 ÷ 21,6', one is not None and one['HORAS-CONJUNTO'] == fmt(298 / 21.6, 1) + ' h' and not linha(rid3 + '|c0'), one)
        # ---------- 4 · incluir outra configuração em Adubação de cobertura ----------
        abre('#saf=S2627&passo=operacoes'); expande('op:Adubação a lanço'); clica('at:Adubação a lanço|Adubação de cobertura')
        print('incluir:', botao('+ Outra configuração para Adubação de cobertura', PAINEL))
        chk('4a "+ Outra configuração" abre "Nova configuração" com a atividade à vista e "Por classe" sem patrimônio',
            'Nova configuração' in painel() and valor('opatv') == 'Adubação a lanço · Adubação de cobertura' and valor('conj_id') == 'classe', [painel()[:200], valor('opatv'), valor('conj_id')])
        for k, v in [('nome', 'Trator 75 cv + distribuidor 12 m'), ('larg', '12'), ('vel', '8'), ('efic', '70'), ('maq', '120'), ('impl', '30'), ('pess', '1'), ('pess_rs', '38'), ('diesel', '8')]: campo(k, v)
        c.shot(os.path.join(PROBE, 'rend_depois_form_nova.png')); print('salvar:', salvar())
        at = linha('at:Adubação a lanço|Adubação de cobertura'); rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2')
        ks = [linha(rid4 + f'|c{j}') for j in range(2)] if rid4 else []
        chk('4b a atividade passa a 2 conjuntos; a anterior (Trator 03 + Distribuidor 3 t, 18 ha/h) continua; a nova com 6,72 ha/h',
            bool(at) and at['CONJUNTO'] == '2 conjuntos' and len(ks) == 2 and all(ks) and ks[0]['OPERAÇÃO'].startswith('Trator 03 + Distribuidor 3 t') and ks[0]['RENDIMENTO'] == '18,00 ha/h' and ks[1]['RENDIMENTO'] == '6,72 ha/h', [at, ks])
        c.shot(os.path.join(PROBE, 'rend_depois_rendimentos.png'))
        t1 = (total(), custo()); chk('4c horas e custo recalculados no lugar (mudam)', t1 != t0, [t0, t1])
        # ---------- 5 · mudar a repartição do prestador para 30 % ----------
        ridp = abre_oc('Plantio', 'Plantio e adubação de base', 'T2'); clica(ridp + '|c1')
        chk('5a "Nesta configuração" no formulário aberto pela configuração', 'precisa de ' in (valor('nesta_c') or ''), valor('nesta_c'))
        campo('part', '30'); print('salvar:', salvar())
        ok, det, _, _ = ver_T2(30); chk('5b T2 com 30 % fixo no prestador: área 89,4 + 208,6 = 298 ha e horas/R$/ha do espelho', ok and det[1][1] and det[1][1]['ÁREA'] == '89,4 ha', det)
        etapa(4); k6b = k6(); etapa(3); chk('5c demanda de insumos (CAL-01) igual à inicial: a divisão não muda dose × área', k6b == k6a and k6a != '', [k6a, k6b])
        # ---------- 6 · recurso compartilhado ----------
        rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid4 + '|c1')
        opts = c.js("[...document.querySelectorAll('aside [id$=\"_conj_id\"] option')].map(o=>[o.value,o.innerText])") or []
        alvo, alvo_t = next((o for o in opts if o[0].endswith('+a07') and not o[0].startswith('a03')), (None, ''))
        print('escolher', alvo, campo('conj_id', alvo)); print('salvar:', salvar())
        rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); ks = [linha(rid4 + f'|c{j}') for j in range(2)]
        clica(rid4); nt = valor('neste_c') or ''; esc()
        mm = re.search(r'Atendido: [\d.,]+ ha · ([\d.,]+) horas-conjunto · ([\d.,]+) h decorridas', nt)
        chk('6a mesmo distribuidor do cadastro nas duas configurações → "em sequência"; decorrido = horas-conjunto na ocorrência',
            all(k and 'em sequência' in k['SITUAÇÃO'] for k in ks) and bool(mm) and mm.group(1) == mm.group(2), [ks, nt])
        for j in (1, 0):
            rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid4 + f'|c{j}'); campo('jan', '3'); print('janela 3 h:', salvar())
        rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); o2 = linha(rid4)
        c.shot(os.path.join(PROBE, 'rend_depois_conflito.png'))
        chk('6b janela de 3 h por talhão: área que não cabe fica "sem conjunto"; sequência acima da janela aparece como conflito; nada vira 0 h',
            bool(o2) and 'ha sem conjunto' in o2['SITUAÇÃO'] and 'sequência não cabe na janela' in o2['SITUAÇÃO'] and o2['HORAS-CONJUNTO'] not in ('0,0 h', ''), o2)
        # ---------- 7 · partes fixas acima de 100 % ----------
        ridp = abre_oc('Plantio', 'Plantio e adubação de base', 'T2'); clica(ridp + '|c0'); campo('part', '80'); salvar(); pe = painel()
        chk('7 partes fixas 30 % + 80 % são recusadas com motivo; o formulário continua aberto com o que foi digitado', 'o máximo é 100 %' in pe and valor('part') == '80', pe[:300])
        campo('part', ''); salvar()
        # ---------- 8 · remover a configuração incluída ----------
        rid4 = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid4 + '|c1')
        print('remover (1º toque):', botao('Remover esta configuração', PAINEL))
        conf = c.js("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/^Confirmar: remover/.test(t))") or []
        print('confirmar:', botao('Confirmar: remover', PAINEL, True), toast())
        at = linha('at:Adubação a lanço|Adubação de cobertura')
        chk('8a remover pede confirmação e a atividade volta a uma configuração', bool(conf) and bool(at) and at['CONJUNTO'] != '2 conjuntos', [conf, at])
        # prestador volta a dividir pelo rendimento e a janela da atividade sai: totais voltam aos iniciais
        ridp = abre_oc('Plantio', 'Plantio e adubação de base', 'T2'); clica(ridp + '|c1'); campo('part', ''); salvar()
        expande('op:Adubação a lanço'); clica('at:Adubação a lanço|Adubação de cobertura'); campo('jan', ''); print('desfeito:', salvar())
        t2 = (total(), custo()); chk('8b depois de desfazer, horas e custo voltam aos iniciais', t2 == t0, [t0, t2])
        chk('8c sem erros de JS na página', erros() == '', erros())
    if MODO == 'telas':
        # ---------- 10 · outras safras: totais = espelho; safra encerrada só consulta ----------
        for sf in ('S27SF', 'LG2627'):
            abre(f'#saf={sf}&passo=operacoes'); ms = D2.plano_op(sf)
            chk(f'10 {sf}: Total de horas-conjunto e custo = espelho dados2.plano_op (uma configuração por atividade)', total() == fmt(ms['hconj'], 1) + ' h' and custo() == 'Custo de operação ' + rs(ms['cop']) and ms['multi'] == 0, [total(), custo(), fmt(ms['hconj'], 1), rs(ms['cop'])])
        # 10b (LG2627): o filtro do mês fecha com a célula e com o espelho (Σ horas de Operadores em nov/26 = capSaf)
        G = D2.capacidade('LG2627'); cel = G['oper']['cells'][2]
        botao('Capacidade por mês ▾')
        r = c.js("""(()=>{ const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/^RECURSO/i.test(t.querySelector('[role=columnheader]').innerText)); if(!t) return null; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.trim().toLowerCase());
          const i=hs.indexOf('nov/26'); const b=t.querySelector('[role=row][data-rid=oper]').querySelectorAll('[role=cell]')[i].querySelector('button'); if(!b) return 'sem'; b.click(); return b.getAttribute('aria-label'); })()"""); time.sleep(.7)
        chk('10b LG2627 Operadores nov/26: aria-label, Total da g_op e espelho capSaf com as mesmas horas', bool(r) and (fmt(cel['d'], 1) + ' h de ' + fmt(cel['cap'], 1) + ' h') in r and total() == fmt(cel['dThis'], 1) + ' h', [r, total(), fmt(cel['dThis'], 1)])
        abre('#saf=S2526&passo=operacoes'); clica('op:Colheita de grãos')
        fa = c.js("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/configuração/.test(t))") or []
        ro = c.js("(()=>{const i=[...document.querySelectorAll('aside [id$=\"_vel\"]')].find(x=>x.offsetParent); return i?(i.readOnly||i.disabled):null;})()")
        chk('11 Safra 2025/26 (encerrada): formulário só em consulta, sem "+ Outra configuração" nem Salvar', fa == [] and ro is True and 'Salvar' not in painel(), [fa, ro, painel()[:200]])
        # ---------- 9 · celular (390 px): a tabela rola dentro da caixa ----------
        abre('#saf=S2627&passo=operacoes', 390, 844, True); abre_oc('Plantio', 'Plantio e adubação de base', 'T2')
        c.shot(os.path.join(PROBE, 'rend_depois_celular_plano.png'))
        hs = c.js("document.documentElement.scrollWidth>innerWidth+1")
        chk('9 celular 390 px: etapa 3 sem rolagem lateral da página (a tabela rola dentro da caixa) e sem erros', not hs and erros() == '', [hs, erros()])
    SEQ = 'Em sequência: divide trator, implemento ou operador'
    if MODO == 'bordas':
        # ---------- B1 · janela 0 h com rendimento válido: pendente com a causa certa, nunca 0 h nem R$ 0; o veredito diz ----------
        abre('#saf=S2627&passo=operacoes'); clica('op:Tratamento de sementes'); campo('esc', 'Só esta atividade'); campo('jan', '0'); print('janela 0:', salvar())
        rid = abre_oc('Tratamento de sementes', 'Tratamento de sementes', 'T2'); oc = linha(rid) if rid else None; op = linha('op:Tratamento de sementes')
        c.shot(os.path.join(PROBE, 'rend_bordas_janela0.png'))
        chk('B1a janela 0 h (rendimento 40 ha/h válido): a Situação diz "sem horas na janela · pendente", não "sem rendimento"', bool(oc) and 'sem horas na janela · pendente' in oc['SITUAÇÃO'] and 'sem rendimento' not in oc['SITUAÇÃO'], oc)
        chk('B1b linhas de operação e atividade com todas as ocorrências pendentes não mostram 0,0 h nem R$ 0', bool(op) and op['HORAS-CONJUNTO'] in ('', '—') and not op['CUSTO'].startswith('R$ 0') and 'sem horas na janela · 3 pendentes' in op['SITUAÇÃO'], op)
        v = veredito(); chk('B1c o veredito diz que o cálculo está incompleto pelas ocorrências pendentes (R3)', v.startswith('Cálculo incompleto: Tratamento de sementes com 3 ocorrências pendentes (sem horas na janela)'), v)
        # ---------- B2 · duas configurações em sequência numa janela de 3 h (Controle de ácaro, T7 42 ha) ----------
        abre('#saf=S2627&passo=operacoes'); expande('op:Pulverização'); clica('at:Pulverização|Controle de ácaro')
        for k, v in [('esc', 'Só esta atividade'), ('modo', 'Largura × velocidade'), ('larg', '6'), ('vel', '8'), ('efic', '75'), ('maq', '180'), ('impl', '0'), ('pess', '0'), ('pess_rs', '0')]: campo(k, v)
        print('A:', salvar()); clica('at:Pulverização|Controle de ácaro'); print('incluir:', botao('+ Outra configuração para Controle de ácaro', PAINEL))
        campo('conj_id', 'prestador'); time.sleep(.2)
        for k, v in [('nome', 'B prestador 12 m'), ('modo', 'Largura × velocidade'), ('larg', '12'), ('vel', '8'), ('efic', '75'), ('maq', '300'), ('seq', SEQ), ('jan', '3')]: campo(k, v)
        print('B:', salvar())
        rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); clica(rid + '|c0'); campo('seq', SEQ); campo('jan', '3'); print('A em sequência:', salvar())
        rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); oc = linha(rid); c.shot(os.path.join(PROBE, 'rend_bordas_sequencia_janela3.png'))
        e = D2.repartir(42, [dict(nome='A', rend=D2.rend_calc(6, 8, 75), custo_h=180, jan=3, seq=True), dict(nome='B', rend=D2.rend_calc(12, 8, 75), custo_h=300, jan=3, seq=True)])
        mm = re.search(r'([\d.,]+) ha sem conjunto', oc['SITUAÇÃO'] if oc else ''); sem = float(mm.group(1).replace('.', '').replace(',', '.')) if mm else -1
        chk('B2a sequência numa janela de 3 h: "sem conjunto" = espelho 25,8 ha; horas-conjunto 3,0 h', bool(oc) and abs(sem - 25.8) < 0.01 and oc['HORAS-CONJUNTO'] == '3,0 h' and abs(e['saldo'] - 25.8) < 1e-9, [oc, sem])
        clica(rid); nt = valor('neste_c') or ''
        chk('B2b o conflito continua à vista com o motivo (precisam de 7,78 h para os 42 ha; a janela tem 3 h) e a área que não cabe é explicada',
            bool(oc) and 'sequência não cabe na janela' in oc['SITUAÇÃO'] and 'em sequência precisam de 7,78 h para 42 ha; a janela tem 3 h' in nt and 'dividem a mesma janela' in nt, nt)
        tt = trio_txt(e); cf = [cfg_txt(x) for x in e['itens']]; esc()
        nc = []
        for j in range(2):
            rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); clica(rid + f'|c{j}'); nc.append(valor('nesta_c') or ''); esc()
        chk('B2c necessário = atendido + saldo na ocorrência ("Neste talhão") e em cada configuração ("Nesta configuração") = espelho', all(t in nt for t in tt) and all(t in x for t, x in zip(cf, nc)), [nt, nc, tt, cf])
        # ---------- S5 da decisão Codex na tela: partes fixas 50/50 em sequência, janela de 3 h ----------
        for j in range(2):
            rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); clica(rid + f'|c{j}'); campo('part', '50'); salvar()
        rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); clica(rid); nt5 = valor('neste_c') or ''; esc()
        nc5 = []
        for j in range(2):
            rid = abre_oc('Pulverização', 'Controle de ácaro', 'T7'); clica(rid + f'|c{j}'); nc5.append(valor('nesta_c') or ''); esc()
        e5 = D2.repartir(42, [dict(nome='A', rend=D2.rend_calc(6, 8, 75), custo_h=180, jan=3, seq=True, part=50), dict(nome='B', rend=D2.rend_calc(12, 8, 75), custo_h=300, jan=3, seq=True, part=50)])
        tt5 = trio_txt(e5); cf5 = [cfg_txt(x) for x in e5['itens']]
        chk('B2d S5 na tela (50 % + 50 %, janela 3 h): necessário, atendido e saldo do espelho; motivo com as 8,75 h da demanda inteira',
            all(t in nt5 for t in tt5) and 'em sequência precisam de 8,75 h para 42 ha; a janela tem 3 h' in nt5 and all(t in x for t, x in zip(cf5, nc5)) and abs(e5['nec']['hconj'] - 8.75) < 1e-9, [nt5, nc5])
        # ---------- B3 · teclado: Enter na linha da atividade abre o formulário ----------
        foco = c.js("(()=>{const r=document.querySelector('[role=row][data-rid=\"at:Pulverização|Dessecação pré-plantio\"]'); if(!r) return false; r.focus(); return document.activeElement===r;})()")
        c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13, 'text': '\r', 'unmodifiedText': '\r'}); c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13}); time.sleep(.6)
        ab = 'Rendimento' in painel() and valor('esc') == 'Só esta atividade'
        chk('B3 Enter na linha da atividade abre o formulário Rendimento ("Só esta atividade")', bool(foco) and ab, [foco, painel()[:120]])
        chk('B4 sem erros de JS', erros() == '', erros())
    if MODO == 'bordas2':
        # ---------- B5 · grupo da fazenda (1 distribuidor) põe em sequência: o motivo aparece; a troca da 1ª configuração conta ----------
        abre('#saf=S2627&passo=operacoes'); expande('op:Adubação a lanço'); clica('at:Adubação a lanço|Adubação de cobertura'); botao('+ Outra configuração para Adubação de cobertura', PAINEL)
        for k, v in [('nome', 'Classe distribuidor 12 m'), ('larg', '12'), ('vel', '8'), ('efic', '70'), ('maq', '120'), ('impl', '30'), ('pess', '1'), ('pess_rs', '38')]: campo(k, v)
        print('classe:', salvar())
        rid = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid); nt = valor('neste_c') or ''; esc()
        chk('B5a "Ao mesmo tempo" posta em sequência pelo grupo da fazenda: "Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1"', 'Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1' in nt, nt)
        rid = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid + '|c0'); campo('troca', '2'); print('troca 2 h na 1ª:', salvar())
        rid = abre_oc('Adubação a lanço', 'Adubação de cobertura', 'T2'); clica(rid); nt2 = valor('neste_c') or ''; esc()
        mm = re.search(r'Atendido: [\d.,]+ ha · ([\d.,]+) horas-conjunto · ([\d.,]+) h decorridas', nt2); num = lambda x: float(x.replace('.', '').replace(',', '.'))
        chk('B5b troca informada na 1ª configuração entra no decorrido (decorrido = horas-conjunto + 2 h)', bool(mm) and abs(num(mm.group(2)) - num(mm.group(1)) - 2) < 0.11, nt2)
        # ---------- B6 · prestador pelo formulário: não conta horas-homem da fazenda (Resumo = Operadores no formulário do recurso) ----------
        abre('#saf=S2627&passo=operacoes'); expande('op:Adubação a lanço'); clica('at:Adubação a lanço|Adubação de cobertura'); botao('+ Outra configuração para Adubação de cobertura', PAINEL); campo('conj_id', 'prestador'); time.sleep(.2)
        pess0 = valor('pess'); campo('nome', 'Prestador lanço'); campo('maq', '250'); r_ = salvar()
        botao('Resumo da safra'); pn = painel(); esc()
        hh = re.search(r'([\d.,]+) horas-homem', pn); botao('Capacidade por mês ▾'); clica('oper'); hs = valor('hs_c') or ''
        chk('B6a prestador incluído pelo formulário (Pessoas vinha 1, copiado): horas-homem do Resumo = horas de Operadores na safra', bool(hh) and hs.startswith(fmt(float(hh.group(1).replace('.', '').replace(',', '.')), 1) + ' h'), [pess0, hh and hh.group(1), hs])
        chk('B6b o aviso diz que a tarifa do prestador é a de Máquina e que implemento e pessoas da fazenda não entram', 'Prestador: a tarifa é a de Máquina (R$ 250,00/h)' in (r_[1] or ''), r_)
        chk('B7 sem erros de JS', erros() == '', erros())
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK)+len(FAIL)} OK' + (' · falhas: ' + ' | '.join(FAIL) if FAIL else ''), flush=True)
sys.exit(0 if not FAIL else 1)
