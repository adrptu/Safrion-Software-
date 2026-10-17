# AGRO-06 · revisão Claude do PR #95 (Codex)

```text
ID / resultado útil / persona: AGRO-06 · registrar o laudo de solo com os 15 analitos, sem perder zero, unidade, método, limite e qualificador · agrônomo digitando um laudo real
Requisitos do PRD e fora do escopo: contrato PR #47 (6228621408, 6228566667); ESPECIFICACAO.md (solo) §Registrar laudo e 38.3 ("<" não calculável). Fora: solo.js, OCR, upload, layouts por laboratório, "Ver original" da TAB-11
Autor / revisor / integrador: Codex / Claude / Claude
Base (commit ou hashes) / arquivos sob responsabilidade: base f3ceb3c · HEAD a10656a (7c8d377 + autocorreção do LD 0) · areas/analise_solo.py, agro06_analitos_unit.js, docs/integracao/V73/AGRO-06/codex/REVISAO.md
Aceite e comando de verificação: §3 abaixo (comandos e saídas); sonda rev95_sonda.py a 1440/390 com contraprova em f3ceb3c
Estado / impedimento / próximo passo: SEM parecer favorável — S2 A1 e A2 e S3 A3 e A4 (min-height) a corrigir na mesma branch; A5 vira tarefa de domínio; reavalio o novo HEAD
```

Revisor: Claude (Opus 5.5) · 17/10/2026 · HEAD avaliado `a10656a74164c01fee6bf3a19fecf82d602fd93a`.

## 1. Veredito

**Não integrar ainda.** O PR entrega o que promete no caminho feliz: os 15 analitos aparecem, o zero e o ausente
ficam separados, a unidade e o LD 0 (corrigido em `a10656a`) chegam ao domínio, o erro do domínio mantém o painel aberto com os
valores, a amostra repetida é recusada e o laudo nasce "Aguardando validação". Os campos novos, porém, abrem dois caminhos
para o laudo validado sugerir dose por uma regra que não vale para ele (A1 e A2, S2). O contrato do PR #47 diz "nenhuma inferência
de dose ou de norma". As duas correções são locais à tela, sem mexer no `solo.js`.

## 2. Achados

### A1 · S2 · qualificador em texto livre: o domínio só entende "<", e a dica da própria tela leva ao valor errado
- **Caminho:** `tools/prototipo/v37/gen37/areas/analise_solo.py` l.261 (campo livre com a dica "Ex.: abaixo do limite") e l.107
  (envia `q` como foi digitado). O domínio reconhece só `q === '<'` (`solo.js` l.33 `soloCmolc` e l.53 `soloKmg`; ESPECIFICACAO.md
  l.127 e l.224). O detalhe do laudo só mostra o qualificador quando ele é "<" (`analise_solo.py` l.149).
- **Contraexemplo (executado, `rev95_dominio.py`, HEAD):** laudo do T1 com "K < 1 mg/dm³". O agrônomo segue a dica: valor 1,
  qualificador "abaixo do limite". O laudo é validado e o Planejar safra sugere **KCl 60 % de 120 para 180 kg/ha** ("K 1 mg/dm³ (Mehlich-1) → baixo").
  Com "<", o mesmo laudo dá "K abaixo do limite de detecção; nada sugerido". O Al "< 0,1" escrito do mesmo jeito entra como 0,1
  no t e no m, que deveriam sair "não calculável". O agrônomo que valida não vê o qualificador no Extraído, porque a coluna Qualificador · LD
  mostra só "1". O teste do PR fixa justamente o texto que o domínio ignora (`q:'< LD'` e `q:'não detectado'`).
- **Correção:** o qualificador vira uma lista curta com dois valores: vazio ("valor medido") e `<` ("abaixo do limite de detecção").
  Grava exatamente `''` ou `'<'`. O `>` fica fora até o domínio tratá-lo, com contrato próprio. Ajustar o teste: `'< LD'` e
  `'não detectado'` não podem existir. Acrescentar um caso que passe pelo `soloKmg` e dê "K abaixo do limite" (contraprova: reprova em `a10656a`).

### A2 · S2 · método de P/K diferente do extrator: a regra de K usa o extrator do laudo, não o método da linha
- **Caminho:** `analise_solo.py` l.107 (`met: x.met || ext`, "método informado prevalece"). A regra de K do domínio decide pelo
  `L1.ext` do laudo (`solo.js` l.226 e l.238). A especificação tem um só controle: "Extrator de P e K (Mehlich-1 ou Resina)".
  Na base, o método do K era sempre o extrator (`met: x.a==='K' ? r.ext : ''`), então a divergência não existia.
- **Contraexemplo (executado):** o laudo é de resina. O agrônomo deixa o extrator padrão (Mehlich-1) e escreve "Resina" no Método
  do K, que agora está à mão. O domínio grava `ext Mehlich-1` com `K.met Resina`. Depois de validado, o T1 recebe a sugestão de
  K₂O pela **tabela de Mehlich-1** ("K 58,65 mg/dm³ (Mehlich-1) → médio", 150 kg/ha de KCl). O inverso também acontece. Com o exemplo
  carregado e o extrator trocado para Resina, o K fica gravado como "Mehlich-1" num laudo Resina. Nesse caso a regra não sugere,
  mas o registro se contradiz.
- **Correção:** para P e K, o método é o extrator do laudo. Nos detalhes do P e do K aparece "Extrator do laudo: Mehlich-1",
  só para leitura, e a serialização envia sempre `met: ext`. Se for preciso registrar outro método de P/K, ele exige contrato com o domínio
  (`L1.ext` contra `K.met`). Ajustar o teste: hoje ele espera que "Outro método" prevaleça no P.

### A3 · S3 · detalhe sem valor some sem aviso
- **Caminho:** `analise_solo.py` l.107 (`filter(v !== '')`). O `sujo()` (l.215) conta `met/ld/q` como alteração, mas o envio os descarta.
- **Contraexemplo (executado):** Al "< 0,1" digitado só nos detalhes (LD 0,1, qualificador `<`, valor vazio). O envio sai `[]` para o Al,
  e o laudo registra "Al não analisado" sem nenhum aviso. Pela especificação, um resultado medido abaixo do LD é diferente de "não analisado".
- **Correção:** a linha que tem método, LD ou qualificador sem valor recusa no próprio painel, com o painel aberto e as escolhas preservadas:
  "Al: informe o valor do laudo (para < 0,1: valor 0,1 e qualificador <) ou limpe os detalhes."

### A4 · S3 · "Método e limites": alvo de 17 px e fora do padrão de seta (TAB-11) na composição
- **Caminho:** `analise_solo.py` l.257, `<summary style="cursor:pointer;font-size:12px;">` com o marcador nativo do navegador.
- **Executado (sonda):** os 15 summaries medem 17 px de altura a 1440 e a 390 com toque. O mínimo é 24 px a 1440 e 44 px a 390 (TAB-11 F).
  Nenhum tem `.g2seta` (TAB-11 B). O `seta_padrao_test` da TAB-11 não percebe porque não abre o formulário de registro.
- **Correção:** na composição com a TAB-11, o integrador (Claude) aplica `{E.seta()}` e `class="g2seta-nome"` com `min-height: 44px` a 390
  (24 px a 1440), e acrescenta `AG-02.dc.html#registrar=Santa Rita/T3` aos EXTRAS do `seta_padrao_test`. Nesta base sem a TAB-11,
  basta o `min-height`. O componente `E.seta` ainda não existe em `f3ceb3c`.

### A5 · S3 · pH em água lido com a régua de CaCl₂ (o domínio ignora a unidade na interpretação)
- **Caminho:** o PR oferece `'H₂O'` no pH (`SO_UN`, l.104). `soloIndVal` (`solo.js` l.41–45) devolve `Number(x.v)` sem olhar a unidade,
  e a coluna pH do AG-02 esconde o meio (`analise_solo.py` l.130, `ind.un==='CaCl₂'?''`).
- **Contraexemplo (executado):** pH 5,8 em H₂O sai 5,8 na régua de CaCl₂ (cortes 4,4/5,0/5,5/6,0), ou seja, "adequado" no mapa de calor (contraste
  Absoluto), quando em água isso é acidez. O defeito já existia para Ca/Mg em mmolc/dm³ (39 lido como 39 cmolc) e para a Argila em g/kg,
  que vieram da base. Não mexe em dose: a calagem usa o V, que converte.
- **Correção (fora deste PR, `solo.js` está fora do escopo):** tarefa de domínio para que o `soloIndVal` dê "unidade incompatível" (null)
  quando `x.un ≠ ind.un` sem conversão, e para mostrar o meio do pH na coluna. Não bloqueia este PR. Se o autor preferir, segura o `H₂O`
  até essa tarefa.

### A6 · S4 · observações sem bloqueio
- O sódio (Na) não está na lista, mas o domínio o soma no SB (`soloIdx`). Fica como "Na não analisado". A cobertura bate com os 15 da base e do `IND`.
- O exemplo do formulário (`dados_solo.EXEMPLO`) tem 5 analitos (Ca, Mg, K, H+Al, Al), não 15. O "Cortado: descarte dos nove analitos ao usar exemplo"
  do REVISAO.md exagera: o exemplo nunca os teve.
- Valor negativo (Ca −3,1) é aceito pelo `soloRegistrar` (anterior ao PR, do domínio). Fica para a mesma tarefa de domínio do A5.
- Os rótulos dos detalhes (`<label>Método…`) não têm o estilo dos outros rótulos do formulário (12 px, 700, cor secundária).

## 3. O que foi executado (e o que só foi especificado)

Ambiente: worktree `/tmp/claude-0/rev95` em `a10656a`, dados sintéticos. Brutos em `docs/integracao/V73/AGRO-06/claude/`.

| # | Comando | Resultado |
|---|---|---|
| 1 | `node agro06_analitos_unit.js` (HEAD `a10656a`) | PASS |
| 2 | contraprova do teste do Codex: `node agro06_analitos_unit.js <analise_solo.py de 7c8d377>` | AssertionError (LD 0 perdido) · exit 1 |
| 3 | contraprova: `node agro06_analitos_unit.js <analise_solo.py de f3ceb3c>` | ReferenceError soRlAnalito · exit 1 |
| 4 | `SAFRION_DADOS=sintetico python3 -B solo_unit_test.py` | RESULTADO: OK 129/129 |
| 5 | `SAFRION_DADOS=sintetico python3 -B solo_regressao_test.py` | RESULTADO: OK 2/2 |
| 6 | `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && SAFRION_DADOS=sintetico python3 -B montar_render.py` | 148 artboards · _render 156 páginas · exit 0; reconstrução com a mesma árvore: AG-02 idêntico byte a byte |
| 7 | `SAFRION_DADOS=sintetico python3 -B rev95_dominio.py <gen37>` (helpers reais do PR + solo.js real) | saída em `claude/rev95_dominio_HEAD.txt`: A1, A2, A3, A5 e os casos de zero, vírgula, unidade e LD 0 |
| 8 | `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B rev95_sonda.py _render 1440,390` (portão: 1 Chrome principal) | **29/31**: 15 analitos na ordem; nomes acessíveis "Valor de X" / "Unidade de X" / "Método·Limite de detecção·Qualificador de X" e `inputmode=decimal`; laudo com 15 linhas (Al **0**, Zn vazio, LD do Cu **0** digitado por teclado, vírgula, K em cmolc/dm³, Argila em g/kg) → domínio grava 14 analitos, `Al.v "0"`, `Cu.ld "0"`, `pH 5.4`, `Ca 3.90`, sem Zn, P/K com `met Mehlich-1`, MO `met ""`, Aguardando validação, painel do laudo novo aberto; erro do domínio (sem laboratório) mantém painel, valores, unidade trocada, LD 0 e detalhes abertos; repetido recusado no painel, nada gravado; Enter real abre o summary, Tab Método → Limite → Qualificador; foco visível; toque abre a 390; Esc com alterações avisa; sem estouro lateral; sem erro de JS; 63 paradas de Tab do × ao "Registrar laudo". **As 2 falhas são o A4** (summary 17 px a 1440 e a 390) |
| 9 | contraprova da sonda em `f3ceb3c` (`render_base`: AG-02 da base) | reprova: formulário com 6 analitos (`Ca, Mg, K, H+Al, Al, Argila`); a sonda para ao procurar "Valor de pH" · exit 1 |
| 10 | primeira rodada da sonda (`rev95_sonda_HEAD_v1_enter_sem_texto.log`) | descartada como prova: o Enter saía sem o texto `\r`, então o Chrome não ativava o summary (defeito da sonda, não do PR); corrigida como no `patest.py`, a mesma rodada inteira foi refeita (linha 8) |
| 11 | bateria do solo no navegador, um teste por vez com o portão (`rev95_bateria.sh`; brutos `claude/rev95_bat_*.log`) | `solo_ag02_test.py desktop` OK 27/27 · `celular` OK 5/5 · `mapa_solo_texto_test.py` 9 ok · 0 falhas · `solo_rev_test.py` OK 22/22 · `solo_mapa_calor_test.py` 9/9 · `solo_saf_test.py` OK 36/36 · `paginas_scan_test.py` 5 ok · 0 falhas (148 páginas) |
| 12 | sha256 de todo o `_render` da base contra o do HEAD (`claude/rev95_render_base_x_head.diff`) | das 181 páginas e arquivos, só `AG-02.dc.html` muda; reconstruir o HEAD dá o mesmo resultado. Por isso o `solo_os_test.py` (só OS e SAF, que ficaram idênticas) não foi rodado |

**Especificado, não executado:** leitor de tela real (NVDA/VoiceOver). A sonda confere os nomes acessíveis pelo `aria-label`, não a fala.

## 4. Ensaio de integração

`git merge-tree --write-tree` (git 2.43), sem conflito nos dois casos:

| Alvo | Árvore | Resultado |
|---|---|---|
| composição local `457ef14` (`/tmp/claude-0/int90`, branch `comp` = `f3ceb3c` + PR #89) | `d60dbeda` | limpo; o PR #89 não toca em arquivo de solo; `analise_solo.py` da junção passa no AST e no `agro06_analitos_unit.js` |
| TAB-11 `f42f5c7` (`/tmp/claude-0/seta`, base `d995ded`) | `4eb4b05d` | limpo; a única linha da TAB-11 em `analise_solo.py` (o summary "Ver original" ganha `class="g2seta-nome"` e `{E.seta()}`) fica junto com as 15 linhas novas; AST e teste do Codex passam na junção |

O que fica para a composição com a TAB-11 é padrão, não conflito: os 15 summaries "Método e limites" precisam da seta e do alvo (A4), e o
`seta_padrao_test` precisa abrir o formulário de registro (`AG-02.dc.html#registrar=Santa Rita/T3`), senão não os vê.

## 5. Delta `7c8d377..a10656a`
A autocorreção troca o fallback por verdade (`q.ld||''`) por um teste explícito de `null/undefined` na normalização (`soRlAnalito`),
no render (`rl_ans`) e na serialização (`soRlEnviarAnalitos`). O teste passou a usar `ld:0` numérico. Executado: o teste novo reprova em `7c8d377` e passa em
`a10656a` (linhas 1–2). Na sonda, o LD do Cu digitado como "0" chega ao domínio como `"0"` (§3). Nada mais mudou: são 2 arquivos e 4 linhas.
