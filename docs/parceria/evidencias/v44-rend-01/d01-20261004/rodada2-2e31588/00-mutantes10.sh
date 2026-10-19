# mutantes da rodada 2 do D-01 (REND): cópia descartável de 2e31588; volta UM defeito e o teste tem de falhar
set -u
M=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/mutantes10; rm -rf $M; mkdir -p $M
git -C /home/user/sp-camada-sintetica archive 2e31588 tools/prototipo/v37 | tar -x -C $M; cd $M/tools/prototipo/v37/gen37; mkdir -p _probe
export CHROME_BIN=/tmp/cloudchrome/chrome
volta(){ git -C /home/user/sp-camada-sintetica archive 2e31588 tools/prototipo/v37/gen37/safra.js tools/prototipo/v37/gen37/dados2.py tools/prototipo/v37/gen37/areas/processo_safra.py | tar -x -C $M; }
muta(){ python3 - "$1" "$2" "$3" <<'PY'
import sys; f,a,b=sys.argv[1:4]; s=open(f,encoding='utf-8').read(); assert s.count(a)==1,(f,a[:70],s.count(a)); open(f,'w',encoding='utf-8').write(s.replace(a,b))
PY
}
ora(){ python3 rend_multiconjuntos_unit.py 2>&1 | grep -E "^FALHA|RESULTADO|Error" | cut -c1-110; }
echo "== sem mutante"; ora | tail -1
echo "== mutante rodada 1 inteira: bloco REPARTIR, espelho e ajudas de 04bf6f2"
git -C /home/user/sp-camada-sintetica show 04bf6f2:tools/prototipo/v37/gen37/safra.js > safra.js; git -C /home/user/sp-camada-sintetica show 04bf6f2:tools/prototipo/v37/gen37/dados2.py > dados2.py; git -C /home/user/sp-camada-sintetica show 04bf6f2:tools/prototipo/v37/gen37/areas/processo_safra.py > areas/processo_safra.py
ora; volta
echo "== mutante R2-1: sem o teto de cortes por componente (JS)"
muta safra.js "if(nc.length>8192){ est=true; break; }" "if(nc.length>1e12){ est=true; break; }"; ora; volta
echo "== mutante R2-2: buraco no componente inteiro, com quem não tem janela (JS)"
muta safra.js "const cf0=comp.filter(i=>isFinite(V[i].H));" "const cf0=comp;"; ora; volta
echo "== mutante R2-3: partes fixas na ordem de chegada das restrições (JS)"
muta safra.js "gs.filter(g=>!SUB[g]).concat(gs.filter(g=>SUB[g])).forEach(g=>{" "gs.forEach(g=>{"; ora; volta
echo "== mutante R2-4: um motivo de troca por restrição (JS)"
muta safra.js "const r0=raiz(pistaA[g][0].i)+'@'+W[g], c=tcG[r0];" "const r0=g, c=tcG[r0];"; ora; volta
echo "== mutante R2-4b: conflito com um motivo por restrição (JS)"
muta safra.js "if(!cfG[r0]){ cfG[r0]={g,xs,nec,d}; cfO.push(r0); }" "if(!cfG[g]){ cfG[g]={g,xs,nec,d}; cfO.push(g); }"; ora; volta
echo "== mutante R2-5a: motivo da troca mesmo quando tudo cabe (JS)"
muta safra.js "bs=true; lg[g]=1;" "bs=true; lg[g]=1; liga[g]=1;"; ora; volta
echo "== mutante R2-5b: ajuste da troca sempre 'tire da sequência' (JS)"
muta safra.js "(o.indexOf('at:')===0?'use outro conjunto para '+quem:" "(o.indexOf('at:')===0?'tire '+quem+' da sequência':"; ora; volta
echo "== mutante R2-5c: motivo da troca sem o grupo (JS)"
muta safra.js "' h de '+nomes(pistaA[g])+' ('" "' h ('"; ora; volta
echo "== mutante R2-5d: sequência de estimativa como fato (JS)"
muta safra.js "x.seqEst=x.emSeq&&!xs.some(y=>y!==x&&UI.raiz(y.i)===UI.raiz(x.i));" "x.seqEst=false;"; ora; volta
echo "== mutante R2-5e: ajuda da janela antiga"
muta areas/processo_safra.py "Prazo, contado do início da ocorrência, para este conjunto terminar em cada talhão ou parcela; em sequência, cada configuração termina dentro da própria janela, e a janela maior de outra não amplia a dela." "Quanto este conjunto pode trabalhar em cada talhão ou parcela; em sequência, as configurações dividem a maior janela entre elas."; ora; volta
echo "== mutante R2-5f (tela): chip agregado antigo '3 sem horas na janela · pendente'"
muta safra.js "t:c+' · '+(its.length>1?pc[c]+(pc[c]>1?' pendentes':' pendente'):'pendente')" "t:(its.length>1?pc[c]+' '+c:c)+' · pendente'"
python3 build.py >/dev/null 2>&1 && python3 montar_render.py >/dev/null 2>&1 && timeout 900 flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py bordas 2>&1 | grep -E "^FALHA|RESULTADO" | cut -c1-140
volta
echo "== fim"
