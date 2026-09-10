import { useMemo, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Grid, Html, Line, OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

const HUB = new THREE.Vector3(0, 0, 0)
const CLOUD_POS = new THREE.Vector3(0.6, 2.95, -5.5)

/* На уском екрану платно је ниско, па ознаке имају мало пиксела по јединици
   висине. Зато се распоред тамо сабије водоравно (да ознаке остану у кадру) и
   развуче усправно (да се не преклапају). Мења се само положај чворова —
   не и размера самих тела, да не постану јајаста.

   MOB_Y је спуштен са 1.3 на 1.15 кад је сцена добила једанаести чвор. Основни
   усправни распон је тада проширен са −1.9…1.7 на −2.4…1.75, па мобилни
   распоред и са мањим множиоцем даје практично исти размак између ознака као
   пре (0.41 × 1.15 ≈ 0.47). Без тога би најнижи чвор пробио под. */
const MOB_XZ = 0.78
const MOB_Y = 1.15
const pozicijaZa = (poz, mobile) =>
  mobile ? [poz[0] * MOB_XZ, poz[1] * MOB_Y, poz[2] * MOB_XZ] : poz

/* --- један чвор = један пројекат ---------------------------------------- */
function Node({ p, onSelect, showLabel = true, isLight = false, mobile = false }) {
  const ref = useRef()
  const [hover, setHover] = useState(false)

  useFrame((state, dt) => {
    if (!ref.current) return
    const target = hover ? 1.22 : 1
    ref.current.scale.setScalar(THREE.MathUtils.damp(ref.current.scale.x, target, 8, dt))
    ref.current.rotation.y += dt * 0.25
  })

  return (
    <group position={pozicijaZa(p.pozicija, mobile)}>
      <mesh
        ref={ref}
        onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer' }}
        onPointerOut={() => { setHover(false); document.body.style.cursor = '' }}
        onClick={(e) => { e.stopPropagation(); onSelect(p.slug) }}
      >
        <icosahedronGeometry args={[0.42, 0]} />
        <meshStandardMaterial
          color={isLight ? '#FFFFFF' : '#0f2a22'}
          emissive={p.boja}
          emissiveIntensity={hover ? 1.2 : (isLight ? 0.75 : 0.5)}
          roughness={0.3}
          metalness={0.2}
          flatShading
        />
      </mesh>
      <lineSegments scale={1.001}>
        <edgesGeometry args={[new THREE.IcosahedronGeometry(0.42, 0)]} />
        <lineBasicMaterial color={p.boja} transparent opacity={hover ? 0.95 : (isLight ? 0.75 : 0.5)} />
      </lineSegments>

      {/* Ознака је HTML који се увећава како чвор прилази камери. Сцена се
          врти, па се пре или касније свака два чвора нађу близу на екрану —
          ниједан распоред чворова то не решава на сваком углу ротације. Једино
          што делује свуда је мања ознака. Од дванаестог пројекта висински
          размак је 0.38 (испод правила 0.4), па је distanceFactor спуштен на
          5.3 — однос величина-ознаке/размак остаје као код провереног
          распореда од 11 чворова (0.41 размак, distanceFactor 6.0). */}
      {showLabel && (
        <Html
          position={[0, 0.72, 0]}
          center
          distanceFactor={mobile ? 5.9 : 5.3}
          zIndexRange={[10, 0]}
          wrapperClass="node-label-wrap"
        >
          <div
            className={`node-label${hover ? ' is-hover' : ''}${mobile ? ' node-label--sm' : ''}`}
            onPointerOver={() => setHover(true)}
            onPointerOut={() => setHover(false)}
          >
            <button className="node-label__name" onClick={() => onSelect(p.slug)}>
              <b>{p.broj}</b> {p.cvor || p.naziv}
            </button>
            {p.repo && (
              <a
                className="node-label__repo"
                href={p.repo}
                target="_blank"
                rel="noreferrer"
                title="Изворни кôд на GitHub-у"
                onClick={(e) => e.stopPropagation()}
              >
                кôд ↗
              </a>
            )}
          </div>
        </Html>
      )}
    </group>
  )
}

/* --- импулс података који путује чвор ⇄ модел -------------------------- */
function Pulse({ from, phase, speed, reduced, isLight = false }) {
  const ref = useRef()
  const a = useMemo(() => new THREE.Vector3(...from), [from])
  useFrame((state) => {
    if (!ref.current) return
    const t = reduced ? 0.5 : (state.clock.elapsedTime * speed + phase) % 1
    const k = t < 0.5 ? t * 2 : (1 - t) * 2 // ping-pong
    ref.current.position.lerpVectors(a, HUB, k)
  })
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.055, 8, 8]} />
      <meshBasicMaterial color={isLight ? '#8C6500' : '#D8AE45'} />
    </mesh>
  )
}

/* --- „облак“ горе, замрачен и неповезан -------------------------------- */
function DisconnectedCloud({ isLight = false, mobile = false }) {
  const puffs = [
    [0, 0, 0, 0.62],
    [0.62, -0.08, 0, 0.48],
    [-0.6, -0.04, 0.08, 0.44],
    [0.2, 0.3, -0.15, 0.4],
  ]
  return (
    <group position={CLOUD_POS} scale={0.85}>
      {puffs.map(([x, y, z, r], i) => (
        <mesh key={i} position={[x, y, z]}>
          <dodecahedronGeometry args={[r, 0]} />
          <meshBasicMaterial color={isLight ? '#8AA394' : '#33413A'} wireframe transparent opacity={isLight ? 0.28 : 0.32} />
        </mesh>
      ))}
      {/* прекинута веза ка облаку */}
      <Line
        points={[[0, -0.7, 0], [0, -1.7, 0]]}
        color={isLight ? '#729080' : '#3A4B41'}
        lineWidth={1}
        dashed
        dashSize={0.14}
        gapSize={0.16}
        transparent
        opacity={isLight ? 0.45 : 0.55}
      />
      {!mobile && (
        <Html position={[0, 1.05, 0]} center distanceFactor={14} wrapperClass="node-label-wrap">
          <span className="cloud-label">облак · искључен</span>
        </Html>
      )}
    </group>
  )
}

/* --- ситна прашина ----------------------------------------------------- */
function Dust({ count, reduced, isLight = false }) {
  const ref = useRef()
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 22
      arr[i * 3 + 1] = Math.random() * 9 - 2
      arr[i * 3 + 2] = (Math.random() - 0.5) * 22
    }
    return arr
  }, [count])
  useFrame((_, dt) => {
    if (ref.current && !reduced) ref.current.rotation.y += dt * 0.012
  })
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.028} color={isLight ? '#0C6146' : '#5FBA98'} transparent opacity={isLight ? 0.25 : 0.5} depthWrite={false} />
    </points>
  )
}

export default function EdgeNetwork({ projekti, onSelect, reduced = false, mobile = false, theme = 'dark' }) {
  const spin = useRef()
  const isLight = theme === 'light'
  const bgCol = isLight ? '#F5F8F6' : '#090E0C'
  const fogCol = isLight ? '#F5F8F6' : '#090E0C'

  useFrame((state, dt) => {
    if (!spin.current) return
    if (!reduced) spin.current.rotation.y += dt * 0.04
    const tx = -state.pointer.y * 0.1
    const tz = state.pointer.x * 0.1
    spin.current.rotation.x = THREE.MathUtils.damp(spin.current.rotation.x, tx, 3, dt)
    spin.current.rotation.z = THREE.MathUtils.damp(spin.current.rotation.z, tz, 3, dt)
  })

  return (
    <>
      <color attach="background" args={[bgCol]} key={bgCol} />
      <fog attach="fog" args={[fogCol, mobile ? 14 : 10, mobile ? 30 : 26]} key={fogCol} />

      <ambientLight intensity={isLight ? 0.85 : 0.4} />
      <pointLight position={[5, 6, 5]} intensity={isLight ? 1.4 : 1.5} decay={0} color={isLight ? '#4ED8A3' : '#bff0df'} />
      <pointLight position={[-6, -2, -4]} intensity={isLight ? 0.7 : 0.7} decay={0} color={isLight ? '#C99E32' : '#D8AE45'} />

      <OrbitControls
        makeDefault
        enableZoom={false}
        enablePan={false}
        enableDamping
        autoRotate={false}
        minPolarAngle={Math.PI / 3.4}
        maxPolarAngle={Math.PI / 1.85}
      />

      <Grid
        position={[0, -2.9, 0]}
        args={[40, 40]}
        cellSize={0.9}
        cellThickness={isLight ? 0.5 : 0.6}
        cellColor={isLight ? '#D6E3DC' : '#1c2b24'}
        sectionSize={4.5}
        sectionThickness={isLight ? 0.8 : 1}
        sectionColor={isLight ? '#8FBDAA' : '#14624A'}
        fadeDistance={24}
        fadeStrength={2}
        infiniteGrid
      />

      <group ref={spin} position={[0, 0.15, 0]}>
        {/* централни „модел“ */}
        <mesh>
          <octahedronGeometry args={[0.62, 0]} />
          <meshStandardMaterial
            color={isLight ? '#0C6146' : '#0e1f19'}
            emissive={isLight ? '#128662' : '#5FBA98'}
            emissiveIntensity={isLight ? 0.45 : 0.7}
            flatShading
            metalness={0.3}
            roughness={0.3}
          />
        </mesh>

        {projekti.map((p) => (
          <group key={p.slug}>
            <Line
              points={[pozicijaZa(p.pozicija, mobile), [0, 0, 0]]}
              color={isLight ? '#0C6146' : '#2f6a55'}
              lineWidth={1}
              transparent
              opacity={isLight ? 0.3 : 0.4}
            />
            <Pulse from={pozicijaZa(p.pozicija, mobile)} phase={Math.random()} speed={0.28} reduced={reduced} isLight={isLight} />
            <Node p={p} onSelect={onSelect} showLabel isLight={isLight} mobile={mobile} />
          </group>
        ))}

        <DisconnectedCloud isLight={isLight} mobile={mobile} />
        <Dust count={mobile ? 180 : 650} reduced={reduced} isLight={isLight} />
      </group>
    </>
  )
}
