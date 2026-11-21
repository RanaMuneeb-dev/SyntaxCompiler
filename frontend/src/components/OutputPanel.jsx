import { useEffect, useRef, useState } from 'react'
import s from './OutputPanel.module.css'

export default function OutputPanel({ output, onClear }) {
  const bottomRef = useRef(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [output])

  function handleCopy() {
    if (!output || output.length === 0) return
    const text = output.map(l => l.value).join('\n')
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!output || output.length === 0)
    return (
      <div className={s.empty}>
        <span className={s.emptyIcon}>▶</span>
        <p className={s.emptyTitle}>Console Output Idle</p>
        <p className={s.emptySub}>Run the compiler to execute the virtual machine and see outputs here.</p>
      </div>
    )

  const printCount = output.filter(l => l.type === 'print').length
  const errCount   = output.filter(l => l.type === 'error').length

  return (
    <div className={s.wrap}>
      <div className={s.termHeader}>
        <div className={s.termDots}>
          <span className={s.dot} style={{ background: '#ff5f56' }} />
          <span className={s.dot} style={{ background: '#ffbd2e' }} />
          <span className={s.dot} style={{ background: '#27c93f' }} />
        </div>
        <span className={s.termLabel}>TAC Virtual Machine Console</span>
        <div className={s.termActions}>
          <button className={s.termBtn} onClick={handleCopy} title="Copy console output">
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
        </div>
      </div>

      <div className={s.terminal}>
        <div className={s.termBanner}>
          <span>[VM Initialized] Execution Target: TAC Intermediate Representation</span>
        </div>
        {output.map((line, i) => (
          <div
            key={i}
            className={`${s.line} ${line.type === 'error' ? s.lineErr : ''}`}
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <span className={s.prompt}>
              {line.type === 'error' ? '✖' : '❯'}
            </span>
            <span className={s.lineNum}>L{line.line ?? '?'}</span>
            <span className={s.value}>{String(line.value)}</span>
          </div>
        ))}
        <div className={s.cursor} ref={bottomRef}>
          <span className={s.cursorBar}>█</span>
        </div>
      </div>

      <div className={s.footer}>
        <span className={s.footerStat}>
          ✓ {printCount} print call(s) executed
        </span>
        {errCount > 0 && (
          <span className={s.footerErr}>
            ✖ {errCount} runtime error(s)
          </span>
        )}
        <span className={s.footerRight}>Status: Exit 0 (Success)</span>
      </div>
    </div>
  )
}
