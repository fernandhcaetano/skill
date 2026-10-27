import React from "react";
import "@fontsource/oswald/500.css";
import "@fontsource/oswald/600.css";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";

// Reels "5 motivos – Extra Natal": o vídeo original fica intacto; entre os motivos entra
// uma cartela de parede branca com o título do briefing, e no fim a tela com o logo.

const SOURCE_FRAMES = 1565; // natal.mp4 = 52,17 s
// Cortes do próprio vídeo onde cada motivo começa (momentos sem fala).
const MOTIVO_CUTS = [160, 346, 588, 811, 1048];
const MOTIVOS = [
  "MODA MASCULINA PREMIUM",
  "ATENDIMENTO QUE FAZ A DIFERENÇA",
  "APRENDIZADO NA PRÁTICA",
  "ATENÇÃO AOS DETALHES",
  "TRABALHO EM EQUIPE",
];
const CARD = 60; // 2 s
const END = 75; // 2,5 s
const FADE = 2; // micro-fade de áudio nos pontos de corte

type Block = { kind: "video"; from: number; to: number } | { kind: "card"; n: number } | { kind: "end" };

const blocks: Block[] = [];
let prev = 0;
MOTIVO_CUTS.forEach((cut, i) => {
  blocks.push({ kind: "video", from: prev, to: cut }, { kind: "card", n: i });
  prev = cut;
});
blocks.push({ kind: "video", from: prev, to: SOURCE_FRAMES }, { kind: "end" });

const len = (b: Block) => (b.kind === "video" ? b.to - b.from : b.kind === "card" ? CARD : END);
export const NATAL_DURATION = blocks.reduce((s, b) => s + len(b), 0);

const Wall: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #FFFFFF 0%, #F3F1ED 70%, #E9E6E0 100%)" }}>
    {/* textura sutil de parede pintada */}
    <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.07 }}>
      <filter id="wall">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="4" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#wall)" />
    </svg>
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>{children}</AbsoluteFill>
  </AbsoluteFill>
);

const MotivoCard: React.FC<{ n: number }> = ({ n }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [3, 13], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ease = 1 - (1 - p) ** 3;
  return (
    <Wall>
      <div
        style={{
          width: 880,
          textAlign: "center",
          color: "#111",
          fontFamily: "'Oswald', sans-serif",
          textTransform: "uppercase",
          opacity: ease,
          transform: `translateY(${(1 - ease) * 24}px)`,
        }}
      >
        <div style={{ fontSize: 50, fontWeight: 500, letterSpacing: `${0.22 - 0.08 * ease}em`, marginBottom: 18 }}>
          Motivo {n + 1} —
        </div>
        <div style={{ fontSize: 104, fontWeight: 600, lineHeight: 1.02, letterSpacing: "0.01em" }}>{MOTIVOS[n]}</div>
      </div>
    </Wall>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ease = 1 - (1 - p) ** 3;
  return (
    <Wall>
      <Img
        src={staticFile("oficina.svg")}
        style={{ width: 620, opacity: ease, transform: `scale(${0.94 + 0.06 * ease})`, filter: `blur(${(1 - ease) * 6}px)` }}
      />
    </Wall>
  );
};

const VideoPart: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const d = to - from;
  return (
    <OffthreadVideo
      src={staticFile("natal.mp4")}
      startFrom={from}
      endAt={to}
      volume={(f) => interpolate(f, [0, FADE, d - FADE, d], [from === 0 ? 1 : 0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
    />
  );
};

export const Natal: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill style={{ background: "#fff" }}>
      {blocks.map((b, i) => {
        const start = at;
        at += len(b);
        return (
          <React.Fragment key={i}>
            <Sequence from={start} durationInFrames={len(b)}>
              {b.kind === "video" && <VideoPart from={b.from} to={b.to} />}
              {b.kind === "card" && <MotivoCard n={b.n} />}
              {b.kind === "end" && <EndCard />}
            </Sequence>
            {b.kind === "card" && (
              <>
                <Sequence from={start - 8} durationInFrames={17}>
                  <Audio src={staticFile("sfx/whoosh.wav")} volume={0.55} />
                </Sequence>
                <Sequence from={start + 5} durationInFrames={11}>
                  <Audio src={staticFile("sfx/hit.wav")} volume={0.5} />
                </Sequence>
              </>
            )}
            {b.kind === "end" && (
              <Sequence from={start} durationInFrames={END}>
                <Audio src={staticFile("sfx/chime.wav")} volume={0.45} />
              </Sequence>
            )}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
