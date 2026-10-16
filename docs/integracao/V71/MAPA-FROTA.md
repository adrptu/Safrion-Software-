# MAPA-FROTA · Máquinas das O.S. em execução no Mapa, e telemetria pela mesma filosofia

> Proprietário, 16/10/2026 (pedido): "No mapa / OS, tem que ter um botão de 1 clique para ver as máquinas representadas e ícones intuitivos das operações, andando no mapa (as que estão em execução). Melhore o prompt para si mesmo e junto com códex implantem isso da melhor forma possível."
>
> Proprietário, 16/10/2026 (acréscimo): "Deixa opção de telemetria também integrar com essa mesma filosofia."

## Pedido melhorado

**Resultado útil.**

- Gestor, PCP e agrônomo, com **1 clique** a partir do Mapa (em qualquer uma das nove funções) ou da O.S. em execução, veem onde estão agora os conjuntos das O.S. **Em execução**.
- Cada conjunto aparece com o ícone da operação, nunca só pela cor. Mostra também o estado, a fonte e a idade da posição, e quanto falta.
- **Mais 1 toque** abre a O.S.
- O que não se sabe aparece escrito: "Sem sinal há 18 min", "Posição indisponível", "Simulação". Nada é inventado.
- A telemetria real dos fornecedores entra pelo mesmo princípio:
  - conecta-se em até 2 toques no Safrion;
  - as máquinas se vinculam sozinhas pelo número de série, e só a dúvida vai para confirmação;
  - a fonte e a idade ficam sempre à vista;
  - desconecta-se com 1 toque.

**Personas.**

- **Gestor (Ana, gestora e RT):** quer saber quem está trabalhando, quem parou e o que falta, sem ligar para o campo.
- **PCP (Caio):** confere se o conjunto alocado está na O.S. certa, vê conflito de uso e reprograma.
- **Agrônomo RT (Ana):** confere a operação em curso no talhão certo, por exemplo pulverização perto de área sensível ou de colheita.
- **PCM (Otávio):** vê onde está o ativo parado ou impedido. Não vê o nome do operador.
- **Operador (Marcos):** é fonte e titular do dado. A posição do celular dele só é usada com aviso, durante o turno aberto, e ele pode parar.

**Restrições.**

- O Mapa não ganha função nova (DEC-1610-09). O botão vai para a barra de ferramentas, sobre o mapa (DS-50). A O.S. não ganha a visão Mapa (DEC-2609-09). "Ver no mapa" é um link (BOT-08).
- O estado da O.S., o estado operacional da máquina e a situação da posição são três eixos separados. Nenhum deles se deduz do outro.
- No protótipo, "andando" é uma **simulação rotulada**. Ela nunca produz apontamento, consumo, carga, avanço nem fase.
- Sem localização confiável, não há ponto no mapa (PRD 8.4.4, 44.11.2 e 69.9.3).
- Localização de pessoa é dado pessoal (LGPD, art. 5º, I). Ela fica desligada por padrão (NFR-17), é mostrada só a perfis com motivo e só durante a execução.
- O Safrion só lê dados do equipamento. Nenhum comando vai à máquina (PRD 1.2, l.155).
- Credencial real, conta e contrato com fornecedor ficam com o proprietário (AGENTS §2; ENG-017). No protótipo existe só o ambiente de testes simulado, rotulado.

**Pronto quando.**

- M1–M22 (F1), N1–N9 (F2) e T1–T14 (F3a e F3b) passam, cada um na sua fatia e com a contraprova.
- K1–K10 ficam no teto, e nenhum cenário de hoje piora.
- A conferência em Decimal continua 54/54.

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: MAPA-FROTA / em 1 clique no Mapa (qualquer função) ou na O.S. em execução, ver onde estão agora os conjuntos das O.S. Em execução, o que fazem (ícone da operação), o estado, a fonte e a idade da posição e quanto falta, e abrir a O.S. com +1 toque; telemetria real pela mesma filosofia / gestor, PCP, agrônomo RT, PCM; operador como fonte e titular do dado
Requisitos do PRD e fora do escopo: IN-04 (PRD l.397–421), 8.4.4 e OSFASE-07/13 (l.3002–3036), 44.11.1–2 (l.7487–7507), 69.9.3 (l.10302), 67 (l.9514–9540), MAPUX-06/07 (l.9549–9550), DS-14/15 (l.14111–14112), DS-48 a 52 e DS-62 (l.14422–14464, 14587–14593), 74.7.3–4 (l.14641–14670), DS-65 a 68 (l.14720–14723), 36.7 (l.6522–6530), 64 (l.9284) e 64.5 (l.9298), 12.4 (l.4627), RF-INT-004/007/008 (l.2698–2702), CF-03 (l.1845–1857), NFR-17/18 (l.4681–4682), CONC-09/10/13/20/21 (l.12898–12971), AC-110/111 (l.13615–13616), PEND-06/08/13 (l.13682–13689), 1.2 (l.155); DEC-2609-03/06/09/12, DEC-1610-04/09/11/12; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex (produto e QA; crítica antecipada 6223268675) e Gemini (três contraprovas, pelo conector do Codex) / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: leitura em c90b062 (claude/v44-v69-mapa, worktree limpo) e PRD/DECISIONS da main 94e19e4 / só este arquivo e mapa-frota/; os arquivos de produto estão em §Fatias e só se reservam quando a fatia entrar
Aceite e comando de verificação: M1–M22, N1–N9, T1–T14 e K1–K10 abaixo / python3 -B docs/integracao/V71/mapa-frota/mapa_frota_chk.py (54/54, executado em 16/10); produto: node frota_unit.js; python3 -B mapa_frota_test.py (especificados)
Estado / impedimento / próximo passo: especificado, sem código. A F1 entra quando houver vaga no teto de três frentes (§3.6), com autoria única de areas/inicio.py combinada com EX-42, MAPA-MIP-PROD, SOLO-FOLHA-NIVEIS e SAF-MAPA. A integração real depende do proprietário (custo e contrato)
```

## Revisão (Codex e Gemini)

- **Codex:** produto, aceite, cliques e QA. Fez uma crítica antecipada do desenho inicial, antes deste arquivo (comentário 6223268675 no PR #47).
- **Gemini, pelo conector do Codex:** contraprova de três pontos depois:
  - localização presumida;
  - transição de sinal;
  - foco e movimento.
- **Peso das decisões abaixo:** são proposta do autor. Viram decisões dos agentes só depois dos dois pareceres escritos (§3). O Codex registra o SHA-256 do texto revisado.

| Revisor | SHA-256 do texto revisado | Data | Parecer |
|---|---|---|---|
| Codex (crítica antecipada) | não se aplica: foi sobre o desenho inicial, antes deste arquivo | 16/10/2026 | Comentário 6223268675. Sete pontos, aceites propostos, pedido de matriz estado × fonte × ação e da lista de arquivos da F1. Tratamento abaixo |
| Codex (revisão deste arquivo) | pendente | — | pendente |
| Gemini (três contraprovas) | pendente | — | pendente |

**Tratamento da crítica antecipada (6223268675):**

| # | Ponto | Tratamento |
|---|---|---|
| 1 | Separar o estado da O.S., o estado operacional e a qualidade/idade da posição. "Sem sinal" não prova parada nem deslocamento. Sem posição, fica na lista com "Posição indisponível", nunca no centro do talhão. O.S. pausada não some | **Aceito.** Decisões 3 e 4, §Entidades e estados, §Matriz, M4, M5 e M7; conferência L7 e P3 a P6 |
| 2 | Área apontada e ha/h não determinam trajetória, rumo nem coordenada. O percurso sintético é explícito e fica dentro da geometria demonstrativa. Nunca produz apontamento, consumo, carga nem avanço. O rastro leva a marca de simulação | **Aceito.** O primeiro desenho dizia que a posição seria "coerente com a área apontada": isso saiu. O percurso é um dado declarado da fixture; a área e a velocidade só servem para conferir que ele é plausível (G4), sem relação com a área feita. Decisões 7 e 13, M14, M19 e N2 |
| 3 | Contrato mínimo da leitura, com ordem pelo instante observado: duplicata ou atrasada não faz voltar; futura ou inválida não vira atual. O limite de idade vem do contrato da fonte, e a fixture declara o seu | **Aceito.** Decisão 8 e §Contrato de dados. O oráculo vai de L1 a L10. Limites: fixture com 60 s; bomba e pivô com 15 min, número já aceito na DEC-1610-04; telemetria de máquina pelo contrato do fornecedor; app pela configuração do app. Não há limite universal |
| 4 | Uma representação por conjunto, com os componentes identificados, sem clonar trator e implemento. O mesmo ativo em duas O.S. incompatíveis vira conflito com acesso às origens | **Aceito.** Decisão 6, M8 e K1–K3. Detalhe acrescentado: duas O.S. do mesmo agrupador (OS-LOTE) não são conflito |
| 5 | "Ver no mapa" abre um recorte temporário e acende a camada em 1 clique. A volta preserva o contexto. Se um filtro esconderia o alvo, o recorte é explicado. Sem autorização, nada de operador nem posição, nem em dica ou lista | **Aceito.** Decisões 14 e 15, M12 e M13 |
| 6 | "Pausar animação" e a redução de movimento param a interpolação, mas o estado e a idade seguem. Pausar a animação não pausa a operação. Nada de pan automático nem de reordenação que roube o foco. Em zoom baixo, o grupo abre a lista, e o selecionado continua identificável | **Aceito.** Decisões 11 e 12, M10, M11, N3, N4 e N6 |
| 7 | "Carga atual" só com fato. O EX-38 é projeção; sem fato, aparece "Preparo previsto" ou nada | **Aceito.** Decisão 9 e E1–E2. Na colheita, a carga é fato (c.producao.cargas). Na pulverização não há fato de carga no cenário, então aparece "Preparo previsto (projeção da O.S.)" |
| — | Aceites propostos pelo Codex | Todos entram: pausa e impedimento (M7); fim ou cancelamento com o painel aberto (M9); posição ausente, velha, fora de ordem ou futura (M4–M6); conjunto duplicado (M8); usuário sem autorização (M13); 20 marcadores sobrepostos (M11); ida e volta com filtro (M12); Enter, Espaço e Esc, foco, 390 px, redução e pausa (M10, M16, M17, N3 e N4); a animação e a reentrada não mudam o domínio (M14 e N8); lista e mapa com a mesma origem e idade (M15) |

## Situação em 16/10 (lida no código em c90b062)

`G` = `tools/prototipo/v37/gen37`.

| # | Achado | Onde |
|---|---|---|
| A1 | A barra tem nove funções em abas, e a barra de ferramentas fica sobre o mapa: Selecionar área, Medir, Desenhar, Importar, Tela cheia e Importar laudo (só no Solo). É ali que o alternador "Máquinas" cabe sem criar função | `G/areas/inicio.py:108-113` (LAYS), `:1626-1640` (`_rail`), `:1526-1535` (`tools`) |
| A2 | Há dois desenhos. A Santa Rita é um SVG demonstrativo (viewBox 1000 × 620). A Lagoa Grande usa MapLibre GL 5.9.0 com imagem Sentinel-2 e marcador HTML por pivô. A fazenda padrão do Mapa é a Lagoa Grande | `inicio.py:1407-1438` (`_mapsvg`), `:102-105` (GEO), `:569` (maplibre-gl@5.9.0), `:616-638` (`lgEnsure`, marcadores em `:636`), `:520` e `:1111` (padrão Lagoa Grande) |
| A3 | A função Ordens de serviço filtra a fase e mostra Fases, Avanço, Atrasos e Impedimentos. O Avanço é "área apontada ÷ área das ordens abertas, sem geometria executada" | `inicio.py:117-119`, `:790-803` (`osCls`), `:815-816` (`osFonte`) |
| A4 | O Mapa lê a fase, o realizado e os selos da O.S. no cenário compartilhado (`cenGet`), igual à tela O.S. A sobreposição usa a mesma fonte | `inicio.py:685-707` (`mapOrdsCen`) |
| A5 | **Não existe posição de máquina em nenhum dado nem tela.** A conexão de demonstração "Telemetria de máquinas" diz trazer "horímetro e posição dos tratores e da colhedora", mas nenhuma tela usa posição, e o horímetro dos tratores vem de apontamento ou abastecimento: só bombas e gotejo têm "Telemetria". GPS aparece só nos pontos do MIP e no texto do catálogo. Coerência S4: a F3a corrige o texto | `G/dados_config.py:23-24`; `G/dados_manutencao.py:30-44`; `G/dados_mip.py:12, 242-247` |
| A6 | O cenário inicial tem cinco O.S. Em execução: OS-0420 (plantio, T4, "Impedida · ativo bloqueado") e OS-0421 (pulverização, T1+T2, 190 de 350 ha) na Santa Rita; OS-0505 (colheita, Pivô 19), OS-0506 e OS-0507 (fertirrigação, Pivôs 4 e 5) na Lagoa Grande. Conferência C1 | `G/dados.py:106-109`; `G/dados_lagoa_safra.py:122-124` |
| A7 | O conjunto vem da alocação, a "fonte única de quem e o que está em cada O.S.". No dia 26/09: OS-0421 com Trator 03 + PJ-3030 (C2); OS-0420 com Trator 02 + Plantadeira, alocação condicional, e a O.S. continua "Impedida" (C3). Há um conflito latente em 24/09, 06:00–11:00: PJ, Marcos e Paula estão ao mesmo tempo na OS-0421 e na OS-0424 (C4). A Lagoa Grande não tem nenhum recurso na alocação (C5) | `G/alocacao.py:10-36` (blocos em `:21`, `:26`, `:28`), `:44` (fonte única), `:48` (`alVigente`), `:62` (`alDaOrdem`) |
| A8 | O conjunto padrão de pulverização no CD-03 é Trator 02 + PJ-3030, e o rendimento r1 é "Trator 02 + PJ-3030 36 m". A OS-0421 está alocada com o Trator 03. Não é erro; o mapa segue a alocação (C6) | `G/dados_cad.py:89`; `G/dados2.py:90`; `alocacao.py:21` |
| A9 | Rendimento = largura × velocidade × eficiência (DEC-2609-03): 36 m × 8 km/h × 75 % = 21,6 ha/h; a plantadeira dá 6,804, que o catálogo arredonda para 6,8. Conferência R | `G/dados2.py:89-98`; `G/dados_cad.py:69-78` |
| A10 | O app tem um aparelho só (operador Marcos). O turno guarda `{os, ini, d, chave, pausas, fim}`, mas **não guarda o recurso**: no protótipo, o vínculo entre o conjunto e a execução só existe pela alocação. "Sem sinal" no app é `c.app.online` | `G/cenario.py:100-102`; `G/cenario.js:493-505` (turno e pausa), `:801` (`cenSinal`); `G/areas/mobile.py:185` (`mbPausado`) |
| A11 | O preparo do EX-38 é projeção: tanque ÷ vazão dá as cargas (E1–E2). Não há fato de carga de pulverização no cenário. Na colheita, a carga é fato | `G/cenario.js:93-127`; `G/cenario.py:61`; `G/dados_producao.py:76-94` |
| A12 | A demonstração tem duas datas de "hoje": 23/09/2026 no Mapa e nos dados, 26/09/2026 no cenário e no app. A sobreposição usa a data operacional do cenário. Achado S4, não corrigido aqui | `inicio.py:224`; `G/dados.py:5`; `G/dados_config.py:12`; `cenario.js:537` |
| A13 | Os responsáveis das O.S. da Lagoa Grande (Sérgio, Wesley, Joaquim…) não estão no cadastro de pessoas (CD-04) | `dados_lagoa_safra.py:121-128` × `dados_cad.py:106` |
| A14 | A tela Integrações (CF-03) lista cinco conexões de demonstração, com o selo "Demonstração · nenhuma conexão real" e a credencial "Não configurada · cofre do ambiente". É a base da F3a | `G/areas/configuracoes.py:282-341`; `dados_config.py:18-29` |
| A15 | Há funções de geometria prontas para reaproveitar: ponto no polígono, raio pela área e círculo | `G/talgeo.js:18-25` |
| A16 | O contexto do mapa fica no `sessionStorage` 'mapa-ctx', e já existe entrada por hash (`#car`). O `#frota=OS-xxxx` segue o mesmo padrão | `inicio.py:1106-1111`, `:1260-1262` |
| A17 | A O.S. não tem visão Mapa (DEC-2609-09) | `G/areas/processo_os.py:1656` |
| A18 | Os ícones (`engine.ICONS`) não têm trator, pulverização, plantio nem adubação. Têm Colheita, truck, Irrigação, pivot e wrench | `G/engine.py:12-92` |
| A19 | O próximo passo da O.S. Em execução é "Registrar apontamento". "Ver no mapa" fica como link secundário e não disputa a primária | `processo_os.py:616-640` (`osProx`) |

## O que o PRD já decide (não se reescreve aqui)

| Regra | Fonte |
|---|---|
| Ativo fixo aparece na localização conhecida. Ativo móvel sem localização atual confiável fica na lista, sem ponto fictício | 8.4.4 (l.3008); 69.9.3 (l.10302) |
| Sem geometria executada, o progresso numérico não gera área espacial inventada | OSFASE-07 (l.3024); 8.4.4 Avanço espacial |
| Máquina sem telemetria não fica invisível: usa apontamento ou checklist, com fonte e idade. Informação vencida mostra "A confirmar". Sem localização confiável, nada de posição inventada | 44.11.2 (l.7505) |
| Sem apontamento nem telemetria atual, o estado é desconhecido, nunca ocioso presumido | 44.9 (l.7442) |
| A ocupação tem os valores Livre, Reservada, Operando, Parada operacional e Fora do calendário. Condição técnica e ocupação são eixos separados | 44.11.1 (l.7495–7497) |
| GPS ajuda na localização e na área, mas não prova aplicação, qualidade nem presença contínua | 64 (l.9284) |
| Sem localização contínua de pessoas por padrão. Finalidade, acesso, minimização e retenção por classe de dado | NFR-17 (l.4681) |
| Clima, sensores e telemetria têm provedor identificado; qualidade e atraso ficam visíveis; a falta vira leitura manual ou estimativa sinalizada | 12.4 (l.4627); RF-INT-004 (l.2698) |
| Credencial por empresa, integração e ambiente, com escopo mínimo, validade, rotação e revogação; segredo fora de código e de log | RF-INT-008 (l.2702); NFR-18; CF-03 (l.1845–1857) |
| Retorno da aplicação e telemetria guardam posição e qualidade GNSS; a lacuna fica "sem informação", não aplicação zero; a presença da máquina não prova dose | 36.7 (l.6524–6526) |
| Precedência entre relatos do mesmo fato: telemetria **homologada** acima de leitura manual, declaração e estimativa; acima da tolerância, vai à conferência | CONC-09/10 (l.12898–12899); AC-110 |
| A hora do aparelho não escolhe vencedor; o instante estimado traz incerteza | CONC-20/21 (l.12970–12971) |
| Medir não é comandar: o comando remoto fica desligado | 1.2 (l.155); 36.6 (l.6516) |
| Movimento reduzido: transição de 0 ms, e nenhuma informação depende de animação. Alvo de 44 px no toque | DS-14/15 (l.14111–14112) |
| Ferramentas sobre o mapa; selo-resumo no cabeçalho; painel do talhão só com seleção; lista equivalente | DS-50, DS-52 e DS-62 (l.14439–14464, 14587–14593); MAPUX-06 (l.9549) |

## Referências do setor (AGENTS §3.3)

Pesquisa feita em 16/10/2026. Cada linha diz como a fonte foi conferida:

- **lida:** corpo da página aberto;
- **índice:** página dinâmica ou bloqueada, conteúdo pelo resumo do buscador;
- **revenda:** guia de concessionário.

Estar no mercado não prova regra de domínio; o aceite se mede pelos K e M abaixo.

| Referência | O que mostra de máquina no mapa | Decisão |
|---|---|---|
| **John Deere Operations Center:** [guia do mapa](https://support.koenigequipment.com/how-to-use-the-map-in-john-deere-operations-center-to-see-your-fields-and-equipment) (revenda, lida); [Develop with Deere](https://developer.deere.com/dev-docs/machine-device-state-reports) e [Machine Engine Hours](https://developer.deere.com/dev-docs/machine-engine-hours) (índice) | O ícone mostra a posição atual. Três estados: trabalhando, ocioso e em transporte. Com modem JDLink, atualiza "roughly every 5 seconds". Ao tocar, mostra quando a máquina trabalhou ou se moveu pela última vez. Na API: Machine Location History, com latitude, longitude e altitude no intervalo do dispositivo, e Breadcrumbs, registrados só enquanto trabalha | **Adotar** estado por ícone e palavra, e "última leitura há…". **Adaptar** o histórico para a barra de tempo (EX-42, depois). **Adiar** a conexão real (F3a sandbox; real com o proprietário) |
| **Case IH FieldOps (CNH):** [página do produto](https://caseih.com/en-us/unitedstates/products/precision-technology/case-ih-fieldops) (lida); [FieldOps API](https://develop.cnh.com/api-guides/fieldops-api) (índice; acesso bloqueado na rede) | "See machine status, location, and estimated job completion times at a glance"; histórico por dias e safras; frota mista. A API segue a ISO 15143-3 e usa OAuth 2.0 | **Adotar** "quanto falta", adaptado: saldo apontado em ha e estimativa rotulada no rendimento de referência, nunca pelo trajeto. **Adotar** frota mista por adaptador |
| **PTx Trimble Fleet:** [páginas de ajuda](https://ww2.agriculture.trimble.com/software-user-guide/fleet-feature-comparison) (índice; redirecionam para ptxag.com) | Veículos no mapa e "última localização". Só o modem tradicional rastreia a máquina desligada. Recursos dependem de licença | **Adotar** "última posição" separada de "atual". **Descartar** rastrear máquina desligada: não muda decisão e fere a minimização |
| **Climate FieldView:** [Cab e RemoteView](https://assets-0.climate.com/getting-started/fieldview-101) (índice) | O RemoteView mostra só o equipamento conectado agora ao FieldView Cab com internet. Há mapa do trajeto do preparo de solo | **Adotar** "atual só com leitura dentro do limite". **Adiar** o mapa de cobertura (as-applied, PRD 36.7) |
| **Aegro Máquinas:** [conexão com a John Deere](https://aegro.com.br/suporte/integracoes-adicionais/aegro-maquinas-john-deere/) (lida; atualizada em 05/08/2026) | "Conectar", login John Deere e concessão de permissões por nível (Equipamento, Localizações, Trabalho). A máquina chega com o nome dado na John Deere e é conciliada **à mão** na importação | **Adaptar** conectar em poucos toques. **Descartar** vincular toda máquina à mão: aqui o vínculo é automático por fabricante e nº de série, e só a dúvida vai para confirmação |

**Integração e padrões** (para a F3a, com a mesma regra de conferência):

- **AGCO Connect** ([lançamento, 2019](https://investors.agcocorp.com/node/20231), índice): rastreio em tempo real no mapa, combustível, horas de motor e trajeto.
  - O nome "Fuse" não apareceu nas fontes de 16/10; a marca atual da conectividade AGCO se confirma com o fornecedor.
- **CNH:** o AFS Connect, lançado em 2019 (índice), é a origem do FieldOps descrito acima.
- **Trimble e Raven:** o PTx Trimble Fleet está na tabela acima. A Raven não foi conferida nesta pesquisa; entra quando houver cliente com o equipamento.
- **Solinftec** ([site](https://www.solinftec.com/pt-br/), índice; artigo com 403): monitoramento em tempo real, computador de bordo e funcionamento sem internet no campo.
- **ISO 11783-10** ([ISO 11783-10:2015](https://scc-ccn.ca/standardsdb/standards/8154090), índice; norma paga): TaskData/ISOXML, com registro de tempo e posição (seção 6.2 na edição de 2009).
- **AgGateway ADAPT** ([wiki](https://aggateway.atlassian.net/wiki/x/N4DcB), índice): modelo comum (ADM) compatível com a ISO 11783-10; plug-ins por fabricante, os da comunidade sob licença EPL.
- **ISO 15143-3 / AEMP 2.0** (índice; fichas de fabricantes): última localização, horas de operação acumuladas e combustível usado. Fontes de terceiros apontam consulta **horária** em algumas APIs.
  - Risco R5: "ao vivo" depende do plano do fornecedor.
  - A tela mostra a idade real, sem prometer tempo real.

**Acessibilidade e privacidade:**

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/): 2.2.2 (pausar, parar, ocultar), 2.3.3 (animação disparada por interação), 2.5.8 (tamanho do alvo), 1.4.1 (uso da cor) e 4.1.3 (mensagens de estado).
- [LGPD, Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm): art. 5º, I (dado pessoal) e art. 6º, I e III (finalidade e necessidade).
  - O Planalto respondeu 503 em 16/10; o texto foi conferido por cópia.
  - A revogação "facilitada" (art. 8º, § 5º) fica a conferir no original.

## Decisões propostas (Claude; valem depois dos pareceres)

1. **Botão de 1 clique, sem função nova.**
   - "Máquinas" entra na barra de ferramentas do mapa (DS-50) como alternador (`aria-pressed`). Leva ícone de trator e o contador "(N)" das O.S. Em execução no recorte, e fica visível nas nove funções e na tela cheia.
   - Ligar põe uma camada sobre a função ativa sem mudar as cores, rótulos, filtros e números dela.
   - Ao lado, "Lista (N)" abre a lista equivalente no painel direito.
   - Ligado ou desligado fica lembrado no 'mapa-ctx', como a função.
   - O cabeçalho continua com o selo-resumo (DS-62): não há primária nova.
   - Na O.S. Em execução, "Ver no mapa" é link secundário (BOT-08) no detalhe e no ⋯ da linha (TAB-05).
   - *Dano evitado:* uma função nova quebraria a DEC-1610-09; esconder as máquinas numa função faria perder a camada em análise.
2. **Universo: só O.S. Em execução,** lidas no cenário (`cenGet`, a mesma fonte de `mapOrdsCen`), na fazenda e safra do contexto.
   - Pausada e impedida continuam: são Em execução com selo.
   - A liberar, Liberadas, Em conferência, Encerradas e Canceladas nunca entram.
   - O filtro Cultura não esconde máquina, porque ela pode estar fora de talhão; o talhão fora do filtro fica neutro.
   - *Dano evitado:* mostrar como "em campo" uma ordem que não começou ou já terminou; esconder a parada que pede ação.
3. **Três eixos separados:**
   - estado da O.S., que vem do cenário;
   - estado operacional do conjunto (Trabalhando, Deslocando, Parada, Desligada ou Desconhecido), com fonte e hora próprias;
   - situação da posição (Atual, Sem sinal há N min, Posição indisponível), com fonte, hora, idade e qualidade.
   - Nenhum se deduz do outro: "sem sinal" não é "parada"; pausa informada não é "sem sinal"; "desligada" informada pela fonte não é "sem sinal".
   - *Dano evitado:* mandar socorro a uma máquina que só perdeu o sinal, ou achar que trabalha uma que parou.
4. **Sem posição, sem ponto.** Sem leitura válida, o conjunto fica só na lista com "Posição indisponível · motivo". Os motivos:
   - sem fonte vinculada;
   - sem conjunto alocado;
   - app sem turno aberto;
   - perfil sem permissão.
   - Nunca no centro do talhão nem no "local" do cadastro.
   - *Dano evitado:* procurar a máquina no lugar errado; dar falsa confiança.
5. **Ícone por operação, nunca só cor.**
   - A família vem da operação da atividade da O.S. (catálogo), não do texto do tipo. Tabela abaixo.
   - O marcador tem fundo `cor.texto.principal`, ícone branco, anel branco de 2 px e rótulo curto com halo ("T03 · Pulverização").
   - O selo de estado tem forma e palavra.
   - A legenda mostra os ícones presentes e os estados.
   - *Dano evitado:* leitura falhar com daltonismo, sol forte ou tela pequena; ícone tirado do texto divergir do catálogo.

   | Família | Operações (catálogo) | Ícone | Texto curto |
   |---|---|---|---|
   | Pulverização | Pulverização, dessecação, fungicida, herbicida | barra com gotas (novo) | Pulverização |
   | Plantio | Plantio, plantio de mudas, semeadura e transplante | broto (novo) | Plantio |
   | Adubação e correção | Adubação a lanço e de cobertura, calagem, gessagem, fosfatagem | leque de grânulos (novo) | Adubação |
   | Preparo de solo | Preparo do solo, de canteiros, reforma | disco de grade (novo) | Preparo |
   | Colheita | Mecanizada, de frutas, do café, de cana, de hortaliças | `Colheita` (existe) | Colheita |
   | Transporte | Carreta, graneleiro, transporte interno | `truck` (existe) | Transporte |
   | Irrigação e fertirrigação | Ativo fixo: só na lista (decisão 18) | `Irrigação` (existe) | Irrigação |
   | Outra | Tratos culturais, roçada, poda | `wrench` (existe) | nome da operação |

6. **Um marcador por conjunto vinculado à execução** (trator ou colhedora + implemento).
   - A posição é a do componente que tem fonte; os componentes aparecem no painel.
   - Ativo em duas O.S. Em execução fora do mesmo agrupador: selo "Conflito · também na OS-xxxx" nos dois, com acesso às duas origens. Nada se escolhe em silêncio (AC-111).
   - No mesmo agrupador (OS-LOTE): um marcador com as O.S. do grupo e sem conflito.
   - No protótipo, o vínculo é a alocação do dia operacional, rotulada "pela alocação". No software real é o turno ou apontamento com o recurso (execução).
   - *Dano evitado:* dois marcadores para um trator; conflito de uso simultâneo escondido.
7. **"Andando" no protótipo é simulação rotulada.**
   - Percurso sintético explícito na fixture:
     - passadas paralelas a cada 36 m, com recuo de 18 m nas cabeceiras, dentro da geometria demonstrativa;
     - na Lagoa Grande, em metros relativos ao centro do pivô, para valer com a geometria real ou a sintética sem gravar coordenada real.
   - Velocidade declarada: 8 km/h na pulverização; 3 km/h com paradas na colheita.
   - Leitura a cada 10 s; limite de idade de 60 s; tempo real, sem acelerar.
   - O relógio é o da data operacional do cenário com a hora do navegador (como `cenAgora`). A simulação roda em qualquer hora e **não segue a janela da alocação**, e isso fica escrito na dica do selo.
   - A simulação nunca produz apontamento, consumo, carga, avanço nem fase. A área feita e o saldo vêm só do cenário.
   - A marca "Simulação" aparece no marcador (dica e `aria-label`), na lista, no painel e no rastro. A legenda leva o selo persistente "Posições simuladas · demonstração".
   - *Dano evitado:* confundir demonstração com telemetria; o relógio da animação mexer em área ou estoque.
8. **Contrato de leitura com ordem e idade por fonte** (§Contrato).
   - Vale o instante **observado**. Duplicata é ignorada; leitura atrasada só completa o rastro; futura ou inválida é recusada; salto impossível fica suspeito até a leitura seguinte confirmar.
   - O limite de idade é o da fonte; a fronteira é inclusiva (L6).
   - No software real, o relógio é o do servidor, e o instante do app é estimado com incerteza (CONC-20/21).
   - *Dano evitado:* a máquina "voltar" no mapa; leitura futura virar atual; posição velha parecer atual.
9. **Painel com 1 toque e "Abrir O.S." com +1.** O painel mostra:
   - O.S. e versão;
   - operação (ícone e nome);
   - talhão;
   - conjunto (componentes);
   - estado operacional, com fonte e hora;
   - posição, com fonte, hora, idade e qualidade;
   - quanto falta: "190 de 350 ha apontados · saldo 160 ha · ≈ 7,4 h no rendimento de referência (estimativa)" (E3);
   - velocidade da leitura;
   - carga só com fato:
     - colheita: "Última carga CG-… às hh:mm";
     - pulverização: "Preparo previsto (projeção da O.S.): 6 cargas de 30 ha, a última com 10 ha" (E1–E2);
     - sem dado, o campo some.
   - Operador: nome só para gestor e PCP; para os outros perfis, "operador da O.S.".
   - Primária: **Abrir O.S.** Secundárias: "Ver impedimento", quando houver, e "Ver talhão".
   - *Dano evitado:* carga prevista virar abastecida; nome e posição expostos a quem não coordena pessoas.
10. **Lista equivalente.**
    - Fica no painel direito; no celular, numa folha inferior.
    - Colunas: Conjunto, Operação, O.S., Talhão, Estado, Posição (fonte · idade) e Feito/saldo.
    - A ordem é estável, por O.S. (não por distância nem por recência).
    - Enter ou Espaço abre; Esc volta e devolve o foco à linha ou ao marcador de origem.
    - *Dano evitado:* quem usa teclado, leitor de tela ou tela pequena perder a informação; reordenação roubar o foco.
11. **Movimento acessível (F2).**
    - O marcador interpola entre leituras.
    - Com `prefers-reduced-motion`, sem interpolação nem transição: a posição muda só a cada leitura.
    - **"Pausar animação"** (WCAG 2.2.2) congela as posições exibidas com o rótulo "Posições de hh:mm:ss". O estado e a idade continuam a se atualizar. Não pausa a operação.
    - Sem pan automático.
    - A idade escrita se atualiza a cada 15 s.
    - Só a mudança de estado da máquina selecionada vai para a região `aria-live` "polite".
    - Com a página oculta, nada se anima.
    - *Dano evitado:* distração ou desconforto; leitor de tela falando sem parar; a pessoa perder o lugar.
12. **Agrupamento.** Marcadores a menos de 28 px na tela viram o botão "N máquinas" (44 px), que abre a lista dos N. O selecionado fica fora do grupo, com anel de seleção.
    - *Dano evitado:* 20 marcadores empilhados, ilegíveis e inalcançáveis.
13. **Rastro curto (F2).**
    - Só do turno corrente da O.S. Em execução, nos últimos 30 min.
    - Linha fina de 2 px, nunca faixa com largura: não é área executada (OSFASE-07).
    - Segmentado por fonte: telemetria contínua, app tracejado, simulação pontilhada e marcada.
    - Quebrado nas lacunas maiores que o limite. A leitura atrasada preenche a lacuna com marca.
    - Some quando a O.S. sai de Em execução.
    - *Dano evitado:* o rastro parecer área aplicada; fontes misturadas sem marca.
14. **"Ver no mapa" com recorte temporário.**
    - `IN-04.dc.html#frota=OS-0421` abre na fazenda e safra da O.S., com Máquinas ligada, o conjunto selecionado, o painel aberto e o mapa enquadrado.
    - Se o filtro salvo esconderia o alvo, aparece a faixa "Recorte temporário: OS-0421 · Sair do recorte".
    - O 'mapa-ctx' não muda até a pessoa mexer.
    - O Voltar (do navegador ou "Voltar à OS-0421") devolve a O.S. com a visão, os filtros e o foco.
    - Sem permissão, a mesma entrada abre a lista sem posição.
    - *Dano evitado:* perder o contexto de trabalho; filtro esconder o alvo em silêncio.
15. **Permissão e LGPD** (§Privacidade).
    - Veem a posição: gestor, PCP, agrônomo e PCM.
    - Veem o nome do operador junto da posição: gestor e PCP.
    - Os demais perfis veem só a O.S. e "Posição restrita ao seu perfil", nada no DOM, na dica ou no `aria-label`.
    - *Dano evitado:* vigilância indevida; exposição de dado pessoal.
16. **Um relógio só.** A idade, a lista e o painel usam o mesmo "agora" e o mesmo arredondamento (M15).
17. **EX-42.** Máquinas mostra só o agora. Com a barra de tempo noutra data, a camada se desliga e avisa "Máquinas: só no tempo atual". "Reproduzir o trajeto do dia" fica para depois.
18. **Ativos fixos de irrigação** (pivô, gotejo, bomba): ficam só na lista, com "Ativo fixo · ver na Irrigação" (link para a IR), sem marcador móvel nem rastro.
    - *Dano evitado:* duplicar a função Irrigação; marcador no centro do pivô parecer máquina.
19. **Telemetria real pela mesma filosofia** (seção própria abaixo; F3a e F3b).
20. **Só leitura.** A conexão traz dados e não leva nada à máquina (`leva: nada`). Comando remoto e envio de rota ficam fora (PRD 1.2).

## Entidades e estados

| Entidade | Estados visíveis | Fonte | Próxima ação |
|---|---|---|---|
| O.S. (existente) | As cinco etapas. Só Em execução entra. Selos: turno pausado, impedida, parcial | cenário (`c.ordens[id].etapa`, selos) | Abrir O.S. |
| Conjunto em execução (derivado, não é fato gravado) | Componentes; vínculo `execucao` (real) ou `alocacao` (protótipo); agrupador; conflito | alocação vigente do dia operacional (protótipo); turno ou apontamento com recurso (real) | Abrir O.S. (o PCP aloca lá) |
| Estado operacional | Trabalhando · Deslocando · Parada (motivo: pausa, impedida, carregando, sem trabalho) · Desligada · Desconhecido | telemetria (velocidade, implemento engajado, motor); app (turno e pausa); O.S. (selo de impedimento); fixture | — |
| Posição | Atual · Sem sinal há N min · Sem fonte (desconectada) · Posição indisponível (motivo) · Restrita ao perfil; origem simulada ou observada | leituras (§Contrato) | — |
| Fonte de posição (conexão) | Desconectada · Conectando · Conectada (ambiente de testes) · Conectada · Erro · Revogada | CF-03 | Conectar · Desconectar |
| Vínculo do equipamento | Vinculado por nº de série · Confirmar vínculo (motivo) · Confirmado (por quem, quando) · Sem ativo no cadastro · Ignorado | CF-03 × CD-03 | Confirmar · Escolher outro · Ignorar · Criar ativo com estes dados |

## Matriz estado × fonte × ação

| # | Situação | O.S. | Estado operacional (fonte · hora) | Posição | No mapa | Na lista | Ação |
|---|---|---|---|---|---|---|---|
| 1 | Trabalhando | Em execução | Trabalhando (telemetria ou simulação · 10:42:10) | Atual · há 8 s · ±3 m | Sólido, ícone, seta de rumo, rastro (F2) | "Trabalhando · 8 km/h · há 8 s" | Abrir O.S. |
| 2 | Deslocando | Em execução | Deslocando (telemetria) | Atual | Sólido, seta, rótulo "deslocando" | "Deslocando · fora do T2" | Abrir O.S. |
| 3 | Turno pausado | Em execução, selo "Turno pausado" | Parada · pausa desde 11:02 (app) | Da pausa (11:02), não "sem sinal" | Sólido, sem seta, selo ‖ | "Parada · pausa desde 11:02" | Abrir O.S. |
| 4 | Impedida | Em execução, selo vermelho | Parada · impedida: texto do selo (O.S.) | Atual ou indisponível | Selo ‖ com a palavra "impedida" e contorno do traço vermelho | "Parada · impedida: Trator T1 em manutenção" | Abrir O.S.; Ver impedimento |
| 5 | Desligada | Em execução | Desligada às 12:03 (telemetria) | Da hora em que desligou | Sólido, sem seta, selo ⏻ | "Desligada às 12:03" | Abrir O.S. |
| 6 | Sem sinal | Em execução | Último conhecido: "Trabalhando às 10:12" | Sem sinal há 18 min | Vazado cinza, imóvel, sem seta; o rastro termina | "Sem sinal há 18 min · última: Trabalhando 10:12" | Abrir O.S. |
| 7 | Fonte desconectada | Em execução | Desconhecido desde 10:40 | "Sem fonte: telemetria desconectada às 10:40 · última há N min" | Igual ao sem sinal | "Sem fonte de posição" | Abrir O.S.; (gestor) Ver integração |
| 8 | Nunca houve posição | Em execução | Pela O.S. ou pelo app | Posição indisponível (motivo) | Nenhum | "Posição indisponível · sem fonte vinculada" | Abrir O.S. |
| 9 | Sem conjunto | Em execução | Desconhecido | Indisponível | Nenhum | "Sem conjunto alocado hoje" | Abrir O.S. |
| 10 | Conflito de ativo | Em execução em duas O.S. | Do ativo | Do ativo | Um marcador por conjunto, selo "Conflito" | Duas linhas "Conflito · também na OS-xxxx" | Abrir cada O.S. |
| 11 | Leitura atrasada, futura, inválida ou suspeita | — | Não muda | Não muda; contador no detalhe da fonte | O marcador não volta | — | — |
| 12 | Sai de Em execução com o painel aberto | Em conferência, Encerrada ou Cancelada | — | — | O marcador sai | A linha sai; o painel avisa "saiu de Em execução (agora …)" | Abrir O.S. |
| 13 | Perfil sem permissão | Qualquer | Só o estado da O.S. | "Restrita ao seu perfil" | Nenhum | Sem posição e sem operador | Abrir O.S. |
| 14 | Ativo fixo de irrigação | Em execução | Da Irrigação | — | Nenhum | "Ativo fixo · ver na Irrigação" | Ver na Irrigação |
| 15 | Origem simulada | Qualquer linha acima | Origem simulada | Idem, com a marca | + "Simulação" | "Fonte: simulação" | — |
| 16 | Barra de tempo noutra data (EX-42) | — | — | — | Camada desligada, com aviso | — | Voltar a hoje |

## Contrato de dados

**Leitura de posição.** É um relato da fonte; não é fato de execução.

| Campo | Tipo e unidade | Regra |
|---|---|---|
| `id` | texto estável da fonte | Deduplica (L2) |
| `fonte` | `{tipo: telemetria \| app \| simulacao \| arquivo, conexao_id, fornecedor, aparelho_id?}` | `arquivo` = ISOXML ou ADAPT importado |
| `origem` | `observada \| simulada` | `simulada` nunca existe em produção; carrega a marca |
| `ativo_id` | ID do CD-03, pelo vínculo | Sem vínculo, a leitura fica na conexão e não vai ao mapa |
| `observado_em` | instante UTC da medição | Ordena (L3); no app, instante estimado com incerteza (CONC-21) |
| `recebido_em` | instante do servidor | Futura se `observado_em > recebido_em + 120 s` (configurável) (L4) |
| `lon`, `lat` | graus WGS 84 (EPSG:4326) | Inválida fora da faixa ou em 0,0 (L5) |
| `precisao_m` ou `qualidade` | m horizontal, ou classe GNSS (RTK fixo, RTK flutuante, SBAS, autônomo, celular) | Mostrada; ausente vira "precisão não informada" |
| `rumo_graus` | 0–359; nulo quando parado | A seta só aparece com posição atual e mais de 0,5 km/h |
| `velocidade_kmh` | decimal | Velocidade implícita acima do máximo da classe (fixture: 60 km/h) deixa a leitura suspeita (L8–L9) |
| `estado_operacional` | `trabalhando \| deslocando \| parada \| desligada \| desconhecido` + `estado_fonte` + `estado_em` | Nunca se deduz pela idade |
| `limite_idade_s` | da fonte | Fixture: 60 s; bomba e pivô: 15 min (DEC-1610-04); telemetria: contrato do fornecedor; app: configuração do app |
| extras (F3b) | `horas_motor_h` + instante; `combustivel_pct`; `area_trabalhada_ha` do segmento (ref. 36.7) | Só leitura. Nenhum efeito sem confirmação do operador ou homologação (§Telemetria) |

**Conjunto em execução.** É derivado e se recalcula a cada leitura do cenário:

```
{os_id, versao, etapa, agrupador_id?,
 componentes: [{ativo_id, papel: trator|colhedora|implemento, nome, classe}],
 pessoas: [{papel: operador|caldeiro, nome (conforme permissão)}],
 vinculo: execucao|alocacao, condicional: bool,
 conflitos: [{ativo_id, os_ids}],
 estado_operacional: {valor, motivo?, fonte, em},
 posicao: {fonte_escolhida, leitura?, situacao, idade_s?, motivo?, origem}}
```

**Escolha da fonte por máquina** (P1–P7): telemetria com leitura atual vence o app com leitura atual. Sem nenhuma atual, vale a última posição conhecida, como "Sem sinal", dizendo de qual fonte. A troca de fonte fica marcada no rastro e no painel.

**Agora.**

- Protótipo: data operacional do cenário (`CEN_DIA_OP`) com a hora do navegador. Os testes controlam o relógio por `window.__frotaRelogio`, um gancho só de teste, como o `window.__LGI` existente.
- Software real: relógio do servidor.

## Telas

**Mapa (IN-04), na peça comum das duas variantes (normal e tela cheia), nos dois desenhos (SVG e MapLibre).**

- **Barra de ferramentas:** "Máquinas (N)" (alternador) e "Lista (N)". Com 390 px, os dois têm 44 px de alvo e quebram de linha com as outras ferramentas, sem rolagem lateral.
- **Marcador:**
  - o visual tem 32 px e a área de toque, 44 px;
  - é um `<button>` com `aria-label` assim: "Trator 03 + Pulverizador PJ-3030 · Pulverização · OS-0421 · Trabalhando · leitura há 8 s · simulação";
  - no SVG, um grupo focável (DS-52 corrige o `role="img"` com botões dentro);
  - no MapLibre, um `maplibregl.Marker` com `<button>`, como os rótulos dos pivôs;
  - fica acima dos talhões, sem roubar o clique deles fora do marcador.
- **Legenda (DS-51):** acrescenta um grupo "Máquinas" com os ícones presentes e os estados (▶ trabalhando, → deslocando, ‖ parada, ⏻ desligada, ◌ sem sinal), mais o selo "Posições simuladas · demonstração".
- **Painel do conjunto:** usa o mesmo contêiner do painel do talhão, com uma primária (Abrir O.S.). Selecionar o marcador não seleciona o talhão.
- **Etiqueta de modo (DS-50):** com Máquinas ligada e nenhum modo ativo, "Máquinas · toque numa máquina para ver a O.S.".

**O.S.:** "Ver no mapa", com ícone de mapa, como link secundário:

- no bloco de recursos da tela de trabalho da O.S. Em execução;
- no ⋯ da linha (TAB-05) da lista e do Kanban, só em Em execução.

**CF-03, App de campo e CD-03:** na §Telemetria.

## Telemetria real com a mesma filosofia (F3a e F3b)

**Onde.** Na tela Integrações (CF-03), que já existe, sem menu novo.

- A linha "Telemetria de máquinas" (`dados_config.py:23`) vira uma linha (cartão em linha, VIS-06) por fonte:
  - John Deere Operations Center;
  - CNH FieldOps (Case IH e New Holland);
  - AGCO (Fendt, Massey Ferguson, Valtra);
  - PTx Trimble;
  - Solinftec;
  - Arquivo padrão (ISOXML/TaskData ou ADAPT, por importação);
  - App de campo (posição do celular no turno).
- Cada linha mostra o estado, as máquinas vinculadas, quantas há a confirmar e a última leitura com idade.
- Tocar abre o detalhe com uma primária:
  - **Conectar**, se desconectada;
  - **Confirmar N vínculos**, se houver dúvida;
  - **Ver máquinas**, se estiver em dia.

**Conectar (≤ 2 toques no Safrion).**

1. O primeiro toque abre a linha do fornecedor; o segundo toca em Conectar.
2. No software real, abre o consentimento OAuth do fornecedor. Os escopos pedidos são de **somente leitura**: equipamentos, localização, horas de motor e trabalho. Os toques nas telas do fornecedor (login, permitir, escolher organização) são contados à parte (K8).
3. Na volta, o vínculo roda sozinho e o resultado aparece numa linha: "12 equipamentos: 10 vinculados por nº de série · 2 para confirmar".
4. No protótipo, o consentimento é uma tela simulada, rotulada "Ambiente de testes simulado · nenhuma conta real", com uma lista fixa de equipamentos sintéticos.
5. **Nenhuma credencial existe no protótipo:**
   - nenhuma chamada a domínio de fornecedor;
   - nada em arquivo, fixture, log ou prompt (ENG-017).
6. No real:
   - o segredo do aplicativo fica no cofre do ambiente;
   - o token, por organização e cifrado no servidor;
   - nunca no navegador;
   - validade, último uso e quem concedeu ficam visíveis, sem segredo (RF-INT-008).

**Vínculo automático** (V1–V8):

- O equipamento do fornecedor casa com o ativo do CD-03 por **fabricante + nº de série (PIN/chassi) normalizado**: maiúsculas, sem espaço, hífen, ponto ou barra. O modelo serve de conferência.
- Um ativo só com fabricante, série e modelo iguais vira "Vinculado por nº de série".
- Vão para a lista curta "Confirmar vínculo", com o motivo:
  - modelo diferente;
  - série repetida no cadastro;
  - fabricante diferente;
  - fornecedor sem série.
- Em "Confirmar vínculo", 1 toque por item: Confirmar o candidato, Escolher outro (só da mesma classe e sem vínculo) ou Ignorar (máquina de terceiro).
- Série desconhecida vira "Sem ativo no cadastro". Saídas: "Criar ativo com estes dados" (pré-preenchido, sem redigitar) ou Ignorar.
- **Nunca se vincula por nome**, nem por nome aproximado (V5).
- O CD-03 ganha os campos fabricante e nº de série (FO-22). Os ativos de demonstração recebem séries sintéticas óbvias ("SINT-JD-6M155-0001").

**Prioridade e qualidade por máquina:** telemetria > app de campo > última posição conhecida (P1–P7).

- A tela mostra a fonte, a hora da leitura e a idade.
- Leitura velha vira "Sem sinal há N min" e para de andar.
- Fonte diferente não se mistura no rastro sem marca.
- Posição velha nunca aparece como atual.

**O que a telemetria traz além da posição:** só o que muda uma decisão, e nada vira fato sozinho.

| Dado | Uso | Regra |
|---|---|---|
| Horas de motor | Leitura de horímetro na Manutenção, com fonte e hora | Abaixo da leitura manual até a homologação do equipamento; homologado, entra na precedência do CONC-09. Sem efeito duplicado |
| Velocidade e estado (trabalhando, ocioso, transporte, desligada) | Estado operacional no Mapa e no painel | É o eixo 2, nunca a fase da O.S. |
| Área trabalhada ou aplicada por segmento (as-applied, 36.7) | Sugestão no apontamento: "21,4 ha segundo a telemetria · confirme" | O operador confirma ou altera, e **nada é apontado sozinho**. Telemetria não homologada × apontamento: divergência acima da tolerância (CONC-10; PEND-06) vira **aviso** na O.S. Homologada: vale o CONC-09/10 do PRD (Em conferência acima da tolerância), sem segunda baixa |
| Combustível (nível ou consumo) | Informação no painel da máquina | Nunca gera abastecimento nem movimento de estoque: o escritor do abastecimento ainda está pendente (PEND-08, fora dos números aceitos na DEC-1610-04) |

**App de campo como fonte** (para máquina sem telemetria; F3b):

- Desligado por padrão em cada fazenda (NFR-17).
- O gestor liga em CF-03, com a finalidade escrita: "posição da máquina da O.S. durante o turno".
- Ao **Iniciar turno**, o operador vê o aviso "A posição deste celular aparece no mapa da fazenda enquanto o turno estiver aberto". O cabeçalho do app mostra "Posição em uso".
- Pausar ou fechar o turno param o envio, e "Parar de compartilhar" faz o mesmo com 1 toque. Nunca há envio fora de turno aberto.
- Sem sinal, as leituras ficam no aparelho e seguem com o instante estimado (CONC-21). Chegando atrasadas, só completam o rastro.

**Desconectar com 1 toque, sem confirmação extra:**

- Revogar o acesso é a direção que protege a privacidade e precisa ser fácil.
- O efeito é imediato:
  - a fonte some;
  - as máquinas dela viram "Sem fonte: … desconectada às hh:mm", com o visual do sem sinal;
  - onde houver app atual, ele assume e a troca fica marcada.
- Os vínculos ficam guardados para reconectar.
- O ato vai para a trilha da Auditoria (CF-04).
- Reconectar pede novo consentimento.

## Privacidade, permissão e segurança

- **Quem vê:**
  - posição: gestor, PCP, agrônomo e PCM;
  - nome do operador ao lado da posição: gestor e PCP;
  - o resto: lista sem posição e sem operador.
  - No software real é uma permissão própria, "Ver localização de máquinas", concedida por papel em CF-01; o servidor nunca envia posição a quem não a tem. No protótipo, o papel do perfil decide (`g2papel`).
- **Quando:** só durante Em execução e no turno.
  - Fora disso, nem o mapa nem a lista consultam posição.
  - Máquina desligada não é rastreada.
- **Retenção (proposta dos agentes, parâmetro publicado por CMD-29):**
  - rastro bruto de posição: 24 h, para conferir o apontamento do dia; depois se apaga ou se agrega sem pessoa;
  - o retorno da aplicação (36.7) segue a retenção da evidência da O.S., sem expor nome fora do vínculo dela.
  - O cliente pode reduzir. O jurídico do cliente (controlador) confere a base legal antes do piloto (risco R6).
- **Segurança:**
  - somente leitura e sem comando;
  - escopo mínimo;
  - credencial fora de código, de log e do protótipo;
  - diagnóstico exportável sem segredo (CF-03);
  - Gitleaks antes de cada envio (AGENTS §3.5).

## Aceites

**F1 · Ver as máquinas** (sobreposição, lista, painel, "Ver no mapa"; posição por leituras simuladas discretas a cada 10 s, sem interpolação nem rastro).

| ID | Caso | Oráculo |
|---|---|---|
| M1 | Universo no cenário inicial | **Santa Rita:** a lista tem exatamente OS-0421 (Trator 03 + Pulverizador PJ-3030, "pela alocação") e OS-0420 (Trator 02 + Plantadeira 24 linhas, alocação condicional, "Parada · impedida", "Posição indisponível"); **1 marcador** (OS-0421). **Lagoa Grande** (com a fixture da F1): OS-0505 (Trator LG-01 + Carreta de colheita LG), OS-0506 e OS-0507 ("Ativo fixo · ver na Irrigação"); **1 marcador** (OS-0505). Os IDs são iguais a `{o \| etapa = Em execução, fazenda, safra}` do `cenGet()`. Iniciar a OS-0424 a faz entrar; enviar a OS-0421 para conferência a faz sair |
| M2 | 1 clique em cada função | Nas nove funções e na tela cheia: 1 clique liga e o seguinte desliga. `aria-pressed` acompanha. Função, filtros, seleção de talhão e zoom ficam iguais (estado comparado antes e depois, exceto a chave da camada) |
| M3 | 1 toque abre a O.S. | Tocar no marcador ou na linha abre o painel com os campos da decisão 9. "Abrir O.S." leva a `OS.dc.html#OS-0421` com 1 toque |
| M4 | Posição dentro e sem ponto inventado | Toda leitura simulada fica dentro da geometria do talhão da O.S. (`tgDentro`) ou num trecho de deslocamento declarado (G3, G6). OS-0420 e as O.S. sem fonte não têm marcador; nenhum marcador cai no centroide nem no "local" do cadastro (mutante: com marcador no centroide, M4 reprova) |
| M5 | Idade na fronteira | Com o relógio de teste: idade de 60 s mostra "Atual"; 61 s mostra "Sem sinal há 1 min", com marcador vazado cinza, imóvel e sem rumo. O texto nunca diz "parada" por causa da idade (L6) |
| M6 | Ordem, duplicata, futura, inválida, salto | `frota_unit.js` reproduz L1–L10 com as mesmas saídas do `mapa_frota_chk.py` |
| M7 | Pausa e impedimento | Turno pausado no app: a O.S. continua na lista e no mapa como "Parada · pausa desde hh:mm" (P5). Impedida: "Parada · impedida: …". Nenhuma das duas some |
| M8 | Conflito | Com a OS-0421 em execução, iniciar a OS-0424: o PJ-3030 fica nas duas. Aparecem duas linhas com "Conflito · também na OS-…" e acesso às duas; nenhuma é escolhida. As mesmas O.S. num agrupador não mostram conflito (K1–K3) |
| M9 | Fim ou cancelamento com o painel aberto | Com o painel da OS-0421 aberto, enviá-la para conferência noutra aba: o marcador sai; o painel diz "OS-0421 saiu de Em execução (agora Em conferência)" e oferece Abrir O.S.; o foco fica no painel; nenhum outro painel abre sozinho |
| M10 | Teclado e lista | Tab percorre os marcadores em ordem estável (por O.S.). Enter ou Espaço abre. Esc fecha e devolve o foco ao marcador ou à linha de origem. Lista com as colunas da decisão 10; durante 5 min de leituras, a ordem e o foco não mudam |
| M11 | 20 sobrepostos | Fixture de teste com 20 conjuntos na mesma posição: um botão "20 máquinas" (44 px) abre a lista com 20 linhas. O selecionado fica fora do grupo, identificável |
| M12 | Ver no mapa, ida e volta | Do detalhe e do ⋯ da OS-0421, com 1 clique: Mapa da Santa Rita, Máquinas ligada, conjunto selecionado, painel aberto. Com o filtro salvo em Lagoa Grande ou noutra safra: faixa "Recorte temporário" e 'mapa-ctx' inalterado. Voltar devolve a OS-0421 com a mesma visão, filtros e foco. "Sair do recorte" restaura o contexto anterior |
| M13 | Sem autorização | Perfil Rui (almoxarife): só a lista, sem posição nem operador ("Posição restrita ao seu perfil"). A varredura do DOM, das dicas e dos `aria-label` não acha coordenada, nome de operador nem "há N s" de posição |
| M14 | Sem efeito no domínio | 30 min de simulação, ligar e desligar 20×, recarregar 5×: o JSON do cenário fica igual byte a byte; área realizada, saldo, estoque, custódia, cargas e fases iguais (mutante: a simulação gravar o realizado reprova M14) |
| M15 | Mesma origem e idade | Para cada conjunto, mapa (`aria-label`), lista e painel mostram a mesma fonte, hora e idade, com o mesmo arredondamento |
| M16 | 390 px, 1440 px e 44 px | Com 390 px: alternador, Lista, marcadores e grupo com alvo ≥ 44 × 44 px; painel em folha inferior; sem rolagem lateral. Em 1440 e 390 px, nenhum erro de JS |
| M17 | Movimento reduzido | Com `prefers-reduced-motion`, a duração de transição calculada dos marcadores é 0 s. Na F1 não há animação; na F2, ver N4 |
| M18 | Nunca só cor | Cada marcador tem ícone da operação, rótulo curto e selo com forma e palavra. A legenda lista os ícones presentes e os estados. A captura em escala de cinza mantém a leitura (inspeção) |
| M19 | Simulação rotulada | Com Máquinas ligada, o selo "Posições simuladas · demonstração" fica na legenda. Lista e painel dizem "Fonte: simulação". Nenhum texto diz "telemetria" para posição simulada |
| M20 | Função ativa intacta | Com Máquinas ligada, cores (`fl_*`), rótulos e números da faixa da função ativa ficam iguais (snapshot antes e depois) nas nove funções |
| M21 | EX-42 | Quando houver a barra de tempo, com data diferente de hoje: "Máquinas: só no tempo atual", sem marcadores. Antes do EX-42, não se aplica |
| M22 | Contraprova | Na versão de antes da F1 (`ANTES`, árvore limpa) não há alternador: M1–M3 e M12 reprovam |

**F2 · Movimento suave e rastro.**

| ID | Caso | Oráculo |
|---|---|---|
| N1 | Interpolação | As posições amostradas por quadro ficam no segmento entre leituras consecutivas. Sem extrapolação: sem leitura nova, o marcador para na última |
| N2 | Rastro | Só do turno corrente, últimos 30 min, linha de 2 px sem largura, marcado "simulação". Quebrado nas lacunas maiores que 60 s; a leitura atrasada preenche com marca, e o marcador não volta |
| N3 | Pausar animação | 1 clique congela as posições, com o rótulo "Posições de hh:mm:ss"; estado e idade da lista seguem a cada 15 s. "Retomar" pula para a posição atual. O cenário não muda |
| N4 | Redução de movimento | Sem interpolação nem transição: a posição muda só a cada leitura. "Pausar" continua disponível |
| N5 | Transição de sinal | Fixture da OS-0505 com lacuna de 3 min a cada 12 min: atual → "Sem sinal há 1 min" → atual de novo. O rastro se completa com as leituras atrasadas, o marcador nunca volta e o estado nunca vira "parada" na lacuna |
| N6 | Foco e posição | Com o foco numa linha e 5 min de atualizações: o foco e a rolagem ficam; não há pan automático; a região `aria-live` só anuncia a mudança de estado da selecionada |
| N7 | Desempenho | Fixture de teste com 50 conjuntos, 10 min a 1440 px no Chromium: nenhuma tarefa longa acima de 50 ms vinda da camada (`PerformanceObserver` longtask). Com a página oculta, nenhum `requestAnimationFrame` |
| N8 | Domínio | Repete o M14 com a animação ligada |
| N9 | Gemini | As três contraprovas (localização presumida, transição de sinal, foco e movimento) registradas e tratadas |

**F3a · Conexão de telemetria (CF-03, ambiente de testes simulado no protótipo).**

| ID | Caso | Oráculo |
|---|---|---|
| T1 | Conectar | ≤ 2 toques no Safrion: abrir o fornecedor e Conectar. A tela simulada de consentimento mostra os escopos de somente leitura e o selo "Ambiente de testes simulado"; Permitir conecta |
| T2 | Vínculo automático | Cinco equipamentos sintéticos John Deere: T1 e Trator 04 (série do CD-03) ficam "Vinculado por nº de série"; um de série desconhecida vira "Sem ativo"; um de série igual e modelo diferente e um sem série vão para "Confirmar". Resumo: "5 equipamentos: 2 vinculados · 2 para confirmar · 1 sem ativo" (V1–V8) |
| T3 | Confirmar | 1 toque por item. Duplicata e dúvida nunca se vinculam sozinhas. O mesmo nome com outra série não vincula |
| T4 | Prioridade | Telemetria atual vence o app. Sem telemetria e com app atual, o app assume em ≤ 1 leitura, com a troca marcada no painel e no rastro. Sem nenhuma, "Sem sinal" com a fonte (P1–P7) |
| T5 | Desconectar | 1 toque: a fonte some. As máquinas dela viram "Sem fonte: … desconectada às hh:mm" no mesmo desenho; os vínculos ficam guardados; a trilha da CF-04 registra quem e quando |
| T6 | Nenhuma credencial | Gitleaks e varredura no `_render` e nas fontes: zero token, `client_secret` ou chave. Com interceptação de rede, zero requisições a domínios de fornecedor |
| T7 | Contrato | As cargas simuladas de cada formato (estilo JD, ISO 15143-3, ISOXML TimeLog) se normalizam no contrato da leitura, com `origem: simulada`; os campos ausentes ficam ausentes, sem zero |
| T8 | Texto coerente | O texto da conexão (A5) só promete o que a tela usa |

**F3b · App de campo como fonte e dados além da posição.**

| ID | Caso | Oráculo |
|---|---|---|
| T9 | App desligado por padrão | Sem o gestor ligar em CF-03, nenhuma posição do app vai ao Mapa |
| T10 | Aviso e turno | Ligado: aviso ao Iniciar turno e "Posição em uso" no cabeçalho. Pausar, fechar o turno ou "Parar de compartilhar" (1 toque) param o envio. Fora do turno, zero leitura |
| T11 | Sugestão de apontamento | Ao fechar o turno, a área vem sugerida pela telemetria; sem confirmar, nada se aponta. Com telemetria não homologada, divergência acima da tolerância vira aviso na O.S. Homologada, vale CONC-09/10 |
| T12 | Horas de motor | Aparecem na Manutenção como leitura "telemetria (não homologada)" com hora, sem passar à frente da leitura manual nem duplicar |
| T13 | Combustível | Só informativo: nenhum abastecimento nem movimento de estoque criado |
| T14 | Retenção e perfis | Leitura de posição com mais de 24 h não aparece em consulta nenhuma (software real; no protótipo, rastro só do turno). M13 repetido para a fonte app |

## Cliques e digitação (AGENTS §3.3)

Contagem a partir da tela já aberta (Mapa em qualquer função, ou tela de trabalho da O.S.), no mesmo cenário, na versão `ANTES` e na de depois. Os números "Antes" foram contados lendo o código em c90b062 e serão medidos de novo no E2E. Digitação: 0 em todos.

| ID | Tarefa | Antes (contado no código; medir) | Depois (teto) |
|---|---|---|---|
| K1 | Ver onde estão as máquinas das O.S. em execução | Impossível: não há posição. O mais perto: 2 (Ordens de serviço + Fase "Em execução"), que mostra só os talhões | 1 (Máquinas) |
| K2 | Saber o que uma máquina faz e quanto falta | Impossível como máquina. Pela O.S.: 4 (função, fase, talhão, Abrir O.S.), com o conjunto na tela da O.S. | 2 (Máquinas, máquina) |
| K3 | Abrir a O.S. da máquina | 4 (caminho do K2) | 3 |
| K4 | Da O.S. em execução, ver a máquina no mapa | Impossível. Achar o talhão: 3 (menu Mapa, Ordens de serviço, talhão) | 1 (Ver no mapa) |
| K5 | Voltar à O.S. no mesmo estado | — | 1 |
| K6 | Pelo teclado, abrir a máquina | — | 3 (Máquinas, Lista, linha) |
| K7 | Pausar e retomar o movimento | — | 1 + 1 |
| K8 | Conectar um fornecedor | Impossível (só demonstração) | ≤ 2 no Safrion; telas do fornecedor contadas à parte; +1 por máquina a confirmar |
| K9 | Desconectar | — | 1 (no detalhe já aberto) |
| K10 | Operador compartilhar a posição | — | 0 a mais (o aviso vem no Iniciar turno); parar = 1 |

## Contraprova

- **F1:** o `_render` de antes da F1 (árvore limpa) reprova M1–M3 e M12.
- **Mutantes, cada um reprovando o seu aceite:**
  - marcador no centroide sem leitura (M4);
  - idade sem limite (M5);
  - ordenação pela chegada (M6, L3);
  - simulação gravando o realizado (M14);
  - lista ordenada por distância (M10);
  - um marcador por componente (M8).
- **F2:** o `_render` da F1 reprova N1–N3 e N5.
- **F3a:** CF-03 sem Conectar reprova T1. Mutante de vínculo por nome reprova T3 e V5.

## Testes (proporcionais ao risco: posição e permissão sem efeito em dinheiro ou estoque)

- **Unidade:**
  - `frota_unit.js` (node), com os mesmos casos L, P, V e K do `mapa_frota_chk.py`;
  - derivação dos conjuntos sobre o `CEN0` (C1–C5);
  - família do ícone por operação, agrupamento e texto da idade.
- **Navegador:** `mapa_frota_test.py` (Playwright).
  - Larguras: 1440 e 390 px.
  - Perfis: Ana, Caio, Otávio e Rui.
  - Relógio controlado.
  - Fluxos: Ver no mapa ida e volta, conflito, pausa, saída de Em execução e 20 sobrepostos.
- **Regressão proporcional:**
  - `mapa9_test`, `mapa_filtros_test`, `mapa_faixa_test`, `mapa_cancel_test`, `map_trilha_icones_test`, `talmapa_test`, `colheita_mapa_test`;
  - `componentes_test`, `ds_1610_test`, `regras_toque_test`, `acao_unica_test`;
  - `alocacao_unit_test`, `os_recurso_test`, `os_cenario_test`;
  - os testes de Cadastros e Manutenção que contam ativos (a F1 acrescenta dois).
- **F3a e F3b:** `frota_tel_unit.js`, `cf03_tel_test.py` e `app_turno_posicao_test.py`; Gitleaks.
- **Estado:** nenhum teste de produto foi executado; é especificação.

## Fatias (uma por vez, AGENTS §3.1 e §3.6)

| Fatia | Conteúdo | Arquivos prováveis | Aceite | Cliques |
|---|---|---|---|---|
| **F1 · Ver as máquinas** | Contrato e regras puras; fixture simulada com leituras discretas a cada 10 s; alternador e Lista; marcadores nos dois desenhos; painel e lista; conflito; permissão; agrupamento; "Ver no mapa" com recorte temporário; conjunto sintético da Lagoa Grande na fonte única (Trator LG-01 + Carreta de colheita LG, alocados à OS-0505 de 21 a 26/09, 06:00–15:00, enquanto ela está Em execução) | `frota.js` (novo: conjuntos, leitura, fonte, conflito, ícone, grupo, textos); `dados_frota.py` (novo: percursos relativos, velocidades, intervalo e limite, marca); `areas/inicio.py` (`_mapcard` nas duas variantes, `_mapsvg`, `lgEnsure`/`lgSync`, legenda, painel e lista, `#frota=`, recorte, 'mapa-ctx'); `alocacao.py` (recursos e blocos da OS-0505); `dados_cad.py` (a16 Trator LG-01, a17 Carreta de colheita LG); `dados_manutencao.py` (contadores, se a Manutenção exigir); `areas/processo_os.py` (Ver no mapa no detalhe e no ⋯); `engine.py` (ícones novos, pela skill `padrao-safrion`, DEC-1610-12); testes `frota_unit.js` e `mapa_frota_test.py` | M1–M22 | K1–K6 |
| **F2 · Movimento e rastro** | Interpolação fora do `setState`; rastro do turno; Pausar animação; lacuna de sinal na fixture; desempenho | `frota.js`; `dados_frota.py`; `areas/inicio.py` (laço de quadro, camada de linha no SVG e no MapLibre, botão); testes | N1–N9 | K7 |
| **F3a · Conexão de telemetria** | CF-03 por fornecedor; Conectar e Desconectar em ambiente de testes simulado; vínculo por série; prioridade; normalizadores de formato; texto da conexão corrigido | `dados_config.py` (CONEXOES); `configuracoes.js` (conectar, desconectar, vincular, trilha); `areas/configuracoes.py` (linhas, detalhe, confirmar vínculo); `dados_cad.py` + `areas/cad_ativos_pessoas.py` (fabricante e série no CD-03); `dados_frota.py` (catálogo do ambiente de testes); `frota.js` (normalizadores e prioridade); testes | T1–T8 | K8–K9 |
| **F3b · App como fonte e dados além da posição** | App como fonte com aviso e "Posição em uso"; sugestão de área no apontamento; horas de motor na Manutenção; combustível informativo | `areas/mobile.py`; `cenario.js` (estado de compartilhamento do app, sem mudar os comandos de turno); `areas/configuracoes.py`; `areas/processo_os.py`; manutenção; testes | T9–T14 | K10 |
| fora do protótipo | Integração real com fornecedor (conta, OAuth, contrato, homologação em HML) | software real (`packages/integrations`) | — | — |

## Relação com as frentes vizinhas

- **EX-42 (tempo no Mapa):**
  - Máquinas é só o agora (decisão 17).
  - "Reproduzir o trajeto do dia" reaproveitará o controle de tempo único: Hoje, arraste e Reproduzir/pausa.
  - A semântica de "pausar" é a mesma: nunca mexe numa operação de negócio.
  - Nada aqui cria outro controle de tempo.
- **OS-LOTE (agrupador):**
  - Um conjunto que executa O.S. do mesmo agrupador é um marcador só, sem conflito.
  - A contagem de O.S. não soma o grupo como ordem (decisão 6; K2).
- **SAF-MAPA:** se a peça comum de desenho de talhões for extraída antes, a camada de máquinas entra nela. Se não, entra em `inicio.py` com a mesma interface, para mudar de lugar depois.
- **MAPA-MIP-PROD (parte 2) e PRD 36.7:**
  - O leitor de ISOXML/ADAPT é peça única com a importação do mapa de colheita e o retorno da aplicação.
  - A F3a só normaliza a posição e o estado.
- **EX-38:** o preparo previsto é lido de `cenPreparoOrdem` e mostrado como projeção, sem copiar a conta.
- **PA-OPER:** a família do ícone sai da operação do catálogo, que a PA-OPER organiza; sem tabela paralela.
- **Autoria de `inicio.py`:** EX-42, MAPA-MIP-PROD, SOLO-FOLHA-NIVEIS e SAF-MAPA também mexem nele. A F1 só começa com a autoria combinada (§3.4, uma solução por problema) e vaga no teto de três frentes (§3.6).

## Riscos

| # | Risco | Mitigação |
|---|---|---|
| R1 | O motor do protótipo redesenha tudo a cada `setState`; animar por ele custaria caro | Marcadores movidos direto no DOM (como `LGI.markers`). `setState` só em mudança discreta (estado, idade a cada 15 s); N7 |
| R2 | Várias frentes no mesmo `inicio.py` | Autoria única e sequência combinadas antes do código; contraprova da composição (§3.6) |
| R3 | Dois ativos novos e a alocação da Lagoa Grande mudam contagens em Cadastros, Manutenção e Carga do PCP | Atualizar os testes protegidos com a nova contagem, sem afrouxar; regressão listada |
| R4 | A 8 km/h, o marcador anda cerca de 0,33 unidade/s no desenho e pode parecer parado (G4b) | Seta de rumo, velocidade, "há N s" e rastro; sem acelerar o tempo |
| R5 | A API de alguns fornecedores não é "ao vivo" (consulta horária em parte das APIs ISO 15143-3, segundo terceiros; 5 s na tela do Operations Center, segundo revenda) | Idade honesta; limite por fornecedor no contrato; pergunta 1 ao proprietário |
| R6 | A posição pelo celular é dado pessoal do empregado; a base legal e o aviso dependem do cliente | Desligada por padrão; aviso e indicador; nunca fora do turno; jurídico do cliente antes do piloto |
| R7 | Duas datas de "hoje" na demonstração (A12) | A camada usa `CEN_DIA_OP`; achado registrado para a frente dos dados |
| R8 | Confundir a simulação com o real | Selo persistente e "Simulação" em todo texto (M19) |
| R9 | Relógio do aparelho errado no real | Ordem pelo instante estimado, com incerteza (CONC-20/21) |
| R10 | O CD-03 não tem nº de série hoje | A F3a cria o campo; sem ele, tudo vai para "Confirmar vínculo" (V7), nunca por nome |

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Reproduzir o trajeto do dia ou histórico | EX-42 F1a/F1c entregue e retenção da posição publicada |
| Mapa de cobertura ou aplicação executada (as-applied) | Retorno da aplicação (36.7) implementado e homologado por equipamento |
| Integração real com fornecedor (conta, OAuth, contrato, HML) | Autorização do proprietário (custo e contrato; pergunta 1) e ambiente de testes do fornecedor liberado |
| Comando remoto ou envio de rota à máquina | Nunca neste escopo (PRD 1.2); só por decisão do proprietário e conector homologado |
| Geocerca, alerta de saída da área, "toque de recolher" | Pedido do proprietário, com avaliação de privacidade |
| Marcador de ativo fixo e posição do braço do pivô | Telemetria do pivô com ângulo e ativo no CD-03 |
| Pessoas a pé (equipe sem máquina) no mapa | Nunca por padrão (NFR-17); só por decisão expressa |
| Previsão de término por IA | IA religada pelo proprietário (DEC-1610-11) |
| Abastecimento a partir do combustível da telemetria | PEND-08 decidida |
| Logística entre talhões e caminhões | Módulo Logística |

## Perguntas ao proprietário

Só as que dependem dele: custo, contrato e realidade da fazenda. As demais estão decididas acima ou no PRD.

1. **Telemetria real.**
   - Quais marcas de trator, colhedora e pulverizador as fazendas do piloto usam? Elas já têm modem ou plano de conectividade?
   - O senhor autoriza buscar condições e termos com os fornecedores dessas marcas: plano, acesso à API, uso dos dados e tempo de atualização?
   - **O que se ganha:** posição e horas de motor sem digitação; sugestão de área no apontamento; máquina parada vista sem ligar para o campo.
   - **O que custa:** depende do fornecedor e do plano. Não há estimativa: nenhum preço foi inventado.
   - **Até a resposta:** só o ambiente de testes simulado.
2. **Celular do operador como fonte** para máquina sem telemetria: oferecer no piloto?
   - Vale só no turno, com aviso, e o operador pode parar.
   - **Até a resposta:** fica desligado (NFR-17).

## Conferência executada

- **Script:** `docs/integracao/V71/mapa-frota/mapa_frota_chk.py` (378 linhas, SHA-256 `9b3ec23af4329884f61a6239a9b5140334c34b58d1d5fbc7fbea6072b0f778d6`). O caminho do gerador é relativo ao próprio script.
- **Comando:** `python3 -B docs/integracao/V71/mapa-frota/mapa_frota_chk.py`.
- **Execução em 16/10/2026:** saída 0 e **54 OK · 0 falhas**. A saída está em `mapa_frota_chk.out` (SHA-256 `de4b7ec921316d130b794f4be810fd54313b03ed8bea7698efa1660b97c91324`).
- **O que confere contra as fontes do protótipo:**
  - **R** (8): rendimento de referência pela DEC-2609-03 e larguras do CD-03;
  - **C** (7): O.S. Em execução, conjuntos pela alocação, conflito latente de 24/09 e ausência de alocação na Lagoa Grande;
  - **E** (3): projeção do EX-38 e tempo restante no rendimento de referência;
  - **G** (7): percurso sintético dentro de T2 e do Pivô 19 e sua plausibilidade.
- **Oráculos executáveis das regras desta especificação:**
  - **L** (11): contrato de leitura;
  - **P** (7): prioridade de fontes;
  - **V** (8): vínculo por série;
  - **K** (3): conflito.
  - Eles conferem a regra escrita, não o produto. O `frota_unit.js` vai reproduzi-los contra o código.
- **Limites:**
  - nenhum navegador, banco ou fornecedor foi exercitado;
  - a geometria da Lagoa Grande é a sintética (`dados_lagoa_fonte.REAL = False`; "Demonstração sintética");
  - G4 é plausibilidade do percurso declarado, não medida de área;
  - as referências do setor marcadas "índice" não tiveram o corpo da página lido.
