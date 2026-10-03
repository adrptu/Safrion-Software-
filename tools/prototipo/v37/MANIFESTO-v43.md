# MANIFESTO-v43 — backup do gerador do protótipo (CONTINUIDADE-MAC-20261003)

- **Base:** 310844a3305401ca17655a5bb8617f5f8aa6d460 (branch claude/prototipo-gen37-fonte). **Branch:** prototipo/v43. Sem merge para main, sem PR de implementação.
- **Origem dos arquivos:** base durável do Claude `cons/work/fontes-claude/prototipo-v37/gen37` no estado da v43 publicada (artefato versão 43, id 1791045948-ee9d).
- **Validação da v43 nessa origem (registrada no canal):** suíte de 80 testes sem regressão nova (os 15 vermelhos já falhavam na v42), varredura 145/145 páginas sem erro, build determinístico (dois builds com páginas idênticas).
- **Filtro (o mesmo da base):** .py/.js/.json/.md/.css/.sh fora de _render/__pycache__; páginas geradas project/*.dc.html; sondas _probe/*.py. Incluídos 497 arquivos do gen37 e 6 JSONs irmãos (tools/prototipo/v37/*.json).
- **Segredos:** varredura por padrões de token/chave/senha/e-mail nos arquivos incluídos: 0 achados.

## Dados reais fora deste commit (22 arquivos)
Contêm dado real da Fazenda Lagoa Grande (CAR, coordenadas e área dos pivôs, cenas Sentinel-2, safra sobre os pivôs reais). Ficam na base durável local e no checkpoint `cons/work/fontes-claude/checkpoint-20261003/fontes_qm_gen37.tgz`. **A inclusão deles no repositório depende da decisão do Adrianus.** Sem eles, esta branch não reconstrói as telas (o gerador importa esses módulos).
- dados_cad.py
- dados_lagoa/analisar.py
- dados_lagoa/analisar_test.py
- dados_lagoa/baixar.py
- dados_lagoa/baixar_rgb.py
- dados_lagoa/busca.json
- dados_lagoa/cenas.json
- dados_lagoa/lagoa_analise.json
- dados_lagoa/lagoa_cadastro.json
- dados_lagoa/lagoa_rgb.json
- dados_lagoa/lagoa_s2.json
- dados_lagoa/lagoa_s2_resumo.json
- dados_lagoa/processar.py
- dados_lagoa_safra.py
- project/AG-01.dc.html
- project/AG-01det.dc.html
- project/AG-03.dc.html
- project/AG-04.dc.html
- project/CD-01.dc.html
- project/CD-01det.dc.html
- project/IN-04.dc.html
- project/MB-06.dc.html

## Arquivos mantidos na versão da base, sem a v43 (174)
São as sondas antigas e o support.js que não existem na origem v43, além das versões-base dos arquivos de dado real acima, que não contêm dado real. Saem do backup só as 2 páginas geradas que a v43 não produz mais: IN-02det e IN-02x-os0420.

## Excluídos pelo filtro (não são fonte)
- fora do filtro da base: 116

## v44 parcial (snapshot separado, fora desta branch)
- fontes_base_v43m_gen37.tgz · sha256 7571a12908db028f87265327e71d58a069aeec90531eb301ace4d3ac9887d4b5
- fontes_qm_gen37.tgz · sha256 75dd6f000c5ea6cca2f8288eee3fa368e3a1b5c1e2467b87a7d4f9dca72f2c91
- fontes_qr_gen37.tgz · sha256 7e05a2aa8b25470db9ffb9b1ab276ddf71566b5e3d6e6b17802274069850b24d
- fontes_qu_gen37.tgz · sha256 02f96e2079aade9e83b184ef3ba0207044861df2255e4f6fc9c7b3039055e286
- qr = REND-MULTICONJUNTOS (implementação concluída; verificação em andamento); qu = UX-ACAO-UNICA (implementação interrompida às 16:48Z e retomada em série). Snapshot das 16:48Z, antes da retomada.
