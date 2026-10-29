import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";

// Reels do Rê (mascote da Reserva) na Escola DOM – 1P5P. Sem som (a música entra na postagem).
// Cortes rápidos (~1–1,5 s), alternando o Rê e a reação das crianças.
// [clipe, ponto de entrada (s), duração (s), zoom] – zoom > 1 = plano fechado com leve push-in.
type Cut = [clip: string, from: number, dur: number, zoom?: number];

const CUTS: Cut[] = [
  // chegada pela escada
  ["IMG_4784", 0.0, 1.6],
  ["IMG_4786", 1.4, 1.2, 1.12],
  ["IMG_4785", 2.4, 1.3],
  ["IMG_4787", 0.0, 0.9, 1.1],
  ["IMG_4784", 5.2, 1.4],
  // entrando no refeitório
  ["IMG_4788", 0.0, 1.1],
  ["IMG_4790", 0.2, 1.4],
  ["IMG_4791", 0.0, 1.3],
  ["IMG_4793", 0.5, 1.2, 1.15],
  ["IMG_4791", 2.6, 1.2],
  ["IMG_4796", 0.4, 1.2],
  ["IMG_4790", 2.0, 1.4, 1.1],
  ["IMG_4791", 5.0, 1.4, 1.1],
  ["IMG_4793", 2.2, 1.1],
  // festa com as crianças
  ["IMG_4836", 0.3, 1.4],
  ["IMG_4836", 2.2, 1.3, 1.1],
  ["IMG_4836", 4.6, 1.3, 1.12],
  ["IMG_4860", 0.2, 1.1],
  ["IMG_4860", 2.8, 1.2],
  ["IMG_4861", 0.0, 1.2],
  ["IMG_4861", 1.9, 1.4, 1.1],
  ["IMG_4862", 0.0, 1.4],
  ["IMG_4747", 0.3, 1.1, 1.1],
  ["IMG_4835", 0.0, 1.2, 1.1],
  ["IMG_4879", 0.0, 1.3],
  ["IMG_4879", 2.5, 1.5, 1.1],
  ["IMG_4832", 0.4, 1.2],
  ["IMG_4879", 4.9, 1.4],
  ["IMG_4880", 0.0, 1.4, 1.08],
  ["IMG_4881", 0.6, 1.3],
  ["IMG_4739", 0.3, 1.2],
  ["IMG_4797", 0.0, 1.5],
  ["IMG_4797", 3.4, 3.2],
];

const FPS = 30;
const frames = (s: number) => Math.round(s * FPS);
export const RE_DURATION = CUTS.reduce((t, c) => t + frames(c[2]), 0);

const Shot: React.FC<{ cut: Cut }> = ({ cut: [clip, from, dur, zoom = 1] }) => {
  const f = useCurrentFrame();
  const push = zoom > 1 ? interpolate(f, [0, frames(dur)], [0, 0.03]) : 0;
  return (
    <AbsoluteFill style={{ transform: `scale(${zoom + push})` }}>
      <OffthreadVideo src={staticFile(`1p5p/${clip}.mp4`)} startFrom={frames(from)} muted />
    </AbsoluteFill>
  );
};

export const ReReel: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {CUTS.map((c, i) => {
        const start = at;
        at += frames(c[2]);
        return (
          <Sequence key={i} from={start} durationInFrames={frames(c[2])} premountFor={30}>
            <Shot cut={c} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
