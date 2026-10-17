# -*- coding: utf-8 -*-
"""Medida do robô v5 (EX-51) numa candidata do protótipo, com um comando.

Uso (qualquer pasta; os caminhos do pacote são relativos a este arquivo):
  python3 -I rodar.py --render <_render da candidata> --trabalho <dir de trabalho>
          [--modos isolado,pacote] [--fases preparar,robo,leva,nav,escopo28,resumo] [--so T1,T2] [--limite-min 90]
          [--entrega <pasta>]   copia resumos, entradas e brutos (tar.gz se passarem de 5 MB) para a pasta

Modos do robô (o código de medida e de contagem é o mesmo; muda só onde os quadros rodam):
  isolado  padrão. Três trabalhadores, cada um numa aba e numa origem própria (porta própria), com um quadro cada.
           O Voltar do navegador de um quadro não mexe nos outros e o armazenamento local não é compartilhado.
  pacote   como veio no pacote: uma aba, três quadros na mesma página. O Voltar do navegador (history.back) de um quadro
           anda na história conjunta da aba e pode voltar OUTRO quadro (conferido: ver LEIAME, "Diferenças de método").

Fases (nesta ordem):
  preparar  copia o _render para <trabalho>/v3 e gera ocultas.json e screens.json (preparar.py)
  robo      abre o robô no Chrome headless via CDP, roda run5() e espera window.__fim
  leva      2ª passada (leva-check.json): abre o endereço de cada passagem que leva um registro e espera 2,6 s
  nav       navegacao.json: h1 renderizado de cada página .dc.html
  escopo28  escopo-28.json: Fazenda e Safra escolhidas na O.S. (Cargas, para a própria O.S.) chegam a cada uma das 28 telas
            principais do resumo? Mesma ação do escopo() do robô, com controle pelo padrão de cada tela aberta do zero
  resumo    anexo-robo-v5-resumo.py (com e sem a 2ª passada) e comparar.py (tabela v108 × agora)

Regras: só 127.0.0.1; espera haver menos de 4 processos Chrome principais antes de abrir o seu; encerra só os processos que
iniciou (pelo PID); perfil do Chrome temporário em /dev/shm, apagado no fim.
"""
import argparse, base64, json, os, re, shutil, socket, struct, subprocess, sys, tempfile, time, unicodedata
import urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
PACOTE = os.path.normpath(os.path.join(AQUI, '..'))
BASE = os.path.join(PACOTE, 'robo-v5-base')
ROBO = os.path.join(AQUI, 'robot.html')
RESUMO = os.path.join(AQUI, 'resumo.py')
CHROME = '/tmp/cloudchrome/chrome'
# única mudança no robô para o modo isolado: número de quadros configurável (padrão 3, igual ao pacote)
ROBO_DE = 'const frs = [0, 1, 2].map(() => {'
ROBO_PARA = 'const frs = Array.from({ length: window.__ROBO_FRAMES || 3 }, (_, k) => k).map(() => {'


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def porta_livre():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


# ---------- processos Chrome principais (sem --type=; crashpad não conta) ----------
def chromes_principais():
    n = []
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            a = open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\0')
        except OSError:
            continue
        if not a or not a[0]:
            continue
        exe = os.path.basename(a[0].decode('utf-8', 'replace'))
        if exe not in ('chrome', 'chromium', 'chromium-browser', 'headless_shell', 'google-chrome'):
            continue
        if any(x.startswith(b'--type=') for x in a):
            continue
        n.append(int(pid))
    return n


def esperar_vaga(max_min=60):
    t0 = time.time()
    while True:
        n = chromes_principais()
        if len(n) < 4:
            log(f'Chrome principais em execução: {len(n)} (< 4), pode abrir')
            return
        if time.time() - t0 > max_min * 60:
            sys.exit(f'Ainda há {len(n)} Chrome principais depois de {max_min} min; não abro outro')
        log(f'Chrome principais em execução: {len(n)}; espero 20 s')
        time.sleep(20)


# ---------- CDP mínimo (websocket RFC 6455; mesma abordagem de tools/prototipo/v37/gen37/cdp.py) ----------
class WS:
    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.s = socket.create_connection((u.hostname, u.port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                        f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            c = self.s.recv(4096)
            if not c:
                raise ConnectionError('websocket fechado no handshake')
            buf += c
        if b' 101 ' not in buf.split(b'\r\n')[0]:
            raise RuntimeError(buf[:200])
        self.rest = buf.split(b'\r\n\r\n', 1)[1]

    def _read(self, n, fim):
        while len(self.rest) < n:
            falta = fim - time.monotonic()
            if falta <= 0:
                raise TimeoutError
            self.s.settimeout(falta)
            c = self.s.recv(1 << 20)
            if not c:
                raise ConnectionError('websocket fechado')
            self.rest += c
        d, self.rest = self.rest[:n], self.rest[n:]
        return d

    def send(self, text):
        p = text.encode()
        m = os.urandom(4)
        n = len(p)
        h = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else (bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536 else bytes([0x80 | 127]) + struct.pack('>Q', n)))
        self.s.sendall(h + m + bytes(b ^ m[i % 4] for i, b in enumerate(p)))

    def recv(self, timeout):
        fim = time.monotonic() + timeout
        out = b''
        while True:
            b0, b1 = self._read(2, fim)
            op = b0 & 0x0f
            n = b1 & 0x7f
            if n == 126:
                n = struct.unpack('>H', self._read(2, fim))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._read(8, fim))[0]
            if b1 & 0x80:
                mk = self._read(4, fim)
                data = bytes(x ^ mk[i % 4] for i, x in enumerate(self._read(n, fim)))
            else:
                data = self._read(n, fim)
            if op == 9:
                continue
            out += data
            if b0 & 0x80:
                return out.decode('utf-8', 'replace')


class Aba:
    def __init__(self, info, dialogos):
        self.tid = info['id']
        self.ws = WS(info['webSocketDebuggerUrl'])
        self.i = 0
        self.dialogos = dialogos
        self.call('Page.enable')
        self.call('Runtime.enable')
        self.call('Emulation.setFocusEmulationEnabled', {'enabled': True})   # cada aba age como a aba em foco

    def _evento(self, m):
        if m.get('method') == 'Page.javascriptDialogOpening':
            pr = m.get('params') or {}
            tipo = pr.get('type')
            aceita = tipo in ('alert', 'beforeunload')   # confirm e prompt são cancelados: o robô não executa ação por diálogo
            self.dialogos.append({'tipo': tipo, 'msg': (pr.get('message') or '')[:160], 'url': pr.get('url', ''), 'aceito': aceita})
            self.i += 1
            self.ws.send(json.dumps({'id': self.i, 'method': 'Page.handleJavaScriptDialog', 'params': {'accept': aceita}}))

    def call(self, method, params=None, timeout=60):
        self.i += 1
        mid = self.i
        self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        fim = time.monotonic() + timeout
        while True:
            falta = fim - time.monotonic()
            if falta <= 0:
                raise TimeoutError(method)
            try:
                m = json.loads(self.ws.recv(falta))
            except (TimeoutError, socket.timeout):
                raise TimeoutError(method)
            if m.get('id') == mid:
                if 'error' in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get('result', {})
            if 'method' in m:
                self._evento(m)

    def pump(self, seg):
        fim = time.monotonic() + seg
        while True:
            falta = fim - time.monotonic()
            if falta <= 0:
                return
            try:
                m = json.loads(self.ws.recv(falta))
            except (TimeoutError, socket.timeout):
                return
            if 'method' in m:
                self._evento(m)

    def js(self, expr, timeout=60):
        r = self.call('Runtime.evaluate', {'expression': expr, 'awaitPromise': True, 'returnByValue': True}, timeout=timeout)
        if 'exceptionDetails' in r:
            raise RuntimeError(r['exceptionDetails'].get('text', 'js') + ' ' + str((r['exceptionDetails'].get('exception') or {}).get('description', ''))[:300])
        return r['result'].get('value')

    def goto(self, url, espera_corpo=True, max_s=20):
        """Navega e espera o documento novo (não o anterior) completo; com espera_corpo, também texto no corpo."""
        self.js("window.__robo5Velho = 1; 1")
        self.call('Page.navigate', {'url': url})
        fim = time.monotonic() + max_s
        cond = "!window.__robo5Velho && document.readyState==='complete'" + (" && !!document.body && document.body.innerText.length>50" if espera_corpo else '')
        while time.monotonic() < fim:
            self.pump(0.2)
            try:
                if self.js(cond, timeout=10):
                    return True
            except Exception:
                pass
        return False


class Chrome:
    def __init__(self, binario, w=3920, h=1200):
        self.port = porta_livre()
        self.dir = tempfile.mkdtemp(prefix='robo5_', dir='/dev/shm' if os.path.isdir('/dev/shm') else None)
        self.p = subprocess.Popen([binario, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
                                   '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
                                   '--disk-cache-size=1048576', f'--remote-debugging-port={self.port}', f'--user-data-dir={self.dir}',
                                   f'--window-size={w},{h}', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        log(f'Chrome iniciado, PID {self.p.pid}')
        self.dialogos = []
        tabs = None
        fim = time.monotonic() + 60
        while time.monotonic() < fim:
            try:
                tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json', timeout=5))
                break
            except Exception:
                time.sleep(0.3)
        pages = [x for x in (tabs or []) if x.get('type') == 'page']
        if not pages:
            self.close()
            raise RuntimeError('Chrome headless não respondeu em 60 s')
        self.abas = [Aba(pages[0], self.dialogos)]

    def nova_aba(self):
        """Aba nova em janela própria: no headless só a aba da frente de cada janela fica visível (as de trás param o
        requestAnimationFrame); com uma janela por aba, todas ficam visíveis."""
        if not hasattr(self, 'navegador'):
            info = json.load(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/version', timeout=10))
            self.navegador = WS(info['webSocketDebuggerUrl'])
            self.nid = 0
        self.nid += 1
        self.navegador.send(json.dumps({'id': self.nid, 'method': 'Target.createTarget', 'params': {'url': 'about:blank', 'newWindow': True}}))
        fim = time.monotonic() + 30
        tid = None
        while time.monotonic() < fim and not tid:
            m = json.loads(self.navegador.recv(30))
            if m.get('id') == self.nid:
                tid = m['result']['targetId']
        for _ in range(50):
            tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json', timeout=5))
            info = next((t for t in tabs if t.get('id') == tid), None)
            if info and info.get('webSocketDebuggerUrl'):
                break
            time.sleep(0.2)
        a = Aba(info, self.dialogos)
        self.abas.append(a)
        return a

    def fechar_extras(self):
        """Fecha abas que as páginas abriram (window.open); as do robô ficam."""
        try:
            tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json', timeout=5))
        except Exception:
            return 0
        minhas = {a.tid for a in self.abas}
        n = 0
        for t in tabs:
            if t.get('type') == 'page' and t.get('id') not in minhas:
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/close/{t['id']}", timeout=5).read()
                    n += 1
                except Exception:
                    pass
        return n

    def close(self):
        if getattr(self, '_fechado', False):
            return
        self._fechado = True
        try:
            self.p.terminate()
            self.p.wait(10)
        except Exception:
            try:
                self.p.kill()
                self.p.wait(10)
            except Exception:
                pass
        shutil.rmtree(self.dir, ignore_errors=True)


# ---------- servidores (subprocessos; encerrados pelo PID) ----------
class Servidores:
    def __init__(self):
        self.ps = []

    def subir(self, trab, robo, telas, saida):
        p = subprocess.Popen([sys.executable, '-I', os.path.join(BASE, 'servidor.py'), '--trabalho', trab, '--robo', robo, '--telas', telas, '--saida', saida],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, start_new_session=True)
        linha = p.stdout.readline().strip()
        if not linha.startswith('porta '):
            p.terminate()
            raise RuntimeError('servidor não subiu')
        self.ps.append(p)
        porta = int(linha.split()[1])
        log(f'servidor em 127.0.0.1:{porta}, PID {p.pid}')
        return f'http://127.0.0.1:{porta}'

    def parar(self):
        for p in self.ps:
            p.terminate()
            try:
                p.wait(10)
            except Exception:
                p.kill()
            log(f'servidor PID {p.pid} encerrado')
        self.ps = []


def limpar_origem(aba, base):
    aba.goto(base + '/robot3/vazio.html', espera_corpo=False)
    aba.js("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Proprietário'); 1")


# ---------- fase robo ----------
def fase_robo(chrome, srvs, trab, modo, so, limite_min, workers):
    saida = os.path.join(trab, 'saida-' + modo)
    shutil.rmtree(saida, ignore_errors=True)
    os.makedirs(saida)
    telas = json.load(open(os.path.join(trab, 'robot3', 'screens.json'), encoding='utf-8'))
    if so:
        telas = [t for t in telas if t['n'] in so]
    if modo == 'pacote':
        robo = ROBO
        grupos = [telas]
        quadros = None
    else:
        s = open(ROBO, encoding='utf-8').read()
        if s.count(ROBO_DE) != 1:
            raise RuntimeError('robô mudou: não achei o ponto de criação dos quadros')
        robo = os.path.join(trab, 'robo-v5-isolado.html')
        open(robo, 'w', encoding='utf-8').write(s.replace(ROBO_DE, ROBO_PARA))
        grupos = [telas[k::workers] for k in range(workers)]
        quadros = 1
    trabalhos = []
    starts = []
    for k, g in enumerate(grupos):
        f = os.path.join(trab, 'robot3', f'screens-{modo}-{k}.json')
        json.dump(g, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
        base = srvs.subir(trab, robo, f, saida)
        aba = chrome.abas[k] if k < len(chrome.abas) else chrome.nova_aba()
        if not aba.goto(base + '/anexo-robo-v5.html', espera_corpo=False):
            raise RuntimeError('robô não carregou')
        # o 1º trabalhador roda run5() inteiro (inclui o teste de escopo); os outros, run5(lista) (o robô pula o escopo)
        arg = 'undefined' if (k == 0 and not so) else json.dumps([t['n'] for t in g])
        pre = f'window.__ROBO_FRAMES = {quadros};' if quadros else ''
        starts.append((aba, f'(()=>{{ {pre} window.__erroRun5 = null; window.run5({arg}).catch(e => {{ window.__erroRun5 = String(e && e.stack || e); }}); return 1; }})()'))
        trabalhos.append((aba, base, len(g)))
    if modo != 'isolado':
        raise RuntimeError('v5.1 exige modo isolado; v5 original preservado na base')
    for k,(aba,_,_) in enumerate(trabalhos):
        aba.js(f"localStorage.setItem('ex51-isolation-{k}', 'worker-{k}'); 1")
    checks=[]
    for k,(aba,base,_) in enumerate(trabalhos):
        marks=aba.js("Object.keys(localStorage).filter(k=>k.startsWith('ex51-isolation-'))")
        checks.append({'worker':k,'origin':base,'marks':marks})
        if marks != ['ex51-isolation-'+str(k)]:
            raise RuntimeError('armazenamento não isolado: '+str(checks))
        aba.js(f"localStorage.removeItem('ex51-isolation-{k}'); 1")
    json.dump(checks,open(os.path.join(trab,'isolamento-v51.json'),'w'),indent=2)
    for aba,js in starts:
        aba.js(js)
    log(f'robô ({modo}): {len(telas)} telas em {len(trabalhos)} aba(s)')
    t0 = time.time()
    ultimo = None
    while True:
        for aba, _, _ in trabalhos:
            aba.pump(3)
        chrome.fechar_extras()
        st = [aba.js("({fim: !!window.__fim, feitas: window.__done || 0, erro: window.__erroRun5})") for aba, _, _ in trabalhos]
        for x in st:
            if x['erro']:
                raise RuntimeError('run5: ' + x['erro'])
        feitas = sum(x['feitas'] for x in st)
        if feitas != ultimo:
            log(f'robô ({modo}): feitas {feitas} de {len(telas)} · {(time.time() - t0) / 60:.1f} min')
            ultimo = feitas
        if all(x['fim'] for x in st):
            break
        if time.time() - t0 > limite_min * 60:
            raise TimeoutError(f'robô passou de {limite_min} min ({feitas} de {len(telas)})')
    with open(os.path.join(trab, f'robo-{modo}.log'), 'w', encoding='utf-8') as f:
        for k, (aba, _, _) in enumerate(trabalhos):
            f.write(f'# aba {k}\n' + aba.js("document.getElementById('log').textContent") + '\n')
    dur = time.time() - t0
    log(f'robô ({modo}) terminou em {dur / 60:.1f} min')
    return dur, trabalhos[0][1]


# ---------- fase leva (2ª passada) ----------
VISTA = {'vis', 'modo', 'passo', 'aba', 'visao', 'etapa', 'tab', 'view', 'r'}   # chaves de visão: não identificam registro


def sem_acento(t):
    t = unicodedata.normalize('NFD', t or '')
    return ''.join(ch for ch in t if unicodedata.category(ch) != 'Mn').lower()


def norm_tok(t):
    return re.sub(r'\s+', ' ', re.sub(r'[-_+]', ' ', sem_acento(t))).strip()


def tokens(url):
    h = url.split('#', 1)[1] if '#' in url else ''
    out = []
    for parte in h.split('&'):
        parte = urllib.parse.unquote(parte)
        if '=' in parte:
            k, v = parte.split('=', 1)
            if k.strip().lower() in VISTA:
                continue
        else:
            v = parte
        v = norm_tok(v)
        if len(v) >= 3:
            out.append(v)
    return out


def entr_do_resumo():
    s = open(RESUMO, encoding='utf-8').read()
    m = re.search(r"ENTR = re\.compile\(r'(.+?)'\)", s)
    return re.compile(m.group(1))


LEVA_JS = r"""(() => {
  const norm = t => (t || '').replace(/\s+/g, ' ').trim();
  const vis = e => !!(e && e.getClientRects().length) && getComputedStyle(e).visibility !== 'hidden';
  const dl = [...document.querySelectorAll('[role=dialog],dialog[open],[aria-modal=true]')].filter(vis);
  const d = dl[dl.length - 1] || null;
  let dlg = '';
  if (d) { const h = d.querySelector('h1,h2,h3,[role=heading]'); dlg = h ? norm(h.innerText).slice(0, 100) : (norm(d.innerText).slice(0, 60) || '(diálogo sem título)'); }
  const h1 = norm((document.querySelector('h1') || {}).innerText || '');
  const selected=[...document.querySelectorAll('.g2flash,[aria-selected=true],.g2r:focus,.g2r:focus-within')].filter(vis).map(e=>norm(e.innerText));
  return { dlg, h1, selected, url: location.pathname.split('/').pop().replace('.dc.html', '') + location.hash, corpo: document.body ? document.body.innerText : '' };
})()"""


def fase_leva(chrome, base, trab, modo):
    aba = chrome.abas[0]
    ENTR = entr_do_resumo()
    saida = os.path.join(trab, 'saida-' + modo)
    alvos = []
    for f in sorted(os.listdir(saida)):
        if not f.endswith('.v5.json') or f.startswith('escopo'):
            continue
        d = json.load(open(os.path.join(saida, f), encoding='utf-8'))
        for i, p in enumerate(d.get('passagens', [])):
            if p.get('r') != 'navega':
                continue
            para = p.get('para') or ''
            isrec = p.get('origem') == 'detalhe' or bool(p.get('alvo')) or '#' in para     # mesmo critério do resumo
            leva = ('#' in (p['el'].get('h') or '')) or bool(ENTR.search(p['el']['t'])) or ('#' in para)
            if not (isrec and leva):
                continue
            h = p['el'].get('h') or ''
            if p['el'].get('k') == 'a' and h:
                url = urllib.parse.urljoin(f'{base}/v3/{d["screen"]}.dc.html', h)
            else:
                dest, _, hh = para.partition('#')
                url = f'{base}/v3/{dest}.dc.html' + ('#' + hh if hh else '')
            alvos.append((d['screen'], i, url, p.get('alvo') or ''))
    log(f'2ª passada ({modo}): {len(alvos)} passagens que levam um registro')
    base_corpo = {}
    out = []
    for k, (tela, i, url, alvo) in enumerate(alvos):
        limpar_origem(aba, base)
        aba.goto(url, espera_corpo=False)
        aba.pump(2.6)
        r = aba.js(LEVA_JS)
        corpo_n = norm_tok(r['corpo'])
        toks = tokens(url)
        tok = next((t for t in toks if t in corpo_n), '')
        pag = url.split('#')[0]
        if pag not in base_corpo:      # diagnóstico: o mesmo texto aparece sem o endereço do registro?
            limpar_origem(aba, base)
            aba.goto(pag, espera_corpo=False)
            aba.pump(2.6)
            base_corpo[pag] = norm_tok(aba.js(LEVA_JS)['corpo'])
        out.append({'tela': tela, 'i': i, 'endereco': url.split('/v3/', 1)[-1], 'alvo': alvo, 'dlg': r['dlg'], 'h1': r['h1'][:120],
                    'alvoNoH1': bool(alvo and alvo in r['h1']), 'url': r['url'], 'alvoNoCorpo': False, 'tokNoCorpo': '', 'chegouEstrito': bool(alvo and re.search(r'(?<![A-Za-z0-9_-])'+re.escape(alvo)+r'(?![A-Za-z0-9_-])',' '.join([r['dlg']]+r.get('selected',[])))),
                    'diag': {'tokens': toks, 'tokSemEndereco': bool(tok and tok in base_corpo[pag]),
                             'alvoSemEndereco': bool(alvo and norm_tok(alvo) in base_corpo[pag])}})
        chrome.fechar_extras()
        if (k + 1) % 25 == 0:
            log(f'2ª passada ({modo}): {k + 1}/{len(alvos)}')
    json.dump(out, open(os.path.join(saida, 'leva-check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    log(f'2ª passada ({modo}): leva-check.json gravado')


# ---------- fase nav (h1 renderizado de cada página) ----------
def fase_nav(chrome, base, trab):
    aba = chrome.abas[0]
    v3 = os.path.join(trab, 'v3')
    rows = []
    for f in sorted(os.listdir(v3)):
        if not f.endswith('.dc.html'):
            continue
        t = f[:-len('.dc.html')]
        limpar_origem(aba, base)
        aba.goto(f'{base}/v3/{f}', espera_corpo=True, max_s=12)
        aba.pump(0.5)
        r = aba.js("({h1: ((document.querySelector('h1')||{}).innerText||'').replace(/\\s+/g,' ').trim(), title: document.title})")
        rows.append({'tela': t, 'titulo': r['h1'] or r['title'], 'h1': r['h1'], 'title': r['title']})
        chrome.fechar_extras()
    json.dump({'rows': rows}, open(os.path.join(trab, 'entradas', 'navegacao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    log(f'navegacao.json: {len(rows)} páginas')


# ---------- fase escopo28 ----------
ESC_LER = r"""(() => { const vis = e => !!(e && e.getClientRects().length) && getComputedStyle(e).visibility !== 'hidden';
  const s = [...document.querySelectorAll('select')].filter(vis); const o = {}, op = {};
  for (const [k, re] of [['fazenda', /fazenda/i], ['safra', /safra/i]]) { const x = s.find(x => re.test(x.getAttribute('aria-label') || ''));
    o[k] = x ? (x.options[x.selectedIndex] || {}).text || '' : null; op[k] = x ? [...x.options].map(o => o.text) : null; }
  return { sel: o, opcoes: op }; })()"""
# mesma ação do escopo() do robô: escolhe a opção pelo texto, dispara change e input
ESC_SET = r"""((rotulo, v) => { const vis = e => !!(e && e.getClientRects().length) && getComputedStyle(e).visibility !== 'hidden';
  const x = [...document.querySelectorAll('select')].filter(vis).find(x => new RegExp(rotulo, 'i').test(x.getAttribute('aria-label') || ''));
  if (!x) return null; const o = [...x.options].find(o => o.text === v || o.value === v); if (!o) return null;
  x.value = o.value; x.dispatchEvent(new Event('change', { bubbles: true })); x.dispatchEvent(new Event('input', { bubbles: true })); return o.value; })"""
# valores preferidos, na ordem: o 1º é o do escopo() do robô; os outros só entram quando o padrão da tela de destino já é o 1º
PREF = {'fazenda': ['Lagoa Grande', 'Boa Vista', 'Santa Rita'], 'safra': ['2026/27', 'Safrinha 2027', '2025/26']}


def princ_do_resumo():
    s = open(RESUMO, encoding='utf-8').read()
    return json.loads(re.search(r"PRINC = (\[.*?\])", s).group(1).replace("'", '"'))


def fase_escopo28(chrome, base, trab, origem='OS', origem_alt='CARGA'):
    """Escolhe Fazenda e Safra numa tela (O.S.; para a própria O.S., Cargas) e abre a tela de destino pelo endereço, na mesma aba,
    como o escopo() do robô. Controle: o padrão do destino aberto do zero. Por seletor, o valor escolhido é o 1º de PREF que existe
    na origem e no destino e difere do padrão do destino; sem valor assim, o seletor não é testável.
    Resultado: sem seletor | inconclusivo (nenhum seletor testável) | herda (todos os testáveis chegam com a escolha) | não herda."""
    aba = chrome.abas[0]

    def abrir(t):
        limpar_origem(aba, base)
        aba.goto(f'{base}/v3/{t}.dc.html', espera_corpo=True, max_s=12)
        aba.pump(1.0)
        return aba.js(ESC_LER)

    ops_origem = {o: abrir(o)['opcoes'] for o in (origem, origem_alt)}
    out = []
    for t in princ_do_resumo():
        org = origem_alt if t == origem else origem
        padrao = abrir(t)
        escolha = {}
        for k in ('fazenda', 'safra'):
            if padrao['sel'][k] is None:
                continue
            v = next((v for v in PREF[k] if v in (ops_origem[org][k] or []) and v in padrao['opcoes'][k] and v != padrao['sel'][k]), None)
            if v:
                escolha[k] = v
        abrir(org)
        aplicou = {}
        for k, v in escolha.items():
            aplicou[k] = aba.js(f'({ESC_SET})({json.dumps(k)}, {json.dumps(v)})')
            aba.pump(0.3)
        lido_origem = aba.js(ESC_LER)['sel']
        aba.js("window.__robo5Velho = 1; 1")
        aba.js(f"location.href = {json.dumps(t + '.dc.html')}; 1")
        fim = time.monotonic() + 12
        while time.monotonic() < fim:
            aba.pump(0.25)
            try:
                if aba.js("!window.__robo5Velho && document.readyState==='complete' && !!document.body && document.body.innerText.length>50"):
                    break
            except Exception:
                pass
        aba.pump(1.0)
        chegou = aba.js(ESC_LER)['sel']
        if padrao['sel']['fazenda'] is None and padrao['sel']['safra'] is None:
            res = 'sem seletor'
        elif not escolha:
            res = 'inconclusivo'
        elif all(chegou.get(k) == v for k, v in escolha.items()):
            res = 'herda'
        else:
            res = 'não herda'
        out.append({'tela': t, 'origem': org, 'escolha': escolha, 'aplicouNaOrigem': lido_origem, 'padrao': padrao['sel'], 'opcoesDestino': padrao['opcoes'],
                    'chegou': chegou, 'resultado': res})
        chrome.fechar_extras()
    json.dump(out, open(os.path.join(trab, 'escopo-28.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log('escopo-28.json: ' + ', '.join(f"{k}={sum(1 for x in out if x['resultado'] == k)}" for k in sorted({x['resultado'] for x in out})))


# ---------- fase resumo ----------
def resumir(trab, saida, destino):
    oc = os.path.join(trab, 'entradas', 'ocultas.json')
    r = subprocess.run([sys.executable, '-I', RESUMO, saida, oc, os.path.join(trab, 'v3'), destino], capture_output=True, text=True)
    print(os.path.basename(destino), r.stdout.strip(), r.stderr.strip(), flush=True)
    if r.returncode:
        raise RuntimeError('resumo falhou: ' + destino)


def fase_resumo(trab, modos):
    for modo in modos:
        saida = os.path.join(trab, 'saida-' + modo)
        if not os.path.isdir(saida):
            continue
        resumir(trab, saida, os.path.join(trab, f'resumo-{modo}.json'))
        # a mesma medida sem a 2ª passada: os mesmos brutos, sem leva-check.json
        so1 = os.path.join(trab, f'saida-{modo}-1a')
        shutil.rmtree(so1, ignore_errors=True)
        os.makedirs(so1)
        for f in os.listdir(saida):
            if f.endswith('.v5.json'):
                os.symlink(os.path.join(saida, f), os.path.join(so1, f))
        resumir(trab, so1, os.path.join(trab, f'resumo-{modo}-1a-passada.json'))
    json.dump({'metodo':'v5.1','comparavel_com_v5':False,'motivo':'oráculos corrigidos; confrontar os brutos caso a caso'},open(os.path.join(trab,'comparacao.json'),'w'),ensure_ascii=False,indent=2)


def entregar(trab, modos, destino):
    import tarfile
    os.makedirs(destino, exist_ok=True)
    for f in ['isolamento-v51.json', 'comparacao.json', 'escopo-28.json', 'execucao.json', 'preparo.json', 'v3.sha256'] + \
             [f'resumo-{m}{x}.json' for m in modos for x in ('', '-1a-passada') if (m, x) != ('isolado', '')] + [f'robo-{m}.log' for m in modos]:
        if os.path.exists(os.path.join(trab, f)):
            shutil.copy2(os.path.join(trab, f), destino)
    if os.path.exists(os.path.join(trab, 'resumo-isolado.json')):
        shutil.copy2(os.path.join(trab, 'resumo-isolado.json'), os.path.join(destino, 'resumo.json'))
    os.makedirs(os.path.join(destino, 'entradas'), exist_ok=True)
    for f in ('ocultas.json', 'navegacao.json'):
        if os.path.exists(os.path.join(trab, 'entradas', f)):
            shutil.copy2(os.path.join(trab, 'entradas', f), os.path.join(destino, 'entradas'))
    shutil.copy2(os.path.join(trab, 'robot3', 'screens.json'), os.path.join(destino, 'entradas'))
    brutos = []
    for m in modos:
        d = os.path.join(trab, 'saida-' + m)
        if os.path.isdir(d):
            brutos += [(os.path.join(d, f), f'brutos-{m}/{f}') for f in sorted(os.listdir(d)) if f.endswith('.json') and not f.startswith('.')]
    total = sum(os.path.getsize(a) for a, _ in brutos)
    if total > 5 * 1024 * 1024:
        with tarfile.open(os.path.join(destino, 'brutos.tar.gz'), 'w:gz') as t:
            for a, n in brutos:
                t.add(a, arcname=n)
    else:
        for a, n in brutos:
            os.makedirs(os.path.dirname(os.path.join(destino, n)), exist_ok=True)
            shutil.copy2(a, os.path.join(destino, n))
    log(f'entrega em {destino}: {len(brutos)} brutos ({total / 1024 / 1024:.1f} MB{", comprimidos" if total > 5 * 1024 * 1024 else ""})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--render')
    ap.add_argument('--trabalho', required=True)
    ap.add_argument('--modos', default='isolado')
    ap.add_argument('--so', default='')
    ap.add_argument('--fases', default='preparar,robo,leva,nav,escopo28,resumo')
    ap.add_argument('--chrome', default=CHROME)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--limite-min', type=float, default=90)
    ap.add_argument('--entrega')
    a = ap.parse_args()
    fases = a.fases.split(',')
    modos = a.modos.split(',')
    trab = os.path.abspath(a.trabalho)
    so = [x for x in a.so.split(',') if x]
    t0 = time.time()
    exec_json = os.path.join(trab, 'execucao.json')
    if 'preparar' in fases:
        if not a.render:
            sys.exit('--render é obrigatório na fase preparar')
        r = subprocess.run([sys.executable, '-I', os.path.join(BASE, 'preparar.py'), '--render', a.render, '--trabalho', trab])
        if r.returncode:
            sys.exit('preparar falhou')
    reg = json.load(open(exec_json, encoding='utf-8')) if os.path.exists(exec_json) else {}
    if any(f in fases for f in ('robo', 'leva', 'nav', 'escopo28')):
        for modo in modos:
            if not any(f in fases for f in ('robo', 'leva')):
                break
            esperar_vaga()
            srvs = Servidores()
            c = None
            t1 = time.time()
            try:
                c = Chrome(a.chrome)
                if 'robo' in fases:
                    dur, base = fase_robo(c, srvs, trab, modo, so, a.limite_min, a.workers)
                    reg.setdefault(modo, {})['robo_min'] = round(dur / 60, 1)
                else:
                    base = srvs.subir(trab, ROBO, os.path.join(trab, 'robot3', 'screens.json'), os.path.join(trab, 'saida-' + modo))
                if 'leva' in fases:
                    t2 = time.time()
                    fase_leva(c, base, trab, modo)
                    reg.setdefault(modo, {})['leva_min'] = round((time.time() - t2) / 60, 1)
                reg.setdefault(modo, {}).update({'dialogos_js': list(c.dialogos), 'so': so, 'quando': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                                                 'total_min': round((time.time() - t1) / 60, 1)})
            finally:
                if c:
                    c.close()
                    log(f'Chrome PID {c.p.pid} encerrado')
                srvs.parar()
            json.dump(reg, open(exec_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        if 'nav' in fases or 'escopo28' in fases:
            esperar_vaga()
            srvs = Servidores()
            c = None
            try:
                c = Chrome(a.chrome)
                base = srvs.subir(trab, ROBO, os.path.join(trab, 'robot3', 'screens.json'), os.path.join(trab, 'saida-nav'))
                if 'nav' in fases:
                    t2 = time.time()
                    fase_nav(c, base, trab)
                    reg['nav_min'] = round((time.time() - t2) / 60, 1)
                if 'escopo28' in fases:
                    t2 = time.time()
                    fase_escopo28(c, base, trab)
                    reg['escopo28_min'] = round((time.time() - t2) / 60, 1)
            finally:
                if c:
                    c.close()
                    log(f'Chrome PID {c.p.pid} encerrado')
                srvs.parar()
                shutil.rmtree(os.path.join(trab, 'saida-nav'), ignore_errors=True)
    reg['chrome'] = subprocess.run([a.chrome, '--version'], capture_output=True, text=True).stdout.strip()
    json.dump(reg, open(exec_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if 'resumo' in fases:
        fase_resumo(trab, modos)
    if a.entrega:
        entregar(trab, modos, os.path.abspath(a.entrega))
    log(f'fim em {(time.time() - t0) / 60:.1f} min')


if __name__ == '__main__':
    main()

