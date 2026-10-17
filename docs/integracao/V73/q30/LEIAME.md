# Bateria q30 da composição 05947ad (PRs #81, #90 e #91) e publicação v109/v110

- **Composição:** `05947ad0152c31c106569219d4fdd09b8c7849a1` = `b9898643662715a3f7b17bf7797d44e81e5e4a3d` + PR #81 (EST-ONDA0, HEAD `2daee8e`) + PRs #90 e #91 (CRE-BANCO F1, HEAD `b35cd0c`; Crédito F2, HEAD `52cfe85`).
  - Enviada para `claude/v44-v69-mapa` em 17/10, com o Gitleaks limpo.
  - Integração feita pelo Claude como revisor (DEC-0910-02).
- **Render:** 156 páginas (`q30_build.log`), dados sintéticos.
- **Execução:** tudo foi executado. O Chrome rodou em `/tmp/cloudchrome/chrome`, com CDP_GL=1. O script é `q30.sh`, e `q30.out` é o resumo de uma linha por teste; os brutos estão em `q30_*.log`.

## Resultado (q30.out)

Testes em Node (sem navegador):

| Teste | Resultado |
|---|---|
| `est_onda0_unit.js` | 24/24 |
| `credito_ficha_unit.js` | 18/18 |
| `credito_ficha_motor_unit.js` | 17/17, na segunda execução |
| `credito_ficha_build.py` | GE08 gerada |
| `ds_inventario.py --catraca` | ok |

O `credito_ficha_motor_unit.js` deu rc=1 na primeira execução. O script rodou o teste antes de `credito_ficha_build.py` gerar o `credito_ficha_generated.js` (ENOENT), ou seja, foi um erro de ordem no script, não do produto. Reexecutado em `05947ad` depois da geração, passou em 17/17 (`q30_credito_ficha_motor_unit.js.rerun.log`, `q30_nota_motor.txt`).

Testes no navegador:

| Teste | Resultado |
|---|---|
| `est_onda0_test` | 24/24 |
| `credito_menu` (1440 e 390 px) | 26/26 |
| `links_ocultos` | 16/16 |
| `cadastros_rev1` | 19/19 |
| `cad_gravacao_falha` | 7/7 |
| `ds_modulos --catraca` | ok |
| `est_a4` | 53/53 |
| `consumo_divergente` | 21/21 |
| `os_cenario` | 22/22 |
| `tabelas_est` | 34/34 |
| `ben_fluxo` (multilote, multilote390, rodape) | 15/15 |
| `cadastros_padrao` | 44/44 |
| `demanda_estado_nav` | 14/14 |
| `paginas_scan` | 5/5, 148 páginas |

O `ds_modulos --catraca` regravou `docs/integracao/V72/ds-modulos.json` com a medição da composição. A única mudança é um rótulo de desvio TAB-08 já aceito na OS-0424-ficha: "tabela" passou a "Cargas de preparo".

## q28 (pasta `q28/`), em `7a6aa56` = b989864 + PR #81

| Teste | Resultado |
|---|---|
| `est_onda0_unit` | 24/24 |
| `est_cenario` | 15/15 |
| `esttest` | OK |
| `est_sem_validade_nav` | 8/8 |
| `map_decisoes` | 18/18 |
| `ben_fluxo`, todos os modos | 209 OK e 0 FALHA, mas incompleta: estourou o limite de 1.500 s (rc=124) |

- Os modos do `ben_fluxo` que faltaram foram cobertos na q30.
- Três linhas "sem -B" no `q28.out` vêm de um erro de leitura do `q28.sh`, que pulou `est_onda0_test` e as catracas. Esses testes foram incluídos na q30.
- A q30 mudou a composição (entraram os PRs #90 e #91). Por isso os testes de estoque e cenário foram repetidos nela; os da q28 valem como prova anterior equivalente.

## Publicação

- O artefato https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm foi publicado em dois envios, por causa do limite de 64 MB:
  - versão 109 (`1792196232-286d`);
  - versão 110 (`1792196275-c572`).
- Foram publicadas as 156 páginas `.dc.html` do render de `05947ad`. Nesse render, 148 páginas diferem da versão publicada anterior, 1792184197-5a81.
- **Readback:** 4 de 4 páginas conferem pelo SHA-256 entre o render e o publicado.

| Página | SHA-256 |
|---|---|
| `GE-08.dc.html` | `e8f4b49d…00ae` |
| `EST.dc.html` | `7a572043…c27b` |
| `MOD-CRE.dc.html` | `778aa4bd…33e3` |
| `OS.dc.html` | `f6317eff…8452` |
