# -*- coding: utf-8 -*-
"""LEVE-1 · executor do leve1_unit.js (regras sem navegador; proprietário 19/10: "leve e fluido"). Monta o JS real das telas em três partes:
  os    g2lib.js + assinatura + Configurações + cenario.js + Estoque + núcleo da O.S. (como o config_unit_test.py): horas do turno, Iniciar e
        Enviar no clique (osDireto), alçada sem motivo e 2º aprovador mantido;
  man   perfis + dados_manutencao (como o ma_vinculo_test.py U): cancelar OM sem motivo, vincular conta de agora, liberar com sugestão;
  mapa  cenario.js + assinatura + base do cadastro + talgeo.js + talmapa.js (como o assinatura_unit_test.py): avisos de área no Mapa.
Uso (de gen37/): SAFRION_DADOS=sintetico python3 -B leve1_unit_test.py   (sai 1 se algo falhar). Contraprova: o mesmo par de arquivos numa
cópia da árvore cbe4cd38 reprova as verificações novas."""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
import cenario
import dados_assinatura as DA
import dados_config as DCF
import dados_manutencao as DM
import areas.processo_os as P
import areas.inicio as I
from areas import processo_estoque as PE
PRE = 'globalThis.print=(...a)=>console.log(...a);\n'
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];},clear:()=>{__ls={};}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
U = open(os.path.join(HERE, 'leve1_unit.js'), encoding='utf-8').read()
G2 = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\nvar GRIDS=[];\n' + PE.JS
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
M = dict(cad0=I._cad0(), hoje_iso='2026-09-23', lg=dict(pivos=[]))
FONTES = {
    'os': PRE + LS + G2 + '\n' + DA.js_prefixo() + DCF.js_prefixo() + EST + '\n' + OS + "\nconst PARTE='os';\n" + U,
    'man': PRE + cenario.perfis_js() + DM.js_prefixo() + "\nconst PARTE='man';\n" + U,
    'mapa': (PRE + "globalThis.localStorage=(()=>{const m=new Map();return{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()};})();\n"
             "globalThis.window=globalThis; if(!globalThis.addEventListener) globalThis.addEventListener=()=>{};\n"
             + cenario.js_prefixo() + DA.js_prefixo() + DA.js_cad0() + 'const M = ' + json.dumps(M, ensure_ascii=False) + ';\n'
             + 'function nfx(n,d){ return Number(n||0).toLocaleString("pt-BR",{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }\nfunction isLG(t){ return String(t).indexOf("PV")===0; }\n'
             + open('talgeo.js', encoding='utf-8').read() + '\n' + open('talmapa.js', encoding='utf-8').read() + "\nconst PARTE='mapa';\n" + U),
}
falhas, tot = 0, 0
for nome, src in FONTES.items():
    fd, p = tempfile.mkstemp(prefix='leve1_' + nome + '_', suffix='.js')
    with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
    try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
    finally: os.unlink(p)
    print(f'--- parte {nome}'); print(r.stdout, end='')
    lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
    if r.returncode or not any(l.startswith('TOTAL ') for l in lin): print('FALHA motor JS da parte', nome, ':', r.stderr[-1500:]); fa += 1
    falhas += fa; tot += n
print(f'RESULTADO {tot - falhas}/{tot}' + (' · FALHOU' if falhas else ''))
sys.exit(1 if falhas else 0)
