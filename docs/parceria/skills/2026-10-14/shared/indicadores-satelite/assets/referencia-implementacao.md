# Referência de implementação: cor, contraste, manchas, estado

Exemplos de funções puras, não implementação validada para produção. Conferir nodata, amostra, escala, resolução e limiares contra o SKILL.md e dados conhecidos antes de adaptar. Cores relativas não são diagnóstico; área depende da transformação real do raster. Resoluções do sensor: [Copernicus S2 Mission](https://sentiwiki.copernicus.eu/web/s2-mission).

## Paleta e classes (fonte única)

```ts
export const CLASSES_VIGOR = [
  { id: 1, nome: 'Índice muito baixo', cor: '#E4002B', max: 0.30 },
  { id: 2, nome: 'Fraco',      cor: '#FF6A00', max: 0.45 },
  { id: 3, nome: 'Atenção',    cor: '#FFD500', max: 0.60 },
  { id: 4, nome: 'Médio',      cor: '#B5E61D', max: 0.72 },
  { id: 5, nome: 'Bom',        cor: '#3FBF2A', max: 0.82 },
  { id: 6, nome: 'Vigor alto', cor: '#0B7A1E', max: 1.00 },
] as const;
export const COR_SEM_DADO = '#9E9E9E'; // nuvem, sombra, fora do talhão: hachurado
```

## Escala: absoluta × relativa

```ts
export type Escala = { modo: 'absoluta' | 'relativa'; min: number; max: number };            // valores que viram 0 % e 100 % da rampa

export const escalaAbsoluta: Escala = { modo: 'absoluta', min: 0.30, max: 0.82 }; // limites da classe 1 e 6

/** Estica o contraste ao próprio talhão (ou à fazenda): percentil 2–98 dos pixels válidos. */
export function escalaRelativa(valores: Float32Array, p = [0.02, 0.98], minAmostra = 2): Escala | null {
  const v = Array.from(valores).filter(Number.isFinite).sort((a, b) => a - b);
  if (v.length < Math.max(2, minAmostra)) return null; // sem dado ou amostra insuficiente
  const q = (t: number) => v[Math.min(v.length - 1, Math.floor(t * (v.length - 1)))];
  const min = q(p[0]), max = q(p[1]);
  return max - min < 0.02 ? { modo: 'relativa', min: min - 0.01, max: max + 0.01 } : { modo: 'relativa', min, max }; // talhão uniforme não vira ruído
}
```

`null` significa sem escala/estatística confiável: mostrar “Sem dado” ou “Amostra insuficiente”, sem classificar vigor ou ausência de manchas. O mínimo de 2 no exemplo evita uma amostra única; o mínimo operacional deve ser definido por fonte, resolução e cobertura exigida, sem presumir validade agronômica por atingir esse número.

## Colorização no cliente (rampa contínua, sem suavização espacial)

```ts
const STOPS = CLASSES_VIGOR.map(c => c.cor);   // 6 paradas igualmente espaçadas em t ∈ [0,1]

export function corDoIndice(valor: number, escala: Escala | null): string {
  if (!Number.isFinite(valor) || !escala || !Number.isFinite(escala.min) || !Number.isFinite(escala.max) || escala.max <= escala.min) return COR_SEM_DADO;
  const t = Math.min(1, Math.max(0, (valor - escala.min) / (escala.max - escala.min)));
  const pos = t * (STOPS.length - 1), i = Math.floor(pos), f = pos - i;
  return i >= STOPS.length - 1 ? STOPS[i] : misturaHex(STOPS[i], STOPS[i + 1], f);
}

/** Classe para legenda, tabela e histograma. Absoluto usa os limites configurados; relativo usa seis cortes iguais. A rampa contínua não define a classe. */
export function classeDoIndice(valor: number, escala: Escala | null) {
  if (!Number.isFinite(valor) || !escala || !Number.isFinite(escala.min) || !Number.isFinite(escala.max) || escala.max <= escala.min) return null;
  // Intervalos absolutos com limite superior exclusivo; a última classe inclui o limite final.
  if (escala.modo === 'absoluta') return CLASSES_VIGOR.find(c => valor < c.max) || CLASSES_VIGOR[CLASSES_VIGOR.length - 1];
  const t = (valor - escala.min) / (escala.max - escala.min);
  return CLASSES_VIGOR[Math.min(5, Math.max(0, Math.floor(t * 6)))];
}
```
Renderizar em `<canvas>` pixel a pixel (ImageData) ou tile PNG; CSS `image-rendering: pixelated`. Nunca `bilinear`, nunca `blur`. Opacidade 0.85 na visão da fazenda, 1.0 no detalhe do talhão. Rótulo do talhão: fonte 700, 16–28 px conforme zoom, halo 3 px de contraste, camada acima do raster.

## Estatística e manchas

```ts
export function estatisticas(v: Float32Array, minAmostra = 2) {
  const s = Array.from(v).filter(Number.isFinite).sort((a, b) => a - b);
  if (s.length < Math.max(2, minAmostra)) return null;
  const q = (t: number) => s[Math.floor(t * (s.length - 1))];
  const media = s.reduce((a, b) => a + b, 0) / s.length;
  const dp = Math.sqrt(s.reduce((a, b) => a + (b - media) ** 2, 0) / s.length);
  return { n: s.length, media, mediana: q(0.5), dp, p2: q(0.02), p10: q(0.10), p90: q(0.90), p98: q(0.98) };
}

/** Exemplo conservador: abaixo de ambos os cortes (min), não OU; candidatos a vistoria, sem diagnóstico causal. Validar limiares, nodata e amostra. */
export function mascaraFraco(v: Float32Array, st: ReturnType<typeof estatisticas>) {
  if (!st) return null; // não interpretar falta de estatística como ausência de manchas
  const corte = Math.min(st.media - 1.5 * st.dp, st.p10);
  return Uint8Array.from(v, x => (Number.isFinite(x) && x < corte ? 1 : 0));
}

/** Componentes conexos (8 vizinhos) com área mínima; retorna manchas com área, média e centroide em índice de pixel. */
export function manchas(mask: Uint8Array, v: Float32Array, largura: number, altura: number, minPixels = 3) {
  const rotulo = new Int32Array(mask.length); let n = 0; const out = [];
  for (let i = 0; i < mask.length; i++) {
    if (!mask[i] || rotulo[i]) continue;
    const fila = [i]; rotulo[i] = ++n; const px: number[] = [];
    while (fila.length) {
      const p = fila.pop()!; px.push(p);
      const x = p % largura, y = (p / largura) | 0;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const nx = x + dx, ny = y + dy, q = ny * largura + nx;
        if (nx < 0 || ny < 0 || nx >= largura || ny >= altura || rotulo[q] || !mask[q]) continue;
        rotulo[q] = n; fila.push(q);
      }
    }
    if (px.length < minPixels) continue;
    const media = px.reduce((a, p) => a + v[p], 0) / px.length;
    const cx = px.reduce((a, p) => a + (p % largura), 0) / px.length;
    const cy = px.reduce((a, p) => a + ((p / largura) | 0), 0) / px.length;
    out.push({ pixels: px.length, media, centroide: { x: cx, y: cy }, indices: px });
  }
  return out.sort((a, b) => b.pixels - a.pixels);
}
```
Área em ha = pixels × (resolução m)² / 10 000 (Sentinel-2: 0,01 ha/pixel). Converter centroide para lon/lat pelo geotransform do raster. Excluir 1 pixel de borda do polígono antes da estatística. Pivô: além do centroide, calcular ângulo (setor) e raio (distância ao centro do pivô) da mancha.

## Estado do talhão

Derivados ausentes entram como NaN no exemplo numérico abaixo (não converter null para zero). Estatística insuficiente mantém “Sem dado”; não significa “Normal”.

```ts
export function estadoTalhao(a: { diasDesdeCena: number | null; nuvemPct: number; areaFracaPct: number; quedaPct: number; maiorManchaNovaHa: number }) {
  if (a.diasDesdeCena === null || a.diasDesdeCena > 15) return { estado: 'Sem imagem', acao: 'Buscar imagens' };
  if (!Number.isFinite(a.diasDesdeCena) || a.diasDesdeCena < 0 || !Number.isFinite(a.nuvemPct) || a.nuvemPct < 0 || a.nuvemPct > 100) return { estado: 'Sem dado', acao: 'Ver qualidade da cena' };
  if (a.nuvemPct > 20) return { estado: 'Nuvem', acao: 'Aguardar próxima cena' };
  if (![a.areaFracaPct, a.quedaPct, a.maiorManchaNovaHa].every(Number.isFinite) || a.areaFracaPct < 0 || a.areaFracaPct > 100 || a.maiorManchaNovaHa < 0) return { estado: 'Sem dado', acao: 'Ver qualidade da cena' };
  if (a.areaFracaPct > 15 || a.quedaPct > 15 || a.maiorManchaNovaHa > 1) return { estado: 'Crítico', acao: 'Criar vistoria' };
  if (a.areaFracaPct >= 5 || a.quedaPct >= 10) return { estado: 'Atenção', acao: 'Ver manchas' };
  return { estado: 'Normal', acao: 'Ver histórico' };
}
```

## Casos de teste mínimos
- `corDoIndice(0.30, absoluta)` → `#E4002B`; `corDoIndice(0.82, absoluta)` → `#0B7A1E`; `NaN` → cinza.
- `escalaRelativa` de um talhão com valores 0,84–0,93 devolve min≈0,84 e max≈0,93 (o mapa usa a rampa inteira).
- Raster sintético 10×10 com bloco de 3 px fracos → 1 mancha; bloco de 2 px → 0 manchas; dois blocos separados → 2 manchas.
- `estadoTalhao` cobre também estatística ausente/NaN e amostra insuficiente, sem cair em Normal; Sem imagem e Nuvem preservam a precedência quando seus dados são válidos.
- Mesma cor na legenda e no pixel para um valor dado (snapshot).
