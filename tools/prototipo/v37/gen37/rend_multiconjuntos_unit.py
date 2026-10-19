# -*- coding: utf-8 -*-
"""Teste unitário puro · REND-MULTICONJUNTOS-20261003 (sem navegador, < 5 s).
Roda a MESMA função da tela (bloco REPARTIR de safra.js, no JavaScriptCore do macOS) e o espelho dados2.repartir (Python, com Fraction,
sem arredondar) contra o oráculo do pacote (12 casos Codex · multiconjuntos-oraculo.json), a contraprova Gemini de três conjuntos
(multiconjuntos-gemini-contraprova.json) e as bordas do PRD (rendimento ausente/zero, área zero, janela zero, tarifa desconhecida,
partes acima de 100 %, recurso compartilhado por grupo da fazenda). Cada caso imprime esperado, JS e Python; JS confere com tolerância
relativa 1e-9 (ponto flutuante), Python confere exato (Fraction).
Correções da verificação (rodada 2): a sequência respeita a janela ANTES de dividir a área (PRD 44.3 · casos 05c, S1–S5), a troca da
primeira configuração conta (começa a de menor troca · S3), a pendência diz a causa real (E1, E4, E9, E10), e 400 entradas aleatórias
conferem paridade JS × Python e as invariantes (Σ q + sem conjunto = Q, h ≤ janela própria, sequência ≤ janela da sequência).
REND-RETORNO-1818 (decisão Codex 7ae753dc): necessidade da demanda inteira, atendido na janela e saldo (área + horas) separados. S5 sai do
contrato (54/3,6 + 54/7,2 = 22,5 h necessárias, janela 10 h, déficit 12,5 h), não da saída antiga (17,5 h / 7,5 h, que cortava a parte A na
janela antes de somar); S1 tinha o mesmo corte (6 h → 70/9 h). Novos: S6 (partes fixas ao mesmo tempo, janela própria) e, em todo caso e nas
400 entradas, necessário = atendido + saldo em ha e em horas-conjunto.
PRE-REV-20261004 (pré-revisão do autor): R1 janela 0 numa sequência declarada mantém a necessidade e o déficit (S5 com a janela de A = 0);
R2 o grupo de recursos que junta uma sequência declarada com uma configuração sem janela não relaxa a janela da sequência (1 e 2
plantadeiras); R3 partes que somam 100 % em área grande não deixam resíduo; nas 400 entradas, a sequência declarada cabe na janela dela.
Rodada 2 da revisão: uma restrição de janela por recurso físico (sequência declarada, cada ativo, cada grupo de recursos que serializa) mais
o fecho finito; configuração fora do plano não liga ninguém (T1a–T1c), ponte por outro grupo ou ativo não relaxa janela finita (T2a–T2b),
a troca reservada é a que o decorrido cobra (N1), motivo sem 'dividem a mesma janela' com a outra em janela 0 (M1), fração final no corte
aninhado (M2); nas entradas aleatórias, cada ativo cabe na janela dele e uma configuração ociosa (janela 0, fora do plano) não muda nada.
Rodada 3: sem restrição do fecho (só recurso físico); grupo de recursos decidido pelo maior uso simultâneo real e, com 1 unidade, como um
ativo (P1, P2); janela 0 conta no grupo do plano (P3); empate de troca independe da ordem das linhas (P4); 1 ou 2 unidades: mesma divisão
quando o grupo não limita (P5).
Rodada 4: grupo de 1 unidade conta como "nunca ao mesmo tempo" para os outros grupos (Q1/Q2: colheita de café, colhedora como grupo = como
ativo); configuração que sozinha precisa de mais unidades do que a fazenda tem não trabalha, com motivo e causa (Q3, Q4); busca do uso
simultâneo com poda (Q5: 20 configurações em menos de 1 s).
Rodada 5: o grupo inteiro de quem se exclui duas a duas (clique maximal) divide a maior janela dele (V1–V3: triângulos de sequência, ativo e
grupos de 1 unidade); componente não cordal divide a maior janela finita (V4: ciclo de 5); cadeia simples só por pares (V5); busca por
componente (V6: 24 configurações em pares); o motivo diz o pico real (V7); unidades negativas ignoradas (V8); nas entradas aleatórias, todo
conjunto de configurações que se excluem duas a duas cabe na maior janela delas.
B5a (rodada 5): no pico de um grupo, o próprio grupo não separa os usuários dele; o motivo de um grupo de 1 unidade diz "precisariam de 2" quando
os usuários são independentes (Q1, V9) e "quem a usa divide a janela dela" quando já estão em sequência (P2a).
Rodada 6: trator × implemento (2×2, 3×10, 4×5) é grafo perfeito: só as cliques valem, sem o conservador do componente (W1a–W1d); o grupo que só
passa das unidades no plano não serializa a divisão (W2); cadeia de 28 configurações com 14 operadores não serializa e o motivo diz o pico
real (W3a, W3b); 30 configurações em trios respondem em menos de 1 s, com o conservador e o motivo (W4).
D-01 (5983640246): janela temporal da ocorrência; subgrupo que se exclui com janela finita cabe no maior prazo dele, mesmo com vizinho de prazo
maior ou sem janela (D01a, D01b, D01d, D01e, D01f; controle sem restrição falsa D01c); invariante por cortes por prazo em todo grupo exclusivo,
ativo, sequência e grupo de 1 unidade. Regras mantidas com comunicação fiel: (a) causa da troca reservada (Da); (b) "consideradas em sequência
nesta estimativa" (Db); (c) ajuda sem promessa de término simultâneo ou capacidade máxima (Dc).
Uso: python3 rend_multiconjuntos_unit.py"""
import sys, os, json, re, subprocess, tempfile
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import dados2 as D2
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
# jsc no macOS; fora dele (Linux/nuvem) o node, com print → console.log; o mesmo bloco REPARTIR nos dois
MOTOR,PRELUDIO=([JSC],'') if os.path.exists(JSC) else (['node'],'globalThis.print=(...a)=>console.log(...a);')
src=open(os.path.join(HERE,'safra.js')).read()
m=re.search(r'// >>> REPARTIR.*?// <<< REPARTIR',src,re.S); assert m, 'bloco REPARTIR não encontrado em safra.js'
BLOCO=m.group(0)
DCFG100=[{'id': 'A', 'nome': 'A', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ab', 'ac', 'ad']}, {'id': 'B', 'nome': 'B', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ab', 'bc', 'bd']}, {'id': 'C', 'nome': 'C', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ac', 'bc', 'cd']}, {'id': 'D', 'nome': 'D', 'rend': 1, 'custo_h': 1, 'jan': 100, 'part': 25, 'ativos': ['ad', 'bd', 'cd']}]; DCFGSEM=[{'id': 'A', 'nome': 'A', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ab', 'ac', 'ad']}, {'id': 'B', 'nome': 'B', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ab', 'bc', 'bd']}, {'id': 'C', 'nome': 'C', 'rend': 1, 'custo_h': 1, 'jan': 10, 'part': 25, 'ativos': ['ac', 'bc', 'cd']}, {'id': 'D', 'nome': 'D', 'rend': 1, 'custo_h': 1, 'jan': '', 'part': 25, 'ativos': ['ad', 'bd', 'cd']}]
A=dict(id='A',nome='A 6 m',rend='RA',custo_h=180,diesel=12)          # A (6 m, 8 km/h, 75 %) e B (12 m, 8 km/h, 75 %): rendimento calculado
B=dict(id='B',nome='B 12 m',rend='RB',custo_h=300,diesel=20)
def cf(base,**kw): d=dict(base); d.update(kw); return d
# casos: (id, descrição, Q, configurações, grupos de recursos, {campo: esperado})
CASOS=[
 ('03 paralelo_proporcional_tempo_horas_conjunto','108 ha, 3,6 e 7,2 ha/h, divide pelo rendimento → 36/72 ha, 10 h decorridas, 20 horas-conjunto',
   108,[A,B],None,dict(q=['36','72'],decorrido='10',hconj='20',saldo='0')),
 ('04 particao_fixa_tempo_horas_conjunto','54/54 ha fixos → 15 h decorridas, 22,5 horas-conjunto',
   108,[cf(A,part=50),cf(B,part=50)],None,dict(q=['54','54'],decorrido='15',hconj='45/2')),
 ('05a recurso_compartilhado_troca','36/72 ha com o mesmo operador (sequência) e 1 h de troca → 21 h decorridas, 20 horas-conjunto',
   108,[cf(A,seq=True),cf(B,seq=True,troca=1)],None,dict(decorrido='21',hconj='20',troca='1',conflito=False,**{'nec.decorrido':'21','nec.hconj':'20','falta.hconj':'0'})),
 ('05b mesmo_trator_do_cadastro','mesmo trator a01 nas duas (sem marcar sequência) → em sequência: 20 h decorridas',
   108,[cf(A,ativos=['a01','a06']),cf(B,ativos=['a01','a10'])],None,dict(decorrido='20',hconj='20')),
 ('05c sequencia_nao_cabe_na_janela','a mesma sequência precisaria de 21 h numa janela de 12 h → conflito (faltam 9 h) e a área que não cabe fica sem conjunto: 2 × 5,5 h + 1 h de troca = 12 h; 19,8 + 39,6 = 59,4 ha; 48,6 ha sem conjunto',
   108,[cf(A,seq=True,jan=12),cf(B,seq=True,troca=1,jan=12)],None,dict(conflito=True,deficit='9',decorrido='12',hconj='11',q=['99/5','198/5'],alocado='297/5',saldo='243/5',
   nq=['36','72'],motivo='precisam de 21 h para 108 ha; a janela tem 12 h',**{'nec.hconj':'20','nec.decorrido':'21','falta.hconj':'9','falta.decorrido':'9'})),
 ('S1 sequencia_janela_3h_B4.3','42 ha, 3,6 e 7,2 ha/h em sequência, janela de 3 h → 1,5 h cada: 5,4 + 10,8 = 16,2 ha (≤ 21,6 possíveis), 25,8 ha sem conjunto (≥ 20,4), decorrido 3 h; necessário 42 ÷ 10,8 × 2 = 70/9 h (não 6 h: o plano não corta na janela), déficit 43/9 h',
   42,[cf(A,seq=True,jan=3),cf(B,seq=True,jan=3)],None,dict(q=['27/5','54/5'],alocado='81/5',saldo='129/5',decorrido='3',hconj='3',conflito=True,deficit='43/9',motivo=['mesma janela','precisam de 7,78 h para 42 ha; a janela tem 3 h'],
   **{'nec.decorrido':'70/9','falta.hconj':'43/9','falta.decorrido':'43/9'})),
 ('S2 sequencia_e_paralela','A e B em sequência (janela 3 h) e C 6 ha/h ao mesmo tempo, sem janela, 42 ha → A e B param em 1,5 h; C faz o resto: 5,4 + 10,8 + 25,8 ha, nada sem conjunto, decorrido 4,3 h',
   42,[cf(A,seq=True,jan=3),cf(B,seq=True,jan=3),dict(id='C',nome='C',rend=6,custo_h=200)],None,dict(q=['27/5','54/5','129/5'],saldo='0',decorrido='43/10',hconj='73/10',conflito=True,deficit='2',
   motivo='precisam de 5 h para 27 ha; a janela tem 3 h',**{'nec.hconj':'73/10','falta.hconj':'0','falta.decorrido':'0'})),
 ('S3 troca_na_primeira_P10b','troca de 2 h só na 1ª configuração: começa a de menor troca (B, 0 h) e A entra com 2 h → 22 h decorridas, 20 horas-conjunto',
   108,[cf(A,seq=True,troca=2),cf(B,seq=True)],None,dict(decorrido='22',hconj='20',troca='2')),
 ('S4 grupo_da_fazenda_com_janela','1 plantadeira na fazenda e janela de 12 h → em sequência, 6 h cada: 21,6 + 43,2 ha; 43,2 ha sem conjunto; precisaria de 20 h',
   108,[cf(A,rec={'plant':1},jan=12),cf(B,rec={'plant':1},jan=12)],{'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['108/5','216/5'],saldo='216/5',decorrido='12',conflito=True,deficit='8',motivo='Plantadeiras',
   **{'nec.decorrido':'20','falta.hconj':'8'})),
 ('S5 partes_fixas_em_sequencia','PRD 22.1 · 50 % + 50 % em sequência, janela de 10 h. Necessário (demanda inteira, partilha do usuário): 54/3,6 + 54/7,2 = 22,5 h; janela 10 h; déficit 12,5 h (a saída antiga, 17,5 h / 7,5 h, cortava A em 36 ha antes de somar). Atendido (sem mudar a distribuição): A 36 ha na própria janela, a sequência reduz as duas a 4/7 → 144/7 + 216/7 ha em 10 h; saldo 396/7 ha = faltam 12,5 horas-conjunto; necessário 54 + 54 ha = atendido + saldo',
   108,[cf(A,part=50,seq=True,jan=10),cf(B,part=50,seq=True,jan=10)],None,dict(q=['144/7','216/7'],alocado='360/7',saldo='396/7',hconj='10',decorrido='10',conflito=True,deficit='25/2',nq=['54','54'],
   motivo=['partes fixas em sequência não cabem na janela de 10 h: cada uma faz 57,14 %','precisam de 22,5 h para 108 ha; a janela tem 10 h'],
   **{'nec.area':'108','nec.hconj':'45/2','nec.decorrido':'45/2','falta.area':'396/7','falta.hconj':'25/2','falta.decorrido':'25/2','falta.semHoras':'0'})),
 ('S6 partes_fixas_ao_mesmo_tempo','50 % + 50 % ao mesmo tempo (recursos próprios), janela de 10 h cada: A precisa de 15 h para 54 ha e faz 36 ha; B faz 54 ha em 7,5 h → atendido 90 ha, saldo 18 ha = faltam 5 h (de A); necessário 22,5 horas-conjunto e 15 h decorridas; sem sequência, sem conflito',
   108,[cf(A,part=50,jan=10),cf(B,part=50,jan=10)],None,dict(q=['36','54'],alocado='90',saldo='18',hconj='35/2',decorrido='10',conflito=False,deficit='0',nq=['54','54'],motivo='parte fixa não cabe na janela',
   **{'nec.hconj':'45/2','nec.decorrido':'15','falta.hconj':'5','falta.decorrido':'5'})),
 ('06 capacidade_janela_saldo','36 ha, A 4 h e B 2 h disponíveis → 28,8 ha atendidos, 7,2 ha sem conjunto',
   36,[cf(A,jan=4),cf(B,jan=2)],None,dict(alocado='144/5',saldo='36/5',pendente=False,**{'nec.hconj':'22/3','falta.hconj':'4/3','falta.decorrido':'2/3'})),
 ('07a custos_proporcional','tarifas 180 e 300 R$/h, 36/72 ha → R$ 4.800',108,[A,B],None,dict(custo='4800',custoOk=True)),
 ('07b custos_fixo','54/54 ha → R$ 4.950',108,[cf(A,part=50),cf(B,part=50)],None,dict(custo='4950')),
 ('08 custo_unitario_proporcional','custo por ha = custo total ÷ área atendida = 400/9 (R$ 44,44…/ha), não média de custos',108,[A,B],None,dict(custoHa='400/9')),
 ('10a diesel_recalculado_por_hora','12 e 20 L/h, 36/72 ha → 320 L',108,[A,B],None,dict(diesel='320')),
 ('10b diesel_fixo','54/54 ha → 330 L',108,[cf(A,part=50),cf(B,part=50)],None,dict(diesel='330')),
 ('G1 gemini_tres_conjuntos','150 ha; 4,5/6/7,5 ha/h; janelas 10/8/5 h; 200/250/320 R$/h → 45/48/37,5 ha; 130,5 atendidos; 19,5 sem conjunto; 23 horas-conjunto; 10 h; R$ 5.600',
   150,[dict(id='X',nome='X',rend='9/2',jan=10,custo_h=200),dict(id='Y',nome='Y',rend=6,jan=8,custo_h=250),dict(id='Z',nome='Z',rend='15/2',jan=5,custo_h=320)],None,
   dict(q=['45','48','75/2'],alocado='261/2',saldo='39/2',hconj='23',decorrido='10',custo='5600',custoHa='11200/261',**{'nec.hconj':'105/4','nec.decorrido':'133/12','falta.hconj':'13/4','falta.decorrido':'13/12'})),
 ('E1 rendimento_ausente','rendimento vazio não divide 50 ha: pendente, sem horas (nunca 0 h), área sem conjunto, causa "sem rendimento"',
   50,[dict(id='S',nome='S',rend='',custo_h=100)],None,dict(pendente=True,hconj=None,decorrido=None,saldo='50',motivo='sem rendimento',causa='sem rendimento',**{'nec.hconj':None,'falta.hconj':None,'falta.semHoras':'50'})),
 ('E2 rendimento_zero','rendimento 0 não divide: pendente',50,[dict(id='S',nome='S',rend=0,custo_h=100)],None,dict(pendente=True,hconj=None,saldo='50')),
 ('E3 area_zero','área 0 é válida: 0 horas-conjunto, nada pendente',0,[A],None,dict(pendente=False,hconj='0',decorrido='0',saldo='0',**{'nec.hconj':'0','falta.hconj':'0'})),
 ('E4 janela_zero','janela 0 h com rendimento válido: sem capacidade, os 10 ha ficam sem conjunto; pendente com a causa "sem horas na janela" (não "sem rendimento")',10,[dict(id='J',nome='J',rend=5,jan=0,custo_h=100)],None,
   dict(alocado='0',saldo='10',motivo='janelas não comportam',pendente=True,hconj=None,causa='sem horas na janela',**{'nec.hconj':'2','falta.hconj':'2','falta.decorrido':'2'})),
 ('E9 sem_configuracao','atividade sem configuração: pendente com a causa "sem conjunto"',10,[],None,dict(pendente=True,hconj=None,saldo='10',causa='sem conjunto')),
 ('E10 janela_zero_na_sequencia','a troca (3 h) passa a janela da sequência (2 h): nada cabe, pendente com a causa da troca (regra a, 5983640246)',
   20,[cf(A,seq=True,jan=2,troca=3),cf(B,seq=True,jan=2,troca=3)],None,dict(pendente=True,hconj=None,saldo='20',causa='troca reservada ocupa a janela')),
 ('E5 tarifa_desconhecida','tarifa vazia não vira R$ 0: custo não calculável, R$/ha vazio',108,[A,cf(B,custo_h='')],None,dict(custoOk=False,custoHa=None,motivo='tarifa desconhecida')),
 ('E6 partes_acima_de_100','70 % + 50 % → aviso e conservação (Σ q + sem conjunto = Q)',100,[dict(id='P',nome='P',rend=10,part=70,custo_h=1),dict(id='Q',nome='Q',rend=10,part=50,custo_h=1)],None,
   dict(motivo='partes fixas somam 120',conserva=True)),
 ('E7 invalida_na_divisao_pelo_rendimento','uma configuração sem rendimento na divisão pelo rendimento: a divisão fica pendente (não joga tudo na outra)',
   108,[A,cf(B,rend='')],None,dict(pendente=True,saldo='108',motivo='divisão pelo rendimento fica pendente')),
 ('E8a grupo_da_fazenda_1_plantadeira','duas configurações com plantadeira e a fazenda tem 1 → em sequência: decorrido = horas-conjunto',
   108,[cf(A,rec={'plant':1}),cf(B,rec={'plant':1})],{'plant':{'un':1,'nome':'Plantadeiras'}},dict(decorrido='20',hconj='20',motivo='Plantadeiras')),
 ('E8b grupo_da_fazenda_2_plantadeiras','com 2 plantadeiras trabalham ao mesmo tempo: 10 h',
   108,[cf(A,rec={'plant':1}),cf(B,rec={'plant':1})],{'plant':{'un':2,'nome':'Plantadeiras'}},dict(decorrido='10')),
 ('R1 janela_zero_na_sequencia_declarada','PRE-REV R1 · o S5 com a janela de A = 0: A não recebe área, mas a sequência declarada continua precisando de 54/3,6 + 54/7,2 = 22,5 h numa janela de 10 h (déficit 12,5 h, como com 0,01 h); B faz 54 ha em 7,5 h',
   108,[cf(A,part=50,seq=True,jan=0),cf(B,part=50,seq=True,jan=10)],None,dict(q=['0','54'],alocado='54',saldo='54',hconj='15/2',decorrido='15/2',conflito=True,deficit='25/2',nq=['54','54'],
   motivo=['parte fixa não cabe na janela de 0 h','precisam de 22,5 h para 108 ha; a janela tem 10 h'],**{'nec.decorrido':'45/2','falta.decorrido':'15'})),
 ('R2a grupo_de_recursos_nao_relaxa_janela_1','PRE-REV R2 · A e B em sequência declarada (janela 10 h), C sem janela; A e C usam plantadeira e a fazenda tem 1: a união por falta de plantadeira não tira a janela de A+B (5 h cada, 25 + 25 ha); C faz 150 ha; tudo em sequência: 40 h',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=10,rec={'plant':1},custo_h=100),dict(id='B',nome='B',rend=5,seq=True,jan=10,custo_h=100),dict(id='C',nome='C',rend=5,rec={'plant':1},custo_h=100)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['25','25','150'],saldo='0',decorrido='40',conflito=True,deficit='50/3',motivo=['Plantadeiras','precisam de 26,67 h para 133,33 ha; a janela tem 10 h'])),
 ('T1a ociosa_nao_liga_ativo','rodada 2 · Z (janela 0, sem %, fora do plano) no trator a01 e na sequência declarada com D (sem janela) não junta B+C a D: B e C dividem os 10 h do a01 (25 + 25 ha), conflito de 30 h; D faz 250 ha',
   300,[dict(id='B',nome='B',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='C',nome='C',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='Z',nome='Z',rend=5,jan=0,seq=True,ativos=['a01'],custo_h=1),dict(id='D',nome='D',rend=5,seq=True,custo_h=1)],
   None,dict(q=['25','25','0','250'],conflito=True,deficit='30',decorrido='50',motivo='precisam de 40 h para 200 ha; a janela tem 10 h')),
 ('T1b ociosa_nao_serializa','rodada 2 · A (janela 0, sem %) com os ativos a01 e a02 não põe B (a01) e C (a02) em sequência: 30 + 30 ha em 6 h, sem conflito',
   60,[dict(id='A',nome='A',rend=5,jan=0,ativos=['a01','a02'],custo_h=1),dict(id='B',nome='B',rend=5,jan=6,ativos=['a01'],custo_h=1),dict(id='C',nome='C',rend=5,jan=6,ativos=['a02'],custo_h=1)],
   None,dict(q=['0','30','30'],conflito=False,decorrido='6',saldo='0')),
 ('T1c ociosa_nao_estica_sequencia','rodada 2 · A e B em sequência declarada (janela 3 h); Z (janela 0) na sequência e no a01 de C (janela 20 h) não estica a janela de A+B: 7,5 + 7,5 ha, déficit 71/3 h',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=3,custo_h=1),dict(id='B',nome='B',rend=5,seq=True,jan=3,custo_h=1),dict(id='Z',nome='Z',rend=5,seq=True,jan=0,ativos=['a01'],custo_h=1),dict(id='C',nome='C',rend=5,jan=20,ativos=['a01'],custo_h=1)],
   None,dict(q=['15/2','15/2','0','100'],conflito=True,deficit='71/3',decorrido='20')),
 ('T2a ponte_por_outro_grupo_2','rodada 2 · A sem janela usa 2 tratores, B (janela 2 h) usa trator e operador, C (janela 2 h) usa operador; 2 tratores e 1 operador: B+C dividem os 2 h do operador (5 + 5 ha)',
   100,[dict(id='A',nome='A',rend=5,rec={'trat':2},custo_h=1),dict(id='B',nome='B',rend=5,jan=2,rec={'trat':1,'oper':1},custo_h=1),dict(id='C',nome='C',rend=5,jan=2,rec={'oper':1},custo_h=1)],
   {'trat':{'un':2,'nome':'Tratores'},'oper':{'un':1,'nome':'Operadores'}},dict(q=['90','5','5'],conflito=True,deficit='34/3',decorrido='20')),
 ('T2b ponte_por_outro_grupo_3','rodada 2 · o mesmo com 3 tratores (mais recurso): a mesma divisão, nunca mais otimista com menos; decorrido 18 h',
   100,[dict(id='A',nome='A',rend=5,rec={'trat':2},custo_h=1),dict(id='B',nome='B',rend=5,jan=2,rec={'trat':1,'oper':1},custo_h=1),dict(id='C',nome='C',rend=5,jan=2,rec={'oper':1},custo_h=1)],
   {'trat':{'un':3,'nome':'Tratores'},'oper':{'un':1,'nome':'Operadores'}},dict(q=['90','5','5'],conflito=True,deficit='34/3',decorrido='18')),
 ('T2c ponte_por_sequencia','rodada 2 · B e C no a01 (janela 10 h) e Z (janela 0,01 h) no a01 e na sequência declarada com D (sem janela): B+C+Z dividem os 10 h do a01',
   300,[dict(id='B',nome='B',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='C',nome='C',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='Z',nome='Z',rend=5,jan='1/100',seq=True,ativos=['a01'],custo_h=1),dict(id='D',nome='D',rend=5,seq=True,custo_h=1)],
   None,dict(q=['999/40','999/40','1/20','250'],conflito=True,deficit='35',decorrido='60')),
 ('N1 troca_reservada_e_cobrada','rodada 2 · A e B em sequência (janela 10 h, troca 2 h cada) e C com a plantadeira de A (1 na fazenda): C começa o fecho, A e B pagam a troca; A+B com as trocas cabem nos 10 h (3 + 2 + 3 + 2)',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=10,troca=2,rec={'plant':1},custo_h=1),dict(id='B',nome='B',rend=5,seq=True,jan=10,troca=2,custo_h=1),dict(id='C',nome='C',rend=5,rec={'plant':1},custo_h=1)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['15','15','170'],decorrido='44',conflito=True,deficit='62/3',motivo='precisam de 30,67 h para 133,33 ha; a janela tem 10 h')),
 ('M2 fracao_final_no_corte_aninhado','rodada 2 · A e B (30 % cada, sequência, janela 4 h) e C (40 %, janela 10 h) com a plantadeira de A: dois cortes (sequência e plantadeira); A+B ≤ 4 h e A+C ≤ 10 h; o motivo diz a fração final de cada uma',
   1000,[dict(id='A',nome='A',rend=1,part=30,seq=True,jan=4,rec={'plant':1},custo_h=1),dict(id='B',nome='B',rend=1,part=30,seq=True,jan=4,custo_h=1),dict(id='C',nome='C',rend=1,part=40,jan=10,rec={'plant':1},custo_h=1)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['5/3','2','25/3'],motivo=['janela de 4 h: fazem de 41,67 % a 50 %','janela de 10 h: fazem de 41,67 % a 83,33 %'])),
 ('P1 grupo_ja_no_fecho_por_outro_grupo','rodada 3 · B e C usam trator e o único operador (janelas de 2 h); A sem janela usa 2 tratores: o fecho pelos tratores não apaga a restrição do operador (5 + 5 ha)',
   100,[dict(id='A',nome='A',rend=5,rec={'trat':2},custo_h=1),dict(id='B',nome='B',rend=5,jan=2,rec={'trat':1,'oper':1},custo_h=1),dict(id='C',nome='C',rend=5,jan=2,rec={'trat':1,'oper':1},custo_h=1)],
   {'trat':{'un':2,'nome':'Tratores'},'oper':{'un':1,'nome':'Operadores'}},dict(q=['90','5','5'],conflito=True,deficit='34/3',motivo='Operadores')),
 ('P2a uma_plantadeira_como_grupo','rodada 3 · A e B em sequência com a única plantadeira (janelas de 3 h) e C na sequência sem janela: A+B dividem os 3 h da plantadeira',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=3,rec={'plant':1},custo_h=1),dict(id='B',nome='B',rend=5,seq=True,jan=3,rec={'plant':1},custo_h=1),dict(id='C',nome='C',rend=5,seq=True,custo_h=1)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['15/2','15/2','185'],conflito=True,deficit='71/3',motivo='Plantadeiras: a fazenda tem 1; quem a usa divide a janela dela')),
 ('P2b uma_plantadeira_como_ativo','rodada 3 · o mesmo com a plantadeira como ativo p01 do cadastro: a mesma divisão',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=3,ativos=['p01'],custo_h=1),dict(id='B',nome='B',rend=5,seq=True,jan=3,ativos=['p01'],custo_h=1),dict(id='C',nome='C',rend=5,seq=True,custo_h=1)],
   None,dict(q=['15/2','15/2','185'],conflito=True,deficit='71/3')),
 ('P3 grupo_com_janela_0_no_plano','rodada 3 · o S5 com a plantadeira (1 na fazenda) no lugar da sequência e a janela de A = 0: o grupo do plano conta A; conflito, déficit 12,5 h, necessário 22,5 h',
   108,[cf(A,part=50,jan=0,rec={'plant':1}),cf(B,part=50,jan=10,rec={'plant':1})],{'plant':{'un':1,'nome':'Plantadeiras'}},
   dict(q=['0','54'],conflito=True,deficit='25/2',**{'nec.decorrido':'45/2'})),
 ('P5a fecho_nao_e_restricao_1','rodada 3 · A (a01), B (a01 e a02), C (a02 e plantadeira), D sem janela (plantadeira): cada ativo cabe nos 10 h dele; com 1 plantadeira',
   1000,[dict(id='A',nome='A',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=5,jan=10,ativos=['a01','a02'],custo_h=1),dict(id='C',nome='C',rend=5,jan=10,ativos=['a02'],rec={'plant':1},custo_h=1),dict(id='D',nome='D',rend=5,rec={'plant':1},custo_h=1)],
   {'plant':{'un':1,'nome':'Plantadeiras'}},dict(q=['25','25','25','925'],conflito=True,deficit='90')),
 ('P5b fecho_nao_e_restricao_2','rodada 3 · o mesmo com 2 plantadeiras: a mesma divisão (menos recurso não dá plano mais otimista)',
   1000,[dict(id='A',nome='A',rend=5,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=5,jan=10,ativos=['a01','a02'],custo_h=1),dict(id='C',nome='C',rend=5,jan=10,ativos=['a02'],rec={'plant':1},custo_h=1),dict(id='D',nome='D',rend=5,rec={'plant':1},custo_h=1)],
   {'plant':{'un':2,'nome':'Plantadeiras'}},dict(q=['25','25','25','925'],conflito=True,deficit='90')),
 ('Q1 cafe_colhedora_como_grupo','rodada 4 · colheita de café, 60 ha, janelas de 80 h: A e B com a única colhedora, trator e 2 operadores; C com equipe de 6; 8 operadores: A e B nunca juntas, então cabem 2 + 6 = 8; 20 + 20 + 20 ha, déficit 80/9 h só da colhedora',
   60,[dict(id='A',nome='A',rend='1/2',jan=80,rec={'colh':1,'trator':1,'oper':2},custo_h=1),dict(id='B',nome='B',rend='1/2',jan=80,rec={'colh':1,'trator':1,'oper':2},custo_h=1),dict(id='C',nome='C',rend='7/20',jan=80,rec={'oper':6},custo_h=1)],
   {'colh':{'un':1,'nome':'Colhedoras'},'trator':{'un':4,'nome':'Tratores'},'oper':{'un':8,'nome':'Operadores e equipe'}},dict(q=['20','20','20'],saldo='0',conflito=True,deficit='80/9',motivo='Colhedoras: ao mesmo tempo precisariam de 2, a fazenda tem 1')),   # B5a: o pico da colhedora não se separa por ela mesma
 ('Q2 cafe_colhedora_como_ativo','rodada 4 · o mesmo com a colhedora como ativo colh01 do cadastro: a mesma divisão',
   60,[dict(id='A',nome='A',rend='1/2',jan=80,ativos=['colh01'],rec={'trator':1,'oper':2},custo_h=1),dict(id='B',nome='B',rend='1/2',jan=80,ativos=['colh01'],rec={'trator':1,'oper':2},custo_h=1),dict(id='C',nome='C',rend='7/20',jan=80,rec={'oper':6},custo_h=1)],
   {'colh':{'un':1,'nome':'Colhedoras'},'trator':{'un':4,'nome':'Tratores'},'oper':{'un':8,'nome':'Operadores e equipe'}},dict(q=['20','20','20'],saldo='0',conflito=True,deficit='80/9')),
 ('Q3 equipe_maior_que_o_quadro','rodada 4 · equipe de 10 com 8 operadores na fazenda: não trabalha, pendente com a causa "sem recurso na fazenda" e o motivo',
   10,[dict(id='E',nome='E',rend=1,jan=20,rec={'oper':10},custo_h=1)],{'colh':{'un':1,'nome':'Colhedoras'},'trator':{'un':4,'nome':'Tratores'},'oper':{'un':8,'nome':'Operadores e equipe'}},
   dict(q=['0'],pendente=True,causa='sem recurso na fazenda',saldo='10',motivo='E: precisa de 10 em Operadores e equipe, a fazenda tem 8; não trabalha nesta ocorrência')),
 ('Q4 equipe_maior_com_parte_fixa','rodada 4 · E (equipe de 10, 50 %) e F (1 operador, 50 %): E fica sem conjunto com o motivo; F faz a parte dela',
   100,[dict(id='E',nome='E',rend=1,part=50,jan=100,rec={'oper':10},custo_h=1),dict(id='F',nome='F',rend=1,part=50,jan=100,rec={'oper':1},custo_h=1)],{'colh':{'un':1,'nome':'Colhedoras'},'trator':{'un':4,'nome':'Tratores'},'oper':{'un':8,'nome':'Operadores e equipe'}},
   dict(q=['0','50'],saldo='50',pendente=False,motivo='E: precisa de 10 em Operadores e equipe')),
 ('V1 triangulo_sequencia_ativo_grupo','rodada 5 · A e B em sequência, A e C no a01, B e C na única plantadeira (janelas de 10 h, 1 ha/h, 15 ha): nunca juntas, dividem 10 h: 10/3 ha cada, 5 sem conjunto, déficit 5 h',
   15,[dict(id='A',nome='A',rend=1,jan=10,seq=True,ativos=['a01'],rec={'oper':2},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,seq=True,rec={'plant':1,'oper':4},custo_h=1),dict(id='C',nome='C',rend=1,jan=10,ativos=['a01'],rec={'plant':1,'oper':5},custo_h=1)],
   {'plant':{'un':1,'nome':'Plantadeiras'},'oper':{'un':8,'nome':'Operadores'}},dict(q=['10/3','10/3','10/3'],saldo='5',conflito=True,deficit='5')),
 ('V2 triangulo_de_grupos_de_1','rodada 5 · pulverizador, plantadeira e distribuidor (1 de cada) em triângulo: 10/3 ha cada, déficit 5 h',
   15,[dict(id='A',nome='A',rend=1,jan=10,rec={'pulv':1,'plant':1,'oper':3},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,rec={'plant':1,'dist':1,'oper':3},custo_h=1),dict(id='C',nome='C',rend=1,jan=10,rec={'dist':1,'pulv':1,'oper':3},custo_h=1)],
   {'pulv':{'un':1},'plant':{'un':1},'dist':{'un':1},'oper':{'un':8}},dict(q=['10/3','10/3','10/3'],saldo='5',conflito=True,deficit='5')),
 ('V3 triangulo_puro','rodada 5 · A e B em sequência, B e C no a02, A e C no a01: 10/3 ha cada, déficit 5 h',
   15,[dict(id='A',nome='A',rend=1,jan=10,seq=True,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,seq=True,ativos=['a02'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,ativos=['a01','a02'],custo_h=1)],
   None,dict(q=['10/3','10/3','10/3'],saldo='5',conflito=True,deficit='5')),
 ('V4 ciclo_de_5_sem_corda','rodada 5 · 5 configurações em ciclo de ativos (cada uma divide um com a vizinha): não cordal, o componente divide os 10 h (conservador): 2 ha cada',
   25,[dict(id=f'C{i}',nome=f'C{i}',rend=1,jan=10,ativos=[f'e{i}',f'e{(i+4)%5}'],custo_h=1) for i in range(5)],None,dict(q=['2','2','2','2','2'],saldo='15',conflito=True,deficit='15')),
 ('V5 cadeia_so_por_pares','rodada 5 · A–B no a01 e B–C no a02 (cordal): só os pares dividem janela; B primeiro e A com C ao mesmo tempo: 5 + 5 + 5 ha em 10 h',
   30,[dict(id='A',nome='A',rend=1,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['a01','a02'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,ativos=['a02'],custo_h=1)],
   None,dict(q=['5','5','5'],saldo='15',conflito=True,deficit='10')),
 ('V7 pico_real_no_motivo','rodada 5 · três equipes de 6 operadores com 8 na fazenda: o motivo diz o pico real (18), não o primeiro valor acima de 8',
   60,[dict(id=f'E{i}',nome=f'E{i}',rend='7/20',jan=80,rec={'oper':6},custo_h=1) for i in range(3)],{'oper':{'un':8,'nome':'Operadores e equipe'}},
   dict(motivo='Operadores e equipe: ao mesmo tempo precisariam de 18, a fazenda tem 8')),
 ('V8 unidades_negativas','rodada 5 · grupo com unidades negativas (fora da tela) é ignorado: A, que nem usa o grupo, faz os 30 ha',
   30,[dict(id='A',nome='A',rend=1,jan=30,rec={'oper':1},custo_h=1)],{'plant':{'un':-1},'oper':{'un':8}},dict(q=['30'],saldo='0',pendente=False)),
 ('V9 b5a_pico_do_grupo_de_1','B5a · A e B ao mesmo tempo, cada uma com o único distribuidor: o motivo diz "Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1" (o grupo não se separa por ele mesmo)',
   100,[dict(id='A',nome='A',rend=5,jan=20,rec={'dist':1},custo_h=1),dict(id='B',nome='B',rend=5,jan=20,rec={'dist':1},custo_h=1)],{'dist':{'un':1,'nome':'Distribuidores'}},
   dict(motivo='Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1; trabalham uma de cada vez')),   # regra (b), 5983640246
 ('W1a dois_tratores_duas_plantadeiras','rodada 6 · T1+P1, T1+P2, T2+P1 e T2+P2 (2 ha/h, janelas de 10 h, 80 ha): ciclo de 4 é grafo perfeito; T1+P1 com T2+P2 e depois T1+P2 com T2+P1: 10 ha cada, 40 ha, déficit 10 h',
   80,[dict(id=f'T{t}P{p}',nome=f'T{t}+P{p}',rend=2,jan=10,ativos=[f't{t}',f'p{p}'],custo_h=1) for t in (1,2) for p in (1,2)],None,
   dict(q=['10','10','10','10'],alocado='40',saldo='40',conflito=True,deficit='10',motivo='em sequência precisam de 20 h para 40 ha; a janela tem 10 h')),
 ('W1b dois_por_dois_janela_de_1h','rodada 6 · o mesmo com 200 ha, só T1+P1 com janela de 1 h e as outras sem janela: atende os 200 ha, sem conflito (T1+P1 faz 2 ha)',
   200,[dict(id=f'T{t}P{p}',nome=f'T{t}+P{p}',rend=2,jan=(1 if (t,p)==(1,1) else ''),ativos=[f't{t}',f'p{p}'],custo_h=1) for t in (1,2) for p in (1,2)],None,
   dict(q=['2','66','66','66'],alocado='200',saldo='0',conflito=False)),
 ('W1c dois_por_dois_parte_fixa_janela_0','rodada 6 · T1+P1 com 10 % fixos e janela 0, as outras sem janela, 200 ha: 180 ha atendidos, sem conflito falso de "janela 0 h"',
   200,[dict(id=f'T{t}P{p}',nome=f'T{t}+P{p}',rend=2,jan=(0 if (t,p)==(1,1) else ''),part=(10 if (t,p)==(1,1) else ''),ativos=[f't{t}',f'p{p}'],custo_h=1) for t in (1,2) for p in (1,2)],None,
   dict(q=['0','60','60','60'],alocado='180',saldo='20',conflito=False)),
 ('W1d tres_tratores_dez_implementos','rodada 6 · 3 tratores × 10 implementos (30 configurações, 1 ha/h, janelas de 10 h, 100 ha): cada trator trabalha 10 h, 30 ha (o conservador do componente daria 10)',
   100,[dict(id=f'T{t}P{p}',nome=f'T{t}+P{p}',rend=1,jan=10,ativos=[f't{t}',f'p{p}'],custo_h=1) for t in range(3) for p in range(10)],None,
   dict(alocado='30',saldo='70',conflito=True)),
 ('W2 grupo_so_do_plano_nao_serializa_divisao','rodada 6 · 2 tratores; A e B (janela 10 h, 1 trator cada) e C (20 % fixos, janela 0, 1 trator), 30 ha: no plano 3 > 2, na divisão só A e B, que cabem juntas: 10 + 10 ha, 10 h decorridas',
   30,[dict(id='A',nome='A',rend=1,jan=10,rec={'trat':1},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,rec={'trat':1},custo_h=1),dict(id='C',nome='C',rend=1,part=20,jan=0,rec={'trat':1},custo_h=1)],
   {'trat':{'un':2,'nome':'Tratores'}},dict(q=['10','10','0'],alocado='20',saldo='10',decorrido='10')),
 ('W3a cadeia_de_28_com_14_operadores','rodada 6 · 28 configurações em cadeia (cada uma divide um ativo com a seguinte), 1 operador cada, 14 na fazenda, janelas de 100 h, 2.000 ha: o pico real é 14 (cabe); cada par vizinho divide 100 h: 50 ha cada, 1.400 ha',
   2000,[dict(id=f'K{i}',nome=f'K{i}',rend=1,jan=100,ativos=[f'a{i}',f'a{i+1}'],rec={'op':1},custo_h=1) for i in range(28)],{'op':{'un':14,'nome':'Operadores'}},
   dict(alocado='1400',saldo='600')),
 ('W3b cadeia_de_30_com_10_operadores','rodada 6 · a mesma cadeia com 30 configurações e 10 operadores: o motivo diz o pico real (15), não a soma (30)',
   2000,[dict(id=f'K{i}',nome=f'K{i}',rend=1,jan=100,ativos=[f'a{i}',f'a{i+1}'],rec={'op':1},custo_h=1) for i in range(30)],{'op':{'un':10,'nome':'Operadores'}},
   dict(motivo='Operadores: ao mesmo tempo precisariam de 15, a fazenda tem 10; configurações consideradas em sequência nesta estimativa')),   # regra (b)
 ('D01a subgrupo_finito_com_vizinho_de_100h','D-01 (5983640246) · A, B e C (janelas de 10 h) e D (100 h) se excluem duas a duas, 25 % cada de 16 ha: A+B+C precisariam de 12 h em 10 h; cada uma faz 10/3 ha, D faz 4, 2 ha sem conjunto, déficit 2 h',
   16,DCFG100,None,dict(q=['10/3','10/3','10/3','4'],alocado='14',saldo='2',conflito=True,deficit='2',motivo='em sequência precisam de 12 h para 12 ha; a janela tem 10 h')),
 ('D01b subgrupo_finito_com_vizinho_sem_janela','D-01 · o mesmo com D sem janela: a mesma divisão (um vizinho sem prazo não amplia o dos outros)',
   16,DCFGSEM,None,dict(q=['10/3','10/3','10/3','4'],alocado='14',saldo='2',conflito=True,deficit='2')),
 ('D01c controle_positivo_sem_restricao_falsa','D-01 · controle: as mesmas quatro com 8 ha (2 h cada; A+B+C = 6 h em 10 h): tudo atendido, sem conflito',
   8,DCFG100,None,dict(q=['2','2','2','2'],alocado='8',saldo='0',conflito=False,deficit='0')),
 ('D01d recurso_unico_com_vizinho_sem_janela','D-01 · A e B (janela de 10 h) e D (sem janela) no mesmo a01, 24 ha pelo rendimento: A e B param em 5 h cada (A+B = 10 h), D faz o resto; a partilha do plano (8 + 8) não cabe: déficit 6 h',
   24,[dict(id='A',nome='A',rend=1,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['a01'],custo_h=1),dict(id='D',nome='D',rend=1,ativos=['a01'],custo_h=1)],None,
   dict(q=['5','5','14'],alocado='24',saldo='0',conflito=True,deficit='6')),
 ('D01e prazos_aninhados','D-01 · três no mesmo a01 com prazos 2, 5 e 10 h, 30 ha pelo rendimento (1 ha/h): cortes 2 · 5 · 10 (EDF): A 2, B 3, C 5 ha; déficit pela partilha do plano',
   30,[dict(id='A',nome='A',rend=1,jan=2,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=5,ativos=['a01'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,ativos=['a01'],custo_h=1)],None,
   dict(q=['2','3','5'],alocado='10',saldo='20',conflito=True)),
 ('Da troca_reservada_ocupa_a_janela','regra (a) · A (50 %, janela 10 h) e B (sem %, troca 10 h) em sequência, 10 ha: a troca reservada de B ocupa a janela; pendente com a causa e o motivo da troca',
   10,[dict(id='A',nome='A',rend=1,custo_h=1,jan=10,part=50,seq=True,troca=0),dict(id='B',nome='B',rend=1,custo_h=1,jan=10,seq=True,troca=10)],None,
   dict(q=['0','0'],pendente=True,causa='troca reservada ocupa a janela',motivo=['B: troca de 10 h reservada na janela de 10 h de A e B (sequência declarada)','reduza a troca ou tire B da sequência declarada'])),
 ('Db consideradas_em_sequencia','regra (b) · 3 configurações com 1 trator cada e 2 tratores: o motivo diz "consideradas em sequência nesta estimativa" (não afirma que trabalham em sequência)',
   20,[dict(id='A',nome='A',rend=1,custo_h=1,jan=10,part=50,rec={'trator':1}),dict(id='B',nome='B',rend=1,custo_h=1,jan=10,part=25,rec={'trator':1}),dict(id='C',nome='C',rend=1,custo_h=1,jan=10,part=25,rec={'trator':1})],
   {'trator':{'un':2,'nome':'Tratores'}},dict(motivo='Tratores: ao mesmo tempo precisariam de 3, a fazenda tem 2; configurações consideradas em sequência nesta estimativa')),
 ('R2-2a buraco_por_configuracao_sem_janela','rodada 2 do D-01 · anel de 5 (T1, P2, O3, T3, P1) em que só K0 e K2 têm janela (30 h) e não dividem nada: o buraco passa por configurações sem prazo, que vão por último; K0 e K2 juntas de 0 a 20 h, 20 ha cada, sem conflito',
   100,[dict(id='K0',nome='K0',rend=1,jan=30,ativos=['T1','P1','O1'],custo_h=1),dict(id='K1',nome='K1',rend=1,ativos=['T1','P2','O2'],custo_h=1),dict(id='K2',nome='K2',rend=1,jan=30,ativos=['T2','P2','O3'],custo_h=1),
        dict(id='K3',nome='K3',rend=1,ativos=['T3','P3','O3'],custo_h=1),dict(id='K4',nome='K4',rend=1,ativos=['T3','P1','O4'],custo_h=1)],None,
   dict(q=['20','20','20','20','20'],saldo='0',conflito=False)),
 ('R2-2b buraco_entre_quem_tem_janela','rodada 2 do D-01 · controle positivo: o mesmo anel com as cinco em 30 h continua no conservador e diz isso no motivo (estimativa)',
   100,[dict(id='K0',nome='K0',rend=1,jan=30,ativos=['T1','P1','O1'],custo_h=1),dict(id='K1',nome='K1',rend=1,jan=30,ativos=['T1','P2','O2'],custo_h=1),dict(id='K2',nome='K2',rend=1,jan=30,ativos=['T2','P2','O3'],custo_h=1),
        dict(id='K3',nome='K3',rend=1,jan=30,ativos=['T3','P3','O3'],custo_h=1),dict(id='K4',nome='K4',rend=1,jan=30,ativos=['T3','P1','O4'],custo_h=1)],None,
   dict(q=['6','6','6','6','6'],conflito=True,motivo=['arranjo de recursos compartilhados que esta estimativa não confere exatamente','consideradas em sequência nesta estimativa, precisam de'])),
 ('R2-3 partes_fixas_grupo_inteiro_primeiro','rodada 2 do D-01 · A, B e C (3 ha/h, 12 %, 10 h) e D (4 ha/h, 64 %, 20 h), todas com máquina em comum duas a duas: o grupo inteiro (20 h) reduz as quatro na mesma fração (5/7); A+B+C = 8,57 h ≤ 10 h, então o subgrupo de 10 h não reduz de novo',
   100,[dict(id='A',nome='A',rend=3,part=12,jan=10,ativos=['ab','ac','ad'],custo_h=1),dict(id='B',nome='B',rend=3,part=12,jan=10,ativos=['ab','bc','bd'],custo_h=1),
        dict(id='C',nome='C',rend=3,part=12,jan=10,ativos=['ac','bc','cd'],custo_h=1),dict(id='D',nome='D',rend=4,part=64,jan=20,ativos=['ad','bd','cd'],custo_h=1)],None,
   dict(q=['60/7','60/7','60/7','320/7'],motivo='cada uma faz 71,43 %')),
 ('R2-5b troca_na_mesma_maquina','rodada 2 do D-01 · A e B no mesmo a01 (10 h cada), B com troca de 10 h, sem sequência declarada: o motivo nomeia o grupo e a origem e propõe outro conjunto, não "tirar da sequência"',
   20,[dict(id='A',nome='A',rend=1,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['a01'],troca=10,custo_h=1)],None,
   dict(motivo=['B: troca de 10 h reservada na janela de 10 h de A e B (mesma máquina do cadastro)','reduza a troca ou use outro conjunto para B'])),
 ('R2-5c troca_nomeia_o_grupo','rodada 2 do D-01 · A–B na máquina x e B–C na máquina y, B troca 3 h e C troca 1 h, mesma janela de 10 h: um motivo de troca por grupo e janela, o da maior troca, dizendo de quais configurações é (antes, "B" com 3 h e "B, C" com 4 h na mesma janela, sem dizer o grupo)',
   30,[dict(id='A',nome='A',rend=1,jan=10,ativos=['x'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,troca=3,ativos=['x','y'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,troca=1,ativos=['y'],custo_h=1)],None,
   dict(motivo=['B, C: troca de 4 h reservada na janela de 10 h de B e C (mesma máquina do cadastro)'])),
 ('R3-1a p4_trator_implemento_prazos_diferentes','rodada 3 do D-01 · S2 (anterior ao D-01): A=T1+I1 (1 h), B=T1+I2 (2 h), C=T2+I2 (2 h), D=T2+I3 (1 h), 4 ha: antes 4 ha sem conflito, mas A e D prendem T1 e T2 na 1ª hora e B+C precisam de 2 h em 1 h; agora conservador (cortes do componente), com conflito e motivo',
   4,[dict(id='A',nome='A',rend=1,jan=1,ativos=['T1','I1'],custo_h=1),dict(id='B',nome='B',rend=1,jan=2,ativos=['T1','I2'],custo_h=1),dict(id='C',nome='C',rend=1,jan=2,ativos=['T2','I2'],custo_h=1),dict(id='D',nome='D',rend=1,jan=1,ativos=['T2','I3'],custo_h=1)],None,
   dict(q=['1/2','1/2','1/2','1/2'],alocado='2',conflito=True,motivo='prazos diferentes em recursos compartilhados')),
 ('R3-1b anel_com_membro_sem_janela','rodada 3 do D-01 · S2 (agravado pela R2-2): anel A–B–C–D–E (A e D 1 h, B e C 2 h, E sem janela, 6 ha/h), 10 ha: antes 10 ha sem conflito com 1 h fictícia; agora conservador e com conflito',
   10,[dict(id='A',nome='A',rend=1,jan=1,ativos=['e0','e1'],custo_h=1),dict(id='B',nome='B',rend=1,jan=2,ativos=['e1','e2'],custo_h=1),dict(id='C',nome='C',rend=1,jan=2,ativos=['e2','e3'],custo_h=1),dict(id='D',nome='D',rend=1,jan=1,ativos=['e3','e4'],custo_h=1),dict(id='E',nome='E',rend=6,ativos=['e4','e0'],custo_h=1)],None,
   dict(q=['1/2','1/2','1/2','1/2','8'],conflito=True,motivo='prazos diferentes em recursos compartilhados')),
 ('R3-2c conflito_de_fato_e_de_estimativa','rodada 3 do D-01 · A e B na mesma máquina t1 (fato) e C, D só pelos Operadores (2 na fazenda, estimativa), 10 h cada, 50 ha: os dois motivos, o de fato primeiro',
   50,[dict(id='A',nome='A',rend=1,jan=10,ativos=['t1'],rec={'op':1},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['t1'],rec={'op':1},custo_h=1),dict(id='C',nome='C',rend=1,jan=10,rec={'op':1},custo_h=1),dict(id='D',nome='D',rend=1,jan=10,rec={'op':1},custo_h=1)],{'op':{'un':2,'nome':'Operadores'}},
   dict(conflito=True,motivo=['A e B: em sequência precisam de 25 h para 25 ha; a janela tem 10 h','A, B, C e D: consideradas em sequência nesta estimativa, precisam de 50 h'])),
 ('R3-4a par_que_passa_do_grupo_e_fato','rodada 3 do D-01 · A precisa de 2 tratores e B de 1, a fazenda tem 2: nunca trabalham juntas (fato, não estimativa)',
   30,[dict(id='A',nome='A',rend=1,jan=10,rec={'tr':2},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,rec={'tr':1},custo_h=1)],{'tr':{'un':2,'nome':'Tratores'}},
   dict(conflito=True,motivo=['Tratores: ao mesmo tempo precisariam de 3, a fazenda tem 2; trabalham uma de cada vez','A e B: em sequência precisam de 30 h'])),
 ('R2b grupo_de_recursos_nao_relaxa_janela_2','PRE-REV R2 · o mesmo com 2 plantadeiras: a mesma divisão (menos recurso nunca dá plano mais otimista); C ao mesmo tempo: 30 h',
   200,[dict(id='A',nome='A',rend=5,seq=True,jan=10,rec={'plant':1},custo_h=100),dict(id='B',nome='B',rend=5,seq=True,jan=10,custo_h=100),dict(id='C',nome='C',rend=5,rec={'plant':1},custo_h=100)],
   {'plant':{'un':2,'nome':'Plantadeiras'}},dict(q=['25','25','150'],saldo='0',decorrido='30',conflito=True,deficit='50/3')),
]
RA='rendCalc(6,8,75)'; RB='rendCalc(12,8,75)'
def js_val(x):
    if x=='RA': return RA
    if x=='RB': return RB
    if isinstance(x,str) and re.fullmatch(r'\d+/\d+',x): a,b=x.split('/'); return f'({a}/{b})'
    return json.dumps(x)
def js_cfg(c): return '{'+','.join(f'{json.dumps(k)}:{js_val(v)}' for k,v in c.items())+'}'
def py_val(x):
    if x=='RA': return D2.rend_calc(F(6),F(8),F(75))
    if x=='RB': return D2.rend_calc(F(12),F(8),F(75))
    if isinstance(x,bool) or x is None or x=='' : return x
    if isinstance(x,(int,float)) : return F(str(x))
    if isinstance(x,str) and re.fullmatch(r'-?\d+(/\d+)?(\.\d+)?',x): return F(x)
    return x
def py_cfg(c): return {k:(py_val(v) if k in ('rend','part','jan','custo_h','diesel','troca','pess') else v) for k,v in c.items()}
SEL="r=>({alocado:r.alocado,saldo:r.saldo,pendente:r.pendente,causa:r.causa,hconj:r.hconj,decorrido:r.decorrido,troca:r.troca,custo:r.custo,custoOk:r.custoOk,custoHa:r.custoHa,diesel:r.diesel,hh:r.hh,conflito:r.conflito,deficit:r.deficit,nec:r.nec,falta:r.falta,motivos:r.motivos,q:r.itens.map(x=>x.q),nq:r.itens.map(x=>x.nq),fq:r.itens.map(x=>x.fq),Q:r.Q})"
js=['function nfa(n){ return String(n); }',BLOCO,'const SEL='+SEL+';','const OUT={};']
for cid,_,Q,cfgs,pools,_e in CASOS:
    js.append(f"OUT[{json.dumps(cid)}]=SEL(repartir({json.dumps(Q)},[{','.join(js_cfg(c) for c in cfgs)}],{json.dumps(pools)}));")
# especiais: 01 rendimentos, 02 recíproco, 09 insumos, 11 gargalo em série, 12 sem arredondar
js.append("OUT['01']=[rendCalc(6,8,75),rendCalc(12,8,75)];")
js.append("OUT['02']=[repartir(1,[{rend:rendCalc(6,8,75)}]).hconj,repartir(1,[{rend:rendCalc(12,8,75)}]).hconj];")
js.append("(()=>{ const r=repartir(108,[{rend:rendCalc(6,8,75)},{rend:rendCalc(12,8,75)}]); OUT['09']=[108*2,r.itens.reduce((a,x)=>a+x.q*2,0)+r.saldo*2]; })();")
js.append("OUT['11']=(()=>{ const t=[repartir(48,[{rend:6},{rend:4}]).decorrido,repartir(48,[{rend:6}]).decorrido,repartir(48,[{rend:8}]).decorrido]; const T=Math.max.apply(null,t); return [48/T,T,t]; })();")
js.append("OUT['R3']=(()=>{ const r=repartir(2882.53,[48.7,17.6,21.9,5.4,6.4].map((p,i)=>({nome:'P'+i,rend:5,part:p,seq:true})).concat([{nome:'L',rend:5,seq:true,troca:2}])); return [r.itens[5].q,r.motivos.filter(m=>/não cobrem/.test(m)).length,r.decorrido]; })();")
js.append("OUT['P4']=['ABC','CAB','BCA'].map(o=>{ const d={A:{id:'A',nome:'A',rend:5,seq:true,ativos:['a01'],jan:3,troca:1,custo_h:1},B:{id:'B',nome:'B',rend:5,seq:true,jan:3,troca:1,custo_h:1},C:{id:'C',nome:'C',rend:5,ativos:['a01'],troca:1,custo_h:1}}; const r=repartir(11.25,o.split('').map(k=>d[k])); const q={}; r.itens.forEach(x=>{ q[x.id]=x.q; }); return [q.A,q.B,q.C,r.conflito,r.deficit,r.decorrido]; });")
js.append("OUT['Q4m']=repartir(100,[{id:'E',nome:'E',rend:1,part:50,jan:100,rec:{oper:10},custo_h:1},{id:'F',nome:'F',rend:1,part:50,jan:100,rec:{oper:1},custo_h:1}],{oper:{un:8,nome:'Operadores e equipe'}}).motivos;")
js.append("OUT['Q5']=(()=>{ const cs=[]; for(let i=0;i<20;i++) cs.push({id:'K'+i,nome:'K'+i,rend:2+i%3,jan:30,rec:{trator:1,plant:1,oper:2},custo_h:1}); const t0=Date.now(); const r=repartir(800,cs,{trator:{un:4},plant:{un:1},oper:{un:8}}); return [Date.now()-t0,r.alocado+r.saldo]; })();")
js.append("OUT['V6']=(()=>{ const cs=Array.from({length:24},(_,i)=>({id:'K'+i,nome:'K'+i,rend:1,jan:100,ativos:['a'+Math.floor(i/2)],rec:{oper:1},custo_h:1})); const t0=Date.now(); const r=repartir(2400,cs,{oper:{un:12}}); return [Date.now()-t0,r.alocado,r.motivos.some(m=>/ao mesmo tempo precisariam/.test(m))]; })();")
js.append("OUT['W3m']=repartir(2000,Array.from({length:28},(_,i)=>({id:'K'+i,nome:'K'+i,rend:1,jan:100,ativos:['a'+i,'a'+(i+1)],rec:{op:1},custo_h:1})),{op:{un:14,nome:'Operadores'}}).motivos;")
js.append("OUT['W1t']=(()=>{ const cs=[]; for(let t=0;t<4;t++) for(let p=0;p<5;p++) cs.push({id:'T'+t+'P'+p,nome:'T'+t+'+P'+p,rend:2,jan:(t===0&&p===0)?50:'',ativos:['t'+t,'p'+p],custo_h:1}); const t0=Date.now(); const r=repartir(4000,cs); return [Date.now()-t0,r.alocado,r.conflito]; })();")
js.append("OUT['W4']=(()=>{ const cs=[]; for(let a=0;a<30;a++){ const at=[]; for(let b=0;b<30;b++) if(Math.floor(a/3)!==Math.floor(b/3)) at.push('e'+Math.min(a,b)+'_'+Math.max(a,b)); cs.push({id:'K'+a,nome:'K'+a,rend:1,jan:100,ativos:at,custo_h:1}); } const t0=Date.now(); const r=repartir(3000,cs); return [Date.now()-t0,r.alocado+r.saldo,r.motivos.some(m=>/combinações demais/.test(m))]; })();")
js.append("OUT['D01f']=(()=>{ const r=repartir(15,[{id:'A',nome:'A',rend:1,jan:10,seq:true,ativos:['a01','t1'],rec:{oper:2},custo_h:1},{id:'B',nome:'B',rend:1,jan:10,seq:true,ativos:['t2'],rec:{plant:1,oper:4},custo_h:1},{id:'C',nome:'C',rend:1,jan:10,ativos:['a01','t3'],rec:{plant:1,oper:5},custo_h:1},{id:'D',nome:'D',rend:1,ativos:['t1','t2','t3'],custo_h:1}],{plant:{un:1,nome:'Plantadeiras'},oper:{un:8,nome:'Operadores'}}); return [r.itens.slice(0,3).reduce((a,x)=>a+x.h,0),r.conflito]; })();")
js.append("OUT['M1']=repartir(100,[{nome:'A',rend:3.6,seq:true,jan:0,custo_h:1},{nome:'B',rend:7.2,seq:true,jan:10,custo_h:1}]).motivos;")
js.append("OUT['12']=[repartir(1,[{rend:rendCalc(1.1,3.7,63)}]).hconj, 1/(Math.round(rendCalc(1.1,3.7,63)*100)/100)];")
js.append("OUT['R2-1']=(()=>{ const cs=[]; for(let a=0;a<22;a++){ const at=[]; for(let b=0;b<22;b++) if(a!==b&&Math.floor(a/2)!==Math.floor(b/2)) at.push('e'+Math.min(a,b)+'_'+Math.max(a,b)); cs.push({id:'K'+a,nome:'K'+a,rend:1,jan:10+(a%2)*11+Math.floor(a/2),ativos:at,custo_h:1}); } cs.push({id:'A',nome:'A',rend:1,jan:10,ativos:['ab'],custo_h:1},{id:'B',nome:'B',rend:1,jan:10,ativos:['ab','bc'],custo_h:1},{id:'C',nome:'C',rend:1,jan:10,ativos:['bc'],custo_h:1}); const t0=Date.now(); const r=repartir(3000,cs); return [r.itens.slice(22).map(x=>x.q),r.motivos.some(m=>/combinações demais/.test(m)),Date.now()-t0]; })();")
js.append("OUT['R2-4']=(()=>{ const P=[2,3,2,1,2,1,3,2,2,1,1,2,4]; const pa=[]; P.forEach((n,k)=>{ for(let j=0;j<n;j++) pa.push(k); }); const cs=pa.map((p,a)=>{ const at=[]; pa.forEach((q,b)=>{ if(b!==a&&q!==p) at.push('e'+Math.min(a,b)+'_'+Math.max(a,b)); }); return {id:'K'+a,nome:'K'+a,rend:1+(a%5),jan:2+((a*7)%19),part:(a%3===0)?2:'',troca:(a%4)*0.5,ativos:at,custo_h:1}; }); const t0=Date.now(); const r=repartir(400,cs); const r2=repartir(30,[{id:'A',nome:'A',rend:1,jan:10,ativos:['x'],custo_h:1},{id:'B',nome:'B',rend:1,jan:10,troca:3,ativos:['x','y'],custo_h:1},{id:'C',nome:'C',rend:1,jan:10,troca:1,ativos:['y'],custo_h:1}]); return [r.motivos,Date.now()-t0,r2.motivos.filter(m=>/troca de/.test(m)).length]; })();")
js.append("OUT['R3x']=[[20,[{id:'A',nome:'A',rend:1,jan:6,seq:true,rec:{tr:1},custo_h:1},{id:'B',nome:'B',rend:1,jan:6,seq:true,rec:{tr:1},custo_h:1},{id:'Z',nome:'Z',rend:1,seq:true,rec:{tr:1},custo_h:1},{id:'C',nome:'C',rend:1,jan:3,rec:{tr:2},custo_h:1}],{tr:{un:2,nome:'Tratores'}}],[50,[{id:'A',nome:'A',rend:1,jan:10,ativos:['t1'],rec:{op:1},custo_h:1},{id:'B',nome:'B',rend:1,jan:10,ativos:['t1'],rec:{op:1},custo_h:1},{id:'C',nome:'C',rend:1,jan:10,rec:{op:1},custo_h:1},{id:'D',nome:'D',rend:1,jan:10,rec:{op:1},custo_h:1}],{op:{un:2,nome:'Operadores'}}],[30,[{id:'A',nome:'A',rend:1,jan:10,rec:{tr:2},custo_h:1},{id:'B',nome:'B',rend:1,jan:10,rec:{tr:1},custo_h:1}],{tr:{un:2,nome:'Tratores'}}]].map(([Q,cs,pl])=>{ const r=repartir(Q,cs,pl); return [r.conflito,r.conflitoEst,r.itens.map(x=>x.seqEst)]; }).concat([[' ','0x10','1_000','1,5','.5','5.','1e2','Infinity','',null].map(v=>{ const n=rpNum(v); return n===null?'nulo':(isNaN(n)?'invalido':n); })]);")
js.append("OUT['R2-5a']=(()=>{ const r=repartir(8,[{id:'F',nome:'F',rend:1,part:60,custo_h:1},{id:'B',nome:'B',rend:1,part:10,jan:4,ativos:['m'],troca:2,custo_h:1},{id:'A',nome:'A',rend:2,jan:4,ativos:['m'],custo_h:1}]); return [r.alocado,r.motivos.filter(m=>/troca de/.test(m))]; })();")
js.append("OUT['R2-5d']=[[20,[{id:'A',nome:'A',rend:1,custo_h:1,jan:10,part:50,rec:{trator:1}},{id:'B',nome:'B',rend:1,custo_h:1,jan:10,part:25,rec:{trator:1}},{id:'C',nome:'C',rend:1,custo_h:1,jan:10,part:25,rec:{trator:1}}],{trator:{un:2,nome:'Tratores'}}],[10,[{id:'A',nome:'A',rend:1,custo_h:1,jan:10,part:50,seq:true},{id:'B',nome:'B',rend:1,custo_h:1,jan:10,seq:true,troca:10}],null],[20,[{id:'A',nome:'A',rend:1,jan:10,ativos:['a01'],custo_h:1},{id:'B',nome:'B',rend:1,jan:10,ativos:['a01'],custo_h:1}],null]].map(([Q,cs,pl])=>{ const r=repartir(Q,cs,pl); return [r.conflito,r.conflitoEst,r.itens.map(x=>[x.emSeq,x.seqEst])]; });")
js.append('print(JSON.stringify(OUT));')
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(PRELUDIO+'\n'+'\n'.join(js)); jsf=f.name
pr=subprocess.run(MOTOR+[jsf],capture_output=True,text=True,timeout=30); os.unlink(jsf)
if pr.returncode!=0 or not pr.stdout.strip(): print('motor JS (jsc/node) falhou:',pr.stderr[:800]); print('RESULTADO: 0/1 · jsc não rodou'); sys.exit(1)
OUT=json.loads(pr.stdout.strip().splitlines()[-1])
OK=0; N=0
def near(a,b):
    if a is None or b is None: return a is b
    return abs(float(a)-float(b))<=1e-9*max(1.0,abs(float(b)))
def exp_val(v): return F(v) if isinstance(v,str) and re.fullmatch(r'-?\d+(/\d+)?',v) else v
def pega(d,k):   # campo simples ou aninhado ('nec.hconj')
    for parte in k.split('.'): d=d[parte]
    return d
def fecha(r,qs,nqs,fqs,eq):   # necessário = atendido + saldo (ha e horas-conjunto); saldo = Σ saldo por configuração + sem horas calculáveis
    n,f=r['nec'],r['falta']; hc=r['hconj'] or 0
    ok=eq(n['area'],r['Q']) and eq(f['area'],r['saldo']) and eq(sum(nqs)+f['semHoras'],r['Q']) and eq(sum(fqs)+f['semHoras'],r['saldo'])
    ok&= all(a>=b-1e-9 for a,b in zip(nqs,qs))
    if n['hconj'] is not None: ok&= f['hconj'] is not None and eq(n['hconj'],hc+f['hconj']) and n['decorrido']>=(r['decorrido'] or 0)-1e-9
    return bool(ok)
def chk(cid,desc,exp_s,js_s,py_s,ok):
    global OK,N; N+=1; OK+=1 if ok else 0
    print(f"{'OK   ' if ok else 'FALHA'} {cid} · {desc}\n        esperado={exp_s}\n        JS={js_s}\n        Py={py_s}",flush=True)
for cid,desc,Q,cfgs,pools,exp in CASOS:
    j=OUT[cid]; p=D2.repartir(py_val(Q) if not isinstance(Q,str) else Q,[py_cfg(c) for c in cfgs],pools)
    p_q=[x['q'] for x in p['itens']]; ok=True; ej={}; ep={}
    for k,v in exp.items():
        if k in ('q','nq'):
            pv=[x[k] for x in p['itens']]; e=[F(x) for x in v]; ej[k]=j[k]; ep[k]=[str(x) for x in pv]
            ok&= all(near(a,b) for a,b in zip(j[k],e)) and len(j[k])==len(e) and all(F(a)==b for a,b in zip(pv,e))
        elif k=='motivo':
            ej[k]=j['motivos']; ep[k]=p['motivos']
            for v_ in ([v] if isinstance(v,str) else v): ok&= any(v_ in m_ for m_ in j['motivos']) and any(v_ in m_ for m_ in p['motivos'])
        elif k=='conserva':
            sj=sum(j['q'])+j['saldo']; sp=sum(p_q)+p['saldo']; ej[k]=f'Σq+saldo={sj}'; ep[k]=f'Σq+saldo={sp}'; ok&= near(sj,j['Q']) and F(sp)==F(Q)
        else:
            e=exp_val(v); jv,pv=pega(j,k),pega(p,k); ej[k]=jv; ep[k]=str(pv) if pv is not None and not isinstance(pv,bool) else pv
            if isinstance(e,F): ok&= near(jv,e) and pv is not None and F(pv)==e
            else: ok&= (jv==e) and (pv==e)
    # conservação em todo caso: Σ q + sem conjunto = Q (JS e Python)
    cj=near(sum(j['q'])+j['saldo'],j['Q']); cp=F(sum(p_q,F(0))+p['saldo'])==F(p['Q'])
    # necessário = atendido + saldo, em ha e em horas-conjunto (JS com tolerância, Python exato)
    nj=fecha(j,j['q'],j['nq'],j['fq'],near); npy=fecha(p,p_q,[x['nq'] for x in p['itens']],[x['fq'] for x in p['itens']],lambda a,b: F(a)==F(b))
    cj=cj and nj; cp=cp and npy
    ok&= cj and cp
    chk(cid,desc,json.dumps(exp,ensure_ascii=False),json.dumps(ej,ensure_ascii=False)+f' · conserva={cj}',json.dumps(ep,ensure_ascii=False,default=str)+f' · conserva={cp}',ok)
# especiais
ra,rb=D2.rend_calc(F(6),F(8),F(75)),D2.rend_calc(F(12),F(8),F(75))
chk('01 capacidades_ha_h','A 6 m × 8 km/h × 75 % e B 12 m × 8 km/h × 75 %','(18/5, 36/5)',OUT['01'],(str(ra),str(rb)),near(OUT['01'][0],F(18,5)) and near(OUT['01'][1],F(36,5)) and (ra,rb)==(F(18,5),F(36,5)))
pa=D2.repartir(F(1),[dict(rend=ra)])['hconj']; pb=D2.repartir(F(1),[dict(rend=rb)])['hconj']
chk('02 reciproco_h_ha','horas por hectare = 1 ÷ rendimento','(5/18, 5/36)',OUT['02'],(str(pa),str(pb)),near(OUT['02'][0],F(5,18)) and near(OUT['02'][1],F(5,36)) and (pa,pb)==(F(5,18),F(5,36)))
p9=D2.repartir(F(108),[dict(rend=ra),dict(rend=rb)]); i9=sum((x['q']*2 for x in p9['itens']),F(0))+p9['saldo']*2
chk('09 insumos_conservados','dose 2 un/ha em 108 ha: 216 antes e depois da divisão (dose × área não muda com os conjuntos)','(216, 216)',OUT['09'],(216,str(i9)),near(OUT['09'][0],216) and near(OUT['09'][1],216) and i9==216)
t11=[D2.repartir(F(48),[dict(rend=F(6)),dict(rend=F(4))])['decorrido'],D2.repartir(F(48),[dict(rend=F(6))])['decorrido'],D2.repartir(F(48),[dict(rend=F(8))])['decorrido']]; T11=max(t11)
chk('11 gargalo_serie_limite_inferior','etapas em série: 6+4 ha/h em paralelo, 6 e 8 ha/h; 48 ha → gargalo 6 ha/h, limite inferior 8 h (paralelo soma, série não)','(6, 8)',
    OUT['11'],(str(F(48)/T11),str(T11),[str(x) for x in t11]),near(OUT['11'][0],6) and near(OUT['11'][1],8) and F(48)/T11==6 and T11==8)
p12=D2.repartir(F(1),[dict(rend=D2.rend_calc(F('1.1'),F('3.7'),F(63)))])['hconj']
chk('12 sem_arredondamento_intermediario','1,1 m × 3,7 km/h × 63 %: h/ha = 100000/25641 (≈ 3,9000039); arredondar o rendimento para 0,26 daria 3,846','100000/25641',
    OUT['12'],str(p12),near(OUT['12'][0],F(100000,25641)) and p12==F(100000,25641) and abs(OUT['12'][1]-OUT['12'][0])>0.05)
r3c=[dict(nome=f'P{i}',rend=5,part=p,seq=True) for i,p in enumerate([48.7,17.6,21.9,5.4,6.4])]+[dict(nome='L',rend=5,seq=True,troca=2)]
p3f=D2.repartir(2882.53,r3c); p3=D2.repartir(F('2882.53'),[py_cfg(c) for c in r3c])
chk('R3 resto_relativo_area_grande','PRE-REV R3 · 2.882,53 ha com partes 48,7 + 17,6 + 21,9 + 5,4 + 6,4 = 100 % e uma configuração sem % em sequência (troca 2 h): ela não recebe área nem soma troca, em ponto flutuante (JS e Python) e exato',
    '[0, 0 avisos "não cobrem", decorrido 2882,53/5]',OUT['R3'],(p3f['itens'][5]['q'],str(p3['itens'][5]['q']),str(p3['decorrido'])),
    OUT['R3'][0]==0 and OUT['R3'][1]==0 and near(OUT['R3'][2],F('2882.53')/5) and p3f['itens'][5]['q']==0 and p3['itens'][5]['q']==0 and p3['decorrido']==F('2882.53')/5
    and not any('não cobrem' in m for m in p3f['motivos']+p3['motivos']))
chk('Q4b sem_sequencia_falsa','rodada 4 · E não trabalha (equipe maior que o quadro): o grupo não diz "trabalham em sequência" por causa dela','sem "trabalham em sequência"',OUT['Q4m'],'',
    not any('trabalham em sequência' in m for m in OUT['Q4m']))
import time as _t
_t0=_t.time(); _p5=D2.repartir(800,[dict(id=f'K{i}',nome=f'K{i}',rend=2+i%3,jan=30,rec={'trator':1,'plant':1,'oper':2},custo_h=1) for i in range(20)],{'trator':{'un':4},'plant':{'un':1},'oper':{'un':8}}); _dt=_t.time()-_t0
chk('Q5 vinte_configuracoes_rapido','rodada 4 · 20 configurações com 3 grupos de recursos: a busca do uso simultâneo com poda responde em menos de 1 s (JS e Python) e conserva a área',
    '< 1000 ms',f"JS {OUT['Q5'][0]} ms · Σ = {OUT['Q5'][1]}",f'Py {round(_dt*1000)} ms',OUT['Q5'][0]<1000 and _dt<1 and near(OUT['Q5'][1],800) and abs(float(_p5['alocado']+_p5['saldo'])-800)<1e-6)
_t0=_t.time(); _p6=D2.repartir(2400,[dict(id=f'K{i}',nome=f'K{i}',rend=1,jan=100,ativos=[f'a{i//2}'],rec={'oper':1},custo_h=1) for i in range(24)],{'oper':{'un':12}}); _dt6=_t.time()-_t0
chk('V6 pares_por_componente','rodada 5 · 24 configurações em pares no mesmo ativo, 12 operadores: o pico real é 12 (cabe), sem serializar todas; cada par divide os 100 h: 1.200 ha em menos de 1 s (JS e Python)',
    '1200 ha, sem "ao mesmo tempo precisariam", < 1 s',f"JS {OUT['V6'][0]} ms · {OUT['V6'][1]} ha · sequência={OUT['V6'][2]}",f"Py {round(_dt6*1000)} ms · {float(_p6['alocado'])} ha",
    OUT['V6'][0]<1000 and near(OUT['V6'][1],1200) and not OUT['V6'][2] and _dt6<1 and abs(float(_p6['alocado'])-1200)<1e-6)
chk('W3c cadeia_sem_pico_inventado','rodada 6 · cadeia de 28 com 14 operadores: nenhum motivo "ao mesmo tempo precisariam" (o pico real cabe)','sem "precisariam"',OUT['W3m'],
    D2.repartir(2000,[dict(id=f'K{i}',nome=f'K{i}',rend=1,jan=100,ativos=[f'a{i}',f'a{i+1}'],rec={'op':1},custo_h=1) for i in range(28)],{'op':{'un':14,'nome':'Operadores'}})['motivos'],
    not any('precisariam' in m for m in OUT['W3m']) and not any('precisariam' in m for m in D2.repartir(2000,[dict(id=f'K{i}',nome=f'K{i}',rend=1,jan=100,ativos=[f'a{i}',f'a{i+1}'],rec={'op':1},custo_h=1) for i in range(28)],{'op':{'un':14,'nome':'Operadores'}})['motivos']))
_t0=_t.time(); _w1=D2.repartir(4000,[dict(id=f'T{a}P{b}',nome=f'T{a}+P{b}',rend=2,jan=(50 if (a,b)==(0,0) else ''),ativos=[f't{a}',f'p{b}'],custo_h=1) for a in range(4) for b in range(5)]); _dw1=_t.time()-_t0
chk('W1e quatro_tratores_cinco_implementos','rodada 6 · 4 tratores × 5 implementos (20 configurações, 2 ha/h), só T0+P0 com janela de 50 h, 4.000 ha: atende tudo, sem conflito, em menos de 1 s (JS e Python)',
    '4000 ha, sem conflito, < 1 s',f"JS {OUT['W1t'][0]} ms · {OUT['W1t'][1]} ha · conflito={OUT['W1t'][2]}",f"Py {round(_dw1*1000)} ms · {float(_w1['alocado'])} ha · conflito={_w1['conflito']}",
    OUT['W1t'][0]<1000 and near(OUT['W1t'][1],4000) and not OUT['W1t'][2] and _dw1<1 and abs(float(_w1['alocado'])-4000)<1e-6 and not _w1['conflito'])
_cs4=[]
for _a in range(30): _cs4.append(dict(id=f'K{_a}',nome=f'K{_a}',rend=1,jan=100,ativos=[f'e{min(_a,_b)}_{max(_a,_b)}' for _b in range(30) if _a//3!=_b//3],custo_h=1))
_t0=_t.time(); _p4=D2.repartir(3000,_cs4); _d4=_t.time()-_t0
chk('W4 trios_rapido','rodada 6 · 30 configurações em trios (juntas dentro do trio, nunca com outro trio: 3^10 cliques): passa do teto de cliques, o componente divide a janela (conservador), com o motivo, em menos de 1 s (JS e Python), conservando a área',
    '< 1000 ms, motivo "combinações demais"',f"JS {OUT['W4'][0]} ms · Σ = {OUT['W4'][1]} · motivo={OUT['W4'][2]}",f"Py {round(_d4*1000)} ms · motivo={any('combinações demais' in m for m in _p4['motivos'])}",
    OUT['W4'][0]<1000 and near(OUT['W4'][1],3000) and OUT['W4'][2] and _d4<1 and abs(float(_p4['alocado']+_p4['saldo'])-3000)<1e-6 and any('combinações demais' in m for m in _p4['motivos']))
_v1d=[dict(id='A',nome='A',rend=1,jan=10,seq=True,ativos=['a01','t1'],rec={'oper':2},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,seq=True,ativos=['t2'],rec={'plant':1,'oper':4},custo_h=1),
      dict(id='C',nome='C',rend=1,jan=10,ativos=['a01','t3'],rec={'plant':1,'oper':5},custo_h=1),dict(id='D',nome='D',rend=1,ativos=['t1','t2','t3'],custo_h=1)]
_rv=D2.repartir(F(15),[py_cfg(c) for c in _v1d],{'plant':{'un':1,'nome':'Plantadeiras'},'oper':{'un':8,'nome':'Operadores'}}); _hv=sum((x['h'] for x in _rv['itens'][:3]),F(0))
chk('D01f triangulo_mais_vizinho_sem_janela','D-01 · o S2 refutado na rodada 5 (triângulo A–B–C de 10 h + D sem janela ligado às três): A+B+C cabem nos 10 h e há conflito (Python com Fraction; JS no R1/R2)',
    'h(A+B+C) ≤ 10, conflito',f"JS {OUT['D01f']}",f'Py h={_hv} conflito={_rv["conflito"]}',_hv<=10 and _rv['conflito'] and OUT['D01f'][0]<=10+1e-9 and OUT['D01f'][1])
_ps=open(os.path.join(HERE,'areas','processo_safra.py'),encoding='utf-8').read()
chk('Dc ajuda_sem_promessa','regra (c) · a ajuda de "Parte da área" não promete término no mesmo horário nem capacidade máxima',
    'sem "terminam juntas"','','',"as configurações sem % terminam juntas" not in _ps and 'não garante' in _ps)
# ---------- rodada 2 do D-01 (pré-revisão adversarial do autor sobre 04bf6f2) ----------
_ps2=open(os.path.join(HERE,'areas','processo_safra.py'),encoding='utf-8').read(); _sj=open(os.path.join(HERE,'safra.js'),encoding='utf-8').read(); _d2=open(os.path.join(HERE,'dados2.py'),encoding='utf-8').read()
_bl=lambda t,a,b: t[t.index(a):t.index(b)]
chk('R2-5e ajudas_e_motivos_sem_regra_antiga','rodada 2 do D-01 · ajudas da janela, da parte e da sequência e motivos do conservador sem "dividem a maior janela" nem "as mesmas horas produtivas"; a ajuda da janela fala em prazo',
    'ausentes; "Prazo" na ajuda','','',
    'dividem a maior janela' not in _ps2 and 'mesmas horas produtivas' not in _ps2 and 'Prazo, contado do início da ocorrência' in _ps2 and 'faz a estimativa considerar as configurações em sequência' in _ps2
    and 'dividem a maior janela' not in _bl(_sj,'// >>> REPARTIR','// <<< REPARTIR') and 'dividem a maior janela' not in _bl(_d2,'# >>> REPARTIR','def _ok('))
def _pares11():
    cs=[]
    for a in range(22):
        at=[f'e{min(a,b)}_{max(a,b)}' for b in range(22) if a!=b and a//2!=b//2]
        cs.append(dict(id=f'K{a}',nome=f'K{a}',rend=1,jan=10+(a%2)*11+a//2,ativos=at,custo_h=1))
    return cs+[dict(id='A',nome='A',rend=1,jan=10,ativos=['ab'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['ab','bc'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,ativos=['bc'],custo_h=1)]
_t0=_t.time(); _r21=D2.repartir(3000,_pares11()); _d21=_t.time()-_t0
chk('R2-1 teto_de_cortes_por_componente','rodada 2 do D-01 · 11 pares que passam de 8 192 cortes ficam no conservador (com motivo), mas o A–B–C independente continua com 5 ha cada (antes 3,33 ha cada, com conflito falso)',
    'A, B, C = 5 · motivo "combinações demais" · < 1 s',f"JS q={OUT['R2-1'][0]} motivo={OUT['R2-1'][1]} {OUT['R2-1'][2]} ms",f"Py q={[round(float(x['q']),4) for x in _r21['itens'][22:]]} {round(_d21*1000)} ms",
    all(near(v,5) for v in OUT['R2-1'][0]) and OUT['R2-1'][1] and OUT['R2-1'][2]<1000 and all(abs(float(x['q'])-5)<1e-9 for x in _r21['itens'][22:])
    and any('combinações demais' in m for m in _r21['motivos']) and _d21<10)
def _r24():
    P=[2,3,2,1,2,1,3,2,2,1,1,2,4]; pa=[k for k,n in enumerate(P) for _ in range(n)]
    return [dict(id=f'K{a}',nome=f'K{a}',rend=1+(a%5),jan=2+((a*7)%19),part=2 if a%3==0 else '',troca=(a%4)*0.5,ativos=[f'e{min(a,b)}_{max(a,b)}' for b,q in enumerate(pa) if b!=a and q!=p],custo_h=1) for a,p in enumerate(pa)]
_t0=_t.time(); _p24=D2.repartir(400,_r24()); _d24=_t.time()-_t0
_p24c=D2.repartir(30,[dict(id='A',nome='A',rend=1,jan=10,ativos=['x'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,troca=3,ativos=['x','y'],custo_h=1),dict(id='C',nome='C',rend=1,jan=10,troca=1,ativos=['y'],custo_h=1)])
chk('R2-4 motivos_por_grupo_e_janela','rodada 2 do D-01 · 26 configurações em 13 partes (máquina por par), partes fixas e trocas: no máximo 3 motivos por configuração (04bf6f2: 176; ee4f954: 1.672), JS = Python, < 1 s; A–B/B–C na mesma janela: um motivo de troca',
    '≤ 78 motivos · JS = Py · < 1 s · 1 motivo de troca',f"JS {len(OUT['R2-4'][0])} motivos {OUT['R2-4'][1]} ms · troca {OUT['R2-4'][2]}",f"Py {len(_p24['motivos'])} motivos {round(_d24*1000)} ms · troca {sum('troca de' in m for m in _p24c['motivos'])}",
    len(OUT['R2-4'][0])<=78 and OUT['R2-4'][0]==_p24['motivos'] and OUT['R2-4'][1]<1000 and _d24<10 and OUT['R2-4'][2]==1 and sum('troca de' in m for m in _p24c['motivos'])==1)
_r3=[]
for Q_,cs_,pl_ in ((20,[dict(id='A',nome='A',rend=1,jan=6,seq=True,rec={'tr':1},custo_h=1),dict(id='B',nome='B',rend=1,jan=6,seq=True,rec={'tr':1},custo_h=1),dict(id='Z',nome='Z',rend=1,seq=True,rec={'tr':1},custo_h=1),dict(id='C',nome='C',rend=1,jan=3,rec={'tr':2},custo_h=1)],{'tr':{'un':2,'nome':'Tratores'}}),
                   (50,[dict(id='A',nome='A',rend=1,jan=10,ativos=['t1'],rec={'op':1},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['t1'],rec={'op':1},custo_h=1),dict(id='C',nome='C',rend=1,jan=10,rec={'op':1},custo_h=1),dict(id='D',nome='D',rend=1,jan=10,rec={'op':1},custo_h=1)],{'op':{'un':2,'nome':'Operadores'}}),
                   (30,[dict(id='A',nome='A',rend=1,jan=10,rec={'tr':2},custo_h=1),dict(id='B',nome='B',rend=1,jan=10,rec={'tr':1},custo_h=1)],{'tr':{'un':2,'nome':'Tratores'}})):
    r_=D2.repartir(F(Q_),[py_cfg(c) for c in cs_],pl_); _r3.append([r_['conflito'],r_['conflitoEst'],[x['seqEst'] for x in r_['itens']]])
_n3=['nulo' if n is None else ('invalido' if n!=n else n) for n in (D2._rp_num(v) for v in (' ','0x10','1_000','1,5','.5','5.','1e2','Infinity','',None))]
_x3=[[True,False,[False,False,False,False]],[True,False,[False,False,True,True]],[True,False,[False,False]]]
chk('R3-2 conflito_de_fato_nao_vira_estimativa','rodada 3 do D-01 · (a) A e B em sequência declarada (6 h) com C que precisa dos 2 tratores: conflito de fato, não "nesta estimativa"; (c) fato + estimativa no mesmo grupo: conflitoEst falso, só C e D como estimativa; par que passa do grupo é fato; e número em texto lido igual em JS e Python (espaço = vazio; 0x10, 1_000 e Infinity inválidos)',
    str(_x3)+' · '+str(_n3),OUT['R3x'],[_r3,_n3],OUT['R3x'][:3]==_x3 and _r3==_x3 and OUT['R3x'][3]==_n3 and _n3==['nulo','invalido','invalido',1.5,0.5,5.0,100.0,'invalido','nulo','nulo'])
_c25=[dict(id='F',nome='F',rend=1,part=60,custo_h=1),dict(id='B',nome='B',rend=1,part=10,jan=4,ativos=['m'],troca=2,custo_h=1),dict(id='A',nome='A',rend=2,jan=4,ativos=['m'],custo_h=1)]
_p25f=D2.repartir(8,_c25); _p25=D2.repartir(F(8),[py_cfg(c) for c in _c25])
chk('R2-5a empate_sem_motivo_de_troca','rodada 2 do D-01 · tudo cabe (empate de ponto flutuante em A: 1,2 h para 1,2 h): sem o motivo "para liberar horas" da troca, em JS, Python float e Python Fraction',
    '8 ha, nenhum motivo de troca',OUT['R2-5a'],[float(_p25f['alocado']),[m for m in _p25f['motivos'] if 'troca de' in m],str(_p25['alocado']),[m for m in _p25['motivos'] if 'troca de' in m]],
    near(OUT['R2-5a'][0],8) and not OUT['R2-5a'][1] and abs(_p25f['alocado']-8)<1e-9 and not any('troca de' in m for m in _p25f['motivos']+_p25['motivos']) and _p25['alocado']==8)
_e25=[]
for Q_,cs_,pl_ in ((20,[dict(id='A',nome='A',rend=1,custo_h=1,jan=10,part=50,rec={'trator':1}),dict(id='B',nome='B',rend=1,custo_h=1,jan=10,part=25,rec={'trator':1}),dict(id='C',nome='C',rend=1,custo_h=1,jan=10,part=25,rec={'trator':1})],{'trator':{'un':2,'nome':'Tratores'}}),
                   (10,[dict(id='A',nome='A',rend=1,custo_h=1,jan=10,part=50,seq=True),dict(id='B',nome='B',rend=1,custo_h=1,jan=10,seq=True,troca=10)],None),
                   (20,[dict(id='A',nome='A',rend=1,jan=10,ativos=['a01'],custo_h=1),dict(id='B',nome='B',rend=1,jan=10,ativos=['a01'],custo_h=1)],None)):
    r_=D2.repartir(F(Q_),[py_cfg(c) for c in cs_],pl_); _e25.append([r_['conflito'],r_['conflitoEst'],[[x['emSeq'],x['seqEst']] for x in r_['itens']]])
_x25=[[True,True,[[True,True]]*3],[True,False,[[False,False],[False,False]]],[True,False,[[True,False],[True,False]]]]   # o 3º: mesma máquina, 20 h em 10 h: conflito de fato
chk('R2-5d sequencia_de_estimativa_na_tela','rodada 2 do D-01 · regra (b) nos chips: 3 com 1 trator cada e 2 tratores → "em sequência nesta estimativa" e "não cabe na janela nesta estimativa"; sequência declarada e mesma máquina continuam como fato',
    str(_x25),OUT['R2-5d'],_e25,OUT['R2-5d']==_x25 and _e25==_x25)
p4=[]
for o in ('ABC','CAB','BCA'):
    d=dict(A=dict(id='A',nome='A',rend=F(5),seq=True,ativos=['a01'],jan=F(3),troca=F(1),custo_h=F(1)),B=dict(id='B',nome='B',rend=F(5),seq=True,jan=F(3),troca=F(1),custo_h=F(1)),C=dict(id='C',nome='C',rend=F(5),ativos=['a01'],troca=F(1),custo_h=F(1)))
    r=D2.repartir(F('11.25'),[d[k] for k in o]); q={x['id']:x['q'] for x in r['itens']}; p4.append([q['A'],q['B'],q['C'],r['conflito'],r['deficit'],r['decorrido']])
chk('P4 empate_de_troca_independe_da_ordem','rodada 3 · A e B em sequência (janela 3 h, troca 1 h), C no a01 de A sem janela (troca 1 h), nas ordens ABC, CAB e BCA: a mesma divisão (3,75 ha cada), sem conflito, decorrido 4,25 h',
    '3 × [15/4, 15/4, 15/4, False, 0, 17/4]',OUT['P4'],[[str(v) for v in x] for x in p4],
    all(near(a,F(15,4)) and near(b,F(15,4)) and near(c,F(15,4)) and cf_ is False and near(df,0) and near(dc,F(17,4)) for a,b,c,cf_,df,dc in OUT['P4'])
    and all(x==[F(15,4),F(15,4),F(15,4),False,0,F(17,4)] for x in p4))
pm1=D2.repartir(F(100),[dict(nome='A',rend=F('3.6'),seq=True,jan=F(0),custo_h=F(1)),dict(nome='B',rend=F('7.2'),seq=True,jan=F(10),custo_h=F(1))])['motivos']
chk('M1 motivo_sem_sequencia_falsa','rodada 2 · A (janela 0) e B (janela 10 h) em sequência declarada, pelo rendimento: B faz 72 ha na janela dela; o motivo é só "as janelas não comportam", sem "sequência declarada" nem "dividem a mesma janela"',
    "['as janelas não comportam toda a área']",OUT['M1'],pm1,OUT['M1']==pm1==['as janelas não comportam toda a área'])
# ---------- 400 entradas aleatórias (semente fixa): paridade JS × Python (float) e invariantes nos dois ----------
import random
rng=random.Random(20261003); RND=[]
for n in range(400):
    k=rng.randint(1,4); cfs=[]
    for j in range(k):
        c=dict(id=f'c{j}',nome=f'C{j}',rend=(rng.choice([2.925,3.6,6.8,7.2,18,21.6,round(rng.uniform(.5,25),3)]) if rng.random()<.85 else rng.choice(['',0,'3,6'])),
               custo_h=rng.choice([rng.randint(50,400),'']),diesel=rng.choice(['',rng.randint(4,30)]))
        if rng.random()<.3: c['part']=rng.choice([0,20,30,50,70])
        if rng.random()<.8: c['jan']=rng.choice([0,1,2,3,5,8,12,20])
        if rng.random()<.6: c['seq']=True
        if rng.random()<.4: c['troca']=rng.choice([0,.5,1,2])
        if rng.random()<.3: c['ativos']=[rng.choice(['a01','a02'])]
        if rng.random()<.5: c['rec']={'plant':1}
        c['pess']=rng.choice([0,1,2])
        cfs.append(c)
    RND.append((rng.choice([0,rng.randint(1,300),round(rng.uniform(1,300),2),round(rng.uniform(1,300),2)]),cfs,rng.choice([None,{'plant':{'un':1,'nome':'Plantadeiras'}},{'plant':{'un':2,'nome':'Plantadeiras'}}])))
SELR="r=>({Q:r.Q,alocado:r.alocado,saldo:r.saldo,pendente:r.pendente,causa:r.causa,hconj:r.hconj,decorrido:r.decorrido,custo:r.custo,custoOk:r.custoOk,diesel:r.diesel,hh:r.hh,conflito:r.conflito,deficit:r.deficit,nec:r.nec,falta:r.falta,motivos:r.motivos,it:r.itens.map(x=>({q:x.q,h:x.h,ht:x.ht,H:isFinite(x.H)?x.H:-1,g:x.grupo,s:x.emSeq,nq:x.nq,fq:x.fq}))})"
jr=['function nfa(n){ return String(n); }',BLOCO,'const SELR='+SELR+';','const R=[];']+[f"R.push(SELR(repartir({json.dumps(Q)},{json.dumps(c)},{json.dumps(pl)})));" for Q,c,pl in RND]+['print(JSON.stringify(R));']
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(PRELUDIO+'\n'+'\n'.join(jr)); jsf=f.name
pr=subprocess.run(MOTOR+[jsf],capture_output=True,text=True,timeout=60); os.unlink(jsf); JR=json.loads(pr.stdout.strip().splitlines()[-1])
def inv(r,Q,cfs,pl=None):   # invariantes de um resultado (JS ou Python no mesmo formato)
    e=[]; its=r['it']; sq=sum(x['q'] for x in its)
    # D-01 (5983640246): janela temporal da ocorrência; todo subgrupo que se exclui e tem janela finita cabe no maior prazo dele (cortes por
    # prazo: os de janela ≤ t cabem em t, para cada janela finita t do grupo). Um membro sem janela ou de prazo maior não amplia os demais.
    def corta(xs):
        fin=[x for x in xs if x['H']>=0]
        return any(sum(x['h'] for x in fin if x['H']<=t)>t+1e-9 for t in {x['H'] for x in fin} if sum(1 for x in fin if x['H']<=t)>1)
    ds=[x for x,c in zip(its,cfs) if c.get('seq') and x['nq']>1e-12]   # sequência declarada no plano (PRE-REV R2)
    if len(ds)>1 and corta(ds): e.append('sequência declarada passa do prazo de um subgrupo')
    from itertools import combinations as _comb   # rodada 5: todo conjunto que se exclui duas a duas (sequência, ativo, plantadeira de 1)
    um1=bool(pl) and (pl.get('plant') or {}).get('un')==1
    def _ex(a,b): return (a.get('seq') and b.get('seq')) or bool(set(a.get('ativos') or [])&set(b.get('ativos') or [])) or (um1 and (a.get('rec') or {}).get('plant') and (b.get('rec') or {}).get('plant'))
    tr=[(x,c) for x,c in zip(its,cfs) if x['nq']>1e-12]   # no plano; cada grupo maximal com os cortes por prazo (cobre todo subgrupo)
    for m in range(2,len(tr)+1):
        for S in _comb(tr,m):
            if not all(_ex(a[1],b[1]) for a,b in _comb(S,2)): continue
            if any(all(_ex(o[1],s[1]) for s in S) for o in tr if all(o is not s for s in S)): continue   # não maximal
            if corta([x for x,_ in S]): e.append('grupo exclusivo passa do prazo de um subgrupo')
    for z in sorted({a for c in cfs for a in (c.get('ativos') or [])}):   # cada ativo do cadastro
        da=[x for x,c in zip(its,cfs) if z in (c.get('ativos') or []) and x['nq']>1e-12]
        if len(da)>1 and corta(da): e.append('ativo passa do prazo de um subgrupo')
    if abs(sq+r['saldo']-Q)>1e-7*max(1,Q): e.append('Σq+saldo≠Q')
    if any(x['q']<-1e-12 for x in its) or r['saldo']<-1e-12: e.append('negativo')
    if any(x['H']>=0 and x['h']>x['H']+1e-9 for x in its): e.append('h>janela própria')
    # grupo de recursos com 1 unidade: se dois usuários poderiam trabalhar juntos, todos dividem a maior janela deles (rodada 3: restrição por
    # recurso físico; o fecho inteiro não é restrição, o decorrido o trata como uma sequência só)
    if pl and (pl.get('plant') or {}).get('un')==1:
        up=[(x,c) for x,c in zip(its,cfs) if (c.get('rec') or {}).get('plant') and x['nq']>1e-12]
        junto=lambda a,b: (a.get('seq') and b.get('seq')) or bool(set(a.get('ativos') or [])&set(b.get('ativos') or []))
        if any(not junto(a[1],b[1]) for i,a in enumerate(up) for b in up[i+1:]) and corta([x for x,_ in up]):
            e.append('grupo de recursos passa do prazo de um subgrupo')
    if r['pendente'] and (r['hconj'] is not None or not r['causa']): e.append('pendente sem causa ou com horas')
    if not r['pendente'] and r['causa']: e.append('causa sem pendência')
    if r['hconj'] is not None and abs(r['hconj']-sum(x['h'] for x in its))>1e-9*max(1,r['hconj']): e.append('horas-conjunto≠Σh')
    if not fecha(r,[x['q'] for x in its],[x['nq'] for x in its],[x['fq'] for x in its],lambda a,b: abs(a-b)<=1e-7*max(1,abs(b))): e.append('necessário≠atendido+saldo')
    return e
def pyr(Q,c,pl):
    p=D2.repartir(Q,c,pl); f=lambda v: float(v) if v is not None and not isinstance(v,bool) else v
    return dict(Q=f(p['Q']),alocado=f(p['alocado']),saldo=f(p['saldo']),pendente=p['pendente'],causa=p['causa'],hconj=f(p['hconj']),decorrido=f(p['decorrido']),custo=f(p['custo']),
                custoOk=p['custoOk'],diesel=f(p['diesel']),hh=f(p['hh']),conflito=p['conflito'],deficit=f(p['deficit']),motivos=p['motivos'],
                nec={k:f(v) for k,v in p['nec'].items()},falta={k:f(v) for k,v in p['falta'].items()},
                it=[dict(q=f(x['q']),h=f(x['h']),ht=f(x['ht']),H=(-1 if x['H']==float('inf') else f(x['H'])),g=x['grupo'],s=x['emSeq'],nq=f(x['nq']),fq=f(x['fq'])) for x in p['itens']])
def igual(a,b):
    for k in ('alocado','saldo','hconj','decorrido','custo','diesel','hh','deficit'):
        x,y=a[k],b[k]
        if (x is None)!=(y is None) or (x is not None and abs(x-y)>1e-7*max(1,abs(y))): return k
    for k in ('pendente','causa','conflito','custoOk','motivos'):
        if a[k]!=b[k]: return k
    for g in ('nec','falta'):
        for k in ('area','hconj','decorrido','semHoras'):
            x,y=a[g][k],b[g][k]
            if (x is None)!=(y is None) or (x is not None and abs(x-y)>1e-7*max(1,abs(y))): return g+'.'+k
    if any(abs(x['nq']-y['nq'])>1e-7*max(1,abs(y['nq'])) or abs(x['fq']-y['fq'])>1e-7*max(1,abs(y['fq'])) for x,y in zip(a['it'],b['it'])): return 'itens.nq/fq'
    if any(abs(x['q']-y['q'])>1e-7*max(1,abs(y['q'])) or x['s']!=y['s'] for x,y in zip(a['it'],b['it'])): return 'itens'
    return None
# configuração ociosa (janela 0, sem %, fora do plano porque há outra sem % com horas): o resultado das outras não muda (JS e Python)
OCI=[]
for n,(Q,c,pl) in enumerate(RND):
    if any('part' not in x and x.get('jan')!=0 for x in c):
        z=dict(id='z',nome='Z',rend=5,jan=0,seq=True,ativos=['a01','a02'],rec={'plant':1},custo_h=1); OCI.append((n,Q,c+[z],pl))   # liga tudo o que puder
jo=['function nfa(n){ return String(n); }',BLOCO,'const SELR='+SELR+';','const R=[];']+[f"R.push(SELR(repartir({json.dumps(Q)},{json.dumps(c)},{json.dumps(pl)})));" for _,Q,c,pl in OCI]+['print(JSON.stringify(R));']
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False) as f: f.write(PRELUDIO+'\n'+'\n'.join(jo)); jsf=f.name
pr=subprocess.run(MOTOR+[jsf],capture_output=True,text=True,timeout=60); os.unlink(jsf); JO=json.loads(pr.stdout.strip().splitlines()[-1])
def mesmo(a,b):
    for k in ('alocado','saldo','decorrido','deficit','hconj'):
        if (a[k] is None)!=(b[k] is None) or (a[k] is not None and abs(a[k]-b[k])>1e-7*max(1,abs(b[k]))): return k
    if a['conflito']!=b['conflito'] or a['pendente']!=b['pendente']: return 'conflito/pendente'
    if any(abs(x['q']-y['q'])>1e-7*max(1,abs(y['q'])) for x,y in zip(a['it'],b['it'])): return 'itens'
    return None
noci=0; exo=[]
for (n,Q,c,pl),j in zip(OCI,JO):
    d=mesmo(j,JR[n]) or mesmo(pyr(Q,c,pl),pyr(*RND[n]))
    if d is None: noci+=1
    elif len(exo)<2: exo.append((n,d))
npar=0; ninv=0; ex=[]; nseq=0; nconf=0; npend=0
for (Q,c,pl),j in zip(RND,JR):
    py=pyr(Q,c,pl); d=igual(j,py); ij=inv(j,float(Q),c,pl); ip=inv(py,float(Q),c,pl)
    if d is None: npar+=1
    elif len(ex)<3: ex.append(('paridade',d,Q,c,pl,j.get(d),py.get(d)))
    if not ij and not ip: ninv+=1
    elif len(ex)<3: ex.append(('invariante',ij,ip,Q,c,pl))
    nseq+=any(x['s'] for x in j['it']); nconf+=j['conflito']; npend+=j['pendente']
assert nseq>=100 and nconf>=20, (nseq,nconf)   # a amostra precisa exercitar sequência e conflito
chk('R1 paridade_js_python_400','400 entradas aleatórias (rendimento vazio/0/vírgula, partes, janelas 0–20 h, sequência, troca, mesmo ativo, grupo da fazenda): JS = Python',
    '400/400',f'{npar}/400 iguais',f'com sequência {nseq} · conflito {nconf} · pendentes {npend} · exemplos {ex[:2]}',npar==400)
chk('R2 invariantes_400','Σ q + sem conjunto = Q, sem negativos, h ≤ janela própria, sequência declarada, cada ativo e o grupo de 1 plantadeira ≤ a janela deles, pendente com causa e sem horas, horas-conjunto = Σ h, necessário = atendido + saldo (ha e horas-conjunto)',
    '400/400',f'{ninv}/400 sem violação',f'exemplos {ex[:2]}',ninv==400)
chk('R4 ociosa_nao_muda_400',f'rodada 2 · {len(OCI)} entradas aleatórias com uma configuração ociosa a mais (janela 0, sem %, fora do plano; na sequência, nos ativos a01 e a02 e na plantadeira): atendido, saldo, decorrido, déficit, conflito e divisão iguais',
    f'{len(OCI)}/{len(OCI)}',f'{noci}/{len(OCI)} iguais',f'exemplos {exo}',noci==len(OCI) and len(OCI)>=150)
print(f'RESULTADO: {OK}/{N} OK · JS = bloco REPARTIR de safra.js no jsc · Python = dados2.repartir com Fraction',flush=True)
sys.exit(0 if OK==N else 1)
