# MAPA-UX · Avaliação independente do Claude (passo 1)

Pedido do proprietário de 16/10/2026: "Mapa da fazenda com UX e UI de excelência" ([pedido.md](pedido.md); inventário em [anexo-analise.md](anexo-analise.md)).

- **Autor:** Claude. **Revisor do passo 2:** Codex. **Quem registra o desenho final e as fatias no checkpoint:** só o Codex (passo 3 do pedido).
- **Data:** 16/10/2026 (medidas de navegador no início de 17/10, UTC).
- **Bases lidas:**
  - fonte do protótipo: `b9898643662715a3f7b17bf7797d44e81e5e4a3d` (`G` = `tools/prototipo/v37/gen37`);
  - render publicado: versão 1792184197-5a81, espelho local `site70` (só leitura). **O espelho foi trocado às 00:16:19 UTC de 17/10, durante a passada de navegador**, pelo render da composição 05947ad (b989864 + PRs #81, #90 e #91; publicação registrada em 47ccc1d). Nenhum arquivo do mapa mudou entre b989864 e 05947ad (`reproducao/espelho_troca.txt`); M0–M2 rodaram no espelho antigo e as demais no novo;
  - PRD, DECISIONS e design system: `origin/main` `c8274086`;
  - Raio-X: artefato BhceWUXPoT9BXgTGUCy6LP, versão 1792193012-4fc4 (lido como dado; só trechos curtos citados aqui).
- **Estado:** especificado. As medidas da §R foram **executadas**; nada aqui foi implantado.
- **Não simulei o Codex nem o Gemini.** Onde a decisão é material, marquei "Gemini via Codex" ou "proprietário" (§7).

```text
ID / resultado útil / persona: MAPA-UX passo 1 / avaliar o mapa atual contra o pedido, o PRD, o NAV/DS, a skill de satélite e as 10 heurísticas / gestor, agrônomo, PCP, operador no celular
Requisitos do PRD e fora do escopo: IN-04, 67, 74.5.22–26, 74.7, UX-05, DEC-2609-06/12, DEC-1610-03/09/12; fora: implantar, registrar checkpoint, crítica do Raio-X (frente paralela)
Autor / revisor / integrador: Claude / Codex / Codex (registro)
Base / arquivos sob responsabilidade: b989864 / docs/integracao/V73/MAPA-UX/ (só documentos e reprodução)
Aceite e comando de verificação: §R; python3 -I -B reproducao/cores.py; python3 -I -B reproducao/busca_paleta.py; python3 -I -B reproducao/cor_significado.py <G>; SITE=<site70> CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 python3 -I -B reproducao/repro_mapa.py
Estado / impedimento / próximo passo: entregue para o passo 2 (divergências por fonte ou reprodução)
```

## Resumo

- **D1–D30:** 26 confirmados por inteiro e 4 em parte (D2, D11, D12, D19). Nenhum caiu por inteiro. As partes que não reproduzem: o Chrome expõe os botões do SVG (D2); a mancha não cobre o rótulo (D11); os rótulos das camadas não são cortados, só o chip da mancha (D12); o resultado de "Medir" é anunciado pela região viva (D19).
- **5 achados novos** (N1–N5). O mais sério: abrir o painel encolhe o mapa e o talhão salta 175 a 192 px; o segundo clique, que deveria fechar, seleciona o vizinho.
- **Maior dano hoje:** a fazenda padrão (Lagoa Grande) não tem nenhum pivô alcançável por teclado (0 de 23 em 140 Tabs) e o mapa depende do CDN em tempo de execução (D1 e D26, S2).
- **Antes, medido:** 2 cliques até o detalhe do pior talhão em 18 de 18 combinações (camada × fazenda), se a pessoa já sabe qual é; nenhuma dica no hover nem no foco; 19 controles abaixo de 44 px a 390 px; rótulos da Santa Rita com 4,4 px no celular; 11 pares de rótulos sobrepostos na Lagoa Grande a 390 px; "não se aplica" × fundo 1,00:1; menor distância de cor entre estados na deuteranopia 1,0.
- **Principais mudanças que proponho ao desenho:**
  1. Uma camada de botões acessíveis por talhão, sobre qualquer motor, com busca "Ir para talhão" ("/"): é o que destrava teclado, leitor de tela, URL e testes estáveis (`[data-talhao]`).
  2. O cartão de hover é uma variante do `g2dica` com 80 ms (0 ms no foco e entre vizinhos), e não um componente novo.
  3. Regra única da câmera: só se move por pedido explícito (busca, "Enquadrar", "Ver no mapa", voltar).
  4. Painel por cima do mapa, sem encolher o mapa (N1).
  5. Legenda que trabalha (contagem, área, clique filtra) no lugar de um ranking novo: leva ao pior talhão em 2 ações.
  6. Contraste Fazenda/Absoluto na visão da fazenda; painel na mesma escala (D9: hoje o mesmo pixel é "Falha" no mapa e "Vigor alto" no painel).
  7. Tokens por significado, medidos: distância mínima de 13,6 na deuteranopia (hoje 1,0); Estádio sai do amarelo e do laranja.
  8. Verde só para comando; navegação vira link (N2, BOT-08). Aprovar e liberar continuam um a um (DEC-1610-03).
  9. Um motor só (MapLibre empacotado) em duas etapas: primeiro a camada de botões (F1), depois a troca do motor da Santa Rita (F3), revendo o X-CAD-9 com prova.
- **Precisa do Gemini via Codex:** paleta por significado (acessibilidade), painel sem seleção (fluxo, contraria DEC-2609-06) e modelo de teclado (uma parada de Tab com setas).
- **Precisa do proprietário:** paleta alternativa da rampa de vigor, "você está aqui" no app (posição pessoal), mapa-base ou imagem real com custo, liberação do teste com usuários (UX-13).

## Onde está a fonte do IN-04

- O anexo cita linhas do HTML publicado. A fonte vigente é Python e JS no gerador:
  - lógica do mapa: `G/areas/inicio.py:517-1401` (`MAP_JS`), mais `G/talmapa.js` e `G/talgeo.js`;
  - desenho (SVG, painel, faixa, ferramentas): `G/areas/inicio.py:1403-1662`;
  - dica comum: `G/g2lib.js:1146-1257`; aviso e região viva: `G/engine.py:2148-2180`, `G/g2lib.js:1045-1130`.
- **Tradução das linhas (executado):** no IN-04 da versão 1792184197-5a81 (a do anexo), linha publicada = linha de `inicio.py` + 6695 até a `:1204`, e + 6692 depois da `:1208`. As 1028 linhas de JS do mapa (7212 a 8239) têm par literal na fonte de b989864 (`reproducao/fonte_publicado.txt`, gerado antes da troca do espelho). No espelho novo (05947ad) o deslocamento é + 6698 e as 875 linhas da lógica do mapa também têm par literal (`reproducao/fonte_publicado_05947ad.txt`).

## 1. Confirmação dos D1–D30 na fonte vigente

Legenda: **sim (código)** = confirmado pela leitura; **sim (navegador)** = reproduzido no render publicado (§R, medida citada); **parcial** = parte confirma e parte não; **não reproduz** = com a prova. Severidade pelo PRD 22.1 (ENG-003) com a ligação NN/g de `docs/design-system/diretrizes-ux.md:13`. Esforço: P (horas), M (1–2 dias), G (vários dias).

| D | Confirma? | Fonte vigente (arquivo:linha em `G`) | S | Correção proposta | Esforço |
|---|---|---|---|---|---|
| D1 | sim (código e navegador, §R M0/M1) | `areas/inicio.py:632-633` (clique e cursor só no canvas), `:646` (marcador `role=img`, sem foco), `:1558` (`#mapa-real` sem papel) | S2 | Botão `[data-talhao]` por pivô sobre o canvas, busca "Ir para talhão" e Esc (MUX-F1) | M |
| D2 | parcial: o código confirma; no Chrome a árvore de acessibilidade expõe os 8 botões (§R M2). Fica o risco em outros leitores, porque a regra ARIA trata filhos de `img` como apresentação | `areas/inicio.py:1434` (`svg role=img`) envolvendo `:1411` (`role=button`) | S3 | `role=group` com nome; talhões como botões com `[data-talhao]` | P |
| D3 | sim (código e navegador, §R M3) | `g2lib.js:1170` (SVG não vira dica), `:1171-1173`; `areas/inicio.py:633` (só cursor); realce `engine.py:1091` sob o grupo de pixels desenhado depois do polígono (`areas/inicio.py:1416-1417`, `:1441`) | S3 | Cartão do mapa (variante do `g2dica`) e realce do contorno acima dos pixels | M |
| D4 | sim (código) | `areas/inicio.py:1126` (`scale` de 1 a 2, sem pan), `:1556` (`overflow: hidden`) | S3 | Pan e enquadrar (MUX-F3, MapLibre); até lá, arrastar no SVG | M |
| D5 | sim (código e navegador, §R M14) | `areas/inicio.py:1191` (`has_full=!map_lg`), `:1558` (tela cheia sem o ramo do mapa real) | S4 | Tela cheia comum às duas fazendas, com Esc e foco | P |
| D6 | sim (código e navegador, §R M14) | `areas/inicio.py:1102` (`FAZ` vira Santa Rita para tudo que não é Lagoa Grande), `:1189` | S3 | "Todas" com as duas fazendas lado a lado ou fora do filtro | P |
| D7 | sim (código e navegador, §R M15) | `areas/inicio.py:1127` (Satélite → `AG-06.dc.html`), `:1016` (painel); `AG-06` tem o título "Eficácia e histórico" (site70) | S3 | Sem link até o EX-42 entregar a série do índice; depois, a série do talhão | P |
| D8 | sim (código e navegador, §R M15) | `areas/inicio.py:1074` e `:1127` (sem talhão); a O.S. aceita `#tal=Faz\|T` (`areas/processo_os.py:969-976`) | S3 | Levar `#tal=` | P |
| D9 | sim (código e navegador, §R M17) | `areas/inicio.py:116` (Talhão é o 1º, portanto o padrão), `:862-865` (legenda só com nomes sem talhão escolhido), `:833` e `:987` (chip pela classe absoluta `ka`), `:1006-1011` (pixel pela absoluta) | S3 | Padrão Fazenda (ou Absoluto) na visão da fazenda; Talhão só com um talhão escolhido e com nomes relativos; painel na escala do mapa (skill §1; EX-42 decisão 4) | M |
| D10 | sim (código; executado sobre `M.px`) | `areas/inicio.py:353` (`CS=16`, "10 m"), `:1011` ("· 10 m ·"). T1: 312 ha em 276 células = 1,13 ha/célula; C1: 0,22 ha/célula (o desenho não é proporcional) | S4 | Tirar "10 m"; dizer "célula do desenho"; escala real na MUX-F3 | P |
| D11 | parcial: mancha só no T7, sim; sobreposição com o rótulo, **não reproduz** (0 px² a 1440 px, §R M18b); o chip é cortado (N4) | `areas/inicio.py:1423-1425` (círculo e chip fixos no T7), `:349-351` e `:745` (mancha só no T7) | S4 | Mancha vinda do dado (qualquer talhão), chip fora do rótulo | M |
| D12 | parcial: encolhe, sim (a 390 px o rótulo de 15 un vira 4,4 px e o subtítulo 3,8 px, §R M7); corte, **não reproduz** nos rótulos das 9 camadas e filtros (§R M7b); só o chip da mancha é cortado (N4) | `areas/inicio.py:1428-1429` (`foreignObject` de 20 e 46 un), `:1403-1406` (15 e 13 px escalados com o SVG) | S3 | Rótulos em px fixos fora do SVG escalado; reticências e texto inteiro no cartão | M |
| D13 | sim (código e navegador, §R M16) | `areas/inicio.py:645` (0,55 na classe, 0,35 na nuvem), `:854` (amostra a 100 %), `:430` (`gray` = `cloud`) | S3 | `fill-pattern` de hachura no MapLibre; a legenda com a mesma opacidade | P |
| D14 | sim (código; contraste executado) | `areas/inicio.py:430` (`none` `#E4E9DF`) sobre `:1556` (fundo `#E3EADB`): 1,00:1; cinza × não se aplica 1,28:1 | S3 | Contorno tracejado `#6B776F` (3,80:1) e "fora do filtro" com rótulo | P |
| D15 | sim (código; inventário e simulação executados) | `areas/inicio.py:785`, `:866-871`, `:1370`; cinza e amarelo com 13 significados cada (`reproducao/cor_significado.txt`); deuteranopia: 1,0 de distância mínima | S3 | Tokens por significado (§5) | M |
| D16 | sim (código e navegador, §R M10) | `areas/inicio.py:1435` (fundo sem clique), `:1145-1147` (no Satélite o clique troca de pixel, não desmarca), `talmapa.js:67` | S4 | Esc e clique no fundo desmarcam; o mesmo toggle em todas as camadas; pixel só no modo "Inspecionar" | P |
| D17 | sim (código e navegador, §R M10) | `areas/inicio.py:1111` (só `sessionStorage`), `:620` (câmera nasce no `bbox`) | S3 | URL com fazenda, camada, data e talhão; câmera lembrada | P |
| D18 | sim (código e navegador, §R M11: com o contexto na Santa Rita, `#talhao=PV05` não troca a fazenda nem abre o painel) | `talmapa.js:166-169` (`#talhao=` põe a seleção sem trocar a fazenda); `areas/inicio.py:1110` (seleção filtrada pela fazenda) | S3 | `#talhao=` impõe a fazenda do talhão; se não achar, aviso visível (SEL-02) | P |
| D19 | parcial: não mede, sim, e o aviso some antes de 5 s (§R M12); "mudo para leitor de tela", **não reproduz**: a região viva `#g2-vivo` recebe o mesmo texto (`g2lib.js:1130`; `engine.py:2177`) | "Medir" repete a área do cadastro: `areas/inicio.py:1143`, `:606`; aviso some em 4,5 s: `engine.py:2149` | S4 | Resultado no painel; renomear "Área e perímetro" até medir de verdade (MUX-F3) | P |
| D20 | sim (navegador, §R M10, M14: Esc não fecha painel nem tela cheia; tela cheia sem `aria-modal` e sem foco dentro; a 390 px o painel nasce em y = 825 numa janela de 844) | `areas/inicio.py:1162` (só `scrollTop` interno), `:1659` (painel abaixo de 62vh de mapa no estreito), `:1660` (diálogo sem `aria-modal`, sem Esc) | S3 | Foco no título do painel, Esc, folha inferior visível; tela cheia como diálogo modal | M |
| D21 | sim (código e navegador, §R M13) | `areas/inicio.py:1634` (`role=tab` sem `aria-controls` e sem setas); `g2lib.js:1355` exige `[data-visao]` | S4 | Setas e Home/End no `tablist` (o `g2visaoTecla` já faz a conta) | P |
| D22 | sim (navegador, §R M5: a 390 px com toque, 19 controles abaixo de 44 px; a 1440 px, nenhum abaixo de 24) | `areas/inicio.py:1165` (ferramentas com padding 6/10, sem altura mínima), `:1523` (zoom 36 px), `:1498` (fechar 30 px) | S3 | `min-height` e `min-width` com `--g2-alvo` (44 px no toque), como o ícone de laudo já faz (`:1535`) | P |
| D23 | sim (navegador, §R M6: a 1440 px a legenda cobre 9 a 11 % de T4, T3, T7 e C1 e recebe o clique; a 390 px ocupa 13 % e 17 % da altura do mapa, não os 30 % do teto do CSS) | `areas/inicio.py:1562` (legenda absoluta sobre o mapa), `:1659` (até 30 % no estreito) | S3 | Legenda recolhível; `pointer-events: none` no contêiner e `auto` nos itens | P |
| D24 | sim (código e navegador, §R M15) | `areas/inicio.py:1127-1128` (`FL` sem Solo e sem Colheita › Situação) | S4 | Atalhos "Abrir Análises de solo ›" e "Abrir Previsão e colheita ›" | P |
| D25 | sim (código e navegador, §R M15) | `areas/inicio.py:911` (`ICN` sem `Colheita`), `:1445` (`ICS` idem); usado em `:1080`, `:1398-1400` | S4 | Pôr `Colheita` nas listas de ícones | P |
| D26 | sim (código e navegador, §R M0) | `areas/inicio.py:569` (CDN em tempo de execução), `:571` (2,59 MB sem indicador), `:649` (só aviso na falha) | S2 | Empacotar o MapLibre; indicador de carga; lista como alternativa (MUX-F3) | M |
| D27 | sim (código) | `areas/inicio.py:646` ("P1"), `:986` ("Pivô 1"), `areas/cad_fazendas.py:231` ("PV01"); a Santa Rita também tem "P1" e "P2" (`areas/inicio.py:103`) | S3 | Um nome exibido ("P1"); "Pivô 1" e "PV01" como apelidos na busca; prefixo da fazenda só quando "Todas" | P |
| D28 | sim (navegador, §R M8: a 390 px, 11 pares de rótulos sobrepostos entre 23; a 1440 px, nenhum) | `areas/inicio.py:565-566` (rótulos em px fixos), `:635-636` (`.peq` para menos de 20 ha nunca ocorre: o menor pivô tem 29,92 ha) | S3 | Regra por tamanho em tela e colisão (só o número quando não cabe) | M |
| D29 | sim (navegador, §R M9b: um dedo move o mapa e a página não rola; o mesmo gesto fora do mapa rola 165 px) | `areas/inicio.py:619-620` (sem `cooperativeGestures`) | S3 | Gesto cooperativo no estreito (dois dedos movem; um dedo rola a página) | P |
| D30 | sim (código) | `areas/inicio.py:1527` (rótulo "Selecionar área", dica "Selecionar vários talhões"), `:1167` | S4 | Renomear "Selecionar vários" | P |

**Achados novos (fora do anexo), todos executados:**

| N | Achado | Prova | S | Correção | Esforço |
|---|---|---|---|---|---|
| N1 | Abrir o painel encolhe o mapa de 1306 para 921 px. O talhão clicado salta 175 px (T4) e 192 px (PV05); sob o ponteiro passa a estar o vizinho (T3, PV06). O segundo clique "para fechar" seleciona outro talhão | §R M20, M19b; `G/areas/inicio.py:1495` (painel de 384 px em `flex`), `:1554` | S3 | Painel por cima do mapa, sem mudar a largura; no MapLibre, `padding` da câmera em vez de redimensionar | P |
| N2 | Verde de navegação no painel: "Abrir laudo" (Solo), "Abrir OS-0507" (Irrigação, Lagoa Grande), "Acompanhar OM-0233" (Ordens de serviço, T4) | §R M4; `G/areas/inicio.py:1361-1364`, `:1078`, `:948` e `:968` | S4 | Navegação vira link (BOT-08); verde só para comando | P |
| N3 | O canvas do MapLibre tem o nome acessível "Map" (inglês) e `role=region`; o contêiner `#mapa-real` tem `aria-label` sem papel | §R M0; `G/areas/inicio.py:619`, `:1558` | S4 | `locale` pt-BR do MapLibre ou o nome do grupo da camada de botões | P |
| N4 | O chip da mancha mostra "mancha 1,2" sem "ha": `foreignObject` de 21 px com conteúdo de 37 px e `overflow: hidden` | §R M18c (recorte `reproducao/m18c_T7_satelite_1440.png`), M7b; `G/areas/inicio.py:1425` | S4 | Chip fora do SVG escalado ou com largura pelo texto | P |
| N5 | O "pior estado" do Integrado não considera pragas nem carência: só O.S., irrigação e a mancha do satélite | `G/areas/inicio.py:176-177`, `:714-719` (leitura) | S3 | O Integrado pega o pior das camadas pela mesma ordem SEV, com o motivo | M |

## 2. O padrão de interação do talhão (seção 1 do pedido)

| Item do pedido | Decisão | Motivo e regra proposta |
|---|---|---|
| Polígono real, contorno fino, número grande com halo | **Adotar** | PRD 74.7.5 já exige ID grande com halo. A Santa Rita não tem polígono real: continua "Demonstrativo" (selo da legenda). |
| Até 3 linhas no talhão; em zoom pequeno só o número | **Adotar** | Resolve D12 e D28. Regra por tamanho em tela, não pelo zoom: com menos de 72 px de largura útil, só o número; menos de 32 px, só o contorno e o número no cartão. Rótulos em px fixos (14–16 px), nunca escalados com o SVG. |
| Selos no canto (manejo recente, O.S. em andamento, alerta) | **Adaptar** | No máximo 2 selos por talhão, com ícone e sem cor nova: o selo usa a forma (ícone) e a legenda diz o significado. O "manejo recente" lê o fato apontado (EX-38/EX-42), nunca o planejado. Selo não é alvo de toque (o talhão é). |
| Sem dado, nuvem ou sem lavoura: hachura ou neutro | **Adotar** | DS-66 já separa: hachura = sem leitura; liso = não se aplica. Falta o contorno tracejado do liso (hoje some no fundo, 1,00:1; §5). |
| Realce do contorno e cursor de mão em menos de 100 ms | **Adotar** | Realce por estilo (CSS ou `feature-state` no MapLibre), sem `setState` do motor. |
| Cartão de hover × atraso de 300 ms do `g2dica` (hoje: nenhuma dica no mapa, §R M3) | **Adaptar** | Um componente só (o `g2dica`, com `role=tooltip`, `aria-describedby`, Esc e toque longo), numa variante "cartão do mapa": **0 ms no foco**; no ponteiro, **80 ms** no 1º talhão e 0 ms ao passar de um talhão para o vizinho com o cartão aberto (o `g2dica` já faz isso, `G/g2lib.js:1227`). Assim cumpre "< 100 ms" sem piscar ao cruzar a fazenda. O atraso de 300 ms continua para botões e selos (VIS-04). |
| Conteúdo do cartão | **Adotar, com corte** | Linha 1: número · área · cultura e estádio. Linha 2: valor da camada com unidade · estado em texto · data do dado. Linha 3 (só quando houver): comparação curta ou manejo/O.S. Última linha: "Clique para detalhar" (no toque: "Toque para detalhar"). Nada além disso: o resto é do painel. |
| Cartão não cobre o talhão nem é cortado | **Adotar** | Lado do talhão com mais espaço (direita, esquerda, acima, abaixo), ancorado na caixa do talhão; preso à janela com 8 px. Se o talhão ocupa mais de 60 % do mapa (zoom alto), o cartão vai para o canto do mapa oposto ao ponteiro. Nunca segue o ponteiro (evita tremor). |
| Sem ação dentro do cartão | **Adotar** | Já é regra do pedido (§5) e do VIS-04. |
| Clique seleciona, contorno forte, `aria-pressed` | **Adotar** | Hoje o contorno de foco (tracejado escuro) e o de seleção (escuro, 6 un) se confundem (`G/engine.py:1106` × `G/areas/inicio.py:1141`). Proposta: seleção = contorno escuro 4 px + halo branco 2 px; foco = anel verde de 2 px fora do contorno (o anel do DS). |
| "O mapa não muda de zoom sozinho" × "busca centraliza" | **Adaptar (regra única)** | A câmera só se move por **pedido explícito**: busca "Ir para talhão", "Enquadrar", link "Ver no mapa" (`#talhao=`, `#frota=`) e voltar ao mapa. Clique, hover, troca de camada, filtro e seleção pela lista nunca movem a câmera. No pedido explícito: centraliza; aproxima só se o talhão ficar com menos de 48 px; afasta só se não couber. Respeita `prefers-reduced-motion` (sem animação). É o que o PRD 67.3 já diz ("centralizando apenas quando solicitado") e o que o MAPA-FROTA pede ("sem pan automático"). |
| Detalhe no painel lateral (embaixo no celular), sem sair do mapa | **Adaptar** | Já existe (384 px), mas **encolhe o mapa** e o talhão salta 175 a 192 px (N1, §R M20). Proposta: o painel fica por cima do mapa, que não muda de largura. Falta também: foco no título ao abrir por teclado, Esc fecha e devolve o foco ao talhão, e no estreito a folha inferior visível (hoje nasce em y = 825 de 844, D20). |
| "Abrir talhão ›" para o CD-01det e voltar igual | **Adotar** | Link secundário (BOT-08). O retorno depende de a URL guardar o estado (D17). |
| Fechar: clicar de novo, Esc, "‹ Todos os talhões" | **Adotar** | Mais o clique no fundo (D16). Hoje Esc e fundo não fecham (§R M10), e o "clicar de novo" cai no vizinho por causa do N1. "‹ Todos os talhões" só existe quando o painel sem seleção mostra a visão da fazenda (abaixo). |
| Painel sem seleção = visão da fazenda | **Adaptar** | O IN-04 hoje não tem painel sem seleção (PRD 74.6.6: painel "só com seleção"). Proposta: sem seleção, o painel fica fechado no computador e a legenda que trabalha (abaixo) faz o papel de ranking. Na camada Pragas e doenças, a visão da fazenda é o Raio-X do alvo (frente paralela; fronteira na §3). Abrir o painel sem seleção contraria DEC-2609-06 ("seleção abre painel direito"): **decisão material de fluxo → Gemini via Codex**. |
| URL com camada, data e talhão | **Adotar** | SEL-02 já exige. Formato proposto: `#faz=LG&lay=sat&t=PV05&dt=25-09` (sem acento, sem literal de fazenda no código). O `mapa-ctx` continua só como lembrança da última escolha. |
| Seleção de vários (Shift + clique, laço ou retângulo) | **Adaptar** | Só onde há ação em lote real: "Programar vistoria nas áreas" (existe, uma vistoria por talhão) e "Criar O.S. para os N" (uma O.S. por talhão, P23 da análise externa v4, `docs/integracao/V71/EX-analise-externa-v4.md:78`; nascem em rascunho/A liberar, **nunca aprovadas ou liberadas em lote**, DEC-1610-03 e CMD-06). Shift + clique e o modo "Selecionar vários" (renomeado, D30) entram na F1; retângulo fica para quando o SAF-MAPA precisar (ele já cita a ferramenta). Laço: descartar (sem caso de uso que o retângulo não cubra). |
| Barra "4 talhões · 182 ha" com as ações | **Adotar** | Já existe no painel (`panelArea`, `G/areas/inicio.py:1093-1097`). Mover para uma barra fina sobre o mapa no estreito. |
| Legenda que trabalha (contagem, área, hover destaca, clique filtra) | **Adotar** | É o "ranking" sem tela nova: a classe mais grave vem primeiro (ordem SEV) com "3 talhões · 254 ha"; clicar filtra e lista os talhões da classe no painel; cada item abre o talhão. Isso leva o gestor ao pior talhão em 2 ações (aceite do pedido). |
| Busca "P12", "T4" (centraliza e seleciona) | **Adotar** | Campo "Ir para talhão" no topo do mapa, atalho "/"; aceita número, nome e apelido (P1, Pivô 1, PV01 → o mesmo, D27). |
| Trocar camada mantém zoom, data e seleção | **Adotar** | Já mantém seleção e filtros (`G/areas/inicio.py:1137`); falta a câmera do MapLibre (D17). |
| Teclado: Tab entra; setas entre vizinhos; Enter; Esc; "/" | **Adaptar** | Proposta: o mapa é **uma parada de Tab** (padrão "roving tabindex", só o talhão ativo com `tabindex=0`); setas vão ao vizinho na direção (pelo centro); Home/End ao primeiro/último pela ordem do nome; Enter seleciona; Esc fecha; "/" busca. Com 23 pivôs, colocar todos na ordem de Tab custaria até 23 Tabs para sair do mapa. Decisão de acessibilidade material → **Gemini via Codex** (alternativa: todos na ordem de Tab, mais simples e mais lenta). |
| Celular: toque seleciona e abre folha inferior; toque longo mostra o cartão | **Adotar** | O toque longo já existe no `g2dica` (500 ms, `G/g2lib.js:1239-1241`). A folha inferior abre com meia altura e mostra o mapa acima. |
| Alvos ≥ 48 px, texto ao sol, "você está aqui" | **Adaptar** | O DS fixa 44 px (DS-15); 48 px só se o Codex mudar o token. "Você está aqui" fica fora da F1: depende de GPS do aparelho e de permissão (§7). |
| Nome acessível completo por talhão | **Adotar** | Hoje: "T1: <rótulo da camada>" (`G/areas/inicio.py:1141`) e, na Lagoa Grande, `role=img` sem foco (`:646`). Proposta: "P4, 73 ha, mamão em produção, ácaro 23 % das folhas, acima do NC, vistoria em 19/09" (mesma regra do Raio-X, linha 784-807 do artefato). |
| Estado em texto além da cor; foco visível; nada só no hover | **Adotar** | O rótulo já é texto. Falta: a mesma informação do cartão estar no nome acessível e no painel. |
| Desempenho: hover e seleção < 100 ms, troca de camada sem recarregar, sem salto | **Adotar** | Hover por estilo; seleção sem redesenhar a página inteira (hoje cada `setState` redesenha o template). Medido (indicativo, §R M19): clique → painel de 79 a 295 ms na Santa Rita; troca de camada de 73 a 933 ms; o salto ao abrir o painel (N1) quebra o "sem salto". |

## 3. Por camada

Cada linha: o que existe (com fonte), o que falta e o conflito com regra. "Primária" = o verde do rodapé do painel (BOT-01: um verde por contexto; BOT-04: mini no painel do mapa).

| Camada | Cor e legenda | Cartão de hover (proposto) | Painel: existe → falta | Primária proposta e conflitos |
|---|---|---|---|---|
| **Integrado** | Pior estado operacional; legenda em 5 itens sem contagem (`G/areas/inicio.py:861`). | "T4 · 204 ha · soja · semeadura" / "OS-0420 impedida · Trator T1 · desde 23/09" / "Clique para detalhar". | Existe: "Neste talhão", uma linha por camada com "Ver …" (`:1079-1092`). Falta: o **motivo principal** no topo e o estado "pior entre camadas" de verdade (hoje só O.S., irrigação e mancha entram, `:714-719`; pragas e carência não). | A do motivo principal, delegada à camada dele. Conflito: se o motivo é "a liberar", a primária é **abrir a liberação** da ordem (CMD-06 no próprio painel da camada O.S., com confirmação), nunca "liberar" direto do Integrado. Sem verde quando o motivo é só informativo. |
| **Satélite** | Rampa de vigor do PRD 74.7.2. Padrão "Talhão" (relativo) na visão da fazenda contraria a skill §1 e gera D9. | "P2 · 80 ha · milho V10" / "NDVI 0,76 · bom · cena 21/09 · nuvem 1 %" / "−4 % desde 16/09". | Existe: cena, nuvem, estado, 5 índices, pixel, mancha (`:997-1016`). Falta: histograma de classes, série do índice (EX-42) e inspetor de pixel no hover. | Pela skill §3.6: Normal → "Ver histórico" (link, BOT-08), Atenção → "Ver manchas", Crítico → "Programar vistoria" (verbo do BOT-03 e do AG-01; a skill e o pedido dizem "Criar vistoria"; **divergência de verbo**, resolver por fonte: PRD AG-01 usa "Programar vistoria → FO-03"). Hoje o verde fica dentro do item da mancha (`:1009`, `:1014`): BOT-01 diz que bloco de conteúdo não tem verde. Mover para o rodapé. |
| **Solo** | Classes da tabela ou relativo; legenda relativa com 4 rótulos vazios (`:1327`). | "T2 · 298 ha" / "V % 48 · abaixo da meta 60 · laudo LAU-… de 12/08" / "pior ponto: K 0,9 mg/dm³". | Existe: laudo, coleta, situação, uso no plano, V/K/CTC, mapa de calor e 6 piores pontos (`:1336-1359`). Falta: link de módulo na faixa (D24) e valores na legenda relativa. | "Registrar laudo" ou "Validar laudo" (comando). "Abrir laudo" é navegação: vira link (BOT-08), não verde (`:1361-1364`). |
| **Pragas e doenças** | 8 classes (`:867`). | "P4 · 73 ha · mamão" / "ácaro 23 % das folhas · 1,5× o NC · vistoria 19/09" / "defensivo há 4 dias" (selo) / risco 7 dias só se o Raio-X publicar (fronteira abaixo). | Existe: vistorias do período, ritmo, protocolo, próximo passo da pior vistoria (`:1051-1064`). | "Decidir controle" quando acima do NC (`G/mip.js:149`): a decisão emite receituário e a O.S. **nasce em A liberar**; aprovar e liberar continuam individuais na O.S. (DEC-1610-03, CMD-06). Sem conflito. |
| **Ordens de serviço** | Fases, Avanço, Atrasos, Impedimentos, Insumos. "A liberar" e "Encerradas" com a mesma cor (`:808`). | "T1 · 312 ha" / "3 ordens: 1 em execução (190/350 ha), 1 a liberar" / "OS-0421 · dia 4 de 7". | Existe: cartões das O.S. e "Próximo passo" com comando e confirmação (`:942-973`). Falta: "Nova O.S. neste talhão" com o talhão (D8). | O comando do próximo passo da ordem escolhida (Liberar, Aprovar, Iniciar…), **uma ordem por vez**, com confirmação; já é o que existe. Conflito a evitar: "Abrir O.S." como verde (é navegação, BOT-08). O pedido sugere "Abrir O.S."; proponho manter o comando como verde e "Abrir ordem ›" como link, como hoje. |
| **Irrigação** | Hoje ou Balanço hídrico (`:868-869`). Azul "irrigando" igual a "liberadas" e "em controle". | "P2 · 80 ha" / "déficit 11,2 mm · 10,8 mm a 62 % · medido 06:00" / "última rega 22/09". | Existe: balanço, lâmina, percentímetro, ordens (`:1040-1049`). | Ação do setor (`xi.ac`), hoje link para IR (`:1078`). Se for "Programar irrigação", é verde; se só abre, link. Irrigação só com água **não** passa pelo agrônomo (DEC-2609-10): o cartão não mostra "a liberar" para água. |
| **Estádio** | Pré-plantio, vegetativo, reprodutivo, produção contínua (amarelo), granação (laranja), colhido (`:866`). Amarelo e laranja aqui não são alerta (D15). | "C1 · 38 ha · café Catuaí 144" / "granação · 7 anos · colheita prevista 20/05/2027". | Existe: ocupação e cultivos (`:994-995`). | Sem primária (consulta). "Ver calendário"/"Abrir no Planejar safra" é link. Hoje não há verde: correto. |
| **Colheita e produtividade** | Situação (5 classes) ou Carência e destino. Produtividade só no rótulo; "programada" azul aqui e lima em Pragas e Irrigação. | "T2 · 298 ha" / "57 sc/ha · −7 % da meta · romaneios conferidos" ou "carência até 30/09". | Existe: previsão, colhido, produtividade, próximo passo (`:1393-1400`). Falta: escala por sc/ha ou % da meta, ícone "Colheita" nos botões (D25), link de módulo em Situação (D24). | A do próximo passo da Previsão e colheita (`colhAc`), já verde. "Abrir romaneios" é link. Na carência, "Ver restrição" é navegação: link, não verde (`:1250-1256`). |
| **Custos** | "Previsto R$/ha": tudo azul (`:850`); "Realizado × previsto": ok / até +10 % / acima. | "T4 · 204 ha" / "R$ 2.050/ha · +18 % do previsto · parcial: 30 de 204 ha" / "reparo OM-0233". | Existe: previsto, realizado provisório, conferido, cobertura (`:1028-1038`). | Sem primária (consulta). "Ver custo do talhão" é link. Falta escala de cor divergente com valores (§5). |

**Fronteira com o Raio-X do alvo (frente paralela, `docs/integracao/V73/RAIOX-ALVO/`, não reescrita aqui):**

- O mapa entrega a **peça**: talhão como botão, cartão, seleção, legenda, painel e o selo "manejo recente".
- O Raio-X entrega o **conteúdo** do painel sem seleção na camada Pragas e doenças, a aba de risco e a linha "Próximos 7 dias".
- O cartão de hover mostra o risco em 7 dias **só se** o Raio-X publicar um resultado para aquele talhão e data; o mapa não calcula risco.
- A linha do tempo arrastável é do EX-42 (`docs/integracao/V71/EX-42.md`, decisão 1: "tempo único"); o mapa só recolore pela data.
- "EX-43" citado no pedido não existe no repositório (procurei em `git ls-files` de b989864, de `origin/main` c8274086 e da worktree do Raio-X). Pendência na §9.

## 4. Motor de mapa: um só (MapLibre) × SVG

**Recomendação:** um motor só, **MapLibre GL**, empacotado (sem CDN em tempo de execução), com uma **camada de botões acessíveis** por cima do canvas. Em duas etapas, para não quebrar 15 testes de uma vez.

| | MapLibre (um motor) | SVG (um motor) | Dois motores com uma peça comum (hoje + peça) |
|---|---|---|---|
| Pan, roda, pinça, enquadrar, tela cheia | prontos | a fazer (D4) | a fazer só no SVG |
| Imagem de satélite e pixels | pronto (`lgCanvas`, `G/areas/inicio.py:584-588`) | possível (canvas no `foreignObject`), lento com muitas células | duas implementações |
| Desenhar e importar talhão | pronto (`G/talmapa.js`) | não existe | só na Lagoa Grande |
| Máquinas (MAPA-FROTA) | `Marker` com `<button>` | grupo focável | **duas** implementações (o MAPA-FROTA já prevê as duas) |
| Acessibilidade | canvas não é acessível: exige a camada de botões | elementos no DOM, mais simples | duas regras |
| Sem internet | exige empacotar (hoje CDN, D26) | funciona | depende do motor |
| Tamanho | 954.516 B (249.690 B em gzip -9), executado | ~0 | soma |
| WebGL | exige (SwiftShader nos testes; aparelho antigo sem WebGL fica sem mapa) | não exige | — |
| Software real (PRD 67.3: tiles e camadas; skill de satélite §5: MapLibre/Leaflet) | caminho natural | não escala para milhares de talhões e tiles | — |

**Custo e risco:**

- **Empacotar:** no protótipo, publicar `maplibre-gl.js` (BSD-3-Clause, executado: `package.json` 5.9.0) como arquivo de apoio do artefato, com caminho relativo; no PWA, precache do Workbox. Custo P. Sem gasto.
- **Santa Rita sem polígono real:** a geometria esquemática vai para GeoJSON num quadro de coordenadas **sintético e rotulado** ("Demonstrativo"), como a Lagoa Grande sintética já faz (`M.lg.rot` = "Demonstração sintética", executado). O desenho atual não é proporcional à área (T1: 1,13 ha por célula; C1: 0,22 ha; executado sobre `M.px`): a migração é a chance de corrigir a escala do desenho, mantendo o rótulo "Demonstrativo".
- **Decisão anterior:** o NAV registrou "X-CAD-9 · não aplicar: unificar apagaria função" (`docs/navegacao/CONSOLIDADO.md:161`). A função que se perderia (pixels, mapa de calor do solo, mancha) já existe no caminho MapLibre (`lgCanvas`, `lgSoloCanvas`, `:584-596`). Proponho rever o X-CAD-9 com essa prova; é decisão técnica dos agentes.
- **Testes:** 15 arquivos de teste, mais o `engine.py` e o `g2lib.js`, usam `svg [role=button]` (executado: `grep -l` em `G`). Por isso a F1 cria o seletor estável `[data-talhao]` nos dois desenhos; a troca de motor (F3) vem depois, sem reescrever os testes de novo.
- **Licença dos dados:** sem dado real no protótipo (a Lagoa Grande publicada é sintética; o KML do proprietário só existe no Mac). Imagem real futura: Copernicus Sentinel-2 é aberta com atribuição ("Contains modified Copernicus Sentinel data"); mapa-base de terceiros pago ou com termos de uso fica com o proprietário (§7). Glyphs/fontes de rótulo do MapLibre: evitar a camada `symbol` com servidor de fontes; rótulos ficam na camada de botões (acessível e sem serviço externo).
- **Carga:** `lagoa_s2.json` tem 2.586.169 B (938.180 B em gzip), sem indicador de carga (D26). Proposta: barra de carga do DS no cartão do mapa e "Pixels do satélite: carregando…" na legenda.

## 5. Paleta semântica única e segura para daltonismo

**Medido (executado, `reproducao/cores.txt` e `reproducao/busca_paleta.txt`):**

- Hoje, na deuteranopia, a menor distância de cor (CIEDE2000) entre classes usadas juntas é **1,0** (azul "em controle" × roxo "reprodutivo"); lima × amarelo dá 3,6; vermelho × verde-escuro, 6,8. Na protanopia, lima × amarelo dá 2,5. Abaixo de ~10, duas manchas pequenas se confundem.
- "Não se aplica" (`#E4E9DF`) contra o fundo (`#E3EADB`): **1,00:1**. Cinza × não se aplica: 1,28:1. A listra da hachura contra a base: 1,69:1.
- A mesma cor recebe até 13 significados entre as camadas (cinza e amarelo; `reproducao/cor_significado.txt`, executado sobre a fonte).
- Rampa de vigor do PRD 74.7.2: na deuteranopia, "atenção" × "médio" ficam a 2,8; na protanopia, a 1,4.

**Proposta (tokens por significado, não por cor; tons perto dos da 74.7.3, separados por luminosidade):**

| Token | Hex | Usos (exemplos) | × fundo | Texto sobre |
|---|---|---|---:|---|
| `mapa.estado.impede` | `#89291A` | impedida, conflito, acima do NC, atrasada, falta comprar, carência em curso, acima de +10 %, déficit ≥ 15 mm | 7,12:1 | branco 8,77:1 |
| `mapa.estado.urgente` | `#CD6F1D` | foco, vence hoje, déficit 10–15 mm | 2,90:1 | escuro 4,70:1 |
| `mapa.estado.atencao` | `#EAC453` | perto do NC, até 3 dias, pendência com dono, decisão do agrônomo pendente, a conferir, até +10 % | 1,36:1 | escuro 9,99:1 |
| `mapa.estado.em-dia` | `#4CA96B` | abaixo do NC, no prazo, em dia, estoque cobre, no previsto, déficit < 5 mm | 2,37:1 | escuro 5,74:1 |
| `mapa.estado.em-curso` | `#275A86` | em execução, irrigando, em colheita, em controle | 5,90:1 | branco 7,26:1 |
| `mapa.estado.programado` | `#A0C4E3` | liberada, programada (vistoria, rega, colheita) | 1,48:1 | escuro 9,17:1 |
| `mapa.estado.concluido` | `#73827A` | encerrada, colhida | 3,28:1 | branco 4,04:1 |
| `mapa.neutro` | `#C9CFCB` | pré-plantio, sem previsto, sequeiro, fase A liberar (ETP-01: etapa futura neutra) | 1,29:1 | escuro 10,59:1 |
| `mapa.sem-leitura` | hachura `#C9CFCB` + listra `#6B6B6B` | nuvem, sem imagem, sonda sem dado, estimado | listra × base 3,37:1 (hoje 1,69:1) | — |
| `mapa.nao-se-aplica` | `#E4E9DF` liso + contorno tracejado `#6B776F` | sem ordem, sem pendência, fora do filtro, colhido no Estádio | contorno × fundo 3,80:1 (hoje 1,00:1) | — |

- **Menor distância CIEDE2000 entre os 7 estados:** 20,5 (visão normal), 13,6 (deuteranopia), 14,9 (protanopia), 15,1 (tritanopia). Hoje: 1,0 na deuteranopia.
- **Segunda codificação:** o texto do rótulo (já existe), mais um selo de forma só para `impede` (ícone de alerta) e `em-curso` (▶). A hachura fica exclusiva de "sem leitura".
- **Estádio** sai da paleta de estado (amarelo e laranja deixam de significar fase): `mapa.fase.vegetativo #438F82`, `reprodutivo #9C86CF`, `producao-continua #2A4E75`, `enchimento-maturacao #8C6638`, `pre-plantio #C9CFCB`; menor distância nas 4 visões: 18,5.
- **Camadas quantitativas:** Custos "Realizado × previsto" em escala divergente azul–laranja com 5 classes e valores na legenda (≤ −10 %, −10 a −0,5 %, no previsto, até +10 %, > +10 %); "Previsto R$/ha" e Colheita (sc/ha ou % da meta) em escala sequencial de um tom com 5 classes por quebras da fazenda. Valor sempre no rótulo e no cartão.
- **Rampa de vigor:** mantida (regra de satélite do proprietário, PRD 74.7 e skill §2). Compensação: valores na legenda sempre, inspetor de pixel no hover, contorno da mancha. Oferecer uma paleta alternativa para daltonismo como preferência do usuário é decisão do **proprietário** (§7).
- **Contraste do rótulo:** o halo branco do PRD 74.7.5 continua obrigatório. Sobre `impede` e `em-curso`, texto escuro sem halo mede 1,91:1 e 2,31:1; com o halo, vale a medida do PRD (16,75:1).
- Isto muda a tabela do PRD 74.7.3: **proposta**, para o Codex registrar ou recusar; a escolha de acessibilidade é material → **Gemini via Codex**.

## 6. Componente comum de mapa

**Fronteira.** O componente é dono de: geometria e desenho, rótulos (número e até 2 linhas, regra por tamanho), cartão de hover/foco, seleção (um ou vários), teclado, busca "Ir para talhão", legenda que trabalha, ferramentas (zoom, enquadrar, tela cheia), estado na URL, toque, camadas sobrepostas (máquinas), nome acessível e cores por token. **Não** é dono de: regras de cada camada (`mip.js`, `irrigacao_estado.js`, `custo_dominio`, `solo.js`, `dados_carencia.py`), conteúdo do painel e primária (da tela), linha do tempo (EX-42), Raio-X, dados da frota (`frota.js` do MAPA-FROTA), desenho e importação (`talmapa.js`, como ferramenta), comandos (`osc_*`).

**API mínima (proposta, JS do protótipo; o mesmo contrato vai para `packages/ui` no software real):**

```text
mapa = MapaTalhoes.monta(el, {
  fazenda, motor: 'maplibre' | 'svg',                 // 'svg' só até a F3
  talhoes: [{ id, nome, apelidos[], ha, geom, rotuloEm }],
  camada: { classe(id) → { token, rotulo, valor, unidade, estado, data, fonte },
            cartao(id) → [linha1, linha2, linha3?], selos(id) → [{ icone, nome }], legenda() → [{ token, texto }] },
  selecao: { modo: 'um' | 'varios', ids, aoMudar(ids) },
  aoAbrir(id),                                        // painel (da tela)
  sobreposicoes: [{ id: 'frota', marcadores: [{ id, pos, icone, rotulo, nomeAcessivel, aoAbrir }] }],
  url: true                                           // #faz=&lay=&t=&dt=
})
→ mapa.selecionar(ids) · mapa.focar(id) · mapa.enquadrar(ids, motivo) · mapa.destacarClasse(token) · mapa.redesenhar() · mapa.destruir()
```

- Seletor estável para testes: `[data-talhao="<id>"]` no botão de cada talhão, nos dois desenhos.
- `enquadrar` exige `motivo` ('busca', 'link', 'enquadrar', 'voltar'): sem motivo, não move a câmera (regra da §2).

**Telas:**

| Tela | Uso | F1? |
|---|---|---|
| IN-04 | completo | sim |
| CD-01 (visão Mapa) | só leitura + clique abre o **detalhe** CD-01det, não o formulário (`G/areas/cad_fazendas.py:424`, `:449`); mesmos nomes e cores | não (MUX-F4) |
| CD-01det | o polígono do próprio talhão (hoje `clip-path` igual para todos, `:624-634`) | não (MUX-F4) |
| PL-06 | só leitura da proposta de parcelas | não (MUX-F4) |
| CA-01 | sai o SVG fixo (`G/areas/campo.py:154`, textos escritos à mão); fica "Ver no mapa ›" para a camada Ordens de serviço | não (MUX-F4; corte) |
| AG-01det | pontos pelo GPS dentro do polígono (hoje pelo índice, `G/areas/agronomia.py:834`) | não (MUX-F4) |
| MB-06 | minimapa da rota, sem internet | não (depois da F3, que empacota o motor) |
| MAPA-FROTA | usa `sobreposicoes`; com a F1 antes, as máquinas entram uma vez só | ver §8 |

**Fora da F1:** retângulo/laço, comparação de duas datas lado a lado, "você está aqui", minimapa do app, troca de motor da Santa Rita, tiles vetoriais e mapa-base real.

## 7. Riscos e decisões materiais

| # | Risco (dano) | Mitigação | Quem decide |
|---|---|---|---|
| R1 | Fazenda padrão inacessível por teclado e leitor de tela: a pessoa não chega ao painel (D1) | F1: camada de botões e busca | agentes |
| R2 | Contraste "Talhão" chama de "Falha" o pixel mais baixo de um talhão sadio; o painel diz "Vigor alto" para o mesmo pixel (D9, §R M17): vistoria desnecessária ou confiança errada | F2: padrão Fazenda/Absoluto na visão da fazenda; nomes relativos ("mais baixo do talhão"); painel na mesma escala | agentes (skill §1 e EX-42 já mandam) |
| R3 | Cor com significados diferentes e paleta que some na deuteranopia (D14, D15) | F2: tokens por significado e segunda codificação | **Gemini via Codex** (acessibilidade) |
| R4 | Mapa padrão some sem internet ou com o CDN fora (D26) | F3: empacotar | agentes |
| R5 | Trocar o motor quebra 15 testes e o MAPA-FROTA em andamento | `[data-talhao]` na F1; troca na F3; sequência com o MAPA-FROTA | Codex (checkpoint) |
| R6 | Um dedo arrasta o mapa em vez de rolar a página no celular (D29) | gesto cooperativo (dois dedos para mover) no estreito | agentes |
| R7 | Ação em lote virar aprovação em lote | lote só cria rascunhos/programação; aprovar e liberar seguem individuais (DEC-1610-03, CMD-06); teste que tenta liberar em lote e é recusado | já decidido (proprietário) |
| R8 | Painel sem seleção (visão da fazenda) contraria DEC-2609-06 | manter fechado sem seleção, ou abrir como exceção registrada | **Gemini via Codex** (fluxo) |
| R9 | Teclado: uma parada de Tab com setas × todos os talhões no Tab | protótipo das duas com leitor de tela | **Gemini via Codex** (acessibilidade) |
| R10 | Paleta alternativa para daltonismo na rampa de vigor muda a regra de satélite do proprietário | oferecer como preferência, padrão inalterado | **proprietário** |
| R11 | "Você está aqui" usa a posição do aparelho (dado pessoal no app de campo) | fora da F1; só no app, com aviso e só para a própria pessoa | **proprietário** (e jurídico do cliente no software real) |
| R12 | Mapa-base ou imagem real de terceiros com custo ou termos | fora; usar só dado sintético e Sentinel-2 aberto | **proprietário** |
| R13 | PRD desatualizado: diz "barra vertical" (IN-04, 74.5.22) e o MAP-03 de 16/10 levou a barra para o alto, na horizontal | registro do Codex na próxima versão do PRD | Codex |
| R14 | Teste com usuários (UX-13; DEC-1610-02: depois de melhorar os módulos) não feito: "tempo até achar o talhão" fica sem medida real | medir interações agora; tempo com 3 a 5 pessoas quando liberado | proprietário (liberação) |

## 8. Fatias propostas (sugestão; o Codex decide e registra)

Ordem vigente de autoria em `inicio.py`: MAPA-FROTA → EX-42 → SOLO-FOLHA-NIVEIS → SAF-MAPA (`docs/integracao/V71/MAPA-FROTA.md:691`), com teto de 3 frentes (AGENTS §3.6). Sugiro encaixar a MUX-F1 **antes** da F1 do MAPA-FROTA, porque as máquinas usariam a mesma camada de botões e as `sobreposicoes`, em vez de dois desenhos.

| ID | Resultado útil · persona | Arquivos prováveis | Aceite observável | Medida antes → meta depois |
|---|---|---|---|---|
| **MUX-F0 · Destinos e nomes** (P, pode ir junto de qualquer frente que já mexa em `inicio.py`) | Gestor e agrônomo não perdem o contexto ao sair do mapa | `G/areas/inicio.py` (FL, `panelTal`, `MAPVALS`), `G/talmapa.js` (`#talhao=`), `G/areas/cad_fazendas.py` (nome exibido) | "Nova O.S. neste talhão" abre a O.S. com `#tal=`; `#talhao=PV05` com contexto da Santa Rita abre a Lagoa Grande e seleciona; "Ver histórico" some até o EX-42; Solo e Colheita com atalho; ícone em Colheita; um nome exibido por pivô ("P1"), apelidos na busca | Destinos sem contexto: 4 (M11, M15) → 0; nomes por pivô: 3 → 1 exibido; contraprova: o render 1792184197-5a81 reprova |
| **MUX-F1 · Encontrar e ler o talhão** (M) | Gestor e agrônomo, no computador e no celular, acham um talhão e leem o essencial sem abrir nada | novo `G/mapa_comum.js` (cartão, seleção, teclado, busca, URL, botões `[data-talhao]`), `G/areas/inicio.py` (adaptadores SVG e MapLibre, painel por cima do mapa, legenda), `G/g2lib.js` (variante do `g2dica`), `G/engine.py` (alvo de 44 px nas ferramentas); testes `mapa_comum_unit.js`, `mapa_ux_test.py`; migração dos 15 testes de `svg [role=button]` para `[data-talhao]` | Hover ou Tab num talhão mostra o cartão em < 100 ms, sem corte, com valor, estado e data; Enter abre o painel com foco no título; Esc fecha e devolve o foco; "/" + "P12" + Enter seleciona; URL guarda camada e talhão; legenda não bloqueia clique; a 390 px o painel abre como folha visível | Lagoa Grande: 0 de 23 pivôs alcançáveis por teclado → todos, com ≤ 4 teclas ("/", nome, Enter); Santa Rita: 28 Tabs até o 1º talhão → 1 parada de Tab; cliques até o detalhe do pior talhão: 2, mas só para quem já sabe qual é → 2 pela legenda, sem procurar; dica no hover e no foco: 0 de 9 camadas → 9; alvos < 44 px a 390: 19 → 0; salto ao abrir o painel: 175–192 px → 0; Esc fecha: não → sim |
| **MUX-F2 · Cor que diz a verdade** (M) | Agrônomo e gestor, inclusive com daltonismo, leem a classe certa e comparam talhões | `G/areas/inicio.py` (`LCOR_OP` → tokens, `legend`, `cls0`, Satélite e Solo), `G/ui37.py` (`LCOR`), `G/engine.py` (tokens); testes de cor (DS-65 a DS-68) | Contraste padrão Fazenda/Absoluto na visão da fazenda; nomes relativos sem "falha"; painel na mesma escala do mapa; hachura e contorno do "não se aplica"; Estádio sem amarelo/laranja; Custos e Colheita com escala e valores; legenda com contagem e área | Menor CIEDE2000 na deuteranopia: 1,0 → ≥ 13; "não se aplica" × fundo: 1,00:1 → contorno ≥ 3:1; significados por cor: até 13 → 1; pixel "Falha" no mapa e "Vigor alto" no painel (M17) → a mesma classe nos dois |
| **MUX-F3 · Um motor** (G) | Todos, com ou sem internet, no computador e no celular | `G/areas/inicio.py` (Santa Rita em GeoJSON sintético, canvas de pixels reaproveitando `lgCanvas`), arquivo de apoio `maplibre-gl.js` no artefato, `G/talmapa.js`; testes de mapa | Mapa carrega sem acesso ao CDN; tela cheia nas duas fazendas; pan, pinça e enquadrar; rótulos sem sobreposição a 390 px; gesto cooperativo no celular; indicador de carga dos pixels | Pares de rótulos sobrepostos a 390: 11 → 0; rótulo da Santa Rita a 390: 4,4 px → ≥ 12 px; arrasto de 1 dedo: move o mapa → rola a página; mapa sem acesso ao CDN: falha → carrega |
| **MUX-F4 · Mesmo mapa em toda tela** (M) | Quem cadastra, planeja e confere vê os mesmos talhões, nomes e cores | `G/areas/cad_fazendas.py`, `G/areas/planejamento.py`, `G/areas/campo.py` (corte do SVG fixo), `G/areas/agronomia.py` | CD-01 Mapa abre o CD-01det; CD-01det desenha o polígono do talhão; CA-01 leva à camada O.S.; AG-01det põe os pontos pelo GPS | Desenhos da Santa Rita: 4 → 1 |

Medidas comuns a todas: contagem de cliques e teclas no mesmo cenário antes/depois (AGENTS §3.3), capturas a 1440 e 390 px, leitor de tela (árvore de acessibilidade do Chrome) e a bateria do módulo. "Tempo até achar o talhão" só com usuários (UX-13, R14); até lá, mede-se "interações até achar" (busca × varredura).

## 9. Três listas, suposições e pendências

**Aplicar**
1. Camada de botões acessíveis + busca "Ir para talhão" na Lagoa Grande: hoje a fazenda padrão não é operável sem mouse (D1).
2. Cartão de hover/foco < 100 ms pela variante do `g2dica`: o pedido central do proprietário, sem componente novo.
3. Regra única da câmera ("só por pedido"): concilia "não muda de zoom sozinho" com busca e "Ver no mapa".
4. Contraste Fazenda/Absoluto na visão da fazenda e painel na mesma escala: tira a contradição do D9.
5. Tokens por significado, hachura e contorno do "não se aplica": medidos, com 13,6 de distância mínima na deuteranopia (hoje 1,0).
6. Legenda que trabalha (contagem, área, clique filtra): leva ao pior talhão em 2 ações sem tela nova.
7. Destinos com contexto (`#tal=`, `#talhao=` trocando a fazenda, histórico real ou sem link).

**Deixar de fora (com gatilho)**
1. Laço de seleção: volta se um caso de uso real não couber no retângulo.
2. "Você está aqui": volta com a decisão do proprietário sobre posição no app.
3. Paleta alternativa da rampa de vigor: volta com a decisão do proprietário.
4. Comparar duas datas lado a lado: volta com o EX-42 (tempo único).
5. Painel sem seleção com a visão da fazenda fora de Pragas e doenças: volta com o parecer do Gemini (R8).

**Cortar**
1. Mapa SVG fixo do CA-01 (textos escritos à mão, `G/areas/campo.py:154`): vira link para a camada Ordens de serviço.
2. "Medir" que só repete a área do cadastro (D19): ou mede de verdade (F3, com o MapLibre) ou sai; na F1, renomear para "Área e perímetro" e mostrar no painel.
3. Rótulo "10 m" do pixel da Santa Rita (D10): a célula do desenho não tem 10 m.
4. "Todas" no filtro de fazenda enquanto só uma fazenda é desenhada por vez (D6): mostrar as duas ou tirar a opção.
5. O "Ver histórico" para o AG-06 de pragas (D7) até o EX-42 entregar a série do índice.

**Suposições**
- S1: o runtime `x-dc` repassa eventos a elementos SVG como o React (o código do mapa supõe isso; os cliques reproduzidos na §R funcionaram). Gatilho: falha de evento no SVG em outro navegador.
- S2: dados sintéticos bastam para todas as medidas desta avaliação. Gatilho: medida que dependa de geometria real (área por pixel, colisão de rótulos com talhões pequenos).
- S3: o Chrome headless com SwiftShader representa o desempenho de um computador comum só de forma grosseira; os tempos de carga da §R são indicativos. Gatilho: medida de desempenho para aceite (INP/LCP do software real).

**Pendências**
- P1: "EX-43" (risco em 7 dias) não existe no repositório. Gatilho: o Codex indicar o arquivo ou registrar o ID.
- P2: UX-13 aparece só em `docs/design-system/diretrizes-ux.md:44` (análise externa), não no PRD. Gatilho: registro do ID pelo Codex.
- P3: crítica do Raio-X do alvo (frente paralela) pode mudar o conteúdo do painel de Pragas e doenças. Gatilho: entrega da crítica.
- P4: decisões R3, R8 e R9 (Gemini via Codex) e R10–R12 (proprietário).

## 10. As 10 heurísticas (NN/g), no mapa atual

| Heurística | Achado principal | D |
|---|---|---|
| 1. Visibilidade do estado | Sem indicador de carga do mapa e dos pixels; "Medir" responde num aviso de 4,5 s | D19, D26 |
| 2. Correspondência com o mundo real | "Falha" para o pixel mais baixo de um talhão sadio; "10 m" numa célula de ~1 ha; três nomes para o mesmo pivô | D9, D10, D27 |
| 3. Controle e liberdade | Esc e clique no fundo não desmarcam; zoom sem pan prende as bordas | D4, D16 |
| 4. Consistência e padrões | A mesma cor com até 13 significados; quatro desenhos da Santa Rita; clique abre formulário no CD-01 e painel no IN-04 | D15, §2 do anexo |
| 5. Prevenção de erros | Link "Ver histórico" leva a outro assunto; `#talhao=` falha em silêncio | D7, D18 |
| 6. Reconhecer em vez de lembrar | Sem busca de talhão; legenda sem valores no contraste Talhão | D9, opor. 1 |
| 7. Flexibilidade e eficiência | Sem atalhos de teclado no mapa; sem URL para voltar ou compartilhar | D17, D21 |
| 8. Estética e minimalismo | Rótulos de 4,4 px no celular e 11 pares sobrepostos; chip da mancha cortado; legenda cobre talhões | D12, D23, D28, N4 |
| 9. Reconhecer, diagnosticar e recuperar erros | "Mapa real indisponível… Recarregue a página" sem alternativa (lista) | D26 |
| 10. Ajuda e documentação | Fonte e regra na dica ⓘ: bom; falta "clique no talhão para ver detalhes" na etiqueta de modo (PRD 74.5.24) | — |

## R. Reprodução (executado)

**Ambiente (executado em 17/10/2026, 00:15–00:35 UTC):** espelho local do render publicado, servido só para leitura; ele foi trocado às 00:16:19 UTC (M0–M2 na versão 1792184197-5a81; o resto na composição 05947ad, com os arquivos do mapa iguais, `reproducao/espelho_troca.txt`); Chrome headless `/tmp/cloudchrome/chrome` com SwiftShader (`CDP_GL=1`), perfil e porta próprios, depois da linha FIM da bateria q30 e com nenhum outro Chrome principal aberto. MapLibre 5.9.0 **carregou do CDN** neste ambiente (pronto em 3,4 s). Dados sintéticos.

**Comandos e saídas (em `reproducao/`):**

| Arquivo | O que mede |
|---|---|
| `repro_mapa.py` | script único; `MEDIDAS=M9b,M10b` roda só as escolhidas |
| `repro_mapa.json` / `.txt` | M0–M18 (passada principal, 19 medidas, 0 erros) |
| `repro_mapa_b.json` … `repro_mapa_h.json` | M3b, M9b, M10b, M18b, M10c, M18c, M7b, M19, M19b, M20 (repetições com outro método) |
| `m18c_T7_satelite_1440.png` | recorte de 185 × 258 px do T7 (17,8 KB) |
| `cores.py` / `cores.txt`, `busca_paleta.py` / `.txt` | contraste WCAG, daltonismo (Machado 2009) e CIEDE2000 |
| `cor_significado.py` / `.txt` | significados por cor nas legendas (estático) |
| `fonte_publicado.py` / `.txt` e `fonte_publicado_05947ad.txt` | publicado = fonte de b989864 e tradução das linhas do anexo; o mesmo no espelho novo |
| `espelho_troca.txt` | hora da troca do espelho e prova de que os arquivos do mapa não mudaram |

**Medidas "antes":**

| # | Medida | Resultado |
|---|---|---|
| M0 | Carga do mapa padrão | Pronto em 3,4 s; sem erro de JS. Canvas: nome "Map", `role=region`, `tabindex=0`. Marcador do pivô: `role=img`, sem `tabindex` |
| M1 | Tab na Lagoa Grande (1440) | 140 Tabs: o 28º chega ao canvas "Map"; depois, só ferramentas e zoom. **Nenhum pivô focável** |
| M2 | Tab na Santa Rita (1440) | 1º talhão no **28º Tab**; os 8 em sequência (28º a 35º; T7 no 34º). Nome: "T1: OS-0430 a liberar" (sem área nem cultura). A árvore do Chrome expõe os 8 botões |
| M3/M3b | Dica no hover e no foco | Nenhuma nas duas fazendas. O headless responde `(hover: hover)` falso: o realce `brightness(.92)` não pôde ser visto aqui (código em `G/engine.py:1091`). No Satélite, o grupo de pixels (opacidade 1) fica depois do polígono |
| M4 | Cliques até o detalhe do pior talhão (ordem SEV do protótipo) | **2 em 18 de 18** (camada + talhão). Até decidir: 3 em 11; sem primária em 7 (Integrado, Estádio e Custos nas duas fazendas; Satélite na Lagoa Grande). Primárias de navegação: "Abrir laudo", "Abrir OS-0507", "Acompanhar OM-0233" |
| M5 | Alvos (1440 fino; 390 toque) | 1440: nenhum abaixo de 24 px. 390: **19 abaixo de 44 px** (ferramentas 31, zoom 36, fechar 30, segmentados 25, ações do painel 29,6); abas e atalho com 44 |
| M6 | Legenda sobre o mapa | 1440: cobre 9–11 % de T4, T3, T7 e C1; o clique no centro dela não chega ao mapa. 390: 13 % (Santa Rita) e 17 % (Lagoa Grande) da altura do mapa |
| M7/M7b | Rótulos da Santa Rita | Escala 0,976 a 1440 e **0,292 a 390**: número 11,7 px, rótulo **4,4 px**, subtítulo 3,8 px. Cortado: só o chip da mancha, em todas as variantes do Satélite |
| M8 | Rótulos da Lagoa Grande | 1440 (zoom 12,95): 0 sobreposições. 390 (zoom 12,01): **11 pares** sobrepostos entre 23 |
| M9/M9b | Arrasto de um dedo a 390 | O gesto sintético de rolagem não moveu nada (M9, inconclusivo). Com eventos de toque (M9b): **o mapa move e a página não rola**; o mesmo gesto na faixa da camada rola 165 px |
| M10 | Esc, fundo, endereço, foco | Painel continua aberto depois de Esc e de clique no fundo; `location.hash` vazio antes e depois; o foco fica no polígono clicado |
| M10b/c | Toque a 390 | O toque emulado gerou `pointerdown`/`touchend` e **nenhum `click`, nem numa aba comum**: limitação da ferramenta, não do produto. Com clique de ponteiro no mesmo ponto, o painel abre com o topo em **y = 825** numa janela de 844 |
| M11 | `#talhao=PV05` com o contexto na Santa Rita | Fica na Santa Rita, sem painel e sem aviso |
| M12 | Medir | Aviso "Medição · T1: 312 ha · perímetro ≈ 7,1 km (geometria do cadastro)"; a região viva recebe o mesmo texto; o aviso sumiu antes de 5 s |
| M13 | Abas das camadas | Seta → não move o foco; `aria-controls` 0; `tabpanel` 0 |
| M14 | Tela cheia e "Todas" | Sem "Tela cheia" na Lagoa Grande. Na Santa Rita: diálogo sem `aria-modal`, foco fora dele, Esc não fecha. "Todas" mostra só o SVG da Santa Rita e "Boa Vista sem geometria" |
| M15 | Atalhos e destinos | Solo e Colheita sem atalho; Satélite → `AG-06.dc.html` (faixa e painel); "Nova O.S. neste talhão" → `OS.dc.html` sem talhão; botões da Colheita sem ícone |
| M16 | Lagoa Grande: opacidade | Mapa com 0 e 0,55; amostra da legenda com 1; sem hachura no MapLibre |
| M17 | Satélite, contraste padrão | Padrão "Talhão"; legenda só com nomes sem talhão escolhido. Um pixel **vermelho ("Falha") do P1 aparece no painel como "NDVI 0,82 · Vigor alto"**; com o talhão escolhido, a legenda vai de "Falha < 0,826" a "Vigor alto ≥ 0,858" |
| M18b/c | Mancha do T7 | 0 px² de sobreposição com o rótulo; o chip mostra "mancha 1,2" (FO de 21 px, conteúdo de 37 px) |
| M19 | Tempos (indicativos, SwiftShader) | Santa Rita, clique → painel: 295, 94, 94, 87 e 79 ms. Troca de camada até 2 quadros: 73–137 ms (Santa Rita) e 81–933 ms (Lagoa Grande; Ordens de serviço 933). Lagoa Grande, clique → painel: **não medido** (o método falhou; ver `repro_mapa_f.json` e M19b) |
| M20 | Salto ao abrir o painel | Mapa de 1306 → 921 px; T4 anda 175 px e PV05, 192 px; sob o ponteiro ficam T3 e PV06 |

**Itens "[confirmar no navegador]" do anexo:** D12 (encolhe: sim; corta: não, salvo o chip), D28 (sim, 11 pares a 390 px), D29 (sim, com eventos de toque) e rótulos do canvas do MapLibre (sim: "Map", em inglês, `role=region`).

**Limites:** sem leitor de tela real (só a árvore de acessibilidade do Chrome); sem usuário (UX-13); hover CSS não observável no headless; tempos medidos com WebGL por software.
