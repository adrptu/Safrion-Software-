# mutantes da rodada 6 da SINT (U1-U5): cópia descartável de 2ce5a43; cada um volta UMA correção e o quantidade_test.py tem de falhar
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes8; rm -rf $M; mkdir -p $M
git -C /home/user/sp-fix archive 2ce5a43 tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37; mkdir -p _probe
mut(){ nome=$1; arq=$2; old=$3; new=$4; cp $arq /tmp/.mut8.bak
  python3 - "$arq" "$old" "$new" <<'PY'
import sys; f,o,n=sys.argv[1:]; s=open(f,encoding='utf-8').read()
if s.count(o)<1: print('MUTANTE NÃO APLICADO',f,repr(o[:60])); sys.exit(3)
open(f,'w',encoding='utf-8').write(s.replace(o,n))
PY
  if [ $? -ne 0 ]; then echo "== mutante $nome: NÃO APLICADO (falha do roteiro)"; cp /tmp/.mut8.bak $arq; return; fi
  echo "== mutante $nome ($arq)"; python3 quantidade_test.py > /tmp/.mut8.out 2>&1; ec=$?; grep -E "^(FALHOU|RESULTADO)" /tmp/.mut8.out | cut -c1-140; echo "[exit $ec]"; cp /tmp/.mut8.bak $arq; }
echo "== sem mutante"; python3 quantidade_test.py | tail -1
mut U1-filtro-volume irrigacao_estado.js '&& (a.vol > 0 || irrApParc(a, x.ha)));' '&& a.vol > 0);'
mut U2-sem-recusa irrigacao_estado.js "  if (p && irrPassProx(o)) return 'A passada '" "  if (false && p && irrPassProx(o)) return 'A passada '"
mut U3-mip-sem-finito mip.js "if (c && c.lotes && dose > 0 && area > 0 && isFinite(dose) && isFinite(area))" "if (c && c.lotes && dose > 0 && area > 0)"
mut U3-ajuste-sem-finito areas/processo_os.py "if(!isFinite(d)||!isFinite(ar)) return 'Dose ou área inválida: informe um número.';" ""
mut U4-casas areas/irrigacao.py "{l:'Área coberta',t:irrN(cob,2,1)+' de '+irrN(x.ha,2,0)+' ha'}" "{l:'Área coberta',t:irrN(cob,1)+' de '+irrN(x.ha,1)+' ha'}"
mut U5-dose-1-casa irrigacao_estado.js "irrN(d.dose, 3, 1) + ' kg/ha" "irrN(d.dose, 1) + ' kg/ha"
