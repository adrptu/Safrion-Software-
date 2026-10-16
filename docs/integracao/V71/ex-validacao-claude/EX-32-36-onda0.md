# EX-32 a EX-36 (Onda 0) · reprodução do Claude no protótipo

> Só leitura, render limpo ff3903d/ba0e994, dados sintéticos. Agente de reprodução do Claude, 16/10/2026. Insumo para a classificação conjunta com o Codex (6215503388, 6216511997, 6217217024).

Trabalho só de leitura: não editei nada no repositório nem fiz commit.

### Versão e escopo

- **Código lido:** /home/user/sp-v69/tools/prototipo/v37/gen37 (e37080a). Abaixo chamo essa pasta de **G**, e as linhas citadas são dela.
- **Navegador:** usei o render /tmp/claude-0/v69b/tools/prototipo/v37/gen37/_render. Versão validada: **ba0e994**.
  - Das 13:35 às 13:42 UTC rodei EX-33 e EX-34 no render ba0e994 (montado às 13:30:41). Conferi o md5 antes e depois: não mudou.
  - Às 13:42:56 o render foi remontado em **ff3903d**. A diferença para ba0e994 é só o CSS dos menus flutuantes (`engine.py` box-sizing e `g2lib.js` posição do filtro), sem efeito nas regras reproduzidas. EX-35, EX-36 e a reexecução de EX-32 (13:45 às 14:06) rodaram nesse render.
  - A primeira passada de EX-32 (13:23 às 13:27) rodou no render anterior. As telas eram as mesmas e repeti tudo depois com o mesmo resultado.
- **Diferença a156f83 → ba0e994:** não mexe em nenhuma tela citada; só IN-04/osAb e frentes MAPA/D5/TAB-08.
- **Perfis usados:** Ana (gestora e agrônoma), Caio (PCP, não agrônomo), Rui (almoxarife). Não existe perfil "Marcos" no seletor.
- **Severidade:** dou duas. **P** é o dano no protótipo como está. **R** é o dano se o comportamento for levado ao produto.
- **Achado de contexto, decisivo:** quase todas as telas citadas estão fora do menu ("módulos ocultos", `ui37.oculto()`). Exceções: GE-02, GE-08, AG-01, CD-04/CF-01, IR-01/02/03det, EST e OS.
  - As telas ocultas só abrem por link a 1–5 saltos do menu. PT-06 e MB-08 não têm link nenhum (só URL ou canvas).
  - A maioria só mostra mensagem fixa (`msgbtn`/`imsg`) ou guarda estado só na página, sem gravar no cenário compartilhado.

### EX-32 Aprovação em lote

| Sub-item | Reprodução | Origem | Classificação | Severidade e dano | Correção mínima | Teste de regressão |
|---|---|---|---|---|---|---|
| PL-04 "Liberar prontas" | Com Ana e com Caio, o clique mostra o **mesmo texto**: "Liberada 1 de 5… OS-0430 ✓ liberada por Ana (agrônoma)…". Cenário inalterado (só a chave do perfil no localStorage). Na O.S., a OS-0430 continua "A liberar", sem CMD-42 registrado. **Respostas às perguntas:** (1) a OS-0430 (Glifosato 480, 2,4-D, óleo) **não tinha** aprovação individual antes do lote; (2) o texto implica que o agrônomo libera, e no modelo do protótipo isso é aprovar e liberar juntos, mas nada é gravado; (3) o ator do "recibo" é fixo ("Ana") mesmo com Caio clicando; (4) sim, entra O.S. com produto sem aprovação. **Contraste:** em OS.dc, Caio é recusado ("o perfil Caio · PCP não tem esses papéis"); Ana grava, por O.S., "v1 aprovada por Ana (agrônoma) (CMD-42)" e "v1 liberada por Ana (gestora) (CMD-06)". | G/areas/planejamento.py:438-440 (texto fixo); o caminho correto está em G/areas/processo_os.py:404-457 e G/g2lib.js:707-708 | **Confirmado como mensagem falsa; sem efeito gravado** | P: S3 (diz que liberou defensivo, em nome de outra pessoa, sem aprovação; o caminho real impede). R: **S1** (execução de defensivo sem CMD-42) | Trocar o texto fixo por um resultado calculado por O.S.: libera só "só água" e O.S. com CMD-42 da versão vigente (`osAprovada`), com o perfil ativo dono da AL-01 (`osc_liberar`). As demais saem "recusada: aguarda aprovação individual · abrir na O.S.". Alternativa: remover o lote e linkar OS.dc. | **Unidade:** cenário semente, Caio → OS-0430 recusada e cenário igual. Após `osc_aprovar` por Ana → grava só CMD-06 com o ator ativo. **Navegador:** Caio em PL-04 → o texto não pode conter "liberada por Ana". A versão atual reprova (texto fixo). |
| CA-01 "Selecionar as 12" + "Liberar selecionadas" | Com Ana e com Caio, 12 linhas marcadas. Mensagem fixa: recusa OS-0418, 0431, 0422 e 0423 por estoque, máquina, janela ou conflito, **omite a OS-0430** e termina com "Com produto, quem libera é o agrônomo". Com só a OS-0415 (encerrada) marcada, o texto é idêntico. Nada é gravado. | G/areas/campo.py:195-197 | **Confirmado como mensagem fixa**; "processa o lote" foi **refutado**, nada é processado | P: S3. R: S1 (lote com O.S. com produto sem aprovação) | Igual à PL-04: resultado por item calculado do cenário e do perfil, ou remover o lote | Marcar só a OS-0415 → o resultado não pode citar OS-0418. Marcar a OS-0430 sem CMD-42 → "recusada: sem aprovação individual". A versão atual reprova os dois. |
| IN-02 "Aprovar selecionados" | Caio (PCP) marca as 4 linhas e aprova: "aprovadas: Ajuste de inventário Galpão 2 (AP-2211); Política de estoque Diesel (AP-2212); Acesso · novo operador Beto (AP-2213)". O orçamento da Direção **não** entra ("exige revisão individual"). Fica só na página: some ao recarregar e não chega a SU-09 nem a CF-01. | G/areas/inicio.py:1665-1690 (`v.lote` sem conferir o perfil; em ba0e994 +1 linha) | **Confirmado em parte**: mistura tipos e não confere quem aprova. "Aprova a Direção" foi **refutado** | P: S3. R: **S1** (concessão de acesso e ajuste de estoque sem alçada, por quem não é gestor) | Conferir `cenExigeAlc` por item. Lote só da mesma alçada e do mesmo tipo. Acesso (AL-13) e ajuste de inventário (AL-09) fora do lote, decididos no módulo de origem (`cenAprovarAjuste`). | Caio aprova o lote → nenhum item aprovado, motivo "papel gestor". Ana → acesso e inventário "decidir no módulo". A versão atual aprova 3 com Caio. |
| CA-03 encerra a OC-114 | Todas marcadas, ou só a OC-114: "OC-114 recusada: a OM-0233 ainda está em execução". Mas o texto é fixo: com só a OC-114 marcada diz "OC-116 encerrada", e a linha não muda. | G/areas/campo.py:478-479; CA-03det :518 ("Indisponível") | "Encerra a OC-114" **refutado**. **Confirmado**: resultado fixo, independente da seleção | P: S3 (resultado falso de item não selecionado). R: S2 se mantido assim | Resultado calculado por item selecionado, ou remover o lote | Marcar só a OC-114 → o texto não pode citar a OC-116. A versão atual reprova. |

### EX-33 Fricção proporcional ao risco

Todos os cliques abaixo foram feitos como Caio, salvo onde indicado.

| Sub-item | Reprodução | Origem | Classificação | Severidade e dano | Correção mínima | Teste de regressão |
|---|---|---|---|---|---|---|
| CO-06det "Liberar" lote reprovado | 1 clique: "Liberado para blend/mercado interno tipo 7 · Recibo QL-1148". Não pede motivo nem confere papel. Mensagem fixa. | G/areas/colheita.py:584 | **Confirmado em parte**: não libera como tipo 6, só para destino compatível (tipo 7). Falta papel e motivo | P: S3. R: S2 (produto fora do padrão liberado por quem não é da Qualidade) | Exigir o papel Qualidade e motivo; recibo com o ator | Caio clica → recusa por papel. A versão atual libera. |
| PT-04det "Recusar crédito" | Diz "Recusa registrada com motivo" sem pedir motivo (portal do credor) | G/areas/parceiros.py:326 | **Confirmado** | P: S3. R: S3 | Abrir o motivo obrigatório antes de registrar | Clicar → aparece o campo de motivo e não registra sem ele. A versão atual registra. |
| GE-05 "Emitir crédito" | 1 clique: "Crédito CR-031 de R$ 885… saldo do título passa a R$ 7.965". Some ao recarregar. | G/areas/gestao.py:433-436, 457 | **Confirmado** | P: S3. R: S2 (baixa de recebível sem alçada) | Alçada por papel e valor (depende de decisão do proprietário), prévia "saldo antes → depois" e Desfazer enquanto não conciliado | Caio clica → recusa. A versão atual emite. |
| LO-04 "Contratar" frete de R$ 1.824 | 1 clique: "Rota Sul contratada · CT-0912 · VG-119". Idempotente. Fica só na página. | G/areas/logistica.py:552-560 | **Confirmado** (o rótulo já mostra valor e prestador) | P: S3. R: S3 | Alçada por valor (decisão pendente "frete") e cancelar antes do despacho | Caio clica → recusa ou pede alçada. A versão atual contrata. |
| AG-06 "Registrar parecer" | Caio grava um parecer técnico pronto ("redução… não atribuída ao produto") | G/areas/agronomia.py:399 | **Confirmado** | P: S3. R: S3 | Usar o campo "Parecer técnico" vazio que já existe no formulário; só agrônomo | Caio → recusa. Ana → exige texto. A versão atual grava o texto pronto. |
| SU-05 "Formalizar contrato" antes da Direção | No SU-04, "Selecionar Fertisul (R$ 360.905) · segue para aprovação: Direção". A nota diz "Alçada: Direção **(até R$ 300 mil)**", e esse texto está errado. No SU-05, Caio formaliza o CT-2026-14 (78,85 t, "Aguardando aceite") sem nenhuma aprovação registrada. | G/areas/suprimentos.py:590 (texto fixo "(até R$ 300 mil)"), 652-664 | **Confirmado** | P: S3 (só na página). R: **S2** (compromisso de R$ 360 mil sem a Direção) | "Formalizar" desabilitado com motivo até haver aprovação da alçada pelo valor (`_alcada`); corrigir a nota | Sem aprovação → botão desabilitado com o motivo. A versão atual formaliza. |
| SU-05 "Emitir pedido" | "PC-095 · 11.000 L contra o CT-2026-03 · emissão automática em 26/09… R$ 64,2 mil de 120 mil". Mensagem fixa. | G/areas/suprimentos.py:671, 135 | **Refutado em parte**: a tolerância "hipótese" não pesa, porque 103 + 11 = 114 de 180 mil L contratados. Resta 1 clique sem alçada nem prévia | P: S4. R: S3 | Prévia e alçada na emissão | Prévia mostra volume e valor antes de agendar. |
| SU-05 "Confirmar fornecedor" | "Fertisul confirmou a carga 3". O PC-094 (Casa das Peças) continua "A confirmar". | G/areas/suprimentos.py:671-681 | **Confirmado** | P: S3. R: S3 | Ação na linha do pedido "A confirmar" | Confirmar → muda o PC-094, não a Fertisul. |
| SU-04 "Enviar COT-113" | "enviada a 3 convidados" sem mostrar os destinatários | G/areas/suprimentos.py:584-588 | **Confirmado** | P: S3. R: S3 | Confirmação listando destinatários, item e quantidade | O diálogo lista os 3 nomes antes de enviar. |
| GE-04 remessa sem prévia | 1 clique: "REM-2609-02 enviada · Fertisul PC-088 R$ 233.000". A NF 8790 fica de fora (aguarda alçada). | G/areas/gestao.py:370-373, 388 | **Confirmado**: só títulos aprovados entram, mas sem prévia e sem conferir o papel | P: S3. R: S2 (envio irreversível ao banco) | Prévia (títulos, total, conta) e papel de pagamento | Clique → abre a prévia com R$ 233.000; Caio é recusado. |
| SU-08 "Registrar perda" | Rui escolhe o aprovador ("Gerente da fazenda"), submete a PE-013 e **ele mesmo** clica "Aprovar perda". Resultado: "PE-013 aprovada por **Ana (gestora)** · 5 kg baixados". Some ao recarregar. | G/areas/suprimentos.py:1048-1050 (aprovador escolhido por quem pede), 1085 (nome fixo) | **Confirmado** | P: S3. R: **S2** (autoaprovação e autor falso na baixa de estoque) | Aprovador sai do valor ou da alçada; quem pede não aprova; recibo com `g2ator` do perfil ativo | Rui aprova a própria PE → recusa. A versão atual grava "por Ana". |
| GE-08 "Autorizado pela Direção" | Caio clica "Autorizar bloco" e recebe "Autorizado pela Direção · Banco Terra acessa 'Compromissos e garantias'" | G/areas/gestao.py:630-632 | **Confirmado** (a análise citou Ana; reproduzi com Caio) | P: S3. R: **S1** (dado financeiro liberado a terceiro sem alçada, com autor falso) | Exigir o papel Direção e gravar o ator real; sem titular, desabilitar com motivo | Caio → recusa. A versão atual autoriza. |
| CD-04 "Liberar O.S. (agrônomo)" | Ana marca a opção para Caio. O formulário mostra "Exige CREA com validade… Pendente: grava, mas a pessoa fica não alocável". Salvar → "não alocável… CREA pendente". Nada vai para o CF-01 (fica só na página). No CF-01, o papel de agrônomo de Caio está desabilitado: "Agrônomo só com CREA válido no cadastro (lei…)". | G/areas/cad_ativos_pessoas.py:29-34; G/configuracoes.js:66; G/areas/configuracoes.py:121 | **Refutado** (não é livre). Resta S4: o nome contraria "aprovar ≠ liberar" | P: S4. R: S4 | Renomear para "Aprovar O.S. (agrônomo)" | Varredura de textos sem "Liberar O.S. (agrônomo)". |
| PL-06 publica "aguardando aprovação" | "Parcelamento v2 publicado…" e o cabeçalho continua "Proposta v2 aguardando aprovação". Caio pode publicar. Mensagem fixa. | G/areas/planejamento.py:144, 621 | **Confirmado** | P: S3. R: S3 | "Publicar" desabilitado com motivo até a aprovação | Com status "aguardando" → botão desabilitado. |
| Publicações sem Desfazer | Plano v4 (PL-02: "alçada da agronomia", publicado por Caio), ajuste do T1-A (PL-02det: Cletodim 0,36 L/ha, por Caio), cenário (PL-03), previsão V2 (GE-02, no menu). Todas com texto fixo, sem Desfazer e sem conferir papel. | G/areas/planejamento.py:140-145, 368; G/areas/gestao.py:210 | **Confirmado** | P: S3. R: S3 (o ajuste de dose por PCP fica mitigado porque a O.S. só muda quando o agrônomo libera) | Papel conferido e "Voltar à versão anterior" (republicar a anterior). Observação: o UX-04 do PRD trata de linha clicável; **não há regra de Desfazer no design system**, isso exige decisão nova | Caio publica o plano → recusa. |

### EX-34 Medida e evidência pré-preenchidas

| Sub-item | Reprodução | Origem | Classificação | Severidade e dano | Correção mínima | Teste de regressão |
|---|---|---|---|---|---|---|
| CA-03 "Evidência: Foto" | Registrar ocorrência vem com Evidência = "Foto". Não há campo de anexo. Salvar grava a OC-117 com "Foto" sem foto nenhuma. | G/areas/campo.py:475 (`def:'Foto'`) | **Confirmado** | P: S3 (fato registrado falso). R: S3 | Sem valor padrão; foto como anexo | Abrir → Evidência vazia; salvar sem escolher → recusa. A versão atual grava "Foto". |
| LO-02det "Foto do lacre anexada" | O select **mostra** a opção (a única) e "Portaria (Jair)", mas Salvar recusa: "Informe conferido por. Informe evidência." O estado está vazio. | G/areas/logistica.py:396 + motor G/g2lib.js:670 (select sem opção vazia) | **Refutado quanto a gravar**. **Confirmado**: o select engana visualmente e a evidência é declaração sem anexo | P: S3. R: S3 | Opção vazia "Escolha…" em todo select obrigatório sem padrão (no motor); lacre com anexo | Abrir → select mostra "Escolha…". A versão atual mostra a 1ª opção. |
| SU-07det "Quantidade medida" = 10 | Rui abre "Receber devolução" com 10 já preenchido e confirma sem mexer: "10 sc… custódia de Paula 10 → 0". Fica só na página (tela oculta). | G/areas/suprimentos.py:959 (`def K0`) | **Confirmado** | P: S3. R: S2 | Campo vazio, com "em custódia: 10 sc" como dica | Abrir → campo vazio; confirmar vazio → recusa. |
| **EST "Receber devolução"** (fluxo real, no menu; a análise não citou) | REQ-031 abre com Quantidade conferida = **500** (a custódia) e Condição "Apta". Salvar sem mexer **grava no cenário**: MV "devolucao 500 kg apta", custódia 500 → 0, "encerramento liberado". | G/areas/processo_estoque.py:517 (`qtd: … it.custodia`, `cond: conds[0]`) | **Confirmado** | **S2** (saldo e custódia sem medição; uma perda some e a O.S. pode encerrar) | Quantidade vazia (custódia na dica); condição sem padrão | Abrir a REQ-031 → qtd vazia; salvar → recusa; `movs` inalterado. A versão atual grava MV de 500 kg. |
| PL-02 "Realizada" | O select mostra "Realizada", mas Salvar recusa: "Informe decisão da pendência". | G/areas/planejamento.py:237 + G/g2lib.js:670 | **Refutado quanto a gravar**. **Confirmado** o engano visual (mesmo defeito do motor) | P: S3. R: S3 | A mesma opção vazia no motor | O mesmo teste do LO-02det. |
| MB-04 "Equipamento" | O tipo vem "Equipamento" (marcado) e Registrar recusa: "Escolha a máquina". | G/areas/mobile.py:680 | **Confirmado** | S4 (fricção; pode desviar o tipo para Manutenção) | Tipo sem padrão | Abrir → nenhum tipo marcado. |

### EX-35 Listas fora de contexto ou de organização

**Causa comum:** G/engine.py:655-701. A função `_opts_for` acrescenta listas globais fixas (`OPTIONS[...]`) a todo campo de painel cujo rótulo contenha "responsável", "tipo", "variedade", "máquina", "lote", "método" ou "produto".

| Sub-item | Reprodução (opções exibidas) | Origem | Classificação | Severidade e dano | Correção mínima | Teste de regressão |
|---|---|---|---|---|---|---|
| PT-06 | Portal **Fertisul**, "Criar ação interna" → Responsável: Diego Prado, **Ana, Marcos, Rui, Paula**. A tela não tem link de nenhuma página (só URL ou canvas). | G/areas/parceiros.py:422 + G/engine.py:692 | **Confirmado** (exposição entre organizações na própria tela do fornecedor) | **S1 pela regra**. Dano real hoje nulo (nomes sintéticos fixos do motor). R: S1 | `_opts_for` não acrescenta listas globais: só o valor dado e "Buscar no cadastro…", com origem por contexto ou organização | Varredura de painéis (como ex35_scan2.py): PT-06 Responsável sem Ana/Marcos/Rui/Paula. A versão atual reprova. |
| CO-06 | "Inspecionar lote" → Lote: L39-120, **F26-02, D26-11** (insumos), L27-…; Método: pano-de-batida, armadilha, saturação por bases, SMP… | G/areas/colheita.py:538 + motor | **Confirmado** | S3 | Mesma correção no motor | A lista não contém F26-02 nem métodos de MIP ou solo. |
| CO-02 | "Preparar ordens" → Máquinas: Trator, **Pulverizador, Plantadeira**, Colhedora… | G/areas/colheita.py:243 + motor | **Confirmado** | S3 | idem | Sem Plantadeira nem Pulverizador. |
| PL-06 | "Simular parcelas" → Variedade A/B: 58 W, M 5947, BRS 7380, **Tainung 01 (mamão)**, Aliança. Talhão: T5, T7 (mamão). | G/areas/planejamento.py:601 + motor | **Confirmado** | S3 | idem | Sem Tainung 01. |
| PL-05 | "Reprogramar saldo" → Máquina: **Trator 01 · JD 6M 155** (o T1 bloqueado pela OM-0233) | G/areas/planejamento.py:501 + motor | **Confirmado** | S3 | idem; máquina bloqueada desabilitada com motivo | Trator T1 ausente ou desabilitado. |
| CA-01det | "Ajustar produtos e doses do saldo" → Produto: Fungicida A, **Soja em grão, Milho em grão, Mamão cx, Café beneficiado** | G/areas/campo.py:274 + motor | **Confirmado** | S3 (o ajuste real é feito em OS.dc) | idem | Sem grãos. |
| AG-01 "Programar vistoria" | Abre em **Lagoa Grande** (padrão sem contexto do mapa) e lista os pivôs dessa fazenda. Com filtro Santa Rita, lista T1–T4, P1, P2, T7 e C1. | G/areas/agronomia.py:542 (`agFaz`, padrão 'Lagoa Grande'), 735-744 | **Refutado** (a lista segue a fazenda da tela). Resta S4: padrão fixo Lagoa Grande | S4 | Herdar a fazenda do contexto global | Sem contexto → a fazenda do topo. |
| EST NF 4533 → PC-096 | Rui abre a NF 4533 (semente 58 W, Coop. Vale, 20.000 kg) e troca Pedido para **PC-096 · Caixa de mamão (Embalagens Açu)**. Com 1.000, **grava no cenário**: "1.000 un de Caixa de mamão… no lote S58-0926 · disponível 540 → 1.540 un" (MV-1001). Só recusa acima do saldo do pedido. | G/areas/processo_estoque.py:87 (Pedido editável na NF já vinculada), 372-376, 309-317 | **Confirmado** | **S2** (entrada de item, fornecedor e unidade errados no saldo compartilhado; caixa fantasma, que pela leitura do código pode destravar ordem do BEN em dados_ben.py:55-58) | Pedido só leitura na NF já vinculada; se trocar, conferir fornecedor e item NF × pedido e exigir "Item diferente do pedido" (que recusa) | Trocar para PC-096 e salvar → recusa e `movs` inalterado. A versão atual grava MV-1001. |
| Portal, tipo de documento | PT-05det "Enviar documento da carga 3" → Tipo: NF-e, **Preventiva, Preditiva, Corretiva, Melhoria** | G/areas/parceiros.py:395 + motor | **Confirmado** | S4 | Correção do motor | Tipo sem "Preventiva". |

### EX-36 Integridade da irrigação

| Sub-item | Reprodução | Origem | Classificação | Severidade e dano | Correção mínima | Teste de regressão |
|---|---|---|---|---|---|---|
| IR-01, −3,8 % com tolerância de 3 % | O painel mostra "MEDIDO 1.206 m³ · −3,8 %" e a leitura já vem preenchida (1.206). "Validar e encerrar" fecha a OS-0394 ("Hidrômetro prevaleceu"). **Rui (almoxarife) também consegue.** Não pede motivo. | G/irrigacao_estado.js:457-468; G/areas/irrigacao.py:456, 482 | **Confirmado** (o balanço usa o medido, o que está correto) | S3 (divergência encerrada sem motivo e sem papel) | Acima da tolerância: primária "Aceitar com motivo" (papel irrigante ou gestor) e secundária "Devolver para conferir o hidrômetro" | Rui → recusa; Ana sem motivo → recusa. A versão atual encerra. |
| MB-08, 14,47 % e "volta completa" | Tela estática, oculta e sem link. O recibo diz "10,81 mm nos 80 ha (volta completa)". | G/areas/mobile.py:961-1006 | **Confirmado na tela** (não alcançável pela navegação) | P: S4 | Ver a linha abaixo (fluxo real) | — |
| **IR-03det término** (fluxo real, no menu) | "Iniciar irrigação" (20:02) e logo depois "Confirmar término": o padrão é **"Volta completa · 80 ha"** com o hidrômetro **já preenchido** (8.480 m³, constante da semente). Confirmar → "OS-0419 conferida e encerrada · 10,6 mm no setor". Balanço creditado e déficit 11,2 → 1,7 mm, minutos após o início. A "leitura" de parada parcial é derivada da estimativa (0,985 ×), então a conferência automática nunca diverge. | G/areas/irrigacao.py:481 (`full:true`, `vol:irrTele`), 570; G/irrigacao_estado.js:418, 425-455 | **Confirmado** | **S2** (balanço hídrico falso: a próxima necessidade sai subestimada e a lavoura fica sem água; dado "medido" fabricado) | Sem padrão na área (antes do fim previsto, "Término antecipado" com área real); leitura vazia, nunca derivada da estimativa (no protótipo, rotular "simulado") | Iniciar e logo confirmar término → recusa sem área e leitura informadas. A versão atual encerra e credita. |
| IR-02, lâmina abaixo do mínimo do pivô | O número não é "2 mm". Santa Rita, Pivô 2: "2 de **6,22 mm** · 8,3 h por passada", contra a ficha de 6,7 mm e 9 h a 100 % (G/dados.py:52). Lagoa Grande, PV19: "1 de **2,82 mm** · 6,3 h"; pela ficha demonstrativa a 100 % dá cerca de 7,2 mm e 16 h (calculado de G/dados_irrigacao.py:138-140). | G/irrigacao_estado.js:120-124 (`irrNec` sem o piso da ficha), 362; G/areas/irrigacao.py:346-348. O `irrPerc` (131-147) já tem o piso, mas não é usado aqui | **Confirmado**, com o número corrigido | **S2** (plano fisicamente impossível; volume e duração errados. Por inferência, não reproduzido: a conferência da outorga usa o volume planejado) | Programar com lâmina por passada ≥ lâmina a 100 % e duração ≥ volta a 100 %, ou bloquear com motivo | PV19 → lâmina por passada ≥ 7,2 mm ou bloqueio. A versão atual propõe 2,82 mm. |
| IR-03det, início às 20:02 na ponta | O chip **"Ponta parcial (20–21 h)"** aparece sob Janela antes e depois de iniciar. Pela regra, é aviso de custo e não trava. | G/irrigacao_estado.js:195-198, 262 | **Refutado** (o aviso existe). Resta S4: o toast de início não repete o aviso | S4 | Opcional: repetir o aviso na confirmação | — |

### S1 e S2 confirmados, em ordem de prioridade

**No fluxo real (menu, gravam no cenário compartilhado):**
1. **S2 · IR-03det término.** "Volta completa" e leitura pré-preenchidas encerram e creditam o balanço minutos após o início.
2. **S2 · EST, NF ligada a pedido errado.** A NF 4533 vira 1.000 caixas no lote de semente.
3. **S2 · EST, devolução pré-preenchida.** 500 kg "Apta" em 2 cliques zeram a custódia.
4. **S1 pela regra no PT-06, S3 nos demais · motor `_opts_for`.** Uma correção resolve 8 itens do EX-35. Esforço mínimo.
5. **S2 · IR-02.** Lâmina e duração abaixo do mínimo físico do pivô.

**S1/S2 só se levados ao produto** (hoje são telas ocultas, com texto fixo ou estado só na página): PL-04 e CA-01 (S1), IN-02 (S1, acesso e inventário), GE-08 (S1), SU-05 sem a Direção, SU-08, GE-05, GE-04, SU-07det e CO-06det (S2). Recomendo desligar esses botões ou ligá-los ao fluxo real antes de reaproveitar qualquer tela.

### O que a análise errou

- **PL-04 e CA-01 "reproduziu":** nada é processado. São textos fixos, iguais para Ana e Caio. A OS-0430 continua "A liberar" e o fluxo real (OS.dc) exige aprovação individual com alçada.
- **CA-03:** a OC-114 é recusada, não encerrada. O defeito é o texto fixo.
- **IN-02:** o orçamento da Direção não entra no lote. O problema é não conferir o perfil.
- **CD-04:** exige CREA. O papel de agrônomo no CF-01 só existe com CREA válido.
- **AG-01:** a lista segue o filtro de fazenda.
- **IR-03det:** o aviso de ponta existe.
- **IR-02:** o valor é 6,22 ou 2,82 mm, não "2 mm".
- **SU-05 "Emitir pedido":** a tolerância não pesa, o pedido está dentro do volume contratado.
- **CO-06det:** libera só para o tipo 7, não como tipo 6.
- **LO-02det e PL-02:** não gravam sem escolha; é defeito visual do select do motor.
- **"UX-04":** no PRD é outra regra (linha clicável de tabela); não existe regra de Desfazer no design system.
- **Contexto ignorado:** a análise tratou telas ocultas e estáticas como fluxos ativos.
- **Deixou de fora** os três S2 do fluxo real: IR-03det término, EST devolução e EST NF↔pedido.

### Scripts e capturas

Todos estão em docs/integracao/V71/ex-validacao-claude/onda0/

**Scripts**
- Biblioteca: docs/integracao/V71/ex-validacao-claude/onda0/o0lib.py
- EX-32:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_pl04.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_ca01.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_in02.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_ca03.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex_final.py (reexecução em ff3903d e contraste com OS.dc)
- EX-33:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_cd04.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_pub.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_pub2.py
- EX-34:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_est.py
- EX-35:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_scan2.py
  - docs/integracao/V71/ex-validacao-claude/onda0/dbg_pt06.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_ag01.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_est.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_pt.py
- EX-36:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir02b.py
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir02c.py

**Capturas principais**
- EX-32:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_pl04_Caio_ba0e994.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_ca01_Caio_ba0e994.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_ca01_so0415.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_os0430_Caio.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_os0430_Ana.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_in02_Caio_ba0e994.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex32_ca03_so114_ba0e994.png
- EX-33:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_su05_caio.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_su08_aprovada_rui.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_ge08_caio.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_cd04_marcado.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_cf01_caio.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex33_pub_PL-06.png
- EX-34:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_ca03_salvo.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_lo02det_form.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_su07det_confirmado.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_est_devolucao_salva.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_pl02_form.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex34_mb04_inicial.png
- EX-35:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_PT-06_drawer.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_PL-06_drawer.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_ag01_prim_santarita.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_est_nf4533_pc096.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex35_pt05det_tipo.png
- EX-36:
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir01_painel.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir03det_termino_painel.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir03det_terminada.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir02_lagoa.png
  - docs/integracao/V71/ex-validacao-claude/onda0/ex36_ir02_programar.png

### O que não verifiquei

- Os números do IR-02 Lagoa a 100 % (cerca de 7,2 mm e 16 h) são cálculo meu a partir da fórmula da ficha demonstrativa; a tela não mostra esses valores.
- O impacto na outorga é inferência a partir do código; não reproduzi.
- Não verifiquei se o select do design system dispara a troca ao clicar na opção que já aparece (PL-02 e LO-02det).
- Não verifiquei o Desfazer das publicações da nova geração (PA, AL-18).
