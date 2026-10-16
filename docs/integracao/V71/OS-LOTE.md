# OS-LOTE · Juntar O.S. e reprogramar O.S. futuras em lote

Pedidos do proprietário em 16/10/2026, com o texto melhorado para implantar.

> "na hora de liberar e executar O.S o agronomo tem que ter opcao de agrupar O.S em mais de 1 talhao com mesma atividade e insumos e doses, enfim melhore essa minha ideia e implante da melhor forma possivel baseado nas melhores praticas de gestao agricola e agronomica, mas ultra simples, rapido e pratico, sem burocracia."

> "Se no meio da safra o agronomo precisar reprogramar todas O.S futura da safra/fazenda de 1 ou mais talhoes, tem que ser rapido, facil e intuitivo, tirando ou incluindo inusmos, mudando data, cancelando alguma entrada, etc. Somente das O.S ainda nao aprovadas/em execucao, concluidas."

## Acordo curto (AGENTS §3.4)

| Campo | Conteúdo |
|---|---|
| ID / resultado útil / persona | **OS-LOTE**: o agrônomo junta numa O.S. só as aplicações iguais de vários talhões e reprograma, de uma vez, as O.S. futuras de um ou mais talhões. Persona: agrônomo/coordenador. |
| PRD / fora do escopo | PRD 41 e 73.9 (aprovação individual), 24 (servidor é a autoridade), CMD-06 (liberar), CMD-42 (aprovar), ENG-011/013/021/022. **Fora:** O.S. já aprovada, liberada, em execução, em conferência ou encerrada; mudar o plano agronômico (o plano continua; só as O.S. mudam). |
| Autor / revisor / integrador | Claude (frente) / Codex / Claude (composição). |
| Base | Ponta da `claude/v44-v69-mapa` no início da frente. Arquivos: `areas/processo_os.py`, o cenário (`cen*` no `g2lib.js`), os testes novos. |
| Aceite e verificação | Critérios A e B abaixo. Teste novo `os_lote_test.py` (unidade em node e navegador), com contraprova. `os_cenario`, `tabelas_os` e `ds_1610` continuam verdes. |
| Estado | Na fila. Abre quando uma das 3 frentes em curso entrar na versão publicada (VEL §3.6). |

## A · Juntar O.S. iguais numa O.S. só

**Boa prática:**
- Uma calda/operação que atende vários talhões vizinhos com a mesma receita reduz deslocamento, preparo de calda e sobra de tanque.
- A rastreabilidade continua por talhão: área, dose aplicada, data, carência e custo.

### Quando o sistema sugere (sem o agrônomo procurar)

Duas ou mais O.S. em **A liberar, ainda não aprovadas**, com tudo isto igual:
- mesma fazenda e mesma safra;
- mesma cultura;
- mesma operação;
- mesmos insumos com a **mesma dose por hectare**;
- janelas que se cruzam.

Talhões diferentes.

### Como fica na tela (2 cliques)

1. Na lista de O.S., cada grupo possível aparece **uma vez**, como aviso pequeno no alto do bloco "Ordens por fase" (AVI-01).
   - Texto: "3 O.S. podem virar 1: Fungicida 1ª aplicação · T1, T2, T4".
   - Botão: "Juntar".
   - O ⋯ da linha também oferece "Juntar com…" (TAB-05).
2. "Juntar" abre uma confirmação curta, sem formulário:
   - talhões e área total;
   - insumos e quantidade total (dose × área de cada talhão);
   - janela comum;
   - recursos (os da O.S. mais cedo, com a checagem de conflito que já existe).
3. Ao confirmar, nasce **uma O.S.** com os N talhões. Por padrão ela fica "A aprovar"; quem tem a alçada de aprovar ganha "Juntar e aprovar" num toque.
   - As O.S. de origem ficam **Canceladas · motivo "juntada na OS-xxxx"**: vão para o histórico e não contam em demanda nem custo.
   - As reservas de insumo passam para a O.S. nova, sem reservar duas vezes.
4. Enquanto não for liberada, "Separar" desfaz: as O.S. de origem voltam como estavam.

### Execução (app de campo e O.S.)

- A O.S. juntada mostra os talhões na ordem de execução sugerida.
- O apontamento continua **por talhão**: área feita, dose, horário, clima.
- A carência e a reentrada contam por talhão, pela data em que cada um foi aplicado.
- O custo é rateado pela área de cada talhão.

### Travas (com o dano que evitam)

| Trava | Dano evitado |
|---|---|
| Receita diferente (produto, dose/ha, cultura) não junta | Aplicar dose ou produto errado num talhão: resultado técnico e lei (bula, receituário) |
| Janelas sem cruzamento não juntam | Aplicar fora do estádio ou da janela recomendada |
| O.S. aprovada, liberada ou em execução não junta | Mudar o que já foi decidido e autorizado sem nova decisão |
| A soma das reservas vira a reserva da nova O.S. (transferência, não soma nova) | Estoque reservado duas vezes |
| Uma aprovação individual para a O.S. juntada (DEC-1610-03) | Execução sem aprovação agronômica |

### Critérios de aceite (A)

1. As O.S. iguais em "A liberar" aparecem como sugestão; O.S. com dose, produto, cultura ou janela diferentes não aparecem.
2. Juntar 3 O.S. leva no máximo 2 cliques do aviso até a O.S. criada.
3. Área, quantidade de cada insumo e custo da O.S. nova somam exatamente as de origem (decimal).
4. As de origem ficam Canceladas com o motivo "juntada na OS-xxxx". A reserva total de cada insumo não muda (contraprova: somar em vez de transferir reprova).
5. "Separar" devolve as O.S. de origem iguais às de antes, nos ids, nas quantidades e nas reservas.
6. Apontamento por talhão: o app e a conferência mostram cada talhão; a carência conta por talhão.
7. A O.S. juntada exige aprovação antes de liberar (CMD-42 → CMD-06).
8. Mesmo comando repetido com a mesma chave de idempotência não cria uma segunda O.S.

## B · Reprogramar O.S. futuras em lote

**Boa prática:** o replanejamento do meio da safra (chuva, praga, troca de produto, falta de insumo) acontece num lugar só, com prévia do efeito. Isso evita editar uma O.S. por vez e esquecer alguma.

### Entrada

- Botão secundário **"Reprogramar"** na barra da Ordem de Serviço.
- No Planejar safra, ⋯ do talhão: "Reprogramar O.S. futuras".
- A tela já chega com a fazenda, a safra e o talhão herdados (AGENTS §3.3).

### Painel lateral, uma tela, 3 passos curtos

1. **Quais O.S.:**
   - talhões (chips, vários);
   - "a partir de" (hoje por padrão);
   - operação (opcional).
   - A lista mostra as O.S. elegíveis, todas marcadas.
   - As não elegíveis aparecem só como contagem com o motivo, sem entrar no lote: "4 fora: 2 aprovadas, 1 em execução, 1 encerrada".
2. **O que mudar** (uma ou mais ações, cada uma numa linha):
   - **Datas:** deslocar ± N dias ou definir uma data.
   - **Incluir insumo:** produto do cadastro (busca) e dose/ha.
   - **Retirar insumo.**
   - **Trocar produto**, mantendo ou ajustando a dose.
   - **Alterar dose.**
   - **Cancelar O.S.**, com motivo curto obrigatório: lista de toques (Chuva, Praga controlada, Mudança de plano, Outro).
3. **Prévia e aplicar.** Antes de gravar, mostra:
   - por O.S., "antes → depois";
   - o resumo: insumos a mais e a menos por produto, custo Δ (R$ e R$/ha) e O.S. canceladas;
   - os bloqueios, com o motivo na linha da O.S.
   - Um botão: **"Aplicar em N O.S."**. Depois, aviso com **Desfazer**.

### Regras

- **Só O.S. não aprovadas.** Aprovada, liberada, em execução, em conferência, encerrada e cancelada ficam fora, com o motivo à vista.
  - Para mudar uma aprovada, o agrônomo usa o caminho de hoje: ajustar gera nova versão e volta para aprovação.
- **Cada O.S. alterada ganha nova versão** (o `osc_ajustar` de hoje).
  - Grava no histórico: "Reprogramada em lote por <pessoa> em <data>: <ações>".
  - Continua "A aprovar".
- **Demanda e reservas recalculadas na mesma gravação.** Compras recebe a nova demanda. Reserva que sobrar volta ao estoque.
- **Tudo ou nada:** um comando, com chave de idempotência; se uma O.S. trava, nada é gravado sem a pessoa ver.
- **O plano agronômico não muda.** Depois de aplicar, a mensagem oferece, como atalho e não como passo obrigatório: "Atualizar o plano também?".

### Travas (dano que evitam)

| Trava | Dano evitado |
|---|---|
| Produto incluído ou trocado precisa ter registro para a cultura e alvo (Agrofit) | Aplicação ilegal ou ineficaz |
| Dose acima da bula bloqueia | Fitotoxidez, resíduo, lei |
| Nova data + carência depois da colheita prevista bloqueia aquela O.S. | Colher com resíduo acima do limite |
| Data fora da janela do estádio: só aviso | Eficácia (o agrônomo decide) |
| O.S. fora do lote não muda | Alterar o que já foi aprovado ou executado |

### Critérios de aceite (B)

1. A partir da O.S. ou do Planejar safra, reprogramar 5 O.S. de 2 talhões (deslocar +7 dias e trocar um produto) leva no máximo 8 cliques e 2 campos digitados. Medir no teste.
2. Só O.S. não aprovadas entram. As demais aparecem com o motivo e não mudam (contraprova: incluir aprovada reprova).
3. A prévia bate com o resultado gravado: datas, insumos, quantidades, custo e Δ de demanda por produto.
4. Produto sem registro para a cultura, dose acima da bula e carência depois da colheita bloqueiam a O.S. na prévia, com o motivo.
5. Cancelar exige motivo. As canceladas saem da demanda e devolvem a reserva.
6. "Desfazer" volta tudo como antes, nas versões, na demanda e nas reservas.
7. Repetir o comando com a mesma chave não aplica duas vezes.
8. O histórico de cada O.S. mostra a reprogramação, quem fez e quando.

## Testes (proporcionais ao risco: estoque, demanda e aprovação)

- **Unidade (node):**
  - elegibilidade;
  - igualdade de receita;
  - somas em decimal;
  - transferência de reserva;
  - desfazer e separar;
  - idempotência;
  - travas de registro, bula e carência.
- **Navegador:**
  - fluxo A e fluxo B completos, a 1440 e a 390 px (toque de 44 px);
  - teclado;
  - sem erro de JS;
  - cliques medidos.
- **Contraprova** em cada regra de estoque e de aprovação.
- **Fotos** na galeria (skill `padrao-safrion`).
