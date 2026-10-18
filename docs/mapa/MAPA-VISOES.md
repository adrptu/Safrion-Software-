# MAPA-VISOES · macro e micro, sintética e analítica, em todas as camadas do Mapa (rascunho R1, 18/10/2026)

Autor: Claude · revisor: Codex · integrador: Codex · protótipo no regime leve (AGENTS §3.5). Primeira aplicação: Solo ([SOLO-GEO](../analise-solo/SOLO-GEO.md)).

## Pedido do proprietário (18/10/2026, literal)

> "O mesmo que pedi acima, fazer também para todas funcionalidades do mapa, visao macro e micro, sintetica e analitica de forma rápida, facil, intuitiva e completa, para agilizar e facilitar análise e decisão."

## 1. Hoje

O Mapa tem 9 camadas (`areas/inicio.py`, `LAYS`): Integrado, Satélite, Solo, Pragas e doenças, Ordens de serviço, Irrigação, Estádio, Colheita e Custos. Cada camada mostra **uma métrica por vez** sobre os talhões e abre o painel de um talhão. Não existe:

- **Resumo da fazenda**: o que está bem, o que está mal e quantos hectares cada caso ocupa;
- **Matriz** com todos os talhões e as métricas da camada lado a lado;
- **Visão do talhão** com todas as métricas de uma vez.

Hoje, para comparar talhões, é preciso trocar de métrica e lembrar dos números.

## 2. Padrão único: quatro visões, uma barra

A barra da camada ganha **Mapa · Resumo · Matriz** (VIS-07, um toque). O talhão abre a visão **Talhão**.

| Visão | Pergunta que responde | Conteúdo |
|---|---|---|
| **Resumo** (macro sintética) | Como está a fazenda? | 3 a 6 números com unidade; % da área por classe de cada métrica (barra empilhada); uma frase do que mais pesa ("K baixo em 212 ha") com o link para a Matriz filtrada |
| **Matriz** (macro analítica) | Onde e quanto? | Talhões × métricas da camada; célula com valor (ou mín · méd · máx quando há variação dentro do talhão) e cor da classe; ordenar, filtrar por "fora do adequado"; rodapé com a média ponderada da fazenda |
| **Mapa** (como hoje) | Onde fica? | Uma métrica no espaço, com a mesma escala e legenda da Matriz |
| **Talhão** (micro sintética → analítica) | O que acontece neste talhão? | Todas as métricas da camada em pequenos múltiplos, com detalhe (pontos, série no tempo, ordens) e ações |

**Regras:**
- Mesma escala e cores no Mapa, na Matriz e no Talhão. O contraste (Talhão, Fazenda, Absoluto) é declarado na legenda.
- Número sempre com unidade, e a fonte na dica (ⓘ). Métrica sem fonte não entra.
- Os filtros da camada (fazenda, safra, período, laudo, cena) valem para as quatro visões. "‹ Matriz" ou "‹ Resumo" volta ao mesmo lugar.
- Célula → Talhão com a métrica em foco. Linha → Talhão.
- **Acessibilidade:** a Matriz é tabela com cabeçalhos (`role=table`). Teclado: setas movem entre células, Enter abre. A cor nunca é a única informação: a classe também vai em texto.
- **Celular (390 px):** a Matriz rola dentro do contêiner com a 1ª coluna fixa; o Resumo vira lista; a página não rola de lado.
- Só leitura: olhar não grava nada. Ação (abrir O.S., programar, registrar) leva à tela dona do comando.

## 3. O que cada camada mostra

| Camada | Resumo | Matriz (colunas) | Talhão |
|---|---|---|---|
| Solo | % da área por classe em cada indicador; pior indicador por área | Indicadores do laudo: mín · méd · máx | Mini-mapas de todos os indicadores, pontos e CV % |
| Satélite | Média, mín. e máx. do índice na fazenda; % da área por classe de vigor; Δ da cena anterior | NDVI, NDRE, EVI, SAVI e NDMI: média, CV % e Δ | Mini-mapas dos índices, série das cenas e histograma |
| Pragas e doenças | Talhões e área acima do nível de controle; alvos em alta | Alvos: último nível ÷ NC e tendência | Pontos de monitoramento, série por alvo e O.S. ligada |
| Ordens de serviço | Ordens por fase, atrasadas e impedidas | Fase, atraso (dias), impedimento e avanço % | Ordens do talhão no tempo |
| Irrigação | Setores a programar e impedidos; déficit médio | Déficit, % da CAD, gatilho, lâmina programada e cobertura | Balanço diário, água no solo e ordens |
| Estádio | Talhões por estádio; próximas operações em 7 dias | Cultura, estádio, DAP e próxima operação | Linha do tempo do ciclo |
| Colheita | % colhido; produtividade real × prevista; carência | % colhido, sc/ha real e prevista, umidade e carência | Cargas, produtividade e destino |
| Custos | R$/ha previsto e realizado; desvio | R$/ha por natureza (insumo, operação, máquina, mão de obra) e desvio | Composição e ponte do desvio |
| Integrado | Talhões com algo a resolver, por camada | Uma coluna por camada com o pior estado (semáforo + texto) | Lista do que resolver, cada item com o link da camada |

## 4. Fatias

- **F1:** Solo (Resumo, Matriz e Talhão), junto com a SOLO-GEO F1. É o padrão de referência.
- **F2:** Integrado e Satélite. O Integrado vira a porta de entrada da análise.
- **F3:** Irrigação, Pragas e doenças, e Colheita.
- **F4:** Ordens de serviço, Estádio e Custos.

## 5. Aceite comum a cada camada (V1–V8, com contraprova na versão anterior)

- **V1** A barra mostra Mapa · Resumo · Matriz; o padrão abre como hoje (Mapa).
- **V2** A Matriz lista todos os talhões do filtro. Cada célula tem valor e unidade, e o oráculo do teste recalcula pela fonte do domínio.
- **V3** A cor e a classe da célula são as mesmas do Mapa para a mesma métrica e talhão.
- **V4** O Resumo soma a área do filtro (±0,1 ha) e a frase de destaque aponta o pior caso por área.
- **V5** Célula → Talhão com a métrica em foco; voltar mantém ordem, filtro e rolagem.
- **V6** Teclado e leitor de tela percorrem a Matriz; a classe aparece também em texto.
- **V7** A 390 px nada vaza; a 1ª coluna fica fixa.
- **V8** Sem erro de JavaScript; o armazenamento fica igual ao só olhar.

## 6. Perguntas ao Codex

1. A matriz do Integrado (pior estado por camada) substitui o painel "Atenção" do Mapa ou fica ao lado dele?
2. A ordem das fatias F2–F4 está boa? Meu critério foi frequência de uso e dano: o Integrado decide a rotina, Irrigação e Pragas mexem com a safra.
