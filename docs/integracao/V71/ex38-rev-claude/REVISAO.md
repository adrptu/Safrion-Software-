# Revisão do Claude · PR #77 (EX-38), HEAD e3e017c, base 519ed7b

Executado em 16/10/2026, dados sintéticos, render limpo de cada lado (156 páginas). Veredito: **devolver** (um S2 no escopo; AGENTS §3).

- `ex38_rev_test.py`: PR **36/45**; base **17/43** (`ex38_rev_pr_e3e017c.log`, `ex38_rev_base_519ed7b.log`). Repetir com `BASE_RENDER=<render 519ed7b> MUT_RENDER=<render com tanque do PJ-3030 em 2.500 L> python3 -B ex38_rev_test.py`; para a base, acrescentar `RENDER_DIR=<render 519ed7b>`.
- A cópia versionada do `ex38_rev_test.py` só renomeia a variável da chave do cenário (o Gitleaks a tomava por chave de API); o comportamento é o mesmo do teste executado.
- `ex38_test.py` do Codex: 12/12 no PR; na base o harness não roda (`ValueError: substring 'const dProj=' not found`), erro de ferramenta, não contraprova.
- Regressão um teste por vez: `regressao/`, `regressao_base/` e `regressao_resumo.txt`. Regressões do PR (base verde): app_entrega_parcial 5/7, app_mb03_turno 10/11, consumo_divergente 20/21 e mbtest com 1 falha, todas do cartão do MB-01 (achado 4). Vermelhos antigos iguais na base: dose_divergente 7/16, ap_unico, solo_os e ostest.
- As fichas em PDF do PR e da base ficaram fora do commit (binários); os números delas estão no log (A1d).

## Achados

1. **S2 · falta e preparo errados sem sinal; fórmula duplicada (ENG-011).** Turno fechado no app sem sinal (OS-0421, 20 ha, 10 L): as três telas mostram falta de 25 L (certo: 15 L), Adjuvante 40 L (certo: 35 L) e 6 cargas (certo: 5); a linha do painel diz USADO 105 L e falta 25 L, e a trilha diz Consumido 95 L e Em custódia 65 L. Com a área toda feita no aparelho e custódia 0, o MB-01 pede 70 L (certo: 0). Causa: `cenario.js:67` usa `o.saldo` do servidor e `:74` a custódia já baixada no aparelho; `:101` calcula o preparo sobre `o.saldo`; `processo_os.py:769` lê `cenGet()` cru em vez do `osReqVis`. Já existe a fonte única `cenOsSup` (`cenario.js:148-168`, CTL-4). Correção: previsto, custódia e falta saem do `cenOsSup`, e a área pendente no aparelho (`osApPend`) sai da área do preparo; teste com o `cenFecharTurno` real sem sinal.
2. **S3 · carga fantasma por ponto flutuante** (`cenario.js:101`, `Math.ceil(area/haCarga)` sem a tolerância de 1e-9 da base). Apontamentos de 0,2 e 39,8 ha: saldo 120.00000000000001 e "5 cargas · última 0 ha" (certo: 4 cargas · última 30 ha).
3. **S3 · trava do preparo bloqueia a custódia** (`os_campo.py:107`, `primDis` em qualquer fase). OS-0424 entregue e em v2 sem instrução mostra "Conferir preparo na O.S." desabilitado; a base oferece "Confirmar recebimento".
4. **S3 · MB-01 perdeu informação acionável** (`mobile.py:221-230`). Some "retirar 65 L" (13 galões) e "com você 1 L"; "Em conferência" fica sem a custódia. Manter o estado da base e acrescentar previsto e falta; o `app_mb03_turno` usa janela de 400 caracteres que o cartão maior estoura.
5. **S3 · ficha impressa perdeu "· parcial" na última carga e a instrução do caldeiro** (`os_campo.py:171-172`, `:190-191`). Os números estão certos.
6. **S4 (opcional):** "1 cargas" (`cenario.js:113`); "Reserva ao liberar" e "Consumo conferido" viraram "Sem requisição · previsto … · falta …" (`processo_os.py:773`; mostrar só em Liberadas e Em execução); o conjunto na ficha perdeu o trator; cabeçalho 128 ha × tabela 98 ha sem dizer "saldo"; app bloqueado com "Carga 0 de 0 · Tanque: —"; `disabled` em vez de `aria-disabled` com motivo (VIS-04) e ramo de aviso de `os_campo.py:108` que nunca roda; `EQ421` sem uso (`mobile.py:72`); coluna Calda de 96 px quebra no PDF; totais de `os_campo.py:76-77` em float com 3 casas, fora do serviço (ENG-013; leitura de código).

## Conferido sem achado

Um único `cenPreparoOrdem` alimenta painel, MB-02det, app e ficha; 100 L/ha só como semente em `cenario.py` e o tanque vem do `dados_cad`; cenário salvo da base (v 7) lido intacto; aprovação e liberação inalteradas; teclado (A8) e 390 px (A9) verdes. A base reprova A1b, A2, A3, A4, A5b/e/f e A6, os casos que a fatia corrige.
