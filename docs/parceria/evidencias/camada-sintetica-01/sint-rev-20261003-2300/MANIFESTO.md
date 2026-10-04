# Evidências · SINT-REV-20261003-2300 (correções C01, C02, G01, T01 da CAMADA-SINTETICA-01)

- **Pedido:** retorno consolidado do Codex e do Gemini real, issue 1, comentário 5974392800. Base conferida antes de editar: `99276ee48ebaf039221f3a7bc5b525b02006aa41`.
- **Commits:**
  - reservas nomeadas antes de editar: `5f20cc5`, `d8de28c`, `0033463` (só a RETOMADA);
  - correções: `f3a5e8c` (13 arquivos);
  - estas evidências: commit seguinte.
  - O conteúdo testado é o de `f3a5e8c`: depois do início da cadeia (23:54:45Z) só mudou a RETOMADA, que é documentação.
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux x86_64, Python 3.11, Node 22.22, Chromium 141 (Playwright). Wrapper local `CHROME_BIN` (`--no-sandbox` e `--proxy-server` do proxy oficial; fora do repositório) e CA do proxy na NSS, com a verificação TLS ligada. **Solicitante:** Codex e Gemini (SINT-REV). **Revisores:** Codex e Gemini focal.
- **Cadeia:** `bash /tmp/cadeia2.sh`, a partir de `project/`, `_render/` e `saida/` apagados, de 2026-10-03T23:54:45Z a 2026-10-04T00:09:09Z. A contraprova do T01 (`10-…`) roda logo depois, numa cópia temporária que não fica no repositório.
- **Redação:** os mesmos 3 valores do manifesto anterior viram `<área redigida>` quando aparecem seguidos de "ha": 5 ocorrências em 3 logs, todas no contexto Santa Rita/P2 e provavelmente coincidência numérica. O resultado de cada linha não muda.
- **Antes da cadeia final, sem log preservado:** três tentativas intermediárias, descritas no recibo:
  - primeira, sem o ajuste do `carencia_test`: 85/91;
  - segunda, com o consumo em `Math.round`: 85/91;
  - terceira, só os dois testes: `os_v39_liberar` 14/14 e carência 85/91.
  A sonda `11-sonda-arredondamento.py` reproduziu a causa: o apontamento da área cheia era recusado com "Consumo … acima do que está em custódia" porque JS e Python arredondavam diferente.

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-camada-sintetica/tools/prototipo/v37/gen37/project · menu vigent | 0 | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 14/14 | 0 | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 python3 talmapa_test.py /tmp/evid2/capturas` | 0 | RESULTADO: 8/8 | 0 | `6400bac18cf5d3c7b7a94bbafb10193f9a3fbc6456823f32d91cfdf7a426325b` | `6400bac18cf5d3c7b7a94bbafb10193f9a3fbc6456823f32d91cfdf7a426325b` |
| `06-varredura.log` | `python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `07-decimais-crus.py` | `marca de tempo/resumo` | — |  | 0 | `db096e7cbe61351ee980ac3b5ab8a35a175c6200cd9d26d565cd95b6c08bbd03` | `db096e7cbe61351ee980ac3b5ab8a35a175c6200cd9d26d565cd95b6c08bbd03` |
| `08-resumo.txt` | `resumo impresso por bash /tmp/cadeia2.sh (uma linha por etapa)` | — |  | 0 | `11549d3a0ff06d8227bb8a16dc8ebe675ad5b32cde070d8c0223bf3f6cbb81e2` | `11549d3a0ff06d8227bb8a16dc8ebe675ad5b32cde070d8c0223bf3f6cbb81e2` |
| `10-contraprova-T01-exit.log` | `python3 _t01_contraprova_irr.py   (cópia temporária de irr_estado_test.py com o item 1 forçado a falhar)` | 1 | 37 ok · 1 falhas ['1 sem erro de carga (FALHA FORÇADA NA CONTRAPROVA)'] | 2 | `556fce84dc5474e8a34d42c5b85e302e35271bbb7e4da2d4f7e4491d36c82144` | `1f7e5e339a38b25730002562144849069aaeabb31306d18423ba44b6cde7128a` |
| `11-sonda-arredondamento.py` | `marca de tempo/resumo` | — |  | 0 | `6fdefc1637ec7f2b8c7275bfb68898a14c51d9491ea8bcaa546aaaa70d9ea357` | `6fdefc1637ec7f2b8c7275bfb68898a14c51d9491ea8bcaa546aaaa70d9ea357` |
| `capturas/talmapa_celular.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` |
| `capturas/talmapa_desktop.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` |
| `fim.txt` | `marca de tempo/resumo` | — |  | 0 | `cf42fc5206633917f487454d644bc1a8d98af39c9a4836ddfa42e3f2cb0eea37` | `cf42fc5206633917f487454d644bc1a8d98af39c9a4836ddfa42e3f2cb0eea37` |
| `inicio.txt` | `marca de tempo/resumo` | — |  | 0 | `edb8f00e447c0ad16f057bfacbffeaf61606e4e05e75b2ab0f2d0734dfe029c0` | `edb8f00e447c0ad16f057bfacbffeaf61606e4e05e75b2ab0f2d0734dfe029c0` |
| `lagoa/carencia_test.py.log` | `CDP_GL=1 timeout 900 python3 carencia_test.py` | 0 | RESULTADO: 91/91 verificações | 0 | `6a98e3bde39f6de7bfa9bfe59ff08f403fae75ba97fc9a302cf1a8e73610a1ee` | `6a98e3bde39f6de7bfa9bfe59ff08f403fae75ba97fc9a302cf1a8e73610a1ee` |
| `lagoa/irr_estado_test.py.log` | `CDP_GL=1 timeout 900 python3 irr_estado_test.py` | 0 | 38 ok · 0 falhas [] | 2 | `d9443ede8b37bf45886b673aadadbfec91344b480ff232e85a34c0542f1e4fd8` | `ada10769140f1943c6f2349943a29111bd0c90cfdf8bd0142479b74a0fbc6e96` |
| `lagoa/irr_fluxo_test.py.log` | `CDP_GL=1 timeout 900 python3 irr_fluxo_test.py` | 0 | 33 ok · 0 falhas [] | 1 | `a198bfef5f4024cfb7e9d8cae7e0d0ccbe26741de5c4b27324345b0ac1c1cb59` | `19e74e78850dc35d8d7d122b33d49c04d74f163ac10d7404d8d8314b57b3a255` |
| `lagoa/map_decisoes_test.py.log` | `CDP_GL=1 timeout 900 python3 map_decisoes_test.py` | 0 | 13 ok · 0 falhas [] | 0 | `6e076bc4e9eb2e07e3a97713f4961db2d68fa72f3fb7b2693d04e337856b6d99` | `6e076bc4e9eb2e07e3a97713f4961db2d68fa72f3fb7b2693d04e337856b6d99` |
| `lagoa/map_irrig_filtro_test.py.log` | `CDP_GL=1 timeout 900 python3 map_irrig_filtro_test.py` | 0 | 15 ok · 0 falhas [] | 0 | `697c962ed12893dd619f02e19537c056f9589ae5588ebd0ba24a1067a5357c92` | `697c962ed12893dd619f02e19537c056f9589ae5588ebd0ba24a1067a5357c92` |
| `lagoa/mip_correcoes_test.py.log` | `CDP_GL=1 timeout 900 python3 mip_correcoes_test.py` | 0 | RESULTADO 14/14 | 0 | `6785a0cae0c59dbeae945829c0d286b80be78f87a5fe35651438860f2a2e3d05` | `6785a0cae0c59dbeae945829c0d286b80be78f87a5fe35651438860f2a2e3d05` |
| `lagoa/mip_fluxo_test.py.log` | `CDP_GL=1 timeout 900 python3 mip_fluxo_test.py` | 0 | RESULTADO 15/15 | 0 | `244963288a57a8537afd8105e4eee74bbd42ea4b591ee1d1b41f1f92e9e2d9b8` | `244963288a57a8537afd8105e4eee74bbd42ea4b591ee1d1b41f1f92e9e2d9b8` |
| `lagoa/mip_unit_test.py.log` | `CDP_GL=1 timeout 900 python3 mip_unit_test.py` | 0 | RESULTADO 34/34 | 0 | `e714f56b5cb58a2d038c3d7e12d89b661c7e5da404ab701e8520eec8e3cc3648` | `e714f56b5cb58a2d038c3d7e12d89b661c7e5da404ab701e8520eec8e3cc3648` |
| `lagoa/os_v39_bloq_test.py.log` | `CDP_GL=1 timeout 900 python3 os_v39_bloq_test.py` | 0 | RESULTADO: 11/11 ok | 0 | `e614cb35f398b043c701a815115caf07da307f3ad974fcc210645acc69ae005d` | `e614cb35f398b043c701a815115caf07da307f3ad974fcc210645acc69ae005d` |
| `lagoa/os_v39_liberar_test.py.log` | `CDP_GL=1 timeout 900 python3 os_v39_liberar_test.py` | 0 | RESULTADO: 14/14 ok | 0 | `19746fa70ccaf31f51a47f13ecc798dc862cf25cac3a4c575b01afdf404446b1` | `19746fa70ccaf31f51a47f13ecc798dc862cf25cac3a4c575b01afdf404446b1` |
| `lagoa/os_v39_selo_agua_test.py.log` | `CDP_GL=1 timeout 900 python3 os_v39_selo_agua_test.py` | 0 | RESULTADO: 12/12 ok | 0 | `8a191e198da65ddf83436f386c86be67e958398bf7005be8f55cc71b9a6dcdf0` | `8a191e198da65ddf83436f386c86be67e958398bf7005be8f55cc71b9a6dcdf0` |

**Limites:**
- Isto é protótipo com dados fictícios. Não é HML, backend nem publicação, e não é auditoria integral da v44.
- **Modo real:** a equivalência foi provada só em memória, com as áreas inteiras implícitas nos literais antigos. Se as áreas reais tiverem decimais, o C01 passa a usá-los de propósito. Isso só se confere no Mac, com a varredura por valor.
- **Risco registrado, não alterado:** dose × área sem arredondar em `cenario.js:152` e `areas/mobile.py:507/525` (app).
- **Histórico:** os literais antigos de área continuam nos commits anteriores das branches limpas. A remediação do histórico é decisão do Codex.
- **Não alterado:** a captura móvel (390 px, controles cortados) fica no bloco de UX vigente, e a aproximação do círculo (+0,58 %) é uma limitação aceita.
