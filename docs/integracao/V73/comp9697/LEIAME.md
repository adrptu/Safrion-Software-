# Integração dos PRs #96 (AGRO-10b) e #97 (AGRO-01/OS-05)

- **Autor:** Codex. **Revisor e integrador:** Claude.
- **Composição:**
  - `6f1584b` = `f7b8c8e` + merge de `b61e714` (PR #96);
  - `fa4413a` = `6f1584b` + merge de `17e6208` (PR #97).
  - Nenhum dos dois merges teve conflito.

## Bateria no render de `fa4413a` (executado; dados sintéticos; portão de 1 Chrome)

| Teste | Resultado |
|---|---|
| agro10_estado_test (#96) | PASS |
| agro01_previa_test (#97) | PASS |
| saf_fazendas · saf_multi_fazenda · tabelas_saf | 14/14 · 23/23 · 24/24 |
| tabelas_os · os_cenario | 40/40 · 22/22 |
| paginas_scan | 5 ok, 0 falhas (148 páginas) |

## Sonda de navegador Claude (`sonda_claude_96_97_100.py`)

A sonda rodou na árvore de revisão `4fd5b8b` + #96 + #97 + #100, a 1440 e a 390 px, com teclado.

**Na candidata** (`sonda2_candidata.log`):
- **#96:** o formulário "Editar safra" abre sem o campo Estado e com o nome editável.
- **#97 (PL-04 e CA-01):** o "Conferir caminho de liberação" abre e fecha por teclado; cada O.S. vem com o link para ela, e "Abrir O.S. ›" abre a própria O.S.; nada é gravado; não há rolagem lateral.
- **Falhas que não são destes PRs:**
  - 2 da sonda sobre a coluna Estado: ela já não aparece por padrão na base, e a hipótese da sonda estava errada;
  - 2 do #100, devolvido com A1.

**Na base `4fd5b8b`** (`sonda2_base_4fd5b8b.log`):
- o campo Estado aparece no formulário;
- não há prévia;
- o botão do CA-01det não navega.

## O que não bloqueia

- **#96, S3:** sem o campo, uma safra nova fica sempre "Rascunho", porque nenhuma ação a leva para "Em planejamento". Hoje esse estado não trava nada no protótipo. A ação de avançar o estado (AGRO-10) fica fora deste PR.
- **#97, S4:** no CA-01, a prévia aparece com a seleção e mostra todas as O.S. a liberar, como o próprio texto diz. A seleção, sem outra ação em lote, ficou sem uso; sobra para a revisão da tela.
