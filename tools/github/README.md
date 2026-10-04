# Fluxo de pull requests

Pedido de Adrianus e reserva: [5985332590](https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5985332590).
Arquitetura revisada por Claude: [5985359084](https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5985359084).
As regras de equipe continuam em [protocolo](../../docs/parceria/protocolo.md).

`fluxo_pr.py` automatiza abertura idempotente de draft, preflight e merge imediato
por SHA. Usa `gh` autenticado **com a identidade existente do executor**, sem ler
ou guardar tokens. Não instala ferramentas, cria contas, muda ruleset, faz push,
atualiza branch, habilita auto-merge, resolve discussões ou emite pareceres.
Não é serviço de plantão. O agente continua sendo responsável pelo acionamento e
por examinar a evidência. Rodar uma cópia revisada do helper; nunca a versão de um
PR não revisado com credencial de escrita. Não executa textos de PR no shell.

## Abrir uma candidata

Depois do push autorizado, indique o commit completo e o corpo salvo em arquivo:

```sh
python3 tools/github/fluxo_pr.py abrir --branch codex/minha-fatia \
  --head-sha COMMIT_COMPLETO --title 'Resultado da mudança' --body-file /tmp/pr.md
```

Busca por repositório, base e branch. Se já existir, retorna o mesmo PR sem
sobrescrever edição concorrente. Um PR fechado/integrado exige outra branch.
POST incerto provoca leitura de volta, nunca novo POST automático. Resultado
ausente ou ambíguo bloqueia. `abrir` cria somente draft; tornar pronto é decisão
do responsável após examinar os aceites, pelo canal existente.

## Recibos reais, sem simulação de identidades

Cada agente registra **um comentário JSON puro na conversa do PR**, a partir de
sua execução/análise real. Texto citado, bloco de código ou simples ACK não vale.
O autor apresenta evidência; os outros dois apresentam revisão e contraprova.
Exemplo de forma (valores ilustrativos, não constituem recibo):

```json
{
  "schema": "safrion-review-v1",
  "repo": "adrptu/Safrion-Software-",
  "pr": 123,
  "head_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "base_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "author": "codex",
  "agent": "claude",
  "role": "reviewer",
  "model": "modelo real registrado pelo executor",
  "verdict": "pass",
  "blocking_findings": [],
  "raw_evidence_analyzed": true,
  "executions": [{
    "requester": "claude", "executor": "executor identificado",
    "result": "comando, resultado e alcance analisados",
    "evidence_url": "https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-123",
    "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  }],
  "limits": ["limites pertinentes da prova"]
}
```

O coordenador reúne no `pedido.json`: `repo`, `pr`, `head_sha`, `base_sha`,
`author`, `integrator` e `receipts` (lista de três objetos com `comment_id` e
`sha256` do corpo UTF-8 exato retornado pela API). Agentes permitidos: `codex`,
`claude`, `gemini`; papéis únicos: `author`, `reviewer`, `counterproof`.
Um recibo estruturado posterior para a mesma candidata substitui o anterior, inclusive se bloquear. A conversa inteira é paginada; comentário narrativo fora do formato precisa ser tratado pelo integrador.
Uma mudança de HEAD/base ou edição do recibo invalida o pedido; reaproveitar
provas pertinentes exige novo parecer explícito sobre a composição atual.

**Limite de confiança:** a conta GitHub compartilhada não autentica qual IA
atuou. O helper verifica forma, origem do comentário, hashes e candidata; não
certifica que a IA leu/executou o que declarou, nem analisa semanticamente logs,
URLs ou todos os achados. O integrador independente confere isso nos canais reais
antes de montar o pedido. O SHA da evidência é rastreio, não download/verificação
automática do conteúdo. Não chamar esses recibos de três aprovações nativas.

## Conferir e integrar

```sh
python3 tools/github/fluxo_pr.py verificar --pedido /tmp/pedido.json
python3 tools/github/fluxo_pr.py integrar --pedido /tmp/pedido.json --head COMMIT_COMPLETO
python3 tools/github/fluxo_pr.py integrar --pedido /tmp/pedido.json --head COMMIT_COMPLETO --executar
```

Os dois primeiros comandos só leem. O terceiro coleta de novo, valida e faz um
único PUT com SHA esperado. Autor não integra próprio PR. O integrador real deve
ser o agente indicado, não um nome fornecido pelo autor. `verificar --snapshot`
serve para análise/teste ou conector oficial: nunca alimenta a mutação `integrar`.
Snapshot vence em 120 segundos. O conector pode usar os `merge_arguments` após
releitura equivalente; não guardar uma decisão `eligible` para outra retomada.

Gate: PR aberto, pronto, da mesma origem, base main atual incorporada, estado
clean; política ao vivo igual à versão revisada sem bypass; todos os checks
obrigatórios executados com success no HEAD/app exatos; três recibos e papéis;
nenhuma discussão aberta ou revisão nativa solicitando alterações. Skipped,
neutral, erro, paginação incompleta e ausência de dado bloqueiam. Mudança da
política bloqueia para revisão, em vez de aceitar silenciosamente menos checks.

O SHA do PUT impede troca de HEAD. A API não fornece compare-and-swap para base
e recibos. A base é relida antes do PUT e a proteção strict continua obrigatória;
os pais do merge são conferidos depois. Não há promessa de transação atômica
entre comentários, CI e merge. Mudança concorrente observada exige diagnóstico,
sem bypass, atualização automática da branch ou reversão automática.

Em timeout/recusa, relê o PR uma vez. Reexecutar após merge confirmado apenas
confere pais, presença em main e runs de push, sem repetir PUT. O JSON resultante
deve ser preservado pelo integrador no PR como recibo de operação. Ausência de
run é estado pendente, não CI verde; a retomada existente confere os runs depois.
Merge não equivale a aceite de HML ou autorização de produção.

## CI e ativação

O helper e testes entram pelos checks existentes; nenhum workflow novo ou
GITHUB_TOKEN de escrita. GitHub informa que esse token exige aprovação para
certos eventos de PR e não dispara os pushes seguintes. Usar a identidade
existente evita introduzir essa dependência, mas **cada execução real** deve
registrar merge, SHA, ator e CI pós-merge. Primeiro merge deste helper é do
Claude, após parecer Codex/Claude/Gemini e checks: o autor não o autoaprova.
Os drafts #32–#37 não ganham aceite por esta entrega. A correção de imagens já
preparada em outro PR continua sendo dependência; não repetir pesquisa de digest.

Teste local sem rede: `python3 -m unittest discover -s tools/ci -p test_fluxo_pr.py`.

Fontes oficiais conferidas em 04/10/2026:
[GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token),
[merge e SHA esperado](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request),
[auto-merge](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request).
