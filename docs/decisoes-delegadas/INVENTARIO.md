# Inventário das decisões que esperam o proprietário

**Data:** 09/10/2026, depois da mensagem do proprietário "voce e codex tomem todas deciões por mim, estarei fora". **Autor:** Claude (subagente). **Rótulo:** levantamento por leitura; nenhuma decisão foi tomada aqui e nenhum repositório foi alterado.

**Limite da delegação usado na coluna Limite:**
- **DENTRO**: decisão de produto, regra, desenho, prioridade, escopo, valor-padrão ou parâmetro. Claude e Codex decidem, de forma reversível ou parametrizada.
- **DENTRO · fato da fazenda**: não é decisão; é um dado da realidade. Vale o padrão seguro já em uso, marcado "a confirmar com o dado real".
- **FORA · aguarda o proprietário**: conta, custo, contrato, dado real de cliente, ERP real, publicação a usuários reais, produção, configuração de segurança ou aceite humano dele. Fica registrado sem bloquear o resto.

**Totais:** 130 itens, depois de juntar repetições. DENTRO: 114, dos quais 16 são fato da fazenda. FORA: 16.

| Domínio | Itens | FORA |
|---|---|---|
| Agronomia e lei | 9 | 0 |
| Operação e O.S. | 18 | 0 |
| Suprimentos e custos | 15 | 1 |
| Manutenção | 10 | 1 |
| Produção e comercial | 15 | 0 |
| Irrigação e água | 4 | 0 |
| Plataforma, acesso e design | 49 | 10 |
| Processo e prioridade | 10 | 4 |

**Como ler as fontes:** `main:` é a `origin/main` em `5831eb3`; `sp-xxx:` é a worktree `<sp-xxx>` no HEAD do dia; `scratchpad/` é a pasta desta sessão. Linha = número no arquivo naquela base.

## Itens FORA da delegação (aguardam o proprietário)

| ID | Pergunta | Por que fica com ele |
|---|---|---|
| EXT-01 | Criar a conta de faturamento e o projeto do Google Cloud e provisionar a homologação hospedada? | Cria conta e gera custo em nome dele (login, termos, cartão) |
| EXT-02 | Configurar o teto de gasto nativo do Cloud Run na conta de faturamento? | Mexe em faturamento da conta dele |
| EXT-03 | Contratar hospedagem do piloto (≈ US$ 112 a 183/mês) e domínio próprio? | Gera custo mensal e contrato |
| EXT-04 | Contratar ou licenciar o SonarQube (gate externo de qualidade, ENG-018)? | Licença e conta com custo |
| EXT-05 | Contratar revisão humana qualificada (segurança e arquitetura) antes do piloto? | Contrata profissional e gera custo |
| EXT-06 | Instalar o Docker Desktop no Mac dele (licença depende do porte da empresa; pede a senha do Mac)? | Licença conforme o porte da empresa e senha da máquina dele |
| EXT-07 | Integrar de verdade com o ERP (Sankhya ou TOTVS), com credenciais e sandbox, e ler QR/DANFE ou SEFAZ? | Integração com ERP real e credenciais |
| EXT-08 | Fornecer os dados reais da implantação: empresas, fazendas, culturas, protocolos com responsável técnico, plano de contas, alçadas reais, crédito, retenção e conectividade (PRD 20.6)? | Dado real de cliente e da empresa |
| EXT-09 | Publicar para usuários reais, iniciar o piloto e aceitar a candidata de produção? | Publicação a usuários reais e produção exigem aceite explícito dele |
| EXT-10 | Que perfil de atendimento prometer no piloto (disponibilidade, plantão, horário de reconhecimento) (PEND-OP-01)? | Compromisso de serviço com clientes reais e custo de plantão |
| EXT-11 | Quais provedores, contrato de dados, local de processamento e orçamento do assistente de IA (PEND-IA-01)? | Contrato com terceiros, dados e custo |
| EXT-12 | Aceitar, como usuário, as fatias do protótipo na homologação (ex.: cadastros com seleção que abre detalhe)? | Aceite humano dele; os agentes nunca o declaram em nome dele |
| EXT-13 | Preços, mínimo, franquias, número de planos, trial, retenção e calendário de cobrança do agricultor e dos parceiros (DEC-05, DEC-09)? | Valor comercial que vira contrato com clientes reais em nome dele |
| EXT-14 | Contratar ferramenta de atendimento de mercado ou fazer tela interna para os chamados (PEND-FB-05, proposta)? | Ferramenta de mercado gera conta e custo (a tela interna seria decisão dos agentes) |
| EXT-15 | Aceitar consignação de peças caras oferecida por fornecedor real? | Contrato com fornecedor real |
| EXT-16 | Enviar mensagens reais (convite por e-mail ou WhatsApp) no software real? | Mensagem real a pessoas |

## Agronomia e lei

### AGR-01

- **Pergunta:** Adotar a pré-autorização por limiares, em que o agrônomo aprova de uma vez as O.S. mecânicas sem insumo que repetem o plano (PEND-01)?
- **Opções levantadas:** Adotar o envelope completo de 73.12.1 (até 30 dias, lista fechada, amostragem de 10 %); Recusar; Adiar até medir a fila do agrônomo no piloto.
- **Padrão atual:** Aprovação individual (CMD-42) para toda O.S. agrícola, inclusive mecânica, exceto água sem produto (APROV-16); nada no protótipo.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13675`, `main:docs/PRD.md:13693`, `main:docs/PRD.md:13462`, `main:docs/DECISIONS.md:47`.

### AGR-02

- **Pergunta:** Gessagem e diagnóstico de subsuperfície: habilitar a fórmula ou mantê-la só como demonstração até haver protocolo com fonte e responsável técnico (DEC-08)?
- **Opções levantadas:** Só com protocolo curado, fonte, escopo e casos homologados; Demonstração rotulada (como hoje); Desligar.
- **Padrão atual:** Gatilho Ca < 0,5 ou m > 20 % com laudo de 20–40 cm, rotulado demonstração; fórmula não habilitada para uso real.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10504`, `main:docs/PRD.md:10474`, `main:docs/DECISIONS.md:45`, `sp-solo:docs/analise-solo/DECISOES.md:11`.

### AGR-03

- **Pergunta:** Qual tabela regional de calagem e adubação (fonte, edição, cultura e região) a análise de solo usa para sugerir dose?
- **Opções levantadas:** Tabela oficial do estado de cada fazenda, escolhida com responsável técnico (verificar edição vigente); Manter a regra de demonstração; Desligar as sugestões.
- **Padrão atual:** Regra de demonstração rotulada "tabela regional a decidir pelo proprietário": só Soja e Mehlich-1, V2 60 % (Mamão 70 %); sem laudo vale a dose do plano.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-solo:docs/analise-solo/ESPECIFICACAO.md:156`, `sp-solo:docs/analise-solo/ESPECIFICACAO.md:245`, `sp-solo:docs/analise-solo/ESPECIFICACAO.md:422`, `sp-solo:docs/analise-solo/DECISOES.md:10`.

### AGR-04

- **Pergunta:** Ampliar a análise de solo para laudo por zona e taxa variável, comparativo completo com leitura automática de laudo (OCR) e propostas de corretivos na Compra?
- **Opções levantadas:** Fazer agora; Deixar para o software real; Fazer só o laudo por zona com média ponderada.
- **Padrão atual:** Fora; laudo por zona não sugere dose; calcário aparece "Sem fornecedor homologado".
- **Limite:** **DENTRO**.
- **Fontes:** `sp-solo:docs/analise-solo/ESPECIFICACAO.md:424`, `sp-solo:docs/analise-solo/ESPECIFICACAO.md:426`, `sp-solo:docs/analise-solo/ESPECIFICACAO.md:432`, `sp-solo:docs/analise-solo/DECISOES.md:23`.

### AGR-05

- **Pergunta:** Por quanto tempo cada fonte de dado (sonda, clima, previsão, telemetria, vistoria, satélite, análise de solo e foliar) conta como atual numa recomendação (PEND-13)?
- **Opções levantadas:** Valores da tabela de 73.7.8 (sonda 24 h, previsão 12 h, telemetria 15 min, vistoria 7 d, satélite 10 d, solo 24 meses); Outros prazos por fazenda.
- **Padrão atual:** Tabela de 73.7.8; água sem produto nunca bloqueada nem enviada ao agrônomo por dado vencido; protótipo sem validade por fonte (IR-7).
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13687`, `scratchpad/parecer/APENDICE.md:170`.

### AGR-06

- **Pergunta:** Abrir agora a frente "Aplicação segura e legal": reentrada no talhão, autoria do receituário e de quem publica o plano, receituário vinculado à O.S., família da operação, ocorrências com destino, sobra de calda e EPI?
- **Opções levantadas:** Abrir agora como a próxima frente; Fazer já só reentrada e família da operação (viram S1 no software real) e o resto depois; Esperar o fim do passo 1.
- **Padrão atual:** Nada iniciado; o Codex pediu que nenhuma frente nasça do parecer sem decisão (6088167538).
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:517`, `scratchpad/parecer/PARECER.md:58`, `scratchpad/parecer/PARECER.md:64`, `scratchpad/parecer/PARECER.md:142`, `scratchpad/parecer/PARECER.md:218`, `scratchpad/parecer/APENDICE.md:86`, `scratchpad/parecer/APENDICE.md:89`, `scratchpad/parecer/APENDICE.md:90`, `scratchpad/parecer/APENDICE.md:66`, `scratchpad/parecer/APENDICE.md:294`, `sp-nav:docs/navegacao/ESPECIFICACAO.md:77`, `PR #47 comentário 6088167538`.

### AGR-07

- **Pergunta:** Encaixar na frente de outorga e Agrofit (sp-ctl5) a conferência legal do plano e do ajuste por talhão (bula, alvo, carência, unidade) e a trava de unidade bula × lote?
- **Opções levantadas:** Encaixar agora; Depois da integração do sp-ctl5; Frente própria.
- **Padrão atual:** sp-ctl5 já leva o alvo pelo "Usar na O.S."; plano publica sem conferir bula; reserva aceita kg num lote em L.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:513`, `scratchpad/parecer/PARECER.md:70`, `scratchpad/parecer/PARECER.md:77`, `scratchpad/parecer/APENDICE.md:87`, `scratchpad/parecer/APENDICE.md:88`, `scratchpad/parecer/APENDICE.md:122`.

### AGR-08

- **Pergunta:** Conferir o CREA (e número de registro e ART) no momento de aprovar a O.S., e não só ao conceder o papel?
- **Opções levantadas:** Encaixar no sp-conf agora; Depois da revisão do Codex do sp-conf.
- **Padrão atual:** sp-conf confere o CREA só ao conceder ou reativar o papel (R4).
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:512`, `scratchpad/parecer/PARECER.md:219`, `scratchpad/parecer/APENDICE.md:59`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:106`.

### AGR-09

- **Pergunta:** Fazenda arrendada com contrato vencido e em renovação continua operando?
- **Opções levantadas:** Trava ao salvar a fazenda ativa (atual); Aviso com prazo e registro do protocolo de renovação; Trava só nos processos afetados.
- **Padrão atual:** Mantém a trava de hoje (cad_fazendas.py:418) e mostra a causa.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-cadux:docs/cadastros-ux/DECISOES.md:42`, `sp-cadux:docs/cadastros-ux/REQUISITOS.md:459`.

## Operação e O.S.

### OPE-01

- **Pergunta:** Quem libera a O.S. já aprovada pelo agrônomo: o gestor, o PCP ou outro papel (PEND-OS-01)?
- **Opções levantadas:** Gestor (padrão dos agentes); PCP (texto original do PRD e da AL-01); Configurável por fazenda em CF-02.
- **Padrão atual:** OS_LIB = 'gestor'; CMD-42 e CMD-06 gravados em separado; quem tem os dois papéis confirma uma vez; a AL-01 é editável no CF-01.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/DECISIONS.md:50`, `main:docs/DECISIONS.md:60`, `scratchpad/parecer/PARECER.md:542`, `scratchpad/parecer/APENDICE.md:143`, `scratchpad/parecer/APENDICE.md:278`, `scratchpad/codex-6064114787.md:21`, `sp-conf:docs/configuracoes/DECISOES.md:43`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:113`, `sp-dom:docs/controle-01/PLANO.md:470`, `sp-proto:tools/prototipo/v37/gen37/areas/processo_os.py:325`.

### OPE-02

- **Pergunta:** Validade máxima do pacote offline, atraso de sincronização tolerado e retenção do registro de repetição (PEND-02)?
- **Opções levantadas:** 7 d de pacote + 30 d de atraso + 30 d de margem, retenção de 90 d (proposta); Outros valores que respeitem IDEM-19.
- **Padrão atual:** Proposta como configuração inicial de HML e piloto, marcada "valor proposto".
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13676`, `main:docs/PRD.md:12721`.

### OPE-03

- **Pergunta:** Quem trata a chegada recusada por chave de repetição expirada, e em quanto tempo (PEND-03)?
- **Opções levantadas:** PCP (O.S. e apontamento), almoxarife (estoque), TI (integração), 1 dia útil, depois o gestor; Outro dono.
- **Padrão atual:** A proposta, configurável em CF-02; nada é reaplicado sozinho.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13677`.

### OPE-04

- **Pergunta:** Tolerâncias para vincular dois registros do mesmo fato sem abrir conferência (PEND-06)?
- **Opções levantadas:** Valores iniciais de CONC-10, revistos depois do piloto; Tolerância zero.
- **Padrão atual:** Valores iniciais de CONC-10, configuráveis com versão.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13680`.

### OPE-05

- **Pergunta:** Acrescentar a 72.3 a nota de leitura: o app não aceita acima do saldo e o excedente vai por ocorrência à conferência (PEND-07)?
- **Opções levantadas:** Acrescentar a nota; Deixar a leitura só no cap. 73.
- **Padrão atual:** CONC-14 já aplica a leitura; não muda comportamento.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13681`, `main:docs/PRD.md:12936`.

### OPE-06

- **Pergunta:** Janelas e prazos da conciliação (abastecimento 2 h, horímetro ±0,2 h, aguardando 72 h, caso 2 dias úteis) (PEND-09)?
- **Opções levantadas:** Valores propostos; Outros por fazenda.
- **Padrão atual:** Valores iniciais, configuráveis.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13683`.

### OPE-07

- **Pergunta:** Quem fica ciente quando o conferente aceita fato acima do autorizado ou fora da versão (PEND-10)?
- **Opções levantadas:** Aprovador da versão na O.S. com produto; PCP na água sem produto; Também na operação mecânica sem insumo.
- **Padrão atual:** A proposta, sem aprovação retroativa (CMD-43).
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13684`, `main:docs/prd/v3_10-reconciliacao.md:89`.

### OPE-08

- **Pergunta:** Impedir encerrar a O.S. enquanto um aparelho com a ordem no pacote tem item "Aguardando envio" (PEND-17, proposta fora de 73.12)?
- **Opções levantadas:** Recusar o encerramento, com "Encerrar sem o aparelho" pelo gestor; Só aviso ao conferente.
- **Padrão atual:** Aviso ao conferente, sem bloqueio; CMD-10 não alterado.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:58`, `main:docs/prd/v3_10-reconciliacao.md:93`.

### OPE-09

- **Pergunta:** Encaixar na frente de domínio (sp-dom) a conferência de mistura completa antes de iniciar e o volume de calda como parte da versão aprovada, com uma conta só para web, app e ficha?
- **Opções levantadas:** Encaixar agora; Frente própria depois do passo 1.
- **Padrão atual:** Início ignora componente fora da requisição; web 3.000 L/100 L/ha × app 2.000 L/120 L/ha.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:511`, `scratchpad/parecer/PARECER.md:130`, `scratchpad/parecer/PARECER.md:136`, `scratchpad/parecer/APENDICE.md:140`, `scratchpad/parecer/APENDICE.md:141`.

### OPE-10

- **Pergunta:** Encaixar na frente de demanda (sp-ctl4) a operação vencida sem O.S. como "vencida · decidir" (sem sair da compra), plantio sugerido nunca antes de hoje e "coberto pelo pedido"?
- **Opções levantadas:** Encaixar agora; Depois da integração do sp-ctl4.
- **Padrão atual:** sp-ctl4 muda o nome, mas o uso continua fora da compra (cal01.js:14).
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:514`, `scratchpad/parecer/PARECER.md:102`, `scratchpad/parecer/APENDICE.md:111`, `scratchpad/parecer/APENDICE.md:114`, `scratchpad/parecer/APENDICE.md:126`.

### OPE-11

- **Pergunta:** Cancelar O.S. com material entregue deve ficar "Cancelamento pendente" até a devolução (item não listado nos passos 2 e 3)?
- **Opções levantadas:** Encaixar no sp-sup com a reserva que volta; Encaixar no sp-dom; Frente 3.1.
- **Padrão atual:** Tela diz "Reserva liberada" e 320 L ficam com o operador sem pendência.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:220`, `scratchpad/parecer/APENDICE.md:139`.

### OPE-12

- **Pergunta:** Abrir a frente "Planejamento confiável" junto com o CONTROLE-02: variedade do cadastro, versão do plano no cultivo, estados e autorização da safra, conferência diária, custo por horas e entrada transversal de Controle (PEND-CTL-03)?
- **Opções levantadas:** Abrir depois da frente 3.1; Abrir já a variedade e a versão no cultivo (S2 mais baratos); Esperar o CONTROLE-02 completo.
- **Padrão atual:** CONTROLE-02 pendente, não iniciado; PEND-CTL-03: Controle transversal depois do CONTROLE-01.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:526`, `scratchpad/parecer/PARECER.md:82`, `scratchpad/parecer/PARECER.md:88`, `scratchpad/parecer/PARECER.md:95`, `scratchpad/parecer/PARECER.md:208`, `scratchpad/parecer/APENDICE.md:108`, `scratchpad/parecer/APENDICE.md:109`, `scratchpad/parecer/APENDICE.md:110`, `scratchpad/parecer/APENDICE.md:145`, `scratchpad/parecer/APENDICE.md:272`, `scratchpad/parecer/APENDICE.md:275`, `main:docs/DECISIONS.md:52`, `sp-nav:docs/navegacao/ESPECIFICACAO.md:76`, `scratchpad/codex-6064114787.md:25`.

### OPE-13

- **Pergunta:** Na tabela de operações do Planejar safra bastam rendimento (ha/h) e Custo R$/ha, com largura, velocidade e eficiência só no formulário (PEND-SAF-01, muda DEC-2609-03)?
- **Opções levantadas:** Sim, só no formulário; Manter as colunas na tabela.
- **Padrão atual:** Só no formulário (corte ratificado tecnicamente pelo Codex em 08/10).
- **Limite:** **DENTRO**.
- **Fontes:** `sp-safc02:docs/planejar-safra/etapa-unica-3-4-5/DECISOES.md:59`, `main:docs/DECISIONS.md:77`, `scratchpad/codex-6064114787.md:43`, `main:docs/PRD.md:12472`.

### OPE-14

- **Pergunta:** O custo da safra mês a mês precisa estar no Planejar safra ou basta o total por cultura (PEND-SAF-02)?
- **Opções levantadas:** Sai do Planejar safra e fica no orçamento; Volta com desenho próprio.
- **Padrão atual:** Sai do Planejar safra; continua exigido no orçamento (PRD 44.5 e 44.6).
- **Limite:** **DENTRO**.
- **Fontes:** `sp-safc02:docs/planejar-safra/etapa-unica-3-4-5/DECISOES.md:60`, `main:docs/DECISIONS.md:77`.

### OPE-15

- **Pergunta:** As duas fazendas dividem máquinas e pessoas na conta de capacidade?
- **Opções levantadas:** Cada fazenda soma as suas safras (atual); Somar as safras abertas das duas fazendas.
- **Padrão atual:** Cada fazenda soma as suas safras abertas.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-safc02:docs/planejar-safra/etapa-unica-3-4-5/DECISOES.md:61`.

### OPE-16

- **Pergunta:** Quantos dias depois da colheita o talhão fica livre para a próxima cultura (folga de liberação)?
- **Opções levantadas:** 0 dia (atrás da colhedora); 1 dia; Alguns dias por cultura.
- **Padrão atual:** 1 dia.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/planejar-safra/etapa-2-talhoes/DECISOES.md:42`, `sp-safc01:docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md:642`.

### OPE-17

- **Pergunta:** Pousio, reforma, área arrendada a terceiro ou embargada devem impedir o planejamento do talhão ou só avisar?
- **Opções levantadas:** Trava para embargo (lei) e aviso para pousio e reforma; Só aviso; Trava para todos.
- **Padrão atual:** Não existe; o talhão aparece Livre (orientação: marcar Inativo).
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/planejar-safra/etapa-2-talhoes/DECISOES.md:43`, `sp-safc01:docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md:644`.

### OPE-18

- **Pergunta:** Como encerrar o ciclo perene (erradicação ou renovação), tratar a safra 2025/26 encerrada com lavoura no campo e exigir colheita real da antecessora para liberar a sucessora?
- **Opções levantadas:** O.S. de erradicação encerrada fecha a ocupação; Reabrir a S2526 ou mover os ciclos; Proteção física na liberação (CMD-06).
- **Padrão atual:** Perene não termina no sistema; previsão não trava; ciclo mínimo é estimativa e safra encerrada não libera talhão ocupado.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/planejar-safra/etapa-2-talhoes/DECISOES.md:50`, `sp-proto:docs/planejar-safra/etapa-2-talhoes/DECISOES.md:52`, `sp-proto:docs/planejar-safra/etapa-2-talhoes/DECISOES.md:53`, `scratchpad/codex-6064114787.md:43`, `main:docs/DECISIONS.md:64`.

## Suprimentos e custos

### SUP-01

- **Pergunta:** Quem aprova ajuste de inventário e consumo acima da custódia, e o que fazer quando a mesma pessoa contou e aprova (PEND-CTL-02)?
- **Opções levantadas:** Gestor, com "revisão independente pendente" visível quando acumula (atual); Exigir outra pessoa sempre; Direção acima de um valor.
- **Padrão atual:** Gestor; acima da custódia, gestor; coberto pela custódia, almoxarife ou gestor; acúmulo vira revisão posterior visível.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/DECISIONS.md:51`, `main:docs/DECISIONS.md:63`, `scratchpad/codex-6064114787.md:24`, `sp-sup:docs/suprimentos-simplificado/DECISOES.md:33`, `sp-sup:docs/suprimentos-simplificado/DECISOES.md:34`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:117`, `sp-dom:docs/controle-01/PLANO.md:471`.

### SUP-02

- **Pergunta:** Quais são as alçadas reais de compra de insumos, peças e serviços?
- **Opções levantadas:** Manter as faixas de demonstração; Valores da política da fazenda.
- **Padrão atual:** Gestor de suprimentos até R$ 50 mil, gerente da fazenda até R$ 300 mil, acima Direção (demonstração, sem valor de produção).
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:tools/prototipo/v37/gen37/dados2.py:844`, `sp-sup:docs/suprimentos-simplificado/DECISOES.md:36`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:124`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:31`, `main:docs/PRD.md:5164`.

### SUP-03

- **Pergunta:** Haverá teto de custo por O.S. (hoje R$ 80 mil digitado em Configurações e não lido por comando)?
- **Opções levantadas:** Teto lido pelo custo previsto da O.S. num serviço único; Sem teto.
- **Padrão atual:** Texto digitado; nenhum comando lê.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-conf:docs/configuracoes/ESPECIFICACAO.md:220`.

### SUP-04

- **Pergunta:** Que tolerância de quantidade vale na compra e no recebimento (DEC-07)?
- **Opções levantadas:** Zero, diferença vira divergência registrada (atual); Tolerância por contrato e item.
- **Padrão atual:** 0 %; ±10 % não é padrão autorizado.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10503`, `main:docs/DECISIONS.md:44`, `sp-sup:docs/suprimentos-simplificado/DECISOES.md:37`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:32`.

### SUP-05

- **Pergunta:** Laudo obrigatório para todo lote em quarentena ou só para algumas classes de produto?
- **Opções levantadas:** Todo lote (atual); Só classes definidas.
- **Padrão atual:** Todo lote.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-sup:docs/suprimentos-simplificado/DECISOES.md:35`.

### SUP-06

- **Pergunta:** Prazos e carências da validade da reserva de material por finalidade (PEND-04)?
- **Opções levantadas:** Planejamento 3 d após o início previsto; execução 2 d; manutenção 7 d; aviso 24 h antes (proposta); Outros prazos.
- **Padrão atual:** Valores propostos em CF-02; o protótipo não tem validade de reserva (EST-15).
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13678`, `main:docs/PRD.md:12745`, `scratchpad/parecer/APENDICE.md:205`.

### SUP-07

- **Pergunta:** Quantas vezes e por quanto tempo a reserva pode ser renovada, e por quem (PEND-05)?
- **Opções levantadas:** Até 2 renovações de 7 d (3 d na execução), por almoxarife e PCP (PCM na manutenção); Outros limites.
- **Padrão atual:** A proposta, configurável.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13679`.

### SUP-08

- **Pergunta:** Prazos para resolver "Cota sem retorno" e "Sem cobertura" (PEND-16)?
- **Opções levantadas:** 2 dias úteis e 1 dia útil, depois aviso (proposta); Outros prazos.
- **Padrão atual:** A proposta; ao fim do prazo só há aviso.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13690`.

### SUP-09

- **Pergunta:** Na transferência direta de custódia entre O.S., reduzir na hora a reserva da ordem que recebe (PEND-19, proposta fora de 73.12)?
- **Opções levantadas:** Reduzir na mesma transação; Manter a reserva inteira até o término.
- **Padrão atual:** A reserva da destinatária não muda; devolução no término.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:58`, `main:docs/prd/v3_10-reconciliacao.md:140`.

### SUP-10

- **Pergunta:** No fechamento do período, aparelho sem sincronizar gera só aviso ou bloqueia o fechamento (PEND-15)?
- **Opções levantadas:** Aviso, e o fato tardio entra como ajuste da competência anterior; Bloquear até envio ou aparelho declarado perdido.
- **Padrão atual:** Aviso sem bloqueio.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13689`.

### SUP-11

- **Pergunta:** Encaixar na frente de suprimentos (sp-sup): lote elegível com validade e saída do que vence primeiro, vários lotes, reserva que volta ao dispensar e encerrar, produto errado no recebimento e depois pedido até o recebimento com aprovação de quem age (SUP-3)?
- **Opções levantadas:** Encaixar agora, nesta ordem; Depois de juntar SUP-2a e 2b.
- **Padrão atual:** Lote único pelo maior saldo, sem validade; reserva não volta; SUP-3 especificada e adiada.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:502`, `scratchpad/parecer/PARECER.md:107`, `scratchpad/parecer/PARECER.md:113`, `scratchpad/parecer/PARECER.md:124`, `scratchpad/parecer/PARECER.md:198`, `scratchpad/parecer/APENDICE.md:137`, `scratchpad/parecer/APENDICE.md:138`, `scratchpad/parecer/APENDICE.md:188`, `scratchpad/parecer/APENDICE.md:189`, `scratchpad/parecer/APENDICE.md:190`, `scratchpad/parecer/APENDICE.md:192`, `scratchpad/parecer/APENDICE.md:193`.

### SUP-12

- **Pergunta:** Como tratar custo da terra, arrendamento e formação da lavoura perene como investimento (GAP-4)?
- **Opções levantadas:** Linha própria "custo da terra", fora do custo operacional, rotulada; Ratear no custo por hectare; Formação do perene como ativo amortizado.
- **Padrão atual:** Fora do custo e da oferta.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:546`, `scratchpad/parecer/APENDICE.md:297`.

### SUP-13

- **Pergunta:** Por qual valor a peça recondicionada entra no estoque e em que natureza vão os serviços de terceiros (PCMS D4)?
- **Opções levantadas:** Custo do recondicionamento; Valor de reposição; Natureza nova para serviços de terceiros.
- **Padrão atual:** Só existe a natureza 3.1.05 "Peças e manutenção".
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:46`.

### SUP-14

- **Pergunta:** Ligar pedido automático por estoque mínimo e máximo (PCMS P8)?
- **Opções levantadas:** Desligado, só sugestão de um toque (atual); Ligado com limites por item, fornecedor homologado e alçada.
- **Padrão atual:** Desligado.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:37`, `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:10`.

### EXT-07

- **Pergunta:** Integrar de verdade com o ERP (Sankhya ou TOTVS), com credenciais e sandbox, e ler QR/DANFE ou SEFAZ?
- **Opções levantadas:** Sandbox autorizado primeiro; Adiar.
- **Padrão atual:** Fila do ERP simulada, sem credencial.
- **Limite:** **FORA** · aguarda o proprietário · Integração com ERP real e credenciais.
- **Fontes:** `main:docs/PRD.md:5165`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:229`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:230`, `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:21`.

## Manutenção

### MAN-01

- **Pergunta:** Quem aprova a ordem de manutenção e até que valor, quem aceita serviço de oficina externa, qual o teto da compra de balcão e quem decide conflito entre manutenção e O.S. de produção?
- **Opções levantadas:** Faixas da compra aplicadas à estimativa da OM (atual); Alçada própria de manutenção; Delegar ao responsável de manutenção o conflito de janela.
- **Padrão atual:** Faixas da compra; na 1ª faixa a aprovação do responsável vale como autorização econômica; conflito com a gerência (Ana); balcão permitido como fato registrado, sem teto.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:547`, `scratchpad/parecer/APENDICE.md:223`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:43`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:36`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:33`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:38`, `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:11`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:222`.

### MAN-02

- **Pergunta:** Qual o critério de criticidade das máquinas?
- **Opções levantadas:** Campo no cadastro (A/B/C pelo impacto na produção e na segurança); Calculada pelo atraso (atual).
- **Padrão atual:** Calculada pelo atraso; o cadastro de máquinas não tem criticidade.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:547`, `scratchpad/parecer/APENDICE.md:230`.

### MAN-03

- **Pergunta:** Qual o custo-hora real da oficina?
- **Opções levantadas:** Manter R$ 320/h como hipótese; Valor real da fazenda.
- **Padrão atual:** R$ 320/h (hipótese).
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:30`, `sp-proto:docs/pcm-suprimentos/DECISOES.md:44`.

### MAN-04

- **Pergunta:** Controlar pneus (posição, recapagem, km) agora?
- **Opções levantadas:** Agora; Depois.
- **Padrão atual:** Fora.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:45`, `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:12`.

### MAN-05

- **Pergunta:** A peça já disponível e a que chega para uma OM devem ficar presas a ela desde a aprovação (PCMS D5; muda DEC-2609-13, que reserva na liberação)?
- **Opções levantadas:** Reservar na liberação (atual); Reservar desde a aprovação, por criticidade e depois data.
- **Padrão atual:** Reserva na liberação; cobertura planejada só no cálculo e no aviso.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:47`, `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:9`.

### MAN-06

- **Pergunta:** Qual a capacidade semanal da oficina por especialidade?
- **Opções levantadas:** Definir horas por especialidade; Deixar "não calculável".
- **Padrão atual:** Não definida; o indicador fica "não calculável".
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/DECISOES.md:39`, `sp-pcm:docs/pcm-simplificado/FORA-DE-ESCOPO.md:30`.

### MAN-07

- **Pergunta:** Adotar regras que o PCM simplificado deixou fora: geração automática da preventiva, aprovação de várias OMs num toque, antecipar preventiva em dia e desfazer bloqueio registrado por engano?
- **Opções levantadas:** Manter fora; Adotar com política expressa e repetição protegida no servidor.
- **Padrão atual:** Fora; a geração da preventiva continua decisão do PCM.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-pcm:docs/pcm-simplificado/FORA-DE-ESCOPO.md:13`, `sp-pcm:docs/pcm-simplificado/FORA-DE-ESCOPO.md:15`, `sp-pcm:docs/pcm-simplificado/FORA-DE-ESCOPO.md:16`, `sp-pcm:docs/pcm-simplificado/FORA-DE-ESCOPO.md:17`.

### MAN-08

- **Pergunta:** Encaixar na frente de manutenção (sp-pcm) o diesel lançado em dobro e o consumo por hora, a regra única "a máquina impede o trabalho" também na O.S. e na irrigação, e as peças pelo passo 1b?
- **Opções levantadas:** Encaixar agora; Depois da revisão do Codex da correção ba03515.
- **Padrão atual:** sp-pcm resolve só o trator T1; o autor relata a correção do diesel em ba03515, ainda sem revisão do Codex.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:507`, `scratchpad/parecer/PARECER.md:154`, `scratchpad/parecer/PARECER.md:183`, `scratchpad/parecer/PARECER.md:189`, `scratchpad/parecer/APENDICE.md:221`, `scratchpad/parecer/APENDICE.md:224`, `scratchpad/parecer/APENDICE.md:225`, `scratchpad/parecer/APENDICE.md:228`, `scratchpad/parecer/APENDICE.md:229`, `scratchpad/parecer/APENDICE.md:164`, `PR #47 comentário 6088167538`.

### MAN-09

- **Pergunta:** Quem é o escritor designado do abastecimento: almoxarife do local ou abastecedor designado por ponto (PEND-08)?
- **Opções levantadas:** Almoxarife do local; Abastecedor designado por ponto em CF-02.
- **Padrão atual:** Almoxarife do local.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13682`, `main:docs/prd/v3_10-reconciliacao.md:78`.

### EXT-15

- **Pergunta:** Aceitar consignação de peças caras oferecida por fornecedor real?
- **Opções levantadas:** Aceitar oferta; Não.
- **Padrão atual:** Fora.
- **Limite:** **FORA** · aguarda o proprietário · Contrato com fornecedor real.
- **Fontes:** `sp-proto:docs/pcm-suprimentos/FORA-DE-ESCOPO.md:13`.

## Produção e comercial

### PRO-01

- **Pergunta:** A saca dos contratos de soja (CT-201, CT-203, CRE-0095, BT-090) é de 50 ou de 60 kg?
- **Opções levantadas:** 50 kg; 60 kg; Massa registrada por contrato, com fonte.
- **Padrão atual:** "Saca a conferir": suspende só falta, reserva, carga, crédito e oferta dependentes; quem tem o contrato registra a massa com fonte.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `scratchpad/parecer/PARECER.md:543`, `scratchpad/parecer/APENDICE.md:251`, `sp-proto:docs/colheita/DECISOES.md:49`, `sp-com:docs/comercial/DECISOES.md:40`, `sp-com:docs/comercial/DECISOES.md:33`, `scratchpad/codex-6064114787.md:39`, `scratchpad/codex-6070584991.md:15`, `main:docs/DECISIONS.md:28`.

### PRO-02

- **Pergunta:** Na Lagoa Grande o mamão é vendido por kg como sai do campo ou passa por packing?
- **Opções levantadas:** Por kg do campo; Packing.
- **Padrão atual:** Desenho com packing (BEN-1) e venda por kg.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/colheita/DECISOES.md:46`.

### PRO-03

- **Pergunta:** Quantas plantas vivas por hectare e qual a perda esperada do mamão em produção?
- **Opções levantadas:** Valores da fazenda.
- **Padrão atual:** Valores sintéticos (D-10).
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/colheita/DECISOES.md:47`.

### PRO-04

- **Pergunta:** O armazém usa tabela própria de desconto de umidade e impureza?
- **Opções levantadas:** Tabela do armazém; Tabela padrão cadastrada.
- **Padrão atual:** Umidade e impureza fixas; classe "Padrão".
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-proto:docs/colheita/DECISOES.md:48`, `scratchpad/parecer/APENDICE.md:263`.

### PRO-05

- **Pergunta:** Qual padrão oficial de classificação (MAPA) cadastrar por produto?
- **Opções levantadas:** Cadastrar o padrão vigente, com item e vigência verificados (verificar vigência); Sem padrão oficial no protótipo.
- **Padrão atual:** Nenhuma norma embutida; padrão entra cadastrado e versionado.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:11`.

### PRO-06

- **Pergunta:** O limite de crédito da Frutas Real é R$ 120.000?
- **Opções levantadas:** R$ 120.000; Outro valor.
- **Padrão atual:** R$ 120.000 sintético; próxima carga de 10 t pede a gestora.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-com:docs/comercial/DECISOES.md:37`, `sp-com:docs/comercial/DECISOES.md:12`.

### PRO-07

- **Pergunta:** Quem aprova crédito na fazenda: gestora, proprietário ou financeiro?
- **Opções levantadas:** Gestora; Proprietário; Financeiro.
- **Padrão atual:** Gestora.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-com:docs/comercial/DECISOES.md:38`.

### PRO-08

- **Pergunta:** O mamão da Lagoa Grande é entregue no cliente (frete do produtor) ou retirado na fazenda?
- **Opções levantadas:** Entregue no cliente; Retirado na fazenda.
- **Padrão atual:** Sintético.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-com:docs/comercial/DECISOES.md:39`.

### PRO-09

- **Pergunta:** Que tolerância de peso os contratos aceitam na entrega?
- **Opções levantadas:** Tolerância por contrato; Sem tolerância.
- **Padrão atual:** Todo excesso sobre o reservado pede a gestora.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-com:docs/comercial/DECISOES.md:41`, `sp-com:docs/comercial/DECISOES.md:29`.

### PRO-10

- **Pergunta:** Valores do beneficiamento: tolerância da pesagem, alçada de diferença (% e teto por rota) e quem é "a gestão", umidades, incerteza, matéria seca, fração vendável, equipe e custo-hora do packing, metas, horas da linha e vida útil?
- **Opções levantadas:** Manter os sintéticos versionados; Valores da fazenda e do responsável técnico, com fonte.
- **Padrão atual:** Sintético vN "a confirmar pelo proprietário"; acima da alçada decide Ana; horas da linha sem padrão.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-ben:docs/beneficiamento/DECISOES.md:33`, `sp-ben:docs/beneficiamento/DECISOES.md:41`, `sp-ben:docs/beneficiamento/DECISOES.md:42`, `sp-ben:docs/beneficiamento/DECISOES.md:49`, `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:9`, `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:10`.

### PRO-11

- **Pergunta:** Permitir liberar lote fora do padrão por concessão de um cliente específico?
- **Opções levantadas:** Não; Sim, com registro do cliente e da concessão.
- **Padrão atual:** Não existe.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:12`.

### PRO-12

- **Pergunta:** Registrar fruto e coco de café em saca ou litro e mostrar o equivalente a 14 % do grão úmido?
- **Opções levantadas:** Fazer, com fator e fonte por item; Não fazer.
- **Padrão atual:** Fora; campo vazio.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:14`, `sp-ben:docs/beneficiamento/FORA-DE-ESCOPO.md:15`.

### PRO-13

- **Pergunta:** Unidade da laranja (caixa de 40,8 kg/ha ou t/ha) e de coco e abacaxi (mil frutos/ha)?
- **Opções levantadas:** cx/ha com t/ha ao lado; mil frutos/ha com t opcional (proposta); t/ha para todas (letra da DEC-0510-03).
- **Padrão atual:** Proposta dos agentes, sem decisão.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-ben:docs/culturas/UNIDADES-DE-MERCADO.md:99`, `sp-ben:docs/culturas/UNIDADES-DE-MERCADO.md:51`, `sp-ben:docs/culturas/UNIDADES-DE-MERCADO.md:65`, `main:docs/DECISIONS.md:28`.

### PRO-14

- **Pergunta:** Qual meta de acerto da previsão de colheita (DEC-03)?
- **Opções levantadas:** WAPE ≤ 10 % como alvo experimental por cultura e horizonte; Sem meta até o piloto.
- **Padrão atual:** Alvo experimental, sem prometer acurácia nem bloquear vendas.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10499`, `main:docs/DECISIONS.md:40`.

### PRO-15

- **Pergunta:** Como distribuir oportunidades a parceiros (DEC-06)?
- **Opções levantadas:** Só destinatários confirmados, sugestão sem publicação (atual); Automação com política do produtor, revogável.
- **Padrão atual:** Só destinatários confirmados.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10502`, `main:docs/DECISIONS.md:43`.

## Irrigação e água

### IRR-01

- **Pergunta:** Com a outorga "em renovação", pode irrigar?
- **Opções levantadas:** Só aviso (atual); Permitir só com protocolo de renovação registrado no prazo; sem ele, trava; Trava sempre.
- **Padrão atual:** Só aviso "Outorga em renovação"; outorga vencida trava. Norma: Lei 9.433/1997 e regra do órgão estadual (verificar vigência).
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:544`, `scratchpad/parecer/APENDICE.md:172`, `sp-proto:tools/prototipo/v37/gen37/irrigacao_estado.js:209`.

### IRR-02

- **Pergunta:** Os pivôs da Lagoa Grande captam numa rede comum às outorgas do Rio A?
- **Opções levantadas:** Sim, soma por curso; Não, outorga por ponto.
- **Padrão atual:** Premissa sintética de rede comum; conferir vínculo e capacidade por ponto antes de dado real.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `sp-dom:docs/controle-01/PLANO.md:482`, `sp-ben:docs/controle-01/desenho/FRENTE-E.md:378`, `main:docs/DECISIONS.md:66`, `scratchpad/codex-6064114787.md:27`.

### IRR-03

- **Pergunta:** O que significa a "lâmina 21 h" da ficha do pivô e qual o regime de operação?
- **Opções levantadas:** Guardar como referência do regime, sem calcular prescrição; Converter em parâmetro depois de confirmado.
- **Padrão atual:** Guardada como referência, sem prescrição.
- **Limite:** **DENTRO** · fato da fazenda: vale o padrão seguro, a confirmar com o dado real.
- **Fontes:** `main:docs/DECISIONS.md:75`, `scratchpad/codex-6064114787.md:52`, `sp-solo:docs/analise-solo/DECISOES.md:40`.

### IRR-04

- **Pergunta:** Abrir a frente "Irrigação medida": fonte de volume por setor (hidrômetro ou estimado), cadastro único de setor e pivô com vazão versionada, percentímetro e parâmetros com versão?
- **Opções levantadas:** Abrir depois das frentes 3.1 e 3.2; Antecipar só a fonte de volume (S2).
- **Padrão atual:** Volume pré-preenchido como "telemetria"; vazão da irrigação diferente do cadastro.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:532`, `scratchpad/parecer/PARECER.md:164`, `scratchpad/parecer/PARECER.md:170`, `scratchpad/parecer/APENDICE.md:165`, `scratchpad/parecer/APENDICE.md:166`, `scratchpad/parecer/APENDICE.md:167`, `scratchpad/parecer/APENDICE.md:173`.

## Plataforma, acesso e design

### PLA-01

- **Pergunta:** As camadas do Mapa voltam às nove decididas em 26/09 (com Solo, Estádio e Colheita e produtividade) ou se registram as atuais?
- **Opções levantadas:** Voltar às nove de DEC-2609-06/12; Registrar as atuais como nova decisão; Híbrido: nove nomes, com Carência e Insumos como filtros.
- **Padrão atual:** Integrado, Satélite, Lavoura, MIP/MID, Carência e destino, Irrigação, O.S./prazos, Insumos, Custos; Solo e Colheita na fase 2.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:545`, `scratchpad/parecer/APENDICE.md:72`, `main:docs/PRD.md:12475`, `main:docs/PRD.md:12480`, `sp-proto:tools/prototipo/v37/gen37/areas/inicio.py:99`, `sp-solo:docs/analise-solo/ESPECIFICACAO.md:425`.

### PLA-02

- **Pergunta:** A assinatura cobra por área física contratada ou por hectare ativo medido no cadastro (DEC-01)?
- **Opções levantadas:** Área contratada; Área medida, com piso mensal.
- **Padrão atual:** Proposta: área contratada; protótipo com exemplo e nenhuma cobrança real.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10497`, `main:docs/PRD.md:8832`, `main:docs/DECISIONS.md:38`, `sp-proto:docs/plataforma-assinaturas/DECISOES.md:118`.

### PLA-03

- **Pergunta:** Régua de inadimplência: quantos dias e o que é restringido?
- **Opções levantadas:** Régua do protótipo (PLAT-D08); Outra.
- **Padrão atual:** Exemplo do protótipo.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-proto:docs/plataforma-assinaturas/DECISOES.md:121`.

### PLA-04

- **Pergunta:** Tela de entrada por papel ou o Mapa como entrada de todos (DEC-02)?
- **Opções levantadas:** Por papel, com preferência individual; Mapa para todos.
- **Padrão atual:** Por papel, com preferência individual autorizada.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10498`, `main:docs/DECISIONS.md:39`.

### PLA-05

- **Pergunta:** Manter integralmente os controles técnicos de qualidade e segurança antes do piloto (DEC-04)?
- **Opções levantadas:** Manter; Mudar só com ADR e análise de risco.
- **Padrão atual:** Mantidos; sem redução para cumprir prazo.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:10500`, `main:docs/PRD.md:10481`, `main:docs/DECISIONS.md:41`.

### PLA-DS01

- **Pergunta:** Cor das etapas da O.S.: Liberadas em azul e Em execução em verde? (PEND-DS-01)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta (A liberar Neutro · Liberadas azul · Em execução verde · Em conferência atenção · Encerradas Neutro).
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15161`, `main:docs/DECISIONS.md:49`.

### PLA-DS02

- **Pergunta:** "Sobras a receber" ou "Sobras pendentes"? (PEND-DS-02)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** "Sobras a receber" (8.4.3 ainda diz "pendentes").
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15162`, `main:docs/DECISIONS.md:49`, `main:docs/prd/v3_10-reconciliacao.md:86`.

### PLA-DS03

- **Pergunta:** Entregar modo escuro agora? (PEND-DS-03)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** Só tema claro.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15163`, `main:docs/DECISIONS.md:49`.

### PLA-DS04

- **Pergunta:** Nome exibido "Do Talhão à O.S." e logotipo definitivo? (PEND-DS-04)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** Nome "Do Talhão à O.S." e marca provisória; o logotipo definitivo é um arquivo que só ele fornece.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15164`, `main:docs/DECISIONS.md:49`.

### PLA-DS05

- **Pergunta:** Confirmar as fontes Sora e Manrope servidas pelo próprio produto? (PEND-DS-05)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta; conferir a licença no pacote antes de publicar.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15165`, `main:docs/DECISIONS.md:49`.

### PLA-DS06

- **Pergunta:** Pontos de quebra: celular abaixo de 768 px, tablet até 1279 px, desktop acima? (PEND-DS-06)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15166`, `main:docs/DECISIONS.md:49`, `sp-cadux:docs/cadastros-ux/REQUISITOS.md:210`.

### PLA-DS07

- **Pergunta:** Barra vertical do mapa com 96 px? (PEND-DS-07)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** 96 px.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15167`, `main:docs/DECISIONS.md:49`.

### PLA-DS08

- **Pergunta:** Retirar "Em planejamento" e usar só os estados de 8.1 na safra? (PEND-DS-08)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** Estados de 8.1.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15168`, `main:docs/DECISIONS.md:49`.

### PLA-DS09

- **Pergunta:** Menu recolhido com 64 px? (PEND-DS-09)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta; no desktop começa aberto.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15169`, `main:docs/DECISIONS.md:49`.

### PLA-DS10

- **Pergunta:** Paleta do índice de água (NDWI) sem as cores de vigor? (PEND-DS-10)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15170`, `main:docs/DECISIONS.md:49`.

### PLA-DS11

- **Pergunta:** Paleta do Solo por faixa técnica, sem "alto" em verde? (PEND-DS-11)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta; atributo sem faixa mostra o valor escrito.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15171`, `main:docs/DECISIONS.md:49`.

### PLA-DS12

- **Pergunta:** Raster por pixel sobre imagem de satélite real? (PEND-DS-12)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** Polígono com a classe do valor médio, fundo liso.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15172`, `main:docs/DECISIONS.md:49`.

### PLA-DS13

- **Pergunta:** Apresentação compacta de números em mapa, cartão e KPI? (PEND-DS-13)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A 10.0 (duas casas) em toda a interface.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15173`, `main:docs/DECISIONS.md:49`.

### PLA-DS14

- **Pergunta:** Sons curtos de retorno no app? (PEND-DS-14)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** A proposta (tom de 150 ms e dois tons de 300 ms).
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15174`, `main:docs/DECISIONS.md:49`.

### PLA-DS15

- **Pergunta:** Palavra da reserva comercial que vence: "Vencida · devolvida ao disponível"? (PEND-DS-15)
- **Opções levantadas:** Adotar a proposta de 74.12; Manter o protótipo; Outra.
- **Padrão atual:** "Expirada", em Neutro.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15175`, `main:docs/DECISIONS.md:49`.

### PLA-06

- **Pergunta:** Encaixar na frente do design system (sp-ds) a cor das etapas e pendências: "concluída" só com a condição cumprida e vermelho só para impedimento real?
- **Opções levantadas:** Encaixar agora; Depois da integração do sp-ds.
- **Padrão atual:** Etapas futuras e pendências comuns em vermelho.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:515`, `scratchpad/parecer/PARECER.md:225`, `scratchpad/parecer/APENDICE.md:127`, `scratchpad/parecer/APENDICE.md:180`, `scratchpad/parecer/APENDICE.md:157`.

### PLA-07

- **Pergunta:** Prazos de reconhecimento e escalonamento das exceções de integração com o ERP (PEND-11)?
- **Opções levantadas:** Controladoria e almoxarifado 1 dia útil, TI 4 h úteis (proposta); Outros.
- **Padrão atual:** Valor proposto em CF-02; nada é compromisso de atendimento.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13685`.

### PLA-08

- **Pergunta:** Algum tipo de efeito só encerra a O.S. depois da confirmação do ERP (PEND-12)?
- **Opções levantadas:** Nenhum tipo marcado; Marcar só com exigência legal ou fiscal demonstrada.
- **Padrão atual:** Nenhum tipo marcado.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13686`.

### PLA-09

- **Pergunta:** Atraso tolerado das visões gerenciais (PEND-14)?
- **Opções levantadas:** Metas de PROJ-06 (5 a 60 min); Consolidação horária ou diária, mais barata.
- **Padrão atual:** Valores de PROJ-06.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13688`.

### PLA-10

- **Pergunta:** Permitir a exceção de equipe pequena (revisor posterior) em metas ligadas a remuneração variável (PEND-18)?
- **Opções levantadas:** Permitir com revisor posterior designado; Proibir e exigir revisor externo.
- **Padrão atual:** Sem a exceção.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:13691`, `main:docs/PRD.md:200`.

### PLA-11

- **Pergunta:** Que evidência mínima habilita a gravação de cada operação no ERP (PEND-20, proposta fora de 73.12)?
- **Opções levantadas:** Cada caso contratado ocorrido e conciliado e um fechamento mensal sem divergência; Outro critério.
- **Padrão atual:** 66.3 sem número.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:169`, `main:docs/prd/v3_10-reconciliacao.md:154`.

### PLA-12

- **Pergunta:** Quem aceita habilitar e retomar a gravação no ERP, por linha (PEND-21)?
- **Opções levantadas:** Almoxarifado, controladoria, compras e financeiro, cada um na sua linha; TI não aceita sozinho; Responsável do processo da linha.
- **Padrão atual:** Responsável do processo da linha contratada.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:169`.

### PLA-13

- **Pergunta:** Em que ordem habilitar a gravação no ERP no piloto (PEND-22)?
- **Opções levantadas:** Consumo e devolução, depois custos, depois pedidos; títulos ficam no ERP; Outra.
- **Padrão atual:** Todas as operações só leitura.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:169`.

### PLA-14

- **Pergunta:** Quem não consegue anexar imagem pode relatar problema sem o print (PEND-FB-01)?
- **Opções levantadas:** Marcar "não consigo anexar" e enviar com o contexto; Print obrigatório com ajuda da equipe.
- **Padrão atual:** Print obrigatório, com ajuda da equipe.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15376`.

### PLA-15

- **Pergunta:** Por quanto tempo guardar os prints dos relatos (PEND-FB-02), estendido a chamado e contexto?
- **Opções levantadas:** 180 dias depois do encerramento, com exclusão a pedido; Outro prazo.
- **Padrão atual:** Antes de cliente real, nenhum print com dado real.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/PRD.md:15377`, `main:docs/prd/v3_10-reconciliacao.md:171`.

### PLA-16

- **Pergunta:** Prazo de primeira resposta dos chamados que não são incidente (PEND-FB-03, proposta)?
- **Opções levantadas:** Por tipo e contrato, antes do piloto, sem as 48 h da referência.
- **Padrão atual:** Nenhum prazo exibido.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:130`.

### PLA-17

- **Pergunta:** Quem vê os chamados dentro da organização (PEND-FB-04, proposta)?
- **Opções levantadas:** Administrador vê todos; demais só os próprios; Só autor e suporte.
- **Padrão atual:** Só autor e suporte.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:171`.

### PLA-18

- **Pergunta:** Quando entregar a Ajuda com chamado (PEND-FB-06, proposta)?
- **Opções levantadas:** Junto do primeiro piloto; Depois.
- **Padrão atual:** Escopo mínimo do piloto sem mudança.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:171`.

### PLA-19

- **Pergunta:** Que etapas da implantação contam como obrigatórias para "Implantação parada" (PEND-USO-01, proposta)?
- **Opções levantadas:** As que levam ao primeiro resultado útil do perfil; Todas.
- **Padrão atual:** Toda etapa pendente conta.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:170`.

### PLA-20

- **Pergunta:** Quem no suporte recebe a permissão de acompanhar a adoção (PEND-USO-02, proposta)?
- **Opções levantadas:** Equipe de sucesso do cliente com MFA e trilha; Todo administrador.
- **Padrão atual:** Ninguém por padrão.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:170`.

### PLA-21

- **Pergunta:** Como fazer contato proativo com o cliente a partir de uma leitura de uso (PEND-USO-03, proposta)?
- **Opções levantadas:** Contato humano no canal preferido, respeitando recusa; Automação.
- **Padrão atual:** Contato humano autorizado, sem automação.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:170`.

### PLA-22

- **Pergunta:** Criar pontuação agregada de saúde da conta (PEND-USO-04, proposta)?
- **Opções levantadas:** Só depois de medir no piloto; Agora.
- **Padrão atual:** Só as quatro leituras explicáveis de 58.5.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:170`.

### PLA-23

- **Pergunta:** Incluir em Configurações vigência, delegação e substituição temporária de papéis, exportação completa dos cadastros e trilha de apontamentos e contagens, e confirmar as pessoas Comercial e Lúcia?
- **Opções levantadas:** Fazer agora; Quando houver férias de RT a cobrir; Software real.
- **Padrão atual:** Fora; Comercial e Lúcia ficam fora das alçadas.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-conf:docs/configuracoes/ESPECIFICACAO.md:217`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:224`, `sp-conf:docs/configuracoes/ESPECIFICACAO.md:227`, `sp-conf:docs/configuracoes/DECISOES.md:170`.

### PLA-24

- **Pergunta:** Fechar a PEND-REPO-01 (plano do GitHub e proteção da main), já que a proteção está ativa no servidor?
- **Opções levantadas:** Registrar o fechamento; Manter aberta.
- **Padrão atual:** Ruleset 24154464 ativo, conferido no servidor; o DECISIONS ainda a lista como pendente.
- **Limite:** **DENTRO**.
- **Fontes:** `main:docs/DECISIONS.md:48`, `main:docs/STATUS.md:17`.

### EXT-01

- **Pergunta:** Criar a conta de faturamento e o projeto do Google Cloud e provisionar a homologação hospedada?
- **Opções levantadas:** Criar quando ele voltar; Continuar só local e na CI.
- **Padrão atual:** Nada provisionado; gasto de referência US$ 30/mês aceito em 29/09, mas conta, cartão e termos exigem a identidade dele.
- **Limite:** **FORA** · aguarda o proprietário · Cria conta e gera custo em nome dele (login, termos, cartão).
- **Fontes:** `main:docs/STATUS.md:16`, `main:docs/STATUS.md:31`, `main:docs/parceria/rodadas/evidencias/R-006-hospedagem.md:13`, `main:docs/parceria/rodadas/evidencias/R-006-hospedagem.md:180`, `main:docs/OPERACAO.md:17`.

### EXT-02

- **Pergunta:** Configurar o teto de gasto nativo do Cloud Run na conta de faturamento?
- **Opções levantadas:** Configurar; Só alertas.
- **Padrão atual:** Proposta, não configurada.
- **Limite:** **FORA** · aguarda o proprietário · Mexe em faturamento da conta dele.
- **Fontes:** `main:docs/parceria/rodadas/evidencias/R-006-hospedagem.md:117`, `main:docs/parceria/rodadas/evidencias/R-006-hospedagem.md:123`.

### EXT-03

- **Pergunta:** Contratar hospedagem do piloto (≈ US$ 112 a 183/mês) e domínio próprio?
- **Opções levantadas:** HA dedicado; HA compartilhado sem SLA.
- **Padrão atual:** Não contratado; endereço padrão.
- **Limite:** **FORA** · aguarda o proprietário · Gera custo mensal e contrato.
- **Fontes:** `main:docs/parceria/rodadas/R-006-plano-f0-f1.md:82`.

### EXT-04

- **Pergunta:** Contratar ou licenciar o SonarQube (gate externo de qualidade, ENG-018)?
- **Opções levantadas:** Licenciar; Manter a exceção registrada até o piloto.
- **Padrão atual:** Pendente, com exceção registrada.
- **Limite:** **FORA** · aguarda o proprietário · Licença e conta com custo.
- **Fontes:** `main:docs/STATUS.md:43`, `main:docs/parceria/rodadas/R-006-plano-f0-f1.md:93`.

### EXT-06

- **Pergunta:** Instalar o Docker Desktop no Mac dele (licença depende do porte da empresa; pede a senha do Mac)?
- **Opções levantadas:** Docker Desktop; Colima; Não precisa (CI já roda o banco real).
- **Padrão atual:** Continuava com ele em 27/09; estado atual não conferido.
- **Limite:** **FORA** · aguarda o proprietário · Licença conforme o porte da empresa e senha da máquina dele.
- **Fontes:** `main:docs/parceria/rodadas/R-006-skills-ferramentas-plano.md:60`, `main:docs/parceria/rodadas/R-006-plano-f0-f1.md:72`.

### EXT-10

- **Pergunta:** Que perfil de atendimento prometer no piloto (disponibilidade, plantão, horário de reconhecimento) (PEND-OP-01)?
- **Opções levantadas:** Piloto com disponibilidade menor declarada; Metas do cap. 30.
- **Padrão atual:** Não chamar o piloto de 24×7.
- **Limite:** **FORA** · aguarda o proprietário · Compromisso de serviço com clientes reais e custo de plantão.
- **Fontes:** `main:docs/PRD.md:15378`, `main:docs/PRD.md:5820`.

### EXT-11

- **Pergunta:** Quais provedores, contrato de dados, local de processamento e orçamento do assistente de IA (PEND-IA-01)?
- **Opções levantadas:** Decidir com estimativa por organização e mês.
- **Padrão atual:** Assistente desligado.
- **Limite:** **FORA** · aguarda o proprietário · Contrato com terceiros, dados e custo.
- **Fontes:** `main:docs/PRD.md:15379`.

### EXT-13

- **Pergunta:** Preços, mínimo, franquias, número de planos, trial, retenção e calendário de cobrança do agricultor e dos parceiros (DEC-05, DEC-09)?
- **Opções levantadas:** Manter exemplos no protótipo; Fixar oferta antes do piloto pagante.
- **Padrão atual:** Exemplos do protótipo; nenhuma cobrança real.
- **Limite:** **FORA** · aguarda o proprietário · Valor comercial que vira contrato com clientes reais em nome dele.
- **Fontes:** `main:docs/PRD.md:10501`, `main:docs/PRD.md:10505`, `main:docs/PRD.md:10483`, `main:docs/DECISIONS.md:42`, `main:docs/DECISIONS.md:46`, `sp-proto:docs/plataforma-assinaturas/DECISOES.md:119`, `sp-proto:docs/plataforma-assinaturas/DECISOES.md:120`, `sp-proto:docs/plataforma-assinaturas/DECISOES.md:122`.

### EXT-14

- **Pergunta:** Contratar ferramenta de atendimento de mercado ou fazer tela interna para os chamados (PEND-FB-05, proposta)?
- **Opções levantadas:** Ferramenta de mercado; Tela interna restrita.
- **Padrão atual:** A definir antes do piloto.
- **Limite:** **FORA** · aguarda o proprietário · Ferramenta de mercado gera conta e custo (a tela interna seria decisão dos agentes).
- **Fontes:** `main:docs/prd/v3_10-reconciliacao.md:171`.

### EXT-16

- **Pergunta:** Enviar mensagens reais (convite por e-mail ou WhatsApp) no software real?
- **Opções levantadas:** Com autorização dele.
- **Padrão atual:** Nunca no protótipo.
- **Limite:** **FORA** · aguarda o proprietário · Mensagem real a pessoas.
- **Fontes:** `sp-conf:docs/configuracoes/ESPECIFICACAO.md:231`, `AGENTS.md §2`.

## Processo e prioridade

### PRC-01

- **Pergunta:** Juntar ao protótipo as 13 frentes já feitas, uma por vez e nesta ordem, corrigindo antes o defeito do PCM e consertando "Restaurar dados" e "Entrar como" do índice?
- **Opções levantadas:** Ordem do parecer (demanda e capacidade → domínio → suprimentos → manutenção → configurações → outorga, solo, comercial, beneficiamento → tabelas, design, navegação); Ordem por dependência de arquivos.
- **Padrão atual:** Integração em andamento (BEN integrado); o S1 do PCM impede publicar a candidata afetada até revisão.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:489`, `scratchpad/parecer/PARECER.md:224`, `scratchpad/parecer/APENDICE.md:274`, `scratchpad/parecer/APENDICE.md:283`, `scratchpad/resp-6079601661.md:36`, `PR #47 comentário 6088167538`.

### PRC-02

- **Pergunta:** Encaixar as lacunas nas frentes atuais (passo 2) antes de abrir frentes novas (passo 3), e abrir as novas uma por vez na ordem 3.1 → 3.2 → 3.3 → 3.4?
- **Opções levantadas:** Ordem do parecer; Priorizar só os riscos que viram S1 no software real; Adiar o passo 3 até o fim do passo 1.
- **Padrão atual:** Nada aberto; o Codex não dispara frentes sem decisão.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:501`, `scratchpad/parecer/PARECER.md:517`, `PR #47 comentário 6088167538`.

### PRC-03

- **Pergunta:** Abrir a frente "Cadastro que alimenta os processos" (talhão inativo, fornecedor homologado e frota lidos do cadastro salvo)?
- **Opções levantadas:** Fazer como 3.4; Só rotular "demonstração" no cadastro.
- **Padrão atual:** Cadastros salvos não chegam aos processos.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:537`, `scratchpad/parecer/PARECER.md:222`, `scratchpad/parecer/APENDICE.md:296`.

### PRC-04

- **Pergunta:** Ratificar em bloco as decisões dos agentes nos DECISOES.md das frentes, as mudanças pedidas por ele a decisões anteriores (menu da Manutenção, Planejar safra em 4 etapas, Suprimentos, Beneficiamento, seleção que abre detalhe) e registrar os pedidos ainda fora do DECISIONS (água só na Irrigação, O.S. sem etapa de revisão)?
- **Opções levantadas:** Ratificar e registrar; Ratificar só o que já foi revisado pelo Codex.
- **Padrão atual:** Cada DECISOES diz "vale até o proprietário mudar"; registros pendentes com o Codex.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-pcm:docs/pcm-simplificado/DECISOES.md:27`, `sp-safc02:docs/planejar-safra/etapa-unica-3-4-5/DECISOES.md:69`, `sp-sup:docs/suprimentos-simplificado/DECISOES.md:42`, `sp-ben:docs/beneficiamento/DECISOES.md:58`, `sp-cadux:docs/cadastros-ux/REQUISITOS.md:456`, `scratchpad/parecer/APENDICE.md:181`, `sp-proto:tools/prototipo/v37/gen37/areas/processo_os.py:7`.

### PRC-05

- **Pergunta:** Fazer as cinco referências do setor por módulo ainda faltantes (Suprimentos, Manutenção, Beneficiamento) e só então comparar com o mercado?
- **Opções levantadas:** Fazer antes de levar cada módulo à homologação; Fazer só no software real.
- **Padrão atual:** Não pesquisado; o Codex pede não afirmar "acima do mercado" sem prova.
- **Limite:** **DENTRO**.
- **Fontes:** `sp-sup:docs/suprimentos-simplificado/DECISOES.md:45`, `sp-pcm:docs/pcm-simplificado/DECISOES.md:111`, `sp-ben:docs/beneficiamento/DECISOES.md:62`, `scratchpad/parecer/PARECER.md:13`, `PR #47 comentário 6088167538`.

### PRC-06

- **Pergunta:** O que fica só para o software real e quando iniciar a próxima etapa dele (além de F0 e F1), sempre com dados fictícios e sem custo?
- **Opções levantadas:** Iniciar ao fechar o passo 1 do protótipo; Iniciar por módulo validado; Esperar o proprietário voltar.
- **Padrão atual:** F0/F1 autorizadas só com dados fictícios (DEC-2709-01); AGENTS §2 pede comando dele para etapa nova; a mensagem de 09/10 delega as decisões.
- **Limite:** **DENTRO**.
- **Fontes:** `scratchpad/parecer/PARECER.md:462`, `scratchpad/parecer/PARECER.md:539`, `main:docs/DECISIONS.md:25`, `scratchpad/codex-6064114787.md:47`.

### EXT-05

- **Pergunta:** Contratar revisão humana qualificada (segurança e arquitetura) antes do piloto?
- **Opções levantadas:** Contratar antes do piloto.
- **Padrão atual:** Controle pendente; sem ela não há piloto.
- **Limite:** **FORA** · aguarda o proprietário · Contrata profissional e gera custo.
- **Fontes:** `main:docs/parceria/rodadas/R-006-plano-f0-f1.md:96`.

### EXT-08

- **Pergunta:** Fornecer os dados reais da implantação: empresas, fazendas, culturas, protocolos com responsável técnico, plano de contas, alçadas reais, crédito, retenção e conectividade (PRD 20.6)?
- **Opções levantadas:** Na implantação real.
- **Padrão atual:** Tudo sintético.
- **Limite:** **FORA** · aguarda o proprietário · Dado real de cliente e da empresa.
- **Fontes:** `main:docs/PRD.md:5155`, `main:docs/PRD.md:5161`.

### EXT-09

- **Pergunta:** Publicar para usuários reais, iniciar o piloto e aceitar a candidata de produção?
- **Opções levantadas:** Depois da homologação.
- **Padrão atual:** Produção não existe.
- **Limite:** **FORA** · aguarda o proprietário · Publicação a usuários reais e produção exigem aceite explícito dele.
- **Fontes:** `AGENTS.md §3.1`, `main:docs/STATUS.md:35`, `main:docs/DECISIONS.md:95`.

### EXT-12

- **Pergunta:** Aceitar, como usuário, as fatias do protótipo na homologação (ex.: cadastros com seleção que abre detalhe)?
- **Opções levantadas:** Testar quando voltar.
- **Padrão atual:** Segue o desenho; aceite na homologação.
- **Limite:** **FORA** · aguarda o proprietário · Aceite humano dele; os agentes nunca o declaram em nome dele.
- **Fontes:** `sp-cadux:docs/cadastros-ux/DECISOES.md:41`, `AGENTS.md §3.1`.

## Repetições juntadas

| Item | Assuntos que eram a mesma pergunta em lugares diferentes |
|---|---|
| OPE-01 | PEND-OS-01 (DECISIONS), GES-7 (parecer), decisão 1 da seção 7 do parecer, CONF-D10 / AL-01, risco aberto do CTL-3 (PLANO), retorno Codex 6064114787 |
| PRO-01 | PRO-1 e decisão 2 do parecer, pergunta 4 da Colheita, pergunta 4 e D-C27 do Comercial, A-17 do Codex (6070584991), DEC-0510-03 |
| SUP-01 | PEND-CTL-02 (DECISIONS e retorno Codex), parâmetros 1 e 2 do Suprimentos, AL-09 e AL-10 das Configurações |
| SUP-02 | AL-16 das Configurações, "Alçadas reais" do Suprimentos, P2 da PCM × Suprimentos, PRD 20.6 |
| SUP-04 | DEC-07 do PRD, tolerância do Suprimentos, P3 da PCM × Suprimentos |
| MAN-01 | MAN-3 e decisão 6 do parecer, D1, P4, P7 e P9 da PCM × Suprimentos, "Alçada da manutenção" das Configurações, delegação do conflito de janela (FORA-DE-ESCOPO) |
| MAN-02 | MAN-10 e decisão 6 do parecer |
| AGR-02 | DEC-08, B-05 do PRD e D-03 da Análise de solo |
| AGR-06 | Itens 1, 2, 14 e linhas 22, 25 e 27 do parecer (AGRO-1, AGRO-4 = OS-6, AGRO-7 = OS-20, CAD-8, GAP-1, GAP-2, OS-15), AGRO-5 e "Quem publica" da navegação |
| OPE-12 | Itens 5, 6, 7 e 21 do parecer (SAF-1, SAF-2 = AGRO-6, SAF-3, GES-4, OS-9, GES-1), PEND-CTL-03, adoção de versão da navegação |
| SUP-11 | Itens 9, 10, 11 e 20 do parecer (OS-1, OS-2 = EST-1 + EST-3, EST-2, CMP-1, CMP-2 ≈ GES-2) |
| MAN-08 | Itens 15, 18 e 19 do parecer (MAN-1 ≈ IR-1, MAN-4, MAN-5, MAN-8, MAN-9) e o S1 do PCM citado pelo Codex (6088167538) |
| PLA-01 | CAD-14 e decisão 4 do parecer, camada Solo da Análise de solo |
| PLA-02, EXT-13 | DEC-01, DEC-05, DEC-09, B-13, B-14 do PRD e perguntas 1 a 5 da Plataforma de assinaturas |
| PLA-DS02 | PEND-DS-02 e o selo "Sobras pendentes" deixado na 8.4.3 pela reconciliação |
| IRR-01 | IR-9 e decisão 3 do parecer |
| SUP-12 | GAP-4 e decisão 5 do parecer |
| PRC-04 | Mudanças de decisões anteriores (D-01 a D-05 do PCM, PEND-SAF registro DEC-0510-xx, registro do Suprimentos de 05/10, rótulo do Beneficiamento, D1 dos Cadastros × DEC-2609-14) e IR-18 (água só na Irrigação, pedido de 01/10) |

## O que foi varrido e limites

- **PRD v3.11 da main:** 73.12 (PEND-01 a PEND-16 e PEND-18), 73.12.1, 74.12 (PEND-DS-01 a 15), 75.8 (PEND-FB-01, FB-02, OP-01, IA-01), 70.4 (DEC-01 a DEC-09 e linhas B de pendência explicitada) e 20.6. Busca por "PEND-", "decisão do proprietário" e "a confirmar".
- **Registro da reconciliação v3.10 (main):** propostas ainda fora do texto normativo, sem linha em 73.12 ou 75.8: PEND-17, PEND-19, PEND-20 a 22, PEND-FB-03 a 06 e PEND-USO-01 a 04. Entraram como itens porque esperam o proprietário, mas não estão no PRD.
- **DECISIONS.md e STATUS.md da main** (`5831eb3`), ADRs 0005 e 0006, OPERACAO.md, rodadas R-006 e evidências de hospedagem.
- **Worktrees <sp->*:** todos os `DECISOES.md`, `ESPECIFICACAO.md` e `FORA-DE-ESCOPO.md` distintos por conteúdo (46 versões únicas), mais `controle-01/PLANO.md` e `desenho/FRENTE-E.md`, `cadastros-ux/REQUISITOS.md`, `culturas/UNIDADES-DE-MERCADO.md` e `navegacao/ESPECIFICACAO.md`. Quando havia versões diferentes do mesmo arquivo, li a da worktree dona da frente.
- **Parecer de 09/10:** seção 7 (seis decisões), passos 1, 2 e 3, tabela de S3 relevantes e apêndice.
- **Comentários do Codex:** cópias em `scratchpad/codex-*.md`, `scratchpad/nav/6080540795-1611.md`, `scratchpad/resp-6079601661.md` e o comentário 6088167538, lido do GitHub com `gh api`.
- **Fora da varredura:** pastas de verificação e evidências (saídas brutas), os 2.633 arquivos `.md` repetidos entre worktrees além das versões únicas, e o histórico da issue #1 que não foi copiado ao scratchpad.
- **Não incluído como pendência do proprietário:** decisões técnicas já resolvidas pelo Codex sem consulta a ele (B-R8, item 12 do PCM, SAF ocupação, N1 a N6 e X-AGR-3, X-CTX da navegação), ADRs 0005 e 0006 (aguardam revisão do Codex, não dele) e defeitos do parecer que não pedem escolha (entram pelos itens de "encaixe" e "frente").
- **Estados a conferir:** PEND-REPO-01 parece resolvida (STATUS mostra a proteção ativa); o Docker Desktop no Mac (EXT-06) não tem registro de resposta depois de 27/09.
- **Normas citadas** (Lei 9.433/1997, padrões de classificação do MAPA, tabelas regionais de adubação) são referências a conferir na fonte e na vigência; nenhuma foi afirmada como fato.
