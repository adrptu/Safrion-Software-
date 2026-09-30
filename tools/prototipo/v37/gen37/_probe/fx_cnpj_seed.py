# -*- coding: utf-8 -*-
"""Item 6 · CD-05: todos os CPF/CNPJ da demonstração têm dígitos verificadores válidos (validação do próprio formulário) e o PT-07 mostra o mesmo CNPJ da Fertisul."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); b.goto('CD-05.dc.html')
docs = b.J("[...document.querySelectorAll('[role=row]')].map(r=>(r.innerText.match(/\\d{2}\\.\\d{3}\\.\\d{3}\\/\\d{4}-\\d{2}|\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}/)||[''])[0]).filter(Boolean)")
def ok_doc(d):
    d = re.sub(r'\D', '', d)
    if len(d) == 11:
        for n in (9, 10):
            s = sum(int(d[i]) * (n + 1 - i) for i in range(n))
            if (s * 10) % 11 % 10 != int(d[n]): return False
        return True
    w = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in (12, 13):
        s = sum(int(d[i]) * w[i + 13 - n] for i in range(n)); r = s % 11
        if (0 if r < 2 else 11 - r) != int(d[n]): return False
    return True
bad = [d for d in docs if not ok_doc(d)]; print('   documentos:', len(docs), '| inválidos:', bad)
b.ok(len(docs) >= 15 and not bad, 'CD-05: todos os CPF/CNPJ da demonstração com dígito verificador válido', bad)
fe = [d for d in docs if d.startswith('12.345.678')]
b.goto('PT-07.dc.html'); pt = sorted(set(re.findall(r'12\.345\.678/0001-\d{2}', b.body()))); print('   Fertisul CD-05', fe, '· PT-07', pt)
b.ok(fe and pt == fe[:1], 'PT-07 mostra o mesmo CNPJ da Fertisul que o CD-05', (fe, pt))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
