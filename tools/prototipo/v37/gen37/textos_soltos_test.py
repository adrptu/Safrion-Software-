# -*- coding: utf-8 -*-
"""TEXTO-2 · segunda passada do pedido do proprietário (13/10/2026): "reduza ou elimine todas essas descrições abaixo dos titulos e os
demais soltos pela tela.... em todas as telas do sistema. somos minimalistas e essencialistas".

Abre cada tela alterada e confere, como a pessoa veria:
  T  a frase tirada não está no texto visível da tela (document.body.innerText);
  D  a frase levada para a dica está no data-dica do ⓘ "Regras desta tela" (header button.g2-info);
  F  o dado, a trava e o rótulo de demonstração que ficam à vista continuam à vista (nada de dado sumiu junto);
  E  sem erro de JS em nenhuma tela aberta.
Contraprova: com RENDER_DIR apontando para um render de antes da TEXTO-2 o teste reprova (as frases ainda estão à vista).
Rode depois de build.py + montar_render.py: env CHROME_BIN=... SAFRION_DADOS=sintetico python3 -B textos_soltos_test.py"""
import os, sys, json, time, unicodedata
G = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, G)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')

# (tela, frase tirada (como estava à vista), trecho que não pode mais aparecer, trecho que tem de estar na dica ⓘ ou None se apagada, origem na base 48f570b)
TIRADAS = [
    ('MB-01', 'Siga a ordem da janela; o botão diz o próximo passo.', 'siga a ordem da janela', 'segue a ordem da janela', 'areas/mobile.py:364'),
    ('MB-01', 'Escolha o trabalho para abrir o formulário do seu domínio.', 'escolha o trabalho para abrir o formulário', None, 'areas/mobile.py:370'),
    ('MB-02', 'suas (Marcos) e da equipe · mesma ordem do escritório', 'suas (marcos) e da equipe', 'mesma ordem do escritório', 'areas/mobile.py:430'),
    ('MB-02', 'Abra a ordem para ver instrução, insumos e apontamentos.', 'abra a ordem para ver instrução', None, 'areas/mobile.py:402'),
    ('MB-02', 'Consulte; quem executa é o responsável indicado.', 'consulte; quem executa', 'quem executa é o responsável indicado', 'areas/mobile.py:404'),
    ('MB-02', 'Água simplificada: abre em Irrigação, sem materiais e sem requisição.', 'água simplificada: abre em irrigação', 'abre em irrigação, sem materiais e sem requisição', 'areas/mobile.py:423'),
    ('MB-02', 'Fechar o turno não encerra a ordem. Encerrar é no escritório, com apontamentos enviados e nada em custódia.', 'encerrar é no escritório', 'encerrar é no escritório, com apontamentos enviados e nada em custódia', 'areas/mobile.py:425'),
    ('MB-02det', 'Siga dose, janela e preparo da versão autorizada.', 'siga dose, janela e preparo', 'siga dose, janela e preparo da versão autorizada', 'areas/mobile.py:440'),
    ('MB-02det', 'Use só o material autorizado; a sobra volta pela devolução.', 'use só o material autorizado', 'use só o material autorizado; a sobra volta pela devolução', 'areas/mobile.py:447'),
    ('MB-02det', 'Confira o que já foi enviado e o que está só no aparelho.', 'confira o que já foi enviado', None, 'areas/mobile.py:453'),
    ('MB-03', 'iniciar, pausar e fechar · hectares, horas e consumo', 'iniciar, pausar e fechar · hectares', None, 'areas/mobile.py:599'),
    ('MB-03', 'Inicie o turno na ordem em que vai trabalhar.', 'inicie o turno na ordem', 'inicie o turno na ordem em que vai trabalhar', 'areas/mobile.py:527'),
    ('MB-03x-recibo', 'fila do aparelho · cada registro entra uma vez', 'fila do aparelho · cada registro', 'cada registro entra uma vez', 'areas/mobile.py:632'),
    ('MB-03x-recibo', 'Reenvios devolvem o mesmo recibo; a conferência decide o realizado.', 'reenvios devolvem o mesmo recibo', 'reenvios devolvem o mesmo recibo; a conferência decide o realizado', 'areas/mobile.py:610'),
    ('MB-03x-recibo', 'Conflito com outro aparelho abre reconciliação sem somar em dobro. Pacote revogado ou vencido vira relato para decisão, sem aprovação retroativa.', 'conflito com outro aparelho', 'conflito com outro aparelho abre reconciliação sem somar em dobro', 'areas/mobile.py:621'),
    ('MB-04', 'tipo e texto · foto e voz simuladas · funciona sem sinal', 'tipo e texto · foto e voz simuladas', 'funciona sem sinal', 'areas/mobile.py:717'),
    ('MB-05', 'retiradas do operador e tarefas do almoxarife · por lote e embalagem', 'retiradas do operador e tarefas do almoxarife', None, 'areas/mobile.py:796'),
    ('MB-05', 'Use na ordem; a sobra volta pela devolução ao Rui.', 'use na ordem; a sobra volta', 'use na ordem; a sobra volta pela devolução', 'areas/mobile.py:788'),
    ('MB-05', 'Leve a O.S.; Rui entrega por lote e embalagem.', 'leve a o.s.;', 'entrega por lote e embalagem', 'areas/mobile.py:789'),
    ('MB-05', 'Confirmar o recebimento põe o material sob sua custódia; o apontamento do turno baixa o consumo.', 'põe o material sob sua custódia', 'confirmar o recebimento põe o material sob sua custódia', 'areas/mobile.py:744'),
    ('MB-05det', ' · conferência física contra QR (fim do subtítulo)', 'conferência física contra qr', 'contra o qr', 'areas/mobile.py:821'),
    ('MB-05det', 'Confira as sacas contra o QR antes de confirmar.', 'confira as sacas contra o qr', 'confira as sacas contra o qr antes de confirmar', 'areas/mobile.py:811'),
    ('MB-05det', 'Ao confirmar: custódia zera, a conta 100 = 70 + 30 fecha e a OS-0417 segue para o fechamento da conferência · sobras íntegras entram no lote M26-05 (sobras) até inspeção.', 'ao confirmar: custódia zera', 'ao confirmar: custódia zera', 'areas/mobile.py:812'),
    ('MB-05det', 'Material preparado não retorna como produto original disponível; só sobra íntegra volta ao estoque.', 'material preparado não retorna', 'material preparado não retorna como produto original disponível', 'areas/mobile.py:814'),
    ('MB-07', 'previsão de colheita · conta por planta e estádio', 'previsão de colheita · conta por planta', 'por planta e estádio', 'areas/mobile.py:945'),
    ('MB-07', 'Toque no talhão de fruta em produção que vai contar.', 'toque no talhão de fruta', 'toque no talhão de fruta em produção que vai contar', 'areas/mobile.py:906'),
    ('MB-08', 'OS-0419 · Pivô 2 · água · sem emissão manual (subtítulo)', 'sem emissão manual', 'sem emissão manual', 'areas/mobile.py:975'),
    ('MB-08', 'Água sem produto: sem materiais, sem requisição, sem custódia e sem devolução.', 'sem requisição, sem custódia e sem devolução', 'sem requisição, sem custódia e sem devolução', 'areas/mobile.py:956'),
    ('MB-08', 'Confira a lâmina antes de iniciar.', 'confira a lâmina antes de iniciar', 'confira a lâmina antes de iniciar', 'areas/mobile.py:957'),
    ('MB-08', 'Acompanhe a volta e confirme o término no fim.', 'acompanhe a volta e confirme', 'confirme o término no fim', 'areas/mobile.py:963'),
    ('MB-08', 'Registre pausas e avanço sem encerrar a ordem.', 'registre pausas e avanço sem encerrar a ordem', 'registre pausas e avanço sem encerrar a ordem', 'areas/mobile.py:964'),
    ('MB-08', 'passam do máximo de 12,0 mm por passada: o sistema divide em 2 passadas de 6,75 mm. Sem aprovação; libera quando a janela for definida.', 'o sistema divide em', 'dividida pelo sistema em passadas iguais, sem aprovação', 'areas/mobile.py:971'),
    ('MB-08', 'Só a fertirrigação (OS-0418) é liberada pelo agrônomo, com materiais e requisição próprios.', 'só a fertirrigação (os-0418) é liberada', 'só a fertirrigação (os-0418) é liberada pelo agrônomo', 'areas/mobile.py:972'),
    ('MB-08', 'Área/volume insuficientes? Registra-se o tempo e a estimativa fica pendente — a lâmina não é afirmada como medida. Não existe “Encerrar e apontar”.', 'área/volume insuficientes', 'a lâmina não é afirmada como medida', 'areas/mobile.py:974'),
    ('MB-08x-recibo', 'mapa, lista, quadro e app leem o mesmo evento', 'mapa, lista, quadro e app leem', 'mapa, lista, quadro e app leem o mesmo evento', 'areas/mobile.py:995'),
    ('MB-08x-recibo', 'Fatos consistentes → conferência e encerramento automáticos, com recibos separados.', 'fatos consistentes →', 'encerramento automáticos, com recibos separados', 'areas/mobile.py:983'),
    ('MB-08x-recibo', 'Confira os recibos e a área realmente atendida.', 'confira os recibos e a área', None, 'areas/mobile.py:991'),
    ('MB-08x-recibo', 'Balanço hídrico atualizado uma vez por aplicação', 'balanço hídrico atualizado uma vez', 'o balanço hídrico é atualizado uma vez por aplicação', 'areas/mobile.py:990'),
    ('MB-08x-recibo', 'Horímetro divergente da lâmina calculada → a ordem fica Em conferência com o motivo exibido; corrigir a calibração do pivô substitui a fórmula anterior.', 'horímetro divergente da lâmina calculada →', 'corrigir a calibração do pivô substitui a fórmula anterior', 'areas/mobile.py:993'),
    ('MB-09', 'condição, leitura e abastecimento · funciona sem sinal', 'condição, leitura e abastecimento · funciona', 'condição, leitura e abastecimento; funciona sem sinal', 'areas/mobile.py:1084'),
    ('MB-09', 'Herdada do seu turno; toque noutra ou busque pelo nome.', 'herdada do seu turno;', 'toque noutra ou busque pelo nome', 'areas/mobile.py:1005'),
    ('MB-09', ' · toque noutra para trocar (fim de "Herdada do turno da OS-0421")', 'toque noutra para trocar', 'toque noutra ou busque pelo nome', 'areas/mobile.py:1049'),
    ('MB-09', 'Tanque, volume e leitura; a foto do tíquete é a evidência.', 'a foto do tíquete é a evidência', 'tanque, volume e leitura; a foto do tíquete é a evidência', 'areas/mobile.py:1017'),
    ('MB-09det', 'Nunca voltam ao estoque livre: destino e responsável.', 'nunca voltam ao estoque livre', 'nunca voltam ao estoque livre: destino e responsável', 'areas/mobile.py:1130'),
    ('MB-10', 'colheita: área e cargas do talhão · motorista: viagem', 'colheita: área e cargas do talhão', None, 'areas/mobile.py:1314'),
    ('MB-10', 'Aponte a área do turno e registre cada carga que sai do talhão; a balança pesa e recebe.', 'aponte a área do turno e registre', 'aponte a área do turno e registre cada carga que sai do talhão', 'areas/mobile.py:1245'),
    ('MB-10', 'Área não gera produção: a produção do talhão nasce só da carga pesada e recebida.', 'área não gera produção', 'área não gera produção: a produção do talhão nasce só da carga pesada e recebida', 'areas/mobile.py:1257'),
    ('CA-01', '(o agrônomo libera) no indicador A LIBERAR', '(o agrônomo libera)', 'o agrônomo libera a ordem', 'areas/campo.py:208'),
    ('CA-01det', 'término físico do escopo (ou dispensa autorizada do saldo) entra automaticamente em Em conferência — nenhum botão pula etapa', 'término físico do escopo (ou dispensa', '(ou dispensa autorizada do saldo) entra automaticamente em em conferência', 'areas/campo.py:287'),
    ('CA-01det', 'O agrônomo ajusta e libera a v3 só para o saldo; as fichas do saldo passam à v3.', 'o agrônomo ajusta e libera a v3', 'o agrônomo ajusta e libera a v3 só para o saldo', 'areas/campo.py:296'),
    ('CA-01x-os0420', 'impedimento é selo: a ordem segue Em execução e nenhum botão pula etapa', 'impedimento é selo', 'impedimento é selo: a ordem segue em execução e nenhum botão pula etapa', 'areas/campo.py:346'),
    ('CA-02', 'Se a liberação não estiver mais vigente, o saldo reaberto recebe o selo Pausada até renovar as condições. Correção só documental permanece Em conferência — não reabre período contábil nem reescreve fatos.', 'o saldo reaberto recebe o selo', 'o saldo reaberto recebe o selo pausada até renovar as condições', 'areas/campo.py:425'),
    ('CA-02', 'Concluir execução não encerra a ordem com custódia, divergência ou conferência pendente.', 'concluir execução não encerra a ordem', 'concluir execução não encerra a ordem com custódia, divergência ou conferência pendente', 'areas/campo.py:428'),
    ('CA-04', 'Declarar o retorno não aumenta o estoque utilizável: só a quantidade medida e recebida entra no local e na condição registrados. Sem ajuste automático pela diferença.', 'declarar o retorno não aumenta', 'declarar o retorno não aumenta o estoque utilizável', 'areas/campo.py:564'),
    ('CO-02', 'Hectares concluídos não geram quilogramas de estoque, e pesagens não duplicam a produção da mesma carga. Ex.: avanço de 30 ha numa ordem de 100 ha …', 'hectares concluídos não geram quilogramas', 'hectares concluídos não geram quilogramas de estoque', 'areas/colheita.py:247'),
    ('CO-02det', 'Término físico entra automaticamente em Em conferência; encerrar exige cargas e apontamentos conciliados.', 'encerrar exige cargas e apontamentos conciliados', 'encerrar exige cargas e apontamentos conciliados', 'areas/colheita.py:292'),
    ('CO-04', 'A entrada NÃO equivale a liberação comercial: produto em processo continua identificado … nunca soma com ela.', 'a entrada não equivale a liberação comercial', 'a entrada não equivale a liberação comercial: produto em processo continua identificado', 'areas/colheita.py:383'),
    ('CO-05', '— fechar processo não libera lote … decisão posterior de qualidade não reabre a ordem encerrada', 'fechar processo não libera lote', 'decisão posterior de qualidade não reabre a ordem encerrada', 'areas/colheita.py:419'),
    ('CO-05det', 'Concluir execução leva a Em conferência; fechar processo exige balanço conferido.', 'concluir execução leva a em conferência', 'concluir execução leva a em conferência; fechar processo exige balanço conferido', 'areas/colheita.py:482'),
    ('CO-06', 'Lotes de campo vêm dos apontamentos das O.S. de colheita (parcela + data). … LMR Brasil: ANVISA … Regras de exportação não carregadas …', 'lotes de campo vêm dos apontamentos', 'lotes de campo vêm dos apontamentos das o.s. de colheita', 'areas/colheita.py:669'),
    ('CO-06', 'Bloqueio invalida a elegibilidade das reservas afetadas e avisa o Comercial automaticamente — tentativas de reservar ou expedir o lote falham com motivo …', 'invalida a elegibilidade das reservas', 'invalida a elegibilidade das reservas afetadas', 'areas/colheita.py:543'),
    ('CO-07', 'o contrato barter que originou a reserva não é subtraído de novo. A oferta futura … não soma como estoque; …', 'o contrato barter que originou a reserva', 'o contrato barter que originou a reserva não é subtraído de novo', 'areas/colheita.py:635'),
    ('SU-01', 'as 10 t em quarentena não entram e ficam como coberto se o laudo aprovar, somadas uma única vez. Clique na linha para ver a memória de cálculo.', 'ficam como coberto se o laudo aprovar', 'ficam como coberto se o laudo aprovar, somadas uma única vez', 'areas/suprimentos.py:295'),
    ('SU-02', 'Classe ABC financeira não substitui criticidade: Diesel é B em valor e Alta em criticidade. Limites do depósito e validade …', 'classe abc financeira não substitui', 'classe abc financeira não substitui criticidade', 'areas/suprimentos.py:343'),
    ('SU-03', 'Físico ≠ utilizável ≠ disponível. Custódia em campo fica fora do físico do depósito e não soma duas vezes; …', 'físico ≠ utilizável ≠ disponível', 'físico ≠ utilizável ≠ disponível', 'areas/suprimentos.py:416'),
    ('SU-04', 'O fornecedor responde pelo portal externo com convite próprio, nunca por esta lista. A SOL-2026-07 veio de Planejar safra …', 'o fornecedor responde pelo portal externo', 'o fornecedor responde pelo portal externo com convite próprio', 'areas/suprimentos.py:584'),
    ('SU-05', 'O recebido já está dentro das liberações acumuladas e não é subtraído de novo do saldo contratual.', 'o recebido já está dentro das liberações', 'o recebido já está dentro das liberações acumuladas', 'areas/suprimentos.py:673'),
    ('SU-05', 'Recebimento parcial mantém o saldo do pedido aberto; o aceite físico acontece em Recebimentos.', 'recebimento parcial mantém o saldo', 'recebimento parcial mantém o saldo do pedido aberto', 'areas/suprimentos.py:676'),
    ('SU-06', 'Aceite físico não aprova o título: o título segue para Contas a pagar à parte. O retido em quarentena …', 'aceite físico não aprova o título', 'aceite físico não aprova o título', 'areas/suprimentos.py:828'),
    ('SU-07', 'Material entregue sai do disponível e passa à custódia da ordem; o consumo apontado no campo não repete a saída. …', 'material entregue sai do disponível', 'material entregue sai do disponível e passa à custódia da ordem', 'areas/suprimentos.py:932'),
    ('SU-07det', 'É o mesmo balanço que a conferência da ordem usa. Declarar a devolução não aumenta o utilizável do depósito; …', 'é o mesmo balanço que a conferência', 'é o mesmo balanço que a conferência da ordem usa', 'areas/suprimentos.py:995'),
    ('SU-08', 'Correção não apaga a operação original: o estorno cria movimento novo com vínculo. …', 'correção não apaga a operação original', 'correção não apaga a operação original', 'areas/suprimentos.py:1083'),
    ('SU-09', 'O contador não vê o saldo do sistema e os movimentos do escopo ficam suspensos entre o corte e o encerramento: …', 'o contador não vê o saldo do sistema', 'o contador não vê o saldo do sistema', 'areas/suprimentos.py:1162'),
    ('PL-02', '“20 dias antes do plantio · DAP −20 · previsto para 25/09” — o produtor não digita sinal negativo. …', 'o produtor não digita sinal negativo', 'o produtor não digita sinal negativo', 'areas/planejamento.py:256'),
    ('PL-03', 'não ofertado como livre (cartão do Trator T1)', 'não ofertado como livre', 'máquina bloqueada não é ofertada como livre', 'areas/planejamento.py:318'),
    ('PL-03', 'trator livre + implemento reservado ≠ conjunto livre', 'trator livre + implemento reservado', 'trator livre + implemento reservado ≠ conjunto livre', 'areas/planejamento.py:320'),
    ('PL-03', 'não fica verde por falta de notícia', 'não fica verde por falta de notícia', 'não fica verde por falta de notícia', 'areas/planejamento.py:321'),
    ('PL-03', 'Contadores são recortes que se sobrepõem — não somam o total da frota. … fonte: PCM + eventos da operação.', 'contadores são recortes', 'contadores são recortes que se sobrepõem', 'areas/planejamento.py:373'),
    ('PL-05', 'Resolver compra ou manutenção revalida prontidão; não inicia máquina nem muda a agenda automaticamente. …', 'resolver compra ou manutenção revalida', 'resolver compra ou manutenção revalida prontidão', 'areas/planejamento.py:502'),
    ('PL-05det', 'A parada do Trator T1 reduz a capacidade da janela uma única vez (já refletida em Capacidade e recursos); …', 'reduz a capacidade da janela', 'a parada do trator t1 reduz a capacidade da janela uma única vez', 'areas/planejamento.py:551'),
    ('PL-06', 'Parcelas não duplicam hectares de cobrança (312 ha); operações e materiais seguem a parcela correta.', 'parcelas não duplicam hectares', 'parcelas não duplicam hectares de cobrança', 'areas/planejamento.py:567'),
    ('VE-01', 'Saldo final é o máximo factível sob capacidade e prazo — folga de outra classe ou dia não cobre esta janela. … condição prevista, não garantia.', 'saldo final é o máximo factível', 'folga de outra classe ou dia não cobre esta janela', 'areas/comercial.py:101'),
    ('VE-02', 'vira premissa só ao usar na gestão. Contrato futuro não é inventado: só instrumentos existentes nas fontes acima.', 'contrato futuro não é inventado', 'contrato futuro não é inventado', 'areas/comercial.py:221'),
    ('VE-03', 'Aceite registrado pelas duas partes, por versão. Confirmação automática só sob política prévia explícita do produtor. …', 'confirmação automática só sob política', 'confirmação automática só sob política prévia explícita do produtor', 'areas/comercial.py:286'),
    ('VE-06', 'O ajuste financeiro fica vinculado ao caso — crédito não é emitido pelo retorno em si. Recolhimento, se decidido, …', 'crédito não é emitido pelo retorno', 'crédito não é emitido pelo retorno em si', 'areas/comercial.py:544'),
    ('LO-02', 'Política v4: elegibilidade (presença, prontidão, doca livre, documentos) › janela em risco › … Tolerância de chegada: 30 min.', 'política v4: elegibilidade', 'elegibilidade (presença, prontidão, doca livre, documentos)', 'areas/logistica.py:360'),
    ('LO-02', 'A preparar → Em separação → Conferência → … Qualidade, financeiro e documentos são dimensões separadas.', 'documentos são dimensões separadas', 'qualidade, financeiro e documentos são dimensões separadas', 'areas/logistica.py:364'),
    ('LO-02det', 'o rateio da instalação não se aplica a esta carga', 'o rateio da instalação não se aplica', 'o rateio da instalação não se aplica', 'areas/logistica.py:438'),
    ('LO-04', 'Sugestão não despacha transportador.', 'sugestão não despacha transportador', 'sugestão de rota não despacha transportador', 'areas/logistica.py:573'),
    ('GE-02', 'Autorizar versão: só a Direção, pela caixa de Aprovações.', 'autorizar versão: só a direção', 'autorizar versão: só a direção, pela caixa de aprovações', 'areas/gestao.py:210'),
    ('GE-02det', 'A matemática explica o desvio, mas não prova desperdício: pode ser ajuste técnico autorizado, condição operacional ou erro de registro a investigar.', 'mas não prova desperdício', 'a matemática explica o desvio, mas não prova desperdício', 'areas/gestao.py:239'),
    ('GE-04', 'Fonte oficial: ERP designado — aqui se propõe, aprova e concilia; … nunca conta duas vezes … não finge recebimento de venda futura.', 'fonte oficial: erp designado', 'fonte oficial: erp designado', 'areas/gestao.py:380'),
    ('GE-06det', 'Fórmula: custo total da operação ÷ ha efetivamente tratados (apontados)', 'custo total da operação ÷ ha', 'custo total da operação ÷ ha efetivamente tratados', 'areas/gestao.py:500'),
    ('GE-06det', 'Fonte: lançamentos de custo documento a documento + apontamentos da O.S.', 'lançamentos de custo documento a documento', 'lançamentos de custo documento a documento', 'areas/gestao.py:502'),
    ('GE-08', '— o mesmo saco nunca garante dois contratos.', 'o mesmo saco nunca garante', 'o mesmo saco nunca garante dois contratos', 'areas/gestao.py:631'),
    ('CF-01', 'Origem: Cadastros › Pessoas e equipes (nome, função, habilidade e CREA). Aqui não se cadastra pessoa. Papel é permissão de decidir; …', 'aqui não se cadastra pessoa', 'aqui não se cadastra pessoa', 'areas/configuracoes.py:221'),
    ('CF-01', 'Os comandos da O.S., do Estoque e do app leem esta tabela. Mudança vale para o próximo comando e nunca reescreve registro antigo.', 'leem esta tabela', 'nunca reescreve registro antigo', 'areas/configuracoes.py:224'),
    ('CF-03', 'Sincronizar envia ao ERP cada movimento uma vez por conteúdo: repetir não reenvia; … O app de campo envia pelo próprio aparelho quando há sinal.', 'sincronizar envia ao erp cada movimento', 'sincronizar envia ao erp cada movimento uma vez por conteúdo', 'areas/configuracoes.py:326'),
    ('CF-05', 'Origem: Cadastros › Fazendas, áreas e talhões · conta a área cultivável dos talhões ativos de fazendas ativas; safra, parcela e operação não entram.', 'conta a área cultivável dos talhões ativos', 'conta a área cultivável dos talhões ativos de fazendas ativas', 'areas/assinatura.py:249'),
    ('CF-05', '(Configurações › Usuários e alçadas) · usuários sem limite · não entram na cobrança', '(configurações › usuários e alçadas)', 'pessoas com acesso vêm de configurações › usuários e alçadas', 'areas/assinatura.py:157'),
    ('CF-05', 'Usuários sem limite e fora da cobrança. (nota dos planos)', 'usuários sem limite e fora da cobrança.', 'usuários sem limite e fora da cobrança', 'areas/assinatura.py:253'),
    ('CF-05', 'só demonstração · avança a data da cobrança, não a dos outros módulos', 'avança a data da cobrança', 'a data simulada avança só a cobrança, não os outros módulos', 'areas/assinatura.py:243'),
    ('CF-05', 'O período fecha no último dia do mês e a fatura vence no dia 1 (exemplo, a decidir pelo proprietário).', 'o período fecha no último dia do mês', 'o período fecha no último dia do mês e a fatura vence no dia 1 (exemplo, a decidir pelo proprietário)', 'areas/assinatura.py:244'),
    ('BO-01', 'Mínimo: cobra-se o maior entre o mínimo e preço × área (não se soma). Mudança: vale do dia 1 do próximo ciclo e nunca retroage. Base (DEC-01): …', 'cobra-se o maior entre o mínimo', 'cobra-se o maior entre o mínimo e preço × área', 'areas/plataforma.py:171'),
    ('BO-02', 'a vencer, vencidas, pendentes ou em contestação', 'a vencer, vencidas, pendentes', 'faturas abertas: a vencer, vencidas, pendentes ou em contestação', 'areas/plataforma.py:51'),
    ('BO-02', 'cobrada = mín(medida; contratada)', 'mín(medida; contratada)', 'área cobrada = mín(medida; contratada)', 'areas/plataforma.py:52'),
    ('BO-02', 'Isolamento: a plataforma vê área e cobrança por organização (e por fazenda na consulta contratual), nunca cultura, safra, operação ou insumo.', 'isolamento: a plataforma vê', 'isolamento: a plataforma vê área e cobrança por organização', 'areas/plataforma.py:122'),
    ('PT-02', 'Cada versão submetida fica preservada — revisar antes do prazo cria nova versão; motivo de não seleção é agregado.', 'revisar antes do prazo cria nova versão', 'revisar antes do prazo cria nova versão', 'areas/parceiros.py:175'),
    ('PT-05det', '— recusa no recebimento abre divergência, não devolve ao estoque apto.', 'abre divergência, não devolve', 'recusa no recebimento abre divergência', 'areas/parceiros.py:398'),
    ('ON-01det', 'Estoque, análise ou plantio nunca são completados com dados inventados. Área importada maior que a declarada (480 ha) abre revisão …', 'são completados com dados inventados', 'nunca são completados com dados inventados', 'areas/onboarding_backoffice.py:181'),
    ('IC', 'esperando o mês certo, antes da necessidade (repetia o título do indicador)', 'antes da necessidade', None, 'areas/inteligencia.py:228'),
    ('IC', 'comprando pela melhor cotação (repetia o título do indicador)', 'comprando pela melhor cotação', None, 'areas/inteligencia.py:233'),
    ('MA', 'das OMs encerradas no sistema (indicador de custo)', 'das oms encerradas no sistema', None, 'areas/maquinas.py:320'),
]

# (tela, o que fica à vista: dado, trava ou rótulo de demonstração/exemplo; nada disso pode sumir junto com a explicação)
FICAM = [
    ('MB-02', 'Impedimento: OM-0233 · Trator T1 bloqueado'), ('MB-02', 'Relato fora da autorização atual · aguarda decisão'),
    ('MB-05det', 'REQ-031 · sobras da OS-0417'), ('MB-05det', 'Responsável pela custódia: Paula'),
    ('MB-08', 'OS-0422 · 13,5 mm em 2 passadas de 6,75 mm'), ('MB-08', 'Origem: balanço de 23/09 · déficit 11,2 mm'),
    ('MB-08x-recibo', 'Balanço hídrico: 10,6 mm creditados nos 80 ha do pivô'), ('MB-08x-recibo', 'Conferência: 10,6 mm medidos'),
    ('MB-09', 'Herdada do turno da OS-0421 (alocação de hoje)'), ('MB-09', 'a foto é simulada neste protótipo'),
    ('MB-09det', 'você vê a ordem, sem alterar'), ('MB-04', 'a foto e a voz são simuladas neste protótipo'),
    ('CA-01', '3 com produto · 2 só água'), ('CA-01det', 'Recomendação de origem: fungicida 1ª aplicação · protocolo do plano técnico · v2 aprovada'),
    ('CA-04', 'Balanço da REQ-031: 100 sc entregues − 70 consumidos − 20 recebidos = 10 sc com Paula'),
    ('CO-05', 'segue Bloqueado pela inspeção INSP-88'), ('CO-06', 'Demonstração · pós-colheita, laudos e destinos sintéticos'),
    ('CO-07', 'Soja: físico apto 38.420 sc − reserva 3.875 sc = disponível 34.545 sc'),
    ('SU-01', 'KCl 60%: falta firme 140 − 50 − 40 = 50 t'), ('SU-02', 'Propostas e exceções aguardando: Diesel S10 v5'),
    ('PL-03', 'elegível só após confirmação do PCP'), ('PL-03', 'Última atualização 07:42'), ('PL-06', 'Proposta · não divide a área vigente'),
    ('VE-01', 'Atualizado hoje 06:30'), ('VE-02', 'Câmbio da simulação: R$ 5,32/US$ (PTAX D-1)'), ('VE-06', 'o lote L26-118'),
    ('LO-02det', 'Frete: retirada pelo cliente'), ('LO-04', 'Mesma base: 9,6 t · 512 km · refrigerado'),
    ('GE-02det', 'desvio contra essa base = R$ 1.008'), ('GE-04', 'título único de R$ 233.000'), ('GE-06det', 'R$/ha · 120 ha·operação'),
    ('GE-08', 'comprometida'), ('CF-03', 'nenhuma credencial existe nesta demonstração'),
    ('CF-05', 'Pessoas com acesso: 14 · fora da cobrança'), ('CF-05', 'exemplo · a decidir pelo proprietário'), ('CF-05', 'Data simulada da cobrança'),
    ('BO-01', 'PRECO-01: R$ 2,00/ha·mês = R$ 24,00/ha·ano'), ('BO-01', 'Todos os valores são exemplo, a decidir pelo proprietário'),
    ('BO-02', 'medida 2.958,23 ha'), ('PT-05det', 'Entregue dentro da janela com NF-e e laudo por carga'),
    ('IC', 'insumo(s) mais baratos'), ('IC', 'contra a referência da safra'),
]

def norm(s): return ' '.join(unicodedata.normalize('NFC', str(s or '')).replace(' ', ' ').lower().split())

MOVEL = ('MB-', 'OS-0424-app')
OK, FA = [], []
def chk(nome, cond, info=''):
    (OK if cond else FA).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else '· ' + str(info)[:300]))

telas = []
for t, *_ in TIRADAS + FICAM:
    if t not in telas: telas.append(t)
p, srv = servir(R); c = Chrome(); J = c.js; ERR = {}
try:
    modo = None
    for t in telas:
        m = t.startswith(MOVEL)
        if m != modo: c.aparelho(390, 844, 1, True) if m else c.aparelho(1440, 900, 1, False); modo = m
        c.goto(f'http://127.0.0.1:{p}/{t}.dc.html', 1.2)
        vis = norm(J("document.body.innerText"))
        dica = norm(J("(()=>{ const b=document.querySelector('header button.g2-info'); return b?(b.getAttribute('data-dica')||''):''; })()"))
        errs = json.loads(J("JSON.stringify(window.__errs||[])") or '[]')
        if errs: ERR[t] = errs
        for tt, frase, fora, na_dica, fonte in TIRADAS:
            if tt != t: continue
            chk(f'T {t}: fora da vista · “{frase[:70]}”', norm(fora) not in vis, fora)
            if na_dica: chk(f'D {t}: na dica ⓘ · “{na_dica[:70]}”', norm(na_dica) in dica, dica[:200] or 'sem ⓘ')
        for tt, fica in FICAM:
            if tt == t: chk(f'F {t}: segue à vista · “{fica[:70]}”', norm(fica) in vis, fica)
    # Q · o ⓘ novo do app (cabeçalho do mobile37): toque curto abre a dica com as regras e tocar de novo fecha; alvo ≥ 44 × 44 px; o selo
    # do cabeçalho continua logo depois do título (o anúncio "Tela: … · estado" e o realce do estado leem o irmão do h1)
    c.aparelho(390, 844, 2, True); c.goto(f'http://127.0.0.1:{p}/MB-02.dc.html', 1.2)
    DICA = "JSON.stringify((()=>{const d=document.getElementById('g2-dica'); return d&&!d.hidden&&d.getClientRects().length?d.innerText.trim():'';})())"
    b = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('header button.g2-info[aria-label=\"Regras desta tela\"]'); if(!b) return null; const r=b.getBoundingClientRect(); "
                     "return {x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height,d:b.getAttribute('data-dica')||''};})())") or 'null')
    d1 = d2 = ''
    if b: c.toque(b['x'], b['y']); time.sleep(.4); d1 = json.loads(J(DICA) or '""'); c.toque(b['x'], b['y']); time.sleep(.4); d2 = json.loads(J(DICA) or '""')
    chk('Q MB-02 390 px: toque curto no ⓘ abre a dica com as regras e tocar de novo fecha', bool(b) and bool(b['d']) and d1 == b['d'].strip() and d2 == '', [b, d1[:80], d2[:80]])
    chk('Q alvo do ⓘ do app ≥ 44 × 44 px', bool(b) and min(b['w'], b['h']) >= 44, b)
    irmao = J("(document.querySelector('header h1')||{}).nextElementSibling ? document.querySelector('header h1').nextElementSibling.innerText.trim() : ''") or ''
    chk('Q MB-02: o selo do cabeçalho segue logo depois do título (o ⓘ vem depois do selo)', irmao == '1 impedida · 1 revogada', irmao)
    e = json.loads(J("JSON.stringify(window.__errs||[])") or '[]')
    if e: ERR['MB-02 (toque)'] = e
    # A · na web o ⓘ fica logo depois do h1 (shell37): o anúncio da tela e o realce do estado leem o selo, não o ⓘ (antes: "Tela: … · i")
    c.aparelho(1440, 900, 1, False); c.goto(f'http://127.0.0.1:{p}/CA-02.dc.html', 1.5)
    a = json.loads(J("JSON.stringify((()=>{ const h=document.querySelector('header h1'); const i=h&&h.nextElementSibling; const s=i&&i.classList.contains('g2-info')?i.nextElementSibling:null; "
                     "return {msg:((window.__g2realces||[])[0]||{}).msg||'', tit:h?h.textContent.trim():'', selo:s?s.textContent.replace(/\\s+/g,' ').trim():'', info:!!(i&&i.classList.contains('g2-info'))}; })())") or '{}')
    chk('A CA-02 1440 px: com o ⓘ ao lado do título, o anúncio é "Tela: título · estado" (não "· i")',
        a.get('info') and bool(a.get('selo')) and a.get('msg') == f"Tela: {a.get('tit')} · {a.get('selo')}", a)
    e = json.loads(J("JSON.stringify(window.__errs||[])") or '[]')
    if e: ERR['CA-02 (anúncio)'] = e
finally:
    c.close(); srv.terminate()
chk('E sem erro de JS nas telas abertas', not ERR, ERR)
print(f'\n{len(OK)} OK · {len(FA)} falhas · {len(telas)} telas · render {R}')
sys.exit(1 if FA else 0)
