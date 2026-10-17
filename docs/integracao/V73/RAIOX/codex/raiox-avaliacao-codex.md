# Raio-X do alvo — avaliação independente Codex

17/10/2026. Pedido96191be; anexo versão3 em529adf7, SHA256e7872cb02fc667330354560a6b88b82cd5485ab656b2d7546b2500d645805e5e,151382bytes. Parecer Claude não lido. Confronto com EX-42 integrado em a7f52ae e seus requisitos PRD/NAV/DS referenciados; esta avaliação não substitui revisão completa do PRD canônico nem adoção do RT. Proposta para comparação, não desenho final ou liberação de implementação.

## Resultado
Adotar o acesso contextual às fontes e a separação entre associação, comparação de manejo e previsão. Não transportar o motor demonstrativo diretamente ao produto. Reproduzi12/14 no núcleo real e identifiquei duas utilizações de dados futuros. Os números da demonstração não comprovam inferência causal, intervalos calibrados ou previsão operacional.

## Evidência executada
Node24.19.0, núcleo do script até marcador estado, sem DOM/navegador. Gabarito usa a função original gabaritoRows e mesma definição shown. Primeira extração falhou por IIFE incompleto; harness fechado, algoritmo preservado.

| Alvo | Efeitos encontrados | Falsos fortes/moderados | Brier modelo | Persistência | Eventos positivos/teste |
|---|---:|---:|---:|---:|---:|
| Ácaro | 4/5 | 0 | 0,05882 | 0,16129 | 4/31 |
| Mosca | 3/4 | 0 | 0,04431 | 0,13636 | 5/44 |
| Antracnose | 3/3 | 0 | 0,00302 | 0,02041 | 1/49 |
| Cochonilha | 2/2 | 0 | 0,04413 | 0,21622 | 9/37 |

O gabarito conta direção encontrada inclusive por variável associada ao grupo; não mede cobertura da magnitude nem comprova100%dos efeitos fortes. Uma semente e um positivo de antracnose não validam calibração±10p.p. ou população externa.

## Achados para corrigir no desenho
1. **Corte temporal HT (reproduzido, S2 se adotado no produto).** rxHT, linhas620–634: nearestObs±3 admite controle depois deD. D10, tratadoD1=10/D10=5 e dois controlesD1=10/D12=10 produzem47,619% com dois controles futuros. Aceite: nenhuma observação posterior aD influencia resultado; sem comparação elegível, mostrar motivo e fontes, sem percentual.
2. **Validação prospectiva (reproduzido na característica, S2 se adotado).** rxRisk usa fval no teste histórico; winVals/climaAt lê clima realizado atéd2. Na origemD30→D37, alterar somente Tmáx realizadoD35 em+70 muda a característica em+10°C. Não é previsão arquivada disponível emD30. Aceite: separar instante do evento, disponibilidade e origem da previsão; backtest usa somente dados disponíveis na origem. Revalidar gate após correção; vitória atual não libera probabilidades7/14dias.
3. **Comparabilidade dos controles (fonte).** rxHT relaxa filtros até todos os candidatos quando faltam dois pareados. Isso contraria “sem comparação válida”. Não transformar ausência de par em comparabilidade; declarar estágio, janela, nível e intervenções elegíveis, permitir resultado indisponível. Epsilon muda HT tradicional e exige rótulo/método explícito; não converter denominador inválido em eficácia por suavização silenciosa.
4. **SeguimentoNC (conflito com EX-42§8).** rxHT censura emD e backDay vira tempo exato; ausência de observação atéD não prova permanência abaixoNC. Exigir pós abaixoNC, retorno em intervalo e censura na última observação elegível. Primeiro pós acimaNC não é retorno demonstrado. KM convencional não deve apagar censura por intervalo/seguimento incompleto; método exige decisão específica.
5. **Seleção e evidência (fonte, decisão metodológica pendente).** rxFit escolhe janela/limiar/representante no conjunto; rxBoot mantém matriz selecionada fixa. Corrigir multiplicidade das janelas não demonstra correção da busca inteira. Proponho validar procedimento completo em dados separados e simulações repetidas, incluindo seleção dentro do treino; comparar alternativa simples antes de LightGBM/SHAP. Não classificar Forte só pela reprodução da mesma safra. É crítica de desenho, ainda sem estimativa executada da inflação de falsos positivos.
6. **Época e confundimento.** Não excluir época automaticamente apenas porque desaparece um efeito desejado. Com uma safra, registrar confundimento/não identificabilidade e análise de sensibilidade. Pareamento observacional e selo doRT não provam causalidade ou resistência. “Possível perda de resposta; investigar cobertura, pressão e sequência” em lugar de diagnóstico/recomendação automática.

## Fluxo e cortes
Mapa/monitoramento no recorte→lista de associações ou comparações→achado→casos/fontes EX-42. Cabeçalho informa alvo, cultura/safra, unidade/protocolo, data de corte, cobertura e cálculo. Estados: calculando, disponível, insuficiente, desatualizado, erro; cada um oferece próximo passo pertinente e retorno preservado. Sem menu novo. A primeira camada diz “associado a aumento/redução”, não “faz subir/descer”. Separar efeito estimado de manejo e referência agronômica não medida. Nenhum ranking recomenda produto/dose.

Marca “Confere/Não confere/Investigar” é avaliação com autor/data. Promoção a protocolo é outra operação explícita versionada com permissão e confirmação; não dispara pelo clique da marca. Criar vistoria produz rascunho com contexto; não cria O.S. ou aprovação. Tabela equivalente, unidades, fonte/intervalo e teclado são requisitos; testes visuais1440/390 e usuários ainda não executados.

## Proposta de sequência, usando fatias1–5 do pedido
1. Fatia1: contratos de observação/protocolo/tempo disponível, dados sintéticos, exclusões, proveniência e gabarito com sementes independentes. Dependência imediata do EX-42, sem reimplementar seu motor factual.
2. Fatia2: comparação de aplicações somente com elegibilidade/controle demonstrados e seguimento correto; antes disso, variação observada do EX-42 permanece operável.
3. Fatia3: associações e subdetalhe com evidência, sem causalidade. Comparar métodos simples com validação da seleção completa.
4. Fatia4: risco7dias após backtest prospectivo/calibração/baseline definidos;14dias tem aceite próprio e não herda vitória7dias.
5. Fatia5: avaliaçãoRT e promoção versionada, preservando aprovação individual.
Autoria/arquivos serão contratados após confronto com Claude e decisão material Gemini, no registro atual. Não abrir implementação concorrente nem atrasar publicaçãoq30.

## Aceites a tornar verificáveis
- Corrigir “3–5 usuários e ao menos4 compreendem”: fixar número/proporção antes de medir.
- Separar zero falso forte/moderado numa fixture de taxa≤5% numa série de simulações; denominador, sementes e regra definidos antes do ajuste.
- Casos adversariais: controle futuro, revisão retroativa, previsão publicada depois da origem, ausência≠zero, unidade/protocolo mudados, múltiplas intervenções, sem pareamento, denominadorzero, intervalo sem visita, censura e evento nunca abaixoNC.
- Validar magnitude/intervalo, estabilidade, calibração e baseline por horizonte. Com dados insuficientes, manter fatos e referência rotulada, não número convincente.
- Job real posterior: versão de entradas/modelo/parametrização e escopo, idempotência, publicação atômica de resultado, falha/recuperação e acesso revalidado. Protótipo não comprova servidor/banco/job.

## Aplicado, fora e cortado
Aplicado: rastreabilidade/limite temporal EX-42, contexto NAV/DS, reprodução do motor, duas contraprovas, incerteza e autoria delimitada.
Fora: aprovaçãoRT, adoção de janela/limiar, calibração real, usuários, browser, custo de job, decisão sobre habilitação do motor estatístico e implantação. Não presumir resposta às decisões8do pedido.
Cortado: causalidade no rótulo, recomendação automática, fallback silencioso de controles e conclusão funcional baseada em12/14.

Próximo: Claude confronta sua avaliação independente; Gemini real resolve pacote mínimo sobre evidência pós-seleção, eficácia/seguimento e previsão antes do desenho final. Nenhuma fonte real/segredo deve integrar esse pacote. Provas anexas são sintéticas. q30/PR81/90/91 seguem prioridade.
