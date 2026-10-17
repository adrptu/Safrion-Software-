# -*- coding: utf-8 -*-
"""Confere que o JS do mapa no IN-04 publicado é a fonte de b989864 e traduz as linhas citadas pelo anexo.
Uso: python3 -I -B fonte_publicado.py <IN-04.dc.html publicado> <gen37> [auto]
Sem "auto": faixa fixa 7212-8239 e linhas do anexo (espelho 1792184197-5a81, saída em fonte_publicado.txt, gerada antes da troca do espelho).
Com "auto": a faixa vai de "const IDXN=M.idxn;" ao fim de colhAc, sem a linha de dados "const M = …" (saída em fonte_publicado_05947ad.txt)."""
import sys, glob
pub = open(sys.argv[1], encoding='utf-8').read().split('\n'); G = sys.argv[2]
idx = {}
for s in sorted(glob.glob(G + '/*.js') + glob.glob(G + '/*.py') + glob.glob(G + '/areas/*.py')):
    for j, l in enumerate(open(s, encoding='utf-8').read().split('\n'), 1):
        k = l.strip()
        if len(k) > 25: idx.setdefault(k, (s.split('gen37/')[-1], j))
a, b = 7212, 8240
if len(sys.argv) > 3 and sys.argv[3] == 'auto':
    a = next(i for i, l in enumerate(pub, 1) if l.strip() == 'const IDXN=M.idxn;'); b = next(i for i, l in enumerate(pub, 1) if l.strip().startswith('function colhAc(t)')) + 3
    off = a - next(j for j, l in enumerate(open(G + '/areas/inicio.py', encoding='utf-8').read().split('\n'), 1) if l.strip() == 'const IDXN=M.idxn;')
    print(f'faixa automática {a}-{b - 1}; deslocamento publicado − inicio.py no início da faixa: {off}')
sem = [i for i in range(a, b) if len(pub[i - 1].strip()) > 25 and pub[i - 1].strip() not in idx and not pub[i - 1].strip().startswith('const M = ')]
print(f'linhas de JS do mapa no publicado ({a}-{b - 1}) sem par literal na fonte: {len(sem)} de {b - a}')
cit = "1231 1282 1413 7257 7260 7264 7266 7275 7296 7300 7301 7304 7307 7311 7314 7315 7320 7321 7323 7326 7327 7328 7329 7331 7334 7338 7340 7341 7409 7440 7453 7480 7485 7521 7549 7551 7557 7559 7560 7561 7565 7581 7606 7637 7680 7682 7702 7706 7711 7746 7769 7775 7780 7787 7788 7792 7797 7801 7803 7805 7806 7815 7821 7822 7823 7830 7832 7833 7835 7836 7837 7838 7842 7843 7845 7852 7854 7856 7857 7860 7862 7872 7876 7879 7882 7884 7886 7890 7942 7951 7991 8011 8015 8048 8057 8085 8231 8240 8337 8339 8342 8532"
if len(sys.argv) > 3 and sys.argv[3] == 'auto': sys.exit(0)
print('linha publicada -> fonte')
for n in map(int, cit.split()):
    f = idx.get(pub[n - 1].strip()); print(n, '->', f'{f[0]}:{f[1]}' if f else '? (linha de template ou fora do JS)')
