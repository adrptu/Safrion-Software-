# complemento da 09-mutantes (SINT, 3ba5f14): Y1 com a assinatura da rodada 5 (o roteiro anterior mirava a linha antiga e não aplicou)
# e Q2 com a saída inteira e o código de saída (a 09 filtrava só FALHOU/RESULTADO e o teste quebrou sem imprimir)
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes5b; rm -rf $M; mkdir -p $M
git -C /home/user/sp-fix archive 3ba5f14 tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37; mkdir -p _probe
mut(){ nome=$1; arq=$2; old=$3; new=$4; teste=$5; cp $arq /tmp/.mut.bak
  python3 - "$arq" "$old" "$new" <<'PY'
import sys; f,o,n=sys.argv[1:]; s=open(f,encoding='utf-8').read()
if s.count(o)!=1: print('MUTANTE NÃO APLICADO',f,repr(o[:60])); sys.exit(3)
open(f,'w',encoding='utf-8').write(s.replace(o,n))
PY
  if [ $? -ne 0 ]; then echo "== mutante $nome: NÃO APLICADO (falha do roteiro)"; cp /tmp/.mut.bak $arq; return; fi
  echo "== mutante $nome ($arq)"; python3 $teste > /tmp/.mut.out 2>&1; ec=$?; grep -E "^(FALHOU|RESULTADO)" /tmp/.mut.out | cut -c1-160; echo "[exit $ec]"; [ $ec -ne 0 ] && tail -4 /tmp/.mut.out | cut -c1-200; cp /tmp/.mut.bak $arq; }
echo "== sem mutante"; python3 quantidade_test.py | tail -1
mut Q2-sem-exponencial cenario.js '(?:e([+-]\d+))?$/.exec' '$/.exec' quantidade_test.py
mut Y1-v2-zero irrigacao_estado.js '  { const m = irrV2Zero(o, x, p, d.dose); if (m) throw new Error(m); }' '  ' quantidade_test.py
