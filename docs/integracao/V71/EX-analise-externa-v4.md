# Análise externa, 4ª versão (16/10/2026): delta sobre a 3ª (EX-40, indicadores do EX-26 e Anexo A)

O proprietário colou a 4ª versão em 16/10/2026, no canal do Claude, como arquivo (`prompt-safrion-excelencia.md`, SHA-256 `7d89604174c35f6a4e947de35fb471b35663f53a22e545abf68123b25e7677d2`).
- **Mantém da 3ª versão** (`EX-analise-externa-v3.md`, que mantém a 2ª): EX-01 a EX-39, método, critério de entrada, "não fazer", decisões do proprietário e entrega. A tabela final passa a ir até EX-40, e o Codex recebe a lista até EX-40.
- **Abaixo, só o que é novo,** no texto do proprietário: EX-40 (Onda B, ajustes menores), a versão ampliada do EX-26 e o Anexo A com os princípios P01–P66, que antes eram citados como "lista enviada".
- **Como entra:** é insumo, não requisito; PRD, NAV/DS, protocolo e decisões registradas prevalecem. O Anexo A é régua para os EX, não requisito por si. A classificação do Claude vem em arquivo próprio, separado, depois deste registro.

## Onda B · item novo

EX-40 Ajustes menores (baixo esforço):
  - páginas de módulo (MOD-*) com a contagem de pendências por item, ou abrir direto na tela de trabalho; hoje são 3 a 5 links sem estado, um clique a mais;
  - PL-05 "Notificar responsáveis" passa a ser automático;
  - AG-05 "Validar" e "Publicar" num passo só, mantendo a aprovação do RT;
  - AG-06 "Propor melhoria" e "Propor revisão" viram uma ação só;
  - o bloco "Manutenções e impacto na produção", repetido em PL-03 e PL-04, aparece uma vez;
  - a tabela "Água no solo" do AG-02 vai para Irrigação;
  - PCOM: "Colunas" e "Tabela/Cartões" aparecem duas vezes;
  - CD-04: três formas de filtrar (lista "Função", chips e "Agrupar") viram uma;
  - ações destrutivas vão para o ⋯: "Encerrar saldo", "Cancelar reserva", "Cancelar sem execução";
  - MB-06 "Concluir com 9 de 14" pede confirmação ou oferece Desfazer;
  - contrato formal só para entrega programada; compra avulsa abaixo da alçada vira "Aprovar e emitir pedido" (sujeito à decisão da seção 5);
  - "Restaurar demonstração" fica só no protótipo e não vai para o produto.

## Onda C · EX-26 ampliado (substitui o texto da 2ª versão)

EX-26 Painéis por exceção (PAGR, PMAN, PSUP, IN-04; P60):
  - todo número abre a lista filtrada;
  - sem somas repetidas e sem linhas "nada a fazer agora";
  - cerca de 6 indicadores de resultado por painel, com meta e tendência; o painel mostra primeiro os que pedem ação e deixa o resto sob demanda.
  - Indicadores que provam resultado, por módulo (do painel de especialistas):
    - agronomia: % de aplicações acima do NC e dentro da janela, eficácia por produto × alvo, custo de controle em R$/ha, % de recomendações com registro válido, % de vistorias no prazo;
    - PCP: % de área feita dentro da janela, aderência plano × executado, déficit de capacidade visto com semanas de antecedência, tempo entre impedimento e liberação;
    - execução: ha/h real × padrão, horas paradas por causa, custo por ha da operação, % da área aplicada dentro das condições;
    - irrigação: lâmina aplicada × necessidade, horas em ponta, % da outorga usada;
    - suprimentos e estoque: % da demanda coberta antes da janela, ruptura que parou O.S., economia realizada, capital parado, perda por validade, acuracidade de inventário;
    - manutenção: disponibilidade da frota na janela, MTBF/MTTR, % de preventiva, backlog em horas, custo por hora;
    - colheita e pós-colheita: perda na colheita, erro da previsão (WAPE), % classe A, % de lotes aprovados, quebra;
    - comercial: % vendido × custo coberto, preço contra referência, basis, OTIF, frete por tonelada;
    - gestão: custo por saca e margem por hectare por talhão, desvio decomposto, caixa de 13 semanas.

## ANEXO A · PRINCÍPIOS DE PRODUTO (P01–P66)
Definidos na conversa como padrão de excelência para gestão agrícola: o mais clean, minimalista e funcional possível, com o mínimo de digitação e cliques, o máximo de automação, autocomplete e listas, e zero retrabalho. Servem de régua para os EX; não são requisito por si.

A. Estrutura (Menu → Listagem → Detalhe → Sub-detalhe)
P01 Menu agrupado por tarefa: Hoje · Lavoura · Operação · Recursos · Resultado.
P02 A home "Hoje" é a lista de pendências, com a ação no próprio item. Sem gráficos decorativos.
P03 Talhão. Estados: Ativo · Inativo. Detalhe: Safra atual · Operações · Monitoramentos · Solo · Custo e resultado · Mapa.
P04 Plano de safra. Rascunho→Enviar para aprovação · Em aprovação→Aprovar · Vigente→Revisar (cria nova versão) · Encerrado. Detalhe: Talhões e culturas · Operações previstas · Insumos · Orçamento · Planejado × realizado.
P05 Ordem de serviço. Estados em P12. Detalhe: Resumo · Insumos · Máquinas e equipe · Apontamentos · Custo · Histórico.
P06 Monitoramento (MIP). Aberto→Avaliar · Avaliado→Decidir; controlar gera O.S., aguardar agenda revisita. Detalhe: Pontos · Pragas e níveis · Mapa de calor · Decisão e responsável técnico.
P07 Insumo/estoque. Disponível · Reservado · Vencendo · Bloqueado. Detalhe: Saldo por depósito e lote · Movimentos · Reservas · Preço médio.
P08 Máquina. Disponível · Em operação · Em manutenção · Inativa. Detalhe: Uso (h, ha) · Abastecimentos · Manutenções · Custo-hora.
P09 Romaneio. Pesagem→Classificar · Classificado→Fechar · Fechado. Detalhe: Pesos · Umidade e impureza · Destino · Contrato.
P10 Contrato de venda. Aberto→Registrar entrega · Em entrega · Cumprido. Detalhe: Volume · Entregas · Preço · Recebimentos.
P11 Mapa, calendário e quadro são visões da mesma listagem, não telas novas.

B. Ciclo da O.S.
P12 Uma ação primária por estado:
    Rascunho → Programar (pede só talhão, operação e janela);
    Programada → Liberar (verifica estoque e reserva, máquina e operador livres, receituário, carência e restrições, alçada);
    Liberada → Iniciar execução (envia ao app ou ao monitor da máquina; a reserva vira retirada);
    Em execução → Apontar (área, horas, insumo real, clima, GPS, foto; Pausar como secundária);
    Pausada → Retomar (com motivo);
    Concluída → Conferir e encerrar (supervisor confere, sobra devolvida, custo apurado);
    Encerrada (realizado definitivo); Cancelada (motivo, reserva liberada, histórico preservado).
P13 O estado só muda por ação; nenhum "status" editável à mão.
P14 Concluir ≠ encerrar; apontar 100 % da área não encerra a O.S.

C. Verbos além do CRUD
P15 Copiar da safra anterior e usar modelo; copia a estrutura, nunca o executado.
P16 Reprogramar (preserva a data original), pausar e retomar com motivo (vira indicador de parada), dividir e agrupar O.S.
P17 Estornar, inativar em vez de excluir, reabrir com permissão e motivo, desfazer no que é reversível. Nada que mexeu em estoque ou custo é excluído.
P18 Conferir apontamento (só o conferido entra no custo definitivo), devolver sobra, fechar período, ratear.
P19 Reservar, retirar, transferir e devolver como movimentos com rastro.
P20 Comparar (planejado × realizado, talhão × talhão, safra × safra, no mesmo recorte e unidade) e simular (sem gravar).
P21 Atribuir, comentar e mencionar, anexar foto ou documento, compartilhar a O.S. em PDF ou link; a conversa fica no registro.
P22 Importar e exportar (planilha, KML/shapefile, XML de NF-e, arquivo da máquina) com prévia do que entrou e do que falhou.
P23 Ação em massa com resultado parcial explícito; selecionar talhões gera uma O.S. por talhão; colar do Excel na grade. (Aprovação agronômica continua individual.)

D. Entrada mínima
P24 O usuário só informa o que o sistema não sabe: a diferença do planejado, decisões técnicas, medidas sem sensor e aprovações.
P25 Cada registro nasce preenchido pelo anterior: plano → O.S. → apontamento → custo → financeiro.
P26 Apontamento por exceção: "Executado como planejado" em 1 toque; só a diferença é digitada; sinalizado se GPS ou telemetria contradizem.
P27 Contexto Fazenda · Safra fixo e herdado; abrir pelo talhão ou pelo mapa já seleciona; máquina e operador sugeridos pelo contexto.
P28 Captura automática: GPS, hora, clima, telemetria, balança, XML da NF-e, QR de máquina e lote.
P29 Cálculo no lugar de campo: total = dose × área, nº de tanques, horas pelo horímetro, L/h, peso líquido corrigido por umidade e impureza, fim da carência, custo.
P30 Unidade ao lado do campo e conversões centralizadas; data da operação ≠ data do registro; executor ≠ usuário logado; último valor só para contexto, nunca para dose, lote ou quantidade; seletor que distingue homônimos; um campo de observação.
P31 Listas que aprendem (chips dos mais usados) e busca tolerante a acento, código e apelido.
P32 Criar ali mesmo o cadastro que falta.
P33 Todo valor automático mostra a origem e é editado no lugar.
P34 Automação gera rascunho e nunca executa (estoque mínimo → pedido; horímetro → preventiva; MIP → O.S.; O.S. concluída → devolução).

E. Zero retrabalho
P35 Validação na entrada, com a correção escrita na mensagem.
P36 Cadastro único, referenciado em todo lugar.
P37 Rascunho automático e offline, com fila visível; "salvo no aparelho" ≠ "recebido pelo servidor".
P38 Envio idempotente.
P39 Conferência por exceção: só divergências; o resto em massa.
P40 Corrigir = estorno + novo registro pré-preenchido.
P41 Um lançamento produz todos os efeitos: estoque, custo e planejado × realizado.

F. Regras de negócio
P42 Estoque atômico e nunca negativo; período fechado só aceita estorno; sincronização com versão e conflito visível.
P43 Produto registrado para cultura e alvo; dose acima da bula bloqueada ou exceção com RT; carência e reentrada bloqueiam; condições de aplicação registradas; área apontada maior que o talhão alerta; APP e reserva legal bloqueiam; capacitação do operador; rotação de mecanismo de ação. Normas: conferir vigência e parametrizar.
P44 Conflito de máquina ou operador no mesmo horário; preventiva pelo horímetro.
P45 Custo parcial ≠ zero; razões (custo/ha, produtividade) não se somam; rateio com critério declarado; planejado × realizado no mesmo recorte.
P46 Permissão por papel e fazenda; alçada por valor e tipo; auditoria com antes/depois, quem, quando e de onde.

G. Interface
P47 Lista e detalhe lado a lado no desktop; tela cheia no celular.
P48 Grade editável inline para lançar vários de uma vez.
P49 Etapas no detalhe com dica do próximo passo.
P50 Linha do tempo de eventos no detalhe.
P51 Busca global (⌘K), atalhos N/E/Esc, Enter cria a próxima linha, datas "hoje/ontem/+7".
P52 Visões salvas.
P53 Desfazer em snackbar; confirmação só no irreversível.
P54 Resposta ao toque em menos de 100 ms; skeleton no lugar de spinner.
P55 Plano enviado à máquina e aplicação real voltando como apontamento.
P56 MIP com mapa de calor e decisão.
P57 Anatomia clean: uma primária, secundárias no ⋯, sem cards nem ícones decorativos, uma cor de destaque, estado em texto.
P58 Modo campo: offline, fila visível, alvos de 48 px, contraste para sol, um apontamento por tela.

H a L. Fluxo, indicadores, metas, limites e cortes
P59 Fluxo encadeado: plano → recomendação → O.S. → liberar → retirada → execução → apontamento → conferência → devolução → encerramento → planejado × realizado; colheita → romaneio → armazém → contrato → receita → margem por talhão; ciclos paralelos de MIP, manutenção e compra.
P60 Indicadores que mudam decisão, com drill-down até o apontamento e marcados como parciais quando falta dado.
P61 Metas de toques: apontar como planejado 2 toques e 0 digitação; com diferença 3 toques e 1 número; mesma operação em 8 talhões 4 toques; receber compra 0 digitação; abastecer 1 número; romaneio 2 números; monitorar praga 0 texto; chuva 1 número.
P62 A automação para em liberar, receber, encerrar e pagar (sempre um toque explícito); dose, lote e quantidade vêm do plano ou da medição; todo valor automático é visível e editável.
P63 Formulário com 3 a 5 campos visíveis e o resto em "Mais opções"; sem wizard para cadastro.
P64 Uma ação primária com verbo e objeto; sem "Salvar", "Salvar e novo" e "Salvar e fechar" lado a lado.
P65 Sem menus por perfil: a mesma tela, com permissões diferentes.
P66 Sem um relatório em PDF para cada coisa: listagem com filtro, agrupamento e exportação.

Suposições dos princípios: foco em grão e fibra com operação mecanizada (pecuária, café e cana seguem o mesmo esqueleto com entidades próprias); telemetria, balança e estação são opcionais (sem elas, vira 1 número digitado); as referências de mercado citadas na conversa (Airtable, Linear, Stripe, Salesforce Path, SAP Fiori, John Deere Operations Center, Cropwise) vêm do comportamento público conhecido, não de auditoria atual; normas precisam de conferência de vigência; metas de toque precisam ser validadas com cronômetro e operador real.
