import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  continueRender,
  delayRender,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Telão Black Friday Azzas 2026 — "Modo Friday" pulsando, 1920x1080, loop de 15 s.
export const MF_FPS = 30;
export const MF_DURATION = 450; // 15 s
const BEAT = 15; // 120 bpm
const OUTRO = 420; // a partir daqui tudo sai, para emendar no começo do loop

const FONT = "ArchivoBlackMF";
if (typeof window !== "undefined" && typeof FontFace !== "undefined") {
  const handle = delayRender("fonte Archivo Black");
  const face = new FontFace(FONT, `url(${staticFile("modofriday/ArchivoBlack-Regular.ttf")})`);
  face
    .load()
    .then(() => {
      document.fonts.add(face);
      continueRender(handle);
    })
    .catch(() => continueRender(handle));
}

const C = {
  blue: "#014DB1",
  blueLight: "#2F7BFF",
  blueDark: "#001B55",
  yellow: "#FFD21F",
  red: "#E8262B",
  green: "#22A447",
  ink: "#0B1633",
};

const TAU = Math.PI * 2;

// "batida": 1 no instante do beat, decai rápido. A cada 4 beats, mais forte.
const kick = (frame: number, start: number) => {
  if (frame < start) return 0;
  const t = frame - start;
  const beatIdx = Math.floor(t / BEAT);
  const into = t % BEAT;
  const strength = beatIdx % 4 === 0 ? 1 : 0.6;
  return strength * Math.exp(-into / 3.2);
};

const outroScale = (frame: number, delay = 0) =>
  interpolate(frame, [OUTRO + delay, OUTRO + delay + 18], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.back(2)),
  });

/* ---------------- fundo ---------------- */

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const k = kick(frame, 18);
  const rot = (frame / MF_DURATION) * 30; // 30° por loop = 2 raios, emenda sem salto
  return (
    <AbsoluteFill style={{ background: C.blue, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 42%, ${C.blueLight} 0%, ${C.blue} 45%, ${C.blueDark} 100%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "40%",
          width: 3200,
          height: 3200,
          marginLeft: -1600,
          marginTop: -1600,
          borderRadius: "50%",
          background:
            "repeating-conic-gradient(from 0deg, rgba(255,255,255,0.10) 0deg 7.5deg, rgba(255,255,255,0) 7.5deg 15deg)",
          transform: `rotate(${rot}deg)`,
          opacity: 0.55 + k * 0.45,
          maskImage: "radial-gradient(circle, black 10%, transparent 60%)",
          WebkitMaskImage: "radial-gradient(circle, black 10%, transparent 60%)",
        }}
      />
      {/* brilho atrás do logo */}
      <div
        style={{
          position: "absolute",
          left: 960 - 700,
          top: 410 - 420,
          width: 1400,
          height: 840,
          borderRadius: "50%",
          background: `radial-gradient(ellipse, rgba(255,226,90,${0.32 + k * 0.3}) 0%, rgba(255,210,31,0) 65%)`,
          transform: `scale(${1 + k * 0.08})`,
        }}
      />
    </AbsoluteFill>
  );
};

/* ---------------- confete e moedas caindo ---------------- */

const CONFETTI_COLORS = [C.yellow, C.red, C.green, "#FFFFFF", "#8F3FD1", "#FF8A00"];

const Confetti: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [10, 40], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [OUTRO, MF_DURATION], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const H = 1080 + 240;
  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>
      {new Array(46).fill(0).map((_, i) => {
        const r = (s: string) => random(`cf-${i}-${s}`);
        const laps = 1 + Math.floor(r("l") * 3); // voltas completas por loop
        const y = ((r("o") * H + (frame * laps * H) / MF_DURATION) % H) - 120;
        const x = r("x") * 1920 + Math.sin((frame / MF_DURATION) * TAU * 2 + r("p") * TAU) * 40;
        const isCoin = i % 7 === 0;
        const spin = (frame / MF_DURATION) * 360 * (2 + Math.floor(r("s") * 3)) * (r("d") > 0.5 ? 1 : -1);
        if (isCoin) {
          const s = 46 + r("z") * 24;
          return (
            <Img
              key={i}
              src={staticFile("modofriday/moeda.png")}
              style={{
                position: "absolute",
                left: x,
                top: y,
                width: s,
                transform: `rotateY(${spin}deg)`,
                opacity: 0.9,
              }}
            />
          );
        }
        const w = 14 + r("w") * 14;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: w,
              height: w * 0.45,
              borderRadius: 3,
              background: CONFETTI_COLORS[Math.floor(r("c") * CONFETTI_COLORS.length)],
              transform: `rotate(${spin}deg) rotateX(${spin * 1.3}deg)`,
              opacity: 0.85,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------------- carta de baralho colorida (estilo jogo de cartas numerado) ---------------- */

const NumberCard: React.FC<{ color: string; label: string; width: number }> = ({ color, label, width }) => {
  const h = width * 1.5;
  const big = label.length > 1 ? width * 0.42 : width * 0.56;
  const stroke = Math.max(2, width * 0.018);
  return (
    <div
      style={{
        width,
        height: h,
        borderRadius: width * 0.1,
        background: "#FFFFFF",
        padding: width * 0.055,
        boxSizing: "border-box",
        boxShadow: "0 18px 30px rgba(0,0,0,0.35)",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          borderRadius: width * 0.07,
          background: color,
          overflow: "hidden",
          fontFamily: FONT,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: width * 0.78,
            height: h * 0.72,
            marginLeft: -width * 0.39,
            marginTop: -h * 0.36,
            borderRadius: "50%",
            background: "#FFFFFF",
            transform: "rotate(28deg)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: big,
            color,
            WebkitTextStroke: `${stroke}px ${C.ink}`,
            textShadow: `${stroke * 2}px ${stroke * 2}px 0 ${C.ink}`,
            fontStyle: "italic",
          }}
        >
          {label}
        </div>
        {[
          { left: width * 0.07, top: width * 0.03, rot: 0 },
          { right: width * 0.07, bottom: width * 0.03, rot: 180 },
        ].map((p, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: p.left,
              top: p.top,
              right: p.right,
              bottom: p.bottom,
              fontSize: width * 0.17,
              color: "#FFFFFF",
              WebkitTextStroke: `${stroke * 0.6}px ${C.ink}`,
              fontStyle: "italic",
              transform: `rotate(${p.rot}deg)`,
            }}
          >
            {label}
          </div>
        ))}
      </div>
    </div>
  );
};

/* ---------------- objetos que entram e flutuam ---------------- */

type Floater = {
  key: string;
  x: number; // centro
  y: number;
  rot: number;
  enter: number; // frame de entrada
  from: [number, number]; // deslocamento inicial
  spin: number; // giros na entrada
  bob: number; // amplitude da flutuação
  z?: number;
  blur?: number;
  render: () => React.ReactNode;
};

const img = (name: string, w: number, extra?: React.CSSProperties) => () => (
  <Img
    src={staticFile(`modofriday/${name}.png`)}
    style={{ width: w, display: "block", filter: "drop-shadow(0 16px 22px rgba(0,0,0,0.38))", ...extra }}
  />
);

const FLOATERS: Floater[] = [
  // fundo (menores, desfocados — dão profundidade)
  { key: "uY", x: 80, y: 560, rot: -24, enter: 30, from: [-500, 0], spin: 1, bob: 16, blur: 3, render: () => <NumberCard color={C.yellow} label="4" width={120} /> },
  { key: "uG", x: 1845, y: 570, rot: 22, enter: 33, from: [500, 0], spin: -1, bob: 16, blur: 3, render: () => <NumberCard color={C.green} label="9" width={120} /> },
  { key: "pR", x: 560, y: 95, rot: -12, enter: 40, from: [0, -400], spin: 0, bob: 10, blur: 2, render: img("peao_vermelho", 70) },
  { key: "pA", x: 1370, y: 95, rot: 14, enter: 42, from: [0, -400], spin: 0, bob: 10, blur: 2, render: img("peao_amarelo", 70) },
  // frente
  { key: "uR", x: 165, y: 255, rot: -14, enter: 14, from: [-700, -300], spin: 2, bob: 22, render: () => <NumberCard color={C.red} label="7" width={190} /> },
  { key: "uB", x: 1755, y: 255, rot: 13, enter: 17, from: [700, -300], spin: -2, bob: 22, render: () => <NumberCard color="#1C6FE0" label="+2" width={190} /> },
  { key: "cS", x: 270, y: 620, rot: 9, enter: 22, from: [-800, 200], spin: 1, bob: 18, render: img("carta_sorte", 185) },
  { key: "cM", x: 1650, y: 620, rot: -9, enter: 25, from: [800, 200], spin: -1, bob: 18, render: img("carta_misterio", 185) },
  { key: "dB", x: 125, y: 950, rot: -10, enter: 28, from: [-600, 500], spin: 3, bob: 12, render: img("dado", 185) },
  { key: "dP", x: 1790, y: 955, rot: 8, enter: 31, from: [600, 500], spin: -3, bob: 12, render: img("dados", 240) },
];

const FloaterLayer: React.FC<{ back: boolean }> = ({ back }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = kick(frame, 18);
  return (
    <AbsoluteFill>
      {FLOATERS.filter((f) => Boolean(f.blur) === back).map((f, i) => {
        const p = spring({ frame: frame - f.enter, fps, config: { damping: 13, stiffness: 90, mass: 0.9 } });
        const phase = random(`bob-${f.key}`) * TAU;
        const t = (frame / MF_DURATION) * TAU;
        const bobY = Math.sin(t * 3 + phase) * f.bob;
        const bobR = Math.sin(t * 2 + phase) * 4;
        const dx = f.from[0] * (1 - p);
        const dy = f.from[1] * (1 - p);
        const rot = f.rot + bobR + (1 - p) * 360 * f.spin;
        const s = outroScale(frame, i * 1.2) * (0.4 + 0.6 * p) * (1 + k * 0.035);
        return (
          <div
            key={f.key}
            style={{
              position: "absolute",
              left: f.x,
              top: f.y,
              transform: `translate(-50%, -50%) translate(${dx}px, ${dy + bobY}px) rotate(${rot}deg) scale(${s})`,
              opacity: p > 0.01 ? 1 : 0,
              filter: f.blur ? `blur(${f.blur}px)` : undefined,
            }}
          >
            {f.render()}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------------- logo ---------------- */

const LOGO_W = 1150;
const LOGO_RATIO = 739 / 1581;
const LOGO_Y = 410;
const LAND = 12;

const Logo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 2, fps, config: { damping: 9, stiffness: 120, mass: 0.8 } });
  const k = kick(frame, 18);
  const wobble = Math.sin((frame / MF_DURATION) * TAU * 4) * 1.6;
  const scale = enter * (1 + k * 0.075) * outroScale(frame, 4);
  const rot = (1 - enter) * -14 + wobble;
  const h = LOGO_W * LOGO_RATIO;
  return (
    <div
      style={{
        position: "absolute",
        left: 960 - LOGO_W / 2,
        top: LOGO_Y - h / 2,
        width: LOGO_W,
        height: h,
        transform: `rotate(${rot}deg) scale(${scale})`,
      }}
    >
      <Img
        src={staticFile("modofriday/logo.png")}
        style={{
          width: "100%",
          filter: `drop-shadow(0 ${14 + k * 10}px 0 rgba(0,17,60,0.55)) drop-shadow(0 0 ${30 + k * 50}px rgba(255,220,80,${0.35 + k * 0.4}))`,
        }}
      />
    </div>
  );
};

// onda de choque na chegada do logo e em cada beat forte
const Shockwaves: React.FC = () => {
  const frame = useCurrentFrame();
  const starts = [LAND];
  for (let f = 18; f < OUTRO; f += BEAT * 4) starts.push(f);
  return (
    <AbsoluteFill>
      {starts.map((s) => {
        const t = frame - s;
        if (t < 0 || t > 26) return null;
        const p = t / 26;
        const size = 500 + p * 1500;
        return (
          <div
            key={s}
            style={{
              position: "absolute",
              left: 960 - size / 2,
              top: LOGO_Y - size * 0.32,
              width: size,
              height: size * 0.64,
              borderRadius: "50%",
              border: `${s === LAND ? 14 : 8}px solid rgba(255,220,80,${(1 - p) * (s === LAND ? 0.9 : 0.5)})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------------- subtítulo ---------------- */

const WORDS: { t: string; hot?: boolean }[] = [
  { t: "A" },
  { t: "NOSSA" },
  { t: "BLACK" },
  { t: "FRIDAY" },
  { t: "JÁ", hot: true },
  { t: "COMEÇOU!", hot: true },
];

const Subtitle: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const box = spring({ frame: frame - 34, fps, config: { damping: 12, stiffness: 140 } });
  const k = kick(frame, 18);
  const bigBeat = frame >= 18 && Math.floor((frame - 18) / BEAT) % 4 === 0 ? k : 0;
  const s = box * (1 + bigBeat * 0.04) * outroScale(frame, 0);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 812,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          transform: `rotate(-2deg) scale(${s})`,
          background: C.yellow,
          padding: "18px 44px 22px",
          borderRadius: 14,
          boxShadow: `10px 10px 0 ${C.ink}`,
          border: `5px solid ${C.ink}`,
          display: "flex",
          gap: 22,
          fontFamily: FONT,
          fontSize: 62,
          lineHeight: 1,
          color: C.ink,
          letterSpacing: 1,
        }}
      >
        {WORDS.map((w, i) => {
          const p = spring({ frame: frame - 40 - i * 4, fps, config: { damping: 10, stiffness: 180 } });
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                transform: `translateY(${(1 - p) * 40}px) scale(${0.3 + 0.7 * p})`,
                opacity: Math.min(1, p * 2),
                color: w.hot ? C.red : C.ink,
              }}
            >
              {w.t}
            </span>
          );
        })}
      </div>
    </div>
  );
};

/* ---------------- flash ---------------- */

const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [LAND, LAND + 2, LAND + 10], [0, 0.55, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <AbsoluteFill style={{ background: "#FFF6CC", opacity: o, pointerEvents: "none" }} />;
};

export const ModoFriday: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background />
      <FloaterLayer back />
      <Confetti />
      <Shockwaves />
      <FloaterLayer back={false} />
      <Logo />
      <Subtitle />
      <Flash />
    </AbsoluteFill>
  );
};
