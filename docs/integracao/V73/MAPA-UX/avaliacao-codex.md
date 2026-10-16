# Mapa — avaliação independente Codex, primeira conferência de fonte

Base b9898643662715a3f7b17bf7797d44e81e5e4a3d. Pedidos originais 96191be2837b7273898b850e5d42313653f79264; cinco anexos conferidos contra SHA256SUMS, todos iguais. Parecer Claude não lido. Este documento fecha a conferência abaixo, não a avaliação integral D1–D30 nem o desenho final. Nenhuma implantação iniciada. Navegador indisponível para Codex: não há medição de tempo, leitor de tela ou celular executada aqui.

## Decisões que o pedido já permite

- Prevalece o aceite de resposta em menos de100ms sobre a sugestão de atraso300ms do anexo. Sem atraso artificial; medir processamento e pintura no dispositivo alvo, sem prometer desempenho por desenho.
- Selecionar preserva câmera; enquadrar só por comando explícito. A oportunidade12 do anexo (enquadrar selecionado) não deve produzir movimento automático contrariando NÃO FAZER5.
- Clique comum seleciona o talhão, também no Satélite. Pixel deve ter modo explícito de inspeção; Esc sai primeiro do modo ativo e depois da seleção, sem apagar rascunho de desenho.
- Lista/busca sincronizada é caminho essencial de teclado e contingência. MapLibre unificado é opção de arquitetura, não pré-requisito para restaurar acesso/contexto. Não substituir geometrias sintéticas por geometrias inventadas.
- Contraste relativo deve usar nomes relativos e limites do talhão selecionado. Índice baixo não é diagnóstico de falha. Não trocar escala ou classe do painel silenciosamente; declarar contexto quando se compara classificação absoluta com contraste relativo.
- No toque adotar48px conforme pedido principal;44px é piso mencionado no anexo, não alvo final. Hover sem ações; o detalhe contém a ação da tarefa.

## Evidência independente na fonte (caminhos relativos a tools/prototipo/v37/gen37)

| IDs | Observação confirmada por leitura | Fonte |
|---|---|---|
| D1 | Marcadores criados como div, recebem role img e nenhum foco/ativação no trecho; seleção do pivô depende do click pv-fill. Impacto no leitor de tela ainda exige execução. | areas/inicio.py:631–646 |
| D2 | Polígonos/círculos com role button/tabIndex0 dentro de svg role img. | areas/inicio.py:1411,1434 |
| D3 | mouseenter/leave do pivô só alteram cursor; nenhum cartão nesse caminho. Não medi realce/oclusão. | areas/inicio.py:632 |
| D4/D5 | SVG usa scale1–2; has_full é falso para map_lg. Perda de alcance requer navegador. | areas/inicio.py:1126,1191 |
| D7 | Histórico de satélite aponta AG-06; o código não fornece talhão nesse link. Confirmação do destino AG-06 ainda pendente nesta conferência. | areas/inicio.py:1016,1127 |
| D8 | Nova O.S. neste talhão aponta OS.dc.html sem identificação; link da faixa também não a inclui. | areas/inicio.py:1074,1127 |
| D9 | Legenda elimina números no contraste Talhão sem seleção; nomes seguem Falha/Fraco/etc. Raster usa limites relativos e cartão de pixel usa classe própria, a reconciliar. | areas/inicio.py:347,861–865,1007–1011,1148–1150 |
| D10 | CS16 é descrito como10m demonstrativos e o cartão anuncia10m. Isso não comprova resolução efetiva; não converti desenho em área geográfica. | areas/inicio.py:353,1011 |
| D11/D12 | Mancha é desenhada somente em T7; caixas de texto possuem alturas20/46 e posições fixas. Corte/sobreposição não medidos. | areas/inicio.py:1423–1429 |
| D13 | Preenchimento operacional usa0.55, nuvem0.35; legenda usa cor opaca/hachura. Diferença de codificação confirmada. | areas/inicio.py:645,854 |
| D14/D15 | Estados distintos compartilham tokens, inclusive colhido/fora do filtro e produção contínua/amarelo. Não reproduzi a simulação de daltonismo do anexo. | areas/inicio.py:430,866–869 |
| D16 | Satélite retorna ao selecionar pixel antes do toggle de talhão. | areas/inicio.py:605–608,1143–1146 |
| D17 | Persistência mapa-ctx guarda seleção/filtros/zoom SVG, sem câmera MapLibre nem serialização de seleção na URL nesse caminho. | areas/inicio.py:1111 |
| D18 | #talhao seleciona e busca anéis de Lagoa Grande, sem atualizar mf_faz. | talmapa.js:163–167 |
| D19 | Medir mostra área/perímetro cadastrado em toast; não mede geometria desenhada. | areas/inicio.py:602,1142,1168 |
| D20 | pan_close limpa seleção; mudança de painel só ajusta scrollTop interno. Não há gestão de foco nesse caminho. | areas/inicio.py:1159–1162 |
| D21 | Abas têm role/aria-selected, sem aria-controls ou handler de setas no componente. | areas/inicio.py:1634–1638 |
| D22 | Zoom36px e fechar30px explícitos. Dimensão efetiva com CSS global requer execução. | areas/inicio.py:1498,1523 |
| D24 | FL não contém Solo nem Colheita. | areas/inicio.py:1127 |
| D29 | Configuração MapLibre não declara cooperativeGestures; impacto no toque ainda pendente. | areas/inicio.py:619–621 |
| D30 | Selecionar área implementa clique para somar talhões, não laço. | areas/inicio.py:1174 |

D6, D23, D25, D26, D27, D28 e telas CD-01/CD-01det/PL-06/CA-01/AG-01det/MB ainda precisam conferência própria. Não herdar como verificados os números/linhas do HTML do anexo. Não há fechamento de nenhum D por esta leitura: confirmar defeito não equivale a corrigi-lo.

## Ordem proposta, ainda sem divisão de autoria de implementação

1. Acesso/contexto: lista/busca, semântica, seleção/retorno, destinos com talhão/fazenda; manter nove camadas e comandos de domínio existentes.
2. Honestidade visual: limites e nomes relativos, qualidade/cena/resolução e diferença entre sem dado/fora do filtro; legenda e painel coerentes.
3. Interação: cartão hover/foco, folha no celular, alvos e rótulos, legenda recolhível, pan/enquadrar explícito. Testar antes de migrar motor.
4. Uniformizar geometrias/nomes/paletas nas telas dependentes e fechar demais D; manter lista acessível quando não houver geometria.

Aplicar: contexto único e nomes objetivos. Deixar de fora desta conferência: opinião Claude, consenso Gemini e teste de usuário ainda não executados. Cortar da proposta: atraso300ms e recentralização automática, por conflito com pedido principal. Próximo passo: completar fontes/D restantes e quadro das nove camadas, depois confrontar avaliações e somente então registrar fatias finais.

## Complemento da mesma conferência

D26: dependência do CDN confirmada em areas/inicio.py:569 e fetch de lagoa_s2.json:571. Não medi2,5MB, carga/offline ou recuperação. D28: marcador com fonte15/11px e largura máxima120px em565–566; não há colisão declarada no trecho635–636, mas sobreposição real continua pendente. D6: comentário inicial declara Todas=SantaRita+aviso, e map_lg só é verdadeiro para fazenda exatamente LagoaGrande(1191); é indicação consistente, a confirmar pelo fluxo completo. Falha de busca local icons.py: arquivo não existe nesse runtime; não concluir D25 por esse erro.

## Segunda passagem — conclusão da avaliação estática independente

A conferência estática está pronta para comparação de pareceres, sem equivaler a aceite funcional. As pendências de navegador e de teste com usuários abaixo continuam bloqueadas/não executadas.

- D6 confirmado no caminho: MAPVALS converte qualquer fazenda diferente de Lagoa Grande em Santa Rita (inicio.py:1101); map_lg só liga em Lagoa Grande(1191). "Todas" precisa visão global honesta, com lista de todas e destaque das que não têm geometria; não remover a visão global necessária.
- D23: legenda ocupa div absoluto de esquerda a direita no rodapé, recebe eventos normais(inicio.py:1562). Risco de interceptação confirmado estruturalmente; área efetivamente coberta pendente. Mover/recolher legenda mantendo seus controles acessíveis é preferível a desativar pointer-events de toda a legenda interativa.
- D25 precisa precisão: Colheita EXISTE em engine.ICONS e na barra estática. Falta no ICN de ações dinâmicas(inicio.py:911–915), embora colhAc use esse nome(1398–1400). Corrigir o catálogo das ações, não criar outro ícone nem tratar toda a barra como quebrada.
- D27: cadastro imprime pid(PVxx) em cad_fazendas.py:232 e mapa usa rot em inicio.py:646. Identidade interna pode continuar PV01; rótulo visível deve ser único, com fazenda no contexto para distinguir P1 homônimo. Não renomear IDs persistidos só para corrigir texto.
- D28: estrutura de rótulo sem política de colisão confirmada; corte e sobreposição permanecem hipóteses a medir.
- CD-01: formas só têm onClick, sem foco; callbacks mc abrem g2open do formulário(cad_fazendas.py:205–216,424,449). Usar detalhe existente e conservar editar como ação dentro dele.
- CD-01det: clip-path único independentemente do talhão(cad_fazendas.py:546). Mostrar geometria cadastrada; quando faltar, estado sem geometria, sem polígono plausível inventado.
- PL-06: desenho específico de T1 com coordenadas fixas(planejamento.py:86–89). Distinguir esquema de proposta de mapa georreferenciado, preservando as regras de parcelas.
- CA-01: mapa contém literal190/350ha(campo.py:154–157). Usar estado compartilhado ou link contextual à camada O.S., não duplicar valores estáticos.
- AG-01det: pontos posicionados por índice alternado(agronomia.py:834). Não apresentá-los como localização GPS; manter lista de coleta e só projetar geometrias válidas. Rota esquemática pode permanecer identificada como tal.
- MB: não conferido integralmente neste escopo; alegação de ausência global de mapa permanece relato do anexo. Não bloquear reparos IN-04 pela criação de um mapa mobile novo.

## Proposta por camada (não implantação aprovada)

Todas usam fazenda/safra/talhão, data e origem comuns. Lista e mapa representam a mesma coleção filtrada. Seleção abre detalhe lateral/abaixo, sem modal; comando de domínio conserva permissão, prévia e recibo. Sem dado tem estado e recuperação próprios.

| Camada | Hover/foco | Detalhe e ação primária por estado | Adotar/adaptar/cortar |
|---|---|---|---|
| Integrado | motivo prioritário, data, pendências | causas ordenadas com origem; agir sobre motivo prioritário usando comando existente | adaptar "pior" para não comparar números incomparáveis; empate tem regra estável e motivo visível |
| Satélite | índice/unidade, cena, qualidade, escala | estatísticas/limites e manchas; Ver qualidade se inválido, Ver histórico se válido sem alerta, Criar vistoria se investigação pertinente | adotar contraste honesto; cortar diagnóstico Falha por cor e histórico dirigido a pragas |
| Solo | data da amostra, indicador/unidade e qualidade | laudo/pontos/limitações/recomendação existente; Ver análise ou Registrar laudo quando ausente | adaptar interpolação: identificada como estimativa, nunca amostra medida em todo pixel |
| Pragas e doenças | alvo, nível/unidade, NC e data | vistoria/tendência/manejo; Decidir controle quando decisão pendente, Vistoriar quando dado insuficiente | preservar motor MIP; risco7dias só quando modelo/dados sustentarem, sem previsão inventada |
| Ordens de serviço | fase, atraso, realizado/unidade | lista de ordens e ordem ativa; próximo comando permitido da selecionada, com recibo | preservar comandos no lugar e aprovações; cortar links sem talhão, sem liberação em lote implícita |
| Irrigação | lâmina/necessidade, origem e estimativa | balanço/turno/impedimento; Abrir turno ou tratar impedimento pertinente | preservar distinção água/fertirrigação e validação; não padronizar uma aprovação errada |
| Estádio | cultura, estádio, DAP/DAE com referência | ciclo/histórico/próximo estágio; Ver calendário contextual | adaptar fases para paleta categórica, sem parecer alerta apenas pela cor |
| Colheita e produtividade | situação, previsto/realizado e unidade | previsão/romaneios/carência; abrir a origem que resolve o estado | adaptar escala por cultura/unidade; não comparar diretamente sc/ha e t/ha nem ocultar carência |
| Custos | realizado/planejado por ha e parcialidade | composição/denominador/origens; Ver custo do talhão | adotar escala quantitativa só com bases comparáveis; não transformar ausência em zero |

## Conferência das dez heurísticas e critérios pendentes

Visibilidade: processamento/erro/data/seleção; mundo real: unidade e nomes de fazenda/talhão; controle: Esc por nível e retorno sem perda; consistência: catálogo de estado/ação único; prevenção: identidade composta e máscara de qualidade; reconhecimento: lista/busca/legenda; eficiência: teclado e retorno contextual; minimalismo: cartão só essencial, sem ação; recuperação: dados ausentes/erro de carregamento com próximo passo; ajuda: origem/metodologia junto do contexto. Essa análise de desenho não é uma medição de usabilidade.

Provas ainda necessárias: navegador1440/390 e teclado/leitor de tela para D1/2/4/12/20/21/22/23/28/29; tempo hover/seleção/carga no dispositivo-alvo; medir antes/depois com mesmos dados;3–5 usuários por perfil e sucesso>=95% são aceites futuros, não resultados. Não há autorização para fabricar entrevistas ou contagens. Fontes agro de limites/risco ficam para avaliaçãoRaio-X e decisão materialGemini; não são validadas por esta revisãoUX.

Aplicado na proposta: nove camadas, master-detail, contextos, identidade estável, uma ação por estado e dados honestos. Deixado de fora desta fatia: migração integral de motor, mapaMB novo, seleção por laço e linha do tempo global até contrato/capacidade demonstrados; todos permanecem candidatos, não requisitos descartados. Cortado: atraso artificial, câmera automática, ação no hover, clone de regrasO.S., forma fictícia apresentada como real. Nenhuma edição de código nesta avaliação. Próximo passo: trocar avaliações concluídas, resolver divergências por fonte/prova, consultar Gemini na escolha material de interação e registrar autoria/base/arquivos/aceite antes de implementar.
