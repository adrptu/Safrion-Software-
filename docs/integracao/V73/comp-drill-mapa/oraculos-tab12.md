# Oráculos obsoletos com a TAB-12 (drill recolhido por padrão)

```text
ID / resultado útil / persona: ORACULOS-TAB12 / ds_test, acao_unica_test e ds_1610_test voltam a medir o que mediam, depois de abrir o grupo como a pessoa faria / quem planeja a safra e quem lê a O.S. em Cartões
Requisitos do PRD e fora do escopo: TAB-12 (docs/design-system/padroes-1610.md; proprietário, 17/10/2026) e AGENTS.md §3.6 (corrigir oráculo não é afrouxar); fora: código de produto
Autor / revisor / integrador: Claude (subagente) / Codex / Claude
Base (commit ou hashes) / arquivos sob responsabilidade: e3c1d572 (intdrill) / ds_test.py, acao_unica_test.py, ds_1610_test.py
Aceite e comando de verificação: os 3 testes verdes no _render de e3c1d572; contraprova reprova onde o defeito existe (abaixo)
Estado / impedimento / próximo passo: 6 oráculos adaptados; acao_unica item 7 vermelho por defeito do produto (abaixo), fica para a frente DRILL
```

## O que mudou em cada teste (17/10/2026)

O critério e o limite de cada verificação não mudaram. A única mudança é abrir o grupo antes de medir, pela seta ou por "Expandir tudo", como a pessoa faria.

| Teste · item | Sem expansão (e3c1d572) | Com expansão (e3c1d572) | Base 0ec3a34, sem DRILL |
|---|---|---|---|
| ds_test B5 (hover da linha-filha T1, CD-01) | linha T1 fora da tela (o teste quebrava em `getComputedStyle(null)`) | seta da Santa Rita aberta: T1 à vista, hover `rgb(242, 248, 244)` | T1 à vista, hover `rgb(242, 248, 244)` |
| acao_unica 2b (tabela da etapa 2 ≥ 300 px) | 133 px, 3 linhas (só a faixa) | "Expandir tudo": 423 px, 21 linhas, área 75 px, folga 0, sem rolagem dupla | 423 px, 20 linhas, área 75, folga 0 |
| acao_unica 3 ("Planejar ›" do T3, S27SF) | linha T3 fora da tela | 1 faixa aberta: T3 à vista | T3 à vista |
| acao_unica 4 (linhas iguais antes e depois do avanço, mínimo 8) | 1 linha (a faixa) | "Expandir tudo" antes de cada leitura: 19 linhas | 14 linhas (18 com tudo aberto) |
| acao_unica 5 (safra nova: T1, T7 e C1) | só "Santa Rita" e "Total" | faixa aberta: T1 a C1; T1 "Livre · 152 ha · 21/02/2027" | T1 a C1; T1 com os mesmos valores |
| ds_1610 C1 e C3 (O.S. em Cartões por talhão) | 0 cartões, 14 grupos recolhidos | "Expandir tudo": 16 cartões, coluna vazia de 7 px, 16 com selo (1440 e 390) | 16 cartões, 7 px, 16 com selo |

Os itens 4 e 5 do `acao_unica_test.py` não estavam na lista dos 4 vermelhos porque o teste parava no item 3. Ao rodar até o fim, os dois falharam pelo mesmo motivo e foram adaptados pela mesma regra, com a função `abre_drill`.

## Resultados (executado)

Comando, a partir de `tools/prototipo/v37/gen37`: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=<render> python3 -B <teste>.py`

| Render | Teste | Resultado |
|---|---|---|
| e3c1d572 | ds_test.py | `RESULTADO: OK 72/72` |
| e3c1d572 | ds_1610_test.py | `16 ok · 0 falhas` |
| e3c1d572 | acao_unica_test.py (modo saf) | `9 ok · 1 falhas`: item 7 (defeito abaixo) |
| 0ec3a34 (base) | ds_test.py, só a parte B (`DS_PARTES=B DS_RENDER=…`) | `OK 8/8` (B5 e B6 iguais) |
| 0ec3a34 (base) | acao_unica_test.py | `10 ok · 0 falhas` |
| 5bb8f5e (contraprova) | ds_1610_test.py | `9 ok · 7 falhas` |

**Contraprova C3.** O render de 5bb8f5e foi montado num worktree temporário com `build.py` e `montar_render.py`; o worktree foi removido no fim. Lá, C3 reprova: coluna vazia de 43 px a 1440 e de 51 px a 390, e 0 de 11 cartões com selo a 390. É o mesmo defeito registrado na DS-MODULOS-2. O C1 agrupado também reprova: tem cabeçalho de colunas, 1 cartão por fileira e 0 selos.

Na base 0ec3a34, os grupos já nascem abertos e a expansão não muda nada. Lá, o ds_test (parte B) e o acao_unica_test adaptados passam inteiros. A sonda de antes e depois, a mesma da tabela acima, dá para C1 e C3 a mesma medida da candidata. Isso mostra que abrir o grupo não altera o que se mede. O ds_1610_test inteiro não foi rodado nessa base.

## Achado: defeito do produto, não oráculo (acao_unica item 7)

O item 7 faz "Corrigir cultivos" na revisão (S2627, etapa 4) e espera voltar à etapa 2 com o foco no 1º cultivo sem plano (T4).

- **Em e3c1d572:** a faixa da Santa Rita continua recolhida, a linha do T4 nem é montada e o foco cai no título "Talhões e cultivos" (H3). Isso acontece com e sem a busca "o".
- **Na base 0ec3a34:** o foco vai para a linha do T4 (`c4`).

A TAB-12 diz que "o endereço ou a ação que leva a um registro abre o caminho dele". "Corrigir cultivos" é uma ação desse tipo e não abre o caminho. Por isso o item não foi adaptado: abrir a faixa depois não devolve o foco, e aceitar o foco no título seria afrouxar o teste.

- **Severidade:** S3. A nota lista T4, T3, P1 e P2, e "Aplicar plano em 4 cultivos" continua funcionando.
- **Correção sugerida, na frente DRILL:** "Corrigir cultivos" abre o caminho até o 1º cultivo sem plano (`g2caminho`) antes de pôr o foco nele.
