PROJETO: Safrion (Do Talhão à O.S.) · EX-54 · Frentes de trabalho (agrupamento de O.S. e talhões para execução e logística)

PEDIDO DO PROPRIETÁRIO (18/10/2026)
"Na parte de ordem de serviço agrícola, o agrupamento de OS e talhões semelhantes para facilitar execução e logística contínua na fazenda está muito ruim. Pegue as melhores práticas e referências do mundo nisso e crie algo mais inteligente, intuitivo, prático."

COMO TRABALHAR (protocolo da equipe, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint da issue #1 e o protocolo canônico. Este prompt não substitui o PRD nem as decisões NAV/DS.
2. Antes de qualquer código, Claude e Codex melhoram este desenho de forma independente: cada um reproduz o agrupamento atual, confere as regras e a heurística abaixo e decide Adotar, Adaptar ou Rejeitar cada parte. Divergência se resolve por fonte ou reprodução; o Codex registra no checkpoint (só ele edita o checkpoint).
3. Gemini real para as decisões de domínio materiais: calda que continua de um talhão para o outro com rateio (rastreabilidade de agrotóxico), ordem e lavagem depois de herbicida, limites de clima para pulverizar. Pacote mínimo, sem dados reais. Não simule nenhum modelo.
4. Só depois implante, por fatias, com revisão cruzada: quem revisa integra o PR do outro.

ESPECIFICAÇÃO VIVA (referência de ideias, não código a copiar)
https://claude.ai/artifact/4cRucvLyPCnwbmnoUpMuyV (artefato "Frentes de trabalho do Safrion"; privado, aberto pelo proprietário) e o arquivo frentes-trabalho-safrion.html, a mesma página para abrir no navegador sem o link. A demonstração usa a geometria real dos 23 pivôs da Lagoa Grande do protótipo; as O.S. 0601 a 0611, os conjuntos de pulverização, os rendimentos e a previsão do tempo são exemplos.

O QUE ACONTECE HOJE (versão publicada 1792342402-4b90, Ordem de Serviço › "Agrupar operações compatíveis", reproduzido)
- Só junta calda idêntica (mesmo produto e mesma dose). A OS-0598 (sulfato de magnésio 3 kg/ha) fica fora do grupo de 2 kg/ha com "Sem outra O.S. compatível neste contexto".
- Só pulverização e só O.S. "A liberar" ("Somente A liberar, antes de compromissos"). Plantio, calagem e adubação a lanço não agrupam; OS-0421 e OS-0424 (Fungicida A, talhões vizinhos) e os plantios OS-0420 e OS-0431 (mesma soja 58 W e MAP 250 kg/ha) nunca se encontram.
- Sem mapa, rota, capacidade nem clima: "Sequência por prazo da origem" e "horas não calculadas".
- "Cada talhão usa seu conjunto e suas cargas, sem transferir restos entre O.S.": 30 ha com a mesma calda viram 3 cargas separadas.
- Mensagem errada: a OS-0431 é plantio e aparece "Sem conjunto · alocar pulverizador na O.S.".
- Dados de exemplo sem lugar no mapa ("Talhão demonstrativo A a E").
- Já certo e mantido: o grupo (GRP-) não aprova, não libera nem reserva; "aprovação e liberação continuam por O.S."; origens preservadas.

O QUE FAZER: FRENTES DE TRABALHO
Uma frente é um conjunto (trator, implemento e operador) percorrendo uma sequência de talhões com a mesma família de operação, num período. Substitui o diálogo "Agrupar operações compatíveis".
1. Candidatas: O.S. não encerradas no horizonte (padrão 14 dias, configurável) da Fazenda e Safra do escopo (EX-51 R5), em qualquer estado antes de "Em conferência", inclusive o saldo das que estão em execução. A frente só executa as liberadas; as outras aparecem com quem decide.
2. Família pelo implemento exigido: pulverização (pulverizador, turbo ou barra), adubação e calagem a lanço (distribuidor), plantio (plantadeira), colheita (colhedora), tratos manuais (equipe). Troca de implemento é parada; a frente não mistura famílias.
3. Compatibilidade dentro da família:
   - Pulverização: calda idêntica (mesmos produtos, doses e volume de calda) continua no tanque de um talhão para o outro; mesmo produto com outra dose entra na mesma frente como nova calda; produtos diferentes compatíveis entram com troca de calda; herbicida ou hormonal só por último, seguido de tríplice lavagem registrada, ou num pulverizador dedicado; nunca antes de cultura sensível.
   - Plantio: mesma cultivar, tratamento de semente e adubo de base; troca de cultivar exige limpeza da plantadeira registrada (pureza).
   - A lanço: mesmo produto; dose diferente é nova regulagem.
4. Ordem: janela que fecha antes entre as que já estão abertas e, empatando, o talhão mais perto (a partir da sede, da pilha ou do último talhão), preferindo a mesma calda; herbicida no fim. "Otimizar ordem" refaz; a pessoa reordena com setas ou arrastando, e a frente recusa a ordem que põe herbicida antes de cultura sensível sem lavagem.
5. Capacidade e tempo: rendimento do conjunto (ha/h do CD-08), cargas e reabastecimentos (tanque, caixa, distribuidor), deslocamento entre talhões (distância por estrada ou, sem malha viária, linha reta × fator configurável) e horas de trabalho. Pulverização só nas horas aptas da previsão: Delta T, vento e chuva com limites configuráveis por produto e por bula (referência: Delta T de 2 a 8; vento de 3 a 20 km/h com gotas grossas e de 5 a 15 km/h com gotas finas, GRDC). Calagem e plantio respeitam chuva e solo.
6. Não cabe na janela? Divide com outro conjunto livre da mesma família, tirando do fim da sequência; sem conjunto livre, marca em vermelho a O.S. que termina depois da janela e oferece "Reprogramar" ou "Pedir conjunto" (pendência para o PCP, EX-51).
7. Cargas contínuas: na mesma calda, a carga que sobra de um talhão segue para o próximo, com o volume rateado por O.S. e por carga (rastro: "carga 7: 4,2 ha no P6 + 5,8 ha no P4"). Antes de trocar de calda, a última carga sai do tamanho exato, sem sobra. Quem decide se o rateio vale para agrotóxico é o RT; até essa decisão, a frente funciona com carga fechada por O.S. e mostra o ganho que o rateio traria.
8. Porquê e ganho: cada frente mostra por que juntou (mesma calda, janelas que se cruzam, vizinhos) e o ganho contra fazer cada O.S. sozinha (horas, km e cargas), além dos alertas (aprovação pendente com quem decide, herbicida no fim, fora da janela).
9. Programar frente: grava início e fim previstos em cada O.S., o conjunto, uma requisição de insumos para a frente com o rateio por O.S. (o servidor reserva por O.S.) e o roteiro no app. Não aprova, não libera e não reserva por conta própria (decisão fixa: aprovação agronômica individual).
10. Roteiro no app do operador: talhão de agora e o próximo (distância, o que continua da carga), cargas e calda, apontamento que começa ao entrar no talhão pelo GPS e fica na O.S. dele (D1 e D2 do EX-53), funcionando sem sinal.
11. Replanejar por evento (EX-51): chuva, máquina parada, O.S. nova compatível ("cabe na frente F2") e insumo atrasado recalculam a frente e avisam só quem precisa agir.

ONDE FICA (sem item novo na barra)
- Ordem de Serviço: visão "Frentes", ao lado de Tabela, Cartões, Kanban, Calendário e Carga por recurso, com lista de frentes à esquerda, mapa com rota numerada e, abaixo, sequência, linha do tempo com as horas aptas, insumos e roteiro. A visão Carga por recurso mostra as frentes como barras por conjunto.
- Mapa e visão Mapa das telas agrícolas (EX-55): a camada Ordens de serviço ganha "Mostrar frentes".
- App de campo: "Roteiro de hoje".

ESTADOS DA FRENTE E AÇÃO PRIMÁRIA
Sugerida → Programar frente · Programada → Iniciar (no app) · Em execução → Apontar (no app) · Concluída (todas as O.S. em conferência ou encerradas) → Ver resultado · Impedida (conjunto parado, clima, insumo) → Resolver (abre o impedimento). Cada estado em texto e cor (EX-49).

FATIAS (ordem sugerida; Claude e Codex podem reordenar com motivo)
F1 Família por implemento, compatibilidade de calda e ordem por janela e distância, na visão Frentes, sem cargas contínuas; corrigir a mensagem do plantio ("alocar pulverizador").
F2 Capacidade, cargas, deslocamento e divisão entre conjuntos; linha do tempo; programar frente com requisição única.
F3 Horas aptas pela previsão (integração da estação e da previsão) e replanejamento por evento.
F4 Roteiro no app com apontamento por talhão (depende do D1 e D2 do EX-53).
F5 Cargas contínuas com rateio, depois da decisão do RT.

ACEITE
- Na Lagoa Grande do cenário, as O.S. de acaricida, fungicida e calagem da semana viram frentes com rota numerada no mapa, porquês, ganho em horas, km e cargas, e nenhuma O.S. fora da janela sem alerta e saída.
- OS-0420 e OS-0431 (plantio, mesma cultivar e adubo) aparecem na mesma frente quando o conjunto existe; OS-0421 e OS-0424 (Fungicida A) também, com a diferença de adjuvante mostrada como troca de calda.
- Herbicida entra sempre por último, com tríplice lavagem registrada; a frente recusa outra ordem sem lavagem.
- Programar frente não muda o estado de aprovação de nenhuma O.S.; a O.S. pendente segue na fila de Aprovações e a frente começa pelas liberadas.
- Números da frente iguais aos da O.S., do Estoque e do Painel (EX-51 R8); funciona com teclado (setas para ordem, Enter no pivô) e no celular.

NÃO FAZER
- Aprovar, liberar ou reservar em lote pela frente.
- Misturar famílias de implemento ou esconder a troca de calda.
- Calcular reserva na tela; o servidor reserva por O.S.
- Fixar limites de clima, rendimento ou volume de calda no código: são parâmetros com fonte.
- Criar item novo na barra principal.

REFERÊNCIAS
- John Deere Work Planner: plano para vários talhões escolhidos no mapa, com detalhes por talhão enviados ao monitor. https://www.rdoequipment.com/resources/blogs/john-deere-work-planner-overview
- Solinftec: programação diária e rotas a partir das ordens, da previsão e dos dados das máquinas; o fabricante relata máquinas 30 % do tempo paradas e 35 % se deslocando. https://www.solinftec.com/en-us/machine-utilization/ · https://www.croplife.com/?p=86314
- Roteamento em logística de campo (linha de Bochtis e Sørensen): ordem dos talhões como problema de roteamento com janelas de tempo. https://www.igi-global.com/chapter/the-agricultural-routing-planning-in-field-logistics/196931 · https://arxiv.org/pdf/1703.08999
- GRDC (deriva e inversão) e Delta T de 2 a 8. https://groundcover.grdc.com.au/weeds-pests-diseases/weeds/spray-safely-to-reduce-drift-risk-this-summer · https://dpir.nt.gov.au/primary-industry/primary-industry-publications/regional-newsletters/tp/top-paddock-122017/limiting-spray-drift-and-improving-coverage
- Limpeza do pulverizador depois de auxínicos (UF/IFAS, UT). https://edis.ifas.ufl.edu/publication/PI291 · https://utia.tennessee.edu/publications/wp-content/uploads/sites/269/2023/10/W071.pdf

ENTREGA (no canal registrado)
- Reprodução do agrupamento atual e validação de cada regra (Confirmada com arquivo e trecho, Refutada, Já resolvida), por Claude e por Codex, e a decisão final.
- Desenho no motor: visão Frentes, cálculo, dados novos (conjunto, capacidade, horas aptas), eventos e app.
- Decisão do RT sobre cargas contínuas e lavagem, e do proprietário só se mudar escopo.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
