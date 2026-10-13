# -*- coding: utf-8 -*-
"""CTL-5 · E2 (RL-E3): AG-07 (Consulta Agrofit) só consulta; "Usar na O.S." leva produto da fazenda, cultura e alvo ao "Ajustar antes de
liberar" da ordem A liberar da cultura, e o registro (produto, dose, alvo, quem aprovou) só nasce na O.S., pela trava legal única do CTL-1.
Parte 1 (node, sem navegador): cenario.js + núcleo da O.S. + agOsCand do AG-07 rodam usar_os_unit.js.
Parte 2 (fonte): o AG-07 não tem mais o fluxo paralelo de receituário (gaveta, "Emitir receituário", "Receituário emitido · assinado").
Revisão do CTL-5 (09/10): U4, U5 e U14–U15 (só ordem de pulverização ou tratamento de sementes é candidata), U16–U18 (alvo × referência
conferida, carAlvoRef, a mesma regra no AG-07 e na trava da O.S.), F5 (perfil) e F6 (operação no link).
Uso: python3 usar_os_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, re, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
sys.dont_write_bytecode = True
import cenario
from areas.processo_os import JS_NUCLEO
import areas.agronomia as AG
OK, FAIL = [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:500]), flush=True)
g2 = [l for l in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8') if l.startswith('function g2num')][0]
m = (re.search(r'function agOsOp\(o\)\{.*?\n  \.sort\(\(a,b\)=>AGC\.compare\(a\.id,b\.id\)\); \}', AG.AGF_JS, re.S)
     or re.search(r'function agOsCand\(c,cn\)\{.*?\n  \.sort\(\(a,b\)=>AGC\.compare\(a\.id,b\.id\)\); \}', AG.AGF_JS, re.S))
import json
AGFD = AG.agf_dados()   # osop: operação de cada ordem da semente (o mesmo dado da página)
cand = ("const AGC=new Intl.Collator('pt-BR',{numeric:true,sensitivity:'base'});\nconst AGF={osop:" + json.dumps(AGFD.get('osop') or {}, ensure_ascii=False) + "};\n"
        + m.group(0) + '\n') if m else ''
SHIM = ("globalThis.print=(...a)=>console.log(...a);\n"
        "const __LS={};globalThis.localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v)},removeItem:k=>{delete __LS[k]}};\n"
        "var window={addEventListener(){}}; var location={hash:''};\n")
src = (SHIM + g2 + cenario.perfis_js() + cenario.js_prefixo() + "const OSD={ords:[],nova:{emb:{}}};\n" + JS_NUCLEO + '\n' + cand
       + open(os.path.join(HERE, 'usar_os_unit.js'), encoding='utf-8').read())
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(src)
r = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=180); os.unlink(f.name)
print(r.stdout, end=''); print(r.stderr[-2000:], end='')
for ln in r.stdout.splitlines():
    if ln.startswith('OK    '): OK.append(ln)
    elif ln.startswith('FALHA '): FAIL.append(ln)
if r.returncode or 'JS: ' not in r.stdout: FAIL.append('node: execução interrompida')
# ---- parte 2 · fonte do AG-07
src7 = open(os.path.join(HERE, 'areas', 'agronomia.py'), encoding='utf-8').read()
ini = src7.index('# ================= AG-07'); ag7 = src7[ini:]
proib = [t for t in ('Emitir receituário', 'Receituário emitido', 'Preparar receituário', 'assinado por', 'AG_RT', 'agf_rx', 'rx_emit', '_agf_receituario') if t in ag7]
chk('F1 AG-07 sem fluxo paralelo de receituário (gaveta, "Emitir receituário", "Receituário emitido · assinado por …")', not proib, proib)
chk('F2 AG-07 oferece "Usar na O.S." com cultura, alvo e ordem A liberar, e leva produto, cultura e o alvo como a referência da fazenda o escreve (ar, carAlvoRef)',
    '>Usar na O.S.</button>' in ag7 and 'aria-label="Ordem A liberar"' in ag7 and ":usar='+[pf,cn,ar].map(encodeURIComponent).join('|')" in ag7 and 'carAlvoRef(CARD.prod[n],cn,t)' in ag7)
chk('F3 o link da O.S. aceita #OS-xxxx:usar=<produto>|<cultura>|<alvo> e abre o ajuste com o produto incluído, dose em branco',
    'usar=(.*)' in JS_NUCLEO + open(os.path.join(HERE, 'areas', 'processo_os.py'), encoding='utf-8').read() and "dose:'',alvo:us.alvo" in open(os.path.join(HERE, 'areas', 'processo_os.py'), encoding='utf-8').read())
from areas.processo_os import _nova_ordem_dados
osp = AGFD.get('osp') or []
chk('F4 o AG-07 só oferece produto que a O.S. aceita: AGF.osp = catálogo do "Incluir produto" da O.S. (sem link sem saída para produto só de referência)',
    osp == sorted({x['p'] for x in _nova_ordem_dados()['prods']}) and "F.nf.filter(n=>(AGF.osp||[]).indexOf(n)>=0)" in ag7, len(osp))
pos = open(os.path.join(HERE, 'areas', 'processo_os.py'), encoding='utf-8').read()
chk('F5 perfil sem o papel de agrônomo: o AG-07 desliga "Usar na O.S." e diz quem decide (g2perfil/g2papel/g2quem; revisão do CTL-5, S4-1)',
    "agr=g2papel(PF,'agronomo')" in ag7 and "&&!!ord&&agr;" in ag7 and "é decisão de '+g2quem('agronomo')" in ag7)
chk('F6 o link da O.S. confere a operação (carOpDef) antes de incluir: ordem que não pulveriza não recebe produto da Consulta Agrofit (S3-1)',
    "if(us&&!carOpDef(a.op))" in pos)
print(f'\nRESULTADO {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
