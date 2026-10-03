# RETOMADA-NUVEM: passagem do Claude local (Mac) para a sessão do Claude na nuvem
`CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01`

**Quem é quem**
- **Adrianus** é o proprietário. Ele delegou as decisões técnicas e de produto ao Claude e ao Codex (DECISOES-DELEGADAS-20261003). Ficam com ele custo, contas e acessos, dados reais, contratos, publicação para usuários reais e aceite.
- **Claude** é o autor do produto: protótipo e software real.
- **Codex** coordena, revisa e publica no GitHub.
- **Gemini** faz contraprova focal.

**Mac e canal**
- O Mac agora é só console.
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
| `prototipo-limpo/v44-rend` | `126899e5b3227327029d5c54e87d7313e1cfff02` | trilha REND, **parcial** (S5 corrigido sem verificação; o teste de telas não rodou) |
| `prototipo-limpo/v44-acao` | `20f25726d6318c2e249e38575e5458455a32ec16` | trilha AÇÃO + padrão v3.1, **parcial** (`impl` cortado no meio; sem verificação) |

**Não use:**
- `prototipo/v43` (c9d61266/d22da69), que contém dado real; a remediação é do Codex;
- os commits locais d7a2411b e f7967369, que nunca foram transportados.

**Merge:** `git merge prototipo-limpo/v44-rend prototipo-limpo/v44-acao` sobre `prototipo-limpo/v43`. A base de merge é `prototipo-limpo/base`. Conflito provável só em `areas/irrigacao.py` (faixa de etapas): vale a decisão da AÇÃO (indicador informativo) aplicada sobre o `_etp_nav` da v43.

**Origem de cada snapshot:** `MAPA-ORIGEM-SANITIZADO.json`, com a impressão sha256 das fontes de origem no Mac. A política de exclusão e redação está em `MANIFESTO-CORTE-REMOTO-01.md`.

**Software real:**
- `claude/next-16-3-6` = `a2ffe24` (pin e792 + PR34 + PR35), publicado.
- `claude/env-ui-c2-comp` = `4b7f2f07` (C2): bundle `eea16286` na pasta `fontes-claude/env-ui-c2` do Mac, a ser publicado pelo Codex.

## Como montar e testar na nuvem
```
cd tools/prototipo/v37/gen37
python3 build.py            # sai com 1 se algum módulo falhar
python3 montar_render.py    # monta _render/ com project/, support.js e os JSONs do AGROFIT
CHROME_BIN=$(which chromium || which google-chrome) python3 varredura.py   # "RESULTADO: 145/145 páginas sem erro"
python3 <teste>.py          # Chrome headless via cdp.py (CHROME_BIN)
```
Sem a camada sintética (tarefa 1), o build para em `dados_lagoa_fonte`, com uma mensagem clara.

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
   1. CAT-ATV (`abc41b07`)
   2. REND-config 15–18 + D4 + ALOC `058eb147`
   3. Monitoramento agrícola + MAPA-VISOES (`f46b2e19`)
   4. SUP v2 (`e643eec7`)
   5. ORC-CUSTOS (`7915f874`)
   6. SOLO-MAPA-TV (`0b10392f`)
   7. VEN v2 (`25d0882a`)

   Os pacotes estão em `work/prototipo-fase1/revisoes/qualidade-20261003/`; o Codex os transporta para o GitHub.

## Reservas locais soltas
Assim que este pacote for entregue, nenhum autor local roda e nenhuma reserva do Mac continua valendo. Cada tarefa acima passa a ter autoria remota única. Os originais com dado real ficam só no Mac, em `~/Safrion-recuperacao-local/corte-remoto-01/` (fora do iCloud), para eventual recuperação pelo proprietário.
