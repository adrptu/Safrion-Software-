# Artefato v151 · PA-OPER: três achados da revisão do Codex (19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versões 171 (`1792433405-2caf`) e 172 (`1792433426-124a`), 2 lotes de 30 páginas.
- **Fonte:** `claude/v44-pa-oper-f1` em `c2af319e`. Correção dos três P2 da revisão 6271563229 sobre a v150 (zoom do Mapa, `f285b4a6`).
- **Build publicado:** árvore de publicação fora do git.
  - Os 3 arquivos de código mudados (`operacoes.js`, `areas/processo_planos.py`, `areas/processo_os.py`) são iguais aos da `c2af319e`.
  - Os dados reais da Lagoa Grande ficam só no artefato privado (exceção do proprietário de 19/10; nada real no repositório).
  - `paginas_scan_test` nessa árvore: 5/5 nas 147 páginas, em 2 tamanhos.
  - Os testes de impacto rodaram no build sintético (`pa-oper-f1/brutos/revisao/`).
- **Páginas:** as 60 que mudaram em relação à v150, pelo sha256 do build completo. O `operacoes.js` entra em todas as telas com cenário.
- **Leitura de volta (executada):** as 60 páginas da versão 172 são iguais, byte a byte, às enviadas (`sha256.txt`).

**O que conferir:**
- Agrícola › Planos agronômicos › um produto com bula por 100 L em kg e plano em L: o aviso diz "dose não conferida", sem ⛔.
- Uma O.S. de cultivo que ficou numa versão antiga do plano, sem essa versão guardada: a calda aparece "pendente", não a da versão atual.
