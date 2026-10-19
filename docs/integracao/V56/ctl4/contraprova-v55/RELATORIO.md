# Contraprova do S2 do Codex (comentário 6133690044, PR #47): demanda do Planejar safra e da Compra ignora a devolução e a quarentena

Autor: Claude (subagente de contraprova), 12/10/2026. Somente leitura: sem commit, sem push, sem comentário no GitHub, dados sintéticos.

## Como foi executado (executado)

| Item | 0c0931f (v55 publicada) | 2e466eb (candidata v56, contém a 0c0931f) |
|---|---|---|
| Worktree destacada | `wt-0c0931f` | `wt-2e466eb` |
| `python3 build.py` | 135 artboards, saída 0, `grep -c FALHA` = 0 | 138 artboards, saída 0, `grep -c FALHA` = 0 |
| `python3 montar_render.py` | 142 páginas, sintéticos 5/5, saída 0, FALHA = 0 | 145 páginas, sintéticos 5/5, saída 0, FALHA = 0 |
| Roteiro | `scripts/roteiro.py 0c0931f`, 2 execuções, leituras idênticas | `scripts/roteiro.py 2e466eb`, 2 execuções, leituras idênticas |
| Erros JS na página | nenhum | nenhum |

- Comando: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpR3.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 scripts/roteiro.py <sha7>`.
- O `_render/` foi servido com `python3 -m http.server` em 127.0.0.1, numa porta livre. O Chrome headless (`cdp.py`) rodou com perfil novo, em 1440×1000.
- `localStorage` e `sessionStorage` foram limpos no início (contagem 0/0). Nenhum estado foi restaurado.
- Os passos 1 e 2 foram feitos pela tela, com clique na linha, preenchimento do formulário e clique em Salvar.
- As leituras vêm do DOM, nas colunas pelo cabeçalho. A memória de cálculo foi lida no painel lateral, aberto com clique no insumo.

## Passos e efeito no Estoque (executado, iguais nas duas versões)

| Passo | Tela | Valor obtido | Esperado (Codex) | Confere |
|---|---|---|---|---|
| 1 · Receba devoluções → REQ-031 → 500 → Salvar | recibo | "500 kg de MAP 11-52 devolvidos ao disponível. Custódia de MAP 11-52 na OS-0417: 500 kg → 0 kg · encerramento liberado." | recibo "500 kg … devolvidos ao disponível", custódia 500 → 0 | sim |
| 1 | condição padrão do formulário | "Apta · volta ao disponível" | — | — |
| 1 | cenário `MAP 11-52\|M26-07` | físico 90.000 → **90.500**; REQ-031 custódia 500 → 0, devolvido 1.000 → 1.500 | físico 90.500 | sim |
| 1 | EST · Confira saldos · M26-07 | físico 90.500 kg · disponível 90.500 kg (antes 90.000/90.000; custódia OS-0417 500 kg → —) | — | — |
| 2 · Confira recebimentos → NF 4533 (conferida 20.000, apta 0, quarentena 20.000, validade 03/2027, motivo) → Salvar | recibo | "Recebimento NF 4533 conferido: 20.000 kg de Semente de soja 58 W no lote S58-0926 (validade 03/2027). Disponível 12.000 kg → 12.000 kg; 20.000 kg em quarentena ficam fora do disponível." | — | — |
| 2 | cenário `Semente de soja 58 W\|S58-0926` | físico 20.000 · quarentena 20.000 · validade 03/2027 (não existia antes) | 20.000 físicos, 20.000 em quarentena | sim |
| 2 | EST · Confira saldos · Semente de soja 58 W | item: físico 32.000 · bloqueado 20.000 · **disponível 12.000**; lote S58-0926: físico 20.000 · bloqueado 20.000 "Liberar após inspeção" · disponível 0 · "Em quarentena" | disponível total 12.000 | sim |
| 2 | EST · linha NF 4533 | "NF 4533 24/09/2026 23/09/2026 PC-090 … S58-0926 20.000 kg 20.000 kg 0 kg 20.000 kg Aguarda laudo — 03/2027" | — | — |

## Demanda: antes, depois do passo 1 e depois do passo 2 (executado)

Os valores abaixo são **idênticos em 0c0931f e 2e466eb**: comparação JSON das linhas e do total, 6 de 6 iguais. Também não mudam entre "antes", "após o passo 1" e "final".

As capturas SAF e CMP de cada versão têm o mesmo md5 nos três momentos (execução 2). Há uma exceção: `0c0931f/0_antes_SAF_SEMENTE.png` difere das outras duas. Pela inspeção visual, a única diferença é o aviso temporário "Safra aberta: Safra 2026/27 · Demanda de insumos", ausente nela; os números são os mesmos.

### Planejar safra · `SAF.dc.html#saf=S2627&passo=demanda` (com "Expandir tudo")

| Insumo | Coluna | Antes | Após o passo 1 | Final (após o passo 2) | Esperado no final |
|---|---|---|---|---|---|
| MAP 11-52 | Demanda bruta | 152.500 kg | 152.500 kg | 152.500 kg | 152.500 kg |
| MAP 11-52 | Estoque apto | 90.000 kg | 90.000 kg | **90.000 kg** | **90.500 kg** |
| MAP 11-52 | Recebimentos previstos | 0 kg | 0 kg | 0 kg | 0 kg |
| MAP 11-52 | Necessidade líquida | 62.500 kg | 62.500 kg | **62.500 kg** | **62.000 kg** |
| MAP 11-52 | Falta em | 18/10/2026 | 18/10/2026 | 18/10/2026 | 18/10/2026 (falta de 24.000) |
| MAP 11-52 | Valor | R$ 243.750,00 | R$ 243.750,00 | **R$ 243.750,00** | R$ 241.800,00 (calculado: 62.000 × 3,90) |
| MAP 11-52 | Situação | Em cotação | Em cotação | Em cotação | — |
| Semente de soja 58 W | Demanda bruta | 23.816 kg | 23.816 kg | 23.816 kg | 23.816 kg |
| Semente de soja 58 W | Estoque apto | 12.000 kg | 12.000 kg | 12.000 kg | 12.000 kg |
| Semente de soja 58 W | Recebimentos previstos | 20.000 kg | 20.000 kg | **20.000 kg** | 0 kg apto (os 20.000 estão em quarentena) |
| Semente de soja 58 W | Necessidade líquida | 0 kg | 0 kg | **0 kg** | **11.816 kg pendentes da qualidade** (não compra firme) |
| Semente de soja 58 W | Situação | Coberto pelo estoque | Coberto pelo estoque | **Coberto pelo estoque** | não coberto; pendente do laudo |
| — | Total ("Valor da necessidade líquida") | R$ 379.580,00 · 15 insumos a comprar | igual | igual | muda (só o MAP já dá −R$ 1.950,00) |
| — | Primária | "Abrir Compra de insumos ›" | igual | igual | — |

Memória de cálculo da Semente no final, nas duas telas: "Estoque apto hoje: 12.000 kg ¦ 05/10/2026 · Recebimento PC-090 (Coop. Vale) · +20.000,0 kg → saldo 32.000 kg ¦ 15/10 … 8.320 → saldo 23.680 ¦ 18/10 … 15.496 → saldo 8.184 ¦ Sem falta nesta safra". Os 20.000 kg que já chegaram e estão em quarentena continuam contados como entrada apta prevista.

Memória do MAP no final: "Estoque apto hoje: 90.000 kg … falta 24.500 … falta 38.000 … = 62.500 kg". Os 500 kg devolvidos não aparecem.

### Compra · `CMP.dc.html#sol=SOL-2026-07&saf=S2627` (abre expandida)

| Insumo | Coluna | Antes | Após o passo 1 | Final | Esperado no final |
|---|---|---|---|---|---|
| MAP 11-52 | Bruta | 152.500 | 152.500 | 152.500 | 152.500 |
| MAP 11-52 | Estoque apto | 90.000 | 90.000 | **90.000** | **90.500** |
| MAP 11-52 | A receber | 0 | 0 | 0 | 0 |
| MAP 11-52 | Necessidade | 62.500 | 62.500 | **62.500** | **62.000** |
| MAP 11-52 | Valor | R$ 243.750,00 | igual | igual | R$ 241.800,00 (calculado) |
| MAP 11-52 | Na compra | A cotar | A cotar | A cotar | — |
| Semente de soja 58 W | Bruta | 23.816 | 23.816 | 23.816 | 23.816 |
| Semente de soja 58 W | Estoque apto | 12.000 | 12.000 | 12.000 | 12.000 |
| Semente de soja 58 W | A receber | 20.000 | 20.000 | **20.000** | 0 apto (20.000 em quarentena, condicionados ao laudo) |
| Semente de soja 58 W | Necessidade | 0 | 0 | **0** | **11.816 pendentes da qualidade** |
| Semente de soja 58 W | Na compra | Coberto | Coberto | **Coberto** | não coberto; pendente do laudo |
| — | Total | R$ 379.580,00 · "15 insumos a comprar · 3 insumos cobertos por estoque e pedidos" | igual | igual | muda |
| — | Primária | "Solicitar cotações ›" | igual | igual | — |

Conta do esperado (calculado a partir da própria memória da tela):
- **MAP:** 90.500 − 40.000 (15/10) = 50.500. Depois, 50.500 − 74.500 (18/10) dá falta de 24.000. Somada à falta de 38.000 (25/10), a necessidade é **62.000**.
- **Semente:** sem os 20.000 em quarentena, 12.000 − 8.320 (15/10) = 3.680. Depois, 3.680 − 15.496 (18/10) dá falta de **11.816**.

## Conclusão

- **Reproduz na 0c0931f e na 2e466eb.** Os números são os mesmos nas duas, o que mostra que a integração v56 não corrige o defeito.
- **MAP 11-52:** a tela mostra estoque apto 90.000 e necessidade 62.500. O esperado é 90.500 e 62.000. Diferença de **+500 kg de necessidade (+R$ 1.950,00)** nas duas telas.
- **Semente de soja 58 W:** a tela mostra necessidade 0, "Coberto" e 20.000 a receber. O esperado são **11.816 kg descobertos**, condicionados ao laudo. A quarentena é tratada como entrada apta futura.
- **Causa observada no código das duas versões:** a demanda do SAF (`safra.js` `demanda()`) lê só o `D2` congelado no build. São `D2.fisico`, `D2.quar`, `D2.receb`, `D2.recebDt` e `D2.reservas`: 0c0931f:572–589 e 2e466eb:584–601. O `D2` é serializado em `areas/processo_safra.py:227–228`. A CMP recebe `dem` de `areas/processo_compras.py` `_cd()` (linhas 39–57), também calculado no build a partir de `dados2.demanda`. Nenhuma das duas lê o cenário (`cenGet`) onde o Estoque grava. Por isso nenhuma ação do Estoque altera a demanda, nem só a quarentena.
- **Severidade:** concordo com S2 pelo AGENTS.md (cálculo material incorreto).
  - Necessidade a mais no MAP gera compra em excesso.
  - Na Semente, a falta fica escondida e o insumo some da compra ("Coberto"), com risco de faltar semente no plantio de 18/10 se o laudo reprovar.

## Divergências em relação ao Codex

1. **Nenhuma divergência numérica.** Os valores do Codex conferem todos: bruta 152.500, apto 90.000, necessidade 62.500; 23.816, apto 12.000, 20.000, 0 / Coberto; recibo; custódia 500 → 0; M26-07 com 90.500; S58-0926 20.000/20.000; disponível 12.000.
2. **Texto:** a frase "20.000 ainda a receber" não existe nas páginas (`grep` em SAF.dc.html e CMP.dc.html: 0 ocorrências nas duas versões). O valor 20.000 aparece:
   - na coluna "Recebimentos previstos" do SAF;
   - na coluna "A receber" da CMP;
   - na memória, como "05/10/2026 · Recebimento PC-090 (Coop. Vale) · +20.000,0 kg".

   O número é o mesmo; a redação do Codex é paráfrase.
3. **Nome da situação:** no SAF a situação da Semente é "Coberto pelo estoque"; na CMP é "Coberto". O Codex escreveu "Coberto" para as duas.
4. **Alcance:** o Codex atribui o defeito à leitura do `D2`. A contraprova confirma isso e mostra que o defeito é mais amplo que a quarentena. SAF e CMP são estáticos em relação ao Estoque: a devolução apta (passo 1) também não muda nada, e as capturas são byte a byte iguais antes e depois, salvo o aviso temporário citado acima.
5. **Linhas citadas:** as referências do Codex valem para a 0c0931f. Na 2e466eb, o trecho de `safra.js` passou para 584–601. Em `processo_safra.py`, o `D2` é montado na linha 228; a 227 monta a `SOL-2026-07` com `D2.demanda`.

## Arquivos

- Logs: `logs/0c0931f/` e `logs/2e466eb/`.
  - `build.log`, `render.log`;
  - `valores.json` (execução 2) e `valores_exec1.json` (execução 1);
  - `roteiro.log`, `roteiro_exec1.log`, `roteiro.stdout`.
- Capturas: `shots/0c0931f/` e `shots/2e466eb/`, 25 cada.
  - `0_antes_*`, `1_form_devolucao`, `1_recibo_devolucao`, `1_apos_dev_*`, `2_form_recebimento`, `2_recibo_recebimento`, `2_apos_quar_EST_saldos`, `3_final_*`;
  - `*_SAF_MAP`, `*_SAF_SEMENTE`, `*_CMP_MAP` e `*_CMP_SEMENTE` mostram a linha com a coluna Estoque apto.
- Roteiro: `scripts/roteiro.py`. Resumo: `scripts/resumo.py <valores.json>`.
- Nota: para criar as worktrees a partir de `/home/user/Safrion-Software-`, os objetos dos dois commits foram trazidos com `git fetch --no-tags --no-write-fetch-head /home/user/sp-camada-sintetica <sha>`, porque a 2e466eb não existe no `origin`. O fetch não criou ref nem FETCH_HEAD e não mexeu na árvore de trabalho.
