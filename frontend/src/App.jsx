import { useState, useRef, useEffect, useCallback } from 'react'
import ParticleCanvas from './components/ParticleCanvas'
import TokensPanel    from './components/TokensPanel'
import ASTPanel       from './components/ASTPanel'
import SymbolTable    from './components/SymbolTable'
import TACPanel       from './components/TACPanel'
import OptimizerPanel from './components/OptimizerPanel'
import OutputPanel    from './components/OutputPanel'
import s              from './App.module.css'

const API = 'http://localhost:8000'

const PRESETS = {
  romanUrdu: {
    name: '🇵🇰 Roman Urdu (While Loop)',
    code: `// Roman Urdu Programming
rakho n = 5;
rakho fact = 1;

/* loop calculates factorial */
jabtak (n > 1) {
  fact = fact * n;
  n = n - 1;
}

agar (fact == 120) {
  dikhao "Mubarak ho! Factorial 120 aaya hai";
} warna {
  dikhao "Error";
}

dikhao "Result:";
dikhao fact;`
  },
  fibonacci: {
    name: '🔢 Fibonacci Series',
    code: `// Fibonacci Series Generator
let a = 0;
let b = 1;
let count = 8;

print "First 8 Fibonacci numbers:";
while (count > 0) {
  print a;
  let next = a + b;
  a = b;
  b = next;
  count = count - 1;
}`
  },
  optimizer: {
    name: '⚡ Optimizer (Constant Folding)',
    code: `// Constant Folding & Branch Pruning
let a = 10 + 20 * 2;
let b = (100 / 2) - 10;
let c = "Hello " + "Syntax Summit!";

// Dead branch elimination:
if (1) {
  let active = 42;
  print active;
} else {
  let dead = 999;
  print dead;
}

print a;
print b;
print c;`
  },
  logic: {
    name: '🔍 Modulo & Logic (% && ||)',
    code: `// Even / Odd and Compound Logic
let num = 14;

if (num % 2 == 0 && num > 10) {
  print "Number is even and greater than 10";
} else {
  print "Condition not met";
}

let is_zero = !(num > 0);
print is_zero;`
  },
  basic: {
    name: '📝 Basic Sample',
    code: `let x = 10;
let y = x + 20;
let z = (x * 2) + y;
print z;
print x + y;`
  }
}

const SNIPPETS = [
  { label: '+ rakho', code: 'rakho x = 10;\n' },
  { label: '+ jabtak', code: 'jabtak (n > 0) {\n  n = n - 1;\n}\n' },
  { label: '+ agar/warna', code: 'agar (x > 0) {\n  dikhao "Positive";\n} warna {\n  dikhao "Negative";\n}\n' },
  { label: '+ dikhao', code: 'dikhao x;\n' },
  { label: '+ modulo %', code: 'x = n % 2;\n' },
]

const TABS = [
  { id: 'tokens',    label: 'Tokens',    icon: '◈', phase: '01' },
  { id: 'ast',       label: 'AST',       icon: '⬡', phase: '02' },
  { id: 'symbols',   label: 'Symbols',   icon: '◎', phase: '03' },
  { id: 'tac',       label: 'TAC',       icon: '≋', phase: '04' },
  { id: 'optimizer', label: 'Optimizer', icon: '⚡', phase: '04.5' },
  { id: 'output',    label: 'Output',    icon: '▶', phase: '05' },
]

const PHASES = ['Lexer', 'Parser', 'Semantic', 'Optimizer', 'TAC', 'Run']

export default function App() {
  const [presetKey, setPresetKey] = useState('romanUrdu')
  const [source,    setSource]    = useState(PRESETS.romanUrdu.code)
  const [result,    setResult]    = useState(null)
  const [tab,       setTab]       = useState('tokens')
  const [loading,   setLoading]   = useState(false)
  const [connErr,   setConnErr]   = useState(null)
  const [compiled,  setCompiled]  = useState(false)
  const [isLight,   setIsLight]   = useState(false)
  const [activePhase, setActivePhase] = useState(-1)
  const [execTime,  setExecTime]  = useState(null)

  const taRef = useRef(null)

  useEffect(() => {
    document.documentElement.classList.toggle('light', isLight)
  }, [isLight])

  const lineCount = source.split('\n').length

  const compile = useCallback(async () => {
    setLoading(true)
    setConnErr(null)
    setActivePhase(0)
    const startTime = performance.now()

    const phaseTick = setInterval(() => {
      setActivePhase(p => (p < PHASES.length - 1 ? p + 1 : p))
    }, 120)

    try {
      const res  = await fetch(`${API}/compile`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ source }),
      })
      const data = await res.json()
      const elapsed = Math.round(performance.now() - startTime)
      setExecTime(elapsed)
      setResult(data)
      setCompiled(true)
      if (data.success && data.output?.length > 0) {
        setTab('output')
      }
    } catch {
      setConnErr('Cannot reach compiler server on port 8000. Make sure backend is running.')
    } finally {
      clearInterval(phaseTick)
      setActivePhase(PHASES.length - 1)
      setLoading(false)
    }
  }, [source])

  function handleKey(e) {
    if (e.key === 'Tab') {
      e.preventDefault()
      const el  = taRef.current
      const st  = el.selectionStart
      const en  = el.selectionEnd
      const val = source.slice(0, st) + '  ' + source.slice(en)
      setSource(val)
      requestAnimationFrame(() => { el.selectionStart = el.selectionEnd = st + 2 })
    }
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) compile()
  }

  function insertSnippet(code) {
    const el = taRef.current
    if (!el) {
      setSource(s => s + '\n' + code)
      return
    }
    const st = el.selectionStart
    const en = el.selectionEnd
    const val = source.slice(0, st) + code + source.slice(en)
    setSource(val)
    requestAnimationFrame(() => {
      el.focus()
      el.selectionStart = el.selectionEnd = st + code.length
    })
  }

  function handleCopySource() {
    navigator.clipboard.writeText(source)
  }

  function handleClearSource() {
    setSource('')
    setResult(null)
  }

  function handleResetPreset() {
    setSource(PRESETS[presetKey].code)
    setResult(null)
  }

  const counts = {
    tokens:    result?.tokens?.length ?? 0,
    ast:       result?.ast ? '✓' : '—',
    symbols:   result?.symbol_table?.length ?? 0,
    tac:       result?.optimized_tac?.length ?? result?.tac?.length ?? 0,
    optimizer: result?.optimization_stats?.total_optimizations ?? 0,
    output:    result?.output?.filter(o => o.type === 'print').length ?? 0,
  }

  const phaseError = result?.error

  return (
    <>
      <ParticleCanvas isLight={isLight} />

      <div className={s.app}>
        {/* ── Topbar ── */}
        <header className={s.topbar}>
          <div className={s.brand}>
            <span className={s.brandBracket}>&lt;</span>
            <span className={s.brandName}>SYNTAX<span className={s.brandAccent}>COMPILER</span></span>
            <span className={s.brandBracket}>/&gt;</span>
          </div>

          <span className={s.summitBadge}>SYNTAX SUMMIT '26</span>

          {/* Preset Showcase Selector */}
          <div className={s.presetBox}>
            <span className={s.presetLabel}>Preset:</span>
            <select
              className={s.presetSelect}
              value={presetKey}
              onChange={e => {
                const key = e.target.value
                setPresetKey(key)
                setSource(PRESETS[key].code)
                setResult(null)
              }}
            >
              {Object.entries(PRESETS).map(([key, item]) => (
                <option key={key} value={key}>{item.name}</option>
              ))}
            </select>
          </div>

          {/* Phase progress indicators */}
          <div className={s.phasePills}>
            {PHASES.map((p, i) => (
              <span
                key={p}
                className={`${s.pill} ${compiled && i <= activePhase ? s.pillActive : ''}`}
                style={{ transitionDelay: `${i * 40}ms` }}
              >
                <span className={s.pillDot} />
                {p}
              </span>
            ))}
          </div>

          <div className={s.metaBar}>
            <span className={s.metaTag}>Python 3.12 · Pure VM</span>

            {/* Day / Night Animated Toggle */}
            <button
              className={`${s.themeToggle} ${isLight ? s.themeToggleLight : ''}`}
              onClick={() => setIsLight(v => !v)}
              title={isLight ? "Switch to Night Mode (Dark)" : "Switch to Day Mode (Light)"}
              aria-label="Toggle Day / Night theme"
            >
              <span className={s.toggleTrack}>
                <span className={s.toggleIconSun}>☀️</span>
                <span className={s.toggleIconMoon}>🌙</span>
                <span className={s.toggleThumb} />
              </span>
              <span className={s.toggleText}>{isLight ? 'Day' : 'Night'}</span>
            </button>
          </div>
        </header>

        {/* ── Main Grid ── */}
        <div className={s.main}>
          {/* ─ Editor column ─ */}
          <div className={s.editorCol}>
            {/* Tab header */}
            <div className={s.editorHeader}>
              <div className={s.fileTab}>
                <span className={s.fileDot} />
                <span>main.snx (Bilingual Source)</span>
              </div>
              <div className={s.editorActions}>
                <button className={s.actionBtn} onClick={handleCopySource} title="Copy code">
                  📋 Copy
                </button>
                <button className={s.actionBtn} onClick={handleResetPreset} title="Reset code">
                  ↺ Reset
                </button>
                <button className={s.actionBtn} onClick={handleClearSource} title="Clear editor">
                  🧹 Clear
                </button>
              </div>
            </div>

            {/* Quick Snippets Bar */}
            <div className={s.snippetBar}>
              <span className={s.snippetLabel}>Insert:</span>
              {SNIPPETS.map(snip => (
                <button
                  key={snip.label}
                  className={s.snippetChip}
                  onClick={() => insertSnippet(snip.code)}
                >
                  {snip.label}
                </button>
              ))}
            </div>

            {/* Editor Box */}
            <div className={s.editorBox}>
              <div className={s.gutter}>
                {Array.from({ length: lineCount }, (_, i) => (
                  <div key={i} className={s.gutterLine}>{i + 1}</div>
                ))}
              </div>
              <textarea
                ref={taRef}
                className={s.textarea}
                value={source}
                onChange={e => setSource(e.target.value)}
                onKeyDown={handleKey}
                spellCheck={false}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
              />
            </div>

            {/* Syntax reference */}
            <div className={s.cheatsheet}>
              <span className={s.cheatLabel}>SYNTAX:</span>
              <div className={s.cheatItems}>
                <code className={s.cheatCode}><span className={s.kw}>rakho / let</span> x = 10;</code>
                <code className={s.cheatCode}><span className={s.kw}>jabtak / while</span> (cond) &#123; &#125;</code>
                <code className={s.cheatCode}><span className={s.kw}>agar / if</span> (x &gt; 5 aur y &lt; 10) &#123; &#125;</code>
                <code className={s.cheatCode}><span className={s.kw}>dikhao / print</span> x % 2;</code>
              </div>
            </div>

            {/* Run Button */}
            <button
              className={`${s.runBtn} ${loading ? s.runBtnLoading : ''}`}
              onClick={compile}
              disabled={loading}
            >
              {loading ? (
                <span className={s.spinnerWrap}>
                  <span className={s.spinner} />
                  COMPILING, OPTIMIZING & RUNNING...
                </span>
              ) : (
                <>
                  <svg className={s.runIcon} viewBox="0 0 16 16" fill="currentColor">
                    <path d="M3 2.5l10 5.5-10 5.5V2.5z"/>
                  </svg>
                  <span>EXECUTE COMPILER PIPELINE</span>
                  <span className={s.kbdHint}>[Ctrl+Enter]</span>
                </>
              )}
            </button>

            {/* Status bar */}
            {result && !loading && (
              <div className={`${s.statusBar} ${result.success ? s.statusOk : s.statusErr}`}>
                <div className={s.statusLeft}>
                  <span className={s.statusIcon}>{result.success ? '✓' : '✖'}</span>
                  <span>
                    {result.success
                      ? `Compiled Successfully · ${result.tokens?.length} tokens · ${result.optimized_tac?.length} TAC instrs · ${result.optimization_stats?.total_optimizations} optimizations`
                      : (phaseError ? `${phaseError.phase} error on line ${phaseError.line}: ${phaseError.message}` : `${result.semantic_errors?.length} semantic error(s)`)}
                  </span>
                </div>
                {execTime !== null && (
                  <span className={s.execTag}>{execTime}ms</span>
                )}
              </div>
            )}
            {connErr && (
              <div className={`${s.statusBar} ${s.statusErr}`}>
                <span className={s.statusIcon}>⚠</span> {connErr}
              </div>
            )}
          </div>

          {/* ─ Output column ─ */}
          <div className={s.outputCol}>
            {/* Phase Error Banner */}
            {phaseError && (
              <div className={s.errBanner}>
                <div className={s.errBannerHead}>
                  <span className={s.errPhase}>{phaseError.phase} Error</span>
                  <span className={s.errLoc}>Line {phaseError.line} · Col {phaseError.col}</span>
                </div>
                <p className={s.errMsg}>{phaseError.message}</p>
              </div>
            )}

            {/* Tab Navigation */}
            <div className={s.tabBar}>
              {TABS.map(t => (
                <button
                  key={t.id}
                  className={`${s.tabBtn} ${tab === t.id ? s.tabActive : ''} ${t.id === 'output' ? s.tabOutput : ''}`}
                  onClick={() => setTab(t.id)}
                >
                  <span className={s.tabPhase}>{t.phase}</span>
                  <span className={s.tabIcon}>{t.icon}</span>
                  <span className={s.tabLabel}>{t.label}</span>
                  {(counts[t.id] || counts[t.id] === '✓') && counts[t.id] !== 0 && counts[t.id] !== '—' && (
                    <span className={`${s.tabBadge} ${t.id === 'output' ? s.tabBadgeOutput : ''}`}>
                      {counts[t.id]}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab Content Display */}
            <div className={s.tabContent} key={tab + (result ? '1' : '0')}>
              {!result ? (
                <div className={s.emptyState}>
                  <div className={s.emptyIcon}>⬡</div>
                  <p className={s.emptyTitle}>Syntax Compiler Ready</p>
                  <p className={s.emptySub}>
                    Select a showcase preset above, or use the quick insert snippets and press{' '}
                    <kbd className={s.kbd}>Ctrl+Enter</kbd> to compile.
                  </p>
                </div>
              ) : (
                <>
                  {tab === 'tokens'    && <TokensPanel tokens={result.tokens} />}
                  {tab === 'ast'       && <ASTPanel    ast={result.ast} />}
                  {tab === 'symbols'   && <SymbolTable symbols={result.symbol_table} errors={result.semantic_errors} />}
                  {tab === 'tac'       && <TACPanel    tac={result.optimized_tac || result.tac} />}
                  {tab === 'optimizer' && <OptimizerPanel stats={result.optimization_stats} rawTac={result.tac} optimizedTac={result.optimized_tac} />}
                  {tab === 'output'    && <OutputPanel output={result.output} />}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
