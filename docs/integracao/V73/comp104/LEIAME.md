# Revisão e integração do PR #104 (PAINEL-FIXO-2), executada em 17/10/2026

- **Candidata:** a composição 5bb8f5e com o merge de 2e94a49 (worktree `rev104`, árvore igual à integrada aqui).

| Prova | Resultado | Bruto |
|---|---|---|
| `painel_fixo_2_test.py` do Codex, contra a base 5bb8f5e | PASS | `painel_fixo_2_test.log` |
| Painéis com confirmação de texto fixo (`paineis_estaticos.py`, render inteiro) | menu: base 4 → candidata 0; ocultas: 28 → 28 | `paineis_base_5bb8f5e.out`, `paineis_candidata.out` |
| Sonda do Claude (`sonda104.py`), 1440 e 390 | 48 OK · 0 falhas | `sonda104b.log` |
| `credito_menu_test` | 26/26 | `credito_menu_test.log` |
| `links_ocultos_test` | rc=0 | `links_ocultos_test.log` |
| `paginas_scan_test` | 5 ok · 0 falhas (148 páginas) | `paginas_scan_test.log` |

**O que a sonda confere:**
- Os 4 botões, acionados pelo teclado, mostram a prévia "nada foi alterado" sobre o assunto certo. Nada é gravado no navegador e não aparece confirmação fictícia nem painel lateral.
- Em CA-02, "Abrir O.S." (no "⋯") leva à OS-0417.
- Em GE-08, "Registrar liberação da 2ª parcela" (no "⋯") não libera parcela.

**Primeira execução da sonda:** 38 OK e 6 falhas, todas da própria sonda.
- Ela clicava em tudo que estava recolhido, o que abria painéis.
- Ela não abria o "⋯" onde ficam "Abrir O.S." e a 2ª parcela.

A sonda foi corrigida para abrir só o menu ou o bloco que contém o controle. O bruto da primeira execução não foi versionado.

**Achado S4, sem bloquear:** `getest.py`, uma sonda legada de 03/10 fora das baterias, ainda espera PP-014 e "Enviar ao credor".
