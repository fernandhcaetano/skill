import React, { useMemo } from "react";
import * as THREE from "three";
import { ThreeCanvas } from "@remotion/three";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Blimp, Canopy, Env, Lines, LogoTube, logoPoint, rimPoints, useBlimpTexture } from "./three-parts";

// "+soma" em CGI no Rio (FOOH): dirigível com o logo sobre o Pão de Açúcar,
// pôr do sol com o "+" saltando de paraquedas e pousando no Arpoador ao lado do "soma".

export const SOMA_CGI_FPS = 30;
const S1 = 120; // dirigível, Pão de Açúcar
const S2 = 135; // pôr do sol, salto
const S3 = 135; // close no paraquedas
const S4 = 240; // pouso no Arpoador + logo completo
export const SOMA_CGI_DURATION = S1 + S2 + S3 + S4;

const W = 1080;
const H = 1920;
const CAM = { fov: 30, position: [0, 0, 10] as [number, number, number], near: 0.1, far: 100 };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Fundo + 3D na mesma "lente": o zoom lento afeta os dois juntos.
const Shot: React.FC<{
  bg: string;
  zoom: [number, number];
  bgShift?: [number, number]; // deslocamento vertical do fundo (px) para simular tilt
  grade?: string;
  children: React.ReactNode;
}> = ({ bg, zoom, bgShift = [0, 0], grade, children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = frame / durationInFrames;
  const z = interpolate(p, [0, 1], zoom);
  const shift = interpolate(p, [0, 1], bgShift, { easing: Easing.inOut(Easing.sin) });
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${z})` }}>
        <Img
          src={staticFile(bg)}
          style={{
            position: "absolute",
            width: W,
            height: H * (bgShift[0] || bgShift[1] ? 1.25 : 1),
            objectFit: "cover",
            top: bgShift[0] || bgShift[1] ? -H * 0.125 + shift : 0,
          }}
        />
        <ThreeCanvas width={W} height={H} camera={CAM} shadows gl={{ antialias: true, alpha: true }}>
          <Env />
          {children}
        </ThreeCanvas>
      </AbsoluteFill>
      {grade && <AbsoluteFill style={{ background: grade, mixBlendMode: "soft-light" }} />}
      {/* vinheta sutil */}
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at 50% 50%, transparent 60%, rgba(0,0,0,0.22) 100%)" }}
      />
    </AbsoluteFill>
  );
};

// ---------- Cena 1: dirigível passa pelo Pão de Açúcar ----------
const Scene1: React.FC = () => {
  const f = useCurrentFrame();
  const tex = useBlimpTexture();
  if (!tex) return null;
  const x = interpolate(f, [0, S1], [2.6, 0.15], { easing: Easing.out(Easing.quad) });
  const bob = Math.sin(f / 18) * 0.03;
  return (
    <Shot bg="soma/cgi/bg1_pao.jpg" zoom={[1.0, 1.05]}>
      <ambientLight intensity={0.55} />
      <hemisphereLight args={["#cfe6ff", "#3a5a40", 0.6]} />
      <directionalLight position={[-4, 6, 6]} intensity={3.2} color="#fff6e8" />
      <group position={[x, 2.0 + bob, 0]} rotation={[0.05, -0.12, Math.sin(f / 25) * 0.015]}>
        <Blimp frame={f} length={2.1} tex={tex} />
      </group>
    </Shot>
  );
};

// ---------- Cena 2: pôr do sol, o "+" salta e abre o paraquedas ----------
const Scene2: React.FC = () => {
  const f = useCurrentFrame();
  const tex = useBlimpTexture();
  const { fps } = useVideoConfig();
  const bx = interpolate(f, [0, S2], [0.9, -0.15]);
  const by = 0.62;
  const drop = 22; // frame em que solta
  const t = Math.max(0, f - drop);
  const open = spring({ frame: f - drop - 14, fps, config: { damping: 12, stiffness: 90 } });
  // queda: rápida antes de abrir, depois desce devagar com o vento
  const py = by - 0.12 - Math.min(t, 14) * 0.012 - Math.max(0, t - 14) * 0.006;
  const px = bx + 0.05 - t * 0.0015;
  if (!tex) return null;
  const plusW = 0.9; // largura do logo inteiro nesta escala
  const plus = logoPoint(50, 50, plusW);
  return (
    <Shot bg="soma/cgi/bg2_sunset.jpg" zoom={[1.0, 1.04]} grade="rgba(255,150,60,0.18)">
      <ambientLight intensity={0.35} />
      <hemisphereLight args={["#ffd2a8", "#2a2030", 0.5]} />
      {/* contraluz do sol atrás */}
      <directionalLight position={[2, 1, -6]} intensity={2.5} color="#ffb070" />
      <directionalLight position={[-3, 2, 6]} intensity={0.7} color="#ffd9c0" />
      <group position={[bx, by + Math.sin(f / 20) * 0.01, -1]} rotation={[0.05, -0.15, 0]}>
        {tex && <Blimp frame={f} length={0.62} tex={tex} />}
      </group>
      {f >= drop && (
        <group position={[px, py, -1]} rotation={[0, 0, Math.sin(f / 9) * 0.08 * open]}>
          <group position={[0, 0.14 * open, 0]}>
            <Canopy radius={0.07} open={Math.max(0.05, open)} frame={f} />
          </group>
          {open > 0.2 && (
            <Lines top={rimPoints(0.064 * open, 0.14 * open + 0.025, 10)} bottom={new THREE.Vector3(0, 0, 0)} opacity={open} />
          )}
          <group position={[-plus.x, -plus.y - 0.03, 0]} rotation={[0, f * 0.02, 0]}>
            <LogoTube part="plus" width={plusW} thick={1.8} />
          </group>
        </group>
      )}
    </Shot>
  );
};

// ---------- Cena 3: close no paraquedas descendo ----------
const Scene3: React.FC = () => {
  const f = useCurrentFrame();
  const sway = Math.sin(f / 16) * 0.12;
  const y = interpolate(f, [0, S3], [0.5, -0.35]);
  const canR = 1.25;
  const rimY = Math.cos(1.15) * canR * 0.7; // altura da borda (escala Y = 0.7)
  const rimR = Math.sin(1.15) * canR;
  const plusW = 4.6;
  const plus = logoPoint(50, 50, plusW);
  const load = new THREE.Vector3(0, -2.2, 0);
  const canopyY = 0.9;
  return (
    <Shot bg="soma/cgi/bg3_ceu.jpg" zoom={[1.02, 1.08]} bgShift={[-180, 180]}>
      <ambientLight intensity={0.5} />
      <hemisphereLight args={["#fff1dc", "#c9b8a8", 0.6]} />
      <directionalLight position={[3, 5, 5]} intensity={2.2} color="#ffe6c8" />
      <group position={[0.1, y, 0]} rotation={[0.25, f * 0.004, sway]}>
        <group position={[0, canopyY, 0]}>
          <Canopy radius={canR} frame={f} />
        </group>
        <Lines top={rimPoints(rimR, canopyY + rimY, 16)} bottom={load} />
        <group position={[load.x - plus.x, load.y - plus.y - 0.06, 0]} rotation={[0, Math.sin(f / 30) * 0.4, 0]}>
          <LogoTube part="plus" width={plusW} thick={1.8} />
        </group>
      </group>
    </Shot>
  );
};

// ---------- Cena 4: pouso no Arpoador, logo completo ----------
const LAND = 96; // frame do pouso
const Scene4: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const LW = 2.6; // largura do logo no mundo
  const base = new THREE.Vector3(0.0, 0.27, 0); // centro do logo pousado
  const plusHome = logoPoint(50, 50, LW).add(base);
  // descida: vem do alto à esquerda, curva com o vento
  const p = interpolate(f, [0, LAND], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const start = new THREE.Vector3(-1.3, 3.6, -0.5);
  const ctrl = new THREE.Vector3(0.6, 2.3, -0.2);
  const pos = new THREE.QuadraticBezierCurve3(start, ctrl, plusHome).getPoint(p);
  // aterrissagem: "squash" e volta com mola
  const landed = f >= LAND;
  const sq = landed ? spring({ frame: f - LAND, fps, config: { damping: 7, stiffness: 180 } }) : 0;
  const squash = landed ? 1 - 0.18 * (1 - sq) * Math.cos((f - LAND) / 2.5) * Math.exp(-(f - LAND) / 10) : 1;
  const swing = landed ? 0 : Math.sin(f / 10) * 0.15 * (1 - p);
  // velame: depois do pouso solta e voa para longe com o vento
  const away = Math.max(0, f - LAND - 4);
  const canopyPos = new THREE.Vector3(
    pos.x - 0.1 + away * 0.035,
    pos.y + 1.1 + away * 0.028 - (landed ? Math.min(f - LAND, 4) * 0.04 : 0),
    pos.z - away * 0.06,
  );
  const canR = 0.5;
  const linesOn = away < 6;
  // "soma" balança de leve com o impacto
  const wob = landed ? Math.sin((f - LAND) / 2) * 0.012 * Math.exp(-(f - LAND) / 12) : 0;
  // poeira/borrifo no impacto
  const puffs = useMemo(
    () =>
      Array.from({ length: 22 }, (_, i) => ({
        a: (i / 22) * Math.PI * 2 + (i % 3) * 0.3,
        sp: 0.012 + ((i * 37) % 10) * 0.0016,
        sz: 0.03 + ((i * 53) % 7) * 0.008,
      })),
    [],
  );
  const pt = f - LAND;
  return (
    <Shot bg="soma/cgi/bg4_arpoador.jpg" zoom={[1.0, 1.07]}>
      <ambientLight intensity={0.5} />
      <hemisphereLight args={["#d6ecff", "#7a7068", 0.7]} />
      <directionalLight
        position={[4, 7, 6]}
        intensity={2.6}
        color="#fff4e0"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-3}
        shadow-camera-right={3}
        shadow-camera-top={3}
        shadow-camera-bottom={-3}
        shadow-bias={-0.0005}
        shadow-radius={6}
      />
      {/* chão invisível (a pedra) que só recebe a sombra */}
      <mesh rotation={[-Math.PI / 2 + 0.06, 0, 0]} position={[0, base.y - 0.31, 0]} receiveShadow>
        <planeGeometry args={[8, 6]} />
        <shadowMaterial opacity={0.35} />
      </mesh>
      <group position={base} rotation={[0, 0, wob]}>
        <LogoTube part="soma" width={LW} thick={1.8} />
      </group>
      {/* o "+" (ancorado no próprio centro para o squash) */}
      <group position={pos} rotation={[0, 0, swing]} scale={[2 - squash, squash, 1]}>
        <group position={[-plusHome.x + base.x, -plusHome.y + base.y, 0]}>
          <LogoTube part="plus" width={LW} thick={1.8} />
        </group>
      </group>
      {/* velame */}
      {away < 120 && (
        <group position={canopyPos} rotation={[0.3 + away * 0.01, away * 0.03, swing - away * 0.012]}>
          <Canopy radius={canR} frame={f} open={1} />
        </group>
      )}
      {linesOn && (
        <Lines
          top={rimPoints(Math.sin(1.15) * canR, Math.cos(1.15) * canR * 0.7, 12).map((v) => v.clone().add(canopyPos))}
          bottom={pos}
          opacity={1 - away / 6}
        />
      )}
      {pt >= 0 &&
        pt < 30 &&
        puffs.map((d, i) => {
          const k = pt / 30;
          return (
            <mesh
              key={i}
              position={[
                plusHome.x + Math.cos(d.a) * d.sp * pt * 1.6,
                base.y - 0.27 + Math.abs(Math.sin(d.a)) * d.sp * pt * 0.6,
                Math.sin(d.a) * d.sp * pt * 0.8,
              ]}
            >
              <sphereGeometry args={[d.sz * (1 + k * 2), 10, 8]} />
              <meshStandardMaterial color="#f2efe9" transparent opacity={0.7 * (1 - k)} roughness={1} />
            </mesh>
          );
        })}
    </Shot>
  );
};

export const SomaCGI: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Sequence durationInFrames={S1}>
      <Scene1 />
    </Sequence>
    <Sequence from={S1} durationInFrames={S2}>
      <Scene2 />
    </Sequence>
    <Sequence from={S1 + S2} durationInFrames={S3}>
      <Scene3 />
    </Sequence>
    <Sequence from={S1 + S2 + S3} durationInFrames={S4}>
      <Scene4 />
    </Sequence>
    <Audio src={staticFile("soma/cgi/trilha.wav")} />
  </AbsoluteFill>
);
