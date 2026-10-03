---
name: dev-frontend-mobile
description: Implemente e revise interfaces web, PWA e mobile com estado, formulários, desempenho, acessibilidade, offline e sincronização confiáveis. Use ao alterar telas, componentes ou navegação executável.
---

# Frontend e mobile — meta: rápido, robusto, sem bug de tela

UX/UI é `ux-essencial`; organização das telas (listagem → detalhe → sub-detalhe, rotas `/entidade`, `/entidade/:id`) é `master-detail-ux`; tabelas é `tabelas-interativas`. Aqui é a engenharia por trás.

## Estrutura e código
- **Organização por feature**, não por tipo: `src/features/pedidos/{components,hooks,api,schemas,index.ts}`; `src/shared/{ui,lib,hooks}` só para o que é realmente genérico. Feature exporta só pelo `index.ts`; sem import cruzado entre features (usar `shared` ou compor na página).
- **TypeScript estrito** (`dev-revisao/assets/tsconfig.strict.json`); props tipadas; sem `any`; discriminated unions para estados (`{status:'loading'} | {status:'error', error} | {status:'ok', data}`), nunca vários booleanos.
- **Componentes coesos**, uma responsabilidade; lógica em funções testáveis. Não fragmentar só por contagem de linhas. Regra compartilhada de domínio não substitui validação autoritativa no servidor.
- **Design system** único: o design system do projeto prevalece; usar seus tokens e componentes em `shared/ui`, sem hex/px solto. M3 de `ux-essencial` vale somente na ausência de padrão. Storybook quando o projeto adotar, sem introduzi-lo por obrigação em toda mudança.
- Sem duplicação: verificar `shared/ui` antes de criar componente; variantes via props, não cópia.

## Estado (três tipos, três ferramentas)
| Tipo | Ferramenta | Regra |
|---|---|---|
| **Servidor** (dados da API) | TanStack Query / SWR / RTK Query; Server Components + Server Actions no Next | cache, revalidação, retry, **atualização otimista**; nunca copiar para estado global |
| **Cliente** (UI: modal aberto, rascunho) | `useState` local → Zustand/signals/Riverpod/ViewModel só se compartilhado | mínimo possível; derivar em vez de duplicar |
| **URL** (filtro, aba, página, item aberto) | router (`searchParams`) | tudo que o usuário quer compartilhar/recarregar/voltar |

Cliente de API **tipado e gerado do OpenAPI** (openapi-typescript/orval); schemas zod compartilhados com o backend quando monorepo.

## Formulários e dados
- Reutilizar a biblioteca do projeto; schema, validação útil, teclado e autocomplete corretos. Autosave preserva rascunho; comandos de negócio exigem envio explícito. Atualização otimista só onde reversível, com pendência visível e sem afirmar aceite antes do recibo.
- Datas: `Intl`/`date-fns` com fuso explícito; números/moeda com `Intl.NumberFormat('pt-BR')`. Nunca `toFixed` para dinheiro.
- Listas > 200 itens virtualizadas (TanStack Virtual / FlashList / `ListView.builder`).

## Rotas, erros e carregamento
- Rotas com **lazy loading** por página; **error boundary** por rota e por widget crítico com ação de tentar de novo; `Suspense` com skeleton no formato do conteúdo.
- Tratamento global: erro de rede → snackbar com "Tentar de novo"; 401 → renovar token/login mantendo a rota de retorno; 403/404 → página própria.
- Erros e Web Vitals enviados ao Sentry (com release e source maps); nunca falhar em silêncio.

## Performance (orçamento medido no CI)
- **Web**: JS inicial ≤ 200 kB gz; LCP < 2,5 s, INP < 200 ms, CLS < 0,1 (Lighthouse CI no pipeline, falha se regredir). Code splitting, `next/image`/`<img width height loading=lazy>`, fontes com `display=swap` e preload, sem biblioteca pesada para coisa pequena (checar bundle com `source-map-explorer`), memoização só onde medido, sem re-render em cascata (React DevTools Profiler / React Compiler).
- **Mobile**: 60 fps em listas (FlashList/RecyclerView/`ListView.builder`), imagens em cache com tamanho certo, sem trabalho pesado na thread de UI, startup < 2 s, Hermes ativado (RN), tamanho do app monitorado.
- Pré-carregar a próxima tela provável; stale-while-revalidate; `prefetch` nos links visíveis.

## Segurança no cliente
- Nada de segredo no bundle (só chaves públicas); chamadas sensíveis passam pelo backend.
- Sem `dangerouslySetInnerHTML`/`innerHTML` com dado do usuário; sanitizar (DOMPurify) se inevitável; **CSP** estrita com nonce; cookies `HttpOnly` para sessão (nada de token em `localStorage`).
- Mobile: token em Keychain/Keystore (`expo-secure-store`); certificate pinning em app financeiro; ofuscação/ProGuard em release; sem log sensível.
- Dependências auditadas; Renovate semanal.

## Acessibilidade (testada, não só pretendida)
- `jest-axe`/`@axe-core/playwright` nos testes; Testing Library consulta por papel/rótulo (força HTML semântico).
- Teclado completo, foco visível e gerido em modais/rotas, `aria-live` para snackbar, contraste AA, `prefers-reduced-motion`.
- Mobile: TalkBack/VoiceOver nos fluxos principais; alvos conforme o design system e a plataforma; na ausência, ≥ 48 dp; `accessibilityLabel` em ícones.

## Mobile — específico
- **PWA em campo**: IndexedDB para rascunhos/fila e Service Worker para recursos offline, conforme a arquitetura do projeto. Testar limites de armazenamento, expulsão de cache e encerramento do navegador. Não depender exclusivamente de sincronização em segundo plano: oferecer recuperação/reenvio em primeiro plano com recibo e idempotência. Conferir suporte atual em iOS/Android nos dispositivos-alvo antes de prometer operação offline; isso não exige criar app nativo.
- **Expo (RN)** por padrão (EAS Build/Submit/Update, expo-router, TypeScript); **Flutter** quando o time é Dart ou precisa de UI pixel-idêntica; nativo (Compose/SwiftUI) por exigência de plataforma (widgets, watch, hardware).
- Arquitetura: feature-first; MVVM/ViewModel (Compose, SwiftUI) ou hooks + Query (RN); Riverpod/Bloc (Flutter).
- **Offline-first** no campo: armazenamento local por empresa/usuário, fila persistente, idempotência e política de conflito. Distinguir salvo localmente, pendente, rejeitado e aceito conforme vocabulário do projeto; aceite requer recibo do servidor. Testar reinício, perda de rede, reenvio, troca de conta e conflito sem duplicar estoque/custos. Limpar/proteger dados no logout conforme política.
- Deep links / universal links configurados; push (FCM/APNs) com opt-in no momento certo; permissões pedidas just-in-time com explicação.
- Crash reporting (Sentry/Crashlytics), analytics de eventos-chave, feature flags remotas, **OTA updates** (EAS Update) para JS; versionamento semântico + build number automático.
- CI: lint + testes + build de release em todo PR; distribuição interna (TestFlight/Internal testing) automática do trunk; checklist de loja (ícones, splash, capturas, privacidade, política, `NSUsageDescription`, permissões mínimas).
- Testes: unit (lógica), componente (RNTL/widget tests/Compose tests), E2E (Maestro) nos 5–10 fluxos críticos em iOS **e** Android; golden/snapshot para componentes de design system.

## Checklist de tela/componente
- [ ] Feature coesa e lógica testável; sem fragmentação artificial
- [ ] Estado no lugar certo; otimista apenas onde seguro; local/pendente/aceito distintos
- [ ] Estados vazio/carregando/erro/sucesso implementados; error boundary; skeleton
- [ ] Formulário com schema, validação, rascunho e envio explícito quando necessário; teclado/autocomplete corretos
- [ ] Tipos estritos; cliente de API gerado; sem `any`
- [ ] Lighthouse/Web Vitals ou fps dentro do orçamento; bundle não cresceu
- [ ] Acessibilidade com axe passando; teclado/leitor de tela
- [ ] Testes: unit + componente (Testing Library) + E2E se fluxo crítico
- [ ] Claro/escuro, responsivo (compacto/médio/expandido), pt-BR
