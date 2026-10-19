# HML-SECRET-07 — duas exceções exatas

Registro de 19/10/2026. Autor da aplicação: Codex. Revisor/integrador: Claude.
Esta evidência acompanha a exceção nos PRs #118 e #123 e pode ser lida sem recuperar commits antigos ou abrir os comentários.
Ela corrige a falta de evidência local apontada na [revisão 5570491406](https://github.com/adrptu/Safrion-Software-/pull/123#discussion_r4312976695).

## Autorização e autoria

O proprietário Adrianus autorizou somente os dois achados abaixo. A transcrição da confirmação direta no canal do Claude, registrada por Claude em 19/10/2026 às 10:24:19 UTC, é:

> Pergunta: “Registro a exceção exata só dessas duas fingerprints, como você aprovou para as 31 do PR #73?”
>
> Resposta do proprietário: “Sim, exceção exata (Recomendado)”.

[Recibo de Claude 6265042151](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6265042151): confirma a coincidência com a autorização anterior e delimita Codex como autor da aplicação nos dois PRs e Claude como revisor. O comentário é o registro feito por Claude da resposta humana, não uma aprovação de autoria do bot.

Histórico preservado:
- [6257438021](https://github.com/adrptu/Safrion-Software-/pull/118#issuecomment-6257438021), 01:02:34 UTC: Codex registrou o “autorizo” do proprietário, restrito às duas fingerprints, inicialmente atribuindo a aplicação a Claude.
- [6258052688](https://github.com/adrptu/Safrion-Software-/pull/118#issuecomment-6258052688), 02:01:02 UTC: cobrança da dependência; não é nova autorização.
- [6258416170](https://github.com/adrptu/Safrion-Software-/pull/118#issuecomment-6258416170), 02:33:26 UTC: Claude confirmou ambos os falsos positivos e solicitou confirmação direta. A dúvida foi resolvida pelo recibo 6265042151 acima, que também atualizou a divisão de autoria.

Não há autorização para regex ampla, exclusão de arquivos/caminhos inteiros, achados novos, alteração da proteção, produção ou gasto.

## Triagem recuperável

As fontes foram recuperadas pelo conector GitHub nos commits imutáveis abaixo. SHA-256 refere-se aos bytes UTF-8 integrais recuperados; os trechos deste registro omitem os valores para não gerar outra ocorrência documental.

### 1. Nome de armazenamento local do protótipo

Fingerprint exata:

```text
6cd9919ac5ede6e43a60e877463bb0f6bd7b7785:tools/prototipo/v37/gen37/sup_politicas.js:generic-api-key:2
```

[Fonte imutável](https://github.com/adrptu/Safrion-Software-/blob/6cd9919ac5ede6e43a60e877463bb0f6bd7b7785/tools/prototipo/v37/gen37/sup_politicas.js): 3.433 bytes, 13 linhas.
SHA-256: `7d60d87965a9000bae384a49257e2ef86580e9437c4412dfb44fbdfd437e7f60`.

Trecho sanitizado observado:

```text
// SU-02: propostas e aprovações do protótipo; perfil de demonstração não é autorização de servidor.
const SUP_POL_KEY=[nome de chave localStorage omitido];
storage.getItem(SUP_POL_KEY)
storage.setItem(SUP_POL_KEY,JSON.stringify(next))
```

Conclusão Codex/Claude: o valor identifica o registro do armazenamento local do protótipo. Seus usos recuperam e persistem JSON; não autenticam serviço, conta ou usuário. Não é credencial. A exceção cobre somente esse achado na linha 2 do commit indicado.

### 2. Reprodução de falso positivo em relatório anterior

Fingerprint exata:

```text
0a9c4a70180c9fcf2ea9f79f2b492ed389b5eae4:docs/integracao/V71/ex38-codex/r2/gitleaks.txt:generic-api-key:1
```

[Fonte imutável](https://github.com/adrptu/Safrion-Software-/blob/0a9c4a70180c9fcf2ea9f79f2b492ed389b5eae4/docs/integracao/V71/ex38-codex/r2/gitleaks.txt): 385 bytes, 2 linhas.
SHA-256: `590f7389d704114ed247ce9228fda3d2b4d57ac4d4e4ad64e52dd0681968e9b2`.

Conteúdo recuperado, com o único valor de chave omitido:

```text
Gitleaks 8.30.1, dir /private/tmp/ex38-r2-scan --redact --no-banner --report-format json.
Delta sem contexto + README/provas: 28474 bytes, no leaks found, exit0, JSON[].
Fontes completos: achado generic-api-key somente cenario.js:6,
CEN_KEY=[nome de chave localStorage omitido], chave localStorage idêntica ao pai e3e017c.
Inspeção confirma falso positivo, nenhuma allowlist/proteção alterada.
```

Conclusão Codex/Claude: o arquivo é um relatório que descreve a chave local do cenário, sem credencial. A exceção cobre somente essa reprodução na linha 1 do commit indicado. A afirmação sobre o scan antigo é conteúdo da fonte, não um scan reexecutado nesta rodada.

## Limites e validação

Somente as duas linhas exatas são acrescentadas ao `.gitleaksignore`. `.gitleaks.toml`, regras padrão, canários, workflow e proteção não mudam. O contrato em `tools/ci/test_gitleaks_excecoes.py` exige a lista exata, sem duplicatas ou curingas.

Evidência da aplicação anterior à correção documental:
- PR #123, HEAD `d87557d39c8d1bd5740070831e1d7112a3acc060`: 8 testes do contrato passaram; 8 mutações (commit, caminho, regra, linha, curinga, adição, duplicação e remoção) foram rejeitadas. Gitleaks 8.30.1 no delta local: nenhum achado.
- Varredura histórica de CI passou nesse mesmo HEAD: [job 118016887843](https://github.com/adrptu/Safrion-Software-/actions/runs/39239588989/job/118016887843).
- A revisão automática de código desse HEAD pediu este registro local; a [revisão de segurança 6265574275](https://github.com/adrptu/Safrion-Software-/pull/123#issuecomment-6265574275) terminou sem achados.

As provas acima identificam o HEAD examinado e não antecipam aceite do novo commit documental. O revisor deve conferir o delta, os checks do HEAD final e integrar o PR do outro. Para repetir o contrato local: `python3 -m unittest tools.ci.test_gitleaks_excecoes -v` (Python 3.11+).
