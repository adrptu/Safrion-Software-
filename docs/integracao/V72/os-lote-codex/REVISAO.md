# OS-LOTE-F1 + Y4 — candidata Codex para revisão Claude

Base de autoria: 698790bbafc8074bd1c612adf2bd58f7ae0ea85c. Contrato 6222036340/6222100368/6222201845. Extensão de autoria alocacao.py aprovada por Claude em 6223659889 após pedido 6223646782.

## Comportamento
Na coleção de O.S., seleção explícita das origens compatíveis → prévia → confirmação. Agrupar mantém IDs, versões, demanda, aprovação e liberação por origem. Programação pode ficar pendente e ser confirmada depois. A proposta substitui somente os blocos das origens selecionadas, valida o estado final, conflitos, manutenção, classes, potência e habilitação. CMD-06 reutilizado por origem, sem CMD-42 implícito; recibo parcial e intenção durável. Apontamentos e consumo continuam nas origens.
Y4: residual não negativo menor que 1e-9 ha na projeção de preparo vira zero; área negativa continua inválida.

## Executado por Codex, dados sintéticos
- Node: 74/74 (os_lote_unit.js), carregando o núcleo real gerado por Python, sem mock de CMD-06.
- Regressão existente alocacao_unit_test.py: 21/21.
- Jornada real da seed: compor 3 origens (30 ha), programar depois, aprovar 2, liberar 2/manter 1 pendente, entregar/confirmar/iniciar/apontar 15 ha; consumo 30 kg e saldo agregado 15 ha.
- AST Python dos 4 arquivos; cenario.py via CLI; geração de OS.dc.html e node --check do script gerado: sucesso.
- Logs nesta pasta. Não são provas de navegador.

## A executar por Claude antes do aceite
os_lote_test.py propõe 32 verificações de teclado/foco/rascunho/recibo, desktop 1440 e celular 390, em perfil descartável e RENDER_DIR da candidata. Ainda não executado. Codex não contornou o bloqueio de navegador existente.
Revisar criticamente domínio/UI e adaptar a menor correção ao autor. Executar também a programação pela UI, liberação parcial, quota e recuperação; verificar carga PCP, manutenção/troca de recurso, O.S./apontamentos e os consumidores afetados de alVigente. Reutilizar resultados válidos e retestar a composição com PR87 apenas onde afetado.

## Limites e decisões para revisão
- Fresh seed: OS-0590…0593, três compatíveis e uma dose diferente. Parcelas LG-DEMO-A…D são sintéticas, sem geometria, no contexto Lagoa Grande/Mamão Formosa; nenhuma recomendação agronômica. Sem migração/reset de cenário salvo.
- Cadastro CD-04 é a fonte da regra de habilitação. Adaptador local usa a mesma função tanto na data de referência do cadastro quanto na data proposta; a divergência de datas da demonstração já existente não foi escondida nem alterada globalmente.
- Sequência que cruza meia-noite é recusada nesta fatia; interface deve permitir corrigir início. Partes B, VRA e reprogramação de ocorrências futuras fora do escopo.
- Persistência é a do protótipo: testes sequenciais não provam concorrência entre abas nem banco real.
- Ainda não publicada nem pronta para homologação. Codex autor, Claude revisor/integrador. Nenhuma autoaprovação.
