import { fileURLToPath } from 'node:url';

import type { NextConfig } from 'next';

const config: NextConfig = {
  // Imagem de implantação (HML): só o que o servidor rastreado precisa, a partir da raiz do monorepo, porque
  // @safrion/db e os outros pacotes do workspace ficam fora da pasta do app.
  output: 'standalone',
  outputFileTracingRoot: fileURLToPath(new URL('../../', import.meta.url)),
  // @safrion/db calcula a pasta das migrações por import.meta.url e usa pg: rodam como pacotes do Node, sem empacotar.
  serverExternalPackages: ['@safrion/db', 'pg'],
  // A F0-c não tem imagem para otimizar; o sharp fica desligado no allowBuilds.
  images: { unoptimized: true },
  poweredByHeader: false,
};

export default config;
