# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Cadastros (CD-01..CD-07 e CD-01det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("160,0 ha", "R$ 14,49/ha"),
"Custo R$/h" e "Custo R$/ha", filtro e ordenação em todas as colunas, filtro pelo texto da célula, ordem pelo número e pela data,
Situação em chip; 390 px rolando dentro da caixa. Defeitos reproduzidos: outorga aparecia como "Certidão" (CD-01 Água) e a Safra Mamão
da Lagoa Grande aparecia nas parcelas de talhão da Santa Rita (CD-01det). Fluxo do cadastro na grade (CD-03): normal (salvar o custo e a
célula/ordem acompanham), recusa (número inválido não grava) e repetição (salvar de novo não duplica). Vazio continua vazio.
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

try:
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= CD-01 Talhões =================
    abre('CD-01.dc.html'); aba('Talhões'); g = Grade(J, 0)
    d = tf03('CD-01 Talhões', g, ['Fazenda › talhão', 'Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas na safra 2026/27', 'Situação'])
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
    d = tf03('CD-01 Água', g, ['Ponto de água', 'Fazenda', 'Documento', 'Uso', 'Curso d’água', 'Vazão', 'Vencimento', 'Situação'])
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
    dp = tf03('CD-01det parcelas', gp, ['Safra › parcela', 'Tipo', 'Cultura', 'Cultivar', 'Área', 'Livre', 'Plantio', 'Situação'])
    gs = [cells[0] for grp, cells in grupos(gp) if grp]
    chk('CD-01det (defeito): T1 da Santa Rita só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', gs and not any('Mamão' in x for x in gs) and 'Safra 2026/27' in gs, gs)
    t1b = next((r for r in dp if r.get('Safra › parcela') == 'T1-B'), {}); sfr = next((r for r in dp if r.get('Safra › parcela') == 'Safrinha 2027'), {})
    chk('CD-01det: T1-B Parcela | Soja | 62 X | 152,0 ha | 25/10/2026 | Sem polígono; Safrinha 2027 livre 152 ha (número)',
        [t1b.get(k) for k in ('Tipo', 'Cultura', 'Cultivar', 'Área', 'Plantio', 'Situação')] == ['Parcela', 'Soja', '62 X', '152,0 ha', '25/10/2026', 'Sem polígono'] and sfr.get('Livre') == '152 ha' and sfr.get('Situação') == 'Rascunho', (t1b, sfr))
    shot('cd01det-1440')
    # ================= CD-02 =================
    abre('CD-02.dc.html'); aba('Culturas'); g = Grade(J, 0)
    d = tf03('CD-02 Culturas', g, ['Cultura › cultivar', 'Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Item de semente', 'Cultivos', 'Situação'])
    w58 = next((r for r in d if r.get('Cultura › cultivar') == '58 W'), {}); mam = next((r for r in d if r.get('Cultura › cultivar', '').startswith('Mamão Formosa')), {})
    chk('CD-02: 58 W = Anual | sc de 60 kg/ha | 118 dias | 6 cultivos (número); Mamão Formosa em t/ha/ano (DEC-0510-03)',
        [w58.get(k) for k in ('Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Cultivos')] == ['Anual', 'sc de 60 kg/ha', '118 dias', '6'] and mam.get('Unidade de produtividade') == 't/ha/ano', (w58, mam))
    g.filtra('Unidade de produtividade', ['t/ha/ano']); fl = [r.get('Cultura › cultivar') for r in g.dicts()]
    chk('CD-02: filtro Unidade de produtividade = t/ha/ano vale na cultivar (Mamão Formosa › Formosa)', len(fl) == 2 and fl[0].startswith('Mamão Formosa') and fl[1] == 'Formosa', fl)
    limpa(J); g.ordena('Ciclo', desc=True); bl = por_grupo(g, 'Ciclo')
    chk('CD-02: ordenar Ciclo (dias) pelo número dentro da cultura', bl and all(crescente([num(x) for x in b], True) for b in bl), bl[:2])
    aba('Operações'); g = Grade(J, 0)
    d = tf03('CD-02 Rendimentos', g, ['Operação › conjunto', 'Processo', 'Cultura', 'Modo', 'Largura', 'Velocidade', 'Eficiência', 'Rendimento', 'Custo R$/h', 'Custo R$/ha', 'Fonte'])
    pz = next((r for r in d if r.get('Operação › conjunto', '').startswith('Trator 02')), {})
    chk('CD-02: pulverização 36 m | 8 km/h | 75 % | 21,60 ha/h | R$ 313,00/h | R$ 14,49/ha; processo Tratos culturais',
        [pz.get(k) for k in ('Processo', 'Largura', 'Velocidade', 'Eficiência', 'Rendimento', 'Custo R$/h', 'Custo R$/ha')] == ['Tratos culturais', '36 m', '8 km/h', '75 %', '21,60 ha/h', 'R$ 313,00/h', 'R$ 14,49/ha'], pz)
    g.filtra('Processo', ['Colheita']); fl = {r.get('Processo') for r in g.dicts(True)}
    chk('CD-02: filtro Processo = Colheita vale no conjunto', fl == {'Colheita'} and len(g.dicts(True)) == 2, [r.get('Operação › conjunto') for r in g.dicts(True)])
    limpa(J)
    # ================= CD-03 =================
    abre('CD-03.dc.html'); g = Grade(J, 0)
    d = tf03('CD-03 Máquinas', g, ['Máquina ou instalação', 'Modelo', 'Classe', 'Capacidade', 'Largura de trabalho', 'Custo R$/h', 'Conjuntos', 'Próxima calibração', 'Situação'])
    pv = next((r for r in d if r.get('Máquina ou instalação') == 'Pulverizador PJ-3030'), {})
    chk('CD-03: pulverizador Uniport 3030 | 3.000 L | 36 m | R$ 95,00/h | 14/12/2026 | Apta',
        [pv.get(k) for k in ('Modelo', 'Capacidade', 'Largura de trabalho', 'Custo R$/h', 'Próxima calibração', 'Situação')] == ['Uniport 3030', '3.000 L', '36 m', 'R$ 95,00/h', '14/12/2026', 'Apta'], pv)
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
    g.cabecalho_ordena('Capacidade'); cr = [num(x) for x in g.col('Capacidade') if x != '—']
    chk('CD-03: um clique no título Capacidade ordena crescente pelo número (mesmo com unidades diferentes por classe)', crescente(cr), g.col('Capacidade')[:6])
    for _ in range(2): g.cabecalho_ordena('Capacidade')
    chk('CD-03 (repetição): três cliques no título (crescente → decrescente → sem ordem) voltam à ordem original', [r.get('Máquina ou instalação') for r in g.dicts()] == base, base[:4])
    # fluxo do cadastro na grade: salvar o custo do Trator 03 → célula e ordem acompanham; número inválido não grava; salvar de novo não duplica
    def abre_linha(nome): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(nome)})===0); r&&r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    def campo(fid, val): J(f"""(()=>{{const i=document.querySelector('#{fid}'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.2)
    def salvar(): J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', '172,5'); salvar()
    t3 = next((r for r in g.dicts() if r.get('Máquina ou instalação') == 'Trator 03'), {})
    g.ordena('Custo R$/h', desc=True); ordem = [r.get('Máquina ou instalação') for r in g.dicts()]
    chk('CD-03 fluxo (normal): salvar 172,5 → célula "R$ 172,50/h" e a ordem por custo põe o Trator 03 entre os de 180 e os de 150',
        t3.get('Custo R$/h') == 'R$ 172,50/h' and ordem.index('Trator 03') == ordem.index('Trator 02') + 1, (t3.get('Custo R$/h'), ordem[:6]))
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', 'abc'); salvar()
    err = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Descartar alterações'); b&&b.click();})()"); time.sleep(.3)
    t3b = next((r for r in g.dicts() if r.get('Máquina ou instalação') == 'Trator 03'), {})
    chk('CD-03 fluxo (recusa): custo "abc" mostra "Use um número" e não grava (célula segue R$ 172,50/h)', 'Use um número' in err and t3b.get('Custo R$/h') == 'R$ 172,50/h', (err[-160:], t3b.get('Custo R$/h')))
    abre_linha('Trator 03'); salvar(); n3 = [r.get('Máquina ou instalação') for r in g.dicts()].count('Trator 03')
    chk('CD-03 fluxo (repetição): salvar de novo sem mudar não duplica a linha nem muda o valor', n3 == 1 and next((r for r in g.dicts() if r.get('Máquina ou instalação') == 'Trator 03'), {}).get('Custo R$/h') == 'R$ 172,50/h', n3)
    shot('cd03-1440')
    # ================= CD-04 =================
    abre('CD-04.dc.html'); aba('Pessoas'); g = Grade(J, 0)
    d = tf03('CD-04 Pessoas', g, ['Pessoa', 'Equipe', 'Habilidades', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação', 'Situação'], extra=())
    lu = next((r for r in d if r.get('Pessoa') == 'Lucas'), {})
    chk('CD-04: Lucas Campo 2 | Safrista | 31/07/2027 | R$ 38,00/h | NR-31 | 15/08/2026 | Não alocável em O.S.',
        [lu.get(k) for k in ('Equipe', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação', 'Situação')] == ['Campo 2', 'Safrista', '31/07/2027', 'R$ 38,00/h', 'NR-31', '15/08/2026', 'Não alocável em O.S.'], lu)
    rr = g.rotulos('Habilidades')
    chk('CD-04: o filtro de Habilidades oferece cada habilidade (não a lista inteira da célula)', rr and 'Operar trator' in rr and not any(',' in x for x in rr), rr)
    g.filtra('Habilidades', ['Operar trator']); fl = sorted(r.get('Pessoa') for r in g.dicts())
    chk('CD-04: filtro Habilidades = Operar trator → Beto, Carlos, Lucas, Marcos (pertinência, não texto)', fl == ['Beto', 'Carlos', 'Lucas', 'Marcos'], fl)
    limpa(J); g.ordena('Validade da habilitação'); vh = [instante(x) for x in g.col('Validade da habilitação') if instante(x)]
    chk('CD-04: ordenar Validade da habilitação por data', crescente(vh), g.col('Validade da habilitação'))
    # ================= CD-05 =================
    abre('CD-05.dc.html'); aba('Parceiros'); g = Grade(J, 0)
    d = tf03('CD-05 Parceiros', g, ['Parceiro', 'CPF/CNPJ', 'Papéis', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados', 'Situação do papel'])
    sv = next((r for r in d if r.get('Parceiro') == 'Sementes Vale'), {}); cv = next((r for r in d if r.get('Parceiro') == 'Coop. Vale'), {})
    chk('CD-05: Sementes Vale WhatsApp 65 99555-6677 sem autorização (Canais = E-mail); Coop. Vale com dois papéis e dois estados',
        sv.get('WhatsApp') == '65 99555-6677' and sv.get('Canais autorizados') == 'E-mail' and cv.get('Papéis') == 'Fornecedor, Cliente' and cv.get('Situação do papel') == 'Homologado Limite vigente', (sv, cv))
    g.filtra('Canais autorizados', ['WhatsApp']); fl = g.dicts()
    chk('CD-05: filtro Canais autorizados = WhatsApp (por item da lista)', fl and all('WhatsApp' in r.get('Canais autorizados', '') for r in fl) and len(fl) < len(d), len(fl))
    limpa(J)
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Clientes')).click()"); time.sleep(.6)
    dc = tf03('CD-05 Clientes', g, ['Parceiro', 'CPF/CNPJ', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados', 'Limite de crédito', 'Validade da análise de crédito', 'Situação do papel'])
    rh = next((r for r in dc if r.get('Parceiro') == 'Rede Hortifrúti BA'), {})
    chk('CD-05 Clientes: Rede Hortifrúti BA R$ 40.000 | 31/08/2026 | Limite vencido', [rh.get(k) for k in ('Limite de crédito', 'Validade da análise de crédito', 'Situação do papel')] == ['R$ 40.000', '31/08/2026', 'Limite vencido'], rh)
    g.ordena('Limite de crédito', desc=True); lc = [num(x) for x in g.col('Limite de crédito')]
    chk('CD-05 Clientes: ordenar Limite de crédito pelo número', crescente(lc, True), g.col('Limite de crédito'))
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Todos')).click()"); time.sleep(.5)
    aba('Cobertura'); g = Grade(J, 0)
    d = tf03('CD-05 Cobertura', g, ['Grupo de insumo', 'Fornecedores que recebem cotação', 'Situação'])
    se = next((r for r in d if r.get('Grupo de insumo') == 'Sementes'), {}); co = next((r for r in d if r.get('Grupo de insumo') == 'Combustível'), {})
    chk('CD-05 Cobertura: a Situação diz o estado (o número fica ao lado): Sementes 2 Com concorrência; Combustível 0 Sem fornecedor',
        [se.get('Fornecedores que recebem cotação'), se.get('Situação')] == ['2', 'Com concorrência'] and co.get('Fornecedores que recebem cotação') == '0' and co.get('Situação', '').startswith('Sem fornecedor'), (se, co))
    # ================= CD-06 =================
    abre('CD-06.dc.html'); aba('Itens'); g = Grade(J, 0)
    d = tf03('CD-06 Itens', g, ['Grupo › item', 'Natureza de custo', 'Unidade', 'Embalagem', 'Controle', 'Preço de referência', 'Data do preço', 'Situação'])
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
    d = tf03('CD-06 Locais', g, ['Local', 'Fazenda', 'Tipo', 'Capacidade', 'Itens com este local padrão'])
    g.ordena('Capacidade', desc=True); cp = [x for x in g.col('Capacidade') if x != '—']
    chk('CD-06 Locais: capacidade como número com unidade, ordenada pelo número (60.000 sc de 60 kg antes de 15.000 L)', cp == ['60.000 sc de 60 kg', '15.000 L'], cp)
    # ================= CD-07 =================
    abre('CD-07.dc.html'); g = Grade(J, 0)
    d = tf03('CD-07 Estrutura', g, ['Dimensão › código', 'Nome', 'Origem', 'Início da vigência', 'Fim da vigência', 'Vínculos', 'Conta no ERP (Sankhya)', 'TOP no ERP', 'Situação', 'No rascunho'])
    n1 = next((r for r in d if r.get('Dimensão › código') == '3.1.01'), {}); e2 = next((r for r in d if r.get('Dimensão › código') == '02'), {})
    chk('CD-07: 3.1.01 Fertilizantes e corretivos | 01/07/2026 | 30/06/2027 | 4.1.1.01 | 1201 | Mapeado; 02 Novo no rascunho',
        [n1.get(k) for k in ('Nome', 'Início da vigência', 'Fim da vigência', 'Conta no ERP (Sankhya)', 'TOP no ERP', 'Situação')] == ['Fertilizantes e corretivos', '01/07/2026', '30/06/2027', '4.1.1.01', '1201', 'Mapeado'] and e2.get('No rascunho') == 'Novo', (n1, e2))
    g.ordena('Início da vigência', desc=True); bl = por_grupo(g, 'Início da vigência')
    chk('CD-07: ordenar Início da vigência por data dentro da dimensão', bl and all(crescente([instante(x) for x in b], True) or len(set(b)) < 2 for b in bl), bl[:2])
    g.filtra('Origem', ['Culturas e cultivares']); fl = {r.get('Origem') for r in g.dicts(True)}
    chk('CD-07: filtro Origem = Culturas e cultivares → só os códigos de cultura', fl == {'Culturas e cultivares'} and len(g.dicts(True)) == 5, len(g.dicts(True)))
    limpa(J); shot('cd07-1440')
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
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
