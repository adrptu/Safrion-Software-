# Sonda AGUA-SOLO-IRR no Mapa: por setor, o déficit da camada Irrigação (M.irr[t].d), a assinatura da irrAgua visível no IN-04
# e se o balanço com CAD (irrBalDias) está ativo. Saída JSON para comparar antes × depois.
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
try:
    c.aparelho(1440, 900, 1, False); out = {}
    for faz in ('Lagoa Grande', 'Santa Rita'):
        c.goto(f'http://127.0.0.1:{p}/vazio-ensaio.html', .2)
        J("localStorage.clear(); sessionStorage.clear(); sessionStorage.setItem('mapa-ctx'," + json.dumps(json.dumps({'mf_faz': faz, 'lay': 'Irrigação', 'flt': {'Irrigação': {'ver': 'Balanço hídrico'}}})) + "); 1")
        c.call('Page.navigate', {'url': f'http://127.0.0.1:{p}/IN-04x.dc.html'})
        for _ in range(300):
            try:
                if J("!!window.__ex55e&&window.__ex55e('!!MUX.self&&TIDS().length>0')"): break
            except Exception: pass
            time.sleep(.1)
        out[faz] = json.loads(J("window.__ex55e(" + json.dumps(
            "JSON.stringify({assinatura:irrAgua.length, setores:Object.fromEntries(Object.keys(irrGet().setores).map(t=>{const s=irrGet(); const b=irrBalDias(s,t,irrCreditos(s,t)); return [t,{mapa:(M.irr[t]||{}).d===undefined?null:(M.irr[t]||{}).d, cad:b?b.cad:null, comCAD:!!b, def:irrDef(s,t)}];}))})") + ")"))
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    for f, x in out.items(): print(f, 'irrAgua.length', x['assinatura'], '· setores com CAD ativo', sum(1 for v in x['setores'].values() if v['comCAD']), 'de', len(x['setores']))
finally:
    c.close(); srv.terminate()
