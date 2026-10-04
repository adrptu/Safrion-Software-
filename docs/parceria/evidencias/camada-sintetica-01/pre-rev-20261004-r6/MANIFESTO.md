# Evidências · rodada 6 da SINT (U1–U5), candidata `2ce5a43`

- **Branch:** `claude/camada-sintetica-01` (PR 36). Base: `3ba5f14` (candidata das rodadas 1–5, evidências `25d3c47`). Reserva `ecc94d7` registrada antes de editar; correção `2ce5a43`.
- **Pedido:** RETOMADA-20261004-1742 (5982724904) e 5982995985. Achados da revisão adversarial da rodada 5 (`10-revisao-rodada-5.json`, revisão do próprio autor, com verificador independente por achado; não é revisão do outro agente).
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux, Python 3.11, Node 22.22, Chromium do contêiner (`CHROME_BIN`), navegador serializado por `flock /tmp/cdp9333.lock`, TLS ligado.
- **Cadeia:** `E=/tmp/evid10 bash 00-cadeia5.sh` na worktree de `2ce5a43`, a partir de saídas apagadas, de 2026-10-04T18:38:46Z a 19:03:56Z; nenhum arquivo testado mudou durante a execução (a RETOMADA foi atualizada depois).
- **Mutantes:** `00-mutantes8.sh` (09) em cópia descartável de `2ce5a43`; cada um desfaz uma correção (U1, U2, U3 no MIP, U3 no ajuste, U4, U5) e o `quantidade_test.py` falha no item 14 em todos. O item 14 também falha no código de `3ba5f14` (13/14).
- **Redação:** a mesma regra conservadora dos manifestos anteriores; sha256 do publicado e do original.

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `00-cadeia5.sh` | `script da cadeia/mutantes` | — | RESULTADO/ok ·/artboards/_render montado/TOTAL' $E/$n.log / tail -1 / cut -c1-140)"; } | 0 | `3f7d5a3d1f52b80db38df9a943948b39fd352bd0a219e0633cdecffb0b1007db` | `3f7d5a3d1f52b80db38df9a943948b39fd352bd0a219e0633cdecffb0b1007db` |
| `00-mutantes8.sh` | `script da cadeia/mutantes` | — | RESULTADO)" /tmp/.mut8.out / cut -c1-140; echo "[exit $ec]"; cp /tmp/.mut8.bak $arq; } | 0 | `465311cda3f1967f4d46e9620c53379d8bf05b35015a20b36d722962f0c9554f` | `465311cda3f1967f4d46e9620c53379d8bf05b35015a20b36d722962f0c9554f` |
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-fix/tools/prototipo/v37/gen37/project · menu vigente: 39 · ocult | 0 | `c904692f8971f76c6023c4c8cd391ec9ce69b8c29180c4cf3010d78888d62dbe` | `c904692f8971f76c6023c4c8cd391ec9ce69b8c29180c4cf3010d78888d62dbe` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 16/16 | 0 | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 flock /tmp/cdp9333.lock python3 talmapa_test.py /tmp/evid10/capturas` | 0 | RESULTADO: 8/8 | 0 | `55c0a69b2c392de7eacb092dff73cddf12bc29546d151a8545cd14b92453bee3` | `55c0a69b2c392de7eacb092dff73cddf12bc29546d151a8545cd14b92453bee3` |
| `06-varredura.log` | `flock /tmp/cdp9333.lock python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `08-quantidade_test.log` | `python3 quantidade_test.py` | 0 | RESULTADO: 14/14 | 0 | `036136c372bc1900447c4961941b9ca739015959e200ba8edc239fb36f76615f` | `036136c372bc1900447c4961941b9ca739015959e200ba8edc239fb36f76615f` |
| `09-mutantes.log` | `bash 00-mutantes8.sh` | 1 / 1 / 1 / 1 / 1 / 1 | RESULTADO: 13/14 | 0 | `8a99459ac5180e511e9fa91bd2d7a0e664d4ce964a572e06f5f050c99251f83c` | `8a99459ac5180e511e9fa91bd2d7a0e664d4ce964a572e06f5f050c99251f83c` |
| `10-revisao-rodada-5.json` | `saída bruta do fluxo de revisão revisao-rodada-5.js` | — | artboards; montar_render.py exit 0.\n- irr_estado_test.py: 38 ok, 0 falhas.\n- irr_fluxo_t | 1 | `60380ac4ab96b9a1889973572e651a17e38220508e431cdf9a9185adb243bbc7` | `21fffc4180f1b56d2217e8b0a837d2bd3f3df4ecba48e17e62883e875920204d` |
| `fim.txt` | `marca de tempo` | — |  | 0 | `4d157ce25a17a94b9d408ac8c86181494ced5e47995735f56158ff228e6f3a1c` | `4d157ce25a17a94b9d408ac8c86181494ced5e47995735f56158ff228e6f3a1c` |
| `inicio.txt` | `marca de tempo` | — |  | 0 | `6770c457acaebdf5c465459b7c76b4f292b2711d1010a77ec9673b621808c2c9` | `6770c457acaebdf5c465459b7c76b4f292b2711d1010a77ec9673b621808c2c9` |
| `lagoa/carencia_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 carencia_test.py` | 0 | RESULTADO: 91/91 verificações | 0 | `182e505954cd898bef539f4997125121f3de564bf588c86a4a220efd40359534` | `182e505954cd898bef539f4997125121f3de564bf588c86a4a220efd40359534` |
| `lagoa/irr_estado_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 irr_estado_test.py` | 0 | 38 ok · 0 falhas [] | 2 | `b5cfda603834dce6bd2f5cc9f5876115ffb207d4ccd3b3f0967f00d069d552fc` | `816de624a53e3a3bbf00b609fad3ca259eb53e64eb66a58349b010da1cf64844` |
| `lagoa/irr_fluxo_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 irr_fluxo_test.py` | 0 | 33 ok · 0 falhas [] | 1 | `dfba64ddc91c63a2eb585c1c1e53d42f2699198d2c3e30db90efc3e5142332d3` | `5417f37eae55e5e99439ddc21b19bd490cb2b2a002de414b8417218945d5614d` |
| `lagoa/map_decisoes_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 map_decisoes_test.py` | 0 | 13 ok · 0 falhas [] | 0 | `f3dc918062ac9dddf534e5bcdcd1d66f81ce0252455985c4d8bea3bb56bc50e7` | `f3dc918062ac9dddf534e5bcdcd1d66f81ce0252455985c4d8bea3bb56bc50e7` |
| `lagoa/map_irrig_filtro_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 map_irrig_filtro_test.py` | 0 | 15 ok · 0 falhas [] | 0 | `b27af9aa6a1ef023b42dc905da1073e4e8cfef336b1017be921433f5ec33a2b7` | `b27af9aa6a1ef023b42dc905da1073e4e8cfef336b1017be921433f5ec33a2b7` |
| `lagoa/mip_correcoes_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 mip_correcoes_test.py` | 0 | RESULTADO 14/14 | 0 | `e7074c476de90b24b3b0b1eceb3dd9e77a712ceafd425b41851e05d5ea978c3a` | `e7074c476de90b24b3b0b1eceb3dd9e77a712ceafd425b41851e05d5ea978c3a` |
| `lagoa/mip_fluxo_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 mip_fluxo_test.py` | 0 | RESULTADO 15/15 | 0 | `d9bb34dfd571de113daba461accb91ff7c458a796495ed527841eb1470d77304` | `d9bb34dfd571de113daba461accb91ff7c458a796495ed527841eb1470d77304` |
| `lagoa/mip_unit_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 mip_unit_test.py` | 0 | RESULTADO 34/34 | 0 | `283101b6854665ee36210757a2a26917a1547f89aa9bdd1240edc6ef799ca4b2` | `283101b6854665ee36210757a2a26917a1547f89aa9bdd1240edc6ef799ca4b2` |
| `lagoa/os_v39_bloq_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 os_v39_bloq_test.py` | 0 | RESULTADO: 11/11 ok | 0 | `c2bcd560389095a44c4dc4eed0f67b5a9dd83c4470c79dc6b7f8e05272fedd08` | `c2bcd560389095a44c4dc4eed0f67b5a9dd83c4470c79dc6b7f8e05272fedd08` |
| `lagoa/os_v39_liberar_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 os_v39_liberar_test.py` | 0 | RESULTADO: 14/14 ok | 0 | `dfb13674ede80042cf45f1fe7aa7e1f00b6203a4d8753b767c5a459872cdb91b` | `dfb13674ede80042cf45f1fe7aa7e1f00b6203a4d8753b767c5a459872cdb91b` |
| `lagoa/os_v39_selo_agua_test.py.log` | `CDP_GL=1 timeout 900 flock /tmp/cdp9333.lock python3 os_v39_selo_agua_test.py` | 0 | RESULTADO: 12/12 ok | 0 | `eefbadf68ec60139471cd51fa328ebad512c9d263d706b4aae74886d559372b0` | `eefbadf68ec60139471cd51fa328ebad512c9d263d706b4aae74886d559372b0` |
| `capturas/talmapa_celular.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `8aecb099662515c64de9a757abb3b652ca3e4c2c62ba2e2682be6cbfa00f961a` | `8aecb099662515c64de9a757abb3b652ca3e4c2c62ba2e2682be6cbfa00f961a` |
| `capturas/talmapa_desktop.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` |

## Achados e estados

| ID | Sev. | Estado | Onde |
|---|---|---|---|
| U1 | S3 | **corrigido** (`2ce5a43`) | `irrigacao_estado.js` (irrCreditos) e espelho `dados_irrigacao.py` (_gov): parcial com 0 m³ conta a área coberta; a lâmina vem só de quem tem volume |
| U2 | S3 | **corrigido** | `irrigacao_estado.js` (irrV2Zero): v2 com passada em curso e outra programada é recusada com a orientação do X5, no estado e na prévia |
| U3 | S3 | **corrigido** | `mip.js` (mipChecks) e `areas/processo_os.py` (osc_ajFalta, validação e prévias do ajuste): número não finito vira trava antes de qualquer conta |
| U4 | S4 | **corrigido** | `areas/irrigacao.py` e `irrigacao_estado.js`: 2 casas na cobertura, área e trilha |
| U5 | S4 | **corrigido** | `irrigacao_estado.js`: dose da v2 com até 3 casas (mínimo 1) |

Nenhum S1/S2 conhecido.

**Limites:** protótipo, não HML. Três parcelas deixam resíduo de custódia de −1,78e−15 em ponto flutuante; não se afirma "zero exato" em geral. A revisão incluída é a do autor; a revisão de Codex e a contraprova do Gemini são separadas.
