# PAINEL02 — colheita por cultivo e período

Contrato6159867848 (PR61), resposta a PN-DECISAO/6159523648. Autor Codex; revisor/integrador Claude. Base4f222e840a18aa6aa68fd86f5b71673392772e74. Somente dois arquivos novos de código; Manutenção, paineis.py, domínio e composição continuam com Claude.

A semana em curso de uma cultura semanal usa prVersaoSem e somente os passes daquela semana. Anuais usam a previsão e o resultado da safra do cultivo. Não soma culturas ou unidades; previsão ausente não vira zero; café a apurar permanece explícito. Sem porcentagem de desvio final de período aberto. Usa G2 existente para busca, ordenação e filtros; abre COLH#cultivo com teclado/toque; volta conserva busca e foco. É uma primeira leitura de colheita no PAGR, não o encerramento do painel agrícola: custos, impedimentos, execução e MIP continuam pendentes da composição de getters canônicos.

## Integração pelo Claude
Em areas/paineis.py, dentro do for de build(), antes do antigo corpo de PAGR:

```python
if fid == 'PAGR':
    from areas.painel_agricola import render
    render()
    continue
```

O módulo novo exporta render(), sem build() automático, para não ser executado e depois sobrescrito pelo gerador antigo na descoberta alfabética de build.py. Nenhuma mudança automática de menu ou do PMAN/PSUP. Confirmar antes a integração dos commits18322fe/e2e2385 de PR61 (foco de teste e corte de gráfico redundante). O teste antigo de PAINEL01 precisa ser reconciliado pelo integrador: asserções PAGR quatro contadores/primeiro link OS foram substituídas por esta fatia; manter os casos PMAN/PSUP/PCOM e os testes novos. Não apagar falhas silenciosamente.

## Provas executadas

Dados sintéticos, perfil/servidor locais isolados:

```sh
SAFRION_DADOS=sintetico python3 build.py
SAFRION_DADOS=sintetico python3 -c 'from areas.painel_agricola import render; render()'
SAFRION_DADOS=sintetico python3 montar_render.py
python3 painel_agricola_test.py
python3 painel_agricola_test.py --ui
```

Build147/render156; unidade13/13 exit0; UI20/20 exit0 em1440 e390. Brutos em provas/. Unidade inclui fatos do seed (Pivô19:72.9t previstas/36.42t recebidas), previsão futura, passe de outra semana, fonte ausente e café a apurar. Contraprovas de projeção substituem apenas o retorno de prTal em dois casos, explicitamente no teste; demais casos usam motor real. UI usa Enter no desktop, toque real no celular, verifica destino e restauração de busca/foco. Grade no celular rola horizontalmente dentro do conteúdo, sem overflow da página; não houve teste de leitor de tela. Sem nova bateria integral.

Aplicado: período/origem/unidades explícitos, grade existente e destino canônico. Fora: indicadores de custo/impedimento/MIP, publicação e aplicação real. Cortado: contadores de O.S. e gráfico repetidos no PAGR, substituídos pela comparação focal. Não é painel completo nem nova entidade/menu.
