# -*- coding: utf-8 -*-
"""O.S. · selo do cabeçalho e painéis de água (verificador v39, itens 3 e 7): a cor do selo segue o filtro (vermelho só com impedidas);
nos painéis das ordens de água cada fato aparece uma vez (nota de ET só no Próximo passo; lâmina só em Insumos)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
T = Os(); J = T.J
VERM = 'rgb(180, 35, 24)'
def filtro(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def hdr(): return J("(()=>{const s=document.querySelector('header h1').nextElementSibling; const c=s&&s.firstElementChild; return c?[c.innerText.trim(),getComputedStyle(c).color,getComputedStyle(c).backgroundColor]:['','',''];})()")
def secao(p, a, b):
    i = p.find(a); j = p.find(b, i + 1) if b else -1
    return p[i:j] if j > i else p[i:]
try:
    T.abrir(wait=1.3)
    t, c, bg = hdr()
    T.ok(t.endswith('2 impedidas') and c == VERM, 'Santa Rita · todas as safras: selo vermelho com 2 impedidas', (t, c))
    filtro('Filtrar por safra', '2025/26'); t, c, bg = hdr()
    T.ok(t == '0 em execução · nenhuma impedida' and c != VERM and bg != 'rgb(253, 232, 230)', 'safra 2025/26: nenhuma impedida sem vermelho', (t, c, bg))
    filtro('Filtrar por safra', 'Todas'); filtro('Filtrar por fazenda', 'Boa Vista'); t, c, bg = hdr()
    T.ok(t == '0 em execução · nenhuma impedida' and c != VERM, 'Boa Vista: nenhuma impedida sem vermelho', (t, c))
    filtro('Filtrar por fazenda', 'Santa Rita'); t, c, bg = hdr()
    T.ok(c == VERM, 'voltar a Santa Rita: vermelho de novo', (t, c))
    # ---- OS-0423: nota de ET uma vez (Próximo passo) ----
    T.ordem('OS-0423'); p = T.pan(); pl = p.lower()
    T.ok(pl.count('estimativa por et') == 1 and 'Estimativa por ET · sonda sem dado (não bloqueia).' in secao(p, 'PRÓXIMO PASSO', 'ATIVIDADE'), 'OS-0423: nota de ET só no Próximo passo', pl.count('estimativa por et'))
    T.ok(p.count('4,0 mm') == 1 and '4,0 mm' in secao(p, 'INSUMOS', 'RECURSOS'), 'OS-0423: lâmina só em Insumos', p.count('4,0 mm'))
    T.ok(p.count('14:00–15:00') + p.count('14:00 às 15:00') == 1, 'OS-0423: conflito da B3 citado uma vez', p[p.find('SITUAÇÃO ATUAL'):][:200])
    T.fechar()
    # ---- OS-0422: lâmina uma vez (Insumos) ----
    T.ordem('OS-0422'); p = T.pan()
    T.ok(p.count('6,75 mm') == 1 and p.count('13,5 mm') == 1 and '6,75 mm' in secao(p, 'INSUMOS', 'RECURSOS'), 'OS-0422: 13,5 mm em 2 passadas de 6,75 mm só em Insumos', (p.count('6,75 mm'), p.count('13,5 mm')))
    T.ok('Definir janela' in p and 'João (irrigante)' in p and 'agrônom' not in p, 'OS-0422: próximo passo Definir janela com João, sem agrônomo', p[p.find('PRÓXIMO'):][:240])
    T.fechar()
    # ---- OS-0419: lâmina uma vez ----
    T.ordem('OS-0419'); p = T.pan()
    T.ok(p.count('10,81 mm') == 1 and 'olítica' not in p, 'OS-0419: 10,81 mm uma vez, sem citar política', p.count('10,81 mm'))
    T.fechar()
    T.ok(not T.erros(), 'sem erro JS', T.erros())
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
