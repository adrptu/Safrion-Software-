# ACELERA · testes do protótipo mais rápidos, com o mesmo resultado (13/10/2026)

Branch `claude/v44-acelera`, base `302b26f` (candidata V56 sem a CTL-4). Regime leve do protótipo (AGENTS.md §3.5).
Nenhum teste existente mudou: nenhuma asserção, oráculo, tolerância ou caso. Mudaram só as esperas da infraestrutura
(`cdp.py`, `comp_lib.py`, `journeys.py`, `est_lib.py`, `os_lib.py`); entraram duas ferramentas (`render_cache.sh`,
`testes_afetados.py`) e dois testes da própria espera (`cdp_unit_test.py`, sem navegador; `cdp_espera_test.py`, com navegador).
Brutos: [`docs/integracao/ACELERA/brutos/`](../../../../docs/integracao/ACELERA/brutos/).

## O que mudou
| Parte | Antes | Agora |
|---|---|---|
| `cdp.py` `goto` | dormia `wait` (2,5 s por padrão) + até 10 s esperando o texto + 0,6 s fixos | espera o documento novo completo e com texto e depois a página assentar; teto = o fim da espera antiga (`max(início + wait, pronto) + 0,6 s`, com o pronto arredondado ao passo de 0,25 s do laço antigo) |
| `comp_lib.py` `goto` | `espera` + laço de 0,2 s + 0,4 s fixos | o mesmo, com teto `max(início + espera, pronto) + 0,4 s` |
| `Chrome.settle(quieto=0.3, teto=5)` | — | reutilizável (cdp e comp_lib): volta quando nada acontece na página por `quieto` s, contados da chamada; nunca passa do `teto`, salvo pelo crédito (abaixo) |
| `time.sleep(x)` com x ≥ 1 s num teste, fora de laço, no fio principal | dormia x | `settle(0.3, x)`. Laço que dorme (sondagem com orçamento de tempo), espera < 1 s e `time.sleep` de outro fio (servidor de teste) ficam como estavam |
| `journeys.py`, `est_lib.py`, `os_lib.py` | 1,2 + 1,5 s depois do clique que navega; 0,2–0,8 s depois de clicar ou avisar | `settle`/`espera_acao` com o mesmo teto; a espera depois de subir o servidor (tempo real) ficou fixa |
| Crédito do relógio fixo | — | o que as esperas anteriores economizaram; timer e pedido de rede são esperados quando, com as esperas fixas, já teriam vencido antes da próxima ação |
| `render_cache.sh <commit> [gen37]` | build + montar_render a cada vez (≈ 20–40 s) | uma vez por chave `<sha>-<SAFRION_DADOS>-<gerador>`, artefato imutável (manifesto sha256 conferido a cada chamada), trava contra montagem dupla (≈ 0,5 s depois) |
| `testes_afetados.py <base> <cabeça>` | bateria inteira | lista os testes que a mudança pode afetar, com o motivo |

**Assentar** (observação instalada em todo documento novo por `Page.addScriptToEvaluateOnNewDocument`). Ocupado enquanto houver:
navegação pendente (evento `navigate`, `beforeunload`, `Page.navigate/reload`), documento carregando, rede em curso (fetch, corpo
da resposta, XHR, FileReader, Blob, `crypto.subtle.digest`, `createImageBitmap`), timer ou intervalo devido, animação CSS finita
rodando, fonte ou imagem carregando. Quieto exige, além disso, nenhuma mutação no DOM (MutationObserver), quadro de animação
(`requestAnimationFrame`) ou mensagem do agendador do React (`MessagePort.postMessage`) por `quieto` s. DOM quieto é só
pré-condição: o teste continua afirmando o resultado do domínio como antes. Os invólucros só observam (chamam o original com os
mesmos argumentos).

**Crédito (relógio da espera fixa).** Cada espera que volta antes do teto adianta o teste em relação à execução com esperas fixas;
o crédito é a soma desse adiantamento. Timer e pedido de rede guardam o crédito do momento em que nasceram (`window.__sfcred`,
posto pelo `cdp.py` no fim de cada espera) e são esperados exatamente quando, no relógio da espera fixa, já teriam vencido antes
do fim desta espera: timer de `d` ms criado com crédito `c0` é devido se `agora + d + c0 ≤ início + teto + crédito atual`; pedido de
rede criado com `c0` é esperado enquanto `agora + c0 < início + teto + crédito atual`. Mutação, animação CSS, fonte, imagem e carga
seguem só o teto de cada espera. Cada espera vai no máximo a `teto + crédito`, e a soma das esperas nunca passa da soma dos tetos.

## Por que o resultado não muda
- Entre duas ações do teste, o que a página faria por timer ou rede com as esperas fixas acontece também agora, e o que só
  aconteceria depois da próxima ação continua não acontecendo. O que não depende de relógio (o efeito do clique, a renderização)
  é esperado até a página assentar, nunca além do teto antigo.
- **Divergência achada e corrigida na espera (não no teste).** A primeira versão (sem crédito, `2f63028`) deu `solo_os_test` 17/18
  na bateria (referência 18/18): no AC-SOLO-14 o aviso de 3,5 s do "Salvar ajuste" ainda não tinha vencido quando o teste clicava
  "Liberar para execução", porque cada uma das três esperas seguintes voltou em ~0,3 s; com as esperas fixas (1,0 + 3,1 + 1,4 s)
  ele vencia antes, e o re-render que ele provoca relê o cenário com o lote elevado. Com o crédito, o aviso vence antes do clique,
  como antes: `solo_os_test` 18/18 (duas vezes isolado e na bateria).
- **Contraprova da espera** (`cdp_espera_test.py`, oráculo = as mesmas cenas com `SAFRION_ESPERA=fixa` num processo filho):
  E1 aviso de 3,5 s e quatro esperas de 1 s (visível em 1, 2 e 3 s; some antes da quarta ação); E2 crédito acumulado e aviso NOVO de
  1,5 s (visível depois de 1 s: o crédito não adianta timer criado depois dele); E3 resposta de rede de 1,5 s; E4 soma das esperas ≤
  soma dos tetos; E5 `goto` só de âncora não espera documento novo. Executado: 6/6 na versão final (três vezes); a versão sem crédito
  (`2f63028`) falha E1; o rascunho que dava crédito sem a data do timer falha E2. `cdp_unit_test.py`: 5/5; a versão `2f63028` falha
  o item novo (o `time.sleep` do servidor de teste, em outro fio, virava espera no navegador e travava o protocolo).
- **Prazos contratuais ficam fora.** Na bateria, todo "em até N s" é laço de sondagem com orçamento de relógio (ma_unica 10 s,
  varredura 8 s, pa_lista, etapas_celular): `time.sleep` em laço não muda, e o orçamento é tempo de parede. A espera por condição
  só volta mais cedo (o que torna a asserção seguinte mais exigente, nunca mais fácil) ou espera um timer/rede que o relógio fixo
  já teria visto.

## Como usar
```
cd tools/prototipo/v37/gen37
../ferramentas/render_cache.sh <commit>             # monta uma vez; imprime o caminho do _render/ guardado
../ferramentas/render_cache.sh <commit> .           # e copia project/ e _render/ para esta pasta
python3 ../ferramentas/testes_afetados.py <base> <cabeça> --motivos   # quais testes rodar e por quê
python3 ../ferramentas/testes_afetados.py <base> <cabeça> --lista     # nome|VAR=v|comando, navegador primeiro
SAFRION_ESPERA=fixa python3 <teste>.py              # as esperas fixas de antes, inteiras (comparar, isolar um teste instável)
```
- Cache em `$SAFRION_RENDER_CACHE` (padrão: `render-cache/` no rascunho da sessão; fora dela, `${TMPDIR:-/tmp}/safrion-render-cache`).
  Chave `<sha>-<SAFRION_DADOS>-py<versão>-r<receita>`; só dados sintéticos; build com erro ou com "FALHA" no log não entra;
  arquivo alterado, a mais ou a menos no artefato é recusado. Executado: `302b26f` montado em 20 s; segunda chamada 0,46 s; o
  `_render/` é idêntico ao da chave antiga (o `project/canvas.json` só difere no carimbo `createdOnFiles`).
- Perfil do Chrome novo por execução: `cdp.Chrome` e `comp_lib.Chrome` criam um perfil temporário a cada navegador (o modo
  `CDP_PORT`, que anexa a um Chrome aberto, é opcional e não é usado na bateria).
- `testes_afetados.py` lê os testes na cabeça e marca: página `*.dc.html` que mudou citada pelo teste ou por um apoio que ele
  importa; teste que varre todas as páginas; arquivo servido que mudou (support.js, JSON: vale para todas); arquivo de gen37 que o
  teste usa (import, `.js`/`.json` citado, glob) e mudou; o próprio teste mudou; e sempre `varredura.py`,
  `acoes_duplicadas.py` e `links_ocultos_test.py`. É a lista para rodar primeiro; a bateria completa continua valendo a cada marco.

## Medição (executado)
Quinze testes de navegador, na trava `cdpA`, `CDP_GL=1`, dados sintéticos, mesmo artefato montado (`render_cache.sh 302b26f`, copiado
para os dois lados). "Antes" = código `302b26f` (esperas fixas); "depois" = esperas finais (`8bdf790`). Medida principal: o par
alternado (`14-medida`, antes e depois do mesmo teste um logo após o outro, a ordem trocando a cada teste). Tempo de parede dentro
da trava (não conta a espera pela trava). Colunas extras: outras amostras do código antigo (00-antes e 06-medida, mesmo código) e o
tempo do mesmo teste na bateria completa com o código final.

| Teste | Antes (s) | Depois (s) | Diferença | Antes, outras amostras (s) | Depois, na bateria (s) | Mesmo resultado em todas |
|---|---|---|---|---|---|---|
| `tabelas_cad_test` | 321 | 310 | -3% | 326 · 336 | 309 | sim |
| `tabelas_irr_test` | 208 | 178 | -15% | 204 · 218 | 173 | sim |
| `comercial_fluxo_test` | 138 | 127 | -8% | 131 · 149 | 125 | sim |
| `ctl5_test` | 82 | 75 | -9% | 80 · 95 | 70 | sim |
| `solo_saf_test` | 118 | 97 | -17% | 115 · 131 | 115 | sim |
| `partest` | 97 | 99 | +1% | 126 · 111 | 95 | sim |
| `acao_responsivo` | 69 | 68 | -0% | 84 · 81 | 74 | sim |
| `ostest` | 26 | 23 | -11% | 26 · 35 | 26 | sim |
| `osacoes` | 29 | 29 | +3% | 29 · 35 | 28 | sim |
| `producao_fluxo_test` | 255 | 228 | -11% | 269 · 303 | 237 | sim |
| `ma_unica_test` | 169 | 163 | -3% | 184 · 246¹ | 169 | sim no código final; ver nota ¹ |
| `irr_fluxo_test` | 138 | 104 | -24% | 144 · 168 | 119 | sim |
| `cafe_apurar_nav` | 28 | 26 | -7% | 29 · 36 | 27 | sim |
| `dose_divergente_nav` | 58 | 55 | -6% | 61 · 76 | 57 | sim |
| `etapas_celular` | 44 | 44 | +1% | 46 · 52 | 44 | sim |
| **Soma** | **1778** | **1626** | **-9%** | | | |

¹ A amostra de 246 s do **código antigo** (esperas fixas, máquina carregada) deu `ma_unica_test` 22/23 (AC-PCM-02: o terceiro
destino, "Novo plano do Silo 01", veio vazio). É instabilidade que já existia, sob carga; todas as amostras com as esperas novas
deram 23/23 (bateria, par alternado e a medição da versão anterior das esperas). Fica registrada, não escondida.

Ganho medido: **9 % na soma dos 15** (1.778 → 1.626 s), de 0 a 24 % por teste; nenhum teste ficou mais lento além do ruído (+1 a +3 %).
Nos testes medidos a maior parte do tempo é trabalho real do navegador e esperas curtas (< 1 s, que a regra manteve fixas: protegem
debounce e animação). Os ganhos maiores desta frente estão fora da espera: `render_cache.sh` (montagem de 20–40 s → 0,5 s por commit já
montado) e `testes_afetados.py` (5 de 181 testes numa correção de um teste; 22 de 181 numa mudança de uma página).

## Equivalência (executado)
| Prova | Resultado |
|---|---|
| Bateria completa da V56 (54 de navegador + 17 de unidade: `lista_cand.txt` + `cadc_cd02_test`, mesmos comandos) com as esperas finais (`8bdf790`), comparada teste a teste com os brutos da `1f83eee` (cand-2e466eb com os refeitos da cand-1f83eee por cima): código de saída, resumo e o rótulo de cada asserção que falha | **71/71 iguais**. As falhas conhecidas da referência continuam as mesmas: componentes_interacao 2, componentes_ajustes 2, agrofit 1, etapas_complemento 2, etapas_desktop 1 (base `gen37_antes` ausente, como na referência), etapas_faixa 1, ostest 1, os_cenario 1, osacoes 5 |
| Versão com defeito (`2e466eb`, os cinco vermelhos de integração da V56) com as esperas finais, comparada com a cand-2e466eb | **5/5 iguais**: tabelas_cad 176/178, tabelas_irr parado em ~4 s, ctl5 28/30, ficha_pivo 17/21, comercial_fluxo 71/72. As esperas novas não escondem nenhum vermelho |
| Testes da espera | `cdp_espera_test.py` 6/6 e `cdp_unit_test.py` 5/5; contraprovas acima |

Soma do tempo dos 54 de navegador nesta bateria: 4.364 s (referência cand-2e466eb: 5.345 s, outra hora e outra carga da máquina;
só indicativo — a comparação controlada é a da Medição).

## Seleção pelo impacto: prova com os vermelhos reais (executado com as ferramentas finais)
Para cada vermelho de integração da V56 e da CTL-4, a lista da mudança que o causou inclui o teste que o pegou
(`testes_afetados.py <base> <cabeça> --motivos`):

| Vermelho (correção) | Mudança que causou | Teste que pegou | Na lista? Motivo | Tamanho da lista |
|---|---|---|---|---|
| DS × TABR (`490301f`) | `d30f30b → 4afd477` (junção da TABR depois do DS) | `tabelas_irr_test` | sim: o teste mudou; usa `tabelas_lib.py` mudado; abre CD-0x/IR-0x mudadas | 106 de 162 |
| TABR × BEN (`1e847eb`) | `d30f30b → 4afd477` (BEN já estava na base) | `tabelas_cad_test` | sim: o teste mudou; abre CD-01…CD-07 | 106 de 162 |
| TABR × SOLO (`8245911`) | `7cd0082 → afc38fa` (junção do SOLO) | `tabelas_cad_test`, `cadc_cd02_test` | sim: abre CD-06 e as demais CD mudadas | 173 de 175 |
| CTL5 × TABR (`885a68c`) | `4afd477 → 7cd0082` (junção da CTL5) | `ctl5_test`, `ficha_pivo_test` | sim: o teste mudou; abre CD-01, IR-0x, CD-03 | 167 de 169 |
| CTL5 × SOLO (`885a68c`, item 12) | `7cd0082 → afc38fa` | `ficha_pivo_test` | sim: usa `dados_lagoa_safra.py` mudado; abre CD-03, IR-01 | 173 de 175 |
| COM × BEN (`1f83eee`) | `a676ac0 → e9670f0` (junção do COM) e `ab25ec2 → 0ad2d0d` (PV-031 no Comercial) | `comercial_fluxo_test` | sim: o teste mudou / abre COLH, EXPED, PCOM, PROD, VEN | 178 de 181 · 148 de 181 |
| CTL-4 (`78711bb`) | `853a6a8 → 4130972` | `saf_cmp_continuidade_test`, `esttest` | sim: o teste mudou / abre EST, OS | 119 de 146 |

Mudanças pequenas dão listas curtas: só um teste (`490301f`, `8245911`, `1f83eee`, `93ca16c`, `ab25ec2`) → 5 de 181 (o teste,
o conjunto fixo e `quantidade_test`, que lê os testes por glob); `885a68c` (dois testes) → 6; a largura de coluna do CD-04
(`1e847eb`) → 22 de 181; o texto do laudo no Estoque (`78711bb`) → 37 de 146; só documentação (`1f83eee → 302b26f`) → o conjunto
fixo (3). Junções de frente mudam quase todas as páginas (o motor, o cenário e o design system vão em todas), e a lista fica quase
inteira.

## Limites
- A máquina tem 4 CPUs e outras execuções usaram o navegador ao mesmo tempo (carga média entre 10 e 15 durante a medição): os
  tempos variam de uma amostra para outra; por isso a medição principal é o par alternado (antes e depois do mesmo teste, um logo
  após o outro, na mesma trava, com a ordem trocando a cada teste).
- O ganho é menor nos testes que já eram limitados pelo trabalho real do navegador (mapa com WebGL por software, telas grandes) e
  maior nos que somavam muitas esperas fixas.
- O crédito cobre o que a página agenda (timer, intervalo, rede). Um teste que dependesse de quanto tempo uma animação CSS rodou
  entre duas ações, sem timer, poderia ver outro quadro; nenhum dos 71 da bateria depende disso (71/71 iguais).
- Cache: como root, `chmod` não impede escrita; a guarda real é o manifesto conferido a cada chamada. O build não é bit a bit
  reprodutível (carimbo de hora no `canvas.json`), e é por isso que o artefato é montado uma vez e reaproveitado.
- `testes_afetados.py` é a lista para rodar primeiro, não substitui a bateria completa a cada marco (AGENTS.md §3.6).
- Esperas < 1 s nos testes ficam fixas por regra (protegem debounce e animação); são a maior parte das esperas que sobraram.
- `etapas_celular_test.py desktop` compara com `../gen37_antes/_render`; sem essa base ele falha em 3 s (igual à referência).
