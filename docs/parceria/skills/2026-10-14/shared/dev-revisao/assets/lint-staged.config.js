// Pre-commit: só nos arquivos alterados, rápido. Instalação: npx husky init && echo "npx lint-staged" > .husky/pre-commit
export default {
  '*.{ts,tsx,js,jsx}': ['prettier --write', 'eslint --fix --max-warnings=0', () => 'tsc --noEmit -p tsconfig.json', 'vitest related --run'],
  '*.{json,md,yml,yaml,css}': ['prettier --write'],
  '*.py': ['ruff format', 'ruff check --fix', () => 'mypy .'],
  '*': ['gitleaks protect --staged --no-banner'],
};
