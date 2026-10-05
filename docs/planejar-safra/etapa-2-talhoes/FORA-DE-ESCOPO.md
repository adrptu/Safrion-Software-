# Fora do escopo · etapa 2 "Talhões e cultivos" (v2)

Cada item diz por que fica de fora e o que vale até lá. Acompanha [`ESPECIFICACAO.md`](ESPECIFICACAO.md) e [`DECISOES.md`](DECISOES.md).

| Item | Por que fica de fora | Até lá |
|---|---|---|
| Faixa gráfica de área × tempo na linha | Célula SVG nova no g2lib, tema escuro, `aria-label` por linha; caro a 390 px | Colunas Livre a partir de, Ocupa até e Fim por |
| Indisponibilidade por período (pousio, reforma, arrendamento, embargo) | O PRD não tem regra (busca em PRD.md só acha recursos e máquinas); depende da resposta do dono | Talhão aparece Livre; Inativo no CD-01 se sair de uso de vez (só vale no Planejar com o PR-C) |
| Encerramento do ciclo perene (erradicação/renovação) | Sem regra no PRD; "Excluir" apaga o histórico (RF-DOM-001, PRD.md:2713) | Perene sem fim; T7 e C1 nunca ficam livres; o Pivô 12 já é ciclo novo (lg12) |
| Registro de colheita real (fonte do "Observado") | Pede comando e tela próprios | O serviço aceita `colheita_real`; nenhum dado usa |
| Proteção na liberação da O.S. (CMD-06) da sucessora sem colheita real da antecessora | É da execução, não do planejamento | Pendência "Sobreposição prevista" visível |
| Editor de momento da operação (PRD 39.3, "Ajustar data da atividade") | Não existe no protótipo | "Mudar plantio ›" e "Informar colheita ›" |
| Duração da colheita na ocupação (área ÷ rendimento, CAL-14) | Depende da etapa de operações (paralelo) | Data de colheita do plano = início da colheita; folga explícita |
| Sucessão dentro da mesma safra ("Planejar depois") | Hoje também não existe (`safra.js:530`) | Usar a safra da safrinha (Safrinha 2027) |
| Consórcio (PRD 43.1) | Pede modelo explícito | — |
| Planejar vários talhões em lote (PRD 39.2 passo 3) | Outra fatia | Planejar › por linha; Aplicar plano em lote continua |
| Folga por cultura | Parâmetro único até o dono responder | Folga única |
| Chips de cultura, sugestões de Variedade, atalho de data no painel | Tipos de campo novos no g2lib | Listas como hoje; Plantio vem do PlantioMin |
| CD-01det e `_aloc` no mesmo serviço (`areas/cad_fazendas.py:449-462`) | Outra tela | Dois cálculos de "livre" (risco ENG-011); `ocupacao.py` já fica pronto |
| Limite do plantio ao período da safra no `cultCheck` (`safra.js:527-537`) | Achado separado (OC-R5) | Plantio fora do período é aceito, com as travas da R-14 |
| Classificar as pendências antigas da DEMO-09 | Outra fatia | — |
| Itens do §6.3 da especificação | Registrar sem mexer | — |
