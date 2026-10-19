# Evidências · SINT-C03 (comentário 5974993475): regra única de quantidade de insumo

- **Correção isolada:** commit `45b34c7`. A reserva foi registrada antes, em `b8d3fb0`. A base é `e10b4ae` (candidata da SINT-REV, `f3a5e8c` + evidências).
- **Regra:** quantidade = dose × área em decimal exato, 2 casas, meio para cima (`quantidade.py` ⇄ `cenQtd`). Consumo de cada apontamento = quantidade(acumulado depois) − quantidade(acumulado antes) (`cenQtdTrecho`), de modo que a soma fecha no total e a custódia zera. Não há tolerância nova.
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux, Python 3.11, Node 22.22, Chromium 141. Wrapper local `CHROME_BIN` e CA do proxy na NSS, com TLS ligado.
- **Cadeia:** `bash /tmp/cadeia3.sh`, a partir de saídas apagadas, de 2026-10-04T00:32:59Z a 00:47:25Z. O conteúdo testado é o de `45b34c7`: depois do início, só mudou a RETOMADA.
- **Redação:** a mesma regra conservadora dos manifestos anteriores (3 valores possivelmente reais seguidos de "ha").

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-camada-sintetica/tools/prototipo/v37/gen37/project · menu vigent | 0 | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 14/14 | 0 | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 python3 talmapa_test.py /tmp/evid3/capturas` | 0 | RESULTADO: 8/8 | 0 | `6ff6bbc8194dc59e14c45bcd8a4061c234f7dd247f3d7ccb5b2e5e9194ff7c21` | `6ff6bbc8194dc59e14c45bcd8a4061c234f7dd247f3d7ccb5b2e5e9194ff7c21` |
| `06-varredura.log` | `python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `08-quantidade_test.log` | `python3 quantidade_test.py` | 0 | RESULTADO: 6/6 | 0 | `1874ef91399168355836f8e44644bff3d5f75928a79baae0d0971efdb2e3d1e9` | `1874ef91399168355836f8e44644bff3d5f75928a79baae0d0971efdb2e3d1e9` |
| `09-resumo.txt` | `marca de tempo/resumo` | — | 15 ok · 0 falhas [] | 0 | `2416b60b8958a8405c821528cf771fce463387f5e184f7e69c1fdc885deeac5f` | `2416b60b8958a8405c821528cf771fce463387f5e184f7e69c1fdc885deeac5f` |
| `capturas/talmapa_celular.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` |
| `capturas/talmapa_desktop.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` |
| `fim.txt` | `marca de tempo/resumo` | — |  | 0 | `d5992657f194e6598a6a86c2061428218cb63b19eaabfe4c3ba866d81e6cf0ff` | `d5992657f194e6598a6a86c2061428218cb63b19eaabfe4c3ba866d81e6cf0ff` |
| `inicio.txt` | `marca de tempo/resumo` | — |  | 0 | `e7a1b5f7e6093838fbbe8beebeab72388f346231cbee1cdb00ea42a993dbda69` | `e7a1b5f7e6093838fbbe8beebeab72388f346231cbee1cdb00ea42a993dbda69` |
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
- Isto é protótipo, não HML. A regra no sistema real deve viver num único serviço de domínio com tipo decimal (ENG-011/013).
- Linhas de Santa Rita com consumo literal nas requisições (`dados2.REQUISICOES`) não foram alteradas.
- A equivalência do modo real foi provada em memória, só para áreas inteiras.
