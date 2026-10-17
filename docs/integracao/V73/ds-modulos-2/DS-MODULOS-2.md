# DS-MODULOS-2 · Padrão do Agrícola em todos os módulos, MAIS-02 e cartões compactos

> Proprietário:
> - 16/10/2026: "os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez."
> - 17/10/2026: "aplicacao do design system padrao, referencia modulo agricola ainda nao foi para demais modulos, como esta isso para o artefato?"
> - 17/10/2026, sobre Manutenção › Planos: "os 3 pontinhos no topo da tela a direita em criar plano.... é uma boa, toda tela que tiver mais ações pode ter esses 3 pontinhos nesses botões dessa região da tela."
> - 17/10/2026, com print da O.S. em Cartões agrupada por talhão: "os cartoes em ordem de serviço estao fora do padrao design system".

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: DS-MODULOS-2 (MAIS-02, VIS-07, TAB-05 no motor, CAB-1/CAB-2 fora do menu, TAB-07 tela a tela) / todo módulo com o cabeçalho, a tabela, os cartões e as ações do Agrícola / todos os usuários
Requisitos do PRD e fora do escopo: PRD cap. 74; padroes-1510, padroes-1610 e padroes-1710; fora: CA-02, GE-02det, GE-03, GE-08 (frente PAINEL-FIXO-2 do Codex) e os arquivos areas/campo.py e areas/gestao.py; corpo do mapa do IN-04 (frente MAPA-UX); padrão de expansão (x0/exp) e regra de setas (frente DRILL)
Autor / revisor / integrador: Claude / Codex / integrador da composição (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: 5bb8f5e / ui37.py, engine.py, g2lib.js, ds_modulos.py, áreas listadas abaixo e os testes adaptados
Aceite e comando de verificação: ds_modulos.py --catraca e a bateria em "Provas"
Estado / impedimento / próximo passo: ver "O que fica"
```

## O que mudou (peça comum primeiro)

| ID | Mudança | Onde | Alcance |
|---|---|---|---|
| CAB-1 | Tela fora do menu ganha o "‹ Módulo" (`volta_pilula`) pelo prefixo (`VOLTA_PREF`) e o caminho diz o mesmo módulo; ON-01 e BO-02 voltam a "Outros acessos"; a ficha impressa da OS-0424 ganha "‹ Ficha do app" | `ui37.shell37`, `ui37.VOLTA37`, `areas/os_campo.py` | 50 desvios → 1 (CA-02, frente do Codex) |
| CAB-2 | Fazenda, safra e parceiro saem do topo e vão para a faixa "Trabalhando em" (FIL-01, `CTX_LAB`) | `ui37.shell37` | 57 → 0 |
| MAIS-02 | À direita do título, só a primária e o ⋯ com as outras ações; regra medida | `engine.recolhe_cabecalho` (usa `mais` e `item_menu`), `ui37.shell37`, `ds_modulos.py`; Estrutura gerencial (`cad_produtos_estrutura.py`) | 1 → 0 |
| TAB-05 | O ⋯ da linha é o padrão do motor (`menu_linha=None` → ligado); a pergunta da linha fica à vista (`decide`) | `engine.grid`, `g2lib.g2vals`; Estoque marca as perguntas da linha com `decide` | 31 → 2 (CA-02 e GE-08, frente do Codex) |
| VIS-07 | Cartões do motor em grade de cartões compactos, sem cabeçalho de colunas, com o selo de estado no título e até 4 campos rotulados, também agrupados | `engine.CARTOES_CSS`, `engine._cartoes_html`, `g2lib.g2cdVals` | toda lista do motor em Cartões |
| TAB-07 | Cartões de resumo saem de cima da lista, tela a tela (tabela abaixo) | 11 arquivos de área | 35 → 9 (todas em arquivos da frente do Codex) |
| FIL-01 | A escolha do talhão no detalhe do cadastro vai para a faixa comum de filtros | `areas/cad_fazendas.py` | 1 → 0 |

### TAB-07 tela a tela

| Tela | O que saiu de cima da lista | Para onde foi |
|---|---|---|
| IV | Produtos em alta, Vender agora, Mês de melhor preço | colunas Tendência e Melhor mês; "Vender agora N" no filtro rápido; selo do cabeçalho |
| IC | Insumos em alta, Comprar agora, Economia esperando o mês certo | coluna Tendência; "Comprar agora N" no filtro rápido; a economia abre os indicadores entre os blocos, depois da lista |
| CF-05 | Plano, área medida, prévia, próxima cobrança | pares rótulo × valor da própria assinatura (sem número grande) |
| BO-02 | Mensalidades vigentes, organizações, faturas abertas, área cobrada | pares rótulo × valor: são os totais da plataforma pedidos no PRD §6 (área cobrada = mín(medida; contratada) não é soma de coluna) |
| ON-01 | Trial, área declarada, pendências, modo | selo do cabeçalho "Passo 3 de 6 · N pendências · trial até 18/10"; área e modo já estão em "Direitos do trial" |
| AG-01det | Pontos válidos, média válida, pontos ≥ NC, evidências | pares rótulo × valor do resultado da vistoria |
| PT-06 | — | é o painel do Portal do parceiro ("Indicadores"): os cartões são o conteúdo; o medidor passou a tratá-la como Painel |
| PL-01, PL-03, PL-04, PL-05 | safras, carga × capacidade, ordens do período, impedimentos | selo do cabeçalho com o que pede atenção; o resto está nas linhas |
| CO-01, CO-02, CO-07 | oferta, janela, saldos | selo do cabeçalho; linhas da oferta, das ordens e dos lotes |
| LO-01 a LO-04 | cargas, pátio, viagens, fretes | selo do cabeçalho; linhas |
| VE-04 | a confirmar, disputa, sem alocação, recebíveis | selo "3 a confirmar · 2 em risco · 1 disputa"; linhas |
| SU-01 | falta firme, atrasados, condicionado, valor | selo "18 itens com falta firme · 5 atrasados · R$ 428,3 mil"; o condicionado está na linha do KCl |
| SU-03 | conflito, retidos, custódia, valor | selo; coluna Custódia; valor em insumos na linha de total da coluna Valor |
| SU-05 a SU-09 | conflitos, divergências, quarentena, custódia, trânsito, ajustes | selo do cabeçalho (já dizia o que pede atenção); linhas |

<!-- RESULTADOS -->
