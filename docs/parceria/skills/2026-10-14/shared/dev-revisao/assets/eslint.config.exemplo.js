// ESLint flat config — TypeScript estrito com verificação de tipos.
// npm i -D eslint typescript-eslint eslint-plugin-sonarjs eslint-plugin-unicorn eslint-plugin-import-x eslint-config-prettier
// React: + eslint-plugin-react-hooks eslint-plugin-jsx-a11y
import tseslint from 'typescript-eslint';
import sonarjs from 'eslint-plugin-sonarjs';
import unicorn from 'eslint-plugin-unicorn';
import importX from 'eslint-plugin-import-x';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**', '.next/**'] },
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  sonarjs.configs.recommended,
  unicorn.configs.recommended,
  importX.flatConfigs.recommended,
  importX.flatConfigs.typescript,
  {
    languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } },
    rules: {
      // Erros e tipos
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-non-null-assertion': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      '@typescript-eslint/ban-ts-comment': ['error', { 'ts-expect-error': 'allow-with-description', minimumDescriptionLength: 10 }],
      'no-console': ['error', { allow: ['warn', 'error'] }],
      'no-empty': ['error', { allowEmptyCatch: false }],
      // Tamanho e complexidade
      complexity: ['error', 10],
      'max-depth': ['error', 3],
      'max-lines-per-function': ['warn', { max: 60, skipBlankLines: true, skipComments: true }],
      'max-params': ['error', 3],
      'no-magic-numbers': ['warn', { ignore: [-1, 0, 1, 2, 100, 1000], ignoreArrayIndexes: true, enforceConst: true, detectObjects: false }],
      'sonarjs/cognitive-complexity': ['error', 15],
      'sonarjs/no-duplicate-string': ['warn', { threshold: 4 }],
      // Imports
      'import-x/no-cycle': 'error',
      'import-x/no-unused-modules': 'off', // usar knip
      'import-x/order': ['error', { 'newlines-between': 'always', alphabetize: { order: 'asc' } }],
      // Unicorn: regras que atrapalham mais do que ajudam
      'unicorn/prevent-abbreviations': 'off',
      'unicorn/filename-case': ['error', { cases: { kebabCase: true, pascalCase: true } }],
      'unicorn/no-null': 'off',
      'unicorn/no-array-reduce': 'off',
    },
  },
  {
    files: ['**/*.{test,spec}.{ts,tsx}', 'e2e/**'],
    rules: { 'max-lines-per-function': 'off', 'no-magic-numbers': 'off', 'sonarjs/no-duplicate-string': 'off', '@typescript-eslint/no-non-null-assertion': 'off' },
  },
  prettier,
);
