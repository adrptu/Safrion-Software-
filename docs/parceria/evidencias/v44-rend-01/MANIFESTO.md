# Evidências · V44-REND composição (contrato no comentário 5974952517; liberada pelo 5974993475)

- **Branch** `claude/v44-rend-01`, a partir de `0fcc2dc` (candidata CAMADA + SINT-REV + SINT-C03):
  - reserva `0aec48c`;
  - merge **sequencial** `e9fd934` de `prototipo-limpo/v44-rend` `126899e5`; conflito só no `cdp.py`, resolvido mantendo o `CHROME_BIN` portátil da v43;
  - teste unitário portado para node `8ab98c5`;
  - estas evidências no commit seguinte.
  - O conteúdo testado é o de `8ab98c5`: a cadeia rodou com o teste já portado, e depois só mudou a RETOMADA.
- **Executor:** Claude Code remoto, sessão https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh. Linux, Python 3.11, Node 22.22, Chromium 141. Wrapper local `CHROME_BIN` e CA do proxy na NSS, com TLS ligado.
- **Cadeia:** `bash /tmp/cadeia4.sh`, a partir de saídas apagadas. Depois dela vieram os modos `telas`, `bordas` e `bordas2` (`12-rend_*.log`).
  - **Nome enganoso:** `11-rend_telas.log` é o modo **padrão `fluxo`** (itens 1–8, 16 verificações). O modo `telas` (itens 9–11) é o `12-rend_telas.log`.
- **S5:** necessidade 22,5 h e déficit 12,5 h, conferidos no JS (bloco REPARTIR do `safra.js`) e no espelho Python `dados2.repartir`, com Fraction, de forma exata (`10-rend_unit.log`).
- **Redação:** a mesma regra conservadora dos manifestos anteriores.

| Arquivo | Comando | Exit | Resultado | Redações | sha256 publicado | sha256 original |
|---|---|---|---|---|---|---|
| `01-build.log` | `python3 build.py` | 0 | artboards → /home/user/sp-camada-sintetica/tools/prototipo/v37/gen37/project · menu vigent | 0 | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` | `5c61c70f44980491d8a245ddfa312e9af9b514ca18553a47c957cde722fbc0ad` |
| `02-montar_render.log` | `python3 montar_render.py` | 0 | _render montado: 144 páginas + 20 arquivos do site · dados reais locais: 5/5 | 0 | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` | `69cdd56ef9df122f4d536f343ff3ac512b39fdd621c1aec6d5f44fee2001ca55` |
| `03-camada_test.log` | `python3 dados_lagoa_sintetico/camada_test.py` | 0 | RESULTADO: 14/14 | 0 | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` | `25d6f2451350cde7af20047819f52a22309f0d8bf273edaac13290e855459fee` |
| `04-talgeo_test.log` | `node talgeo_test.js` | 0 | RESULTADO: 8/8 | 0 | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` | `81d604fc0cc9833a9e74a2bd21d3999ae9439f7f03e0cacd0fc6e3e47d0afd21` |
| `05-talmapa_test.log` | `CDP_GL=1 python3 talmapa_test.py /tmp/evid4/capturas` | 0 | RESULTADO: 8/8 | 0 | `a1e9c401da4640402ea3e00656a87a6ea20834b0c9efc9bcca488efbcdef6886` | `a1e9c401da4640402ea3e00656a87a6ea20834b0c9efc9bcca488efbcdef6886` |
| `06-varredura.log` | `python3 varredura.py` | 0 | RESULTADO: 144/144 páginas sem erro | 0 | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` | `b1f637c2526410a3816f7737396093a68e56c5fc18b6c87d8ffd84fe7a42e75e` |
| `07-decimais-crus.log` | `python3 /tmp/decimais.py` | 0 | TOTAL 0 [] | 0 | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` | `cdff59294adc6b3eaf185f682b5837a1737f8ee24b18c080cbf6d464875ffab1` |
| `08-quantidade_test.log` | `python3 quantidade_test.py` | 0 | RESULTADO: 6/6 | 0 | `1874ef91399168355836f8e44644bff3d5f75928a79baae0d0971efdb2e3d1e9` | `1874ef91399168355836f8e44644bff3d5f75928a79baae0d0971efdb2e3d1e9` |
| `09-resumo.txt` | `marca de tempo/resumo` | — | 15 ok · 0 falhas [] | 0 | `8761246b9f4dbd3123cf1f6afca8c06fad0090f217f0071121eef62325c92de2` | `8761246b9f4dbd3123cf1f6afca8c06fad0090f217f0071121eef62325c92de2` |
| `10-rend_unit.log` | `python3 rend_multiconjuntos_unit.py` | 0 | RESULTADO: 36/36 OK · JS = bloco REPARTIR de safra.js no jsc · Python = dados2.repartir co | 0 | `a9b51291962c4e5f48b6d1b22f9cb4d51eb2ef69e10068ca2169259195408e0f` | `a9b51291962c4e5f48b6d1b22f9cb4d51eb2ef69e10068ca2169259195408e0f` |
| `11-rend_telas.log` | `python3 rend_multiconjuntos_test.py` | 0 | RESULTADO: 16/16 OK | 0 | `9f171612b7922826a69df64e9a15057a2ef0d8f961c5d536236d19f2c1aa8550` | `9f171612b7922826a69df64e9a15057a2ef0d8f961c5d536236d19f2c1aa8550` |
| `12-rend_bordas.log` | `python3 rend_multiconjuntos_test.py bordas` | 0 | RESULTADO: 10/10 OK | 0 | `f65f27a674d2a620f2d2cc533deed164d09d795caa4a89cd051d1b3b47df514c` | `f65f27a674d2a620f2d2cc533deed164d09d795caa4a89cd051d1b3b47df514c` |
| `12-rend_bordas2.log` | `python3 rend_multiconjuntos_test.py bordas2` | 0 | RESULTADO: 5/5 OK | 0 | `14de206e9292a71250f72f0503e28ed8d76103ef3d61aa7ac85d3e53b82d7320` | `14de206e9292a71250f72f0503e28ed8d76103ef3d61aa7ac85d3e53b82d7320` |
| `12-rend_telas.log` | `python3 rend_multiconjuntos_test.py telas` | 0 | RESULTADO: 4/4 OK | 0 | `d73ffb245c445f69bc738e1d893896a65b3f9ba277be2bc35b0e0819cd0fcf4f` | `d73ffb245c445f69bc738e1d893896a65b3f9ba277be2bc35b0e0819cd0fcf4f` |
| `capturas-rend/rend_depois_celular_plano.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `b2060d251b29387183579df74d2bb85b8644395c324af445d3f7dd6847f11ecb` | `b2060d251b29387183579df74d2bb85b8644395c324af445d3f7dd6847f11ecb` |
| `capturas-rend/rend_depois_celular_rendimentos.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `149587e03696c61aaa34642ff2204e5fb782f0bd2aed1cece9db9b11934aa30d` | `149587e03696c61aaa34642ff2204e5fb782f0bd2aed1cece9db9b11934aa30d` |
| `capturas-rend/rend_depois_conflito.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `252eab7f6b529ad78cec54937c160bee515e7c1d1869c81a9da3678a69dfe5f3` | `252eab7f6b529ad78cec54937c160bee515e7c1d1869c81a9da3678a69dfe5f3` |
| `capturas-rend/rend_depois_form_nova.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `b27e31052b02282e9299b9ab156c718b5315fa73da662842a6a0ecfe26e1d2cb` | `b27e31052b02282e9299b9ab156c718b5315fa73da662842a6a0ecfe26e1d2cb` |
| `capturas-rend/rend_depois_plano_operacional.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `a459e458d3beb05172862016b5d5e5df12bd6c56e361694c3fd45168c423ca5c` | `a459e458d3beb05172862016b5d5e5df12bd6c56e361694c3fd45168c423ca5c` |
| `capturas-rend/rend_depois_rendimentos.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `ea9aacc03ac6f288294687290e1a4ae6ff65045f11b848313d37856ce6bc8362` | `ea9aacc03ac6f288294687290e1a4ae6ff65045f11b848313d37856ce6bc8362` |
| `capturas/talmapa_celular.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` | `7dbf1e818b28f78e860bdc09b83da5681c391a933d08755289f1e13fe8fb1f21` |
| `capturas/talmapa_desktop.png` | `captura de talmapa_test.py (mesmo run de 05)` | — |  | 0 | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` | `185f0f1046284ab3425dc048b5022b62a8f5fca2f875423ac99eb397f0609bb2` |
| `fim.txt` | `marca de tempo/resumo` | — |  | 0 | `5392e3c99c713fccb9f5e47528636b37e1a71a7fa41e5480294fd74c586918f7` | `5392e3c99c713fccb9f5e47528636b37e1a71a7fa41e5480294fd74c586918f7` |
| `inicio.txt` | `marca de tempo/resumo` | — |  | 0 | `45c72976ac5df0aee63cc724d0e9f709e3593a6be424584036c1e358ad19480e` | `45c72976ac5df0aee63cc724d0e9f709e3593a6be424584036c1e358ad19480e` |
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
- Composição para revisão: não é aceite, publicação nem integração definitiva.
- No celular, a tabela larga do plano exige rolagem lateral (`capturas-rend/rend_depois_celular_rendimentos.png`). Isso fica para o bloco de UX/AÇÃO.
- Os números antigos da REND (unit 35/36, fluxo 16/16, telas 4/4) eram relato do Mac. Os valores que valem são estes, re-executados na nuvem.
