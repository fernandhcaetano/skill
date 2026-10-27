# estilo.md — referência: `@robles.ia` "vídeo editado con IA" (46,8 s)

Fonte analisada: 576×1024, 30 fps, AAC 44,1 kHz. Valores convertidos para **1080×1920 @ 30 fps** (fator ×1,875).
Itens marcados com [SUPOSIÇÃO] foram estimados visualmente, não medidos.

## 1. Estrutura e ritmo de cortes
- Duração total 46,8 s; fala ocupa 0–42,5 s; **end card de 4,3 s** (42,5–46,8 s).
- Cortes de plano detectados (s): 2,4 · 5,4 · 6,8 · 10,4 · 12,5 · 23,3 · 24,1 · 27,0 · 29,4 · 32,1 · 37,6 · 38,8 · 41,9 → **troca a cada ~3,3 s em média** (mín. 0,8 s, máx. 10,8 s no bloco do prompt).
- Alterna dois modos de tela:
  - **A-roll (talking head)** ≈ 45 % do tempo: câmera frontal, rosto centralizado, corte seco, sem zoom aparente [SUPOSIÇÃO: zoom ≤ 3 %].
  - **Tela de motion graphics** ≈ 55 %: o rosto some e a fala continua em off sobre um fundo claro com elementos animados.
- Silêncios: praticamente nenhum pausa > 0,25 s (apenas 1 de 0,6 s) → **cortar todo silêncio > 0,3 s**.

## 2. Legendas (palavra por palavra)
- Posição: **topo**, centralizada; bloco começa em y ≈ 160 px e termina em y ≈ 330 px (8–17 % da altura).
- Estrutura em 2 níveis por bloco:
  - **Linha pequena** (palavras de apoio): ~48 px, peso 600, preta `#111111` sobre fundo claro / branca `#FFFFFF` sobre vídeo.
  - **Palavra destaque** (1 palavra-chave por bloco): ~105 px, peso 800, tracking levemente negativo (−2 %).
    - Sobre fundo claro: azul `#0053FF`.
    - Sobre vídeo: branca `#FFFFFF` com sombra suave (0 4 20 rgba(0,0,0,.35)).
  - Às vezes uma 3ª linha pequena abaixo do destaque (ex.: "con IA", "etcétera,") ~40 px.
- Fonte: sans geométrica arredondada com "t" característico [SUPOSIÇÃO: **Gilroy / Satoshi**; substituto livre: **Plus Jakarta Sans** ou **Outfit** ExtraBold].
- **Palavras por bloco**: 1–4 na linha pequena + 1 destaque; bloco dura 0,5–1,5 s.
- Animação de entrada por palavra: aparece com **blur 12 px → 0 + opacidade 0 → 1 + sobe 10 px**, ~6 frames (0,2 s), easing out.
- Palavras ainda não ditas ficam **cinza claro 25 % de opacidade** e "acendem" quando faladas (karaokê) — visível em "con un ~~estilo~~", "por el ~~prompt~~".
- Saída do bloco: blur + fade out, ~5 frames.

## 3. Telas de motion graphics (b-roll)
- Fundo: quase branco `#FAFAFD` com **gradiente radial azul-lavanda** `#D2DFFD` vindo dos cantos superior-direito e inferior-esquerdo (opacidade ~60 %).
- Elementos: cards brancos com raio 24–32 px e sombra suave (0 20 60 rgba(30,60,140,.12)); mockups de celular com borda preta 8 px e raio ~48 px; chips/pills pretas com texto mono branco (ex.: `• VÍDEO 2 · EDITADO CON IA`).
- Fonte secundária: **monoespaçada** (~22 px, tracking +5 %) para rótulos técnicos (`referencia.mp4`, `estilo.md`, `SKILL.md`) [SUPOSIÇÃO: JetBrains Mono / IBM Plex Mono].
- Ícone/acento laranja `#E8603C` (asterisco do Claude) usado com moderação.
- Cada elemento ilustra literalmente a frase falada (lista "1 · 2", checklist que vai marcando, cards v1/v2/v3, diagrama SKILL → vídeos).
- Animações: entrada com **spring** (scale 0,9 → 1 + fade, ~12 frames), itens de lista em **stagger de 4–6 frames**, checkboxes marcando no momento da palavra.
- Legenda nessas telas vai **embaixo** (y ≈ 1100–1300 px, ~57–68 %), mesmo estilo de 2 níveis.

## 4. Transições
- A-roll ↔ motion: **corte seco** na maioria.
- Entre telas de motion: elementos saem com blur/fade enquanto os novos entram (cross de ~8 frames).
- Abertura: 3 cards de "vídeo exemplo" em sequência rápida (0–2,5 s) como gancho visual.

## 5. Cor do vídeo (A-roll)
- Gradação neutra, levemente quente, contraste médio; sem LUT forte [SUPOSIÇÃO].

## 6. Elementos fixos
- Marca d'água TikTok + `@robles.ia` (da plataforma — **não replicar**; substituir pelo seu @ se quiser).
- End card 4,3 s: fundo `#12121C`, logo + barra de busca com o @ (estilo TikTok glitch).

## 7. Som
- Voz limpa, sem música de fundo audível [SUPOSIÇÃO: música ≤ −30 dB ou ausente].
- Sem efeitos sonoros perceptíveis nas transições [SUPOSIÇÃO].

## 8. Personalização (preencher conforme sua marca)
- Cor de destaque: `#0053FF` → _____
- Fonte principal: Plus Jakarta Sans ExtraBold → _____
- @ no end card: _____
