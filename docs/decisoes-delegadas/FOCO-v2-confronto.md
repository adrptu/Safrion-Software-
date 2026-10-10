# Confronto: FOCO-APLICACAO-REAL v2 e checkpoint × passos 1 a 3

**Autor:** Claude · **Revisor:** Codex · **Data:** 10/10/2026 · **Pedido:** recibo 6091443216, item 5
**Base:** `docs/decisoes-delegadas/DECISOES-DELEGADAS.md` §5 (passos 1 a 3), a partir de `64040f8`; worktree em `7d38e5d`

**Para que serve.** O conjunto vigente do protótipo é **todo** o conjunto de melhorias já pedido ou em andamento, com os IDs e estados do checkpoint, e não só os passos 1 a 3 do parecer. Os passos são uma organização proposta, não uma lista exaustiva. Esta tabela mostra onde cada ID está nos passos ou que ele está fora deles. Este arquivo não cria regra nem fila: a fonte canônica é o FOCO v2, e o estado vem do checkpoint.

## Fontes

| Fonte | Rótulo |
|---|---|
| FOCO-APLICACAO-REAL v2: https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5974888468 (criado em 04/10 às 00:12Z, editado às 00:14Z) | executado: leitura integral em 10/10/2026 |
| Checkpoint da issue #1, comentário 5858061746, só leitura (cabeçalho "Checkpoint vigente — 2026-10-10 00:00 UTC", `updated_at` 2026-10-09T23:59:53Z, 241 linhas) | executado: leitura integral em 10/10/2026, sem edição |
| Recibo do Codex 6091443216 (PR #47) | executado: leitura em 10/10/2026 |
| PR #47, comentários 6091432263 (DOM) e 6091433483 (pacotes PCM, NAV-1 e SAF) | executado: leitura em 10/10/2026 |
| `tools/prototipo/v37/RETOMADA-NUVEM.md`, linhas 149 a 334 (última mudança `e847a1d`, 05/10): composição da fila D7 e dos contratos de 03/10 | executado: leitura em 10/10/2026; o estado ali é de 05/10 |
| `git log` da branch `claude/prototipo-v44` (merges da REND, da AÇÃO e das TABELAS-FOCO) | executado em 10/10/2026 |
| Busca por "hiperclareza" em todo o repositório | executado em 10/10/2026: nenhum resultado |
| Cabeçalhos anteriores do checkpoint (`dom-1fd8cfa/checkpoint-header-2325.md` e `ben-1440889/checkpoint-header-2349.md`, na pasta local do Codex) | **não lido**: fora do repositório |
| Textos dos nove contratos de 03/10 (5974199895, 5974202396, 5974203077), QUALIDADE v2 (5974025581) e pedidos de 09/10 (6079601661) | **não relidos** nesta etapa |

## Confronto

"Permanece" é o termo do bloco "Conjunto e próxima dependência" do checkpoint. Passo 1, 2 e 3 são os de `DECISOES-DELEGADAS.md` §5.

| ID (origem) | Estado no checkpoint | Onde está nos passos 1 a 3 |
|---|---|---|
| BEN: correção do S2 de origem por lote, 6090699184 (checkpoint) | S2 corrigido no runtime `1440889` (pacote `f6cb4f4`). Codex 4/4 e 163/163, Gemini 3/3. Parecer 6091321884 favorável ao delta, sem aceite global. Envelope documental pedido; 6091432263 o dá por atendido | Passo 1, item 0 |
| BEN1, restante da frente do Beneficiamento (checkpoint) | Permanece | Passo 1, item 0 cobre só a correção. **Fora dos passos: divergência explícita** para o restante da BEN-1 |
| DOM: B-R8 e COLH-C01 (checkpoint) | Pacote `7386172`, Codex 53/53. S3 em `processo_os.py` 864–867; depois, parecer focal favorável sobre `c764de9` (6091432263), sem aceite global. A reaplicação sem O.S. executável e a ligação `x.ben` dependem da integração do BEN. Vermelhos de base (PEND-OS-01, Estoque etapa 4) preservados | Passo 1, itens 0 (revisão) e 3 (junção); passo 2 (OPE-09) |
| COM: Comercial e logística (checkpoint) | Permanece. Ordem coordenada: BEN → DOM → COM → PCM | Passo 1, item 7 (sp-com); passo 2. **Divergência de ordem:** o passo 1 põe a sp-com depois da sp-pcm (item 5). Vale a ordem coordenada do checkpoint (FOCO v2: "preservar a ordem por dependências já coordenada") |
| PCM: `ba03515`, PCM-1a a 1c e simplificação (checkpoint) | Permanece. O S1 da segunda falha de freio em `ba03515` exige revisão | Passo 1, item 5, depois da revisão; passo 2 (manutenção). PCM-1b: passo 2, Suprimentos. **PCM-1c: fora dos passos, divergência explícita** |
| SAF: lote SAF-C01b e SAF-C02 (checkpoint) | Isolados e em testes, aguardando pacote recuperável. O pacote saiu depois em `7d38e5d` (6091433483) | Passo 1, item 1; passo 2 |
| NAV1 `a7023ca` e NAV 6080540795 (checkpoint) | SAF → NAV1. NAV é norma, com a aplicação nas telas ainda aberta | Passo 1, item 8 (sp-nav); passo 2 (PLA-01, PLA-04) |
| NAV2 (checkpoint) | Permanece | **Fora dos passos: divergência explícita** |
| TF, Cadastros e Irrigação: restante das TABELAS-FOCO (checkpoint) | Permanece | Passo 1, item 8 (sp-tabr) |
| CTL4 (checkpoint) | Permanece | Passo 1, item 2; passo 2 (OPE-10) |
| CTL5 (checkpoint) | Permanece | Passo 1, item 7; passo 2 (Outorga e Agrofit) |
| SUP: SUP-1, 2a, 2b e SUP-3 (checkpoint) | Permanece | Passo 1, item 4; passo 2 (SUP-3 como "do pedido ao recebimento") |
| SOLO (checkpoint) | Permanece | Passo 1, item 7; passo 2 |
| Configurações (checkpoint) | Permanece | Passo 1, item 6; passo 2 |
| CONTROLE-02 (checkpoint) | Permanece | Passo 3.2 |
| RN-031, versão de referência do plano (checkpoint) | Permanece | Passo 3.2, pelo CONTROLE-02 (`docs/controle-01/PLANO.md:421`). Não está nomeada no passo: entra pelo ID |
| PCP: PCP-ALOC-DESEMPENHO-20261003, 5973928269 (checkpoint e FOCO v2) | Permanece | **Fora dos passos: divergência explícita** |
| D7: fila dos contratos de 03/10 (checkpoint) | Permanece, com os "nove contratos 03/10" | Desdobrada nas sete linhas seguintes, pela fila D7 do `RETOMADA-NUVEM.md` (05/10). A composição exata dos nove blocos não foi relida |
| CAT: CAT-ATV `e47021d5` (FOCO v2; D7) | Permanece. Nenhum commit com esse nome na branch | **Fora dos passos: divergência explícita.** A 3.4 cobre só três ligações de cadastro |
| REND-config 15–18, D4 e ALOC `058eb147` (D7) | Permanece. Nenhum commit com esse nome na branch | **Fora dos passos: divergência explícita** |
| MAPA: monitoramento agrícola, MAPA-VISOES `f46b2e19` e MAPA-ICONES `abc41b07` (FOCO v2; D7) | Permanece. Em 05/10, MAPA-ICONES não estava aplicado e o patch não se aplicava mais à base | **Fora dos passos: divergência explícita.** O passo 2 só traz a barra do Mapa (PLA-01) e, no design, DS07, DS10 e DS12 |
| SUP v2 `e643eec7` (FOCO v2; D7) | Permanece | Passo 1, item 4 (sp-sup). A aderência da sp-sup ao SUP v2 não foi conferida: **divergência a conferir** |
| ORC: ORC-CUSTOS `7915f874` (FOCO v2; D7) | Permanece. Nenhum commit com esse nome na branch | **Fora dos passos: divergência explícita.** A OPE-14 remete o custo mensal ao Orçamento sem passo |
| SOLO-MAPA-TV `0b10392f` / `8c83b04e` (FOCO v2; D7) | Permanece | Passo 1, item 7 (sp-solo), com aderência ao contrato **a conferir** |
| VEN: VEN v2 `25d0882a` / `df64ef85` (FOCO v2; D7) | Permanece | Passo 1, item 7 (sp-com), com aderência ao VEN v2 **a conferir** |
| REND: V44-REND, multiconjuntos (FOCO v2) | Não aparece no bloco vigente; o histórico está no cabeçalho arquivado, não lido. Na branch: merges `e7bf13e` e `17bdf5d` (git log) | Fora dos passos, como frente já integrada. **Estado de aceite a conferir** no cabeçalho arquivado |
| AÇÃO: UX-ACAO-UNICA v2 e padrão de comandos v3.1 (FOCO v2) | Igual à REND. Na branch: `e91a7f4` e `3d8b3e4` (git log). A aplicação do padrão v3.1 nas demais telas era pendência em 05/10 | Fora dos passos. **Estado de aceite e aplicação do v3.1 a conferir** |
| DS (sp-ds) e padrões SEL-02, BOT-03 e BOT-07 (PR #50, `5831eb3`) (checkpoint) | DS e CADUX permanecem. Os padrões são norma, com a aplicação nas telas ainda aberta | Passo 1, item 8; passo 2 (Design). A aplicação dos padrões a **todas** as telas não tem passo próprio: **divergência explícita** |
| CADUX: cadastros com seleção que abre detalhe (checkpoint) | Permanece | Passo 1, item 8, por último; passo 2 (AGR-09) |
| Cadastros (recibo 6091443216) | Pela TF e pela CADUX acima | Passo 1, item 8; PRC-03; passo 3.4 |
| Ficha do pivô e capacidade (checkpoint) | Permanece | Parcial: passo 2, Outorga e Agrofit (IRR-03 e IRR-04). A ficha do pivô no detalhe do equipamento: **fora dos passos, divergência explícita** |
| Agrofit, praga-alvo (checkpoint) | Permanece | Parcial: passo 2 (AGR-07 confere o alvo). As colunas de praga-alvo na consulta Agrofit: **fora dos passos, divergência explícita** |
| Hiperclareza (recibo 6091443216) | Pedido direto do proprietário ao Codex, preservado no recibo 6091898499 (PR #51), sem horário: "Se alguma tela não tiver hiper foco e hiper clareza ao usuário melhore com claude." e "sempre tem que estar hiper claro o que fazer, de onde veio, para onde vai no fluxo de processos. com ações únicas e não redundantes para cada coisa no sistema." | **Fora dos passos.** Encaixa em NAV, DS e UX existentes, sem fase nem portão novos; verificável por tela: origem e contexto, estado, ação primária, consequência e destino, recuperação, com rascunho, filtros e foco preservados |
| Achados 5974392800 e precisão dose × área (FOCO v2) | Não aparece no bloco vigente. Pelo `RETOMADA-NUVEM.md`, a SINT-C03 foi corrigida no protótipo | Fora dos passos do protótipo. No software real, regra única em decimal no domínio (ENG-011 e ENG-013), como pendência da transferência. A PLA-DS13 trata só da exibição |
| QUALIDADE-ARTEFATO v2 (5974025581): jornada completa das três IAs (FOCO v2) | Direção preservada | Não é passo: é a condição de saída do conjunto (PRC-06) |
| Software real: C2 `4b7f2f07`, PR34 `a2ffe24`, PR35 `7251ff5`, F3, F2, Gitleaks, CI e HML (FOCO v2) | C2 e PRs #32 a #35 preservados para a transição | Fora dos passos por definição, porque não é protótipo. A PRC-06 os preserva |
| Mandatos da v2: publicação incremental operável e revisada; protótipo acessível para comparação; conjunto concluído e auditado antes da transferência | V54 é a última publicação relatada, sem v55 comprovada. Publicação parcial não dispara auditoria nem PRD | Não são passos: são regras transversais (PRC-01 e PRC-06) |

## Itens dos passos que o checkpoint ainda não mostra

Vêm do parecer de 09/10 e das decisões delegadas. Não conflitam com o FOCO v2, mas o checkpoint ainda não os registra (quem mantém o checkpoint é o Codex):
- frentes novas 3.1 Aplicação segura e legal, 3.3 Irrigação medida e 3.4 Cadastro que alimenta os processos;
- "Restaurar dados iniciais" (GES-3), "Entrar como" (GES-12), aviso de demonstração nos cadastros (PRC-03) e texto de ajuda do custo da terra (SUP-12);
- os encaixes do passo 2.

## Resumo

- **Fora dos passos (divergência explícita):** restante da BEN-1, PCM-1c, NAV2, PCP-ALOC, CAT-ATV, REND-config com D4 e ALOC, MAPA (monitoramento, visões e ícones), ORC-CUSTOS, aplicação dos padrões do design system em todas as telas, ficha do pivô no detalhe do equipamento, colunas de praga-alvo e hiperclareza.
- **A conferir:** a aderência da sp-sup ao SUP v2, da sp-solo ao SOLO-MAPA-TV e da sp-com ao VEN v2; o estado de aceite da REND e da AÇÃO.
- **Ordem:** "COM antes da PCM" (cabeçalho das 00:00 UTC) é estado antigo. Vigente pelos recibos do Codex de 10/10 (6091515434, 6091532182, 6091571327, 6091898499): composição SAF → DOM → PCM sobre o BEN corrigido, depois a NAV-1, e a COM depois da composição.
- Nenhum desses IDs sai do conjunto vigente: todos continuam como requisito, com o estado do checkpoint, até a conclusão e a auditoria do conjunto (PRC-06).
