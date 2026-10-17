# Recibo da publicação do artefato v124/v125 (17/10/2026): SU-08 com perda pelo ajuste AL-09 (PR #108)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm.
  - A versão 124 (`1792252831-caf3`) levou as 28 primeiras páginas.
  - A versão 125 (`1792252853-6a54`) levou as outras 28 e é o estado completo.
  - Foram dois envios porque as 56 páginas somam 67 MB, acima do limite de um envio.
- **Páginas reenviadas:** 56.
  - `SU-08.dc.html` traz a mudança da tela.
  - As outras 55 diferem só pela função `cenPerdaNova`, acrescentada ao fim do `cenario.js` (conferido página a página contra o espelho).
  - Antes de enviar, as 56 publicadas foram lidas e eram iguais ao espelho da v123.
- **Leitura de volta por sha256** (6 de 6 conferem):

  | Página | sha256 (início) |
  |---|---|
  | SU-08 | `30ead4f8ad2c` |
  | AG-01 | `9ed5c4fcbe2a` |
  | IR-03det | `f14b49628836` |
  | OS | `680044f24082` |
  | SAF | `83befb0de03c` |
  | EST | `5b36d1e920c2` |

- **Origem:** composição `df887d9`. Contém o PR #108 do Codex (HEAD `550de54`) integrado em `8dceba2` e os meus ajustes em `3d822e4` e `df887d9`.
- **Provas:** `comp108/`.
