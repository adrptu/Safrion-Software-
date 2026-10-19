# PCM × Suprimentos de manutenção · v2 · Decisões

Complemento de `ESPECIFICACAO.md` (§14 do v1). Rótulo: especificado. Autor: Claude. Revisor: Codex. Nada aqui é aprovação do proprietário (AGENTS §2).

## 1. Assumi
- A OM é "O.S. de manutenção" (47.4 l.7728). A REQ da OM usa o campo `os`, com `dom:'man'`, e o rótulo "Entregue por O.S." do EST continua correto.
- **A reserva acontece na liberação** (DEC-2609-13 l.12227; DEC-2609-05 l.12220; 72.3 item 2, l.12234). O cap. 72 prevalece sobre a leitura isolada do CMD-42/44 (72.1, l.12208). Na aprovação, o CMD-42 gera a REQ, mostra a cobertura por linha e abre a SC da falta (PRD l.7053). O protótipo já reserva ao liberar (`cenario.js:4`; `dados_manutencao.py:389`).
- A cobertura planejada (M05) é derivada e não reserva: dá prioridade à OM aprovada antes só no cálculo da falta e no aviso. Quem libera primeiro leva a peça, com aviso.
- Responsável de manutenção: Otávio (`p11`, sintético). Ana (comprador e aprovador na CMP) e Rui (almoxarife) como em ESPECIFICACAO.md §3.3; acumular papéis é admitido (PRD 2.1 l.195) e não viola o RF-GOV-002.
- Peças "Sem lote" usam lote interno de entrada, gerado pelo sistema.
- O andamento da cotação fica no registro da CMP (`proc['SC-041']`); só os fatos (PC aprovado, recebimento) vão para o cenário. O andamento não vai para `c.scs[id]` porque `procGravar` roda a cada render (`processo_compras.py:594`).
- O prefixo SC-nnn continua (já existe em `dados_manutencao.py:396` e `ma_correcoes_om_test.py:75`); a origem distingue SC e SOL na CMP.
- A OM-0221 foi feita pela concessionária: as 14 h são do prestador e o serviço vale 3.800 − 1.280 = R$ 2.520 (Bloco 3).

## 2. Cortei
- Os 14 indicadores de um dos desenhos foram a 9 no v1 e agora a 3 no Bloco 1 (PCMS-I1, KPI-PCM-08, KPI-SUP-06) mais 4 nos Blocos 4 e 7 (KPI-SUP-05, PCMS-I7, KPI-PCM-10, KPI-PCM-02.MTTR/.RESTAURACAO). Saíram o I2 (sinônimo do componente "falta de peça") e o I4 (é a regra C01, não indicador).
- Não há PS separado: o serviço é PC do tipo serviço.
- Kit e peça retirada saíram do Bloco 1.
- Nenhuma tela nova, coluna nova, nem botão de compra ou de recebimento na MA-04 (a ponte do 1b é temporária e rotulada).
- A divergência da OM-0234 no SU oculto não será corrigida.
- `serv` e `ret` saíram do CEN0 do Bloco 1; entram no PR que os usar.
- Os critérios de aceite dos Blocos 2 a 7 deixaram de ser escritos pelo Claude: viraram "verificações propostas" no Anexo B.
- Saiu a `seq` de SC e de PC: os ids são derivados (maior + 1, com piso).

## 3. Parâmetros do dono, com default
Valem até o dono decidir. Mudar um parâmetro publica nova versão (CMD-29 l.2800).

| Parâmetro | Default | Fonte do default |
|---|---|---|
| P1 Custo-hora da oficina | R$ 320/h | `dados_manutencao.py:22` (hipótese) |
| P2 Alçada de compra de peça e serviço | A dos insumos, com as faixas da PCMS-G02 | `dados2.py:705` |
| P3 Tolerância de recebimento e de medição | 0% (DEC-07 pendente, l.10252) | Mais conservador |
| P4 Compra ou serviço emergencial sem pedido | Permitido só como fato registrado, com quem autorizou, quando e o motivo (padrão: o aprovador da OM; "ninguém autorizou" fica visível). Exceção sempre visível. Título só depois do PC de regularização na alçada normal. Sem teto especial | 47.5 l.7736; M25 e S07. Teto e autorizador: D1 |
| P5 Teste obrigatório para aceitar serviço | Sim quando a OM bloqueia o ativo (Bloqueado, Restrito ou Aguardando teste na abertura ou no aceite) ou quando o checklist tem item de teste ou medição (seed: "Teste de pressão em carga", OM-0233; "Medir pressão de recalque", OM-0228; "Teste em vazio", OM-0221). Nos demais casos vale o campo da linha, preenchido com "sim" e alterável com motivo | 47.5 l.7738; CMD-19 l.2790; RF-AST-005 l.2570 |
| P6 Metas dos indicadores | ESPECIFICACAO.md §7 e Anexo B | Revisar com 60 dias de dados reais |
| P7 Autorização econômica da OM (CF-02 de manutenção) | As faixas da P2 aplicadas à estimativa da OM (C01); na primeira, a aprovação do responsável de manutenção vale também como autorização econômica (PCMS-G07). Decisão do proprietário a confirmar (D1) | CMD-06 l.2777; 47.5 l.7740; RF-GOV-002 l.2673; faixas de `dados2.py:705` |
| P8 Automação de pedido por mínimo/máximo | Desligada. Só a sugestão de um toque que abre a SC. Ligada: limites por item e período, fornecedor e condições homologados, cotação e alçada mantidas | 65.5 l.9202; AGENTS §2 |
| P9 Quem decide conflito OM × O.S. de produção | Gerência dentro da alçada: Ana, gestora/PCP, nível Gerente da fazenda | 47.8 l.7820; `processo_compras.py:19`; `dados2.py:705` |
| P10 Capacidade semanal por especialidade | Não definida: "semanas equivalentes" do KPI-PCM-08 fica "não calculável" | KPI-PCM-08 l.8518 |

## 4. Pendente de dado real ou de decisão
Nenhuma destas pendências bloqueia o Bloco 1. As do dono dependem da realidade da fazenda; nenhuma é pergunta de programação (AGENTS §3.2).
- **D1 (dono):** quem aprova a OM e até que valor (P7); quem aceita serviço de oficina externa; teto e quem autoriza a compra de balcão (P4); quem é a gerência real que decide conflito de janela (P9).
- **D2 (dono):** custo-hora real da oficina (P1).
- **D3 (dono):** se os pneus entram agora.
- **D4 (dono, com o contador):** por qual valor a peça recondicionada entra no estoque, e em qual natureza vão os serviços de terceiros (hoje só existe a 3.1.05 "Peças e manutenção", `dados_cad.py:151`).
- **D5 (dono):** "Quando a OM espera dias por uma peça comprada, a peça já disponível e a peça que chega para ela devem ficar presas a essa OM desde a aprovação?" Dano que a trava evitaria: outra OM liberada antes consome a peça e a OM de origem volta a esperar compra. Base: CMD-44 (l.2827), cap. 42 "reserva pode apoiar planejamento" (l.7053), 47.8 item 5 (l.7821). Se aprovar, registra-se uma DEC e só então M05 e M13 reservam, com a ordem "criticidade, depois data" publicada como parâmetro (CMD-29).
- **Preços, prazos e fornecedores reais de peças** (dono).
- **Seed da OM-0233 (Codex, produto e QA; dado sintético, sem consultar o dono).** O protótipo é incoerente:
  - GE-03 (`gestao.py:279`): 18.400 = "peças + 6,5 h", provisório, aguarda NF;
  - GE-04 (`gestao.py:347`): NF 1203 da HidroMec de 18.400, conferida;
  - MA-04det (`maquinas.py:629-630`): ≈ R$ 6,2 mil, "sem terceiros";
  - seed (`dados_manutencao.py:193`): especialidade Mecânico, 6,5 h próprias.
  Somar 18.400 às peças e às horas conta o mesmo custo duas vezes (princípio 4, CAL-04) e fere a PCMS-C03. Opções: **(a)** OM-0233 própria, coerente com MA-04det, seed e REQ-034; os 18.400 deixam de ser serviço dela; o C9 usa serviço fictício com valor declarado como parâmetro do seed; GE-03 lê o custo do cenário (Bloco 7) e GE-04 deixa a HidroMec fixa; opcionalmente a HidroMec vai para o C10 como remessa de recondicionamento. **(b)** OM-0233 como serviço completo da HidroMec: custo 18.400, sem as 6,5 h próprias nem consumo próprio; contradiz REQ-034, C4 e a verificação ex-AC-30. **(c)** "O serviço é a diferença" (12.220), só se a NF 1203 também mudar. Qualquer opção muda `gestao.py:279` ou `maquinas.py:630`.

## 5. Conflitos resolvidos

### 5.1 Entre os dois desenhos do v1 (só os motivos que continuam valendo)

| Tema | Decisão e motivo |
|---|---|
| Quando reservar | **Na liberação** (DEC-2609-13). O v1 escolheu a aprovação; a revisão (achado A02) mostrou que contraria decisão registrada do dono. A alternativa virou a pergunta D5 |
| Campo da REQ de OM | `os` = OM + `dom:'man'`. Menos mudança: o rótulo do EST e o `esttest.py:88` continuam |
| Consumo acima da custódia | Vai para conferência. Reaproveita `confs`/`cenConciliar` (RN-018) e não trava um fato real |
| Números do C1 | 12 L, R$ 2.626,00: o valor que `ma_correcoes_om_test.py` já usa |
| Escopo do Bloco 1 | Inclui compra e recebimento. Sem eles, o C2 não pode ir ao dono |
| Ordem dos Blocos 2 e 3 | **Ativo antes do serviço.** Motivo principal: operar ativo bloqueado é candidato a S1 (§7), e RF-AST-001/005 são E1 enquanto RF-OPS-008 é E2 (l.2540, 2566, 2570, 4847-4848). O aceite depende do teste do Bloco 2 só quando a linha exige teste (P5). A divisão 3a/3b fica como opção (Anexo B) |
| Série do pedido de serviço | Mesma série PC-2xx, com `tipo` |
| Lubrificantes | Grupo próprio, natureza 3.1.04 (`dados_cad.py:150`) |
| OM-0221 | Serviço de R$ 2.520; o especialista era terceiro e a composição bate com 3.800 |
| R$ 18.400 da OM-0233 | O v1 os tratou como serviço sem pedido, somando R$ 24.580. **Revertido** (achado PCM-COD-03): é custo contado duas vezes. Pendência do Codex (§4) |
| Menu | "Compras": a tela passa a ter duas origens |
| Numeração | Uma solução para REQ, SC e PC: maior + 1, com piso. Mantém a REQ-041 (`os_v39_liberar_test.py:43`) e o PC-201 |

### 5.2 Entre achados da revisão (resolvidos uma vez)

| Sobreposição | Decisão |
|---|---|
| PCM-COD-02 (reescrever `manFalta` no 1a) × PCMS-R05 (1a sem mudar regra) | R05: o 1a só muda o acesso e mantém `itens.saldo`; o defeito do COD-02 deixa de existir. `manLivre`, os 7 leitores de saldo e as verificações negativas do COD-02 vão para o 1b, reescritos uma vez |
| PCM-COD-04 (id derivado) × PCM-COD-05 (manter `seq.pc:201` e semear PC-200) | Os dois: id derivado (maior + 1, piso 201) e o C8 com PC-200. A invariante do COD-05 ("nunca sobrescrever") vira o U30 |
| A05 (`prev` + `prevOrig` + `prevHist`) × PCMS-R10 (`prevs` só de acréscimo) | R10: uma lista e `prevAtual()`, sem segundo campo de data (uma fonte). O selo com "prometido" e o OTIF de A05 usam `prevs[0]` |
| A06 × PCMS-R09 (indicadores) | ID do PRD quando a fórmula é a do PRD (KPI-PCM-08, KPI-SUP-05, KPI-SUP-06, KPI-PCM-02.MTTR/.RESTAURACAO, KPI-PCM-10); ID local quando não é (PCMS-I1, PCMS-I7). Capacidade do KPI-PCM-08 como P10 sem default numérico (A06), e não derivada do turno (R09) |
| A03 × PCMS-R13 (autorização econômica) | Uma regra, PCMS-G07: default de A03 (faixas da `ALCADA`), gating da SC de R13 (a SC só abre com `autEcon`), checagem no liberar e no entregar |
| PCM-COD-06 × PCMS-R07 (toques) | R07: medir antes de prometer, saldo por papel, "Entregar REQ inteira", teto N. Os limites do COD-06 entram no AC-24 como forma de comparação, não como número fixo |
| PCMS-R02 "M25" × PCMS-R12 "M25" | Balcão fica M25 (Bloco 1c); remanejar vira M26 (Bloco 2) |
| U-tests novos de A04, R02, R07, R12, R13 (todos começando em U25) | Renumerados uma vez em ESPECIFICACAO.md §11.3 (U01-U44, F1-F9) |
| A07 "P8" × A08 "P8" | P8 = automação de pedido; P9 = quem decide conflito |
| PCMS-R02 (peça de balcão para OM em A liberar fica reservada) × DEC-2609-13 | Fica livre e cobre a OM pela cobertura planejada; reserva na liberação |
| PCMS-R12 (preventiva aprovada segura o kit) × DEC-2609-13 | Sem reserva na aprovação, o problema só sobra para OM Liberada; o M26 vale a partir de Liberadas |
| A14 ("Sobras a receber") × instrução "nomes do PRD 8.4.3" | A14: o selo usa o texto que o protótipo já usa na O.S. (`processo_os.py:242`), e a divergência com "Sobras pendentes" vai à v3.10 com duas opções; nunca trocar só na OM |
| A08 (PL-03/04/05 lendo o cenário) × tamanho do Bloco 1 | Decisão e Mover no 1b (MA-03); PL-03/04/05 lendo `o.conflito.dec` no Bloco 2, junto com A05-A07 |
| PCMS-R09 item 7 (alinhar Rui e Paula) × PCMS-R13 item 4 (não renomear) | Nada a renomear: a tela CD-04 já mostra Rui almoxarife (`cad_ativos_pessoas.py:34-37`, executado: leitura) |

### 5.3 Entre a revisão e as instruções desta rodada
- **Portão do Bloco 1.** O achado PCMS-R01 pedia a 2c e a 2d integradas antes do 1a. A instrução desta rodada fixa "PR aberto com bateria verde". Adotei a instrução como portão de início e o merge da 2d como portão de integração do 1a (ESPECIFICACAO.md §0.2).
- **§14.5 para o arquivo da rodada** (achado PCMS-R15, item 4). Esta rodada só escreve em `v2/`; a tabela fica em §5.1 e o Codex a move para `docs/parceria/rodadas/` ao abrir a rodada da fatia.

## 6. Propostas ao PRD v3.10 (autor: Codex; revisor: Claude; entrada por PR)
1. Contrato do SU-07 (l.1241): incluir a O.S. de manutenção autorizada pelo responsável de manutenção (47.4).
2. Selos da 8.4.3 (l.2962), com o mesmo texto do ESPECIFICACAO.md §5.2:
   - adaptações: "Aguardando aprovação" no lugar de "Aguardando agrônomo" para a OM (47.4 l.7728); "Falta peça" equivalente a "Falta insumo"; "Revisão pendente" como adaptação de "Revisão de saldo pendente" (l.2978);
   - novos: "Aguarda autorização econômica", "Aguarda pedido de compra (PC) · previsão" (no protótipo, "Aguarda PC-201 · prev. dd/mm · fornecedor"; "Aguarda pedido" sozinho se confunde com "Falta peça · SC-041"), "Compra sem pedido · regularizar", "Pronta para liberar", "Aguarda entrega", "Consumo em conferência" (já em `cenario.js:144`), "Cancelamento pendente" (CMD-46), "Aguarda teste" (47.5 l.7736, 7740), "Serviço a aceitar", "Ativo bloqueado" (já em `dados_manutencao.py:350, 380`), "Conflito · OS";
   - divergência "Sobras pendentes" (l.2962, 2964) × "Sobras a receber" (protótipo, na O.S. e na OM): (a) a v3.10 adota "Sobras a receber", inclusive no exemplo obrigatório da l.2964; ou (b) o protótipo renomeia na O.S. e na OM ao mesmo tempo (`processo_os.py:241-242`, `inicio.py:637-641`, `suprimentos.py:830`, `planejamento.py:423`, `dados.py:32, 90`, e os testes `os_v39_bloq_test.py:33-37`, `map_irrig_filtro_test.py:88`, `map_decisoes_test.py:83`).
3. Fluxos: FL-15 e FL-PCM-01/02/03 ganham raias de Almoxarifado e Compras; o nó A do FL-10 (l.3457, "1 · Abra a demanda da safra"), a etapa 1 da Compras na 71.6 (l.10367) e o nó A do UX-03 (l.11879) passam a "Abra a demanda (safra ou manutenção)".
4. RF-OPS-008 (l.2540): incluir a MA-04 nas telas; definir pedido de serviço com medição e aceite (estende FO-17 e FO-18, l.2327-2328).
5. CD-05 (l.1748, 1752): definir o grupo de serviço (não estocável) e a especialidade como atributo da homologação. A regra "papel Fornecedor + grupo + e-mail" continua.
6. 69.3 (l.9479-9487): SU-01 a SU-09 passam a depender do cap. 47 e de PCM-06/07.
7. Estados e valorização de peça recuperável e de garantia; definição de kit de preventiva (65.2).
8. Registrar o **pedido** de 05/10/2026 no cap. 72 e em `docs/DECISIONS.md`, como pedido e não como aprovação.
9. Só se o dono aprovar a D5: reserva desde a aprovação para OM, com a ordem de alocação do que chega como parâmetro.
10. Remanejamento de reserva entre O.S. de manutenção como composição atômica de CMD-44, decidida por quem tem a alçada (47.8) (M26).
11. Só com decisão do dono: delegar ao responsável de manutenção a decisão de conflito com produção, com o dano nomeado (FORA-DE-ESCOPO.md §1).

## 7. Severidade proposta para o software real (o Codex confirma em QA)
Regra: uma versão real que habilita o domínio afetado não sai com S1 ou S2 conhecido (ENG-003 l.5185; AGENTS §3). Cada item traz a categoria da 22.1 (l.5189) e o dano.
- **S1 candidato · comando físico perigoso, por analogia** (o sistema autoriza operar máquina insegura): iniciar O.S. ou turno com ativo bloqueado; liberar ativo sem teste válido (CMD-19; AC-40 l.4800; PCM-08 l.7802; PCMS-A03).
- **S2 · duplicidade de obrigação ou movimento:** repetir receber, entregar, consumir, devolver ou aceitar grava segundo efeito (PCMS-G04; RF-SUP-008 l.2590).
- **S2 · cálculo material incorreto:** custo da OM contado duas vezes, ou com peça não consumida ou serviço não aceito (CAL-04 l.4249; PCM-09; RN-030); estoque paralelo ou saldo que nenhum movimento explica (RF-SUP-003 l.2585); entregue, consumido, devolvido e custódia que não fecham (RF-SUP-008); entrada que muda saldo ou custo sem origem (PC com NF) e sem exceção emergencial registrada (RF-SUP-007 l.2589; 47.5 l.7736; P4); saldo criado por ajuste de inventário para cobrir compra sem pedido.
- **S2 · obrigação indevida:** serviço não aceito vira título (RF-OPS-008 l.2540; S06).
- **A classificar em QA:** peça entregue a OM sem autorização do responsável de manutenção (PCM-07 l.7801; 47.4 l.7728). Não herda a regra da aprovação agronômica, porque a manutenção é exceção (AGENTS §3). S1 se a falha estiver na permissão do servidor; S2 se o efeito for no estoque e no custo.

A proteção acompanha o domínio habilitado (P0 obrigatório antes de operar o domínio, l.111): Blocos 1a/1b e 2 (RF-SUP-003/007/008, RF-AST-001/005, E1) antes de habilitar o PCM com estoque; Bloco 1c (RF-SUP-004/005/006, E2) antes da compra; Bloco 3 (RF-OPS-008, E2) antes do serviço de terceiro.

**Quais domínios entram na primeira versão real é decisão do proprietário** (AGENTS §2; DEC-2709-01, `docs/DECISIONS.md:25`). Isto é proposta.

## 8. Evidência
- **Executado em 05/10/2026, só leitura:**
  - `git log`, `git status` e `git branch -a` em `/home/user/sp-tab5` (HEAD `0cf6f90`, branch `claude/v44-tabelas-05`, só arquivos não rastreados).
  - Leitura das linhas citadas no PRD, em `docs/DECISIONS.md`, em `tools/prototipo/v37/RETOMADA-NUVEM.md` e no `gen37`.
  - Python sobre o seed: CEN0 = 19.134 caracteres; `man` = 19.195; DM.JS = 25.856; `cenario.js` = 25.143; 27 lotes em 5 locais; 11 requisições (REQ-021..025, 031, 035, 036, 038..040); preços e saldos de `ITENS`; seed `v=3`.
  - Node sobre o JS da manutenção (`manGerarTodas` num clone do seed): OM-0235 (a03, PM-02, Alta, janela 24/09, FIL-MF4292 1 un + OL-1540 12 L, 4 h, falta do filtro), OM-0236 (a06, Alta, janela 24/09) e OM-0237 (a11, Média, janela 01/10).
  - Python (`docs/pcm-suprimentos/verificacao/contas.py`, com `Decimal`): C1 2.626,00 (e 2.738,00 com 16 L e como estimativa); C2 1.776,00 (F08, 160,00) e 1.771,20 (F09, 155,20; diferença 4,80); chegada F08 24/09 sem atraso e F09 29/09 com atraso, contra a necessidade de 24/09; C3 4.392,00; C4 6.180,00; C8 1.280 + 2.520; C11 1.791,00; OM sintética 55.280,00; lotes do C1 (1, 104, custódia 4, 108) e do C3 (5); 13 lotes do Almox. oficina, 10 com saldo; 14 requisições depois de restaurar; espera de 1 dia no teste unitário; atraso de 3 dias contra `prevs[0]` no exemplo do KPI-SUP-05; diesel 5.700 → 5.520 L.
  - Existência dos scripts de §0.3 (`ls`); contagens fixas nos testes (`est_cenario_test.py:99`, `os_cenario_test.py:87-89`, `cadp_fix_test.py:75, 80`, `cada_cd04_test.py:25, 28`).
- **Não executado:** nenhum teste do protótipo, nenhum build, nenhum navegador. Nada foi editado fora de `docs/pcm-suprimentos/` e `docs/pcm-suprimentos/verificacao/`. Sem checkout, commit ou push.
- **Especificado:** todo o resto.

## 9. Revisão adversarial aplicada
Fonte: `docs/pcm-suprimentos/verificacao/revisao.json` (42 confirmados; 1 refutado, PCM-COD-01, não mudou nada). "Spec" = ESPECIFICACAO.md.

| ID | O que mudou |
|---|---|
| PCM-COD-02 | `manLivre` e os 7 leitores de saldo (`dados_manutencao.py:387, 397, 424`; `maquinas.py:382, 469, 893`) reescritos uma vez no 1b; verificações negativas do PM e do painel e grep de `itens[...].saldo` na F6. O 1a não apaga `saldo` (ver §5.2) |
| PCM-COD-03 | C9 sem total fixo (invariante C4 + aceito); R$ 24.580 saiu; incoerência do seed da OM-0233 registrada como pendência do Codex com três opções (§4); ex-AC-30 qualificado ao estado do Bloco 2; `gestao.py:279` e `maquinas.py:630` nos arquivos do Bloco 3 |
| PCM-COD-04 | `cenProxId` com piso 201 e PCs fixos; `solDe('SC-…')` sem `pcIni`; prévia em `M()`; `emitir` grava pelo cenário; `pick` e `abrirHash` aceitam SC; `cenGravarPedidos` idempotente por (SC, fornecedor); U21 |
| PCM-COD-05 | C8 semeia PC-200; seed separado do exemplo pós-C2 no §3.1; ids nunca sobrescrevem (U30); regressão C2 → C9 no Anexo B; exemplo de inteligência "Serviço HidroMec · OM-0233 medido" |
| PCM-COD-06 | §9 com regra de contagem e saldo por papel e por tela; AC-24 compara com o "antes" medido; o roteiro avisa que o dono faz a parte do mecânico na MA-04 |
| PCM-COD-07 | Lubrificantes entra só em `dados2.py:682`; `assert` de grupos únicos após `dados_cad.py:117`; AC-02 confere grupo único e select sem repetição |
| PCM-COD-08 | DM.JS só nas telas que chamam `man*`; `man` no CEN0 de todas; tamanhos executados por grupo de tela; guarda sobre `project/*.html` |
| PCM-COD-09 | Bateria com cadastros, AG, MB e app; `HABILIDADES`/`_ORDEM` do Otávio; `cada_cd04` 11/11; ajustes de `cadc_cd06`, `cadc_fix_cd06` e `cadc_cd07`; AC-02b |
| PCM-COD-10 | Tabela de sinais por tipo (§3.2); `entrega.res`; grep estrutural forte (U44); conciliação por movimento em todo lote (C06); `osc_cancelar` passa por `cenEstornarReserva` |
| PCM-COD-11 | "Compras" no menu, na trilha, no `<title>`, no `<h1>`, no docstring, no guia e no índice; subtítulo com as duas origens; botões do SAF mantidos de propósito; proteção no `cmptest.py` |
| PCM-COD-12 | Roteiro do dono nomeia tela, caminho e resultado: gerar no MA-03, abrir a OM-0235, aprovar na MA-04; OM-0236 e OM-0237 fora do teste |
| PCM-COD-13 | Linha "Lote de Diesel S10" em "Não existe"; semente com fonte (5.700 L, R$ 6,19); decisões de código do lote, comboio e versão; verificação de 180 L no Anexo B |
| A01 | M19 reescrita pelo CMD-46: só sem trabalho iniciado, "Cancelamento pendente · Rui", Cancelada só com custódia zero e REQ conciliada, função comum com a O.S.; U16-U19; AC-19b; selo e rótulo "Cancelar sem execução" |
| A02 | Reserva na liberação (DEC-2609-13) em M05, M06, M09 e M13, no diagrama, nos casos e nos testes; argumento do CMD-05 retirado; D5 ao dono e proposta 9 |
| A03 | PCMS-G07 (autorização econômica no liberar e no entregar, com estimativa pela mesma função do custo); P7 com default das faixas da `ALCADA`; princípio 2 reescrito; AC-08b; U37-U38 |
| A04 | PCMS-G04 com `chave` gerada por quem abre a ação e `ver` por objeto; recibos na mesma mudança; FO-18 continua; U31-U36; AC-07 e AC-07b; nota do MB-05 offline no Anexo B |
| A05 | Data prometida versionada (`prevs`, ver §5.2), selo com "prometido", KPI-SUP-05 contra `prevs[0]` com denominador pela promessa original; AC-14; verificação B4 |
| A06 | KPI-PCM-08 com a fórmula do PRD e três componentes; PCMS-I1 local, população alinhada e envelhecimento; KPI-PCM-02 separado em .MTTR e .RESTAURACAO; caso de OM com falta aberta no U27 |
| A07 | PCMS-G05 separa os verbos e as fontes; P8 desligada; o "Nunca" saiu de FORA-DE-ESCOPO e de §6 |
| A08 | M09b: conflito decidido pela gerência com alternativa registrada; Mover dentro da tolerância; C1 por Mover e C1b por decisão; P9; selo "Conflito · OS-0420 · Ana (gerência)"; `ma_planos_test.py:53-56` a ajustar |
| A09 | P5 cobre ativo Restrito e checklist com teste ou medição; S05 com default e motivo; C07 como regra do PRD, sem parâmetro novo; verificação na OM-0228 |
| A10 | §7 com categoria da 22.1 por item, casos que faltavam e a decisão de escopo devolvida ao dono; Bloco 3 com P0 por RF-OPS-008, não por "pedido expresso" |
| A11 | `semPedido = {autorizou, em, motivo}` no serviço (S07) e na compra (M25); P4 exige autorizador; seed do C9 com autorizador e motivo; verificação B3 |
| A12 | Prestadores com papéis Fornecedor e Prestador, homologados no grupo "Serviços de manutenção"; S02 pela regra vigente da l.1752; efeitos em `dados2.GRUPOS`, `GRUPO_NAT` e `cotaveis()`; proposta 5 |
| A13 | M20: só aumento volta à aprovação; redução estorna com motivo; "Revisão pendente" na OM em execução; dano nomeado |
| A14 | Selo "Sobras a receber · Rui"; a mensagem da M18 não é selo; um só texto para o selo do PC; proposta 2 com todos os selos e a divergência "Sobras pendentes" |
| A15 | RN-042 na frase de "um estoque"; S06 com SU-06, GE-04, RF-SUP-011 e RF-LOG-004 por analogia; M13 com RF-SUP-007, 47.4 e DEC-2609-13 |
| PCMS-R01 | Portões em §0.2; o 1a muda a saída das 23 páginas do cenário; bateria inteira em todo PR; retrato do repositório atualizado (`0cf6f90`, `origin` em `cd9cdc3`) |
| PCMS-R02 | M25 (balcão) no 1c, com autorizador, regularização visível e sem estoque fantasma; C11; U41-U43; AC-17a; S2 do ajuste para cobrir compra sem pedido |
| PCMS-R03 | Motivo da ordem dos blocos corrigido; limitação "sem serviço de terceiro" no roteiro do dono; divisão 3a/3b como opção |
| PCMS-R04 | F08 com prazo de 1 dia; `precisa` em ISO; `falta` da SC = menor `precisa`; roteiro com a proposta sugerida; espera de 1 dia no teste; mensagens de inteligência reescritas; F09 exige justificativa |
| PCMS-R05 | 1a só muda o acesso; 1b reescreve uma vez, com ponte rotulada para o C2; 1c troca a ponte pela compra real; homologação de C1+C3 depois do 1b |
| PCMS-R06 | `tok` na SC e na chave do `solDe`; limpeza dentro de `cenReset` com `cenSave`; CMP descarta andamento antigo; F7 com os cinco botões e a troca de versão |
| PCMS-R07 | Medição antes e depois por papel; "Entregar REQ inteira"; teto N da compra; manchete honesta; ordem do roteiro do dono corrigida |
| PCMS-R08 | M12 e §5.1 dizem o que a 2d faz e o que não faz; o 1c muda unidade dos 4 campos e das 3 mensagens, `epedBase`/`efert` e o fallback "kg"; U24 |
| PCMS-R09 | I2 removido; I6 vira KPI-SUP-06 sem a meta trivial; I8 vira KPI-SUP-05; um dono por indicador; até quatro cartões; I1 com envelhecimento |
| PCMS-R10 | `prevs` só de acréscimo, `prevAtual()`, `cenReprogramarPC`; `pcx` sem `prev` para PC-2xx; U22 |
| PCMS-R11 | Chave da SC definida (tipo, origem Manutenção; linha por `cod`; origem por OM e `cod`); "A cotar"; congelamento no "Enviar convites"; SC-nnn mantido com justificativa; estado `{tipo, id}` na CMP; U14; F9 |
| PCMS-R12 | M06 cita o remanejamento; M26 (Bloco 2) adaptada à reserva na liberação; caso C7b; gatilho de inteligência; proposta 10 |
| PCMS-R13 | G07 com SC só depois da autorização; `confirmado:'balcao'` e textos de entrega na OM; Ana e Rui declarados no §3.3 |
| PCMS-R14 | Mesma correção do PCM-COD-07, aplicada uma vez |
| PCMS-R15 | Valores só no §10; regras com mensagem e dano; U-tests citam regra e caso; §12 virou matriz; §8 integrado ao §2.2; Blocos 2 a 7 no Anexo; ACs dos Blocos 2 a 7 viraram verificações propostas ao Codex; §13 e §14 viraram arquivos próprios |

## 10. Achados aplicados em parte, com motivo
- **PCMS-R09, item 1 (capacidade do KPI-PCM-08 tirada das escalas):** não apliquei a derivação (motivo em FORA-DE-ESCOPO.md §1). Ficou a P10 sem default numérico e "não calculável", como propõe o achado A06.
- **PCMS-R09, item 7 (alinhar o cadastro do almoxarife):** nada a alinhar na tela (§5.2).
- **PCMS-R01 (portão "integradas por PR revisado"):** apliquei como portão de integração do 1a; o de início segue a instrução desta rodada (§5.3).
- **PCMS-R15, item 4 (§14.5 no arquivo da rodada):** ver §5.3.
- **PCMS-R05, item 2 (ponte com lote OF26-02):** a ponte usa o mesmo gerador de lote interno do 1c (OF26-15), para haver uma solução só.
- **A08, item 4 (PL-03/04/05 lendo o cenário):** adiado para o Bloco 2 (§5.2).
- **PCMS-R03, item 3 (divisão 3a/3b):** é opcional no próprio achado; ficou registrada, sem ser adotada.

## 11. Conferência da v2 contra a revisão (05/10/2026)
Conferência feita por um subagente Claude a pedido do fluxo desta rodada. Não substitui a revisão do Codex (AGENTS §3).

**Executado (só leitura do `gen37` em `0cf6f90`; escrita só em `v2/`):**
- Leitura dos 42 achados confirmados (`revisao.json`) e dos três arquivos da v2. Resultado: 39 resolvidos, 3 em parte com motivo (PCMS-R01, PCMS-R09, PCMS-R15; §10), nenhum aberto.
- `python3 calc/contas.py`: saída igual a `verificacao/contas.out`.
- Recálculo independente importando `dados_manutencao` e `dados2` (preços, planos PM-01/PM-02, `_oms()`, `CUSTO_H`, `HOJE`): C1 2.738,00 (estimativa) e 2.626,00; C2 1.776,00 (F08, 160,00) e 1.771,20 (F09, 155,20); C3 4.392,00; C4 6.180,00; C8 1.280 + 2.520; C11 1.791,00; sintética 55.280,00; F08 chega 24/09 sem atraso, F09 29/09 com atraso, contra 24/09; 13 lotes, 10 com saldo. Tudo bate com o §10.
- `cenario.seed()`: v=3, 27 lotes, 5 locais, 11 requisições, sem diesel; chaves `v, rev, ordens, reqs, lotes, movs, ocorr, app`. Tamanhos 19.134 (CEN0), 19.195 (`man`), 25.856 (DM.JS). Contagens fixas conferidas: `cadp_fix_test.py:75` (20), `cada_cd04_test.py:28` ('10/10'), `est_cenario_test.py:99` e `os_cenario_test.py:89` (11), `os_v39_liberar_test.py:43` (REQ-041). Scripts da §0.3 existem, exceto o novo `pcm_sup_test.py`.
- `grep -i reserv` nos três arquivos: nenhum resto de "reserva na aprovação" fora da pergunta D5, da proposta 9 e da linha de FORA-DE-ESCOPO que a recusa.

**Corrigido nesta conferência:**
1. **M05 (ESPECIFICACAO l.267).** A cobertura somava "quantidade em SC ou PC aberto". Isso contradizia o C2 ("filtro 0/1" com a SC já aberta), o U25 e o U26 (cobertura só fecha com peça apta) e a PCMS-I1 (espera até a cobertura completa). Agora a cobertura é só o livre físico; SC e PC mudam o selo e não voltam à SC.
2. **§3.1 ids (l.189).** "A faixa PC-101..200 fica com as safras" contradizia o PC-200 do C8. Agora: as safras numeram a partir de PC-101, 10 por safra (4 safras no seed, até PC-140).
3. **§3.1 seed (l.184).** `confs` e `ajustes` não estão no seed; nascem no uso (`cenario.js:107, 182`).
4. **§3.2 (l.225).** Faltava o tipo `recebimento` do app (qtd 0, `cenario.js:123`) entre os movimentos sem efeito no lote. Sem ele, a C06 não classifica todo movimento.
5. **Anexo B, B2 (l.721), reserva na liberação.** "Reduzir 16 → 14 L na OM-0234 estorna 2 L" supunha reserva sem dizer a fase; agora vale para a OM-0234 Liberada, e na aprovada só muda a cobertura. O MA-03 saiu da lista do Bloco 2, porque já lê `o.conflito.dec` no 1b (§5.1, C1b, AC-11b). A verificação "GE-03, GE-04 e MA-04det com o mesmo custo da OM-0233" foi para o B3, onde mudam `gestao.py:279` ou `maquinas.py:630` (PCM-COD-03).
6. **C2 e C11 (l.490, 492).** Faltava "Iniciar" antes de "Concluir".
7. **§5.2 item 10 (l.404).** "Sobras a receber · Rui", igual a AC-04, F1 e ao padrão "selo · dono" dos outros itens.
8. **§12, aceite do corte (l.666).** O `grep -c "2.626"` contava a própria linha (dava 2). Agora o padrão é `'2\.626'` e o custo do C2 no roteiro do dono (§11.4) fica declarado como a única repetição necessária.
9. **Repetição cortada (fonte única, AGENTS §3.4):**
   - §2.3: os invariantes da REQ e do PC remetem à C06 e à G02;
   - M11: o selo remete ao §5.2 item 5; as datas ficam só em U22 e AC-14;
   - §5.1: as fases do "Cancelar sem execução" remetem à M19; os atalhos com o nome antigo remetem a FORA-DE-ESCOPO §4;
   - AC-19b: fica só o observável que não está na M19;
   - faixas de alçada: só na G02; G07, §3.3, C11, P2 e P7 citam a G02 (o "até R$ 50.000" da G07 fica, porque é o texto observável do AC-08b);
   - DECISOES §1 (pessoas) remete ao §3.3; §10 (PCMS-R09 itens 1 e 7, PCMS-R15 item 4) remete a FORA-DE-ESCOPO §1, §5.2 e §5.3;
   - FORA-DE-ESCOPO §1: "Volta quando" de D5 e P8 remete a DECISOES §4 e §3.

**Não executado:** nenhum teste do protótipo, build ou navegador.
