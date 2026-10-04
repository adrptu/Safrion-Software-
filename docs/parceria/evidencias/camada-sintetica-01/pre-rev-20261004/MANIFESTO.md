# Evidências · PRE-REV-20261004 da camada sintética/SINT (rodadas 1–5), candidata `3ba5f14`

- **Branch:** `claude/camada-sintetica-01`. Base: `0fcc2dc` (candidata CAMADA + SINT-REV + SINT-C03). Commits da PRE-REV: `b4fbf15`, `94b58fe`, `a53a16f`, `a7ee5d9` (P1–P8); `1988b0e`, `6995717` (Q1–Q6); `fff6051`, `abbef76` (Z1–Z5); `96ed62e`, `a1f653e` (Y1–Y6); `c349594`, `3ba5f14` (X1–X6). Reservas registradas em `tools/prototipo/v37/RETOMADA-NUVEM.md` antes de cada edição.
- **Pedido:** RETOMADA-20261004-1742 (issue 1, comentário 5982724904) e recibo/decisão 5982995985.
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux, Python 3.11, Node 22.22, Chromium do contêiner (`CHROME_BIN`), navegador serializado por `flock /tmp/cdp9333.lock`, TLS ligado.
- **Cadeia:** `bash 00-cadeia5.sh` na worktree de `3ba5f14`, a partir de saídas apagadas, de 2026-10-04T17:36:21Z a 17:53:50Z; nenhum arquivo mudou durante a execução.
- **Mutantes:** `00-mutantes5.sh` (09) em cópia descartável de `3ba5f14`; o complemento `00-mutantes5b.sh` (09b) refaz Y1, que não foi aplicado na 09 por mirar a assinatura anterior a X5, e Q2, que quebrou o teste sem linha de resultado. Todos os mutantes aplicados são mortos.
- **Revisão adversarial da rodada 5** (`10-revisao-rodada-5.json`, saída bruta do fluxo de revisão do autor, com verificador independente por achado). Não é revisão do outro agente.
- **Redação:** a mesma regra conservadora dos manifestos anteriores (3 valores possivelmente reais seguidos de "ha" viram `<área redigida>`); sha256 do arquivo publicado e do original.

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `00-cadeia5.sh` | `script da cadeia/mutantes` | — | RESULTADO/ok ·/artboards/_render montado/TOTAL' $E/$n.log / tail -1 / cut -c1-140)"; } | 0 | `3f7d5a3d1f52b80db38df9a943948b39fd352bd0a219e0633cdecffb0b1007db` | `3f7d5a3d1f52b80db38df9a943948b39fd352bd0a219e0633cdecffb0b1007db` |
| `00-mutantes5.sh` | `script da cadeia/mutantes` | — | RESULTADO)" / cut -c1-160; cp /tmp/.mut.bak $arq; } | 0 | `4b2308831fa5046ee097a696b0fe796390635737d865f949f4c6cd58be8eab1f` | `4b2308831fa5046ee097a696b0fe796390635737d865f949f4c6cd58be8eab1f` |
| `00-mutantes5b.sh` | `script da cadeia/mutantes` | — | RESULTADO)" /tmp/.mut.out / cut -c1-160; echo "[exit $ec]"; [ $ec -ne 0 ] && tail -4 /tmp/ | 0 | `d8e1d3595d380fd0590d935a0e391f9ecf3614199197290ca0b0556d5b7b0db2` | `d8e1d3595d380fd0590d935a0e391f9ecf3614199197290ca0b0556d5b7b0db2` |
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-fix/tools/prototipo/v37/gen37/project · menu vigente: 39 · ocult | 0 | `c904692f8971f76c6023c4c8cd391ec9ce69b8c29180c4cf3010d78888d62dbe` | `c904692f8971f76c6023c4c8cd391ec9ce69b8c29180c4cf3010d78888d62dbe` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 16/16 | 0 | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 flock /tmp/cdp9333.lock python3 talmapa_test.py /tmp/evid7/capturas` | 0 | RESULTADO: 8/8 | 0 | `a1c504c300358ebfafcd4c491c2dcc00b9586299ab4263bb2627aed3a42fcf65` | `a1c504c300358ebfafcd4c491c2dcc00b9586299ab4263bb2627aed3a42fcf65` |
| `06-varredura.log` | `flock /tmp/cdp9333.lock python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `08-quantidade_test.log` | `python3 quantidade_test.py` | 0 | RESULTADO: 13/13 | 0 | `177f3e84336905f60c9efdfa726ed16e52bbfca3edae321973e6a6d57cc754fb` | `177f3e84336905f60c9efdfa726ed16e52bbfca3edae321973e6a6d57cc754fb` |
| `09-mutantes.log` | `bash 00-mutantes5.sh` | — | RESULTADO: 12/13 | 0 | `63c094ae7c2cb11e1449119633f9b45f6609dd6e6e31946beb45c77856c60646` | `63c094ae7c2cb11e1449119633f9b45f6609dd6e6e31946beb45c77856c60646` |
| `09b-mutantes-complemento.log` | `bash 00-mutantes5.sh` | 1 / 1 | RESULTADO: 12/13 | 0 | `c2b78987f3a471c1b266504e422f76c1750e6bbe731473be619ca51cbc35f3fa` | `c2b78987f3a471c1b266504e422f76c1750e6bbe731473be619ca51cbc35f3fa` |
| `10-revisao-rodada-5.json` | `marca de tempo` | — | artboards; montar_render.py exit 0.\n- irr_estado_test.py: 38 ok, 0 falhas.\n- irr_fluxo_t | 1 | `60380ac4ab96b9a1889973572e651a17e38220508e431cdf9a9185adb243bbc7` | `21fffc4180f1b56d2217e8b0a837d2bd3f3df4ecba48e17e62883e875920204d` |
| `fim.txt` | `marca de tempo` | — |  | 0 | `cdc51f01c7c2cfcec5b6e982d59346eb9f160c4d5cacb870f409940d817deefe` | `cdc51f01c7c2cfcec5b6e982d59346eb9f160c4d5cacb870f409940d817deefe` |
| `inicio.txt` | `marca de tempo` | — |  | 0 | `dada05fa49d3c90630a47c63e97f90c985b7d279910c92b5dbd5399827400524` | `dada05fa49d3c90630a47c63e97f90c985b7d279910c92b5dbd5399827400524` |
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
| P1–P8, Q1–Q6, Z1–Z5, Y1–Y6, X1–X6 | S2–S4 | corrigidos, com regressão (ver RETOMADA-NUVEM.md) | `quantidade.py`, `cenario.js`, `mip.js`, `irrigacao_estado.js`, `areas/*.py` |
| U1 | S3 | **aberto** (anterior à rodada 5) | `irrigacao_estado.js:356/96`: fertirrigação v2 depois de avanço de 0,01–0,06 ha não credita o pivô (v1 com 0 m³ sai do grupo) e o painel recomenda nova rega |
| U2 | S3 | **aberto** (anterior à rodada 5) | `irrigacao_estado.js:441`: com passada parcial e outra programada, a v2 soma a passada seguinte no volume mas cobre só o saldo; a passada some e o crédito fica sem sentido |
| U3 | S3 | **aberto** (anterior à rodada 5) | `mip.js:247/261` (e `processo_os.py:316/557/567`): dose ou área não finita (1e999) lança dentro do renderVals e o painel "Decidir controle" some |
| U4 | S4 | **aberto** | `areas/irrigacao.py:431`: cobertura e área do setor com 0–1 casa no IR-03det |
| U5 | S4 | **aberto** | `irrigacao_estado.js:446`: dose da v2 com 1 casa ao lado do total com 2 |

Nenhum S1/S2 conhecido. U1–U5 vão para a próxima fatia da SINT, com regressão.

**Limites:**
- Isto é protótipo, não HML. A regra de quantidade no sistema real fica num único serviço de domínio com tipo decimal (ENG-011/013).
- Três parcelas deixam resíduo de custódia de −1,78e−15 em ponto flutuante; não se afirma "zero exato" em geral.
- A revisão incluída é a do autor; a revisão de Codex e a contraprova do Gemini são separadas.
