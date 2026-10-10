# Descoberta — regras de negócio que limitam as visões (lente "regras")

- Pedido: ViewSwitcher (proprietário, 10/10/2026). Leitura feita só com leitura, sem build nem testes.
- Bases lidas: `Safrion-Software-` em `b8d6f84` (PRD 3.11, DECISIONS, design system, `apps/web`); `sp-proto` em `0139898` (branch `claude/prototipo-v44`, gerador `tools/prototipo/v37/gen37`). As frentes DS, TABR e NAV1 foram consultadas sem diferença material para esta lente.
- Rótulo: tudo aqui está **especificado ou lido**. Nada foi executado.
- Abreviações: `PRD:n` é a linha de `docs/PRD.md`; `gen37/` é `sp-proto/tools/prototipo/v37/gen37/`.

## 0. Resumo

1. **Kanban da O.S.:** nenhum arraste é seguro no protótipo. Lá, `osc_liberar` aprova e libera juntos (CMD-42 + CMD-06, `gen37/areas/processo_os.py:327-343`), e o PRD proíbe aprovar por arraste (APROV-05, `PRD:13421`).
   - No software real, só A liberar → Liberadas (CMD-06) e Em conferência → Encerradas (CMD-10) podem ser **iniciados** por arraste, sempre com confirmação no contexto.
   - As outras transições são fatos do executor ou derivadas, ou são saltos. Essas o arraste recusa.
2. **"Desfazer" não existe para comandos com efeito.** CMD-06 cria reserva. CMD-08 devolve a reserva sem carência. CMD-10 fecha a edição. Uma reserva vencida não volta (`PRD:2845`, `PRD:7516`). O que dá para oferecer é **confirmar antes**; desfazer só para preferência de visão e reprogramação de data, como novo comando.
3. **Calendário:** só a **janela prevista de execução** é editável (`PRD:3079`), pelo PCP (CMD-05/11/34). Ordem iniciada move só o saldo. Fatos (início, apontamento, término) nunca. O protótipo **não tem validador de janela**, então o calendário fica só de leitura até existir um.
4. **Mapa:** só existe geometria de talhão/parcela e de pivô. Na Lagoa Grande, os pivôs são círculos (sintéticos na nuvem). Na Santa Rita, só o T1 tem polígono validado e o resto é desenho. Pontos de água são pontos. Máquinas não têm posição. Vistorias e ocorrências se localizam pelo talhão, não pelo ponto.
5. **Carga por recurso:** existe e é decisão do proprietário. É a visão "Recursos" da O.S. (DEC-2609-09, `PRD:12477`; `gen37/alocacao.py`). O filtro não pode esconder ocupação de outra ordem.
6. **Árvore "fazenda › setor › talhão" está errada.** O setor é o setor de irrigação, opcional e entidade distinta (`PRD:7258`). A árvore certa é Fazenda › Talhão › Parcela. Centro de custo é plano nos dados; só Natureza tem hierarquia.
7. **Galeria:** nenhuma entidade tem foto como informação principal.
8. **Tabela agrupada já é um estado da Lista** (G2 "+ Agrupar por", `PRD:297`). No software real, `agrupar=` já está na URL e a soma se recusa a juntar unidades diferentes (`apps/web/src/tabela/logica.ts:173,227-292`). Não criar um segundo componente.

## 1. Kanban da O.S.: transições por arraste

Regras de base:
- Cinco colunas fixas; selo nunca vira coluna (`PRD:2972-2984`).
- A etapa é derivada do estado, não gravada pela tela (`PRD:2988`, `PRD:2895`).
- O arraste "apenas inicia o comando de transição permitido. Não grava estado diretamente… Preferir botões contextuais" (`PRD:2996`). Ver também OSFASE-08 (`PRD:3025`).
- O protótipo não oferece arrastar; se oferecer, tem alternativa por botão (DS-46, `PRD:14409`). Arrastar sempre tem alternativa (`PRD:15021`, WCAG 2.5.7).
- No celular: seletor das cinco etapas e lista vertical, sem arraste (`PRD:2992`).
- Aprovar (CMD-42) e liberar (CMD-06) são ações separadas, sem ação composta (`PRD:2877`, APROV-09 `PRD:13435`).

| De → Para | Comando · quem | Pré-condição (PRD) | Validador no protótipo | Arraste | Dano evitado (severidade se errar) | Desfazer |
|---|---|---|---|---|---|---|
| A liberar → Liberadas | CMD-06 (`PRD:2790`) · liberador por domínio: PCP ou gestor (DEC-0910-15, pendente); no protótipo `OS_LIB='gestor'` (`processo_os.py:325`) | Três condições, uma a uma (APROV-01, `PRD:13396`): autorização econômica (CMD-04); aprovação vigente da **versão** (APROV-07); prontidão. Também: cobertura de lotes (RSV-03 a), trava legal, carência e talhão indisponível (DEC-0910-22, `DECISIONS.md:135`) | `osc_liberar` → `osLibPor` exige agrônomo **e** gestor, depois `osc_libEfeito` com carência (`carBloqColheita`, `dados_carencia.py:384`), regra legal (`osUsoErro`) e estoque (`cenLiberar`, `cenario.js:75`). Ver `processo_os.py:334-364` | **Protótipo: recusar.** O comando grava CMD-42 junto, e aprovar por arraste é proibido (APROV-05). A versão também não é exibida ao decisor (CMD-42, `PRD:2838`). O protótipo removeu o estado "Aprovada pelo agrônomo" (`processo_os.py:44-51,164`), então não há como distinguir aprovada de não aprovada. **Real:** só como início de CMD-06 sobre versão já aprovada em CMD-42 separado, com confirmação no contexto (DS-44) mostrando REQ, lotes, validade e resultado por item. Sem aprovação, recusa "Aguardando agrônomo · {nome}". Água sem produto não é arrastável: o CMD-06 é do sistema (APROV-15) | S1: aprovar ou liberar sem revisar produto, dose e área leva a aplicação sem aprovação ou receituário. Também reserva indevida de lote | Não há "desliberar". O caminho é CMD-46 (cancelar sem execução, gestor, motivo; `PRD:2842`) ou nova versão (CMD-32) |
| Liberadas → Em execução | CMD-07 Iniciar (`PRD:2791`) · executor | Liberação e aprovação vigentes (APROV-07); reserva cobre o saldo elegível (RSV-15, `PRD:12822`); checklist; condições. Chuva impede iniciar, mas não tira a ordem de Liberadas (APROV-10, `PRD:13441`) | `osc_iniciar` (`processo_os.py:415`) com carência e `osIniErro` → `cenIniFalta` (entrega e confirmação no app, `cenario.js:169`). No app: `cenIniciarTurno` (`cenario.js:179`) | **Recusar.** O início é o "primeiro evento real de início" (`PRD:2869`) e se registra onde acontece (app ou turno), por quem executa | S1/S2: fato físico inexistente gravado; início sem entrega ou checklist | Sem reverso: "não fazer parecer que nunca começou" (`PRD:2988`) |
| Em execução → Em conferência | CMD-08 Concluir execução (`PRD:2792`) · executor | Todo o trabalho físico terminou, ou o saldo foi dispensado por CMD-47. Reprogramar não conta como término | `osc_conferencia` (`processo_os.py:443`) recusa se o saldo for maior que 0 | **Recusar.** A entrada é automática ao concluir, e não se cria clique só para passar de coluna (`PRD:2875-2877`). Com saldo, o caminho é Dispensar saldo (CMD-47; gestor e agrônomo; acima de 20 % vai à Direção, `processo_os.py:464-468`) | S2: área não tratada declarada como feita; o saldo some do PCP/PCE (`PRD:2959`); a reserva entra na política **sem carência** (tabela RSV-05, `PRD:12777`) e volta ao disponível | O reverso é CMD-48 (`PRD:2844`), com motivo e reserva nova (RSV-15). Pode falhar se o lote já foi tomado. **CMD-48 não existe no protótipo** |
| Em conferência → Encerradas | CMD-10 (`PRD:2794`) · conferente ou regra autorizada | Apontamentos conferidos; saldo destinado; sobras recebidas; custódia zero; relato em conferência resolvido (CONC-19); nada pendente no aparelho (DEC-0910-18) | `osc_encerrar` → `cenPodeEncerrar` (`cenario.js:430`) | **Admissível, mas não recomendado.** Se oferecer, o drop abre a confirmação com o bloqueio do `cenPodeEncerrar` e quem resolve. A recomendação é o botão no Próximo passo (`PRD:2996`) | S2: encerrar com sobra ou custódia deixa estoque e custo errados (OSFASE-05). O validador já barra | Irreversível: fecha a edição direta e grava a outbox do ERP. Correção só por evento vinculado |
| Liberadas → A liberar | Não há comando de usuário. É derivado: liberação deixa de vigorar ou aprovação é invalidada (FL-OS-01, `PRD:2954`; APROV-08/10) | — | — | **Recusar.** Para revogar, usar CMD-46, CMD-32 ou o bloqueio do PCM (CMD-18) | S2: etapa gravada pela tela diverge das outras visões; reserva órfã | — |
| Em execução → A liberar ou Liberadas | — | — | — | **Recusar** (`PRD:2988`) | S1/S2: integridade do fato | — |
| Em conferência → Em execução | CMD-48 · conferente ou PCP com permissão de CF-02 | Motivo, saldo ou programação, revalidação técnica, RSV-15 | Não implementado | Botão "Retornar ao trabalho" com motivo. Se houver arraste, o drop **abre o formulário** e não executa sozinho | Correção só de documento permanece Em conferência | — |
| Encerradas → qualquer | — | — | — | **Recusar** | Histórico | — |
| Saltos: A liberar → Execução, Conferência ou Encerradas; Liberadas → Conferência ou Encerradas; Execução → Encerradas | Seria uma composição de comandos | — | — | **Recusar.** "Arrastar Em execução para Encerrada não elimina conferência ou devoluções" (`PRD:2996`) | S1/S2 | — |
| Para Canceladas | CMD-46 | Sem realizado, só em A liberar ou Liberadas | `osc_cancelar` (`processo_os.py:454`) | Não é coluna (`PRD:2984`). Fica como ação secundária destrutiva | — | — |
| Reordenar dentro da coluna | — | — | — | Não gravar como prioridade. A ordem sugerida é por risco e prazo, explicada (`PRD:2998`) | — | — |

As famílias de manutenção (MA-04) e beneficiamento (CO-05) usam as mesmas 5 colunas com outro aprovador (`PRD:2881-2889`). O componente do beneficiamento já é o mesmo `_kanban` (`processo_beneficiamento.py:9,13`). Valem as mesmas regras de arraste.

## 2. Calendário: o que é editável, por quem e como

| Data | Editável? | Quem · comando | Validação | Desfazer |
|---|---|---|---|---|
| Janela prevista da O.S. em A liberar | Sim. A janela é a **data prevista de execução**, não a de criação (`PRD:3079`) | PCP · CMD-05 Programar (`PRD:2789`). Antes de CMD-04, fica como proposta, sem reserva | APROV-11 (`PRD:13442`): dia ou hora **dentro** da janela técnica aprovada é operacional e revalida só a prontidão. **Fora** da janela técnica fixada (estádio, DAP, umidade) é técnica: nova versão e nova aprovação. Também revalidar se a data afeta clima, estádio, insumo ou instrução (`PRD:3091`). Carência e reentrada pela área (DEC-0910-11). Recurso livre no novo intervalo (sobreposição: RECURSO-06). Trocar a data não troca produto nem área (`PRD:699`) | Novo CMD-05 com validação nova |
| Janela da O.S. em Liberadas | Sim, com aviso de impacto | PCP · CMD-05 | Fora da validade da liberação, ela deixa de vigorar e a ordem volta a A liberar (`PRD:2954`, `PRD:3091`). A reserva sai de "protegida" e entra na política (tabela RSV-05, `PRD:12763-12779`). Fichas e pacote offline já distribuídos exigem notificação e reconhecimento (44.9). "Arrastar mostra impacto antes de confirmar" (`PRD:633`) | **Não restaura** liberação nem reserva vencida (CMD-49, `PRD:2845`; `PRD:7516`) |
| Ordem Em execução | Só o **saldo** | PCP · CMD-11 Reprogramar saldo (`PRD:2795`) | "Não deslocar ordem em execução ou concluída" (`PRD:6774`). Saldo fora da liberação entra na política (`PRD:12774`) | Idem |
| Em conferência ou Encerradas; início ou término real; data de apontamento | **Não**: são fatos | Correção com histórico (CMD-50), nunca por arraste | — | — |
| Data de operação do plano gerada por gatilho (DAP/DAC) | Não por arraste | Agronomia, no rascunho do plano (39.6) | "Data calculada é projeção; não substituir o gatilho por sua data" (`PRD:6772`). Fixar a data é escolha explícita. Mudar a âncora é CMD-31 | — |
| Vistoria programada (AG-01, FO-03) | Sim | Agrônomo | Afastar além do intervalo do protocolo (`dados_mip.py`: `inter`) gera **aviso**, não trava (AGENTS §4). Vistoria coletada é fato | Reprogramar |
| Irrigação (OS-0419/0422/0423) | Sim, por hora | Irrigante ou PCP | Muda a janela, então revalida bomba, energia, conflito (ex.: "Conflito · parada da B3") e limite da outorga (DEC-0910-33/34). Na água sem produto, a liberação automática (DEC-2609-10) é reavaliada | — |
| Preventiva de manutenção | Sim, dentro do limite técnico | PCM | "Adiamento além do limite não é autorizado apenas pelo arrastar da agenda" (`PRD:7964`); adiar exige decisão, limite e janela registrados (`PRD:7524`) | — |
| Alerta ou pendência (IN-03) | "Adiar alerta não muda a data da obrigação" (`PRD:388`) | — | — | — |

Regras transversais:
- Não exigir arrastar para operar (`PRD:2379`). A alternativa ao arraste no calendário faz parte do aceite [S3] (`PRD:307`).
- Usar o fuso da fazenda (`PRD:3075`).
- Ordem sem janela (OS-0422, "Janela a definir"; `gen37/dados.py:116` com `('','')`) não pode sumir: vai para a faixa "Sem data".
- Ordens de outros períodos continuam visíveis (`PRD:3095`, JANELA-06 `PRD:3113`).

**No protótipo não há validador de janela.** O "Programar" do PL-04 e o formulário do CA-01 aceitam janela em texto livre (`gen37/areas/planejamento.py:411`, `gen37/areas/campo.py:189`), e nenhum CTL cobre isso (`sp-proto/docs/controle-01/PLANO.md:34-43`). Antes de permitir arraste, precisa existir um serviço único de domínio (ENG-011). Até lá, o calendário fica **só de leitura**, com "Programar" no detalhe.

## 3. Mapa: geometria que existe no dado sintético

| Entidade | Geometria | Fonte | Recorte honesto |
|---|---|---|---|
| Talhão da Santa Rita | Só o T1 tem "polígono v3 validado". Os demais são desenho demonstrativo (centro e raio pela área) | `gen37/dados.py:126`; `gen37/dados_mip.py:100` | Mostrar a qualidade da geometria (IN-04: "Geometria/localização e sua qualidade", `PRD:407`) |
| Parcela | c1, d1 e e1 validadas; c2 sem polígono | `gen37/dados.py:127` | Sem polígono: aparece na lista como pendência, sem localização inventada (`PRD:7272`) |
| Pivôs da Lagoa Grande (23) | Círculo "centro + área declarada, não polígono validado". O KML real só existe no Mac do proprietário; na nuvem, a versão sintética fica no mar | `gen37/areas/cad_fazendas.py:5-6`; `gen37/dados_lagoa_sintetico/kml.py:1-30` | Rótulo "Demonstração sintética" |
| Talhão desenhado ou importado | Polígono (localStorage) | `gen37/talmapa.js:1-30` | — |
| Pontos de água e outorgas | Ponto (lat/lon) | `kml.py` (`_agua`) | Cadastro da fazenda |
| RL, APP, vegetação | Só área (ha), sem geometria na sintética | `kml.py` (`_ambiental`) | Não desenhar |
| O.S. | Via `talhoes[]`. OB-0104 não tem talhão ("Armazém Sede") | `gen37/dados.py:114-120` | Várias ordens no mesmo talhão: contagem e resumo, nunca a cor da última (`PRD:3008`, OSFASE-06). Sem geometria executada, não pintar avanço (OSFASE-07, `PRD:3024`). Ordem sem talhão vai para "Sem localização" |
| Vistoria | Ponto numerado **sem coordenada gravada**. O GPS do AG-01det é calculado para exibição | `gen37/dados_mip.py:171-176`; `gen37/areas/agronomia.py:875,885` | Só no nível do talhão |
| Ocorrência (CA-03) | Local em texto ("T4 · OS-0420") | `gen37/areas/campo.py:457` | Nível do talhão |
| Máquina | `local` em texto; a telemetria traz só o horímetro | `gen37/dados_cad.py:64-73`; `gen37/dados_manutencao.py:39-41` | **Sem mapa.** "Sem localização confiável, não inventar posição" (`PRD:7505`). Ativo móvel fica na lista sem ponto; ativo fixo aparece na localização conhecida (`PRD:3008`) |
| Software real | Nenhuma geometria: `packages/domain` só tem saldo e unidades | — | Mapa depende de fatia PostGIS que ainda não existe |

**Mapa já tem dono.** A decisão v3.9 é "Não há tabela nem lista abaixo do mapa: lista e Kanban de ordens ficam em Ordem de Serviço" (`PRD:9516`; DEC-2609-06, `PRD:12474`). A O.S. ganhou "Recursos", não "Mapa" (DEC-2609-09, `PRD:12477`). A tela CA-01 antiga tinha Lista · Kanban · Mapa (`campo.py:198`); a atual tem Lista · Kanban · Recursos (`processo_os.py:1232`).

Um "Mapa" dentro da O.S. tem de **reusar o IN-04** (funcionalidade "Ordens de serviço": Fases, Avanço, Atrasos, Impedimentos; `PRD:3002-3010`), sem segundo componente. A O.S. filtra Fazenda **e Safra**, e o Mapa só Fazenda (DEC-2609-11, `PRD:12479`). Então a visão precisa carregar a Safra ou declará-la.

**Talhão:** o CD-01 já tem "Lista | Mapa" e a árvore por fazenda (`cad_fazendas.py:5-7`). A SEL-01 (proprietário, 09/10) pede "fazenda → talhões (mapa e tabela sincronizados)" (`docs/design-system/README.md:24`), e "seleção no mapa e na tabela são a mesma seleção" (`PRD:7272`). Uma alternância exclusiva que esconda a tabela contraria a SEL-01. Precisa decidir.

## 4. Carga por recurso

- **O dado existe** em `gen37/alocacao.py`:
  - 15 recursos: 7 máquinas (com 2 pivôs), 4 implementos e 4 pessoas (`:10`);
  - `ALOC` com O.S., dia, início, fim e situação firme, condicional ou manutenção (`:17-37`), na semana de 22 a 27/09 (`:6`);
  - `conflitos()` (`:44`); `semana()` mede uso, excesso de jornada e ociosos.
- Já está na tela: aba "Recursos" (`processo_os.py:1158,1232`), por DEC-2609-09 (`PRD:12477`).
- O PRD manda um quadro único "Máquinas agora e na programação" nas abas de PL-03/PL-04 e MA-01, sem agenda paralela (`PRD:7487`, RECURSO-10).
- Regras que limitam a visão:
  - **Filtro:** hoje o Recursos "diz que o filtro não se aplica" (`processo_os.py:795`). Para atender "mesmo estado de filtro", o filtro **realça** as ordens filtradas e mostra as demais alocações do recurso como "ocupado (fora do filtro)". Nunca esconde. Dano evitado: recurso ocupado parecer livre e ser alocado duas vezes (RECURSO-06; "não ocultar sobrecarga", `PRD:7451`). O mesmo vale para recurso que atende duas fazendas ou safras (DEC-0910-20, pendente; SAF-C02).
  - "Apto não significa livre; livre não significa compatível" (`PRD:7489`). Trator livre com implemento reservado é conjunto impedido (RECURSO-01). Contadores que se sobrepõem não se somam (`PRD:7499`).
  - Célula vazia não é ociosidade: "Sem apontamento/telemetria atual → estado desconhecido, nunca presumir ociosidade" (`PRD:7442`). Sem ranking punitivo (`PRD:7461`). Custo de pessoa é restrito por permissão (`PRD:1741`).
  - Agregado mensal não resolve conflito no mesmo intervalo (`PRD:7431`).
  - Arrastar uma alocação = simular e depois CMD-34 Publicar alocação (`PRD:2825`): reserva sem sobreposição, conflito vai ao PL-05, nada é liberado. A simulação não move a agenda (ALOC-07). Não retirar recurso de atividade em andamento sem decisão explícita (44.9). **O protótipo não tem validador de realocação** (só detecta conflito), então fica só de leitura.

## 5. Tabela agrupada com subtotal

Regra de base:
- "+ Agrupar por" faz parte do contrato de **toda** tabela.
- "Subtotais somente em medidas aditivas de mesma unidade/base; percentuais, custos por hectare e taxas são recalculados, nunca somados" (`PRD:297`). Total só de medida aditiva da mesma unidade (DS-40, `PRD:14346`).
- No software real isso já existe: `somar` devolve null se as unidades diferem (`apps/web/src/tabela/logica.ts:173`), e `agrupar=` vai na URL (`:227-292`; `Tabela.tsx:537-541`).
- **Portanto a "Tabela agrupada" é um estado da Lista.** O ícone da visão, se existir, liga `agrupar=<padrão da entidade>` no mesmo G2, com uma chave de estado só (AGENTS §3.4).

| Entidade | Agrupar por | Subtotal válido | Subtotal inválido |
|---|---|---|---|
| Estoque (lote), real e protótipo | Produto | Físico e utilizável na unidade-base (`apps/web/src/estoque/lista.ts:13-20`) | Por grupo, estado ou local: unidades misturadas (L, kg, sc), só contagem. R$ só quando houver valoração (o real ainda não tem). Nunca somar depósito com custódia (`PRD:1177`). Bloqueado, quarentena e vencido sem sobreposição (`PRD:1173`) |
| Lançamento de custo (GE-03) | Natureza, centro, cultura, talhão, operação | R$ | R$/ha é recalculado. "Não alocado" fica visível (`PRD:8363`). Relatório por natureza e por operação não se soma (`PRD:8255`). **No protótipo as dimensões estão numa coluna de texto só** ("Soja · T1+T2 · OS-0421", `gen37/areas/gestao.py:273-291`): separar em colunas antes (TABR) |
| O.S. | Fase, talhão, atividade, responsável | Contagem; ha só se todas as linhas estiverem em ha, e então rotular **ha-operação** (`PRD:7292`) | "Não somar hectares com toneladas" (`PRD:2994`). OB-0104 tem `area=None` |
| Demanda de insumos (SAF etapa 6, CMP 2) | Grupo → produto (71.6) | Valor em R$ | Quantidade só por produto |
| Pedidos e compras | Fornecedor, grupo | R$ | Quantidade só por item |

## 6. Árvore

- **Fazenda › setor › talhão: não existe e não deve existir.**
  - O "setor" do talhão é o pivô, a bomba ou o gotejo de irrigação. É opcional e não existe no sequeiro (`gen37/dados_cad.py:22`, `cad_fazendas.py:93`).
  - "Setor hidráulico, zona de solo e parcela produtiva são entidades diferentes que podem se sobrepor… sem tratá-las como sinônimos" (`PRD:7258`; entidades separadas em `PRD:4548`).
  - Como pai, deixaria órfãos os talhões de sequeiro.
- **Árvore certa: Fazenda › Talhão › Parcela.**
  - O CD-01 já é árvore por fazenda, com subtotal por fazenda e sem total que some fazendas (`cad_fazendas.py:7`).
  - A parcela tem vigência por safra, então a folha depende do filtro de safra.
  - Dividir ou unir preserva a linhagem (`PRD:1682`, `PRD:7272`).
- **Centro de custo:** o PRD prevê "hierarquia e vigência" (`PRD:8262`), mas **nos dados é plano**: CR e CC com `sup=''` (`gen37/dados_cad.py:186-189`). Só a **Natureza** tem dois níveis, 3.1 › 3.1.0x (`:179-185`). O CD-07 já é árvore "Dimensão → código" (`cad_produtos_estrutura.py:7`).
  - Hoje dá para fazer Árvore por natureza.
  - Árvore por centro só quando o CD-07 ganhar "superior" para CR.
  - Não derivar o centro da hierarquia física (`PRD:4575`; `PRD:1798`).
- Outras árvores que o dado sustenta:
  - Produto: grupo › item (`cad_produtos_estrutura.py:3`);
  - Estoque: item › lote (`gen37/areas/processo_estoque.py:117-120`);
  - O.S. com várias parcelas (`processo_os.py:1226`);
  - Ativos: ativo › conjunto/componente (MA-01, `PRD:877`; dado a conferir).

## 7. Galeria

Nenhuma entidade tem foto como informação principal.
- **Vistoria:** a decisão vem da contagem por ponto contra o NC (`dados_mip.py:171-176`). As fotos são "2 por ponto coletado", contadas como rótulo e sem arquivo de imagem (`agronomia.py:865,885`).
- **Ocorrência:** a evidência é 1 campo de 7 (`PRD:738`; `campo.py:457`).
- Mancha de satélite é indício (`PRD:411`).
- Com dado sintético, a galeria mostraria marcadores no lugar de fotos (sem imagem real, ENG-017).
- **Recomendação:** sem visão Galeria. As fotos ficam no bloco "Evidências" do detalhe (AG-01det).

## 8. Matriz e Timeline

**Matriz:**
- Já é contrato: operação × mês com alternância para semana (`PRD:7338`), e "uma matriz por atividade/recurso" no Planejar safra (`PRD:10616`).
- Talhão × semana é nova. O valor é número de operações ou **ha-operação**, nunca soma de produtos de unidades diferentes. Separar previsto (projeção do gatilho), emitido e realizado, sem repetir o realizado (`PRD:7292`).
- Só leitura; a célula abre a lista filtrada.

**Timeline:**
- **O.S.:** início e fim existem (`dados.py:116`), e "Janela a definir" vai para uma linha própria.
- **Safra:** tem início e fim, mas são só 3 linhas, e a Safrinha cai dentro da 2026/27 (`gen37/dados2.py:14-17`). Valor baixo.
- **Ocupação dos talhões** (`gen37/ocupacao.py`): é onde o tempo decide. Precisa distinguir a parte certa da estimada ("Livre × A conferir"). "Ciclo mínimo é estimativa; período/safra encerrado não comprova desocupação física" (alinhamento de 08/10, `docs/DECISIONS.md:54-66`).

## 9. Entidade × visões: sugestão corrigida

| Entidade | Sugestão | Corrigido | Motivo |
|---|---|---|---|
| Talhão | Lista, Mapa, Árvore (fazenda › setor › talhão) | Lista em árvore Fazenda › Talhão › Parcela, mais Mapa com tabela sincronizada | Setor não é pai (`PRD:7258`); SEL-01 |
| Safra | Lista, Timeline | Só Lista, portanto **sem seletor**. A Timeline vai para a ocupação | 3 linhas |
| O.S. | Lista, Kanban, Calendário, Carga por recurso, Mapa | Lista; Kanban (5 fases; sem arraste no protótipo); Recursos (= carga por recurso, DEC-2609-09); Calendário só de leitura até haver validador; Mapa = IN-04 "Ordens de serviço" | §1–§4 |
| Atividade/Aplicação | Lista, Calendário, Matriz, Mapa | Não é listagem própria hoje: as ocorrências ficam no Planejar safra, etapa 4, e as aplicações são O.S. com apontamentos. A Matriz já é contrato do Planejar safra; Calendário e Mapa são os da O.S. | Evitar uma segunda fonte (`PRD:2856`) |
| Insumo/Estoque | Lista, Tabela agrupada | Lista com agrupamento (estado do G2); subtotal só por produto | §5 |
| Máquina | Lista, Carga por recurso, Mapa | Lista (ativo › conjunto) e Carga ("Máquinas agora e na programação", `PRD:7487`). **Sem Mapa** | Sem posição (`PRD:7505`) |
| Vistoria/Ocorrência | Lista, Mapa, Galeria | Lista; Mapa no nível do talhão (IN-04 "Pragas e doenças"); Calendário só para a vistoria programada. **Sem Galeria** | §3, §7 |
| Lançamento de custo | Lista, Tabela agrupada, Árvore (centro de custo) | Lista com agrupamento por dimensão (R$; R$/ha recalculado; "Não alocado" visível) e Árvore **por natureza**. Árvore por CR fica adiada | §5, §6 |
| OM e Beneficiamento | — | Mesmo Kanban de 5 fases (PCM D-07: "Sem ordem" é visão própria, nunca bandeja) | `PRD:2881-2889` |

## 10. O que NÃO deve virar visão

- **Kanban por selo ou condição** (Pausada, Impedida, Parcial): selo não vira coluna (`PRD:2984`, UIREL-02).
- **Kanban por integração ERP:** é proibido (INTEG-27).
- **Kanban de lote:** o estado de qualidade é uma dimensão, e mudá-lo exige laudo (`cenLiberarQuarentena`, `cenario.js:130`; CMD-24).
- **Documentos com ciclo próprio** (compra, venda, requisição, expedição): não se transformam em O.S. (`PRD:2881`).
- **Calendário editável de fatos** (apontamento, início, término).
- **Calendário de Safra:** é um período, não uma agenda.
- **Mapa de Máquina, de Estoque ou de Custo na listagem:** máquina e estoque não têm posição. Custo já é funcionalidade do IN-04.
- **Galeria** (§7).
- **Árvore fazenda › setor › talhão.**
- **Árvore de CR antes de existir o "superior" no CD-07.**
- **"Tabela agrupada" como componente separado do G2.**
- **Matriz que some produtos ou unidades diferentes.**
- **Carga por recurso** que esconda ocupação fora do filtro ou que vire ranking de pessoas.

## 11. Conflitos a registrar ou decidir antes do código

1. **Só ícone:**
   - O pedido contraria "Ícones não substituem rótulo" (`PRD:291`) e BOT-05, "sempre com rótulo" (`README:14`).
   - A VIS-04 admite dica para "ícones sem texto" (`README:30`), e o menu recolhido (DS-28) é precedente.
   - **Registrar como decisão do proprietário de 10/10** em `docs/DECISIONS.md`, refinando 4.2 e DS-57.
   - No toque não há dica (VIS-04), então o menu "mais" precisa mostrar o nome em texto.
2. **Papel ARIA:**
   - A DS-57 diz "Visões alternativas (Kanban, Recursos) são abas do mesmo bloco" (`PRD:14541`). Aba usa `role=tab` e `aria-selected` (DS-36, `PRD:14304`).
   - O pedido usa `aria-pressed`, que é a variante segmentada da DS-36, também válida (`PRD:14209`).
   - Escolher uma das duas e registrar.
3. **Desfazer** (§0.2): trocar por confirmação antes do efeito (DS-44, `PRD:14386`), e oferecer desfazer só onde existe comando inverso legítimo.
4. **"Aprovar e liberar" composto no protótipo** (`processo_os.py:44-51,327-343`): diverge do PRD e está pendente (DEC-0910-15, `DECISIONS.md:129,158`). Nenhum arraste pode cair nele.
5. **Mapa na O.S. × IN-04** (DEC-2609-06 e 09): a visão reusa o IN-04, ou o proprietário reabre a decisão.
6. **Talhão Lista | Mapa exclusivo × SEL-01 sincronizado.**
7. **Calendário e alocação sem validador** no protótipo: ficam só de leitura até existir o serviço único.
8. **Atalhos 1…9:** o projeto não tem atalho de dígito, só Enter, Esc e setas (`gen37/g2lib.js:73-76,174,247,293`). Pela condição do próprio pedido, não aplicar (WCAG 2.1.4 exigiria poder desligar ou remapear).
9. **Ação primária:** fica "Criar ordem" (BOT-03; nunca "Nova") no cabeçalho, igual em todas as visões. O Mapa do IN-04 não tem primário (DS-62), mas dentro da O.S. vale o primário da listagem.

## 12. Requisitos de teste que saem desta lente

- **Unidade:**
  - Matriz de drop (de, para) → "recusa com motivo e quem resolve" ou "comando X". Nenhum drop gera CMD-42. Água sem produto não é arrastável. Saltos são recusados.
  - Visões válidas por entidade (tabela do §9).
  - `?view=` inválido ou sem permissão abre a Lista com aviso visível, sem escolher outra visão em silêncio (análogo à SEL-02, `README:25`).
  - Soma nula com unidades mistas (já existe, `logica.ts:173`).
- **Ponta a ponta:**
  - Filtro de fase "Liberadas" deixa a Lista e o Kanban com a mesma contagem. É a regressão de "lista 2 ordens, Kanban 10" (`processo_os.py:794`).
  - Recursos com filtro não mostra recurso ocupado como livre.
  - OS-0422 sem janela aparece em "Sem data".
  - Em 390 px, o Kanban vira seletor de etapa com lista vertical (`PRD:2992`).
