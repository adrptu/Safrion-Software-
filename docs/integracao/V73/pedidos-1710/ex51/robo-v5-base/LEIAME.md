# Robô v5 · medida de base na candidata atual (EX-51)

Medida **executada** por Claude em 17/10/2026, das 18:20 às 19:10 UTC, com repetição das 19:10 às 19:30. Dados sintéticos do protótipo, sem segredo.

**Candidata medida:**
- `_render` existente em `/tmp/claude-0/int90/tools/prototipo/v37/gen37/_render`, copiado sem alteração.
- Árvore `int90`, branch `comp`, HEAD `c709db66`. Esse commit só acrescenta os documentos do EX-51 sobre `1460bba9` ("Integra DS-MODULOS-2 … na composição").
- As páginas foram montadas às 17:57 UTC, 18 s depois de `1460bba9`. Não remontei a candidata e não conferi essa correspondência.
- Identificação: sha256 do conjunto (181 arquivos) `39b88342b9aa985f011dd9fabc9c5482d7a03a0c983b23fb740e8845158dd038`, um hash por arquivo em `v3.sha256`.

## Rodar de novo (um comando)

```sh
cd docs/integracao/V73/pedidos-1710/ex51/robo-v5-base
python3 -I rodar.py --render <árvore>/tools/prototipo/v37/gen37/_render --trabalho <pasta de trabalho> --entrega <pasta nova, ex.: ../robo-v5-F1>
```

- **Tempo:** cerca de 27 min nesta máquina (robô 12,5, 2ª passada 8,3, títulos 2,8 e escopo 2,4).
- **Modo do pacote:** `--modos isolado,pacote` também roda o robô como veio no pacote, com mais 20 min.
- **Requisitos:** Python 3, Chromium (padrão `/tmp/cloudchrome/chrome`, troque com `--chrome`) e cerca de 120 MB para a cópia.
- **Chrome:** antes de abrir, o script espera haver menos de 4 processos Chrome principais. No fim, encerra só os PIDs que ele mesmo iniciou: o Chrome e os servidores. O perfil temporário fica em `/dev/shm` e é apagado.
- **Saída:** a tabela v108 × agora sai no terminal e em `comparacao.json`. Com `--entrega`, a pasta recebe `resumo.json` (modo isolado), as entradas e os brutos. Os brutos vão em `tar.gz` quando passam de 5 MB.
- **Fases separadas:** use `--fases preparar,robo,leva,nav,escopo28,resumo` para escolher.
- **Pasta de entrega:** use uma pasta nova por fatia. A pasta desta base não deve ser sobrescrita.

## O que foi medido

- **Telas:** 102 páginas passaram pelo robô e 94 entram na conta do resumo, a mesma base de 94 telas da v108.
  - As 102 páginas são as 156 `.dc.html` do `_render`, menos 46 marcadas Excluir no EX-50 e menos 8 sem aplicativo.
  - As 8 sem aplicativo: MA-01 a MA-05, MA-04det e PM só redirecionam para MA; a Main é página técnica neutra.
  - Da conta do resumo saem também os hubs MOD-* e CD.
- **Por tela:** o robô abre até 3 registros, conta as referências a outros registros e os campos de cadastro, e lê o "Próximo passo".
- **Passagens:** o robô clica até 9 por tela. Em cada uma confere se o destino abre o registro, se mostra a volta à origem e se o Voltar do navegador reabre o detalhe.
- **2ª passada (`leva-check.json`):** abre o endereço de cada uma das 125 passagens que levam um registro e espera 2,6 s.
- **`escopo-28.json`:** confere se Fazenda e Safra escolhidas numa tela chegam a cada uma das 28 telas principais (detalhe em "Diferenças de método", item 6).

## Antes (v108) × agora (candidata)

| Medida | v108 (anexo) | **Agora · base** (modo isolado) | Agora · modo do pacote |
|---|---|---|---|
| IDs clicáveis | 17/55 (31 %) | **39/85 (46 %)** | 35/78 (45 %) |
| Cadastros clicáveis | 6/71 (8 %) | **6/84 (7 %)** | 6/70 (9 %) |
| Passagens que chegam no registro | 44/88 (50 %) | **85/153 (56 %)** | 61/107 (57 %) |
| (só 1ª passada) | — | 82/153 (54 %) | 56/107 (52 %) |
| Volta à origem | 16/88 (18 %) | **22/153 (14 %)** | 12/107 (11 %) |
| Voltar do navegador reabre o detalhe | 0/59 | **10/107 (9 %)** | 1/77 (1 %) |
| Escopo herdado nas 28 telas principais | 0/28 (leitura do código) | **0/28** (escopo28) | mesma medida |

Contexto:

| | v108 | Base (isolado) | Modo do pacote |
|---|---|---|---|
| Telas · detalhes · passagens | 94 · 180 · 209 | 94 · 190 · 247 | 92 · 179 · 206 |
| Passagens para outra tela · abrem no lugar · sem efeito | 152 · 43 · 14 | 233 · 11 · 3 | 155 · 46 · 5 |
| Das que levam registro: não levam · levam e o destino ignora | 23 · 21 | 35 · 33 | 27 · 19 |
| Detalhes com Próximo passo · dizem quem age | 29/180 · 9 | 32/190 · 13 | 29/179 · 11 |
| Telas principais com filtro Fazenda · Safra | 9/28 · 5/28 | 9/28 · 5/28 | 9/28 · 5/28 |

- **Repetição.** A segunda rodada do modo isolado (`repeticao/`) deu exatamente os mesmos números do resumo. Nos brutos só um hub mudou, o MOD-MAN, que fica fora da conta. A base é reproduzível nesta candidata.
- **Para o aceite do EX-51.** 43 passagens levam a telas marcadas Excluir: SU-07 e VE-06 (4 cada), PL-02, PL-05, CO-06det, GE-06det, VE-04 e SU-05det (3 cada) e outras. Três cliques ficam sem efeito: MB-08 "Ver próximo setor", PT-05det "Abrir divergência" e PT-07 "Ver assinatura e fatura".
- **Onde o Voltar já reabre o detalhe.** AG-01 (3 casos) e AG-07 (6 casos) põem o registro no endereço ao abrir o detalhe. Há também 1 caso PAGR → MB-07 em que a volta caiu em COLH#lg24 com um detalhe de mesmo título aberto. O resumo conta esse caso como reaberto; ele merece conferência.
- **Escopo.** As 9 telas com seletor não herdam a escolha: IN-04, OS, EST, COLH, AG-01, AG-02, IR-01, CARGA e PROD. As outras 19 não têm seletor.
- **Piores pares** (em `resumo.json`, chave `piores`): CF-01→OS (8), BEN→PROD (7), CD-03→MA (6), IR-01→IR-03det (6) e PCOM→VEN (5).

## Diferenças de método

1. **Modo isolado na base, no lugar dos 3 quadros numa página.**
   - **O problema.** No robô do pacote, `history.back()` de um quadro anda na história conjunta da aba e pode voltar outro quadro. A prova é `prova-historia-conjunta.py`, executada; a saída foi: antes `['?a=2','?b=2']`, depois de `A.history.back()` `['?a=2','?b=1']`, ou seja, voltou o B.
   - **O efeito no modo do pacote.** 12 telas foram medidas em outra página (por exemplo, BO-02 caiu em BO-01 e CMP em CF-01). Em 130 passagens o Voltar não moveu o quadro. Houve 46 "mesma tela", 20 "não achou" e 2 telas com erro (PROD e MB-03x-recibo).
   - **No modo isolado:** 0 telas em outra página, 0 Voltar sem efeito, 0 "não achou", 0 erros e 9 "mesma tela" (navegação interna legítima).
   - **A mudança.** No modo isolado, cada um dos 3 trabalhadores roda numa aba e numa origem (porta) próprias, com um quadro só. A única mudança no robô é o número de quadros: `[0, 1, 2]` passa a `window.__ROBO_FRAMES || 3`. Ela é aplicada em tempo de execução numa cópia (`robo-v5-isolado.html` na pasta de trabalho). A lógica de medida e de contagem não muda.
   - **Hipótese sobre a v108, não comprovada aqui.** Os números da v108 (209 passagens, 43 no lugar, Voltar 0/59) se parecem com os do modo do pacote. A v108 provavelmente sofreu o mesmo efeito.
2. **2ª passada reconstruída.**
   - O script dela não veio no pacote. Escrevi o meu com os campos que o resumo lê: `dlg` é o título do diálogo aberto; `alvoNoH1`; `url`; `alvoNoCorpo`; `tokNoCorpo` é um valor do endereço achado no texto, sem acento e com hífen virando espaço, ignorando chaves de visão como `vis`, `modo` e `passo`.
   - Ela muda pouco o resultado: 82 → 85 chegam.
   - **Ressalva.** Das 85 chegadas, 17 vêm do texto da página. Em 9 delas esse texto aparece também sem o endereço (campo `diag` do `leva-check.json`). O critério do resumo é frouxo nesse ponto.
3. **Resumo sem mudança.** `anexo-robo-v5-resumo.py` rodou como veio, com `python3 -I`, e não precisou de ajuste.
4. **`navegacao.json`.** É o h1 renderizado de cada uma das 156 páginas, lido no Chrome; sem h1, vale o `<title>`. Em IR-03det, MB-01, MB-02det, MB-06 e MB-09det o h1 é feito por modelo e mostra o registro padrão. Exemplo: IR-03det mostra "OS-0419 · Irrigação · Pivô 2".
5. **`ocultas.json`.**
   - Vem dos 123 itens da classificação do Codex, na ordem e com a decisão do anexo original (`anexo-telas-ocultas.md`). A ordem foi conferida item a item pelo nome.
   - Aplica as 8 exclusões retiradas na própria classificação: MA-01 a MA-05, MA-04det, PM e Main.
   - Resultado: 50 itens Excluir, dos quais 46 são páginas e 4 são funções.
6. **Escopo.**
   - O resumo fixa `herda: 0` e não mede essa grandeza.
   - O `escopo()` do robô testa 8 pares e deu 0/8. Mas registrou "sem seletor" em O.S. e Estoque, que têm o filtro. Provavelmente ele lê a chegada antes de a tela nova montar. Por isso o 0/8 não serve de prova.
   - Por isso acrescentei o `escopo28`:
     - a origem é a O.S.; para a própria O.S., a origem é Cargas;
     - a ação é a mesma do robô;
     - o controle é o padrão de cada tela aberta do zero;
     - o valor escolhido é diferente desse padrão (Lagoa Grande ou Boa Vista, 2026/27);
     - a navegação é pelo endereço, na mesma aba.
   - Na IN-04 a Safra só tem 2026/27 e não pôde ser testada; valeu a Fazenda.
7. **Ambiente.**
   - Chromium 141, headless.
   - Cada aba numa janela própria: no headless, as abas de trás ficam "hidden" e param o `requestAnimationFrame`. Isso foi conferido.
   - Foco emulado, temporizadores sem estrangulamento e cache de disco de 1 MB.
   - Diálogos JS: alert é aceito; confirm e prompt são cancelados. Nenhum ocorreu.
   - As fontes do Google carregam pelo proxy da sessão.

## Limitações

- **Esperas fixas do robô:** 650 ms para o diálogo e 6 s para a navegação. A carga da máquina ficou entre 10 e 12 em 4 núcleos durante a medida, e a repetição não mostrou variação. Mesmo assim, compare as fatias na mesma máquina e com o modo isolado.
- **Amostra, não inventário:** até 3 registros e até 9 passagens por tela. Os totais (85, 153 etc.) mudam quando as telas ganham ou perdem links. Compare as proporções e as listas de passagens com problema em `resumo.json`.
- **Comparação com a v108 com cautela:** o método da v108 é o do modo do pacote, com o problema do item 1, e a 2ª passada dela não está disponível.
- **Não medido aqui:** as três jornadas de referência, a igualdade de contagens entre Mapa, painéis e listas, e o teclado e leitor de tela do aceite do EX-51.

## Arquivos

| Arquivo | O que é |
|---|---|
| `rodar.py` | Comando único: prepara, sobe servidores e Chrome, roda o robô, a 2ª passada, os títulos, o escopo28 e o resumo, e entrega |
| `servidor.py` | Servidor mínimo em 127.0.0.1: `/v3/<TELA>.dc.html` e arquivos de apoio, `/robot3/screens.json`, `POST /save?name=` e o robô |
| `preparar.py` | Copia o `_render` e gera `ocultas.json`, `screens.json` e `v3.sha256` |
| `comparar.py` | Tabela v108 × agora (`comparacao.json`) |
| `prova-historia-conjunta.py` | Prova do item 1 de "Diferenças de método" |
| `resumo.json` | Resumo da base (modo isolado, com 2ª passada) |
| `resumo-isolado-1a-passada.json`, `resumo-pacote*.json` | Mesma medida sem a 2ª passada e no modo do pacote |
| `comparacao.json`, `escopo-28.json`, `preparo.json`, `execucao.json`, `execucao.log`, `robo-*.log` | Tabela, escopo, preparo, tempos e registros da execução |
| `entradas/` | `ocultas.json`, `navegacao.json`, `screens.json` |
| `brutos-isolado/`, `brutos-pacote/` | `*.v5.json`, `escopo.v5.json` e `leva-check.json` (0,4 MB no total, sem compressão). No pacote também os 2 `*.v5err.json` |
| `repeticao/` | Resumo, tabela e registro da 2ª rodada do modo isolado |
