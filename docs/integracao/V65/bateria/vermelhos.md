# V65 · classificação dos vermelhos da bateria completa

**Escopo:**
- Bateria executada uma vez na composição v63 (`int/v62`, `35d00fa`), com dados sintéticos: 179 testes do `gen37`, 4 em paralelo (máquina de 4 núcleos).
- Saída bruta, uma linha por teste: `_resumo.txt`.
- As mudanças posteriores (v64 e v65) rodaram os testes de impacto listados no `README.md`.

**Regra (AGENTS §3.6):**
- Cada vermelho é **defeito do produto**, **teste obsoleto** ou **falha da ferramenta**.
- Corrigir não é afrouxar: a verificação continua reprovando o defeito que protege.
- "Vermelho antigo" quer dizer que já falhava igual na bateria da v58 (`docs/integracao/V58/bateria`).
- Também foram conferidos os testes com saída 0 que imprimem falha: o código de saída sozinho não prova nada.

## 1. Defeito do produto (corrigido)

| Teste | Defeito | Correção | Depois |
|---|---|---|---|
| `ben_fluxo_test` (achado do Codex UX-BEN35-AVISO-01, S3) | A 390 px, depois de salvar a devolução e abrir a entrega, o aviso ficava sobre o "Fechar" do painel; o toque só funcionava depois de o aviso sumir. | O aviso não captura toque (`pointer-events: none`) e, no pé, sobe ao topo quando ficaria sobre um botão, link ou campo à vista (`g2toastLugar`, `g2lib.js`). | `sobra390 conferencia390` 15/15 sem espera. Verificação nova AV: na versão sem a correção, FALHOU 8/9 ("esperou 4 s: Fechar") |

## 2. Teste obsoleto (o produto mudou por pedido registrado; a verificação foi atualizada, não afrouxada)

| Teste | O que mudou no produto | Ajuste | Depois |
|---|---|---|---|
| `config_test` (A14), `plataforma_test` (A14a, A14d) | Um campo de busca por tela (proprietário, 13/10): a 2ª grade busca pelo campo da 1ª. | Um campo visível e as duas grades no mesmo grupo (`data-g2q`). | §5 |
| `links_ocultos_test` (E1b) | Fixture `_pendente.js` do PAINEL-01 (Codex) na pasta das páginas. | Arquivos `_pendente` fora da varredura de links. | §5 |
| `ma_atrito_test`, `ma_planos_test`, `ma_unica_test` | Navegação sem submenus (13/10): Manutenção abre numa tela de entrada com cartões. | Os caminhos passam pelos cartões. | §5 |
| `esttest` | EST-1 (Codex): a mensagem diz "vencido em 08/2026" e "sem quantidade apta para uso". | Texto novo esperado. | §5 |
| `ds_test` (D8, D8b) | Menos texto no Mapa (14/10): a fonte da camada foi para o ⓘ. | Lê a dica do ⓘ. | §5 |
| `os_v39_selo_agua_test`, `os_v39_bloq_test`, `os_irrig_filtro_test` | O ⓘ das regras da tela fica depois do título. | O cabeçalho pula o ⓘ. | §5 |
| `producao_fluxo_test` (AC-01) | O Painel entrou em Agrícola e o Custos e fechamento (GE-03) é o último cartão. | Os cartões de produção aparecem juntos, em sequência. | §5 |
| `solo_ag02_test` (AC-SOLO-18) | Um campo de busca por tela. | Busca pelo campo único. | §5 |
| `praga_alvo_unit_test` (U2) | Coluna Alvos na lista por produto (proprietário, 13/10). | A coluna `alvo` na lista esperada. | §5 |
| `map_aprov_test` (3), `map_decisoes_test` (1, 11) | Menos texto no Mapa (14/10): o indicador diz "A liberar", a fase do Kanban, sem "(agrônomo)". | Texto novo esperado. | §5 |
| `map_decisoes_test` (3), `map_irrig_filtro_test` (3) | Camadas novas: Análises de solo e Colheita (pedido de 14/10). | Lista na ordem da barra. | §5 |
| `tabelas_est_test` (seção 1, NF 4533) | EST-1 (`8d0a86c`, Codex): o "hoje" do Estoque passou a ser a data operacional única da demonstração (26/09), a mesma da O.S., do Mapa e do app. | O teste lê a data de `dados_config.DIA_OP`. | 34/34 |
| `pttest` (DEMO-10 PT-04) | Menos texto: o rodapé da PT-04 virou a dica ⓘ "Regras desta tela". | Lê a dica do ⓘ. | §5 |

## 3. Falha da ferramenta (o produto está certo)

| Teste | Causa | Prova |
|---|---|---|
| `ben_fluxo_test` (rc=1 com 137/137) | Dois modos reaproveitavam o nome `FX`, que é a função dos estados de partida; rodados juntos, o segundo modo quebrava. | Nome próprio (`FXS`); todos os modos em §5. |
| `config_test` | 866 s sob carga de 4 navegadores. | Sozinho: §5. |
| `painel_modulos_test --ui` (Codex) | `document.activeElement` nulo durante a navegação (achado PN-UI-FOCO, enviado ao Codex, autor do arquivo). | Com cópia que trata o nulo: 61/61. O arquivo do Codex não foi alterado. |

## 4. Vermelhos antigos (já falhavam na v58; não são regressão)

| Teste | Resultado | Frente |
|---|---|---|
| `consumo_divergente_test` | rc=1 | tarefa #80 |
| `os_cenario_test` (21/22), `ostest` | "A liberar sem revisão…" | backlog de base verde |
| `intest`, `psfix38test`, `saf38test`, `saftest` | rc=1: telas v38, anteriores à etapa única do Planejar safra | backlog de base verde |
| `testes_pedido`, `agrofit_test` (17/18), `getest`, `vetest` ("OF-103 editada"), `cotest` | falham com saída 0 | backlog de base verde |

## 5. Reexecução depois das correções
Ver a tabela no fim deste arquivo (preenchida com as execuções na v65).
