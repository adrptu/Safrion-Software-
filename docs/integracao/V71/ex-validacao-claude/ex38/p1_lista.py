from base import *
s = S()
try:
    s.reset('Ana'); s.go('OS.dc.html', 1.5)
    rows = s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,140))")
    print(len(rows)); print('\n'.join(rows))
    print('TOPO:', s.J("(document.querySelector('header')||document.body).innerText.slice(0,600)"))
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
