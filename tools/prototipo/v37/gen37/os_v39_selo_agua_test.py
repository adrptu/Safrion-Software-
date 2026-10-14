# -*- coding: utf-8 -*-
"""O.S. · selo do cabeçalho e ordens de água (verificador v39, itens 3 e 7, revisto pela decisão do proprietário de 01/10/2026).
A cor do selo segue o filtro (vermelho só com impedidas; as impedidas são as ordens abertas com selo vermelho). As ordens só com água
(OS-0419/0422/0423) não são O.S. agrícola: ficam fora da lista, do Kanban, dos chips e do selo da OS.dc.html; a fertirrigação OS-0418
fica na O.S. com produto, requisição e liberação da agrônoma. As de água vivem na IR-03 (Ordens de irrigação), cada fato uma vez por
linha, e a OS-0419 abre na IR-03det. Lê a _render/ como está (não copia project/ por cima)."""
import sys, os, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
from comp_lib import troca_visao   # VISOES-1: troca de visão pelo seletor (data-visao), não pelo texto
T = Os(copiar=False); J = T.J
VERM, AMAR = 'rgb(180, 35, 24)', 'rgb(138, 90, 0)'
AGUA = ('OS-0419', 'OS-0422', 'OS-0423')
def filtro(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def hdr(): return J("(()=>{let s=document.querySelector('header h1').nextElementSibling; while(s&&s.classList&&s.classList.contains('g2-info')) s=s.nextElementSibling;    const c=s&&s.firstElementChild; return c?[c.innerText.trim(),getComputedStyle(c).color,getComputedStyle(c).backgroundColor]:['','',''];})()")
def nimp(t):   # '2 em execução · 3 impedidas' -> 3; 'nenhuma impedida' -> 0
    m = re.search(r'(\d+) impedidas?$', t); return int(m.group(1)) if m else (0 if t.endswith('nenhuma impedida') else None)
# ordens abertas (fora de Encerradas/Canceladas) com selo vermelho na linha
IMP = """[...document.querySelectorAll('[role=row].g2ed')].filter(r=>!/Encerrad|Cancelad/.test(r.innerText))
  .filter(r=>[...r.querySelectorAll('span')].some(s=>!s.children.length&&s.innerText.trim()&&getComputedStyle(s).color==='rgb(180, 35, 24)'))
  .map(r=>r.innerText.split('\\n')[0].trim())"""
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def kanban(): return J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].map(b=>b.innerText.split('\\n')[0].trim())") or []
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def agua_txt(): return re.findall(r'OS-04(?:19|22|23)', J("document.body.innerText") or '')
def clica(t): J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.4)
def cor(id_, t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); const s=r&&[...r.querySelectorAll('span')].filter(x=>x.innerText.trim().startsWith({json.dumps(t)})).pop(); return s?getComputedStyle(s).color:'';}})()") or ''
ERR = []
try:
    T.abrir(wait=1.3)
    t, c, bg = hdr(); imp = J(IMP)
    T.ok(t.endswith('3 impedidas') and c == VERM and sorted(imp) == ['OS-0418', 'OS-0420', 'OS-0431'],
         'Santa Rita · todas as safras: selo vermelho com 3 impedidas = ordens abertas com selo vermelho (OS-0418 sem lote de Ureia, OS-0420, OS-0431), nenhuma de água', (t, c, imp))
    filtro('Filtrar por safra', '2025/26'); t, c, bg = hdr()
    T.ok(t == '0 em execução · nenhuma impedida' and c != VERM and bg != 'rgb(253, 232, 230)', 'safra 2025/26: nenhuma impedida sem vermelho', (t, c, bg))
    filtro('Filtrar por safra', 'Todas'); filtro('Filtrar por fazenda', 'Boa Vista'); t, c, bg = hdr()
    T.ok(t == '0 em execução · nenhuma impedida' and c != VERM, 'Boa Vista: nenhuma impedida sem vermelho', (t, c))
    filtro('Filtrar por fazenda', 'Santa Rita'); t, c, bg = hdr(); n_sr = nimp(t)
    T.ok(c == VERM and n_sr == 3, 'voltar a Santa Rita: vermelho de novo', (t, c))
    filtro('Filtrar por fazenda', 'Lagoa Grande'); t_lg, c_lg, _ = hdr(); imp_lg = J(IMP); n_lg = nimp(t_lg)
    filtro('Filtrar por fazenda', 'Todas'); t_td, c_td, _ = hdr(); n_td = nimp(t_td)
    T.ok(bool(n_lg) and n_lg == len(imp_lg) and c_lg == VERM and n_td == n_sr + n_lg and c_td == VERM,
         'Lagoa Grande e Fazenda Todas: o selo segue o filtro (vermelho; impedidas = ordens abertas com selo vermelho; Todas = Santa Rita + Lagoa Grande)', (t_lg, imp_lg, t_td, c_td))
    ERR += T.erros()
    # ---- água fora da O.S. (decisão de 01/10) ----
    filtro('Filtrar por fazenda', 'Santa Rita'); L = ids(); ch = chips()
    T.ok(len(L) == 10 and ch[:1] == [f'Todas {len(L)}'] and not set(AGUA) & set(L) and not agua_txt(),
         'Santa Rita · todas as safras: 10 ordens agrícolas, chip Todas = linhas, sem OS-0419/0422/0423 na lista nem no texto da tela', (L, ch[:1], agua_txt()))
    troca_visao(J,'kanban'); K = kanban(); a_kb = agua_txt(); troca_visao(J,'lista')
    T.ok(sorted(K) == sorted(L) and not set(AGUA) & set(K) and not a_kb, 'Kanban de Santa Rita: os mesmos 10 cartões da lista, nenhum de água', (K, a_kb))
    # ---- fertirrigação OS-0418 fica na O.S. ----
    l = T.linha('OS-0418'); T.ordem('OS-0418'); p = T.pan(); ins = p[p.find('INSUMOS'):p.find('RECURSOS')]
    T.ok('Fertirrigação' in l and 'A liberar' in l and 'Ana (agrônoma)' in p and 'Ureia 45%' in ins and 'REQ-' in ins and 'Liberar bloqueado: sem lote de Ureia 45%' in p,
         'OS-0418 (fertirrigação) continua na O.S.: produto Ureia 45% com requisição em Insumos, liberação pela agrônoma, liberar bloqueado sem lote', (l, ins[:200], p[:200]))
    T.fechar(); ERR += T.erros()
    # ---- ordens de água na IR-03: cada fato uma vez por linha ----
    T.c.goto(f'http://127.0.0.1:{T.p}/IR-03.dc.html', wait=1.0)
    # revisão TABR (09/10/2026): na Pendência o chip diz o tipo ("Conflito") e o detalhe ("parada da B3 · 14:00–15:00") vai na dica e no texto do
    # leitor de tela (A11); avisos (a nota de ET) e passadas saíram da grade da IR-03 para o detalhe da ordem (A1): cada fato continua uma vez só
    l3 = T.linha('OS-0423')
    l2 = T.linha('OS-0422')
    l9 = T.linha('OS-0419'); c23 = cor('OS-0423', 'Conflito'); c22 = cor('OS-0422', 'Janela a definir'); ERR += T.erros()
    def det(oid): T.c.goto(f'http://127.0.0.1:{T.p}/IR-03det.dc.html#{oid}', wait=1.0); return J("document.body.innerText") or ''
    d23 = det('OS-0423'); d22 = det('OS-0422')
    T.ok(l3.count('Conflito') == 1 and l3.count('parada da B3') == 1 and c23 == VERM and l3.count('4,0 mm') == 1 and 'estimativa por et' not in l3.lower() and 'estimativa por et' in d23.lower(),
         'IR-03 · OS-0423: selo vermelho Conflito (parada da B3 na dica) e lâmina 4,0 mm uma vez na linha; a nota de ET no detalhe (formato irrMm: 2 casas, mínimo 1)', (l3, c23, d23[:300]))
    T.ok(l2.count('Janela a definir') == 1 and c22 == AMAR and l2.count('13,5 mm') == 1 and '13,5 mm brutos em 2 passadas' in d22,
         'IR-03 · OS-0422: selo amarelo Janela a definir e 13,5 mm uma vez na linha; as 2 passadas no detalhe da ordem', (l2, c22, d22[:300]))
    T.c.goto(f'http://127.0.0.1:{T.p}/IR-03det.dc.html', wait=1.0); b = J("document.body.innerText") or ''
    T.ok('Liberadas' in l9 and l9.count('10,81 mm') == 1 and J("document.querySelector('h1').innerText.trim()") == 'OS-0419 · Irrigação · Pivô 2' and '10,81 mm' in b
         and 'olítica' not in b and 'agrônom' not in b, 'IR-03 · OS-0419 liberada com 10,81 mm uma vez na linha; IR-03det abre a OS-0419 sem citar política nem agrônomo', (l9, b[:160]))
    ERR += T.erros()
    T.ok(not ERR, 'sem erro JS (O.S., IR-03 e IR-03det)', ERR)
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
