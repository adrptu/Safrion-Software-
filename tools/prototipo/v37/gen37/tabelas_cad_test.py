# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Cadastros (CD-01..CD-07 e CD-01det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("160,0 ha", "R$ 14,49/ha"),
"Custo R$/h" e "Custo R$/ha", filtro e ordenação em todas as colunas, filtro pelo texto da célula, ordem pelo número e pela data,
Situação em chip; 390 px rolando dentro da caixa. Defeitos reproduzidos: outorga aparecia como "Certidão" (CD-01 Água) e a Safra Mamão
da Lagoa Grande aparecia nas parcelas de talhão da Santa Rita (CD-01det). Fluxo do cadastro na grade (CD-03), a 1440 e a 390 px (toque): normal
(salvar o custo e a célula/ordem acompanham), recusa (número inválido não grava) e repetição (salvar de novo não duplica). Vazio continua vazio.
Revisão TABR (09/10/2026): a Situação logo depois da identificação, à vista sem rolar a 1440 e a 1280 px, e as grades cabem na caixa a
1440 px (A1; CD-05 rola só os contatos); capacidade só numa grandeza (CD-03 pelo filtro de Classe, CD-06 pelo filtro Tanque/Silo; A4);
o filtro marcado continua no menu do papel (A5); motivo e verbo da pessoa não alocável e o "Disponível até" vencido em vermelho (A3);
"No rascunho" só com rascunho (A8); calibração a vencer no chip (A10); fonte do rendimento em texto, não chip de estado (A11); a vazão
ordena em m³/h (mutante M-a: tabelas_cad_irr_unit B1 e B1b; a ordem na tela não distingue com os valores do cenário) e a capacidade da classe Irrigação aparece (mutante M-k);
o detalhe do PV01 (Lagoa Grande) mostra a parcela que a lista conta (pré-existente). Colunas que entram e saem (CD-05 papel, CD-03 Classe,
CD-06 Tanque/Silo) ficam sob os cabeçalhos e o cabeçalho não quebra linha (mutante M-e: sem ncol_dinamico a trilha fica menor e cabeçalho e
células quebram juntos; desalinhadas() pega pela ordem das bordas, sonda de 10/10/2026).
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

def fluxo_custo(g, tam, val, cel):
    """CD-03: salvar o custo do Trator 03 → célula e ordem por custo acompanham (normal); "abc" mostra "Use um número" e não grava (recusa);
    salvar de novo sem mudar não duplica a linha nem muda o valor (repetição)."""
    def abre_linha(nome): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(nome)})===0); r&&r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    def campo(fid, v): J(f"""(()=>{{const i=document.querySelector('#{fid}'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.2)
    def salvar(): J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    linha = lambda: next((r for r in g.dicts() if r.get('Máquina ou instalação') == 'Trator 03'), {})
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', val); salvar(); t3 = linha()
    g.ordena('Custo R$/h', desc=True); ordem = [r.get('Máquina ou instalação') for r in g.dicts()]; ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk(f'CD-03 fluxo {tam} (normal): salvar {val} → célula "{cel}" e a ordem por custo põe o Trator 03 entre os de 180 e os de 150',
        t3.get('Custo R$/h') == cel and crescente(ch, True) and ordem.index('Trator 03') == ordem.index('Trator 02') + 1, (t3.get('Custo R$/h'), ordem[:6]))
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', 'abc'); salvar()
    err = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Descartar alterações'); b&&b.click();})()"); time.sleep(.3)
    chk(f'CD-03 fluxo {tam} (recusa): custo "abc" mostra "Use um número" e não grava (célula segue {cel})', 'Use um número' in err and linha().get('Custo R$/h') == cel, (err[-160:], linha().get('Custo R$/h')))
    abre_linha('Trator 03'); salvar(); n3 = [r.get('Máquina ou instalação') for r in g.dicts()].count('Trator 03')
    chk(f'CD-03 fluxo {tam} (repetição): salvar de novo sem mudar não duplica a linha nem muda o valor', n3 == 1 and linha().get('Custo R$/h') == cel, n3)

try:
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= CD-01 Talhões =================
    abre('CD-01.dc.html'); aba('Talhões'); g = Grade(J, 0)
    d = tf03('CD-01 Talhões', g, ['Fazenda › talhão', 'Situação', 'Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas na safra 2026/27'])
    t1 = next((r for r in d if r.get('Fazenda › talhão') == 'T1'), {}); p1 = next((r for r in d if r.get('Fazenda › talhão') == 'P1'), {})
    pv = next((r for r in d if r.get('Fazenda › talhão', '').startswith('PV')), {})
    chk('CD-01: T1 Sequeiro | 312,0 ha | 312,4 ha | +0,1 % | 2 parcelas (número) | Em dia; P1 Pivô central',
        [t1.get(k) for k in ('Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas na safra 2026/27', 'Situação')] == ['Sequeiro', '312,0 ha', '312,4 ha', '+0,1 %', '2', 'Em dia'] and p1.get('Sistema') == 'Pivô central', (t1, p1))
    chk('CD-01: pivô da Lagoa Grande (círculo do KML) dito uma vez, na Situação; Polígono fica "—"', pv.get('Polígono') == '—' and pv.get('Situação') == 'Círculo do KML', pv)
    g.ordena('Área cultivável', desc=True); bl = por_grupo(g, 'Área cultivável')
    chk('CD-01: ordenar Área cultivável (decrescente) pelo número dentro de cada fazenda', bl and all(crescente([num(x) for x in b], True) for b in bl), [b[:4] for b in bl])
    g.filtra('Sistema', ['Pivô central']); s1 = {r.get('Sistema') for r in g.dicts(True)}
    chk('CD-01: filtro Sistema = Pivô central (texto da célula) deixa só pivôs', s1 == {'Pivô central'}, s1)
    limpa(J); shot('cd01-talhoes-1440')
    # ================= CD-01 Água =================
    aba('Água'); g = Grade(J, 0)
    d = tf03('CD-01 Água', g, ['Ponto de água', 'Situação', 'Fazenda', 'Documento', 'Uso', 'Curso d’água', 'Vazão', 'Vencimento'])
    a1 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 1 ')), {}); a6 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 6 ')), {})
    chk('CD-01 Água (defeito): a outorga do ponto 1 aparece como Outorga (antes "Certidão"); o ponto 6 é Certidão', a1.get('Documento') == 'Outorga' and a6.get('Documento') == 'Certidão', (a1, a6))
    chk('CD-01 Água: ponto 1 = Captação superficial | Rio A | 180 m³/h | 30/04/2031 | Vigente',
        [a1.get(k) for k in ('Uso', 'Curso d’água', 'Vazão', 'Vencimento', 'Situação')] == ['Captação superficial', 'Rio A (demonstração)', '180 m³/h', '30/04/2031', 'Vigente'], a1)
    fx = J("[...document.querySelectorAll('.cadx-faixa')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ')).join(' | ')") or ''
    chk('CD-01 Água (defeito): a faixa "precisa de atenção" diz Outorga SINT-003/0000 (antes "Certidão SINT-003/0000")', 'Outorga SINT-003/0000' in fx and 'Certidão SINT-003' not in fx, fx[:200])
    g.ordena('Vazão'); vz = [x for x in g.col('Vazão') if x != '—']; m3 = [num(x) * (3.6 if x.endswith('L/s') else 1) for x in vz]
    chk('CD-01 Água: ordenar Vazão pelo valor em m³/h (L/s × 3,6), com a unidade do documento na célula', crescente(m3) and any(x.endswith('L/s') for x in vz), vz)
    g.ordena('Vencimento'); vc = [instante(x) for x in g.col('Vencimento') if x != '—']
    chk('CD-01 Água: ordenar Vencimento por data (anos diferentes)', crescente(vc) and len({x[0] for x in vc}) > 2, g.col('Vencimento')[:6])
    g.filtra('Documento', ['Certidão']); dc = g.dicts()
    chk('CD-01 Água: filtro Documento = Certidão → só certidões (4)', len(dc) == 4 and all(r.get('Documento') == 'Certidão' for r in dc), [r.get('Ponto de água') for r in dc])
    limpa(J)
    aba('Ambiental'); tf03('CD-01 Ambiental', Grade(J, 0), ['Área ambiental', 'Fazenda', 'Tipo', 'Área'])
    # ================= CD-01det =================
    abre('CD-01det.dc.html#talhao=T1'); gi, gp = Grade(J, 0), Grade(J, 1)
    di = tf03('CD-01det ficha', gi, ['Fazenda', 'Sistema', 'Setor de irrigação', 'Área cultivável', 'Polígono', 'Versão', 'Diferença ha', 'Diferença %', 'Situação'], ficha=True)
    f0 = di[0] if di else {}
    chk('CD-01det ficha: T1 = Santa Rita | Sequeiro | — | 312,0 ha | 312,4 ha | v3 | +0,4 ha | +0,1 % | Ativo',
        [f0.get(k) for k in ('Fazenda', 'Sistema', 'Setor de irrigação', 'Área cultivável', 'Polígono', 'Versão', 'Diferença ha', 'Diferença %', 'Situação')] == ['Santa Rita', 'Sequeiro', '—', '312,0 ha', '312,4 ha', 'v3', '+0,4 ha', '+0,1 %', 'Ativo'], f0)
    dp = tf03('CD-01det parcelas', gp, ['Safra › parcela', 'Situação', 'Tipo', 'Cultura', 'Cultivar', 'Área', 'Livre', 'Plantio'])
    gs = [cells[0] for grp, cells in grupos(gp) if grp]
    chk('CD-01det (defeito): T1 da Santa Rita só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', gs and not any('Mamão' in x for x in gs) and 'Safra 2026/27' in gs, gs)
    t1b = next((r for r in dp if r.get('Safra › parcela') == 'T1-B'), {}); sfr = next((r for r in dp if r.get('Safra › parcela') == 'Safrinha 2027'), {})
    chk('CD-01det: T1-B Parcela | Soja | 62 X | 152,0 ha | 25/10/2026 | Sem polígono; Safrinha 2027 livre 152 ha (número)',
        [t1b.get(k) for k in ('Tipo', 'Cultura', 'Cultivar', 'Área', 'Plantio', 'Situação')] == ['Parcela', 'Soja', '62 X', '152,0 ha', '25/10/2026', 'Sem polígono'] and sfr.get('Livre') == '152 ha' and sfr.get('Situação') == 'Rascunho', (t1b, sfr))
    # pré-existente (revisão TABR): a lista conta 1 parcela no PV01 da Lagoa Grande; o detalhe mostra a mesma (antes a Safra Mamão com 0 ha e 29,9 ha livres)
    abre('Main.dc.html', .3); abre('CD-01det.dc.html#talhao=PV01'); dl = Grade(J, 1).dicts();   # outra página antes: só trocar o # não recarrega
    pv1 = next((r for r in dl if r.get('Safra › parcela') == 'Pivô 1'), {})
    sm = next((r for r in dl if r.get('Safra › parcela', '').startswith('Safra Mamão')), {})
    lv = num(sm.get('Livre') or 'x')
    chk('CD-01det PV01 (Lagoa Grande): a parcela Pivô 1 da Safra Mamão aparece (Mamão Formosa | 29,9 ha) e a safra fica sem área livre',
        pv1.get('Cultura') == 'Mamão Formosa' and pv1.get('Área') == '29,9 ha' and lv is not None and abs(lv) < 0.05, (pv1.get('Cultura'), pv1.get('Área'), sm.get('Livre'), sm.get('Situação')))
    abre('Main.dc.html', .3); abre('CD-01det.dc.html#talhao=T1')
    shot('cd01det-1440')
    # ================= CD-02 =================
    abre('CD-02.dc.html'); aba('Culturas'); g = Grade(J, 0)
    d = tf03('CD-02 Culturas', g, ['Cultura › cultivar', 'Situação', 'Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Item de semente', 'Cultivos'])
    w58 = next((r for r in d if r.get('Cultura › cultivar') == '58 W'), {}); mam = next((r for r in d if r.get('Cultura › cultivar', '').startswith('Mamão Formosa')), {})
    chk('CD-02: 58 W = Anual | sc de 60 kg/ha | 118 dias | 6 cultivos (número); Mamão Formosa em t/ha/ano (DEC-0510-03)',
        [w58.get(k) for k in ('Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Cultivos')] == ['Anual', 'sc de 60 kg/ha', '118 dias', '6'] and mam.get('Unidade de produtividade') == 't/ha/ano', (w58, mam))
    g.filtra('Unidade de produtividade', ['t/ha/ano']); fl = [r.get('Cultura › cultivar') for r in g.dicts()]
    chk('CD-02: filtro Unidade de produtividade = t/ha/ano vale na cultivar (Mamão Formosa › Formosa)', len(fl) == 2 and fl[0].startswith('Mamão Formosa') and fl[1] == 'Formosa', fl)
    limpa(J); g.ordena('Ciclo', desc=True); bl = por_grupo(g, 'Ciclo')
    chk('CD-02: ordenar Ciclo (dias) pelo número dentro da cultura', bl and all(crescente([num(x) for x in b], True) for b in bl), bl[:2])
    aba('Operações'); g = Grade(J, 0)
    d = tf03('CD-02 Rendimentos', g, ['Operação › conjunto', 'Fonte', 'Processo', 'Cultura', 'Rendimento', 'Custo R$/h', 'Custo R$/ha'])
    pz = next((r for r in d if r.get('Operação › conjunto', '').startswith('Trator 02')), {})
    chk('CD-02: pulverização Medição local | Tratos culturais | 21,60 ha/h | R$ 313,00/h | R$ 14,49/ha',
        [pz.get(k) for k in ('Fonte', 'Processo', 'Rendimento', 'Custo R$/h', 'Custo R$/ha')] == ['Medição local', 'Tratos culturais', '21,60 ha/h', 'R$ 313,00/h', 'R$ 14,49/ha'], pz)
    fch = [(r.get('Operação › conjunto'), c) for r, c in zip(g.dicts(), g.chips('Fonte')) if c]
    chk('CD-02 (A11): a Fonte é texto; só a premissa a validar é chip (pendência com "Validar ›")', [x for x, _ in fch] == ['Derriçadeiras portáteis · equipe de 6'], fch)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Trator 02')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    fv = lambda k: J(f"(document.querySelector('#fx_g_rend_{k}')||{{}}).value") or ''
    chk('CD-02 (A1): largura 36 m, velocidade 8 km/h e eficiência 75 % no painel do rendimento (saíram da grade)', [fv('larg'), fv('vel'), fv('efic')] == ['36', '8', '75'], [fv('larg'), fv('vel'), fv('efic')])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    g.filtra('Processo', ['Colheita']); fl = {r.get('Processo') for r in g.dicts(True)}
    chk('CD-02: filtro Processo = Colheita vale no conjunto', fl == {'Colheita'} and len(g.dicts(True)) == 2, [r.get('Operação › conjunto') for r in g.dicts(True)])
    limpa(J)
    # ================= CD-03 =================
    abre('CD-03.dc.html'); g = Grade(J, 0)
    CD3 = ['Máquina ou instalação', 'Situação', 'Classe', 'Custo R$/h', 'Conjuntos', 'Próxima calibração']
    d = tf03('CD-03 Máquinas', g, CD3)
    pv = next((r for r in d if r.get('Máquina ou instalação') == 'Pulverizador PJ-3030'), {}); pk = next((r for r in d if r.get('Máquina ou instalação') == 'Packing linha 1'), {})
    chk('CD-03: pulverizador Apta | Pulverizador | R$ 95,00/h | 14/12/2026 (modelo e largura no painel)',
        [pv.get(k) for k in ('Situação', 'Classe', 'Custo R$/h', 'Próxima calibração')] == ['Apta', 'Pulverizador', 'R$ 95,00/h', '14/12/2026'], pv)
    chk('CD-03 (A10): calibração que vence em 15 dias diz isso no chip (Packing linha 1: "Calibração a vencer" e "Registrar calibração"; antes "Apta" verde e só a data em amarelo)',
        pk.get('Situação') == 'Calibração a vencer Registrar calibração ›' and pk.get('Próxima calibração') == '01/10/2026', pk)
    # A4: a capacidade muda de grandeza com a classe; a coluna entra quando o filtro de Classe deixa uma só (rótulo e unidade da classe)
    g.filtra('Classe', ['Irrigação']); hs = g.heads(); vz = g.col('Vazão'); al3 = g.desalinhadas()
    chk('CD-03 (A4, M-k): Classe = Irrigação → coluna Vazão em m³/h depois da Classe, com a vazão das 3 instalações', [h for h, _ in hs] == CD3[:3] + ['Vazão'] + CD3[3:] and dict(hs).get('Vazão') == 'm³/h'
        and len(vz) == 3 and all(un_ok(x, 'm³/h') and x != '—' for x in vz), (hs, vz))
    chk('CD-03 (A4): com a coluna de capacidade (7 colunas) cada célula fica sob o seu cabeçalho (a trilha do grid acompanha a coluna que entra)', len(hs) == 7 and al3 == 0, (len(hs), al3))
    g.ordena('Vazão', desc=True); vz2 = [num(x) for x in g.col('Vazão')]
    chk('CD-03 (A4): ordenar a Vazão pelo número', crescente(vz2, True), g.col('Vazão'))
    g.filtra('Classe', ['Trator', 'Pulverizador']); hs2 = g.labels()
    g.filtra('Classe', ['Trator']); pt = g.col('Potência'); hs3 = g.labels()
    chk('CD-03 (A4): Trator + Pulverizador (cv e L) → sem coluna de capacidade; só Trator → Potência em cv', hs2 == CD3 and hs3 == CD3[:3] + ['Potência'] + CD3[3:] and pt and all(x.endswith(' cv') for x in pt), (hs2, hs3, pt))
    limpa(J); chk('CD-03 (A4): Limpar filtros tira a coluna de capacidade', g.labels() == CD3, g.labels())
    g.ordena('Custo R$/h', desc=True); ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk('CD-03: ordenar Custo R$/h (decrescente) pelo número', crescente(ch, True), g.col('Custo R$/h')[:5])
    g.ordena('Próxima calibração'); cl = g.col('Próxima calibração'); dv = [instante(x) for x in cl if x != '—']
    chk('CD-03: ordenar Próxima calibração por data; sem data no fim', crescente(dv) and cl[len(dv):] == ['—'] * (len(cl) - len(dv)), cl)
    g.filtra('Classe', ['Irrigação']); fl = [r.get('Máquina ou instalação') for r in g.dicts()]
    chk('CD-03: filtro Classe = Irrigação → as 3 bombas/setores', len(fl) == 3 and all(r.get('Classe') == 'Irrigação' for r in g.dicts()), fl)
    # recusa e repetição do filtro: vazio continua vazio; o mesmo filtro duas vezes dá o mesmo recorte
    J("""(()=>{const i=document.querySelector('input[aria-label="Buscar nesta tabela"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Silo');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('CD-03 (recusa): Classe = Irrigação + busca "Silo" → nenhuma linha e o aviso "Nenhuma linha corresponde aos filtros" (sem voltar a todas)', g.dicts() == [] and vaz, len(g.dicts()))
    limpa(J); n0 = len(g.dicts()); g.filtra('Classe', ['Trator']); a1 = [r.get('Máquina ou instalação') for r in g.dicts()]; g.filtra('Classe', ['Trator']); a2 = [r.get('Máquina ou instalação') for r in g.dicts()]
    chk('CD-03 (repetição): o mesmo filtro duas vezes dá o mesmo recorte; Limpar filtros volta às 15', a1 == a2 and len(a1) == 4 and n0 == 15, (a1, a2, n0))
    abre('CD-03.dc.html'); g = Grade(J, 0); base = [r.get('Máquina ou instalação') for r in g.dicts()]   # sem ordem aplicada
    g.cabecalho_ordena('Custo R$/h'); cr = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk('CD-03: um clique no título Custo R$/h ordena crescente pelo número', crescente(cr), g.col('Custo R$/h')[:6])
    for _ in range(2): g.cabecalho_ordena('Custo R$/h')
    chk('CD-03 (repetição): três cliques no título (crescente → decrescente → sem ordem) voltam à ordem original', [r.get('Máquina ou instalação') for r in g.dicts()] == base, base[:4])
    # fluxo do cadastro na grade: salvar o custo do Trator 03 → célula e ordem acompanham; número inválido não grava; salvar de novo não duplica
    fluxo_custo(g, '1440', '172,5', 'R$ 172,50/h')
    shot('cd03-1440')
    # ================= CD-04 =================
    abre('CD-04.dc.html'); aba('Pessoas'); g = Grade(J, 0)
    d = tf03('CD-04 Pessoas', g, ['Pessoa', 'Situação', 'Equipe', 'Habilidades', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação'], extra=())
    lu = next((r for r in d if r.get('Pessoa') == 'Lucas'), {})
    chk('CD-04 (A3): Lucas Não alocável em O.S. (motivo na dica: NR-31 vencida) · Renovar NR-31 | Campo 2 | Safrista | 31/07/2027 | R$ 38,00/h | NR-31 | 15/08/2026',
        [lu.get(k) for k in ('Situação', 'Equipe', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação')] == ['Não alocável em O.S. : NR-31 vencida em 15/08/2026 Renovar NR-31 ›', 'Campo 2', 'Safrista', '31/07/2027', 'R$ 38,00/h', 'NR-31', '15/08/2026'], lu)
    # A3: contrato encerrado (Disponível até no passado) diz o motivo e o próximo passo, e a data fica em vermelho (a reprodução do revisor: Carlos até 01/09/2026)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Carlos')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('#fx_g_pes_ate'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2026-09-01'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.2)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.7)
    ca = next((r for r in g.dicts() if r.get('Pessoa') == 'Carlos'), {})
    cor = J("""(()=>{const t=([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[0]; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').trim());
      const r=[...t.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Carlos')===0); const c=r.querySelectorAll('[role=cell]')[hs.indexOf('Disponível até')]; const sp=[...c.querySelectorAll('span')].filter(s=>s.innerText.trim()==='01/09/2026').pop(); return sp?getComputedStyle(sp).color:'';})()""") or ''
    chk('CD-04 (A3): Carlos com "Disponível até" 01/09/2026 → "Não alocável em O.S." com o motivo (contrato encerrado) e "Renovar contrato ›"; a data em vermelho',
        ca.get('Situação') == 'Não alocável em O.S. : Contrato encerrado em 01/09/2026 Renovar contrato ›' and ca.get('Disponível até') == '01/09/2026' and cor == 'rgb(180, 35, 24)', (ca.get('Situação'), ca.get('Disponível até'), cor))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Carlos')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    cal = [J(f"(document.querySelector('#fx_g_pes_{k}')||{{}}).value") for k in ('cal', 'acesso')]
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    chk('CD-04 (A1): calendário e acesso ao app no painel da pessoa (saíram da grade)', cal[0] == 'Da equipe' and cal[1] in ('Com login', 'Sem login', 'Acesso solicitado'), cal)
    rr = g.rotulos('Habilidades')
    chk('CD-04: o filtro de Habilidades oferece cada habilidade (não a lista inteira da célula)', rr and 'Operar trator' in rr and not any(',' in x for x in rr), rr)
    g.filtra('Habilidades', ['Operar trator']); fl = sorted(r.get('Pessoa') for r in g.dicts())
    chk('CD-04: filtro Habilidades = Operar trator → Beto, Carlos, Lucas, Marcos (pertinência, não texto)', fl == ['Beto', 'Carlos', 'Lucas', 'Marcos'], fl)
    limpa(J); g.ordena('Validade da habilitação'); vh = [instante(x) for x in g.col('Validade da habilitação') if instante(x)]
    chk('CD-04: ordenar Validade da habilitação por data', crescente(vh), g.col('Validade da habilitação'))
    # ================= CD-05 =================
    abre('CD-05.dc.html'); aba('Parceiros'); g = Grade(J, 0)
    d = tf03('CD-05 Parceiros', g, ['Parceiro', 'Situação do papel', 'CPF/CNPJ', 'Papéis', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados'])
    sv = next((r for r in d if r.get('Parceiro') == 'Sementes Vale'), {}); cv = next((r for r in d if r.get('Parceiro') == 'Coop. Vale'), {})
    chk('CD-05: Sementes Vale WhatsApp 65 99555-6677 "não autorizado" (Canais = E-mail); Coop. Vale com dois papéis e dois estados',
        sv.get('WhatsApp') == '65 99555-6677 não autorizado' and sv.get('Canais autorizados') == 'E-mail' and cv.get('Papéis') == 'Fornecedor, Cliente' and cv.get('Situação do papel') == 'Homologado Limite vigente', (sv, cv))
    g.filtra('Canais autorizados', ['WhatsApp']); fl = g.dicts()
    chk('CD-05: filtro Canais autorizados = WhatsApp (por item da lista)', fl and all('WhatsApp' in r.get('Canais autorizados', '') for r in fl) and len(fl) < len(d), len(fl))
    limpa(J)
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Clientes')).click()"); time.sleep(.6)
    dc = tf03('CD-05 Clientes', g, ['Parceiro', 'Situação do papel', 'CPF/CNPJ', 'Papéis', 'Limite de crédito', 'Validade da análise de crédito', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados'])
    chk('CD-05 Clientes (M-e): com 10 colunas (2 a mais que em Todos) cada célula fica sob o seu cabeçalho', len(g.labels()) == 10 and g.desalinhadas() == 0, (len(g.labels()), g.desalinhadas()))
    rh = next((r for r in dc if r.get('Parceiro') == 'Rede Hortifrúti BA'), {})
    chk('CD-05 Clientes: Rede Hortifrúti BA R$ 40.000 | 31/08/2026 | Limite vencido', [rh.get(k) for k in ('Limite de crédito', 'Validade da análise de crédito', 'Situação do papel')] == ['R$ 40.000', '31/08/2026', 'Limite vencido'], rh)
    g.ordena('Limite de crédito', desc=True); lc = [num(x) for x in g.col('Limite de crédito')]
    chk('CD-05 Clientes: ordenar Limite de crédito pelo número', crescente(lc, True), g.col('Limite de crédito'))
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Todos')).click()"); time.sleep(.5)
    # A5: em Todos, Papéis = Cliente; em Transportadores (0 linhas) o menu de Papéis continua com "Cliente" marcado (antes sumia do menu)
    papel = lambda t: (J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"), time.sleep(.6))
    g.filtra('Papéis', ['Cliente']); papel('Transportadores'); n0 = len(g.dicts())
    g._menu('Papéis'); mm = J("[...document.querySelectorAll('[role=dialog] label')].map(l=>[l.innerText.replace(/\\s+/g,' ').trim(), l.querySelector('input').checked])") or []
    J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    chk('CD-05 (A5): Papéis = Cliente e depois Transportadores → 0 linhas e o menu de Papéis mostra "Cliente 0" marcado', n0 == 0 and ['Cliente 0', True] in mm, (n0, mm))
    limpa(J); papel('Todos')
    aba('Cobertura'); g = Grade(J, 0)
    d = tf03('CD-05 Cobertura', g, ['Grupo de insumo', 'Fornecedores que recebem cotação', 'Situação'])
    se = next((r for r in d if r.get('Grupo de insumo') == 'Sementes'), {}); co = next((r for r in d if r.get('Grupo de insumo') == 'Combustível'), {})
    chk('CD-05 Cobertura: a Situação diz o estado (o número fica ao lado): Sementes 2 Com concorrência; Combustível 0 Sem fornecedor',
        [se.get('Fornecedores que recebem cotação'), se.get('Situação')] == ['2', 'Com concorrência'] and co.get('Fornecedores que recebem cotação') == '0' and co.get('Situação', '').startswith('Sem fornecedor'), (se, co))
    # ================= CD-06 =================
    abre('CD-06.dc.html'); aba('Itens'); g = Grade(J, 0)
    d = tf03('CD-06 Itens', g, ['Grupo › item', 'Situação', 'Natureza de custo', 'Unidade', 'Embalagem', 'Preço de referência', 'Data do preço'])
    ds = next((r for r in d if r.get('Grupo › item') == 'Diesel S10'), {}); ca = next((r for r in d if r.get('Grupo › item') == 'Calcário dolomítico'), {})
    chk('CD-06: Diesel S10 L | granel | R$ 6,19/L | 15/09/2026; Calcário dolomítico sem preço (— | Sem preço)',
        [ds.get(k) for k in ('Unidade', 'Embalagem', 'Preço de referência', 'Data do preço')] == ['L', 'granel', 'R$ 6,19/L', '15/09/2026'] and ca.get('Preço de referência') == '—' and ca.get('Situação', '').startswith('Sem preço'), (ds, ca))
    pr = [x for x in g.col('Preço de referência', True) if x.startswith('R$')]
    chk('CD-06: preço com a unidade do item na célula ("R$ 22,00/L", "R$ 2,40/kg")', pr and all(re.fullmatch(r'R\$ [\d.]+,\d{2}/(L|kg|un|t|sc 60 kg)', x) for x in pr), pr[:5])
    g.filtra('Natureza de custo', ['3.1.02 · Defensivos']); fl = {r.get('Natureza de custo') for r in g.dicts(True)}
    chk('CD-06: filtro Natureza de custo vale no item', fl == {'3.1.02 · Defensivos'} and len(g.dicts(True)) > 5, len(g.dicts(True)))
    limpa(J); g.ordena('Preço de referência', desc=True); bl = por_grupo(g, 'Preço de referência')
    chk('CD-06: ordenar Preço de referência pelo número dentro do grupo', bl and all(crescente([num(x) for x in b if x != '—'], True) or len([x for x in b if x != '—']) < 2 for b in bl), bl[:2])
    aba('Locais'); g = Grade(J, 0)
    d = tf03('CD-06 Locais', g, ['Local', 'Fazenda', 'Tipo', 'Itens com este local padrão'])
    # A4: L (tanque) e sc de 60 kg (silo) são grandezas diferentes: a capacidade entra com o filtro Tanque ou Silo, com a unidade dele
    qtipo = lambda t: (J(f"[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"), time.sleep(.5))
    qtipo('Tanque'); ht = g.heads(); ct = g.col('Capacidade'); al6 = g.desalinhadas(); qtipo('Silo'); hsl = g.heads(); cs_ = g.col('Capacidade'); qtipo('Todos')
    chk('CD-06 Locais (A4): sem coluna de capacidade em Todos; Tanque → Capacidade em L (15.000 L); Silo → em sc de 60 kg (60.000 sc de 60 kg)',
        'Capacidade' not in g.labels() and dict(ht).get('Capacidade') == 'L' and ct == ['15.000 L'] and dict(hsl).get('Capacidade') == 'sc de 60 kg' and cs_ == ['60.000 sc de 60 kg'], (ht, ct, hsl, cs_))
    chk('CD-06 Locais (A4): com a Capacidade (5 colunas) cada célula fica sob o seu cabeçalho', len(ht) == 5 and al6 == 0, (len(ht), al6))
    # ================= CD-07 =================
    abre('CD-07.dc.html'); g = Grade(J, 0)
    CD7 = ['Dimensão › código', 'Situação', 'Nome', 'Início da vigência', 'Fim da vigência', 'Conta no ERP (Sankhya)', 'No rascunho']
    d = tf03('CD-07 Estrutura', g, CD7)
    n1 = next((r for r in d if r.get('Dimensão › código') == '3.1.01'), {}); e2 = next((r for r in d if r.get('Dimensão › código') == '02'), {})
    chk('CD-07: 3.1.01 Mapeado | Fertilizantes e corretivos | 01/07/2026 | 30/06/2027 | 4.1.1.01; 02 Novo no rascunho',
        [n1.get(k) for k in ('Situação', 'Nome', 'Início da vigência', 'Fim da vigência', 'Conta no ERP (Sankhya)')] == ['Mapeado', 'Fertilizantes e corretivos', '01/07/2026', '30/06/2027', '4.1.1.01'] and e2.get('No rascunho') == 'Novo', (n1, e2))
    def painel7(cod):
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(cod)})===0); r&&r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
        out = [J(f"(document.querySelector('#fx_g_dim_{k}')||{{}}).value") or '' for k in ('origT', 'vincT', 'top')]
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3); return out
    p31, pso = painel7('3.1.01'), painel7('SOJA')
    chk('CD-07 (A1): origem, vínculos e TOP no painel do código (3.1.01 Estrutura gerencial · grupos … · TOP 1201; SOJA Culturas e cultivares)', p31[0] == 'Estrutura gerencial' and p31[2] == '1201' and p31[1] and pso[0] == 'Culturas e cultivares', (p31, pso))
    g.ordena('Início da vigência', desc=True); bl = por_grupo(g, 'Início da vigência')
    chk('CD-07: ordenar Início da vigência por data dentro da dimensão', bl and all(crescente([instante(x) for x in b], True) or len(set(b)) < 2 for b in bl), bl[:2])
    g.filtra('Situação', ['Dimensão própria']); fl = {r.get('Situação') for r in g.dicts(True)}
    chk('CD-07: filtro Situação = Dimensão própria → culturas e processos (9)', fl == {'Dimensão própria'} and len(g.dicts(True)) == 9, len(g.dicts(True)))
    limpa(J); shot('cd07-1440')
    # A8: depois de publicar, "No rascunho" sai (não fica uma coluna vazia em todas as linhas); com rascunho novo, volta
    J("(()=>{const c=[...document.querySelectorAll('.cadx-aviso')].find(c=>c.innerText.indexOf('Publicar estrutura')>=0); c&&c.click();})()"); time.sleep(.6)
    h_pub = g.labels(); al7 = g.desalinhadas()
    chk('CD-07 (A8): depois de "Publicar estrutura", a coluna "No rascunho" sai e as células seguem sob os cabeçalhos', h_pub == CD7[:-1] and al7 == 0, (h_pub, al7))
    # A1: a Situação à vista sem rolar a grade a 1440 e 1280 px; a 1440 px as grades cabem na caixa (o CD-05 rola só os contatos, no fim)
    MED = """(()=>[...document.querySelectorAll('.g2rola')].filter(r=>r.offsetParent).map(r=>{const R=r.getBoundingClientRect(); const hs=[...r.querySelectorAll('[role=table]>[role=row] [role=columnheader]')];
      const lab=h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim(); return {sobra:r.scrollWidth-r.clientWidth, fora:hs.filter(h=>h.getBoundingClientRect().right>R.right+1).map(lab)};}))()"""
    larg = []
    for w in (1440, 1280):
        c.aparelho(w, 900, 1, False)
        for pg, tabs in (('CD-01.dc.html', ['Talhões', 'Água']), ('CD-01det.dc.html#talhao=T1', ['']), ('CD-02.dc.html', ['Culturas', 'Operações']), ('CD-03.dc.html', ['']),
                         ('CD-04.dc.html', ['Pessoas']), ('CD-05.dc.html', ['Parceiros']), ('CD-06.dc.html', ['Itens', 'Locais']), ('CD-07.dc.html', [''])):
            abre(pg)
            for tb in tabs:
                if tb: aba(tb)
                for i, m in enumerate(J(MED) or []):
                    ruim = sorted({'Situação', 'Situação do papel', 'Fonte'} & set(m['fora'])) + (['rola %d px' % m['sobra']] if (w == 1440 and m['sobra'] > 1 and not pg.startswith('CD-05')) else [])
                    if ruim: larg.append((w, pg.split('.')[0], tb, i, ruim))
    chk('CD (A1): Situação à vista sem rolar a 1440 e 1280 px; a 1440 px as grades cabem na caixa (o CD-05 rola só os contatos)', not larg, larg)
    c.aparelho(1440, 900, 1, False)
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (1440)', not ERRS, ERRS[:3])
    # ================= 390 px =================
    c.aparelho(390, 844, 2, True); r390 = []
    for pg, tabs in (('CD-01.dc.html', ['Talhões', 'Água']), ('CD-01det.dc.html#talhao=T1', ['']), ('CD-02.dc.html', ['Culturas', 'Operações']), ('CD-03.dc.html', ['']),
                     ('CD-04.dc.html', ['Pessoas']), ('CD-05.dc.html', ['Parceiros', 'Cobertura']), ('CD-06.dc.html', ['Itens', 'Locais']), ('CD-07.dc.html', [''])):
        abre(pg)
        for tb in tabs:
            if tb: aba(tb)
            n = J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length") or 0
            for i in range(n):
                q = Grade(J, i).rola_dentro(); r390.append((pg.split('.')[0] + (' ' + tb if tb else '') + f' #{i}', q.get('pagina'), q.get('cabe') or q.get('rola'), q.get('c0'), q.get('rola')))
        if pg.startswith('CD-03'): shot('cd03-390')
    ruim = [x for x in r390 if not (x[1] and x[2] and x[3])]
    chk(f'390 px: {len(r390)} grades sem rolagem lateral da página; cada grade cabe ou rola dentro da caixa, com a 1ª coluna à vista', r390 and not ruim, ruim or r390[:3])
    chk('390 px: as grades largas rolam dentro da caixa (pelo menos as de muitas colunas)', sum(1 for x in r390 if x[4]) >= len(r390) - 3, [x[0] for x in r390 if not x[4]])
    # fluxo a 390 px, com toque: o mesmo cadastro na grade (normal, recusa, repetição) e o filtro pelo menu da coluna
    abre('CD-03.dc.html'); g = Grade(J, 0); fluxo_custo(g, '390 px', '165', 'R$ 165,00/h'); limpa(J)
    n0 = len(g.dicts()); g.filtra('Classe', ['Irrigação']); a1 = [r.get('Máquina ou instalação') for r in g.dicts()]
    J("""(()=>{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Silo');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('CD-03 390 px (filtro): Classe = Irrigação → 3 linhas; + busca "Silo" → nenhuma linha e o aviso; Limpar filtros volta a todas',
        len(a1) == 3 and g.dicts() == [] and vaz and (limpa(J) or True) and len(g.dicts()) == n0, (a1, n0))
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
