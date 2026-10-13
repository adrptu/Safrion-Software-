# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Cadastros (CD-01..CD-07 e CD-01det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("160,0 ha", "R$ 14,49/ha"),
"Custo R$/h" e "Custo R$/ha", filtro e ordenação em todas as colunas, filtro pelo texto da célula, ordem pelo número e pela data,
Situação em chip; 390 px rolando dentro da caixa. Defeitos reproduzidos: outorga aparecia como "Certidão" (CD-01 Água) e a Safra Mamão
da Lagoa Grande aparecia nas parcelas de talhão da Santa Rita (CD-01det). Fluxo do cadastro na grade (CD-03), a 1440 e a 390 px (toque): normal
(salvar o custo e a célula/ordem acompanham), recusa (número inválido não grava) e repetição (salvar de novo não duplica). Vazio continua vazio.
CADUX (09/10/2026, seleção que abre detalhe): as telas viraram mestre → detalhe → painel; cada grade tem até 7 colunas (ESPECIFICACAO §2.2)
com a Situação em 2º lugar, e o que saiu da lista foi para o painel ou para o cabeçalho. Expectativas que mudaram, com o motivo:
  CD-01: abas viraram endereços (#aba=, #faz=); "Parcelas" conta as safras abertas da fazenda (T1: 3); Boa Vista sem safra aberta não
         mostra a coluna; o curso d'água e o "precisa de atenção" da outorga estão no painel do ponto de água (a faixa saiu);
  CD-01det: a ficha de 9 colunas virou o cabeçalho do detalhe (DS-58) numa linha;
  CD-02: tipo de ciclo e unidade de produtividade no mestre (a cultura); largura, velocidade, eficiência, R$/ha e processo no painel e no
         mestre de operações; o filtro de processo virou o filtro de Modo;
  CD-03: com a classe escolhida, as grandezas dela em colunas (Pulverizador: Barra e Tanque); o título ordenado é Potência (Trator);
         a busca é a do mestre; o ativo abre em consulta e "Editar ativo" abre o formulário;
  CD-04: custo-hora e "disponível até" no painel (G1); "Validade da habilitação" virou "Próxima validade"; Acesso ao app com a equipe;
  CD-05: CPF/CNPJ no painel; cobertura = "Grupos de insumo" do mestre, com Itens no CD-06;
  CD-06: natureza de custo no cabeçalho do grupo (o filtro dela virou o de Controle); "Unidade" virou "Unidade-base";
  CD-07: Origem, Vínculos, Fim da vigência e TOP no painel (A13); filtro por "No rascunho".
Uso: python3 tabelas_cad_test.py [pasta de capturas]   (< 3 min)"""
import sys, os, re, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from tabelas_lib import Grade, limpa, num, un_ok, instante, crescente
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''), flush=True)

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))
ERRS = []
def abre(pg, w=1.4):
    try: e = J("window.__errs") or []
    except Exception: e = []
    ERRS.extend(e); c.goto(f'http://127.0.0.1:{p}/{pg}', w)
def aba(nome):
    r = J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.offsetParent&&b.innerText.trim().startsWith({json.dumps(nome)})); if(!b) return false; b.click(); return true;}})()"); time.sleep(.6); return r
def grupos(g):
    """linhas da árvore com a marca de grupo (linha com seta)."""
    return J(f"[...([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}].querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[!!r.querySelector('button[aria-label^=\"Expandir\"],button[aria-label^=\"Recolher\"]'),[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim())])") or []
def por_grupo(g, col):
    """valores da coluna nas folhas, um bloco por grupo (a árvore ordena dentro do nível)."""
    hs = g.labels(); k = hs.index(col); out = []; cur = None
    for grp, cells in grupos(g):
        if grp: cur = []; out.append(cur)
        elif cur is not None: cur.append(cells[k])
    return [b for b in out if len(b) > 1]
def tf03(nome, g, esperado, ficha=False, extra=()):
    """TF03 da grade: colunas exatas, uma variável por coluna, filtro e ordem em todas, unidade junto do valor, situação em chip."""
    hs = g.heads(); ls = [h for h, _ in hs]
    chk(f'{nome}: colunas {" | ".join(esperado)}', ls == esperado, ls)
    chk(f'{nome}: nenhum rótulo composto (" · ", " / ") e custo como "Custo R$/h"/"Custo R$/ha"',
        not any(' · ' in h or ' / ' in h for h in ls) and all(h.startswith('Custo R$/') for h, u in hs if u.startswith('R$/')), ls)
    if not ficha:
        m = g.com_menu(); chk(f'{nome}: filtro (▾) e ordenação no título em todas as {len(m)} colunas', m and all(m), m)
    d = g.dicts(); ruins = [(h, r.get(h)) for h, u in hs if u for r in d if not un_ok(r.get(h, ''), u, extra)]
    chk(f'{nome}: unidade junto do valor nas colunas com unidade ({", ".join(h + " " + u for h, u in hs if u) or "nenhuma"})', not ruins, ruins[:4])
    if 'Situação' in ls or 'Situação do papel' in ls:
        col = 'Situação' if 'Situação' in ls else 'Situação do papel'; ch = [x for x in g.chips(col) if x is not None]
        chk(f'{nome}: {col} em chip em todas as linhas com valor ({len(ch)})', ch and all(ch), g.chips(col)[:6])
    return d

def alvo(txt):
    """CADUX (BOT-07): o registro abre pelo alvo nomeado da 1ª célula da linha, em consulta."""
    return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].filter(x=>x.offsetParent).find(x=>x.innerText.replace(/\\s+/g,' ').trim().indexOf({json.dumps(txt)})===0); const a=r&&r.querySelector('.g2alvo'); if(!a) return false; a.click(); return true;}})()")
def painel(): return J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
def botao_painel(t): J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.45)
def fecha_painel(): J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.35)
def todas():
    """a 390 px a tela abre no mestre: escolhe o 1º item ("Todas…") para chegar à grade."""
    if not J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length"):
        J("(()=>{const b=[...document.querySelectorAll('.cmd-lista .cmd-it')].find(b=>b.getClientRects().length); b&&b.click();})()"); time.sleep(1.0)   # a 1ª coluna presa se ajusta depois do desenho
def busca_mestre(q):
    J(f"""(()=>{{const i=document.querySelector('#mx-q'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(q)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.5)

def fluxo_custo(g, tam, val, cel):
    """CD-03: salvar o custo do Trator 03 → célula e ordem por custo acompanham (normal); "abc" mostra "Use um número" e não grava (recusa);
    salvar de novo sem mudar não duplica a linha nem muda o valor (repetição). CADUX: o ativo abre em consulta e "Editar ativo" abre o formulário."""
    def abre_linha(nome): alvo(nome); time.sleep(.5); botao_painel('Editar ativo')
    def campo(fid, v): J(f"""(()=>{{const i=document.querySelector('#{fid}'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.2)
    def salvar(): J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    linha = lambda: next((r for r in g.dicts() if r.get('Ativo') == 'Trator 03'), {})
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', val); salvar(); cons = painel(); fecha_painel(); t3 = linha()
    g.ordena('Custo R$/h', desc=True); ordem = [r.get('Ativo') for r in g.dicts()]; ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk(f'CD-03 fluxo {tam} (normal): salvar {val} volta à consulta do Trator 03; célula "{cel}" e a ordem por custo põe o Trator 03 entre os de 180 e os de 150',
        cons.replace('‹ Todos os ativos ', '', 1).startswith('Ativo · Trator 03') and t3.get('Custo R$/h') == cel and crescente(ch, True) and ordem.index('Trator 03') == ordem.index('Trator 02') + 1, (cons[:40], t3.get('Custo R$/h'), ordem[:6]))
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', 'abc'); salvar()
    err = painel()
    botao_painel('Cancelar'); botao_painel('Descartar alterações'); fecha_painel()
    chk(f'CD-03 fluxo {tam} (recusa): custo "abc" mostra "Use um número" e não grava (célula segue {cel})', 'Use um número' in err and linha().get('Custo R$/h') == cel, (err[-160:], linha().get('Custo R$/h')))
    abre_linha('Trator 03'); salvar(); fecha_painel(); n3 = [r.get('Ativo') for r in g.dicts()].count('Trator 03')
    chk(f'CD-03 fluxo {tam} (repetição): salvar de novo sem mudar não duplica a linha nem muda o valor', n3 == 1 and linha().get('Custo R$/h') == cel, n3)

try:
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= CD-01 Talhões (Todas as fazendas: árvore fazenda › talhão) =================
    abre('CD-01.dc.html#aba=talhoes'); g = Grade(J, 0)
    d = tf03('CD-01 Talhões (todas)', g, ['Fazenda › talhão', 'Situação', 'Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas'])
    t1 = next((r for r in d if r.get('Fazenda › talhão') == 'T1'), {}); p1 = next((r for r in d if r.get('Fazenda › talhão') == 'P1'), {})
    pv = next((r for r in d if r.get('Fazenda › talhão', '').startswith('PV')), {})
    # CADUX (§2.1): "Parcelas" conta as parcelas das safras abertas da fazenda (Santa Rita: 2026/27 e Safrinha 2027), não só da 2026/27
    chk('CD-01: T1 Sequeiro | 312,0 ha | 312,4 ha | +0,1 % | 3 parcelas nas safras abertas (número) | Em dia; P1 Pivô central',
        [t1.get(k) for k in ('Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas', 'Situação')] == ['Sequeiro', '312,0 ha', '312,4 ha', '+0,1 %', '3', 'Em dia'] and p1.get('Sistema') == 'Pivô central', (t1, p1))
    chk('CD-01: pivô da Lagoa Grande (círculo do KML) dito uma vez, na Situação; Polígono fica "—"', pv.get('Polígono') == '—' and pv.get('Situação') == 'Círculo do KML', pv)
    g.ordena('Área cultivável', desc=True); bl = por_grupo(g, 'Área cultivável')
    chk('CD-01: ordenar Área cultivável (decrescente) pelo número dentro de cada fazenda', bl and all(crescente([num(x) for x in b], True) for b in bl), [b[:4] for b in bl])
    g.filtra('Sistema', ['Pivô central']); s1 = {r.get('Sistema') for r in g.dicts(True)}
    chk('CD-01: filtro Sistema = Pivô central (texto da célula) deixa só pivôs', s1 == {'Pivô central'}, s1)
    limpa(J); shot('cd01-talhoes-1440')
    # fazenda escolhida no mestre: a coluna da fazenda sai; Boa Vista (sem safra aberta) não mostra Parcelas (§2.1)
    abre('CD-01.dc.html#faz=SR&aba=talhoes'); tf03('CD-01 Talhões (Santa Rita)', Grade(J, 0), ['Talhão', 'Situação', 'Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas'])
    abre('CD-01.dc.html#faz=BV&aba=talhoes'); lb = Grade(J, 0).labels()
    chk('CD-01 Boa Vista (sem safra aberta): sem a coluna Parcelas', lb == ['Talhão', 'Situação', 'Sistema', 'Área cultivável', 'Polígono', 'Diferença'], lb)
    # ================= CD-01 Água (todas as fazendas, com a coluna Fazenda) =================
    abre('CD-01.dc.html#aba=agua'); g = Grade(J, 0)
    d = tf03('CD-01 Água', g, ['Ponto de água', 'Situação', 'Documento', 'Uso', 'Vazão', 'Vencimento', 'Fazenda'])
    a1 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 1 ')), {}); a6 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 6 ')), {})
    chk('CD-01 Água (defeito): a outorga do ponto 1 aparece como Outorga (antes "Certidão"); o ponto 6 é Certidão', a1.get('Documento') == 'Outorga' and a6.get('Documento') == 'Certidão', (a1, a6))
    chk('CD-01 Água: ponto 1 = Captação superficial | 180 m³/h | 30/04/2031 | Vigente | Lagoa Grande',
        [a1.get(k) for k in ('Uso', 'Vazão', 'Vencimento', 'Situação', 'Fazenda')] == ['Captação superficial', '180 m³/h', '30/04/2031', 'Vigente', 'Lagoa Grande'], a1)
    # CADUX: o curso d'água e o "precisa de atenção" ficam no painel do ponto (a faixa saiu; o Próximo passo diz o documento certo)
    alvo('Ponto de água 1 '); time.sleep(.5); p_a1 = painel(); fecha_painel()
    alvo('Ponto de água 3 '); time.sleep(.5); p_a3 = painel(); fecha_painel()
    chk('CD-01 Água: o painel do ponto 1 traz o curso d’água (Rio A)', 'Rio A (demonstração)' in p_a1, p_a1[:300])
    chk('CD-01 Água (defeito): o painel do ponto vencido diz Outorga SINT-003/0000 (antes "Certidão SINT-003/0000")', 'Outorga SINT-003/0000' in p_a3 and 'Certidão SINT-003' not in p_a3, p_a3[:400])
    g.ordena('Vazão'); vz = [x for x in g.col('Vazão') if x != '—']; m3 = [num(x) * (3.6 if x.endswith('L/s') else 1) for x in vz]
    chk('CD-01 Água: ordenar Vazão pelo valor em m³/h (L/s × 3,6), com a unidade do documento na célula', crescente(m3) and any(x.endswith('L/s') for x in vz), vz)
    g.ordena('Vencimento'); vc = [instante(x) for x in g.col('Vencimento') if x != '—']
    chk('CD-01 Água: ordenar Vencimento por data (anos diferentes)', crescente(vc) and len({x[0] for x in vc}) > 2, g.col('Vencimento')[:6])
    g.filtra('Documento', ['Certidão']); dc = g.dicts()
    chk('CD-01 Água: filtro Documento = Certidão → só certidões (4)', len(dc) == 4 and all(r.get('Documento') == 'Certidão' for r in dc), [r.get('Ponto de água') for r in dc])
    limpa(J)
    abre('CD-01.dc.html#aba=ambiental'); tf03('CD-01 Ambiental', Grade(J, 0), ['Área ambiental', 'Tipo', 'Área', 'Fazenda'])
    # ================= CD-01det (a ficha de 1 linha virou o cabeçalho do detalhe, DS-58) =================
    abre('CD-01det.dc.html#talhao=T1'); gp = Grade(J, 0)
    sub = J("(document.querySelector('main .cmd-ds')||{innerText:''}).innerText") or ''
    chk('CD-01det: o cabeçalho do talhão diz Santa Rita · Sequeiro · 312,0 ha cultivável · polígono 312,4 ha (v3) numa linha (antes a ficha de 9 colunas)',
        sub.startswith('Santa Rita · Sequeiro · 312,0 ha cultivável · polígono 312,4 ha (v3)'), sub)
    dp = tf03('CD-01det parcelas', gp, ['Safra › parcela', 'Tipo', 'Cultura', 'Cultivar', 'Área', 'Livre', 'Plantio', 'Situação'])
    gs = [cells[0] for grp, cells in grupos(gp) if grp]
    chk('CD-01det (defeito): T1 da Santa Rita só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', gs and not any('Mamão' in x for x in gs) and 'Safra 2026/27' in gs, gs)
    t1b = next((r for r in dp if r.get('Safra › parcela') == 'T1-B'), {}); sfr = next((r for r in dp if r.get('Safra › parcela') == 'Safrinha 2027'), {})
    chk('CD-01det: T1-B Parcela | Soja | 62 X | 152,0 ha | 25/10/2026 | Sem polígono; Safrinha 2027 livre 152 ha (número)',
        [t1b.get(k) for k in ('Tipo', 'Cultura', 'Cultivar', 'Área', 'Plantio', 'Situação')] == ['Parcela', 'Soja', '62 X', '152,0 ha', '25/10/2026', 'Sem polígono'] and sfr.get('Livre') == '152 ha' and sfr.get('Situação') == 'Rascunho', (t1b, sfr))
    shot('cd01det-1440')
    # ================= CD-02 (culturas → cultivares; tipo de ciclo e unidade de produtividade no mestre) =================
    abre('CD-02.dc.html'); g = Grade(J, 0)
    d = tf03('CD-02 Culturas', g, ['Cultura › cultivar', 'Situação', 'Ciclo', 'Item de semente', 'Cultivos'])
    w58 = next((r for r in d if r.get('Cultura › cultivar') == '58 W'), {})
    mestre = J("[...document.querySelectorAll('.cmd-lista .cmd-it')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
    mam = next((x for x in mestre if x.startswith('Mamão Formosa')), '')
    chk('CD-02: 58 W = 118 dias | 6 cultivos (número); no mestre, Soja "Anual · sc de 60 kg/ha" e Mamão Formosa em t/ha/ano (DEC-0510-03)',
        [w58.get(k) for k in ('Ciclo', 'Cultivos')] == ['118 dias', '6'] and 't/ha/ano' in mam and any(x.startswith('Soja') and 'Anual · sc de 60 kg/ha' in x for x in mestre), (w58, mestre))
    J("(()=>{const b=[...document.querySelectorAll('.cmd-lista .cmd-it')].find(b=>b.innerText.trim().startsWith('Mamão Formosa')); b&&b.click();})()"); time.sleep(.6)
    fl = [r.get('Cultura › cultivar') or r.get('Cultivar') for r in Grade(J, 0).dicts(True)]
    chk('CD-02: escolher Mamão Formosa no mestre deixa só a cultivar Formosa (antes: filtro t/ha/ano na coluna)', fl == ['Formosa'], fl)
    abre('CD-02.dc.html'); g = Grade(J, 0); g.ordena('Ciclo', desc=True); bl = por_grupo(g, 'Ciclo')
    chk('CD-02: ordenar Ciclo (dias) pelo número dentro da cultura', bl and all(crescente([num(x) for x in b], True) for b in bl), bl[:2])
    abre('CD-02.dc.html#aba=operacoes'); g = Grade(J, 0)
    d = tf03('CD-02 Rendimentos', g, ['Operação › conjunto', 'Situação', 'Cultura', 'Modo', 'Rendimento', 'Custo R$/h', 'Fonte'])
    pz = next((r for r in d if r.get('Operação › conjunto', '').startswith('Trator 02')), {})
    chk('CD-02: pulverização Largura × velocidade | 21,60 ha/h | R$ 313,00/h | Medição local (largura, velocidade, eficiência e R$/ha no painel, §2.2)',
        [pz.get(k) for k in ('Modo', 'Rendimento', 'Custo R$/h', 'Fonte')] == ['Largura × velocidade', '21,60 ha/h', 'R$ 313,00/h', 'Medição local'], pz)
    g.filtra('Modo', ['Informado']); fl = {r.get('Modo') for r in g.dicts(True)}
    chk('CD-02: filtro Modo = Informado vale no conjunto', fl == {'Informado'} and len(g.dicts(True)) >= 1, [r.get('Operação › conjunto') for r in g.dicts(True)])
    limpa(J)
    # ================= CD-03 (classe → ativos; com a classe escolhida, as grandezas dela) =================
    abre('CD-03.dc.html'); g = Grade(J, 0)
    d = tf03('CD-03 Ativos', g, ['Ativo', 'Situação', 'Classe', 'Modelo', 'Custo R$/h', 'Próxima calibração', 'Conjuntos'])
    pv = next((r for r in d if r.get('Ativo') == 'Pulverizador PJ-3030'), {})
    chk('CD-03: pulverizador Uniport 3030 | R$ 95,00/h | 14/12/2026 | Apta',
        [pv.get(k) for k in ('Modelo', 'Custo R$/h', 'Próxima calibração', 'Situação')] == ['Uniport 3030', 'R$ 95,00/h', '14/12/2026', 'Apta'], pv)
    g.ordena('Custo R$/h', desc=True); ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk('CD-03: ordenar Custo R$/h (decrescente) pelo número', crescente(ch, True), g.col('Custo R$/h')[:5])
    g.ordena('Próxima calibração'); cl = g.col('Próxima calibração'); dv = [instante(x) for x in cl if x != '—']
    chk('CD-03: ordenar Próxima calibração por data; sem data no fim', crescente(dv) and cl[len(dv):] == ['—'] * (len(cl) - len(dv)), cl)
    g.filtra('Classe', ['Irrigação']); fl = [r.get('Ativo') for r in g.dicts()]
    chk('CD-03: filtro Classe = Irrigação → as 3 bombas/setores', len(fl) == 3 and all(r.get('Classe') == 'Irrigação' for r in g.dicts()), fl)
    # recusa e repetição do filtro: vazio continua vazio; o mesmo filtro duas vezes dá o mesmo recorte (CADUX: a busca é a do mestre)
    busca_mestre('Silo')
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('CD-03 (recusa): Classe = Irrigação + busca "Silo" → nenhuma linha e o aviso "Nenhuma linha corresponde aos filtros" (sem voltar a todas)', g.dicts() == [] and vaz, len(g.dicts()))
    busca_mestre(''); limpa(J); n0 = len(g.dicts()); g.filtra('Classe', ['Trator']); a1 = [r.get('Ativo') for r in g.dicts()]; g.filtra('Classe', ['Trator']); a2 = [r.get('Ativo') for r in g.dicts()]
    chk('CD-03 (repetição): o mesmo filtro duas vezes dá o mesmo recorte; Limpar filtros volta às 15', a1 == a2 and len(a1) == 4 and n0 == 15, (a1, a2, n0))
    abre('CD-03.dc.html#classe=pulverizador'); gpz = Grade(J, 0)
    dz = tf03('CD-03 Pulverizador', gpz, ['Ativo', 'Situação', 'Barra', 'Tanque', 'Custo R$/h', 'Próxima calibração', 'Conjuntos'])
    chk('CD-03 Pulverizador: as grandezas da classe em colunas próprias, com a unidade na célula (36 m | 3.000 L)', [dz[0].get(k) for k in ('Barra', 'Tanque')] == ['36 m', '3.000 L'] if dz else False, dz[:1])
    abre('CD-03.dc.html#classe=trator'); g = Grade(J, 0); base = [r.get('Ativo') for r in g.dicts()]   # sem ordem aplicada
    g.cabecalho_ordena('Potência'); cr = [num(x) for x in g.col('Potência') if x != '—']
    chk('CD-03 Trator: um clique no título Potência ordena crescente pelo número', crescente(cr), g.col('Potência')[:6])
    for _ in range(2): g.cabecalho_ordena('Potência')
    chk('CD-03 (repetição): três cliques no título (crescente → decrescente → sem ordem) voltam à ordem original', [r.get('Ativo') for r in g.dicts()] == base, base[:4])
    # fluxo do cadastro: salvar o custo do Trator 03 → célula e ordem acompanham; número inválido não grava; salvar de novo não duplica
    abre('CD-03.dc.html'); g = Grade(J, 0); fluxo_custo(g, '1440', '172,5', 'R$ 172,50/h')
    shot('cd03-1440')
    # ================= CD-04 (equipe → pessoas; o custo-hora sai da lista, G1) =================
    abre('CD-04.dc.html'); g = Grade(J, 0)
    d = tf03('CD-04 Pessoas', g, ['Pessoa', 'Situação', 'Habilidades', 'Vínculo', 'Habilitação', 'Próxima validade', 'Equipe'], extra=())
    lu = next((r for r in d if r.get('Pessoa') == 'Lucas'), {})
    chk('CD-04: Lucas Campo 2 | Safrista | NR-31 | 15/08/2026 | Não alocável em O.S. (custo e disponibilidade no painel)',
        [lu.get(k) for k in ('Equipe', 'Vínculo', 'Habilitação', 'Próxima validade', 'Situação')] == ['Campo 2', 'Safrista', 'NR-31', '15/08/2026', 'Não alocável em O.S.'] and 'Custo R$/h' not in g.labels(), lu)
    rr = g.rotulos('Habilidades')
    chk('CD-04: o filtro de Habilidades oferece cada habilidade (não a lista inteira da célula)', rr and 'Operar trator' in rr and not any(',' in x for x in rr), rr)
    g.filtra('Habilidades', ['Operar trator']); fl = sorted(r.get('Pessoa') for r in g.dicts())
    chk('CD-04: filtro Habilidades = Operar trator → Beto, Carlos, Lucas, Marcos (pertinência, não texto)', fl == ['Beto', 'Carlos', 'Lucas', 'Marcos'], fl)
    limpa(J); g.ordena('Próxima validade'); vh = [instante(x) for x in g.col('Próxima validade') if instante(x)]
    chk('CD-04: ordenar Próxima validade por data', crescente(vh), g.col('Próxima validade'))
    abre('CD-04.dc.html#eq=e2'); lb = Grade(J, 0).labels()
    chk('CD-04 Campo 1: com a equipe escolhida, "Acesso ao app" entra no lugar de Equipe', lb == ['Pessoa', 'Situação', 'Habilidades', 'Vínculo', 'Habilitação', 'Próxima validade', 'Acesso ao app'], lb)
    # ================= CD-05 (papel → parceiros; Grupos de insumo em consulta) =================
    abre('CD-05.dc.html'); g = Grade(J, 0)
    d = tf03('CD-05 Parceiros', g, ['Parceiro', 'Situação do papel', 'Papéis', 'Contato', 'E-mail', 'WhatsApp', 'Canais autorizados'])
    sv = next((r for r in d if r.get('Parceiro') == 'Sementes Vale'), {}); cv = next((r for r in d if r.get('Parceiro') == 'Coop. Vale'), {})
    chk('CD-05: Sementes Vale WhatsApp 65 99555-6677 "não autorizado" (Canais = E-mail); Coop. Vale com dois papéis e dois estados',
        sv.get('WhatsApp') == '65 99555-6677 não autorizado' and sv.get('Canais autorizados') == 'E-mail' and cv.get('Papéis') == 'Fornecedor, Cliente' and cv.get('Situação do papel') == 'Homologado Limite vigente', (sv, cv))
    g.filtra('Canais autorizados', ['WhatsApp']); fl = g.dicts()
    chk('CD-05: filtro Canais autorizados = WhatsApp (por item da lista)', fl and all('WhatsApp' in r.get('Canais autorizados', '') for r in fl) and len(fl) < len(d), len(fl))
    limpa(J)
    abre('CD-05.dc.html#papel=cliente'); g = Grade(J, 0)
    dc = tf03('CD-05 Clientes', g, ['Parceiro', 'Situação do papel', 'Papéis', 'Limite de crédito', 'Validade da análise de crédito', 'Contato', 'E-mail'])
    rh = next((r for r in dc if r.get('Parceiro') == 'Rede Hortifrúti BA'), {})
    chk('CD-05 Clientes: Rede Hortifrúti BA R$ 40.000 | 31/08/2026 | Limite vencido', [rh.get(k) for k in ('Limite de crédito', 'Validade da análise de crédito', 'Situação do papel')] == ['R$ 40.000', '31/08/2026', 'Limite vencido'], rh)
    g.ordena('Limite de crédito', desc=True); lc = [num(x) for x in g.col('Limite de crédito')]
    chk('CD-05 Clientes: ordenar Limite de crédito pelo número', crescente(lc, True), g.col('Limite de crédito'))
    abre('CD-05.dc.html#papel=grupos'); g = Grade(J, 0)
    d = tf03('CD-05 Grupos de insumo', g, ['Grupo', 'Situação', 'Fornecedores que recebem cotação', 'Itens no CD-06'])
    se = next((r for r in d if r.get('Grupo') == 'Sementes'), {}); co = next((r for r in d if r.get('Grupo') == 'Combustível'), {})
    chk('CD-05 Grupos de insumo: a Situação diz o estado (o número fica ao lado): Sementes 2 Com concorrência; Combustível 0 Sem fornecedor',
        [se.get('Fornecedores que recebem cotação'), se.get('Situação')] == ['2', 'Com concorrência'] and co.get('Fornecedores que recebem cotação') == '0' and co.get('Situação', '').startswith('Sem fornecedor'), (se, co))
    # ================= CD-06 (grupo → itens; natureza no cabeçalho do grupo) =================
    abre('CD-06.dc.html'); g = Grade(J, 0)
    d = tf03('CD-06 Itens', g, ['Grupo › item', 'Situação', 'Unidade-base', 'Embalagem', 'Controle', 'Preço de referência', 'Data do preço'])
    ds = next((r for r in d if r.get('Grupo › item') == 'Diesel S10'), {}); ca = next((r for r in d if r.get('Grupo › item') == 'Calcário dolomítico'), {})
    chk('CD-06: Diesel S10 L | granel | R$ 6,19/L | 15/09/2026; Calcário dolomítico sem preço (— | Sem preço)',
        [ds.get(k) for k in ('Unidade-base', 'Embalagem', 'Preço de referência', 'Data do preço')] == ['L', 'granel', 'R$ 6,19/L', '15/09/2026'] and ca.get('Preço de referência') == '—' and ca.get('Situação', '').startswith('Sem preço'), (ds, ca))
    pr = [x for x in g.col('Preço de referência', True) if x.startswith('R$')]
    chk('CD-06: preço com a unidade do item na célula ("R$ 22,00/L", "R$ 2,40/kg")', pr and all(re.fullmatch(r'R\$ [\d.]+,\d{2}/(L|kg|un|t|sc 60 kg)', x) for x in pr), pr[:5])
    g.filtra('Controle', ['Lote e validade']); fl = {r.get('Controle') for r in g.dicts(True)}
    chk('CD-06: filtro Controle = Lote e validade vale no item (a natureza de custo foi para o cabeçalho do grupo)', fl == {'Lote e validade'} and len(g.dicts(True)) > 5, len(g.dicts(True)))
    limpa(J); g.ordena('Preço de referência', desc=True); bl = por_grupo(g, 'Preço de referência')
    chk('CD-06: ordenar Preço de referência pelo número dentro do grupo', bl and all(crescente([num(x) for x in b if x != '—'], True) or len([x for x in b if x != '—']) < 2 for b in bl), bl[:2])
    abre('CD-06.dc.html#grp=GR6'); cab = J("(document.querySelector('main .cmd-dc')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    chk('CD-06 Fungicidas: a natureza de custo aparece no cabeçalho do grupo (3.1.02 · Defensivos)', '3.1.02' in cab and 'Defensivos' in cab, cab[:200])
    abre('CD-06.dc.html#grp=locais'); g = Grade(J, 0)
    d = tf03('CD-06 Locais', g, ['Local', 'Fazenda', 'Tipo', 'Capacidade', 'Itens com este local padrão'])
    g.ordena('Capacidade', desc=True); cp = [x for x in g.col('Capacidade') if x != '—']
    chk('CD-06 Locais: capacidade como número com unidade, ordenada pelo número (60.000 sc de 60 kg antes de 15.000 L)', cp == ['60.000 sc de 60 kg', '15.000 L'], cp)
    # ================= CD-07 (dimensão → árvore código › subcódigo; fim da vigência e TOP no painel, A13) =================
    abre('CD-07.dc.html'); g = Grade(J, 0)
    d = tf03('CD-07 Estrutura', g, ['Dimensão › código', 'Nome', 'Situação', 'Início da vigência', 'Conta no ERP', 'No rascunho'])
    n1 = next((r for r in d if r.get('Dimensão › código') == '3.1.01'), {}); e2 = next((r for r in d if r.get('Dimensão › código') == '02'), {})
    chk('CD-07: 3.1.01 Fertilizantes e corretivos | 01/07/2026 | 4.1.1.01 | Mapeado; 02 Novo no rascunho',
        [n1.get(k) for k in ('Nome', 'Início da vigência', 'Conta no ERP', 'Situação')] == ['Fertilizantes e corretivos', '01/07/2026', '4.1.1.01', 'Mapeado'] and e2.get('No rascunho') == 'Novo', (n1, e2))
    g.ordena('Início da vigência', desc=True); bl = por_grupo(g, 'Início da vigência')
    chk('CD-07: ordenar Início da vigência por data dentro da dimensão', bl and all(crescente([instante(x) for x in b], True) or len(set(b)) < 2 for b in bl), bl[:2])
    g.filtra('No rascunho', ['Novo']); fl = {r.get('No rascunho') for r in g.dicts(True)}
    chk('CD-07: filtro No rascunho = Novo → só os códigos novos', fl == {'Novo'} and len(g.dicts(True)) >= 2, [r.get('Dimensão › código') for r in g.dicts(True)])
    limpa(J); shot('cd07-1440')
    abre('CD-07.dc.html#dim=natureza&cod=3.1.01'); p7 = painel()
    chk('CD-07: o painel do 3.1.01 traz o fim da vigência (30/06/2027) e a TOP no ERP (1201)', '30/06/2027' in p7 and '1201' in p7, p7[:400])
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (1440)', not ERRS, ERRS[:3])
    # ================= 390 px =================
    c.aparelho(390, 844, 2, True); r390 = []
    # CD-02 → CD-02#aba=operacoes muda só o endereço (sem recarregar): a grade de Operações, que estava oculta, aparece por troca de
    # estilo; a 1ª coluna dela tem de ser limitada como a de uma página nova (defeito de 09/10: ficava com 344 de 292 px, g2lib presa())
    for pg in ('CD-01.dc.html#faz=SR&aba=talhoes', 'CD-01.dc.html#aba=agua', 'CD-01det.dc.html#talhao=T1', 'CD-02.dc.html', 'CD-02.dc.html#aba=operacoes', 'CD-03.dc.html',
               'CD-04.dc.html', 'CD-05.dc.html', 'CD-05.dc.html#papel=grupos', 'CD-06.dc.html', 'CD-06.dc.html#grp=locais', 'CD-07.dc.html'):
        abre(pg); todas()
        n = J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length") or 0
        if not n: r390.append((pg, False, False, False, False)); continue
        for i in range(n):
            q = Grade(J, i).rola_dentro(); r390.append((pg.split('.')[0] + pg.split('html')[1] + f' #{i}', q.get('pagina'), q.get('cabe') or q.get('rola'), q.get('c0'), q.get('rola')))
        if pg.startswith('CD-03'): shot('cd03-390')
    ruim = [x for x in r390 if not (x[1] and x[2] and x[3])]
    chk(f'390 px: {len(r390)} grades sem rolagem lateral da página; cada grade cabe ou rola dentro da caixa, com a 1ª coluna à vista', r390 and not ruim, ruim or r390[:3])
    # CADUX: com ≤ 7 colunas (§2.2), a maioria cabe; as que não cabem rolam dentro da caixa (conferido acima)
    # fluxo a 390 px, com toque: o mesmo cadastro (normal, recusa, repetição) e o filtro pelo menu da coluna
    abre('CD-03.dc.html'); todas(); g = Grade(J, 0); fluxo_custo(g, '390 px', '165', 'R$ 165,00/h'); limpa(J)
    n0 = len(g.dicts()); g.filtra('Classe', ['Irrigação']); a1 = [r.get('Ativo') for r in g.dicts()]
    chk('CD-03 390 px (filtro): Classe = Irrigação → 3 linhas; Limpar filtros volta a todas', len(a1) == 3 and (limpa(J) or True) and len(g.dicts()) == n0, (a1, n0))
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
