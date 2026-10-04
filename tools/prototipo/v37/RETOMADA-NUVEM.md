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
    - **Q2 · S3 · `gen37/areas/irrigacao.py:517` (introduzido pela P2):** a prévia chama `cenQtd` com a dose digitada; dose em notação exponencial derruba a tela. Só calcula com dose válida (0 < dose ≤ 50) e sem lançar exceção (`cenQtdOu` em `gen37/cenario.js`).
    - **Q3 · S3 · `gen37/areas/processo_os.py:569` (trava do ajuste), `:549/:558` (prévias) e `:483` (usado sem requisição):** dose × área cru; a trava recusa o que a regra única libera. Passam à regra única.
    - **Q4 · S4 · `gen37/mip.js:260`:** aviso de estoque do MIP com dose × área cru. Passa à regra única.
    - **Q5 · S4 · `gen37/areas/mobile.py:433` e `gen37/areas/agronomia.py:298/754/757`:** área com 1 casa ao lado da dose ou do total (a conta escrita não fecha). Passa a 2 casas.
    - **Q6 · S4 · `gen37/quantidade_test.py`:** o item 8 passa a cobrir a v2 com passada em curso (prévia = O.S.; v1 + v2 = área do setor) e o item 10 passa a varrer todo produto dose × área do JS (inclusive o embutido nos .py), com exceções nomeadas (planejamento, custo, carga do tanque).
  - **Separação:** nenhum hunk da REND (`126899e5`) toca esses arquivos. A AÇÃO (`20f25726`) toca `agronomia.py:1748` e `irrigacao.py:26–86`, fora das linhas acima. Depois do commit aqui, a `claude/v44-rend-01` recebe esta branch por merge.

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
