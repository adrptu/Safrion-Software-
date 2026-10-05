# mutantes da rodada 3 do D-01 (REND): cópia descartável de dbe8f0c; volta UM defeito e o oráculo tem de falhar
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes11; rm -rf $M; mkdir -p $M
git -C /home/user/sp-camada-sintetica archive dbe8f0c tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37; mkdir -p _probe
volta(){ git -C /home/user/sp-camada-sintetica archive dbe8f0c tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M; }
muta(){ python3 - "$1" "$2" "$3" <<'PY'
import sys; f,a,b=sys.argv[1:4]; s=open(f,encoding='utf-8').read(); assert s.count(a)==1,(f,a[:70],s.count(a)); open(f,'w',encoding='utf-8').write(s.replace(a,b))
PY
}
ora(){ python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-110; }
echo "== sem mutante"; ora | tail -1
echo "== mutante rodada 2 inteira: bloco e espelho de 2e31588"
git -C /home/user/sp-camada-sintetica show 2e31588:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 2e31588:tools/prototipo/v37/gen37/dados2.py > dados2.py; ora; volta
echo "== mutante R3-1: sem o conservador de prazos diferentes com P4 (JS)"
muta safra.js "if(!cliq&&dl.length>1&&p4()){" "if(false&&!cliq&&dl.length>1&&p4()){"; ora; volta
echo "== mutante R3-1b: conservador sem exigir P4 (JS, amplo demais)"
muta safra.js "if(!cliq&&dl.length>1&&p4()){" "if(!cliq&&dl.length>1){"; ora; volta
echo "== mutante R3-2: sem os cortes de fato no plano (JS)"
muta safra.js "if(m>1) bk([],ns.map((_,k)=>k),[]);" "if(false) bk([],ns.map((_,k)=>k),[]);"; ora; volta
echo "== mutante R3-4a: par que passa do grupo deixa de ser fato (JS)"
muta safra.js "return a>0&&b>0&&a+b>z[2]+1e-9;" "return false;"; ora; volta
echo "== mutante R3-4b: leitura de número antiga (JS)"
muta safra.js "if(!/^[+-]?(\\d+(\\.\\d*)?|\\.\\d+)([eE][+-]?\\d+)?\$/.test(t)) return NaN;" ""; ora; volta
echo "== mutante R3-4c: conflito sem o motivo de fato quando há estimativa maior (JS)"
muta safra.js "if(c.f) ms.push([c.f,false]);" ""; ora; volta
echo "== fim"
