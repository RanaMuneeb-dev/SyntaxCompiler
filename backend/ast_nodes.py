"""
AST Node definitions for the Mini Compiler.
Supports: Declarations, Assignments, Print, If-Else, While Loops,
          Binary Ops, Logical Ops, Comparisons, and Unary Ops.
"""


class ASTNode:
    pass


class ProgramNode(ASTNode):
    def __init__(self):
        self.statements = []

    def to_dict(self):
        return {
            "type": "Program",
            "statements": [s.to_dict() for s in self.statements],
        }


class DeclNode(ASTNode):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line

    def to_dict(self):
        return {
            "type": "Declaration",
            "name": self.name,
            "expr": self.expr.to_dict(),
            "line": self.line,
        }


class AssignNode(ASTNode):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line

    def to_dict(self):
        return {
            "type": "Assignment",
            "name": self.name,
            "expr": self.expr.to_dict(),
            "line": self.line,
        }


class PrintNode(ASTNode):
    def __init__(self, args, line):
        self.args = args
        self.line = line

    @property
    def expr(self):
        return self.args[0] if self.args else None

    def to_dict(self):
        return {
            "type": "Print",
            "args": [a.to_dict() for a in self.args],
            "expr": self.args[0].to_dict() if self.args else None,
            "line": self.line,
        }


class IfNode(ASTNode):
    """
    if ( condition ) { then_body } else { else_body }
    else_body is [] when there is no else branch.
    """
    def __init__(self, condition, then_body, else_body, line):
        self.condition = condition    # ASTNode (CompareNode, LogicalOpNode, etc.)
        self.then_body = then_body    # list[ASTNode]
        self.else_body = else_body    # list[ASTNode]
        self.line      = line

    def to_dict(self):
        return {
            "type":      "If",
            "condition": self.condition.to_dict(),
            "then_body": [s.to_dict() for s in self.then_body],
            "else_body": [s.to_dict() for s in self.else_body],
            "line":      self.line,
        }


class WhileNode(ASTNode):
    """
    while ( condition ) { body }
    """
    def __init__(self, condition, body, line):
        self.condition = condition    # ASTNode
        self.body      = body         # list[ASTNode]
        self.line      = line

    def to_dict(self):
        return {
            "type":      "While",
            "condition": self.condition.to_dict(),
            "body":      [s.to_dict() for s in self.body],
            "line":      self.line,
        }


class CompareNode(ASTNode):
    """
    Comparison: left op right
    op in { '==', '!=', '<', '<=', '>', '>=' }
    """
    def __init__(self, op, left, right, line):
        self.op    = op
        self.left  = left
        self.right = right
        self.line  = line

    def to_dict(self):
        return {
            "type":  "Compare",
            "op":    self.op,
            "left":  self.left.to_dict(),
            "right": self.right.to_dict(),
            "line":  self.line,
        }


class LogicalOpNode(ASTNode):
    """
    Logical: left op right
    op in { '&&', '||' }
    """
    def __init__(self, op, left, right, line):
        self.op    = op
        self.left  = left
        self.right = right
        self.line  = line

    def to_dict(self):
        return {
            "type":  "LogicalOp",
            "op":    self.op,
            "left":  self.left.to_dict(),
            "right": self.right.to_dict(),
            "line":  self.line,
        }


class UnaryOpNode(ASTNode):
    """
    Unary: op expr
    op in { '-', '!' }
    """
    def __init__(self, op, expr, line):
        self.op   = op
        self.expr = expr
        self.line = line

    def to_dict(self):
        return {
            "type": "UnaryOp",
            "op":   self.op,
            "expr": self.expr.to_dict(),
            "line": self.line,
        }


class BinOpNode(ASTNode):
    def __init__(self, op, left, right, line):
        self.op    = op
        self.left  = left
        self.right = right
        self.line  = line

    def to_dict(self):
        return {
            "type":  "BinaryOp",
            "op":    self.op,
            "left":  self.left.to_dict(),
            "right": self.right.to_dict(),
            "line":  self.line,
        }


class NumberNode(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line  = line

    def to_dict(self):
        return {"type": "Number", "value": self.value, "line": self.line}


class StringNode(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line  = line

    def to_dict(self):
        return {"type": "String", "value": self.value, "line": self.line}


class IdentNode(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line

    def to_dict(self):
        return {"type": "Identifier", "name": self.name, "line": self.line}
