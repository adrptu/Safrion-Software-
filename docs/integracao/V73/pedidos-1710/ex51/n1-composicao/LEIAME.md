# EX-51 N-1/B-3: revisão do PR #113 e composição do Claude (17/10/2026)

- **Autor do PR #113:** Codex. Head `da83c39a`, base `31680412`, interface final 6241782009.
- **Revisor e integrador:** Claude. Composição em `d238f361` (código) e `bc04d914` (testes), na branch `n1comp` sobre o PR. Integração com a composição publicada (v129) em `intn1`.

## O que o PR #113 entrega (conferido)
- MIP e O.S. no mesmo envelope durável do cenário (`c.mip`), numa gravação estrita só:
  - O.S., DIA, REC/RA, decisão versionada e recibo idempotente (`cenIdem` com resultado).
- Migração da chave antiga sem apagá-la.
- Portas B-3 em `osc_aprovar` e `osc_liberar`, inclusive pelas portas de grupo:
  - recusam receituário ausente, cancelado, duplicado ou divergente (produto, unidade, dose, área, total);
  - erradicação sem produto fica fora, como antes.
- Testes do autor: 6 + 8 + 24 (`n1_*_test.cjs`). Reexecutados: verdes.

## Achados da revisão (corrigidos na composição, com aviso ao autor)

| ID | Sev. | Achado | Correção |
|---|---|---|---|
| R1 | S2 | `mipGet` lança na leitura quando a cópia antiga está ilegível ou incompatível. Com o armazenamento bloqueado, lança `SecurityError` cru. A tela de Pragas e doenças abria sem dados e sem explicação. | Leitura segura: a lista fica vazia e aparece o aviso "Dados ilegíveis" com "Restaurar demonstração". Gravar continua recusado. Armazenamento bloqueado não é tratado como dado ilegível. |
| R2 | S2 | MB-06 sem `cenario.js`: a coleta no app era recusada sem aviso (`mipMudar(null,…)`). | MB-06 carrega `cenario.js`, como previsto no contrato (lado do Claude). |
| R3 | S3 | "Migra uma vez" não se sustentava: depois de "Restaurar demonstração" em O.S., Estoque ou App (`cenReset`), a cópia antiga voltava, com decisões apontando para O.S. que não existem mais. | Marca `…:migrado` depois da 1ª gravação; restaurar no AG-01 também marca. |
| R4 | S3 | O.S. do MIP criada antes da migração ficava travada pelo B-3 sem caminho visível: abrir o AG-01 não gravava, e reemitir é recusado enquanto a O.S. não está cancelada. | A migração acontece ao abrir uma tela de Pragas e doenças (Mapa, AG-01 ou app), uma vez. |
| R5 | — | Chamador do AG-01 (lado do Claude). | Envia autor (perfil ativo), chave `MIP-EMI-<vis>-v<dver>-<nonce>` gerada ao abrir e mantida na repetição (nova quando o conteúdo muda) e `dver`. Sem AL-02, o motivo aparece antes do clique. |
| R6 | — | UI B-3 (lado do Claude). | Selo "Receituário divergente", dono, prazo e bloqueio "Liberar e aprovar bloqueados" com "Abrir Pragas e doenças" na lista, no Kanban e no painel. Quem só aprova não converte esse bloqueio em espera. |
| R7 | S4 | Mensagens com "Ana" fixo ("Ana libera na O.S.", "Responsável técnico: Ana"), enquanto o autor agora é o perfil. | Fica para a próxima fatia; não altera o dado gravado. |
| R8 | S4 | A comparação da string do cenário dentro da transação é síncrona e sempre igual: não protege nada. O comentário do autor já diz que não é trava. | Mantida. A concorrência entre abas segue pendente, como declarado. |
| R9 | S3 | Cenário gravado em versão antiga: o MIP recusa gravar, enquanto as outras telas sobrescrevem. | Mantido (conservador). A saída é "Restaurar demonstração" no AG-01. |

- **Chave do cenário:** o `mip.js` passou a usar a constante de `cenario.js` (`CEN_KEY`) em vez de repetir o nome.
- **Ganchos de teste:** `window.__cen` (O.S.) ganhou as portas de aprovação e de grupo; `window.__mip` ganhou as chaves.

## Grupo no fluxo real
- A O.S. recém-emitida pelo MIP não tem pulverizador alocado. A composição do grupo recusa ("Sem conjunto · alocar pulverizador na O.S.") antes de gravar qualquer coisa (`n1_fluxo_test` N5).
- A recusa do receituário nas portas do grupo está no `n1_recipe_test.cjs`, com a fonte real de `cenGrupoAprovar` e `cenGrupoLiberar`.
- O grupo com O.S. do MIP depois da alocação pelo PCP não foi exercitado no navegador.

## Contraprova (executada)
- `n1_composicao_test.cjs` com o `mip.js` do PR #113 (`MIP_JS=…`): reprova 6 de 7.
- Pelo que a pessoa vê, no render do PR #113 sem a composição (`contraprova-visivel.json`):
  - AG-01: emitir recusa com "Decisão sem autor, chave ou versão";
  - MB-06: a coleta não registra e não avisa;
  - cópia ilegível: o AG-01 não diz nada.
- No render composto:
  - AG-01 emite a OS-0440;
  - MB-06: "Ponto 1 registrado";
  - cópia ilegível: "Dados ilegíveis".

## Bateria integrada (executada, render da composição `6e027f79`)
- 31 testes; resumo em `bateria/resumo.txt` e os brutos em `bateria/`.
- Todos verdes, exceto dois vermelhos já presentes na base v129 (`5466c6d0`):
  - `textos_soltos` 266/267: oráculo obsoleto do CA-01det. O Codex trocou o rodapé por um texto honesto em `d3435d04` (PAINEL-FIXO-1). Oráculo corrigido nesta entrega: 267/267 (`bateria/textos_soltos_test_pos.log`).
  - `mbtest` MB-02 "conteúdo cabe na altura": excesso de 1142 px, igual na base v129 (`../../../artefato-v130/mbtest_base_v129.log`).
- Base verde (`claude/v44-v73-base-verde-1710`, só testes): `aprova_quem_decide` 103/103 e `config_unit` 226/226 nesta composição.

## Pendente
- Aceite de concorrência entre abas (declarado pelo autor).
- R7.
- Grupo com O.S. do MIP depois da alocação.
