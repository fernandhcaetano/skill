import React from "react";
import "@fontsource/poppins/500.css";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import edit from "./edit-1p5p.json";
import captions from "./captions-1p5p.json";
import { shots } from "./shots-1p5p";

// "Estilo Trabalho" (estilo-trabalho.md): cortes secos, A-roll intercalado com B-roll,
// legenda pequena branca com contorno, por frase, centralizada em y ≈ 1460 px. Sem efeitos.

const { fps: FPS, duration: DURATION, segments } = edit;

export const TRABALHO_DURATION = Math.ceil(DURATION * FPS);

// A-roll: um <Sequence> por trecho de fala. O último se estende pelo respiro final.
const ARoll: React.FC = () => (
  <>
    {segments.map((s, i) => {
      const from = Math.round(s.outStart * FPS);
      const last = i === segments.length - 1;
      const dur = last ? TRABALHO_DURATION - from : Math.round((s.srcEnd - s.srcStart) * FPS);
      return (
        <Sequence key={i} from={from} durationInFrames={dur} premountFor={30}>
          <OffthreadVideo src={staticFile("video_proxy.mp4")} startFrom={Math.round(s.srcStart * FPS)} muted />
        </Sequence>
      );
    })}
  </>
);

// B-roll por cima do A-roll; voz contínua.
const BRoll: React.FC = () => (
  <>
    {shots.map((sh, i) => {
      if (!sh.clip) return null;
      const from = Math.round(sh.at * FPS);
      const end = i + 1 < shots.length ? shots[i + 1].at : DURATION;
      return (
        <Sequence key={i} from={from} durationInFrames={Math.round(end * FPS) - from} premountFor={30}>
          <OffthreadVideo src={staticFile(`1p5p/${sh.clip}.mp4`)} startFrom={Math.round(sh.from * FPS)} muted />
        </Sequence>
      );
    })}
  </>
);

// Legenda segura até a próxima frase quando o intervalo é curto, para não piscar.
const Caption: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const i = captions.findIndex((c, k) => {
    const next = captions[k + 1];
    const end = next && next.start - c.end < 0.35 ? next.start : c.end;
    return t >= c.start && t < end;
  });
  if (i < 0) return null;
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: 1460,
          maxWidth: 700,
          textAlign: "center",
          fontFamily: "'Poppins', sans-serif",
          fontWeight: 500,
          fontSize: 36,
          lineHeight: 1.3,
          color: "#FFFFFF",
          WebkitTextStroke: "1.5px #000",
          paintOrder: "stroke fill",
          textShadow: "0 0 2px rgba(0,0,0,0.6)",
        }}
      >
        {captions[i].text}
      </div>
    </AbsoluteFill>
  );
};

export const Trabalho: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <ARoll />
    <BRoll />
    <Caption />
    <Audio src={staticFile("voice.wav")} />
  </AbsoluteFill>
);
