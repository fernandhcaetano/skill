---
name: estilo-trabalho
description: "Estilo Trabalho" — edita vídeos institucionais/de marca do trabalho do usuário (ex.: Oficina, moda masculina): cortes secos sem pausas nem erros, A-roll intercalado com B-roll do ambiente e produtos (~55 %), legenda pequena branca com contorno, centralizada a 77 % da altura, por frase; sem motion graphics nem efeitos. Use quando o usuário pedir um vídeo "do trabalho", "estilo trabalho" ou mandar um briefing de Reels da marca.
---

# Estilo Trabalho

Referência completa com medidas: `estilo-trabalho.md`. Exemplo analisado: `raw/trabalho/exemplo_trabalho.mp4` (não versionado; está no Drive do usuário).

## Entrada
- Vídeo(s) brutos: A-roll (pessoa falando) e, se houver, clipes de B-roll separados. Pegue pelo Drive (veja a skill `editar-video`, passo 0).
- **Briefing** (PDF/texto) com roteiro: use-o como guia do que deve ser dito, da ordem e dos letreiros pedidos (ex.: "números de 1 a 5 com títulos curtos").
- Pergunte ao usuário **o que aproveitar do estilo anterior** (`estilo.md`) antes de montar. Por padrão, nada.

## Passos
1. **Preparar e cortar a fala**: igual à skill `editar-video` (passos 1 e 2: `scripts/prepare.sh`, revisar `raw/chunks.txt`, preencher `KEEP`/`SPLIT`, `scripts/build-edit.py`). Compare a fala com o roteiro do briefing para escolher a tomada certa de cada frase; mantenha a última versão completa. Mostre a lista de cortes ao usuário.
2. **B-roll**: liste os clipes disponíveis com uma prancha de quadros (`ffmpeg ... fps=1,tile`) e associe cada frase do roteiro ao clipe que a ilustra literalmente. Alvo: troca de plano a cada ~2,5 s, B-roll ~55 % do tempo, voz contínua por cima. Sequências de detalhe de produto podem ter planos de ~1 s.
3. **Legenda** (componente próprio, não o `Captions.tsx` do outro estilo): blocos de 3–8 palavras por frase, quebrando em pontuação/pausa; Poppins 500 ~36 px, branco com `-webkit-text-stroke`/contorno preto ~1,5 px, centralizada, `top ≈ 1460 px`, largura máx. ~700 px, caixa normal com pontuação. Sem animação.
4. **Marca**: inclua um plano real do logo/letreiro da marca logo após a abertura, se houver, com ~1,5 s de respiro. Encerramento: a própria fala de despedida ou a CTA do briefing; tela de identidade visual só se o briefing pedir.
5. **Áudio**: só voz, mesma limpeza do `build-edit.py`; sem música, a menos que o usuário peça.
6. Render, conferência (stills, duração, loudness) e envio — igual à skill `editar-video`, passo 4.

## Aprendizados
- (registrar aqui ajustes que o usuário pedir nos vídeos do trabalho)
