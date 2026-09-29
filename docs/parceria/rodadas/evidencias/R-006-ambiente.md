# Ambiente local para a F0: inventário (27/09/2026, Claude Code)

Rótulos: **[verificado]** = saída de comando nesta sessão; **[especificado]** = escrito no repositório (PRD, ADR, CI, STATUS); **[não verificado]** = sem fonte conferida. Nada foi instalado, baixado ou alterado. Único arquivo escrito: este.

## 1. Máquina [verificado]
- macOS 26.5.2 (25F84), Apple Silicon (arm64), 8 CPUs, 8 GiB de RAM (8589934592 bytes).
- Disco do usuário (/System/Volumes/Data): 228 GiB, **12 GiB livres, 94% usado**.
- Xcode Command Line Tools: presente (`/Library/Developer/CommandLineTools`, pacote 26.4.1).
- Homebrew: **ausente** (sem `brew`, sem `/opt/homebrew`, sem `/usr/local/Homebrew`).
- git 2.50.1 (Apple) em `/usr/bin`. python3 do sistema 3.9.6; python3 do runtime do Codex 3.12.14 (a CI usa 3.12).
- `gh`: ausente.

## 2. Node e pnpm [verificado]
- PATH comum: `node`, `npm`, `pnpm`, `corepack` **ausentes**. Sem nvm, fnm, volta, asdf ou mise.
- Runtime do Codex: `.../codex-primary-runtime/dependencies/node/bin/node --version` → **v24.19.0**.
- O caminho pedido `.../dependencies/node/bin/fallback/pnpm` **não existe**. O pnpm real está em `.../dependencies/bin/fallback/pnpm` (script bash que chama o node acima com `node_modules/pnpm/bin/pnpm.mjs`) → **11.25.0**.
- Sem npm e sem corepack no runtime do Codex.
- O script do pnpm do Codex exporta `pnpm_config_pm_on_fail=ignore`: ele **ignora** divergência entre o `packageManager` do projeto e a versão em uso.

## 3. Docker e contêineres [verificado]
- `docker`, `colima`, `podman`, `orb`/`orbctl`, `limactl`, `lima`, `nerdctl`, `rdctl`, `container` (Apple): todos ausentes do PATH.
- Sem Docker.app, OrbStack.app, Podman Desktop.app ou Rancher Desktop.app em `/Applications`; sem Docker.app em `~/Applications`.
- Sem socket (`/var/run/docker.sock`, `~/.docker/run/docker.sock`) e sem `~/.docker`, `~/.colima`, `~/.orbstack`, `~/.rd`, `~/.testcontainers.properties`.
- `docker info` não foi rodado: não há binário. **Nenhum runtime de contêiner nesta máquina.**

## 4. PostgreSQL [verificado]
- `psql`, `postgres`, `pg_ctl`, `initdb`, `pg_isready`: ausentes.
- `brew list | grep postgres`: não se aplica (sem Homebrew).
- Sem Postgres.app (`/Applications`, `~/Applications`) e sem `/Library/PostgreSQL`. PostGIS: nenhum.

## 5. Repositório `do-talhao-a-os` [verificado, só leitura, sem fetch]
- `origin` → `https://github.com/adrptu/Safrion-Software-.git` (fetch e push).
- Branch atual `docs/r005-missao-metodo`, **sem upstream**. Locais: essa e `main`. Remotas: `origin/main`.
- Últimos commits: `c3616d2` (R-005), `a1f5b16` (R-004), `7f2f1a8`, `3ecdaac`, `c629175`.
- HEAD está 1 commit à frente de `origin/main` (ref local); `main` = `origin/main`. `git status` limpo.
- Não existem `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `.nvmrc`, `.node-version` nem arquivo Compose.
- `python3 tools/ci/checar_contrato_codigo.py` rodado localmente → "N/A ... repositório só de documentação", saída 0.
- `docs/architecture/versions.md`: **nenhuma versão fixada** (Node, pnpm, TypeScript, Next, Postgres/PostGIS, Prisma, Vitest, Testcontainers etc.).

## 6. O que a CI exige quando houver `package.json` [especificado: `ci.yml` + `checar_contrato_codigo.py`]
- `package.json` **e** `pnpm-lock.yaml` juntos. Só um dos dois = falha.
- `packageManager` exato no formato `pnpm@X.Y.Z` (hash `+sha...` opcional).
- `engines.node` preenchido.
- `.nvmrc` com versão exata `X.Y.Z` (o `setup-node` lê `node-version-file: .nvmrc`).
- Scripts na raiz, não vazios: `format:check`, `lint`, `typecheck`, `test`, `build`. Rodam **sem** `--if-present`.
- Ordem no job `codigo` (ubuntu-latest, 30 min): `pnpm install --frozen-lockfile` → `format:check` → `lint` → `typecheck` → `test` → `build`.
- `pnpm/action-setup` é chamado sem `version`; a versão viria do `packageManager` [não verificado nesta sessão; STATUS diz que os inputs foram conferidos no `action.yml`].
- Outros jobs: documentação (Python 3.12, `checar_docs.py` + `unittest`), Gitleaks, Trivy fs (HIGH/CRITICAL).
- **Lacuna:** o job `codigo` não declara `services: postgres`. Integração com Postgres real na CI dependerá de Testcontainers no Docker do runner [disponibilidade de Docker no runner: não verificado nesta sessão] ou de um service container a acrescentar.
- A CI remota **não roda hoje**: conta do GitHub bloqueada, segundo `docs/STATUS.md` [especificado].

## 7. O que a F0 pede do ambiente [especificado: R-002 §5, PRD cap. 23 e 25, ADR 0001]
- Monorepo pnpm com versões fixadas; `packages/domain`; `packages/db` com migração inicial; RLS com teste de isolamento na credencial real (ENG-025); envelope de comando; shell web; `pnpm check` real.
- Integração = **Vitest + Testcontainers com PostgreSQL/PostGIS** (PRD, tabela de testes). ENG-034 proíbe trocar por mocks ou SQLite.
- Comandos contratados (`pnpm setup`, `doctor`, `test:integration`...) **ainda não existem**.
- A F0 não vai à homologação; prova-se por testes na CI (R-002).

## 8. O que falta para rodar a F0 localmente
| # | Falta | Situação | Bloqueia |
|---|---|---|---|
| 1 | Runtime de contêiner compatível com Docker (Testcontainers depende dele) | Ausente [verificado] | Testes de integração locais em Postgres real |
| 2 | Imagem PostgreSQL + PostGIS para arm64 | Ausente; exigirá download. Imagem arm64 nativa: [não verificado] | Idem |
| 3 | Node e pnpm próprios do projeto | Só no runtime do Codex, fora do PATH [verificado] | Reprodutibilidade; o Claude Code não tem node no PATH |
| 4 | Versões fixadas (`versions.md`, `.nvmrc`, `packageManager`) | Nenhuma [verificado] | Contrato da CI |
| 5 | Dependências npm | Exigirão download (`pnpm install`) | Tudo que é código |
| 6 | Espaço em disco | 12 GiB livres [verificado]; tamanho de runtime + imagem + `node_modules`: [não verificado] | Pode faltar |
| 7 | Memória | 8 GiB [verificado]; folga para VM + Postgres + Next + Vitest: [não verificado] | Pode ficar lento |

## 9. Menor caminho para preencher a falta (não executado)
1. **Decisão do proprietário: instalar um runtime de contêiner.** Opções: Docker Desktop, OrbStack (ambos `.app` para download) ou Colima (pede Homebrew, que também falta, ou instalação manual) + CLI `docker`. Licença, custo e necessidade de senha de administrador: [não verificado]; conferir na fonte oficial antes de escolher. Os agentes não instalam.
2. **Conferir espaço:** ver o tamanho oficial do runtime e da imagem antes; se passar do que cabe em 12 GiB com folga, liberar espaço primeiro.
3. **Fixar versões na fonte oficial, na data** (Node LTS, pnpm, Postgres/PostGIS, Testcontainers etc.) e gravar em `versions.md`, `.nvmrc`, `engines.node` e `packageManager`. Se escolherem Node 24.19.0 e pnpm 11.25.0, o runtime do Codex serve para verificação local, desde que a versão do pnpm seja exatamente a fixada (o `pm_on_fail=ignore` não avisa).
4. **Para o Claude Code rodar sozinho:** Node no PATH (instalador oficial ou gerenciador de versões), ou chamar o runtime do Codex pelo caminho completo. Ambos: download ou dependência de caminho interno.
5. **Downloads necessários, na ordem:** runtime de contêiner → `pnpm install` (registro npm) → imagem Postgres/PostGIS (baixada pelo Testcontainers na primeira execução).
6. **Antes do primeiro commit com código:** rodar `checar_contrato_codigo.py` localmente e confirmar "OK".
7. **CI:** decidir entre Testcontainers no runner ou `services: postgres` no job `codigo`; só vale depois de a conta do GitHub ser liberada.
- Sem o passo 1, a F0 pode avançar em `packages/domain` (unidade e propriedade, sem banco), mas **não** em RLS, migração, envelope atômico e outbox.

## 10. Riscos
- **Hoje não há onde rodar integração em Postgres real:** a máquina não tem runtime de contêiner nem Postgres, e a CI remota está bloqueada. A F0 não pode ser declarada pronta enquanto isso durar.
- Disco a 94%: runtime, imagens, `node_modules` e cache do pnpm podem esgotar o espaço (tamanhos [não verificado]).
- 8 GiB de RAM: a VM do contêiner disputa memória com Next, Vitest e, depois, Playwright.
- Depender do runtime do Codex: caminho interno que pode mudar sem aviso; o pnpm dele ignora divergência de `packageManager`; o caminho informado na tarefa (`node/bin/fallback/pnpm`) estava errado.
- Imagem PostGIS em arm64: se só houver amd64, a emulação fica lenta [não verificado].
- Branch atual sem upstream e sem fetch nesta sessão: `origin/main` local pode estar desatualizada; a F0 deve nascer em `feat/f0-fundacao` a partir de `main` conferida.
- Tudo que falta exige download; nada foi baixado. Nada aqui é homologação: homologação exige candidata por commit, deploy e autorização de custo do proprietário (AGENTS.md, R-002).
