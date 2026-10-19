# Artefato v139 (versões 149–151, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versões:** 149 (`1792378583-7a4c`), 150 (`1792378613-1fc1`) e 151 (`1792378621-2088`). São 3 lotes, com 29, 27 e 2 páginas.
- **Fonte:** `452c5afd` em `claude/v44-v135-osagrupa`, com o código igual ao do `f44ab371`. O render é o build `SAFRION_DADOS=sintetico` desse commit.
- **Aceite do Codex:** VIS-08 e bloco A em 6258622734, F1a2 em 6258387053 (PR #125). Os PRs #121 e #122 têm o parecer do Claude (6257700828 e 6258085312).

## O que mudou
- **VIS-08:** o modo de visão passa a ser escolhido pelo ícone em todas as telas, inclusive Planejar safra › Editar talhões (Ver em mapa), Cadastros › Fazendas e talhões, Beneficiamento e Manutenção › Ordens (`../v139/LEIAME.md`).
- **PR #121 (EX-57 F0c, Codex):** a data das atividades sai de uma regra só. A necessidade sem data fica "sem data" e não entra no calendário nem nos custos.
- **PR #122 (EX-53 F1a parte 1, Codex):** indicador sem meta configurada fica cinza e diz "Meta não configurada". Os alertas de domínio continuam coloridos.
- **PR #125 (EX-53 F1a parte 2, Claude):**
  - o "% do orçado" sai de uma conta só, e as Alavancas avisam a falta de meta uma vez;
  - as colunas das listas do Painel ficam alinhadas;
  - o domínio do cumprimento de preventiva (KPI-PCM-05) passa a contar as vencidas, ainda sem cartão.
- **São 58 páginas.** A maioria muda porque a regra única de datas do PR #121 entra no código delas.

## Como conferir
1. **Planejar safra › Editar talhões…:** o seletor tem dois ícones, Ver em tabela e Ver em mapa, e o mapa abre pelo ícone.
2. **Painel › Prioridades:** o título das Alavancas mostra "Meta não configurada" uma vez, e as células não têm cor de meta.
3. **Painel › Manutenção:** as colunas de dias, responsável e verbo começam no mesmo ponto em todas as linhas.

## Conferência (executada)
- **Mesmo estado de partida:** antes do envio, o artefato publicado (versão 148) estava igual ao build limpo do `7aa910df` (v138), conferido por sha256 nos arquivos que a ferramenta mostrou.
- **58 páginas a enviar:** a lista é a diferença entre o build limpo do `452c5afd` e o build limpo do `7aa910df`. O espelho de envio já tinha as 4 páginas da VIS-08 sem que elas estivessem publicadas, por isso a lista não saiu do espelho.
- **Render certo:** o build limpo do `452c5afd` difere do render testado com o PR #124 só nas 3 páginas desse PR (IC, IN-04 e IV), que ficam para a próxima versão.
- **Leitura de volta:** as 58 páginas da versão 151 são idênticas por sha256 ao espelho e ao build limpo (`sha256.txt`).
