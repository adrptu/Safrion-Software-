# Oráculos propostos para a regressão da EX-38, avaliados sobre o que o navegador mostrou (render limpo de ff3903d).
# Cada um deve REPROVAR hoje (e passar depois da correção). Lê só as saídas em out/.
import json, re, os, sys
sys.dont_write_bytecode = True
O = '/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/ex38/out'
P = json.load(open(os.path.join(O, 'os_paineis.json')))
T = lambda f: open(os.path.join(O, f), encoding='utf-8').read()
num = lambda s: float(s.replace('.', '').replace(',', '.'))
res = []
def ok(id_, cond, msg, ev):
    res.append((id_, cond)); print(('PASSA ' if cond else 'REPROVA ') + id_ + ' · ' + msg + ' · ' + ev)
# R1 OS-0421: mesmo tanque, vazão, área por carga e produto por carga no painel da O.S., no app e no cadastro (a05 tanque 3000)
m = re.search(r'tanque útil ([\d.]+) L · (\d+) L/ha\): ([\d,]+) ha por carga.*?Fungicida A ([\d,]+) L por carga', P['OS-0421'])
a = re.search(r'Preparo por tanque: ([\d.]+) L de calda · (\d+) L/ha · cobre ([\d,]+) ha · ([\d,]+) L de Fungicida A', T('MB-02det_OS-0421_Marcos.txt'))
os_ = tuple(num(x) for x in m.groups()); app = tuple(num(x) for x in a.groups())
ok('R1', os_ == app and os_[0] == 3000, 'tanque/vazão/ha por carga/L por carga iguais (O.S. = app = cadastro a05)', f'O.S. {os_} · app {app}')
# R2 O.S. com "usado" > 0 só com item de requisição que tenha consumido igual
def sem_req(oid, prod):
    t = P[oid]; i = t.find(prod); seg = t[i:i + 400]
    return ('Reservado' not in seg.split('\n', 8)[-1] and 'lote' not in seg.split('\n')[6]) if i >= 0 else False
r2 = []
for oid, prod in [('OS-0421', 'Adjuvante espalhante'), ('OS-0420', 'MAP 11-52')]:
    t = P[oid]; i = t.find(prod); blk = t[i:i + 300].split('\n')
    usado = blk[4]; trilha = any(x.startswith('Reservado') for x in blk[5:8])
    r2.append((oid, prod, usado, trilha))
ok('R2', all(u in ('—',) or tr for _, _, u, tr in r2), 'insumo com "usado" tem requisição e movimento', str(r2))
# R3 OS-0420: o mesmo conjunto de produtos no painel, na O.S. completa e no almoxarifado
pan = set(p for p in ['Semente de soja 58 W', 'MAP 11-52', 'KCl 60', 'TS nematicida'] if p in P['OS-0420'][:P['OS-0420'].find('APONTAMENTOS')])
comp = set(p for p in ['Semente de soja 58 W', 'MAP 11-52', 'KCl 60', 'TS nematicida'] if p in T('CA-01x-os0420.txt'))
su = T('SU-07.txt'); al = set(p for p in ['Semente de soja 58 W', 'MAP 11-52', 'KCl 60', 'TS nematicida'] if re.search(r'OS-0420[^\n]*\n' + re.escape(p), su))
ok('R3', pan == comp == al, 'OS-0420 com a mesma instrução no painel, na O.S. completa e no SU-07', f'painel {sorted(pan)} · completa {sorted(comp)} · SU-07 {sorted(al)}')
# R4 app mostra quanto falta para terminar (dose × saldo − custódia = 0,5 × 160 − 65 = 15 L)
ok('R4', re.search(r'(falta|faltam|a entregar|Retirar)\D{0,20}15 L', T('MB-02det_OS-0421_Marcos.txt')) is not None, 'app da OS-0421 mostra os 15 L que faltam', 'MB-02det só diz "Com você 65 L"; CA-01det tem "A ENTREGAR 15 L": ' + str('15 L' in T('CA-01det.txt')))
# R5 entrega em embalagem fechada (galão 5 L, saco 25 kg)
fr = []
for oid, prod, n in [('OS-0504', 'Abamectina 18 EC', 5), ('OS-0508', 'Tebuconazol 200 EC', 5), ('OS-0506', 'Sulfato de potássio', 25), ('OS-0507', 'Nitrato de amônio', 25)]:
    q = num(re.search(r'Entregue ([\d.,]+) (?:L|kg)', P[oid][P[oid].find(prod):]).group(1)); fr.append((oid, prod, q, round(q / n, 3)))
ok('R5', all(abs(k - round(k)) < 1e-9 for *_, k in fr), 'entregue = número inteiro de embalagens', str(fr))
# R6 entregue ≤ necessidade arredondada à embalagem (OS-0417: 3.500 kg = 70 sc)
e = num(re.search(r'Entregue ([\d.]+) kg', P['OS-0417']).group(1)); nec = num(re.search(r'kg/ha\n([\d.]+) kg', P['OS-0417']).group(1))
ok('R6', e <= nec, 'OS-0417 entregue ≤ necessidade', f'entregue {e} kg × necessidade {nec} kg')
# R7 recurso único: OS-0504 cita o PJ-3030 e o Trator 02 e tem de entrar na checagem de conflito
ok('R7', 'RECURSOS ALOCADOS' in P['OS-0504'] and 'Nenhuma ordem de Lagoa Grande' not in open(os.path.join(O, 'carga_lagoa.txt')).read() + ' ',
   'OS-0504 com recurso alocado e checado', 'painel OS-0504 sem Recursos alocados; conjunto "' + re.search(r'CONJUNTO\n([^\n]*)', P['OS-0504']).group(1) + '"')
# R8 horas previstas cabem na janela alocada
h = num(re.search(r'HORAS PREVISTAS\n([\d,]+) h', P['OS-0424']).group(1)); jan = re.findall(r'(\d\d):(\d\d)–(\d\d):(\d\d)', re.search(r'Máquina · Trator 04\n(?:Trocar\n)?([^\n]*)', P['OS-0424']).group(1))
dj = sum((int(c) * 60 + int(d) - int(a_) * 60 - int(b)) / 60 for a_, b, c, d in jan)
ok('R8', h <= dj or 'não cabe' in P['OS-0424'], 'OS-0424 horas ≤ janela ou aviso', f'{h} h numa janela de {dj} h, sem aviso')
# R9 limpeza registrada entre 2,4-D (OS-0430 25/09 13:00) e o próximo uso do PJ-3030 (OS-0421 26/09 06:00)
ca = open(os.path.join(O, 'carga_santarita.txt')).read()
ok('R9', re.search(r'[Ll]impeza|descontamina', ca + P['OS-0430'] + P['OS-0421']) is not None, 'passo de limpeza depois de 2,4-D', 'PJ-3030 25/09: OS-0421 06–11 + OS-0430 13:00–20:24; 26/09 OS-0421 06–12; nenhum passo de limpeza')
# R10 calibração: ficha mostra vazão alvo por bico (L/min)
ok('R10', re.search(r'L/min', T('OS-0424-ficha.txt') + T('OS-0424-app_Marcos.txt')) is not None, 'ficha com vazão alvo por bico', 'ficha só tem "leque 110-015 · 3 bar"; espaçamento não cadastrado')
print('RESUMO:', sum(1 for _, c in res if not c), 'de', len(res), 'reprovam hoje')
