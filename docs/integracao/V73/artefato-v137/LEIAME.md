# Artefato v137 (versão 147, 18/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 147 (`1792361592-0e5f`), um lote com 10 páginas.
- **Fonte:** `aa506fc2` em `claude/v44-v135-osagrupa`. O render é o build `SAFRION_DADOS=sintetico` desse commit.
- **O que mudou:** 10 páginas em relação à v136. Nenhuma página entrou ou saiu, e o `index.html` fica igual.
  - `OS.dc.html`: visão Mapa (EX-55 F1) e a faixa de recorte no Mapa e nas Frentes.
  - `AG-01.dc.html`: visão Mapa em Pragas e doenças.
  - `IR-01.dc.html`: visão Mapa em Irrigação.
  - `SAF.dc.html`: a 2ª linha do rótulo do mapa aparece.
  - `IN-04.dc.html`: mesma saída (coleta A2 60/60). O código da Irrigação passou a vir de uma fonte única.
  - `IN-03.dc.html`, `IR-02.dc.html`, `IR-03.dc.html`, `IR-03det.dc.html` e `IR-04.dc.html`: carregam o mesmo código da Irrigação (`irrigacao_estado.js`).

## Como conferir

O roteiro está em `docs/mapa/EX-55-F1/LEIAME.md` («Como conferir no artefato»).

## Conferência (executada)

- **Render:** o build do commit limpo (`git worktree` em `aa506fc2`) é idêntico ao render testado: 179 arquivos por sha256, 0 diferenças. O render testado tinha a mais só a página de sonda `_irr_estado.html`, que não vem do build. Os testes estão em `docs/mapa/EX-55-F1/logs/`.
- **Espelho:** o espelho local é igual ao render em todos os arquivos do render.
- **Leitura de volta** da versão 147, comparada com o espelho e com o render limpo:

| Página | sha256 |
|---|---|
| AG-01.dc.html | `800cbc6a1c81af7cd722ba1e343811b30d6f08a2834bd41d7b34d9421e5707f4` |
| IN-03.dc.html | `3efacb6dbce9286eb929ef754f5babe272bc6d96e69495a735e622c4ed4cb3c9` |
| IN-04.dc.html | `b05e8823bc562370a5c9f886df044ccb8ad2d8ea4cd5a923798586ab7967ff38` |
| IR-01.dc.html | `703e39c2e499474a0858a3594e2c4868c9ceeb174aedcd0b6e1c5483c2fb2ef5` |
| IR-02.dc.html | `6df2be9c661ca80da3f3c4847f4c0d7f5d41e8d3bb82acfd07c2cb7c49443e9c` |
| IR-03.dc.html | `036f06c96e77557762c87d22359b4d5a6c9ae1b37bb48d1774f4750459ef427c` |
| IR-03det.dc.html | `2f3bd54ee2ac68c2d15733f7a09c0cf788bfc2df3208dc311ff3b1df9b4f8edd` |
| IR-04.dc.html | `1df4016948e2384e1e27dd6c20a75b758c5014e8d1a62840d1340bd39b3886a6` |
| OS.dc.html | `872b2a6b295a6c949b9e9790f8a95e566538aed6cdf7fd7a679b778885c771c9` |
| SAF.dc.html | `0b7d73218defa10340154127620eb2a3aa5f1bab2a6901ea54e75491db9ba3b8` |

As 10 páginas são iguais.
