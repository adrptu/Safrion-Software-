// ESLint em configuração flat (ENG-008), com regras tipadas do typescript-eslint (ENG-009) e a fronteira do domínio (ENG-012).
import js from '@eslint/js';
import nextPlugin from '@next/eslint-plugin-next';
import { defineConfig } from 'eslint/config';
import reactHooks from 'eslint-plugin-react-hooks';
import tseslint from 'typescript-eslint';

const DOMINIO = [
  'packages/domain/src/**/*.ts',
  'packages/domain/src/**/*.mts',
  'packages/domain/src/**/*.cts',
];

export default defineConfig(
  {
    ignores: ['**/dist/**', 'coverage/**', '.semgrep/**', '**/.next/**', '**/next-env.d.ts'],
  },
  { linterOptions: { reportUnusedDisableDirectives: 'error' } },
  js.configs.recommended,
  tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': 'allow-with-description',
          'ts-ignore': true,
          'ts-nocheck': true,
        },
      ],
    },
  },
  {
    // ENG-012 e ENG-016: o domínio só importa o que está na lista e não depende de relógio, acaso nem ambiente.
    files: DOMINIO,
    linterOptions: { noInlineConfig: true },
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              regex: '^(?!decimal\\.js$)(?!\\./(?!.*\\.\\./)).*',
              message:
                'ENG-012: o domínio só importa decimal.js e arquivos do próprio src com "./" (sem subir de pasta).',
            },
          ],
        },
      ],
      'no-restricted-syntax': [
        'error',
        {
          selector: 'ImportExpression',
          message: 'ENG-012: import dinâmico não é permitido no domínio.',
        },
        {
          selector: "CallExpression[callee.name='require']",
          message: 'ENG-012: require não é permitido no domínio.',
        },
        {
          selector: "MemberExpression[object.name='Date'][property.name='now']",
          message: 'ENG-016: o domínio recebe a data de fora; não lê o relógio.',
        },
        {
          selector: "NewExpression[callee.name='Date'][arguments.length=0]",
          message: 'ENG-016: o domínio recebe a data de fora; não lê o relógio.',
        },
        {
          selector: "MemberExpression[object.name='Math'][property.name='random']",
          message: 'ENG-016: aleatoriedade entra como dependência controlável, não no domínio.',
        },
        {
          selector: "Identifier[name='process']",
          message: 'ENG-012: o domínio não lê o ambiente do processo.',
        },
      ],
    },
  },
  {
    // Aplicação web (ADR 0004): regras do Next e dos hooks do React. O eslint-config-next não entra: seus plugins de React,
    // import e jsx-a11y ainda não aceitam o ESLint 10; a acessibilidade é conferida com axe nos testes ponta a ponta.
    files: ['apps/web/**/*.{ts,tsx}'],
    extends: [nextPlugin.configs['core-web-vitals'], reactHooks.configs.flat.recommended],
    settings: { next: { rootDir: 'apps/web/' } },
  },
  {
    files: ['**/*.js', '**/*.mjs'],
    extends: [tseslint.configs.disableTypeChecked],
    languageOptions: {
      globals: { process: 'readonly', console: 'readonly', URL: 'readonly' },
    },
  },
  {
    // Templates independentes de aplicação: mantêm lint sintático, sem inventar um projeto TS.
    files: ['docs/parceria/skills/2026-10-14/shared/**/*.{js,ts}'],
    extends: [tseslint.configs.disableTypeChecked],
  },
  {
    // Assets executados no navegador, não no Node do produto.
    files: [
      'docs/parceria/skills/2026-10-14/shared/tabelas-interativas/assets/tabela.js',
      'docs/parceria/skills/2026-10-14/shared/ux-essencial/assets/m3-kit.js',
    ],
    languageOptions: {
      globals: {
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        FormData: 'readonly',
        innerWidth: 'readonly',
        innerHeight: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        requestAnimationFrame: 'readonly',
      },
    },
  },
);
