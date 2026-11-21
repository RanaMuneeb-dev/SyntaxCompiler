import { useState } from 'react'
import s from './SymbolTable.module.css'

const TYPE_STYLE = {
  number: { bg: 'rgba(0,255,157,0.12)',  color: '#00ff9d', border: 'rgba(0,255,157,0.3)' },
  int:    { bg: 'rgba(0,255,157,0.12)',  color: '#00ff9d', border: 'rgba(0,255,157,0.3)' },
  float:  { bg: 'rgba(255,184,0,0.12)',  color: '#ffb800', border: 'rgba(255,184,0,0.3)' },
  string: { bg: 'rgba(244,114,182,0.12)', color: '#f472b6', border: 'rgba(244,114,182,0.3)' },
  bool:   { bg: 'rgba(56,189,248,0.12)',  color: '#38bdf8', border: 'rgba(56,189,248,0.3)' },
}

export default function SymbolTable({ symbols, errors }) {
  const [search, setSearch] = useState('')
  const hasErrors  = errors  && errors.length  > 0
  const hasSymbols = symbols && symbols.length > 0

  const filteredSymbols = (symbols || []).filter(sym =>
    sym.name.toLowerCase().includes(search.toLowerCase()) ||
    sym.type.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className={s.wrap}>
      {/* Semantic Errors Section */}
      {hasErrors && (
        <div className={s.errors}>
          <div className={s.errHead}>
            <span className={s.errIcon}>⚠️</span>
            <span className={s.errTitle}>Semantic Type & Scope Errors ({errors.length})</span>
          </div>
          <div className={s.errList}>
            {errors.map((e, i) => (
              <div key={i} className={s.errRow}>
                <span className={s.errBadge}>Line {e.line}</span>
                <span className={s.errMsg}>{e.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Toolbar */}
      {hasSymbols && (
        <div className={s.toolbar}>
          <div className={s.searchWrap}>
            <span className={s.searchIcon}>🔍</span>
            <input
              type="text"
              className={s.searchInput}
              placeholder="Search variables..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <span className={s.statText}>
            Variables Declared: <strong>{symbols.length}</strong>
          </span>
        </div>
      )}

      {!hasSymbols ? (
        <div className={s.emptyBox}>
          <span className={s.emptyIcon}>◎</span>
          <p className={s.empty}>No symbols declared yet in symbol table.</p>
        </div>
      ) : (
        <div className={s.table}>
          <div className={s.header}>
            <span>#</span>
            <span>IDENTIFIER</span>
            <span>INFERRED TYPE</span>
            <span>SCOPE</span>
            <span style={{ textAlign: 'right' }}>DECLARATION</span>
          </div>
          {filteredSymbols.map((sym, i) => {
            const ts = TYPE_STYLE[sym.type] || {
              bg: 'rgba(107,115,148,0.15)',
              color: '#6b7394',
              border: 'rgba(107,115,148,0.3)',
            }
            return (
              <div key={i} className={s.row} style={{ animationDelay: `${i * 35}ms` }}>
                <span className={s.idx}>{i + 1}</span>
                <span className={s.name}>
                  <code>{sym.name}</code>
                </span>
                <span>
                  <span
                    className={s.type}
                    style={{ background: ts.bg, color: ts.color, borderColor: ts.border }}
                  >
                    {sym.type}
                  </span>
                </span>
                <span className={s.scope}>Global</span>
                <span className={s.lineNum}>Line {sym.declared_at}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
