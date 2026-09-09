import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import EdgeNetwork from './EdgeNetwork'

export default function HeroScene({ projekti, onSelect, reduced, mobile, theme = 'dark' }) {
  return (
    <Canvas
      className="hero__canvas"
      dpr={[1, 1.75]}
      gl={{ antialias: true, powerPreference: 'high-performance' }}
      camera={{ position: [0, mobile ? 0.7 : 1.2, mobile ? 11 : 9.1], fov: mobile ? 46 : 40 }}
      frameloop={reduced ? 'demand' : 'always'}
    >
      <Suspense fallback={null}>
        <EdgeNetwork
          projekti={projekti}
          onSelect={onSelect}
          reduced={reduced}
          mobile={mobile}
          theme={theme}
        />
      </Suspense>
    </Canvas>
  )
}
