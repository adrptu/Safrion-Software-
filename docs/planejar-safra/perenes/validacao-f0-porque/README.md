# EX-57 F0 — data no painel Por quê

Codex, 19/10/2026. Base: e4318104b4ce6e3b674fde6fa603b1c291e62683. Revisor/integrador: Claude.
Contrato: PR47, recibos6265546121 e6265682436. Um ajuste de apresentação no painel compartilhado AG-02/SAF; F1–F4 e validação agronômica não são concluídos por esta entrega.

## Problema e correção

Quando a atividade não tinha âncora, a lista explicava “aguarda plantio/colheita”, mas o painel Por quê mostrava apenas “Data: —”. O painel agora usa o helper existente soloDataTexto. Nenhuma data é inventada, e dose, quantidade, custo e motivo de não aplicação permanecem iguais. Não há novo campo, etapa, comando ou menu.

Arquivos de produto/teste: areas/analise_solo.py e datas_consumidores_ocupacao_test.cjs em tools/prototipo/v37/gen37. Helpers solo.js/datas_atividade.js e regras de ocupação não foram alterados.

## Prova executada

Node v24.19.0: node tools/prototipo/v37/gen37/datas_consumidores_ocupacao_test.cjs

Os arquivos de dependência usados no teste têm os mesmos Git blobs da base acima: cenario.js 7220ede39022595c25075a9d7972740f15184b94; producao.js fa9004519fc3112e26b18b2f7a3f6e09ab1e2d7f; solo.js d1966b3998b7d48dd7229eefbbb414a89ad0dded; datas_atividade.js e30ac5966c406ed1bb539c7f5183b8ff4274982d; ocupacao.js 3a97b0c17e90f33db325abd1b416e59cc6ebd9e5.

Contraprova antes da correção: 16 casos existentes passaram; a primeira comparação do painel falhou somente em “Data: —” versus “Data: aguarda plantio”, com dose/quantidade/custo iguais. Bruto: before.txt.
Antes dessa contraprova houve dois ajustes no harness: fornecer a data sintética CEN0 exigida pelo carregamento de cenario.js e corrigir o texto esperado da dose para conservar kg/ha. Não foram defeitos do produto nem justificaram mudar suas regras.

Saída final (exit 0):

```text
7/7 ocupação: ausência não vira plantio/zero; âncora informada/plano canônica
4/4 rótulos de análise do solo preservam data ou explicam ausência
3/3 plano sem âncora não inventa fim nem liberação confirmada
2/2 informar âncora restaura fim canônico do plano
7/7 painel Por quê: âncora ausente/real, negação, dose/quantidade/custo e imutabilidade
```

Total: 23 casos. As sete contraprovas novas cobrem DAP, DAPC, DANC, DATA, tipo ausente, data real e motivo de não aplicação. O teste chama as funções reais extraídas de SOLO_UI_JS e compara também valores/unidades e imutabilidade da sugestão. git diff --check passou.

Limite: prova de funções de apresentação, sem execução nova de navegador/teclado/celular; os controles, foco, layout e eventos não mudam. Reaproveita as verificações anteriores dos controles sem alegar nova prova visual. Não comprova homologação, parâmetros validados pelos RTs, integração real ou publicação.
