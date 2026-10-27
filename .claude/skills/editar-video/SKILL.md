---
name: editar-video
description: Edita um vídeo vertical de "falando para a câmera" em português no estilo do estilo.md (cortes secos sem pausas nem erros, áudio limpo, legendas palavra por palavra no topo com palavra-destaque azul, zooms alternados e telas de motion graphics que ilustram a fala). Use quando o usuário mandar um vídeo bruto para editar.
---

# Editar vídeo no estilo aprovado

Projeto Remotion em `/home/user/my-video` (1080×1920, 30 fps). Referência visual: `estilo.md`.
Primeira versão aprovada pelo usuário: vídeo político de 3:08 → 1:51 (`out/edit_v1.mp4`).

## 0. Pré-requisitos
- `whisper.cpp/main` e `whisper.cpp/ggml-medium.bin` (se faltar: `node scripts/install-whisper.mjs`; o modelo vem de huggingface.co, que precisa estar liberado na rede).
- Vídeo grande do Google Drive: `curl -L -o raw/X.MOV "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"` (arquivo compartilhado "qualquer pessoa com o link"; domínios drive.google.com e drive.usercontent.google.com liberados).

## 1. Preparar
`bash scripts/prepare.sh raw/X.MOV` → gera `public/video_proxy.mp4`, `raw/audio*.wav`, `raw/segs.json`, transcrição por trecho em `raw/chunks/` e a lista `raw/chunks.txt`.

## 2. Decidir os cortes (o passo que mais importa)
Leia `raw/chunks.txt` inteiro com atenção — o usuário erra e se corrige com frequência.
- **Corte** o começo antes da primeira frase real, ruídos/trechos vazios, barulhos no fim (ex.: som de ligação).
- **Falsas largadas e repetições**: quando a mesma ideia aparece em vários trechos seguidos, mantenha **só a última versão completa** (ex.: 3× "Essas eleições…", 5× "eu acho que a gente tem que ensinar…").
- **Correções dentro de um trecho** ("pra ano que vem, não, né? daqui a quatro anos"): use `SPLIT` em `scripts/build-edit.py` com os tempos das palavras de `raw/chunks/cNNN.wav.json` (o script encaixa cada corte no ponto mais silencioso ±150 ms).
- Trechos curtos sem texto entre duas frases da mesma ideia podem ser palavras curtas ("e de novo", "disso") — na dúvida, mantenha.
- Preencha `KEEP` e `SPLIT` em `scripts/build-edit.py`; ajuste `FIXES`/`PROPER` para erros de transcrição e nomes próprios.
- **Mostre ao usuário a lista do que foi cortado** e qualquer nome/palavra duvidosa do Whisper antes de renderizar a versão final.

`python3 -I scripts/build-edit.py` → gera `src/edit.json` (cortes + palavras no tempo final) e `public/voice.wav` (micro-fades, highpass 80 Hz, afftdn, compressor 3:1, loudnorm −14 LUFS).

## 3. Visual
- `src/Edit/Captions.tsx`: blocos de ≤4 palavras (quebra em pontuação ou pausa > 0,3 s); palavra-destaque = primeira em `KEYWORDS`, senão a mais longa. Atualize `KEYWORDS` com as palavras fortes do novo tema. Topo sobre o vídeo, embaixo (y 1130) sobre telas claras.
- `src/Edit/Main.tsx`: zoom alterna 1.00 / 1.14 / 1.06 / 1.18 por corte + push-in de 3 % por plano, origem 50 % 42 % (rosto).
- `src/Edit/Scenes.tsx`: **reescreva o array `scenes` para cada vídeo** — 6 a 8 telas de 2–5 s, cada uma ancorada em frases da transcrição com `sc("frase início", "frase fim", …)`. Ilustre literalmente o que é dito (cards, pills pretas com texto mono, checklists que marcam na hora da palavra, números grandes). Nada de dados inventados — só o que a pessoa fala.
- Cores/fontes em `src/Edit/theme.ts` (azul `#0053FF`, laranja `#E8603C`, Plus Jakarta Sans + JetBrains Mono via @fontsource).

## 4. Revisar e renderizar
1. `npx tsc --noEmit`
2. Stills de conferência: `npx remotion still Edit out.png --frame=N --browser-executable=/opt/pw-browsers/chromium --scale=0.4` em 5–6 momentos (legenda sobre vídeo, cada tela animada). Confira sobreposições e legibilidade.
3. `npx remotion render Edit out/edit_vN.mp4 --browser-executable=/opt/pw-browsers/chromium --concurrency=4 --crf=20` (≈15 min para 2 min de vídeo; rode em background).
4. Verifique duração e loudness (`ffmpeg -i out/... -af ebur128 -f null -` → I ≈ −14 LUFS) e envie o arquivo ao usuário.

## 5. Aprendizados
Quando o usuário aprovar ou corrigir algo, registre aqui ou no `estilo.md` para os próximos vídeos.
- v1 aprovada sem ajustes.
