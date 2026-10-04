# mutantes da PRE-REV-20261004 na REND (D-01): cópia descartável de 04bf6f2; volta UM defeito e o teste tem de falhar
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes9; rm -rf $M; mkdir -p $M
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37; mkdir -p _probe
export CHROME_BIN=/tmp/cloudchrome/chrome
echo "== sem mutante"; python3 rend_multiconjuntos_unit.py | tail -1 | cut -c1-40
echo "== mutante R1-R3: bloco REPARTIR e espelho anteriores (4c90f31)"
git -C /home/user/sp-camada-sintetica show 4c90f31:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 4c90f31:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 1: bloco REPARTIR e espelho de 6e157c6 (antes do modelo por recurso físico)"
git -C /home/user/sp-camada-sintetica show 6e157c6:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 6e157c6:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 2: bloco REPARTIR e espelho de 1688f97 (com o fecho como restrição)"
git -C /home/user/sp-camada-sintetica show 1688f97:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 1688f97:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 3: bloco REPARTIR e espelho de 1f88bf3"
git -C /home/user/sp-camada-sintetica show 1f88bf3:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 1f88bf3:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 4: bloco REPARTIR e espelho de 9e9cf73 (sem os grupos que se excluem)"
git -C /home/user/sp-camada-sintetica show 9e9cf73:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 9e9cf73:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 5 sem B5a: bloco REPARTIR e espelho de 2eeb2e3"
git -C /home/user/sp-camada-sintetica show 2eeb2e3:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 2eeb2e3:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante rodada 5 com B5a: bloco REPARTIR e espelho de dba9ff0 (sem W1-W4)"
git -C /home/user/sp-camada-sintetica show dba9ff0:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show dba9ff0:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante D-01: bloco REPARTIR e espelho de ee4f954 (sem os cortes por prazo)"
git -C /home/user/sp-camada-sintetica show ee4f954:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show ee4f954:tools/prototipo/v37/gen37/dados2.py > dados2.py
python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-120
git -C /home/user/sp-camada-sintetica archive 04bf6f2 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py | tar -x -C $M
echo "== mutante R5: memória CAL-01 com a área inteira (nf no lugar de nfa)"
python3 - <<'PY'
f='safra.js'; s=open(f,encoding='utf-8').read(); o="'/ha × '+nfa(o.area)+' ha'"; assert s.count(o)==1; open(f,'w',encoding='utf-8').write(s.replace(o,"'/ha × '+nf(o.area)+' ha'"))
PY
python3 build.py >/dev/null 2>&1 && python3 montar_render.py >/dev/null 2>&1 && timeout 900 flock /tmp/cdp9333.lock python3 saf_cmp_continuidade_test.py 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
python3 - <<'PY'
f='safra.js'; s=open(f,encoding='utf-8').read(); o="'/ha × '+nf(o.area)+' ha'"; s=s.replace(o,"'/ha × '+nfa(o.area)+' ha'")
o2="mrow('ma','Área trabalhada (ha)',mat.area,'ha')"; assert s.count(o2)==1; open(f,'w',encoding='utf-8').write(s.replace(o2,"mrow('ma','Área trabalhada (ha)',mat.area)"))
PY
echo "== mutante R7: Por mês com a área inteira"
python3 build.py >/dev/null 2>&1 && python3 montar_render.py >/dev/null 2>&1 && timeout 900 flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py telas 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-120
