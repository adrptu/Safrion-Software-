#!/bin/bash
# Contraprova do M1 (paridade O.S. × IN-04): duas mutações na regra, só na página da O.S.; o M1 tem de reprovar nas duas.
# Uso: SAIDA=<pasta de trabalho> GEN=<tools/prototipo/v37/gen37> PACOTE=<A2_IN04_pacote.json> bash contraprova_m1.sh
SP=${SAIDA:?defina SAIDA}; G=${GEN:?defina GEN}
E="env CHROME_BIN=${CHROME_BIN:-chromium} CDP_GL=1 SAFRION_DADOS=sintetico"
mkdir -p "$SP/ex55f1/r2"
for m in classe rotulo; do
  D=$SP/ex55f1/mut_$m; [ -e "$D" ] && { echo "pasta $D já existe: use uma SAIDA vazia"; exit 2; }; cp -r $G/_render "$D"
  python3 - "$D/OS.dc.html" "$m" <<'PY'
import sys
p, m = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
a, b = ("return {c:mc_FASEC[f0]||'gray',", "return {c:'gray',") if m == 'classe' else ("return {c,l:o.id+' · '+o.pz+mais(os.length)};", "return {c,l:o.id+' - '+o.pz+mais(os.length)};")
assert s.count(a) == 1, (m, s.count(a)); open(p, 'w', encoding='utf-8').write(s.replace(a, b)); print('mutante', m, 'aplicado')
PY
  RENDER_DIR="$D" MAPA_A2_PACK=${PACOTE:?defina PACOTE} timeout 900 $E python3 -B $G/os_mapa_test.py > $SP/ex55f1/r2/contraprova_$m.log 2>&1
  echo "mutante $m rc=$? · $(grep -c "^FALHA M1" $SP/ex55f1/r2/contraprova_$m.log) falha(s) no M1"
done
