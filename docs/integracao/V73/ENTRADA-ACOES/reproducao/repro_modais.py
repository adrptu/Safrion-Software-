# -*- coding: utf-8 -*-
"""Reprodução no navegador de ações DENTRO de modais, que o robô da varredura não clicou (executado).

Uso: CHROME_BIN=/tmp/cloudchrome/chrome python3 -B -I repro_modais.py <pasta_render> <pasta_gen37>
- Serve o render (somente leitura) num http.server próprio, numa porta livre; Chrome headless com perfil temporário (cdp.Chrome).
- Casos:
  M1 PL-02 · "Decidir pendência" da C1: o que a lista "Decisão da pendência" mostra, o que o rascunho guarda e o que o Salvar faz.
  M2 CA-01det · painel "Ajustar produtos e doses do saldo": opções da lista "Produto", dose já escrita e o resultado do confirmar
     depois de trocar a dose para 9,99.
  M3 ON-01 · painel "Rever dados": opções da lista "E-mail do responsável".
Nada é gravado fora do perfil temporário; o render não é alterado.
"""
import sys, os, json, time, subprocess, socket
R, G = sys.argv[1], sys.argv[2]
sys.path.insert(0, G)
from cdp import Chrome  # noqa: E402

def livre():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p

CLK = r"""((t)=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')].filter(e=>e.getClientRects().length);
 const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.scrollIntoView({block:'center'}); e.click(); return 'ok';})"""
SETV = r"""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NÃO ACHEI: '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
 Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
TOAST = r"""(()=>[...document.querySelectorAll('[role=status],[role=alert]')].map(e=>e.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).join(' | '))()"""

porta = livre()
srv = subprocess.Popen(['python3', '-m', 'http.server', str(porta), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
c = Chrome(port=livre(), w=1440, h=1100)
out = {}
def J(x): return c.js(x)
def abrir(t):
    c.goto(f'http://127.0.0.1:{porta}/{t}.dc.html', wait=1.5)
def espera(expr, ate=8.0):
    fim = time.monotonic() + ate
    while time.monotonic() < fim:
        if J(expr): return True
        time.sleep(0.2)
    return False
try:
    # M1 · PL-02
    abrir('PL-02')
    m1 = {'clique': J(f"({CLK})('Decidir pendência')")}
    espera("!!document.querySelector('#fx_g_op_dec')")
    m1['lista'] = J("""(()=>{const s=document.querySelector('#fx_g_op_dec'); if(!s) return null;
      return {mostra: s.options[s.selectedIndex]?s.options[s.selectedIndex].text:null, value: s.value, selectedIndex: s.selectedIndex,
              opcoes: [...s.options].map(o=>o.text), evidencia_visivel: !!document.querySelector('#fx_g_op_evid')};})()""")
    m1['salvar'] = J(f"({CLK})('Salvar')"); time.sleep(0.8)
    m1['erros_no_painel'] = J("""(()=>[...document.querySelectorAll('aside,[role=dialog]')].map(e=>e.innerText).join(' ').match(/Informe [^.\\n]*\\./g))()""")
    m1['linha_C1'] = J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/Adubação pós-colheita/.test(x.innerText)); return r?r.innerText.replace(/\\s+/g,' ').slice(0,160):null;})()""")
    out['M1_PL02_decidir_pendencia'] = m1
    # M2 · CA-01det
    abrir('CA-01det')
    m2 = {'abrir_painel': J(f"({CLK})('Ajustar produtos e doses do saldo')")}
    espera("!!document.querySelector('#produto')")
    m2['produto_opcoes'] = J("(()=>{const s=document.querySelector('#produto'); return s?[...s.options].map(o=>o.text):null;})()")
    m2['dose_escrita'] = J("(()=>{const i=document.querySelector('#novadoseporha'); return i?{value:i.value,type:i.type,inputmode:i.getAttribute('inputmode')}:null;})()")
    m2['troca_dose'] = J(f"({SETV})('#novadoseporha','9,99')")
    m2['confirmar'] = J(f"({CLK})('Ajustar e liberar saldo')"); time.sleep(0.8)
    m2['aviso'] = J(TOAST)
    out['M2_CA01det_ajustar_saldo'] = m2
    # M3 · ON-01
    abrir('ON-01')
    m3 = {'abrir_painel': J(f"({CLK})('Rever dados')")}
    espera("!!document.querySelector('select[aria-label^=\"E-mail do responsável\"]')")
    m3['email_opcoes'] = J("(()=>{const s=document.querySelector('select[aria-label^=\"E-mail do responsável\"]'); return s?{tag:s.tagName,opcoes:[...(s.options||[])].map(o=>o.text)}:null;})()")
    out['M3_ON01_rever_dados'] = m3
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(json.dumps(out, ensure_ascii=False, indent=1))
