# PAINEL-01 — painéis dos módulos

Codex autor; Claude revisor/integrador. Contrato6157925031, liberação6158695076 e ACK6158745262. Base de autoria f6b31f755f04e4925d896e6d9a085e523ea79aef; integração na composição vigente de Claude.

Três telas de leitura: PAGR (Agrícola), PMAN (Manutenção), PSUP (Suprimentos). Quatro indicadores por tela, um gráfico de contagens com valores textuais e até quatro acessos às telas existentes. A ação principal usa o cabeçalho do shell e permanece alcançável ao rolar. Fórmulas/fontes no componente de dica existente, com teclado e toque. Comercial reutiliza PCOM como primeiro cartão. Não há comandos de domínio nestes painéis.

Escopo explícito: todas as fazendas e safras do cenário atual. Indicadores contam registros; não somam kg, L, ha ou moedas. Vazio válido é zero; fonte ausente/incompleta mostra Sem dados e acesso à origem. Agrícola exclui ordens BEN. Manutenção usa manSemOm/manAberta. Requisições usam cenSaldoEntregar do motor vigente (sem copiar a fórmula, que difere entre f6 e a composição35d). O gráfico do Estoque particiona os lotes físicos sem dupla contagem: com quarentena; reservados sem quarentena; sem ambos. Os indicadores de reserva/quarentena podem se sobrepor, como explicado na dica.

## Integração pelo revisor

Arquivos de autoria: work/prototipo-fase1/gen37/areas/paineis.py e painel_modulos_test.py. Nenhum arquivo de Claude foi alterado no commit. Os patches nesta pasta foram aplicados apenas à cópia isolada de QA:

1. `git apply docs/painel01/painel01-ui37.patch`: acrescenta os três cartões Painel, reutiliza os hubs, coloca PCOM primeiro. Reconciliar com MENU2/CURTO37 atuais, preservando BEN e demais deltas de Claude.
2. `git apply docs/painel01/painel01-nav-test.patch`: atualiza somente a expectativa explícita de Manutenção de quatro para cinco cartões. Não elimina as verificações de nomes, ordem, destino ou foco.
3. Build e render; executar painel_modulos_test.py (Node) e --ui (Chrome). Rodar checks da integração afetada.

Não mesclar/publicar sem aplicar os patches e conferir a composição. Este PR não conclui o conjunto do protótipo, HML nem PRD.

## Evidências de autoria

- build147 artboards; render156 páginas sintéticas.
- Oráculos16/16: contagens controladas, BEN/canceladas/encerradas excluídas, serviços devidos/fora da janela/plano inativo, partição de lotes, requisições por registro, zero/ausente/inválido e leitura sem mutação.
- UI61/61: desktop1440 e celular390, cartão primeiro, quatro indicadores, dicas com teclado/Enter/Escape/toque e alvo44px, ação primária alcançável com scroll, destinos e volta com foco; fonte ausente, vazio e atualização pelo cenário sem recarga.
- links_ocultos16/16.
- nav_modulos original14/15: única divergência era a expectativa antiga de quatro cartões da Manutenção. Patch de expectativa aplicado na cópia de QA; reexecução15/15.
- busca_unica6/6 em156páginas; paginas_scan4/4 em147páginas não técnicas ×2larguras, incluindo contraprova da captura de erro. Sem JS/overflow/submenu. A inspeção final focal dos três painéis61/61 cobre a mudança posterior da primária para o cabeçalho, sem repetir páginas intactas.
- Inspeção visual desktop/celular executada; corrigido acesso principal antes abaixo da dobra. Sem teste em aparelho físico/Safari, nem prova de software real.

Uma fixture inicial supunha que f6 já subtraía dispensado em cenSaldoEntregar, como35d. O oráculo da base passou a usar custódia integral para o item coberto; não se alterou o motor nem se ocultou divergência de comportamento. A dica descreve a contagem e referencia a regra vigente. Brutos iniciais preservados localmente.

Aplicado: Menu→painel de visão geral→listagem/detalhe existentes, contexto global nomeado, foco preservado, fontes e estado visíveis, uma primária. Fora: indicadores financeiros/agronômicos novos, filtragem por fazenda/safra e gráficos de tendência sem série validada. Cortado: subtítulos longos, biblioteca de gráficos, novo menu/cadastro e cálculos paralelos. Reutilizado benchmark vigente outputs/diretriz-benchmark-e-produtividade.md: contexto e origem compartilhados, sem nova pesquisa para o mesmo módulo.
