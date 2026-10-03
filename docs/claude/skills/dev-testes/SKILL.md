---
name: dev-testes
description: Defina e execute testes proporcionais ao comportamento e risco, incluindo unitários, integração, contrato, E2E e carga quando pertinente. Use em implementação, regressões, diagnóstico de testes e critérios de liberação.
---

# Testes automatizados — reduzir falhas com evidência

Teste comportamentos e riscos, não contagens. Nenhuma suíte garante ausência absoluta de bugs. Ajustes de texto/instruções ou visuais reversíveis sem mudança de comportamento podem ser verificados por leitura/inspeção; não criar testes que só repetem a implementação.

## TDD por padrão
1. **Vermelho:** escrever o menor teste que descreve o comportamento desejado e vê-lo falhar (pelo motivo certo).
2. **Verde:** o código mais simples que passa.
3. **Refatorar:** limpar duplicação e nomes com a suíte verde.
Bug reportado → reproduzir e escrever a regressão quando viável → corrigir → verificar. Execute os testes afetados a cada mudança; amplie para a suíte exigida no gate de entrega, sem repetir baterias intactas sem motivo.

## Pirâmide (referência, não quota)
| Nível | O que cobre | Velocidade | Quanto |
|---|---|---|---|
| **Unitário** | regras de negócio, cálculos, validações, reducers, utils, componentes isolados | ms | 70 % |
| **Integração** | módulo + banco real (Testcontainers/Docker), handlers HTTP, filas, repositórios, componentes com dados | ~100 ms–1 s | 20 % |
| **Contrato** | forma das APIs entre front/back e serviços (OpenAPI/Pact); schema do banco vs. ORM | rápido | por API |
| **E2E** | 5–15 fluxos críticos completos no navegador/dispositivo (login, cadastro, compra, fluxo principal) | s | 10 % |
| **Propriedade** | invariantes com dados gerados (fast-check / Hypothesis) para parsers, cálculos, serialização | — | onde há lógica densa |
| **Mutação** | Stryker / mutmut no núcleo de domínio: prova que os testes detectam mudanças | lento, CI noturno | domínio |
| **Carga** | k6 nos endpoints críticos antes de lançar e antes de picos | — | pré-lançamento |

Mocks só na fronteira do sistema (APIs de terceiros, relógio, aleatoriedade, e-mail). **Banco de dados é real** nos testes de integração (Docker), nunca mockado.

## O que obrigatoriamente testar
- Caminho feliz, **limites** (0, 1, máximo, vazio, nulo, unicode, negativo), **erros** (entrada inválida, rede falha, timeout, concorrência).
- Dinheiro, arredondamento, datas/timezones/horário de verão, ordenação com acentos.
- **Permissões**: cada endpoint com usuário sem permissão → 403; sem login → 401; outro tenant → 404.
- Idempotência de operações repetidas e concorrentes; migrações com dados, compatibilidade e recuperação. Um rollback de código não exige nem autoriza apagar dados com uma migração reversa.
- Estados de UI: vazio, carregando, erro, sucesso; acessibilidade (axe) nos componentes.

## Como escrever testes bons
- **Nome descreve comportamento**: `deve rejeitar pedido com quantidade zero` / `test_rejects_zero_quantity`. Um comportamento por teste.
- Estrutura **Arrange–Act–Assert**, sem lógica (if/loop) dentro do teste.
- **Determinístico**: relógio falso, seed fixa, sem `sleep`, sem depender de ordem ou de rede; cada teste cria e limpa seus dados (transação com rollback ou banco por teste).
- Dados via **factories/builders** (`buildPedido({ total: 0 })`), não fixtures gigantes.
- Asserções específicas (`toEqual({...})`, não `toBeTruthy`); mensagens de erro verificadas por conteúdo.
- Testar comportamento observável, não implementação (não asserta chamadas internas nem estado privado).
- Testes de componente com Testing Library: consultar por papel/rótulo acessível (`getByRole('button', { name: 'Salvar' })`), nunca por classe/CSS.
- Metas de duração definidas pelo projeto e medidas. Paralelismo/sharding só com isolamento de dados, portas e perfis; jornadas dependentes declaram sequência e precondições. Scripts agregadores falham quando uma verificação falha; ajuda, zero testes e testes pulados não contam como aprovação.

## Cobertura e confiança
- Preserve os gates já contratados pelo projeto. Em projeto novo, defina metas pelo risco e pela linha de base, sem impor percentuais arbitrários como prova de qualidade.
- Domínio, dinheiro, permissões, concorrência e sincronização exigem cenários felizes, negativos e limites pertinentes. Remover código morto pode mudar a cobertura; avalie a proteção do comportamento, não apenas o percentual. Mutação é útil quando revela lacunas do núcleo, não em toda mudança.

## Testes instáveis (flaky)
Registre causa, responsável e prazo pela criticidade. Não coloque em quarentena a única prova de uma regra crítica para liberar a entrega. Repetições diagnósticas ficam explícitas; testes instáveis não viram aprovação por retry silencioso.

## Ferramentas por stack
| Stack | Unit/Integração | Componentes | E2E | Extras |
|---|---|---|---|---|
| TypeScript/Node/React | **Vitest** (ou Jest) + Testcontainers/`pg-mem` não; usar Postgres real | Testing Library + jest-axe; Storybook + test-runner | **Playwright** (traços, vídeos, sharding) | fast-check, Stryker, MSW (mock de HTTP), k6, `supertest` |
| Python | **pytest** + pytest-asyncio + Testcontainers; `httpx.AsyncClient` para FastAPI | — | Playwright (Python) | Hypothesis, mutmut, factory_boy, freezegun, respx |
| Go | `testing` + testify + Testcontainers | — | Playwright | rapid (property), gomock só na borda |
| Android/Kotlin | JUnit5 + MockK + Turbine | Compose UI tests | Maestro / Espresso | Kotest property |
| iOS/Swift | XCTest / Swift Testing | ViewInspector / snapshot | XCUITest / Maestro | — |
| React Native/Expo | Vitest/Jest + RNTL | RNTL | **Maestro** ou Detox | — |
| Flutter | `flutter test` | widget tests | `integration_test` / Maestro / Patrol | golden tests |

Configurações prontas: [assets/vitest.config.ts](assets/vitest.config.ts), [assets/playwright.config.ts](assets/playwright.config.ts), [assets/pytest.ini](assets/pytest.ini).

## Checklist do PR
- [ ] Comportamentos e riscos alterados têm testes no nível adequado; fronteiras críticas têm integração e jornadas críticas têm E2E
- [ ] Bug corrigido tem teste que falhava antes
- [ ] Nenhum `skip`/`only`/`xit`; nenhum teste com `sleep` ou dependência de ordem
- [ ] Limites, erros e permissões cobertos
- [ ] Gates de cobertura pertinentes atendidos; duração medida; nenhum agregado mascara falha ou ausência de testes
- [ ] Testes legíveis: alguém entende o comportamento só lendo os nomes
