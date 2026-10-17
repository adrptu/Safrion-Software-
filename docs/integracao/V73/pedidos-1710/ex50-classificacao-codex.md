<!-- Cópia fiel do comentário 6234421209 do Codex no PR #47 (17/10/2026, base 4d06b39), versionada pelo Claude para revisão item a item. Autor do conteúdo: Codex. -->

# EX50 — classificação estática consolidada dos 123 IDs

Base: 4d06b39. Conferência de fonte e provas parciais: não comprova equivalência funcional, não libera exclusões, não conclui o protótipo. Pareceres por item conservam limites e recibos. Testes de navegador continuam bloqueados para Codex.

## 1 · AG-01 › #VIS-…:decidir e :programar
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/agronomia.py:587-620
agHash reconhece VIS:decidir/programar, consulta mipGet/mipProx atual, ajusta filtros e abre formulario somente se proxima acao permite. Nao executa decisao por navegar. Preservar ID, talhao/alvo, estado atual, mensagem inexistente, retorno/foco/trap. Nao substituir link contextual por emissao automatica.

## 2 · AG-04
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/agronomia.py:245-268
AG04 mistura base de recomendacoes com receituarios vivos mipGet/cenario. a4Rec distingue rascunho/emitido/cancelado e OS cancelada, motivo/substituto e origem VIS; encaminha decidir ou OS pelo estado. Preservar origem/RT/registro/unidades/janela/versao e cancelamentos; nao transformar tabela em seed nem considerar texto AGROFIT validacao legal.

## 3 · AG-04det
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 4 · AG-05
Conferido estaticamente; migracao condicionada a equivalencia
Fonte: agronomia.py:340-379
Biblioteca guarda fonte/escopo/RT em grade local; Publicar e mensagem. Migrar metadados e versionamento sem presumir publicacao efetiva.

## 5 · CA-02
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 6 · CA-03
Confirmado; migracao exige reconciliar fonte da ocorrencia
Fonte: campo.py:441-449,453-520; mobile.py:721
CA-03 atualiza g_oc local; MB-04 grava cenOcorrencia. Encerrar usa imsg fixo. Nao assumir sincronizacao por texto de encaminhamento.

## 7 · CD-01 › detalhe do talhão
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/cad_fazendas.py:244-255,308-337,470-521,675-685
Entrada CD01 para detalhe usa ID via #talhao= e irDet; detalhe generico mesmo do ID102 ja conferido. Seletor mostra talhao escolhido ou escolha explicita sem substituicao silenciosa; lista em arvore por fazenda. Preservar ID/fazenda, estado inativo, safra/parcelas/versoes e rascunho/foco na navegacao. Reutilizar prova estatica102, sem teste navegador novo.

## 8 · CO-06
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 9 · GE-01
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 10 · GE-06
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 11 · IN-01
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/inicio.py:1706-1742
IN01 fila seed fixa; prazo/responsavel editados na grade local e contadores derivados dessa grade. Alertas agrupados e sincronizacao pendente sao texto seed. Preservar origem/ID, estado e impedimento atual, dono/prazo, contagem sem duplicar casos e link preciso ao comando. Mudar tarefa nao altera origem nem concede permissao; convergencia com Meu dia/MAPA precisa estado vivo, nao copiar esses numeros.

## 12 · IN-02
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 13 · IR-01 › seletor de etapas
Conferido estaticamente; preservar comandos ao migrar navegacao
Fonte: irrigacao.py:36-46
Faixa e navegacao livre entre quatro telas, nao wizard; preservar acessos e pendencias ao converter em abas.

## 14 · LO-02det
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 15 · MB-05 › aba Almoxarife
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/mobile.py:740-815
MB05 almox mistura REQ031/R38 seed e demanda Fungicida A viva demViva/cenDisp com liq/cond/bruta. Preservar falta firme separada de quarentena sem compra automatica, nao congelar reservas sem conflito. Aba operador usa fila/hash e cenConfirmarRecebimento compartilhado; nao substituir por cartoes seed. Role local demonstrativo nao comprova permissao; divergencia say nao executa congelamento.

## 16 · MB-05det
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/mobile.py:817-842
MB05det devolucao usa s.rc local e recibo DV0912 fixo; altera exibicao dev/cus sem cenMudar ou estoque compartilhado. Divergencia 8/10 e mensagem e nao conserva saldo2 efetivamente. Preservar quantidade recebida real, saldo pendente com dono, produto/lote/unidade e condicao de retorno, recibo e fechamento somente apos conciliacao. Material preparado nao volta como produto original; sobra integra depende inspecao.

## 17 · MB-08
Confirmado como demonstracao; manter nao equivale a funcionamento
Fonte: mobile.py:969-1014; acoes say e primary_href para recibo fixo
Sem comando de dominio neste trecho; recibo fixo nao comprova encerramento. Nao reexpor como operacao validada.

## 18 · OS › colunas ocultas
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/processo_os.py:1743-1752
Sit/dono/acao sem ess; padrao id/ativ/tal/prazo/fase/prog. Confirmada diferenca entre fase e situacao/impedimento. Migrar proximo passo/dono/estado para leitura direta mantendo tipagem/filtro e escolha de colunas; nao confundir icone com texto equivalente.

## 19 · PL-04
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 20 · PL-05det
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 21 · SU-01
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 22 · SU-02
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 23 · SU-05
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 24 · SU-06
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 25 · SU-08
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 26 · Tabelas › ⋯ da linha
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/engine.py:1774-1796;g2lib.js:604-636
Anexo tem diagnostico desatualizado: menu_linha/rmenu permite menu sem dele. Extrai act, preserva atalhos desce/full e sufixo seta, exclui por ultimo com confirmacao; sem acoes remove coluna. Falta ativacao por grade nao equivale a limitacao do motor. Reutilizar revisao EX47; nao reintroduzir coluna vazia nem perder guards/foco.

## 27 · BO-01
Presenca e acesso confirmados; decisao comercial pendente
Fonte: plataforma.py:23,150-189
BO-01 tem ligacao nas telas da plataforma; parametros de exemplo, decisao de precos pendente.

## 28 · BO-02
Conferido estaticamente com ressalvas; migracao pendente
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 29 · GE-04
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/gestao.py:320-377
GE04: remessa, retorno e proposta usam flags locais e valores fixos; nao comprovam banco ou comando compartilhado. Preservar origem do titulo, proposta/aprovacao/remessa/liquidacao distintas, conta/data, obrigacao unica, recibo bancario e divergencia de conciliacao.

## 30 · GE-05
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/gestao.py:382-445
GE05: caso filtra grade; cobranca explicitamente simulada e credito CR031/RC12 ajusta grade local. Preservar caso/entrega/titulo, venda original, credito separado da qualidade fisica, autorizacao de cobranca, idempotencia e totais por cliente; sem prova de operacao financeira real.

## 31 · MOD-OUT
Presenca e acesso confirmados; decisao comercial pendente
Fonte: ui37.py:88-89,121; modulos.py:123
MOD-OUT e hub gerado e acessivel; isolamento nao pode apagar acesso de teste do app sem destino substituto.

## 32 · ON-01
Presenca e acesso confirmados; decisao comercial pendente
Fonte: ui37.py:89; onboarding_backoffice.py:54-65
Onboarding tem entrada em Outros acessos; drawers demonstrativos nao comprovam cadastro integrado.

## 33 · PT-01
Presenca e acesso confirmados; decisao comercial pendente
Fonte: ui37.py:88; parceiros.py:164-194
Portal tem entrada e liga cotacao, pedido, credito e assinatura; exclusao exige preservar destinos e decisao de escopo.

## 34 · PT-02
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:196-217
PT02 lista seed de convites/propostas selecionadas e nao selecionadas. Preservar escopo concedido, finalidade/prazo, versoes e motivo agregado sem concorrentes; link ao contrato/pedido nao substitui sua aprovacao.

## 35 · PT-02det
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:218-269
PT02det recalcula quantidade*preco por item, edita condicoes/esclarecimentos em grades locais. ver/chg apenas incrementam versao e toast; nao demonstram snapshot historico, PDF, entrega ao comprador nem bloqueio temporal. Preservar rascunho/submetida, snapshot, prazo, CIF/FOB/unidades e finalidade concedida.

## 36 · PT-03
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:270-312
PT03 grade de ofertas/reserva seed e proposta local. js.once env e reset apos editar nao comprovam ATP compartilhado/expiracao/conversao. Preservar reserva temporaria, saldo publicado nao negativo, devolucao/deducao unica, janela e aceite das partes antes de contrato; recibo PC7781 e mensagem demonstrativa.

## 37 · PT-04
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:313-335
PT04 dossies e historico de acesso fixos. Preservar concessao por bloco/finalidade/vigencia, decisao acessivel apos expiracao sem reabrir blocos e registro de acesso real; aprovacao condicional nao e desembolso nem compra paga.

## 38 · PT-04det
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:336-373
PT04det condicoes/complemento/contraproposta via drawer e recusa/conferencia via mensagem. Nao comprovam revogacao, motivo obrigatorio, nova versao, documento ou liberacao real. Preservar autorizacao por bloco, documento condicionante, aceite, parcelas e servico da divida separados; recusa revoga acesso mantendo trilha.

## 39 · PT-05
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:374-399
PT05 lista seed de negocios proprios ganhos/perdidos, documentos, mensagens vinculadas; preservar origem cotacao/proposta/contrato/pedido e motivo agregado, sem revelar concorrentes.

## 40 · PT-05det
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:400-441
PT05det: contrato140t distinto de pedido liberado; titulo calculado PC.qtd*preco, cargas recebidas/apto/quarentena separadas. Previsao editavel local; divergencia flag local; envio documento drawer. Preservar unidade t/kg, pagamento apos aceite, documento por carga, revisao com novo aceite e recusa sem reentrada automatica em estoque apto; mensagem nao prova notificacao/anexo/movimento.

## 41 · PT-07
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:483-533
PT07: empresa/preferences/usuarios editados em grades locais; autorreferencia admin readonly; revogar e Pt.act mensagem, convite simulado; correspondencia recalculada e toast. Preservar identidade CNPJ, org/papel/ativo, exclusao de autopromocao, revogacao real de sessoes e preferencias. Plano/preco segue hipotese e aceite explicito; assinatura nao autoriza dados nem altera ranking. Nao ativar cobranca/campanhas.

## 42 · AG-03
Conferido estaticamente; migracao condicionada a equivalencia
Fonte: agronomia.py:149-192
AG-03 le e grava mipGet/mipMudar, preserva rascunho e retoma decisao quando OS cancelada. Nao e somente copia estatica.

## 43 · AG-03det
Conferido estaticamente; migracao condicionada a equivalencia
Fonte: agronomia.py:198-216
Detalhe DIA-007 e fixo; lista AG-03 e dinamica. Substituir links de evidencias/laudos/recomendacao sem perder contexto.

## 44 · AG-06
Conferido estaticamente; migracao condicionada a equivalencia
Fonte: agronomia.py:384-427
Eficacia usa casos fixos, formulario local e mensagem de parecer. Preservar pre/pos, metodo, unidade e distincao observacao/causalidade na migracao.

## 45 · CA-01
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/campo.py:169-220
CA01: lista usa _ordens; previa de caminho de liberacao e somente leitura e considera A-liberar; preparar/emitir periodo mostra mensagem fixa. Preservar janela/equipe/permissoes, prontidao atual, fase distinta de impedimento e nao inferir aprovacao pela emissao. Nao regredir previa somente leitura nem confundir com agrupamento ja entregue no PR105.

## 46 · CA-01det
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/campo.py:221-305
CA01det: _apRecalc recalcula linhas locais; texto de trilha nao comprova historico persistido. ajustar_saldo consulta cenGetOS0421 e so encaminha saldo positivo A-liberar. Preservar realizado/planejado, historico real de correcao, versao/saldo/reaprovacao atuais, custodia e encerramento do turno distinto da O.S.

## 47 · CA-01x-os0420
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/campo.py:308-367
CA01x OS0420: cenario fixo 30/100 ha (18 confirmados/12 provisorios), saldo70 impedido OM0233 e V2 executada/V3 restante. Preservar versao da execucao, alteracao somente do restante, aptidao/substituto confirmado, custodia/custo e impedimento separado da fase. Seed agronomico nao e recomendacao validada.

## 48 · CA-04
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/campo.py:527-574
CA04: requisicoes D2 por OS/item/lote/unidade; recebimento sem entrega bloqueado e encerramento informa custodia10sc; solicitar material e mensagem. Preservar identidade, devolucao declarada versus recebida/qualificada, responsavel e bloqueio de fechamento ate saldo/destino resolvido. Rodape nao comprova sincronizacao entre telas.

## 49 · CO-01
Conferido estaticamente: legado local, equivalencia pendente
Fonte: colheita.py:159-213
CO-01 mostra previsao e erro de cenario; edita grade local e publica por mensagem. Preservar versao congelada, classe comercial e escopo temporal no destino.

## 50 · CO-02
Conferido estaticamente: legado local, equivalencia pendente
Fonte: colheita.py:216-253
CO-02 programa ordens de cenario com idrw/imsg/Pt.act; nao comprova reserva de recursos nem emissao real. Migracao deve usar OS vigente.

## 51 · CO-02det
Conferido estaticamente: legado local, equivalencia pendente
Fonte: colheita.py:256-309
CO-02det soma t em g_ap local; concluir altera c2f, finalizar turno so toast. Nao migrar como comando de apontamento integrado. Preservar separacao area/peso e conciliacao por carga.

## 52 · CO-03
Conferido: carga em grade local, equivalencia pendente
Fonte: colheita.py:311-353
CO-03 calcula bruto-tara e gera identificadores no grid; vincular pesagem/romaneio e mensagem. Usar carga unica no destino para nao duplicar massa.

## 53 · CO-04
Conferido: recebimento legado demonstrativo
Fonte: colheita.py:356-390
CO-04 usa linhas fixas/Pt.act para receber e segregar; preservar carga/retorno e qualidade, nao copiar sucesso textual como movimentacao.

## 54 · CO-05
Conferido: lista legada com edicao local
Fonte: colheita.py:393-434
CO-05 cria/edita g_ob local e anuncia autorizacao por Pt.act. Preservar origem/rota/janela e separacao processo encerrado versus lote liberado; migracao para BEN depende de equivalencia dos comandos atuais.

## 55 · CO-05det
Conferido: detalhe legado com estados locais
Fonte: colheita.py:437-506
co5_bal recalcula entrada/saidas/descarte; concluir, conferir e fechar alteram c5f/c5c locais e editar invalida conferencia. Finalizar turno apenas toast; genealogia fixa. Preservar balanco e qualidade independente no BEN, sem adotar tolerancia 0.05 t ou textos fixos como regra canonica.

## 56 · CO-06det
Confirmado; detalhe legado de qualidade e demonstrativo
Fonte: colheita.py:559-594
Liberar e Manter bloqueio usam imsg; destinar usa idrw. Recibo QL-1148 e texto fixo, nao prova comando. Migrar ao detalhe do lote com fonte vigente.

## 57 · CO-07
Confirmado; saldo legado usa dados de cenario
Fonte: colheita.py:597-645
Grade de lotes preserva qualidade/reserva/custodia e diferencia sc50/sc60/kg. Migrar por fonte de movimentos vigente, sem somar sacas de massas diferentes.

## 58 · Ferramentas de demonstração
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/ui37.py:271-284;areas/processo_os.py:1179-1180,1374-1378,1735-1736
Perfil de demonstracao no avatar e reset OS com confirmacao cenReset compartilhado. Consolidar entrada no avatar nao remover capacidade de QA; preservar perfil todos papeis, aviso do alcance OS/estoque/app, cancelamento, recuperacao de cenario ilegivel e separacao da data simulada. Nao executar reset nem presumir que todos modulos usam mesmo armazenamento.

## 59 · GE-06det
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: gestao.py:491-517
GE-06det explica denominador ha-operacao, decomposicao volume/consumo/preco e documentos, mas valores sao fixos. Migrar evidencia e metodo para GE-02det sem tratar hipotese como causa confirmada.

## 60 · GE-07
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: gestao.py:525-569
GE-07 cria/edita casos g_ac com dono/prazo e muda estado local ao encerrar/reabrir. Verificar resultado e mensagem fixa; evidencia de encerramento 5% para 3.8% e hardcoded. Meu dia deve conservar origem, hipotese, evidencia, dono, prazo e historico; proposta de parametro e operacao distinta.

## 61 · GE-08 › #vis=
Conferido estaticamente; aceite da migracao pendente
Fonte: modulos.py:98-103 e gestao.py:738/749
Preservar entradas e comandos vivos; nenhum aceite de exclusao.

## 62 · IN-03
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: inicio.py:1744-1799
IN-03 combina tarefas de cenario com leitura dinamica irrGet/irrProx para OS-0422/0423; prioridades e donos respeitam ajustes locais. Migrar para Meu dia preservando links de origem, prazos da obrigacao e dependencia; nao classificar toda agenda como texto fixo.

## 63 · IR-02
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: irrigacao.py:277-367
IR-02 tem programacao executavel via irrMudar/irrProgramar, agenda captacao-ordens de agua/fertirrigacao, uso/outorga e bloqueios. Mantem tarefa unica existente, necessidade/eficiencia/passadas/volume/duracao, sugestao de janela e tratamento agua sem produto. Consolidar em IR-01/03 somente preservando essas funcoes e deep link #programar=; nao excluir como pagina meramente demonstrativa.

## 64 · LO-01
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: logistica.py:140-220
LO-01 reprograma janela preservando original e avalia conflito de doca em linhas locais. Agrupamento e mensagem de incompatibilidade fixa; nao confundir com agrupamento OS do PR105. Migrar agenda/capacidade/conservacao/rota preservando compromisso versus expectativa.

## 65 · LO-02
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: logistica.py:222-371
LO-02 altera fila e separacao em estado local, valida identificacao na chegada, lote apto/quantidade e condiciona encaixe a separacao. Toast de saldo 50000-q nao prova movimentacao de estoque. EXPED deve preservar fila, motivo, janela original, aptidao fiscal/qualidade e saida unica sem copiar recibos fixos.

## 66 · LO-03
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: logistica.py:450-494
LO-03 edita previsao/transportador em g_vg e usa viagens, evidencia, rateio e OTIF fixos. Preservar janela original, aceite parcial, saldo recusado e caso comercial; retirada nao comprova entrega, reprogramacao nao substitui compromisso.

## 67 · LO-04
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: logistica.py:498-590
LO-04 cotacao/pedido de documento sao explicitamente simulados; contratar/encaminhar pagamento alteram grade e flags locais ct/pg com recibos fixos. Preservar elegibilidade, unidades R$/t/viagem/km, medicao, contrato congelado e custo unico; ERP nao deve receber titulo real a partir desses toasts.

## 68 · MA-01
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 69 · MA-02
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 70 · MA-03
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 71 · MA-04
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 72 · MA-04det
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 73 · MA-05
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 74 · MB-10 › aba Motorista
Conferido estaticamente; aceite da migracao pendente
Fonte: mobile.py:392,1243-1244,1263-1280
Preservar entradas e comandos vivos; nenhum aceite de exclusao.

## 75 · Main
Exclusao refutada e retirada por Claude; manter pagina tecnica Main
Fonte: [6232949775, 6232996804, 6233013087]
Revisao de fonte, nao navegador; preservar condicoes e ressalvas dos recibos.

## 76 · OS › "Abrir ordem completa ›"
Conferido estaticamente com limites funcionais
Fonte: processo_os.py:1315,1587
Link completo depende de o.link; remover exige preservar a informacao de destino no detalhe vigente.

## 77 · OS-0424-ficha
Conferido estaticamente com limites funcionais
Fonte: os_campo.py:70-86,167-180; processo_os.py:1600
Impressao le cenPreparoOrdem e versao vigente, mas esta fixada a OS-0424. Nao generalizar cobertura a todas OS.

## 78 · PL-01
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:148-200
PL-01 edita grades locais safra/cultivo, novas safras recebem link SAF sem identidade no destino. Vincular ciclo/revisar idade sao mensagens. Consolidacao deve preservar ocupacao perene, plantio previsto distinto de realizado, hipoteses de meta e aprovacao de plano/orcamento.

## 79 · PL-02
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:203-278
PL-02 atualiza pendencia vencida na grade g_op (realizada/pendente/nao aplicavel), com evidencia/prazo/motivo; mensagens de demanda nao comprovam calculo integrado. Modelo e antecipacao sao simulados. Preservar necessidade unica e saldo, gatilhos por extenso, excecoes locais e consulta ao realizado antes de decidir atraso.

## 80 · PL-02det
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:280-312
PL-02det gera datas por ancora prevista do T1-A e compara dose local/padrao; grade permite motivo local, mas resumo de custo e situacao sao fixos. Migrar com identidade do talhao, motivo/versionamento e excecao preservada; nao copiar justificativa agronomica de cenario como recomendacao geral.

## 81 · PL-03
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:314-376
PL-03 capacidade/ocupacao/deficit e condicoes das maquinas sao cenarios fixos; edicao de hipoteses g_cen, simulacao/publicacao por mensagem. Preservar carga por classe, rendimento, disponibilidade tecnica versus ocupacao/elegibilidade e manutencao; consolidar em SAF sem prometer contratacao.

## 82 · PL-05
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:460-518
PL-05 edita dono/prazo/alternativa locais em g_imp; notificacao explicitamente simulada, reprogramacao por drawer e aprovacao por mensagem. Preservar impedimento na origem, sem criar etapa Kanban; resolver nao inicia nem libera, e reprogramar afeta somente saldo futuro.

## 83 · PL-06
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: planejamento.py:559-625
PL-06 recalcula janela de colheita local ao mudar data de pA/pB, mas mapa, sobreposicao e curva semanal sao cenario calculado ao gerar a pagina; toast promete revalidar ao publicar. Preservar identidade/geometria/area e hipotese de produtividade/ciclo; equivalencia SAF exige validacao geometrica e curva integrada, sem duplicar hectares.

## 84 · PM
Exclusao retirada: manter alias tecnico fora do menu
Fonte: maquinas.py:33-35,1476-1485; build.py:38-40
Recomendacao ao Claude; aceite pendente. Nenhuma exclusao executada.

## 85 · PT-06
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/parceiros.py:49-90;442-482
PT06: indicadores seed, conversao ganhos/(propostas-em analise), receita apenas concluidos. Acao interna possui pt06Check efetivo para linha r2/org e pessoa ativa F01, alterando grade local explicitamente sem envio. Preservar estes guards, denominadores, origem/cobertura, escopo proprio e supressao de amostra pequena; texto de exportacao/consentimento nao prova exportacao nem governanca. Elegibilidade e seed, nao sincronizacao comprovada com edicoes PT07.

## 86 · SU-03
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: suprimentos.py:365-425
SU-03 calcula fisico-retido-reservado a partir de lotes de geracao, distingue custodia/consignado/valor; reserva RUN.res altera grade local g_sal e flags, sem prova de comando central. Preservar unidade, lote, proprietario/local e custodia fora do fisico; nao tomar toast de reserva como integracao.

## 87 · SU-03det
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: suprimentos.py:428-528
SU-03det tem dois caminhos: conflito com decisoes locais res/wait e sem-conflito com faViva/cenGet/cenResPropria/cenDisp/demViva e cenOuvir. Este ultimo le estoque/reserva e demanda unificada de SAF/CMP, separa falta firme de qualidade pendente e evita duplicar plano com OS. Consolidacao em EST deve preservar essa leitura viva e links de origem; nao classificar o detalhe inteiro como demonstracao fixa.

## 88 · SU-04
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: suprimentos.py:531-601
SU-04 equaliza mercadoria/frete e alcada com dados de geracao; selecao e convite alteram flags locais, envio explicitamente simulado. Preservar necessidade unica, fornecedores homologados, rascunho versus enviado, base comparavel e aprovacao distinta da selecao.

## 89 · SU-05det
Conferido estaticamente; consolidacao condicionada a equivalencia
Fonte: suprimentos.py:693-744
SU-05det calcula saldos/exposicao do contrato demonstrativo; reprogramacao e emissao alteram flags locais e calendario fixo, sem integracao de recebimento real. Preservar liberado acumulado versus recebido, saldo contratual sem dupla subtracao, tolerancia aceita e condicoes de credito/recebimento antes de liberar.

## 90 · SU-07
Conferido estaticamente; equivalencia funcional pendente
Fonte: suprimentos.py:863-945
Fila por requisicao com solicitado/entregue/consumido/custodia; RUN.sol e sep/ent/ent40 alteram g_req e flags locais, sem prova de movimento central. Preservar versao aprovada, impedimentos, saldo autorizado, FEFO, parcial executavel, recebedor e ausencia de segunda saida no consumo.

## 91 · SU-07det
Conferido estaticamente; equivalencia funcional pendente
Fonte: suprimentos.py:948-1016
Balanço local rcv/dst/conc e recibo fixo CC-0417. Declaracao nao baixa custodia; recebimento distingue apto/quarentena/improprio; destinacao aguarda aprovacao; conciliacao exige zero. EST precisa manter identidade da requisicao, segregacao e historico; toast nao comprova integracao.

## 92 · SU-09
Conferido estaticamente; equivalencia funcional pendente
Fonte: suprimentos.py:1105-1182
Inventario g_inv local: planejamento, recontagem, causa/evidencia e flags de aprovacao. apr gera AJ local e afirma extrato sem comando central neste handler. Preservar corte por escopo, contagem cega, segregacao real contador/aprovador, recontagem e ajuste unico; textos e perfil Ana fixo nao comprovam controles.

## 93 · VE-01
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:85-186
Balanço misto: bases de cenário fixas e saldoRT local para uma reserva. Preservar identidade única reserva/compromisso, classe/janela, aptidão, capacidade e margem; garantia não vira demanda física. Equivalência PCOM ainda não executada.

## 94 · VE-02
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:188-227
Preços e comparações fixos; alertas editáveis locais, sem prova de alimentação externa ou notificação. Preservar fonte/licença/data/atraso, ausente diferente de zero, unidade/moeda declaradas e alerta sem venda. Conversões de exemplo não validadas como regra do mercado.

## 95 · VE-03
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:229-290
Ofertas locais com rascunho privado e envio explicitamente simulado; comparação de líquido fixa. Preservar produto/classe/janela, unidade de quantidade e preço, frete/prazo, destinatários autorizados, aceite da versão e oferta distinta de pedido.

## 96 · VE-04
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:293-377
Misto: carteira g_cart/vconf local com saldo B fixo e recibos fixos; toast declara crédito/preço/capacidade sem verificá-los no handler. Reservas g_rsv são vivas via cenOuvir/cenGet/prP/prPedRow/prPanPed e comando compartilhado prReservar. Preservar essa integração, versões, saldo único, unidades e recuperação de conflito; não classificar a tela inteira como estática.

## 97 · VE-04det
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:377-440
Detalhe PV-031: revisão v3 local preserva v2 e exige aceite; genealogia/alocação/financeiro fixos. Preservar versão aceita, quantidade prometível por classe, inspeção, dedução única e recebível condicionado ao evento; envio simulado não é aceite nem confirmação.

## 98 · VE-05
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:443-493
Obrigações físicas, garantias e exposição separadas; novo compromisso altera g_ob e toast afirma recálculo, mas g_dim permanece semeado. Preservar identidade da CPR/barter/contrato, base e janela, aditivo/aceite e liquidação por eventos; garantia não é segunda venda.

## 99 · VE-06
Conferido estaticamente; equivalencia funcional pendente
Fonte: comercial.py:496-550
Casos g_rc locais; autorizar retorno é Pt.act com mensagem, novo caso afirma genealogia sem consulta no handler. Preservar entrega/lote/quantidade/unidade/evidência, retorno bloqueado até Qualidade e encerramento físico+financeiro; crédito separado do retorno e decisão de recolhimento rastreável.

## 100 · AG-01det
Conferido estaticamente; equivalencia funcional pendente
Fonte: agronomia.py:849-867; JS_AG01DET anterior
Detalhe vivo por hash VIS com mipGet/mipRes/mipSit/mipProx e mipMudar para sincronizar/parcial/monitorar/pós. Preservar identidade da vistoria e retorno, unidades/protocolo, ausência distinta de zero, recoleta fora da média. Rota W, GPS/hora/precisão fallback e duas fotos por ponto são gerados: não são provas de coleta real. Manter detalhe com distinção explícita entre dado e demonstração.

## 101 · CA-03det
Confirmado; migracao exige reconciliar fonte da ocorrencia
Fonte: campo.py:441-449,453-520; mobile.py:721
CA-03 atualiza g_oc local; MB-04 grava cenOcorrencia. Encerrar usa imsg fixo. Nao assumir sincronizacao por texto de encaminhamento.

## 102 · CD-01det
Conferido estaticamente; equivalencia funcional pendente
Fonte: cad_fazendas.py:521-687
Detalhe por talhao= com parcelas por safra, áreas cultivável/calculada e versões. cadGravar usa localStorage; polígono salva versão/área e pgeo Validada como simulação. Preservar prévia/motivo, versões vinculadas às OS, área por safra, inativo e recuperação de rascunho; não confundir simulação com geometria persistida real.

## 103 · Faixa "Pagar fatura ›"
Conferido estaticamente; equivalencia funcional pendente
Fonte: ui37.py:349-357; assinatura.js:255-264
Gerador exclui BO/ON/PT/CF05, mas permite demais telas. assinAvisoVals liga faixa por atraso/inadimplência sem perfil/alçada. Restrição proposta a Mapa/Assinatura+AL15 ainda não está comprovada na base. Manter restrição no ponto de uso e alçada no comando cfPor, não inferir permissão pela faixa.

## 104 · GE-02det
Conferido estaticamente; equivalencia funcional pendente
Fonte: gestao.py:221-258
Comparação fixa V1/V2/real com documentos, base preservada e proposta de parâmetro explicitamente indisponível. Contraprova aritmética executada:4000+800+480+528=5808; orçamento flexível4800,desvio1008. Preservar ha-op versus área física, consumo/preço/unidades e origem; cálculo não prova desperdício ou envio de proposta.

## 105 · IR-03
Conferido estaticamente; preservar comandos ao migrar navegacao
Fonte: irrigacao.py:370-414
Lista usa irrGet, etapa e proximo passo; distingue agua e fertirrigacao que abre OS. Migrar sem duplicar fonte nem comando.

## 106 · IR-03det
Conferido estaticamente; preservar comandos ao migrar navegacao
Fonte: irrigacao.py:565-640
Detalhe chama irrTerminar, irrAvanco e irrReclassTudo; preserva rascunho/motivo, zero versus ausencia de leitura e aprovacao da fertirrigacao. Nao confundir com recibo fixo MB-08.

## 107 · IR-04
Conferido estaticamente; preservar comandos ao migrar navegacao
Fonte: irrigacao.py:675-718
Fontes usam irrMudar, irrCalibrar, irrSondaMarcar e consumo irrUsoDia; marcar suspeita/validar afeta balanco. Preservar origem das outorgas no cadastro.

## 108 · Links diretos por ID
Conferido estaticamente; equivalencia funcional pendente
Fonte: Base 4d06b39; tools/prototipo/v37/gen37/areas/processo_os.py:1083-1103;agronomia.py:587-620;cad_fazendas.py:337;producao.py:385-386,515-516;processo_planos.py:125-160;processo_compras.py:620-629
Links por ID sao contrato de entrada/contexto, nao funcao descartavel: OS valida ids/painel e ajusta fazenda/safra, nova preenche sem emitir, usar consome hash; VIS valida proxima acao. Reutilizar28 casos de redirect existentes; nao equivalem a execucao de todos handlers. Cobertura estatica transversal representativa, todas as familias exigem equivalencia na candidata, inclusive desconhecido/encoding/voltar/recarregar/perfil.

## 109 · MB-01
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:373-416
Fila viva por operador ou executante de manutenção; próximo passo via mbPrim/mbOmPasso, cenário compartilhado. Preservar perfil, seleção e fila por janela, sem confundir avatar de demonstração com autenticação real.

## 110 · MB-02
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:418-450
Minhas ordens dinâmicas via mbMinhas/mbCard, cartões da equipe semeados e ACK local. Preservar restrição de responsável, impedimento/revogação, versão realizada versus saldo; ciência não libera execução.

## 111 · MB-02det
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:453-512
Detalhe deriva ordem selecionada/operador, mbPasso, cenPreparoOrdem, custódia e apontamentos/conferências. Preservar ordem, versão, estado de envio e saldo por produto; não remover detalhe vivo ao simplificar navegação.

## 112 · MB-03
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:514-620;180-195
Turno usa cenMudar/cenFecharTurno, valida saldo menos pendente e horas, diferencia consumo sugerido/estimado/informado e excesso em conferência. mbResta extraída:4/4 contraprovas com mbProv fixture; não prova de integração offline. Fechar turno não encerra OS.

## 113 · MB-03x-recibo
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:622-651
Envios derivados de c.app.fila/recibos, reenvio por cenMudar/mbSinal; há recibo APT semeado adicional. Preservar identidade/reenvio sem duplicar, revogação/conflitos e conferência separada. Cenário não comprova servidor remoto ou app instalado.

## 114 · MB-04
Confirmado: app registra ocorrencia no cenario
Fonte: mobile.py:656-721; cenMudar/cenOcorrencia
Foto explicitamente simulada; leitura estatica nao comprova upload nem navegacao.

## 115 · MB-05
Confirmado: vistoria tem entrada e estado compartilhado
Fonte: mobile.py:390,844-907; MB-06 usa dados_mip/mip e hash VIS
Nao testar pelo posicionamento no canvas; navegador nao executado nesta conferencia.

## 116 · MB-06
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:845-908
Coleta viva por VIS/protocolo com mipColetar/mipCorrigir/mipConcluir via mipMudar; incompleta/recoleta reabre sem decisão, correção bloqueada após decisão ou pendência. Preservar unidade/critério, zero versus vazio, foco no próximo ponto e decisão do agrônomo separada; checkbox GPS é demonstração.

## 117 · MB-07
Confirmado como demonstracao; manter nao equivale a funcionamento
Fonte: mobile.py:969-1014; acoes say e primary_href para recibo fixo
Sem comando de dominio neste trecho; recibo fixo nao comprova encerramento. Nao reexpor como operacao validada.

## 118 · MB-08x-recibo
Confirmado como demonstracao; manter nao equivale a funcionamento
Fonte: mobile.py:969-1014; acoes say e primary_href para recibo fixo
Sem comando de dominio neste trecho; recibo fixo nao comprova encerramento. Nao reexpor como operacao validada.

## 119 · MB-09
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:1063-1106
Máquina usa estado/manutenção, herança da alocação, operador distinto do lançador, mbManCmd abastecer/leitura com chave estável para duplo toque. Preservar tanque/lote, unidade h/km, data, cheio, fila/conflitos/estornos e evidência explicitamente simulada.

## 120 · MB-09det
Conferido estaticamente; equivalencia funcional pendente
Fonte: mobile.py:1163-1238
OM viva por hash/seleção, manPode e mbManCmd com chave; serviço/medição/teste e tentativas, motivo para não OK, peças aplicadas/retiradas e destino, leitura/horas explícitas. Aptidão separada da conclusão, com teste e alçada; foto simulada não é evidência real.

## 121 · MB-10
Conferido estaticamente; aceite da migracao pendente
Fonte: mobile.py:392,1243-1244,1263-1280
Preservar entradas e comandos vivos; nenhum aceite de exclusao.

## 122 · ON-01det
Conferido estaticamente; equivalencia funcional pendente
Fonte: onboarding_backoffice.py:127-166
Importação por flags locais grav, imp_ok e prévia semeada. Repetir evita novos flags, mas não comprova leitura de arquivo/transação de cadastro. Preservar CRS/mapeamento/unidades, erros por objeto, parcial explícito e decisão mesclar/ignorar; toast Gravados não prova importação real.

## 123 · OS-0424-app
Conferido estaticamente com limites funcionais
Fonte: os_campo.py:88-112; mobile.py:462
App confirma recebimento via comando; cargas preparadas ficam no estado da tela, apontamento final apenas toast. Nao equivale a aplicacao registrada.


Consolidação recuperável para revisão crítica do Claude: os recibos incrementais continuam válidos, inclusive correção do diagnóstico do menu de linha (item26). Não substitui o checkpoint da issue1 nem cria fila. Próxima ação de autoria Codex permanece SU01 no contrato EX50(a)-SUP, após SHA/liberação da composição; nenhum arquivo do Claude alterado.