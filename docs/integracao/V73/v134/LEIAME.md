# v134 · composição de 18/10/2026 (claude/v44-v134)

## O que entra

| Item | Pedido ou origem | Onde |
|---|---|---|
| ATIVO-UNICO | Proprietário, 18/10: cadastro de ativos numa fonte só, entre Manutenção e Cadastros. | CD-03 é a identidade; a MA é a visão operacional. |
| SAF-MAPA | Proprietário, 18/10: planejar a safra no mapa. | Planejar safra › etapa 2 › Mapa. Erro de gravação visível no mapa. Toque de 44 px. |
| AGUA-SOLO-IRR | Proprietário, 18/10: água no solo vive na Irrigação. | IR-01 › Água no solo (CC, PMP, CAD, AFD). O gatilho é o menor entre o limiar e a AFD. A emenda R24 está na especificação de solo. |
| Q5 fronteira | Codex 6250436415 | Duas previsões do mesmo PC e item sem linha, ou duas parcelas da mesma linha, não baixam a mesma nota duas vezes (JS e Python). |
| KMZ | Codex 6252555281 | KMZ corrompido ou com o diretório central fora do arquivo mostra "KMZ ilegível…" com o que fazer. |
| INTEL-03 | Codex 6252555281 | "Padrão observado" e "acerto retrospectivo"; produto perecível; compra que precisa vir antes do mês. |
| PAINEL-03 | Codex 6252555281 | A classe do ativo bloqueado vem da causa: risco à segurança é "Lei e segurança". |
| Oráculos | Base verde | CD-03 com 16 ativos (o CB-01 entrou) e "Editar talhões ›" no saf_lote. |

## Testes executados (render desta composição; brutos em `logs/`)

- ativo_unico 7/7; saf_mapa 9/9; agua_irr 10/10; saf_lote 47/47; cada_cd03 14/14; cada_fix03 11/11; tabelas_cad 206/206.
- mod_fluxo 17; ds_man; ma_menu 10/10; ma_unica 23/23; ma_rastreio 58/58; ma_planos 18/18; ma_vinculo 101/101; ma_regras 150/150; man_limpa 9; cadastros_padrao 44/44.
- cartoes 70/70; solo_ag02 30/30; ficha_pivo 21/21; irr_estado 38/38; solo_unit 129/129; ficha_pivo_unit 23/23; irr_onda0 28/28.
- mapa_kmz 6/6; intel03_nav 37; intel03_unit 28/28; inteligencia_nav 28/28; painel03 48.
- c34_fluxo 17; est_onda0 24/24; c34_paridade (16 paridades); c34_test 20 PASS.
- ds_test 72/72; paginas_scan 5 (146 páginas); textos_soltos 267/267.
- tabelas_irr 98/106 e tabelas_cad_irr_unit: vermelhos iguais aos da base v133, caso a caso (`base_tabelas_irr_v133.log`, `base_tabelas_cad_irr_unit_v133.log`; TABR-CTX-02 do IR-01). Não vêm desta composição.

## Contraprovas na base com o defeito

| Teste | Base | Resultado |
|---|---|---|
| ativo_unico | v133 | 0/7 |
| saf_mapa | v133 | Reprova (rc=1): a visão Mapa não existe. |
| agua_irr | v133 | 1/10 |
| c34_paridade | d8ef918d | Reprova no contraexemplo do Codex (80 e 30, `recebNaoApuravel` vazio). |
| mapa_kmz | Render antes da correção do leitor | 5/6 (K6), em `mapa_kmz_antes_da_correcao.txt` |
