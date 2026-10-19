# Artefato v144 (versões 158–160, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão final:** 160 (`1792408774-5929`), publicada em 3 lotes: versões 158, 159 e 160, com 66, 64 e 17 páginas.
- **Fonte:** `e4318104` em `claude/v44-v135-osagrupa`. Reúne os PRs #133, #134 e #135, todos de autoria do Claude e integrados pelo Codex com pareceres favoráveis no HEAD (`a417e284`, `761448b5` e `a2e36e37`).
- **Árvore:** `49e5cca4`, idêntica à da composição de prova em que a bateria rodou.

## O que mudou
- **Mapa › Colheita e produtividade (P5, PR #133):** o rótulo do pivô segue a unidade de produtividade escolhida. Em kg/ha, o Pivô 19 mostra o mesmo número da Previsão e colheita. O rótulo composto ("em colheita · … kg/ha · estimativa") cabe inteiro a 1440 e a 390 px.
- **Painel › Manutenção › Backlog da oficina (D11b, PR #134):**
  - **Semanas equivalentes:** o cartão mostra, por especialidade, as horas do backlog ÷ as horas semanais configuradas em Configurações › Capacidade semanal.
  - **Sem capacidade:** a dica diz o motivo ("não configurada" ou "a revisar").
  - **Pessoa que sai do cadastro com dedicação ativa:** suspende o total da especialidade até alguém retirar a dedicação na CF-06, com versão e histórico.
- **Alvo de toque (F3, PR #135):** o "×" de fechar desenhado à mão nos painéis do Mapa passa a ter 44 px no toque, pela regra comum do motor.
  - **Por que 147 páginas:** a regra comum entra em todas as telas, por isso todas as páginas mudaram.

## Como conferir
1. **Mapa:**
   - escolha a Lagoa Grande e a função Colheita e produtividade;
   - em Previsão e colheita, troque a unidade do Mamão para kg/ha;
   - de volta ao Mapa, o Pivô 19 mostra o valor em kg/ha.
2. **Configurações › Capacidade semanal:**
   - dê 30 HH/semana de Mecânico ao Zé;
   - no Painel › Manutenção, o Backlog da oficina mostra "Mecânico 11,5 (0,4 semana)".
3. **Saída do cadastro:**
   - em Cadastros › Pessoas, retire o Zé;
   - o cartão diz "capacidade a revisar (pessoa saiu do cadastro…)";
   - na CF-06, a linha do Zé aparece só para retirar a dedicação.

## Conferência (executada)
- **Diferença para a v143:** 147 páginas, comparadas com o build limpo da v143 publicada. O publicado antes do envio era idêntico a esse build, conferido por sha256.
- **Bateria no build da árvore `49e5cca4`** (brutos nesta pasta; resumo em `bateria_resumo.log`). Todos os testes passaram:

| Teste | Resultado |
|---|---|
| `pg_cap_motivo_unit` | 10/10 |
| `man_backlog_unit` | 23/23 |
| `mapa_colheita_unid_unit` | 6/6 |
| `capacidade_unit` | 101/101 |
| `mapa_rotulo_corte` | 5/5 |
| `mapa_rotulo_real` | 6/6 |
| `alvo_fechar` | 6/6 |
| `cf06_orfa` | 6/6 |
| `ma_semanas` | 5/5 |
| `ma_backlog` | 5/5 |
| `painel03` | 54/54 |
| `config` | 90/90 |
| `ds` | 72/72 |
| `mapa_mux_f1` | 43/43 |
| `mapa_mux_f2` | 29/29 |
| `colheita_mapa` | 7/7 |
| `paginas_scan` | 5/5, nas 147 páginas |

- **`producao_fluxo` 93/93.** Na v143 o resultado era 92/93: o AC-h, a camada do Mapa que não seguia a unidade escolhida, é exatamente o defeito que o P5 corrige.
- **Leitura de volta:** as 147 páginas da versão 160 são idênticas ao build por sha256 (`sha256.txt`).
