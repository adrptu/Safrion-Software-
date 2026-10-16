# -*- coding: utf-8 -*-
"""Conferência executável da MAPA-MIP-PROD, parte 2 (arquivo sintético completo: limpeza, médias, células) e parte 3 (Alavancas).
Dados 100 % sintéticos com efeitos plantados e semente fixa. numpy/scipy para a estatística; Decimal para dinheiro.
Uso: python3 -I mapa_alavancas_chk.py [semente]"""
import sys, math, itertools, hashlib, io
from decimal import Decimal as D, ROUND_HALF_UP
import numpy as np
from scipy import stats
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261016
rng = np.random.default_rng(SEED)
OK = []
def chk(n, c, info=''):
    OK.append(bool(c)); print(('OK    ' if c else 'FALHA ') + n + (' · ' + str(info) if info != '' else ''))
r2 = lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)

# ---------- talhão P1 (pivô) · Soja · safra 2024/25 sintética · 95 ha no cadastro · células do desenho (inicio.py _pixels: CS=16, P1 'circ' 700,158,104)
HA = 95.0; R = math.sqrt(HA * 1e4 / math.pi); S = R / 104.0           # metros por px do desenho
cells = []
for gy in range(0, 620, 16):
    for gx in range(0, 1000, 16):
        cx, cy = gx + 8, gy + 8
        if (cx - 700) ** 2 + (cy - 158) ** 2 <= 104 ** 2: cells.append((gx, gy, (cx - 700) * S, -(cy - 158) * S))
n = len(cells); X = np.array([c[2] for c in cells]); Y = np.array([c[3] for c in cells]); LADO = 16 * S
print(f'P1: {n} células do desenho · lado {LADO:.1f} m · {HA / n:.4f} ha por célula (área do cadastro ÷ células)')
idx = {(c[0], c[1]): i for i, c in enumerate(cells)}
# ---------- verdade plantada por célula (o que a análise enxerga na célula; erro de interpolação dos laudos fica fora deste teste)
K = 60 + 18 * np.sin(X / 170) * np.cos(Y / 210) + 0.018 * X + rng.normal(0, 3, n)          # mg/dm³ · EFEITO +0,20 sc/ha por mg/dm³
ARG = 35 + 9 * np.cos((X + Y) / 260) + rng.normal(0, 1.5, n)                               # % · EFEITO +0,15 sc/ha por ponto %
CTC = 1.5 + 0.2 * ARG + rng.normal(0, 0.35, n)                                              # cmolc/dm³ · sem efeito próprio (confundida com argila)
MO = 2.6 + 0.4 * np.sin(Y / 140 + 1) + rng.normal(0, 0.12, n)                              # % · NULA
P = 18 + 5 * np.cos(X / 120) + rng.normal(0, 2, n)                                          # mg/dm³ · NULA
PH = 5.4 + 0.25 * np.sin((X - Y) / 200) + rng.normal(0, 0.06, n)                           # CaCl₂ · NULA
V = 30 + 40 * (PH - 4.8) + rng.normal(0, 2.0, n)                                            # % · NULA (confundida com pH)
ang = (np.degrees(np.arctan2(Y, X)) + 360) % 360; SET = (ang // 90).astype(int) + 1          # setores do pivô (1 a 4)
DEF = np.array([{1: 14, 2: 18, 3: 58, 4: 16}[s] for s in SET], dtype=float)                 # mm acumulados · EFEITO −0,10 sc/ha por mm
TRUE = dict(K=0.20, DEF=-0.10, ARG=0.15, CTC=0.0, MO=0.0, P=0.0, PH=0.0, V=0.0)
YC = 60 + 0.20 * (K - 60) - 0.10 * (DEF - 16) + 0.15 * (ARG - 35) + rng.normal(0, 2.0, n)   # sc/ha verdadeiro da célula
NDVI = 0.62 + 0.004 * (YC - 60) + rng.normal(0, 0.015, n)                                   # indicador (efeito da produtividade)

# ---------- PARTE 2 · arquivo do monitor de colheita sintético (passadas E–O a cada 9 m; 1 ponto a cada 5 s)
rows = []
for pi_, yy in enumerate(np.arange(-R + 4.5, R, 9.0)):
    half = math.sqrt(max(R * R - yy * yy, 0)) + 12.0                                           # a máquina passa 12 m além da borda
    x = -half; k = 0; seg = []
    while x <= half:
        v = rng.normal(6.0, 0.4); dist = v / 3.6 * 5; seg.append([x, yy, v, dist, pi_ + 1]); x += dist
    for j, (xx, y2, v, dist, pas) in enumerate(seg):
        gx = int((700 + xx / S) // 16 * 16); gy = int((158 - y2 / S) // 16 * 16)
        ci = idx.get((gx, gy))
        if ci is None:   # célula de borda sem centro dentro do círculo: usa a célula mais próxima
            ci = int(np.argmin((X - xx) ** 2 + (Y - y2) ** 2))
        y_sc = YC[ci] + rng.normal(0, 3.0)
        U = rng.uniform(14.5, 19.0); area = 9.0 * dist / 1e4
        massa = y_sc * 60 * (100 - 14) / (100 - U) * area                                       # kg úmidos no intervalo
        rows.append(dict(x=xx, y=y2, v=v, dist=dist, pas=pas, U=U, massa=massa, j=j, nseg=len(seg)))
N0 = len(rows); m = np.array
# defeitos plantados
for r in rows:
    if r['j'] < 2 or r['j'] >= r['nseg'] - 2: r['massa'] *= 0.35                              # enchimento e esvaziamento no fim da passada
sel = rng.choice(N0, size=int(0.01 * N0), replace=False)
for i in sel: rows[i]['v'] = 1.2; rows[i]['dist'] = 1.2 / 3.6 * 5                           # parada ou manobra lenta
sel = rng.choice(N0, size=int(0.005 * N0), replace=False)
for i in sel: rows[i]['U'] = 0.0                                                             # umidade inválida
sel = rng.choice(N0, size=int(0.005 * N0), replace=False)
for i in sel: rows[i]['massa'] *= 2.5                                                        # pico do sensor
# CSV canônico (separador ;, decimal ,) e SHA-256 para a idempotência
# lat/lon pela mesma conversão linear do tgCirculo (talgeo.js: 111.320 m por grau de longitude × cos(lat) e 110.540 m por grau de latitude),
# com o centro do P1 no pxCoord do desenho (inicio.py:755): (700, 158) → −15,54727 · −54,29720
LAT0 = -15.5612 - (158 - 556) * 0.000035; LON0 = -54.2987 + (700 - 650) * 0.00003
print(f'centro do P1: {LAT0:.5f} · {LON0:.5f} · raio pela área do cadastro {R:.1f} m')
buf = io.StringIO(); buf.write('lat;lon;passada;vel_kmh;largura_m;dist_m;umid_pct;massa_kg\n')
for r in rows:
    la = LAT0 + r['y'] / 110540; lo = LON0 + r['x'] / (111320 * math.cos(math.radians(LAT0)))
    buf.write(f'{la:.8f};{lo:.8f}'.replace('.', ',') + f";{r['pas']};" + ';'.join(f'{v:.3f}'.replace('.', ',') for v in (r['v'], 9.0, r['dist'], r['U'], r['massa'])) + '\n')
SHA = hashlib.sha256(buf.getvalue().encode('utf-8')).hexdigest()
print(f'arquivo sintético: {N0} pontos · {len(buf.getvalue().encode()) / 1e6:.2f} MB · SHA-256 {SHA}')
# ---------- limpeza (ordem fixa; cada ponto leva o 1º motivo)
x = m([r['x'] for r in rows]); y = m([r['y'] for r in rows]); v = m([r['v'] for r in rows]); dist = m([r['dist'] for r in rows])
U = m([r['U'] for r in rows]); massa = m([r['massa'] for r in rows]); jj = m([r['j'] for r in rows]); ns = m([r['nseg'] for r in rows])
area = 9.0 * dist / 1e4; kg14 = np.where(U > 0, massa / area * (100 - U) / (100 - 14), np.nan); sc = kg14 / 60
rho = np.hypot(x, y); motivo = np.array([''] * N0, dtype=object)
def marca(cond, nome):
    mk = (motivo == '') & cond; motivo[mk] = nome; return int(mk.sum())
cont = {}
cont['fora do talhão'] = marca(rho > R, 'fora do talhão')
cont['umidade inválida (fora de 8 a 40 %)'] = marca((U < 8) | (U > 40), 'umidade')
cont['velocidade fora de 3 a 10 km/h'] = marca((v < 3) | (v > 10), 'velocidade')
# início e fim de passada: os 2 primeiros e os 2 últimos pontos DENTRO do talhão de cada passada
ini_fim = np.zeros(N0, bool)
pas = m([r['pas'] for r in rows])
for p_ in np.unique(pas):
    ii = np.where((pas == p_) & (rho <= R))[0]
    if len(ii): ini_fim[ii[:2]] = True; ini_fim[ii[-2:]] = True
cont['início ou fim de passada (2 pontos)'] = marca(ini_fim, 'passada')
cont['borda (a menos de 9 m do contorno)'] = marca(R - rho < 9.0, 'borda')
ok = motivo == ''; med = np.median(sc[ok]); mad = np.median(np.abs(sc[ok] - med)); lim = 3 * 1.4826 * mad
cont['fora da mediana ± 3 × 1,4826 × MAD'] = marca(np.abs(sc - med) > lim, 'outlier')
val = motivo == ''; NV = int(val.sum())
print('prévia · entrou', NV, 'de', N0, '·', {k: v_ for k, v_ in cont.items()})
media = float(np.sum(kg14[val] * area[val]) / np.sum(area[val]) / 60)       # média ponderada pela área dos pontos (sc/ha, 14 %)
simples = float(np.mean(sc[val])); cobre = float(np.sum(area[val]))
APUR = 57.20                                                                  # produtividade apurada sintética (romaneio, base 14 %, sem impureza): 5.434 sc em 95 ha
dif = (media - APUR) / APUR * 100
print(f'média ponderada {media:.4f} sc/ha · média simples {simples:.4f} · área coberta {cobre:.2f} ha ({cobre / HA * 100:.2f} %) · apurada {APUR} · diferença {dif:+.2f} %')
chk('C1 prévia: soma dos motivos + válidos = total de pontos', sum(cont.values()) + NV == N0)
chk('C1 cada defeito plantado cai num motivo (todos os motivos com contagem > 0)', all(v_ > 0 for v_ in cont.values()), cont)
chk('C2 média ponderada pela área ≠ média simples (pontos com área diferente)', abs(media - simples) > 1e-6, f'{media:.4f} × {simples:.4f}')
# sem limpeza (mutante): picos, paradas e cabeceiras entram
suj = (rho <= R) & (U > 0)
media_suja = float(np.sum(kg14[suj] * area[suj]) / np.sum(area[suj]) / 60)
chk('C3 mutante sem limpeza muda a média (mais de 0,5 sc/ha)', abs(media_suja - media) > 0.5, f'{media_suja:.2f} × {media:.2f}')
chk('C4 diferença mapa × apurada visível e calculada sobre a apurada (5.434 sc ÷ 95 ha = 57,20 sc/ha)', abs(dif - (media - 57.20) / 57.20 * 100) < 1e-12 and abs(5434 / 95 - 57.2) < 1e-12, f'{dif:+.2f} %')
# ---------- células: IDW (potência 2, k = 12, raio = maior entre 15 m e meia diagonal da célula); célula sem ponto no raio = sem registro
RAIO = max(15.0, LADO * math.sqrt(2) / 2); xv, yv, sv = x[val], y[val], sc[val]
YI = np.full(n, np.nan)
for i in range(n):
    d2 = (xv - X[i]) ** 2 + (yv - Y[i]) ** 2; o = np.argsort(d2)[:12]; o = o[d2[o] <= RAIO ** 2]
    if len(o): w = 1 / np.maximum(d2[o], 1e-6); YI[i] = np.sum(w * sv[o]) / np.sum(w)
semreg = int(np.isnan(YI).sum())
print(f'células com valor {n - semreg} de {n} · raio {RAIO:.1f} m · correlação célula IDW × verdade {np.corrcoef(YI[~np.isnan(YI)], YC[~np.isnan(YI)])[0, 1]:.3f}')
chk('C5 toda célula do pivô tem ponto no raio (sem registro = 0 aqui; célula vazia ficaria "sem registro", nunca zero)', semreg == 0, semreg)

# ---------- PARTE 3 · Alavancas: unidade = célula (no protótipo a célula do desenho já tem ≈ 0,71 ha, o tamanho do bloco de inferência)
VARS = [('K', 'K (mg/dm³)', K, 'controlável (adubação)'), ('DEF', 'Déficit hídrico acumulado (mm)', DEF, 'controlável (irrigação)'),
        ('ARG', 'Argila (%)', ARG, 'condição'), ('CTC', 'CTC (cmolc/dm³)', CTC, 'condição'), ('MO', 'MO (%)', MO, 'condição'),
        ('P', 'P (mg/dm³)', P, 'controlável (adubação)'), ('PH', 'pH (CaCl₂)', PH, 'controlável (calagem)'), ('V', 'V (%)', V, 'controlável (calagem)')]
yv_ = YI; NMIN = 30
chk('E0 n de células com valor ≥ n mínimo 30', np.sum(~np.isnan(yv_)) >= NMIN, int(np.sum(~np.isnan(yv_))))
# n efetivo por par (Clifford, Richardson e Hémon 1989): Var(r) ≈ [n + Σ_k n_k ρx(k) ρy(k)] / n², n_ef = 1 + 1/Var(r);
# ρ(k) = correlograma de Moran na classe de distância k (k = 1..7 células, metade da extensão do pivô), pares ordenados
CX = np.array([c[0] for c in cells]) / 16.0; CY = np.array([c[1] for c in cells]) / 16.0
DM = np.rint(np.hypot(CX[:, None] - CX[None, :], CY[:, None] - CY[None, :])).astype(int); KMAX = 7
CL = [(DM == k) for k in range(1, KMAX + 1)]; NK = [int(c.sum()) for c in CL]
def correlograma(a):
    z = a - a.mean(); s2 = np.mean(z * z); return [float(z @ c @ z / (nk * s2)) for c, nk in zip(CL, NK)]
def n_ef(a, b):
    ra, rb = correlograma(a), correlograma(b); var = (n + sum(nk * x * y for nk, x, y in zip(NK, ra, rb))) / n ** 2; return 1 + 1 / var
res = {}
for k, nome, arr, tipo in VARS:
    rs, p0 = stats.spearmanr(arr, yv_); ne = n_ef(stats.rankdata(arr), stats.rankdata(yv_))
    se = math.sqrt(1.06 / (ne - 3)); z = math.atanh(rs); tt = rs * math.sqrt((ne - 2) / (1 - rs * rs)); p = 2 * stats.t.sf(abs(tt), ne - 2)
    res[k] = dict(nome=nome, rs=rs, p=p, p0=p0, ne=ne, lo=math.tanh(z - 1.96 * se), hi=math.tanh(z + 1.96 * se), tipo=tipo)
# BH (FDR) sobre as 8 variáveis candidatas, com os p do n efetivo
ps = np.array([res[k]['p'] for k, *_ in VARS]); o = np.argsort(ps); mm = len(ps); qv = np.empty(mm)
acc = 1.0
for r_, i in reversed(list(enumerate(o))): acc = min(acc, ps[i] * mm / (r_ + 1)); qv[i] = acc
for (k, *_), q_ in zip(VARS, qv): res[k]['q'] = q_
ps0 = np.array([res[k]['p0'] for k, *_ in VARS]); o0 = np.argsort(ps0); q0 = np.empty(mm); acc = 1.0
for r_, i in reversed(list(enumerate(o0))): acc = min(acc, ps0[i] * mm / (r_ + 1)); q0[i] = acc
for (k, *_), q_ in zip(VARS, q0): res[k]['q0'] = q_
rsn, pn = stats.spearmanr(NDVI, yv_)
print('\nSpearman (n = %d células) · n efetivo por par (CRH 1989, correlograma de Moran até %d células) · IC 95 %% por Fisher z com EP = √(1,06/(n_ef−3)) · q = BH sobre 8' % (n, KMAX))
for k, *_ in VARS:
    r = res[k]; print(f"   {r['nome']:32s} ρ = {r['rs']:+.3f} [{r['lo']:+.3f}; {r['hi']:+.3f}] · n_ef = {r['ne']:.1f} · p = {r['p']:.4f} · q = {r['q']:.4f} · (sem n_ef: p = {r['p0']:.4f}, q = {r['q0']:.4f}) · {r['tipo']}")
print(f'   NDVI 15/01 (indicador, fora do modelo)  ρ = {rsn:+.3f} · p = {pn:.2g}')
# grupos de variáveis confundidas: |ρ| ≥ 0,7 entre explicativas
G = {k: {k} for k, *_ in VARS}
for (a, _, A, _), (b, _, B, _) in itertools.combinations(VARS, 2):
    rr, _ = stats.spearmanr(A, B)
    if abs(rr) >= 0.7: G[a] |= G[b]; [G.__setitem__(z_, G[a]) for z_ in G[a]]
grupos = sorted({tuple(sorted(g)) for g in G.values() if len(g) > 1})
print('   grupos confundidos (|ρ| ≥ 0,7):', grupos)
# OLS com variáveis padronizadas (efeito relativo) e originais (efeito em sc/ha) + LMG
Xm = np.column_stack([arr for _, _, arr, _ in VARS]); keys = [k for k, *_ in VARS]
def ols(Xa, yy):
    A = np.column_stack([np.ones(len(yy)), Xa]); b, *_ = np.linalg.lstsq(A, yy, rcond=None); e = yy - A @ b
    dof = len(yy) - A.shape[1]; s2 = e @ e / dof; cov = s2 * np.linalg.inv(A.T @ A); return b, np.sqrt(np.diag(cov)), e, dof
b, se, e, dof = ols(Xm, yv_); tq = stats.t.ppf(0.975, dof)
R2full = 1 - e @ e / np.sum((yv_ - yv_.mean()) ** 2)
def r2m(cols):
    if not cols: return 0.0
    _, _, ee, _ = ols(Xm[:, cols], yv_); return 1 - ee @ ee / np.sum((yv_ - yv_.mean()) ** 2)
p_ = len(keys); R2c = {}
for size in range(p_ + 1):
    for c in itertools.combinations(range(p_), size): R2c[c] = r2m(list(c))
lmg = np.zeros(p_)
for j in range(p_):
    others = [i for i in range(p_) if i != j]; tot = 0.0
    for size in range(p_):
        for c in itertools.combinations(others, size):
            w = math.factorial(size) * math.factorial(p_ - size - 1) / math.factorial(p_)
            tot += w * (R2c[tuple(sorted(c + (j,)))] - R2c[c])
    lmg[j] = tot
print(f'\nRegressão (n = {n}, {p_} variáveis) · R² = {R2full:.3f} · Σ LMG = {lmg.sum():.3f}')
for j, k in enumerate(keys):
    lo, hi = b[j + 1] - tq * se[j + 1], b[j + 1] + tq * se[j + 1]
    res[k].update(b=b[j + 1], blo=lo, bhi=hi, lmg=lmg[j])
    print(f"   {res[k]['nome']:32s} β = {b[j + 1]:+.4f} [{lo:+.4f}; {hi:+.4f}] (plantado {TRUE[k]:+.2f}) · LMG {lmg[j]:.3f} ({lmg[j] / R2full * 100:.1f} % do R²)")
chk('E1 Σ LMG = R² do modelo completo', abs(lmg.sum() - R2full) < 1e-9)
chk('E2 efeito plantado de K (+0,20) dentro do IC 95 % de β', res['K']['blo'] <= 0.20 <= res['K']['bhi'], f"[{res['K']['blo']:.4f}; {res['K']['bhi']:.4f}]")
chk('E2 efeito plantado do déficit (−0,10) dentro do IC 95 % de β', res['DEF']['blo'] <= -0.10 <= res['DEF']['bhi'], f"[{res['DEF']['blo']:.4f}; {res['DEF']['bhi']:.4f}]")
nulas = ['MO', 'P', 'PH', 'V']
chk('E4a associação simples (Spearman com n efetivo e FDR): nenhuma nula acusada', all(res[k]['q'] >= 0.05 for k in nulas), {k: round(res[k]['q'], 4) for k in nulas})
falso = [k for k in nulas if res[k]['q0'] < 0.05]
chk('E4b contraprova: tratando as 134 células como independentes (sem n efetivo), pH e V% passariam mesmo com FDR', len(falso) > 0, {k: round(res[k]['q0'], 4) for k in falso})
# teste conjunto (F) de cada grupo confundido: retirar o grupo inteiro do modelo
def f_grupo(cols):
    _, _, e1, d1 = ols(Xm, yv_); rest = [i for i in range(len(keys)) if i not in cols]; _, _, e0, _ = ols(Xm[:, rest], yv_)
    F = ((e0 @ e0 - e1 @ e1) / len(cols)) / (e1 @ e1 / d1); return F, stats.f.sf(F, len(cols), d1)
for g in (('ARG', 'CTC'), ('PH', 'V')):
    F, pf = f_grupo([keys.index(k) for k in g]); res['+'.join(g)] = dict(F=F, p=pf, lmg=sum(lmg[keys.index(k)] for k in g))
    print(f"   grupo {'+'.join(g)}: F = {F:.2f} · p = {pf:.4g} · LMG do grupo {res['+'.join(g)]['lmg']:.3f}")
# confiança do ranking: modelo conjunto (resíduos sem dependência espacial, E7) + BH sobre 6 hipóteses: K, DEF, MO, P e os 2 grupos
pm = {k: 2 * stats.t.sf(abs(res[k]['b'] / ((res[k]['bhi'] - res[k]['blo']) / (2 * tq))), dof) for k in ('K', 'DEF', 'MO', 'P')}
pm['ARG+CTC'] = res['ARG+CTC']['p']; pm['PH+V'] = res['PH+V']['p']
hs = list(pm); pv = np.array([pm[h] for h in hs]); oo = np.argsort(pv); qm = np.empty(len(hs)); acc = 1.0
for r_, i in reversed(list(enumerate(oo))): acc = min(acc, pv[i] * len(hs) / (r_ + 1)); qm[i] = acc
QM = dict(zip(hs, qm)); print('   modelo · p e q (BH, 6 hipóteses):', {h: (f'{pm[h]:.3g}', f'{QM[h]:.3g}') for h in hs})
chk('E3 no modelo: K, déficit e o grupo argila+CTC com q < 0,05', QM['K'] < 0.05 and QM['DEF'] < 0.05 and QM['ARG+CTC'] < 0.05)
chk('E4 no modelo: MO, P e o grupo pH+V% com q ≥ 0,05 e IC de β de MO e P com o zero', QM['MO'] >= 0.05 and QM['P'] >= 0.05 and QM['PH+V'] >= 0.05 and all(res[k]['blo'] <= 0 <= res[k]['bhi'] for k in ('MO', 'P')))
chk('E5b grupo argila+CTC (efeito plantado na argila) significativo em conjunto; grupo pH+V% (nulo) não', res['ARG+CTC']['p'] < 0.05 and res['PH+V']['p'] >= 0.05,
    (round(res['ARG+CTC']['p'], 5), round(res['PH+V']['p'], 4)))
chk('E5c o efeito plantado da argila (+0,15) está no IC de β, mas β sozinho não separa argila de CTC (IC com o zero)', res['ARG']['blo'] <= 0.15 <= res['ARG']['bhi'] and res['ARG']['blo'] <= 0, (round(res['ARG']['blo'], 3), round(res['ARG']['bhi'], 3)))
chk('E5 argila e CTC aparecem como grupo; pH e V% também', ('ARG', 'CTC') in grupos and ('PH', 'V') in grupos, grupos)
# oráculo do BH em Decimal (lista fixa): sem correção 5 passam; com BH a 0,05 só 2
from decimal import getcontext; getcontext().prec = 28
PL = [D('0.001'), D('0.008'), D('0.039'), D('0.041'), D('0.042'), D('0.06')]; mB = len(PL); qd = [None] * mB; acc = D(1)
for i in range(mB - 1, -1, -1): acc = min(acc, PL[i] * mB / (i + 1)); qd[i] = acc
chk('E9 BH em Decimal: p = 0,001 · 0,008 · 0,039 · 0,041 · 0,042 · 0,06 → q = 0,006 · 0,024 · 0,0504 · 0,0504 · 0,0504 · 0,06 (2 passam; sem correção, 5)',
    qd == [D('0.006'), D('0.024'), D('0.0504'), D('0.0504'), D('0.0504'), D('0.06')] and sum(1 for x in PL if x < D('0.05')) == 5 and sum(1 for x in qd if x < D('0.05')) == 2, [str(x) for x in qd])
# NDVI no modelo (mutante): o indicador absorve o efeito das alavancas
b2, se2, _, _ = ols(np.column_stack([Xm, NDVI]), yv_)
chk('E6 mutante NDVI no modelo: β de K encolhe 15 % ou mais (o indicador esconde a alavanca)', abs(b2[1]) <= abs(b[1]) * 0.85, f'{b2[1]:.4f} × {b[1]:.4f} ({(1 - b2[1] / b[1]) * 100:.1f} %)')
# Moran's I dos resíduos (vizinhança por aresta, linhas padronizadas) com teste por permutação (999)
nb = [[idx[(cells[i][0] + dx, cells[i][1] + dy)] for dx, dy in ((16, 0), (-16, 0), (0, 16), (0, -16)) if (cells[i][0] + dx, cells[i][1] + dy) in idx] for i in range(n)]
def moran(z):
    z = z - z.mean(); num = sum(z[i] * np.mean(z[nb[i]]) for i in range(n) if nb[i]); return n / n * num / np.sum(z * z)
Ires = moran(e); perm = np.array([moran(rng.permutation(e)) for _ in range(999)]); pI = (1 + np.sum(perm >= Ires)) / 1000
IK = moran(K - K.mean()); IY = moran(yv_ - yv_.mean()); IPH = moran(PH - PH.mean())
print(f'\nMoran I (vizinhos por aresta): resíduos {Ires:+.3f} (p perm. = {pI:.3f}) · K {IK:+.3f} · pH {IPH:+.3f} · produtividade {IY:+.3f}')
chk('E7 resíduos sem dependência espacial restante (p ≥ 0,05), enquanto K e produtividade são autocorrelacionados (I > 0,3)', pI >= 0.05 and IK > 0.3 and IY > 0.3, (round(Ires, 3), pI, round(IK, 3), round(IY, 3)))
# ganho potencial: |β| × (mediana da faixa boa − mediana da faixa ruim), faixas = quartis da variável; preço sintético do comercial
PRECO = D('129.40')   # dados_comercial.REF Soja em grão (sintético, ex-VE-02)
def faixas(arr, sinal):
    q1, q3 = np.percentile(arr, [25, 75]); ruim = arr <= q1 if sinal > 0 else arr >= q3; boa = arr >= q3 if sinal > 0 else arr <= q1
    return ruim, boa
print()
for k in ('K', 'DEF'):
    arr = dict(K=K, DEF=DEF)[k]; s_ = 1 if res[k]['b'] > 0 else -1; ruim, boa = faixas(arr, s_)
    delta = abs(np.median(arr[boa]) - np.median(arr[ruim])); g = abs(res[k]['b']) * delta
    glo, ghi = sorted([abs(res[k]['blo']) * delta, abs(res[k]['bhi']) * delta]); gt = abs(TRUE[k]) * delta
    area_r = ruim.sum() * HA / n; rs_ha = r2(g) * PRECO
    res[k].update(g=g, glo=glo, ghi=ghi, area=area_r)
    print(f"   {res[k]['nome']}: faixa ruim {ruim.sum()} células ({area_r:.2f} ha) · Δ medianas {delta:.2f} · ganho {g:.2f} sc/ha [{glo:.2f}; {ghi:.2f}] · plantado {gt:.2f} · R$ {rs_ha}/ha · R$ {(rs_ha * r2(area_r)).quantize(D('1'))} na faixa ruim")
    chk(f'E8 ganho plantado de {k} ({gt:.2f} sc/ha) dentro do intervalo do ganho', glo <= gt <= ghi)
# ---------- F3b · teste em faixas: 6 pares (tratamento × testemunha), efeito plantado +3,0 sc/ha; semente própria (SEED + 1)
def ensaio(g):
    bl = g.normal(0, 3, 6); T = 61 + bl + 3.0 + g.normal(0, 1.2, 6); C = 61 + bl + g.normal(0, 1.2, 6); dd = T - C
    md = dd.mean(); sd = dd.std(ddof=1); h = stats.t.ppf(0.975, 5) * sd / math.sqrt(6); return T, C, dd, md, md - h, md + h
g2 = np.random.default_rng(SEED + 1); T, C, dd, md, lo, hi = ensaio(g2)
print(f'\nteste em faixas (semente {SEED + 1}): diferenças {np.round(dd, 2)} · média {md:.2f} sc/ha · IC 95 % [{lo:.2f}; {hi:.2f}] (t com 5 gl = {stats.t.ppf(0.975, 5):.4f})')
chk('F1 efeito plantado (+3,0) dentro do IC e IC sem o zero → "efeito confirmado"', lo <= 3.0 <= hi and lo > 0, (round(lo, 2), round(hi, 2)))
g3 = np.random.default_rng(SEED + 2); sims = [ensaio(g3) for _ in range(4000)]
cob = np.mean([s_[4] <= 3.0 <= s_[5] for s_ in sims]); poder = np.mean([s_[4] > 0 for s_ in sims])
print(f'   4.000 ensaios simulados: cobertura do IC 95 % = {cob * 100:.1f} % · IC sem o zero em {poder * 100:.1f} %')
chk('F1b cobertura do IC entre 94 % e 96 % (o método, não só uma semente)', 0.94 <= cob <= 0.96, round(cob, 4))
lo2 = (T.mean() - C.mean()) - stats.t.ppf(0.975, 5) * math.sqrt(T.var(ddof=1) / 6 + C.var(ddof=1) / 6)
chk('F2 mutante sem pareamento: limite inferior menor (a variação entre blocos alarga o intervalo)', lo2 < lo, (round(lo2, 2), round(lo, 2)))
custo = D('100') * D('2.40')   # 100 kg/ha de KCl × R$ 2,40/kg (preço sintético do KCl no Mapa, OS-0420)
liq = r2(md) * PRECO - custo
print(f'   valor: {r2(md)} sc/ha × R$ {PRECO} = R$ {r2(md) * PRECO}/ha; menos o custo do tratamento R$ {custo}/ha = R$ {liq}/ha')
print('\nRESUMO:', sum(OK), 'de', len(OK), 'conferências passaram · semente', SEED)
