# V67 · pedidos do proprietário de 14/10/2026 (tarde)

Dados sintéticos. Branch `claude/v44-v66`. Regime leve do protótipo (AGENTS §3.5).

| ID | Pedido (palavras do proprietário) | O que mudou | Prova (executado) |
|---|---|---|---|
| OS-ACAO-OFF-01 | "ordem de serviço agrícola esta faltando edição de insumos ... e botão de liberar a O.S para liberadas" | A tela da OS-0430 não mostrava os botões porque o perfil ativo era Otávio (PCM), sem o papel de aprovar e liberar. Antes, sem o papel, as ações sumiam. Agora "Liberar para execução" e "Ajustar antes de liberar" ficam visíveis e indisponíveis (apagados, cursor de proibido), com o motivo ao lado: quem decide e "troque no avatar do menu". O comando continua recusando do mesmo jeito. | `os_ator` 15/15 e `solo_rev` 22/22, com oráculos ajustados (acionável × indisponível em `os_lib.temb`/`temb_off`); `os_v39_bloq` 13/13; `os_v39_liberar` 20/20; `carencia` 91/91; `solo_os` 18/18; `ds` 69/69; `botoes_retorno` 6/6; `regras_toque` 5/5; `config` 88/88 |
| PERFIL-TODOS-01 | "me coloque sempre no perfil que tem todos acessos para testar tudo" | Perfil de teste "Proprietário · todos os papéis (teste)": todos os papéis do catálogo, fora do cadastro de pessoas. Não entra em "quem decide" nem nas alçadas. A casca do artefato (`gen37/site_index.html`, agora versionada) o põe a cada abertura. Trocar no avatar vale até a próxima abertura. Não é segurança de acesso. | OS-0430 com esse perfil: Liberar → Confirmar liberação → Liberadas (sonda no navegador) |
| OS-RECURSO-01 | "edição de ... recursos (pessoas e máquinas)" | Troca de recurso na O.S. antes da execução (A liberar ou Liberadas). Troca por outro da mesma função (trator por trator, operador por operador), feita pelo PCP ou por quem libera (AL-01). Substituto ocupado, em manutenção ou bloqueado na Manutenção aparece com o motivo e não pode ser escolhido; o comando recusa igual. A troca fica no cenário (`c.ordens[os].rec` e `recHist`). Uma fonte só (`alocacao.py`: `alVigente`) para o painel da O.S., o conjunto da atividade, a Origem, a Carga do PCP (agora calculada no navegador), a Manutenção (`manAloc`) e o app. | `alocacao_unit` 18/18; `os_recurso` 13/13 (navegador). Limitação corrigida em 392cb92: ver abaixo |
| CRED-MENU-01 | "crie o menu de crédito" | Módulo "Crédito" na barra lateral, entre Comercial e Configurações. Abre direto "Crédito e garantias" (GE-08: dívida, serviço da dívida, capacidade, solicitações e contratos, acompanhamento e dossiê com consentimento), tela que já existia sem entrada no menu. | `nav_modulos` 15/15; sonda: o link da barra leva a GE-08 |
| ACOES-PE-01 | "Biblioteca de planos ainda com bug visual" | Causa geral, não só da Biblioteca: o `main` tem 22 px de respiro no pé (18 px no estreito). Com `bottom:0`, a área de ações ficava presa 22 px acima do fim da janela, e o conteúdo rolava visível nessa faixa, embaixo dela. A área desce sobre o respiro e o repõe por dentro. A regra C3 da varredura visual passa a acusar faixa acima de 2 px (antes, 30 px). | Sonda PA (1440, 1024, 390): barra encosta no fim da janela, nada embaixo; `patest` 46/46 |

## Decisões tomadas pelos agentes
- **Sem papel:** a ação fica visível e indisponível, com o motivo; não some. Padrão de botões do design system. A troca de perfil continua só no avatar (sem "ver como" nas telas, pedido de 14/10).
- **Perfil de todos os acessos:** fica fora das pessoas, para não alterar os textos de "quem decide", as alçadas nem o cadastro. O padrão do código continua o primeiro perfil, e os testes não mudam; quem põe o perfil de todos os acessos é a casca do artefato.
- **Troca de recurso:** só dentro da mesma função e só antes da execução. Recusa choque de horário e ativo bloqueado (dano evitado: a mesma máquina ou pessoa em duas ordens ao mesmo tempo, ou máquina parada mandada a campo). Ultrapassar a jornada vira aviso, não trava. Bloco de manutenção da semana deixa de contar quando o ativo fica apto na Manutenção.
- **Crédito:** a tela existente (GE-08) entra no menu como está. Um painel gerencial de crédito (cobertura do serviço da dívida, CAL-19; garantias comprometidas) fica para a revisão dos painéis por alavancas (PAINEL-02).

## Bateria (executada na render de `ddf794c`, 14/10, em série)

Verdes: `ds` 69/69 (rodado sozinho; a falha D6 anterior era carga concorrente), `visoes` 9/9, `visoes_unit` 22/22, `tabelas_os` 40/40,
`acao_unica` 10/10, `os_ator` 15/15, `os_v39_liberar` 20/20, `os_v39_bloq` 13/13, `solo_rev` 22/22, `carencia` 91/91,
`painel_modulos --ui` 61/61, `painel_agricola --ui` 24/24, `ma_regras` 150/150, `ma_unica` 23/23, `matest` 40/40, `ma_app` 36/36,
`ma_app_fluxo` 24/24, `mbtest` sem falha, `ma_rastreio` 58/58, `map_decisoes` 18/18, `map_trilha_icones` 9/9, `talmapa` 8/8,
`paginas_scan` 4/4 (147 páginas), `patest` 46/46, `botoes_retorno` 6/6, `regras_toque` 5/5, `nav_modulos` 15/15,
`visual_corte` PA, OS, MB- e GE-08 sem achado.

Vermelhos e destino:
- `ostest` 32/33 e `os_cenario` 21/22: vermelhos antigos, iguais na v63 e na v66 (oráculos obsoletos: a atividade a7 cai na trava
  legal; o cenário subiu de versão). Oráculos corrigidos neste lote: 33/33 e 22/22.
- `links_ocultos` 15/16: efeito do menu Crédito (GE-08 no menu leva a GE-04, PT-04 e VE-05). Pares registrados com motivo: 16/16.
- `visual_corte` SAF (3 achados C1) e MA (9 achados C4 nos redirecionamentos MA-02/03/04det): iguais à linha de base da v63/v66.

## Publicação

Artefato https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm, versões 72 e 73 (1791981008-cc48), em duas partes pelo limite de 64 MB
por envio: 147 páginas mudadas e a casca nova (perfil de todos os acessos). Conferido por hash: `OS.dc.html` 69a500d0…, `GE-08.dc.html`
8bdd18a8… iguais aos da render; a casca publicada traz o `safrion.perfilDemo`.

## Correção depois da publicação (parecer do Codex 6167883199)

Limitação das versões 72/73 do artefato (fonte ddf794c), achada pelo Codex por contraprova:
- **Alocação (S2):** O.S. cancelada no cenário continuava ocupando máquina, implemento e pessoa na Carga do PCP, na Manutenção e na troca de recurso; O.S. removida do cenário voltava pela alocação de origem.
- **Ponte do painel (S2/S3):** ao chegar de um grupo do painel (`#painel=`), a busca salva, os filtros de coluna e os seletores Fazenda/Safra/Cultura/Talhão continuavam valendo sobre o recorte e podiam esconder ordens dele.

Correção em 392cb92 (`claude/v44-v66`):
- `alVigente` ignora a O.S. cancelada no cenário e a removida dele (fonte única para painel da O.S., Carga, Manutenção e app).
- Com o recorte do painel, busca, filtros de coluna e seletores ficam suspensos, avisados na faixa e apagados; "Ver todas" devolve tudo como estava.

Prova (executada, render de 392cb92 idêntica byte a byte à testada): `alocacao_unit` 21/21 (3 casos novos), `os_recurso` 16/16
(R14 a R16 novos). Contraprova na render anterior: R14 e R16 reprovam, e 2 dos 3 casos novos de alocação. Regressão das áreas
afetadas: `tabelas_os` 40/40, `ostest` 33/33, `os_cenario` 22/22, `filtros_cultura` 10/10, `visoes` 9/9, `ma_unica` 23/23,
`matest` 40/40, `mbtest` sem falha, `ma_rastreio` 58/58, `ma_app_fluxo` 24/24, `nav_modulos` 15/15, `os_ator` 15/15,
`paginas_scan` 4/4 (147 páginas).
