#!/bin/sh
# Fontes que resolvem as divergências do confronto (só leitura).
# Uso: sh fontes_confronto.sh <repo> <G> <render>
#   <repo>   clone com os commits c827408 (origin/main), 529adf7 (pedidos-1610) e 47ccc1d (claude/v44-v69-mapa)
#   <G>      tools/prototipo/v37/gen37 de 47ccc1d (arquivos do mapa iguais aos de b989864)
#   <render> render publicado da composição 05947ad
REPO=$1; G=$2; R=$3
MAIN=c827408673580d18195dcf247388dac036d26bc1
PED=529adf7
FON=47ccc1d
sec(){ printf '\n## %s\n' "$1"; }
cut200(){ cut -c1-220; }

sec "0. Bases: anexos de pedidos-1610 contra o SHA256SUMS ($PED) e arquivos do mapa entre b989864 e $FON"
D=docs/integracao/V73/pedidos-1610
git -C "$REPO" show $PED:$D/SHA256SUMS | while read h n; do
  a=$(git -C "$REPO" show "$PED:$D/$n" | sha256sum | cut -d' ' -f1)
  if [ "$a" = "$h" ]; then echo "igual  $n"; else echo "DIFERE $n"; fi
done
printf 'arquivos do mapa alterados entre b989864 e %s: ' $FON
git -C "$REPO" diff --name-only b9898643662715a3f7b17bf7797d44e81e5e4a3d $FON -- \
  tools/prototipo/v37/gen37/areas/inicio.py tools/prototipo/v37/gen37/talmapa.js tools/prototipo/v37/gen37/talgeo.js \
  tools/prototipo/v37/gen37/g2lib.js tools/prototipo/v37/gen37/engine.py tools/prototipo/v37/gen37/areas/cad_fazendas.py \
  tools/prototipo/v37/gen37/areas/campo.py tools/prototipo/v37/gen37/areas/agronomia.py tools/prototipo/v37/gen37/areas/planejamento.py | wc -l

sec "1. PRD ($MAIN): lista alternativa, painel, tabela abaixo, câmera, alvo, geometria sintética"
git -C "$REPO" show $MAIN:docs/PRD.md | grep -n \
  -e 'Mapa e lista equivalentes' -e '^| RF-WRK-004' -e 'Não há tabela nem lista abaixo do mapa' \
  -e 'MAPUX-04:\*\*' -e 'MAPUX-06:\*\*' -e 'centralizando apenas quando solicitado' \
  -e 'Ausentes no protótipo | Ampliar mapa' -e 'O mapa é um grupo com nome acessível' \
  -e 'Abre à direita só com seleção' -e '^| Zoom | `role="group"' -e '^| DS-15 |' \
  -e 'Recolhível, com o estado lembrado' -e 'Geometria sintética no modo demo é identificada' \
  -e '^| DEC-2609-06 | Barras do mapa | Barra vertical' -e 'sem depender exclusivamente de gestos' | cut200

sec "2. Design system ($MAIN): BOT-03, BOT-08, SEL-01, VIS-04"
git -C "$REPO" show $MAIN:docs/design-system/README.md | grep -n -e '^| BOT-03' -e '^| BOT-08' -e '^| SEL-01' -e '^| VIS-04' | cut200

sec "3. Pedido e EX-43 ($PED, pedidos-1610)"
git -C "$REPO" show $PED:docs/integracao/V73/pedidos-1610/mapa-ux-pedido.md | grep -n \
  -e 'Alvos de toque de 48 px' -e 'Teclado: Tab entra no mapa' -e 'Zoom ou recentralização automática' \
  -e 'mostra o cartão em menos de 100 ms' -e 'REFERÊNCIAS PARA TIRAR' -e 'painel sem seleção' | cut200
git -C "$REPO" show $PED:docs/integracao/V73/pedidos-1610/mapa-ux-anexo-analise.md | grep -n \
  -e 'após cerca de 300 ms' -e 'enquadrar o selecionado' -e 'Alvos de 44 px no toque' | cut -c1-160
git -C "$REPO" show $PED:docs/integracao/V73/pedidos-1610/excelencia-pedido-ex01-48.md | grep -n \
  -e '^EX-43 Raio-X do alvo' -e 'risco de passar do NC em 7 e 14 dias' -e '"Risco nos próximos 7 dias" com "Criar vistoria"' | cut -c1-160

sec "4. Skill de satélite ($FON): dois níveis e ação por estado"
git -C "$REPO" show $FON:docs/claude/skills/indicadores-satelite/SKILL.md | grep -n \
  -e '^| \*\*Fazenda\*\* (listagem)' -e '^| \*\*Talhão\*\* (detalhe)' -e '^| Normal |' -e '^| Atenção |' -e '^| Crítico |' | cut -c1-160

sec "5. NAV: X-CAD-9 ($FON)"
git -C "$REPO" show $FON:docs/navegacao/CONSOLIDADO.md | grep -n '^| X-CAD-9' | cut200

sec "6. Fonte do protótipo ($FON): ícone Colheita, aria-pressed, forced-colors, verbo da vistoria"
grep -n "^ 'Colheita':'M12" "$G/engine.py" | cut -c1-40
grep -n "'Colheita': 'Colheita'" "$G/areas/inicio.py" | cut -c1-60
printf 'ICN (inicio.py:911) tem Colheita? '; sed -n 911p "$G/areas/inicio.py" | grep -c "'Colheita'"
printf 'ICS (inicio.py:1445) tem Colheita? '; sed -n 1445p "$G/areas/inicio.py" | grep -c "'Colheita'"
printf 'talhão do SVG (inicio.py:1411) com aria-pressed? '; sed -n 1411p "$G/areas/inicio.py" | grep -c 'aria-pressed'
printf 'forced-colors em engine.py: '; grep -c 'forced-colors' "$G/engine.py"; printf 'forced-colors em areas/inicio.py: '; grep -c 'forced-colors' "$G/areas/inicio.py"
printf '"Programar vistoria" em areas/inicio.py: '; grep -c 'Programar vistoria' "$G/areas/inicio.py"; printf '"Criar vistoria" em areas/inicio.py: '; grep -c 'Criar vistoria' "$G/areas/inicio.py"
printf 'g2dica: '; grep -n "pointerleave',()=>g2dicaSai(120)" "$G/g2lib.js" | cut -c1-12; grep -n ":300); },true);" "$G/g2lib.js" | cut -c1-12

sec "7. Render publicado (05947ad): AG-06, Ver dados, arquivos de apoio, MapLibre"
grep -o '<title>[^<]*</title>' "$R/AG-06.dc.html"
printf 'IN-04: "Ver dados abaixo"=%s  "Localizar no mapa"=%s  <table=%s\n' \
  "$(grep -c 'Ver dados abaixo' "$R/IN-04.dc.html")" "$(grep -c 'Localizar no mapa' "$R/IN-04.dc.html")" "$(grep -c '<table' "$R/IN-04.dc.html")"
printf 'IN-04 busca lagoa_s2.json por caminho relativo: '; grep -c "fetch('lagoa_s2.json')" "$R/IN-04.dc.html"
printf 'IN-04 carrega MapLibre do CDN: '; grep -c 'cdn.jsdelivr.net/npm/maplibre-gl@5.9.0' "$R/IN-04.dc.html"
ls -l "$R/lagoa_s2.json" | awk '{print "lagoa_s2.json no render:", $5, "B"}'
