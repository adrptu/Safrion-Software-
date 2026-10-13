# Parecer: regras de negócio e boas práticas no protótipo

**Para:** Adrianus · **De:** Claude · **Data:** 09/10/2026
**Pedido (09/10):** "Confira se todas as regras de negócio e melhores práticas de gestão agronômica, agrícola, suprimentos, PCM etc. estão incorporados da melhor forma possível em cada menu, submenu, tela, botão, campo, tabela etc. E apenas me dê seu parecer sem mudar nada ainda."
**Objeto:** protótipo publicado v53 (branch única `claude/prototipo-v44`, commit `cdc185f`). Depois da v53 entrou só a trava de área com lavoura perene antiga (`9fb09a5`), que mexe apenas na ocupação dos talhões.
**Contrato:** PRD v3.11. Ela já está na `main` (PR #48, merge `266a682`) e o AGENTS.md já a cita como vigente. O pedido partia da premissa de que ainda não estava integrada; essa premissa está desatualizada.
**Nada foi alterado.** Foi só leitura e simulação com dados sintéticos fora do repositório.

---

## 1. Veredito geral

O protótipo tem as regras centrais bem desenhadas. Em vários pontos elas são melhores que o comum no mercado:
- toda O.S. agrícola passa pela aprovação do agrônomo, e aprovar não libera;
- registro, dose da bula e carência são conferidos por uma regra só;
- o material só sai para O.S. liberada, e a sobra precisa voltar antes de encerrar;
- um apontamento repetido não soma duas vezes;
- a colheita respeita a carência e é rastreada do talhão até o pedido;
- a irrigação só com água dispensa o agrônomo, e a fertirrigação volta para ele.

As fraquezas estão em dois lugares:
- **Nas passagens entre módulos.** O cadastro não alimenta os processos. O bloqueio da manutenção não segura a O.S. nem a irrigação. A compra emitida não chega ao recebimento. A ocorrência do campo não chega ao escritório.
- **Nos controles de segundo nível.** Lote vencido e ordem de validade, reentrada no talhão, autoria do receituário fora da O.S. e custo realizado sem as horas.

**Gravidade.** Não encontrei nenhum S1. Encontrei **38 S2**:
- **9 já estão em correção** numa frente;
- **29 não têm frente em execução, ou têm só cobertura parcial**. Juntando os repetidos, são 21 assuntos.

Dois pontos que hoje são S3 virariam S1 se fossem levados assim ao software real:
- a exceção da irrigação só com água é decidida pelo nome da operação;
- o CREA não é conferido no momento de aprovar.

---

## 2. Quadro por módulo

| Módulo | Nota | O que está bem | Principais lacunas sem frente | Já em correção |
|---|---|---|---|---|
| **Cadastros e Mapa** | Bom, com lacunas | Parceiro único por CPF/CNPJ com papéis. Talhão com área cultivável, geometria versionada e travas de soma. Unidade-base travada quando há saldo. Estrutura gerencial por dimensões. Mapa com área geodésica e importação com prévia. | Os cadastros salvos não chegam aos processos. Importar ou desenhar no Mapa grava sem as conferências do talhão. Defensivo sem registro nem composição. Operação sem "família". Calibração e habilitação NR por atividade. | Colunas (sp-tabr). CREA na concessão do papel (sp-conf). Garantia de PRNT/K₂O (sp-solo). |
| **Agronomia** (MIP, planos, Agrofit, solo) | Bom, com lacunas | Base Agrofit real, com a idade à vista. Rotação por modo de ação. LMR por destino. MIP com média só dos pontos válidos e nível de controle por estádio. Plano versionado, com as diferenças mostradas antes de publicar. | Receituário do MIP gravado em nome da agrônoma (S2). Unidade trocada kg × L (S2). Plano sem conferir bula e alvo (S2). Reentrada (S2). Publicar plano sem papel nem autor. | AG-07 só para consulta e alvo levado à O.S. (sp-ctl5). Análise de solo como sugestão (sp-solo). |
| **Planejar safra** | Bom, com lacunas | Ocupação do talhão no tempo, com motivo. Parcelas sobre a área cultivável. Demanda datada, com memória do cálculo. Capacidade com turnos e sem custo zero. Envio para cotação sem duplicar. | Variedade digitada em texto livre (S2). Versão do plano não fica gravada no cultivo (S2). Safra sem aprovação, orçamento e encerramento (S2). Plantio sugerido no passado some da compra (S2). | Demanda por fazenda e sem duplicar (sp-ctl4). Trava de área com perene (já integrada). Capacidade igual entre safras (sp-safc02). |
| **Ordem de Serviço e app de campo** | Forte no essencial; lacunas no estoque e na calda | 5 fases fixas. Aprovação e liberação gravadas em separado. Trava legal antes de gravar. Apontamento sem duplicar e funcionando sem sinal. Encerrar só com custódia zero. | Reserva que nunca volta ao estoque (S2). Lote vencido e ordem de validade (S2). Mistura incompleta pode iniciar (S2). Ficha de calda com valores fixos e diferentes entre web e app (S2). Reentrada (S2). Ocorrências sem destino (S2). | Aprovar e liberar por pessoas diferentes (sp-conf). Divergência de dose no turno (sp-dom). |
| **Irrigação** | Bom, com lacunas | Tarefa única por setor. Água sem agrônomo e fertirrigação com agrônomo. Contas da lâmina corretas. Passagem parcial do pivô. Sem leitura não há crédito no balanço. Outorga vencida trava. | Bloqueio da manutenção não impede iniciar (S2). Volume "medido" inventado em pivô sem hidrômetro (S2). Vazão diferente da do cadastro (S2). Percentímetro, CAD e Kc. Energia. | Outorga com fonte única (sp-ctl5). CAD como referência (sp-solo). Colunas (sp-tabr). |
| **Suprimentos** (Compra e Estoque) | Bom, com lacunas; o mais exposto | Custódia que fecha a conta. Recebimento com travas. Quarentena só sai com laudo. Inventário cego. Cotação só a fornecedor homologado. Menor custo total que chega antes da falta. Alçada pelo valor total. | Lote vencido e ordem de validade (S2). Produto errado entra como o comprado (S2). Pedido emitido não chega ao recebimento (S2, só especificado). Aprovação gravada em nome da Ana (S2, só especificado). Embalagens vazias, transferência, validade da reserva. | Entrega só da reserva própria, laudo por parcela, contagem, unidade (sp-sup). Compra sem pedir de novo o já entregue (sp-ctl4). |
| **Manutenção (PCM)** | Fraco no publicado; bom na frente | Vence pelo que chegar primeiro (h, km ou dias). Uma OM por ciclo. Plano versionado. Contador com controle de qualidade. Checklist nunca pré-marcado. Concluir a OM não libera a máquina. | Bloqueio não segura a O.S. (S2). Peças fora do Estoque e corretiva sem peça (S2). Diesel lançado em dobro e consumo L/h errado (S2; o L/h é defeito da própria frente). Criticidade calculada pelo atraso. Checklist antes do uso. | Triagem, "apto" só com teste, números calculados e menu único (sp-pcm, feito e não juntado). 1b/1c só especificados. |
| **Produção** (colheita, cargas, estoque de produto) | Forte | Carência lida ao vivo no lote. Carga só nasce de O.S. aprovada. Produção só de carga recebida. Contas exatas. Previsão versionada. Rastreio do talhão ao pedido. | Balança sem conferência de valor absurdo. Previsão de grão = meta × área. Liberar lote, pesar e estornar sem conferir o papel. Estoque em terceiros. | Saca de 50 × 60 kg (sp-com). Café "sc a apurar" (sp-dom). Packing do mamão (sp-ben). Comercial (sp-com). |
| **Gestão, custos e Configurações** | Fraco (oculto e com números fixos), salvo Estrutura gerencial e Assinatura | Estrutura gerencial por dimensões. Mapa › Custos com o denominador declarado e orçamento flexível. Assinatura com a área lida do cadastro. | Custo realizado sem as horas (S2). Sem base aprovada do orçamento. Custo da O.S. contado em dobro. "Restaurar" e "Entrar como" do índice enganam. Sem "Relatar problema". Custo-hora de pessoa visível a todos. | Configurações lendo as alçadas e a trilha reais; assinatura em nome de quem age (sp-conf). |
| **Entre módulos** | Fraco | Coleta do MIP no app ligada de verdade. Fertirrigação sem lacuna. Encerrar exige custódia zero. | Ocorrências do campo sem destino (S2). Sobra de calda devolvida como produto puro. Cadastros paralelos. Custo da terra. Mão de obra sem equipe. | Parcial: ocorrência de equipamento vira achado da manutenção (sp-pcm). |

---

## 3. Lacunas não cobertas, por prioridade

S1: nenhuma.

### 3.1 S2 sem frente em execução (ou só com cobertura parcial)

**1. Receituário do MIP gravado em nome da agrônoma** (AGRO-1)
- **Onde:** Agrícola › Pragas e doenças › vistoria › Decidir controle › "Emitir receituário e gerar O.S." e "Registrar e programar próxima".
- **Regra:** decide e assina o agrônomo ou responsável técnico (PRD AG-04, AGR-031, AG-07). Nenhum registro grava o nome de quem não agiu.
- **Dano:** qualquer perfil (testado com o do PCP) emite o receituário e escolhe produto e dose, e o sistema grava como decisão da Ana. A execução ainda depende da liberação pelo agrônomo; por isso é S2, e não S1.
- **Fazer:** só o papel de agrônomo emite e decide. Gravar quem agiu. Para os demais perfis, botão desligado com o motivo.

**2. Reentrada no talhão tratado** (AGRO-4, OS-6)
- **Onde:** ficha do produto, decisão do MIP, receituário e liberação ou início de O.S. manual no talhão tratado, inclusive no app.
- **Regra:** RN-016 (restrição obrigatória, sem justificativa) e AGENTS §4 (trava por lei).
- **Dano:** a equipe pode ser mandada ao talhão dentro do intervalo de reentrada (tratos culturais, erradicação, colheita manual de mamão) sem nenhum aviso. Há risco de intoxicação e de infração. O dado já está na base Agrofit (44 produtos), mas nenhuma regra o usa.
- **Fazer:** calcular "reentrada até dd/mm hh" a partir da aplicação apontada, com o mesmo cálculo da carência. Impedir liberar ou iniciar O.S. com entrada de pessoas antes desse prazo. Mostrar na ficha do operador e no Mapa.

**3. Plano agronômico e ajuste por talhão sem conferir a bula** (AGRO-3; inclui SAF-15 e AGRO-11)
- **Onde:** Agrícola › Planos agronômicos › atividade › insumos (dose/ha, "Incluir insumo") › Publicar; Planejar safra › Ajustar insumos.
- **Regra:** AGR-027 e AGR-028 (uso permitido, dose, alvo, carência, reentrada e limite de aplicações em todo plano).
- **Dano:** a demanda e a compra saem com dose e unidade fora da bula. Exemplo: Inseticida B planejado a 0,30 L/ha, quando a bula é de 0,8 a 1,0 kg/ha (produto em pó), e numa fase cujo alvo não tem registro. A O.S. só trava na liberação, dentro da janela e com a compra já feita.
- **Fazer:** alvo em cada item de defensivo. A mesma conferência legal da O.S. aparece como selo na linha do plano: aviso no plano, trava só onde a O.S. travaria. O catálogo do plano vem do cadastro de produtos.
- **Cobertura parcial:** sp-ctl5 já leva o alvo pelo "Usar na O.S.".

**4. Unidade trocada entre a bula e o lote** (AGRO-2)
- **Onde:** Pragas e doenças › Decidir controle › "Estoque cobre"; O.S. gerada; reserva.
- **Dano:** 50 kg reservados num lote controlado em litros. Saldo e custo ficam errados. Reproduzido.
- **Fazer:** ligar o produto da fazenda ao registro, com formulação e unidade. A emissão e a reserva travam quando a unidade da dose for diferente da do lote, com a mensagem "corrija o cadastro" e sem conversão automática.

**5. Variedade digitada em texto livre** (SAF-1)
- **Onde:** Planejar safra › Talhões e cultivos › Planejar ou Dividir › Variedade → Demanda › Sementes.
- **Regra:** PRD 39.1–39.2 (variedade escolhida do cadastro de cultivares) e catálogo escolhido por busca.
- **Dano:** digitar "58W" em vez de "58 W" criou uma semente nova a comprar, cerca de 15,5 t (≈ R$ 147 mil ao preço do plano), e deixou sobrar a semente certa em estoque. Visto na tela.
- **Fazer:** escolher a variedade no cadastro, filtrado pela cultura, com "Cadastrar variedade" no próprio painel. A semente fica ligada à cultivar, não ao texto.

**6. A versão do plano usada em cada cultivo não fica gravada** (SAF-2, AGRO-6)
- **Onde:** Planejar safra › colunas Plano e Versão; Planos agronômicos › "decida a adoção em Planejar safra".
- **Regra:** PRD 40.3 (o cultivo guarda a versão; versão nova não muda nada em silêncio).
- **Dano:** a safra 2025/26, já encerrada, mostra as versões v6, v6 e v4, publicadas depois do plantio. No software real, publicar uma versão nova mudaria doses, demanda e compras de todas as safras abertas sem decisão de ninguém. O link prometido leva a uma tela sem essa decisão.
- **Fazer:** gravar plano e versão no cultivo. Quando houver versão nova, mostrar "v6 · v7 disponível" com "Revisar atualização".
- **Cobertura:** a frente de navegação (sp-nav) deixa este ponto expressamente fora.

**7. Safra sem aprovação de plano, orçamento e encerramento** (SAF-3; ver também GES-4)
- **Onde:** Planejar safra › Escolha a safra › Estado (livre: "Rascunho" ou "Em planejamento"). A etapa 4 não tem "Publicar plano", "Autorizar execução" nem "Encerrar safra".
- **Regra:** PRD 8.1 (estados da safra), CMD-02/03/04 (publicar, autorizar orçamento, autorizar execução), RN-031 (base aprovada × revisão × realizado).
- **Dano:** sem base aprovada, não existe previsto × realizado. A O.S. é liberada sem orçamento autorizado. Mudanças feitas depois de a O.S. sair ficam sem rastro. Não é S1 porque cada O.S. continua exigindo o agrônomo.
- **Fazer:** adotar os estados do 8.1. "Publicar plano" congela a versão. A gerência autoriza a execução, e a liberação da O.S. confere essa autorização. "Encerrar safra" com as pendências destinadas.
- **Cobertura parcial:** o CONTROLE-02, pendente e não iniciado, cobre só a versão de referência.

**8. Operação com data já passada some da compra** (SAF-4; ver também SAF-7)
- **Onde:** Planejar safra › Demanda › "Já realizado" e "Necessidade líquida"; painel Planejar › plantio sugerido.
- **Dano:** o sistema sugeriu plantio em 21/09, com "hoje" em 23/09. Em seguida, MAP 51 t, glifosato 408 L e semente 10,6 t apareceram como "já realizados", sem nenhuma O.S., e saíram da compra. Visto na tela.
- **Fazer:** o sp-ctl4 deixa de chamar isso de "realizado", mas o uso continua fora da compra. Além disso, operação vencida sem O.S. deve aparecer como "vencida · decidir" e continuar na demanda. O plantio sugerido nunca deve ser anterior a hoje.

**9. Reserva que nunca volta ao estoque** (OS-1)
- **Onde:** O.S. › "Dispensar saldo", "Enviar para conferência" e "Conferir e encerrar"; reflexo em Estoque › saldos.
- **Regra:** PRD 42.5 (nenhuma reserva ativa ao encerrar) e CMD-47.
- **Dano:** depois do ciclo completo da OS-0430, ficam reservados para sempre 20 L de glifosato, 10 L de 2,4-D e 5 L de óleo. O disponível fica menor, surge "falta insumo" falsa em outras O.S., e Suprimentos compra o que já tem. Reproduzido.
- **Fazer:** ao dispensar e ao entrar em conferência, devolver ao disponível a reserva não entregue. Recusar o encerramento com reserva ativa.

**10. Lote vencido, ordem de validade e vários lotes** (OS-2, EST-1, EST-3)
- **Onde:** O.S. › Liberar; Estoque › Confira saldos (Disponível ao lado do selo "Vencido"); Entregue por O.S. › Lote reservado.
- **Regra:** RN-015, 42.1, CMD-16, RN-011. Prática de almoxarifado: sai primeiro o que vence primeiro.
- **Dano:**
  - defensivo vencido na prateleira é reservado e entregue (reproduzido);
  - com dois lotes que juntos cobrem a ordem, a liberação é recusada por "saldo insuficiente". Na operação real cada nota vira um lote, então isso trava o dia a dia;
  - o lote que vence primeiro fica parado;
  - uma ordem da Lagoa Grande reserva insumo do almoxarifado da Santa Rita.
  Na demonstração isso ainda não aparece, porque há um lote por produto e nenhum vencido.
- **Fazer:** lote elegível é o lote apto, da fazenda ou local da ordem e válido até o fim da janela. Reservar pela validade mais próxima, repartindo entre lotes. O almoxarife pode trocar por outro lote apto, com registro.

**11. Produto errado recebido entra como o comprado** (EST-2)
- **Onde:** Estoque › Confira recebimentos › Recebimento › Divergência "Item diferente do pedido".
- **Regra:** SUBST-07 e SUBST-14 (v3.10/3.11) e RF-SUP-007.
- **Dano:** o produto real entra com o nome e o lote do produto comprado, fica disponível e pode ser entregue à O.S. que receitou outro produto.
- **Fazer:** essa divergência obriga a bloquear tudo, registrar o produto real ou recusar a entrada, e abre a divergência para o comprador.

**12. Mistura incompleta pode começar** (OS-4)
- **Onde:** O.S. › painel da OS-0421 › Insumos (adjuvante); app › Iniciar turno.
- **Regra:** PRD 42.2 e ESTOS-03 (não aplicar mistura incompleta).
- **Dano:** o adjuvante aprovado não está na requisição, e o sistema deixa iniciar. O painel mostra "usado 47,5 L" e "Entregue ao operador" sem que isso tenha acontecido. Web e app se contradizem. Reproduzido.
- **Fazer:** o início confere todos os componentes da versão aprovada. Componente sem requisição bloqueia, com "quem resolve". "Usado" só aparece depois de baixa real.

**13. Ficha de calda com tanque e volume fixos, diferentes na web e no app** (OS-5)
- **Onde:** O.S. › Retirada e fichas de execução; app › Preparo por tanque; ficha do caldeiro.
- **Regra:** PRD 41.3 (o volume de aplicação faz parte da versão aprovada), 41.5 e 41.6.
- **Dano:** a web diz 3.000 L e 100 L/ha, com fungicida e adjuvante. O app diz 2.000 L e 120 L/ha, com 8,3 L de fungicida e sem adjuvante. Preparar pelo app num pulverizador regulado para 100 L/ha dá cerca de 17 % menos dose, e sem adjuvante. O percentual é inferido por cálculo.
- **Fazer:** o volume de calda (L/ha) vira campo da versão aprovada pelo agrônomo. A capacidade útil vem do cadastro ou da calibração. Uma conta só para o painel, o app e a ficha impressa.

**14. Ocorrência do campo não chega a ninguém e a O.S. encerra** (GAP-1)
- **Onde:** app › Registrar ocorrência → O.S. › Conferir e encerrar.
- **Regra:** RF-OPS-006, FO-08 e CA-03 (encaminhar pela causa, com dono; encerrar só com a ocorrência destinada).
- **Dano:** "Ajudante com tontura após o preparo da calda" e "deriva para a lavoura do vizinho" foram registradas, e a O.S. encerrou como conforme. Nenhuma tela do escritório mostra as ocorrências. Reproduzido, e conferido de novo no código nesta consolidação.
- **Fazer:** gravidade e destino pelo tipo:
  - praga → vistoria;
  - falha de aplicação → agrônomo;
  - clima → PCP;
  - segurança → gestor, com "Pausar ordem".
  Mostrar as ocorrências abertas no painel da O.S. e só encerrar com todas destinadas.
- **Cobertura parcial:** no sp-pcm, "Equipamento" vira achado da manutenção.

**15. Máquina ou bomba bloqueada pela manutenção não segura a O.S. nem a irrigação** (MAN-1, IR-1)
- **Onde:** Manutenção › Bloquear ativo → O.S. (Liberar, Iniciar turno); Irrigação › ordem › "Iniciar irrigação".
- **Regra:** RF-AST-001, CMD-18, 47.8, AGUA-08 e CMD-07.
- **Dano:**
  - ao bloquear o pulverizador PJ-3030, a tela diz "as O.S. ficam impedidas", mas as três O.S. que usam a máquina seguem normais;
  - a ordem da Bomba do Pivô 2, em corretiva na manutenção, é liberada, e "Iniciar" é aceito.
  Há risco a pessoas e ao equipamento, e o PCM fica com uma garantia falsa. Não é S1 porque o sistema não liga máquina.
- **Fazer:** uma regra única "a máquina impede o trabalho" (bloqueada, ou restrita de forma incompatível), conferida ao liberar e ao iniciar na O.S., no turno e na irrigação. A irrigação passa a ler a condição e as paradas da manutenção. Até lá, a mensagem lista as O.S. afetadas sem afirmar que foram impedidas.
- **Cobertura parcial:** sp-pcm resolve só o trator T1.

**16. Irrigação: volume "medido" inventado** (IR-2)
- **Onde:** Irrigação › ordem › Confirmar término › "Leitura do hidrômetro", que já vem preenchida.
- **Regra:** PRD 41.8 e RF-WAT-004 (falta de dado não vira aplicação prevista registrada como real).
- **Dano:** em pivô sem medidor (toda a Lagoa Grande), o sistema preenche 98,5 % do previsto como se fosse "telemetria", encerra sozinho como "conferida" e credita no balanço. A próxima lâmina sai errada, e uma estimativa fica gravada como medição. Reproduzido.
- **Fazer:** cada setor ligado à sua fonte de volume (hidrômetro ou "sem medidor"). Sem medidor, "estimado por tempo × vazão", marcado como estimado. Conferência automática só com medidor cadastrado.

**17. Irrigação: vazão diferente da do cadastro** (IR-3; parte do GAP-3)
- **Onde:** Irrigação › setor › Equipamento; Cadastros › Máquinas › Bomba do Pivô 1/2 › Vazão; "Cadastrar setores".
- **Dano:** a mesma bomba tem duas vazões:

  | Bomba | No cadastro | Na irrigação |
  |---|---|---|
  | Pivô 1 | 300 m³/h | 540 m³/h |
  | Pivô 2 | 340 m³/h | 598 m³/h |
  | Gotejo T7 | 45 m³/h | 839 m³/h |

  Corrigir no cadastro não muda duração, janela, conflito de bomba nem a conferência da outorga. O campo do talhão diz que "o balanço usa este vínculo", e não usa.
- **Fazer:** um cadastro de setor ou pivô ligado ao talhão, à bomba, à captação, ao medidor e à sonda, com vazão efetiva versionada (data do ensaio). A irrigação lê esse cadastro.

**18. Oficina: peças fora do estoque e corretiva sem peça** (MAN-4, MAN-5)
- **Onde:** Manutenção › ordem › Peças; Estoque.
- **Regra:** RF-AST-004 (ordem única com peças), 47.4 e cap. 42. O DECISIONS (item 12) já registra isso como S2.
- **Dano:** filtro e óleo saem para a oficina sem movimento no Estoque. A corretiva, onde está o maior gasto, nasce sem peça e não tem como incluir. O custo por máquina fica subestimado, e há compra duplicada ou falta na preventiva.
- **Fazer:** manter a sequência SUP-2a → SUP-2b → PCM-1b (só especificada). Logo depois, antecipar "Incluir peça" e "Peça retirada".

**19. Diesel: abastecimento lançado em dobro e consumo errado** (MAN-8, MAN-9)
- **Onde:** Manutenção › Abastecimentos (web) e app › Registrar abastecimento; coluna Consumo e alerta de desvio.
- **Regra:** CAL-07; CONC-09/11 (v3.10/3.11).
- **Dano:**
  - o mesmo abastecimento de 200 L lançado pelo Otávio e pelo Zé vira dois lançamentos (640 L no ativo);
  - com um complemento entre dois tanques cheios, o consumo sai pela metade (8,2 L/h em vez de 17,3), o alerta acusa um subconsumo falso, e um desvio de diesel fica escondido.
  O segundo ponto é defeito da própria frente da manutenção.
- **Fazer:** ligar o segundo registro do mesmo fato ao primeiro ("Já registrado por…"); volumes diferentes vão para conferência. O consumo soma todos os abastecimentos entre dois tanques cheios. Acrescentar um teste com complemento.

**20. Compra: pedido não chega ao recebimento, e a aprovação é gravada em nome da Ana** (CMP-1, CMP-2, GES-2)
- **Onde:** Suprimentos › Compra › Aprove a compra e Acompanhe a entrega; Estoque › Registrar recebimento › Pedido.
- **Regra:** RF-SUP-006/007; PRD 2.1 (ninguém amplia o próprio acesso; a decisão é por papel e valor).
- **Dano:**
  - o pedido aprovado (PC-101 em diante) não aparece para receber, e o acompanhamento nunca mostra recebido nem atraso;
  - com o perfil do almoxarife ou do PCP escolhido, uma compra de até R$ 300 mil é gravada como aprovada pela Ana;
  - acima da alçada, o próprio comprador registra a decisão da Direção.
- **Fazer:** o pedido fica no mesmo registro do Estoque. A aprovação exige o papel com alçada de quem age. A Direção decide só pelo perfil da Direção.
- **Cobertura:** está especificado (SUP-3 e PCM-1c), mas adiado e sem código.

**21. Custo realizado no Mapa não usa as horas nem o preço real** (GES-1)
- **Onde:** Mapa › camada Custos (cor do talhão, "Realizado provisório", painel Custos). É a única visão de custo no menu.
- **Regra:** PRD 44.5 (horas × tarifa), 51.3 e ORC-03.
- **Dano:** 10 ha de plantio feitos em 1,5 h ou em 6 h dão o mesmo custo. Nesse exemplo, R$ 1.793,60 ficam escondidos, e o talhão aparece verde, "no previsto", com custo real maior. Reproduzido.
- **Fazer:** quando houver horas apontadas, custo da operação = horas × custo/h do conjunto. Sem horas, rótulo "pela tarifa padrão". Insumo com o rótulo "a preço do plano" até o lote ter custo.

### 3.2 S3 mais relevantes

| # | Onde | Dano | Fazer |
|---|---|---|---|
| 22 | Cadastros › Culturas e operações › Operação (sem campo "família") (CAD-8) | A exceção da irrigação só com água é decidida pelo nome. Uma operação chamada "Irrigação com ureia" pularia o agrônomo: seria S1 no software real. | Campo "Família" (Agrícola · Irrigação só com água · Manutenção · Beneficiamento). A exceção vale só para irrigação sem nenhum produto. |
| 23 | Aprovação da O.S. e CD-04 (CREA só como data) (CAD-1) | O CREA vencido não é conferido na hora de aprovar. O sp-conf confere só ao conceder o papel. | Conferir a credencial no momento da aprovação. Registrar o número do registro e vincular a ART. |
| 24 | O.S. › Cancelar sem execução, com material entregue (OS-3) | A tela diz "Reserva liberada no Estoque", e 320 L ficam com o operador sem nenhuma pendência na O.S. nem no app. | A ordem fica "Cancelamento pendente" até a devolução. |
| 25 | O.S. do plano sem receituário vinculado (AGRO-7, OS-20) | A maioria das aplicações não tem documento legal rastreável no sistema. | Ao aprovar O.S. com agrotóxico, exigir número, data e responsável técnico do receituário (emitido no sistema ou fora). |
| 26 | Cadastros salvos não alimentam os processos (GAP-3) | Talhão inativado continua planejável. Fornecedor homologado continua "não homologado" na Compra. O senhor validaria cadastros que não mudam nada. | Os processos leem o cadastro salvo, ou o cadastro mostra o aviso "demonstração". No software real, uma identidade única por máquina. |
| 27 | Sobra de calda (GAP-2) | Para encerrar, é preciso "devolver" calda como glifosato puro, ou declarar aplicado o que não foi. | "Registrar sobra ou perda", com destino próprio, separado da devolução. |
| 28 | Índice › "Restaurar dados iniciais" e "Entrar como" (GES-3, GES-12) | Restaurar não restaura (os dados ficam salvos no navegador), e "Entrar como Beto (agrônomo)" mantém a Ana. O senhor testaria sobre dados alterados e com o perfil errado. | Ligar o botão à restauração real. O cartão do perfil troca o perfil de verdade. |
| 29 | Etapas "concluídas" com pendência e etapas futuras em vermelho (SAF-20, IR-17, OS-21) | No Planejar safra, a etapa aparece "✓ concluída" com 4 cultivos sem plano, e as etapas futuras aparecem em vermelho. Na Irrigação, a pendência comum aparece em vermelho. Uma ordem de beneficiamento encerrada aparece com selo vermelho. Provavelmente é a origem da sua dúvida sobre "concluído em vermelho". | "Concluída" só quando a condição da etapa se cumpre. Vermelho só para impedimento real (ETP-01, DS-17). |

**Demais S3, numa linha por módulo** (detalhe no apêndice):
- **Cadastros:**
  - Mapa grava sem as conferências do talhão (CAD-2);
  - item sem conversões nem dono (CAD-4);
  - local sem tipo Packing (CAD-5);
  - rendimento com R$/h digitado (CAD-6);
  - unidade da cultura sem trava (CAD-7);
  - calibração (CAD-9);
  - NR por atividade (CAD-10);
  - parceiro sem documentos (CAD-11);
  - máquina sem fazenda (CAD-12);
  - estrutura gerencial aceita ciclo pai-filho (CAD-13);
  - camadas do Mapa diferentes do decidido (CAD-14).
- **Agronomia:**
  - publicar plano sem papel (AGRO-5);
  - contagem de aplicações diferente da O.S. (AGRO-8);
  - protocolo MIP sem fonte (AGRO-9);
  - inimigos naturais e espécie de daninha (AGRO-10);
  - catálogo do plano (AGRO-11);
  - gatilho de perene (AGRO-12);
  - foco sem pontos (AGRO-13);
  - dose pré-preenchida (AGRO-14).
- **Planejar safra:**
  - plantio fora do zoneamento (ZARC) ou no vazio sanitário sem aviso (SAF-7);
  - excluir cultivo já plantado (SAF-8);
  - trocar a fazenda da safra (SAF-9);
  - janela em dias aptos (SAF-10);
  - capacidade e custo sem o realizado (SAF-12);
  - resumo sem R$/sc (SAF-13);
  - simulação de recurso que grava no cadastro (SAF-14);
  - produto fixo ou troca de marca (SAF-16);
  - "coberto" quando é pedido (SAF-18);
  - prazo de reposição fixo (SAF-19);
  - colheita × secagem (SAF-21);
  - links para telas fixas (SAF-22).
- **O.S.:**
  - encerrar marca tudo como conferido (OS-9);
  - apontamento sem horas nem talhão (OS-10);
  - app sem motivo de pausa (OS-11);
  - revisar saldo (OS-12);
  - histórico para o agrônomo (OS-13);
  - vento e umidade (OS-14);
  - EPI (OS-15);
  - ficha só na OS-0424 (OS-16);
  - conflito de recurso (OS-17);
  - detalhe com dado velho (OS-18);
  - custo da O.S. (OS-19).
- **Irrigação:**
  - percentímetro (IR-4);
  - CAD e Kc (IR-5);
  - "medido" que é estimado (IR-6);
  - validade das fontes (IR-7);
  - energia (IR-8);
  - regime da outorga (IR-9);
  - parâmetros sem versão (IR-10);
  - app do irrigante (IR-11);
  - fertirrigação sem papel (IR-12);
  - simular período (IR-13).
- **Suprimentos:**
  - conferência não cega no recebimento (EST-9);
  - preço × nota (EST-10);
  - valor do estoque (EST-11);
  - local de defensivo (EST-12);
  - embalagens vazias (EST-13);
  - transferência e estorno (EST-14);
  - validade da reserva (EST-15);
  - validade do lote existente ignorada (EST-16);
  - segregação de funções (CMP-4);
  - prazo de pagamento (CMP-5);
  - identidade do produto na proposta (CMP-6);
  - múltiplo de embalagem (CMP-7);
  - cancelar pedido (CMP-8);
  - atraso apagado (CMP-9);
  - reposição (CMP-10).
- **Manutenção:**
  - verificação de segurança antes do serviço (MAN-2);
  - aprovação econômica (MAN-3);
  - criticidade (MAN-10);
  - custo divergente na Gestão (MAN-11);
  - parada fora do PCP (MAN-12);
  - horímetro no apontamento (MAN-13);
  - checklist pré-uso (MAN-14);
  - "Pode operar? Não" (MAN-15);
  - executante (MAN-16);
  - apto sem segundo olhar (MAN-17);
  - fonte do plano (MAN-18);
  - causa da falha (MAN-19);
  - tempos (MAN-20);
  - cancelar e terceiro (MAN-21);
  - componentes (MAN-22).
- **Produção:**
  - físico do grão (PRO-3);
  - balança (PRO-4);
  - previsão de grão (PRO-5);
  - contagem com uma planta (PRO-6);
  - liberar sem papel (PRO-8);
  - colheita sem carga (PRO-9);
  - terceiros (PRO-12);
  - classificação (PRO-13);
  - romaneio (PRO-14);
  - capacidade de recepção (PRO-15).
- **Gestão:**
  - base do orçamento (GES-4);
  - previsto calculado em dobro (GES-5);
  - liberador PCP × gestor (GES-7);
  - telas de Gestão fixas (GES-8);
  - custo dobrado na O.S. (GES-9);
  - ficha de indicador (GES-10);
  - índice no celular (GES-11);
  - "Relatar problema" (GES-13);
  - custo-hora de pessoa (GES-14);
  - modo de gravação no ERP (GES-15).
- **Entre módulos:**
  - custo da terra e arrendamento (GAP-4);
  - mão de obra por equipe (GAP-5).

### 3.3 S4 (cosmético ou melhoria), uma linha por módulo
- **Cadastros:** CCIR, NIRF e inscrição estadual; textura do talhão; empresa e arrendador vindos do cadastro mestre; cultivar sem grupo de maturação, tecnologia e ZARC; jornada sem intervalo; defensivo em local impróprio; vigência da estrutura gerencial; conferência simulada no detalhe da fazenda; colunas compostas (as colunas estão no sp-tabr).
- **Agronomia:** a memória de cálculo do KCl não fecha (é 117 kg/ha e +2,9 %).
- **Planejar safra:** sem aviso de soja sobre soja; colunas demais; "Salvar" sem dizer o alcance; eficiência sem faixa típica; "Nova safra" sem herdar a fazenda; o PRD 71.6 ainda descreve 6 etapas.
- **O.S. e app:** ordem encerrada com selo vermelho (já no 3.2); "Hoje no campo" sem os blocos Agora/Depois/Impedidas; lista com 18 colunas.
- **Irrigação:** chuva prevista e gráfico por setor; desempenho com números fixos; sensor sem setor e "validar" sem motivo; vermelho em pendência comum; a decisão "água só na Irrigação" não está registrada; colunas (sp-tabr).
- **Suprimentos:** inventário sem plano cíclico; grades de 12 a 14 colunas, com a unidade fora da célula (sp-sup).
- **Manutenção:** menus demais (resolvido no sp-pcm); abastecimento sem limite do tanque; pendência criada com 1 h inventada.
- **Produção:** "Bloqueado" inclui "em inspeção"; veículos fixos; silo medido em sacas; custo R$/sc ausente.
- **Gestão:** cor de indicador definida pela posição; aviso de recusa igual ao de sucesso; busca que não é campo; vários menus abertos; o índice ainda diz "PRD v3.7" e o cenário DEMO-14 diz 60/40, quando os dados estão em 30/70.

---

## 4. O que já está em correção nas frentes

Conferido no git hoje. Das frentes listadas, só a da trava de área entrou no protótipo, e foi depois da v53. As outras 13 têm trabalho feito na própria frente que ainda não foi juntado ao protótipo publicado. Esse é o "no meio do caminho" mais concreto.

| Frente | O que cobre deste parecer | Estado |
|---|---|---|
| Trava de área com perene (sp-safc01) | SAF-6 (talhão com mais hectares planejados do que tem) | Juntada ao protótipo (`9fb09a5`), depois da v53. Um ajuste posterior da frente (`d1b81f4`) ainda está fora. Não conferi se o artefato foi republicado. |
| Capacidade entre safras (sp-safc02) | SAF-11 | Feita, não juntada |
| Demanda única (sp-ctl4) | SAF-5 (estoque por fazenda), CMP-3 (compra do já entregue), SAF-17 (cotação que não reduz); SAF-4 só em parte | Feita, não juntada (15 commits) |
| Outorga, Agrofit e alvo (sp-ctl5) | AGRO-15 (AG-07 "emitia" receituário); alvo no "Usar na O.S." (parte do AGRO-3 e do OS-13); outorga como fonte única (parte do IR-9). A ficha do pivô ainda não começou. | Feita, não juntada |
| Análise de solo (sp-solo) | AGRO-16 (calagem e validação pelo agrônomo; análise como sugestão); CAD como referência (parte do IR-5) | Feita até a P6, não juntada |
| Configurações (sp-conf) | OS-7 (aprovar e liberar por pessoas diferentes); GES-6 (alçadas e trilha reais); assinatura em nome de quem age (parte do GES-2); CREA na concessão do papel (parte do CAD-1) | Feita, não juntada; revisão do Codex pendente. Resíduo: a dispensa de saldo ainda exige os dois papéis na mesma pessoa. |
| Domínio (sp-dom) | OS-8 (divergência de dose no turno); PRO-2 (café "sc a apurar") | Feita, não juntada |
| Comercial (sp-com) | PRO-1 (saca de 50 × 60 kg), PRO-7 (vencido na reserva), PRO-11 (comercial); PRO-8 em parte | Feita, não juntada |
| Beneficiamento (sp-ben) | PRO-10 (packing do mamão); PRO-8 e PRO-13 em parte | Feita, não juntada |
| Manutenção (sp-pcm) | MAN-6 (triagem e criar ordem), MAN-7 ("apto" só com teste), MAN-23 (números calculados), MAN-24 (menu único); em parte MAN-1 (só o T1), MAN-12, MAN-16, MAN-20 | Feita, não juntada. **Traz um defeito novo (MAN-9).** O 1b e o 1c estão só especificados. |
| Suprimentos (sp-sup) | EST-4 (entrega só da reserva própria), EST-5 a EST-8 (laudo por parcela, contagem, unidade, devolução), SUPR-1 (grades) | Feita (SUP-2a e SUP-2b), não juntada. A SUP-3 (CMP-1, CMP-2, CMP-9) está especificada e adiada. |
| Tabelas (sp-tabr) | CAD-22, IR-19 e parte do IR-15 e do IR-16 (uma variável por coluna) | Feita, não juntada |
| Design system (sp-ds) | Separadores, hover verde, retorno visual e dica | Feita, não juntada. Não trata a cor das etapas e pendências (SAF-20, IR-17). |
| Navegação (sp-nav) | Planos agronômicos em lista → detalhe, sem etapas falsas em vermelho | Feita (1 commit), não juntada. Não constava da lista do pedido. Deixa a versão por cultivo (SAF-2) fora. |
| Pendentes sem frente ativa | CONTROLE-02 (OS-9, SAF-3 em parte, SAF-12, GES-4); PCM-1b/1c (MAN-3, MAN-4, MAN-20, MAN-21); SUP-3 (CMP-1, CMP-2, CMP-9); custos D7/ORC-CUSTOS (GES-1, GES-8, SAF-13) | Não iniciados |

---

## 5. O PRD: o que é da v3.9 e o que a v3.10/3.11 acrescentou

A v3.11 já está na `main` (PR #48). Para separar as exigências, comparei os identificadores com a versão anterior ao PR #48, que é a v3.9.

**Exigências que já estavam na v3.9 e o protótipo ainda não cumpre (as mais pesadas):**
- **Lote e reserva:**
  - lote vencido e ordem de validade (RN-015, 42.1);
  - reserva devolvida ao encerrar e ao dispensar (42.5, CMD-47);
  - cancelamento com material entregue (CMD-46);
  - mistura completa antes de iniciar (42.2, ESTOS-03);
  - volume de calda na versão aprovada (41.3, 41.5).
- **Agronomia e lei:**
  - reentrada (RN-016);
  - conferência legal do plano (AGR-027/028);
  - autoria da decisão técnica (AG-04, AGR-031, AG-07).
- **Planejamento:**
  - variedade do cadastro (39.1–39.2);
  - versão do plano no cultivo (40.3);
  - estados e autorização da safra (8.1, CMD-04);
  - nenhuma execução inferida pela data (SAFRA-05).
- **Manutenção e irrigação:**
  - bloqueio do ativo nas alocações (RF-AST-001, 47.8, AGUA-08, PCMP-04);
  - peças na ordem (RF-AST-004);
  - consumo de diesel (CAL-07);
  - volume medido ou estimado (RF-WAT-004);
  - vazão efetiva (CAL-09).
- **Suprimentos:** pedido até o recebimento (RF-SUP-006/007); conciliação com a nota (RF-SUP-011).
- **Governança e custos:**
  - quem decide e alçada (2.1, RF-GOV-002);
  - inativar bloqueia novos usos (RF-DAT-001);
  - custo de máquina por horas (44.5);
  - base aprovada × revisão × realizado (RN-031).
- **Campo:** ocorrência com destino (RF-OPS-006).

**O que a v3.10/3.11 acrescentou e o protótipo ainda não reflete:**
- **Produto fixo ou troca de marca pelo mesmo ingrediente ativo** (40.5, 40.6, SUBST-01 a SUBST-17; v3.11). Está ausente:
  - no plano e no ajuste por talhão (SAF-16);
  - na proposta de compra (CMP-6);
  - no item de defensivo (CAD-3);
  - no recebimento de produto diferente (EST-2).
- **Confiabilidade transacional e offline (cap. 73, v3.10):**
  - **Bem atendido:** aprovação individual também nas operações mecânicas (73.9); conciliação do apontamento web × app; consumo acima da custódia (CMD-50).
  - **Falta:**
    - família da operação (CAD-8);
    - aprovar e liberar como duas ações (APROV-09, AC-142): o sp-conf faz em parte, e o padrão depende da sua decisão (PEND-OS-01);
    - validade da reserva (RN-046, CMD-49, RSV-16; EST-15);
    - abastecimento registrado por duas pessoas (CONC-09/11, AC-75; MAN-8);
    - validade de cada fonte de dado da irrigação (PROJ-13/14; IR-7);
    - "Meu dia" com Agora/Depois/Impedidas (64.7; OS-22);
    - aviso de ha/h acima do rendimento (CAMPO-14; OS-11);
    - chave de repetição na Compra, no receituário e no plano (73.3).
- **Design system (cap. 74, v3.10) e padrões de 09/10:**
  - vermelho só para impedimento (DS-17; SAF-20, IR-17, OS-21);
  - cor pelo estado e não pela posição (DS-37; GES-16);
  - aviso de recusa distinguível (DS-43);
  - tela de entrada legível no celular (74.3.11; GES-11);
  - unidade explícita e uma variável por coluna (em correção no sp-sup e no sp-tabr).
- **Melhoria contínua (cap. 75, v3.10):** "Ajuda › Relatar problema", com imagem e comentário (FB-01 a FB-05), está ausente (GES-13).
- **API de integração e credencial por integração** (RF-INT-008, v3.11): o sp-conf mostra a fila do ERP sem duplicar; faltam o modo de gravação e a ficha da credencial (GES-15).

---

## 6. Limites deste parecer

- **Como foi feito.** Nove auditorias por módulo, uma segunda verificação independente e uma crítica de completude.
  - **Os 38 S2 foram reverificados:** no código, e a maioria reproduzida com o motor real do protótipo e dados sintéticos. A exceção é o GAP-1, que a crítica reproduziu e eu reconferi no código.
  - **Os S3 e S4 vêm da primeira passada:** cada um tem o arquivo e a linha, mas não houve segunda verificação independente.
  - **O navegador foi usado poucas vezes** (Planejar safra, MIP, Kanban da O.S., índice, assinatura). O resto é leitura do código e simulação.
- **Defeitos latentes.** Vários só aparecem em condições que os dados de demonstração não têm (lote vencido, dois lotes do mesmo produto, CREA vencido, pivô sem medidor em uso). Classifiquei pela regra como ela seria levada ao software real e marquei "latente" onde cabe.
- **Normas a verificar.** Nada aqui é afirmado como fato legal. São citações a conferir na fonte e na vigência:
  - NR-31 (aplicação e armazenamento de agrotóxicos, EPI), NR-10, NR-12 e NR-7;
  - Lei 7.802/1989 e Lei 14.785/2023 com o Decreto 4.074/2002 (conteúdo do receituário);
  - Lei 9.974/2000 (devolução de embalagens);
  - Lei 9.433/1997 e normas estaduais (outorga e regime em renovação);
  - ZARC e calendários de vazio sanitário (MAPA e estados);
  - ABNT NBR 9843-3 (armazenamento);
  - regras tarifárias da ANEEL;
  - classificação de grãos do MAPA;
  - metodologia de custo da Conab;
  - ASABE D497 (eficiência de campo);
  - ISO 9001, item 8.4 (homologação de fornecedor).
  Valores de referência (limite de deriva, intervalo de inventário, faixa de eficiência) não foram inventados.
- **O que é do software real e não se cobra do protótipo:**
  - servidor como autoridade, transação, chave de repetição e outbox;
  - login, permissões e trilha imutável;
  - LGPD;
  - integração real com ERP, nota fiscal e balança;
  - telemetria, horímetro e estação;
  - funcionamento sem internet de verdade;
  - geometria no banco;
  - conta decimal;
  - desempenho.
  O parecer julga se a **regra** está desenhada certo para ser levada.
- **Não examinado** (a crítica de completude apontou):
  - filas por papel ("Meu dia", "Aprovações");
  - perfis que faltam (comprador, direção, qualidade, irrigante, PCM);
  - rastreio do lote de insumo até o cliente e caderno de campo por talhão;
  - estádio da lavoura como fonte única;
  - as jornadas DEMO do PRD 16.2 de ponta a ponta;
  - a cadeia completa do diesel;
  - algumas telas do app;
  - expurgo de grão, qualidade de semente, drone, substituto do responsável técnico e financeiro;
  - acessibilidade além do que foi citado.
- **Sobre "concluído em vermelho".** No produto, os casos são os da linha 29 (etapas e selos). Sobre o trabalho dos agentes, a seção 4 mostra o que está feito nas frentes e não juntado ao protótipo.

---

## 7. Ordem recomendada

**Passo 1. Fechar o que está no meio do caminho, antes de pedir novo teste ao senhor.**
- Juntar ao protótipo, uma frente por vez, com a bateria de testes e a revisão do Codex, as 13 frentes já feitas.
- Ordem sugerida pela dependência:
  1. demanda (sp-ctl4) e capacidade (sp-safc02);
  2. domínio (sp-dom);
  3. suprimentos 2a e 2b (sp-sup);
  4. manutenção (sp-pcm), **corrigindo antes o consumo de diesel (MAN-9)**;
  5. configurações (sp-conf), depois da revisão;
  6. outorga e Agrofit (sp-ctl5), solo (sp-solo), comercial (sp-com) e beneficiamento (sp-ben);
  7. tabelas (sp-tabr), design (sp-ds) e navegação (sp-nav).
- No mesmo passo, corrigir o "Restaurar dados iniciais" e o "Entrar como" do índice (GES-3, GES-12). É barato e protege o seu tempo de teste.

**Passo 2. Encaixar nas frentes atuais o que é da mesma natureza:**
- **Suprimentos (sp-sup):**
  - lote elegível, validade e vários lotes (item 10);
  - reserva que volta (item 9);
  - produto errado no recebimento (item 11);
  - depois, SUP-3 (item 20).
- **Manutenção (sp-pcm):**
  - diesel (item 19);
  - regra única "a máquina impede o trabalho", também na irrigação (item 15);
  - peças pelo 1b (item 18).
- **Domínio (sp-dom):** mistura incompleta (item 12) e ficha de calda (item 13).
- **Configurações (sp-conf):** CREA conferido na decisão (linha 23).
- **Outorga e Agrofit (sp-ctl5):** alvo e conferência legal também no plano (item 3) e unidade da bula × lote (item 4).
- **Demanda (sp-ctl4):** operação vencida que continua na compra (item 8); "coberto pelo pedido" (SAF-18).
- **Design (sp-ds):** etapas e cores (linha 29).

**Passo 3. Frentes novas, uma por vez, nesta ordem:**
1. **Aplicação segura e legal:**
   - reentrada (2);
   - autoria do receituário do MIP (1);
   - receituário vinculado à O.S. (25);
   - família da operação (22);
   - ocorrências com destino (14);
   - sobra de calda (27);
   - EPI (OS-15).
2. **Planejamento confiável, junto com o CONTROLE-02:**
   - variedade do cadastro (5);
   - versão do plano no cultivo (6);
   - estados e autorização da safra (7);
   - conferência diária;
   - custo realizado por horas (21).
3. **Irrigação medida:**
   - fonte de volume por setor (16);
   - cadastro único de setor e pivô (17);
   - percentímetro;
   - parâmetros com versão.
4. **Cadastro que alimenta os processos** (26).

**Fica para o software real:** a infraestrutura listada na seção 6, levando as regras já corrigidas no protótipo.

**Decisões que só o senhor pode tomar** (perguntas curtas, na homologação):
1. Na sua fazenda, quem libera a O.S. já aprovada pelo agrônomo: o PCP ou o gestor? (GES-7, PEND-OS-01)
2. Os contratos de soja são em saca de 50 ou de 60 kg? (PRO-1)
3. Com a outorga "em renovação", pode irrigar? Depende do jurídico e da norma do estado. (IR-9)
4. As camadas do Mapa voltam às 9 decididas em 26/09 (com Solo, Estádio e Colheita)? (CAD-14)
5. Custo da terra e arrendamento, e a formação da lavoura perene como investimento: como tratar, com o contador? (GAP-4)
6. Valor da alçada de manutenção e critério de criticidade das máquinas. (MAN-3, MAN-10)

Apêndice técnico, com todos os achados (identificador, arquivo:linha, severidade e cobertura): `APENDICE.md`, na mesma pasta.
