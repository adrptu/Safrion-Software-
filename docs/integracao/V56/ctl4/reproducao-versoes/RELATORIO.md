# CTL-4: os dois S2 atingem a v55 publicada ou a candidata v56?

Pedido do Codex (revisor) antes de liberar a v56: reproduzir, versão por versão, os dois S2 da CTL-4 com as mesmas entradas, pela tela e pelo motor.
Autor: Claude (subagente). Data: 12/10/2026. Tudo abaixo foi **executado**; dados sintéticos (`SAFRION_DADOS=sintetico`). Nenhum commit, nenhum push, nenhuma edição em `/home/user/sp-*`.

## Resposta curta

**Os dois S2 não atingem a v55 publicada (0c0931f) nem a candidata v56 (0ad2d0d e o merge 2e466eb).** Eles só existem no 853a6a8, a ponta da branch da CTL-4 com as correções, que ainda não foi integrada.

Três provas independentes sustentam isso:
1. **Ancestralidade.** Nenhum dos 17 commits da CTL-4 é ancestral de 0c0931f, de 0ad2d0d, de 2e466eb ou de 5d2119c (HEAD atual da int/v56). Pelo `git cherry`, nenhuma mudança equivalente chegou por outro caminho.
2. **Código.** As funções que causam os dois S2 (`cenEstDem`, `cenDemEntradas`, `cenOsDem`, `demFazenda`, `demSolSit` e `demSolRevisar`) não existem na v55 nem na v56. Nessas versões, `dados2.demanda(safra, ajustes, planos_extra)` não recebe o cenário: o Planejar safra e a Compra são calculados no build.
3. **Tela.** Com as mesmas entradas, a v55 e a v56 não mudam nenhum número do Planejar safra, da Compra nem do Mapa › Insumos. No 853a6a8, as mesmas entradas reproduzem os dois S2 exatamente como no achado original.

**Risco:** se o 853a6a8 for integrado na v56 sem nova correção, os dois S2 entram junto.

**Com a mesma entrada, a v55 e a v56 têm dois defeitos diferentes, ambos S3:**
- A quarentena fica escondida: o pedido continua "a receber" e o item aparece "Coberto".
- Cancelar a O.S. mostra "nada tinha sido entregue", mesmo com material entregue.

Os dois estão nas ressalvas, com reprodução.

## Versões testadas

Os commits não existem em `/home/user/Safrion-Software-`. Por isso, as worktrees foram criadas com `git -C /home/user/sp-camada-sintetica worktree add --detach`, o mesmo repositório das worktrees `sp-ctl4` e `sp-v56`. Cada versão foi gerada com `build.py` e montada com `montar_render.py`.

| Versão | Papel | Build |
|---|---|---|
| c5d337a | CTL-4 antes das correções | 0 FALHA · 140 páginas |
| 853a6a8 | CTL-4 com as correções, onde os S2 foram achados | 0 FALHA · 140 páginas |
| 0c0931f | v55 publicada (claude/prototipo-v44) | 0 FALHA · 142 páginas |
| 0ad2d0d | candidata v56 antes de juntar 0c0931f | 0 FALHA · 145 páginas |
| 2e466eb | merge de 0c0931f na int/v56 (`git -C /home/user/sp-v56 log --merges -1`; pais 0ad2d0d e 0c0931f) | 0 FALHA · 145 páginas |

O HEAD atual da int/v56, 5d2119c, só acrescenta `docs/integracao/V55/publicacao.md`. Não foi testado à parte.

## S2-1: a custódia fora do pendente deixa de contar como suprimento

**Esperado** (invariante da CTL-4; PRD 24; CAL-01): a custódia é suprimento. Entregar, cancelar a O.S. ou devolver a sobra não muda a necessidade líquida nem a compra.

### D1: devolver a sobra da OS-0417

Entrada: Estoque › Devolução de 500 kg de MAP 11-52 da REQ-031. A OS-0417 está Em conferência.

| Versão | Planejar safra: MAP (antes → depois) | Total e primária | Compra e Mapa T4 | Reproduz |
|---|---|---|---|---|
| c5d337a | 80.000 → 80.000 kg, Em cotação | R$ 430.255,00, sem mudança | sem mudança; Falta 80.000 kg | não |
| **853a6a8** | **80.000 → 79.500 kg, "Acima da demanda · 500 kg"** | **R$ 430.255,00 → 428.305,00; primária "Atualizar SOL-2026-07"** | Compra ganha o aviso "Acima da demanda · 500 kg"; Mapa: Falta 79.500 kg | **sim** |
| 0c0931f (v55) | 62.500 → 62.500 kg, Em cotação | R$ 379.580,00, sem mudança | sem mudança; Falta 80.000 kg | não |
| 0ad2d0d (v56) | 62.500 → 62.500 kg | R$ 379.580,00, sem mudança | sem mudança | não |
| 2e466eb (v56) | 62.500 → 62.500 kg | R$ 379.580,00, sem mudança | sem mudança | não |

Nas cinco versões, o cenário lido depois do passo confirma que a devolução aconteceu: custódia de 500 → 0 kg e lote M26-07 com 90.500 kg.

### C4: entregar, cancelar a O.S. e devolver

Entrada:
1. Estoque › Entregar 8.000 kg de NPK 20-05-20 da REQ-040 (OS-0425).
2. O.S. › OS-0425 › Cancelar sem execução (Ana, com motivo).
3. Estoque › Devolver os 8.000 kg.

| Versão | NPK: semente → entrega → cancelamento → devolução | Total e primária depois do cancelamento | Reproduz |
|---|---|---|---|
| c5d337a | 14.800 → **6.800 ("Acima da demanda · 8.000 kg")** → 14.800 → 14.800 kg | R$ 430.255,00 | não. Tem outro defeito: a entrega muda a compra (R$ 403.055,00). A correção do 853a6a8 tirou esse defeito, e ele não está na v55 nem na v56. |
| **853a6a8** | 14.800 → 14.800 → **22.800 kg "Complemento"** → 14.800 kg | **R$ 457.455,00 (+R$ 27.200); "Enviar para cotação"; Mapa C1: Falta 22.800 kg** | **sim** |
| 0c0931f (v55) | 14.800 kg nos quatro passos | R$ 379.580,00; "Abrir Compra de insumos ›"; Mapa C1: Falta 14.800 kg | não |
| 0ad2d0d (v56) | 14.800 kg nos quatro passos | R$ 379.580,00, sem mudança | não |
| 2e466eb (v56) | 14.800 kg nos quatro passos | R$ 379.580,00, sem mudança | não |

**Motor** (node com o `cenario.js`, o `cal01.js` e as funções `osc_*` reais da versão; arquivo `logs/<sha>/motor.log`):
- 853a6a8: o cancelamento leva o NPK de 14.800 para 22.800 kg, e a devolução o traz de volta a 14.800 kg.
- 853a6a8, caso T10: com o complemento enviado e o pedido emitido antes da devolução, a SOL fica com 22.800 kg, marcada "Acima da demanda" com diferença de 8.000 kg. São R$ 27.200 comprados a mais.
- 853a6a8, caso A11: a OS-0421 aponta 150 ha usando 20 L e depois devolve 40 L. A Safrinha 2027 cai de 7,98 L para 0 L.
- c5d337a: a entrega leva o NPK de 14.800 para 6.800 kg, e o cancelamento o devolve a 14.800 kg. A devolução de 8.000 kg e a do A11 não mudam nada.
- v55 e v56: o motor da demanda viva não existe nessas versões (não aplicável).

## S2-2: a quarentena vira falta firme

**Esperado** (PRD 65.4; CAL-01 "Qualidade pendente"; DEMO-02):
- A parcela em quarentena aparece como falta condicionada à qualidade, com decisão visível.
- Ela não conta como apta nem como saldo aberto do pedido.
- Nenhuma compra nova é proposta automaticamente.
- O laudo passa a parcela para apta uma única vez.

### G5: NF inteira em quarentena

Entrada:
1. Estoque › Conferir NF 4533 (PC-090): conferida 20.000 kg, apta 0, quarentena 20.000, validade 06/2027, motivo informado.
2. Laudo LAB-1 registrado por Ana, pelo comando da própria página do Estoque.

| Versão | Semente de soja 58 W: antes → NF → laudo | Total e primária com a NF | Mapa T4 com a NF | Reproduz |
|---|---|---|---|---|
| c5d337a | 0 kg "Coberto pelo estoque" nos três passos | R$ 430.255,00, sem mudança | "Pedido a receber · PC-090" | não; quarentena escondida (ressalva 3) |
| **853a6a8** | 0 → **15.456 kg "Complemento"** → 0 | **R$ 430.255,00 → 577.087,00; 15 insumos; "Enviar para cotação"** | **"Falta 15.456 kg"** | **sim** |
| 0c0931f (v55) | 0 kg "Coberto pelo estoque" nos três passos; recebimentos previstos continuam em 20.000 kg | R$ 379.580,00, sem mudança | "Pedido a receber · PC-090" | não; quarentena escondida (ressalva 3) |
| 0ad2d0d (v56) | igual à v55 | R$ 379.580,00, sem mudança | "Pedido a receber · PC-090" | não; quarentena escondida |
| 2e466eb (v56) | igual à v55 | R$ 379.580,00, sem mudança | "Pedido a receber · PC-090" | não; quarentena escondida |

**Motor:**
- 853a6a8: a Semente vai de 0 para 15.456 kg com a NF em quarentena e volta a 0 com o laudo; o total vai de R$ 430.255 para 577.087. `demSolSit` devolve "Complemento", e `demSolRevisar` coloca a Semente na SOL com 15.456 kg: é a compra duplicada.
- c5d337a: a Semente fica em 0 kg ("Coberto").
- v55 e v56: não aplicável.

### D3: devolução bloqueada (o mesmo mecanismo)

Entrada: Estoque › Devolução de 30 L de Fungicida A da REQ-035, como "Bloqueada para inspeção".

| Versão | Safra 2026/27 | Safrinha 2027 | Reproduz |
|---|---|---|---|
| c5d337a | 0,0 → 5,5 L "Complemento"; R$ 430.255,00 → 431.049,60 | 23,0 → 47,5 L | sim (já existia, como diz o achado) |
| **853a6a8** | 0,0 → 5,5 L "Complemento" | 23,0 → 47,5 L | **sim** |
| v55 e v56 (as três) | 145,2 L, sem mudança | 47,5 L, sem mudança | não |

## Consumidores atingidos (só no 853a6a8)

Pela busca nas 140 páginas do `_render`, só três chamam `cenDemEntradas`/`demFazenda`: SAF, CMP e IN-04.

| Consumidor | O que muda |
|---|---|
| **Planejar safra** | Necessidade líquida, Situação ("Complemento" ou "Acima da demanda"), Valor, "Valor da necessidade líquida", número de insumos e primária ("Enviar para cotação" ou "Atualizar SOL-2026-07") |
| **Mapa › Insumos** | Rótulo do talhão e "Falta X kg" (T4 e C1) |
| **Compra** | O aviso "Acima da demanda" aparece na linha (D1). Quantidade e total da SOL só mudam quando alguém aciona a primária do Planejar safra; o motor mostra o efeito (T10: SOL de 22.800 kg; G5: Semente entra na SOL com 15.456 kg). |
| **Portal do parceiro** (PT-02det) | Não muda: é lido no build. Ficou em R$ 362.796,49 antes e depois do D1. |
| **SU-03det** | Não muda: é fixo no build. Já é um S3 da lista original. |

Na v55 e na v56, nenhum desses números muda com as entradas.

## Ressalvas e achados com a mesma entrada

1. **Origem dos commits.** Os commits não existem em `/home/user/Safrion-Software-` (HEAD b8d6f84). As worktrees vieram de `/home/user/sp-camada-sintetica`, sem editar nem commitar nada.
2. **Primárias e laudo não acionados pela tela.**
   - Não acionei pela tela "Enviar para cotação" nem "Atualizar SOL". O efeito na SOL e no pedido vem do motor (T10 e G5b).
   - O laudo foi registrado com `window.__cen.cenLiberarQuarentena`, o comando da própria página do Estoque, e não pelo formulário da linha do lote.
3. **Achado, S3 proposto, de origem base, na v55, na v56 e também no c5d337a: a quarentena fica escondida.**
   - Reprodução: depois da NF 4533 conferida com 20.000 kg em quarentena (o cenário mostra o lote S58-0926 com 20.000 kg em quarentena):
     - o Planejar safra mantém "Semente de soja 58 W · 0 kg · Coberto pelo estoque", com recebimentos previstos de 20.000 kg;
     - a Compra mantém "23.816 · 12.000 · 20.000 · 0 kg · Coberto";
     - o Mapa T4 mantém "Pedido a receber · PC-090".
   - O que contraria:
     - PRD 65.4: a quarentena "não permanece simultaneamente no saldo aberto do pedido" e a falta deve ficar "sinalizada como falta condicionada à qualidade";
     - CAL-01: "não contar ... como saldo aberto do pedido";
     - M-02: proíbe "ocultação da falta real".
   - Por que S3 e não S2: não gera compra errada. O Estoque avisa que "20.000 kg em quarentena ficam fora do disponível". O dano é que a falta só aparece tarde se o laudo reprovar.
   - Causa: o Planejar safra lê a semente do build, a mesma limitação que a CTL-4 veio corrigir.
4. **Achado S3, de origem base, na v55 e na v56: o aviso de cancelamento contradiz a custódia.**
   - É o achado 7 da lista original, agora reproduzido nas cinco versões.
   - Reprodução: cancelar a OS-0425 depois de entregar 8.000 kg mostra "Requisição REQ-040 cancelada; nada tinha sido entregue."
   - O cenário lido logo depois mostra a REQ-040 com entregue 8.000 kg e custódia 8.000 kg.
5. **Divergência que já existia, sem relação com as entradas.** Na v55 e na v56, o Mapa T4 mostra MAP "Falta 80.000 kg", e o Planejar safra mostra 62.500 kg. É a DEM-05, que a CTL-4 C2 (ffb3da6) corrige.
6. **c5d337a com a entrada C4.** A entrega muda a compra: de 14.800 para 6.800 kg, "Acima da demanda · 8.000 kg". É o defeito que o 853a6a8 corrigiu. Não está na v55 nem na v56.
7. **Rótulo dos dados no build.** No c5d337a e no 853a6a8, o `montar_render` antigo escreve "dados reais locais: 5/5". Com `SAFRION_DADOS=sintetico`, `dados_lagoa_fonte` aponta para a pasta sintética, e as worktrees não têm `dados_lagoa/`. Os dados usados são sintéticos.

## Arquivos

Base: `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/ctl4-recorte/`

- **Logs** (`logs/<sha>/`):
  - `nav_s21.log` (D1 e C4 pela tela);
  - `nav_s22.log` (G5 e D3 pela tela);
  - `motor.log`;
  - `.out` (saída bruta).
- **Logs gerais** (`logs/`):
  - `ancestralidade.log`;
  - `build_<sha>.log`;
  - `resumo.txt` (números por passo, extraídos dos logs);
  - `execucao_navegador.out`.
- **Capturas** (`shots/<sha>/`): 18 por versão, por exemplo `d1_saf.png`, `c4_saf_cancelada.png`, `c4_mapa_c1_cancelada.png`, `g5_saf_quar.png`, `g5_mapa_t4_quar.png` e `d3_saf.png`.
- **Harness** (`harness/`):
  - `navlib.py`, `nav_s21.py` e `nav_s22.py`, cópia parametrizada do `ctl4rv/v1-estado` (variáveis `GEN`, `OUTD` e `LOGF`);
  - `m_s2.py` (motor);
  - `resumo.py`.

### Comandos

Navegador, uma versão por vez, com a trava cdpR:
```
env GEN=<wt>/tools/prototipo/v37/gen37 OUTD=shots/<sha> LOGF=logs/<sha>/nav_s2X.log VER=<sha> CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpR.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 harness/nav_s2X.py
```
Resultado: 10 de 10 execuções com exit 0 e nenhum erro de JavaScript.

Motor:
```
env GEN=... VER=<sha> SAFRION_DADOS=sintetico python3 harness/m_s2.py
```
Resultado: 5 de 5 com exit 0.

As worktrees foram removidas ao final, e os logs e as capturas foram guardados.
