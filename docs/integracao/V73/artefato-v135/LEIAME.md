# Artefato v135 com a v134 (versões 143 a 145, 18/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versões:**
  - 143 (`1792353715-cb6c`, lote 1, 31 páginas);
  - 144 (`1792353736-90e5`, lote 2, 30);
  - 145 (`1792353756-21cf`, lote 3, 6).
- **Fonte:** `76dfe2b8` em `claude/v44-v135-osagrupa`, que reúne:
  - a v134 (`e0c47a00`) e a correção dos 3 S2 do Codex (`91a8ab1d`);
  - o EX-54 F1 (Frentes);
  - o EX-57 F0a/F0b do Codex (`62e13a67`, `75e77324`), que ainda não aparece em tela;
  - os oráculos da v135.

  O render é o build `SAFRION_DADOS=sintetico` desse commit.
- **O que mudou:** 68 páginas mudaram em relação à v133, e nenhuma entrou ou saiu. Ficam fora:
  - `index.html`, igual;
  - `_irr_estado.html`, subproduto local que nenhuma página referencia e cujo nome com "_" é reservado pelo serviço.
- **Conteúdo:**
  - ATIVO-UNICO, SAF-MAPA F1 e AGUA-SOLO-IRR (v134), com os 3 S2 do Codex corrigidos;
  - EX-54 F1, visão Frentes na O.S.

## Conferência (executada)

- **Render:** o render do commit limpo `76dfe2b8` é idêntico ao que a bateria testou (180 arquivos por sha256, 0 diferenças).
- **Espelho:** o espelho local (`site133`) é igual ao render em todos os arquivos.
- **Leitura de volta** da versão 145, comparada com o espelho:

| Página | sha256 |
|---|---|
| OS.dc.html | `c0c55f7f78ad0111c5d82b44adeb3a090f47da4fce2b7b8e8b1716fd59ca2474` |
| SAF.dc.html | `82dfb1405f4e6cd27f5a08392035462649211fc7acea5eb9a021395477d55ce8` |
| IR-01.dc.html | `c3026ff4306bb439eb4f02a84e61acc7483d50cf82b02d0367ce190aa65f13bf` |
| CD-03.dc.html | `1d8d748c5d38123e67d0ac86627eb2027795eb69e78f1b7936791790ed47b15e` |

4/4 iguais. A bateria e a reexecução estão em `docs/integracao/V73/v135/` (LEIAME e `logs/`). Ficam 2 vermelhos antigos, iguais na v134 e já com o Codex: `filtros_cultura` F2 e `tabelas_irr` TABR-CTX-02.
