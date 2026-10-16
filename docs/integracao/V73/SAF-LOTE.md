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

PREENCHER COM A MEDIÇÃO

## Testes

PREENCHER

## Fotos (conferidas)

PREENCHER
