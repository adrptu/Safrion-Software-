# RX-1 — núcleo de comparação e seguimento

19/10/2026 · Codex autor · Claude revisor/integrador · base `d022c74524a7bcb349c05dd25cc13c2ec9cb472d`.
Partilha: PR47/6266132270; confirmação e localização da F1b: 6266180436. A F1b está especificada, sem código integrado. Não tratar AG06 com linhas fixas como comparação funcional.

## Entrega e limite

Primeira parte executável do RX-1: função pura `RaioxComparacao.analisar(dados, contexto, parametros, pedido)`. Arquivos novos `raiox_comparacao.js`, `raiox_comparacao_test.cjs` e este documento. Não altera fonte MIP, agronomia, mapas, persistência, fórmulas do RX-0 nem fontes reais. Não habilita nova tela. O RX-1 completo depende do adaptador F1b e da revisão independente do núcleo e do método demonstrativo de agregação; não dispara auditoria integral.

Fonte de regras: `docs/integracao/V73/RAIOX-ALVO/rx0-contrato-proposta.md`, EST-3a/3b e Δ17/10-2; EX42/V71 §11 e casos T7/T8 em MAPA-MIP-PROD. Referência histórica do confronto, sem repetir o gerador ou transformar seu diagnóstico em validação causal. A F1b futura substitui as linhas fixas EF017–EF021 em `areas/agronomia.py`; `mipPos` agenda a leitura pós e não calcula comparação. Esses dois arquivos permanecem fora desta autoria.

| Entidade/nível | Estado devolvido | Próxima ação do consumidor |
|---|---|---|
| Aplicação / detalhe → comparação | Sem fonte/ordem válida | Abrir a fonte e corrigir o dado indicado |
| Comparação / subdetalhe | Controles insuficientes | Mostrar candidatos, exclusões e leituras; não relaxar filtros |
| Comparação / subdetalhe | Agregação pendente | Exibir razões por controle como diagnóstico; não publicar percentual agregado |
| Comparação / subdetalhe | Disponível demonstrativo | Exibir método, controles/fontes, interpolação e faixa descritiva; abrir a fonte |
| Seguimento / subdetalhe | S1–S6/S5a/S5b | Mostrar leituras, intervalo ou última leitura e motivo; preservar contexto |

## Contrato da função

- `contexto`: `org`, `fazenda`, `cultivo`, `safra`, `alvo`, `corte` explícitos. Não é autorização de acesso: o futuro adaptador deve obter somente fontes permitidas ao usuário.
- `dados`: listas completas de versões de `leituras` e `aplicacoes` de defensivos no universo autorizado. Leituras e aplicação principal ficam no alvo selecionado; a checagem de interferência e o encerramento do seguimento recebem também aplicações de defensivos para outros alvos no mesmo contexto de organização/fazenda/cultivo/safra. Não misturar adubação ou irrigação nesta lista de defensivos. Uma fonte contém os cinco campos de contexto, `talhao`, `id`, `versao` inteira positiva, `evento`, `disponivelEm`, `precisao: 'instante'`, `estado`. Instantes UTC canônicos `YYYY-MM-DDTHH:mm:ss.sssZ`; o adaptador fará a conversão do fuso da fazenda. Dias sem ordem não podem ser promovidos a meio-dia fictício.
- Leitura: `valor` numérico finito não negativo, `unidade`, `protocolo` identificando a versão, `estadio`, `avaliador` pseudônimo. Só `estado: 'completa'` forma par. Ausência não vira zero. Aplicação: só `estado: 'confirmada'` inicia episódio; cancelamento substitui versão anterior. Manejo conhecido parcial/pendente não comprova ausência de interferência.
- Seleciona maior disponibilidade até o corte por chave completa. A identidade da leitura inclui alvo; a identidade da aplicação é org/fazenda/cultivo/safra/talhão/id, sem alvo, para que corrigir o alvo não duplique o evento. Duplicidade de versão/disponibilidade é inválida, independentemente da ordem. Revisão conhecida inválida não recupera versão antiga. Versão futura é excluída antes de avaliar valor/estado e não entra em contagem ou motivo.
- `pedido`: `aplicacao`, `antes`, `depois` como `{talhao, id}` e `controles` como `{talhao, antes, depois}`. São candidatos explicitamente indicados pelo adaptador, não uma lista escolhida pelo algoritmo para maximizar efeito. O núcleo revalida todos; um talhão repetido não aumenta n. As versões efetivamente usadas voltam na proveniência com escopo completo.
- `parametros`: `id`, `versao`, `publicadoEm`, `origem: 'demonstrativo'`, `protocolo`, `unidade`, `nc`, `antesMaxDias`, `depoisMinDias`, `depoisMaxDias`, `toleranciaDias`, `residualDias`, `pisoAntes`, `diferencaRelativaAntes`, `minControles`. Tudo explícito; sem defaults agronômicos. Os valores do teste são sintéticos. O campo opcional `agregacao: 'mediana_razoes_talhao_v1'` habilita explicitamente o agregado demonstrativo; ausente mantém a pendência e valor desconhecido invalida o contrato. Este primeiro núcleo recusa origem RT: habilitar parâmetros adotados exige o adaptador de protocolo versionado e a validação pertinente.

Comparação: ordem estrita antes/aplicação/depois tanto no tratado quanto em cada controle, janela declarada, mesmo estádio e faixa relativa inicial, tolerância temporal e ausência demonstrável de outra aplicação de defensivo, inclusive para outro alvo (MAPA-MIP-PROD itens8–9, linhas182/196). Cada controle expõe razão C_depois/C_antes e contraste `1 − (T_depois/T_antes)/(C_depois/C_antes)`, sem ε, truncamento ou causalidade. T_antes e C_antes zero excluem; C_depois zero exclui conservadoramente, pois a razão por controle deve ser positiva; T_depois zero permanece observado. Quantidade abaixo do mínimo não cria resultado. Sem método declarado, mesmo com controles suficientes, devolve `variacao: null` e `agregacao_pendente`. Com `mediana_razoes_talhao_v1`, calcula F = mediana das razões individuais e E = 1 − (T_depois/T_antes)/F. Para n par, a mediana é a média dos dois fatores centrais e `medianaInterpolada` sempre informa isso. O rótulo é “Contraste frente ao fator mediano dos controles”. Retorna fatores, quantidade, fontes e mínimo/máximo dos contrastes individuais; essa faixa não é intervalo de confiança. Mediana de razões, razão de médias e mediana dos contrastes não são intercambiáveis. Zero observado depois mantém o marcador próprio e não prova erradicação. Valores negativos não são truncados. O método é uma proposta executável para demonstração, pendente de revisão Claude, não adoção agronômica real.

Seguimento é população P-SEG separada: não exige antes nem controle. S6 se protocolo/unidade do NC incompatível; S4 sem leitura; S5a sem leitura até nova aplicação; S2 primeiro pós já ≥NC; S1 retorno no intervalo (última leitura baixa, primeira ≥NC]; S3 abaixo até a última leitura; S5b mesma evidência encerrada por novo manejo. Nunca censura na data de corte sem visita. Leitura simultânea à nova aplicação é excluída por ordem não demonstrada; leituras conflitantes no mesmo instante deixam o seguimento indisponível.

## Verificação executada

`node tools/prototipo/v37/gen37/raiox_comparacao_test.cjs` — 45/45 casos PASS, Node24.19.0. Inclui controle futuro D10/D12, versão retroativa, existência futura, isolamento de todos os componentes do contexto, ausência/parcial/zero, interferência, campanha, não fallback, S1–S6, conflito de instantes e permutações/imutabilidade. Sete casos adicionais verificam a agregação par/ímpar, contraste entre métodos, controles divergentes, insuficiência/zero/duplicação, resultado negativo, invariância à ordem e escala comum e método ausente/desconhecido.

Contraprova executada: remover o filtro `disp > corte` reprovou a invariância de versões futuras (exit 1). O fonte original permaneceu intacto. Não é teste de UI, integração MIP, fonte real ou validação RT. Nenhum teste navegador é alegado para esta parte sem tela.

## Continuação na mesma entrega

1. Claude critica contrato e núcleo, especialmente seleção de candidatos, agregação e tratamento conservador da ordem. Corrigir o que for material antes da integração pelo revisor.
2. Delimitar adaptador F1b em agronomia/MIP depois da entrega ativa MAPA-FROTA, com versão e campos reais demonstrativos; não fabricar datas, observações ou estados ausentes na fonte.
3. Ligar lista → comparação → fontes, filtros/foco e retorno preservados; verificar teclado/celular e contraprovas do fluxo. Então registrar implementado no protótipo, separado de publicação e software real.

Aplicado: núcleo único, estados explícitos, proveniência e exclusões temporais. Fora: tela, controle automático, agregação entre aplicações, causalidade, recomendações, risco, backend real e aprovação RT. Cortado: fallback de controles, ε silencioso, ausência como zero e censura sem leitura, pois criariam evidência inexistente.


## Correção devolvida A1/A2 — 19/10

Achados automáticos4313384219/4313384228 no HEAD64658a9, reproduzidos antes da alteração:
- A1: tratado antes emD1, aplicaçãoD2 e controle antesD3 dentro da tolerância era aceito como elegível. Agora cada controle exige antes < aplicação < depois; igualdade também exclui.
- A2: defensivo para A2 no tratado entre as leituras era descartado ao analisar A1. O resultado indevido era agregação pendente/S3. Agora o mesmo caso é interferência no tratado/S5a, e a fonte mantém o alvo real da nova aplicação. O controle também é excluído quando recebe defensivo para outro alvo no intervalo/resíduo. É cautela por possível interferência, não afirmação de eficácia cruzada.

Provas: os31casos anteriores mais7casos de fronteira/escopo/versão passaram (38/38). O fonte64658a9 com os novos testes falha(exit1). Dois mutantes independentes, restaurando só a ordem antiga ou só o filtro de alvo antigo, também falham(exit1). Sem nova bateria RX0, navegador ou dado real. Ainda dependem de revisão Claude e ligação F1b; não encerrar os achados por autoaprovação.


## Agregação demonstrativa — decisão revisável de 19/10

Histórico: a candidata64658a9 e a correção40aa1a1 mantinham toda agregação pendente. A consulta abaixo destravou apenas a proposta demonstrativa explícita. O núcleo continua recusando origem RT; não aplicar o método por default ou apresentar como validado em campo.

Gemini real Pro/HIGH, via adaptador oficial Vertex existente, foi consultado uma vez com pacote matemático sintético. Parecer concluído, sem execução de código pelo Gemini. Codex executou contraprovas com aritmética racional Python e os testes Node do núcleo.

| Exemplo sintético elegível | Contraste com mediana dos fatores | Com razão das médias | Mediana dos contrastes |
|---|---:|---:|---:|
| T10→5; C5→10 e C15→15 | 2/3 | 3/5 | 5/8 |
| T10→5; C5→10, C10→10, C15→15 | 1/2 | 4/7 | 1/2 |
| T10→2; C5→25 e C10→5 | 51/55 ≈92,73% | — | 78% |

No último exemplo, a faixa dos contrastes individuais é60%–96% e F=2,75. O exemplo original do Gemini C2→10 foi ajustado para C5→25: preserva razão5 e satisfaz a faixa inicial demonstrativa de±50% do teste. Isso não valida essa tolerância para uso agronômico.

Consolidação crítica do parecer:
- Adotados o fator mediano por talhão, identificação do método, aviso de interpolação para todo n par, faixa descritiva e zero observado. Fatores e contrastes individuais ficam recuperáveis.
- Rejeitada a equivalência entre ponderar pelo nível inicial e ponderar por área/população total. A razão das médias pondera pelos valores iniciais; inferir área ou total populacional exigiria outras hipóteses.
- Rejeitadas as afirmações gerais de independência, imunidade e robustez: independência não foi demonstrada e, com dois controles, a mediana interpolada é a média e permanece sensível a extremos.
- Não adotado o limiar arbitrário n≤4 para avisar interpolação. O núcleo expõe a informação para todos os tamanhos pares, sem inventar limiar estatístico.
- Não adotados termos causais como “explosão natural”. Há somente mudança observada. A observação sobre janela curta é cautela de interpretação, não prova biológica nem novo prazo agronômico; o núcleo conserva a janela explicitamente recebida.

A futura UI deve mostrar o método e n, permitir abrir controles/fontes, informar interpolação, identificar a faixa como descritiva e marcar zero observado na amostra. Precisão visual deve ser proporcional ao dado. Isso é critério de integração ainda não executada; nenhum teste de navegador foi alegado.

### Recibo e parecer bruto sanitizado

O bloco conserva integralmente o texto retornado e os metadados de modelo/payload. Foram omitidos identificador do projeto, modo de autenticação e caminho absoluto local da skill; nenhum segredo ou dado real entrou no pacote.

```json
{
  "at": "2026-10-19T11:49:56.293119+00:00",
  "modelRequested": "gemini-3.1-pro-preview",
  "generationConfig": {
    "candidateCount": 1,
    "maxOutputTokens": 16384,
    "thinkingConfig": {
      "thinkingLevel": "HIGH"
    }
  },
  "payloadSha256": "fe756e8ee746810222b5ef2b7db77f85fe8ef22757d98a4c29a3723cd760544a",
  "transportSha256": "3da14c38a810d346dfe2c1fa79f821f9022640459bce770c393bda9107fcd42c",
  "status": "complete",
  "finishReason": "STOP",
  "modelVersion": "gemini-3.1-pro-preview",
  "responseId": "5QPWatXHAeXIobIPz-Ch6AM",
  "usageMetadata": {
    "promptTokenCount": 3079,
    "candidatesTokenCount": 1602,
    "totalTokenCount": 7071,
    "trafficType": "ON_DEMAND",
    "promptTokensDetails": [
      {
        "modality": "TEXT",
        "tokenCount": 3079
      }
    ],
    "candidatesTokensDetails": [
      {
        "modality": "TEXT",
        "tokenCount": 1602
      }
    ],
    "thoughtsTokenCount": 2390
  },
  "text": "**Decisão: (A)** Escolher para esta demonstração o fator típico por talhão via **mediana das razões** ($F = \\text{mediana}(r_i)$), com rótulo e método explícitos. Não há razão matemática ou contratual para manter o agregado indisponível, desde que a natureza descritiva e não causal seja estritamente respeitada na interface.\n\n### Justificativa Matemática: Mediana das Razões vs. Razão das Médias\nO requisito define a pergunta exata: *\"quanto o fator de mudança do tratado ficou abaixo/acima do fator típico dos controles comparáveis?\"* e exclui o peso de área ou população total. \n\nA **razão das médias** ($\\sum C_{depois} / \\sum C_{antes}$) pondera implicitamente cada talhão pelo seu nível inicial ($C_{antes}$). Um controle que inicia com 15 insetos tem 3 vezes mais peso na formação do fator do que um controle que inicia com 5. Isso responde à pergunta de \"dinâmica populacional total na soma das áreas\", violando a exclusão de peso de área.\n\nA **mediana das razões** ($r_i$) isola o comportamento intrínseco de cada talhão como uma unidade independente, imune a distorções causadas por um único controle com infestação inicial desproporcional. Ela reflete o \"fator típico\" solicitado de forma estatisticamente robusta contra *outliers* observacionais.\n\n### 3 Contrapontos Materiais à Proposta do Codex\n\n1.  **Não-linearidade e Ambiguidade de Agregação (O problema do $n$ par):** \n    Como o seu Exemplo 1 provou por álgebra, $1 - rT/\\text{mediana}(r_i) \\neq \\text{mediana}(E_i)$. A inversão matemática na fórmula do contraste ($1 - 1/x$) significa que a mediana interpolada dos fatores não gera o mesmo resultado que a mediana dos contrastes quando $n$ é par. O Codex propõe $E = 1 - rT/F$. Isso é defensável, mas a interface deve deixar cristalino que o agregado é \"o contraste frente ao fator mediano\", e não a \"mediana dos contrastes\", sob pena de auditoria matemática falhar por falha de rotulagem.\n2.  **Sensibilidade da Interpolação a Comportamentos Divergentes:**\n    Em um cenário de $n$ pequeno e par (ex: $n=2$), onde um controle explode (fator alto) e o outro sofre queda natural (fator baixo), a média aritmética dos dois centrais (regra da mediana par) cria um fator de controle sintético ($F$) que não existiu na realidade de nenhum talhão, podendo inflar ou deflacionar drasticamente o contraste agregado de forma contra-intuitiva.\n3.  **Ilusão de Precisão com Interrupção Prematura:**\n    Se as datas de evento não considerarem o ciclo de vida completo (janela curta), a mediana das razões capturará apenas ruído estocástico inicial, não a dinâmica populacional real. Embora a ausência causal não vete a exibição, mostrar agregados com precisão decimal em janelas exíguas passa uma falsa percepção de consolidação do fenômeno.\n\n### Novo Contraexemplo (Distorção em $n$ par por comportamentos extremos)\nDemonstração do contraponto 2:\n*   $T$: $10 \\rightarrow 2$ ($rT = 0,2$)\n*   $C_1$: $2 \\rightarrow 10$ ($r_1 = 5,0$ - explosão natural)\n*   $C_2$: $10 \\rightarrow 5$ ($r_2 = 0,5$ - queda natural)\n\n**Álgebra:**\n*   Fatores: $0,5$ e $5,0$. Mediana $F = (5,0 + 0,5)/2 = 2,75$.\n*   Contraste Agregado via Codex ($E$): $1 - (0,2 / 2,75) = 1 - 0,0727 = \\textbf{92,73\\%}$.\n*   Contrastes individuais ($E_i$): $E_1 = 1 - (0,2/5) = 96\\%$; $E_2 = 1 - (0,2/0,5) = 60\\%$.\n*   Mediana dos $E_i$: $(96\\% + 60\\%)/2 = \\textbf{78\\%}$.\n\n*Crítica material:* Ao interpolar um fator sintético ($F=2,75$), o modelo relata um contraste de 92,7% que se descola fortemente do contraste real contra a área que sofreu queda natural ($60\\%$). Este é o limite matemático do método com $n$ baixo.\n\n### Diretrizes de Apresentação (Intervalo e Zero)\n\n*   **Intervalo Mín-Máx:** Deve ser estritamente rotulado como *\"Faixa observada (Mín - Máx dos contrastes individuais)\"*. Não usar colchetes tradicionais de estatística inferencial (ex: `[40% - 80%]`), pois induzem leitura de intervalo de confiança. A exibição sugerida é listar os extremos textualmente ao lado ou abaixo, demonstrando a variabilidade sem prometer distribuição paramétrica.\n*   **Tratamento de 100% (Zero Observado):** Se $T_{depois} = 0$, $rT = 0$, logo a fórmula resulta puramente em $E = 100\\%$, independentemente dos controles (assumindo $F > 0$). Para evitar a leitura de \"eficácia comprovada/erradicação\", a interface deve exibir um marcador fixo: **\"100% (Leitura zero na amostra)\"**. Isso atesta o fato observacional sem prometer suficiência causal para a lavoura.\n\n### Aceite Mínimo (Checklist de Integração)\nPara o PR avançar sob a Opção A, o código e a UI devem implementar:\n1.  **Cálculo Estrito:** A implementação de $F$ é estritamente a mediana matemática do array de $r_i$. O agregado $E$ calcula $1 - (rT / F)$, e não a mediana dos $E_i$.\n2.  **Disclaimer Dinâmico:** Se $n$ é par e $\\le 4$, o tooltip ou rótulo do agregado deve advertir que o \"Fator típico (Mediana)\" foi interpolado entre áreas com comportamentos possivelmente díspares.\n3.  **Tratamento de Controles Nulos:** Se $n$ ficar abaixo do mínimo demonstrativo acordado por exclusão de controles estruturalmente inválidos ($C_{antes}=0$ ou $C_{depois}=0$), a função retorna `null` para o agregado, não zero ou exceção engolida.\n4.  **Terminologia Segura:** Remoção absoluta de termos como \"Eficácia\", \"Controle %\", ou \"Intervalo de Confiança\". Uso exclusivo de \"Contraste Observado\" e \"Fator de Mudança\"."
}
```

### Correção A3 — revisão Claude 5572126839

A janela residual anterior à leitura inicial também se aplica ao tratado. Um defensivo de outro alvo nesse intervalo torna o contraste indisponível. Contraprova no HEAD1889755: teste novo falha; após a correção, 46/46 PASS em Node24.19.0, incluindo evento fora da janela que permanece elegível. Sem mudança de interface ou validação agronômica real.
