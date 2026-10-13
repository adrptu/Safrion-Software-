# -*- coding: utf-8 -*-
"""Comercial e logística · contas da semente e da tarefa do proprietário (ESPECIFICACAO.md §6 e §8.1).
Uso: python3 docs/comercial/verificacao/contas.py  → uma linha por conta e 'FALHAS: 0' no fim.
Decimal (ENG-013); datas pelo calendário. Números sintéticos (a Lagoa Grande é sintética)."""
from decimal import Decimal as D, ROUND_HALF_UP
import datetime as dt
F = []
def ok(k, cond, info=''):
    print(('OK    ' if cond else 'FALHA ') + k + ('' if cond else ' · ' + str(info)))
    if not cond: F.append(k)
q2 = lambda x: x.quantize(D('0.01'), ROUND_HALF_UP)
SC = D(60)                                   # Soja: sc 60 kg (CULTURA_UN; D-19 da Colheita)
dia = lambda s: dt.date.fromisoformat(s)
venc = lambda d0, n: (dia(d0) + dt.timedelta(days=n)).isoformat()
valor = lambda base, pmassa, preco: q2(base / pmassa * preco)   # comValor: base ÷ massa da unidade de preço × preço

# KC01 · valor e unidade
ok('KC01 616 sc × R$ 128,00/sc = R$ 78.848,00; 36.960 kg = 616 sc', valor(D(36960), SC, D('128')) == D('78848.00') and D(36960) / SC == 616)
# KC02 · soja em estoque (semente da Colheita: L10-031, RS-0001, PV-030)
fis, rs1, pv30 = D(2305200), D(232500), D(240000)
disp = fis - rs1; falta = pv30 - rs1
ok('KC02 L10-031 38.420 sc · reservado 3.875 · disponível 34.545 · falta do PV-030 125 · livre agora 34.420 sc',
   fis / SC == 38420 and rs1 / SC == 3875 and disp / SC == 34545 and falta / SC == 125 and (disp - falta) / SC == 34420)
# KC03 · reservar a falta (125 sc)
rs2 = falta; disp2 = fis - rs1 - rs2
ok('KC03 RS nova 7.500 kg (125 sc) · disponível 34.420 sc · falta 0', rs2 == 7500 and disp2 / SC == 34420 and pv30 - rs1 - rs2 == 0)
# KC04 · saída da RM-0002 (bitrem do cliente): bruto 51.200, tara 14.240; consome a reserva mais antiga primeiro
liq = D(51200) - D(14240); fis3 = fis - liq; rs1b = rs1 - liq; res3 = rs1b + rs2; disp3 = fis3 - res3
ok('KC04 líquido 36.960 kg = 616 sc · físico 37.804 sc · RS-0001 195.540 kg · reservado 3.384 sc · disponível 34.420 sc (igual) · falta 0',
   liq == 36960 and fis3 / SC == 37804 and rs1b == 195540 and res3 / SC == 3384 and disp3 / SC == 34420 and pv30 - liq - res3 == 0)
# KC05 · a receber e vencimentos (sem recebimento registrado no protótipo, D-07)
ar30 = valor(liq, SC, D('128')); ar37 = valor(D(30490), D(1), D('3.00'))
ok('KC05 PV-030 R$ 78.848 vence 26/09 (à vista na entrega) · PV-037 R$ 91.470 vence 15/10 (17/09 + 28 d) · total R$ 170.318',
   ar30 == D('78848.00') and venc('2026-09-26', 0) == '2026-09-26' and ar37 == D('91470.00') and venc('2026-09-17', 28) == '2026-10-15' and ar30 + ar37 == D('170318.00'))
# KC06 · preço médio contratado (ponderado; natureza Venda; CPR e barter fora)
soja_v = D(4000) * 128 + D(12000) * 132; soja_q = D(16000)
mam_v = D(10000) * D('3.05') + D(30490) * D('3.00') + D(30000) * D('3.10'); mam_q = D(10000 + 30490 + 30000)
ok('KC06 soja R$ 131,00/sc (R$ 2.096.000 ÷ 16.000 sc) · mamão R$ 3,05/kg (R$ 214.970 ÷ 70.490 kg) · realizado mamão R$ 3,00/kg',
   q2(soja_v / soja_q) == D('131.00') and mam_v == D('214970.00') and q2(mam_v / mam_q) == D('3.05') and q2(ar37 / D(30490)) == D('3.00'))
# KC07 · soja 26/27: oferta publicada × vendas futuras (CT-203, CRE-0095, BT-090 no estado)
pub = D(614400 + 565440 + 1126440 + 734400 + 357120 + 376200 + 316800); fut = D(12000 + 6900 + 1000) * SC
ok('KC07 oferta 68.180 sc · vendas futuras 19.900 sc · livre 48.280 sc', pub / SC == 68180 and fut / SC == 19900 and (pub - fut) / SC == 48280)
# KC08 · mamão: estoque agora e S41 (sem versão publicada)
ok('KC08 mamão estoque: apto 0 − falta do PV-036 10.000 = déficit 10.000 kg · S41: 0 − 30.000 = déficit 30.000 kg', D(0) - 10000 == -10000 and D(0) - 30000 == -30000)
# KC09 · crédito da Frutas Real na saída do PV-036 (limite do CD-05 R$ 120.000 até 31/12/2026)
exp = ar37 + valor(D(10000), D(1), D('3.05'))
ok('KC09 a receber 91.470 + saída 30.500 = R$ 121.970 > R$ 120.000 → gestor aprova', exp == D('121970.00') and exp > 120000)
# KC10 · entrega com devolução de 400 kg (maturação avançada)
ent = D(10000) - 400
ok('KC10 entregue 9.600 kg · a receber R$ 29.280 · vence 24/10 (26/09 + 28 d) · falta do PV-036 400 kg',
   valor(ent, D(1), D('3.05')) == D('29280.00') and venc('2026-09-26', 28) == '2026-10-24' and D(10000) - ent == 400)
# KC11 · quantidade prevista da carga = mín(reserva não programada, capacidade do veículo)
prev = min(pv30, D(37000))
ok('KC11 bitrem 37 t: previsto 37.000 kg = 616,67 sc', prev == 37000 and q2(prev / SC) == D('616.67'))
# KC12 · limite vencido (Rede Hortifrúti BA, CD-05 limv 31/08/2026) na data operacional 26/09/2026
ok('KC12 31/08/2026 < 26/09/2026 → limite vencido', dia('2026-08-31') < dia('2026-09-26'))
# KC13 · CPR CRE-0095: equivalente R$ 820.000 ÷ 6.900 sc
ok('KC13 CPR R$ 118,84/sc equivalente (fora do preço médio)', q2(D(820000) / 6900) == D('118.84'))
# KC14 · depois da tarefa da Colheita (L39-133 12.050 kg Liberado; 10.000 kg reservados ao PV-036)
ok('KC14 mamão estoque: apto 12.050 · compromissos 10.000 · coberto 10.000 · livre 2.050 kg', D(12050) - D(10000) == 2050)
# ---- v1.1 · revisão por contraexemplo (CE-nn em DECISOES.md) ----
# KC15 · AC-13: três saídas de uma reserva de 10.000 kg zeram a reserva em decimal; em float sobra resto (CE-17)
v3 = [valor(D(x), D(1), D('3.05')) for x in ('3333.3', '3333.3', '3333.4')]   # um arredondamento por saída (evento)
ok('KC15 10.000 − 3.333,3 − 3.333,3 − 3.333,4 = 0 exato (float deixa resto); valores 10.166,57 + 10.166,57 + 10.166,87 = R$ 30.500,01 (centavo do arredondamento por evento)',
   D(10000) - D('3333.3') - D('3333.3') - D('3333.4') == 0 and (10000 - 3333.3 - 3333.3 - 3333.4) != 0
   and v3 == [D('10166.57'), D('10166.57'), D('10166.87')] and sum(v3) == D('30500.01'))
# KC16 · linha Estoque do Painel fecha quando venda futura reserva estoque (CE-12): PV-038 reserva os 2.050 kg livres do L39-133
apto, pv36, res38 = D(12050), D(10000), D(2050)
comp = pv36 + res38; livre = (apto - pv36 - res38) - 0
ok('KC16 mamão estoque: oferta 12.050 − compromissos 12.050 (10.000 do PV-036 + 2.050 reservados ao PV-038) = livre 0; v1.0 dava 12.050 − 10.000 ≠ 0',
   comp == 12050 and livre == 0 and apto - comp == livre and apto - pv36 != livre)
# KC17 · em 05/10 (S41 começou), venda futura de período começado conta no estoque e lote vencido sai do livre (CE-02)
hoje = '2026-10-05'; vence133 = '2026-09-29'; ini_s41 = '2026-10-05'
livre_v11 = D(0) - 0 - D(30000)          # disponível não vencido 0 − falta das prontas 0 − falta da PV-038 (período começado)
livre_v10 = D(2050) - 0                  # v1.0: disponível do L39-133 vencido − falta só das prontas; PV-038 fora de tudo
ok('KC17 05/10: L39-133 vencido (29/09) fora do livre; PV-038 conta no estoque → déficit 30.000 kg (v1.0 mostrava 2.050 kg livres)',
   dia(vence133) < dia(hoje) and ini_s41 <= hoje and livre_v11 == -30000 and livre_v10 == 2050)
# KC18 · excesso de peso na saída (CE-03): 10.040 kg pesados para 10.000 reservados ao PV-036; excesso sai do disponível com a gestora
liq18 = D(10040); exc = liq18 - pv36; disp18 = D(2050) - exc; fis18 = apto - liq18; v18 = valor(liq18, D(1), D('3.05'))
ok('KC18 excesso 40 kg: disponível do L39-133 2.050 → 2.010 · físico 2.010 · falta 0 · R$ 30.622,00 · exposição 122.092 > 121.970 aprovado (aprova de novo)',
   exc == 40 and disp18 == 2010 and fis18 == 2010 and pv36 - liq18 <= 0 and v18 == D('30622.00') and ar37 + v18 == D('122092.00') and ar37 + v18 > D('121970'))
# KC19 · A-17 (Codex 6070584991): a massa da saca dos contratos legados de soja não é decidida pela semente; com 50 kg ou 60 kg registrados,
# os compromissos 26/27 (19.900 sc) e a oferta livre fecham em kg pela massa de cada contrato, nunca pelo cadastro atual da cultura
oferta2627 = D(4090800); comp_sc = D(12000) + D(6900) + D(1000)
c60, c50 = comp_sc * 60, comp_sc * 50
ok('KC19 19.900 sc × 60 kg = 1.194.000 kg (livre 2.896.800 kg = 48.280 sc); × 50 kg = 995.000 kg (livre 3.095.800 kg = 51.596,67 sc de 60 kg; +199.000 kg); CT-203 12.000 sc 50 kg × R$ 132,00 = R$ 1.584.000,00 (o valor do acordo não depende da massa)',
   c60 == 1194000 and oferta2627 - c60 == 2896800 and (oferta2627 - c60) / SC == 48280 and c50 == 995000 and oferta2627 - c50 == 3095800
   and q2((oferta2627 - c50) / SC) == D('51596.67') and c60 - c50 == 199000 and q2(D(12000) * D('132')) == D('1584000.00'))
# KC20 · PV-030 com 50 kg: 4.000 sc = 200.000 kg; a RS-0001 (232.500 kg) fica 32.500 kg acima da venda = 650 sc de 50 kg (Em risco: cancelar e reservar de novo)
ok('KC20 PV-030 com 50 kg: 200.000 kg; RS-0001 232.500 kg acima em 32.500 kg = 650 sc 50 kg', D(4000) * 50 == 200000 and (rs1 - D(4000) * 50) / 50 == 650)
print('FALHAS:', len(F))
