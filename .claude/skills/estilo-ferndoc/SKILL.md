---
name: estilo-ferndoc
description: "Estilo ferndoc" — edita os vídeos do TikTok PESSOAL do Fernando (@ferndoc), inclusive quando a gravação vem em várias partes (celular descarregou, várias tomadas). Decupagem completa antes de editar (repetições, melhor tomada, assuntos repetidos entre partes), cortes secos sem pausas de "pensando", zoom alternado, gancho grande só no começo (Archivo Black) e rótulos pequenos (Bricolage), tudo em branco. Use quando ele mandar vídeo(s) brutos para o TikTok pessoal / ferndoc.
---

# Estilo ferndoc (TikTok pessoal)

Guia completo, referências e histórico das decisões: `estilo-pessoal.md` (leia a seção 6 antes de começar).
Ferramentas: `scripts/ferndoc/decupar.py`, `scripts/ferndoc/montar.py`, `scripts/ferndoc/lettering.py` (fontes em `scripts/ferndoc/fonts/`).
Pré-requisito numa sessão nova: `pip install faster-whisper` (modelo baixa do huggingface.co).

## Regra de ouro
**Profissional, no nível das referências.** E **nada de renderizar antes de bater a decupagem com ele** ("não fique fazendo o vídeo, vamos bater tudo antes").
Prévias em foto (quadros) são bem-vindas; vídeo só depois da aprovação.

## 0. Receber os brutos
- Vêm do Drive (pasta ou arquivos). Baixe cada um com
  `curl -L -o raw/ferndoc/parteN.mov "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
- **Várias partes = mesma gravação** (ex.: o celular descarregou 2× → 3 vídeos). Ordene pelo horário de gravação
  (`ffprobe -show_entries format_tags=creation_time`) e confirme a ordem com ele se houver dúvida.
- Prancha de quadros de cada parte (`ffmpeg -vf fps=1/3,scale=150:-1,tile=...`) para ver enquadramento, luz e cenário.

## 1. Decupar (o passo mais importante)
`python3 -I scripts/ferndoc/decupar.py raw/ferndoc/parte1.mov raw/ferndoc/parte2.mov ...`
→ `raw/ferndoc/chunks.txt`: trechos de fala `parte.trecho [ini-fim] texto` (divididos nas pausas, com limiar adaptado ao ruído do ambiente;
cada trecho transcrito isolado para que repetições não sejam "limpas") + seção **FRASES REPETIDAS** agrupando a mesma frase dita mais de uma vez.

Leia TUDO e monte um **relatório de decupagem** para ele, antes de qualquer render:
1. **Repetições / novas tentativas**: em cada grupo, escolha a melhor tomada — completa, sem tropeço, com mais energia e boa dicção.
   Na dúvida, a última completa. Diga qual ficou e por quê.
2. **Assunto repetido entre partes**: depois de cada recomeço (bateria), ele tende a reintroduzir o tema ou repetir uma explicação.
   Mantenha uma só vez, no lugar que faz mais sentido na história.
3. **Pausas de "pensando"**, "é…", "hum", "tipo", respirações longas, falsas largadas: tudo sai (corte seco). Não pode sobrar espaço sem fala.
4. **Estrutura**: o vídeo tem que abrir com o gancho nos primeiros 1–3 s (se a melhor frase de gancho estiver no meio, traga para o começo),
   seguir uma linha clara e fechar com CTA/fecho curto. Aponte o que **dá para melhorar** (gancho fraco, trecho longo demais,
   informação que falta, ordem melhor) — como um editor, não só um cortador.
5. Liste nomes próprios/palavras duvidosas da transcrição para ele confirmar (ex.: "Linha Amarela", "pedágio", "Sodexo?").

Formato do relatório: tabela curta "fica / sai / por quê" + duração estimada + sugestões. Espere o OK.

## 2. Montar (só depois do OK)
1. Escreva `raw/ferndoc/corte.json` com os trechos na ordem final (ajustes finos com `ini`/`fim` em segundos da fonte;
   use os tempos das palavras em `raw/ferndoc/chunks.json`). O script encaixa cada corte no ponto mais silencioso (±120 ms),
   aplica micro-fades, tonemap HDR→SDR quando precisa e **alterna zoom 1.00/1.12** entre cortes da mesma parte (disfarça o jump cut).
2. Rode sem lettering primeiro para gerar `raw/ferndoc/palavras_final.json` (palavras no tempo final) — ou calcule pelos trechos.
3. Escreva `raw/ferndoc/lettering.json` (formato no topo de `lettering.py`) e rode:
   `python3 -I scripts/ferndoc/montar.py raw/ferndoc/corte.json out/ferndoc_vN.mp4 raw/ferndoc/parte1.mov ...`
   Áudio sai em −14 LUFS (highpass 80 Hz + compressor 3:1).

## 3. Lettering (decisões dele, 06/11/2026)
- **Tudo branco** `#FFFFFF`, sombra suave, sem caixa de fundo, sem contorno. Sem cor de destaque.
- **Gancho (só nos primeiros segundos)**: frase de apoio em **Bricolage Grotesque 500** minúscula (~54 px) + palavras-chave em
  **Archivo Black** CAIXA ALTA (~112 px), entrando palavra por palavra no tempo da fala. **Letra grande só aqui.**
- **Resto do vídeo**: só **rótulos pequenos** em Bricolage minúscula: lugar, preço, item, reação ("(fiz errado)"), frase-chave curta.
  1–2 linhas, poucos (um a cada ~4–6 s no máximo), sem legenda corrida (legenda palavra a palavra ainda em aberto — pergunte).
- Posição: espaço vazio, **nunca sobre o rosto**; fora das zonas de UI do TikTok (topo < 150 px, base > ~1550 px, lateral direita ~120 px).
  Confira em quadros reais de cada trecho antes do render final.

## 4. Cenário e gravação
Estático: parede de **madeira clara** + **cortina preta** (foto em `estilo-pessoal.md`). Texto deve cair sobre a cortina ou sobre ele, não na madeira
(perde contraste). Sugestões já dadas: quina na diagonal (madeira só em ~1/3 lateral), luz quente rasante na cortina, objeto-assinatura no quadro.

## 5. Som
- **Efeitos sonoros: do CapCut/TikTok**, enviados por ele (pasta no Drive) → banco em `public/sfx/ferndoc/`. **Nunca sintetizados** (soaram artificiais).
  Poucos, só em ênfase (2–4 por vídeo). Até o banco existir, sem efeitos.
- Música de fundo: decidir depois (ainda não).

## 6. Revisar e entregar
Quadros de conferência (gancho, cada rótulo, cortes com zoom), duração, loudness (`-af ebur128` → I ≈ −14 LUFS), sincronia labial nos cortes.
Envie o vídeo + a lista do que foi cortado. Registre aqui ou em `estilo-pessoal.md` tudo que ele aprovar ou corrigir.

## Aprendizados
- 1ª tentativa (sushi, 04/11): caixa branca + whoosh em todo corte = "péssimo". Nunca repetir.
