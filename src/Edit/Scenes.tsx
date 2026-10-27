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
const Checklist: React.FC<{ title: string; items: { label: string; at: number }[]; sceneStart: number }> = ({ title, items, sceneStart }) => {
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
  sc("já tem uma Câmara", "tipo de governo", () => (
    <Center>
      <Pill dark>CONGRESSO NACIONAL</Pill>
      <div style={{ display: "flex", gap: 30 }}>
        <Card delay={4} style={{ width: 400, textAlign: "center" }}>
          <div style={{ fontSize: 56, fontWeight: 800 }}>Câmara</div>
          <div style={{ fontSize: 34, color: "#777" }}>dos Deputados</div>
        </Card>
        <Card delay={22} style={{ width: 400, textAlign: "center" }}>
          <div style={{ fontSize: 56, fontWeight: 800 }}>Senado</div>
          <div style={{ fontSize: 34, color: "#777" }}>Federal</div>
        </Card>
      </div>
      <Card delay={40} style={{ padding: "26px 44px" }}>
        <div style={{ fontSize: 44, fontWeight: 800, color: theme.orange }}>maioria contra o governo</div>
      </Card>
    </Center>
  )),
  sc("quase impossível", "de passar", () => (
    <Center>
      <Card style={{ width: 760 }}>
        <div style={{ fontFamily: theme.mono, fontSize: 30, color: "#888" }}>proposta_do_governo.pdf</div>
        {[0, 1, 2].map((k) => (
          <div key={k} style={{ height: 22, borderRadius: 11, background: "#e9ecf5", margin: "26px 0", width: `${90 - k * 18}%` }} />
        ))}
      </Card>
      <Card delay={8} style={{ padding: "22px 40px", background: theme.orange, transform: "rotate(-6deg)" }}>
        <div style={{ fontSize: 60, fontWeight: 800, color: "#fff" }}>QUASE IMPOSSÍVEL</div>
      </Card>
    </Center>
  )),
  sc("nós fomos pra rua", "nós divulgamos", (s) => (
    <Center>
      <Pill dark>COMO GANHAMOS</Pill>
      <Checklist
        sceneStart={s}
        title="mobilização.md"
        items={[
          { label: "fomos pra rua", at: findPhrase("pra rua")[0] },
          { label: "fizemos barulho", at: findPhrase("fizemos barulho")[0] },
          { label: "divulgamos", at: findPhrase("divulgamos")[0] },
        ]}
      />
    </Center>
  )),
  sc("esquerda e direita", "família Bolsonaro", (s) => <Union sceneStart={s} />),
  sc("qual é o dever", "de cada um", () => (
    <Center>
      <Card style={{ width: 300, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontSize: 220, fontWeight: 800, color: theme.accent }}>?</div>
      </Card>
      <Pill dark>O DEVER DE CADA UM</Pill>
    </Center>
  )),
  sc("da segurança pública do Rio", "Rio de Janeiro", () => (
    <Center>
      <Pill dark>RIO DE JANEIRO</Pill>
      <Card delay={4} style={{ width: 760, textAlign: "center" }}>
        <div style={{ fontFamily: theme.mono, fontSize: 30, color: "#888" }}>responsável por</div>
        <div style={{ fontSize: 70, fontWeight: 800, color: theme.accent, letterSpacing: "-0.02em" }}>segurança pública</div>
        <div style={{ fontSize: 44, fontWeight: 600 }}>= governador do estado</div>
      </Card>
    </Center>
  )),
  sc("cabe a gente fiscalizar", "se mobilizar", (s) => (
    <Center>
      <Checklist
        sceneStart={s}
        title="nosso_papel.md"
        items={[
          { label: "fiscalizar", at: findPhrase("fiscalizar")[0] },
          { label: "se mobilizar", at: findPhrase("se mobilizar", findPhrase("fiscalizar")[0])[0] },
        ]}
      />
    </Center>
  )),
  sc("daqui a quatro anos", "em quem votar", () => (
    <Center>
      <Pill dark>PRÓXIMA ELEIÇÃO</Pill>
      <Card delay={4} style={{ textAlign: "center", width: 520 }}>
        <div style={{ fontSize: 200, fontWeight: 800, color: theme.accent, lineHeight: 1 }}>4</div>
        <div style={{ fontSize: 56, fontWeight: 800 }}>anos</div>
      </Card>
    </Center>
  )),
];

const Union: React.FC<{ sceneStart: number }> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - 18, fps, config: { damping: 16 } });
  const box = (label: string, color: string, dir: number) => (
    <div
      style={{
        position: "absolute", top: 640, left: 540 - 210 + dir * (420 - 200 * p),
        width: 420, padding: "34px 0", textAlign: "center", borderRadius: 999,
        background: "#fff", boxShadow: theme.cardShadow, fontSize: 58, fontWeight: 800, color,
      }}
    >
      {label}
    </div>
  );
  return (
    <AbsoluteFill>
      {box("esquerda", theme.orange, -1)}
      {box("direita", theme.accent, 1)}
      <div style={{ position: "absolute", top: 860, width: "100%", textAlign: "center", opacity: p }}>
        <Pill dark>JUNTOS NAS URNAS</Pill>
      </div>
    </AbsoluteFill>
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
