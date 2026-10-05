# CONTROLE-01-D · Frente D · Aprova quem decide: ajuste de estoque, quarentena, dispensa de saldo, consumo acima da custódia e checklist da manutenção (desenho corrigido)

Severidade: S2 em D1 (ajuste), D2 (quarentena), D3 (dispensa, inclusive a alçada de 20 % que hoje só existe na tela) e D5 (consumo acima da custódia aceito sem o gestor). S3 em D4 (checklist). Nenhum é S1: nenhum dos cinco permite executar operação no campo sem aprovação.

Dano: D1: quem conta o estoque pode aprovar o próprio ajuste e esconder uma perda, e a trilha grava "Ana (gestora)" mesmo quando não foi ela. Na proposta original ainda havia uma burla: Ana registrava a contagem, declarava "Paula" no campo de contador e aprovava sem revisão posterior (executado: aj.rev vazio). D2: material em quarentena sem laudo entra no disponível e segue para as O.S. Exemplos: KCl com laudo de umidade pendente, semente sem germinação, embalagem aberta na devolução. D3: uma área sai do plano sem decisão técnica nem gerencial. Exemplo: 40 ha da OS-0421 ficam sem o fungicida porque alguém marcou a própria caixa "o agrônomo confirmou". Além disso, o comando aceita 71 ha (acima do limite de 20 % = 70 ha) sem a Direção, porque o limite só existe na tela (executado: saldo 160 → 89). D5: o consumo relatado acima da custódia baixa o lote sem aprovador, como se fosse consumo: 20 L de Fungicida A saem do F26-02 (545 → 525 L) e a trilha grava sempre "Rui (almoxarife)". D4: um clique registra como feitas todas as tarefas pendentes da manutenção (troca de óleo, filtros, graxa). O registro fica falso e o ativo volta ao campo sem o serviço.

PRD: PRD 2, papéis (l.170-187): agrônomo l.176, PCM/mecânico l.179, almoxarife l.181 ("custódia e conferência física"), qualidade e aptidão l.183. PRD 2.1 (l.191-197): acumular papéis, revisão posterior e servidor que valida a ação. DEC-2609-13 (PRD l.12227; DECISIONS.md:23): ajuste aprovado pelo gestor. RF-SUP-007 (l.2589): receber, inspecionar e liberar; documento não substitui inspeção. RF-SUP-010 (l.2592): o ajuste conserva evidência, motivo e aprovador. FO-32 (l.2350). SU-09 (l.1287-1289): limite e segregação conforme CF-02. RN-015 (l.217). RN-018 (l.218). SU-06 (l.1220-1226): responsáveis e "Liberar qualidade". PRD 42.4 (l.7081). PRD l.7083: diferença vira "ajuste auditado, sem virar consumo por subtração automática". DEMO-02 (l.4710). CMD-47 (l.2830): "alçada gerencial CF-02 e validação técnica aplicável; atividade agrícola exige decisão agronômica". AL-05 (configuracoes.py:178): "Gerencial · Ana + validação agronômica do RT; até 20 %; acima, Direção". PRD l.10047. PRD 54.2: l.8371 (não pré-marcar) e l.8373 (usuário/papel e momento). FO-30 (l.2349): resposta sem default positivo. PRD 47.5 (l.7738). AGENTS §4: servidor é a autoridade, fórmula e regra num lugar só, trava só com dano nomeado. Padrões adotados para as decisões do proprietário, que ele pode mudar: (2) o gestor aprova o ajuste e o consumo acima da custódia, e se for a mesma pessoa que registrou a contagem fica a revisão posterior; (3) a entrada de Controle fica para depois. A v3.10 (CMD-50, em revisão) põe a conciliação com o almoxarife e precisa refletir o padrão (2).

Arquivos: /home/user/sp-tab5/tools/prototipo/v37/gen37/g2lib.js, /home/user/sp-tab5/tools/prototipo/v37/gen37/ui37.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/cenario.js, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/processo_estoque.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/processo_os.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/dados_manutencao.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/maquinas.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/esttest.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/est_cenario_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/osacoes.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/verif_os.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/consumo_divergente_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/est_fix1_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/ma_correcoes_om_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/ma_correcoes_pm_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/ma_planos_test.py, scratchpad/ctl/d_cet/frente_d_corrigida.diff, scratchpad/ctl/d_cet/corrige.py, scratchpad/ctl/d/patch.py, scratchpad/ctl/d_cet/monta.py, scratchpad/ctl/d_cet/teste_d2.js, scratchpad/ctl/d_cet/stubs_antes2.js, scratchpad/ctl/d_cet/verde2.txt, scratchpad/ctl/d_cet/vermelho2.txt, scratchpad/ctl/d_cet/proposta_original2.txt, scratchpad/ctl/d_cet/ataque.js, scratchpad/ctl/d_cet/ataque2.js, scratchpad/ctl/d_cet/a3_atual.js, scratchpad/ctl/d_cet/os0420.js, scratchpad/ctl/d_cet/ataques_saida.txt, scratchpad/ctl/d_cet/tela.py, scratchpad/ctl/d_cet/tela_est2.js, scratchpad/ctl/d_cet/tela_os2.js, scratchpad/ctl/d_cet/tela_ma.js, scratchpad/ctl/d_cet/sintaxe.py, scratchpad/ctl/d_cet/v37q

# CONTROLE-01 · Frente D: aprova quem decide (desenho corrigido)

**Base:** protótipo `884620c` (sp-tab5, `claude/v44-tabelas-05`), PRD v3.9, `DECISIONS.md` e `AGENTS.md`.

**Executado** (node 22 e python 3.11, sem navegador):
- a reprodução no código atual;
- a proposta original em `ctl/d/v37p`;
- a proposta corrigida em `ctl/d_cet/v37q`, que é `v37p` mais `ctl/d_cet/corrige.py`, onde cada troca exige um trecho exato e único.

Tudo isso roda fora do repositório.

**Não feito:**
- nenhum teste em navegador;
- nenhuma edição no repositório. O HEAD continua `884620c` e nenhum arquivo rastreado mudou.

## Acordo curto (AGENTS 3.4)
```text
ID / resultado útil / persona: CONTROLE-01-D · cada decisão de controle é registrada por quem tem o papel · gestora e agrônoma (Ana), almoxarife, mecânico
Requisitos do PRD e fora do escopo: R-D0..R-D5 abaixo · fora: liberação da O.S. (padrão 1, Frente F), Compra/Direção, entrada de Controle (padrão 3)
Autor / revisor / integrador: Claude / Codex / Codex
Base (commit ou hashes) / arquivos sob responsabilidade: 884620c · g2lib.js, ui37.py, cenario.js, dados_manutencao.py, areas/processo_estoque.py, areas/processo_os.py, areas/maquinas.py
Aceite e comando de verificação: GEN=<gen37> python3 ctl/d_cet/monta.py teste_d2.js → 71/71 · tela.py (EST 18/18, OS 7/7, MA-04 4/4) · sintaxe.py → 144 telas, 0 erro · navegador (§5.4)
Estado / impedimento / próximo passo: corrigido e executado em cópia · sem impedimento · aplicar ctl/d_cet/frente_d_corrigida.diff numa branch e rodar a bateria do navegador
```

## 0. Premissas (corrigidas)
- **Menu lateral:** "Trocar perfil de demonstração ▾" é texto fixo (`ui37.py:218-222`), sem nenhum `onClick`. Toda tela interna nasce com `perfil='Ana · Gestora'` (`ui37.py:258`).
- **Índice:** o desenho dizia que "Entrar como" abre a tela inicial do perfil, mas não abre nada. Os 8 cartões (`indice.py:8-15`) são `<div>`, porque `_ab` não cria link quando o destino está no menu ou nos ocultos (`indice.py:56, 63-68`). Cada cartão só mostra "começa em: …" e nada fica gravado.
- **Consequência:** nenhuma decisão sabe quem age. A proposta cria o mínimo necessário:
  - um seletor no menu lateral, com uma única lista de perfis (`G2_PERFIS` em `g2lib.js`);
  - a escolha gravada no navegador (`safrion.perfilDemo`);
  - comandos que recebem o ator.
- **Software real:** o ator vem da sessão no servidor (PRD 2.1, l.197). O índice já avisa que a troca "não comprova segurança" (`indice.py:84`).

## 1. Problema reproduzido (executado no código atual)

Saída já registrada pela frente (`ctl/d/repro_saida.txt`). Rodei de novo e só difere pela hora.
```
=== D1 · ajuste: qualquer um aprova; a trilha grava sempre "Ana (gestora)" ===
msg: Ajuste INV-2611 (AJ-71) aprovado por Ana (gestora): −20 L no lote G26-14. Físico 1.200 L → 1.180 L.
depois: físico 1180 · aprovador gravado no ajuste: (nenhum campo) · movimento quem = Ana (gestora)
=== D2 · quarentena liberada sem laudo ===
antes: quarentena 10000 · disponível 50000 → depois: quarentena 0 · disponível 60000 · doc = (nenhum laudo)
=== D3 · dispensa sem validação de quem tem o papel ===
saldo 160 → 120 · gravado: "validação agronômica registrada" · quem validou: (não gravado)
=== D4 · "Marcar pendentes como feitas" ===
OM-0234 · 5 tarefas · msg: 5 tarefas marcadas como feitas. · quem/quando por tarefa: [{},{},{},{},{}]
```

Novos casos, executados com `ctl/d_cet/a3_atual.js` e `ctl/d_cet/ataque2.js` sobre o código atual:
```
=== D3b · limite AL-05 só na tela ===
comando com 71 ha na OS-0421 (limite 20 % de 350 = 70 ha) → Dispensados 71 ha da OS-0421 · realizado 190 ha preservado · saldo 89 ha.
=== D5 · consumo acima da custódia (padrão 2: aprova o gestor) ===
fechar turno (85 L informados, 65 L em custódia) → Consumo em conferência: Fungicida A 85 L relatados, 65 L em custódia · Rui (almoxarife) concilia.
prévia → Baixa 85 L na OS-0421: 65 L da custódia de Marcos · 20 L saem do lote F26-02 (livre).
aceite sem ator → CC-301 aceito: Fungicida A 85 L baixados na OS-0421 · 20 L regularizados do lote F26-02.
lote F26-02: físico 545 → 525 L · disponível 480 → 460 L · k.por = Rui (almoxarife)
```

Ataques à proposta original (`ctl/d_cet/ataques_saida.txt`):
- **Burla da revisão posterior:** Ana registra a contagem, declara "Paula" como contadora e aprova. Resultado: `aj.rev = ''`, ou seja, nenhuma revisão.
- **Alçada de 20 % só na tela:** o comando aceita 71 ha (saldo 160 → 89).
- **Consumo acima da custódia:** o aceite sem ator baixa 20 L e grava Rui.
- **Revisão da quarentena inalcançável:** recebimento e devolução gravam sempre `'Rui (almoxarife)'` (`cenario.js:87, 98`), e só o gestor libera. A comparação nunca dispara.

**Onde está no código:**
- **Ajuste:** `processo_estoque.py:482`; nome fixo em `cenario.js:113` e `processo_estoque.py:230, 301`.
- **Quarentena:** `cenario.js:101-103`; `processo_estoque.py:366, 554-559`.
- **Dispensa:**
  - caixa marcada por quem dispensa (`processo_os.py:921, 643, 650`);
  - texto genérico gravado (`processo_os.py:387`);
  - limite de 20 % só na tela (`processo_os.py:648`), com `LIM_DISP` fora do núcleo (`processo_os.py:426`; o `JS_NUCLEO` vai de l.209 a l.421).
- **Consumo:** `cenario.js:210-226`; `k.por` fixo (`cenario.js:212, 225`; `CEN_CONC_RESP`, l.142); botões em `processo_estoque.py:194-195, 568-569`.
- **Checklist:** `maquinas.py:461-462, 513`.

## 2. Regras (numeradas e testáveis)

**R-D0. Decisão com papel.**
- Todo comando de decisão recebe o ator. O papel pode ser um nome ou uma lista, e com lista todos os papéis são exigidos.
- Sem o papel, o comando recusa com "<ação>: decisão de <quem tem o papel>. Nada foi alterado." O cenário não muda, porque `cenMudar` é atômico. A recusa vale também quando o comando é chamado direto.
- A revisão posterior só existe onde é alcançável: no ajuste, quando quem aprova é quem registrou a contagem.
- **Dano evitado:** decisão em nome de quem não decidiu.
- **Fonte:** PRD 2.1 l.195-197; AGENTS §2 e §4.

**R-D1. Ajuste de inventário.**
- Só o papel gestor aprova.
- Fica gravado: aprovador, hora, o contador declarado e quem registrou a contagem (`reg`, o perfil que salvou).
- Revisão posterior: se quem aprova é quem registrou, a decisão vale e fica gravado "revisão posterior pendente (Ana registrou a contagem e decidiu)". Isso aparece no ajuste, no movimento, na mensagem e na linha.
- O contador declarado é um campo livre (`processo_estoque.py:117`) e não decide a revisão. No software, quem registra é a sessão.
- "Recontar" continua para todos: recusa o ajuste sem mudar o saldo e limpa o `reg`.
- A lista de contadores não muda.
- **Dano evitado:** perda escondida por quem contou; saldo alterado sem aprovador.
- **Fonte:** DEC-2609-13 (l.12227); RF-SUP-010 (l.2592); FO-32 (l.2350); SU-09 (l.1287-1289); padrão (2).

**R-D2. Liberar quarentena.**
- Exige o nº do laudo ou do relatório de inspeção, sem espaços em branco, e o papel gestor.
- Fica gravado no movimento: laudo, quem e hora.
- Sem laudo ou sem o papel, o lote continua bloqueado. Repetir não soma.
- Não há revisão posterior: quem bloqueia é sempre o almoxarife que recebe (`cenario.js:87, 98`), e quem libera é a gestora. Já há segregação.
- **Dano evitado:** material impróprio no disponível e entregue às O.S.
- **Fonte:** RN-015 (l.217); RF-SUP-007 (l.2589); SU-06 (l.1220-1226); PRD 42.4 (l.7081); DEMO-02 (l.4710).
- **Padrão adotado por nós:** o PRD 2 (l.183) separa a aptidão do lote (qualidade) da conferência física (almoxarife, l.181), e a demonstração não tem ninguém de qualidade. Por isso a gestora libera. O proprietário pode mudar.

**R-D3. Dispensar saldo de O.S. agrícola.**
- Exige a alçada gerencial e a validação agronômica (CMD-47, l.2830; AL-05, `configuracoes.py:178`). O perfil precisa dos dois papéis: hoje só Ana.
- A caixa de marcar sai. Fica gravado "decisão gerencial e validação agronômica de Ana (gestora e agrônoma) às hh:mm" e também `dispPor` e `dispEm`.
- O limite de 20 % da área passa para o comando (`LIM_DISP` no `JS_NUCLEO`, uma regra só). Acima dele: "71 ha = 20,3 % acima de 20 % · exige Direção." O limite é acumulado e vale para a chamada direta.
- **Acúmulo:** não há revisão posterior. Até 20 % não existe segunda decisão (`processo_os.py:642`), e acima disso a Direção já é exigida.
- **Dano evitado:** área tirada do plano sem decisão técnica e gerencial, ou acima da alçada.

**R-D4. Checklist da manutenção** (sem mudança em relação ao desenho original).
- Sem ação em massa: cada tarefa é respondida uma a uma, e fica gravado quem respondeu e a hora.
- Concluir continua exigindo todas as tarefas respondidas (`dados_manutencao.py:417`).
- Ninguém fica impedido de responder: a trava aqui seria sem dano. O dano é o "feito" em massa, e a resposta individual com autor resolve.
- **Fonte:** PRD 54.2 l.8371 e l.8373; FO-30.

**R-D5. Consumo acima da custódia (nova; padrão 2).**
- Aceitar um caso em que parte sai do lote (excedente da custódia maior que 0) é decisão do gestor.
- Aceitar o que a custódia cobre, ou "Recusar relato" (sem efeito no lote), continua aberto e grava quem decidiu.
- O caso (`k.por`) e os dois movimentos gravam quem decidiu. Chamada sem ator, como nos testes de navegador, grava o conciliador de sempre.
- Na tela, quem não é gestor vê "aceite: Ana (gestora)" no lugar de "Aceitar consumo".
- **Dano evitado:** material sai do lote como "consumo" sem aprovador; trilha com o nome errado.
- **Fonte:** padrão (2); PRD l.7083; RN-018 (l.218).
- **Acúmulo:** não se aplica. Quem relata é o operador (Marcos).

**Perfis de demonstração.** A lista única fica em `g2lib.js`. Os rótulos gravados são os mesmos das telas: "Ana (agrônoma)" aparece 11 vezes em `processo_os.py`, 3 em `mobile.py` e 1 em `inicio.py`, e é o `OS_AGRO` da Frente F.

| Perfil (texto do seletor) | Papéis gravados | Fonte no código |
|---|---|---|
| Ana · Gestora e agrônoma RT | gestora; agrônoma | `configuracoes.py:8, 104`; `processo_os.py:87` |
| Caio · PCP | PCP | `configuracoes.py:105`; `indice.py:10` |
| Rui · Almoxarife | almoxarife | `cenario.js:77`; `indice.py:12` |
| Paula · Almoxarife | almoxarife | `processo_estoque.py:23` |
| Zé · Mecânico | mecânico | `maquinas.py:221`; `mobile.py:893` |

Ana é o perfil padrão, como hoje. Beto fica de fora porque é "Agrônomo(a)" em `indice.py:9` e "Operador" em `configuracoes.py:109`.

## 3. Mudança de código por arquivo

O diff completo contra `884620c` está em `ctl/d_cet/frente_d_corrigida.diff`. Ele é `ctl/d/patch.py` mais `ctl/d_cet/corrige.py`.

- **`g2lib.js` (+13):**
  - `G2_PERFIS`, `g2perfil()` (com `localStorage` e memória de reserva), `g2papel(p, papel|lista)` (todos exigidos), `g2ator(p, papel|lista)` ("Ana (gestora)", "Ana (gestora e agrônoma)"), `g2quem` e `g2mesma`;
  - no `g2navvals`: `perfil_k`, `perfil_ini`, `perfil_opts` e `perfil_set` (grava e mostra o aviso), mais um ouvinte de `storage`.
- **`ui37.py:218` (+6):** quando `perfil=='Ana · Gestora'`, mostra um `<select aria-label="Trocar perfil de demonstração">` com `sc-for`, no mesmo padrão de `engine.py:1273`. Portal, backoffice e onboarding continuam fixos.
- **`cenario.js` (+24/−12):**
  ```diff
  + function cenExige(ator,papel,acao){ if(!g2papel(ator,papel)) throw new Error(acao+': decisão de '+g2quem(papel)+'. Nada foi alterado.'); return g2ator(ator,papel); }
  + function cenRevisao(ator,autor,fato){ return g2mesma(ator&&ator.k,autor)?'revisão posterior pendente ('+ator.k+' '+fato+' e decidiu)':''; }
  + cenLiberarQuarentena(c,key,laudo,ator): cenExige(ator,'gestor',…); sem laudo → erro; cenMov(…,quem,doc)            // sem revisão
  + cenAprovarAjuste(c,id,aprovar,ator): quem=cenExige(ator,'gestor',…); aj.por, aj.em; aj.rev=cenRevisao(ator,aj.reg,'registrou a contagem')
  + cenConciliar(c,id,aceitar,motivo,ator): quem = (aceitar && !p.erro && p.falta>1e-9) ? cenExige(ator,'gestor','Aceitar '+falta+' '+un+' acima da custódia ('+k.id+')')
  +                                              : (ator ? g2ator(ator,'almoxarife') : CEN_CONC_RESP); k.por=quem; movimentos com quem
  ```
- **`areas/processo_estoque.py` (+45/−31):**
  - `estContar(…,ator)` grava `aj.reg` e `rec.reg`;
  - `estRecontar` limpa o `reg`; no INV-2609, `aj.reg=rec.reg`;
  - `ESAVE.g_cnt` repassa `g2perfil()` (l.346);
  - `estAprovar(c,inv,ator)` usa `aj.por` e `aj.rev` na mensagem;
  - `emovTxt` usa `m.quem`, `m.doc` e `m.rev` (o `rev` só no ajuste);
  - painel `libq` com o campo `#est-laudo`, "Liberar com o laudo", "Manter bloqueado" e erro em `role=alert`;
  - `elotRow(…,GEST)`: sem o papel, a célula mostra "aguarda laudo · Ana (gestora) libera";
  - contagens: sem o papel, "aprova: Ana (gestora)"; com acúmulo, a revisão aparece na Situação;
  - `ecfCel(k,c,ask,GEST)` (l.194) e as duas chamadas: com excedente e sem o papel, "aceite: Ana (gestora)";
  - `v.k3` (l.527): "Rui (almoxarife) confere ou recusa o relato; Ana (gestora) aceita o excedente";
  - `cfok` e `cfr` repassam `g2perfil()`;
  - **`CONTADORES` não muda.**
- **`areas/processo_os.py` (+15/−13):**
  - `LIM_DISP` sai de l.426 e vai para antes de `osc_dispensar`, dentro do núcleo;
  - `osc_dispensar(c,id,n,mot,ator)` chama `cenExige(ator,['gestor','agronomo'],…)` primeiro e confere o limite acumulado de 20 %;
  - em `osWork`, `DSP=['gestor','agronomo']`; quem não tem os papéis vê o `pan_dispQ`, e o formulário mostra o `pan_dval` em texto;
  - em `pan_dissave`, saem as verificações de 20 % (l.648) e da caixa (l.650); o erro do comando aparece no painel por `osRun` (l.293-294);
  - o `<input type="checkbox">` sai (l.921).
- **`dados_manutencao.py:404` (+3/−1) e `areas/maquinas.py` (+5/−7):** iguais ao desenho original (`manResp(…,ator)` grava `t.por` e `t.em`; saem `pan_hasTodas`, `pan_todas` e o botão).

**Total:** 7 arquivos, +111/−64 (`git diff --numstat` executado em `v37q`).

## 4. Textos de tela
- **Menu lateral:** seletor "Trocar perfil de demonstração" com a legenda "Perfil de demonstração". Ao trocar: "Perfil de demonstração: Caio · PCP (não é segurança de acesso)."
- **Estoque, contagens:**
  - para quem não é gestor: "aprova: Ana (gestora)";
  - comando forçado: "Aprovar o ajuste INV-2611: decisão de Ana (gestora). Nada foi alterado.";
  - aprovado: "Ajuste INV-2611 (AJ-71) aprovado por Ana (gestora): −20 L no lote G26-14. Físico 1.200 L → 1.180 L.";
  - quando quem aprova registrou a contagem, a mensagem acrescenta "Fica revisão posterior pendente (Ana registrou a contagem e decidiu).";
  - trilha: "ajuste de inventário INV-2611 aprovado por Ana (gestora): −20 L".
- **Estoque, quarentena:**
  - para quem não é gestor: "aguarda laudo · Ana (gestora) libera";
  - painel: "Liberar 10.000 kg do lote K26-11 (KCl 60%): informe o laudo que aprova o material.";
  - erro: "Informe o nº do laudo ou relatório de inspeção do lote K26-11. Sem laudo o lote continua bloqueado.";
  - sucesso: "10.000 kg do lote K26-11 liberados com o laudo LAB-0917 por Ana (gestora). Disponível de KCl 60%: 50.000 kg → 60.000 kg.";
  - trilha: "quarentena liberada com o laudo LAB-0917 por Ana (gestora): 10.000 kg passam a disponível".
- **Estoque, consumo:**
  - para quem não é gestor, com excedente: "aceite: Ana (gestora)" e "Recusar relato";
  - comando forçado: "Aceitar 20 L acima da custódia (CC-301): decisão de Ana (gestora). Nada foi alterado.";
  - no recibo do app (`mobile.py:491`): "Aceito por Ana (gestora) · …".
- **O.S.:**
  - para quem não tem os papéis: "Dispensar saldo: decisão de Ana (gestora e agrônoma).";
  - formulário: "Decisão gerencial e validação agronômica: Ana (gestora e agrônoma), registradas ao confirmar.";
  - acima do limite: "71 ha = 20,3 % acima de 20 % · exige Direção.";
  - sucesso: "Dispensados 40 ha da OS-0421 por Ana (gestora e agrônoma) · realizado 190 ha preservado · saldo 120 ha.";
  - gravado na ordem: "Saldo de 40 ha dispensado: <motivo> · decisão gerencial e validação agronômica de Ana (gestora e agrônoma) às hh:mm. Realizado de 190 ha preservado."
- **MA-04, em cada tarefa:** "por Zé (mecânico) às hh:mm".

## 5. Testes

### 5.1 Unitário, sem navegador (executado)
- **Comando:** `GEN=<gen37> python3 ctl/d_cet/monta.py teste_d2.js`
- **Proposta corrigida (`v37q`):** **71 ok, 0 falhas** (`verde2.txt`).
- **Proposta original (`v37p`):** 45 ok, 26 falhas (`proposta_original2.txt`). Falham a revisão pelo registrante, o limite no comando, o D5 e os rótulos.
- **Código atual, com `stubs_antes2.js`:** 23 ok, 47 falhas (`vermelho2.txt`).

Correção de uma afirmação do desenho original: não é verdade que "todos os NEGATIVOS falham no código atual". Cinco passam nos dois porque são guardas de regressão: repetir a aprovação, repetir a liberação, OS-0424 em Liberadas, 4 de 5 tarefas respondidas e "Não feito" sem motivo.

| Regra | Positivo | NEGATIVO |
|---|---|---|
| R-D0 | Perfil padrão é Ana; perfil desconhecido volta a Ana. `g2quem`: "Ana (gestora)", "Ana (agrônoma)", "Ana (gestora e agrônoma)" e "Rui (almoxarife) ou Paula (almoxarife)". Trocar para Caio grava e avisa | Caio não tem os dois papéis da dispensa |
| R-D1 | INV-2611: Ana aprova e o físico vai de 1.200 para 1.180 L, com `aj.por`, `aj.em` e contador Paula. Ana registra 1.185 L (declarando Paula) e aprova: 1.185 L e "revisão posterior pendente (Ana registrou a contagem e decidiu)" no ajuste, no movimento, na mensagem e na trilha. Rui registra e Ana aprova: sem revisão. INV-2609: Ana aprova e o MAP vai de 90.000 para 89.400 kg. Recontar limpa o `reg`. Contadores continuam Paula e Rui | Rui, Paula, Caio e chamada sem ator: o físico segue 1.200 L. Repetir não aplica de novo. Rui no INV-2609 não cria ajuste |
| R-D2 | K26-11 com LAB-0917: disponível de 50.000 para 60.000 kg, com laudo e quem no movimento e sem campo `rev`. Devolução bloqueada de 10 L na REQ-035: o F26-02 fica com físico 555, quarentena 10 e disponível 480; com INSP-0042, o disponível vai a 490 L. Recebimento S58-0926 grava Rui | Rui, Paula e Caio com laudo: o disponível segue 50.000 kg. Laudo vazio, só espaços ou ausente: segue bloqueado. Repetir não soma: segue 60.000 kg. Rui na devolução: segue 480 L |
| R-D3 | OS-0421: Ana dispensa 40 ha e o saldo vai de 160 para 120; `dispPor` e hora gravados. Limite exato 40 + 30 = 70 ha: aceita, e o saldo fica em 90 | Caio, Rui, Zé e chamada sem ator: o saldo segue 160. Comando com 71 ha: "exige Direção" e o saldo segue 160. Acumulado 40 + 31 = 71 ha: "exige Direção" e o saldo segue 120. OS-0424: "não está em execução" |
| R-D5 | CC-301 (85 L relatados, 65 L em custódia): Ana aceita e o F26-02 vai de 545 para 525 L; o caso grava "Ana (gestora)" e os movimentos "Ana (gestora) → Marcos · regularização CC-301" e "Ana (gestora) · aceite CC-301". Coberto pela custódia (75 L, depois de entregar mais 10 L): Rui aceita. Rui recusa e fica gravado Rui; recusa sem ator grava o conciliador de sempre | Rui, Caio e chamada sem ator não aceitam os 20 L acima da custódia: o F26-02 segue 545 L e o caso segue "Em conferência" |
| R-D4 | OM-0234: cada resposta grava quem e a hora. Respondidas as 5, uma a uma, a ordem vai para "Em conferência" | `pan_todas` não existe mais. 4 de 5 respondidas não concluem. "Não feito" sem motivo não conclui. Desmarcar apaga quem e hora |

### 5.2 Lógica das telas construídas, rodada em node sem navegador (executado)
Rodado com `ctl/d_cet/tela.py` sobre `v37q/project`:
- **EST (`tela_est2.js`), 18/18:**
  - os 12 casos do desenho original;
  - 6 casos do D5: com Rui, a linha da REQ-035 mostra "aceite: Ana (gestora) | Recusar relato", o resumo diz quem confere e quem aceita, e a chamada direta mantém 545 L;
  - Ana aceita e o lote vai a 525 L;
  - coberto pela custódia, Rui vê "Aceitar consumo".
- **OS (`tela_os2.js`), 7/7:** o erro de 71 ha vem do comando e aparece no painel, com o saldo em 160.
- **MA-04 (`tela_ma.js`), 4/4.**
- **Sintaxe (`sintaxe.py`):** os scripts das 144 telas compilam, sem nenhuma `const` duplicada (`LIM_DISP` mudou de lugar; o Mapa inclui o `JS_NUCLEO`).

### 5.3 Testes existentes rodados em `v37q` (executado)
- `carencia_test.py unit`: 50/50.
- `mip_unit_test.py`: 34/34.
- `quantidade_test.py`: 14/14.
- `rend_multiconjuntos_unit.py`: 106/106.
- `build.py`: "144 artboards". O seletor aparece em 106 telas; ficam sem ele BO, PT, ON, MB, Main e OS-0424-app/ficha.

### 5.4 Navegador (especificado, não executado)
Antes de rodar, é preciso reconstruir `project/` com `build.py`. Cada execução usa um perfil novo do Chrome (`est_lib.py:3`), então o perfil começa em Ana.

- **`esttest.py` parte 1 (l.47-49):**
  1. Clicar "Liberar após inspeção" no K26-11.
  2. Clicar "Liberar com o laudo" com o campo vazio: espera-se "Sem laudo o lote continua bloqueado" e o KCl ainda com 10.000 kg bloqueados.
  3. Preencher `setv('est-laudo','LAB-0917')` e clicar "Liberar com o laudo": espera-se 60.000 kg disponíveis.
  4. Na seção Movimentos: Documento LAB-0917 e Quem "Ana (gestora)".
- **`esttest.py` parte 3 (l.125):** acrescentar a verificação de que o aviso contém "Fica revisão posterior pendente (Ana registrou a contagem e decidiu)."
- **`esttest.py` parte 4 (nova):**
  1. Gravar `safrion.perfilDemo='Rui'`. O INV-2609 mostra "aprova: Ana (gestora)" e não mostra "Aprovar ajuste"; o K26-11 mostra "aguarda laudo · Ana (gestora) libera".
  2. Ainda como Rui, contar o INV-2611 (contador Paula, 1180, com causa).
  3. Trocar para Ana pelo seletor (`setv('[aria-label="Trocar perfil de demonstração"]','Ana')`) e clicar "Aprovar ajuste": o aviso não fala de revisão e o G26-14 fica com 1.180 L.
- **`est_cenario_test.py:58-60`:** no O26-05, o mesmo fluxo com o laudo INSP-0042. Os números não mudam: 10 L e 330 L.
- **`osacoes.py`:**
  - l.80 e l.96: tirar `marca('Validação agronômica')`;
  - **l.88: tirar também o `btn('Confirmar dispensa')`**, senão a dispensa acontece ali, e trocar a verificação por `'Decisão gerencial e validação agronômica: Ana (gestora e agrônoma), registradas ao confirmar.' in pan()`;
  - l.89: só `btn('Confirmar dispensa')`;
  - os textos de l.82, l.90 e l.97 não mudam (executado `os0420.js`: "70 ha = 70 % acima de 20 % · exige Direção.");
  - novo caso: com o perfil Caio, a OS-0421 mostra "Dispensar saldo: decisão de Ana (gestora e agrônoma)." e não mostra o botão.
- **`verif_os.py:82, 93`:** tirar `marca('Validação agronômica')`.
- **`consumo_divergente_test.py`:**
  - l.68: o texto esperado passa a ser "· Rui (almoxarife) confere ou recusa o relato; Ana (gestora) aceita o excedente";
  - novo caso antes de l.86: com o perfil Rui, a linha mostra "aceite: Ana (gestora)" e não mostra "Aceitar consumo"; depois volta para Ana.
- **`ma_correcoes_om_test.py:45`, `ma_correcoes_pm_test.py:41` e `ma_planos_test.py:58`:**
  - trocar "Marcar pendentes como feitas" por um auxiliar que clica "Feito" em cada `aside [role=group]` ainda sem `aria-pressed=true`;
  - verificar que aparece "por Ana (gestora) às".

### 5.5 Cliques e digitação (especificado, a medir no navegador)

| Fluxo | Hoje | Proposta | Motivo da diferença |
|---|---|---|---|
| Ajuste | 1 clique | 1 clique | igual |
| Quarentena | 2 cliques | 2 cliques + 1 campo | o laudo é a evidência (RN-015) |
| Dispensa | 2 cliques + caixa + motivo | 2 cliques + motivo | um clique a menos |
| Consumo, para a gestora | 2 cliques | 2 cliques | igual |
| Checklist da OM-0234 | 1 clique | 5 cliques | PRD 54.2 e FO-30 proíbem pré-marcar |

## 6. Testes existentes que mudam de expectativa
- **Liberação da quarentena:** `esttest.py:47-49`, `est_cenario_test.py:58`, `est_repro.py:22` e `verif_est2.py:15`.
- **Dispensa:** `osacoes.py:80, 88-89, 96` e `verif_os.py:82, 93`.
- **Checklist:** `ma_correcoes_om_test.py:45`, `ma_correcoes_pm_test.py:41` e `ma_planos_test.py:58`.
- **Novo:** `consumo_divergente_test.py:68`.
- **Sem mudança:**
  - `est_fix1_test.py:56`, que espera os contadores `['Paula (almoxarife)', 'Rui (almoxarife)']`. O desenho original quebrava este teste ao pôr Ana na lista e não o listava;
  - `est_fix1_test.py:38, 48, 52`;
  - `esttest.py` parte 3: nenhuma verificação exata do aviso;
  - `est_cenario_test.py:71-73`;
  - `consumo_divergente_test.py:86-96, 107, 127, 141-143`: Ana aceita pela tela, l.96 repete depois de aceito, e a recusa sem ator grava "Rui (almoxarife)";
  - `app_mb03_turno_test.py:22`;
  - `acao_unica_test.py` 13;
  - `cftest.py:70`.

## 7. Riscos de regressão
1. **Largura do seletor:** "Ana · Gestora e agrônoma RT" pode cortar no select de 170 px. Verificar com `widthcheck`, `verif_largura` e `verif_overflow`, também com o menu recolhido. Se cortar, encurtar para "Ana · Gestora e RT".
2. **Liberação da O.S. sem perfil:** com o perfil Rui, a O.S. ainda deixa "Liberar para execução" (`processo_os.py:336, 415`). Isso é o padrão (1), da Frente F, que deve usar `cenExige(ator,'agronomo')` no CMD-42. Os rótulos já batem: "Ana (agrônoma)" é o `OS_AGRO` em `ctl/fF/processo_os.py.diff`. Até lá, o roteiro do proprietário não troca de perfil na O.S.
3. **Revisão no fluxo padrão:** quando Ana registra e aprova, aparece a revisão posterior. É a regra (PRD 2.1). Para ver uma aprovação limpa, conte como Rui ou Paula.
4. **Dependência de `g2lib.js`:** `cenario.js` chama `g2lib` só no momento da chamada. Todas as telas carregam `G2LIB` antes de `EXTRAJS` (`engine.py:1449`). A carência (sem `g2lib`) passou 50/50, e `cenConciliar` só chama `g2ator` quando recebe o ator.
5. **Integração com as frentes A, B e F:**
   - nenhuma toca `cenConciliar` (conferido em `b/v37p`, `b_cet/v37q` e `fF/v37`);
   - em `processo_os.py`, a B muda l.238-241, 347-349 e 417, e a F muda l.150-617, enquanto a D muda l.381-388, 426, 629-651 e 908-921;
   - em `maquinas.py`, a F muda l.163-700 fora das linhas 452-513 da D;
   - não há linha em comum. Integrar por rebase e rodar `teste_d2.js` de novo.
6. **Cenário salvo no navegador:** os campos novos (`aj.por`, `aj.reg`, `rec.reg`, `mov.doc`, `mov.rev`, `t.por`, `osc.dispPor`) são só acréscimos.
7. **Restaurar demonstração:** não volta o perfil para Ana.
8. **Lote vencido:** a trava continua só na tela (`processo_estoque.py:557`). É uma lacuna anterior.
9. **SU-09:** a tela oculta, fora do menu (`ui37.py:33-41`), ainda oferece "Aprovar ajuste" sem papel (`suprimentos.py:1081-1104`). É maquete com estado próprio.
10. **Índice:** o texto ainda cita perfis que não estão no seletor (Beto, Marcos, Dora) e não aponta o seletor (S4).

## 8. Tamanho
- **Fonte:** 7 arquivos, +111/−64.
- **Testes:**
  - runner `monta.py` com cerca de 35 linhas;
  - `aprova_quem_decide_unit.js`, igual a `teste_d2.js`, com cerca de 130 linhas;
  - opcional: `tela.py`, os 3 roteiros e `sintaxe.py`, cerca de 95 linhas;
  - ajustes de navegador, cerca de 55 linhas.

## 9. Fora do escopo
- O ato de "revisar" a revisão posterior fica para a entrada de Controle (padrão 3).
- O laudo reprovado e a destinação do lote.
- As respostas do PRD 54.2 (Conforme / Não foi possível verificar).
- A Compra e a Direção.
- A liberação da O.S. com aprovado por e liberado por (padrão 1).
- O "Cancelar sem execução" (CMD-46), que não estava na auditoria.

## Contestações

**Aceitas:**
1. **Burla da revisão posterior no ajuste** (executada): Ana declarava "Paula" e aprovava sem revisão. Agora a revisão compara quem aprova com quem registrou a contagem (o perfil).
2. **Regressão não listada:** pôr "Ana (gestora)" nos contadores quebrava `est_fix1_test.py:56`. A mudança sai, e o acúmulo aparece pelo registrante.
3. **Revisão da quarentena inalcançável:** recebimento e devolução gravam sempre Rui (`cenario.js:87, 98`), e só a gestora libera. Saiu, porque era código morto.
4. **Limite de 20 % só na tela** (executado: o comando aceitava 71 ha). Passou para o comando, numa regra só, e saiu da tela (`processo_os.py:648`).
5. **CMD-47 e AL-05 pedem alçada gerencial e validação agronômica,** e o desenho exigia só agrônomo. Agora exige os dois papéis. Na demonstração nada muda, porque Ana tem os dois.
6. **Rótulo "Ana (agrônoma RT)" divergia** das 15 ocorrências de "Ana (agrônoma)" nas telas da O.S., do app e do Mapa, e da Frente F. Agora é "agrônoma".
7. **O padrão (2) também cobre o consumo acima da custódia,** e o desenho o omitia (executado: 20 L saíam do lote sem gestor, com Rui na trilha). Entrou como R-D5.
8. **Afirmação falsa:** "todos os NEGATIVOS falham no código atual". Cinco são guardas de regressão e passam nos dois.
9. **Premissa do índice:** "Entrar como" não abre tela nenhuma; os cartões não têm link (`indice.py:63-68`).
10. **Roteiro de `osacoes.py:88` ambíguo:** se só a verificação for trocada, a dispensa acontece na l.88 e a l.89 falha. Ficou especificado: tirar também o clique.
11. **`consumo_divergente_test.py:68`** muda e entrou na lista.

**Recusadas:**
1. **Deixar o almoxarife liberar a quarentena com laudo** (o SU-06 o lista como usuário). O PRD 2 separa conferência física (l.181) de aptidão (l.183). Quem recebe não deve liberar o que bloqueou, e a trava protege estoque. Fica a gestora, como padrão nosso.
2. **Exigir o papel de mecânico para responder o checklist.** Seria trava sem dano. O dano é o "feito" em massa, e a resposta individual com autor e hora resolve. A gestora pode registrar o que o mecânico relatou (PRD 2.1).
3. **Restringir "Recontar" e "Recusar relato" ao gestor.** Nenhum dos dois muda o saldo, a contagem seguinte revela a diferença e o registro diz quem fez.
4. **Revisão posterior no consumo.** É inalcançável: quem relata é o operador (Marcos).
5. **Levar a trava de lote vencido para o comando.** É uma lacuna anterior e fica como risco 8.
6. **Tirar o "Manter" repetido na célula do lote.** É polimento (S4) e não muda o controle.
7. **Fazer o índice gravar o perfil, ou mudar o texto dele.** Não é essencial ao controle; fica como risco 10.
8. **Exigir perfil na liberação da O.S.** É o padrão (1), da Frente F; a dependência fica no risco 2.
9. **Corrigir o SU-09.** É uma tela oculta, de maquete; fica no risco 9.
