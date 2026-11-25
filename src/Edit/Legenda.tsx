import "@fontsource/inter/500.css";
import React from "react";
import { useCurrentFrame } from "remotion";
import { FPS, Word, words } from "./data";

// Legenda no estilo do vídeo "kit da Reserva": pequena, branca com contorno preto fino,
// por frase, ~77 % da altura, sem destaque nem animação.
type Block = { text: string; start: number; end: number };

const buildBlocks = (): Block[] => {
  const blocks: Block[] = [];
  let cur: Word[] = [];
  let sentenceStart = true;
  const flush = () => {
    if (!cur.length) return;
    let text = cur.map((w) => w.text).join(" ");
    if (sentenceStart) text = text[0].toUpperCase() + text.slice(1);
    sentenceStart = /[.?!]$/.test(text);
    blocks.push({ text, start: cur[0].start, end: cur[cur.length - 1].end });
    cur = [];
  };
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const gap = next ? next.start - w.end : 1;
    if (/[.?!]$/.test(w.text) || (/,$/.test(w.text) && cur.length >= 3) || cur.length >= 7 || gap > 0.4) flush();
  });
  flush();
  return blocks.map((b, i) => ({ ...b, end: Math.min(blocks[i + 1]?.start ?? b.end + 0.5, b.end + 0.5) }));
};

const blocks = buildBlocks();

export const Legenda: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const b = blocks.find((x) => t >= x.start - 0.05 && t < x.end);
  if (!b) return null;
  return (
    <div
      style={{
        position: "absolute", top: 1460, left: 0, right: 0, display: "flex", justifyContent: "center",
      }}
    >
      <div
        style={{
          maxWidth: 720, textAlign: "center", color: "#fff",
          fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: 32, lineHeight: 1.25,
          WebkitTextStroke: "2.5px #000", paintOrder: "stroke fill",
          textShadow: "0 1px 3px rgba(0,0,0,.35)",
        }}
      >
        {b.text}
      </div>
    </div>
  );
};
