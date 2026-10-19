# Evidências · PRE-REV-20261004 na V44-REND (rodadas 1–6), candidata `6afb511`

- **Branch:** `claude/v44-rend-01`, empilhada sobre `claude/camada-sintetica-01`. Base `74893ad` (composição V44-REND), merge da camada `4b75731`, reserva `4c90f31`; rodadas: `6e157c6` (R1–R6), `1688f97` + merge `5393523`, `1f88bf3` + merge `286d1c4`, `9e9cf73` + merge `5e89d98`, `2eeb2e3` + merge `5855254`, `dba9ff0` (B5a), reserva `0ff5b00` e **`6afb511` (rodada 6: W1–W4)**.
- **Pedido:** RETOMADA-20261004-1742 (issue 1, comentário 5982724904) e recibo/decisão 5982995985. Contrato REND no comentário 5974952517 (liberado pelo 5974993475).
- **Vínculo com a publicação:** a versão `1791137438-fa18` do artefato foi gerada de `dba9ff0`. `6afb511` = `dba9ff0` + reserva + W1–W4, só em `safra.js`, `dados2.py`, `rend_multiconjuntos_unit.py` e `RETOMADA-NUVEM.md`.
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux, Python 3.11, Node 22.22, Chromium do contêiner (`CHROME_BIN`), navegador serializado por `flock /tmp/cdp9333.lock`, TLS ligado.
- **Cadeia:** `E=/tmp/evid9 bash 00-cadeia6.sh` na worktree de `6afb511`, a partir de saídas apagadas, de 2026-10-04T18:30:06Z a 19:03:09Z. A execução foi cortada pelo limite de 30 min do executor em segundo plano enquanto `lagoa/os_v39_bloq_test.py` aguardava a trava do navegador (o log dele só tinha o comando); os quatro passos restantes rodaram em seguida com `00-cadeia6-resto.sh` (mesmos comandos, mesmo commit, worktree sem mudança: `retomada.txt`). Nenhum passo concluído foi repetido.
- **Mutantes** (`00-mutantes7.sh`, `14-mutantes.log`): o bloco REPARTIR e o espelho de cada rodada anterior (4c90f31, 6e157c6, 1688f97, 1f88bf3, 9e9cf73, 2eeb2e3 e dba9ff0) contra o oráculo de 82 verificações, e os mutantes de texto R5/R7 nas telas.
- **Revisão adversarial da rodada 5** (`15-revisao-rodada-5.json`, saída bruta do fluxo de revisão do autor, com verificador independente por achado) e **sondas do revisor rodadas contra a R6** (`16-sondas-revisor-r6.log`). Não é revisão do outro agente.
- **Redação:** a mesma regra conservadora dos manifestos anteriores (3 valores possivelmente reais seguidos de "ha" viram `<área redigida>`); um deles é um inteiro de 2 dígitos e também mascara valores sintéticos dos casos do oráculo. sha256 do publicado e do original.

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `00-cadeia6-resto.sh` | `script da cadeia/mutantes` | — | RESULTADO/ok ·/artboards/_render montado/TOTAL' $E/$n.log / tail -1 / cut -c1-140)"; } | 0 | `4bc45edfc1ec97c18177fc21f729b96c0be63485a00f860c625e67d062fae988` | `4bc45edfc1ec97c18177fc21f729b96c0be63485a00f860c625e67d062fae988` |
| `00-cadeia6.sh` | `script da cadeia/mutantes` | — | RESULTADO/ok ·/artboards/_render montado/TOTAL' $E/$n.log / tail -1 / cut -c1-140)"; } | 0 | `d91955e443466d6fe7a1db76bf11c5e25323461ebacf2425afd4d4937b2ef9ec` | `d91955e443466d6fe7a1db76bf11c5e25323461ebacf2425afd4d4937b2ef9ec` |
| `00-mutantes7.sh` | `script da cadeia/mutantes` | — | RESULTADO" / cut -c1-120 | 0 | `544754a1514e0629bd092624f4678b3d17abe62440f2cd0ccc1c615115c66199` | `544754a1514e0629bd092624f4678b3d17abe62440f2cd0ccc1c615115c66199` |
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-camada-sintetica/tools/prototipo/v37/gen37/project · menu vigent | 0 | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 16/16 | 0 | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` | `c02916639501028221f28e7c50a8fb223c4536b8ed27e90f75893ebd470810ae` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 flock /tmp/cdp9333.lock python3 talmapa_test.py /tmp/evid9/capturas` | 0 | RESULTADO: 8/8 | 0 | `f75eaefc08b965f16cba3b4fc2abc80bcdc60ae0be78c62416e785aa4e4c367c` | `f75eaefc08b965f16cba3b4fc2abc80bcdc60ae0be78c62416e785aa4e4c367c` |
| `06-varredura.log` | `flock /tmp/cdp9333.lock python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` | `8ee9e3230540e930394e516c430c5b05e53f16c515439f010641f7f6b81253c1` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `08-quantidade_test.log` | `python3 quantidade_test.py` | 0 | RESULTADO: 13/13 | 0 | `177f3e84336905f60c9efdfa726ed16e52bbfca3edae321973e6a6d57cc754fb` | `177f3e84336905f60c9efdfa726ed16e52bbfca3edae321973e6a6d57cc754fb` |
| `10-rend_unit.log` | `python3 rend_multiconjuntos_unit.py` | 0 | RESULTADO: 82/82 OK · JS = bloco REPARTIR de safra.js no jsc · Python = dados2.repartir co | 4 | `1614713731621039e51d30d4af19468805a56e7f8baece4adb114e9462381c18` | `855bdb05da2dce2bb754af427b37281b7b284f247c5c79334706b7249fcdb4a1` |
| `11-rend_fluxo.log` | `flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py fluxo` | 0 | RESULTADO: 16/16 OK | 0 | `12843e830239807ae394e8457da63a7677cb6e870d60ca2816cc1819e0f71a4d` | `12843e830239807ae394e8457da63a7677cb6e870d60ca2816cc1819e0f71a4d` |
| `12-rend_bordas.log` | `flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py bordas` | 0 | RESULTADO: 10/10 OK | 0 | `4c6bdce406480683729506b7e33bbacdd04c48ecf991d08063411639a6d17c58` | `4c6bdce406480683729506b7e33bbacdd04c48ecf991d08063411639a6d17c58` |
| `12-rend_bordas2.log` | `flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py bordas2` | 0 | RESULTADO: 5/5 OK | 0 | `5a8217edacbf873c6d61127185edca976cdee4ecc0f99e10885f3b86752d308c` | `5a8217edacbf873c6d61127185edca976cdee4ecc0f99e10885f3b86752d308c` |
| `12-rend_telas.log` | `flock /tmp/cdp9333.lock python3 rend_multiconjuntos_test.py telas` | 0 | RESULTADO: 5/5 OK | 0 | `5bdbfb0ce9892c03549e44fbdf92d722957a8ce6c7ab937662d2d2b7003e7d94` | `5bdbfb0ce9892c03549e44fbdf92d722957a8ce6c7ab937662d2d2b7003e7d94` |
| `13-saf_cmp_continuidade.log` | `timeout 900 flock /tmp/cdp9333.lock python3 saf_cmp_continuidade_test.py` | 0 | RESULTADO: 31 ok · 0 falhas | 0 | `aa7b141d0d5247db95f89e5c49d5e160566b5d763ccdd2e2d42abe83b8fe22ff` | `aa7b141d0d5247db95f89e5c49d5e160566b5d763ccdd2e2d42abe83b8fe22ff` |
| `14-mutantes.log` | `bash 00-mutantes7.sh` | — | RESULTADO: 4/5 OK · falhas: 10b LG2627 por mês: área trabalhada com até 2 casas e meses =  | 0 | `13c16401aa862cc6c7244c1d625f817779d29ec58fdb52513f2783fad542fae7` | `13c16401aa862cc6c7244c1d625f817779d29ec58fdb52513f2783fad542fae7` |
| `15-revisao-rodada-5.json` | `saída bruta do fluxo de revisão revisao-rodada-5.js` | — | artboards; montar_render.py exit 0.\n- irr_estado_test.py: 38 ok, 0 falhas.\n- irr_fluxo_t | 1 | `60380ac4ab96b9a1889973572e651a17e38220508e431cdf9a9185adb243bbc7` | `21fffc4180f1b56d2217e8b0a837d2bd3f3df4ecba48e17e62883e875920204d` |
| `16-sondas-revisor-r6.log` | `comandos no próprio log (sondas do revisor)` | — |  | 0 | `637e272974299bdaccdbcef9135c65b6740de208d44690511936e40dfad14c89` | `637e272974299bdaccdbcef9135c65b6740de208d44690511936e40dfad14c89` |
| `fim.txt` | `marca de tempo` | — |  | 0 | `322666a399c518d5af2076a03a893b801766881b0a109295e2fe9b3827b0c139` | `322666a399c518d5af2076a03a893b801766881b0a109295e2fe9b3827b0c139` |
| `inicio.txt` | `marca de tempo` | — |  | 0 | `8035ccbcd2f533f32bf0e2d6f603fc01a83be16aa743eb1285e478dc5f8e039f` | `8035ccbcd2f533f32bf0e2d6f603fc01a83be16aa743eb1285e478dc5f8e039f` |
| `retomada.txt` | `marca do corte e da retomada (00-cadeia6-resto.sh)` | — |  | 0 | `bc3a42f3dae8d9eff9fcbabfad63522e61b0c48abd334540790b4af27671be7e` | `bc3a42f3dae8d9eff9fcbabfad63522e61b0c48abd334540790b4af27671be7e` |
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

| ID | Sev. | Estado | Onde e o quê |
|---|---|---|---|
| R1–R7, T1a–T2c, N1, M1, M2, P1–P5, Q1–Q5, V1–V9 | S2–S4 | corrigidos nas rodadas 1–5, com regressão no oráculo (ver RETOMADA-NUVEM.md) | `safra.js` (bloco REPARTIR), `dados2.py`, `areas/processo_safra.py` |
| B5a | S4 (texto) | corrigido em `dba9ff0`; `bordas2` 5/5 no navegador | pico do grupo de 1 unidade |
| S2 proposto na rodada 5 (triângulo + 4ª configuração com janela maior) | — | **refutado** pelo verificador: regra declarada da maior janela; trocar a regra é decisão do dono do oráculo → aberto (d) | `safra.js:118` |
| W1 | S3 | **corrigido** em `6afb511` (W1a–W1e) | 2 tratores × 2 plantadeiras e trator × implemento (grafos perfeitos) caíam no conservador do componente: 20 em vez de 40 ha, 2 em vez de 200 ha |
| W2 | S3 | **corrigido** em `6afb511` (W2) | grupo que só passa das unidades no plano serializava a divisão (5 + 5 em vez de 10 + 10 ha) |
| W3 | S3 | **corrigido** em `6afb511` (W3a–W3c) | cadeia de 28–30 configurações estourava o teto, serializava tudo (100 em vez de 1.400 ha) e o motivo inventava o pico |
| W4 | S4 | **corrigido** em `6afb511` (W4) | cliques sem teto: 2,1 s em JS e 6,1 s em Python com 30 configurações em trios; agora ≤ 37 ms e ≤ 79 ms |
| (a) (b) (c) (d) | S3 | **abertos para a regra do dono do oráculo (Codex)**, conservadores, descritos na RETOMADA | troca reservada; grupo de `un` frentes serializa todos; "terminam juntas" não monótona; regra da janela do grupo |

Nenhum S1/S2 conhecido.

**Limites:**
- Protótipo, não HML. A regra de rendimento no sistema real fica num único serviço de domínio (ENG-011).
- Trios com 24+ configurações na mesma operação passam do teto de cliques e ficam no conservador do componente, com motivo.
- As sondas aleatórias raramente geram ciclos de 4 ou trator × implemento; esses casos estão no oráculo (W1a–W1e).
- A revisão incluída é a do autor; a revisão de Codex e a contraprova do Gemini são separadas.
