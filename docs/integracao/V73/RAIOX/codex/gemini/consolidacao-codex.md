# Raio-X — consulta focal Gemini e leitura crítica Codex

Base da avaliação Codex: b291746d. Confronto Claude: 45b097f. Consulta única em 17/10/2026 pelo adaptador Vertex existente, Gemini real gemini-3.1-pro-preview/HIGH; resposta CMjSao3TFOqDn_APgPSKuAk, STOP. Pacote de 6863 bytes inspecionado, sintético, sem dados reais/segredos. A resposta é parecer textual; Gemini não executou testes nem acessou fontes/código. As referências metodológicas pedidas não vieram identificadas. Nenhuma certificação ou aprovação de implantação.

## Direção proposta para revisão do Claude
- Manter data de disponibilidade/proveniência, população na origem, horizonte fixo e arquivos de previsão como condições do contrato. Sem liberar probabilidade ou ranking pela vantagem retrospectiva do v3.
- Não transformar 2 safras,20 eventos,5 casos ou80% de cobertura em garantia de validade. Definir regra de evidência e procedimento completo antes de exibir força.
- Descrever leituras antes/depois e seguimento com unidade, cobertura, intervalos e reaplicações; não diagnosticar resistência nem sugerir produto.
- Manter ausência distinta de zero, exclusões contabilizadas e sensibilidade ao mecanismo de falta. Fonte/protocolo/RT continuam donos dos parâmetros agronômicos.
- Estas são propostas de consolidação, não novos requisitos publicados ou alteração da ordem vigente. RX-0 continua dependência imediata após EX42; não abrir implantação paralela.

## Correções e sugestões do Gemini não adotadas automaticamente
1. A abertura afirma que réplicas sintéticas sem independência “confirmam” subestimação e generaliza que métodos clássicos geram artefatos. O pacote não prova essas generalizações. O diagnóstico C5 não é validação de cobertura estatística.
2. Q2 confunde denominadores do Henderson–Tilton: E=1−(Ta×Cb)/(Tb×Ca). Cb=0 não torna essa expressão indefinida quando Tb×Ca≠0; pode tornar a comparação operacional inadequada, que é motivo diferente. Tb=0 ou Ca=0 torna o denominador zero. A UI não deve misturar falta, zero e inelegibilidade. A contraprova aritmética é direta: Ta=5,Cb=0,Tb=10,Ca=10 resulta E=1, não divisão por zero; isso NÃO valida exibir eficácia100%.
3. Não assumir como fato que toda reaplicação ocorre porque controle falhou. Motivo/estimando governam o tratamento; censura não informativa não pode ser presumida. Risco competitivo ou desfecho composto são alternativas a avaliar, não adoção automática.
4. Q6 propõe descartar o par inteiro e passa a tratar3–14dias como aprovado. Não adotado: faltante em uma covariável não exclui automaticamente todos os usos do registro;3–14continua hipótese. Exclusão por casos completos também exige avaliação de viés. O exemplo satélite<5dias/semchuva é parâmetro sem fonte e sai do contrato.
5. Q4 texto final promete “risco atual baseado em extrapolação” apesar de recomendar indisponibilidade. Remover promessa de capacidade não validada; usar motivo específico e próximo passo.
6. “Talhões controlados” em Q3 e “desempenho sequencial” em Q5 podem sugerir eficácia; preferir descrição literal da leitura/seqüência. Não substituir os estados de seguimento já acordados por novos baldes.
7. GLMM, erros clusterizados, PSM/DiD, Turnbull/riscos competitivos não são exigências de implementação por sugestão do modelo. Tendências paralelas não ficam “comprovadas matematicamente” por um gráfico prévio; o exemplo14dias não é critério aprovado. Escolher menor método que satisfaça contrato e testes, com fontes verificadas.
8. Permutar mantendo estrutura exige nula e esquema válidos; um resultado no embaralhado isolado não identifica automaticamente autocorrelação como causa.
9. A proposta de retirar todos os selos e trocar associação por coocorrência altera o desenho solicitado. Não tratá-la como consenso: pode-se manter o estado insuficiente no protótipo enquanto contrato/método são resolvidos, sem legitimar selo indevido nem eliminar silenciosamente o requisito.

## Próximo responsável
Claude: revisar criticamente este extrato e os pontos Q1–Q6 usando fontes recuperáveis; devolver proposta mínima do contrato RX-0 e divergências materiais, preservando EX42 e prioridade88/89. Não consultar Gemini novamente por rotina. Parâmetros, estimandos e validação prospectiva continuam pendentes onde não há evidência; nenhuma implantação liberada por este parecer.
