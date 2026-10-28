"""Reserva 1P5P: legendas e planos ancorados no tempo da FALA ORIGINAL (raw/1p5p/fala.mov).

Assim, se os cortes mudarem (build-edit.py), basta rodar de novo:
  python3 -I scripts/build-edit.py && python3 -I scripts/plan-1p5p.py
Gera src/Trabalho/plan-1p5p.json (cortes + legendas + planos no tempo final).
"""
import json

edit = json.load(open("src/Trabalho/edit-1p5p.json"))
S = edit["segments"]


def out(t):
    """Tempo da fonte -> tempo no vídeo final. Dentro de um corte, vai para o próximo trecho."""
    for s in S:
        if s["srcStart"] - 1e-6 <= t <= s["srcEnd"] + 1e-6:
            return round(s["outStart"] + t - s["srcStart"], 3)
    nxt = [s for s in S if s["srcStart"] > t]
    return nxt[0]["outStart"] if nxt else edit["duration"]


# (início, fim, texto) em segundos da fonte. Por frase, 3–8 palavras.
CAPTIONS = [
    (1.51, 3.20, "Você sabia que a cada peça"),
    (3.20, 4.50, "que você compra na Reserva,"),
    (4.55, 6.07, "cinco pratos são complementados?"),
    (6.43, 8.10, "Sim, esse é o 1P5P,"),
    (8.36, 10.20, "um projeto que há 10 anos"),
    (10.25, 12.25, "providencia complementação alimentar"),
    (12.29, 12.95, "para quem precisa."),
    (13.21, 14.90, "E esse ano, ele completa 10 anos."),
    (17.07, 18.62, "Oi, eu sou a Ludy,"),
    (18.67, 21.0, "do time de Sustentabilidade do grupo."),
    (21.30, 23.05, "Hoje estamos aqui para celebrar"),
    (23.05, 24.97, "o Dia Mundial da Alimentação"),
    (25.11, 26.45, "e trouxemos pessoas"),
    (26.45, 28.07, "de diferentes áreas da marca"),
    (28.33, 29.63, "para poder vivenciar"),
    (30.0, 31.30, "esse projeto na prática."),
    (31.38, 33.07, "Estamos aqui na Escola DOM"),
    (33.43, 36.07, "e, junto com times de sede, CD e marca,"),
    (36.23, 38.83, "vamos experienciar essa iniciativa na prática."),
    (40.4, 41.8, "Foi um dia de muita troca,"),
    (41.8, 43.2, "aprendizado e celebração."),
    (43.47, 45.05, "Junto com a chefe Neide Marco,"),
    (45.05, 46.93, "já parceira de longo prazo do projeto,"),
    (47.27, 48.70, "as crianças participaram"),
    (48.70, 49.8, "de uma oficina de cupcakes"),
    (50.03, 51.45, "e puderam mostrar um pouco mais"),
    (51.45, 52.87, "da escola para o nosso time."),
    (54.77, 56.6, "Isso reforça a importância"),
    (56.6, 58.6, "do aproveitamento alimentar."),
    (59.07, 61.6, "E também podemos, nessa troca, trazer"),
    (61.83, 63.5, "o nosso encantamento para a escola,"),
    (63.5, 64.5, "com a presença do Rê,"),
    (64.7, 65.67, "nosso mascote,"),
    (65.83, 66.93, "que celebrou com a gente"),
    (67.2, 68.33, "esse momento tão importante."),
    (70.17, 71.65, "Celebrar 10 anos é reconhecer"),
    (71.65, 72.97, "que cada prato importa"),
    (73.37, 74.7, "e que seguimos juntos,"),
    (74.9, 76.3, "fortalecendo essa rede,"),
    (76.3, 77.8, "que trabalha para complementar"),
    (78.0, 79.4, "a alimentação de quem precisa."),
]

# (tempo na fonte onde o plano começa, clipe ou None = A-roll, ponto de entrada no clipe[, velocidade])
# 15.4 = fim do trecho 3 (com END_EXTRA).
SHOTS = [
    (1.47, None, 0),  # "Você sabia que a cada peça…"
    (15.4, "IMG_4691", 0.2),  # parede "Gente boa e do bem", já com "Oi, eu sou a Ludy" por cima
    (18.67, "IMG_4672", 0.3),  # "do time de Sustentabilidade do grupo" → Ludy no palco
    (21.0, "IMG_4671", 0),  # "estamos aqui para celebrar" → Ludy apresentando
    (23.05, "IMG_4688", 0),  # "Dia Mundial da Alimentação" → telão com alimentos
    (25.13, "IMG_4685", 0.5),  # "trouxemos pessoas"
    (26.45, "IMG_4690", 0.3),  # "de diferentes áreas da marca"
    (28.06, "IMG_4692", 0),  # "vivenciar esse projeto na prática" → chegando
    (31.38, "IMG_4693", 0),  # "Estamos aqui…" → mural "Sejam bem-vindos"
    (32.17, "IMG_4696", 0, 0.5),  # "Escola DOM" → camiseta DOM, câmera lenta (tremia)
    (33.73, "IMG_4694", 0.3),  # "times de sede, CD e marca"
    (36.06, "IMG_4695", 0.3),  # "vamos experienciar"
    # Ação na escola: vídeos novos (pasta "AQUI"), todos entram.
    (38.83, "IMG_4835", 0),  # "Foi um dia de muita troca" → meninas batendo palma
    (41.8, "IMG_4884", 2.0),  # "aprendizado e celebração" → aluna falando
    (43.47, "IMG_4752", 0.3),  # "chefe Neide Marco" → as chefs
    (45.05, "IMG_4710", 0.8),  # "parceira de longo prazo do projeto"
    (47.27, "IMG_4732", 0.5),  # "as crianças participaram"
    (48.7, "IMG_4724", 0.5),  # "oficina de cupcakes" → confeitando de perto
    (49.8, "IMG_4714", 0.3),  # "mostrar um pouco mais" → chef ajudando no cupcake
    (51.45, "IMG_4832", 0),  # "para o nosso time" → criança fazendo coração
    (54.77, "IMG_4734", 0.5),  # "Isso reforça a importância"
    (56.6, "IMG_4725", 0),  # "do aproveitamento alimentar"
    (57.6, "IMG_4773", 0.3),
    (59.07, "IMG_4748", 0.3),  # "nessa troca" → equipe com o cupcake
    (60.47, "IMG_4774", 0.5),
    (61.83, "IMG_4784", 0),  # "encantamento para a escola" → Rê chegando
    (63.5, "IMG_4880", 0),  # "presença do Rê, nosso mascote"
    (65.83, "IMG_4862", 0),  # "que celebrou com a gente" → Rê com as crianças
    (67.2, "IMG_4747", 0.3),  # "esse momento tão importante"
    (70.17, None, 0),  # "Celebrar 10 anos…"
    (71.65, "IMG_4750", 0.5),  # "cada prato importa"
    (73.37, "IMG_4739", 0.3),  # "seguimos juntos" → crianças e equipe
    (74.9, "IMG_4736", 0.3),  # "fortalecendo essa rede"
    (76.3, None, 0),  # fecha na Ludy
]

plan = {
    **edit,
    "captions": [{"start": out(a), "end": out(b), "text": t} for a, b, t in CAPTIONS],
    "shots": [{"at": out(sh[0]), "clip": sh[1], "from": sh[2], "rate": sh[3] if len(sh) > 3 else 1}
              for sh in SHOTS],
}
json.dump(plan, open("src/Trabalho/plan-1p5p.json", "w"), ensure_ascii=False, indent=1)
# Confere se cada plano cabe no clipe (duração do clipe - ponto de entrada).
import subprocess
shots = plan["shots"]
for k, sh in enumerate(shots):
    end = shots[k + 1]["at"] if k + 1 < len(shots) else edit["duration"]
    note = ""
    if sh["clip"]:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    f"public/1p5p/{sh['clip']}.mp4"], capture_output=True, text=True).stdout)
        if sh["from"] + (end - sh["at"]) * sh["rate"] > dur:
            note = f"  !! clipe curto ({dur:.1f}s)"
    print(f'{sh["at"]:6.2f} {end - sh["at"]:5.2f}s {sh["clip"] or "A-roll"}{note}')
print(f'duração {edit["duration"]:.1f}s')
