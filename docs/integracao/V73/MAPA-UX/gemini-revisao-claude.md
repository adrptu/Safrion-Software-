# MAPA-UX · Revisão do Claude da consolidação Gemini G1–G3 (Codex)

- **O que se revisa:** a consolidação do Codex sobre a consulta única ao Gemini.
  - Commit `87e524e0392b176ed0920660f718b947d88d44c4`, branch `codex/mapa-avaliacao-20261016`, pasta `docs/integracao/V73/MAPA-UX/codex/gemini/`: `pacote.txt`, `parecer.json` e `consolidacao-codex.md` (citada como "cons. l.N").
  - Comentário do Codex no PR #47, [6228085879](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6228085879).
- **Bases:**
  - confronto `59572be` (`confronto-claude-codex.md`);
  - fonte do protótipo `47ccc1d`, com os arquivos do mapa iguais aos de `b989864`;
  - PRD e design system em `c827408`.
- **Autor:** Claude. **Revisor:** Codex. **Registro:** Codex.
- **Estado:** especificado. Executado só o que a §R lista: a unidade da regra de vizinho, em Node, e a leitura das fontes W3C, APG, NVDA e Chrome, com SHA-256.
  - Não simulei o Gemini nem repeti a consulta.
  - Não abri navegador: o portão já tinha um Chrome principal rodando, e esta tarefa tem prioridade menor.
  - Leitor de tela real: nenhum dos dois agentes tem.

```text
ID / resultado útil / persona: MAPA-UX · revisão G1–G3 / dizer o que da consolidação vale, delimitar a menor contraprova real do G2 e a fronteira de layout do G3 no contrato / gestor e agrônomo no teclado ou com leitor de tela; operador no celular
Requisitos do PRD e fora do escopo: pedido §1 (teclado, celular, 48 px), §4 (aceite de teclado e leitor), 74.5.24–26, SEL-02, DS-15; WCAG 2.2 (1.4.10, 1.4.11, 1.4.13, 2.1.4, 2.4.11, 2.5.1, 2.5.7); fora: implantar, editar PRD, nova consulta ao Gemini
Autor / revisor / integrador: Claude / Codex / Codex
Base / arquivos sob responsabilidade: 87e524e × 59572be / docs/integracao/V73/MAPA-UX/gemini-revisao-claude.md e reproducao/gemini/
Aceite e comando de verificação: §R; node reproducao/gemini/vizinho_unit.js; sh reproducao/gemini/fontes_gemini.sh <pasta vazia>; sh reproducao/gemini/fontes_delta4.sh <pasta vazia> (Δ4)
Estado / impedimento / próximo passo: entregue; a contraprova do G2 (§2) espera quem tenha leitor real; a fronteira do G3 (§3) entra no contrato da F3 depois da MAPA-FROTA
```

## Resumo

- **Contagem:** 30 itens da consolidação. ~~**Concordo com 23, ajusto 7, divirjo de 0**~~ **Δ4 17/10:** **concordo com 24, ajusto 6, divirjo de 0** (§1); o item 1 passou a concordo pela procedência que o Codex informou. Há também 3 acréscimos sobre o parecer do Gemini que a consolidação não tratou (§1.1).
- **Ajuste principal no G2:**
  - O bloqueio "o `group` não garante que as setas cheguem em modo de navegação" é verdadeiro, mas a pergunta está um passo ao lado.
  - Com tabindex móvel, os botões continuam no documento, e o cursor virtual do leitor chega a todos eles na ordem da lista. O aceite do pedido ("teclado e leitor de tela percorrem os talhões com nome acessível completo") não depende das setas chegarem.
  - A contraprova mede, primeiro, se tudo é alcançável e sem armadilha, e depois se as setas chegam. A segunda resposta muda só a instrução dada ao usuário de leitor.
- **Ajustes de fonte:**
  - `application` restrito ao grupo é legítimo pela ARIA 1.2 (o exemplo dela é um editor de slides movido por setas) e entra na contraprova; global, não.
  - `tabindex` no grupo só vale com `aria-activedescendant`, que a ARIA 1.2 permite em `group`.
  - O "/" é atalho de um caractere e cai na WCAG 2.1.4: fica ativo só com o foco dentro do bloco do mapa.
  - Ida e volta: o `panBy` em pixels é simétrico na projeção; só o limite e a mudança de zoom quebram a simetria.
- **Contraprova do G2 (§2):** página sintética `reproducao/gemini/g2_contraprova.html` com `group`, `toolbar` e `application` só no grupo. Roteiro de 7 passos, matriz mínima de 6 combinações, regra de decisão, e a fronteira do que o Chrome sem tela prova.
- **Δ4 17/10 (Codex, PR #47, [6228236159](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6228236159)):** seis correções, com o texto anterior riscado.
  - Item 1: a procedência Vertex fica pela cadeia adaptador + bruto.
  - §2.6: a página só cobre setas, Tab, Enter, Home/End e a árvore; "/", campos, IME e Esc → talhão são da integração.
  - §2.4: o G2 final exige as combinações obrigatórias.
  - §3.1: sem conclusão antecipada sobre o foco; a prova é o T6.
  - T3: cobertura separada da visão simultânea.
  - §3.2: 48 px por padrão, com teste em dispositivo híbrido.
- **Fronteira do G3 (§3):**
  - Lugar: o grupo de zoom atual (direita, `top: 96px`), com um botão "Mover o mapa" que abre a cruz. Nada de barra nova, `nav` ou `fieldset`.
  - Tamanho: ~~48 px no toque e 36 px no mouse~~ Δ4: 48 px por padrão; 36 px só sem nenhum dispositivo de toque disponível (`any-pointer`). Passo: 1/3 da vista.
  - Limites: o último passo é parcial, e o botão fica `aria-disabled`, mas focável.
  - Testes: ida e volta, limite, cobertura, 390 px, dispositivo híbrido (Δ4) e foco não encoberto.

## 1. Revisão item a item

Fonte "fontes" = `reproducao/gemini/fontes_gemini.txt` (trecho, URL, SHA-256 da página baixada em 17/10).

| # | Item da consolidação | Parecer | Fundamento | Fonte |
|---|---|---|---|---|
| 1 | Metadados da consulta (cons. l.2): única, modelo, HIGH, STOP, `responseId`, 8176 tokens (3565 + 1984 + 2627), pacote de 6128 bytes | ~~**Ajuste**~~ **Δ4 17/10:** **Concordo** | ~~Tudo confere no bruto, menos "Vertex", que o `parecer.json` não nomeia (só `project` e `authenticationMode`).~~ Δ4: tudo confere no bruto. A plataforma vem da cadeia adaptador + bruto: segundo o Codex, o adaptador executado (`work/agentes-config/gemini-consult-1d2e6a3b.py:104`) chama `aiplatform.googleapis.com/…:generateContent`, e não houve outra consulta. Essa confirmação é do Codex; **não li o adaptador**. A procedência não cai só porque o JSON não traz o rótulo. Nota que fica: o `payloadSha256` não é o SHA-256 do `pacote.txt` (`9d1dbae4…`), o que é esperado se o payload levou a skill `dev-revisao`; vale dizer isso para não parecer divergência | `parecer.json:2-49`; `wc -c` e `sha256sum` do `pacote.txt` |
| 2 | G1: manter A como candidata, não aprovação final (l.5) | Concordo | É o que o confronto já dizia: nada se aplica antes dos pares reais | `confronto-claude-codex.md` §8, item 4 |
| 3 | G1: branco 90 % é translúcido, não "sólido/opaco" como o Gemini escreveu (l.5) | Concordo | O parecer diz "placa opaca 90%" e "placa de fundo sólido" | `parecer.json:27`; `contraste_pares_placa.txt` |
| 4 | G1: os 4,76 são do texto escuro sobre o token, não do token sobre branco (l.5) | Concordo | `#7D8C85` opaco: escuro 4,76:1; branco 3,52:1. O Gemini escreveu "4.76:1 sobre fundo branco" | `contraste_pares.txt` E |
| 5 | G1: 13,362:1 contínuo, 13,424:1 em 8 bits (l.5) | Concordo | Mesmos números do modo `--placa-limite` | `contraste_pares_placa.txt` |
| 6 | G1: sete classes não violam memória por si; não cortar estados (l.5) | Concordo | O Gemini não trouxe fonte nem medida. O estado está em texto no rótulo, no cartão e na lista, e a legenda fica visível e recolhível (74.5.25): não há o que lembrar | `PRD.md:14454`; pedido l.71 |
| 7 | G1: contraste calculado não verifica ocultação, tamanho, forced-colors, foco nem usabilidade; inspeção estática isolada não certifica o render (l.5) | **Ajuste** | Concordo, com uma precisão. O 13,424:1 é limite analítico para **qualquer** fundo opaco, mas condicionado a quatro fatos do render, que o Chrome sem tela confere: (a) a placa cobre a caixa inteira do texto, com acentos e descendentes; (b) nenhuma `opacity`, `filter` ou `mix-blend-mode` no texto ou nos ancestrais; (c) texto opaco `#15201A`; (d) placa composta como especificada (amostrar pixels da placa em captura). O aceite proposto pelo Gemini ("ferramenta estática prova em qualquer ponto") não vale como está | `contraste_pares_placa.txt`; `inicio.py:1405` (`opacity .85` hoje no sub) |
| 8 | G2: o bloqueio principal não foi resolvido: `group` não garante que as setas do leitor em modo de navegação cheguem aos botões (l.7) | **Ajuste** | A premissa é verdadeira. O NVDA usa as setas no modo de navegação e só passa as teclas ao controle no modo de foco, que liga sozinho "se o controle exigir"; a ARIA 1.2 só pede passagem de teclas para papéis de widget e `application`. Mas, com tabindex móvel, os botões continuam no documento, e o cursor virtual chega a todos na ordem da lista. O aceite do pedido (§4: "teclado e leitor de tela percorrem os talhões") não exige setas. A contraprova (§2) mede primeiro alcance completo e ausência de armadilha; a chegada das setas define a instrução | fontes: NVDA 2026.2; ARIA 1.2 (`application`; widget); pedido l.126 (numeração de `529adf7`) |
| 9 | G2: não rejeitar `toolbar` por "sequestro" genérico; é padrão legítimo; a navegação linear documentada não equivale aos vizinhos espaciais (l.7) | Concordo | APG Toolbar: uma parada de Tab; setas esquerda e direita (ou cima e baixo com `aria-orientation=vertical`); nada sobre modo de leitor. Na ARIA 1.2, `toolbar` tem superclasse `group`, então nem a especificação garante troca de modo. A frase do Gemini ("toolbar força modo formulário") não tem fonte | fontes: APG Toolbar; ARIA 1.2 `toolbar` |
| 10 | G2: não usar `application` global (l.7) | **Ajuste** | Concordo para global. Restrito ao grupo de talhões, é o caso que a ARIA 1.2 descreve: "assistive technologies … SHOULD switch to a mode that passes most or all standard input events through", com o exemplo de um editor de slides movido por setas. Exige associar todo texto não decorativo por `aria-labelledby` ou `aria-describedby`. Entra na contraprova como A3 | fontes: ARIA 1.2 `application` |
| 11 | G2: não pôr `tabindex=0` no grupo e nos botões ao mesmo tempo; foco móvel no botão ativo (l.7) | **Ajuste** | Concordo com a regra. Precisão: `tabindex` no grupo é legítimo na outra técnica do APG (`aria-activedescendant` no contêiner, sem `tabindex` nos botões), e a ARIA 1.2 permite `aria-activedescendant` em `group`. Fica o tabindex móvel, porque o foco real no botão é o que o Esc devolve e o que o painel usa | fontes: APG teclado; ARIA 1.2 `aria-activedescendant` |
| 12 | G2: prova real de leitor necessária; a matriz do Gemini não cobre JAWS nem TalkBack (l.7) | Concordo | Matriz mínima na §2.4 | — |
| 13 | G2: não adotar Shift + setas sem verificar conflito com seleção múltipla (l.7) | Concordo | No APG Listbox, Shift + seta move o foco e alterna a seleção. Aqui, Shift + clique já é "selecionar vários" | fontes: APG Listbox; avaliação §2 l.118 |
| 14 | G2: "/" respeita edição, `contenteditable` herdado, controles compostos e IME; `tagName` não basta (l.7) | **Ajuste** | Concordo e acrescento a fonte que faltou: "/" é atalho de um caractere (WCAG 2.1.4, nível A), que precisa poder ser desligado, remapeado ou ficar ativo só com o foco no componente. Proposta: ativo só com o foco dentro do bloco do mapa; ignorado com `isContentEditable`, `isComposing` (IME), papéis `textbox`, `searchbox` e `combobox`, e com qualquer modificador | fontes: Understanding 2.1.4 |
| 15 | G2: ao filtrar o focado, destino determinístico, sem foco no `body` (l.7) | Concordo | Mesma regra do SEL-02: nunca selecionar outro em silêncio | DS `README.md:25` (SEL-02) |
| 16 | G2: pedir ao Claude a menor contraprova real, sem trocar a geometria por ordem textual (l.7) | Concordo | §2. As setas seguem a geometria; a ordem do DOM (lista) serve só ao cursor virtual | `vizinho_unit.txt` |
| 17 | G3i: não adotar `body overflow:hidden` nem `fitBounds` ao abrir o teclado (l.9) | Concordo | O `fitBounds` automático contraria o NÃO FAZER 5 do pedido. Pela WCAG 1.4.10, o mapa é exceção de layout em duas dimensões, mas a folha, os filtros e os controles precisam refluir a 320 px CSS; `overflow:hidden` no `body` pode cortá-los | pedido l.136; fontes: Understanding 1.4.10 |
| 18 | G3i: `100dvh` sozinho não prova que o teclado virtual fica visível (l.9) | Concordo | Desde o Chrome 108 no Android, o padrão redimensiona só a vista visual; o comportamento varia por navegador e sistema, "beyond your control" | fontes: Chrome, viewport-resize-behavior |
| 19 | G3i: não rejeitar gestos cooperativos por alegação não medida; há alternativa com botões (l.9) | Concordo | A 2.5.1 aceita gesto de vários pontos quando há operação com um ponteiro sem gesto de trajeto | fontes: Understanding 2.5.1 |
| 20 | G3i: B com reserva continua hipótese; trocar de modo só fora do gesto, sem perder contexto e foco (l.9) | Concordo | — | `confronto-claude-codex.md` §5, G3 (i) |
| 21 | G3i: expandir e recolher a folha precisa de botão, não só de alça arrastável (l.9) | Concordo | Arrastar a alça é movimento de arrasto (2.5.7) | fontes: Understanding 2.5.7 |
| 22 | G3ii: (a), os direcionais no grupo existente, é a candidata mínima, compatível com o exemplo W3C de mapa (l.11) | Concordo | O exemplo existe: "A map allows users to drag the view … and the map has up/down/left/right buttons" | fontes: Understanding 2.5.7 |
| 23 | G3ii: sem `opacity` de 80 % nos controles (l.11) | Concordo | A 1.4.11 pede 3:1 contra as cores adjacentes; translúcido depende do que está embaixo, e não libera área | fontes: Understanding 1.4.11 |
| 24 | G3ii: fundo sólido e `stopPropagation` não tornam selecionável um talhão coberto (l.11) | Concordo | O problema é alcance e visibilidade, não vazamento de evento. A regra da §3 fecha a cruz quando o foco entra num talhão (2.4.11) e mantém lista, busca e teclado como caminhos. Δ4 17/10: fechar a cruz não basta sozinho; a prova é o T6 | fontes: Understanding 2.4.11 |
| 25 | G3ii: passo de 1/3 explora com sobreposição, sem centralizar exato; ida 3 + volta 3 só é simétrica sem limite, projeção ou zoom alterado; não exigir precisão infinita (l.11) | **Ajuste** | Concordo, menos "projeção". O `panBy` do MapLibre move em pixels de tela; voltar o mesmo número de pixels no mesmo zoom devolve o centro, porque projetar e desprojetar se inverte (a rotação está desligada, `inicio.py:620-621`). Quebram a simetria o limite (`lgLimites`, `:612`) e a mudança de zoom. Aceite de equivalência: **cobertura** (§3.5, T3) | `inicio.py:612`, `:619-621` |
| 26 | G3ii: os botões de pan não usam as setas dos talhões (l.11) | Concordo | Acrescento: o canvas deixa de ser parada de Tab (hoje `tabindex=0`, nome "Map", M0), para não haver dois modelos de seta. O teclado move o mapa pelos botões | avaliação §R M0 |
| 27 | G3ii: verificar 390 px, folha aberta, teclado e bordas (l.11) | Concordo | O teclado virtual não se emula no Chrome sem tela: vai para o teste em aparelho (§3.5) | — |
| 28 | Fonte: APG Toolbar (l.14) | Concordo | Conferida: uma parada de Tab e setas pela orientação; não trata de modo de leitor | fontes |
| 29 | Fonte: Understanding 2.5.7 (l.15) | Concordo | Conferida: o exemplo do mapa, e equivalência de teclado não basta sem controle de clique ou toque | fontes |
| 30 | Evidência: `--placa-limite` reproduzido em 13,424, 13,362 e 8,883 (l.18) | Concordo | Os mesmos números da saída guardada | `contraste_pares_placa.txt` |

### 1.1 Acréscimos sobre o parecer do Gemini (não tratados na consolidação)

| # | Trecho do parecer | Parecer do Claude | Fonte |
|---|---|---|---|
| X1 | Pôr os botões de pan num `<nav aria-label="Controle de câmera">` ou `<fieldset>` | **Divirjo do Gemini.** `navigation` é landmark de navegação do documento ("usually links"); controles de câmera não são isso, e um landmark a mais faz ruído. `fieldset` é de formulário. Fica o grupo que já existe (`role=group`, 74.5.24), renomeado para "Zoom e movimento" | fontes: ARIA 1.2 `navigation`; `PRD.md:14444` |
| X2 | Rejeitar (b), "só após zoom", porque "falha com leitores de tela mesmo em zoom zero" | **Ajuste no motivo; a conclusão (a) fica.** Com a fazenda inteira na vista não há o que mover. O motivo bom é a estabilidade: os botões ficam sempre presentes e ficam `aria-disabled` no limite, focáveis para serem descobertos (APG Toolbar), em vez de aparecer e sumir | fontes: APG Toolbar (controles desabilitados focáveis) |
| X3 | Rejeitar (c), "Centralizar aqui", porque "viola uma ação primária por contexto" | **Ajuste no motivo; a conclusão fica.** A regra de um verde por contexto (BOT-01) trata de botões, não do clique no mapa; "Medir" e "Selecionar área" já são modos. O motivo bom: (c) exige entrar e sair de um modo e disputa o clique do talhão enquanto está ligado | DS `README.md:10` (BOT-01); `inicio.py:1174` |

## 2. Menor contraprova real do G2

### 2.1 O que ela decide

Para cada papel do contêiner, `group` (A), `toolbar` (A2) e `application` só no grupo (A3):
- **Obrigatório:**
  1. o usuário de leitor alcança e aciona os 4 talhões no modo padrão do leitor;
  2. ouve nome e estado (`aria-pressed`);
  3. sai do grupo com Tab, e a leitura volta a funcionar depois (sem armadilha).
- **Informativo:** as setas chegam à página depois do Tab, sem troca manual de modo.

### 2.2 Material (executado o que dá sem navegador)

- `reproducao/gemini/g2_contraprova.html`: página sintética, sem dado real.
  - Três variantes com os mesmos 4 botões em grade 2 × 2, nomes no formato do pedido, `aria-pressed`, tabindex móvel, instruções no `aria-describedby`, e "texto antes" e "texto depois" para o modo de navegação.
  - Um registro de toda tecla que **a página** recebe: variante, tecla, alvo, `defaultPrevented` e foco depois. Tecla consumida pelo leitor não aparece no registro, e essa é a medida.
  - "Mostrar registro" gera o JSON para copiar.
- `reproducao/gemini/vizinho_unit.js`: a regra de vizinho espacial da página, extraída e testada em Node (**executado**: 10 de 10, incluindo a propriedade "o escolhido está sempre no semiplano da direção" em 2000 casos sintéticos × 4 setas). O script da página compila (sintaxe conferida em Node).
- **Não executado:** a página num navegador. É o portão da §2.6, antes de chamar qualquer pessoa. **Δ4 17/10:** esse portão da página cobre só setas, Tab, Enter, Home/End e a árvore de acessibilidade. Os checks de "/", campos, `contenteditable`, IME e Esc → talhão com sobreposição não estão nesta página e ficam para a integração da MUX-F1 (§2.6).

### 2.3 Roteiro, por combinação de leitor e navegador

Leitor no modo padrão, página aberta no topo.

1. Ler com a seta para baixo até "Texto antes da variante A". Tab. **Anotar:** o leitor trocou de modo sozinho (som ou fala)? O que anunciou (grupo, nome do botão, estado)?
2. Seta para a direita, uma vez. **Anotar:** a fala; e se o registro ganhou a linha `[A] ArrowRight` com o foco em "P2…".
3. Seta para baixo, uma vez. **Anotar:** o mesmo, esperando o foco em "T4…".
4. Enter. **Anotar:** o estado anunciado mudou para pressionado?
5. Tab. **Anotar:** saiu do grupo? O leitor voltou ao modo de navegação?
6. Seta para baixo. **Anotar:** lê "Texto depois da variante A" (sem armadilha)?
7. Sem usar Tab, ler com a seta para baixo até os botões da variante; ativar um com Enter. **Anotar:** os 4 são alcançáveis pelo cursor virtual, na ordem P1, P2, T3, T4?

Repetir de 1 a 7 nas variantes A2 e A3. Ao fim, "Mostrar registro" e copiar o JSON.

No toque (VoiceOver iOS e TalkBack), os passos 2, 3 e 6 viram: deslizar para o próximo item, tocar duas vezes para ativar, explorar pelo toque cada botão.

### 2.4 Matriz mínima

| # | Leitor | Navegador e sistema | Peso |
|---|---|---|---|
| 1 | VoiceOver | Safari, macOS | obrigatória |
| 2 | NVDA (2026.x) | Chrome, Windows | obrigatória |
| 3 | NVDA | Firefox, Windows | desejável |
| 4 | JAWS | Chrome, Windows | desejável (licença do fabricante) |
| 5 | VoiceOver | Safari, iOS, no toque | obrigatória para o campo (uma de 5 ou 6) |
| 6 | TalkBack | Chrome, Android, no toque | obrigatória para o campo (uma de 5 ou 6) |

**Regra de decisão:**
- ~~Fica **A** (`group`) se cumprir o obrigatório da §2.1 em todas as combinações executadas.~~ **Δ4 17/10:** fica **A** (`group`) se cumprir o obrigatório da §2.1 em **todas as combinações obrigatórias da matriz** (1, 2, e 5 ou 6) e em todas as desejáveis que forem executadas. O informativo (setas chegam ou não) muda só o texto da instrução para usuário de leitor.
- Passa para A2 ou A3 só se A falhar no obrigatório e a outra cumprir. A3 sempre restrito ao grupo e com todo texto associado.
- Nenhuma conclusão vale para combinação não executada.
- **Δ4 17/10:** se alguma combinação obrigatória ficar bloqueada (sem ambiente, sem pessoa ou sem licença), registra-se **aprovação parcial**: as combinações aprovadas, as bloqueadas e o motivo de cada uma. O G2 não congela como final enquanto houver obrigatória bloqueada.
- **Δ4 17/10:** passar só no Chrome sem leitor **nunca** seleciona o G2 final; é só o portão para chamar uma pessoa.

### 2.5 Quem pode executar

| Combinação | Quem | Condição |
|---|---|---|
| 1 (macOS) | O proprietário no Mac, uns 10 minutos. Ou o Codex, cujo ambiente é Darwin (`parecer.json`, `runtime.system`), se o VoiceOver puder ser controlado por AppleScript | O controle por AppleScript é uma opção que o proprietário liga no Utilitário do VoiceOver. Sem custo, mas é ação dele, e **não verifiquei** se basta no ambiente do Codex |
| 2–4 (Windows) | Nenhum agente tem Windows | Máquina Windows do proprietário, se houver, ou o teste com usuários da DEC-1610-02. O JAWS pede licença: custo, então decide o proprietário |
| 5–6 (celular) | O proprietário, com o próprio aparelho, uns 10 minutos | Ou o teste com usuários (DEC-1610-02) |

### 2.6 O que o Chrome sem tela prova e o que não prova

Δ4 17/10: na tabela, só as duas primeiras linhas valem para a página atual. A página não tem campo, `contenteditable`, handler de "/", painel sobreposto nem Esc; as linhas 3 e 4 são checks do teste de integração da MUX-F1 (`mapa_mux_f1_test.py`, especificado), no IN-04 com o painel real. O portão da página **não** cobre essas linhas.

| Prova (portão antes de chamar uma pessoa) | Não prova |
|---|---|
| Com `Input.dispatchKeyEvent` (CDP), nas três variantes: Tab chega ao 1º botão; as setas levam aos vizinhos esperados (os mesmos da unidade); Home e End; Enter alterna `aria-pressed`; Tab sai do grupo; as setas ficam com `defaultPrevented` | Se o leitor troca de modo, captura a tecla ou a deixa passar: o CDP entrega a tecla direto à página, sem leitor no meio |
| Pela árvore de acessibilidade (`Accessibility.getFullAXTree`): papel, nome e descrição do contêiner; 4 botões com nome e estado; nenhum ancestral `img` | O que o leitor fala, a verbosidade e a ordem de anúncio |
| Que o "/" é ignorado em campo, `contenteditable` e composição de IME (`Input.imeSetComposition`). **Δ4: integração da MUX-F1, não esta página** | O mapeamento em cada API de plataforma (AX no macOS, UIA e IA2 no Windows, Android): a árvore do Chrome é uma só |
| Que o foco volta ao botão do talhão depois de Esc, com a sobreposição já fechada (regra do Δ2). **Δ4: integração da MUX-F1, não esta página** | Exploração por toque, gestos do leitor e braile |

## 3. Fronteira de layout do G3 (ii) para o contrato

Entra no contrato da F3, depois da MAPA-FROTA e com o SHA fixado (confronto §8.2).

### 3.1 Lugar

- O grupo que já existe: hoje `<div role="group" aria-label="Zoom">`, com `position: absolute; right: 12px; top: 96px`, em coluna (`inicio.py:1523-1524`).
  - O rótulo passa a "Zoom e movimento".
  - Nada de barra nova, landmark `nav` ou `fieldset` (X1).
- **Fechado (padrão):** Aproximar (+), Afastar (−) e "Mover o mapa" (botão de alternância com `aria-expanded` e `aria-controls`), em coluna, no mesmo canto. As posições de + e − não mudam.
- **Aberto:** à esquerda da coluna, alinhada ao topo do grupo, uma cruz 3 × 3 com:
  - ↑ "Mover para cima", ← "Mover para a esquerda", → "Mover para a direita" e ↓ "Mover para baixo";
  - no centro, "Ajustar à fazenda" (74.5.24);
  - os cantos vazios sem área de clique (`pointer-events: none`), para não roubar o toque do talhão.
- **Fecha quando:**
  - "Mover o mapa" é acionado de novo;
  - Esc é pressionado com o foco na cruz (o foco volta ao "Mover o mapa");
  - o foco entra no grupo de talhões. ~~Assim, o talhão focado nunca fica inteiramente coberto (2.4.11). A cruz aberta é conteúdo aberto pelo usuário, que ele fecha sem mover o foco (Nota 2 da 2.4.11).~~ **Δ4 17/10:** fechar a cruz reduz a área coberta, mas sozinho não garante que o foco não fique encoberto por outros controles (coluna de zoom, ferramentas, legenda, painel ou folha). A prova é o T6, sem conclusão antes dele.
- **Enquadramento inicial:** reserva a margem da coluna fechada, não a da cruz. É o estado inicial da câmera, não um movimento.

### 3.2 Tamanho

- ~~**48 × 48 px** por botão com ponteiro grosso (`@media (pointer: coarse)`), como pede o pedido (l.67).~~
- ~~**36 × 36 px** com ponteiro fino, como o zoom de hoje (74.5.24); o piso de 24 px do DS-15 no desktop continua.~~
- **Δ4 17/10:** **48 × 48 px por padrão** em todos os controles do mapa, como pede o pedido (l.67). Reduz para **36 × 36 px** só quando nenhum dispositivo de toque está disponível: `@media not all and (any-pointer: coarse)`.
  - Motivo: `pointer` reflete só o dispositivo principal; `any-pointer` reflete a união de todos (Media Queries 4, `reproducao/gemini/fontes_delta4.txt`).
  - Num híbrido com mouse principal e tela de toque, `pointer: coarse` é falso, mas `any-pointer: coarse` é verdadeiro, e os 48 px ficam.
  - O piso de 24 px do DS-15 no desktop continua; a área ocupada abaixo usa 48 px como padrão.
- Espaço entre botões: 6 px, o atual.
- **Área ocupada:** fechado, 48 × 156 px ~~no toque~~ por padrão (36 × 120 ~~no mouse~~ só sem nenhum toque, Δ4); aberto, 210 × 156 px ~~no toque~~ por padrão (162 × 120 só sem nenhum toque).
  - A 390 px, o grupo vai de y = 96 a y = 252. A faixa de ferramentas termina por volta de y = 87 (`top: 52px`, `inicio.py:1659`), e a legenda ocupa no máximo os 30 % de baixo do mapa.
  - **Medir na F3:** sem interseção com ferramentas, legenda e folha. Se a largura do mapa a 390 px for menor que 2 × 210 px, a cruz aberta cobre mais da metade da largura nessa faixa; por isso ela é temporária e fecha pelas regras da §3.1.

### 3.3 Passo e comportamento

- Cada acionamento move a vista **1/3 da dimensão visível do mapa** naquele eixo.
  - MapLibre: `panBy([±L/3, 0])` ou `panBy([0, ±A/3])`.
  - SVG da Santa Rita: o mesmo deslocamento em pixels de tela, convertido para unidades do desenho; depende do pan do D4.
- Zoom e rotação não mudam (a rotação já está desligada, `inicio.py:620-621`).
- Animação curta, sem animação com `prefers-reduced-motion`.
- Um acionamento é um passo; não há repetição ao segurar.
- O canvas deixa de ser parada de Tab, com o teclado do MapLibre desligado. As setas dos talhões nunca movem a câmera, e os botões de pan nunca mudam a seleção (item 26).

### 3.4 Limites

- **Área navegável:**
  - na Lagoa Grande, a imagem (`lgLimites`, `inicio.py:612`; `minZoom 11`, `maxZoom 17.5`, `:621`);
  - na Santa Rita, o desenho (`viewBox`), depois do pan do D4.
- O passo que passaria do limite é **parcial**: para no limite.
- No limite, o botão daquela direção fica `aria-disabled="true"`.
  - Ele **continua focável**, como o APG recomenda quando descobrir a função importa.
  - Acionado, não move e anuncia uma vez "Limite do mapa à direita" (ou a direção) pela região viva que já existe.
- Com a fazenda inteira na vista e no zoom mínimo, os quatro podem ficar desabilitados. O desenho não muda, e os botões não somem.

### 3.5 Testes

Especificados; o render `05947ad` reprova T1, porque não há botões de pan.

| # | Teste | Aceite | Onde |
|---|---|---|---|
| T1 | Ida e volta longe dos limites | Em dois zooms (enquadramento + 1 e + 3), com pelo menos 3 passos livres em cada direção: → × 3 e ← × 3 devolvem o centro com até 1 px de diferença (em `map.project`). O mesmo com ↑ × 3 e ↓ × 3. Zoom, seleção, painel, rascunho e URL da seleção iguais; foco no último botão acionado. Repetir na Santa Rita depois do D4 | Chrome sem tela |
| T2 | Limite | → até ficar `aria-disabled` (k acionamentos). O último passo é parcial (até L/3), e a borda da vista coincide com a do limite (± 1 px). Acionar no limite não move (0 px) e anuncia uma vez. ← × k volta para dentro de um passo do centro inicial. "Ajustar à fazenda" devolve o enquadramento inicial (± 1 px) | Chrome sem tela |
| T3 | Cobertura (equivalência para explorar) | ~~No enquadramento + 3, a busca em largura pelos passos alcança vistas cuja união cobre 100 % da área navegável (amostra a cada 10 px). Cada um dos 31 talhões pode ficar inteiro fora da área da cruz aberta em alguma vista alcançável~~<br>**Δ4 17/10:**<br>**T3a, cobertura integral:** no enquadramento + 3, a busca em largura pelos passos alcança vistas cuja união cobre 100 % da área navegável (amostra a cada 10 px). Assim, todo ponto da área e do contorno de cada talhão fica visível, fora de qualquer controle, em alguma vista alcançável; não precisa ser tudo ao mesmo tempo.<br>**T3b, visão simultânea:** para cada um dos 31 talhões, existe um estado alcançável só por comandos explícitos (passos, Afastar ou "Ajustar à fazenda") com o talhão inteiro na vista e fora de qualquer controle. No zoom + 3 isso só se exige do talhão cuja caixa cabe na vista menos a área dos controles; o maior usa Afastar ou "Ajustar à fazenda", e o teste registra o zoom usado | Chrome sem tela |
| T4 | 390 px e toque | Todos os botões do grupo com pelo menos 48 × 48 px. O grupo não cruza ferramentas, legenda nem folha aberta (interseção = 0). Abrir e fechar a cruz não move a câmera | Chrome sem tela, com ponteiro grosso emulado |
| T4h | Δ4 17/10: dispositivo híbrido (mouse e toque) | (a) Estático: nenhuma regra deixa controle do mapa abaixo de 48 px fora de `not all and (any-pointer: coarse)`. (b) Com emulação de toque: 48 px; sem nenhum toque: 36 px. (c) Num híbrido real (notebook com tela de toque ou tablet com mouse ou trackpad), com o mouse como principal: todos os controles com pelo menos 48 × 48 px | (a) leitura do CSS; (b) Chrome sem tela, que não reproduz fielmente um híbrido (a emulação de toque muda o dispositivo principal; não verifiquei se o CDP emula `any-pointer` separado de `pointer`); (c) aparelho real |
| T5 | Sem conflito | Acionar pan nunca muda a seleção nem abre o painel. Setas num talhão nunca mudam o centro (0 px) | Chrome sem tela |
| T6 | Foco não encoberto | ~~Com a cruz aberta, Tab até um talhão: a cruz fecha, e a caixa do talhão focado não fica inteiramente coberta por nenhum controle~~<br>**Δ4 17/10:** com a cruz aberta, Tab até um talhão: a cruz fecha. Com a coluna de zoom, as ferramentas, a legenda, o painel e a folha nas posições reais, a caixa de cada talhão focado não fica inteiramente coberta (interseção menor que a área do talhão). Vale para os 31 talhões, a 1440 e a 390 px. É a prova; nada se conclui antes dela | Chrome sem tela |
| T7 | Teclado virtual e leitor no toque | Folha aberta com o teclado virtual: botões e detalhe alcançáveis. VoiceOver e TalkBack: os 8 botões anunciados com nome e estado, ativados com toque duplo | Aparelho real (o Chrome sem tela não emula) |

## R. Reprodução

| Comando | Saída | Resultado |
|---|---|---|
| `node reproducao/gemini/vizinho_unit.js` | `vizinho_unit.txt` | **Executado.** 10 de 10: casos da grade 2 × 2, bordas, desvio lateral, empate e propriedade em 2000 casos sintéticos × 4 setas. O script da página compila |
| `sh reproducao/gemini/fontes_gemini.sh <pasta vazia>` | `fontes_gemini.txt` | **Executado em 17/10, 01:52 UTC.** 13 páginas com HTTP 200: APG Toolbar, Teclado e Listbox; ARIA 1.2; Understanding 2.5.7, 2.5.1, 2.1.4, 1.4.10, 1.4.11, 2.4.11 e 1.4.13; NVDA 2026.2 User Guide; Chrome, viewport-resize-behavior. Guarda o SHA-256 parcial de cada página e os trechos citados; as páginas não entram no repositório |
| `sh reproducao/gemini/fontes_delta4.sh <pasta vazia>` | `fontes_delta4.txt` | **Executado em 17/10, 02:03 UTC** (Δ4). Media Queries Level 4, HTTP 200: `pointer` é o dispositivo principal; `any-pointer` é a união de todos |
| `reproducao/gemini/g2_contraprova.html` | — | **Especificado.** Página da contraprova; o portão do Chrome sem tela (§2.6) vem antes de qualquer pessoa |

Fora do escopo:
- PR #88, PR #89, a correção dos rádios e a publicação, que o Codex mantém como prioridade.
- Nenhuma consulta nova ao Gemini e nenhuma mudança no PRD.
