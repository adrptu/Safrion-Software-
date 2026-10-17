# Recibo da publicação do artefato v122 (17/10/2026): SU-01 com a necessidade da OM (PR #106)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versão 122, ID `1792247938-af12`. É o estado completo.
- **Páginas reenviadas** (as únicas diferentes da v121):
  - `SU-01.dc.html`, sha256 `7a178e8913c11c50582a083232e69e3ea45c259ba1c0296e4a8bd6f2513883af`;
  - `SU-04.dc.html`, sha256 `5c3c960f624c56e2b53ec1d5662e74694b1caa6b8447ef44397aa6fd080b77ae`.
  - A leitura de volta confere nas duas.
- **Antes de enviar,** as páginas publicadas foram lidas e eram as da v121 (`17a8169d…` e `c4e0e687…`, iguais ao render de `df8ee9d`).
- **Origem:** composição `2249b84`. Contém o PR #106 do Codex (HEAD `b0888cc`) integrado em `5697d1a` e o ajuste do integrador em `fea4441`.
- **Provas:** `comp106/`.
- **Observação:** a SU-01 passou de 494 kB para 1,15 MB, porque agora carrega o estado da manutenção (`DM.js_prefixo()`) para ler a OM viva.
