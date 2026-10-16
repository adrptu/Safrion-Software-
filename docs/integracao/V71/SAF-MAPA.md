# SAF-MAPA · Planejar a safra no mapa

> Proprietário, 16/10/2026: "Coloque opção de planejar Safra no modo de visão mapa clicando nos talhões e colocando culturas, planos, etc e com opções rápidas de aplicar a todos e talhões, etc. igual ou melhor que o PIMS e Gatec web fazem. Vendo ao vivo, cultura, variedade e plano agronômico alocado."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: SAF-MAPA / planejar cultura, variedade e plano de vários talhões de uma vez, tocando no mapa, vendo o resultado ao vivo / agrônomo e gerente de PCP
Requisitos do PRD e fora do escopo: Planejar safra (SAF, etapa 2), master-detail (PRD 4.2/4.3), DS cap. 74 (seletor de visão, BOT-01, SEL-01/02), SAF-C01/C02, AGR-02; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa a partir de d482a07 / areas/processo_safra.py, safra.js, peça comum do desenho de talhões (hoje em areas/inicio.py e talgeo.js), testes novos saf_mapa_unit.js e saf_mapa_test.py
Aceite e comando de verificação: M1–M12 abaixo / node saf_mapa_unit.js; python3 -B saf_mapa_test.py; mais os testes de SAF tocados
Estado / impedimento / próximo passo: especificado; entra depois da autoria ativa (Cadastros) e das correções da Onda 0; ordem entre OS-LOTE, SOLO-VRA e SAF-MAPA conforme o pedido do proprietário
```

## Referências (AGENTS §3.3)

- **PIMS e GAtec citados pelo proprietário.** A busca de 16/10 não achou documentação oficial das telas de mapa de nenhum dos dois.
  - GAtec: só a página da Senior, com capacidades gerais (planejamento da safra, plantio e colheita, sem tela de mapa descrita).
  - PIMS: aparece em vagas do setor sucroenergético como ferramenta de planejamento e programação.
- **Não se copia recurso não verificado.** O aceite se mede contra o fluxo pedido pelo proprietário e pela contagem de cliques antes e depois (§3.3).

## Decisões dos agentes (delegação do proprietário)

1. **Lugar.** Planejar safra › etapa 2 ("Defina cultivos e plano"). Ganha o seletor de visão **Tabela | Mapa**, o mesmo componente comum da DS (como Tabela | Cartões).
   - Não é tela nova: mesmos dados, mesmos comandos e mesmo contexto Fazenda · Safra.
   - A Tabela continua como está e abre por padrão. A visão escolhida fica lembrada por usuário (padrão que já existe).
2. **Mapa.** A mesma geometria de talhões do Mapa (IN-04), extraída para uma peça comum. Não há cópia do desenho, e vale para as duas fazendas.
   - **Cor:** pela cultura, com legenda que mostra a área de cada cultura.
   - **Rótulo ao vivo:** talhão · cultura · variedade · plano (abreviado se faltar espaço; completo na dica e no `aria-label`).
   - **Sem cultivo:** contorno tracejado, "Sem cultivo".
   - **Cultivo sem plano:** amarelo, "Sem plano".
   - **Talhão indisponível** (perene ou ocupado em outra safra aberta, SAF-C01/C02): cinza, com o motivo na dica.
   - **Safra encerrada:** só consulta.
3. **Seleção.**
   - Toque ou clique no talhão alterna a seleção (contorno verde e marca).
   - "Selecionar área" (retângulo) reaproveita a ferramenta do IN-04.
   - **Atalhos de um toque:** Todos · Sem cultivo · Sem plano · Por cultura (lista curta) · Limpar.
   - Contador: "N talhões · X ha".
   - Esc limpa. Talhão indisponível não entra na seleção.
4. **Painel lateral "Planejar N talhões",** com uma primária.
   - **Campos:**
     - Cultura: um toque, lista das culturas cadastradas;
     - Variedade: filtrada pela cultura, do cadastro;
     - Plano agronômico: filtrado pela cultura, só os publicados, com a mesma avaliação de compatibilidade da Tabela;
     - Plantio: data com atalhos dentro da janela do plano;
     - Meta: sugerida pela cultura ou pelo plano, editável.
   - **Pré-preenchimento:** campo com o mesmo valor em todos os selecionados vem preenchido; com valores diferentes mostra "vários" e só muda se a pessoa mexer.
   - **Primária:** **"Aplicar a N talhões"** (verbo + objeto, BOT-01).
   - **Opção rápida no topo do painel:** "Aplicar o plano a todos os talhões de <cultura> sem plano".
5. **Ao vivo.** O mapa recolore e reescreve os rótulos no mesmo instante, e a Tabela mostra o mesmo, porque o estado é um só.
   - Faixa de números: área planejada / área da fazenda; área e % por cultura; talhões sem plano; custo estimado dos planos (R$/ha × ha, a mesma conta da etapa 3).
6. **Regras: nenhuma nova.** O mapa chama os mesmos comandos da Tabela (aplicar plano, gravar cultivo), com a mesma chave de idempotência e as mesmas travas.
   - Plano incompatível com a cultura: recusado com motivo, por talhão.
   - Área do cultivo = área do talhão. Dividir talhão em parcelas continua na Tabela.
   - Aplicação parcial: os que passaram gravam, os recusados ficam listados com o motivo, como na aplicação em lote de hoje.
   - **Desfazer** a última aplicação (UX-04): o toast traz "Desfazer", que volta os cultivos tocados ao estado anterior. É um comando, não apaga o histórico.
7. **Acessibilidade e celular.**
   - Os talhões do mapa são focáveis e têm nome acessível.
   - O painel lista os talhões selecionados, com remover por item; o teclado faz tudo sem o mapa.
   - A 390 px o mapa ocupa a largura e o painel vira folha inferior.
   - Alvos de 44 px no toque.

## Aceite

| ID | Caso | Oráculo |
|---|---|---|
| M1 | Etapa 2, visão Mapa | os talhões da fazenda do contexto, com cor da cultura, rótulo cultura · variedade · plano, "Sem cultivo" e "Sem plano" nos casos; legenda com área por cultura |
| M2 | Selecionar 3 talhões tocando e aplicar Soja · variedade X · plano Y | os 3 gravados; mapa e Tabela mostram o mesmo na hora; faixa de números atualizada |
| M3 | Atalho "Sem cultivo" + aplicar | só os talhões sem cultivo mudam; os outros intactos |
| M4 | "Aplicar o plano a todos os talhões de Soja sem plano" | os talhões de soja sem plano recebem o plano; os de soja com plano não mudam |
| M5 | Plano incompatível (plano de mamão em soja) | recusado com motivo por talhão; nada gravado nesses |
| M6 | Talhão perene ou ocupado em outra safra | cinza, não selecionável, motivo na dica (SAF-C01/C02) |
| M7 | Seleção com variedades diferentes | campo Variedade mostra "vários" e não sobrescreve se não for mexido |
| M8 | Desfazer | volta os cultivos tocados ao estado anterior; o mapa e a Tabela também |
| M9 | Recarregar | o planejado continua (estado gravado, não de memória) |
| M10 | Teclado (sem mapa) e 390 px (toque) | o mesmo resultado de M2; nada sai da janela |
| M11 | Safra encerrada | só consulta: sem seleção nem painel |
| M12 | Cliques e digitação de M2 e M4, Tabela × Mapa | contados no teste; o Mapa não pode exigir mais que a Tabela |

**Contraprova:** a versão publicada antes não tem a visão Mapa e reprova M1–M10.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Desenhar ou dividir talhão em parcelas no mapa | pedido do proprietário; hoje "Dividir" fica na Tabela |
| Sugestão automática de cultura por rotação ou histórico | decisão do proprietário sobre regra de rotação; IA desligada até a estimativa de custo |
| Copiar a safra anterior inteira | EX-14, quando entrar |
| Comparação de recursos com PIMS ou GAtec | fonte oficial ou demonstração acessível |
