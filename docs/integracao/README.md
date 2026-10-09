# Integração na branch única: saídas brutas por candidata

Cada frente entra na `claude/prototipo-v44` pelo mesmo procedimento:
1. Merge `--no-ff` do commit exato que foi verificado, e não da ponta da branch da frente.
2. Build com 0 FALHA, `montar_render` e varredura de todas as páginas.
3. Testes do módulo e regressão das áreas tocadas. Cada vermelho é comparado com o pré-merge.
4. Dois verificadores independentes (agentes Claude separados; não é revisão do Codex):
   - **A:** integridade do merge e regressão;
   - **B:** aceite pela persona no navegador, em 1440×900 e 390×844, com os 7 critérios NAV-CLAREZA.
5. S1/S2 achado é corrigido em commit "Integração <ID>: …", com teste de regressão, e verificado de novo. Sem correção segura, o merge é desfeito localmente e nada é publicado.

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-proto>`, `<sp-…>` e `<chrome>`. Os dados são sintéticos (`SAFRION_DADOS=sintetico`).

| Candidata | Pré-merge | HEAD | Estado | Brutos |
|---|---|---|---|---|
| SAF-C01 (1ª entrega, `ef0d7b2`) | `cdc185f` | `9fb09a5` | Integrada, verificada (A e B sem S1/S2) e publicada (artefato v54). Reproduzida pelo Codex em 6086012087 | `SAF-C01/` |
| BEN (`4459669`) | `8c00092` | `a47578f` | Integrada. A 1ª verificação achou 3 S2, corrigidos em `bc0e76f`, `17ce6d2` e `a47578f`. **Reverificação (A e B) em andamento; ainda não publicada no artefato** | `BEN/` |

Arquivos do BEN:
- `pos-correcao/`: bateria do corretor depois de `bc0e76f`, `17ce6d2` e `a47578f` (`bateria_fin.txt`: `ben_fluxo` 85/85 nos 7 modos e varredura 141/141; `ben_mutantes.log` 61/61; `ben_unit_test.log` 144/144; `red_antes.log` mostra os testes novos vermelhos no `_render` antigo, 6/24).
- `pareceres.json`: relato do integrador, das lentes A e B da 1ª verificação (sobre `0644b1b`), do corretor e da lente já concluída da reverificação (sobre `a47578f`).
- **Teclado:** nenhum teste do BEN exercita o teclado. A cobertura de celular é emulação a 390 px (modos celular e faixa390). O teclado fica pendente.
- `resumo.txt` (merge, build, render, varredura), `nav_resumo.txt` (navegador), um `.log` por teste, `base_*` (pré-merge) e `links_ocultos_test_corrigido.log` (depois do `0644b1b`).
