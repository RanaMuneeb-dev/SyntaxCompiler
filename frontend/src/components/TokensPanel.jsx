import { useState, useMemo } from 'react'
import s from './TokensPanel.module.css'

const TYPE_META = {
  KEYWORD:   { color: '#a855f7', label: 'KEYWORD'   },
  IDENT:     { color: '#00f5ff', label: 'IDENT'     },
  NUMBER:    { color: '#00ff9d', label: 'NUMBER'    },
  STRING:    { color: '#f472b6', label: 'STRING'    },
  OP:        { color: '#ffb800', label: 'OP'        },
  COMPARE:   { color: '#ff4466', label: 'COMPARE'   },
  LOGIC_AND: { color: '#e879f9', label: 'AND'       },
  LOGIC_OR:  { color: '#c084fc', label: 'OR'        },
  LOGIC_NOT: { color: '#f43f5e', label: 'NOT'       },
  ASSIGN:    { color: '#ffb800', label: 'ASSIGN'    },
  SEMI:      { color: '#6b7394', label: 'SEMI'      },
  LPAREN:    { color: '#ff7733', label: 'LPAREN'    },
  RPAREN:    { color: '#ff7733', label: 'RPAREN'    },
  LBRACE:    { color: '#ff7733', label: 'LBRACE'    },
  RBRACE:    { color: '#ff7733', label: 'RBRACE'    },
  COMMA:     { color: '#6b7394', label: 'COMMA'     },
}

export default function TokensPanel({ tokens }) {
  const [filterType, setFilterType] = useState('ALL')
  const [search, setSearch] = useState('')

  const filteredTokens = useMemo(() => {
    if (!tokens) return []
    return tokens.filter(tok => {
      const matchType = filterType === 'ALL' || tok.type === filterType
      const matchSearch = !search ||
        tok.value.toLowerCase().includes(search.toLowerCase()) ||
        tok.type.toLowerCase().includes(search.toLowerCase())
      return matchType && matchSearch
    })
  }, [tokens, filterType, search])

  if (!tokens || tokens.length === 0)
    return <p className={s.empty}>No tokens yet. Run the compiler.</p>

  const typeCounts = tokens.reduce((acc, t) => {
    acc[t.type] = (acc[t.type] || 0) + 1
    return acc
  }, {})

  return (
    <div className={s.wrap}>
      {/* Search & Stats Bar */}
      <div className={s.toolbar}>
        <div className={s.searchWrap}>
          <span className={s.searchIcon}>🔍</span>
          <input
            type="text"
            className={s.searchInput}
            placeholder="Search tokens by value or type..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className={s.clearBtn} onClick={() => setSearch('')}>✕</button>
          )}
        </div>

        <div className={s.stats}>
          <span className={s.statItem}>
            Total: <strong>{tokens.length}</strong>
          </span>
          <span className={s.statItem}>
            Showing: <strong>{filteredTokens.length}</strong>
          </span>
        </div>
      </div>

      {/* Interactive Filter Chips */}
      <div className={s.legend}>
        <button
          className={`${s.chip} ${filterType === 'ALL' ? s.chipActive : ''}`}
          style={{ '--c': '#38bdf8' }}
          onClick={() => setFilterType('ALL')}
        >
          ALL ({tokens.length})
        </button>
        {Object.entries(TYPE_META).map(([type, { color }]) => {
          const count = typeCounts[type] || 0
          if (count === 0) return null
          return (
            <button
              key={type}
              className={`${s.chip} ${filterType === type ? s.chipActive : ''}`}
              style={{ '--c': color }}
              onClick={() => setFilterType(filterType === type ? 'ALL' : type)}
            >
              {type} ({count})
            </button>
          )
        })}
      </div>

      {/* Table */}
      <div className={s.grid}>
        <div className={s.header}>
          <span>#</span>
          <span>TYPE</span>
          <span>LEXEME / VALUE</span>
          <span style={{ textAlign: 'center' }}>LINE</span>
          <span style={{ textAlign: 'center' }}>COL</span>
        </div>
        {filteredTokens.map((tok, i) => {
          const color = TYPE_META[tok.type]?.color ?? '#6b7394'
          const displayVal = tok.type === 'STRING' ? `"${tok.value}"` : (tok.value || '—')
          return (
            <div key={i} className={s.row} style={{ animationDelay: `${Math.min(i * 12, 300)}ms` }}>
              <span className={s.idx}>{i + 1}</span>
              <span className={s.badge} style={{ '--c': color }}>{tok.type}</span>
              <code className={s.val}>{displayVal}</code>
              <span className={s.pos}>{tok.line}</span>
              <span className={s.pos}>{tok.col}</span>
            </div>
          )
        })}
        {filteredTokens.length === 0 && (
          <p className={s.noMatch}>No matching tokens found for "{search}"</p>
        )}
      </div>
    </div>
  )
}
