# -*- coding: utf-8 -*-
"""CONF-01 · app de campo no mesmo estado de Configurações (revisão 09/10, F14 e F16), sem navegador: monta o JS real do app como a página MB
(g2lib.js inteiro + assinatura + CONF0/configuracoes.js + cenário com produção + JS do app) e confere no node:
- F16 descartar turno respeita o acesso do operador (mbDescartar → cenAppAtivo), como iniciar, pausar e fechar;
- F14 o passo da ordem nomeia quem entregou (movimento da entrega), nunca nome fixo.
Uso (de gen37/): python3 config_app_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
import cenario
import dados_assinatura as DA
import dados_config as DCF
from areas import mobile
PRE = ("globalThis.print=(...a)=>console.log(...a);\nvar __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
       "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
CASOS = r"""
let nfail = 0, n = 0;
function ok(t, c, got) { n++; if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 400))); } }
const G = () => cenGet(); const M = f => cenMudar(null, f); const ini = () => { cenReset(); G2_PERFIL_MEM = ''; };
const passo = id => { const c = G(); const p = mbPasso(c, c.ordens[id]); return [p.k, p.chip[0]]; };
try {
  ini(); M(c => { cenIniciarTurno(c, 'OS-0421'); return { msg: '' }; }); M(c => confAcesso(c, 'p2', false, 'k', 'Ana')); const rv = G().rev;
  const r = M(c => mbDescartar(c));
  ok('F16 Marcos desativado: descartar o turno é recusado ("Acesso de Marcos desativado") e o turno fica', /Acesso de Marcos desativado/.test(r.erro || '') && G().rev === rv && !!G().app.turno, r);
  ini(); M(c => { cenIniciarTurno(c, 'OS-0421'); return { msg: '' }; }); const r2 = M(c => mbDescartar(c));
  ok('F16 referência: com acesso, descartar segue', !r2.erro && !G().app.turno, r2);
  ini(); const e = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Marcos', 'Paula'));
  ok('F14 MB-01: "Entregue por Paula" quando Paula entregou (o movimento diz), não "por Rui"', !e.erro && JSON.stringify(passo('OS-0424')) === JSON.stringify(['confirmar', 'Entregue por Paula · REQ-039']), [e.erro, passo('OS-0424')]);
  ini(); M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Marcos', 'Rui'));
  ok('F14 referência: entregue por Rui segue "Entregue por Rui" (app_cenario_test)', passo('OS-0424')[1] === 'Entregue por Rui · REQ-039', passo('OS-0424'));
} catch (e) { ok('ERRO ' + String(e.message || e), false); }
console.log('RESULTADO ' + (n - nfail) + '/' + n);
"""
src = PRE + open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read() + '\n' + DA.js_prefixo() + DCF.js_prefixo() + cenario.js_prefixo() + mobile.JS_BASE + mobile.MBAPP_JS + CASOS
fd, p = tempfile.mkstemp(prefix='confapp_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
finally: os.unlink(p)
print(r.stdout, end='')
if r.returncode: print('FALHA motor JS:', r.stderr[-1500:])
lin = r.stdout.splitlines(); fa = sum(1 for l in lin if l.startswith('FALHA ')); tot = sum(1 for l in lin if l.startswith(('OK ', 'FALHA ')))
sys.exit(0 if tot and not fa and r.returncode == 0 else 1)
