# Capturas complementares: O.S. completa (CA-01det, CA-01x-os0420), SU-07, CD-04, ficha do app e impressa da OS-0424, MB-05
from base import *
s = S(1440, 2000)
try:
    s.reset('Ana')
    for p in ['CA-01det', 'CA-01x-os0420', 'SU-07', 'CD-04', 'PL-04', 'OS-0424-ficha']:
        s.go(p + '.dc.html', 1.5); s.shot(p + '.png')
    s.c.aparelho(390, 1400, 2, True); s.reset('Ana')
    for p in ['OS-0424-app', 'MB-05', 'MB-01']:
        s.go(p + '.dc.html', 1.5); s.shot(p + '.png')
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
