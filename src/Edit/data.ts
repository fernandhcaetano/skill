import edit from "../edit.json";

export type Word = { text: string; start: number; end: number };
export type Segment = { srcStart: number; srcEnd: number; outStart: number };

export const FPS = edit.fps;
export const DURATION = edit.duration;
export const words: Word[] = edit.words;
export const segments: Segment[] = edit.segments;

const norm = (s: string) => s.toLowerCase().replace(/[^\p{L}\p{N} ]/gu, "");

// Encontra uma frase na transcrição e devolve [início, fim] em segundos.
export const findPhrase = (phrase: string, from = 0): [number, number] => {
  const target = phrase.split(" ").map(norm);
  for (let i = 0; i < words.length; i++) {
    if (words[i].start < from) continue;
    if (target.every((t, k) => words[i + k] && norm(words[i + k].text) === t)) {
      return [words[i].start, words[i + target.length - 1].end];
    }
  }
  throw new Error(`Frase não encontrada: ${phrase}`);
};
