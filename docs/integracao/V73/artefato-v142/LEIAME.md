# Artefato v142 (versões 154 a 156, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão final:** 156 (`1792388225-f56c`). Foram três envios para a mesma URL, porque cada envio leva até 64 MB: versão 154 com 36 páginas, 155 com 69 e 156 com 42.
- **Fonte:** `bb039eb9` em `claude/v44-v135-osagrupa`. É a composição com o PR #129 (D11, integrado pelo Claude com parecer `6260108974`) e o PR #130 (M7a, integrado pelo Codex com parecer `5567257676`).
- **Páginas:** 147, sendo 146 que mudaram e a CF-06, que é nova. Quase todas mudam porque o leitor de metas (`metas.js`) e o item "Metas e limites" do menu entram em todas as telas.

## O que mudou
- **Configurações › Metas e limites (CF-06), nova, do Codex:** o gestor define ou retira a meta de quatro indicadores, com motivo, versão e histórico. Os indicadores são cumprimento de preventiva, custo realizado × previsto, preço de venda × referência e preço de compra × referência.
  - Sem meta, a comparação fica cinza, com "Meta não configurada".
  - Com meta, o Painel › Manutenção (cumprimento de preventiva), o Mapa › Custos e a Inteligência de vendas e de compras ganham a cor e o resultado da meta.
- **Painel › Manutenção › "Backlog da oficina" (KPI-PCM-08), novo, do Claude:** mostra as horas previstas das ordens ainda não executadas.
  - A divisão é por especialidade e por situação: pronto, falta de peça e pendência técnica.
  - Uma ordem sem tempo previsto não vira 0 e aparece como "sem estimativa". As semanas equivalentes esperam a capacidade semanal.
- **Manutenção › Kanban:** a carga das colunas usa a mesma soma e avisa as ordens sem estimativa.

## Como conferir
1. Abra **Painel › Manutenção**. O cartão "Backlog da oficina" mostra "14,5 HH" e, embaixo, "Mecânico 11,5 · Eletricista 3 — pronto 9,5 · pendência técnica 5". A pendência técnica é a OM-0234, em conflito com a OS-0420.
2. Abra **Configurações › Metas e limites › Custo realizado × previsto da execução**. Grave a meta 5 % e a atenção 10 %, com um motivo.
3. Volte ao **Mapa › Custos** e escolha "Realizado × previsto". A legenda passa a "Meta atendida · Atenção à meta · Fora da meta". O Pivô 4 mostra "R$ 10.573 · +0,0 %" e "Meta atendida".

## Conferência (executada)
- **Build limpo:** o build de `bb039eb9` é idêntico ao render em que os testes do M7a rodaram (árvore `3ecb0e06`, 0 diferenças). A árvore é a mesma do `7507876d`.
- **Diferença para a v141:** 146 páginas mudam e uma é nova (`CF-06.dc.html`), comparadas com o build limpo da v141 publicada. Antes de sobrescrever, a listagem do artefato conferiu que o publicado era a v141.
- **Leitura de volta:** as 147 páginas da versão 156 são idênticas ao build limpo por sha256 (`sha256.txt`).
- **Testes:** em `../pr129/` (D11) e `../ex53-m7/` (M7a, com a correção dos três componentes em `logs/tres-componentes/`).
