# Recibo da publicação do artefato v130 (17/10/2026): receituário do MIP na O.S. (N-1/B-3) e base verde

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versão 134 (`1792281471-f538`), num envio só.
- **Antes de enviar:** o espelho tinha o estado da v129 (versão 133).
  - Mudaram 11 páginas: AG-01, AG-01det, AG-03, AG-04, IN-04, LO-02det, MB-06, OS, PAGR, PMAN e PSUP.
  - As outras 137 páginas e os arquivos de apoio são iguais byte a byte e não foram reenviados.
- **Leitura de volta, sha256 igual ao espelho:**

  | Página | sha256 |
  |---|---|
  | `AG-01.dc.html` | `3935a0ca…` |
  | `MB-06.dc.html` | `bdffda8e…` |
  | `OS.dc.html` | `1e746b06…` |
  | `PAGR.dc.html` | `da6d6706…` |

- **Origem:** `6e027f79` (worktree `intn1`) = composição `5466c6d0` + PR #113 (`da83c39a`) + composição do Claude.
  - O que a composição acrescenta ao PR #113: emissão pelo AG-01, coleta no MB-06, selo e bloqueio B-3 na O.S., leitura segura e migração única.
  - Os commits seguintes (`35b8b040`, `98788456`, `dcc174c3`) só mexem em testes e documentos; a montagem do produto é a mesma.
- **Montagem:** `_render` às 22:42:02 UTC, depois do commit `6e027f79` (22:41:42), com a árvore do produto limpa.
- **Provas:**
  - bateria integrada de 31 testes: `../pedidos-1710/ex51/n1-composicao/bateria/resumo.txt`;
  - achados e contraprova: `../pedidos-1710/ex51/n1-composicao/LEIAME.md`.
- **Vermelhos antigos:**

  | Teste | Na base v129 | Nesta versão |
  |---|---|---|
  | `aprova_quem_decide` | 102/103 | 103/103: oráculo do seletor com o perfil "todos os papéis" (`1b5a4acd`) |
  | `config_unit` | 216/226 | 226/226: fixture emite OS-0699/0698, fora da semente nova (`35b8b040`) |
  | `textos_soltos` | 266/267 | 267/267: oráculo do CA-01det segue o rodapé honesto de `d3435d04` (`98788456`) |
  | `mbtest` MB-02 "conteúdo cabe na altura" | excesso 1142 px (`mbtest_base_v129.log`) | igual, sem regressão; fica para a próxima rodada da base verde |

  - O `mbtest` termina com código 0 mesmo com 1 falha. O executor não sinaliza a falha pelo código de saída.
