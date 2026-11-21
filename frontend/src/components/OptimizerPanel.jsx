import s from './OptimizerPanel.module.css'

export default function OptimizerPanel({ stats, rawTac, optimizedTac }) {
  if (!stats) {
    return <p className={s.empty}>Run the compiler to view optimization metrics.</p>
  }

  const rawCount = rawTac?.length || 0
  const optCount = optimizedTac?.length || 0
  const instructionsSaved = Math.max(0, rawCount - optCount)
  const reductionPercent = rawCount > 0 ? Math.round((instructionsSaved / rawCount) * 100) : 0

  return (
    <div className={s.wrap}>
      {/* KPI Cards */}
      <div className={s.kpiGrid}>
        <div className={s.kpiCard}>
          <div className={s.kpiTop}>
            <span className={s.kpiIcon}>⚡</span>
            <span className={s.kpiLabel}>Constants Folded</span>
          </div>
          <span className={s.kpiValue} style={{ color: '#00ff9d' }}>
            {stats.constants_folded}
          </span>
          <span className={s.kpiSub}>Static math evaluated at compile-time</span>
        </div>

        <div className={s.kpiCard}>
          <div className={s.kpiTop}>
            <span className={s.kpiIcon}>✂️</span>
            <span className={s.kpiLabel}>Dead Branches Pruned</span>
          </div>
          <span className={s.kpiValue} style={{ color: '#ff7733' }}>
            {stats.dead_branches_pruned}
          </span>
          <span className={s.kpiSub}>Unreachable conditions discarded</span>
        </div>

        <div className={s.kpiCard}>
          <div className={s.kpiTop}>
            <span className={s.kpiIcon}>📉</span>
            <span className={s.kpiLabel}>TAC Instructions Saved</span>
          </div>
          <span className={s.kpiValue} style={{ color: '#38bdf8' }}>
            {instructionsSaved}
          </span>
          <span className={s.kpiSub}>From {rawCount} down to {optCount}</span>
        </div>

        <div className={s.kpiCard}>
          <div className={s.kpiTop}>
            <span className={s.kpiIcon}>🚀</span>
            <span className={s.kpiLabel}>Code Reduction Rate</span>
          </div>
          <span className={s.kpiValue} style={{ color: '#f472b6' }}>
            {reductionPercent}%
          </span>
          <div className={s.progressBar}>
            <div className={s.progressFill} style={{ width: `${Math.min(reductionPercent, 100)}%` }} />
          </div>
        </div>
      </div>

      {/* Optimization Audit Log */}
      <div className={s.logSection}>
        <div className={s.logTitle}>
          <span className={s.logBadge}>PASS 1</span>
          <span>Constant Folding & Control Flow Optimization Audit Log ({stats.log?.length || 0})</span>
        </div>
        {stats.log && stats.log.length > 0 ? (
          <div className={s.logList}>
            {stats.log.map((entry, idx) => (
              <div key={idx} className={s.logItem}>
                <span className={s.logCheck}>✓</span>
                <span className={s.logText}>{entry}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className={s.noLogText}>
            Code contains no static constant operations to fold. Dynamic execution preserved.
          </p>
        )}
      </div>

      {/* Comparison: Raw vs Optimized TAC */}
      <div className={s.tacCompare}>
        <div className={s.col}>
          <div className={s.colHeader}>
            <span>Raw TAC (Before Optimization)</span>
            <span className={s.badgeRaw}>{rawCount} instrs</span>
          </div>
          <div className={s.tacList}>
            {rawTac && rawTac.map((t, i) => (
              <div key={i} className={s.tacLine}>
                <span className={s.lineNum}>{i + 1}</span>
                <span className={s.lineCode}>{t.text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={s.col}>
          <div className={s.colHeader}>
            <span>Optimized TAC (Emitted)</span>
            <span className={s.badgeOpt}>{optCount} instrs</span>
          </div>
          <div className={s.tacList}>
            {optimizedTac && optimizedTac.map((t, i) => (
              <div key={i} className={s.tacLine}>
                <span className={s.lineNum}>{i + 1}</span>
                <span className={s.lineCode} style={{ color: '#00ff9d', fontWeight: 600 }}>{t.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
