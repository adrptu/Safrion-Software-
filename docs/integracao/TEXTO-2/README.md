# TEXTO-2 · menos texto solto nas telas (segunda passada)

Pedido do proprietário (13/10/2026): "reduza ou elimine todas essas descrições abaixo dos titulos e os demais soltos pela tela.... em todas as telas do sistema. somos minimalistas e essencialistas."

A primeira passada (`c24ab70`, já publicada) tirou subtítulos, descrições de bloco e rodapés e criou o ⓘ "Regras desta tela" ao lado do título. Esta segunda passada tira as frases explicativas que ainda ficavam soltas no corpo das telas.

```text
ID / resultado útil / persona: TEXTO-2 · telas só com dado, estado, trava e próximo passo; a regra fica no ⓘ · gestor, agrônomo, operador (app)
Requisitos do PRD e fora do escopo: AGENTS §4 (trava só onde protege algo; estado visível; próximo passo com verbo) · fora: Mapa (areas/inicio.py), solo.js e a faixa "Filtros desta tela" (com o integrador)
Autor / revisor / integrador: Claude / Codex (sem bloquear, §3.5) / integrador da branch do protótipo
Base (commit ou hashes) / arquivos sob responsabilidade: 48f570b, branch local int/texto2 · areas/{mobile,campo,colheita,suprimentos,planejamento,comercial,logistica,gestao,configuracoes,assinatura,plataforma,parceiros,onboarding_backoffice,inteligencia,maquinas}.py, engine.py, ui37.py, g2lib.js e 3 testes
Aceite e comando de verificação: ≥ 70 % dos caracteres de explicação fora da vista · textos_soltos_test.py verde no render novo e vermelho no de antes
Estado / impedimento / próximo passo: pronto para revisão · sem impedimento · integrar na branch do protótipo e publicar o artefato
```

## Resultado (executado em 14/10/2026)

| Medida | Antes (`48f570b`) | Depois | Variação |
|---|---:|---:|---:|
| Varredura combinada (blocos ≥ 45 car., cortados em 140): caracteres | 21.926 | 12.604 | −42,5 % |
| Varredura combinada: telas com texto solto | 97 | 79 | −18 |
| Explicação à vista (varredura sem corte, 68 telas, classificação pela lista do teste) | 12.680 car. | 661 car. | **−94,8 %** (meta: −70 %) |

- Os 661 caracteres que ficaram são as frases mantidas de propósito (seção "Ficou à vista"). Elas contam como explicação que ficou, por conservadorismo.
- O resto da varredura é dado, trava, rótulo de demonstração ou exemplo, nomes dos cartões das telas de entrada (MOD-*) e o anúncio "Tela: …" para leitor de tela. Esse anúncio é a região viva invisível (`g2sr`), mas a varredura a conta porque ela tem caixa de 1 px.
- Brutos: `brutos/varredura-antes.json`, `brutos/varredura-depois.json`, `brutos/varredura-completa-*.json` e `brutos/metrica.txt`, com a classificação bloco a bloco.
- Ferramentas: `ferramentas/scan_textos_txt.py` (a varredura combinada), `ferramentas/scan_completo.py` (a mesma sem o corte em 140), `ferramentas/metrica.py` e `ferramentas/mantidas.json`.

## O que mudou

- **App de campo (MB-\*).** O cabeçalho do app ganhou o mesmo ⓘ "Regras desta tela" da web (`engine.mobile`, `ui37.mobile37`, parâmetro `dica`). Ele fica depois do selo, com alvo de 44 × 44 px.
  - Saíram o subtítulo fixo do cabeçalho, as descrições fixas sob os títulos e dos cartões, a legenda das etapas e as notas de regra. A descrição que mostra estado (buraco dinâmico) fica.
- **Web.** As notas de regra soltas no corpo foram para o `footer` (o ⓘ) de cada tela.
  - Saíram os blocos que só tinham regra: CO-02 "Avanço × carga", CO-04 "Regra do recebimento", VE-03 "Regras da confirmação", ON-01det "Regra da importação" e, no app, MB-08x "Quando não fecha sozinho".
  - Quando a nota misturava dado e regra, o dado ficou à vista e a regra foi para o ⓘ. Exemplos: KCl 60 % (SU-01), Soja apto − reserva (CO-07), PC-088 (GE-04), "Pessoas com acesso: 14" (CF-05), PRECO-01 (BO-01).
  - `engine.section` e o `bloco` do Campo não deixam corpo vazio quando o bloco ficou só com ações. `engine.stepper` não deixa legenda vazia.
- **Correção junto (defeito da primeira passada, S3).** Nas telas da web com ⓘ, o irmão do `h1` passou a ser o ⓘ. Por isso o anúncio ao abrir a tela dizia "Tela: Apontamentos e conferência · i", em vez do estado, e o realce do estado olhava o ⓘ.
  - Executado: sonda no CA-02 e no GE-02 antes da correção.
  - O `g2lib.js` (`g2estadoCab`) agora pula o ⓘ. Proteção: verificação A do `textos_soltos_test.py`.

## Frases tiradas ou movidas (113)

Destino "dica ⓘ" é o `data-dica` do `header button.g2-info` da tela. "Apagada" é frase que só repetia o título, o botão ou a coluna, ou que era instrução genérica.

| Tela | Frase (até 100 car.) | Destino | Origem (base `48f570b`) | Onde está agora |
|---|---|---|---|---|
| MB-01 | Siga a ordem da janela; o botão diz o próximo passo. | dica ⓘ | `areas/mobile.py:364` | `areas/mobile.py:399` |
| MB-01 | Escolha o trabalho para abrir o formulário do seu domínio. | apagada | `areas/mobile.py:370` | — |
| MB-02 | suas (Marcos) e da equipe · mesma ordem do escritório | dica ⓘ | `areas/mobile.py:430` | `areas/mobile.py:435` |
| MB-02 | Abra a ordem para ver instrução, insumos e apontamentos. | apagada | `areas/mobile.py:402` | — |
| MB-02 | Consulte; quem executa é o responsável indicado. | dica ⓘ | `areas/mobile.py:404` | `areas/mobile.py:435` |
| MB-02 | Água simplificada: abre em Irrigação, sem materiais e sem requisição. | dica ⓘ | `areas/mobile.py:423` | `areas/mobile.py:435` |
| MB-02 | Fechar o turno não encerra a ordem. Encerrar é no escritório, com apontamentos enviados e nada em c… | dica ⓘ | `areas/mobile.py:425` | `areas/mobile.py:436` |
| MB-02det | Siga dose, janela e preparo da versão autorizada. | dica ⓘ | `areas/mobile.py:440` | `areas/mobile.py:495` |
| MB-02det | Use só o material autorizado; a sobra volta pela devolução. | dica ⓘ | `areas/mobile.py:447` | `areas/mobile.py:495` |
| MB-02det | Confira o que já foi enviado e o que está só no aparelho. | apagada | `areas/mobile.py:453` | — |
| MB-03 | iniciar, pausar e fechar · hectares, horas e consumo | apagada | `areas/mobile.py:599` | — |
| MB-03 | Inicie o turno na ordem em que vai trabalhar. | dica ⓘ | `areas/mobile.py:527` | `areas/mobile.py:603` |
| MB-03x-recibo | fila do aparelho · cada registro entra uma vez | dica ⓘ | `areas/mobile.py:632` | `areas/mobile.py:633` |
| MB-03x-recibo | Reenvios devolvem o mesmo recibo; a conferência decide o realizado. | dica ⓘ | `areas/mobile.py:610` | `areas/mobile.py:633` |
| MB-03x-recibo | Conflito com outro aparelho abre reconciliação sem somar em dobro. Pacote revogado ou vencido vira … | dica ⓘ | `areas/mobile.py:621` | `areas/mobile.py:634` |
| MB-04 | tipo e texto · foto e voz simuladas · funciona sem sinal | dica ⓘ | `areas/mobile.py:717` | `areas/mobile.py:720` |
| MB-05 | retiradas do operador e tarefas do almoxarife · por lote e embalagem | apagada | `areas/mobile.py:796` | — |
| MB-05 | Use na ordem; a sobra volta pela devolução ao Rui. | dica ⓘ | `areas/mobile.py:788` | `areas/mobile.py:799` |
| MB-05 | Leve a O.S.; Rui entrega por lote e embalagem. | dica ⓘ | `areas/mobile.py:789` | `areas/mobile.py:799` |
| MB-05 | Confirmar o recebimento põe o material sob sua custódia; o apontamento do turno baixa o consumo. | dica ⓘ | `areas/mobile.py:744` | `areas/mobile.py:798` |
| MB-05det |  · conferência física contra QR (fim do subtítulo) | dica ⓘ | `areas/mobile.py:821` | `areas/mobile.py:824` |
| MB-05det | Confira as sacas contra o QR antes de confirmar. | dica ⓘ | `areas/mobile.py:811` | `areas/mobile.py:824` |
| MB-05det | Ao confirmar: custódia zera, a conta 100 = 70 + 30 fecha e a OS-0417 segue para o fechamento da con… | dica ⓘ | `areas/mobile.py:812` | `areas/mobile.py:824` |
| MB-05det | Material preparado não retorna como produto original disponível; só sobra íntegra volta ao estoque. | dica ⓘ | `areas/mobile.py:814` | `areas/mobile.py:825` |
| MB-07 | previsão de colheita · conta por planta e estádio | dica ⓘ | `areas/mobile.py:945` | `areas/mobile.py:949` |
| MB-07 | Toque no talhão de fruta em produção que vai contar. | dica ⓘ | `areas/mobile.py:906` | `areas/mobile.py:949` |
| MB-08 | OS-0419 · Pivô 2 · água · sem emissão manual (subtítulo) | dica ⓘ | `areas/mobile.py:975` | `areas/mobile.py:976` |
| MB-08 | Água sem produto: sem materiais, sem requisição, sem custódia e sem devolução. | dica ⓘ | `areas/mobile.py:956` | `areas/mobile.py:976` |
| MB-08 | Confira a lâmina antes de iniciar. | dica ⓘ | `areas/mobile.py:957` | `areas/mobile.py:976` |
| MB-08 | Acompanhe a volta e confirme o término no fim. | dica ⓘ | `areas/mobile.py:963` | `areas/mobile.py:977` |
| MB-08 | Registre pausas e avanço sem encerrar a ordem. | dica ⓘ | `areas/mobile.py:964` | `areas/mobile.py:976` |
| MB-08 | passam do máximo de 12,0 mm por passada: o sistema divide em 2 passadas de 6,75 mm. Sem aprovação; … | dica ⓘ | `areas/mobile.py:971` | `areas/mobile.py:977` |
| MB-08 | Só a fertirrigação (OS-0418) é liberada pelo agrônomo, com materiais e requisição próprios. | dica ⓘ | `areas/mobile.py:972` | `areas/mobile.py:978` |
| MB-08 | Área/volume insuficientes? Registra-se o tempo e a estimativa fica pendente — a lâmina não é afirma… | dica ⓘ | `areas/mobile.py:974` | `areas/mobile.py:979` |
| MB-08x-recibo | mapa, lista, quadro e app leem o mesmo evento | dica ⓘ | `areas/mobile.py:995` | `areas/mobile.py:996` |
| MB-08x-recibo | Fatos consistentes → conferência e encerramento automáticos, com recibos separados. | dica ⓘ | `areas/mobile.py:983` | `areas/mobile.py:996` |
| MB-08x-recibo | Confira os recibos e a área realmente atendida. | apagada | `areas/mobile.py:991` | — |
| MB-08x-recibo | Balanço hídrico atualizado uma vez por aplicação | dica ⓘ | `areas/mobile.py:990` | `areas/mobile.py:996` |
| MB-08x-recibo | Horímetro divergente da lâmina calculada → a ordem fica Em conferência com o motivo exibido; corrig… | dica ⓘ | `areas/mobile.py:993` | `areas/mobile.py:997` |
| MB-09 | condição, leitura e abastecimento · funciona sem sinal | dica ⓘ | `areas/mobile.py:1084` | `areas/mobile.py:1087` |
| MB-09 | Herdada do seu turno; toque noutra ou busque pelo nome. | dica ⓘ | `areas/mobile.py:1005` | `areas/mobile.py:1087` |
| MB-09 |  · toque noutra para trocar (fim de "Herdada do turno da OS-0421") | dica ⓘ | `areas/mobile.py:1049` | `areas/mobile.py:1087` |
| MB-09 | Tanque, volume e leitura; a foto do tíquete é a evidência. | dica ⓘ | `areas/mobile.py:1017` | `areas/mobile.py:1088` |
| MB-09det | Nunca voltam ao estoque livre: destino e responsável. | dica ⓘ | `areas/mobile.py:1130` | `areas/mobile.py:1220` |
| MB-10 | colheita: área e cargas do talhão · motorista: viagem | apagada | `areas/mobile.py:1314` | — |
| MB-10 | Aponte a área do turno e registre cada carga que sai do talhão; a balança pesa e recebe. | dica ⓘ | `areas/mobile.py:1245` | `areas/mobile.py:1319` |
| MB-10 | Área não gera produção: a produção do talhão nasce só da carga pesada e recebida. | dica ⓘ | `areas/mobile.py:1257` | `areas/mobile.py:1319` |
| CA-01 | (o agrônomo libera) no indicador A LIBERAR | dica ⓘ | `areas/campo.py:208` | `areas/campo.py:219` |
| CA-01det | término físico do escopo (ou dispensa autorizada do saldo) entra automaticamente em Em conferência … | dica ⓘ | `areas/campo.py:287` | `areas/campo.py:304` |
| CA-01det | O agrônomo ajusta e libera a v3 só para o saldo; as fichas do saldo passam à v3. | dica ⓘ | `areas/campo.py:296` | `areas/campo.py:303` |
| CA-01x-os0420 | impedimento é selo: a ordem segue Em execução e nenhum botão pula etapa | dica ⓘ | `areas/campo.py:346` | `areas/campo.py:364` |
| CA-02 | Se a liberação não estiver mais vigente, o saldo reaberto recebe o selo Pausada até renovar as cond… | dica ⓘ | `areas/campo.py:425` | `areas/campo.py:437` |
| CA-02 | Concluir execução não encerra a ordem com custódia, divergência ou conferência pendente. | dica ⓘ | `areas/campo.py:428` | `areas/campo.py:438` |
| CA-04 | Declarar o retorno não aumenta o estoque utilizável: só a quantidade medida e recebida entra no loc… | dica ⓘ | `areas/campo.py:564` | `areas/campo.py:573` |
| CO-02 | Hectares concluídos não geram quilogramas de estoque, e pesagens não duplicam a produção da mesma c… | dica ⓘ | `areas/colheita.py:247` | `areas/colheita.py:253` |
| CO-02det | Término físico entra automaticamente em Em conferência; encerrar exige cargas e apontamentos concil… | dica ⓘ | `areas/colheita.py:292` | `areas/colheita.py:308` |
| CO-04 | A entrada NÃO equivale a liberação comercial: produto em processo continua identificado … nunca som… | dica ⓘ | `areas/colheita.py:383` | `areas/colheita.py:390` |
| CO-05 | — fechar processo não libera lote … decisão posterior de qualidade não reabre a ordem encerrada | dica ⓘ | `areas/colheita.py:419` | `areas/colheita.py:435` |
| CO-05det | Concluir execução leva a Em conferência; fechar processo exige balanço conferido. | dica ⓘ | `areas/colheita.py:482` | `areas/colheita.py:506` |
| CO-06 | Lotes de campo vêm dos apontamentos das O.S. de colheita (parcela + data). … LMR Brasil: ANVISA … R… | dica ⓘ | `areas/colheita.py:669` | `areas/colheita.py:556` |
| CO-06 | Bloqueio invalida a elegibilidade das reservas afetadas e avisa o Comercial automaticamente — tenta… | dica ⓘ | `areas/colheita.py:543` | `areas/colheita.py:554` |
| CO-07 | o contrato barter que originou a reserva não é subtraído de novo. A oferta futura … não soma como e… | dica ⓘ | `areas/colheita.py:635` | `areas/colheita.py:651` |
| SU-01 | as 10 t em quarentena não entram e ficam como coberto se o laudo aprovar, somadas uma única vez. Cl… | dica ⓘ | `areas/suprimentos.py:295` | `areas/suprimentos.py:302` |
| SU-02 | Classe ABC financeira não substitui criticidade: Diesel é B em valor e Alta em criticidade. Limites… | dica ⓘ | `areas/suprimentos.py:343` | `areas/suprimentos.py:353` |
| SU-03 | Físico ≠ utilizável ≠ disponível. Custódia em campo fica fora do físico do depósito e não soma duas… | dica ⓘ | `areas/suprimentos.py:416` | `areas/suprimentos.py:425` |
| SU-04 | O fornecedor responde pelo portal externo com convite próprio, nunca por esta lista. A SOL-2026-07 … | dica ⓘ | `areas/suprimentos.py:584` | `areas/suprimentos.py:598` |
| SU-05 | O recebido já está dentro das liberações acumuladas e não é subtraído de novo do saldo contratual. | dica ⓘ | `areas/suprimentos.py:673` | `areas/suprimentos.py:689` |
| SU-05 | Recebimento parcial mantém o saldo do pedido aberto; o aceite físico acontece em Recebimentos. | dica ⓘ | `areas/suprimentos.py:676` | `areas/suprimentos.py:689` |
| SU-06 | Aceite físico não aprova o título: o título segue para Contas a pagar à parte. O retido em quarente… | dica ⓘ | `areas/suprimentos.py:828` | `areas/suprimentos.py:843` |
| SU-07 | Material entregue sai do disponível e passa à custódia da ordem; o consumo apontado no campo não re… | dica ⓘ | `areas/suprimentos.py:932` | `areas/suprimentos.py:945` |
| SU-07det | É o mesmo balanço que a conferência da ordem usa. Declarar a devolução não aumenta o utilizável do … | dica ⓘ | `areas/suprimentos.py:995` | `areas/suprimentos.py:1012` |
| SU-08 | Correção não apaga a operação original: o estorno cria movimento novo com vínculo. … | dica ⓘ | `areas/suprimentos.py:1083` | `areas/suprimentos.py:1099` |
| SU-09 | O contador não vê o saldo do sistema e os movimentos do escopo ficam suspensos entre o corte e o en… | dica ⓘ | `areas/suprimentos.py:1162` | `areas/suprimentos.py:1180` |
| PL-02 | “20 dias antes do plantio · DAP −20 · previsto para 25/09” — o produtor não digita sinal negativo. … | dica ⓘ | `areas/planejamento.py:256` | `areas/planejamento.py:275` |
| PL-03 | não ofertado como livre (cartão do Trator T1) | dica ⓘ | `areas/planejamento.py:318` | `areas/planejamento.py:380` |
| PL-03 | trator livre + implemento reservado ≠ conjunto livre | dica ⓘ | `areas/planejamento.py:320` | `areas/planejamento.py:380` |
| PL-03 | não fica verde por falta de notícia | dica ⓘ | `areas/planejamento.py:321` | `areas/planejamento.py:381` |
| PL-03 | Contadores são recortes que se sobrepõem — não somam o total da frota. … fonte: PCM + eventos da op… | dica ⓘ | `areas/planejamento.py:373` | `areas/planejamento.py:381` |
| PL-05 | Resolver compra ou manutenção revalida prontidão; não inicia máquina nem muda a agenda automaticame… | dica ⓘ | `areas/planejamento.py:502` | `areas/planejamento.py:516` |
| PL-05det | A parada do Trator T1 reduz a capacidade da janela uma única vez (já refletida em Capacidade e recu… | dica ⓘ | `areas/planejamento.py:551` | `areas/planejamento.py:556` |
| PL-06 | Parcelas não duplicam hectares de cobrança (312 ha); operações e materiais seguem a parcela correta. | dica ⓘ | `areas/planejamento.py:567` | `areas/planejamento.py:623` |
| VE-01 | Saldo final é o máximo factível sob capacidade e prazo — folga de outra classe ou dia não cobre est… | dica ⓘ | `areas/comercial.py:101` | `areas/comercial.py:186` |
| VE-02 | vira premissa só ao usar na gestão. Contrato futuro não é inventado: só instrumentos existentes nas… | dica ⓘ | `areas/comercial.py:221` | `areas/comercial.py:227` |
| VE-03 | Aceite registrado pelas duas partes, por versão. Confirmação automática só sob política prévia expl… | dica ⓘ | `areas/comercial.py:286` | `areas/comercial.py:291` |
| VE-06 | O ajuste financeiro fica vinculado ao caso — crédito não é emitido pelo retorno em si. Recolhimento… | dica ⓘ | `areas/comercial.py:544` | `areas/comercial.py:549` |
| LO-02 | Política v4: elegibilidade (presença, prontidão, doca livre, documentos) › janela em risco › … Tole… | dica ⓘ | `areas/logistica.py:360` | `areas/logistica.py:371` |
| LO-02 | A preparar → Em separação → Conferência → … Qualidade, financeiro e documentos são dimensões separa… | dica ⓘ | `areas/logistica.py:364` | `areas/logistica.py:372` |
| LO-02det | o rateio da instalação não se aplica a esta carga | dica ⓘ | `areas/logistica.py:438` | `areas/logistica.py:446` |
| LO-04 | Sugestão não despacha transportador. | dica ⓘ | `areas/logistica.py:573` | `areas/logistica.py:583` |
| GE-02 | Autorizar versão: só a Direção, pela caixa de Aprovações. | dica ⓘ | `areas/gestao.py:210` | `areas/gestao.py:216` |
| GE-02det | A matemática explica o desvio, mas não prova desperdício: pode ser ajuste técnico autorizado, condi… | dica ⓘ | `areas/gestao.py:239` | `areas/gestao.py:264` |
| GE-04 | Fonte oficial: ERP designado — aqui se propõe, aprova e concilia; … nunca conta duas vezes … não fi… | dica ⓘ | `areas/gestao.py:380` | `areas/gestao.py:388` |
| GE-06det | Fórmula: custo total da operação ÷ ha efetivamente tratados (apontados) | dica ⓘ | `areas/gestao.py:500` | `areas/gestao.py:525` |
| GE-06det | Fonte: lançamentos de custo documento a documento + apontamentos da O.S. | dica ⓘ | `areas/gestao.py:502` | `areas/gestao.py:525` |
| GE-08 | — o mesmo saco nunca garante dois contratos. | dica ⓘ | `areas/gestao.py:631` | `areas/gestao.py:646` |
| CF-01 | Origem: Cadastros › Pessoas e equipes (nome, função, habilidade e CREA). Aqui não se cadastra pesso… | dica ⓘ | `areas/configuracoes.py:221` | `areas/configuracoes.py:278` |
| CF-01 | Os comandos da O.S., do Estoque e do app leem esta tabela. Mudança vale para o próximo comando e nu… | dica ⓘ | `areas/configuracoes.py:224` | `areas/configuracoes.py:279` |
| CF-03 | Sincronizar envia ao ERP cada movimento uma vez por conteúdo: repetir não reenvia; … O app de campo… | dica ⓘ | `areas/configuracoes.py:326` | `areas/configuracoes.py:340` |
| CF-05 | Origem: Cadastros › Fazendas, áreas e talhões · conta a área cultivável dos talhões ativos de fazen… | dica ⓘ | `areas/assinatura.py:249` | `areas/assinatura.py:296` |
| CF-05 | (Configurações › Usuários e alçadas) · usuários sem limite · não entram na cobrança | dica ⓘ | `areas/assinatura.py:157` | `areas/assinatura.py:297` |
| CF-05 | Usuários sem limite e fora da cobrança. (nota dos planos) | dica ⓘ | `areas/assinatura.py:253` | `areas/assinatura.py:297` |
| CF-05 | só demonstração · avança a data da cobrança, não a dos outros módulos | dica ⓘ | `areas/assinatura.py:243` | `areas/assinatura.py:298` |
| CF-05 | O período fecha no último dia do mês e a fatura vence no dia 1 (exemplo, a decidir pelo proprietári… | dica ⓘ | `areas/assinatura.py:244` | `areas/assinatura.py:298` |
| BO-01 | Mínimo: cobra-se o maior entre o mínimo e preço × área (não se soma). Mudança: vale do dia 1 do pró… | dica ⓘ | `areas/plataforma.py:171` | `areas/plataforma.py:193` |
| BO-02 | a vencer, vencidas, pendentes ou em contestação | dica ⓘ | `areas/plataforma.py:51` | `areas/plataforma.py:146` |
| BO-02 | cobrada = mín(medida; contratada) | dica ⓘ | `areas/plataforma.py:52` | `areas/plataforma.py:146` |
| BO-02 | Isolamento: a plataforma vê área e cobrança por organização (e por fazenda na consulta contratual),… | dica ⓘ | `areas/plataforma.py:122` | `areas/plataforma.py:146` (PRIV, linha 19) |
| PT-02 | Cada versão submetida fica preservada — revisar antes do prazo cria nova versão; motivo de não sele… | dica ⓘ | `areas/parceiros.py:175` | `areas/parceiros.py:181` |
| PT-05det | — recusa no recebimento abre divergência, não devolve ao estoque apto. | dica ⓘ | `areas/parceiros.py:398` | `areas/parceiros.py:405` |
| ON-01det | Estoque, análise ou plantio nunca são completados com dados inventados. Área importada maior que a … | dica ⓘ | `areas/onboarding_backoffice.py:181` | `areas/onboarding_backoffice.py:186` |
| IC | esperando o mês certo, antes da necessidade (repetia o título do indicador) | apagada | `areas/inteligencia.py:228` | — |
| IC | comprando pela melhor cotação (repetia o título do indicador) | apagada | `areas/inteligencia.py:233` | — |
| MA | das OMs encerradas no sistema (indicador de custo) | apagada | `areas/maquinas.py:320` | — |

## Por tela (varredura combinada, caracteres · blocos)

Telas com texto longo cortado em 140 caracteres aparecem sem mudança nesta varredura mesmo quando a explicação saiu: CA-04, CO-05, GE-08, VE-02 e VE-06. Para elas, vale a varredura sem corte (`brutos/metrica.txt`).

| Tela | Antes (car. · blocos) | Depois (car. · blocos) | Diferença |
|---|---:|---:|---:|
| CF-05 | 648 · 6 | 157 · 2 | -491 |
| MB-08 | 1000 · 12 | 547 · 7 | -453 |
| MB-08x-recibo | 862 · 12 | 513 · 8 | -349 |
| MB-05det | 447 · 6 | 102 · 2 | -345 |
| PL-03 | 557 · 7 | 217 · 3 | -340 |
| MB-02 | 1011 · 13 | 678 · 8 | -333 |
| LO-02 | 280 · 2 | 0 · 0 | -280 |
| CF-01 | 269 · 2 | 0 · 0 | -269 |
| MB-05 | 416 · 6 | 156 · 2 | -260 |
| MB-03x-recibo | 333 · 4 | 80 · 1 | -253 |
| BO-02 | 296 · 4 | 55 · 1 | -241 |
| CA-02 | 228 · 2 | 0 · 0 | -228 |
| CO-06 | 416 · 4 | 193 · 3 | -223 |
| MB-10 | 282 · 4 | 60 · 1 | -222 |
| MB-09 | 285 · 5 | 91 · 2 | -194 |
| SU-05 | 192 · 2 | 0 · 0 | -192 |
| CA-01det | 264 · 2 | 90 · 1 | -174 |
| MB-02det | 418 · 7 | 253 · 4 | -165 |
| PL-02 | 140 · 1 | 0 · 0 | -140 |
| PL-05 | 140 · 1 | 0 · 0 | -140 |
| CO-02 | 140 · 1 | 0 · 0 | -140 |
| SU-04 | 280 · 2 | 140 · 1 | -140 |
| SU-07det | 347 · 4 | 207 · 3 | -140 |
| PL-05det | 989 · 10 | 849 · 9 | -140 |
| SU-08 | 140 · 1 | 0 · 0 | -140 |
| SU-02 | 213 · 2 | 73 · 1 | -140 |
| VE-01 | 280 · 2 | 140 · 1 | -140 |
| SU-06 | 140 · 1 | 0 · 0 | -140 |
| SU-03 | 200 · 2 | 60 · 1 | -140 |
| CF-03 | 249 · 2 | 109 · 1 | -140 |
| ON-01det | 140 · 1 | 0 · 0 | -140 |
| SU-09 | 191 · 2 | 51 · 1 | -140 |
| SU-07 | 140 · 1 | 0 · 0 | -140 |
| SU-01 | 188 · 2 | 48 · 1 | -140 |
| CO-04 | 190 · 2 | 50 · 1 | -140 |
| VE-03 | 140 · 1 | 0 · 0 | -140 |
| PL-06 | 277 · 2 | 140 · 1 | -137 |
| IC | 358 · 5 | 231 · 3 | -127 |
| GE-06det | 344 · 6 | 217 · 4 | -127 |
| PT-02 | 114 · 1 | 0 · 0 | -114 |
| MB-01 | 156 · 3 | 46 · 1 | -110 |
| CO-02det | 105 · 1 | 0 · 0 | -105 |
| MB-07 | 101 · 2 | 0 · 0 | -101 |
| MB-03 | 142 · 3 | 45 · 1 | -97 |
| CO-05det | 362 · 4 | 281 · 3 | -81 |
| LO-04 | 78 · 1 | 0 · 0 | -78 |
| PT-05det | 123 · 1 | 52 · 1 | -71 |
| CA-01x-os0420 | 534 · 5 | 463 · 4 | -71 |
| CO-07 | 140 · 1 | 70 · 1 | -70 |
| MA-05 | 113 · 2 | 51 · 1 | -62 |
| MA | 113 · 2 | 51 · 1 | -62 |
| MA-01 | 113 · 2 | 51 · 1 | -62 |
| GE-02 | 57 · 1 | 0 · 0 | -57 |
| MB-04 | 161 · 3 | 105 · 2 | -56 |
| MB-09det | 354 · 6 | 301 · 5 | -53 |
| LO-02det | 115 · 1 | 64 · 1 | -51 |
| CA-01 | 45 · 1 | 0 · 0 | -45 |
| GE-02det | 247 · 3 | 210 · 3 | -37 |
| BO-01 | 331 · 3 | 318 · 3 | -13 |
| GE-04 | 140 · 1 | 137 · 1 | -3 |

Telas sem mudança na varredura combinada (o texto à vista é dado, trava, rótulo ou está fora do escopo; algumas só por causa do corte em 140): AG-07, OS-0424-ficha, PCOM, CD-07, AG-01det, CO-03, PL-02det, AG-04det, VE-02, MB-06, GE-05, CA-04, PL-01, IN-01, CA-03det, IV, CD-03, MOD-OUT, SU-05det, AG-03det, VE-06, PT-02det, SU-03det, GE-08, CD-01, CO-05, OS-0424-app, MOD-COM, MOD-AGR, BEN, EXPED, IR-03det, PT-04det, IN-03, MOD-CFG, VEN, EST.

## Ficou à vista, por ser dado, trava, rótulo ou documento

| Tela | Texto | Motivo |
|---|---|---|
| AG-07 | Fonte: AGROFIT/MAPA · dados abertos (CC-BY) · arquivo de 02/10/2026 · 4.409 produtos com registro | Atribuição da licença CC-BY e data da base: a licença pede a fonte à vista |
| OS-0424-app | Complete com água até o volume do tanque, na ordem da instrução liberada. | Instrução técnica de preparo da calda (ordem de mistura), não explicação de tela |
| OS-0424-ficha | Tanque útil… Coloque o produto indicado e complete com água… · Ficha impressa… perde a validade… | Ficha impressa para uso sem internet: papel não tem ⓘ, e a validade da versão é trava |
| CO-05det | L39-120/121 seguem Aguardando inspeção até a decisão em CO-06, mesmo com o processo encerrado. | Estado dos lotes e impedimento até a decisão da qualidade |
| MB-09det | Ação de Zé, executante · você vê a ordem, sem alterar. | Trava: diz por que os comandos estão indisponíveis para o perfil |
| MB-04 | Escolha a máquina: a falha vai para a Manutenção. | Campo obrigatório: sem máquina, a falha de equipamento não grava |
| MB-04, MB-09 | Sem foto · a foto (e a voz) são simuladas neste protótipo. | Rótulo de demonstração |
| BO-01, CF-05 | Todos os valores são exemplo, a decidir pelo proprietário (DEC-01, DEC-05, DEC-09) | Aviso de exemplo a decidir pelo proprietário |
| CF-03 | Fila do ERP: 0 movimentos · app de campo: Com sinal (simulado) · nenhuma credencial existe nesta demonstração | Estado e rótulo de demonstração |
| CO-06 | Demonstração · pós-colheita, laudos e destinos sintéticos | Rótulo de demonstração encurtado; a origem dos lotes e a fonte do LMR foram para o ⓘ |
| PL-03 | livre hoje · 25/09 reservado (OS-0430) elegível só após confirmação do PCP | Trava: a máquina só é elegível depois da confirmação |
| PT-04det | … as próximas só liberam com a <documento> | Trava da liberação condicional |
| EXPED | nada a programar: reserve lote em Contratos e pedidos | Estado e próximo passo com verbo |
| MA | sem encerradas com vencimento registrado · set/2026 | Por que o indicador não é calculável (estado do dado) |

Os demais blocos que ficaram são dado ou estado: contexto do registro, números, recibos, linhas do tempo, cartões de máquina e alternativas de decisão (PL-05det).

Não mexi nos estados vazios ("Quando o escritório liberar…"), que só aparecem com a lista vazia, nem nas dicas de campo de formulário.

## Pendências com o Codex

Tiveram commits do Codex depois de 10/10: `areas/processo_estoque.py`, `areas/processo_os.py`, `areas/processo_safra.py`, `cenario.js/.py`, `conferencia_diaria*`, `plano_referencia*` e `cal01.js`. Nenhum foi editado.

Nas telas deles, a varredura achou só a linha de estado do EST: "2 notas a conferir · em quarentena: KCl 60% 10.000 kg · pedidos com saldo a entregar: …". Ela é dado e não precisa sair.

Não há frase explicativa pendente com o Codex.

## Fora do escopo (Mapa e faixa de filtros com o integrador)

Não editei `areas/inicio.py`, `solo.js` nem a faixa "Filtros desta tela" (`mf-tela`). Na varredura, as telas do `inicio.py` têm:
- IN-01: ocorrências agrupadas, que são dado;
- IN-03: "Encerrar OS-0417 depende de receber 10 sc em custódia…", que é trava e fica.

Não houve nada a desfazer.

## Testes (executados no render de `int/texto2`, `SAFRION_DADOS=sintetico`, um teste de navegador por vez)

Comando base, de `tools/prototipo/v37/gen37`: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <teste>`.

| Teste | Resultado | Observação |
|---|---|---|
| `textos_soltos_test.py` (novo) | 263 OK · 0 falhas · 63 telas | T 113, D 103, F 42, Q 3, A 1, E 1 |
| `textos_soltos_test.py` com `RENDER_DIR=` render limpo de `48f570b` (contraprova) | 41 OK · 222 falhas (reprova, como esperado) | Os 113 T reprovam |
| `paginas_scan_test.py` | 4 OK · 0 falhas | 144 páginas × 2 tamanhos sem erro de JS e sem rolagem lateral |
| `ds_unit_test.py` | OK 29/29 | |
| `links_ocultos_test.py` | 15/16: falha E1b | Já falha na base: `est_validade_conc_pendente.js` (Codex) chama `cenLiberar`. Nenhum dos dois arquivos mudou |
| `nav_modulos_test.py` | 15 OK · 0 falhas | |
| `busca_unica_test.py` | 7 OK · 0 falhas | |
| `regras_toque_test.py` | 5 OK · 0 falhas | |
| `mbtest.py` | 0 falhas | Oráculo "13,5 mm (OS-0422)" passou para o dado novo "OS-0422 · 13,5 mm" |
| `config_test.py` | 87/88: falha A14 | A14 (2 buscas na tela) já falha na base, pela busca única. A9 agora confere "Pessoas com acesso: 14 · fora da cobrança" à vista e a origem no ⓘ |
| `cotest.py` | 40/53 | As mesmas 13 falhas da base (40/53 no render limpo). CO-04 e CO-05 conferem a regra no ⓘ |
| `ds_test.py` | 67/69: falham D8 e D8b | Já falham na base (fonte do Mapa no IN-04, fora do escopo) |
| `app_cenario`, `app_mb02det`, `app_mb03_turno`, `app_mb03x`, `app_mb04`, `app_restaurar`, `app_saldo_zero`, `app_os0424` | todos verdes | 15, 8, 11, 7, 6, 4, 12 e 9 OK |
| `ma_app_test.py`, `ma_app_fluxo_test.py` | 36/36 e 24/24 | |
| `assinatura_test.py`, `componentes_test.py` | 45 OK e 3 OK | |
| `plataforma_test.py` | 20/22: falham A14a e A14d | Já falham na base (busca única) |
| `sutest`, `pltest`, `lotest`, `partest`, `obotest`, `inteligencia_nav_test` | todos verdes | |
| `getest.py` (falha `pc088_unico`) e `vetest.py` (falha OF-103 editada) | 1 falha cada | As mesmas da base, no render limpo |

Ordem das rodadas: `textos_soltos`, `paginas_scan`, `ds_test`, `busca_unica`, `nav_modulos`, `regras_toque`, `mbtest`, `ds_unit` e `links_ocultos` rodaram depois da última mudança de código, a correção do `g2lib.js`. Os demais rodaram antes dela, sobre as mesmas telas. A correção só muda o anúncio e o realce do estado do cabeçalho; o `ds_test` (partes C e D) e o `textos_soltos_test` (A) cobrem esses pontos depois da correção.

"Já falha na base" significa que a mesma falha aparece com o teste da base (`git show 48f570b:…`) contra o render limpo de `48f570b`. Esse render foi montado em pasta à parte, com `git archive`. A conferência foi executada.

## Contraprova

`textos_soltos_test.py` contra o render limpo de `48f570b`: 41 OK · 222 falhas (reprova, como esperado).
- As 113 verificações T reprovam: as frases estavam à vista.
- 101 das 103 D reprovam. As 2 que passam (CA-01 e LO-04) já tinham a regra no rodapé antigo.
- Q reprova: não havia ⓘ no app. A reprova: o anúncio era "Tela: … · i".
- Nenhum erro de JS.
