# EX-53 D11b, consumidor: semanas equivalentes no Backlog da oficina, 19/10/2026

**Autoria:** Claude, que tem a autoria de `manBacklog` e `pgBacklog` (M7a). **Revisão e integração:** Codex.
**Base:** composição `5bc0b340`, com o PR #132 (D11b, fonte da capacidade) integrado.

## Resultado útil
O gestor informa na CF-06 quantas horas por semana cada pessoa dedica a cada especialidade. O cartão "Backlog da oficina" do Painel › Manutenção passa a dizer quantas semanas de trabalho o backlog representa: "Mecânico 11,5 (0,4 semana)".

**Dano evitado:**
- **Antes:** o backlog em HH não dizia se a fila era de dias ou de meses.
- **Agora:** semanas equivalentes = HH ÷ capacidade semanal (ESPECIFICACAO §7, l.432). Sem capacidade válida não há número, e a dica diz o motivo (nunca 0).

## Mudança
- **`dados_manutencao.py`:**
  - `manHH` conta também as ordens sem tempo por especialidade (`semEsp`);
  - `manSemanas(r, cap)` calcula, por especialidade, `{hh, cap, pessoas, semanas, parcial, motivo}`;
  - `manBacklog(c, aid, cap)` devolve `semanas` por especialidade. Antes era `null` para o backlog inteiro.
- **Regras:**
  - **Sem capacidade** (`capacidadeDe` devolve `null`): `semanas` fica `null`, com o motivo "capacidade";
  - **Só ordens sem tempo:** `null`, com o motivo "sem estimativa";
  - **Ordem sem especialidade:** não consulta capacidade;
  - **Especialidade com ordem sem tempo:** as semanas são um mínimo ("≥").
- **`areas/painel_gestao.py`:** `pgBacklog(m, c)` passa `e => capacidadeDe(c, e)`.
  - **Cartão:** "Especialidade HH (N semana[s])" só onde há capacidade.
  - **Dica:** a capacidade de cada especialidade ("Mecânico 30 HH/semana (1 pessoa)") e, agrupado, o motivo das que não têm número:
    - "capacidade semanal não configurada";
    - "capacidade a revisar (calendário, situação ou contrato mudou)", quando há dedicação ativa que deixou de valer. Isso é lido pelos leitores públicos do PR #132 (`pessoasCapacidade`, `capacidadeRegistro`).
  - **Quebra de linha:** o "·" e o número ficam presos ao que medem (` `), e nenhuma linha começa com "·". As fotos de 1440 px mostravam "· Eletricista" abrindo linha.
- **Oráculo mudado, com motivo:** o B2 do `man_backlog_unit.js` conferia `r.semanas === null`, o contrato anterior. Agora confere que, sem capacidade, nenhuma especialidade tem número. A propriedade é a mesma.

## Testes executados (render sintético, Chrome)

| Teste | Resultado |
|---|---|
| `man_backlog_unit` (B15 a B21 novos: oráculo HH ÷ capacidade, sem capacidade, sem leitor, parcial, sem estimativa, sem especialidade, capacidade zero) | 23/23 |
| `ma_semanas` (novo, tudo pela tela). S1 sem capacidade; S2 CF-06 com 30 HH/semana de Mecânico para o Zé, o cartão mostra "Mecânico 11,5 (0,4 semana)" pelo oráculo dos dados crus; S3 o calendário da Oficina muda na CD-04, a dedicação deixa de valer e a dica diz "capacidade a revisar"; S4 1440/390 sem rolagem lateral e sem "·" abrindo linha; S5 sem erro de JS | 5/5 |
| Contraprova: `ma_semanas` no render da composição `5bc0b340`, sem o consumidor | 2/5. Reprova S1, S2 e S3 |

**Impacto, no render final:**

| Teste | Resultado |
|---|---|
| `ma_backlog` | 5/5 |
| `painel03` | 54/54 |
| `ex53_metas` | PASS |
| `ex53_m5_cartao` | PASS |
| `textos_soltos` | 267/267 |

**Impacto, no render anterior aos ajustes de quebra** (as mudanças seguintes tocam só o texto do cartão do backlog):

| Teste | Resultado |
|---|---|
| `ex53_alav_meta` | 5/5 |
| `ex53_f1c` | PASS |
| `paginas_scan` | 5/5 (147 páginas) |

## Fotos conferidas (`fotos/`)
- **`cf06_dedicacao_1440`:** a dedicação do Zé (Mecânico 30) sendo informada.
- **`pg_backlog_semanas_1440`:** "Mecânico 11,5" / "(0,4 semana) ·" / "Eletricista 3 — pronto 9,5 ·" / "pendência técnica 5".
- **`pg_backlog_semanas_390`:** em 3 linhas, sem rolagem lateral.

## Fora desta entrega
- **Reincidência (KPI-PCM-07):** segue como item do EX-53.
- **Cor do cartão:** o KPI-PCM-08 não tem meta inicial (ESPECIFICACAO §7), então continua sem cor.
