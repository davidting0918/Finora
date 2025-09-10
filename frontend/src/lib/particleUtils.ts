/**
 * 3D 粒子環工具函數
 * 生成適配 Finora 色彩主題的粒子點座標
 */

import * as THREE from 'three'

// 匹配應用主題的顏色配置
const FINORA_COLORS = {
  blue: {
    primary: '#3b82f6',   // blue-500
    secondary: '#2563eb', // blue-600
    tertiary: '#1d4ed8',  // blue-700
  },
  purple: {
    primary: '#8b5cf6',   // purple-500
    secondary: '#7c3aed', // purple-600
    tertiary: '#6d28d9',  // purple-700
  },
  emerald: {
    primary: '#10b981',   // emerald-500
    secondary: '#059669',  // emerald-600
    tertiary: '#047857',   // emerald-700
  },
  slate: {
    primary: '#64748b',   // slate-500
    secondary: '#475569',  // slate-600
    tertiary: '#334155',   // slate-700
  }
}

export interface ParticlePoint {
  idx: number
  position: [number, number, number]
  color: string
}

/**
 * 生成內圈粒子點（較小半徑，更密集）
 */
export const generateInnerPoints = (count: number = 120): ParticlePoint[] => {
  const points: ParticlePoint[] = []
  const colors = [
    FINORA_COLORS.blue.primary,
    FINORA_COLORS.blue.secondary,
    FINORA_COLORS.purple.primary,
    FINORA_COLORS.purple.secondary,
    FINORA_COLORS.emerald.primary,
    FINORA_COLORS.slate.primary,
  ]

  for (let i = 0; i < count; i++) {
    // 使用多層圓形分佈創建自然的星雲效果
    const layer = Math.floor(i / (count / 6)) // 6 個不同層次
    const radius = 2.2 + layer * 0.6 // 內圈半徑範圍 2.2 - 5.2

    // 黃金角度分佈，避免重複模式
    const angle = i * 137.5 * (Math.PI / 180) // 黃金角度
    const height = (Math.random() - 0.5) * 1.5 // 垂直變化

    // 添加一些隨機性讓分佈更自然
    const radiusVariation = radius + (Math.random() - 0.5) * 0.5
    const heightVariation = height + (Math.random() - 0.5) * 0.3

    const x = Math.cos(angle) * radiusVariation
    const z = Math.sin(angle) * radiusVariation
    const y = heightVariation

    // 基於位置選擇顏色，創造漸層效果
    const colorIndex = Math.floor((layer + (i % 3)) % colors.length)

    points.push({
      idx: i,
      position: [x, y, z],
      color: colors[colorIndex]
    })
  }

  return points
}

/**
 * 生成外圈粒子點（較大半徑，較稀疏）
 */
export const generateOuterPoints = (count: number = 90): ParticlePoint[] => {
  const points: ParticlePoint[] = []
  const colors = [
    FINORA_COLORS.blue.secondary,
    FINORA_COLORS.blue.tertiary,
    FINORA_COLORS.purple.secondary,
    FINORA_COLORS.purple.tertiary,
    FINORA_COLORS.emerald.secondary,
    FINORA_COLORS.slate.secondary,
  ]

  for (let i = 0; i < count; i++) {
    // 外圈使用更大的半徑和更多的垂直變化
    const layer = Math.floor(i / (count / 5)) // 5 個層次
    const radius = 5.8 + layer * 0.8 // 外圈半徑範圍 5.8 - 9.0

    // 使用費波納契螺旋分佈
    const goldenRatio = (1 + Math.sqrt(5)) / 2
    const angle = i / goldenRatio * 2 * Math.PI
    const height = (Math.random() - 0.5) * 2.5 // 更大的垂直變化

    // 外圈粒子更加分散
    const radiusVariation = radius + (Math.random() - 0.5) * 1.0
    const heightVariation = height + (Math.random() - 0.5) * 0.8

    const x = Math.cos(angle) * radiusVariation
    const z = Math.sin(angle) * radiusVariation
    const y = heightVariation

    // 外圈使用較深的顏色
    const colorIndex = Math.floor((layer + (i % 2)) % colors.length)

    points.push({
      idx: i + 1000, // 避免與內圈重複
      position: [x, y, z],
      color: colors[colorIndex]
    })
  }

  return points
}

/**
 * 生成中圈粒子點（介於內外圈之間）
 */
export const generateMiddlePoints = (count: number = 45): ParticlePoint[] => {
  const points: ParticlePoint[] = []
  const colors = [
    FINORA_COLORS.blue.tertiary,
    FINORA_COLORS.purple.tertiary,
    FINORA_COLORS.emerald.tertiary,
    FINORA_COLORS.slate.tertiary,
  ]

  for (let i = 0; i < count; i++) {
    // 中圈半徑範圍
    const layer = Math.floor(i / (count / 3)) // 3 個層次
    const radius = 4.5 + layer * 0.7 // 中圈半徑範圍 4.5 - 5.9

    // 使用不同的角度分佈避免與內外圈重疊
    const angle = (i * 222.5 + 45) * (Math.PI / 180) // 偏移 45 度
    const height = (Math.random() - 0.5) * 2.0 // 垂直變化

    // 添加變化
    const radiusVariation = radius + (Math.random() - 0.5) * 0.6
    const heightVariation = height + (Math.random() - 0.5) * 0.4

    const x = Math.cos(angle) * radiusVariation
    const z = Math.sin(angle) * radiusVariation
    const y = heightVariation

    const colorIndex = Math.floor((layer + i) % colors.length)

    points.push({
      idx: i + 500, // 避免與其他環重複
      position: [x, y, z],
      color: colors[colorIndex]
    })
  }

  return points
}

/**
 * 生成散布粒子點（隨機分佈在整個空間）
 */
export const generateScatteredPoints = (count: number = 30): ParticlePoint[] => {
  const points: ParticlePoint[] = []
  const colors = [
    FINORA_COLORS.slate.primary,
    FINORA_COLORS.slate.secondary,
    FINORA_COLORS.blue.tertiary,
    FINORA_COLORS.purple.tertiary,
  ]

  for (let i = 0; i < count; i++) {
    // 隨機分佈在 2-10 半徑範圍內
    const radius = 2 + Math.random() * 8
    const angle = Math.random() * 2 * Math.PI
    const height = (Math.random() - 0.5) * 3

    const x = Math.cos(angle) * radius
    const z = Math.sin(angle) * radius
    const y = height

    const colorIndex = Math.floor(Math.random() * colors.length)

    points.push({
      idx: i + 1500, // 避免與其他環重複
      position: [x, y, z],
      color: colors[colorIndex]
    })
  }

  return points
}

// 預生成的粒子點，提高性能
export const pointsInner = generateInnerPoints()
export const pointsOuter = generateOuterPoints()
export const pointsMiddle = generateMiddlePoints()
export const pointsScattered = generateScatteredPoints()

/**
 * 生成連接線的粒子點（可選功能）
 */
export const generateConnectionPoints = (innerPoints: ParticlePoint[], outerPoints: ParticlePoint[], density: number = 0.1): ParticlePoint[] => {
  const connections: ParticlePoint[] = []
  const connectionColor = FINORA_COLORS.slate.tertiary

  for (let i = 0; i < innerPoints.length; i++) {
    if (Math.random() > density) continue // 控制連接密度

    const innerPoint = innerPoints[i]
    const nearestOuter = outerPoints[Math.floor(Math.random() * outerPoints.length)]

    // 在兩點之間創建中間點
    const midX = (innerPoint.position[0] + nearestOuter.position[0]) / 2
    const midY = (innerPoint.position[1] + nearestOuter.position[1]) / 2
    const midZ = (innerPoint.position[2] + nearestOuter.position[2]) / 2

    connections.push({
      idx: 2000 + i,
      position: [midX, midY, midZ],
      color: connectionColor
    })
  }

  return connections
}

/**
 * 根據時間創建動態顏色效果
 */
export const getDynamicColor = (baseColor: string, time: number, index: number): string => {
  // 使用 HSL 色彩空間創建脈動效果
  const hue = (time * 0.5 + index * 30) % 360
  const saturation = 60 + Math.sin(time + index) * 20
  const lightness = 50 + Math.sin(time * 0.8 + index * 0.5) * 15

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`
}

export default {
  pointsInner,
  pointsOuter,
  pointsMiddle,
  pointsScattered,
  generateInnerPoints,
  generateOuterPoints,
  generateMiddlePoints,
  generateScatteredPoints,
  generateConnectionPoints,
  getDynamicColor,
  FINORA_COLORS
}
