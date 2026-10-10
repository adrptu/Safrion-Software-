# Pacote de revisão da frente DOM (B-R8 e COLH-C01)

Fonte recuperável para revisão isolada, antes da integração (pedido do Codex em 6090240891 e 6090966236). Nada aqui é código integrado: a frente ainda não entrou na branch única. Ela entra depois do BEN corrigido, porque toca os mesmos arquivos de Produção e cenário.

- Frente: branch `claude/v44-dom`, base `ecc8b00`, commit final `1fd8cfa` ("DOM: correções da revisão").
- `commits.txt`: os 6 commits, `ecc8b00..1fd8cfa`.
- `patches/`: um `git format-patch` por commit. Para reproduzir: `git am patches/*.patch` sobre `ecc8b00`.
- `diff-ecc8b00-1fd8cfa.patch` e `diffstat.txt`: diff inteiro (18 arquivos, +886 −77).
- `relatos.md`: relatos de implementação, revisão adversarial (1 S2 e 4 S3 na B-R8) e correção (todos tratados; a emissão da O.S. de reaplicação fica como próxima fatia).
- `brutos/`: 113 logs já executados pela frente (unidade, navegador, base). Caminhos da máquina trocados por marcadores; dados sintéticos.

**Rodada 1 da revisão (DOM-REV-20261009-01, 6091211425).** S3 do rascunho do outro dia corrigido em `c764de9`; patch, diff e brutos (antes FALHA, depois 21/21) em `rev01/`.
