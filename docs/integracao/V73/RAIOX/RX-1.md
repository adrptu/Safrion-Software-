# RX-1 — núcleo de comparação e seguimento

19/10/2026 · Codex autor · Claude revisor/integrador · base `d022c74524a7bcb349c05dd25cc13c2ec9cb472d`.
Partilha: PR47/6266132270; confirmação e localização da F1b: 6266180436. A F1b está especificada, sem código integrado. Não tratar AG06 com linhas fixas como comparação funcional.

## Entrega e limite

Primeira parte executável do RX-1: função pura `RaioxComparacao.analisar(dados, contexto, parametros, pedido)`. Arquivos novos `raiox_comparacao.js`, `raiox_comparacao_test.cjs` e este documento. Não altera fonte MIP, agronomia, mapas, persistência, fórmulas do RX-0 nem fontes reais. Não habilita nova tela. O RX-1 completo depende do adaptador F1b e da revisão do método de agregação; não dispara auditoria integral.

Fonte de regras: `docs/integracao/V73/RAIOX-ALVO/rx0-contrato-proposta.md`, EST-3a/3b e Δ17/10-2; EX42/V71 §11 e casos T7/T8 em MAPA-MIP-PROD. Referência histórica do confronto, sem repetir o gerador ou transformar seu diagnóstico em validação causal. A F1b futura substitui as linhas fixas EF017–EF021 em `areas/agronomia.py`; `mipPos` agenda a leitura pós e não calcula comparação. Esses dois arquivos permanecem fora desta autoria.

| Entidade/nível | Estado devolvido | Próxima ação do consumidor |
|---|---|---|
| Aplicação / detalhe → comparação | Sem fonte/ordem válida | Abrir a fonte e corrigir o dado indicado |
| Comparação / subdetalhe | Controles insuficientes | Mostrar candidatos, exclusões e leituras; não relaxar filtros |
| Comparação / subdetalhe | Agregação pendente | Exibir razões por controle como diagnóstico; não publicar percentual agregado |
| Seguimento / subdetalhe | S1–S6/S5a/S5b | Mostrar leituras, intervalo ou última leitura e motivo; preservar contexto |

## Contrato da função

- `contexto`: `org`, `fazenda`, `cultivo`, `safra`, `alvo`, `corte` explícitos. Não é autorização de acesso: o futuro adaptador deve obter somente fontes permitidas ao usuário.
- `dados`: listas completas de versões de `leituras` e `aplicacoes` no universo autorizado. Uma fonte contém os cinco campos de contexto, `talhao`, `id`, `versao` inteira positiva, `evento`, `disponivelEm`, `precisao: 'instante'`, `estado`. Instantes UTC canônicos `YYYY-MM-DDTHH:mm:ss.sssZ`; o adaptador fará a conversão do fuso da fazenda. Dias sem ordem não podem ser promovidos a meio-dia fictício.
- Leitura: `valor` numérico finito não negativo, `unidade`, `protocolo` identificando a versão, `estadio`, `avaliador` pseudônimo. Só `estado: 'completa'` forma par. Ausência não vira zero. Aplicação: só `estado: 'confirmada'` inicia episódio; cancelamento substitui versão anterior. Manejo conhecido parcial/pendente não comprova ausência de interferência.
- Seleciona maior disponibilidade até o corte por chave completa. Duplicidade de versão/disponibilidade é inválida, independentemente da ordem. Revisão conhecida inválida não recupera versão antiga. Versão futura é excluída antes de avaliar valor/estado e não entra em contagem ou motivo.
- `pedido`: `aplicacao`, `antes`, `depois` como `{talhao, id}` e `controles` como `{talhao, antes, depois}`. São candidatos explicitamente indicados pelo adaptador, não uma lista escolhida pelo algoritmo para maximizar efeito. O núcleo revalida todos; um talhão repetido não aumenta n. As versões efetivamente usadas voltam na proveniência com escopo completo.
- `parametros`: `id`, `versao`, `publicadoEm`, `origem: 'demonstrativo'`, `protocolo`, `unidade`, `nc`, `antesMaxDias`, `depoisMinDias`, `depoisMaxDias`, `toleranciaDias`, `residualDias`, `pisoAntes`, `diferencaRelativaAntes`, `minControles`. Tudo explícito; sem defaults agronômicos. Os valores do teste são sintéticos. Este primeiro núcleo recusa origem RT: habilitar parâmetros adotados exige o adaptador de protocolo versionado e a validação pertinente.

Comparação: ordem estrita antes/aplicação/depois, janela declarada, mesmo estádio e faixa relativa inicial, tolerância temporal e ausência demonstrável de outra intervenção. Cada controle expõe razão C_depois/C_antes e contraste `1 − (T_depois/T_antes)/(C_depois/C_antes)`, sem ε, truncamento ou causalidade. T_antes e C_antes zero excluem; C_depois zero exclui conservadoramente enquanto a agregação não foi decidida; T_depois zero permanece observado. Quantidade abaixo do mínimo não cria resultado. Mesmo com controles suficientes, `variacao: null` e `agregacao_pendente`: mediana de razões e razão de médias não são intercambiáveis. Decisão metodológica continua pendente, sem consulta ritual ao Gemini.

Seguimento é população P-SEG separada: não exige antes nem controle. S6 se protocolo/unidade do NC incompatível; S4 sem leitura; S5a sem leitura até nova aplicação; S2 primeiro pós já ≥NC; S1 retorno no intervalo (última leitura baixa, primeira ≥NC]; S3 abaixo até a última leitura; S5b mesma evidência encerrada por novo manejo. Nunca censura na data de corte sem visita. Leitura simultânea à nova aplicação é excluída por ordem não demonstrada; leituras conflitantes no mesmo instante deixam o seguimento indisponível.

## Verificação executada

`node tools/prototipo/v37/gen37/raiox_comparacao_test.cjs` — 31/31 casos PASS, Node24.19.0. Inclui controle futuro D10/D12, versão retroativa, existência futura, isolamento de todos os componentes do contexto, ausência/parcial/zero, interferência, campanha, não fallback, S1–S6, conflito de instantes e permutações/imutabilidade.

Contraprova executada: remover o filtro `disp > corte` reprovou a invariância de versões futuras (exit 1). O fonte original permaneceu intacto. Não é teste de UI, integração MIP, fonte real ou validação RT. Nenhum teste navegador é alegado para esta parte sem tela.

## Continuação na mesma entrega

1. Claude critica contrato e núcleo, especialmente seleção de candidatos, agregação e tratamento conservador da ordem. Corrigir o que for material antes da integração pelo revisor.
2. Delimitar adaptador F1b em agronomia/MIP depois da entrega ativa MAPA-FROTA, com versão e campos reais demonstrativos; não fabricar datas, observações ou estados ausentes na fonte.
3. Ligar lista → comparação → fontes, filtros/foco e retorno preservados; verificar teclado/celular e contraprovas do fluxo. Então registrar implementado no protótipo, separado de publicação e software real.

Aplicado: núcleo único, estados explícitos, proveniência e exclusões temporais. Fora: tela, controle automático, agregação, causalidade, recomendações, risco, backend real e aprovação RT. Cortado: fallback de controles, ε silencioso, ausência como zero e censura sem leitura, pois criariam evidência inexistente.
