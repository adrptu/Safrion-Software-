// ESLint em configuração flat (ENG-008), com regras tipadas do typescript-eslint (ENG-009) e a fronteira do domínio (ENG-012).
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';

const DOMINIO = [
  'packages/domain/src/**/*.ts',
  'packages/domain/src/**/*.mts',
  'packages/domain/src/**/*.cts',
];

export default defineConfig(
  { ignores: ['**/dist/**', 'coverage/**', '.semgrep/**'] },
  { linterOptions: { reportUnusedDisableDirectives: 'error' } },
  js.configs.recommended,
  tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      '@typescript-eslint/ban-ts-comment': [
        'error',
        { 'ts-expect-error': 'allow-with-description', 'ts-ignore': true, 'ts-nocheck': true },
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
        { selector: 'ImportExpression', message: 'ENG-012: import dinâmico não é permitido no domínio.' },
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
    files: ['**/*.js', '**/*.mjs'],
    extends: [tseslint.configs.disableTypeChecked],
    languageOptions: { globals: { process: 'readonly', console: 'readonly', URL: 'readonly' } },
  },
);
