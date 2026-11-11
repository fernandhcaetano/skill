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
- **Efeitos sonoros: do CapCut/TikTok**, gravados por ele **uma única vez** (gravação de tela do CapCut tocando as prévias; pasta
  "Efeito Sonoros" dentro da pasta dos vídeos no Drive). Recortar cada som e **versionar no repo** em `public/sfx/ferndoc/<categoria>/<nome>.wav`
  + `public/sfx/ferndoc/catalogo.md` (nome no CapCut, categoria, duração, uso). Ele não vai gravar de novo: nunca apagar esse banco.
  **Nunca sintetizados** (soaram artificiais).
- **O banco é um cardápio, não uma lista para usar tudo.** Cada som tem uma função, como nas referências estudadas:
  | Som | Quando usar |
  |---|---|
  | Teclado/digitação | texto sendo **digitado** na tela (letra por letra) — o som acompanha a animação |
  | Clique (mouse) | algo **aparece** na tela: foto, imagem, cartela, rótulo importante; ou **troca de vídeo/cena** marcante |
  | Whoosh/transição | troca de assunto/bloco, entrada de cartela em tela cheia (não em todo corte) |
  | Pop | entrada pontual de um elemento pequeno (sticker, emoji, número) |
  | Ding/brilho | revelação, preço, "olha isso" |
  | Boom/impacto grave | gancho forte ou virada (no máx. 1 por vídeo) |
  Som sempre **motivado por algo que acontece na imagem**. Cortes comuns de fala (jump cuts) ficam **sem** som. Voz sempre na frente
  (efeitos ~8–12 dB abaixo do pico da voz). Liste no relatório de decupagem onde cada efeito vai entrar.
- Música de fundo: decidir depois (ainda não).

## 6. Revisar e entregar
Quadros de conferência (gancho, cada rótulo, cortes com zoom), duração, loudness (`-af ebur128` → I ≈ −14 LUFS), sincronia labial nos cortes.
Envie o vídeo + a lista do que foi cortado. Registre aqui ou em `estilo-pessoal.md` tudo que ele aprovar ou corrigir.

## Aprendizados
- **Gancho novo (11/11, Welcome)**: ele quer o gancho **estático**, curto e forte, estilo TikTok: palavras-chave em **Anton branca com
  contorno preto** (`["SALE", 0, "A130"]` no lettering), 2 linhas centralizadas em y≈395, acima da cabeça, sem animação, até o
  1º corte. **Sem emoji** nos textos. Vídeo que ele já manda editado (voz + B-roll): manter os cortes dele (1 trecho só, sem
  apertar.py), só lettering + efeitos; clique em cada peça no provador, swish nas mudanças de ambiente, coro no desconto.
- **Altura do texto (09/11)**: rótulos e gancho em **y = 270** (logo abaixo das abas Seguindo/Para você do TikTok, como a referência
  que ele mandou). y 200 ficava "nas barras". Prévia: `preview-posicao-topo.jpg`. (Opção "embaixo" y≈1400 foi sugerida p/ venda,
  ele preferiu o topo.)
- **Respiro final (09/11, Renner v5)**: "diminuir só um pouquinho" → padrão do apertar.py = pausas ≥ 0,4 s saem; folga 0,12 antes /
  0,20 depois; palavra final + 0,25 s. Cuidado: NÃO interromper montagem com REUSE=1 (trecho fica pela metade) — montar.py agora
  confere a duração antes de reaproveitar. Transcrever o resultado em blocos de 8 s (a transcrição corrida pula trechos).
- **Renner v4 (09/11) — regra de corte**: NADA de fundido/transição ("não quero efeito de transição"): `transicao` padrão = 0.
  O que ele quer é **respiro**: todo corte termina ≥ 0,35 s depois da última palavra (apertar.py garante pelas palavras) e começa
  ≥ 0,12 s antes da primeira. Se dois cortes ficam a < 0,15 s um do outro, juntar num trecho contínuo (sem corte). Frase seguida de
  ação (ex.: vestir a jaqueta) = deixar contínuo, não pular para o meio da ação.
- **Ritmo (09/11, Renner v3)**: "zero silêncio" com folga mínima ficou SECO demais. Equilíbrio aprovado em teste: `apertar.py`
  com padrões novos = só tira pausas ≥ 0,5 s, mantém 0,12 s antes e **0,28 s de respiro depois** de cada frase, + fundido 0,16 s.
  Suspiro/leitura longa continuam saindo (são > 0,5 s).
- **Renner (09/11)**: ele achou os cortes "muito secos" → `montar.py` agora faz **fundido de 0,16 s** (imagem + som) em todo corte
  (`"transicao"` no corte.json; 0 = seco). Pediu **um pouco mais claro**: npl 240 nesse vídeo (280 = calibrado do print; menor =
  mais claro). Foto em tela cheia: recortar 9:16 centrado nele (conferir o tamanho real do arquivo!), ~1,6 s, zoom leve.
- **"Trava" (09/11)**: fragmento de fala < 0,6 s entre dois cortes ("E eu", "O", "mas gente") parece travamento. `apertar.py` agora
  junta esses pedaços com o vizinho ou avisa; depois de montar, listar os trechos (< 0,6 s = problema) e conferir que nenhum corte
  começa no meio de palavra (ex.: "…u não tô" — puxar o início para a palavra inteira).
- **Regra (08/11): ZERO silêncio.** Ele quer fora todo suspiro/respiração e toda cena olhando o iPad/lendo sem falar. Depois de
  montar a lista de cortes, SEMPRE rodar `scripts/ferndoc/apertar.py raw/ferndoc/corte.json` (parte os trechos em todo intervalo sem
  voz ≥ 0,25 s) e conferir pela transcrição que nenhuma palavra sumiu. Recalcular os tempos do lettering pelas palavras depois.
- **Intolerância (08/11, opinião/sério)**: tom sério = quase sem efeito (só clique na cartela da manchete), sem coro/teclado/swish.
  Print de manchete vira cartela off-white em tela cheia (3 s) via `{"clipe": cartela.mp4}`. Como editor, sinalizar falas que acusam
  pessoa real identificável e dúvidas factuais (cargo/nome) e deixar ele decidir (ele cortou a acusação; Ana Elisa Santos = deputada
  federal PT-MG). Título longo no gancho: `"G88"` no lettering (tamanho próprio).
- **COR DEFINITIVA (08/11, aprovada: "Perfeito")**: SDR "sem mexer" = conversão HDR->SDR **calibrada pelo print da galeria do iPhone**: hable com
  **npl=280**, sem nenhum ajuste (`"cor": "neutra"`, `"npl": 280` = padrão do montar.py). npl=100 (antes) deixava a pele ~25 % mais
  clara que no iPhone = "estourado"/"cara de tratamento". Se um vídeo novo parecer diferente, pedir 1 print da galeria e recalibrar
  o npl comparando madeira/cortina/pele (script em raw/ferndoc/goldengoose/calib).
- **COR (08/11)**: o modo `"cor": "original"` (HDR mantido) foi REJEITADO ("parece que o HDR está ativado"). Padrão = **`"cor": "neutra"`**
  (igual à Anitta v2: só hable npl=100, sem ajuste). Modo original, se um dia precisar: mantém o HDR (HLG) do iPhone,
  HEVC 10 bits (hvc1), igual à galeria; texto em cinza 191 (branco de referência HLG). Limitação: clipes SDR em tela cheia ainda não
  são aceitos nesse modo (converter o clipe para HLG antes, se precisar). Prévias de quadro para mim: converter só na hora de olhar.
- **Golden Goose True-Star (08/11)**: escreve-se **True-Star** (com hífen) e Ball Star. Sem tratamento de cor. `aparar.py` NÃO serve
  para cenas de ação sem fala (encurta/zera) nem para falas baixas ("Gostei!", "Bora") — use só em trechos de fala e confira; na
  dúvida, cortes manuais pela palavra + checar energia. Ações longas (calçar/amarrar) viram 1,5–2 s. Planos fechados em pé: sem rótulo
  no topo (bate na cabeça).
- **Top 5 Anitta / Equilibrivm I (06/11)**: ranking com clipes em TELA CHEIA 9:16 depois de cada nome (`{"clipe":..., "enquadre":[[t,cx,zoom,cy]...]}`
  no corte.json, um item por plano). Pedidos dele: clipe só no top 5 (menções sem clipe), **~5 s** por clipe, sempre no **refrão**;
  se a Anitta não aparece no refrão, ainda assim usar o refrão (ele preferiu as dançarinas do refrão de Desgraça ao gancho com close
  dela). Achar refrão: transcrever a música e ver a linha que repete; planos: `shots.py`/diferença de quadros; rosto: marcar à mão
  (Haar falha em clipe escuro). **Tirar suspiros**: rodar `scripts/ferndoc/aparar.py` no corte.json (voz 55–60 dB acima do piso;
  suspiro até ~26) e conferir palavras curtas do início ("Rankeando", "do") que ele pode comer. Nesse vídeo ele pediu **sem tratamento
  de cor** (`"cor": "neutra"`), mantendo efeitos sonoros, animação do texto e zoom.
- **Cor (06/11)**: bug sério corrigido no `montar.py` — o ffprobe devolve `arib-std-b67,` (vírgula extra, Dolby Vision) e a
  detecção de HDR falhava: v1/v2 saíram com HLG cru → "pálido, amarelado, cara de HDR". Também faltava etiquetar os trechos como bt709.
  Sempre conferir no `.tag` do trecho (`raw/ferndoc/segs/sNNN.mov.tag`) que a conversão entrou e comparar 1 quadro com a prévia aprovada.
  Look aprovado: opção "2 menos amarelo". Recomendação dada: desligar Vídeo HDR no iPhone (Ajustes → Câmera → Gravar Vídeo).
- **Mondepars v1 aprovado ("ficou TUDO!")** — só pediu tirar a cara de HDR ("a cor fica estranha"). Conversão HDR→SDR do iPhone
  agora é hable npl=100 + gama 1.12 (em `montar.py`); a antiga (mobius npl=203) saturava e alaranjava a pele.
- **Mondepars (06/11, 3 partes, 5min05 → 1min37)**: celular grava a frontal **espelhada** (texto da sacola invertido) — ele prefere **deixar como está**.
  Abertura testada: cold open de 2,6 s com o item mais curioso já vestido ("essa gravata, espetacular") antes do "bora ver o que eu comprei".
  Ele esqueceu a palavra "acervo" na fala → virou rótulo digitado "pro meu acervo" + som de teclado. Emendas entre partes ("eu tinha ficado
  sem memória, continuando", "como eu estava falando") sempre saem. Rótulos no topo (y≈210) batem na cabeça em planos em pé/close:
  conferir cada um e descer para o peito (y 900–1450) quando precisar. Montagem por trechos (`montar.py`, `REUSE=1` reaproveita).
- 1ª tentativa (sushi, 04/11): caixa branca + whoosh em todo corte = "péssimo". Nunca repetir.
