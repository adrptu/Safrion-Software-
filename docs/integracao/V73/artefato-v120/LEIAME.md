# Recibo da publicação do artefato v120 (17/10/2026): prévia do OS-LOTE com insumos e datas

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versão 120, ID `1792234809-f8c8`. Estado completo.
- **Página reenviada:** só `OS.dc.html`, com sha256 `767307ef8c7099b8814ee521865263ae4d0bcbe3233db59f8f659ea6b83a3ff8`. A leitura de volta confere.
- **Origem:** prévia `41f46c6`, montada da composição `8ab68a9` com o PR #105 (HEAD `705efa0`, do Codex), em revisão.
- **Branch única:** `claude/prototipo-v44` = `9e25565`.
- **O que muda para o proprietário:** em "Agrupar operações compatíveis", cada calda já mostra a tabela das O.S. com talhão, área, insumos (produto · dose/ha · total) e datas (início e prazo), antes de escolher. A ação "Agrupar estas 3" fica no cabeçalho do grupo.
- **Provas** (`provas-resumo.txt`):
  - fluxo pelo teclado a 1440 e 390: verde;
  - `os_lote_test`: 32/34;
  - `os_cenario` 22/22, `kanban_raias` 9/9, `quantidade_test` 16/16, `paginas_scan` 5/5.
- **Defeito conhecido (S3):** depois de "Confirmar agrupamento", o Esc não fecha o modal. Foi devolvido ao Codex (6233108926). A integração na composição espera a correção.
