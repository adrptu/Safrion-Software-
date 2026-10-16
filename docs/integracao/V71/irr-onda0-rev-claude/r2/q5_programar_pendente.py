# Q5 (revisor): com a OS-0419 em conferência "área e tempo" (80 ha / 8.480 m³ informados, sem crédito), o IR-02 deixa programar
# outra ordem para o Pivô 2? Mostra algum aviso da água informada e não validada? Uso: python3 q5_programar_pendente.py <gen37>
import sys, os, time, json
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
DLG = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getBoundingClientRect().width>1)"
def clk(t, dlg=False):
    r = J(f"(()=>{{const R={'('+DLG+')' if dlg else 'document'}; const b=[...R.querySelectorAll('button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(t)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.9); return r
def setv(fid, val):
    return J(f"""(()=>{{const e=({DLG}).querySelector('#{fid}'); if(!e) return false; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()""")
def toast(): time.sleep(.3); return J("((document.querySelector('.g2toast')||{}).innerText||'').trim()")
def dtxt(): return J(f"(()=>{{const d={DLG}; return d?d.innerText.replace(/\\s+/g,' '):null;}})()")
def S(): return json.loads(J("localStorage.getItem('talhao-os-irrigacao-v1')") or 'null')
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear();1")
    c.goto(U('IR-03det.dc.html#OS-0419'), 1.6); clk('Iniciar irrigação')
    for t in ('Registrar término antecipado', 'Confirmar término'):
        if clk(t): break
    time.sleep(.4); setv('tm_cob', '80'); setv('tm_vol', '8480'); time.sleep(.3); setv('tm_mot', 'Volta informada (sintético)')
    clk((dtxt() or '').split(' · ')[0] if dtxt() and dtxt().startswith('Registrar') else 'Confirmar término', True); t1 = toast()
    s = S(); o = s['ordens']['OS-0419']
    print('1 término:', t1[:160], '· etapa', o['etapa'], '· conf', (o.get('conf') or {}).get('st'), '· crédito', [a for a in s['setores']['P2']['bal']['ap'] if a['os'] == 'OS-0419'])
    c.goto(U('Main.dc.html'), .2); c.goto(U('IR-01.dc.html'), 2.0)
    r = J("[...document.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ')).find(t=>/Pivô 2 /.test(t))||''"); print('2 IR-01 Pivô 2:', r)
    c.goto(U('Main.dc.html'), .2); c.goto(U('IR-02.dc.html#programar=P2'), 2.0); d = dtxt() or ''
    print('3 IR-02 painel P2:', d[d.find('DÉFICIT'):][:600])
    prog = J(f"(()=>{{const b=[...({DLG}).querySelectorAll('button')].find(b=>/^Programar/.test(b.innerText.trim())); return b?b.innerText.trim():null;}})()")
    if prog:
        clk(prog, True); t3 = toast(); s = S()
        novas = [k for k, z in s['ordens'].items() if z['setor'] == 'P2' and z['etapa'] not in ('Encerradas', 'Canceladas')]
        print('4 programou:', t3[:200], '· ordens abertas do P2:', novas)
    print('RESULTADO Q5:', 'programar oferecido' if prog else 'programar não oferecido', '· aviso de água não validada:', ('não validad' in d.lower() or 'a conferir' in d.lower()))
finally:
    c.close(); srv.terminate()
