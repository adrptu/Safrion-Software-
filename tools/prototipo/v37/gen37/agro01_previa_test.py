"""AGRO-01/OS-05: renderiza expressões reais das duas ações com dados sintéticos.
python3 agro01_previa_test.py [diretório com base-planejamento.py/base-campo.py]
Sem DOM/E2E; prévia é um snapshot da lista, não prontidão calculada pelo motor.
"""
import ast
import copy
import html
from pathlib import Path
import sys
root = Path(__file__).resolve().parent
env = dict(esc=html.escape, BTN_ST=lambda *a: "", OS_DES={"id":"OS-0430"},
           OS_DEMO17={"id":"OS-0431"},
           msgbtn=lambda label,msg,**kw: msg, imsg=lambda label,msg,*a,**kw: msg)
env["ords"] = [
    dict(v=dict(os="OS-TESTE",etp="A liberar"),p=dict(sel=[dict(t="Falta <insumo>")])),
    dict(v=dict(os="OS-IGNORADA",etp="Encerradas"),p={})]
env["ordens"] = [dict(id="OS-TESTE",etapa="A liberar"),dict(id="OS-IGNORADA",etapa="Encerradas")]
env["_selos"] = lambda o: [("Falta <insumo>", "red")]
before = copy.deepcopy((env["ords"],env["ordens"]))
for name,label in [("planejamento","Liberar prontas"),("campo","Liberar selecionadas")]:
    path = Path(sys.argv[1])/("base-"+name+".py") if len(sys.argv)>1 else root/"areas"/(name+".py")
    tree=ast.parse(path.read_text())
    # Locate exactly the old action or the replacement expression, not unrelated controls.
    old=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and n.args
         and isinstance(n.args[0],ast.Constant) and n.args[0].value==label]
    candidates=[n for n in ast.walk(tree) if isinstance(n,ast.BinOp)
                and "Conferir caminho de liberação" in ast.unparse(n)
                and isinstance(n.right,ast.Constant) and isinstance(n.right.value,str)
                and n.right.value.endswith("</details>")]
    node=old[0] if old else max(candidates,key=lambda n:len(ast.unparse(n)))
    result=eval(compile(ast.Expression(node),str(path),"eval"),env)
    assert "OS-TESTE" in result, "Prévia deve derivar da lista; não resultado fixo"
    assert "OS-IGNORADA" not in result
    assert "Falta &lt;insumo&gt;" in result
    assert 'href="OS.dc.html#OS-TESTE"' in result
    assert "Abrir O.S. ›" in result
    assert "onClick" not in result and "onclick" not in result
    assert "liberada por Ana" not in result and "Resultado por item" not in result
    assert "sem executar liberação" in result
    assert (env["ords"],env["ordens"]) == before
    # Empty queue cannot invent a result or an O.S.
    saved=env["ords"],env["ordens"]
    env["ords"],env["ordens"]=[],[]
    empty=eval(compile(ast.Expression(node),str(path),"eval"),env)
    assert 'href="OS.dc.html#' not in empty
    env["ords"],env["ordens"]=saved
    print("PASS",name,": prévia por linha, escape, destino, ausência de comando e fila vazia")
