# Projeto Black Friday nos CDs (vídeos da Luísa / entrevistas)

Combinado com o usuário (24/11/2026):
- **Só legenda + corte do início** (tirar silêncio/fala antes da primeira frase e silêncio no fim). Nada de efeitos.
- **Marcas e logos podem aparecer** — não esconder mais (sem recorte nem apagar painéis).
- Dividir em 2 só se o vídeo for grande (~50 s): cortar numa pausa natural / troca de pergunta.
- Conferir com o usuário nomes que a transcrição pode errar (ex.: Michele, Braulio, Isaque).

## Cor "F" (iPhone HDR → SDR, um pouco mais claro que o original)
```
zscale=w=1080:h=1920:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,
zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=0.97:saturation=1.05:contrast=1.12,fps=30
```

## Legenda pequena (ASS, 1080×1920)
`Style: Leg,Inter Medium,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,190,190,420,1`
Frases curtas (3–8 palavras), separadas à mão em pontos naturais; tempos das palavras do whisper.cpp (`-ml 1 -sow -ojf`).
Atenção: o Whisper inventa frases em trechos de silêncio no fim — conferir com a energia do áudio.

## Áudio
`acompressor=threshold=-24dB:ratio=4:attack=5:release=120:makeup=3,alimiter=limit=0.89:level=false,loudnorm=I=-10:TP=-1.0:LRA=7`, 48 kHz, AAC 192k.
