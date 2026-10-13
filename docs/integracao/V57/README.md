# V57 · CONF (Usuários e alçadas) + menu Manutenção com subitens (executado, 13/10/2026)

Regime rápido do protótipo: testes pelo impacto, mais a varredura. A revisão do Codex não bloqueia a publicação (pedido do proprietário, 13/10). Os dados são sintéticos.

## O que entrou
- **Base:** v56 publicada (`3e3e0a8`).
- **CONF** (`4b4b7a6`):
  - telas Usuários e alçadas, Integrações e Auditoria, com alçadas G2_ALCADAS;
  - R13: aprovar (AL-02) e liberar (AL-01) separados; R14: quem envia para conferência e quem encerra fica gravado;
  - a CF-02 sai (CONF-D01).
- **A4 finito** (`986e82f`): quantidade contada finita, na contagem e na aprovação (achado S3 do Codex, 6148863313).
- **Menu Manutenção** (pedido do proprietário, 13/10): quatro subitens, um por visão da tela única: Pendências sem ordem · Ordens de manutenção · Ativos e disponibilidade · Planos preventivos. O destaque segue a visão aberta.

## Decisões da junção CONF × v56
| Ponto | Decisão | Motivo |
|---|---|---|
| `p11` usado pelas duas frentes | Caio fica `p11`; Otávio passa a `p14` | a CONF já usava `p11` na implantação e nos testes |
| Papéis da v56 (expedição, PCM, irrigante, comercial) | entram no `G2_PAPEIS` | sem isso, o perfil efetivo da CONF os descartava (Comercial e PCM parariam) |
| Dora (Comercial) | entra no CD-04 como `p15`, na equipe Comercial | CONF R5: quem decide é pessoa do cadastro |
| OS_AGRO, OS_LIB, CEN_CONF_AP, CEN_CONC_RESP | viram funções em todo o código | o nome vem da alçada, não fixo |
| Travas da v56 com papel fixo | reprovar laudo → AL-11; revisão de dose B-R8 → AL-02; conferência diária → AL-12 | CONF A4: nenhum comando confere papel literal. **AL-12 na conferência diária aguarda o aceite do Codex (autor)** |
| SOLO "Ajustar antes de liberar" | só para quem aprova e libera; quem só aprova segue "Aprovar vN" | R13; o ajuste continua disponível como secundário |
| Auditoria → ordem do BEN | abre Cargas enquanto o BEN não está publicado | decisão da v55 (BEN fora da navegação) |
| Conferência diária na colheita e na manutenção | vale para toda O.S. agrícola; os testes conferem o dia antes de encerrar | U14b, R06b e REV-A5 já falhavam na v56 publicada |

## Testes (executado)
- **Unidade:** config_unit 218/218, config_regressao 6/6, config_app 4/4, ficha_pivo_unit 23/23, aprova_quem_decide 103/103, est_a4 53/53, conferência diária 30/30, ds_unit 29/29, producao_unit 123/123, ma_regras 150/150.
- **Navegador:**
  - CONF: config_test 88/88, cada_cd04 15/15, links_ocultos 14/14, plataforma 22/0, assinatura 45/0;
  - Estoque e compras: est_a4_nav 15/15, esttest OK, est_fix1 13/13, est_fix2 11/11, est_cenario 15/15, tabelas_est 34/34, cmptest sem falha;
  - O.S. e demanda: demanda_unica 71/0, os_aprov_lib 51/0, tabelas_os 38/38, os_ator 15/15, conferência diária 16/16;
  - Design system: ds_test 69/69;
  - Manutenção: ma_menu 5/5 (novo), ma_atrito 13/13, matest 40/40, ma_planos 18/18, ma_rastreio 58/58, ma_app_fluxo 24/24;
  - acao_unica 10/10; varredura e ações repetidas na rodada final (`final/`).
- **Expectativas que mudaram, com o motivo:**
  - +Otávio e +Dora: 15 pessoas, 14 com acesso, trilha 18;
  - CONF F6: o contador deixou de ter valor padrão, então o teste escolhe;
  - menu: chegar à Manutenção custa 1 clique a mais (abrir o grupo e escolher a visão).

## Vermelhos antigos (iguais aos da v55)
- ostest 32/1 ("painel da nova ordem A liberar");
- os_cenario 21/22;
- consumo_divergente 20/21 (EST etapa 4);
- ben_fluxo (BEN fora do ar, em correção na rodada 3).

## Limites e pendências
- **Erro de processo:** a branch `claude/v44-v57-base` (`f6d7486`) subiu com os diretórios gerados `_render/` e `project/`, que trazem 30 nomes de chave de localStorage apontados pelo Gitleaks. Não são credenciais. A remoção foi bloqueada pelo sistema de permissões e fica com o proprietário. A base correta é `claude/v44-v57-conf` (`da723e6`).
- **Ficam para a v58:** TABR-CTX-02, UNID e VISOES-1 (corrigidas, ainda não compostas), os 4 S3 da lente CTL-4 e a inteligência comercial (INTEL-01).
