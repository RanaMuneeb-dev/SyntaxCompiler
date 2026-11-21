import { useState, useEffect } from 'react'
import s from './ASTPanel.module.css'

const NODE_COLORS = {
  Program:     '#6b7394',
  Declaration: '#a855f7',
  Assignment:  '#00f5ff',
  Print:       '#00ff9d',
  If:          '#ff7733',
  While:       '#38bdf8',
  Compare:     '#ff4466',
  LogicalOp:   '#e879f9',
  UnaryOp:     '#f97316',
  BinaryOp:    '#ffb800',
  Identifier:  '#00f5ff',
  Number:      '#00ff9d',
  String:      '#f472b6',
}

const NODE_ICONS = {
  Program:     '⬡',
  Declaration: '◈',
  Assignment:  '←',
  Print:       '▶',
  If:          '⋈',
  While:       '⟳',
  Compare:     '≟',
  LogicalOp:   '⋏',
  UnaryOp:     '¬',
  BinaryOp:    '⊕',
  Identifier:  '◎',
  Number:      '#',
  String:      '"',
}

function countNodes(node) {
  if (!node) return 0
  let count = 1
  const children = [
    ...(node.statements || []),
    ...(node.args       || []),
    ...(node.body       || []),
    ...(node.then_body  || []),
    ...(node.else_body  || []),
    ...(node.expr  ? [node.expr]  : []),
    ...(node.left  ? [node.left]  : []),
    ...(node.right ? [node.right] : []),
    ...(node.condition ? [node.condition] : []),
  ].filter(Boolean)
  for (const child of children) {
    count += countNodes(child)
  }
  return count
}

function ASTNodeItem({ node, depth = 0, forceOpen }) {
  const [open, setOpen] = useState(true)

  useEffect(() => {
    if (forceOpen !== null) {
      setOpen(forceOpen)
    }
  }, [forceOpen])

  if (!node) return null

  const color = NODE_COLORS[node.type] || '#e2e6f0'
  const icon  = NODE_ICONS[node.type]  || '·'

  let children = []
  if (node.type === 'If') {
    children = [
      node.condition,
      ...(node.then_body || []),
      ...(node.else_body || []),
    ].filter(Boolean)
  } else if (node.type === 'While') {
    children = [
      node.condition,
      ...(node.body || []),
    ].filter(Boolean)
  } else {
    children = [
      ...(node.statements || []),
      ...(node.args       || []),
      ...(node.body       || []),
      ...(node.then_body  || []),
      ...(node.else_body  || []),
      ...(node.expr  ? [node.expr]  : []),
      ...(node.left  ? [node.left]  : []),
      ...(node.right ? [node.right] : []),
      ...(node.condition ? [node.condition] : []),
    ].filter(Boolean)
  }

  const hasChildren = children.length > 0

  const detail =
    node.name  != null ? node.name  :
    node.value != null ? (node.type === 'String' ? `"${node.value}"` : node.value) :
    node.op    != null ? node.op    : ''

  return (
    <div className={s.node} style={{ '--depth': depth }}>
      <div
        className={s.label}
        style={{ '--c': color }}
        onClick={() => hasChildren && setOpen(o => !o)}
      >
        <span className={s.icon} aria-hidden="true">{icon}</span>

        {hasChildren && (
          <span className={s.toggle}>{open ? '▾' : '▸'}</span>
        )}

        <span className={s.type}>{node.type}</span>

        {detail && (
          <span className={s.detail}>
            {(node.op || node.type === 'Compare' || node.type === 'LogicalOp') ? <span className={s.op}>{detail}</span> : detail}
          </span>
        )}

        {node.line != null && (
          <span className={s.line}>:{node.line}</span>
        )}
      </div>

      {open && hasChildren && (
        <div className={s.children}>
          {children.map((child, i) => (
            <ASTNodeItem key={i} node={child} depth={depth + 1} forceOpen={forceOpen} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function ASTPanel({ ast }) {
  const [forceOpen, setForceOpen] = useState(null)

  if (!ast)
    return <p className={s.empty}>No AST yet. Run the compiler.</p>

  const totalNodes = countNodes(ast)

  return (
    <div className={s.wrap}>
      {/* Header Toolbar */}
      <div className={s.toolbar}>
        <div className={s.stats}>
          <span>AST Generated · <strong>{totalNodes}</strong> nodes</span>
        </div>
        <div className={s.actions}>
          <button className={s.toolBtn} onClick={() => setForceOpen(true)}>
            Expand All
          </button>
          <button className={s.toolBtn} onClick={() => setForceOpen(false)}>
            Collapse All
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className={s.legend}>
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <span key={type} className={s.chip} style={{ '--c': color }}>
            {NODE_ICONS[type]} {type}
          </span>
        ))}
      </div>

      {/* Tree view */}
      <div className={s.treeBox}>
        <ASTNodeItem node={ast} forceOpen={forceOpen} />
      </div>
    </div>
  )
}
