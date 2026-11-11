import React, { useEffect, useMemo, useState } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { continueRender, delayRender, staticFile } from "remotion";
import logo from "./logoPaths.json";

export const GRAPHITE = "#373435"; // cor do logo +soma
export const BEGE = "#DDC6B4"; // bege rosado do fecho do vídeo antigo

// ---------- ambiente (reflexos suaves para o material brilhante) ----------
export const Env: React.FC<{ intensity?: number }> = ({ intensity = 0.6 }) => {
  const { gl, scene } = useThree();
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = intensity;
    return () => {
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, scene, intensity]);
  return null;
};

// ---------- logo +soma como tubo 3D ao longo da linha central ----------
// Caminhos 0,1,3,6 formam o "+"; o resto forma "soma".
const PLUS_IDX = [0, 1, 3, 6];
const LW = logo.width;
const LH = logo.height;

type Part = "plus" | "soma";

const buildTubes = (part: Part, width: number, thick: number) => {
  const s = width / LW;
  const r = (logo.stroke / 2) * s * thick;
  const geos: THREE.BufferGeometry[] = [];
  const caps: THREE.Vector3[] = [];
  logo.paths.forEach((p, i) => {
    if ((part === "plus") !== PLUS_IDX.includes(i)) return;
    // origem no centro do logo inteiro, y para cima
    const pts = p.map(([x, y]) => new THREE.Vector3((x - LW / 2) * s, (LH / 2 - y) * s, 0));
    const curve =
      pts.length > 2
        ? new THREE.CatmullRomCurve3(pts, false, "centripetal")
        : new THREE.LineCurve3(pts[0], pts[1]);
    const seg = Math.max(8, Math.round(curve.getLength() / (r * 0.6)));
    geos.push(new THREE.TubeGeometry(curve as THREE.Curve<THREE.Vector3>, seg, r, 20, false));
    caps.push(pts[0], pts[pts.length - 1]);
  });
  return { geos, caps, r, s };
};

export const logoPoint = (px: number, py: number, width: number) => {
  const s = width / LW;
  return new THREE.Vector3((px - LW / 2) * s, (LH / 2 - py) * s, 0);
};

export const LogoTube: React.FC<{
  part: Part;
  width: number;
  thick?: number;
  color?: string;
  castShadow?: boolean;
}> = ({ part, width, thick = 1.35, color = GRAPHITE, castShadow = true }) => {
  const { geos, caps, r } = useMemo(() => buildTubes(part, width, thick), [part, width, thick]);
  const mat = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color,
        roughness: 0.32,
        metalness: 0.0,
        clearcoat: 1,
        clearcoatRoughness: 0.15,
      }),
    [color],
  );
  return (
    <group>
      {geos.map((g, i) => (
        <mesh key={i} geometry={g} material={mat} castShadow={castShadow} />
      ))}
      {caps.map((c, i) => (
        <mesh key={`c${i}`} position={c} material={mat} castShadow={castShadow}>
          <sphereGeometry args={[r, 20, 14]} />
        </mesh>
      ))}
    </group>
  );
};

// ---------- texturas de canvas (carregam o PNG do logo) ----------
const useImage = (src: string) => {
  const [img, setImg] = useState<HTMLImageElement | null>(null);
  const [handle] = useState(() => delayRender(`img ${src}`));
  useEffect(() => {
    const i = new Image();
    i.onload = () => {
      setImg(i);
      continueRender(handle);
    };
    i.src = src;
  }, [src, handle]);
  return img;
};

// Corpo do dirigível: esfera com polos no eixo Y, depois girada para ficar deitada.
// u=0,25 é o lado virado para a câmera; o logo é desenhado girado 90° no canvas.
export const useBlimpTexture = () => {
  const img = useImage(staticFile("soma/logo_soma_branco.png"));
  return useMemo(() => {
    if (!img) return null;
    const c = document.createElement("canvas");
    c.width = 2048;
    c.height = 1024;
    const ctx = c.getContext("2d")!;
    const g = ctx.createLinearGradient(0, 0, 2048, 0);
    g.addColorStop(0, "#2b292a");
    g.addColorStop(0.5, "#3a3738");
    g.addColorStop(1, "#2b292a");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 2048, 1024);
    // faixa bege nas pontas (nariz e cauda)
    ctx.fillStyle = BEGE;
    ctx.fillRect(0, 0, 2048, 40);
    ctx.fillRect(0, 984, 2048, 40);
    // logo: leitura ao longo de v (para baixo no canvas), "para cima" do logo = +u (direita)
    const lw = 760; // comprimento do logo em px de canvas (ao longo do corpo)
    const lh = (lw * img.height) / img.width;
    ctx.save();
    ctx.translate(0.25 * 2048, 512);
    ctx.rotate(Math.PI / 2);
    // após a rotação, eixo x local aponta para baixo (v = leitura) e y local para a esquerda (-u = "baixo" do logo)
    ctx.drawImage(img, -lw / 2, -lh / 2, lw, lh);
    ctx.restore();
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    return t;
  }, [img]);
};

// ---------- dirigível ----------
// a textura é criada FORA do ThreeCanvas (no componente da cena) para o render esperar o PNG
export const Blimp: React.FC<{ frame: number; length?: number; tex: THREE.Texture }> = ({ frame, length = 2.4, tex }) => {
  const R = length * 0.19;
  const fin = useMemo(() => {
    const sh = new THREE.Shape();
    sh.moveTo(0, 0);
    sh.lineTo(0.2 * length, 0);
    sh.lineTo(0.27 * length, 0.16 * length);
    sh.lineTo(0.17 * length, 0.16 * length);
    sh.closePath();
    return new THREE.ExtrudeGeometry(sh, {
      depth: 0.012 * length,
      bevelEnabled: true,
      bevelSize: 0.006 * length,
      bevelThickness: 0.006 * length,
      bevelSegments: 2,
    });
  }, [length]);
  const finMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: BEGE, roughness: 0.5 }),
    [],
  );
  return (
    <group>
      <mesh rotation={[0, 0, Math.PI / 2]} scale={[R, length / 2, R]} castShadow>
        <sphereGeometry args={[1, 96, 64]} />
        <meshPhysicalMaterial map={tex} roughness={0.45} clearcoat={0.25} clearcoatRoughness={0.4} />
      </mesh>
      {/* gôndola */}
      <mesh position={[-0.02 * length, -R * 1.0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <capsuleGeometry args={[R * 0.14, length * 0.12, 8, 16]} />
        <meshStandardMaterial color="#5a5556" roughness={0.4} />
      </mesh>
      <mesh position={[-0.02 * length, -R * 1.02, R * 0.165]} rotation={[0, 0, Math.PI / 2]}>
        <planeGeometry args={[R * 0.12, length * 0.13]} />
        <meshStandardMaterial color="#1c2833" roughness={0.1} metalness={0.4} />
      </mesh>
      {/* aletas em cruz na cauda */}
      {[0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2].map((a, i) => (
        <group key={i} position={[length * 0.22, 0, 0]} rotation={[a, 0, 0]}>
          <mesh geometry={fin} material={finMat} position={[0, R * 0.45, -0.006 * length]} />
        </group>
      ))}
      {/* hélices */}
      {[-1, 1].map((sd) => (
        <group key={sd} position={[-0.02 * length, -R * 0.9, sd * R * 0.42]}>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[R * 0.06, R * 0.07, R * 0.3, 12]} />
            <meshStandardMaterial color="#2a2a2a" />
          </mesh>
          <mesh position={[-R * 0.17, 0, 0]} rotation={[frame * 1.3, 0, 0]}>
            <boxGeometry args={[R * 0.01, R * 0.36, R * 0.03]} />
            <meshStandardMaterial color="#888" transparent opacity={0.55} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

// ---------- paraquedas (velame redondo em gomos bege/grafite) ----------
const useCanopyTexture = () =>
  useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 1024;
    c.height = 256;
    const ctx = c.getContext("2d")!;
    const gores = 12;
    for (let i = 0; i < gores; i++) {
      ctx.fillStyle = i % 2 === 0 ? BEGE : "#F4EEE8";
      ctx.fillRect((i * 1024) / gores, 0, 1024 / gores + 1, 256);
    }
    // borda grafite
    ctx.fillStyle = GRAPHITE;
    ctx.fillRect(0, 236, 1024, 20);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);

export const Canopy: React.FC<{ radius: number; open?: number; frame: number }> = ({ radius, open = 1, frame }) => {
  const tex = useCanopyTexture();
  const theta = 1.15;
  // leve "respiração" do tecido
  const breathe = 1 + Math.sin(frame * 0.25) * 0.02;
  return (
    <group scale={[radius * open * breathe, radius * (0.55 + 0.15 * open), radius * open * breathe]}>
      <mesh castShadow>
        <sphereGeometry args={[1, 64, 24, 0, Math.PI * 2, 0, theta]} />
        <meshStandardMaterial map={tex} side={THREE.DoubleSide} roughness={0.85} />
      </mesh>
    </group>
  );
};

// cordas: de pontos na borda do velame até o ponto de carga
export const Lines: React.FC<{ top: THREE.Vector3[]; bottom: THREE.Vector3; opacity?: number }> = ({
  top,
  bottom,
  opacity = 1,
}) => {
  const geo = useMemo(() => {
    const arr: number[] = [];
    top.forEach((p) => arr.push(p.x, p.y, p.z, bottom.x, bottom.y, bottom.z));
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(arr, 3));
    return g;
  }, [top, bottom]);
  return (
    <lineSegments geometry={geo}>
      <lineBasicMaterial color="#efe9e2" transparent opacity={0.85 * opacity} />
    </lineSegments>
  );
};

export const rimPoints = (radius: number, yRim: number, n = 12) =>
  Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2;
    return new THREE.Vector3(Math.cos(a) * radius, yRim, Math.sin(a) * radius);
  });
