# V65 · composição, bateria completa e o que entra

Autor e integrador: Claude. Revisor: Codex (regime leve do protótipo, AGENTS §3.5 e §3.6; a revisão não bloqueia a publicação). Dados sintéticos.

**Base:** v64 publicada (`48f570b`, artefato versão 67). A bateria completa rodou uma vez na composição v63 (`35d00fa`), de que a v64 só difere pelos dois achados do Codex abaixo; as mudanças da v65 levam testes de impacto (AGENTS §3.6).

## O que entra
| Item | Origem | Testes de impacto (executados) |
|---|---|---|
| Achados do Codex de 14/10: cadastro só confirma salvo depois de gravar (CD08-GRAVA-01, S2); ⓘ abre com toque curto no celular (UX-C24-REGRAS-01, S3) | `48f570b` (já publicado na v64) | `cad_gravacao_falha` 6/6 (contraprova 1/6), `regras_toque` 5/5 (contraprova 3/5) |
| Mapa: camada **Colheita** (pedido do proprietário, 14/10: "o mapa é um modo de visão geográfico de tudo o que acontece na fazenda") | `0346e66` | `colheita_mapa` 7/7 (oráculo: as linhas da grade da Colheita; contraprova 1/7), `map_trilha_icones` 9/9 com as 11 camadas |
| Faixa de filtros só com o funil e a dica "Filtros" (pedido de 14/10: "teste o símbolo de filtro junto ou sozinho") | `0346e66` | `tabelas_os` (rótulo "Filtros" pelo `aria-label`) |
| Fonte única da situação da colheita (`prTal`, `prPrevTxt`, `prJanAnual`, `PR_SITORD`, `PR_SITCOR` em `producao.js`), usada pela Colheita e pela camada do Mapa (ENG-011) | `0346e66` | `producao_fluxo` 92/92, `producao_unit` 160/160 |
| PAINEL-01 (Codex, PR #61): painel de Agrícola, Manutenção e Suprimentos, primeiro item de cada módulo | `1e9fcef`, `47a8274` | `painel_modulos` 61/61 (com a cópia descrita em PN-UI-FOCO), `nav_modulos` 15/15, `busca_unica` 7/7 |
| UX-BEN35-AVISO-01 (revisão do Codex, S3): o aviso não captura toque e, no pé, sobe ao topo quando ficaria sobre um botão, link ou campo (o topo cobria a navegação: refeito na v66, ver `../V66/README.md`) | `4f222e8` | `ben_fluxo sobra390 conferencia390` 15/15 sem espera; contraprova sem a correção: "esperou 4 s o aviso sair de cima de Fechar". Verificação nova AV no `ben_fluxo` |

| CD08-GRAVA-01 residual (revisão do Codex 6159509677, S2): a semente criada com a cultivar entra na mesma gravação da cultura e da cultivar; com falha, nada fica gravado | `f68faa5` | `cad_gravacao_falha` 7/7 com o G7 (falha só na gravação final); contraprova 6/7, com a semente gravada e visível no CD-06. Vizinhos: `cadc_cd02` 15/15, `cadc_cd06` 14/14, `cd08_cultura` 5/5 |
| PR #61, devolução do Codex: espera de foco tolerante (`18322fe`) e Painel de Agrícola sem o gráfico que repetia os cartões (`e2e2385`) | `4b07499` (merge) | §5 de `bateria/vermelhos.md` |
| EST-1 (PR #60, Codex): o "hoje" do Estoque é a data operacional única (26/09) | já na v63; oráculo em `f6cf9ff` | `tabelas_est` 34/34 |

**DEC-0910-36 (barra do Mapa):** decidida pelo proprietário em 14/10, ao pedir que cada funcionalidade importante de Agrícola tenha ícone e função no Mapa. A camada Colheita entra por essa decisão. Cobertura dos itens de Agrícola no Mapa (conferida no código de `areas/inicio.py`):

| Item de Agrícola | No Mapa |
|---|---|
| Planejar safra, Planos agronômicos | camada Lavoura (cultivo, plantio previsto, plano e versão aplicados; "Abrir no Planejar safra") |
| Análises de solo | camada Análises de solo |
| Ordem de Serviço | camada Ordens de serviço |
| Pragas e doenças | camada Pragas e doenças |
| Irrigação | camada Irrigação |
| Previsão e colheita, Recebimento | camada Colheita (nova; cargas a receber na balança) |
| Orçamento e previsões, Custos e fechamento | camada Custos (R$/ha realizado × orçado) |
| Painel, Consulta Agrofit, Beneficiamento, Estoque de produto | fora do Mapa: resumo, catálogo de registros e operações de galpão e armazém, sem talhão |

## Bateria
Ver `bateria/vermelhos.md` (classificação) e `bateria/_resumo.txt` (uma linha por teste).

## Gitleaks no envio da `claude/v44-v65` (14/10)
- O primeiro envio rodou o Gitleaks com a base vazia: a referência remota da v64 não existia na cópia local, a varredura cobriu 0 commits e o envio seguiu. Erro de procedimento meu.
- Varredura refeita sobre o intervalo certo (`b3917b7..4f222e8`, 6 commits): 1 achado, falso positivo. A regra `generic-api-key` marcou, em `painel_modulos_test.py` (commit `207f362` do PR #61, linha 91), o nome da chave do cenário no armazenamento do navegador. Esse nome é público, aparece em todo o protótipo e não é credencial.
- O envio anterior (`claude/v44-v64`, `35d00fa..b3917b7`, 3 commits) foi revarrido: nenhum achado.
- Correção do procedimento: os envios passam por um script que recusa base inexistente, intervalo vazio, varredura de 0 commits e qualquer achado.
