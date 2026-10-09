# SAF-C02 · harness do Codex, antes e depois

Achado: Codex, adendo de 09/10/2026 no PR #47 (comentário 6079770308). Correção: Claude, branch `claude/v44-saf-c02`, base `16d6734`.

| Arquivo | sha256 | O que é |
|---|---|---|
| `harness_original.js` | `bc141473d2cc4063652bc7335feaa142f9bc75781f7f4254cbad060dd3725308` | harness do comentário, copiado sem mudança |
| `antes.json` | `0f00e6e1c2c7831536fa426af6aab5843f2fb4750f0dc6ea6951154a35d8a874` | saída bruta na base (`CHECA_HASH=1`, fonte d96875f8…e9677): A 340 h (R2), B 140 h (R4), `same_total: false` |
| `harness_adaptado.js` | `7bcf243e672c229039786ee6236dfd58b8a2010132492f644d3f368bde9db6d4` | mesma fixture; única mudança na linha 14 |
| `depois.json` | `5a463f6bed14ae3d257a9ad93c6c6cfd510cb7192d5054334e8cb7b537ce2506` | saída bruta depois das correções da verificação (fonte 9e329c43…b8b95): A 140 h (R4, cita a B2 fora da conta), B 140 h (R4), `same_total: true`. Só o `source_hash` mudou em relação à saída da 62b0904 (fonte 1f18e705…cd56a, sha256 da saída 49eb8b9e…f9ce) |

**Adaptação (linha 14):** a nova assinatura do `capSaf` recebe o período de cada outra safra, para etiquetar as ocorrências dela pela origem. O item de `outras` passa de `{id, nome, oc}` para `{id, nome, ini, fim, oc}`, com `ini` e `fim` de `period[oid]`. Fixture, recursos, meses e saída não mudam. Sem `CHECA_HASH`, porque a fonte mudou.

**Harness original na correção:** sem `ini` e `fim` nas outras safras, o `capSaf` agora recusa com erro explícito ("capSaf: a safra B chegou sem o período (ini e fim)"), em vez de somar tudo em silêncio e voltar aos 340 h (achado da 3ª verificação). Por isso o original só roda na base.

## Saídas brutas (`saidas/`, correções da verificação)

Executadas com `SAFRION_DADOS=sintetico` (a worktree não tem dado real: `REAL=False`). Caminhos de máquina trocados por marcadores (`<fora-do-repo>`, `<copia-62b0904>`, `<chrome>`). "real" no nome de um caso de teste é o cenário do protótipo, sintético.

| Grupo | Arquivos | Resultado |
|---|---|---|
| Harness | `harness-antes-base16d6734.json`, `harness-original-na-correcao.err.txt` | base: byte a byte igual a `antes.json`; original na correção: erro explícito de contrato |
| Propriedade e simetria (scripts das verificações independentes, fora do repositório) | `simetria-2000-sem20261009.txt`, `simetria-10000-sem777.json`, `txt-3000-*.json`, `min-float-*.json`, `prop3-correcao.json`, `prop-r3-correcao.json`, `semh-*.json` | correção: 0 falhas; `txt` 0 divergências (62b0904: 9); 3 safras: "5 %" nas três vistas (62b0904: "4 %", "4 %", "5 %"); "≥" nas duas vistas |
| Unidade | `capacidade_unit.log`, `capacidade_unit-testes-novos-no-codigo-62b0904.log`, `rend_multiconjuntos_unit.log`, `links_ocultos_test.log`, `camada_test.log`, `camada_test-62b0904.log` | 101/0; testes novos no código da 62b0904: 5 falhas; 106/106; 8/0; 16/17 (o 16, versão do cenário, já falhava na 62b0904) |
| Navegador | `saf_capacidade_simetrica_test.log`, `…-render-62b0904.log`, `varredura.log` e os demais `*_test*.log`, `partest.log` | 38/0 (no render da 62b0904: 10 falhas, só os casos novos); varredura 140/140; demais iguais aos da 62b0904, partest 46/1 (T1-C, vermelho conhecido) |
| Gerador | `build.log`, `montar_render.log` | 140 páginas, 0 FALHA; "dados da Lagoa Grande: sintéticos 5/5" |

Os testes de navegador do SAF (exceto `saf_capacidade_simetrica_test` e a varredura) rodaram sobre o build anterior à troca dos links do PL-03; entre os dois builds só mudou `areas/planejamento.py` (PL-02, PL-04 e PL-05).

Comandos (executados; caminhos a partir da raiz do repositório):

```text
V=docs/planejar-safra/verificacao-saf-c02; S=tools/prototipo/v37/gen37/safra.js
CHECA_HASH=1 node $V/harness_original.js $S > $V/antes.json   # na base 16d6734
node $V/harness_adaptado.js $S > $V/depois.json               # depois da correção
```
