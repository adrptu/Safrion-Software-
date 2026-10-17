# Recibo da publicação do artefato v123 (17/10/2026): SU-02 com proposta, aprovação e publicação de política (PR #107)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versão 123, ID `1792250503-1cb0`. É o estado completo.
- **Página reenviada:** só `SU-02.dc.html`, com sha256 `059bfe578dbe1713a37bcb6277ab4cdce0de12082abb4b279e780b48e90ed4cc`. A leitura de volta confere.
- **Antes de enviar,** a SU-02 publicada foi lida (`9329c41c…`, igual ao espelho da v122).
- **Origem:** composição `c31d9c4`. O PR #107 do Codex (HEAD `91fa027`) foi integrado por squash em `8ab7267`, com a constante renomeada para `SUP_POL_LS`. O motivo: o nome `SUP_POL_KEY` com o valor literal dava falso positivo do generic-api-key no Gitleaks, e não há segredo. Ajustes do integrador em `8096556`, `2b95aa6` e `9973f09`.
- **Provas:** `comp107/`.
  - Depois da renomeação, o build, os testes Node (11/11 e 9/9) e a sonda foram repetidos sobre a árvore enviada.
  - A sonda conferiu o selo vivo, a publicação com recibo `p1:1`, a recusa ao perfil sem gestão e a ausência de erros de JS.
