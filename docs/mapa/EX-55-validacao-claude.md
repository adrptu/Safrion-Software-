# EX-55 · Mapa dentro das telas do Agrícola · validação independente do Claude

Pedido do proprietário (18/10/2026) e prompt: `docs/integracao/V73/pedidos-1810/prompt-safrion-mapa-nas-telas.md`. Este documento é a decisão do Claude, feita sem ver a do Codex. O Codex registra o confronto no checkpoint.

## 1. O que existe hoje (lido no código da composição v135)

| Peça | Onde | Serve ao EX-55? |
|---|---|---|
| Classificação por camada: uma função para todas as camadas (`cls(l,f,t)` → classe e rótulo do talhão; `osCls`, `mipOf`, `soloCls`, `colhCls`, irrigação) | `areas/inicio.py` (JS do IN-04, a partir da linha ~856) | **Sim. É a regra única (R1).** Hoje vive só dentro do IN-04 |
| Mapa da Lagoa Grande em MapLibre (imagem e desenho do talhão) | `talmapa.js` e IN-04 | Não para embutir: pesado e sem teclado (achado do EX-44). Fica no Mapa da fazenda |
| Geometria dos talhões das duas fazendas (LG em lon/lat projetado, SR esquemática) | `geo_talhoes.mapa()` | Sim: a mesma fonte do IN-04 |
| Mapa SVG embutido nº 1: Planejar safra › Editar talhões › Mapa (seleção por talhão, teclado, rótulo ao vivo) | `safra_mapa.js` e `areas/saf_lote.py` | Sim: já cumpre R3, R4 e R8 para uma tela |
| Mapa SVG embutido nº 2: O.S. › Frentes (rota numerada, sede, marcadores HTML) | `areas/processo_os.py` (`_fr_mapa`) | Sim, mas é uma **segunda cópia**: viola R1 se ficar |

**Conclusão.** O componente quase existe, em duas cópias e sem a classificação do IN-04. A F1 junta as duas cópias num componente e liga esse componente à classificação única. Não se escreve um terceiro mapa.

## 2. Decisões de desenho (Claude)

- **D1 · Adaptar R1.** "Mesmo motor" = mesma classificação, mesmas classes, cores e legenda, e o mesmo "sem dado". O desenho embutido é SVG, a partir da mesma geometria (`geo_talhoes`), e não MapLibre.
  - **Motivo:** o MapLibre não é operável pelo teclado (EX-44), pesa no celular e não traz a imagem de satélite que essas telas não usam.
  - A imagem continua no Mapa da fazenda, aberta pela ação secundária R6.
- **D2 · Extrair a classificação** do IN-04 para `mapa_camadas.js`, com as mesmas funções e sem mudar a saída:
  - o IN-04 passa a carregar o arquivo;
  - contraprova: o IN-04 dá os mesmos rótulos e as mesmas classes antes e depois, nas 9 camadas;
  - teste de paridade com uma varredura por talhão e camada.
- **D3 · Componente `mapaEmb`**, da união de `safra_mapa.js` com `_fr_mapa`. A tela fornece:
  - o recorte (as linhas da própria lista);
  - a camada e o "Mostrar";
  - o clique (abre o detalhe da tela);
  - as ações de seleção permitidas.
  
  O componente faz:
  - desenho, legenda com "sem dado" em hachura;
  - contador "N no mapa · M sem geometria", com a lista dos que não têm geometria;
  - dica de 3 ou 4 valores;
  - teclado (Tab na ordem da lista, Enter, Esc);
  - seleção (clique, Shift+clique; o laço fica para a F2);
  - selo "posição esquemática" na Santa Rita.
- **D4 · Visão "Mapa"** entra no registro de visões (`visoes.py`) e vale para as telas que a declaram (`?view=mapa`, preferência por pessoa e tela).
  - Na O.S., a visão Frentes continua: é onde a frente se monta.
  - O "Mostrar · Frentes" do Mapa da O.S. desenha a rota da frente escolhida com o mesmo componente.
- **D5 · Seleção nunca aprova.** As ações de seleção são as que a tela já tem para vários talhões.
  - A O.S. não ganha "criar O.S. nos selecionados" na F1: a emissão vem do plano, e "criar a partir do mapa" é a F2.
  - Nada de aprovação em lote, por decisão fixa.

## 3. Tela por tela (decisão do Claude)

| Tela | Prompt | Claude | Fatia | Motivo |
|---|---|---|---|---|
| Ordens de serviço | alto | **Adotar** | F1 | A camada O.S. já existe (`osCls`: Fases, Avanço, Atrasos, Impedimentos). A rota da frente reaproveita o EX-54 |
| Pragas e doenças | alto | **Adotar** | F1 | A camada MIP já existe (`mipOf`, a pior situação no período). A vistoria atrasada é o caso de uso diário |
| Irrigação | alto | **Adotar** | F1 | A camada já existe (setores, déficit). "Programar nos setores em déficit" já é ação da tela |
| Planejar safra | alto | **Já feito** (SAF-MAPA) | F1 | Migra para o componente único. Os testes `saf_mapa_test` M1–M9 são a regressão |
| Colheita | alto | **Adotar** | F2 | A camada `colhCls` existe. A seleção para programar colheita depende da O.S. de colheita |
| Análises de solo | alto | **Adaptar** | F3 | Só com laudo georreferenciado. A interpolação exige a legenda de valores e a qualidade do dado (SOLO-GEO F1 antes) |
| Custos | alto | **Adaptar** | F3 | Corrigir antes o "todo talhão com previsto fica azul" (EX-44). Sem a correção, o mapa engana |
| Orçamento | médio | **Adotar** | F3 | Junto com o ORC-2 (variação explicada), não antes |
| Planos agronômicos | médio | **Adaptar** (ver §6, ponto 1) | F4 | Versão adotada por talhão; destaca a adoção desigual |
| Recebimento | médio | **Adotar** | F4 | A origem por talhão |
| Agrofit, Beneficiamento, Estoque de produto, Painel | sem mapa | **Rejeitar** a visão; adotar o link ao talhão | F4 | Não há decisão espacial |

## 4. Aceite da F1 (medido antes do código)

1. **Paridade da classificação:** para cada talhão das duas fazendas e cada camada e "Mostrar" usados nas 3 telas, a classe e o rótulo do componente são iguais aos do IN-04. A contraprova é uma mudança deliberada na regra, que tem de reprovar.
2. **Mesmo recorte:** com o filtro da tela (fazenda, safra, cultura, talhão), o mapa mostra exatamente os talhões das linhas visíveis. O contador "N no mapa · M sem geometria" bate com a lista.
3. **Clique:** abre o detalhe da própria tela (O.S., vistoria, setor), e não o IN-04. Talhão com vários registros abre a lista curta.
4. **Teclado:**
   - Tab percorre na ordem da lista, Enter abre, Esc fecha;
   - `aria-label` com os mesmos 3 ou 4 valores da dica;
   - alvo de 44 px no celular.
5. **Endereço:** `?view=mapa` reabre a visão; Voltar e F5 preservam a visão e o talhão aberto.
6. **Escala:** "Sem dado" em hachura e contado; selo "posição esquemática" na Santa Rita.
7. **Mapa da fazenda:**
   - "Abrir no Mapa da fazenda" leva a camada e o escopo;
   - o IN-04 continua igual (`mapa9_test`, `mapa_filtros_test` e `mapa_mux_*` verdes).
8. **Regressão do componente único:**
   - `saf_mapa_test` M1–M9 e `os_frentes_test` F1–F9 passam no componente único;
   - 390 px sem rolagem lateral; nenhum erro de script.

## 5. Listas curtas

- **Aplicado:** componente único a partir das duas cópias; classificação do IN-04 como fonte; F1 = O.S., Pragas, Irrigação e a migração do Planejar safra.
- **Deixado de fora (com gatilho):**
  - laço de seleção: F2;
  - interpolação de solo: volta com o SOLO-GEO F1;
  - mapa de custos: volta com a correção do EX-44;
  - mapa de planos: F4 (§6, ponto 1).
- **Cortado:** mapa no Agrofit, Beneficiamento, Estoque de produto e Painel; MapLibre embutido.
- **Gemini:** não é necessário para a F1, porque não há divergência de domínio. Fica para a F3, em solo (interpolação) e produtividade.

## 6. Confronto com o Codex (6253659075, 18/10/2026): os 5 pontos aceitos e incorporados

| # | Ponto do Codex | Decisão | Como fica |
|---|---|---|---|
| 1 | Planos não pode ficar à espera de novo pedido do proprietário | **Aceito** | Planos agronômicos passa de "Adiar" para **Adaptar, F4**: o mapa mostra a versão adotada por talhão e destaca a adoção desigual. O requisito já está no prompt de 18/10 |
| 2 | Separar abrir de selecionar | **Aceito** | Nas telas de consulta (O.S., Pragas, Irrigação), clique, toque ou Enter no talhão **abre** o detalhe. A seleção tem controle próprio e acessível: o botão "Selecionar talhões" liga o modo de seleção, e então o toque marca, sem depender de Shift. Um gesto nunca abre e marca ao mesmo tempo. No Planejar safra o contrato atual continua: tocar marca as linhas do talhão, inclusive "em parte" (mixed) |
| 3 | Paridade no mesmo contexto | **Aceito** | A classe, a dica, o total e a lista curta vêm **das linhas visíveis da própria lista** (o mesmo recorte de fazenda, safra, cultura, talhão e busca). Um talhão com duas O.S., uma delas filtrada fora, pinta só pela visível. Unidades diferentes não se somam e a lista curta mantém os IDs. O extrator declara as suas dependências e não carrega o IN-04 inteiro |
| 4 | O Planejar safra pinta o rascunho | **Aceito** | Ficam em comum o desenho, a seleção e a geometria. O adaptador de contexto do Planejar safra continua lendo o rascunho (`sl.vals`: cultivar, plano e semana) e nunca o `lavOf` publicado. A regressão prova rascunho, seleção parcial e foco ao alternar Tabela e Mapa (`saf_mapa_test` M1–M9) |
| 5 | Não chamar as nove camadas de prontas | **Aceito** | A F1 valida só os contextos usados (camada O.S. em Fases, Avanço, Atrasos e Impedimentos; MIP; Irrigação de hoje e balanço) e as regressões existentes. "Sem leitura", "sem cultura" e "não aplicável" continuam distintos. Laço, solo e índices seguem pendentes com os seus IDs |

**O aceite da F1 (§4) muda assim:**
- **Item 1:** a paridade é medida com o recorte real de cada tela, com um caso de talhão com registro filtrado fora.
- **Item 3:** clique abre; a seleção só pelo modo "Selecionar talhões".
- **Novo item 9:** no Planejar safra, a cor vem do rascunho e não do publicado. A contraprova é alterar o rascunho sem salvar: a cor muda.

**Divisão de arquivos antes do código** (pedido do Codex):
- `mapa_camadas.js`: a classificação extraída do IN-04, só as funções e dependências declaradas;
- `mapa_emb.js`: desenho, legenda, dica, teclado e seleção;
- adaptadores por tela: `os_mapa.js`, `mip_mapa.js`, `irr_mapa.js` e o atual `safra_mapa.js`, que vira adaptador.

Autoria Claude; o Codex revisa.
