# -*- coding: utf-8 -*-
"""CONF-01 · defeitos da base 99537ca que o módulo corrige, cada um com o teste que falha na base e passa depois (proteção de regressão).
Sem navegador. Uso (de gen37/): python3 config_regressao_test.py                 (gerador desta cópia; sai 1 se algum caso falhar)
Reprodução na base: GEN=<gen37 extraído de 99537ca> python3 config_regressao_test.py   (esperado: os casos R1..R6 FALHAM)
R1 · 2ª dispensa sobrescrevia quem dispensou (osc_txt: dispPor) e a trilha perdia a 1ª decisão (RV-03).
R2 · pedir recontagem recusava o ajuste sem gravar quem pediu (estRecontar sem ator; CONF-D17).
R3 · "vale este" fechava o caso de consumo com autor e sem marca: a trilha contaria um CMD-50 que ninguém deu (RV-03).
R4 · aceite do consumo sem hora da decisão (a trilha só tinha a hora do relato).
R5 · Caio decidia pelo perfil (G2_PERFIS) sem estar no CD-04: segundo cadastro de pessoas (CONF-D04).
R6 · CF-02 dizia "Liberador do domínio · Caio (PCP)" e o comando liberava com o gestor (CONF-D10): texto paralelo ao comando."""
import os, sys, re, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.abspath(os.environ.get('GEN', HERE))
sys.path.insert(0, G); os.chdir(G)
import cenario
import areas.processo_os as P
from areas import processo_estoque as PE
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
pre = ''
for mod in ('dados_assinatura', 'dados_config'):   # prefixos de toda tela, quando existem nesta cópia
    if os.path.exists(os.path.join(G, mod + '.py')): pre += __import__(mod).js_prefixo()
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\nvar GRIDS=[];\n' + PE.JS
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
JS = r'''
let nfal = 0; function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfal++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 300))); } }
const caso = (t, f) => { try { f(); } catch (e) { ok(t + ' (erro: ' + String(e.message || e) + ')', false); } };
const M = f => cenMudar(null, f); const G = () => cenGet();
caso('R1', () => { cenReset(); M(c => osc_dispensar(c, 'OS-0421', 10, 'chuva', 'Ana')); M(c => osc_dispensar(c, 'OS-0421', 5, 'máquina', 'Ana'));
  const d = (G().ordens['OS-0421'].osc || {}).disps || [];
  ok('R1 duas dispensas na mesma O.S. ficam registradas, cada uma com quem decidiu (10 ha e 5 ha)', d.length === 2 && d[0].ha === 10 && d[1].ha === 5 && d.every(x => x.por === 'Ana (gestora e agrônoma)'), d); });
caso('R2', () => { cenReset(); M(c => estContar(c, 'INV-2611', 'Glifosato 480|G26-14', 1180, 'Paula (almoxarife)', 'bombona avariada', 'Rui'));
  M(c => estRecontar(c, 'INV-2611', 'Rui')); const aj = (G().ajustes || [])[0] || {};
  ok('R2 pedir recontagem grava quem recusou o ajuste (Rui (almoxarife)) e a hora', aj.estado === 'Recusado' && aj.por === 'Rui (almoxarife)' && /^\d\d:\d\d$/.test(aj.em || ''), aj); });
caso('R3', () => { cenReset(); M(c => { osc_apontar(c, 'OS-0421', '26/09', 50, { 'Fungicida A': 80, 'Adjuvante espalhante': 0 }, [], 'W-1'); cenIniciarTurno(c, 'OS-0421'); return cenFecharTurno(c, 50, 8, { 'Fungicida A': 25 }, '', []); });
  M(c => cenApDecidir(c, 'OS-0421', 6, 'este', 'Paula')); const k = (G().confs || []).find(x => x.estado === 'Recusado') || {};
  ok('R3 caso de consumo fechado pela decisão de duplicidade leva via CMD-09 (não é um CMD-50)', k.via === 'CMD-09' && k.por === 'Paula (conferência)', k); });
caso('R4', () => { cenReset(); M(c => osc_apontar(c, 'OS-0421', '26/09', 50, { 'Fungicida A': 80, 'Adjuvante espalhante': 0 }, [], 'W-cc')); const id = G().confs[0].id;
  M(c => cenConciliar(c, id, true, undefined, 'Ana')); const k = G().confs[0];
  ok('R4 aceite do consumo grava a hora da decisão (em)', k.estado === 'Aceito' && /^\d\d:\d\d$/.test(k.em || ''), k); });
console.log('TOTAL JS · falhas ' + nfal);
'''
src = 'globalThis.print=(...a)=>console.log(...a);\n' + LS + open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read() + '\n' + pre + EST + '\n' + OS + '\n' + JS
fd, p = tempfile.mkstemp(prefix='confreg_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
finally: os.unlink(p)
print(r.stdout, end='')
if r.returncode: print('FALHA motor JS:', r.stderr[-1500:])
lin = r.stdout.splitlines(); res = [l.startswith('OK') for l in lin if l.startswith(('OK ', 'FALHA '))]
def chk(t, c, got=''):
    res.append(bool(c)); print(('OK    ' if c else 'FALHA ') + t + ('' if c else ' · ' + str(got)[:300]))
import dados_cad as DC
import areas.cad_ativos_pessoas as CAP
nomes = [v['nome'] for _pid, v in CAP.pessoas()]
g2 = open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read()
perfis = re.findall(r"\{k:'([^']+)',t:", g2[g2.index('const G2_PERFIS='):g2.index('];', g2.index('const G2_PERFIS='))])
chk('R5 todo perfil que decide (G2_PERFIS) é uma pessoa do CD-04 (Caio incluído)', all(k in nomes for k in perfis), [k for k in perfis if k not in nomes])
cfg = open(os.path.join(G, 'areas', 'configuracoes.py'), encoding='utf-8').read()
osp = open(os.path.join(G, 'areas', 'processo_os.py'), encoding='utf-8').read()
lib = 'gestor' if (re.search(r"const OS_LIB='gestor'", osp) or re.search(r"id:'AL-01'[^}]*papeis:\['gestor'\]", g2)) else '?'
chk('R6 a tela de alçadas não afirma um liberador diferente do que o comando usa (AL-01 = ' + lib + ')', 'Liberador do domínio · Caio (PCP)' not in cfg and lib == 'gestor', 'CF-02 diz "Caio (PCP)"; o comando usa ' + lib)
n = len(res); fa = res.count(False)
print(f'RESULTADO {n - fa}/{n}')
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
