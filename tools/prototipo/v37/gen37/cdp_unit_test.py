# -*- coding: utf-8 -*-
"""Teste de unidade do cdp.py (ACELERA, 13/10/2026), sem navegador:
1. WebSocket: mensagens do CDP chegam picadas (e fragmentadas, com ping no meio) e a leitura tem prazo curto; todas têm de
   sair inteiras e na ordem. Defeito protegido: o leitor de 302b26f perdia o cabeçalho lido quando o prazo vencia no meio
   de um quadro e desalinhava o fluxo (10 de 40 mensagens).
2. time.sleep de teste: ≥ 1 s fora de laço vira settle; dentro de laço (sondagem com orçamento de tempo) fica fixo.
3. time.sleep de outro fio (servidor de teste) é tempo real: não vira settle.
Uso: python3 cdp_unit_test.py"""
import os, sys, socket, struct, time, random, threading, tempfile, textwrap
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CHROME_BIN', sys.executable)   # o import do cdp procura um Chrome; aqui ele não é usado
import cdp
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + ('' if cond else ' · ' + str(info)[:300]))


def quadro(txt, fin=True, op=1):
    p = txt.encode(); n = len(p); h = bytes([(0x80 if fin else 0) | op])
    h += bytes([n]) if n < 126 else (bytes([126]) + struct.pack('>H', n) if n < 65536 else bytes([127]) + struct.pack('>Q', n))
    return h + p


def ws_picado(semente):
    random.seed(semente)
    a, b = socket.socketpair(); w = cdp.WS.__new__(cdp.WS); w.s = a; w.rest = b''
    msgs = ['x' * random.choice([5, 200, 70000]) + str(i) for i in range(40)]; fluxo = b''
    for i, m in enumerate(msgs):
        if i % 7 == 3: fluxo += quadro('', op=9)
        fluxo += quadro(m[:10], fin=False) + quadro(m[10:], fin=True, op=0) if i % 5 == 2 else quadro(m)
    def envia():
        k = 0
        while k < len(fluxo):
            n = random.randint(1, 5000); b.sendall(fluxo[k:k + n]); k += n; time.sleep(random.choice([0, 0, 0.03]))
    threading.Thread(target=envia, daemon=True).start()
    got, vencidos, fim = [], 0, time.monotonic() + 20
    try:
        while len(got) < len(msgs) and time.monotonic() < fim:
            try: got.append(w.recv(timeout=0.01))
            except TimeoutError: vencidos += 1
    finally:
        a.close(); b.close()
    return got == msgs, len(got), vencidos


for s in (7, 11):
    igual, n, venc = ws_picado(s)
    chk(f'WS semente {s}: 40 mensagens picadas, fragmentadas e com ping chegam inteiras e na ordem com prazo de 10 ms ({venc} prazos vencidos no meio)', igual and n == 40, (n, venc))

src = textwrap.dedent('''\
    import time
    time.sleep(1.2)
    for i in range(3):
        time.sleep(1)
    while False: time.sleep(1)
    def f():
        time.sleep(2)
    x = [time.sleep(1) for _ in ()]
    ''')
with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as t: t.write(src)
try:
    lacos = {ln: cdp._em_laco(t.name, ln) for ln in (2, 4, 5, 7, 8)}
finally:
    os.unlink(t.name)
chk('time.sleep fora de laço (linha 2, função na linha 7) assenta; em for, while e compreensão (linhas 4, 5, 8) fica fixo',
    lacos == {2: False, 4: True, 5: True, 7: False, 8: True}, lacos)
chk('SAFRION_ESPERA padrão é por condição e time.sleep foi trocado só nesse modo',
    cdp.CONDICAO == ((os.environ.get('SAFRION_ESPERA') or 'condicao').strip().lower() != 'fixa') and ((time.sleep is cdp._sono) == cdp.CONDICAO))
# 3. time.sleep ≥ 1 s de outro fio (servidor de teste, ajudante) é tempo real: não vira settle (o navegador é do fio principal).
class _Nav:
    _fechado = False
    def __init__(self): self.chamadas = []
    def settle(self, q, t): self.chamadas.append(t)
_nav = _Nav(); cdp._USO.append(_nav)
_FONTE = 'import cdp\ncdp._sono(1.0)\n'
with tempfile.NamedTemporaryFile('w', dir=HERE, prefix='_unit_fio_', suffix='.py', delete=False) as _f: _f.write(_FONTE)   # um "teste" do protótipo
_cod = compile(_FONTE, _f.name, 'exec')
try:
    if cdp.CONDICAO:
        th = threading.Thread(target=lambda: exec(_cod, {})); t0 = time.monotonic(); th.start(); th.join(); dt_fio = time.monotonic() - t0
        exec(_cod, {})
        chk('time.sleep(1,0) de outro fio dorme o tempo real (sem settle); o do fio principal vira settle', _nav.chamadas == [1.0] and dt_fio >= 0.99, (_nav.chamadas, round(dt_fio, 2)))
finally:
    cdp._USO.remove(_nav); os.unlink(_f.name)
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
