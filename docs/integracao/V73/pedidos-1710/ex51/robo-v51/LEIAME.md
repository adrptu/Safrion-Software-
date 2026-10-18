# EX51 · Robô v5.1 · candidata para revisão

Autor Codex, revisor/integrador Claude. Base 259c13bcb338df2643bc45e270cb075488660cc1. Contratos 6241229682/6241254289. Arquivos novos nesta pasta; fontes e brutos v5 preservados. Não muda o produto.

O v5 podia usar o hash observado no destino como alvo esperado e aceitar qualquer diálogo/texto corporal na segunda passada. Esta candidata captura o alvo na origem, exige ID exato no título do painel ou item selecionado, inclui RA e exclui CMD/EX/DEC. Sem alvo único, publica inconclusiva separada. Relata erros e prefixos que continuam texto. A passagem por `[data-g2pilha]` e o link “Abrir na tela de …” ficam separados nos brutos, com o mesmo alvo. Voltar exige a tela original e o título original, incluindo o empilhado quando presente.

O executor reaproveita preparar.py/servidor.py da pasta irmã robo-v5-base. Usa uma origem por trabalhador, testa marcas cruzadas no localStorage antes de começar e conserva escopo28. O modo pacote não é válido para v5.1. Usa o Chrome já autorizado do executor Claude; não executar como alternativa a uma interface bloqueada.

```sh
node oraculo_test.cjs
python3 -I resumo_test.py
python3 -I rodar.py --render <render imutável> --trabalho <pasta nova> --entrega <pasta nova>
```

Executado por Codex: 20 contraprovas JS das funções reais de alvo/chegada; fixture do resumo que rejeita destino errado e a aprovação frouxa da segunda passada; sintaxe JS/Python. Não executados: navegador, isolamento real, empilhado real, escopo28 e linha de base. Claude deve revisar e rodar na mesma candidata. A análise de sintaxe não substitui esses aceites.

Não comparar taxas diretamente com v108/v5. comparacao.json declara métodos não comparáveis. A revisão da nova base precisa confrontar cada passagem com os brutos v5 e justificar diferenças; os brutos contêm origem, clique, alvo e destino. Esta candidata não automatiza esse confronto semântico.

O comando padrão executa também `casos_criticos.py`, adaptado da prova do revisor Claude em c1c30e24 (fontes e brutos originais preservados), pelas listagens e pelos endereços dirigidos. `aceite.py` exige os dois recibos, inventário crítico explícito, ausência de casos inconclusivos/falhos e as quatro taxas (IDs clicáveis, chegada, volta à origem e Voltar reabre) ≥95% cada, com denominadores não vazios. Ausência de evidência bloqueia. `PASSOU_MEDICAO` é somente resultado desta medição, nunca liberação da F1. O inventário de IDs é específico desta candidata: mudanças de dados exigem revisão do inventário. Use pastas novas; não reutilize recibos de outra execução/render. Execução parcial não serve para aceite.

Correção da revisão 6242167973: fragmento separado antes de decodificar query; alvo primário exato sem aceitar sufixo /2 ou ID secundário; h1 aceito só sem diálogo; diálogo sem título nunca usa corpo. Segunda passada exige o mesmo destino observado no clique. Resumo separa navegação de tela de registro inconclusivo, inclui arquivos de erro, herança medida e contagens de empilhado/dona/retorno. São correções candidatas A1–A11, sujeitas à contraprova do revisor no mesmo render.

Validação local adicional: `node segunda_passada_test.cjs`, `python3 -I segunda_passada_test.py` (7 casos), `python3 -I aceite_test.py` (6 casos) e `python3 -I resumo_test.py`. O teste do resumo cobre erro de execução e herança, além da chegada estrita. Nenhum desses testes executa navegador; isolamento, histórico, empilhado e novo inventário dirigido continuam pendentes de execução real.

Limites: nomes de cadastros sem data-ref explícito não são inferidos. Título/seleção provam chegada estrutural, não regra de negócio. Restauração de foco, seção e rolagem exige os testes T3/T5/T7 da F1. O teste de marcas observa armazenamento; isolamento do histórico depende do arranjo de abas/origens do executor e deve ser retestado no navegador.

## Correção candidata da rodada 2 (6243792206)

N1: o clique na dona captura sua própria URL anterior; uma mudança anterior do hash da pilha não encerra essa espera. O portão exige navegação entre telas diferentes e o resumo só conta chegada à dona em `navega`. O título original é preservado para Voltar. N2: `abre` define o destino; contexto (`painel`, `vis`, `de`, `para`, `ver`, `sob`) não vira alvo; IDs restantes conflitantes são inconclusivos. N3: OM→OS usa destino OS explícito, não menção textual a OS em link SM. OS→EST/outro é informativo; falhas críticas incluem a identificação do caso. A4: texto com IDs também indica intenção de registro. N5: o título/h1 que sustentou chegada fica no bruto.

N4 parcial: origem exige primeiro ID, não substring. Vínculo automático entre recibo, execução e render permanece pendente; pasta nova continua obrigatória. N6 parcial: openRow espera o aparecimento do diálogo (limite 6 s); resumo da primeira passada, encerramento de Chrome após timeout e tempo da fase críticos permanecem pendentes. Nenhuma dessas pendências foi declarada resolvida.

Executados localmente: oraculo_test.cjs (inclui 3 novos fragmentos N2), segunda_passada_test.cjs, segunda_passada_test.py, resumo_test.py (inclui pilha sem navegação), aceite_test.py (14 contraprovas, incluindo cada meta zerada, mesma tela, origem ambígua e caso informativo), rodada2_test.py (3 classificações N3), compilação Python. Reteste real da página sintética lenta com dona errada e da base de 181 arquivos deve ser feito pelo revisor; não executado por Codex.

O requisito OS↔RA permanece obrigatório. A incompatibilidade com F1 sem dona de RA requer decisão registrada no desenho da F1; este PR não adia silenciosamente o aceite nem altera telas.
