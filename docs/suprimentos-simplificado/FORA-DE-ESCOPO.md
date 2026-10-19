# Fora de escopo · Suprimentos simplificado v2

Cada item diz por que fica fora e onde ou quando volta. Abreviações: as da `ESPECIFICACAO.md`.

| Item | Por que fica fora | Onde ou quando volta |
|---|---|---|
| Demanda × realizado: a demanda não lê o realizado das O.S. (`cal01.js:14`); a Compra pede 145,2 L de Fungicida A que a OS-0421 já executa | é fórmula de planejamento, não de suprimentos | CONTROLE-01 item 10, **antes** de levar a Compra ao proprietário |
| Fórmula própria do Mapa (`inicio.py:335-372`) | mesma causa | CONTROLE-01 |
| Passo "Retirar no almoxarifado" na entrega parcial no app (`mobile.py:200`; AUD:191) | é regra do app de campo | CONTROLE-01 |
| "Reservar complemento" pelo almoxarife (CMD-44, PRD:2827) quando a O.S. pede mais do que a REQ reservou | não existe hoje; a v2 só torna a falta visível ("Reserva parcial · faltam X") | fatia própria depois do PCM 1c |
| SU-02 (política de estoque), transferência com trânsito (RF-SUP-009), FEFO (`cenLote` pega o lote com mais saldo, `cenario.js:42`), estorno com vínculo, Desfazer da entrega | lacunas mantidas; nenhuma é agravada | fatias próprias |
| Telas ocultas SU-01 a SU-09 | continuam ocultas; são a única cobertura de estorno e concorrência (`sutest.py`) | revisão geral do protótipo |
| Aba do almoxarife no app em cartões (MB-05, SU-07 "Ler QR → MB-05", SU-09 "Contar → MB-05") | a aba atual tem dados fixos e contraditórios; sai como recorte temporário | quando virar a mesma fila em cartões, com as funções do `est.js` |
| Leitura de QR da O.S. e da DANFE; integração com SEFAZ ou ERP | integração real é do proprietário (AGENTS §2) | autorização dele |
| Casca responsiva (menu lateral vira ☰ a ≤640 px) | muda todas as telas; opção (a) do achado D-R02 | frente própria de casca, com teste em todas as páginas |
| Congelar a ordem da grade enquanto o painel está aberto | a linha não carrega comando; não protege dano | — |
| Serviço com medição/aceite e bem/ativo (SUPv2 65.7; SUP-A02) | não há serviço nem imobilizado nos dados do protótipo; só a Situação "Conferir serviço" fica reservada | quando a 1ª compra de serviço ou ativo entrar nos dados |
| Ação em lote com seleção de IDs entre documentos (SUPv2:89) | o comando coletivo desta frente age sobre um documento (REQ, SOL) e mostra a prévia no rótulo | quando houver tarefa real de lote |
| Cotação on-line real e pregão ao vivo (SUPv2 65.8) | envio é simulado no protótipo | software real |
| Emissão por grupo de fornecedor dentro da mesma solicitação | não pedido; muda a regra da alçada | decisão de produto |
| Linha do tempo do item (`cal01().linhas` + `c.movs`) | depende do 1c e do CONTROLE-01 | painel de consulta em Confira saldos |
| Página única "Suprimentos" | a v2 mantém 2 telas com papéis distintos | — |
| Software real: login, servidor com alçada (CF-02), chave de idempotência no servidor (ENG-021/022) | o protótipo simula com Ver como e `cenMudar` com `cmd` | fatia de software real |
| KPI-SUP em painel | aqui só se preservam os marcos com horário | Controle |
