# MA-VINCULO · Vincular ativos a planos de manutenção

> Proprietário, 16/10/2026: "No módulo de manutenção, não consegui achar nada para vincular ativos a planos de manutenção, faça algo bem melhor. E que seja intuitivo, rapido, facil e pratico."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: MA-VINCULO / achar os ativos sem plano e vinculá-los em poucos toques, nos dois sentidos (ativo → plano e plano → ativos), com o próximo vencimento à vista antes de gravar / Otávio (PCM); Zé e Ana veem, sem permissão de gravar
Requisitos do PRD e fora do escopo: PRD 41, 47 e cap. 74 (BOT-01..09, TAB-01..10, VIS-05/06, SEL-04, FIL-01, MAIS-01); AGENTS §3.3 e §4; revisão do Codex 6226249749 (base de contagem). Fora: situação "Inativo" do CD-03 gravada no cenário (o cadastro de máquinas ainda não grava; ver Limites)
Autor / revisor / integrador: Claude / Codex / integrador da composição (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: b989864 / dados_manutencao.py (regras), areas/maquinas.py (tela MA), areas/modulos.py (aviso só da Manutenção: `_extra_do` e 2 parâmetros opcionais em `_hub`; as outras entradas iguais byte a byte), areas/cad_ativos_pessoas.py (só o link do CD-03), visoes_marcas.py (linha MA g_at), testes ma_vinculo_*
Aceite e comando de verificação: ma_vinculo_test.py U A B; ma_vinculo_medida.py (base × depois); regressão listada em "Testes"
Estado / impedimento / próximo passo: executado na branch claude/v44-v73-ma-vinculo (811bf7c + este registro) / sem impedimento / revisão do Codex
```

## O que o usuário vê e como usa

1. **Achar.** Na entrada do módulo Manutenção aparece "⚠ 4 ativos sem plano de manutenção · Vincular ›". Um toque abre Ativos já no filtro rápido **Sem plano** (o mesmo filtro também está na barra da grade, ao lado da busca, com a contagem).
2. **Ver.** A visão Ativos ganhou a coluna **Plano** (2ª coluna, no "Abre com"): cada plano do ativo com a situação (Atrasado · Vence em N h ou dias · Em dia · Rascunho · Plano inativo). Ativo sem plano mostra "Sem plano" e a ação: **"Vincular ao PM-07 ›"** (sugestão explícita) ou **"Criar plano ›"** quando nenhum plano do grupo serve.
3. **Vincular um.** "Vincular ao PM-07 ›" abre o painel com o plano já escolhido e o ativo marcado. Sem execução registrada, a pessoa escolhe "Contar de agora" ou "Informar a última execução"; a prévia mostra a origem da base e o próximo vencimento. "Vincular ao PM-07" grava.
4. **Vincular vários.** No cabeçalho de Ativos, "Vincular a plano" abre o mesmo painel com os ativos sem plano que a grade mostra (SEL-04: lista já marcada, um plano por vez, quem não serve fica de fora com o motivo). No detalhe do plano, a seção **Ativos deste plano** tem "Vincular ativos": candidatos compatíveis primeiro (os do "Aplica a" já marcados), busca e caixas. A primária diz o efeito: "Vincular 3 ativos ao PM-11".
5. **Desvincular.** Na linha de "Ativos deste plano", ⋯ › Desvincular: o painel avisa a OM aberta (que continua) e pede o motivo (atalhos de um toque ou texto).
6. **"Aplica a".** Editar plano mostra "Hoje: Todos do modelo MF 7719 (1 ativo)" e, ao trocar o modo, o quadro **Ao salvar** com o efeito (quem entra como candidato, quem segue vinculado).
7. **Cadastro de máquinas (CD-03).** No detalhe da máquina, só leitura: "Plano: PM-01 ›" (ou "Sem plano de manutenção · Vincular na Manutenção ›"), que leva à Manutenção. Um único lugar edita.

## Desenho (um só modelo de dados)

- `p.aplica` diz **a quem o plano se aplica**: `{t:'modelo', v:[modelos], x:[ativos de outro modelo vinculados como exceção]}` ou `{t:'ativos', v:[ativos escolhidos]}`. A extensão é só o `x`.
- `c.vinc['PM|ativo']` é **o vínculo**, com a base de contagem: `marco` (última execução antes do vínculo), `ult` (última por serviço, que vale primeiro: `manRef`), `desde`, e, quando desvinculado, `fim` (quem, quando, motivo) e `hist`.
- Regras num lugar só (`dados_manutencao.py`, JS): `manVincCompat`, `manVincSug`, `manVincBase`, `manVincRef`, `manVincPrev`, `manVincular`, `manDesvincular`, `manAplicaNova`, `manPlSit`. O recorte que diz "Sem plano" (`JS_VINC_BASE`: `manSemPlano`, `manPlanosDe`, `manVincVale`, `manPlVale`, `manAtvAtivo`) é o mesmo texto na tela MA, na entrada do módulo e no CD-03.
- Prévia = gravado: a prévia usa `manRef` + `manVenc` + `manProxTxt`, a mesma conta das linhas de vencimento.
- Gravação: `manMudar(..., {estrito:true})`: o recibo só aparece depois que o navegador gravou; se falhar, nada muda e o painel fica com as escolhas.

## Regras e o dano que cada trava evita

| Regra | Tipo | Dano evitado |
|---|---|---|
| Grupo de máquina diferente (plano de trator em pulverizador) é recusado, com o motivo | trava | ordem com tarefas e peças erradas; peça reservada para a máquina errada |
| Modelo diferente no mesmo grupo | aviso, permite | nenhum bloqueio desnecessário; quem vincula confere tarefas e peças |
| Mesmo serviço por dois planos no mesmo ativo é recusado (`manDupServ`, regra anterior) | trava | ordem em dobro |
| Gatilho por h ou km que o ativo não conta: aviso "vence só a cada N dias"; serviço sem nenhum gatilho aplicável é recusado. **Rege a versão publicada** (a mesma da prévia e das linhas); o rascunho de plano publicado só avisa; sem versão publicada, rege o rascunho v1 (revisão Codex 6229032017) | trava/aviso | plano "válido" que nunca vence (o antigo "Sem gatilho" calado); rascunho tornando elegível o que a versão em vigor não atende |
| Publicar não pode deixar ativo vinculado sem gatilho aplicável: "Publicar vN" desligado com o motivo | trava | máquina que parece coberta e não tem vencimento depois da publicação |
| Vincular, revincular ou repetir nunca zera nem sobrescreve marco, última execução ou ciclo; nunca registra manutenção como feita (Codex 6226249749) | trava | atraso escondido: 250 h, referência 1.000 h, leitura 1.450 h é Vencida; com a leitura atual como base daria Em dia |
| Sem execução registrada, a pessoa escolhe: informar a última execução ou contar de agora (marco estimado, marcado) | escolha obrigatória | data ou leitura inventada pelo sistema |
| Última execução: data futura, leitura negativa ou maior que a atual recusadas; corrigir a base de uma OM pede motivo | trava | base impossível; correção sem rastro |
| Contador ausente não vira 0; ativo com contador sem leitura não "conta de agora" | trava | vencimento calculado de um zero falso |
| Ativo inativo não é candidato nem "Sem plano" | trava | plano para máquina que não roda |
| Lote: tudo ou nada; repetir com a mesma chave ou com o vínculo existente não muda nada | trava | metade gravada; duplo clique gravando duas vezes |
| Lote = o conjunto marcado (revisão Codex): a busca não tira nem põe ninguém (o marcado continua na lista e no rótulo mesmo fora da busca); ao gravar, todos os marcados são conferidos de novo e um que ficou inválido (inativo, já vinculado, fora do cadastro) bloqueia o lote inteiro: nada gravado, sem recibo, painel aberto com a seleção e o motivo até a pessoa desmarcá-lo | trava | lote gravado pela metade em silêncio (a busca ou uma mudança de cadastro tirava ativos da gravação sem aviso) |
| Desvincular pede motivo, guarda o vínculo (fim + histórico) e não apaga a OM aberta; vincular de novo retoma a mesma contagem | trava | histórico perdido; ordem apagada; ciclo recomeçado do zero |
| Permissão pela regra que já existia (`manExige(c,pf,'plano')`): quem não pode vê o motivo e o botão desligado | trava | vínculo feito por quem não responde pelo plano |
| "Sem plano" = sem vínculo em plano ativo **e publicado**; vínculo só em rascunho ou em plano inativo aparece como Rascunho/Plano inativo | informação | ativo que parece coberto e não gera vencimento |
| Trocar "Aplica a" não perde vínculo e mostra o efeito antes de salvar; um plano serve a um grupo de máquina | trava + prévia | vínculo sumindo em silêncio; plano misturando grupos |

## Números antes × depois (AGENTS §3.3)

Executado: `ma_vinculo_medida.py`, o mesmo roteiro no navegador, perfil Otávio, estado zerado; cada ação conta 1 clique (lista nativa = abrir + escolher = 2); o resultado de cada cenário é conferido no estado (brutos: `ma-vinculo/medida_base.json` e `ma-vinculo/medida_depois.json`).

| Cenário | Base (render 8bdc1a1) | Depois | Resultado conferido |
|---|---|---|---|
| M1 · achar os ativos sem plano, a partir da entrada do módulo | 3 cliques (cartão Ativos + Pendência › Sem plano) | **1 clique** (aviso "4 ativos sem plano · Vincular ›") | lista só com a07, a09, a10, a12 nos dois |
| M2 · vincular 3 tratores a um plano (PM-11), sem execução registrada | 13 cliques (3 × painel "Vincular ativo": ativo, "Sem histórico", Salvar) | **3 cliques** ("Vincular ativos" › "Contar de agora" › "Vincular 3 ativos ao PM-11") | bases 2.988 · 5.120 · 3.410 h nos dois |
| M3 · vincular o Gotejo T7 ao plano do mesmo grupo (PM-07), a partir de Ativos | 8 cliques (Planos › PM-07 › Editar plano › marcar › Salvar › Vincular ativo › Sem histórico › Salvar) | **3 cliques** ("Vincular ao PM-07 ›" › "Contar de agora" › "Vincular ao PM-07") | base 5.210 h nos dois |

Digitação: 0 caractere nos três cenários, antes e depois. Quem informa a última execução digita data e leitura nos dois (os atalhos "Hoje" e "Atual · N h" do próprio ativo poupam a digitação quando valem).

Na base, "Sem histórico" gravava hoje e a leitura atual numa caixa marcada sem dizer a consequência; agora é a escolha explícita "Contar de agora", com a origem e a prévia à vista (revisão do Codex 6226249749).

## Testes

Ambiente: `tools/prototipo/v37/gen37`, `SAFRION_DADOS=sintetico`, montagem `build.py` + `montar_render.py` (156 páginas), Chrome headless, um navegador por vez. Brutos em `ma-vinculo/logs/` (um `.log` por teste; `resumo*.txt` por rodada).

**Candidata final:** render de **811bf7c** (árvore limpa). A bateria completa rodou antes de duas correções (painel: candidato do "Aplica a" recusado listado com o motivo; rodapé a 390 px) e de dois ajustes de teste; os testes que tocam essas peças rodaram de novo na candidata final (rodada 4). Os demais não mudaram de entrada (mesmas páginas fora do painel do vínculo) e não foram repetidos.

### Sem navegador (executado)

| Comando | Resultado |
|---|---|
| `python3 ma_vinculo_test.py U` (regras no node, `ma_vinculo_unit.js`) | 37/37 em 4d76bd1; 42/42 com a correção V8 (revisão Codex 6229032017), que reprova em 4d76bd1 (37/41: V8.1, V8.2 e a exceção de `manPubSemGatilho`) |
| `python3 ma_regras_test.py` (inclui `ma_regras_unit.js` e `ma_os_unit.js`) | 150/150 |
| `python3 ma_app_test.py` · `python3 compras_materiais_unit_test.py` | 36/36 · 41/41 |
| `python3 dados_manutencao.py` (autoteste: 14 vencimentos, 4 sem plano) | ok |
| `python3 ds_inventario.py --catraca` | catraca ok (css 6 · tabela 5 · cartão 5; não subiu) |
| `cmp` das entradas dos outros módulos (project de b989864 × 811bf7c) | MOD-AGR, MOD-COM, MOD-SUP, MOD-CFG, MOD-CRE e MOD-OUT iguais byte a byte |

### Navegador (executado)

| Teste | Resultado | Observação |
|---|---|---|
| `ma_vinculo_test.py U A B` (1440 e 390) | **88/88** (rodada 4, 811bf7c) | 1ª rodada: 1 falha de tempo em A4 (grade ainda desenhando); corrigido com espera pela condição |
| `ma_vinculo_test.py A` com A14 e A15 (revisões Codex 6229032017 e lote = seleção explícita) | **53/53** na correção; contraprova no `_render` de ad7af21 (maquinas.py e dados_manutencao.py idênticos a 4d76bd1): **47/53 — reprova** A14 (2) e A15 (4) | 4d76bd1 gravava só a02 quando a03 ficava Inativo depois de marcado, e a busca "Trator 02" gravava só a02 dos 3 marcados; brutos em `ma-vinculo/codex-lote-selecao/` |
| `ma_vinculo_test.py A B` na **base** (pasta de symlinks → render 8bdc1a1) | **1/11 — reprova** | sem aviso na entrada, `pend=semplano` ignorado (16 linhas), sem coluna Plano, sem painel; as duas partes param |
| `ma_app_fluxo_test` · `ma_atrito_test` · `ma_correcoes_om_test` | 24/24 · 13/13 · 15/15 | |
| `ma_correcoes_pm_test` | 11/12 → **12/12** (rodada 4) | falha real: candidato do "Aplica a" recusado sumia do painel; corrigido no produto |
| `ma_menu_test` · `ma_planos_test` | 10/10 · 18/18 | |
| `ma_rastreio_test` · `ma_revisao_test` | **58/58 · 18/18** (rodada 4) | |
| `ma_unica_test` | 22/23 → **23/23** (rodada 4) | oráculo ajustado (abaixo); AC-PCM-22 a 390 px (≥ 5 linhas acima da dobra) passou |
| `man_limpa_test` · `cada_cd03_test` | 9/9 · 14/14 | |
| `tabelas_cad_test` · `cadastros_padrao_test` | 206/206 · 44/44 | |
| `ds_1610_test` · `ds_1510_test` · `ds_padrao_test` | 14/14 · 17/17 · 17/17 | MAIS-01 (M7) incluído |
| `tab_drill_cab_test` (148 telas, 1440 e 390) | 6/6 | TAB-09/TAB-10 |
| `cartoes_test` | 69/70 → **70/70** (rodada 4) | oráculo ajustado (abaixo); os 5 M2d rodam (SAF, CD-05, MA Ativos, EST, CF-01) |
| `paginas_scan_test` (148 páginas) | 5/5 | linha do resumo perdida ao trocar o executor; o log está completo |
| `painel_modulos_test` · `nav_modulos_test` · `mod_fluxo_test` | 87/87 · 15/15 · 17/17 | |
| `ds_modulos.py --catraca` | catraca ok | Manutenção: 0 desvio nas 9 regras (`ma-vinculo/ds-modulos.json`) |
| `ma_vinculo_medida.py` base × depois | ver "Números" | brutos `medida_*.json` |

### Oráculos mudados (e por quê)

- `ma_correcoes_pm_test` 3, 4 e 7, `ma_revisao_test` F22, `ma_rastreio_test` F11: o painel "Vincular ativo" (um por vez, `#vk_*`) saiu; a mesma regra (base da OM encerrada, corrigível com motivo; leitura negativa recusada; mesmo serviço por dois planos recusado) agora é conferida no painel único "Vincular ativos" (`#vl-painel`, `#vl_data_<ativo>`, `#vl_leit_<ativo>`).
- `ma_rastreio_test` F21: a seção "Ativos vinculados · só leitura" virou "Ativos deste plano" (vincular e desvincular moram nela); continua sem "Gerar".
- `ma_unica_test` AC-PCM-05/06/07: o ⋯ da linha (TAB-05, 15/10) não é botão de comando; abre o menu, e o "Desvincular" abre o painel com motivo. Só o gatilho `.g2mais` sai da conta.
- `cartoes_test` (chips da barra): o filtro da tela marcado com `data-filtro-tela` (o "Sem plano") não entra na conta do "2º chip"; nas outras telas a escolha é a mesma (a primeira tentativa, que só olhava o grupo "Filtro rápido por", tirava o M2d do CD-05 e foi desfeita).

### Especificado, não executado

- Situação "Inativo" vinda do CD-03: a regra existe (`manAtvAtivo`) e foi testada pondo `sit` no estado; o cadastro de máquinas ainda não grava a situação no cenário.
- Revisão do Codex sobre esta entrega.

## Fotos

Em `ma-vinculo/fotos/` (1440 e 390 px, colunas como a pessoa vê; conferidas uma a uma):

| Foto | O que mostra |
|---|---|
| `F1_entrada_*` | entrada do módulo com "⚠ 4 ativos sem plano de manutenção · Vincular ›" |
| `F2_ativos_*` | visão Ativos com a coluna Plano (PM-xx + situação) e o filtro "Sem plano 4" na barra |
| `F3_sem_plano_*` | filtro ligado: 4 linhas, "Vincular ao PM-07 ›", "Vincular ao PM-08 ›", "Criar plano ›"; primária "Vincular a plano" |
| `F4_painel_um_*`, `F4b_depois_*` | painel de um ativo (plano escolhido, aviso de modelo diferente, contar de agora, prévia) e a lista depois |
| `F5_plano_*` | detalhe do plano: "Ativos deste plano" com base de contagem, próximo vencimento por serviço, situação e ⋯ |
| `F6_lote_*` | lote no plano (3 marcados, "Informar a última execução", data/leitura com atalhos, "Vincular 3 ativos ao PM-11") |
| `F7a_menu_linha_*`, `F7_desvincular_*` | ⋯ › Desvincular; painel com a OM-0234 que continua aberta e o motivo |
| `F8_ativo_*` | detalhe do ativo com "Plano PM-07 › Em dia" no cabeçalho |
| `F9_aplica_a_*` | Editar plano: "Hoje: …" e o quadro "Ao salvar" ao trocar "Aplica a" |
| `F10_cd03_1440` | CD-03: "Plano: PM-01 ›" só leitura, na Origem do detalhe da máquina |

Achados nas fotos, corrigidos antes da entrega: a 390 px a ação da linha "Sem plano" ficava escondida pela regra que mostra só a 1ª parte de cada célula; campos de data e leitura quebravam separados do rótulo; o rodapé do painel quebrava a primária para a linha de baixo; busca no painel de um ativo só era ruído (agora só em lista longa); o link do CD-03 saía com "› ›".

## Limites

- **"Aplica a" e grupo:** a compatibilidade usa o campo `grupo` que o plano já tinha (Tratores, Pulverizadores…); plano novo sem ativo herda o grupo do 1º ativo (regra anterior). Trocar "Aplica a" para outro grupo com ativo vinculado é recusado.
- **Base proposta pela OM encerrada** continua a regra D-41 (`manMarcoSug`, mesmo nome de serviço). Sem OM e sem vínculo anterior, a pessoa escolhe; nada é inferido.
- **CD-03 → Inativo:** ver "Especificado, não executado".
- **areas/modulos.py:** além do recorte da Manutenção, `_hub` ganhou dois parâmetros opcionais (aviso e JS) e a chamada do `build()` passa `_extra_do(nome)`, que só devolve algo para a Manutenção. As outras 6 entradas saem iguais byte a byte (sha256 conferido).
- **visoes_marcas.py:** a linha `MA g_at` ganhou "Plano" no "Abre com" (5 colunas essenciais).
- **Base da contraprova e da medição:** o render pronto de 8bdc1a1 (como pedido); difere de b989864 só numa dica do g2lib, fora da Manutenção.
- **Ícone do "Desvincular" no ⋯:** o motor escolhe o ícone pelo verbo (sai o de link); um ícone próprio de "desvincular" fica para o motor.
- **Incidente de execução:** o nome `bateria.sh` no scratchpad compartilhado colidiu com o de outra frente; um comando dela executou o meu script em paralelo por ~2 min (2 navegadores). Parei só a instância duplicada e renomeei os meus (`ma_vinculo_bateria*.sh`); as primeiras linhas de `logs/resumo.txt` misturam as duas instâncias. Os resultados acima vêm dos logs de cada teste e das rodadas 2 a 4.
- Sem push e sem comentário no GitHub; a revisão do Codex fica por fazer.
