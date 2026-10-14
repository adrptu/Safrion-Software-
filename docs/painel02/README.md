# PAINEL02 — colheita por cultivo e período

Contrato6159867848; revisão Claude6160679862. Autor Codex; revisor/integrador Claude. Base do PR4f222e840a18aa6aa68fd86f5b71673392772e74; correção exercitada com composição v66/5eb1ba70936f4e311a155b20024a166940a54e0c. Somente dois arquivos de código: areas/painel_agricola.py e painel_agricola_test.py. paineis.py, Manutenção, domínio e composição permanecem com Claude.

A semana em curso usa prVersaoSem e passes daquele período; anuais usam previsão e resultado da safra. Não soma culturas/unidades. Previsão ausente e café a apurar têm chave numérica nula explícita: ficam no fim nas duas direções de ordenação, sem converter o número contido no rótulo em produção medida.

## Integração pelo revisor

O módulo exporta secao() → (HTML, JS), sem reset de tela, shell ou build automático. No ramo PAGR de paineis.build, após inicializar E e antes de shell37, chamar secao(), inserir seu HTML abaixo dos quatro cartões e incorporar JS em E.EXTRAJS. No EXTRAVALS único existente chamar pnaVals(self,v) somente quando PN_ID==='PAGR'. Preservar cenOuvir/modVolta já existentes, cartões e ação Consultar O.S. A seção não substitui o painel.

Escolhida a alternativa expressamente aceita na revisão: filtros de coluna G2, sem faixa adicional. Cultivo · fazenda identifica também cultura/variedade. Nenhuma frase fixa nova de escopo; regras no ⓘ de 44px. Preserva G2 para filtro/busca/ordenação e retorno ao cultivo COLH.

## Provas executadas nesta correção

Sobre cópia sintética isolada de v66/5eb1ba7, sem editar paineis.py:
- build147/render156 previamente verificados.
- painel_agricola_test.py --prepare compõe em memória a seção e os cartões reais; montar_render.py regenerou156.
- painel_agricola_test.py:20/20 exit0. Usa o g2sort real para anual sem previsão e café a apurar nas duas direções.
- painel_agricola_test.py --ui:24/24 exit0 em1440/390. Inclui cartões/ação preservados, posição abaixo dos cartões, ausência da frase redundante, valores/períodos, Enter/toque real, ajuda/Escape, destino, volta com busca/foco e ausência de overflow/erroJS.

Brutos novos em provas/r2/. Os brutos anteriores foram preservados como histórico. A composição acima é harness de teste: Claude ainda precisa aplicar o gancho ao produto, revisar e integrar. Não executado leitor de tela, auditoria integral nem HML. Os testes painel_modulos/nav_modulos serão reconciliados/executados pelo integrador na candidata composta.

Aplicado: origem, período, unidades, cartões e grade existente. Fora: custos/impedimentos/execução/MIP, publicação e aplicação real. Cortado: instrução redundante da seção e substituição indevida dos cartões. O conjunto PAINEL02 continua parcial.
