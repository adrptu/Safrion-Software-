# PCM simplificado · v2: uma entrada, uma tela, um detalhe por coisa

**Pedido do proprietário (Adrianus, 05/10/2026), literal:** "PCM /manutenção também tem telas e menus demais. simplifique, integre em algo mais prático e intuitivo, sem perde funcionalidade importante. Elimina qualquer coisa ambigua, repetitiva, e faça o melhor num só." É pedido, não aprovação deste desenho.

- **Rótulo:** especificado. Nada foi editado no protótipo, nenhum teste rodou, nenhum navegador foi aberto. Executado: `git log`, `git diff --stat cd01b46 9c617c4` e leitura do código e das especificações citadas.
- **v2 (05/10/2026):** aplica a revisão adversarial da v1. São 48 achados: 30 aceitos, 18 ajustados e 0 recusados (Anexo; decisões novas em DECISOES §6).
- **Papéis:** autor Claude · revisor Codex. No protótipo a revisão não bloqueia (AGENTS §3.5).
- **Origem:** três desenhos (por ordem, por ativo, por papel) e dois juízes, que empataram entre "ordem" e "ativo" (77 × 77). A v1 é a síntese, com os enxertos aceitos (DECISOES §1 e §4).
- **Substitui** só tela e menu da PCMS v2 (§5 e partes do §11). As regras de domínio continuam na PCMS e no PRD (§6).
- **Abreviações:**
  - `gen37/` = `/home/user/sp-proto/tools/prototipo/v37/gen37/`;
  - M = `gen37/areas/maquinas.py` · DM = `gen37/dados_manutencao.py` · UI = `gen37/ui37.py` · MB = `gen37/areas/mobile.py` · AL = `gen37/alocacao.py` · DC = `gen37/dados_cad.py`;
  - PRD l.N = linha de `/home/user/Safrion-Software-/docs/PRD.md` (v3.9);
  - PCMS = `docs/pcm-suprimentos/ESPECIFICACAO.md` v2 · SUP = `docs/suprimentos-simplificado/ESPECIFICACAO.md` · AUD = `docs/controle-01/AUDITORIA-PLANEJAMENTO-CONTROLE-EXECUCAO.md`;
  - F01–F111 = funções do inventário (§4) · D-nn = DECISOES.md.
- **Pessoas (sintéticas):**
  - Otávio, responsável de manutenção (PCM);
  - Zé, mecânico (NR-12);
  - João, irrigante com NR-10, o único habilitado para as OMs de especialidade Eletricista (DC:83);
  - Ana, gestora e gerência;
  - Rui, almoxarife;
  - Marcos, operador.

## 0. Como executar

### 0.1 Mapa do existente

**Base das linhas (R24):** `cd01b46`.
- M, DM, UI, `build.py`, AL, DC, `areas/campo.py` e `areas/cad_ativos_pessoas.py` são idênticos em `9c617c4` (diff vazio).
- MB, `areas/processo_os.py`, `areas/inicio.py` e `cenario.js` mudaram com o CTL-2. As linhas desses quatro arquivos estão em `9c617c4`.
- Cada passo reancora as linhas no hash em que começa.

| O quê | Onde | Decisão | Passo (§7.2) |
|---|---|---|---|
| Vencimento, geração sem duplicar, "cumpre também"; janela gerada (DM:363) | DM:309-373 | **fica** (a janela padrão ao gerar não muda: a PCMS C2 depende dela) | — |
| Cinco fases | DM:268 (`MAN_FASES`) | **fica** | — |
| Checklist com motivo, leitura obrigatória e plausível, ciclo fechado, Pendência por "Não feito" | DM:404-444 | **fica**: a conclusão mantém a trava da leitura menor (DM:420) e o aviso de leitura implausível (M:497-499); a tarefa ganha tipo | S2 |
| Leitura a confirmar: Confirmar, Confirmar troca, Descartar | DM:454-477 | **fica** a regra; a decisão vai ao painel da leitura; o histórico vai para `c.leituras` | S2 |
| Mover a janela | M:327-330, 363-366 (`ma_mover`, só para a OM-0234) | **muda**: um comando "Mover janela" para toda OM, com o conflito calculado (§3.3) | S1 |
| Conflito com a produção | DM:203 (fixo, só na OM-0234) | **muda**: calculado sobre AL (a mesma fonte de O.S. › Recursos) | S1 |
| Alocação da OS-0420 | AL:25-26 (T02, PL e CAR até 27/09) | **muda**: ganha 28/09, como já dizem M:343 ("substituto até 28/09") e DM:203 | S1 |
| Rascunho, versão, publicar, travas do serviço e do vínculo | M:731-990 (`PM_JS`) | **fica** a regra; muda a moldura | S1 |
| Componentes: painel (Tab, Esc); grupo de 1 item = link direto; seletor de visão; Lista e Kanban de 5 colunas; chip Canceladas | M:66-74, 1009-1024; UI:60, 453; `processo_os.py:21, 1189` | **fica** (reaproveitar) | S1; 1b |
| Menu Manutenção com 6 itens | UI:39-40 | **muda**: 1 item "Manutenção" → `MA.dc.html`; o comentário UI:31-34 ganha "05/10" | S1 |
| Card do Índice | `areas/indice.py:42-48` (lê `MENU2`) | **muda** sozinho para 1 link | S1 |
| Telas PM, MA-01..05 | M:120-726, 1041-1172; `build()` M:1175-1176 | **muda**: uma tela `MA` (§3); os arquivos antigos viram redirecionamento (§3.1) | S1 |
| Canvas | `build.py:28-32` (`_wh` exige `$preview`), 42, 62-76 | **muda**: lista de páginas de redirecionamento fora do canvas, como já faz l.23-24 | S1 |
| MA-04det no S1 | M:562 (`PARENT37`), 602, 656 (faixa) | **muda**: sai a faixa; "Voltar às ordens" e `PARENT37` → `MA.dc.html#vis=ordens` | S1 |
| Painel da OM e próximo passo | M:375-542 | **muda**: painel único (§3.3) | S1 (moldura), S2 (OM-0233), 1b (passos) |
| 6 casos do MA-02 só na tela | M:219-241 | **muda**: vão ao estado (`c.achados`, que substitui `c.ach`), com os mesmos IDs, origem e componente | S1 |
| Estado da manutenção | DM:255 (`v=2`), 272 (`manGet` repõe o seed se `v` mudar) | **muda**: `v=3` no S1, `v=4` no S2 (estado salvo de versão antiga volta ao seed, sem erro) | S1; S2 |
| Seed da OM | DM:177-203 | **muda**: executante (OM-0233 e OM-0230 → Zé; OM-0228 → João; OM-0221 → concessionária); histórico encerrado sintético a partir de `VINCULOS.ult` (OM-0102 … OM-0231), com custo pela função única | S1 |
| Responsável técnico do ativo | M:126 (`RESP`, só na tela) | **muda**: vai para os dados de manutenção do ativo (DM `EXTRA`) | S1 |
| Lançamentos fixos AB-1037..1042 | M:661-669 | **muda**: vão ao estado (`c.abast`) | S2 |
| OM-0233 com `det` e tarefa "Teste de pressão em carga" | DM:192-198; M:576-583, 613 | **muda**: sai `det`; a tarefa vira tipo Teste com a 1ª tentativa Reprovada (23/09 09:00); peças retiradas semeadas (bomba recuperável "A definir"; mangueiras para sucata) | S2 |
| OM-0228 | DM:182-184 | **muda**: "Medir pressão de recalque" vira Medição; as outras duas viram Verificação | S2 |
| Tarefa como texto | DM:84-86 (`_s`), 160-161 (`_chk`) | **muda**: `{t, tipo}`, padrão "Serviço" | S2 |
| Condição do ativo só no seed | DM:28-44 | **muda**: gravada por comando, com histórico e com a OM que a trata | S2 |
| Pessoas e habilidades | DC:77-88; `areas/cad_ativos_pessoas.py:28, 38` | **muda**: Otávio entra no S1 (a PCMS punha no 1b), porque o Ver como precisa dele; Zé ganha a habilidade "Testar reparo" no S2 | S1; S2 |
| Links de fora para MA-0x, MA-04det e PM | `areas/inicio.py:122, 1391`; `areas/campo.py:59, 362, 491-492, 521`; `areas/cad_ativos_pessoas.py:217`; `areas/gestao.py:151, 278-279, 348, 468, 481-483, 545`; `areas/planejamento.py:114, 400`; `areas/agronomia.py:356` | **muda**: endereço do item (`MA.dc.html#om=`, `#ativo=`, `#vis=`) | S1 |
| Detalhes no canvas | `build.py:42` | **muda**: sem MA-04det | S2 |
| CD-03: horímetro editável, condição fixa | `areas/cad_ativos_pessoas.py:107-110`; DC:60 | **muda**: só leitura, lida do cenário, link `MA#ativo=` | S3 |
| O.S.: ativo bloqueado fixo | `processo_os.py:89, 100, 149-154`, Recursos 1113-1140; AL | **muda**: lê a condição única; dono com link `MA#om=` | S3 |
| App: atalhos do MB-01; MB-09 e MB-09det fixos; operador fixo; MB-04 grava na O.S. | MB:12, 331-337, 610-620, 863-905 | **muda**: §3.7 | S4 |
| Faixa "Telas da manutenção" | M:32-36 | **sai** | S1 |
| Indicador de 3 etapas do PM | M:730, 967-970, 1172 | **sai** | S1 |
| "Marcar pendentes como feitas" | M:460-461, 512 | **sai** (PRD 54.2 l.8371) | S1 |
| KPIs e selos fixos; Pareto; utilização; Agenda; Elegível; contingência | M:122-170, 213, 252-266, 305, 551, 558, 695-696, 726 | **saem** | S1 |
| "Restaurar demonstração" ×3 | M:319, 554, 1068 | **muda**: 1× no menu ⋯ | S1 |
| MA-04det | M:561-656 | **sai**; redireciona a `MA#om=OM-0233` | S2 |
| "Propor substituição" (`c.prop`) e "Liberar mesmo assim" | M:322, 367-368, 494-496; DM:386-392 | **saem** (PCMS-M09b) | 1b |
| "Solicitar compra", "Resolver sobras"; "Registrar recebimento" | DM:394-401, 445-447 | **saem** (PCMS §0.1) | 1b; 1c |

### 0.2 Portões
1. O Codex registra como **pedidos** os de 01/10, 02/10 e 05/10 sobre a Manutenção, em `docs/DECISIONS.md` ou numa rodada (AGENTS §2). Hoje eles existem só em comentário de código (UI:31-34; M:2-11). O S1 muda o menu de 02/10 e não entra sem esse registro.
2. Uma frente ativa por vez (AGENTS §3.1). A ordem entre frentes (CTL-3 em andamento, SUP, BEN) é do Codex. Esta spec fixa só a ordem interna da Manutenção (§7.2).
3. Base de cada passo: a ponta de `claude/prototipo-v44` (hoje `9c617c4`). O "antes" dos cliques é medido nessa ponta, antes do S1.
4. Uma autoria por arquivo ao mesmo tempo: M, DM, UI, AL, `build.py`, `areas/indice.py`, MB, `areas/cad_ativos_pessoas.py`, `areas/processo_os.py`.
5. Proibido abrir, copiar ou renderizar `prototipo/v43` e os commits `c9d61266` e `d22da69`.

### 0.3 Testes por passo (regime leve)
```sh
cd /home/user/sp-proto/tools/prototipo/v37/gen37
python3 dados_manutencao.py && python3 build.py && python3 montar_render.py && python3 varredura.py
python3 ma_regras_test.py unit     # novo: regras em node, padrão carencia_test.py:9-32
python3 ma_unica_test.py           # novo: menu, rotas antigas, 5 fases, uma primária, nenhum comando em linha, 390 px, F5, Ver como
python3 ma_atrito_test.py          # novo: cliques, teclas e trocas de tela das tarefas (a)-(e); antes no hash base, depois no candidato
python3 ma_planos_test.py && python3 ma_correcoes_om_test.py && python3 ma_correcoes_pm_test.py && python3 matest.py
python3 links_ocultos_test.py && python3 acao_unica_test.py && python3 map_decisoes_test.py && python3 etapas_celular_test.py
python3 os_cenario_test.py && python3 tabelas_os_test.py   # S1 (AL ganha 28/09) e S3
python3 cada_cd03_test.py && python3 cada_fix03_test.py && python3 os_v39_bloq_test.py   # S3
```
- **Por passo:** regras em node, build, varredura e testes do módulo (AGENTS §3.5). A bateria completa (PCMS §0.3) roda nos marcos: fim do S2 e fim do 1c.
- **A adaptar** (troca o observável; a regra fica):
  - `matest.py`: a faixa e MA-01..05 viram visões; "Mover OM-0234 para 29/09" continua.
  - `ma_planos_test.py:54-58`, `ma_correcoes_om_test.py:45-49` e `ma_correcoes_pm_test.py:41`:
    - responder tarefa por tarefa e usar o chip "Previsto (x h)";
    - com conflito, liberar pela secundária "Liberar mesmo assim" (até o 1b) ou mover antes pela primária "Mover janela";
    - `PM.dc.html` vira `MA#plano=`;
    - o contador do MA-01 vira a coluna Leitura; o achado do MA-02 vira o painel do achado.
  - `acao_unica_test.py:169-174`: a faixa do MA-03 sai.
  - `etapas_celular_test.py:104-107, 142, 217-238`: MA-01 sai das faixas.
  - `links_ocultos_test.py:28-29, 42-43`.
  - `map_decisoes_test.py:70-72, 99-101`: `MA-04#OM-0233` → `MA#om=OM-0233`.
  - `componentes_test.py:239-242`: MA-01 → `MA#vis=ativos`.
  - `cada_cd03_test.py:17-25` (S3): "Em manutenção" vira a condição única.
- **Critério:** nenhuma falha nova contra a base. Teste instável ou ignorado não se esconde. Todo defeito corrigido ganha regressão.

## 1. Missão e princípios

**Missão:** o PCM, o mecânico e a gestora entram por uma porta e acham o que é deles, sem perder controle que proteja máquina, estoque ou dinheiro.

**"Num só" aqui é:**
- 1 item de menu;
- 1 tela (`MA`) com 4 visões;
- 1 detalhe por coisa (OM, ativo, plano, achado, vencimento);
- 1 comando por efeito;
- 1 fonte por fato (condição, leitura, estoque, custo, agenda).

**Princípios, em ordem:**
1. **Nada essencial some.** O que sai é duplicado, fixo, só mensagem ou de risco (§4).
2. **Natureza à vista.** Cada visão responde uma pergunta e tem uma natureza: planejamento, execução e apontamento, ou controle (§2).
3. **A linha identifica, o painel resolve** (SUP §2.3). Uma primária por tela, com verbo e objeto.
4. **Um fato, uma fonte, um comando.**
5. **Herdar o contexto.** Não pedir o mesmo dado duas vezes. Último valor nunca para lote, quantidade ou leitura (AGENTS §3.3).
6. **Nenhuma regra de domínio nova.** As mudanças de regra corrigem conflito com o PRD ou com a AGENTS §3.3, ou fecham saída que faltava, e estão nomeadas: D-11, D-12, D-18, D-23, D-31, D-34, D-35, D-38 e D-40.
7. **Cada passo deixa o protótipo funcionando** (§7.2).

## 2. Menu e telas: antes → depois

| | Antes | Depois |
|---|---|---|
| Itens de menu | 6, mais 1 clique para abrir o grupo | 1, link direto; card do Índice com 1 link |
| Páginas no escritório | 7: PM, MA-01..05, MA-04det | 1 (`MA.dc.html`): 4 visões e 2 páginas de detalhe (ativo, plano) |
| Navegações paralelas | faixa de 5 telas, 3 etapas do PM, 3 steppers no MA-04det, links de bloco | seletor de 4 visões; 1 barra de fases, só no painel da OM |
| Modelos de detalhe da OM | 3 (painel, MA-04det, MB-09det) | 1 |
| Painéis, formulários, gavetas | 11 | 9, um por registro |
| Grades | 15 | 5 de trabalho e 5 tabelas curtas nos detalhes (4 no ativo, 1 no plano), todas com ordenação |
| Cartões de indicador | 20, a maioria fixa | 11 (3 + 4 + 4), calculados ou "não calculável" |
| Lugares que mudam a condição | 4, nenhum grava | painel Condição (Bloquear, Restringir, Encerrar restrição) e "Declarar apto" no painel da OM |
| Entradas de leitura | 5, por 3 caminhos | 1 função, em 4 pontos, com histórico |
| App | MB-09 e MB-09det ocultos, sem gravar | os mesmos 2 IDs, ligados ao MB-01, gravando e funcionando sem sinal |

**A tela `MA`** (Menu → Listagem → Detalhe → Sub-detalhe):

| Visão (`#vis=`) | Pergunta | Natureza | Abre nela (Ver como) |
|---|---|---|---|
| **Sem ordem** (`semordem`) | O que precisa virar ordem, e o que faço com cada item? | Planejamento, diário | Otávio, se há vencimento devido sem ordem ou achado Alta sem ação |
| **Ordens** (`ordens`) | Que ordem precisa de mim, e o que falta para ela andar? | Execução e apontamento; Em conferência e Encerradas são controle do fechamento | Zé ("Aguardam você"); Otávio nos demais casos; Ana, quando há decisão dela pendente |
| **Ativos** (`ativos`) | Que máquina pode trabalhar, o que ela pede e quanto custa? | Controle | Ana, sem decisão pendente |
| **Planos** (`planos`) | Que regra gera cada preventiva, e em que versão? | Planejamento, uso raro | ninguém |

- Ativo (`#ativo=`) e plano (`#plano=`) são páginas que substituem a lista. "‹ Ativos" e "‹ Planos" voltam com filtro e posição.
- OM, achado, vencimento, condição, leitura e os painéis do plano são painéis laterais.

## 3. Cada tela

### 3.1 Regras comuns
- **Cabeçalho:**
  - "Manutenção" e Fazenda (topo);
  - **Ver como (simulação)**: Otávio · Zé · Ana;
  - selo só com impedimentos, calculado ("1 ativo bloqueado · 1 conflito");
  - menu ⋯ com "Restaurar demonstração" (1×, diz o que restaura).
- **Ver como:**
  - define a abertura (§2) e é o `por` de todo comando;
  - habilita os comandos pela matriz abaixo; os outros ficam desabilitados com o motivo ("Ação do Otávio", "Ação de João, executante");
  - `localStorage` com try/catch; nunca muda o estado da demonstração;
  - reaproveita o componente da SUP §2.2 ou do CTL-3, o que existir primeiro (D-20).

| Comando | Otávio (PCM) | Zé (mecânico) | Ana (gestora) |
|---|---|---|---|
| Registrar achado · Registrar leitura · Registrar abastecimento | sim | sim | sim |
| Decidir o achado (Vincular · Gerar com o achado · Criar ordem corretiva · Fechar sem serviço) · Gerar ordem(ns) · Mover janela · Liberar serviço · Encerrar ordem · Confirmar ou descartar leitura · Corrigir com estorno · comandos do plano | sim | não | não |
| Bloquear · Restringir · Encerrar restrição · Declarar apto · Manter bloqueado · trocar o responsável técnico (CMD-18/19) | sim | só onde é o responsável técnico do ativo (T1, Trator 02, Pulverizador) | não |
| Incluir tarefa | sim, até Liberadas | sim, Em execução, quando executante | não |
| Iniciar · responder tarefas · Peças retiradas · Concluir | só onde é o executante | só onde é o executante | não |
| Responder tarefa de Teste | não | sim, com a habilidade "Testar reparo" (S2) | não |
| Passos-ponte até o 1b/1c (D-22): "Solicitar compra (simulado · Compras recebe no 1c)", "Registrar recebimento (simulado · papel do Almoxarifado)", "Resolver sobras (simulado · papel do Almoxarifado)", "Liberar mesmo assim" | sim | não | não |
| Pedir decisão da gerência (1b) | sim | não | não |
| Autorizar R$ x · Registrar decisão (1b) | não | não | sim |
| Restaurar demonstração | sim | sim | sim |

- **Seletor de visão:** contador neutro do que espera quem está vendo; vermelho só para impedimento. Sem número de etapa.
- **Grades:**
  - busca, filtro e ordenação nas 5 grades de trabalho;
  - nas tabelas dos detalhes, ordenação por coluna e busca quando passam de 10 linhas;
  - unidade na célula;
  - "Custo R$/h da oficina" (OM) ≠ "Custo R$/h da máquina" (CD-03) (DEC-0510-02);
  - nenhum botão de comando em `[role=row]`; o ID é link para o registro.
- **Cartões:**
  - até 4 por visão (PRD l.8505);
  - cartão de contagem é o filtro: tocar filtra, e nenhum chip repete o número;
  - sem dado: "não calculável"; MTBF sem falha: "não estimável".
- **Painel:**
  - a ≥1024 px abre ao lado; a ≤640 px ocupa a tela;
  - painel aberto sozinho ao entrar é **não modal**: o foco fica na lista, o leitor de tela recebe um anúncio e o Tab não fica preso;
  - o Tab fica preso só a ≤640 px ou quando o usuário abriu o painel (F07);
  - uma primária no rodapé; com painel aberto, só ela é primária;
  - depois do comando: comprovante do mesmo registro e link "Próxima: … ›", que só navega.
- **Comando:**
  - leva chave e versão do registro (`o.rv`, PCMS-G04). `o.ver` continua sendo a versão do plano (D-46);
  - a chave é gerada ao abrir o painel de um registro novo e renovada depois de cada comando gravado, inclusive a cada "Salvar e registrar outro";
  - a mesma chave devolve o recibo, sem gravar de novo;
  - até o 1b: `c.recibos` da manutenção e barreira por estado (D-30). No 1b: `cenMudar(self, fn, cmd)`.
- **390 px:**
  - sem rolagem lateral da página;
  - o seletor vira lista ("Sem ordem · 5 ▾");
  - cartões 2 × 2;
  - a grade mostra Identificação e Situação; o resto rola dentro da caixa;
  - painel em tela cheia com a primária sem rolar;
  - pelo menos 5 linhas da grade acima da dobra a 390 × 844.
- **Endereços:**
  - `#vis=` (com `&tipo=` e `&modo=`), `#om=`, `#achado=`, `#venc=`, `#ativo=`, `#plano=`, `#leitura=`, `#novo=plano:<ativo>`;
  - F5 reabre; abrir por endereço não grava.
- **Redirecionamento:** os arquivos antigos (D-24) ficam fora do canvas e do Índice.

| Antigo | Novo | Passo |
|---|---|---|
| `PM.dc.html` · `#PM-xx` · `#novo:aid` | `MA.dc.html#vis=planos` · `#plano=PM-xx` · `#novo=plano:aid` | S1 |
| `MA-01.dc.html` | `#vis=ativos` | S1 |
| `MA-02.dc.html` | `#vis=semordem&tipo=achados` | S1 |
| `MA-03.dc.html` | `#vis=semordem` | S1 |
| `MA-04.dc.html` · `#OM-x` | `#vis=ordens` · `#om=OM-x` | S1 |
| `MA-05.dc.html` | `#vis=ativos&modo=abastecimentos` | S1 |
| `MA-04det.dc.html` | `#om=OM-0233` | S2 |

### 3.2 Sem ordem
- **Cartões-filtro (3).** Uma base de prazo só: o início da janela (vencimento − tolerância), com horizonte de 10 d (DM:20).
  - Vencidas sem ordem · N (base do KPI-PCM-05);
  - Em breve sem ordem · N (janela em até 10 d);
  - Achados críticos sem ação · N (KPI-PCM-11).
- **Grade:** uma linha por vencimento (ativo × serviço) sem OM, ou por achado sem OM.

| Coluna | Exemplo |
|---|---|
| Item | "PM-01 · vencimento" / "SM-0150 · relato" / "INSP-104 · inspeção" |
| Ativo | "Trator 02", com os selos Ativo bloqueado · Leitura de dd/mm · Leitura a confirmar · Marco estimado |
| O que | "Revisão 250 h" / "Hidráulico · Vazamento leve em mangueira" |
| Prazo | "Vencida · 30 h além" / "Em breve · janela abre em 5 d" / "Alta · desde 21/09" / "Voltou da OM-0230" |
| Peças | "Com saldo" / "Falta 1 un · Filtro de óleo MF 4292" / "—" |
| Próximo passo (texto) | "Vincular à OM-0234" / "Gerar com a PM-05" / "Criar ordem corretiva" |

- **Colunas essenciais (proprietário, 10/10; COLUNAS-1):** a versão do plano ("v3"), a periodicidade ("a cada 250 h ou 180 dias") e a leitura do ativo ("2.988 h · 23/09") saíram das células e ficam no painel do vencimento (Versão, Periodicidade, cálculo com a leitura, Leitura atual do ativo) e no painel do achado (Leitura atual do ativo). A busca continua achando a linha por elas. Os selos do ativo ficam na célula (R-13).
- **Filtros:**
  - busca; Tipo (Vencimentos · Achados); Criticidade; Grupo; Plano;
  - Prazo: Vencidas · Até 10 d (padrão) · Até 30 d. É cumulativo pelo início da janela e sempre inclui as vencidas. Os achados não passam por esse filtro.
- **Ordenação:** todas as colunas. Padrão (consequência, depois prazo; PRD 47.3 l.7718):
  1. achado Alta ou com sugestão Bloqueado;
  2. vencimento Vencido;
  3. o resto pelo início da janela; achado pela data.
- **Primária:** **"Gerar N ordens preventivas"**.
  - N = vencimentos do filtro em Vencida ou Em breve sem ordem; "Até 30 d" só mostra, porque Em dia não gera (CAL-06).
  - N = 0: desabilitada com "Nada a gerar neste filtro".
  - Comprovante: "3 ordens em A liberar · Abrir as 3 ›".
  - **Secundária:** "Registrar achado".
- **Painel do vencimento** (`#venc=PM-01|a02|s1`):
  - cálculo: "3.043 h = 2.793 h + 250 h · leitura 2.988 h em 23/09 · ou 01/03/2027 · o horímetro vence primeiro";
  - tolerância, peças planejadas com o livre, "cumpre também", versão;
  - primária **"Gerar ordem preventiva"** (abre o painel da OM nova); Em dia, sem primária (PRD CAL-06; DM:358);
  - link "Abrir PM-01 ›".
- **Painel do achado** (`#achado=SM-0150`):
  - mostra origem, componente, ocorrências (n e datas), sintoma, evidência, leitura, criticidade (editável num toque), condição sugerida e quem registrou;
  - o ativo é só leitura, com o link "Mudar condição ›".
  - **Primária, por precedência:**
    1. Alta ou sugestão Bloqueado → **"Criar ordem corretiva"**. Vincular só se a OM aberta do ativo tem janela até amanhã.
    2. OM do mesmo ativo em A liberar, Liberadas ou Em execução (M:281) → **"Vincular à OM-0234"**. Nunca Em conferência ou Encerradas. Em execução, o executante vê o selo "Tarefa nova".
    3. Vencimento Vencida ou Em breve sem OM no mesmo ativo → **"Gerar ordem preventiva com NC-0912"**. Gera e vincula numa transação.
    4. Senão → **"Criar ordem corretiva"**. Vai para A liberar e herda ativo, componente, sintoma e criticidade. Especialidade pela classe e janela "Próxima sem conflito", corrigíveis. O tempo previsto, exigido para liberar, é informado no painel da OM.
  - Depois da primária, abre o painel da OM.
  - **Secundárias:** todas as outras opções que se aplicam, em lista, e **"Fechar sem serviço"** (motivo obrigatório; PRD 54.4 l.8392).
  - A decisão é a triagem: o selo "Nova" sai.
  - **Volta do achado:** a OM é encerrada ou cancelada sem resposta Conforme à Verificação do achado (inclusive com "Não se aplica"). O achado volta a "Sem ordem", com o selo "Voltou da OM-xxxx".
- **Registrar achado:**
  - **Campos:**
    - ativo (busca; herdado no detalhe do ativo);
    - Origem, um toque: Relato · Inspeção · Alerta;
    - **Componente**, um toque, lista curta: Motor · Hidráulico · Elétrico · Transmissão · Rodado e freios · Órgão de trabalho · Outro;
    - sintoma;
    - criticidade, um toque, sem padrão;
    - condição sugerida: Apto · Restrito · Bloqueado;
    - evidência opcional (selo "Sem evidência");
    - leitura opcional (§3.6).
  - **Responsável técnico** vem do ativo.
  - **Repetição:** mesmo ativo e mesmo componente com achado aberto mostra "Possível repetição de INSP-104 · Somar / Registrar novo", um toque (RF-AST-002 l.2567).
  - **"Registrar e bloquear":** com sugestão Bloqueado, quem tem a competência (matriz §3.1) registra e bloqueia num comando, com o achado como origem.
  - **Prefixo do ID** (D-48): Relato e Alerta → SM; Inspeção → INSP; Não conforme do checklist da OM → NC. Número = maior do prefixo + 1 (como `cenProxId`, PCMS §3.1).

### 3.3 Ordens e o painel da OM
- **Cartões (4):**
  - Ordens críticas abertas (PRD 55.2, Oficina);
  - Backlog em HH (KPI-PCM-08; semanas "não calculável" sem P10);
  - Custódias pendentes (KPI-SUP-06; desde o 1b);
  - Espera por peça (PCMS-I1; desde o 1c).
- **Modos:** Lista | Kanban (componente da O.S.; **5 colunas fixas**; mesmo filtro).
- **Chips:**
  - Todas + 5 fases com contagem, a única contagem de fase;
  - a partir do 1b, o chip **Canceladas** fica fora das 5 fases e fora do Kanban (PCMS-M19, como a O.S. em `processo_os.py:21`).
- **Rotina:**
  - "Aguardam você · N": OMs Liberadas ou Em execução em que você é o executante, ou com selo principal em seu nome;
  - "Esta semana": OMs com janela até domingo e as vencidas. Agrupa por dia, com HH por especialidade e "capacidade da oficina não calculável" sem P10.
- **Colunas** (colunas essenciais, proprietário, 10/10; COLUNAS-1: 8 → 7):
  - Ordem (o ID, link `#om=`);
  - Ativo (coluna própria: "Ordem · ativo" se dividiu, R-01);
  - Serviço ("Revisão 250 h"; o tipo, a criticidade e o plano vão ao painel da OM e ao bloco Ordens do ativo);
  - Janela; Fase;
  - Pendência (selo principal · dono · prazo, "+n");
  - Executante.
  - Saíram para o painel da OM ("Custo e tempos") e para o bloco Ordens do ativo: Tempo ("6,5 h prev. · 4,0 h real") e Custo ("R$ 1.776,00 est." / "R$ 3.800,00"). A busca acha a OM pelo ativo, pelo tipo e pelo plano.
- **Filtros:** busca; **Tipo** (Todos os tipos · Preventiva · Corretiva · Pendência), em chips fora da grade, criado antes de o tipo sair da célula e lido também pelo Kanban; Executante, Pendência e Ativo pelas colunas; Especialidade e Data (janela ou encerramento; Mês atual · 30 d · 12 m).
- **Ordenação:** todas as colunas. Padrão: abertas pela janela e depois pela criticidade; Encerradas no fim, da mais recente.
- **Primária da lista:** nenhuma. A ≥1024 px abre, sem modal, o painel da 1ª OM que espera o papel (abrir não executa).
- **Teclado (COLUNAS-1, 10/10):** Enter na linha abre o painel da OM (cabeçalho com tipo, plano e, fora da preventiva, a criticidade); Esc fecha e devolve o foco à linha, também quando o painel da 1ª OM já estava aberto ao lado.

**Painel da OM** (`#om=`; o único detalhe de OM, na web e no app). Só o bloco da fase atual vem aberto; os outros mostram uma linha de resumo.
1. **Cabeçalho:**
   - "OM-0234 · Trator 02 › · Preventiva · PM-01 v3";
   - barra das 5 fases (única);
   - faixa Veio de → Está aqui → Falta (selo principal com dono e prazo, "+n") → Próxima ação (= primária) (PRD l.280).
2. **Ativo**, só leitura: condição (com "tratada por esta OM" quando for o caso) e leitura com data; "Abrir Trator 02 ›".
3. **Janela e equipe:**
   - **Janela** (dia; ocupa o tempo previsto). O padrão ao gerar é o do DM:363. Muda pelo comando **"Mover janela"**, em A liberar e Liberadas, com atalhos Amanhã · Próxima sem conflito · data:
     - recalcula o conflito;
     - guarda o vencimento original (`o.vencOrig`, KPI-PCM-05);
     - dentro da tolerância (`ma_mover` generalizado), move direto;
     - fora da tolerância ou já vencida: até o 1b, aviso "fica fora da tolerância · venceu/vence em dd/mm" com motivo; no 1b, "Pedir decisão da gerência" (PCMS-M09b);
     - em Liberadas, mover para um dia com conflito segue a regra do Liberar com conflito.
   - **Conflito** (função única, D-38): o recurso do ativo (mapa `aid → recurso` de AL) não tem, no dia da janela, horas livres (jornada de AL:7-8 − horas alocadas em O.S. firme ou condicional) para o tempo previsto.
     - A fonte é AL, embutida no build; é a mesma de O.S. › Recursos (dado da semana, não estado, até o Bloco 2/PCMS-A05).
     - As linhas "manutenção" de AL ficam fora: a OM é a fonte da sua janela.
     - Recalculado ao gerar, ao criar e a cada mudança de janela.
     - Selo: "Conflito · OS-0420 28/09".
   - "Próxima sem conflito" = o 1º dia a partir de amanhã sem conflito, até 7 d. Sem um dia assim, o atalho não aparece.
   - **Executante:** obrigatório para liberar.
     - É sugerido entre as pessoas do CD-04 com a habilitação da especialidade (Mecânico → NR-12; Eletricista → NR-10; Terceiro → texto do prestador).
     - Com uma pessoa só, vem pré-escolhida, à vista e corrigível. Sem nenhuma: "Falta: executante".
     - A Pendência herda o executante da OM de origem.
   - Especialidade e tempo previsto em h.
   - Impacto na produção: só com conflito ou bloqueio, lido da mesma função.
   - Retorno previsto: condicional com falta de peça (PCMS-A06).
4. **Tarefas**, pelo tipo (tabela abaixo; D-11). Motivo obrigatório fora de Feito, Conforme e Aprovado. Nada vem marcado.
   - **"Incluir tarefa"** (tipo e texto): só em Corretiva e Pendência, até Em execução, conforme a matriz. A preventiva segue a versão do plano.
   - **"Teste do reparo · <sintoma>"** (tipo Teste, não excluível) entra sozinho na OM que trata a condição de um ativo Bloqueado que ainda não tem Teste. No Restrito, também vale uma Medição Conforme (CMD-19: "teste válido para o risco", PRD l.2790).
5. **Peças:**
   - colunas Item · Planejado · Situação · Aplicado;
   - Situação numa célula: "Reservado 1 kit · OF26-01" / "Em custódia 16 L · Zé" / "Falta 1 un · SC-041";
   - Aplicado: chip "Usei tudo (16 L)" ou valor digitado (PCMS-M16, desde o 1b); até lá, vazio = planejado;
   - "Ver conciliação" recolhida, com as 7 quantidades da PCMS §5.1 (1b);
   - **Peças retiradas:** destino Recondicionar · Garantia · Sucata, com responsável. Nunca volta ao livre (PCMS-M24; D-13).
6. **Conclusão:**
   - leitura pela função única (§3.6). Na conclusão, leitura menor que a última **recusa** o Concluir: "Falta: decidir a leitura (troca de contador) · Otávio" (DM:420). Leitura implausível dá aviso "Corrigir leitura / Concluir com esta leitura" (DM:426; M:497-499), e o valor confirmado fecha o ciclo;
   - horas de oficina pelo chip "Previsto (5,0 h)" ou digitadas (D-18).
7. **Custo e tempos:**
   - estimado → final pela função única (PCMS-C01; "Custo R$/h da oficina 320");
   - reparo, espera por peça e espera por equipe separados (PCMS-C05; 1c).
8. **Origem:**
   - achados vinculados, com a regra D-31 (abaixo);
   - plano e versão ("segue na v3").

**Tipos de tarefa**

| Tipo | Respostas | Efeito na conclusão |
|---|---|---|
| Serviço | Feito · Não feito · Não se aplica | "Não feito" abre OM de Pendência (como hoje, DM:441-443) |
| Verificação | Conforme · Não conforme · Não se aplica · Não foi possível verificar (PRD l.8371) | Não conforme e Não foi possível verificar abrem ou somam achado do ativo e componente (PRD l.8392) |
| Medição | valor com unidade + Conforme ou Não conforme | igual à Verificação; Conforme vale como teste do Restrito |
| Teste | Aprovado · Reprovado, com evidência; só quem tem a habilitação | lista de tentativas `{r, evid, por, em}`, só por acréscimo. Reprovado mantém a OM Em execução e o ativo bloqueado. Concluir exige a última tentativa Aprovada (PRD l.7738; PCMS-A04) |

**D-31 (achado → tarefa):**
- O achado vinculado, ou que originou a OM, vira uma Verificação "Verificar: <sintoma>".
- Achados do mesmo ativo e componente viram uma Verificação só.
- O achado de origem da OM que trata a condição se resolve pelo teste válido dessa OM (Teste Aprovado ou Medição Conforme), sem Verificação a mais.
- No seed: SM-0147 e INSP-105 se resolvem pelo Teste da OM-0233; SM-0152, pela Medição da OM-0228.

**Primária por fase e situação**

| Fase · situação | Primária | Quem | Passo |
|---|---|---|---|
| A liberar · sem aprovação, 100 % coberta, sem conflito, até R$ 50.000 | **Aprovar e liberar** (grava CMD-42 e CMD-06 separados; PRD l.2968) | Otávio | 1b |
| A liberar · sem aprovação, com falta | **Aprovar ordem** (a SC nasce sozinha, PCMS-M07) | Otávio | 1b |
| A liberar · acima de R$ 50.000 | **Autorizar R$ x** (PCMS-G07) | Ana | 1b |
| A liberar · conflito, com dia livre dentro da tolerância | **Mover janela para 29/09**; secundária "Pedir decisão da gerência" (1b) ou "Liberar mesmo assim" (até o 1b) | Otávio | S1; 1b |
| A liberar · conflito, sem dia livre dentro da tolerância | até o 1b: **Liberar serviço**, com o aviso "Liberar mesmo assim"; no 1b: **Pedir decisão da gerência** | Otávio | S1; 1b |
| A liberar · decisão pedida | **Registrar decisão** (mover, substituto, remanejar a O.S. ou aceitar atraso com déficit; PCMS-M09b) | Ana | 1b |
| A liberar · aprovada, falta peça | nenhuma; selo "Falta peça · SC-041 · Comprador · Ana" → `CMP#sol=` | — | 1b/1c |
| A liberar · falta peça (até o 1b) | **Solicitar compra (simulado · Compras recebe no 1c)** → **Registrar recebimento (simulado · papel do Almoxarifado)** | Otávio | S1 |
| A liberar · coberta (até o 1b: sem aprovação) | **Liberar serviço** (exige executante e tempo; reserva 100 % por lote, PCMS-M09) | Otávio | S1 |
| Liberadas | **Iniciar serviço**; selo "Aguarda entrega · Rui" → `EST#req=` | executante | S1 |
| Em execução | **Concluir serviço**; desabilitada com "Falta: …" (tarefas, teste, leitura, horas, aplicado) | executante | S1 |
| Em conferência · OM trata a condição, teste válido | **Declarar Trator T1 apto** (CMD-19; antes do Encerrar, PCMS-C07); secundária "Manter bloqueado · motivo" | Otávio ou responsável técnico | S2 |
| Em conferência · custódia > 0 ou consumo em conferência | nenhuma; selo "Sobras a receber · Rui" ou "Consumo em conferência" (dono pela SUP DECISOES §2) → `EST#req=`. Até o 1b: **Resolver sobras (simulado · papel do Almoxarifado)**, Otávio | — / Otávio | 1b / S1 |
| Em conferência · pronta | **Encerrar ordem · R$ 2.626,00** (PCMS-M18) | Otávio | S1 |
| Encerradas | nenhuma; comprovante e custo | — | S1 |

- **Encerrar ordem, regra única** (F79 + F92; D-34). Recusa com "Falta: … · dono" quando faltar:
  1. sobras resolvidas (até o 1b, pela ponte; no 1b, custódia zero e nenhuma conferência aberta);
  2. destino e responsável em toda peça retirada (dano evitado: perder peça recuperável);
  3. na OM que trata a condição, "Declarar apto" ou "Manter bloqueado/restrito · motivo" registrado (dano evitado: ativo preso, ou liberado, sem decisão).
  - As horas já são exigidas no Concluir.
  - "Manter" desfaz o vínculo entre a condição e a OM. O detalhe do ativo passa a pedir "Criar ordem corretiva".
- **Secundárias:**
  - "Cancelar sem execução" (só antes de iniciar; PCMS-M19; 1b);
  - navegação: `#plano=`, `CMP#sol=`, `EST#req=`, `OS.dc.html#OS-`.

### 3.4 Ativos e o detalhe do ativo
- **Período** (cabeçalho da visão): Mês atual · 30 d · 12 m; padrão Mês atual.
- **Cartões (4):**
  - **Aptos agora** ("14 de 16"; condição, não disponibilidade; filtra os não aptos);
  - Cumprimento de preventiva no período (KPI-PCM-05; "não calculável" enquanto as encerradas não tiverem `o.vencOrig`);
  - **Custo de manutenção · set/2026** (KPI-PCM-10; "das OMs encerradas no sistema"; o que está "em andamento R$ x est." aparece separado);
  - MTBF · MTTR (KPI-PCM-02; "não estimável").
- **Modos:** Ativos | Abastecimentos (D-15).
- **Colunas (Ativos)** (colunas essenciais, 10/10; COLUNAS-1: 7 → 5):
  - Ativo ("Trator T1 · JD 6M 155"; o local fica no cabeçalho da página do ativo);
  - Condição ("Bloqueado · desde 21/09"; "Restrito · até 30/09");
  - Próxima manutenção (a mais urgente, "+n");
  - Em aberto: primeiro o que pede ação ("Leitura a confirmar", "Leitura de 12/09", "Desvio de consumo +18 %"), depois as ordens e achados ("OM-0233 · Em execução" / "NC-0912 sem ordem", links);
  - Custo no período (total no rodapé).
  - Saíram para a página do ativo: Leitura ("4.312 h · 23/09": cabeçalho, Situação e "Leituras e abastecimentos") e Consumo ("11,8 L/h · tanque cheio", com o desvio: "Custo e desempenho"; PRD CAL-07). A busca acha o ativo pelo local, pela leitura e pelo consumo.
- **Filtros:**
  - busca; Grupo (classes do PRD 47.6);
  - Condição (Apto · Restrito · Bloqueado, com contagem);
  - Pendência (Leitura a confirmar · Sem plano · Achado sem ordem · Desvio de consumo · Vence em 30 d · Restrição vencida).
- **Ordenação:** todas as colunas; padrão Bloqueado primeiro, depois a próxima manutenção. **Primária:** nenhuma.
- **Modo Abastecimentos:**
  - colunas (10/10; COLUNAS-1: 8 → 6): Lançamento · Ativo · Volume ("320 L") · Data · Consumo (L/h ou km/L) · Qualidade (Confirmada · A confirmar · Troca de contador · Descartada · Estornado);
  - operador, evidência, tanque/lote, método e a leitura do abastecimento ficam no painel do lançamento e na busca;
  - filtros: data, ativo, **Tanque/lote** (seletor fora da grade, criado antes de a coluna sair), qualidade;
  - primária **"Registrar abastecimento"** (ativo por busca), com "Salvar e registrar outro" (§3.6).
- **Detalhe do ativo** (`#ativo=a01`): cabeçalho com nome do CD-03, modelo, local, grupo, condição, leitura e selo. Abre aberto o bloco que tem pendência.
  1. **Situação:**
     - condição com motivo, desde, quem, evidência, prazo (Restrito) e a OM que a trata;
     - responsável técnico;
     - link "Mudar condição ›";
     - leitura com origem e qualidade;
     - agenda lida de AL (a mesma de O.S. › Recursos);
     - retorno previsto condicional.
  2. **O que vence:** todos os serviços, inclusive em dia e com ordem. A linha abre o painel do vencimento. "Sem vínculo · Vincular ›" e "Sem plano · Criar plano ›" levam ao plano.
  3. **Achados:** todos, com estado (Sem ordem · Na OM-0234 · Resolvido · Fechado sem serviço). A linha abre o painel do achado.
  4. **Ordens:** todas, com fase e custo (colunas Ordem, Serviço · tipo, Janela, Fase, Custo; o ativo não se repete na célula, é o título da página).
  5. **Leituras e abastecimentos:** de `c.leituras` e `c.abast`. A linha abre o painel da leitura.
  6. **Custo e desempenho:**
     - custo no período por natureza (3.1.05 peças, 3.1.04 lubrificantes, oficina, terceiros);
     - custo por hora operada (KPI-PCM-10) · não calculável;
     - consumo 7 d com método e desvio;
     - disponibilidade 30 d (KPI-PCM-01.DISPONIBILIDADE) · não calculável;
     - MTBF/MTTR; cumprimento de preventiva.
- **Primária do detalhe:** a primeira que se aplica, nesta ordem:
  1. "Confirmar leitura 3.140 h" (há leitura pendente);
  2. "Criar ordem corretiva" (Bloqueado sem OM que trate);
  3. "Registrar abastecimento" (ativo motorizado);
  4. "Registrar leitura" (tem contador);
  5. nenhuma.
- **Secundárias:** "Registrar achado" e "Registrar leitura" (quando não é a primária).
- **Links:** "Abrir no CD-03 ›" e "Ver agenda em O.S. › Recursos ›".

### 3.5 Planos e o detalhe do plano
- **Lista:**
  - colunas (10/10; COLUNAS-1: 6 → 3): Plano · PM-xx · Estado ("Publicado v3 · Rascunho v4 em edição" / "Inativo") · Situação ("2 vencidas · 1 sem ordem", link para Sem ordem filtrada pelo plano; "1 ativo do modelo sem vínculo" quando o plano alcança um ativo que não está vinculado);
  - Aplica-se a, Serviços e o contador de Ativos ficam na página do plano (cabeçalho, Serviços, Ativos vinculados) e na busca;
  - filtros: Grupo, Estado, busca;
  - acima da grade: "4 ativos sem plano · Distribuidor 3 t, Máquina TSI, Esqueletadeira, Gotejo T7 · Criar plano" (calculado por `pmSemPlano`; Aplica-se a herdado);
  - **primária:** **Novo plano**.
- **Detalhe** (`#plano=PM-01`):
  - selo, versão, Aplica-se a;
  - faixa de estado de uma linha: "Rascunho v4 em edição · vencimentos seguem a v3 · Descartar rascunho" / "Rascunho v1 · publique" / "Inativo · Reativar";
  - **Serviços:** a linha expande; o nome abre o painel do serviço;
  - **Ativos vinculados**, só leitura (ativo · marco · próximo vencimento · situação · ordem), sem "Gerar"; a 390 px o conjunto à vista é Ativo, Situação e Próximo vencimento (quando o contrato G2-COL entrar);
  - **Versões**, recolhido.
- **Primária:** **Publicar vN** (desabilitada com o motivo enquanto faltar serviço, gatilho ou tarefa) · **Reativar** (inativo) · nenhuma (publicado sem rascunho).
- **Secundárias:** Incluir serviço · Vincular ativo · Editar plano; ⋯ Inativar.
- **Painéis:**
  - **Serviço:** gatilhos h/km/dias, tolerâncias, base do ciclo, cumpre também, tempo, especialidade, tarefas com tipo, peças com selo do livre; "Excluir serviço" só no rascunho.
  - **Vínculo** (D-41):
    - o marco vem pré-preenchido da última OM encerrada **do mesmo serviço, ou de um que o "cumpre também"**, com a origem à vista ("da OM-0219 · 02/09 · 2.793 h");
    - é corrigível com motivo;
    - corretiva nunca serve de marco;
    - sem essa OM: data e leitura, ou "Sem histórico (marco estimado)".
  - **Novo/Editar plano:** nome, Aplica-se a, Começar de, aviso de cobertura dupla.
  - **Publicar:** diferenças, impacto, "ordens abertas seguem a v3".
  - Travas atuais (M:800-864, 930-956).

### 3.6 Painéis de condição e de leitura
- **Condição** (quem: matriz §3.1). Grava a condição única com histórico `{cond, motivo, por, em, achado, om, ate}`. A primária diz o efeito: "Bloquear Trator T1".
  - **Bloquear** (CMD-18): motivo, evidência, achado de origem; "Tratar na OM-xxxx" quando há OM aberta.
  - **Restringir** (PRD 47.3 l.7720): limites e **prazo**. Vencido o prazo, aparece o selo "Restrição vencida" (aviso).
  - **Encerrar restrição** (Restrito → Apto): motivo e evidência (medição). Só quando não há OM aberta que trate a restrição.
  - **Trocar responsável técnico:** com motivo.
  - Bloqueado → Apto só por "Declarar apto" no painel da OM (D-10).
- **Leitura e abastecimento**, uma função para abastecimento, conclusão, achado e leitura avulsa. Estende `manLeitura` (DM:454-460) e grava o histórico em `c.leituras` `{aid, val, un, data, origem, qual, por}`.
  - **Herdados:**
    - ativo (no detalhe, ou do turno);
    - data e hora, corrigíveis (atalhos Hoje · Ontem · data);
    - operador da alocação do ativo no dia (AL), corrigível; sem alocação, lista curta sem pré-escolha;
    - `por`.
  - **Pedidos:**
    - tanque/lote (lista curta; pré-escolhido só se for o único elegível, à vista e corrigível);
    - volume em L;
    - leitura com unidade (vazia; "Última: 2.988 h em 23/09");
    - evidência opcional.
  - **Leitura com data anterior à última:** é comparada com as leituras vizinhas no histórico. Entra no histórico sem mudar a leitura atual e sem pedir troca de contador. Fora dos vizinhos, fica "a confirmar".
  - **Leitura de hoje:**
    - menor que a anterior: "confirme a troca de contador";
    - acima do possível: confirmar ou descartar;
    - os vencimentos seguem a leitura anterior até a decisão (DM:405-408, 452-477).
  - **Na conclusão vale o §3.3, item 6** (trava da leitura menor; aviso de implausível).
  - **"Salvar e registrar outro":** grava, gera chave nova, limpa ativo, tanque/lote, volume, leitura e evidência, e mantém só a data. O operador é herdado de novo do novo ativo.
  - **Lançamento aberto:** "Confirmar leitura" / "Confirmar troca de contador" (primária), "Descartar" e "Corrigir com estorno" (motivo; lançamento novo; o original fica).

### 3.7 App (390 px)
- **Perfil do app** (S4): Ver como (simulação) Marcos · Zé, em `c.app.usuario`. Hoje o operador é fixo em `c.app.operador` (MB:12).
- **Sem sinal** (`cenSinal`, padrão do app):
  - os comandos do MB-09, MB-09det e MB-04 levam a chave gerada no aparelho e vão para a fila;
  - a fila é enviada uma vez só;
  - na volta, o cenário revalida fase e `o.rv`. Se a OM mudou, o registro vira "Conflito a resolver · Otávio" no painel da OM e nunca é aplicado em silêncio.
- **CTL-2 conferido:** `cenApontar` é o turno da O.S. As horas da OM entram só no Concluir; não há segundo apontamento.

| Tela | O que tem | Passo |
|---|---|---|
| MB-01 Hoje no campo | **Minha fila:** Marcos vê só as O.S.; Zé vê as OMs em que é executante, pela janela e depois pela criticidade, com "Iniciar serviço". Cartão "Máquina" na vaga vazia (MB:336) | S4 |
| MB-09 "Máquina" | ativo herdado do turno, senão lista curta com busca. Condição em texto ("Não opere" quando Bloqueado), leitura com data, OM aberta. Primária "Registrar abastecimento" (com "Salvar e registrar outro"). Secundárias "Registrar leitura" e "Reportar falha" (MB-04 com o ativo herdado) | S4 |
| MB-09det "Ordem de manutenção" | o painel da OM em 390 px, com as mesmas funções; Teste desabilitado com o motivo para quem não tem a habilitação | S4 |
| MB-04 Ocorrência | tipo "Equipamento", e "Segurança" ligada a máquina, pede o ativo (lista curta dos ativos da O.S. ou do turno) e grava um **achado** de origem Relato, ligado à O.S., pela mesma função do MB-09. Os outros tipos seguem como OC da O.S. (MB:610-620) | S4 |

### 3.8 Telas de fora
| Tela | Muda | Passo |
|---|---|---|
| CD-03 | condição, responsável técnico e leitura só leitura, da fonte única, com link `MA#ativo=`; "Custo R$/h da máquina"; a calibração fica no CD-03 (aferição, D-16) | S3 |
| O.S., Mapa, CA-01x, EST | links direto ao registro (`MA#om=`); a O.S. lê a condição única | S1; S3 |
| AL | OS-0420 com T02, PL e CAR condicional também em 28/09 (alinha com M:343 e DM:203) | S1 |
| CMP | recebe a SC de origem Manutenção (PCMS 1c) | 1c |
| Telas ocultas | links para `MA#…` | S1 |

## 4. Rastreio F01–F111

**Tratamento:**
- **Fica**;
- **Funde**: duas ou mais viram uma;
- **Grava**: passa a gravar ou a existir;
- **Módulo**: vai para Estoque ou Compras por regra;
- **Sai**: só acessória, duplicada, fixa ou de risco, com o motivo.

| F | Destino | Tratamento | Passo |
|---|---|---|---|
| F01 | Menu com 1 item; Índice com 1 link | Funde 6 → 1 | S1 |
| F02, F03 | — | Sai: a faixa repete o menu e tem pendências fixas; as 3 etapas do PM não são etapas | S1 |
| F04 | Detalhe do plano: trilha "‹ Planos" e "Publicar vN" | Fica o comando; sai o botão que só navega | S1 |
| F05 | Menu ⋯ do cabeçalho | Funde 3 → 1 | S1 |
| F06, F07 | Endereços e redirecionamentos do §3.1; Tab preso só no painel aberto pelo usuário ou a ≤640 px | Fica | S1 |
| F08, F09, F10 | Visão Planos (grade, filtro Grupo, linha "4 ativos sem plano"); filtro "Sem plano" em Ativos | Fica (cartões viram linhas) | S1 |
| F11–F17, F19, F20, F23, F24 | Detalhe do plano e painéis Serviço, Novo/Editar plano e Publicar | Fica, travas iguais | S1 |
| F18 | Expandir por serviço | Fica; "Expandir tudo" sai (Publicar já mostra o que mudou) | S1 |
| F21 | Detalhe do plano › Ativos vinculados, só leitura | Sai a grade repetida e o "Gerar" | S1 |
| F22 | Painel Vínculo | Fica; marco pré-preenchido da última OM encerrada do mesmo serviço, corrigível (D-41) | S2 |
| F25, F26 | Cartões de Sem ordem; selo de impedimentos; filtro "Conflito" em Ordens | Funde | S1 |
| F27, F28, F29 | Sem ordem (até 30 d) e bloco O que vence do ativo (todos) | Fica, mesmos selos e situações | S1 |
| F30 | Item com OM sai de Sem ordem (a linha some); o ativo mostra "OM-0234 · A liberar" | Fica | S1 |
| F31, F32 | Painel do vencimento; primária de Sem ordem | Fica, uma instância por tela; sai o link "Ver ordens" | S1 |
| F33, F55, F83 | Painel da OM › Janela e equipe › Impacto na produção, pela função de conflito sobre AL | Funde 5 → 1; Grava (calculado, D-38) | S1 |
| F34 | Painel da OM: "Mover janela" para toda OM, com tolerância e conflito | Fica, generalizado | S1 |
| F35 | Painel da OM: "Pedir decisão da gerência"; Ana "Registrar decisão" | Fica com a alçada certa (PCMS-M09b) | 1b |
| F36, F37, F38 | Cartão "Aptos agora"; coluna Condição; filtro Condição; a Leitura na página do ativo e "Leitura a confirmar" em Em aberto (COLUNAS-1, 10/10) | Fica; "Elegíveis" sai com a F40 | S1 |
| F39, F40 | Agenda lida de AL no detalhe do ativo | Sai o dado fixo; elegibilidade é da O.S. | S1 |
| F41 | Colunas Próxima manutenção e Em aberto | Fica | S1 |
| F42, F44 | Uso 30 d derivado dos apontamentos (FORA-DE-ESCOPO) | Sai o dado fixo | S1 |
| F43, F54 | Painel Condição (Bloquear, Restringir com prazo, Encerrar restrição, responsável técnico no ativo) | Funde 4 → 1; Grava | S1 (responsável); S2 |
| F45, F46, F57, F82, F102 | — | Sai: navegação repetida e selos fixos; selo calculado no lugar | S1 |
| F47, F48 | Cartão "Achados críticos"; Sem ordem com Tipo = Achados, por consequência; bloco Achados do ativo | Fica | S1 |
| F49 | "Registrar achado" (Sem ordem e ativo), com componente; app MB-04 | Grava | S1; S4 |
| F50, F51, F52 | Painel do achado: Vincular / Gerar preventiva com o achado / Criar ordem corretiva / Fechar sem serviço | Grava; a F52 passa a existir | S1 |
| F53 | IDs como links `#om=` | Fica | S1 |
| F56 | — (KPI-PCM-07 no GE-06, Bloco 7) | Sai o dado fixo | S1 |
| F58 | — (chips de fase; retorno no painel) | Sai: repete a F59 | S1 |
| F59, F60, F61 | Ordens: chips, Lista e Kanban, colunas Pendência e Executante | Fica | S1 |
| F62 | Primária do painel (F65) | Funde: o comando fica, só no painel | S1 |
| F63 | — | Sai: link de bloco | S1 |
| F64, F65, F84, F85, F93 | Painel da OM: cabeçalho, barra única, faixa de continuidade, primária | Funde | S1 |
| F66 | "Liberar serviço" (exige executante); "Aprovar e liberar" | Fica; "Liberar mesmo assim" sai no 1b | S1; 1b |
| F67 | Selo "Falta peça · SC-041 · Ana" → `CMP#sol=` | Fica | 1b |
| F68, F69, F78 | SC automática; Estoque › Receba e inspecione; Estoque › Atenda requisições | Módulo (PCMS-M07, M12, M17); até lá, ponte rotulada para Otávio | 1b; 1c |
| F70 | Painel da OM; cartão do MB-01 | Fica | S1; S4 |
| F71, F86 | Tarefas por tipo; "Incluir tarefa" em Corretiva e Pendência | Funde: um modelo | S2 |
| F72 | — | Sai: pré-marca como feito (PRD l.8371) | S1 |
| F73, F74, F97 | Função única de leitura; trava da leitura menor e aviso de implausível na conclusão; decisão no painel da leitura | Fica | S1; S2 |
| F75 | Chip "Previsto" ou valor digitado | Fica, sem valor implícito | S1 |
| F76 | Peças: Planejado · Situação · Aplicado; conciliação recolhida | Fica | S1; 1b |
| F77, F90 | "Concluir serviço", uma regra | Funde | S2 |
| F79, F92 | "Encerrar ordem · R$ x", uma regra (§3.3) | Funde | S2 |
| F80, F81 | Painel da OM › Origem; OM de Pendência por "Não feito" | Fica | S1 |
| F87 | — | Sai: só mensagem; cada resposta grava | S2 |
| F88, F89 | Tarefa Teste com tentativas; "Declarar apto" / "Manter bloqueado" em Em conferência | Grava | S2 |
| F91 | Peças retiradas, exigidas no Encerrar | Fica, gravando | S2 |
| F94 | — (dia no modo Abastecimentos; tanque no Estoque, Bloco 6; consumo em Ativos) | Sai o dado fixo | S2 |
| F95, F96 | Modo Abastecimentos; painel da leitura; app MB-09 | Fica, com herança | S2; S4 |
| F98, F99 | — | Sai: conferir é a F97; desvio é filtro e achado de origem Alerta | S2 |
| F100, F101 | "Corrigir com estorno"; coluna Consumo nos Abastecimentos e o consumo do ativo em "Custo e desempenho" (fora da linha de Ativos, COLUNAS-1), de `c.abast` | Grava | S2 |
| F103, F104 | MB-01, MB-09 "Máquina", MB-09det = painel da OM, MB-04 → achado; sem sinal | Grava | S4 |
| F105, F106, F109, F111 | Links → `MA#om=OM-0233` e `MA#…` | Fica, direto | S1 |
| F107, F108 | CD-03 e O.S. leem a condição única; calibração fica no CD-03 | Fonte única | S3 |
| F110 | Compras recebe a SC de manutenção | Lacuna fechada | 1c |

**Saldo:**
- Nenhuma das 73 essenciais sai.
- 3 mudam de módulo por regra: F68, F69, F78.
- 14 passam a gravar ou a existir: F33 (calculado), F43, F49, F50, F52, F54, F88, F89, F91, F100, F101, F103, F104 e a OM-0233 no estado.
- Saem só acessórias: F02, F03, F18 (parte), F21 (grade), F39, F40, F42, F44, F45, F46, F56, F57, F58, F63, F72, F82, F87, F94, F98, F99, F102.
- A F62 (essencial) funde com a F65.
- Conferência: as 111 funções (F01–F111) aparecem uma vez na coluna F (verificado por script na v2).

## 5. Ambiguidades e repetições eliminadas

| # | Antes | Depois |
|---|---|---|
| 1 | Navegação às mesmas telas em 6 lugares | 1 item de menu e 4 visões |
| 2 | Nome no menu ≠ verbo na faixa (5 pares) | um nome por visão: Sem ordem, Ordens, Ativos, Planos |
| 3 | MA-03 com 3 nomes ("Plano de manutenção", "Vencimentos e paradas", "Programe as preventivas") | "Planos" é só a regra versionada; o que vence está em "Sem ordem" |
| 4 | "Gerar ordem" no PM e no MA-03, com a mesma grade | Gerar só em Sem ordem (lote), no painel do vencimento e no painel do achado ("com o achado") |
| 5 | Impacto na produção em 5 telas e 3 textos | uma função de conflito sobre AL; uma seção no painel da OM |
| 6 | Condição muda em 4 lugares e vem de 2 fontes | painel Condição + "Declarar apto"; uma fonte |
| 7 | Horímetro digitado em 5 lugares | uma função de leitura com histórico; CD-03 só lê |
| 8 | 3 modelos de OM, "Concluir" com 3 regras, "Encerrar" com 2 | um painel, uma regra de cada |
| 9 | "Registrar inspeção" 2×, "Bloquear ativo" 2× | "Registrar achado" e "Bloquear" 1× por tela |
| 10 | Fase 3× na lista e 4× no detalhe | contagem só nos chips; barra no painel |
| 11 | Mesma ação na linha e no painel | só no painel |
| 12 | "Restaurar demonstração" 3× | 1× |
| 13 | 8 nomes para a entrada de um problema (SM, INSP, NC, falha, alerta, achado, caso, ocorrência) | **Achado**, com Origem e prefixo por origem; IDs antigos mantidos; "ocorrência" só para a OC da O.S. |
| 14 | Bloqueado com 6 nomes; recomendação com 5 valores | Apto · Restrito · Bloqueado em toda parte; "Impedida" só na O.S. |
| 15 | Contador / Horímetro / Leitura do horímetro / Leitura | coluna "Leitura" com h ou km na célula; campo "Leitura do horímetro · h" |
| 16 | "Ver falta de peça" / "Solicitar compra" / "Falta peça" | um selo "Falta peça · SC-041 · Ana" |
| 17 | "Liberar" com dois sentidos | "Liberar serviço" (CMD-06) e "Declarar apto" (CMD-19) |
| 18 | OM / Ordem de manutenção / O.S. de manutenção | "ordem de manutenção (OM)"; "O.S." só para a agrícola |
| 19 | "Encerrar" para achado e para OM | "Fechar sem serviço" (achado) e "Encerrar ordem" (OM); "Encerrar restrição" (condição) |
| 20 | "Gerar" e "Criar" sem regra | "Gerar" = do plano (preventiva); "Criar" = do achado (corretiva) |
| 21 | Custo-hora em 3 bases | "Custo R$/h da oficina" (OM) e "Custo R$/h da máquina" (CD-03); "por hora operada" só como KPI, não calculável |
| 22 | Calibração do CD-03 parecendo preventiva | aferição no CD-03; preventiva no plano |
| 23 | "Colhedora CH-01" × "Axial-Flow 7250" | nome do CD-03 em toda parte |
| 24 | "Criar ordem" levava à lista; "Triar" não gravava | cria a OM; a decisão é a triagem e grava |
| 25 | Links para listas genéricas e duas rotas para a OM-0233 | endereço do item; uma rota `MA#om=OM-0233` |
| 26 | KPIs e selos fixos que parecem vivos; mensagens que parecem gravar | calculados ou removidos; passo simulado diz "(simulado · …)" |
| 27 | MA-05 sem herança; marco e contador pedidos de novo | ativo, data, operador e marco herdados e corrigíveis |
| 28 | Sem papéis | Ver como: Otávio, Zé, Ana; matriz papel × comando; app Marcos · Zé |
| 29 | "A programar" × "A liberar" (parecem fases vizinhas); "Programação" com dois sentidos | visão "Sem ordem"; bloco "Janela e equipe" |
| 30 | Quatro horizontes ("7 d", "10 d", "em breve", "esta semana") | um horizonte pelo início da janela (10 d); "Esta semana" = janela das OMs até domingo |
| 31 | "Disponibilidade 14 de 16" lido como % | "Aptos agora · 14 de 16"; disponibilidade 30 d só como KPI, não calculável |
| 32 | "Próxima livre" sem definição; dois comandos de janela | "Próxima sem conflito" definida; um comando, "Mover janela" |
| 33 | `o.ver` = versão do plano e versão do registro | `o.ver` (plano) e `o.rv` (registro) |

## 6. Regras preservadas (fonte única; nada é reescrito aqui)

| Tema | Fonte | Onde aparece |
|---|---|---|
| 5 fases; fase só por comando; condição em selo; OM única | PRD 47.5 l.7740; RF-AST-004 l.2569; PCMS §2.3; AGENTS §4 | Ordens, painel |
| Aprovar ≠ liberar; Aprovar e liberar; autorização econômica; conflito com produção | PCMS-M05, M09, M09b, G07; PRD l.2968, 47.8 l.7820 | painel (1b) |
| Peça como lote; reserva na liberação; SC automática; recebimento; entrega; consumo; devolução; encerrar; cancelar; balcão | PCMS-M01..M19, M25 | painel, Estoque, Compras (1b/1c) |
| Custo da OM, preço do lote, espera por peça, conciliação | PCMS-C01, C02, C05, C06 | painel, Ativos |
| Condição única; bloquear; declarar apto com teste válido para o risco; teste reprovado; aptidão antes do custo; operação degradada com limites e prazo | PCMS-A01..A06, C07; RN-021 l.223; CMD-18/19 l.2789-2790; RF-AST-005 l.2570; PRD l.7720, l.7738 | painel Condição, painel da OM |
| Leitura com unidade, data, origem e qualidade; aviso, nunca trava (fora da conclusão) | PRD 47.2 l.7714; DM:405-408, 419-420, 452-477 | função única |
| Respostas do checklist; não conforme vira achado; concluir não resolve o achado | PRD 54.2 l.8371; 54.4 l.8392; 54.5 l.8404 | tarefas, achado |
| Gatilho combinado; uma OM por ciclo; versão; referência + intervalo | PRD 47.2 l.7712; RF-AST-003 l.2568; CAL-06; DM:309-373; M:731-990 | Planos, Sem ordem |
| Abastecimento: um movimento; L/h só com método; estorno | RF-AST-006 l.2571; CAL-07 l.4297; ENG-026 | painel da leitura |
| Indicadores: até 4 cartões; "não calculável"; família com ID completo | PRD 55.2 l.8505, 55.3; l.8478; PCMS §7 | cartões |
| Chave e versão por comando; segregação | PCMS-G01, G04; ENG-021/022 | todo comando |
| Dados sintéticos | ENG-017; PCMS-G06 | tudo |

## 7. Relação com a PCMS v2 e ordem única

### 7.1 O que esta spec substitui na PCMS
| PCMS | Passa a ser |
|---|---|
| §5.1 linha "MA-01..05, PM (mantidas)" e princípio 6 "nenhuma tela" | tela `MA` única; continua "nenhuma tela nova" |
| §5.1 MA-04 (passo único, painel de peças de 7 colunas) | painel da OM (§3.3): mesmos passos + "Aprovar e liberar"; as 7 colunas recolhidas em "Ver conciliação" |
| §5.1 MA-03 "Decisão da gerência" ao lado de "Mover" | só no painel da OM |
| §5.1 PM "selo de saldo" | painel do serviço em `#plano=` |
| §6 destinos ("MA-04 →", "MA-03 →", "PM →") | `MA#om=`, `MA#venc=`, `MA#plano=` |
| §7 4º cartão "A liberar" | "Ordens críticas abertas" (o chip já conta A liberar) |
| §9 orçamento de atrito | mesmo método; mede também trocas de tela (`ma_atrito_test.py`) |
| §11.2 1a "prefixo das 6 telas" (M:168, 277, 326, 557, 706, 1171) | prefixo de 1 página (`MA`); redirecionamentos sem prefixo |
| §11.2 1a: `man:{…, ach, …}` (PCMS l.185) | `man:{…, achados, leituras, recibos, …}` (pendência registrada em DECISOES §5) |
| §3.1 `o.ver` como versão do registro (PCMS l.190, 207) | `o.rv`; `o.ver` fica a versão do plano (pendência em DECISOES §5) |
| §11.2 1b reescreve `ma_passo`/`ma_exec` (M:379-401) | reescreve o painel único; Otávio já existe (S1) |
| §11.4 roteiro: "No MA-03, toque em 'Gerar 3 ordens preventivas'"; "Na MA-04, toque em 'Aprovar ordem'" | "Em Manutenção › Sem ordem, toque em 'Gerar 3 ordens preventivas'"; "no painel da OM-0235, toque em 'Aprovar ordem'" |
| §12 AC-11b "decisão aparece no MA-03 de outro quadro"; AC-23 e F6 "HTML da MA-04", "PM-01/PM-02" | "no painel da OM-0234 de outro quadro"; HTML de `MA`; painel do serviço |
| Anexo A PCMS-A02 "pelo MA-02 ou pelo MA-01" | painel Condição |

- Os números ficam: C1 R$ 2.626,00 · C2 R$ 1.776,00 · C3 R$ 4.392,00 · C11 R$ 1.791,00 (PCMS §10).
- A janela gerada também fica (OM-0235 em 24/09, PCMS l.484).

### 7.2 Ordem única (cada passo deixa o protótipo funcionando)
| Passo | Resultado útil | Inclui | Não inclui |
|---|---|---|---|
| **S1 · Uma entrada, uma tela** | menu com 1 item; `MA` com 4 visões; painel único da OM; detalhes de ativo e plano | §2, §3.1-3.5 com as regras de hoje; `v=3`: achados no estado, com componente; executante; responsável técnico; histórico encerrado; Registrar achado, Criar ordem corretiva e Fechar sem serviço; volta do achado; conflito calculado e "Mover janela" único; AL com 28/09; Ver como e matriz; Otávio no CD-04; período e custo; redirecionamentos e `build.py`; links de fora; fim da faixa, das 3 etapas, de "Marcar pendentes", de KPIs e selos fixos | MA-04det fica, aberto por "Abrir ordem completa" na OM-0233, sem faixa e com volta a `MA#vis=ordens` |
| **S2 · Um detalhe, um fato** | OM-0233 no painel único; condição e leitura gravadas | `v=4`; MA-04det sai; tipos de tarefa; Incluir tarefa; Teste com tentativas; Teste do reparo; Declarar apto / Manter; Encerrar com regra única; Peças retiradas; painel Condição com prazo e Encerrar restrição; painel da leitura com histórico e data corrigível; abastecimentos no estado; modo Abastecimentos; estorno; marco do vínculo | condição lida fora da Manutenção |
| **1a · Um estado** (PCMS §11.2) | manutenção dentro do cenário | como na PCMS, sobre 1 página, levando `achados`, `leituras` e `recibos` | — |
| **S3 · Fonte única fora** | CD-03 e O.S. leem condição, responsável e leitura | §3.8; teste de que O.S., CD-03 e `MA` mostram a mesma condição | impedimento derivado (PCMS-A05, Bloco 2) |
| **1b · Um estoque** (PCMS) | aprovar, Aprovar e liberar, conflito pela gerência, SC automática, sobras e consumo pelo EST, cancelar com chip Canceladas | sobre o painel único; saem "Liberar mesmo assim", "Mover mesmo assim", "Solicitar compra" e "Resolver sobras" | recebimento real |
| **1c · Compra e recebimento** (PCMS) | C2 e C11 completos | sai a ponte "Registrar recebimento" | — |
| **S4 · App** | MB-01, MB-09, MB-09det e MB-04 no cenário | §3.7: perfil Marcos · Zé, sem sinal, MB-04 → achado | diesel como lote (Bloco 6) |

- **Depois:** PCMS Bloco 2 restante (M20 "Incluir peça", M26) e Blocos 3-7.
- **Marcos com bateria completa:** fim do S2 e fim do 1c.
- **Mostrar ao dono, com uma tarefa curta:** depois do S2 (tela única) e depois do 1c (PCMS §11.4 reescrito).

## 8. Cliques antes → depois (especificado por leitura)

**Convenção (a do inventário):**
- parte de fora da Manutenção; "Manutenção" passa a ser 1 clique;
- lista de seleção = 2 cliques; lista curta em chips = 1 toque;
- campo digitado = 1 clique + teclas;
- trocas = troca de página.
- **Medição real:** `ma_atrito_test.py`.
- **Conflitos pela função D-38 sobre AL** (com 28/09):
  - OM-0234 (T02, 28/09): sim;
  - OM-0235 (T03, 24/09): não; restam 5 h livres e a OM pede 4 h;
  - OM-0236 (Plantadeira, 24/09): sim (OS-0420 e OS-0431);
  - OM-0237 (Bomba do Pivô 2, 01/10): não.

| Tarefa | Antes (cliques · teclas · trocas) | Depois (cliques · teclas · trocas) | Passo |
|---|---|---|---|
| (a) Zé conclui a OM-0234 liberada (5 tarefas), web | 11 (8 com o atalho de risco) · 4 · 0 | **11** (Manutenção · OM-0234 na fila · Iniciar · Feito ×5 · leitura · Previsto · Concluir) · 4 · 0; **12** no S2 (+ Conforme da Verificação do INSP-104) | S1; S2 |
| (a) Zé conclui a OM-0233 com teste e declara apto (responsável técnico do T1) | 5-6, sem gravar · 0 · 1 | **7** (Manutenção · Aprovado · foto · leitura · Previsto · Concluir · Declarar apto) · 4 · 0, gravando | S2 |
| (a) a mesma, no app | impossível | **7** (OM-0233 na Minha fila · Aprovado · foto · leitura · Previsto · Concluir · Declarar apto) · 4 · 0 | S4 |
| (b) SM-0150 → corretiva liberada | impossível | **5** (Manutenção · SM-0150 · Criar ordem corretiva · tempo · Liberar/Aprovar e liberar) · 1 · 0 | S1; 1b |
| (b) INSP-104 → OM-0234, resolvendo o conflito | 9 (6 forçando) · 0 · 3 | **5** (Manutenção · INSP-104 · Vincular · Mover janela para 29/09 · Liberar/Aprovar e liberar) · 0 · 0 | S1; 1b |
| (b) NC-0912 | 7 · 0 · 2, sem ver conflito | **5** (Manutenção · NC-0912 · Gerar preventiva com NC-0912 · Liberar · Liberar mesmo assim) · 0 · 0; no 1b, o 5º toque vira "Pedir decisão da gerência" | S1; 1b |
| (c) ver o que vence | 2, sem filtro de semana | **1** (Otávio abre em Sem ordem, prazo até 10 d) | S1 |
| (c) programar | 3 | **2** (+ "Gerar 3 ordens preventivas") | S1 |
| (c) liberar as 3 | 10 acumulado · 0 · 1, sem ver conflito | **11** acumulado (Abrir as 3 · Solicitar compra · Registrar recebimento · Liberar · Próxima · Liberar · Liberar mesmo assim · Próxima · Liberar) · 0 · 0 | S1 |
| (c) liberar as 3, com compra real | — | **8** acumulado (Abrir as 3 · Aprovar ordem · Próxima · Pedir decisão da gerência · Próxima · Aprovar e liberar); a OM-0235 espera a compra e a OM-0236, a Ana | 1c |
| (d) aptos agora | 2, sem % | **1** (Ana abre em Ativos) | S1 |
| (d) custo do mês | inexistente | **1** (cartão "Custo de manutenção · set/2026") | S1 |
| (d) custo de uma OM | 4 | **2** (Manutenção · ativo › Ordens) | S1 |
| (d) custo por ativo | inexistente | **1** (coluna com total) | S1 |
| (e) abastecimento, web | 13 · ≈17 · 0 | **9** (Manutenção · Ativos · ativo · Registrar · tanque · volume · leitura · operador · Salvar) · 7 · 0; 8 com o operador herdado da alocação; −1 com tanque único | S2 |
| (e) abastecimento, app | 1 toque fictício | **6** (Máquina · tanque · volume · leitura · foto · Registrar) · 7 · 0 | S4 |

**Sobe, por fato real** (AC-PCM-28):
- horas pelo chip (+1; sem valor implícito);
- Verificação de achado vinculado (+1 por grupo ativo × componente; PRD 54.5);
- "Próxima" entre OMs (+1 por OM depois da 1ª; o comando sai da linha, F62);
- conflito agora calculado (+1: "Liberar mesmo assim" ou "Pedir decisão");
- aprovação (+1 por OM; PCMS-M05);
- checklist de 18 itens = 18 toques (sem "Marcar pendentes"; PRD l.8371).

## 9. Critérios de aceite

IDs AC-PCM-nn (não "PCMS-nn", que colide com as regras da PCMS; D-26). Todo teste sai com código ≠ 0 quando falha.

| AC | Observável | Teste | Passo |
|---|---|---|---|
| AC-PCM-01 | Menu: grupo Manutenção com 1 item "Manutenção" → `MA.dc.html`, desenhado como link direto; card do Índice com 1 link | `ma_unica_test` | S1 |
| AC-PCM-02 | Rotas antigas (§3.1), com e sem âncora (`#OM-0234`, `#PM-01`, `#novo:a14`), abrem o destino da tabela; MA-04det só a partir do S2; páginas de redirecionamento fora do canvas; `build.py` e a varredura sem erro | `ma_unica_test`; `varredura.py` | S1; S2 |
| AC-PCM-03 | Nenhum link para tela removida: grep -E `(MA-0[1-5]\|PM)\.dc\.html` em `project/*.html`, fora das páginas de redirecionamento, = 0. "MA-04det" só no link "Abrir ordem completa" e no `det` da OM-0233 no S1; = 0 no S2. `links_ocultos_test` passa | `ma_unica_test`; `links_ocultos_test` | S1; S2 |
| AC-PCM-04 | Kanban com exatamente 5 colunas, nesta ordem; nenhum item sem OM tem fase nem aparece no Kanban; Canceladas só no chip próprio (1b) | `ma_unica_test` | S1; 1b |
| AC-PCM-05 | Uma primária visível por tela: em cada visão, detalhe e painel, ≤ 1 botão primário; com painel aberto, nenhum primário fora dele | `ma_unica_test` | todos |
| AC-PCM-06 | Nenhum botão de comando em `[role=row]` nas 5 grades | `ma_unica_test` | S1 |
| AC-PCM-07 | Sem faixa, stepper ou cartão de fase; contagem de fase só nos chips | `ma_unica_test` | S1 |
| AC-PCM-08 | "Gerar" só em Sem ordem, no painel do vencimento e no painel do achado. Gerar a partir do seed cria OM-0235, OM-0236 e OM-0237 em A liberar, sem reserva, com as janelas de hoje (24/09, 24/09, 01/10) | `ma_regras_test`; `ma_planos_test` | S1 |
| AC-PCM-09 | Achado: Criar ordem corretiva cria 1 OM em A liberar com ativo, componente, sintoma e criticidade herdados (repetir devolve a mesma); Alta → primária Criar; Vincular não é oferecido para a OM-0230 (Em conferência); Gerar com o achado (1 OM + vínculo); Fechar sem serviço exige motivo; o selo "Nova" sai; OM encerrada ou cancelada sem Conforme devolve o achado com "Voltou da OM-xxxx"; mesmo ativo e mesmo componente oferecem Somar, componente diferente não | `ma_regras_test` | S1; S2 |
| AC-PCM-10 | Sem "Marcar pendentes"; nenhuma tarefa nasce respondida | `ma_unica_test` | S1 |
| AC-PCM-11 | Tipos de tarefa: "Não feito" abre OM de Pendência (`ma_correcoes_om_test` mantido); "Não conforme" e "Não foi possível verificar" abrem ou somam achado; achado vinculado só fica Resolvido com Conforme; os achados do seed se resolvem pelo Teste (OM-0233) e pela Medição (OM-0228), sem Verificação a mais | `ma_regras_test` | S2 |
| AC-PCM-12 | Teste: Reprovado deixa a OM Em execução e o ativo Bloqueado, sem OM nova; Concluir é recusado sem a última tentativa Aprovada; depois de Reprovado e Aprovado, as duas tentativas aparecem no painel; a OM-0233 já traz a 1ª Reprovada; Ver como sem habilitação vê o Teste desabilitado com o motivo | `ma_regras_test`; `ma_unica_test` | S2 |
| AC-PCM-13 | Condição: Bloquear/Restringir grava condição, motivo, prazo, `por` e data. "Declarar apto" só em Em conferência com teste válido. Encerrar é recusado na OM que trata a condição sem "Declarar apto" ou "Manter". A OM-0228 (Medição Conforme) devolve a Bomba do Pivô 2 a Apto. A corretiva criada de um achado bloqueante ganha "Teste do reparo" e chega a Apto. "Encerrar restrição" sem OM aberta exige motivo e evidência. MA-04det não é gerado | `ma_regras_test`; `ma_unica_test` | S2 |
| AC-PCM-14 | Mesma condição do Trator T1 em `MA`, CD-03 e O.S. depois de bloquear e de declarar apto | `ma_unica_test` | S3 |
| AC-PCM-15 | Leitura: abastecimento, conclusão, achado e leitura avulsa chamam a mesma função; campo nunca pré-preenchido. Na conclusão, leitura menor é recusada (regressão: concluir com 150 h no Trator 02 não fecha o ciclo nem desloca referências) e leitura implausível dá aviso. Fora da conclusão, menor vira troca a confirmar. Tíquete com data anterior entra no histórico sem pedir troca. Vencimentos seguem a anterior até a decisão. CD-03 sem campo editável | `ma_regras_test`; `ma_correcoes_om_test` | S2; S3 |
| AC-PCM-16 | Abastecimento: herda ativo, operador da alocação e data (corrigível); lote pré-escolhido só com 1 elegível. "Registrar outro" com 3 tíquetes cria 3 lançamentos e limpa ativo, tanque, volume, leitura e evidência; duplo toque no mesmo cria 1. Estorno cria lançamento novo e mantém o original; L/h só com método | `ma_regras_test` | S2 |
| AC-PCM-17 | Cartões ≤ 4 por visão; nenhum valor fixo; "não calculável"/"não estimável"; tocar no cartão de contagem filtra; "Aptos agora" no lugar de "Disponibilidade"; custo pelo período escolhido | `ma_unica_test` | S1 |
| AC-PCM-18 | Nenhum selo fixo: grep "1 bloqueio ativo", "3 de alta criticidade", "1 desvio a investigar", "1 bloqueado · 1 restrito" em `MA` = 0 | `ma_unica_test` | S1 |
| AC-PCM-19 | Ver como: Otávio abre em Sem ordem, Zé em Ordens "Aguardam você" (OM-0233, ≥ 1), Ana em Ativos (ou Ordens, com decisão dela). Cada linha da matriz §3.1 é habilitada só para o papel dela. Passos-ponte habilitados para Otávio com "(simulado · …)": a OM-0230 encerra pela demonstração e a OM-0235 sai de A liberar. Trocar o papel não muda o estado gravado | `ma_unica_test` | S1 |
| AC-PCM-20 | F5 reabre `#om=`, `#achado=`, `#venc=`, `#ativo=`, `#plano=`, `#vis=…&tipo=`, `&modo=`; "‹ Ativos" e "‹ Planos" voltam com filtro e posição | `ma_unica_test` | S1 |
| AC-PCM-21 | As 5 grades com busca, filtro e ordenação; as tabelas dos detalhes com ordenação e busca acima de 10 linhas; unidade na célula; rótulos "Custo R$/h da oficina" e "Custo R$/h da máquina" | `ma_unica_test` | S1 |
| AC-PCM-22 | 390 × 844: sem rolagem lateral; Identificação e Situação à vista; ≥ 5 linhas da grade acima da dobra; painel em tela cheia com a primária sem rolar; painel aberto sozinho a ≥1024 px sem prender o Tab | `ma_unica_test`; `etapas_celular_test` | S1 |
| AC-PCM-23 | Planos: sem indicador de etapas; Publicar mostra diferenças e impacto; travas atuais passam (`ma_planos_test`, `ma_correcoes_pm_test` adaptados); "4 ativos sem plano" calculado. Vínculo: marco pré-preenchido só da OM encerrada do mesmo serviço, com origem à vista e corrigível; a corretiva OM-0221 não serve de marco para a Colhedora | `ma_planos_test`; `ma_correcoes_pm_test`; `ma_regras_test` | S1; S2 |
| AC-PCM-24 | Conflito: sem "Liberar mesmo assim"; Mover dentro da tolerância; Registrar decisão exige alternativa (PCMS AC-11b reescrito) | `pcm_sup_test` | 1b |
| AC-PCM-25 | C1, C2, C3 e C11 com os valores da PCMS §10, percorridos pela tela `MA` | `pcm_sup_test fluxo` | 1b; 1c |
| AC-PCM-26 | Peças retiradas: destino com responsável; nenhum movimento de lote; Encerrar recusado com peça retirada "A definir" (bomba da OM-0233) | `ma_regras_test` | S2 |
| AC-PCM-27 | App: Zé vê a OM-0233 na Minha fila; Marcos não vê OM. MB-09 mostra "Não opere" com o ativo Bloqueado. MB-09det conclui com as regras do painel. MB-04 com ativo grava achado visível em Sem ordem, inclusive a ocorrência "Equipamento" aberta pelo MB-01. Sem sinal: concluir e abastecer ficam no aparelho, o reenvio não duplica, e OM mudada vira "Conflito a resolver" | `mbtest.py`; `ma_unica_test` | S4 |
| AC-PCM-28 | Atrito: cliques, teclas e trocas das tarefas (a)-(e) medidos antes (hash base) e depois; nenhum total sobe sem a linha do §8 que nomeia o fato | `ma_atrito_test` | S1; S2; S4 |
| AC-PCM-29 | Dados sintéticos: nenhum dado real, nome real de cliente, coordenada ou segredo nos arquivos mexidos (varredura de segredos da CI) | CI | todos |
| AC-PCM-30 | Janela: o conflito sai da função sobre AL (OM-0234 em 28/09 e OM-0236 em 24/09 com conflito; OM-0235 e OM-0237 sem); "Mover janela" é o único comando de janela; "Próxima sem conflito" da OM-0234 = 29/09; fora da tolerância pede motivo (até o 1b); `o.vencOrig` preservado | `ma_regras_test` | S1 |
| AC-PCM-31 | Liberar exige executante; com uma pessoa habilitada ela vem pré-escolhida (Zé para Mecânico; João para Eletricista); sem executante: "Falta: executante" | `ma_regras_test` | S1 |
| AC-PCM-32 | Estado: o estado `v=2` salvo volta ao seed `v=3` (S1) e o `v=3` ao `v=4` (S2), sem erro de leitura de `c.achados`; `o.ver` continua a versão do plano (`ma_planos_test:69-70` passa) | `ma_regras_test`; `ma_planos_test` | S1; S2 |

**Aceite do corte:**
- cada F do §4 tem destino;
- cada essencial tem passo;
- nenhuma regra da PCMS foi reescrita aqui; as duas mudanças de nome que tocam a PCMS (`achados` e `o.rv`) estão em DECISOES §5;
- o Codex confere escopo e significado.

## 10. Fora de escopo
Em `FORA-DE-ESCOPO.md`, cada item com o motivo e a condição de retorno.

## Anexo · Revisão adversarial v1 → v2

Decisão: **aceito** (aplicado como pedido) · **ajustado** (aplicado de outro jeito, dito como) · **recusado** (com fundamento). Nenhum recusado.

| ID | Sev. | Decisão | Onde mudou |
|---|---|---|---|
| PCM-R01 | S2 | ajustado: matriz papel × comando; passos-ponte com Otávio, rotulados "(simulado · …)", em vez de pôr Rui no Ver como; Bloquear com Otávio e com o responsável técnico do ativo (não com Zé sempre) | §3.1 matriz; §3.3 tabela; AC-PCM-19; D-33 |
| PCM-R02 | S2 | ajustado: o "Teste do reparo" entra só na OM que trata a condição; no Restrito vale Medição Conforme; Encerrar exige "Declarar apto" ou "Manter"; "Encerrar restrição" com prazo no painel Condição | §3.3 Tarefas e Encerrar; §3.6; AC-PCM-13; D-34; FORA §1 |
| PCM-R03 | S2 | ajustado: Vincular em A liberar, Liberadas ou Em execução (como M:281), nunca Em conferência; regra de volta do achado aceita | §3.2 painel do achado; AC-PCM-09; D-35 |
| PCM-R04 | S2 | aceito | §3.5 Vínculo; F22; AC-PCM-23; D-41 |
| PCM-R05 | S2 | aceito: a conclusão mantém a trava da leitura menor (DM:420) | §0.1; §3.3 item 6; §3.6; AC-PCM-15; D-40 |
| PCM-R06 | S2 | ajustado: chave nova a cada registro; depois de salvar fica só a data; o operador é herdado de novo do novo ativo | §3.1 Comando; §3.6; AC-PCM-16; D-30 |
| PCM-R07 | S2 | aceito | §3.7 MB-04; AC-PCM-27 |
| PCM-R08 | S2 | aceito | §3.3 tabela de tipos; §0.1 OM-0233; AC-PCM-12; D-36 |
| PCM-R09 | S3 | ajustado: executante obrigatório e sugerido pela habilitação; OM-0228 → João (único NR-10 no CD-04); tarefa (a) feita com a OM-0234 (S1) e a OM-0233 (S2) | §3.3 Janela e equipe; §0.1 seed; §8 (a); AC-PCM-19, 31; D-37 |
| PCM-R10 | S3 | aceito | §3.7; AC-PCM-27; D-42 |
| PCM-R11 | S3 | aceito | §3.4 período, cartões e colunas; §0.1 histórico encerrado; AC-PCM-17; D-43 |
| PCM-R12 | S3 | ajustado: conflito = horas livres do recurso no dia menores que o tempo previsto, sobre AL; com isso o Trator 03 não tem conflito em 24/09 (5 h livres ≥ 4 h) e a Plantadeira tem; AL ganha 28/09 | §3.3 Janela e equipe; §3.8 AL; §8; AC-PCM-30; D-38 |
| PCM-R13 | S3 | ajustado: um comando, "Mover janela"; "Próxima sem conflito" definida; fora da tolerância vira aviso com motivo até o 1b e decisão da gerência no 1b | §3.3; §5 #32; AC-PCM-30; D-38 |
| PCM-R14 | S3 | aceito | §3.6; AC-PCM-15; D-40 |
| PCM-R15 | S3 | aceito | §3.2 painel do achado; AC-PCM-09 |
| PCM-R16 | S3 | aceito (lista com Órgão de trabalho) | §3.2 Registrar achado; AC-PCM-09; D-45 |
| PCM-R17 | S3 | ajustado: o responsável técnico fica nos dados de manutenção do ativo (DM), editável no painel Condição e só leitura no CD-03 (S3) | §0.1; §3.4; §3.6; F43; D-49 |
| PCM-R18 | S3 | ajustado: base única (início da janela, 10 d); cartões "Vencidas sem ordem" e "Em breve sem ordem"; o "7 d" sai; ordenação escrita | §3.2; §5 #30; D-28 |
| PCM-R19 | S3 | aceito | D-31 em §3.3; §8 refeito; AC-PCM-11 |
| PCM-R20 | S4 | aceito | visão "Sem ordem"; bloco "Janela e equipe"; §5 #29; D-44 |
| PCM-R21 | S4 | aceito | §3.1 Grades; §3.6 `c.leituras`; AC-PCM-21 |
| PCM-R22 | S4 | aceito | §3.1 Painel; AC-PCM-22 |
| PCM-R23 | S4 | aceito | §3.5; AC-PCM-23 |
| R01 | S2 | ajustado: "Incluir tarefa" em Corretiva e Pendência; Teste do reparo automático; Medição Conforme vale no Restrito; Encerrar com decisão de aptidão; OM-0228 com Medição | §3.3; §0.1; AC-PCM-13; D-34 |
| R02 | S2 | aceito (1ª opção). A parte "concluir com 29.950 e depois descartar" não se aplica: "Concluir com esta leitura" grava a leitura (DM:436) | §3.3 item 6; AC-PCM-15; D-40 |
| R03 | S2 | ajustado: um comando; conflito calculado; fora da tolerância é aviso com motivo até o 1b (não devolve a OM para A liberar); "Próxima sem conflito" fica, porque não depende da P10 | §3.3; AC-PCM-30; D-38 |
| R04 | S2 | ajustado: Em execução continua permitido, como no código (M:281), com o selo "Tarefa nova"; Em conferência nunca; caso da OM-0230 no AC-PCM-09 | §3.2; AC-PCM-09; D-35 |
| R05 | S2 | aceito | §3.3; §0.1 OM-0233; AC-PCM-12, 26; D-36 |
| R06 | S3 | aceito | §0.1 MA-04det no S1; §7.2 S1; AC-PCM-02, 03 |
| R07 | S3 | aceito | §3.1 tabela de redirecionamento; §0.1 `build.py`; AC-PCM-02, 20 |
| R08 | S3 | aceito | §0.1 estado; §7.1; §7.2; AC-PCM-32; D-47 |
| R09 | S3 | aceito | §0.3 |
| R10 | S3 | ajustado: mesma solução do PCM-R18 | §3.2; D-28 |
| R11 | S3 | aceito | §3.1 matriz; §3.2 "Registrar e bloquear"; D-33 |
| R12 | S3 | ajustado: a OM-0228 fica com João (NR-10), não com Zé (NR-12 não cobre serviço elétrico); a fila é ordenada pela janela e depois pela criticidade | §3.3; §3.7; §8; D-37 |
| R13 | S3 | ajustado: o S1 lê AL embutida no build (mesma fonte de O.S. › Recursos, declarada dado da semana); vira estado no Bloco 2 | §3.3; §3.6; D-38 |
| R14 | S3 | aceito | §3.3 Encerrar; AC-PCM-26; D-34 |
| R15 | S3 | aceito | §3.3 chips; AC-PCM-04; D-39 |
| R16 | S3 | ajustado: soma por ativo e componente (não pela origem: relato e inspeção do mesmo defeito devem somar) | §3.2; D-45 |
| R17 | S3 | aceito | §3.1 Comando; §5 #33; §7.1; D-46 |
| R18 | S3 | ajustado: D-31 vale para o seed, e os achados de origem se resolvem pelo teste válido da OM, sem Verificação a mais | §3.3 D-31; AC-PCM-11 |
| R19 | S4 | aceito | §3.2 (01/03/2027); §3.5 |
| R20 | S4 | aceito | §4 F62; saldo |
| R21 | S4 | aceito | AC-PCM-07, 08, 21, 22 |
| R22 | S4 | aceito | §3.4; §5 #31 |
| R23 | S4 | aceito | §3.4 cartão rotulado; histórico encerrado no seed |
| R24 | S4 | ajustado: base fixa `cd01b46`; os quatro arquivos que mudaram foram reancorados em `9c617c4`; CTL-2 conferido (sem sobreposição com a OM) | §0.1 Base; §3.7 |
| R25 | S4 | aceito | §3.2 prefixo; D-48 |

**Contagem:**

| Severidade | Aceitos | Ajustados | Recusados |
|---|---|---|---|
| S2 | 6 | 7 | 0 |
| S3 | 14 | 10 | 0 |
| S4 | 10 | 1 | 0 |
| **Total** | **30** | **18** | **0** |
