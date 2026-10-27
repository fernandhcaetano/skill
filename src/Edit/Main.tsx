import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./Captions";
import { FPS, segments } from "./data";
import { SceneLayer, scenes } from "./Scenes";

// Alterna enquadramento a cada corte (aberto / fechado) para dar ritmo.
const ZOOMS = [1.0, 1.14, 1.06, 1.18];

const Clip: React.FC<{ srcStart: number; dur: number; zoom: number }> = ({ srcStart, dur, zoom }) => {
  const frame = useCurrentFrame();
  // leve push-in contínuo dentro do plano
  const push = interpolate(frame, [0, dur * FPS], [0, 0.03]);
  return (
    <AbsoluteFill style={{ transform: `scale(${zoom + push})`, transformOrigin: "50% 42%" }}>
      <OffthreadVideo src={staticFile("video_proxy.mp4")} startFrom={Math.round(srcStart * FPS)} muted />
    </AbsoluteFill>
  );
};

const onLight = (t: number) => scenes.some((s) => t >= s.start && t < s.end);

export const Main: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {segments.map((s, i) => {
        const from = Math.round(s.outStart * FPS);
        const dur = Math.round((s.srcEnd - s.srcStart) * FPS);
        return (
          <Sequence key={i} from={from} durationInFrames={dur} premountFor={30}>
            <Clip srcStart={s.srcStart} dur={dur / FPS} zoom={ZOOMS[i % ZOOMS.length]} />
          </Sequence>
        );
      })}
      {scenes.map((sc, i) => (
        <Sequence key={`s${i}`} from={Math.round(sc.start * FPS)} durationInFrames={Math.round((sc.end - sc.start) * FPS)}>
          <SceneLayer scene={sc} />
        </Sequence>
      ))}
      <Captions onLight={onLight} />
      <Audio src={staticFile("voice.wav")} />
    </AbsoluteFill>
  );
};
