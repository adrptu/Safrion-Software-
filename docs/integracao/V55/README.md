# V55 · candidata ao artefato (ENTREGA-VISIVEL-20261010)

- **Candidata:** a ponta deste commit na `claude/prototipo-v44`.
  - Código = `6cce975`, que é a composição 47ff754 mais o BEN fora da navegação.
  - Documentação = mais a ponta anterior (`f359db2`, via `7e3d0d2`).
  - `git diff 47ff754 7e3d0d2 -- tools` está vazio.
- **Base publicada:** v54, de 09/10 às 17:10 UTC (SAF-C01, 9fb09a5). Sem o BEN.
- **Decisão de recorte:** Codex 6093581671.
  - Entram: MA, Planejar safra, divergência do turno (B-R8) e café.
  - O BEN não é publicado. O código dele fica na branch, com reativação por `BEN_PUBLICADO=True` em `ui37.py` depois da rodada 3.

## O que muda para o proprietário (em relação à v54)
1. **Manutenção numa tela só (MA).**
   - Um trator com dois motivos de bloqueio só volta a "Apto" quando os dois são resolvidos.
   - Até lá, o app e as O.S. continuam dizendo "Não opere".
2. **Planejar safra.**
   - A área livre do talhão é a mesma na trava, no aviso, no painel e na tabela.
   - O sistema sugere uma parcela que não colide com outra.
   - No Dividir, a recusa vencida some, e o "Área conferida" só aparece sem recusa à vista.
   - A capacidade de tratores e operadores é a mesma em qualquer safra aberta.
3. **Fecho do turno da O.S.**
   - Dose ou consumo divergente dá o selo "Divergência de consumo/dose".
   - A O.S. espera a revisão do agrônomo antes do encerramento.
4. **Café recebido em litros** aparece como "sc a apurar", nunca como 0 sc.

O Beneficiamento ainda não é publicado: saldo e reserva de caixas estão em correção (rodada 3).

## Commits de código desde a v54 (primeiro pai)
- Integrações BEN rodadas 1 e 2 (código mantido, tela fora da navegação).
- SAF-LOTE `26ee460`: SAF-C01b e SAF-C02.
- DOM `14e1e0e` e `8a1d6a9`.
- PCM `a32f9ef` e `9f05304`.
- `f768576`.
- SAF-C01b `00c16e3`.
- BEN r2 `4410b89`.
- `47ff754`, que corrige o PCM × BEN: `c.man` e "Ver na Manutenção" → `MA.dc.html#ativo=`.
- `6cce975`: BEN fora da navegação.

## Testes executados
- **Composição 47ff754** (`brutos/cand-47ff754_resumo.txt`):

  | Teste | Resultado |
  |---|---|
  | ben_fluxo | 172/172 |
  | saf_c01 | 68/68 |
  | ma_unica | 23/23 |
  | producao_fluxo | 66/66 |
  | ocupacao | 65/65 |
  | saf_operacoes | 87/87 |
  | saf_revisao | 42/42 |
  | saf_capacidade_simetrica | 38/38 |
  | tabelas_saf | 24/24 |
  | saf_cmp_continuidade | 31/31 |
  | ma_planos | 18/18 |
  | app_* | verdes |
  | rend_* | verdes |
  | carencia_fluxo | 41/41 |

  O build tem 0 FALHA e a varredura dá 142/142.
- **Recorte 6cce975:**
  - build com 0 FALHA: 135 quadros, 41 na página do menu e 94 nos ocultos, com o BEN nos ocultos;
  - varredura 142/142;
  - `links_ocultos_test`: 14 testes, 0 falhas. A extração passou a valer para todo `*.dc.html`. Os casos L4a-c são focais. O mutante `<a href="BEN.dc.html#OB-0110">` no PROD derruba o L2 e o L4b;
  - varredura de DOM `varre_ben.py`: 192 estados, 0 elementos que levam a `BEN.dc.html`. Cobre as 41 telas visíveis a 1440 e a 390 px, cada carga, cada lote do PROD, cada linha do COLH, as telas do Estoque, cada O.S. e cada ativo e OM da MA.
  - O restante da regressão do recorte (CARGA, PROD, Estoque, MA, menu), comparado com 47ff754, entra neste pacote assim que terminar.
- **Vermelhos base × candidata:** `VERMELHOS.md`. As falhas são idênticas em ostest, osacoes, acao_unica responsivo e partest.
