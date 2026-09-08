import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import EdgeNetwork from './EdgeNetwork'

export default function HeroScene({ projekti, onSelect, reduced, mobile }) {
  return (
    <Canvas
      className="hero__canvas"
      dpr={[1, 1.75]}
      gl={{ antialias: true, powerPreference: 'high-performance' }}
      camera={{ position: [0, 1.7, mobile ? 11 : 9.2], fov: 42 }}
      frameloop={reduced ? 'demand' : 'always'}
    >
      <Suspense fallback={null}>
        <EdgeNetwork
          projekti={projekti}
          onSelect={onSelect}
          reduced={reduced}
          mobile={mobile}
        />
      </Suspense>
    </Canvas>
  )
}
