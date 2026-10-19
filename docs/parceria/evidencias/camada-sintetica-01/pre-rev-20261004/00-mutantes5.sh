# mutantes da PRE-REV-20261004 (SINT): cada um volta UM defeito numa cópia descartável de 3ba5f14; o teste tem de falhar
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes5; rm -rf $M; mkdir -p $M
git -C /home/user/sp-fix archive 3ba5f14 tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37
mut(){ nome=$1; arq=$2; old=$3; new=$4; teste=$5; cp $arq /tmp/.mut.bak
  python3 - "$arq" "$old" "$new" <<'PY'
import sys; f,o,n=sys.argv[1:]; o=o.replace('\\n','\n'); n=n.replace('\\n','\n'); s=open(f,encoding='utf-8').read()
if s.count(o)!=1: print('MUTANTE NÃO APLICADO',f,repr(o[:60])); sys.exit(3)
open(f,'w',encoding='utf-8').write(s.replace(o,n))
PY
  if [ $? -ne 0 ]; then echo "== mutante $nome: NÃO APLICADO (falha do roteiro)"; cp /tmp/.mut.bak $arq; return; fi
  echo "== mutante $nome ($arq)"; python3 $teste 2>&1 | grep -E "^(FALHOU|RESULTADO)" | cut -c1-160; cp /tmp/.mut.bak $arq; }
echo "== sem mutante"; python3 quantidade_test.py | tail -1; python3 dados_lagoa_sintetico/camada_test.py | tail -1
mut P1-mip mip.js "tot: cenQtd(dose, area), sit:" "tot: Math.round(dose * area * 1000) / 1000, sit:" quantidade_test.py
# P2 volta as DUAS linhas (total da v2 em kg inteiros e a O.S. lendo esse total); só uma delas é mutante equivalente (f.tot já seria cenQtd)
cp irrigacao_estado.js /tmp/.mut2.bak; python3 - <<'PY'
f='irrigacao_estado.js'; s=open(f,encoding='utf-8').read(); o="tot: cenQtd(d.dose, area), sw };"; assert s.count(o)==1; open(f,'w',encoding='utf-8').write(s.replace(o,"tot: Math.round(d.dose * area), sw };"))
PY
mut P2-fertirrigacao irrigacao_estado.js "tot: cenQtd(f.dose, f.area), sit:" "tot: f.tot, sit:" quantidade_test.py
cp /tmp/.mut2.bak irrigacao_estado.js
mut P3-formulario areas/agronomia.py "area:mipN(area,2),data,mot:'',err:''}" "area:mipN(area,1),data,mot:'',err:''}" quantidade_test.py
mut P7-trava-desligada areas/processo_os.py "if(q>it.custodia+1e-9) throw new Error('Consumo de '" "if(false&&q>it.custodia+1e-9) throw new Error('Consumo de '" quantidade_test.py
mut P4-versao cenario.py "return dict(v=3, rev=0," "return dict(v=2, rev=0," dados_lagoa_sintetico/camada_test.py
mut P5-base-literal dados_irrigacao.py "base=_REAL['OS-0507']" "base=0" dados_lagoa_sintetico/camada_test.py
mut Q1-area-1-casa irrigacao_estado.js "Math.round((x.ha - Math.min(x.ha, p.cob || 0)) * 100) / 100" "Math.round((x.ha - Math.min(x.ha, p.cob || 0)) * 10) / 10" quantidade_test.py
mut Q1-previa-propria areas/irrigacao.py "const area=irrAreaV2(x,pa);" "const area=pa?Math.round((x.ha-(pa.cob||0))*10)/10:x.ha;" quantidade_test.py
mut Q2-sem-exponencial cenario.js "(?:e([+-]\\d+))?\$/.exec" "\$/.exec" quantidade_test.py
mut Q3-trava-crua areas/processo_os.py "need=cenQtd(d,ar);" "need=d*ar;" quantidade_test.py
mut Q4-mip-cru mip.js "const need = cenQtd(dose, area);" "const need = dose * area;" quantidade_test.py
mut Z1-total-zero-liberado cenario.js "    if (x.dose > 0 && !(x.tot > 0)) throw new Error" "    if (false) throw new Error" quantidade_test.py
mut Z2-aviso-soma-lotes mip.js "    const lt = cenLote(c, u.nome), disp = lt ? cenDisp(lt) : 0;" "    const disp = Object.values(c.lotes).filter(l => l.prod === u.nome).reduce((q, l) => q + Math.max(0, (l.fisico || 0) - (l.quarentena || 0) - (l.reservado || 0)), 0);" quantidade_test.py
mut Z4-avanco-3-casas irrigacao_estado.js "  cob = irr2(cob);   // 2 casas, antes de validar (PRE-REV Z4/Y4)\\n  if (!(cob >= 0)" "  if (!(cob >= 0)" quantidade_test.py
mut Y1-v2-zero irrigacao_estado.js "  { const m = irrV2Zero(x, p, d.dose); if (m) throw new Error(m); }" "  " quantidade_test.py
mut Y2-mip-zero mip.js "  else if (dose > 0 && !(cenQtd(dose, area) > 0)) tr.push" "  else if (false) tr.push" quantidade_test.py
mut Y3-rotulo areas/processo_os.py "    const z=e&&/Dose × área de (.+?) dá 0/.exec(e);" "    const z=null;" quantidade_test.py
mut Y4-binario irrigacao_estado.js "function irr2(n) { const t = String(n); return /e/i.test(t) ? Math.round(n * 100) / 100 : Number(Math.round(Number(t + 'e2')) + 'e-2'); }" "function irr2(n) { return Math.round(n * 100) / 100; }" quantidade_test.py
mut Y6-trava-zero areas/processo_os.py "  if(!(need>0)) return 'Dose × área dá 0 '+un+': aumente a dose ou a área.';" "  if(false) return '';" quantidade_test.py
mut X1-painel-estoque areas/processo_os.py "if(e) b=o.total0?{acao:" "if(e) b=false?{acao:" quantidade_test.py
mut X2-ajuste-sem-lib areas/processo_os.py "  { const z0=o.ins.find(x=>x.dose>0&&!(x.tot>0)); if(z0) throw" "  { const z0=null; if(z0) throw" quantidade_test.py
mut X5-msg-passadas irrigacao_estado.js "return irrPassProx(o) ? 'A passada '" "return false ? 'A passada '" quantidade_test.py
