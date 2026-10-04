# RETOMADA-NUVEM: passagem do Claude local (Mac) para a sessão do Claude na nuvem
`CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01`

**Quem é quem**
- **Adrianus** é o proprietário. Ele delegou as decisões técnicas e de produto ao Claude e ao Codex (DECISOES-DELEGADAS-20261003). Ficam com ele custo, contas e acessos, dados reais, contratos, publicação para usuários reais e aceite.
- **Claude** é o autor: protótipo e software real. A autoria delimitada do protótipo passou do Claude local para o **Claude nuvem** (despacho CORTE-REMOTO-01 / CAMADA-SINTETICA-01, 03/10).
- **Codex** coordena, lidera produto, design e UX, revisa e publica no GitHub.
- **Gemini** real faz contraprova focal, sem simulação de modelo.

**Mac e canal**
- **Correção da coordenação (03/10):** o Mac ainda **não** é só console. Coordenação/GPT e outras fontes continuam pendentes lá. Nenhum trabalho pesado novo roda no Mac.
- O canal passa a ser a **issue 1 e os PRs** do repositório privado; o canal de arquivos do Mac vira espelho.
- Leia também `docs/claude/CLAUDE-proprietario.md` (como o Adrianus quer trabalhar) e `docs/claude/skills/` (master-detail-ux, ux-essencial, tabelas-interativas, minimalismo-essencial, agro-gestao-conhecimento, dev-* etc.). Elas valem sem precisar perguntar.

## Regras que continuam valendo
- **Dado real:**
  - Nenhum dado real da Fazenda Lagoa Grande sai do Mac: CAR, coordenadas, perímetros, áreas por pivô, outorgas, cenas e imagens Sentinel.
  - **Não use os commits `c9d61266` e `d22da69` da branch `prototipo/v43`.** Eles contêm áreas reais em páginas geradas e coordenadas em testes; a remediação é do Codex.
  - Use só as branches `prototipo-limpo/*` abaixo.
- **Autoria:** uma por arquivo, ao mesmo tempo.
- **Relatórios:** em pt-BR, separando protótipo, software real e HML. Cite só número, SHA e hora que saíram de um comando seu.
- **Publicação:** protótipo testado é publicado a cada pedido do Adrianus (artefato `https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm`). Sem push em main, sem merge e sem PR próprio integrado: o Codex revisa e integra.
- **Padrão de comandos v3.1:** `tools/prototipo/v37/specs/padrao-comandos-v3-prompt.md`. Uma ação por efeito, posição e tipo de botão por função, dentro × fora do componente.
- **Decisões D1–D8** (DECISOES-DELEGADAS-20261003), com os ajustes do Codex (retorno `cc02b54f`):
  - **D1:** a sequência de conjuntos é uma "alternativa factível sugerida" com premissas, conforme PRD 44.9 e REND `7ae753dc`. Nunca é a mais rápida incondicionalmente.
  - **D2:** diesel entra em litros, com o custo contado uma vez; a demanda própria depende de quem fornece o combustível.
  - **D3:** 6,804 é guardado internamente; a tela mostra 6,80.
  - **D4:** capacidade compartilhada entre ocorrências, conforme ALOC `058eb147`.
  - **D6:** LMR sem regra oficial carregada fica bloqueado.
  - **D7:** ordem da fila (abaixo).
  - **D8:** PCM.

## Branches limpas (repositório NOVO, base sem pais)
O pacote vem de um `.git` novo. A base é um **commit raiz sem pais**, e nenhum ancestral do repositório antigo é transportado.

| Branch | Commit | O que é |
|---|---|---|
| `prototipo-limpo/base` | `e8d780de2a660bb023eb49483878c0d1b04bff0a` | base_v43m saneada, raiz sem pais; base de merge das trilhas v44 |
| `prototipo-limpo/v43` | `abc00a4b2031b1d62540091c7b8ec427aefd0ce2` + commit de passagem (este arquivo) | v43 publicada saneada, com portabilidade, mais documentos da passagem |
| `prototipo-limpo/v44-rend` | `126899e5b3227327029d5c54e87d7313e1cfff02` | trilha REND, **parcial** (S5 corrigido sem verificação; o teste de telas não rodou). Os números citados são relato: os brutos ficaram no Mac e não valem como teste desta candidata |
| `prototipo-limpo/v44-acao` | `20f25726d6318c2e249e38575e5458455a32ec16` | trilha AÇÃO + padrão v3.1, **parcial** (`impl` cortado no meio; sem verificação). Os números citados são relato, como na REND |

**Não use:**
- `prototipo/v43` (c9d61266/d22da69), que contém dado real; a remediação é do Codex;
- os commits locais d7a2411b e f7967369, que nunca foram transportados.

**Merge:** sequencial e revisado, **não octopus**. Cada trilha entra num merge próprio (CAMADA-SINTETICA, depois REND, depois AÇÃO) sobre `prototipo-limpo/v43`, com revisão do Codex antes de cada um. Não iniciar auditoria integral da v44 antes disso. A base de merge é `prototipo-limpo/base`. Conflito provável só em `areas/irrigacao.py` (faixa de etapas): vale a decisão da AÇÃO (indicador informativo) aplicada sobre o `_etp_nav` da v43.

**Origem de cada snapshot:** `MAPA-ORIGEM-SANITIZADO.json`, com a impressão sha256 das fontes de origem no Mac. A política de exclusão e redação está em `MANIFESTO-CORTE-REMOTO-01.md`.

**Software real:**
- `claude/next-16-3-6` = `a2ffe24` (pin e792 + PR34 + PR35), publicado.
- `claude/env-ui-c2-comp` = `4b7f2f07` (C2): bundle `eea16286` na pasta `fontes-claude/env-ui-c2` do Mac, a ser publicado pelo Codex.

## Como montar e testar na nuvem
```
cd tools/prototipo/v37/gen37
python3 build.py            # sai com 1 se algum módulo falhar
python3 montar_render.py    # monta _render/ com project/, support.js e os JSONs do AGROFIT
CHROME_BIN=$(which chromium || which google-chrome) python3 varredura.py   # build limpo na nuvem: "RESULTADO: 144/144 páginas sem erro" (ver tarefa 1)
python3 <teste>.py          # Chrome headless via cdp.py (CHROME_BIN)
```
Sem a camada sintética (tarefa 1), o build para em `dados_lagoa_fonte`, com uma mensagem clara.

**Executor da nuvem** (contêiner Linux como root, saída pelo proxy da sessão):
- O Chromium exige `--no-sandbox`. O `CHROME_BIN` aponta para um wrapper local, fora do repositório, que acrescenta essa opção e `--proxy-server` para o proxy oficial. O `cdp.py` não muda.
- O MapLibre vem do CDN e precisa da CA oficial do proxy na NSS do navegador: `certutil -A -n ccr-agent-proxy -t C,, -i /root/.ccr/agent-proxy-ca.crt`. A verificação TLS continua ligada.

## Reserva ativa (Claude nuvem · CAMADA-SINTETICA-01 · branch `claude/camada-sintetica-01`)
- Reservados pelo despacho: `gen37/dados_lagoa_sintetico/**`, `gen37/dados_lagoa_fonte.py`, `gen37/talmapa_test.py`, `gen37/talgeo_test.js` e este arquivo.
- **Necessidade nomeada antes de editar:** o rótulo "Demonstração sintética" precisa substituir os textos que afirmam dado real ("imagem real (Copernicus/ESA)", "Sentinel-2 real", "KML do proprietário"). Esses textos estão em:
  - `gen37/areas/inicio.py`: mapa IN-04, legenda, cena e pixel;
  - `gen37/areas/cad_fazendas.py`: ajuda e consulta do cadastro.

  Os dois passam a ser reservados só para essa troca de texto.
- A trilha AÇÃO também altera `areas/inicio.py`. O merge depois deve ser sequencial e revisado.
- **SINT-REV-20261003-2300 (issue 1, comentário 5974392800):** reserva das correções C01, C02, G01 e T01 nos arquivos que o retorno lista.
  - **Necessidade nomeada antes de editar:** com a área de 2 casas da fonte única (C01), duas exibições passam a mostrar decimal com ponto ("29.92 ha"). As duas linhas ficam reservadas **só** para trocar o ponto por vírgula:
    - `gen37/areas/processo_safra.py:39`: ajuda "Áreas" do formulário do SAF;
    - `gen37/areas/processo_os.py:195`: rótulo do cultivo na O.S.
  - Nenhum hunk da REND (`126899e5`) ou da AÇÃO (`20f25726`) toca essas linhas. Não há mudança de lógica.
  - **Segunda necessidade nomeada antes de editar (C01 · dose × área):** `gen37/areas/processo_os.py:351` (`osc_apontar`) calcula o consumo como dose × área sem arredondar, mas o total do insumo é guardado com 2 casas. Com área decimal, o apontamento da área cheia é recusado (ex. sintético: 0,5 L/ha × 62,79 ha = 31,395 L contra 31,39 L em custódia). A linha fica reservada **só** para arredondar o consumo na mesma precisão do total. Nenhum hunk da AÇÃO toca essa linha.
    - **Ampliação nomeada antes de editar:** o JS arredonda 31,395 para 31,4 (`Math.round(x*100)/100`), e o Python (`round(x, 2)`), para 31,39. As três contas de dose × área do JS em `processo_os.py` (`:323`, total ao ajustar a área; `:351`, consumo; `:712`, total na ordem nova) passam a usar `Number(x.toFixed(2))`, que dá o mesmo valor do Python. Nenhum hunk da AÇÃO toca essas linhas.
    - **Mesmo padrão em outros arquivos, não alterado (risco registrado):** `cenario.js:152` e `areas/mobile.py:507/525` (app) calculam dose × área sem arredondar. Nenhum teste da cadeia os exercita com área decimal.
- REND, AÇÃO, C2 e PR34 não são editados nesta etapa.

- **SINT-C03 (comentário 5974993475), reserva registrada antes de editar:**
  - **Regra explícita de quantidade:** dose × área em decimal exato, 2 casas, meio para cima. O consumo de cada apontamento é quantidade(acumulado depois) − quantidade(acumulado antes), então a soma fecha no total e a custódia zera, sem tolerância nova.
  - **Arquivos:**
    - `gen37/quantidade.py` (novo, regra em Python);
    - `gen37/quantidade_test.py` (novo, regressão focal);
    - `gen37/cenario.js`: `cenQtd`/`cenQtdTrecho` e o consumo padrão do turno (`cenFecharTurno`);
    - `gen37/cenario.py:73`: consumido da semente da custódia da Lagoa pela mesma regra;
    - `gen37/areas/processo_os.py:176` (produtor Python do total) e `:323/:351/:357/:712` (consumidores JS);
    - `gen37/areas/mobile.py:507/510/525` (sugestão de consumo do app);
    - `gen37/dados_lagoa_safra.py` (textos de quantidade).
  - Nenhum hunk da REND toca esses arquivos. Na AÇÃO, só `processo_os.py` é tocado, em `645/851/981/987`, fora das linhas acima.

- **PRE-REV-20261004 (pré-revisão adversarial do autor sobre `0fcc2dc`/`74893ad`, antes do PR pedido pelo Adrianus), reserva registrada antes de editar:**
  - **Achados de 3 revisores independentes, cada um reproduzido em node com o JS real; correção nesta branch:**
    - **P1 · S2 · `gen37/mip.js:295`:** a O.S. emitida pelo MIP grava o total como `Math.round(dose×área×1000)/1000`, fora da regra única. Ex. sintético: 0,25 kg/ha × 37,75 ha → 9,438 contra 9,44 do consumo; o apontamento da área toda é recusado. Passa a `cenQtd(dose, área)`.
    - **P2 · S2 · `gen37/irrigacao_estado.js:433/452`:** a v2 de fertirrigação grava o total em kg inteiros (`Math.round(dose×área)`). Ex. sintético: 12 kg/ha × 48,93 ha → 587 contra 587,16; o apontamento do saldo é recusado. Passa à mesma regra, e a mensagem mostra 2 casas. A prévia em `gen37/areas/irrigacao.py:516` mostra o mesmo número.
    - **P3 · S3 · `gen37/areas/agronomia.py:664/668` e `gen37/mip.js:235/246`:** "Decidir controle" preenche a área do talhão com 1 casa; com área de 2 casas, ela passa do talhão e trava a emissão com mensagem que mostra o mesmo número. Passa a 2 casas no formulário e na mensagem.
    - **P4 · S3 · `gen37/cenario.py:79`:** a semente mudou sem subir `v`; o estado salvo de antes volta a travar o apontamento. Sobe para `v=3`.
    - **P5 · S3 · `gen37/dados_irrigacao.py:171/172`:** a `base` das fertirrigações OS-0506/OS-0507 é literal, não o realizado da semente; aparece aplicação fantasma. Passa a derivar de `dados_lagoa_safra.ORDENS`.
    - **P6 · S3 · `gen37/dados_mip.py:190/193`:** a área das decisões ligadas a OS-0504/OS-0508 é literal (maior que o talhão em PV06). Passa a derivar da mesma fonte.
    - **P7 · S3 · `gen37/quantidade_test.py`:** o item 6 não executa a recusa por custódia (passa com a trava desligada). Passa a executar a recusa na web e no app, e ganha os fluxos MIP → O.S. e fertirrigação → O.S. com custódia 0.
    - **P8 · S4 · `gen37/quantidade.py`:** `qtd_trecho` não é usado e arredonda a 6 casas de outro jeito que o JS. Sai.
  - Testes que podem mudar de linha de base: `irr_estado_test.py`, `mip_unit_test.py`, `mip_correcoes_test.py`, `dados_lagoa_sintetico/camada_test.py`.
    - **Nomeado depois da cadeia, antes de editar:** a mensagem "Área maior que o talhão" passou a 2 casas (P3). O `mip_unit_test.py` roda `gen37/mip_test.js:62–63`, e o `mip_correcoes_test.py:102` monta o texto esperado com 1 casa; os dois passam a 2 casas. O `carencia_test.py` falhou só porque a worktree nova não tem a pasta não rastreada `_probe/`; não muda (a cadeia cria a pasta).
  - **Revisão adversarial das correções (rodada 2), reserva antes de editar:**
    - **Q1 · S3 · `gen37/irrigacao_estado.js:429` e `gen37/areas/irrigacao.py:515`:** com passada em curso, a v2 arredonda o saldo de área para 1 casa (v1 + v2 ≠ área do setor; reserva de outra área). Uma função única com 2 casas serve à v2 e à prévia.
    - **Q2 · S3 · `gen37/areas/irrigacao.py:517` (introduzido pela P2):** a prévia chama `cenQtd` com a dose digitada; dose em notação exponencial derruba a tela. Só calcula com dose válida (0 < dose ≤ 50); e o `cenDec` de `gen37/cenario.js` passa a aceitar notação exponencial (como o `Decimal` do Python) e a converter o decimal exato no número mais próximo, então a regra única não lança com `1e-7` nem diverge do Python em valores extremos.
    - **Q3 · S3 · `gen37/areas/processo_os.py:569` (trava do ajuste), `:549/:558` (prévias) e `:483` (usado sem requisição):** dose × área cru; a trava recusa o que a regra única libera. Passam à regra única.
    - **Q4 · S4 · `gen37/mip.js:260`:** aviso de estoque do MIP com dose × área cru. Passa à regra única.
    - **Q5 · S4 · `gen37/areas/mobile.py:433` e `gen37/areas/agronomia.py:298/754/757`:** área com 1 casa ao lado da dose ou do total (a conta escrita não fecha). Passa a 2 casas.
    - **Q6 · S4 · `gen37/quantidade_test.py`:** o item 8 passa a cobrir a v2 com passada em curso (prévia = O.S.; v1 + v2 = área do setor) e o item 10 passa a varrer todo produto dose × área do JS (inclusive o embutido nos .py), com exceções nomeadas (planejamento, custo, carga do tanque).
  - **Revisão adversarial da rodada 2 (rodada 3), reserva antes de editar:**
    - **Z1 · S3 · `gen37/cenario.js:48` (cenLiberar) e `gen37/areas/processo_os.py:569` (trava do ajuste):** dose > 0 com total 0,00 pela regra única libera e a ordem nunca inicia (entregar 0 é recusado). A liberação e a trava recusam com "dose × área dá 0".
    - **Z2 · S3 · `gen37/mip.js:261`:** o aviso de estoque do MIP soma todos os lotes, mas a liberação reserva de um lote só. Passa ao mesmo critério (cenDisp(cenLote)).
    - **Z3 · S4 · `gen37/irrigacao_estado.js:438/439/460` e `gen37/areas/irrigacao.py:426/517`:** área com 1 casa ao lado do total de 2 casas nos textos da v2. Passa a até 2 casas.
    - **Z4 · S4 · `gen37/irrigacao_estado.js:344/362` (irrAvanco e término):** avanço digitado com mais de 2 casas faz v1 + v2 ≠ área do setor. A cobertura é guardada com 2 casas.
    - **Z5 · S4 · `gen37/quantidade_test.py`:** varredura nos dois sentidos (área × dose) e testes de comportamento da trava do ajuste, do aviso do MIP e da recusa de total 0.
  - **Revisão adversarial da rodada 3 (rodada 4), reserva antes de editar:**
    - **Y1 · S3 · `gen37/irrigacao_estado.js:435` e prévia em `gen37/areas/irrigacao.py:517`:** com o avanço em 100 %, a v2 nascia com 0 ha e 0 kg e a ordem ficava sem saída (Z1 recusa a liberação). Recusa ao criar, com a causa ("a passada já cobriu o setor" ou "aumente a dose").
    - **Y2 · S3 · `gen37/mip.js:246–262` (mipChecks):** receituário e O.S. com total 0 (foco de 0,01 ha). Trava "dose × área dá 0: aumente a área".
    - **Y3 · S3 · `gen37/areas/processo_os.py:246–250` (osMerge):** a recusa de total 0 aparecia como "Falta insumo" com dono Suprimentos. Passa a "Total 0", com o agrônomo e "ajustar antes de liberar".
    - **Y4 · S3 · `gen37/irrigacao_estado.js:344/362` e `gen37/areas/irrigacao.py:491/510`:** o arredondamento a 2 casas vinha depois da validação (término com 0,004 ha virava 0 e encerrava com conferência falsa). Arredonda antes de validar, no estado e na tela.
    - **Y5 · S4 · `gen37/areas/irrigacao.py:427/436` e `gen37/irrigacao_estado.js:107/557`:** cobertura e faixa com 1 casa ao lado do saldo da v2 com 2 casas. Passa a até 2 casas (mínimo 1, como antes).
    - **Y6 · S4 · `gen37/areas/processo_os.py` (trava do ajuste) e `gen37/quantidade_test.py`:** a trava vira a função `osc_ajFalta` do núcleo (a tela chama a mesma), com teste de comportamento; testes do término com 20,275 e 0,004 ha, da v2 com 0 ha e do MIP com total 0.
  - **Revisão adversarial da rodada 4 (rodada 5), reserva antes de editar:**
    - **X1 · S3 · `gen37/areas/processo_os.py:248` (osMerge), `:413` (osProx) e `:526` (ajLib):** com total 0, o painel da O.S. e o do Mapa ainda mandavam resolver no Suprimentos e o dono podia não ser o agrônomo. O impedimento diz o agrônomo, sem o link do Estoque; o ajuste continua "Salvar e liberar".
    - **X2 · S4 · `gen37/areas/processo_os.py:312` (osc_ajustar):** "Salvar ajuste" sem liberar gravava versão com total 0. Recusa sempre.
    - **X3 · S4 · `gen37/areas/irrigacao.py:483/492/510` e `gen37/irrigacao_estado.js:562–564` (irrSituacao):** área do setor com 0 ou 1 casa ao lado da cobertura com 2 casas (a mensagem recusava o próprio limite). Passa a até 2 casas.
    - **X4 · S4 · `gen37/areas/agronomia.py:676` (TAGS):** a trava de total 0 do MIP aparecia como "Dose fora da bula". Chip próprio.
    - **X5 · S4 · `gen37/irrigacao_estado.js:54` (irrV2Zero):** com outra passada programada, a recusa manda confirmar o término e adicionar os produtos às próximas passadas (não criar nova ordem).
    - **X6 · `gen37/quantidade_test.py`:** proteção de regressão de X1, X2 e X5.
  - **Separação:** nenhum hunk da REND (`126899e5`) toca esses arquivos. A AÇÃO (`20f25726`) toca `agronomia.py:1748` e `irrigacao.py:26–86`, fora das linhas acima. Depois do commit aqui, a `claude/v44-rend-01` recebe esta branch por merge.

## Reserva ativa · V44-REND (contrato no comentário 5974952517; liberada pelo 5974993475) · branch `claude/v44-rend-01`
- **Base:** `0fcc2dc` (candidata CAMADA + SINT-REV + SINT-C03), mais o merge **sequencial** (não octopus) de `prototipo-limpo/v44-rend` `126899e5`.
- **Arquivos:** `gen37/dados2.py`, `gen37/safra.js`, `gen37/areas/processo_safra.py` (preservar a formatação SINT da linha 39), `gen37/rend_multiconjuntos_test.py` e `gen37/rend_multiconjuntos_unit.py`. `gen37/cdp.py` entra só para resolver o conflito do merge.
- A correção SINT-C03 fica separada (`45b34c7`, na branch `claude/camada-sintetica-01`). A AÇÃO vem depois. A composição não é aceite nem publicação.
- **Estado da composição (executado na nuvem):**
  - merge `e9fd934`, com conflito só no `cdp.py`, resolvido mantendo o `CHROME_BIN`; o `rend_multiconjuntos_unit.py` passa a rodar no node fora do macOS;
  - REND unitário 36/36: o S5 dá 22,5 h necessárias e 12,5 h de déficit, em JS e no espelho Python (Fraction);
  - REND telas: fluxo 16/16, telas 4/4, bordas 10/10, bordas2 5/5;
  - build 0, varredura 144/144, camada 14/14, talgeo 8/8, talmapa 8/8, quantidade 6/6 e regressão da Lagoa verde;
  - aguarda a revisão do Codex e a contraprova do Gemini.
- **PRE-REV-20261004 na REND (pré-revisão adversarial do autor; reserva registrada antes de editar):** a camada/SINT corrigida entrou por merge `4b75731`. Achados executados por sondas (bloco REPARTIR no node + `dados2.repartir` em float e Fraction):
  - **R1 · S2 · `safra.js:66` e `dados2.py:228`:** configuração com janela 0 sai das uniões de sequência, e a necessidade e o déficit da sequência declarada somem (S5 com a janela de A = 0 dá déficit 0; com 0,01 h dá 12,5 h). As uniões passam a ser montadas sobre toda configuração com rendimento válido e parte no plano; a janela 0 continua sem receber área, e a troca dela não reduz a janela de quem trabalha.
  - **R2 · S2 · `safra.js:74–77` e `dados2.py:250–262`:** a união imposta por falta de recurso (grupo de recursos) junta uma sequência declarada com uma configuração sem janela, e a janela da sequência vira infinita: com MENOS plantadeiras o plano fica mais otimista (A+B fazem 20 h numa janela de 10 h, sem conflito). Passa a valer cada restrição: a de cada sequência declarada/mesmo ativo (a maior janela dela) e a do grupo de recursos (a maior janela do grupo, se finita), ao mesmo tempo, na divisão, no plano e no déficit.
  - **R3 · S3 · `safra.js:63` e `dados2.py:226`:** resto das partes fixas com tolerância absoluta 1e-12; acima de ~2 000 ha, partes que somam 100 % deixam resíduo que ativa configuração fantasma. Passa a tolerância relativa à área.
  - **R4 · S4 · `areas/processo_safra.py:148` e `safra.js:576–577`:** a etapa 4 mostra a área sem casas (Pivô 21 de 80,82 ha como 81; configurações 40 + 40). Passa a 2 casas, sem zeros à direita; o item 10 do `rend_multiconjuntos_test.py` passa a comparar com 2 casas.
  - **R5 · S3 · `safra.js:200` e `dados2.py:150`:** a memória CAL-01 mostra a área inteira (2.000 kg/ha × 48 ha = 96.940 kg). Passa a 2 casas nos dois lados.
  - **R6 · S3 · `gen37/saf_cmp_continuidade_test.py:142–145` (arquivo novo nesta reserva):** os itens 28/29 da Lagoa comparam números fixos da área antiga e falham na base e na composição (29 ok · 2 falhas); passam a calcular a expectativa por `dados2`. A AÇÃO toca esse arquivo nas linhas 48 e 70, fora destas. A suíte entra na cadeia.
  - **Revisão adversarial das correções (rodada 2), nos mesmos arquivos da reserva REND:**
    - **R1 introduzia S2** (configuração ociosa de janela 0 ligava o que não divide nada) e **R2 ficava incompleto (S2)** (ponte por outro grupo, ativo ou sequência ainda relaxava janela finita). Modelo novo, igual em `safra.js` e `dados2.py`: no plano só quem tem parte (sem % só as da divisão pelo rendimento); uma restrição de janela por recurso físico (sequência declarada, cada ativo, cada grupo de recursos que serializa), cada uma com a maior janela dos seus membros; mais o fecho de quem recebe área, se a janela dele é finita (o comportamento anterior quando tudo é finito); janela 0 entra só no plano; a troca reservada é a que o decorrido cobra (S3); o motivo do corte aninhado diz a fração final (S4); sem "dividem a mesma janela" quando a outra está em janela 0 (S3).
    - **R7 · S4 · `safra.js` (g_mat):** "Por mês" mostra a área com até 2 casas, e os meses somam o total.
    - Oráculo `rend_multiconjuntos_unit.py`: 50 verificações (T1a–T1c, T2a–T2c, N1, M1, M2, R4 "ociosa não muda" em 352 entradas, invariante por ativo); `rend_multiconjuntos_test.py telas` com o item 10b.
  - **Revisão adversarial da rodada 2 (rodada 3), mesmos arquivos:** dois S2 anteriores ao PRE-REV ainda abertos (grupo de recursos cujos usuários já estavam no mesmo fecho não restringia; janela 0 fora da decisão do grupo) e dois S3 da rodada 2 (o fecho finito sumia com um membro sem janela; empate de troca dependia da ordem). Duas falhas pelo mesmo motivo: muda a hipótese. **Só restrições por recurso físico** (sequência declarada, cada ativo, cada grupo de recursos); o fecho não é restrição (o decorrido continua tratando-o como uma sequência só, conservador). Grupo de recursos decidido pelo maior uso simultâneo real (sem a mesma sequência e sem ativo em comum), no plano (com janela 0) e na divisão; com 1 unidade, como um ativo. Troca reservada sem depender da ordem (a menor do fecho, se um membro a tem; o decorrido começa por ela). Oráculo: 57 verificações (P1–P5); o código das rodadas 1 e 2 falha nelas.
  - **Revisão adversarial da rodada 3 (rodada 4), mesmos arquivos:** S2 da rodada 3 (grupo de 1 unidade fora do "nunca ao mesmo tempo": na colheita de café, independentes eram serializadas) e S2 anterior (configuração que sozinha precisa de mais unidades do que a fazenda tem era planejada sem conflito). Grupo de 1 unidade conta como ativo para os outros grupos; configuração sem recurso não trabalha, com motivo e causa "sem recurso na fazenda" (a janela digitada continua na tela); busca do uso simultâneo com poda (20 configurações em ~1 ms). Oráculo: 63 verificações (Q1–Q5); o código da rodada 3 falha em 4.
  - **Revisão adversarial da rodada 4 (rodada 5), mesmos arquivos:** S2 (três configurações que se excluem duas a duas por recursos diferentes, um triângulo, faziam 15 h numa janela de 10 h sem conflito: as restrições por recurso só limitam pares) e S4 (pico do motivo, busca sem teto, unidades negativas). **Grupo inteiro de quem se exclui duas a duas** (clique maximal do grafo "nunca ao mesmo tempo": sequência, ativo, grupo de 1 unidade ou que serializa) divide a maior janela dele, no plano e na divisão; componente não cordal (ciclo de 4 ou mais sem corda) divide a maior janela finita dele (conservador, como o fecho antigo). Busca do uso simultâneo por componente, com teto; o motivo diz o pico real; unidades negativas ignoradas. Oráculo: 71 verificações (V1–V8 e a invariante "todo grupo maximal que se exclui cabe na maior janela"); o código da rodada 4 falha em V1–V4 e V7 e quebra no V8.
  - **B5a (rodada 5, achado do autor na cadeia; RETOMADA-20261004-1742, comentário 5982724904):** no pico de um grupo de recursos, o próprio grupo de 1 unidade separava os usuários dele (pico 1 em vez de 2) e o motivo dizia "quem a usa divide a janela dela" para configurações independentes. A decisão não mudava (grupo de 1 unidade sempre restringe); só o texto. No pico do grupo k, k não conta como "nunca ao mesmo tempo". Oráculo 72 (V9; Q1 corrigido, a expectativa da rodada 4 tinha o defeito); o código sem a correção falha em Q1 e V9; `rend_multiconjuntos_test.py bordas2` B5a volta a passar.
  - **Revisão adversarial da rodada 5 (rodada 6), mesmos arquivos da reserva (`safra.js`, `dados2.py`, `rend_multiconjuntos_unit.py`); reserva antes de editar.** Nenhum S1/S2 confirmado. O S2 proposto (triângulo + 4ª configuração com janela maior ou sem janela) foi refutado pelo verificador: segue a regra declarada "cada grupo divide a maior janela dos seus membros, sem limite se um não tem", igual para um recurso único desde `1688f97`; trocar essa regra é decisão do dono do oráculo (Codex) e entra no aberto (d). Três S3 e um S4 **introduzidos pela rodada 5**:
    - **W1 · S3 · `safra.js:119–123` e `dados2.py:320–331` (grafo):** 2 tratores × 2 plantadeiras (4 configurações, ciclo de 4) caem no "não cordal" e o componente divide a maior janela finita: atende 20 em vez de 40 ha, ou 2 em vez de 200 ha com uma janela de 1 h, e acusa conflito falso. C4 e trator × implemento são grafos perfeitos, e neles as cliques bastam. O conservador do componente fica só para grafo não perfeito (buraco ímpar de 5+ vértices no grafo ou no complemento), com a maior janela dos membros (mesma regra das cliques); cliques demais (> 4 096) ou busca que passa do teto também caem nele, com motivo.
    - **W2 · S3 · `safra.js:108/113` e `dados2.py:299/303` (SER):** um grupo que só passa das unidades no plano (por causa de uma janela 0) serializava a divisão (5 + 5 ha em vez de 10 + 10). Plano e divisão passam a ter cada um a sua lista.
    - **W3 · S3 · `safra.js:95–102` e `dados2.py:263–287` (simul):** com 28–30 configurações em cadeia o teto estourava, todas serializavam (100 em vez de 1.400 ha) e o motivo afirmava um pico inventado. Busca exata com cota por cobertura de cliques e parada assim que passa das unidades; se ainda estourar, o motivo não afirma o pico.
    - **W4 · S4 · desempenho:** cliques sem teto (30 configurações em trios: 2,1 s em JS e 6,1 s em Python). Teto de cliques (W1) e restrições indexadas por configuração.
  - **Abertos para regra do dono do oráculo (Codex), S3, sem mudança aqui:** (a) troca de configuração que não recebe área continua reservada na janela da sequência (conservador); (b) grupo de recursos com `un` frentes serializa todos quando faltam unidades (3 configurações com 2 plantadeiras fazem o de 1).
    (c) a divisão "terminam juntas" não é monótona em recurso: mais uma unidade num grupo, ou uma janela maior, pode reduzir o atendido (conservador; ex.: Q=100, A 1 ha/h janela 6 h a01+plantadeira, B 10 ha/h janela 10 h a01, C 1 ha/h janela 3 h plantadeira: 76 ha com 1 plantadeira, 58 com 2).

## Tarefas, na ordem
1. **CAMADA-SINTETICA (CORTE-REMOTO-01)**
   - **Arquivos novos:** `dados_lagoa_sintetico/{__init__.py, kml.py, gerar.py, saida/}`.
   - **Contrato:** `tools/prototipo/v37/specs/esquema_lagoa.md` (só a estrutura, sem valores).
   - **Gerador:**
     - determinístico, com semente fixa;
     - local fictício, com pivôs em círculo e raio = √(área·10⁴/π);
     - áreas e coordenadas inventadas;
     - CAR `SINTETICO-…`, perímetros, RL/APP e água inventados;
     - índices por pixel coerentes com a narrativa da safra (produção, formação, plantio recente, preparo, renovação no Pivô 12);
     - PNG gerado em Python puro (zlib), sem PIL.
   - **Rótulo:** no modo sintético, a interface mostra "Demonstração sintética".
   - **Refazer:** `talmapa_test.py` e `talgeo_test.js` (saíram do pacote), com coordenadas lidas de `dados_lagoa_fonte`.
   - **Aceite:**
     - build 0 e varredura 145/145;
     - testes que dependem da Lagoa Grande (map_decisoes, map_irrig_filtro, talmapa, carencia_test, mip_*, irr_*, os_v39_*, rend telas) passam, ou ficam listados com a nova linha de base e o motivo;
     - `ferramentas/varrer_categorias.py` dá TOTAL 0 (a varredura com valores reais é feita no Mac pelo proprietário/Codex).
   - **Estado (Claude nuvem, branch `claude/camada-sintetica-01`): implementado e testado, aguardando revisão do Codex e contraprova focal do Gemini.**
     - **Executado na nuvem:** build 0; montar_render ok; varredura 144/144; `dados_lagoa_sintetico/camada_test.py` 11/11; `talgeo_test.js` 8/8; `talmapa_test.py` 8/8; `varrer_categorias.py` TOTAL 0. Recibo, brutos e testes Lagoa com nova linha de base estão na issue 1.
     - **144 e não 145:** o build limpo gera 144 páginas. Hipótese não verificada: a 145ª era a `IN-02x-os0422`, que deixou de ser gerada e ficou de sobra no `project/` do Mac.
     - **Saída gerada:** `saida/` não é versionada. O `dados_lagoa_fonte` a gera sozinho, igual byte a byte; o carimbo fica em `saida/_carimbo.json`.
     - **SINT-REV-20261003-2300 (comentário 5974392800), correções aplicadas, aguardando nova revisão:**
       - **C01:** `PIVOS_HA` com 2 casas, igual ao mapa. O ponto decimal virou vírgula em `processo_safra.py:39` e `processo_os.py:195`. Dose × área tem um único arredondamento, no JS igual ao Python (`processo_os.py:323/351/712`).
       - **C02:** realizado, apontamentos, saldos, frações, textos, reservas e estoque das O.S. da Lagoa saem da área do pivô e das doses dos PLANOS. No modo real, com as áreas inteiras implícitas nos literais antigos, os 17 dicionários e as ordens ficam idênticos.
       - **G01:** o carimbo exige o conjunto exato das 11 saídas.
       - **T01:** `irr_estado_test` sai com 1 quando falha; expectativas de área vêm da fonte; `mip_unit_test` e `carencia_test` rodam no node fora do macOS; `os_v39_liberar` usa uma colheita sem carência pendente e mantém a prova negativa da carência.
       - **Executado na nuvem:** build 0; varredura 144/144; camada 14/14; talgeo 8/8; talmapa 8/8; decimais crus 0; mip_unit 34/34; carência 91/91; mip_correcoes 14/14; mip_fluxo 15/15; irr_estado 38/38; irr_fluxo 33/33; os_v39 liberar 14/14, bloq 11/11, selo_agua 12/12; map_decisoes 13/13; map_irrig_filtro 15/15. Contraprova do exit do T01: exit 1 com falha forçada.
     - **SINT-C03 (comentário 5974993475), corrigido:** regra única de quantidade (`quantidade.py` ⇄ `cenQtd`/`cenQtdTrecho`), em decimal exato, 2 casas, meio para cima, com consumo por trecho acumulado. Aplicada à O.S. (produtor e consumidores), ao app (que deixa de ser só risco), à semente da custódia e aos textos.
       - **Executado:** `quantidade_test` 6/6 (Python = JS em 7 771 casos, 774 com empate; 62,25 ha e 62,79 ha passam; trechos conservam o total; turno do app; sementes da Lagoa zeram a custódia).
       - **Cadeia completa verde:** build 0, varredura 144/144, camada 14/14, talgeo 8/8, talmapa 8/8, carência 91/91 e os demais testes da Lagoa.
     - **Achado para o Codex:** o círculo do `talgeo.js` (110 540 m/grau de latitude + esfera de 6 378 137 m + 72 lados) mede ≈ +0,58 % da área declarada. Está abaixo do limite de 1 % do `tmValida`.
   - **Atenção:** o artefato publicado hoje mostra a fazenda real; publicar da nuvem troca pelos dados sintéticos. Combine com o Codex e o Adrianus antes da primeira publicação a partir da nuvem.
2. **V44-REND** (REND-MULTICONJUNTOS `082884f3`; REND-RETORNO-1818 `7ae753dc`)
   - **Já feito:** implementação, verificação e correção. Unit 35/35, fluxo 16/16, telas 4/4, varredura 145/145. Brutos em `checkpoint-20261003/rend_fix_logs/` no Mac.
   - **S5** (22,5 h de necessidade e 12,5 h de déficit; separar demanda, atendimento e saldo): correção feita no bloco REPARTIR. O repro dá necessidade 45/2 h e déficit 25/2 h; unit 36/36, fluxo 16/16, build ok. **Falta:** conferir o espelho em `dados2.py`, rodar o teste de telas e fazer a verificação independente.
   - **Próximo:** verificar e corrigir o S5, depois integrar.
3. **V44-ACAO** (UX-ACAO-UNICA v2 `c691c431` + padrão v3.1)
   - **Feito em parte:** o `impl:acao` foi cortado depois do comando em execução. Estava removendo duplicatas (ex.: link de planos no MA-03) e escrevendo o modo `v3` do `acao_unica_test.py`. Comece pelo `git diff prototipo-limpo/base..prototipo-limpo/v44-acao` e rode `acoes_duplicadas.py` antes e depois.
   - **Próximo:** verificação adversarial e correção. Contraprovas Gemini (a)(b)(c) mais o 16º item com teclado virtual, matriz de responsividade, varredura de duplicatas por comando + alvo + registro (`acoes_duplicadas.py`) com meta 0, e pendências de componentes (OS-0424-app em 980 px, AG-07).
4. **INTEGRAR e PUBLICAR a v44** (com a ressalva da tarefa 1 sobre publicação).
5. **PADRÃO DE COMANDOS v3.1** nas demais telas e no gerador: posições nomeadas nos componentes, mais uma verificação na varredura que reprova duplicata ou comando fora do lugar.
6. **C2-F3** (software, `cc02b54f`)
   - **Base:** `4b7f2f07`.
   - **Fazer:** recibo local mínimo de pedido encerrado (referência, estado e metadados, por usuário e organização, com retenção limitada; gravado e conferido antes de excluir a pendência; sem duplicar; preservando a sucessora).
   - **Arquivos:** `pendencias.ts`, `useCadastroComando.ts`, `EnviosCadastro.tsx` e os testes.
   - **Provas:** reabrir, falha de gravação, isolamento e sucessora. Não iniciado.
7. **PR34-GITLEAKS-DIAG**
   - **Base:** `a2ffe24`. A CI deu 28 achados sem detalhe.
   - **Fazer:** emissão segura só de regra, arquivo, linha, commit e ID sanitizado, nunca Secret nem Match. Entregar o diff ao Codex **antes** de qualquer execução diagnóstica. Não iniciado.
8. **Fila D7, depois disso:**
   1. CAT-ATV. Correção de 03/10: `abc41b07` é **MAPA-ICONES**, não CAT. O CAT transportado tem `e47021d5`, e esse hash é do trecho, não do arquivo de origem.
   2. REND-config 15–18 + D4 + ALOC `058eb147`
   3. Monitoramento agrícola + MAPA-VISOES (`f46b2e19`) e MAPA-ICONES (`abc41b07`)
   4. SUP v2 (`e643eec7`)
   5. ORC-CUSTOS (`7915f874`)
   6. SOLO-MAPA-TV (`0b10392f` nesta lista; a cópia transportada tem `8c83b04e`)
   7. VEN v2 (`25d0882a` nesta lista; a cópia transportada tem `df64ef85`)

   **Textos transportados para a nuvem** (issue 1, comentários 5974199895, 5974202396 e 5974203077): os 9 blocos foram lidos e o sha256 de cada um confere com o declarado. **Divergência para o Codex decidir:** SOLO e VEN têm hashes diferentes nesta lista e na cópia transportada. Até a decisão, vale a cópia transportada, por ser a única recuperável na nuvem; nenhuma das duas foi aplicada. REND usa o patch cumulativo v2 (`11ccf1f0`), nunca junto do delta incremental.
   **Estado de implementação:** só o MAPA-ICONES foi conferido no código. Não está aplicado e o patch não se aplica mais à base (o `agronomia.py` mudou). Os demais itens estão "não iniciados" pelo registro de passagem, sem conferência arquivo por arquivo.
9. **Registrados para gatilho, sem iniciar:**
   - **PCP-ALOC-DESEMPENHO-20261003** (issue 1, comentário 5973928269; contrato SHA-256 `98ac1c49fe0d06799dfac46e9d1a8d365a23f4e39f1bf1c7b1fdeffd657aae66`): depois do aceite da CAMADA-SINTETICA, no fluxo existente (PL03/04, REND-config + D4/ALOC `058eb147`), sem sobrescrever REND/AÇÃO.
   - **QUALIDADE-ARTEFATO-20261003-FLUXO, adendo v2** (comentário 5974025581, SHA-256 `3000d8d3fa8e16630b373f2af756a8ba9ebc8e9b8c1db68a8469d57808bfaf3d`): jornada completa por IA só depois de **todas** as melhorias concluídas. A camada sintética e uma publicação parcial não contam como conclusão.

## Reservas locais soltas
Assim que este pacote for entregue, nenhum autor local roda e nenhuma reserva do Mac continua valendo. Cada tarefa acima passa a ter autoria remota única. Os originais com dado real ficam só no Mac, em `~/Safrion-recuperacao-local/corte-remoto-01/` (fora do iCloud), para eventual recuperação pelo proprietário.
