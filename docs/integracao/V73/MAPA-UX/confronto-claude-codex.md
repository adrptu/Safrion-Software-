# MAPA-UX · Confronto das avaliações Claude × Codex (passo 2)

Pedido do proprietário de 16/10/2026: "Mapa da fazenda com UX e UI de excelência" ([pedido.md](pedido.md), [anexo-analise.md](anexo-analise.md)). Passo 2 do pedido: divergência se resolve por fonte ou reprodução; o Gemini real entra só em decisão material de fluxo ou acessibilidade, pelo conector do Codex; o Codex registra o desenho final e as fatias no checkpoint.

- **Avaliações confrontadas:**
  - Claude: `6c03d7e:docs/integracao/V73/MAPA-UX/avaliacao-claude.md` (citada como "Claude l.N");
  - Codex: `b39dccbb3cec06b4549895740144d4419df2a019:docs/integracao/V73/MAPA-UX/avaliacao-codex.md`, branch `codex/mapa-avaliacao-20261016` (citada como "Codex l.N");
  - comentário do Codex no PR #47, [6226913160](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6226913160) (16/10, 23:53 UTC);
  - retorno do Codex sobre a avaliação do Claude, [6227708290](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6227708290) (17/10, 01:02 UTC), respondido ponto a ponto na §8.
- **Bases (executado, `reproducao/confronto/fontes_confronto.txt` §0):**
  - pedido e anexo: `529adf7` (`docs/integracao/V73/pedidos-1610/`); os 11 arquivos conferem com o `SHA256SUMS`; as cópias desta pasta só acrescentam a linha de origem;
  - fonte do protótipo: `47ccc1d` (`claude/v44-v69-mapa`), com os 9 arquivos do mapa iguais aos de `b989864`, a base das duas avaliações;
  - render: composição `05947ad`, em `/tmp/claude-0/int90/.../_render` (só leitura);
  - PRD, DECISIONS e design system: `origin/main` `c827408`.
- **Autor:** Claude. **Revisor:** Codex. **Registro do desenho e das fatias:** só o Codex (passo 3).
- **Estado:** especificado. As reproduções da §R foram **executadas** (estáticas). O navegador não foi usado, porque nenhuma divergência precisou dele. Não simulei o Codex nem o Gemini, e nada foi enviado.

```text
ID / resultado útil / persona: MAPA-UX passo 2 / confronto ponto a ponto das duas avaliações, com cada divergência resolvida por fonte, reprodução ou pergunta ao Gemini / gestor, agrônomo, PCP, operador no celular
Requisitos do PRD e fora do escopo: IN-04, 67, 74.5.22–26, 74.7, MAPUX-04/06, RF-WRK-004, DEC-2609-06/11, DEC-0910-01 (BOT/SEL/VIS), DEC-1610-02/03; fora: registrar checkpoint, enviar ao Gemini, implantar
Autor / revisor / integrador: Claude / Codex / Codex (registro)
Base / arquivos sob responsabilidade: 6c03d7e × b39dccb, fonte 47ccc1d, PRD c827408 / docs/integracao/V73/MAPA-UX/confronto-claude-codex.md e reproducao/confronto/
Aceite e comando de verificação: §R; python3 -I -B reproducao/confronto/linhas_citadas.py <G>; sh reproducao/confronto/fontes_confronto.sh <repo> <G> <render>; python3 -I -B reproducao/confronto/mb_mapa.py <render>; python3 -I -B reproducao/confronto/contraste_pares.py <render>; python3 -I -B reproducao/confronto/manifesto_medidas.py reproducao; python3 -I -B reproducao/confronto/alvos48.py reproducao
Estado / impedimento / próximo passo: entregue ao Codex para o registro (§7, §8) e, depois de resolvidas as divergências por fonte, para o pacote do Gemini (§5)
```

## Resumo

- **61 pontos confrontados:** 23 convergentes, 25 complementares e 13 divergentes.
- **As 13 divergências:**
  - 10 se resolvem por fonte, e 5 delas são a mesma regra (BOT-03/08: navegação não é primária);
  - 1 se resolve em parte por fonte e o resto vai ao Gemini (teclado e leitor de tela);
  - 1 se resolve por critério técnico, com gatilho (motor único);
  - 1 é de fatiamento: há proposta, e o Codex registra.
  - Nenhuma precisou de navegador.
- **O ponto que mais muda o desenho:** os dois deixaram passar a contradição das fontes sobre a lista.
  - Lista alternativa obrigatória: MAPUX-06, RF-WRK-004 (P0), "Ver dados" no 74.5.24 e 74.5.26.
  - A atualização v3.9 do cap. 67 (decisões do proprietário de 25 e 26/09) diz "Não há tabela nem lista abaixo do mapa" (`PRD.md:9516`).
  - Por eliminação, a lista é uma **visão alternativa no mesmo bloco** ("Ver dados", Lista | Mapa), com os mesmos filtros, a mesma seleção e o mesmo painel.
  - O Codex viu a necessidade (Codex l.10), sem a fonte; o Claude não a viu.
- **Comentário do Codex 6226913160:** 7 afirmações conferidas, todas confirmadas. A do D25 está certa e incompleta (§1).
- **Retorno do Codex 6227708290 (§8):** 8 pontos. 5 aceitos, 3 aceitos com ajuste ("fora do filtro", painel por cima do mapa, e ordem com a embalagem), nenhuma divergência.
  - Reproduzi os 4,04:1 e 4,15:1 do "concluído" e achei mais pares abaixo do limite: texto sobre preenchimento, contorno de seleção e anel de foco.
  - A correção verificável é uma placa ~~sólida~~ branca a 90 % atrás do rótulo (Δ2 17/10) e anéis em duas cores.
  - O delta mínimo foi aplicado na avaliação do Claude, com o marcador "Δ 17/10"; os brutos não mudaram.
  - Um manifesto liga cada medida ao render certo: o M3 cruza a troca do espelho.
- **Δ2 17/10 (Codex, 6227901968):** 6 ajustes de documento, com o texto anterior riscado.
  - O cartão: a WCAG 1.4.13 não fixa os 120 ms. "0 ms" quer dizer sem espera programada, e o aceite declara o método e o limite da medida.
  - A placa a 90 % tem limite de 13,424:1 sobre qualquer fundo; os 14,39:1 valem só para a Santa Rita testada.
  - O caso de borda do painel segue a regra do Codex.
  - G2 e G3 foram reescritas.
  - O D26 usa o gatilho do Codex.
  - As divergências com o PRD estão listadas para a conferência final (§9), sem editar o PRD.
- **Conclusões do Claude corrigidas:** 15 itens, 14 de conteúdo e 1 de citação, com 2 linhas (§4).
- **Gemini via Codex:** 3 perguntas em rascunho (§5). O Codex só empacota depois de resolver as divergências por fonte; nesta passada não há consulta.
- **Proprietário:** 3 decisões, mais 1 que só aparece se a frente do Raio-X pedir (§6).
- **Fatias:**
  - MAPA-FROTA F1 primeiro (autoria vigente), depois MUX-F0 → MUX-F1, por contrato de arquivos e base (§8.2);
  - em seguida F2 ler o talhão → F3 mexer no mapa → F4 outras telas;
  - embalagem e motor único ficam para decisão posterior, com gatilho.

## 1. Conferência do comentário do Codex (6226913160)

| # | Afirmação | Conferência | Fonte |
|---|---|---|---|
| 1 | D25: o ícone Colheita existe em `engine.ICONS` e na barra estática; falta no ICN das ações; não refazer o ícone | **Confirmada e incompleta.** O ícone existe (`engine.py:22`) e a barra das 9 funções usa esse ícone (`areas/inicio.py:1628-1629`). Falta `'Colheita'` no `ICN` (`:911`), que marca o ícone da ação, e também no `ICS` (`:1445`), que desenha o ícone no painel. O reparo cabe nas duas listas | `fontes_confronto.txt` §6 |
| 2 | O pedido principal prevalece sobre as sugestões do anexo: sem os 300 ms, sem recentralização automática, 48 px no toque | **Confirmada.** Pedido: cartão "em menos de 100 ms" (l.123), "Zoom ou recentralização automática sem pedido" em NÃO FAZER (l.136), "48 px ou mais" (l.67). Anexo: "após cerca de 300 ms" (opor. 2), "enquadrar o selecionado" (opor. 12), "44 px no toque" (opor. 14) | §3 |
| 3 | CD-01 abre o formulário | **Confirmada.** `cad_fazendas.py:424` e `:449` chamam `g2open`, que abre o formulário (`g2lib.js:193-205`). Só a linha da fazenda tem atalho próprio (`.dr`, `cad_fazendas.py:356`) | leitura |
| 4 | CA-01 tem o literal 190/350 | **Confirmada:** `campo.py:156-157` ("Em execução · 190/350 ha" e `wr=int(316*190/350)`) | leitura |
| 5 | AG-01det posiciona os pontos pelo índice | **Confirmada:** `agronomia.py:834` (`x=60+i·880/(n−1)`, `y` alterna 70 e 230) | leitura |
| 6 | Visual, desempenho, leitor de tela e usuários ficaram NÃO executados | **Confirmada para o Codex** (Codex l.3 e l.91). O Claude executou no navegador (M0–M20: árvore de acessibilidade do Chrome, tempos indicativos com SwiftShader). Leitor de tela real e usuários não foram executados por nenhum dos dois | Claude §R |
| 7 | MB não foi auditado integralmente | **Confirmada.** Complementei agora, em leitura estática: nenhuma das 15 telas MB tem mapa. Em 11 delas, o aviso de carência pode levar ao IN-04 ("Ver restrição no mapa") | `mb_mapa.txt` |

**Citações de linha (executado):**
- Das 109 citações das duas avaliações, 106 batem com a fonte vigente.
- As 3 deslocadas são do Codex e o conteúdo se confirma: D3 cita `:632` (a linha é `:633`); D19 cita `:602` e `:1142` (as linhas são `:606` e `:1143`).
- Detalhe em `linhas_citadas.txt`.

## 2. Tabela de confronto

Legenda das colunas:
- **Classe:**
  - **conv**: mesmo diagnóstico e solução compatível;
  - **compl**: mesma direção, e um traz prova ou regra que falta ao outro, ou fecha o que o outro deixou pendente;
  - **div**: posições incompatíveis no diagnóstico, na solução ou na ordem.
- **Como:** a fonte com arquivo e linha, a reprodução, ou "→ Gemini".

### 2.1 D1–D30

| # | Tema | Claude | Codex | Classe | Resolução proposta | Como |
|---|---|---|---|---|---|---|
| D1 | Lagoa Grande sem teclado nem leitor de tela | l.57 (S2; M1: 0 de 23 pivôs em 140 Tabs) | l.18 | conv | Um botão por talhão num grupo com nome, mais a lista alternativa (T4) e a busca | `inicio.py:633`, `:646`; M1 (Claude, executado) |
| D2 | `role=img` envolvendo botões | l.58 (parcial: o Chrome expõe os 8) | l.19 | compl | `role=group` com nome; talhão como botão | `PRD.md:14462` (74.5.26: "grupo com nome acessível… cada talhão é um botão") |
| D3 | Sem hover; realce sob os pixels | l.59 | l.20 | conv | Cartão do mapa (variante do `g2dica`); realce acima dos pixels | `linhas_citadas.txt` (Codex: +1 linha) |
| D4 | Zoom sem pan na Santa Rita | l.60 (pan no MapLibre, F3) | l.21 | conv | Pan no SVG sem esperar o motor; "Ajustar à fazenda" e "Voltar à seleção" | `PRD.md:14447` (74.5.24, "Ausentes no protótipo") |
| D5 | Sem tela cheia na Lagoa Grande | l.61 | l.21 | conv | Tela cheia nas duas, com Esc e foco | `inicio.py:1191` |
| D6 | "Todas" mostra só a Santa Rita | l.62 e l.304 ("mostrar as duas ou tirar a opção") | l.59 (não remover a visão global) | **div** | **Manter "Todas"**: a lista alternativa mostra todas as fazendas; o mapa mostra as que têm geometria, com o aviso das que não têm | Fonte: RF-WRK-004 (`PRD.md:2475`); DEC-2609-11, "Mapa: Fazenda (filtro)" e estado vazio com ação (`PRD.md:12479`); "uma ou várias fazendas" (`PRD.md:7`). O Claude retira "tirar a opção" |
| D7 | "Ver histórico" leva ao AG-06 | l.63 (M15) | l.22 (destino "pendente") | compl | Sem link até o EX-42 entregar a série do índice; nunca o AG-06 | Reprodução estática: `AG-06.dc.html` tem `<title>Eficácia e histórico</title>` (`fontes_confronto.txt` §7) |
| D8 | "Nova O.S. neste talhão" sem talhão | l.64 | l.23 | conv | Levar `#tal=` | `processo_os.py:969-976` |
| D9 | Contraste "Talhão" com nomes absolutos | l.65 (M17) | l.11 e l.24 | compl | Padrão Absoluto ou Fazenda na visão da fazenda; Talhão só com talhão escolhido e nomes relativos. O painel mostra a classe da escala ativa e o valor absoluto rotulado, o que atende "mesma escala" (Claude) e "declarar contexto" (Codex) | Skill de satélite §1 (`SKILL.md:18-19`) |
| D10 | Pixel anunciado como "10 m" | l.66 (1,13 ha por célula, executado) | l.25 ("não comprova") | compl | Tirar "10 m" | Cálculo do Claude sobre `M.px` |
| D11 | Mancha só no T7, sobre o rótulo | l.67 (não sobrepõe; o chip é cortado) | l.26 (não medido) | compl | Mancha vinda do dado; chip fora do rótulo | M18b/c (Claude, executado) |
| D12 | Rótulos cortados e encolhidos | l.68 (4,4 px a 390) | l.26 (não medido) | compl | Rótulos em px fixos, fora da escala do SVG | M7/M7b |
| D13 | Opacidade da Lagoa Grande ≠ legenda | l.69 | l.27 | conv | Mesma opacidade e hachura nos dois | `inicio.py:645` |
| D14 | "Não se aplica" da cor do fundo | l.70 (1,00:1) | l.28 | conv | Contorno tracejado; "fora do filtro" com rótulo | `inicio.py:430` |
| D15 | Cor com vários significados; daltonismo | l.71 (ΔE00 mínimo de 1,0 na deuteranopia) | l.28 (não reproduziu) | compl | Tokens por significado | → Gemini G1 |
| D16 | Esc e fundo não desmarcam; pixel no Satélite | l.72 | l.9 e l.29 (Esc por nível; preservar rascunho) | compl | Clique = talhão em todas as camadas; pixel só no modo "Inspecionar"; Esc fecha o modo, depois a seleção, sem apagar o desenho | `inicio.py:1143-1146` |
| D17 | Seleção e câmera fora da URL | l.73 | l.30 | conv | URL com fazenda, camada, data e talhão | SEL-02 (DS `README.md:25`) |
| D18 | `#talhao=` não troca a fazenda | l.74 (M11) | l.31 | conv | Trocar a fazenda; aviso se não achar | `talmapa.js:167`; SEL-02 |
| D19 | "Medir" não mede | l.75 (a região viva anuncia) | l.32 (Codex: −4 e −1 linha) | compl | Resultado no painel; "Área e perímetro" até medir de verdade | `g2lib.js:1130`; `linhas_citadas.txt` |
| D20 | Painel sem foco nem Esc; a 390 px nasce fora da tela | l.76 | l.33 | conv | Foco no título, Esc e folha inferior | `inicio.py:1162` |
| D21 | Abas sem setas nem `aria-controls` | l.77 | l.34 | conv | Setas e Home/End | `inicio.py:1634` |
| D22 | Alvos de toque | l.78 e l.125 (44 px pelo DS-15) | l.12 e l.35 (48 px) | **div** | **48 px no toque, só nos controles do mapa**, sem mudar o token global; os 44 px do DS-15 continuam como piso. Hoje, abaixo de 48 px a 390: de 21 a 29 dos 29 controles medidos. Para talhões menores que 48 px na tela, a alternativa é a lista e a busca (NC5) | Fonte: pedido l.67; DS-15 é limite mínimo (`PRD.md:14112`). O zoom de 44 px do 74.5.24 (`PRD.md:14444`) entra no registro do Codex. Recontagem: `alvos48.txt` |
| D23 | Legenda bloqueia o clique | l.79 (contêiner `pointer-events: none`, itens `auto`, recolhível) | l.60 (mover ou recolher, sem desligar a legenda interativa) | compl | Legenda recolhível com estado lembrado; fora do desenho (`padding` da câmera); contêiner sem eventos e itens com eventos | `PRD.md:14454` (74.5.25) |
| D24 | Solo e Colheita sem link de módulo | l.80 | l.36 | conv | Link de módulo nas 9 | `inicio.py:1127` |
| D25 | Ícone Colheita nas ações | l.81 (ICN e ICS) | l.61 (existe em ICONS; falta no ICN) | compl | `'Colheita'` no `ICN` e no `ICS`; nenhum ícone novo | `fontes_confronto.txt` §6 |
| D26 | Dependência do CDN; sem indicador de carga | l.82 (S2, na F3) | l.53; 6227708290 item 7 (embalagem é decisão posterior) | conv | Empacotar o MapLibre como arquivo de apoio, do jeito que o `lagoa_s2.json` já é. É decisão posterior e não bloqueia F0/F1, mas fica registrada com gatilho próprio por ser S2 na fazenda padrão (§8, item 7) | `fontes_confronto.txt` §7 (fetch relativo do `lagoa_s2.json`; MapLibre do CDN) |
| D27 | Três nomes por pivô | l.83 | l.62 | conv | Um nome exibido; ID interno intacto; apelidos na busca | `cad_fazendas.py:232` |
| D28 | Colisão de rótulos na Lagoa Grande | l.84 (11 pares a 390) | l.53 e l.63 (a medir) | compl | Regra por tamanho em tela | M8 (Claude, executado) |
| D29 | Arrasto de um dedo no celular | l.85 (M9b) | l.37 (pendente) | compl | Ver G3 | → Gemini G3 |
| D30 | "Selecionar área" sugere laço | l.86 | l.38 | conv | "Selecionar vários" | `inicio.py:1174`, `:1527` |

### 2.2 Achados novos do Claude (N1–N5)

| # | Tema | Claude | Codex | Classe | Resolução proposta | Como |
|---|---|---|---|---|---|---|
| N1 | Abrir o painel encolhe o mapa; o talhão salta 175–192 px | l.92 | — | compl | Painel por cima do mapa | M20; `PRD.md:9538` ("sem deslocar a página involuntariamente") |
| N2 | Verde em navegação ("Abrir laudo", "Abrir OS-0507", "Acompanhar OM-0233") | l.93 | l.77–85 (põe "Ver …" na coluna de ação primária) | **div** | Navegação vira link; verde só para comando | Fonte: BOT-03 ("Nunca … 'Ver …' como primário") e BOT-08 (DS `README.md:12`, `:17`; DEC-0910-01) |
| N3 | Canvas com o nome "Map", em inglês | l.94 | — | compl | Nome em pt-BR, ou o nome do grupo de talhões | M0 |
| N4 | Chip "mancha 1,2" sem "ha" | l.95 | — | compl | Chip com largura pelo texto | M18c |
| N5 | O Integrado ignora pragas e carência | l.96 | l.77 (empate estável; não comparar números incomparáveis) | compl | Estado ordinal por camada (ordem SEV) em todas as camadas, empate estável e motivo visível; o Codex registra a precedência | `inicio.py:176-177`, `:714-719` |

### 2.3 Por camada

| # | Camada | Claude | Codex | Classe | Resolução proposta | Como |
|---|---|---|---|---|---|---|
| C1 | Integrado | l.136 | l.77 | compl | Primária delegada à camada do motivo; nunca liberar a partir do Integrado | DEC-1610-03; CMD-06 |
| C2 | Satélite | l.137 ("Ver histórico" como link; "Programar vistoria") | l.78 ("Ver qualidade", "Ver histórico", "Criar vistoria" como primárias) | **div** | "Ver histórico", "Ver manchas" e "Ver qualidade" (acréscimo do Codex) viram links. Verde só "Programar vistoria", com mancha ou estado crítico | Fonte: BOT-03/08. **Verbo:** BOT-03 manda "Programar" quando a finalidade é agendar uma execução, e o protótipo já usa "Programar vistoria" (9 vezes; nenhum "Criar vistoria"). O PRD IN-04 (`PRD.md:409`), a skill (`SKILL.md:58`) e o EX-43 dizem "Criar vistoria": o Codex alinha o texto no registro |
| C3 | Solo | l.138 (Registrar ou Validar laudo; "Abrir laudo" como link) | l.79 ("Ver análise" ou "Registrar laudo"; interpolação como estimativa) | **div** | Verde só com comando (Registrar, Validar ou Corrigir laudo); "Ver análise" vira link; a interpolação é rotulada "estimativa" (Codex) | BOT-03/08 |
| C4 | Pragas e doenças | l.139 | l.80 ("Vistoriar quando dado insuficiente"; risco só com modelo) | compl | "Decidir controle" acima do NC; "Programar vistoria" com dado insuficiente; risco em 7 dias só se o Raio-X publicar | EX-43 (`529adf7`, excelência l.590–600) |
| C5 | Ordens de serviço | l.140 | l.81 | conv | Próximo comando da ordem escolhida, uma por vez, com recibo; "Abrir ordem ›" como link | DEC-1610-03; BOT-08 |
| C6 | Irrigação | l.141 | l.82 | conv | Ação do setor: comando é verde, abrir é link; água sem agrônomo | DEC-2609-10 |
| C7 | Estádio | l.142 (sem primária) | l.83 ("Ver calendário contextual") | **div** | Sem verde; "Ver calendário" como link; fases com paleta categórica | BOT-03 |
| C8 | Colheita e produtividade | l.143 | l.84 (não comparar sc/ha e t/ha; não ocultar carência) | compl | Próximo passo da Previsão e colheita (comando); escala por cultura e unidade ou "% da meta"; carência visível | BOT-08 |
| C9 | Custos | l.144 (sem primária) | l.85 ("Ver custo do talhão"; ausência ≠ zero) | **div** | Sem verde; link; escala só com base comparável; ausência nunca vira zero (Codex) | BOT-03 |

### 2.4 Pontos transversais

| # | Tema | Claude | Codex | Classe | Resolução proposta | Como |
|---|---|---|---|---|---|---|
| T1 | Atraso do cartão | l.107 (80 ms no ponteiro; 0 no foco e entre vizinhos) | l.7 (sem atraso artificial); 6227708290 item 3 (medir do evento à pintura) | **div** | ~~**0 ms para abrir**, medido do evento à pintura (§8, item 3); mantém o fechamento de 120 ms do `g2dica` e o "0 ms entre vizinhos"~~ **Δ2 17/10:** abre **sem espera programada** (não é pintura instantânea nem latência zero), medido pelo método e com o limite da §8, item 3. Ao sair, vale o timer atual do `g2dica` (120 ms), que a WCAG não fixa | Fonte: aceite "menos de 100 ms" (pedido l.123). Dado do próprio Claude: um `setState` leva 79–295 ms (M19); 80 ms de espera deixariam 20 ms para pintar. `g2lib.js:1192` (120 ms) e `:1227` |
| T2 | Câmera | l.112 | l.8 | conv | Câmera só se move por pedido explícito: busca, "Ajustar à fazenda", "Voltar à seleção", "Ver no mapa" | Pedido l.136; `PRD.md:9538` ("centralizando apenas quando solicitado") |
| T4 | Lista alternativa | l.121 (só busca) e l.82 (lista como contingência, na F3) | l.10 (lista e busca: caminho essencial), l.47 | **div** | **Visão "Ver dados" (Lista \| Mapa) no mesmo bloco, na F1**: mesmos filtros, seleção e painel; ordem pela gravidade da camada; "Localizar no mapa" por linha | Fonte: MAPUX-06 (`PRD.md:9549`), RF-WRK-004 P0 (`:2475`), 74.5.24 (`:14447`), 74.5.26 (`:14462`). A v3.9 (`:9516`) proíbe lista abaixo do mapa: sobra a visão alternativa. Hoje o render não tem nada disso (0 "Ver dados abaixo", 0 "Localizar no mapa", 0 `<table`) |
| T5 | Cartão sem ação | l.110 | l.12 | conv | Nenhuma ação no cartão | Pedido §5 |
| T6 | Painel sem seleção (visão da fazenda) | l.116 e l.260 (→ Gemini) | — | compl | **Não vai ao Gemini.** O painel abre só com seleção. O "ranking" é a legenda que trabalha mais a visão Lista | Fonte: DEC-2609-06 (`PRD.md:12475`), 74.5.26 (`:14463`), v3.9 (`:9516`). No pedido, isso é referência que "não é requisito" (l.9). Exceção só para o Raio-X, e decide o proprietário (§6, O4) |
| T7 | Modelo de teclado | l.123 e l.261 (uma parada de Tab com setas; → Gemini) | l.10 e l.44 (lista e busca; semântica) | **div** (parcial) | O pedido já diz "Tab entra no mapa; setas andam entre talhões vizinhos" (l.63), e o 74.5.26 pede um botão por talhão. Resta o padrão para o leitor de tela | Fonte em parte; o resto → Gemini G2 |
| T8 | Seleção de vários | l.118 | l.93 (laço fora) | conv | Shift + clique e "Selecionar vários"; o lote cria rascunhos e nunca aprova nem libera | DEC-1610-03 |
| T9 | CD-01, CD-01det, PL-06, CA-01, AG-01det | l.239–243 | l.64–68 | conv | CD-01 abre o detalhe; CD-01det mostra a geometria cadastrada ou "sem geometria"; PL-06 identificado como esquema; CA-01 vira link para a camada O.S.; AG-01det sem posição de GPS fingida | `cad_fazendas.py:424`, `:449`, `:546`; `campo.py:156-157`; `agronomia.py:834` |
| T10 | Geometria da Santa Rita no motor único | l.173 (GeoJSON sintético; "corrigir a escala do desenho") | l.10 e l.65 (não inventar geometria) | **div** | Não redesenhar: a mesma forma sintética, com o selo "Demonstrativo"; a área exibida é a área cadastrada | Fonte: "Geometria sintética no modo demo é identificada" (`PRD.md:5091`) |
| T11 | Telas MB | l.244 (MB-06 depois do motor) | l.69 (não auditado; não bloquear o IN-04) | compl | Sem mapa MB novo nesta frente. O IN-04 a 390 px é o mapa que o campo vê | `mb_mapa.txt` (executado) |
| T12 | EX-43 | l.152 e l.313 ("não existe no repositório") | — | compl | O EX-43 é o Raio-X do alvo: risco em 7 e 14 dias e "Criar vistoria (rascunho, nunca O.S.)". A fronteira do Claude (o mapa não calcula risco) continua; a P1 fecha | `529adf7`, `excelencia-pedido-ex01-48.md:590-600` |
| T13 | 10 heurísticas | §10 | l.89 | conv | — | — |
| T14 | Teste com usuários (UX-13) | l.266 | l.91 | conv | Não executado; vale a DEC-1610-02 (depois dos demais módulos) | DECISIONS, DEC-1610-02 |

### 2.5 Motor, paleta, componente e fatias

| # | Tema | Claude | Codex | Classe | Resolução proposta | Como |
|---|---|---|---|---|---|---|
| M | Motor | §4 (MapLibre único na F3; rever o X-CAD-9) | l.10, l.46 e l.93 (opção de arquitetura; testar antes) | **div** | F1–F4 independem do motor; ~~empacotar já (D26).~~ **Δ2 17/10:** D26 com o gatilho registrado pelo Codex (§8, item 7). Unificar só com prova de paridade (pixels, solo, mancha, rótulos, testes) e contrato; o X-CAD-9 só se revê com essa prova | Critério técnico dos agentes; `CONSOLIDADO.md:161` |
| P | Paleta | §5 | l.45, l.47 e l.83; 6227708290 item 4 | compl | Tokens por significado; Estádio com paleta categórica. Nada se aplica antes de revisar os pares reais (texto, seleção e foco sobre o preenchimento com opacidade); ΔE00 não certifica acessibilidade (§8, item 4) | `contraste_pares.txt`; depois → Gemini G1 |
| Cmp | Componente comum | §6 (API) | l.73 (lista e mapa, a mesma coleção) | compl | A API ganha a visão Lista e o `[data-talhao]` nos dois desenhos; as sobreposições (frota) entram pelo mesmo contrato | 74.5.26; SEL-01 |
| F | Fatias | §8 | l.42–47 | **div** | §7 deste documento | Proposta; o Codex registra |

## 3. Completude

### 3.1 Só o Claude viu

- N1 a N5.
- As medidas M0–M20.
- A paleta medida (CIEDE2000 e simulação de daltonismo).
- A API do componente.
- A relação com o MAPA-FROTA.
- "Você está aqui" como dado pessoal.
- A atribuição do Copernicus.
- `prefers-reduced-motion`.
- Os contornos de foco e de seleção iguais.
- As fronteiras com o EX-42 e o Raio-X.
- O PRD ainda dizer "barra vertical" depois do MAP-03 (R13).

### 3.2 Só o Codex viu

- Esc por nível sem apagar o rascunho de desenho.
- "Ver qualidade" para cena inválida.
- Programar vistoria quando o dado é insuficiente.
- Integrado sem comparar números incomparáveis, com empate estável.
- Interpolação do solo rotulada como estimativa.
- Ausência ≠ zero em Custos.
- Não comparar sc/ha com t/ha.
- Não renomear IDs persistidos.
- Lista quando não há geometria.
- PL-06 e AG-01det identificados como esquema.
- Não bloquear o IN-04 por um mapa MB novo.
- Anexos conferidos pelo `SHA256SUMS`.
- Não fabricar entrevistas nem contagens.

### 3.3 Nenhum dos dois viu (executado aqui, leitura estática)

| # | Achado | Prova | Efeito no desenho |
|---|---|---|---|
| NC1 | As fontes da lista se contradizem: a lista alternativa é obrigatória, mas a v3.9 proíbe lista abaixo do mapa. O PRD já registra "Ver dados", "Ajustar à fazenda", "Voltar à seleção" e "Ampliar mapa" como ausentes no protótipo | `PRD.md:9516`, `:9549`, `:2475`, `:14447`, `:14462`; render sem nada disso | T4: visão "Ver dados" na F1; nomes do PRD no lugar de "Enquadrar" |
| NC2 | Os talhões do SVG não têm `aria-pressed`: o leitor de tela não sabe qual está selecionado (o pedido pede `aria-pressed`, l.48) | `inicio.py:1411` (`fontes_confronto.txt` §6) | F1; S3 (estado não exposto) |
| NC3 | Arrastar (pan) e gesto de dois dedos pedem alternativa com um ponteiro e sem arrasto (WCAG 2.5.7 e 2.5.1). A linha do tempo "arrastável" do EX-42 também precisa dela | "sem depender exclusivamente de gestos" (`PRD.md:9532`) | G3; ~~Aproximar/Afastar, "Ajustar à fazenda", "Voltar à seleção", busca e lista cobrem o caso~~ **Δ2 17/10:** zoom, ajuste e busca não garantem pan até qualquer ponto; o G3 verifica controles direcionais por clique, sem barra permanente nova |
| NC4 | O cartão precisa cumprir a WCAG 1.4.13: o ponteiro pode ir do talhão ao cartão sem que ele suma, e Esc fecha. ~~O `g2dica` já faz isso (fecha 120 ms depois de sair do gatilho e da dica)~~ **Δ2 17/10:** a 1.4.13 não fixa tempo: pede que o cartão continue visível enquanto o talhão **ou** o próprio cartão tiver hover ou foco, e que possa ser dispensado. O `g2dica` atende hoje com um timer de 120 ms ao sair do gatilho e da dica e com Esc; os 120 ms são da peça, não da WCAG ([W3C, Understanding 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html)) | `g2lib.js:1192` | Reforça "variante do `g2dica`, não componente novo"; é o que concilia "some ao sair" com o 1.4.13 |
| NC5 | Talhão menor que 48 px na tela: com a escala do anexo (cerca de 16 m/px a 390 px), o menor pivô (29,92 ha) teria uns 39 px de diâmetro (**estimativa, não medida**) | Anexo D28; Claude M8 | Os 48 px valem para controles; o talhão pequeno usa o controle equivalente (lista e busca, exceção do 2.5.8) |
| NC6 | Modo de alto contraste (forced-colors): a peça só trata esse modo na barra de visões; ninguém verificou o preenchimento do SVG nele | `engine.py:1444` (1 regra); `areas/inicio.py` sem nenhuma | Pendência: medir com emulação na F2 |
| NC7 | Nenhuma tela de campo tem mapa (0 de 15). Em 11, o aviso de carência leva ao IN-04 | `mb_mapa.txt` | Os defeitos a 390 px (D20, D22, D23, D28, D29, N1) pesam para o operador |
| NC8 | O nome acessível do PRD ("{talhão}: {estado}", 74.5.26) é mais curto que o do pedido ("P4, 73 ha, mamão em produção, …") | `PRD.md:14461`; pedido l.72 | Adota-se o do pedido, mais novo e específico; o Codex atualiza o 74.5.26 |
| NC9 | Foco encoberto (WCAG 2.4.11): a legenda e a folha inferior podem cobrir o talhão focado | não medido | Entra no aceite da F3 |
| NC10 | O protótipo já pinta valor estimado como "sem leitura": na Irrigação, "≈ 10,8 mm · estimado" usa a mesma hachura de "nuvem · sem leitura". O 74.7 não põe "estimado" na hachura, e "estimado" é etiqueta de origem do valor | `inicio.py:842` × `:832`, legenda `:868-869`; `PRD.md:14667`, `:14196`; DS-66 (`:14721`) | F2: cor da classe do valor mais a etiqueta "≈ estimado" (§8, item 5) |
| NC11 | Com a opacidade real, o contorno de seleção `#15201A` não chega a 3:1 sobre "impede" e "em curso" (2,42 e 2,96). O anel de foco `#1E7A4C` não chega sobre 5 dos 9 preenchimentos. Na Lagoa Grande (0,55 sobre a imagem), nem o texto branco nem o escuro passam em todos os tokens | `contraste_pares.txt` C e D | F2: seleção e foco em duas cores; placa ~~sólida~~ branca a 90 % atrás do rótulo nas duas fazendas, com o limite de 13,424:1 para qualquer fundo (§8, item 4; Δ2 17/10) |

## 4. Conclusões do Claude que mudam

1. **Atraso do cartão:** de 80 ms para **0 ms** (T1). **Δ2 17/10:** "0 ms" quer dizer sem espera programada; não se declara latência zero (§8, item 3).
2. **Alvo de toque no mapa:** de 44 px para **48 px** (D22).
3. **Lista alternativa:** de "busca, com lista como contingência na F3" para a **visão "Ver dados" na F1** (T4, NC1).
4. **Painel sem seleção:** sai do pacote do Gemini; as fontes resolvem (T6).
5. **"Todas":** não se tira a opção (D6).
6. **Empacotar o MapLibre (D26, S2):** deixa de ser F3. Proposta deste confronto: F1. Depois do retorno 6227708290, é decisão posterior que não bloqueia F0/F1, com gatilho próprio (§8, item 7).
7. **Santa Rita no motor único:** sem redesenhar "na escala"; a forma sintética continua, com o selo (T10).
8. **EX-43:** existe em `529adf7`; a pendência P1 fecha (T12).
9. **Gesto no celular (D29):** sai de "decisão dos agentes" e vai ao Gemini, com a alternativa sem arrasto (G3, NC3).
10. **Citações:** o `clip-path` do CD-01det está em `cad_fazendas.py:546` (o Claude citou `:624-634`, que é o `geoVals`); o "PV01" está em `:232` (o Claude citou `:231`, o círculo).
11. **Nomes dos comandos de câmera:** "Ajustar à fazenda" e "Voltar à seleção" (74.5.24), no lugar de "Enquadrar".

Pelo retorno 6227708290 (detalhe na §8; delta "Δ 17/10" na avaliação):

12. **Contraste:** "concluído" com 4,04:1 (branco) e 4,15:1 (escuro), os dois abaixo de 4,5. Seleção e foco abaixo de 3:1 em parte dos preenchimentos. O halo da avaliação só é sólido no número. Correção: placa ~~sólida~~ branca a 90 % (limite de 13,424:1 sobre qualquer fundo; Δ2 17/10) e anéis em duas cores (item 4).
13. **"Estimado"** sai de "sem leitura"; as bases de Custos e Colheita passam a ser comparáveis (mesma cultura, safra e unidade, ou "% da meta") (item 5).
14. **Painel por cima do mapa** sem `padding` automático da câmera, com os 4 critérios do Codex (item 6).
15. **Ordem:** a MUX-F1 não passa à frente da MAPA-FROTA F1 sem contrato (item 7). Rastreabilidade: o M3 cruza a troca do espelho; N5 é leitura estática; o D25 corrige só o catálogo das ações (item 8).

Continuam de pé, sem ressalva: N1–N5, os 26 D confirmados por inteiro e os 4 parciais, a paleta medida (que agora vai ao Gemini), a regra da câmera, a fronteira com o Raio-X e o EX-42, e a relação com o MAPA-FROTA.

## 5. Pacote mínimo do Gemini (rascunho; o Codex envia; nada foi enviado)

Só dados sintéticos do protótipo. Nenhum dado real, nenhum segredo.

**Estado (17/10, retorno 6227708290):**
- o Codex só empacota depois de resolver as divergências por fonte, e não há consulta nesta passada;
- o Codex lista teclado, paleta e painel como candidatos. Aqui o painel já está resolvido por fonte (T6); se o Codex discordar, a pergunta volta no formato abaixo;
- o G1 só segue depois da revisão dos pares reais (§8, item 4);
- Δ2 17/10 (6227901968): o Codex monta o pacote G1–G3 com estas correções e pede a crítica do Gemini real, sem consulta ritual.

### G1 · Cor dos estados no mapa (acessibilidade)

- **Pergunta fechada:** para que 7 estados operacionais do talhão sejam distinguíveis por quem tem deuteranopia ou protanopia (impede, urgente, atenção, em dia, em curso, programado, concluído), qual codificação adotar no preenchimento, sabendo que o rótulo do talhão já traz o estado em texto? A, B ou C.
- **Alternativas:**
  - **A.** Tokens por significado, separados pela luminosidade, com selo de forma só em "impede" e "em curso"; hachura exclusiva de "sem leitura"; "não se aplica" com contorno tracejado.
  - **B.** Manter os matizes atuais e acrescentar padrão ou textura por estado.
  - **C.** Manter a paleta atual e confiar só no texto do rótulo.
- **Posições:**
  - Claude: A (avaliação §5);
  - Codex: concorda com a direção (paleta única; Estádio categórico, Codex l.45, l.47 e l.83), sem escolher entre A, B e C.
- **Dados mínimos:**
  - Hoje (`M.lcop`): ok `#7FAE68`, good `#5F8F55`, lime `#A9C06A`, yellow `#D4B25A`, orange `#D98A4E`, red `#C8553D`, gray `#C9CFCB`, blue `#6E9FC6`, navy `#44739A`, purple `#9B8BC4`, none `#E4E9DF`; fundo `#E3EADB`. Menor ΔE00 entre classes usadas juntas: 1,0 na deuteranopia (blue × purple) e 2,5 na protanopia (lime × yellow). "None" contra o fundo: 1,00:1.
  - Proposta A: impede `#89291A`, urgente `#CD6F1D`, atenção `#EAC453`, em dia `#4CA96B`, em curso `#275A86`, programado `#A0C4E3`, concluído `#73827A`, neutro `#C9CFCB`, não se aplica `#E4E9DF` com contorno `#6B776F` (3,80:1). Menor ΔE00: 20,5 (normal), 13,6 (deuteranopia), 14,9 (protanopia), 15,1 (tritanopia).
  - Medidas do Claude: `reproducao/cores.txt` e `busca_paleta.txt`, simulação de Machado (2009). O Codex reproduziu os mínimos 13,6, 14,9 e 15,1.
  - Pares reais (`contraste_pares.txt`): o texto vai sobre placa ~~sólida (pior caso 14,39:1)~~ **Δ2 17/10:** branca a 90 %, translúcida: 14,39:1 é o menor valor só entre os fundos testados da Santa Rita; para qualquer fundo opaco, o limite é 13,424:1 (placa sobre preto, `contraste_pares_placa.txt`); nenhuma `opacity` no ancestral do texto. Seleção e foco usam duas cores. Se houver texto direto sobre o token, "concluído" passa a `#7D8C85` (4,76:1 opaco; ΔE00 mínimo de 13,5, 16,9 e 16,9). ΔE00 não certifica acessibilidade.
  - Fora da pergunta: a rampa de vigor do Satélite (decisão do proprietário, O1).

### G2 · Teclado e leitor de tela nos talhões (acessibilidade)

- ~~**Pergunta fechada:** já existe a lista alternativa (MAPUX-06) e o pedido diz "Tab entra no mapa; setas andam entre talhões vizinhos". Qual padrão usar para os talhões **no mapa**? A ou B.~~
- **Δ2 17/10, pergunta:** o pedido **exige** "Tab entra no mapa; setas andam entre talhões vizinhos; Enter seleciona; Esc fecha; '/' busca", e a lista alternativa existe (MAPUX-06). Critique a semântica e a compatibilidade com leitores de tela (NVDA, JAWS, VoiceOver, TalkBack) da proposta A. Responda: A serve como está; A serve com ajustes (quais); ou há uma alternativa compatível com o requisito (qual)?
- **Alternativas:**
  - **A.** Grupo com nome (`role=group`), um botão por talhão, com `aria-pressed` e nome completo. Uma parada de Tab (tabindex móvel); setas vão ao vizinho na direção; Home/End vão ao primeiro e ao último pelo nome. A ordem no DOM é a da lista, para o leitor de tela no modo de navegação percorrer os botões nessa ordem.
  - ~~**B.** Todos os talhões na ordem de Tab, sem setas.~~ Δ2 17/10: retirada. Não cumpre "setas andam entre talhões vizinhos" e não equivale ao requisito.
  - **Δ2, A2 (alternativa compatível, para a crítica):** o mesmo grupo de A com um papel composto que leva os leitores ao modo de foco (por exemplo `role=toolbar`). As setas seguem a ordem do nome, e a direção espacial entra como acréscimo; instruções no `aria-describedby`. Serve só de exemplo: a alternativa compatível pode ser outra.
- **Posições:**
  - Claude: A (avaliação §2, l.123);
  - Codex: lista e busca são o caminho essencial (l.10) e a semântica entra na 1ª fatia (l.44); ~~não escolheu entre A e B~~ Δ2 17/10: pede crítica da semântica e da compatibilidade da navegação por setas exigida, sem escolher entre A e A2.
- **Dados mínimos:**
  - Santa Rita: 8 talhões (T1, T2, T4, T3, T7, C1, P1, P2); hoje o 1º talhão é o 28º Tab.
  - Lagoa Grande: 23 pivôs (PV01…PV23); hoje nenhum é focável.
  - Nome proposto: "P4, 73 ha, mamão em produção, ácaro 23 % das folhas, acima do NC, vistoria em 19/09".
  - Sinal a pesar na resposta: o leitor de tela em modo de navegação captura as setas.
  - Exigência já aceita (6227708290, item 7): semântica, instruções visíveis e no `aria-describedby` do grupo, e prova com leitor de tela real; a árvore do Chrome não basta.

### G3 · Mover o mapa sem arrastar, e arrastar × rolar no celular (fluxo e acessibilidade)

- **Pergunta fechada, parte (i):** a 390 px, como conciliar mover o mapa com rolar a página? A, B ou C.
- **Alternativas:**
  - **A.** A página rola; no mapa, dois dedos movem e um dedo rola a página (gesto cooperativo), com aviso curto.
  - **B.** A tela não rola: o mapa ocupa a altura que sobra, o detalhe abre numa folha inferior por cima, e um dedo move o mapa. Quando a altura não basta (zoom do navegador, tela baixa), vale A.
  - **C.** Manter: um dedo move o mapa, e a página não rola sobre ele.
  - ~~Em todas: alternativa sem arrasto (Aproximar e Afastar, "Ajustar à fazenda", "Voltar à seleção", busca e lista; WCAG 2.5.7).~~ Δ2 17/10: zoom, ajuste e busca não garantem pan até qualquer ponto; isso é a parte (ii).
- **Posições (parte i):**
  - Claude: A na avaliação (l.85 e l.258). Neste confronto, **B com A como reserva**, porque o pedido (folha inferior, l.68), o PRD 67.2 ("painel inferior expansível", `PRD.md:9532`) e o MAP-03 (o mapa ocupa a altura que sobra) apontam para B;
  - Codex: "folha no celular" na 3ª fatia (l.46); D29 pendente (l.37); sem escolha.
- **Dados mínimos da parte (i) (Claude, executado):**
  - um dedo move o mapa e a página não rola; o mesmo gesto na faixa da camada rola 165 px (M9b);
  - o painel nasce em y = 825, numa janela de 844 (M10c);
  - nenhuma tela de campo tem mapa, e o aviso de carência leva ao IN-04 (NC7).
- **Δ2 17/10, pergunta fechada, parte (ii):** como garantir pan até **qualquer** ponto do mapa sem arrastar (WCAG 2.5.7), no computador e a 390 px, sem criar barra permanente nova? a, b ou c.
  - **a.** Quatro botões direcionais por clique (↑ ↓ ← →) dentro do grupo de zoom que já existe (74.5.24). Passo de 1/3 da área visível, nome acessível, 48 px no toque.
  - **b.** Os mesmos botões, mas só quando o mapa está ampliado além do enquadramento da fazenda.
  - **c.** Modo "Centralizar aqui": ligado, um toque ou clique centraliza o mapa no ponto (sem arrastar); Esc sai do modo.
  - Posições: Claude, **a** (não cria barra, cobre as duas fazendas e o teclado, e não disputa o clique do talhão como o **c**); Codex: considerar controles direcionais por clique, sem barra permanente nova; sem escolha.
  - Dados mínimos: o grupo "Zoom" tem hoje Aproximar e Afastar, 36 px no desktop e 44 px no toque (74.5.24). A Santa Rita só tem zoom de 1× a 2×, sem pan (D4). Na Lagoa Grande, o pan é por arrasto ou pelo teclado no canvas (MapLibre).

**Fora do pacote, com motivo:**
- painel sem seleção (T6) e lista alternativa (T4): resolvidos por fonte;
- atraso do cartão (T1) e alvo de 48 px (D22): resolvidos pelo pedido;
- verbo e verde das camadas (C2–C9, N2): resolvidos pela BOT-03/08;
- precedência do Integrado (N5): decisão de produto do Codex;
- motor (M): decisão técnica dos agentes.

## 6. Decisões do proprietário

| # | Decisão | Recomendação | Posições |
|---|---|---|---|
| O1 | Oferecer uma paleta alternativa da rampa de vigor (Satélite) para daltonismo, como preferência de cada usuário | Oferecer como preferência, mantendo o padrão do PRD 74.7 e da skill | Claude: a favor (R10). Codex: não tratou |
| O2 | "Você está aqui": mostrar a posição do aparelho no mapa (dado pessoal no app de campo) | Fora desta frente; quando entrar, só no app, com aviso e só para a própria pessoa | Claude: R11. Codex: não tratou. Hoje nenhuma tela de campo tem mapa (NC7) |
| O3 | Mapa-base ou imagem real de terceiros, com custo ou termos de uso | **Conjunta:** não contratar agora; seguir com dados sintéticos; imagem real futura do Sentinel-2, aberta, com atribuição | Claude: R12. Codex: não substituir geometrias sintéticas por inventadas (l.10) |
| O4 | **Só se a frente do Raio-X pedir:** abrir o painel sem seleção com a visão da fazenda, o que muda a DEC-2609-06 e o 74.5.26 | Manter a DEC-2609-06; a visão da fazenda fica na visão Lista e na legenda | Claude: manter (T6). Codex: não tratou |

**Já decidido, nada a pedir:**
- teste com usuários depois dos demais módulos (DEC-1610-02);
- aprovação individual (DEC-1610-03);
- 48 px (pedido de 16/10).

## 7. Fatias e ordem (sugestão; o Codex registra)

**Em que os dois concordam** (Claude §8 × Codex l.44–47; convergência declarada no 6227708290):
- acesso e contexto primeiro (botões, busca e lista acessível antes de qualquer migração de motor);
- depois, honestidade visual;
- depois, interação;
- por último, as telas dependentes;
- motor único e embalagem fora das fatias iniciais;
- nenhuma implantação antes do registro do desenho e das fatias (6226913160).

| Fatia | Conteúdo | Origem | Medida antes → meta |
|---|---|---|---|
| **MUX-F0 · Destinos, nomes e ícone** (P) | Definição executável na §8.2 | Claude F0; Codex 1 | §8.2 |
| **MUX-F1 · Achar e abrir o talhão** (M) | Definição executável na §8.2 | Claude F0 + parte da F1; Codex 1 | §8.2 |
| **MUX-F2 · Ler o talhão** (M) | <ul><li>Cartão no hover e no foco, aberto ~~em 0 ms e medido do evento à pintura~~ sem espera programada e medido pelo método da §8, item 3 (T1, NC4; Δ2 17/10)</li><li>D9, D10, D13, D14 e D15, com os pares reais revisados (NC11) e a paleta depois do G1</li><li>"Estimado" fora da hachura (NC10)</li><li>Legenda que trabalha: contagem, área, realça e filtra a lista</li><li>Painel na escala do mapa</li><li>N2 e BOT-08 nas 9 camadas; N5 com prioridade e motivo estáveis</li><li>Escalas de Custos e Colheita com base comparável</li><li>forced-colors (NC6)</li></ul> | Claude F2 + o cartão da F1; Codex 2 + o cartão do 3 | Dica no hover e no foco: 0 de 9 camadas → 9, com p95 ~~evento→pintura~~ < 100 ms pelo método da §8, item 3, que é aproximação com limite declarado (Δ2 17/10), no aparelho de referência. Pares de texto abaixo de 4,5:1 e de seleção/foco abaixo de 3:1 (`contraste_pares.txt`) → 0. Pixel "Falha" no mapa e "Vigor alto" no painel → a mesma classe |
| **MUX-F3 · Mexer no mapa sem perder o lugar** (M) | <ul><li>Painel por cima do mapa, com os 4 critérios do Codex (N1, §8 item 6)</li><li>Folha inferior (D20)</li><li>48 px nos controles do mapa (D22); legenda (D23)</li><li>Rótulos (D12, D28, N4)</li><li>Pan no SVG, "Ajustar à fazenda" e "Voltar à seleção" (D4)</li><li>Tela cheia nas duas (D5)</li><li>Gesto (D29, depois do G3)</li><li>Medir (D19)</li><li>"Selecionar vários" e Shift + clique (D30)</li></ul> | Claude F1 e F3 (partes); Codex 3 | Deslocamento do selecionado ao abrir e fechar o painel: 175–192 px → 0. Controles do mapa abaixo de 48 px a 390: de 21 a 29 → 0. Pares de rótulos sobrepostos a 390: 11 → 0 |
| **MUX-F4 · Mesmo mapa nas outras telas** (M) | CD-01, CD-01det, PL-06, CA-01 e AG-01det (T9); junto com ou depois do SAF-MAPA, que extrai a peça comum | Claude F4; Codex 4 | Desenhos da Santa Rita: 4 → 1 |
| Decisão posterior · Embalagem (D26) e motor único | Empacotar o MapLibre; Santa Rita no MapLibre sem redesenho (T10) | Claude F3; Codex: decisão posterior | Gatilho: §8, item 7 |

**Divergências de fatiamento e o que ficou:**
1. **Onde fica o cartão.**
   - Claude: na 1ª fatia. Codex: na 3ª.
   - Proposta: **na F2, junto da cor honesta**. O cartão repete o estado em texto; antes do D9 corrigido, repetiria "Falha" para o pixel mais baixo de um talhão sadio.
2. **D26:** fica fora de F0/F1, como decisão posterior com gatilho (aceito no §8, item 7). **Δ2 17/10:** gatilho registrado pelo Codex no 6227901968.
3. **Motor único:** candidato com gatilho, como o Codex propôs.
4. **Ordem em relação ao MAPA-FROTA:** retirada a proposta de passar a MUX-F1 à frente (§8, item 7).
   - Ordem sugerida, com contrato de arquivos e base em cada inserção: MAPA-FROTA F1 → MUX-F0 → MUX-F1 → MUX-F2 → EX-42 → MUX-F3 → SOLO-FOLHA-NIVEIS → SAF-MAPA com MUX-F4.
   - A MUX-F2 vem antes do EX-42 porque a linha do tempo recolore o mapa, e recolorir com o D9 aberto anima a classe errada.
   - Vale o teto de três frentes (§3.6).

## 8. Retorno do Codex sobre a avaliação do Claude (6227708290)

O Codex leu a avaliação `6c03d7e`, os brutos M19b/M20 e o `espelho_troca.txt`. Reproduziu o `cores.py` e o `busca_paleta.py` (mínimos 13,6, 14,9 e 15,1) e confirmou que `inicio.py`, `talmapa.js`, `engine.py` e `g2lib.js` não mudaram entre `b989864` e `05947ad`. Sem navegador, ele não reivindica reprodução de gestos, tempos ou árvore.

**Delta aplicado na avaliação do Claude:** 21 trechos marcados "Δ 17/10", só nos 8 pontos abaixo. Os JSONs e os `.txt` da §R da avaliação não mudaram.

### 8.1 Ponto a ponto

| # | Ponto do Codex | Resposta | Fonte ou reprodução | Delta na avaliação |
|---|---|---|---|---|
| 1 | 48 px no toque (pedido l.67); o DS de 44 é piso, não veto; "19 → 0 abaixo de 44" não basta | **Aceito.** 48 px no toque, aplicado localmente aos controles do mapa (abas, ferramentas, zoom, fechar, segmentados, atalho e ações do painel), sem mudar o `--g2-alvo` global. Medida nova a 390 px: abaixo de 48, **de 21 a 29 dos 29** controles medidos (21 é o mínimo garantido; as 9 abas e o atalho têm 44 no menor lado). Meta: 0. O talhão menor que 48 px na tela usa o controle equivalente na lista e na busca (NC5) | Pedido l.67; DS-15 (`PRD.md:14112`); `alvos48.txt` (recontagem do bruto M5) | D22; tabela §2 (alvos); medida da F1 |
| 2 | Não retirar "Todas" para corrigir o D6 | **Aceito.** Já era a resolução do D6 neste confronto | RF-WRK-004 (`PRD.md:2475`); DEC-2609-11 (`:12479`) | D6; §9, item 4 |
| 3 | 80 ms de timer não prova < 100 ms; sem atraso artificial; medir do evento à pintura | **Aceito.** ~~O cartão abre em 0 ms, no foco e no ponteiro. Método da F2, no aparelho de referência: `performance.now()` no `pointerover` ou `focusin` do talhão até o `requestAnimationFrame` seguinte ao cartão visível. Aceite: p95 abaixo de 100 ms; o SwiftShader só serve de indicação. Sem soma nominal como prova. Fica um único tempo: o fechamento de 120 ms do `g2dica`. Não é amortecimento de abertura: é o que deixa o ponteiro ir do talhão até o cartão sem ele sumir (WCAG 1.4.13). A troca entre vizinhos é 0 ms e também se mede~~<br>**Δ2 17/10:**<ul><li>**Abertura:** "0 ms" quer dizer **sem espera programada** (nenhum timer de abertura), não pintura instantânea. Não se declara latência zero.</li><li>**Método do aceite (a):** do `event.timeStamp` do `pointerover` ou `focusin` até o callback do `requestAnimationFrame` em que o cartão já está visível. **Limite:** é aproximação; mede até o quadro ser preparado, não até os pixels na tela.</li><li>**Método (b):** a duração da entrada `event` do Event Timing, quando o cartão é inserido no próprio manipulador. **Limite:** vai até a apresentação do quadro seguinte, arredondada a 8 ms, e não inclui o monitor.</li><li>**Aceite:** p95 abaixo de 100 ms pelos dois métodos, no aparelho de referência; o SwiftShader só serve de indicação; sem soma nominal como prova. A troca entre vizinhos se mede do mesmo jeito.</li><li>**Fechamento:** vale o timer atual do `g2dica` (120 ms). A WCAG 1.4.13 não fixa tempo: a conformidade depende de o cartão continuar visível enquanto o talhão **ou** o próprio cartão tiver hover ou foco, e de poder ser dispensado (Esc).</li></ul> | Pedido l.123; `g2lib.js:1192`, `:1227`; [W3C, Understanding 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) (Δ2) | Cartão (tabela §2); Δ2 também no resumo da avaliação |
| 4 | Concluído com 4,04:1 (branco) e 4,15:1 (escuro); ΔE não certifica; corrigir de forma verificável; não aplicar a paleta antes de revisar os pares reais | **Aceito e reproduzido**, com mais pares abaixo do limite:<ul><li>os mesmos 4,04 e 4,15 (seção A, colunas opacas);</li><li>Santa Rita (0,88 sobre `#E3EADB`): texto escuro abaixo de 4,5 em "impede" (2,42) e "em curso" (2,96); branco abaixo em 7 dos 9;</li><li>Lagoa Grande (0,55 sobre a imagem): nenhuma cor de texto passa em todos os tokens;</li><li>seleção `#15201A` abaixo de 3:1 em "impede" e "em curso"; foco `#1E7A4C` abaixo em 5 dos 9;</li><li>o halo sólido só existe no número; o sub e o rótulo usam sombra difusa.</li></ul>**Correção verificável:**<ul><li>~~placa branca sólida a 90 % atrás do rótulo, nas duas fazendas (pior caso 14,39:1);~~ **Δ2 17/10:** placa branca a 90 % (translúcida) atrás do rótulo, nas duas fazendas, com texto opaco `#15201A`. 14,39:1 é o menor valor só entre os fundos testados da Santa Rita. Para qualquer fundo opaco, inclusive a imagem da Lagoa Grande, o limite é 13,424:1 (a placa sobre preto). **Regra:** nenhuma `opacity` no ancestral do texto; hoje o sub da Santa Rita tem `opacity .85` (`inicio.py:1405`);</li><li>seleção e foco com escuro e branco, que cobre os 9 tokens; verde com branco falha no "em dia". Seleção contínua; foco tracejado e afastado;</li><li>se houver texto direto sobre o token, "concluído" passa a `#7D8C85` (4,76:1 opaco, 5,49:1 no uso; ΔE00 mínimo de 19,6, 13,5, 16,9 e 16,9).</li></ul>Aceite da F2: zero par abaixo do limite no script, refeito com os tokens finais | WCAG 2.2 1.4.3 (fonte citada pelo Codex) e 1.4.11; `contraste_pares.txt` A–F; `contraste_pares_placa.txt` G (Δ2) | §5: concluído; contraste do rótulo |
| 5 | "Estimado" não é "sem leitura"; separar qualidade e origem do valor; sem dado, fora do filtro e não se aplica distintos; Integrado com prioridade e motivo estáveis; bases comparáveis | **Aceito, com um ajuste no meio de "fora do filtro".**<ul><li>"Estimado" sai da hachura: é valor com origem marcada (cor da classe do valor e etiqueta "≈ estimado"). O protótipo já erra isso hoje (NC10).</li><li>Sem dado (hachura), não se aplica (liso) e fora do filtro ficam distintos no rótulo, na legenda e na lista. No preenchimento, o 74.7 põe "fora do filtro" no token liso de "não se aplica"; uma marca visual própria muda o 74.7 e fica para o registro do Codex.</li><li>Integrado: cada camada dá uma classe ordinal pela própria regra; o Integrado toma a mais grave; o empate segue a ordem fixa das 9 funções; o motivo diz a camada. Nenhum número de camadas ou unidades diferentes é comparado.</li><li>Custos e Colheita: escala só dentro de base comparável (mesma cultura, safra e unidade); entre culturas, "% da meta"; ausência nunca vira zero.</li></ul> | `PRD.md:14666-14667` (74.7), `:14196` (etiqueta "estimado"), `:14721` (DS-66), `:14779` (sem valor ≠ zero); `inicio.py:842` × `:832` | §5: sem leitura; não se aplica; camadas quantitativas |
| 6 | Painel sobreposto: o `padding` automático da câmera pode trazer o movimento de volta; 4 critérios | **Aceito, com um caso de borda explícito.** Sem `padding` automático: abrir e fechar o painel não muda a câmera nem a largura do mapa. Os 4 critérios entram no aceite da F3:<ol><li>o selecionado mantém as coordenadas em tela (deslocamento 0 px, método do M20);</li><li>área e foco não ficam encobertos;</li><li>Esc e voltar não perdem a câmera nem o rascunho;</li><li>voltar restaura a câmera e não reenquadra.</li></ol>~~**Caso de borda:** um talhão a menos de 384 px (a largura do painel) da borda direita fica sob o painel, e sem mover a câmera o critério 2 não se cumpre. Proposta: "Ajustar à fazenda", inclusive no enquadramento inicial (que é pedido explícito), reserva a faixa do painel, então só chega a esse caso quem arrastou o mapa. Nesse caso, o painel abre, o talhão fica onde está, e o cabeçalho do painel mostra "Voltar à seleção" (pedido explícito, 1 ação). O Codex decide se aceita essa exceção ao critério 2~~<br>**Δ2 17/10:** **caso de borda, com a regra do Codex (6227901968), adotada.** "Voltar à seleção" sozinho não basta, e o enquadramento inicial não conta como pedido explícito.<ol><li>Ao abrir, o foco vai para o título visível do painel, que nomeia o talhão.</li><li>Enquanto o foco está no painel, o selecionado pode ficar em parte sob ele, desde que haja identificação contextual (o título com o talhão) e um comando explícito para localizá-lo ("Localizar no mapa", que só move a câmera quando acionado).</li><li>Ao fechar o painel ou devolver o foco ao talhão, primeiro sai a sobreposição; só depois o foco volta ao botão do talhão.</li><li>A câmera não muda sozinha em nenhum desses passos.</li></ol>O critério 2 passa a valer assim: com o foco no talhão, área e foco nunca ficam encobertos; com o foco no painel, a cobertura parcial é permitida nas condições do passo 2. Aceite da F3: os quatro passos e o deslocamento de 0 px do M20 | Pedido l.48 e NÃO FAZER 5; `PRD.md:9538`; M20 | N1; painel lateral (tabela §2) |
| 7 | Botões, busca e lista antes do motor é convergência; não antecipar a MUX-F1 sobre a autoria do MAPA-FROTA sem contrato; embalagem é decisão posterior; teclado por setas exige semântica, instruções e leitor real | **Aceito, com um ajuste.**<ul><li>Convergência registrada.</li><li>Retirada a proposta de MUX-F1 antes da MAPA-FROTA F1. A divisão da §8.2 entra depois dela, por contrato de arquivos e base.</li><li>Embalagem: aceito que é decisão posterior e não bloqueia F0/F1. **Ajuste:** o D26 é S2 na fazenda padrão (o mapa some sem o CDN), e o IN-04 a 390 px é o mapa a que o campo chega (NC7). Peço ao Codex que registre o gatilho: antes de qualquer publicação que leve o IN-04 a uso sem internet, ou na primeira fatia que mexer no carregamento do motor. **Δ2 17/10:** registrado pelo Codex (6227901968): antes de publicar o IN-04 para uso offline, ou na primeira alteração do carregamento; com o CDN indisponível, a lista e um aviso recuperável continuam. Isso entra no aceite da MUX-F1 (item 10).</li><li>Teclado: o aceite da MUX-F1 traz semântica, instruções visíveis e no `aria-describedby`, e prova com leitor de tela real. Nenhum dos dois agentes tem leitor real neste ambiente, então a prova é portão para fechar D1, D2 e T7. Gatilho: ambiente com NVDA, VoiceOver ou TalkBack, ou o teste com usuários da DEC-1610-02.</li></ul> | Fronteira de `inicio.py` aceita no 6224071197 (`MAPA-FROTA.md:678`); AGENTS §3.6 | Teclado; ordem (§8 da avaliação); MUX-F3 |
| 8 | Rastreabilidade: JSONs com a versão antiga; §N "todos executados"; D25 sem ausência global | **Aceito.**<ul><li>Brutos intactos e manifesto novo: M0–M2 no espelho antigo (certo); M3 cruza a troca (indeterminado); M4–M11 no novo (provável; margem de 5,5 s no M4); M12–M18 e os brutos b–h no novo (certo). O resultado vale para os dois, porque os arquivos do mapa são iguais; muda o rótulo da versão. A frase "M0–M2 no antigo e as demais no novo" estava imprecisa no M3.</li><li>§N corrigido: N1–N4 no navegador, N5 por leitura estática.</li><li>D25: o ícone existe na barra e no `engine`; corrige-se só o catálogo das ações (`ICN` e `ICS`).</li></ul> | `manifesto_medidas.txt`; `fontes_confronto.txt` §6 | Bases (l.9); §N; D25; §R |

Fora do escopo deste confronto: a "devolução 88→89" que o Codex pede para priorizar.

**Δ2 17/10 (comentário 6227901968):**
- 6 ajustes de documento nos itens 3, 4, 6 e 7 desta tabela, na §5 (G2 e G3), na §7 e na §8.2. Estão marcados "Δ2 17/10", com o texto anterior riscado.
- O Codex registrou a convergência (Lista | Mapa no mesmo bloco; "Todas" mantida; nomes, ícones e contexto na F0; F1 antes do motor) e o gatilho do D26.
- Ele diz que isso não é aceite integral dos 61 pontos nem teste com leitor real. Das seções F e D do contraste e da renderização, diz que ainda não as reproduziu.

### 8.2 Divisão executável MUX-F0 e MUX-F1 (autorias vigentes)

**Regras do contrato proposto:**
- O Claude é autor de `inicio.py` na sequência aceita (MAPA-FROTA → EX-42 → SOLO-FOLHA-NIVEIS → SAF-MAPA). As duas fatias entram depois da MAPA-FROTA F1.
- Nenhuma toca arquivo de outra frente: `alocacao.py` (PR #88), `processo_os.py` (só leitura do `#tal=`), `cad_fazendas.py`, `frota.js` e os arquivos do EX-42, do SOLO-FOLHA-NIVEIS e do SAF-MAPA.
- Peças comuns do DS (`engine.py`, `g2lib.js`) ficam para a F2 e a F3.
- A interface nova fica dentro de `inicio.py`, com a API da §6 da avaliação, para o SAF-MAPA extrair depois. É a mesma regra do MAPA-FROTA (`MAPA-FROTA.md:684`).
- `G` = `tools/prototipo/v37/gen37`.

```text
ID / resultado útil / persona: MUX-F0 · Destinos, nomes e ícone / quem sai do mapa chega ao destino com a fazenda e o talhão já escolhidos, e o mesmo pivô tem um nome só no IN-04 / gestor, agrônomo, PCP
Requisitos do PRD e fora do escopo: D7, D8, D18, D24, D25, D27 (só no IN-04); SEL-02; BOT-08. Fora: D27 no CD-01 (MUX-F4), cor, cartão, teclado, lista, motor e embalagem
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base / arquivos sob responsabilidade: ponta publicada da branch única claude/prototipo-v44 que contém a MAPA-FROTA F1 (o Codex fixa o SHA no contrato; hoje os arquivos do mapa são iguais em b989864, 05947ad e 47ccc1d). ~~Opção, se o Codex aceitar no contrato: junto da MAPA-FROTA F1, mesmo autor, porque as funções não se cruzam~~ Δ2 17/10: o contrato só vira executável quando o Codex fixar o SHA depois da MAPA-FROTA; até lá, nenhuma autoria ativa fica reservada para a MUX /
  G/areas/inicio.py, só: FL (:1127-1128: sem "Ver histórico" para o AG-06; link de módulo em Solo e Colheita › Situação); painel da O.S. (:1074: "Nova O.S. neste talhão" com #tal=); seção do Satélite (:1016: sem link para o AG-06); ICN (:911) e ICS (:1445): 'Colheita'; cabeçalho do painel do pivô (:986: "P5", não "Pivô 5");
  G/talmapa.js (:163-169: #talhao= troca a fazenda; ID inexistente dá aviso visível e acessível e não seleciona outro);
  teste novo G/mapa_mux_f0_test.py
Aceite e comando de verificação:
  1. "Nova O.S. neste talhão" (e "Abrir ordens" com talhão selecionado) abre a O.S. com #tal=<fazenda>|<talhão> e o talhão já escolhido;
  2. com o contexto salvo na Santa Rita, IN-04.dc.html#talhao=PV05 abre a Lagoa Grande com o PV05 selecionado; #talhao=PV99 mostra aviso e não seleciona nada;
  3. Satélite sem link para o AG-06, na faixa e no painel;
  4. Solo e Colheita › Situação com link de módulo;
  5. as ações de Colheita mostram o ícone que a barra já usa;
  6. no IN-04, o pivô aparece como "P5" no marcador, no painel e no nome acessível.
  Comando: python3 -B mapa_mux_f0_test.py (especificado, a criar) e os testes de mapa existentes do gerador; contraprova: o render de 05947ad reprova os itens 1 a 6
Medida antes → meta: destinos sem contexto (M11, M15): 4 → 0; ações de Colheita sem ícone (:1080, :1398-1400): todas → nenhuma; nomes do mesmo pivô no IN-04: 2 → 1
Estado / impedimento / próximo passo: especificado. Começa depois do registro do Codex, com vaga no teto de três frentes. Δ2 17/10: não executável até o SHA fixado depois da MAPA-FROTA; sem reserva de autoria ativa
```

```text
ID / resultado útil / persona: MUX-F1 · Achar e abrir o talhão / quem não usa mouse acha qualquer talhão das duas fazendas, abre o painel e volta sem perder o lugar; todos acham o talhão pela busca e pela lista / gestor e agrônomo no computador, inclusive só com teclado ou com leitor de tela; operador que chega pelo aviso de carência a 390 px
Requisitos do PRD e fora do escopo: D1, D2, D6, D16, D17, D20 (foco e Esc), NC1 (visão "Ver dados"), NC2 (aria-pressed); 74.5.24, 74.5.26, MAPUX-06, RF-WRK-004, SEL-02. Fora: cartão e cor (F2); painel por cima, folha inferior, 48 px, "Ajustar à fazenda" e "Voltar à seleção" (F3); motor e embalagem (decisão posterior)
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base / arquivos sob responsabilidade: ponta publicada depois da MUX-F0 (mesmo contrato) /
  G/areas/inicio.py: SVG _mapsvg (:1407-1438): grupo com nome no lugar de role=img; data-talhao e aria-pressed em cada talhão, mantendo role=button para não quebrar os testes que usam svg [role=button];
    marcadores da Lagoa Grande (:636-646): botões focáveis no mesmo grupo, com data-talhao, aria-pressed e nome completo; se a MAPA-FROTA F1 já tiver a camada de marcadores, usa a mesma;
    busca "Ir para talhão" e atalho "/"; visão "Ver dados" (Lista | Mapa) no mesmo bloco, com os mesmos filtros, seleção e painel (template e MAPVALS, :1100-1191);
    Esc por nível e clique no fundo (:1435; clique fora de pv-fill); foco no título do painel e retorno (pan_close, :1159-1162);
    URL #faz=&lay=&t=&dt= junto do mapa-ctx (:1111); "Todas" (:1102, :1189-1191);
  testes novos G/mapa_mux_f1_test.py (Chrome a 1440 e 390, com árvore de acessibilidade) e G/mapa_mux_unit.js (vizinho por direção, ordem da lista, leitura da URL)
Aceite e comando de verificação:
  1. nas duas fazendas, o mapa é um grupo com nome ("Talhões da Fazenda X · N talhões"). Tab entra uma vez; setas vão ao vizinho na direção; Home e End vão ao primeiro e ao último pelo nome; Enter abre o painel com foco no título; Esc fecha e devolve o foco ao talhão; o Tab seguinte sai do mapa (depende do G2: ~~se o Gemini escolher B, este item vira "todos os talhões no Tab" e o resto não muda~~ Δ2 17/10: a alternativa B saiu; se o G2 pedir ajuste em A ou uma alternativa compatível, como A2, o item 1 segue a resposta, mantendo as setas que o pedido exige);
  2. instruções visíveis junto do mapa ("Setas: talhão vizinho · Enter: abrir · /: buscar") e no aria-describedby do grupo;
  3. cada talhão tem role=button, aria-pressed igual à seleção e nome completo no formato do pedido;
  4. "/" foca a busca; "P5", "PV05", "Pivô 5" ou "T4" + Enter seleciona e abre o painel; na Lagoa Grande, enquadra (pedido explícito, tmEnquadra); fora disso, a câmera não se move;
  5. "Ver dados" alterna Lista | Mapa: uma linha por talhão, com valor, estado em texto e data da camada ativa, ordem pela gravidade e "N de M"; a linha abre o mesmo painel; "Localizar no mapa" volta ao mapa com o talhão selecionado; os filtros são os mesmos;
  6. "Todas": a lista mostra as três fazendas; o mapa mostra as que têm geometria e diz quais não têm;
  7. Esc fecha o modo ativo, depois a seleção, sem apagar o rascunho de desenho; clique no fundo desmarca;
  8. recarregar IN-04.dc.html#faz=LG&lay=sat&t=PV05&dt=25-09 restaura fazenda, camada, data e seleção; voltar do CD-01det restaura câmera e seleção, sem reenquadrar;
  9. portão: prova com leitor de tela real antes de fechar D1, D2 e T7 (§8.1, item 7);
  10. Δ2 17/10: com o CDN indisponível, a visão Lista continua e o aviso oferece tentar de novo, sem recarregar a página (gatilho do D26 registrado pelo Codex). No item 1, "Esc fecha" segue a ordem do §8.1, item 6: a sobreposição sai antes de o foco voltar ao talhão.
  Comando: python3 -B mapa_mux_f1_test.py e node mapa_mux_unit.js (especificados) e os testes de mapa existentes; contraprova: o render de 05947ad reprova os itens 1 a 8
Medida antes → meta: pivôs da Lagoa Grande alcançáveis por teclado: 0 de 23 → 23 (método M1); paradas de Tab no mapa da Santa Rita: 8 → 1 (M2); teclas para abrir um talhão pelo nome: impossível → até 4 ("/", nome, Enter); talhões com aria-pressed: 0 de 31 → 31; lista equivalente: não existe → existe, com "N de M"; Esc fecha o painel: não → sim; location.hash com a seleção: vazio → completo (M10)
Estado / impedimento / próximo passo: especificado. Depende do registro do Codex, do G2 (só o item 1) e da vaga no teto de três frentes. Δ2 17/10: não executável até o SHA fixado depois da MAPA-FROTA e da MUX-F0; sem reserva de autoria ativa
```

## 9. Divergências com o PRD para a conferência final (Δ2 17/10)

O PRD não muda agora: o gatilho é a conferência depois do conjunto vigente (DEC-0910-06; Codex 6227901968). Ficam registradas aqui, para essa conferência:

| # | PRD hoje | Desenho deste confronto | Fonte do desenho |
|---|---|---|---|
| PRD-1 | 67.2/67.3: tabela abaixo do mapa × v3.9 (`PRD.md:9516`): nenhuma tabela nem lista abaixo do mapa (contradição interna) | Lista alternativa como visão "Ver dados" (Lista \| Mapa) no mesmo bloco | MAPUX-06, RF-WRK-004, 74.5.24, 74.5.26 (T4, NC1) |
| PRD-2 | 74.5.24: zoom de 44 × 44 px no toque (`:14444`) | 48 px nos controles do mapa no toque | Pedido l.67 (D22) |
| PRD-3 | 74.5.26: nome do talhão "{talhão}: {estado}" (`:14461`) | Nome completo do pedido ("P4, 73 ha, mamão em produção, …") | Pedido l.72 (NC8) |
| PRD-4 | IN-04 (`:409`) e a skill de satélite: "Criar vistoria" | "Programar vistoria", que já é o verbo do protótipo | BOT-03 (DEC-0910-01) (C2) |
| PRD-5 | 67.2 e 74.5.22: "barra vertical" de funções | Barra horizontal com nome no alto do mapa | MAP-03, pedido de 16/10 (R13 da avaliação) |
| PRD-6 | 74.7: "fora do filtro" no token liso de "não se aplica" (`:14666`) | Mesmo preenchimento, distinção pelo texto; marca visual própria só se o Codex registrar | Retorno 6227708290, item 5 |
| PRD-7 | 74.7.3: tabela de cores de estado | Tokens por significado, depois do G1 e da revisão dos pares reais | Avaliação §5; §8, item 4 |
| PRD-8 | 74.7.5: halo branco no rótulo | Placa branca a 90 % atrás do rótulo; sem `opacity` no ancestral do texto | `contraste_pares.txt` B; `contraste_pares_placa.txt` G |
| PRD-9 | 74.5.24: "Ajustar à fazenda" e "Voltar à seleção" sem regra de câmera | Câmera só por pedido explícito; o enquadramento inicial não conta como pedido; sem `padding` automático | §8, item 6 |

## R. Reprodução (executado em 17/10/2026, só leitura)

| Comando | Saída | Resultado |
|---|---|---|
| `python3 -I -B reproducao/confronto/linhas_citadas.py <G>` | `linhas_citadas.txt` | 109 citações das duas avaliações: 106 batem; 3 do Codex estão deslocadas de 1 a 4 linhas, com o conteúdo confirmado na linha vizinha |
| `sh reproducao/confronto/fontes_confronto.sh <repo> <G> <render>` | `fontes_confronto.txt` | §0: 11 de 11 anexos iguais ao `SHA256SUMS`; 0 arquivo do mapa alterado entre `b989864` e `47ccc1d`. §1–§5: as linhas de PRD, DS, pedido, EX-43, skill e NAV citadas aqui. §6: ícone, `aria-pressed`, forced-colors e verbo na fonte. §7: título do AG-06, ausência da lista no IN-04 e arquivos de apoio |
| `python3 -I -B reproducao/confronto/mb_mapa.py <render>` | `mb_mapa.txt` | 15 telas MB: 0 com mapa; 11 com o código do link "Ver restrição/pendência no mapa" |
| `python3 -I -B reproducao/confronto/contraste_pares.py <render>` | `contraste_pares.txt` | Retorno, item 4. A: texto sobre o token opaco e sobre o preenchimento da Santa Rita (reproduz 4,04 e 4,15). B: placa ~~sólida, pior caso 14,39:1~~ a 90 %, 14,39:1 só entre os fundos testados da Santa Rita (Δ2). C: seleção e foco contra o preenchimento. D: Lagoa Grande a 0,55 sobre a imagem (PNG decodificado em Python puro; 820 linhas com filtro 0). E: candidatos a "concluído". F: anéis em duas cores |
| `python3 -I -B reproducao/confronto/contraste_pares.py --placa-limite` | `contraste_pares_placa.txt` | Δ2 17/10: placa a 90 % sobre preto, composta em 8 bits: `#E6E6E6` × `#15201A` = 13,424:1 (sem arredondar: 13,362:1); o 14,39:1 da seção B vale só para os fundos testados da Santa Rita. Com `opacity .85` no ancestral (sub da Santa Rita, `inicio.py:1405`), o par muda para 8,883:1. O `contraste_pares.txt` não mudou (mesmo SHA-256 antes e depois) |
| `python3 -I -B reproducao/confronto/manifesto_medidas.py reproducao` | `manifesto_medidas.txt` | Retorno, item 8: cada medida M0–M20 ligada ao espelho e ao SHA. M0–M2 no antigo; M3 indeterminado; M4–M11 no novo (provável); M12–M18 e b–h no novo (certo). Lê as horas de gravação da worktree em que as medidas rodaram |
| `python3 -I -B reproducao/confronto/alvos48.py reproducao` | `alvos48.txt` | Retorno, item 1: dos 29 controles medidos a 390 px (bruto M5), de 21 a 29 abaixo de 48 px |

Notas:
- `<G>` é `tools/prototipo/v37/gen37` de `47ccc1d`, extraído com `git show` para uma pasta de rascunho. `<render>` é o render de `05947ad`.
- Limites: leitura estática; sem navegador, leitor de tela real ou usuários. As medidas de navegador citadas (M0–M20) são as do Claude em `6c03d7e`, não repetidas aqui.
