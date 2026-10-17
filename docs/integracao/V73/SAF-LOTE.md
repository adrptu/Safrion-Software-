# SAF-LOTE · "Editar talhões" da fazenda numa grade só (EDL-01) e entrada rápida (INP)

> Proprietário, 16/10/2026 (capturas: Planejar safra › "Defina cultivos e planos", grade agrupada por fazenda, e o painel "Dividir T1 em parcelas"):
> "coloque um botao para poder editar de uma vez todos talhoes de uma fazenda numa tela só. como no outro anexo. todos inputs do usuário no sistema devem ser mais rápido e fácil."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: SAF-LOTE (EDL-01, INP-01 a INP-11) / planejar e corrigir todos os talhões de uma fazenda numa grade só, com menos cliques e digitação / quem planeja a safra (gerente agrícola, agrônomo)
Requisitos do PRD e fora do escopo: AGENTS §3.3 e §4; PRD cap. 74; regras do Planejar safra (SAF-C01, SAF-C02, R-14, R-15, R-22, R-24, D-U01). Fora: gravar o Planejar safra no navegador (ver Decisões), trava da O.S. no painel do cultivo e no "Aplicar plano" (próxima onda), as outras telas do inventário (ENTRADA-RAPIDA.md)
Autor / revisor / integrador: Claude / Codex (regime leve do protótipo, §3.5) / integrador da composição
Base (commit ou hashes) / arquivos sob responsabilidade: c9ffa08 / safra_lote.js, areas/saf_lote.py, safra.js (dvCampos, dvConferir e dvAplicar extraídos do dvSave; faixa da fazenda; ganchos), areas/processo_safra.py (inclusão), g2lib.js (g2inp), saf_lote_test.py, saf_lote_unit*, saf_lote_medida.py, entrada_inventario.py e estes documentos
Aceite e comando de verificação: saf_lote_test.py (1440 e 390 px), saf_lote_unit_test.py, saf_lote_medida.py e a regressão listada em "Testes"
Estado / impedimento / próximo passo: executado na branch claude/v44-v73-saf-lote (commits locais, sem envio); próximo: revisão do Codex e as ondas do ENTRADA-RAPIDA.md
```

## O que a pessoa vê e como usa

- **Onde abrir:**
  - safra de uma fazenda: "Editar talhões…" no título do bloco "Talhões e cultivos", ao lado de "Planejar talhões livres…";
  - safra de várias fazendas: "Editar talhões ›" na faixa de cada fazenda (ex.: "Santa Rita · 1.165 ha · 8 de 8 talhões planejados"), também no modo Cartões; no celular, também no ⋯ da faixa.
- **O painel "Editar talhões da Santa Rita"** tem o mesmo desenho do Dividir:
  - resumo: área, área planejada, área livre, "x de y planejados" e um selo ("Tudo salvo", "N alterações não salvas" ou "A corrigir");
  - uma linha por talhão; as parcelas ficam recuadas embaixo do título do talhão;
  - colunas: Talhão ou parcela, Área (ha), Cultura, Variedade, Plantio, Meta, Unidade, Plano agronômico e Situação.
- **Para planejar ou corrigir rápido:**
  - digitar direto: no computador, o foco já abre na 1ª célula editável;
  - Tab anda nas colunas; Enter ou ↓ desce na mesma coluna; ↑ sobe; Esc fecha (com alteração, pergunta antes);
  - marcar linhas (ou "todas") e preencher a faixa "Aplicar aos marcados" uma vez;
  - colar um bloco do Excel ou do Google Planilhas a partir de uma célula;
  - "Salvar alterações (N)" grava tudo de uma vez; as células alteradas ficam com borda âmbar até salvar.
- **Para dividir um talhão em parcelas:** "Dividir T1" na linha abre o painel Dividir de sempre. O Editar talhões não refaz a divisão.

## Regras aplicadas (uma fonte só, ENG-011)

| Regra | Como vale no Editar talhões | Fonte |
|---|---|---|
| Campos obrigatórios (cultura, variedade, plantio, meta ≥ 0) e plano da mesma cultura | Recusa no Salvar, na célula, com a mensagem do Dividir | `dvCampos` (extraído do `dvSave`) |
| Talhão inteiro: plano da cultura, área, ocupação (R-14 trava, R-15 pendência) | O mesmo conferidor do painel do cultivo | `cultCheck` |
| Talhão dividido: soma das parcelas ≤ capacidade (SAF-C01), nomes, ocupação das outras safras | A mesma conferência do Dividir; a área livre planejada junto entra na soma | `dvConferir` (extraído do `dvSave`) |
| Talhão livre: plantio mínimo, parcela sugerida, área livre | O mesmo caminho do "Planejar ›" | `cultCheck` (novo), `pltCultivo`, `sugerirParcela`, `pltPmin` |
| Meta na unidade escolhida (D-U01, R-U06) | A unidade fica ao lado, nunca se escolhe na linha; salvar sem mudar o texto não regrava | `metaRascunho`, `metaGravar`, `metaUnTela` |
| Trocar o plano descarta os ajustes de dose do cultivo | Igual ao painel e ao Dividir; o aviso diz quantos | `adjOf` |
| Só os cultivos desta safra (R-22) | O painel é por sub-safra (fazenda) | `cultsDe` |

**O que fica travado, com o motivo:**

| Situação | O que trava | Motivo (o dano que evita) |
|---|---|---|
| O.S. **Liberada** ou **Em execução** nesta safra no talhão ou na parcela (ex.: T2 com a OS-0421) | Cultura, variedade e plano. Plantio e meta seguem editáveis | A ordem saiu com essa receita. Mudar o plano deixaria a ordem em campo diferente do planejado (resultado técnico). A célula diz a O.S. e o link "OS-0421 ›" abre a ordem |
| Ciclo perene vinculado (R-24) | Cultura, variedade, plantio e área (plano e meta editáveis) | Vêm do ciclo |
| Perene de outra safra ocupando o talhão (Safrinha: T7 mamão e C1 café; Lagoa Grande: os 23 pivôs) | A linha toda ("Perene · só leitura"), com quem ocupa | Não há área para planejar nesta safra |
| Área do talhão inteiro | Só leitura (vem do cadastro CD-01) | Campo calculável não se digita (INP-02); para plantar parte, Dividir |
| Área livre de um talhão (linha livre) | Só leitura (calculada pela ocupação) | Idem |

- **Gravação:**
  - atômica por fazenda: qualquer recusa não grava nada e mantém o rascunho;
  - chave do comando gerada ao abrir: o duplo clique não grava duas vezes;
  - conflito detectado: se cultivos, marcas de "sem plantio" ou a fase das O.S. desta safra mudaram depois de abrir (ex.: outra aba liberou uma O.S.), o Salvar recusa com o motivo;
  - falha no meio (exceção) não grava nada e mantém o rascunho;
  - plano operacional, recursos e demanda são recalculados pela mesma conta, porque é o mesmo estado da tela.

## Decisões tomadas nesta frente (para revisão)

1. **O Planejar safra continua sem gravar no navegador.**
   - Hoje nenhum caminho do Planejar safra grava os cultivos no `localStorage`: painel do cultivo, Dividir e Planejar talhões livres. Recarregar a página volta à semente, e os testes contam com isso (`saf_nav_lib.py`: "a página recarrega e o estado volta ao inicial").
   - Por isso "recarregar preserva" e "falha de armazenamento (setItem lançando)" não se aplicam a esta frente.
   - Em lugar do teste de armazenamento, executei a falha no meio da gravação e o conflito com outra aba (o cenário das O.S. é compartilhado no navegador).
   - Gravar o Planejar safra no navegador é mudança da tela inteira, com outro contrato de teste. Fica para decisão.
2. **A trava da O.S. está só no Editar talhões.**
   - No código de hoje, o painel do cultivo e o "Aplicar plano em N cultivos" **não** travam cultura, variedade nem plano quando há O.S. liberada ou em execução.
   - O pedido mandava travar no lote. Ficou numa função só (`slOsTravas`), pronta para o painel e o Aplicar plano.
   - Levar a trava para lá muda testes existentes (painel do cultivo em T1, T2 e T4). É a próxima onda; até lá, o painel do cultivo continua permitindo a troca.
3. **Lugar da ação.** Com uma fazenda, o "Editar talhões…" fica no título do bloco, ao lado do "Planejar talhões livres…", a ação irmã, na mesma forma. Com várias fazendas, fica só na faixa de cada fazenda, que continua à vista quando se filtra uma: sem cópia da ação.
4. **↓ na Variedade desce de linha**, como nas outras colunas. A sugestão do cadastro (lista do navegador) se escolhe com o mouse ou digitando.
5. **Colar um valor só** em lista, data, número ou célula travada passa pela conferência, com o resumo. Texto solto na Variedade cola como sempre.
6. **Sugestão de contexto ao trocar a cultura** (INP-10):
   - a variedade e o plano da cultura anterior saem;
   - vazios, recebem a variedade e o plano mais usados nesta safra;
   - na linha livre, o plantio recebe o primeiro dia possível, calculado;
   - a meta nunca é sugerida;
   - tudo que muda fica destacado como alteração.

## Números: cliques e digitação (AGENTS §3.3)

**Executado:** `saf_lote_medida.py`, no navegador a 1440 px, sobre o render da f2f74f8 (árvore limpa). Ele usa cliques reais do mouse (CDP) e conta as teclas.

**Cenário:**
- Safra 2027/28 nova da Santa Rita.
- Planejar os 6 talhões livres (T1, T2, T3, T4, P1 e P2) com Soja · 58 W · Soja alta tecnologia · plantio 15/10/2027 e a meta de cada um (64, 62, 63, 60, 66 e 65 sc/ha).
- T7 e C1 seguem com o perene de outra safra.
- Criar a safra fica fora da conta, porque é igual nos três caminhos.

**Como conta:**
- abrir a lista e escolher a opção são 2 cliques;
- escolher o campo para digitar é 1 clique;
- cada caractere, Enter, Esc ou Ctrl+V é 1 tecla.

| Caminho | Cliques | Teclas | Cultivos gravados |
|---|---:|---:|---|
| **A · antes:** "Planejar ›" em cada talhão, formulário e Salvar | **29** | **64** | 6 |
| **B · depois:** "Editar talhões…", marcar todas, "Aplicar aos marcados" (cultura, variedade, plantio e plano) e metas na coluna com Enter | **11** | **30** | 6 |
| **C · depois:** "Editar talhões…", colar o bloco da planilha (6 × 5) na 1ª cultura, Salvar | **3** | **2** | 6 |

- **Conferência:** os três caminhos gravam os mesmos 6 cultivos (talhão, cultura, variedade, plano, plantio, meta e área), e o teste confere isso.
- **No caminho C,** o bloco já vem pronto da planilha da fazenda. A digitação dele fica fora da conta.
- **Ganho:** B corta 62 % dos cliques e 53 % das teclas; C corta 90 % dos cliques.
- **Para comparar:** quando todos os talhões levam os mesmos valores, inclusive a meta, o "Planejar talhões livres…" que já existia faz o mesmo que o caminho B. O ganho novo está em:
  - valores diferentes por talhão;
  - corrigir o que já está planejado;
  - colar da planilha.
- **Bruto:** `saf-lote/saf_lote_medida.py.log`, nesta pasta.

## Testes

**Candidata:** f2f74f8 (esta frente com a composição `origin/claude/v44-v69-mapa` 47ccc1d, que contém a 05947ad), render montado de árvore limpa.
- **Comando:** `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B <teste>`, um Chrome por vez.
- **Base:** c9ffa08 (render da V73).
- **Brutos:** `saf-lote/`, nesta pasta.

**Novos (executados):**

| Teste | Resultado | Contraprova na base |
|---|---|---|
| `saf_lote_unit_test.py` (node: colar TSV, datas, número pt-BR, o que cada célula aceita, aplicar aos marcados, contador) | 47/47 | sem `safra_lote.js`: não monta |
| `saf_lote_test.py` (1440 e 390 px: A abrir, B planilha, C aplicar, D colar, E recusas, F salvar, G Esc, conflito, falha e Dividir, H celular, I INP no motor) | 45/45 | reprova em A1 (sem o botão) |
| `saf_lote_medida.py` (cliques e teclas, três caminhos) | OK: mesmos 6 cultivos; 29/64 → 11/30 → 3/2 | — |

**Regressão (executada na f2f74f8):**

| Teste | Resultado | Observação |
|---|---|---|
| `saf_c01_test.py` | 68/68 | cobre o Dividir depois da extração do `dvConferir` |
| `saf_revisao_test.py` | 40/42 | as 2 falhas são S3.1 (g_cap); classificação abaixo |
| `ocupacao_test.py` | 65/65 | |
| `saf_capacidade_simetrica_test.py` | 38/38 | |
| `saf_cmp_continuidade_test.py` | 31/31 | |
| `saf_contexto_test.py` | 10/10 | |
| `saf_fazendas_test.py` | 14/14 | |
| `saf_multi_fazenda_test.py` | 23/23 | |
| `saf_impedimentos_test.py` | 5/5 | |
| `saf_operacoes_test.py` | 87/87 | |
| `saf_tab_test.py` | 14/14 | |
| `saf_totais_test.py` | 14/14 | |
| `tabelas_saf_test.py` | 24/24 | |
| `acao_unica_test.py` (família SAF, o padrão do teste) | 10/10 | |
| `ds_1610_test.py` | 14/14 | |
| `ds_modulos.py --catraca` | catraca ok | |
| `tab_drill_cab_test.py` | 6/6 | |
| `cartoes_test.py` | 70/70 | |
| `paginas_scan_test.py` | 5/5 (148 páginas) | |
| `tabelas_cad_test.py` | 206/206 | |
| `cadastros_padrao_test.py` | 44/44 | |
| `ds_1510_test.py` | 17/17 | |
| `saf_revisao_test.py` na **base** (render de c9ffa08) | 40/42 | as mesmas 2 falhas S3.1 (g_cap da S27SF e da safra nova): já existiam antes desta frente (`base_saf_revisao_test.py.log`) |

**Sem navegador (executados):**

| Teste | Resultado |
|---|---|
| `pa_regras_test.py` | 18/18; carrega o `g2lib` no node, e o `g2inp` fica fora sem `document` |
| `cen_grava_test.py` | 10/10 |
| `ds_unit_test.py` | 31/31 |
| `capacidade_unit.py` | 101 OK |
| `ds_inventario.py --catraca` | catraca ok (o painel não tem `role=table`, cartão próprio nem CSS sobre `.g2`) |

**Oráculos corrigidos no próprio teste novo, antes da entrega (sem mudar o produto):**
- B1 e B2: a linha abaixo de T3 é T4, e não P1.
- E2: a Situação lida sem repetir o texto.
- H7: o item do ⋯ se chama "Editar talhões da Lagoa Grande".
- H7: a altura do link e do ⋯ da faixa é registrada, não exigida. São peças do motor; ver Limites.

## Fotos (conferidas)

Em `tools/prototipo/v37/gen37/_probe/` (não versionadas), geradas pelo `saf_lote_test.py`:
- `saf_lote_1440_painel.png`: painel da Santa Rita depois de salvar T1-A com 150 ha. Mostra a linha "T1 · área livre 10 ha" que apareceu, as O.S. que travam com o link e a dica da grade.
- `saf_lote_390_lista.png`: celular, linhas em bloco com rótulos, travas e barra de salvar fixa.
- `saf_lote_390_aplicar.png`: celular, faixa "Aplicar aos marcados" aberta com 1 linha marcada.
- `saf_lote_390_faixa.png`: celular, faixa da Lagoa Grande com "Editar talhões ›".

**O que se viu nas fotos:**
- sem rolagem de lado;
- os campos alinhados às colunas a 1440 px;
- no celular, os rótulos em cima de cada campo.
- A data aparece como mm/dd/aaaa porque o Chrome de teste roda em inglês; no navegador em português, é dd/mm/aaaa.
- O aviso "Safra aberta" que cobre parte da tela no celular é o aviso de carga da página, que já existia.

## Limites e próximos passos

- **Recarregar e falha de armazenamento:** não se aplicam (Decisão 1). O que se executou foi a falha no meio da gravação (G4 e G5) e o conflito com outra aba (G2 e G3).
- **Trava da O.S. no painel do cultivo e no "Aplicar plano":** fica para a próxima onda (Decisão 2).
- **Alvo de toque das peças do motor na faixa da fazenda a 390 px (medido):**
  - o link "Editar talhões ›" tem 18 px, como o "Planejar talhões livres ›" ao lado;
  - o ⋯ da linha tem 32 px.
  - A correção é do motor (DS-ALVO para link de célula e ⋯ da linha) e vale para todas as tabelas. No painel, todos os alvos têm 44 px (H2).
- **Custo de desenho (medido numa sonda, fora do teste):** cada tecla na grade leva de 200 a 280 ms, porque redesenha a tela inteira, como no Dividir. Não atrapalhou a digitação nos testes. Se pesar com fazendas muito grandes, a saída é guardar o cálculo da etapa 4 enquanto o painel está aberto.
- **`docs/STATUS.md`:** não foi alterado por esta frente. A integração da composição atualiza.

## Fechamento da bateria (17/10, depois da entrega)

- O grupo B rodou inteiro na f2f74f8 (executado): `tabelas_cad` 206/206, `cadastros_padrao` 44/44 e `ds_1510` 17/17. Os brutos estão nesta pasta.
- O `saf_revisao_test.py` dá 40/42 na base e 40/42 na candidata, com as mesmas 2 falhas. Portanto não são regressão desta frente.
- Causa provável: o seletor do teste procura "Capacidade por mês ▾", e desde a TAB-09 a tela mostra "▸ Capacidade por mês". Isso é leitura de código, não verificação. A correção do seletor fica fora desta frente.
