import { useEffect, useRef } from 'react'

export default function ParticleCanvas({ isLight }) {
  const canvasRef = useRef(null)
  const stateRef  = useRef({ isLight, animId: null })

  useEffect(() => {
    stateRef.current.isLight = isLight
  }, [isLight])

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx    = canvas.getContext('2d')
    let   mouse  = { x: 0, y: 0 }

    function resize() {
      canvas.width  = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    const onMouse = e => { mouse.x = e.clientX; mouse.y = e.clientY }
    window.addEventListener('mousemove', onMouse)

    /* ── Particles ── */
    const COUNT = 70
    const particles = Array.from({ length: COUNT }, () => ({
      x:   Math.random() * window.innerWidth,
      y:   Math.random() * window.innerHeight,
      z:   Math.random() * 400 + 80,
      vx:  (Math.random() - 0.5) * 0.35,
      vy:  (Math.random() - 0.5) * 0.35,
      vz:  (Math.random() - 0.5) * 0.55,
      r:   Math.random() * 1.6 + 0.5,
      hue: Math.random() > 0.5 ? 187 : 272,   // cyan vs violet
    }))

    /* ── Floating code glyphs ── */
    const GLYPHS = ['let', 'rakho', 'jabtak', 'agar', 'dikhao', 'while', 'if', 't1', 'L1', '==', '&&', '||', '{}', ';']
    const glyphs = Array.from({ length: 18 }, () => ({
      text: GLYPHS[Math.floor(Math.random() * GLYPHS.length)],
      x:    Math.random() * window.innerWidth,
      y:    Math.random() * window.innerHeight,
      vy:   -(Math.random() * 0.4 + 0.1),
      alpha: Math.random() * 0.12 + 0.03,
      size: Math.floor(Math.random() * 6) + 10,
    }))

    let t = 0
    function draw() {
      stateRef.current.animId = requestAnimationFrame(draw)
      t++

      const W     = canvas.width
      const H     = canvas.height
      const fovX  = W / 2
      const fovY  = H / 2
      const dark  = !stateRef.current.isLight

      ctx.clearRect(0, 0, W, H)

      /* ── Perspective grid ── */
      const gridAlpha = dark ? 0.045 : 0.06
      ctx.lineWidth   = 0.5

      const wobble = Math.sin(t * 0.003) * 30
      for (let gx = -7; gx <= 7; gx++) {
        const x0 = fovX + (gx * 70 + mouse.x * -0.012 + wobble) * 0.85
        const x1 = fovX + (gx * 240 + mouse.x * -0.022 + wobble) * 0.85
        const g   = ctx.createLinearGradient(x0, 0, x1, H)
        g.addColorStop(0,   `rgba(${dark?'0,220,255':'0,80,200'},0)`)
        g.addColorStop(0.4, `rgba(${dark?'0,220,255':'0,80,200'},${gridAlpha})`)
        g.addColorStop(1,   `rgba(${dark?'0,220,255':'0,80,200'},0)`)
        ctx.strokeStyle = g
        ctx.beginPath(); ctx.moveTo(x0, 0); ctx.lineTo(x1, H); ctx.stroke()
      }
      for (let gy = 0; gy <= 10; gy++) {
        const fy = gy / 10
        const spread = (fy + 0.15) * 0.9
        const xL = fovX - 520 * spread + mouse.x * -0.008
        const xR = fovX + 520 * spread + mouse.x * -0.008
        const yy = fy * H + mouse.y * 0.006
        ctx.strokeStyle = `rgba(${dark?'0,220,255':'0,80,200'},${gridAlpha * (0.3 + fy * 0.7)})`
        ctx.beginPath(); ctx.moveTo(xL, yy); ctx.lineTo(xR, yy); ctx.stroke()
      }

      /* ── Particles ── */
      particles.forEach(p => {
        p.x += p.vx + mouse.x * 0.00006
        p.y += p.vy + mouse.y * 0.00006
        p.z += p.vz
        if (p.x < 0)   p.x = W
        if (p.x > W)   p.x = 0
        if (p.y < 0)   p.y = H
        if (p.y > H)   p.y = 0
        if (p.z < 40)  p.z = 500
        if (p.z > 540) p.z = 40

        const scale = 380 / p.z
        const px    = fovX + (p.x - fovX) * scale
        const py    = fovY + (p.y - fovY) * scale
        const r     = Math.max(0.3, p.r * scale * 1.4)
        const alpha = dark
          ? (1 - p.z / 540) * 0.75
          : (1 - p.z / 540) * 0.55

        ctx.beginPath()
        ctx.arc(px, py, r, 0, Math.PI * 2)
        ctx.fillStyle = `hsla(${p.hue},100%,${dark ? 72 : 42}%,${alpha})`
        ctx.fill()
      })

      /* ── Connecting lines ── */
      ctx.lineWidth = 0.6
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx   = particles[i].x - particles[j].x
          const dy   = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 130) {
            const a = (1 - dist / 130) * (dark ? 0.18 : 0.10)
            ctx.strokeStyle = `rgba(${dark ? '0,200,255' : '0,60,180'},${a})`
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      /* ── Floating glyphs ── */
      ctx.font = `400 12px 'JetBrains Mono', monospace`
      glyphs.forEach(g => {
        g.y += g.vy
        if (g.y < -20) { g.y = H + 20; g.x = Math.random() * W }
        ctx.fillStyle = dark
          ? `rgba(0,220,255,${g.alpha})`
          : `rgba(0,60,180,${g.alpha * 0.7})`
        ctx.fillText(g.text, g.x, g.y)
      })
    }

    draw()

    return () => {
      cancelAnimationFrame(stateRef.current.animId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMouse)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed', inset: 0, zIndex: 0,
        pointerEvents: 'none', display: 'block',
      }}
    />
  )
}