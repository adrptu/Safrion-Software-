# -*- coding: utf-8 -*-
"""rev95 · reteste dos achados A1–A4 do PR #95 no AG-02 real (navegador), a 1440 e a 390 com toque. Dados sintéticos.
R1 qualificador: só "Valor medido" e "<"; K "< 1" registrado pela tela e validado → soloKmg "K abaixo do limite de detecção" e nenhuma sugestão de K no T1.
R2 extrator: exemplo carregado + P digitado + extrator trocado para Resina → P e K mostrados só leitura com Resina e gravados como Resina;
   o método do MO continua editável e é gravado.
R3 detalhe sem valor: Al com LD 0,1 e "<" e valor vazio → recusado no painel, nada gravado, escolhas e detalhes abertos mantidos.
R4 os 15 summaries "Método e limites" com altura ≥ 24 px a 1440 e ≥ 44 px a 390.
Contraprova: o mesmo roteiro no render com o AG-02 de a10656a (qualificador em texto livre: digita "abaixo do limite", como a dica antiga).
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B rev95_reteste.py <RENDER_DIR> [1440,390]"""
import os, sys, json, time
GEN = os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
import subprocess, tempfile
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
import cenario, dados_solo
_PREF = 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + cenario.js_prefixo() + dados_solo.js_prefixo()
def dominio_T1(cen_json, lid):
    """o script da página roda em escopo próprio (text/x-dc): o estado gravado (__solo.cen()) é conferido no node com o mesmo solo.js e SOLO0 do build"""
    js = _PREF + 'const c=' + cen_json + ';' + r"""
const ls=soloLaudos(c,SOLO0); const l=ls.find(x=>x.id==='""" + lid + r"""'); const cu=SOLO0.cult.find(x=>x.faz==='Santa Rita'&&x.tal==='T1');
const s=soloSugestoes(soloCtxBase(c,SOLO0), soloCultivoBase(SOLO0,cu)); const K=soloAn(l,'K');
console.log(JSON.stringify({sit:l.sit, kmg:soloKmg(K), kSug:s.sug.filter(x=>x.regra==='potássio').map(x=>x.prod+' '+x.padrao+'→'+x.sug), info:s.info.filter(t=>/K /.test(t))}));"""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); fn = f.name
    r = subprocess.run(['node', fn], capture_output=True, text=True); os.unlink(fn)
    try: return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: return {'erro': (r.stderr or r.stdout)[-400:]}
R = os.path.abspath(sys.argv[1]); LARGS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1440,390').split(',')]
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.DLG=()=>[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop()||null;
window.SETV=(el,val)=>{ if(!el) throw new Error('campo ausente'); const P=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(el,val);
  el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return el.value; };
window.Q=(lab)=>{ const d=DLG(); return d?d.querySelector('[aria-label="'+lab+'"]'):null; };
window.BTN=(t,root)=>[...(root||document).querySelectorAll('button,summary,a')].filter(VIS).find(b=>N(b.innerText)===t)||null;
window.SUM=(a)=>[...DLG().querySelectorAll('summary')].find(x=>N(x.innerText)==='Método e limites · '+a);
window.ABRE=(a)=>{ const s=SUM(a); if(!s.parentElement.open) s.click(); return s.parentElement.open; };
window.QUALI=(a,modo)=>{ const e=Q('Qualificador de '+a); if(e.tagName==='SELECT') return SETV(e,'<'); return SETV(e, modo); };   /* a10656a: texto livre como a dica antiga */
window.NOVO=()=>{ const d=DLG(); if(d){ const f=BTN('Fechar',d)||BTN('Cancelar',d); if(f) f.click(); } const b=[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Registrar laudo'); b.click(); };
window.REG=()=>[...DLG().querySelectorAll('.so-pe button')].filter(VIS).find(b=>N(b.innerText)==='Registrar laudo').click();
window.LAUS=()=>__solo.get().laudos||{};
window.ULT=()=>{ const L=LAUS(); const ks=Object.keys(L); return ks.length?L[ks[ks.length-1]]:null; };
'ok'"""
p, srv = servir(R); c = Chrome(); J = c.js
def form(tal, lab, vals, ext=None):
    J("NOVO()"); time.sleep(.45); J("SETV(DLG().querySelector('#rl_tal'),%s)" % json.dumps(tal)); time.sleep(.15)
    J("BTN('Ontem',DLG()).click()"); time.sleep(.15); J("SETV(DLG().querySelector('#rl_lab'),%s)" % json.dumps(lab)); time.sleep(.15)
    if ext: J("BTN(%s,DLG()).click()" % json.dumps(ext)); time.sleep(.15)
    for a, v in vals: J("SETV(Q('Valor de %s'),%s)" % (a, json.dumps(v))); time.sleep(.05)
try:
    for W in LARGS:
        toque = W < 800; tag = f'[{W}]'
        c.aparelho(W, 844 if toque else 1000, toque=toque)
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','\"Ana\"')")
        c.goto(f'http://127.0.0.1:{p}/AG-02.dc.html'); J(LIB)
        # ---- R1 qualificador
        form('T1', 'Agrolab', [('Ca', '3,10'), ('Mg', '1,25'), ('K', '1'), ('H+Al', '3,00'), ('Al', '0')])
        J("ABRE('K')"); time.sleep(.15)
        op = J("(()=>{ const e=Q('Qualificador de K'); return e.tagName==='SELECT'?[...e.options].map(o=>[o.value,N(o.text)]):e.tagName; })()")
        J("SETV(Q('Limite de detecção de K'),'1')"); time.sleep(.1); J("QUALI('K','abaixo do limite')"); time.sleep(.15)
        n0 = J("Object.keys(LAUS()).length"); J("REG()"); time.sleep(.6)
        l1 = J("ULT()") or {}; k1 = next((x for x in l1.get('an', []) if x['a'] == 'K'), None)
        chk(f'{tag} R1 qualificador só com "Valor medido" e "<"', op == [['', 'Valor medido'], ['<', 'Abaixo do limite de detecção (<)']], op)
        val = J("(()=>{ const r=__solo.validar(%s,'R95-RV-%d','Ana'); return r.erro||r.msg; })()" % (json.dumps(l1.get('id', '')), W)); time.sleep(.3)
        r1 = dominio_T1(J("JSON.stringify(__solo.cen())"), l1.get('id', ''))
        chk(f'{tag} R1 K "< 1" registrado pela tela grava q "<" e LD "1"; validado, soloKmg "K abaixo do limite de detecção" e nenhuma sugestão de K no T1',
            l1.get('tal') == 'T1' and J("Object.keys(LAUS()).length") == n0 + 1 and k1 and k1.get('q') == '<' and k1.get('ld') == '1' and r1 and r1.get('sit') == 'Validado'
            and (r1.get('kmg') or {}).get('v') is None and (r1.get('kmg') or {}).get('nc') == 'K abaixo do limite de detecção' and not r1.get('kSug') and any('nada sugerido' in t for t in r1.get('info', [])), [k1, val, r1])
        ext_ = J("(()=>{ const d=DLG(); return d?N(d.innerText):''; })()") or ''
        chk(f'{tag} R1 o Extraído do laudo mostra o qualificador ("< 1") para quem valida', ' < 1 ' in (' ' + ext_ + ' '), ext_[ext_.find('K '):ext_.find('K ') + 120] if 'K ' in ext_ else ext_[:200])
        # ---- R2 extrator
        J("NOVO()"); time.sleep(.45); J("BTN('Preencher com o laudo de exemplo',DLG()).click()"); time.sleep(.3)
        J("SETV(Q('Valor de P'),'14')"); J("SETV(Q('Valor de MO'),'28')"); time.sleep(.1); J("ABRE('P'); ABRE('K'); ABRE('MO')"); time.sleep(.15)
        J("SETV(Q('Método de MO'),'Walkley-Black')"); time.sleep(.1)
        J("BTN('Resina',DLG()).click()"); time.sleep(.3)
        mt = J("['P','K','MO'].map(a=>{ const e=Q('Método de '+a); return [a, e.value, e.readOnly, N(e.closest('label').innerText)]; })")
        chk(f'{tag} R2 depois de trocar o extrator: P e K mostram "Resina" só leitura ("Extrator do laudo"); o método do MO segue editável',
            mt and mt[0][1:3] == ['Resina', True] and mt[1][1:3] == ['Resina', True] and mt[2][1:3] == ['Walkley-Black', False] and mt[0][3] == 'Extrator do laudo', mt)
        n1 = J("Object.keys(LAUS()).length"); J("REG()"); time.sleep(.6); l2 = J("ULT()") or {}
        g2 = {x['a']: x for x in l2.get('an', [])}
        chk(f'{tag} R2 exemplo + Resina: laudo T7 com ext Resina, P e K gravados com met Resina, MO com Walkley-Black',
            J("Object.keys(LAUS()).length") == n1 + 1 and l2.get('tal') == 'T7' and l2.get('ext') == 'Resina' and g2.get('P', {}).get('met') == 'Resina'
            and g2.get('K', {}).get('met') == 'Resina' and g2.get('MO', {}).get('met') == 'Walkley-Black', [l2.get('id'), l2.get('ext'), g2.get('P'), g2.get('K'), g2.get('MO')])
        # ---- R3 detalhe sem valor
        form('T3', 'Agrolab', [('K', '40')]); J("ABRE('Al')"); time.sleep(.15)
        J("SETV(Q('Limite de detecção de Al'),'0,1')"); time.sleep(.1); J("QUALI('Al','<')"); time.sleep(.15)
        n2 = J("Object.keys(LAUS()).length"); J("REG()"); time.sleep(.5)
        r3 = J("(()=>{ const d=DLG(); const V=l=>{ const e=Q(l); return e?e.value:null; }; const s=d&&SUM('Al'); const u=ULT();"
               " return {h:d?N(d.querySelector('h2').innerText):null, al:d?[...d.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | '):'',"
               " ld:V('Limite de detecção de Al'), q:V('Qualificador de Al'), aberto:s?s.parentElement.open:null, k:V('Valor de K'), alv:V('Valor de Al'), n:Object.keys(LAUS()).length,"
               " ult:u?[u.id,u.tal,u.an.map(x=>x.a).join(',')]:null}; })()")
        chk(f'{tag} R3 Al só com LD 0,1 e "<": recusado no painel ("Al: informe o valor…"), nada gravado; LD, "<", detalhes abertos e K 40 mantidos',
            r3 and r3['h'] == 'Registrar laudo de solo' and 'Al: informe o valor do laudo' in r3['al'] and r3['n'] == n2 and r3['ld'] == '0,1' and r3['q'] == '<' and r3['aberto'] is True and r3['k'] == '40' and r3['alv'] == '', r3)
        # ---- R4 alvo do summary
        geo = J("(()=>{ const ss=[...DLG().querySelectorAll('summary')].filter(VIS); const h=ss.map(s=>Math.round(s.getBoundingClientRect().height*10)/10); return {n:ss.length,min:Math.min(...h),max:Math.max(...h),lado:DLG().scrollWidth<=DLG().clientWidth+1}; })()")
        alvo = 44 if toque else 24
        chk(f'{tag} R4 os 15 summaries "Método e limites" com altura ≥ {alvo} px; sem estouro lateral', geo and geo['n'] == 15 and geo['min'] >= alvo and geo['lado'], geo)
        c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'rev95_reteste_{W}_{os.path.basename(R)}.png'))
        er = J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0).join(' | ')") or ''
        chk(f'{tag} nenhum erro de JS', not er, er)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {"OK" if not FAIL else "FALHA"} {len(OK)}/{len(OK) + len(FAIL)}' + ('' if not FAIL else ' · falhas: ' + ' || '.join(FAIL)))
sys.exit(1 if FAIL else 0)
