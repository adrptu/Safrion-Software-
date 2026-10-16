# Texto integral das telas citadas (perfil Ana; app também com Marcos) + capturas
from base import *
PAGS = ['CA-01det', 'CA-01x-os0420', 'SU-07', 'SU-07det', 'PL-04', 'CARGA', 'CA-04', 'OS-0424-ficha']
s = S()
try:
    s.reset('Ana')
    for p in PAGS:
        s.go(p + '.dc.html', 1.5); t = s.body(); s.save(p + '.txt', t); print(p, len(t))
    s.c.aparelho(390, 1800, 2, True)
    for perfil in ['Ana', 'Marcos']:
        s.reset(perfil)
        for p in ['MB-01', 'MB-02', 'MB-05', 'MB-05det', 'OS-0424-app']:
            s.go(p + '.dc.html', 1.5); t = s.body(); s.save(f'{p}_{perfil}.txt', t); print(p, perfil, len(t))
        for o in ['OS-0421', 'OS-0424', 'OS-0420', 'OS-0417', 'OS-0504', 'OS-0425', 'OS-0506', 'OS-0507', 'OS-0505']:
            s.J(f"localStorage.setItem('talhao-os-mb-os',{json.dumps(o)}); 1"); s.go('MB-02det.dc.html', 1.5); t = s.body(); s.save(f'MB-02det_{o}_{perfil}.txt', t); print('MB-02det', o, perfil, len(t))
            if perfil == 'Marcos' and o in ('OS-0421', 'OS-0424'): s.shot(f'MB-02det_{o}.png')
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
