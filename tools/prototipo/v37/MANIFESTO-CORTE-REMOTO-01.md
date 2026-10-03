# MANIFESTO · CORTE-REMOTO-01 (CONTINUIDADE-MAC-20261003)

**Regra:** nenhum valor real da Fazenda Lagoa Grande sai do Mac (CAR, coordenadas, perímetros, RL/APP, áreas por pivô, outorgas, nomes de rios, cenas e imagens Sentinel-2). Os originais ficam só no Mac, em `~/Safrion-recuperacao-local/corte-remoto-01/`, fora do iCloud.

**Repositório:** git novo. A base é um commit raiz sem pais, e nada do histórico anterior vem junto.

**Redigidos e excluídos:** veja `MAPA-ORIGEM-SANITIZADO.json` (chaves `redigidos` e `fora`).

**Ficam só no Mac**, porque contêm valores reais:
- a varredura por valores (`varrer_real.py`);
- o saneador (`sanear.py`);
- o módulo `dados_lagoa_kml.py`;
- a pasta `dados_lagoa/`.

**Vem para a nuvem:**
- `ferramentas/varrer_categorias.py`, que procura por categoria (formato de CAR, id de cena, coordenada precisa, nº de outorga, nome do KML) sem conter valor real;
- `ferramentas/acoes_duplicadas.py`;
- `specs/esquema_lagoa.md`, só a estrutura;
- `specs/padrao-comandos-v3-prompt.md`, o padrão de comandos v3.1;
- `docs/claude/`, com as instruções do proprietário e as skills, sem segredos (conferido).

**Conferido antes de entregar, nos 4 snapshots:**
- varredura por valor real: TOTAL 0;
- varredura por categoria: TOTAL 0;
- nomes de rio: 0;
- compilação Python: ok.

No bundle, todos os blobs alcançáveis foram varridos, não só a ponta (recibo junto do bundle).

**Pendente na nuvem:**
- camada sintética, depois build, montar_render e varredura 145/145;
- testes que dependem da Lagoa Grande, com nova linha de base declarada;
- verificar e corrigir REND-S5 e AÇÃO;
- integração e publicação da v44.

O artefato publicado hoje usa dados reais. Publicar a partir da nuvem troca pelos dados sintéticos: combine antes com o Codex e o Adrianus.
