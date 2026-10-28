// Reserva 1P5P – plano a plano (tempos no vídeo final, em segundos).
// clip null = A-roll (Ludy falando). `from` = ponto de entrada no clipe de B-roll.
// Os dois "só audio" (14,2–58,2 s) não têm imagem útil: ali é 100 % B-roll.
export type Shot = { at: number; clip: string | null; from: number };

export const shots: Shot[] = [
  { at: 0, clip: null, from: 0 }, // "Você sabia que a cada peça…"
  { at: 4.6, clip: "IMG_4681", from: 2.5 }, // "esse é o 1P5P" → telão 1P=5P
  { at: 6.16, clip: null, from: 0 },
  { at: 8.05, clip: "IMG_4664", from: 0 }, // "complementação alimentar" → mesa de comida
  { at: 10.9, clip: null, from: 0 },
  { at: 12.7, clip: "IMG_4691", from: 0.3 }, // respiro de marca: logo "Gente boa e do bem"
  { at: 14.2, clip: "IMG_4672", from: 0.3 }, // "Oi, eu sou a Ludy" → Ludy no palco
  { at: 18.13, clip: "IMG_4671", from: 0 }, // "estamos aqui para celebrar"
  { at: 19.88, clip: "IMG_4688", from: 0 }, // "Dia Mundial da Alimentação" → telão com alimentos
  { at: 21.8, clip: "IMG_4685", from: 0.5 }, // "trouxemos pessoas"
  { at: 23.12, clip: "IMG_4690", from: 0.3 }, // "de diferentes áreas da marca"
  { at: 24.73, clip: "IMG_4692", from: 0 }, // "vivenciar esse projeto na prática" → chegando
  { at: 27.41, clip: "IMG_4693", from: 0 }, // "Estamos aqui…" → mural "Sejam bem-vindos"
  { at: 28.2, clip: "IMG_4696", from: 0 }, // "Escola DOM" → camiseta DOM
  { at: 29.4, clip: "IMG_4694", from: 0.3 }, // "times de sede, CD e marca"
  { at: 31.73, clip: "IMG_4695", from: 0.3 }, // "vamos experienciar"
  { at: 34.33, clip: "IMG_4700", from: 3 }, // "Foi um dia de muita troca"
  { at: 35.73, clip: "IMG_4711", from: 0.5 }, // "aprendizado e celebração"
  { at: 37.14, clip: "IMG_4709", from: 0 }, // "chef …" → chefs
  { at: 38.72, clip: "IMG_4710", from: 0.8 },
  { at: 40.6, clip: "IMG_4713", from: 0 }, // "as crianças participaram"
  { at: 42.03, clip: "IMG_4714", from: 0.3 }, // "oficina de cupcakes"
  { at: 43.13, clip: "IMG_4708", from: 0 }, // "mostrar um pouco mais da escola"
  { at: 44.55, clip: "IMG_4706", from: 0.5 },
  { at: 45.97, clip: "IMG_4715", from: 0 }, // "aproveitamento alimentar"
  { at: 47.8, clip: "IMG_4716", from: 0.5 },
  { at: 49.8, clip: "IMG_4712", from: 0.3 }, // "nessa troca"
  { at: 51.2, clip: "438f643e", from: 3.5 }, // "encantamento para a escola"
  { at: 54.0, clip: "c8c60717", from: 2.5 }, // "presença do Rê, nosso mascote"
  { at: 55.97, clip: "2e781ec8", from: 0 }, // "que celebrou com a gente"
  { at: 57.07, clip: "729f8c30", from: 0 }, // "esse momento tão importante"
  { at: 58.2, clip: null, from: 0 }, // "Celebrar 10 anos…"
  { at: 61.0, clip: "736c2a90", from: 0 }, // "seguimos juntos, fortalecendo essa rede"
  { at: 63.73, clip: null, from: 0 }, // fecha na Ludy
];
