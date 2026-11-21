"""
Compiler Optimization Pass (Phase 04.5)
Performs:
  1. Constant Folding: Pre-calculates static arithmetic, comparisons, and logic at compile-time.
  2. Algebraic Simplification: Simplifies identities like x + 0, x * 1, x * 0.
  3. Dead Code Elimination: Prunes impossible branches in if/else statements and while loops.
"""

from ast_nodes import (
    ProgramNode, DeclNode, AssignNode, PrintNode, IfNode, WhileNode,
    CompareNode, LogicalOpNode, UnaryOpNode, BinOpNode,
    NumberNode, StringNode, IdentNode, ASTNode,
)


def _to_num(val):
    try:
        f = float(val)
        return int(f) if f.is_integer() else f
    except (ValueError, TypeError):
        return None


class Optimizer:
    def __init__(self):
        self.optimizations = []
        self.constants_folded = 0
        self.dead_branches_pruned = 0

    def optimize(self, program: ProgramNode):
        new_stmts = []
        for stmt in program.statements:
            opt_stmt = self._fold_stmt(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    new_stmts.extend(opt_stmt)
                else:
                    new_stmts.append(opt_stmt)

        opt_program = ProgramNode()
        opt_program.statements = new_stmts
        return opt_program, {
            "constants_folded": self.constants_folded,
            "dead_branches_pruned": self.dead_branches_pruned,
            "total_optimizations": len(self.optimizations),
            "log": self.optimizations,
        }

    def _fold_stmt(self, node: ASTNode):
        if isinstance(node, DeclNode):
            opt_expr = self._fold_expr(node.expr)
            return DeclNode(name=node.name, expr=opt_expr, line=node.line)

        if isinstance(node, AssignNode):
            opt_expr = self._fold_expr(node.expr)
            return AssignNode(name=node.name, expr=opt_expr, line=node.line)

        if isinstance(node, PrintNode):
            opt_args = [self._fold_expr(arg) for arg in node.args]
            return PrintNode(args=opt_args, line=node.line)

        if isinstance(node, IfNode):
            opt_cond = self._fold_expr(node.condition)

            # Check if condition is a statically known constant number
            if isinstance(opt_cond, NumberNode):
                cond_val = _to_num(opt_cond.value)
                if cond_val:  # Truthy: Always executes then_body
                    self.dead_branches_pruned += 1
                    self.optimizations.append(
                        f"Line {node.line}: Condition is always true ({cond_val}). Pruned else branch."
                    )
                    folded_then = []
                    for s in node.then_body:
                        res = self._fold_stmt(s)
                        if res: folded_then.extend(res if isinstance(res, list) else [res])
                    return folded_then
                else:         # Falsy: Always executes else_body
                    self.dead_branches_pruned += 1
                    self.optimizations.append(
                        f"Line {node.line}: Condition is always false (0). Pruned then branch."
                    )
                    folded_else = []
                    for s in node.else_body:
                        res = self._fold_stmt(s)
                        if res: folded_else.extend(res if isinstance(res, list) else [res])
                    return folded_else

            # Both branches optimized
            opt_then = [self._fold_stmt(s) for s in node.then_body]
            opt_else = [self._fold_stmt(s) for s in node.else_body]
            return IfNode(
                condition=opt_cond,
                then_body=[s for s in opt_then if s],
                else_body=[s for s in opt_else if s],
                line=node.line,
            )

        if isinstance(node, WhileNode):
            opt_cond = self._fold_expr(node.condition)
            if isinstance(opt_cond, NumberNode) and _to_num(opt_cond.value) == 0:
                self.dead_branches_pruned += 1
                self.optimizations.append(
                    f"Line {node.line}: While loop condition is false (0). Eliminated loop completely."
                )
                return None

            opt_body = [self._fold_stmt(s) for s in node.body]
            return WhileNode(
                condition=opt_cond,
                body=[s for s in opt_body if s],
                line=node.line,
            )

        return node

    def _fold_expr(self, node: ASTNode):
        if isinstance(node, BinOpNode):
            left = self._fold_expr(node.left)
            right = self._fold_expr(node.right)

            # 1. Constant folding of two numbers
            if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                l_val = _to_num(left.value)
                r_val = _to_num(right.value)
                if l_val is not None and r_val is not None:
                    res = None
                    if node.op == "+":
                        res = l_val + r_val
                    elif node.op == "-":
                        res = l_val - r_val
                    elif node.op == "*":
                        res = l_val * r_val
                    elif node.op == "/" and r_val != 0:
                        res = l_val / r_val
                    elif node.op == "%" and r_val != 0:
                        res = l_val % r_val

                    if res is not None:
                        # Clean int formatting
                        if isinstance(res, float) and res.is_integer():
                            res = int(res)
                        self.constants_folded += 1
                        self.optimizations.append(
                            f"Line {node.line}: Constant folded {l_val} {node.op} {r_val} → {res}"
                        )
                        return NumberNode(value=str(res), line=node.line)

            # 2. String concatenation folding
            if node.op == "+" and isinstance(left, StringNode) and isinstance(right, StringNode):
                folded_str = left.value + right.value
                self.constants_folded += 1
                self.optimizations.append(
                    f'Line {node.line}: Constant folded string concatenation → "{folded_str}"'
                )
                return StringNode(value=folded_str, line=node.line)

            # 3. Algebraic identities
            if isinstance(right, NumberNode):
                r_val = _to_num(right.value)
                if node.op == "+" and r_val == 0:
                    return left
                if node.op == "-" and r_val == 0:
                    return left
                if node.op == "*" and r_val == 1:
                    return left
                if node.op == "*" and r_val == 0:
                    return NumberNode(value="0", line=node.line)

            return BinOpNode(op=node.op, left=left, right=right, line=node.line)

        if isinstance(node, CompareNode):
            left = self._fold_expr(node.left)
            right = self._fold_expr(node.right)
            if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                l_val = _to_num(left.value)
                r_val = _to_num(right.value)
                if l_val is not None and r_val is not None:
                    res = False
                    if node.op == "==": res = (l_val == r_val)
                    elif node.op == "!=": res = (l_val != r_val)
                    elif node.op == "<":  res = (l_val < r_val)
                    elif node.op == "<=": res = (l_val <= r_val)
                    elif node.op == ">":  res = (l_val > r_val)
                    elif node.op == ">=": res = (l_val >= r_val)
                    int_res = 1 if res else 0
                    self.constants_folded += 1
                    self.optimizations.append(
                        f"Line {node.line}: Folded comparison {l_val} {node.op} {r_val} → {int_res}"
                    )
                    return NumberNode(value=str(int_res), line=node.line)
            return CompareNode(op=node.op, left=left, right=right, line=node.line)

        if isinstance(node, LogicalOpNode):
            left = self._fold_expr(node.left)
            right = self._fold_expr(node.right)
            if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                l_val = 1 if _to_num(left.value) else 0
                r_val = 1 if _to_num(right.value) else 0
                if node.op == "&&":
                    res = 1 if (l_val and r_val) else 0
                elif node.op == "||":
                    res = 1 if (l_val or r_val) else 0
                else:
                    res = 0
                self.constants_folded += 1
                self.optimizations.append(
                    f"Line {node.line}: Folded logical {l_val} {node.op} {r_val} → {res}"
                )
                return NumberNode(value=str(res), line=node.line)
            return LogicalOpNode(op=node.op, left=left, right=right, line=node.line)

        if isinstance(node, UnaryOpNode):
            expr = self._fold_expr(node.expr)
            if isinstance(expr, NumberNode):
                val = _to_num(expr.value)
                if val is not None:
                    if node.op == "-":
                        res = -val
                        return NumberNode(value=str(res), line=node.line)
                    if node.op == "!":
                        res = 0 if val else 1
                        return NumberNode(value=str(res), line=node.line)
            return UnaryOpNode(op=node.op, expr=expr, line=node.line)

        return node
