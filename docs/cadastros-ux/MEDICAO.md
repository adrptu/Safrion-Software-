# CADUX · Medição das tarefas antes e depois (09/10/2026)

Mesma contagem nas duas pontas: o item do menu conta 1 clique; escolher numa lista conta 1; digitar conta o campo e os caracteres, sem clique. 1440 × 900 com mouse; 390 × 844 com toque. Tudo **executado** no navegador headless (Chrome por CDP), com dados sintéticos.

- **Antes** (base `4d03d57`): tarefas 1 a 7 em [antes/tarefas.json](antes/tarefas.json) (INVENTARIO §4); tarefas 8 a 11 em [antes/tarefas_p0.json](antes/tarefas_p0.json), medidas agora na mesma base (o P0 que faltava).
- **Depois** (branch `claude/v44-cadux`): `cadux_tarefas_test.py`, 26/26, grava [depois/tarefas.json](depois/tarefas.json) e falha se uma tarefa passar do alvo da ESPECIFICACAO §5.

| # | Tarefa | Antes: cliques · caracteres | Alvo (§5) | Depois 1440 | Depois 390 | O que mudou além do número |
|---|---|---|---|---|---|---|
| 1 | Talhões da Santa Rita e o T2 | 3 · 0 pela aba Talhões, passando pelo formulário; 7 pelo cartão da fazenda (o caminho intuitivo) | 3 · 0 | **3 · 0** | **3 · 0** | Os talhões aparecem no 2º clique, na mesma tela; o T2 abre em consulta |
| 2 | Cadastrar o B2 (80 ha) na Boa Vista | 4 · 4, com a fazenda errada (um dos cliques é trocá-la); 5 pelo cartão | 4 · 4 | **4 · 4** | **4 · 4** | A fazenda vem do mestre; nenhum clique corrige padrão |
| 3 | Trator 02: contador e conjuntos | 3 (2 + 1 rolagem no painel) | 2 (390: 3) | **2 · 0** | **3 · 0** | Contador e conjuntos acima da dobra, sem rolar |
| 4a | Equipe e papel do Marcos | 1 (1440); o roteiro gravado deu 10 | 1 (390: 3) | **1 · 0** | **3 · 0** | — |
| 4b | Quem mais está na equipe Campo 1 | 5 (1440, probe3) | 2 | **2 · 0** | **2 · 0** | Antes, marcar a equipe no filtro mostrava as outras pessoas |
| 5 | Fungicida: registro, unidade, embalagem e locais | 2 · 9; o registro não existia | 3 · 0 | **3 · 0** | **3 · 0** | Sem digitar; o registro aparece como lacuna (L01) |
| 6 | O que a Agro Norte fornece | 4 (2 pelo atalho) | 2 (390: 3) | **2 · 0** | **3 · 0** | — |
| 7 | Cultivar 58 W e o rendimento da pulverização | 5, em 2 painéis sem ligação | 3 | **3 · 0** | **3 · 0** | Cultivar e rendimento no mesmo painel |
| 8 | Talhão seguido na mesma fazenda (do 2º em diante) | 3 + nome e área; a fazenda vem Santa Rita e precisa trocar | 2 | **2** | **2** | "+ Criar outro talhão na Boa Vista" herda a fazenda |
| 9 | PV07 da Lagoa Grande pela busca (390) | 2 · 4, e abre o formulário de edição | 2 · 4 | — | **2 · 4** | Abre em consulta |
| 9m | PV07 pelo mapa (390) | sem caminho: o CD-01 da base não tem mapa da Lagoa Grande | 5 | — | **4 · 0** | O pivô abre no 1º toque (alvo de 24 px ou mais) |
| 10 | Fungicida novo (L, galão de 5 L, Almox. defensivos) | 6 · 23, mas grava em **Fertilizantes** (grupo, unidade kg e embalagem Saco vêm preenchidos sem aviso); certo, são 7 | a medir | **7 · 23** | **7 · 23** | Sem padrão escondido: grupo herdado do mestre; unidade, embalagem e local vazios (R14) |
| 11 | Quem fornece Tebuconazol 200 EC | 1 · 11, sem resultado (a busca não acha) | 2 · 11 | **1 · 11** | **2 · 11** | A busca acha o grupo do insumo e os fornecedores |

**Leitura.** Nenhuma tarefa passou do alvo. Onde o número ficou igual (2, 9 pela busca, 10), o ganho é de erro evitado: a fazenda e o grupo vêm certos, nada vem preenchido escondido, e o registro abre em consulta, não em edição. As tarefas 8, 9m e 11 não tinham caminho, ou tinham um caminho errado, na base.

**Fora da conta.** A tarefa do mecânico (achar a máquina pelo número de série) não é medível: o ativo não tem série nem código patrimonial (L07, ESPECIFICACAO §8). A tarefa 9 é do agrônomo a 390 e não foi medida a 1440.
