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

# (tempo na fonte onde o plano começa, clipe ou None = A-roll, ponto de entrada no clipe)
# 14.9 = fim do trecho 3: o plano do logo ocupa o silêncio inserido (GAP_AFTER).
SHOTS = [
    (1.47, None, 0),  # "Você sabia que a cada peça…"
    (6.43, "IMG_4681", 2.5),  # "esse é o 1P5P" → telão 1P=5P
    (8.36, None, 0),
    (10.25, "IMG_4664", 0),  # "complementação alimentar" → mesa de comida
    (13.1, None, 0),
    (14.9, "IMG_4691", 0.2),  # respiro de marca: parede "Gente boa e do bem"
    (17.07, "IMG_4672", 0.3),  # "Oi, eu sou a Ludy" → Ludy no palco
    (21.0, "IMG_4671", 0),  # "estamos aqui para celebrar"
    (23.05, "IMG_4688", 0),  # "Dia Mundial da Alimentação" → telão com alimentos
    (25.13, "IMG_4685", 0.5),  # "trouxemos pessoas"
    (26.45, "IMG_4690", 0.3),  # "de diferentes áreas da marca"
    (28.06, "IMG_4692", 0),  # "vivenciar esse projeto na prática" → chegando
    (31.38, "IMG_4693", 0),  # "Estamos aqui…" → mural "Sejam bem-vindos"
    (32.17, "IMG_4696", 0),  # "Escola DOM" → camiseta DOM
    (33.73, "IMG_4694", 0.3),  # "times de sede, CD e marca"
    (36.06, "IMG_4695", 0.3),  # "vamos experienciar"
    (38.83, "IMG_4700", 3),  # "Foi um dia de muita troca"
    (41.8, "IMG_4711", 0.5),  # "aprendizado e celebração"
    (43.47, "IMG_4709", 0),  # "chefe Neide Marco" → chefs
    (45.05, "IMG_4710", 0.8),
    (47.27, "IMG_4713", 0),  # "as crianças participaram"
    (48.7, "IMG_4714", 0.3),  # "oficina de cupcakes"
    (49.8, "IMG_4708", 0),  # "mostrar um pouco mais da escola"
    (51.45, "IMG_4706", 0.5),
    (54.77, "IMG_4715", 0),  # "aproveitamento alimentar"
    (56.6, "IMG_4716", 0.5),
    (59.07, "IMG_4712", 0.3),  # "nessa troca"
    (60.47, "438f643e", 1.5),  # "encantamento para a escola" → Rê chega nas mesas
    (63.5, "729f8c30", 0),  # "presença do Rê, nosso mascote"
    (65.84, "fe3cbf1e", 3.0),  # "que celebrou com a gente" → Rê dançando
    (67.2, "438f643e", 6.2),  # "esse momento tão importante" → crianças de braços pra cima
    (70.17, None, 0),  # "Celebrar 10 anos…"
    (73.37, "736c2a90", 0),  # "seguimos juntos, fortalecendo essa rede" → abraço do Rê
    (76.3, None, 0),  # fecha na Ludy
]

plan = {
    **edit,
    "captions": [{"start": out(a), "end": out(b), "text": t} for a, b, t in CAPTIONS],
    "shots": [{"at": out(a), "clip": c, "from": f} for a, c, f in SHOTS],
}
json.dump(plan, open("src/Trabalho/plan-1p5p.json", "w"), ensure_ascii=False, indent=1)
for s in plan["shots"]:
    print(f'{s["at"]:6.2f} {s["clip"] or "A-roll"}')
print(f'duração {edit["duration"]:.1f}s')
