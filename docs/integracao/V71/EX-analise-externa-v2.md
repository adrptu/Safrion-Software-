# Análise externa do protótipo, 2ª versão (16/10/2026): EX-01 a EX-37

Substitui a 1ª versão (`EX-analise-externa.md`, EX-01 a EX-31) como insumo. O proprietário colou esta versão em 16/10/2026, no canal do Claude. O texto abaixo segue o dele; só a forma foi organizada em listas.

## Origem e limites

Uma sessão do Claude, fora do repositório, analisou o artefato publicado (versão 1792123204-c09d, fonte a156f83).

**O que foi feito:**
- **Telas:** 148 abertas no navegador. De cada uma, no estado inicial, saíram botões, campos, tabelas e texto.
- **Modais:** um robô clicou em 370 ações e capturou 83 modais e painéis, entre eles 64 formulários com 339 campos editáveis. Ele clicou em uma ação por verbo em cada tela, na primeira linha clicável de cada tabela e nos menus ⋯.
- **Reprodução manual:** os riscos mais graves (PL-04 "Liberar prontas", CA-01 "Liberar selecionadas") e os fluxos OS-0421, MB-03, CA-02, SAF e CO-03.
- **Revisão:** cinco revisões por área, com duas lentes:
  - simplicidade e produtividade, contra a lista P01–P66;
  - valor de gestão, como painel de agrônomo, gerente de PCP, engenheiro agrícola, engenheiro de produção, PCM, suprimentos, comercial e controller, com a IA como camada de automação.

**Limites declarados pela própria análise:**
- nenhum formulário foi preenchido nem enviado;
- todos os modais têm uma etapa só;
- onde não está escrito "medido", cliques e campos são estimativas;
- os dados sintéticos foram tratados como intencionais;
- o repositório pode estar à frente da versão publicada.

**Como entra no trabalho:** é insumo, não requisito. Prevalecem PRD, NAV/DS, protocolo e decisões registradas. Método, critério de entrada e "não fazer" são os mesmos da 1ª versão; a 2ª versão acrescenta a Onda 0 (riscos), que vai primeiro.

## Diagnóstico (nota de valor de gestão / simplicidade, 0 a 5)

| Área | Notas | Área | Notas |
|---|---|---|---|
| Agronomia | 4 / 3 | Suprimentos e compras | 3,5 / 2,5 |
| Cadastros | 3,5 / 3,5 | Estoque | 4 / 2,5 |
| Planejamento | 4 / 2 | Manutenção | 2,5 / 3 |
| Entrada e pendências | 3 / 3 | Colheita e pós-colheita | 3 / 2,5 |
| Painéis | 3 / 2 | Comercial e logística | 3 / 2 |
| Execução de O.S. | 3 / 2 | Gestão e finanças | 3,5 / 3 |
| App de campo | 3 / 3 | Plataforma | 3 / 3 |
| Irrigação | 4 / 3 | | |

**Forte em:**
- rastreabilidade e integridade de saldo;
- cálculo com origem;
- bloqueio que explica causa e responsável;
- automação que propõe sem executar.

**Formulários:** todos de uma etapa; metade dos 339 campos já vem preenchida; os campos numéricos usam teclado decimal e mostram a unidade.

**Fraco em:**
- (a) ações de risco que executam em lote ou com 1 clique, sem motivo nem alçada;
- (b) duas gerações de telas e formulários convivendo;
- (c) dados que se contradizem entre telas e dentro dos modais;
- (d) poucos indicadores de resultado (custo/sc, margem por talhão, % na janela, ha/h, paradas, cobertura, MTBF);
- (e) digitação de dados que o sistema já tem;
- (f) primária ausente, genérica ("Salvar" em 34 de 64 formulários) ou ativa só para recusar depois do clique.

## Preservar (não mexer sem motivo)

- **Faixa "VEIO DE → ESTÁ AQUI → FALTA → PRÓXIMA AÇÃO"** nos detalhes; levar para todo detalhe.
- **Coluna de próximo passo** com verbo e responsável ("Pesar · Lúcia").
- **Formulários de uma etapa,** sem wizard, com a unidade junto do campo.
- **Painel MIP VIS-013:**
  - vistoria → receituário → O.S. em 2 toques, sem digitação;
  - só produtos registrados para cultura × alvo;
  - IRAC, faixa de bula, carência e limite por ciclo;
  - "aplicar até" calculado;
  - O.S. nascendo "A liberar".
- **Bloqueio que diz causa, solução e responsável.**
- **Automação como proposta:** prévia, simulação sem reservar, "Proposto · aguarda PCP", "revisão sugerida, nada alterado".
- **OM preventiva gerada do plano,** com o vencimento original preservado.
- **Conciliação que abre só a divergência.**
- **Prévia de importação** (CD-07) e importação que grava os prontos e mantém os erros (ON-01det).
- **Idempotência e rastreio:** mesmo recibo, "Duplicado · sem nova entrada", extrato imutável, estorno com vínculo.
- **Cálculo com origem visível.**
- **Honestidade do dado:** "ausente ≠ zero", "Parcial · conferir cobertura", "(HIPÓTESE)", "sem custo realizado".
- **Segregação:** quem estava com a custódia não confirma o próprio recebimento; quem aplica o lacre não confere.
- **Offline com recibo em três estados** e custódia em conta fechada.

## Onda 0 · Riscos (primeiro)

### EX-32 Aprovação em lote, contra a decisão de 16/10 ("Aprovação em lote: fora, de propósito")

**Casos citados:**
- **PL-04 "Liberar prontas":** liberou a OS-0430 (dessecação com defensivo) num lote de 5, com a mensagem "OS-0430 ✓ liberada por Ana (agrônoma)". A análise diz que reproduziu.
- **CA-01:** "Selecionar as 12 linhas" + "Liberar selecionadas" processa o lote, com a mensagem "Com produto, quem libera é o agrônomo". A análise diz que reproduziu.
- **IN-02 "Aprovar selecionados":** mistura alçadas (inventário, política de estoque, orçamento da Direção, acesso de operador).
- **CA-03:** encerra ocorrências em lote, inclusive a OC-114 "Grave" com OM ainda em execução.

**Correção proposta:**
- lote só para O.S. "só água" com prontidão e para itens da mesma alçada e do mesmo tipo;
- O.S. com produto é liberada uma a uma, com "aprovou, abre a próxima" (UX-06).

### EX-33 Fricção proporcional ao risco (motivo, alçada, prévia ou Desfazer)

**Executam com 1 clique, sem motivo nem alçada:**
- CO-06det "Liberar" um lote reprovado (defeitos 103 > 86);
- PT-04det "Recusar crédito" (diz "registrada com motivo" sem pedir motivo);
- GE-05 "Emitir crédito";
- LO-04 "Contratar" frete de R$ 1.824;
- AG-06 "Registrar parecer", que grava uma conclusão técnica pronta.

**SU-05:**
- "Formalizar contrato" funciona antes da aprovação da Direção, cuja alçada vai "até R$ 300 mil" numa compra de R$ 360.905;
- "Emitir pedido" agenda emissão automática contra um contrato com tolerância "hipótese, não aceita";
- "Confirmar fornecedor" confirmou a carga da Fertisul, quando o único pedido "A confirmar" era o PC-094.

**Envios sem prévia:**
- SU-04 "Enviar COT-113" vai a 3 fornecedores sem mostrar os destinatários;
- GE-04 manda a remessa ao banco sem prévia do total.

**Alçada fora do lugar:**
- SU-08 "Registrar perda": quem pede escolhe o aprovador; a alçada deve sair do valor;
- GE-08: Ana registra "Autorizado pela Direção";
- CD-04: "Liberar O.S. (agrônomo)" é um checkbox livre; conferir a exigência de habilitação/RT.

**Publicações sem Desfazer (UX-04):** parcelamento (PL-06 publica mesmo "aguardando aprovação"), plano, ajuste, cenário.

### EX-34 Medida e evidência nunca vêm pré-preenchidas

- CA-03 "Evidência: Foto" marcada sem foto;
- LO-02det "Foto do lacre anexada" marcada;
- SU-07det "Quantidade medida" vem com 10, contra o próprio texto ("medida… não a declarada");
- PL-02 "Realizada" pré-marcada numa pendência vencida;
- MB-04 "Equipamento" pré-marcado, o que obriga a escolher máquina.

### EX-35 Listas filtradas por contexto e por organização

- **PT-06:** o fornecedor vê usuários da fazenda (Ana, Marcos, Rui, Paula) como responsáveis possíveis; é exposição entre organizações.
- **Opções que não cabem no contexto:**
  - CO-06 lista lotes de insumo (F26-02, D26-11) e métodos de MIP e solo;
  - CO-02 oferece plantadeira e pulverizador para colheita;
  - PL-06 oferece variedade de mamão para soja;
  - PL-05 oferece o Trator T1 bloqueado;
  - CA-01det oferece grãos como insumo;
  - AG-01 "Programar vistoria" oferece talhões de outra fazenda;
  - EST deixa ligar a NF 4533 ao pedido PC-096 (Mamão);
  - no portal, o tipo de documento oferece "Preventiva/Corretiva".

### EX-36 Integridade da irrigação

- **IR-01 "Conferir medição":** com −3,8 % de desvio (tolerância 3 %), a ação continua "Validar e encerrar"; deve virar "Aceitar com motivo" ou "Devolver".
- **MB-08:** aceita o término com 14,47 % da volta e emite o recibo "volta completa · 10,81 mm nos 80 ha"; antes do fim da volta, a ação deve ser "Término antecipado", com a área real.
- **IR-02:** o plano de 2 mm por passada fica abaixo do mínimo físico do pivô (6,7 mm a 100 %).
- **IR-03det:** começa às 20:02, dentro da ponta, sem aviso.

## Onda A · Fundação

### EX-01 Dados coerentes entre telas e dentro dos modais

Corrigir as contradições e criar um teste que compare contadores e valores da mesma entidade em todas as telas (aceite: 0 divergências).

- **Produção:** previsão de soja 26/27 68.180 sc (COLH) × 51.280 sc (GE-01, VE-05, GE-08); o IV soma safras (106.600 = 38.420 + 68.180); COLH mostra 0,48 e 0,73 t/ha no mesmo painel.
- **O.S.:**
  - OS × CA-01 divergem (OS-0430 "Falta máquina" × "Sem pendência"; "3 impedidas" × "2");
  - o painel da OS-0420 lista "MAP 11-52 250 kg/ha", e a O.S. completa e a REC-014 dizem "KCl 60 % 120 kg/ha";
  - a OS-0418 aparece como "Pivô 1" e como "gotejo T7";
  - "Trator 02 assume" × "aguarda PCP".
- **Manutenção e estoque:** MA "Ordens 0" com 4 OMs; PSUP "quarentena 1" × SU-03 "retidos 3"; "conflito de reserva 0" com uma linha "Reserva em conflito"; lote M26-05 × M26-07.
- **Compras:** SOL-2026-07 em três estados; "pedir até" diverge entre SU-01 e IC; MAP 62.500 × 79.500 kg; o contrato sai com 78,85 t, mas a proposta de R$ 360.905 era de 96,99 t.
- **Vendas:** recebíveis VE-04 × GE-05; PV-037 entregue mas ausente em GE-05; VD-2101 sem venda.
- **Irrigação:** "sem pendências" × "1 conflito"; Pivô 2 com 9,8 × 11,2 mm.
- **Cadastros e insumos:** PJ-3030 com tanque de 3.000 × 2.000 L; Inseticida B em L no CD-06 e em "1,0 kg/ha" na decisão; K do LAU-2043 em mg/dm³ × cmolc/dm³; "Pivô 22" × "PV22".
- **Planejamento:** "publicado na v4" com a v4 ainda em rascunho.

### EX-02 Uma entidade, uma listagem, um detalhe e um formulário

Consolidar com redirecionamento, como já feito em MA-01..05 → MA.

- **Colheita:** CO-01..05 e CO-07 → COLH, CARGA, BEN, PROD; CO-05det vira detalhe de BEN; CO-06/det vira seção de qualidade do lote.
- **Vendas:** VE-01, VE-02, VE-04, VE-05 → VEN e IV, com VE-04det como detalhe (hoje 3 formulários para a mesma venda); antes, migrar PV-026..029 e PV-032..034.
- **Logística:** LO-01..03 → EXPED com visões de agenda, fila e docas; LO-02det como detalhe.
- **Estoque:** SU-03 e SU-06..09 → EST com abas por entidade (hoje 2 formulários diferentes para receber a mesma NF: "Local" × "Depósito"; "Apta/Em quarentena" × "Inspeção").
- **Compras:** CMP, SU-01, SU-04, SU-05 e IC → listagem de solicitações por estado; detalhe com Demanda, Comparação, Pedido e Cargas; "quando comprar" vira coluna; SU-02 vai para configuração.
- **Safras:** SAF + PL-01 → uma listagem de safras, com PL-02, PL-03 e PL-06 como seções (hoje 2 formulários "Nova safra" diferentes e o parcelamento aparece duas vezes: PL-06 e "Dividir em parcelas" no SAF).
- **Demais:** OS + CA-01 → uma listagem de O.S.; IN-01 + IN-03 → Meu dia, com visão Lista | Semana; IR-01..03 → uma listagem por setor; MB-02 e a abertura do MB-03 deixam de repetir o MB-01.
- Antes de remover qualquer tela, confirmar no registro que ela é versão antiga, e não variante deliberada.

### EX-03 Vocabulário único (complementa UX-01)

- um verbo por ação ("Registrar apontamento", "Registrar avanço", "Apontar uso", "Apontar área");
- coluna "Próxima ação" em todas as listagens;
- ciclo do plano com no máximo 4 estados (hoje 7);
- siglas sem colisão (PV, OC, ROM × RM, COT × NEG, CT de frete × CT de venda);
- nenhum código interno nem nota interna na tela (CMD-06, DEC-09, RN-039, "VE-05 (oculto)… pergunta 4 ao proprietário");
- nome do menu = título = trilha, com raiz única.

### EX-04 Contexto Fazenda · Safra herdado em toda tela e em todo modal (P27)

- **Telas que abrem sem contexto:** IN-04, PAGR, PCOM, PMAN, PSUP, SAF, PA, AG-02..04, COLH, CMP, MB-07.
- **Modais:**
  - "Nova ordem" pede a safra;
  - "Programar vistoria", "Criar diagnóstico" e "Registrar laudo" ignoram o filtro;
  - "Programar pós" cai na AG-01 sem talhão, alvo nem data (deveria vir com 7 DAA);
  - SU-01 "Reprogramar" pega o primeiro item, não a linha clicada;
  - SU-01 "Abrir cotação" chega no CMP em "Nenhuma safra escolhida".
- A etapa "Escolha a safra" sai do CMP e do SAF.

### EX-05 A primária resolve o estado e nunca falha depois do clique (aplica UX-02)

- **Sem primária:** IN-04, AG-03, AG-05, AG-06, IN-02, PAGR, SAF, PL-05, CMP, IC, CO-04, BEN, PROD, IV, VE-03, GE-01, GE-06det, IR-03, IR-04, MB-02, MB-05, MB-07, PT-02, PT-04..07, além dos painéis de O.S. (OS-0418, OS-0420).
- **Primária que não resolve o estado:** SU-02, SU-03, SU-08, VEN, VE-01, VE-06, CO-02, CO-06, CD-07, CA-01x (falta "Confirmar substituto"), GE-08 (abre o portal do banco), ON-01, PT-02det ("Nada mudou desde a v1"), PT-04det ("Ainda não recebido").
- **Ativas que só recusam depois do clique** (devem aparecer desabilitadas com o motivo e a ação de cobrar o responsável):
  - GE-03 "Fechar competência", CA-02 "Encerrar", CA-04 "Confirmar recebimento";
  - SU-07 "Confirmar entrega" e "Separar FEFO", SU-02 "Publicar vigência", SU-09 "Submeter ajuste";
  - PL-01 "Autorizar execução" e "Encerrar período", AG-05 "Publicar", OS-0424-app "Retirar".
- Painel VIS-013 com dois botões verdes; CO-06det sem decisão neutra.

## Onda B · Entrada mínima

### EX-06 Turno por exceção (MB-03, MB-10; P24, P26, P29, P61)

- abre preenchido: hectares do dia previsto, horas = fim − início − pausas, consumo = dose × ha;
- "Fechar turno como previsto" em 1 toque; o operador toca só no valor que mudou;
- sinaliza quando GPS ou telemetria contradizem.
- **Medido:** 5 toques e 2 números obrigatórios; meta 2 e 0. Turno com diferença: cerca de 11 toques, 2 números e 1–2 textos; meta 3 e 1.

### EX-07 Paradas com causa

- MB-08 e CA-01det já pausam com motivo, mas sem duração; MB-03 pausa sem motivo;
- reusar a lista de causas que já existe, com início e fim registrados sozinhos;
- a ocorrência fica ligada à O.S. e à máquina, e o sistema propõe "Reprogramar saldo".
- **Resultado:** ha/h real, eficiência de campo e Pareto de paradas. Estimativa: 5,6 ha/h contra 28,8 ha/h teóricos do PJ-3030, número que não aparece em nenhuma tela.

### EX-08 Condições de aplicação e calibração (OS-0424-app, MB-02det, MB-03, painel VIS-013, CA-01det; P43)

- limites de vento, temperatura, UR e Delta T, mais reentrada, na ficha e na decisão;
- "Iniciar turno" confere clima e checklist, com alerta ou bloqueio configurável e exceção liberada pelo RT;
- "Aumentar dose" mostra o limite de bula;
- conferência de calibração: vazão por bico × taxa (estimativa: −11 % na OS-0424, supondo bicos a 50 cm).

### EX-09 Abastecer com 1 número (MB-09)

- horímetro vem da telemetria ou do turno; tanque e lote vêm do último uso;
- sai o segundo botão com a mesma validação.
- **Medido:** 5 toques, 2 números e 1 chip.

### EX-10 Conferência por exceção (CA-02 e "Conferir dia" da OS; P39)

- hoje "Conferidos 2 de 2" aceita junto o turno com "horas acima do previsto";
- conferir em massa só o que está dentro da tolerância e destacar o divergente, com "Aceitar com motivo" ou "Devolver";
- "Liberar OS-0418" e o roteiro saem da CA-02.

### EX-11 Recebimento de NF (SU-06/EST; UX-09)

- "Ler documento/QR" abre o mesmo formulário e não lê nada: deve ler chave/XML e preencher pedido, NF, lote, validade e preço;
- "Confere com a NF" como primária, com a quantidade da NF quando estiver dentro da tolerância de +5 %;
- apta e quarentena derivadas da inspeção;
- NF e quantidade na nota somente leitura.
- **Medido:** SU-06 com 2 números (conferida, validade); EST com 4 números mais o motivo da quarentena; meta 0 ou 1.

### EX-12 Romaneio de entrada (CARGA; P09, P28, P29)

- estados Pesagem → Classificar → Fechar ("Fechar" não existe hoje);
- ticket e bruto vêm da balança; tara vem do cadastro do veículo (hoje "sem valor anterior");
- líquido corrigido ao vivo pela tabela do armazém (hoje "Calculado ao salvar"; CG-0988: 9.840 → cerca de 9.470 kg);
- umidade, impureza e classe como campos numéricos com unidade (no CO-03 são um texto livre só).
- **Medido no fluxo novo:** cerca de 9 toques e 3 números, mais 2 no grão; meta cerca de 4 toques e 2 números.

### EX-13 Laudo de solo (AG-02)

- o modal tem 17 campos (7 digitados) e não tem pH, P e MO;
- V % e CTC não são calculados;
- o "OCR" anunciado é um campo de texto com o nome do PDF.
- **Correção:** importar o arquivo do laboratório com prévia, unidade padrão (mostrando a digitada como origem) e V %/CTC ao vivo; ler PDF depende de IA.

### EX-14 Nascer do anterior (SAF, PL-01, PA; P13, P15, P25)

- nem "Criar safra" nem "Editar" oferecem cópia: incluir "Copiar cultivos e planos de 2025/26";
- nome derivado das datas; período com seletor de data;
- sai o campo "Estado" editável à mão;
- "Aplicar modelo" e "Gerar sugestões pelas análises" saem do ⋯ do PL-02 e vão para o lugar da criação.
- **Ganho:** de 7 campos para 2 escolhas no cabeçalho; a grade vira revisão das diferenças.

### EX-15 MIP: ajustes no painel que já funciona (VIS-013)

- um só botão verde;
- origem da dose ("mínimo da bula" ou "protocolo MIP Feijão v2");
- regra de rotação aplicada a todo grupo repetido (hoje marca o IRAC 1B, mas não o IRAC 23 de 25/08);
- reentrada e condições de aplicação;
- visão Mapa de calor na AG-01;
- "Programar pós" já preenchido.
- A aprovação individual fica.

### EX-16 Rascunhos automáticos em suprimentos e manutenção (P34, P44)

- a OM preventiva já é gerada do plano: falta vir com a data sugerida ("Janela: 24/09") e com a compra da peça já reservada para a OM;
- falta firme ou mínimo/máximo gera rascunho de solicitação, e o "Comprar agora" do IC também;
- achado crítico nasce como OM em rascunho;
- O.S. concluída sugere a devolução;
- FEFO vem pré-selecionado.

### EX-17 Um lançamento produz todos os efeitos (P25, P41)

A conciliação bancária e a proposta aceita virando pedido já existem. Falta:
- venda com unidade e safra na quantidade (causa raiz do "saca a conferir");
- preço do compromisso em campo próprio (hoje vai em "Condições", texto livre);
- entrega baixa o contrato e cria o título a receber; medição de frete cria o título a pagar (não verificável no protótipo).

### EX-37 Formulários enxutos

- **Primária com verbo e objeto:** 34 de 64 formulários usam "Salvar"; ON-01det diz "Validar" e grava; VE-04det diz "Salvar" e envia ao cliente.
- **Obrigatórios marcados:** nenhum está marcado nos 15 formulários de agronomia e cadastros.
- **3 a 5 campos visíveis e "Mais opções":** CD-04 tem 23 campos (separar Operação de Permissões, cerca de 6 visíveis); CD-03 tem 12; CA-02 "Reabrir saldo", 7; CA-03, 7 (cerca de 3 bastam).
- **Lista no lugar de texto livre:** motivo, causa, local, evidência como foto, alteração de política com mínimo/máximo e unidade, "Compromisso" do IN-03 como busca de registro, evidências do diagnóstico, carga e horário do LO-01.
- **Derivar em vez de digitar:**
  - razão social pelo CNPJ;
  - colhido = soma das cargas (CO-02det);
  - cenário a partir da V2 (GE-02);
  - pedido e lote vindos da linha (VE-06);
  - itens da versão vigente na requisição (CA-04);
  - R$/h do CD-03 e do CD-04 no CD-08, com "Aplicar 19,8 ha/h";
  - massa da saca vinda do contrato (PCOM);
  - área do talhão pelo polígono ou KML (CD-01);
  - data de hoje nos registros do dia.

## Onda C · Gestão que gera resultado

### EX-18 Janela agronômica como eixo do PCP (PL-02..04, PAGR)

- folga da janela por operação e programação ordenada por folga × prioridade;
- capacidade por semana (hoje por mês);
- "% de área dentro da janela" no painel;
- término previsto pelo ha/h real (UX-07);
- reprogramação sugerida após chuva ou quebra.

### EX-19 Custo por saca e margem por hectare por talhão (PL-01, PA, GE-01, PCOM; P20, P45, P59)

- o espaço "CUSTO R$/T" no painel do talhão e o custo por talhão no GE-03 já existem: falta ligar os dois;
- simulação entre planos (PA: R$ 2.099,90 × R$ 1.383,50/ha);
- GE-01 desce até talhão, romaneio, contrato e custo, marcando o que é parcial.

### EX-20 Previsão móvel única de produção

Hoje só o mamão é previsto por contagem, e a soja segue "Prevista (v1)". Proposta: uma previsão só (colhido + saldo × produtividade amostrada), alimentando comercial, garantias e caixa.

### EX-21 Política de comercialização (IV, VEN)

- % vendido × custo coberto por safra;
- alerta de preço que considera o custo por saca;
- gatilho que gera rascunho de oferta; posições de trava e basis.
- Hoje 61 % da soja está sem preço, com margem exposta estimada em R$ 484 mil.

### EX-22 Caixa de 13 semanas (GE-04)

Montado a partir de títulos, contratos, plano e previsão.

### EX-23 Suprimentos com indicadores de resultado

- prazo de entrega por fornecedor no "pedir até";
- % da demanda coberta antes da janela; ruptura que parou O.S.;
- economia realizada; validade e "vencendo" na lista;
- capital sem demanda em 90 dias;
- inventário cíclico pela curva ABC (hoje o escopo da contagem é manual).

### EX-24 PCM com indicadores de resultado (MA)

- disponibilidade da frota na janela;
- MTBF/MTTR, % preventiva, backlog em horas, custo por hora;
- kit de peças por plano.

### EX-25 Irrigação de valor

- chuva medida e prevista no balanço (o cadastro aceita sensor de chuva, mas não há nenhum);
- início fora da ponta, com o custo da ponta mostrado nas janelas e respeitando a outorga;
- alerta de pressão e vazão.

### EX-26 Painéis por exceção (PAGR, PMAN, PSUP, IN-04; P60)

- todo número abre a lista filtrada;
- sem somas repetidas e sem linhas "nada a fazer agora";
- cerca de 6 indicadores de resultado com meta e tendência.

### EX-27 Talhão como centro (CD-01det)

Seções Operações, Monitoramento, Solo, Custo e margem e Linha do tempo, reaproveitando as listagens filtradas.

### EX-28 Insumo ligado ao registro do Agrofit (CD-06 → AG-07/AG-04; P36, P43)

- o formulário do item ganha registro, concentração, ingrediente ativo, mecanismo de ação, carência e dose de bula (hoje não tem campo de registro);
- seletor mostra registro e concentração (evita lançar 867 g/L como 806);
- unidade única do item (Inseticida B em L × kg/ha).

### EX-29 Cadastros alimentados pelo realizado (CD-03, CD-08)

- ha/h e R$/h recalculados dos apontamentos;
- "Aplicar" na revisão sugerida;
- conjunto escolhido da aba Conjuntos.

### EX-30 Plataforma

- escopo por fazenda (já pedido no convite do ON-01) também no CF-01, mais alçadas de pagamento, crédito a cliente e liberação de lote;
- recibos de comando (QL-1148, CMD-5522) na trilha do CF-04, com antes → depois;
- rótulo "Importar 9 talhões e 6 máquinas" no lugar de "Validar";
- tirar "IA 200 interações" do CF-05, ON-01 e BO-01.

### EX-31 Fila e entrada (IN-01, IN-02; UX-05, UX-06)

- decidir no lugar, em painel lateral (hoje "Decidir" navega para SU-09 e as ações do Meu dia saem da tela);
- idade da pendência e prioridade por impacto (ha parados × dias de janela);
- visões salvas.

## Decisões do proprietário pedidas pela análise (não implantar sem aceite registrado)

- **EX-32:** confirmar que a correção é tirar o lote das O.S. com produto (entendimento da decisão de 16/10; só muda se o proprietário decidir o contrário).
- **Irrigação só com água:** IR-01 e IN-03 dizem "libera ao programar, sem aprovação (água sem produto)", e o MB-08x diz "encerrada automaticamente". Confirmar se ficam fora da aprovação agronômica individual (DEC-2609-10 já registra a exceção).
- **EX-10:** aceite automático do turno dentro da tolerância, ou conferência humana de tudo.
- **EX-08:** clima como alerta ou bloqueio, e quem libera a exceção.
- **Alçadas por valor:** perda, crédito a cliente, frete, liberação de lote e pagamento de manutenção (hoje uma fatura de oficina cai na alçada de suprimentos); e "Aprovar e emitir pedido" numa só ação abaixo da alçada.
- **Automações com IA** (foto de praga, leitura de PDF, produtividade por imagem, falhas recorrentes, comprar × esperar): desligadas até a estimativa de custo (DEC-1610-11).

## Entrega pedida

- tabela EX-01..EX-37: validação e evidência · decisão Claude · decisão Codex · decisão final · onda · ganho medido (antes → depois) · esforço · risco;
- o que a análise errou ou deixou de fora, segundo o Codex, e como foi tratado;
- plano das ondas, com fatias, autoria e revisão;
- decisões pendentes do proprietário, cada uma com recomendação e impacto;
- três listas curtas, com motivo: aplicado, deixado de fora, cortado;
- suposições e pendências, cada uma com o gatilho de retomada.
