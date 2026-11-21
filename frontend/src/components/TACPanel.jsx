import { useState } from 'react'
import s from './TACPanel.module.css'

const OP_META = {
  print:    { color: '#00ff9d', label: 'PRINT'  },
  '+':      { color: '#00f5ff', label: 'ADD'    },
  '-':      { color: '#ff7733', label: 'SUB'    },
  '*':      { color: '#ffb800', label: 'MUL'    },
  '/':      { color: '#ff4466', label: 'DIV'    },
  '%':      { color: '#a855f7', label: 'MOD'    },
  '&&':     { color: '#e879f9', label: 'AND'    },
  '||':     { color: '#c084fc', label: 'OR'     },
  '!':      { color: '#f43f5e', label: 'NOT'    },
  compare:  { color: '#ff4466', label: 'CMP'    },
  label:    { color: '#38bdf8', label: 'LABEL'  },
  goto:     { color: '#fbbf24', label: 'GOTO'   },
  if_false: { color: '#f97316', label: 'BRANCH' },
  null:     { color: '#a855f7', label: 'COPY'   },
}

export default function TACPanel({ tac, title }) {
  const [search, setSearch] = useState('')

  if (!tac || tac.length === 0)
    return <p className={s.empty}>No TAC generated yet.</p>

  const filteredTac = tac.filter(instr =>
    instr.text.toLowerCase().includes(search.toLowerCase()) ||
    (instr.op && instr.op.toLowerCase().includes(search.toLowerCase())) ||
    (instr.result && instr.result.toLowerCase().includes(search.toLowerCase()))
  )

  const labelCount = tac.filter(t => t.op === 'label').length
  const jumpCount  = tac.filter(t => t.op === 'goto' || t.op === 'if_false').length

  return (
    <div className={s.wrap}>
      {/* Header Toolbar */}
      <div className={s.toolbar}>
        <div className={s.searchWrap}>
          <span className={s.searchIcon}>🔍</span>
          <input
            type="text"
            className={s.searchInput}
            placeholder="Search TAC instructions..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className={s.stats}>
          <span>Total: <strong>{tac.length}</strong></span>
          <span>Labels: <strong style={{ color: '#38bdf8' }}>{labelCount}</strong></span>
          <span>Jumps: <strong style={{ color: '#fbbf24' }}>{jumpCount}</strong></span>
        </div>
      </div>

      <div className={s.header}>
        <span>#</span>
        <span>INSTRUCTION</span>
        <span>RESULT</span>
        <span style={{ textAlign: 'center' }}>OP</span>
        <span>ARG 1</span>
        <span>ARG 2</span>
      </div>

      <div className={s.list}>
        {filteredTac.map((instr, i) => {
          const meta   = OP_META[instr.op] ?? OP_META[null]
          const isTemp = instr.result?.startsWith('t')
          const isLabel = instr.op === 'label'
          const isJump = instr.op === 'goto' || instr.op === 'if_false'

          return (
            <div
              key={i}
              className={`${s.row} ${isLabel ? s.rowLabel : ''} ${isJump ? s.rowJump : ''}`}
              style={{
                borderLeftColor: meta.color,
                animationDelay: `${Math.min(i * 15, 250)}ms`,
              }}
            >
              <span className={s.idx}>{i + 1}</span>

              <div className={s.codeCol}>
                <code className={s.text}>{instr.text}</code>
                {isJump && (
                  <span className={s.jumpTag}>
                    {instr.op === 'goto' ? '↷ unconditional' : '↳ conditional'}
                  </span>
                )}
              </div>

              <span className={s.result} style={{ color: isTemp ? '#a855f7' : (isLabel ? '#38bdf8' : 'var(--cyan)') }}>
                {instr.result !== '_' ? instr.result : '—'}
              </span>

              <span className={s.op} style={{ color: meta.color }}>
                {instr.op ?? '='}
              </span>

              <span className={s.cell}>{instr.arg1 ?? '—'}</span>
              <span className={s.cell}>{instr.arg2 ?? '—'}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
