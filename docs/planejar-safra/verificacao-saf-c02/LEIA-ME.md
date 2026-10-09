# SAF-C02 · harness do Codex, antes e depois

Achado: Codex, adendo de 09/10/2026 no PR #47 (comentário 6079770308). Correção: Claude, branch `claude/v44-saf-c02`, base `16d6734`.

| Arquivo | sha256 | O que é |
|---|---|---|
| `harness_original.js` | `bc141473d2cc4063652bc7335feaa142f9bc75781f7f4254cbad060dd3725308` | harness do comentário, copiado sem mudança |
| `antes.json` | `0f00e6e1c2c7831536fa426af6aab5843f2fb4750f0dc6ea6951154a35d8a874` | saída bruta na base (`CHECA_HASH=1`, fonte d96875f8…e9677): A 340 h (R2), B 140 h (R4), `same_total: false` |
| `harness_adaptado.js` | `7bcf243e672c229039786ee6236dfd58b8a2010132492f644d3f368bde9db6d4` | mesma fixture; única mudança na linha 14 |
| `depois.json` | `49eb8b9e23b3bdc88eb8ae14d2c90ad44fb40f6b24087ae7b370664518fcf9ce` | saída bruta depois da correção (fonte 1f18e705…cd56a): A 140 h (R4, cita a B2 fora da conta), B 140 h (R4), `same_total: true` |

**Adaptação (linha 14):** a nova assinatura do `capSaf` recebe o período de cada outra safra, para etiquetar as ocorrências dela pela origem. O item de `outras` passa de `{id, nome, oc}` para `{id, nome, ini, fim, oc}`, com `ini` e `fim` de `period[oid]`. Fixture, recursos, meses e saída não mudam. Sem `CHECA_HASH`, porque a fonte mudou.

Comandos (executados; caminhos a partir da raiz do repositório):

```text
V=docs/planejar-safra/verificacao-saf-c02; S=tools/prototipo/v37/gen37/safra.js
CHECA_HASH=1 node $V/harness_original.js $S > $V/antes.json   # na base 16d6734
node $V/harness_adaptado.js $S > $V/depois.json               # depois da correção
```
