"""EST-1: memória do disponível coerente com vencimento e saldo por lote."""
from est_lib import Est
E=Est(copiar=False)
try:
 for w in [1440,390]:
  E.c.size(w,900 if w==1440 else 844);E.abrir();E.J('localStorage.clear();sessionStorage.clear()');E.abrir()
  E.mudar("""c.lotes['Memória sintética|V']={prod:'Memória sintética',lote:'V',un:'L',local:'Almox. Santa Rita',validade:'01/2000',fisico:100,reservado:0,quarentena:0};
  c.lotes['Memória sintética|A']={prod:'Memória sintética',lote:'A',un:'L',local:'Almox. Santa Rita',validade:'12/2099',fisico:40,reservado:10,quarentena:5};
  c.lotes['Memória sintética|R']={prod:'Memória sintética',lote:'R',un:'L',local:'Almox. Santa Rita',validade:'—',fisico:10,reservado:20,quarentena:0};""")
  before=E.cen('JSON.stringify(c.lotes)');E.abrir()
  if w<900:E.J("document.querySelector('label[for=etp-c1].etp-atual').click()")
  E.clk('Confira saldos');E.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.includes('Memória sintética'));if(!r)throw Error('linha ausente');r.querySelectorAll('[role=cell]')[4].click();})()");__import__('time').sleep(.4);t=E.aside();print('MEMORIA',w,t)
  E.ok('25 L' in t and '150 L − 30 L − 5 L = 25 L' not in t,str(w)+': não mostra igualdade falsa de totais',t)
  E.ok('não vencidos' in t and 'mínimo de zero' in t,str(w)+': explica exclusão por validade e saldo não negativo por lote',t)
  E.ok(E.cen('JSON.stringify(c.lotes)')==before,str(w)+': consulta preserva lotes/reservas/quarentena')
  E.ok(not E.erros(),str(w)+': sem erro de execução',E.erros())
finally:ok=E.fim()
raise SystemExit(0 if ok else 1)
