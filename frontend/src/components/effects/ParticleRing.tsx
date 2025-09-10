import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Sphere } from "@react-three/drei";
import { pointsInner, pointsOuter, pointsMiddle, pointsScattered } from "../../lib/particleUtils";
import { Group } from "three";

interface ParticleRingProps {
  className?: string;
  autoRotate?: boolean;
  interactive?: boolean;
  height?: string;
  cameraPosition?: [number, number, number];
  ambientIntensity?: number;
  showHint?: boolean;
  hintText?: string;
}

const ParticleRing: React.FC<ParticleRingProps> = ({
  className = "",
  autoRotate = true,
  interactive = false,
  height = "100%",
  cameraPosition = [10, -7.5, -5],
  ambientIntensity = 0.3,
  showHint = false,
  hintText = "Drag & Zoom"
}) => {
  return (
    <div className={`relative ${className}`} style={{ pointerEvents: interactive ? 'auto' : 'none' }}>
      <Canvas
        camera={{
          position: cameraPosition,
        }}
        style={{ height }}
        className="bg-transparent"
      >
        {interactive && (
          <OrbitControls
            maxDistance={20}
            minDistance={10}
            enableDamping={true}
            dampingFactor={0.05}
            autoRotate={autoRotate}
            autoRotateSpeed={0.8}
          />
        )}

        {/* 環境光照 - 創造柔和的整體照明 */}
        <ambientLight intensity={ambientIntensity} />

        {/* 主要方向光 - 創造深度感 */}
        <directionalLight
          position={[5, 5, 5]}
          intensity={0.4}
          color="#ffffff"
        />

        {/* 側面填充光 */}
        <pointLight
          position={[-10, 0, -10]}
          intensity={0.2}
          color="#3b82f6"
          distance={30}
        />

        {/* 背面柔光 */}
        <pointLight
          position={[0, 10, -20]}
          intensity={0.15}
          color="#8b5cf6"
          distance={25}
        />

        <PointCircle autoRotate={autoRotate} interactive={interactive} />
      </Canvas>

      {/* 互動提示文字 */}
      {interactive && showHint && (
        <h1 className="absolute top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] text-slate-200 font-medium text-2xl md:text-5xl pointer-events-none opacity-60 select-none">
          {hintText}
        </h1>
      )}
    </div>
  );
};

interface PointCircleProps {
  autoRotate: boolean;
  interactive: boolean;
}

const PointCircle: React.FC<PointCircleProps> = ({ autoRotate, interactive }) => {
  const ref = useRef<Group | null>(null);

  useFrame(({ clock }) => {
    if (ref.current && autoRotate) {
      // 當 OrbitControls 沒有處理自動旋轉時，添加備用旋轉
      // 這主要是為了非交互模式或作為額外的動畫層
      if (!interactive) {
        // 緩慢旋轉，創造優雅的動態效果
        ref.current.rotation.z = clock.getElapsedTime() * 0.03;
        ref.current.rotation.y = clock.getElapsedTime() * 0.01;
      }

      // 添加輕微的上下浮動（始終存在）
      ref.current.position.y = Math.sin(clock.getElapsedTime() * 0.5) * 0.2;
    }
  });

  return (
    <group ref={ref}>
      {/* 內圈粒子 - 較亮、較大 */}
      {pointsInner.map((point) => (
        <Point
          key={point.idx}
          position={point.position}
          color={point.color}
          size={0.11}
          emissiveIntensity={0.65}
          roughness={0.3}
        />
      ))}

      {/* 中圈粒子 - 中等亮度和大小 */}
      {pointsMiddle.map((point) => (
        <Point
          key={point.idx}
          position={point.position}
          color={point.color}
          size={0.09}
          emissiveIntensity={0.5}
          roughness={0.4}
        />
      ))}

      {/* 外圈粒子 - 較暗、較小，創造深度 */}
      {pointsOuter.map((point) => (
        <Point
          key={point.idx}
          position={point.position}
          color={point.color}
          size={0.075}
          emissiveIntensity={0.4}
          roughness={0.5}
        />
      ))}

      {/* 散布粒子 - 最小、最暗，填充空間 */}
      {pointsScattered.map((point) => (
        <Point
          key={point.idx}
          position={point.position}
          color={point.color}
          size={0.06}
          emissiveIntensity={0.3}
          roughness={0.6}
        />
      ))}
    </group>
  );
};

interface PointProps {
  position: number[];
  color: string;
  size?: number;
  emissiveIntensity?: number;
  roughness?: number;
}

const Point: React.FC<PointProps> = ({
  position,
  color,
  size = 0.1,
  emissiveIntensity = 0.5,
  roughness = 0.5
}) => {
  const ref = useRef<any>(null);

  // 添加個別粒子的微妙動畫
  useFrame(({ clock }) => {
    if (ref.current) {
      // 每個粒子都有獨特的脈動頻率
      const uniqueFreq = (position[0] + position[1] + position[2]) * 0.1;
      const scale = 1 + Math.sin(clock.getElapsedTime() * 2 + uniqueFreq) * 0.1;
      ref.current.scale.setScalar(scale);
    }
  });

  return (
    // @ts-expect-error - Passing a num array as opposed to a Vector3 is acceptable
    // and the referenced method in the documentation
    <Sphere ref={ref} position={position} args={[size, 16, 16]}>
      <meshStandardMaterial
        emissive={color}
        emissiveIntensity={emissiveIntensity}
        roughness={roughness}
        metalness={0.1}
        color={color}
        transparent={true}
        opacity={0.9}
      />
    </Sphere>
  );
};

export default ParticleRing;
