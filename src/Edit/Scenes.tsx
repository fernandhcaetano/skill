import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { findPhrase, FPS } from "./data";
import { theme } from "./theme";

// Telas de motion graphics que entram por cima do vídeo enquanto a fala continua.
// Cada tela começa/termina numa frase da transcrição.

const useEnter = (delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 14, mass: 0.6 } });
};

const Background: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(circle at 100% 0%, ${theme.bgGlow} 0%, transparent 45%),
        radial-gradient(circle at 0% 100%, ${theme.bgGlow} 0%, transparent 45%), ${theme.bg}`,
      fontFamily: theme.font,
      color: theme.ink,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Pill: React.FC<{ children: React.ReactNode; dark?: boolean; style?: React.CSSProperties }> = ({ children, dark, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 14,
      padding: "14px 30px",
      borderRadius: 999,
      background: dark ? "#111" : "#fff",
      color: dark ? "#fff" : theme.ink,
      fontFamily: theme.mono,
      fontSize: 30,
      letterSpacing: "0.05em",
      boxShadow: theme.cardShadow,
      ...style,
    }}
  >
    {dark && <span style={{ width: 12, height: 12, borderRadius: 6, background: theme.accent }} />}
    {children}
  </div>
);

const Card: React.FC<{ children: React.ReactNode; delay?: number; style?: React.CSSProperties }> = ({ children, delay = 0, style }) => {
  const p = useEnter(delay);
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 32,
        boxShadow: theme.cardShadow,
        padding: "44px 52px",
        opacity: p,
        transform: `scale(${0.9 + 0.1 * p}) translateY(${(1 - p) * 30}px)`,
        filter: `blur(${(1 - p) * 8}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const Center: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 380, gap: 36 }}>
    {children}
  </AbsoluteFill>
);

// Checklist que marca cada item no momento em que a palavra é dita.
export const Checklist: React.FC<{ title: string; items: { label: string; at: number }[]; sceneStart: number }> = ({ title, items, sceneStart }) => {
  const frame = useCurrentFrame();
  const t = sceneStart + frame / FPS;
  return (
    <Card style={{ width: 760 }}>
      <div style={{ fontFamily: theme.mono, fontSize: 30, color: "#888", marginBottom: 26 }}>{title}</div>
      {items.map((it) => {
        const on = interpolate(t, [it.at, it.at + 0.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={it.label} style={{ display: "flex", alignItems: "center", gap: 24, margin: "18px 0", opacity: 0.3 + 0.7 * on }}>
            <div
              style={{
                width: 52, height: 52, borderRadius: 12,
                border: `4px solid ${on > 0.5 ? theme.accent : "#ccd"}`,
                background: on > 0.5 ? theme.accent : "transparent",
                color: "#fff", fontSize: 36, fontWeight: 800,
                display: "flex", alignItems: "center", justifyContent: "center",
                transform: `scale(${1 + 0.15 * Math.sin(on * Math.PI)})`,
              }}
            >
              {on > 0.5 ? "✓" : ""}
            </div>
            <div style={{ fontSize: 58, fontWeight: 800, letterSpacing: "-0.02em" }}>{it.label}</div>
          </div>
        );
      })}
    </Card>
  );
};

export type Scene = { start: number; end: number; render: (start: number) => React.ReactNode };

const sc = (startPhrase: string, endPhrase: string, render: Scene["render"]): Scene => {
  const [start] = findPhrase(startPhrase);
  const [, end] = findPhrase(endPhrase, start);
  return { start: start - 0.1, end: end + 0.25, render };
};

export const scenes: Scene[] = [
  sc("primeira Black Friday", "na arena", () => (
    <Center>
      <Pill dark>RESERVA · NA ARENA</Pill>
      <Card delay={4} style={{ width: 640, textAlign: "center", background: "#111" }}>
        <div style={{ fontFamily: theme.mono, fontSize: 30, color: "#aaa", letterSpacing: "0.05em" }}>PRIMEIRA</div>
        <div style={{ fontSize: 118, fontWeight: 800, color: "#fff", letterSpacing: "-0.03em", lineHeight: 1 }}>BLACK</div>
        <div style={{ fontSize: 118, fontWeight: 800, color: theme.orange, letterSpacing: "-0.03em", lineHeight: 1 }}>FRIDAY</div>
      </Card>
    </Center>
  )),
  sc("bateu a primeira meta", "mais gritou", (s) => <Meta sceneStart={s} />),
  sc("as expectativas foram criadas", "estão altíssimas", (s) => <Hype sceneStart={s} />),
  sc("veio pra ganhar", "esse jogo", () => (
    <Center>
      <Card style={{ width: 300, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontSize: 190, lineHeight: 1 }}>🏆</div>
      </Card>
      <Pill dark>VEIO PRA GANHAR</Pill>
    </Center>
  )),
];

// Barra de meta que enche e marca no momento de "meta".
const Meta: React.FC<{ sceneStart: number }> = ({ sceneStart }) => {
  const frame = useCurrentFrame();
  const t = sceneStart + frame / FPS;
  const hit = findPhrase("meta")[0];
  const fill = interpolate(t, [sceneStart + 0.2, hit], [0.1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const done = t >= hit;
  return (
    <Center>
      <Card style={{ width: 760 }}>
        <div style={{ fontFamily: theme.mono, fontSize: 30, color: "#888", display: "flex", justifyContent: "space-between" }}>
          <span>meta_1</span>
          <span style={{ color: done ? theme.accent : "#888" }}>{Math.round(fill * 100)}%</span>
        </div>
        <div style={{ height: 40, borderRadius: 20, background: "#e9ecf5", marginTop: 26, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${fill * 100}%`, borderRadius: 20, background: theme.accent }} />
        </div>
        <div style={{ fontSize: 58, fontWeight: 800, marginTop: 30, letterSpacing: "-0.02em", opacity: done ? 1 : 0.3 }}>
          {done ? "✓ " : ""}primeira meta batida
        </div>
      </Card>
      {t >= findPhrase("a marca que")[0] && (
        <Card style={{ padding: "22px 40px", background: theme.orange, transform: "rotate(-4deg)" }}>
          <div style={{ fontSize: 54, fontWeight: 800, color: "#fff" }}>A MARCA QUE MAIS GRITOU</div>
        </Card>
      )}
    </Center>
  );
};

// Medidor de expectativa que sobe até "altíssimas".
const Hype: React.FC<{ sceneStart: number }> = ({ sceneStart }) => {
  const frame = useCurrentFrame();
  const t = sceneStart + frame / FPS;
  const top = findPhrase("estão altíssimas")[1];
  const lvl = interpolate(t, [sceneStart + 0.2, top], [0.15, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Center>
      <Pill dark>EXPECTATIVAS</Pill>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 26, height: 440 }}>
        {[0.25, 0.45, 0.65, 0.85, 1].map((h, k) => {
          const on = lvl >= h - 0.05;
          return (
            <div key={k} style={{ width: 110, height: 440 * h, borderRadius: 24, boxShadow: theme.cardShadow,
              background: on ? (k === 4 ? theme.orange : theme.accent) : "#fff", transition: "none" }} />
          );
        })}
      </div>
      <div style={{ fontSize: 96, fontWeight: 800, letterSpacing: "-0.03em", color: theme.orange, opacity: lvl > 0.95 ? 1 : 0 }}>
        ALTÍSSIMAS
      </div>
    </Center>
  );
};

export const SceneLayer: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const len = (scene.end - scene.start) * FPS;
  const o = interpolate(frame, [0, 5, len - 6, len], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Background>{scene.render(scene.start)}</Background>
    </AbsoluteFill>
  );
};
