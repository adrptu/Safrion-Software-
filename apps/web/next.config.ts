import type { NextConfig } from 'next';

const config: NextConfig = {
  // @safrion/db calcula a pasta das migrações por import.meta.url e usa pg: rodam como pacotes do Node, sem empacotar.
  serverExternalPackages: ['@safrion/db', 'pg'],
  // A F0-c não tem imagem para otimizar; o sharp fica desligado no allowBuilds.
  images: { unoptimized: true },
  poweredByHeader: false,
};

export default config;
