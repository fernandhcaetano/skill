import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { FPS, Word, words } from "./data";
import { theme } from "./theme";

// Palavras que ganham destaque quando aparecem no bloco.
const KEYWORDS = new Set([
  "difícil", "impossível", "dever", "mobilização", "rua", "barulho", "divulgamos",
  "juntaram", "continuar", "internet", "povo", "ensinar", "segurança", "errou",
  "piora", "fiscalizar", "mobilizar", "prioritário", "envolvidos", "atento",
  "projetar", "reeleito", "manchado", "nascer", "votar", "ruins", "Lula",
  "Bolsonaro", "Senado", "Deputados", "governador", "população", "eleito",
]);

type Block = { words: Word[]; hi: number; start: number; end: number };

const clean = (t: string) => t.replace(/[^\p{L}\p{N}]/gu, "");

const buildBlocks = (): Block[] => {
  const blocks: Block[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (!cur.length) return;
    let hi = cur.findIndex((w) => KEYWORDS.has(clean(w.text)));
    if (hi < 0) {
      hi = cur.reduce((best, w, i) => (clean(w.text).length > clean(cur[best].text).length ? i : best), 0);
    }
    blocks.push({ words: cur, hi, start: cur[0].start, end: cur[cur.length - 1].end });
    cur = [];
  };
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const punct = /[.,?!]$/.test(w.text);
    const gap = next ? next.start - w.end : 1;
    if (cur.length >= 4 || punct || gap > 0.3) flush();
  });
  flush();
  // Cada bloco fica na tela até o próximo começar (no máx. +0,4 s).
  return blocks.map((b, i) => ({
    ...b,
    end: Math.min(blocks[i + 1]?.start ?? b.end + 0.4, b.end + 0.4),
  }));
};

const blocks = buildBlocks();

const AnimatedWord: React.FC<{ w: Word; t: number; big?: boolean; onLight: boolean }> = ({ w, t, big, onLight }) => {
  const p = interpolate(t, [w.start - 0.03, w.start + 0.17], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const color = big ? (onLight ? theme.accent : "#fff") : onLight ? theme.ink : "#fff";
  return (
    <span
      style={{
        display: "inline-block",
        marginRight: big ? 0 : "0.25em",
        color,
        opacity: 0.22 + 0.78 * p,
        filter: `blur(${(1 - p) * 10}px)`,
        transform: `translateY(${(1 - p) * 10}px)`,
      }}
    >
      {w.text}
    </span>
  );
};

export const Captions: React.FC<{ onLight: (t: number) => boolean }> = ({ onLight }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const block = blocks.find((b) => t >= b.start - 0.05 && t < b.end);
  if (!block) return null;
  const light = onLight(t);
  const out = interpolate(t, [block.end - 0.15, block.end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pre = block.words.slice(0, block.hi);
  const post = block.words.slice(block.hi + 1);
  const shadow = light ? "none" : "0 4px 20px rgba(0,0,0,.45)";
  const small: React.CSSProperties = { fontSize: 50, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.15 };

  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: light ? 1130 : 170,
        textAlign: "center",
        fontFamily: theme.font,
        textShadow: shadow,
        opacity: out,
        filter: `blur(${(1 - out) * 8}px)`,
      }}
    >
      {pre.length > 0 && (
        <div style={small}>
          {pre.map((w, i) => <AnimatedWord key={i} w={w} t={t} onLight={light} />)}
        </div>
      )}
      <div style={{ fontSize: 108, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.05 }}>
        <AnimatedWord w={block.words[block.hi]} t={t} big onLight={light} />
      </div>
      {post.length > 0 && (
        <div style={{ ...small, fontSize: 42 }}>
          {post.map((w, i) => <AnimatedWord key={i} w={w} t={t} onLight={light} />)}
        </div>
      )}
    </div>
  );
};
