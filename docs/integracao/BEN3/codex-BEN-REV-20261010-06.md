# Codex BEN-REV-20261010-06 (PR #47, 6093132750) — aceite adicional para o DESENHO da rodada 3

Reproduções do Codex (Node, motor original, sintético):
1. OB-0110 em conferência, entrada 600 kg, única saída 10 kg estornada, custódia 60: benCxSobra retorna 60, esperado 0. ATENÇÃO: benEmProc também retorna 0 por depender da etapa/conclusão; ampliar só o ternário da benCxSobra para conferência usando benEmProc NÃO corrige. A necessidade residual tem de considerar entradas e saídas válidas independentemente do estado visual.
2. Dois lotes elegíveis 500+420, sem reserva/quarentena: benCaixasLivres retorna 500, há 920. Contar e reservar devem usar o MESMO conjunto de lotes elegíveis, com linha/proveniência por lote e TUDO-OU-NADA se faltar saldo.
3. Devolução já recebida: QA-A solicitou/recebeu/devolveu 60, custódia 0; único lote com 100 físicos e 80 reservados a QA-B. cenEntregar(QA-A,60,Rui) aceita e deixa físico 40/reservado 20, enquanto QA-B continua precisando 80. Além do saldo fantasma, a entrega precisa respeitar a reserva da PRÓPRIA requisição, não reduzir a reserva agregada alheia por Math.max.
Errata do Codex: o caso "conference-all-custody" do harness 9/9 tinha expectativa 60 e confirmava a regra defeituosa — retirado.

Aceite adicional:
- Separar necessidade restante, reserva por requisição/lote, custódia, consumo, devolução recebida e quarentena; devolver sobra NÃO autoriza nova entrega sem reserva legítima.
- Distinguir devolver SOBRA de devolver material para SUBSTITUIÇÃO: não alterar cegamente cenSaldoEntregar para todos os domínios sem conferir o contrato PRD 42.1 e O.S./app/SUP. Comando/refeitos materiais reabrem só as dependências afetadas.
- Formulário guiado recebe ordem/REQ/lotes e o limite da sobra; revalida quantidade/estado/versão ao confirmar; se obsoleto, recusa sem escrita e oferece recuperação.
- Repetição de Enter não avança a operação seguinte; Esc/voltar preservam rascunho ou confirmam descarte conforme DS; retorno do Estoque preserva a origem.
- Testes de conservação por sequência com SEMENTE FIXA e registro da MENOR sequência reprodutora. Cobrir também falta no segundo lote: nenhuma reserva parcial órfã; estorno/devolução na origem e a outra ordem intacta.
- Devolver desenho/decisões e a primeira fonte estável com diff/brutos no pacote docs/integracao/BEN/rod3/. Gemini entra na crítica do delta material.

## Acréscimo (editado 03:09 UTC) — Gemini BEN-GEMINI-20261010-05 e limite adicional
- Gemini Pro/HIGH confirmou os três mecanismos (só análise de fonte e brutos, sem execução própria).
- ADOTAR: balanço de massa independente da etapa; proteção da reserva por requisição.
- NÃO ADOTAR como receita global: subtrair simplesmente o devolvido em cenSaldoEntregar (precisa preservar a distinção sobra/substituição e o contrato dos demais consumidores: PRD 42.1, O.S., app, SUP).
- Somar lotes sem reservar por lote é insuficiente.
- Os dois testes sugeridos pelo Gemini repetem os recortes já executados: reutilizar, não repetir.
- LIMITE ADICIONAL (aceite transitivo, não defeito reproduzido): o desenho tem de tratar a sequência
  "devolução válida → outra ordem reserva → estorno posterior de descarte/saída".
  Recalcular a necessidade; se surgir falta, mostrar impedimento recuperável e solicitar reposição com reserva legítima;
  nunca inventar custódia, consumir reserva alheia ou impedir o registro correto do estorno.
  Devolver contraprova junto da rodada 3.
